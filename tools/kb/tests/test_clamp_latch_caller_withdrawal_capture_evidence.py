"""Actual original clamp latch caller withdrawal raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import clamp_latch_caller_withdrawal_contract as contract,clamp_latch_caller_withdrawal_matrix as matrix
from kb import clamp_latch_caller_withdrawal_capture_evidence as proof,clamp_latch_caller_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['clamp_latch_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original clamp latch caller withdrawal capture')
        pytest.skip('the complete original clamp latch caller withdrawal capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_clamp_latch_caller_withdrawal_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/clamp_latch_caller_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-clamp-latch-caller-withdrawal-paths.c','tools/kb/src/kb/proof_sources.py',
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
        'copy':lambda c:c['kind']=='real-ROM-byte-copy-mode' and c['config_8b7e']==128,
        'first-zero':lambda c:c['kind']=='actual-byte-absolute-difference-and-ten-boundary' and c['byte_11ea']==0 and c['byte_22e4']==0,
        'first-negative':lambda c:c['kind']=='actual-byte-absolute-difference-and-ten-boundary' and c['byte_11ea']==0 and c['byte_22e4']==9,
        'first-ten':lambda c:c['kind']=='actual-byte-absolute-difference-and-ten-boundary' and c['byte_11ea']==10 and c['byte_22e4']==0,
        'second127':lambda c:c['kind']=='actual-full-word-shift2-absolute-difference-and128-boundary' and c['word_1062']==25 and c['word_1fa4']==227,
        'second128':lambda c:c['kind']=='actual-full-word-shift2-absolute-difference-and128-boundary' and c['word_1062']==25 and c['word_1fa4']==228,
        'below':lambda c:c['kind']=='signed-word-addend-and-unordered-byte-clamp' and c['byte_55e6']==127 and c['word_1ee2']==65535 and c['config_8692']==200 and c['config_8693']==100,
        'above':lambda c:c['kind']=='signed-word-addend-and-unordered-byte-clamp' and c['byte_55e6']==255 and c['word_1ee2']==32767 and c['config_8692']==0 and c['config_8693']==255,
        'unordered':lambda c:c['kind']=='signed-word-addend-and-unordered-byte-clamp' and c['byte_55e6']==255 and c['word_1ee2']==0 and c['config_8692']==200 and c['config_8693']==100,
        'gate-block':lambda c:c['kind']=='complete-raw-control-operand-or-prior-state-width' and c['byte_4185']==0,
        'fallback-block':lambda c:c['kind']=='alternate-unsigned-word-versus-byte-admission' and c['byte_55e6']==128 and c['word_117e']==128,
        'fallback-pass':lambda c:c['kind']=='alternate-unsigned-word-versus-byte-admission' and c['byte_55e6']==128 and c['word_117e']==127,
        'signed-refresh':lambda c:c['kind']=='complete-signed-load-word-refresh-physical-bits' and c['word_1026']==32768}
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
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x393F4}


@pytest.mark.parametrize('name',('state', 'copy', 'first-zero', 'first-negative', 'first-ten', 'second127', 'second128', 'below', 'above', 'unordered', 'gate-block', 'fallback-block', 'fallback-pass', 'signed-refresh'))
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


@pytest.mark.parametrize('name',('state', 'copy', 'first-zero', 'first-negative', 'first-ten', 'second127', 'second128', 'below', 'above', 'unordered', 'gate-block', 'fallback-block', 'fallback-pass', 'signed-refresh'))
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


@pytest.mark.parametrize('name',('state', 'copy', 'first-zero', 'first-negative', 'first-ten', 'second127', 'second128', 'below', 'above', 'unordered', 'gate-block', 'fallback-block', 'fallback-pass', 'signed-refresh'))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_every_raw_curve_axis_configuration_and_literal_byte_is_exact(windows,name,phase):
    declared,image,_,selected=windows
    for address,raw in selected[name][1][phase].items():
        for offset in range(len(raw)):
            case,observed,_,_=deepcopy(selected[name]);changed=bytearray(raw);changed[offset]^=1
            observed[phase][address]=bytes(changed)
            with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('name',('state', 'copy', 'first-zero', 'first-negative', 'first-ten', 'second127', 'second128', 'below', 'above', 'unordered', 'gate-block', 'fallback-block', 'fallback-pass', 'signed-refresh'))
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


def test_actual_absolute_calls_keep_zero_negative_and_both_comparison_boundaries(windows):
    selected=windows[3]
    for name,count,first in (('first-zero',2,0),('first-negative',2,-9),('first-ten',1,10)):
        _,_,result,value=selected[name]
        assert len(result['calls'])==count
        call=result['calls'][0]
        assert (call['site'],call['target'],call['entry']['registers'][4])==(0x3936C,0x22590,first&0xFFFFFFFF)
        assert value['calls'][0]['return_registers'][0]==abs(first)
    for name,delta in (('second127',-127),('second128',-128)):
        result=selected[name][2];call=result['calls'][1]
        assert (call['site'],call['target'],call['entry']['registers'][4])==(0x3938A,0x22590,delta&0xFFFFFFFF)
        expected=next(row for row in selected[name][3]['calls'] if row['site']==0x3938A)
        assert expected['return_registers'][0]==abs(delta) and expected['return_site']==0x22596
        assert next(row for row in result['branches'] if row['site']==0x39394)['kind']==('fallthrough' if name=='second127' else 'taken')


def test_actual_unordered_clamp_and_latch_publish_three_separate_width_bound_values(windows):
    selected=windows[3]
    for name,byte in (('below',200),('above',255),('unordered',100),('fallback-pass',129)):
        case,observed,result,value=selected[name]
        assert observed['memory_after'][0][0x55E6]==byte and observed['memory_after'][0][0x422F]==0xA4
        writes=[(row['site'],row['address'],row['width_bytes']) for row in result['accesses'] if row['domain']=='ram' and row['mode']=='write']
        assert (0x393D4,0x010055E6,1) in writes and (0x393E2,0x0100422F,1) in writes
        assert writes[-1]==(0x393EE,0x01001FA4,2)
    for name in ('gate-block','fallback-block'):
        assert all(row['site'] not in (0x393D4,0x393E2) for row in selected[name][2]['accesses'])


def test_actual_signed_word_refresh_preserves_full_bits_and_returned_offset(windows):
    for case,observed,result,value in windows[3].values():
        assert observed['memory_after'][0][0x1FA4:0x1FA6]==observed['memory_before'][0][0x1026:0x1028]
        assert observed['exit'][-1]==value['output']==0x144
    _,_,result,_=windows[3]['signed-refresh']
    load=next(row for row in result['trace'] if row['site']==0x393EC)
    assert load['after']['registers'][2]==0xFFFF8000


@pytest.mark.parametrize('site',(0x39332,0x393D4,0x393E2,0x393EE))
@pytest.mark.parametrize('fault',('omit','duplicate','bytes','address','width_bytes','register','mode','domain'))
def test_each_real_byte_or_word_publication_keeps_exact_order_width_and_complete_bytes(windows,site,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['copy' if site==0x39332 else 'state'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    index=next(i for i,row in enumerate(result['accesses']) if row['site']==site)
    if fault=='omit':result['accesses'].pop(index)
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][index]))
    else:
        row=result['accesses'][index];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_all_complete_actual_paths_keep_the_entire_table_interval_unread(windows):
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='clamp_latch_caller_withdrawal_paths']
    assert len(rows)==1
    for case,observed,result,value in windows[3].values():transfers.require_no_selected_datum(result,rows)


@pytest.mark.parametrize('address',(0x1562F,0x15630,0x15631,0x1563E,0x1563F))
@pytest.mark.parametrize('mode',('read','write'))
def test_actual_direct_table_absence_cannot_be_replaced_by_first_byte_or_first_word_absence(windows,address,mode):
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='clamp_latch_caller_withdrawal_paths']
    result=deepcopy(windows[3]['state'][2]);result['accesses'].append(dict(site=0x39316,mode=mode,address=address,width_bytes=2,domain='changed',register=0,bytes='0000'))
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,rows)


@pytest.mark.parametrize('fault',('input-echo','write-set-only','identical-values','missing-publications'))
def test_causal_guard_requires_different_common_computed_values_outside_the_controlled_input(windows,monkeypatch,fault):
    declared,_,_,selected=windows;base=selected['state'][1];actual=[deepcopy(base),deepcopy(base)]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x39316:('word_1ee2',)})
    for index,row in enumerate(actual):
        memory=bytearray(row['memory_before'][0]);memory[0x1EE2:0x1EE4]=index.to_bytes(2,'big');row['memory_before']=(bytes(memory),)
    publications={0:{(0x010055E6,1):b'1'},1:{(0x010055E6,1):b'2'}}
    if fault=='input-echo':publications={i:{(0x01001EE2,2):i.to_bytes(2,'big')} for i in range(2)}
    elif fault=='write-set-only':publications[1]={}
    elif fault=='identical-values':publications[1]=deepcopy(publications[0])
    else:publications.pop(1)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


def test_causal_guard_keeps_the_real_returned_offset_and_requires_a_changed_actual_publication(windows,monkeypatch):
    declared,_,_,selected=windows;base=selected['state'][1];actual=[deepcopy(base),deepcopy(base)]
    monkeypatch.setattr(matrix,'ENTRY_FIELDS',{0x39316:('word_1ee2',)})
    for index,row in enumerate(actual):
        memory=bytearray(row['memory_before'][0]);memory[0x1EE2:0x1EE4]=index.to_bytes(2,'big');row['memory_before']=(bytes(memory),)
        assert row['exit'][-1]==0x144
    proof.require_positive_alternatives(actual,declared,{0:{(0x010055E6,1):b'1'},1:{(0x010055E6,1):b'2'}})
