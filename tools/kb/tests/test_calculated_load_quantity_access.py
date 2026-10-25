"""Exact retained conditional reader, namespace and complete owning transition refusals."""
from copy import deepcopy
import json
from types import SimpleNamespace
import pytest
from kb import repo,test_contract
from kb import calculated_load_quantity_access_contract as contract

def row():return contract.descriptor(repo.ROOT)['reference'][0]

def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))

def test_the_single_append_retains_both_readers_and_every_other_native_property():
    selected=row();before=json.loads(selected['original_native_json']);after=json.loads(selected['proposed_native_json'])
    stripped=deepcopy(after)
    target=next(r for r in stripped['link'] if (r['type'],r['to'])==('reader','eminent-chamois/fn'))
    original_target=next(r for r in before['link'] if (r['type'],r['to'])==('reader','eminent-chamois/fn'))
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence'] and 'evidence' not in original_target:target.pop('evidence')
    assert stripped==before
    assert any((r['type'],r['to'])==('reader','successful-ammonite/fn') for r in after['link'])
    symbol=next(r for r in after['symbol'] if r['layout']=='7mfk')
    assert symbol['address']=='000129d2' and 'width' not in symbol and 'signed' not in symbol
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    assert json.loads(selected['original_claim_json'])['to']=='eminent-chamois/fn'
    value=contract.item(selected)['value']
    assert value['producer_store']==dict(site=0xB999A,address=0xFFFF329F,width_bytes=1)
    assert value['consumer_read']==dict(site=0x808F4,address=0xFFFF329F,width_bytes=1)
    assert value['native_address']==0x129D2 and value['scope']=='exact-two-phase-conditional-table-derived-quantity'
    for key in ('native_geometry_inference','scale_admission','units_admission','natural_scheduling_inference','hardware_qualification'):
        assert value[key] is False

@pytest.mark.parametrize('fault',('duplicate','other-target','other-owner','scale-support','forged-original','partial-phase'))
def test_owning_writer_selection_rejects_any_change_to_the_one_exact_complete_append(fault):
    selected=row();op=contract.operation(selected)
    assert contract.operations([deepcopy(op)],repo.ROOT) is True
    changed=deepcopy(op)
    if fault=='duplicate':ops=[changed,deepcopy(changed)]
    else:
        if fault=='other-target':changed['to']='successful-ammonite/fn'
        elif fault=='other-owner':changed['meaning']='another-table/tbl'
        elif fault=='scale-support':changed['evidence'][0]['supports']='scale'
        elif fault=='forged-original':changed['evidence'][0]['value']['original_claim_sha256']='0'*64
        else:changed['evidence'][0]['value'].pop('producer_store')
        ops=[changed]
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)

@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','physical-ROM-read-claim','other-role','other-native-fact'))
def test_only_the_unique_exact_conditional_append_can_be_neutral_to_existing_physical_scopes(fault):
    selected=row();item=contract.item(selected);current=link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='writer'
    elif fault=='physical-ROM-read-claim':current.evidence[0]['value']['scope']='physical-ROM-read-at-808f4'
    elif fault=='other-role':current.roles.append('arithmetic-factor')
    else:current.props['note']='changed unrelated native note'
    assert contract.publication(current,item) is False

@pytest.mark.parametrize('fault',('owner-note','other-reader','semantic-type','ledger-position','function-summary'))
def test_complete_retained_owner_and_function_images_are_required_without_a_summary_substitute(monkeypatch,fault):
    document=deepcopy(contract.DECLARED);selected=document['reference'][0]
    if fault=='function-summary':
        value=json.loads(document['retained_function']['native_json']);value['summary']='truncated function';document['retained_function']['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_native_json'])
        if fault=='owner-note':value['note']=['truncated conditional context']
        elif fault=='other-reader':value['link']=[r for r in value['link'] if r.get('to')!='successful-ammonite/fn']
        elif fault=='semantic-type':next(r for r in value['symbol'] if r['layout']=='7mfk')['width']=8
        else:value['ledger']=list(reversed(value['ledger']))+[dict(source='invented')]
        selected['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)

def test_the_new_namespace_has_no_fallback_into_existing_physical_or_absence_proofs():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('maf-access','closed-loop-coordinate-access','scalar-ram-leaf-withdrawal','register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    original=link(json.loads(row()['original_claim_json']))
    assert contract.looks_like_access(original)
    original.owner.key='unrelated/tbl'
    assert not contract.looks_like_access(original)
