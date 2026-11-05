"""The steady-window acceptance metrics of the hold audit."""

import contextlib
from dataclasses import replace
import io
import math
from pathlib import Path
import statistics
import tempfile
import unittest
from unittest import mock

from patches import rolling_launch as model
from tools.logs import rolling_launch_audit as audit
from tools.logs.tests.test_rolling_launch_audit import (
    HISTORICAL,
    RPM_SETTINGS,
    RPM_SLOT,
    SPEED_SETTINGS,
    rpm_run,
    run_main,
)


THRESHOLDS = """\
schema_version = 1

[window]
steady_after_s = {steady}
min_steady_s = {minimum}
band_hz = [3.0, 7.0]
band_min_s = 1.0

[rpm]
p5_below_soft_rpm = 100
p95_above_rpm = 200
peak_above_rpm = 500

[speed]
mean_error_kmh = 0.5
speed_spread_kmh = 1.0
rpm_spread_rpm = 200

[series]
repeats = 3
"""
PERIOD = audit.BASE_TICK_SECONDS
LAUNCH = RPM_SLOT.launch_rpm_native * audit.RPM_PER_COUNT
WIDTH = RPM_SLOT.launch_soft_width_native * audit.RPM_PER_COUNT


def thresholds(steady=1.0, minimum=1.0, text=None):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "thresholds.toml"
        path.write_text(text or THRESHOLDS.format(steady=steady, minimum=minimum))
        return audit.load_thresholds(path)


def snapshot(tick, rpm, speed=None, **values):
    native = round(rpm / audit.RPM_PER_COUNT)
    fields = dict(
        tick=tick, button=None, dashboard=None, speed_kmh=speed, coolant_raw=None,
        rpm_raw=native, rpm_low=native, rpm_high=native, fuel_inhibit_mask=0,
        final_timing_raw=0, app1_raw=0, bfs_raw=0, knock_surface_state=0,
        exhaust_cvtc_target_raw=0, phase=model.Phase.ACTIVE, map_index=0,
    )
    fields.update(values)
    return audit.Sample(**fields)


def sine(count, amplitude, k, offset=0.0):
    return [offset + amplitude * math.sin(2 * math.pi * k * n / count) for n in range(count)]


class ThresholdFileTest(unittest.TestCase):
    def test_the_file_states_every_value(self):
        values = thresholds()
        self.assertEqual(values.band_hz, (3.0, 7.0))
        self.assertEqual(values.repeats, 3)
        self.assertEqual(values.p95_above_rpm, 200.0)

    def test_an_incomplete_or_invalid_file_is_refused(self):
        base = THRESHOLDS.format(steady=1.0, minimum=1.0)
        cases = {
            "missing key": (base.replace("peak_above_rpm = 500\n", ""), "keys differ"),
            "extra key": (base.replace("[series]\n", "[series]\nlimit = 1\n"), "keys differ"),
            "missing table": (base.split("[series]")[0], "tables differ"),
            "schema": (base.replace("schema_version = 1", "schema_version = 2"), "schema"),
            "schema boolean": (
                base.replace("schema_version = 1", "schema_version = true"), "schema"
            ),
            "schema float": (
                base.replace("schema_version = 1", "schema_version = 1.0"), "schema"
            ),
            "negative": (base.replace("p95_above_rpm = 200", "p95_above_rpm = -1"), ">= 0"),
            "boolean": (base.replace("rpm_spread_rpm = 200", "rpm_spread_rpm = true"), "number"),
            "band order": (base.replace("[3.0, 7.0]", "[7.0, 3.0]"), "low < high"),
            "repeats": (base.replace("repeats = 3", "repeats = 0"), "integer >= 1"),
        }
        for name, (text, message) in cases.items():
            with self.subTest(name), self.assertRaisesRegex(ValueError, message):
                thresholds(text=text)


class BandTest(unittest.TestCase):
    def test_a_sine_on_a_band_bin_reads_its_rms(self):
        # 256 ticks of 10.24 ms: bin 13 is 4.96 Hz, bin 3 is 1.14 Hz. The
        # removed line takes a fraction of a percent of either sine.
        rms = 40 / math.sqrt(2)
        self.assertAlmostEqual(
            audit.band_rms(sine(256, 40, 13, 3500), PERIOD, 3, 7), rms, delta=0.01 * rms
        )
        self.assertLess(audit.band_rms(sine(256, 40, 3), PERIOD, 3, 7), 0.01 * rms)

    def test_a_drift_leaves_the_band(self):
        drift = [3000 + 2 * n for n in range(256)]
        self.assertAlmostEqual(audit.band_rms(drift, PERIOD, 3, 7), 0, places=6)

    def test_a_segment_without_a_band_bin_has_no_value(self):
        self.assertIsNone(audit.band_rms([1.0, 2.0, 3.0, 4.0], PERIOD, 3, 7))


def rpm_window(values, start_tick=1000):
    return [snapshot(start_tick + index, value) for index, value in enumerate(values)]


