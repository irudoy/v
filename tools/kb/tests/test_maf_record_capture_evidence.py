"""Actual complete record observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import maf_record_contract as contract,maf_record_capture_evidence as proof
from kb import maf_record_semantics as scalar


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['maf_record_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original MAF record reader capture')
        pytest.skip('the complete original MAF record reader capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('path',('tools/kb/src/kb/proof_sources.py','tools/kb/src/kb/proof_reuse.py'))
def test_actual_record_consumer_requires_transitive_source_binding_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError,match='dependency'):
        proof.require_witness(original[0],original[2],inputs)


def test_missing_original_record_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('maf_record_paths')
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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_maf_record_readers.s',
    'tools/sh-elf-run/harness-maf-record.c','tools/sh-elf-run/maf_record_capture.py',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'tools/kb/src/kb/maf_record_contract.py','tools/kb/src/kb/maf_record_capture_evidence.py',
    'tools/kb/src/kb/maf_record_matrix.py','tools/kb/src/kb/maf_record_semantics.py',
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/tests/test_ram_structure.py'))

def test_stale_actual_consumed_source_refuses(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared)
    return declared,image,fixture,observations


@pytest.mark.parametrize('entry',(0x25E20,0x3C3C6))
@pytest.mark.parametrize('flags',(0,0x80,0xFF))
@pytest.mark.parametrize('fault',('member','sibling0','sibling2','before-canary','status-input',
    'record-output','status-output','outside','argument','gbr','frame-before','frame-after',
    'abi','sp','pr','sr','macl','continuation','base-pool','index-pool'))
def test_actual_record_member_siblings_index_GBR_and_complete_state_are_required(actual_windows,entry,flags,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==entry and row['flags']==flags
              and row['argument']==0x129 and row['variant']==0 and row['sr']==0)
    observed=deepcopy(observations[case['index']])
    offsets={'member':0x5A94,'sibling0':0x5A93,'sibling2':0x5A95,
             'before-canary':0x5A92,'status-input':0x2449,
             'record-output':0x5A94,'status-output':0x2449,'outside':0x5A96}
    if fault in offsets:
        key='memory_after' if fault in ('record-output','status-output','outside') else 'memory_before'
        memory=bytearray(observed[key][0]);memory[offsets[fault]]^=1;observed[key]=(bytes(memory),)
    elif fault in ('argument','gbr'):
        context=list(observed['context']);context[4 if fault=='argument' else 15]^=1
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
        at=0x25F10 if fault=='base-pool' else 0x3C470
        data=bytearray(observed['calibration_before'][at]);data[-1]^=1
        observed['calibration_before'][at]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('entry',(0x25E20,0x3C3C6))
@pytest.mark.parametrize('flags',(0,0x80,0xFF))
@pytest.mark.parametrize('fault',('omit-read','extra-read','site','width','direction','sibling0','sibling2',
    'value','return','scratch','t','macl','mach','gbr'))
def test_actual_byte1_transfer_and_natural_return_are_required(actual_windows,entry,flags,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==entry and row['flags']==flags
              and row['argument']==0x129 and row['variant']==0 and row['sr']==0)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    leaf=next(row for row in result['accesses'] if row['site']==0x25E32)
    if fault=='omit-read':result['accesses'].remove(leaf)
    elif fault=='extra-read':result['accesses'].append(deepcopy(leaf))
    elif fault in ('site','width','direction','sibling0','sibling2','value'):
        if fault=='site':leaf['site']+=2
        elif fault=='width':leaf['width_bytes']=2
        elif fault=='direction':leaf['mode']='write'
        elif fault=='sibling0':leaf['address']-=1
        elif fault=='sibling2':leaf['address']+=1
        else:leaf['bytes']=bytes([flags^1]).hex()
    elif fault=='return':next(row for row in result['branches'] if row['kind']=='return')['target']+=2
    elif fault=='scratch':
        registers=list(result['registers']);registers[2]^=1;result['registers']=tuple(registers)
    elif fault=='t':result['sr']^=1
    else:result[fault]^=1
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('flags',(0,0x80,0xFF))
@pytest.mark.parametrize('fault',('call-site','call-target','call-return','call-sp','delay-index','entry-sp',
    'entry-pr','entry-gbr','extra-call','omit-read','omit-write','extra-write','rmw-site','rmw-width',
    'rmw-address','rmw-value','observing-return','register-output'))
def test_actual_coordinator_call_delay_RMW_and_separate_return_are_required(actual_windows,flags,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==0x3C3C6 and row['flags']==flags
              and row['status']==0x7F and row['variant']==0 and row['sr']==0)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    call=result['calls'][0]
    if fault.startswith('call-'):
        key={'call-site':'site','call-target':'target','call-return':'return_address','call-sp':'sp'}[fault]
        call[key]+=4 if key=='sp' else 2
    elif fault=='delay-index':
        registers=list(call['entry']['registers']);registers[4]^=1;call['entry']['registers']=tuple(registers)
    elif fault.startswith('entry-'):call['entry'][fault[6:]]^=1
    elif fault=='extra-call':result['calls'].append(deepcopy(call))
    elif fault=='observing-return':
        [row for row in result['branches'] if row['kind']=='return'][-1]['target']+=2
    elif fault=='register-output':
        registers=list(result['registers']);registers[0]^=1;result['registers']=tuple(registers)
    else:
        read=next(row for row in result['accesses'] if row['domain']=='ram' and row['address']==0x01002449 and row['mode']=='read')
        store=next(row for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write')
        if fault=='omit-read':result['accesses'].remove(read)
        elif fault=='omit-write':result['accesses'].remove(store)
        elif fault=='extra-write':result['accesses'].append(deepcopy(store))
        elif fault=='rmw-site':store['site']=0x3C3D8 if store['site']==0x3C3D6 else 0x3C3D6
        elif fault=='rmw-width':store['width_bytes']=2
        elif fault=='rmw-address':store['address']+=1
        else:store['bytes']=bytes([int(store['bytes'],16)^1]).hex()
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


def test_actual_sentinel_has_no_fabricated_record_read(actual_windows):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['argument']==0xFFFFFFFF)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    assert not any(row['domain']=='ram' for row in result['accesses'])
    result['accesses'].append(dict(site=0x25E32,mode='read',address=0x01005A94,
                                   width_bytes=1,bytes=bytes([case['flags']]).hex(),domain='ram'))
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('field',('address','bytes','source_sha256','object_sha256','elf_sha256'))
def test_independently_assembled_record_boundary_is_required(original,field):
    packet=deepcopy(original[2]);row=packet['boundaries'][0]
    if field=='address':row[field]+=2
    elif field=='bytes':row[field]='000b0009'
    else:row.pop(field)
    refuse(original,packet)
