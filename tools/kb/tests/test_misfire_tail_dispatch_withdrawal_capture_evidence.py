"""Actual original misfire tail dispatch withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import misfire_tail_dispatch_withdrawal_contract as contract,misfire_tail_dispatch_withdrawal_matrix as matrix
from kb import misfire_tail_dispatch_withdrawal_capture_evidence as proof,misfire_tail_dispatch_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['misfire_tail_dispatch_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original misfire tail dispatch withdrawal capture')
        pytest.skip('the complete original misfire tail dispatch withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_misfire_tail_dispatch_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/misfire_tail_dispatch_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-misfire-tail-dispatch-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
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
        'tail-disabled':lambda c:c['kind']=='each-complete-raw-configuration-byte' and c['config_186ce']==0,
        'hysteresis-clear':lambda c:c['kind']=='independent-hysteresis-promotion-and-comparison' and (c['byte_24c4'],c['byte_11b2'],c['config_8bda'])==(0,0,32),
        'hysteresis-equality':lambda c:c['kind']=='independent-hysteresis-promotion-and-comparison' and (c['byte_24c4'],c['byte_11b2'],c['config_8bda'])==(128,28,32),
        'byte-increment':lambda c:c['kind']=='actual-byte-counter-increment-or-saturated-signed-return' and c['byte_4096']==254,
        'byte-saturated':lambda c:c['kind']=='actual-byte-counter-increment-or-saturated-signed-return' and c['byte_4096']==255,
        'all-thresholds':lambda c:c['kind']=='three-distinct-threshold-flags-and-ordered-word-updates' and (c['word_409e'],c['word_40a0'],c['word_40a2'],c['byte_4241'])==(200,1000,200,0),
        'signed-local':lambda c:c['kind']=='complete-word-threshold-product-and-signed-local-preimage' and c['word_409e']==32768 and c['config_8354']==255,
        'speed-high':lambda c:c['kind']=='sign-extended-byte-before-unsigned-speed-and-independent-stops' and (c['byte_3834'],c['byte_444d'],c['byte_444c'])==(128,0,0),
        'speed-low':lambda c:c['kind']=='sign-extended-byte-before-unsigned-speed-and-independent-stops' and (c['byte_3834'],c['byte_444d'],c['byte_444c'])==(30,0,0),
        'first-stop':lambda c:c['kind']=='complete-independent-RAM-control-operand-or-prior-state' and c['byte_444d']==1 and (c['word_409e'],c['word_40a0'])==(200,1000),
        'third-stop':lambda c:c['kind']=='complete-independent-RAM-control-operand-or-prior-state' and c['byte_444c']==1 and c['word_40a2']==200,
        'mode-reset':lambda c:c['kind']=='complete-mode-prerequisite-reset-chain' and (c['byte_4251'],c['byte_41d2'])==(0,3),
        'prerequisite-reset':lambda c:c['kind']=='complete-mode-prerequisite-reset-chain' and (c['byte_4251'],c['byte_41d2'])==(128,2)}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x8739A}


@pytest.mark.parametrize('name',('state', 'tail-disabled', 'hysteresis-clear', 'hysteresis-equality', 'byte-increment', 'byte-saturated', 'all-thresholds', 'signed-local', 'speed-high', 'speed-low', 'first-stop', 'third-stop', 'mode-reset', 'prerequisite-reset'))
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
    elif fault=='extra-call':result['calls'].append(dict(site=observed['entry'],target=0x7C4E2))
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


@pytest.mark.parametrize('name',('state', 'tail-disabled', 'hysteresis-clear', 'hysteresis-equality', 'byte-increment', 'byte-saturated', 'all-thresholds', 'signed-local', 'speed-high', 'speed-low', 'first-stop', 'third-stop', 'mode-reset', 'prerequisite-reset'))
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


@pytest.mark.parametrize('name',('state', 'tail-disabled', 'hysteresis-clear', 'hysteresis-equality', 'byte-increment', 'byte-saturated', 'all-thresholds', 'signed-local', 'speed-high', 'speed-low', 'first-stop', 'third-stop', 'mode-reset', 'prerequisite-reset'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'tail-disabled', 'hysteresis-clear', 'hysteresis-equality', 'byte-increment', 'byte-saturated', 'all-thresholds', 'signed-local', 'speed-high', 'speed-low', 'first-stop', 'third-stop', 'mode-reset', 'prerequisite-reset'))
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


def test_single_real_BSR_has_exact_root_arguments_complete_post_delay_state_and_natural_return(windows):
    for case,observed,result,value in windows[3].values():
        assert len(result['calls'])==1 and len(value['calls'])==1
        call=result['calls'][0];expected=value['calls'][0]
        assert (call['site'],call['target'],call['return_address'],call['sp'])==(0x7C496,0x7C4E0,0x7C49A,observed['sp']-4)
        assert call['entry']==dict(registers=tuple(observed['context'][:15]),sp=observed['sp']-4,
            gbr=observed['context'][15],mach=observed['context'][16],macl=observed['context'][17],
            sr=observed['sr_before'],pr=0x7C49A)
        terminal=next(i for i,row in enumerate(result['trace']) if row['site']==expected['return_site'])
        assert expected['return_site'] in (0x7C522,0x7C526)
        assert result['trace'][terminal+1]['delay_slot'] is True
        assert result['trace'][terminal+1]['next']==0x7C49A
        assert result['trace'][terminal+1]['after']['registers'][:15]==expected['return_registers']
    assert windows[3]['byte-increment'][3]['calls'][0]['return_registers'][0]==255
    assert windows[3]['byte-saturated'][3]['calls'][0]['return_registers'][0]==0xFFFFFFFF


@pytest.mark.parametrize('name',('state','tail-disabled','hysteresis-clear','byte-saturated'))
@pytest.mark.parametrize('fault',('target','site','continuation','SP','R0','R4','R14','SR','PR','GBR','MACH','MACL'))
def test_detached_real_helper_target_arguments_or_state_is_refused(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case);call=result['calls'][0]
    if fault in ('target','site','continuation','SP'):
        key={'target':'target','site':'site','continuation':'return_address','SP':'sp'}[fault];call[key]^=2
    elif fault.startswith('R') and fault[1:].isdigit():
        registers=list(call['entry']['registers']);registers[int(fault[1:])]^=1;call['entry']['registers']=tuple(registers)
    else:call['entry'][fault.lower()]^=0x10 if fault=='SR' else 1
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_tail_entry_restores_root_PR_SP_and_reuses_only_the_exact_PR_MACL_frame_word(windows):
    for case,observed,result,value in windows[3].values():
        trace=result['trace'];at=next(i for i,row in enumerate(trace) if row['site']==0x7C49C)
        assert trace[at]['after']['registers'][2]==0x872D0
        assert trace[at+1]['site']==0x7C49E and trace[at+1]['delay_slot'] is True
        assert trace[at+2]['site']==0x872D0 and trace[at+2]['before']['pr']==observed['continuation']
        assert trace[at+2]['before']['registers'][15]==observed['sp']
        events=[row for row in result['accesses'] if row['site'] in (0x7C494,0x7C49E,0x872D0,0x8739C)]
        assert [row['address'] for row in events]==[observed['sp']-4]*4
        assert [(row['site'],row['mode'],row['width_bytes']) for row in events]==[
            (0x7C494,'write',4),(0x7C49E,'read',4),(0x872D0,'write',4),(0x8739C,'read',4)]
        assert events[0]['bytes']==events[1]['bytes']==observed['continuation'].to_bytes(4,'big').hex()
        assert events[2]['bytes']==events[3]['bytes']==observed['context'][17].to_bytes(4,'big').hex()
        assert result['macl']==observed['context'][17]


@pytest.mark.parametrize('name',('state','tail-disabled','signed-local'))
@pytest.mark.parametrize('fault',('tail-target','tail-delay','tail-entry-PR','tail-entry-SP','tail-entry-R4','PR-read','MACL-save','MACL-restore'))
def test_real_tail_cannot_be_replaced_by_a_stub_detached_entry_or_final_state_only(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='tail-target':next(row for row in result['branches'] if row['site']==0x7C49C)['target']^=2
    elif fault=='tail-delay':next(row for row in result['trace'] if row['site']==0x7C49E)['delay_slot']=False
    elif fault.startswith('tail-entry-'):
        row=next(row for row in result['trace'] if row['site']==0x872D0)['before']
        if fault=='tail-entry-PR':row['pr']^=1
        else:
            registers=list(row['registers']);registers[15 if fault=='tail-entry-SP' else 4]^=1;row['registers']=tuple(registers)
    else:
        site={'PR-read':0x7C49E,'MACL-save':0x872D0,'MACL-restore':0x8739C}[fault]
        event=next(row for row in result['accesses'] if row['site']==site);event['bytes']='00000000'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_distinct_local_stores_keep_the_post_threshold_signed_preincrement_words(windows):
    for name in ('state','signed-local','all-thresholds'):
        case,observed,result,value=windows[3][name]
        rows=[row for row in result['accesses'] if row['site'] in (0x87370,0x87378)]
        expected_first=0xFFFF8000 if name=='signed-local' else 0 if name=='all-thresholds' else 199
        expected_second=0 if name=='all-thresholds' else 999
        assert [(row['site'],row['address'],row['width_bytes'],row['register'],row['bytes']) for row in rows]==[
            (0x87370,observed['sp']-12,4,0,expected_first.to_bytes(4,'big').hex()),
            (0x87378,observed['sp']-8,4,0,expected_second.to_bytes(4,'big').hex())]
        assert value['local_counter_preimages']==((0x87370,observed['sp']-12,expected_first),(0x87378,observed['sp']-8,expected_second))
    assert windows[3]['first-stop'][3]['local_counter_preimages']==()


@pytest.mark.parametrize('site',(0x87370,0x87378))
@pytest.mark.parametrize('fault',('omit','duplicate','swap-locals','final-value','address','width_bytes','register','mode','domain'))
def test_equal_terminal_state_does_not_replace_either_signed_local_preimage(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['signed-local'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    at=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(at)
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][at]))
    elif fault=='swap-locals':result['accesses'][at]['address']=observed['sp']-(8 if site==0x87370 else 12)
    elif fault=='final-value':result['accesses'][at]['bytes']=value['word_counters'][0 if site==0x87370 else 1].to_bytes(4,'big').hex()
    else:
        row=result['accesses'][at];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_actual_threshold_flags_and_counter_words_have_separate_ordered_site_and_width_bindings(windows):
    rows=[row for row in windows[3]['all-thresholds'][2]['accesses'] if row['domain']=='ram' and row['mode']=='write']
    assert [(row['site'],row['address'],row['width_bytes']) for row in rows]==[
        (0x7C506,0x010024C4,1),(0x7C524,0x01004096,1),
        (0x872F8,0x0100409E,2),(0x87300,0x01004241,1),
        (0x87310,0x010040A0,2),(0x87318,0x01004241,1),
        (0x87332,0x010040A2,2),(0x8733A,0x01004241,1),
        (0x87374,0x0100409E,2),(0x8737C,0x010040A0,2),(0x87396,0x010040A2,2)]
    flags=[row['bytes'] for row in rows if row['address']==0x01004241]
    assert flags==['20','a0','e0']
    for name,count in (('state',200),('speed-high',200),('speed-low',0x15C),('third-stop',0x85),('mode-reset',0)):
        assert windows[3][name][1]['exit'][-1]==count
    speed=next(row for row in windows[3]['speed-high'][2]['trace'] if row['site']==0x8735A)
    assert speed['after']['registers'][2]==0xFFFFFF80


@pytest.mark.parametrize('site',(0x7C506,0x7C524,0x872F8,0x87300,0x87310,0x87318,0x87332,0x8733A,0x87374,0x8737C,0x87396))
@pytest.mark.parametrize('fault',('omit','duplicate','bytes','address','width_bytes','register','mode','domain'))
def test_each_real_flag_and_counter_store_requires_its_exact_ordered_physical_bytes(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['all-thresholds'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    at=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(at)
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][at]))
    else:
        row=result['accesses'][at];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('field,values',(('byte_4096',(0,1)),('word_409e',(199,200)),('word_40a0',(999,1000)),
    ('word_40a2',(199,200)),('byte_444d',(0,1)),('byte_444c',(0,1))))
def test_actual_fixed_other_counter_and_stop_pairs_have_distinct_common_computed_publications(original,monkeypatch,field,values):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    decoded=proof.observations(original[2],declared);actual=[];publications={}
    def matching(case,raw):
        if case['kind']!='complete-independent-RAM-control-operand-or-prior-state' or case[field]!=raw:return False
        held=dict(matrix.DEFAULTS)
        if field=='byte_4096':held['byte_11b2']=255
        elif field=='word_409e':held['word_40a0']=1000
        elif field in ('word_40a0','word_40a2'):held['word_409e']=200
        elif field=='byte_444d':held.update(word_409e=200,word_40a0=1000)
        else:held['word_40a2']=200
        held[field]=raw
        return all(case[name]==value for name,value in held.items())
    for index,raw in enumerate(values):
        case=next(row for row in declared['cases'] if matching(row,raw));observed=decoded[case['index']]
        result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        actual.append(observed);publications[index]=proof.computed_publications(observed,result)
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x7C494:(field,)})
    publication={'byte_4096':(0x01004096,1),'word_409e':(0x01004241,1),'word_40a0':(0x01004241,1),
        'word_40a2':(0x01004241,1),'byte_444d':(0x0100409E,2),'byte_444c':(0x010040A2,2)}[field]
    assert publications[0][publication]!=publications[1][publication]
    if field not in ('word_40a2','byte_444c'):assert actual[0]['exit'][-1]==actual[1]['exit'][-1]
    proof.require_positive_alternatives(actual,declared,publications)


@pytest.mark.parametrize('fault',('input-echo','arbitrary-counter-change','saturated-input','identical-values','write-set-only','missing-publications'))
def test_same_address_counter_credit_requires_two_exact_actual_increments_not_input_echo(windows,monkeypatch,fault):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x7C494:('byte_4096',)})
    for index,row in enumerate(actual):
        memory=bytearray(row['memory_before'][0]);memory[0x4096]=index;row['memory_before']=(bytes(memory),)
    publications={0:{(0x01004096,1):b'\x01'},1:{(0x01004096,1):b'\x02'}}
    if fault=='input-echo':publications={i:{(0x01004096,1):bytes([i])} for i in range(2)}
    elif fault=='arbitrary-counter-change':publications={i:{(0x01004096,1):bytes([10+i])} for i in range(2)}
    elif fault=='saturated-input':
        memory=bytearray(actual[1]['memory_before'][0]);memory[0x4096]=255;actual[1]['memory_before']=(bytes(memory),);publications[1]={(0x01004096,1):b'\xff'}
    elif fault=='identical-values':publications[1]=deepcopy(publications[0])
    elif fault=='write-set-only':publications[1]={(0x01004097,1):b'\x02'}
    else:publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_changed_exact_counter_increment_is_the_only_same_input_footprint_exception(windows,monkeypatch):
    declared,_,_,selected=windows;actual=[deepcopy(selected['state'][1]),deepcopy(selected['state'][1])]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x7C494:('byte_4096',)})
    for index,row in enumerate(actual):
        memory=bytearray(row['memory_before'][0]);memory[0x4096]=index;row['memory_before']=(bytes(memory),)
    proof.require_positive_alternatives(actual,declared,{0:{(0x01004096,1):b'\x01'},1:{(0x01004096,1):b'\x02'}})


def test_full_original_retains_exact_native_alias_and_all_domain_admission_boundaries(original):
    result=proof.require_primary(original[0],original[1])
    for key in ('complete_actual_dispatch_BSR_and_tail','complete_hysteresis_and_byte_counter',
            'complete_thresholded_word_counters','complete_PR_MACL_and_distinct_local_carriers',
            'complete_selected_native_RAM_root_absence','scheduler_cadence_and_transitive_dependencies_preserved'):
        assert result[key] is True
    assert result['selected_native_RAM_aliases']=={'ffff84ba':'010084ba'}
    assert len(result['conditional_branch_outcomes'])==14 and result['fixed_branch_outcomes']=={}
