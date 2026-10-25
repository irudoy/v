"""Actual published/live timing additive R6/R2 quantity, complete-state and causal refusal sources."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import timing_additive_candidate_contract as contract,timing_additive_candidate_matrix as matrix
from kb import timing_additive_candidate_semantics as numeric,timing_additive_candidate_transfers as transfers
from kb import timing_additive_candidate_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-additive-refusal');value.update(updates);return value

def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);cal=matrix.calibrations(source,image,value)
    memory=matrix.memory(value);context=matrix.context(source,value);sp=0x30000000;continuation=0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    independent=numeric.evaluate(memory,cal,bytes(frame))
    bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        bound_before=bound,bound_after=bound,
        memory_before=(memory,),memory_after=(result['ram'],),frame_before=bytes(frame),frame_after=result['frame'],
        calibration_before=cal,calibration_after=cal,sr_before=context[18],abi_before=tuple(range(12)),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,independent,fixture)
    return observed,result,independent,fixture

@pytest.mark.parametrize('raw',(0,1,127,128,255,256,32767,32768,65535))
def test_actual_additive_is_published_and_used_by_complete_live_registers(raw):
    observed,result,value,fixture=reconstructed(source_surface=[raw]*64)
    candidate=min(255,min(255,raw)*65535*255//500000)
    memory=observed['memory_after'][0]
    assert memory[0x134A]==memory[0x12D4]==value['candidate']==candidate
    assert memory[0x1830]==value['value']==min(127,candidate)
    assert not any(r['mode']=='read' and r['address']==matrix.RAM_BASE+0x134A for r in result['accesses'])

@pytest.mark.parametrize('updates',(dict(word_1024=65535,word_10ca=65535),
    dict(word_1024=1,word_10ca=0),dict(word_1024=0,word_10ca=1),dict(word_1024=1,word_10ca=1),
    dict(source_outer_axis=[0,65535,0,32768,32767,1,65534,65535],word_10ca=32768),
    dict(source_inner_axis=[65535]*8,word_1024=0),dict(byte_2458=32,byte_23ee=128),
    dict(byte_41ab=0,prior_134a=255),dict(word_28b8=7349),dict(word_28ba=7349),
    dict(byte_23bd=255,byte_23f1=127,byte_1a7d=255),
    dict(byte_23c5=255,byte_23f1=128,byte_15ea=255)))
def test_full_kernel_fraction_activation_and_compositor_branches(updates):
    reconstructed(**updates)

@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width','live-R6','live-R2',
    'output-register','return-delay','saved-GBR','carrier-high16','incoming-carrier-high16',
    'local-word-width','helper-argument','fake-prior-read','opcode'))
def test_matching_bytes_cannot_replace_full_state_local_carrier_or_live_registers(fault):
    observed,result,value,fixture=reconstructed()
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x100,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x4BE92)['width_bytes']=2
    elif fault in ('live-R6','live-R2','output-register'):
        site,register={'live-R6':(0x4BE96,6),'live-R2':(0x4BEA2,2),'output-register':(0x4BEE2,2)}[fault]
        row=next(r for r in result['trace'] if r['site']==site)
        registers=list(row['before']['registers']);registers[register]^=0x10000;row['before']['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-GBR':next(r for r in result['accesses'] if r['site']==0x4BDCA)['address']+=4
    elif fault=='carrier-high16':
        row=next(r for r in result['trace'] if r['site']==0x26286)
        registers=list(row['after']['registers']);registers[5]^=0x10000;row['after']['registers']=tuple(registers)
    elif fault=='incoming-carrier-high16':
        frame=bytearray(observed['frame_before']);frame[136]^=1;observed['frame_before']=bytes(frame)
    elif fault=='local-word-width':next(r for r in result['accesses'] if r['site']==0x4BE48)['width_bytes']=4
    elif fault=='helper-argument':
        call=result['calls'][-1];registers=list(call['entry']['registers']);registers[0]=500001;call['entry']['registers']=tuple(registers)
    elif fault=='fake-prior-read':next(r for r in result['accesses'] if r['site']==0x4BE70)['address']=matrix.RAM_BASE+0x134A
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

def causal_pairs(**updates):
    pairs=[]
    for index in range(64):
        for raw in (0,1):
            surface=[0]*64;surface[index]=raw
            observed,result,value,fixture=reconstructed(source_surface=surface,word_10ca=(index//8)*8192,
                word_1024=(index%8)*8192,**updates);pairs.append((observed,value))
    for index in range(8):
        for raw in (0,1):
            curve=[0]*9;curve[index]=raw
            observed,result,value,fixture=reconstructed(source_curve=curve,source_surface=[255]*64,
                byte_106f=index*32,**updates);pairs.append((observed,value))
    return pairs

def test_all_surface_words_and_active_curve_bytes_need_actual_causal_publications():
    wanted={f'surface-word-{i}':True for i in range(64)}|{f'curve-byte-{i}':True for i in range(8)}
    assert proof.require_causal_alternatives(causal_pairs())==wanted
    with pytest.raises(ValueError):proof.require_causal_alternatives(causal_pairs(byte_41ab=0))
    pairs=causal_pairs()
    for observed,value in pairs:
        raw=bytearray(observed['memory_after'][0]);raw[0x1830]=0;observed['memory_after']=(bytes(raw),);value['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)

def test_active_overwritten_prior_and_both_inactive_prior_boundaries():
    active=[];inactive=[]
    for prior in (0,1,127,128,255):
        observed,result,value,fixture=reconstructed(prior_134a=prior);active.append((observed,value))
        for updates in (dict(byte_41ab=0),dict(byte_2458=32)):
            observed,result,value,fixture=reconstructed(prior_134a=prior,**updates);inactive.append((observed,value))
    assert proof.require_prior_invariance(active) is True
    assert proof.require_disabled_prior_invariance(inactive)==dict(alternate=True,disabled=True)
    raw=bytearray(active[-1][0]['memory_after'][0]);raw[0x88]^=1;active[-1][0]['memory_after']=(bytes(raw),)
    with pytest.raises(ValueError):proof.require_prior_invariance(active)
    raw=bytearray(inactive[-1][0]['memory_after'][0]);raw[0x134A]^=1;inactive[-1][0]['memory_after']=(bytes(raw),)
    with pytest.raises(ValueError):proof.require_disabled_prior_invariance(inactive)

def test_ninth_byte_is_physically_read_with_zero_arithmetic_weight():
    pairs=[]
    for byte in (0,1,127,128,255):
        observed,result,value,fixture=reconstructed(source_curve=[0]*8+[byte],byte_106f=224)
        pairs.append((observed,value))
    assert proof.require_ninth_byte_invariance(pairs) is True
    next(r for r in pairs[-1][1]['operands'] if r['site']==0x26486)['width_bytes']=2
    with pytest.raises(ValueError):proof.require_ninth_byte_invariance(pairs)
