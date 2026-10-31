import dataclasses
import unittest

from patches import rolling_launch as rl


class RollingLaunchTest(unittest.TestCase):
    def setUp(self):
        self.calibration = rl.Calibration(
            mode=rl.Mode.RPM_HOLD,
            enable_mask=0x01,
            coolant_min=80,
            coolant_max=220,
            min_speed=10,
            min_rpm_native=200,
            min_pedal=1000,
            rpm_offset_native=16,
            min_hysteresis_native=4,
            max_hysteresis_native=12,
            hysteresis_ratio_tenths=20,
            run_timeout_ticks=4,
            rearm_ticks=3,
        )
        self.inputs = rl.Inputs(
            active_index=0,
            button=rl.BUTTON_CANCEL,
            speed=20,
            rpm_native=300,
            pedal=2000,
            coolant=150,
        )

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
            {"schema_version": 1},
            {"mode": 3},
            {"enable_mask": 0x20},
            {"options": 1},
            {"coolant_min": 221, "coolant_max": 220},
            {"min_speed": -1},
            {"min_speed": 0x100},
            {"retard_ramp_native": 0},
            {"retard_ramp_native": 17},
            {"min_rpm_native": 0},
            {"rpm_offset_native": 0},
            {"min_hysteresis_native": 0},
            {"min_hysteresis_native": 13},
            {"max_hysteresis_native": 16},
            {"max_hysteresis_native": 0x100},
            {"hysteresis_ratio_tenths": 0},
            {"hysteresis_ratio_tenths": 0x100},
            {"run_timeout_ticks": 0},
            {"rearm_ticks": 0},
            {"target_commands": (109,) * 5},
            {"magic_inverse": 0},
            {"end_marker": 0},
        )
        for changes in invalid:
            with self.subTest(changes=changes):
                candidate = dataclasses.replace(self.calibration, **changes)
                self.assertFalse(candidate.is_valid())

    def test_gate_flags_report_all_conditions_not_only_first_failure(self):
        inputs = dataclasses.replace(
            self.inputs,
            button=rl.BUTTON_RELEASED,
            speed=5,
            coolant=150,
        )
        flags, reason = rl.evaluate_gates(inputs, self.calibration)
        self.assertEqual(reason, rl.AbortReason.BUTTON_INVALID)
        self.assertTrue(flags & rl.Flag.CONFIG_VALID)
        self.assertTrue(flags & rl.Flag.MAP_ENABLED)
        self.assertTrue(flags & rl.Flag.RPM_OK)
        self.assertTrue(flags & rl.Flag.COOLANT_OK)
        self.assertFalse(flags & rl.Flag.BUTTON_HELD)
        self.assertFalse(flags & rl.Flag.SPEED_OK)

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

    def test_observe_mode_transitions_without_a_fuel_cut_request(self):
        calibration = dataclasses.replace(
            self.calibration, mode=rl.Mode.OBSERVE
        )
        result = rl.step(rl.RuntimeState(), self.inputs, calibration)
        self.assertEqual(result.state.phase, rl.Phase.ACTIVE)
        self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)
        self.assertFalse(result.state.flags & rl.Flag.FUEL_HOLD)
        high = dataclasses.replace(self.inputs, rpm_native=400)
        held = rl.step(result.state, high, calibration).state
        self.assertEqual(held.phase, rl.Phase.ACTIVE)
        self.assertEqual(
            (held.fuel_cut_request, held.request_latch), (0, 0)
        )

        released = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED
        )
        result = rl.step(result.state, released, calibration)
        self.assertEqual(result.state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)

    def test_rpm_hold_captures_saturated_thresholds_without_limiter_writes(self):
        result = rl.step(rl.RuntimeState(), self.inputs, self.calibration)
        self.assertEqual(result.state.phase, rl.Phase.ACTIVE)
        self.assertEqual(result.state.captured_rpm_native, 300)
        self.assertEqual(result.state.cut_rpm_native, 316)
        self.assertEqual(result.state.restore_rpm_native, 310)
        self.assertEqual(result.state.retard_band_start_native, 300)
        self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)
        self.assertTrue(result.state.flags & rl.Flag.FUEL_HOLD)
        self.assertEqual(result.state.fuel_cut_request, 0)

        released = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED
        )
        result = rl.step(result.state, released, self.calibration)
        self.assertEqual(result.state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(
            result.state.abort_reason, rl.AbortReason.BUTTON_RELEASED
        )
        self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)

        saturated_inputs = dataclasses.replace(
            self.inputs, rpm_native=0xFFF8
        )
        calibration = dataclasses.replace(
            self.calibration, min_rpm_native=9
        )
        saturated = rl.step(
            rl.RuntimeState(), saturated_inputs, calibration
        )
        self.assertEqual(saturated.state.cut_rpm_native, 0xFFFF)
        self.assertEqual(saturated.state.restore_rpm_native, 0xFFF3)
        self.assertEqual(
            saturated.state.retard_band_start_native, 0xFFF8
        )

    def test_the_request_holds_from_cut_until_below_restore(self):
        state = rl.step(rl.RuntimeState(), self.inputs, self.calibration).state
        self.assertEqual((state.cut_rpm_native, state.restore_rpm_native), (316, 310))
        for rpm, latch in (
            (315, 0), (316, 1), (320, 1), (311, 1), (310, 1), (309, 0),
            (312, 0), (316, 1),
        ):
            with self.subTest(rpm=rpm):
                inputs = dataclasses.replace(self.inputs, rpm_native=rpm)
                state = rl.step(state, inputs, self.calibration).state
                self.assertEqual(state.phase, rl.Phase.ACTIVE)
                self.assertEqual(state.request_latch, latch)
                self.assertEqual(state.fuel_cut_request, 0x3F if latch else 0)
                self.assertEqual(bool(state.flags & rl.Flag.FUEL_CUT), bool(latch))
            state = dataclasses.replace(state, run_ticks=0)

        released = dataclasses.replace(self.inputs, button=rl.BUTTON_RELEASED)
        state = rl.step(state, released, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual((state.fuel_cut_request, state.request_latch), (0, 0))
        self.assertFalse(state.flags & rl.Flag.FUEL_CUT)

    def test_every_tick_clears_a_stale_request(self):
        cooldown = rl.RuntimeState(
            phase=rl.Phase.COOLDOWN,
            abort_reason=rl.AbortReason.BUTTON_RELEASED,
            active_mode_snapshot=rl.Mode.RPM_HOLD,
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
                result = rl.step(rl.RuntimeState(), inputs, self.calibration)
                self.assertEqual(result.state.phase, rl.Phase.ACTIVE)
                self.assertEqual(
                    bool(result.state.flags & rl.Flag.FUEL_CUT), expected
                )

    def test_adaptive_hysteresis_and_retard_ramp_use_min_ratio_and_max(self):
        calibration = dataclasses.replace(
            self.calibration,
            min_rpm_native=1,
            retard_ramp_native=8,
        )
        cases = (
            (160, 176, 172, 168),
            (400, 416, 408, 400),
            (560, 576, 565, 560),
            (600, 616, 604, 600),
        )
        for captured, cut, restore, band_start in cases:
            with self.subTest(captured=captured):
                inputs = dataclasses.replace(
                    self.inputs, rpm_native=captured
                )
                result = rl.step(rl.RuntimeState(), inputs, calibration)
                self.assertEqual(result.state.cut_rpm_native, cut)
                self.assertEqual(result.state.restore_rpm_native, restore)
                self.assertEqual(
                    result.state.retard_band_start_native, band_start
                )

    def test_active_aborts_cover_map_request_change_and_timeout(self):
        active = rl.step(
            rl.RuntimeState(), self.inputs, self.calibration
        ).state

        requested = dataclasses.replace(self.inputs, button=rl.BUTTON_SET)
        result = rl.step(active, requested, self.calibration)
        self.assertEqual(result.state.abort_reason, rl.AbortReason.MAP_REQUEST)

        changed = dataclasses.replace(self.inputs, active_index=1)
        result = rl.step(active, changed, self.calibration)
        self.assertEqual(result.state.abort_reason, rl.AbortReason.MAP_CHANGED)
        self.assertEqual(result.limiter_index, 0)

        state = active
        for _ in range(self.calibration.run_timeout_ticks):
            result = rl.step(state, self.inputs, self.calibration)
            state = result.state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(state.abort_reason, rl.AbortReason.TIMEOUT)
        self.assertFalse(state.flags & rl.Flag.TIMER_OK)

        invalid_mode = dataclasses.replace(self.calibration, mode=3)
        result = rl.step(active, self.inputs, invalid_mode)
        self.assertEqual(result.state.abort_reason, rl.AbortReason.MODE_CHANGED)

        invalid_marker = dataclasses.replace(self.calibration, magic=0)
        result = rl.step(active, self.inputs, invalid_marker)
        self.assertEqual(
            result.state.abort_reason, rl.AbortReason.CONFIG_INVALID
        )

    def test_cooldown_requires_release_and_complete_rearm(self):
        active = rl.step(
            rl.RuntimeState(), self.inputs, self.calibration
        ).state
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

        active_again = rl.step(state, self.inputs, self.calibration).state
        self.assertEqual(active_again.phase, rl.Phase.ACTIVE)

    def test_zero_code_does_not_advance_cooldown_rearm(self):
        active = rl.step(
            rl.RuntimeState(), self.inputs, self.calibration
        ).state
        released = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED
        )
        cooldown = rl.step(active, released, self.calibration).state
        unknown = dataclasses.replace(self.inputs, button=0x00)
        state = rl.step(cooldown, unknown, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(state.rearm_ticks, 0)

    def test_corrupt_state_restores_map_1(self):
        state = dataclasses.replace(rl.RuntimeState(), phase=9)
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
        result = rl.step(rl.RuntimeState(), inputs, calibration)
        self.assertEqual(result.state.phase, rl.Phase.ACTIVE)
        self.assertTrue(result.state.flags & rl.Flag.PEDAL_OK)

    def test_zero_minimum_speed_disables_the_speed_requirement(self):
        calibration = dataclasses.replace(self.calibration, min_speed=0)
        inputs = dataclasses.replace(self.inputs, speed=0)
        result = rl.step(rl.RuntimeState(), inputs, calibration)
        self.assertEqual(result.state.phase, rl.Phase.ACTIVE)
        self.assertTrue(result.state.flags & rl.Flag.SPEED_OK)

    def test_ignition_adapter_can_only_add_retard(self):
        calibration = dataclasses.replace(
            self.calibration,
            mode=rl.Mode.RPM_HOLD_RETARD,
            target_commands=(115, 116, 117, 114, 113),
        )
        active = rl.step(
            rl.RuntimeState(), self.inputs, calibration
        ).state

        _, effective = rl.apply_ignition_command(
            active, calibration, 110, 300
        )
        self.assertEqual(effective, 110)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, 304
        )
        self.assertEqual(effective, 111)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, 308
        )
        self.assertEqual(effective, 112)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, 312
        )
        self.assertEqual(effective, 113)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, 315
        )
        self.assertEqual(effective, 114)

        state, effective = rl.apply_ignition_command(
            active, calibration, 110, 316
        )
        self.assertEqual(effective, 115)
        self.assertEqual(state.stock_ign_command, 110)
        self.assertEqual(state.effective_ign_command, 115)

        _, effective = rl.apply_ignition_command(
            active, calibration, 117, 316
        )
        self.assertEqual(effective, 117)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, 316, apc_mode_snapshot=0x40
        )
        self.assertEqual(effective, 110)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, 316, apc_mode_snapshot=0x20
        )
        self.assertEqual(effective, 115)
        inactive = dataclasses.replace(active, phase=rl.Phase.COOLDOWN)
        _, effective = rl.apply_ignition_command(
            inactive, calibration, 110, 316
        )
        self.assertEqual(effective, 110)

        with self.assertRaisesRegex(ValueError, "APC mode snapshot"):
            rl.apply_ignition_command(
                active, calibration, 110, 316, apc_mode_snapshot=0x100
            )
        with self.assertRaisesRegex(ValueError, "native RPM"):
            rl.apply_ignition_command(active, calibration, 110, 0x10000)


if __name__ == "__main__":
    unittest.main()
