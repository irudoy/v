"""Real coefficient propagation, shared latch state and complete raw/state refusal controls."""
from copy import deepcopy
import json
import pytest
from kb import repo, byte_surface_equations as state
from kb import blend_weight_quantity_contract as contract, blend_weight_quantity_matrix as matrix
from kb import blend_weight_quantity_semantics as semantics, blend_weight_quantity_transfers as transfers
from kb import blend_weight_quantity_capture_evidence as proof


def case(**updates):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal-control')
    value.update(updates)
    return value


def equations(value):
    calibration = matrix.input_calibrations(value)
    producer = semantics.caller(0, matrix.memory(value), calibration)
    consumer = semantics.caller(1, producer['memory'], calibration)
    return producer, consumer, calibration


def test_every_active_curve_word_changes_real124A_without_a_terminal_selector_claim():
    for index in range(16):
        inputs = []
        for raw in (0, 32768):
            curve = [32768] * 17
            curve[index] = raw
            p, c, cal = equations(case(weight_curve=curve, word_1a78=index * 4096))
            assert p['weight'] == c['weight'] == raw
            assert p['memory'][0x190E:0x1910] == raw.to_bytes(2, 'big')
            assert c['memory'][0x124A:0x124C] == c['blend'].to_bytes(2, 'big')
            inputs.append((p, c))
        assert (inputs[0][1]['blend'], inputs[1][1]['blend']) == (0, 32767)
        assert inputs[0][1]['final'] == inputs[1][1]['final'] == 0x5000
    for poison in (0, 1, 32767, 32768, 65535):
        assert equations(case(prior_190e=poison))[1]['blend'] == 32767


def test_actual_coordinate_refresh_and_zero_fraction_neighbor_remain_distinct_obligations():
    curve = [4095 * index for index in range(17)]
    p, c, cal = equations(case(byte_417e=8, word_10d2=4096, word_1a78=0x5000, weight_curve=curve))
    assert p['coordinate_refreshed'] is True and p['weight_coordinate'] == 4096
    assert p['weight'] == c['weight'] == curve[1]
    for guard in (0, 1, 32767, 32768, 65535):
        curve = [32768] * 17
        curve[16] = guard
        p, c, cal = equations(case(word_1a78=65535, weight_curve=curve))
        assert p['weight_curve']['physical_cells'] == [15, 16]
        assert p['weight_curve']['fraction'] == 0 and p['weight'] == 32768
        assert c['blend'] == 32767


def test_unsigned_comparisons_use_actual_sign_extended_MOV_W_operands():
    p, c, cal = equations(case(rom_89fb=0x40, word_10d2=0x8000, rom_95d2=0x7FFF, rom_16338=0x7FFF))
    assert p['rate_branch'] == c['rate_branch'] == 'coordinate-limit'
    p, c, cal = equations(case(rom_89fb=0x40, word_10d2=0x7FFF, rom_95d2=0x8000,
        rom_16338=0x8000, rom_8775=100, rom_15f69=100))
    assert p['rate_branch'] == c['rate_branch'] == 'rate-add'
    assert p['rate_quotient'] == c['rate_quotient'] == 100


def test_latch_reconciliation_uses_actual_producer_flags_and_preserves_other_bits():
    p, c, cal = equations(case(byte_4205=0x80, byte_4214=0x84, byte_4180=0, rom_89fb=0x28))
    assert c['reconciled'] is True
    assert c['memory'][0x4205] == c['memory'][0x4214] == 0x80
    assert c['final_enabled'] is False and c['final'] == 0x5000
    p, c, cal = equations(case(byte_4205=0x84, byte_4214=0x84, byte_4180=0, rom_89fb=0x28))
    assert c['reconciled'] is False and c['final_enabled'] is True and c['final'] == 32767


def handoff():
    p, c, cal = equations(case())
    a = dict(phase=0, pair=0, memory_after=(p['memory'],), calibration_after=cal, bound_after=b'complete-bound')
    b = dict(phase=1, pair=0, memory_before=(p['memory'],), calibration_before=deepcopy(cal), bound_before=b'complete-bound')
    return a, b, p, c


@pytest.mark.parametrize('fault', ('unrelated-RAM', 'same-weight-reset', 'shared-flag', 'calibration', 'bound', 'pair', 'phase', 'synthetic-weight'))
def test_matching_weight_or_final_output_cannot_replace_complete_phase_continuity(fault):
    a, b, p, c = handoff()
    transfers.require_handoff(a, b, p, c)
    if fault in ('unrelated-RAM', 'same-weight-reset', 'shared-flag'):
        raw = bytearray(b['memory_before'][0])
        raw[{'unrelated-RAM': 0x4000, 'same-weight-reset': 0x1A78, 'shared-flag': 0x4205}[fault]] ^= 1
        b['memory_before'] = (bytes(raw),)
    elif fault == 'calibration':
        b['calibration_before'][0x89FB] = b'\x28'
    elif fault == 'bound':
        b['bound_before'] = b'other-bound'
    elif fault == 'pair':
        b['pair'] = 1
    elif fault == 'phase':
        b['phase'] = 0
    else:
        p['weight'] ^= 1
    with pytest.raises(ValueError):
        transfers.require_handoff(a, b, p, c)


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
        rows[1]['entry'] = 0x70E4C
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
def test_complete_state_rejects_changes_outside_the_scalar_weight(phase, fault):
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
        next(r for r in result['accesses'] if r['site'] == (0x70EC2 if phase == 0 else 0x7211A))['width_bytes'] = 1
    else:
        result['trace'][-1]['delay_slot'] = False
    with pytest.raises(ValueError):
        transfers.require(observed, result, numeric, fixture)
