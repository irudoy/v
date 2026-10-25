"""Independent word wrap, neutral boundaries and complete physical-state refusals."""
from copy import deepcopy
import pytest
from kb import repo, byte_surface_equations as state
from kb import ltft_adjustment_update_contract as contract, ltft_adjustment_update_matrix as matrix
from kb import ltft_adjustment_update_semantics as numeric, ltft_adjustment_update_transfers as transfers
from kb import ltft_adjustment_update_capture_evidence as proof


def case(**changes):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal')
    value.update(changes)
    return value


def equations(value):
    return numeric.caller(matrix.memory(value), matrix.input_calibrations(value), matrix.context({}, value))


def test_each_exact_word_has_held_other_actual_output_alternatives():
    for name, inputs, outputs in (('word_2304', (0, 65535), (30000, 29983)),
                                  ('word_2308', (0, 32768), (29993, 30007)),
                                  ('word_564a', (25000, 30000), (25007, 29993))):
        result = [equations(case(**{name: raw})) for raw in inputs]
        assert tuple(value['value'] for value in result) == outputs
        for value in result:
            assert int.from_bytes(value['memory'][0x564A:0x564C], 'big') == value['value']
            assert value['memory'][0x5648:0x564A] == bytes.fromhex('beef')
            assert value['memory'][0x564C:0x564E] == bytes.fromhex('cafe')


def test_signed_sum_and_candidate_words_keep_their_actual_lowword_wrap():
    value = equations(case(word_1308=65535, word_2308=1))
    assert (value['signed_sum'], value['error']) == (0, 39936)
    up = equations(case(word_564a=65535, rom_878f=0))
    down = equations(case(word_564a=0, word_1308=0))
    assert (up['increased'], up['candidate'], up['value']) == (6, 6, 21760)
    assert (down['decreased'], down['candidate'], down['value']) == (65529, 65529, 33024)


def test_exact_neutral_crossings_and_quiet_paths_use_the_real_delta():
    for old in (25593, 25607):
        for active in (0, 2):
            value = equations(case(word_564a=old, byte_3e30=active))
            assert value['delta'] == 7 and value['candidate'] == value['value'] == 25600
    held = equations(case(byte_3e30=0, byte_3ea4=2, byte_2461=0))
    assert held['candidate'] == held['value'] == 30000 and held['branch'] == 'quiet-status-hold'


def test_temperature_steps_wrap_before_the_actual_global_raw_bounds():
    down = equations(case(byte_22e1=0, word_29e4=0, word_564a=1))
    up = equations(case(byte_22e1=0, word_29e4=65535, word_564a=65535))
    assert (down['candidate'], down['value']) == (65281, 33024)
    assert (up['candidate'], up['value']) == (255, 21760)
    assert down['reset_after'] == up['reset_after'] == 0


def test_unordered_bounds_and_neutralization_after_them_remain_separate():
    bounded = equations(case(rom_86be=0, rom_86bf=255))
    neutral = equations(case(rom_86be=0, rom_86bf=255, record_129=128, byte_41b5=255))
    assert (bounded['limited_upper'], bounded['limited'], bounded['value']) == (0, 65280, 65280)
    assert neutral['limited'] == 65280 and neutral['value'] == 25600 and neutral['control_neutral'] is None
    timer = equations(case(byte_4498=255))
    assert timer['timer_after'] == 255 and not timer['timer_written'] and timer['value'] == 30000


def reconstructed(**changes):
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value = case(**changes)
    fixture, _ = contract.fixture_for_case(source, image, value)
    context = matrix.context(source, value)
    sp, continuation = 0x30000000, 0x30010000
    frame = bytearray(b''.join((0xA3B4C5D6 + index * 17).to_bytes(4, 'big') for index in range(48)))
    frame[160:164] = context[19].to_bytes(4, 'big')
    frame[164:168] = context[7].to_bytes(4, 'big')
    frame[184:188] = continuation.to_bytes(4, 'big')
    before, calibration = matrix.memory(value), matrix.calibrations(source, image, value)
    result = state.execute(source, fixture, context, before, bytes(frame), sp, continuation, contract.ENTRY, 0, trace=True)
    observed = dict(entry=contract.ENTRY, context=context, sp=sp, continuation=continuation, memory_before=(before,),
        calibration_before=calibration, frame_before=bytes(frame), frame_after=result['frame'], memory_after=(result['ram'],),
        exit=(result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])), sr_before=0)
    return observed, result, numeric.caller(before, calibration, context), fixture


