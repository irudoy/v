"""Independent signed bounds, complete raw transport and real-state refusal controls."""
from copy import deepcopy
import json
import pytest
from kb import repo,byte_surface_equations as state
from kb import request_boundary_publication_contract as contract,request_boundary_publication_matrix as matrix
from kb import request_boundary_publication_semantics as numeric,request_boundary_publication_transfers as transfers
from kb import request_boundary_publication_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-refusal');value.update(updates);return value

def equations(value):return numeric.caller(matrix.memory(value),matrix.input_calibrations(value))

def isolated(**updates):
    profile=dict(word_2438=2000,word_19c2=3000,word_34ca=(-1000)&65535,
        word_34b8=32767,word_34ba=32767,word_34b4=32767,word_3484=32768,
        word_3480=32767,word_413a=32768,word_4138=32767,word_349a=32768,mode_8b38=0,mode_83c1=1)
    profile.update(updates);return case(**profile)

def test_actual_two_store_choices_use_transformed_registers_and_the_independent_cap():
    direct=equations(isolated(word_3480=100,word_349a=1000))
    capped=equations(isolated(word_3480=100,word_349a=1000,mode_83c1=0))
    assert (direct['value'],capped['value'])==(100,1000)
    assert (direct['publication_site'],direct['publication_register'])==(0x791A8,13)
    assert (capped['publication_site'],capped['publication_register'])==(0x791B2,7)
    for poison in (0,1,32767,32768,65535):
        assert equations(isolated(word_3480=100,word_349a=1000,word_19c6=poison))['value']==100

def test_reversed_limits_retain_different_ordered_signed_word_publications():
    value=equations(isolated(word_413a=2000,word_4138=(-200)&65535))
    assert value['signed_value']==-200 and value['value']==0xFF38
    assert value['memory'][0x415E:0x4162]==bytes.fromhex('07d007d0')
    writes=[row for row in value['operands'] if row['site']==0x791A8]
    assert writes==[dict(site=0x791A8,mode='write',address=0x010019C6,width_bytes=2,register=13,domain='ram',bytes='ff38')]

def test_nonpositive_offset_is_an_actual_mode_controlled_transformation():
    off=equations(isolated(word_2438=(-2000)&65535,mode_8b38=0))
    on=equations(isolated(word_2438=(-2000)&65535,mode_8b38=1))
    assert (off['signed_value'],on['signed_value'])==(-2000,-1000)
    assert equations(isolated(word_2438=(-2000)&65535,word_34ca=1000,mode_8b38=1))['signed_value']==0

def test_complete_first_stages_keep_real_byte_clamp_division_and_counter_reset():
    value=equations(case(mode_8b38=2))
    assert value['retained']==42 and value['correction']==18
    assert value['memory'][0x186B]==42 and value['memory'][0x336B]==18
    value=equations(case(mode_8b38=2,byte_1864=255,byte_186b=0))
    assert value['retained']==255 and value['correction']==0
    profile=dict(byte_4184=128,byte_244f=32,byte_41e1=1,word_3446=20,byte_3448=7,byte_2ec3=3)
    value=equations(case(**profile))
    assert value['first_grid']['value']==15 and value['second_grid']['value']==25
    assert value['threshold']==25 and value['counter']==21 and value['active'] is False
    assert value['memory'][0x3446:0x3449]==bytes.fromhex('001507')
    value=equations(case(**dict(profile,grid_aaea=[0]*16)))
    assert value['threshold']==10 and value['active'] is True
    assert value['memory'][0x3446:0x3449]==bytes(3) and not value['memory'][0x41E1]&1

def test_actual_byte_endpoint_return_sign_extension_precedes_caller_EXTU_B():
    source=case(byte_106f=240,curve_12e1a=[255]*16);value=equations(source)
    calls=numeric.call_values(matrix.memory(source),matrix.input_calibrations(source),value)
    assert calls[0x793F2]['returned'][0]==0xFFFFFFFF
    assert calls[0x79420]['arguments'][5]==255+24

def causal_observation(source):
    value=equations(source)
    return dict(entry=contract.ENTRY,context=matrix.context({},source),memory_before=(matrix.memory(source),),
        memory_after=(value['memory'],),calibration_before=matrix.input_calibrations(source),
        bound_before=bytes(sum(row['size'] for row in contract.BOUND_SPANS)),
        frame_before=bytes(192),sp=0x30000000,continuation=0x30010000,abi_before=tuple(range(12)),sr_before=0),value

