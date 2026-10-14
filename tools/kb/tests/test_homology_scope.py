"""Exact subject queries retain full-model terminals and donor dependencies."""
from copy import deepcopy
import hashlib
from unittest import mock

import pytest

from kb import checks, compile, match, repo
from kb.model import Issue, SymbolKey
from tools.kb.tests import test_match as support
from tools.kb.tests import writer_sources

THIS_TEST = 'tools/kb/tests/test_homology_scope.py'
MISSING = {'kind': 'test', 'path': THIS_TEST, 'key': 'test_missing_scoped_terminal'}
DONOR = SymbolKey('7mfk', 'ram', support.APC_7MFK)
OWNER = SymbolKey('jk00d', 'ram', support.APC_JK00D)
EDGE = {'kind': 'masked-match', 'supports': 'homology',
        'at': f'jk00d:{support.APC_MATCH:08x}',
        'to': f'7mfk:{support.APC_REGION:08x}', 'count': 1, 'value': 14}
ANCHOR = {'kind': 'l0', 'supports': 'identity', 'at': f'7mfk:{support.APC_STORE:08x}'}


def controlled_model():
    def declare(builder):
        builder.symbol('7mfk', 'ram', support.APC_7MFK, 'kb/ram/donor.toml',
                       group=('ram', 'chain'), evidence=[deepcopy(ANCHOR)])
        builder.symbol('jk00d', 'ram', support.APC_JK00D, 'kb/ram/owner.toml',
                       group=('ram', 'chain'), evidence=[deepcopy(EDGE)])
        builder.symbol('7mfk', 'ram', support.INJECTION, 'fixture.csv', evidence=[deepcopy(MISSING)])
    return support.model_of(declare)


def filtered(model, subjects):
    full = checks.homology(model)
    selected = checks.homology(model, subjects=subjects)
    assert selected == [issue for issue in full if issue.subject in subjects]
    return selected


def test_default_full_retains_complete_issue_records_and_order():
    model = controlled_model()
    symbol = model.symbols[SymbolKey('7mfk', 'ram', support.INJECTION)]
    failure = match.verify(model, symbol, MISSING)
    assert failure and not checks._owned(model, symbol)
    expected = [Issue('homology', 'fixture.csv', symbol.key.key,
                      f'{checks._item(MISSING)}: {failure}')]
    assert checks.homology(model) == expected
    assert checks.homology(model, subjects=None) == expected
    assert checks.CHECKS['homology'](model) == expected


def test_empty_selection_performs_no_verification():
    model = controlled_model()
    with mock.patch.object(match, 'verify', side_effect=AssertionError('verify called')), \
            mock.patch.object(match, 'grounded', side_effect=AssertionError('grounded called')):
        assert checks.homology(model, subjects=set()) == []
        assert checks.homology(model, subjects=()) == []


@pytest.mark.parametrize('terminal', (
    MISSING,
    {'kind': 'l0-context', 'at': 'not-a-location', 'key': 'reference', 'value': {'span': 1}},
    {'kind': 'indirect', 'mode': 'base', 'at': 'not-a-location', 'value': 2},
))
def test_selected_non_owned_symbol_retains_explicit_terminal_errors(terminal):
    model = controlled_model()
    symbol = model.symbols[SymbolKey('7mfk', 'ram', support.INJECTION)]
    symbol.evidence = [deepcopy(terminal)]
    assert not checks._owned(model, symbol)
    issues = filtered(model, {symbol.key.key})
    assert len(issues) == 1
    assert issues[0].check == 'homology' and issues[0].path == 'fixture.csv'
    assert match.verify(model, symbol, terminal) in issues[0].message


def test_owned_subject_follows_an_unselected_broken_external_donor():
    model = controlled_model()
    owner, donor = model.symbols[OWNER], model.symbols[DONOR]
    assert filtered(model, {owner.key.key}) == []
    donor.evidence = []
    with mock.patch.object(match, '_anchor', wraps=match._anchor) as anchors:
        selected = checks.homology(model, subjects={owner.key.key})
    assert any(call.args[1] is donor for call in anchors.call_args_list)
    assert selected == [i for i in checks.homology(model) if i.subject == owner.key.key]
    assert len(selected) == 1 and 'neither an anchor nor homologous' in selected[0].message


