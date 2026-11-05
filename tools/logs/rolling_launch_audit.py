#!/usr/bin/env python3
"""Audit the Rolling Launch hold of a JK08A tuning MLG or TRC capture.

The reader returns the verified snapshots of a capture. Each snapshot carries
the stock button and dashboard frames, vehicle speed, coolant, the
fuel-inhibit, timing, APC, pedal, BFS, knock-surface, and exhaust-CVTC
telemetry sources, and the Rolling Launch phase and abort reason. The
integrator, speed error, torque fraction, and cut counter are slots of the
launch-law configurations of the dynamic page: a snapshot carries the slots
that the configuration and group of its configuration byte name, and the
others read None.

The hold audit replays the speed controller of `patches/rolling_launch.py`
with the calibration of the flashed image through every ACTIVE run. The
speed error of a snapshot lies inside the abort window. The model integrator
follows the published errors from zero at the entry tick, or from a published
integrator; the model fraction follows from the previous fraction through the
rate limit. A snapshot without the speed error leaves the integrator unknown,
and one without the fraction widens the previous fraction by the rate limit.
Under the one-group configuration every snapshot carries the error, the
fraction, and the cut counter, so every fraction equals its model step. Under
the two-group configuration a snapshot of group 0 follows a published
integrator and a snapshot whose fraction is unknown, so its fraction lies in
the model range of the two-tick step. In hold mode the cut counter of a run
lies within the cuts that the delivered fractions owe the spark events of its
engine speed.

Engine speed is the coordinate `0xFFFF11F4` in counts of 12.5 RPM, which is a
shift of the word that stock frame 0x180 carries. The frame is sampled at
another instant of the cycle, so every RPM bound spans the frames recorded
with the snapshot and with the next one, widened by `STOCK_RPM_MARGIN` counts.

A TRC adds frame times: the first and last page of every snapshot group and
the context frames of 0x239 and 0x551, plus the raw torque, transmission,
and speed frames for the optional bus join.
"""

from __future__ import annotations

import argparse
import bisect
from dataclasses import dataclass, field, replace
import hashlib
import json
import math
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import rolling_launch
from patches.rolling_launch_layout import load_layout
from tools.can_dashboard.model import (
    ASCD_BUTTON_ID,
    BASE_TICK_SECONDS,
    DASHBOARD_STATE_ID,
    DashboardModel,
    FrameRecord,
)
from tools.logs import can_telemetry
from tools.logs import mlg_relation_audit
from tools.logs import mlg_retime
from tools.logs import peak_trc_audit
from tools.logs import tcm_shift_audit

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
# The Rolling Launch fields of the hold audit and their sample attributes.
# The phase and the abort reason are fixed and context fields; the others are
# slots of the dynamic page.
HOLD_SOURCES = {
    "rolling_launch_phase": "phase",
    "rolling_launch_abort_reason": "abort_reason",
    "rolling_launch_integrator_raw": "integrator",
    "rolling_launch_speed_error_raw": "speed_error",
    "rolling_launch_torque_fraction_raw": "torque_fraction",
    "rolling_launch_cut_counter": "cut_counter",
}
# Spark events per tick and native RPM count: three events per revolution,
# 12.5 RPM per count, and 10.24 ms per tick.
EVENTS_PER_COUNT_TICK = 3 * 12.5 / 60 * 0.01024
# The six accumulators start a run at offsets that sum to 2.75 cuts, and each
# truncates less than one cut, so a run that owes E cuts makes more than
# E - 3.25 and at most E + 2.75. One event of phase uncertainty at each end of
# the run widens both sides by one cut.
_OFFSET_CUTS = (
    sum(rolling_launch.SPARK_CYLINDER_OFFSETS) / rolling_launch.SPARK_CUT_ONE
)
CUTS_BELOW = _OFFSET_CUTS - rolling_launch.SPARK_CYLINDER_COUNT - 1
CUTS_ABOVE = _OFFSET_CUTS + 1
# Every tag of the rotating context pages is refreshed within this many
# snapshots, so the abort reason of the snapshot this far after the abort
# tick was captured after it.
CONTEXT_REFRESH_SNAPSHOTS = 5
BUS_IDS = {0x160, 0x174, 0x176, 0x177, 0x180, 0x280, 0x284, 0x421}


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
    phase: int | None = None
    abort_reason: int | None = None
    integrator: int | None = None
    speed_error: int | None = None
    torque_fraction: int | None = None
    cut_counter: int | None = None
    # The configuration byte of the dynamic page.
    configuration: int | None = None
    # The selected map index of the rotating context, 0 for Map 1.
    map_index: int | None = None


