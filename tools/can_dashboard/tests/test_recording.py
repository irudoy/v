import contextlib
import errno
import math
from pathlib import Path
import struct
import tempfile
import unittest
from unittest import mock

from tools.can_dashboard import model, presentation, recording
from tools.logs import can_telemetry
from tools.logs import mlvlg


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
    def one_record(self, output):
        generator = model.DemoGenerator()
        dashboard = model.DashboardModel("tuning", 0x6F0, 1)
        feed_group(dashboard, generator.group(1), 0.0)
        recorder = recording.TelemetryMlgRecorder(output, "tuning", 1_776_000_000)
        recorder.append(dashboard, 0.0)
        recorder._stream.flush()
        return recorder, dashboard

    def test_append_failure_stops_further_writes_and_retains_data(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "full-disk.mlg"
            recorder, dashboard = self.one_record(output)
            try:
                with mock.patch.object(
                    recorder._writer, "write", side_effect=OSError(errno.ENOSPC, "disk full")
                ), self.assertRaises(OSError):
                    recorder.append(dashboard, 0.01)
                with self.assertRaisesRegex(ValueError, "closed"):
                    recorder.append(dashboard, 0.02)
                recorder.abort()
                self.assertFalse(output.exists())
                self.assertEqual(mlvlg.validate_mlg(recorder.temporary).data_records, 1)
            finally:
                recorder.abort()

    def test_abort_preserves_the_recorded_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, _dashboard = self.one_record(Path(directory) / "aborted.mlg")
            try:
                recorder.abort()
                self.assertTrue(recorder.temporary.exists())
                self.assertEqual(mlvlg.validate_mlg(recorder.temporary).data_records, 1)
            finally:
                recorder.abort()

    def test_encoding_failure_stops_recording_without_losing_previous_data(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, dashboard = self.one_record(Path(directory) / "encoding-error.mlg")
            try:
                with mock.patch.object(
                    recorder._writer, "write", side_effect=mlvlg.MlvlgError("invalid record")
                ), self.assertRaises(mlvlg.MlvlgError):
                    recorder.append(dashboard, 0.01)
                with self.assertRaisesRegex(ValueError, "closed"):
                    recorder.append(dashboard, 0.02)
                self.assertEqual(mlvlg.validate_mlg(recorder.temporary).data_records, 1)
            finally:
                recorder.abort()

    def test_destination_conflict_keeps_both_files(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "conflict.mlg"
            recorder, _dashboard = self.one_record(output)
            try:
                output.write_bytes(b"another recording")
                with self.assertRaises(FileExistsError):
                    recorder.close()
                recorder.abort()
                self.assertEqual(output.read_bytes(), b"another recording")
                self.assertEqual(mlvlg.validate_mlg(recorder.temporary).data_records, 1)
            finally:
                recorder.abort()

    def test_flush_failure_keeps_recorded_data_after_abort(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, _dashboard = self.one_record(Path(directory) / "flush-error.mlg")
            try:
                with mock.patch.object(
                    recording.os, "fsync", side_effect=OSError(errno.ENOSPC, "disk full")
                ), self.assertRaises(OSError):
                    recorder.close()
                recorder.abort()
                self.assertEqual(mlvlg.validate_mlg(recorder.temporary).data_records, 1)
            finally:
                recorder.abort()

    def test_partial_append_failure_recovers_only_the_earlier_record(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, dashboard = self.one_record(Path(directory) / "partial.mlg")
            try:
                valid = recorder.temporary.read_bytes()

                def partial_write(values, elapsed):
                    block = mlvlg.encode_data_block(recorder.fields, values, 1, elapsed)
                    recorder._stream.write(block[:-2])
                    raise OSError(errno.ENOSPC, "disk full")

                with mock.patch.object(recorder._writer, "write", side_effect=partial_write), self.assertRaises(OSError):
                    recorder.append(dashboard, 0.01)
                retained = recorder.temporary.read_bytes()
                self.assertGreater(len(retained), len(valid))
                output = Path(directory) / "partial.recovered.mlg"
                recovered = recording.recover_recording(recorder.temporary, output)
                self.assertEqual(recovered.validation.data_records, 1)
                self.assertEqual(output.read_bytes(), valid)
                self.assertEqual(recorder.temporary.read_bytes(), retained)
            finally:
                recorder.abort()

    def test_stream_close_failure_does_not_delete_recorded_data(self):
        with tempfile.TemporaryDirectory() as directory:
            recorder, _dashboard = self.one_record(Path(directory) / "close-error.mlg")
            stream = mock.Mock(wraps=recorder._stream)
            stream.close.side_effect = OSError(errno.EIO, "close failed")
            try:
                with mock.patch.object(recorder, "_stream", stream):
                    with self.assertRaises(OSError):
                        recorder.close()
                    self.assertEqual(recorder.abort(), recorder.temporary)
                    self.assertIsNotNone(recorder.close_error)
                self.assertEqual(mlvlg.validate_mlg(recorder.temporary).data_records, 1)
            finally:
                recorder.abort()

    def test_failed_atomic_publication_retains_the_capture(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "unsupported.mlg"
            recorder, _dashboard = self.one_record(output)
            try:
                with mock.patch.object(
                    recording.os, "link", side_effect=OSError(errno.EOPNOTSUPP, "publication unsupported")
                ), self.assertRaises(OSError):
                    recorder.close()
                self.assertFalse(output.exists())
                self.assertEqual(recorder.retained_path, recorder.temporary)
                self.assertEqual(mlvlg.validate_mlg(recorder.temporary).data_records, 1)
            finally:
                recorder.abort()

    def test_failure_after_publication_reports_the_actual_output_path(self):
        with tempfile.TemporaryDirectory() as directory, contextlib.chdir(directory):
            output = Path("published.mlg")
            recorder, _dashboard = self.one_record(output)
            original_stat = Path.stat

            def fail_output_stat(path, *args, **kwargs):
                if path == output:
                    raise OSError(errno.EIO, "output stat failed")
                return original_stat(path, *args, **kwargs)

            try:
                with mock.patch.object(Path, "stat", fail_output_stat), self.assertRaises(OSError):
                    recorder.close()
                self.assertEqual(recorder.abort(), Path(directory).resolve() / output)
                self.assertEqual(mlvlg.validate_mlg(output).data_records, 1)
            finally:
                recorder.abort()

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
        self.assertEqual(validation.fields, 89)
        self.assertEqual(header[2], 1_776_000_000)
        names = [name for _, name in fields]
        self.assertIn("Vehicle speed", names)
        self.assertIn("Stock CAN RPM", names)
        self.assertIn("Gear", names)
        self.assertIn("Intake CVTC target", names)
        self.assertIn("Exhaust CVTC target", names)
        self.assertIn("Knock timing state", names)
        self.assertIn("High-detonation surface selected", names)
        self.assertNotIn("gps_lat", names)
        self.assertNotIn("gps_lon", names)
        self.assertEqual([name for name in names if "*" in name], [])
        cvtc_units = {
            "Intake CVTC actual B1": "degCA",
            "Intake CVTC target": "degCA",
            "Exhaust CVTC actual B1": "degCA",
            "Exhaust CVTC actual B2": "degCA",
            "Exhaust CVTC target": "degCA",
        }
        cvtc_specs = {
            binding.spec.name: binding.spec
            for binding in recorder.bindings
            if binding.spec.name in cvtc_units
        }
        self.assertEqual(set(cvtc_specs), set(cvtc_units))
        for name, spec in cvtc_specs.items():
            self.assertEqual(spec.scale, 0.5)
            self.assertEqual(spec.transform, -128.0)
            self.assertEqual(spec.units, cvtc_units[name])
        duty_specs = {
            binding.spec.name: binding.spec
            for binding in recorder.bindings
            if binding.spec.name in {
                "CVTC duty B1",
                "Intake CVTC duty command B1",
                "Exhaust CVTC duty B1 word",
            }
        }
        self.assertEqual(set(duty_specs), {"CVTC duty B1"})
        self.assertEqual(duty_specs["CVTC duty B1"].scale, 0.39)
        self.assertEqual(duty_specs["CVTC duty B1"].units, "%")
        knock_specs = {
            binding.spec.name: binding.spec
            for binding in recorder.bindings
            if binding.spec.name in {
                "Knock timing state",
                "High-detonation surface selected",
            }
        }
        self.assertEqual(knock_specs["Knock timing state"].scale, 1 / 256)
        self.assertEqual(knock_specs["Knock timing state"].units, "deg")
        self.assertEqual(knock_specs["Knock timing state"].digits, 3)
        self.assertEqual(
            knock_specs["High-detonation surface selected"].display_style,
            mlvlg.MLG_ON_OFF,
        )
        secondary_throttle_specs = [
            binding.spec
            for binding in recorder.bindings
            if binding.spec.name in {"Secondary TPS B1", "Secondary TPS B2"}
        ]
        self.assertEqual(len(secondary_throttle_specs), 2)
        for spec in secondary_throttle_specs:
            self.assertEqual(spec.scale, 1 / 200)
            self.assertEqual(spec.units, "V")
            self.assertEqual(spec.digits, 3)
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
        self.assertEqual(records[-1]["Gear"], dashboard.tcm_gear)
        self.assertIn(dashboard.tcm_gear, model.TCM_GEARS)

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
            self.assertTrue(temporary.exists())
            self.assertEqual(mlvlg.validate_mlg(temporary).data_records, 1)


class RecordingRecoveryTest(unittest.TestCase):
    def retained_file(self, directory):
        source = Path(directory) / ".drive.mlg.retained.tmp"
        with source.open("wb") as stream:
            writer = mlvlg.StreamWriter(
                stream, (mlvlg.FieldSpec("Probe", field_type=mlvlg.MLG_U16),), 123
            )
            writer.write((100,), 0.0)
            writer.write((101,), 0.01)
        return source

    def test_recovery_copies_only_valid_records_and_keeps_corrupt_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.retained_file(directory)
            valid = source.read_bytes()
            source.write_bytes(valid + b"\x00\x02\x00")
            original = source.read_bytes()
            output = Path(directory) / "drive.recovered.mlg"
            recovered = recording.recover_recording(source, output)
            self.assertEqual(output.read_bytes(), valid)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(recovered.validation.data_records, 2)
            self.assertEqual(recovered.excluded_bytes, 3)
            self.assertTrue(recovered.tail_error)
            self.assertEqual(mlvlg.validate_mlg(output), recovered.validation)
            with self.assertRaises(mlvlg.MlvlgError):
                mlvlg.validate_mlg(source)

    def test_valid_unfinished_file_is_copied_without_deleting_its_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.retained_file(directory)
            original = source.read_bytes()
            output = Path(directory) / "recovered.mlg"
            recovered = recording.recover_recording(source, output)
            self.assertIsNone(recovered.tail_error)
            self.assertEqual(recovered.excluded_bytes, 0)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(output.read_bytes(), original)

    def test_recovery_never_overwrites_an_existing_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.retained_file(directory)
            original = source.read_bytes()
            output = Path(directory) / "existing.mlg"
            output.write_bytes(b"another recording")
            with self.assertRaises(FileExistsError):
                recording.recover_recording(source, output)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(output.read_bytes(), b"another recording")

    def test_destination_appearing_during_recovery_is_not_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.retained_file(directory)
            original = source.read_bytes()
            output = Path(directory) / "appeared.mlg"
            validate = mlvlg.validate_mlg

            def validate_and_create_destination(path):
                result = validate(path)
                output.write_bytes(b"another recording")
                return result

            with mock.patch.object(
                recording.mlvlg, "validate_mlg", side_effect=validate_and_create_destination
            ), self.assertRaises(FileExistsError):
                recording.recover_recording(source, output)
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual(output.read_bytes(), b"another recording")

    def test_recovery_storage_failure_preserves_the_source(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.retained_file(directory)
            original = source.read_bytes()
            output = Path(directory) / "full-disk.mlg"
            with mock.patch.object(
                recording.os, "fsync", side_effect=OSError(errno.ENOSPC, "disk full")
            ), self.assertRaises(OSError):
                recording.recover_recording(source, output)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse(output.exists())
            self.assertEqual(set(Path(directory).iterdir()), {source})

    def test_invalid_header_is_retained_without_a_recovered_output(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "invalid.tmp"
            source.write_bytes(b"invalid header")
            output = Path(directory) / "recovered.mlg"
            with self.assertRaises(mlvlg.MlvlgError):
                recording.recover_recording(source, output)
            self.assertEqual(source.read_bytes(), b"invalid header")
            self.assertFalse(output.exists())

    def test_failed_copy_validation_keeps_the_original(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.retained_file(directory)
            original = source.read_bytes()
            output = Path(directory) / "invalid-copy.mlg"
            mismatch = mlvlg.ValidationSummary(fields=2, record_length=2, data_records=2, marker_records=0)
            with mock.patch.object(
                recording.mlvlg, "validate_mlg", return_value=mismatch
            ), self.assertRaisesRegex(mlvlg.MlvlgError, "differs"):
                recording.recover_recording(source, output)
            self.assertEqual(source.read_bytes(), original)
            self.assertFalse(output.exists())


class MlgCalibrationGateTest(unittest.TestCase):
    """Bind recorded channel values to the values the dashboard displays."""

    RAW_PROBES = (0, 1, 37, 64, 128, 200, 255, 1024, 25_600, 27_069, 65_535)

    def setUp(self):
        self.bindings = recording.build_bindings("tuning")
        self.profile = model.DashboardModel().decoder.profile
        self.calibrations = can_telemetry.calibrations(self.profile)

    def test_every_field_of_the_profile_reaches_one_channel_in_order(self):
        fields = [
            field["name"]
            for field in can_telemetry.profile_fields(self.profile)
        ]
        recorded = [
            binding.source
            for binding in self.bindings
            if binding.source_kind == "raw"
        ]
        self.assertEqual(recorded, fields)
        self.assertGreater(len(self.calibrations), 50)

    def test_channel_values_equal_dashboard_engineering_values(self):
        for binding in self.bindings:
            calibration = self.calibrations.get(binding.source)
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

    def test_a_channel_takes_the_presentation_of_its_field(self):
        specs = {binding.source: binding.spec for binding in self.bindings}
        for field in can_telemetry.profile_fields(self.profile):
            spec = specs[field["name"]]
            dashboard = field["dashboard"]
            with self.subTest(field=field["name"]):
                self.assertEqual(spec.name, dashboard["label"])
                self.assertEqual(spec.category, dashboard["group"])
                self.assertEqual(spec.digits, dashboard["digits"])
                self.assertEqual(spec.units, can_telemetry.display_unit(field))

    def test_candidate_marker_matches_the_dashboard_units(self):
        layout = presentation.default()
        metrics = {metric.key: metric for metric in layout.hero}
        for _tab, panels in layout.tabs:
            for _title, panel in panels:
                metrics.update({metric.key: metric for metric in panel})
        compared = 0
        for binding in self.bindings:
            metric = metrics.get(can_telemetry.engineering_key(binding.source))
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
