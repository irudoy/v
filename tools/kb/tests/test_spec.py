"""Declarative command contracts agree with the CLI and MCP interfaces."""

import argparse
import contextlib
from dataclasses import dataclass, field
import io
import re
import unittest

from kb import cli, mcp, project, repo, spec

COMMON = "### 12.1 Invocation"
READ = "### 12.2 Read commands"
WRITE = "### 12.3 Write commands"
CODES = "### 12.5 Exit codes"
READ_OPTIONS = "<read options>"
PACKAGE = "tools/kb/src/kb"
TOKEN = re.compile(r"\[|\]|\.\.\.|--[a-z-]+|(?:<[^>]+>[:=]?)+|"
                   r"[a-z]+(?:-[a-z]+)*(?:\|[a-z]+(?:-[a-z]+)*)*")
WORD = re.compile(r"[a-z]+(?:-[a-z]+)*")


@dataclass
class Option:
    value: bool
    required: bool
    repeat: bool


@dataclass
class Positional:
    required: bool
    variadic: bool
    choices: tuple = ()


@dataclass
class Syntax:
    text: str
    table: str
    command: str = ""
    positionals: list = field(default_factory=list)
    options: dict = field(default_factory=dict)


def _close(tokens, start):
    depth = 0
    for index in range(start, len(tokens)):
        depth += {"[": 1, "]": -1}.get(tokens[index], 0)
        if depth == 0:
            return index
    raise ValueError(f"unbalanced brackets in {' '.join(tokens)}")


def _elements(syntax, tokens, start, stop, common, optional=False, repeat=False):
    index = start
    while index < stop:
        token = tokens[index]
        if token == "[":
            close = _close(tokens, index)
            again = close + 1 < stop and tokens[close + 1] == "..."
            _elements(syntax, tokens, index + 1, close, common, True, repeat or again)
            index = close + (2 if again else 1)
        elif token == READ_OPTIONS:
            syntax.options.update(common)
            index += 1
        elif token.startswith("--"):
            value = index + 1 < stop and tokens[index + 1].startswith("<")
            index += 2 if value else 1
            again = index < stop and tokens[index] == "..."
            index += 1 if again else 0
            syntax.options[token] = Option(value, not optional, repeat or again)
        else:
            again = index + 1 < stop and tokens[index + 1] == "..."
            choices = tuple(token.split("|")) if "|" in token else ()
            syntax.positionals.append(Positional(not optional, repeat or again, choices))
            index += 2 if again else 1


def parse(text, table, common=None):
    """The syntax of a command of the tables: its command words, positionals,
    and options."""
    tokens = TOKEN.findall(text)
    if "".join("".join(tokens).split()) != "".join(text.split()) or tokens[:1] != ["kb"]:
        raise ValueError(f"`{text}` is no command syntax")
    index = 1
    while index < len(tokens) and WORD.fullmatch(tokens[index]):
        index += 1
    syntax = Syntax(text, table, " ".join(tokens[1:index]))
    _elements(syntax, tokens, index, len(tokens), common or {})
    return syntax


def common_options(root=repo.ROOT):
    """The options of `[<read options>]` from the table of section 12.1."""
    found = {}
    for cells in spec.table(COMMON, root):
        for text in re.findall(r"`([^`]+)`", cells[0]):
            found.update(parse(f"kb {text}", COMMON).options)
    return {name: Option(option.value, False, False) for name, option in found.items()}


def rows(root=repo.ROOT):
    """Every command syntax of the tables of sections 12.2 and 12.3."""
    common = common_options(root)
    found = []
    for heading in (READ, WRITE):
        for cells in spec.table(heading, root):
            for text in re.findall(r"`([^`]+)`", cells[0]):
                found.append(parse(text, heading, common))
    return found


def leaves(parser, prefix=()):
    """{command words: parser} of every command of `kb` without subcommands."""
    found = {}
    for name, sub in mcp._subparsers(parser).choices.items():
        nested = [action for action in sub._actions
                  if isinstance(action, argparse._SubParsersAction)]
        if nested:
            found.update(leaves(sub, prefix + (name,)))
        else:
            found[" ".join(prefix + (name,))] = sub
    return found


