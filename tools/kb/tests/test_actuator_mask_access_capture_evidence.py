"""Actual original actuator mask access raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import actuator_mask_access_contract as contract,actuator_mask_access_matrix as matrix
from kb import actuator_mask_access_capture_evidence as proof,actuator_mask_access_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['actuator_mask_access_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original actuator mask access capture')
        pytest.skip('the complete original actuator mask access capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_actuator_mask_access_paths'] is True and result['positive_diagnostic_array_reader'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/actuator_mask_access_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-actuator-mask-access-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    predicates={
        'first':lambda c:c['kind']=='complete-raw-register-width',
        'second':lambda c:c['kind']=='second-fixed-record-byte1-bit7-entire-raw-byte' and c['byte_5a82']==128,
        'inactive':lambda c:c['kind']=='second-fixed-record-byte1-bit7-entire-raw-byte' and c['byte_5a82']==0,
        'stage0':lambda c:c['kind']=='unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48' and c['byte_11b3']==42,
        'stage1':lambda c:c['kind']=='unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48' and c['byte_11b3']==43,
        'stage5':lambda c:c['kind']=='unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48' and c['byte_11b3']==44,
        'stage7':lambda c:c['kind']=='unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48' and c['byte_11b3']==45,
        'stage15':lambda c:c['kind']=='unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48' and c['byte_11b3']==46,
        'stage31':lambda c:c['kind']=='unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48' and c['byte_11b3']==47,
        'stage63':lambda c:c['kind']=='unsigned-staged-mask-entire-raw-byte-and-thresholds43-through48' and c['byte_11b3']==48,
        'low2':lambda c:c['kind']=='low-speed-entire-byte-including-signed-load-boundary' and c['byte_110e']==2,
        'above3':lambda c:c['kind']=='low-speed-entire-byte-including-signed-load-boundary' and c['byte_110e']==3,
        'signed128':lambda c:c['kind']=='low-speed-entire-byte-including-signed-load-boundary' and c['byte_110e']==128,
        'state-clear':lambda c:c['kind']=='state-bit2-entire-raw-byte-with-admitted-low-speed' and c['byte_10e4']==0}
    for name,predicate in predicates.items():
        case=next(row for row in declared['cases'] if predicate(row));observed=actual[case['index']]
        result,value=proof.require_state(declared,image,case,observed,repo.ROOT);selected[name]=(case,observed,result,value)
    return declared,image,actual,selected


def test_all_natural_leaf_entries_have_separate_complete_register_SR_RAM_frame_and_physical_results(windows):
    declared,image,_,selected=windows
    for case,observed,result,value in selected.values():
        fixture,_=contract.fixture_for_case(declared['source'],image,case)
        assert observed['exit']==(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers']))
        assert observed['memory_after']==(value['ram'],)
        assert result['accesses']==transfers.physical(observed,result,value,fixture)
        assert len(result['calls'])==len(value['calls']) and result['trace'][-1]['delay_slot'] is True
        assert result['trace'][-1]['next']==observed['continuation']
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x5099C}


@pytest.mark.parametrize('name',('first', 'second', 'inactive', 'stage0', 'stage1', 'stage5', 'stage7', 'stage15', 'stage31', 'stage63', 'low2', 'above3', 'signed128', 'state-clear'))
@pytest.mark.parametrize('fault',('register','SR','PR','GBR','MACH','MACL','frame','RAM','extra-data-read','extra-data-write',
    'extra-call','branch-site','branch-target','branch-delay','omit-return','extra-return','code-byte','omit-code',
    'delay-slot','return-SP','return-GBR','return-MACL','return-target'))
def test_actual_complete_state_physical_natural_branch_delay_and_return_refusals(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
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
    elif fault=='code-byte':result['code'][next(iter(result['code']))]='0009'
    elif fault=='omit-code':result['code'].pop(next(iter(result['code'])))
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    elif fault=='return-SP':
        registers=list(result['trace'][-1]['after']['registers']);registers[15]-=4
        result['trace'][-1]['after']['registers']=tuple(registers)
    elif fault=='return-GBR':result['trace'][-1]['after']['gbr']^=1
    elif fault=='return-MACL':result['trace'][-1]['after']['macl']^=1
    else:result['trace'][-1]['next']^=2
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('name',('first', 'second', 'inactive', 'stage0', 'stage1', 'stage5', 'stage7', 'stage15', 'stage31', 'stage63', 'low2', 'above3', 'signed128', 'state-clear'))
@pytest.mark.parametrize('fault',('site','mode','address','width_bytes','register','domain','bytes','omit','duplicate'))
def test_exact_ordered_physical_data_pool_and_stack_operands_cannot_be_substituted(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='omit':result['accesses'].pop()
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][0]))
    else:
        row=result['accesses'][0];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('offset',(0,4,8,12,16,20,68,76,80,84,88,132,136,180,184,344,348,368,372,376,536,560,564,568))
def test_original_observer_preserves_every_complete_CPU_SP_PR_SR_ABI_and_frame_slice(original,offset):
    packet=deepcopy(original[2]);row=packet['observations'][0]
    data=bytearray.fromhex(row['observation']);data[offset]^=1;row['observation']=data.hex()
    restream(packet);refuse(original,packet)


@pytest.mark.parametrize('name',('first', 'second', 'inactive', 'stage0', 'stage1', 'stage5', 'stage7', 'stage15', 'stage31', 'stage63', 'low2', 'above3', 'signed128', 'state-clear'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('first', 'second', 'inactive', 'stage0', 'stage1', 'stage5', 'stage7', 'stage15', 'stage31', 'stage63', 'low2', 'above3', 'signed128', 'state-clear'))
@pytest.mark.parametrize('fault',('R0','R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12','R13','R14','SP','PR','GBR','MACH','MACL','SR','target'))
def test_every_real_helper_keeps_complete_actual_post_delay_state(windows,name,fault):
    declared,image,_,selected=windows
    for index in range(len(selected[name][2]['calls'])):
        case,observed,result,value=deepcopy(selected[name]);call=result['calls'][index]
        fixture,_=contract.fixture_for_case(declared['source'],image,case)
        if fault.startswith('R') and fault[1:].isdigit():
            registers=list(call['entry']['registers']);registers[int(fault[1:])]^=1;call['entry']['registers']=tuple(registers)
        elif fault=='target':call['target']^=2
        else:call['entry'][fault.lower()]^=0x10 if fault=='SR' else 1
        with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_exact_post_delay_record_ids_bind_the_actual_array_member_addresses(windows):
    _,_,_,selected=windows
    for name,ids,addresses in (('first',(0x71,),(0xFFFF586C,)),('second',(0x71,0x123),(0xFFFF586C,0xFFFF5A82))):
        _,_,result,value=selected[name]
        calls=[row for row in result['calls'] if row['target']==0x25E20]
        assert tuple(row['entry']['registers'][4] for row in calls)==ids
        assert transfers.require_fixed_record_reads(result)==addresses
        assert all(row['return_site']==0x25E40 for row in value['calls'] if row['target']==0x25E20)


@pytest.mark.parametrize('fault',('first-id','second-id','member-address','member-width','member-register','member-domain','omit-read','duplicate-read'))
def test_fixed_record_array_dependency_cannot_be_replaced_by_a_root_byte_absence_check(windows,fault):
    result=deepcopy(windows[3]['second'][2]);calls=[row for row in result['calls'] if row['target']==0x25E20]
    if fault.endswith('id'):
        row=calls[0 if fault=='first-id' else 1];registers=list(row['entry']['registers']);registers[4]^=1;row['entry']['registers']=tuple(registers)
    else:
        index=next(i for i,row in enumerate(result['accesses']) if row['site']==0x25E32)
        if fault=='omit-read':result['accesses'].pop(index)
        elif fault=='duplicate-read':result['accesses'].append(deepcopy(result['accesses'][index]))
        else:
            row=result['accesses'][index];key={'member-address':'address','member-width':'width_bytes','member-register':'register','member-domain':'domain'}[fault]
            row[key]='changed' if key=='domain' else row[key]^1
    with pytest.raises(ValueError):transfers.require_fixed_record_reads(result)


def test_all_seven_unsigned_stage_results_and_signed_low_speed_boundary_are_actual(windows):
    selected=windows[3]
    for name,value in (('stage0',0),('stage1',1),('stage5',5),('stage7',7),('stage15',15),('stage31',31),('stage63',63),
            ('inactive',0),('low2',63),('above3',5),('signed128',5),('state-clear',5)):
        assert selected[name][1]['exit'][-1]==selected[name][3]['output']==value
    low=selected['signed128'][2]
    loaded=next(row for row in low['trace'] if row['site']==0x509F0)
    assert loaded['after']['registers'][2]==0xFFFFFF80


def test_second_mask_call_delay_slot_and_later_reload_use_one_real_local_byte(windows):
    _,_,_,selected=windows
    for name in ('stage0','stage1','stage5','stage7','stage15','stage31','stage63','low2'):
        _,observed,result,value=selected[name];call=next(row for row in result['calls'] if row['site']==0x5098E)
        local=observed['sp']-8
        rows=[row for row in result['accesses'] if row['site'] in (0x50990,0x50992)]
        assert [(row['site'],row['mode'],row['address'],row['width_bytes'],row['register'],row['domain']) for row in rows]==[
            (0x50990,'write',local,1,0,'frame'),(0x50992,'read',local,1,2,'frame')]
        assert rows[0]['bytes']==rows[1]['bytes'] and call['entry']['sp']==local
        delay=next(row for row in result['trace'] if row['site']==0x50990)
        assert delay['delay_slot'] is True and delay['next']==0x509EA
        assert value['frame']==observed['frame_after'] and value['ram']==observed['memory_after'][0]


@pytest.mark.parametrize('site',(0x50990,0x50992))
@pytest.mark.parametrize('fault',('omit','duplicate','bytes','address','width_bytes','register','mode','domain'))
def test_local_byte_argument_requires_both_exact_ordered_physical_operands(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['first'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][index]))
    else:
        row=result['accesses'][index];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)
