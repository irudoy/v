import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from kb import project
from tools.kb.tests.test_guard import make_repo


SESSION = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"


class SessionLauncherTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.base = Path(self.scratch.name).resolve()
        self.home = self.base / "home"
        self.home.mkdir()
        self.root = make_repo(self.base / "project with spaces")
        self.launcher = self.root / "tools/kb/codex-launcher.py"
        shutil.copyfile(Path(project.hook.__file__).with_name("codex-launcher.py"), self.launcher)
        self.launcher.chmod(0o755)
        self.binary = self.base / "native"
        self.binary.write_text(f"#!{sys.executable}\nimport json, os, sys\n"
                               "print(json.dumps({'args': sys.argv[1:], 'guard': os.environ.get('KB_GUARD')}))\n"
                               "sys.exit(17)\n")
        self.binary.chmod(0o755)
        self.codex = self.home / ".local/bin/codex"
        self.codex.parent.mkdir(parents=True)
        self.codex.symlink_to(self.binary)
        self.environment = {**os.environ, "HOME": str(self.home), "KB_GUARD": ""}
        result = subprocess.run([sys.executable, str(self.launcher), "--install"],
                                env=self.environment, capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr), (0, ""))

    def tearDown(self):
        self.scratch.cleanup()

    def launch(self, arguments, mode="", cwd=None):
        return subprocess.run([str(self.codex), *arguments], cwd=cwd or self.root,
                              env={**self.environment, "KB_GUARD": mode},
                              capture_output=True, text=True)

    def guarded(self, session=SESSION, root=None, mode=""):
        root = root or self.root
        result = subprocess.run([sys.executable, str(root / "tools/kb/hook.py")],
            input=json.dumps({"session_id": session, "cwd": str(root), "tool_name": "Read",
                              "tool_input": {"file_path": str(root / "kb/names.csv")}}),
            env={**self.environment, "KB_GUARD": mode}, capture_output=True, text=True)
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        return bool(result.stdout)

    def state_files(self):
        return sorted(self.home.glob(".local/state/vq-kb-guard/*/*.json"))

    def test_off_survives_remote_environment_without_affecting_other_sessions_or_projects(self):
        arguments = ["--remote", "unix://", "resume", SESSION, "a prompt with spaces"]
        result = self.launch(arguments, "off")
        self.assertEqual(result.returncode, 17)
        self.assertEqual(json.loads(result.stdout), {"args": arguments, "guard": None})
        self.assertFalse(self.guarded())
        self.assertTrue(self.guarded(OTHER))
        self.assertTrue(self.guarded(session="fixture"))
        self.assertTrue(self.guarded(root=make_repo(self.base / "other project")))
        state, = self.state_files()
        self.assertEqual(stat.S_IMODE(state.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(state.parent.stat().st_mode), 0o700)

    def test_on_overrides_off_in_both_persistent_state_and_hook_environment(self):
        self.launch(["resume", SESSION], "off")
        result = self.launch(["resume", SESSION], "on")
        self.assertEqual(result.returncode, 17)
        self.assertTrue(self.guarded(mode="off"))
        self.assertFalse(self.guarded(OTHER, mode="off"))  # Legacy environment fallback.
        self.assertEqual(len(self.state_files()), 1)

    def test_unset_mode_passes_every_argument_through_without_creating_state(self):
        arguments = ["exec", "resume is a word in this prompt", "--config", "anything=1"]
        result = self.launch(arguments)
        self.assertEqual(result.returncode, 17)
        self.assertEqual(json.loads(result.stdout)["args"], arguments)
        self.assertEqual(self.state_files(), [])

    def test_options_do_not_confuse_values_with_commands_and_cd_resolves_the_project(self):
        arguments = ["-c", 'name="resume"', "--remote=unix://", "resume", SESSION,
                     "--cd", str(self.root / "tools/kb"), "resume --last"]
        result = self.launch(arguments, "off", cwd=self.base)
        self.assertEqual(result.returncode, 17, result.stderr)
        self.assertEqual(json.loads(result.stdout)["args"], arguments)
        self.assertFalse(self.guarded())
        result = self.launch([f"-C{self.root}", "resume", OTHER], "off", cwd=self.base)
        self.assertEqual(result.returncode, 17, result.stderr)
        self.assertFalse(self.guarded(OTHER))

    def test_ambiguous_selection_wrong_project_and_invalid_modes_do_not_launch(self):
        for arguments, mode, directory in (
                (["resume", "--last"], "off", self.root),
                (["resume", "my-session"], "off", self.root),
                (["resume"], "on", self.root),
                (["exec", SESSION], "off", self.root),
                (["resume", SESSION], "false", self.root),
                (["resume", SESSION], "off", make_repo(self.base / "unrelated"))):
            with self.subTest(arguments=arguments, mode=mode):
                result = self.launch(arguments, mode, directory)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertEqual(self.state_files(), [])

    def test_malformed_state_never_grants_an_exception(self):
        self.launch(["resume", SESSION], "off")
        state, = self.state_files()
        valid = json.loads(state.read_text())
        for value in ("{", "[]", "null", json.dumps({**valid, "project": "/wrong"}),
                      json.dumps({**valid, "session_id": OTHER}),
                      json.dumps({**valid, "mode": "invalid"}),
                      json.dumps({**valid, "version": True}),
                      json.dumps({**valid, "version": 2})):
            with self.subTest(value=value):
                state.write_text(value)
                self.assertTrue(self.guarded())
        with patch.object(Path, "home", return_value=self.home):
            with self.assertRaises(ValueError):
                project.hook.set_session_mode(self.root, "../../outside", "off")

    def test_install_is_repeatable_and_preserves_the_native_executable(self):
        native = self.codex.with_name("codex-native")
        self.assertEqual(native.resolve(), self.binary)
        result = subprocess.run([sys.executable, str(self.launcher), "--install"],
                                env=self.environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(self.codex.resolve(), self.launcher)
        self.assertEqual(native.resolve(), self.binary)
        native.unlink()
        native.write_text("occupied")
        result = subprocess.run([sys.executable, str(self.launcher), "--install"],
                                env=self.environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(native.read_text(), "occupied")
