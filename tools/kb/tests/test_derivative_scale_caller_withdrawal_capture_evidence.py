"""Actual original derivative scale caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import derivative_scale_caller_withdrawal_contract as contract,derivative_scale_caller_withdrawal_matrix as matrix
from kb import derivative_scale_caller_withdrawal_capture_evidence as proof,derivative_scale_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['derivative_scale_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original derivative scale caller withdrawal capture')
        pytest.skip('the complete original derivative scale caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_derivative_scale_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/derivative_scale_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-derivative-scale-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    for name,entry in (('first',0xB78DA),('second',0xB7A3C)):
        case=next(row for row in declared['cases'] if row['entry']==entry)
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0xB7A38,0xB7B94}


@pytest.mark.parametrize('name',('first','second'))
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


@pytest.mark.parametrize('name',('first','second'))
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


@pytest.mark.parametrize('name',('first','second'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_physical_curve_axis_literal_and_selector_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for at,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][at]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('first','second'))
@pytest.mark.parametrize('fault',('R0','R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12','R13','R14','SP','PR','GBR','MACH','MACL','SR','target'))
def test_every_real_helper_has_complete_actual_post_delay_inputs_even_when_scalar_remainder_is_unknown(windows,name,fault):
    declared,image,_,selected=windows
    for index in range(len(selected[name][2]['calls'])):
        case,observed,result,value=deepcopy(selected[name]);call=result['calls'][index]
        fixture,_=contract.fixture_for_case(declared['source'],image,case)
        if fault.startswith('R') and fault[1:].isdigit():
            registers=list(call['entry']['registers']);registers[int(fault[1:])]^=1;call['entry']['registers']=tuple(registers)
        elif fault=='target':call['target']^=2
        else:call['entry'][fault.lower()]^=0x10 if fault=='SR' else 1
        with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_actual_helpers_use_eight_and_sixteen_words_and_preserve_the_full_fifth_argument(windows):
    _,_,_,selected=windows
    first=selected['first'];second=selected['second']
    for chosen,call_site,axis_base,origin in ((first,0x26502,0x13B38,30),
            (second,0x264D6,0x13BB8,14),(second,0x26502,0x13BF8,30)):
        call=next(row for row in chosen[2]['calls'] if row['site']==call_site and row['entry']['registers'][0]==axis_base)
        assert call['target']==0x26984 and call['entry']['registers'][4]==origin
    case,observed,result,value=second
    assert observed['context'][19]==case['stack_argument']
    carrier=[row for row in result['accesses'] if row['site'] in (0xB7A58,0xB7A5E,0xB7A9E)]
    assert [(row['site'],row['mode'],row['address'],row['width_bytes']) for row in carrier]==[
        (0xB7A58,'read',observed['sp'],4),(0xB7A5E,'write',observed['sp']+3,1),(0xB7A9E,'read',observed['sp']+3,1)]
    assert carrier[0]['bytes']==case['stack_argument'].to_bytes(4,'big').hex()
    assert carrier[1]['bytes']==carrier[2]['bytes']==f'{case["stack_argument"]&255:02x}'
    assert observed['frame_before'][160:164]==observed['frame_after'][160:164]
    middle=next(row for row in result['calls'] if row['site']==0xB7AAC)
    assert middle['entry']['registers'][6]==(case['stack_argument']&255)<<8
    for chosen,site in ((first,0xB78F0),(second,0xB7A62)):
        call=next(row for row in chosen[2]['calls'] if row['site']==site)
        assert call['entry']['registers'][:2]==(20000,chosen[0]['raw_r6'])


@pytest.mark.parametrize('fault',('full-word-read','low-byte-write','low-byte-read','frame-carrier','context-carrier'))
def test_an_unchanged_final_fifth_word_cannot_replace_actual_intermediate_transfers(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['second'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='context-carrier':observed['context']=(*observed['context'][:19],observed['context'][19]^0x100)
    elif fault=='frame-carrier':
        frame=bytearray(observed['frame_before']);frame[160]^=1;observed['frame_before']=bytes(frame)
    else:
        site={'full-word-read':0xB7A58,'low-byte-write':0xB7A5E,'low-byte-read':0xB7A9E}[fault]
        result['accesses']=[row for row in result['accesses'] if row['site']!=site]
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('key',('timing_denominator_paths','normalization_paths','division_callees_paths','viridian_armadillo_paths'))
def test_identical_primary_retains_every_full_helper_and_existing_viridian_caller_original(original,key):
    record=deepcopy(original[1]);record['candidate']['witness'].pop(key)
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_component_retains_all_exact_alias_absence_and_fixed_premises(original):
    result=proof.require_primary(original[0],original[1])
    for flag in ('no_selected_ram_datum_access','complete_timing_helpers_same_primary',
            'complete_normalization_helpers_same_primary','complete_direct_helpers_same_primary','complete_viridian_caller_same_primary'):
        assert result[flag] is True
    assert len(result['conditional_branch_outcomes'])==31 and len(result['fixed_divisor_outcomes'])==7
    assert result['selected_native_RAM_aliases']=={'ffff110e':'0100110e','ffff178e':'0100178e',
        'ffff2733':'01002733','ffff3348':'01003348','ffff35a0':'010035a0','ffff35b6':'010035b6'}
