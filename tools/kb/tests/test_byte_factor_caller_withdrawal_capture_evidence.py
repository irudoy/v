"""Actual original byte factor caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import byte_factor_caller_withdrawal_contract as contract,byte_factor_caller_withdrawal_matrix as matrix
from kb import byte_factor_caller_withdrawal_capture_evidence as proof,byte_factor_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['byte_factor_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original byte factor caller withdrawal capture')
        pytest.skip('the complete original byte factor caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_byte_factor_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/byte_factor_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-byte-factor-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
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
        'override-positive':lambda c:c['kind']=='in-place-byte-override-clamp-with-complete-prior-publication' and c['byte_1657']==255 and c['config_886d']==1,
        'override-zero':lambda c:c['kind']=='in-place-byte-override-clamp-with-complete-prior-publication' and c['byte_1657']==0 and c['config_886d']==255,
        'negative-difference':lambda c:c['kind']=='full-unsigned-first-and-signed-second-word-difference' and c['word_15fc']==0 and c['word_15fe']==32767 and c['byte_2458']==0,
        'signed-difference':lambda c:c['kind']=='full-unsigned-first-and-signed-second-word-difference' and c['word_15fc']==65535 and c['word_15fe']==32768 and c['byte_2458']==0,
        'percentage-cap':lambda c:c['kind']=='complete-percentage-mode-low32-product-logical-shift14-and-byte-cap' and c['word_15fc']==65535 and c['word_15fe']==32768 and c['config_886b']==255,
        'first-endpoint':lambda c:c['kind']=='each-independent-raw-curve-cell-and-direction' and c['curve_value_15']==255,
        'second-endpoint':lambda c:c['kind']=='each-independent-raw-curve-cell-and-direction' and c['curve_value_7']==255,
        'partial-cap':lambda c:c['kind']=='complete-low-high-partial-product-and-high-term-or-final-byte-cap' and c['word_15fc']==65535 and c['word_15fe']==32768 and c['curve_value_0']==255,
        'partial-low':lambda c:c['kind']=='complete-low-high-partial-product-and-high-term-or-final-byte-cap' and c['word_15fc']==65535 and c['word_15fe']==0 and c['curve_value_0']==1}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x4BB66}


@pytest.mark.parametrize('name',('state', 'override-positive', 'override-zero', 'negative-difference', 'signed-difference', 'percentage-cap', 'first-endpoint', 'second-endpoint', 'partial-cap', 'partial-low'))
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


@pytest.mark.parametrize('name',('state', 'override-positive', 'override-zero', 'negative-difference', 'signed-difference', 'percentage-cap', 'first-endpoint', 'second-endpoint', 'partial-cap', 'partial-low'))
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


@pytest.mark.parametrize('name',('state', 'override-positive', 'override-zero', 'negative-difference', 'signed-difference', 'percentage-cap', 'first-endpoint', 'second-endpoint', 'partial-cap', 'partial-low'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'override-positive', 'override-zero', 'negative-difference', 'signed-difference', 'percentage-cap', 'first-endpoint', 'second-endpoint', 'partial-cap', 'partial-low'))
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


def test_actual_signed_word_difference_and_both_natural_curve_calls_preserve_complete_argument_state(windows):
    _,_,_,selected=windows;_,observed,result,value=selected['signed-difference']
    calls=[row for row in result['calls'] if row['site'] in (0x4BADE,0x4BB0C)]
    assert [(row['site'],row['target'],row['entry']['registers'][4]) for row in calls]==[
        (0x4BADE,0x26370,0x126A8),(0x4BB0C,0x26370,0x126A0)]
    assert all(row['entry']['registers'][14]==98303 for row in calls)
    first=next(row for row in result['accesses'] if row['site']==0x4BA7C)
    second=next(row for row in result['accesses'] if row['site']==0x4BA82)
    assert (first['bytes'],second['bytes'])==('ffff','8000')
    assert value['mode']=='curves' and observed['frame_after']==value['frame']==result['frame']


def test_actual_percentage_delay_slot_store_and_common_return_store_remain_distinct(windows):
    _,_,_,selected=windows
    for name,site,delay,raw in (('percentage-cap',0x4BABE,True,'ff'),('override-positive',0x4BB5E,False,'fd'),
            ('override-zero',0x4BB5E,False,'00'),('partial-cap',0x4BB5E,False,'ff')):
        _,observed,result,value=selected[name]
        rows=[row for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write' and row['address']==0x01001657]
        assert [(row['site'],row['width_bytes'],row['bytes']) for row in rows]==[(site,1,raw)]
        assert next(row for row in result['trace'] if row['site']==site)['delay_slot'] is delay
        assert observed['exit'][-1]==0x3CB and value['known_registers'][0]==0x3CB


@pytest.mark.parametrize('name,site',(('percentage-cap',0x4BABE),('override-positive',0x4BB5E),('state',0x4BAE6),('state',0x4BB14)))
@pytest.mark.parametrize('fault',('omit','duplicate','bytes','address','width_bytes','register','mode','domain'))
def test_each_real_computed_byte_store_has_exact_site_width_direction_and_order(windows,name,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][index]))
    else:
        row=result['accesses'][index];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_signed_endpoint_raw_return_is_bound_before_the_caller_unsigned_byte_publication(windows):
    _,_,_,selected=windows
    for name,site in (('first-endpoint',0x4BADE),('second-endpoint',0x4BB0C)):
        _,_,result,value=selected[name];call=next(row for row in value['calls'] if row['site']==site)
        assert call['return_site']==0x2637E and call['return_registers'][0]==0xFFFFFFFF
        actual=next(row for row in result['calls'] if row['site']==site)
        assert actual['entry']['registers'][5]>=224


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_common_computed_publication_alternatives_refuse_input_echo_or_only_a_new_write_set(windows,monkeypatch,fault):
    declared,_,_,selected=windows;base=selected['state'][1];actual=[deepcopy(base),deepcopy(base)]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x4BA48:('byte_2478',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x2478]=index;observed['memory_before']=(bytes(before),)
        if fault=='input-echo':publications[index]={(0x01002478,1):bytes([index])}
        elif fault=='write-set-only':publications[index]={(0x01001657+index,1):bytes(1)}
        else:publications[index]={(0x01001657,1):bytes(1)}
    if fault=='missing-publications':publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_common_actual_publication_must_change_value_outside_the_controlled_RAM_input(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x4BA48:('byte_2478',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x2478]=index;observed['memory_before']=(bytes(before),)
        publications[index]={(0x01001657,1):bytes([index])}
    proof.require_positive_alternatives(actual,declared,publications)


def test_computed_publication_bindings_use_real_writes_and_actual_final_memory(windows):
    _,_,_,selected=windows;_,observed,result,_=selected['state'];publications=proof.computed_publications(observed,result)
    assert publications and all(raw==observed['memory_after'][0][address-matrix.RAM_BASE:address-matrix.RAM_BASE+width]
        for (address,width),raw in publications.items())
    assert (0x01001657,1) in publications


def test_complete_previous_byte_curve_original_is_mandatory_from_the_identical_primary(original):
    result=proof.require_primary(original[0],original[1])
    assert all(result[key] is True for key in ('complete_direct_helpers_same_primary','complete_signed_word_difference',
        'complete_dual_byte_partial_product','complete_both_natural_curve_calls'))
    assert result['selected_native_RAM_aliases']=={'ffff23c5':'010023c5'}
    assert len(result['conditional_branch_outcomes'])==12
    assert result['fixed_branch_outcomes']=={'00026a9a':['taken']}
    record=deepcopy(original[1]);record['candidate']['witness'].pop('byte_curve_caller_withdrawal_paths')
    with pytest.raises(ValueError):proof.require_primary(original[0],record)
