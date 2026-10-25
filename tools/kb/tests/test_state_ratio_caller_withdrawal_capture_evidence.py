"""Actual original state ratio caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import state_ratio_caller_withdrawal_contract as contract,state_ratio_caller_withdrawal_matrix as matrix
from kb import state_ratio_caller_withdrawal_capture_evidence as proof,state_ratio_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['state_ratio_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original state ratio caller withdrawal capture')
        pytest.skip('the complete original state ratio caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_state_ratio_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/state_ratio_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-state-ratio-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    predicates={
        'ratio':lambda c:c['entry']==0x64CB2,
        'ratio-negative':lambda c:c['kind']=='signed-word-divisor-sign-normalization-shift-wrap-and-ratio-clamps' and c['word_240e']==65535 and c['config_8ea6']==0,
        'ratio-zero':lambda c:c['kind']=='signed-word-divisor-sign-normalization-shift-wrap-and-ratio-clamps' and c['word_240e']==0,
        'unsigned':lambda c:c['kind']=='independent-active-ratio-state-flag-and-calibration-input' and c['config_870c']==0 and c['byte_246a']==0 and c['config_8b3f']==20 and c['word_1866']==1800,
        'byte':lambda c:c['entry']==0xBDC66,
        'curve-second':lambda c:c['kind']=='exact-implicit-coordinate-boundaries-and-endpoint-promotion' and c['config_8616']==0 and c['byte_106f']==64,
        'curve-first':lambda c:c['kind']=='exact-implicit-coordinate-boundaries-and-endpoint-promotion' and c['config_8616']==1 and c['byte_2772']==32,
        'curve-endpoint':lambda c:c['kind']=='exact-implicit-coordinate-boundaries-and-endpoint-promotion' and c['config_8616']==0 and c['byte_106f']==224,
        'counter-hold':lambda c:c['kind']=='independent-active-byte-state-interpolation-counter-and-offset-input' and c['byte_24a7']==2 and c['byte_25ee']==1,
        'special':lambda c:c['kind']=='independent-active-byte-state-interpolation-counter-and-offset-input' and c['config_8b34']==16 and c['config_8b42']==2 and c['byte_10e4']==8}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x64FDE,0xBDED4}


@pytest.mark.parametrize('name',('ratio', 'ratio-negative', 'ratio-zero', 'unsigned', 'byte', 'curve-second', 'curve-first', 'curve-endpoint', 'counter-hold', 'special'))
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


@pytest.mark.parametrize('name',('ratio', 'ratio-negative', 'ratio-zero', 'unsigned', 'byte', 'curve-second', 'curve-first', 'curve-endpoint', 'counter-hold', 'special'))
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


@pytest.mark.parametrize('name',('ratio', 'ratio-negative', 'ratio-zero', 'unsigned', 'byte', 'curve-second', 'curve-first', 'curve-endpoint', 'counter-hold', 'special'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('ratio', 'ratio-negative', 'ratio-zero', 'unsigned', 'byte', 'curve-second', 'curve-first', 'curve-endpoint', 'counter-hold', 'special'))
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


def test_negative_signed_word_divisor_retains_real_normalization_and_saved_argument_state(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['ratio-negative']
    call=next(row for row in result['calls'] if row['site']==0x64D54)
    assert call['target']==0x21BBC and call['entry']['registers'][:2]==(0xFFFFFFFF,0xFFFF0000)
    assert {0x21BCC,0x21BCE}<=set(result['code']) and value['ram'][0x1866:0x1868]==b'\xff\xff'
    assert 0x21C70 not in result['code'] and value['ram'][0x9818:0x981C]==matrix.DEFAULTS['dword_9818'].to_bytes(4,'big')


def test_curve_publications_keep_the_separate_saved_increment_candidate(windows):
    _,_,_,selected=windows
    for name in ('curve-first','curve-second','curve-endpoint'):
        case,observed,result,value=selected[name]
        candidate=next(row for row in result['accesses'] if row['site']==0xBDE40)
        final=next(row for row in result['accesses'] if row['site']==0xBDEC6)
        stores=[row for row in result['accesses'] if row['site'] in (0xBDE8C,0xBDE94)]
        assert candidate['address']==final['address']==observed['sp']-28 and candidate['bytes']==final['bytes']
        assert [row['address'] for row in stores]==[0x01001A1E,0x010025EE] and stores[0]['bytes']==stores[1]['bytes']
        assert int(final['bytes'],16)==case['byte_2326']+1 and value['ram'][0x2326]==case['byte_2326']+1
    endpoint=next(row for row in selected['curve-endpoint'][2]['trace'] if row['site']==0x26380)
    assert endpoint['after']['registers'][0]&0xFFFFFF00==0xFFFFFF00


@pytest.mark.parametrize('site',(0xBDDB2,0xBDDB6,0xBDDCE,0xBDDE2,0xBDE40,0xBDEC6))
@pytest.mark.parametrize('fault',('omit','bytes','address','width'))
def test_terminal_frame_cannot_replace_intermediate_low_endpoint_or_candidate_lineage(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['curve-second'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(index for index,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    else:
        row=result['accesses'][index]
        if fault=='bytes':row['bytes']='changed'
        elif fault=='width':row['width_bytes']=1
        else:row['address']+=4
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_common_computed_publication_alternatives_refuse_input_echo_or_only_a_new_write_set(windows,monkeypatch,fault):
    declared,_,_,selected=windows;base=selected['ratio'][1];actual=[deepcopy(base),deepcopy(base)]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x64CB2:('byte_1082',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x1082]=index
        observed['memory_before']=(bytes(before),)
        if fault=='input-echo':publications[index]={(0x01001082,1):bytes([index])}
        elif fault=='write-set-only':publications[index]={(0x01001866+index,2):bytes(2)}
        else:publications[index]={(0x01001866,2):bytes(2)}
    if fault=='missing-publications':publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_common_actual_publication_must_change_value_outside_the_controlled_RAM_input(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['ratio'][1]),deepcopy(selected['ratio'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x64CB2:('byte_1082',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x1082]=index;observed['memory_before']=(bytes(before),)
        publications[index]={(0x01001866,2):index.to_bytes(2,'big')}
    proof.require_positive_alternatives(actual,declared,publications)


def test_computed_publications_use_real_writes_and_actual_final_memory(windows):
    _,_,_,selected=windows;_,observed,result,_=selected['curve-second'];publications=proof.computed_publications(observed,result)
    assert all(raw==observed['memory_after'][0][address-matrix.RAM_BASE:address-matrix.RAM_BASE+width]
        for (address,width),raw in publications.items())
    assert {(0x01002326,1),(0x01001A1E,1),(0x010025EE,1)}<=set(publications)


@pytest.mark.parametrize('component',('division_callees_paths','byte_curve_caller_withdrawal_paths'))
def test_identical_primary_requires_every_full_previous_original(original,component):
    record=deepcopy(original[1]);record['candidate']['witness'].pop(component)
    with pytest.raises(ValueError):proof.require_primary(original[0],record)


def test_identical_primary_retains_the_original_complete_standard_implicit_byte_source(original,monkeypatch):
    from kb import ignition_literal_evidence
    stdout,current=ignition_literal_evidence.require_original(original[0],original[1])
    stdout=''.join(line for line in stdout.splitlines(keepends=True)
        if not line.startswith('VQ_SH_ELF_STOCK_CODE status=PASS region=jk08a-implicit-byte-curve cases='))
    monkeypatch.setattr(ignition_literal_evidence,'require_original',lambda *args:(stdout,current))
    with pytest.raises(ValueError,match='standard implicit-byte'):proof.require_primary(original[0],original[1])


def test_component_retains_full_originals_and_exact_fixed_premises(original):
    result=proof.require_primary(original[0],original[1])
    assert all(result[key] is True for key in ('complete_direct_helpers_same_primary',
        'complete_previous_byte_curve_caller_same_primary','complete_standard_implicit_byte_same_primary','no_selected_datum_access'))
    assert result['selected_native_RAM_aliases']=={}
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)
    assert len(result['fixed_divisor_outcomes'])==len(proof.FIXED_BRANCHES)
