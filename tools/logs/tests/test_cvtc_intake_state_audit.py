import dataclasses
from pathlib import Path
from types import SimpleNamespace
import unittest

from tools.logs import cvtc_intake_state_audit as audit
from tools.logs import cvtc_target_audit


CALIBRATION = audit.load_state_calibration()
REARM = 4


def state_input(index, **overrides):
    """Return a snapshot that passes every observable idle-source term."""
    values = {
        "run": 0,
        "tick": 100 + index,
        "rpm_raw": 124,
        "bfs_raw": 0x2000,
        "coolant_raw": 80,
        "oil_raw": 80,
        "iat_raw": 70,
        "battery_raw": 170,
        "app1_raw": 150,
        "vehicle_speed_kmh": 0.0,
    }
    values.update(overrides)
    return audit.StateInput(**values)


def replay(inputs, latch=True, rearm=REARM):
    return audit.replay_states(
        inputs,
        CALIBRATION,
        app1_released_max=153,
        rearm_snapshots=rearm,
        latch_initial=latch,
    )


def sample(index, target, run=0, tick=None):
    return SimpleNamespace(
        run=run, tick=100 + index if tick is None else tick, reference_a_raw=target
    )


def point(selected, main=None, alternate=0x80, band="cold"):
    return SimpleNamespace(
        coolant_selected_raw=selected,
        main_selected_raw=selected + 1 if main is None else main,
        alternate_source_raw=alternate,
        coolant_band=band,
    )


def state(idle=False, operating=False):
    return audit.IntakeState(
        idle_bit=idle,
        operating_bit=operating,
        latch=True,
        failing_idle_terms=(),
        failing_operating_terms=(),
    )


class StateCalibrationTest(unittest.TestCase):
    def test_stock_constants(self):
        cal = CALIBRATION
        self.assertEqual(
            (cal.idle_rpm_hold, cal.idle_rpm_set_offset, cal.idle_bfs_min),
            (112, 8, 0x1400),
        )
        self.assertEqual(
            (cal.idle_coolant_min, cal.idle_coolant_max, cal.idle_oil_min),
            (55, 100, 55),
        )
        self.assertEqual((cal.idle_iat_min, cal.idle_iat_max), (55, 100))
        self.assertEqual(cal.idle_oil_max, 255)
        self.assertTrue(cal.idle_oil_enabled)
        self.assertTrue(cal.idle_iat_enabled)
        self.assertEqual(
            (cal.idle_speed_byte_max, cal.idle_rearm_reload), (2, 100)
        )
        self.assertEqual((cal.battery_min_exclusive, cal.battery_max), (125, 200))
        self.assertTrue(cal.closed_throttle_clears_operating)
        self.assertEqual(
            (
                cal.coolant_ceiling,
                cal.coolant_latched_min,
                cal.coolant_unlatched_min,
                cal.engine_speed_min,
            ),
            (170, 70, 106, 72),
        )
        self.assertEqual(cal.rise_period, 5)

    def test_speed_byte_divides_the_km_h_times_ten_word_by_twenty(self):
        self.assertEqual(audit.speed_byte(0.0), 0)
        self.assertEqual(audit.speed_byte(5.99), 2)
        self.assertEqual(audit.speed_byte(6.0), 3)
        self.assertEqual(audit.speed_byte(1000.0), 0xFF)


