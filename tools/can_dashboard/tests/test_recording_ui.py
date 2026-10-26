"""Recording failure reports and offline recovery without a Tk display."""

import contextlib
import errno
import io
from pathlib import Path
import tempfile
import types
import unittest
from unittest import mock

from tools.can_dashboard import app
from tools.logs import mlvlg


class RecordingFailureUiTest(unittest.TestCase):
    def dashboard(self):
        retained = Path("retained directory/.drive.mlg.unfinished.tmp")
        error = OSError(errno.ENOSPC, "disk full")
        recorder = types.SimpleNamespace(
            append=mock.Mock(side_effect=error), close=mock.Mock(side_effect=error),
            abort=mock.Mock(return_value=retained), close_error=None,
        )
        dashboard = object.__new__(app.DashboardApp)
        dashboard.recorder = recorder
        dashboard.recording_clock = types.SimpleNamespace(elapsed=mock.Mock(return_value=0.1))
        dashboard.record_var = types.SimpleNamespace(set=mock.Mock())
        dashboard._sync_record_button = mock.Mock()
        dashboard.model = object()
        return dashboard, recorder, retained

    def test_append_error_reports_the_retained_path_and_stops_recording(self):
        dashboard, recorder, retained = self.dashboard()
        with self.assertLogs(app.LOG.name, level="ERROR") as logs:
            dashboard._record_snapshot(None, 1.0)
        self.assertIsNone(dashboard.recorder)
        self.assertIsNone(dashboard.recording_clock)
        dashboard.record_var.set.assert_called_with(f"MLG incomplete: {retained}")
        self.assertIn(str(retained), " ".join(logs.output))
        dashboard._record_snapshot(None, 2.0)
        recorder.append.assert_called_once()
        recorder.abort.assert_called_once()

    def test_finalize_error_reports_the_retained_path(self):
        dashboard, recorder, retained = self.dashboard()
        with self.assertLogs(app.LOG.name, level="ERROR") as logs:
            dashboard.stop_recording()
        self.assertIsNone(dashboard.recorder)
        self.assertIsNone(dashboard.recording_clock)
        dashboard.record_var.set.assert_called_with(f"MLG incomplete: {retained}")
        self.assertIn(str(retained), " ".join(logs.output))
        dashboard.stop_recording()
        recorder.close.assert_called_once()
        recorder.abort.assert_called_once()

    def test_stream_close_error_remains_visible(self):
        dashboard, recorder, retained = self.dashboard()
        recorder.close_error = OSError(errno.EIO, "stream close failed")
        with self.assertLogs(app.LOG.name, level="ERROR") as logs:
            dashboard.stop_recording()
        self.assertIn("stream close failed", " ".join(logs.output))
        dashboard.record_var.set.assert_called_with(f"MLG incomplete: {retained}")


class RecordingRecoveryCommandTest(unittest.TestCase):
    def test_recovers_a_prefix_without_opening_Tk(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "retained.tmp"
            with source.open("wb") as stream:
                writer = mlvlg.StreamWriter(stream, (mlvlg.FieldSpec("Probe"),), 123)
                writer.write((100,), 0.0)
                stream.write(b"\x00\x01\x00")
            original = source.read_bytes()
            output = Path(directory) / "recovered.mlg"
            stdout = io.StringIO()
            with mock.patch.object(app.tk, "Tk") as tk_root, contextlib.redirect_stdout(stdout), self.assertLogs(app.LOG.name):
                status = app.main([
                    "--recover-recording", str(source), "--recovery-output", str(output), "--no-log-file"
                ])
            self.assertEqual(status, 0)
            tk_root.assert_not_called()
            self.assertEqual(mlvlg.validate_mlg(output).data_records, 1)
            self.assertEqual(source.read_bytes(), original)
            self.assertIn("Recovered prefix", stdout.getvalue())
            self.assertIn("3 damaged trailing bytes excluded", stdout.getvalue())
            self.assertIn(str(source), stdout.getvalue())

    def test_requires_both_recovery_paths(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            app.main(["--recover-recording", "retained.tmp", "--no-log-file"])
        self.assertEqual(error.exception.code, 2)

    def test_recovery_cannot_start_live_recording(self):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            app.main([
                "--recover-recording", "retained.tmp", "--recovery-output", "recovered.mlg",
                "--record", "live.mlg", "--no-log-file",
            ])
        self.assertEqual(error.exception.code, 2)

    def test_recovery_rejects_diagnostic_modes_before_hardware_or_Tk(self):
        for option in ("--pcan-driver-check", "--smoke-test"):
            with self.subTest(option=option), mock.patch.object(app.tk, "Tk") as tk_root:
                with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    app.main([
                        "--recover-recording", "retained.tmp", "--recovery-output", "recovered.mlg",
                        option, "--no-log-file",
                    ])
                self.assertEqual(error.exception.code, 2)
                tk_root.assert_not_called()
