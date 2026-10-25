"""Actual paired words, full RAM continuity, physical stores and complete CPU refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import transmission_candidate_boundary_contract as contract
from kb import transmission_candidate_boundary_matrix as matrix
from kb import transmission_candidate_boundary_semantics as numeric
from kb import transmission_candidate_boundary_transfers as transfers
from kb import transmission_candidate_boundary_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-pair-unit-refusal')
    value.update(updates);return value

def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);cal=matrix.calibrations(source,image,value)
    bound=b''.join(fixture[row['address']:row['address']+row['size']] for row in contract.BOUND_SPANS)
    memory=matrix.memory(value);rows=[]
    for phase in (0,1):
        context=matrix.context(source,value,phase);sp=0x30000000+phase*0x2000;continuation=0x30010000+phase*0x2000
        frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
        frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
        frame[184:188]=continuation.to_bytes(4,'big')
        result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRIES[phase],context[18],trace=True)
        independent=numeric.evaluate(phase,memory,cal)
        observed=dict(pair=0,phase=phase,phase_id=contract.PHASES[phase],entry=contract.ENTRIES[phase],context=context,
            sp=sp,continuation=continuation,memory_before=(memory,),memory_after=(result['ram'],),
            calibration_before=cal,calibration_after=cal,bound_before=bound,bound_after=bound,
            frame_before=bytes(frame),frame_after=result['frame'],sr_before=context[18],abi_before=tuple(range(12)),
            exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
        transfers.require(observed,result,independent,fixture);rows.append((observed,result,independent))
        memory=result['ram']
    transfers.require_handoff(rows[0][0],rows[1][0],rows[0][2],rows[1][2])
    return rows,fixture

@pytest.mark.parametrize('raw',(0,1,127,128,255,256,32767,32768,32769,65535))
def test_signed_source_word_reaches_the_actual_final_word_with_full_RAM_continuity(raw):
    rows,fixture=reconstructed(word_4162=raw)
    first,last=rows[0][0],rows[1][0]
    assert first['memory_after']==last['memory_before']
    assert last['memory_after'][0][0x19C6:0x19C8]==raw.to_bytes(2,'big')
    assert rows[0][2]['candidate']==(raw-65536 if raw&32768 else raw)

@pytest.mark.parametrize('updates',(dict(rom_83c1=1),dict(byte_41a6=0,rom_89c5=0),
    dict(rom_89c5=0),dict(rom_8b38=3),dict(word_4138=32768,word_413a=32767)))
def test_full_bypass_mode_and_unordered_signed_limit_paths(updates):
    reconstructed(**updates)

@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width','store-register','return-delay','stack-word','special-register','opcode'))
def test_matching_final_word_cannot_replace_complete_physical_or_CPU_evidence(fault):
    rows,fixture=reconstructed();observed,result,value=rows[0]
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x77840)['width_bytes']=1
    elif fault=='store-register':
        row=next(r for r in result['trace'] if r['site']==0x77866);registers=list(row['before']['registers']);registers[13]^=0x10000;row['before']['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='stack-word':next(r for r in result['accesses'] if r['domain']=='frame')['address']+=4
    elif fault=='special-register':result['gbr']^=1
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

@pytest.mark.parametrize('fault',('RAM','calibration','bound','phase','pair','carried-word'))
def test_handoff_rejects_detached_or_reseeded_complete_actual_state(fault):
    rows,fixture=reconstructed();first,last=rows[0][0],rows[1][0];pvalue,cvalue=rows[0][2],rows[1][2]
    if fault=='RAM':
        raw=bytearray(last['memory_before'][0]);raw[0x88]^=1;last['memory_before']=(bytes(raw),)
    elif fault=='calibration':last['calibration_before']={**last['calibration_before'],0x83C1:b'\x01'}
    elif fault=='bound':last['bound_before']=b'\x01'+last['bound_before'][1:]
    elif fault=='phase':last['phase']=0
    elif fault=='pair':last['pair']=1
    else:next(row for row in cvalue['operands'] if row['site']==0x7914E)['bytes']='0000'
    with pytest.raises(ValueError):transfers.require_handoff(first,last,pvalue,cvalue)

def test_actual_causal_group_rejects_bypass_input_echo_and_accepts_carried_words():
    pairs=[]
    for raw in (0,1000):
        rows,fixture=reconstructed(word_4162=raw)
        pairs.append((rows[0][0],rows[1][0],rows[0][2],rows[1][2]))
    assert proof.require_causal_alternatives(pairs)=={'native-signed-candidate':True}
    pairs=[]
    for raw in (0,1000):
        rows,fixture=reconstructed(word_4162=raw,rom_83c1=1)
        pairs.append((rows[0][0],rows[1][0],rows[0][2],rows[1][2]))
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)


def test_source_mask_preserves_other_RAM_and_both_complete_phase_contexts():
    rows,fixture=reconstructed();first,last=rows[0][0],rows[1][0]
    baseline=proof.held_key(first,last,0x01004162,2,'ram')[0]
    changed=deepcopy(first);raw=bytearray(changed['memory_before'][0]);raw[0x4162]^=1
    changed['memory_before']=(bytes(raw),)
    assert proof.held_key(changed,last,0x01004162,2,'ram')[0]==baseline
    different=deepcopy(last);context=list(different['context']);context[0]^=1;different['context']=tuple(context)
    assert proof.held_key(changed,different,0x01004162,2,'ram')[0]!=baseline
