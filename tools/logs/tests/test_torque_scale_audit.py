import contextlib
from dataclasses import replace
from datetime import datetime
import io
from pathlib import Path
import tempfile
import tomllib
import unittest
from unittest import mock

from tools.can_dashboard import model as dashboard
from tools.logs import mlvlg, torque_scale_audit as audit
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
    """Frame 0x180 word of a net torque in raw counts (defs/analysis/can/JK08A.can.md)."""
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

    def test_new_tick_records_split_a_restart_that_the_recorded_time_reveals(self):
        ticks = [0x2820, 0x2821, 0x0300, 0x0301]
        times = [10.0, 10.01, 11.0, 11.01]
        self.assertEqual(
            list(audit.new_tick_records(ticks, times)),
            [(0, 0, 0x2820), (1, 0, 0x2821), (2, 1, 0x0300), (3, 1, 0x0301)],
        )

    def test_full_pedal_segments_keep_intervals_of_the_minimum_length(self):
        rows = [sample(index * STEP, app1=940 if index < 200 or 300 <= index < 400 else 150)
                for index in range(500)]
        segments = audit.full_pedal_segments(rows)
        self.assertEqual(len(segments), 1)
        self.assertAlmostEqual(segments[0][0], 0.0)
        self.assertAlmostEqual(segments[0][1], 199 * STEP)

    FULL_PEDAL = dict(
        speed_kmh=None, stock_rpm=None, rpm_raw=0, app1_raw=940, timing_raw=30,
        torque_raw=2500, bfs_raw=20000, selector=None, actual_word=None,
    )

    def test_a_stream_pause_keeps_its_time_and_splits_segments(self):
        pause = 5.0
        # STOP holds the tick, so the snapshot after START is the next tick.
        rows = [
            (0, tick, tick * STEP + (pause if tick > 300 else 0.0), self.FULL_PEDAL)
            for tick in range(1, 601)
        ]
        samples = audit.timed_samples(rows)
        self.assertEqual([index for index, s in enumerate(samples) if s.paused], [300])
        self.assertEqual(samples[0].seconds, STEP)
        self.assertAlmostEqual(samples[300].seconds - samples[299].seconds, STEP + pause)
        self.assertAlmostEqual(samples[-1].seconds - samples[300].seconds, 299 * STEP)
        segments = audit.full_pedal_segments(list(samples))
        self.assertEqual(len(segments), 2)
        self.assertAlmostEqual(segments[0][1], samples[299].seconds)
        self.assertAlmostEqual(segments[1][0], samples[300].seconds)

    def test_a_drained_host_stall_keeps_tick_time_and_one_segment(self):
        times = [tick * STEP for tick in range(1, 601)]
        # Snapshots 300..329 leave the host queue together with snapshot 330.
        times[300:330] = [times[330]] * 30
        rows = [(0, tick, times[tick - 1], self.FULL_PEDAL) for tick in range(1, 601)]
        samples = audit.timed_samples(rows)
        self.assertFalse(any(s.paused for s in samples))
        self.assertEqual([s.seconds for s in samples], [tick * STEP for tick in range(1, 601)])
        self.assertEqual(len(audit.full_pedal_segments(list(samples))), 1)

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


