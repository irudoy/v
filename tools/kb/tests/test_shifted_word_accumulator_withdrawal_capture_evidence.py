"""Actual GNU raw-original, complete state, physical and independent causal refusals."""
from copy import deepcopy
import hashlib
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import shifted_word_accumulator_withdrawal_contract as contract
from kb import shifted_word_accumulator_withdrawal_capture_evidence as proof
from kb import shifted_word_accumulator_withdrawal_transfers as transfers


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness'][proof.COMPONENT]
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the complete B acceptance requires the actual natural accumulator original')
        pytest.skip('the complete natural accumulator original is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_shifted_word_accumulator_withdrawal_paths'] is True
    assert result['no_selected_datum_access'] is True and result['complete_native_control_window'] is True
    assert result['complete_bounded_shift_and_saturated_word'] is True
    assert set(result['causal_inputs'])=={'gate','native_gate','metric','word','prior','factor','shift','threshold'}
    assert len(result['native_bindings'])==2
    assert proof.require_owning_result(result) is True
    for key in ('native_geometry_inference','scale_admission','units_admission','native_identity_admission',
            'natural_caller_reachability','natural_scheduling_inference','hardware_qualification'):
        assert result[key] is False
    return model,record,packet,result


@pytest.mark.parametrize('flag',proof.OWNING_FLAGS)
def test_owning_boundary_refuses_an_omitted_or_false_independent_obligation(original,flag):
    result=deepcopy(original[3]);result[flag]=False
    with pytest.raises(ValueError):proof.require_owning_result(result)


@pytest.mark.parametrize('fault',('missing','extra','owner','function','original','shape'))
def test_owning_boundary_refuses_a_changed_exact_native_binding(original,fault):
    result=deepcopy(original[3])
    if fault=='missing':result['native_bindings'].pop()
    elif fault=='extra':result['native_bindings'].append(deepcopy(result['native_bindings'][0]))
    elif fault=='shape':result['native_bindings']={}
    else:result['native_bindings'][0][{'owner':'meaning','function':'function_meaning','original':'original_claim_sha256'}[fault]]='changed'
    with pytest.raises(ValueError):proof.require_owning_result(result)


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
def test_actual_primary_requires_every_exact_raw_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','native-window',
    'observer','header','omit','duplicate','swap','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after','native-before','native-after','outside-return'))
def test_actual_complete_original_refuses_source_toolchain_native_or_transport_substitution(original,fault):
    packet=deepcopy(original[2])
    if fault=='code':packet['reconstruction']['code'][0]['reconstructed']+='00'
    elif fault=='pool':packet['reconstruction']['pools'].pop()
    elif fault=='alias':packet['aliases'].append(dict(address=0,alias=4))
    elif fault=='returncode':packet['simulator']['returncode']=1
    elif fault=='timeout':packet['simulator']['timeout_seconds']=1
    elif fault=='compiler':packet['command'][0]='another-gcc'
    elif fault=='simulator':packet['simulator']['command'][0]='another-run'
    elif fault=='native-window':packet['simulator']['command'].pop(2)
    elif fault=='observer':packet['consumed'][proof.OBSERVER]+='00'
    elif fault=='header':packet['consumed'][proof.HEADER]+='00'
    elif fault=='outside-return':packet['boundaries'].append(dict(address=0xC2000,bytes='000b0009'))
    else:
        rows=packet['observations']
        if fault=='omit':rows.pop()
        elif fault=='duplicate':rows[-1]=deepcopy(rows[0])
        elif fault=='swap':rows[0],rows[-1]=rows[-1],rows[0]
        elif fault=='entry':rows[0]['entry']+=2
        else:
            field=fault.replace('-','_');raw=bytearray.fromhex(rows[0][field]);raw[0]^=1;rows[0][field]=raw.hex()
        restream(packet)
    refuse(original,packet)


