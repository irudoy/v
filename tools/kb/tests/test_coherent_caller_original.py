"""Actual original caller-copy state supplies leaf refusal inputs without GNU reruns."""

from copy import deepcopy
import json

import pytest

from kb import compile, copy_evidence as common, coherent_copy_evidence as proof
from kb import coherent_copy_matrix as matrix, lock, repo, test_evidence
from kb.model import SymbolKey


CALLS=(0x20bd0,0x20cba,0x20cdc,0x20ce6)


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(common._read(repo.ROOT,common.RECEIPT))
        packet=record['candidate']['witness']['coherent']
        if len(packet['windows'])!=len(matrix.WINDOWS):
            raise KeyError('the original omits the added caller windows')
    except (OSError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original coherent caller capture')
        pytest.skip('the complete original coherent caller capture is unavailable')
    with lock.held(repo.ROOT):
        model=compile.build(repo.ROOT)
    symbol=model.symbols[SymbolKey('7mfk','ram',common.MEMBERS['reader'][1])]
    assert common.failure(common.item('reader'),symbol,model,'identity',record=record) is None
    return model,record,packet


@pytest.fixture(params=CALLS)
def observed(original,request):
    index,= [index for index,window in enumerate(matrix.WINDOWS) if window.call==request.param]
    window=matrix.WINDOWS[index]
    declared=proof.descriptor(repo.ROOT)['window'][index]
    pools=b''.join(matrix.alias(row['value']).to_bytes(4,'big') for row in declared['pool'])
    packet=original[2]['windows'][index]
    return window,packet['cases'][0],packet['observations'][0],pools


@pytest.mark.parametrize('fault',('incoming','special','exit','source','destination','frame','abi','outside','pool'))
def test_actual_extended_window_refuses_wrong_state_or_datum(observed,fault):
    window,case,original,pools=observed
    changed=deepcopy(original)
    if fault=='incoming':
        changed['incoming'][1]^=1
    elif fault=='special':
        changed['entry_t_after']^=1
    elif fault=='exit':
        changed['exit'][19]^=1
    elif fault in ('source','destination','frame','pool'):
        key={'source':'read_before','destination':'destination_after','frame':'frame_after','pool':'pools_after'}[fault]
        value=bytearray.fromhex(changed[key])
        if value:
            value[0]^=1
        else:
            value.append(1)
        changed[key]=value.hex()
    elif fault=='abi':
        changed['abi_after'][0]^=1
    else:
        changed['outside_changes'].append([0x4321,0,1])
    with pytest.raises(ValueError):
        matrix.validate_observation(window,case,changed,pools)


@pytest.mark.parametrize('field',('code','pools','cases','observations','aliases','boundary','fixture_sha256'))
def test_actual_extended_window_requires_every_physical_binding(original,field):
    packet=deepcopy(original[2])
    packet['windows'][0].pop(field)
    with pytest.raises((ValueError,KeyError)):
        proof.validate_witness(packet,original[1]['candidate']['producer_inputs'],repo.ROOT)


@pytest.mark.parametrize('source',('tools/sh-elf-run/stock_jk08a_coherent_00020bd0.s',
                                  'tools/sh-elf-run/stock_jk08a_coherent_00020ce6.s'))
def test_actual_complete_capture_refuses_another_consumed_caller_source(original,source):
    packet=deepcopy(original[2])
    packet['consumed'][source]+='00'
    with pytest.raises(ValueError,match='source snapshot'):
        proof.validate_witness(packet,original[1]['candidate']['producer_inputs'],repo.ROOT)
