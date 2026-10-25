"""Natural register-helper byte boundary and independent arithmetic contracts."""

from copy import deepcopy
import json

import pytest

from kb import repo,test_contract
from kb import register_only_helpers_contract as contract,register_only_helpers_matrix as matrix
from kb import register_only_helpers_semantics as scalar
from kb import register_only_withdrawal_contract as withdrawal


def evaluate(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry,**changes)
    context=matrix.context({},case)
    return scalar.evaluate(entry,context,case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('entry,amount',((0x224F8,7),(0x224FA,6),(0x2251C,11)))
@pytest.mark.parametrize('value,negative',((0,False),(1,False),(0x7FFFFFFF,False),(0x80000000,True),(0xFFFFFFFF,True)))
def test_independent_shift_results_preserve_sign_and_exact_final_T_bit(entry,amount,value,negative):
    result=evaluate(entry,raw_r0=value,initial_sr=0x3F1)
    signed=value-(1<<32) if negative else value
    assert result['output']==(signed>>amount)&0xFFFFFFFF
    assert result['sr']==0x3F0|((value>>(amount-1))&1)
    assert result['path'][-2:]==(result['return_site'],result['return_site']+2)
    if entry==0x2251C:
        assert [row['site'] for row in result['physical']]==[0x2251C,0x2252E]
        assert result['frame'][156:160]==matrix.DEFAULTS['raw_r1'].to_bytes(4,'big')
    else:assert result['physical']==[]


@pytest.mark.parametrize('left,right,subtract,flag,expected',(
    (1,0,1,0,0),(1,0,1,1,1),(1,0,1,0x100,0),(1,0,1,0x101,1),
    (0x80000000,0,0,0,1),(0x7FFFFFFF,0,0,0,0),(0,0,1,1,1),(0x80000000,0,1,1,0)))
def test_conditional_signed_comparison_uses_low_byte_flag_and_modular_subtraction(left,right,subtract,flag,expected):
    value=evaluate(0x259D0,raw_r4=left,raw_r5=right,raw_r6=subtract,raw_r7=flag)
    assert value['output']==expected and value['registers'][7]==flag&255
    assert value['physical']==[]
    assert value['branches'][0]['delay'] is True
    assert value['branches'][0]['kind']==('fallthrough' if flag&255 else 'taken')


@pytest.mark.parametrize('left,right,fraction,expected',(
    (0,65536,32768,32768),(65536,0,32768,32768),(0,65536,65536,0),
    (0xFFFFFFFF,0,1,0xFFFF0000),(0x80000000,0,0xFFFFFFFF,0x7FFF8000),
    (1,1,0xFFFFFFFF,1)))
def test_interpolation_uses_low32_product_high_word_and_unsigned_branch(left,right,fraction,expected):
    value=evaluate(0x26740,raw_r0=left,raw_r2=right,raw_r3=fraction)
    assert value['output']==expected and value['registers'][1]==value['macl']
    assert bool(value['physical'])==(right<left)
    assert value['branches'][0]['kind']==('taken' if right>=left else 'fallthrough')


def test_mask_helper_combines_only_register_arguments_and_keeps_upper_bits_in_R4():
    value=evaluate(0x50A4C,raw_r4=0x80000020,raw_r5=0x01000004,raw_r6=3,initial_sr=0x3F1)
    assert value['output']==39 and value['registers'][4]==0x81000027
    assert value['sr']==0x3F1 and value['physical']==[]


def test_exact_fixture_has_all_six_natural_entries_and_full_fallthrough_without_relocations_or_stubs():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    assert contract.independent_fixture(source,image)==(image,[])
    assert contract.ENTRIES==(0x224F8,0x224FA,0x2251C,0x259D0,0x26740,0x50A4C)
    assert contract.SPANS[:2]==((0x224F8,0x224FA),(0x224FA,0x22508))
    assert contract.UNIT['pools']==contract.UNIT['aliases']==[]
    assert sum(last-first for first,last in contract.SPANS)==112
    assert all(source[name] is False for name in contract.FLAGS)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_added_semantic_scale_units_caller_geometry_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('old,new',(('frame_bytes = 192','frame_bytes = 352'),
    ('context_bytes = 80','context_bytes = 76'),('end = 140552','end = 140550'),
    ('width = 1','width = 2')))
def test_source_refuses_partial_return_delay_and_changed_observer_domains(tmp_path,old,new):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert old in text
    path.write_text(text.replace(old,new,1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,value',(('raw_r0',-1),('raw_r7',1<<32),('raw_r4',True),
    ('variant',256),('initial_sr',2),('entry',0x224FC)))
def test_input_boundary_requires_full_typed_registers_and_exact_natural_entries(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x224F8);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


def test_published_originals_entries_and_counts_follow_the_executed_descriptors():
    rows=withdrawal.descriptor(repo.ROOT)['reference']
    text=(repo.ROOT/'defs/JK08A.register-only-helpers.md').read_text()
    published=[line for line in text.splitlines() if line.startswith('| `7mfk:')]
    assert published==['| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+
        '` | `'+row['original_claim_sha256']+'` |' for row in rows]
    assert len(rows)==12 and len({row['owner'] for row in rows})==11
    assert '56 stock instructions' in text and sum((b-a)//2 for a,b in contract.SPANS)==56
    assert 'six natural entries' in text and len(contract.ENTRIES)==6
    assert '112 bound code bytes' in text and sum(row['size'] for row in contract.BOUND_SPANS)==112
    owners={row['owner']:row for row in rows}
    removed=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))
        -sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json'])) for row in owners.values())
    assert 'fourteen exact' in text and removed==14
