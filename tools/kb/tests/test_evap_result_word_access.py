"""Exact writer append and full native owner, function and reverse-property retention."""
from copy import deepcopy
import json
import pytest
from kb import repo
from kb import evap_result_word_access_contract as contract


def test_only_one_writer_evidence_append_changes_the_complete_native_owner():
    row, = contract.descriptor(repo.ROOT)['reference']
    before, after = (json.loads(row[key + '_native_json']) for key in ('original', 'proposed'))
    stripped = deepcopy(after)
    target = next(r for r in stripped['link'] if (r['type'], r['to']) == ('writer', 'classic-pelican/fn'))
    assert target['evidence'].pop() == contract.item(row)
    if not target['evidence']:
        target.pop('evidence')
    assert stripped == before
    assert target['reverse_relies'] == 'structure' and target['reverse_supports'] == 'identity'
    assert after['unit'] == 'diagnostic raw' and row['original_ledger_json'] == row['proposed_ledger_json']
    symbol, = [r for r in after['symbol'] if r['layout'] == '7mfk']
    assert symbol['address'] == 'ffff301c' and 'width' not in symbol and 'signed' not in symbol
    assert contract.symbol_key(row).kind == 'ram'
    value = contract.item(row)['value']
    assert value['actual_store'] == dict(site=0xB22A6, address=0xFFFF301C, width_bytes=2, pointer_register=12)
    assert value['entry_pointer'] == dict(register=6, native=0xFFFF301C, simulator=0x0100301C)
    assert value['caller_context']['whole_caller_execution_admitted'] is False


@pytest.mark.parametrize('fault', ('duplicate', 'reader', 'other-owner', 'scale', 'pointer', 'caller-scope'))
def test_exact_writer_batch_refuses_related_but_different_operations(fault):
    row, = contract.descriptor(repo.ROOT)['reference']
    operation = contract.operation(row)
    assert operation['type'] == 'writer' and contract.operations([deepcopy(operation)], repo.ROOT)
    changed = deepcopy(operation)
    if fault == 'duplicate':
        operations = [changed, deepcopy(changed)]
    else:
        if fault == 'reader':
            changed['type'] = 'reader'
        elif fault == 'other-owner':
            changed['meaning'] = 'elegant-woodlouse/ram'
        elif fault == 'scale':
            changed['evidence'][0]['supports'] = 'scale'
        elif fault == 'pointer':
            changed['evidence'][0]['value']['entry_pointer']['simulator'] ^= 2
        else:
            changed['evidence'][0]['value']['caller_context']['whole_caller_execution_admitted'] = True
        operations = [changed]
    with pytest.raises(ValueError):
        contract.operations(operations, repo.ROOT)
