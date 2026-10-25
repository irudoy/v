"""Actual complete bank pulse observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import bank_pulse_contract as contract,bank_pulse_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['bank_pulse_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original bank pulse capture')
        pytest.skip('the complete original bank pulse capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_missing_original_bank_pulse_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('bank_pulse_paths')
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
    elif fault=='boundary':packet['boundaries'].append(dict(address=0x4EBA2,bytes='000b0009'))
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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_bank_base_pulse.s',
    'tools/sh-elf-run/harness-bank-pulse.c','tools/sh-elf-run/bank_pulse_capture.py',
    'tools/kb/src/kb/bank_pulse_contract.py','tools/kb/src/kb/bank_pulse_capture_evidence.py',
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/tests/test_bank_base_pulse_chain.py','tools/sh-elf-run/stock-jk08a-bank-base-pulse-cases.h',
    'tools/kb/src/kb/bank_pulse_semantics.py','tools/kb/src/kb/bank_pulse_matrix.py'))
def test_stale_actual_consumed_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    return declared,image,fixture,observations


@pytest.mark.parametrize('bank',(0,1))
@pytest.mark.parametrize('fault',('s-input','l-input','precursor-input','offset-input','sibling-input',
    'output','sibling-output','outside','r4','frame','abi','sp','continuation','exit','pr','calibration'))
def test_each_actual_bank_refuses_changed_inputs_or_complete_state(actual_windows,bank,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['raw_r4']&255==bank and row['variant']==7
              and row['precursor']==32768)
    observed=deepcopy(observations[case['index']]);shift=bank*2
    addresses={'s-input':0x22DC+shift,'l-input':0x2302+shift,'precursor-input':0x18C0+shift,
        'offset-input':0x2310+shift,'sibling-input':0x22DC+(1-bank)*2,
        'output':0x191C+shift,'sibling-output':0x191C+(1-bank)*2,'outside':0x1234}
    if fault in addresses:
        key='memory_before' if fault.endswith('input') else 'memory_after'
        memory=bytearray(observed[key][0]);memory[addresses[fault]]^=1;observed[key]=(bytes(memory),)
    elif fault=='r4':
        values=list(observed['context']);values[4]^=1;observed['context']=tuple(values)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('abi','exit','pr'):
        key='abi_after' if fault=='abi' else 'exit';values=list(observed[key]);values[1 if fault=='pr' else 0]^=1;observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:
        data=bytearray(observed['calibration_before'][0x4EC04]);data[0]^=1
        observed['calibration_before'][0x4EC04]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('bank',(0,1))
@pytest.mark.parametrize('fault',('site','width','direction','address','bytes','call','scratch'))
def test_actual_banks_refuse_changed_physical_transfer_or_scratch_state(actual_windows,bank,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['raw_r4']&255==bank and row['variant']==7
              and row['precursor']==32768)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    if fault=='call':result['calls'].append(dict(site=0x4EB9E,target=0x4EBA2))
    elif fault=='scratch':
        values=list(result['registers']);values[2]^=1;result['registers']=values
    else:
        row=next(row for row in result['accesses'] if row['site']==0x4EB5E)
        if fault=='site':row['site']+=2
        elif fault=='width':row['width_bytes']=1
        elif fault=='direction':row['mode']='write'
        elif fault=='address':row['address']+=2
        else:row['bytes']='0000' if row['bytes']!='0000' else '0001'
    with pytest.raises(ValueError):proof.semantic(case,observed,result)


@pytest.mark.parametrize('site',(0x4EB04,0x4EB42))
def test_both_actual_LTFT_read_sites_are_required_independently(actual_windows,site):
    declared,image,fixture,observations=actual_windows
    def selected(case):
        if case['raw_r4']&255!=1:return False
        if site==0x4EB04:return bool(case['f1']&2)
        return not case['f1']&2 and case['c1' if case['f2']&16 else 'c0']<=16384
    case=next(row for row in declared['cases'] if selected(row));observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    result['accesses']=[row for row in result['accesses'] if row['site']!=site]
    with pytest.raises(ValueError):proof.semantic(case,observed,result)
