"""Natural normalizer premises bind both pointer pairs and preserve semantic types."""

from copy import deepcopy
import json

import pytest

from kb import phase_normalization_contract as contract,phase_normalization_matrix as matrix
from kb import phase_normalization_capture_evidence as proof,phase_access_contract as owning,repo
from kb.test_stock_capture import tool


def test_existing_natural_unit_changes_only_its_one_declared_pointer_literal():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    assert aliases==[dict(address=0x29020,original=0xFFFF128C,alias=0x0100128C)]
    restored=bytearray(fixture);restored[0x29020:0x29024]=bytes.fromhex('ffff128c')
    assert bytes(restored)==image and fixture[0x28DC8:0x28E7C]==image[0x28DC8:0x28E7C]
    assert fixture[0x28E7C:0x28E9E]==image[0x28E7C:0x28E9E]
    assert (contract.POOLS[-1]['address'],contract.POOLS[-1]['size'],contract.POOLS[-1]['value'])==(0x28EA0,2,6554)
    assert sum(row['size'] for row in contract.POOLS)==8
    assert (declared['window'][1]['end']-declared['window'][1]['start'])//2==17
    assert contract.RETURNS==()
    assert declared['assembly']=='tools/sh-elf-run/stock_jk08a_injection_tooth.s'


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('field,old,new',(('word',4294906808,4294906810),('byte',4294907226,4294907227)))
def test_descriptor_refuses_a_different_pointer_pair(tmp_path,field,old,new):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text()
    path.write_text(text.replace(f'{field} = {old}',f'{field} = {new}',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('pair',range(2))
@pytest.mark.parametrize('role,field,width',(('word','count',2),('byte','remainder',1)))
def test_reader_alternatives_hold_every_other_input_and_complete_context_fixed(pair,role,field,width):
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    case=next(row for row in matrix.cases(declared,image) if row['pair']==pair and row['phase']==4 and row['count']==4)
    other=deepcopy(case);other[field]^=1
    assert matrix.context(declared,case)==matrix.context(declared,other)
    first,second=bytearray(matrix.memory(case)),bytearray(matrix.memory(other));at=case[role]&65535
    assert first[at:at+width]!=second[at:at+width]
    first[at:at+width]=second[at:at+width]
    assert first==second


def test_private_header_matches_existing_observer_inputs_without_expected_outputs():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    packet=dict(source=declared,cases=list(matrix.cases(declared,image)))
    producer=tool(repo.ROOT,'phase_normalization_capture.py','_kb_phase_normalization_test_producer')
    assert producer.header(packet,image)==proof.header(packet,image)


def test_joint_relations_share_six_complete_owner_documents_and_preserve_unset_types():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==12 and len({row['owner'] for row in rows})==6
    for owner in ('huge-lori/ram','economic-collie/ram','vivacious-petrel/ram','peridot-pony/ram'):
        selected=[row for row in rows if row['owner']==owner]
        assert {row['direction'] for row in selected}=={'reader','writer'}
        assert len({row['original_native_json'] for row in selected})==1
        assert len({row['proposed_native_json'] for row in selected})==1
        before=json.loads(selected[0]['original_native_json']);after=json.loads(selected[0]['proposed_native_json'])
        assert {key:value for key,value in before.items() if key!='link'}=={
            key:value for key,value in after.items() if key!='link'}
        if owner in ('vivacious-petrel/ram','peridot-pony/ram'):
            assert all(row['declared_width']==row['declared_signed']=='unset' for row in selected)
    text=(repo.ROOT/'defs/JK08A.phase-normalization.md').read_text()
    assert f'{len(rows)} exact original relations' in text


@pytest.mark.parametrize('phase,count,remainder,output',((4,5,250,(3,14)),(4,4,250,(3,4)),
    (9,9,250,(8,4)),(0,14,250,(10,14)),(0,13,250,(10,4)),
    (0,25,128,(25,128)),(4,65535,128,(65535,128)),(9,65535,255,(65533,19))))
def test_existing_integer_equation_retains_phase_edges_unsigned_words_and_byte_wrap(phase,count,remainder,output):
    numeric=tool(repo.ROOT,'stock_injection_programmer_model.py','_kb_phase_normalization_test_numeric')
    assert numeric.normalized(count,remainder,phase)[:2]==output
