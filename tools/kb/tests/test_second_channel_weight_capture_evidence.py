"""Actual published/live second-channel R5 quantity, complete-state and causal refusal sources."""
from copy import deepcopy
import pytest
from kb import repo,byte_surface_equations as state
from kb import second_channel_weight_contract as contract,second_channel_weight_matrix as matrix
from kb import second_channel_weight_semantics as numeric,second_channel_weight_transfers as transfers
from kb import second_channel_weight_capture_evidence as proof

def case(**updates):
    value=dict(deepcopy(matrix.DEFAULTS),index=0,kind='independent-weight-refusal');value.update(updates);return value

def reconstructed(**updates):
    image=repo.images(repo.ROOT)['JK08A'].path.read_bytes();source=contract.descriptor(repo.ROOT)
    value=case(**updates);fixture,_=contract.fixture_for_case(source,image,value);cal=matrix.calibrations(source,image,value)
    memory=matrix.memory(value);context=matrix.context(source,value);sp=0x30000000;continuation=0x30010000
    frame=bytearray(b''.join((0xA3B4C5D6+i*17).to_bytes(4,'big') for i in range(48)))
    frame[160:164]=context[19].to_bytes(4,'big');frame[164:168]=context[7].to_bytes(4,'big');frame[184:188]=continuation.to_bytes(4,'big')
    result=state.execute(source,fixture,context,memory,bytes(frame),sp,continuation,contract.ENTRY,context[18],trace=True)
    independent=numeric.evaluate(memory,cal,bytes(frame))
    bound=b''.join(fixture[r['address']:r['address']+r['size']] for r in contract.BOUND_SPANS)
    observed=dict(index=0,entry=contract.ENTRY,context=context,sp=sp,continuation=continuation,
        bound_before=bound,bound_after=bound,
        memory_before=(memory,),memory_after=(result['ram'],),frame_before=bytes(frame),frame_after=result['frame'],
        calibration_before=cal,calibration_after=cal,sr_before=context[18],abi_before=tuple(range(12)),
        exit=(result['sr'],result['pr'],result['macl'],result['mach'],result['gbr'],*reversed(result['registers'])))
    transfers.require(observed,result,independent,fixture)
    return observed,result,independent,fixture

@pytest.mark.parametrize('raw',(0,1,1024,32767,32768,32769,65535))
def test_actual_weight_is_published_and_continues_through_live_R5(raw):
    observed,result,value,fixture=reconstructed(weight_surface=[raw]*64)
    memory=observed['memory_after'][0]
    assert int.from_bytes(memory[0x35F4:0x35F6],'big')==value['weight']==raw
    assert int.from_bytes(memory[0x35CA:0x35CC],'big')==value['blended']==raw
    assert int.from_bytes(memory[0x35CC:0x35CE],'big')==value['output']==min(800,raw)
    assert int.from_bytes(memory[0x1248:0x124A],'big')==value['value']==min(800,raw)*727//800
    assert not any(r['mode']=='read' and r['address']==matrix.RAM_BASE+0x35F4 for r in result['accesses'])

@pytest.mark.parametrize('updates',(
    dict(byte_2c71=255,word_10bc=65535),dict(byte_2c71=1,word_10bc=0),
    dict(byte_2c71=0,word_10bc=1),dict(byte_2c71=1,word_10bc=1),
    dict(weight_axes=[0,65535,0,32768,32767,1,65534,65535]*2,word_10bc=32768),
    dict(weight_axes=[65535]*16,byte_2c71=0),dict(byte_249f=2),
    dict(rom_83c1=128,rom_1630c=65535),
    dict(rom_83c1=128,rom_1630c=32768,byte_245e=64,ordinary_curves=[65535]*48+[0]),
    dict(word_31e2=0),dict(word_2698=800),dict(word_3024=0),
    dict(byte_4214=64,word_35ea=65535)))
def test_full_surface_modes_overflow_division_and_output_boundaries(updates):
    reconstructed(**updates)

@pytest.mark.parametrize('fault',('exit-SR','exit-register','frame','other-RAM','source-width',
    'pre-extension-R5','extended-R5','product-R5','output-register','wide-R14',
    'return-delay','saved-MACL','carrier-high16','incoming-carrier-high16',
    'local-word-width','helper-argument','fake-prior-read','opcode'))
