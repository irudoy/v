"""Complete natural base-pulse inputs preserve exact native and machine domains."""

from copy import deepcopy
import json

import pytest

from kb import bank_pulse_contract as contract,bank_pulse_matrix as matrix,bank_pulse_semantics as numeric
from kb import bank_pulse_capture_evidence as proof,bank_pulse_access_contract as owning,repo
from kb.test_stock_capture import tool


def test_complete_primary_binds_every_explicit_raw_and_owning_descriptor_input():
    import hashlib
    from kb import copy_witness
    inputs=copy_witness.provenance(repo.ROOT)
    for path in (contract.DESCRIPTOR,owning.DESCRIPTOR,contract.ARITHMETIC_SOURCE,
        'defs/JK08A.phase-normalization.toml','defs/JK08A.phase-access-claims.toml',
        'defs/JK08A.learning-transfers.toml','defs/JK08A.learning-access-claims.toml',
        'defs/JK08A.bank-pulse-stages.toml','tools/kb/tests/test_channel_pulse_chain.py'):
        assert inputs[path]==hashlib.sha256((repo.ROOT/path).read_bytes()).hexdigest()


def test_existing_complete_natural_unit_changes_only_three_declared_pointer_literals():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    assert aliases==[dict(address=at,original=original,alias=matrix.RAM_BASE+(original&65535))
                     for at,original in contract.ALIASES.items()]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and fixture[0x4EAD4:0x4EBA2]==image[0x4EAD4:0x4EBA2]
    assert contract.RETURNS==() and declared['assembly']=='tools/sh-elf-run/stock_jk08a_bank_base_pulse.s'
    assert int.from_bytes(image[0x4EB9E:0x4EBA2],'big')==0x000B4F16


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('old,new',(('end = 322466','end = 322464'),
    ('value = 1680','value = 1682'),('value = 4294916096','value = 4294916098')))
def test_descriptor_refuses_different_code_offsets_or_arithmetic_literal(tmp_path,old,new):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(old,new,1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def input_header(expected,values):
    return ('static const struct bank_base_case bank_base_cases[] = {\n'
        '    {0xf00dca01U,{'+','.join(str(value)+'U' for value in expected)+'},'+
        ','.join(str(value)+'U' for value in values)+'},\n};\n')


def test_legacy_expected_register_output_final_T_and_group_columns_are_not_inputs():
    expected=list(range(15))
    values=[30000,30000,30000,32768,100,32768,16384,16385,12345,2,0,1,7,1,9]
    first=matrix.source_inputs(input_header(expected,values))
    expected=[value^0xFFFFFFFF for value in expected]
    values[8],values[13],values[14]=54321,0,10
    assert first==matrix.source_inputs(input_header(expected,values))
    assert 'output' not in first[0] and 'expected' not in first[0] and 'expected_t' not in first[0]


@pytest.mark.parametrize('bank',(0,1))
@pytest.mark.parametrize('role',matrix.READER_FIELDS)
def test_positive_reader_alternatives_hold_every_other_input_and_complete_context_fixed(bank,role):
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    seed=next(row for row in matrix.cases(declared,image) if row['raw_r4']&255==bank and row['variant']==7)
    first,second=deepcopy(seed),deepcopy(seed)
    first[role],second[role]=(0,65535) if role in ('precursor','offset') else (26000,40000)
    assert matrix.context(declared,first)==matrix.context(declared,second)
    assert matrix.calibrations(declared,image,first)==matrix.calibrations(declared,image,second)
    left,right=bytearray(matrix.memory(first)),bytearray(matrix.memory(second))
    at=dict(matrix.WORDS)[role]+bank*2
    assert left[at:at+2]!=right[at:at+2]
    outputs=[numeric.evaluate(bytes(memory),bank,seed['f1'],seed['f2'])['output'] for memory in (left,right)]
    left[at:at+2]=right[at:at+2]
    assert left==right and outputs[0]!=outputs[1]


def test_private_header_matches_existing_observer_inputs_without_expected_outputs():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    cases=matrix.cases(declared,image);packet=dict(source=declared,cases=list(cases))
    producer=tool(repo.ROOT,'bank_pulse_capture.py','_kb_bank_pulse_test_producer')
    assert producer.header(packet,image)==proof.header(packet,image)
    assert len(matrix.source_inputs((repo.ROOT/matrix.INPUT_SOURCE).read_text()))==6184
    assert {row['raw_r4']&255 for row in cases}=={0,1}


def test_joint_nine_relations_preserve_eight_complete_owner_documents_and_exact_semantic_types():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==9 and len({row['owner'] for row in rows})==8
    assert [row['direction'] for row in rows].count('reader')==6
    for row in rows:
        assert (row['declared_width'],row['declared_signed'])==(
            'unset' if row['owner']=='injection_1/ram' else 16,'unset')
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json'])
        assert {key:value for key,value in before.items() if key!='link'}=={
            key:value for key,value in after.items() if key!='link'}
    ltft=next(row for row in rows if row['owner']=='ltft_b2/ram')
    assert ltft['sites']==[0x4EB04,0x4EB42]
    grouped=[row for row in rows if row['owner']=='famous-grouse/ram']
    assert {row['direction'] for row in grouped}=={'reader','writer'}
    assert len({row['proposed_native_json'] for row in grouped})==1
    text=(repo.ROOT/'defs/JK08A.bank-pulse-transfers.md').read_text()
    assert f'{len(rows)} exact original relations' in text


def memory(s=30000,l=30000,e=30000,precursor=32768,additive=100,offset=32768,c0=16384):
    case=dict(raw_r4=0,s=s,l=l,e=e,precursor=precursor,additive=additive,offset=offset,c0=c0,c1=65535)
    return matrix.memory(case)


@pytest.mark.parametrize('kwargs,flag,output,exit_t',(
    ({},2,19500,0),({'precursor':0,'offset':0},2,100,0),
    ({'s':65535,'e':25602,'precursor':65535,'additive':0,'c0':65535},0,65535,0),
    ({'s':65535,'e':25603,'precursor':65535,'additive':0,'c0':65535},0,0,0),
    ({'s':0,'l':0,'e':0,'precursor':1,'additive':0,'offset':0},2,65535,1),
    ({'s':0,'l':0,'e':0,'precursor':1,'additive':65535,'offset':32768},2,65535,0),
    ({'s':0,'l':0,'e':0,'precursor':1,'additive':65535,'offset':33024},2,65535,1),
))
def test_existing_scalar_equations_retain_low32_product_offset_wrap_and_cap(kwargs,flag,output,exit_t):
    result=numeric.evaluate(memory(**kwargs),0,flag,0)
    assert (result['output'],result['exit_t'])==(output,exit_t)


@pytest.mark.parametrize('flag1,flag2,c0,c1,include',((0,0,16384,65535,True),
    (0,0,16385,0,False),(0,16,65535,16384,True),(0,16,0,16385,False),(2,16,65535,65535,True)))
def test_LTFT_gate_preserves_flag_override_and_control_threshold(flag1,flag2,c0,c1,include):
    before=bytearray(memory(c0=c0));before[0x22E8:0x22EA]=c1.to_bytes(2,'big')
    assert numeric.evaluate(bytes(before),0,flag1,flag2)['include_l'] is include
