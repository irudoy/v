from dataclasses import fields, replace
import struct

import pytest

from patches import rolling_launch as rl


@pytest.fixture
def calibration():
    slot = rl.Slot(integral_gain=2, max_trim_rpm=20, max_trim_speed=20, floor_command=120,
                   launch_rpm_native=300, launch_speed_threshold=50,
                   launch_soft_width_native=40)
    return rl.Calibration(mode=rl.Mode.HOLD, enable_mask=31, slots=(slot,)*5,
                          run_timeout_ticks=20, rearm_ticks=3)


@pytest.fixture
def inputs():
    return rl.Inputs(button=rl.BUTTON_CANCEL, speed=500, rpm_native=280,
                     pedal=100, coolant=150, hcan1_state=1,
                     port_input_state=0x80, speed_wire_word=5000)


@pytest.fixture
def table():
    return rl.EfficiencyTable(tuple(1000-10*i for i in range(41)))


def activate(calibration, inputs, table):
    return rl.step(rl.RuntimeState(), inputs, calibration, table).state


def test_record_offsets_have_an_independent_binary_vector(calibration):
    data = calibration.to_bytes()
    assert len(data) == 102
    assert data[:8] == bytes.fromhex("524c06011f0000ff")
    assert data[0x1C:0x1E] == b"\0\0"
    assert data[0x23:0x28] == bytes.fromhex("00adb3a55a")
    assert data[0x28:0x34] == bytes.fromhex("000214147800012c00320028")
    assert data[0x64:] == bytes.fromhex("a55a")
    assert rl.Calibration.from_bytes(data) == calibration
    assert rl.Calibration().is_valid()
    assert rl.Calibration().enable_mask == 0


def test_asymmetric_trim_slots_preserve_word_alignment_and_reject_padding(calibration):
    c = replace(calibration, slots=tuple(replace(slot, max_trim_rpm=40,
                                                max_trim_speed=20) for slot in calibration.slots))
    data = c.to_bytes()
    assert data[0x28:0x34] == bytes.fromhex("000228147800012c00320028")
    assert rl.Calibration.from_bytes(data) == c
    damaged = bytearray(data)
    damaged[0x28+5] = 1
    assert not rl.Calibration.from_bytes(damaged).is_valid()


@pytest.mark.parametrize("size", [0, 40, 72, 92, 101, 103])
def test_record_wrong_size_is_not_a_legacy_upgrade(size):
    with pytest.raises(ValueError):
        rl.Calibration.from_bytes(bytes(size))


@pytest.mark.parametrize("name,value", [
    ("magic", 0), ("schema_version", 5), ("mode", 2), ("enable_mask", 32),
    ("options", 1), ("coolant_min", 256), ("coolant_max", -1),
    ("min_speed", -1), ("max_speed", 65536), ("min_rpm_native", 0),
    ("min_rpm_native", 32767), ("min_pedal", -1), ("window_width", 0),
    ("window_top", 256), ("u_rate_limit", 0), ("u_rate_limit", 1001),
    ("integrator_limit", 1001), ("reserved", 1), ("reserved_1c", 1),
    ("reserved_1d", 1), ("reserved_23", 1), ("abort_above", 0),
    ("abort_below", 256), ("run_timeout_ticks", 0), ("rearm_ticks", 32768),
    ("speed_frame_age_limit", 0), ("speed_frame_age_limit", 255),
    ("magic_inverse", 0), ("end_marker", 0), ("slot_end_marker", 0),
    ("mode", True), ("enable_mask", False),
])
def test_configuration_rejects_out_of_range_fields(calibration, name, value):
    assert not replace(calibration, **{name: value}).is_valid()


def test_cross_field_bounds_are_checked_with_correct_offset_sign(calibration):
    assert not replace(calibration, min_speed=600, max_speed=599).is_valid()
    assert not replace(calibration, coolant_min=200, coolant_max=199).is_valid()
    assert replace(calibration, target_speed_offset=99).is_valid()
    assert not replace(calibration, target_speed_offset=100).is_valid()
    assert replace(calibration, target_speed_offset=-149).is_valid()
    assert not replace(calibration, target_speed_offset=-150).is_valid()


