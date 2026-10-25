"""Actual paired words, full RAM continuity, physical stores and complete CPU refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import coasting_term_quantity_contract as contract
from kb import coasting_term_quantity_matrix as matrix
from kb import coasting_term_quantity_semantics as numeric
from kb import coasting_term_quantity_transfers as transfers
from kb import coasting_term_quantity_capture_evidence as proof

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

@pytest.mark.parametrize('raw',(0,1,2,127,128,254,255))
def test_unsigned_curve_result_reaches_both_real_words_and_rate_limited_final_word(raw):
    rows,fixture=reconstructed(source_curve=[raw]*8)
    first,last=rows[0][0],rows[1][0]
    assert first['memory_after']==last['memory_before']
    assert first['memory_after'][0][0x1230:0x1232]==first['memory_after'][0][0x126E:0x1270]==raw.to_bytes(2,'big')
    assert last['memory_after'][0][0x13EA:0x13EC]==min(255,128*raw).to_bytes(2,'big')
    assert rows[1][2]['source_word']==raw
    assert 0x47278 in transfers.INFEASIBLE_SITES and transfers.FIXED_BRANCHES[0x47276]=='taken'

@pytest.mark.parametrize('updates',(dict(byte_2458=0),dict(byte_244f=4),dict(diagnostic_140=128),
    dict(rom_870c=128,byte_2466=0),dict(rom_870c=128,byte_2458=160,rom_8252=255,byte_110e=255),
    dict(byte_2473=4,byte_2465=64,prior_13ea=65535),dict(byte_24a0=1,prior_13ea=256),
    dict(byte_2473=4,word_1748=65535,coasting_curve=list(reversed(range(16))),byte_110e=31)))
def test_complete_admission_correction_latch_cap_and_decay_paths(updates):
    reconstructed(**updates)

@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width','store-register','return-delay','stack-word','special-register','opcode'))
def test_matching_final_word_cannot_replace_complete_physical_or_CPU_evidence(fault):
    rows,fixture=reconstructed();observed,result,value=rows[0]
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x26AAC)['width_bytes']=2
    elif fault=='store-register':
        row=next(r for r in result['trace'] if r['site']==0x2C63C);registers=list(row['before']['registers']);registers[6]^=0x10000;row['before']['registers']=tuple(registers)
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
    elif fault=='calibration':last['calibration_before']={**last['calibration_before'],0x870C:b'\x01'}
    elif fault=='bound':last['bound_before']=b'\x01'+last['bound_before'][1:]
    elif fault=='phase':last['phase']=0
    elif fault=='pair':last['pair']=1
    else:next(row for row in cvalue['operands'] if row['site']==0x4726E)['bytes']='0000'
    with pytest.raises(ValueError):transfers.require_handoff(first,last,pvalue,cvalue)

def causal_pairs(**updates):
    pairs=[]
    for index in range(8):
        for raw in (0,1):
            curve=[0]*8;curve[index]=raw
            rows,fixture=reconstructed(source_curve=curve,byte_1077=index*32,**updates)
            pairs.append((rows[0][0],rows[1][0],rows[0][2],rows[1][2]))
    return pairs

def test_each_actual_source_cell_needs_changed_carried_word_and_final_publication():
    assert proof.require_causal_alternatives(causal_pairs())=={f'source-cell-{i}':True for i in range(8)}
    with pytest.raises(ValueError):proof.require_causal_alternatives(causal_pairs(byte_2458=0))
    pairs=causal_pairs()
    for producer,consumer,pvalue,cvalue in pairs:
        memory=bytearray(consumer['memory_after'][0]);memory[0x13EA:0x13EC]=b'\x00\x00';consumer['memory_after']=(bytes(memory),);cvalue['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)

def test_source_mask_preserves_other_cells_and_both_complete_phase_contexts():
    rows,fixture=reconstructed();first,last=rows[0][0],rows[1][0]
    baseline=proof.held_key(first,last,0x122E2,1,'rom')[0]
    changed=deepcopy(first);raw=bytearray(changed['calibration_before'][0x122E2]);raw[0]^=1
    changed['calibration_before'][0x122E2]=bytes(raw)
    assert proof.held_key(changed,last,0x122E2,1,'rom')[0]==baseline
    raw[1]^=1;changed['calibration_before'][0x122E2]=bytes(raw)
    assert proof.held_key(changed,last,0x122E2,1,'rom')[0]!=baseline
    different=deepcopy(last);context=list(different['context']);context[0]^=1;different['context']=tuple(context)
    assert proof.held_key(first,different,0x122E2,1,'rom')[0]!=baseline