def options(parser):
    """{long option: action} of a command, without help."""
    return {max(action.option_strings, key=len): action for action in parser._actions
            if action.option_strings and not isinstance(action, argparse._HelpAction)}


def positionals(parser):
    return [action for action in parser._actions if not action.option_strings]


def _value(action):
    if action is not None and action.choices:
        return str(next(iter(action.choices)))
    if action is not None and action.type is not None:
        try:
            action.type("x")
        except (ValueError, TypeError, argparse.ArgumentTypeError):
            return "1"
    return "x"


def argv(syntax, parser, full):
    """A command line of the syntax: its required elements, and with `full`
    every element, a variadic or repeated one twice."""
    line = syntax.command.split()
    actions = positionals(parser)
    for index, positional in enumerate(syntax.positionals):
        if not (positional.required or full):
            continue
        action = actions[index] if index < len(actions) else None
        value = positional.choices[0] if positional.choices else _value(action)
        line += [value] * (2 if positional.variadic and full else 1)
    found = options(parser)
    for name, option in syntax.options.items():
        if not (option.required or full):
            continue
        once = [name, _value(found.get(name))] if option.value else [name]
        line += once * (2 if option.repeat and full else 1)
    return line


class CommandTableTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = rows()
        cls.parser = cli.build_parser()
        cls.commands = leaves(cls.parser)

    def forms(self, command):
        return [syntax for syntax in self.rows if syntax.command == command]


    def test_every_declared_row_names_a_command_of_the_parser(self):
        for syntax in self.rows:
            self.assertIn(syntax.command, self.commands,
                          f"`{syntax.text}` names no command of kb")

    def test_every_command_of_the_parser_has_a_declared_row(self):
        for command in self.commands:
            self.assertTrue(self.forms(command),
                            f"kb {command} has no declared command row")

    def test_the_options_agree(self):
        for command, parser in self.commands.items():
            forms = self.forms(command)
            if not forms:
                continue
            with self.subTest(command=command):
                stated = {}
                for syntax in forms:
                    for name, option in syntax.options.items():
                        stated.setdefault(name, []).append(option)
                actions = options(parser)
                self.assertEqual(sorted(stated), sorted(actions))
                for name, action in actions.items():
                    found = stated[name]
                    self.assertEqual({option.value for option in found}, {action.nargs != 0},
                                     f"{name} takes a value")
                    self.assertEqual({option.repeat for option in found},
                                     {isinstance(action, argparse._AppendAction)},
                                     f"{name} repeats")
                    required = len(found) == len(forms) and all(option.required
                                                                for option in found)
                    self.assertEqual(required, bool(action.required), f"{name} is required")

    def test_the_positionals_agree(self):
        arity = {None: (True, False), "+": (True, True), "*": (False, True),
                 "?": (False, False)}
        for command, parser in self.commands.items():
            forms = self.forms(command)
            if len(forms) != 1:
                continue
            with self.subTest(command=command):
                actions = positionals(parser)
                stated = forms[0].positionals
                self.assertEqual(len(stated), len(actions))
                for positional, action in zip(stated, actions):
                    self.assertEqual((positional.required, positional.variadic),
                                     arity[action.nargs], action.dest)
                    self.assertEqual(set(positional.choices), set(action.choices or ()),
                                     action.dest)

    def test_every_declared_row_parses(self):
        for syntax in self.rows:
            parser = self.commands.get(syntax.command)
            if parser is None:
                continue
            for full in (False, True):
                line = argv(syntax, parser, full)
                with self.subTest(line=" ".join(line)):
                    error = io.StringIO()
                    try:
                        with contextlib.redirect_stderr(error):
                            self.parser.parse_args(line)
                    except SystemExit:
                        self.fail(f"`{syntax.text}`: {error.getvalue().strip()}")

    def test_the_mcp_tools_are_the_declared_read_commands(self):
        read = {syntax.command for syntax in self.rows if syntax.table == READ}
        self.assertEqual(set(mcp.READ_COMMANDS), read)
        self.assertEqual(mcp.WRITE_COMMANDS, ("apply",))

    def test_the_exit_codes_are_those_of_the_table(self):
        table = {int(cells[0]) for cells in spec.table(CODES)}
        used = set()
        for path in (repo.ROOT / PACKAGE).rglob("*.py"):
            used.update(int(code) for code in
                        re.findall(r"\bcode=(\d+)", path.read_text(encoding="utf-8")))
        self.assertEqual(used | {0}, table)


