import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

from kb import guard, project, repo

CONFIG = """\
[guard]
trees = ["kb/", "l0/"]
git = ["add", "commit", "diff", "log", "show", "status"]
"""

PROJECTIONS = """\
[[projection]]
path = "defs/*.xml"
generator = "tools/defs/build.py"
inputs = ["defs/source.toml"]
consumers = []
read = "guarded"

[[projection]]
path = "GUIDE.md#kb"
generator = "tools/guide.py"
inputs = ["tools/guide.py"]
consumers = []
read = "open"
"""

GUIDE = """\
# Guide

Hand-written text.

<!-- kb:begin -->
Generated text.
<!-- kb:end -->

More hand-written text.
"""

SETTINGS = {"hooks": {"PreToolUse": [{
    "matcher": "|".join(guard.TOOLS),
    "hooks": [{"type": "command", "command": "python3 tools/kb/hook.py"}]}]}}
CODEX_SETTINGS = {"hooks": {"PreToolUse": [{
    "matcher": "|".join(guard.CODEX_TOOLS),
    "hooks": [{"type": "command", "command": "python3 tools/kb/hook.py"}]}]}}


def make_repo(root, files=None):
    """A git working tree with the guard inputs and `files`, all tracked."""
    defaults = {
        "tools/kb/config.toml": CONFIG,
        "tools/kb/projections.toml": PROJECTIONS,
        "tools/kb/hook.py": (project.hook.__file__,),
        "tools/defs/build.py": "",
        "tools/guide.py": "",
        "defs/source.toml": "",
        "defs/JK08A.xml": "<rom/>\n",
        "defs/open.csv": "a,b\n",
        "GUIDE.md": GUIDE,
        "kb/names.csv": "layout,kind,address,name,former\n",
        "kb/ram/normalized_bfs.toml": "",
        "l0/7mfk/funcs.csv": "entry\n",
        "open.txt": "open\n",
        ".ignore": "/kb/\n/l0/\n/defs/*.xml\n",
        ".claude/settings.json": json.dumps(SETTINGS),
        ".codex/hooks.json": json.dumps(CODEX_SETTINGS),
    }
    defaults.update(files or {})
    for name, text in defaults.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(text, tuple):
            shutil.copy(text[0], path)
        else:
            path.write_text(text, encoding="utf-8")
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    subprocess.run(["git", "add", "-A", "-f"], cwd=root, check=True)
    return root


