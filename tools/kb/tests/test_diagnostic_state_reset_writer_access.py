"""Exact writer append, complete native preservation and owning-result refusals."""
from copy import deepcopy
from types import SimpleNamespace
import json
import pytest
from kb import repo,test_origins
from kb import diagnostic_state_reset_writer_access_contract as contract
from kb import diagnostic_state_reset_writer_access_evidence as proof
from kb import diagnostic_state_reset_writer_access_resolution as resolution


def row():return contract.descriptor(repo.ROOT)['reference'][0]


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']),to=SimpleNamespace(key=document['to']),
        type=document['type'],slot=document['slot'],offset=document['offset'],roles=list(document['roles']),
        props=deepcopy(document['props']),evidence=deepcopy(document['evidence']),
        stated=list(document['stated']),sources=list(document['sources']))


def test_one_append_preserves_full_owner_function_type_evidence_and_ledgers():
    selected=row();before,after=(json.loads(selected[phase+'_native_json']) for phase in ('original','proposed'))
    stripped=deepcopy(after);target,=[value for value in stripped['link'] if (value['type'],value['to'])==('writer','amber-wildcat/fn')]
    old_target,=[value for value in before['link'] if (value['type'],value['to'])==('writer','amber-wildcat/fn')]
    assert target['evidence'].pop()==contract.item(selected)
    if not target['evidence'] and 'evidence' not in old_target:target.pop('evidence')
    assert stripped==before
    assert selected['declared_width']==selected['declared_signed']=='unset'
    assert all('width' not in value and 'signed' not in value for value in before['symbol'])
    assert before['unit']==after['unit']=='raw'
    assert before['summary']==after['summary'] and before['note']==after['note']
    assert selected['original_ledger_json']==selected['proposed_ledger_json']
    assert json.loads(selected['original_symbol_evidence_json'])==before['symbol'][0]['evidence']
    assert {entry['address'] for entry in contract.DECLARED['retained_functions']}=={0x2E76E,0x2E81A,0xCD75C}
    value=contract.item(selected)['value']
    assert value['scope']=='exact-diagnostic-state-reset-writer'
    assert value['actual_constant_write']==dict(site=0x2E84A,address=0xFFFF99DE,width_bytes=1,register=14,
        full_register_value=0,value=0,loop_start=0xFFFF99DC,loop_count=24,zero_based_iteration=2)
    assert value['constant_requires_distinct_final_outputs'] is False
    assert value['native_storage']==[dict(start=0xFFFF8400,size=256),dict(start=0xFFFF9900,size=1792),dict(start=0xFFFFF500,size=256)]
    assert selected['original_claim_sha256'] in (repo.ROOT/'defs/JK08A.diagnostic-state-reset-writer.md').read_text()


@pytest.mark.parametrize('fault',('duplicate','reader-direction','other-target','scale-support','nonzero-store','forged-original','widened-native'))
def test_normal_writer_requires_the_one_exact_complete_append(fault):
    selected=row();op=contract.operation(selected);assert contract.operations([deepcopy(op)],repo.ROOT) is True
    if fault=='duplicate':ops=[op,deepcopy(op)]
    else:
        if fault=='reader-direction':op['type']='reader'
        elif fault=='other-target':op['to']='unrelated/fn'
        elif fault=='scale-support':op['evidence'][0]['supports']='scale'
        elif fault=='nonzero-store':op['evidence'][0]['value']['actual_constant_write']['value']=1
        elif fault=='widened-native':op['evidence'][0]['value']['native_storage'][0]['size']+=1
        else:op['evidence'][0]['value']['original_claim_sha256']='0'*64
        ops=[op]
    with pytest.raises(ValueError):contract.operations(ops,repo.ROOT)


@pytest.mark.parametrize('fault',('duplicate-evidence','wrong-direction','other-role','native-fact','other-live-register'))
def test_only_the_unique_exact_writer_append_is_neutral(fault):
    selected=row();item=contract.item(selected);current=link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current,item) is True
    assert contract.publication(link(json.loads(selected['original_claim_json'])),item) is False
    if fault=='duplicate-evidence':current.evidence.append(deepcopy(item))
    elif fault=='wrong-direction':current.type='reader'
    elif fault=='other-role':current.roles.append('invented-role')
    elif fault=='native-fact':current.props['note']='changed fact'
    else:current.evidence[0]['value']['actual_constant_write']['register']=0
    assert contract.publication(current,item) is False


