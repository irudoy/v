"""Actual complete high-bit clearer stream, physical carriers, computed outputs and refusals."""
from copy import deepcopy
import hashlib
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import diagnostic_record_highbit_clear_contract as contract, diagnostic_record_highbit_clear_matrix as matrix
from kb import diagnostic_record_highbit_clear_capture_evidence as proof, diagnostic_record_highbit_clear_transfers as transfers


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['diagnostic_record_highbit_clear_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('common B acceptance requires the complete original high-bit clearer capture')
        pytest.skip('the complete original high-bit clearer capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    for flag in ('exact_diagnostic_record_highbit_clear_paths','complete_AND7F_read_write_RTS_delay',
            'complete_sentinel_no_RAM_access','complete_full_R4_modulo_addressing','complete_CPU_SR_frame_RAM','complete_physical_member_preimages_and_publications',
            'fixed_other_actual_common_member_alternatives','complete_native_owner_function_TEST_ledger',
            'no_array_extent_inference','no_selected_datum_absence_inference'):
        assert result[flag] is True
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
def test_original_capture_requires_every_source_stream_toolchain_and_observer_field(original,field):
    packet=deepcopy(original[2]);packet.pop(field);refuse(original,packet)


@pytest.mark.parametrize('fault',('code','pool','alias','returncode','timeout','compiler','simulator','observer',
    'header','omit','duplicate','swap','kind','entry','context-after','calibration-before','calibration-after',
    'bound-before','bound-after','outside-return'))
def test_actual_source_toolchain_complete_stream_and_fixture_bytes_refuse_substitution(original,fault):
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


@pytest.mark.parametrize('path',proof.SOURCE_FILES)
def test_actual_consumer_binds_every_current_independent_source(original,path):
    inputs=deepcopy(original[1]['candidate']['producer_inputs']);inputs.pop(path)
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


@pytest.fixture(scope='module')
def windows(original):
    declared=original[2]['declaration'];image=repo.images()['JK08A'].path.read_bytes()
    actual=proof.observations(original[2],declared);selected={}
    for index in contract.INDICES:
        for raw in (0,1,128,255):
            field='record_000_1' if index==0xFFFFFFFF else matrix.selected_field(index)
            kind='inert-sentinel-complete-preimages' if index==0xFFFFFFFF else 'every-physical-selected-byte-preimage'
            case=next(row for row in declared['cases'] if row['kind']==kind and row['raw_r4']==index and row[field]==raw)
            observed=actual[case['index']];result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
            selected[index,raw]=(case,observed,result,value)
    return declared,image,actual,selected


@pytest.mark.parametrize('index',tuple(i for i in contract.INDICES if i!=0xFFFFFFFF))
@pytest.mark.parametrize('raw',(0,1,128,255))
def test_actual_source_sign_extension_AND_and_RTS_delay_keep_complete_full_width_state(windows,index,raw):
    _,_,_,selected=windows;case,observed,result,value=selected[index,raw]
    address=(matrix.RAM_BASE+0x5719+3*index)&0xFFFFFFFF
    assert [(event['site'],event['mode'],event['bytes']) for event in result['accesses'] if event['domain']=='ram']==[
        (0x8C35A,'read',bytes([raw]).hex()),(0x8C360,'write',bytes([raw&0x7F]).hex())]
    assert all(event['address']==address for event in result['accesses'] if event['domain']=='ram')
    loaded=next(row for row in result['trace'] if row['site']==0x8C35A)['after']['registers'][0]
    assert loaded==(raw if raw<128 else raw|0xFFFFFF00)
    assert observed['exit'][-1]==raw&0x7F and observed['memory_after'][0][address-matrix.RAM_BASE]==raw&0x7F
    assert result['trace'][-1]['site']==0x8C360 and result['trace'][-1]['delay_slot'] is True
    assert result['trace'][-1]['next']==observed['continuation'] and observed['exit']==value['exit']


@pytest.mark.parametrize('raw',(0,1,128,255))
def test_actual_sentinel_has_no_RAM_operand_and_uses_its_own_real_RTS_and_nop_delay(windows,raw):
    _,_,_,selected=windows;case,observed,result,value=selected[0xFFFFFFFF,raw]
    assert all(event['domain']=='rom' for event in result['accesses'])
    assert observed['memory_after']==observed['memory_before'] and observed['frame_after']==observed['frame_before']
    assert observed['exit'][-1]==0xFFFFFFFF and result['trace'][-1]['site']==0x8C364
    assert result['trace'][-1]['delay_slot'] is True
    assert proof.computed_publications(observed,result)=={}


@pytest.mark.parametrize('fault',('register','SR','PR','GBR','MACH','MACL','frame','RAM','extra-read','extra-write',
    'extra-call','branch-site','branch-target','branch-delay','omit-return','code-byte','omit-code',
    'delay-slot','return-SP','intermediate-upper-R0','intermediate-full-R4','delay-store-register','delay-store-byte',
    'trace-only-physical'))
def test_actual_full_state_physical_address_carriers_branches_and_delay_are_independent(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[0xAAAAAAAB,128])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault in ('register','SR','PR','GBR','MACH','MACL'):
        key={'register':'registers','SR':'sr','PR':'pr','GBR':'gbr','MACH':'mach','MACL':'macl'}[fault]
        if key=='registers':result[key]=(result[key][0]^1,*result[key][1:])
        else:result[key]^=1
    elif fault=='frame':result['frame']=bytes([result['frame'][0]^1])+result['frame'][1:]
    elif fault=='RAM':result['ram']=bytes([result['ram'][0]^1])+result['ram'][1:]
    elif fault in ('extra-read','extra-write'):
        result['accesses'].append(dict(site=contract.ENTRY,mode='read' if fault=='extra-read' else 'write',
            address=matrix.RAM_BASE+0x5718,width_bytes=1,register=0,domain='ram',bytes='a5'))
    elif fault=='extra-call':result['calls'].append(dict(site=contract.ENTRY,target=0x8C942))
    elif fault.startswith('branch-'):
        key=fault.split('-')[1];row=result['branches'][0];row[key]=not row[key] if key=='delay' else 1
    elif fault=='omit-return':result['branches'].pop()
    elif fault=='code-byte':result['code'][contract.ENTRY]='0009'
    elif fault=='omit-code':result['code'].pop(contract.ENTRY)
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    elif fault=='return-SP':
        registers=list(result['trace'][-1]['after']['registers']);registers[15]-=4
        result['trace'][-1]['after']['registers']=tuple(registers)
    elif fault in ('intermediate-upper-R0','intermediate-full-R4'):
        state=next(row for row in result['trace'] if row['site']==0x8C35A)['after']
        registers=list(state['registers']);registers[0 if fault=='intermediate-upper-R0' else 4]^=0x10000
        state['registers']=tuple(registers)
    elif fault=='trace-only-physical':
        row=next(row for row in result['trace'] if row['site']==0x8C35A)
        row['accesses']=deepcopy(row['accesses']);row['accesses'][0]['address']+=1
    else:
        row=next(row for row in result['accesses'] if row['site']==0x8C360)
        if fault=='delay-store-register':row['register']=1
        else:row['bytes']=bytes([int(row['bytes'],16)^1]).hex()
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('sentinel-store','sentinel-read','sentinel-return','active-return','active-byte'))
def test_actual_publication_boundary_refuses_an_invented_sentinel_effect_or_detached_actual_R0(windows,fault):
    _,_,_,selected=windows
    case,observed,result,value=deepcopy(selected[0xFFFFFFFF if fault.startswith('sentinel') else 0,128])
    if fault in ('sentinel-store','sentinel-read'):
        result['accesses'].append(dict(site=0x8C364,mode='write' if fault=='sentinel-store' else 'read',
            address=matrix.RAM_BASE+0x5719,width_bytes=1,register=0,domain='ram',bytes='80'))
    elif fault.endswith('return'):observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    else:
        after=bytearray(observed['memory_after'][0]);after[0x5719]^=1;observed['memory_after']=(bytes(after),)
    with pytest.raises(ValueError):proof.computed_publications(observed,result)


