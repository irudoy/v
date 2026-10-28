"""Shell data and actual protected operations have separate guard decisions."""

from pathlib import Path
import json
import os
import subprocess
import sys

from kb import project
from tools.kb.tests.test_guard import GuardCase, PROJECTIONS


class ShellOperationTest(GuardCase):
    def test_bare_tree_operands_are_protected(self):
        for command in ("cat kb", "cat -n kb/names.csv", "cp -n kb/names.csv open.txt",
                        "ls kb", "rg needle kb", "rg --files l0",
                        "grep -R needle kb", "head l0", "find kb"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_absolute_globs_and_symlinks_keep_the_project_root(self):
        (self.root / "alias").symlink_to(self.root / "kb", target_is_directory=True)
        for operand in (self.path("kb/*"), self.path("l0/*/*.csv"),
                        self.path("defs/*.xml"), self.path("alias/*")):
            for program in ("cat", "ls", "rg --files"):
                with self.subTest(program=program, operand=operand):
                    self.assertIsNotNone(self.denied("Bash", command=f'{program} "{operand}"'))

    def test_subshell_directory_changes_do_not_escape_their_scope(self):
        for command in ("(cd l0); cat open.txt", "(cd l0 && uv run kb brief); cat open.txt",
                        "(cd l0; (cd ..)); cat open.txt"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in ("(cd l0; cat 7mfk/funcs.csv); cat open.txt",
                        "cd l0; (cd ..); cat 7mfk/funcs.csv",
                        "(cd l0); cat kb/names.csv"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_command_wrappers_leave_the_inner_command_decision(self):
        for command in ("timeout 600 uv run kb check --only sites",
                        "timeout -k 5 -s KILL 600 uv run kb check --only sites",
                        "timeout --signal=TERM --preserve-status 10m kb brief",
                        "nice -n 10 uv run kb brief", "nice uv run kb brief",
                        "nohup uv run kb check", "env KB_LIMIT=1 uv run kb brief",
                        "env -u KB_GUARD uv run kb brief", "time -p uv run kb brief",
                        "timeout 5 nice -n 5 env A=1 uv run kb find knock"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in ("timeout 5 cat kb/names.csv", "timeout -s KILL 5 cat kb/names.csv",
                        "timeout --kill-after=5 10m cat defs/JK08A.xml",
                        "nice -n 10 cat l0/7mfk/funcs.csv", "nohup cat kb/names.csv",
                        "env A=1 cat kb/names.csv", "timeout 5 nice env cat kb/names.csv",
                        "env -C kb cat names.csv", "time -o kb/names.csv true",
                        "env -S 'cat kb/names.csv'"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_literal_drafts_and_message_text_are_not_file_operands(self):
        messaging = Path.home() / ".codex/skills/codex-messaging/scripts/sessions.py"
        commands = [
            "printf '%s\\n' 'kb/names.csv' > draft.txt",
            "echo l0/7mfk/funcs.csv > draft.txt",
            "printf '%s' '>' 'kb/names.csv'",
            "printf '%s' '<<' 'kb/names.csv'",
            "printf '%s' '$(cat kb/names.csv)'",
            "printf '%s' '`cat kb/names.csv`'",
            "cat <<<'kb/names.csv'",
            "cat <<'EOF' > draft.txt\nkb/ram/x.toml\n$(cat kb/names.csv)\nEOF",
            f"python3 {messaging} send recipient --text 'Read kb/names.csv and l0/7mfk/funcs.csv'",
            "git commit -m 'Preserve kb/ram/x.toml'",
            "git commit -F - <<'EOF'\nPreserve kb/ram/x.toml\nEOF",
            "test 'kb/names.csv' != 'l0/7mfk/funcs.csv'",
        ]
        for command in commands:
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "cat <<EOF > draft.txt\n$(cat kb/names.csv)\nEOF",
            "python3 - <<EOF\nprint('$(cat kb/names.csv)')\nEOF",
            'printf "%s" "$(cat $(printf kb/names.csv))"',
            'cat <<<"$(cat kb/names.csv)"',
            'captured=$(cat kb/names.csv)',
            'captured=$(cat kb/names.csv) printf "%s" done',
            "sh <<'EOF'\ncat kb/names.csv\nEOF",
            f"python3 {messaging} send recipient --file kb/names.csv",
            f'python3 {messaging} send recipient --text "$(cat kb/names.csv)"',
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_literal_python_metadata_is_separate_from_actual_file_access(self):
        programs = [
            "header = '# kb/ram/x.toml'; print(header)",
            "assert not 'tmp/capture.txt'.startswith('kb/')",
            "from pathlib import Path\nimport json, tomllib\n"
            "source = Path('tmp/capture.txt')\ntext = source.read_text()\n"
            "body = text.split('# kb/ram/x.toml', 1)[-1]\n"
            "body = body.replace('kb/ram/x.toml', 'captured')\n"
            "result = tomllib.loads(body)\nPath('tmp/metadata.json').write_text(json.dumps(result))",
            "captured = ['kb/ram/x.toml']; assert captured == ['kb/ram/x.toml']",
        ]
        for program in programs:
            with self.subTest(program=program):
                self.assertIsNone(self.denied("Bash", command=f"python3 - <<'PY'\n{program}\nPY"))
        for program in (
            "print(open('kb/names.csv').read())",
            "from pathlib import Path\nPath('l0/7mfk/funcs.csv').read_text()",
            "filename = 'kb/names.csv'; print(open(filename).read())",
            "from pathlib import Path\np = Path('kb'); (p / 'names.csv').read_text()",
            "import subprocess\nsubprocess.run(['cat', 'kb/names.csv'])",
            "from unknown import consume\nconsume('kb/names.csv')",
            "from os import system as print\nprint('cat kb/names.csv')",
            "filename = 'kb/names.csv'; print(open(filename).read()); filename = 'open.txt'",
            "from pathlib import Path\nvalue = 'literal'\nvalue = Path('open.txt')\nvalue.replace('kb/names.csv')",
            "with open('kb/names.csv') as source:\n    print(source.read())",
        ):
            with self.subTest(program=program):
                self.assertIsNotNone(self.denied("Bash", command=f"python3 - <<'PY'\n{program}\nPY"))

    def test_generated_file_edits_are_guarded_even_when_the_projection_is_open(self):
        (self.root / "tools/kb/projections.toml").write_text(PROJECTIONS + '''
[[projection]]
path = "defs/open-generated.csv"
generator = "tools/defs/build.py"
inputs = []
consumers = []
read = "open"
''')
        self.guard = project.hook.Guard(self.root)
        for command in (
            "echo value > defs/open-generated.csv", "tee defs/open-generated.csv",
            "cp open.txt defs/open-generated.csv", "mv open.txt defs/open-generated.csv",
            "cp --target-directory=kb open.txt",
            "sed -i '' 's/a/b/' defs/open-generated.csv", "rm defs/open-generated.csv",
            "git restore -- defs/open-generated.csv", "git checkout HEAD -- defs/open-generated.csv",
            "git checkout defs/open-generated.csv",
            "git rm defs/open-generated.csv", "git diff --output=defs/open-generated.csv",
            "sort -o defs/open-generated.csv open.txt",
            "awk 'BEGIN {print 1 > \"defs/open-generated.csv\"}' open.txt",
            "python3 -c \"from pathlib import Path; Path('defs/open-generated.csv').write_text('x')\"",
            "python3 -c \"open('defs/open-generated.csv', mode='w')\"",
            "python3 -c \"from pathlib import Path; Path('defs/open-generated.csv').open('w')\"",
            "python3 -c \"from pathlib import Path; Path('open.txt').rename('defs/open-generated.csv')\"",
            "python3 -c \"from pathlib import Path; target=Path('open.txt'); target.replace('defs/open-generated.csv')\"",
            "python3 -c \"from pathlib import Path; paths=[Path('open.txt')]; paths[0].replace('defs/open-generated.csv')\"",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        for command in ("cat defs/open-generated.csv", "git diff -- defs/open-generated.csv",
                        "git restore --staged defs/open-generated.csv"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))

    def test_editor_reads_do_not_become_generated_section_edits(self):
        for command in (
            "sed -n '1,170p' GUIDE.md",
            "sed -n '1,170p' open.txt",
            "awk 'NR < 170 {print $1}' GUIDE.md",
            "sed 's|old|kb/names.csv|' open.txt",
            "awk '{print \"kb/names.csv\"}' open.txt",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "sed -i '' 's/a/b/' GUIDE.md",
            "sed --in-place=.bak 's/a/b/' GUIDE.md",
            "sed -n 'w GUIDE.md' open.txt",
            "sed 's/a/b/w GUIDE.md' open.txt",
            "sed -n 'r kb/names.csv' open.txt",
            r"sed '/a\/b/r kb/names.csv' open.txt",
            "sed -fkb/names.csv open.txt",
            "awk '{print $1 > \"GUIDE.md\"}' open.txt",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_metadata_can_raise_a_builtin_exception_before_writing_an_open_note(self):
        source = ("from pathlib import Path\n"
                  "note = Path('/private/tmp/note.md')\ntext = note.read_text()\n"
                  "paragraph = 'Read GUIDE.md and kb/names.csv as metadata'\n"
                  "if 'anchor' not in text:\n    raise SystemExit('missing anchor')\n"
                  "note.write_text(text.replace('anchor', paragraph))")
        self.assertIsNone(self.denied("Bash", command=f"python3 - <<'PY'\n{source}\nPY"))
        self.assertIsNotNone(self.denied("Bash", command="python3 -c 'from os import system as SystemExit; SystemExit(\"cat kb/names.csv\")'"))

    def test_git_metadata_does_not_authorize_a_blob_read_or_a_message_file_read(self):
        for command in ("git show --stat HEAD:kb/names.csv", "git commit -F kb/names.csv",
                        "git -C kb grep needle", "git diff --no-index kb/names.csv open.txt"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        for command in ("git show --stat HEAD -- kb/names.csv", "git diff -- kb/names.csv",
                        "git show 2a4ce4dc -- GUIDE.md Makefile | grep kb",
                        "git show HEAD -- kb/names.csv", "git show HEAD -- GUIDE.md",
                        "git show HEAD -- public:kb/names.csv",
                        "git -C . status --short", "git log --oneline -- kb/names.csv"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))

    def test_git_show_review_does_not_authorize_blobs_or_output_writes(self):
        for command in ("git show HEAD:kb/names.csv", "git show HEAD:l0/7mfk/funcs.csv",
                        "git show HEAD --output=GUIDE.md", "git show HEAD -- GUIDE.md > GUIDE.md"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        self.guard.git = ("show --stat",)
        self.assertIsNone(self.denied("Bash", command="git show --stat HEAD -- GUIDE.md"))
        self.assertIsNotNone(self.denied("Bash", command="git show HEAD -- GUIDE.md"))

    def test_static_shell_variables_preserve_literal_and_file_operand_roles(self):
        self.assertIsNone(self.denied("Bash", command="name=kb/names.csv; printf '%s' \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv; cat \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv cat \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv; name=open.txt cat \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="env name=kb/names.csv python3 other.py"))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv; export name; python3 other.py"))

    def test_pipeline_data_becomes_xargs_file_operands(self):
        for command in (
            "echo kb/names.csv | xargs cat",
            "echo kb/names.csv | xargs -I{} cat {}",
            "printf '%s\\n' kb/names.csv | xargs cat",
            "echo kb/names.csv | cat | xargs -n 1 cat",
            "echo defs/JK08A.xml | xargs tee",
            "echo open.txt | xargs cat kb/names.csv",
            "xargs -a kb/names.csv echo",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        for command in (
            "echo kb/names.csv | xargs echo",
            "echo kb/names.csv | xargs printf '%s'",
            "echo open.txt | xargs cat",
            "echo kb/names.csv; echo open.txt | xargs cat",
            "rg -l 'kb/names.csv' tools/ | xargs cat",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))

    def test_substitution_file_operands_treat_backticks_and_dollar_forms_equally(self):
        for command in ("cat `echo kb`/names.csv", "cat $(echo kb)/names.csv"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_python_program_arguments_are_file_operands(self):
        for command in (
            "python3 -c 'import sys; print(open(sys.argv[1]).read())' kb/names.csv",
            "python3 outside.py kb/names.csv",
            "python3 outside.py kb/names.csv <<'PY'\nprint('input data')\nPY",
            "python3 - kb/names.csv <<'PY'\nimport sys\nprint(open(sys.argv[1]).read())\nPY",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        self.assertIsNone(self.denied("Bash", command="python3 -c 'import sys; print(sys.argv)' open.txt"))
        self.assertIsNone(self.denied("Bash", command="python3 -u - open.txt <<'PY'\nprint('input data')\nPY"))

    def test_bound_variables_are_expanded_before_sed_operand_checks(self):
        self.assertIsNone(self.denied("Bash", command="S=/private/tmp/scratch; sed s/a/b/ $S/a.py > $S/b.py"))
        self.assertIsNotNone(self.denied("Bash", command="S=kb; sed s/a/b/ $S/names.csv"))

    def test_dynamic_operands_keep_conservative_checks_within_the_repository(self):
        # /private/tmp contains the fixture; model the actual root outside it.
        self.guard.root = self.guard.cwd = Path("/workspace/vq")
        self.assertIsNone(self.denied("Bash", command="for t in a b; do cat /private/tmp/$t.output; done"))
        self.assertIsNone(self.denied("Bash", command="for t in a b; do cat /workspace/vq/$t.output; done"))
        for command in ("for t in $unknown; do cat /workspace/vq/$t.output; done",
                        "for t in a b; do cat kb/$t.toml; done",
                        "for t in $unknown; do cat /workspace/$t.output; done"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_review_forms_through_the_bash_json_hook(self):
        cases = [
            ("echo kb/names.csv | xargs cat", True),
            ("echo kb/names.csv | xargs -I{} cat {}", True),
            ("cat `echo kb`/names.csv", True),
            ("cat $(echo kb)/names.csv", True),
            ("python3 -c 'import sys; print(open(sys.argv[1]).read())' kb/names.csv", True),
            ("python3 outside.py kb/names.csv", True),
            ("S=/private/tmp/scratch; sed s/a/b/ $S/a.py > $S/b.py", False),
            ("S=/private/tmp/scratch; cp $S/a.py /private/tmp/b.py", False),
            ("for t in a b; do cat /outside/scratch/$t.output; done", False),
            ("for t in a b; do cat kb/$t.toml; done", True),
            ("for n in 9 62; do gh issue view $n --repo irudoy/vhrev --json body -q .body; done", False),
            ('gh issue close 40 --repo irudoy/vhrev --comment "...kb/fn/rough-porpoise.toml..."', False),
            ("gh issue create --body-file kb/names.csv", True),
        ]
        for command, denied in cases:
            with self.subTest(command=command):
                result = subprocess.run([sys.executable, str(self.root / "tools/kb/hook.py")],
                    input=json.dumps({"tool_name": "Bash", "cwd": str(self.root),
                                      "tool_input": {"command": command}}),
                    capture_output=True, text=True,
                    env={**os.environ, "KB_GUARD": "", "HOME": str(self.root)})
                self.assertEqual((result.returncode, result.stderr), (0, ""))
                if denied:
                    decision = json.loads(result.stdout)["hookSpecificOutput"]
                    self.assertEqual(decision["permissionDecision"], "deny")
                else:
                    self.assertEqual(result.stdout, "")

    def test_literal_for_lists_resolve_every_possible_operand(self):
        for command in (
            "for n in 9 62; do gh issue view $n --repo irudoy/vhrev --json body -q .body; done",
            "for name in open.txt other.txt; do unknown-command $name; done",
            "for name in open.txt other.txt; do cat $name; done",
            "for a in open other; do for b in txt csv; do cat $a.$b; done; done",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "for name in open.txt kb/names.csv; do unknown-command $name; done",
            "for name in open.txt kb/names.csv; do cat $name; done",
            "for a in open kb; do for b in names.csv; do cat $a/$b; done; done",
            "name=open.txt; for name in $unknown; do cat $name; done",
            "for name in $unknown; do unknown-command $name; done",
            "for name in 9 62; do cat kb/names.csv; done",
            "for name in kb/names.csv; do echo $name | xargs cat; done",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_gh_issue_and_pr_text_options_are_data_but_body_files_are_operands(self):
        for subject in ("issue", "pr"):
            for action in ("create", "comment", "close", "edit"):
                for option in ("--comment", "--body", "--title", "-b", "-t"):
                    with self.subTest(subject=subject, action=action, option=option):
                        self.assertIsNone(self.denied("Bash", command=
                            f'gh {subject} {action} 40 --repo irudoy/vhrev {option} "...kb/fn/rough-porpoise.toml..."'))
        for command in (
            "gh issue close 40 --comment='kb/names.csv'",
            "gh pr edit 40 -bkb/names.csv -tkb/ram/x.toml",
            "body=kb/names.csv; gh issue comment 40 --body \"$body\"",
            "gh issue create --body-file GUIDE.md",
            "gh pr edit -F GUIDE.md",
            "gh issue create --body-file - <<'EOF'\nkb/names.csv\nEOF",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "gh issue create --body-file kb/names.csv",
            "gh pr edit -Fkb/names.csv",
            'gh issue close 40 --comment "$(cat kb/names.csv)"',
            "gh pr edit --body-file=kb/names.csv",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))


def test_unsupported_fallback_python_returns_a_deliberate_denial(tmp_path):
    script = ("import runpy,sys\nsys.version_info=(3,10,0)\n"
              f"runpy.run_path({project.hook.__file__!r},run_name='__main__')\n")
    result = subprocess.run([sys.executable, "-c", script], input="{}",
        capture_output=True, text=True, env={**os.environ, "KB_GUARD": "", "HOME": str(tmp_path)})
    assert result.returncode == 0 and result.stderr == ""
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "Python 3.11" in decision["permissionDecisionReason"]


def test_missing_tomllib_returns_a_deliberate_denial(tmp_path):
    script = ("import builtins,runpy\noriginal_import=builtins.__import__\n"
              "def checked_import(name,*args,**kwargs):\n"
              "    if name == 'tomllib':\n"
              "        raise ModuleNotFoundError('missing tomllib',name='tomllib')\n"
              "    return original_import(name,*args,**kwargs)\n"
              "builtins.__import__=checked_import\n"
              f"runpy.run_path({project.hook.__file__!r},run_name='__main__')\n")
    result = subprocess.run([sys.executable, "-c", script], input="{}",
        capture_output=True, text=True, env={**os.environ, "KB_GUARD": "", "HOME": str(tmp_path)})
    assert result.returncode == 0 and result.stderr == ""
    decision = json.loads(result.stdout)["hookSpecificOutput"]
    assert decision["permissionDecision"] == "deny"
    assert "tomllib" in decision["permissionDecisionReason"]
