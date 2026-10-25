"""Actual complete admission observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import closed_loop_admission_contract as contract,closed_loop_admission_capture_evidence as proof
from kb import closed_loop_admission_semantics as scalar


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['closed_loop_admission_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original closed-loop admission decoder capture')
        pytest.skip('the complete original closed-loop admission decoder capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_missing_original_admission_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('closed_loop_admission_paths')
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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_closed_loop_adjustment.s',
    'tools/sh-elf-run/harness-closed-loop-admission.c','tools/sh-elf-run/closed_loop_admission_capture.py',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'tools/kb/src/kb/closed_loop_admission_contract.py','tools/kb/src/kb/closed_loop_admission_capture_evidence.py',
    'tools/kb/src/kb/closed_loop_admission_matrix.py','tools/kb/src/kb/closed_loop_admission_semantics.py',
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/width_view_matrix.py'))

def test_stale_actual_consumed_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    return declared,image,fixture,observations


def selected_case(declared,index,mask):
    entry=contract.ENTRIES[int(index==3)];field=('mask2c','mask2e','mask30','mask39')[index]
    return next(row for row in declared['cases'] if row['entry']==entry and row[field]==mask
                and row['variant']==0 and row['sr']==0
                and all(row[other]==0 for other in ('mask2c','mask2e','mask30','mask39') if other!=field))


@pytest.mark.parametrize('index',range(4))
@pytest.mark.parametrize('mask',(0,1,2,3,0x80,0xFF))
@pytest.mark.parametrize('fault',('raw','other-input','bank1','bank2','canary','gbr','r8','r9','r10',
    'frame-before','frame-after','abi','sp','pr','sr','macl','continuation','base-pool','offset-pool'))
def test_actual_mask_bank_outputs_premises_and_complete_state_are_required(actual_windows,index,mask,fault):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,index,mask)
    observed=deepcopy(observations[case['index']]);decoder=contract.DECODERS[index]
    at=(contract.INCOMING['gbr']&65535)+decoder['offset']
    offsets={'raw':decoder['input']&65535,'other-input':0x48C1,'bank1':at,'bank2':at+1,'canary':at+2}
    if fault in offsets:
        key='memory_before' if fault in ('raw','other-input') else 'memory_after'
        memory=bytearray(observed[key][0]);memory[offsets[fault]]^=1;observed[key]=(bytes(memory),)
    elif fault in ('gbr','r8','r9','r10'):
        context=list(observed['context']);context[{'gbr':15,'r8':8,'r9':9,'r10':10}[fault]]^=1
        observed['context']=tuple(context)
    elif fault in ('frame-before','frame-after'):
        key=fault.replace('-','_');frame=bytearray(observed[key]);frame[156]^=1;observed[key]=bytes(frame)
    elif fault=='abi':
        values=list(observed['abi_after']);values[0]^=1;observed['abi_after']=tuple(values)
    elif fault in ('pr','sr','macl'):
        values=list(observed['exit']);values[{'pr':1,'sr':0,'macl':2}[fault]]^=1;observed['exit']=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:
        pool=0xA114C if fault=='base-pool' else decoder['pool']
        data=bytearray(observed['calibration_before'][pool]);data[-1]^=1
        observed['calibration_before'][pool]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('index',range(4))
@pytest.mark.parametrize('mask',(0,1,2,3))
@pytest.mark.parametrize('fault',('omit-store','extra-store','site','width','direction','sibling-bank','value',
    'omit-read','read-address','read-value','read-width','extra-call','return','scratch','t','macl','mach','gbr'))
def test_actual_source_bit_bank_delay_slot_and_exact_byte_store_are_required(actual_windows,index,mask,fault):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,index,mask)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    decoder=contract.DECODERS[index];address=contract.INCOMING['gbr']+decoder['offset']+1
    store=next(row for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write' and row['address']==address)
    read=next(row for row in result['accesses'] if row['site']==decoder['read_site'])
    if fault=='omit-store':result['accesses'].remove(store)
    elif fault=='extra-store':result['accesses'].append(deepcopy(store))
    elif fault=='site':store['site']=decoder['zero_site'] if store['site']==decoder['one_site'] else decoder['one_site']
    elif fault=='width':store['width_bytes']=2
    elif fault=='direction':store['mode']='read'
    elif fault=='sibling-bank':store['address']-=1
    elif fault=='value':store['bytes']='01' if store['bytes']=='00' else '00'
    elif fault=='omit-read':result['accesses'].remove(read)
    elif fault=='read-address':read['address']+=1
    elif fault=='read-value':read['bytes']=bytes([mask^1]).hex()
    elif fault=='read-width':read['width_bytes']=2
    elif fault=='extra-call':result['calls'].append(dict(site=case['entry'],target=0xA0EE8))
    elif fault=='return':next(row for row in result['branches'] if row['kind']=='return')['target']+=2
    elif fault=='scratch':
        registers=list(result['registers']);registers[6]^=1;result['registers']=tuple(registers)
    elif fault=='t':result['sr']^=1
    else:result[fault]^=1
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('index',(0,1))
@pytest.mark.parametrize('field',('address','bytes','source_sha256','object_sha256','elf_sha256'))
def test_each_independently_assembled_outside_return_is_required(original,index,field):
    packet=deepcopy(original[2]);row=packet['boundaries'][index]
    if field=='address':row[field]+=2
    elif field=='bytes':row[field]='000b0009'
    else:row.pop(field)
    refuse(original,packet)
