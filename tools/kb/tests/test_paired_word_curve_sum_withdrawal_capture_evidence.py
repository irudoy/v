"""Actual original paired word curve sum withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import paired_word_curve_sum_withdrawal_contract as contract,paired_word_curve_sum_withdrawal_matrix as matrix
from kb import paired_word_curve_sum_withdrawal_capture_evidence as proof,paired_word_curve_sum_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['paired_word_curve_sum_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original paired word curve sum withdrawal capture')
        pytest.skip('the complete original paired word curve sum withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_paired_word_curve_sum_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/paired_word_curve_sum_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-paired-word-curve-sum-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
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
        'direct':lambda c:c['kind']=='complete-independent-RAM-operand-or-prior-state' and c['byte_24d2']==0 and c['word_120e']==0,
        'floor':lambda c:c['kind']=='direct-floor-first-cap-and-second-cap-boundaries' and (c['word_183e'],c['word_1340'],c['word_120e'])==(0,0,65535),
        'first-cap':lambda c:c['kind']=='direct-floor-first-cap-and-second-cap-boundaries' and (c['word_183e'],c['word_1340'],c['word_120e'])==(65535,65535,0),
        'second-cap':lambda c:c['kind']=='direct-floor-first-cap-and-second-cap-boundaries' and (c['word_183e'],c['word_1340'],c['word_120e'])==(65535,1,4),
        'endpoint':lambda c:c['kind']=='each-knot-endpoint-neighbor-and-fraction-cell' and c['word_28bc']==63488,
        'past-endpoint':lambda c:c['kind']=='complete-flat-duplicate-descending-and-nonmonotonic-axis' and c['axis_word_00']==0 and c['axis_word_01']==2048 and c['word_28bc']==65535,
        'below-flat':lambda c:c['kind']=='complete-flat-duplicate-descending-and-nonmonotonic-axis' and all(c[name]==1000 for name in matrix.AXIS_FIELDS) and c['word_28bc']==0,
        'equal-flat':lambda c:c['kind']=='complete-flat-duplicate-descending-and-nonmonotonic-axis' and all(c[name]==1000 for name in matrix.AXIS_FIELDS) and c['word_28bc']==1000,
        'fraction':lambda c:c['kind']=='each-knot-endpoint-neighbor-and-fraction-cell' and c['word_28bc']==1024,
        'curve-below-cap':lambda c:c['kind']=='two-real-curve-result-sum-cap' and c['curve_word_00']==32767,
        'curve-above-cap':lambda c:c['kind']=='two-real-curve-result-sum-cap' and c['curve_word_00']==32768,
        'ascending':lambda c:c['kind']=='both-interpolation-directions-full-word-domain' and c['curve_word_00']==0,
        'descending':lambda c:c['kind']=='both-interpolation-directions-full-word-domain' and c['curve_word_00']==65535}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x72CF0}


@pytest.mark.parametrize('name',('state', 'direct', 'floor', 'first-cap', 'second-cap', 'endpoint', 'past-endpoint', 'below-flat', 'equal-flat', 'fraction', 'curve-below-cap', 'curve-above-cap', 'ascending', 'descending'))
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


@pytest.mark.parametrize('name',('state', 'direct', 'floor', 'first-cap', 'second-cap', 'endpoint', 'past-endpoint', 'below-flat', 'equal-flat', 'fraction', 'curve-below-cap', 'curve-above-cap', 'ascending', 'descending'))
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


@pytest.mark.parametrize('name',('state', 'direct', 'floor', 'first-cap', 'second-cap', 'endpoint', 'past-endpoint', 'below-flat', 'equal-flat', 'fraction', 'curve-below-cap', 'curve-above-cap', 'ascending', 'descending'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'direct', 'floor', 'first-cap', 'second-cap', 'endpoint', 'past-endpoint', 'below-flat', 'equal-flat', 'fraction', 'curve-below-cap', 'curve-above-cap', 'ascending', 'descending'))
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


def test_direct_and_alternate_paths_keep_two_distinct_ordered_full_word_publications(windows):
    for name,(case,observed,result,value) in windows[3].items():
        rows=[row for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write']
        first_site=0x72CE0 if value['alternate'] else 0x72C8C
        assert [(row['site'],row['address'],row['width_bytes']) for row in rows]==[
            (first_site,0x010019B2,2),(0x72CE4,0x010019B6,2)]
        assert observed['memory_after'][0][0x19B2:0x19B4]==value['first_output'].to_bytes(2,'big')
        assert observed['memory_after'][0][0x19B6:0x19B8]==value['second_output'].to_bytes(2,'big')
        assert observed['exit'][-1]==value['output']==0x72A
        assert result['registers'][5]==(0xFFFFFFFF if value['alternate'] else 65535)
    for name,first,second in (('direct',1500,1200),('floor',0,0),('first-cap',65535,65535),
            ('second-cap',65535,65535),('curve-below-cap',65534,65534),('curve-above-cap',65535,65535)):
        assert (windows[3][name][3]['first_output'],windows[3][name][3]['second_output'])==(first,second)


def test_both_real_word_curve_calls_bind_complete_post_delay_coordinate_curve_and_axis_arguments(windows):
    for case,observed,result,value in windows[3].values():
        roots=[row for row in result['calls'] if row['target']==0x26524]
        if not value['alternate']:
            assert roots==[] and result['calls']==[]
            continue
        assert [row['site'] for row in roots]==[0x72CB6,0x72CC6]
        for call,coordinate in zip(roots,(case['word_28bc'],case['word_28be'])):
            assert call['entry']['registers'][4:7]==(0x13202,0x155A0,coordinate)
            at=next(i for i,row in enumerate(result['trace']) if row['site']==call['site'])
            assert result['trace'][at+1]['delay_slot'] is True
            assert result['trace'][at+1]['site']==call['site']+2
            assert result['trace'][at+2]['site']==0x26524
        axes=[row for row in result['calls'] if row['target']==0x26984]
        assert len(axes)==2
        assert all((row['entry']['registers'][0],row['entry']['registers'][4])==(0x155A0,62) for row in axes)
        for call in (row for row in result['calls'] if row['target']==0x26C78):
            assert 0<call['entry']['registers'][0]<=65535
            assert call['entry']['registers'][1]<call['entry']['registers'][0]*65536


def test_first_curve_return_survives_the_second_real_call_in_its_actual_two_byte_local_carrier(windows):
    for case,observed,result,value in windows[3].values():
        carrier=[row for row in result['accesses'] if row['site'] in (0x72CBA,0x72CCA)]
        if not value['alternate']:
            assert carrier==[]
            continue
        first=next(row for row in value['lookups'] if row['kind']=='curve')['value']
        assert [(row['site'],row['mode'],row['address'],row['width_bytes'],row['register'],row['bytes']) for row in carrier]==[
            (0x72CBA,'write',observed['sp']-24,2,0,first.to_bytes(2,'big').hex()),
            (0x72CCA,'read',observed['sp']-24,2,7,first.to_bytes(2,'big').hex())]
        sites=[row['site'] for row in result['trace']]
        assert sites.index(0x72CBA)<sites.index(0x72CC6)<sites.index(0x72CCA)
        saved=next(row for row in result['trace'] if row['site']==0x72CBA)
        assert saved['before']['registers'][0]&65535==first
        loaded=next(row for row in result['trace'] if row['site']==0x72CCA)
        assert loaded['after']['registers'][7]&65535==first


@pytest.mark.parametrize('name',('state','fraction','ascending','descending'))
@pytest.mark.parametrize('fault',('omit-save','omit-load','final-output-copy','full-word-width','wrong-local','register'))
def test_identical_final_state_cannot_replace_the_intermediate_local_word_lineage(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    at=next(i for i,row in enumerate(result['accesses']) if row['site']==(0x72CCA if fault=='omit-load' else 0x72CBA))
    if fault in ('omit-save','omit-load'):result['accesses'].pop(at)
    elif fault=='final-output-copy':result['accesses'][at]['bytes']=value['first_output'].to_bytes(2,'big').hex()
    elif fault=='full-word-width':result['accesses'][at]['width_bytes']=4
    elif fault=='wrong-local':result['accesses'][at]['address']+=2
    else:result['accesses'][at]['register']=7
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_endpoint_neighbor_has_exact_physical_bytes_without_numerical_causality_credit(windows):
    for name in ('endpoint','past-endpoint'):
        case,observed,result,value=windows[3][name]
        events=[row for row in result['accesses'] if row['site']==0x26536 and row['address']==0x13242]
        assert len(events)==1 and events[0]['width_bytes']==2
        assert events[0]['bytes']==case['curve_word_32'].to_bytes(2,'big').hex()
        curves=[row for row in value['lookups'] if row['kind']=='curve']
        assert curves[0]['index']==31 and curves[0]['fraction']==0
        assert curves[0]['value']==case['curve_word_31']
    assert 'curve_word_32' not in matrix.ENTRY_FIELDS[0x72C3C]


@pytest.mark.parametrize('name,site',(('direct',0x72C8C),('state',0x72CE0),('direct',0x72CE4),('state',0x72CE4)))
@pytest.mark.parametrize('fault',('omit','duplicate','bytes','address','width_bytes','register','mode','domain'))
def test_each_direct_or_curve_word_store_keeps_exact_site_width_bytes_and_order(windows,name,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    at=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(at)
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][at]))
    else:
        row=result['accesses'][at];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_all_actual_paths_keep_both_bytes_of_the_exact_existing_scalar_unaccessed(windows):
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='paired_word_curve_sum_withdrawal_paths']
    assert len(rows)==1 and rows[0]['original_claim_sha256']=='782329298a209bf40a282b98cc45b4be8e5a2ac28662ac911cedf461f885ba0b'
    for case,observed,result,value in windows[3].values():transfers.require_no_selected_datum(result,rows)


@pytest.mark.parametrize('address,width',((0x942B,2),(0x942C,1),(0x942D,1),(0x942D,2)))
@pytest.mark.parametrize('mode',('read','write'))
def test_actual_scalar_absence_cannot_be_replaced_by_only_first_byte_absence(windows,address,width,mode):
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='paired_word_curve_sum_withdrawal_paths']
    result=deepcopy(windows[3]['state'][2]);result['accesses'].append(dict(site=0x72C3C,mode=mode,address=address,width_bytes=width,domain='changed',register=0,bytes='00'*width))
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,rows)


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_causal_guard_requires_a_changed_common_computed_value_outside_the_controlled_input(windows,monkeypatch,fault):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x72C3C:('word_28bc',)})
    for index,row in enumerate(actual):
        memory=bytearray(row['memory_before'][0]);memory[0x28BC:0x28BE]=index.to_bytes(2,'big');row['memory_before']=(bytes(memory),)
        assert row['exit'][-1]==0x72A
    publications={0:{(0x010019B2,2):b'12'},1:{(0x010019B2,2):b'34'}}
    if fault=='input-echo':publications={i:{(0x010028BC,2):i.to_bytes(2,'big')} for i in range(2)}
    elif fault=='write-set-only':publications[1]={(0x010019B6,2):b'34'}
    elif fault=='identical-values':publications[1]=deepcopy(publications[0])
    else:publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_constant_returned_offset_requires_a_different_actual_common_word_publication(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x72C3C:('word_28bc',)})
    for index,row in enumerate(actual):
        memory=bytearray(row['memory_before'][0]);memory[0x28BC:0x28BE]=index.to_bytes(2,'big');row['memory_before']=(bytes(memory),)
        assert row['exit'][-1]==0x72A
    proof.require_positive_alternatives(actual,declared,{0:{(0x010019B2,2):b'12'},1:{(0x010019B2,2):b'34'}})


def test_complete_previous_curve_scale_original_remains_required_from_the_identical_primary(original):
    result=proof.require_primary(original[0],original[1])
    assert all(result[key] is True for key in ('complete_direct_helpers_same_primary','complete_actual_paired_word_curve_calls',
        'complete_raw_axis_and_curve','complete_two_saturated_word_publications','complete_local_word_carrier',
        'complete_selected_scalar_interval_absence','derived_request_and_area_dependencies_preserved'))
    assert result['selected_native_RAM_aliases']=={}
    assert len(result['conditional_branch_outcomes'])==11 and result['fixed_branch_outcomes']=={'00026c7a':['fallthrough']}
    record=deepcopy(original[1]);record['candidate']['witness'].pop('curve_scale_caller_withdrawal_paths')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)
