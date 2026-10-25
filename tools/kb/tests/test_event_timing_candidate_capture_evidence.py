"""Actual published/live R6 quantity, complete-state and causal refusal sources."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import event_timing_candidate_contract as contract,event_timing_candidate_matrix as matrix
from kb import event_timing_candidate_semantics as numeric,event_timing_candidate_transfers as transfers
from kb import event_timing_candidate_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-event-refusal');value.update(updates);return value

def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);cal=matrix.calibrations(source,image,value)
    memory=matrix.memory(value);context=matrix.context(source,value);sp=0x30000000;continuation=0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    independent=numeric.evaluate(memory,cal)
    bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        bound_before=bound,bound_after=bound,
        memory_before=(memory,),memory_after=(result['ram'],),frame_before=bytes(frame),frame_after=result['frame'],
        calibration_before=cal,calibration_after=cal,sr_before=context[18],abi_before=tuple(range(12)),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,independent,fixture)
    return observed,result,independent,fixture

@pytest.mark.parametrize('raw',(0,1,127,128,255,256,32767,65535))
def test_actual_word_candidate_is_published_and_consumed_live(raw):
    observed,result,value,fixture=reconstructed(source_words=[raw]*9)
    memory=observed['memory_after'][0]
    assert int.from_bytes(memory[0x2000:0x2002],'big')==value['candidate']==raw
    assert int.from_bytes(memory[0x1FF6:0x1FF8],'big')==value['scaled']==raw
    assert memory[0x12D6]==value['value']==(-min(128,raw))&255
    assert not any(r['mode']=='read' and r['address']==matrix.RAM_BASE+0x2000 for r in result['accesses'])

@pytest.mark.parametrize('updates',(dict(byte_24c5=32,byte_11fa=128,byte_22fa=255,word_23c2=65535),
    dict(rom_8710=0,byte_24cb=4,byte_11f9=255,byte_22fa=127),
    dict(source_axis=[0,65535,0,32768,32767,1,65534,65535],word_237e=32768),
    dict(source_words=[65535]*9,rom_8a3c=255,byte_2459=32),
    dict(rom_8290=1,byte_24c0=64,prior_1ff8=1,byte_229d=0),
    dict(rom_8290=1,byte_24c0=64,prior_1ff8=0xFFFFFFFF,byte_229d=0),
    dict(rom_8290=255,byte_24c2=1,byte_2378=128),
    dict(byte_40e7=255,byte_11f9=128,byte_2356=127),
    dict(byte_24cc=2,byte_2378=128)))
def test_complete_knock_axis_coefficient_slew_and_override_paths(updates):
    reconstructed(**updates)

@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width','live-R6','output-register',
    'return-delay','saved-GBR','helper-argument','fake-prior-read','opcode'))
def test_matching_bytes_cannot_replace_full_state_or_live_R6(fault):
    observed,result,value,fixture=reconstructed()
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x100,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x4DA90)['width_bytes']=1
    elif fault in ('live-R6','output-register'):
        row=next(r for r in result['trace'] if r['site']==(0x4DAB8 if fault=='live-R6' else 0x4DB8C))
        registers=list(row['before']['registers']);registers[6]^=0x10000;row['before']['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-GBR':next(r for r in result['accesses'] if r['site']==0x4D9A6)['address']+=4
    elif fault=='helper-argument':
        call=result['calls'][-1];registers=list(call['entry']['registers']);registers[0]=101;call['entry']['registers']=tuple(registers)
    elif fault=='fake-prior-read':next(r for r in result['accesses'] if r['site']==0x4DA92)['address']=matrix.RAM_BASE+0x2000
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

def causal_pairs(**updates):
    pairs=[]
    for index in range(8):
        for raw in (0,1):
            words=[0]*9;words[index]=raw
            observed,result,value,fixture=reconstructed(source_words=words,word_237e=index*8192,**updates)
            pairs.append((observed,value))
    return pairs

def test_every_active_word_needs_changed_actual_candidate_scaled_and_final_output():
    assert proof.require_causal_alternatives(causal_pairs())=={f'active-word-{i}':True for i in range(8)}
    with pytest.raises(ValueError):proof.require_causal_alternatives(causal_pairs(byte_24cc=2))
    pairs=causal_pairs()
    for observed,value in pairs:
        raw=bytearray(observed['memory_after'][0]);raw[0x12D6]=0;observed['memory_after']=(bytes(raw),);value['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)

def test_overwritten_prior_word_is_an_independent_full_state_control():
    pairs=[]
    for prior in (0,1,127,128,255,32768,65535):
        observed,result,value,fixture=reconstructed(prior_2000=prior);pairs.append((observed,value))
    assert proof.require_prior_invariance(pairs) is True
    raw=bytearray(pairs[-1][0]['memory_after'][0]);raw[0x88]^=1;pairs[-1][0]['memory_after']=(bytes(raw),)
    with pytest.raises(ValueError):proof.require_prior_invariance(pairs)

def test_ninth_word_is_physically_read_with_zero_arithmetic_weight():
    pairs=[]
    for word in (0,1,127,32768,65535):
        observed,result,value,fixture=reconstructed(source_words=[0]*8+[word],word_237e=57344)
        pairs.append((observed,value))
    assert proof.require_ninth_word_invariance(pairs) is True
    next(r for r in pairs[-1][1]['operands'] if r['site']==0x264DE)['width_bytes']=1
    with pytest.raises(ValueError):proof.require_ninth_word_invariance(pairs)