@dataclass(frozen=True)
class DynamicPage:
    """The fields that the configuration byte of a snapshot makes current.

    A field outside the dynamic page is current in every snapshot. A slot
    field is current only when the configuration and group of the byte name
    it, because the dashboard holds the last value of a slot that the
    snapshot does not carry.
    """

    field: str | None
    dynamic: frozenset
    groups: dict

    @classmethod
    def of(cls, profile):
        return cls(
            can_telemetry.configuration_field(profile),
            can_telemetry.dynamic_field_names(profile),
            {
                row["id"] | index << 7: frozenset(names)
                for row in profile.get("configurations", ())
                for index, names in enumerate(row["groups"])
            },
        )

    def carries(self, selector, name):
        return name not in self.dynamic or name in self.groups.get(selector, ())


@dataclass(frozen=True)
class TraceTiming:
    """Frame times of a TRC in milliseconds from the trace start.

    The page times align with the verified snapshots; the context frames hold
    byte 3 of every 0x239 frame and byte 5 of every 0x551 frame.
    `bus_frames` retains standard data frames by ID for the raw bus audit.
    """

    first_page_ms: tuple[float, ...]
    last_page_ms: tuple[float, ...]
    button_frames: tuple[tuple[float, int], ...]
    dashboard_frames: tuple[tuple[float, int], ...]
    bus_frames: dict[int, tuple[tuple[float, bytes], ...]] = field(default_factory=dict)


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


def _sample(tick: int, value, rpm_raw: int, page: DynamicPage) -> Sample:
    selector = None if page.field is None else _optional_int(value(page.field))
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
        **{
            attribute: (
                _optional_int(value(name)) if page.carries(selector, name) else None
            )
            for name, attribute in HOLD_SOURCES.items()
        },
        configuration=selector,
        map_index=_optional_int(value("active_map_index")),
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
    page = DynamicPage.of(can_telemetry.load_schema()[1]["tuning"])
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
            _sample(
                tick,
                lambda name: columns[name][index] if name in columns else None,
                rpm[index],
                page,
            )
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
    page = DynamicPage.of(model.decoder.profile)
    samples = []
    first_pages = []
    last_pages = []
    buttons = []
    dashboard = []
    bus = {can_id: [] for can_id in BUS_IDS}
    group_start = None
    run = None
    for frame in trace.frames:
        timestamp = frame.offset_ms / 1000.0
        standard = not frame.extended and not frame.remote
        if standard and frame.can_id in bus:
            bus[frame.can_id].append((frame.offset_ms, bytes(frame.data)))
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

        samples.append(_sample(snapshot.unwrapped_tick, value, rpm_raw, page))
        first_pages.append(group_start)
        last_pages.append(frame.offset_ms)
    timing = TraceTiming(
        tuple(first_pages), tuple(last_pages), tuple(buttons), tuple(dashboard),
        {can_id: tuple(frames) for can_id, frames in bus.items()},
    )
    return Capture(path, digest, tuple(_stock_speed_bounds(samples)), timing)


def read_capture(path: Path, **options) -> Capture:
    if Path(path).suffix.lower() == ".trc":
        return read_trc(path, **options)
    return read_mlg(path)



@dataclass(frozen=True)
class HoldRun:
    """One ACTIVE run of contiguous snapshots and its audit results.

    `law_ticks` counts the snapshots whose torque fraction was checked
    against the model step.
    `target_speed` is the range of the stock-frame speed minus the published
    error in km/h*10, which stays narrow while the speed word follows the
    frame. `cuts` and `owed` are None outside hold mode, for a run without
    the snapshots before and after it, and when a fraction of the run or a
    cut counter of those snapshots is unknown. The owed cuts follow the cut
    fraction of the trim efficiency of the map slot.
    `floor_ticks` counts the hold snapshots whose stock APC command plus
    the trim lies past the floor command, so the applied retard is smaller
    than the trim, the fired events deliver more than the stored
    efficiency, and the actuator cuts more events than the delivered
    torque needs; the speed loop absorbs the difference.
    """

    start_tick: int
    end_tick: int
    abort_reason: int | None
    law_ticks: int
    failures: tuple[tuple[int, str], ...]
    target_speed: tuple[float, float] | None
    ceiling_ticks: int
    cuts: int | None
    owed: tuple[float, float] | None
    floor_ticks: int = 0

    @property
    def cuts_inside(self) -> bool | None:
        if self.cuts is None or self.owed is None:
            return None
        return self.owed[0] < self.cuts <= self.owed[1]


