"""Complete paired unit-state fixtures and refusal controls; actual admission requires the shared original."""
from copy import deepcopy
import pytest
from kb import repo,coherent_copy_matrix as coherent,byte_surface_equations as state,packed_transfer_evidence
from kb import pedal_snapshot_high_state_contract as contract,pedal_snapshot_high_state_matrix as matrix
from kb import pedal_snapshot_high_state_capture_evidence as proof,pedal_snapshot_high_state_semantics as numeric
from kb import pedal_snapshot_high_state_transfers as transfers


def case(**changes):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value=dict(deepcopy(matrix.DEFAULTS),threshold_curve=image[0x1473A:0x1474A],index=0,kind='paired-refusal')
    value.update(changes);return value


def reconstructed(**changes):
    source=contract.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();value=case(**changes)
    fixture,_=contract.fixture_for_case(source,image,value);before=matrix.memory(value)
    legacy=matrix.snapshot_context(value);context=matrix.context(source,value);meta=matrix.snapshot_case(value)
    sp,first_return,second_return=0x30000000,0x30010000,0x30020000
    gpr,t,middle=coherent.expected(matrix.WINDOW,meta,before,first_return);middle=bytes(middle)
    legacy_frame=coherent.initial_frame(first_return);legacy_sr=0xF0|value['snapshot_t']
    legacy_abi=(*coherent.ABI,sp+164,0x2468ACE0)
    first=dict(exit=((legacy_sr&~1)|t,first_return,legacy[17],legacy[16],legacy[15],*reversed(gpr)),
        sp=sp,continuation=first_return,abi_before=legacy_abi,abi_after=legacy_abi,
        frame_before=legacy_frame,frame_after=bytes(coherent.frame(matrix.WINDOW,meta,legacy_frame)),sr_before=legacy_sr)
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=second_return.to_bytes(4,'big')
    result=state.execute(source,fixture,context,middle,bytes(frame),sp,second_return,contract.ENTRY,context[18],trace=True)
    abi=(*packed_transfer_evidence.ABI,sp+164,0x13579BDF)
    second=dict(exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        sp=sp,continuation=second_return,abi_before=abi,abi_after=abi,
        frame_before=bytes(frame),frame_after=result['frame'],sr_before=context[18])
    cal=matrix.calibrations(source,image,value);bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    observed=dict(index=0,entry=contract.ENTRY,snapshot_entry=contract.SNAPSHOT['entry'],snapshot_context=legacy,context=context,
        snapshot_observer=first,comparator_observer=second,memory_before=before,memory_after_snapshot=middle,
        memory_before_comparator=middle,memory_after=result['ram'],calibration_before=cal,calibration_after=cal,
        bound_before=bound,bound_after=bound)
    return dict(source=source,bound_spans=[[r['address'],r['size']] for r in contract.BOUND_SPANS]),image,value,observed,result,fixture


@pytest.mark.parametrize('changes',({},dict(word_2672=0),dict(word_2672=65535),dict(rom_870c=128),
    dict(rom_870c=128,byte_110e=28),dict(byte_246d=128),dict(byte_24d7=255),
    dict(byte_424f=8),dict(record_0=128),dict(byte_2471=64,rom_88b4=255),
    dict(rom_8c74=0,rom_9536=0),dict(byte_2470=2,rom_8c75=0,rom_9536=0)))
def test_full_existing_history_and_actual_complete_comparator_paths(changes):
    declared,image,value,observed,_,_=reconstructed(**changes)
    proof.require_state(declared,image,value,observed)


@pytest.mark.parametrize('fault',('history-word','handoff-byte','snapshot-SR','snapshot-frame','snapshot-SP',
    'snapshot-R11','comparator-frame','comparator-ABI','unrelated-final-RAM','calibration','bound-code'))
def test_matching_high_bit_cannot_replace_complete_pair(fault):
    declared,image,value,observed,_,_=reconstructed()
    proof.require_state(declared,image,value,observed)
    if fault in ('history-word','handoff-byte','unrelated-final-RAM'):
        key={'history-word':'memory_after_snapshot','handoff-byte':'memory_before_comparator','unrelated-final-RAM':'memory_after'}[fault]
        raw=bytearray(observed[key]);raw[0x266E if fault=='history-word' else 0x88]^=1;observed[key]=bytes(raw)
    elif fault=='snapshot-SR':
        first=observed['snapshot_observer'];first['exit']=(first['exit'][0]^1,*first['exit'][1:])
    elif fault=='snapshot-frame':
        first=observed['snapshot_observer'];first['frame_after']=b'\x01'+first['frame_after'][1:]
    elif fault=='snapshot-SP':observed['snapshot_observer']['sp']+=4
    elif fault=='snapshot-R11':
        context=list(observed['snapshot_context']);context[11]=0;observed['snapshot_context']=tuple(context)
    elif fault=='comparator-frame':
        second=observed['comparator_observer'];second['frame_after']=b'\x01'+second['frame_after'][1:]
    elif fault=='comparator-ABI':
        second=observed['comparator_observer'];second['abi_after']=(0,*second['abi_after'][1:])
    elif fault=='calibration':
        observed['calibration_after']=dict(observed['calibration_after'])
        observed['calibration_after'][0x8FDC]=bytes(2)
    else:observed['bound_after']=b'\x01'+observed['bound_after'][1:]
    with pytest.raises(ValueError):proof.require_state(declared,image,value,observed)


@pytest.mark.parametrize('fault',('read-width','curve-post-delay','fixed-record-ID','GBR','delay-slot','live-curve-store'))
def test_matching_values_cannot_replace_full_actual_comparator_operands(fault):
    declared,image,value,observed,result,fixture=reconstructed(rom_870c=128)
    numeric_value=numeric.caller(observed['memory_before_comparator'],observed['calibration_before'],observed['context'])
    actual=dict(observed['comparator_observer'],context=observed['context'],
        memory_before=(observed['memory_before_comparator'],),memory_after=(observed['memory_after'],),
        calibration_before=observed['calibration_before'])
    transfers.require(actual,result,numeric_value,fixture)
    if fault=='read-width':next(r for r in result['accesses'] if r['site']==0x47AAA)['width_bytes']=1
    elif fault in ('curve-post-delay','fixed-record-ID'):
        call=next(r for r in result['calls'] if r['site']==(0x47A90 if fault=='curve-post-delay' else 0x47AFC))
        registers=list(call['entry']['registers']);registers[5 if fault=='curve-post-delay' else 4]^=0x10000
        call['entry']['registers']=tuple(registers)
    elif fault=='GBR':result['gbr']^=1
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    else:
        row=next(r for r in result['trace'] if r['site']==0x47A9A)
        registers=list(row['before']['registers']);registers[6]^=65536;row['before']['registers']=tuple(registers)
    with pytest.raises(ValueError):transfers.require(actual,result,numeric_value,fixture)


def test_causal_key_holds_both_complete_phase_inputs_and_only_varies_source_word():
    first=reconstructed(word_2672=0)[3];second=reconstructed(word_2672=65535)[3]
    assert proof.held_key(first)[0]==proof.held_key(second)[0]
    proof.require_causal_alternatives([(first,{'pedal_high':False}),(second,{'pedal_high':True})])
    altered=deepcopy(second);raw=bytearray(altered['memory_before']);raw[0x2674]^=1;altered['memory_before']=bytes(raw)
    assert proof.held_key(first)[0]!=proof.held_key(altered)[0]