@pytest.mark.parametrize('changes', ({}, dict(word_1308=0), dict(word_1308=65535), dict(byte_3e30=0),
    dict(byte_3e30=0, byte_3ea4=2, byte_2461=0), dict(byte_4498=255), dict(byte_22e1=0),
    dict(byte_230e=0, word_29e4=0), dict(byte_22e1=0, word_29e4=65535),
    dict(record_129=128), dict(byte_41b5=1), dict(word_564a=25593), dict(word_564a=25607)))
def test_complete_real_update_hold_reset_temperature_and_neutral_paths(changes):
    observed, result, value, fixture = reconstructed(**changes)
    transfers.require(observed, result, value, fixture)


@pytest.mark.parametrize('fault', ('exit-SR', 'frame', 'other-RAM', 'read-width', 'local-word', 'live-store',
    'post-delay-divisor', 'fixed-ID', 'return-GBR', 'delay-slot', 'computed-word'))
def test_matching_adjustment_bytes_cannot_replace_complete_operands_or_state(fault):
    observed, result, value, fixture = reconstructed()
    transfers.require(observed, result, value, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame':
        observed['frame_after'] = b'\x01' + observed['frame_after'][1:]
    elif fault == 'other-RAM':
        raw = bytearray(observed['memory_after'][0]); raw[0x88] ^= 1; observed['memory_after'] = (bytes(raw),)
    elif fault == 'read-width':
        next(row for row in result['accesses'] if row['site'] == 0x5820A)['width_bytes'] = 1
    elif fault == 'local-word':
        next(row for row in result['accesses'] if row['site'] == 0x58218)['bytes'] = '0000'
    elif fault == 'live-store':
        row = next(row for row in result['trace'] if row['site'] == 0x5848E)
        registers = list(row['before']['registers']); registers[14] += 65536; row['before']['registers'] = tuple(registers)
    elif fault in ('post-delay-divisor', 'fixed-ID'):
        call = next(row for row in result['calls'] if row['site'] == (0x581AE if fault == 'post-delay-divisor' else 0x58478))
        registers = list(call['entry']['registers']); registers[0 if fault == 'post-delay-divisor' else 4] = 0
        call['entry']['registers'] = tuple(registers)
    elif fault == 'return-GBR':
        result['gbr'] ^= 1
    elif fault == 'delay-slot':
        result['trace'][-1]['delay_slot'] = False
    else:
        raw = bytearray(value['memory']); raw[0x564A] ^= 1; value['memory'] = bytes(raw)
    with pytest.raises(ValueError):
        transfers.require(observed, result, value, fixture)


def test_held_other_key_preserves_the_other_reader_and_complete_context():
    value = case()
    observed = dict(entry=contract.ENTRY, context=matrix.context({}, value), memory_before=(matrix.memory(value),),
        calibration_before=matrix.input_calibrations(value), bound_before=bytes(sum(row['size'] for row in contract.BOUND_SPANS)),
        frame_before=bytes(192), sp=0x30000000, continuation=0x30010000, abi_before=tuple(range(12)), sr_before=0)
    changed = deepcopy(observed)
    raw = bytearray(changed['memory_before'][0]); raw[0x2304:0x2306] = b'\xff\xff'; changed['memory_before'] = (bytes(raw),)
    assert proof.held_key(observed, matrix.RAM_BASE + 0x2304, 2, 'ram')[0] == proof.held_key(changed, matrix.RAM_BASE + 0x2304, 2, 'ram')[0]
    raw[0x2308] ^= 1; changed['memory_before'] = (bytes(raw),)
    assert proof.held_key(observed, matrix.RAM_BASE + 0x2304, 2, 'ram')[0] != proof.held_key(changed, matrix.RAM_BASE + 0x2304, 2, 'ram')[0]