def read_calibration(image: Path) -> rolling_launch.Calibration:
    """Read the Rolling Launch configuration record of a flashed image: the
    current record, or the schema 4 record of an earlier image, which
    holds one integral gain for every map and no trim."""
    layout = load_layout()
    span = layout.configuration
    legacy = layout.retired_configuration_for(rolling_launch.LEGACY_SCHEMA_VERSION)
    data = Path(image).read_bytes()
    if len(data) < max(span.end, legacy.end):
        raise ValueError(f"{image}: image ends before the configuration record")
    calibration = rolling_launch.Calibration.from_bytes(data[span.start : span.end])
    if calibration.is_valid():
        return calibration
    try:
        return rolling_launch.Calibration.from_legacy_bytes(
            data[legacy.start : legacy.end]
        )
    except ValueError:
        raise ValueError(
            f"{image}: the Rolling Launch configuration is invalid"
        ) from None


def run_slot(samples, start, end, calibration) -> rolling_launch.Slot:
    """The map slot of an ACTIVE run: the slot of the selected map that the
    context refresh reports within the run and the snapshots before it."""
    slots = set(calibration.slots)
    if len(slots) == 1:
        return calibration.slots[0]
    first = max(0, start - CONTEXT_REFRESH_SNAPSHOTS)
    indices = {
        sample.map_index
        for sample in samples[first : end + 1]
        if sample.map_index is not None
    }
    if len(indices) != 1 or not 0 <= min(indices) < rolling_launch.SLOT_COUNT:
        raise ValueError(
            f"tick {samples[start].tick}: the capture lacks one selected map"
            " for the run of a configuration with per-map slots"
        )
    return calibration.slot(indices.pop())


def _predecessor(samples, index):
    if index and samples[index - 1].tick == samples[index].tick - 1:
        return samples[index - 1]
    return None


def _replay(samples, start, end, calibration, slot):
    """Replay the controller through one ACTIVE run.

    Return the failures, the count of checked fractions, and the bounds of
    the torque fraction at every snapshot of the run, None where unknown.
    """
    unit = rolling_launch.U_ONE
    rate = calibration.u_rate_limit
    previous = _predecessor(samples, start)
    integrator = fraction = None
    if previous is not None and previous.phase == rolling_launch.Phase.IDLE:
        integrator, fraction = 0, (unit, unit)
    failures = []
    law_ticks = 0
    bounds = []
    for sample in samples[start : end + 1]:
        error = sample.speed_error
        command = None
        if error is None:
            integrator = None
        else:
            if not -calibration.abort_below <= error <= calibration.abort_above:
                failures.append(
                    (sample.tick, "speed error outside the abort window")
                )
            if integrator is not None:
                proportional = rolling_launch.proportional_fraction(
                    error, calibration
                )
                integrator = rolling_launch.update_integrator(
                    integrator, proportional, error, calibration,
                    slot.integral_gain,
                )
                command = min(
                    max(
                        proportional
                        + (integrator >> rolling_launch.INTEGRATOR_SHIFT),
                        0,
                    ),
                    unit,
                )
        if fraction is not None:
            low, high = fraction
            if command is None:
                fraction = max(0, low - rate), min(unit, high + rate)
            else:
                fraction = (
                    min(max(command, low - rate), low + rate),
                    min(max(command, high - rate), high + rate),
                )
        if sample.integrator is not None:
            if integrator is not None and sample.integrator != integrator:
                failures.append(
                    (sample.tick,
                     f"integrator {sample.integrator}, model {integrator}")
                )
            integrator = sample.integrator
        published = sample.torque_fraction
        if published is not None:
            if command is not None and fraction is not None:
                law_ticks += 1
                low, high = fraction
                if not low <= published <= high:
                    model = low if low == high else f"{low}..{high}"
                    failures.append(
                        (sample.tick,
                         f"torque fraction {published}, model {model}")
                    )
            fraction = published, published
        bounds.append(fraction)
    return failures, law_ticks, bounds


def _abort_reason(samples, end):
    """The abort reason of the snapshot that the context refresh makes
    fresh after the run, or None when the capture lacks it."""
    tick = samples[end].tick + CONTEXT_REFRESH_SNAPSHOTS
    for sample in samples[end + 1 : end + 1 + CONTEXT_REFRESH_SNAPSHOTS]:
        if sample.phase != rolling_launch.Phase.COOLDOWN:
            return None
        if sample.tick == tick:
            return sample.abort_reason
    return None


