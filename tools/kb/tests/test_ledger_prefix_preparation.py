"""Terminal recognition reads current manual prefixes only when requested."""

from types import SimpleNamespace
from unittest import mock

import pytest

from kb import convert, repo, tokens


def conversion():
    result = convert.Conversion.__new__(convert.Conversion)
    result.root = repo.ROOT
    return result


@pytest.mark.parametrize('text', ['registry:defs/source.csv',
                                 'test:tools/kb/tests/test_convert.py#check',
                                 'spec:hardware-results:immo.developer_flag',
                                 'spec:1*2=2'])
def test_terminals_without_manual_names_keep_evidence_without_reading_prefixes(text):
    converter = conversion()
    [token] = tokens.parse(text)
    symbol = SimpleNamespace(layout='7mfk')
    expected = tokens.evidence(token, symbol.layout, ('manual-',))
    with mock.patch.object(repo, 'config', side_effect=AssertionError('unused prefixes read')):
        item, raw = converter._ledger_item(symbol, 'dtc', {}, token)
    assert item == raw == expected


def test_each_manual_recognition_reads_current_prefixes():
    converter = conversion()
    [token] = tokens.parse('spec:manual-probe')
    symbol = SimpleNamespace(layout='7mfk')
    with mock.patch.object(repo, 'config', side_effect=[
            {'tokens': {'manual': ['manual-']}}, {'tokens': {'manual': ['other-']}}]) as reader:
        first, _ = converter._ledger_item(symbol, 'dtc', {}, token)
        second, _ = converter._ledger_item(symbol, 'dtc', {}, token)
    assert reader.call_count == 2
    assert first == {'kind': 'manual', 'key': 'manual-probe'}
    assert second == {'kind': 'spec', 'key': 'manual-probe'}


def test_manual_recognition_preserves_current_configuration_refusals():
    converter = conversion()
    [token] = tokens.parse('spec:manual-probe')
    with mock.patch.object(repo, 'config', side_effect=repo.KbError('invalid owner schema')):
        with pytest.raises(repo.KbError, match='invalid owner schema'):
            converter._ledger_item(SimpleNamespace(layout='7mfk'), 'dtc', {}, token)
