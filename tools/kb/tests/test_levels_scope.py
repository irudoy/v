"""Selected subjects retain full-model preparation and exact failure reports."""

from copy import deepcopy
from unittest import mock

import pytest

from kb import checks, compile, levels, match, repo
from kb.model import Status, SymbolKey
from tools.kb.tests import test_homology_scope as homology
from tools.kb.tests.test_levels import DID, ENTRY, L0, RAM, SOURCE, datum, function, model_of


def subject(model, address, layout='7mfk', kind='ram'):
    return checks._subject(model.symbols[SymbolKey(layout, kind, address)].meaning)


def filtered(model, subjects):
    full = levels.check(model)
    selected = levels.check(model, subjects=subjects)
    assert selected == [issue for issue in full if issue.subject in subjects]
    return selected


def chain_model(route='forward', cycle=False):
    def declare(builder):
        first = datum(builder, RAM, 'code')
        second = datum(builder, RAM + 2, 'code')
        third = datum(builder, RAM + 4, 'candidate', evidence=())
        if route == 'trace':
            builder.symbols[first].evidence.append(
                {'kind': 'trace', 'relies': 'level', 'to': second})
        elif route == 'reverse':
            builder.link(second, 'input', first, 'fixture', props={'reverse_relies': 'level'})
        else:
            builder.link(first, 'input', second, 'fixture', props={'relies': 'level'})
        builder.link(second, 'input', third, 'fixture', props={'relies': 'level'})
        if cycle:
            builder.link(second, 'input', first, 'fixture', props={'relies': 'level'})
    return model_of(declare)


def test_default_and_mandatory_gate_keep_the_complete_result():
    model = chain_model()
    full = levels.check(model)
    assert full and any('chain ends at' in issue.message for issue in full)
    assert levels.check(model, subjects=None) == full
    assert checks.CHECKS['levels'](model) == full
    assert checks.audit(model, ('levels',))['levels'] == full


def test_empty_and_missing_subjects_keep_complete_preparation():
    model = chain_model()
    for subjects in (set(), (), {'missing/ram'}):
        with mock.patch.object(levels, '_Collector', wraps=levels._Collector) as collected, \
                mock.patch.object(levels, 'hardware', wraps=levels.hardware) as hardware:
            assert filtered(model, subjects) == []
        assert collected.call_count == hardware.call_count == 2


@pytest.mark.parametrize('route', ('forward', 'reverse', 'trace'))
@pytest.mark.parametrize('cycle', (False, True))
def test_external_multi_hop_donors_and_cycles_preserve_causes(route, cycle):
    model = chain_model(route, cycle)
    selected = filtered(model, {subject(model, RAM)})
    assert any('chain ends at' in issue.message and 'candidate' in issue.message
               for issue in selected)
    analysis = levels.analyze(model, subjects={subject(model, RAM)})
    assert {claim.subject for claim in analysis.claims} == {
        subject(model, RAM + offset) for offset in (0, 2, 4)}


@pytest.mark.parametrize('route', ('forward', 'reverse'))
def test_external_symbol_claim_has_priority_over_meaning_claim(route):
    def declare(builder):
        owner = datum(builder, RAM, 'code', layout='jk00d')
        donor = datum(builder, RAM + 2, 'code')
        builder.symbol('jk00d', 'ram', RAM + 4, 'fixture', group=('ram', RAM + 2),
                       props={'level': 'candidate'}, evidence=[deepcopy(L0)])
        builder.link(owner if route == 'forward' else donor, 'input',
                     donor if route == 'forward' else owner, 'fixture',
                     props={('relies' if route == 'forward' else 'reverse_relies'): 'level'})
    model = model_of(declare)
    selected = filtered(model, {subject(model, RAM, 'jk00d')})
    assert any('candidate' in issue.message for issue in selected)


def test_missing_external_claim_retains_the_exact_failure():
    def declare(builder):
        owner = datum(builder, RAM, 'code')
        donor = datum(builder, RAM + 2, None)
        builder.link(owner, 'input', donor, 'fixture', props={'relies': 'scale'})
    model = model_of(declare)
    selected = filtered(model, {subject(model, RAM)})
    assert any('declares no scale_level' in issue.message for issue in selected)


def test_equal_dependency_bounds_preserve_original_explanation_order():
    def declare(builder):
        owner = datum(builder, RAM, 'code')
        for offset in (2, 4):
            donor = datum(builder, RAM + offset, 'candidate', evidence=())
            builder.link(owner, 'input', donor, 'fixture', props={'relies': 'level'})
    model = model_of(declare)
    subjects = {subject(model, RAM)}
    first = filtered(model, subjects)
    model.links.reverse()
    second = filtered(model, subjects)
    assert first != second