def _owed_cuts(samples, start, end, bounds, efficiency):
    """The bounds of the cuts owed from the IDLE snapshot before the run
    through the snapshot after it, or None without both of them or with a
    fraction of the run unknown."""
    before = _predecessor(samples, start)
    after = end + 1 < len(samples) and samples[end + 1].tick == samples[end].tick + 1
    if before is None or not after or None in bounds:
        return None
    unit = rolling_launch.U_ONE
    low = high = 0.0
    for index in range(start, end + 2):
        sample = samples[index]
        fractions = []
        if index <= end:
            fractions.append(bounds[index - start])
        if index > start:
            fractions.append(bounds[index - start - 1])
        # Before the update of the entry tick the phase is IDLE, and after the
        # update of the tick that ends the run it is COOLDOWN; both cut nothing.
        if index in (start, end + 1):
            fractions.append((unit, unit))
        # The cut fraction falls as the torque fraction rises.
        low += sample.rpm_low * EVENTS_PER_COUNT_TICK * min(
            rolling_launch.cut_fraction(fraction, efficiency)
            for _low, fraction in fractions
        )
        high += sample.rpm_high * EVENTS_PER_COUNT_TICK * max(
            rolling_launch.cut_fraction(fraction, efficiency)
            for fraction, _high in fractions
        )
    return max(0.0, low / unit + CUTS_BELOW), high / unit + CUTS_ABOVE


def audit_hold(samples, calibration) -> tuple[HoldRun, ...]:
    """Audit every ACTIVE run of the verified snapshots.

    The replay steps the controller once per snapshot, so a capture whose
    snapshots do not step by one tick, which a tick divisor above 1
    produces, is refused.
    """
    samples = list(samples)
    if not any(sample.phase is not None for sample in samples):
        raise ValueError("the capture carries no Rolling Launch phase")
    step = math.gcd(
        *(after.tick - before.tick for before, after in zip(samples, samples[1:]))
    )
    if step > 1:
        raise ValueError(
            f"the snapshots step by {step} ticks; the hold audit needs one"
            " snapshot per tick"
        )
    active = rolling_launch.Phase.ACTIVE
    runs = []
    index = 0
    while index < len(samples):
        if samples[index].phase != active:
            index += 1
            continue
        start = index
        while (
            index + 1 < len(samples)
            and samples[index + 1].phase == active
            and samples[index + 1].tick == samples[index].tick + 1
        ):
            index += 1
        runs.append(_run(samples, start, index, calibration))
        index += 1
    return tuple(runs)


def _run(samples, start, end, calibration):
    run = samples[start : end + 1]
    for sample in run:
        if sample.speed_error is None and sample.integrator is None:
            raise ValueError(
                f"tick {sample.tick}: the capture lacks the Rolling Launch"
                " hold fields"
            )
    slot = run_slot(samples, start, end, calibration)
    failures, law_ticks, bounds = _replay(samples, start, end, calibration, slot)
    targets = [
        sample.speed_kmh * 10 - sample.speed_error
        for sample in run
        if sample.speed_kmh is not None and sample.speed_error is not None
    ]
    cuts = owed = None
    floor_ticks = 0
    if calibration.mode == rolling_launch.Mode.HOLD:
        if slot.max_trim:
            floor_ticks = sum(
                sample.apc_command_raw + slot.max_trim > slot.floor_command
                for sample in run
            )
        owed = _owed_cuts(
            samples, start, end, bounds, slot.trim_efficiency
        )
        if owed is not None:
            counters = [
                sample.cut_counter for sample in samples[start - 1 : end + 2]
            ]
            if None in counters:
                owed = None
            else:
                cuts = sum(
                    (after - before) & 0xFF
                    for before, after in zip(counters, counters[1:])
                )
    return HoldRun(
        start_tick=samples[start].tick,
        end_tick=samples[end].tick,
        abort_reason=_abort_reason(samples, end),
        law_ticks=law_ticks,
        failures=tuple(failures),
        target_speed=(min(targets), max(targets)) if targets else None,
        ceiling_ticks=sum(
            sample.fuel_inhibit_mask & rolling_launch.FUEL_CUT_CYLINDER_MASK
            == rolling_launch.FUEL_CUT_CYLINDER_MASK
            for sample in run
        ),
        cuts=cuts,
        owed=owed,
        floor_ticks=floor_ticks,
    )


def _reason_name(reason):
    if reason is None:
        return "unknown"
    try:
        return rolling_launch.AbortReason(reason).name
    except ValueError:
        return str(reason)


