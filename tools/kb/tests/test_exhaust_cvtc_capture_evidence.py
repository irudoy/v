"""Actual original CVTC raw state, causal output and physical/call refusal sources."""

from copy import deepcopy
import hashlib
import json

import pytest

from kb import compile,copy_evidence,repo,test_evidence
from kb import exhaust_cvtc_contract as contract,exhaust_cvtc_matrix as matrix
from kb import exhaust_cvtc_capture_evidence as proof,exhaust_cvtc_transfers as transfers
from kb import exhaust_cvtc_access_contract as owning


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['exhaust_cvtc_transition_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires the complete original CVTC capture')
        pytest.skip('the complete original CVTC capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    assert result['exact_cvtc_accesses'] is True and result['exact_input_premise']==contract.PREMISE
    assert result['exact_cvtc_gain_output'] is True
    assert len(result['conditional_branch_outcomes'])==len(proof.REQUIRED_BRANCHES)
    assert all(outcomes==['fallthrough','taken'] for outcomes in result['conditional_branch_outcomes'].values())
    for key in ('native_geometry_inference','automatic_resolution','scale_admission','units_admission',
            'sensor_producer_admission','natural_caller_reachability','hardware_qualification'):
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
    elif fault=='pool':packet['reconstruction']['pools'][0]['stock']+='00'
    elif fault=='alias':packet['aliases'][0]['alias']+=4
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


@pytest.mark.parametrize('path',(*proof.SOURCE_FILES,'tools/sh-elf-run/exhaust_cvtc_capture.py',
    'tools/sh-elf-run/stock_jk08a_exhaust_cvtc_transition.s','tools/sh-elf-run/stock_ignition_consumer_invoke.s',
    'tools/sh-elf-run/harness-exhaust-cvtc-paths.c','tools/kb/src/kb/proof_sources.py',
    'tools/kb/src/kb/proof_reuse.py','tools/kb/tests/test_ram_structure.py','tools/kb/tests/test_indexed_input_word.py'))
def test_actual_consumer_requires_complete_current_input_sources_before_domain_admission(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    choices=(
        ('state-off',0xC1DEC,'positive-state-reader',dict(mode=0)),
        ('state-on',0xC1DEC,'positive-state-reader',dict(mode=1)),
        ('cur-zero',0xC1DEC,'positive-current-state',dict(current=0)),
        ('cur-nonzero',0xC1DEC,'positive-current-state',dict(current=512)),
        ('mode-clear',0xC1DEC,'positive-mode-store',dict(flags=0)),
        ('mode-set',0xC1DEC,'positive-mode-store',dict(flags=5)),
        ('error-zero',0xC1DEC,'positive-error-payload',dict(error=0)),
        ('error-large',0xC1DEC,'positive-error-payload',dict(error=65535)),
        ('payload-zero',0xC2040,'positive-payload-duty',dict(payload=0)),
        ('payload-positive',0xC2040,'positive-payload-duty',dict(payload=0x01000000)),
        ('duty-off',0xC2040,'positive-mode-duty',dict(mode=0)),
        ('duty-on',0xC2040,'positive-mode-duty',dict(mode=1)),
        ('lag-zero',0xC2040,'positive-lag-duty',dict(lag=0)),
        ('lag-large',0xC2040,'positive-lag-duty',dict(lag=65535)),
        ('copy-zero',0xC2040,'positive-lag-store',dict(current=0)),
        ('copy-nonzero',0xC2040,'positive-lag-store',dict(current=512)),
        ('curve-down',0xC1DEC,'curve-boundary',dict(coordinate=121,curve_kind=1)),
        ('curve-up',0xC1DEC,'curve-boundary',dict(coordinate=121,curve_kind=2)),
        ('curve-upper',0xC1DEC,'curve-boundary',dict(coordinate=255,curve_kind=2)),
        ('alternate',0xC1DEC,'alternate-wrap',dict(term_a=32768,term_b=32768,accumulator=0x08000001)))
    for name,entry,kind,changes in choices:
        case=next(row for row in declared['cases'] if row['entry']==entry and row['kind']==kind
            and all(row[key]==value for key,value in changes.items()))
        observed=actual[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
        selected[name]=(case,observed,result,value)
    return declared,image,selected


def test_eleven_originals_require_real_output_changes_under_complete_fixed_other_inputs(windows):
    declared,_,selected=windows
    proof.require_positive_alternatives([row[1] for row in selected.values()],
        [row[3] for row in selected.values()],declared,owning.descriptor(repo.ROOT)['reference'])
    for low,high in (('cur-zero','cur-nonzero'),('mode-clear','mode-set'),('error-zero','error-large'),
            ('payload-zero','payload-positive'),('duty-off','duty-on'),('lag-zero','lag-large'),('copy-zero','copy-nonzero')):
        assert selected[low][1]['memory_after']!=selected[high][1]['memory_after']


@pytest.mark.parametrize('name',('curve-down','curve-up','curve-upper','alternate','duty-on','lag-large','copy-nonzero'))
@pytest.mark.parametrize('fault',('return-site','return-target','omit-return','extra-call',
    'physical-site','physical-address','physical-width','physical-byte','omit-read','duplicate-read','omit-pool','code'))
def test_actual_physical_width_byte_order_and_natural_return_boundaries_are_independent(windows,name,fault):
    declared,image,selected=windows;case,observed,result,value=deepcopy(selected[name])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    returned=next(row for row in result['branches'] if row['kind']=='return')
    accessed=next(row for row in result['accesses'] if row['domain']=='ram')
    if fault=='return-site':returned['site']+=2
    elif fault=='return-target':returned['target']+=2
    elif fault=='omit-return':result['branches'].remove(returned)
    elif fault=='extra-call':result['calls'].append(deepcopy(result['calls'][0]))
    elif fault=='physical-site':accessed['site']+=2
    elif fault=='physical-address':accessed['address']+=2
    elif fault=='physical-width':accessed['width_bytes']=3
    elif fault=='physical-byte':accessed['bytes']='ff'*accessed['width_bytes']
    elif fault=='omit-read':result['accesses'].remove(accessed)
    elif fault=='duplicate-read':result['accesses'].append(deepcopy(accessed))
    elif fault=='code':result['code'][next(iter(result['code']))]='0009'
    else:
        pool=next(row for row in result['accesses'] if row['domain']=='rom'
            and int.from_bytes(fixture[row['site']:row['site']+2],'big')>>12 in (9,13))
        result['accesses'].remove(pool)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('name',('curve-up','curve-upper','duty-on'))
@pytest.mark.parametrize('fault',('target','site','return','sp','gbr','mach','post-delay-operand'))
def test_actual_delayed_calls_require_exact_operands_targets_and_frame_phases(windows,name,fault):
    _,_,selected=windows;_,observed,result,value=deepcopy(selected[name]);call=result['calls'][0]
    if fault=='target':call['target']+=2
    elif fault=='site':call['site']+=2
    elif fault=='return':call['return_address']+=2
    elif fault=='sp':call['entry']['sp']-=4
    elif fault=='gbr':call['entry']['gbr']^=4
    elif fault=='mach':call['entry']['mach']^=4
    else:
        registers=list(call['entry']['registers']);registers[6 if name.startswith('curve-') else 0]^=1
        call['entry']['registers']=tuple(registers)
    with pytest.raises(ValueError):transfers.require_calls(observed,result,value)


@pytest.mark.parametrize('fault',('zero-divisor-code','wide-divisor-code','bank-branch','extra-return'))
def test_actual_explicit_branch_and_natural_return_premises_refuse_other_paths(windows,fault):
    _,_,selected=windows;_,observed,result,value=deepcopy(selected['curve-up'])
    if fault=='zero-divisor-code':result['code'][0x21D6A]='0009'
    elif fault=='wide-divisor-code':result['code'][0x21D76]='0009'
    elif fault=='bank-branch':next(row for row in result['branches'] if row['site']==0xC1EF0)['kind']='fallthrough'
    else:result['branches'].append(dict(site=0xC2000,target=observed['continuation'],kind='return',delay=True))
    with pytest.raises(ValueError):
        proof.require_premises(result,value);transfers.require_calls(observed,result,value)


@pytest.mark.parametrize('offset',(0,4,8,12,16,20,68,76,80,84,88,132,136,180,184,344,348,368,372,376,536,560,564,568))
def test_complete_original_observer_requires_all_CPU_SP_PR_ABI_frame_and_SR_bytes(original,offset):
    packet=deepcopy(original[2]);row=packet['observations'][0]
    data=bytearray.fromhex(row['observation']);data[offset]^=1;row['observation']=data.hex()
    restream(packet);refuse(original,packet)


@pytest.mark.parametrize('name',('curve-up','alternate','duty-on','lag-large','copy-nonzero'))
@pytest.mark.parametrize('offset',(0,0x1108,0x143A,0x1AA8,0x1AAE,0x1AB6,0x1B1A,0x1B1D,0x1C72,0xFFFF))
def test_actual_complete_terminal_RAM_requires_exact_scalar_state_and_untouched_neighbors(windows,name,offset):
    declared,image,selected=windows;case,observed,_,_=deepcopy(selected[name])
    data=bytearray(observed['memory_after'][0]);data[offset]^=1;observed['memory_after']=(bytes(data),)
    with pytest.raises(ValueError):proof.require_state(declared,image,case,observed,repo.ROOT)


@pytest.mark.parametrize('identity',tuple(row[0] for row in owning.IDENTITIES))
def test_fixed_other_inputs_cannot_be_replaced_by_unchanged_actual_outputs(windows,identity):
    declared,_,selected=windows
    row=next(row for row in owning.descriptor(repo.ROOT)['reference'] if row['id']==identity)
    actual=deepcopy([item[1] for item in selected.values()]);values=[item[3] for item in selected.values()]
    for observed in actual:
        observed['memory_after']=(bytes(65536),)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,values,declared,[row])
