"""Actual original byte curve caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import byte_curve_caller_withdrawal_contract as contract,byte_curve_caller_withdrawal_matrix as matrix
from kb import byte_curve_caller_withdrawal_capture_evidence as proof,byte_curve_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['byte_curve_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original byte curve caller withdrawal capture')
        pytest.skip('the complete original byte curve caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_byte_curve_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/byte_curve_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-byte-curve-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    choices=(('first-up',0x2C59C,dict(coordinate_first=31,curve_first_0=0,curve_first_1=32)),
        ('first-down',0x2C59C,dict(coordinate_first=31,curve_first_0=255,curve_first_1=223)),
        ('first-flat',0x2C59C,dict(coordinate_first=31,curve_first_0=127,curve_first_1=127)),
        ('first-endpoint',0x2C59C,dict(coordinate_first=224,curve_first_7=255)),
        ('direct-up',0x6E3D8,dict(mode=2,coordinate_second=31,curve_second_0=0,curve_second_1=32)),
        ('direct-down',0x6E3D8,dict(mode=2,coordinate_second=31,curve_second_0=255,curve_second_1=223)),
        ('direct-endpoint',0x6E3D8,dict(mode=2,coordinate_second=224,curve_second_7=255)),
        ('scaled-short',0x6E3D8,dict(mode=0,coordinate_second=0,gain=0,denominator=1)),
        ('scaled-long',0x6E3D8,dict(mode=0,coordinate_second=255,gain=255,denominator=1)),
        ('scaled-down',0x6E3D8,dict(mode=0,coordinate_second=31,gain=64,denominator=32,curve_second_0=255,curve_second_1=223)),
        ('scaled-endpoint',0x6E3D8,dict(mode=0,coordinate_second=224,gain=64,denominator=32,curve_second_7=255)),
        ('zero-bypass',0x6E3D8,dict(mode=0,denominator=0)))
    for name,entry,changes in choices:
        case=next(row for row in declared['cases'] if row['entry']==entry
            and all(row[key]==value for key,value in changes.items()))
        observed=actual[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        selected[name]=(case,observed,result,value)
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x2C5BC,0x6E43E}


@pytest.mark.parametrize('name',('first-up','first-down','first-flat','first-endpoint','direct-up','direct-down','direct-endpoint','scaled-short','scaled-long','scaled-down','scaled-endpoint','zero-bypass'))
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


@pytest.mark.parametrize('name',('first-down','direct-down','scaled-down','scaled-endpoint'))
@pytest.mark.parametrize('fault',('site','mode','address','width_bytes','register','domain','bytes','omit','duplicate'))
def test_exact_ordered_physical_data_pool_and_stack_operands_cannot_be_substituted(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='omit':result['accesses'].pop()
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][0]))
    else:
        row=result['accesses'][0];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_actual_return_and_store_variation_requires_complete_fixed_other_preimages(windows):
    declared,_,actual,_=windows
    proof.require_positive_alternatives(actual,declared)
    unchanged=deepcopy(actual)
    for observed in unchanged:
        observed['exit']=(*observed['exit'][:-1],0);observed['memory_after']=(bytes(65536),)
    with pytest.raises(ValueError):proof.require_positive_alternatives(unchanged,declared)


@pytest.mark.parametrize('offset',(0,4,8,12,16,20,68,76,80,84,88,132,136,180,184,344,348,368,372,376,536,560,564,568))
def test_original_observer_preserves_every_complete_CPU_SP_PR_SR_ABI_and_frame_slice(original,offset):
    packet=deepcopy(original[2]);row=packet['observations'][0]
    data=bytearray.fromhex(row['observation']);data[offset]^=1;row['observation']=data.hex()
    restream(packet);refuse(original,packet)


@pytest.mark.parametrize('offset',(0,1))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_immutable_byte_mode_limit_refuses_either_changed_byte(windows,offset,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['first-up'])
    raw=bytearray(observed[phase][0x26382]);raw[offset]^=1;observed[phase][0x26382]=bytes(raw)
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('base',(0x12332,0x1296C))
@pytest.mark.parametrize('offset',range(8))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_byte_of_both_complete_controlled_curve_preimages_is_exact(windows,base,offset,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['scaled-down'])
    raw=bytearray(observed[phase][base]);raw[offset]^=1;observed[phase][base]=bytes(raw)
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name,index',(('first-up',0),('first-down',0),('first-endpoint',0),
    ('direct-down',0),('scaled-down',0),('scaled-down',1),('scaled-endpoint',1),('scaled-short',1),('scaled-long',1)))
@pytest.mark.parametrize('fault',('R0','R1','R4','R5','R8','SP','PR','GBR','SR','MACL','target','before-delay'))
def test_actual_complete_post_delay_curve_and_division_helper_inputs_are_independent(windows,name,index,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case);call=result['calls'][index]
    if fault.startswith('R') and fault[1:].isdigit():
        registers=list(call['entry']['registers']);registers[int(fault[1:])]^=1;call['entry']['registers']=tuple(registers)
    elif fault=='target':call['target']^=2
    elif fault=='before-delay':call['entry']['registers']=call['registers']
    else:call['entry'][fault.lower()]^=1
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('name,index',(('first-up',0),('first-down',0),('first-endpoint',0),
    ('scaled-down',0),('scaled-down',1),('scaled-endpoint',1),('scaled-short',1),('scaled-long',1)))
@pytest.mark.parametrize('fault',('omit-helper','return-site','return-SP','return-R2','return-MACL','return-SR','return-delay','return-target'))
def test_real_interior_curve_and_division_returns_cannot_be_replaced_by_outputs(windows,name,index,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case);call=value['calls'][index]
    terminal=next(i for i,r in enumerate(result['trace']) if r['site']==call['return_site'])
    if fault=='omit-helper':
        first=next(i for i,r in enumerate(result['trace']) if r['site']==call['site'])+2
        result['trace'][first:terminal+2]=[]
    elif fault=='return-site':result['trace'][terminal]['site']^=2
    elif fault in ('return-SP','return-R2'):
        row=result['trace'][terminal+1]['after'];registers=list(row['registers']);registers[15 if fault=='return-SP' else 2]^=4;row['registers']=tuple(registers)
    elif fault in ('return-MACL','return-SR'):result['trace'][terminal+1]['after'][fault[7:].lower()]^=1
    elif fault=='return-delay':result['trace'][terminal+1]['delay_slot']=False
    else:result['trace'][terminal+1]['next']^=2
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_descending_curve_save_is_read_before_division_replaces_the_same_frame_word(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['scaled-down']
    events=[row for row in result['accesses'] if row['site'] in (0x26744,0x26752,0x21BBC)]
    assert [(r['site'],r['mode'],r['address'],r['bytes']) for r in events]==[
        (0x26744,'write',observed['sp']-12,'000000ff'),(0x26752,'read',observed['sp']-12,'000000ff'),
        (0x21BBC,'write',observed['sp']-12,'00000040')]
    assert observed['frame_after'][148:152]==bytes.fromhex('00000040')


@pytest.mark.parametrize('fault',('omit-first-save','replace-first-with-final','swap-save-and-replacement','omit-first-read'))
def test_identical_terminal_frame_cannot_replace_intermediate_curve_save_and_read(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['scaled-down'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case);events=result['accesses']
    first=next(i for i,r in enumerate(events) if r['site']==0x26744)
    if fault=='omit-first-save':events.pop(first)
    elif fault=='replace-first-with-final':events[first]['bytes']='00000040'
    elif fault=='swap-save-and-replacement':
        other=next(i for i,r in enumerate(events) if r['site']==0x21BBC);events[first],events[other]=events[other],events[first]
    else:events.pop(next(i for i,r in enumerate(events) if r['site']==0x26752))
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_identical_primary_requires_the_separate_complete_original_direct_helper_capture(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('division_callees_paths')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_actual_component_requires_all_five_native_aliases_and_direct_helper_original(original):
    result=proof.require_primary(original[0],original[1])
    assert result['no_selected_ram_datum_access'] is True and result['complete_direct_helpers_same_primary'] is True
    assert result['selected_native_RAM_aliases']=={'ffff1300':'01001300','ffff1f86':'01001f86',
        'ffff2451':'01002451','ffff4185':'01004185','ffff84c0':'010084c0'}
    assert result['fixed_byte_mode_outcomes']=={'00026a9a':['taken']}
