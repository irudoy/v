"""Session overrides through the public CLI and the ordinary hook entry point."""

import contextlib
import io
import json
import os
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

from kb import cli, project, repo
from tools.kb.tests.test_guard import make_repo


SESSION = "11111111-1111-4111-8111-111111111111"
OTHER = "22222222-2222-4222-8222-222222222222"


class SessionGuardTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.base = Path(self.scratch.name).resolve()
        self.home = self.base / "home"
        self.home.mkdir()
        self.root = make_repo(self.base / "project with spaces")
        self.addCleanup(self.scratch.cleanup)
        self.addCleanup(patch.stopall)
        patch.object(Path, "home", return_value=self.home).start()
        patch.object(repo, "ROOT", self.root).start()

    def command(self, action, session=SESSION, structured=True):
        arguments = ["guard", action, "--session", session]
        if structured:
            arguments.append("--json")
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = cli.main(arguments)
        return code, out.getvalue(), err.getvalue()

    def guarded(self, session=SESSION, root=None, environment="", antigravity=False):
        root = root or self.root
        if antigravity:
            call = {
                "hookEventName": "PreToolUse",
                "conversationId": session,
                "cwd": str(root),
                "toolCall": {"id": "call_1", "name": "read_file",
                             "args": {"Path": str(root / "kb/names.csv")}},
            }
        else:
            call = {"session_id": session, "cwd": str(root), "tool_name": "Read",
                    "tool_input": {"file_path": str(root / "kb/names.csv")}}
        out = io.StringIO()
        with patch.object(project.hook, "ROOT", root), \
                patch.object(project.hook.sys, "stdin", io.StringIO(json.dumps(call))), \
                patch.dict(os.environ, {"KB_GUARD": environment}), \
                contextlib.redirect_stdout(out):
            code = project.hook.main()
        self.assertEqual(code, 0)
        return json.loads(out.getvalue()) if out.getvalue() else None

    def files(self):
        return sorted(self.home.glob(".local/state/vq-kb-guard/*/*.json"))

    def test_off_persists_for_the_active_session_and_preserves_other_sessions_and_projects(self):
        definitions = {name: (self.root / name).read_bytes()
                       for name in (".codex/hooks.json", ".claude/settings.json",
                                    ".agents/hooks.json")}
        code, out, err = self.command("off")
        self.assertEqual((code, err), (0, ""))
        state = json.loads(out)
        self.assertEqual((state["mode"], state["session_id"], state["project"]),
                         ("off", SESSION, str(self.root)))
        self.assertIsNone(self.guarded())
        self.assertIsNotNone(self.guarded(OTHER))
        self.assertIsNotNone(self.guarded("fixture"))
        self.assertIsNotNone(self.guarded(root=make_repo(self.base / "other project")))
        self.assertEqual(definitions, {name: (self.root / name).read_bytes()
                                      for name in definitions})
        [saved] = self.files()
        self.assertEqual(stat.S_IMODE(saved.stat().st_mode), 0o600)
        self.assertEqual(stat.S_IMODE(saved.parent.stat().st_mode), 0o700)

    def test_on_overrides_off_and_the_hook_environment_for_only_the_selected_session(self):
        self.assertEqual(self.command("off")[0], 0)
        self.assertEqual(self.command("on")[0], 0)
        self.assertIsNotNone(self.guarded(environment="off"))
        self.assertIsNone(self.guarded(OTHER, environment="off"))
        self.assertEqual(len(self.files()), 1)
        self.assertEqual(json.loads(self.command("status")[1])["mode"], "on")

    def test_status_reads_the_saved_override_without_creating_or_rewriting_state(self):
        self.assertIsNone(json.loads(self.command("status")[1])["mode"])
        self.assertEqual(list(self.home.iterdir()), [])
        self.command("off")
        [saved] = self.files()
        before = saved.read_bytes(), saved.stat().st_mtime_ns
        self.assertEqual(json.loads(self.command("status")[1])["mode"], "off")
        self.assertEqual((saved.read_bytes(), saved.stat().st_mtime_ns), before)

    def test_status_does_not_claim_a_remote_hooks_environment(self):
        with patch.dict(os.environ, {"KB_GUARD": "off"}):
            code, out, err = self.command("status")
        self.assertEqual((code, err), (0, ""))
        self.assertIsNone(json.loads(out)["mode"])
        self.assertIn("unset (hook environment fallback)",
                      self.command("status", structured=False)[1])

    def test_commands_do_not_access_the_graph_or_compile_the_knowledge_model(self):
        with patch.object(cli.graph, "fresh", side_effect=AssertionError("graph access")), \
                patch.object(cli.compile, "cached", side_effect=AssertionError("model access")):
            for action in ("status", "off", "status", "on"):
                with self.subTest(action=action):
                    self.assertEqual(self.command(action)[0], 0)

    def test_guard_commands_are_available_while_the_guard_is_enabled(self):
        self.command("on")
        guard = project.hook.Guard(self.root, self.root)
        for action in ("off", "on", "status"):
            with self.subTest(action=action):
                self.assertIsNone(guard.decide("Bash", {
                    "command": f"uv run kb guard {action} --session {SESSION}"}))

    def test_an_explicit_uuid_is_required_and_invalid_selection_creates_no_state(self):
        for session in ("my-session", "../../outside", "", "fixture"):
            for action in ("status", "off", "on"):
                with self.subTest(session=session, action=action):
                    code, out, err = self.command(action, session)
                    self.assertEqual((code, out), (2, ""))
                    self.assertIn("explicit session UUID", err)
                    self.assertEqual(self.files(), [])
        for arguments in (["guard", "off"], ["guard", "invalid", "--session", SESSION]):
            with self.subTest(arguments=arguments), contextlib.redirect_stderr(io.StringIO()), \
                    self.assertRaises(SystemExit) as error:
                cli.main(arguments)
            self.assertEqual(error.exception.code, 2)
            self.assertEqual(self.files(), [])

    def test_equivalent_uuid_and_project_paths_share_one_record(self):
        session = "abcdef01-2345-4678-9abc-def012345678"
        self.command("off", session.upper())
        self.assertEqual(json.loads(self.command("status", session)[1])["session_id"], session)
        alias = self.base / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with patch.object(repo, "ROOT", alias):
            self.command("on", session)
        self.assertEqual(len(self.files()), 1)
        self.assertEqual(json.loads(self.command("status", session)[1])["mode"], "on")

    def test_malformed_state_grants_no_exception_and_status_does_not_repair_it(self):
        self.command("off")
        [saved] = self.files()
        valid = json.loads(saved.read_text())
        for value in ("{", "[]", "null", json.dumps({**valid, "project": "/wrong"}),
                      json.dumps({**valid, "session_id": OTHER}),
                      json.dumps({**valid, "mode": "invalid"}),
                      json.dumps({**valid, "version": True}),
                      json.dumps({**valid, "version": 2})):
            with self.subTest(value=value):
                saved.write_text(value)
                self.assertIsNotNone(self.guarded())
                self.assertIsNone(json.loads(self.command("status")[1])["mode"])
                self.assertEqual(saved.read_text(), value)
        self.command("on")
        self.assertEqual(json.loads(self.command("status")[1])["mode"], "on")

    def test_failed_atomic_replace_retains_the_previous_override_and_cleans_the_temporary_file(self):
        self.command("off")
        [saved] = self.files()
        before = saved.read_bytes()
        with patch.object(project.hook.os, "replace", side_effect=PermissionError("refused")):
            code, out, err = self.command("on")
        self.assertEqual((code, out), (6, ""))
        self.assertIn("cannot update KB guard session state", err)
        self.assertEqual(saved.read_bytes(), before)
        self.assertEqual(list(saved.parent.iterdir()), [saved])

    def test_a_codex_denial_names_the_session_command_without_changing_the_record(self):
        decision = self.guarded()["hookSpecificOutput"]
        self.assertIn(f"uv run kb guard off --session {SESSION}",
                      decision["permissionDecisionReason"])
        self.assertEqual(self.files(), [])

    def test_antigravity_conversation_id_uses_the_same_session_override(self):
        decision = self.guarded(antigravity=True)
        self.assertEqual(decision["decision"], "deny")
        self.assertIn(f"uv run kb guard off --session {SESSION}", decision["reason"])
        self.assertEqual(self.command("off")[0], 0)
        self.assertIsNone(self.guarded(antigravity=True))
        self.assertIsNotNone(self.guarded(OTHER, antigravity=True))
        self.assertEqual(self.command("on")[0], 0)
        self.assertIsNotNone(self.guarded(environment="off", antigravity=True))


if __name__ == "__main__":
    unittest.main()
