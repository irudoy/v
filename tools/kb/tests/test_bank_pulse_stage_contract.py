"""Bounded additional stages preserve exact stock, input and native domains."""

from copy import deepcopy
import json

import pytest

from kb import bank_pulse_stage_contract as contract,bank_pulse_stage_matrix as matrix
from kb import bank_pulse_stage_semantics as numeric,bank_pulse_stage_capture_evidence as proof,repo
from kb import bank_pulse_access_contract as owning
from kb.test_stock_capture import tool


def test_two_existing_units_and_real_helpers_change_only_declared_pointer_literals():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image);restored=bytearray(fixture)
    assert len(source['unit'])==2 and contract.ENTRIES==(0x4E974,0x4EBA2) and contract.RETURNS==()
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]
    assert set(contract.FUNCTIONS)=={0x4E974,0x4EBA2,0x21CE0,0x2657C,0x224F8,0x5B7EC}
    wide=next(row for row in contract.POOLS if row['address']==0x4ED70)
    assert wide['size']==20
    assert fixture[0x4ED70:0x4ED74]==bytes.fromhex('0100128c')
    assert fixture[0x4ED74:0x4ED84]==image[0x4ED74:0x4ED84]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_stage_descriptor_rejects_implicit_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT/contract.DESCRIPTOR).read_text().replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def header(array,rows):
    def c(value):return '{'+','.join(c(item) for item in value)+'}' if type(value) is list else hex(value)+'U'
    return 'static const struct input '+array+'[]={\n'+''.join(c(row)+',\n' for row in rows)+'};\n'


def prefix_files(root,precursor,channel):
    for path,array,row in zip(matrix.INPUT_SOURCES,('pulse_precursor_cases','channel_pulse_cases'),(precursor,channel)):
        target=root/path;target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(header(array,[deepcopy(row) for _ in range(matrix.PREFIX_INPUTS)]))


def test_all_legacy_expected_results_registers_and_local_columns_are_ignored(tmp_path):
    precursor=[0,0,0,32768,65535,1000,1024,16384,0,16384,25600,25600,0x12C000,170,0,0,
               1,4096,4096,4096,32768,0,7,[1,2,3],list(range(8))]
    channel=[1,0xFFFFFF01,0,32768,65535,0,0,8,128,170,13528,16384,4250,0,1,0,
             0,100,200,0,300,400,500,600,list(range(15)),list(range(15))]
    prefix_files(tmp_path,precursor,channel);before=matrix.inputs(tmp_path)
    for index in range(16,23):precursor[index]^=0xA5A5
    precursor[23]=[0,0,0];precursor[24]=[0xFFFFFFFF]*8
    for index in range(16,24):channel[index]^=0x5A5A
    channel[24]=[0xFFFFFFFF]*15;channel[25]=[0]*15
    prefix_files(tmp_path,precursor,channel)
    assert before==matrix.inputs(tmp_path)
    assert all(not {'expected','expected_sr','common_output','transformed'}&row.keys() for row in before)


def test_additional_inputs_preserve_the_full_existing_GNU_matrix_sources_and_header_encoding():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    declared=dict(source=source,cases=list(matrix.cases(source,image)))
    producer=tool(repo.ROOT,'bank_pulse_stage_capture.py','_kb_bank_pulse_stage_test_producer')
    assert producer.header(declared,image)==proof.header(declared,image)
    assert {row['kind'] for row in declared['cases']}==set(matrix.KINDS)
    assert {row['channel'] for row in declared['cases'] if row['kind']=='channel'}==set(range(6))
    text=(repo.ROOT/'defs/JK08A.bank-pulse-transfers.md').read_text()
    assert f'{matrix.PREFIX_INPUTS} input-only prefix rows' in text


def test_bank1_positive_alternatives_fix_every_other_RAM_context_and_calibration_byte():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    seed=next(row for row in matrix.cases(source,image) if row['kind']=='precursor')
    first,second=deepcopy(seed),deepcopy(seed);first['bank1']=0;second['bank1']=65535
    assert matrix.context(source,first)==matrix.context(source,second)
    assert matrix.calibrations(source,image,first)==matrix.calibrations(source,image,second)
    left,right=bytearray(matrix.memory(first)),bytearray(matrix.memory(second))
    model=tool(repo.ROOT,'stock_precursor_model.py','_kb_bank_pulse_stage_test_numeric')
    a=numeric.precursor(bytes(left),matrix.calibrations(source,image,first),model)
    b=numeric.precursor(bytes(right),matrix.calibrations(source,image,second),model)
    assert a['output']!=b['output'] and left[0x40B8:0x40BA]!=right[0x40B8:0x40BA]
    left[0x40B8:0x40BA]=right[0x40B8:0x40BA]
    assert left==right


def test_joint_native_family_preserves_untyped_channel_and_grouped_precursor_owner():
    rows=owning.descriptor(repo.ROOT)['reference'];added=[row for row in rows if row['component']=='bank_pulse_stages']
    assert len(added)==3
    channel=next(row for row in added if row['owner']=='injection_1/ram')
    assert channel['declared_width']==channel['declared_signed']=='unset'
    for owner in ('famous-grouse/ram','giga-eel/ram'):
        assert all((row['declared_width'],row['declared_signed'])==(16,'unset') for row in added if row['owner']==owner)
    grouped=[row for row in rows if row['owner']=='famous-grouse/ram']
    assert len({row['original_native_json'] for row in grouped})==len({row['proposed_native_json'] for row in grouped})==1
    before=json.loads(grouped[0]['original_native_json']);after=json.loads(grouped[0]['proposed_native_json'])
    assert {key:value for key,value in before.items() if key!='link'}=={
        key:value for key,value in after.items() if key!='link'}


@pytest.mark.parametrize('mask,base,additive,multiplier,opening,compensated,transformed,lower',(
    (0,0,0,128,170,0,399,399),
    (2,65535,32767,255,123,123,123,891),
    (0,65535,32767,255,170,65535,65535,391),
    (0,0,32768,255,170,0,399,399),
))
def test_channel_equations_preserve_inhibit_signed_words_affine_wrap_and_cap(mask,base,additive,multiplier,opening,compensated,transformed,lower):
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    seed=next(row for row in matrix.cases(source,image) if row['kind']=='channel' and row['channel']==1)
    case=dict(seed,mask=mask,odd_base=base,additive=additive,subtractive=0,flag=0,multiplier=multiplier,
              opening=opening,a=65535,c=65535,b=65535,d=65535)
    result=numeric.channel(matrix.memory(case),matrix.calibrations(source,image,case),1)
    assert (result['compensated'],result['transformed'],result['lower'])==(compensated,transformed,lower)
