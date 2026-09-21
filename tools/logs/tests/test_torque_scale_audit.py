from dataclasses import replace
from pathlib import Path
import tempfile
import tomllib
import unittest

from tools.logs import torque_scale_audit as audit
from tools.mapkit import rom as romkit

STOCK_AXIS = (64, 128, 192, 256, 320, 416, 512, 608)
STOCK_TABLE = (407, 428, 446, 485, 542, 644, 739, 824)
STOCK_BFS_NUMERATOR = 185
STOCK_BFS_SCALER = 27226
LOCKED_RPM_PER_KMH = 25.608
RPM_PER_KMH = audit.gear_speed_ratios(LOCKED_RPM_PER_KMH)
BASE = audit.BaseTerm(STOCK_AXIS, STOCK_TABLE, STOCK_BFS_NUMERATOR, STOCK_BFS_SCALER)
STEP = audit.BASE_TICK_SECONDS


def sample(seconds, *, speed=None, rpm=None, app1=0, timing=30, torque=2500, bfs=20000,
           selector=None, word=None, mask=0, run=0):
    rpm_raw = 0 if rpm is None else int(rpm / audit.RPM_PER_COUNT)
    return audit.Sample(
        seconds=seconds, run=run, speed_kmh=speed, stock_rpm=rpm, rpm_raw=rpm_raw,
        app1_raw=app1, timing_raw=timing, torque_raw=torque, bfs_raw=bfs, selector=selector,
        actual_word=word, fuel_inhibit_mask=mask,
    )


def pull(selector, *, speed_ratio=0.95, gear=2, seconds=3.0, first_kmh=40.0, last_kmh=60.0, **extra):
    """A full-pedal run with a linear speed rise and a converter at speed_ratio in gear."""
    count = int(seconds / STEP) + 1
    rows = []
    for index in range(count):
        speed = first_kmh + (last_kmh - first_kmh) * index / (count - 1)
        rpm = RPM_PER_KMH[gear] * speed / speed_ratio
        rows.append(sample(index * STEP, speed=speed, rpm=rpm, app1=940, selector=selector, **extra))
    return rows


def pack(net):
    """Frame 0x180 word of a net torque in raw counts (defs/JK08A.can.md)."""
    return max(0, min(4094, int(net / audit.CAN_TORQUE_DIVISOR) + audit.CAN_TORQUE_ZERO))


def synthetic_point(gear, speed_kmh, accel, net, segment=0):
    rad = audit.engine_rad_per_metre(RPM_PER_KMH[gear])
    return audit.Point(
        capture="synthetic", segment=segment, seconds=0.0, speed_mps=speed_kmh / 3.6, accel=accel,
        rpm=RPM_PER_KMH[gear] * speed_kmh, engine_accel=rad * accel, gear=gear, speed_ratio=1.0,
        gross=net, base=0.0, net=net, actual_word_torque=None,
    )


class BaseTermTest(unittest.TestCase):
    def test_stock_image_holds_the_replayed_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "stock.bin"
            path.write_bytes(romkit.load("JK08A").data)
            self.assertEqual(audit.BaseTerm.from_image(path), BASE)

    def test_lookup_interpolates_with_a_q16_fraction(self):
        for rpm_raw, value in zip(STOCK_AXIS, STOCK_TABLE):
            self.assertEqual(BASE.lookup(rpm_raw), value)
        self.assertEqual(BASE.lookup(0), STOCK_TABLE[0])
        self.assertEqual(BASE.lookup(1000), STOCK_TABLE[-1])
        self.assertEqual(BASE.lookup(96), 407 + (21 * 0x8000 >> 16))
        falling = audit.BaseTerm((0, 100), (300, 100), 1, 1)
        self.assertEqual(falling.lookup(25), 300 - (200 * 0x4000 >> 16))

    def test_value_subtracts_the_truncated_fuel_term_and_saturates(self):
        self.assertEqual(BASE.value(64, 27226), 407 - 185)
        self.assertEqual(BASE.value(64, 147), 407)
        self.assertEqual(BASE.value(64, 27226 * 2), 407 - 370)
        self.assertEqual(BASE.value(64, 27226 * 3), 0)