@pytest.mark.parametrize("name,value", [
    ("integral_gain", -1), ("integral_gain", 32768),
    ("max_trim_rpm", 41), ("max_trim_speed", 41),
    ("max_trim_rpm", -1), ("max_trim_speed", -1), ("reserved_05", 1),
    ("floor_command", 121), ("launch_rpm_native", 160),
    ("launch_rpm_native", 32768), ("launch_speed_threshold", 0),
    ("launch_soft_width_native", -1), ("launch_soft_width_native", 140),
    ("max_trim_rpm", True), ("max_trim_speed", False),
])
def test_every_slot_is_checked_even_when_disabled(calibration, name, value):
    slots = list(calibration.slots)
    slots[4] = replace(slots[4], **{name: value})
    assert not replace(calibration, enable_mask=0, slots=tuple(slots)).is_valid()


def test_upper_bounds_and_hard_zone(calibration):
    slot = rl.Slot(integral_gain=32767, max_trim_rpm=40, max_trim_speed=40,
                   floor_command=120, launch_rpm_native=32767,
                   launch_speed_threshold=65535, launch_soft_width_native=32766-160)
    c = replace(calibration, slots=(slot,)*5, min_speed=0, max_speed=0,
                u_rate_limit=1000, integrator_limit=1000,
                run_timeout_ticks=32767, rearm_ticks=32767, speed_frame_age_limit=254)
    assert c.is_valid()
    assert rl.Calibration.from_bytes(c.to_bytes()) == c
    assert replace(c, slots=(replace(slot, launch_soft_width_native=0),)*5).is_valid()


def test_efficiency_table_serialization_and_validation(table):
    assert len(table.to_bytes()) == 82
    assert table.to_bytes()[:6] == bytes.fromhex("03e803de03d4")
    assert rl.EfficiencyTable.from_bytes(table.to_bytes()) == table
    for values in [(), (999,)*41, (1000,)*40, (1000,)*40+(0,), (1000,)*40+(1001,)]:
        assert not rl.EfficiencyTable(values).is_valid()
        with pytest.raises(ValueError):
            rl.EfficiencyTable(values).to_bytes()
    with pytest.raises(ValueError):
        rl.EfficiencyTable.from_bytes(bytes(82))


def test_efficiency_curve_interpolation_includes_descending_floor():
    axis = (0, 3, 6, 9, 12, 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45)
    values = (1, 8, 3, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140)
    table = rl.EfficiencyTable.from_curve(axis, values)
    assert table.at(0) == 1000
    assert table.at(1) == (256-3)*1000//256
    # 8 + floor(-5/3) = 6, rather than truncation toward zero to 7.
    assert table.at(4) == (256-6)*1000//256
    assert table.at(40) == (256-123)*1000//256
    with pytest.raises(ValueError):
        rl.EfficiencyTable.from_curve((0,)*16, values)


@pytest.mark.parametrize("width,error,expected", [
    (0, -1, 1000), (0, 0, 0), (0, 1, 0),
    (40, -41, 1000), (40, -40, 1000), (40, -20, 500),
    (40, -1, 25), (40, 0, 0), (40, 1, 0),
    (3, -2, 666), (3, -1, 333), (32767, -32768, 1000),
])
def test_rpm_fraction_boundaries(width, error, expected):
    assert rl.rpm_fraction(error, width) == expected


@pytest.mark.parametrize("speed,kind", [(0, rl.RegulatorKind.RPM),
    (49, rl.RegulatorKind.RPM), (50, rl.RegulatorKind.SPEED), (51, rl.RegulatorKind.SPEED)])
def test_threshold_uses_only_speed_and_equality_selects_speed(calibration, inputs, table, speed, kind):
    c = replace(calibration, min_speed=0)
    s = activate(c, replace(inputs, speed=speed), table)
    assert s.phase == rl.Phase.ACTIVE
    assert s.regulator_kind == kind
    assert s.cut_fraction == 0 and not s.actuation_ready


