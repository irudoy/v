"""Exact native owner/function/TEST preservation and typed owning refusals."""

from copy import deepcopy
import json
from pathlib import Path
import pytest
from kb import compile,repo,store,test_origins
from kb import scalar_ram_leaf_withdrawal_contract as owning
from kb import scalar_ram_leaf_withdrawal_evidence as family
from kb import signed_abs_register_helper_withdrawal_capture_evidence as capture


def selected():
    row,=[row for row in owning.descriptor(repo.ROOT)['reference']
        if row['component']=='signed_abs_register_helper_withdrawal_paths']
    return row


def test_exact_reader_and_one_owner_selector_preserve_every_other_native_fact():
    row=selected();assert row['original_claim_sha256']=='782dacc59731fbc23c8a52ec82e8f9cc0468235c9826a1eee5214cbe5d571417'
    claim=json.loads(row['original_claim_json'])
    assert (claim['type'],claim['owner'],claim['to'])==('reader','wandering-grasshopper/ram','clay-capuchin/fn')
    assert claim['props']==dict(layouts=['7mfk'],relies='contract',supports='identity')
    assert row['declared_width']==row['declared_signed']=='unset'
    before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json']);expected=deepcopy(before)
    link,=[link for link in expected['link'] if link['type']=='reader' and link['to']=='clay-capuchin/fn']
    expected['link'].remove(link);removed=[]
    for marker in expected.get('ledger',[]):
        for dependency in list(marker.get('dependency',[])):
            if (dependency.get('type'),dependency.get('to'),dependency.get('end'))==('reader','clay-capuchin/fn','owner'):
                removed.append(dependency);marker['dependency'].remove(dependency)
    assert len(removed)==1 and after==expected
    assert before['unit']==after['unit']=='raw difference' and before['symbol']==after['symbol']
    assert len([link for link in after['link'] if link['type']=='input'])==2
    writer,=[link for link in after['link'] if link['type']=='writer'];assert writer['to']=='gay-labrador/fn'
    assert {key:value for key,value in before.items() if key not in ('link','ledger')}=={
        key:value for key,value in after.items() if key not in ('link','ledger')}


def test_complete_native_function_and_its_existing_bounded_caller_contract_remain_exact():
    row,=[row for row in owning.descriptor(repo.ROOT)['function'] if row['function']==0x22590]
    before=owning.function_native_document(row,'original');after=owning.function_native_document(row,'proposed')
    assert row['owner']=='clay-capuchin/fn' and before==after
    assert before['block']=='library/block' and before['role']=='service'
    assert 'five register instructions, no memory access' in before['contract']
    assert 'INT32_MIN domain is outside this caller contract' in before['summary']
    assert before['ledger']==[dict(registry='funcs',order=56,fields=['role','contract','contract_conf'],contract=[0])]


def result():
    return dict(**{key:True for key in capture.OWNING_FLAGS},**{key:False for key in capture.NON_ADMISSIONS},
        stdout_sha256='1'*64,native_bindings=[dict(symbol='7mfk-ffff2c1c/ram',meaning='wandering-grasshopper/ram',
            function='7mfk-00022590/fn',function_meaning='clay-capuchin/fn',
            original_claim_sha256='782dacc59731fbc23c8a52ec82e8f9cc0468235c9826a1eee5214cbe5d571417')])


@pytest.mark.parametrize('key',capture.OWNING_FLAGS)
@pytest.mark.parametrize('fault',('missing','false','integer'))
def test_owning_consumer_requires_every_independent_full_raw32_obligation(key,fault):
    value=result();assert capture.require_owning_result(value) is True
    if fault=='missing':value.pop(key)
    else:value[key]=1 if fault=='integer' else False
    with pytest.raises(ValueError):capture.require_owning_result(value)


@pytest.mark.parametrize('key',capture.NON_ADMISSIONS)
@pytest.mark.parametrize('fault',('missing','true','integer'))
def test_owning_result_grants_no_type_scale_unit_geometry_caller_scheduler_or_hardware_fact(key,fault):
    value=result()
    if fault=='missing':value.pop(key)
    else:value[key]=0 if fault=='integer' else True
    with pytest.raises(ValueError):capture.require_owning_result(value)


@pytest.mark.parametrize('fault',('shape','owner','function','meaning','original','stdout'))
def test_owning_result_refuses_another_exact_original_or_missing_actual_original_hash(fault):
    value=result()
    if fault=='shape':value['native_bindings']={}
    elif fault=='stdout':value['stdout_sha256']='missing'
    else:value['native_bindings'][0][{'owner':'meaning','function':'function','meaning':'function_meaning','original':'original_claim_sha256'}[fault]]='changed'
    with pytest.raises(ValueError):capture.require_owning_result(value)


@pytest.fixture(scope='module')
def native_models():
    declared=owning.descriptor(repo.ROOT);models={}
    for phase in ('original','proposed'):
        overlay={Path(row['source']):store.render(row['owner'].rsplit('/',1)[1],json.loads(row[phase+'_native_json']))
            for row in declared['reference']}
        overlay.update({Path(row['source']):store.render('fn',owning.function_native_document(row,phase))
            for row in declared['function']})
        models[phase]=compile.build(repo.ROOT,overlay)
    return models


def test_complete_native_phases_preserve_every_original_TEST_origin_and_attachment(native_models):
    before,after=(native_models[phase] for phase in ('original','proposed'))
    assert family.native_rows(before,'original')==family.native_rows(after,'proposed')
    assert {key:origin.packet() for key,origin in test_origins.index(before).items()}=={
        key:origin.packet() for key,origin in test_origins.index(after).items()}


@pytest.mark.parametrize('phase',('original','proposed'))
@pytest.mark.parametrize('fault',('unit','input','writer','owner-TEST','ledger-order','function-note','function-TEST'))
def test_actual_native_consumer_refuses_unrelated_owner_function_or_TEST_changes(native_models,monkeypatch,phase,fault):
    row=selected();function,=[item for item in owning.descriptor(repo.ROOT)['function'] if item['function']==0x22590]
    path=function['source'] if fault.startswith('function-') else row['source'];load=store.load
    def changed(root,name,overlay=None):
        value=deepcopy(load(root,name,overlay))
        if str(name)!=path:return value
        if fault=='unit':value['unit']='unregistered unit'
        elif fault in ('input','writer'):
            link=next(link for link in value['link'] if link['type']==fault);value['link'].remove(link)
        elif fault.endswith('TEST'):value['symbol'][0]['evidence']=[]
        elif fault=='ledger-order':value['ledger'][0]['order']+=1
        else:value['note']=[]
        return value
    monkeypatch.setattr(store,'load',changed)
    with pytest.raises(ValueError):family.native_rows(native_models[phase],phase)
