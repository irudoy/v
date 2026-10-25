"""Exact indexed_by association and complete native owner/function refusal boundaries."""
from copy import deepcopy
from types import SimpleNamespace
import json
import re
import pytest
from kb import repo
from kb import coolant_surface_coordinate_access_contract as contract


def rows():return contract.descriptor(repo.ROOT)['reference']
def row(index=0):return rows()[index]
def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),stated=list(document['stated']),sources=list(document['sources']))


@pytest.mark.parametrize('index',(0,1))
def test_each_append_retains_role_properties_and_all_native_facts(index):
    selected=row(index);before,after=(json.loads(selected[phase+'_native_json']) for phase in ('original','proposed'))
    stripped=deepcopy(after);target,=[r for r in stripped['link'] if (r['type'],r['to'])==('reader','gabby-vole/fn')]
    old_target,=[r for r in before['link'] if (r['type'],r['to'])==('reader','gabby-vole/fn')]
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence'] and 'evidence' not in old_target:target.pop('evidence')
    assert stripped==before and before['unit']==after['unit']==('normalized coolant index','raw')[index]
    old,new=(json.loads(selected[phase+'_claim_json']) for phase in ('original','proposed'))
    assert old['roles']==new['roles']==['indexed_by'] and old['props']==new['props']
    assert old['props']['reverse_supports']=='identity' and old['props']['reverse_relies']==('structure','level')[index]
    assert selected['declared_width']==selected['declared_signed']=='unset'
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    for kind in ('writer','copy','input'):
        assert [r for r in before['link'] if r['type']==kind]==[r for r in after['link'] if r['type']==kind]
    assert before.get('diagnostic')==after.get('diagnostic')
    value=contract.item(selected)['value']
    assert value['wrapper_physical_RAM106F_read' if index==0 else 'wrapper_physical_RAM10F0_read'] is False
    assert value['entry']==0x52576 and value['function']=='7mfk:00026040' and value['caller']=='7mfk:00052576'
    assert value['actual_input']['coordinate_register']==(5,6)[index]
    assert value['actual_input']['read_site']==(0x52582,0x52588)[index]
    assert value['actual_input']['address']==(0xFFFF106F,0xFFFF10F0)[index]
    if index==0:
        assert value['actual_input']['unsigned_extension_site']==0x52586
        assert value['actual_second_input']['unsigned_delay_site']==0x5258E
    else:
        assert value['actual_input']['unsigned_delay_site']==0x5258E
        assert value['physical_quantity_unresolved'] is True and value['unit_raw_retained_without_new_admission'] is True
        assert old['props']['supports']=='identity' and old['props']['relies']=='level'
    assert value['actual_final_output']==dict(address=0xFFFF1652,width_bytes=2,site=0x525CC,register=2)
    assert value['scope']==('exact-coolant-coordinate-handoff','exact-raw-inner-coordinate-handoff')[index]
    assert [(r['owner'],r['address']) for r in contract.DECLARED['retained_functions']]==[
        ('gabby-vole/fn',0x26040),('vivacious-cheetah/fn',0x52576)]
    for retained in contract.DECLARED['retained_functions']:
        assert contract.digest(json.loads(retained['native_json']))==retained['native_sha256']
    text=(repo.ROOT/'defs/JK08A.coolant-surface-coordinate.md').read_text()
    assert selected['original_claim_sha256'] in text
    assert int(re.search(r'joint group of (\d+) ordinary owning operations',text)[1])==len(rows())==2


@pytest.mark.parametrize('index',(0,1))
@pytest.mark.parametrize('fault',('duplicate','missing','writer-direction','other-target','scale-support','fixed-wrapper-read','forged-original'))
def test_normal_writer_requires_the_complete_joint_append_group(index,fault):
    ops=[contract.operation(selected) for selected in rows()]
    assert contract.operations(deepcopy(ops),repo.ROOT) is True
    if fault=='duplicate':ops.append(deepcopy(ops[index]))
    elif fault=='missing':ops.pop(index)
    elif fault=='writer-direction':ops[index]['type']='writer'
    elif fault=='other-target':ops[index]['to']='unrelated/fn'
    elif fault=='scale-support':ops[index]['evidence'][0]['supports']='scale'
    elif fault=='fixed-wrapper-read':
        key='wrapper_physical_RAM106F_read' if index==0 else 'wrapper_physical_RAM10F0_read'
        ops[index]['evidence'][0]['value'][key]=True
    else:ops[index]['evidence'][0]['value']['original_claim_sha256']='0'*64
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('index',(0,1))
@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','other-role','native-fact','other-register'))
def test_only_each_unique_exact_coordinate_append_is_neutral(index,fault):
    selected=row(index);item=contract.item(selected);current=link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='writer'
    elif fault=='other-role':current.roles.append('invented-role')
    elif fault=='native-fact':current.props['note']='changed fact'
    else:current.evidence[0]['value']['actual_input']['coordinate_register']=6 if index==0 else 5
    assert contract.publication(current,item) is False


@pytest.mark.parametrize('index',(0,1))
@pytest.mark.parametrize('fault',('summary','writer','input','diagnostic','unit','width','signed','ledger','wrapper','caller'))
def test_full_native_preimages_refuse_either_owner_or_function_changes(monkeypatch,index,fault):
    document=deepcopy(contract.DECLARED);selected=document['reference'][index]
    if fault in ('wrapper','caller'):
        position=0 if fault=='wrapper' else 1;value=json.loads(document['retained_functions'][position]['native_json'])
        value['summary']='partial function';document['retained_functions'][position]['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_native_json'])
        if fault=='summary':value['summary']='partial candidate'
        elif fault in ('writer','input'):value['link']=[r for r in value['link'] if r['type']!=fault]
        elif fault=='diagnostic':value['diagnostic']=[]
        elif fault=='unit':value['unit']='unproved unit'
        elif fault=='width':value['width']=8
        elif fault=='signed':value['signed']=False
        else:value['ledger']=[]
        selected['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def test_exact_namespace_has_no_absence_or_other_owner_fallback():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('engine-speed-curve-input-access','scalar-ram-leaf-withdrawal','register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    for selected in rows():
        current=link(json.loads(selected['original_claim_json']));assert contract.looks_like_access(current)
        current.owner.key='unrelated/ram';assert not contract.looks_like_access(current)