def test_speed_minimum_does_not_block_stationary_launch(calibration, inputs, table):
    s = activate(calibration, replace(inputs, speed=0), table)
    assert s.phase == rl.Phase.ACTIVE and s.regulator_kind == rl.RegulatorKind.RPM
    assert s.target_rpm_native == 300 and s.control_error == -20
    assert s.law_output == 500
    assert (s.target_speed, s.torque_fraction, s.integrator, s.torque_command) == (0, 0, 0, 0)


def test_mode_is_latched_when_threshold_is_crossed(calibration, inputs, table):
    rpm_inputs = replace(inputs, speed=0)
    rpm = activate(calibration, rpm_inputs, table)
    rpm = rl.step(rpm, inputs, calibration, table).state
    assert rpm.phase == rl.Phase.ACTIVE and rpm.regulator_kind == rl.RegulatorKind.RPM
    c = replace(calibration, min_speed=0)
    road = activate(c, replace(inputs, speed=50), table)
    road = rl.step(road, replace(inputs, speed=0), c, table).state
    assert road.phase == rl.Phase.ACTIVE and road.regulator_kind == rl.RegulatorKind.SPEED


def test_mode_selects_and_latches_its_own_trim(calibration, inputs, table):
    c = replace(calibration, min_speed=0, slots=tuple(
        replace(slot, max_trim_rpm=40, max_trim_speed=20) for slot in calibration.slots))
    rpm_inputs = replace(inputs, speed=0, rpm_native=280)
    rpm = activate(c, rpm_inputs, table)
    speed = activate(c, replace(inputs, speed=50), table)
    assert rpm.active_max_trim == 40 and speed.active_max_trim == 20
    rpm = rl.ignition_step(rpm, 80, c, table)
    speed = rl.ignition_step(speed, 80, c, table)
    assert (rpm.effective_command, rpm.applied_trim, rpm.applied_efficiency) == (120, 40, 600)
    assert rpm.cut_fraction == 500
    assert (speed.effective_command, speed.applied_trim, speed.applied_efficiency) == (100, 20, 800)
    assert speed.cut_fraction == rl.cut_fraction(speed.law_output, 800)
    # A changed speed cannot replace the latched RPM trim with the road trim.
    rpm = rl.step(rpm, replace(rpm_inputs, speed=100), c, table).state
    assert rpm.active_max_trim == 40 and rpm.regulator_kind == rl.RegulatorKind.RPM
    # Selection is a value snapshot, not a later read of a different slot field.
    edited = replace(c, slots=tuple(replace(slot, max_trim_rpm=0, max_trim_speed=0)
                                  for slot in c.slots))
    assert rl.ignition_step(rpm, 80, edited, table).applied_trim == 40


def test_both_mode_trims_use_the_same_floor_and_actual_efficiency(calibration, inputs, table):
    c = replace(calibration, slots=tuple(
        replace(slot, max_trim_rpm=40, max_trim_speed=20) for slot in calibration.slots))
    for speed, selected in [(0, 40), (500, 20)]:
        state = activate(c, replace(inputs, speed=speed), table)
        state = rl.ignition_step(state, 115, c, table)
        assert state.active_max_trim == selected
        assert (state.effective_command, state.applied_trim, state.applied_efficiency) == (120, 5, 950)


def test_each_trim_can_be_disabled_independently(calibration, inputs, table):
    for rpm_trim, speed_trim in [(0, 20), (40, 0)]:
        c = replace(calibration, slots=tuple(
            replace(slot, max_trim_rpm=rpm_trim, max_trim_speed=speed_trim)
            for slot in calibration.slots))
        rpm = rl.ignition_step(activate(c, replace(inputs, speed=0), table), 80, c, table)
        road = rl.ignition_step(activate(c, inputs, table), 80, c, table)
        assert rpm.applied_trim == rpm_trim
        assert road.applied_trim == speed_trim


