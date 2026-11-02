#!/usr/bin/env python3
"""Read the verified snapshots of a JK08A tuning MLG or TRC capture.

The Rolling Launch audits evaluate activations from these snapshots. Each
snapshot carries the stock button and dashboard frames, vehicle speed,
coolant, and the fuel-inhibit, timing, APC, pedal, BFS, knock-surface, and
exhaust-CVTC telemetry sources.

Engine speed is the coordinate `0xFFFF11F4` in counts of 12.5 RPM, which is a
shift of the word that stock frame 0x180 carries. The frame is sampled at
another instant of the cycle, so every RPM bound spans the frames recorded
with the snapshot and with the next one, widened by `STOCK_RPM_MARGIN` counts.

A TRC adds frame times: the first and last page of every snapshot group and
the context frames of 0x239 and 0x551.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard.model import (
    ASCD_BUTTON_ID,
    DASHBOARD_STATE_ID,
    DashboardModel,
    FrameRecord,
)
from tools.logs import mlg_relation_audit
from tools.logs import mlg_retime
from tools.logs import peak_trc_audit

# The coordinate of a snapshot lies between the stock frames recorded with it
# and with the next snapshot apart from the update jitter that registry entry
# can_telemetry.stock_speed_bracket_2026_09_22 bounds; the margin exceeds it.
STOCK_RPM_MARGIN = 8
TELEMETRY_SOURCES = (
    "fuel_inhibit_mask",
    "final_timing_raw",
    "apc_command_raw",
    "app1_raw",
    "bfs_raw",
    "knock_surface_state",
    "exhaust_cvtc_target_raw",
)
CONTEXT_SOURCES = (
    "ascd_button_raw",
    "dashboard_state_raw",
    "vehicle_speed_kmh",
    "coolant_raw",
)


@dataclass(frozen=True)
class Sample:
    tick: int
    button: int | None
    dashboard: int | None
    speed_kmh: float | None
    coolant_raw: int | None
    rpm_raw: int
    rpm_low: int
    rpm_high: int
    fuel_inhibit_mask: int
    final_timing_raw: int
    apc_command_raw: int
    app1_raw: int
    bfs_raw: int
    knock_surface_state: int
    exhaust_cvtc_target_raw: int


@dataclass(frozen=True)
class TraceTiming:
    """Frame times of a TRC in milliseconds from the trace start.

    The page times align with the verified snapshots; the context frames hold
    byte 3 of every 0x239 frame and byte 5 of every 0x551 frame.
    """

    first_page_ms: tuple[float, ...]
    last_page_ms: tuple[float, ...]
    button_frames: tuple[tuple[float, int], ...]
    dashboard_frames: tuple[tuple[float, int], ...]


@dataclass(frozen=True)
class Capture:
    path: Path
    sha256: str
    samples: tuple[Sample, ...]
    timing: TraceTiming | None = None


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _optional_int(value) -> int | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return int(value)


def _optional_float(value) -> float | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    return float(value)


def _sample(tick: int, value, rpm_raw: int) -> Sample:
    return Sample(
        tick=tick,
        button=_optional_int(value("ascd_button_raw")),
        dashboard=_optional_int(value("dashboard_state_raw")),
        speed_kmh=_optional_float(value("vehicle_speed_kmh")),
        coolant_raw=_optional_int(value("coolant_raw")),
        rpm_raw=rpm_raw,
        rpm_low=rpm_raw,
        rpm_high=rpm_raw,
        **{name: int(value(name)) for name in TELEMETRY_SOURCES},
    )


def stock_speed_pairs(samples) -> list[tuple[int, int]]:
    """Return the lower and upper word of the stock frames around each snapshot.

    The stock frame recorded with a snapshot precedes its group, and the frame
    recorded with the next snapshot follows it. A snapshot without a next one
    keeps its own frame.
    """
    pairs = []
    for index, sample in enumerate(samples):
        words = [sample.rpm_raw]
        if index + 1 < len(samples) and samples[index + 1].tick == sample.tick + 1:
            words.append(samples[index + 1].rpm_raw)
        pairs.append((min(words), max(words)))
    return pairs


def _stock_speed_bounds(samples: list[Sample]) -> list[Sample]:
    """Widen each stock-frame word to the words its snapshot can carry."""
    return [
        replace(
            sample,
            rpm_low=max(0, low - STOCK_RPM_MARGIN),
            rpm_high=high + STOCK_RPM_MARGIN,
        )
        for sample, (low, high) in zip(samples, stock_speed_pairs(samples))
    ]


def read_mlg(path: Path) -> Capture:
    """Read the verified snapshots of one dashboard MLVLG recording."""
    recording_ = mlg_relation_audit.read_recording(path)
    columns = recording_.columns
    required = ("tick16", "schema_verified", *TELEMETRY_SOURCES, *CONTEXT_SOURCES)
    missing = [name for name in required if name not in columns]
    rpm = mlg_relation_audit.engine_speed_counts(recording_)
    if rpm is None:
        missing.append("engine speed")
    if missing:
        raise ValueError(f"{path}: missing channels {', '.join(missing)}")
    ticks = mlg_retime.unwrap_ticks(columns["tick16"])
    samples = []
    previous = None
    for index, tick in enumerate(ticks):
        # A bridge record repeats the preceding snapshot, tick included.
        if tick == previous or columns["schema_verified"][index] != 1:
            continue
        previous = tick
        if rpm[index] is None:
            continue
        samples.append(
            _sample(tick, lambda name: columns[name][index], rpm[index])
        )
    return Capture(
        Path(path), recording_.sha256, tuple(_stock_speed_bounds(samples))
    )


def read_trc(
    path: Path,
    *,
    profile: str = "tuning",
    can_id: int = 0x6F0,
    tick_divisor: int = 1,
) -> Capture:
    """Replay a PEAK TRC through the dashboard model into verified snapshots."""
    path = Path(path)
    digest = _sha256_file(path)
    trace = peak_trc_audit.load_trace(path)
    model = DashboardModel(profile, can_id, tick_divisor)
    samples = []
    first_pages = []
    last_pages = []
    buttons = []
    dashboard = []
    group_start = None
    run = None
    for frame in trace.frames:
        timestamp = frame.offset_ms / 1000.0
        standard = not frame.extended and not frame.remote
        if standard and frame.can_id == can_id and len(frame.data) == 8:
            # The low nibble of byte 0 is the page index of a group.
            if not frame.data[0] & 0x0F:
                group_start = frame.offset_ms
        snapshot = model.process_frame(
            FrameRecord(
                arbitration_id=frame.can_id,
                data=frame.data,
                timestamp=timestamp,
                received_monotonic=timestamp,
                is_extended_id=frame.extended,
                is_remote_frame=frame.remote,
            ),
            now=timestamp,
        )
        if standard and frame.can_id == ASCD_BUTTON_ID and len(frame.data) >= 4:
            buttons.append((frame.offset_ms, model.ascd_button_raw))
        elif (
            standard and frame.can_id == DASHBOARD_STATE_ID and len(frame.data) >= 6
        ):
            dashboard.append((frame.offset_ms, model.dashboard_state_raw))
        if snapshot is None or not model.schema_verified:
            continue
        if any(name not in model.raw for name in TELEMETRY_SOURCES):
            continue
        rpm_raw = model.engine_speed_counts
        if rpm_raw is None:
            continue
        if run is None:
            run = snapshot.run
        elif snapshot.run != run:
            raise ValueError(f"{path}: the capture spans more than one producer run")

        def value(name):
            if name in model.raw:
                return model.raw[name]
            return getattr(model, name, None)

        samples.append(_sample(snapshot.unwrapped_tick, value, rpm_raw))
        first_pages.append(group_start)
        last_pages.append(frame.offset_ms)
    timing = TraceTiming(
        tuple(first_pages), tuple(last_pages), tuple(buttons), tuple(dashboard)
    )
    return Capture(path, digest, tuple(_stock_speed_bounds(samples)), timing)


def read_capture(path: Path, **options) -> Capture:
    if Path(path).suffix.lower() == ".trc":
        return read_trc(path, **options)
    return read_mlg(path)

