"""Actual original auxiliary rate caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import aux_rate_caller_withdrawal_contract as contract,aux_rate_caller_withdrawal_matrix as matrix
from kb import aux_rate_caller_withdrawal_capture_evidence as proof,aux_rate_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['aux_rate_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original auxiliary rate caller withdrawal capture')
        pytest.skip('the complete original auxiliary rate caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_aux_rate_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/aux_rate_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-aux-rate-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
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
        'bypass':lambda c:c['kind']=='independent-active-counter-word-flag-and-real-auxiliary-gate-input' and c['byte_24c0']==0,
        'empty':lambda c:c['kind']=='independent-active-counter-word-flag-and-real-auxiliary-gate-input' and c['word_235c']==0,
        'signed-local':lambda c:c['kind']=='sign-extended-saved-counter-two-dword-carriers-and-ordered-clamps' and c['word_2018']==32768 and c['word_201a']==250,
        'long-product':lambda c:c['kind']=='complete-unsigned-word-product-and-real-short-long-divider-boundary' and c['word_235c']==65535 and c['word_201a']==65535,
        'lower-after-upper':lambda c:c['kind']=='sign-extended-saved-counter-two-dword-carriers-and-ordered-clamps' and c['word_2018']==0 and c['word_201a']==0,
        'initialize':lambda c:c['kind']=='real-initialization-and-post-gate-publication-clear' and c['byte_4251']==1 and c['word_34e4']==0 and c['byte_4184']==0,
        'clear':lambda c:c['kind']=='real-initialization-and-post-gate-publication-clear' and c['byte_4251']==0 and c['word_34e4']==20 and c['byte_4184']==0,
        'gate-block':lambda c:c['kind']=='real-initialization-and-post-gate-publication-clear' and c['byte_4251']==0 and c['word_34e4']==20 and c['byte_4184']==64,
        'first-negative-word':lambda c:c['kind']=='raw-sign-extended-first-auxiliary-word-and-unsigned-second-word' and c['word_34e4']==32768 and c['word_34e6']==0,
        'second-unsigned-word':lambda c:c['kind']=='raw-sign-extended-first-auxiliary-word-and-unsigned-second-word' and c['word_34e4']==0 and c['word_34e6']==32768}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x68DE4}


@pytest.mark.parametrize('name',('state', 'bypass', 'empty', 'signed-local', 'long-product', 'lower-after-upper', 'initialize', 'clear', 'gate-block', 'first-negative-word', 'second-unsigned-word'))
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


@pytest.mark.parametrize('name',('state', 'bypass', 'empty', 'signed-local', 'long-product', 'lower-after-upper', 'initialize', 'clear', 'gate-block', 'first-negative-word', 'second-unsigned-word'))
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


@pytest.mark.parametrize('name',('state', 'bypass', 'empty', 'signed-local', 'long-product', 'lower-after-upper', 'initialize', 'clear', 'gate-block', 'first-negative-word', 'second-unsigned-word'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'bypass', 'empty', 'signed-local', 'long-product', 'lower-after-upper', 'initialize', 'clear', 'gate-block', 'first-negative-word', 'second-unsigned-word'))
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


def test_both_real_local_dword_stores_and_signed_word_reload_remain_ordered(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['signed-local']
    rows=[next(row for row in result['accesses'] if row['site']==site) for site in (0x68D90,0x68D92,0x68DA6)]
    assert [(row['mode'],row['width_bytes'],row['bytes']) for row in rows]==[
        ('write',4,'ffff8000'),('write',4,'ffff8000'),('read',4,'ffff8000')]
    assert [row['address']-observed['sp'] for row in rows]==[-16,-20,-20]


@pytest.mark.parametrize('site',(0x68D90,0x68D92,0x68DA6))
@pytest.mark.parametrize('fault',('omit','bytes','address','width'))
def test_terminal_frame_cannot_replace_either_local_dword_or_its_real_reload(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['signed-local'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(index for index,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    elif fault=='bytes':result['accesses'][index]['bytes']='changed'
    elif fault=='width':result['accesses'][index]['width_bytes']=2
    else:result['accesses'][index]['address']+=4
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_real_full_unsigned_product_and_long_helper_return_keep_all_raw_word_bits(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['long-product']
    assert [(row['site'],row['target'],row['return_address']) for row in result['calls']]==[
        (0x68D9E,0x21CE0,0x68DA2),(0x68DC8,0x8C3FA,0x68DCC)]
    call=result['calls'][0]
    assert call['entry']['registers'][0]==4000 and call['entry']['registers'][1]==65535*65535
    assert value['calls'][0]['long_path'] is True
    assert value['calls'][0]['return_registers'][0]==65535*65535//4000
    assert int.from_bytes(result['ram'][0x201E:0x2020],'big')==65535-125


def test_call_delay_publication_and_later_actual_clear_are_two_separate_real_stores(windows):
    _,_,_,selected=windows;_,observed,result,_=selected['clear']
    rows=[row for row in result['accesses'] if row['address']==0x0100201E and row['mode']=='write']
    assert [(row['site'],row['width_bytes'],row['bytes']) for row in rows]==[(0x68DCA,2,'00e1'),(0x68DDA,2,'0000')]
    assert next(row for row in result['trace'] if row['site']==0x68DCA)['delay_slot'] is True
    assert result['ram'][0x201E:0x2020]==bytes(2)
    blocked=selected['gate-block'][2]
    assert [row['site'] for row in blocked['accesses'] if row['address']==0x0100201E and row['mode']=='write']==[0x68DCA]


def test_auxiliary_gate_keeps_signed_first_word_and_unsigned_second_word_paths(windows):
    _,_,_,selected=windows;first=selected['first-negative-word'][2];second=selected['second-unsigned-word'][2]
    assert next(row for row in first['trace'] if row['site']==0x8C428)['after']['registers'][2]==0xFFFF8000
    assert all(row['site']!=0x8C430 for row in first['trace'])
    assert next(row for row in second['trace'] if row['site']==0x8C430)['after']['registers'][2]==0xFFFF8000
    assert next(row for row in second['trace'] if row['site']==0x8C432)['after']['registers'][2]==32768


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_common_computed_publication_alternatives_refuse_input_echo_or_only_a_new_write_set(windows,monkeypatch,fault):
    declared,_,_,selected=windows;base=selected['state'][1];actual=[deepcopy(base),deepcopy(base)]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x68D58:('byte_24c0',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x24C0]=index;observed['memory_before']=(bytes(before),)
        if fault=='input-echo':publications[index]={(0x010024C0,1):bytes([index])}
        elif fault=='write-set-only':publications[index]={(0x0100201E+index,1):bytes(1)}
        else:publications[index]={(0x0100201E,1):bytes(1)}
    if fault=='missing-publications':publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_common_actual_publication_must_change_value_outside_the_controlled_RAM_input(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x68D58:('byte_24c0',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x24C0]=index;observed['memory_before']=(bytes(before),)
        publications[index]={(0x0100201E,1):bytes([index])}
    proof.require_positive_alternatives(actual,declared,publications)


def test_computed_publication_bindings_use_real_writes_and_actual_final_memory(windows):
    _,_,_,selected=windows;_,observed,result,_=selected['state'];publications=proof.computed_publications(observed,result)
    assert publications and all(raw==observed['memory_after'][0][address-matrix.RAM_BASE:address-matrix.RAM_BASE+width]
        for (address,width),raw in publications.items())
    assert (0x0100201E,2) in publications


def test_component_retains_full_real_auxiliary_gate_and_complete_direct_helper_original(original):
    result=proof.require_primary(original[0],original[1])
    assert result['complete_direct_helpers_same_primary'] is True and result['complete_real_auxiliary_gate'] is True
    assert result['selected_native_RAM_aliases']=={}
    assert len(result['conditional_branch_outcomes'])==14
    assert result['fixed_branch_outcomes']=={f'{site:08x}':[outcome] for site,outcome in proof.FIXED_BRANCHES.items()}