def test_maps_have_independent_threshold_target_width_and_binary_slots(calibration, inputs, table):
    slots = list(calibration.slots)
    slots[1] = replace(slots[1], launch_rpm_native=400,
                       launch_speed_threshold=100, launch_soft_width_native=100)
    c = replace(calibration, min_speed=0, slots=tuple(slots))
    assert c.to_bytes()[0x34:0x40] == bytes.fromhex("000214147800019000640064")
    first = activate(c, replace(inputs, speed=70, rpm_native=350), table)
    second = activate(c, replace(inputs, active_index=1, speed=70, rpm_native=350), table)
    assert first.regulator_kind == rl.RegulatorKind.SPEED
    assert second.regulator_kind == rl.RegulatorKind.RPM
    assert second.target_rpm_native == 400 and second.law_output == 500


def test_target_is_from_cancel_edge_even_if_other_gates_delay_activation(calibration, inputs, table):
    waiting = rl.step(rl.RuntimeState(), replace(inputs, pedal=0), calibration, table).state
    assert waiting.phase == rl.Phase.IDLE and waiting.cancel_speed_capture == 500
    active = rl.step(waiting, replace(inputs, speed=520), calibration, table).state
    assert active.phase == rl.Phase.ACTIVE and active.target_speed == 500
    assert active.speed_error == 20
    far = rl.step(waiting, replace(inputs, speed=651), calibration, table).state
    assert far.phase == rl.Phase.IDLE and far.abort_reason == rl.AbortReason.SPEED_ABOVE_WINDOW


@pytest.mark.parametrize("offset,error", [(99, -99), (-149, 149)])
def test_offset_bounds_admit_the_actual_negative_initial_error(calibration, inputs, table, offset, error):
    c = replace(calibration, target_speed_offset=offset)
    state = activate(c, inputs, table)
    assert state.phase == rl.Phase.ACTIVE
    assert state.target_speed == inputs.speed+offset and state.speed_error == error


@pytest.mark.parametrize("speed,offset,target", [(1, -149, 0), (65535, 99, 65535)])
def test_speed_target_saturates_without_unsigned_wrap(calibration, inputs, table, speed, offset, target):
    c = replace(calibration, min_speed=0, max_speed=0, target_speed_offset=offset,
                slots=tuple(replace(slot, launch_speed_threshold=1) for slot in calibration.slots))
    state = activate(c, replace(inputs, speed=speed), table)
    assert state.phase == rl.Phase.ACTIVE and state.target_speed == target


def test_invalid_cancel_capture_needs_a_new_press(calibration, inputs, table):
    waiting = activate(calibration, replace(inputs, speed_wire_word=0xFFFF), table)
    waiting = rl.step(waiting, inputs, calibration, table).state
    assert waiting.phase == rl.Phase.IDLE
    assert waiting.abort_reason == rl.AbortReason.CANCEL_CAPTURE_INVALID
    released = rl.step(waiting, replace(inputs, button=rl.BUTTON_RELEASED), calibration, table).state
    assert rl.step(released, inputs, calibration, table).state.phase == rl.Phase.ACTIVE


@pytest.mark.parametrize("hcan,port,wire,expected", [
    (0, 0x80, 0, False), (1, 0, 0, False), (0, 0, 0, False),
    (1, 0x80, 0xFFFF, False), (1, 0x80, 0, True),
    (0x81, 0xFF, 0, True), (0x80, 0x80, 0, False),
])
def test_real_standstill_needs_both_bits_and_a_valid_raw_word(
        calibration, inputs, table, hcan, port, wire, expected):
    i = replace(inputs, speed=0, speed_frame_age=0, hcan1_state=hcan,
                port_input_state=port, speed_wire_word=wire)
    state = activate(calibration, i, table)
    assert (state.phase == rl.Phase.ACTIVE) == expected


