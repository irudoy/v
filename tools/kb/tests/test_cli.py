from argparse import Namespace
import contextlib
import io
import unittest
from unittest import mock

from kb import cli, repo
from kb.refs import Ref
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


class CodeTargetTest(unittest.TestCase):
    """`kb code` of a location, of a function symbol, and of a meaning."""

    MEANING = {"key": "demo/fn", "kind": "fn", "home": "7mfk"}
    SYMBOL = {"name": "demo", "kind": "fn", "layout": "1nd", "address": 0x11363C}
    HOME = {"name": "demo", "kind": "fn", "layout": "7mfk", "address": 0xC338A}

    def target(self, text, layout=None, found=None):
        """The target of `kb code <text> [--layout <layout>]` over references
        that `found` resolves by (text, layout)."""
        asked = []

        def resolve(session, ref, on, root):
            asked.append((ref, on))
            return found[(ref, on)]

        @contextlib.contextmanager
        def fresh(root, no_sync, log):
            yield None

        args = Namespace(ref=text, layout=layout, no_sync=True)
        with mock.patch.object(cli.graph, "fresh", fresh), \
                mock.patch.object(cli.refs, "resolve", resolve):
            layout, address, symbol = cli.code_target(args)
        return layout.id, address, symbol, asked

    def test_a_location_names_its_layout_and_address_without_the_graph(self):
        self.assertEqual(self.target("7mfk:000c3390", found={}),
                         ("7mfk", 0xC3390, None, []))

    def test_a_function_symbol_names_its_layout_and_address(self):
        found = {("demo", "1nd"): Ref("symbol", self.SYMBOL, self.MEANING, "1nd", 0x11363C)}
        self.assertEqual(self.target("demo", "1nd", found),
                         ("1nd", 0x11363C, "demo/fn/1nd-0011363c", [("demo", "1nd")]))

    def test_a_meaning_without_a_layout_shows_its_home_symbol(self):
        found = {("demo", None): Ref("meaning", self.MEANING),
                 ("demo", "7mfk"): Ref("symbol", self.HOME, self.MEANING, "7mfk", 0xC338A)}
        self.assertEqual(self.target("demo", found=found),
                         ("7mfk", 0xC338A, "demo/fn/7mfk-000c338a",
                          [("demo", None), ("demo", "7mfk")]))

    def test_a_meaning_without_a_symbol_on_the_layout_is_not_found(self):
        found = {("demo", "jk00c"): Ref("meaning", self.MEANING, layout="jk00c",
                                        note="no symbol on jk00c")}
        with self.assertRaises(KbError) as missing:
            self.target("demo", "jk00c", found)
        self.assertEqual(missing.exception.code, 5)
        self.assertIn("demo/fn has no symbol on jk00c", str(missing.exception))

    def test_data_is_no_function(self):
        cell = {"name": "load", "kind": "ram", "layout": "7mfk", "address": 0xFFFF8000}
        found = {("load", None): Ref("symbol", cell, None, "7mfk", 0xFFFF8000)}
        with self.assertRaises(KbError) as data:
            self.target("load", found=found)
        self.assertEqual(data.exception.code, 2)
        self.assertIn("kb show load/ram/7mfk-ffff8000", str(data.exception))


class CypherCommandTest(unittest.TestCase):
    def test_a_writing_query_is_a_usage_error_before_any_connection(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cli.main(["cypher", "MATCH (n) DETACH DELETE n"]), 2)
        self.assertIn("read-only", err.getvalue())


class CheckCommandTest(unittest.TestCase):
    def test_unknown_checks_are_a_usage_error(self):
        with contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cli.main(["check", "--only", "blocks"]), 2)
        self.assertIn("unknown or inactive checks", err.getvalue())


if __name__ == "__main__":
    unittest.main()
