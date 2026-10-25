"""Actual full bank1 writer, complete-state and causal refusal sources."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import third_trim_word_writer_contract as contract,third_trim_word_writer_matrix as matrix
from kb import third_trim_word_writer_semantics as numeric,third_trim_word_writer_transfers as transfers
from kb import third_trim_word_writer_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-third-trim-refusal');value.update(updates);return value

def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);cal=matrix.calibrations(source,image,value)
    memory=matrix.memory(value);context=matrix.context(source,value);sp=0x30000000;continuation=0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    independent=numeric.evaluate(memory,cal,context)
    bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        bound_before=bound,bound_after=bound,
        memory_before=(memory,),memory_after=(result['ram'],),frame_before=bytes(frame),frame_after=result['frame'],
        calibration_before=cal,calibration_after=cal,sr_before=context[18],abi_before=tuple(range(12)),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,independent,fixture)
    return observed,result,independent,fixture

@pytest.mark.parametrize('raw',(0,1,23039,23040,25000,25599,25600,28159,28160,32768,65535))
def test_actual_bank1_correction_word_uses_complete_entry(raw):
    words=[0x6400]*256;words[0]=raw
    observed,result,value,fixture=reconstructed(prior_words=words)
    wanted=max(90*256,min(raw+4,110*256))
    assert int.from_bytes(observed['memory_after'][0][0x2A24:0x2A26],'big')==value['word']==wanted
    assert value['channel']==0 and value['mask']==1 and value['full_word_register']==wanted

@pytest.mark.parametrize('old',(0,1,25599,25600,25601,25608,65535,0x7FFFFFFF,0x80000000,0xFFFFFFFF))
@pytest.mark.parametrize('step',(0,8,255))
def test_full_signed32_counter_and_raw_low16_word(old,step):
    counters=[0x6400]*256;counters[0]=old
    observed,result,value,fixture=reconstructed(flags_328a=0,flags_328b=0,flags_328c=1,
        accumulators=counters,rom_86f5=step)
    signed=old-(1<<32) if old&0x80000000 else old
    wanted=min(0x6400,signed+step) if signed<0x6400 else max(0x6400,signed-step)
    assert result['registers'][2]==value['full_word_register']==wanted&0xFFFFFFFF
    assert int.from_bytes(observed['memory_after'][0][0x3310:0x3314],'big')==wanted&0xFFFFFFFF
    assert int.from_bytes(observed['memory_after'][0][0x2A24:0x2A26],'big')==wanted&65535

@pytest.mark.parametrize('fault',('exit-SR','detached-MQ','exit-register','frame','other-RAM','source-width',
    'index-address','full-R2','shared-R0','return-delay','saved-word','fake-call','opcode'))
def test_matching_low16_cannot_replace_full_state_and_real_store_registers(fault):
    observed,result,value,fixture=reconstructed(rom_8b2a=4,flags_328a=3,flags_328b=3)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x100,*observed['exit'][1:])
    elif fault=='detached-MQ':
        result['sr']^=0x100;observed['exit']=(result['sr'],*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x5B6F0)['width_bytes']=4
    elif fault=='index-address':next(r for r in result['accesses'] if r['site']==0x5B6F0)['address']+=2
    elif fault in ('full-R2','shared-R0'):
        site,register=(0x5B6F0,2) if fault=='full-R2' else (0x5B6F4,0)
        row=next(r for r in result['trace'] if r['site']==site)
        registers=list(row['before']['registers']);registers[register]^=0x10000;row['before']['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-word':next(r for r in result['accesses'] if r['domain']=='frame')['address']+=4
    elif fault=='fake-call':result['calls'].append(dict(site=0x5B534,target=0x21CE0))
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

def test_all_raw_channels_are_observed_without_extending_bank1_identity():
    pairs=[]
    for channel in range(256):
        context=list(matrix.DEFAULT_CONTEXT);context[4]=0xABCD0000|channel
        observed,result,value,fixture=reconstructed(context=context,rom_8b2a=4,flags_328a=3,flags_328b=3)
        pairs.append((observed,value))
    assert proof.require_channels(pairs) is True
    with pytest.raises(ValueError):proof.require_channels(pairs[:-1])

def test_bank1_word_and_counter_have_held_other_actual_storage_alternatives():
    pairs=[]
    for raw in (23040,25000,28159):
        words=[0x6400]*256;words[0]=raw
        observed,result,value,fixture=reconstructed(prior_words=words);pairs.append((observed,value))
    for raw in (0,1,25599):
        counters=[0x6400]*256;counters[0]=raw
        observed,result,value,fixture=reconstructed(flags_328a=0,flags_328b=0,flags_328c=1,accumulators=counters)
        pairs.append((observed,value))
    assert proof.require_causal_alternatives(pairs)==dict([('prior-bank1-word',True),('full-bank1-accumulator',True)])
    for observed,value in pairs:
        memory=bytearray(observed['memory_after'][0]);memory[0x2A24:0x2A26]=b'\x64\x00'
        observed['memory_after']=(bytes(memory),);value['word']=0x6400
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)

def test_independent_sibling_modes_and_discarded_entry_channel_high_bits():
    siblings=[];high=[]
    for shared in (False,True):
        for prior in (0,1,32768,65535):
            words=[0x6400]*256;words[1]=prior
            observed,result,value,fixture=reconstructed(prior_words=words,rom_8b2a=4 if shared else 0,
                flags_328a=3 if shared else 1,flags_328b=3 if shared else 1)
            siblings.append((observed,value))
    assert proof.require_sibling_modes(siblings)==dict(ordinary=True,shared=True)
    for raw in (0,0x100,0x80000000,0xFFFF0000):
        context=list(matrix.DEFAULT_CONTEXT);context[4]=raw
        observed,result,value,fixture=reconstructed(context=context);high.append((observed,value))
    assert proof.require_channel_high_bits_invariance(high) is True
    memory=bytearray(high[-1][0]['memory_after'][0]);memory[0x88]^=1;high[-1][0]['memory_after']=(bytes(memory),)
    with pytest.raises(ValueError):proof.require_channel_high_bits_invariance(high)