def test_age_boundary_and_running_rpm_input_failure(calibration, inputs, table):
    i = replace(inputs, speed=0, speed_wire_word=0,
                speed_frame_age=calibration.speed_frame_age_limit)
    state = activate(calibration, i, table)
    assert state.phase == rl.Phase.ACTIVE
    state = rl.step(state, replace(i, port_input_state=0), calibration, table).state
    assert state.phase == rl.Phase.COOLDOWN
    assert state.abort_reason == rl.AbortReason.SPEED_SOURCE_NOT_READY


def test_corrupt_efficiency_blocks_both_activation_and_a_running_hold(calibration, inputs, table):
    invalid = rl.EfficiencyTable((0,)*41)
    state = activate(calibration, inputs, invalid)
    assert state.phase == rl.Phase.IDLE and state.abort_reason == rl.AbortReason.CONFIG_INVALID
    active = activate(calibration, inputs, table)
    aborted = rl.step(active, inputs, calibration, invalid).state
    assert aborted.phase == rl.Phase.COOLDOWN and aborted.cut_fraction == 0


def test_release_has_priority_over_other_input_failures(calibration, inputs, table):
    active = activate(calibration, inputs, table)
    state = rl.step(active, replace(inputs, button=rl.BUTTON_RELEASED,
                                   port_input_state=0, pedal=0), calibration, table).state
    assert state.abort_reason == rl.AbortReason.BUTTON_RELEASED


def test_observe_computes_the_law_but_never_arms_cut(calibration, inputs, table):
    c = replace(calibration, mode=rl.Mode.OBSERVE)
    i = replace(inputs, speed=0, rpm_native=300)
    state = activate(c, i, table)
    state = rl.ignition_step(state, 100, c, table)
    assert state.law_output == 0
    assert state.effective_command == 100 and not state.actuation_ready
    assert state.cut_fraction == 0 and not state.flags & rl.Flag.HOLD


@pytest.mark.parametrize("changes,reason", [
    ({"hcan1_state": 0}, rl.AbortReason.SPEED_SOURCE_NOT_READY),
    ({"port_input_state": 0}, rl.AbortReason.SPEED_SOURCE_NOT_READY),
    ({"speed_wire_word": 0xFFFF, "speed": 0}, rl.AbortReason.SPEED_VALUE_INVALID),
    ({"speed_frame_age": 11}, rl.AbortReason.SPEED_FRAME_STALE),
    ({"speed_frame_age": 255}, rl.AbortReason.SPEED_FRAME_STALE),
    ({"rpm_native": 32768}, rl.AbortReason.RPM_INPUT_INVALID),
    ({"rpm_native": 159}, rl.AbortReason.RPM_LOW),
    ({"pedal": 0}, rl.AbortReason.PEDAL_LOW),
    ({"active_index": 1}, rl.AbortReason.MAP_CHANGED),
    ({"button": rl.BUTTON_SET}, rl.AbortReason.MAP_REQUEST),
    ({"button": rl.BUTTON_RELEASED}, rl.AbortReason.BUTTON_RELEASED),
    ({"button": 0}, rl.AbortReason.BUTTON_INVALID),
])
def test_active_abort_releases_q_without_slew(calibration, inputs, table, changes, reason):
    state = activate(calibration, inputs, table)
    state = rl.ignition_step(state, 100, calibration, table)
    result = rl.step(state, replace(inputs, **changes), calibration, table).state
    assert result.phase == rl.Phase.COOLDOWN and result.abort_reason == reason
    assert result.cut_fraction == 0 and not result.actuation_ready


def test_rpm_full_cut_is_immediate_after_the_command_is_applied(calibration, inputs, table):
    i = replace(inputs, speed=0, rpm_native=300)
    state = activate(replace(calibration, u_rate_limit=1), i, table)
    assert state.law_output == 0 and state.cut_fraction == 0
    state = rl.ignition_step(state, 100, calibration, table)
    assert state.cut_fraction == 1000
    assert state.applied_efficiency == 800
    assert rl.actuation(rl.RegulatorKind.RPM, 500, 20, table, True) == 500


