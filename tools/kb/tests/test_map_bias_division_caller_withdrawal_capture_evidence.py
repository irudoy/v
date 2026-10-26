"""Actual complete raw original, selected-prior independence and state/physical refusals."""
from copy import deepcopy
import hashlib
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import map_bias_division_caller_withdrawal_contract as contract
from kb import map_bias_division_caller_withdrawal_capture_evidence as proof
from kb import map_bias_division_caller_withdrawal_transfers as transfers


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['map_bias_division_caller_withdrawal_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete natural map-bias caller original')
        pytest.skip('the complete natural map-bias caller original is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    for flag in ('exact_map_bias_division_caller_withdrawal_paths','complete_map_bias_and_axis_paths',
            'complete_positive_unsigned_division','complete_actual_fifth_word','complete_independent_frame',
            'complete_local_word_carrier','no_selected_datum_access','complete_selected_scalar_interval_absence',
            'derived_request_and_area_dependencies_preserved','complete_direct_helpers_same_primary'):
        assert result[flag] is True
    assert all(outcomes==['fallthrough','taken'] for outcomes in result['conditional_branch_outcomes'].values())
    assert result['fixed_branch_outcomes']=={f'{site:08x}':[wanted] for site,wanted in transfers.FIXED_BRANCHES.items()}
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
def test_actual_capture_requires_every_complete_raw_source_and_terminal_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','observer',
    'header','omit','duplicate','swap','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after','outside-return'))
def test_changed_bytes_toolchain_or_restreamed_observations_cannot_replace_the_actual_original(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'].pop()
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
        elif fault=='entry':rows[0]['entry']=0x22590
        else:
            key=fault.replace('-','_');raw=bytearray.fromhex(rows[0][key]);raw[0]^=1;rows[0][key]=raw.hex()
        restream(packet)
    refuse(original,packet)


@pytest.mark.parametrize('path',proof.SOURCE_FILES)
def test_actual_consumer_refuses_an_omitted_current_dependency(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared)
    case=next(row for row in declared['cases'] if row['kind']=='actual-coordinate-alternatives-fixed-other' and row['word_1702']==128)
    observed=actual[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
    return declared,image,case,observed,result,value,actual


@pytest.mark.parametrize('fault',('register','SR','entry-frame','exit-frame','unrelated-RAM','trace-state','trace-continuation',
    'delay-slot','physical-address','physical-width','physical-register','physical-byte','callee','post-delay-argument','return','fifth-word'))
def test_a_matching_final_scalar_cannot_replace_complete_state_physical_frame_or_real_calls(windows,fault):
    declared,image,case,observed,result,value,actual=deepcopy(windows)
    if fault in ('register','SR'):
        raw=list(observed['exit']);raw[0 if fault=='SR' else 5]^=1;observed['exit']=tuple(raw)
    elif fault in ('entry-frame','exit-frame'):
        key='frame_before' if fault=='entry-frame' else 'frame_after';raw=bytearray(observed[key]);raw[128]^=1;observed[key]=bytes(raw)
    elif fault=='unrelated-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x2222]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='trace-state':result['trace'][0]['after']['sr']^=1
    elif fault=='trace-continuation':result['trace'][0]['next']+=2
    elif fault=='delay-slot':next(row for row in result['trace'] if row['delay_slot'])['delay_slot']=False
    elif fault.startswith('physical-'):
        key={'address':'address','width':'width_bytes','register':'register','byte':'bytes'}[fault[9:]]
        result['accesses'][0][key]='changed' if key=='bytes' else 0
    elif fault=='callee':result['calls'][0]['target']=0x224F8
    elif fault=='post-delay-argument':
        call=next(row for row in result['calls'] if row['site']==0x70328)
        registers=list(call['entry']['registers']);registers[7]^=1;call['entry']['registers']=tuple(registers)
    elif fault=='return':result['calls'][0]['return_address']+=2
    else:next(row for row in result['trace'] if row['site']==0x7031A)['accesses'][0]['bytes']='0000'
    with pytest.raises(ValueError):transfers.require(observed,result,value,contract.fixture_for_case(declared['source'],image,case)[0])


@pytest.mark.parametrize('fault',('omit-mode','omit-prior','changed-frame','changed-RAM','changed-CPU'))
def test_selected_prior_independence_requires_both_actual_modes_and_every_fixed_other_preimage(windows,fault):
    declared,image,case,observed,result,value,actual=deepcopy(windows)
    selected=[(index,row) for index,row in enumerate(declared['cases']) if row['kind']=='selected-two-byte-scalar-prior-only']
    index,control=selected[-1]
    if fault=='omit-mode':
        for index,row in selected:
            if row['byte_18b4']==1:row['kind']='unregistered-control'
    elif fault=='omit-prior':control['kind']='unregistered-control'
    else:
        row=actual[index]
        if fault=='changed-frame':raw=bytearray(row['frame_after']);raw[0]^=1;row['frame_after']=bytes(raw)
        elif fault=='changed-RAM':raw=bytearray(row['memory_after'][0]);raw[0]^=1;row['memory_after']=(bytes(raw),)
        else:raw=list(row['exit']);raw[0]^=1;row['exit']=tuple(raw)
    with pytest.raises(ValueError):proof.require_selected_prior_independence(actual,declared)