def test_matching_words_cannot_replace_full_CPU_frame_local_carrier_and_live_registers(fault):
    observed,result,value,fixture=reconstructed()
    if fault=='exit-SR':observed['exit']=(observed['exit'][0]^0x100,*observed['exit'][1:])
    elif fault=='exit-register':observed['exit']=(*observed['exit'][:-1],observed['exit'][-1]^1)
    elif fault=='frame':observed['frame_after']=bytes([observed['frame_after'][0]^1])+observed['frame_after'][1:]
    elif fault=='other-RAM':
        raw=bytearray(observed['memory_after'][0]);raw[0x88]^=1;observed['memory_after']=(bytes(raw),)
    elif fault=='source-width':next(r for r in result['accesses'] if r['site']==0x7A88C)['width_bytes']=1
    elif fault in ('pre-extension-R5','extended-R5','product-R5','output-register','wide-R14'):
        site,register={'pre-extension-R5':(0x7A88C,5),'extended-R5':(0x7A890,5),
            'product-R5':(0x7A898,5),'output-register':(0x7A972,5),'wide-R14':(0x7A90A,14)}[fault]
        row=next(r for r in result['trace'] if r['site']==site)
        registers=list(row['before']['registers']);registers[register]^=0x10000
        row['before']['registers']=tuple(registers)
    elif fault=='return-delay':result['trace'][-1]['delay_slot']=False
    elif fault=='saved-MACL':next(r for r in result['accesses'] if r['site']==0x7A814)['address']+=4
    elif fault=='carrier-high16':
        row=next(r for r in result['trace'] if r['site']==0x26606)
        registers=list(row['after']['registers']);registers[5]^=0x10000;row['after']['registers']=tuple(registers)
    elif fault=='incoming-carrier-high16':
        frame=bytearray(observed['frame_before']);frame[120]^=1;observed['frame_before']=bytes(frame)
    elif fault=='local-word-width':next(r for r in result['accesses'] if r['site']==0x7A878)['width_bytes']=4
    elif fault=='helper-argument':
        call=result['calls'][-1];registers=list(call['entry']['registers'])
        registers[0]=801;call['entry']['registers']=tuple(registers)
    elif fault=='fake-prior-read':
        next(r for r in result['accesses'] if r['site']==0x7A8F8)['address']=matrix.RAM_BASE+0x35F4
    else:result['trace'][0]['bytes']='0009'
    with pytest.raises(ValueError):transfers.require(observed,result,value,fixture)

def causal_pairs():
    pairs=[]
    for index in range(64):
        for raw in (0,1024):
            surface=[0]*64;surface[index]=raw
            observed,result,value,fixture=reconstructed(weight_surface=surface,
                word_10bc=(index//8)*8192,byte_2c71=(index%8)*32)
            pairs.append((observed,value))
    for raw in (0,1024):
        observed,result,value,fixture=reconstructed(rom_83c1=128,rom_1630c=raw)
        pairs.append((observed,value))
    return pairs

def test_all_surface_cells_and_substitute_need_changed_actual_publications():
    wanted={f'weight-surface-word-{i}':True for i in range(64)}|{'raw-substitute-weight':True}
    assert proof.require_causal_alternatives(causal_pairs())==wanted
    pairs=causal_pairs()
    for observed,value in pairs:
        raw=bytearray(observed['memory_after'][0]);raw[0x1248:0x124A]=bytes(2)
        observed['memory_after']=(bytes(raw),);value['value']=0
    with pytest.raises(ValueError):proof.require_causal_alternatives(pairs)

def test_overwritten_prior35F4_is_invariant_on_both_weight_paths():
    pairs=[]
    for prior in (0,1,32767,32768,65535):
        for substitute in (0,128):
            observed,result,value,fixture=reconstructed(prior_35f4=prior,rom_83c1=substitute)
            pairs.append((observed,value))
    assert proof.require_prior_invariance(pairs)==dict(surface=True,substitute=True)
    raw=bytearray(pairs[-1][0]['memory_after'][0]);raw[0x88]^=1
    pairs[-1][0]['memory_after']=(bytes(raw),)
    with pytest.raises(ValueError):proof.require_prior_invariance(pairs)

def test_both_last_physical_curve_guards_have_zero_result_weight():
    pairs=[]
    for alternate in (False,True):
        for raw in (0,1,32767,32768,65535):
            name='alternate_curves' if alternate else 'ordinary_curves'
            curve=list(matrix.DEFAULTS[name]);curve[-1]=raw
            observed,result,value,fixture=reconstructed(word_2698=61440,
                byte_249f=2 if alternate else 0,**{name:curve})
            pairs.append((observed,value))
    assert proof.require_guard_invariance(pairs)=={
        'last-common-curve-guard':True,'last-alternate-curve-guard':True}
    next(r for r in pairs[-1][1]['operands'] if r['address']==0x190D0)['width_bytes']=1
    with pytest.raises(ValueError):proof.require_guard_invariance(pairs)
