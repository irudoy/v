"""Actual complete nested array gate, exact calls/returns and positive R0 refusal sources."""
from copy import deepcopy
import hashlib,json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import diagnostic_record_composite_gate_contract as contract,diagnostic_record_composite_gate_matrix as matrix
from kb import diagnostic_record_composite_gate_capture_evidence as proof,diagnostic_record_composite_gate_transfers as transfers


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['diagnostic_record_composite_gate_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('common B acceptance requires the complete original diagnostic composite gate capture')
        pytest.skip('the complete original diagnostic composite gate capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    for flag in ('exact_diagnostic_record_composite_gate_paths','complete_actual_sentinel_and_short_circuit_calls',
            'complete_nested_indexed_array_reads','complete_CPU_SR_frame_RAM','fixed_other_actual_R0_alternatives',
            'complete_native_owner_function_TEST_ledger','no_array_extent_inference','no_selected_datum_absence_inference'):
        assert result[flag] is True
    assert result['fixed_branch_outcomes']=={'00025a1a':['fallthrough'],'00025a22':['fallthrough']}
    assert all(values==['fallthrough','taken'] for values in result['conditional_branch_outcomes'].values())
    for flag in ('native_identity_admission','native_geometry_inference','automatic_resolution','scale_admission',
            'units_admission','natural_caller_reachability','hardware_qualification'):
        assert result[flag] is False
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
def test_original_capture_requires_every_raw_stream_source_toolchain_and_observer_binding(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','observer',
    'header','omit','duplicate','swap','kind','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after','outside-return'))
def test_complete_actual_source_fixture_and_stream_cannot_be_substituted(original,fault):
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


@pytest.mark.parametrize('path',proof.SOURCE_FILES)
def test_actual_consumer_requires_every_complete_current_domain_and_native_source(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    for index in contract.INDICES:
        for raw in (0,32,64):
            case=next(case for case in declared['cases'] if case['kind']=='every-selected-byte-preimage'
                and case[f'record_{index:03x}_2']==raw and all(case[f'record_{other:03x}_2']==0 for other in contract.INDICES if other!=index))
            observed=actual[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
            selected[index,raw]=(case,observed,result,value)
    return declared,image,actual,selected


@pytest.mark.parametrize('index',contract.INDICES)
@pytest.mark.parametrize('raw',(32,64))
def test_actual_member_accesses_and_complete_post_delay_calls_end_at_the_first_active_record(windows,index,raw):
    declared,image,actual,selected=windows;case,observed,result,value=selected[index,raw]
    assert observed['exit'][-1]==value['output']==1 and value['active_index']==index
    assert len(result['calls'])==2+contract.INDICES.index(index)+1
    assert result['calls'][0]['entry']['registers'][4]==result['calls'][1]['entry']['registers'][4]==0xFFFFFFFF
    for call,predicate in zip(result['calls'],value['predicates']):
        assert call['target']==0x259E4 and call['entry']['registers'][4]==predicate['argument']
        assert call['entry']['sp']==observed['sp']-4 and call['entry']['pr']==call['return_address']
    accesses=[row for row in result['accesses'] if row['domain']=='ram']
    assert accesses[-1]['address']==matrix.RAM_BASE+0x571A+3*index
    assert accesses[-1]['site']==(0x259F6 if raw&64 else 0x25A02)
    assert {row['address'] for row in accesses}=={matrix.RAM_BASE+0x571A+3*other for other in contract.INDICES[:contract.INDICES.index(index)+1]}
    assert observed['memory_before']==observed['memory_after'] and result['trace'][-1]['site']==0x25A8A


@pytest.mark.parametrize('fault',('register','SR','PR','GBR','MACH','MACL','frame','RAM','extra-read','extra-write',
    'call-target','call-site','call-return','call-SP','call-pre-R4','call-post-R4','call-post-SR','call-post-PR',
    'branch-site','branch-target','branch-delay','omit-return','code-byte','omit-code','delay-slot','return-SP',
    'omit-sentinel','invent-sentinel-read','omit-late-call','intermediate-R0','intermediate-R3'))
def test_full_natural_caller_helper_and_short_circuit_state_refuse_detached_or_synthetic_substitutes(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[0x8C,0])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault in ('register','SR','PR','GBR','MACH','MACL'):
        key={'register':'registers','SR':'sr','PR':'pr','GBR':'gbr','MACH':'mach','MACL':'macl'}[fault]
        if key=='registers':result[key]=(result[key][0]^1,*result[key][1:])
        else:result[key]^=1
    elif fault=='frame':result['frame']=bytes([result['frame'][0]^1])+result['frame'][1:]
    elif fault=='RAM':result['ram']=bytes([result['ram'][0]^1])+result['ram'][1:]
    elif fault in ('extra-read','extra-write','invent-sentinel-read'):
        result['accesses'].append(dict(site=0x259F6,mode='write' if fault=='extra-write' else 'read',
            address=matrix.RAM_BASE+0x5718,width_bytes=1,register=0,domain='ram',bytes='a5'))
    elif fault.startswith('call-'):
        call=result['calls'][0]
        if fault in ('call-target','call-site','call-return','call-SP'):
            key={'call-target':'target','call-site':'site','call-return':'return_address','call-SP':'sp'}[fault];call[key]^=2
        elif fault in ('call-pre-R4','call-post-R4'):
            target=call if fault=='call-pre-R4' else call['entry'];registers=list(target['registers']);registers[4]^=0x10000;target['registers']=tuple(registers)
        else:call['entry']['sr' if fault=='call-post-SR' else 'pr']^=1
    elif fault.startswith('branch-'):
        key=fault.split('-')[1];result['branches'][0][key]=False if key=='delay' else 1
    elif fault=='omit-return':result['branches'].pop()
    elif fault=='code-byte':result['code'][contract.ENTRY]='0009'
    elif fault=='omit-code':result['code'].pop(contract.ENTRY)
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    elif fault=='omit-sentinel':result['calls'].pop(0)
    elif fault=='omit-late-call':result['calls'].pop()
    else:
        target=result['trace'][-1]['after'] if fault=='return-SP' else next(row for row in result['trace'] if row['site']==(0x25A10 if fault=='intermediate-R0' else 0x25A5E))['after']
        registers=list(target['registers']);registers[15 if fault=='return-SP' else 0 if fault=='intermediate-R0' else 3]^=0x10000;target['registers']=tuple(registers)
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('site','mode','address','width_bytes','register','domain','bytes','omit','duplicate'))
def test_exact_ordered_member_reads_PC_loads_and_PR_frame_words_are_independent(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[0x8C,0])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='omit':result['accesses'].pop()
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][0]))
    else:
        row=next(row for row in result['accesses'] if row['domain']=='ram');row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('identical-R0','input-echo','changed-other-input','missing-observation'))
def test_actual_positive_R0_requires_record_specific_fixed_other_numerical_alternatives(windows,fault):
    declared,_,actual,_=deepcopy(windows)
    if fault=='missing-observation':actual.pop()
    else:
        for at,observed in enumerate(actual):
            if fault=='changed-other-input':
                context=list(observed['context']);context[0]=at;observed['context']=tuple(context)
            else:
                returned=0 if fault=='identical-R0' else observed['memory_before'][0][0x571A+3*0x14]
                observed['exit']=(*observed['exit'][:-1],returned)
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared)
