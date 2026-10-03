"""Syntax of chain arithmetic, configured by ``[chains.arithmetic]``.

This parser checks notation, not the truth of an equation or its stock-code
binding. Conditions belong to typed meaning links, outside the expression.
"""

from dataclasses import dataclass
import re

from kb.repo import KbError


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    at: int


class Grammar:
    def __init__(self, config):
        label = '[chains.arithmetic] of tools/kb/config.toml'
        try:
            row = config['chains']['arithmetic']
            self.patterns = {key: re.compile(row[key]) for key in ('address', 'number', 'name')}
            self.variables = frozenset(row['variables'])
            self.readers = frozenset(row['readers'])
            self.unary = frozenset(row['unary'])
            self.binary = {operator: rank for rank, group in enumerate(row['binary'], 1)
                           for operator in group}
            self.functions = row['functions']
            lists = (row['variables'], row['readers'], row['unary'],
                     *(row['binary']))
            if (not isinstance(row['binary'], list) or not row['binary']
                    or any(not isinstance(group, list) or not group
                           or any(not isinstance(item, str) or not item for item in group)
                           for group in lists)
                    or not isinstance(self.functions, dict) or not self.functions
                    or any(not isinstance(arity, int) or isinstance(arity, bool) or arity < 1
                           for arity in self.functions.values())
                    or any(pattern.fullmatch('') is not None for pattern in self.patterns.values())):
                raise ValueError('invalid token, operator, or function declaration')
            operators = [item for group in row['binary'] for item in group]
            if len(operators) != len(set(operators)):
                raise ValueError('a binary operator has two precedences')
            symbols = set(self.binary) | self.unary | set('=;(),[]')
            if (not self.unary <= {'+', '-', '~'}
                    or not self.binary.keys() <= {'+', '-', '*', '/', '%', '&', '|', '^', '<<', '>>'}):
                raise ValueError('an operator is not arithmetic punctuation')
            if any(not self.patterns['name'].fullmatch(item)
                   for item in self.variables | self.readers | self.functions.keys()):
                raise ValueError('an operand or function is not a name')
            self.symbols = sorted(symbols, key=lambda item: (-len(item), item))
        except (KeyError, TypeError, ValueError, re.error) as error:
            raise KbError(f'{label}: {error}', code=2) from None

    def tokens(self, text):
        at = 0
        while at < len(text):
            if text[at].isspace():
                at += 1
                continue
            for kind, pattern in self.patterns.items():
                match = pattern.match(text, at)
                if match and (match.end() == len(text)
                              or not re.match(r'[A-Za-z0-9_.]', text[match.end()])):
                    yield Token(kind, match.group(), at)
                    at = match.end()
                    break
            else:
                symbol = next((item for item in self.symbols if text.startswith(item, at)), None)
                if symbol is None:
                    raise ValueError(f'character {text[at]!r} at {at + 1}')
                yield Token('symbol', symbol, at)
                at += len(symbol)
        yield Token('end', '', len(text))

    def validate(self, text):
        """None for assignments of arithmetic expressions, else their error."""
        if not isinstance(text, str) or not text.strip():
            return 'a note requires at least one arithmetic equation'
        try:
            Parser(self, list(self.tokens(text))).parse()
        except (ValueError, RecursionError) as error:
            return str(error) or 'expression nesting exceeds the parser limit'
        return None


class Parser:
    def __init__(self, grammar, tokens):
        self.grammar, self.tokens = grammar, tokens
        self.at = 0
        self.variables = set(grammar.variables)

    @property
    def token(self):
        return self.tokens[self.at]

    def take(self, expected=None):
        token = self.token
        if expected is not None and token.text != expected:
            self.fail(f'expected {expected!r}')
        self.at += 1
        return token

    def fail(self, message):
        found = self.token.text or 'end of note'
        raise ValueError(f'{message} at {self.token.at + 1}, found {found!r}')

    def parse(self):
        while True:
            target = self.take()
            if target.kind not in ('address', 'name'):
                self.fail('an equation needs an address or variable on the left')
            if target.text in self.grammar.functions or target.text in self.grammar.readers:
                self.fail('an equation cannot assign a function or memory reader')
            self.take('=')
            self.expression()
            while self.token.text == '=':
                self.take('=')
                self.expression()
            if target.kind == 'name':
                self.variables.add(target.text)
            if self.token.kind == 'end':
                return
            self.take(';')
            if self.token.kind == 'end':
                self.fail('an equation must follow the separator')

    def expression(self, minimum=1):
        if self.token.text in self.grammar.unary:
            self.take()
            self.expression(max(self.grammar.binary.values()) + 1)
        else:
            self.atom()
        while self.grammar.binary.get(self.token.text, 0) >= minimum:
            precedence = self.grammar.binary[self.take().text]
            self.expression(precedence + 1)

    def atom(self):
        token = self.token
        indexable = token.kind == 'address'
        if token.text == '(':
            self.take('(')
            self.expression()
            self.take(')')
        elif token.kind in ('address', 'number'):
            self.take()
        elif token.kind == 'name':
            self.take()
            if self.token.text == '(':
                if token.text not in self.grammar.functions:
                    self.fail(f'unknown arithmetic function {token.text!r}')
                self.take('(')
                count = 0
                if self.token.text != ')':
                    self.expression()
                    count = 1
                    while self.token.text == ',':
                        self.take(',')
                        self.expression()
                        count += 1
                self.take(')')
                expected = self.grammar.functions[token.text]
                if count != expected:
                    self.fail(f'{token.text} requires {expected} operands, received {count}')
            elif token.text in self.grammar.readers:
                self.take('[')
                self.expression()
                self.take(']')
            elif token.text not in self.variables:
                self.fail(f'unbound arithmetic variable {token.text!r}')
            else:
                indexable = True
        else:
            self.fail('expected an arithmetic operand')
        while self.token.text == '[':
            if not indexable:
                self.fail('only an address or variable admits indexing')
            self.take('[')
            self.expression()
            self.take(']')
