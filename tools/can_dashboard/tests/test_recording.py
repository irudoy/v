import math
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

from tools.can_dashboard import model, recording
from tools.logs import mlvlg


try:
    from tools.can_dashboard import app
except ImportError:  # pragma: no cover - Tk is unavailable
    app = None


def feed_group(dashboard, group, base_time):
    snapshot = None
    for index, frame in enumerate(group):
        result = dashboard.process_frame(
            frame,
            now=base_time + index * 0.00025,
        )
        if result is not None:
            snapshot = result
    return snapshot


def read_f32_records(path):
    data = Path(path).read_bytes()
    header = struct.unpack(">6sHIIIHH", data[:mlvlg.MLG_HEADER_SIZE])
    record_length = header[-2]
    field_count = header[-1]
    offset = mlvlg.MLG_HEADER_SIZE
    fields = []
    for _ in range(field_count):
        descriptor = data[offset : offset + mlvlg.MLG_FIELD_SIZE]
        fields.append(
            (
                descriptor[0],
                descriptor[1:35].split(b"\x00", 1)[0].decode("ascii"),
            )
        )
        offset += mlvlg.MLG_FIELD_SIZE

    records = []
    while offset < len(data):
        payload = data[offset + 4 : offset + 4 + record_length]
        values = {}
        value_offset = 0
        for field_type, name in fields:
            format_string = mlvlg.FIELD_STRUCTS[field_type]
            size = struct.calcsize(format_string)
            values[name] = struct.unpack(
                format_string,
                payload[value_offset : value_offset + size],
            )[0]
            value_offset += size
        records.append(values)
        offset += 4 + record_length + 1
    return header, fields, records


