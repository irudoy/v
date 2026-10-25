"""Independent arithmetic boundaries and complete actual physical-state refusal controls."""
from copy import deepcopy
import pytest
from kb import repo, byte_surface_equations as state
from kb import channel_target_builder_contract as contract, channel_target_builder_matrix as matrix
from kb import channel_target_builder_semantics as numeric, channel_target_builder_transfers as transfers
from kb import channel_target_builder_capture_evidence as proof


def case(**changes):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal')
    value.update(changes)
    return value


def equations(value):
    return numeric.caller(matrix.memory(value), matrix.input_calibrations(value), matrix.context({}, value))


def test_held_other_base_byte_changes_the_actual_channel_word():
    values = [equations(case(rom_8cb6=raw)) for raw in (39, 100)]
    assert [value['value'] for value in values] == [156, 400]
    for value in values:
        assert int.from_bytes(value['memory'][0x28BE:0x28C0], 'big') == value['value']
        assert value['memory'][0x28BC:0x28BE] == bytes.fromhex('beef')
        assert value['memory'][0x28C0:0x28C2] == bytes.fromhex('1234')


def test_first_coordinate_uses_floor_and_the_real_quarter_word_scratch():
    table = list(matrix.DEFAULTS['inverse_curve'])
    table[0] = 1027
    value = equations(case(word_1340=1, inverse_curve=table, byte_24ce=4, rom_9574=0, rom_9578=16383))
    assert (value['first_coordinate'], value['first_inverse']['value'], value['scratch'], value['value']) == (0, 1027, 256, 1024)
    assert value['memory'][0x28F8:0x28FA] == bytes.fromhex('0100')


def test_signed_correction_clamps_the_second_coordinate_without_unsigned_wrap():
    low = equations(case(byte_41a5=4, byte_244f=32, word_19b2=3, correction_570a=65535))
    high = equations(case(byte_41a5=4, byte_244f=32, word_19b2=65535, correction_570a=32767))
    negative = equations(case(byte_41a5=4, byte_244f=32, word_19b2=0, correction_570a=32768))
    assert (low['normal_coordinate'], high['normal_coordinate'], negative['normal_coordinate']) == (0, 65534, 0)
    assert (low['correction_signed'], negative['correction_signed']) == (-1, -32768)


def test_actual_unsigned_axis_numerator_can_have_bit31_set():
    table = [0] * 31 + [65535, 0]
    value = numeric.inverse_curve(b''.join(word.to_bytes(2, 'big') for word in table),
        b'\0\0' * 31 + b'\xff\xff', 32768)
    assert (value['index'], value['fraction'], value['value']) == (30, 32768, 32767)


def test_ordered_bounds_do_not_assume_a_lower_upper_relationship():
    lower = equations(case(rom_9574=1000, rom_9578=39))
    upper = equations(case(rom_9574=65535, rom_9578=38))
    assert (lower['initial_request'], lower['upper_stored'], lower['ordered'], lower['ordered_branch']) == (156, 156, 1000, 'lower')
    assert (upper['initial_request'], upper['upper_stored'], upper['ordered'], upper['ordered_branch']) == (156, 152, 152, 'upper')
    wrapped = equations(case(rom_9578=16384))
    dynamic = equations(case(byte_417e=0, rom_9576=16384, rom_9578=0))
    assert (wrapped['upper_raw'], wrapped['upper_stored'], wrapped['value']) == (65536, 0, 0)
    assert (dynamic['upper_raw'], dynamic['upper_stored'], dynamic['value']) == (65536, 0, 0)


def test_four_real_fixed_records_retain_short_circuit_and_both_caps():
    value = equations(case(record_6f=128, record_121=255, record_70=128, record_122=255, rom_92f2=100))
    assert value['predicate_121'] is value['predicate_122'] is None
    assert (value['ordered'], value['soft_limit'], value['soft_result'], value['value']) == (156, 136, 136, 100)
    inactive = equations(case(record_6f=127, record_121=127, record_70=127, record_122=127))
    assert not inactive['first_active'] and not inactive['second_active'] and inactive['value'] == 156


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


