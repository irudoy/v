"""Natural bank2 CVTC source and independent scalar/refusal contract."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import repo,test_contract
from kb import exhaust_cvtc_contract as contract,exhaust_cvtc_matrix as matrix
from kb import exhaust_cvtc_access_contract as owning,exhaust_cvtc_semantics as scalar


def inputs(entry=0xC1DEC,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return case,source,matrix.memory(case),matrix.calibrations(source,image,case),matrix.context(source,case)


def test_eleven_exact_original_relations_preserve_every_complete_grouped_native_owner():
    rows=owning.descriptor(repo.ROOT)['reference'];assert len(rows)==11
    assert len({row['owner'] for row in rows})==6
    assert {row['function'] for row in rows}=={0xC1DEC,0xC2040}
    originals={row['owner']:json.loads(row['original_native_json']) for row in rows}
    expected=deepcopy(originals)
    for row in rows:
        old,new=json.loads(row['original_claim_json']),json.loads(row['proposed_claim_json'])
        assert old['evidence']==[]
        assert test_contract.exact(new,dict(old,evidence=[owning.item(row)]))
        assert row['original_ledger_json']==row['proposed_ledger_json']
        links=[link for link in expected[row['owner']]['link'] if link['type']==old['type'] and link['to']==old['to']]
        assert len(links)==1;links[0].setdefault('evidence',[]).append(owning.item(row))
    for row in rows:
        assert test_contract.exact(expected[row['owner']],json.loads(row['proposed_native_json']))
        assert test_contract.exact(originals[row['owner']]['symbol'],expected[row['owner']]['symbol'])
    tested={item['key'] for doc in originals.values() for symbol in doc['symbol']
        for item in symbol.get('evidence',()) if item.get('kind')=='test'}
    assert tested=={'test_indexed_state_longword_path','test_indexed_input_word_path','test_indexed_mode_byte_paths'}
    assert {row['declared_width'] for row in rows if row['address']!=0xFFFF1AAE}=={'unset'}
    assert {row['declared_signed'] for row in rows if row['address']!=0xFFFF1AAE}=={'unset'}


def test_exact_natural_fixture_relocates_only_declared_pointers_and_preserves_every_instruction():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    assert contract.BOUNDARIES==() and contract.ENTRIES==(0xC1DEC,0xC2040)
    assert next(row for row in contract.UNIT['pools'] if row['address']==0xC203C)['stock_hex']=='ffff0000'
    assert not any(row['address']==0xC203C for row in aliases)


def test_published_address_direction_and_site_table_reads_the_executed_owning_descriptor():
    rows=owning.descriptor(repo.ROOT)['reference']
    text=(repo.ROOT/'defs/JK08A.exhaust-cvtc-accesses.md').read_text()
    published=[line for line in text.splitlines() if line.startswith('| FFFF')]
    expected=['| '+f'{row["address"]:08X}'+' | '+f'{row["function"]:08X}'+' | '+row['direction']+
        ' | '+','.join(f'{site:08X}' for site in row['sites'])+' |' for row in rows]
    assert published==expected and len(published)==11


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_geometry_sensor_scheduler_scale_units_and_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in text
    path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('old,new',(('bank_index = 1','bank_index = 0'),
    ('battery_minimum = 1','battery_minimum = 0'),('frame_bytes = 192','frame_bytes = 352'),
    ('context_bytes = 80','context_bytes = 76'),('width = 4','width = 2')))
def test_exact_input_storage_and_pointer_premises_are_pinned(tmp_path,old,new):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert old in text
    path.write_text(text.replace(old,new,1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,value',(('raw_r4',0),('raw_r4',2),('battery',0),('battery',256),
    ('mode',256),('current',65536),('payload',1<<32),('initial_sr',2),('curve_kind',5)))
def test_input_only_domain_refuses_unproved_banks_zero_divisors_widths_and_SR(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0xC1DEC,**{field:value})
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('coordinate,expected',((0,0),(10,0),(11,4),(15,25),(20,50),(21,54),(79,255),(255,255)))
def test_independent_curve_clamps_and_truncates_over_actual_search_intervals(coordinate,expected):
    curve=bytes((0,50,100,150,200,225,250,255,17));axis=bytes((10,20,30,40,50,60,70,79))
    assert scalar.curve_value(curve,axis,coordinate)['value']==expected


def test_independent_descending_curve_uses_left_minus_truncated_fraction():
    axis=bytes((10,20,30,40,50,60,70,80));curve=bytes((255,205,155,105,55,30,5,0,7))
    value=scalar.curve_value(curve,axis,11)
    assert value['value']==251 and value['index']==0 and value['fraction']==6553
    assert value['visited']==(7,6,5,4,3,2,1,0)


@pytest.mark.parametrize('mode,flags,mask,current,expected',(
    (0,5,2,512,1),(0,1,2,512,0),(1,0,2,512,0),(1,1,0,512,2),
    (2,1,0,0,0),(2,1,0,512,2),(2,5,2,0,1),(255,0,0,0,255)))
def test_state_transition_order_preserves_zero_then_reenable_and_opaque_nonzero_modes(mode,flags,mask,current,expected):
    _,_,before,calibration,context=inputs(mode=mode,flags=flags,previous_mask=mask,current=current)
    value=scalar.evaluate(0xC1DEC,before,calibration,context)
    assert value['mode']==value['memory'][0x1B1D]==expected


@pytest.mark.parametrize('error,coefficient,expected',((0,625,0),(1,625,256),(1000,625,256000),
    (65535,0,0),(65535,65535,0x04000000)))
def test_split_quotient_and_remainder_bind_full_fixed_point_product(error,coefficient,expected):
    _,_,before,calibration,context=inputs(error=error,coefficient=coefficient,coordinate=170)
    value=scalar.evaluate(0xC1DEC,before,calibration,context)
    assert value['output']==expected
    assert int.from_bytes(value['memory'][0x1AA8:0x1AAC],'big')==expected


@pytest.mark.parametrize('accumulator,expected',((0,0),(0x08000000,0),(0x09000000,0x01000000),
    (0x0C000000,0x04000000),(0x10000000,0x04000000)))
def test_alternate_path_retains_low32_wrap_signed_gate_gain_and_cap(accumulator,expected):
    _,_,before,calibration,context=inputs(configuration=0,coordinate=170,accumulator=accumulator)
    value=scalar.evaluate(0xC1DEC,before,calibration,context)
    assert value['output']==expected


@pytest.mark.parametrize('mode,previous,current_mask,current,lag,decay,expected',(
    (0,2,0,512,256,10,0),(1,2,0,512,256,10,256),(2,0,0,512,256,10,502),
    (2,0,0,512,0,10,512),(2,0,0,512,65535,255,0),(2,0,2,512,256,10,492),
    (2,0,0,65535,0,0,1024),(255,2,0,512,256,10,256)))
def test_duty_request_lag_copy_and_decay_use_exact_unsigned_word_inputs(mode,previous,current_mask,current,lag,decay,expected):
    _,_,before,calibration,context=inputs(0xC2040,mode=mode,previous_mask=previous,current_mask=current_mask,
        current=current,lag=lag,decay=decay)
    value=scalar.evaluate(0xC2040,before,calibration,context)
    assert value['preliminary']==256 and value['output']==expected
    assert int.from_bytes(value['memory'][0x1AAE:0x1AB0],'big')==expected
    assert int.from_bytes(value['memory'][0x1AB6:0x1AB8],'big')==(current if value['copied'] else lag)


def test_inputs_retain_all_complete_neighbor_RAM_without_expected_or_terminal_fields():
    case,source,before,calibration,context=inputs()
    assert len(context)==20 and len(before)==65536
    assert set(case)=={*matrix.DEFAULTS,'kind','index','entry'}
    assert all(not any(part in key for part in ('expected','terminal','result','output')) for key in case)
    for name,at,width in matrix.RAM_FIELDS:
        assert before[at-1]==before[at+width]==0xA5
