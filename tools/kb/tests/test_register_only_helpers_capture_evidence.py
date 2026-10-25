"""Actual original register-only helper raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import register_only_helpers_contract as contract,register_only_helpers_matrix as matrix
from kb import register_only_helpers_capture_evidence as proof
from kb import register_only_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['register_only_helper_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original register-only helper capture')
        pytest.skip('the complete original register-only helper capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_register_only_paths'] is True and result['no_datum_access'] is True
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)
    assert all(outcomes==['fallthrough','taken'] for outcomes in result['conditional_branch_outcomes'].values())
    for key in ('native_geometry_inference','automatic_resolution','scale_admission','units_admission',
            'native_identity_admission','natural_caller_reachability','hardware_qualification'):
        assert result[key] is False
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
    'simulator','toolchain','command','marker','stdout_sha256','observer_object_sha256','boundaries','return_reconstruction'))
def test_complete_actual_capture_requires_every_raw_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','observer',
    'header','omit','duplicate','swap','kind','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after','outside-return'))
def test_actual_source_toolchain_and_complete_original_stream_refuse_changed_bytes(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'].append(dict(address=0,stock='00',reconstructed='00'))
    elif fault=='alias':packet['aliases'].append(dict(address=0,alias=4))
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=1
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    elif fault=='observer':packet['consumed'][proof.OBSERVER]+='00'
    elif fault=='header':packet['consumed'][proof.HEADER]+='00'
    elif fault=='outside-return':packet['boundaries'].append(dict(address=0xC2000,bytes='000b0009'))
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/register_only_helpers_capture.py',
    'tools/sh-elf-run/stock_jk08a_register_only_helpers.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-register-only-helper-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py','tools/kb/tests/test_channel_pulse_chain.py','tools/kb/tests/test_fuel_cut_consumer_chain.py','tools/kb/tests/test_engine_speed_byte_tables.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    choices=(('shift7',0x224F8,dict(raw_r0=0x80000000)),('shift6',0x224FA,dict(raw_r0=0xFFFFFFFF)),
        ('shift11',0x2251C,dict(raw_r0=0x80000000)),
        ('compare-clear',0x259D0,dict(raw_r7=0)),('compare-set',0x259D0,dict(raw_r7=1)),
        ('interpolation-ascending',0x26740,dict(raw_r0=0,raw_r2=65536)),
        ('interpolation-descending',0x26740,dict(raw_r0=65536,raw_r2=0)),
        ('mask',0x50A4C,dict(raw_r4=63)))
    for name,entry,changes in choices:
        case=next(row for row in declared['cases'] if row['entry']==entry
            and all(row[key]==value for key,value in changes.items()))
        observed=actual[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        selected[name]=(case,observed,result,value)
    return declared,image,actual,selected


def test_every_natural_entry_has_independent_complete_scalar_register_and_frame_expectations(windows):
    _,_,_,selected=windows
    for _,observed,result,value in selected.values():
        assert observed['exit']==value['exit']
        assert result['accesses']==value['physical']
        assert all(row['domain']=='frame' for row in result['accesses'])
        assert result['calls']==[] and observed['memory_after']==observed['memory_before']
        assert result['branches'][-1]['site']==value['return_site']
        assert result['trace'][-1]['delay_slot'] is True
        assert result['trace'][-1]['next']==observed['continuation']
    assert selected['shift7'][2]['code'].keys()==dict.fromkeys(range(0x224F8,0x22508,2)).keys()
    assert selected['shift6'][2]['code'].keys()==dict.fromkeys(range(0x224FA,0x22508,2)).keys()


@pytest.mark.parametrize('name',('shift7','shift6','shift11','compare-clear','compare-set',
    'interpolation-ascending','interpolation-descending','mask'))
@pytest.mark.parametrize('fault',('register','SR','PR','GBR','MACH','MACL','frame','RAM',
    'extra-data-read','extra-data-write','extra-call','branch-site','branch-target','branch-delay',
    'omit-return','extra-return','omit-code','delay-slot','return-carrier','return-SP','return-target'))
def test_complete_register_frame_physical_absence_branch_and_return_refusals(windows,name,fault):
    _,_,_,selected=windows;_,observed,result,value=deepcopy(selected[name])
    if fault in ('register','SR','PR','GBR','MACH','MACL'):
        key={'register':'registers','SR':'sr','PR':'pr','GBR':'gbr','MACH':'mach','MACL':'macl'}[fault]
        if key=='registers':result[key]=(result[key][0]^1,*result[key][1:])
        else:result[key]^=1
    elif fault=='frame':result['frame']=bytes([result['frame'][0]^1])+result['frame'][1:]
    elif fault=='RAM':result['ram']=bytes([result['ram'][0]^1])+result['ram'][1:]
    elif fault in ('extra-data-read','extra-data-write'):
        result['accesses'].append(dict(site=observed['entry'],mode='read' if fault.endswith('read') else 'write',
            address=0x010022E0,width_bytes=1,register=0,domain='ram',bytes='a5'))
    elif fault=='extra-call':result['calls'].append(dict(site=observed['entry'],target=0x224FA))
    elif fault.startswith('branch-'):
        row=result['branches'][0];row[fault.split('-')[1]]=not row['delay'] if fault=='branch-delay' else 1
    elif fault=='omit-return':result['branches'].pop()
    elif fault=='extra-return':result['branches'].append(deepcopy(result['branches'][-1]))
    elif fault=='omit-code':result['code'].pop(next(iter(result['code'])))
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    elif fault=='return-carrier':result['trace'][-2]['before']['pr']^=2
    elif fault=='return-SP':
        registers=list(result['trace'][-1]['after']['registers']);registers[15]-=4
        result['trace'][-1]['after']['registers']=tuple(registers)
    else:result['trace'][-1]['next']^=2
    with pytest.raises(ValueError):proof.require_scalar_state(observed,result,value)


@pytest.mark.parametrize('name',('shift11','interpolation-descending'))
@pytest.mark.parametrize('fault',('site','mode','address','width_bytes','register','domain','bytes','omit','duplicate'))
def test_only_exact_ordered_natural_push_and_pop_are_admitted(windows,name,fault):
    _,_,_,selected=windows;_,observed,result,value=deepcopy(selected[name])
    if fault=='omit':result['accesses'].pop()
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][0]))
    else:
        row=result['accesses'][0];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):proof.require_scalar_state(observed,result,value)


def test_actual_R0_outputs_vary_only_with_held_other_register_inputs(windows):
    _,_,actual,_=windows
    proof.require_positive_alternatives(actual)
    unchanged=deepcopy(actual)
    for observed in unchanged:observed['exit']=(*observed['exit'][:-1],0)
    with pytest.raises(ValueError):proof.require_positive_alternatives(unchanged)


@pytest.mark.parametrize('offset',(0,4,8,12,16,20,68,76,80,84,88,132,136,180,184,344,348,368,372,376,536,560,564,568))
def test_original_observer_preserves_complete_CPU_SP_PR_SR_ABI_and_frame_bytes(original,offset):
    packet=deepcopy(original[2]);row=packet['observations'][0]
    data=bytearray.fromhex(row['observation']);data[offset]^=1;row['observation']=data.hex()
    restream(packet);refuse(original,packet)
