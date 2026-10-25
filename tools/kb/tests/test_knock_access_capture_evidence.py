"""Actual four-stage knock originals reject substituted inputs, state and paths."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import knock_access_unit_contract as contract,knock_access_capture_evidence as proof
from kb import knock_access_matrix as matrix,knock_access_transfers as physical


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['knock_accesses']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires all four original knock stages')
        pytest.skip('the complete original knock capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('kind',matrix.KINDS)
def test_each_separate_original_stage_is_required(original,kind):
    packet=deepcopy(original[2]);packet['units'].pop(kind);refuse(original,packet)


@pytest.mark.parametrize('kind',matrix.KINDS)
@pytest.mark.parametrize('fault',('schema','declaration','consumed','reconstruction','aliases','boundaries','observations','simulator','toolchain'))
def test_each_original_stage_keeps_its_complete_physical_packet(original,kind,fault):
    packet=deepcopy(original[2]);packet['units'][kind].pop(fault);refuse(original,packet)


@pytest.mark.parametrize('kind',matrix.KINDS)
@pytest.mark.parametrize('fault',('code','pool','alias','boundary','returncode','timeout','compiler','simulator','private','fixture'))
def test_changed_actual_stock_bytes_fixture_inputs_or_terminal_refuse(original,kind,fault):
    packet=deepcopy(original[2]);unit=packet['units'][kind]
    if fault=='code':unit['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':unit['reconstruction']['pools'][0]['stock']='00'
    elif fault=='alias':unit['aliases'][0]['alias']+=4
    elif fault=='boundary':unit['boundaries'].append(dict(address=0x49D88,bytes='000b0009'))
    elif fault=='returncode':unit['simulator']['returncode']=1
    elif fault=='timeout':unit['simulator']['timeout_seconds']=0
    elif fault=='compiler':unit['command'][0]='another-gcc'
    elif fault=='simulator':unit['simulator']['command'][0]='another-run'
    elif fault=='private':unit['consumed'][proof.OBSERVER]+='00'
    else:unit['fixture_sha256']='0'*64
    refuse(original,packet)


def rewrite(unit):
    rows=iter(unit['observations']);lines=[]
    for line in unit['stdout'].splitlines(keepends=True):
        if line.startswith(proof.PREFIX):
            row=next(rows,None)
            if row is not None:lines.append(proof.PREFIX+json.dumps(row,separators=(',',':'))+'\n')
        else:lines.append(line)
    unit['stdout']=''.join(lines);unit['stdout_sha256']=hashlib.sha256(unit['stdout'].encode()).hexdigest()


@pytest.mark.parametrize('kind',matrix.KINDS)
@pytest.mark.parametrize('fault',('omit','duplicate','swap','entry','role','index','stream','const-context','duplicate-json-key'))
def test_changed_actual_invocations_refuse_with_consistent_original_stream_hash(original,kind,fault):
    packet=deepcopy(original[2]);unit=packet['units'][kind];rows=unit['observations']
    if fault=='omit':rows.pop()
    elif fault=='duplicate':rows[-1]=deepcopy(rows[0])
    elif fault=='swap':rows[0],rows[-1]=rows[-1],rows[0]
    elif fault=='entry':rows[0]['entry']+=2
    elif fault=='role':rows[0]['kind']^=1
    elif fault=='index':rows[0]['index']=True
    elif fault=='stream':
        data=bytearray.fromhex(rows[0]['observation']);data[0]^=1;rows[0]['observation']=data.hex()
    elif fault=='const-context':
        data=bytearray.fromhex(rows[0]['context_after']);data[0]^=1;rows[0]['context_after']=data.hex()
    rewrite(unit)
    if fault=='duplicate-json-key':
        unit['stdout']=unit['stdout'].replace(proof.PREFIX+'{',proof.PREFIX+'{"schema":1,',1)
        unit['stdout_sha256']=hashlib.sha256(unit['stdout'].encode()).hexdigest()
    refuse(original,packet)


@pytest.mark.parametrize('source',(
    contract.DESCRIPTOR,'defs/JK08A.knock-access-claims.toml',*matrix.INPUT_SOURCES,
    *('tools/sh-elf-run/'+name for kind in matrix.KINDS for name in proof.sources(kind)),
    'tools/sh-elf-run/harness-knock-accesses.c','tools/sh-elf-run/knock_access_capture.py',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/kb/src/kb/knock_access_unit_contract.py','tools/kb/src/kb/knock_access_matrix.py',
    'tools/kb/src/kb/knock_access_semantics.py','tools/kb/src/kb/knock_access_transfers.py',
    'tools/kb/src/kb/knock_access_capture_evidence.py','tools/kb/src/kb/knock_access_contract.py',
    'tools/kb/src/kb/knock_access_evidence.py','tools/kb/src/kb/knock_access_resolution.py',
    'tools/kb/tests/knock_software_contract.py','tools/kb/tests/test_knock_threshold_chain.py',
    'tools/kb/tests/test_knock_comparison_chain.py','tools/kb/src/kb/byte_surface_equations.py'))
def test_each_actual_consumed_producer_or_independent_source_is_bound(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def actual_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();result={}
    for kind in matrix.KINDS:
        packet=original[2]['units'][kind];declared=packet['declaration']
        fixture,_=contract.independent_fixture(declared['source'],image)
        result[kind]=(declared,image,fixture,proof.observations(packet,declared))
    return result


def selected_case(declared):
    kind=declared['kind']
    if kind=='normalization':
        return next(case for case in declared['cases'] if case['channel']==1 and case['blocks']
            and len(set(case['bins']))>1 and case['flag']==0 and case['selector']==0x82)
    if kind=='metric':return next(case for case in declared['cases'] if case['scope']==0 and case['channel']==1 and case['mask']==0)
    return next(case for case in declared['cases'] if case['channel']==1 and case['speed']==33 and case['table_override'])


@pytest.mark.parametrize('kind',matrix.KINDS)
@pytest.mark.parametrize('fault',('input','output','sibling','outside','register','fifth','frame','entry-frame',
    'abi','sp','continuation','exit','pr','calibration','prepared-sr'))
def test_each_actual_stage_refuses_changed_complete_input_and_machine_state(actual_windows,kind,fault):
    declared,image,fixture,observations=actual_windows[kind];case=selected_case(declared)
    observed=deepcopy(observations[case['index']])
    if fault in ('input','output','sibling','outside'):
        key='memory_before' if fault=='input' else 'memory_after'
        at={'normalization':{'input':0x2132,'output':0x20D2,'sibling':0x20E2},
            'metric':{'input':0x20C2,'output':0x21D8,'sibling':0x21DC},
            'threshold':{'input':0x11F4,'output':0x2144,'sibling':0x2146},
            'comparison':{'input':0x21D8,'output':0x2144,'sibling':0x2146}}[kind].get(fault,0x1234)
        memory=bytearray(observed[key][0]);memory[at]^=1;observed[key]=(bytes(memory),)
    elif fault in ('register','fifth'):
        context=list(observed['context']);context[19 if fault=='fifth' else 4]^=1;observed['context']=tuple(context)
    elif fault in ('frame','entry-frame'):
        key='frame_before' if fault=='entry-frame' else 'frame_after'
        frame=bytearray(observed[key]);frame[160]^=1;observed[key]=bytes(frame)
    elif fault in ('abi','exit','pr'):
        key='abi_after' if fault=='abi' else 'exit';values=list(observed[key]);values[1 if fault=='pr' else 0]^=1
        observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    elif fault=='prepared-sr':observed['sr_before']^=0x100
    else:
        at=next(iter(observed['calibration_before']));raw=bytearray(observed['calibration_before'][at]);raw[0]^=1
        observed['calibration_before'][at]=bytes(raw)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('kind',matrix.KINDS)
@pytest.mark.parametrize('fault',('site','width','direction','address','bytes','missing-call','extra-call','call-order','call-argument'))
def test_exact_datum_transfers_and_real_post_delay_call_closure_are_required(actual_windows,kind,fault):
    declared,image,fixture,observations=actual_windows[kind];case=selected_case(declared)
    observed=observations[case['index']];result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    if fault=='missing-call':result['calls'].pop(0)
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='call-order':result['calls'][0],result['calls'][1]=result['calls'][1],result['calls'][0]
    elif fault=='call-argument':
        target,index=(0x21CE0,0) if kind=='normalization' else (0x221BC,1) if kind=='metric' else (0x26984,4)
        call=next(row for row in result['calls'] if row['target']==target)
        registers=list(call['entry']['registers']);registers[index]^=1;call['entry']['registers']=registers
    else:
        site,address=(0x4A58C,0x010020D2) if kind=='normalization' else (
            (0x49F4C,0x010021D8) if kind=='metric' else (0x26510,0x1108E))
        row=next(row for row in result['accesses'] if row['site']==site and row['address']==address)
        if fault=='site':row['site']+=2
        elif fault=='width':row['width_bytes']=1
        elif fault=='direction':row['mode']='read' if row['mode']=='write' else 'write'
        elif fault=='address':row['address']+=2
        else:row['bytes']='0000' if row['bytes']!='0000' else '0001'
    with pytest.raises(ValueError):physical.evaluate(case,observed,result)


def test_positive_alternatives_require_input_and_output_variation_with_identical_held_inputs():
    with pytest.raises(ValueError):proof.require_positive({'fixed':{('0001',(1,)),('0002',(1,))}},'fixed output')
    with pytest.raises(ValueError):proof.require_positive({'a':{('0001',(1,))},'b':{('0002',(2,))}},'changed held inputs')
    proof.require_positive({'fixed':{('0001',(1,)),('0002',(2,))}},'exact positive alternatives')
