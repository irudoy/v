"""Actual signed loads, delay arguments, complete caller transfers and causal refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import engine_speed_curve_input_contract as contract,engine_speed_curve_input_matrix as matrix
from kb import engine_speed_curve_input_semantics as numeric,engine_speed_curve_input_transfers as transfers
from kb import engine_speed_curve_input_capture_evidence as proof


def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-speed-coordinate-refusal')
    value.update(updates);return value


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
        bound_before=bound,bound_after=bound,memory_before=(memory,),memory_after=(result['ram'],),
        frame_before=bytes(frame),frame_after=result['frame'],calibration_before=cal,calibration_after=cal,
        sr_before=context[18],abi_before=tuple(range(12)),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,independent,fixture)
    return observed,result,independent,fixture


@pytest.mark.parametrize('snapshot',(0,1,31,32,127,128,223,224,225,255))
@pytest.mark.parametrize('branch',('first','second','third'))
def test_actual_snapshot_reaches_post_delay_R5_and_both_publications(snapshot,branch):
    mode=dict(matrix.SPEED_MODES)[branch]
    observed,result,value,fixture=reconstructed(speed_snapshot=snapshot,**mode)
    assert value['speed_branch']==branch and value['speed_coordinate']==snapshot
    assert observed['memory_after'][0][0x1511]==value['speed_register']&255
    assert observed['memory_after'][0][0x23EE]==value['value']
    load,call={'first':(0x4B054,0x4B058),'second':(0x4B08A,0x4B08E),'third':(0x4B0B4,0x4B0B8)}[branch]
    trace={r['site']:r for r in result['trace']}
    assert trace[load]['after']['registers'][2]==(snapshot-256 if snapshot&128 else snapshot)&0xFFFFFFFF
    assert trace[call+2]['after']['registers'][5]==snapshot


@pytest.mark.parametrize('updates',(
    dict(byte_41de=32,byte_1071=255,rom_86a4=255),
    dict(byte_2458=32,byte_1071=255,byte_2590=0),
    dict(rom_870b=1,word_2318=16384),
    dict(byte_244f=4,byte_22e1=3,byte_106f=255,correction_curves=[255]*32),
    dict(byte_244f=4,byte_42bc=1,correction_curves=[255]*32),
    dict(byte_244f=4,byte_106e=255,clock_15f8=50,rom_878a=255),
    dict(byte_106e=255,clock_15f8=50,rom_8789=255),
    dict(byte_106e=255,clock_15f8=0x80000000,rom_8789=255),
    dict(byte_248d=16,byte_1239=1,prior_1513=128,speed_curves=[0]*24),
    dict(byte_1239=1,byte_1277=0,prior_1513=127),
    dict(byte_24a7=2,byte_11ae=255,byte_2442=128,byte_2443=255,correction_surface=[255]*64),
    dict(byte_24a7=2,byte_11ae=1,byte_2442=1,byte_2443=33),
    dict(byte_24a7=2,surface_inner_axis=[255,128,0,1,128,0,254,255]),
    dict(byte_41ab=64,word_28b8=65535,word_28ba=65535,explicit_byte_curve=[255]*9,explicit_word_curve=[65535]*9),
    dict(byte_41ab=64,word_28b8=7350,word_28ba=65535,rom_9010=7350)))
def test_complete_corrections_surface_carriers_division_and_saturation_boundaries(updates):
    reconstructed(**updates)


@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width',
    'signed-R2','post-delay-R5','curve-return','centered-R2','final-R2','return-delay',
    'saved-GBR','carrier-high24','incoming-carrier-high24','local-byte-width',
    'helper-argument','helper-target','SR-full-read','SR-mask-restore','GBR-rebase','fake-snapshot-read','opcode'))
def test_matching_bytes_cannot_replace_complete_SR_frame_carriers_and_live_registers(fault):
    observed,result,value,fixture=reconstructed(speed_snapshot=255,byte_244f=4,byte_22e1=3,
        byte_24a7=2,byte_11ae=255,byte_2442=128,byte_2443=255,byte_106f=255)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x10,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x4B0B4)['width_bytes']=2
    elif fault in ('signed-R2','post-delay-R5','curve-return','centered-R2','final-R2','carrier-high24','SR-full-read'):
        site,phase,register={'signed-R2':(0x4B0B4,'after',2),'post-delay-R5':(0x4B0BA,'after',5),
            'curve-return':(0x4B0BE,'before',0),'centered-R2':(0x4B0D0,'before',2),
            'final-R2':(0x4B546,'before',2),'carrier-high24':(0x26156,'after',5),
            'SR-full-read':(0x4B2D4,'after',0)}[fault]
        row=next(r for r in result['trace'] if r['site']==site)
        registers=list(row[phase]['registers']);registers[register]^=0x10000;row[phase]['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-GBR':next(r for r in result['accesses'] if r['site']==0x4AFEC)['address']+=4
    elif fault=='incoming-carrier-high24':
        frame=bytearray(observed['frame_before']);frame[116]^=1;observed['frame_before']=bytes(frame)
    elif fault=='local-byte-width':next(r for r in result['accesses'] if r['site']==0x4B396)['width_bytes']=4
    elif fault=='helper-argument':
        call=result['calls'][0];registers=list(call['entry']['registers']);registers[5]^=0x10000
        call['entry']['registers']=tuple(registers)
    elif fault=='helper-target':result['calls'][0]['target']=0x26372
    elif fault=='SR-mask-restore':next(r for r in result['trace'] if r['site']==0x4B380)['after']['sr']^=0x100
    elif fault=='GBR-rebase':next(r for r in result['trace'] if r['site']==0x4AFF0)['after']['gbr']+=4
    elif fault=='fake-snapshot-read':next(r for r in result['accesses'] if r['site']==0x4B0B4)['address']+=1
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def causal_pairs():
    pairs=[]
    for branch in proof.CAUSAL_BRANCHES:
        for snapshot in (0,32):
            observed,result,value,fixture=reconstructed(speed_snapshot=snapshot,**dict(matrix.SPEED_MODES)[branch])
            pairs.append((observed,value))
    return pairs


def test_each_real_handoff_needs_changed_actual1511_and23EE_publications():
    assert proof.require_causal_alternatives(causal_pairs())==dict(first=True,second=True,third=True)
    pairs=causal_pairs()
    for observed,value in pairs:
        raw=bytearray(observed['memory_after'][0]);raw[0x23EE]=0
        observed['memory_after']=(bytes(raw),);value['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)
    with pytest.raises(ValueError):proof.require_causal_alternatives(causal_pairs()[:-2])


def test_substitute_does_not_consume_snapshot_and_preserves_complete_other_state():
    pairs=[]
    for snapshot in (0,1,127,128,255):
        observed,result,value,fixture=reconstructed(speed_snapshot=snapshot,**dict(matrix.SPEED_MODES)['substitute'])
        assert not any(r['mode']=='read' and r['address']==matrix.RAM_BASE+0x11B2 for r in result['accesses'])
        pairs.append((observed,value))
    assert proof.require_substitute_invariance(pairs) is True
    raw=bytearray(pairs[-1][0]['memory_after'][0]);raw[0x88]^=1;pairs[-1][0]['memory_after']=(bytes(raw),)
    with pytest.raises(ValueError):proof.require_substitute_invariance(pairs)


def test_overwritten_prior1511_has_no_effect_on_complete_final_state():
    pairs=[]
    for prior in (0,1,127,128,255):
        for branch in (*proof.CAUSAL_BRANCHES,'substitute'):
            observed,result,value,fixture=reconstructed(prior_1511=prior,**dict(matrix.SPEED_MODES)[branch])
            pairs.append((observed,value))
    assert proof.require_prior_publication_invariance(pairs) is True
    exit_state=pairs[-1][0]['exit'];pairs[-1][0]['exit']=(*exit_state[:-1],exit_state[-1]^1)
    with pytest.raises(ValueError):proof.require_prior_publication_invariance(pairs)


@pytest.mark.parametrize('sr',(0,1,0xF0,0x101,0x201,0x301,0x3F1))
def test_saved_interrupt_mask_is_restored_with_current_MQT(sr):
    context=list(matrix.DEFAULT_CONTEXT);context[18]=sr
    observed,result,value,fixture=reconstructed(context=context,byte_106e=255,clock_15f8=50,rom_8789=255)
    trace={r['site']:r for r in result['trace']}
    assert trace[0x4B2E6]['after']['sr']&0xF0==0xF0
    assert trace[0x4B380]['after']['sr']&0xF0==sr&0xF0
    assert trace[0x4B380]['after']['sr']&~0xF0==trace[0x4B378]['before']['sr']&~0xF0
