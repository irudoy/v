"""Actual original threshold window reader caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import threshold_window_reader_withdrawal_contract as contract,threshold_window_reader_withdrawal_matrix as matrix
from kb import threshold_window_reader_withdrawal_capture_evidence as proof,threshold_window_reader_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['threshold_window_reader_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original threshold window reader caller withdrawal capture')
        pytest.skip('the complete original threshold window reader caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_threshold_window_reader_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/threshold_window_reader_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-threshold-window-reader-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    predicates={
        'state':lambda c:c['kind']=='complete-raw-register-width',
        'flag-bypass':lambda c:c['kind']=='independent-active-coordinate-flag-ratio-and-split-input' and c['byte_4251']==0,
        'lower-clip':lambda c:c['kind']=='raw-low-word-coordinate-and-complete-unsigned-measured-window' and c['raw_r4']&65535==0 and c['word_11bc']==0,
        'upper-clip':lambda c:c['kind']=='raw-low-word-coordinate-and-complete-unsigned-measured-window' and c['raw_r4']&65535==225 and c['word_11bc']==224,
        'empty-window':lambda c:c['kind']=='raw-low-word-coordinate-and-complete-unsigned-measured-window' and c['raw_r4']&65535==285 and c['word_11bc']==255,
        'zero-numerator':lambda c:c['kind']=='two-real-divider-byte-numerators-short-long-and-separate-local-reloads' and c['raw_r5']&255==0 and c['byte_413e']==0,
        'long-divider':lambda c:c['kind']=='two-real-divider-byte-numerators-short-long-and-separate-local-reloads' and c['raw_r5']&255==214 and c['byte_413e']==255,
        'high-split':lambda c:c['kind']=='independent110-split-and-held-byte-agreement' and c['raw_r6']&255==110 and c['byte_3fa4']==110,
        'split-mismatch':lambda c:c['kind']=='independent110-split-and-held-byte-agreement' and c['raw_r6']&255==109 and c['byte_3fa4']==110}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x8489A}


@pytest.mark.parametrize('name',('state', 'flag-bypass', 'lower-clip', 'upper-clip', 'empty-window', 'zero-numerator', 'long-divider', 'high-split', 'split-mismatch'))
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


@pytest.mark.parametrize('name',('state', 'flag-bypass', 'lower-clip', 'upper-clip', 'empty-window', 'zero-numerator', 'long-divider', 'high-split', 'split-mismatch'))
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


@pytest.mark.parametrize('name',('state', 'flag-bypass', 'lower-clip', 'upper-clip', 'empty-window', 'zero-numerator', 'long-divider', 'high-split', 'split-mismatch'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'flag-bypass', 'lower-clip', 'upper-clip', 'empty-window', 'zero-numerator', 'long-divider', 'high-split', 'split-mismatch'))
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


def test_actual_local_byte_and_two_dwords_keep_their_ordered_preimages_and_reloads(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['state']
    sites=(0x847F0,0x84836,0x84838,0x84844,0x84850,0x84852,0x84862)
    rows=[next(row for row in result['accesses'] if row['site']==site) for site in sites]
    assert [(row['mode'],row['width_bytes'],row['bytes']) for row in rows]==[
        ('write',1,'64'),('read',1,'64'),('write',4,'00000064'),('read',4,'00000064'),
        ('read',1,'64'),('write',4,'00000064'),('read',4,'00000064')]
    assert [row['address']-observed['sp'] for row in rows]==[-25,-25,-20,-20,-25,-24,-24]


@pytest.mark.parametrize('site',(0x847F0,0x84836,0x84838,0x84844,0x84850,0x84852,0x84862))
@pytest.mark.parametrize('fault',('omit','bytes','address','width'))
def test_terminal_frame_cannot_replace_any_real_local_byte_or_dword_operand(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['state'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(index for index,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    elif fault=='bytes':result['accesses'][index]['bytes']='changed'
    elif fault=='width':result['accesses'][index]['width_bytes']=8
    else:result['accesses'][index]['address']+=4
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_actual_two_real_divisions_keep_distinct_post_delay_numerators_and_long_return(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['long-divider']
    calls=result['calls'];assert len(calls)==len(value['calls'])==2
    assert [(row['site'],row['target'],row['return_address']) for row in calls]==[
        (0x84840,0x21BBC,0x84844),(0x8485E,0x21BBC,0x84862)]
    assert [(row['entry']['registers'][0],row['entry']['registers'][1]) for row in calls]==[(10,1712),(10,2568)]
    assert [row['long_path'] for row in value['calls']]==[False,True]
    assert [row['return_registers'][0] for row in value['calls']]==[171,256]
    assert observed['exit'][-1]==1 and result['ram']==observed['memory_before'][0]


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_input_echo_or_changed_write_set_cannot_replace_changed_actual_boolean_return(windows,monkeypatch,fault):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x847DC:('byte_4251',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x4251]=index;observed['memory_before']=(bytes(before),)
        if fault=='input-echo':publications[index]={(0x01004251,1):bytes([index])}
        elif fault=='write-set-only':publications[index]={(0x01004A45+index,1):bytes(1)}
        else:publications[index]={(0x01004A45,1):bytes(1)}
    if fault=='missing-publications':publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_fixed_other_changed_actual_R0_is_required_without_any_real_RAM_publication(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x847DC:('byte_4251',)})
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x4251]=index;observed['memory_before']=(bytes(before),)
        observed['exit']=(*observed['exit'][:-1],index)
    proof.require_positive_alternatives(actual,declared,{0:{},1:{}})
    for case,observed,result,value in selected.values():assert proof.computed_publications(observed,result)=={}


def test_component_requires_both_previous_full_helper_originals_and_all_exact_native_aliases(original):
    result=proof.require_primary(original[0],original[1])
    assert result['complete_direct_helpers_same_primary'] is True
    assert result['complete_previous_byte_curve_caller_same_primary'] is True
    assert result['no_selected_ram_datum_access'] is True
    assert result['selected_native_RAM_aliases']=={'ffff4a45':'01004a45','ffff4a70':'01004a70','ffff4ac6':'01004ac6'}
    assert len(result['conditional_branch_outcomes'])==15
    assert result['fixed_branch_outcomes']=={f'{site:08x}':[outcome] for site,outcome in proof.FIXED_BRANCHES.items()}
