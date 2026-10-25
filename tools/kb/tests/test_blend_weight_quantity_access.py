"""Exact retained reader, full native images and owning namespace refusal controls."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from kb import repo
from kb import blend_weight_quantity_access_contract as contract


def row():
    return contract.descriptor(repo.ROOT)['reference'][0]


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']), to=SimpleNamespace(key=document['to']),
        type=document['type'], slot=document['slot'], offset=document['offset'], roles=list(document['roles']),
        props=deepcopy(document['props']), evidence=deepcopy(document['evidence']),
        stated=list(document['stated']), sources=list(document['sources']))


def test_one_append_retains_both_readers_and_all_scale_unit_ledger_and_TEST_context():
    selected = row()
    before, after = (json.loads(selected[key + '_native_json']) for key in ('original', 'proposed'))
    stripped = deepcopy(after)
    target = next(r for r in stripped['link'] if (r['type'], r['to']) == ('reader', 'tuscan-vulture/fn'))
    old_target = next(r for r in before['link'] if (r['type'], r['to']) == ('reader', 'tuscan-vulture/fn'))
    assert target['evidence'].pop() == contract.item(selected)
    if not target['evidence'] and 'evidence' not in old_target:
        target.pop('evidence')
    assert stripped == before and target['relies'] == 'level'
    assert any((r['type'], r['to']) == ('reader', 'eminent-moth/fn') for r in after['link'])
    assert (after['scale'], after['to_raw'], after['unit']) == ('x/65536', 'x*65536', 'Q16 fraction (0..1)')
    symbol, = [r for r in after['symbol'] if r['layout'] == '7mfk']
    assert symbol['address'] == '0001488a' and 'width' not in symbol and 'signed' not in symbol
    assert selected['original_ledger_json'] == selected['proposed_ledger_json']
    assert json.loads(selected['original_claim_json'])['props']['relies'] == 'level'
    value = contract.item(selected)['value']
    assert value['producer_store'] == dict(site=0x70EC2, address=0xFFFF190E, width_bytes=2)
    assert value['consumer_read'] == dict(site=0x7211A, address=0xFFFF190E, width_bytes=2)
    assert value['actual_output'] == dict(site=0x72136, address=0xFFFF124A, width_bytes=2)
    assert value['scope'] == 'exact-two-phase-shared-blend-weight-quantity'
    for key in ('native_geometry_inference', 'scale_admission', 'units_admission', 'natural_scheduling_inference', 'hardware_qualification'):
        assert value[key] is False
    assert [(r['owner'], r['address']) for r in contract.DECLARED['retained_functions']] == [
        ('eminent-moth/fn', 0x70E4C), ('tuscan-vulture/fn', 0x720C4)]


@pytest.mark.parametrize('fault', ('duplicate', 'other-target', 'other-owner', 'scale-support', 'forged-original', 'partial-phase'))
def test_owning_writer_refuses_any_change_to_the_single_exact_append(fault):
    selected = row()
    op = contract.operation(selected)
    assert contract.operations([deepcopy(op)], repo.ROOT) is True
    changed = deepcopy(op)
    if fault == 'duplicate':
        ops = [changed, deepcopy(changed)]
    else:
        if fault == 'other-target':
            changed['to'] = 'eminent-moth/fn'
        elif fault == 'other-owner':
            changed['meaning'] = 'another-table/tbl'
        elif fault == 'scale-support':
            changed['evidence'][0]['supports'] = 'scale'
        elif fault == 'forged-original':
            changed['evidence'][0]['value']['original_claim_sha256'] = '0' * 64
        else:
            changed['evidence'][0]['value'].pop('producer_store')
        ops = [changed]
    with pytest.raises(ValueError):
        contract.operations(ops, repo.ROOT)


@pytest.mark.parametrize('fault', ('duplicate-evidence', 'wrong-direction', 'physical-ROM-read', 'other-role', 'other-native-fact'))
def test_only_the_unique_exact_quantity_append_is_neutral_to_existing_physical_scopes(fault):
    selected = row()
    item = contract.item(selected)
    current = link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current, item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])), item) is False
    if fault == 'duplicate-evidence':
        current.evidence.append(deepcopy(item))
    elif fault == 'wrong-direction':
        current.type = 'writer'
    elif fault == 'physical-ROM-read':
        current.evidence[0]['value']['scope'] = 'physical-ROM-read-at-7211a'
    elif fault == 'other-role':
        current.roles.append('arithmetic-factor')
    else:
        current.props['note'] = 'changed native fact'
    assert contract.publication(current, item) is False


@pytest.mark.parametrize('fault', ('owner-note', 'other-reader', 'semantic-type', 'ledger-position', 'producer-summary', 'consumer-summary'))
def test_complete_owner_and_both_function_images_refuse_summary_substitutes(monkeypatch, fault):
    document = deepcopy(contract.DECLARED)
    selected = document['reference'][0]
    if fault in ('producer-summary', 'consumer-summary'):
        retained = document['retained_functions'][0 if fault == 'producer-summary' else 1]
        value = json.loads(retained['native_json'])
        value['summary'] = 'truncated function'
        retained['native_json'] = json.dumps(value)
    else:
        value = json.loads(selected['original_native_json'])
        if fault == 'owner-note':
            value['note'] = ['truncated quantity context']
        elif fault == 'other-reader':
            value['link'] = [r for r in value['link'] if r.get('to') != 'eminent-moth/fn']
        elif fault == 'semantic-type':
            next(r for r in value['symbol'] if r['layout'] == '7mfk')['width'] = 16
        else:
            value['ledger'] = list(reversed(value['ledger'])) + [dict(source='invented')]
        selected['original_native_json'] = json.dumps(value)
    monkeypatch.setattr(contract.tomllib, 'loads', lambda text: document)
    with pytest.raises(ValueError):
        contract.descriptor(repo.ROOT)


def test_quantity_namespace_has_no_fallback_into_physical_or_absence_admission():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('maf-access', 'calculated-load-quantity-access', 'scalar-ram-leaf-withdrawal', 'register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    original = link(json.loads(row()['original_claim_json']))
    assert contract.looks_like_access(original)
    original.owner.key = 'unrelated/tbl'
    assert not contract.looks_like_access(original)