class WordTest(unittest.TestCase):
    def test_actual_torque_word_uses_byte_2_and_the_high_nibble(self):
        self.assertEqual(audit.actual_torque_word(bytes([0x12, 0x34, 0x3A, 0x5F, 0, 0, 0, 0])), 0x3A5)

    def test_word_torque_is_the_midpoint_of_the_packed_interval(self):
        for net in range(-3000, 3001):
            error = abs(audit.word_torque(pack(net)) - net)
            self.assertLessEqual(error, 4 if -5 < net < 5 else 2, net)

    def test_remainder_skips_invalid_words_reduction_and_fuel_cut(self):
        net = 1500
        gross = net + BASE.value(400, 20000) + 10
        rows = [
            sample(0.00, rpm=5000, app1=900, torque=gross, word=pack(net)),
            sample(0.01, rpm=5000, app1=900, torque=gross, word=audit.CAN_TORQUE_INVALID),
            sample(0.02, rpm=5000, app1=500, torque=gross, word=pack(net)),
            sample(0.03, rpm=5000, app1=900, timing=10, torque=gross, word=pack(net)),
            sample(0.04, rpm=5000, app1=900, torque=gross, word=pack(net), mask=0x3F),
            sample(0.05, rpm=5000, app1=900, torque=gross, word=None),
        ]
        pairs = audit.remainder_pairs(rows, BASE)
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0], (5000.0, 10 - (audit.word_torque(pack(net)) - net)))


class KinematicsTest(unittest.TestCase):
    def test_gear_ratios_scale_the_locked_gear(self):
        self.assertAlmostEqual(RPM_PER_KMH[5], LOCKED_RPM_PER_KMH)
        for gear, ratio in audit.RE5R05A_RATIOS.items():
            self.assertAlmostEqual(RPM_PER_KMH[gear], LOCKED_RPM_PER_KMH * ratio / 0.839)

    def test_classify_gear_requires_the_coupling_range(self):
        gear, ratio = audit.classify_gear(50.0, RPM_PER_KMH[2] * 50.0 / 0.95, RPM_PER_KMH)
        self.assertEqual(gear, 2)
        self.assertAlmostEqual(ratio, 0.95)
        self.assertIsNone(audit.classify_gear(50.0, RPM_PER_KMH[2] * 50.0 / 0.80, RPM_PER_KMH))
        self.assertIsNone(audit.classify_gear(50.0, RPM_PER_KMH[2] * 50.0 / 1.02, RPM_PER_KMH))
        self.assertIsNone(audit.classify_gear(None, 3000.0, RPM_PER_KMH))

    def test_line_fit_recovers_a_line_and_needs_five_samples(self):
        ts = [index * STEP for index in range(40)]
        xs = [3.0 + 2.5 * t for t in ts]
        value, slope = audit.line_fit(ts, xs, 0.2, 0.1)
        self.assertAlmostEqual(value, 3.5)
        self.assertAlmostEqual(slope, 2.5)
        self.assertIsNone(audit.line_fit(ts[:4], xs[:4], 0.0, 1.0))

    def test_new_tick_records_skip_bridges_unwrap_and_split_restarts(self):
        ticks = [65534, 65534, 65535, 0, 1, 5000, 3]
        self.assertEqual(
            list(audit.new_tick_records(ticks)),
            [(0, 0, 65534), (2, 0, 65535), (3, 0, 65536), (4, 0, 65537), (5, 0, 70536), (6, 1, 3)],
        )

    def test_full_pedal_segments_keep_intervals_of_the_minimum_length(self):
        rows = [sample(index * STEP, app1=940 if index < 200 or 300 <= index < 400 else 150)
                for index in range(500)]
        segments = audit.full_pedal_segments(rows)
        self.assertEqual(len(segments), 1)
        self.assertAlmostEqual(segments[0][0], 0.0)
        self.assertAlmostEqual(segments[0][1], 199 * STEP)

    def test_locked_ratio_keeps_steady_windows_only(self):
        steady = [sample(index * STEP, speed=80.0, rpm=80.0 * LOCKED_RPM_PER_KMH) for index in range(300)]
        slipping = [sample(3.1 + index * STEP, speed=80.0,
                           rpm=80.0 * LOCKED_RPM_PER_KMH * (1.02 if index % 2 else 1.0))
                    for index in range(200)]
        slow = [sample(5.2 + index * STEP, speed=40.0, rpm=40.0 * LOCKED_RPM_PER_KMH) for index in range(200)]
        result = audit.locked_ratio(steady + slipping + slow)
        self.assertEqual(result["window_count"], 3)
        self.assertAlmostEqual(result["median"], LOCKED_RPM_PER_KMH)


