"""Exact TEST owning routes and live semantic-context refusal contracts."""

from dataclasses import replace

import pytest

from kb import test_origins as origins
from kb.model import Link, Meaning, Model, Symbol, SymbolKey


@pytest.fixture
def native_origins():
    evidence = {'kind': 'test', 'path': 'tools/kb/tests/test_origin_probe.py',
                'key': 'test_raw_observation'}
    owner = Meaning('ram', 'observed_value', props={'level': 'code'})
    symbol = Symbol(SymbolKey('7mfk', 'ram', 0xffff1000),
                    props={'width': 8, 'signed': False}, evidence=[dict(evidence)],
                    implicit=False, meaning=owner)
    owner.symbols['7mfk'] = symbol
    function = Meaning('fn', 'observation_publisher', props={'level': 'code'})
    entry = Symbol(SymbolKey('7mfk', 'fn', 0x30000), meaning=function)
    function.symbols['7mfk'] = entry
    link = Link(owner, 'reader', function, None, None,
                props={'layouts': ['7mfk'], 'relies': 'structure'},
                evidence=[dict(evidence)])
    owner.links.append(link)
    model = Model({}, {symbol.key: symbol, entry.key: entry}, {}, {}, [])
    model.meanings = [owner, function]
    model.links = [link]
    return model, symbol, link, evidence


def test_same_selector_has_separate_symbol_and_relation_origins(native_origins):
    model, symbol, link, evidence = native_origins
    symbol_origin = origins.symbol_attachment(model, symbol, 0)
    link_origin = origins.link_attachment(model, link, 0)
    assert symbol_origin.key != link_origin.key
    assert symbol_origin.explicit_support is None
    assert link_origin.explicit_support is None
    assert origins.current(model, symbol_origin, evidence) == symbol_origin
    assert origins.current(model, link_origin, evidence) == link_origin


def test_model_change_invalidates_context_without_changing_attachment_identity(native_origins):
    model, symbol, _, evidence = native_origins
    original = origins.symbol_attachment(model, symbol, 0)
    symbol.props['width'] = 16
    current = origins.symbol_attachment(model, symbol, 0)
    assert original.key == current.key
    assert original.context_digest != current.context_digest
    with pytest.raises(ValueError, match='context changed'):
        origins.current(model, original, evidence)


def test_global_relation_order_does_not_replace_its_owning_identity(native_origins):
    model, symbol, link, evidence = native_origins
    original = origins.link_attachment(model, link, 0)
    other = Link(link.owner, 'writer', link.to, None, None)
    model.links.insert(0, other)
    symbol.meaning.links.insert(0, other)
    assert origins.current(model, original, evidence) == original
    link.props['layouts'] = ['1nd']
    with pytest.raises(ValueError, match='context changed'):
        origins.current(model, original, evidence)


def test_nested_bit_context_preserves_its_actual_owner_fields(native_origins):
    model, symbol, _, evidence = native_origins
    owner = symbol.meaning
    owner.props['bit'] = [{'name': 'valid', 'bit': 0, 'level': 'code',
                           'evidence': [dict(evidence)]}]
    origin = origins.capture(model, ('meaning', owner.key, 'properties',
                                     'bit', 0, 'evidence', 0))
    assert isinstance(origin, origins.Origin)
    owner.props['bit'][0]['bit'] = 1
    with pytest.raises(ValueError, match='context changed'):
        origins.current(model, origin, evidence)


def test_failed_origin_capture_is_not_a_missing_optional_argument(native_origins):
    model, symbol, _, evidence = native_origins
    unavailable = origins.capture(model, ('symbol', symbol.key.key, 'evidence', 1))
    assert isinstance(unavailable, origins.Unavailable)
    assert unavailable is not None
    with pytest.raises(ValueError, match='explicit owning origin'):
        origins.current(model, unavailable, evidence)


def test_returned_packets_cannot_mutate_retained_typed_context(native_origins):
    model, symbol, _, evidence = native_origins
    origin = origins.symbol_attachment(model, symbol, 0)
    expected = origin.packet()
    changed = origin.packet()
    changed['context'].clear()
    changed['locator'].append('different-owner')
    assert origin.packet() == expected
    assert origins.current(model, origin, evidence) == origin
    with pytest.raises(ValueError, match='context changed'):
        origins.current(model, replace(origin, kind='link'), evidence)


@pytest.mark.parametrize('wrong_index', [False, True, -1, 1, 0.0])
def test_evidence_position_requires_its_exact_integer(native_origins, wrong_index):
    model, symbol, _, _ = native_origins
    with pytest.raises(ValueError, match='evidence position'):
        origins.symbol_attachment(model, symbol, wrong_index)