def accept(samples, calibration, kind, values):
    return audit.run_acceptance(
        samples, 0, len(samples) - 1, calibration, kind, values
    )


class RunAcceptanceTest(unittest.TestCase):
    def test_the_rpm_window_starts_after_the_steady_delay(self):
        steady = [LAUNCH + value for value in sine(256, 50, 13)]
        samples = rpm_window([LAUNCH + 900] * 98 + steady)
        item = accept(samples, RPM_SETTINGS, model.RegulatorKind.RPM, thresholds())
        self.assertEqual(item.steady_ticks, 256)
        rpm = [sample.rpm_raw * audit.RPM_PER_COUNT for sample in samples[98:]]
        cuts = statistics.quantiles(rpm, n=20, method="inclusive")
        self.assertEqual((item.rpm.p5, item.rpm.p95), (cuts[0], cuts[-1]))
        self.assertEqual(item.peak_above, max(rpm) - LAUNCH)
        self.assertAlmostEqual(item.mean_error, statistics.fmean(rpm) - LAUNCH)
        self.assertGreater(item.band_rpm, 25)
        self.assertIsNone(item.band_speed)
        self.assertEqual(item.verdict, "PASS")
        self.assertEqual(item.map_index, 0)

    def test_each_rpm_bound_fails_by_name(self):
        cases = {
            "P5": ([LAUNCH - WIDTH - 150] * 20 + [LAUNCH] * 80, "RPM P5"),
            "P95": ([LAUNCH + 300] * 20 + [LAUNCH] * 80, "RPM P95"),
            "peak": ([LAUNCH + 600] + [LAUNCH] * 99, "RPM peak"),
        }
        for name, (values, reason) in cases.items():
            with self.subTest(name):
                item = accept(
                    rpm_window(values), RPM_SETTINGS, model.RegulatorKind.RPM,
                    thresholds(steady=0.0, minimum=0.5),
                )
                self.assertEqual(item.verdict, "FAIL")
                self.assertTrue(any(text.startswith(reason) for text in item.reasons))

    def test_a_short_window_has_no_verdict(self):
        item = accept(
            rpm_window([LAUNCH] * 150), RPM_SETTINGS, model.RegulatorKind.RPM,
            thresholds(),
        )
        self.assertEqual(item.steady_ticks, 52)
        self.assertEqual(item.verdict, "n/a")
        self.assertIn("shorter than 1.00 s", item.reasons[0])
        self.assertIsNone(item.rpm)

    def test_the_speed_window_judges_the_error_and_both_spreads(self):
        speeds = [50.0 + value for value in sine(120, 0.3, 4)]
        samples = [
            snapshot(2000 + index, 3000, speed, control_error=round(speed * 10) - 500)
            for index, speed in enumerate(speeds)
        ]
        values = thresholds(steady=0.0, minimum=1.0)
        item = accept(samples, SPEED_SETTINGS, model.RegulatorKind.SPEED, values)
        self.assertEqual(item.verdict, "PASS")
        self.assertFalse(item.standstill)
        self.assertAlmostEqual(item.mean_error, 0.0, places=1)
        self.assertLess(item.speed.width, 1.0)
        self.assertEqual(item.rpm.width, 0)
        drifting = [
            replace(sample, control_error=sample.control_error + 8) for sample in samples
        ]
        item = accept(drifting, SPEED_SETTINGS, model.RegulatorKind.SPEED, values)
        self.assertEqual(item.verdict, "FAIL")
        self.assertTrue(item.reasons[0].startswith("mean speed error +0.80"))

    def test_a_standing_speed_hold_has_no_speed_check(self):
        # A neutral hold at a target of 0 reads a speed error and a speed
        # width of 0 by construction; only the engine-speed width judges it.
        values = thresholds(steady=0.0, minimum=1.0)
        steady = [
            snapshot(5000 + index, 3000, 0.0, control_error=0) for index in range(120)
        ]
        selected = [
            replace(sample, control_error=None, selected_target=0) for sample in steady
        ]
        for name, samples in (("implied", steady), ("selected", selected)):
            with self.subTest(name):
                item = accept(samples, SPEED_SETTINGS, model.RegulatorKind.SPEED, values)
                self.assertTrue(item.standstill)
                self.assertEqual(item.verdict, "n/a")
                self.assertEqual(
                    item.reasons,
                    ("speed checks do not apply at a standing target of 0",),
                )
        revving = [
            replace(sample, rpm_raw=sample.rpm_raw + (40 if index % 2 else 0))
            for index, sample in enumerate(steady)
        ]
        item = accept(revving, SPEED_SETTINGS, model.RegulatorKind.SPEED, values)
        self.assertEqual(item.verdict, "FAIL")
        self.assertTrue(item.reasons[0].startswith("RPM spread"))

    def test_a_hold_that_leaves_a_target_of_0_keeps_its_speed_checks(self):
        samples = [
            snapshot(6000 + index, 3000, index / 40, control_error=round(index / 4))
            for index in range(120)
        ]
        item = accept(
            samples, SPEED_SETTINGS, model.RegulatorKind.SPEED,
            thresholds(steady=0.0, minimum=1.0),
        )
        self.assertTrue(item.standstill)
        self.assertEqual(item.verdict, "FAIL")
        mean = statistics.fmean(round(index / 4) for index in range(120)) / 10
        self.assertTrue(item.reasons[0].startswith(f"mean speed error {mean:+.2f}"))

    def test_a_standing_rpm_hold_keeps_its_rpm_checks(self):
        samples = [
            replace(sample, speed_kmh=0.0) for sample in rpm_window([LAUNCH] * 120)
        ]
        item = accept(
            samples, RPM_SETTINGS, model.RegulatorKind.RPM,
            thresholds(steady=0.0, minimum=1.0),
        )
        self.assertTrue(item.standstill)
        self.assertEqual(item.verdict, "PASS")

    def test_a_speed_gap_splits_the_band_segment(self):
        samples = [
            snapshot(3000 + index, 3000, None if index == 60 else 50.0, control_error=0)
            for index in range(120)
        ]
        item = accept(
            samples, SPEED_SETTINGS, model.RegulatorKind.SPEED,
            thresholds(steady=0.0, minimum=1.0),
        )
        self.assertIsNone(item.band_speed)
        self.assertIsNotNone(item.band_rpm)

    def test_the_historical_floor_share_follows_the_stock_command(self):
        slot = audit.HoldSlot(integral_gain=2, max_trim=20, floor_command=120)
        calibration = replace(HISTORICAL, slots=(slot,) * model.SLOT_COUNT)
        # Stock command 110 + 20 exceeds the floor 120; stock 80 + 20 does not.
        self.assertEqual(
            (audit.stock_apc_command(0), audit.stock_apc_command(30)), (110, 80)
        )
        samples = [
            snapshot(4000 + index, 3000, 50.0, speed_error=0,
                     final_timing_raw=0 if index % 4 else 30)
            for index in range(100)
        ]
        item = accept(
            samples, calibration, model.RegulatorKind.SPEED,
            thresholds(steady=0.0, minimum=0.5),
        )
        self.assertEqual(item.floor_share, 0.75)