def test_speed_hold_has_no_replacement_rpm_ceiling(calibration, inputs, table):
    state = activate(calibration, inputs, table)
    normal = rl.step(state, inputs, calibration, table).state
    high = rl.step(state, replace(inputs, rpm_native=1000), calibration, table).state
    normal = rl.ignition_step(normal, 100, calibration, table)
    high = rl.ignition_step(high, 100, calibration, table)
    assert normal.law_output == high.law_output
    assert normal.cut_fraction == high.cut_fraction
    assert high.target_rpm_native == 0 and int(high.flags) & 0xA000 == 0


def test_clipping_republishes_efficiency_at_the_same_fixed_trim(calibration, inputs, table):
    state = activate(calibration, inputs, table)
    for _ in range(9):
        state = rl.step(state, inputs, calibration, table).state
    full = rl.ignition_step(state, 80, calibration, table)
    clipped = rl.ignition_step(full, 115, calibration, table)
    assert (full.effective_command, full.applied_trim, full.applied_efficiency) == (100, 20, 800)
    assert (clipped.effective_command, clipped.applied_trim, clipped.applied_efficiency) == (120, 5, 950)
    assert full.law_output == clipped.law_output
    assert full.cut_fraction == 1000-1000*full.law_output//800
    assert clipped.cut_fraction == 1000-1000*clipped.law_output//950
    late = rl.ignition_step(clipped, 130, calibration, table)
    assert (late.effective_command, late.applied_trim) == (130, 0)
    fallback = rl.ignition_step(full, 80, calibration, table, apc_fallback=True)
    assert (fallback.effective_command, fallback.cut_fraction, fallback.actuation_ready) == (80, 0, False)


def test_road_replay_uses_selected_ki_and_signed_integrator(calibration, inputs, table):
    slots = list(calibration.slots)
    slots[2] = replace(slots[2], integral_gain=4)
    c = replace(calibration, slots=tuple(slots))
    i = replace(inputs, active_index=2)
    state = activate(c, i, table)
    state = rl.step(state, replace(i, speed=510), c, table).state
    assert state.integrator == -40
    assert state.torque_command == 247  # 250 + arithmetic(-40 >> 4)
    assert state.torque_fraction == 900
    assert rl.update_integrator(-1, 0, 10, c, 4) == -1
    assert rl.update_integrator(16000, 1000, -10, c, 4) == 8000


def test_timeout_and_rearm_use_exact_tick_boundaries(calibration, inputs, table):
    c = replace(calibration, run_timeout_ticks=2)
    state = activate(c, inputs, table)
    state = rl.step(state, inputs, c, table).state
    assert state.run_ticks == 1
    state = rl.step(state, inputs, c, table).state
    assert state.abort_reason == rl.AbortReason.TIMEOUT and state.phase == rl.Phase.COOLDOWN
    released = replace(inputs, button=rl.BUTTON_RELEASED)
    state = rl.step(state, released, c, table).state
    state = rl.step(state, replace(released, button=0), c, table).state
    assert state.rearm_ticks == 0
    for _ in range(3):
        state = rl.step(state, released, c, table).state
    assert state.phase == rl.Phase.IDLE and state.regulator_kind == rl.RegulatorKind.NONE
    assert state.active_max_trim == 0


def test_corrupt_state_restores_map1_and_requests_only_extension_counter_reset(calibration, inputs, table):
    active = activate(calibration, inputs, table)
    for changes in [{"phase": 9}, {"regulator_kind": 0}, {"active_index_snapshot": 5},
                    {"flags": 1 << 13}, {"cut_fraction": 1001}, {"actuation_ready": 2},
                    {"applied_trim": 41}, {"active_max_trim": 41}, {"control_error": 99}]:
        result = rl.step(replace(active, **changes), inputs, calibration, table)
        assert result.limiter_action == rl.LimiterAction.RESTORE_MAP_1
        assert result.reset_event_instrumentation
        assert result.state.abort_reason == rl.AbortReason.STATE_CORRUPT
        assert result.state.cut_fraction == 0
        assert result.state.active_max_trim == 0


