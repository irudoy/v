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
            hysteresis_native=8,
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
            {"schema_version": 2},
            {"mode": 3},
            {"enable_mask": 0x20},
            {"options": 2},
            {"coolant_min": 221, "coolant_max": 220},
            {"min_speed": 0},
            {"speed_padding": 1},
            {"min_rpm_native": 0},
            {"min_pedal": 0},
            {"rpm_offset_native": 0},
            {"hysteresis_native": 200},
            {"run_timeout_ticks": 0},
            {"rearm_ticks": 0},
            {"target_commands": (109,) * 5},
            {"reserved": 1},
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

    def test_observe_mode_transitions_without_limiter_writes(self):
        calibration = dataclasses.replace(
            self.calibration, mode=rl.Mode.OBSERVE
        )
        result = rl.step(rl.RuntimeState(), self.inputs, calibration)
        self.assertEqual(result.state.phase, rl.Phase.ACTIVE)
        self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)
        self.assertFalse(result.state.flags & rl.Flag.FUEL_OVERLAY)

        released = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED
        )
        result = rl.step(result.state, released, calibration)
        self.assertEqual(result.state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(result.limiter_action, rl.LimiterAction.NONE)

    def test_rpm_hold_captures_saturated_overlay_and_restores_snapshot(self):
        result = rl.step(rl.RuntimeState(), self.inputs, self.calibration)
        self.assertEqual(result.state.phase, rl.Phase.ACTIVE)
        self.assertEqual(result.state.captured_rpm_native, 300)
        self.assertEqual(result.state.cut_rpm_native, 316)
        self.assertEqual(result.state.restore_rpm_native, 308)
        self.assertEqual(
            result.limiter_action, rl.LimiterAction.APPLY_OVERLAY
        )
        self.assertEqual(result.limiter_index, 0)

        released = dataclasses.replace(
            self.inputs, button=rl.BUTTON_RELEASED
        )
        result = rl.step(result.state, released, self.calibration)
        self.assertEqual(result.state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(
            result.state.abort_reason, rl.AbortReason.BUTTON_RELEASED
        )
        self.assertEqual(
            result.limiter_action, rl.LimiterAction.RESTORE_SNAPSHOT
        )

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
        self.assertEqual(saturated.state.restore_rpm_native, 0xFFF7)

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

    def test_brake_gate_is_opt_in(self):
        braking = dataclasses.replace(self.inputs, brake_status=0x80)
        result = rl.step(
            rl.RuntimeState(), braking, self.calibration
        )
        self.assertEqual(result.state.phase, rl.Phase.ACTIVE)

        calibration = dataclasses.replace(
            self.calibration, options=rl.Option.BRAKE_GATE
        )
        result = rl.step(rl.RuntimeState(), braking, calibration)
        self.assertEqual(result.state.phase, rl.Phase.IDLE)
        self.assertEqual(
            result.state.abort_reason, rl.AbortReason.BRAKE_ACTIVE
        )

    def test_ignition_adapter_can_only_add_retard(self):
        calibration = dataclasses.replace(
            self.calibration,
            mode=rl.Mode.RPM_HOLD_RETARD,
            target_commands=(115, 116, 117, 114, 113),
        )
        active = rl.step(
            rl.RuntimeState(), self.inputs, calibration
        ).state

        state, effective = rl.apply_ignition_command(
            active, calibration, 110
        )
        self.assertEqual(effective, 115)
        self.assertEqual(state.stock_ign_command, 110)
        self.assertEqual(state.effective_ign_command, 115)

        _, effective = rl.apply_ignition_command(active, calibration, 117)
        self.assertEqual(effective, 117)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, apc_mode_snapshot=0x40
        )
        self.assertEqual(effective, 110)
        _, effective = rl.apply_ignition_command(
            active, calibration, 110, apc_mode_snapshot=0x20
        )
        self.assertEqual(effective, 115)
        inactive = dataclasses.replace(active, phase=rl.Phase.COOLDOWN)
        _, effective = rl.apply_ignition_command(inactive, calibration, 110)
        self.assertEqual(effective, 110)

        with self.assertRaisesRegex(ValueError, "APC mode snapshot"):
            rl.apply_ignition_command(
                active, calibration, 110, apc_mode_snapshot=0x100
            )


if __name__ == "__main__":
    unittest.main()
