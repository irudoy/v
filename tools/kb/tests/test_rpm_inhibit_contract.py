"""Exact bounded sources, independent input domains and full native preservation."""

from copy import deepcopy
import json

import pytest

from kb import rpm_inhibit_contract as contract,rpm_inhibit_matrix as matrix
from kb import rpm_inhibit_semantics as scalar,rpm_inhibit_capture_evidence as proof
from kb import rpm_inhibit_access_contract as owning,repo,test_contract
from kb.test_stock_capture import tool


def test_fourteen_exact_originals_preserve_complete_owner_types_layouts_TEST_and_every_other_relation():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==len({row['owner'] for row in rows})==14
    assert {row['function'] for row in rows}=={0x4ED88}
    assert {row['address'] for row in rows}=={0x934E,0xFFFF2494,0xFFFF2497,0xFFFF24A6,0xFFFF2448,
        0xFFFF418C,0xFFFF2489,0xFFFF249F,0xFFFF41EA,
        0x85D9,0xFFFF247C,0xFFFF247F,0xFFFF249C,0xFFFF41F2}
    for row in rows:
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json'])
        expected=deepcopy(before);old=json.loads(row['original_claim_json'])
        link=next(link for link in expected['link'] if (link['type'],link['to'])==('reader',old['to']))
        link.setdefault('evidence',[]).append(owning.item(row))
        assert test_contract.exact(expected,after)
        assert before['symbol']==after['symbol'] and before['ledger']==after['ledger']
        assert row['original_ledger_json']==row['proposed_ledger_json']
        assert len(before['link'])==len(after['link'])
        if row['address']==0xFFFF249C:
            assert (row['declared_width'],row['declared_signed'])==(8,'unset')
        elif row['address'] not in (0xFFFF2497,0xFFFF24A6):
            assert row['declared_width']==row['declared_signed']=='unset'
            assert owning.native_type(row,'width') is owning.native_type(row,'signed') is None
        else:assert (row['declared_width'],row['declared_signed'])==(8,False)
        if row['address'] in (0x934E,0xFFFF2497):assert len(before['symbol'])==3


def test_stock_caller_leaf_aliases_and_all_outside_returns_restore_the_stock_image():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert contract.SPANS==((0x4EDBE,0x4EDC6),(0x4EDD2,0x4EDD6),(0x4EDEA,0x4EDF0),(0x4EDF8,0x4EDFC),
        (0x4F19C,0x4F1D8),(0x4F240,0x4F282),(0x4F282,0x4F324),
        (0x4F736,0x4F758),(0x4FAA0,0x4FAAC),(0x507CE,0x5082A),(0x50836,0x508E6),
        (0x259E4,0x25A12),(0x26370,0x26382),(0x26740,0x2676E),(0x26A80,0x26ABA))
    assert len(aliases)==15
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    for row in contract.BOUNDARIES:
        at=row['address'];restored[at:at+8]=image[at:at+8]
        assert fixture[at:at+8]==bytes.fromhex('57f6472a000b0009')
        assert not any(first<at+8 and at<last for first,last in contract.SPANS)
    assert bytes(restored)==image and len(contract.BOUNDARIES)==4
    assert contract.SPANS[0][1]-contract.SPANS[0][0]==8 and len(contract.FUNCTIONS)==9
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    assert sum(row['size'] for row in contract.CALIBRATIONS)==27


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_full_coordinator_stock_conditioned_branch_geometry_scale_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,address,width,rom',(('t0',0x934E,2,True),('condition2',0x2494,1,False),
    ('main_flags',0x2497,1,False),('vehicle_flags',0x24A6,1,False)))
