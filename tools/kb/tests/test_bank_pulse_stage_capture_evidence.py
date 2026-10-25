"""Actual complete bank pulse observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import bank_pulse_stage_contract as contract,bank_pulse_stage_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['bank_pulse_stages']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original bank pulse capture')
        pytest.skip('the complete original bank pulse capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_missing_original_bank_pulse_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('bank_pulse_stages')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries',
                                  'observations','simulator','toolchain'))
def test_missing_actual_input_refuses(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','boundary','returncode','timeout','compiler','simulator','private'))
def test_changed_actual_stock_bytes_inputs_or_terminal_refuse(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction'][0]['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction'][0]['pools'][0]['stock']='00000000'
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
    elif fault=='role':rows[0]['kind']^=1
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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_pulse_precursor.s',
    'tools/sh-elf-run/stock_jk08a_channel_pulse.s','tools/sh-elf-run/harness-bank-pulse-stages.c',
    'tools/sh-elf-run/bank_pulse_stage_capture.py','tools/kb/src/kb/bank_pulse_stage_contract.py',
    'tools/kb/src/kb/bank_pulse_stage_matrix.py','tools/kb/src/kb/bank_pulse_stage_semantics.py',
    'tools/kb/src/kb/bank_pulse_stage_capture_evidence.py','tools/sh-elf-run/stock_precursor_model.py',
    'tools/kb/tests/test_channel_pulse_chain.py','tools/sh-elf-run/pulse-precursor-cases.h',
    'tools/sh-elf-run/channel-pulse-cases.h','tools/kb/src/kb/byte_surface_equations.py'))
def test_stale_actual_consumed_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    return declared,image,fixture,observations




def selected_case(declared,kind):
    if kind=='precursor':
        return next(row for row in declared['cases'] if row['kind']==kind and row['cap_flags']==0
            and row['bank0']==row['bank1']==25600 and row['gain']==16384 and row['bfs']==32768)
    return next(row for row in declared['cases'] if row['kind']==kind and row['channel']==1 and row['mask']==0
        and row['odd_base']==65535 and row['additive']==32767 and row['multiplier']==255)


def numeric_model(kind):
    if kind=='channel':return None
    from kb.test_stock_capture import tool
    return tool(repo.ROOT,'stock_precursor_model.py','_kb_bank_pulse_stage_actual_test_numeric')


@pytest.mark.parametrize('kind',('precursor','channel'))
@pytest.mark.parametrize('fault',('input','output','sibling','outside','r4','frame','abi','sp','continuation',
    'exit','pr','calibration','prepared-sr'))
def test_each_actual_stage_refuses_changed_inputs_and_complete_machine_state(actual_windows,kind,fault):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,kind)
    observed=deepcopy(observations[case['index']])
    if fault in ('input','output','sibling','outside'):
        key='memory_before' if fault=='input' else 'memory_after'
        at={'precursor':{'input':0x40B8,'output':0x18C2,'sibling':0x18C0},
            'channel':{'input':0x191E,'output':0x23CA,'sibling':0x23C8}}[kind].get(fault,0x1234)
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault=='r4':
        context=list(observed['context']);context[4]^=1;observed['context']=tuple(context)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('abi','exit','pr'):
        key='abi_after' if fault=='abi' else 'exit';values=list(observed[key]);values[1 if fault=='pr' else 0]^=1;observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    elif fault=='prepared-sr':observed['sr_before']^=0x100
    else:
        at=next(iter(observed['calibration_before']));raw=bytearray(observed['calibration_before'][at]);raw[0]^=1
        observed['calibration_before'][at]=bytes(raw)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('kind',('precursor','channel'))
@pytest.mark.parametrize('fault',('site','width','direction','address','bytes','missing-call','extra-call','call-order','call-argument'))
def test_actual_stage_transfers_and_real_post_delay_calls_are_required(actual_windows,kind,fault):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,kind)
    observed=observations[case['index']];result,_=proof.require_state(declared,image,fixture,case,observed)
    result=deepcopy(result)
    if fault=='missing-call':result['calls'].pop(0)
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='call-order':result['calls'][0],result['calls'][1]=result['calls'][1],result['calls'][0]
    elif fault=='call-argument':
        registers=list(result['calls'][0]['entry']['registers']);registers[1 if kind=='precursor' else 0]^=1
        result['calls'][0]['entry']['registers']=registers
    else:
        site,at=(0x4EA62,0x010018C2) if kind=='precursor' else (0x4EC9E,0x010023CA)
        row=next(row for row in result['accesses'] if row['site']==site and row['address']==at)
        if fault=='site':row['site']+=2
        elif fault=='width':row['width_bytes']=1
        elif fault=='direction':row['mode']='read'
        elif fault=='address':row['address']+=2
        else:row['bytes']='0000' if row['bytes']!='0000' else '0001'
    with pytest.raises(ValueError):proof.semantic(case,observed,result,numeric_model(kind))
