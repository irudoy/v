from argparse import Namespace
import contextlib
import io
import json
import unittest
from unittest import mock

from kb import cli, repo
from kb.answer import Answer
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


class AtCommandTest(unittest.TestCase):
    def test_literal_flag_uses_the_same_reader_session_and_json_contract(self):
        answer = Answer("unused")
        answer.data = {"l0": {"literal": {"value_hex": "0001e30c", "matches": []}}}
        for literal in (False, True):
            with self.subTest(literal=literal):
                output = io.StringIO()
                arguments = ["at", "jk78c:0001e30c", "--json", "--no-sync"]
                if literal:
                    arguments.append("--literal")
                with mock.patch.object(cli.reader, "graph_session", return_value=contextlib.nullcontext("graph")) as session, \
                        mock.patch.object(cli.read, "at", return_value=answer) as at, \
                        contextlib.redirect_stdout(output):
                    self.assertEqual(cli.main(arguments), 0)
                session.assert_called_once_with(repo.ROOT, True)
                at.assert_called_once_with("graph", "jk78c:0001e30c", None, repo.ROOT, literal=literal)
                self.assertEqual(json.loads(output.getvalue()), answer.data)


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
        def fresh(root, no_sync, held=False):
            yield None

        args = Namespace(ref=text, layout=layout, no_sync=True)
        with mock.patch.object(cli.reader, "graph_session", fresh), \
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
        with mock.patch.object(cli.lock, 'held', side_effect=AssertionError('invalid arguments must refuse before locking')), \
                contextlib.redirect_stderr(io.StringIO()) as err:
            self.assertEqual(cli.main(["check", "--only", "missing_check"]), 2)
        self.assertIn("unknown or inactive checks", err.getvalue())
        self.assertIn("blocks", err.getvalue())
        self.assertIn("chains", err.getvalue())


class BenchCommandTest(unittest.TestCase):
    QUESTION = {"id": 9, "command": "kb log apc_output", "budget": 100,
                "baseline": [], "expect": [r"^apc_output/ram$", r"ffff206c -> ffff11f5"]}

    def bench(self, text, *, questions=None, only=None, code=0, baseline=1000, check=False):
        config = {"question": questions or [dict(self.QUESTION)]}
        args = Namespace(only=only, check=check)

        def reply(argv):
            print(text, end="")
            return code

        out = io.StringIO()
        with mock.patch.object(cli.read, "bench", return_value=config), \
                mock.patch.object(cli, "main", side_effect=reply) as command, \
                mock.patch.object(cli, "baseline_tokens", return_value=baseline) as base, \
                contextlib.redirect_stdout(out):
            result = cli.command_bench(args)
        return result, out.getvalue(), command.call_args_list, base.call_count

    def test_an_answer_with_all_required_content_passes_within_budget_and_baseline(self):
        code, text, calls, baselines = self.bench(
            "apc_output/ram\n  jk00d ffff206c -> ffff11f5\n")
        self.assertEqual(code, 0)
        self.assertIn("PASS", text)
        self.assertEqual(calls, [mock.call(["log", "apc_output", "--full"])])
        self.assertEqual(baselines, 1)

    def test_a_small_successful_answer_missing_the_correction_fails(self):
        code, text, _, _ = self.bench("apc_output/ram\n  former meaning name apc_command\n")
        self.assertEqual(code, 1)
        self.assertIn("FAIL", text)
        self.assertIn("missing expected content", text)
        self.assertIn("ffff206c -> ffff11f5", text)

    def test_expected_content_does_not_override_exit_budget_or_baseline_failures(self):
        answer = "apc_output/ram\nffff206c -> ffff11f5\n"
        for params in ({"code": 5}, {"baseline": 1}, {}):
            with self.subTest(params=params):
                text = answer + ("x" * 400 if not params else "")
                self.assertEqual(self.bench(text, **params)[0], 1)

    def test_the_check_runs_no_baseline_and_keeps_the_other_conditions(self):
        answer = "apc_output/ram\n  jk00d ffff206c -> ffff11f5\n"
        code, text, _, baselines = self.bench(answer, baseline=1, check=True)
        self.assertEqual((code, baselines), (0, 0))
        self.assertIn("PASS", text)
        self.assertIn("baseline      -", text)
        for params, reply in (({"code": 5}, answer), ({}, answer + "x" * 400),
                              ({}, "apc_output/ram\n")):
            with self.subTest(params=params, reply=reply[-20:]):
                code, _, _, baselines = self.bench(reply, check=True, **params)
                self.assertEqual((code, baselines), (1, 0))

    def test_the_check_lists_a_question_that_needs_more_than_the_graph_as_not_run(self):
        answer = "apc_output/ram\n  jk00d ffff206c -> ffff11f5\n"
        code_question = {"id": 8, "command": "kb code jk78c:000564a4", "budget": 100,
                         "baseline": [], "expect": [r"void FUN_000564a4\("],
                         "needs": ["ghidra"]}
        questions = [dict(self.QUESTION), code_question]
        code, text, calls, _ = self.bench(answer, questions=questions, check=True)
        self.assertEqual(code, 0)
        self.assertEqual(calls, [mock.call(["log", "apc_output", "--full"])])
        self.assertIn(" 8  NOT RUN  needs ghidra", text)
        self.assertNotIn(" 8  PASS", text)
        code, text, calls, _ = self.bench(answer, questions=questions)
        self.assertEqual(code, 1)
        self.assertEqual(len(calls), 2)
        self.assertIn(" 8  FAIL", text)
        with self.assertRaises(KbError) as error:
            self.bench(answer, questions=questions, only=[8], check=True)
        self.assertEqual(error.exception.code, 2)
        self.assertIn("--check", str(error.exception))

    def test_invalid_needs_fail_before_any_question_runs(self):
        for needs in ("ghidra", ["docker"], ["ghidra", "ghidra"], [None], [["ghidra"]]):
            with self.subTest(needs=needs):
                config = {"question": [{**self.QUESTION, "needs": needs}]}
                with mock.patch.object(cli.read, "bench", return_value=config), \
                        mock.patch.object(cli, "main") as command, \
                        self.assertRaises(KbError) as error:
                    cli.command_bench(Namespace(only=None, check=True))
                self.assertEqual(error.exception.code, 2)
                self.assertIn("needs", str(error.exception))
                command.assert_not_called()

    def test_invalid_contracts_fail_before_any_question_or_baseline_runs(self):
        for expected in (None, [], "literal", [None], [" "], ["["], [".*"], ["(foo)?"]):
            with self.subTest(expected=expected):
                config = {"question": [{**self.QUESTION, "expect": expected}]}
                with mock.patch.object(cli.read, "bench", return_value=config), \
                        mock.patch.object(cli, "main") as command, \
                        mock.patch.object(cli, "baseline_tokens") as baseline, \
                        self.assertRaises(KbError) as error:
                    cli.command_bench(Namespace(only=None, check=False))
                self.assertEqual(error.exception.code, 2)
                command.assert_not_called()
                baseline.assert_not_called()

    def test_an_invalid_later_contract_is_checked_before_any_question_runs(self):
        invalid = {**self.QUESTION, "id": 6, "expect": []}
        with self.assertRaises(KbError) as error:
            self.bench("apc_output/ram\nffff206c -> ffff11f5\n",
                       questions=[self.QUESTION, invalid])
        self.assertEqual(error.exception.code, 2)
        self.assertIn("question 6", str(error.exception))

    def test_unknown_ids_do_not_pass_without_running_a_question(self):
        with self.assertRaises(KbError) as error:
            self.bench("", only=[99])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
