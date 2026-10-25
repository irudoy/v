"""Actual original mixed curve caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import mixed_curve_caller_withdrawal_contract as contract,mixed_curve_caller_withdrawal_matrix as matrix
from kb import mixed_curve_caller_withdrawal_capture_evidence as proof,mixed_curve_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['mixed_curve_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original mixed curve caller withdrawal capture')
        pytest.skip('the complete original mixed curve caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_mixed_curve_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/mixed_curve_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-mixed-curve-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    predicates={
        'implicit-low':lambda c:c['kind']=='word-product-shift-each-cap-and-implicit-domain' and c['word_1e60']==512 and c['word_114e']==1 and c['word_120e']==0,
        'implicit-high':lambda c:c['kind']=='word-product-shift-each-cap-and-implicit-domain' and c['word_1e60']==512 and c['word_114e']==65535 and c['word_120e']==0,
        'signed-word':lambda c:c['kind']=='zero-word-large-positive-divisor-and-full-signed-numerator' and c['word_1752']==512 and c['word_2266']==32768 and c['byte_1765']==0,
        'signed-large':lambda c:c['kind']=='zero-word-large-positive-divisor-and-full-signed-numerator' and c['word_1752']==65535 and c['word_2266']==32768 and c['byte_1765']==255,
        'zero-positive':lambda c:c['kind']=='zero-word-large-positive-divisor-and-full-signed-numerator' and c['word_1752']==0 and c['word_2266']==0 and c['byte_1765']==0,
        'timing':lambda c:c['entry']==0x4BDC2,
        'surface-corner':lambda c:c['kind']=='independent-zero-fraction-and-full-surface-corner-paths' and c['word_10ca']==0 and c['word_1024']==0,
        'byte-endpoint':lambda c:c['entry']==0x4BDC2 and c['kind']=='independent-complete-RAM-or-configuration-input' and c['byte_106f']==255,
        'scale':lambda c:c['entry']==0x659AE,
        'upper-clamp':lambda c:c['kind']=='independent-products-weight-bypasses-and-both-signed16-clamp-boundaries' and c['word_18e4']==16384 and c['gain_byte']==0 and c['word_2408']==65535 and c['word_18ca']==32767 and c['byte_15eb']==0 and c['byte_2485']==0,
        'lower-clamp':lambda c:c['kind']=='independent-products-weight-bypasses-and-both-signed16-clamp-boundaries' and c['word_18e4']==0 and c['gain_byte']==255 and c['word_2408']==65535 and c['word_18ca']==32767 and c['byte_15eb']==0 and c['byte_2485']==0}
    for name,predicate in predicates.items():
        case=next(row for row in declared['cases'] if predicate(row))
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x3B51C,0x41E3C,0x4BEEE,0x65A8E}


@pytest.mark.parametrize('name',('implicit-low', 'implicit-high', 'signed-word', 'signed-large', 'zero-positive', 'timing', 'surface-corner', 'byte-endpoint', 'scale', 'upper-clamp', 'lower-clamp'))
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


@pytest.mark.parametrize('name',('implicit-low', 'implicit-high', 'signed-word', 'signed-large', 'zero-positive', 'timing', 'surface-corner', 'byte-endpoint', 'scale', 'upper-clamp', 'lower-clamp'))
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


@pytest.mark.parametrize('name',('implicit-low', 'implicit-high', 'signed-word', 'signed-large', 'zero-positive', 'timing', 'surface-corner', 'byte-endpoint', 'scale', 'upper-clamp', 'lower-clamp'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_surface_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for at,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][at]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('implicit-low','implicit-high','signed-word','signed-large','timing','surface-corner','byte-endpoint','scale','upper-clamp','lower-clamp'))
@pytest.mark.parametrize('fault',('R0','R1','R2','R3','R4','R5','R6','R7','R8','R9','R10','R11','R12','R13','R14','SP','PR','GBR','MACH','MACL','SR','target'))
def test_every_real_helper_keeps_complete_actual_post_delay_input(windows,name,fault):
    declared,image,_,selected=windows
    for index in range(len(selected[name][2]['calls'])):
        case,observed,result,value=deepcopy(selected[name]);call=result['calls'][index]
        fixture,_=contract.fixture_for_case(declared['source'],image,case)
        if fault.startswith('R') and fault[1:].isdigit():
            registers=list(call['entry']['registers']);registers[int(fault[1:])]^=1;call['entry']['registers']=tuple(registers)
        elif fault=='target':call['target']^=2
        else:call['entry'][fault.lower()]^=0x10 if fault=='SR' else 1
        with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('field',('registers','gbr','mach','macl','sr','pr'))
@pytest.mark.parametrize('phase',('before','after'))
def test_complete_actual_intermediate_CPU_cannot_detach_from_trace_continuity(windows,field,phase):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['timing'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    for index in (0,len(result['trace'])//2,len(result['trace'])-1):
        changed=deepcopy(result);state=changed['trace'][index][phase]
        if field=='registers':state[field]=(state[field][0]^1,*state[field][1:])
        else:state[field]^=1
        with pytest.raises(ValueError):transfers.require(observed,changed,value,fixture)


def test_actual_implicit_literals_select_two_disjoint_caller_reachable_ranges(windows):
    _,_,_,selected=windows
    for name,base,coordinate,first,last in (('implicit-low',0x15042,4,0x15042,0x15062),
            ('implicit-high',0x15022,0xC3FF,0x15022,0x1503E)):
        _,_,result,value=selected[name]
        call=next(row for row in result['calls'] if row['site']==0x3B500)
        assert call['target']==0x263F4 and call['entry']['registers'][4:6]==(base,coordinate)
        reads=[row for row in result['accesses'] if row['site'] in (0x26AA0,0x26AA2)]
        assert len(reads)==2 and all(first<=row['address'] and row['address']+2<=last for row in reads)
        assert not any(row['site'] in (0x26402,0x26404) for row in result['trace'])


def test_complete_local_halfword_is_read_as_full_word_after_real_helper_delay_slots(windows):
    _,_,_,selected=windows;_,observed,result,value=selected['timing']
    write=next(row for row in result['accesses'] if row['site']==0x4BE48)
    read=next(row for row in result['accesses'] if row['site']==0x26286)
    assert write['mode']=='write' and write['width_bytes']==2 and write['address']==observed['sp']-22
    assert read['mode']=='read' and read['width_bytes']==4 and read['address']==observed['sp']-24
    assert bytes.fromhex(read['bytes'])[2:]==bytes.fromhex(write['bytes'])
    assert bytes.fromhex(read['bytes'])[:2]==observed['frame_before'][136:138]
    surface=next(row for row in value['lookups'] if row['kind']=='word-surface')
    assert surface['complete_inner_argument_word']==int(read['bytes'],16)
    assert surface['inner_coordinate']==int(write['bytes'],16)


@pytest.mark.parametrize('site',(0x4BE48,0x26286,0x26280,0x26282,0x2628E,0x26290,0x65A1A,0x65A58))
@pytest.mark.parametrize('fault',('omit','bytes','address','width'))
def test_identical_final_frames_cannot_replace_intermediate_saved_argument_lineage(windows,site,fault):
    declared,image,_,selected=windows
    case,observed,result,value=deepcopy(selected['scale' if site in (0x65A1A,0x65A58) else 'timing'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    else:
        row=result['accesses'][index]
        if fault=='bytes':row['bytes']='00'*row['width_bytes']
        elif fault=='width':row['width_bytes']=1
        else:row['address']+=4
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_timing_retains_actual_unselected_134A_write_and_real_unsigned_large_divider(windows):
    _,_,_,selected=windows;_,_,result,value=selected['timing']
    divider=next(row for row in result['calls'] if row['site']==0x4BE80)
    assert divider['target']==0x21CE0 and divider['entry']['registers'][0]==500000
    assert any(row['site']==0x21CEA and row['kind']=='taken' for row in result['branches'])
    write=next(row for row in result['accesses'] if row['site']==0x4BE92)
    assert (write['mode'],write['address'],write['width_bytes'])==('write',0x0100134A,1)
    assert all(native!=0xFFFF134A for identity,native,alias in transfers.NATIVE_ROOTS)


@pytest.mark.parametrize('component',('timing_division_paths','rugged_gerbil_paths','register_only_helper_paths','division_callees_paths'))
def test_identical_primary_requires_each_full_original_helper_and_generic_endpoint(original,component):
    record=deepcopy(original[1]);record['candidate']['witness'].pop(component)
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_component_retains_full_helper_originals_and_all_actual_fixed_premises(original):
    result=proof.require_primary(original[0],original[1])
    assert all(result[key] is True for key in ('complete_direct_helpers_same_primary','complete_timing_helpers_same_primary',
        'complete_implicit_caller_same_primary','complete_register_helpers_same_primary','no_selected_datum_access'))
    assert result['selected_native_RAM_aliases']=={}
    assert len(result['conditional_branch_outcomes'])==44 and result['fixed_divisor_outcomes']=={
        '00021bc0':['fallthrough'],'00021bca':['taken'],'00021ce4':['fallthrough'],'00021cea':['taken'],
        '000263fa':['fallthrough'],'00026a9a':['fallthrough'],'00026c7a':['fallthrough']}
