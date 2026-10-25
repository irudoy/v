"""Actual paired words, full RAM continuity, physical stores and complete CPU refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import centered_channel_duty_contract as contract
from kb import centered_channel_duty_matrix as matrix
from kb import centered_channel_duty_semantics as numeric
from kb import centered_channel_duty_transfers as transfers
from kb import centered_channel_duty_capture_evidence as proof

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
        independent=numeric.evaluate(phase,memory,cal,context)
        observed=dict(pair=0,phase=phase,phase_id=contract.PHASES[phase],entry=contract.ENTRIES[phase],context=context,
            sp=sp,continuation=continuation,memory_before=(memory,),memory_after=(result['ram'],),
            calibration_before=cal,calibration_after=cal,bound_before=bound,bound_after=bound,
            frame_before=bytes(frame),frame_after=result['frame'],sr_before=context[18],abi_before=tuple(range(12)),
            exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
        transfers.require(observed,result,independent,fixture);rows.append((observed,result,independent))
        memory=result['ram']
    transfers.require_handoff(rows[0][0],rows[1][0],rows[0][2],rows[1][2])
    return rows,fixture

@pytest.mark.parametrize('selected',(0,1))
@pytest.mark.parametrize('raw',(0,1,2,127,128,254,255))
def test_actual_centered_channel_word_reaches_its_indexed_duty(selected,raw):
    context=matrix.initial_context(1);context[4]=selected
    rows,fixture=reconstructed(implicit_curves=[raw]*16,consumer_context=context)
    first,last=rows[0][0],rows[1][0]
    assert first['memory_after']==last['memory_before']
    assert first['memory_after'][0][0x1A9C+selected*4:0x1AA0+selected*4]==(raw*65536).to_bytes(4,'big')
    assert last['memory_after'][0][0x2440+selected]==raw
    assert rows[1][2]['handoff']==raw*65536

@pytest.mark.parametrize('updates',(dict(rom_8dd8=0),dict(byte_1108=0),dict(rom_8616=1,byte_2772=255),
    dict(rom_8616=1,explicit_axis=[255]*8,byte_2772=0),dict(rom_8615=128,byte_2326=0),
    dict(rom_8615=128,byte_2326=255,rom_86b9=0,byte_248e=64,word_2608=0),
    dict(byte_28c2=255),dict(byte_246b=0),dict(word_1afc=0xFFFFFFFF,word_1b00=0x80000000)))
def test_complete_modes_wrapped_dividends_zero_faults_and_terminal_neighbors(updates):
    reconstructed(**updates)

@pytest.mark.parametrize('phase',(0,1))
@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','operand-width','live-store-register','return-delay','stack-word','special-register','opcode'))
def test_matching_duty_bytes_cannot_replace_complete_physical_or_CPU_evidence(phase,fault):
    rows,fixture=reconstructed();observed,result,value=rows[phase]
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x100,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='operand-width':next(r for r in result['accesses'] if r['site']==(0xBE7B6 if phase==0 else 0xBE886))['width_bytes']=2
    elif fault=='live-store-register':
        row=next(r for r in result['trace'] if r['site']==(0xBE7B6 if phase==0 else 0xBE8DC))
        registers=list(row['before']['registers']);registers[2 if phase==0 else 6]^=0x10000;row['before']['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='stack-word':next(r for r in result['accesses'] if r['domain']=='frame')['address']+=4
    elif fault=='special-register':result['gbr']^=1
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

@pytest.mark.parametrize('fault',('RAM','calibration','bound','phase','pair','carried-word','other-channel'))
def test_handoff_refuses_reseeded_synthetic_or_wrong_channel_words(fault):
    rows,fixture=reconstructed();first,last=rows[0][0],rows[1][0];pvalue,cvalue=rows[0][2],rows[1][2]
    if fault=='RAM':
        raw=bytearray(last['memory_before'][0]);raw[0x88]^=1;last['memory_before']=(bytes(raw),)
    elif fault=='calibration':last['calibration_before']={**last['calibration_before'],0x8616:b'\x01'}
    elif fault=='bound':last['bound_before']=b'\x01'+last['bound_before'][1:]
    elif fault=='phase':last['phase']=0
    elif fault=='pair':last['pair']=1
    elif fault=='carried-word':next(r for r in cvalue['operands'] if r['site']==0xBE886)['bytes']='00000000'
    else:next(r for r in cvalue['operands'] if r['site']==0xBE886)['address']+=4
    with pytest.raises(ValueError):transfers.require_handoff(first,last,pvalue,cvalue)

def causal_pairs(**updates):
    pairs=[]
    for selected in (0,1):
        context=matrix.initial_context(1);context[4]=selected
        for index in range(8):
            for raw in (0,1):
                curve=[0]*16;curve[selected*8+index]=raw
                rows,fixture=reconstructed(implicit_curves=curve,byte_106f=index*32,consumer_context=context,**updates)
                pairs.append((rows[0][0],rows[1][0],rows[0][2],rows[1][2]))
    return pairs

def test_every_source_cell_needs_changed_actual_composite_and_corresponding_duty():
    assert proof.require_causal_alternatives(causal_pairs())=={f'implicit-cell-{i}':True for i in range(16)}
    with pytest.raises(ValueError):proof.require_causal_alternatives(causal_pairs(byte_246b=0))
    pairs=causal_pairs()
    for producer,consumer,pvalue,cvalue in pairs:
        memory=bytearray(consumer['memory_after'][0]);memory[0x2440+cvalue['channel']]=0
        consumer['memory_after']=(bytes(memory),);cvalue['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)

def test_mask_keeps_other_cells_and_both_full_phase_contexts_fixed():
    rows,fixture=reconstructed();first,last=rows[0][0],rows[1][0]
    baseline=proof.held_key(first,last,0x12E72,1,'rom')[0]
    changed=deepcopy(first);raw=bytearray(changed['calibration_before'][0x12E72]);raw[0]^=1
    changed['calibration_before'][0x12E72]=bytes(raw)
    assert proof.held_key(changed,last,0x12E72,1,'rom')[0]==baseline
    raw[1]^=1;changed['calibration_before'][0x12E72]=bytes(raw)
    assert proof.held_key(changed,last,0x12E72,1,'rom')[0]!=baseline
    different=deepcopy(last);context=list(different['context']);context[4]^=1;different['context']=tuple(context)
    assert proof.held_key(first,different,0x12E72,1,'rom')[0]!=baseline
