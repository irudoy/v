"""Shell data and actual protected operations have separate guard decisions."""

from pathlib import Path
import json
import os
import subprocess
import sys
import time

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
                        "timeout 5 nice -n 5 env A=1 uv run kb find knock",
                        "timeout --signal=TERM 10 uv run kb brief", "timeout -sTERM 10 kb brief",
                        "nice -n5 uv run kb find knock", "nice --adjustment=5 kb brief",
                        "env --unset=KB_GUARD uv run kb brief", "time -f%e uv run kb brief",
                        "env --split-string='uv run kb brief'", "env -S'kb brief'"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in ("timeout 5 cat kb/names.csv", "timeout -s KILL 5 cat kb/names.csv",
                        "timeout --kill-after=5 10m cat defs/JK08A.xml",
                        "nice -n 10 cat l0/7mfk/funcs.csv", "nohup cat kb/names.csv",
                        "env A=1 cat kb/names.csv", "timeout 5 nice env cat kb/names.csv",
                        "env -C kb cat names.csv", "time -o kb/names.csv true",
                        "env -S 'cat kb/names.csv'", "time --output=kb/names.csv true",
                        "time -okb/names.csv true", "env --chdir=kb cat names.csv",
                        "env -Ckb cat names.csv", "env --split-string='cat kb/names.csv'",
                        "env -S'cat kb/names.csv'", "timeout -sTERM 5 cat kb/names.csv",
                        "nice -n5 cat l0/7mfk/funcs.csv"):
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

    def test_gh_issue_and_pr_numbers_urls_and_branches_are_data(self):
        for command in (
            "for n in $(seq 9 15); do gh issue view $n --repo irudoy/vhrev; done",
            'gh pr view "$branch" --json title -q .title',
            "gh issue reopen $n --comment 'kb/names.csv'",
            "gh pr comment https://github.com/irudoy/vhrev/pull/3 --body-file GUIDE.md",
            'gh issue edit "$n" --add-label "$label" --body "$text"',
            "gh pr edit kb/names.csv --title x",
            "gh issue view 9 --comments",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "for n in $(seq 9 15); do gh issue comment $n --body-file kb/names.csv; done",
            'gh issue edit $n --body-file "$file"',
            "gh issue reopen 9 -F l0/7mfk/funcs.csv",
            "gh pr create --template kb/names.csv",
            "gh pr create -Tkb/names.csv",
            "gh issue create --recover=l0/7mfk/funcs.csv",
            'gh issue reopen 9 --comment "$(cat kb/names.csv)"',
            "gh pr view 3 > kb/names.csv",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_gh_api_endpoints_and_fields_are_data_but_input_files_are_operands(self):
        for command in (
            "for e in $(seq 42 43); do gh api repos/irudoy/vhrev/issues/$e/sub_issues --jq '.[]'; done",
            "gh api repos/irudoy/vhrev/issues/$e/sub_issues",
            "gh api repos/irudoy/vhrev/contents/kb/names.csv --jq .sha",
            "gh api graphql -f query='{ viewer { login } }' -F number=9 -f id=$n",
            "gh api repos/irudoy/vhrev/issues -F title='kb/names.csv' -f body=\"$text\"",
            "gh api repos/irudoy/vhrev/issues -F body=@GUIDE.md --input GUIDE.md",
            "gh api repos/irudoy/vhrev/issues --input - <<'EOF'\nkb/names.csv\nEOF",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "gh api repos/irudoy/vhrev/issues --input kb/names.csv",
            "gh api repos/irudoy/vhrev/issues --input=l0/7mfk/funcs.csv",
            "gh api repos/irudoy/vhrev/issues -F body=@kb/names.csv",
            "gh api repos/irudoy/vhrev/issues -Fbody=@kb/names.csv",
            "gh api repos/irudoy/vhrev/issues --field=body=@kb/names.csv",
            "body=@kb/names.csv; gh api repos/irudoy/vhrev/issues -F text=$body",
            "gh api repos/irudoy/vhrev/issues -F body=$unknown",
            "gh api repos/irudoy/vhrev/issues -F \"$pair\"",
            "gh api repos/irudoy/vhrev/issues --input \"$file\"",
            "gh api repos/irudoy/vhrev/issues -f body=\"$(cat kb/names.csv)\"",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_dynamic_loop_values_are_data_for_kb_references(self):
        for command in (
            'for f in $(cat list.txt); do uv run kb show "$f/field"; done',
            'for f in $(cat list.txt); do kb where "$f"; done',
            'for f in $refs; do uv run kb code "$f"; done',
            "for f in `cat list.txt`; do uv run kb at $f; done",
            *(f'cat list.txt | while read f; do uv run kb {read} "$f"; done'
              for read in ("show", "where", "find", "log", "raw", "code", "at", "impact", "path")),
            'if test -n "$f"; then uv run kb show "$f"; else kb find "$f"; fi',
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            'for f in $(cat list.txt); do cat "$f/field"; done',
            'for f in $(cat list.txt); do uv run cat "$f"; done',
            'for f in $(cat kb/names.csv); do uv run kb show "$f"; done',
            'for f in kb/*; do uv run kb show "$f"; done',
            'for f in l0/7mfk/*.csv; do echo "$f"; done',
            'for f in $d/*; do uv run kb show "$f"; done',
            'cat list.txt | while read f; do cat "$f"; done',
            "while read f; do cat kb/names.csv; done < list.txt",
            "if true; then cat kb/names.csv; fi",
            "if grep -q x kb/names.csv; then true; fi",
            "! cat l0/7mfk/funcs.csv",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_jq_programs_are_data_and_its_inputs_are_read_operands(self):
        (self.root / "open.jq").write_text(".l0\n")
        (self.root / "tmp").mkdir(exist_ok=True)
        (self.root / "tmp/prog.jq").write_text('import "names" as $d {search: "../kb"};\n$d\n')
        for command in (
            "jq '{l0:.l0, symbols:[.symbols[]|{ref:.ref,keys:(.keys|{layout,address,name,summary,"
            "note}),links:.links}]}' tmp/fuel-map.json tmp/request-map.json",
            "jq -r 'input_filename as $file | .l0.accessors[] | select(.modes | index(\"store\")) "
            "| [$file, .function, (.sites | tojson)] | @tsv' tmp/1nd:fffe8079.json",
            "jq '.symbols[] | select(.ref | test(\"/ram$\")) | .ref' tmp/fuel-map.json",
            "jq '{location, l0}' tmp/jk00c:0003f240.json",
            "jq -n --slurpfile a tmp/a.json --slurpfile b tmp/b.json "
            "'[$a[0][], $b[0][]] | map({ref, table: .l0})'",
            "jq '[.[] as $m | $m.accesses[] | {reader:.function_address,table:$m.table_address}]' "
            "tmp/jk78c-table-reader-inventory.json",
            "jq -nr --arg layout l0 --argjson count 1 '{$layout, $count, mode: .include}'",
            "jq -n '$ARGS' --args kb/names.csv l0",
            "jq -f open.jq tmp/a.json",
            "jq -n --rawfile text open.txt '$text' > tmp/out.json",
            "cat tmp/a.json | jq -c '.l0'",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "jq . kb/names.csv", "jq '.l0' l0/7mfk/funcs.csv", "jq . defs/JK08A.xml",
            "jq -n --slurpfile a l0/7mfk/funcs.csv '$a'", "jq -n --rawfile a defs/JK08A.xml '$a'",
            "jq -f kb/names.csv tmp/a.json", "jq --from-file kb/names.csv", "jq -nf kb/names.csv",
            'jq . "$file"', "jq . $(cat list.txt)", "jq . tmp/a.json > kb/names.csv",
            'jq "$program" tmp/a.json', "jq $program tmp/a.json",
            "jq 'import \"kb/names\" as $names; $names' -n", "jq -n 'include \"lib\"; .'",
            "jq -n '\"lib\" | modulemeta'", "jq -L kb -n .", "jq -Lkb -n .",
            "jq --library-path kb -n .", "F=kb/names.csv jq . tmp/a.json",
            'jq . tmp/a.json "$(cat kb/names.csv)"',
            # Module loading through a comment, from a program file, or from
            # a program file that cannot be read.
            "jq -n 'import # c\n\"kb/names\" as $d {search: \".\"}; $d'",
            "jq -n 'include #\n\"l0/x\" {search: \".\"}; .'",
            "jq -n -f tmp/prog.jq", "jq -n -f tmp/missing.jq",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_exit_statuses_are_not_file_operands(self):
        for command in (
            'for ref in 1nd:fffe945f 1nd:fffe9460; do uv run --frozen kb at "$ref" --json --full '
            '> "tmp/$ref.json" || exit $?; done',
            "uv run kb brief || exit $?", "test -f open.txt || return 1",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "exit $(cat kb/names.csv)", 'for f in names.csv; do cat "kb/$f" || exit $?; done',
            "uv run kb brief > kb/names.csv || exit $?",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))

    def test_brace_patterns_and_document_values_have_bounded_inspection(self):
        rows = "".join(f'  {{ kind = \\"l0\\", supports = \\"identity\\", at = \\"jk78c:{n:08x}\\", '
                       f'value = \\"{n:08x}\\" }},\n' for n in range(16))
        draft = ("python3 -c \"from pathlib import Path\nPath('TARGET').write_text('''[[op]]\n"
                 f"evidence = [\n{rows}]\n''')\"")
        started = time.monotonic()
        self.assertIsNone(self.denied("Bash", command=draft.replace("TARGET", "tmp/draft.toml")))
        self.assertIsNotNone(self.denied("Bash", command=draft.replace("TARGET", "defs/JK08A.xml")))
        self.assertIn("brace pattern", self.denied("Bash", command="cat " + "{a,b}" * 12))
        self.assertLess(time.monotonic() - started, 5)
        self.assertIsNotNone(self.denied("Bash", command="cat {open.txt,kb/names.csv}"))
        self.assertIsNone(self.denied("Bash", command="cat {open.txt,defs/open.csv}"))
        self.assertEqual(project.hook.expand("{a,b}/{c,d}"), ["a/c", "a/d", "b/c", "b/d"])

    def test_unquoted_braces_expand_around_a_quoted_space_and_sequences_refuse(self):
        for command in (
            "cat {kb,' '}/names.csv", "cat l{0,\\ }/7mfk/funcs.csv", "cat defs/{JK08A.xml,' '}",
            "cat {{kb,' '},x}/names.csv", "cat 'a b'{/../kb,}/names.csv",
            "cat l{0..0}/7mfk/funcs.csv", "cat {k..k}b/names.csv",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        for command in ("cat 'a {b,c} d'", "cat {open,tmp/a}.txt"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))

    def test_a_link_target_resolves_against_the_directory_of_its_link(self):
        for command in (
            "ln -s ../kb/names.csv tmp/zz.txt", "ln -s ../../l0/7mfk/funcs.csv tmp/a/zz.txt",
            "ln -s -t tmp ../kb", "ln -sf kb/names.csv zz.txt",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(self.denied("Bash", command=command))
        for command in ("ln -s ../open.txt tmp/zz.txt", "ln -s open.txt zz.txt"):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))

    def test_python_names_bound_by_another_form_have_no_literal_value(self):
        prelude = "d = ''.join(['k', 'b'])\nt = 'zz.txt'\n"
        read = "print(open(d + '/' + t).read(), 'l0')"
        programs = [prelude + rebinding + read for rebinding in (
            "t = 'names.csv'\n",
            "for t in ['names.csv']:\n    pass\n",
            "t, u = 'names.csv', 0\n",
            "(t := 'names.csv')\n",
            "t: str = 'names.csv'\n",
            "[(t := 'names.csv') for _ in [0]]\n",
            "[t] = ['names.csv']\n",
            "for t, u in [('names.csv', 0)]:\n    pass\n",
            "match 'names.csv':\n    case t:\n        pass\n",
        )] + [
            "import os\n" + prelude + "for t in ['names.csv']:\n    pass\n"
            "print(open(os.path.join(d, t)).read(), 'l0')",
            "d = ''.join(['k', 'b', '/names.csv'])\nt = 'zz.txt'\nt *= 0\nt += d\n"
            "print(open(t).read(), 'l0')",
            "t = 'zz.txt'\nfor t in ['kb/names.csv']:\n    pass\nprint(open(t).read())",
            "for t in ['kb/names.csv']:\n    open(t)",
            "for print in [open]:\n    print('kb/names.csv')",
        ]
        for program in programs:
            with self.subTest(program=program):
                self.assertIsNotNone(self.denied("Bash", command=f'python3 -c "{program}"'))

    def test_python_reads_dynamic_files_whose_name_end_no_guarded_file_has(self):
        for command in (
            "python3 -c \"import csv, json\nfrom pathlib import Path\n"
            "rows = list(csv.DictReader(open('tmp/operands.csv')))\nout = []\nfor row in rows:\n"
            "    code = Path('tmp/jk78c-' + row['reader'] + '-code.txt').read_text()\n"
            "    if row['site'] in code:\n"
            "        out.append({'kind': 'l0', 'supports': 'identity', 'at': row['site']})\n"
            "Path('tmp/bindings.toml').write_text(json.dumps(out))\"",
            "python3 -c \"import json; ops = json.load(open('tmp/ops.json')); "
            "[print(json.load(open('tmp/' + op['ref'].replace('/', '_') + '.json'))['l0']) "
            "for op in ops]\"",
            "python3 -c \"from pathlib import Path; "
            "print([Path('tmp', f'{name}-code.txt').read_text() for name in ['a', 'l0']])\"",
            "python3 -c \"import csv; csv.writer(open('tmp/out.csv', 'w')).writerows([['l0', 'x']])\"",
        ):
            with self.subTest(command=command):
                self.assertIsNone(self.denied("Bash", command=command))
        for command in (
            "python3 -c \"import sys; print(open('tmp/' + sys.argv[1] + '.toml').read(), 'l0')\" x",
            "python3 -c \"import json; name = json.load(open('tmp/a.json'))['l0']; "
            "print(open(name + 'names.csv').read())\"",
            "python3 -c \"import json\nfrom pathlib import Path\n"
            "for ref in json.load(open('tmp/ops.json')):\n    Path('tmp/' + ref + '.json').write_text('l0')\"",
            "python3 -c \"import json; from pathlib import Path; name = json.load(open('tmp/a.json'))['l0']; "
            "print(list(Path(name + '.json').iterdir()))\"",
            "python3 -c \"import json; name = json.load(open('tmp/a.json'))['l0']; print(open('tmp/' + name).read())\"",
            "python3 -c \"import json; name = json.load(open('tmp/a.json'))['l0']; print(open(name + '/..').read())\"",
            "python3 -c \"import csv; print(list(csv.reader(open('kb/names.csv'))))\"",
            "python3 -c \"from csv import DictReader; print(list(DictReader(open('tmp/a.csv'))), 'l0')\"",
            "python3 -c \"import os; os.replace('open.txt', 'defs/JK08A.xml')\"",
            "python3 -c \"from pathlib import Path; print(Path('.', 'kb/names.csv').read_text())\"",
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
