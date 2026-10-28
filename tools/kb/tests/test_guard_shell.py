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

    def test_git_metadata_does_not_authorize_a_blob_read_or_a_message_file_read(self):
        for command in ("git show --stat HEAD:kb/names.csv", "git commit -F kb/names.csv",
                        "git -C kb grep needle", "git diff --no-index kb/names.csv open.txt"):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        for command in ("git show --stat HEAD -- kb/names.csv", "git diff -- kb/names.csv",
                        "git -C . status --short", "git log --oneline -- kb/names.csv"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))

    def test_static_shell_variables_preserve_literal_and_file_operand_roles(self):
        self.assertIsNone(self.denied("Bash", command="name=kb/names.csv; printf '%s' \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv; cat \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv cat \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv; name=open.txt cat \"$name\""))
        self.assertIsNotNone(self.denied("Bash", command="env name=kb/names.csv python3 other.py"))
        self.assertIsNotNone(self.denied("Bash", command="name=kb/names.csv; export name; python3 other.py"))


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
