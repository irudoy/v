"""Seekable replay of PEAK TRC 1.1, candump, and dashboard MLG recordings.

A replay loads the whole file into a timeline of source times before it
plays. The player feeds the model on the window clock, so playback can pause,
seek, change speed, and loop a region. A seek rebuilds the model: the map
tracker and the acceleration timer resume from a checkpoint copy advanced to
the warm-up start, and the model replays the seconds before the target so
every rotating context and stock frame is current when playback continues.
"""

from __future__ import annotations

from array import array
from bisect import bisect_left, bisect_right
import copy
from dataclasses import dataclass
import math
from pathlib import Path
import struct

from tools.can_dashboard import recording
from tools.can_dashboard.model import (
    OBSERVED_IDS,
    DriveObserver,
    FrameRecord,
    SnapshotRecord,
)
from tools.logs import can_telemetry, mlvlg, peak_trc_audit


SPEEDS = (0.25, 0.5, 1.0, 2.0, 4.0, 8.0)
WARMUP_SECONDS = 3.0
CHECKPOINT_SECONDS = 1.0
MAX_ITEMS_PER_STEP = 8000
FLAG_ERROR = 0x01
DRIVE_SOURCES = (
    "tick16",
    "vehicle_speed_kmh",
    "ascd_button_raw",
    "dashboard_state_raw",
)
MLG_HEADER = struct.Struct(">6sHIIIHH")


class ReplayError(ValueError):
    """Raised when a replay file cannot be loaded."""


@dataclass(frozen=True)
class ReplayLoaded:
    """Source event of a timeline that finished loading."""

    timeline: object


class Timeline:
    """Replay items of one file in non-decreasing source-time order.

    Times are seconds from the start of the capture: the TRC offset, the MLG
    elapsed time, or the candump time since the first line.
    """

    kind = ""

    def __init__(self, path, times, can_id):
        self.path = Path(path)
        self.times = times
        self.can_id = can_id
        self._checkpoints = []
        self._checkpoint_indices = []

    def __len__(self):
        return len(self.times)

    @property
    def duration(self):
        return self.times[-1] if len(self.times) else 0.0

    def index_after(self, time):
        """Index of the first item later than time."""
        return bisect_right(self.times, time)

    def index_at(self, time):
        """Index of the first item at or after time."""
        return bisect_left(self.times, time)

    def observe(self, drive, index):
        raise NotImplementedError

    def build_checkpoints(self):
        drive = DriveObserver(self.can_id)
        checkpoints = []
        due = -math.inf
        for index in range(len(self)):
            time = self.times[index]
            if time >= due:
                checkpoints.append((index, copy.deepcopy(drive)))
                due = time + CHECKPOINT_SECONDS
            self.observe(drive, index)
        self._checkpoints = checkpoints
        self._checkpoint_indices = [index for index, _drive in checkpoints]

    def drive_at(self, index):
        """Return a drive observer that has seen every item before index."""
        position = bisect_right(self._checkpoint_indices, index) - 1
        if position < 0:
            start, drive = 0, DriveObserver(self.can_id)
        else:
            start, saved = self._checkpoints[position]
            drive = copy.deepcopy(saved)
        for item in range(start, index):
            self.observe(drive, item)
        return drive


class FrameTimeline(Timeline):
    """Standard frames that the dashboard consumes, and error records."""

    def __init__(self, path, kind, times, ids, flags, payloads, can_id):
        super().__init__(path, times, can_id)
        self.kind = kind
        self.ids = ids
        self.flags = flags
        self.payloads = payloads

    def item(self, index, received=None):
        return FrameRecord(
            arbitration_id=self.ids[index],
            data=self.payloads[index],
            timestamp=self.times[index],
            received_monotonic=received,
            is_error_frame=bool(self.flags[index] & FLAG_ERROR),
        )

    def observe(self, drive, index):
        if not self.flags[index]:
            drive.frame(self.times[index], self.ids[index], self.payloads[index])


