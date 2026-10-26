"""Raw32 signed boundaries, exact stock words and unchanged native meaning."""

import pytest
from kb import repo
from kb import signed_abs_register_helper_withdrawal_contract as contract
from kb import signed_abs_register_helper_withdrawal_matrix as matrix
from kb import signed_abs_register_helper_withdrawal_semantics as scalar
from kb import signed_abs_register_helper_withdrawal_transfers as transfers


def evaluated(raw,sr=0):
    case=dict(matrix.DEFAULTS,entry=0x22590,index=0,kind='controlled',raw_r4=raw,initial_sr=sr)
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    context=matrix.context(source,case);memory=matrix.memory(case);frame=bytes([0xA5])*192
    value=scalar.evaluate(case['entry'],memory,matrix.calibrations(source,image,case),context,sr,frame,0x02001000,0x02100000)
    return case,context,memory,frame,value


@pytest.mark.parametrize('raw,expected,t',(
    (0,0,0),(1,1,1),(0x7FFFFFFF,0x7FFFFFFF,1),
    (0x80000000,0x80000000,0),(0x80000001,0x7FFFFFFF,0),
    (0xFFFFFFFF,1,0),(0xFFFF0000,0x10000,0),
    (0x10000,0x10000,1),(0xFFFF8000,0x8000,0),(0x8000,0x8000,1)))
@pytest.mark.parametrize('sr',(0,1,0x3F0,0x3F1))
def test_full_raw32_result_zero_minimum_word_T_and_all_preserved_state(raw,expected,t,sr):
    _,context,memory,frame,value=evaluated(raw,sr)
    assert value['registers'][0]==value['registers'][4]==expected
    assert value['sr']==(sr&~1)|t
    assert value['ram']==memory and value['frame']==frame
    assert all(value['registers'][i]==context[i] for i in range(15) if i not in (0,4))
    assert (value['gbr'],value['mach'],value['macl'],value['sp'],value['pr'])==(
        context[15],context[16],context[17],0x02001000,0x02100000)
    assert value['path']==(0x22590,0x22592,*(() if t else (0x22594,)),0x22596,0x22598)


def test_minimum_word_retains_the_real_raw_NEG_carrier_and_zero_uses_the_NEG_path():
    minimum=evaluated(0x80000000)[-1];zero=evaluated(0)[-1]
    assert minimum['registers'][0]==0x80000000 and minimum['registers'][0]!=0x7FFFFFFF
    assert minimum['tags']['minimum_word'] is True
    assert zero['tags']['positive'] is False and 0x22594 in zero['path']


def test_code_observation_uses_the_existing_readonly_transport_and_no_relocation():
    source=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(source,image)
    assert fixture==image and aliases==[]
    assert image[0x22590:0x2259A]==bytes.fromhex('44158900644b000b6043')
    assert contract.UNIT['pools']==contract.UNIT['aliases']==[]
    assert source['adapter']['calibration_input'] is False
    assert source['readonly_observation']==[dict(address=0x22590,size=10)]
    assert source['adapter']['calibration']==source['readonly_observation']
    assert {row['name']:row['bits'] for row in source['adapter']['fields']}['raw_r4']==32


@pytest.mark.parametrize('field,value',(('raw_r4',-1),('raw_r4',1<<32),('raw_r4',True),
    ('raw_control_byte_0',256),('raw_control_byte_3',False),('variant',True),('initial_sr',2)))
def test_inputs_reject_boolean_narrowed_or_invalid_raw_carriers(field,value):
    case=dict(matrix.DEFAULTS,entry=0x22590,index=0,kind='controlled');case[field]=value
    with pytest.raises(ValueError):matrix.require_case(case)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_source_grants_no_identity_type_scale_unit_caller_or_hardware_admission(tmp_path,flag):
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True)
    text=(repo.ROOT/contract.DESCRIPTOR).read_text();path.write_text(text.replace(flag+' = false',flag+' = true',1))
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_specification_counts_and_words_read_the_execution_descriptor():
    source=contract.descriptor(repo.ROOT)
    text=' '.join((repo.ROOT/'defs/JK08A.signed-abs-register-helper-withdrawal-paths.md').read_text().split())
    count=sum((row['end']-row['start'])//2 for row in source['unit']['code'])
    assert len(source['unit']['code'])==1 and 'one complete function body' in text
    assert count==5 and f'{count} stock instructions' in text
    assert sum(row['size'] for row in source['readonly_observation'])==10 and '10 immutable code bytes' in text
    assert len(source['unit']['pools'])==0 and '0 literal pools' in text
    assert len(source['unit']['aliases'])==0 and '0 pointer aliases' in text
    assert source['context_bytes']==80 and '80-byte input context' in text
    assert source['frame_bytes']==192 and '192-byte frame' in text
    assert source['adapter']['profile']=='ordinary-80-572' and '572-byte observation record' in text
    assert len(transfers.WORDS)==count
