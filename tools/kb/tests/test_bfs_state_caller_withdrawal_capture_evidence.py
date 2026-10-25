"""Independent wide publications, complete physical refusals and interval absence."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import bfs_state_caller_withdrawal_contract as contract
from kb import bfs_state_caller_withdrawal_matrix as matrix
from kb import bfs_state_caller_withdrawal_semantics as numeric
from kb import bfs_state_caller_withdrawal_transfers as transfers
from kb import bfs_state_caller_withdrawal_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-unit-refusal')
    value.update(updates);return value

def equations(value):return numeric.quantities(matrix.memory(value),matrix.input_calibrations(value))

@pytest.mark.parametrize(('state','enable','pending','expected'),((0,1,0,1),(0,0,0,0),(1,1,0,2),(1,1,255,1),(2,1,255,2),(2,0,0,0),(0x80000000,1,0,0x80000000)))
def test_first_state_uses_full_raw_state_and_defers_the_zero_curve_transition(state,enable,pending,expected):
    value=equations(case(state_39d0=state,byte_2462=enable,byte_2542=pending))
    assert value['first_state']==expected

def test_each_active_actual_curve_byte_changes_both_computed_publications():
    for i in range(8):
        results=[]
        for raw in (0,255):
            result=equations(case(state_39d0=0,byte_1077=i*32,**{f'curve_{i}':raw}))
            results.append((result['memory'][0x1F78],result['memory'][0x2542]))
        assert results==[(0,0),(255,255)]

@pytest.mark.parametrize(('coordinate','width','mode','expected'),((0,2000,0,1),(8192,2000,0,1),(65535,2000,0,0),(0,2000,16,1),(1000,2000,16,0),(8192,2000,16,0)))
def test_separate_BFS_window_equations_keep_asymmetric_branches(coordinate,width,mode,expected):
    result=equations(case(word_1026=coordinate,word_1062=width,byte_24b1=mode))
    assert result['second_state']==expected

def test_raw_temperature_increment_does_not_wrap_to_a_byte():
    result=equations(case(byte_1079=255,byte_24ba=128,rom_875c=255))
    assert result['hot'] is True and result['memory'][0x24BA]&128

def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);context=matrix.context(source,value)
    sp,continuation=0x30000000,0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big')
    frame[184:188]=continuation.to_bytes(4,'big');before=matrix.memory(value);cal=matrix.calibrations(source,image,value)
    result=state.execute(source,fixture,context,before,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    observed=dict(entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,memory_before=(before,),
        calibration_before=cal,exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        frame_before=bytes(frame),frame_after=result['frame'],memory_after=(result['ram'],),sr_before=context[18])
    independent=numeric.evaluate(contract.ENTRY,before,cal,context,context[18],bytes(frame),sp,continuation)
    return observed,result,independent,fixture

@pytest.mark.parametrize('updates',({},dict(state_39d0=0,byte_1077=17),dict(state_39d0=0,byte_1077=255),
    dict(byte_24b1=16,word_1026=0),dict(state_39d4=0xFFFFFFFF)))
def test_complete_physical_paths_and_separate_publications(updates):
    observed,result,value,fixture=reconstructed(**updates)
    transfers.require(observed,result,value,fixture)

@pytest.mark.parametrize('fault',('exit-SR','frame','other-RAM','curve-argument','neighbor-width','local-slot','tail','predicate-ID','returned-PR','instruction-byte'))
def test_matching_state_outputs_cannot_replace_complete_physical_or_CPU_evidence(fault):
    updates=dict(state_39d0=0,byte_1077=17) if fault in ('curve-argument','neighbor-width','tail') else {}
    observed,result,value,fixture=reconstructed(**updates);transfers.require(observed,result,value,fixture)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault in ('curve-argument','predicate-ID'):
        call=next(r for r in result['calls'] if r['site']==(0x3A772 if fault=='curve-argument' else 0x3A810))
        raw=list(call['entry']['registers']);raw[4]^=1;call['entry']['registers']=tuple(raw)
    elif fault=='neighbor-width':next(r for r in result['accesses'] if r['site']==0x26AAE)['width_bytes']=2
    elif fault=='local-slot':next(r for r in result['accesses'] if r['site']==0x3A840)['address']+=4
    elif fault=='tail':next(r for r in result['trace'] if r['site']==0x26AB8)['delay_slot']=False
    elif fault=='returned-PR':result['pr']^=2
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

@pytest.mark.parametrize('mode',('read','write'))
@pytest.mark.parametrize('offset',range(16))
def test_full_selected_table_interval_refuses_every_byte_and_direction(mode,offset):
    row=dict(original_claim_sha256=contract.DECLARED['selected']['original_claim_sha256'],address=0x15630)
    transfers.require_no_selected_datum(dict(accesses=[]),[row])
    with pytest.raises(ValueError):
        transfers.require_no_selected_datum(dict(accesses=[dict(address=0x15630+offset,width_bytes=1,mode=mode)]),[row])

@pytest.mark.parametrize(('address','width'),((0x1562F,2),(0x1562D,4),(0x1563F,4)))
def test_table_interval_rejects_overlapping_operands_starting_outside_or_crossing_the_end(address,width):
    row=dict(original_claim_sha256=contract.DECLARED['selected']['original_claim_sha256'],address=0x15630)
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(address=address,width_bytes=width)]),[row])

def test_causal_mask_preserves_other_quantity_CPU_frame_and_other_curve_cells():
    value=case(state_39d0=0);memory=matrix.memory(value)
    observed=dict(entry=contract.ENTRY,context=matrix.context({},value),memory_before=(memory,),
        calibration_before=matrix.input_calibrations(value),bound_before=bytes(sum(row['size'] for row in contract.BOUND_SPANS)),
        frame_before=bytes(192),sp=0x30000000,continuation=0x30010000,abi_before=tuple(range(12)),sr_before=0)
    changed=deepcopy(observed);raw=bytearray(changed['calibration_before'][0x12A3A]);raw[1]^=1
    changed['calibration_before'][0x12A3A]=bytes(raw)
    assert proof.held_key(observed,0x12A3B,1,'rom')[0]==proof.held_key(changed,0x12A3B,1,'rom')[0]
    raw=bytearray(changed['memory_before'][0]);raw[0x1062]^=1;changed['memory_before']=(bytes(raw),)
    assert proof.held_key(observed,0x12A3B,1,'rom')[0]!=proof.held_key(changed,0x12A3B,1,'rom')[0]
