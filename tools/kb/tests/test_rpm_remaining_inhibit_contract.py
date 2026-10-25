"""Exact five conditional readers retain the previous nine and every native fact."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import repo,test_contract
from kb import rpm_inhibit_access_contract as owning,rpm_inhibit_contract as previous
from kb import rpm_remaining_inhibit_contract as contract,rpm_remaining_inhibit_matrix as matrix
from kb import rpm_remaining_inhibit_semantics as scalar,rpm_remaining_inhibit_capture_evidence as proof
from kb.test_stock_capture import tool

RETAINED_NINE={'0004ed88-0000934e-reader': '06b1d9e50500580d019435146dc58d13824574719cddab2a5cf8e8a917387195', '0004ed88-ffff2494-reader': '0150d72cc1dc88e37f50f7917005107d3687865e5915da010672d475ff0884aa', '0004ed88-ffff2497-reader': '4b938150413dbd5dbdd576f74733e8e93b1a0ef5ab6122fd22454f69dc4d1033', '0004ed88-ffff24a6-reader': 'e894c1c5dab812be8fe932644ccc845a630eab883b5fb73162460a0521fee362', '0004ed88-ffff2448-reader': '15667a47cca8df1baf85b86eb0f882127406322f284d1902406292c73598c9d5', '0004ed88-ffff418c-reader': '34a50baac00ccdcb6fbfa443e96a466c7f40b6d4d846465db3d795febc025fa7', '0004ed88-ffff2489-reader': 'bede00e4b1d968d38418ebf5fa99ae76113d5d060c06011f11185cd022f0382c', '0004ed88-ffff249f-reader': '4259fff07351d907ac5c546655c5b4b8c92ddc105c5fcefe771b62993a9e031f', '0004ed88-ffff41ea-reader': '9d2a989f2621ec184530c436a0b6992c1d725981ff8f9f068f595bf56288adc3'}
ORIGINALS={0x85D9:'adbb8843af22f6905e6621e97f9ba34d8f8f1148cb7d7140bd95ece8420426ce',
    0xFFFF247C:'1207bd7b2aa266376884f3a784f913d6785590a23da2847dba2d7be3775977c7',
    0xFFFF247F:'14538f273e63967afb86e7fc260c98112ae69c558d44164490db7a69ad70207c',
    0xFFFF249C:'b73c446bfdd0ba749bc64527b07b576952f5e55bbfa37f47ac5041076f60e213',
    0xFFFF41F2:'864f52c02760339d3172565de50cadf5a38c6cf6ac0eaa51b9721ecca3ddaba4'}


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_joint_fourteen_preserve_nine_complete_records_and_five_complete_native_preimages():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==14 and {row['id']:digest(row) for row in rows[:9]}==RETAINED_NINE
    assert {row['address']:row['original_claim_sha256'] for row in rows[9:]}==ORIGINALS
    assert {row['component'] for row in rows[:9]}=={'rpm_inhibit_paths'}
    assert {row['component'] for row in rows[9:]}=={'rpm_remaining_inhibit_paths'}
    for row in rows[9:]:
        before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
        expected=deepcopy(before)
        link=next(link for link in expected['link'] if link['type']=='reader' and link['to']=='fuel_output_inhibit_coordinator/fn')
        link.setdefault('evidence',[]).append(owning.item(row))
        assert test_contract.exact(after,expected)
        assert test_contract.exact(before['symbol'],after['symbol'])
        assert row['original_ledger_json']==row['proposed_ledger_json']
        assert row['declared_signed']=='unset'
        assert row['declared_width']==(8 if row['address']==0xFFFF249C else 'unset')


def test_three_separate_fixture_entries_keep_the_old_nine_fixture_and_all_instruction_bytes():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert contract.ENTRIES==(0x4EDC6,0x4EDE4,0x4EE00)
    assert tuple(row['address'] for row in contract.BOUNDARIES)==(0x4EDCE,0x4EDEA,0x4EE06)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    for row in contract.BOUNDARIES:
        at=row['address'];restored[at:at+8]=image[at:at+8]
        assert fixture[at:at+8]==bytes.fromhex(row['bytes'])
        assert not any(first<at+8 and at<last for first,last in contract.SPANS)
    assert bytes(restored)==image
    old,_=previous.independent_fixture(previous.descriptor(repo.ROOT),image)
    assert old[0x4EDC6:0x4EDCE]!=fixture[0x4EDC6:0x4EDCE]
    assert old[0x4EDEA:0x4EDF0]!=fixture[0x4EDEA:0x4EDF0]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_diagnostic_producer_full_coordinator_scale_units_geometry_or_hardware(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,original,changed',(
    ('status_value','status_value = 192','status_value = 64'),
    ('count','diagnostic_count_minimum = 40','diagnostic_count_minimum = 0'),
    ('dispatch','dispatch_admitted = false','dispatch_admitted = true')))
def test_descriptor_pins_the_actual_quiet_diagnostic_premise(tmp_path,field,original,changed):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert original in text
    path.write_text(text.replace(original,changed,1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def inputs(entry=0x4EDC6,**changes):
    case=deepcopy(matrix.DEFAULTS);case.update(index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return case,source,matrix.memory(case),matrix.calibrations(source,image,case)


@pytest.mark.parametrize('flags,rpm,cut,restore,active',(
    (8,35,36,30,False),(8,36,36,30,True),(0x28,29,36,30,False),(0x28,30,36,30,True),
    (8,36,30,30,True),(8,36,40,30,False),(0x28,36,36,40,False),(0xFF,255,255,255,True)))
def test_stationary_cut_and_restore_bind_the_real_caller_R14(flags,rpm,cut,restore,active):
    case,source,before,calibration=inputs(stationary_flags=flags,rpm50=rpm,
        stationary_cut=cut,stationary_restore=restore,thermal_flags=0)
    result=scalar.evaluate(case['entry'],before,calibration,matrix.context(source,case))
    assert result['output']==(0,0x3E5F6A00|int(active))
    assert bool(result['memory'][0x247F]&32) is active


@pytest.mark.parametrize('readiness,coefficient,expected',((0,0,0),(127,0,0),(128,0,0),
    (65535,255,65535),(65500,255,65535),(381,128,381),(381,127,380)))
def test_stationary_byte16_adjustment_saturates_the_complete_unsigned_accumulator(readiness,coefficient,expected):
    _,_,before,calibration=inputs(readiness_timer=0,readiness=readiness,curve=[coefficient]*16)
    result=scalar.stationary(before,calibration)
    assert int.from_bytes(result['memory'][0x16A6:0x16A8],'big')==expected
    assert result['memory'][0x258A]==100


@pytest.mark.parametrize('coordinate,curve,expected',((0,[0]*16,0),(239,list(range(0,256,17)),253),
    (239,list(range(255,-1,-17)),2),(240,[255]*16,255),(255,[128]*16,128)))
def test_independent_byte16_interpolation_has_exact_fraction_and_upper_return(coordinate,curve,expected):
    assert scalar.byte_curve(curve,coordinate)['value']==expected


@pytest.mark.parametrize('flags,diagnostic,rpm,expected',((8,16,80,1),(8,0,80,0),(0,16,80,0),
    (8,16,75,0),(8,16,76,1),(255,16,255,1)))
def test_conditional_thermal_flag_consumer_keeps_the_quiet_dispatch_premise(flags,diagnostic,rpm,expected):
    _,_,before,calibration=inputs(thermal_flags=flags,diagnostic_flags=diagnostic,rpm25=rpm)
    result=scalar.thermal(before,calibration)
    assert result['output']==expected and result['diagnostic_dispatch'] is False
    assert result['memory'][0x41F2]&16==0
    assert result['memory'][0x4396:0x4398]==bytes((50,10))


@pytest.mark.parametrize('status,count',((64,40),(0,40),(192,39)))
def test_thermal_consumer_refuses_an_unproved_diagnostic_producer_path(status,count):
    _,_,before,calibration=inputs();changed=bytearray(before)
    changed[0x4184]=status;changed[0x571E]=count
    with pytest.raises(ValueError):scalar.thermal(bytes(changed),calibration)


@pytest.mark.parametrize('flags,rpm,exposure,expected',((0,71,24000,0),(0,72,24000,1),
    (128,59,24000,0),(128,60,24000,1),(128,66,23999,0),(128,66,24000,1)))
def test_sustained_threshold_and_hold_bind_both_real_R0_and_caller_R2(flags,rpm,exposure,expected):
    case,source,before,calibration=inputs(0x4EDE4,sustained_flags=flags,rpm25=rpm,exposure=exposure)
    result=scalar.evaluate(case['entry'],before,calibration,matrix.context(source,case))
    assert result['output']==(expected,0x3E5F6A00) and result['r2']==expected


@pytest.mark.parametrize('flags,rpm,request,expected',((0,40,40,0),(0,41,40,1),
    (128,34,40,0),(128,35,40,1),(0,38,40,0),(128,38,40,1),(128,255,255,1)))
def test_CAN_ceiling_uses_strict_nonwrapping_hysteresis_and_real_R0(flags,rpm,request,expected):
    case,source,before,calibration=inputs(0x4EE00,ceiling_flags=flags,rpm50=rpm,request=request)
    result=scalar.evaluate(case['entry'],before,calibration,matrix.context(source,case))
    assert result['output']==(expected,0x3E5F6A00)


def test_private_generated_input_header_contains_no_expected_state_or_numerical_answers():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    declared=dict(source=source,cases=list(matrix.cases(source,image)))
    producer=tool(repo.ROOT,'rpm_remaining_inhibit_capture.py','_kb_rpm_remaining_raw_source')
    assert producer.header(declared,image)==proof.header(declared,image)
    assert all(name not in matrix.FIELDS for name in ('expected','result','terminal','output'))


def test_document_counts_and_exact_premises_read_current_executed_sources():
    text=(repo.ROOT/'defs/JK08A.rpm-remaining-inhibit.md').read_text()
    assert 'five exact reader relations' in text and len(ORIGINALS)==5
    assert 'three bounded caller entries' in text and len(contract.ENTRIES)==3
    assert '35 controlled calibration bytes' in text and sum(row['size'] for row in contract.CONTROLLED_CALIBRATION)==35
    assert 'twenty-two long RAM pointer aliases' in text and len(contract.UNIT['aliases'])==22
    assert '42 conditional branch sites' in text and len(proof.REQUIRED_BRANCHES)==42
    assert 'nine fixed-outcome sites' in text and len(proof.FIXED_BRANCHES)==9
    for literal in ('0004EDC6','0004EDE4','0004EE00','FFFF4184','FFFF571E','0007D8B8',
        '80-byte','572-byte','192-byte','R14','R0/R2','C0'):
        assert literal in text
