from pathlib import Path
import tomllib
import unittest

from tools.can_dashboard import recording
from tools.logs import rolling_launch_audit as audit


ROOT = Path(__file__).resolve().parents[3]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
LOGS_README = ROOT / "tools" / "logs" / "README.md"
LOGS = ROOT / "tmp" / "logs-09-22"
IMAGE = ROOT / "tmp" / "1JK08A-tune-v3-1.bin"
KEY = "stock_speed_bracket_2026_09_22"
CAPTURES = "schema2_profile5_captures_2026_09_22"
ROLLING_LAUNCH_CAPTURE = "11-map-2-rl.trc"
ROLLING_LAUNCH_MAP = 2
RPM_PER_COUNT = recording.MLG_CALIBRATIONS["rpm_raw"].factor
# Figures whose stock-frame value spans the value the published coordinate
# gives, and figures that engine speed does not enter.
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
SPEED_FREE = (
    "activation_count",
    "activation_start_seconds",
    "activation_full_mask_cycles",
    "activation_apc_outside_bound_records",
    "activation_release_clear_records",
    "full_mask_record_count",
    "identity_count",
)


def _normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def excursions(path: Path) -> tuple[str, list[int]]:
    """Return the capture digest and how far each coordinate leaves its pair."""
    published = audit.read_capture(path)
    words = {sample.tick: sample.rpm_raw for sample in published.samples}
    stock = audit.read_capture(path, stock_speed=True)
    values = []
    for sample, (low, high) in zip(
        stock.samples, audit.stock_speed_pairs(stock.samples)
    ):
        word = words.get(sample.tick)
        if word is not None:
            values.append(max(low - word, word - high, 0))
    return published.sha256, values


def spans(outer, inner) -> bool:
    """Return whether one bound encloses another; an empty bound is open."""
    if not outer:
        return True
    return bool(inner) and outer[0] <= inner[0] and inner[-1] <= outer[-1]


class StockSpeedBracketRecordTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            registry = tomllib.load(source)["can_telemetry"]
        cls.record = registry[KEY]
        cls.captures = registry[CAPTURES]

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
        self.assertIn(
            f"{record['inside_count']} of {record['snapshot_count']} snapshots",
            record["result"],
        )
        excursion = record["maximum_excursion_counts"]
        self.assertIn(
            f"at most {excursion} counts, {excursion * RPM_PER_COUNT:g} RPM,",
            record["result"],
        )

    def test_audit_margin_exceeds_the_recorded_excursion(self):
        margin = audit.STOCK_RPM_MARGIN
        self.assertGreater(margin, self.record["maximum_excursion_counts"])
        self.assertIn(
            f"widened by {margin} counts, {margin * RPM_PER_COUNT:g} RPM, beyond "
            f"the excursion that registry entry `can_telemetry.{KEY}` records",
            _normalized(LOGS_README),
        )

    @unittest.skipUnless(LOGS.is_dir(), "road captures are local and untracked")
    def test_captures_reproduce_the_record(self):
        paths = [LOGS / row["capture_name"] for row in self.captures]
        missing = [path.name for path in paths if not path.is_file()]
        if missing:
            self.skipTest(f"missing captures: {', '.join(missing)}")
        record = self.record
        for index, (row, path) in enumerate(zip(self.captures, paths)):
            with self.subTest(capture=path.name):
                digest, values = excursions(path)
                self.assertEqual(digest, row["capture_sha256"])
                self.assertEqual(len(values), record["capture_snapshot_count"][index])
                self.assertEqual(
                    values.count(0), record["capture_inside_count"][index]
                )
                self.assertEqual(
                    max(values), record["capture_maximum_excursion_counts"][index]
                )

    @unittest.skipUnless(
        (LOGS / ROLLING_LAUNCH_CAPTURE).is_file() and IMAGE.is_file(),
        "road captures are local and untracked",
    )
    def test_stock_frame_audit_spans_the_published_rolling_launch_result(self):
        path = LOGS / ROLLING_LAUNCH_CAPTURE
        calibration = audit.load_calibration(IMAGE)
        published = audit.audit_capture(
            audit.read_capture(path), calibration, selected_map=ROLLING_LAUNCH_MAP
        )
        stock = audit.audit_capture(
            audit.read_capture(path, stock_speed=True),
            calibration,
            selected_map=ROLLING_LAUNCH_MAP,
        )
        self.assertEqual(published["engine_speed_source"], "0xFFFF11F4")
        self.assertEqual(stock["engine_speed_source"], "0x180")
        self.assertTrue(all(stock["activation_captured_rpm_native"]))
        for key in WIDENED:
            for index, (outer, inner) in enumerate(zip(stock[key], published[key])):
                with self.subTest(key=key, activation=index):
                    self.assertTrue(spans(outer, inner), (outer, inner))
        for key in SPEED_FREE:
            with self.subTest(key=key):
                self.assertEqual(stock[key], published[key])


if __name__ == "__main__":
    unittest.main()
