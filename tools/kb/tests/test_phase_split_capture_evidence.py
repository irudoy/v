"""Actual natural splitter observations require both stores and complete state."""

from copy import deepcopy

import pytest

from kb import phase_split_semantics as split,phase_normalization_capture_evidence as proof
from test_phase_normalization_capture_evidence import original,actual_windows,refuse


@pytest.mark.parametrize('pair',(0,1))
@pytest.mark.parametrize('argument',(0,10,0x10000,0xFFFFFFFF))
@pytest.mark.parametrize('fault',('word-output','byte-output','outside','r4','r5','r6','frame','abi',
    'pr','sp','continuation','macl','calibration'))
def test_actual_splitter_inputs_outputs_pointer_registers_and_state_are_required(actual_windows,pair,argument,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==0x28E7C and row['pair']==pair and row['argument']==argument)
    observed=deepcopy(observations[case['index']])
    if fault in ('word-output','byte-output','outside'):
        at=case['word']&65535 if fault=='word-output' else case['byte']&65535
        if fault=='outside':at=0x1234
        memory=bytearray(observed['memory_after'][0]);memory[at]^=1;observed['memory_after']=(bytes(memory),)
    elif fault in ('r4','r5','r6'):
        context=list(observed['context']);context[int(fault[1:])]^=1;observed['context']=tuple(context)
    elif fault=='frame':
        frame=bytearray(observed['frame_after']);frame[156]^=1;observed['frame_after']=bytes(frame)
    elif fault in ('abi','pr','macl'):
        key='abi_after' if fault=='abi' else 'exit';values=list(observed[key]);values[1 if fault=='pr' else 2]^=1
        observed[key]=tuple(values)
    elif fault=='sp':observed['sp']+=4
    elif fault=='continuation':observed['continuation']+=2
    else:observed['calibration_before'][0x28EA0]=bytes.fromhex('1999')
    with pytest.raises(ValueError):proof.require_state(declared,image,fixture,case,observed)


@pytest.mark.parametrize('argument',(0,10,0x80000000))
@pytest.mark.parametrize('fault',('omit-word','omit-byte','extra-read','literal','width','direction','address','value','call','scratch'))
def test_actual_BT_S_delay_store_and_byte_publication_are_unconditional(actual_windows,argument,fault):
    declared,image,fixture,observations=actual_windows
    case=next(row for row in declared['cases'] if row['entry']==0x28E7C and row['pair']==1 and row['argument']==argument)
    observed=observations[case['index']];result,_=proof.require_state(declared,image,fixture,case,observed);result=deepcopy(result)
    if fault in ('omit-word','omit-byte'):
        site=0x28E94 if fault=='omit-word' else 0x28E98
        result['accesses']=[row for row in result['accesses'] if row['site']!=site]
    elif fault=='extra-read':
        row=deepcopy(next(row for row in result['accesses'] if row['site']==0x28E94));row['mode']='read';result['accesses'].append(row)
    elif fault=='call':result['calls'].append(dict(site=0x28E9A,target=0x28DC8))
    elif fault=='scratch':
        registers=list(result['registers']);registers[6]^=1;result['registers']=registers
    else:
        row=next(row for row in result['accesses'] if row['site']==(0x28E7E if fault=='literal' else 0x28E94))
        if fault=='literal':row['bytes']='1999'
        elif fault=='width':row['width_bytes']=1
        elif fault=='direction':row['mode']='read'
        elif fault=='address':row['address']+=2
        else:row['bytes']='0000' if row['bytes']!='0000' else '0001'
    with pytest.raises(ValueError):split.evaluate(case,observed,result)


@pytest.mark.parametrize('source',('tools/kb/src/kb/phase_split_semantics.py',))
def test_original_splitter_scalar_source_is_current(original,source):
    inputs=dict(original[1]['candidate']['producer_inputs']);inputs[source]='0'*64
    with pytest.raises(ValueError):proof.require_witness(original[0],original[2],inputs)


def test_missing_natural_splitter_code_or_literal_refuses(original):
    for field in ('code','pools'):
        packet=deepcopy(original[2]);packet['reconstruction'][field].pop();refuse(original,packet)
