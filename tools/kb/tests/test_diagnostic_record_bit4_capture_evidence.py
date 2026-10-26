"""Actual complete bit4 writer stream, physical carriers, computed outputs and refusals."""
from copy import deepcopy
import hashlib
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import diagnostic_record_bit4_contract as contract, diagnostic_record_bit4_matrix as matrix
from kb import diagnostic_record_bit4_capture_evidence as proof, diagnostic_record_bit4_transfers as transfers


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['diagnostic_record_bit4_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('common B acceptance requires the complete original bit4 writer capture')
        pytest.skip('the complete original bit4 writer capture is unavailable')
    model=compile.build(repo.ROOT);result=proof.require_primary(model,record)
    for flag in ('exact_diagnostic_record_bit4_paths','complete_indexed_byte_OR_and_RTS_delay',
            'complete_CPU_SR_frame_RAM','complete_physical_member_preimages_and_publications',
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
        for raw in (0,16,128,255):
            case=next(row for row in declared['cases'] if row['kind']=='every-selected-byte-preimage'
                and row['raw_r4']==index and row[f'record_{index:03x}_2']==raw)
            observed=actual[case['index']]
            result,value=proof.require_state(declared,image,case,observed,repo.ROOT)
            selected[index,raw]=(case,observed,result,value)
    return declared,image,actual,selected


@pytest.mark.parametrize('index',contract.INDICES)
@pytest.mark.parametrize('raw',(0,16,128,255))
def test_actual_complete_leaf_preserves_full_signed_R0_and_exact_record_byte_RMW(windows,index,raw):
    _,_,_,selected=windows;case,observed,result,value=selected[index,raw]
    reads=[row for row in result['accesses'] if row['site']==0x8C974]
    writes=[row for row in result['accesses'] if row['site']==0x8C97A]
    assert len(reads)==len(writes)==1
    assert reads[0]['address']==writes[0]['address']==matrix.RAM_BASE+0x571A+3*index
    assert reads[0]['bytes']==bytes([raw]).hex() and writes[0]['bytes']==bytes([raw|16]).hex()
    before=next(row for row in result['trace'] if row['site']==0x8C97A)['before']['registers'][0]
    assert before==((raw|16) if raw<128 else (raw|16)|0xFFFFFF00)
    assert observed['memory_after'][0][0x571A+3*index]==raw|16
    assert result['trace'][-1]['site']==0x8C982 and result['trace'][-1]['delay_slot'] is True
    assert result['trace'][-1]['next']==observed['continuation']
    assert observed['exit']==value['exit'] and observed['frame_after']==observed['frame_before']


@pytest.mark.parametrize('fault',('register','SR','PR','GBR','MACH','MACL','frame','RAM','extra-read','extra-write',
    'extra-call','branch-site','branch-target','branch-delay','omit-return','code-byte','omit-code',
    'delay-slot','return-SP','intermediate-upper-R0','intermediate-full-R4','delay-store-register','delay-store-byte'))
def test_actual_full_state_index_carriers_physical_operands_and_real_delay_store_are_independent(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[0x129,128])
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
        key=fault.split('-')[1];result['branches'][0][key]=False if key=='delay' else 1
    elif fault=='omit-return':result['branches'].pop()
    elif fault=='code-byte':result['code'][contract.ENTRY]='0009'
    elif fault=='omit-code':result['code'].pop(contract.ENTRY)
    elif fault=='delay-slot':result['trace'][-1]['delay_slot']=False
    elif fault=='return-SP':
        registers=list(result['trace'][-1]['after']['registers']);registers[15]-=4
        result['trace'][-1]['after']['registers']=tuple(registers)
    elif fault in ('intermediate-upper-R0','intermediate-full-R4'):
        state=next(row for row in result['trace'] if row['site']==0x8C978)['after']
        registers=list(state['registers']);registers[0 if fault=='intermediate-upper-R0' else 4]^=0x10000
        state['registers']=tuple(registers)
    else:
        row=next(row for row in result['accesses'] if row['site']==0x8C982)
        row['register' if fault=='delay-store-register' else 'bytes']=0 if fault=='delay-store-register' else '00'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.mark.parametrize('fault',('site','mode','address','width_bytes','register','domain','bytes','omit','duplicate'))
def test_ordered_real_member_read_write_and_PC_operands_cannot_be_merged_or_replaced(windows,fault):
    declared,image,_,selected=windows;case,observed,result,value=deepcopy(selected[1,255])
    fixture,_=contract.fixture_for_case(declared['source'],image,case)
    if fault=='omit':result['accesses'].pop()
    elif fault=='duplicate':result['accesses'].append(deepcopy(result['accesses'][0]))
    else:
        row=result['accesses'][1];row[fault]=row[fault]^1 if type(row[fault]) is int else 'changed'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


@pytest.fixture(scope='module')
def positive(windows):
    declared,_,actual,_=windows;publications={}
    for at,observed in enumerate(actual):
        address=matrix.RAM_BASE+0x571A+3*observed['context'][4]
        publications[at]={(address,1):observed['memory_after'][0][address-matrix.RAM_BASE:address-matrix.RAM_BASE+1],
            (matrix.RAM_BASE+0x508C,1):observed['memory_after'][0][0x508C:0x508D]}
    proof.require_positive_alternatives(actual,declared,publications)
    return declared,actual,publications


@pytest.mark.parametrize('fault',('echo','arbitrary-computed-byte','identical-values','missing-common-publication','missing-index'))
def test_positive_causality_requires_distinct_exact_computed_actual_bytes_with_all_other_inputs_fixed(positive,fault):
    declared,actual,publications=deepcopy(positive)
    if fault=='missing-index':
        for observed in actual:observed['context']=tuple(0 if i==4 else value for i,value in enumerate(observed['context']))
    else:
        for at,observed in enumerate(actual):
            index=observed['context'][4];offset=0x571A+3*index;address=matrix.RAM_BASE+offset
            if fault=='missing-common-publication':publications[at].pop((address,1));continue
            before=observed['memory_before'][0][offset]
            raw=before if fault=='echo' else ((before|16)^1 if fault=='arbitrary-computed-byte' else 16)
            after=bytearray(observed['memory_after'][0]);after[offset]=raw;observed['memory_after']=(bytes(after),)
            publications[at][address,1]=bytes([raw])
    with pytest.raises(ValueError):proof.require_positive_alternatives(actual,declared,publications)
