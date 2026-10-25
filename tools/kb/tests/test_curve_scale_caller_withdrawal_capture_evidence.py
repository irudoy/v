"""Actual original curve scale caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import curve_scale_caller_withdrawal_contract as contract,curve_scale_caller_withdrawal_matrix as matrix
from kb import curve_scale_caller_withdrawal_capture_evidence as proof,curve_scale_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['curve_scale_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original curve scale caller withdrawal capture')
        pytest.skip('the complete original curve scale caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_curve_scale_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/curve_scale_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-curve-scale-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    for name in ('curve-interior', 'curve-descending', 'axis-floor', 'axis-endpoint', 'upper-saturation', 'lower-saturation', 'nonnegative-floor', 'gain-zero'):
        case=next(row for row in declared['cases'] if row['kind']==name)
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0xB77E6}


@pytest.mark.parametrize('name',('curve-interior', 'curve-descending', 'axis-floor', 'axis-endpoint', 'upper-saturation', 'lower-saturation', 'nonnegative-floor', 'gain-zero'))
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


@pytest.mark.parametrize('name',('curve-interior','curve-descending','axis-floor','upper-saturation'))
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


@pytest.mark.parametrize('offset',range(66))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_byte_of_the_complete_physical_curve_and_neighbor_is_exact(windows,offset,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['curve-interior'])
    raw=bytearray(observed[phase][0x14B0A]);raw[offset]^=1;observed[phase][0x14B0A]=bytes(raw)
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('offset',range(64))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_byte_of_the_exact32_word_axis_is_bound(windows,offset,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['axis-floor'])
    raw=bytearray(observed[phase][0x13FF4]);raw[offset]^=1;observed[phase][0x13FF4]=bytes(raw)
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('offset',range(4))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_signed_comparison_constant_remains_immutable_and_unrelocated(windows,offset,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['lower-saturation'])
    assert observed[phase][0xB7970]==bytes.fromhex('ffff6c78')
    raw=bytearray(observed[phase][0xB7970]);raw[offset]^=1;observed[phase][0xB7970]=bytes(raw)
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('curve-interior','curve-descending','axis-floor','axis-endpoint','upper-saturation','lower-saturation'))
@pytest.mark.parametrize('fault',('R0','R1','R2','R3','R4','R5','R6','R7','SP','PR','GBR','MACH','MACL','SR','target'))
def test_every_curve_axis_fraction_and_signed_call_has_complete_post_delay_inputs(windows,name,fault):
    declared,image,_,selected=windows
    for index in range(len(selected[name][2]['calls'])):
        case,observed,result,value=deepcopy(selected[name]);call=result['calls'][index]
        fixture,_=contract.fixture_for_case(declared['source'],image,case)
        if fault.startswith('R') and fault[1:].isdigit():
            registers=list(call['entry']['registers']);registers[int(fault[1:])]^=1;call['entry']['registers']=tuple(registers)
        elif fault=='target':call['target']^=2
        else:call['entry'][fault.lower()]^=0x10 if fault=='SR' else 1
        with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_actual_curve_axis_call_uses32_words_and_the_signed_call_uses_the_original_raw_dividend(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['curve-interior']
    axis=next(row for row in result['calls'] if row['site']==0x2652E)
    assert axis['target']==0x26984 and axis['entry']['registers'][4]==62
    assert axis['entry']['registers'][0]==0x13FF4 and axis['entry']['registers'][5]==case['raw_r4']&65535
    divide=next(row for row in result['calls'] if row['site']==0xB7788)
    assert divide['entry']['registers'][:2]==(10000,case['raw_r5'])
    assert divide['entry']['registers'][1]!=value['curve_value']
    for write_site,read_site,depth,width in ((0xB7770,0xB778A,24,4),(0xB7780,0xB778E,17,1),(0xB7782,0xB77C4,16,2)):
        write=next(row for row in result['accesses'] if row['site']==write_site)
        read=next(row for row in result['accesses'] if row['site']==read_site)
        assert write['address']==read['address']==observed['sp']-depth
        assert write['width_bytes']==read['width_bytes']==width and write['bytes']==read['bytes']


def test_descending_curve_value_is_read_before_signed_division_overwrites_the_same_frame_word(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['curve-descending']
    rows=[row for row in result['accesses'] if row['site'] in (0x26744,0x26752,0x21BBC)]
    divide=next(row for row in result['calls'] if row['site']==0xB7788)
    assert [(row['site'],row['address']) for row in rows]==[(0x26744,observed['sp']-28),
        (0x26752,observed['sp']-28),(0x21BBC,observed['sp']-28)]
    assert rows[0]['bytes']==rows[1]['bytes']=='0000ffff'
    assert rows[2]['bytes']==divide['entry']['registers'][2].to_bytes(4,'big').hex()!=rows[0]['bytes']


@pytest.mark.parametrize('fault',('omit-first-save','replace-with-final','omit-first-read','replace-dividend-with-lookup'))
def test_identical_final_state_cannot_replace_intermediate_curve_save_or_argument_lineage(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['curve-descending'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='replace-dividend-with-lookup':
        call=next(row for row in result['calls'] if row['site']==0xB7788)
        registers=list(call['entry']['registers']);registers[1]=value['curve_value'];call['entry']['registers']=tuple(registers)
    else:
        site=0x26752 if fault=='omit-first-read' else 0x26744
        index=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
        if fault=='replace-with-final':
            result['accesses'][index]['bytes']=next(row for row in result['accesses'] if row['site']==0x21BBC)['bytes']
        else:result['accesses'].pop(index)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('key',('uptight_duck_paths','division_callees_paths'))
def test_identical_primary_retains_both_full_neighbor_and_division_originals(original,key):
    record=deepcopy(original[1]);record['candidate']['witness'].pop(key)
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_component_retains_exact_native_alias_absence_and_all_fixed_divisor_premises(original):
    result=proof.require_primary(original[0],original[1])
    assert result['no_selected_ram_datum_access'] is True
    assert result['complete_curve_helpers_same_primary'] is True and result['complete_direct_helpers_same_primary'] is True
    assert result['selected_native_RAM_aliases']=={'ffff2733':'01002733','ffff3348':'01003348'}
    assert result['fixed_divisor_outcomes']=={'00026c7a':['fallthrough'],'00021bc0':['fallthrough'],
        '00021bca':['taken'],'00021bdc':['fallthrough']}
    assert result['complete_uptight_RAM3348_same_primary'] is True
    assert result['uptight_RAM3348_withdrawal_original']==owning.UPTIGHT_RAM3348_WITHDRAWAL[1]
    assert result['uptight_RAM3348_original_stdout_sha256']==result['curve_helper_original_stdout_sha256']


@pytest.mark.parametrize('flag',('no_selected_RAM3348_access','prior3348_complete_state_independence'))
def test_existing_same_primary_neighbor_cannot_donate_RAM3348_absence_without_its_complete_prior_result(original,monkeypatch,flag):
    require=proof.curve_helpers.require_primary
    def changed(model,record):
        result=dict(require(model,record));result[flag]=False;return result
    monkeypatch.setattr(proof.curve_helpers,'require_primary',changed)
    with pytest.raises(ValueError):proof.require_primary(original[0],original[1])
