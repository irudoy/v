"""Bind four ignition-advance views to the accepted bounded event arithmetic."""

from copy import deepcopy
import importlib.util
from pathlib import Path
import re

import pytest

from kb import compile, derive, repo
from kb.arithmetic import Grammar
from kb.model import SymbolKey


ROOT = repo.ROOT
FUNCTION = SymbolKey('7mfk', 'fn', 0x4d99c)
THIS_TEST = 'tools/kb/tests/test_ignition_event_arithmetic_chain.py'
OWNER_TEST = 'test_ignition_event_arithmetic_chain_owner_contract'
STOCK_TEST = 'test_ignition_event_arithmetic_registered_stock_contract'
SPEC = 'defs/JK08A.ignition-state.md'
SECTION = 'Shared ignition-advance event arithmetic'


def _accepted(filename, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / 'tools/kb/tests' / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


PUBLICATION = _accepted('test_knock_event_publication_chain.py', 'ignition_shared_event_publication')
RETARD = _accepted('test_knock_event_retard_chain.py', 'ignition_shared_event_retard')
EXPECTED = {
    21: (SymbolKey('7mfk', 'ram', 0xffff2378), SymbolKey('7mfk', 'ram', 0xffff12d6), 'adds', 'positive', PUBLICATION.FORMULA),
    22: (SymbolKey('7mfk', 'ram', 0xffff11d6), SymbolKey('7mfk', 'ram', 0xffff12d6), 'adds', 'positive', PUBLICATION.FORMULA),
    23: (SymbolKey('7mfk', 'ram', 0xffff11f9), SymbolKey('7mfk', 'ram', 0xffff11d6), 'subtracts', 'negative', RETARD.FORMULA),
    24: (SymbolKey('7mfk', 'ram', 0xffff22fa), SymbolKey('7mfk', 'ram', 0xffff11d6), 'adds', 'positive', RETARD.FORMULA),
}


def verify_ignition_event_steps(steps):
    assert len(steps) == 34
    grammar = Grammar(repo.config())
    for index, (source, target, effect, sign, formula) in EXPECTED.items():
        step = steps[index]
        assert (step['from'], step['to'], step['effect'], step['sign'], step['via']) == (
            source, target, effect, sign, [FUNCTION])
        assert grammar.validate(step['note']) is None
        assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', formula)


def _steps():
    return compile.cached(ROOT).entities[('chain', 'ignition_advance')].steps


def verify_published_execution_counts(section):
    published = [tuple(map(int, row)) for row in re.findall(
        r'([0-9]+) instructions / ([0-9]+) bytes / ([0-9]+) cases', section)]
    executed = []
    for accepted in (PUBLICATION, RETARD):
        region = accepted._region()
        executed.append((sum(end-start for start, end in region.code_spans)//2,
                         sum(end-start for start, end in region.code_spans)+
                         sum(size for address, size in region.pools), region.cases))
    assert published == executed


def test_ignition_event_arithmetic_chain_owner_contract():
    verify_ignition_event_steps(_steps())
    # These accepted contracts bind widths, independent R6 and all gate/retention links.
    PUBLICATION.test_knock_event_publication_chain_owner_contract()
    RETARD.test_knock_event_retard_chain_owner_contract()
    [section] = re.findall(r'^## '+SECTION+r'\n(.*?)(?=^## |\Z)', (ROOT / SPEC).read_text(), re.M | re.S)
    prose = ' '.join(section.split())
    for phrase in (THIS_TEST, OWNER_TEST, STOCK_TEST, '22', '23', '24', '25',
                   'incoming R6', '0..65535', 'no RAM readback', 'Q', 'G',
                   'whole-word retention', 'physical', 'outside'):
        assert phrase in prose
    verify_published_execution_counts(section)


def test_ignition_event_arithmetic_registered_stock_contract():
    data = derive.image_bytes(repo.layout('7mfk'))
    PUBLICATION.verify_event_publication_stock(data)
    RETARD.verify_event_retard_stock(data)
    PUBLICATION.test_knock_event_publication_registered_stock_contract()
    RETARD.test_knock_event_retard_registered_stock_contract()
    assert (PUBLICATION._region().cases, RETARD._region().cases) == (8754, 7408)


@pytest.mark.parametrize('region_index', (0, 1))
@pytest.mark.parametrize('field_index', (0, 1, 2))
def test_ignition_shared_document_counts_refuse_stale_values(region_index, field_index):
    values = []
    for accepted in (PUBLICATION, RETARD):
        region = accepted._region()
        values.append([sum(end-start for start, end in region.code_spans)//2,
                       sum(end-start for start, end in region.code_spans)+
                       sum(size for address, size in region.pools), region.cases])
    text = '\n'.join(f'{n} instructions / {b} bytes / {c} cases' for n, b, c in values)
    verify_published_execution_counts(text)
    values[region_index][field_index] += 1
    stale = '\n'.join(f'{n} instructions / {b} bytes / {c} cases' for n, b, c in values)
    with pytest.raises(AssertionError):
        verify_published_execution_counts(stale)


def test_ignition_event_arithmetic_proposed_notes_preserve_all_other_step_fields():
    original = _steps()
    proposed = deepcopy(original)
    for index, expected in EXPECTED.items():
        proposed[index]['note'] = expected[4]
    verify_ignition_event_steps(proposed)
    assert all({key: value for key, value in new.items() if key != 'note'} ==
               {key: value for key, value in old.items() if key != 'note'}
               for old, new in zip(original, proposed))
    assert all(proposed[index] == original[index] for index in range(34) if index not in EXPECTED)


@pytest.mark.parametrize('index', tuple(EXPECTED))
@pytest.mark.parametrize('field', ('from', 'to', 'effect', 'sign', 'via', 'note', 'r6_domain', 'retention'))
def test_ignition_event_arithmetic_contract_refuses_unbound_mutations(index, field):
    steps = deepcopy(_steps())
    for at, expected in EXPECTED.items():
        steps[at]['note'] = expected[4]
    if field == 'from':
        steps[index][field] = SymbolKey('7mfk', 'ram', 0xffff1ff6)
    elif field == 'to':
        steps[index][field] = SymbolKey('7mfk', 'ram', 0xffff11d8)
    elif field == 'effect':
        steps[index][field] = 'copies'
    elif field == 'sign':
        steps[index][field] = 'none'
    elif field == 'via':
        steps[index][field] = [SymbolKey('7mfk', 'fn', 0x62e10)]
    elif field == 'r6_domain':
        steps[index]['note'] = steps[index]['note'].replace('P = x', 'P = uint8(x)') if index < 23 else steps[index]['note'].replace('uint16(ffff23c2)', 'uint8(ffff23c2)')
    elif field == 'retention':
        steps[index]['note'] = steps[index]['note'].replace('ffff1ff8+int8', 'int16(ffff1ff8)+int8') if index < 23 else steps[index]['note'].replace('uint16(ffff11d8)', 'int8(ffff11d8)')
    else:
        steps[index][field] += '; ffff11d6 = 0'
    with pytest.raises(AssertionError):
        verify_ignition_event_steps(steps)
