"""Actual complete normalizer observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import phase_normalization_contract as contract,phase_normalization_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['phase_normalization_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original phase normalization capture')
        pytest.skip('the complete original phase normalization capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_missing_original_normalizer_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('phase_normalization_paths')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries',
                                  'observations','simulator','toolchain'))
def test_missing_actual_input_refuses(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','boundary','returncode','timeout','compiler','simulator','private'))
def test_changed_actual_stock_bytes_inputs_or_terminal_refuse(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'][0]['stock']='00000000'
    elif fault=='alias':packet['aliases'][0]['alias']+=4
    elif fault=='boundary':packet['boundaries'].append(dict(address=0x28E7C,bytes='000b0009'))
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=0
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    else:packet['consumed'][proof.OBSERVER]+='00'
    refuse(original,packet)


@pytest.mark.parametrize('fault',('omit','duplicate','swap','entry','role','index','stream','const-context'))
def test_changed_actual_invocations_refuse_with_consistent_stream_hash(original,fault):
    packet=deepcopy(original[2]);rows=packet['observations']
    if fault=='omit':rows.pop()
    elif fault=='duplicate':rows[-1]=deepcopy(rows[0])
    elif fault=='swap':rows[0],rows[-1]=rows[-1],rows[0]
    elif fault=='entry':rows[0]['entry']+=2
    elif fault=='role':rows[0]['kind']=1
    elif fault=='index':rows[0]['index']=True
    elif fault=='stream':
        data=bytearray.fromhex(rows[0]['observation']);data[0]^=1;rows[0]['observation']=data.hex()
    else:
        data=bytearray.fromhex(rows[0]['context_after']);data[0]^=1;rows[0]['context_after']=data.hex()
    iterator=iter(rows);lines=[]
    for line in packet['stdout'].splitlines(keepends=True):
        if line.startswith(proof.PREFIX):
            row=next(iterator,None)
            if row is not None:lines.append(proof.PREFIX+json.dumps(row,separators=(',',':'))+'\n')
        else:lines.append(line)
    packet['stdout']=''.join(lines);packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original,packet)


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_injection_tooth.s',
    'tools/sh-elf-run/harness-phase-normalization.c','tools/sh-elf-run/phase_normalization_capture.py',
    'tools/kb/src/kb/phase_normalization_contract.py','tools/kb/src/kb/phase_normalization_capture_evidence.py',
    'tools/kb/src/kb/byte_surface_equations.py','tools/sh-elf-run/stock_injection_programmer_model.py'))
def test_stale_actual_consumed_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    return declared,image,fixture,observations


@pytest.mark.parametrize('pair',range(2))
@pytest.mark.parametrize('fault',('word-input','byte-input','phase-input','word-output','byte-output','outside',
    'r4','r5','frame','abi','sp','continuation','exit','calibration'))
def test_each_actual_pair_refuses_changed_pointer_datum_or_complete_state(actual_windows,pair,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['pair']==pair and row['phase']==4 and row['count']==4)
    observed=deepcopy(observations[case['index']])
    if fault in ('word-input','byte-input','phase-input','word-output','byte-output','outside'):
        key='memory_before' if fault.endswith('input') else 'memory_after'
        at=case['word']&65535 if fault.startswith('word-') else case['byte']&65535
        if fault=='phase-input':at=0x13B2
        elif fault=='outside':at=0x1234
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault in ('r4','r5'):
        values=list(observed['context']);values[int(fault[1:])]^=2;observed['context']=tuple(values)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('abi','exit'):
        key='abi_after' if fault=='abi' else 'exit';values=list(observed[key]);values[0]^=1;observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:
        data=bytearray(observed['calibration_before'][0x28E9E]);data[0]^=1
        observed['calibration_before'][0x28E9E]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('pair',range(2))
@pytest.mark.parametrize('fault',('site','width','direction','address','bytes','call','scratch'))
def test_actual_pointer_pairs_refuse_changed_physical_transfer_or_scratch_state(actual_windows,pair,fault):
    from kb.test_stock_capture import tool
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['pair']==pair and row['phase']==9 and row['count']==9)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed)
    result=deepcopy(result)
    if fault=='call':result['calls'].append(dict(site=0x28E74,target=0x28E7C))
    elif fault=='scratch':
        values=list(result['registers']);values[2]^=1;result['registers']=values
    else:
        row=next(row for row in result['accesses'] if row['site']==0x28E08)
        if fault=='site':row['site']+=2
        elif fault=='width':row['width_bytes']=2
        elif fault=='direction':row['mode']='read'
        elif fault=='address':row['address']+=1
        else:row['bytes']='00' if row['bytes']!='00' else '01'
    numeric=tool(repo.ROOT,'stock_injection_programmer_model.py','_kb_phase_normalization_test_numeric')
    with pytest.raises(ValueError):proof.semantic(case,observed,result,numeric)
