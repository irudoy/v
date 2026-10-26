"""Exact scalar RAM leaf fixture, arithmetic boundaries and source refusals."""

import json
import pytest

from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import scalar_ram_leaf_contract as contract,scalar_ram_leaf_matrix as matrix
from kb import scalar_ram_leaf_semantics as scalar,scalar_ram_leaf_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as withdrawal
from kb import scalar_ram_leaf_capture_evidence as proof


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    context=matrix.context(source,case);memory=matrix.memory(case);calibration=matrix.calibrations(source,image,case)
    return scalar.evaluate(entry,memory,calibration,context,case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('entry,fields',((0x39588,('slew_a_current','slew_a_target')),(0x39874,('slew_b_current','slew_b_target'))))
@pytest.mark.parametrize('current,target,expected',((30,60,32),(60,30,60),(30,31,31),(254,255,255),(255,0,255),(0,0,0)))
def test_slew_retains_current_above_target_and_advances_at_most_two(entry,fields,current,target,expected):
    result=evaluate(entry,**dict(zip(fields,(current,target))))
    assert result['registers'][0]==expected and result['registers'][4]==expected
    assert result['sr']&1==int(current+2>target)


@pytest.mark.parametrize('flag,expected',((0,0),(1,1),(0x100,0),(0x101,1)))
def test_comparison_helper_subtracts_only_for_zero_low_byte_flag(flag,expected):
    value=evaluate(0x259BE,raw_r4=1,raw_r5=0,raw_r6=1,raw_r7=flag)
    assert value['registers'][0]==value['registers'][2]==expected
    assert value['branches'][0]['delay'] is True and value['path'][-1]==0x259CE


@pytest.mark.parametrize('left,right,gain,expected',((100,50,16384,50),(50,100,16384,0),(16384,0,1,1),(65535,0,65535,65535)))
def test_difference_product_uses_unsigned_words_and_independent_high_word_cap(left,right,gain,expected):
    value=evaluate(0x4AB94,state_231a=left,word_230c=right,product_gain=gain)
    assert int.from_bytes(value['ram'][0x18E2:0x18E4],'big')==expected
    assert value['registers'][2]==expected


@pytest.mark.parametrize('signed_a,signed_b,expected',((32768,32768,0),(32767,32767,65535)))
def test_sum_clamps_after_both_signed_word_terms_and_optional_byte(signed_a,signed_b,expected):
    value=evaluate(0x468B0,sum_signed_a=signed_a,sum_signed_b=signed_b)
    assert int.from_bytes(value['ram'][0x173A:0x173C],'big')==expected


@pytest.mark.parametrize('delta,word,correction,expected',((0,0,0,16384),(0xFFFFFFFF,0,0,16383),
    (0xFFFFC000,128,256,384),(0x7FFFFFFF,0,0,0),(0xFFFF0000,0,0,0),(65535,0,0,65535)))
def test_base_accumulator_retains_low32_wrap_signed_compare_and_both_caps(delta,word,correction,expected):
    value=evaluate(0x554AE,accumulator_delta=delta,word_230c=word,accumulator_correction=correction)
    assert value['registers'][0]==value['registers'][2]==expected
    assert int.from_bytes(value['ram'][0x231A:0x231C],'big')==expected


def test_timing_fields_mask_high_bits_and_clamp_each_independent_difference():
    value=evaluate(0x4AF38,timing_first=255,timing_second=128,timing_offset=10,timing_configuration=2)
    assert value['ram'][0x12DE:0x12E1]==bytes((127,0,0)) and value['ram'][0x23BD]==117


@pytest.mark.parametrize('first,second,trim,expected',((255,255,0,255),(0,0,255,0),(30,40,32,68)))
def test_byte_combination_store_occurs_in_the_natural_RTS_delay_slot(first,second,trim,expected):
    value=evaluate(0x4BB6A,combine_first=first,combine_second=second,combine_trim=trim)
    assert value['ram'][0x23C5]==value['registers'][0]==expected
    assert value['path'][-2:]==(0x4BB9E,0x4BBA0)


@pytest.mark.parametrize('mode,flags,status,expected',((1,64,32,10),(2,64,32,10),(3,64,0,20),(0,0,0,10),(0,0,32,20)))
def test_state_latch_preserves_both_mode_shortcuts_flag_and_status_selection(mode,flags,status,expected):
    value=evaluate(0x4C136,latch_mode=mode,latch_flags=flags,latch_status=status)
    assert value['ram'][0x2404]==expected
    assert value['ram'][0x24D2]==(0xA7 if flags else 0xA5)


@pytest.mark.parametrize('state,expected',((0,0),(1,0),(127,126),(128,129),(255,0)))
def test_signed_byte_decay_keeps_unreachable_clamps_separate_from_feasible_paths(state,expected):
    value=evaluate(0x4E112,decay_state=state,decay_latched=0,decay_flags=16)
    assert value['ram'][0x1513]==expected and value['ram'][0x25FD]==10
    assert not set(value['path'])&set(transfers.INFEASIBLE_INSTRUCTIONS)
    assert value['path'][-2:]==(0x4E15A,0x4E15C)


def test_existing_nonzero_decay_latch_returns_signed_byte_without_stores():
    value=evaluate(0x4E112,decay_latched=128,decay_flags=16)
    assert value['registers'][0]==0xFFFFFF80 and value['sr']&1==0
    assert value['ram'][0x1513]==10 and value['ram'][0x25FD]==128
    assert value['path'][-2:]==(0x4E15E,0x4E160)


def test_signed_selector_returns_its_literal_offset_and_publishes_the_selected_negative_word():
    value=evaluate(0x70D82,selector_flags=2,selector_state=0,selector_candidate=65535,selector_primary=0)
    assert value['registers'][0]==0x736 and value['ram'][0x2438:0x243A]==b'\xff\xff'
    assert value['ram'][0x19C2:0x19C4]==b'\xff\xff'


@pytest.mark.parametrize('flags,gate,current,threshold,output,new_flags',(
    (0,32,200,100,0x5B,8),(8,32,200,100,8,8),(0,0,200,100,0,0),
    (0,32,100,200,0x9F6,0),(0,32,32768,32767,0x5B,8)))
def test_limit_latch_retains_each_return_carrier_and_unsigned_word_order(flags,gate,current,threshold,output,new_flags):
    value=evaluate(0xA5530,limit_flags=flags,limit_gate=gate,limit_current=current,limit_threshold=threshold)
    assert value['registers'][0]==output and value['ram'][0x4204]==new_flags
    assert value['path'][-2] in (0xA5558,0xA555C)


def test_exact_fixture_preserves_all_stock_code_and_only_relocates_declared_native_RAM_pointers():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and len(aliases)==31
    assert len(contract.ENTRIES)==12 and len(contract.UNIT['pools'])==59


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_rejects_table_identity_geometry_scale_units_caller_and_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert flag+' = false' in text
    path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,value',(('sum_signed_a',65536),('sum_configuration',256),
    ('accumulator_delta',-1),('initial_sr',2),('variant',True),('raw_r7',1<<32)))