class RecordTimeline(Timeline):
    """Snapshot records of a dashboard MLG recording, raw values by source."""

    kind = "MLG"

    def __init__(self, path, times, columns, can_id):
        super().__init__(path, times, can_id)
        self.columns = columns
        self._drive_columns = tuple(
            (name, columns[name]) for name in DRIVE_SOURCES if name in columns
        )

    def item(self, index, received=None):
        return SnapshotRecord(
            self.times[index],
            {name: column[index] for name, column in self.columns.items()},
            received,
        )

    def observe(self, drive, index):
        drive.record(
            self.times[index],
            {name: column[index] for name, column in self._drive_columns},
        )


class _FrameColumns:
    def __init__(self):
        self.times = array("d")
        self.ids = array("H")
        self.flags = array("B")
        self.payloads = []

    def append(self, time, can_id, flags, payload):
        if self.times and time < self.times[-1]:
            time = self.times[-1]
        self.times.append(time)
        self.ids.append(can_id)
        self.flags.append(flags)
        self.payloads.append(payload)

    def timeline(self, path, kind, can_id):
        return FrameTimeline(
            path,
            kind,
            self.times,
            self.ids,
            self.flags,
            self.payloads,
            can_id,
        )


def _load_trc(path, can_id):
    trace = peak_trc_audit.load_trace(path)
    kept = {can_id, *OBSERVED_IDS}
    columns = _FrameColumns()
    records = sorted(
        (*trace.frames, *trace.status_records),
        key=lambda record: record.number,
    )
    for record in records:
        time = record.offset_ms / 1000.0
        if isinstance(record, peak_trc_audit.StatusRecord):
            if record.kind == "Error":
                columns.append(time, 0, FLAG_ERROR, b"")
            continue
        if record.extended or record.remote or record.can_id not in kept:
            continue
        columns.append(time, record.can_id, 0, bytes(record.data))
    return columns.timeline(path, "TRC", can_id)


def _load_candump(path, can_id):
    kept = {can_id, *OBSERVED_IDS}
    columns = _FrameColumns()
    first = None
    last = 0.0
    with path.open("r", encoding="utf-8") as source:
        for line in source:
            parsed = can_telemetry.parse_candump_line(line)
            if parsed is None:
                continue
            frame_id, payload, timestamp = parsed
            if timestamp is not None:
                if first is None:
                    first = timestamp
                last = max(last, timestamp - first)
            if frame_id in kept:
                columns.append(last, frame_id, 0, payload)
    return columns.timeline(path, "candump", can_id)


def _channel_key(name):
    return name.replace("*", "").strip().lower()


def _load_mlg(path, can_id, profile, schema_path):
    mlvlg.validate_mlg(path)
    fields = mlvlg.read_fields(path)
    sources_by_name = {
        _channel_key(binding.spec.name): binding.source
        for binding in recording.build_bindings(profile, schema_path)
    }
    sources = [sources_by_name.get(_channel_key(field.name)) for field in fields]
    if "elapsed" not in sources or "tick16" not in sources:
        raise ReplayError(
            f"{path.name} is not a dashboard MLG recording: it has no "
            "Elapsed or Telemetry tick channel"
        )
    elapsed_position = sources.index("elapsed")
    tick_position = sources.index("tick16")
    columns = {}
    kept = []
    for position, source in enumerate(sources):
        if source is None or source in {"date", "elapsed"}:
            continue
        column = columns.setdefault(source, array("f"))
        kept.append((position, column))
    record = struct.Struct(
        ">" + "".join(mlvlg.FIELD_STRUCTS[field.field_type][1:] for field in fields)
    )
    data = path.read_bytes()
    header = MLG_HEADER.unpack_from(data)
    data_begin, record_length = header[4], header[5]
    times = array("d")
    offset = data_begin
    last_tick = None
    while offset < len(data):
        if data[offset] != 0:
            offset += 4 + mlvlg.MLG_MARKER_MESSAGE_SIZE
            continue
        values = record.unpack_from(data, offset + 4)
        offset += 4 + record_length + 1
        tick = values[tick_position]
        if tick == last_tick:
            # A bridge record repeats the last snapshot across a gap.
            continue
        last_tick = tick
        time = float(values[elapsed_position])
        if times and time < times[-1]:
            time = times[-1]
        times.append(time)
        for position, column in kept:
            column.append(values[position])
    return RecordTimeline(path, times, columns, can_id)


