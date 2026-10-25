"""Actual three-word normalization, selected-byte preservation and complete-state refusals."""
from copy import deepcopy
import pytest
from kb import repo, byte_surface_equations as state
from kb import endpoint_normalizer_writer_withdrawal_contract as contract
from kb import endpoint_normalizer_writer_withdrawal_matrix as matrix
from kb import endpoint_normalizer_writer_withdrawal_semantics as numeric
from kb import endpoint_normalizer_writer_withdrawal_transfers as transfers
from kb import endpoint_normalizer_writer_withdrawal_capture_evidence as proof


def case(**changes):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal')
    value.update(changes)
    return value


def equations(value):
    return numeric.caller(matrix.memory(value), matrix.input_calibrations(value))


def test_all_selected_byte_preimages_remain_unchanged_while_three_actual_outputs_are_computed():
    for raw in range(256):
        value = case(byte_41fb=raw)
        result = equations(value)
        assert result['memory'][0x41FB] == raw
        assert result['normalized'] == [400] * 3
        before = matrix.memory(value)
        changed = {i for i, (a, b) in enumerate(zip(before, result['memory'])) if a != b}
        assert changed <= {*range(0x3478, 0x347E)}


def test_each_active_endpoint_word_changes_real_publication_with_other_complete_inputs_fixed():
    for index in range(16):
        for name, values, expected in (('upper', (16000, 32000), (800, 400)), ('lower', (0, 8000), (400, 266))):
            outputs = []
            for raw in values:
                curve = list(matrix.DEFAULTS[name])
                curve[index] = raw
                result = equations(case(**{name: curve}, word_113c=matrix.DEFAULTS['axis'][index]))
                outputs.append(result['normalized'][0])
            assert tuple(outputs) == expected


@pytest.mark.parametrize(('lower', 'upper'), ((0, 0), (8000, 0), (32000, 32000)))
def test_nonpositive_span_uses_actual_explicit_three_word_fallback(lower, upper):
    result = equations(case(lower=[lower] * 16, upper=[upper] * 16))
    assert result['span'] == 0 and result['normalized'] == [800] * 3


def test_signed_input_base_floor_and_endpoint_guard_physical_role_remain_distinct():
    result = equations(case(word_338c=32768, word_338e=48768, word_3396=32767))
    assert result['normalized'] == [0, 400, 800]
    first = equations(case(word_113c=65535, lower_guard=0))
    second = equations(case(word_113c=65535, lower_guard=65535))
    assert first['lower']['value'] == second['lower']['value'] == 0
    assert first['lower']['cells'] == second['lower']['cells'] == [15, 16]
    assert first['lower']['second'] == 0 and second['lower']['second'] == 65535
    assert first['upper']['second'] == matrix.DEFAULTS['lower'][0]


def reconstructed(**changes):
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source = contract.descriptor(repo.ROOT)
    value = case(word_113c=2750)
    value.update(changes)
    fixture, _ = contract.fixture_for_case(source, image, value)
    context = matrix.context(source, value)
    sp, continuation = 0x30000000, 0x30010000
    frame = bytearray(b''.join((0xA3B4C5D6 + i * 17).to_bytes(4, 'big') for i in range(48)))
    frame[160:164] = context[19].to_bytes(4, 'big')
    frame[164:168] = context[7].to_bytes(4, 'big')
    frame[184:188] = continuation.to_bytes(4, 'big')
    before = matrix.memory(value)
    calibration = matrix.calibrations(source, image, value)
    result = state.execute(source, fixture, context, before, bytes(frame), sp, continuation, contract.ENTRY, 0, trace=True)
    observed = dict(entry=contract.ENTRY, context=context, sp=sp, continuation=continuation, memory_before=(before,),
        calibration_before=calibration, exit=(result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
        frame_before=bytes(frame), frame_after=result['frame'], memory_after=(result['ram'],), sr_before=0)
    return observed, result, numeric.caller(before, calibration), fixture


@pytest.mark.parametrize('changes', ({}, dict(upper=[0] * 16), dict(lower=[65535] * 16),
    dict(axis=[0, *([65535] * 15)], word_113c=32768)))
def test_complete_natural_root_zero_span_and_unsigned_axis_numerator(changes):
    observed, result, value, fixture = reconstructed(**changes)
    transfers.require(observed, result, value, fixture)


@pytest.mark.parametrize('fault', ('exit-SR', 'frame', 'other-RAM', 'selected-byte', 'curve-argument',
    'neighbor-width', 'local-slot', 'tail', 'computed-output', 'returned-PR', 'native-datum-read', 'alias-overlap'))
def test_matching_normalized_words_cannot_replace_complete_root_or_whole_datum_absence(fault):
    observed, result, value, fixture = reconstructed()
    transfers.require(observed, result, value, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame':
        observed['frame_after'] = b'\x01' + observed['frame_after'][1:]
    elif fault in ('other-RAM', 'selected-byte'):
        raw = bytearray(observed['memory_after'][0])
        raw[0x41FB if fault == 'selected-byte' else 0x88] ^= 1
        observed['memory_after'] = (bytes(raw),)
    elif fault == 'curve-argument':
        call = next(r for r in result['calls'] if r['site'] == 0x7AF98)
        raw = list(call['entry']['registers'])
        raw[4] ^= 2
        call['entry']['registers'] = tuple(raw)
    elif fault == 'neighbor-width':
        next(r for r in result['accesses'] if r['site'] == 0x2650A)['width_bytes'] = 1
    elif fault == 'local-slot':
        next(r for r in result['accesses'] if r['site'] == 0x7AF9C)['address'] += 2
    elif fault == 'tail':
        next(r for r in result['trace'] if r['site'] == 0x26518)['delay_slot'] = False
    elif fault == 'computed-output':
        value['normalized'][0] ^= 1
    elif fault == 'returned-PR':
        result['pr'] ^= 2
    else:
        result['accesses'].append(dict(site=contract.ENTRY, mode='read', domain='ram', register=0,
            address=0xFFFF41FB if fault == 'native-datum-read' else 0x010041FA,
            width_bytes=1 if fault == 'native-datum-read' else 2, bytes='a5' if fault == 'native-datum-read' else 'a5a5'))
    with pytest.raises(ValueError):
        transfers.require(observed, result, value, fixture)


def test_causal_mask_preserves_the_other_endpoint_axis_full_context_and_selected_byte():
    value = case()
    before = matrix.memory(value)
    result = equations(value)
    observed = dict(entry=contract.ENTRY, context=matrix.context({}, value), memory_before=(before,),
        memory_after=(result['memory'],), calibration_before=matrix.input_calibrations(value),
        bound_before=bytes(sum(r['size'] for r in contract.BOUND_SPANS)), frame_before=bytes(192),
        sp=0x30000000, continuation=0x30010000, abi_before=tuple(range(12)), sr_before=0)
    changed = deepcopy(observed)
    raw = bytearray(changed['calibration_before'][0x154C0])
    raw[1] ^= 1
    changed['calibration_before'][0x154C0] = bytes(raw)
    assert proof.held_key(observed, 0x154C0, 2, 'rom')[0] == proof.held_key(changed, 0x154C0, 2, 'rom')[0]
    raw = bytearray(changed['memory_before'][0])
    raw[0x41FB] ^= 1
    changed['memory_before'] = (bytes(raw),)
    assert proof.held_key(observed, 0x154C0, 2, 'rom')[0] != proof.held_key(changed, 0x154C0, 2, 'rom')[0]
