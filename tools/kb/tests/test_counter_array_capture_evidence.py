"""Actual complete original observations reject wrong ranges, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import counter_array_contract as contract,counter_array_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['counter_array_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original counter array capture')
        pytest.skip('the complete original counter array capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


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
    elif fault=='boundary':packet['boundaries'][0]['address']+=2
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=0
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    else:packet['consumed'][proof.OBSERVER]+='00'
    refuse(original,packet)


@pytest.mark.parametrize('fault',('omit','duplicate','swap','entry','role','index','stream'))
def test_changed_actual_invocations_refuse_with_consistent_stream_hash(original,fault):
    packet=deepcopy(original[2]);rows=packet['observations']
    if fault=='omit':rows.pop()
    elif fault=='duplicate':rows[-1]=deepcopy(rows[0])
    elif fault=='swap':rows[0],rows[-1]=rows[-1],rows[0]
    elif fault=='entry':rows[0]['entry']+=2
    elif fault=='role':rows[0]['kind']=1
    elif fault=='index':rows[0]['index']=True
    else:
        data=bytearray.fromhex(rows[0]['observation']);data[0]^=1;rows[0]['observation']=data.hex()
    iterator=iter(rows);lines=[]
    for line in packet['stdout'].splitlines(keepends=True):
        if line.startswith(proof.PREFIX):
            row=next(iterator,None)
            if row is not None:lines.append(proof.PREFIX+json.dumps(row,separators=(',',':'))+'\n')
        else:lines.append(line)
    packet['stdout']=''.join(lines);packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    refuse(original,packet)


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_counter_arrays.s',
    'tools/sh-elf-run/harness-ram-initialization.c','tools/sh-elf-run/counter_array_capture.py',
    'tools/kb/src/kb/counter_array_contract.py','tools/kb/src/kb/counter_array_capture_evidence.py',
    'tools/kb/src/kb/byte_surface_equations.py'))
def test_stale_actual_consumed_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    return declared,image,fixture,observations


@pytest.mark.parametrize('window',range(3))
@pytest.mark.parametrize('fault',('input','first','last-element','outside','context','frame','abi','sp','continuation','exit','calibration'))
def test_each_actual_window_refuses_wrong_field_boundary_or_complete_state(actual_windows,window,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==contract.WINDOWS[window]['start'])
    observed=deepcopy(observations[case['index']]);spec=contract.WINDOWS[window]
    arrays=[array for array in contract.ARRAYS if array['entry']==spec['start']]
    first=min(array['first']&65535 for array in arrays)
    end=max((array['first']&65535)+array['width_bytes']*array['count'] for array in arrays)
    if fault in ('input','first','last-element','outside'):
        key='memory_before' if fault=='input' else 'memory_after'
        at=first if fault in ('input','first') else end-1 if fault=='last-element' else end
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault=='context':
        values=list(observed['context']);values[15]^=4;observed['context']=tuple(values)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('abi','exit'):
        key='abi_after' if fault=='abi' else 'exit';values=list(observed[key]);values[0]^=1;observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:
        data=bytearray(observed['calibration_before'][0x20660]);data[0]^=1
        observed['calibration_before'][0x20660]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.fixture(scope='module')
def holdoff_cases(actual_windows):
    declared,image,fixture,observations=actual_windows;selected=[]
    for case in declared['cases']:
        if 'holdoff' not in case:continue
        observed=observations[case['index']]
        result,_=proof.require_state(declared,image,fixture,case,observed)
        selected.append((case,observed,result))
    return declared,selected


def test_actual_holdoff_exact_byte_has_fixed_other_positive_output_alternatives(holdoff_cases):
    declared,selected=holdoff_cases
    cases=[row[0] for row in selected];actual=[row[1] for row in selected]
    proof.require_holdoff_positive(actual,dict(declared,cases=cases))
    for case,observed,_ in selected:
        incoming=case['holdoff'];assert observed['memory_before'][0][0x25FF]==incoming
        assert observed['memory_after'][0][0x25FF]==max(0,incoming-1)
        assert observed['memory_before'][0][0x25FE]==observed['memory_before'][0][0x2600]==0xA5
        assert observed['memory_after'][0][0x25FE]==observed['memory_after'][0][0x2600]==0xA4


@pytest.mark.parametrize('fault',('omit','constant-output','confounded-neighbor','confounded-context','confounded-calibration'))
def test_actual_holdoff_positive_refuses_missing_or_confounded_exact_operand_pairs(holdoff_cases,fault):
    declared,selected=deepcopy(holdoff_cases);actual=[row[1] for row in selected]
    cases=[row[0] for row in selected]
    if fault=='omit':actual.pop();cases.pop()
    else:
        for index,row in enumerate(actual):
            if fault=='constant-output':
                memory=bytearray(row['memory_after'][0]);memory[0x25FF]=0;row['memory_after']=(bytes(memory),)
            elif fault=='confounded-neighbor':
                memory=bytearray(row['memory_before'][0]);memory[0x25FE]=index;row['memory_before']=(bytes(memory),)
            elif fault=='confounded-context':
                context=list(row['context']);context[0]=index;row['context']=tuple(context)
            else:row['calibration_before'][0x20B44]=index.to_bytes(4,'big')
    with pytest.raises(ValueError):proof.require_holdoff_positive(actual,dict(declared,cases=cases))


@pytest.mark.parametrize('fault',('ROM-pointer','width','store-direction','store-site','root-offset','omit-repeat',
    'return-site','return-target','frame','register-R0','register-R2','register-R5','register-R6'))
def test_actual_holdoff_refuses_changed_pointer_element_store_or_outside_return(holdoff_cases,fault):
    from kb import counter_array_matrix as matrix
    _,selected=holdoff_cases;case,observed,result=deepcopy(next(row for row in selected if row[0]['holdoff']==128))
    window=contract.WINDOWS[-1];_,wanted,_,_,_=proof.array_equation(window,observed['memory_before'][0])
    access=next(row for row in result['accesses'] if row['mode']=='write' and row['address']==matrix.RAM_BASE+0x25FF)
    if fault=='ROM-pointer':result['accesses'][0]['bytes']='010025fc'
    elif fault=='width':access['width_bytes']=2
    elif fault=='store-direction':access['mode']='read'
    elif fault=='store-site':access['site']+=2
    elif fault=='root-offset':access['address']+=1
    elif fault=='omit-repeat':
        result['accesses'].remove(next(row for row in result['accesses'] if row['site']==0x20950 and row['address']==matrix.RAM_BASE+0x25FF))
    elif fault.startswith('return-'):
        returned=next(row for row in result['branches'] if row['kind']=='return')
        returned['site' if fault=='return-site' else 'target']+=2
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    else:
        registers=list(result['registers']);registers[int(fault.rsplit('R',1)[1])]^=1;result['registers']=tuple(registers)
    with pytest.raises(ValueError):proof.require_holdoff_transfer(observed,result,wanted)