class SegmentTest(unittest.TestCase):
    def points(self, rows, remainder=10.0):
        return audit.segment_points("synthetic", 0, rows, rows[0].seconds, rows[-1].seconds,
                                    RPM_PER_KMH, BASE, remainder)

    def test_manual_second_gear_gives_coupled_points(self):
        rows = pull(0x88)
        points = self.points(rows)
        self.assertGreater(len(points), 20)
        self.assertEqual({p.gear for p in points}, {2})
        accel = (60.0 - 40.0) / 3.6 / rows[-1].seconds
        for point in points:
            self.assertAlmostEqual(point.accel, accel, places=6)
            self.assertAlmostEqual(point.speed_ratio, 0.95, places=6)
            self.assertAlmostEqual(point.net, point.gross - point.base - 10.0)

    def test_manual_third_gear_rejects_a_coupled_second_gear_match(self):
        self.assertEqual(self.points(pull(0x90)), [])

    def test_drive_position_keeps_the_kinematic_gear(self):
        self.assertEqual({p.gear for p in self.points(pull(0x20))}, {2})

    def test_fuel_cut_and_retarded_timing_reject_points(self):
        self.assertEqual(self.points(pull(0x88, mask=0x01)), [])
        self.assertEqual(self.points(pull(0x88, timing=audit.MIN_TIMING_RAW - 1)), [])

    def test_points_below_the_engine_speed_limit_are_rejected(self):
        self.assertEqual(self.points(pull(0x88, first_kmh=20.0, last_kmh=30.0)), [])


