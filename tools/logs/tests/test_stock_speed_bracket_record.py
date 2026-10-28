from pathlib import Path
import tomllib
import unittest

import pytest

from tools.logs import rolling_launch_audit as audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
LOGS = ROOT / "tmp" / "logs-09-22"
IMAGE = ROOT / "tmp" / "1JK08A-tune-v3-1.bin"
KEY = "stock_speed_bracket_2026_09_22"
CAPTURES = "schema2_profile5_captures_2026_09_22"
ROLLING_LAUNCH_RECORD = ("rolling_launch", "map_2_vehicle_2026_09_22")
# Figures whose stock-frame value spans the value the published coordinate
# gave. The rolling-launch record test compares the figures that engine speed
# does not enter.
WIDENED = (
    "activation_rpm_range",
    "activation_captured_rpm_native",
    "activation_captured_rpm",
    "activation_cut_rpm",
    "activation_restore_rpm",
    "activation_capture_records",
    "activation_full_mask_rpm",
    "activation_exit_records",
    "activation_active_ticks_bound",
    "activation_release_exit_bound_ms",
)


def spans(outer, inner) -> bool:
    """Return whether one bound encloses another; an empty bound is open."""
    if not outer:
        return True
    return bool(inner) and outer[0] <= inner[0] and inner[-1] <= outer[-1]


class StockSpeedBracketRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            registry = tomllib.load(source)
        section, name = ROLLING_LAUNCH_RECORD
        cls.rolling_launch = registry[section][name]
        cls.record = registry["can_telemetry"][KEY]
        cls.captures = registry["can_telemetry"][CAPTURES]

    def test_record_sums_its_captures(self):
        record = self.record
        self.assertEqual(record["capture_registry"], f"can_telemetry.{CAPTURES}")
        self.assertTrue((ROOT / record["tool"]).is_file())
        for key in (
            "capture_snapshot_count",
            "capture_inside_count",
            "capture_maximum_excursion_counts",
        ):
            self.assertEqual(len(record[key]), len(self.captures), key)
        self.assertEqual(record["snapshot_count"], sum(record["capture_snapshot_count"]))
        self.assertEqual(record["inside_count"], sum(record["capture_inside_count"]))
        self.assertEqual(
            record["maximum_excursion_counts"],
            max(record["capture_maximum_excursion_counts"]),
        )

    def test_audit_margin_exceeds_the_recorded_excursion(self):
        margin = audit.STOCK_RPM_MARGIN
        self.assertGreater(margin, self.record["maximum_excursion_counts"])

    # The inside and excursion figures compare the stock frames with the
    # coordinate that the recorded profile published, which the recordings
    # converted to the current profile no longer carry; they remain the record.
    @pytest.mark.slow
    @unittest.skipUnless(LOGS.is_dir(), "road captures are local and untracked")
    def test_captures_reproduce_the_snapshot_counts(self):
        paths = [
            LOGS / Path(row["capture_name"]).with_suffix(".mlg").name
            for row in self.captures
        ]
        missing = [path.name for path in paths if not path.is_file()]
        if missing:
            self.skipTest(f"missing captures: {', '.join(missing)}")
        record = self.record
        for index, (row, path) in enumerate(zip(self.captures, paths)):
            with self.subTest(capture=path.name):
                capture = audit.read_capture(path)
                self.assertEqual(capture.sha256, row["converted_mlg_sha256"])
                self.assertEqual(
                    len(capture.samples), record["capture_snapshot_count"][index]
                )

    @pytest.mark.slow
    def test_stock_frame_audit_spans_the_recorded_rolling_launch_result(self):
        published = self.rolling_launch
        path = LOGS / Path(published["capture_name"]).with_suffix(".mlg").name
        if not (path.is_file() and IMAGE.is_file()):
            self.skipTest("road captures are local and untracked")
        capture = audit.read_capture(path)
        self.assertEqual(capture.sha256, published["converted_mlg_sha256"])
        stock = audit.audit_capture(
            capture,
            audit.load_calibration(IMAGE),
            selected_map=published["selected_map"],
        )
        self.assertTrue(all(stock["activation_captured_rpm_native"]))
        for key in WIDENED:
            for index, (outer, inner) in enumerate(zip(stock[key], published[key])):
                with self.subTest(key=key, activation=index):
                    self.assertTrue(spans(outer, inner), (outer, inner))


if __name__ == "__main__":
    unittest.main()