class StateReplayTest(unittest.TestCase):
    def test_closed_pedal_at_standstill_sets_both_bits(self):
        states = replay([state_input(0)])
        self.assertTrue(states[0].idle_bit)
        self.assertTrue(states[0].operating_bit)

    def test_applied_pedal_uses_the_latch_selected_coolant_flag(self):
        inputs = [state_input(0, app1_raw=300, vehicle_speed_kmh=20.0)]
        latched = replay(inputs, latch=True)[0]
        self.assertFalse(latched.idle_bit)
        self.assertTrue(latched.operating_bit)
        unlatched = replay(inputs, latch=False)[0]
        self.assertFalse(unlatched.operating_bit)
        self.assertEqual(unlatched.failing_operating_terms, ("coolant_unlatched",))
        warm = replay(
            [state_input(0, app1_raw=300, vehicle_speed_kmh=20.0, coolant_raw=107)],
            latch=False,
        )[0]
        self.assertTrue(warm.operating_bit)

    def test_latched_coolant_flag_needs_more_than_seventy(self):
        inputs = [
            state_input(0, app1_raw=300, vehicle_speed_kmh=20.0, coolant_raw=70),
            state_input(1, app1_raw=300, vehicle_speed_kmh=20.0, coolant_raw=71),
            state_input(2, app1_raw=300, vehicle_speed_kmh=20.0, coolant_raw=68),
            state_input(3, app1_raw=300, vehicle_speed_kmh=20.0, coolant_raw=67),
        ]
        states = replay(inputs, latch=True)
        # The flag sets above 70 and holds down to 68 with its offset of 3.
        self.assertEqual(
            [item.operating_bit for item in states], [False, True, True, False]
        )

    def test_latch_sets_at_125_and_clears_below_65(self):
        states = replay(
            [
                state_input(0, coolant_raw=124),
                state_input(1, coolant_raw=125),
                state_input(2, coolant_raw=65),
                state_input(3, coolant_raw=64),
            ],
            latch=False,
        )
        self.assertEqual([item.latch for item in states], [False, True, True, False])

    def test_engine_speed_flag_gates_the_map_path(self):
        states = replay(
            [
                state_input(0, app1_raw=300, vehicle_speed_kmh=20.0, rpm_raw=71),
                state_input(1, app1_raw=300, vehicle_speed_kmh=20.0, rpm_raw=72),
                state_input(2, app1_raw=300, vehicle_speed_kmh=20.0, rpm_raw=56),
                state_input(3, app1_raw=300, vehicle_speed_kmh=20.0, rpm_raw=55),
            ]
        )
        self.assertEqual(
            [item.operating_bit for item in states], [False, True, True, False]
        )

    def test_engine_speed_term_sets_at_120_and_holds_to_112(self):
        states = replay(
            [
                state_input(0, rpm_raw=119),
                state_input(1, rpm_raw=120),
                state_input(2, rpm_raw=112),
            ]
        )
        self.assertEqual([item.idle_bit for item in states], [False, True, True])
        self.assertEqual(states[0].failing_idle_terms, ("rpm",))

    def test_speed_and_pedal_terms(self):
        states = replay(
            [
                state_input(0, vehicle_speed_kmh=6.0),
                state_input(1, app1_raw=154),
            ]
        )
        self.assertEqual(states[0].failing_idle_terms, ("speed",))
        self.assertEqual(states[1].failing_idle_terms, ("closed_throttle",))
        # With the pedal off its idle position the map path is open.
        self.assertTrue(states[1].operating_bit)
        # Moving with the pedal at idle leaves both paths closed.
        self.assertFalse(states[0].operating_bit)
        self.assertIn("pedal_applied", states[0].failing_operating_terms)

    def test_option_bits_gate_the_oil_and_iat_terms(self):
        inputs = [state_input(0, oil_raw=40, iat_raw=120)]
        states = replay(inputs)
        self.assertEqual(states[0].failing_idle_terms, ("oil", "iat"))
        calibration = dataclasses.replace(
            CALIBRATION, idle_oil_enabled=False, idle_iat_enabled=False
        )
        states = audit.replay_states(
            inputs,
            calibration,
            app1_released_max=153,
            rearm_snapshots=REARM,
            latch_initial=True,
        )
        self.assertTrue(states[0].idle_bit)

    def test_oil_ceiling_holds_with_its_offset(self):
        calibration = dataclasses.replace(CALIBRATION, idle_oil_max=100)
        states = audit.replay_states(
            [
                state_input(0, oil_raw=101),
                state_input(1, oil_raw=100),
                state_input(2, oil_raw=103),
                state_input(3, oil_raw=104),
            ],
            calibration,
            app1_released_max=153,
            rearm_snapshots=0,
            latch_initial=True,
        )
        self.assertEqual(
            [item.idle_bit for item in states], [False, True, True, False]
        )
        self.assertEqual(states[3].failing_idle_terms, ("oil",))

    def test_rearm_wait_follows_the_last_failing_pass(self):
        inputs = [
            state_input(0, rpm_raw=100),
            state_input(1),
            state_input(2, rpm_raw=100),
            *(state_input(index) for index in range(3, 3 + REARM + 1)),
        ]
        states = replay(inputs)
        # The first activation does not wait for an earlier failure.
        self.assertEqual([item.idle_bit for item in states[:3]], [False, True, False])
        self.assertEqual(
            [item.idle_bit for item in states[3:]], [False] * REARM + [True]
        )
        self.assertEqual(states[3].failing_idle_terms, ("rearm_wait",))

    def test_restart_clears_the_activation(self):
        inputs = [
            state_input(0),
            state_input(1, rpm_raw=100),
            state_input(2, run=1, tick=5),
        ]
        states = replay(inputs, rearm=100)
        self.assertEqual([item.idle_bit for item in states], [True, False, True])

    def test_missed_ticks_count_toward_the_rearm_wait(self):
        inputs = [
            state_input(0),
            state_input(1, rpm_raw=100),
            state_input(2, tick=101 + REARM),
            state_input(3, tick=102 + REARM),
        ]
        states = replay(inputs)
        self.assertEqual(
            [item.idle_bit for item in states], [True, False, False, True]
        )


