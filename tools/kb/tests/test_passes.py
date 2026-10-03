from argparse import Namespace
import contextlib
import io
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from kb import cli, match, passes


class PassesCase(unittest.TestCase):
    """A repository root with one input `a.txt`, the source `tools/kb/k.py`,
    and a check `fake` that reads the input."""

    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name)
        self.write("a.txt", "one")
        self.write("tools/kb/k.py", "")
        self.write("tools/kb/tests/test_k.py", "")
        inputs = mock.patch.dict(passes.INPUTS, {"fake": lambda root: {"a.txt"}})
        inputs.start()
        self.addCleanup(inputs.stop)
        self.runs = []
        self.failures = []
        self.reads = set()

    def write(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def check(self, root):
        self.runs.append(root)
        match.READ.update(self.reads)
        return list(self.failures)

    def run_check(self, changed=True):
        record = passes.Passes(self.root)
        failures = record.run("fake", self.check, changed)
        record.save()
        return failures


class PassesTest(PassesCase):
    def test_the_inputs_of_a_check_include_the_source_of_kb_without_its_tests(self):
        self.assertEqual(passes.Passes(self.root).inputs("fake"), {"a.txt", "tools/kb/k.py"})

    def test_hardware_results_are_inputs_of_the_levels_gate(self):
        self.write("patches/hardware-results.toml", 'hardware_status = "pass"\n')
        with mock.patch.object(passes, "model", return_value={"a.txt"}):
            record = passes.Passes(self.root)
            self.assertIn("patches/hardware-results.toml", record.inputs("levels"))
            before = record.digest("levels", [])
            self.write("patches/hardware-results.toml", 'hardware_status = "pending"\n')
            self.assertNotEqual(record.digest("levels", []), before)

    def test_a_pass_is_skipped_until_an_input_changes(self):
        self.assertEqual(self.run_check(), [])
        self.assertIsNone(self.run_check())
        self.write("a.txt", "three")
        self.assertEqual(self.run_check(), [])
        self.write("tools/kb/k.py", "x = 1\n")
        self.assertEqual(self.run_check(), [])
        self.assertIsNone(self.run_check())
        self.assertEqual(len(self.runs), 3)

    def test_without_changed_every_check_runs(self):
        self.run_check()
        self.assertEqual(self.run_check(changed=False), [])
        self.assertEqual(len(self.runs), 2)

    def test_a_failure_forgets_the_last_pass(self):
        self.run_check()
        self.write("a.txt", "three")
        self.failures = ["a.txt: wrong"]
        self.assertEqual(self.run_check(), ["a.txt: wrong"])
        self.write("a.txt", "one")
        self.failures = []
        self.assertEqual(self.run_check(), [])
        self.assertEqual(len(self.runs), 3)

    def test_the_files_that_a_check_reads_join_its_inputs(self):
        self.write("tests/test_x.py", "def test_x(): pass\n")
        self.reads = {"tests/test_x.py", "a.txt"}
        self.run_check()
        self.assertEqual(passes.Passes(self.root).read("fake"), ["tests/test_x.py"])
        self.reads = set()
        self.assertIsNone(self.run_check())
        self.write("tests/test_x.py", "def test_y(): pass\n")
        self.assertEqual(self.run_check(), [])
        self.assertEqual(len(self.runs), 2)
        self.assertEqual(passes.Passes(self.root).read("fake"), [])

    def test_a_directory_is_an_input_of_fixed_value(self):
        (self.root / "module").mkdir()
        record = passes.Passes(self.root)
        self.assertEqual(record.value("module"), passes.DIRECTORY)
        self.assertNotEqual(record.value("a.txt"), passes.DIRECTORY)


class CheckCommandTest(PassesCase):
    def test_changed_reports_the_checks_that_it_skips(self):
        with mock.patch.dict(cli.CHECKS, {"fake": self.check}, clear=True), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            args = Namespace(only=None, changed=True)
            self.assertEqual(cli.command_check(args, self.root), 0)
            self.assertEqual(cli.command_check(args, self.root), 0)
            self.failures = ["a.txt: wrong"]
            self.write("a.txt", "three")
            self.assertEqual(cli.command_check(args, self.root), 1)
        self.assertEqual(out.getvalue().splitlines(), [
            "check fake: PASS",
            "check fake: PASS, its inputs are those of its last pass",
            "fake: a.txt: wrong",
            "check fake: FAIL 1"])


if __name__ == "__main__":
    unittest.main()
