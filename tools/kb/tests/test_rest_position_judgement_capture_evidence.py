"""Real selected-byte fault effects, exact threshold boundaries and complete-state refusals."""
from copy import deepcopy
import pytest
from kb import repo, byte_surface_equations as state
from kb import rest_position_judgement_contract as contract, rest_position_judgement_matrix as matrix
from kb import rest_position_judgement_semantics as numeric, rest_position_judgement_transfers as transfers
from kb import rest_position_judgement_capture_evidence as proof


def case(**changes):
    value = dict(deepcopy(matrix.DEFAULTS), index=0, kind='independent-refusal')
    value.update(changes)
    return value


def equations(value):
    return numeric.caller(matrix.memory(value), matrix.input_calibrations(value), matrix.context({}, value))


def test_only_the_selected_byte_changes_both_actual_fault_publications():
    results = [equations(case(byte_16bb=raw)) for raw in (0, 128, 255)]
    assert [r['flags'][1:] for r in results] == [(2, 2), (0, 0), (2, 2)]
    assert [r['timers'] for r in results] == [(0, 0, 0, 0), (90, 90, 90, 90), (0, 0, 0, 0)]
    for raw, result in zip((0, 128, 255), results):
        assert result['memory'][0x16BB] == raw
        assert result['memory'][0x358B] == result['flags'][1]
        assert result['memory'][0x3582] == result['flags'][2]


@pytest.mark.parametrize(('selected', 'fault'), ((93, 2), (94, 0), (95, 0), (161, 0), (162, 0), (163, 2)))
def test_actual_upper_and_lower_equalities_are_inside_both_windows(selected, fault):
    result = equations(case(byte_16bb=selected))
    assert result['flags'][1:] == (fault, fault)
    assert result['first']['outside'] is result['second']['outside'] is bool(fault)


def test_signed_integer_thresholds_do_not_wrap_to_bytes():
    high = equations(case(byte_16bb=255, rom_8951=255, rom_8736=255))
    low = equations(case(byte_16bb=0, rom_8952=255, rom_8737=255))
    assert high['first']['high'] == high['second']['high'] == 383
    assert low['first']['low'] == low['second']['low'] == -127
    assert high['flags'][1:] == low['flags'][1:] == (0, 0)


def test_zero_reload_enters_the_actual_measurement_path_without_an_invented_wait():
    result = equations(case(byte_43c3=1, byte_43c2=1, rom_855d=0, rom_871f=0))
    assert not result['first_permit'] and not result['second_permit']
    assert result['first_counter'] == result['second_counter'] == 0
    assert result['first']['measured'] and result['second']['measured']
    assert result['flags'][1:] == (2, 2)


def test_four_timer_gates_and_unrelated_flag_bits_remain_independent():
    result = equations(case(byte_43c1=1, byte_43b7=1, byte_43b5=1, byte_43af=1))
    assert result['flags'][1:] == (0, 0) and result['timers'] == (1, 1, 1, 1)
    result = equations(case(byte_3599=0x80, byte_358b=0x80, byte_3582=0xFD))
    assert result['flags'] == (0x82, 0x82, 0xFF)
    context = list(matrix.DEFAULTS['context'])
    context[5] = 0
    reset = equations(case(context=context, byte_3599=255, byte_358b=0x80, byte_3582=0xFD))
    assert reset['flags'] == (0xFD, 0x80, 0xFD)
    assert reset['timers'] == (90, 90, 90, 90)
    assert reset['first_counter'] == reset['second_counter'] == 10


def reconstructed(**changes):
    source = contract.descriptor(repo.ROOT)
    image = repo.images(repo.ROOT)['JK08A'].path.read_bytes()
    value = case(**changes)
    fixture, _ = contract.fixture_for_case(source, image, value)
    context = matrix.context(source, value)
    sp, continuation = 0x30000000, 0x30010000
    frame = bytearray(b''.join((0xA3B4C5D6 + i * 17).to_bytes(4, 'big') for i in range(48)))
    frame[160:164] = context[19].to_bytes(4, 'big')
    frame[164:168] = context[7].to_bytes(4, 'big')
    frame[184:188] = continuation.to_bytes(4, 'big')
    before, calibration = matrix.memory(value), matrix.calibrations(source, image, value)
    result = state.execute(source, fixture, context, before, bytes(frame), sp, continuation, contract.ENTRY, 0, trace=True)
    observed = dict(entry=contract.ENTRY, context=context, sp=sp, continuation=continuation, memory_before=(before,),
        calibration_before=calibration, frame_before=bytes(frame), frame_after=result['frame'], memory_after=(result['ram'],),
        exit=(result['sr'], result['pr'], result['macl'], result['mach'], result['gbr'], *reversed(result['registers'])), sr_before=0)
    return observed, result, numeric.caller(before, calibration, context), fixture


