"""Exact bank-mask inputs preserve original unsigned-byte owner boundaries."""

from copy import deepcopy
import json

import pytest

from kb import closed_loop_admission_contract as contract,closed_loop_admission_matrix as matrix
from kb import closed_loop_admission_semantics as scalar,closed_loop_admission_capture_evidence as proof
from kb import closed_loop_admission_access_contract as owning,repo
from kb.test_stock_capture import tool


def test_four_original_writers_keep_every_other_native_field_reader_and_TEST_position():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==4 and len({row['owner'] for row in rows})==4
    assert {row['address'] for row in rows}=={0xFFFF97A9,0xFFFF97AB,0xFFFF97AD,0xFFFF97B6}
    assert {row['function'] for row in rows}=={0xA0EE8}
    for row in rows:
        assert (row['declared_width'],row['declared_signed'],row['width_bytes'])==(8,False,1)
        before=json.loads(row['original_native_json']);after=json.loads(row['proposed_native_json'])
        expected=deepcopy(before)
        links=[link for link in expected['link'] if link['type']=='writer']
        assert len(links)==1 and len(before['link'])==len(after['link'])==2
        links[0].setdefault('evidence',[]).append(owning.item(row));assert expected==after
        assert before['symbol']==after['symbol']
        assert row['original_ledger_json']==row['proposed_ledger_json']=='null'


def test_existing_assembly_retains_all_tested_bytes_and_only_one_base_alias_and_two_outside_returns():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert aliases==[dict(address=0xA114C,original=0xFFFF4558,alias=0x01004558)]
    restored=bytearray(fixture);restored[0xA114C:0xA1150]=bytes.fromhex('ffff4558')
    for row in contract.BOUNDARIES:
        at=row['address'];assert fixture[at:at+8]==bytes.fromhex('57f6472a000b0009')
        restored[at:at+8]=image[at:at+8]
    assert bytes(restored)==image
    assert sum(row['size'] for row in contract.POOLS)==13
    for row in contract.WINDOWS:assert fixture[row['start']:row['end']]==image[row['start']:row['end']]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_full_coordinator_integrator_permission_geometry_or_hardware(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('old,new',(('gbr = 16815996','gbr = 16815997'),('r8 = 1','r8 = 0'),
    ('r9 = 0','r9 = 1'),('r10 = 2','r10 = 1'),('value = 872','value = 873')))
def test_descriptor_refuses_GBR_mask_or_bank_premise_changes(tmp_path,old,new):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();assert old in text
    path.write_text(text.replace(old,new,1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


@pytest.mark.parametrize('mask,bank,output',((0,0,0),(0,1,0),(1,0,1),(1,1,0),(2,0,0),(2,1,1),
    (3,0,1),(3,1,1),(0x80,0,0),(0x80,1,0),(0xFE,0,0),(0xFE,1,1),(0xFF,0,1),(0xFF,1,1)))
def test_mask_bits_have_literal_unsigned_byte_boundaries(mask,bank,output):
    assert scalar.scalar(mask,bank)==output


@pytest.mark.parametrize('mask,bank',((-1,0),(256,0),(True,0),(0,True),(0,2)))
def test_scalar_refuses_a_different_mask_width_or_bank(mask,bank):
    with pytest.raises(ValueError):scalar.scalar(mask,bank)


@pytest.mark.parametrize('index',range(4))
def test_bank2_positive_alternatives_hold_bank1_and_every_other_input_fixed(index):
    declared=contract.descriptor(repo.ROOT);row=contract.DECODERS[index]
    first=dict(index=0,entry=contract.ENTRIES[int(index==3)],**dict.fromkeys(matrix.FIELDS,0),variant=0,sr=0)
    second=dict(first);second[matrix.FIELDS[index]]=2
    assert matrix.context(declared,first)==matrix.context(declared,second)
    a,b=bytearray(matrix.memory(first)),bytearray(matrix.memory(second));at=row['input']&65535
    assert a[at]==0 and b[at]==2;a[at]=b[at];assert a==b
    assert scalar.scalar(0,0)==scalar.scalar(2,0)==0
    assert scalar.scalar(0,1)!=scalar.scalar(2,1)


def test_private_input_header_matches_shared_complete_observer_without_expected_outputs():
    image=repo.images()['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    declared=dict(source=source,cases=list(matrix.cases(source,image)))
    producer=tool(repo.ROOT,'closed_loop_admission_capture.py','_kb_closed_loop_admission_test_producer')
    assert producer.header(declared,image)==proof.header(declared,image)


def test_current_narrow_document_binds_executed_contract_counts_and_exact_limits():
    text=(repo.ROOT/'defs/JK08A.closed-loop-admission-accesses.md').read_text()
    for row in contract.WINDOWS:assert f"`{row['start']:08X}`" in text and f"`{row['end']:08X}`" in text
    assert 'two bounded input-decoding windows' in text and len(contract.ENTRIES)==2
    assert 'contain13 bytes' in text and sum(row['size'] for row in contract.POOLS)==13
    assert 'four exact\noriginal writer relations in four complete owner documents' in text
    rows=owning.descriptor(repo.ROOT)['reference'];assert len(rows)==len({row['owner'] for row in rows})==4
    assert 'R8=1, R9=0 and R10=2' in text and 'GBR=0100977C' in text
    assert 'Source preparation does not qualify' in text