class SeriesTest(unittest.TestCase):
    def test_a_series_passes_only_with_enough_judged_runs(self):
        def run(verdict, map_index=2, standstill=False):
            return audit.Acceptance(
                map_index=map_index, kind=model.RegulatorKind.RPM,
                steady_ticks=200, standstill=standstill, verdict=verdict,
            )

        cases = {
            "three pass": ((run("PASS"),) * 3, "PASS"),
            "two judged": ((run("PASS"), run("PASS"), run("n/a")), "INCOMPLETE"),
            "one fails": ((run("PASS"), run("FAIL"), run("PASS")), "FAIL"),
        }
        for name, (items, verdict) in cases.items():
            with self.subTest(name):
                (series,) = audit.series_verdicts(items, 3)
                self.assertEqual(series.verdict, verdict)
        groups = audit.series_verdicts((run("PASS", 1), run("PASS", 2)), 1)
        self.assertEqual([item.map_index for item in groups], [1, 2])

    def test_standing_runs_form_their_own_series(self):
        items = tuple(
            audit.Acceptance(
                map_index=3, kind=model.RegulatorKind.SPEED, steady_ticks=200,
                standstill=standstill, verdict=verdict,
            )
            for standstill, verdict in (
                (False, "PASS"), (True, "FAIL"), (False, "PASS"), (False, "PASS"),
            )
        )
        road, standing = audit.series_verdicts(items, 3)
        self.assertEqual((road.standstill, road.runs, road.verdict), (False, 3, "PASS"))
        self.assertEqual(
            (standing.standstill, standing.runs, standing.verdict), (True, 1, "FAIL")
        )


class MainTest(unittest.TestCase):
    def test_the_report_needs_an_explicit_thresholds_file(self):
        samples = rpm_run()
        status, output = run_main(samples, RPM_SETTINGS)
        self.assertNotIn("acceptance", output)
        capture = audit.Capture(Path("hold.mlg"), "0" * 64, tuple(samples))
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "thresholds.toml"
            path.write_text(THRESHOLDS.format(steady=0.0, minimum=0.05))
            with (
                mock.patch.object(audit, "read_calibration", return_value=RPM_SETTINGS),
                mock.patch.object(audit, "read_capture", return_value=capture),
                contextlib.redirect_stdout(io.StringIO()) as stream,
            ):
                judged = audit.main([
                    "--image", "image.bin", "--thresholds", str(path), "hold.mlg",
                ])
        report = stream.getvalue()
        self.assertEqual(judged, status)
        self.assertIn("acceptance steady_ticks=", report)
        self.assertIn("standstill=yes", report)
        self.assertIn("series map=1 kind=RPM standstill=yes runs=1", report)
        self.assertIn("verdict=INCOMPLETE (repeats 3)", report)


if __name__ == "__main__":
    unittest.main()
