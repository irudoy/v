"""One exact bank1 RAM reader append preserves full native owner and function facts."""
from copy import deepcopy
import json
import pytest
from kb import repo
from kb import rest_position_judgement_access_contract as contract


def row():
    return contract.descriptor(repo.ROOT)['reference'][0]


def test_exact_RAM_reader_append_preserves_all_native_facts_and_unset_types():
    selected = row()
    before, after = (json.loads(selected[which + '_native_json']) for which in ('original', 'proposed'))
    stripped = deepcopy(after)
    target, = [r for r in stripped['link'] if (r['type'], r['to']) == ('reader', 'apricot-echidna/fn')]
    original, = [r for r in before['link'] if (r['type'], r['to']) == ('reader', 'apricot-echidna/fn')]
    assert target['evidence'].pop() == contract.item(selected)
    if not target['evidence'] and 'evidence' not in original:
        target.pop('evidence')
    assert stripped == before and target['relies'] == 'structure'
    assert contract.symbol_key(selected).kind == 'ram'
    assert selected['address'] == 0xFFFF16BB and selected['width_bytes'] == 1
    symbol, = [r for r in after['symbol'] if r['layout'] == '7mfk']
    assert symbol['address'] == 'ffff16bb' and 'width' not in symbol and 'signed' not in symbol
    assert selected['original_ledger_json'] == selected['proposed_ledger_json']
    assert 'bank index 1' in after['summary'] and after['note'] == before['note']
    assert [(r['owner'], r['address']) for r in contract.DECLARED['retained_functions']] == [('apricot-echidna/fn', 0x90256)]
    evidence = contract.item(selected)['value']
    assert evidence['native_index_premise'] == dict(register=4, complete_raw_value=1)
    assert evidence['actual_reads'] == [dict(site=0x9030C, address=0xFFFF16BB, width_bytes=1),
        dict(site=0x903AA, address=0xFFFF16BB, width_bytes=1)]
    assert evidence['scope'] == 'exact-rest-position-judgement'
    for key in ('native_geometry_inference', 'scale_admission', 'units_admission',
            'native_bank_general_identity_admission', 'natural_scheduling_inference', 'hardware_qualification'):
        assert evidence[key] is False


@pytest.mark.parametrize('fault', ('duplicate', 'other-owner', 'other-function', 'other-bank', 'wide-access', 'scale', 'forged-original'))
def test_normal_writer_requires_only_the_exact_complete_single_reader_append(fault):
    selected = row()
    operation = contract.operation(selected)
    assert contract.operations([deepcopy(operation)], repo.ROOT) is True
    changed = deepcopy(operation)
    if fault == 'duplicate':
        operations = [changed, deepcopy(changed)]
    else:
        if fault == 'other-owner':
            changed['meaning'] = 'other-byte/ram'
        elif fault == 'other-function':
            changed['to'] = 'other-judgement/fn'
        elif fault == 'other-bank':
            changed['evidence'][0]['value']['native_index_premise']['complete_raw_value'] = 0
        elif fault == 'wide-access':
            changed['evidence'][0]['value']['width_bytes'] = 2
        elif fault == 'scale':
            changed['evidence'][0]['supports'] = 'scale'
        else:
            changed['evidence'][0]['value']['original_claim_sha256'] = '0' * 64
        operations = [changed]
    with pytest.raises(ValueError):
        contract.operations(operations, repo.ROOT)


@pytest.mark.parametrize('fault', ('owner-summary', 'source-note', 'writer-link', 'semantic-width', 'function-summary'))
def test_full_preimages_refuse_partial_owner_or_function_substitutes(monkeypatch, fault):
    document = deepcopy(contract.DECLARED)
    selected = document['reference'][0]
    if fault == 'function-summary':
        retained = document['retained_functions'][0]
        value = json.loads(retained['native_json']); value['summary'] = 'unproved function meaning'
        retained['native_json'] = json.dumps(value)
    else:
        value = json.loads(selected['original_native_json'])
        if fault == 'owner-summary':
            value['summary'] = 'partial owner'
        elif fault == 'source-note':
            value.pop('note')
        elif fault == 'writer-link':
            value['link'] = [r for r in value['link'] if r['type'] != 'writer']
        else:
            next(r for r in value['symbol'] if r['layout'] == '7mfk')['width'] = 8
        selected['original_native_json'] = json.dumps(value)
    monkeypatch.setattr(contract.tomllib, 'loads', lambda text: document)
    with pytest.raises(ValueError):
        contract.descriptor(repo.ROOT)
