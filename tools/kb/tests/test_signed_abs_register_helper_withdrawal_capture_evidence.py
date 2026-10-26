"""Actual complete-primary raw32 state, source, physical and prior refusals."""

from copy import deepcopy
import hashlib
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import signed_abs_register_helper_withdrawal_contract as contract
from kb import signed_abs_register_helper_withdrawal_capture_evidence as proof
from kb import signed_abs_register_helper_withdrawal_transfers as transfers
from kb import scalar_ram_leaf_withdrawal_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['signed_abs_register_helper_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete standalone raw32 helper original')
        pytest.skip('the complete standalone raw32 helper original is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert proof.require_owning_result(result) is True
    assert result['conditional_branch_outcomes']=={'00022592':['fallthrough','taken']}
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
def test_complete_original_requires_every_raw_source_and_state_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','observer',
    'header','omit','duplicate','swap','kind','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after','outside-return'))
def test_actual_toolchain_code_and_complete_original_stream_refuse_changed_bytes(original,fault):
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
            field=fault.replace('-','_');raw=bytearray.fromhex(rows[0][field]);raw[0]^=1;rows[0][field]=raw.hex()
        restream(packet)
    refuse(original,packet)


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,
    'tools/sh-elf-run/signed_abs_register_helper_withdrawal_capture.py',
    'tools/sh-elf-run/stock_jk08a_signed_abs_register_helper_withdrawal.s',
    'tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-signed-abs-register-helper-withdrawal-paths.c',
    'tools/kb/src/kb/proof_sources.py','tools/kb/src/kb/proof_reuse.py'))
def test_actual_consumer_requires_every_complete_current_source(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    for case,observed in zip(declared['cases'],actual):
        raw=observed['context'][4]
        if raw in (0,1,0xFFFFFFFF,0x80000000) and raw not in selected:
            result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
            selected[raw]=(case,observed,result,value)
    assert set(selected)=={0,1,0xFFFFFFFF,0x80000000}
    return declared,image,actual,selected


@pytest.mark.parametrize('raw',(0,1,0xFFFFFFFF,0x80000000))
@pytest.mark.parametrize('fault',('register','SR','PR','GBR','MACH','MACL','frame','RAM','extra-read','extra-write',
    'extra-call','branch-site','branch-target','branch-delay','omit-return','code-byte','omit-code','delay-slot','return-target'))
def test_actual_complete_state_physical_natural_branch_and_return_refusals(windows,raw,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[raw])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault in ('register','SR','PR','GBR','MACH','MACL'):
        key={'register':'registers','SR':'sr','PR':'pr','GBR':'gbr','MACH':'mach','MACL':'macl'}[fault]
        if key=='registers':result[key]=(result[key][0]^1,*result[key][1:])
        else:result[key]^=1
    elif fault in ('frame','RAM'):
        key='frame' if fault=='frame' else 'ram';result[key]=bytes([result[key][0]^1])+result[key][1:]
    elif fault in ('extra-read','extra-write'):
        result['accesses'].append(dict(site=0x22590,mode=fault.split('-')[1],address=0x01002C1C,
            width_bytes=1,register=4,domain='ram',bytes='a5'))
    elif fault=='extra-call':result['calls'].append(dict(site=0x22590,target=0x224FA))
    elif fault.startswith('branch-'):
        key=fault.split('-')[1];result['branches'][0][key]=not result['branches'][0][key] if key=='delay' else 1
    elif fault=='omit-return':result['branches'].pop()
    elif fault=='code-byte':result['code'][0x22590]='0009'
    elif fault=='omit-code':result['code'].pop(0x22590)
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    else:result['trace'][-1]['next']^=2
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('site',tuple(transfers.WORDS))
@pytest.mark.parametrize('phase',('before','after'))
@pytest.mark.parametrize('field',('registers','gbr','mach','macl','sr','pr'))
def test_actual_every_instruction_binds_all_independent_intermediate_state_fields(windows,site,phase,field):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[0x80000000])
    row=next(row for row in result['trace'] if row['site']==site)
    if field=='registers':row[phase][field]=(row[phase][field][0]^1,*row[phase][field][1:])
    else:row[phase][field]^=1
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def test_actual_fixed_other_argument_variation_requires_changed_computed_R0(windows):
    declared,_,actual,_=windows;proof.require_positive_alternatives(actual,declared)
    changed=deepcopy(actual)
    for observed in changed:observed['exit']=(*observed['exit'][:-1],0)
    with pytest.raises(ValueError):proof.require_positive_alternatives(changed,declared)


def test_actual_selected_raw_byte_priors_cannot_change_computed_state_or_lose_a_sign_class(windows):
    declared,_,actual,_=windows;proof.require_selected_prior_independence(actual,declared)
    changed=deepcopy(actual)
    index=next(index for index,case in enumerate(declared['cases']) if case['kind']=='selected-raw-byte-prior-only')
    changed[index]['exit']=(*changed[index]['exit'][:-1],changed[index]['exit'][-1]^1)
    with pytest.raises(ValueError):proof.require_selected_prior_independence(changed,declared)
    pairs=[(case,observed) for case,observed in zip(declared['cases'],actual) if observed['context'][4]!=0x80000000]
    reduced=dict(declared,cases=[case for case,observed in pairs])
    with pytest.raises(ValueError):proof.require_selected_prior_independence([observed for case,observed in pairs],reduced)


@pytest.mark.parametrize('form',('native','alias','overlap'))
def test_selected_native_root_and_ordinary_alias_refuse_any_data_access(form):
    rows=[row for row in owning.descriptor(repo.ROOT)['reference'] if row['component']=='signed_abs_register_helper_withdrawal_paths']
    original,native,alias=transfers.NATIVE_RAM_ROOTS[0];address=native if form=='native' else alias
    if form=='overlap':address-=1
    with pytest.raises(ValueError):transfers.require_no_selected_datum(dict(accesses=[dict(
        site=0x22590,mode='read',address=address,width_bytes=2,register=4,domain='ram')]),rows)
