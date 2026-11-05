"""Asynchronous PCAN-View TRC 1.1 recording before display filtering."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime
import logging
from pathlib import Path
import queue
import threading

from tools.can_dashboard.model import FrameClock


LOG = logging.getLogger(__name__)
# This bounds pending memory, not the length of a capture. Exhaustion ends the
# raw recording visibly rather than dropping an old or new frame silently.
BACKLOG_FRAMES = 65536


def header(start_epoch):
    local = datetime.fromtimestamp(start_epoch)
    days = (local - datetime(1899, 12, 30)).total_seconds() / 86400
    return (
        ";$FILEVERSION=1.1\n"
        f";$STARTTIME={days:.12f}\n"
        f"; Start time: {local.isoformat(timespec='microseconds')} (local time)\n"
        f"; Unix start seconds: {start_epoch:.9f}\n"
        "; Offset milliseconds / 1000 equals the paired MLG Elapsed channel.\n"
        "; Number) Offset(ms) Type ID DLC Data\n"
    )


def row(number, elapsed, frame):
    prefix = f"{number:8d}) {elapsed * 1000:.6f}"
    data = bytes(frame.data)
    dlc = frame.dlc if frame.dlc is not None else len(data)
    if frame.is_error_frame:
        # TRC 1.1 status rows require exactly four status bytes. Preserve the
        # original python-can payload and DLC in the description as well.
        status = data[:4].ljust(4, b"\x00").hex(" ").upper()
        return (
            f"{prefix} Error {frame.arbitration_id:08X} 4 {status} "
            f"CAN error dlc={dlc} data={data.hex().upper()}\n"
        )
    width = 8 if frame.is_extended_id else 4
    payload = "RTR" if frame.is_remote_frame else data.hex(" ").upper()
    return f"{prefix} Rx {frame.arbitration_id:0{width}X} {dlc} {payload}\n"


class RawLogWriter:
    """One disk worker, with nonblocking submission and stop requests.

    The final path is created exclusively by the worker and stays readable
    after a crash or error. The worker drains accepted frames on normal stop;
    a non-daemon thread also drains them when the window closes.
    """

    def __init__(self, output, start_epoch, *, backlog=BACKLOG_FRAMES):
        self.output = Path(output)
        self.start_epoch = start_epoch
        self.pending = queue.Queue(maxsize=backlog)
        self.finishing = threading.Event()
        self.done = threading.Event()
        self.error = None
        self.frames = 0
        self.thread = threading.Thread(target=self._run, name="raw-trc-writer", daemon=False)
        self.thread.start()

    def append(self, frame, elapsed):
        if self.finishing.is_set():
            return
        try:
            self.pending.put_nowait((frame, elapsed))
        except queue.Full:
            self._fail("raw log backlog exhausted; capture is incomplete")

    def finish(self):
        self.finishing.set()

    def _fail(self, error):
        self.error = str(error)
        self.finishing.set()

    def status(self):
        if self.error is not None:
            return f"TRC incomplete: {self.output}: {self.error}"
        state = "saved" if self.done.is_set() else "saving" if self.finishing.is_set() else "recording"
        return f"TRC: {state} {self.output.name}, {self.frames} frames"

    def _run(self):
        try:
            with self.output.open("x", encoding="ascii", newline="") as stream:
                stream.write(header(self.start_epoch))
                stream.flush()
                while not self.finishing.is_set() or not self.pending.empty():
                    try:
                        frame, elapsed = self.pending.get(timeout=0.1)
                    except queue.Empty:
                        stream.flush()
                        continue
                    stream.write(row(self.frames + 1, elapsed, frame))
                    self.frames += 1
                    if self.frames % 1024 == 0:
                        stream.flush()
                stream.flush()
        except (OSError, ValueError) as error:
            self._fail(error)
        finally:
            self.finishing.set()
            if self.error is not None:
                LOG.error("raw log incomplete at %s: %s", self.output, self.error)
            self.done.set()


class BusRecording:
    """The receive-side clock and raw sink of the current MLG recording."""

    def __init__(self):
        self._lock = threading.Lock()
        self.clock = None
        self.writer = None
        self.retiring = []

    def start(self, output, start_epoch, started):
        with self._lock:
            if self.writer is not None:
                self.retiring.append(self.writer)
            self.clock = FrameClock(started)
            self.writer = RawLogWriter(output, start_epoch)
            return self.clock

    def capture(self, frame):
        # No disk operation or Tk call occurs under this lock or in recv.
        with self._lock:
            if self.clock is None:
                return frame
            elapsed = self.clock.elapsed(frame, frame.received_monotonic)
            if elapsed is None:
                return frame
            self.writer.append(frame, elapsed)
            return replace(frame, recording_started=self.clock.started, recording_elapsed=elapsed)

    def stop(self):
        with self._lock:
            self.clock = None
            if self.writer is not None:
                self.writer.finish()

    def status(self):
        # A previous recording can still be draining when the next one starts.
        # Keep its failure visible alongside the current recording's state.
        with self._lock:
            self.retiring = [writer for writer in self.retiring
                             if not writer.done.is_set() or writer.error is not None]
            writers = [*self.retiring, *([self.writer] if self.writer else [])]
            return " | ".join(writer.status() for writer in writers)
