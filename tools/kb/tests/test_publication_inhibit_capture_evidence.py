"""Actual-original refusals for cached publication and bounded snapshot paths."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence,width_view_matrix
from kb import publication_inhibit_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['publication_inhibit_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original publication-inhibit capture')
        pytest.skip('the complete original publication-inhibit capture is unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['ROM_to_snapshot_dependency_inference'] is False
    assert result['hardware_qualification'] is False
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('consumed','reconstruction','aliases','boundaries','stub_reconstruction',
    'image_sha256','fixture_sha256','simulator','declaration','observations'))
def test_missing_actual_original_physical_inputs_refuse(original,field):
    packet=dict(original[2]);packet.pop(field)
    refuse(original,packet)


@pytest.mark.parametrize('fault',('layout','scope','sequence','wrong-sink','wrong-native-window',
    'wrong-source','failed-simulator','self-admission'))
def test_substituted_execution_or_inference_scope_refuses(original,fault):
    packet=dict(original[2])
    if fault in ('layout','scope','sequence'):
        packet['declaration']=deepcopy(packet['declaration'])
        if fault=='layout':packet['declaration']['layout']='1nd'
        elif fault=='scope':packet['declaration']['ROM_to_snapshot_dependency_inference']=True
        else:packet['declaration']['cases'][1]['stage']=2
    elif fault=='wrong-sink':packet['stub_reconstruction']={**packet['stub_reconstruction'],'bytes':'000b0009'}
    elif fault=='wrong-native-window':packet['simulator']={**packet['simulator'],
        'command':[value.replace('0xffff8400','0xffff9900') for value in packet['simulator']['command']]}
    elif fault=='wrong-source':packet['consumed']={**packet['consumed'],proof.SINK:'000b0009'}
    elif fault=='failed-simulator':packet['simulator']={**packet['simulator'],'returncode':2}
    else:packet['semantic_admission']=True
    refuse(original,packet)


def encode(memory):
    result=[];start=0
    while start<len(memory):
        end=start+1
        while end<len(memory) and memory[end]==memory[start]:end+=1
        result.append(f'{end-start}:{memory[start]:02x}');start=end
    return ','.join(result)


@pytest.mark.parametrize('position,field,offset',(
    (0,'context',28),(0,'context',75),(0,'observation',2),(0,'observation',375),
    (0,'calibration_before',0),(0,'calibration_after',0),(0,'native_before',0xC3),
    (0,'native_after',0xC3),(1,'ram_before',0x2459),(1,'ram_before',0x257A),
    (1,'ram_before',0x1234),(1,'ram_after',0x1072),(2,'ram_before',0x1072),
    (2,'ram_before',0x1234),(2,'ram_after',0x106A),(2,'context',44)))
def test_consistent_stream_mutations_cannot_reset_RAM_or_replace_independent_equations(original,position,field,offset):
    held=original[2];packet=dict(held)
    row=dict(held['observations'][position])
    if field.startswith('ram_'):
        value=bytearray(width_view_matrix.decode_rle(row[field]));value[offset]^=1
        row[field]=encode(value)
    else:
        value=bytearray.fromhex(row[field]);value[offset]^=1;row[field]=value.hex()
    packet['observations']=list(held['observations']);packet['observations'][position]=row
    lines=held['stdout'].splitlines()
    positions=[index for index,line in enumerate(lines) if line.startswith(proof.PREFIX)]
    lines[positions[position]]=proof.PREFIX+json.dumps(row)
    packet['stdout']='\n'.join(lines)+'\n'
    packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original,packet)
