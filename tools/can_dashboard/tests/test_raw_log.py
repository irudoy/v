"""Raw receive capture, asynchronous failures, and existing audit readers."""

from dataclasses import replace
import io
from pathlib import Path
import tempfile
import threading
import time
import unittest
from unittest import mock

from tools.can_dashboard.model import DashboardModel, DemoGenerator, FrameRecord
from tools.can_dashboard.raw_log import BusRecording, RawLogWriter, row
from tools.can_dashboard.recording import TelemetryMlgRecorder
from tools.can_dashboard.tests.test_recording import read_f32_records
from tools.logs import peak_trc_audit, rolling_launch_audit, tcm_shift_audit


class RawLogTest(unittest.TestCase):
    def finish(self, capture):
        capture.stop()
        self.assertTrue(capture.writer.done.wait(5), "raw writer did not finish")
        self.assertIsNone(capture.writer.error)

    def test_every_frame_and_timestamp_survive_a_long_session(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drive.trc"
            capture = BusRecording()
            capture.start(path, 1700000000.125, 10.0)
            frames = (
                FrameRecord(0x123, b"\x01", 1000.1, 10.1),
                FrameRecord(0x1ABCDE, b"\x02\x03", 1000.2, 10.1, is_extended_id=True),
                FrameRecord(0x321, b"", 1000.3, 10.1, is_remote_frame=True, dlc=8),
                FrameRecord(0x456, bytes(8), 1400.1, 410.1),
                FrameRecord(0, b"\x01\x02\x03\x04\x05", 1400.2, 410.2, is_error_frame=True),
            )
            # Pre-start driver events cannot enter either recording.
            self.assertIsNone(capture.capture(FrameRecord(1, b"", 999, 9)).recording_elapsed)
            stamped = [capture.capture(frame) for frame in frames]
            self.finish(capture)
            trace = peak_trc_audit.load_trace(path)
            self.assertEqual([frame.can_id for frame in trace.frames], [0x123, 0x1ABCDE, 0x321, 0x456])
            self.assertEqual([frame.data for frame in trace.frames], [frame.data for frame in frames[:4]])
            self.assertTrue(trace.frames[1].extended)
            self.assertTrue(trace.frames[2].remote)
            self.assertEqual(trace.frames[2].dlc, 8)
            for result, stamp in zip(trace.frames, stamped):
                self.assertAlmostEqual(result.offset_ms / 1000, stamp.recording_elapsed, places=8)
            self.assertGreater(trace.frames[-1].offset_ms, 400000)
            self.assertIn("data=0102030405", trace.status_records[0].description)
            self.assertEqual(capture.writer.frames, len(frames))
            self.assertIn("1000001)", row(1000001, 400, frames[0]))

    def test_audits_read_raw_log_and_mlg_uses_the_same_frame_time(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drive.mlg"
            capture = BusRecording()
            capture.start(path.with_suffix(".trc"), 1700000000.125, 10)
            recorder = TelemetryMlgRecorder(path, "tuning", 1700000000.125)
            model = DashboardModel("tuning", 0x6F0, 1)
            demo = DemoGenerator()
            snapshots = []
            source_time = 1000.0
            for tick in range(1, 21):
                frames = list(demo.stock_context(tick, bus_detail=True)) + list(demo.group(tick))
                # The existing TCM reader requires the three frames as one
                # adjacent group. Demo stock_context supplies that group.
                for frame in frames:
                    source_time += 0.0002
                    frame = capture.capture(replace(frame, timestamp=source_time,
                                                    received_monotonic=10.1))
                    if model.process_frame(frame, now=10.1) is not None:
                        recorder.append(model, frame.recording_elapsed)
                        snapshots.append(frame.recording_elapsed)
            recorder.close()
            self.finish(capture)
            trace = peak_trc_audit.load_trace(path.with_suffix(".trc"))
            records = read_f32_records(path)[2]
            self.assertEqual(len(records), len(snapshots))
            for record, elapsed in zip(records, snapshots):
                self.assertAlmostEqual(record["Elapsed"], elapsed, places=6)
            raw_last_pages = [f.offset_ms / 1000 for f in trace.frames
                              if f.can_id == 0x6F0 and f.data[0] & 15 == 10]
            self.assertEqual(len(raw_last_pages), len(snapshots))
            for raw, elapsed in zip(raw_last_pages, snapshots):
                self.assertAlmostEqual(raw, elapsed, places=8)
            tcm = tcm_shift_audit.read_trc(path.with_suffix(".trc"))
            rolling = rolling_launch_audit.read_trc(path.with_suffix(".trc"))
            self.assertEqual(len(tcm.tcm), 20)
            self.assertTrue(tcm.snapshots)
            self.assertTrue(rolling.samples)

    def test_disk_io_and_finish_do_not_block_the_caller(self):
        entered, release = threading.Event(), threading.Event()

        class SlowStream(io.StringIO):
            def write(self, value):
                entered.set()
                if not release.wait(5):
                    raise OSError("test disk remained blocked")
                return super().write(value)

        with mock.patch.object(Path, "open", return_value=SlowStream()):
            writer = RawLogWriter(Path("drive.trc"), 1700000000)
            try:
                self.assertTrue(entered.wait(1))
                started = time.monotonic()
                writer.append(FrameRecord(0x123, b"\x01"), 0.1)
                writer.finish()
                self.assertLess(time.monotonic() - started, 0.1)
                self.assertFalse(writer.done.is_set())
            finally:
                release.set()
                self.assertTrue(writer.done.wait(5))
            self.assertEqual(writer.frames, 1)

    def test_disk_error_stops_raw_only_and_is_visible(self):
        with mock.patch.object(Path, "open", side_effect=OSError("disk full")), \
                self.assertLogs("tools.can_dashboard.raw_log", level="ERROR"):
            capture = BusRecording()
            capture.start(Path("drive.trc"), 1700000000, 10)
            self.assertTrue(capture.writer.done.wait(2))
            stamped = capture.capture(FrameRecord(0x123, b"\x01", 1000, 10.1))
            self.assertAlmostEqual(stamped.recording_elapsed, 0.1)
            self.assertIn("TRC incomplete", capture.writer.status())
            self.assertIn("disk full", capture.writer.status())
            capture.stop()

    def test_backlog_exhaustion_is_reported_instead_of_silent_loss(self):
        entered, release = threading.Event(), threading.Event()

        def blocked_open(*_args, **_kwargs):
            entered.set()
            release.wait(5)
            return io.StringIO()

        with mock.patch.object(Path, "open", side_effect=blocked_open):
            writer = RawLogWriter(Path("drive.trc"), 1700000000, backlog=1)
            try:
                self.assertTrue(entered.wait(1))
                writer.append(FrameRecord(0x123, b""), 0.1)
                writer.append(FrameRecord(0x124, b""), 0.2)
                self.assertIn("backlog exhausted", writer.status())
            finally:
                with self.assertLogs("tools.can_dashboard.raw_log", level="ERROR"):
                    release.set()
                    self.assertTrue(writer.done.wait(5))

    def test_existing_raw_file_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drive.trc"
            path.write_text("previous capture")
            with self.assertLogs("tools.can_dashboard.raw_log", level="ERROR"):
                writer = RawLogWriter(path, 1700000000)
                self.assertTrue(writer.done.wait(2))
            self.assertEqual(path.read_text(), "previous capture")
            self.assertIn("TRC incomplete", writer.status())

    def test_a_retired_writer_failure_remains_visible_during_the_next_recording(self):
        with tempfile.TemporaryDirectory() as directory:
            capture = BusRecording()
            path = Path(directory) / "old.trc"
            path.write_text("previous capture")
            with self.assertLogs("tools.can_dashboard.raw_log", level="ERROR"):
                capture.start(path, 1700000000, 10)
                self.assertTrue(capture.writer.done.wait(2))
            capture.stop()
            capture.start(Path(directory) / "new.trc", 1700000001, 11)
            try:
                self.assertIn("old.trc", capture.status())
                self.assertIn("TRC incomplete", capture.status())
                self.assertIn("new.trc", capture.status())
            finally:
                self.finish(capture)
