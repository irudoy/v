"""Wide result arithmetic, poisoned input independence and complete physical-state refusals."""
from copy import deepcopy
import json
import pytest
from kb import repo, byte_surface_equations as state
from kb import evap_result_word_contract as contract, evap_result_word_matrix as matrix
from kb import evap_result_word_semantics as numeric, evap_result_word_transfers as transfers
from kb import evap_result_word_capture_evidence as proof


def case(**updates):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal-control')
    value.update(updates)
    return value


def equation(value):
    return numeric.caller(matrix.memory(value), matrix.input_calibrations(value), matrix.context({}, value))


def test_single_coefficient_byte_changes_computed_word_with_exact_pointer_and_other_inputs_fixed():
    outputs = []
    for raw in (0, 128):
        curve = [128] * 16
        curve[0] = raw
        value = equation(case(coefficient_a_default=curve))
        assert value['normalized'] == 65535 and value['pointer'] == 0x0100301C
        outputs.append(numeric.word(value['memory'], 0x301C))
    assert outputs == [0, 65535]
    for poison in (0, 1, 32767, 32768, 65535):
        assert equation(case(prior_301c=poison))['result'] == 65535


def test_zero_difference_zero_parameter_and_positive_quotient_have_independent_dispositions():
    context = matrix.initial_context()
    context[4], context[5] = 0, 1024
    assert equation(case(context=context))['normalized'] == 0
    context[5] = 0
    assert equation(case(context=context))['normalized'] == 65535
    context[4] = 1
    value = equation(case(context=context, rom_94cc=32, rom_8813=1, transform_curve=[1] * 17))
    assert value['branch'] == 'normalized-positive' and value['normalized'] == 1
    assert value['result'] == 1


def test_low16_arguments_keep_arbitrary_upper_bits_and_signed_byte_endpoint_returns():
    first = matrix.initial_context()
    first[4], first[5] = 1, 0
    second = list(first)
    second[4], second[5] = 0xFFFF0001, 0xA5A50000
    assert equation(case(context=first))['memory'] == equation(case(context=second))['memory']
    value = equation(case(byte_10fa=255, coefficient_a_default=[255] * 16))
    assert value['coefficient_a']['returned'] == 0xFFFFFFFF and value['coefficient_a']['value'] == 255


def reconstructed():
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source, value = contract.descriptor(repo.ROOT), case()
    fixture, _ = contract.fixture_for_case(source, image, value)
    context, memory = matrix.context(source, value), matrix.memory(value)
    calibration = matrix.calibrations(source, image, value)
    sp, continuation = 0x30000000, 0x30010000
    frame = bytearray(b''.join((0xA3B4C5D6 + i * 17).to_bytes(4, 'big') for i in range(48)))
    frame[160:164], frame[164:168] = context[19].to_bytes(4, 'big'), context[7].to_bytes(4, 'big')
    frame[184:188] = continuation.to_bytes(4, 'big')
    result = state.execute(source, fixture, context, memory, bytes(frame), sp, continuation, contract.ENTRY, 0, trace=True)
    observed = dict(entry=contract.ENTRY, context=context, sp=sp, continuation=continuation,
        exit=(result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
        frame_after=result['frame'], memory_before=(memory,), memory_after=(result['ram'],), calibration_before=calibration, sr_before=0)
    return observed, result, numeric.caller(memory, calibration, context), fixture


@pytest.mark.parametrize('fault', ('exit-SR', 'frame', 'unrelated-RAM', 'call-argument', 'pointer', 'physical-width', 'delay-slot'))
def test_matching_result_bytes_do_not_replace_complete_CPU_frame_operands_and_return(fault):
    observed, result, value, fixture = reconstructed()
    transfers.require(observed, result, value, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame':
        raw = bytearray(observed['frame_after']); raw[0] ^= 1; observed['frame_after'] = bytes(raw)
    elif fault == 'unrelated-RAM':
        raw = bytearray(observed['memory_after'][0]); raw[0] ^= 1; observed['memory_after'] = (bytes(raw),)
    elif fault == 'call-argument':
        raw = list(result['calls'][0]['entry']['registers']); raw[4] ^= 2; result['calls'][0]['entry']['registers'] = tuple(raw)
    elif fault == 'pointer':
        next(row for row in result['trace'] if row['site'] == 0xB22A6)['before']['registers'] = (0,) * 16
    elif fault == 'physical-width':
        next(row for row in result['accesses'] if row['site'] == 0xB22A6)['width_bytes'] = 1
    else:
        result['trace'][-1]['delay_slot'] = False
    with pytest.raises(ValueError):
        transfers.require(observed, result, value, fixture)


@pytest.mark.parametrize('fault', ('missing', 'index', 'entry', 'context', 'duplicate-key'))
def test_raw_original_refuses_missing_or_detached_single_entry_observations(fault):
    declared = dict(cases=[case()], calibration_spans=[[r['address'], r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'], r['size']] for r in contract.BOUND_SPANS])
    context = b''.join(v.to_bytes(4, 'big') for v in matrix.context({}, case())).hex()
    row = dict(schema=1, index=0, entry=contract.ENTRY, context=context, context_after=context,
        observation=bytes(572).hex(), ram_before='65536:a5', ram_after='65536:a5',
        calibration_before=bytes(sum(n for at, n in declared['calibration_spans'])).hex(),
        calibration_after=bytes(sum(n for at, n in declared['calibration_spans'])).hex(),
        bound_before=bytes(sum(n for at, n in declared['bound_spans'])).hex(),
        bound_after=bytes(sum(n for at, n in declared['bound_spans'])).hex())
    marker = proof.MARKER + ' status=PASS region=' + proof.REGION + ' cases=1'
    def packet(rows):
        return dict(observations=deepcopy(rows), marker=marker,
            stdout='\n'.join([*(proof.PREFIX + json.dumps(r) for r in rows), marker]))
    assert len(proof.observations(packet([row]), declared)) == 1
    if fault == 'index':
        row['index'] = 1
    elif fault == 'entry':
        row['entry'] += 2
    elif fault == 'context':
        row['context_after'] = bytes(80).hex()
    value = packet([] if fault == 'missing' else [row])
    if fault == 'duplicate-key':
        value['stdout'] = value['stdout'].replace('"schema": 1', '"schema": 1, "schema": 1', 1)
    with pytest.raises(ValueError):
        proof.observations(value, declared)