@pytest.fixture(scope='module')
def positive(windows):
    declared,_,actual,_=windows;publications={}
    for at,observed in enumerate(actual):
        index=observed['context'][4]
        if index==0xFFFFFFFF:publications[at]={};continue
        address=(matrix.RAM_BASE+0x5719+3*index)&0xFFFFFFFF;offset=address-matrix.RAM_BASE
        publications[at]={(address,1):observed['memory_after'][0][offset:offset+1]}
    proof.require_positive_alternatives(actual,declared,publications)
    return declared,actual,publications


@pytest.mark.parametrize('fault',('echo','returned-scalar','missing-publication','held-input','write-set-only'))
def test_causal_original_requires_changed_actual_RAM_and_return_with_other_complete_inputs_fixed(positive,fault):
    declared,actual,publications=deepcopy(positive)
    if fault=='held-input':
        for at,observed in enumerate(actual):
            if observed['context'][4]==0:
                context=list(observed['context']);context[0]=at;observed['context']=tuple(context)
    elif fault=='write-set-only':
        for case,observed in zip(declared['cases'],actual):
            if case['kind']!='fixed-other-complete-index-selection':continue
            after=bytearray(observed['memory_after'][0])
            for index in contract.INDICES:
                if index!=0xFFFFFFFF:after[(0x5719+3*index)&0xFFFFFFFF]=0x7F
            observed['memory_after']=(bytes(after),)
    else:
        at=next(i for i,observed in enumerate(actual) if observed['context'][4]==0
            and observed['memory_before'][0][0x5719]==128)
        observed=actual[at]
        if fault=='echo':
            after=bytearray(observed['memory_after'][0]);after[0x5719]=128;observed['memory_after']=(bytes(after),)
            publications[at][matrix.RAM_BASE+0x5719,1]=b'\x80'
        elif fault=='returned-scalar':observed['exit']=(*observed['exit'][:-1],1)
        else:publications[at].clear()
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)


