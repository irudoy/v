from dataclasses import fields
from pathlib import Path
import statistics
import tomllib
import unittest

from tools.logs import torque_scale_audit as audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
CAN = ROOT / "defs" / "JK08A.can.md"
README = ROOT / "tools" / "logs" / "README.md"
STOCK_ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
LOGS = ROOT / "tmp" / "logs-09-22"
IMAGE = ROOT / "tmp" / "1JK08A-tune-v3-1.bin"
KEY = "engine_torque_scale.vehicle_2026_09_22"
COMPATIBLE = "compatible"
EXCLUDED = "excluded"
NOT_SUPPORTED = "not_supported"


def _lookup(registry, dotted):
    node = registry
    for part in dotted.split("."):
        node = node[part]
    return node


def _number(value):
    return f"{value:,}" if isinstance(value, int) and value >= 1000 else f"{value}"


def _range(low, high, unit=""):
    return f"{low}..{high}{unit}"


class TorqueScaleRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        cls.result = _lookup(cls.registry, KEY)
        cls.status = cls.result["term_status"]
        cls.session = _lookup(cls.registry, cls.result["session"])
        cls.captures = {
            row["capture_name"]: row for row in _lookup(cls.registry, cls.result["capture_registry"])
        }
        cls.published = " ".join(CAN.read_text(encoding="utf-8").split())
        cls.readme = " ".join(README.read_text(encoding="utf-8").split())

    def test_record_belongs_to_the_registered_drive(self):
        result = self.result
        self.assertTrue((ROOT / result["audit_tool"]).is_file())
        self.assertEqual(result["recorded_on"], self.session["recorded_on"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        self.assertEqual(self.session["capture_registry"], result["capture_registry"])
        named = (
            list(zip(result["capture_name"], result["capture_sha256"]))
            + list(zip(result["remainder_capture_name"], result["remainder_capture_sha256"]))
            + [(result["cruise_capture_name"], result["cruise_capture_sha256"])]
        )
        for name, digest in named:
            self.assertEqual(self.captures[name]["capture_sha256"], digest, name)
        for name in result["remainder_capture_name"]:
            self.assertTrue(name.endswith(".trc"), name)
        self.assertLessEqual(set(result["segment_capture_name"]), set(result["capture_name"]))

    def test_code_constants_match_the_tool_and_the_stock_image(self):
        result = self.result
        base = audit.BaseTerm.from_image(STOCK_ROM)
        self.assertEqual(result["base_axis_rpm_raw"], list(base.axis))
        self.assertEqual(result["base_table_raw"], list(base.table))
        self.assertEqual(result["bfs_term_numerator"], base.bfs_numerator)
        self.assertEqual(result["bfs_term_scaler"], base.bfs_scaler)
        self.assertEqual(result["base_table_address"], audit.BASE_TABLE_ADDRESS)
        self.assertEqual(result["base_axis_address"], audit.BASE_AXIS_ADDRESS)
        self.assertEqual(result["bfs_term_numerator_address"], audit.BFS_TERM_NUMERATOR_ADDRESS)
        self.assertEqual(result["bfs_term_scaler_address"], audit.BFS_SCALER_ADDRESS)
        self.assertEqual(result["actual_torque_frame"], audit.ACTUAL_TORQUE_ID)
        self.assertEqual(result["can_torque_divisor"], audit.CAN_TORQUE_DIVISOR)
        self.assertEqual(result["can_torque_zero"], audit.CAN_TORQUE_ZERO)
        packing = (
            f"word = clamp(trunc0(source / {audit.CAN_TORQUE_DIVISOR}) + {audit.CAN_TORQUE_ZERO}, 0, 4094)"
        )
        self.assertIn(packing, self.published)
        self.assertIn(f"`{result['net_torque_address']:#010X}`".replace("0X", "0x"), self.published)

    def test_gear_speeds_scale_the_locked_gear(self):
        result = self.result
        self.assertEqual(result["gear_ratios"], list(audit.RE5R05A_RATIOS.values()))
        self.assertEqual(result["locked_gear"], audit.LOCKED_GEAR)
        locked_ratio = result["gear_ratios"][result["locked_gear"] - 1]
        expected = audit.gear_speed_ratios(result["locked_rpm_per_kmh"])
        for gear, value in zip(audit.RE5R05A_RATIOS, result["gear_rpm_per_kmh"]):
            self.assertAlmostEqual(value, expected[gear], delta=0.002)
            self.assertAlmostEqual(
                value, result["locked_rpm_per_kmh"] * audit.RE5R05A_RATIOS[gear] / locked_ratio, delta=0.002)

    def test_vehicle_constants_match_the_tool(self):
        result = self.result
        self.assertEqual(
            result["vehicle_nominal"],
            {field.name: getattr(audit.NOMINAL, field.name) for field in fields(audit.Vehicle)},
        )
        self.assertEqual(result["vehicle_box"], {name: list(ends) for name, ends in audit.VEHICLE_BOX.items()})
        for name, (low, high) in result["vehicle_box"].items():
            self.assertLessEqual(low, result["vehicle_nominal"][name])
            self.assertLessEqual(result["vehicle_nominal"][name], high)
            self.assertIn(name, result["sensitivity_ratio"])

    def test_segments_points_and_ratios_are_consistent(self):
        result = self.result
        count = len(result["segment_capture_name"])
        for key in ("segment_start_seconds", "segment_end_seconds", "segment_point_count",
                    "segment_gears", "ratio_by_segment"):
            self.assertEqual(len(result[key]), count, key)
        self.assertEqual(sum(result["segment_point_count"]), result["point_count"])
        for start, end in zip(result["segment_start_seconds"], result["segment_end_seconds"]):
            self.assertGreaterEqual(end - start, audit.MIN_SEGMENT_SECONDS)
        self.assertAlmostEqual(result["ratio_nominal"], statistics.median(result["ratio_by_segment"]), delta=0.001)
        low, high = result["ratio_box"]
        self.assertLess(low, result["ratio_nominal"])
        self.assertLess(result["ratio_nominal"], high)
        self.assertLessEqual(sum(result["band_point_count"]), result["point_count"])
        for key in ("band_gear", "band_rpm_low", "band_ratio"):
            self.assertEqual(len(result[key]), len(result["band_point_count"]), key)
        for low, high in result["sensitivity_ratio"].values():
            self.assertGreaterEqual(min(low, high), result["ratio_box"][0])
            self.assertLessEqual(max(low, high), result["ratio_box"][1])

    def test_candidate_status_follows_the_bounds(self):
        result = self.result
        status = self.status
        coast_low, coast_high = result["coast_grade_percent_range"]
        pair_low = min(low for low, _ in result["gear_pair_scale_box"])
        pair_high = max(high for _, high in result["gear_pair_scale_box"])
        self.assertEqual(result["candidate_scales_nm_per_raw"], list(audit.CANDIDATE_SCALES_NM))
        for scale, nominal, (low, high), grades in zip(
            result["candidate_scales_nm_per_raw"],
            result["candidate_median_grade_percent"],
            result["candidate_median_grade_percent_box"],
            result["candidate_segment_grade_percent"],
        ):
            self.assertEqual(len(grades), len(result["segment_capture_name"]))
            self.assertAlmostEqual(nominal, statistics.median(grades), delta=0.01)
            self.assertLessEqual(low, nominal)
            self.assertLessEqual(nominal, high)
            verdict = status["scale_" + f"{scale}".replace(".", "_")]
            if verdict == COMPATIBLE:
                self.assertLessEqual(low, 0.0)
                self.assertGreaterEqual(high, 0.0)
                self.assertTrue(pair_low <= scale <= pair_high)
            elif verdict == EXCLUDED:
                self.assertTrue(high < coast_low or low > coast_high)
                self.assertTrue(high < 0.0 or low > 0.0)
            elif verdict == NOT_SUPPORTED:
                self.assertTrue(high < 0.0 or low > 0.0)
                self.assertTrue(scale > pair_high or scale < pair_low)
            else:
                self.fail(verdict)
        low, _ = result["gross_median_grade_percent_box"]
        self.assertGreater(low, 0.0)
        self.assertEqual(status["gross_state_as_flywheel_torque"], NOT_SUPPORTED)
        self.assertEqual(status["net_word_replay"], "pass")
        self.assertLess(abs(result["word_gap_median_raw"]), audit.CAN_TORQUE_DIVISOR)
        for (low, high), nominal in zip(result["gear_pair_scale_box"], result["gear_pair_scale_nominal"]):
            self.assertLessEqual(low, nominal)
            self.assertLessEqual(nominal, high)

    def test_published_text_reads_the_registry(self):
        result = self.result
        published = self.published
        self.assertIn(f"`{KEY}`", published)
        self.assertIn("`tools/logs/torque_scale_audit.py`", published)
        self.assertIn(f"{result['point_count']} converter-coupled full-pedal points", published)
        self.assertIn(f"in {len(result['segment_capture_name'])} segments", published)
        self.assertIn(f"remainder of {result['net_remainder_raw']} raw", published)
        self.assertIn(f"{_number(result['remainder_sample_count'])} TRC samples", published)
        self.assertIn(f"is {result['ratio_nominal']:.3f} of net torque", published)
        self.assertIn(f"and {_range(*result['ratio_box'])} over the box", published)
        labels = [f"net at `{scale} Nm`" for scale in result["candidate_scales_nm_per_raw"]]
        rows = zip(labels, result["candidate_median_grade_percent"], result["candidate_median_grade_percent_box"])
        for label, nominal, (low, high) in rows:
            self.assertIn(f"| {label} | {nominal} percent | {_range(low, high)} percent |", published)
        low, high = result["gross_median_grade_percent_box"]
        gross = result["gross_median_grade_percent"]
        self.assertIn(f"| gross state at `0.1 Nm` | {gross} percent | {_range(low, high)} percent |", published)
        self.assertIn(f"median uphill grade of {gross} percent", published)
        self.assertIn(
            f"The {result['coast_window_count']} neutral-coast windows imply grades of "
            f"{_range(*result['coast_grade_percent_range'])} percent", published)
        pair_low = min(low for low, _ in result["gear_pair_scale_box"])
        pair_high = max(high for _, high in result["gear_pair_scale_box"])
        self.assertIn(
            f"spans {pair_low}..{pair_high} Nm per raw count over the six gear pairs", published)
        self.assertEqual(len(result["gear_pair_segment"]), 6)

    def test_readme_states_the_tool_thresholds(self):
        readme = self.readme
        self.assertIn("## JK08A engine-torque scale audit", README.read_text(encoding="utf-8"))
        for text in (
            f"at {audit.LOCKED_MIN_SPEED_KMH:g} km/h or more",
            f"within {100 * audit.LOCKED_RATIO_TOLERANCE:g} percent of the window median",
            f"APP1 of {audit.REMAINDER_MIN_APP1} raw or more, a timing command of {audit.REMAINDER_MIN_TIMING_RAW} or more",
            f"APP1 at {audit.FULL_PEDAL_APP1} raw or more that lasts at least {audit.MIN_SEGMENT_SECONDS:g} s",
            f"Points lie {audit.POINT_STEP_SECONDS:g} s apart and use line fits over {audit.FIT_HALF_SECONDS:g} s",
            f"speed ratio of {audit.COUPLING_RANGE[0]:.2f}..{audit.COUPLING_RANGE[1]:.2f} in one gear",
            f"a timing command of {audit.MIN_TIMING_RAW} or more, no fuel inhibit, and {audit.MIN_POINT_RPM:g} RPM or more",
            f"faster than {-audit.SHIFT_DROP_RPM_PER_S:g} RPM/s marks a shift",
            f"from {audit.SHIFT_GUARD_SECONDS[0]:g} s before to {audit.SHIFT_GUARD_SECONDS[1]:g} s after it",
            f"all {2 ** len(audit.VEHICLE_BOX)} corners of the box",
        ):
            self.assertIn(text, readme)

    @unittest.skipUnless(LOGS.is_dir() and IMAGE.is_file(), "road captures are local and untracked")
    def test_audit_reproduces_the_record(self):
        result = self.result
        missing = [name for name in result["capture_name"] + result["remainder_capture_name"]
                   if not (LOGS / name).is_file()]
        if missing:
            self.skipTest(f"missing captures: {', '.join(missing)}")
        self.assertEqual(audit.sha256_file(IMAGE), result["image_sha256"])
        output = audit.audit(
            IMAGE,
            LOGS / result["cruise_capture_name"],
            [LOGS / name for name in result["capture_name"]],
            [LOGS / name for name in result["remainder_capture_name"]],
        )
        for key, value in tomllib.loads("\n".join(audit.result_lines(output))).items():
            self.assertEqual(result[key], value, key)


if __name__ == "__main__":
    unittest.main()