@pytest.mark.parametrize('fault',('summary','other-writer','width','signed','unit','ledger','evidence','function','function-ledger'))
def test_complete_native_preimages_refuse_unrelated_changes(monkeypatch,fault):
    document=deepcopy(contract.DECLARED);selected=document['reference'][0]
    if fault in ('function','function-ledger'):
        retained=document['retained_functions'][0];value=json.loads(retained['native_json'])
        if fault=='function':value['summary']='partial function'
        else:value['ledger']=[]
        retained['native_json']=json.dumps(value)
    else:
        value=json.loads(selected['original_native_json'])
        if fault=='summary':value['summary']='partial candidate'
        elif fault=='other-writer':value['link']=[entry for entry in value['link'] if entry['to']!='quartz-trogon/fn']
        elif fault in ('width','signed'):value['symbol'][0][fault]=8 if fault=='width' else False
        elif fault=='unit':value['unit']='invented unit'
        elif fault=='ledger':value['ledger']=[]
        else:value['symbol'][0]['evidence'].pop()
        selected['original_native_json']=json.dumps(value)
    monkeypatch.setattr(contract.tomllib,'loads',lambda text:document)
    with pytest.raises(ValueError):contract.descriptor(repo.ROOT)


def result():
    selected=row()
    return dict({flag:True for flag in proof.REQUIRED_FLAGS},**{flag:False for flag in proof.NON_ADMISSIONS},
        causal_inputs=dict(raw_rom_8dfc=True,raw_rom_8dfd=True),
        constant_writer_inputs=dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True),
        native_bindings=[dict(symbol='7mfk-ffff99de/ram',meaning=selected['owner'],function='7mfk-0002e81a/fn',
            function_meaning='amber-wildcat/fn',original_claim_sha256=selected['original_claim_sha256'])])


@pytest.mark.parametrize('flag',proof.REQUIRED_FLAGS)
@pytest.mark.parametrize('value',(False,1,None))
def test_owning_boundary_requires_each_strict_complete_obligation(flag,value):
    current=result();assert proof.require_result(current,row()) is True;current[flag]=value
    with pytest.raises(ValueError):proof.require_result(current,row())


@pytest.mark.parametrize('flag',proof.NON_ADMISSIONS)
def test_owning_boundary_cannot_grant_an_unmeasured_native_or_hardware_fact(flag):
    current=result();current[flag]=True
    with pytest.raises(ValueError):proof.require_result(current,row())


@pytest.mark.parametrize('fault',('missing','extra','owner','function','original','shape','ROM-proof','constant-proof'))
def test_owning_boundary_binds_the_exact_original_and_both_kinds_of_publication_obligation(fault):
    current=result()
    if fault=='missing':current['native_bindings'].pop()
    elif fault=='extra':current['native_bindings'].append(deepcopy(current['native_bindings'][0]))
    elif fault=='shape':current['native_bindings']={}
    elif fault=='ROM-proof':current['causal_inputs']['raw_rom_8dfc']=False
    elif fault=='constant-proof':current['constant_writer_inputs']['gate_1_full_priors']=False
    else:current['native_bindings'][0][{'owner':'meaning','function':'function_meaning','original':'original_claim_sha256'}[fault]]='changed'
    with pytest.raises(ValueError):proof.require_result(current,row())


def test_transition_refuses_any_TEST_origin_or_evidence_position_change(monkeypatch):
    from kb import copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence
    selected=row();before=SimpleNamespace(root=repo.ROOT,links=[link(json.loads(selected['original_claim_json']))])
    after=SimpleNamespace(root=repo.ROOT,links=[link(json.loads(selected['proposed_claim_json']))])
    monkeypatch.setattr(proof,'native_rows',lambda model:[selected])
    monkeypatch.setattr(proof,'require_current',lambda model:True)
    for module in (copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence):
        monkeypatch.setattr(module,'scope_digest',lambda model:'unchanged-scope')
    origin=dict(owner='exact-source',position=7,evidence=['retained-item'])
    monkeypatch.setattr(test_origins,'index',lambda model:{'exact':SimpleNamespace(packet=lambda:deepcopy(origin))})
    assert resolution.require_transition(before,after)==[selected]
    monkeypatch.setattr(test_origins,'index',lambda model:{'exact':SimpleNamespace(packet=lambda:dict(origin,position=8 if model is after else 7))})
    with pytest.raises(ValueError):resolution.require_transition(before,after)


def test_namespace_has_no_absence_or_other_owner_fallback():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('third-trim-word-writer-access','scalar-ram-leaf-withdrawal','register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    current=link(json.loads(row()['original_claim_json']));assert contract.looks_like_access(current)
    current.owner.key='unrelated/ram';assert not contract.looks_like_access(current)


def test_one_registered_family_routes_the_exact_writer_and_complete_raw_component():
    from kb import ordinary_access_registry as registry
    family,=[entry for entry in registry.FAMILIES if entry.mode==contract.MODE]
    assert family.captures==(('diagnostic_state_reset_writer_paths','diagnostic_state_reset_writer_capture'),)
    assert family.direct_owning is True and family.owner_fallback is False and family.withdrawal_only is False
    assert set(family.evidence.COMPONENTS)=={'diagnostic_state_reset_writer_paths'}
    assert set(proof.capture.SOURCE_FILES)<=set(family.source_files)
    selected=row();assert registry.matching(contract.item(selected))==(family,)
    assert registry.original_family(json.loads(selected['original_claim_json'])) is family
    altered=json.loads(selected['original_claim_json']);altered['to']='quartz-trogon/fn'
    assert registry.original_family(altered) is not family
