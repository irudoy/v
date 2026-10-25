"""Actual original division caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import division_caller_withdrawal_contract as contract,division_caller_withdrawal_matrix as matrix
from kb import division_caller_withdrawal_capture_evidence as proof,division_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['division_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original division caller withdrawal capture')
        pytest.skip('the complete original division caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_division_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/division_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-division-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    choices=(('word',0x3A254,dict(raw_r4=1000,enable_mask=8)),
        ('word-cap',0x3A254,dict(raw_r4=65535,enable_mask=8)),('disabled',0x3A254,dict(enable_mask=0)),
        ('unsigned-zero',0x6E442,dict(source_level=0)),('unsigned-short',0x6E442,dict(source_level=50,factor=0)),
        ('unsigned-long',0x6E442,dict(source_level=1,factor=255)),
        ('zero-positive',0xB7C84,dict(raw_r4=1,factor_first=0)),
        ('zero-negative',0xB7C84,dict(raw_r4=0xFFFFFFFF,factor_first=0)),
        ('signed-short',0xB7C84,dict(raw_r4=1,factor_first=50,factor_second=60)),
        ('signed-long',0xB7C84,dict(raw_r4=107350,factor_first=1,factor_second=1)),
        ('signed-negative',0xB7C84,dict(raw_r4=(-107350)&0xFFFFFFFF,factor_first=1,factor_second=1)),
        ('input-high',0xB7C84,dict(raw_r4=0x7FFFFFFF,factor_first=1,factor_second=1)),
        ('input-low',0xB7C84,dict(raw_r4=0x80000000,factor_first=1,factor_second=1)),
        ('product-cap',0xB7C84,dict(raw_r4=1,factor_first=255,factor_second=255)))
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x3A282,0x6E48C,0xB7CEE}


@pytest.mark.parametrize('name',('word','word-cap','disabled','unsigned-zero','unsigned-short','unsigned-long','zero-positive','zero-negative','signed-short','signed-long','signed-negative','input-high','input-low','product-cap'))
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


@pytest.mark.parametrize('name',('word','unsigned-long','signed-long','signed-negative'))
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
def test_immutable_dividend_multiplier_refuses_either_changed_byte(windows,offset,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['unsigned-long'])
    raw=bytearray(observed[phase][0x6E4E4]);raw[offset]^=1;observed[phase][0x6E4E4]=bytes(raw)
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('at',(0x8349,0x8542,0x8543))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_complete_configuration_bytes_cannot_be_substituted(windows,at,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['signed-long'])
    observed[phase][at]=bytes([observed[phase][at][0]^1])
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('word','unsigned-short','unsigned-long','signed-short','signed-long','signed-negative'))
@pytest.mark.parametrize('fault',('R0','R1','R4','R8','SP','PR','SR','MACL','target','before-delay'))
def test_actual_complete_post_delay_helper_state_cannot_be_replaced_by_pre_delay_or_scalar_results(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case);call=result['calls'][0]
    if fault.startswith('R') and fault[1:].isdigit():
        registers=list(call['entry']['registers']);registers[int(fault[1:])]^=1;call['entry']['registers']=tuple(registers)
    elif fault=='target':call['target']^=2
    elif fault=='before-delay':call['entry']['registers']=call['registers']
    else:call['entry'][fault.lower()]^=1
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('name',('word','unsigned-long','signed-short','signed-long','signed-negative'))
@pytest.mark.parametrize('fault',('omit-helper','return-site','return-SP','return-R2','return-MACL','return-delay','return-target'))
def test_actual_caller_requires_real_helper_bytes_and_complete_natural_return(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case);call=value['calls'][0]
    site=(0x21C6C if call['long_path'] else 0x21C04) if call['target']==0x21BBC else (0x21D66 if call['long_path'] else 0x21D08)
    terminal=next(i for i,r in enumerate(result['trace']) if r['site']==site)
    if fault=='omit-helper':result['trace']=[r for r in result['trace'] if r['site'] in transfers.CALLER_SITES]
    elif fault=='return-site':result['trace'][terminal]['site']^=2
    elif fault in ('return-SP','return-R2'):
        row=result['trace'][terminal+1]['after'];registers=list(row['registers']);registers[15 if fault=='return-SP' else 2]^=4;row['registers']=tuple(registers)
    elif fault=='return-MACL':result['trace'][terminal+1]['after']['macl']^=1
    elif fault=='return-delay':result['trace'][terminal+1]['delay_slot']=False
    else:result['trace'][terminal+1]['next']^=2
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_identical_primary_requires_the_separate_complete_original_direct_helper_capture(original):
    record=deepcopy(original[1]);record['candidate']['witness'].pop('division_callees_paths')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_actual_component_requires_both_native_RAM_aliases_and_direct_helper_original(original):
    result=proof.require_primary(original[0],original[1])
    assert result['no_selected_ram_datum_access'] is True and result['complete_direct_helpers_same_primary'] is True
    assert result['selected_native_RAM_aliases']=={'ffff115e':'0100115e','ffff33fc':'010033fc'}
    assert result['direct_helper_original_stdout_sha256']==original[1]['candidate']['witness']['division_callees_paths']['stdout_sha256']
