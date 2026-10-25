"""Complete natural CPU, physical operands, live stores and matching-output refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import maf_accumulator_update_contract as contract,maf_accumulator_update_matrix as matrix
from kb import maf_accumulator_update_semantics as numeric,maf_accumulator_update_transfers as transfers
def case(**changes):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='complete-source-refusal')
    value.update({row['name']:image[row['address']:row['address']+row['size']]
                  for row in contract.DECLARED['input_blobs']})
    value.update(changes)
    return value


def reconstructed(**changes):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=case(**changes);fixture,_=contract.fixture_for_case(source,image,value);context=matrix.context(source,value)
    sp,continuation=0x30000000,0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=continuation.to_bytes(4,'big')
    before,calibration=matrix.memory(value),matrix.calibrations(source,image,value)
    result=state.execute(source,fixture,context,before,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    observed=dict(entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,memory_before=(before,),
        calibration_before=calibration,frame_before=bytes(frame),frame_after=result['frame'],memory_after=(result['ram'],),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),sr_before=context[18])
    return observed,result,numeric.caller(before,calibration,context),fixture


@pytest.mark.parametrize('changes',({},dict(initialized=0),dict(enabled=0),dict(scaled=0),
    dict(phase_first=0,threshold_sample=255),dict(phase_second=2,word_latched=0),
    dict(word_latched=0,call_count=124),dict(seeded=0),dict(sum=0xFFFFFFFF),
    dict(latched_count=0,rom_8a4c=0,phase_first=0,count_latched=2)))
def test_full_actual_accumulator_and_real_helper_paths(changes):
    observed,result,value,fixture=reconstructed(**changes)
    transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('exit-SR','frame','other-RAM','read-width','GBR','live-store',
    'post-delay-divisor','return-PR','delay-slot','computed-memory','physical-curve'))
def test_matching_output_cannot_replace_complete_operands_or_state(fault):
    observed,result,value,fixture=reconstructed()
    transfers.require(observed,result,value,fixture)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
    elif fault=='frame':observed['frame_after']=b'\x01'+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='read-width':next(r for r in result['accesses'] if r['site']==0x3ADCE)['width_bytes']=2
    elif fault=='GBR':result['trace'][20]['before']['gbr']^=1
    elif fault=='live-store':
        row=next(r for r in result['trace'] if r['site'] in (0x3AD8A,0x3AE1A,0x3AE74))
        registers=list(row['before']['registers']);registers[transfers.STORE_REGISTERS[row['site']]]^=1
        row['before']['registers']=tuple(registers)
    elif fault=='post-delay-divisor':
        row=next(c for c in result['calls'] if c['site']==0x3AC86)
        registers=list(row['entry']['registers']);registers[0]=0;row['entry']['registers']=tuple(registers)
    elif fault=='return-PR':result['pr']^=1
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    elif fault=='computed-memory':
        raw=bytearray(value['memory']);raw[0x399C]^=1;value['memory']=bytes(raw)
    else:next(r for r in result['accesses'] if r['site']==0x2648C)['address']+=1
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)
