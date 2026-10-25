"""Original uptight-duck observations fence the constant divisor and complete state."""

from copy import deepcopy
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import uptight_duck_capture_evidence as proof


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        packet=record['candidate']['witness']['uptight_duck_paths']
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original uptight-duck capture')
        pytest.skip('the complete original uptight-duck capture is unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    assert result['lookup_is_not_the_signed_operand'] is True
    return model,record,packet


def refuse(original,packet):
    with pytest.raises(ValueError):proof.require_witness(original[0],packet,original[1]['candidate']['producer_inputs'])


@pytest.mark.parametrize('field',('declaration','consumed','reconstruction','aliases','boundaries','observations','simulator'))
def test_missing_uptight_duck_physical_input_refuses(original,field):
    packet=dict(original[2]);packet.pop(field);refuse(original,packet)



@pytest.fixture(scope='module')
def coordinate_pairs(original):
    declared=original[2]['declaration'];observed=proof.observations(original[2],declared)
    image=repo.images()['JK08A'].path.read_bytes();fixture,_=proof.contract.independent_fixture(declared['source'],image)
    pairs=[]
    for case,row in zip(declared['cases'],observed):
        if 'fifth_word' not in case:continue
        result,value=proof.require_state(declared,image,fixture,case,row);pairs.append((row,result))
    return pairs


def test_actual_fixed_other_R5_values_reach_three_R6_arguments_and_both_word_outputs(coordinate_pairs,original):
    assert proof.require_coordinate_response(coordinate_pairs) is True
    result=proof.require_primary(original[0],original[1])
    assert result['exact_R5_coordinate_response'] is True
    assert result['real_three_curve_R6_and_publications'] is True
    assert result['datum_identity_inference'] is False and result['native_relation_publication'] is False


@pytest.mark.parametrize('fault',('omit-knot','omit-word-edge','omit-endpoint-edge','constant-output','byte-output',
    'output-site','output-register','output-address','output-domain','output-bytes','duplicate-output',
    'call-argument','call-target','call-site','call-order','fifth-input','SR-input','other-register',
    'frame-input','RAM-input','calibration-input'))
def test_coordinate_response_refuses_echoes_partial_inputs_and_substituted_actual_transfers(coordinate_pairs,fault):
    pairs=deepcopy(coordinate_pairs)
    target=next(i for i,pair in enumerate(pairs) if pair[0]['context'][5]==50)
    observed,result=pairs[target]
    if fault=='omit-knot':pairs.pop(target)
    elif fault=='omit-word-edge':pairs=[pair for pair in pairs if pair[0]['context'][5]!=65535]
    elif fault=='omit-endpoint-edge':pairs=[pair for pair in pairs if pair[0]['context'][5]!=3101]
    elif fault=='constant-output':
        for row,actual in pairs:
            memory=bytearray(row['memory_after'][0]);memory[0x35B6:0x35B8]=bytes(2);row['memory_after']=(bytes(memory),)
            next(event for event in actual['accesses'] if event['site']==0xB78BA)['bytes']='0000'
    elif fault in ('byte-output','output-site','output-register','output-address','output-domain','output-bytes','duplicate-output'):
        event=next(event for event in result['accesses'] if event['site']==0xB78BA)
        if fault=='byte-output':event['width_bytes']=1
        elif fault=='output-site':event['site']+=2
        elif fault=='output-register':event['register']=5
        elif fault=='output-address':event['address']+=1
        elif fault=='output-domain':event['domain']='rom'
        elif fault=='output-bytes':event['bytes']='ffff'
        else:result['accesses'].append(dict(event))
    elif fault in ('call-argument','call-target','call-site','call-order'):
        call=next(call for call in result['calls'] if call['target']==0x26524)
        if fault=='call-target':call['target']+=2
        elif fault=='call-site':call['site']+=2
        elif fault=='call-order':result['calls'].reverse()
        else:
            registers=list(call['entry']['registers']);registers[6]^=1;call['entry']['registers']=tuple(registers)
    elif fault in ('fifth-input','SR-input','other-register'):
        context=list(observed['context']);context[{'fifth-input':19,'SR-input':18,'other-register':4}[fault]]^=1;observed['context']=tuple(context)
    elif fault=='frame-input':observed['frame_before']=bytes([observed['frame_before'][0]^1])+observed['frame_before'][1:]
    elif fault=='RAM-input':
        memory=bytearray(observed['memory_before'][0]);memory[0x11BC]^=1;observed['memory_before']=(bytes(memory),)
    else:observed['calibration_before']={}
    with pytest.raises(ValueError):proof.require_coordinate_response(pairs)
