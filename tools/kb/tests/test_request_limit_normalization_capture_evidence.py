"""Independent limit/mode boundaries and complete physical-state refusal controls."""
from copy import deepcopy
import json
import pytest
from kb import repo, byte_surface_equations as state
from kb import request_limit_normalization_contract as contract, request_limit_normalization_matrix as matrix
from kb import request_limit_normalization_semantics as numeric, request_limit_normalization_transfers as transfers
from kb import request_limit_normalization_capture_evidence as proof

def case(**changes):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-refusal');value.update(changes);return value
def equations(value):return numeric.caller(matrix.memory(value),matrix.input_calibrations(value))

def test_directed_rounding_and_unconditional_last_neighbor_are_distinct_obligations():
    assert numeric.directed_word(0,65535,32768)==32767
    assert numeric.directed_word(65535,0,32768)==32768
    raw=b''.join(i.to_bytes(2,'big') for i in range(16))
    axis=b''.join(i.to_bytes(2,'big') for i in matrix.DEFAULTS['axis'])
    first=numeric.curve(raw,axis,65535,0);second=numeric.curve(raw,axis,65535,65535)
    assert first['value']==second['value']==15 and first['cells']==[15,16]
    assert first['second']==0 and second['second']==65535 and first['fraction']==0

@pytest.mark.parametrize(('lower','upper'),((0,0),(8000,0),(32000,32000)))
def test_actual_nonpositive_span_selects_three_explicit800_words(lower,upper):
    result=equations(case(lower=[lower]*16,upper=[upper]*16))
    assert result['span']==0 and result['normalized']==[800]*3

def test_independent_upper_and_lower_words_change_actual_set_mode_publication():
    upper=[equations(case(upper=[raw]*16,word_338c=(-24768)&65535,word_338e=(-24768)&65535,word_3396=(-24768)&65535))['output'] for raw in (16000,32000)]
    lower=[equations(case(lower=[raw]*16))['output'] for raw in (0,8000)]
    assert upper==[400,200] and lower==[400,266]

def test_stock_clear_mode_uses_alternate_maximum_while_status_uses_clamp():
    selected=equations(case(mode_83c1=0x2E));stock=equations(case(mode_83c1=0x2C))
    assert selected['normalized']==stock['normalized']==[400]*3
    assert (selected['output'],stock['output'])==(400,2000)
    assert selected['second_status']==stock['second_status']==0x85
    assert (selected['request_status'],stock['request_status'])==(0xD7,0xD6)

@pytest.mark.parametrize(('raw','zero','high'),((0,True,False),(799,False,False),(800,False,True),(65535,False,True)))
def test_actual_override_preserves_zero_and800_status_boundaries(raw,zero,high):
    value=equations(case(byte_41f3=1,word_3026=raw))
    assert value['output']==raw and bool(value['second_status']&16)==zero and bool(value['second_status']&32)==high

def reconstructed(**changes):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(word_113c=2750);value.update(changes)
    fixture,_=contract.fixture_for_case(source,image,value)
    context=matrix.context(source,value);sp=0x30000000;continuation=0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    before=matrix.memory(value);cal=matrix.calibrations(source,image,value)
    result=state.execute(source,fixture,context,before,bytes(frame),sp,continuation,contract.ENTRY,0,trace=True)
    observed=dict(context=context,sp=sp,continuation=continuation,memory_before=(before,),calibration_before=cal,
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])),
        frame_before=bytes(frame),frame_after=result['frame'],memory_after=(result['ram'],),sr_before=0)
    return observed,result,numeric.caller(before,cal),fixture

@pytest.mark.parametrize('changes',({},dict(mode_83c1=0x2C),dict(byte_41f3=1,word_3026=0),dict(upper=[0]*16),dict(axis=[0,*([65535]*15)],word_113c=32768)))
def test_complete_actual_modes_zero_span_and_unsigned_axis_numerator(changes):
    observed,result,value,fixture=reconstructed(**changes)
    transfers.require(observed,result,value,fixture)

@pytest.mark.parametrize('fault',('exit-SR','frame','other-RAM','curve-argument','neighbor-width','neighbor-byte','mode-byte','tail','live-limit','live-flag','returned-PR','scalar-only'))
def test_matching_final_word_does_not_replace_complete_state_calls_operands_or_stores(fault):
    observed,result,value,fixture=reconstructed();transfers.require(observed,result,value,fixture)
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^1,*observed['exit'][1:])
    elif fault=='frame':observed['frame_after']=b'\x01'+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='curve-argument':
        call=next(r for r in result['calls'] if r['site']==0x7AF98);raw=list(call['entry']['registers']);raw[4]^=2;call['entry']['registers']=tuple(raw)
    elif fault in ('neighbor-width','neighbor-byte'):
        event=next(r for r in result['accesses'] if r['site']==0x2650A)
        event['width_bytes' if fault=='neighbor-width' else 'bytes']=1 if fault=='neighbor-width' else 'ffff'
    elif fault=='mode-byte':next(r for r in result['accesses'] if r['site']==0x7AF0E)['bytes']='2c'
    elif fault=='tail':next(r for r in result['trace'] if r['site']==0x26518)['delay_slot']=False
    elif fault=='live-limit':value['normalized'][0]^=1
    elif fault=='live-flag':value['request_status']^=1
    elif fault=='returned-PR':result['pr']^=2
    else:value['value']^=1;value['output']^=1
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

def causal(source):
    before=matrix.memory(source);cal=matrix.input_calibrations(source);value=numeric.caller(before,cal)
    return dict(entry=contract.ENTRY,context=matrix.context({},source),memory_before=(before,),memory_after=(value['memory'],),calibration_before=cal,
        bound_before=bytes(sum(r['size'] for r in contract.BOUND_SPANS)),frame_before=bytes(192),sp=0x30000000,continuation=0x30010000,abi_before=tuple(range(12)),sr_before=0)

@pytest.mark.parametrize('fault',('other-curve','axis','ROM-mode','RAM','frame','context','SP'))
def test_held_other_curve_group_preserves_every_other_complete_input(fault):
    first=causal(case());source=case();source['upper'][0]^=1;second=causal(source)
    assert proof.held_key(first,0x154C0,32,'rom')[0]==proof.held_key(second,0x154C0,32,'rom')[0]
    if fault in ('other-curve','axis','ROM-mode'):
        at={'other-curve':0x154E0,'axis':0x14BAA,'ROM-mode':0x83C1}[fault];raw=bytearray(second['calibration_before'][at]);raw[0]^=1;second['calibration_before'][at]=bytes(raw)
    elif fault=='RAM':
        raw=bytearray(second['memory_before'][0]);raw[0x88]^=1;second['memory_before']=(bytes(raw),)
    elif fault=='frame':second['frame_before']=b'\x01'+second['frame_before'][1:]
    elif fault=='context':second['context']=(second['context'][0]^1,*second['context'][1:])
    else:second['sp']+=4
    assert proof.held_key(first,0x154C0,32,'rom')[0]!=proof.held_key(second,0x154C0,32,'rom')[0]
