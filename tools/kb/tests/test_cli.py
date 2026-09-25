import contextlib
import io
import unittest

from kb import cli, repo
from kb.repo import KbError


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


class CypherCommandTest(unittest.TestCase):
    def test_a_writing_query_is_a_usage_error_before_any_connection(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cli.main(["cypher", "MATCH (n) DETACH DELETE n"]), 2)
        self.assertIn("read-only", err.getvalue())


class CheckCommandTest(unittest.TestCase):
    def test_unknown_checks_are_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cli.main(["check", "--only", "homology"]), 2)
        self.assertIn("unknown or inactive checks", err.getvalue())


if __name__ == "__main__":
    unittest.main()
