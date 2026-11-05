"""Sample stock frames retain their decoded values and units in MLG/replay."""

import math
from pathlib import Path
import tempfile
import unittest

from tools.can_dashboard import replay, stock
from tools.can_dashboard.model import DashboardModel, DemoGenerator, FrameRecord
from tools.can_dashboard.recording import TelemetryMlgRecorder
from tools.can_dashboard.tests.test_recording import feed_group, read_f32_records


class StockRecordingTest(unittest.TestCase):
    def test_sample_frames_record_gears_speeds_and_shift_audit_operands(self):
        dashboard = DashboardModel("tuning", 0x6F0, 1)
        frames = (
            (0x174, "3AC3BC3461000000"),
            (0x176, "032007D0000000"),
            (0x177, "000002002048"),
            (0x180, "1F40320321000000"),
            (0x160, "32232300000000"),
            (0x284, "00000000350A0000"),
        )
        for can_id, payload in frames:
            dashboard.process_frame(FrameRecord(can_id, bytes.fromhex(payload)), now=0)
        feed_group(dashboard, DemoGenerator().group(1), 0.01)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drive.mlg"
            recorder = TelemetryMlgRecorder(path, "tuning", 1700000000)
            recorder.append(dashboard, 0.01)
            recorder.close()
            _header, fields, records = read_f32_records(path)
            values = records[0]
            expected = {
                "Gear": 4, "TCM target gear": 3,
                "TCM word A": 940, "TCM word B": 956, "TCM status": 3,
                "TCM output speed": 800, "TCM turbine speed": 2000,
                "TCM output / turbine ratio": 0.4,
                "TCM gear phase": 2, "TCM reduction byte": 32, "TCM shift code": 9,
                "Vehicle speed 0x284": 135.78,
                "CAN actual torque word": 800, "CAN pre-limiter request word": 801,
                "CAN limited request word": 802, "CAN parallel torque word": 803,
            }
            for label, value in expected.items():
                with self.subTest(field=label):
                    self.assertAlmostEqual(values[label], value, places=4)
            specs = {binding.spec.name: binding.spec for binding in recorder.bindings}
            self.assertEqual(specs["Gear"].units, "gear")
            for field in stock.FIELDS:
                self.assertEqual(specs[field.label].units, field.unit)
            restored = DashboardModel("tuning", 0x6F0, 1)
            timeline = replay.load_timeline(path, 0x6F0)
            restored.process_record(timeline.item(0, 1), now=1)
            for field in stock.FIELDS:
                self.assertAlmostEqual(getattr(restored, field.key), getattr(dashboard, field.key), places=4)

    def test_unavailable_and_unreceived_values_are_nan_not_zero(self):
        dashboard = DashboardModel("tuning", 0x6F0, 1)
        demo = DemoGenerator()
        feed_group(dashboard, demo.group(1), 0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drive.mlg"
            recorder = TelemetryMlgRecorder(path, "tuning", 1700000000)
            recorder.append(dashboard, 0)
            for can_id, data in (
                (0x174, bytes.fromhex("000000AA00000000")),
                (0x176, bytes(7)),
                (0x284, bytes.fromhex("00000000FFFF0000")),
                (0x180, bytes.fromhex("0000FFFFFF000000")),
            ):
                dashboard.process_frame(FrameRecord(can_id, data), now=0.01)
            feed_group(dashboard, demo.group(2), 0.01)
            recorder.append(dashboard, 0.01)
            recorder.close()
            values = read_f32_records(path)[2]
            for field in stock.FIELDS:
                self.assertTrue(math.isnan(values[0][field.label]), field.label)
            for label in ("Gear", "TCM target gear", "TCM output / turbine ratio",
                          "Vehicle speed 0x284", "CAN actual torque word", "CAN pre-limiter request word"):
                self.assertTrue(math.isnan(values[1][label]), label)
