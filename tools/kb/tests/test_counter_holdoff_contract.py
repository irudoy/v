"""Exact bounded holdoff byte retains the previous counter claims and TEST origin."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import repo,test_contract
from kb import counter_array_contract as contract,counter_array_matrix as matrix
from kb import counter_array_capture_evidence as proof,counter_access_contract as owning

RETAINED_EIGHT={'ffff2571-writer': '8ebc8a58e51130bf7ffa23f2a5c93fdfcbd91badaec8fbaf9eae2632715e650c', 'ffff2572-writer': '5e62b29b09b263921f7593ed3b31d533be89bff0930e585549f78d87667d862f', 'ffff2573-writer': '0781eb45c89cb35b9d9dd29d623449ce3db6431911cec3317e30686ee60795f2', 'ffff258a-writer': '4d72bbfe25c23c1a13e9aa473afa2eea6f6ec0b219b3e99e7ef5d7d496f5d094', 'ffff2590-writer': 'd428272e1955916dfe0b4cc8de8786a3f4683652c37c69a99ca114991197939d', 'ffff25e7-writer': 'd5443968d261fa106d6ef69a0f616bb29772ccad8718cd8203c22951cb6038ee', 'ffff43be-writer': '75386e8df25432cb0ca1c4cd2a680d5de1d99023ef1dd2bb3a57a9a189d0aaae', 'ffff4413-writer': '4831562b657ee6530947f02e946ccacc09ac605f8c555ffbb64d428d2c595eb6'}
ORIGINAL='6cd674ec09b33c88479f35bb09d7dc472ff4a655f4d7ee8849b3cf75d3c11c57'


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()).hexdigest()


def test_joint9_retains_all_old8_complete_records_and_holdoff_L0_TEST_via_note_and_native_facts():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==9 and {row['id']:digest(row) for row in rows[:8]}==RETAINED_EIGHT
    row=rows[-1];old=json.loads(row['original_claim_json']);new=json.loads(row['proposed_claim_json'])
    assert row['original_claim_sha256']==ORIGINAL
    assert old['evidence']==[dict(at='7mfk:00020956',kind='l0'),dict(kind='test',
        path='tools/kb/tests/test_engine_speed_event_interval.py',key='test_event_interval_modes_wrap_holdoff_and_calls_match_stock')]
    assert new==dict(old,evidence=[*old['evidence'],owning.item(row)])
    assert new['props']==old['props'] and 'via' in old['props'] and 'note' in old['props']
    before,after=(json.loads(row[key]) for key in ('original_native_json','proposed_native_json'))
    expected=deepcopy(before)
    link=next(link for link in expected['link'] if link['type']=='writer' and link['to']=='gentle-bat/fn')
    link.setdefault('evidence',[]).append(owning.item(row))
    assert test_contract.exact(expected,after)
    assert before['symbol']==after['symbol'] and before.get('ledger')==after.get('ledger')
    assert row['declared_width']==row['declared_signed']=='unset' and row['width_bytes']==1


def test_old_two_windows_eighteen_inputs_and_word_patterns_remain_exact():
    source=contract.descriptor(repo.ROOT);old=dict(source,window=source['window'][:2])
    assert matrix.cases(source,b'')[:18]==matrix.cases(old,b'')
    for case in matrix.cases(old,b''):
        assert matrix.context(source,case)==matrix.context(old,case)
        expected=bytearray([case['seed']&255])*65536
        expected[0x2604:0x2618]=case['seed'].to_bytes(2,'big')*10
        assert matrix.memory(case)==bytes(expected)
    assert [(row['count'],row['width_bytes']) for row in contract.ARRAYS[:4]]==[(138,1),(10,2),(195,1),(244,1)]


def test_holdoff_window_binds_the_exact_fourth_byte_offset_and_separate_outside_return():
    source=contract.descriptor(repo.ROOT);window=source['window'][-1];array=source['array'][-1]
    assert window==dict(parent=0x208F8,start=0x2093E,end=0x20962,gbr=0x12344321,prefix_steps=6)
    assert array['first']==0xFFFF25FB and array['count']==7 and array['width_bytes']==1
    assert array['first']+4==0xFFFF25FF and array['store']==0x20956
    image=repo.images()['JK08A'].path.read_bytes();fixture,_=contract.independent_fixture(source,image)
    assert fixture[0x2093E:0x20962]==image[0x2093E:0x20962]
    assert fixture[0x20962:0x20966]==bytes.fromhex('000b0009')
    assert fixture[0x20B44:0x20B48]==bytes.fromhex('010025fb')


@pytest.mark.parametrize('value',(0,1,2,127,128,254,255))
def test_explicit_holdoff_operand_changes_only_one_incoming_byte_with_other_contexts_fixed(value):
    source=contract.descriptor(repo.ROOT)
    case=next(row for row in matrix.cases(source,b'') if row.get('holdoff')==value)
    other=dict(case,holdoff=2 if value!=2 else 1)
    left,right=bytearray(matrix.memory(case)),bytearray(matrix.memory(other))
    assert left[0x25FF]!=right[0x25FF];left[0x25FF]=right[0x25FF]
    assert left==right and matrix.context(source,case)==matrix.context(source,other)
    result,accesses,branches,_,_=proof.array_equation(contract.WINDOWS[-1],matrix.memory(case))
    assert result[0x25FF]==max(0,value-1)
    target=[row for row in accesses if row[2]==0x010025FF]
    assert [row[1] for row in target]==(['read'] if value==0 else ['read','read','write'])
    assert (0x2094E,'taken' if value==0 else 'fallthrough') in branches


@pytest.mark.parametrize('value',(-1,256,True))
def test_typed_holdoff_input_refuses_an_incorrect_byte(value):
    with pytest.raises(ValueError):matrix.memory(dict(index=0,entry=0x2093E,seed=0xA5,holdoff=value))


def test_input_header_keeps_the_existing_observer_and_never_copies_expected_outputs():
    source=contract.descriptor(repo.ROOT);declared=dict(source=source,cases=list(matrix.cases(source,b'')))
    header=proof.header(declared,b'')
    assert b'#define RAM_INITIALIZATION_BYTE_INPUTS 1' in header
    assert b'0x25ffU' in header and b'expected' not in header.split(b'\n',1)[1].lower()
    from kb.test_stock_capture import tool
    producer=tool(repo.ROOT,'counter_array_capture.py','_kb_holdoff_raw_inputs')
    assert producer.header(declared,b'')==header
    from kb import ram_initialization_contract as init,ram_initialization_matrix as init_matrix
    from kb import ram_initialization_capture_evidence as init_proof
    init_source=init.descriptor(repo.ROOT);init_declared=dict(source=init_source,cases=list(init_matrix.cases(init_source,b'')))
    assert b'RAM_INITIALIZATION_BYTE_INPUTS' not in init_proof.header(init_declared,b'')


def test_document_counts_and_exact_TEST_scope_follow_the_executed_sources():
    text=(repo.ROOT/'defs/JK08A.counter-arrays.md').read_text()
    assert 'nine original writer' in text and len(owning.descriptor(repo.ROOT)['reference'])==9
    assert 'five exact ROM pointers' in text and len(contract.POOLS)==5
    assert '34 explicit inputs' in text and len(matrix.cases(contract.descriptor(repo.ROOT),b''))==34
    assert '7 bytes' in text and contract.ARRAYS[-1]['count']==7
    for literal in ('000208F8','0002093E','00020956','FFFF25FB','FFFF25FF','FFFF2602','TEST'):
        assert literal in text
