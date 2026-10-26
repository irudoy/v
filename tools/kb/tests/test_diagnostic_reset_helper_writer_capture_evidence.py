"""Helper full-register loop binding and actual constant-zero publication refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state,packed_transfer_evidence
from kb import diagnostic_state_reset_writer_contract as core,diagnostic_state_reset_writer_matrix as matrix
from kb import diagnostic_state_reset_writer_semantics as numeric,diagnostic_state_reset_writer_transfers as complete
from kb import diagnostic_reset_helper_writer_transfers as transfers,diagnostic_reset_helper_writer_capture_evidence as proof


def reconstructed(**updates):
    source=core.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    case=dict(matrix.DEFAULTS,entry=core.ENTRY,index=0,kind='helper-zero-refusal',**updates)
    context=matrix.context(source,case);memory=matrix.memory(case);fixture,_=core.fixture_for_case(source,image,case)
    cal=matrix.calibrations(source,image,case);sp=0x30000000;continuation=0x30010000;sr=context[18]|0x08000400
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,core.ENTRY,sr,trace=True)
    value=numeric.evaluate(core.ENTRY,memory,cal,context,sr,bytes(frame),sp,continuation)
    observed=dict(entry=core.ENTRY,context=context,sp=sp,continuation=continuation,sr_before=sr,
        memory_before=(memory,),memory_after=(matrix.physical_ordinary(result['ram'],memory),),
        native_before=matrix.native_bytes(memory),native_after=matrix.native_bytes(result['ram']),
        frame_before=bytes(frame),frame_after=result['frame'],exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    assert complete.require(observed,result,value,fixture) is True
    assert transfers.require(observed,result,value) is True
    return observed,result,value


@pytest.mark.parametrize('gate',(0,64))
@pytest.mark.parametrize('prior',(0,1,127,128,255))
def test_real_helper_zero_store_binds_full_registers_iteration_and_separate_shadow(gate,prior):
    observed,result,value=reconstructed(byte_41e1=gate,prior_99c7=prior,raw_r4=0xF1234567)
    writes=[row for row in result['accesses'] if row['site']==0x2E77A]
    assert len(writes)==4 and writes[3]==dict(site=0x2E77A,address=proof.TARGET,width_bytes=1,register=7,mode='write',domain='native-io',bytes='00')
    assert observed['native_before'][proof.NATIVE_OFFSET]==prior and observed['native_after'][proof.NATIVE_OFFSET]==0
    assert observed['memory_after'][0][proof.OFFSET]==prior
    assert result['calls'][0]['entry']['registers'][4]==0xF1234567


@pytest.mark.parametrize('fault',('omit-store','duplicate-store','store-PC','store-register','store-width','store-address','nonzero',
    'full-R7','pointer','counter','bound','opcode','callee-SP','omit-iteration','pre-call-R4','post-delay-R4','call-target','call-PR','return','delay'))
def test_helper_refuses_matching_low_zero_with_substituted_complete_instruction_or_call(fault):
    observed,result,value=reconstructed(prior_99c7=7)
    store=next(row for row in result['accesses'] if row['address']==proof.TARGET)
    loop=[row for row in result['trace'] if row['site']==0x2E77A];selected=loop[3]
    if fault=='omit-store':result['accesses'].remove(store)
    elif fault=='duplicate-store':result['accesses'].append(deepcopy(store))
    elif fault in ('store-PC','store-register','store-width','store-address'):store[{'store-PC':'site','store-register':'register','store-width':'width_bytes','store-address':'address'}[fault]]+=1
    elif fault=='nonzero':store['bytes']='01'
    elif fault in ('full-R7','pointer','counter','bound','callee-SP'):
        registers=list(selected['before']['registers']);registers[{'full-R7':7,'pointer':5,'counter':6,'bound':4,'callee-SP':15}[fault]]^=0x100
        selected['before']['registers']=tuple(registers)
    elif fault=='opcode':selected['word']^=1
    elif fault=='omit-iteration':result['trace'].remove(loop[0])
    elif fault in ('pre-call-R4','post-delay-R4'):
        target=result['calls'][0] if fault=='pre-call-R4' else result['calls'][0]['entry']
        registers=list(target['registers']);registers[4]^=1;target['registers']=tuple(registers)
    elif fault=='call-target':result['calls'][0]['target']+=2
    elif fault=='call-PR':result['calls'][0]['entry']['pr']+=2
    elif fault=='return':next(row for row in result['trace'] if row['site']==0x2E816)['branches'][0]['target']+=2
    else:next(row for row in result['trace'] if row['site']==0x2E818)['delay_slot']=False
    with pytest.raises(ValueError):transfers.require(observed,result,value)


@pytest.fixture(scope='module')
def publication_pairs():
    # Controlled complete publication records isolate the constant-writer boundary.
    source=core.descriptor(repo.ROOT);image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();pairs=[]
    for gate in (0,64):
        for prior in range(256):
            case=dict(matrix.DEFAULTS,entry=core.ENTRY,index=0,kind='helper-publication-refusal',byte_41e1=gate,prior_99c7=prior)
            memory=matrix.memory(case);native=bytearray(matrix.native_bytes(memory));native[proof.NATIVE_OFFSET]=0
            observed=dict(memory_before=(memory,),memory_after=(memory,),native_before=matrix.native_bytes(memory),native_after=bytes(native),
                entry=core.ENTRY,context=matrix.context(source,case),frame_before=bytes(192),sp=0x30000000,continuation=0x30010000,
                abi_before=packed_transfer_evidence.ABI,sr_before=0,calibration_before=matrix.calibrations(source,image,case),bound_before=b'fixed-source-bytes')
            pairs.append((observed,dict(gate=bool(gate))))
    assert proof.require_publications(pairs)==dict(helper_constant_writer_inputs=dict(gate_0_full_priors=True,gate_1_full_priors=True,exact_actual_zero_store=True))
    return pairs


def test_constant_zero_requires_all_actual_priors_and_keeps_one_final_output(publication_pairs):
    assert {observed['native_after'][proof.NATIVE_OFFSET] for observed,value in publication_pairs}=={0}
    assert proof.require_publications(publication_pairs)['helper_constant_writer_inputs']['exact_actual_zero_store'] is True


@pytest.mark.parametrize('fault',('missing-prior','one-gate','echo','ordinary-copy','other-input','detached-prior','bool-gate'))
def test_constant_publication_refuses_missing_priors_echoes_or_other_input_changes(publication_pairs,fault):
    pairs=[(dict(observed),dict(value)) for observed,value in publication_pairs]
    if fault=='missing-prior':pairs=[pair for pair in pairs if pair[0]['native_before'][proof.NATIVE_OFFSET]!=7]
    elif fault=='one-gate':pairs=[pair for pair in pairs if pair[1]['gate']]
    else:
        observed,value=pairs[1]
        if fault=='echo':
            raw=bytearray(observed['native_after']);raw[proof.NATIVE_OFFSET]=1;observed['native_after']=bytes(raw)
        elif fault in ('ordinary-copy','detached-prior'):
            field='memory_after' if fault=='ordinary-copy' else 'memory_before';raw=bytearray(observed[field][0]);raw[proof.OFFSET]=0;observed[field]=(bytes(raw),)
        elif fault=='other-input':observed['sp']+=4
        else:value['gate']=0
    with pytest.raises(ValueError):proof.require_publications(pairs)
