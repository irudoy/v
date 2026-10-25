"""Actual original complete contributor inputs reject changed data and execution boundaries."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import rpm_inhibit_contract as contract,rpm_inhibit_matrix as matrix
from kb import rpm_inhibit_capture_evidence as proof,rpm_inhibit_transfers as transfers


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['rpm_inhibit_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete original RPM contributor capture')
        pytest.skip('the complete original RPM contributor capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_bounded_rpm_inhibit_accesses'] is True
    assert result['full_coordinator_admission'] is result['stock_conditioned_pair_reachability'] is False
    assert result['exact_summary_bit_accesses'] is True and result['stock_shared_status_reachability'] is False
    assert result['exact_composite_status_accesses'] is True and result['stock_composite_seed_reachability'] is False
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)==33
    assert all(values==['fallthrough','taken'] for values in result['conditional_branch_outcomes'].values())
    assert result['fixed_branch_outcomes']=={f'{site:08x}':[kind] for site,kind in proof.FIXED_BRANCHES.items()}
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


def test_missing_original_contributor_component_refuses(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('rpm_inhibit_paths')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries','stub_reconstruction',
    'observations','simulator','toolchain'))
def test_actual_complete_capture_schema_requires_every_original_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','stub','returncode','timeout','compiler','simulator','observer','header'))
def test_actual_reconstruction_source_alias_return_toolchain_and_terminal_refuse_changes(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction'][0]['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction'][1]['pools'][0]['stock']='00000000'
    elif fault=='alias':packet['aliases'][0]['alias']+=4
    elif fault=='stub':packet['stub_reconstruction'][0]['bytes']='000b0009'
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=1
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    elif fault=='observer':packet['consumed'][proof.OBSERVER]+='00'
    else:packet['consumed'][proof.HEADER]+='00'
    refuse(original,packet)


@pytest.mark.parametrize('fault',('omit','duplicate','swap','index','kind','entry','observation','context','context-after'))
def test_actual_invocations_refuse_changes_with_a_consistent_terminal_stream_hash(original,fault):
    packet=deepcopy(original[2]);rows=packet['observations']
    if fault=='omit':rows.pop()
    elif fault=='duplicate':rows[-1]=deepcopy(rows[0])
    elif fault=='swap':rows[0],rows[-1]=rows[-1],rows[0]
    elif fault=='index':rows[0]['index']=True
    elif fault=='kind':rows[0]['kind']=1
    elif fault=='entry':rows[0]['entry']+=2
    else:
        key={'observation':'observation','context':'context','context-after':'context_after'}[fault]
        data=bytearray.fromhex(rows[0][key]);data[0]^=1;rows[0][key]=data.hex()
    restream(packet);refuse(original,packet)


@pytest.mark.parametrize('source',('defs/JK08A.rpm-inhibit.toml','tools/sh-elf-run/rpm_inhibit_capture.py',
    'tools/sh-elf-run/harness-rpm-inhibit-paths.c','tools/sh-elf-run/stock_jk08a_rpm_inhibit_callers.s',
    'tools/sh-elf-run/stock_jk08a_main_rpm_fuel_cut.s','tools/sh-elf-run/stock_jk08a_vehicle_speed_fuel_cut.s',
    'tools/sh-elf-run/stock_jk08a_rpm_summary_leaves.s',
    'tools/sh-elf-run/stock_jk08a_composite_rpm_inhibit.s','tools/sh-elf-run/stock_jk08a_diagnostic_fault_sentinel.s',
    'tools/sh-elf-run/stock_jk08a_implicit_byte_curve.s','tools/kb/src/kb/apc_reset_offset_semantics.py',
    'tools/sh-elf-run/publication_inhibit_snapshot_return.s','tools/kb/src/kb/rpm_inhibit_contract.py',
    'tools/kb/src/kb/rpm_inhibit_matrix.py','tools/kb/src/kb/rpm_inhibit_semantics.py',
    'tools/kb/src/kb/rpm_inhibit_transfers.py','tools/kb/src/kb/rpm_inhibit_capture_evidence.py',
    'tools/kb/src/kb/byte_surface_equations.py'))
def test_actual_complete_source_snapshot_refuses_stale_inputs(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    image=repo.images()['JK08A'].path.read_bytes();declared=original[2]['declaration']
    fixture,_=contract.independent_fixture(declared['source'],image)
    observations=proof.observations(original[2],declared);selected={}
    scenarios={'normal':{},'main-on':dict(rpm=612),'main-active':dict(main_flags=4,rpm=596),
        'main-off':dict(main_flags=4,rpm=595),'main-delay':dict(main_flags=2,rpm=612,main_delay=1),
        'conditioned':dict(config=0xE3,condition2=32,rpm=100),'vehicle-on':dict(speed=93),
        'vehicle-delay':dict(vehicle_control=0x80,vehicle_delay=1,speed=93),
        'vehicle-off':dict(vehicle_flags=1,speed=90),'wide-prior':dict(prior=0x80000000,vehicle_flags=1,speed=91)}
    scenarios.update({'maf-summary-off':{},'maf-summary-on':dict(summary_flags=128),
        'maf-summary-low':dict(summary_flags=128,summary_rpm=191),'shared-status-off':{},
        'shared-status-on':dict(shared_status=2),
        'shared-status-word':dict(summary_flags=128,shared_status=2,prior=0x80000000,prior2=1,prior14=0x40000000),
        'maf-summary-word':dict(summary_flags=128,shared_status=2,prior=0x80000000,prior2=1,prior14=0x40000000)})
    scenarios.update({'composite-normal':{},'composite-seed':dict(seed_flags=128),
        'composite-low-off':dict(low_rpm=68,low_gate1=64,low_gate2=32),
        'composite-low-on':dict(low_flags=1,low_rpm=68,low_gate1=64,low_gate2=32),
        'composite-high-off':dict(rpm=500,high_gate1=4),
        'composite-high-on':dict(high_flags=4,rpm=500,high_gate1=4),
        'composite-curve-up':dict(speed=9,high_gate1=4,**dict(zip(('c'+str(i) for i in range(8)),(0,32,64,96,128,160,192,255)))),
        'composite-curve-down':dict(speed=9,high_gate1=4,**dict(zip(('c'+str(i) for i in range(8)),(255,192,160,128,96,64,32,0)))),
        'composite-word':dict(prior=0x80000000,prior2=1,prior14=0x40000000)})
    for name,changes in scenarios.items():
        wanted=dict(matrix.DEFAULTS);wanted.update(changes)
        kind='maf-summary' if name.startswith('maf-summary') else 'shared-status' if name.startswith('shared-status') else 'composite-status' if name.startswith('composite') else 'contributors'
        case=next(row for row in declared['cases'] if row['kind']==kind and all(row[key]==value for key,value in wanted.items()))
        observed=observations[case['index']];result,value=proof.require_state(declared,image,fixture,case,observed)
        controlled=bytearray(fixture)
        for at,data in observed['calibration_before'].items():controlled[at:at+len(data)]=data
        selected[name]=(case,observed,result,value,bytes(controlled))
    return declared,image,fixture,selected


@pytest.mark.parametrize('name',('normal','main-on','main-active','main-off','main-delay','conditioned',
    'vehicle-on','vehicle-delay','vehicle-off','wide-prior','maf-summary-off','maf-summary-on','maf-summary-low',
    'maf-summary-word','shared-status-off','shared-status-on','shared-status-word',
    'composite-normal','composite-seed','composite-low-on','composite-high-on',
    'composite-curve-up','composite-curve-down','composite-word'))
@pytest.mark.parametrize('fault',('main-input','vehicle-input','condition-input','rpm-input','speed-input','main-output',
    'vehicle-output','main-delay','vehicle-delay','other-RAM','frame-before','frame-after','context','abi','sp','continuation',
    'R0','R2','R14','R7','PR','GBR','MACL','MACH','SR','threshold','configuration',
    'MAF-summary-input','MAF-RPM-input','shared-status-input','low-flags-input','high-flags-input',
    'seed-input','low-RPM-input','threshold-output','low-flags-output','high-flags-output'))
def test_actual_complete_input_output_context_frame_ABI_and_terminal_are_required(windows,name,fault):
    declared,image,fixture,selected=windows;case,saved,_,_,_=selected[name];observed=deepcopy(saved)
    offsets={'main-input':0x2497,'vehicle-input':0x24A6,'condition-input':0x2494,'rpm-input':0x11BC,
        'speed-input':0x110E,'main-output':0x2497,'vehicle-output':0x24A6,'main-delay':0x24F1,
        'vehicle-delay':0x24F6,'other-RAM':0x2498,'MAF-summary-input':0x2448,
        'MAF-RPM-input':0x11B2,'shared-status-input':0x418C,'low-flags-input':0x2489,
        'high-flags-input':0x249F,'seed-input':0x41EA,'low-RPM-input':0x11B3,
        'threshold-output':0x17CA,'low-flags-output':0x2489,'high-flags-output':0x249F}
    if fault in offsets:
        key='memory_before' if fault.endswith('-input') else 'memory_after'
        data=bytearray(observed[key][0]);data[offsets[fault]]^=1;observed[key]=(bytes(data),)
    elif fault in ('frame-before','frame-after'):
        key='frame_before' if fault=='frame-before' else 'frame_after'
        data=bytearray(observed[key]);data[156]^=1;observed[key]=bytes(data)
    elif fault in ('context','abi'):
        key='context' if fault=='context' else 'abi_after';data=list(observed[key]);data[0]^=1;observed[key]=tuple(data)
    elif fault in ('sp','continuation'):observed[fault]^=4
    elif fault in ('threshold','configuration'):
        at=0x934E if fault=='threshold' else 0x8B38
        data=bytearray(observed['calibration_before'][at]);data[0]^=1;observed['calibration_before'][at]=bytes(data)
    else:
        field={'R0':19,'R2':17,'R14':5,'R7':12,'PR':1,'GBR':4,'MACL':2,'MACH':3,'SR':0}[fault]
        data=list(observed['exit']);data[field]^=1;observed['exit']=tuple(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('name',('main-on','main-off','conditioned','vehicle-on','vehicle-off'))
@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','value','domain','order'))
def test_actual_ordered_RAM_ROM_pool_and_RMW_transfers_are_required(windows,name,fault):
    *_,selected=windows;_,observed,saved,value,fixture=selected[name];result=deepcopy(saved)
    site=0x4F2A4 if name=='conditioned' else 0x4F30E if name=='main-on' else 0x4F288
    row=next(row for row in result['accesses'] if row['site']==site and row['mode']=='read')
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(deepcopy(row))
    elif fault=='site':row['site']+=2
    elif fault=='address':row['address']+=1
    elif fault=='width':row['width_bytes']=2 if row['width_bytes']==1 else 1
    elif fault=='direction':row['mode']='write'
    elif fault=='value':
        data=bytearray.fromhex(row['bytes']);data[0]^=1;row['bytes']=data.hex()
    elif fault=='domain':row['domain']='frame'
    else:
        first=result['accesses'].index(row);other=next(index for index,item in enumerate(result['accesses']) if item['site']==0x4F284)
        result['accesses'][first],result['accesses'][other]=result['accesses'][other],result['accesses'][first]
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('call-site','call-target','call-return','call-sp','entry-sp','entry-pr','entry-gbr',
    'first-R0','first-R14','second-R0','second-R14','omit-call','extra-call','return-site','return-target','return-order'))
def test_actual_two_calls_MOV_OR_delay_state_and_natural_outside_returns_are_required(windows,fault):
    *_,selected=windows;_,observed,saved,value,fixture=selected['wide-prior'];result=deepcopy(saved)
    if fault=='omit-call':result['calls'].pop()
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault.startswith('return-'):
        returns=[row for row in result['branches'] if row['kind']=='return']
        if fault=='return-order':
            a=result['branches'].index(returns[0]);b=result['branches'].index(returns[1])
            result['branches'][a],result['branches'][b]=result['branches'][b],result['branches'][a]
        else:returns[0]['site' if fault=='return-site' else 'target']+=2
    elif fault.startswith('call-'):
        key={'call-site':'site','call-target':'target','call-return':'return_address','call-sp':'sp'}[fault]
        result['calls'][0][key]^=4
    elif fault.startswith('entry-'):result['calls'][0]['entry'][fault[6:]]^=4
    else:
        index=0 if fault.startswith('first-') else 1;register=0 if fault.endswith('R0') else 14
        data=list(result['calls'][index]['entry']['registers']);data[register]^=0x80000000
        result['calls'][index]['entry']['registers']=tuple(data)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_conditioned_status_input_has_no_stock_read_claim_from_the_unconditioned_path(windows):
    *_,selected=windows
    ordinary=selected['normal'][2];controlled=selected['conditioned'][2]
    assert not any(row['site']==0x4F2A4 for row in ordinary['accesses'])
    assert any(row['site']==0x4F2A4 and row['address']==0x01002494 and row['mode']=='read'
        for row in controlled['accesses'])
    assert selected['conditioned'][0]['config']&128


@pytest.mark.parametrize('name',('maf-summary-off','maf-summary-on','maf-summary-low','shared-status-on'))
@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','bytes','domain','order'))
def test_actual_summary_RAM_and_PC_pool_transfers_refuse_mutation(windows,name,fault):
    *_,selected=windows;_,observed,saved,value,fixture=selected[name];result=deepcopy(saved)
    rows=[row for row in result['accesses'] if row['domain']!='frame']
    target=next(row for row in rows if row['site']==(0x4FAA2 if name.startswith('shared') else 0x4F738))
    if fault=='omit':result['accesses'].remove(target)
    elif fault=='duplicate':result['accesses'].append(deepcopy(target))
    elif fault=='site':target['site']+=2
    elif fault=='address':target['address']+=1
    elif fault=='width':target['width_bytes']=2
    elif fault=='direction':target['mode']='write'
    elif fault=='bytes':target['bytes']='00' if target['bytes']!='00' else '80'
    elif fault=='domain':target['domain']='frame'
    else:
        left=result['accesses'].index(rows[0]);right=result['accesses'].index(target)
        result['accesses'][left],result['accesses'][right]=result['accesses'][right],result['accesses'][left]
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('name',('maf-summary-word','shared-status-word'))
@pytest.mark.parametrize('fault',('R0','R2','R14','wrong-OR','site','target','return','sp','entry-pr','entry-gbr',
    'omit','duplicate','return-site','return-target','return-order'))
def test_actual_summary_calls_distinguish_R0_and_R2_delay_inputs_and_exact_returns(windows,name,fault):
    *_,selected=windows;_,observed,saved,value,fixture=selected[name];result=deepcopy(saved)
    call=result['calls'][0]
    if fault in ('R0','R2','R14','wrong-OR'):
        registers=list(call['entry']['registers'])
        if fault=='wrong-OR':
            other=value['incoming_r2'] if name.startswith('maf') else value['incoming_r0']
            registers[14]=value['incoming_r14']|other
        else:registers[{'R0':0,'R2':2,'R14':14}[fault]]^=0x80000000
        call['entry']['registers']=tuple(registers)
    elif fault in ('site','target','return','sp'):call['return_address' if fault=='return' else fault]^=4
    elif fault.startswith('entry-'):call['entry'][fault[6:]]^=4
    elif fault=='omit':result['calls'].pop()
    elif fault=='duplicate':result['calls'].append(deepcopy(call))
    else:
        returns=[row for row in result['branches'] if row['kind']=='return']
        if fault=='return-order':
            left=result['branches'].index(returns[0]);right=result['branches'].index(returns[1])
            result['branches'][left],result['branches'][right]=result['branches'][right],result['branches'][left]
        else:returns[0]['site' if fault=='return-site' else 'target']+=2
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('name,site',(('composite-seed',0x507E2),('composite-low-off',0x50844),
    ('composite-low-off',0x50858),('composite-low-on',0x5085A),('composite-low-on',0x50868),
    ('composite-high-off',0x5089C),('composite-high-off',0x508BC),('composite-high-on',0x508BE),
    ('composite-high-on',0x508CC),('composite-high-on',0x508A6),('composite-normal',0x26380),
    ('composite-curve-up',0x26AAC),('composite-curve-down',0x26AAE),
    ('composite-curve-up',0x26AB4),('composite-normal',0x50896),('composite-normal',0x508B0),
    ('composite-normal',0x4EDEA),('composite-normal',0x259E4)))
@pytest.mark.parametrize('fault',('omit','duplicate','site','address','width','direction','bytes','domain','order'))
def test_actual_composite_pool_ROM_RAM_RMW_and_threshold_transfers_are_exact(windows,name,site,fault):
    *_,selected=windows;_,observed,saved,value,fixture=selected[name];result=deepcopy(saved)
    row=next(item for item in result['accesses'] if item['site']==site and item['domain']!='frame')
    if fault=='omit':result['accesses'].remove(row)
    elif fault=='duplicate':result['accesses'].append(deepcopy(row))
    elif fault=='site':row['site']+=2
    elif fault=='address':row['address']+=1
    elif fault=='width':row['width_bytes']=4 if row['width_bytes']!=4 else 2
    elif fault=='direction':row['mode']='write' if row['mode']=='read' else 'read'
    elif fault=='bytes':
        data=bytearray.fromhex(row['bytes']);data[0]^=1;row['bytes']=data.hex()
    elif fault=='domain':row['domain']='frame'
    else:
        first=result['accesses'].index(row)
        other=next(index for index,item in enumerate(result['accesses']) if item['domain']!='frame' and item is not row)
        result['accesses'][first],result['accesses'][other]=result['accesses'][other],result['accesses'][first]
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('call_index',range(4))
@pytest.mark.parametrize('fault',('site','target','return','sp','entry-sp','entry-pr','entry-gbr',
    'omit','duplicate','return-site','return-target','return-order'))
def test_actual_composite_sentinel_curve_closure_and_nested_returns_are_exact(windows,call_index,fault):
    *_,selected=windows;_,observed,saved,value,fixture=selected['composite-curve-down'];result=deepcopy(saved)
    call=result['calls'][call_index]
    if fault in ('site','target','return','sp'):call['return_address' if fault=='return' else fault]^=4
    elif fault.startswith('entry-'):call['entry'][fault[6:]]^=4
    elif fault=='omit':result['calls'].pop(call_index)
    elif fault=='duplicate':result['calls'].append(deepcopy(call))
    else:
        returns=[row for row in result['branches'] if row['kind']=='return']
        if fault=='return-order':
            first=result['branches'].index(returns[0]);second=result['branches'].index(returns[1])
            result['branches'][first],result['branches'][second]=result['branches'][second],result['branches'][first]
        else:returns[call_index]['site' if fault=='return-site' else 'target']+=2
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('call_index,register',((0,0),(0,2),(0,3),(0,14),(1,0),(1,4),(1,7),(1,14),
    (2,0),(2,4),(2,7),(2,14),(3,0),(3,2),(3,4),(3,5),(3,6),(3,7),(3,12),(3,13),(3,14)))
def test_actual_composite_post_delay_full_words_and_both_minus_one_arguments_are_required(windows,call_index,register):
    *_,selected=windows;_,observed,saved,value,fixture=selected['composite-word'];result=deepcopy(saved)
    values=list(result['calls'][call_index]['entry']['registers']);values[register]^=1
    result['calls'][call_index]['entry']['registers']=tuple(values)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('site',tuple(proof.FIXED_BRANCHES))
@pytest.mark.parametrize('fault',('omit','duplicate','outcome'))
def test_actual_composite_exact_sentinel_and_byte_entry_branch_premises_refuse_changes(windows,site,fault):
    *_,selected=windows;result=deepcopy(selected['composite-curve-up'][2])
    row=next(row for row in result['branches'] if row['site']==site)
    if fault=='omit':result['branches'].remove(row)
    elif fault=='duplicate':result['branches'].append(deepcopy(row))
    else:row['kind']='fallthrough' if row['kind']=='taken' else 'taken'
    with pytest.raises(ValueError):proof.require_composite_branches(result)


@pytest.mark.parametrize('site',proof.UNREACHABLE_BRANCHES)
def test_actual_composite_infeasibility_is_bound_to_the_exact_sentinel_closure(windows,site):
    *_,selected=windows;result=deepcopy(selected['composite-normal'][2])
    result['branches'].append(dict(site=site,target=site+2,kind='fallthrough',delay=False))
    with pytest.raises(ValueError):proof.require_composite_branches(result)


@pytest.mark.parametrize('offset',(0x1038,0x4200))
def test_actual_composite_sentinel_closure_has_no_diagnostic_branch_RAM_read(windows,offset):
    *_,selected=windows;result=deepcopy(selected['composite-normal'][2])
    result['accesses'].append(dict(site=0x50806,mode='read',address=matrix.RAM_BASE+offset,
        width_bytes=1,bytes='00',domain='ram'))
    with pytest.raises(ValueError):proof.require_composite_branches(result)


@pytest.mark.parametrize('address',(0x9462,0x12A32))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_actual_composite_complete_hysteresis_and_curve_inputs_are_bound(windows,address,phase):
    declared,image,fixture,selected=windows;case,saved,_,_,_=selected['composite-curve-up']
    observed=deepcopy(saved);data=bytearray(observed[phase][address]);data[0]^=1
    observed[phase][address]=bytes(data)
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)
