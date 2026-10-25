"""Exact retained reader, unchanged native writer and owning refusal boundaries."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from kb import repo
from kb import third_trim_word_writer_access_contract as contract

def row():return contract.descriptor(repo.ROOT)['reference'][0]
def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))

def test_one_append_retains_writer_and_companions_and_full_native_fact_images():
    selected=row();before,after=(json.loads(selected[phase+'_native_json']) for phase in ('original','proposed'))
    stripped=deepcopy(after);target,=[r for r in stripped['link'] if (r['type'],r['to'])==('writer','true-quokka/fn')]
    old_target,=[r for r in before['link'] if (r['type'],r['to'])==('writer','true-quokka/fn')]
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence'] and 'evidence' not in old_target:target.pop('evidence')
    assert stripped==before
    assert [r for r in before['link'] if r['type']=='writer' and r['to']!='true-quokka/fn']==[r for r in after['link'] if r['type']=='writer' and r['to']!='true-quokka/fn']
    assert [r for r in before['link'] if r['type']=='reader']==[r for r in after['link'] if r['type']=='reader']
    assert before['unit']==after['unit']=='percent*256'
    assert selected['declared_width']==16 and selected['declared_signed']=='unset'
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    value=contract.item(selected)['value']
    assert value['identity_channel']==0 and value['raw_channel_values']==256
    assert value['actual_indexed_write']==dict(base=0xFFFF2A24,stride=2,width_bytes=2,site=0x5B6F0,register=2)
    assert value['actual_shared_write']['site']==0x5B6F4
    assert value['native_storage_width']==16 and value['native_producer_signedness']=='unset'
    assert value['typed_reader']=='bank_base_pulse_builder/fn'
    assert value['scope']=='exact-bank1-third-trim-word-writer'
    assert [(r['owner'],r['address']) for r in contract.DECLARED['retained_functions']]==[('true-quokka/fn',0x5B534)]
    text=(repo.ROOT/'defs/JK08A.third-trim-word-writer.md').read_text()
    assert selected['original_claim_sha256'] in text

@pytest.mark.parametrize('fault',('duplicate','reader-direction','other-target','scale-support','other-identity-channel','forged-original'))
def test_normal_writer_requires_the_one_exact_reader_append(fault):
    selected=row();op=contract.operation(selected);assert contract.operations([deepcopy(op)],repo.ROOT) is True
    if fault=='duplicate':ops=[op,deepcopy(op)]
    else:
        if fault=='reader-direction':op['type']='reader'
        elif fault=='other-target':op['to']='unrelated/fn'
        elif fault=='scale-support':op['evidence'][0]['supports']='scale'
        elif fault=='other-identity-channel':op['evidence'][0]['value']['identity_channel']=1
        else:op['evidence'][0]['value']['original_claim_sha256']='0'*64
        ops=[op]
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)

@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','other-role','native-fact','other-live-register'))
def test_only_unique_exact_published_quantity_append_is_neutral(fault):
    selected=row();item=contract.item(selected);current=link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='reader'
    elif fault=='other-role':current.roles.append('invented-role')
    elif fault=='native-fact':current.props['note']='changed fact'
    else:current.evidence[0]['value']['actual_indexed_write']['register']=0
    assert contract.publication(current,item) is False

@pytest.mark.parametrize('fault',('summary','writer','width','ledger','function'))
def test_full_native_preimages_refuse_unrelated_owner_or_function_changes(monkeypatch,fault):
    document=deepcopy(contract.DECLARED);selected=document['reference'][0]
    if fault=='function':
        value=json.loads(document['retained_functions'][0]['native_json']);value['summary']='partial function'
        document['retained_functions'][0]['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_native_json'])
        if fault=='summary':value['summary']='partial candidate'
        elif fault=='writer':value['link']=[r for r in value['link'] if r['type']!='writer']
        elif fault=='width':value['width']=8
        else:value['ledger']=[]
        selected['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)

def test_exact_namespace_has_no_absence_or_other_owner_fallback():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('centered-channel-duty-access','scalar-ram-leaf-withdrawal','register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    current=link(json.loads(row()['original_claim_json']));assert contract.looks_like_access(current)
    current.owner.key='unrelated/ram';assert not contract.looks_like_access(current)
