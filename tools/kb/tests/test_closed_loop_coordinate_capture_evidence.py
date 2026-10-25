"""Actual complete admission observations reject changed pointers, fields and state."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import closed_loop_coordinate_contract as contract,closed_loop_coordinate_capture_evidence as proof
from kb import closed_loop_coordinate_semantics as scalar


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['closed_loop_coordinate_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original closed-loop coordinate decoder capture')
        pytest.skip('the complete original closed-loop coordinate decoder capture is unavailable')
    model=compile.build(repo.ROOT);proof.require_primary(model,record)
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):
        proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def test_missing_original_admission_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('closed_loop_coordinate_paths')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_actual_coordinate_component_supplies_the_exact_sample_argument_without_another_capture(original):
    result=proof.require_primary(original[0],original[1])
    assert result['exact_sample_argument'] is result['exact_coordinate_accesses'] is True
    assert result['native_relation_publication'] is result['scale_admission'] is False


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


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_closed_loop_conversion.s',
    'tools/sh-elf-run/harness-closed-loop-admission.c','tools/sh-elf-run/closed_loop_coordinate_capture.py',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s',
    'tools/kb/src/kb/closed_loop_coordinate_contract.py','tools/kb/src/kb/closed_loop_coordinate_capture_evidence.py',
    'tools/kb/src/kb/closed_loop_coordinate_matrix.py','tools/kb/src/kb/closed_loop_coordinate_semantics.py',
    'tools/kb/src/kb/byte_surface_equations.py','tools/kb/src/kb/width_view_matrix.py',
    'tools/sh-elf-run/stock-jk08a-closed-loop-conversion-cases.h'))

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
    wanted=dict(coefficient_override=64,x1=1000,x2=2000,sr=0)
    if kind=='zero':wanted['coefficient_override']=0
    elif kind=='bypass':wanted['speed_min']=6000
    elif kind=='clamp':wanted.update(coefficient_override=1,x1=65535,x2=0)
    elif kind=='fraction':wanted.update(coefficient_override=256,sample=8<<8)
    return next(row for row in declared['cases'] if row['legacy_index']==-1
        and all(row[key]==value for key,value in wanted.items()))


def sample_pair(actual_windows):
    declared,_,_,observations=actual_windows
    wanted=dict(x1=1000,x2=2000,speed=6000,midpoint=880,upper=65024,lower=51264,
        speed_min=5606,coefficient_override=64,root_override=256,variant=0,sr=0)
    return [observations[next(row for row in reversed(declared['cases']) if row['legacy_index']==-1
        and row['sample']==sample and all(row[key]==value for key,value in wanted.items()))['index']]
        for sample in (0,51264)]


def test_actual_sample_argument_changes_admission_and_output_with_every_other_complete_input_fixed(actual_windows):
    pair=sample_pair(actual_windows)
    proof.require_sample_alternatives(pair)
    output=[tuple(int.from_bytes(row['memory_after'][0][at:at+2],'big') for at in (0x8558,0x855A))
        for row in pair]
    assert output==[(1120,3120),(1000,2000)]


@pytest.mark.parametrize('fault',('one-case','same-sample','same-output','other-RAM','native',
    'context','frame','sp','continuation','abi','sr','calibration'))
def test_actual_sample_argument_refuses_nonvarying_output_or_another_changed_input(actual_windows,fault):
    pair=deepcopy(sample_pair(actual_windows));first,second=pair
    if fault=='one-case':pair.pop()
    elif fault in ('same-sample','same-output','other-RAM'):
        key='memory_after' if fault=='same-output' else 'memory_before'
        data=bytearray(second[key][0])
        if fault=='same-sample':data[0x4524:0x4526]=first[key][0][0x4524:0x4526]
        elif fault=='same-output':data[0x8558:0x855C]=first[key][0][0x8558:0x855C]
        else:data[0x4526]^=1
        second[key]=(bytes(data),)
    elif fault in ('context','abi'):
        key='context' if fault=='context' else 'abi_before'
        values=list(second[key]);values[0]^=1;second[key]=tuple(values)
    elif fault in ('native','frame'):
        key='native_before' if fault=='native' else 'frame_before'
        data=bytearray(second[key]);data[0]^=1;second[key]=bytes(data)
    elif fault in ('sp','continuation','sr'):
        key='sr_before' if fault=='sr' else fault;second[key]^=1
    else:
        data=bytearray(second['calibration_before'][0x8F98]);data[0]^=1
        second['calibration_before'][0x8F98]=bytes(data)
    with pytest.raises(ValueError):proof.require_sample_alternatives(pair)


@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','value','helper-direct-read'))
def test_actual_sample_argument_keeps_the_exact_caller_word_read_and_no_substitute_helper_access(actual_windows,fault):
    declared,image,fixture,observations=actual_windows
    case=selected_case(declared,'positive');observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    row=next(row for row in result['accesses'] if row['site']==0x3EE72)
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(deepcopy(row))
    elif fault=='site':row['site']+=2
    elif fault=='address':row['address']+=2
    elif fault=='width':row['width_bytes']=1
    elif fault=='direction':row['mode']='write'
    elif fault=='value':row['bytes']='0000' if row['bytes']!='0000' else 'ffff'
    else:
        added=deepcopy(row);added['site']=0x3EFB8;result['accesses'].append(added)
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('kind',('positive','zero','bypass','clamp','fraction'))
@pytest.mark.parametrize('fault',('x1','x2','speed','sample','coefficient-copy','fifth-copy','output0','output1',
    'other-RAM','raw-native-alias','native-before','native-workspace','native-left-canary','native-right-canary',
    'native-size','gbr','frame-before','frame-after','fifth-frame','abi','sp','pr','sr','macl','R0','continuation',
    'GBR-word','midpoint','coefficient-root','axis'))
def test_actual_complete_native_RAM_input_output_frame_and_calibration_are_required(actual_windows,kind,fault):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,kind)
    observed=deepcopy(observations[case['index']])
    offsets={'x1':0x8554,'speed':0x110A,'sample':0x4524,'coefficient-copy':0x2F8E,'fifth-copy':0x855F,
             'output0':0x8558,'output1':0x855A,'other-RAM':0x2F8F,'raw-native-alias':0x8560}
    if fault in offsets:
        key='memory_before' if fault in ('x1','speed','sample') else 'memory_after'
        data=bytearray(observed[key][0]);data[offsets[fault]]^=1;observed[key]=(bytes(data),)
    elif fault in ('x2','gbr'):
        context=list(observed['context']);context[0 if fault=='x2' else 15]^=1;observed['context']=tuple(context)
    elif fault.startswith('native-'):
        key='native_before' if fault=='native-before' else 'native_after';data=bytearray(observed[key])
        if fault=='native-size':data.pop()
        else:data[{'native-before':0x60,'native-workspace':0x60,'native-left-canary':0x5F,'native-right-canary':0x74}[fault]]^=1
        observed[key]=bytes(data)
    elif fault in ('frame-before','frame-after','fifth-frame'):
        key='frame_before' if fault=='frame-before' else 'frame_after';data=bytearray(observed[key])
        data[160 if fault=='fifth-frame' else 156]^=1;observed[key]=bytes(data)
    elif fault=='abi':
        values=list(observed['abi_after']);values[0]^=1;observed['abi_after']=tuple(values)
    elif fault in ('pr','sr','macl','R0'):
        values=list(observed['exit']);values[{'pr':1,'sr':0,'macl':2,'R0':19}[fault]]^=1;observed['exit']=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:
        at={'GBR-word':0x3F002,'midpoint':0x8F98,'coefficient-root':0x12292,'axis':0x11B47}[fault]
        data=bytearray(observed['calibration_before'][at]);data[0]^=1;observed['calibration_before'][at]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('kind',('positive','zero','bypass','clamp','fraction'))
@pytest.mark.parametrize('fault',('omit','duplicate','root-address','root-site','root-width','root-direction','root-value',
    'copy-address','copy-site','copy-width','copy-value','native-address','native-width','native-value','return-site','return-target'))
def test_actual_exact_root_publication_and_native_transfers_are_required(actual_windows,kind,fault):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,kind)
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    root=next(row for row in result['accesses'] if row['site']==0x264B8)
    copied=next(row for row in result['accesses'] if row['site']==0x3EFB0)
    native=next(row for row in result['accesses'] if row['site']==0x3F110)
    if fault=='omit':result['accesses'].remove(root)
    elif fault=='duplicate':result['accesses'].append(deepcopy(root))
    elif fault.startswith('return-'):
        row=next(row for row in result['branches'] if row['kind']=='return')
        row['site' if fault=='return-site' else 'target']+=2
    else:
        row=root if fault.startswith('root-') else copied if fault.startswith('copy-') else native
        field=fault.split('-',1)[1]
        if field=='address':row['address']+=1
        elif field=='site':row['site']+=2
        elif field=='width':row['width_bytes']=2 if row['width_bytes']==1 else 1
        elif field=='direction':row['mode']='write'
        else:
            data=bytearray.fromhex(row['bytes']);data[0]^=1;row['bytes']=data.hex()
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('fault',('caller-target','caller-return','caller-sp','caller-entry-sp','caller-gbr',
    'caller-speed','caller-sample','caller-input-pointer','caller-output-pointer','curve-table','curve-axis','curve-input',
    'axis-bound','axis-coordinate','signed-divisor','signed-numerator','extra-call','omit-call'))
def test_actual_post_delay_arguments_and_real_call_sequence_are_required(actual_windows,fault):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,'positive')
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    if fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='omit-call':result['calls'].pop()
    elif fault in ('caller-target','caller-return','caller-sp'):
        key={'caller-target':'target','caller-return':'return_address','caller-sp':'sp'}[fault]
        result['calls'][0][key]+=4 if key=='sp' else 2
    elif fault in ('caller-entry-sp','caller-gbr'):
        result['calls'][0]['entry']['sp' if fault=='caller-entry-sp' else 'gbr']^=4
    else:
        if fault.startswith('curve-'):call=next(row for row in result['calls'] if row['site']==0x3EFA6)
        elif fault.startswith('axis-'):call=next(row for row in result['calls'] if row['site']==0x264AA)
        elif fault.startswith('signed-'):call=next(row for row in result['calls'] if row['site']==0x3F090)
        else:call=result['calls'][0]
        register={'caller-speed':5,'caller-sample':6,'caller-input-pointer':4,'caller-output-pointer':7,
            'curve-table':4,'curve-axis':5,'curve-input':6,'axis-bound':4,'axis-coordinate':5,
            'signed-divisor':0,'signed-numerator':1}[fault]
        values=list(call['entry']['registers']);values[register]^=1;call['entry']['registers']=tuple(values)
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('register',(0,1))
def test_actual_axis_fraction_uses_its_natural_unsigned_division_arguments(actual_windows,register):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,'fraction')
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    call=next(row for row in result['calls'] if row['site']==0x2696A)
    values=list(call['entry']['registers']);values[register]^=1;call['entry']['registers']=tuple(values)
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


def test_actual_zero_coefficient_never_fabricates_a_signed_division_or_fault_store(actual_windows):
    declared,image,fixture,observations=actual_windows;case=selected_case(declared,'zero')
    observed=observations[case['index']]
    result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    assert not any(row['target']==0x21BBC for row in result['calls'])
    result['accesses'].append(dict(site=0x21C74,mode='write',domain='ram',address=0x01009818,width_bytes=4,bytes='0000044e'))
    with pytest.raises(ValueError):scalar.evaluate(case,observed,result)


@pytest.mark.parametrize('field',('address','bytes','source_sha256','object_sha256','elf_sha256'))
def test_independently_assembled_coordinate_observing_return_is_required(original,field):
    packet=deepcopy(original[2]);row=packet['boundaries'][0]
    if field=='address':row[field]+=2
    elif field=='bytes':row[field]='000b0009'
    else:row.pop(field)
    refuse(original,packet)


@pytest.mark.parametrize('fault',('missing','larger','other-base'))
def test_actual_native_memory_domain_is_exact(original,fault):
    packet=deepcopy(original[2]);command=packet['simulator']['command']
    if fault=='missing':command.pop(2)
    elif fault=='larger':command[2]='--memory-region=0xffff8500,512'
    else:command[2]='--memory-region=0xffff8400,256'
    refuse(original,packet)