@pytest.mark.parametrize('changes', ({}, dict(byte_16bb=128), dict(byte_43c3=1),
    dict(byte_43c2=1), dict(byte_2327=0), dict(rom_8e25=255, rom_8e1c=128),
    dict(byte_3599=255, byte_358b=255, byte_3582=255)))
def test_complete_fault_inside_reset_reload_and_high_bit_paths(changes):
    observed, result, value, fixture = reconstructed(**changes)
    transfers.require(observed, result, value, fixture)


@pytest.mark.parametrize('fault', ('exit-SR', 'frame', 'other-RAM', 'read-width', 'same-fault-other-input',
    'ROM-byte', 'local-mask', 'return-GBR', 'invented-call', 'delay-slot', 'computed-flags'))
def test_matching_low_fault_bytes_cannot_replace_complete_operands_or_natural_state(fault):
    observed, result, value, fixture = reconstructed()
    transfers.require(observed, result, value, fixture)
    if fault == 'exit-SR':
        observed['exit'] = (observed['exit'][0] ^ 1, *observed['exit'][1:])
    elif fault == 'frame':
        observed['frame_after'] = b'\x01' + observed['frame_after'][1:]
    elif fault == 'other-RAM':
        raw = bytearray(observed['memory_after'][0]); raw[0x88] ^= 1; observed['memory_after'] = (bytes(raw),)
    elif fault in ('read-width', 'same-fault-other-input'):
        event = next(r for r in result['accesses'] if r['site'] == 0x9030C)
        event['width_bytes' if fault == 'read-width' else 'bytes'] = 2 if fault == 'read-width' else 'ff'
    elif fault == 'ROM-byte':
        next(r for r in result['accesses'] if r['site'] == 0x9030E)['bytes'] = 'ff'
    elif fault == 'local-mask':
        next(r for r in result['accesses'] if r['site'] == 0x902FA)['bytes'] = '01'
    elif fault == 'return-GBR':
        result['gbr'] ^= 1
    elif fault == 'invented-call':
        result['calls'].append(dict(site=contract.ENTRY))
    elif fault == 'delay-slot':
        result['trace'][-1]['delay_slot'] = False
    else:
        raw = bytearray(value['memory']); raw[0x358B] ^= 2; value['memory'] = bytes(raw)
    with pytest.raises(ValueError):
        transfers.require(observed, result, value, fixture)


def test_held_other_mask_does_not_hide_an_unrelated_timer_or_full_bank_context_change():
    value = case()
    result = equations(value)
    observed = dict(entry=contract.ENTRY, context=matrix.context({}, value), memory_before=(matrix.memory(value),),
        memory_after=(result['memory'],), calibration_before=matrix.input_calibrations(value),
        bound_before=bytes(sum(r['size'] for r in contract.BOUND_SPANS)), frame_before=bytes(192),
        sp=0x30000000, continuation=0x30010000, abi_before=tuple(range(12)), sr_before=0)
    second = deepcopy(observed)
    raw = bytearray(second['memory_before'][0]); raw[0x16BB] = 128; second['memory_before'] = (bytes(raw),)
    assert proof.held_key(observed, matrix.RAM_BASE + 0x16BB, 1, 'ram')[0] == proof.held_key(second, matrix.RAM_BASE + 0x16BB, 1, 'ram')[0]
    raw[0x43C1] ^= 1; second['memory_before'] = (bytes(raw),)
    assert proof.held_key(observed, matrix.RAM_BASE + 0x16BB, 1, 'ram')[0] != proof.held_key(second, matrix.RAM_BASE + 0x16BB, 1, 'ram')[0]
