"""Bind the bounded remainder byte to exact arithmetic and registered literals."""
import ast
import builtins
from collections import defaultdict
from dataclasses import replace
from fractions import Fraction
from functools import cache
import math
import re

import pytest

from kb import compile, repo
from kb.arithmetic import Grammar
from tools.kb.tests import test_injection_start_delay_chain as publication

FORMULA = 'F = (uint8(ffff4184)>>6)&1; R = F*uint16(ffff10ca)+(1-F)*uint16(ffff11bc); K = floor(uint32(16*R*50331)/65536); P = uint16(ffff241c); P = max(P,uint16(RAM16[0xffff23d4])); P = max(P,uint16(RAM16[0xffff23d6])); P = max(P,uint16(RAM16[0xffff23d8])); P = max(P,uint16(RAM16[0xffff23da])); P = max(P,uint16(RAM16[0xffff23dc])); P = max(P,uint16(RAM16[0xffff23de])); p = min(255,floor(K*P/65536)); E = uint16(ffff192e); D0 = max(0,2*E-4*p); W = (uint8(ffff24c9)>>5)&1; D = max(0,D0-W*ROM8[0x000083ea]); r = D%120; to = floor(min(116,max(4,r))/4)'


@cache
def program(formula):
    assert Grammar(repo.config()).validate(formula) is None
    text = re.sub(r'\bffff[0-9a-f]{4}\b', lambda match: f'memory[{int(match[0], 16)}]', formula)

    class ExactDivision(ast.NodeTransformer):
        def visit_BinOp(self, node):
            node = self.generic_visit(node)
            if isinstance(node.op, ast.Div):
                return ast.copy_location(ast.Call(ast.Name('Fraction', ast.Load()),
                                                  [node.left, node.right], []), node)
            return node

    return builtins.compile(ast.fix_missing_locations(ExactDivision().visit(ast.parse(text))),
                              '<bounded injection remainder arithmetic>', 'exec')


def evaluate(row, formula=FORMULA):
    memory = {0xffff11bc: row[0][0], 0xffff10ca: row[0][1], 0xffff241c: row[2],
              0xffff192e: row[3], 0xffff4184: row[4][0], 0xffff24c9: row[4][1],
              0xffff4251: row[4][2], 0x83ea: row[5]}
    memory.update((0xffff23d4 + 2 * index, value) for index, value in enumerate(row[1]))
    values = dict(memory=memory, RAM16=memory, ROM8=memory, min=min, max=max, floor=math.floor,
                  uint8=lambda value: value & 255, uint16=lambda value: value & 65535,
                  uint32=lambda value: value & 0xffffffff, Fraction=Fraction)
    exec(program(formula), {'__builtins__': {}}, values)
    return values


def require_literals(formula):
    rows = publication.literals()
    assert len(rows) == publication.actual_counts()[2]
    for index, row in enumerate(rows):
        actual = evaluate(row, formula)
        assert [actual[name] for name in ('K', 'P', 'p', 'D0', 'D', 'r', 'to')] == [
            row[10], row[11], row[13], row[14], row[15], row[17], row[8]], index
        assert type(actual['to']) is int and 1 <= actual['to'] <= 29


def test_injection_angle_equation_matches_every_registered_literal():
    require_literals(FORMULA)
    rows = publication.literals()
    assert set(row[17] for row in rows) == set(range(120))
    assert set(row[8] for row in rows) == set(range(1, 30))


@pytest.mark.parametrize('before,after', (
    ('D%120', 'D%121'), ('max(4,r)', 'max(0,r)'), ('min(116,', 'min(112,'),
    ('/4)', '/3)'), ('uint32(16*R*50331)', 'uint16(16*R*50331)'),
    ('D0-W*ROM8[0x000083ea]', 'D0-(1-W)*ROM8[0x000083ea]'),
))
def test_injection_angle_literals_reject_modulus_clamp_width_and_condition_changes(before, after):
    assert FORMULA.count(before) == 1
    with pytest.raises(AssertionError):
        require_literals(FORMULA.replace(before, after))


@pytest.mark.parametrize('upper', (117, 118, 119, 120))
def test_injection_angle_stored_byte_retains_equivalent_upper_clamps(upper):
    assert {row[17] for row in publication.literals()} == set(range(120))
    require_literals(FORMULA.replace('min(116,', f'min({upper},'))


def test_injection_angle_is_independent_of_the_lead_override_and_ignored_control_bits():
    groups = defaultdict(set)
    for row in publication.literals():
        key = tuple(row[0]), tuple(row[1]), row[2], row[3], row[4][0] & 64, row[4][1] & 32, row[5]
        groups[key].add(row[8])
    assert all(len(values) == 1 for values in groups.values())
    assert set(row[4][2] for row in publication.literals()) == set(range(256))


def test_injection_angle_none_sign_has_an_exact_factory_periodicity_witness():
    rows = publication.literals()
    lower = [row for row in rows if row[3] == 15359 and row[8] == 29 and row[5] == 30
             and row[15] == 30718 and row[17] == 118]
    upper = [row for row in rows if row[3] == 15360 and row[8] == 1 and row[5] == 30
             and row[15] == 30720 and row[17] == 0]
    pairs = [(a, b) for a in lower for b in upper if a[:3] + a[4:8] == b[:3] + b[4:8]]
    assert pairs
    a, b = pairs[0]
    assert a[20] == 0 and b[20] == 1
    assert evaluate(a)['to'] == 29 and evaluate(b)['to'] == 1


def test_injection_angle_published_arithmetic_records_follow_the_native_chain():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'injection_phase')]
    grammar = Grammar(repo.config())
    indices = [index + 1 for index, step in enumerate(chain.steps)
               if grammar.validate(step['note']) is None
               and publication.normalized(model, step['via']) == ['transformed_pulse_maximum/fn']]
    assert indices == [9, 10, 11, 12]
    step = chain.steps[9]
    assert publication.normalized(model, step) == publication.REQUIRED_STEPS['9']
    assert step['note'] == FORMULA and step['sign'] == 'none'
    assert publication.normalized(model, step['via']) == ['transformed_pulse_maximum/fn']
    text = publication.section(publication.SPEC, 'Bounded injection start-delay publication')
    assert f'The {len(indices)} arithmetic records' in text
    assert 'steps 9, 10, 11, and 12' in text
    assert '29 -> 1' in text and '15359 -> 15360' in text


@pytest.mark.parametrize('field,value', (
    ('sign', 'positive'), ('sign', 'negative'), ('effect', 'subtracts'),
    ('via', []), ('via', [publication.SymbolKey('7mfk', 'fn', 0x21e14)]),
    ('to', publication.SymbolKey('7mfk', 'ram', 0xffff23f0)),
    ('note', FORMULA.replace('D%120', 'D%121')),
))
def test_injection_angle_step_refuses_unbound_semantics(field, value):
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'injection_phase')]
    changed = replace(chain, steps=[dict(step) for step in chain.steps])
    changed.steps[9][field] = value
    proxy = type('Model', (), {'entities': {('chain', 'injection_phase'): changed},
                              'meaning_of': model.meaning_of})()
    publication.chain_document_contract(model)
    with pytest.raises(AssertionError):
        publication.chain_document_contract(proxy)
