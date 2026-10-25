"""Actual complete curve observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import maf_transfer_contract as contract,maf_transfer_capture_evidence as proof
from kb import maf_transfer_semantics as scalar


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['maf_transfer_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original MAF curve slice capture')
        pytest.skip('the complete original MAF curve slice capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_missing_original_curve_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('maf_transfer_paths')
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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_maf_transfer.s',
    'tools/sh-elf-run/harness-maf-transfer.c','tools/sh-elf-run/maf_transfer_capture.py',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'tools/kb/src/kb/maf_transfer_contract.py','tools/kb/src/kb/maf_transfer_capture_evidence.py',
    'tools/kb/src/kb/maf_transfer_matrix.py','tools/kb/src/kb/maf_transfer_semantics.py',
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


@pytest.mark.parametrize('adcs',((0,0),(16,0),(0,16),(1008,1008),(65535,65535)))
@pytest.mark.parametrize('fault',('adc1','adc2','word-output','register-output','outside','r14','frame','abi',
    'sp','pr','sr','macl','continuation','curve','literal'))
def test_actual_ADC_pointer_curve_output_and_complete_state_are_required(actual_windows,adcs,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if (row['adc1'],row['adc2'])==adcs and row['profile']==0)
    observed=deepcopy(observations[case['index']])
    if fault in ('adc1','adc2','word-output','outside'):
        key='memory_before' if fault.startswith('adc') else 'memory_after'
        at={'adc1':0x1E48,'adc2':0x1E4A,'word-output':0x1054,'outside':0x1056}[fault]
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault=='r14':
        context=list(observed['context']);context[14]^=2;observed['context']=tuple(context)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[156]^=1;observed['frame_after']=bytes(frame)
    elif fault=='abi':
        values=list(observed['abi_after']);values[0]^=1;observed['abi_after']=tuple(values)
    elif fault in ('register-output','pr','sr','macl'):
        values=list(observed['exit']);values[{'register-output':19,'pr':1,'sr':0,'macl':2}[fault]]^=1
        observed['exit']=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    elif fault=='curve':
        data=bytearray(observed['calibration_before'][0x141F4]);data[0]^=1
        observed['calibration_before'][0x141F4]=bytes(data)
    else:observed['calibration_before'][0x26424]=bytes.fromhex('3e00')
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('adcs',((0,0),(16,16),(1008,1008)))
@pytest.mark.parametrize('fault',('omit-read','extra-read','site','width','direction','address','value','root-swap',
    'call-site','call-target','delay-table','delay-input','call-sp','call-pr','extra-call','return','scratch','macl'))
def test_actual_curve_leaf_transfer_order_and_real_call_arguments_are_required(actual_windows,adcs,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if (row['adc1'],row['adc2'])==adcs and row['profile']==0)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    leaf=next(row for row in result['accesses'] if row['domain']=='rom' and 0x141F4<=row['address']<0x142F4)
    if fault=='omit-read':result['accesses'].remove(leaf)
    elif fault=='extra-read':result['accesses'].append(deepcopy(leaf))
    elif fault in ('site','width','direction','address','value','root-swap'):
        if fault=='site':leaf['site']+=2
        elif fault=='width':leaf['width_bytes']=1
        elif fault=='direction':leaf['mode']='write'
        elif fault=='address':leaf['address']+=2
        elif fault=='root-swap':leaf['address']-=128
        else:leaf['bytes']='0000' if leaf['bytes']!='0000' else '0001'
    elif fault.startswith('call-') or fault.startswith('delay-'):
        call=result['calls'][0]
        if fault=='call-site':call['site']+=2
        elif fault=='call-target':call['target']+=2
        elif fault=='call-sp':call['entry']['sp']+=4
        elif fault=='call-pr':call['entry']['pr']+=2
        else:
            registers=list(call['entry']['registers']);registers[4 if fault=='delay-table' else 5]^=1
            call['entry']['registers']=tuple(registers)
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='return':next(row for row in result['branches'] if row['kind']=='return')['target']+=2
    elif fault=='scratch':
        registers=list(result['registers']);registers[0]^=1;result['registers']=tuple(registers)
    else:result['macl']^=1
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('field',('address','bytes','source_sha256','object_sha256','elf_sha256'))
def test_independently_assembled_curve_boundary_is_required(original,field):
    packet=deepcopy(original[2]);row=packet['boundaries'][0]
    if field=='address':row[field]+=2
    elif field=='bytes':row[field]='000b0009'
    else:row.pop(field)
    refuse(original,packet)


