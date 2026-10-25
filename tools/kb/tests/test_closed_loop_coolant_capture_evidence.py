"""Actual coolant originals reject changed complete state and selected-operand evidence."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import closed_loop_coolant_access_contract as contract,closed_loop_coolant_matrix as matrix
from kb import closed_loop_coolant_capture_evidence as proof,closed_loop_coolant_semantics as semantics


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['closed_loop_coolant_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original coolant capture')
        pytest.skip('the complete original coolant capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_coolant_accesses'] is result['exact_selected_coefficient'] is result['exact_signed_offset'] is True
    assert result['selected_coefficient_indices']==list(range(16))
    assert result['byte_entry_guard_outcomes']==['taken']
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)==25
    assert all(outcomes==['fallthrough','taken'] for outcomes in result['conditional_branch_outcomes'].values())
    for flag in ('native_geometry_inference','automatic_resolution','scale_admission','units_admission',
            'natural_caller_reachability','hardware_qualification'):assert result[flag] is False
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('path',('tools/kb/src/kb/proof_sources.py','tools/kb/src/kb/proof_reuse.py'))
def test_actual_coolant_consumer_requires_transitive_source_binding_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError,match='dependency'):
        proof.require_witness(original[0],original[2],inputs)


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
def test_actual_complete_coolant_original_requires_every_raw_capture_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','observer',
    'header','omit','duplicate','swap','kind','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after'))
def test_actual_coolant_source_toolchain_stream_and_complete_bound_snapshots_are_exact(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'][0]['stock']+='00'
    elif fault=='alias':packet['aliases'][0]['alias']+=4
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
        else:
            field=fault.replace('-','_');data=bytearray.fromhex(rows[0][field]);data[0]^=1;rows[0][field]=data.hex()
        restream(packet)
    refuse(original,packet)


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/closed_loop_coolant_capture.py',
    'tools/sh-elf-run/stock_jk08a_coolant_conditional.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-closed-loop-coolant-paths.c',matrix.INPUT_SOURCE))
def test_actual_coolant_producer_consumer_and_numerical_sources_match_the_original_snapshot(original,path):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[path]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    observations=proof.observations(original[2],declared);selected={}
    for name in ('normal','coefficient-high','offset-low','offset-high','limiter-up','limiter-down','disabled'):
        def matches(row):
            if name in ('normal','coefficient-high'):return (row['kind']=='controlled' and row['load']==row['rpm_select']==0
                and row['curve']==[255]*8 and row['coefficients']==[1 if name=='normal' else 64,*([64]*15)]
                and row['cap']==65535)
            if name.startswith('offset-'):return (row['kind']=='controlled' and row['previous_coolant']==240
                and row['coolant_offset']==(0xFF40 if name=='offset-low' else 0xFF48)
                and row['coefficients']==[64]*16 and row['curve']==matrix.DEFAULTS['curve'])
            if name=='disabled':return row['kind']=='legacy' and row['source_flag']==32
            return (row['kind']=='legacy' and row['flags_a']==1 and row['coefficients']==[255]*16
                and row['curve']==[255]*8 and row['rate']==5 and row['old']==(0 if name=='limiter-up' else 65535))
        case=next(row for row in declared['cases'] if matches(row));observed=observations[case['index']]
        result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        numerical=semantics.numerical(repo.ROOT,case)
        selected[name]=(case,observed,result,value,numerical)
    return declared,image,selected


def test_actual_index_zero_and_signed_offset_pairs_change_the_derived_word_with_all_other_inputs_fixed(windows):
    declared,_,selected=windows
    proof.require_positive_alternatives([value[1] for value in selected.values()],
        [value[3] for value in selected.values()],declared)
    assert selected['normal'][3]['selected_index']==selected['coefficient-high'][3]['selected_index']==0
    assert selected['normal'][3]['output']!=selected['coefficient-high'][3]['output']
    assert selected['offset-low'][3]['output']!=selected['offset-high'][3]['output']


@pytest.mark.parametrize('name',('normal','offset-low','offset-high','limiter-up','limiter-down','disabled'))
@pytest.mark.parametrize('fault',('RAM-before','RAM-after','frame-before','frame-after','bound-before','bound-after',
    'calibration-before','calibration-after','context','ABI','SP','continuation','R0','R1','R5','R10','R14',
    'PR','GBR','MACH','MACL','SR'))
def test_actual_coolant_requires_complete_inputs_outputs_frames_bound_bytes_and_full_terminal(windows,name,fault):
    declared,image,selected=windows;case,saved,_,_,_=selected[name];observed=deepcopy(saved)
    if fault.startswith('RAM-'):
        field='memory_before' if fault=='RAM-before' else 'memory_after'
        data=bytearray(observed[field][0]);data[0x15DA]^=1;observed[field]=(bytes(data),)
    elif fault in ('frame-before','frame-after','bound-before','bound-after'):
        field=fault.replace('-','_');data=bytearray(observed[field]);data[0]^=1;observed[field]=bytes(data)
    elif fault in ('calibration-before','calibration-after'):
        field=fault.replace('-','_');data=bytearray(observed[field][0x990A]);data[0]^=1;observed[field][0x990A]=bytes(data)
    elif fault in ('context','ABI'):
        field='context' if fault=='context' else 'abi_after';data=list(observed[field]);data[0]^=1;observed[field]=tuple(data)
    elif fault in ('SP','continuation'):observed['sp' if fault=='SP' else fault]^=4
    else:
        field={'R0':19,'R1':18,'R5':14,'R10':9,'R14':5,'PR':1,'GBR':4,'MACH':3,'MACL':2,'SR':0}[fault]
        data=list(observed['exit']);data[field]^=1;observed['exit']=tuple(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,case,observed,repo.ROOT)


@pytest.mark.parametrize('site',sorted(semantics.WATCHED))
@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','bytes','domain','order'))
def test_actual_selected_byte_signed_word_axes_curve_limiter_and_publication_transfers_are_exact(windows,site,fault):
    _,_,selected=windows
    chosen=next(value for value in selected.values() if any(row['site']==site for row in value[2]['accesses']))
    case,observed,saved,_,numerical=chosen;result=deepcopy(saved)
    row=next(row for row in result['accesses'] if row['site']==site)
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(deepcopy(row))
    elif fault=='site':row['site']+=2
    elif fault=='address':row['address']+=1
    elif fault=='width':row['width_bytes']=4
    elif fault=='direction':row['mode']='write' if row['mode']=='read' else 'read'
    elif fault=='bytes':
        data=bytearray.fromhex(row['bytes']);data[-1]^=1;row['bytes']=data.hex()
    elif fault=='domain':row['domain']='frame'
    else:
        at=result['accesses'].index(row)
        other=next(index for index,value in enumerate(result['accesses']) if value['site'] in semantics.WATCHED and index!=at)
        result['accesses'][at],result['accesses'][other]=result['accesses'][other],result['accesses'][at]
    with pytest.raises(ValueError):semantics.physical(case,observed,result,numerical)


@pytest.mark.parametrize('target',(0x26370,0x22590))
@pytest.mark.parametrize('fault',('omit','duplicate','site','target','return_address','sp','entry-sp','entry-pr',
    'entry-gbr','R4','R5','R12','order'))
def test_actual_curve_and_absolute_calls_require_real_post_delay_state_and_call_order(windows,target,fault):
    _,_,selected=windows;case,observed,saved,_,numerical=selected['limiter-up'];result=deepcopy(saved)
    row=next(row for row in result['calls'] if row['target']==target)
    if fault=='omit':result['calls'].remove(row)
    elif fault=='duplicate':result['calls'].append(deepcopy(row))
    elif fault in ('site','target','return_address','sp'):row[fault]^=4
    elif fault.startswith('entry-'):row['entry'][fault[6:]]^=4
    elif fault.startswith('R'):
        registers=list(row['entry']['registers']);registers[int(fault[1:])]^=0x80000000;row['entry']['registers']=tuple(registers)
    else:result['calls'].reverse()
    with pytest.raises(ValueError):semantics.physical(case,observed,result,numerical)


@pytest.mark.parametrize('fault',('curve-return','absolute-return','root-return','byte-guard','word-only-code',
    'selected-index','selected-byte','signed-offset','copied-byte-only-positive'))
def test_actual_coolant_refuses_return_guard_selected_index_and_noncausal_positive_substitutions(windows,fault):
    declared,_,selected=windows;case,observed,saved,_,saved_numerical=selected['limiter-up']
    result=deepcopy(saved);numerical=deepcopy(saved_numerical)
    if fault.endswith('-return'):
        target={'curve-return':0x55396,'absolute-return':0x5541E,'root-return':observed['continuation']}[fault]
        next(row for row in result['branches'] if row['kind']=='return' and row['target']==target)['target']^=2
    elif fault=='byte-guard':next(row for row in result['branches'] if row['site']==0x26A9A)['kind']='fallthrough'
    elif fault=='word-only-code':result['code'][0x26A9C]='0009'
    elif fault=='selected-index':
        next(row for row in result['accesses'] if row['site']==0x553E6)['address']^=1
    elif fault=='selected-byte':numerical['selected']^=1
    elif fault=='signed-offset':numerical['coordinate']^=0x80
    else:
        actual=[];values=[]
        for _,old,_,value,_ in selected.values():
            changed=deepcopy(old);memory=bytearray(changed['memory_after'][0]);memory[0x15DA:0x15DC]=b'\0\0'
            changed['memory_after']=(bytes(memory),);actual.append(changed);values.append(value)
        with pytest.raises(ValueError):proof.require_positive_alternatives(actual,values,declared)
        return
    with pytest.raises(ValueError):semantics.physical(case,observed,result,numerical)
