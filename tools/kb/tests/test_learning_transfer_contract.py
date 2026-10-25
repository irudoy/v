"""Reused natural learned-grid units preserve bytes, inputs and native owners."""

from copy import deepcopy
import json

import pytest

from kb import learning_transfer_contract as contract,learning_transfer_matrix as matrix
from kb import learning_transfer_capture_evidence as proof,learning_transfer_semantics as numeric
from kb import learning_access_contract as owning,repo
from kb.test_stock_capture import tool


def test_reused_units_preserve_all_stock_code_and_change_only_declared_aliases():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    assert len(declared['unit'])==3
    assert declared['natural_entries']==[0x5796C,0x57D1E,0x580E8,0x57B26]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    assert (0x58092,0x580C2) in contract.SPANS and (0x580E8,0x58168) in contract.SPANS


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_raw_input_matrix_ignores_every_legacy_expected_output(monkeypatch):
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    before=matrix.cases(declared,image)
    original=matrix.source_array
    def changed(root,path,name):
        rows=deepcopy(original(root,path,name))
        if name=='samples':
            start=11 if path==matrix.INPUT_SOURCES[0] else 12
            for row in rows:
                for index in range(start,len(row)):row[index]=None
        return rows
    monkeypatch.setattr(matrix,'source_array',changed)
    assert matrix.cases(declared,image)==before


def test_private_header_reconstruction_matches_all_natural_input_roles():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    all_cases=matrix.cases(declared,image)
    cases=[next(row for row in all_cases if row['kind']==kind) for kind in matrix.KINDS]
    packet=dict(source=declared,cases=cases)
    producer=tool(repo.ROOT,'learning_transfer_capture.py','_kb_learning_transfer_test_producer')
    assert producer.header(packet,image)==proof.header(packet,image)


@pytest.mark.parametrize('field',('word','stft','previous','aux_lower','aux_upper','decay'))
def test_learning_reader_alternatives_hold_complete_context_and_other_bytes_fixed(field):
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    cases=[row for row in matrix.cases(declared,image) if row['kind']=='learning' and row['argument']==1]
    first=next(row for row in cases if row['word']==25600 and row['stft']==25600 and row['cell_index']==0
               and row['counter']==1 and row['permit_a']==row['permit_b']==255
               and row['decay']==0 and row['aux_lower']==90 and row['aux_upper']==110)
    second=deepcopy(first);second[field]+=1
    assert matrix.context(declared,first)==matrix.context(declared,second)
    a,b=bytearray(matrix.memory(first)),bytearray(matrix.memory(second))
    ca={at:bytearray(data) for at,data in matrix.calibrations(declared,image,first).items()}
    cb={at:bytearray(data) for at,data in matrix.calibrations(declared,image,second).items()}
    if field in ('word','stft','previous'):
        at={'word':0x1350,'stft':0x22DE,'previous':0x2308}[field]
        assert a[at:at+2]!=b[at:at+2];a[at:at+2]=b[at:at+2]
    else:
        at={'aux_lower':0x839D,'aux_upper':0x839C,'decay':0x88F5}[field]
        start=next(start for start,data in ca.items() if start<=at<start+len(data))
        assert ca[start][at-start]!=cb[start][at-start];ca[start][at-start]=cb[start][at-start]
    assert a==b and ca==cb


def test_joint_batch_preserves_all_complete_documents_types_and_TEST_positions():
    rows=owning.descriptor(repo.ROOT)['reference']
    assert len(rows)==21 and len({row['owner'] for row in rows})==13
    assert {row['owner'].rsplit('/',1)[1] for row in rows}=={'ram','tbl'}
    for owner in {row['owner'] for row in rows}:
        selected=[row for row in rows if row['owner']==owner]
        assert len({row['original_native_json'] for row in selected})==1
        assert len({row['proposed_native_json'] for row in selected})==1
        before=json.loads(selected[0]['original_native_json']);after=json.loads(selected[0]['proposed_native_json'])
        assert {key:value for key,value in before.items() if key!='link'}=={
            key:value for key,value in after.items() if key!='link'}
    for owner in ('stft_b2/ram','inquisitive-dormouse/ram','ltft_b2/ram','benevolent-anteater/ram'):
        assert all((row['declared_width'],row['declared_signed'])==(16,'unset') for row in rows if row['owner']==owner)
    text=(repo.ROOT/'defs/JK08A.learning-transfers.md').read_text()
    assert f'{len(rows)} exact original relations' in text


def memory(word=25600,stft=25600,previous=25600,counter=1):
    result=bytearray([0xA5])*65536
    for at,value in ((0x134E,word),(0x22DC,stft),(0x2306,previous)):
        result[at:at+2]=value.to_bytes(2,'big')
    result[0x130A]=0;result[0x49F0]=counter;result[0x1458]=result[0x1457]=255
    return bytes(result)


@pytest.mark.parametrize('word,stft,output',((25599,1,25599),(25600,1,25601),(25601,65535,25601),
    (25600,25600,25600)))
def test_learning_literal_minimum_step_keeps_independent_STFT_gate_and_word_direction(word,stft,output):
    result=numeric.learning(memory(word=word,stft=stft),0,[2,8,16],[26,26,16,8],26,0,90,110,90,110)
    assert result['output']==output


@pytest.mark.parametrize('counter,decay,word,output',((255,0,25600,0),(254,1,25600,254),
    (127,255,25600,0),(1,0,23039,0),(1,0,23040,2),(1,0,28160,0)))
def test_auxiliary_literal_modulo_decay_and_half_open_retention(counter,decay,word,output):
    result=numeric.auxiliary(memory(word=word,counter=counter),0,0,decay,90,110)
    assert result['output']==output
