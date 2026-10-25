"""Original denominator observations fence the zero bypass and complete state."""

import hashlib,json
import pytest
from kb import compile,copy_evidence,repo,test_evidence,width_view_matrix
from kb import timing_denominator_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['timing_denominator_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original timing-denominator capture')
        pytest.skip('the complete original timing-denominator capture is unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['bounded_argument_lineage'] is True and result['zero_bypass_distinct_from_fault_store'] is True
    assert result['datum_identity_inference'] is False and result['automatic_resolution'] is False
    assert result['native_relation_publication'] is False and result['scale_admission'] is False
    assert any(row['zero_bypass'] for row in result['semantic_results'])
    assert any(row['arguments'] is not None for row in result['semantic_results'])
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries',
    'image_sha256','fixture_sha256','simulator','observations'))
def test_missing_denominator_physical_input_refuses(original,field):
    packet=dict(original[2]);packet.pop(field);refuse(original,packet)


def encode(memory):
    result=[];start=0
    while start<len(memory):
        end=start+1
        while end<len(memory) and memory[end]==memory[start]:end+=1
        result.append(f'{end-start}:{memory[start]:02x}');start=end
    return ','.join(result)


@pytest.mark.parametrize('field,offset',(
    ('context',7),('context',79),('observation',0),('observation',567),
    ('ram_before',0x412A),('ram_before',0x11B6),('ram_before',0x10BC),('ram_before',0x41FB),('ram_before',0x4214),
    ('ram_after',0x2CFD),('ram_after',0x2C6C),('ram_after',0x35D6),('ram_after',0x35D2),('ram_after',0x9818),
    ('calibration_before',0),('calibration_after',0)))
def test_consistent_stream_cannot_replace_denominator_arguments_or_the_fault_word(original,field,offset):
    held=original[2];packet=dict(held);row=dict(held['observations'][0])
    if field.startswith('ram_'):
        value=bytearray(width_view_matrix.decode_rle(row[field]));value[offset]^=1;row[field]=encode(value)
    else:
        value=bytearray.fromhex(row[field]);value[offset]^=1;row[field]=value.hex()
    packet['observations']=[row,*held['observations'][1:]]
    lines=held['stdout'].splitlines();position=next(i for i,line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[position]=proof.PREFIX+json.dumps(row);packet['stdout']='\n'.join(lines)+'\n'
    packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original,packet)