class TraceTest(unittest.TestCase):
    def test_trace_without_verified_snapshots_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            trace = Path(directory) / "capture.trc"
            trace.write_text(
                ";$FILEVERSION=1.1\n;$STARTTIME=46251.0734343518\n"
                "      1)    1000.0000 Rx   0180  8  00 00 00 00 00 00 00 00\n",
                encoding="ascii",
            )
            with self.assertRaisesRegex(
                ValueError, "no verified snapshot of telemetry profile 'tuning'"
            ):
                audit.read_trc(trace)

    def test_recording_without_a_channel_names_the_channel_it_expects(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "bare.mlg"
            specs = [
                mlvlg.FieldSpec("Date", "sec", "Time", mlvlg.MLG_U32, mlvlg.MLG_DATE),
                mlvlg.FieldSpec("Elapsed", "s", "Time"),
            ]
            with log.open("wb") as stream:
                writer = mlvlg.StreamWriter(stream, specs, 1_789_600_000)
                writer.write((1_789_600_000, 0.0), 0.0)
            with self.assertRaisesRegex(
                ValueError,
                'engine_torque_state_raw \\(channel "Gross torque-model count"\\)',
            ):
                audit.read_mlg(log)


class AuditInputTest(unittest.TestCase):
    def run_audit(self, cruise_samples, remainder_paths=()):
        captures = {"cruise.mlg": cruise_samples}

        def read_capture(path):
            return audit.Capture(Path(path), "0" * 64, tuple(captures.get(str(path), ())))

        with mock.patch.object(audit, "read_capture", read_capture), \
                mock.patch.object(audit.BaseTerm, "from_image", return_value=BASE):
            audit.audit(Path("image.bin"), Path("cruise.mlg"), [Path("run.mlg")],
                        [Path(path) for path in remainder_paths])

    def test_cruise_without_a_locked_window_is_rejected(self):
        slow = [sample(index * 0.01, speed=40.0, rpm=40.0 * LOCKED_RPM_PER_KMH)
                for index in range(300)]
        with self.assertRaisesRegex(ValueError, "cruise.mlg: no converter-locked cruise"):
            self.run_audit(slow)

    def test_remainder_without_a_pair_is_rejected(self):
        locked = [sample(index * 0.01, speed=80.0, rpm=80.0 * LOCKED_RPM_PER_KMH)
                  for index in range(300)]
        with self.assertRaisesRegex(
            ValueError, "remainder.trc: no valid 0x180 actual-torque word"
        ):
            self.run_audit(locked, ["remainder.trc"])

    def test_road_runs_need_remainder_captures(self):
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr), self.assertRaises(SystemExit) as raised:
            audit.main(["--calibration-image", "image.bin", "--cruise", "cruise.mlg",
                        "run.mlg"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("road runs need captures, --calibration-image, --cruise and --remainder",
                      stderr.getvalue())



TICK_MS = 10.24
# 12:00:00 local time.
START_DAYS = "46251.5"
# Steady levels of the CONSULT trace: seconds, engine speed, 0x180 actual
# word, APP1. Ramps of 0.5 s join them; the last level is too short.
LEVELS = ((3.0, 1500, 900, 300), (3.0, 2000, 1000, 400), (3.0, 2500, 1100, 500), (1.0, 3000, 1200, 600))
RAMP_S = 0.5
REQUEST_GAP = 50
SCALE = 0.08
DEMAND_SCALE = 0.1


class Generator(dashboard.DemoGenerator):
    def __init__(self):
        super().__init__()
        self.values = {}

    def _values(self, elapsed):
        return {**super()._values(elapsed), **self.values}


def consult_rows():
    """(rpm, actual word, APP1) of each tick and the offset of each level start."""
    rows = []
    starts = []
    previous = None
    for seconds, rpm, word, app1 in LEVELS:
        if previous is not None:
            ramp = int(RAMP_S * 1000 / TICK_MS)
            for step in range(ramp):
                fraction = (step + 1) / (ramp + 1)
                rows.append(tuple(round(a + (b - a) * fraction)
                                  for a, b in zip(previous, (rpm, word, app1))))
        starts.append(len(rows))
        rows.extend([(rpm, word, app1)] * int(seconds * 1000 / TICK_MS))
        previous = (rpm, word, app1)
    return rows, starts


def write_consult_trace(path):
    generator = Generator()
    rows, starts = consult_rows()
    lines = [";$FILEVERSION=1.1", f";$STARTTIME={START_DAYS}", "; Generated by test"]
    number = 1
    for tick, (rpm, word, app1) in enumerate(rows):
        generator.values = {
            "app1_raw": app1, "final_timing_raw": 25, "engine_torque_state_raw": 3000,
            "bfs_raw": 20000, "fuel_inhibit_mask": 0,
        }
        offset_ms = 1000.0 + tick * TICK_MS
        request = word + REQUEST_GAP
        frames = [(frame.arbitration_id, frame.data) for frame in generator.group(tick + 1)]
        frames.append((audit.ACTUAL_TORQUE_ID, (rpm * 8).to_bytes(2, "big") + bytes([
            word >> 4, (word & 0x0F) << 4 | request >> 8, request & 0xFF, 0, 0, 0])))
        for can_id, data in frames:
            payload = " ".join(f"{value:02X}" for value in data)
            lines.append(f"{number:7d}) {offset_ms:12.4f} Rx   {can_id:04X}  {len(data)}  {payload}")
            number += 1
            offset_ms += 0.1
    Path(path).write_text("\n".join(lines) + "\n", encoding="ascii")
    return [1.0 + start * TICK_MS / 1000 for start in starts]


class ConsultTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.directory = tempfile.TemporaryDirectory()
        cls.root = Path(cls.directory.name)
        cls.starts = write_consult_trace(cls.root / "block5.trc")

    @classmethod
    def tearDownClass(cls):
        cls.directory.cleanup()

    def points_file(self, text, name="points.toml"):
        path = self.root / name
        path.write_text(text, encoding="utf-8")
        return path

    def standard_points(self):
        """Every level read at its middle; the first by local time, the
        others by TRC offset, the third with a misleading engine speed."""
        blocks = []
        for index, (seconds, rpm, word, _app1) in enumerate(LEVELS):
            middle = self.starts[index] + seconds / 2
            raw = audit.word_torque(word)
            demand = audit.word_torque(word + REQUEST_GAP)
            where = (f'time = "12:00:{middle:05.2f}"' if index == 0
                     else f"offset_s = {middle:.3f}")
            blocks.append(
                f'[[point]]\ncapture = "block5.trc"\n{where}\n'
                f"engine_torque_nm = {SCALE * raw:.3f}\n"
                f"eng_torque_d_nm = {DEMAND_SCALE * demand:.3f}\n"
                f"engine_speed_rpm = {rpm}\nnote = \"level {index + 1}\"\n"
            )
        return self.points_file("tolerance_s = 15\n\n" + "\n".join(blocks))

    def test_points_match_their_steady_levels_and_fit_the_scale(self):
        result = audit.consult_audit(self.standard_points())
        rows = result["rows"]
        self.assertEqual([row["status"] for row in rows],
                         ["ok", "ok", "ok", "no_steady_interval"])
        self.assertEqual([row["word"] for row in rows[:3]], [level[2] for level in LEVELS[:3]])
        self.assertEqual([row["request_word"] for row in rows[:3]],
                         [level[2] + REQUEST_GAP for level in LEVELS[:3]])
        for row, start, level in zip(rows, self.starts, LEVELS):
            if row["status"] == "ok":
                self.assertAlmostEqual(row["start_s"], start, delta=0.05)
                self.assertGreaterEqual(row["seconds"], level[0] - 0.1)
        fit = result["fit"]
        self.assertEqual(fit["points"], 3)
        self.assertAlmostEqual(fit["slope"], SCALE, places=4)
        self.assertAlmostEqual(fit["intercept"], 0.0, places=1)
        self.assertAlmostEqual(fit["origin_slope"], SCALE, places=4)
        index = audit.CANDIDATE_SCALES_NM.index(SCALE)
        self.assertAlmostEqual(fit["candidate_residual_max"][index], 0.0, places=2)
        self.assertGreater(fit["candidate_residual_max"][index + 1], 10.0)
        self.assertAlmostEqual(result["demand_fit"]["slope"], DEMAND_SCALE, places=4)

    def test_local_time_resolves_against_the_capture_start(self):
        start = datetime(2026, 8, 17, 12, 0, 0)
        point = audit.ConsultPoint(Path("x.trc"), "12:00:07.5", None, 100.0)
        self.assertAlmostEqual(audit.hint_offset(point, start), 7.5)
        early = audit.ConsultPoint(Path("x.trc"), "11:59:58", None, 100.0)
        self.assertAlmostEqual(audit.hint_offset(early, start), -2.0)
        next_day = audit.ConsultPoint(Path("x.trc"), "00:00:10", None, 100.0)
        late = datetime(2026, 8, 17, 23, 59, 0)
        self.assertAlmostEqual(audit.hint_offset(next_day, late), 70.0)
        self.assertEqual(audit.trace_start(self.root / "block5.trc").time().hour, 12)

    def test_engine_speed_selects_among_steady_levels(self):
        level = LEVELS[1]
        middle = self.starts[1] + level[0] / 2
        # A hint between the first two levels with the speed of the second.
        hint = self.starts[1] - RAMP_S / 2
        path = self.points_file(
            f'[[point]]\ncapture = "block5.trc"\noffset_s = {hint:.3f}\n'
            f"engine_torque_nm = 80\nengine_speed_rpm = {level[1]}\n",
            "speed.toml",
        )
        (row,) = audit.consult_audit(path)["rows"]
        self.assertEqual(row["word"], level[2])
        self.assertLess(abs(row["start_s"] - middle), level[0])

    def test_point_file_errors(self):
        cases = (
            ('[[point]]\ncapture = "a.trc"\nengine_torque_nm = 1\n', "exactly one of time"),
            ('[[point]]\ncapture = "a.trc"\ntime = "12:00:00"\noffset_s = 1\n'
             "engine_torque_nm = 1\n", "exactly one of time"),
            ('[[point]]\ncapture = "a.trc"\noffset_s = 1\n', "engine_torque_nm are required"),
            ('[[point]]\ncapture = "a.trc"\noffset_s = 1\nengine_torque_nm = 1\nrpm = 2\n',
             "unknown keys rpm"),
            ("timezone = 'UTC'\n", "unknown keys timezone"),
            ("tolerance_s = 5\n", "no \\[\\[point\\]\\]"),
            ("min_seconds = 0\n", "must be positive"),
            ("word_spread = -1\n", "spreads non-negative"),
        )
        for index, (text, message) in enumerate(cases):
            with self.subTest(message=message):
                path = self.points_file(text, f"bad-{index}.toml")
                with self.assertRaisesRegex(ValueError, message):
                    audit.load_consult_points(path)

    def test_file_thresholds_and_the_candidate_of_a_rejected_point(self):
        text = self.standard_points().read_text(encoding="utf-8")
        relaxed = self.points_file(
            text.replace("tolerance_s = 15\n", "tolerance_s = 15\nmin_seconds = 0.8\n"),
            "relaxed.toml",
        )
        rows = audit.consult_audit(relaxed)["rows"]
        self.assertEqual([row["status"] for row in rows], ["ok"] * len(LEVELS))
        self.assertEqual(rows[-1]["word"], LEVELS[-1][2])
        # Under the default 2 s the short last level fails; its candidate is
        # the steady end of the previous level at another engine speed.
        rows = audit.consult_audit(self.standard_points())["rows"]
        self.assertNotIn("candidate", rows[0])
        candidate = rows[-1]["candidate"]
        self.assertEqual((candidate["word"], candidate["rpm"]), (LEVELS[2][2], LEVELS[2][1]))
        self.assertEqual(
            (candidate["word_spread"], candidate["rpm_spread"], candidate["app1_spread"]),
            (0, 0, 0),
        )
        self.assertGreaterEqual(candidate["seconds"], audit.CONSULT_MIN_SECONDS)
        self.assertAlmostEqual(candidate["start_s"] + candidate["seconds"],
                               self.starts[3] - RAMP_S, delta=0.03)

    def test_candidate_reports_the_spread_that_the_thresholds_reject(self):
        # No level lasts 3.5 s, so every window reaches into a ramp.
        middle = self.starts[1] + LEVELS[1][0] / 2
        path = self.points_file(
            f'min_seconds = 3.5\n\n[[point]]\ncapture = "block5.trc"\n'
            f"offset_s = {middle:.3f}\nengine_torque_nm = 80\n",
            "long.toml",
        )
        (row,) = audit.consult_audit(path)["rows"]
        self.assertEqual(row["status"], "no_steady_interval")
        candidate = row["candidate"]
        self.assertGreaterEqual(candidate["seconds"], 3.5)
        self.assertLessEqual(candidate["start_s"], middle)
        self.assertGreaterEqual(candidate["start_s"] + candidate["seconds"], middle)
        self.assertGreater(candidate["word_spread"], 2 * audit.CONSULT_WORD_SPREAD)

    def test_steady_intervals_break_at_fuel_cut_and_spread(self):
        def steady(count, word, *, mask=0, start=0.0, rpm=2000):
            return [replace(sample(start + index * STEP, rpm=rpm, app1=300, word=word, mask=mask),
                            offset_s=start + index * STEP) for index in range(count)]

        rows = steady(300, 1000) + steady(5, 1000, mask=1, start=3.0) + steady(300, 1003, start=3.05)
        intervals = audit.steady_intervals(rows)
        self.assertEqual(intervals, [(0, 299), (305, 604)])
        self.assertEqual(audit.steady_intervals(rows, rpm_target=2500), [])
        self.assertEqual(audit.nearest_steady(rows, 5.0), (305, 604))

    def test_command_line_prints_consult_figures(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(audit.main(["--consult-points", str(self.standard_points())]), 0)
        values = tomllib.loads(output.getvalue())
        self.assertEqual(values["consult_point_count"], len(LEVELS))
        self.assertEqual(values["consult_steady_word"], [level[2] for level in LEVELS[:3]])
        self.assertEqual(values["consult_fit_points"], 3)
        self.assertAlmostEqual(values["consult_fit_slope_nm_per_raw"], SCALE, places=4)
        self.assertEqual(values["consult_demand_fit_points"], 3)
        self.assertEqual(values["consult_capture_name"], ["block5.trc"])
        self.assertEqual(values["consult_min_seconds"], audit.CONSULT_MIN_SECONDS)
        self.assertEqual(values["consult_candidate_word"], [-1, -1, -1, LEVELS[2][2]])
        self.assertNotIn("locked_rpm_per_kmh", values)

    def test_command_line_needs_road_runs_or_points(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                audit.main([])
            with self.assertRaises(SystemExit):
                audit.main(["capture.mlg"])


if __name__ == "__main__":
    unittest.main()
