"""Width-view refusals bind actual complete common-primary observations."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile, copy_evidence, repo, test_evidence
from kb import width_view_capture_evidence as proof, width_view_matrix as matrix


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['width_views']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires its complete original width-view record')
        pytest.skip('the complete original width-view record is not available')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['automatic_resolution'] is False
    assert set(result['fields'])=={
        '7mfk-ffff118a/ram','7mfk-ffff16d2/ram','7mfk-ffff4544/ram','7mfk-ffff2142/ram'}
    return model,record,packet


def refuse(original,packet):
    model,record,_=original
    with pytest.raises(ValueError):
        proof.require_witness(model,packet,record['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('consumed','reconstruction','aliases','boundaries','image_sha256',
    'fixture_sha256','elf_sha256','observer_object_sha256','simulator','declaration','observations'))
def test_width_view_physical_binding_cannot_be_omitted(original,field):
    packet=dict(original[2])
    packet.pop(field)
    refuse(original,packet)


@pytest.mark.parametrize('fault',('layout','width','native-claim','dropped-site','entry','GBR','selector-range',
                                  'automatic-resolution','alias','boundary','source','terminal','self-admission'))
def test_width_view_capture_cannot_substitute_a_semantic_or_physical_binding(original,fault):
    packet=dict(original[2])
    if fault in ('layout','width','native-claim','dropped-site','entry','GBR','selector-range','automatic-resolution'):
        declared=deepcopy(packet['declaration'])
        packet['declaration']=declared
        if fault=='layout':declared['layout']='1nd'
        elif fault=='width':declared['fields'][0]['declared_bits']=16
        elif fault=='native-claim':declared['fields'][0]['original_claim_sha256']='0'*64
        elif fault=='dropped-site':declared['fields'][0]['observed'].pop()
        elif fault=='entry':declared['windows'][0]['entries'][0]+=2
        elif fault=='GBR':declared['windows'][0]['gbr']+=2
        elif fault=='selector-range':declared['selector_range_inference']=True
        else:declared['automatic_resolution']=True
    elif fault=='alias':packet['aliases']=[{**row,'alias':row['alias']+1} for row in packet['aliases']]
    elif fault=='boundary':packet['boundaries']=[{**row,'bytes':'57f6442a000b0009'} for row in packet['boundaries']]
    elif fault=='source':packet['consumed']={**packet['consumed'],proof.OBSERVER:'000b0009'}
    elif fault=='terminal':packet['simulator']={**packet['simulator'],'returncode':4}
    else:packet['semantic_admission']=True
    refuse(original,packet)


def encoded(memory):
    result=[]
    start=0
    while start<len(memory):
        end=start+1
        while end<len(memory) and memory[end]==memory[start]:end+=1
        result.append(f'{end-start}:{memory[start]:02x}')
        start=end
    return ','.join(result)


@pytest.mark.parametrize('field,offset',(
    ('context',0),('context',59),('context',75),('context',79),('context_after',59),
    ('observation',0),('observation',51),('observation',83),('observation',183),
    ('observation',375),('observation',567),('ram_before',0x118B),('ram_before',0x16D3),
    ('ram_before',0x2143),('ram_after',0x118A),('ram_after',0x4545),('ram_after',0x1234)))
def test_consistent_raw_stream_cannot_replace_complete_independent_width_state(original,field,offset):
    held=original[2]
    packet=dict(held)
    row=dict(held['observations'][0])
    if field.startswith('ram_'):
        value=bytearray(matrix.decode_rle(row[field]))
        value[offset]^=1
        row[field]=encoded(value)
    else:
        value=bytearray.fromhex(row[field])
        value[offset]^=1
        row[field]=value.hex()
    packet['observations']=[row,*held['observations'][1:]]
    lines=held['stdout'].splitlines()
    position=next(index for index,line in enumerate(lines) if line.startswith(proof.PREFIX))
    lines[position]=proof.PREFIX+json.dumps(row)
    packet['stdout']='\n'.join(lines)+'\n'
    packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original,packet)


@pytest.mark.parametrize('fault',('missing','duplicate','order','wrong-original','failed-terminal'))
def test_width_views_require_the_same_complete_successful_primary(original,fault):
    model,held,_=original
    record={**held,'candidate':dict(held['candidate']),'terminal':dict(held['terminal'])}
    if fault=='missing':
        record['candidate']['witness']={key:value for key,value in held['candidate']['witness'].items() if key!='width_views'}
    elif fault in ('duplicate','order'):
        packet=dict(held['candidate']['witness']['width_views'])
        rows=list(packet['observations'])
        if fault=='duplicate':rows.append(rows[0])
        else:rows[0],rows[1]=rows[1],rows[0]
        packet['observations']=rows
        record['candidate']['witness']={**held['candidate']['witness'],'width_views':packet}
    elif fault=='wrong-original':record['process_sha256']='0'*64
    else:record['terminal']['actual_exit_code']=1
    with pytest.raises(ValueError):
        proof.require_primary(model,record)
