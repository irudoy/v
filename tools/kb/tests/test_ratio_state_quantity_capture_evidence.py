"""Real table-derived handoff, signed filters, zero errors and complete-state refusals."""
from copy import deepcopy
import json
import pytest
from kb import repo, byte_surface_equations as state
from kb import ratio_state_quantity_contract as contract, ratio_state_quantity_matrix as matrix
from kb import ratio_state_quantity_semantics as semantics, ratio_state_quantity_transfers as transfers
from kb import ratio_state_quantity_capture_evidence as proof


def case(**updates):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal-control')
    value.update(updates)
    return value


def equations(value):
    calibration = matrix.input_calibrations(value)
    producer = semantics.caller(0, matrix.memory(value), calibration)
    consumer = semantics.caller(1, producer['memory'], calibration)
    return producer, consumer, calibration


def test_every_ratio_word_changes_actual_quantity_and_both_later_outputs_with_other_inputs_fixed():
    for index in range(16):
        outputs = []
        for raw in (0, 1024):
            curve = [0] * 16
            curve[index] = raw
            producer, consumer, calibration = equations(case(ratio_curve=curve, rom_920e=(32768 * index + 14) // 15))
            assert producer['quantity'] == consumer['quantity'] == raw
            assert producer['memory'][0x19A2:0x19A4] == raw.to_bytes(2, 'big')
            outputs.append((consumer['first'], consumer['result']))
        assert outputs == [(0, 0), (1024, 1023)]
    for poison in (0, 1, 32767, 32768, 65535):
        producer, consumer, calibration = equations(case(prior_19a2=poison))
        assert producer['quantity'] == consumer['quantity'] == consumer['first'] == 1024
        assert consumer['result'] == 1023


def test_actual_primary_zero_source_and_wide_unsigned_division_remain_distinct():
    producer, consumer, calibration = equations(case(word_1702=0))
    assert producer['divisor'] is None and producer['primary'] == 65535
    producer, consumer, calibration = equations(case(word_1702=65535, word_10d6=65535, word_1582=65535))
    assert (producer['divisor'], producer['dividend'], producer['quotient']) == (204796, 4026470400, 19660)
    assert producer['memory'][0x17E2:0x17E4] == (19660).to_bytes(2, 'big')


def test_real_signed_shift_return_cannot_replace_the_unsigned_post_shift_cap():
    producer, consumer, calibration = equations(case(ratio_curve=[65535] * 16, word_1770=65535))
    assert consumer['product'] == 0xFFFE0001
    assert consumer['shifted_return'] == 0xFFFFF800
    assert consumer['scaled_product'] == 65535 and consumer['first'] == 32767
    producer, consumer, calibration = equations(case(ratio_curve=[65535] * 16, word_1770=65535, word_18d2=65535))
    assert consumer['first_quotient'] == -65535 and consumer['first'] == -32768


def test_zero_divisor_executes_error_store_and_preserves_all_other_RAM():
    producer, consumer, calibration = equations(case(rom_944e=0, prior_9818=0x12345678))
    assert consumer['first_quotient'] == consumer['first'] == 0
    assert consumer['memory'][0x9818:0x981C] == bytes.fromhex('0000044e')
    assert producer['memory'][0x9818:0x981C] == bytes.fromhex('12345678')
    changed = {i for i, (a, b) in enumerate(zip(producer['memory'], consumer['memory'])) if a != b}
    assert changed <= {*(i for at, width in ((0x145A, 2), (0x1792, 2), (0x14F4, 2), (0x1540, 4),
        (0x14F8, 4), (0x14F6, 2), (0x1508, 2), (0x177E, 2), (0x177C, 2), (0x9818, 4)) for i in range(at, at + width))}


def test_shared_neighbor_word_and_complete_signed_centered_offset_remain_physical():
    blob = [32768] * 8 + [100 + 8000 * i for i in range(8)]
    producer, consumer, calibration = equations(case(centered_curve_axis=blob, word_1152=65535))
    assert len(calibration[0x15276]) == 32 and 0x15286 not in calibration
    assert consumer['curve']['physical_cells'] == (7, 8)
    assert consumer['curve']['second'] == 100
    assert consumer['curve']['centered'] == 0
    assert consumer['curve']['initial_live_signed_offset'] == 0xFFFF0000
    assert consumer['memory'][0x1792:0x1794] == bytes(2)


def test_accumulator_wrap_signed_delta_truncation_and_stuck_progress():
    producer, consumer, calibration = equations(case(long_1540=0xFFFFFFFF, word_1152=0, rom_95a0=65535))
    assert consumer['accumulator_one']['updated'] == 131070
    assert consumer['accumulator_one']['raw_delta'] == 131071 and consumer['delta'] == 511
    producer, consumer, calibration = equations(case(long_1540=0, word_1152=1, rom_95a0=0,
        long_14f8=0, rom_918e=0))
    assert consumer['accumulator_one']['updated'] == consumer['accumulator_two']['updated'] == 1
    assert consumer['accumulator_one']['incremented'] and consumer['accumulator_two']['incremented']
    producer, consumer, calibration = equations(case(long_1540=0x80000000, word_1152=0, rom_95a0=1))
    assert (consumer['delta'], consumer['delta_product'], consumer['delta_scaled']) == (-128, -36224, -141)


def test_final_lag_preserves_stuck_adjustment_unsigned_previous_word_and_negative_floor():
    producer, consumer, calibration = equations(case(rom_928c=0, word_177c=0))
    assert (consumer['lag_initial'], consumer['lag'], consumer['result']) == (0, 1, 1)
    producer, consumer, calibration = equations(case(rom_928c=0, word_177c=0,
        centered_curve_axis=[65535] * 8 + [8192 * i for i in range(8)]))
    assert (consumer['lag_initial'], consumer['lag'], consumer['result']) == (0, -1, 0)
    producer, consumer, calibration = equations(case(rom_928c=0, word_177c=65535))
    assert consumer['previous'] == 65535 and consumer['lag_initial'] == -1 and not consumer['stuck']
    assert consumer['result'] == 0


def handoff():
    producer, consumer, calibration = equations(case())
    first = dict(phase=0, pair=0, memory_after=(producer['memory'],), calibration_after=calibration, bound_after=b'complete-bound')
    second = dict(phase=1, pair=0, memory_before=(producer['memory'],), calibration_before=deepcopy(calibration), bound_before=b'complete-bound')
    return first, second, producer, consumer


@pytest.mark.parametrize('fault', ('unrelated-RAM', 'same-quantity-reset', 'accumulator', 'calibration', 'bound', 'pair', 'phase', 'synthetic-quantity'))
def test_matching_quantity_or_output_cannot_replace_complete_phase_continuity(fault):
    first, second, producer, consumer = handoff()
    transfers.require_handoff(first, second, producer, consumer)
    if fault in ('unrelated-RAM', 'same-quantity-reset', 'accumulator'):
        raw = bytearray(second['memory_before'][0])
        raw[{'unrelated-RAM': 0x4000, 'same-quantity-reset': 0x17E2, 'accumulator': 0x1540}[fault]] ^= 1
        second['memory_before'] = (bytes(raw),)
    elif fault == 'calibration':
        second['calibration_before'][0x944E] = bytes(2)
    elif fault == 'bound':
        second['bound_before'] = b'other-bound'
    elif fault == 'pair':
        second['pair'] = 1
    elif fault == 'phase':
        second['phase'] = 0
    else:
        producer['quantity'] ^= 1
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
        rows[1]['entry'] = 0x75174
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
def test_complete_state_rejects_changes_outside_the_scalar_quantity(phase, fault):
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
        next(r for r in result['accesses'] if r['site'] == (0x75204 if phase == 0 else 0x76568))['width_bytes'] = 1
    else:
        result['trace'][-1]['delay_slot'] = False
    with pytest.raises(ValueError):
        transfers.require(observed, result, numeric, fixture)