def decode_speed_word(data: bytes) -> int:
    """JK08A 0x284/0x280 bytes 4..5 in native 0.1 km/h counts.

    The selected receiver divides the big-endian word by ten, truncating,
    and maps the invalid wire word 0xFFFF to zero (kb 7mfk:000c4506).
    """
    if len(data) < 6:
        raise ValueError("speed frame needs bytes 4 and 5")
    word = int.from_bytes(data[4:6], "big")
    return 0 if word == 0xFFFF else word // 10


class _BusIndex:
    def __init__(self, frames):
        self.frames = frames
        self.times = [time for time, _ in frames]

    def before(self, time, age_ms=25):
        index = bisect.bisect_right(self.times, time) - 1
        if index < 0 or time - self.times[index] > age_ms:
            return None
        return self.frames[index]

    def between(self, start, end):
        return self.frames[
            bisect.bisect_left(self.times, start):bisect.bisect_left(self.times, end)
        ]


def _range(values):
    return [min(values), statistics.median(values), max(values)] if values else None


def _tcm_groups(bus):
    """Use the existing TCM field decoder on complete back-to-back groups."""
    result = []
    for time, speed in bus[0x176].frames:
        gear = bus[0x174].before(time, tcm_shift_audit.TCM_GROUP_MS)
        index = bisect.bisect_left(bus[0x177].times, time)
        if gear is None or index == len(bus[0x177].frames):
            continue  # A trace can start or end inside a group.
        phase_time, phase = bus[0x177].frames[index]
        if phase_time - gear[0] >= tcm_shift_audit.TCM_GROUP_MS:
            raise ValueError("late 0x177 in TCM group")
        if min(len(gear[1]), len(speed), len(phase)) < 6:
            raise ValueError("short TCM group")
        selector = bus[0x421].before(time, 100)
        result.append(tcm_shift_audit.TcmFrame(
            time / 1000, gear[1], speed, phase,
            selector[1][0] if selector and selector[1] else None,
        ))
    return result


def _reference_ticks(capture, reference):
    """Join one producer run by tick modulo 65536 and verify its contents.

    A TRC can start before a wrap that precedes the MLG. Each capture must
    contain at most one occurrence of each 16-bit tick; otherwise the join
    is ambiguous. Matching ticks of distinct producer runs are refused.
    """
    indexes = {}
    for index, sample in enumerate(capture.samples):
        tick = sample.tick & 0xFFFF
        if tick in indexes:
            raise ValueError("ambiguous repeated tick in TRC/MLG join")
        indexes[tick] = index
    seen = set()
    matched = 0
    signature = (
        "rpm_raw", "phase", "configuration", "speed_error", "torque_fraction",
        "cut_counter", "app1_raw", "fuel_inhibit_mask",
    )
    for sample in reference.samples:
        tick = sample.tick & 0xFFFF
        if tick in seen:
            raise ValueError("ambiguous repeated tick in MLG reference")
        seen.add(tick)
        if tick in indexes:
            matched += 1
            other = capture.samples[indexes[tick]]
            if any(getattr(sample, key) != getattr(other, key) for key in signature):
                raise ValueError(f"tick {tick}: TRC and MLG snapshots differ")
    if not matched:
        raise ValueError("TRC and MLG have no matching snapshots")
    return indexes


def _speed_targets(samples, times, bus):
    """Intersect possible constant targets using the last two speed frames.

    RAM and the asynchronous CAN page do not share a sampling instant. The
    two preceding speed frames (at most 40 ms old) bracket that uncertainty.
    No target value is fitted or taken from the meter. An empty intersection
    disproves a candidate source; a nonempty one is only compatibility.
    """
    result = {}
    for can_id in (0x280, 0x284):
        intervals = []
        common = None
        for sample, time in zip(samples, times):
            if sample.speed_error is None:
                continue
            index = bisect.bisect_right(bus[can_id].times, time)
            words = [
                decode_speed_word(data) - sample.speed_error
                for frame_time, data in bus[can_id].frames[max(0, index - 2):index]
                if time - frame_time <= 40
            ]
            if words:
                intervals.append((min(words), max(words)))
                candidates = set(words)
                common = candidates if common is None else common & candidates
        low = max((a for a, _ in intervals), default=None)
        high = min((b for _, b in intervals), default=None)
        result[f"0x{can_id:03X}"] = {
            "samples": len(intervals),
            "target_intersection_raw": [low, high] if intervals else None,
            "target_candidates_raw": sorted(common) if common is not None else None,
            "compatible": bool(common) if common is not None else None,
        }
    return result