def test_exact_positive_input_domains_keep_every_other_RAM_context_and_calibration_fixed(field,address,width,rom):
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    first=dict(index=0,kind='contributors',entry=contract.ENTRY,**matrix.DEFAULTS)
    if field=='condition2':first.update(config=0xE3,rpm=100)
    second=dict(first);second[field]^=1 if field in ('t0','vehicle_flags') else 32 if field=='condition2' else 4
    assert matrix.context(source,first)==matrix.context(source,second)
    left,right=bytearray(matrix.memory(first)),bytearray(matrix.memory(second))
    cal_left=matrix.calibrations(source,image,first);cal_right=matrix.calibrations(source,image,second)
    if rom:
        assert left==right
        data=bytearray(cal_left[0x934E]);assert data[:2]!=cal_right[0x934E][:2]
        data[:2]=cal_right[0x934E][:2];cal_left[0x934E]=bytes(data);assert cal_left==cal_right
    else:
        assert cal_left==cal_right and left[address:address+width]!=right[address:address+width]
        left[address:address+width]=right[address:address+width];assert left==right


@pytest.mark.parametrize('field,first,second,output',(
    ('t0',600,601,((1,0),(0,0))),('main_flags',0,4,((0,0),(1,0))),
    ('condition2',0,32,((0,0),(1,0))),('vehicle_flags',0,1,((0,0),(0,1)))))
def test_separate_literal_input_variation_changes_the_expected_caller_output_pair(field,first,second,output):
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    results=[]
    for value in (first,second):
        case=dict(index=0,kind='contributors',entry=contract.ENTRY,**matrix.DEFAULTS);case[field]=value
        if field=='condition2':case.update(config=0xE3,rpm=100)
        result=scalar.compose(matrix.memory(case),matrix.calibrations(source,image,case),case['prior'])
        results.append(result['output'])
    assert tuple(results)==output


def test_real_MOV_OR_delay_inputs_retain_the_full_prior_word_and_vehicle_bit():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    case=dict(index=0,kind='contributors',entry=contract.ENTRY,**matrix.DEFAULTS)
    case.update(prior=0x80000000,vehicle_flags=1,speed=91)
    result=scalar.compose(matrix.memory(case),matrix.calibrations(source,image,case),case['prior'])
    assert result['output']==(0,0x80000001)


def test_private_raw_header_matches_the_existing_observer_and_contains_explicit_inputs_only():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    declared=dict(source=source,cases=list(matrix.cases(source,image)))
    producer=tool(repo.ROOT,'rpm_inhibit_capture.py','_kb_rpm_inhibit_raw_source')
    assert producer.header(declared,image)==proof.header(declared,image)
    assert matrix.FIELDS[0]=='entry' and matrix.FIELDS[-3:]==('prior','variant','sr')


def test_document_gates_the_executed_owning_count_source_aliases_calibration_and_entry_scope():
    text=(repo.ROOT/'defs/JK08A.rpm-inhibit-accesses.md').read_text()
    assert 'contains fourteen exact original reader claims' in text
    assert len(owning.descriptor(repo.ROOT)['reference'])==14
    assert 'Fifteen long RAM pointer aliases' in text and len(contract.ALIASES)==15
    assert '27 calibration bytes' in text and sum(row['size'] for row in contract.CALIBRATIONS)==27
    assert '22 caller bytes' in text and sum(row['end']-row['start'] for row in contract.UNITS[0]['code'])==22
    assert 'all four outside returns' in text and len(contract.BOUNDARIES)==4
    assert '33 actual conditional branch sites' in text and len(proof.REQUIRED_BRANCHES)==33
    assert 'four exact one-sided branch sites' in text and len(proof.FIXED_BRANCHES)==4
    for value in ('0004EDBE','0004EDC6','0004EDC0','0004EDC4','0004F19C','0004F282','FFFF2494',
            '0004EDD2','0004EDD4','0004EDF8','0004EDFA','0004F736','0004FAA0','FFFF2448','FFFF418C'):
        assert value in text
    assert 'explicit controlled configuration bit7' in text and 'full coordinator' in text
    assert 'explicit controlled shared status' in text