def test_state_records_have_exact_reused_offsets(calibration, inputs, table):
    state = activate(calibration, replace(inputs, speed=0), table)
    state = rl.ignition_step(state, 115, calibration, table)
    spark = rl.SparkCutState(quiet_events=7, cut_count=9, accumulators=(1,2,3,4,5,6),
                             consumed_q_sum=0x12345678, eligible_event_counter=0xABCD)
    base, ext = rl.encode_state(state, spark)
    assert (len(base), len(ext)) == (44, 32)
    assert base[0x14:0x16] == bytes.fromhex("012c")
    assert base[0x18:0x1A] == bytes.fromhex("ffec")
    assert base[0x1C:0x20] == bytes.fromhex("07091400")
    assert rl.ENGINE_EXTRA_CLEAR_OFFSETS == (0x1E,)
    assert ext[0x10:0x14] == bytes.fromhex("12345678")
    assert ext[0x18:0x1A] == bytes.fromhex("abcd")
    assert rl.decode_state(base, ext) == (state, spark)
    damaged = bytearray(ext)
    damaged[0x1E] ^= 1
    with pytest.raises(ValueError):
        rl.decode_state(base, damaged)
    damaged_base = bytearray(base)
    damaged_base[0x1F] = 1
    with pytest.raises(ValueError):
        rl.decode_state(damaged_base, ext)


@pytest.mark.parametrize("block,size", [("base", 44), ("extension", 32)])
def test_named_state_fields_own_every_byte_exactly_once(block, size):
    counts = [0]*size
    names = []
    for name, offset, fmt in rl.STATE_FIELDS[block]:
        width = struct.calcsize(">"+fmt)
        assert 0 <= offset < offset+width <= size
        assert offset % width == 0
        names.append(name)
        for byte in range(offset, offset+width):
            counts[byte] += 1
    assert len(names) == len(set(names))
    assert counts == [1]*size
    assert rl.BASE_RESERVED_FIELDS == (("reserved_1f", 0x1F, "B"),)


def test_telemetry_views_have_named_scalar_sources():
    base = {name: (offset, fmt) for name, offset, fmt in rl.BASE_COUNTER_FIELDS}
    ext = {name: (offset, fmt) for name, offset, fmt in rl.EXTENSION_VIEW_FIELDS}
    assert base == {"quiet_events": (0x1C, "B"), "cut_counter": (0x1D, "B")}
    assert ext == {
        "wire_efficiency": (0x0E, "H"), "consumed_q_sum": (0x10, "I"),
        "eligible_event_counter": (0x18, "H"),
        "wire_mode_trim": (0x1E, "B"), "wire_status": (0x1F, "B"),
    }


def test_codec_uses_view_maps_for_both_directions(calibration, inputs, table, monkeypatch):
    runtime = rl.ignition_step(activate(calibration, replace(inputs, speed=0), table),
                               115, calibration, table)
    spark = rl.SparkCutState(quiet_events=7, cut_count=9,
                             consumed_q_sum=0x12345678, eligible_event_counter=0xABCD)
    # Exchange two equal-width views to detect any literal-offset codec path.
    moved = tuple((name, 0x1F if name == "wire_mode_trim" else
                   0x1E if name == "wire_status" else offset, fmt)
                  for name, offset, fmt in rl.EXTENSION_VIEW_FIELDS)
    monkeypatch.setattr(rl, "EXTENSION_VIEW_FIELDS", moved)
    base, extension = rl.encode_state(runtime, spark)
    assert runtime.wire_mode_trim != runtime.wire_status
    assert extension[0x1F] == runtime.wire_mode_trim
    assert extension[0x1E] == runtime.wire_status
    assert rl.decode_state(base, extension) == (runtime, spark)