def test_unanchored_homology_cycle_matches_the_complete_result():
    model = controlled_model()
    model.symbols[DONOR].evidence = [{**EDGE,
        'at': f'7mfk:{support.APC_REGION:08x}', 'to': f'jk00d:{support.APC_MATCH:08x}'}]
    assert match.verify(model, model.symbols[DONOR], model.symbols[DONOR].evidence[0]) is None
    issues = filtered(model, {OWNER.key, DONOR.key})
    assert len(issues) == 2 and all('neither an anchor nor homologous' in i.message for i in issues)


@pytest.mark.parametrize('terminal_state', ('missing-anchor', 'invalid-terminal'))
def test_two_unselected_donors_remain_in_the_grounding_closure(tmp_path, terminal_state):
    writer_sources.write_sources(tmp_path)
    builder = support.Builder(repo.layouts(tmp_path), compile.spaces(repo.config(tmp_path)), {}, {})
    digest = hashlib.sha256(b'\0').hexdigest()
    keys = [SymbolKey(layout, 'tbl', address) for layout, address in
            (('jk00d', 0x300), ('jk00c', 0x200), ('7mfk', 0x100))]
    for index, key in enumerate(keys):
        evidence = []
        if index < 2:
            evidence = [{'kind': 'byte-identical', 'supports': 'homology',
                         'at': key.location, 'to': keys[index + 1].location, 'sha256': digest}]
        elif terminal_state == 'invalid-terminal':
            evidence = [deepcopy(MISSING)]
        builder.symbol(key.layout, key.kind, key.address,
                       'kb/tbl/chain.toml' if index == 0 else 'fixture.csv',
                       group=('tbl', 'chain'), props={'storage': 'uint8', 'cols': 1, 'rows': 1},
                       evidence=evidence)
    model = builder.finish()
    model.root, model.config = tmp_path, repo.config(tmp_path)
    owner, middle, terminal = (model.symbols[key] for key in keys)
    assert checks._owned(model, owner) and not checks._owned(model, middle)
    assert not checks._owned(model, terminal)
    assert match.verify(model, owner, owner.evidence[0]) is None
    assert match.verify(model, middle, middle.evidence[0]) is None
    with mock.patch.object(match, '_anchor', wraps=match._anchor) as anchors:
        issues = checks.homology(model, subjects={owner.key.key})
    assert {call.args[1].key for call in anchors.call_args_list} == set(keys)
    assert issues == [i for i in checks.homology(model) if i.subject == owner.key.key]
    assert len(issues) == 1 and 'neither an anchor nor homologous' in issues[0].message


def test_bit_subjects_and_symbol_subjects_preserve_full_order():
    model = controlled_model()
    donor = model.symbols[DONOR]
    donor.meaning.props['bit'] = [{'name': 'held', 'bit': 0,
                                 'evidence': [{**MISSING, 'at': DONOR.location}]}]
    donor.props['bit'] = [{'name': 'active', 'bit': 1,
                          'evidence': [{**MISSING, 'at': DONOR.location}]}]
    donor.evidence = []
    full = checks.homology(model)
    assert any(' bit held' in i.subject for i in full)
    assert any(' bit active' in i.subject for i in full)
    subjects = {i.subject for i in full}
    assert checks.homology(model, subjects=subjects) == full
    for subject in subjects:
        filtered(model, {subject})
    assert checks.homology(model, subjects={'missing/ram'}) == []


@pytest.fixture(scope='module')
def native_model():
    return compile.build(repo.ROOT)


def test_same_complete_native_model_retains_non_owned_terminal_failure(native_model):
    symbol = next(s for s in native_model.symbols.values() if not checks._owned(native_model, s))
    original = symbol.evidence
    try:
        symbol.evidence = [deepcopy(MISSING)]
        issues = filtered(native_model, {symbol.key.key})
        assert len(issues) == 1 and 'defines no function' in issues[0].message
    finally:
        symbol.evidence = original


def test_same_complete_native_model_retains_external_donor_failure(native_model):
    owner, donor = native_model.symbols[OWNER], native_model.symbols[DONOR]
    before = owner.evidence, donor.evidence
    try:
        owner.evidence, donor.evidence = [deepcopy(EDGE)], [deepcopy(ANCHOR)]
        assert filtered(native_model, {OWNER.key}) == []
        donor.evidence = []
        issues = filtered(native_model, {OWNER.key})
        assert len(issues) == 1 and 'neither an anchor nor homologous' in issues[0].message
    finally:
        owner.evidence, donor.evidence = before