class GuardCase(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.root = make_repo(Path(self.scratch.name).resolve())
        self.guard = project.hook.Guard(self.root)

    def tearDown(self):
        self.scratch.cleanup()

    def path(self, relative):
        return str(self.root / relative)

    def denied(self, tool, **arguments):
        return self.guard.decide(tool, arguments)


class ReadTest(GuardCase):
    def test_a_read_in_a_tree_names_the_command_of_its_path(self):
        self.assertIn("uv run kb show normalized_bfs/ram",
                      self.denied("Read", file_path=self.path("kb/ram/normalized_bfs.toml")))
        self.assertIn("uv run kb show <layout>:<address>",
                      self.denied("Read", file_path=self.path("kb/names.csv")))
        self.assertIn("uv run kb at 7mfk:<address>",
                      self.denied("Read", file_path=self.path("l0/7mfk/funcs.csv")))
        self.assertIsNone(self.denied("Read", file_path=self.path("open.txt")))
        self.assertIsNone(self.denied("Read", file_path="/etc/hosts"))

    def test_every_guarded_projection_is_read_through_kb(self):
        self.assertIn("kb where", self.denied("Read", file_path=self.path("defs/JK08A.xml")))
        self.assertIsNone(self.denied("Read", file_path=self.path("defs/open.csv")))
        self.assertIsNone(self.denied("Read", file_path=self.path("GUIDE.md")))

    def test_a_symbolic_link_counts_as_its_target(self):
        os.symlink("l0/7mfk/funcs.csv", self.root / "link.csv")
        self.assertIsNotNone(self.denied("Read", file_path=self.path("link.csv")))


class EditTest(GuardCase):
    def test_trees_and_projections_change_through_their_commands(self):
        self.assertIn("uv run kb sync", self.denied("Write", file_path=self.path("kb/x.toml"),
                                                    content=""))
        self.assertIn("export-l0.sh", self.denied("Edit", file_path=self.path("l0/7mfk/funcs.csv"),
                                                  old_string="entry", new_string="x"))
        reason = self.denied("Edit", file_path=self.path("defs/JK08A.xml"), old_string="rom",
                             new_string="x")
        self.assertIn("`tools/defs/build.py`", reason)
        self.assertIn("defs/source.toml", reason)
        self.assertIsNone(self.denied("Edit", file_path=self.path("defs/open.csv"),
                                      old_string="a", new_string="b"))
        self.assertIsNone(self.denied("NotebookEdit", notebook_path=self.path("open.ipynb")))

    def test_only_an_edit_of_the_marked_section_is_a_projection_edit(self):
        guide = self.path("GUIDE.md")
        self.assertIsNone(self.denied("Edit", file_path=guide, old_string="Hand-written text.",
                                      new_string="Other text."))
        self.assertIn("the kb section of GUIDE.md", self.denied(
            "Edit", file_path=guide, old_string="Generated text.", new_string="x"))
        self.assertIsNotNone(self.denied("Edit", file_path=guide, old_string="<!-- kb:end -->",
                                         new_string=""))
        self.assertIsNotNone(self.denied("MultiEdit", file_path=guide, edits=[
            {"old_string": "More", "new_string": "Less"},
            {"old_string": "text.\n<!-- kb:end", "new_string": "x"}]))
        self.assertIsNone(self.denied("Write", file_path=guide,
                                      content=GUIDE.replace("More", "Less")))
        self.assertIsNotNone(self.denied("Write", file_path=guide,
                                         content=GUIDE.replace("Generated", "Edited")))
        self.assertIsNotNone(self.denied("Write", file_path=guide, content="# Guide\n"))


class PatchTest(GuardCase):
    def patch(self, text):
        return self.denied("apply_patch", command="*** Begin Patch\n" + text +
                           "*** End Patch\n")

    def test_all_file_operations_inspect_every_protected_path(self):
        for path in ("kb/ram/x.toml", "l0/7mfk/funcs.csv", "defs/JK08A.xml"):
            for body in (f"*** Add File: {path}\n+x\n",
                         f"*** Update File: {path}\n@@\n-old\n+new\n",
                         f"*** Delete File: {path}\n",
                         f"*** Update File: open.txt\n*** Move to: {path}\n@@\n-open\n+x\n",
                         f"*** Update File: {path}\n*** Move to: open.txt\n@@\n-old\n+x\n"):
                with self.subTest(body=body):
                    self.assertIsNotNone(self.patch(body))
        self.assertIsNotNone(self.patch("*** Update File: open.txt\n@@\n-open\n+x\n"
                                      "*** Delete File: kb/names.csv\n"))

    def test_open_files_stay_open(self):
        for body in ("*** Add File: new.txt\n+new\n",
                     "*** Delete File: open.txt\n",
                     "*** Update File: open.txt\n*** Move to: moved.txt\n@@\n-open\n+new\n",
                     "*** Update File: defs/open.csv\n@@\n-a,b\n+c,d\n"):
            with self.subTest(body=body):
                self.assertIsNone(self.patch(body))

    def test_marked_sections_preserve_the_unmodified_context(self):
        self.assertIsNone(self.patch("*** Update File: GUIDE.md\n@@\n"
                                     "-Hand-written text.\n+Other text.\n\n"
                                     " <!-- kb:begin -->\n Generated text.\n"))
        self.assertIsNone(self.patch("*** Update File: GUIDE.md\n@@\n"
                                     " Generated text.\n <!-- kb:end -->\n\n"
                                     "-More hand-written text.\n+Other text.\n"
                                     "*** End of File\n"))
        for body in ("@@\n-Generated text.\n+Edited text.\n",
                     "@@\n-<!-- kb:end -->\n",
                     "@@\n <!-- kb:begin -->\n+Inserted text.\n Generated text.\n",
                     "@@ Generated text.\n+Inserted text.\n <!-- kb:end -->\n"):
            with self.subTest(body=body):
                self.assertIsNotNone(self.patch("*** Update File: GUIDE.md\n" + body))

    def test_whole_file_operations_cannot_remove_a_marked_projection(self):
        for body in ("*** Delete File: GUIDE.md\n",
                     "*** Add File: GUIDE.md\n+# Replaced\n",
                     "*** Update File: GUIDE.md\n*** Move to: moved.md\n@@\n"
                     "-Hand-written text.\n+Other text.\n"):
            with self.subTest(body=body):
                self.assertIsNotNone(self.patch(body))

    def test_absolute_and_symbolic_link_targets_keep_the_same_boundary(self):
        os.symlink("kb/names.csv", self.root / "link.csv")
        for path in (self.path("kb/names.csv"), "link.csv"):
            with self.subTest(path=path):
                self.assertIsNotNone(self.patch(f"*** Delete File: {path}\n"))

    def test_context_matching_and_multiple_hunks_preserve_the_section(self):
        self.assertIsNone(self.patch("*** Update File: GUIDE.md\n@@ # Guide\n\n"
                                     "- Hand-written text.  \n+Other text.\n"
                                     "@@ <!-- kb:end -->\n\n"
                                     "-More hand-written text.\n+Final text.\n"))
        self.assertIsNotNone(self.patch("*** Update File: GUIDE.md\n@@\n"
                                      "-Hand-written text.\n+Other text.\n@@\n"
                                      "-Generated text.\n+Edited text.\n"))
        self.assertEqual((self.root / "GUIDE.md").read_text(), GUIDE)

    def test_uninspectable_patches_are_denied(self):
        self.assertIn("cannot inspect apply_patch", self.denied("apply_patch", command=None))
        self.assertIn("cannot inspect apply_patch", self.denied(
            "apply_patch", command="*** Delete File: kb/names.csv\n"))
        self.assertIn("cannot inspect apply_patch", self.patch(
            "*** Update File: GUIDE.md\n@@\n-missing context\n+new\n"))


class SearchTest(GuardCase):
    def test_a_search_in_a_guarded_path_goes_to_kb_find(self):
        self.assertIn("kb find", self.denied("Grep", pattern="x", path=self.path("l0")))
        self.assertIsNotNone(self.denied("Grep", pattern="x", path=self.path("defs/JK08A.xml")))
        self.assertIsNotNone(self.denied("Glob", pattern="kb/**/*.toml"))
        self.assertIsNotNone(self.denied("Glob", pattern="*.csv", path=self.path("l0/7mfk")))
        self.assertIsNone(self.denied("Grep", pattern="x"))
        self.assertIsNone(self.denied("Grep", pattern="x", path=self.path("defs")))
        self.assertIsNone(self.denied("Glob", pattern="**/*.csv"))


class BashTest(GuardCase):
    DENIED = [
        "cat l0/7mfk/funcs.csv",
        "head -5 kb/names.csv | cut -d, -f1",
        "ls l0/",
        "cat defs/JK08A.xml",
        "git show HEAD:l0/7mfk/funcs.csv",
        "git grep entry -- l0/",
        "rg -n needle l0/",
        "grep -E 'a|b' l0/7mfk/funcs.csv",
        "rg -e needle -- l0/7mfk",
        "cd l0\ncat 7mfk/funcs.csv",
        "cd l0 && ls",
        "python3 - <<'EOF'\nprint(open('l0/7mfk/funcs.csv').read())\nEOF",
        "python3 -c \"print(open('l0/7mfk/funcs.csv').read())\"",
        "git commit -m \"x <<EOF\"\ncat l0/7mfk/funcs.csv",
        "echo ok; sed -n 1p kb/names.csv",
        "KB_GUARD=off cat kb/names.csv",
        "time cat kb/names.csv",
        "awk -F, '{print $1}' --file=l0/7mfk/prog.awk",
    ]
    PASSED = [
        "uv run kb at 7mfk:ffff1079",
        "uv run --directory tools/kb kb show kb/names.csv",
        "kb show l0/7mfk",
        "python3 -m kb raw kb/ram/x.toml",
        "git diff -- l0/ kb/names.csv",
        "git -C . log --oneline -- l0/",
        "git show --stat HEAD -- l0/",
        "git add kb/names.csv && git commit -m 'Draw kb/names.csv rows'",
        "git commit -F - <<'EOF'\nRead kb/names.csv (the names)\nEOF\ngit status",
        "make check",
        "uv run python tools/defs/build.py --out defs/JK08A.xml",
        "./tools/defs/build.py l0/7mfk/funcs.csv",
        "rg -n 'kb/names.csv' tools/",
        "rg -A 3 -e 'l0/7mfk' tools/",
        "grep -rn kb tools/ | head",
        "cd l0 && uv run kb at 7mfk:0",
        "cd l0\ncd ..\nls",
        "ls defs/",
        "cat GUIDE.md",
        "cat defs/open.csv",
        "echo ok > /dev/null; ls",
    ]

    def test_a_command_that_names_a_guarded_path_runs_kb_or_a_gate(self):
        for command in self.DENIED:
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        for command in self.PASSED:
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))

    def test_a_command_inside_a_tree_names_it(self):
        inside = project.hook.Guard(self.root, cwd=self.root / "l0" / "7mfk")
        self.assertIn("l0/7mfk/funcs.csv is L0", inside.decide("Bash", {"command": "cat funcs.csv"}))
        self.assertIsNone(inside.decide("Bash", {"command": f"cd {self.root} && ls"}))

    def test_codex_shell_uses_the_tool_working_directory(self):
        for directory in ("l0/7mfk", self.path("l0/7mfk")):
            with self.subTest(workdir=directory):
                self.assertIsNotNone(self.denied("Bash", command="cat funcs.csv",
                                                 workdir=directory))
                self.assertIsNone(self.denied("Bash", command="uv run kb code 7mfk:0",
                                              workdir=directory))
        self.assertIsNotNone(self.denied("Bash", command="cat ../../kb/names.csv",
                                         workdir="tools/kb"))
        self.assertIsNone(self.denied("Bash", command="python3 hook.py kb/names.csv",
                                      workdir="tools/kb"))

    def test_here_documents_join_the_command_that_reads_them(self):
        commands = project.hook.commands("git commit -F - <<'EOF'\nsee (kb/x)\nEOF\nls -la")
        self.assertEqual(commands, [(["git", "commit", "-F", "-", "<<", "EOF"], [("see (kb/x)", True)]),
                                    (["ls", "-la"], [])])


class HookProcessTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.root = make_repo(Path(self.scratch.name).resolve())

    def tearDown(self):
        self.scratch.cleanup()

    def run_hook(self, call, **environment):
        result = subprocess.run(
            [sys.executable, str(self.root / "tools/kb/hook.py")], input=json.dumps(call),
            capture_output=True, text=True, env={**os.environ, "KB_GUARD": "", **environment})
        return result.returncode, result.stdout, result.stderr

    def test_a_denial_is_a_permission_decision(self):
        code, out, _ = self.run_hook({"tool_name": "Read", "cwd": str(self.root),
                                      "tool_input": {"file_path": str(self.root / "kb/names.csv")}})
        self.assertEqual(code, 0)
        decision = json.loads(out)["hookSpecificOutput"]
        self.assertEqual((decision["hookEventName"], decision["permissionDecision"]),
                         ("PreToolUse", "deny"))
        self.assertTrue(decision["permissionDecisionReason"].startswith("kb guard: "))
        self.assertIn("KB_GUARD=off", decision["permissionDecisionReason"])

    def test_the_guard_passes_open_calls_and_yields_to_kb_guard_off(self):
        read = {"tool_name": "Read", "cwd": str(self.root),
                "tool_input": {"file_path": str(self.root / "kb/names.csv")}}
        self.assertEqual(self.run_hook(read, KB_GUARD="off"), (0, "", ""))
        self.assertEqual(self.run_hook({**read, "tool_input": {
            "file_path": str(self.root / "open.txt")}}), (0, "", ""))

    def test_a_broken_guard_does_not_block_the_session(self):
        (self.root / "tools/kb/projections.toml").write_text("[[projection]\n")
        code, out, err = self.run_hook({"tool_name": "Read", "tool_input": {}})
        self.assertEqual((code, out), (1, ""))
        self.assertIn("kb guard: TOMLDecodeError", err)

    def test_codex_events_return_a_supported_pre_tool_use_denial(self):
        for tool, arguments in (
                ("Bash", {"command": "cat names.csv", "workdir": str(self.root / "kb")}),
                ("apply_patch", {"command": "*** Begin Patch\n"
                                 "*** Delete File: kb/names.csv\n*** End Patch\n"})):
            with self.subTest(tool=tool):
                code, out, err = self.run_hook({"hook_event_name": "PreToolUse",
                    "session_id": "fixture", "turn_id": "fixture", "cwd": str(self.root),
                    "tool_name": tool, "tool_input": arguments})
                self.assertEqual((code, err), (0, ""))
                self.assertEqual(set(json.loads(out)), {"hookSpecificOutput"})
                decision = json.loads(out)["hookSpecificOutput"]
                self.assertEqual(decision["permissionDecision"], "deny")
                self.assertEqual(set(decision), {"hookEventName", "permissionDecision",
                                                 "permissionDecisionReason"})

    def test_codex_launcher_finds_the_worktree_from_a_subdirectory_with_spaces(self):
        root = make_repo(self.root / "worktree with spaces")
        python = root / ".venv/bin/python"
        python.parent.mkdir(parents=True)
        python.symlink_to(sys.executable)
        settings = json.loads((repo.ROOT / guard.CODEX_SETTINGS).read_text(encoding="utf-8"))
        command = settings["hooks"]["PreToolUse"][0]["hooks"][0]["command"]
        call = {"cwd": str(root / "tools/kb"), "tool_name": "Bash",
                "tool_input": {"command": "cat ../../kb/names.csv"}}
        result = subprocess.run(command, shell=True, cwd=root / "tools/kb",
            input=json.dumps(call), capture_output=True, text=True,
            env={**os.environ, "KB_GUARD": ""})
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertEqual(json.loads(result.stdout)["hookSpecificOutput"]["permissionDecision"],
                         "deny")


