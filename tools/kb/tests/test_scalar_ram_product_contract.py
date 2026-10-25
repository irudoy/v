"""Exact scalar product input, width, truncation, carry and source boundaries."""

import json
import pytest

from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import scalar_ram_product_contract as contract,scalar_ram_product_matrix as matrix
from kb import scalar_ram_product_semantics as scalar,scalar_ram_product_transfers as transfers
from kb import scalar_ram_product_capture_evidence as proof
from kb import scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('previous,target,gain,expected',((1,0,32,0),(256,0,32,65535),
    (0,65535,255,32767),(0x1000000,0,255,32768)))
def test_signed_error_truncates_each_stage_toward_zero_before_word_saturation(previous,target,gain,expected):
    value=evaluate(0x5279C,previous_long=previous,target_word=target,error_gain=gain)
    assert int.from_bytes(value['ram'][0x1A66:0x1A68],'big')==expected
    assert value['registers'][2]==0xFFFF8000 and value['registers'][0]==0x7DA


def test_error_disable_preserves_the_incoming_R2_and_the_natural_delayed_zero():
    value=evaluate(0x5279C,error_flags=64,raw_r2=0x01234567)
    assert value['ram'][0x1A66:0x1A68]==bytes(2) and value['registers'][2]==0x01234567
    assert value['registers'][5]==0x01004184 and value['sr']&1==0
    assert value['branches'][0]==dict(site=0x527AA,target=0x527FC,kind='taken',delay=True)


@pytest.mark.parametrize('gain,term,expected',((255,32768,32896),(255,32767,32639),(1,65535,0)))
def test_signed_additive_retains_negative_truncation_and_exact_byte_word_bounds(gain,term,expected):
    value=evaluate(0x52902,additive_gain=gain,signed_term=term,bypass_flags=0,bypass_configuration=0)
    assert int.from_bytes(value['ram'][0x2300:0x2302],'big')==expected
    assert not set(value['path'])&set(transfers.INFEASIBLE_INSTRUCTIONS)


@pytest.mark.parametrize('flags,configuration,expected',((0,0,512),(32,0,512),(0,4,512),(32,4,0)))
def test_additive_zero_override_requires_both_real_RAM_and_ROM_bits(flags,configuration,expected):
    value=evaluate(0x52902,bypass_flags=flags,bypass_configuration=configuration)
    assert value['registers'][0]==value['registers'][5]==expected
    assert value['registers'][6]==0x010022F8


@pytest.mark.parametrize('a,b,factor,pulse,first,second',((128,64,89,32000,44,44000),
    (255,255,255,65535,255,65535),(0,255,255,65535,0,0)))
def test_byte_product_and_pulse_word_have_separate_shifts_and_caps(a,b,factor,pulse,first,second):
    value=evaluate(0x5444C,product_a=a,product_b=b,product_factor=factor,pulse_word=pulse)
    assert value['ram'][0x33BE]==first
    assert int.from_bytes(value['ram'][0x415A:0x415C],'big')==second
    assert value['registers'][6]==second and 0x54490 not in value['path']


def test_blend_keeps_the_low_half_carry_and_full_high_sum_before_final_cap():
    value=evaluate(0xA5284,raw_r4=65535,raw_r5=65535,blend_a=255,blend_b=255)
    assert value['registers'][0]==65535 and value['registers'][4]==65536
    assert value['registers'][2]==0xFFFFFFFF and value['registers'][6]==1
    assert value['sr']&1==1 and value['path'][-2:]==(0xA52E0,0xA52E2)


def test_blend_ignores_only_the_declared_upper_halves_of_both_arguments():
    first=evaluate(0xA5284,raw_r4=65535,raw_r5=32768)
    second=evaluate(0xA5284,raw_r4=0xAAAAFFFF,raw_r5=0xBBBB8000)
    assert first['exit']==second['exit'] and first['ram']==second['ram']


def test_error_flag_is_one_complete_input_byte_and_adapter_memory_binding():
    source=contract.descriptor(repo.ROOT)
    assert ('error_flags',0x4184,1) in matrix.RAM_FIELDS and matrix.WIDTHS['error_flags']==8
    assert dict(offset=0x4184,width=1,field='error_flags') in source['adapter']['memory']
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x5279C,error_flags=64)
    matrix.require_case(case);assert matrix.memory(case)[0x4184]==64


def test_exact_fixture_changes_only_the_eight_declared_long_pointer_aliases():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and len(aliases)==8


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_product_source_refuses_semantic_caller_geometry_units_scale_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,value',(('error_flags',256),('previous_long',-1),('target_word',65536),
    ('product_factor',True),('raw_r4',1<<32),('initial_sr',2)))
def test_raw_domain_rejects_width_boolean_signed_and_SR_substitutions(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x5279C);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


def test_published_product_counts_and_originals_bind_the_executed_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='scalar_ram_product_paths']
    text=(repo.ROOT/'defs/JK08A.scalar-ram-products.md').read_text();words=' '.join(text.split())
    assert len(rows)==7 and len({row['owner'] for row in rows})==7
    assert len(declared['reference'])==125 and len({row['owner'] for row in declared['reference']})==95
    assert len(declared['function'])==67
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+
        '` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('199 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),199),
        ('398 code bytes',sum(b-a for a,b in contract.SPANS),398),('24 literal/configuration spans',len(contract.UNIT['pools']),24),
        ('8 pointer aliases',len(contract.UNIT['aliases']),8),('13 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),13),
        ('3 fixed conditional outcomes',len(transfers.FIXED_BRANCHES),3),
        ('2 unreachable instructions',len(transfers.INFEASIBLE_INSTRUCTIONS),2)):
        assert phrase in words and actual==wanted
    owners={row['owner']:row for row in declared['reference']}
    removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))
        -sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==117 and '117 matching ledger selectors' in words
    assert 'thirteen families and forty-seven capture bindings' in words
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'preceding six adapters' in words and proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==6
