import dataclasses
from pathlib import Path
import re
import unittest

from patches import rolling_launch as rl


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tools" / "sh-elf-run" / "rolling_launch_harness.c"
CONTROLLER_ROW = re.compile(r'\{"(ctrl-[a-z-]+)",([-0-9a-fx, ]+)\}')


class RollingLaunchTest(unittest.TestCase):
    def setUp(self):
        self.calibration = rl.Calibration(
            mode=rl.Mode.HOLD,
            enable_mask=0x01,
            coolant_min=80,
            coolant_max=220,
            run_timeout_ticks=4,
            rearm_ticks=3,
        )
        self.inputs = rl.Inputs(
            active_index=0,
            button=rl.BUTTON_CANCEL,
            speed=500,
            rpm_native=300,
            pedal=2000,
            coolant=150,
        )

    def activate(self, calibration=None, inputs=None):
        return rl.step(
            rl.RuntimeState(),
            inputs or self.inputs,
            calibration or self.calibration,
        ).state

    def test_default_configuration_is_fail_closed_and_round_trips(self):
        calibration = rl.Calibration()
        self.assertTrue(calibration.is_valid())
        self.assertEqual(calibration.enable_mask, 0)
        encoded = calibration.to_bytes()
        self.assertEqual(len(encoded), rl.CONFIG_SIZE)
        self.assertEqual(rl.Calibration.from_bytes(encoded), calibration)

    def test_configuration_rejects_each_integrity_and_range_failure(self):
        invalid = (
            {"magic": 0},
            {"schema_version": 3},
            {"mode": 2},
            {"enable_mask": 0x20},
            {"options": 1},
            {"coolant_min": 221, "coolant_max": 220},
            {"min_speed": -1},
            {"max_speed": 0x10000},
            {"min_speed": 600, "max_speed": 599},
            {"min_rpm_native": 0},
            {"min_pedal": 0x10000},
            {"target_speed_offset": -150},
            {"target_speed_offset": 100},
            {"window_width": 0},
            {"window_width": 0x100},
            {"window_top": 0x100},
            {"u_rate_limit": 0},
            {"u_rate_limit": 1001},
            {"integral_gain": -1},
            {"integral_gain": 0x8000},
            {"integrator_limit": 1001},
            {"abort_above": 0},
            {"abort_below": 0},
            {"rpm_ceiling_offset_native": 0},
            {"run_timeout_ticks": 0},
            {"run_timeout_ticks": 0x8000},
            {"rearm_ticks": 0},
            {"rearm_ticks": 0x8000},
            {"speed_frame_age_limit": 0},
            {"speed_frame_age_limit": 255},
            {"reserved": 1},
            {"magic_inverse": 0},
            {"end_marker": 0},
        )
        for changes in invalid:
            with self.subTest(changes=changes):
                candidate = dataclasses.replace(self.calibration, **changes)
                self.assertFalse(candidate.is_valid())

    def test_configuration_accepts_every_upper_bound(self):
        candidate = dataclasses.replace(
            self.calibration,
            min_speed=0,
            max_speed=0,
            target_speed_offset=99,
            window_width=0xFF,
            window_top=0xFF,
            u_rate_limit=rl.U_ONE,
            integral_gain=0x7FFF,
            integrator_limit=rl.U_ONE,
            rpm_ceiling_offset_native=0xFFFF,
            run_timeout_ticks=0x7FFF,
            rearm_ticks=0x7FFF,
            speed_frame_age_limit=rl.SPEED_FRAME_AGE_LIMIT_MAX,
        )
        self.assertTrue(candidate.is_valid())
        self.assertTrue(
            dataclasses.replace(candidate, target_speed_offset=-149).is_valid()
        )

    def test_gate_flags_report_all_conditions_not_only_first_failure(self):
        inputs = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED, speed=100
        )
        flags, reason = rl.evaluate_gates(inputs, self.calibration)
        self.assertEqual(reason, rl.AbortReason.BUTTON_INVALID)
        self.assertTrue(flags & rl.Flag.CONFIG_VALID)
        self.assertTrue(flags & rl.Flag.MAP_ENABLED)
        self.assertTrue(flags & rl.Flag.SPEED_FRAME_OK)
        self.assertTrue(flags & rl.Flag.RPM_OK)
        self.assertTrue(flags & rl.Flag.COOLANT_OK)
        self.assertFalse(flags & rl.Flag.BUTTON_HELD)
        self.assertFalse(flags & rl.Flag.SPEED_OK)

    def test_the_speed_frame_age_gates_activation_and_aborts_a_run(self):
        limit = self.calibration.speed_frame_age_limit
        exact = dataclasses.replace(self.inputs, speed_frame_age=limit)
        self.assertEqual(self.activate(inputs=exact).phase, rl.Phase.ACTIVE)
        # A stale frame takes priority over a speed outside the range.
        stale = dataclasses.replace(
            self.inputs, speed_frame_age=limit + 1, speed=100
        )
        refused = self.activate(inputs=stale)
        self.assertEqual(refused.phase, rl.Phase.IDLE)
        self.assertEqual(
            refused.abort_reason, rl.AbortReason.SPEED_FRAME_STALE
        )
        self.assertFalse(refused.flags & rl.Flag.SPEED_FRAME_OK)

        active = self.activate()
        aborted = rl.step(
            active,
            dataclasses.replace(self.inputs, speed_frame_age=limit + 1),
            self.calibration,
        ).state
        self.assertEqual(aborted.phase, rl.Phase.COOLDOWN)
        self.assertEqual(
            aborted.abort_reason, rl.AbortReason.SPEED_FRAME_STALE
        )

    def test_activation_speed_range_is_inclusive_and_zero_disables_a_side(self):
        for speed, reason in (
            (199, rl.AbortReason.SPEED_LOW),
            (200, rl.AbortReason.NONE),
            (1200, rl.AbortReason.NONE),
            (1201, rl.AbortReason.SPEED_HIGH),
        ):
            with self.subTest(speed=speed):
                inputs = dataclasses.replace(self.inputs, speed=speed)
                state = self.activate(inputs=inputs)
                self.assertEqual(state.abort_reason, reason)
        open_low = dataclasses.replace(self.calibration, min_speed=0)
        self.assertEqual(
            self.activate(
                open_low, dataclasses.replace(self.inputs, speed=0)
            ).phase,
            rl.Phase.ACTIVE,
        )
        open_high = dataclasses.replace(self.calibration, max_speed=0)
        self.assertEqual(
            self.activate(
                open_high, dataclasses.replace(self.inputs, speed=0xFFFF)
            ).phase,
            rl.Phase.ACTIVE,
        )

    def test_dashboard_feedback_reports_attempt_active_and_cooldown(self):
        failed = rl.RuntimeState(
            abort_reason=rl.AbortReason.RPM_LOW,
            flags=rl.Flag.BUTTON_HELD,
        )
        active = rl.RuntimeState(phase=rl.Phase.ACTIVE)
        cooldown = rl.RuntimeState(phase=rl.Phase.COOLDOWN)

        self.assertEqual(rl.apply_dashboard_feedback(failed, 0xB5), 0xD5)
        self.assertEqual(rl.apply_dashboard_feedback(active, 0xB5), 0xC5)
        self.assertEqual(
            rl.apply_dashboard_feedback(cooldown, 0xB5), 0x85
        )

    def test_dashboard_feedback_preserves_idle_corrupt_and_map_pulse(self):
        normal = rl.RuntimeState(
            abort_reason=rl.AbortReason.BUTTON_INVALID,
        )
        corrupt = dataclasses.replace(normal, phase=9)
        active = rl.RuntimeState(phase=rl.Phase.ACTIVE)
        failed = rl.RuntimeState(
            abort_reason=rl.AbortReason.RPM_LOW,
            flags=rl.Flag.BUTTON_HELD,
        )

        self.assertEqual(rl.apply_dashboard_feedback(normal, 0xB5), 0xB5)
        self.assertEqual(rl.apply_dashboard_feedback(corrupt, 0xB5), 0xB5)
        # The map ON value differs from the failed-attempt value and the map
        # OFF value differs from the ACTIVE value, so each case shows which
        # source owns the frame.
        self.assertEqual(
            rl.apply_dashboard_feedback(
                failed, 0xC5, map_feedback_active=True
            ),
            0xC5,
        )
        self.assertEqual(
            rl.apply_dashboard_feedback(
                active, 0x85, map_feedback_active=True
            ),
            0x85,
        )

        with self.assertRaisesRegex(ValueError, "serialized ASCD status"):
            rl.apply_dashboard_feedback(active, 0x100)

    def test_activation_captures_target_rpm_and_a_fresh_controller(self):
        stale = rl.RuntimeState(
            captured_rpm_native=0x5A5A,
            target_speed=0x5A5A,
            torque_fraction=5,
            integrator=0x4000,
            fuel_cut_request=0x3F,
        )
        result = rl.step(stale, self.inputs, self.calibration)
        state = result.state
        self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)
        self.assertEqual(state.phase, rl.Phase.ACTIVE)
        self.assertEqual(state.active_mode_snapshot, rl.Mode.HOLD)
        self.assertEqual(
            (state.captured_rpm_native, state.target_speed), (300, 500)
        )
        # u_p = 20 * 1000 // 40 and u falls from full torque by the rate.
        self.assertEqual(
            (state.speed_error, state.integrator, state.torque_command,
             state.torque_fraction, state.fuel_cut_request),
            (0, 0, 500, 950, 0),
        )
        self.assertEqual(
            state.flags, rl.Flag((1 << 12) - 1) | rl.Flag.ACTIVE | rl.Flag.HOLD
        )

    def test_the_captured_target_saturates_at_both_ends(self):
        floor = dataclasses.replace(
            self.calibration, min_speed=0, target_speed_offset=-50
        )
        state = self.activate(floor, dataclasses.replace(self.inputs, speed=30))
        self.assertEqual((state.target_speed, state.speed_error), (0, 30))
        ceiling = dataclasses.replace(
            self.calibration, max_speed=0, target_speed_offset=60
        )
        state = self.activate(
            ceiling, dataclasses.replace(self.inputs, speed=0xFFF0)
        )
        self.assertEqual((state.target_speed, state.speed_error), (0xFFFF, -15))

    def test_proportional_fraction_spans_the_window(self):
        for error, expected in (
            (20, 0), (25, 0), (19, 25), (0, 500), (-19, 975), (-20, 1000),
            (-30, 1000),
        ):
            with self.subTest(error=error):
                self.assertEqual(
                    rl.proportional_fraction(error, self.calibration),
                    expected,
                )

    def test_the_integrator_freezes_on_a_saturated_sum_and_stays_bounded(self):
        gain = dataclasses.replace(self.calibration, integral_gain=2)
        self.assertEqual(rl.update_integrator(0, 0, 30, gain), 0)
        self.assertEqual(rl.update_integrator(0, 1000, -30, gain), 0)
        self.assertEqual(rl.update_integrator(0, 500, 5, gain), -10)
        self.assertEqual(rl.update_integrator(0, 500, -5, gain), 10)
        bounded = dataclasses.replace(gain, integrator_limit=1)
        self.assertEqual(rl.update_integrator(15, 500, -5, bounded), 16)
        self.assertEqual(rl.update_integrator(-15, 500, 5, bounded), -16)

    def test_harness_controller_table_matches_the_model(self):
        rows = CONTROLLER_ROW.findall(HARNESS.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 18)
        for name, values in rows:
            (mode, target, fraction, integrator, speed, rpm, captured, gain,
             limit, fuel, error, next_integrator, command, next_fraction,
             request, flags) = (int(item, 0) for item in values.split(","))
            with self.subTest(case=name):
                calibration = dataclasses.replace(
                    self.calibration,
                    mode=mode,
                    integral_gain=gain,
                    integrator_limit=limit,
                )
                state = rl.RuntimeState(
                    phase=rl.Phase.ACTIVE,
                    active_mode_snapshot=mode,
                    captured_rpm_native=captured,
                    target_speed=target,
                    torque_fraction=fraction,
                    integrator=integrator,
                )
                inputs = dataclasses.replace(
                    self.inputs,
                    speed=speed,
                    rpm_native=rpm,
                    fuel_cut_status=fuel,
                )
                result = rl.step(state, inputs, calibration).state
                self.assertEqual(result.phase, rl.Phase.ACTIVE)
                self.assertEqual(
                    (result.speed_error, result.integrator,
                     result.torque_command, result.torque_fraction,
                     result.fuel_cut_request, int(result.flags)),
                    (error, next_integrator, command, next_fraction,
                     request, flags),
                )

    def test_observe_mode_never_requests_a_fuel_cut(self):
        calibration = dataclasses.replace(
            self.calibration, mode=rl.Mode.OBSERVE
        )
        state = self.activate(calibration)
        self.assertEqual(state.phase, rl.Phase.ACTIVE)
        self.assertFalse(state.flags & rl.Flag.HOLD)
        high = dataclasses.replace(self.inputs, rpm_native=0xFFFF)
        held = rl.step(state, high, calibration).state
        self.assertEqual(held.phase, rl.Phase.ACTIVE)
        self.assertEqual(held.fuel_cut_request, 0)
        self.assertFalse(held.flags & rl.Flag.CEILING)

    def test_the_ceiling_request_holds_strictly_above_the_ceiling(self):
        state = self.activate()
        for rpm, held in (
            (379, False), (380, False), (381, True), (300, False),
            (400, True),
        ):
            with self.subTest(rpm=rpm):
                inputs = dataclasses.replace(self.inputs, rpm_native=rpm)
                state = rl.step(state, inputs, self.calibration).state
                self.assertEqual(state.phase, rl.Phase.ACTIVE)
                self.assertEqual(state.fuel_cut_request, 0x3F if held else 0)
                self.assertEqual(bool(state.flags & rl.Flag.CEILING), held)
                self.assertEqual(bool(state.flags & rl.Flag.FUEL_CUT), held)
            state = dataclasses.replace(state, run_ticks=0)

        released = dataclasses.replace(self.inputs, button=rl.BUTTON_RELEASED)
        state = rl.step(state, released, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(state.fuel_cut_request, 0)
        self.assertFalse(state.flags & rl.ACTIVE_OUTPUT_FLAGS)

    def test_every_tick_clears_a_stale_request(self):
        cooldown = rl.RuntimeState(
            phase=rl.Phase.COOLDOWN,
            abort_reason=rl.AbortReason.BUTTON_RELEASED,
            active_mode_snapshot=rl.Mode.HOLD,
            fuel_cut_request=0x3F,
        )
        state = rl.step(cooldown, self.inputs, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(state.fuel_cut_request, 0)

    def test_the_wrapper_ors_only_a_well_formed_request(self):
        for stock, request, expected in (
            (0x00, 0x0000, 0x00),
            (0x05, 0x0000, 0x05),
            (0x00, 0x003F, 0x3F),
            (0x00, 0x0015, 0x15),
            (0x0A, 0x0015, 0x1F),
            (0x3F, 0x0001, 0x3F),
            (0x00, 0x0040, 0x00),
            (0x05, 0x007F, 0x05),
            (0x05, 0x0100, 0x05),
            (0x05, 0xFFFF, 0x05),
        ):
            with self.subTest(stock=stock, request=request):
                self.assertEqual(
                    rl.apply_fuel_cut_request(stock, request), expected
                )
        with self.assertRaisesRegex(ValueError, "stock cylinder mask"):
            rl.apply_fuel_cut_request(0x100, 0)
        with self.assertRaisesRegex(ValueError, "fuel-cut request"):
            rl.apply_fuel_cut_request(0, 0x10000)

    def test_the_fuel_cut_flag_follows_the_active_cut_bit_alone(self):
        for status, expected in (
            (rl.FUEL_CUT_ACTIVE_MASK, True),
            (0xFF, True),
            (0xFF ^ rl.FUEL_CUT_ACTIVE_MASK, False),
            (0x00, False),
        ):
            with self.subTest(status=status):
                inputs = dataclasses.replace(
                    self.inputs, fuel_cut_status=status
                )
                state = self.activate(inputs=inputs)
                self.assertEqual(state.phase, rl.Phase.ACTIVE)
                self.assertEqual(bool(state.flags & rl.Flag.FUEL_CUT), expected)

    def test_active_aborts_cover_every_reason(self):
        active = self.activate()
        cases = (
            ({"button": rl.BUTTON_SET}, None, rl.AbortReason.MAP_REQUEST),
            ({"button": rl.BUTTON_RELEASED}, None,
             rl.AbortReason.BUTTON_RELEASED),
            ({"button": 0x04}, None, rl.AbortReason.BUTTON_INVALID),
            ({"active_index": 1}, None, rl.AbortReason.MAP_CHANGED),
            ({}, {"mode": rl.Mode.OBSERVE}, rl.AbortReason.MODE_CHANGED),
            ({}, {"magic": 0}, rl.AbortReason.CONFIG_INVALID),
            ({"speed": 651}, None, rl.AbortReason.SPEED_ABOVE_WINDOW),
            ({"speed": 399}, None, rl.AbortReason.SPEED_BELOW_WINDOW),
        )
        for inputs, calibration, reason in cases:
            with self.subTest(reason=reason):
                result = rl.step(
                    active,
                    dataclasses.replace(self.inputs, **inputs),
                    dataclasses.replace(self.calibration, **(calibration or {})),
                )
                self.assertEqual(result.state.phase, rl.Phase.COOLDOWN)
                self.assertEqual(result.state.abort_reason, reason)
                self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)
                self.assertFalse(result.state.flags & rl.ACTIVE_OUTPUT_FLAGS)

        for speed in (650, 400):
            with self.subTest(speed=speed):
                inputs = dataclasses.replace(self.inputs, speed=speed)
                self.assertEqual(
                    rl.step(active, inputs, self.calibration).state.phase,
                    rl.Phase.ACTIVE,
                )

        state = active
        for _ in range(self.calibration.run_timeout_ticks):
            state = rl.step(state, self.inputs, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(state.abort_reason, rl.AbortReason.TIMEOUT)
        self.assertFalse(state.flags & rl.Flag.TIMER_OK)

    def test_active_checks_the_window_not_the_activation_range(self):
        active = self.activate()
        narrowed = dataclasses.replace(self.calibration, max_speed=600)
        inputs = dataclasses.replace(self.inputs, speed=650)
        self.assertEqual(
            rl.step(active, inputs, narrowed).state.phase, rl.Phase.ACTIVE
        )

    def test_cooldown_requires_release_and_complete_rearm(self):
        active = self.activate()
        released = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED
        )
        state = rl.step(active, released, self.calibration).state

        held = rl.step(state, self.inputs, self.calibration).state
        self.assertEqual(held.rearm_ticks, 0)
        state = held
        for expected in (1, 2):
            state = rl.step(state, released, self.calibration).state
            self.assertEqual(state.phase, rl.Phase.COOLDOWN)
            self.assertEqual(state.rearm_ticks, expected)
        state = rl.step(state, released, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.IDLE)
        self.assertEqual(state.rearm_ticks, 0)
        self.assertEqual(state.active_mode_snapshot, rl.Mode.OBSERVE)

        active_again = rl.step(state, self.inputs, self.calibration).state
        self.assertEqual(active_again.phase, rl.Phase.ACTIVE)

    def test_zero_code_does_not_advance_cooldown_rearm(self):
        active = self.activate()
        released = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED
        )
        cooldown = rl.step(active, released, self.calibration).state
        unknown = dataclasses.replace(self.inputs, button=0x00)
        state = rl.step(cooldown, unknown, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(state.rearm_ticks, 0)

    def test_corrupt_state_restores_map_1(self):
        for state in (
            rl.RuntimeState(phase=9),
            rl.RuntimeState(active_mode_snapshot=rl.Mode.HOLD),
            rl.RuntimeState(phase=rl.Phase.ACTIVE, active_mode_snapshot=2),
            rl.RuntimeState(phase=rl.Phase.ACTIVE, torque_fraction=1001),
            rl.RuntimeState(phase=rl.Phase.COOLDOWN, rearm_ticks=0x8000),
        ):
            with self.subTest(state=state):
                result = rl.step(state, self.inputs, self.calibration)
                self.assertEqual(result.state.phase, rl.Phase.COOLDOWN)
                self.assertEqual(
                    result.state.abort_reason, rl.AbortReason.STATE_CORRUPT
                )
                self.assertEqual(
                    result.limiter_action, rl.LimiterAction.RESTORE_MAP_1
                )
                self.assertEqual(result.limiter_index, 0)

    def test_zero_minimum_pedal_disables_the_pedal_requirement(self):
        calibration = dataclasses.replace(self.calibration, min_pedal=0)
        inputs = dataclasses.replace(self.inputs, pedal=0)
        state = self.activate(calibration, inputs)
        self.assertEqual(state.phase, rl.Phase.ACTIVE)
        self.assertTrue(state.flags & rl.Flag.PEDAL_OK)


if __name__ == "__main__":
    unittest.main()
