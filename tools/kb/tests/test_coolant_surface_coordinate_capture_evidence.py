"""Full actual coordinate transfers, signed returns, complete state and causal refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import coolant_surface_coordinate_contract as contract,coolant_surface_coordinate_matrix as matrix
from kb import coolant_surface_coordinate_semantics as numeric,coolant_surface_coordinate_transfers as transfers
from kb import coolant_surface_coordinate_capture_evidence as proof


def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-coolant-coordinate-refusal');value.update(updates);return value


def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);cal=matrix.calibrations(source,image,value)
    memory=matrix.memory(value);context=matrix.context(source,value);sp=0x30000000;continuation=0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    independent=numeric.evaluate(memory,cal,bytes(frame));bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        bound_before=bound,bound_after=bound,memory_before=(memory,),memory_after=(result['ram'],),
        frame_before=bytes(frame),frame_after=result['frame'],calibration_before=cal,calibration_after=cal,
        sr_before=context[18],abi_before=tuple(range(12)),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,independent,fixture)
    return observed,result,independent,fixture


@pytest.mark.parametrize('coolant',(0,1,31,32,127,128,223,224,225,255))
@pytest.mark.parametrize('inner',(0,1,223,224,255))
def test_actual_signed_loads_unsigned_arguments_and_complete_publication(coolant,inner):
    observed,result,value,fixture=reconstructed(coolant_snapshot=coolant,inner_snapshot=inner)
    trace={r['site']:r for r in result['trace']}
    assert trace[0x52582]['after']['registers'][0]==(coolant-256 if coolant&128 else coolant)&0xFFFFFFFF
    assert trace[0x52586]['after']['registers'][5]==coolant
    assert trace[0x5258E]['after']['registers'][6]==inner
    assert int.from_bytes(observed['memory_after'][0][0x1652:0x1654],'big')==value['value']==value['surface_value']


@pytest.mark.parametrize('updates',(
    dict(coolant_snapshot=1,inner_snapshot=1,surface=[255 if i%2 else 0 for i in range(64)]),
    dict(coolant_snapshot=223,inner_snapshot=223,surface=[0 if i%2 else 255 for i in range(64)]),
    dict(coolant_snapshot=255,inner_snapshot=255,surface=[255]*64),
    dict(word_1222=1,word_curve=[0,65535,1,32768,32767,65534,255,65535]),
    dict(word_1222=257,word_curve=[65535,0,65535,0,65535,0,65535,0]),
    dict(word_1222=1792,word_curve=[32768]*8),
    dict(word_1222=65535,word_curve=[65535]*8,surface=[255]*64)))
def test_full_surface_fraction_directions_word_endpoints_and_output_saturation(updates):reconstructed(**updates)


@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width','signed-load',
    'unsigned-R5','delay-R6','surface-return','live-R14','word-return','full-shift','word-fraction',
    'product-MACL','publication-R2','return-delay','saved-GBR','helper-argument','tail-stride',
    'GBR-rebase','fake-prior-read','opcode'))
def test_matching_output_word_cannot_replace_complete_live_state_and_real_calls(fault):
    observed,result,value,fixture=reconstructed(coolant_snapshot=255,inner_snapshot=255,word_1222=1)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x100,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x52582)['width_bytes']=2
    elif fault in ('signed-load','unsigned-R5','delay-R6','surface-return','live-R14','word-return','full-shift','word-fraction','publication-R2','tail-stride'):
        site,phase,register={'signed-load':(0x52582,'after',0),'unsigned-R5':(0x52586,'after',5),
            'delay-R6':(0x5258E,'after',6),'surface-return':(0x52590,'before',0),'live-R14':(0x52590,'after',14),
            'word-return':(0x525AE,'before',0),'full-shift':(0x5259C,'after',2),'word-fraction':(0x26A94,'after',3),
            'publication-R2':(0x525CC,'before',2),'tail-stride':(0x26770,'before',5)}[fault]
        row=next(r for r in result['trace'] if r['site']==site);registers=list(row[phase]['registers'])
        registers[register]^=0x10000;row[phase]['registers']=tuple(registers)
    elif fault=='product-MACL':next(r for r in result['trace'] if r['site']==0x525B0)['after']['macl']^=1
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-GBR':next(r for r in result['accesses'] if r['site']==0x5257C)['address']+=4
    elif fault=='helper-argument':
        call=result['calls'][0];registers=list(call['entry']['registers']);registers[5]^=0x10000;call['entry']['registers']=tuple(registers)
    elif fault=='GBR-rebase':next(r for r in result['trace'] if r['site']==0x52580)['after']['gbr']+=4
    elif fault=='fake-prior-read':next(r for r in result['accesses'] if r['site']==0x52592)['address']=matrix.RAM_BASE+0x1652
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def causal_pairs():
    pairs=[]
    for raw in (0,32):
        observed,result,value,fixture=reconstructed(coolant_snapshot=raw);pairs.append((observed,value))
    return pairs


def test_real_coordinate_needs_changed_actual1652_with_other_inputs_fixed():
    assert proof.require_causal_alternatives(causal_pairs())=={'actual-coolant-coordinate-to1652':True}
    pairs=causal_pairs()
    for observed,value in pairs:
        raw=bytearray(observed['memory_after'][0]);raw[0x1652:0x1654]=bytes(2);observed['memory_after']=(bytes(raw),);value['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)
    with pytest.raises(ValueError):proof.require_causal_alternatives(causal_pairs()[:1])


def test_prior1652_is_overwritten_without_changing_complete_other_state():
    pairs=[]
    for prior in (0,1,32767,32768,65535):
        for coordinate in (0,223):
            observed,result,value,fixture=reconstructed(prior_1652=prior,coolant_snapshot=coordinate);pairs.append((observed,value))
    assert proof.require_prior_publication_invariance(pairs) is True
    exit_state=pairs[-1][0]['exit'];pairs[-1][0]['exit']=(*exit_state[:-1],exit_state[-1]^1)
    with pytest.raises(ValueError):proof.require_prior_publication_invariance(pairs)


def test_raw_packet_refuses_duplicate_keys_and_incomplete_self_admission():
    with pytest.raises(ValueError):proof.objects([('schema',1),('schema',1)])
    with pytest.raises(ValueError):proof.require_witness(None,dict(schema=1,semantic_admission=True),{})
