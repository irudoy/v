"""Actual original indexed word update raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import indexed_word_update_contract as contract,indexed_word_update_matrix as matrix
from kb import indexed_word_update_capture_evidence as proof,indexed_word_update_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['indexed_word_update_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original indexed word update capture')
        pytest.skip('the complete original indexed word update capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_indexed_word_update_paths'] is True and result['no_selected_datum_access'] is True
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/indexed_word_update_capture.py',
    'tools/sh-elf-run/stock_jk08a_scalar_ram_leaves.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-indexed-word-update-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    choices=(('run',0x52034,dict(raw_r4=0,raw_r5=1,hold_mask=0,fuel_mask=0,inhibit_mask=0,
            state_word_000=1000,state_word_076=1000,counter_word_000=2000,enable_mask=8)),
        ('held',0x52034,dict(raw_r4=0,raw_r5=1,hold_mask=1)),
        ('disabled',0x52034,dict(enable_mask=0)),
        ('fuel-blocked',0x52034,dict(raw_r5=1,fuel_mask=1)),
        ('threshold-blocked',0x52034,dict(raw_r4=0,state_word_076=0)),
        ('inhibit-blocked',0x52034,dict(raw_r5=1,inhibit_mask=1)),
        ('floor',0x52034,dict(raw_r4=0,state_word_000=1000,counter_word_000=0)),
        ('wrap',0x52034,dict(raw_r4=0,state_word_000=65535,counter_word_000=65535)),
        ('last-index',0x52034,dict(raw_r4=255,state_word_255=65535,counter_word_255=65535)),
        ('SR-context',0x52034,dict(initial_sr=0x3A1,hold_mask=0,fuel_mask=0,enable_mask=8)))
    for name,entry,changes in choices:
        case=next(row for row in declared['cases'] if row['entry']==entry
            and all(row[key]==value for key,value in changes.items()))
        observed=actual[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        selected[name]=(case,observed,result,value)
    return declared,image,actual,selected


def test_all_natural_leaf_entries_have_separate_complete_register_SR_RAM_frame_and_physical_results(windows):
    declared,image,_,selected=windows
    for case,observed,result,value in selected.values():
        fixture,_=contract.fixture_for_case(declared['source'],image,case)
        assert observed['exit']==value['exit'] and observed['memory_after']==(value['ram'],)
        assert result['accesses']==transfers.physical(observed,value,fixture)
        assert result['calls']==[] and result['trace'][-1]['delay_slot'] is True
        assert result['trace'][-1]['next']==observed['continuation']
    assert {row[2]['trace'][-2]['site'] for row in selected.values()}=={0x520E8}


@pytest.mark.parametrize('name',('run','held','disabled','fuel-blocked','threshold-blocked','inhibit-blocked','floor','wrap','last-index','SR-context'))
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


@pytest.mark.parametrize('name',('run','floor','wrap','last-index'))
@pytest.mark.parametrize('fault',('site','mode','address','width_bytes','register','domain','bytes','omit','duplicate'))
def test_exact_ordered_physical_data_pool_and_stack_operands_cannot_be_substituted(windows,name,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='omit':result['accesses'].pop()
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][0]))
    else:
        row=result['accesses'][0];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('identity',tuple(row[10] for row in owning.IDENTITIES if row[6]=='indexed_word_update_paths'))
def test_selected_native_RAM_roots_cannot_be_replaced_by_real_RAM_or_pool_address_evidence(identity):
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='indexed_word_update_paths'];row=next(row for row in rows if row['original_claim_sha256']==identity)
    result=dict(accesses=[dict(domain='rom',site=0x527B0,address=row['address'],width_bytes=1)])
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,rows)
    result['accesses'][0].update(address=0x8BBE,site=0x54458)
    with pytest.raises(ValueError):transfers.require_no_selected_datum(result,rows)


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


@pytest.mark.parametrize('offset',(0,1))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_immutable_interrupt_mask_word_refuses_either_changed_byte(windows,offset,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['run'])
    raw=bytearray(observed[phase][0x52128]);raw[offset]^=1;observed[phase][0x52128]=bytes(raw)
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


@pytest.mark.parametrize('at',(0x87FE,0x8D92))
@pytest.mark.parametrize('phase',('calibration_before','calibration_after'))
def test_complete_byte_configuration_cannot_be_substituted(windows,at,phase):
    declared,image,_,selected=windows;case,observed,_,_=deepcopy(selected['run'])
    observed[phase][at]=bytes([observed[phase][at][0]^1])
    with pytest.raises(ValueError):matrix.require_input(declared['source'],image,case,observed)


def test_actual_frame_retains_old_pointer_before_its_later_replacement(windows):
    _,_,_,selected=windows;case,observed,result,value=selected['wrap']
    events=[r for r in result['accesses'] if r['site'] in (0x520A2,0x520BE,0x520CA)]
    assert [(r['site'],r['mode'],r['bytes']) for r in events]==[
        (0x520A2,'write','01002330'),(0x520BE,'read','01002330'),(0x520CA,'write','01002348')]
    assert observed['frame_after'][148:152]==bytes.fromhex('01002348')
    assert observed['memory_after'][0][0x2348:0x234A]==bytes(2)
    assert value['registers'][6]==65536


@pytest.mark.parametrize('fault',('omit-first-pointer','replace-first-with-final','swap-read-and-replacement','omit-read'))
def test_terminal_frame_cannot_replace_intermediate_ordered_pointer_effects(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['wrap'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    events=result['accesses'];first=next(i for i,r in enumerate(events) if r['site']==0x520A2)
    if fault=='omit-first-pointer':events.pop(first)
    elif fault=='replace-first-with-final':events[first]['bytes']='01002348'
    elif fault=='swap-read-and-replacement':
        a=next(i for i,r in enumerate(events) if r['site']==0x520BE)
        b=next(i for i,r in enumerate(events) if r['site']==0x520CA);events[a],events[b]=events[b],events[a]
    else:events.pop(next(i for i,r in enumerate(events) if r['site']==0x520BE))
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('site,phase',((0x5208A,'before'),(0x5209C,'after'),(0x520D8,'after')))
@pytest.mark.parametrize('mask',(1,0x10,0x80,0x100,0x200))
def test_final_SR_cannot_replace_actual_temporary_and_restored_interrupt_states(windows,site,phase,mask):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected['SR-context'])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    next(row for row in result['trace'] if row['site']==site)[phase]['sr']^=mask
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_actual_component_requires_exact_native_writer_RAM_alias_absence(original):
    result=proof.require_primary(original[0],original[1])
    assert result['no_selected_ram_datum_access'] is True
    assert result['selected_native_RAM_aliases']=={'ffff120e':'0100120e'}
