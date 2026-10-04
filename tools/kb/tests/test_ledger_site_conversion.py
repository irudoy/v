"""A ledger terminal preserves its selected and independently checked context."""

import copy
from types import SimpleNamespace
from unittest import mock

import pytest

from kb import convert, tokens
from kb.model import SymbolKey
from kb.repo import KbError


def fixture():
    item = {'kind': 'l0-context', 'supports': 'identity', 'at': '7mfk:00028ea2',
            'key': 'body', 'value': {'span': 1, 'named': ['fffff434']}}
    document = {'symbol': [{'evidence': [item]}],
                'ledger': [{'registry': 'funcs', 'identity': [0]}]}
    symbol = SimpleNamespace(layout='7mfk', meaning=object(),
                             key=SimpleNamespace(key='7mfk-00028ea2/fn'))
    conversion = object.__new__(convert.Conversion)
    conversion.before = object()
    conversion._document = lambda meaning: document
    conversion._entry = lambda document, symbol: document['symbol'][0]
    return conversion, symbol, document, item, tokens.parse('site:00028ea2')[0]


def test_selected_context_survives_a_terminal_that_omits_its_footprint():
    conversion, symbol, document, item, token = fixture()
    before = copy.deepcopy(document)
    with mock.patch('kb.ledger_projection.match.verify', return_value=None) as checked:
        held = conversion._ledger_site(symbol, 'funcs', token, 'identity')
    assert held == item and held is not item
    assert held['value']['named'] == ['fffff434']
    checked.assert_called_once_with(conversion.before, symbol, item)
    assert document == before


def test_a_stale_selected_context_is_refused():
    conversion, symbol, _, _, token = fixture()
    with mock.patch('kb.ledger_projection.match.verify', return_value='missing reference'):
        with pytest.raises(KbError, match='missing reference') as refused:
            conversion._ledger_site(symbol, 'funcs', token, 'identity')
    assert refused.value.code == 3


@pytest.mark.parametrize('change', ['registry', 'site', 'supports'])
def test_an_unselected_terminal_uses_normal_classification(change):
    conversion, symbol, document, item, token = fixture()
    if change == 'registry':
        document['ledger'][0]['registry'] = 'vars'
    elif change == 'site':
        item['at'] = '7mfk:00028ea4'
    else:
        item['supports'] = 'scale'
    with mock.patch('kb.ledger_projection.match.verify') as checked:
        assert conversion._ledger_site(symbol, 'funcs', token, 'identity') is None
    checked.assert_not_called()


def test_distinct_contexts_with_the_same_terminal_are_ambiguous():
    conversion, symbol, document, item, token = fixture()
    other = copy.deepcopy(item)
    other['value']['named'] = ['fffff456']
    document['symbol'][0]['evidence'].append(other)
    document['ledger'][0]['identity'].append(1)
    with pytest.raises(KbError, match='ambiguous held ledger site'):
        conversion._ledger_site(symbol, 'funcs', token, 'identity')


def test_ledger_call_references_preserve_the_selected_layout():
    home = SymbolKey('7mfk', 'fn', 0x2c648)
    other = SymbolKey('jk00d', 'fn', 0x3c648)
    meaning = SimpleNamespace(key='probe/fn', home='7mfk')
    conversion = object.__new__(convert.Conversion)
    conversion.before = SimpleNamespace(symbols={
        home: SimpleNamespace(meaning=meaning, layout='7mfk'),
        other: SimpleNamespace(meaning=meaning, layout='jk00d')})
    assert conversion._ledger_reference(home) == 'probe/fn'
    assert conversion._ledger_reference(other) == 'probe/fn/jk00d'


def test_a_ledger_call_reference_without_a_meaning_is_refused():
    conversion = object.__new__(convert.Conversion)
    conversion.before = SimpleNamespace(symbols={})
    with pytest.raises(KbError, match='names no meaning'):
        conversion._ledger_reference(SymbolKey('7mfk', 'fn', 0x2c648))


def test_test_evidence_retains_its_required_file_path():
    item = {'kind': 'test', 'path': 'tools/kb/tests/test_airflow_adc.py',
            'key': 'test_maf_adc_unsigned_word_sources_and_shifts_match_stock',
            'to': SymbolKey('7mfk', 'ram', 0xffff1d62),
            'legacy': 'test:stock_adc'}
    before = dict(item)
    assert convert._location(item) == {
        'kind': 'test', 'path': 'tools/kb/tests/test_airflow_adc.py',
        'key': 'test_maf_adc_unsigned_word_sources_and_shifts_match_stock',
        'to': '7mfk:ffff1d62'}
    assert item == before


def test_registry_origin_metadata_stays_out_of_owned_evidence():
    item = {'kind': 'l0', 'at': '7mfk:000280b6',
            'path': 'defs/JK08A.vars.csv', 'legacy': 'site:000280b6'}
    assert convert._location(item) == {'kind': 'l0', 'at': '7mfk:000280b6'}