@pytest.mark.parametrize('path',proof.SOURCE_FILES)
def test_actual_consumer_refuses_any_omitted_complete_source_input(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.mark.parametrize('fault',('duplicate-key','missing-native','extra-field','short-RAM','short-frame','bool-index'))
def test_actual_transport_refuses_duplicate_keys_incomplete_state_or_untyped_order(original,fault):
    packet=deepcopy(original[2]);row=packet['observations'][0]
    if fault=='duplicate-key':
        packet['stdout']=packet['stdout'].replace(proof.PREFIX+'{',proof.PREFIX+'{"schema":1,',1)
        packet['stdout_sha256']=hashlib.sha256(packet['stdout'].encode()).hexdigest()
    else:
        if fault=='missing-native':row.pop('native_after')
        elif fault=='extra-field':row['expected_word']=0
        elif fault=='short-RAM':row['ram_before']='1:a5'
        elif fault=='short-frame':row['observation']=row['observation'][:-2]
        else:row['index']=False
        restream(packet)
    refuse(original,packet)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);result={}
    wanted=(('active',dict(gate=32,native_gate=64,metric=200,word=32768,prior=1000,factor=128,shift=8,threshold=17)),
        ('zero-shift',dict(gate=32,native_gate=64,metric=200,word=32768,prior=1000,factor=128,shift=0,threshold=17)),
        ('zero-product-long-loop',dict(gate=32,native_gate=64,word=0,shift=255)),
        ('reset',dict(gate=0)),('native-inhibit',dict(gate=32,native_gate=0)))
    for name,changes in wanted:
        case=next(row for row in declared['cases'] if all(row[key]==value for key,value in changes.items()))
        observed=actual[case['index']];state,value=proof.require_state(declared,image,case,observed)
        result[name]=(case,observed,state,value)
    return declared,image,result


@pytest.mark.parametrize('fault',('unrelated-RAM','exit-register','exit-SR','entry-frame','exit-frame','native-mirror','callee','access-site',
    'access-address','access-width','access-mode','access-register','access-bytes','loop-branch','delay-slot','return','trace-register'))
def test_matching_word_cannot_replace_complete_state_physical_loop_or_natural_return(windows,fault):
    declared,image,rows=windows;case,observed,result,value=deepcopy(rows['active'])
    if fault=='unrelated-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x2222]^=1;observed['memory_after']=(bytes(raw),)
    elif fault in ('exit-register','exit-SR'):
        raw=list(observed['exit']);raw[0 if fault=='exit-SR' else 5]^=1;observed['exit']=tuple(raw)
    elif fault in ('entry-frame','exit-frame'):
        key='frame_before' if fault=='entry-frame' else 'frame_after';raw=bytearray(observed[key]);raw[100]^=1;observed[key]=bytes(raw)
    elif fault=='native-mirror':
        raw=bytearray(observed['native_before']);raw[0xC3]^=64;observed['native_before']=bytes(raw)
    elif fault=='callee':result['calls'].append(dict(site=0xA53D4,target=0x264CC))
    elif fault.startswith('access-'):
        key=fault[7:];key='width_bytes' if key=='width' else key
        result['accesses'][0][key]='changed' if key in ('mode','bytes') else 0
    elif fault=='loop-branch':result['branches'].pop()
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    elif fault=='return':result['trace'][-1]['next']+=2
    else:result['trace'][1]['before']['registers']=tuple([0]*16)
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    with pytest.raises(ValueError):
        if fault in ('entry-frame','native-mirror'):proof.require_state(declared,image,case,observed)
        else:transfers.require(observed,result,value,fixture)


def test_independent_scalar_counterfactuals_bind_actual_publications_and_fixed_other_inputs(windows):
    declared,image,rows=windows
    _,first,_,value=deepcopy(rows['active']);_,second,_,other=deepcopy(rows['zero-shift'])
    assert value['tags']['updated']!=other['tags']['updated']
    # One isolated two-row pair cannot supply the required alternatives for all eight real input domains.
    with pytest.raises(ValueError):proof.require_causal_alternatives([(first,value),(second,other)])
    other['tags']['updated']=value['tags']['updated']
    with pytest.raises(ValueError):proof.require_causal_alternatives([(first,value),(second,other)])
