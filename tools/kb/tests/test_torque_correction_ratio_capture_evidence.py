"""Actual correction propagation, signed history arithmetic and complete-state refusals."""
from copy import deepcopy
import json
import pytest
from kb import repo, byte_surface_equations as state
from kb import torque_correction_ratio_contract as contract, torque_correction_ratio_matrix as matrix
from kb import torque_correction_ratio_semantics as semantics, torque_correction_ratio_transfers as transfers
from kb import torque_correction_ratio_capture_evidence as proof


def case(**updates):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal-control')
    value.update(updates)
    return value


def equations(value):
    calibration = matrix.input_calibrations(value)
    producer = semantics.caller(0, matrix.memory(value), calibration)
    consumer = semantics.caller(1, producer['memory'], calibration)
    return producer, consumer, calibration


def test_every_active_coefficient_word_changes_both_actual_ratio_bytes_with_other_inputs_fixed():
    for index in range(8):
        outputs = []
        for raw in (0, 512):
            curve = [256] * 9
            curve[index] = raw
            producer, consumer, calibration = equations(case(coefficient_curve=curve, word_11bc=index * 8192))
            assert producer['correction'] == consumer['correction'] == raw // 2
            assert producer['memory'][0x14E2:0x14E4] == (raw // 2).to_bytes(2, 'big')
            outputs.append((consumer['memory'][0x186C], consumer['memory'][0x1864]))
        assert outputs == [(0, 0), (32, 32)]
    for poison in (0, 1, 32767, 32768, 65535):
        producer, consumer, calibration = equations(case(prior_14e2=poison))
        assert producer['correction'] == consumer['correction'] == 128
        assert consumer['memory'][0x186C] == consumer['memory'][0x1864] == 16


def test_actual_byte_selection_and_negative_product_clamp_remain_distinct():
    producer, consumer, calibration = equations(case(coefficient_curve=[512] * 9,
        byte_1071=32, byte_2772=224, byte_4181=0, rom_8639=128))
    assert producer['selected'] == 128 and producer['correction'] == 0
    producer, consumer, calibration = equations(case(coefficient_curve=[512] * 9,
        byte_1071=32, byte_2772=224, byte_4181=128, rom_8639=128))
    assert producer['selected'] == 32 and producer['correction'] == 192
    assert consumer['memory'][0x186C] == consumer['memory'][0x1864] == 24
    producer, consumer, calibration = equations(case(coefficient_curve=[65535] * 9, byte_1071=255))
    assert producer['product'] < 0 and producer['correction'] == 0


@pytest.mark.parametrize('delay,selected', ((0, 2048), (1, 1024), (4, 4096), (10, 10240), (255, 10240)))
def test_delay_selects_actual_history_before_descending_shift(delay, selected):
    producer, consumer, calibration = equations(case(rom_8c61=delay,
        **{f'history_{index}': 1024 * (index + 1) for index in range(10)}))
    assert consumer['delayed'] == selected
    assert semantics.word(consumer['memory'], 0x19A0) == selected
    assert semantics.word(consumer['memory'], 0x19F6) == 2048
    assert semantics.word(consumer['memory'], 0x19F8) == 1024
    assert semantics.word(consumer['memory'], 0x1A08) == 9216


def test_initialization_preserves_flag_bits_and_signed_lag_floor_keeps_stuck_progress():
    producer, consumer, calibration = equations(case(byte_24a3=0xA0,
        **{f'history_{index}': 65535 for index in range(10)}))
    assert consumer['initialized'] is True and consumer['memory'][0x24A3] == 0xA8
    assert consumer['history_before_shift'] == (2048,) * 10
    producer, consumer, calibration = equations(case(word_199e=0, word_19c6=1, lag_curve=[0] * 16))
    assert (consumer['lag_initial'], consumer['lag']) == (0, 1)
    producer, consumer, calibration = equations(case(word_199e=65533, word_19c6=1, lag_curve=[32768] * 16))
    assert (consumer['lag_initial'], consumer['lag']) == (-1, -1)


def test_signed_factor_truncation_keeps_actual_low_word_wrap_and_zero():
    producer, consumer, calibration = equations(case(word_18d4=32768, byte_16a3=255,
        rom_83c1=32, rom_8b38=2))
    assert consumer['factor_quotient'] == 1359872
    assert (consumer['stored_divisor'], consumer['divisor']) == (49152, -16384)
    producer, consumer, calibration = equations(case(word_18d4=65535, byte_16a3=6,
        rom_83c1=32, rom_8b38=2))
    assert consumer['factor_quotient'] == consumer['stored_divisor'] == consumer['divisor'] == 0


@pytest.mark.parametrize('source,divisor,expected', ((32767, 0, 255), (1, 0, 255),
    (32768, 0, 0), (65535, 65535, 255), (1, 65535, 0)))
def test_actual_sentinel_zero_divisor_and_signed_quotient_branches(source, divisor, expected):
    producer, consumer, calibration = equations(case(word_19cc=source, word_34b8=source,
        word_199e=divisor, word_19c6=divisor, coefficient_curve=[0] * 9,
        **{f'history_{index}': divisor for index in range(10)}))
    assert consumer['memory'][0x186C] == consumer['memory'][0x1864] == expected


def handoff():
    producer, consumer, calibration = equations(case())
    first = dict(phase=0, pair=0, memory_after=(producer['memory'],), calibration_after=calibration, bound_after=b'complete-bound')
    second = dict(phase=1, pair=0, memory_before=(producer['memory'],), calibration_before=deepcopy(calibration), bound_before=b'complete-bound')
    return first, second, producer, consumer


@pytest.mark.parametrize('fault', ('unrelated-RAM', 'same-correction-reset', 'history', 'calibration', 'bound', 'pair', 'phase', 'synthetic-correction'))
def test_matching_correction_or_output_cannot_replace_complete_phase_continuity(fault):
    first, second, producer, consumer = handoff()
    transfers.require_handoff(first, second, producer, consumer)
    if fault in ('unrelated-RAM', 'same-correction-reset', 'history'):
        raw = bytearray(second['memory_before'][0])
        raw[{'unrelated-RAM': 0x4000, 'same-correction-reset': 0x14E4, 'history': 0x19F6}[fault]] ^= 1
        second['memory_before'] = (bytes(raw),)
    elif fault == 'calibration':
        second['calibration_before'][0x83C1] = b'\x20'
    elif fault == 'bound':
        second['bound_before'] = b'other-bound'
    elif fault == 'pair':
        second['pair'] = 1
    elif fault == 'phase':
        second['phase'] = 0
    else:
        producer['correction'] ^= 1
    with pytest.raises(ValueError):
        transfers.require_handoff(first, second, producer, consumer)

def raw_packet():
    declared = dict(cases=[case()], calibration_spans=[[r['address'], r['size']] for r in contract.CONTROLLED_CALIBRATION],
        bound_spans=[[r['address'], r['size']] for r in contract.BOUND_SPANS])
    rows = []
    for phase in (0, 1):
        context = b''.join(v.to_bytes(4, 'big') for v in matrix.context({}, case(), phase)).hex()
        rows.append(dict(schema=1, pair=0, phase=phase, phase_id=('producer', 'consumer')[phase], entry=contract.ENTRIES[phase],
            context=context, context_after=context, observation=bytes(572).hex(), ram_before='65536:a5', ram_after='65536:a5',
            calibration_before=bytes(sum(n for at, n in declared['calibration_spans'])).hex(),
            calibration_after=bytes(sum(n for at, n in declared['calibration_spans'])).hex(),
            bound_before=bytes(sum(n for at, n in declared['bound_spans'])).hex(),
            bound_after=bytes(sum(n for at, n in declared['bound_spans'])).hex()))
    marker = proof.MARKER + ' status=PASS region=' + proof.REGION + ' pairs=1 phases=2'
    return declared, rows, dict(observations=deepcopy(rows), marker=marker,
        stdout='\n'.join([*(proof.PREFIX + json.dumps(r) for r in rows), marker]))


@pytest.mark.parametrize('fault', ('missing', 'reverse', 'duplicate-id', 'wrong-entry', 'context', 'duplicate-key'))
def test_raw_stream_rejects_incomplete_or_detached_phase_identity(fault):
    declared, rows, packet = raw_packet()
    assert len(proof.observations(packet, declared)) == 2
    if fault == 'missing':
        rows.pop()
    elif fault == 'reverse':
        rows.reverse()
    elif fault == 'duplicate-id':
        rows[1]['phase'] = 0
    elif fault == 'wrong-entry':
        rows[1]['entry'] = 0x658A4
    elif fault == 'context':
        rows[1]['context_after'] = bytes(80).hex()
    packet['observations'] = deepcopy(rows)
    packet['stdout'] = '\n'.join([*(proof.PREFIX + json.dumps(r) for r in rows), packet['marker']])
    if fault == 'duplicate-key':
        packet['stdout'] = packet['stdout'].replace('"schema": 1', '"schema": 1, "schema": 1', 1)
    with pytest.raises(ValueError):
        proof.observations(packet, declared)


def reconstructed(phase):
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    source, value = contract.descriptor(repo.ROOT), case()
    fixture, _ = contract.fixture_for_case(source, image, value)
    memory = matrix.memory(value)
    calibration = matrix.calibrations(source, image, value)
    for current in range(phase + 1):
        context = matrix.context(source, value, current)
        sp, continuation = 0x30000000, 0x30010000
        frame = bytearray(b''.join((0xA3B4C5D6 + i * 17).to_bytes(4, 'big') for i in range(48)))
        frame[160:164] = context[19].to_bytes(4, 'big')
        frame[164:168] = context[7].to_bytes(4, 'big')
        frame[184:188] = continuation.to_bytes(4, 'big')
        result = state.execute(source, fixture, context, memory, bytes(frame), sp, continuation,
            contract.ENTRIES[current], 0, trace=True)
        observed = dict(phase=current, pair=0, context=context, sp=sp, continuation=continuation,
            exit=(result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])),
            frame_after=result['frame'], memory_before=(memory,), memory_after=(result['ram'],),
            calibration_before=calibration, sr_before=0)
        numeric = semantics.caller(current, memory, calibration)
        memory = result['ram']
    return observed, result, numeric, fixture