@pytest.mark.parametrize('present', (True, False))
def test_external_did_structure_remains_in_complete_preparation(present):
    def declare(builder):
        owner = function(builder, ENTRY)
        donor = datum(builder, SOURCE, 'code')
        builder.link(owner, 'reader', donor, 'fixture', props={'relies': 'structure'})
        if present:
            did = builder.symbol('7mfk', 'did', DID, 'fixture', group=('did', DID), evidence=[{
                'kind': 'did-table', 'at': f'7mfk:{DID:08x}', 'value': f'{SOURCE:08x}'}])
            builder.link(did, 'source', donor, 'fixture', props={'offset': 0})
    model = model_of(declare)
    selected = filtered(model, {subject(model, ENTRY, kind='fn')})
    assert bool(selected) is not present


@pytest.mark.parametrize('broken', (False, True))
def test_identity_selection_retains_external_homology_donors(broken):
    model = homology.controlled_model()
    owner, donor = model.symbols[homology.OWNER], model.symbols[homology.DONOR]
    owner.meaning.props['level'] = 'code'
    if broken:
        donor.evidence = []
    selected = filtered(model, {owner.key.key})
    assert bool(selected) is broken
    analysis = levels.analyze(model, subjects={owner.key.key})
    assert any(claim.symbol is owner for claim in analysis.claims)


@pytest.mark.parametrize('kind,bad,good', (
    ('arithmetic', '1=2', '1=1'),
    ('hardware', 'scope.missing', 'immo.developer_flag'),
))
def test_shared_failed_items_are_checked_globally_after_each_mutation(kind, bad, good):
    def declare(builder):
        datum(builder, RAM, 'code', evidence=())
        datum(builder, RAM + 2, 'code', evidence=())
    model = model_of(declare)
    selected = model.symbols[SymbolKey('7mfk', 'ram', RAM)]
    other = model.symbols[SymbolKey('7mfk', 'ram', RAM + 2)]
    field = 'value' if kind == 'arithmetic' else 'key'
    item = {'kind': kind, field: bad}
    selected.evidence = other.evidence = [item]
    subjects = {checks._subject(selected.meaning)}
    for value, broken in ((bad, True), (good, False), (bad, True)):
        item[field] = value
        issues = filtered(model, subjects)
        assert any('lacks grounding' in issue.message for issue in issues) is broken
        assert selected.evidence[0] is other.evidence[0] is item


@pytest.mark.parametrize('place', ('bit', 'value', 'diagnostic', 'status', 'link'))
def test_selected_standalone_failure_without_a_claim_remains_visible(place):
    def declare(builder):
        first, second = datum(builder, RAM, None), datum(builder, RAM + 2, None)
        if place == 'link':
            builder.link(first, 'input', second, 'fixture',
                         evidence=[{'kind': 'arithmetic', 'value': '1=2'}])
    model = model_of(declare)
    meaning = model.symbols[SymbolKey('7mfk', 'ram', RAM)].meaning
    owner = checks._subject(meaning)
    item = {'kind': 'arithmetic', 'value': '1=2'}
    if place in ('bit', 'value'):
        meaning.props[place] = [{'name': 'probe', 'evidence': [item]}]
        wanted = f'{owner} {place} probe'
    elif place == 'diagnostic':
        meaning.tables['diagnostic'] = [{'id': 'probe', 'evidence': [item]}]
        wanted = f'{owner} diagnostic probe'
    elif place == 'status':
        meaning.statuses['jk00d'] = Status('jk00d', 'absent', evidence=[item])
        wanted = f'{owner} on jk00d'
    else:
        wanted = f'{owner} input link'
    assert not levels.analyze(model).claims
    selected = filtered(model, {wanted})
    assert len(selected) == 1 and 'arithmetic evidence' in selected[0].message


@pytest.fixture(scope='module')
def native_model():
    return compile.build(repo.ROOT)


@pytest.mark.slow
def test_native_selected_positive_negative_and_restored_results_match(native_model):
    symbol = next(symbol for symbol in native_model.symbols.values()
                  if symbol.meaning.key == 'vvel_command_shaft_angle/tbl')
    meaning = symbol.meaning
    subjects = {meaning.key}
    originals = {key: symbol.evidence for key, symbol in meaning.symbols.items()}
    before = filtered(native_model, subjects)
    assert not any('scale' in issue.message for issue in before)
    try:
        for symbol in meaning.symbols.values():
            symbol.evidence = [item for item in symbol.evidence
                               if item.get('supports') != 'scale']
        broken = filtered(native_model, subjects)
        assert broken != before and any('scale level candidate lacks evidence' in issue.message
                                        for issue in broken)
    finally:
        for key, symbol in meaning.symbols.items():
            symbol.evidence = originals[key]
    assert filtered(native_model, subjects) == before