def release_cut_timing(capture, start_index, exit_index, release_ms, rpm_frames):
    """Bound veto-count events between adjacent coherent snapshots.

    Phase is fixed page 2, current every tick. The button attribute is host
    context from 0x239, not the debounced ECU input 0xFFFF2A85. A counter
    increment ending at the first non-ACTIVE snapshot spans the transition;
    only subsequent increments demonstrate counting after that snapshot.
    First-page times are capture proxies, not interrupt-event timestamps.
    """
    samples = capture.samples
    times = capture.timing.first_page_ms
    stop = next((i for i in range(exit_index + 1, len(samples))
                 if samples[i].phase == rolling_launch.Phase.ACTIVE), len(samples))
    deltas = {}
    complete = True
    for index in range(start_index + 1, stop):
        previous, sample = samples[index - 1:index + 1]
        elapsed_ms = times[index] - times[index - 1]
        if (sample.tick != previous.tick + 1 or not 0 < elapsed_ms <= 2000 * BASE_TICK_SECONDS
                or previous.cut_counter is None
                or sample.cut_counter is None):
            complete = False
            continue
        deltas[index] = (sample.cut_counter - previous.cut_counter) & 0xFF
    host = next((i for i in range(start_index, stop)
                 if capture.timing.last_page_ms[i] >= release_ms
                 and samples[i].button == rolling_launch.BUTTON_RELEASED), None)
    changes = [i for i, count in deltas.items() if count]
    result = {
        "host_release_snapshot_tick": samples[host].tick if host is not None else None,
        "host_release_snapshot_first_page_ms": times[host] if host is not None else None,
        "host_release_snapshot_ms": (
            capture.timing.last_page_ms[host] if host is not None else None
        ),
        "ecu_release_snapshot_ms": None,
        "phase_exit_snapshot_tick": samples[exit_index].tick,
        "phase_exit_snapshot_ms": times[exit_index],
        "phase_exit_interval_ms": [times[exit_index - 1], times[exit_index]],
        "phase_exit_counter_increment": deltas.get(exit_index),
        "cuts_after_release_bounds": [
            sum(count for i, count in deltas.items() if times[i - 1] >= release_ms),
            sum(count for i, count in deltas.items() if times[i] > release_ms),
        ] if complete else None,
        "cuts_after_phase_exit_snapshot": (
            sum(count for i, count in deltas.items() if i > exit_index)
            if complete else None
        ),
        "inactive_snapshots_checked": stop - exit_index - 1,
        "inactive_observation_ms": times[stop - 1] - times[exit_index],
        "counter_window_complete": complete,
        "last_increment_snapshot_tick": None,
        "last_increment_snapshot_ms": None,
        "last_cut_offset_ms_bounds": None,
        "last_cut_cycles_bounds": None,
    }
    if not changes:
        return result
    last = changes[-1]
    bounds = [times[last - 1] - release_ms, times[last] - release_ms]
    result.update(last_increment_snapshot_tick=samples[last].tick,
                  last_increment_snapshot_ms=times[last],
                  last_cut_offset_ms_bounds=bounds)
    rpm_frame = rpm_frames.before(times[last])
    if rpm_frame is None or len(rpm_frame[1]) < 2:
        return result
    rpm = int.from_bytes(rpm_frame[1][:2], "big") / 8
    cycles = [ms * rpm / 120000 for ms in bounds]
    result.update(last_cut_rpm=rpm, last_cut_cycles_bounds=cycles,
                  raw_release_one_cycle=(
                      "unresolved_window" if not complete else
                      "within_snapshot_bound" if cycles[1] <= 1 else
                      "beyond_snapshot_bound" if cycles[0] > 1 else
                      "straddles_one_cycle"
                  ))
    return result


