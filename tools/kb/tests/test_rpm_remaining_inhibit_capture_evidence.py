"""Actual remaining_RPM originals reject changed complete state and selected-operand evidence."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import rpm_remaining_inhibit_contract as contract,rpm_remaining_inhibit_matrix as matrix
from kb import rpm_remaining_inhibit_capture_evidence as proof,rpm_remaining_inhibit_semantics as semantics
from kb import rpm_remaining_inhibit_transfers as transfers,rpm_inhibit_access_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['rpm_remaining_inhibit_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original remaining_RPM capture')
        pytest.skip('the complete original remaining_RPM capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_remaining_rpm_accesses'] is True
    assert result['quiet_diagnostic_premise']==contract.DIAGNOSTIC_PREMISE
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)==42
    assert all(outcomes==['fallthrough','taken'] for outcomes in result['conditional_branch_outcomes'].values())
    for flag in ('native_geometry_inference','automatic_resolution','scale_admission','units_admission',
            'diagnostic_producer_admission','whole_coordinator_admission','natural_caller_reachability',
            'hardware_qualification'):assert result[flag] is False
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('path',('tools/kb/src/kb/proof_sources.py','tools/kb/src/kb/proof_reuse.py'))
def test_actual_remaining_RPM_consumer_requires_transitive_source_binding_before_domain_admission(original,path):
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
    'simulator','toolchain','command','marker','stdout_sha256','observer_object_sha256',
    'boundaries','return_reconstruction'))
def test_actual_complete_remaining_RPM_original_requires_every_raw_capture_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','observer',
    'header','omit','duplicate','swap','kind','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after'))
def test_actual_remaining_RPM_source_toolchain_stream_and_complete_bound_snapshots_are_exact(original,fault):
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/rpm_remaining_inhibit_capture.py',
    'tools/sh-elf-run/stock_jk08a_rpm_remaining_inhibit.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-rpm-remaining-inhibit-paths.c',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s'))
def test_actual_remaining_RPM_producer_consumer_and_numerical_sources_match_the_original_snapshot(original,path):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[path]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    choices=(
        ('cut-low',0x4EDC6,'positive-cut',dict(stationary_cut=30)),
        ('cut-high',0x4EDC6,'positive-cut',dict(stationary_cut=40)),
        ('stationary-clear',0x4EDC6,'positive-stationary-state',dict(stationary_flags=8)),
        ('stationary-set',0x4EDC6,'positive-stationary-state',dict(stationary_flags=0x28)),
        ('thermal-clear',0x4EDC6,'positive-thermal-state',dict(thermal_flags=0)),
        ('thermal-set',0x4EDC6,'positive-thermal-state',dict(thermal_flags=8)),
        ('sustained-clear',0x4EDE4,'positive-sustained-state',dict(sustained_flags=0)),
        ('sustained-set',0x4EDE4,'positive-sustained-state',dict(sustained_flags=128)),
        ('ceiling-clear',0x4EE00,'positive-ceiling-state',dict(ceiling_flags=0)),
        ('ceiling-set',0x4EE00,'positive-ceiling-state',dict(ceiling_flags=128)),
        ('curve-up',0x4EDC6,'stationary-byte16-curve',dict(curve=list(range(0,256,17)),rpm16=194)),
        ('curve-down',0x4EDC6,'stationary-byte16-curve',dict(curve=list(range(255,-1,-17)),rpm16=194)),
        ('curve-upper',0x4EDC6,'stationary-byte16-curve',dict(curve=[255]*16,rpm16=640)))
    for name,entry,kind,changes in choices:
        case=next(row for row in declared['cases'] if row['entry']==entry and row['kind']==kind
            and all(row[key]==value for key,value in changes.items()))
        observed=actual[case['index']]
        result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        selected[name]=(case,observed,result,value)
    return declared,image,selected


def test_actual_five_roots_change_real_caller_outputs_with_all_other_inputs_fixed(windows):
    declared,_,selected=windows
    proof.require_positive_alternatives([row[1] for row in selected.values()],
        [row[3] for row in selected.values()],declared,owning.descriptor(repo.ROOT)['reference'])
    assert selected['stationary-clear'][1]['exit'][19]==selected['stationary-set'][1]['exit'][19]
    assert selected['stationary-clear'][1]['exit'][5]!=selected['stationary-set'][1]['exit'][5]
    for stem in ('thermal','sustained','ceiling'):
        assert selected[stem+'-clear'][1]['exit'][19]!=selected[stem+'-set'][1]['exit'][19]
    for stem in ('sustained-clear','sustained-set'):
        observed=selected[stem][1];assert observed['exit'][17]==observed['exit'][19]


@pytest.mark.parametrize('name,word',(('stationary-set',5),('thermal-set',19),
    ('sustained-set',17),('ceiling-set',19)))
def test_actual_caller_result_registers_are_required_independently_of_the_seed_byte(windows,name,word):
    _,image,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(windows[0]['source'],image,case)
    changed=list(observed['exit']);changed[word]^=1;observed['exit']=tuple(changed)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('site','target','return','sp','gbr','delay-r0','delay-r14','curve-argument','curve-table','curve-target'))
def test_actual_natural_calls_and_post_delay_operands_refuse_changed_boundaries(windows,fault):
    _,_,selected=windows;_,observed,result,value=deepcopy(selected['curve-up'])
    call=result['calls'][1] if fault.startswith('curve-') else result['calls'][0]
    if fault=='site':call['site']+=2
    elif fault=='target':call['target']=0x7D8B8
    elif fault=='return':call['return_address']+=2
    elif fault=='sp':call['sp']-=4
    elif fault=='gbr':call['entry']['gbr']^=4
    else:
        registers=list(call['entry']['registers'])
        index={'delay-r0':0,'delay-r14':14,'curve-argument':5,'curve-table':4,'curve-target':2}[fault]
        registers[index]^=1;call['entry']['registers']=tuple(registers)
    with pytest.raises(ValueError):transfers.require_calls(observed,result,value)


@pytest.mark.parametrize('name',('curve-up','curve-down','curve-upper','thermal-set','sustained-set','ceiling-set'))
@pytest.mark.parametrize('fault',('return-site','return-target','missing-return','extra-call','physical-width','physical-byte','omit-read'))
def test_actual_RTS_delay_paths_and_full_ordered_physical_operands_refuse_changes(windows,name,fault):
    declared,image,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    returned=next(row for row in result['branches'] if row['kind']=='return')
    accessed=next(row for row in result['accesses'] if row['domain']!='frame')
    if fault=='return-site':returned['site']+=2
    elif fault=='return-target':returned['target']+=2
    elif fault=='missing-return':result['branches'].remove(returned)
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='physical-width':accessed['width_bytes']=1
    elif fault=='physical-byte':accessed['bytes']='00'*accessed['width_bytes']
    else:result['accesses'].remove(accessed)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('dispatch','status-branch','byte-route','excluded-code'))
def test_actual_fixed_premises_refuse_dispatch_and_excluded_branch_outcomes(windows,fault):
    _,_,selected=windows;_,_,result,value=deepcopy(selected['curve-up'])
    if fault=='dispatch':
        call=deepcopy(result['calls'][0]);call['target']=0x7D8B8;result['calls'].append(call)
    elif fault=='excluded-code':result['code'][0x4F5F6]='420b'
    else:
        site=0x4F4CA if fault=='status-branch' else 0x26A9A
        branch=next(row for row in result['branches'] if row['site']==site)
        branch['kind']='fallthrough'
    with pytest.raises(ValueError):proof.require_premises(result,value)


@pytest.mark.parametrize('field,offset',(('status',0x4184),('count',0x571E)))
def test_actual_complete_incoming_RAM_refuses_unproved_diagnostic_inputs(windows,field,offset):
    declared,image,selected=windows;case,observed,_,_=deepcopy(selected['thermal-set'])
    data=bytearray(observed['memory_before'][0]);data[offset]=0;observed['memory_before']=(bytes(data),)
    with pytest.raises(ValueError):proof.require_state(declared,image,case,observed,repo.ROOT)


@pytest.mark.parametrize('offset',(0,4,8,12,16,20,68,76,80,84,88,132,136,180,184,344,348,368,372,376,536,560,564,568))
def test_original_observer_requires_complete_CPU_SP_PR_ABI_frames_and_SR(original,offset):
    packet=deepcopy(original[2]);row=packet['observations'][0]
    data=bytearray.fromhex(row['observation']);data[offset]^=1;row['observation']=data.hex()
    restream(packet);refuse(original,packet)


@pytest.mark.parametrize('name',('stationary-set','thermal-set','sustained-set','ceiling-set'))
@pytest.mark.parametrize('offset',(0,0x16A6,0x247C,0x247F,0x249C,0x41F2,0xFFFF))
def test_actual_complete_terminal_RAM_requires_the_exact_scalar_and_instruction_result(windows,name,offset):
    declared,image,selected=windows;case,observed,_,_=deepcopy(selected[name])
    data=bytearray(observed['memory_after'][0]);data[offset]^=1;observed['memory_after']=(bytes(data),)
    with pytest.raises(ValueError):proof.require_state(declared,image,case,observed,repo.ROOT)


@pytest.mark.parametrize('fault',('address','bytes','source','object','elf','missing','extra'))
def test_actual_outside_return_reconstruction_is_complete_and_separate(original,fault):
    packet=deepcopy(original[2]);rows=packet['return_reconstruction']
    if fault=='address':rows[0]['address']=0x4EDC6
    elif fault=='bytes':rows[0]['bytes']='000b0009'
    elif fault=='source':rows[0]['source_sha256']='0'*64
    elif fault in ('object','elf'):rows[0][fault+'_sha256']='invalid'
    elif fault=='missing':rows.pop()
    else:rows.append(deepcopy(rows[0]))
    with pytest.raises(ValueError):proof.require_return_reconstruction(repo.ROOT,packet)


