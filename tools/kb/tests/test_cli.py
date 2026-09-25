import contextlib
import io
import unittest

from kb import cli, repo
from kb.repo import KbError


class OutputBudgetTest(unittest.TestCase):
    def test_tokens_count_utf8_bytes_by_three(self):
        self.assertEqual(cli.tokens("abc"), 1)
        self.assertEqual(cli.tokens("abcd"), 2)
        self.assertEqual(cli.tokens("ж"), 1)

    def test_an_answer_within_budget_is_unchanged(self):
        self.assertEqual(cli.fit("line\n", 10, "narrow"), "line\n")
        self.assertEqual(cli.fit("x" * 900, None, "narrow"), "x" * 900)

    def test_a_cut_answer_starts_with_truncated_and_names_the_narrower_call(self):
        text = "".join(f"line {number:04d}\n" for number in range(400))
        out = cli.fit(text, 200, "kb code 7mfk:00026740 --budget 400")
        first = out.splitlines()[0]
        self.assertTrue(first.startswith("TRUNCATED: "))
        self.assertIn("kb code 7mfk:00026740 --budget 400", first)
        self.assertLessEqual(cli.tokens(out), 200)


class LocationTest(unittest.TestCase):
    def test_layout_prefix_or_option(self):
        layout, address = cli.parse_location("7mfk:0x26740")
        self.assertEqual((layout.id, address), ("7mfk", 0x26740))
        layout, address = cli.parse_location("26740", "jk00d")
        self.assertEqual((layout.id, address), ("jk00d", 0x26740))

    def test_errors_carry_the_specified_exit_codes(self):
        with self.assertRaises(KbError) as missing:
            cli.parse_location("26740")
        self.assertEqual(missing.exception.code, 2)
        with self.assertRaises(KbError) as unknown:
            cli.parse_location("zz99:26740")
        self.assertEqual(unknown.exception.code, 5)
        with self.assertRaises(KbError) as disagree:
            cli.parse_location("7mfk:26740", "jk00d")
        self.assertEqual(disagree.exception.code, 2)

    def test_an_instruction_resolves_to_the_function_whose_body_holds_it(self):
        layout = repo.layout("7mfk")
        self.assertEqual(cli.containing_function(layout, 0x26740), "00026740")
        self.assertEqual(cli.containing_function(layout, 0x26742), "00026740")
        with self.assertRaises(KbError) as outside:
            cli.containing_function(layout, 0x8000)
        self.assertEqual(outside.exception.code, 5)


class CheckCommandTest(unittest.TestCase):
    def test_unknown_checks_are_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cli.main(["check", "--only", "homology"]), 2)
        self.assertIn("unknown or inactive checks", err.getvalue())


if __name__ == "__main__":
    unittest.main()
