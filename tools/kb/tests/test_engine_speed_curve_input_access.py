"""Exact coordinate association, complete retained native documents and owning refusals."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from kb import repo
from kb import engine_speed_curve_input_access_contract as contract


def row():return contract.descriptor(repo.ROOT)['reference'][0]
def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))


def test_one_append_retains_writer_copy_unit_types_and_both_full_functions():
    selected=row();before,after=(json.loads(selected[phase+'_native_json']) for phase in ('original','proposed'))
    stripped=deepcopy(after);target,=[r for r in stripped['link'] if (r['type'],r['to'])==('reader','idle_ignition_lookup/fn')]
    old_target,=[r for r in before['link'] if (r['type'],r['to'])==('reader','idle_ignition_lookup/fn')]
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence'] and 'evidence' not in old_target:target.pop('evidence')
    assert stripped==before
    for kind in ('writer','copy','input'):
        assert [r for r in before['link'] if r['type']==kind]==[r for r in after['link'] if r['type']==kind]
    assert before['unit']==after['unit']=='rpm/12.5'
    assert selected['declared_width']==selected['declared_signed']=='unset'
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    value=contract.item(selected)['value']
    assert value['wrapper_physical_RAM11B2_read'] is False
    assert value['entry']==0x4AFDC and value['function']=='7mfk:00026370'
    assert value['caller']=='7mfk:0004afdc'
    assert value['actual_input']==dict(address=0xFFFF11B2,width_bytes=1,
        read_sites=[0x4B054,0x4B08A,0x4B0B4],register=2)
    assert value['actual_quantity_publication']==dict(address=0xFFFF1511,width_bytes=1,site=0x4B0D0,register=2)
    assert value['actual_final_output']==dict(address=0xFFFF23EE,width_bytes=1,site=0x4B546,register=2)
    assert value['actual_inner_stack_argument']['original_frame_high24_offset']==116
    assert value['full_SR_interrupt_restore_and_current_MQT_required'] is True
    assert value['scope']=='exact-engine-speed-coordinate-handoff'
    assert [(r['owner'],r['address']) for r in contract.DECLARED['retained_functions']]==[
        ('idle_ignition_lookup/fn',0x26370),('signed_timing_state_accumulator/fn',0x4AFDC)]
    text=(repo.ROOT/'defs/JK08A.engine-speed-curve-input.md').read_text()
    assert selected['original_claim_sha256'] in text


@pytest.mark.parametrize('fault',('duplicate','writer-direction','other-target','scale-support','fixed-wrapper-read','forged-original'))
def test_normal_writer_requires_one_exact_coordinate_reader_append(fault):
    selected=row();op=contract.operation(selected);assert contract.operations([deepcopy(op)],repo.ROOT) is True
    if fault=='duplicate':ops=[op,deepcopy(op)]
    else:
        if fault=='writer-direction':op['type']='writer'
        elif fault=='other-target':op['to']='unrelated/fn'
        elif fault=='scale-support':op['evidence'][0]['supports']='scale'
        elif fault=='fixed-wrapper-read':op['evidence'][0]['value']['wrapper_physical_RAM11B2_read']=True
        else:op['evidence'][0]['value']['original_claim_sha256']='0'*64
        ops=[op]
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','other-role','native-fact','other-register'))
def test_only_unique_exact_actual_handoff_append_is_neutral(fault):
    selected=row();item=contract.item(selected);current=link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='writer'
    elif fault=='other-role':current.roles.append('invented-role')
    elif fault=='native-fact':current.props['note']='changed fact'
    else:current.evidence[0]['value']['actual_input']['register']=5
    assert contract.publication(current,item) is False


@pytest.mark.parametrize('fault',('summary','writer','copy','unit','width','signed','ledger','wrapper','caller'))
def test_full_native_preimages_refuse_owner_and_either_function_changes(monkeypatch,fault):
    document=deepcopy(contract.DECLARED);selected=document['reference'][0]
    if fault in ('wrapper','caller'):
        index=0 if fault=='wrapper' else 1
        value=json.loads(document['retained_functions'][index]['native_json']);value['summary']='partial function'
        document['retained_functions'][index]['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_native_json'])
        if fault=='summary':value['summary']='partial candidate'
        elif fault in ('writer','copy'):value['link']=[r for r in value['link'] if r['type']!=fault]
        elif fault=='unit':value['unit']='unproved unit'
        elif fault=='width':value['width']=8
        elif fault=='signed':value['signed']=False
        else:value['ledger']=[]
        selected['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def test_exact_namespace_has_no_absence_or_other_owner_fallback():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('second-channel-weight-access','scalar-ram-leaf-withdrawal','register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    current=link(json.loads(row()['original_claim_json']));assert contract.looks_like_access(current)
    current.owner.key='unrelated/ram';assert not contract.looks_like_access(current)
