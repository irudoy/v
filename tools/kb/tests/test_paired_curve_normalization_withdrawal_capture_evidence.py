"""Actual original paired curve normalization callers withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import paired_curve_normalization_withdrawal_contract as contract,paired_curve_normalization_withdrawal_matrix as matrix
from kb import paired_curve_normalization_withdrawal_capture_evidence as proof,paired_curve_normalization_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['paired_curve_normalization_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original paired curve normalization callers withdrawal capture')
        pytest.skip('the complete original paired curve normalization callers withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_paired_curve_normalization_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/paired_curve_normalization_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-paired-curve-normalization-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    predicates={
        'state':lambda c:c['entry']==0x655B4 and c['kind']=='complete-raw-register-width',
        'second':lambda c:c['entry']==0x65B08 and c['kind']=='complete-raw-register-width',
        'alternate-first':lambda c:c['entry']==0x655B4 and c['kind']=='independent-active-flag-signed-byte-word-and-normalization-input' and c['config_8710']==32 and c['word_11a0']!=c['word_119e'],
        'equal-copy':lambda c:c['entry']==0x655B4 and c['kind']=='independent-active-flag-signed-byte-word-and-normalization-input' and c['config_8710']==32 and c['word_11a0']==c['word_119e'],
        'alternate-second':lambda c:c['entry']==0x65B08 and c['kind']=='independent-active-flag-signed-byte-word-and-normalization-input' and c['config_8710']==32,
        'positive-first':lambda c:c['entry']==0x655B4 and c['kind']=='real-positive-and-negative-ratio-saturation-with-unit-divisor' and c['word_18cc']==32767,
        'negative-first':lambda c:c['entry']==0x655B4 and c['kind']=='real-positive-and-negative-ratio-saturation-with-unit-divisor' and c['word_18cc']==32768,
        'positive-second':lambda c:c['entry']==0x65B08 and c['kind']=='real-positive-and-negative-ratio-saturation-with-unit-divisor' and c['word_18cc']==32767,
        'negative-second':lambda c:c['entry']==0x65B08 and c['kind']=='real-positive-and-negative-ratio-saturation-with-unit-divisor' and c['word_18cc']==32768,
        'endpoint':lambda c:c['entry']==0x655B4 and c['kind']=='full-byte-coordinate-and-natural-descending-axis-scan' and c['byte_2404']==128,
        'unordered':lambda c:c['entry']==0x65B08 and c['kind']=='complete-unordered-raw-axis-and-byte-data-preimages'}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x656FE,0x65C22}


@pytest.mark.parametrize('name',('state', 'second', 'alternate-first', 'equal-copy', 'alternate-second', 'positive-first', 'negative-first', 'positive-second', 'negative-second', 'endpoint', 'unordered'))
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


@pytest.mark.parametrize('name',('state', 'second', 'alternate-first', 'equal-copy', 'alternate-second', 'positive-first', 'negative-first', 'positive-second', 'negative-second', 'endpoint', 'unordered'))
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


@pytest.mark.parametrize('name',('state', 'second', 'alternate-first', 'equal-copy', 'alternate-second', 'positive-first', 'negative-first', 'positive-second', 'negative-second', 'endpoint', 'unordered'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'second', 'alternate-first', 'equal-copy', 'alternate-second', 'positive-first', 'negative-first', 'positive-second', 'negative-second', 'endpoint', 'unordered'))
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


@pytest.mark.parametrize('name,sites',(('state',(0x65602,0x65612,0x65608,0x65640)),
    ('second',(0x65B52,0x65B6A,0x65B60,0x65B96))))
def test_actual_saved_coordinate_and_first_coefficient_keep_two_distinct_byte_carriers(windows,name,sites):
    _,_,_,selected=windows;case,observed,result,value=selected[name]
    rows=[next(row for row in result['accesses'] if row['site']==site) for site in sites]
    assert [row['mode'] for row in rows]==['write','read','write','read']
    assert [row['width_bytes'] for row in rows]==[1,1,1,1]
    assert [row['address']-observed['sp'] for row in rows]==[-28,-28,-24,-24]
    assert rows[0]['bytes']==rows[1]['bytes'] and rows[2]['bytes']==rows[3]['bytes']


@pytest.mark.parametrize('name,site',(('state',0x65602),('state',0x65612),('state',0x65608),('state',0x65640),
    ('second',0x65B52),('second',0x65B6A),('second',0x65B60),('second',0x65B96)))
@pytest.mark.parametrize('fault',('omit','bytes','address','width'))
def test_terminal_frame_cannot_replace_either_saved_byte_or_its_real_reload(windows,name,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(index for index,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    elif fault=='bytes':result['accesses'][index]['bytes']='changed'
    elif fault=='width':result['accesses'][index]['width_bytes']=4
    else:result['accesses'][index]['address']+=4
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_endpoint_reads_the_seventeenth_physical_data_byte_before_the_sixteenth_current_byte(windows):
    _,_,_,selected=windows;_,_,result,value=selected['endpoint']
    reads=[row for row in result['accesses'] if row['site'] in (0x264B2,0x264B8)]
    assert [(row['site'],row['address'],row['width_bytes']) for row in reads]==[
        (0x264B2,0x11D34,1),(0x264B8,0x11D33,1),(0x264B2,0x11D34,1),(0x264B8,0x11D33,1)]
    assert all(row['index']==15 and row['fraction']==0 for row in value['lookups'] if row['kind']=='byte-curve')


@pytest.mark.parametrize('name,at,site,wanted',(('positive-first',0x18D4,0x656F2,32767),
    ('negative-first',0x18D4,0x656F2,32768),('positive-second',0x18CE,0x65C16,32767),
    ('negative-second',0x18CE,0x65C16,32768)))
def test_both_actual_signed_word_saturation_outcomes_bind_the_real_RAM_publication(windows,name,at,site,wanted):
    _,_,_,selected=windows;case,observed,result,value=selected[name]
    call=next(row for row in result['calls'] if row['target']==0x21BBC)
    signed=case['word_18cc']-65536 if case['word_18cc']&32768 else case['word_18cc']
    assert call['entry']['registers'][:2]==(1,(signed*256)&0xFFFFFFFF)
    writes=[row for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write']
    assert [(row['site'],row['address'],row['width_bytes'],row['bytes']) for row in writes]==[(site,0x01000000+at,2,f'{wanted:04x}')]
    assert observed['memory_after'][0][at:at+2]==wanted.to_bytes(2,'big')
    assert observed['exit'][-1]==(0x648 if case['entry']==0x655B4 else 0x642)


def test_equal_word_alternate_mode_copies_the_other_actual_publication_without_a_helper(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['equal-copy']
    assert not result['calls'] and observed['memory_after'][0][0x18D4:0x18D6]==case['word_18ce'].to_bytes(2,'big')
    read=next(row for row in result['accesses'] if row['site']==0x65672)
    assert (read['address'],read['width_bytes'])==(0x010018CE,2)


def test_all_actual_causal_inputs_require_a_changed_common_computed_word_with_fixed_other_preimages(windows):
    declared,_,actual,_=windows
    publications={}
    for index,observed in enumerate(actual):
        at=0x18D4 if observed['entry']==0x655B4 else 0x18CE
        publications[index]={(matrix.RAM_BASE+at,2):observed['memory_after'][0][at:at+2]}
    proof.require_positive_alternatives(actual,declared,publications)
    unchanged={index:{key:bytes(len(raw)) for key,raw in rows.items()} for index,rows in publications.items()}
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,unchanged)


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_common_computed_publication_alternatives_refuse_input_echo_or_only_a_new_write_set(windows,monkeypatch,fault):
    declared,_,_,selected=windows;base=selected['state'][1];actual=[deepcopy(base),deepcopy(base)]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x655B4:('byte_12df',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x12DF]=index;observed['memory_before']=(bytes(before),)
        if fault=='input-echo':publications[index]={(0x010012DF,1):bytes([index])}
        elif fault=='write-set-only':publications[index]={(0x010018D4+index,1):bytes(1)}
        else:publications[index]={(0x010018D4,1):bytes(1)}
    if fault=='missing-publications':publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_common_actual_publication_must_change_value_outside_the_controlled_RAM_input(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x655B4:('byte_12df',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x12DF]=index;observed['memory_before']=(bytes(before),)
        publications[index]={(0x010018D4,1):bytes([index])}
    proof.require_positive_alternatives(actual,declared,publications)


def test_computed_publication_bindings_use_real_writes_and_actual_final_memory(windows):
    _,_,_,selected=windows;_,observed,result,_=selected['state'];publications=proof.computed_publications(observed,result)
    assert publications and all(raw==observed['memory_after'][0][address-matrix.RAM_BASE:address-matrix.RAM_BASE+width]
        for (address,width),raw in publications.items())
    assert (0x010018D4,2) in publications


@pytest.mark.parametrize('component',('division_callees_paths','byte_curve_caller_withdrawal_paths','mixed_curve_caller_withdrawal_paths'))
def test_identical_primary_requires_each_complete_previous_direct_byte_and_mixed_original(original,component):
    record=deepcopy(original[1]);record['candidate']['witness'].pop(component)
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_component_retains_both_full_previous_curve_originals_and_all_actual_fixed_premises(original):
    result=proof.require_primary(original[0],original[1])
    assert all(result[key] is True for key in ('complete_direct_helpers_same_primary',
        'complete_previous_byte_curve_caller_same_primary','complete_previous_mixed_curve_caller_same_primary','complete_raw16_axis17_data'))
    assert result['selected_native_RAM_aliases']=={} and len(result['conditional_branch_outcomes'])==28
    assert result['fixed_branch_outcomes']=={f'{site:08x}':[outcome] for site,outcome in proof.FIXED_BRANCHES.items()}
