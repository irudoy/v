"""Actual original DFCO state caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import dfco_state_caller_withdrawal_contract as contract,dfco_state_caller_withdrawal_matrix as matrix
from kb import dfco_state_caller_withdrawal_capture_evidence as proof,dfco_state_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['dfco_state_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original DFCO state caller withdrawal capture')
        pytest.skip('the complete original DFCO state caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_dfco_state_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)
    assert all(outcomes==['fallthrough','taken'] for outcomes in result['conditional_branch_outcomes'].values())
    assert result['reader_only16aa_retained_writer'] is True and result['prior16aa_complete_state_independence'] is True
    assert result['reader_only16aa_original']==transfers.READER16AA_IDENTITY[1]
    assert result['retained16aa_write_sites']==[0x501AE]
    assert result['fixed_branch_outcomes']=={'00025c3c':['fallthrough'],'00026a9a':['taken']}
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/dfco_state_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-dfco-state-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
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
        'early-bypass':lambda c:c['kind']=='independent-active-state-counter-threshold-frame-and-flag-input' and c['byte_2468']==64,
        'counter-init':lambda c:c['kind']=='full-R6-word-write-overwritten-by-real-local-dword-before-byte-reloads' and c['byte_14c1']==0 and c['raw_r6']==1,
        'delay-expiry':lambda c:c['kind']=='independent-active-state-counter-threshold-frame-and-flag-input' and c['raw_r4']==0 and c['raw_r5']==0 and c['byte_14c1']==0 and c['byte_193a']==1 and c['byte_1938']==3,
        'threshold-product':lambda c:c['kind']=='independent-active-state-counter-threshold-frame-and-flag-input' and c['config_8b3f']==128 and c['config_8711']==2 and c['raw_r5']==1 and c['byte_14c1']==3,
        'rotation-invalid':lambda c:c['kind']=='real-rotation-loop-mask-unsigned-count-and-six-call-bound' and c['byte_1936']==3 and c['byte_1937']==6,
        'rotation-six':lambda c:c['kind']=='real-rotation-loop-mask-unsigned-count-and-six-call-bound' and c['byte_1936']==1 and c['byte_1937']==255,
        'raw-index-255':lambda c:c['kind']=='every-raw-unsigned-state-byte-and-complete-indexed-preimage' and c['byte_14c1']==255,
        'zero-table':lambda c:c['kind']=='independent-active-state-counter-threshold-frame-and-flag-input' and c['raw_r4']==0 and c['raw_r5']==0 and c['byte_14c1']==0 and c['byte_1937']==0 and all(c[name]==0 for name in matrix.STATE_FIELDS)}
    for name,predicate in predicates.items():
        case=next(row for row in declared['cases'] if predicate(row));observed=actual[case['index']]
        result,value=proof.require_state(declared,image,case,observed,repo.ROOT);selected[name]=(case,observed,result,value)
    return declared,image,actual,selected


RESTORE_WINDOWS=('first-diagnostic','second-diagnostic','ordinary-lookup','offset-lookup','byte-endpoint','mode-bypass')


@pytest.fixture(scope='module')
def restore_windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    predicates={
        'first-diagnostic':lambda c:c['kind']=='restore-unread16aa-prior-and-retained-writer' and c['byte_5a95']==32,
        'second-diagnostic':lambda c:c['kind']=='restore-unread16aa-prior-and-retained-writer' and c['byte_5a98']==32,
        'ordinary-lookup':lambda c:c['kind']=='restore-unread16aa-prior-and-retained-writer' and c['byte_5a95']==c['byte_5a98']==c['byte_4250']==0,
        'offset-lookup':lambda c:c['kind']=='restore-unread16aa-prior-and-retained-writer' and c['byte_4250']==128,
        'byte-endpoint':lambda c:c['kind']=='restore-complete-coordinate-and-curve-direction' and c['byte_106f']==240,
        'mode-bypass':lambda c:c['kind']=='restore-independent-state-threshold-and-flag-input' and c['byte_2468']==64}
    for name,predicate in predicates.items():
        case=next(row for row in declared['cases'] if row['entry']==0x50018 and predicate(row));observed=actual[case['index']]
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x50762}


@pytest.mark.parametrize('name',('state', 'early-bypass', 'counter-init', 'delay-expiry', 'threshold-product', 'rotation-invalid', 'rotation-six', 'raw-index-255', 'zero-table'))
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


@pytest.mark.parametrize('name',RESTORE_WINDOWS)
@pytest.mark.parametrize('fault',('register','SR','PR','GBR','MACH','MACL','frame','RAM','extra-data-read','extra-data-write',
    'extra-call','branch-site','branch-target','branch-delay','omit-return','extra-return','code-byte','omit-code',
    'delay-slot','return-SP','return-GBR','return-MACL','return-target'))
def test_restore_actual_complete_state_physical_call_and_return_refusals(restore_windows,name,fault):
    test_actual_complete_state_physical_natural_branch_delay_and_return_refusals(restore_windows,name,fault)


def test_restore_actual_windows_retain_the_real_writer_and_natural_return(restore_windows):
    _,_,_,selected=restore_windows
    row=dict(zip(('id','original_claim_sha256','address','function'),transfers.READER16AA_IDENTITY))
    for case,observed,result,value in selected.values():
        writes=transfers.require16aa_reader_with_retained_writer(result,row)
        assert writes==((0x501AE,observed['memory_after'][0][0x16AA]),)
        assert result['trace'][-2]['site']==0x50386 and result['trace'][-1]['delay_slot'] is True
        assert result['trace'][-1]['next']==observed['continuation']
        assert value['gbr']==observed['context'][15] and value['sp']==observed['sp']


@pytest.fixture(scope='module')
def restore_prior_pairs(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared)
    row=dict(zip(('id','original_claim_sha256','address','function'),transfers.READER16AA_IDENTITY))
    pairs=[]
    for case in declared['cases']:
        if case['kind']!='restore-unread16aa-prior-and-retained-writer':continue
        observed=actual[case['index']];result,_=proof.require_state(declared,image,case,observed,repo.ROOT)
        pairs.append((observed,result,transfers.require16aa_reader_with_retained_writer(result,row)))
    assert proof.require16aa_prior_independence(pairs) is True
    return pairs


@pytest.mark.parametrize('fault',('omit','duplicate','prior','entry','frame-before','frame-after','context',
    'CPU','RAM','writer','bound-before','bound-after','calibration-before','calibration-after',
    'ABI-before','ABI-after','call','trace','branch','code'))
def test_restore_actual_prior_domain_refuses_partial_or_changed_complete_inputs_and_outcomes(restore_prior_pairs,fault):
    pairs=list(restore_prior_pairs)
    if fault=='omit':pairs.pop()
    elif fault=='duplicate':pairs.append(pairs[0])
    else:
        observed,result,writes=deepcopy(pairs[1])
        if fault=='prior':
            memory=bytearray(observed['memory_before'][0]);memory[0x16AA]^=1;observed['memory_before']=(bytes(memory),)
        elif fault=='entry':observed['entry']=0x503E0
        elif fault in ('frame-before','frame-after','bound-before','bound-after'):
            key=fault.replace('-','_');raw=observed[key];observed[key]=bytes([raw[0]^1])+raw[1:]
        elif fault=='context':observed['context']=(observed['context'][0]^1,*observed['context'][1:])
        elif fault=='CPU':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
        elif fault=='RAM':
            memory=bytearray(observed['memory_after'][0]);memory[0x1000]^=1;observed['memory_after']=(bytes(memory),)
        elif fault=='writer':writes=((0x501AE,writes[0][1]^1),)
        elif fault.startswith('calibration-'):
            key=fault.replace('-','_');at=next(iter(observed[key]));raw=observed[key][at];observed[key][at]=bytes([raw[0]^1])+raw[1:]
        elif fault.startswith('ABI-'):
            key=fault.lower().replace('-','_');observed[key]=(observed[key][0]^1,*observed[key][1:])
        elif fault=='call':result['calls'][0]['target']+=2
        elif fault=='trace':result['trace'][-1]['next']+=2
        elif fault=='branch':result['branches'][0]['target']+=2
        elif fault=='code':result['code'][next(iter(result['code']))]='0009'
        pairs[1]=(observed,result,writes)
    with pytest.raises(ValueError):proof.require16aa_prior_independence(pairs)


def test_restore_capture_coverage_and_prior_domains_follow_the_current_source_contract():
    words=' '.join((repo.ROOT/'defs/JK08A.dfco-state-caller-withdrawal-paths.md').read_text().split())
    assert len(proof.STATE_REQUIRED_BRANCHES)==47 and len(proof.RESTORE_REQUIRED_BRANCHES)==62
    assert len(proof.REQUIRED_BRANCHES)==109 and len(proof.FIXED_BRANCHES)==2
    for phrase in ('109 two-sided shared conditions','two fixed helper outcomes','four complete prior16AA groups'):
        assert phrase in words


@pytest.mark.parametrize('name',('state', 'early-bypass', 'counter-init', 'delay-expiry', 'threshold-product', 'rotation-invalid', 'rotation-six', 'raw-index-255', 'zero-table'))
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


@pytest.mark.parametrize('name',('state', 'early-bypass', 'counter-init', 'delay-expiry', 'threshold-product', 'rotation-invalid', 'rotation-six', 'raw-index-255', 'zero-table'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'early-bypass', 'counter-init', 'delay-expiry', 'threshold-product', 'rotation-invalid', 'rotation-six', 'raw-index-255', 'zero-table'))
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


def test_full_local_R6_carrier_keeps_word_write_dword_overwrite_and_both_real_byte_reads(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['counter-init']
    rows=[next(row for row in result['accesses'] if row['site']==site) for site in (0x503F4,0x50406,0x50490,0x504AC)]
    assert [(row['mode'],row['width_bytes'],row['bytes']) for row in rows]==[
        ('write',2,'0001'),('write',4,'00000001'),('read',1,'00'),('read',1,'01')]
    assert rows[1]['address']==observed['sp']-36
    assert rows[0]['address']==rows[2]['address']==rows[1]['address']+2 and rows[3]['address']==rows[1]['address']+3


@pytest.mark.parametrize('site',(0x503F4,0x50406,0x50490,0x504AC))
@pytest.mark.parametrize('fault',('omit','bytes','address','width'))
def test_terminal_frame_cannot_replace_real_raw_R6_intermediate_lineage(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['counter-init'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(index for index,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    else:
        row=result['accesses'][index]
        if fault=='bytes':row['bytes']='changed'
        elif fault=='width':row['width_bytes']=8
        else:row['address']+=4
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_six_real_rotation_calls_keep_every_post_delay_argument_and_natural_return(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['rotation-six']
    calls=result['calls'];assert len(calls)==value['rotations']==6
    assert [(row['site'],row['target'],row['return_address']) for row in calls]==[(0x50642,0x50766,0x50646)]*6
    assert [row['entry']['registers'][4] for row in calls]==[1,2,4,8,16,32]
    assert [row['entry']['registers'][13] for row in calls]==[1,2,3,4,5,6]
    assert [row['after']['registers'][0] for row in result['trace'] if row['site']==0x5079A]==[2,4,8,16,32,1]
    assert value['known_registers'][0]==63
    invalid=selected['rotation-invalid'][2]
    assert [row['after']['registers'][0] for row in invalid['trace'] if row['site']==0x5079A]==[0]*6


def test_full_unsigned_state_index_reaches_the_last_physical_byte(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['raw-index-255']
    event=next(row for row in result['accesses'] if row['site']==0x50658)
    assert (event['mode'],event['address'],event['width_bytes'],event['register'])==('read',0x2381B,1,6)
    assert event['bytes']==case['state_byte_255'].to_bytes(1,'big').hex() and value['known_registers'][0]==case['state_byte_255']


def test_actual_RAM1939_write_stays_explicit_and_its_original_remains_unselected(windows):
    _,_,_,selected=windows;_,_,result,_=selected['threshold-product']
    event=next(row for row in result['accesses'] if row['site']==0x50574)
    assert (event['mode'],event['address'],event['width_bytes'])==('write',0x01001939,1)
    assert all(native!=0xFFFF1939 for identity,native,alias in transfers.NATIVE_ROOTS)


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_common_computed_publication_alternatives_refuse_input_echo_or_only_a_new_write_set(windows,monkeypatch,fault):
    declared,_,_,selected=windows;base=selected['state'][1];actual=[deepcopy(base),deepcopy(base)]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x503E0:('byte_106a',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x106A]=index;observed['memory_before']=(bytes(before),)
        if fault=='input-echo':publications[index]={(0x0100106A,1):bytes([index])}
        elif fault=='write-set-only':publications[index]={(0x010014C1+index,1):bytes(1)}
        else:publications[index]={(0x010014C1,1):bytes(1)}
    if fault=='missing-publications':publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_common_actual_publication_must_change_value_outside_the_controlled_RAM_input(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x503E0:('byte_106a',)})
    publications={}
    for index,observed in enumerate(actual):
        before=bytearray(observed['memory_before'][0]);before[0x106A]=index;observed['memory_before']=(bytes(before),)
        publications[index]={(0x010014C1,1):bytes([index])}
    proof.require_positive_alternatives(actual,declared,publications)


def test_computed_publication_bindings_use_real_writes_and_actual_final_memory(windows):
    _,_,_,selected=windows;_,observed,result,_=selected['state'];publications=proof.computed_publications(observed,result)
    assert publications and all(raw==observed['memory_after'][0][address-matrix.RAM_BASE:address-matrix.RAM_BASE+width]
        for (address,width),raw in publications.items())
    assert (0x010014C1,1) in publications and (0x01001939,1) in publications


def test_component_retains_full_rotation_and_both_native_RAM_alias_intervals(original):
    result=proof.require_primary(original[0],original[1])
    assert result['complete_real_rotation_helper'] is True and result['no_selected_ram_datum_access'] is True
    assert result['selected_native_RAM_aliases']=={'ffff14bd':'010014bd','ffff14be':'010014be'}
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES) and result['fixed_branch_outcomes']=={'00025c3c':['fallthrough'],'00026a9a':['taken']}



@pytest.fixture(scope='module')
def prior1939_pairs(original):
    declared=original[2]['declaration'];actual=proof.observations(original[2],declared);pairs=[]
    for case,observed in zip(declared['cases'],actual):
        if case['kind']!='unread1939-prior-and-retained-writes':continue
        if case['byte_2468']&64:writes=()
        elif case['byte_11b3']==255:writes=((0x50594,10),)
        else:writes=((0x50574,observed['memory_after'][0][0x1939]),)
        pairs.append((observed,writes))
    return pairs


def test_actual_prior_byte_domains_preserve_CPU_frame_other_RAM_and_bypass(prior1939_pairs,original):
    assert proof.require1939_prior_independence(prior1939_pairs) is True
    result=proof.require_primary(original[0],original[1])
    assert result['reader_only1939_original']==transfers.READER1939_IDENTITY[1]
    assert result['reader_only1939_retained_writer'] is True
    assert result['prior1939_complete_state_independence'] is True
    assert result['retained1939_write_sites']==[0x50574,0x50594]
    assert result['strict_absence_originals']==[r[0] for r in transfers.NATIVE_ROOTS]


@pytest.mark.parametrize('fault',('omit-prior','omit-write-path','exit','frame','other-RAM','bypass-byte',
    'written-byte','write-site','write-value','input-neighbor','bound-after','calibration-after'))
def test_actual_directional_invariance_refuses_partial_domains_or_changed_complete_state(prior1939_pairs,fault):
    pairs=deepcopy(prior1939_pairs)
    if fault=='omit-prior':pairs.pop()
    elif fault=='omit-write-path':pairs=[pair for pair in pairs if not pair[1] or pair[1][0][0]!=0x50594]
    else:
        index=next(i for i,pair in enumerate(pairs) if bool(pair[1])==(fault in ('written-byte','write-site','write-value')))
        observed,writes=pairs[index]
        if fault=='exit':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
        elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
        elif fault in ('other-RAM','bypass-byte','written-byte'):
            raw=bytearray(observed['memory_after'][0]);raw[0x1939 if fault!='other-RAM' else 0x88]^=1;observed['memory_after']=(bytes(raw),)
        elif fault=='write-site':pairs[index]=(observed,((0x50576,writes[0][1]),))
        elif fault=='write-value':pairs[index]=(observed,((writes[0][0],writes[0][1]^1),))
        elif fault=='input-neighbor':
            raw=bytearray(observed['memory_before'][0]);raw[0x1938]^=1;observed['memory_before']=(bytes(raw),)
        elif fault=='bound-after':observed['bound_after']=b'changed'
        else:observed['calibration_after']={}
    with pytest.raises(ValueError):proof.require1939_prior_independence(pairs)