def audit_bus(capture, runs, *, reference=None):
    """Join holds to raw CAN frames without calling an estimate shaft torque.

    0x180 contains the ECU torque estimate and 0x160 its parallel estimate.
    Neither includes the added spark veto. Equality, including equality
    inside a hold, cannot time restoration of physical torque. Report the
    first subsequent estimate frame and its cycle equivalent separately.
    0x174 words A/B are TCM requests, not actual-torque observations.
    """
    if capture.timing is None:
        raise ValueError("bus join requires a TRC")
    reference = capture if reference is None else reference
    indexes = _reference_ticks(capture, reference)
    bus = {
        can_id: _BusIndex(capture.timing.bus_frames.get(can_id, ()))
        for can_id in BUS_IDS
    }
    tcm = _tcm_groups(bus)
    gear_ratios = {}
    for gear in tcm_shift_audit.RE5R05A_RATIOS:
        ratios = [
            frame.output_speed / frame.turbine_speed for frame in tcm
            if frame.current == frame.target == gear
            and frame.shift_code == tcm_shift_audit.IDLE_SHIFT_CODE
            and frame.selector in (
                *tcm_shift_audit.DRIVE_SELECTORS, *tcm_shift_audit.MANUAL_SELECTORS
            )
            and frame.turbine_speed >= tcm_shift_audit.RATIO_MIN_TURBINE
            and frame.output_speed >= tcm_shift_audit.RATIO_MIN_OUTPUT
        ]
        if ratios:
            gear_ratios[str(gear)] = statistics.median(ratios)
    buttons = capture.timing.button_frames
    releases = [
        time for (_, previous), (time, button) in zip(buttons, buttons[1:])
        if previous == rolling_launch.BUTTON_CANCEL
        and button == rolling_launch.BUTTON_RELEASED
    ]
    holds = []
    active_windows = []
    for number, run in enumerate(runs, 1):
        row = {"hold": number, "start_tick": run.start_tick,
               "abort_reason": _reason_name(run.abort_reason), "covered": False}
        holds.append(row)
        ticks = range(run.start_tick, run.end_tick + 2)
        joined = [indexes.get(tick & 0xFFFF) for tick in ticks]
        if None in joined or any(b != a + 1 for a, b in zip(joined, joined[1:])):
            continue
        start_index, end_index = joined[0], joined[-1]
        times = capture.timing.first_page_ms[start_index:end_index + 1]
        start, end = times[0], times[-1]
        active_windows.append((start, end))
        release = next((t for t in releases if start <= t <= end + 1000), None)
        row.update(covered=True, start_ms=start, end_ms=end, release_ms=release)
        frames = [f for f in tcm if start <= f.seconds * 1000 < end]
        ratios = [f.output_speed / f.turbine_speed for f in frames if f.turbine_speed]
        gears = sorted({f.current for f in frames})
        row["gears"] = gears
        row["ratio_min_median_max"] = _range(ratios)
        row["ratio_reference_median"] = (
            gear_ratios.get(str(gears[0])) if len(gears) == 1 else None
        )
        row["tcm_word_a_range"] = _range([f.word_a for f in frames])
        row["tcm_word_b_range"] = _range([f.word_b for f in frames])
        row["speed_sources"] = _speed_targets(
            capture.samples[start_index:end_index], times[:-1], bus
        )
        equal = compared = 0
        actual = []
        for time, data in bus[0x180].between(start, end):
            parallel = bus[0x160].before(time, 2)
            if len(data) < 5:
                raise ValueError("short 0x180 torque frame")
            word = data[2] << 4 | data[3] >> 4
            actual.append(word)
            if parallel and len(parallel[1]) >= 3:
                other = (parallel[1][1] & 15) << 8 | parallel[1][2]
                if 0xFFF not in (word, other):
                    compared += 1
                    equal += word == other
        row.update(actual_word_range=_range(actual),
                   parallel_pairs=compared, parallel_equal=equal,
                   torque_recovery_ms=None, torque_recovery_cycles=None,
                   torque_recovery_status="spark_veto_not_in_torque_estimate")
        if release is None:
            continue
        next_frames = bus[0x180].between(release, release + 25)
        previous_frame = bus[0x180].before(release)
        if next_frames and previous_frame:
            time, _ = next_frames[0]
            rpm = int.from_bytes(previous_frame[1][:2], "big") / 8
            delay = time - release
            row.update(next_torque_frame_ms=delay, release_rpm=rpm,
                       release_rpm_age_ms=release - previous_frame[0],
                       next_torque_frame_cycles=delay * rpm / 120000)
        cut_timing = release_cut_timing(capture, start_index, end_index, release, bus[0x180])
        if run.abort_reason == rolling_launch.AbortReason.BUTTON_RELEASED:
            # The runtime consumes the stable input after the stock ASCD
            # task and aborts in that pass. The input byte itself is absent.
            cut_timing["ecu_release_inferred_ms_bounds"] = [
                capture.timing.first_page_ms[end_index - 1], end,
            ]
            last = cut_timing["last_increment_snapshot_ms"]
            if (last is not None and "last_cut_rpm" in cut_timing
                    and cut_timing["counter_window_complete"]):
                upper = max(0, last - capture.timing.first_page_ms[end_index - 1])
                cut_timing["last_cut_after_ecu_release_upper_ms"] = upper
                cut_timing["last_cut_after_ecu_release_upper_cycles"] = (
                    upper * cut_timing["last_cut_rpm"] / 120000
                )
        elif run.abort_reason in (
            rolling_launch.AbortReason.PEDAL_LOW, rolling_launch.AbortReason.RPM_LOW,
        ):
            # A released stable input overrides these gate reasons with
            # BUTTON_RELEASED. It has not been accepted at this abort pass.
            cut_timing["ecu_release_inferred_not_before_ms"] = end
            last = cut_timing["last_increment_snapshot_ms"]
            if (last is not None and "last_cut_rpm" in cut_timing
                    and cut_timing["counter_window_complete"]):
                upper = max(0, last - end)
                cut_timing["last_cut_after_ecu_release_upper_ms"] = upper
                cut_timing["last_cut_after_ecu_release_upper_cycles"] = (
                    upper * cut_timing["last_cut_rpm"] / 120000
                )
        row["cut_release"] = cut_timing
        last = cut_timing["last_increment_snapshot_ms"]
        row["last_cut_counter_update_after_release_ms"] = (
            last - release if last is not None and last >= release else None
        )
    frame_speeds = {"inside": [], "outside": []}
    for time, data in bus[0x280].frames:
        other = bus[0x284].before(time)
        if other is None:
            continue
        meter, ecu = decode_speed_word(data), decode_speed_word(other[1])
        if meter < 100:  # Moving samples, at least 10 km/h.
            continue
        key = "inside" if any(a <= time < b for a, b in active_windows) else "outside"
        frame_speeds[key].append(ecu / meter)
    return {
        "trace": capture.path.name, "sha256": capture.sha256,
        "reference": reference.path.name,
        "frame_period_ms": {
            f"0x{can_id:03X}": statistics.median(b - a for a, b in zip(times, times[1:]))
            for can_id, times in (
                (0x239, [t for t, _ in buttons]),
                *((can_id, bus[can_id].times) for can_id in (0x180, 0x280, 0x284)),
            ) if len(times) > 1
        },
        "gear_ratio_medians": gear_ratios,
        "speed_284_over_280": {
            key: {"samples": len(values), "min_median_max": _range(values)}
            for key, values in frame_speeds.items()
        },
        "holds": holds,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--image", type=Path, required=True,
        help="flashed image whose Rolling Launch configuration ran",
    )
    parser.add_argument("captures", type=Path, nargs="+")
    parser.add_argument("--bus-json", type=Path, help="write the raw CAN join of one TRC")
    parser.add_argument("--reference-mlg", type=Path,
                        help="join the TRC by tick to all holds of this MLG")
    args = parser.parse_args(argv)
    if (args.bus_json or args.reference_mlg) and len(args.captures) != 1:
        parser.error("the bus join requires exactly one TRC")
    if args.reference_mlg and not args.bus_json:
        parser.error("--reference-mlg requires --bus-json")
    calibration = read_calibration(args.image)
    failed = False
    for path in args.captures:
        capture = read_capture(path)
        runs = audit_hold(capture.samples, calibration)
        print(f"{capture.path.name} sha256={capture.sha256} runs={len(runs)}")
        # A capture without a run, or a run without a checked fraction,
        # checks nothing and cannot pass.
        failed |= not runs
        for run in runs:
            target = (
                "none" if run.target_speed is None
                else f"{run.target_speed[0]:.0f}..{run.target_speed[1]:.0f}"
            )
            cuts = "n/a"
            if run.cuts is not None:
                low, high = run.owed
                cuts = f"{run.cuts} owed ({low:.2f}, {high:.2f}]"
            print(
                f"  ticks {run.start_tick}..{run.end_tick}"
                f" abort={_reason_name(run.abort_reason)}"
                f" law_ticks={run.law_ticks}"
                f" failed_ticks={len({tick for tick, _ in run.failures})}"
                f" target={target}"
                f" ceiling_ticks={run.ceiling_ticks} cuts={cuts}"
                f" floor_ticks={run.floor_ticks}"
            )
            for tick, failure in run.failures:
                print(f"    tick {tick}: {failure}")
            failed |= (
                bool(run.failures)
                or run.cuts_inside is False
                or not run.law_ticks
            )
        if args.bus_json:
            reference = read_mlg(args.reference_mlg) if args.reference_mlg else capture
            reference_runs = audit_hold(reference.samples, calibration)
            failed |= not reference_runs or any(
                run.failures or run.cuts_inside is False or not run.law_ticks
                for run in reference_runs
            )
            result = audit_bus(capture, reference_runs, reference=reference)
            args.bus_json.write_text(json.dumps(result, indent=2) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
