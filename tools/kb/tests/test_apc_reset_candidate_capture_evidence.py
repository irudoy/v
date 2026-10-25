"""Actual published/live R5 quantity, complete-state and causal refusal sources."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import apc_reset_candidate_contract as contract,apc_reset_candidate_matrix as matrix
from kb import apc_reset_candidate_semantics as numeric,apc_reset_candidate_transfers as transfers
from kb import apc_reset_candidate_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-APC-refusal');value.update(updates);return value

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

@pytest.mark.parametrize('raw',(0,1,2,127,128,254,255))
def test_actual_curve_candidate_is_published_and_consumed_live(raw):
    observed,result,value,fixture=reconstructed(source_curves=[raw]*8+[255]*8,rom_8b87=255,rom_8b88=255)
    wanted=min(255,450*raw*255//0x14000)
    assert observed['memory_after'][0][0x1875]==observed['memory_after'][0][0x2406]==wanted
    assert value['candidate']==value['selected']==wanted
    assert not any(r['mode']=='read' and r['address']==matrix.RAM_BASE+0x1875 for r in result['accesses'])

@pytest.mark.parametrize('updates',(dict(byte_4184=64,word_10ca=65535),dict(byte_1108=0,rom_8525=0),
    dict(byte_4184=64,byte_1108=1,rom_959a=65535,rom_8521=255,rom_8524=255),
    dict(rom_8522=0,rom_8523=255),dict(rom_8b87=0,rom_8b88=255),dict(byte_4251=1)))
def test_complete_modes_zero_speed_wrapped_products_and_diagnostic_override(updates):
    reconstructed(**updates)

@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width','live-R5','output-register','return-delay','saved-word','helper-argument','fake-prior-read','opcode'))
def test_matching_publication_bytes_cannot_replace_complete_state_or_live_R5(fault):
    observed,result,value,fixture=reconstructed()
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x100,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x4C36C)['width_bytes']=2
    elif fault in ('live-R5','output-register'):
        row=next(r for r in result['trace'] if r['site']==(0x4C374 if fault=='live-R5' else 0x4C380))
        registers=list(row['before']['registers']);registers[5 if fault=='live-R5' else 6]^=0x10000;row['before']['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-word':next(r for r in result['accesses'] if r['domain']=='frame')['address']+=4
    elif fault=='helper-argument':
        call=result['calls'][-1];registers=list(call['entry']['registers']);registers[0]=0x14001;call['entry']['registers']=tuple(registers)
    elif fault=='fake-prior-read':
        next(r for r in result['accesses'] if r['site']==0x4C370)['address']=matrix.RAM_BASE+0x1875
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

def causal_pairs(**updates):
    pairs=[]
    for which in (0,1):
        for index in range(8):
            for raw in (0,1):
                values=[0]*8+[255]*8 if which==0 else [255]*8+[0]*8
                values[which*8+index]=raw
                observed,result,value,fixture=reconstructed(source_curves=values,rom_8522=255,rom_8523=0,
                    rom_8525=0,rom_8b87=255,rom_8b88=255,byte_11ae=index*32 if which==0 else 32,
                    byte_1108=32 if which==0 else index*32,**updates)
                pairs.append((observed,value))
    return pairs

def test_every_source_cell_needs_changed_actual_candidate_and_final_output():
    assert proof.require_causal_alternatives(causal_pairs())=={f'curve-cell-{i}':True for i in range(16)}
    with pytest.raises(ValueError):proof.require_causal_alternatives(causal_pairs(byte_4251=1))
    pairs=causal_pairs()
    for observed,value in pairs:
        raw=bytearray(observed['memory_after'][0]);raw[0x2406]=24;observed['memory_after']=(bytes(raw),);value['value']=24
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)

def test_overwritten_prior_byte_is_an_independent_complete_state_control():
    pairs=[]
    for prior in (0,1,127,128,255):
        observed,result,value,fixture=reconstructed(prior_1875=prior);pairs.append((observed,value))
    assert proof.require_prior_invariance(pairs) is True
    raw=bytearray(pairs[-1][0]['memory_after'][0]);raw[0x88]^=1;pairs[-1][0]['memory_after']=(bytes(raw),)
    with pytest.raises(ValueError):proof.require_prior_invariance(pairs)