class PartitionTest(unittest.TestCase):
    def test_rise_requires_three_steps_one_period_apart(self):
        targets = [128] * 6 + [129, 129, 129, 129, 129, 130, 130, 130, 130, 130, 131]
        samples = [sample(index, target) for index, target in enumerate(targets)]
        self.assertEqual(
            audit.rise_indices(samples, 5), set(range(1, len(targets)))
        )
        short = [sample(index, target) for index, target in enumerate(targets[:12])]
        self.assertEqual(audit.rise_indices(short, 5), set())
        self.assertEqual(audit.rise_indices(samples, 4), set())

    def test_leading_idle_hold_before_the_first_rise_is_unresolved(self):
        samples = [sample(index, 0x80) for index in range(8)]
        states = [state(idle=True, operating=True)] * 8
        self.assertEqual(
            audit.start_unresolved(samples, states, {5, 6, 7}), {1, 2, 3, 4}
        )
        states = [state()] + [state(idle=True, operating=True)] * 7
        self.assertEqual(audit.start_unresolved(samples, states, {5, 6, 7}), set())
        self.assertEqual(audit.start_unresolved(samples, states, set()), set())

    def test_classes(self):
        cases = (
            (state(), point(150), 0x80, "neutral_target_0x80"),
            (state(), point(150), 150, "neutral_target_active"),
            (state(True, True), point(150, alternate=160), 160, "idle_exact"),
            (state(True, True), point(150, alternate=160), 155, "idle_other"),
            (state(False, True), point(150), 150, "map_exact_active"),
            (state(False, True), point(0x80), 0x80, "map_exact_0x80"),
            (state(False, True), point(150), 0x80, "map_target_0x80"),
            (state(False, True), point(150), 147, "map_within_3"),
            (state(False, True), point(150), 140, "map_other"),
        )
        for item, replayed, target, expected in cases:
            with self.subTest(expected=expected):
                samples = [sample(0, 0x80), sample(1, target)]
                self.assertEqual(
                    audit.classify(
                        1, samples, [replayed, replayed], [item, item], set(), set()
                    ),
                    expected,
                )
        samples = [sample(0, 0x80), sample(1, 155)]
        idle = [state(True, True)] * 2
        self.assertEqual(
            audit.classify(1, samples, [point(150)] * 2, idle, {1}, set()),
            "idle_rise",
        )
        self.assertEqual(
            audit.classify(1, samples, [point(150)] * 2, idle, {1}, {1}),
            "start_unresolved",
        )

    def test_band_span_uses_the_source_snapshot(self):
        samples = [
            SimpleNamespace(timestamp=0.5 * index, coolant_raw=100 + index)
            for index in range(5)
        ]
        inputs = [
            state_input(index, vehicle_speed_kmh=float(10 * index))
            for index in range(5)
        ]
        span = audit._band_span("cold", [2, 4], samples, inputs)
        self.assertEqual(span.comparisons, 2)
        self.assertEqual(span.elapsed_range, (0.5, 1.5))
        self.assertEqual(span.coolant_raw_range, (101, 103))
        self.assertEqual(span.vehicle_speed_kmh_max, 30.0)
        empty = audit._band_span("warm", [], samples, inputs)
        self.assertEqual(empty.comparisons, 0)
        self.assertIsNone(empty.elapsed_range)

    def test_discrimination_needs_a_selected_byte_unlike_every_path(self):
        # Row i compares target i with the replay of source snapshot i - 1.
        points = [
            point(150, main=160, alternate=170),
            point(150, main=150, alternate=170),
            point(150, main=160, alternate=150),
            point(0x80, main=160, alternate=170),
            point(150, main=160, alternate=170),
            point(148, main=160, alternate=170),
            point(148, main=160, alternate=170),
        ]
        targets = (0x80, 150, 150, 150, 0x80, 170, 148)
        samples = [sample(index, target) for index, target in enumerate(targets)]
        inputs = [
            state_input(index, app1_raw=300, vehicle_speed_kmh=10.0)
            for index in range(len(targets))
        ]
        result = audit._discrimination(
            "cold", [1, 2, 3, 4, 5, 6], samples, points, inputs, 153, {128, 148}
        )
        self.assertEqual(result.comparisons, 3)
        self.assertEqual(
            (result.selected, result.selected_moving, result.selected_pedal_applied),
            (2, 2, 2),
        )
        # Selected 150 lies between the cells; 148 is a cell value.
        self.assertEqual(result.selected_off_cell, 1)
        self.assertEqual((result.alternate, result.neutral, result.main), (1, 0, 0))