def load_timeline(
    path,
    can_id,
    profile="tuning",
    schema_path=can_telemetry.DEFAULT_SCHEMA,
):
    """Load one replay file; the suffix selects TRC, MLG, or candump."""
    path = Path(path)
    suffix = path.suffix.lower()
    try:
        if suffix == ".trc":
            timeline = _load_trc(path, can_id)
        elif suffix == ".mlg":
            timeline = _load_mlg(path, can_id, profile, schema_path)
        else:
            timeline = _load_candump(path, can_id)
    except (
        OSError,
        UnicodeError,
        struct.error,
        peak_trc_audit.TraceError,
        mlvlg.MlvlgError,
    ) as error:
        raise ReplayError(str(error)) from error
    if not len(timeline):
        raise ReplayError(f"{path.name} holds nothing to replay")
    timeline.build_checkpoints()
    return timeline


class ReplayPlayer:
    """Position, speed, and loop region of one loaded timeline.

    The player maps the window clock onto source time from an anchor that
    every play, seek, and speed change resets. It hands out index ranges;
    the caller feeds them to the model and rebuilds the model on a seek.
    """

    def __init__(self, timeline, speed=1.0, loop=False):
        self.timeline = timeline
        self.speed = speed
        self.loop = loop
        self.loop_in = None
        self.loop_out = None
        self.position = 0.0
        self.index = 0
        self.playing = False
        self._anchor_host = None
        self._anchor_position = 0.0

    @property
    def duration(self):
        return self.timeline.duration

    def region(self):
        """Source-time bounds of the loop region."""
        start = 0.0 if self.loop_in is None else self.loop_in
        stop = self.duration if self.loop_out is None else self.loop_out
        return start, stop

    def _stop(self):
        stop = self.region()[1]
        if not self.loop or self.position >= stop:
            return self.duration
        return stop

    def at_stop(self):
        return self.position >= self._stop()

    def past_region(self):
        """Whether the position lies at or after the end of the loop region."""
        return self.position >= self.region()[1]

    def _anchor(self, host_now):
        self._anchor_host = host_now
        self._anchor_position = self.position

    def host_time(self, time, host_now):
        """Window-clock time at which a source time plays, capped at now."""
        if self._anchor_host is None:
            return host_now
        return min(
            host_now,
            self._anchor_host + (time - self._anchor_position) / self.speed,
        )

    def seek(self, target, host_now):
        """Move to target and return the index range that warms a new model."""
        target = min(max(target, 0.0), self.duration)
        self.position = target
        self.index = self.timeline.index_after(target)
        self._anchor(host_now)
        return self.timeline.index_at(target - WARMUP_SECONDS), self.index

    def play(self, host_now):
        self.playing = True
        self._anchor(host_now)

    def pause(self):
        self.playing = False

    def set_speed(self, speed, host_now):
        self.speed = speed
        self._anchor(host_now)

    def set_loop_in(self):
        self.loop_in = self.position
        if self.loop_out is not None and self.loop_out <= self.loop_in:
            self.loop_out = None

    def set_loop_out(self):
        self.loop_out = self.position
        if self.loop_in is not None and self.loop_in >= self.loop_out:
            self.loop_in = None

    def advance(self, host_now):
        """Return the item range due now and whether playback hit its stop."""
        first = self.index
        if not self.playing or self._anchor_host is None:
            return first, first, False
        target = (
            self._anchor_position
            + (host_now - self._anchor_host) * self.speed
        )
        stop = self._stop()
        ended = target >= stop
        if ended:
            target = stop
        last = self.timeline.index_after(target)
        if last - first > MAX_ITEMS_PER_STEP:
            # Fall behind the window clock rather than skip items.
            last = first + MAX_ITEMS_PER_STEP
            target = self.timeline.times[last - 1]
            ended = False
            self._anchor_host = host_now
            self._anchor_position = target
        self.index = last
        self.position = max(self.position, target)
        return first, last, ended


def next_speed(speed):
    """The replay speed after speed in SPEEDS, wrapping to the slowest."""
    for candidate in SPEEDS:
        if candidate > speed + 1e-9:
            return candidate
    return SPEEDS[0]
