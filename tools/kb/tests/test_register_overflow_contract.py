"""Exact stock ADDV/SUBV, minimum-word NEG and complete native helper boundaries."""

import json
import pytest

from kb import repo,proof_adapter
from kb import ordinary_access_registry as registry
from kb import register_overflow_path_contract as contract,register_overflow_matrix as matrix
from kb import register_overflow_semantics as scalar,register_overflow_transfers as transfers
from kb import register_overflow_capture_evidence as proof
from kb import scalar_ram_leaf_withdrawal_contract as withdrawal


def evaluate(first,second,sr=0):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x265C4,raw_r4=first,raw_r5=second,initial_sr=sr)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    return scalar.evaluate(case['entry'],matrix.memory(case),matrix.calibrations(source,image,case),
        matrix.context(source,case),sr,bytes([0xA5])*192,0x02001000,0x02100000)


@pytest.mark.parametrize('first,second,output,r4,r5,t,ret',(
    (0,1,1,0,1,0,0x265D6),
    (0x7FFFFFFF,1,0x7FFFFFFF,0x7FFFFFFF,0x80000000,1,0x265E2),
    (0,0xFFFFFFFF,0xFFFFFFFF,0xFFFFFFFF,1,0,0x265CE),
    (0x80000000,0xFFFFFFFF,0x80000000,0x7FFFFFFF,1,1,0x265DC),
    (1,0x80000000,0x80000000,0x80000001,0x80000000,1,0x265DC),
    (0xFFFFFFFF,0x80000000,0x7FFFFFFF,0x7FFFFFFF,0x80000000,0,0x265CE),
    (0x80000000,0x80000000,0,0,0x80000000,0,0x265CE)))
@pytest.mark.parametrize('sr',(0,1,0x3F0,0x3F1))
def test_exact_stock_piecewise_result_register_mutations_T_and_each_natural_return(first,second,output,r4,r5,t,ret,sr):
    value=evaluate(first,second,sr)
    assert value['registers'][0]==output and value['registers'][4:6]==(r4,r5)
    assert value['sr']==(sr&~1)|t and value['path'][-2:]==(ret,ret+2)
    assert value['ram']==bytes([0xA5])*65536 and value['frame']==bytes([0xA5])*192


def test_minimum_second_operand_retains_NEG_wrap_instead_of_an_ideal_saturating_sum():
    positive=evaluate(1,0x80000000);negative=evaluate(0xFFFFFFFF,0x80000000)
    assert positive['registers'][0]==0x80000000 and positive['registers'][0]!=0x80000001
    assert negative['registers'][0]==0x7FFFFFFF and negative['registers'][0]!=0x80000000


def test_exact_stock_instruction_forms_bind_both_overflow_operations_and_four_RTS_words():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    assert int.from_bytes(image[0x265CA:0x265CC],'big')==0x345B
    assert int.from_bytes(image[0x265D2:0x265D4],'big')==0x354F
    assert {int.from_bytes(image[at:at+2],'big')&0xF00F for at in (0x265CA,0x265D2)}=={0x300B,0x300F}
    assert sum(image[at:at+2]==b'\x00\x0b' for first,last in contract.SPANS for at in range(first,last,2))==4
    fixture,aliases=contract.independent_fixture(source,image)
    assert fixture==image and aliases==[] and contract.CONFIGURATION==[]
    assert contract.UNIT['pools']==[
        dict(address=0x265E8,size=4,stock_hex='80000000'),dict(address=0x265EC,size=4,stock_hex='7fffffff')]


@pytest.mark.parametrize('root',transfers.NATIVE_RAM_ROOTS)
@pytest.mark.parametrize('form',('native','alias','interval'))
def test_selected_native_RAM_root_and_its_alias_are_absent_from_all_admitted_memory_events(root,form):
    rows=[row for row in withdrawal.descriptor(repo.ROOT)['reference'] if row['component']=='register_overflow_paths']
    original,native,alias=root;at=native if form=='native' else alias;width=1
    if form=='interval':at-=1;width=2
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(
        site=0x265CA,mode='read',address=at,width_bytes=width,register=4,domain='ram')]),rows)


@pytest.mark.parametrize('field,value',(('raw_r4',-1),('raw_r5',1<<32),('variant',True),('initial_sr',2)))
def test_input_domains_refuse_narrowed_boolean_or_changed_SR_operands(field,value):
    case=dict(matrix.DEFAULTS,index=0,kind='controlled',entry=0x265C4);case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_refuses_owning_identity_units_scale_geometry_caller_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_published_original_instruction_and_joint_counts_bind_the_executed_sources():
    declared=withdrawal.descriptor(repo.ROOT);rows=[row for row in declared['reference'] if row['component']=='register_overflow_paths']
    text=(repo.ROOT/'defs/JK08A.register-overflow-paths.md').read_text();words=' '.join(text.split())
    assert len(rows)==1 and len(declared['reference'])==124 and len(declared['function'])==66
    assert len({row['owner'] for row in declared['reference']})==95
    assert [line for line in text.splitlines() if line.startswith('| `7mfk:')]==[
        '| `7mfk:'+f'{row["address"]:08x}'+'` | `7mfk:'+f'{row["function"]:08x}'+
        '` | `'+row['original_claim_sha256']+'` |' for row in rows]
    for phrase,actual,wanted in (('17 stock instructions',sum((b-a)//2 for a,b in contract.SPANS),17),
        ('34 code bytes',sum(b-a for a,b in contract.SPANS),34),('2 constant pools',len(contract.UNIT['pools']),2),
        ('0 pointer aliases',len(contract.UNIT['aliases']),0),('3 two-sided conditional sites',len(proof.REQUIRED_BRANCHES),3)):
        assert phrase in words and actual==wanted
    image=repo.images()['JK08A'].path.read_bytes()
    assert '4 natural RTS sites' in words
    assert sum(image[at:at+2]==b'\x00\x0b' for first,last in contract.SPANS for at in range(first,last,2))==4
    assert 'opcode masks300F/300B underF00F' in words
    assert {int.from_bytes(image[at:at+2],'big')&0xF00F for at in (0x265CA,0x265D2)}=={0x300B,0x300F}
    owners={row['owner']:row for row in declared['reference']}
    removed=sum(sum(len(marker.get('dependency',())) for marker in (json.loads(row['original_ledger_json']) or ()))
        -sum(len(marker.get('dependency',())) for marker in (json.loads(row['proposed_ledger_json']) or ())) for row in owners.values())
    removed+=sum(sum(len(marker.get('dependency',())) for marker in json.loads(row['original_ledger_json']))-
        sum(len(marker.get('dependency',())) for marker in json.loads(row['proposed_ledger_json']))
        for row in declared['function'] if 'proposed_ledger_json' in row)
    assert removed==116 and '116 matching ledger selectors' in words
    assert 'thirteen families and forty-seven capture bindings' in words
    assert len(registry.FAMILIES)==13 and len(registry.captures())==47
    assert 'preceding nine adapters' in words and proof_adapter.DESCRIPTORS.index(contract.DESCRIPTOR)==9