@pytest.mark.parametrize('changes', ({}, dict(byte_24ce=4), dict(byte_24d2=1), dict(byte_41a5=4),
    dict(byte_41a5=4, byte_244f=32, word_19b2=65535, correction_570a=1),
    dict(byte_417e=0, byte_11b3=97), dict(record_6f=128, record_70=128),
    dict(record_121=128, record_122=128), dict(rom_9574=1000, rom_9578=39),
    dict(byte_417e=0, rom_9576=16384, rom_9578=0)))
def test_complete_natural_modes_inverse_upper_ordered_and_fixed_record_paths(changes):
    observed, result, value, fixture = reconstructed(**changes)
    transfers.require(observed, result, value, fixture)


@pytest.mark.parametrize('fault', ('exit-SR', 'frame', 'other-RAM', 'word-read-width', 'curve-order', 'return-GBR',
    'local-channel', 'local-request', 'live-store', 'post-delay-index', 'delay-slot', 'computed-word', 'extra-call'))
def test_matching_target_bytes_cannot_replace_complete_operands_and_state(fault):
    observed, result, value, fixture = reconstructed()
    transfers.require(observed, result, value, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame':
        observed['frame_after'] = b'\x01' + observed['frame_after'][1:]
    elif fault == 'other-RAM':
        raw = bytearray(observed['memory_after'][0]); raw[0x88] ^= 1; observed['memory_after'] = (bytes(raw),)
    elif fault == 'word-read-width':
        next(row for row in result['accesses'] if row['site'] == 0x2653C)['width_bytes'] = 1
    elif fault == 'curve-order':
        call = next(row for row in result['calls'] if row['site'] == 0x6F4C4)
        registers = list(call['entry']['registers']); registers[4], registers[5] = registers[5], registers[4]
        call['entry']['registers'] = tuple(registers)
    elif fault == 'return-GBR':
        result['gbr'] ^= 1
    elif fault in ('local-channel', 'local-request'):
        site = 0x6F4A4 if fault == 'local-channel' else 0x6F58E
        next(row for row in result['accesses'] if row['site'] == site)['address'] += 1
    elif fault == 'live-store':
        row = next(row for row in result['trace'] if row['site'] == 0x6F668)
        registers = list(row['before']['registers']); registers[7] += 65536; row['before']['registers'] = tuple(registers)
    elif fault == 'post-delay-index':
        call = next(row for row in result['calls'] if row['site'] == 0x6F640)
        registers = list(call['entry']['registers']); registers[4] = 0x71; call['entry']['registers'] = tuple(registers)
    elif fault == 'delay-slot':
        result['trace'][-1]['delay_slot'] = False
    elif fault == 'extra-call':
        result['calls'].append(dict(site=contract.ENTRY, target=0, return_address=0))
    else:
        raw = bytearray(value['memory']); raw[0x28BE] ^= 1; value['memory'] = bytes(raw)
    with pytest.raises(ValueError):
        transfers.require(observed, result, value, fixture)


def test_held_other_group_retains_raw_other_controls_and_complete_context():
    value = case()
    result = equations(value)
    observed = dict(entry=contract.ENTRY, context=matrix.context({}, value), memory_before=(matrix.memory(value),),
        memory_after=(result['memory'],), calibration_before=matrix.input_calibrations(value),
        bound_before=bytes(sum(row['size'] for row in contract.BOUND_SPANS)), frame_before=bytes(192),
        sp=0x30000000, continuation=0x30010000, abi_before=tuple(range(12)), sr_before=0)
    changed = deepcopy(observed)
    changed['calibration_before'][0x8CB6] = bytes([100])
    assert proof.held_key(observed, 0x8CB6, 1, 'rom')[0] == proof.held_key(changed, 0x8CB6, 1, 'rom')[0]
    changed['calibration_before'][0x9574] = bytes.fromhex('ffff')
    assert proof.held_key(observed, 0x8CB6, 1, 'rom')[0] != proof.held_key(changed, 0x8CB6, 1, 'rom')[0]
