"""Exact retained writer, full native snapshots and owning transition refusals."""
from copy import deepcopy
import json
from types import SimpleNamespace
import pytest
from kb import repo
from kb import request_boundary_publication_access_contract as contract

def row():return contract.descriptor(repo.ROOT)['reference'][0]

def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))

def test_the_one_owning_append_retains_all_native_readers_writers_and_other_facts():
    selected=row();before=json.loads(selected['original_native_json']);after=json.loads(selected['proposed_native_json'])
    stripped=deepcopy(after)
    target=next(value for value in stripped['link'] if (value['type'],value['to'])==('writer','request_boundary_dispatch/fn'))
    original=next(value for value in before['link'] if (value['type'],value['to'])==('writer','request_boundary_dispatch/fn'))
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence'] and 'evidence' not in original:target.pop('evidence')
    assert stripped==before and after['width']==16 and 'signed' not in after
    symbol=next(value for value in after['symbol'] if value['layout']=='7mfk')
    assert symbol['address']=='ffff19c6' and 'signed' not in symbol
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    assert any((value['type'],value['to'])==('writer','signed_request_boundary/fn') for value in after['link'])
    retained=contract.descriptor(repo.ROOT)['retained_functions']
    assert {(value['owner'],value['address']) for value in retained}=={
        ('request_boundary_dispatch/fn',0x79DD8),('acoustic-spaniel/fn',0x797D0),('signed_request_boundary/fn',0x79030)}
    value=contract.item(selected)['value']
    assert value['native_address']==0xFFFF19C6 and value['direction']=='writer' and value['width_bytes']==2
    assert value['actual_store_sites']==[0x791A8,0x791B2] and value['entry']==0x79DD8
    assert value['real_tail']==dict(site=0x79DE0,target=0x79030,PR_restore_delay=0x79DE2)
    assert value['scope']=='exact-delegated-request-publication'
    for key in ('native_geometry_inference','scale_admission','units_admission','natural_scheduling_inference','hardware_qualification'):
        assert value[key] is False

@pytest.mark.parametrize('fault',('duplicate','other-target','other-owner','scale-support','forged-original','partial-call-chain'))
def test_normal_writer_selection_refuses_any_change_to_the_unique_complete_append(fault):
    selected=row();operation=contract.operation(selected)
    assert contract.operations([deepcopy(operation)],repo.ROOT) is True
    changed=deepcopy(operation)
    if fault=='duplicate':operations=[changed,deepcopy(changed)]
    else:
        if fault=='other-target':changed['to']='signed_request_boundary/fn'
        elif fault=='other-owner':changed['meaning']='another-owner/ram'
        elif fault=='scale-support':changed['evidence'][0]['supports']='scale'
        elif fault=='forged-original':changed['evidence'][0]['value']['original_claim_sha256']='0'*64
        else:changed['evidence'][0]['value'].pop('real_tail')
        operations=[changed]
    with pytest.raises(ValueError):contract.operations(operations,repo.ROOT)

@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','direct-root-store','other-role','other-native-fact'))
def test_only_the_exact_owning_append_preserves_existing_physical_scope(fault):
    selected=row();item=contract.item(selected);current=link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='reader'
    elif fault=='direct-root-store':current.evidence[0]['value']['scope']='direct-store-at-79dd8'
    elif fault=='other-role':current.roles.append('arithmetic-factor')
    else:current.props['note']='changed unrelated native note'
    assert contract.publication(current,item) is False

@pytest.mark.parametrize('fault',('owner-note','other-link','semantic-type','ledger-position','function-summary'))
def test_complete_retained_native_images_reject_partial_or_changed_context(monkeypatch,fault):
    document=deepcopy(contract.DECLARED);selected=document['reference'][0]
    if fault=='function-summary':
        value=json.loads(document['retained_functions'][0]['native_json']);value['summary']='truncated function'
        document['retained_functions'][0]['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_native_json'])
        if fault=='owner-note':value['note']=['truncated owner context']
        elif fault=='other-link':value['link']=[item for item in value['link'] if item.get('to')!='signed_request_boundary/fn']
        elif fault=='semantic-type':value['signed']=True
        else:value['ledger']=list(reversed(value['ledger']))+[dict(source='invented')]
        selected['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)

def test_namespace_has_no_fallback_to_an_absence_or_unrelated_positive_component():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('maf-access','calculated-load-quantity-access','scalar-ram-leaf-withdrawal','register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    original=link(json.loads(row()['original_claim_json']))
    assert contract.looks_like_access(original)
    original.owner.key='unrelated/ram'
    assert not contract.looks_like_access(original)
