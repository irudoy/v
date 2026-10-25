"""Full fixed-record predicates,stage/low-speed masks and retained array dependency."""
from copy import deepcopy
import pytest
from kb import repo
from kb import actuator_mask_access_contract as contract,actuator_mask_access_matrix as matrix
from kb import actuator_mask_access_semantics as scalar,actuator_mask_access_transfers as transfers
from kb import actuator_mask_access_capture_evidence as proof


def evaluate(**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x5096C,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(0x5096C,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('byte,mask',((0,0),(42,0),(43,1),(44,5),(45,7),(46,15),(47,31),(48,63),(127,63),(128,63),(255,63)))
def test_actual_unsigned_stage_thresholds_have_seven_distinct_returned_masks(byte,mask):
    value=evaluate(byte_11b3=byte,byte_110e=3)
    assert value['output']==value['known_registers'][0]==mask
    assert value['sp']==0x02001000 and value['pr']==0x02100000


@pytest.mark.parametrize('speed,state,mask',((0,4,63),(1,4,63),(2,4,63),(3,4,5),(127,4,5),(128,4,5),(255,4,5),
    (0,0,5),(0,3,5),(0,5,63),(0,128,5),(0,255,63)))
def test_signed_loaded_speed_uses_unsigned_comparison_and_state_bit2(speed,state,mask):
    value=evaluate(byte_110e=speed,byte_10e4=state)
    assert value['output']==mask and value['known_registers'][6]==2


@pytest.mark.parametrize('first,second,ids,mask',((0,0,(0x71,0x123),0),(127,127,(0x71,0x123),0),
    (128,0,(0x71,),5),(255,255,(0x71,),5),(0,128,(0x71,0x123),5),(1,255,(0x71,0x123),5)))
def test_two_fixed_post_delay_ids_preserve_short_circuit_and_array_members(first,second,ids,mask):
    value=evaluate(byte_586c=first,byte_5a82=second,raw_r4=0xFFFF0000)
    calls=[row for row in value['calls'] if row['target']==0x25E20]
    assert tuple(row['registers'][4] for row in calls)==ids and value['output']==mask
    reads=[event for event in value['events'].values() if event['site']==0x25E32]
    assert tuple(row['address'] for row in reads)==tuple(0x01005718+3*identifier+1 for identifier in ids)
    assert all(row['width_bytes']==1 for row in reads)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_fixture_grants_no_native_geometry_identity_units_scale_scheduling_stub_or_hardware_claim(tmp_path,flag):
    source=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in source
    target=tmp_path/contract.DESCRIPTOR;target.parent.mkdir(parents=True);target.write_text(source.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_complete_fixture_instruction_operand_input_and_helper_counts_are_source_bound():
    declared=contract.descriptor(repo.ROOT)
    words=' '.join((repo.ROOT/'defs/JK08A.diagnostic-array-accesses.md').read_text().split())
    for phrase,actual,wanted in (
        ('95 stock instructions',sum((last-first)//2 for first,last in contract.SPANS),95),
        ('190 code bytes',sum(last-first for first,last in contract.SPANS),190),('4 complete code spans',len(contract.SPANS),4),
        ('94 feasible instructions',len(transfers.FEASIBLE_SITES),94),('1 excluded instruction',len(transfers.INFEASIBLE_SITES),1),
        ('5 literal spans',len(contract.UNIT['pools']),5),('3 pointer aliases',len(contract.UNIT['aliases']),3),
        ('5 complete RAM fields',len(matrix.RAM_FIELDS),5),('15 raw input fields',len(matrix.WIDTHS),15),
        ('5 calibration spans',len(contract.CONTROLLED_CALIBRATION),5),('18 unchanged helper source files',len(contract.REUSED_HELPER_FILES_SHA256),18),
        ('10 two-sided conditions',len(proof.REQUIRED_BRANCHES),10),('1 fixed condition',len(proof.FIXED_BRANCHES),1)):
        assert phrase in words and actual==wanted
    assert transfers.INFEASIBLE_SITES=={0x25E3E} and proof.FIXED_BRANCHES=={0x25E26:'fallthrough'}
    assert contract.ENTRIES==(0x5096C,) and contract.HELPER_ENTRIES==(0x25E20,0x509A0,0x509EA)
    assert contract.CONFIGURATION==[] and contract.INPUT_BLOBS==[]
