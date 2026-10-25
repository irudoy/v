"""Actual complete original observations reject wrong ranges, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import ram_initialization_contract as contract,ram_initialization_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['ram_initialization_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original RAM clear capture')
        pytest.skip('the complete original RAM clear capture is unavailable')
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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_ram_initialization.s',
    'tools/sh-elf-run/harness-ram-initialization.c','tools/sh-elf-run/ram_initialization_capture.py',
    'tools/kb/src/kb/ram_initialization_contract.py','tools/kb/src/kb/ram_initialization_capture_evidence.py',
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


@pytest.mark.parametrize('window',range(5))
@pytest.mark.parametrize('fault',('input','first','last-tail','outside','context','frame','abi','sp','continuation','exit','calibration'))
def test_each_actual_window_refuses_wrong_field_boundary_or_complete_state(actual_windows,window,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==contract.WINDOWS[window]['start'])
    observed=deepcopy(observations[case['index']]);spec=contract.WINDOWS[window]
    first=spec['first']&65535;end=first+4*contract.stores(spec)
    if fault in ('input','first','last-tail','outside'):
        key='memory_before' if fault=='input' else 'memory_after'
        at=first if fault in ('input','first') else end-1 if fault=='last-tail' else end
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
        data=bytearray(observed['calibration_before'][0x22614]);data[0]^=1
        observed['calibration_before'][0x22614]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.fixture(scope='module')
def natural_helper(actual_windows):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==0x26F30)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed)
    return contract.WINDOWS[-1],observed,result


@pytest.mark.parametrize('fault',('pointer','first','limit','reload-width','omit-reload','duplicate-reload',
    'read-write-order','store-address','return-site','return-target','frame-write','frame-byte',
    'R0','R1','R2','R6','GBR','MACH','MACL'))
def test_natural_helper_requires_ordered_ROM_descriptors_stores_and_real_complete_return(natural_helper,fault):
    window,observed,result=deepcopy(natural_helper);end=0x5CF4
    accesses=result['accesses']
    if fault in ('pointer','first','limit','reload-width','omit-reload','duplicate-reload','read-write-order','store-address'):
        site={'pointer':0x26F30,'first':0x26F32,'limit':0x26F36,'store-address':0x26F3E}.get(fault,0x26F42)
        selected=next(row for row in accesses if row['site']==site)
        if fault in ('pointer','first','limit'):selected['bytes']='00000000'
        elif fault=='store-address':selected['address']+=4
        elif fault=='reload-width':selected['width_bytes']=2
        elif fault=='omit-reload':accesses.remove(selected)
        elif fault=='duplicate-reload':accesses.insert(accesses.index(selected),deepcopy(selected))
        else:
            index=accesses.index(selected);accesses[index-1],accesses[index]=accesses[index],accesses[index-1]
    elif fault.startswith('return-'):
        returned=next(row for row in result['branches'] if row['kind']=='return')
        returned['site' if fault=='return-site' else 'target']+=2
    elif fault=='frame-write':
        accesses.append(dict(site=0x26F3E,mode='write',domain='frame',address=observed['sp'],width_bytes=4,bytes='00000000'))
    elif fault=='frame-byte':
        frame=bytearray(observed['frame_after']);frame[0]^=1;observed['frame_after']=bytes(frame)
    elif fault.startswith('R'):
        registers=list(result['registers']);registers[int(fault[1:])]^=1;result['registers']=tuple(registers)
    else:result[fault.lower()]^=1
    with pytest.raises(ValueError):proof.require_natural_helper(window,observed,result,end)


def test_natural_helper_actual_nonempty_loop_writes_the_root_and_keeps_both_tail_bytes(natural_helper):
    window,observed,result=natural_helper
    assert observed['memory_before'][0][0x5B2C]!=0 and observed['memory_after'][0][0x5B2C:0x5B30]==bytes(4)
    assert observed['memory_after'][0][0x5CF0:0x5CF4]==bytes(4)
    assert observed['memory_after'][0][0x5CF4]==observed['memory_before'][0][0x5CF4]
    assert [(row['site'],row['kind']) for row in result['branches'] if row['site']==0x26F3A]==[(0x26F3A,'fallthrough')]
    assert {row['kind'] for row in result['branches'] if row['site']==0x26F46}=={'taken','fallthrough'}
    assert all(row['address']!=0x26F4C for row in contract.RETURNS)
