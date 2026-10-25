"""Direct-callee raw originals grant neither caller attribution nor datum identity."""

import hashlib,json
import pytest
from kb import compile,copy_evidence,repo,test_evidence,width_view_matrix
from kb import division_callees_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['division_callees_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original direct-division capture')
        pytest.skip('the complete original direct-division capture is unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['caller_argument_inference'] is False
    assert result['datum_identity_inference'] is False
    assert result['automatic_resolution'] is False
    assert result['native_relation_publication'] is False
    assert result['scale_admission'] is False
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries',
    'image_sha256','fixture_sha256','simulator','observations'))
def test_missing_direct_original_physical_input_refuses(original,field):
    packet=dict(original[2]);packet.pop(field);refuse(original,packet)


def encode(memory):
    result=[];start=0
    while start<len(memory):
        end=start+1
        while end<len(memory) and memory[end]==memory[start]:end+=1
        result.append(f'{end-start}:{memory[start]:02x}');start=end
    return ','.join(result)


@pytest.mark.parametrize('field,offset',(
    ('context',3),('context',7),('context',75),('context',79),('context_after',3),
    ('observation',0),('observation',3),('observation',79),('observation',183),
    ('observation',375),('observation',567),('ram_before',0x9818),
    ('ram_after',0x9818),('ram_after',0x981B),('ram_after',0x981C),('ram_after',0x1234)))
def test_consistent_stream_cannot_replace_signed_SR_full_state_or_fault_store(original,field,offset):
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
