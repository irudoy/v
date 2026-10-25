"""Actual whole-feedback originals reject changed physical, argument and state evidence."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import closed_loop_feedback_access_contract as contract,closed_loop_feedback_matrix as matrix
from kb import closed_loop_feedback_capture_evidence as proof,closed_loop_feedback_transfers as transfers


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['closed_loop_feedback_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original whole-feedback capture')
        pytest.skip('the complete original whole-feedback capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_feedback_arguments'] is result['exact_feedback_stores'] is result['exact_transition_counter_accesses'] is True
    assert result['transition_saturation_guard_outcomes']==['taken']
    assert all(values==['fallthrough','taken'] for values in result['conditional_branch_outcomes'].values())
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)==27
    for flag in ('physical_callee_reader_inference','native_geometry_inference','automatic_resolution',
            'scale_admission','units_admission','natural_scheduling_inference','hardware_qualification'):
        assert result[flag] is False
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


def restream(packet):
    rows=iter(packet['observations']);lines=[]
    for line in packet['stdout'].splitlines(keepends=True):
        if line.startswith(proof.PREFIX):
            row=next(rows,None)
            if row is not None:lines.append(proof.PREFIX+json.dumps(row,separators=(',',':'))+'\n')
        else:lines.append(line)
    packet['stdout']=''.join(lines);packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()


@pytest.mark.parametrize('field',('schema','declaration','consumed','reconstruction','aliases','observations',
    'simulator','toolchain','command','marker','stdout_sha256','observer_object_sha256'))
def test_actual_complete_original_requires_every_physical_capture_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','word-alias','long-alias','returncode','timeout','compiler',
    'simulator','observer','header','omit','duplicate','swap','kind','entry','context-after'))
def test_actual_source_reconstruction_alias_toolchain_and_complete_invocations_refuse_changes(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'][0]['stock']+='00'
    elif fault in ('word-alias','long-alias'):
        width=2 if fault=='word-alias' else 4
        next(row for row in packet['aliases'] if row['width']==width)['alias']+=4
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=1
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    elif fault=='observer':packet['consumed'][proof.OBSERVER]+='00'
    elif fault=='header':packet['consumed'][proof.HEADER]+='00'
    else:
        rows=packet['observations']
        if fault=='omit':rows.pop()
        elif fault=='duplicate':rows[-1]=deepcopy(rows[0])
        elif fault=='swap':rows[0],rows[-1]=rows[-1],rows[0]
        elif fault=='kind':rows[0]['kind']=True
        elif fault=='entry':rows[0]['entry']+=2
        else:rows[0]['context_after']='00'+rows[0]['context_after'][2:]
        restream(packet)
    refuse(original,packet)


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/stock_jk08a_closed_loop_feedback.s',
    'tools/sh-elf-run/invoke-closed-loop-feedback.s','tools/sh-elf-run/harness-closed-loop-feedback-paths.c',
    matrix.INPUT_SOURCE))
def test_actual_producer_and_independent_consumer_sources_are_bound_to_the_original(original,path):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[path]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    observations=proof.observations(original[2],declared)
    reference=next(row for row in declared['cases'] if row['kind']=='controlled' and row['profile']=='argument-contrast'
        and matrix.memory(row)[0x106E]==40 and matrix.memory(row)[0x1071]==60
        and int.from_bytes(matrix.memory(row)[0x11BC:0x11BE],'big')==3 and matrix.memory(row)[0x10C8]==3)
    saved=matrix.memory(reference);selected={}
    for name,profile,changes in (('normal','argument-contrast',{}),('coordinate-low','argument-contrast',{0x106E:b'\0'}),
            ('coordinate-high','argument-contrast',{0x106E:b'\xff'}),('reverse','argument-reverse',{}),
            ('rpm-zero','argument-contrast',{0x11BC:b'\0\0'}),('speed-low','argument-contrast',{0x1071:b'\0'}),
            ('speed-high','argument-contrast',{0x1071:b'\xff'}),('bank-zero','argument-contrast',{0x10C8:b'\0'}),
            ('bank-one','argument-contrast',{0x10C8:b'\1'})):
        wanted=bytearray(saved)
        for at,data in changes.items():wanted[at:at+len(data)]=data
        case=next(row for row in declared['cases'] if row['kind']=='controlled' and row['profile']==profile and matrix.memory(row)==bytes(wanted))
        observed=observations[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        selected[name]=(case,observed,result,value)
    return declared,image,selected


@pytest.mark.parametrize('name',('normal','coordinate-low','coordinate-high','reverse','rpm-zero','speed-high','bank-zero'))
@pytest.mark.parametrize('fault',('source106E','source1071','RPM','first-store','second-store','other-RAM',
    'native-before','native-after','low-canary','high-canary','unaliased-workspace','bound-before','bound-after',
    'calibration-before','calibration-after','frame-before','frame-after','context','ABI','SP','continuation',
    'R0','R5','R7','R9','R14','PR','GBR','MACH','MACL','SR'))
def test_actual_complete_inputs_state_frame_workspace_canaries_bound_bytes_and_terminal_are_required(windows,name,fault):
    declared,image,selected=windows;case,saved,_,_=selected[name];observed=deepcopy(saved)
    if fault in ('source106E','source1071','RPM','first-store','second-store','other-RAM','unaliased-workspace'):
        offset={'source106E':0x106E,'source1071':0x1071,'RPM':0x11BC,'first-store':0x895C,
            'second-store':0x8960,'other-RAM':0x8968,'unaliased-workspace':0x88B0}[fault]
        phase='memory_before' if fault in ('source106E','source1071','RPM') else 'memory_after'
        data=bytearray(observed[phase][0]);data[offset]^=1;observed[phase]=(bytes(data),)
    elif fault in ('native-before','native-after','low-canary','high-canary'):
        phase='workspace_before' if fault=='native-before' else 'workspace_after'
        data=bytearray(observed[phase]);data[0 if fault=='low-canary' else 365 if fault=='high-canary' else 32]^=1
        observed[phase]=bytes(data)
    elif fault in ('bound-before','bound-after','frame-before','frame-after'):
        phase=fault.replace('-','_');data=bytearray(observed[phase]);data[0]^=1;observed[phase]=bytes(data)
    elif fault in ('calibration-before','calibration-after'):
        phase=fault.replace('-','_');data=bytearray(observed[phase][0x12312]);data[0]^=1
        observed[phase][0x12312]=bytes(data)
    elif fault in ('context','ABI'):
        phase='context' if fault=='context' else 'abi_after';data=list(observed[phase]);data[0]^=1;observed[phase]=tuple(data)
    elif fault in ('SP','continuation'):observed['sp' if fault=='SP' else fault]^=4
    else:
        field={'R0':19,'R5':14,'R7':12,'R9':10,'R14':5,'PR':1,'GBR':4,'MACH':3,'MACL':2,'SR':0}[fault]
        data=list(observed['exit']);data[field]^=1;observed['exit']=tuple(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,case,observed,repo.ROOT)


@pytest.mark.parametrize('site,mode',((0x5CEDA,'read'),(0x5CEE6,'read'),(0x5CEF2,'read'),
    (0x5CEE0,'write'),(0x5D6D2,'read'),(0x5CEF4,'write'),(0x5D844,'read'),(0x5D846,'write'),(0x5D84E,'write')))
@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','bytes','domain','order'))
def test_actual_physical_caller_arguments_partial_stores_pointer_and_both_outputs_are_exact(windows,site,mode,fault):
    *_,selected=windows;_,observed,saved,value=selected['normal'];result=deepcopy(saved)
    row=next(row for row in result['accesses'] if row['site']==site and row['mode']==mode)
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(deepcopy(row))
    elif fault=='site':row['site']+=2
    elif fault=='address':row['address']+=1
    elif fault=='width':row['width_bytes']=4 if row['width_bytes']!=4 else 2
    elif fault=='direction':row['mode']='write' if mode=='read' else 'read'
    elif fault=='bytes':
        data=bytearray.fromhex(row['bytes']);data[-1]^=1;row['bytes']=data.hex()
    elif fault=='domain':row['domain']='rom'
    else:
        positions=[i for i,item in enumerate(result['accesses']) if item['site'] in (0x5CEDA,0x5D84E)]
        left,right=positions[0],positions[-1];result['accesses'][left],result['accesses'][right]=result['accesses'][right],result['accesses'][left]
    trace=dict(active_state=dict(before=value['scalar_before'],after=value['scalar_after'],
        args=(int(bool(observed['memory_before'][0][0x4184]&64)),observed['memory_before'][0][0x1071],
            [value['scalar_before'][0x8937],value['scalar_before'][0x8938]],
            int.from_bytes(observed['memory_before'][0][0x11BC:0x11BE],'big'),observed['memory_before'][0][0x106E])))
    with pytest.raises(ValueError):transfers.require(observed,result,trace)


@pytest.mark.parametrize('fault',('site','target','return','SP','entry-SP','entry-PR','entry-GBR',
    'R4','R5','R6','R7','R9','omit','duplicate','return-site','return-target'))
def test_actual_feedback_call_requires_the_complete_signed_post_delay_arguments_and_natural_return(windows,fault):
    declared,image,selected=windows;case,observed,saved,value=selected['normal'];result=deepcopy(saved)
    call=next(row for row in result['calls'] if row['target']==transfers.TARGET)
    if fault in ('site','target','return','SP'):call[{'return':'return_address','SP':'sp'}.get(fault,fault)]^=4
    elif fault.startswith('entry-'):call['entry'][{'SP':'sp','PR':'pr','GBR':'gbr'}[fault[6:]]]^=4
    elif fault.startswith('R') and fault[1:].isdigit():
        registers=list(call['entry']['registers']);registers[int(fault[1:])]^=0x80000000;call['entry']['registers']=tuple(registers)
    elif fault=='omit':result['calls'].remove(call)
    elif fault=='duplicate':result['calls'].append(deepcopy(call))
    else:
        row=next(row for row in result['branches'] if row['site']==0x5D868)
        row['site' if fault=='return-site' else 'target']+=2
    from tools.kb.tests import closed_loop_feedback_frame as frame
    fixture,_=contract.fixture_for_case(declared['source'],image,case,repo.ROOT)
    _,trace=frame.semantic_trace(matrix.logical_ram(observed['memory_before'][0],observed['workspace_before']),fixture)
    with pytest.raises(ValueError):transfers.require(observed,result,trace)


@pytest.fixture(scope='module')
def counter_windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    observations=proof.observations(original[2],declared);selected={}
    threshold=image[0x8822]*image[0x23752]
    lower=(5000-int.from_bytes(image[0x92EE:0x92F0],'big'))&65535
    upper=(5000+int.from_bytes(image[0x92F0:0x92F2],'big'))&65535
    for name,count,flag,observed_word,previous in (
            ('inactive',0,0,0,0),('increment',0,1,0,0),('armed',0,0,0,1),
            ('threshold',threshold,1,0,0),('over-threshold',threshold+1,1,0,0),
            ('lower',0,1,lower,0),('upper',0,1,upper,0),
            ('below',0,1,(lower-1)&65535,0),('above',0,1,(upper+1)&65535,0),
            ('maximum',65535,1,0,0)):
        def matches(row):
            memory=matrix.memory(row)
            return (row['kind']=='controlled' and row['profile']=='stock'
                and memory[0x11BC:0x11BE]==b'\0\0'
                and int.from_bytes(memory[0x28BA:0x28BC],'big')==5000
                and int.from_bytes(memory[0x29E4:0x29E6],'big')==observed_word
                and int.from_bytes(memory[0x88BA:0x88BC],'big')==count
                and memory[0x88C1]==flag and memory[0x88CD]==previous)
        case=next(row for row in declared['cases'] if matches(row));observed=observations[case['index']]
        result,values=proof.require_state(declared,image,case,observed,repo.ROOT)
        fixture,_=contract.fixture_for_case(declared['source'],image,case,repo.ROOT)
        trace=dict(transition=dict(before=values['transition_before'],after=values['transition_after']))
        selected[name]=(case,observed,result,values,fixture,trace)
    return selected


def test_actual_counter_uses_its_transition_phase_and_inclusive_band_threshold_and_unsigned_word(counter_windows):
    for name,(_,_,_,values,_,_) in counter_windows.items():
        increment=name in ('increment','armed','threshold','below','above')
        assert values['transition_increment'] is increment
        assert values['transition_count_after']==(values['transition_count_before']+1 if increment else 0)
        assert values['transition_flag_after']==int(increment)
        assert values['transition_guard_observed'] is increment
    for name in ('lower','upper'):assert counter_windows[name][3]['transition_inside_band'] is True
    assert counter_windows['maximum'][3]['transition_count_before']==65535


@pytest.mark.parametrize('name,site,mode,address',(
    ('increment',0x5CAD4,'read',0x600D),('increment',0x5CB12,'read',0x600D),
    ('armed',0x5CB1E,'write',0x600D),('increment',0x5CB30,'read',0x6006),
    ('increment',0x5CB7A,'read',0x6006),('increment',0x5CB9C,'read',0x6006),
    ('increment',0x5CBAA,'write',0x6006),('inactive',0x5CBB4,'write',0x600D),
    ('inactive',0x5CBBC,'write',0x6006),('increment',0x5D698,'write',0x6122),
    ('increment',0x5D6A4,'write',0x60A5)))
@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','bytes','domain','order'))
def test_actual_transition_bank2_counter_flag_delay_and_packet_output_are_exact(counter_windows,name,site,mode,address,fault):
    _,observed,saved,_,fixture,trace=counter_windows[name];result=deepcopy(saved)
    row=next(row for row in result['accesses'] if (row['site'],row['mode'],row['address'])==(site,mode,address))
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(deepcopy(row))
    elif fault=='site':row['site']+=2
    elif fault=='address':row['address']+=1
    elif fault=='width':row['width_bytes']=4
    elif fault=='direction':row['mode']='read' if mode=='write' else 'write'
    elif fault=='bytes':
        data=bytearray.fromhex(row['bytes']);data[-1]^=1;row['bytes']=data.hex()
    elif fault=='domain':row['domain']='ram'
    else:
        index=result['accesses'].index(row);result['accesses'].insert(0,result['accesses'].pop(index))
    with pytest.raises(ValueError):transfers.require_transition(observed,result,trace,fixture)


@pytest.mark.parametrize('site,mode',((0x5CC2C,'write'),(0x5D684,'read'),(0x5CC36,'write'),
    (0x5D68E,'read'),(0x5CC42,'write'),(0x5D69C,'read')))
@pytest.mark.parametrize('fault',('omit','duplicate','address','width','bytes','domain'))
def test_actual_transition_packet_nominal_observed_and_output_pointer_carriers_are_complete(counter_windows,site,mode,fault):
    _,observed,saved,_,fixture,trace=counter_windows['increment'];result=deepcopy(saved)
    row=next(row for row in result['accesses'] if row['site']==site and row['mode']==mode)
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(deepcopy(row))
    elif fault=='address':row['address']+=4
    elif fault=='width':row['width_bytes']=2
    elif fault=='domain':row['domain']='ram'
    else:
        data=bytearray.fromhex(row['bytes']);data[-1]^=1;row['bytes']=data.hex()
    with pytest.raises(ValueError):transfers.require_transition(observed,result,trace,fixture)


@pytest.mark.parametrize('target',(0x5D66C,0x5CA8C))
@pytest.mark.parametrize('fault',('omit','duplicate','site','target','return_address','sp',
    'entry-sp','entry-pr','entry-gbr','R4','R5','R6','R7','order'))
def test_actual_transition_real_calls_require_complete_packet_and_callee_post_delay_state(counter_windows,target,fault):
    _,observed,saved,_,fixture,trace=counter_windows['increment'];result=deepcopy(saved)
    row=next(row for row in result['calls'] if row['target']==target)
    if fault=='omit':result['calls'].remove(row)
    elif fault=='duplicate':result['calls'].append(deepcopy(row))
    elif fault in ('site','target','return_address','sp'):row[fault]^=4
    elif fault.startswith('entry-'):row['entry'][fault[6:]]^=4
    elif fault.startswith('R'):
        registers=list(row['entry']['registers']);registers[int(fault[1:])]^=0x80000000;row['entry']['registers']=tuple(registers)
    else:result['calls'].reverse()
    with pytest.raises(ValueError):transfers.require_transition(observed,result,trace,fixture)


@pytest.mark.parametrize('site',(0x5CBE4,0x5D6AA))
@pytest.mark.parametrize('fault',('omit','duplicate','site','kind','target'))
def test_actual_transition_both_natural_returns_are_exact(counter_windows,site,fault):
    _,observed,saved,_,fixture,trace=counter_windows['increment'];result=deepcopy(saved)
    row=next(row for row in result['branches'] if row['site']==site)
    if fault=='omit':result['branches'].remove(row)
    elif fault=='duplicate':result['branches'].append(deepcopy(row))
    elif fault=='kind':row['kind']='taken'
    else:row[fault]+=2
    with pytest.raises(ValueError):transfers.require_transition(observed,result,trace,fixture)


@pytest.mark.parametrize('fault',('fallthrough','saturation-code','before-counter','after-counter','before-flag',
    'after-flag','initial-seed-phase','callee-R0','callee-R3'))
def test_actual_transition_refuses_saturation_escape_wrong_phase_and_separate_counter_flag_equations(counter_windows,fault):
    _,observed,saved,_,fixture,saved_trace=counter_windows['increment'];result=deepcopy(saved);trace=deepcopy(saved_trace)
    if fault=='fallthrough':
        next(row for row in result['branches'] if row['site']==0x5CB84)['kind']='fallthrough'
    elif fault=='saturation-code':result['code'][0x5CB86]='0009'
    elif fault=='initial-seed-phase':trace['transition']['before']=observed['memory_before'][0]
    elif fault.startswith('callee-'):
        row=next(row for row in result['calls'] if row['target']==0x5CA8C)
        registers=list(row['entry']['registers']);registers[int(fault[-1])]^=1;row['entry']['registers']=tuple(registers)
    else:
        phase,datum=fault.split('-');memory=bytearray(trace['transition'][phase]);memory[0x88BB if datum=='counter' else 0x88C1]^=1
        trace['transition'][phase]=bytes(memory)
    with pytest.raises(ValueError):transfers.require_transition(observed,result,trace,fixture)
