"""Actual complete programmer observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import phase_programmer_contract as contract,phase_programmer_capture_evidence as proof
from kb import phase_programmer_semantics as scalar


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['phase_programmer_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original phase programmer capture')
        pytest.skip('the complete original phase programmer capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_missing_original_programmer_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('phase_programmer_paths')
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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_injection_offset.s',
    'tools/sh-elf-run/harness-phase-programmer.c','tools/sh-elf-run/phase_programmer_capture.py',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s','tools/sh-elf-run/injection-offset-cases.h',
    'tools/kb/src/kb/phase_programmer_contract.py','tools/kb/src/kb/phase_programmer_capture_evidence.py',
    'tools/kb/src/kb/phase_programmer_matrix.py','tools/kb/src/kb/phase_programmer_semantics.py',
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/phase_split_semantics.py'))

def test_stale_actual_consumed_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    return declared,image,fixture,observations


@pytest.mark.parametrize('period,remainder',((0,0),(1,10),(8192,4),(25000,8),(65535,255)))
@pytest.mark.parametrize('fault',('period','remainder','word','byte','outside','context','frame',
    'abi','sp','pr','macl','continuation','calibration'))
def test_actual_post_guard_input_output_and_complete_state_are_required(actual_windows,period,remainder,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['period']==period and row['remainder']==remainder)
    observed=deepcopy(observations[case['index']])
    if fault in ('period','remainder','word','byte','outside'):
        key='memory_before' if fault in ('period','remainder') else 'memory_after'
        at={'period':0x22BC,'remainder':0x193B,'word':0x16C2,'byte':0x166C,'outside':0x13B8}[fault]
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault=='context':
        context=list(observed['context']);context[13]^=1;observed['context']=tuple(context)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[156]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('abi','pr','macl'):
        key='abi_after' if fault=='abi' else 'exit';values=list(observed[key]);values[1 if fault=='pr' else 2]^=1
        observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:observed['calibration_before'][0x28EA0]=bytes.fromhex('1999')
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('period,remainder',((0,0),(1,10),(8192,4),(65535,255)))
@pytest.mark.parametrize('fault',('omit-word','omit-byte','extra-read','width','direction','address','value',
    'literal','call-site','call-target','delay-argument','call-sp','call-pr','extra-call','return','scratch','macl'))
def test_actual_call_delay_slot_stores_and_physical_widths_are_required(actual_windows,period,remainder,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['period']==period and row['remainder']==remainder)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    if fault in ('omit-word','omit-byte'):
        site=0x28E94 if fault=='omit-word' else 0x28E98
        result['accesses']=[row for row in result['accesses'] if row['site']!=site]
    elif fault=='extra-read':
        row=deepcopy(next(row for row in result['accesses'] if row['site']==0x28E94))
        row['mode']='read';result['accesses'].append(row)
    elif fault.startswith('call-') or fault=='delay-argument':
        call=result['calls'][0]
        if fault=='call-site':call['site']+=2
        elif fault=='call-target':call['target']+=2
        elif fault=='call-sp':call['entry']['sp']+=4
        elif fault=='call-pr':call['entry']['pr']+=2
        else:
            registers=list(call['entry']['registers']);registers[6]-=0x3E0
            call['entry']['registers']=tuple(registers)
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='return':
        next(row for row in result['branches'] if row['kind']=='return')['target']+=2
    elif fault=='scratch':
        registers=list(result['registers']);registers[13]^=1;result['registers']=tuple(registers)
    elif fault=='macl':result['macl']^=1
    else:
        row=next(row for row in result['accesses'] if row['site']==(0x28E7E if fault=='literal' else 0x28E94))
        if fault=='literal':row['bytes']='1999'
        elif fault=='width':row['width_bytes']=1
        elif fault=='direction':row['mode']='read'
        elif fault=='address':row['address']+=2
        else:row['bytes']='0000' if row['bytes']!='0000' else '0001'
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('field',('address','bytes','source_sha256','object_sha256','elf_sha256'))
def test_independently_assembled_outside_return_is_required(original,field):
    packet=deepcopy(original[2]);row=packet['boundaries'][0]
    if field=='address':row[field]+=2
    elif field=='bytes':row[field]='000b0009'
    else:row.pop(field)
    refuse(original,packet)


