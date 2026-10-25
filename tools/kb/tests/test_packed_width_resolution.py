"""Exact width resolution refuses unqualified execution and preserves questions."""

import json
from copy import deepcopy
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from kb import packed_width, reconciliation, repo
from kb.model import SymbolKey


@pytest.mark.parametrize('fault', ('missing', 'stale', 'failed', 'unrelated', 'changed-width', 'changed-site'))
def test_a_failed_live_contract_cannot_suppress_a_raw_width_question(fault):
    storage = SimpleNamespace(key=SymbolKey('1me3b', 'ram', 0xFFFE81B4), layout='1me3b',
        kind='ram', sources={'controlled-field.toml'}, value=lambda name:8 if name == 'width' else None)
    subject = SimpleNamespace(root=repo.ROOT, symbols={storage.key:storage}, links=[],
        layouts={'1me3b':SimpleNamespace(mcu='SH7059')}, spaces={'SH7059':{}})
    site = dict(site=0x21344, mode='read', width=4)
    source = ({}, {storage.key.location:[('1me3b:00021240', site)]})
    with patch.object(reconciliation, 'accesses', return_value=source), \
         patch.object(reconciliation.match, 'l0_digest', return_value='28a4e19998ef4d2c'), \
         patch.object(packed_width, 'require', side_effect=ValueError(fault)):
        difference = reconciliation.differences(subject)
        raw = reconciliation.differences(subject, width_proofs=False)
    assert difference == raw
    assert len(raw) == 1 and raw[0]['kind'] == 'width'
    assert storage.value('width') == 8


@pytest.mark.parametrize('field', ('symbol', 'width', 'observed'))
def test_width_claim_requires_the_exact_declared_question(field):
    descriptor = packed_width.contract.descriptor(repo.ROOT)
    row = descriptor['field'][0]
    location, kind = row['symbol'].split('/')
    layout, address = location.rsplit('-', 1)
    symbol = SimpleNamespace(key=SymbolKey(layout, kind, int(address, 16)))
    model = SimpleNamespace(root=repo.ROOT, symbols={symbol.key:symbol})
    expected = dict(symbol=row['symbol'], width=row['declared_bits'],
        observed=sorted((entry['function'], entry['site'], entry['mode'], entry['width_bytes'])
                        for entry in row['observed']))
    altered = deepcopy(expected)
    if field == 'symbol':
        altered[field] = '1nd-fffe81cc/ram'
    elif field == 'width':
        altered[field] = 32
    else:
        altered[field] = altered[field][:-1]
    # Only native binding is controlled here. No physical proof can be reached
    # before the changed question is rejected.
    record = {'candidate':{'witness':{'packed_transfers':{key:{} for key in packed_width.contract.LAYOUTS}}}}
    with patch.object(packed_width.contract, 'bind_field', return_value=symbol), \
         patch.object(packed_width.ignition_literal_evidence, 'require_original',
                      side_effect=AssertionError('an unrelated claim reaches physical execution')):
        with pytest.raises(ValueError):
            packed_width.require(model, symbol, altered, record=record)


def test_record_without_packed_originals_is_not_an_explanation():
    descriptor = packed_width.contract.descriptor(repo.ROOT)
    row = descriptor['field'][0]
    location, kind = row['symbol'].split('/')
    layout, address = location.rsplit('-', 1)
    symbol = SimpleNamespace(key=SymbolKey(layout, kind, int(address, 16)))
    model = SimpleNamespace(root=repo.ROOT, symbols={symbol.key:symbol})
    with pytest.raises(ValueError, match='exact complete original layout set'):
        packed_width.require(model, symbol, {}, record={'candidate':{'witness':{}}})