class SyntaxTest(unittest.TestCase):
    def test_a_hyphenated_command_keeps_its_options_and_positionals(self):
        syntax = parse("kb set-link <from> <type> <to> <key>=<value>... "
                       "[--offset <offset>] [--slot <slot>] [--dry-run]", WRITE)
        self.assertEqual(syntax.command, "set-link")
        self.assertEqual(syntax.positionals, [Positional(True, False)] * 3 +
                         [Positional(True, True)])
        self.assertEqual(syntax.options, {"--offset": Option(True, False, False),
                                         "--slot": Option(True, False, False),
                                         "--dry-run": Option(False, False, False)})
        for text in ("kb set-link- <from>", "kb -link <from>", "kb set-link! <from>"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse(text, WRITE)

    def test_generated_examples_accept_an_integer_converter(self):
        parser = argparse.ArgumentParser()
        parser.add_argument("--offset", type=lambda text: int(text, 0))
        syntax = parse("kb [--offset <offset>]", WRITE)
        self.assertEqual(argv(syntax, parser, True), ["--offset", "1"])
        self.assertEqual(parser.parse_args(argv(syntax, parser, True)).offset, 1)

    def test_a_syntax_gives_its_positionals_and_options(self):
        common = {"--full": Option(False, False, False)}
        syntax = parse("kb unresolved <meaning> --layout <l> [--method <kind> --count <n>] "
                       "[--evidence <item>]... [<path>...] [<read options>]", READ, common)
        self.assertEqual(syntax.command, "unresolved")
        self.assertEqual(syntax.positionals, [Positional(True, False), Positional(False, True)])
        self.assertEqual(syntax.options, {
            "--layout": Option(True, True, False), "--method": Option(True, False, False),
            "--count": Option(True, False, False), "--evidence": Option(True, False, True),
            "--full": Option(False, False, False)})

    def test_a_required_option_repeats_with_dots_after_its_value(self):
        syntax = parse("kb absent <meaning> --evidence <item>...", WRITE)
        self.assertEqual(syntax.options["--evidence"], Option(True, True, True))

    def test_words_name_the_command_and_bars_the_choices(self):
        self.assertEqual(parse("kb family new", WRITE).command, "family new")
        syntax = parse("kb instance up|down|status|prune", WRITE)
        self.assertEqual(syntax.command, "instance")
        self.assertEqual(syntax.positionals, [Positional(True, False, ("up", "down", "status",
                                                                         "prune"))])

    def test_a_location_and_an_assignment_are_one_positional(self):
        syntax = parse("kb set <ref> <key>=<value>... --where <layout>:<address>", WRITE)
        self.assertEqual(syntax.positionals, [Positional(True, False), Positional(True, True)])
        self.assertEqual(syntax.options["--where"], Option(True, True, False))

    def test_text_outside_the_grammar_is_refused(self):
        with self.assertRaises(ValueError):
            parse("kb show <ref> (--layout <l>)", READ)
        with self.assertRaises(ValueError):
            parse("uv run kb show <ref>", READ)

    def test_an_escaped_bar_stays_in_its_cell(self):
        cells = [cells for cells in spec.table(WRITE) if cells[0].startswith("`kb instance")]
        self.assertEqual(cells, [["`kb instance up|down|status|prune`",
                                  "[Instances](#11-instances)"]])


if __name__ == "__main__":
    unittest.main()