class TelemetryMlgRecorderTest(unittest.TestCase):
    def test_initialization_error_removes_temporary_file(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "invalid.mlg"
            with self.assertRaisesRegex(
                mlvlg.MlvlgError,
                "timestamp is outside",
            ):
                recording.TelemetryMlgRecorder(
                    output,
                    "tuning",
                    0x1_0000_0000,
                )
            self.assertEqual(list(Path(directory).iterdir()), [])

    def test_empty_forced_recording_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "existing.mlg"
            output.write_bytes(b"existing recording")
            recorder = recording.TelemetryMlgRecorder(
                output,
                "tuning",
                1_776_000_000,
                force=True,
            )
            summary = recorder.close()

            self.assertEqual(output.read_bytes(), b"existing recording")
            self.assertTrue(summary.output_existed)
            self.assertEqual(summary.event_records, 0)
            self.assertEqual(summary.output_size, len(b"existing recording"))

    def test_records_complete_schema_and_stock_context(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "telemetry.mlg"
            recorder = recording.TelemetryMlgRecorder(
                output,
                "tuning",
                1_776_000_000.25,
            )
            for tick in range(1, 9):
                elapsed = (tick - 1) * model.BASE_TICK_SECONDS
                for frame in generator.stock_context(tick, elapsed):
                    dashboard.process_frame(frame, now=elapsed)
                snapshot = feed_group(
                    dashboard,
                    generator.group(tick, elapsed),
                    elapsed,
                )
                self.assertIsNotNone(snapshot)
                recorder.append(dashboard, elapsed)
            summary = recorder.close()
            validation = mlvlg.validate_mlg(output)
            header, fields, records = read_f32_records(output)

        self.assertEqual(summary.event_records, 8)
        self.assertEqual(summary.bridge_records, 0)
        self.assertEqual(validation.data_records, 8)
        self.assertEqual(validation.fields, 81)
        self.assertEqual(header[2], 1_776_000_000)
        names = [name for _, name in fields]
        self.assertIn("Vehicle speed", names)
        self.assertIn("Stock CAN RPM", names)
        self.assertIn("Intake CVTC target", names)
        self.assertIn("Exhaust CVTC target", names)
        self.assertIn("Knock timing state", names)
        self.assertIn("High-detonation surface selected", names)
        self.assertNotIn("gps_lat", names)
        self.assertNotIn("gps_lon", names)
        self.assertEqual([name for name in names if "*" in name], [])
        cvtc_specs = {
            binding.spec.name: binding.spec
            for binding in recorder.bindings
            if binding.spec.name in {
                "Intake CVTC actual B1",
                "Intake CVTC target",
                "Exhaust CVTC target",
            }
        }
        self.assertEqual(set(cvtc_specs), {
            "Intake CVTC actual B1",
            "Intake CVTC target",
            "Exhaust CVTC target",
        })
        for spec in cvtc_specs.values():
            self.assertEqual(spec.scale, 0.5)
            self.assertEqual(spec.transform, -128.0)
            self.assertEqual(spec.units, "degCA*")
        knock_specs = {
            binding.spec.name: binding.spec
            for binding in recorder.bindings
            if binding.spec.name in {
                "Knock timing state",
                "High-detonation surface selected",
            }
        }
        self.assertEqual(knock_specs["Knock timing state"].scale, 1 / 256)
        self.assertEqual(knock_specs["Knock timing state"].units, "state")
        self.assertEqual(knock_specs["Knock timing state"].digits, 3)
        self.assertEqual(
            knock_specs["High-detonation surface selected"].display_style,
            mlvlg.MLG_ON_OFF,
        )
        self.assertEqual(
            records[-1]["Intake CVTC actual B1"],
            dashboard.raw["intake_cvtc_actual_b1_raw"],
        )
        self.assertEqual(
            records[-1]["Intake CVTC target"],
            dashboard.raw["intake_cvtc_target_raw"],
        )
        self.assertEqual(
            records[-1]["Exhaust CVTC target"],
            dashboard.raw["exhaust_cvtc_target_raw"],
        )
        self.assertEqual(
            records[-1]["Knock timing state"],
            dashboard.raw["knock_timing_state_raw"],
        )
        self.assertEqual(
            records[-1]["High-detonation surface selected"],
            0,
        )
        self.assertGreater(records[-1]["Stock CAN RPM"], 0)

    def test_inserts_hold_last_records_for_timestamp_wrap_detection(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        feed_group(dashboard, generator.group(1), 0.0)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "gaps.mlg"
            recorder = recording.TelemetryMlgRecorder(
                output,
                "tuning",
                1_776_000_000,
            )
            recorder.append(dashboard, 0.0)
            recorder.append(dashboard, 1.0)
            summary = recorder.close()
            validation = mlvlg.validate_mlg(output)

        self.assertEqual(summary.event_records, 2)
        self.assertEqual(summary.bridge_records, 3)
        self.assertEqual(validation.data_records, 5)

    def test_validation_mismatch_is_a_handled_mlvlg_error(self):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        feed_group(dashboard, generator.group(1), 0.0)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "mismatch.mlg"
            recorder = recording.TelemetryMlgRecorder(
                output,
                "tuning",
                1_776_000_000,
            )
            recorder.append(dashboard, 0.0)
            temporary = recorder.temporary
            mismatch = mlvlg.ValidationSummary(
                fields=len(recorder.fields) + 1,
                record_length=recorder._writer.record_length,
                data_records=recorder._writer.data_records,
                marker_records=0,
            )
            with mock.patch.object(
                recording.mlvlg,
                "validate_mlg",
                return_value=mismatch,
            ), self.assertRaisesRegex(
                mlvlg.MlvlgError,
                "field count differs",
            ):
                recorder.close()

            self.assertFalse(output.exists())
            self.assertFalse(temporary.exists())


class MlgCalibrationGateTest(unittest.TestCase):
    """Bind recorded channel values to the values the dashboard displays."""

    RAW_PROBES = (0, 1, 37, 64, 128, 200, 255, 1024, 25_600, 27_069, 65_535)

    def setUp(self):
        self.bindings = recording.build_bindings("tuning")

    def test_every_declared_calibration_reaches_a_recorded_channel(self):
        calibrated = {
            binding.source
            for binding in self.bindings
            if binding.source in recording.MLG_CALIBRATIONS
        }
        self.assertEqual(calibrated, set(recording.MLG_CALIBRATIONS))

    def test_channel_values_equal_dashboard_engineering_values(self):
        for binding in self.bindings:
            calibration = recording.MLG_CALIBRATIONS.get(binding.source)
            if calibration is None:
                self.assertEqual(binding.spec.scale, 1.0)
                self.assertEqual(binding.spec.transform, 0.0)
                continue
            spec = binding.spec
            for raw in self.RAW_PROBES:
                with self.subTest(field=spec.name, raw=raw):
                    # MegaLogViewer evaluates (raw + transform) * scale.
                    self.assertAlmostEqual(
                        (raw + spec.transform) * spec.scale,
                        calibration.apply(raw),
                        places=6,
                    )

    def test_channel_names_carry_no_candidate_marker(self):
        for binding in self.bindings:
            with self.subTest(field=binding.spec.name):
                self.assertNotIn("*", binding.spec.name)

    @unittest.skipIf(app is None, "Tk is unavailable")
    def test_candidate_marker_matches_the_dashboard_units(self):
        metrics = {metric.key: metric for metric in app.HERO_METRICS}
        for _title, panel in app.PANELS + app.EXTENDED_PANELS:
            metrics.update({metric.key: metric for metric in panel})
        compared = 0
        for binding in self.bindings:
            calibration = recording.MLG_CALIBRATIONS.get(binding.source)
            key = (
                calibration.target
                if calibration is not None
                else binding.source
            )
            metric = metrics.get(key)
            if metric is None:
                continue
            compared += 1
            with self.subTest(field=binding.spec.name):
                self.assertEqual(
                    "*" in binding.spec.units,
                    "*" in metric.unit,
                )
        self.assertGreater(compared, 50)


if __name__ == "__main__":
    unittest.main()
