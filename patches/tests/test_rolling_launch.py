import dataclasses
from pathlib import Path
import re
import unittest

from patches import rolling_launch as rl


ROOT = Path(__file__).resolve().parents[2]
HARNESS = ROOT / "tools" / "sh-elf-run" / "rolling_launch_harness.c"
CONTROLLER_ROW = re.compile(r'\{"(ctrl-[a-z-]+)",([-0-9a-fx, ]+)\}')
TRIM_ROW = re.compile(r'\{"((?:trim|gain)-[a-z0-9-]+)",([-0-9, ]+)\}')
ADAPTER_ROW = re.compile(r'\{"(adapter-[a-z-]+)",([-0-9a-fxU, ]+)\}')


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
            {"reserved": 1},
            {"slots": (rl.Slot(integral_gain=-1),) * rl.SLOT_COUNT},
            {"slots": (rl.Slot(integral_gain=0x8000),) * rl.SLOT_COUNT},
            {"slots": (rl.Slot(max_trim=rl.TRIM_MAX + 1, trim_efficiency=300),) * rl.SLOT_COUNT},
            {"slots": (rl.Slot(floor_command=0x100),) * rl.SLOT_COUNT},
            {"slots": (rl.Slot(max_trim=20, trim_efficiency=0),) * rl.SLOT_COUNT},
            {"slots": (rl.Slot(max_trim=20, trim_efficiency=1001),) * rl.SLOT_COUNT},
            {"slots": (rl.Slot(trim_efficiency=999),) * rl.SLOT_COUNT},
            {"slots": (rl.Slot(),) * (rl.SLOT_COUNT - 1)},
            {"slot_end_marker": 0},
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
            {"rpm_ceiling_hysteresis_native": 0},
            {"rpm_ceiling_hysteresis_native": 0x100},
            {"rpm_ceiling_hysteresis_native": 81},
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
            slots=(
                rl.Slot(
                    integral_gain=0x7FFF,
                    max_trim=rl.TRIM_MAX,
                    floor_command=0xFF,
                    trim_efficiency=1,
                ),
            ) * rl.SLOT_COUNT,
            integrator_limit=rl.U_ONE,
            rpm_ceiling_offset_native=0xFFFF,
            rpm_ceiling_hysteresis_native=0xFF,
            run_timeout_ticks=0x7FFF,
            rearm_ticks=0x7FFF,
            speed_frame_age_limit=rl.SPEED_FRAME_AGE_LIMIT_MAX,
        )
        self.assertTrue(candidate.is_valid())
        self.assertTrue(
            dataclasses.replace(candidate, target_speed_offset=-149).is_valid()
        )
        self.assertTrue(
            dataclasses.replace(
                self.calibration, rpm_ceiling_hysteresis_native=80
            ).is_valid()
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
        cal = self.calibration
        self.assertEqual(rl.update_integrator(0, 0, 30, cal, 2), 0)
        self.assertEqual(rl.update_integrator(0, 1000, -30, cal, 2), 0)
        self.assertEqual(rl.update_integrator(0, 500, 5, cal, 2), -10)
        self.assertEqual(rl.update_integrator(0, 500, -5, cal, 2), 10)
        bounded = dataclasses.replace(cal, integrator_limit=1)
        self.assertEqual(rl.update_integrator(15, 500, -5, bounded, 2), 16)
        self.assertEqual(rl.update_integrator(-15, 500, 5, bounded, 2), -16)

    def test_the_integrator_uses_the_gain_of_the_activation_map(self):
        slots = tuple(
            rl.Slot(integral_gain=index + 1) for index in range(rl.SLOT_COUNT)
        )
        calibration = dataclasses.replace(self.calibration, slots=slots)
        for index in range(rl.SLOT_COUNT):
            state = rl.RuntimeState(
                phase=rl.Phase.ACTIVE,
                active_index_snapshot=index,
                target_speed=600,
                torque_fraction=500,
            )
            inputs = dataclasses.replace(self.inputs, speed=605)
            result = rl._publish_active(state, rl.Flag(0), inputs, calibration)
            self.assertEqual(result.integrator, -5 * (index + 1))

    def test_the_cut_fraction_compensates_the_trim_efficiency(self):
        for u, e, expected in (
            (0, 1000, 1000), (500, 1000, 500), (1000, 1000, 0),
            (0, 824, 1000), (412, 824, 500), (824, 824, 0),
            (900, 824, 0), (1000, 1, 0), (0, 1, 1000), (1, 3, 667),
        ):
            with self.subTest(u=u, e=e):
                self.assertEqual(rl.cut_fraction(u, e), expected)
        self.assertEqual(rl.trim_efficiency(0), rl.U_ONE)
        self.assertEqual(rl.trim_efficiency(45), 824)
        self.assertEqual(rl.trim_efficiency(0xFF), 3)
        with self.assertRaises(ValueError):
            rl.trim_efficiency(0x100)

    def test_the_ignition_command_retards_to_the_floor_and_never_advances(self):
        slot = rl.Slot(max_trim=20, floor_command=120, trim_efficiency=824)
        slots = (rl.Slot(),) * 3 + (slot, rl.Slot())
        calibration = dataclasses.replace(self.calibration, slots=slots)
        hold = rl.RuntimeState(
            phase=rl.Phase.ACTIVE,
            active_index_snapshot=3,
            active_mode_snapshot=rl.Mode.HOLD,
        )
        for stock, expected in (
            (80, 100), (100, 120), (110, 120), (120, 120), (130, 130),
            (0x1FF, 0xFF),
        ):
            with self.subTest(stock=stock):
                self.assertEqual(
                    rl.ignition_command(hold, stock, calibration, False),
                    expected,
                )
        for state, fallback in (
            (rl.RuntimeState(), False),
            (dataclasses.replace(hold, active_mode_snapshot=rl.Mode.OBSERVE), False),
            (dataclasses.replace(hold, phase=rl.Phase.COOLDOWN), False),
            (dataclasses.replace(hold, active_index_snapshot=0), False),
            (hold, True),
        ):
            with self.subTest(state=state, fallback=fallback):
                self.assertEqual(
                    rl.ignition_command(state, 80, calibration, fallback), 80
                )

    def test_a_schema_4_record_maps_to_uniform_slots(self):
        head = bytearray(self.calibration.to_bytes()[: rl.LEGACY_CONFIG_SIZE])
        head[2] = rl.LEGACY_SCHEMA_VERSION
        head[0x16:0x18] = (3).to_bytes(2, "big")
        calibration = rl.Calibration.from_legacy_bytes(bytes(head))
        self.assertEqual(calibration.slots, (rl.Slot(integral_gain=3),) * rl.SLOT_COUNT)
        self.assertEqual(calibration.reserved, 0)
        self.assertEqual(calibration.to_bytes()[3:0x16], bytes(head[3:0x16]))
        for corrupt in (bytes(head[:-1]), bytes(head[:2]) + b"\x05" + bytes(head[3:])):
            with self.assertRaises(ValueError):
                rl.Calibration.from_legacy_bytes(corrupt)

    def test_harness_trim_table_matches_the_model(self):
        rows = TRIM_ROW.findall(HARNESS.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 11)
        for name, values in rows:
            (index, gain, efficiency, speed, fraction, next_integrator,
             command, next_fraction, next_cut) = (
                int(item, 0) for item in values.split(","))
            with self.subTest(case=name):
                slot = rl.Slot(
                    integral_gain=gain,
                    max_trim=0 if efficiency == rl.U_ONE else 20,
                    floor_command=120,
                    trim_efficiency=efficiency,
                )
                calibration = dataclasses.replace(
                    self.calibration,
                    window_width=40,
                    window_top=20,
                    slots=tuple(
                        slot if item == index else rl.Slot()
                        for item in range(rl.SLOT_COUNT)
                    ),
                )
                self.assertTrue(calibration.is_valid())
                state = rl.RuntimeState(
                    phase=rl.Phase.ACTIVE,
                    active_index_snapshot=index,
                    active_mode_snapshot=rl.Mode.HOLD,
                    captured_rpm_native=300,
                    target_speed=500,
                    torque_fraction=fraction,
                )
                inputs = dataclasses.replace(
                    self.inputs, speed=speed, rpm_native=300
                )
                result = rl._publish_active(
                    state, rl.Flag(0x0FFF), inputs, calibration
                )
                self.assertEqual(result.integrator, next_integrator)
                self.assertEqual(result.torque_command, command)
                self.assertEqual(result.torque_fraction, next_fraction)
                self.assertEqual(result.cut_fraction, next_cut)

    def test_harness_adapter_table_matches_the_model(self):
        rows = ADAPTER_ROW.findall(HARNESS.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 16)
        slots = (rl.Slot(),) * 3 + (
            rl.Slot(max_trim=20, floor_command=120, trim_efficiency=824),
            rl.Slot(max_trim=20, floor_command=255, trim_efficiency=824),
        )
        calibration = dataclasses.replace(self.calibration, slots=slots)
        for name, values in rows:
            phase, mode, index, apc, stock, expected = (
                int(item.rstrip("U"), 0) for item in values.split(","))
            with self.subTest(case=name):
                if index < rl.SLOT_COUNT:
                    state = rl.RuntimeState(
                        phase=phase,
                        active_index_snapshot=index,
                        active_mode_snapshot=mode,
                    )
                    low = rl.ignition_command(
                        state, stock, calibration, bool(apc & 0x40)
                    )
                else:
                    low = stock & 0xFF
                # The adapter replaces r4 only with a later command.
                self.assertEqual(
                    expected, stock if low == stock & 0xFF else low
                )

    def test_harness_controller_table_matches_the_model(self):
        rows = CONTROLLER_ROW.findall(HARNESS.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 24)
        for name, values in rows:
            (mode, target, fraction, integrator, speed, rpm, captured, gain,
             limit, fuel, error, next_integrator, command, next_fraction,
             request, flags, latch, next_latch) = (
                int(item, 0) for item in values.split(","))
            with self.subTest(case=name):
                calibration = dataclasses.replace(
                    self.calibration,
                    mode=mode,
                    slots=(rl.Slot(integral_gain=gain),) * rl.SLOT_COUNT,
                    integrator_limit=limit,
                )
                state = rl.RuntimeState(
                    phase=rl.Phase.ACTIVE,
                    active_mode_snapshot=mode,
                    captured_rpm_native=captured,
                    target_speed=target,
                    torque_fraction=fraction,
                    integrator=integrator,
                    ceiling_latch=latch,
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
                     result.fuel_cut_request, int(result.flags),
                     result.ceiling_latch),
                    (error, next_integrator, command, next_fraction,
                     request, flags, next_latch),
                )

    def test_observe_mode_never_requests_a_fuel_cut(self):
        calibration = dataclasses.replace(
            self.calibration, mode=rl.Mode.OBSERVE
        )
        state = self.activate(calibration)
        self.assertEqual(state.phase, rl.Phase.ACTIVE)
        self.assertFalse(state.flags & rl.Flag.HOLD)
        high = dataclasses.replace(self.inputs, rpm_native=0xFFFF)
        held = rl.step(
            dataclasses.replace(state, ceiling_latch=1), high, calibration
        ).state
        self.assertEqual(held.phase, rl.Phase.ACTIVE)
        self.assertEqual(held.fuel_cut_request, 0)
        self.assertEqual(held.ceiling_latch, 0)
        self.assertFalse(held.flags & rl.Flag.CEILING)

    def test_the_ceiling_latch_cuts_above_the_ceiling_and_restores_below_the_hysteresis(self):
        # Activation at 300 places the cut sum at 380 and the restore sum at 372.
        state = self.activate()
        for rpm, held in (
            (379, False), (380, False), (381, True), (373, True),
            (372, False), (376, False), (400, True),
        ):
            with self.subTest(rpm=rpm):
                inputs = dataclasses.replace(self.inputs, rpm_native=rpm)
                state = rl.step(state, inputs, self.calibration).state
                self.assertEqual(state.phase, rl.Phase.ACTIVE)
                self.assertEqual(state.ceiling_latch, int(held))
                self.assertEqual(state.fuel_cut_request, 0x3F if held else 0)
                self.assertEqual(bool(state.flags & rl.Flag.CEILING), held)
                self.assertEqual(bool(state.flags & rl.Flag.FUEL_CUT), held)
            state = dataclasses.replace(state, run_ticks=0)

        released = dataclasses.replace(self.inputs, button=rl.BUTTON_RELEASED)
        state = rl.step(state, released, self.calibration).state
        self.assertEqual(state.phase, rl.Phase.COOLDOWN)
        self.assertEqual(state.fuel_cut_request, 0)
        self.assertEqual(state.ceiling_latch, 0)
        self.assertFalse(state.flags & rl.ACTIVE_OUTPUT_FLAGS)

    def test_activation_clears_a_retained_ceiling_latch(self):
        state = rl.step(
            rl.RuntimeState(ceiling_latch=1), self.inputs, self.calibration
        ).state
        self.assertEqual(state.phase, rl.Phase.ACTIVE)
        self.assertEqual(state.ceiling_latch, 0)

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
            rl.RuntimeState(phase=rl.Phase.ACTIVE, ceiling_latch=2),
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


