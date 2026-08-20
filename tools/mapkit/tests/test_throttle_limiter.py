from dataclasses import replace

from tools.mapkit.rom import load
from tools.mapkit.throttle_limiter import (
    ThrottleLimiterCalibration,
    ThrottleLimiterInput,
    ThrottleLimiterState,
    step_throttle_limiter,
)


def stock_calibration():
    return ThrottleLimiterCalibration.from_rom(load("JK08A").data)


def state(**changes):
    initial = ThrottleLimiterState(
        speed_filtered=9600,
        dynamic_threshold=9600,
        blended_threshold=9600,
        output=0,
        ramp=10000,
        recovery=0x7FFF,
    )
    return replace(initial, **changes)


def inputs(**changes):
    initial = ThrottleLimiterInput(
        speed_raw=2400,
        app_request=20000,
        baseline_request=-0x8000,
    )
    return replace(initial, **changes)


def test_stock_calibration_is_bound_to_rom():
    calibration = stock_calibration()
    assert calibration == ThrottleLimiterCalibration(
        blend_gain=76,
        normal_ramp_rate=200,
        fast_ramp_rate=1500,
        final_rate=2000,
        base_threshold=9600,
        mode_cap=0xFFFF,
        threshold_down_rate=0,
        alternate_threshold=0xFFFF,
        threshold_up_rate=0,
        recovery_rate_high_context=30,
        recovery_rate_low_context=50,
        auxiliary_duration=182,
        coolant_set_threshold=255,
        coolant_hysteresis=16,
        ramp_mode_load=100,
        ramp_transition=0,
        auxiliary_requests=(1000, 1300, 1300, 1000, 1000),
    )


def test_disabled_branch_changes_only_output():
    calibration = replace(stock_calibration(), base_threshold=0xFFFF)
    before = state(
        speed_filtered=1234,
        dynamic_threshold=321,
        blended_threshold=456,
        ramp=789,
        auxiliary_request=2222,
        auxiliary_duration=3333,
    )
    after = step_throttle_limiter(calibration, before, inputs())
    assert after == replace(before, output=0x7FFF)


def test_blend_uses_entry_filter_while_rates_use_new_filter():
    after = step_throttle_limiter(
        stock_calibration(),
        state(speed_filtered=9583),
        inputs(speed_raw=2400),
    )
    assert after.speed_filtered == 9587
    assert after.blended_threshold == 9584
    assert after.ramp == 9995
    assert after.output == 9948


def test_stable_speed_has_exact_13_count_deadband():
    calibration = stock_calibration()
    at_13 = step_throttle_limiter(
        calibration,
        state(speed_filtered=9587),
        inputs(speed_raw=2397),
    )
    at_14 = step_throttle_limiter(
        calibration,
        state(speed_filtered=9586),
        inputs(speed_raw=2397),
    )
    assert (at_13.blended_threshold, at_13.ramp, at_13.output) == (
        9587,
        10000,
        10000,
    )
    assert (at_14.blended_threshold, at_14.ramp, at_14.output) == (
        9587,
        10001,
        10016,
    )


def test_one_count_above_threshold_reduces_both_terms():
    after = step_throttle_limiter(
        stock_calibration(),
        state(speed_filtered=9601),
        inputs(speed_raw=2401),
    )
    assert after.speed_filtered == 9601
    assert after.blended_threshold == 9600
    assert after.ramp == 9998
    assert after.output == 9982


def test_fast_mode_sequence_matches_exact_rom_execution():
    calibration = stock_calibration()
    before = state(
        speed_filtered=9856,
        output=0x7FFF,
        ramp=10000,
    )
    conditions = inputs(speed_raw=2464)

    first = step_throttle_limiter(calibration, before, conditions)
    assert (first.output, first.ramp, first.ramp_mode, first.ramp_latched) == (
        9703,
        10000,
        100,
        False,
    )

    second = step_throttle_limiter(calibration, first, conditions)
    assert (second.output, second.ramp, second.ramp_mode, second.ramp_latched) == (
        9480,
        9777,
        100,
        False,
    )


def test_coolant_hysteresis_and_dynamic_threshold_branches():
    calibration = replace(
        stock_calibration(),
        alternate_threshold=9000,
        threshold_down_rate=16,
        threshold_up_rate=5,
    )
    current = state(dynamic_threshold=9500)

    alternate = step_throttle_limiter(
        calibration,
        current,
        inputs(raw_coolant=255, dynamic_threshold_enabled=True),
    )
    assert alternate.coolant_latched
    assert alternate.dynamic_threshold == 9484

    retained = step_throttle_limiter(
        calibration,
        alternate,
        inputs(raw_coolant=239, dynamic_threshold_enabled=True),
    )
    assert retained.coolant_latched

    cleared = step_throttle_limiter(
        calibration,
        retained,
        inputs(raw_coolant=238, dynamic_threshold_enabled=True),
    )
    assert not cleared.coolant_latched
    assert cleared.dynamic_threshold == 9473


def test_recovery_rollback_tracking_auxiliary_and_forced_neutral():
    calibration = stock_calibration()
    conditions = inputs(speed_raw=2464)

    rollback = step_throttle_limiter(
        calibration,
        state(speed_filtered=9856, recovery=9000),
        conditions,
    )
    assert (rollback.recovery, rollback.output, rollback.ramp) == (9050, 9050, 10000)

    tracking = step_throttle_limiter(
        calibration,
        state(speed_filtered=9856, recovery=12000),
        replace(conditions, context_next=1),
    )
    assert (tracking.recovery, tracking.output) == (9673, 9673)
    assert (tracking.auxiliary_request, tracking.auxiliary_duration) == (1300, 182)

    neutral = step_throttle_limiter(
        calibration,
        state(speed_filtered=9856, recovery=12000),
        replace(conditions, force_neutral=True, shared_request=1234),
    )
    assert (neutral.output, neutral.ramp) == (0x7FFF, 1234)