@pytest.mark.parametrize('phase', (0, 1))
@pytest.mark.parametrize('fault', ('exit-SR', 'frame-byte', 'RAM-byte', 'call-argument', 'returned-PR', 'physical-width', 'delay-slot'))
def test_complete_state_rejects_changes_outside_the_scalar_correction(phase, fault):
    observed, result, numeric, fixture = reconstructed(phase)
    transfers.require(observed, result, numeric, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame-byte':
        raw = bytearray(observed['frame_after']); raw[0] ^= 1; observed['frame_after'] = bytes(raw)
    elif fault == 'RAM-byte':
        raw = bytearray(observed['memory_after'][0]); raw[0] ^= 1; observed['memory_after'] = (bytes(raw),)
    elif fault == 'call-argument':
        raw = list(result['calls'][0]['entry']['registers']); raw[4] ^= 2; result['calls'][0]['entry']['registers'] = tuple(raw)
    elif fault == 'returned-PR':
        result['pr'] ^= 2
    elif fault == 'physical-width':
        next(r for r in result['accesses'] if r['site'] == (0x6591E if phase == 0 else 0x64BD4))['width_bytes'] = 1
    else:
        result['trace'][-1]['delay_slot'] = False
    with pytest.raises(ValueError):
        transfers.require(observed, result, numeric, fixture)