@pytest.mark.parametrize('fault',('unrelated-RAM','other-calibration','context','frame','bound','SP','scalar-only'))
def test_causal_alternatives_require_every_other_complete_input_and_actual_word_bytes(monkeypatch,fault):
    monkeypatch.setattr(proof,'CAUSAL_INPUTS',(('ram',0x01002438,2,'selected-request'),))
    first=causal_observation(isolated(word_2438=100));second=causal_observation(isolated(word_2438=200))
    assert proof.require_causal_alternatives([first,second])=={'selected-request':True}
    observed,value=second
    if fault=='unrelated-RAM':
        raw=bytearray(observed['memory_before'][0]);raw[0x88]^=1;observed['memory_before']=(bytes(raw),)
    elif fault=='other-calibration':observed['calibration_before'][0x8423]=b'\x00'
    elif fault=='context':observed['context']=(observed['context'][0]^1,*observed['context'][1:])
    elif fault=='frame':observed['frame_before']=b'\x01'+observed['frame_before'][1:]
    elif fault=='bound':observed['bound_before']=b'\x01'+observed['bound_before'][1:]
    elif fault=='SP':observed['sp']+=4
    else:value['value']^=1
    with pytest.raises(ValueError):proof.require_causal_alternatives([first,second])

def raw_packet():
    declared=dict(cases=[case()],calibration_spans=[[row['address'],row['size']] for row in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[row['address'],row['size']] for row in contract.BOUND_SPANS])
    context=b''.join(value.to_bytes(4,'big') for value in matrix.context({},case())).hex()
    row=dict(schema=1,index=0,entry=contract.ENTRY,context=context,context_after=context,
        observation=bytes(572).hex(),ram_before='65536:a5',ram_after='65536:a5',
        calibration_before=bytes(sum(size for at,size in declared['calibration_spans'])).hex(),
        calibration_after=bytes(sum(size for at,size in declared['calibration_spans'])).hex(),
        bound_before=bytes(sum(size for at,size in declared['bound_spans'])).hex(),
        bound_after=bytes(sum(size for at,size in declared['bound_spans'])).hex())
    marker=proof.MARKER+' status=PASS region='+proof.REGION+' cases=1'
    packet=dict(observations=[deepcopy(row)],marker=marker,stdout=proof.PREFIX+json.dumps(row)+'\n'+marker)
    return declared,row,packet

@pytest.mark.parametrize('fault',('missing','extra','wrong-index','wrong-entry','context','duplicate-key','short-bound'))
def test_complete_stream_refuses_detached_identity_context_or_bound_snapshots(fault):
    declared,row,packet=raw_packet();assert len(proof.observations(packet,declared))==1
    if fault=='wrong-index':row['index']=1
    elif fault=='wrong-entry':row['entry']=0x79030
    elif fault=='context':row['context_after']=bytes(80).hex()
    elif fault=='short-bound':row['bound_after']='00'
    rows=[] if fault=='missing' else [row,row] if fault=='extra' else [row]
    packet['observations']=deepcopy(rows)
    packet['stdout']='\n'.join([*(proof.PREFIX+json.dumps(value) for value in rows),packet['marker']])
    if fault=='duplicate-key':packet['stdout']=packet['stdout'].replace('"schema": 1','"schema": 1, "schema": 1',1)
    with pytest.raises(ValueError):proof.observations(packet,declared)

def reconstructed():
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT);value=case()
    fixture,_=contract.fixture_for_case(source,image,value);context=matrix.context(source,value)
    sp,continuation=0x30000000,0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+index*17).to_bytes(4,'big') for index in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    before=matrix.memory(value);cal=matrix.calibrations(source,image,value)
    result=state.execute(source,fixture,context,before,bytes(frame),sp,continuation,contract.ENTRY,0,trace=True)
    observed=dict(context=context,sp=sp,continuation=continuation,memory_before=(before,),calibration_before=cal,
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        frame_after=result['frame'],memory_after=(result['ram'],),sr_before=0)
    return observed,result,numeric.caller(before,cal),fixture

@pytest.mark.parametrize('fault',('exit-SR','frame-byte','RAM-byte','actual-call-argument','returned-PR','physical-width','delay-slot','live-register','scalar-only'))
def test_matching_final_word_does_not_replace_complete_CPU_frame_physical_and_call_state(fault):
    observed,result,value,fixture=reconstructed();transfers.require(observed,result,value,fixture)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
    elif fault=='frame-byte':raw=bytearray(observed['frame_after']);raw[0]^=1;observed['frame_after']=bytes(raw)
    elif fault=='RAM-byte':raw=bytearray(observed['memory_after'][0]);raw[0]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='actual-call-argument':
        call=next(row for row in result['calls'] if row['site']==0x793F2)
        raw=list(call['entry']['registers']);raw[4]^=1;call['entry']['registers']=tuple(raw)
    elif fault=='returned-PR':result['pr']^=2
    elif fault=='physical-width':next(row for row in result['accesses'] if row['site']==value['publication_site'])['width_bytes']=1
    elif fault=='delay-slot':next(row for row in result['trace'] if row['site']==0x79DE2)['delay_slot']=False
    elif fault=='live-register':value['signed_value']^=0x10000
    else:value['value']^=1
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)