class CheckTest(unittest.TestCase):
    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory()
        self.base = Path(self.scratch.name).resolve()

    def tearDown(self):
        self.scratch.cleanup()

    def check(self, name, files=None):
        return guard.check(make_repo(self.base / name, files))

    def test_a_complete_guard_passes(self):
        self.assertEqual(self.check("complete"), [])

    def test_the_settings_run_the_hook_before_every_guarded_tool(self):
        settings = {"hooks": {"PreToolUse": [{"matcher": "Read|Bash", "hooks": [
            {"type": "command", "command": "python3 tools/kb/hook.py"}]}]}}
        failures = self.check("matcher", {".claude/settings.json": json.dumps(settings)})
        self.assertEqual(len(failures), 1)
        self.assertIn("before Edit, Write, MultiEdit, NotebookEdit, Grep, Glob", failures[0])

    def test_ignore_lists_the_trees_and_the_active_guarded_projections(self):
        failures = self.check("ignore", {".ignore": "/kb/\n"})
        self.assertEqual(failures, [".ignore: /l0/ is not listed (fix: add it)",
                                    ".ignore: /defs/*.xml is not listed (fix: add it)"])

    def test_untracked_settings_fail(self):
        root = make_repo(self.base / "untracked")
        subprocess.run(["git", "rm", "-q", "--cached", ".claude/settings.json"], cwd=root,
                       check=True)
        self.assertEqual(guard.check(root)[0],
                         ".claude/settings.json: not tracked (fix: git add -f "
                         ".claude/settings.json)")

    def test_codex_settings_cover_the_canonical_patch_tool(self):
        settings = {"hooks": {"PreToolUse": [{"matcher": "|".join(guard.TOOLS), "hooks": [
            {"type": "command", "command": "python3 tools/kb/hook.py"}]}]}}
        failures = self.check("codex-matcher", {".codex/hooks.json": json.dumps(settings)})
        self.assertEqual(len(failures), 1)
        self.assertIn(".codex/hooks.json: PreToolUse", failures[0])
        self.assertIn("before apply_patch", failures[0])

    def test_codex_settings_must_be_tracked_and_synchronous(self):
        root = make_repo(self.base / "codex-untracked")
        subprocess.run(["git", "rm", "-q", "--cached", ".codex/hooks.json"], cwd=root,
                       check=True)
        self.assertEqual(guard.check(root)[0], ".codex/hooks.json: not tracked "
                         "(fix: git add -f .codex/hooks.json)")
        settings = json.loads(json.dumps(CODEX_SETTINGS))
        settings["hooks"]["PreToolUse"][0]["hooks"][0]["async"] = True
        failures = self.check("codex-async", {".codex/hooks.json": json.dumps(settings)})
        self.assertEqual(len(failures), 1)
        self.assertIn("before Read, Edit", failures[0])


if __name__ == "__main__":
    unittest.main()
