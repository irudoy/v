"""Exact natural CVTC returned-byte disposition and actual-output refusals."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_contract,test_evidence
from kb import cvtc_gain_output_contract as output,calculation_dependency_contract as calculation
from kb import calculation_dependency_evidence as owning
from kb import exhaust_cvtc_capture_evidence as proof

PRIOR_37_SHA256='3bbcb91f1fc98b69e3af2681ab6fccee51a26f1ceaf93afd0e63a0dbdd9ab4e3'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_one_exact_result_preserves_all_prior_calculations_and_complete_native_owner():
    row=output.descriptor(repo.ROOT)['reference'][0]
    old,new=(json.loads(row[key]) for key in ('original_claim_json','proposed_claim_json'))
    before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
    assert old['type']=='reader' and new['type']=='depends' and new['roles']==['arithmetic-output']
    assert new['props']['relies']==old['props']['relies']=='level'
    assert new['props']['via']==["SymbolKey(layout='7mfk', kind='fn', address=794092)"]
    assert row['component']=='exhaust_cvtc_transition_paths'
    assert (row['callsite'],row['delay_slot'],row['returned_site'],row['store_site'])==(0xC1ED4,0xC1ED6,0xC1ED8,0xC1EE2)
    assert len(before['link'])==len(after['link'])==8
    unchanged=deepcopy(after);unchanged['link'][4]=deepcopy(before['link'][4]);unchanged['ledger']=deepcopy(before['ledger'])
    assert test_contract.exact(unchanged,before)
    assert len(before['symbol'][0]['evidence'])==2 and before['symbol']==after['symbol']
    prior=deepcopy(before['ledger']);removed=prior[0]['dependency'].pop(1)
    assert removed==dict(role='consumer',to=output.TARGET,type='reader',end='owner',relies='level',supports='identity')
    assert test_contract.exact(prior,after['ledger'])
    assert len(calculation.IDENTITIES)==38 and digest(calculation.IDENTITIES[:37])==PRIOR_37_SHA256
    assert calculation.IDENTITIES[37:]==(('cvtc-gain','gain-byte',output.OWNER,0xFFFF143A,output.ORIGINAL,output.PROPOSED),)


@pytest.mark.parametrize('flag',output.FLAGS)
def test_descriptor_refuses_inference_outside_the_exact_return_to_store_path(tmp_path,flag):
    path=tmp_path/output.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/output.DESCRIPTOR).read_text();assert flag+' = false' in text
    path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):output.descriptor(tmp_path)


@pytest.mark.parametrize('field',('callsite','delay_slot','returned_site','store_site','width_bytes','coordinate','curve','axis'))
def test_descriptor_pins_the_exact_caller_calibration_input_and_return_phase(tmp_path,field):
    row=output.descriptor(repo.ROOT)['reference'][0]
    text=(repo.ROOT/output.DESCRIPTOR).read_text();old=field+' = '+str(row[field]);assert old in text
    path=tmp_path/output.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text(text.replace(old,field+' = '+str(row[field]+1),1))
    with pytest.raises(ValueError):output.descriptor(tmp_path)


@pytest.mark.parametrize('fault',('other-link','L0-position','ledger-selector','ledger-order','width','signed','unit'))
def test_complete_proposed_native_owner_rejects_other_value_or_evidence_changes(tmp_path,fault):
    row=output.descriptor(repo.ROOT)['reference'][0];original=row['proposed_native_json'];changed=json.loads(original)
    if fault=='other-link':changed['link'][5]['to']='another/fn'
    elif fault=='L0-position':changed['symbol'][0]['evidence'].reverse()
    elif fault=='ledger-selector':changed['ledger'][0]['dependency'].pop()
    elif fault=='ledger-order':changed['ledger'][0]['fields'].reverse()
    elif fault=='width':changed['symbol'][0]['width']=8
    elif fault=='signed':changed['symbol'][0]['signed']=False
    else:changed['unit']='invalid-result-unit'
    changed=json.dumps(changed,sort_keys=True,separators=(',',':'))
    text=(repo.ROOT/output.DESCRIPTOR).read_text();path=tmp_path/output.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text(text.replace(json.dumps(original),json.dumps(changed),1))
    with pytest.raises(ValueError):output.descriptor(tmp_path)


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['exhaust_cvtc_transition_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original CVTC result')
        pytest.skip('the complete original CVTC result is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_cvtc_accesses'] is result['exact_cvtc_gain_output'] is True
    declared=packet['declaration'];actual=proof.observations(packet,declared)
    image=repo.images()['JK08A'].path.read_bytes();selected=[]
    for coordinate,curve in ((50,0),(170,0),(121,1),(121,2)):
        case=next(row for row in declared['cases'] if row['entry']==0xC1DEC and row['kind']=='curve-boundary'
            and row['coordinate']==coordinate and row['curve_kind']==curve)
        observed=actual[case['index']];state,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        selected.append((observed,state,value))
    return model,record,result,selected


def test_actual_output_changes_for_coordinate_and_curve_with_all_other_complete_inputs_fixed(original):
    model,_,_,selected=original
    proof.require_gain_output(model,[row[0] for row in selected],[row[2] for row in selected])
    for observed,state,value in selected:
        proof.require_gain_transfer(observed,state,value)
        assert observed['memory_after'][0][0x143A]==value['curve']['value']
    assert selected[0][0]['memory_after'][0][0x143A]!=selected[1][0]['memory_after'][0][0x143A]
    assert selected[2][0]['memory_after'][0][0x143A]!=selected[3][0]['memory_after'][0][0x143A]


@pytest.mark.parametrize('fault',('return-R0','extended-R6','return-SP','return-PR','return-GBR',
    'store-R6','store-site','store-width','store-register','store-byte','omit-return','omit-store','actual143A'))
def test_actual_return_extension_and_exact_published_byte_have_separate_refusals(original,fault):
    observed,state,value=deepcopy(original[3][2])
    returned=next(row for row in state['trace'] if row['site']==0xC1ED8)
    stored=next(row for row in state['trace'] if row['site']==0xC1EE2)
    if fault in ('return-R0','extended-R6','return-SP','store-R6'):
        node=returned['after'] if fault=='extended-R6' else stored['before'] if fault=='store-R6' else returned['before']
        registers=list(node['registers']);index={'return-R0':0,'extended-R6':6,'return-SP':15,'store-R6':6}[fault]
        registers[index]^=1;node['registers']=tuple(registers)
    elif fault=='return-PR':returned['before']['pr']+=2
    elif fault=='return-GBR':returned['before']['gbr']^=4
    elif fault=='store-site':stored['site']+=2
    elif fault=='store-width':stored['accesses'][0]['width_bytes']=2
    elif fault=='store-register':stored['accesses'][0]['register']=0
    elif fault=='store-byte':stored['accesses'][0]['bytes']='ff'
    elif fault=='omit-return':state['trace'].remove(returned)
    elif fault=='omit-store':state['trace'].remove(stored)
    else:
        memory=bytearray(observed['memory_after'][0]);memory[0x143A]^=1;observed['memory_after']=(bytes(memory),)
    with pytest.raises(ValueError):proof.require_gain_transfer(observed,state,value)


@pytest.mark.parametrize('fault',('unchanged-output','changed-context','missing-curve-pair','missing-coordinate-pair'))
def test_actual_positive_guard_refuses_retained_bytes_and_nonfixed_other_inputs(original,fault):
    selected=deepcopy(original[3])
    if fault=='missing-curve-pair':selected=selected[:2]
    elif fault=='missing-coordinate-pair':selected=selected[2:]
    else:
        for index,(observed,state,value) in enumerate(selected):
            if fault=='unchanged-output':
                memory=bytearray(observed['memory_after'][0]);memory[0x143A]=0;observed['memory_after']=(bytes(memory),)
            else:
                context=list(observed['context']);context[0]^=index+1;observed['context']=tuple(context)
    with pytest.raises(ValueError):proof.require_gain_output(original[0],[row[0] for row in selected],[row[2] for row in selected])


@pytest.mark.parametrize('flag',(None,False,1))
def test_calculation_family_requires_its_distinct_output_flag_after_complete_raw_access_admission(original,monkeypatch,flag):
    model,record,result,_=original;component=deepcopy(result);component['exact_cvtc_gain_output']=flag
    monkeypatch.setattr(proof,'require_witness',lambda *args,**kwargs:deepcopy(component))
    with pytest.raises(ValueError):owning.require_primary(model,record,family=output.FAMILY)


@pytest.mark.parametrize('field,value',(('width',8),('signed',False)))
@pytest.mark.parametrize('side',('symbol','meaning'))
def test_calculation_owner_refuses_promotion_of_unset_semantic_types(original,field,value,side):
    model=deepcopy(original[0]);symbol=model.symbols[calculation.SymbolKey('7mfk','ram',0xFFFF143A)]
    target=symbol if side=='symbol' else symbol.meaning;target.props[field]=value
    with pytest.raises(ValueError):owning.native_rows(model)


def test_published_result_counts_and_identities_read_the_executed_contract():
    text=(repo.ROOT/'defs/JK08A.cvtc-gain-output.md').read_text();row=output.descriptor(repo.ROOT)['reference'][0]
    assert 'contains one exact original' in text and len(output.descriptor(repo.ROOT)['reference'])==1
    assert '38 dispositions' in text and len(calculation.rows(repo.ROOT))==38
    for field in ('address','caller','callsite','delay_slot','returned_site','store_site'):
        assert f'{row[field]:08X}' in text