class SparkCutActuatorTest(unittest.TestCase):
    HOLD = rl.RuntimeState(
        phase=rl.Phase.ACTIVE,
        active_mode_snapshot=rl.Mode.HOLD,
        torque_fraction=500,
        cut_fraction=500,
    )

    def reset(self):
        return rl.spark_event(
            rl.RuntimeState(), rl.SparkCutState(), rl.SparkEvent()
        ).state

    def run_events(self, runtime, count, cut=None, first=1, **event):
        """Run ``count`` matches in firing order from cylinder ``first``."""
        cut = cut or self.reset()
        vetoes = []
        for index in range(count):
            cylinder = (first - 1 + index) % rl.SPARK_CYLINDER_COUNT + 1
            result = rl.spark_event(
                runtime, cut, rl.SparkEvent(cylinder=cylinder, **event)
            )
            cut = result.state
            vetoes.append(result.vetoed)
        return cut, vetoes

    def test_cut_count_and_cylinder_balance_hold_for_every_fraction(self):
        period = 6 * rl.SPARK_CYLINDER_COUNT
        for first in range(1, rl.SPARK_CYLINDER_COUNT + 1):
            for u in range(rl.U_ONE + 1):
                runtime = dataclasses.replace(self.HOLD, cut_fraction=rl.U_ONE - u)
                _cut, vetoes = self.run_events(runtime, 6 * period, first=first)
                ideal = period * (rl.U_ONE - u) / rl.U_ONE
                for start in range(len(vetoes) - period + 1):
                    case = (first, u, start)
                    count = sum(vetoes[start : start + period])
                    self.assertLessEqual(abs(count - ideal), 3, case)
                    if start % period:
                        continue
                    self.assertLessEqual(abs(count - ideal), 1, case)
                    cylinders = [
                        sum(
                            vetoes[
                                start + index : start + period : rl.SPARK_CYLINDER_COUNT
                            ]
                        )
                        for index in range(rl.SPARK_CYLINDER_COUNT)
                    ]
                    self.assertLessEqual(max(cylinders) - min(cylinders), 1, case)

    def test_timeout_forced_match_changes_nothing(self):
        cut = rl.SparkCutState(quiet_events=7, cut_count=9)
        event = rl.SparkEvent(spark_armed=False, veto_byte=0x41, misfire_latch=1)
        for runtime in (rl.RuntimeState(), self.HOLD):
            result = rl.spark_event(runtime, cut, event)
            self.assertEqual(result, rl.SparkResult(cut, 0x41, 1))

    def test_ineligible_events_leave_every_accumulator(self):
        cut, _ = self.run_events(self.HOLD, 4)
        for event in (
            rl.SparkEvent(cylinder=5, synchronized=False),
            rl.SparkEvent(cylinder=5, apc_fallback=True),
            rl.SparkEvent(cylinder=5, dwell_degrees=rl.SPARK_DWELL_LIMIT_DEGREES + 1),
            rl.SparkEvent(cylinder=5, dwell_degrees=0xFF),
            rl.SparkEvent(cylinder=0),
            rl.SparkEvent(cylinder=7),
        ):
            result = rl.spark_event(self.HOLD, cut, event)
            self.assertEqual(result.state, cut)
            self.assertFalse(result.vetoed)
        limit = rl.SparkEvent(cylinder=5, dwell_degrees=rl.SPARK_DWELL_LIMIT_DEGREES)
        result = rl.spark_event(self.HOLD, cut, limit)
        self.assertNotEqual(result.state.accumulators[4], cut.accumulators[4])
        self.assertEqual(result.state.accumulators[:4], cut.accumulators[:4])

    def test_veto_sets_only_bit_7(self):
        full = dataclasses.replace(self.HOLD, cut_fraction=rl.U_ONE)
        cut = self.reset()
        for seed in (0x00, 0x40, 0x7F, 0x80, 0xC0):
            result = rl.spark_event(full, cut, rl.SparkEvent(veto_byte=seed))
            self.assertEqual(result.veto_byte, seed | 0x80)
            self.assertEqual(result.state.cut_count, 1)
        none = dataclasses.replace(self.HOLD, cut_fraction=0)
        _cut, vetoes = self.run_events(none, 72)
        self.assertFalse(any(vetoes))

    def test_states_outside_an_active_hold_reset_the_accumulators(self):
        cut, _ = self.run_events(self.HOLD, 5)
        for runtime in (
            rl.RuntimeState(),
            dataclasses.replace(self.HOLD, active_mode_snapshot=rl.Mode.OBSERVE),
            dataclasses.replace(self.HOLD, phase=rl.Phase.COOLDOWN),
            dataclasses.replace(self.HOLD, cut_fraction=rl.U_ONE + 1),
        ):
            result = rl.spark_event(runtime, cut, rl.SparkEvent())
            self.assertFalse(result.vetoed)
            self.assertEqual(result.state.accumulators, rl.SPARK_CYLINDER_OFFSETS)
        corrupt = dataclasses.replace(cut, accumulators=(rl.SPARK_CUT_ONE,) * 6)
        result = rl.spark_event(self.HOLD, corrupt, rl.SparkEvent(cylinder=3))
        self.assertFalse(result.vetoed)
        self.assertEqual(result.state.accumulators, rl.SPARK_CYLINDER_OFFSETS)

    def test_leaving_active_sets_no_further_veto(self):
        full = dataclasses.replace(self.HOLD, cut_fraction=rl.U_ONE)
        cut, vetoes = self.run_events(full, 6)
        self.assertTrue(all(vetoes))
        released = dataclasses.replace(full, phase=rl.Phase.COOLDOWN)
        _cut, vetoes = self.run_events(released, 6, cut)
        self.assertFalse(any(vetoes))

    def test_misfire_latch_is_marked_and_released_only_by_its_rules(self):
        cut = self.reset()
        marked = rl.spark_event(self.HOLD, cut, rl.SparkEvent())
        self.assertEqual(marked.misfire_latch, rl.MISFIRE_MARKER)
        stock = rl.spark_event(self.HOLD, cut, rl.SparkEvent(misfire_latch=0x32))
        self.assertEqual(stock.misfire_latch, 0x32)
        observe = dataclasses.replace(self.HOLD, active_mode_snapshot=rl.Mode.OBSERVE)
        self.assertEqual(rl.spark_event(observe, cut, rl.SparkEvent()).misfire_latch, 0)

        held = marked.state
        self.assertEqual(held.quiet_events, 0)
        for phase in (rl.Phase.COOLDOWN, rl.Phase.IDLE):
            runtime = rl.RuntimeState(phase=phase)
            state = held
            for count in range(1, rl.MISFIRE_RELEASE_EVENTS + 1):
                result = rl.spark_event(
                    runtime, state, rl.SparkEvent(misfire_latch=rl.MISFIRE_MARKER)
                )
                state = result.state
                self.assertEqual(state.quiet_events, count)
                released = (
                    phase == rl.Phase.IDLE and count >= rl.MISFIRE_RELEASE_EVENTS
                )
                self.assertEqual(result.misfire_latch, 0 if released else 1)
        quiet = dataclasses.replace(held, quiet_events=rl.QUIET_EVENTS_MAX)
        result = rl.spark_event(rl.RuntimeState(), quiet, rl.SparkEvent(misfire_latch=0x32))
        self.assertEqual(result.misfire_latch, 0x32)
        self.assertEqual(result.state.quiet_events, rl.QUIET_EVENTS_MAX)

if __name__ == "__main__":
    unittest.main()
