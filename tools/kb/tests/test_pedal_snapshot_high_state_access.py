"""Exact retained reader, full native images and owning namespace refusal controls."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from kb import repo
from kb import pedal_snapshot_high_state_access_contract as contract


def row():
    return contract.descriptor(repo.ROOT)['reference'][0]


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']), to=SimpleNamespace(key=document['to']),
        type=document['type'], slot=document['slot'], offset=document['offset'], roles=list(document['roles']),
        props=deepcopy(document['props']), evidence=deepcopy(document['evidence']),
        stated=list(document['stated']), sources=list(document['sources']))


def test_one_append_retains_complete_pedal_owner_and_existing_function_facts():
    selected=row();before,after=(json.loads(selected[key+'_native_json']) for key in ('original','proposed'))
    stripped=deepcopy(after);target=next(r for r in stripped['link'] if (r['type'],r['to'])==('reader','remarkable-lynx/fn'))
    old_target=next(r for r in before['link'] if (r['type'],r['to'])==('reader','remarkable-lynx/fn'))
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence'] and 'evidence' not in old_target:target.pop('evidence')
    assert stripped==before
    symbol,=[r for r in after['symbol'] if r['layout']=='7mfk']
    assert symbol['address']=='ffff2672' and 'width' not in symbol and 'signed' not in symbol
    assert selected['declared_width']==selected['declared_signed']=='unset'
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    value=contract.item(selected)['value']
    assert value['source_read']==dict(address=0xFFFF2672,site=0x20FC0,width_bytes=2)
    assert value['producer_store']==dict(address=0xFFFF266E,site=0x20FC4,width_bytes=2)
    assert value['consumer_reads']==[dict(address=0xFFFF266E,site=site,width_bytes=2) for site in (0x47AAA,0x47B94)]
    assert value['actual_output']==dict(address=0xFFFF246A,width_bytes=1,mask=128)
    assert value['scope']=='exact-existing-prefix-pedal-state-quantity'
    for key in ('native_geometry_inference','scale_admission','units_admission','natural_caller_reachability',
                'natural_scheduling_inference','hardware_qualification'):assert value[key] is False
    assert [(r['owner'],r['address']) for r in contract.DECLARED['retained_functions']]==[('remarkable-lynx/fn',0x47A56)]


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
            changed['to'] = 'coherent_snapshot/fn'
        elif fault == 'other-owner':
            changed['meaning'] = 'another-pedal/ram'
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


@pytest.mark.parametrize('fault', ('owner-note', 'other-reader', 'semantic-type', 'ledger-position', 'consumer-summary'))
def test_complete_owner_and_retained_function_refuse_summary_substitutes(monkeypatch, fault):
    document = deepcopy(contract.DECLARED)
    selected = document['reference'][0]
    if fault=='consumer-summary':
        retained = document['retained_functions'][0]
        value = json.loads(retained['native_json'])
        value['summary'] = 'truncated function'
        retained['native_json'] = json.dumps(value)
    else:
        value = json.loads(selected['original_native_json'])
        if fault == 'owner-note':
            value['note'] = ['truncated quantity context']
        elif fault == 'other-reader':
            value['link'] = [r for r in value['link'] if r.get('to') != 'coherent_snapshot/fn']
        elif fault == 'semantic-type':
            next(r for r in value['symbol'] if r['layout'] == '7mfk')['width'] = 16
        else:
            value['ledger'] = list(reversed(value.get('ledger', []))) + [dict(source='invented')]
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