@pytest.mark.parametrize("changes", [
    {"quiet_events": 1.5}, {"cut_count": 1.5}, {"consumed_q_sum": 1.5},
    {"eligible_event_counter": 1.5}, {"accumulators": (1.5, 0, 0, 0, 0, 0)},
])
def test_field_maps_do_not_coerce_non_integer_event_state(changes):
    with pytest.raises(struct.error):
        rl.encode_state(rl.RuntimeState(), replace(rl.SparkCutState(), **changes))


def test_no_current_fuel_control_api():
    for cls in (rl.Slot, rl.Calibration, rl.Inputs, rl.RuntimeState):
        assert not any("fuel" in field.name or "ceiling" in field.name for field in fields(cls))
    assert not hasattr(rl.Flag, "FUEL_CUT") and not hasattr(rl.Flag, "CEILING")
    assert not hasattr(rl, "apply_fuel_cut_request")


def test_fractional_cut_balance_and_integral_for_every_q():
    runtime = rl.RuntimeState(phase=rl.Phase.ACTIVE, active_mode_snapshot=rl.Mode.HOLD)
    for q in range(1001):
        for start in range(6):
            cut = rl.SparkCutState(accumulators=rl.SPARK_CYLINDER_OFFSETS)
            counts = [0]*6
            for n in range(36):
                cylinder = (start+n) % 6
                result = rl.spark_event(replace(runtime, cut_fraction=q), cut,
                                        rl.SparkEvent(cylinder=cylinder+1))
                cut = result.state
                counts[cylinder] += result.cut_requested
            assert abs(sum(counts)-36*q/1000) <= 1
            assert max(counts)-min(counts) <= 1
            assert cut.consumed_q_sum == 36*q
            assert cut.eligible_event_counter == 36


def test_event_eligibility_and_instrumentation_wrap():
    runtime = rl.RuntimeState(phase=rl.Phase.ACTIVE, active_mode_snapshot=rl.Mode.HOLD, cut_fraction=1000)
    cut = rl.SparkCutState(accumulators=rl.SPARK_CYLINDER_OFFSETS,
                           consumed_q_sum=0xFFFFFFFE, eligible_event_counter=65535, cut_count=255)
    no = rl.spark_event(runtime, cut, rl.SparkEvent(eligible=False))
    assert not no.cut_requested and no.state.consumed_q_sum == cut.consumed_q_sum
    result = rl.spark_event(runtime, cut, rl.SparkEvent())
    assert result.cut_requested and result.state.cut_count == 0
    assert result.state.consumed_q_sum == 998 and result.state.eligible_event_counter == 0
    quiet = rl.spark_event(rl.RuntimeState(), result.state, rl.SparkEvent())
    assert not quiet.cut_requested and quiet.state.accumulators == rl.SPARK_CYLINDER_OFFSETS


def test_misfire_marker_release_preserves_stock_latch():
    runtime = rl.RuntimeState(phase=rl.Phase.ACTIVE, active_mode_snapshot=rl.Mode.HOLD)
    result = rl.spark_event(runtime, rl.SparkCutState(), rl.SparkEvent())
    assert result.misfire_latch == 1
    cut = result.state
    for _ in range(13):
        result = rl.spark_event(rl.RuntimeState(), cut, rl.SparkEvent(misfire_latch=1))
        cut = result.state
        assert result.misfire_latch == 1
    assert rl.spark_event(rl.RuntimeState(), cut, rl.SparkEvent(misfire_latch=1)).misfire_latch == 0
    assert rl.spark_event(runtime, cut, rl.SparkEvent(misfire_latch=50)).misfire_latch == 50


def test_dashboard_feedback_keeps_map_feedback_priority():
    active = rl.RuntimeState(phase=rl.Phase.ACTIVE)
    assert rl.apply_dashboard_feedback(active, 0xB5) == 0xC5
    assert rl.apply_dashboard_feedback(active, 0xB5, map_feedback_active=True) == 0xB5
    assert rl.apply_dashboard_feedback(rl.RuntimeState(phase=99), 0xB5) == 0xB5