class RecordIndexTest(unittest.TestCase):
    def test_samples_carry_the_record_index_past_bridge_records(self):
        columns = {
            "date": [0.0, 0.0, 1.0, 1.0],
            "elapsed": [0.0, 0.3, 0.6, 0.61],
            "schema_verified": [1.0, 1.0, 1.0, 1.0],
            "tick16": [10.0, 10.0, 11.0, 12.0],
            "bfs_raw": [8192.0] * 4,
            "stock_rpm": [1500.0] * 4,
            "coolant_raw": [80.0] * 4,
            "knock_surface_state": [0.0] * 4,
            "intake_cvtc_target_raw": [150.0] * 4,
            "exhaust_cvtc_target_raw": [128.0] * 4,
            "intake_cvtc_actual_b1_raw": [150.0] * 4,
            "intake_cvtc_actual_b2_raw": [150.0] * 4,
            "app1_raw": [150.0, 150.0, 300.0, 150.0],
            "vehicle_speed_kmh": [0.0, 0.0, 12.5, 0.0],
            "oil_temperature_did_source_raw": [80.0] * 4,
            "iat_raw": [70.0] * 4,
            "battery_voltage_raw": [170.0] * 4,
        }
        recording = SimpleNamespace(
            path=Path("synthetic.mlg"), columns=columns, record_count=4
        )
        _events, bridges, samples = cvtc_target_audit._recording_samples(
            recording, "tuning"
        )
        self.assertEqual(bridges, 1)
        self.assertEqual([item.record_index for item in samples], [0, 2, 3])
        inputs = audit._state_inputs(recording, samples)
        self.assertEqual([item.app1_raw for item in inputs], [150, 300, 150])
        self.assertEqual([item.vehicle_speed_kmh for item in inputs], [0.0, 12.5, 0.0])
        columns["iat_raw"][2] = float("nan")
        with self.assertRaisesRegex(ValueError, "iat_raw"):
            audit._state_inputs(recording, samples)


if __name__ == "__main__":
    unittest.main()