class ForceBalanceTest(unittest.TestCase):
    def test_implied_grade_inverts_the_flywheel_torque(self):
        point = synthetic_point(3, 90.0, 1.2, 1.0)
        for vehicle in (audit.NOMINAL, replace(audit.NOMINAL, speed_scale=0.97, efficiency=0.86)):
            torque = audit.flywheel_torque(point, vehicle, RPM_PER_KMH, 0.03)
            point_at = replace(point, net=torque / 0.1)
            self.assertAlmostEqual(audit.implied_grade(point_at, vehicle, RPM_PER_KMH, 0.1), 0.03)

    def test_flywheel_torque_adds_the_rotating_terms(self):
        point = synthetic_point(1, 30.0, 3.0, 1.0)
        still = replace(audit.NOMINAL, engine_inertia=0.0, turbine_inertia=0.0)
        rad = audit.engine_rad_per_metre(RPM_PER_KMH[1])
        difference = (audit.flywheel_torque(point, audit.NOMINAL, RPM_PER_KMH)
                      - audit.flywheel_torque(point, still, RPM_PER_KMH))
        self.assertAlmostEqual(difference, (0.18 + 0.06) * rad * 3.0)

    def test_consistent_scale_recovers_the_generating_scale(self):
        scale, grade = 0.09, 0.02
        runs = {1: [(20.0, 4.0), (30.0, 3.8), (40.0, 3.5)], 2: [(60.0, 2.4), (70.0, 2.2), (80.0, 2.0)]}
        points = {}
        for gear, rows in runs.items():
            points[gear] = []
            for speed, accel in rows:
                point = synthetic_point(gear, speed, accel, 1.0)
                torque = audit.flywheel_torque(point, audit.NOMINAL, RPM_PER_KMH, grade)
                points[gear].append(replace(point, net=torque / scale))
        self.assertAlmostEqual(
            audit.consistent_scale(points[1], points[2], audit.NOMINAL, RPM_PER_KMH), scale)
        for point in points[1] + points[2]:
            self.assertAlmostEqual(audit.implied_grade(point, audit.NOMINAL, RPM_PER_KMH, scale), grade)

    def test_neutral_coast_at_the_nominal_road_load_has_zero_grade(self):
        vehicle = audit.NOMINAL
        mass = vehicle.mass_kg + vehicle.rotating_mass_kg
        speed = 100.0 / 3.6
        rows = []
        index = 0
        while speed * 3.6 > 45.0:
            rows.append(sample(index * STEP, speed=speed * 3.6, rpm=800.0, app1=150, selector=0x18))
            speed -= (vehicle.rolling_n + vehicle.aero_n_per_m2s2 * speed * speed) / mass * STEP
            index += 1
        grades = [grade for *_, grade in audit.coast_grades(rows)]
        self.assertGreater(len(grades), 20)
        self.assertLess(max(abs(grade) for grade in grades), 2e-4)

    def test_box_corners_cover_every_combination(self):
        corners = list(audit.box_corners())
        self.assertEqual(len(corners), 2 ** len(audit.VEHICLE_BOX))
        for name, (low, high) in audit.VEHICLE_BOX.items():
            self.assertEqual({getattr(vehicle, name) for vehicle in corners}, {low, high})


class OutputTest(unittest.TestCase):
    def test_result_lines_parse_as_toml(self):
        points = [synthetic_point(2, 50.0 + index, 2.0, 2300.0) for index in range(6)]
        result = {
            "locked": {"window_count": 3, "median": LOCKED_RPM_PER_KMH},
            "rpm_per_kmh": RPM_PER_KMH,
            "remainder_pairs": 4,
            "remainder": 10.0,
            "segments": [{"capture": "synthetic", "start": 1.0, "end": 4.0, "points": 6, "gears": [2]}],
            "points": points,
            "ratio_nominal": 0.9,
            "ratio_box": (0.8, 1.1),
            "ratio_per_segment": {("synthetic", 0): 0.9},
            "ratio_gross_nominal": 0.8,
            "bands": {(2, 3500): (6, 1, 0.9)},
            "candidates": {
                scale: {"segment_grade_nominal": {("synthetic", 0): 0.01},
                        "median_grade_nominal": 0.01, "median_grade_box": (0.0, 0.02)}
                for scale in audit.CANDIDATE_SCALES_NM
            },
            "gross_candidate": {"segment_grade_nominal": {}, "median_grade_nominal": 0.05,
                                "median_grade_box": (0.04, 0.06)},
            "sensitivity": {"mass_kg": (0.88, 0.92)},
            "gear_pairs": [],
            "word_point_count": 0,
            "word_gap_median": None,
            "coast_windows": 0,
            "coast_grade_range": None,
            "coast_grade_median": None,
        }
        parsed = tomllib.loads("\n".join(audit.result_lines(result)))
        self.assertEqual(parsed["locked_rpm_per_kmh"], LOCKED_RPM_PER_KMH)
        self.assertEqual(parsed["segment_gears"], [[2]])
        self.assertEqual(parsed["candidate_median_grade_percent"], [1.0] * 4)
        self.assertEqual(parsed["sensitivity_ratio"], {"mass_kg": [0.88, 0.92]})
        self.assertNotIn("word_gap_median_raw", parsed)


if __name__ == "__main__":
    unittest.main()