def test_raw_input_domain_rejects_changed_width_boolean_numeric_and_SR_premises(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x468B0);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


def test_published_address_originals_and_source_counts_are_read_from_executed_descriptors():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='scalar_ram_leaf_paths']
    text=(repo.ROOT/'defs/JK08A.scalar-ram-leaves.md').read_text();words=' '.join(text.split())
    assert len(rows)==19 and len({row['owner'] for row in rows})==16
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+
        '` | `'+row['original_claim_sha256']+'` |' for row in rows]
    facts=(('364 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),364),
        ('728 code bytes',sum(b-a for a,b in contract.SPANS),728),
        ('59 literal/configuration spans',len(contract.UNIT['pools']),59),
        ('31 pointer aliases',len(contract.UNIT['aliases']),31),
        ('32 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),32))
    for phrase,actual,wanted in facts:assert phrase in text and actual==wanted
    removed=sum(sum(withdrawal.selector(row,row['owner'],item)
        for marker in json.loads(row['original_ledger_json']) for item in marker.get('dependency',())) for row in rows)
    assert f'Exactly {removed} matching ledger selectors' in words and removed==19
    assert 'twelve complete retained function documents' in words and len(declared['function'][:12])==12
    assert 'three unreachable instructions' in words and len(transfers.INFEASIBLE_INSTRUCTIONS)==3
    assert len(transfers.FIXED_BRANCHES)==2 and '4E140' in text and '4E14E' in text
    assert '42 families and 88 capture bindings' in words
    assert len(registry.FAMILIES)==42 and len(registry.captures())==88
    assert 'preceding five adapters' in words and proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==5
    def test_count(value):
        if isinstance(value,dict):return int(value.get('kind')=='test')+sum(test_count(item) for item in value.values())
        if isinstance(value,list):return sum(test_count(item) for item in value)
        return 0
    assert 'two original fuel-base TEST attachments' in words
    assert sum(test_count(json.loads(row['original_native_json'])) for row in declared['function'][:12])==2
