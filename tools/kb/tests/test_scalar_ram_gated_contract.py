"""Exact gated/indexed input, physical alias and independent scalar boundaries."""

import json
import pytest

from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import scalar_ram_gated_contract as contract,scalar_ram_gated_matrix as matrix
from kb import scalar_ram_gated_semantics as scalar,scalar_ram_gated_transfers as transfers
from kb import scalar_ram_gated_capture_evidence as proof
from kb import scalar_ram_leaf_withdrawal_contract as withdrawal


def inputs(entry,**changes):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=entry)
    for name,value in changes.items():
        field=matrix.indexed_field(name,changes.get('raw_r4' if entry==0x3D45C else 'raw_r5',case['raw_r4' if entry==0x3D45C else 'raw_r5'])&255)
        case[field if name in {row[0] for row in matrix.INDEXED_ARRAYS} else name]=value
    return case


def evaluate(entry,**changes):
    case=inputs(entry,**changes);source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(entry,matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),case['initial_sr'],bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('candidate,current,expected,stored',((10,20,10,True),(20,10,10,False),(20,20,20,False)))
def test_indexed_minimum_preserves_its_real_delayed_local_store(candidate,current,expected,stored):
    value=evaluate(0x3D45C,raw_r4=1,candidate=candidate,current=current)
    assert value['ram'][0x3F4D]==expected and int.from_bytes(value['frame'][156:160],'big')==candidate
    assert value['registers'][4]==1 and value['registers'][0]==1
    assert (0x3D4A2 in value['path']) is stored and 0x3D49C in value['path']


def test_last_byte_index_has_no_ready_mask_bit_and_retains_the_natural_return():
    value=evaluate(0x3D45C,raw_r4=0xAAAAFFFF,ready_mask=255)
    assert value['registers'][4]==255 and value['registers'][2]==256
    assert value['registers'][0]==0x57A and 0x3D49C not in value['path']
    assert value['frame']==bytes([0xA5])*192 and value['path'][-2:]==(0x3D4A4,0x3D4A6)


@pytest.mark.parametrize('mode,state,load,flags,expected',((0,25,51,0xA5,0xBD),
    (2,25,51,255,0xEF),(1,25,51,255,0xE7),(0,19,51,255,0xE7),(0,25,50,255,0xEF)))
def test_status_masks_preserve_both_thresholds_mode_shortcuts_and_strict_long_compare(mode,state,load,flags,expected):
    value=evaluate(0x44448,status_mode=mode,status_state=state,status_load=load,status_flags=flags)
    assert value['ram'][0x24D1]==expected
    if mode==2 and state==25:
        assert 0x444A2 in value['path'] and 0x444A8 in value['path'] and value['tags']['first_flags']==255


@pytest.mark.parametrize('weight,expected',((0,32768),(32768,65535),(65535,32767)))
def test_signed_blend_retains_both_direct_endpoints_and_negative_high_half(weight,expected):
    value=evaluate(0x74C08,blend_weight=weight,blend_first=32768,blend_second=32767)
    assert int.from_bytes(value['ram'][0x18F4:0x18F6],'big')==expected
    assert value['path'][-2:]==(0x74C7E,0x74C80)
    assert not any(0x74C48<=site<0x74C54 for site in value['path'])


@pytest.mark.parametrize('primary,external,flags,first,upper,third,fourth',(
    (1,0,0,100,400,200,300),(0,0,0,700,400,200,300),
    (0,0,8,700,500,900,900),(0,1,8,600,500,900,900)))
def test_bound_selection_preserves_four_distinct_actual_word_publications(primary,external,flags,first,upper,third,fourth):
    value=evaluate(0x777FA,bound_configuration=primary,bound_external_configuration=external,bound_flags=flags)
    assert [int.from_bytes(value['ram'][at:at+2],'big') for at in (0x3480,0x3484,0x347E,0x3482)]==[first,upper,third,fourth]
    assert value['registers'][0]==0xB8A and value['path'][-2:]==(0x77876,0x77878)


def test_indexed_reset_and_status_gain_share_one_authoritative_physical_byte():
    assert matrix.INDEXED_ALIASES=={('delay',40):'status_gain'}
    assert matrix.indexed_field('delay',40)=='status_gain' and 'delay_040' not in matrix.WIDTHS
    source=contract.descriptor(repo.ROOT)
    assert [row for row in source['adapter']['memory'] if row['offset']<=0x1958<row['offset']+row['width']]==[
        dict(offset=0x1958,width=1,field='status_gain')]
    for byte in (0,5,17,64,255):
        case=inputs(0x907E8,raw_r4=0,raw_r5=40,status_gain=byte)
        memory=matrix.memory(case)
        assert memory[0x1958]==byte and memory[0x1957]==memory[0x1959]==17
    value=evaluate(0x907E8,raw_r4=0,raw_r5=40,status_gain=5)
    assert value['ram'][0x1958]==0 and value['ram'][0x1957]==value['ram'][0x1959]==17
    assert value['registers'][0]==40 and value['path'][-2:]==(0x90876,0x90878)


def test_gain_variation_reaches_the_same_byte_read_by_the_status_path():
    low=evaluate(0x44448,status_state=25,status_gain=5,status_load=51)
    high=evaluate(0x44448,status_state=25,status_gain=6,status_load=51)
    assert low['ram'][0x24D1]==0xBD and high['ram'][0x24D1]==0xAD


@pytest.mark.parametrize('ready,flags,delay',((0,0x5B,17),(255,0x5A,0)))
def test_indexed_active_paths_preserve_both_actual_delayed_flag_stores(ready,flags,delay):
    value=evaluate(0x907E8,raw_r4=1,raw_r5=0,reset_ready=ready)
    assert value['ram'][0x14F0]==flags and value['ram'][0x1930]==delay
    assert value['path'][-1] in (0x90852,0x90882)


def test_fixture_binds_the_literal_gap_and_natural_MACL_return_separately():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert (0x74C08,0x74C48) in contract.SPANS and (0x74C54,0x74C82) in contract.SPANS
    assert not any(first<=0x74C4E<last for first,last in contract.SPANS)
    assert any(row['address']==0x74C4E and row['size']==2 for row in contract.UNIT['pools'])
    assert any(row['address']==0x74C52 and row['size']==2 for row in contract.UNIT['pools'])
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and len(aliases)==17


@pytest.mark.parametrize('field,value',(('status_gain',256),('candidate_255',-1),('request_255',65536),
    ('raw_r5',True),('raw_r4',1<<32),('initial_sr',2)))
def test_complete_indexed_raw_widths_and_context_refuse_substitution(field,value):
    case=inputs(0x907E8);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_identity_scale_geometry_units_caller_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_gated_counts_and_exact_originals_bind_the_executed_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='scalar_ram_gated_paths']
    text=(repo.ROOT/'defs/JK08A.scalar-ram-gated.md').read_text();words=' '.join(text.split())
    assert len(rows)==5 and len(declared['reference'])==129 and len(declared['function'])==70
    assert len({row['owner'] for row in declared['reference']})==98
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+
        '` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('292 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),292),
        ('584 code bytes',sum(b-a for a,b in contract.SPANS),584),('50 literal/configuration spans',len(contract.UNIT['pools']),50),
        ('17 pointer aliases',len(contract.UNIT['aliases']),17),('25 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),25)):
        assert phrase in words and actual==wanted
    owners={row['owner']:row for row in declared['reference']}
    removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))
        -sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==121 and '121 matching ledger selectors' in words
    assert 'thirteen families and forty-seven capture bindings' in words
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'preceding seven adapters' in words and proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==7
