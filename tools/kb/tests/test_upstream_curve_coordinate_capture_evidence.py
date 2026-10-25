"""Actual upstream return, derived delay R6, complete long output and causal refusals."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import upstream_curve_coordinate_contract as contract,upstream_curve_coordinate_matrix as matrix
from kb import upstream_curve_coordinate_semantics as numeric,upstream_curve_coordinate_transfers as transfers
from kb import upstream_curve_coordinate_capture_evidence as proof


def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-upstream-coordinate-refusal');value.update(updates);return value


def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);cal=matrix.calibrations(source,image,value)
    memory=matrix.memory(value);context=matrix.context(source,value);sp=0x30000000;continuation=0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    independent=numeric.evaluate(memory,cal,bytes(frame),context)
    bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        bound_before=bound,bound_after=bound,memory_before=(memory,),memory_after=(result['ram'],),
        frame_before=bytes(frame),frame_after=result['frame'],calibration_before=cal,calibration_after=cal,
        sr_before=context[18],abi_before=tuple(range(12)),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,independent,fixture)
    return observed,result,independent,fixture


@pytest.mark.parametrize('index',range(8))
@pytest.mark.parametrize('high',(0,0x7FFFFF00,0x80000000,0xFFFFFF00))
def test_actual_source_return_real_delay_R6_complete_fifth_word_and_long_publication(index,high):
    curve=[0]*9;curve[index]=10000
    observed,result,value,fixture=reconstructed(source_curve=curve,context=matrix.raw_context(fifth_word=high|index*32))
    trace={r['site']:r for r in result['trace']}
    assert value['source_return']==10000 and value['consumer_coordinate']==65335 and value['value']==5000
    assert trace[0xB7AB0]['before']['registers'][0]==10000
    assert trace[0xB7AB0]['after']['registers'][2]==10000
    assert trace[0xB7B16]['before']['registers'][6]==(-201)&0xFFFFFFFF
    assert trace[0xB7B16]['after']['registers'][6]==65335
    assert int.from_bytes(observed['memory_after'][0][0x3228:0x322C],'big')==5000
    assert observed['frame_before'][160:164]==observed['frame_after'][160:164]==(high|index*32).to_bytes(4,'big')


@pytest.mark.parametrize('context',(
    matrix.raw_context(H=0),matrix.raw_context(H=20),matrix.raw_context(H=1),
    matrix.raw_context(initial_long=0x80000000,local_byte=255),
    matrix.raw_context(initial_long=0x7FFFFFFF),matrix.raw_context(selector=0xA5B600FF)))
@pytest.mark.parametrize('source',(0,1,32768,65534,65535))
def test_signed_initial_clamps_division_bypass_guard_and_full_sentinel(context,source):
    reconstructed(context=context,source_curve=[source]*9,rom_8a30=255,rom_8832=255)


@pytest.mark.parametrize('updates,entry,fraction',(
    (dict(source_axis=[255]+[65535]*7,context=matrix.raw_context(H=20,fifth_word=1)),0x264CC,1),
    (dict(source_axis=[1]+[65281]*7,context=matrix.raw_context(H=20,fifth_word=255)),0x264CC,65534),
    (dict(output_axis=[0]+[65535]*15,source_curve=[65534]*9,context=matrix.raw_context(H=20)),0x264F8,1),
    (dict(output_axis=[0]+[65535]*15,source_curve=[1]*9,context=matrix.raw_context(H=20)),0x264F8,65534)))
def test_both_real_word_division_minimum_and_maximum_positive_brackets(updates,entry,fraction):
    observed,result,value,fixture=reconstructed(**updates)
    assert proof.curve(value,entry)['fraction']==fraction


@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width',
    'source-return','source-copy','source-extension','negative-product','delay-R6-before','delay-R6-after',
    'consumer-return','B-before-extension','B-after-extension','coefficient-before-extension',
    'publication-R2','full-fifth-word','return-delay','saved-GBR','helper-argument','GBR-rebase','opcode'))
def test_matching_long_output_cannot_replace_complete_state_or_actual_return_path(fault):
    observed,result,value,fixture=reconstructed(source_curve=[10000]*9)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x10,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x264E4)['width_bytes']=1
    elif fault in ('source-return','source-copy','source-extension','negative-product','delay-R6-before','delay-R6-after',
            'consumer-return','B-before-extension','B-after-extension','coefficient-before-extension','publication-R2','full-fifth-word'):
        site,phase,register={'source-return':(0xB7AB0,'before',0),'source-copy':(0xB7AB0,'after',2),
            'source-extension':(0xB7ACA,'after',6),'negative-product':(0xB7ADC,'after',6),
            'delay-R6-before':(0xB7B16,'before',6),'delay-R6-after':(0xB7B16,'after',6),
            'consumer-return':(0xB7B18,'before',0),'B-before-extension':(0xB7B5E,'before',12),
            'B-after-extension':(0xB7B5E,'after',12),'coefficient-before-extension':(0xB7B6E,'before',14),
            'publication-R2':(0xB7B84,'before',2),'full-fifth-word':(0xB7A58,'after',6)}[fault]
        row=next(r for r in result['trace'] if r['site']==site);registers=list(row[phase]['registers'])
        registers[register]^=0x10000;row[phase]['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-GBR':next(r for r in result['accesses'] if r['site']==0xB7A48)['address']+=4
    elif fault=='helper-argument':
        call=result['calls'][1];registers=list(call['entry']['registers']);registers[6]^=0x10000;call['entry']['registers']=tuple(registers)
    elif fault=='GBR-rebase':next(r for r in result['trace'] if r['site']==0xB7A4C)['after']['gbr']+=4
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)


def causal_pairs():
    pairs=[]
    for index in range(8):
        for raw in (0,10000):
            curve=[0]*9;curve[index]=raw
            observed,result,value,fixture=reconstructed(source_curve=curve,context=matrix.raw_context(fifth_word=index*32));pairs.append((observed,value))
    return pairs


def test_all_eight_source_words_need_changed_actual_coordinate_and_publication():
    pairs=causal_pairs();assert proof.require_causal_alternatives(pairs)=={'source-word-'+str(i):True for i in range(8)}
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs[:-2])
    for observed,value in pairs:
        raw=bytearray(observed['memory_after'][0]);raw[0x3228:0x322C]=bytes(4);observed['memory_after']=(bytes(raw),);value['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)


def test_echoed_source_or_actual_coordinate_without_changed_real_output_is_refused():
    pairs=causal_pairs()
    for observed,value in pairs:value['consumer_coordinate']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)


def test_prior3228_requires_complete_exit_RAM_frame_invariance():
    pairs=[]
    for prior in (0,1,0x7FFFFFFF,0x80000000,0xFFFFFFFF):
        observed,result,value,fixture=reconstructed(prior_3228=prior,source_curve=[10000]*9);pairs.append((observed,value))
    assert proof.require_prior_publication_invariance(pairs) is True
    exit_state=pairs[-1][0]['exit'];pairs[-1][0]['exit']=(*exit_state[:-1],exit_state[-1]^1)
    with pytest.raises(ValueError):proof.require_prior_publication_invariance(pairs)


def test_both_physical_guards_are_read_but_have_zero_arithmetic_weight():
    pairs=[]
    for name in ('source_curve','output_curve'):
        for guard in (0,65535):
            curve=list(matrix.DEFAULTS[name]);curve[-1]=guard
            observed,result,value,fixture=reconstructed(**{name:curve},context=matrix.raw_context(fifth_word=224));pairs.append((observed,value))
    assert proof.require_guard_invariance(pairs)=={'source-last-physical-guard':True,'consumer-last-physical-guard':True}
    with pytest.raises(ValueError):proof.require_guard_invariance(pairs[:1])


def test_raw_packet_refuses_duplicate_keys_and_incomplete_self_admission():
    with pytest.raises(ValueError):proof.objects([('schema',1),('schema',1)])
    with pytest.raises(ValueError):proof.require_witness(None,dict(schema=1,semantic_admission=True),{})
