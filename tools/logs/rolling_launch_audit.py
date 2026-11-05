#!/usr/bin/env python3
"""Audit the Rolling Launch hold of a JK08A tuning MLG or TRC capture.

The reader returns the verified snapshots of a capture. Each snapshot carries
the stock button and dashboard frames, vehicle speed, coolant, the
fuel-inhibit, timing, pedal, BFS, knock-surface, and exhaust-CVTC telemetry
sources, and the Rolling Launch phase and abort reason. The other Rolling
Launch fields are slots of the page configurations of the dynamic page: a
snapshot carries the slots that the configuration and group of its
configuration byte name, and the others read None.

The hold audit replays the runtime of `patches/rolling_launch.py` with the
Rolling Launch record of the flashed image through every ACTIVE run: the
record of the current runtime with its efficiency table, or the record of
the registered historical endpoint that the image carries.

A historical endpoint carries the speed hold alone. The speed error of a
snapshot lies inside the abort window. The model integrator follows the
published errors from zero at the entry tick, or from a published
integrator; the model fraction follows from the previous fraction through
the rate limit. A snapshot without the speed error leaves the integrator
unknown, and one without the fraction widens the previous fraction by the
rate limit. Under configuration 1 every snapshot carries the error, the
fraction, and the cut-request counter, so every fraction equals its model
step. Under configuration 2 a snapshot of group 0 follows a published
integrator and a snapshot whose fraction is unknown, so its fraction lies in
the model range of the two-tick step. In hold mode the cut requests of a run
lie within the cuts that the delivered fractions owe the spark events of its
engine speed.

The current runtime selects the RPM or the speed regulator at activation;
the packed views name the kind of every snapshot, and a run keeps one kind.
Configuration 3 carries the control error, the law output, the
cut-request counter, and the applied trim with the actuation-ready bit at
every tick: the RPM fraction equals its model of the error and the soft
width of the map slot, the RPM error places the engine speed between the
stock frames, and the speed regulator replays from the IDLE predecessor
with a zero integrator and a full torque fraction. A run that starts
without its IDLE predecessor, or a gap, leaves the speed law unchecked.
Without the ready bit the applied trim is zero; with it the trim stays
within the trim of the regulator, and a smaller trim is clipped by the
floor. Group 1 of configuration 4 checks the published cut fraction q
against the law output and the efficiency, kind, and ready bit of the same
snapshot: q is zero without the ready bit, 1000 - p under the RPM regulator,
and the cut fraction of u at the efficiency under the speed regulator,
whose efficiency is a table value of a trim up to the trim of the
regulator. Group 0 carries the consumed q sum and the counter together:
between two such snapshots the cut requests lie strictly within six of the
owed cuts, the q sum difference over 1000, and from the reset of the
accumulators before a run they lie in (owed - 3.25, owed + 2.75].
Configuration 5 checks the speed-input bits, the accepted CANCEL, the speed
frame age, one target per run, the RPM target of the map slot, the RPM
sample between the stock frames, and the shared command: the effective
command is the stock command or the stock command with the trim, clipped by
the floor. Configuration 6 adds the release: the first snapshot that shows
the accepted RELEASED has no cut fraction, and the counter holds from it.
A q derived from configuration 3 is not a published q; configurations 4
and 6 publish it.

The counter counts the cut requests of the spark actuator, not withheld
sparks: a requested cut whose dwell arming precedes the dwell-start veto
still fires.

The stock APC command of a snapshot is `110 - final_timing_raw` modulo 256,
the command before the ignition trim of the map slot.

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

from patches import build_rom
from patches import calibration_ranges
from patches import rolling_launch
from patches import runtime_endpoints
from patches import runtime_targets
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
    "rolling_launch_cut_counter": "cut_requests",
    "rolling_launch_control_error_raw": "control_error",
    "rolling_launch_law_output_raw": "law_output",
    "rolling_launch_mode_trim": "mode_trim",
    "rolling_launch_consumed_q_sum_raw": "consumed_q_sum",
    "rolling_launch_cut_fraction_raw": "cut_fraction",
    "rolling_launch_efficiency": "efficiency",
    "rolling_launch_speed_sample_raw": "speed_sample",
    "rolling_launch_selected_target_raw": "selected_target",
    "rolling_launch_status": "status",
    "rolling_launch_rpm_sample_raw": "rpm_sample",
    "rolling_launch_stock_command_raw": "stock_command",
    "rolling_launch_effective_command_raw": "effective_command",
    "rolling_launch_accepted_button_raw": "accepted_button",
    "rolling_launch_speed_age_raw": "speed_age",
}
# The sample attributes of the schema 6 views of the current runtime.
CURRENT_VIEWS = (
    "control_error", "law_output", "mode_trim", "consumed_q_sum",
    "cut_fraction", "efficiency", "speed_sample", "selected_target", "status",
    "rpm_sample", "stock_command", "effective_command", "accepted_button",
    "speed_age",
)
# The packed views of the runtime extension: wire_mode_trim, wire_efficiency
# and wire_status of patches/rolling_launch.py.
MODE_TRIM_VALUE_MASK = 0x3F
MODE_TRIM_SPEED_BIT = 6
MODE_TRIM_READY_BIT = 7
EFFICIENCY_VALUE_MASK = 0x3FF
EFFICIENCY_SPEED_BIT = 14
EFFICIENCY_READY_BIT = 15
STATUS_KIND_MASK = 0x03
# Value valid, frame age within the limit, and speed source ready.
STATUS_INPUTS_MASK = 0x1C
STATUS_CANCEL_BIT = 5
STATUS_RELEASED_BIT = 6
STATUS_BUTTON_MASK = 1 << STATUS_CANCEL_BIT | 1 << STATUS_RELEASED_BIT
STATUS_READY_BIT = 7
# The inactive snapshots after an accepted release whose cut-request
# counter the release audit compares.
RELEASE_SNAPSHOTS = 5
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
    app1_raw: int
    bfs_raw: int
    knock_surface_state: int
    exhaust_cvtc_target_raw: int
    phase: int | None = None
    abort_reason: int | None = None
    integrator: int | None = None
    speed_error: int | None = None
    torque_fraction: int | None = None
    # The wrapping count of cut requests of the spark actuator.
    cut_requests: int | None = None
    # The schema 6 views of the runtime extension; see HOLD_SOURCES.
    control_error: int | None = None
    law_output: int | None = None
    mode_trim: int | None = None
    consumed_q_sum: int | None = None
    cut_fraction: int | None = None
    efficiency: int | None = None
    speed_sample: int | None = None
    selected_target: int | None = None
    status: int | None = None
    rpm_sample: int | None = None
    stock_command: int | None = None
    effective_command: int | None = None
    accepted_button: int | None = None
    speed_age: int | None = None
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

    `law_ticks` counts the snapshots whose controller output was checked
    against the model law, `actuation_ticks` the snapshots whose published
    cut fraction was checked against the output and the trim efficiency of
    the same snapshot, and `input_ticks` the snapshots whose inputs, target,
    or shared ignition command were checked.
    `target_speed` is the range of the stock-frame speed minus the published
    speed error in km/h*10, which stays narrow while the speed word follows
    the frame; it is None under the RPM regulator. `requested_cuts` and
    `owed` are None outside hold mode and when the capture does not bound
    the cuts that the run owes. The owed cuts of a historical endpoint follow
    the delivered fractions, the engine speed, and the trim efficiency of
    the map slot; those of the current runtime are the consumed q sum that
    the spark actuator publishes, over 1000, from the reset of its
    accumulators before the run. `floor_ticks` counts the hold snapshots
    whose trim the floor command clips, so the applied retard is smaller
    than the trim of the slot. `release_cuts` counts the cut requests after
    the snapshot that shows the accepted release of the run, or is None
    without it.
    """

    start_tick: int
    end_tick: int
    abort_reason: int | None
    law_ticks: int
    failures: tuple[tuple[int, str], ...]
    target_speed: tuple[float, float] | None
    requested_cuts: int | None
    owed: tuple[float, float] | None
    floor_ticks: int = 0
    kind: int | None = None
    actuation_ticks: int = 0
    input_ticks: int = 0
    release_cuts: int | None = None

    @property
    def requested_cuts_inside(self) -> bool | None:
        if self.requested_cuts is None or self.owed is None:
            return None
        return self.owed[0] < self.requested_cuts <= self.owed[1]

    @property
    def checked_ticks(self) -> int:
        return self.law_ticks + self.actuation_ticks + self.input_ticks


@dataclass(frozen=True)
class HoldSlot:
    """The controller and spark-actuator settings of one map slot of a
    historical endpoint."""

    integral_gain: int
    max_trim: int = 0
    floor_command: int = 0
    trim_efficiency: int = rolling_launch.U_ONE


@dataclass(frozen=True)
class HoldCalibration:
    """The settings of a flashed Rolling Launch record that the hold audit
    replays. `endpoint` is "current" or the key of the registered historical
    endpoint whose record they come from, and `schema` the schema of the
    record. The slots of the current runtime are `rolling_launch.Slot`
    values beside its efficiency `table`; those of a historical endpoint are
    `HoldSlot` values."""

    endpoint: str
    hold: bool
    window_top: int
    window_width: int
    u_rate_limit: int
    integrator_limit: int
    abort_above: int
    abort_below: int
    slots: tuple
    schema: int = rolling_launch.CONFIG_SCHEMA_VERSION
    table: rolling_launch.EfficiencyTable | None = None
    speed_frame_age_limit: int | None = None

    def slot(self, index):
        return self.slots[index]


def stock_apc_command(final_timing_raw: int) -> int:
    """The stock APC command of a final-timing byte, before the trim."""
    return (mlg_relation_audit.APC_COMMAND_BASE - final_timing_raw) & 0xFF


def endpoint_calibration(record: bytes, state: str, table: bytes | None = None) -> HoldCalibration:
    """Return the hold settings of the Rolling Launch record of an endpoint
    state: "current" with the bytes of its efficiency table, or the key of a
    registered historical endpoint whose speed-hold record has one integral
    gain for every map (schema 4) or per-map slots with the fixed trim
    (schema 5)."""
    if state == "current":
        try:
            calibration = rolling_launch.Calibration.from_bytes(record)
        except ValueError:
            calibration = None
        if (
            calibration is None
            or not calibration.is_valid()
            or calibration.to_bytes() != record
        ):
            raise ValueError("the current Rolling Launch record is invalid")
        try:
            efficiency = rolling_launch.EfficiencyTable.from_bytes(table or b"")
        except ValueError:
            raise ValueError("the current efficiency table is invalid") from None
        return HoldCalibration(
            endpoint=state,
            hold=calibration.mode == rolling_launch.Mode.HOLD,
            window_top=calibration.window_top,
            window_width=calibration.window_width,
            u_rate_limit=calibration.u_rate_limit,
            integrator_limit=calibration.integrator_limit,
            abort_above=calibration.abort_above,
            abort_below=calibration.abort_below,
            slots=calibration.slots,
            schema=calibration.schema_version,
            table=efficiency,
            speed_frame_age_limit=calibration.speed_frame_age_limit,
        )
    schema = runtime_endpoints.historical_endpoint(state).configuration_schema_version
    if schema not in runtime_endpoints.SPEED_HOLD_SCHEMA_FORMATS:
        raise ValueError(
            f"the schema {schema} record of endpoint {state!r} has no speed hold"
        )
    fields = runtime_endpoints.historical_configuration_fields(record, schema)
    if schema == 4:
        slots = (HoldSlot(fields["integral_gain"]),) * (
            runtime_endpoints.SPEED_HOLD_SLOT_COUNT
        )
    else:
        slots = tuple(HoldSlot(**slot) for slot in fields["slots"])
    return HoldCalibration(
        endpoint=state,
        hold=fields["mode"] == "hold",
        window_top=fields["window_top"],
        window_width=fields["window_width"],
        u_rate_limit=fields["u_rate_limit"],
        integrator_limit=fields["integrator_limit"],
        abort_above=fields["abort_above"],
        abort_below=fields["abort_below"],
        slots=slots,
        schema=schema,
    )


def read_calibration(image: Path) -> HoldCalibration:
    """Read the hold settings of a flashed image from the Rolling Launch
    record of the runtime endpoint that the image carries, and for the
    current runtime from its efficiency table."""
    data = Path(image).read_bytes()
    try:
        rom, _detection = build_rom.select_rom(data, build_rom.AUTO_ROM)
    except build_rom.BuildError as error:
        raise ValueError(f"{image}: {error}") from None
    target = runtime_targets.load_runtime_target(rom)
    if target.rolling_layout is None:
        raise ValueError(f"{image}: {rom} has no Rolling Launch runtime")
    stock = target.stock_image.data
    if len(data) != len(stock):
        raise ValueError(
            f"{image}: image has {len(data)} bytes, expected {len(stock)}"
        )
    if all(
        data[offset] == stock[offset]
        for offset in calibration_ranges.load(rom).write_offsets
    ):
        state = "absent"
    else:
        state = runtime_endpoints.classify_runtime(
            data, target, str(image)
        ).rolling
    if state == "absent":
        raise ValueError(f"{image}: the image carries no Rolling Launch runtime")
    record = runtime_endpoints.configuration_record(
        data, target.rolling_layout, state
    )
    table = None
    if state == "current":
        span = target.rolling_layout.efficiency
        table = bytes(data[span.start : span.end])
    try:
        return endpoint_calibration(record, state, table)
    except ValueError as error:
        raise ValueError(f"{image}: {error}") from None


def run_slot(samples, start, end, calibration):
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
    if len(indices) != 1 or not 0 <= min(indices) < len(calibration.slots):
        raise ValueError(
            f"tick {samples[start].tick}: the capture lacks one selected map"
            " for the run of a configuration with per-map slots"
        )
    return calibration.slot(indices.pop())


def _predecessor(samples, index):
    if index and samples[index - 1].tick == samples[index].tick - 1:
        return samples[index - 1]
    return None


def _replay(samples, start, end, calibration, slot, *, error="speed_error",
            fraction="torque_fraction"):
    """Replay the speed controller through one ACTIVE run.

    `error` and `fraction` name the sample attributes of the speed error and
    the torque fraction. Return the failures, the count of checked
    fractions, and the bounds of the torque fraction at every snapshot of
    the run, None where unknown.
    """
    unit = rolling_launch.U_ONE
    rate = calibration.u_rate_limit
    previous = _predecessor(samples, start)
    integrator = bounds_now = None
    if previous is not None and previous.phase == rolling_launch.Phase.IDLE:
        integrator, bounds_now = 0, (unit, unit)
    failures = []
    law_ticks = 0
    bounds = []
    for sample in samples[start : end + 1]:
        value = getattr(sample, error)
        command = None
        if value is None:
            integrator = None
        else:
            if not -calibration.abort_below <= value <= calibration.abort_above:
                failures.append(
                    (sample.tick, "speed error outside the abort window")
                )
            if integrator is not None:
                proportional = rolling_launch.proportional_fraction(
                    value, calibration
                )
                integrator = rolling_launch.update_integrator(
                    integrator, proportional, value, calibration,
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
        if bounds_now is not None:
            low, high = bounds_now
            if command is None:
                bounds_now = max(0, low - rate), min(unit, high + rate)
            else:
                bounds_now = (
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
        published = getattr(sample, fraction)
        if published is not None:
            if command is not None and bounds_now is not None:
                law_ticks += 1
                low, high = bounds_now
                if not low <= published <= high:
                    model = low if low == high else f"{low}..{high}"
                    failures.append(
                        (sample.tick,
                         f"torque fraction {published}, model {model}")
                    )
            bounds_now = published, published
        bounds.append(bounds_now)
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
    produces, is refused. A record of the current runtime audits the runs
    by the schema 6 views of the page configurations; a historical record
    replays the speed hold of its endpoint.
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
    audit_run = _run if calibration.table is None else _current_run
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
        runs.append(audit_run(samples, start, index, calibration))
        index += 1
    return tuple(runs)


def _run(samples, start, end, calibration):
    """Audit one run of a historical speed-hold endpoint."""
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
    requested = owed = None
    floor_ticks = 0
    if calibration.hold:
        if slot.max_trim:
            floor_ticks = sum(
                stock_apc_command(sample.final_timing_raw) + slot.max_trim
                > slot.floor_command
                for sample in run
            )
        owed = _owed_cuts(
            samples, start, end, bounds, slot.trim_efficiency
        )
        if owed is not None:
            counters = [
                sample.cut_requests for sample in samples[start - 1 : end + 2]
            ]
            if None in counters:
                owed = None
            else:
                requested = sum(
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
        requested_cuts=requested,
        owed=owed,
        floor_ticks=floor_ticks,
        kind=rolling_launch.RegulatorKind.SPEED,
    )


def _bit(value, bit):
    return bool(value >> bit & 1)


def _published_kinds(sample):
    """The regulator kinds that the packed views of a snapshot publish."""
    kinds = set()
    if sample.mode_trim is not None:
        kinds.add(2 if _bit(sample.mode_trim, MODE_TRIM_SPEED_BIT) else 1)
    if sample.efficiency is not None:
        kinds.add(2 if _bit(sample.efficiency, EFFICIENCY_SPEED_BIT) else 1)
    if sample.status is not None:
        kinds.add(sample.status & STATUS_KIND_MASK)
    return kinds


def _contiguous(samples, first, last):
    return all(
        samples[index + 1].tick == samples[index].tick + 1
        for index in range(first, last)
    )


def _consumed_cuts(samples, start, end, failures):
    """Bound the cut requests of a run by the consumed q sum.

    The snapshots that publish the q sum and the cut-request counter
    together form the chain. Between two of them the six accumulators hold
    less than one cut each, so the requests lie strictly within six of the
    owed cuts; a chain interval outside that bound is a failure. Return the
    requests and the bounds of the owed cuts from the chain snapshot before
    the run, where the accumulators restart from their offsets, through the
    chain snapshot after it, or (None, None) without both of them, across a
    gap, or when an interval owes too many cuts for the 8-bit counter.
    """
    chain = [
        index for index, sample in enumerate(samples)
        if sample.consumed_q_sum is not None and sample.cut_requests is not None
    ]
    before = next((index for index in reversed(chain) if index < start), None)
    after = next((index for index in chain if index > end), None)
    complete = before is not None and after is not None
    first = before if before is not None else start
    last = after if after is not None else end
    members = [index for index in chain if first <= index <= last]
    owed_total = 0.0
    requested = 0
    for left, right in zip(members, members[1:]):
        if not _contiguous(samples, left, right):
            complete = False
            continue
        owed = ((samples[right].consumed_q_sum - samples[left].consumed_q_sum)
                & 0xFFFFFFFF) / rolling_launch.U_ONE
        cuts = (samples[right].cut_requests - samples[left].cut_requests) & 0xFF
        if owed + rolling_launch.SPARK_CYLINDER_COUNT >= 0x100:
            complete = False
            continue
        if not owed - rolling_launch.SPARK_CYLINDER_COUNT < cuts < (
            owed + rolling_launch.SPARK_CYLINDER_COUNT
        ):
            failures.append(
                (samples[right].tick, f"cut requests {cuts}, owed {owed:.3f}")
            )
        owed_total += owed
        requested += cuts
    if not complete or len(members) < 2:
        return None, None
    return requested, (
        owed_total + _OFFSET_CUTS - rolling_launch.SPARK_CYLINDER_COUNT,
        owed_total + _OFFSET_CUTS,
    )


def _released(sample):
    if sample.accepted_button is not None:
        return sample.accepted_button == rolling_launch.BUTTON_RELEASED
    if sample.status is not None:
        return _bit(sample.status, STATUS_RELEASED_BIT)
    return False


def _release_cuts(samples, end, failures):
    """The cut requests after the snapshot that shows the accepted release
    of a run, or None without that snapshot or its counters.

    The engine pass that accepts RELEASED ends the hold and clears the cut
    fraction before the snapshot, so the counter holds from that snapshot
    through the inactive snapshots that follow it.
    """
    release = end + 1
    if (
        release >= len(samples)
        or not _contiguous(samples, end, release)
        or samples[release].phase != rolling_launch.Phase.COOLDOWN
        or not _released(samples[release])
    ):
        return None
    sample = samples[release]
    if sample.cut_fraction is not None and sample.cut_fraction:
        failures.append(
            (sample.tick, f"cut fraction {sample.cut_fraction} after the accepted release")
        )
    last = release
    while (
        last + 1 < len(samples)
        and last + 1 - release < RELEASE_SNAPSHOTS
        and samples[last + 1].phase != rolling_launch.Phase.ACTIVE
        and _contiguous(samples, last, last + 1)
    ):
        last += 1
    counters = [item.cut_requests for item in samples[release : last + 1]]
    if last == release or None in counters:
        return None
    cuts = sum((right - left) & 0xFF for left, right in zip(counters, counters[1:]))
    if cuts:
        failures.append((sample.tick, f"{cuts} cut requests after the accepted release"))
    return cuts


def _current_run(samples, start, end, calibration):
    """Audit one run of the current runtime by the views that its snapshots
    carry; see the module description."""
    run = samples[start : end + 1]
    for sample in run:
        if all(getattr(sample, name) is None for name in CURRENT_VIEWS):
            raise ValueError(
                f"tick {sample.tick}: the capture lacks the Rolling Launch"
                " hold fields"
            )
    failures = []
    kinds = set().union(*(_published_kinds(sample) for sample in run))
    if 0 in kinds:
        failures.append((samples[start].tick, "regulator kind NONE in an ACTIVE run"))
    kinds.discard(0)
    if len(kinds) > 1:
        failures.append((samples[start].tick, "the regulator kind changes in the run"))
    kind = kinds.pop() if len(kinds) == 1 else None
    rpm = kind == rolling_launch.RegulatorKind.RPM
    slot = run_slot(samples, start, end, calibration)
    trims = (slot.max_trim_rpm,) if rpm else (
        (slot.max_trim_speed,) if kind is not None
        else (slot.max_trim_rpm, slot.max_trim_speed)
    )
    efficiencies = {
        calibration.table.at(trim)
        for trim in range(max(trims) + 1)
    }
    law_ticks = actuation_ticks = input_ticks = floor_ticks = 0
    targets = set()
    if kind == rolling_launch.RegulatorKind.SPEED:
        replayed, law_ticks, _bounds = _replay(
            samples, start, end, calibration, slot,
            error="control_error", fraction="law_output",
        )
        failures.extend(replayed)
    for sample in run:
        tick = sample.tick
        if rpm and sample.control_error is not None:
            coordinate = sample.control_error + slot.launch_rpm_native
            if not sample.rpm_low <= coordinate <= sample.rpm_high:
                failures.append((tick, f"RPM error {sample.control_error} off the stock engine speed"))
            if sample.law_output is not None:
                law_ticks += 1
                model = rolling_launch.rpm_fraction(
                    sample.control_error, slot.launch_soft_width_native
                )
                if sample.law_output != model:
                    failures.append((tick, f"RPM fraction {sample.law_output}, model {model}"))
        if sample.mode_trim is not None:
            applied = sample.mode_trim & MODE_TRIM_VALUE_MASK
            ready = _bit(sample.mode_trim, MODE_TRIM_READY_BIT)
            if applied > max(trims) or (not ready and applied):
                failures.append((tick, f"applied trim {applied}, trim {max(trims)}"))
            if ready and not calibration.hold:
                failures.append((tick, "an ignition command applies in observe mode"))
            if ready and applied < max(trims):
                floor_ticks += 1
        if (
            sample.efficiency is not None
            and sample.cut_fraction is not None
            and sample.law_output is not None
        ):
            actuation_ticks += 1
            efficiency = sample.efficiency & EFFICIENCY_VALUE_MASK
            ready = _bit(sample.efficiency, EFFICIENCY_READY_BIT)
            if efficiency not in efficiencies:
                failures.append((tick, f"efficiency {efficiency} outside the table of the trim"))
            elif kind is not None:
                model = 0
                if ready and rpm:
                    model = rolling_launch.U_ONE - sample.law_output
                elif ready:
                    model = rolling_launch.cut_fraction(sample.law_output, efficiency)
                if sample.cut_fraction != model:
                    failures.append((tick, f"cut fraction {sample.cut_fraction}, model {model}"))
        checked = False
        if sample.status is not None:
            checked = True
            if sample.status & STATUS_INPUTS_MASK != STATUS_INPUTS_MASK:
                failures.append((tick, "a speed input check fails in an ACTIVE snapshot"))
            if not ready_status_consistent(sample):
                failures.append((tick, f"cut fraction {sample.cut_fraction} without an applied command"))
            if sample.status & STATUS_BUTTON_MASK != 1 << STATUS_CANCEL_BIT:
                failures.append((tick, "the accepted button is not CANCEL"))
        if sample.accepted_button is not None:
            checked = True
            if sample.accepted_button != rolling_launch.BUTTON_CANCEL:
                failures.append((tick, f"accepted button 0x{sample.accepted_button:02X}"))
        if sample.speed_age is not None and calibration.speed_frame_age_limit is not None:
            checked = True
            if sample.speed_age > calibration.speed_frame_age_limit:
                failures.append((tick, f"speed frame age {sample.speed_age}"))
        if sample.selected_target is not None:
            checked = True
            targets.add(sample.selected_target)
            if rpm and sample.selected_target != slot.launch_rpm_native:
                failures.append((tick, f"target {sample.selected_target}, slot {slot.launch_rpm_native}"))
        if sample.rpm_sample is not None:
            checked = True
            if not sample.rpm_low <= sample.rpm_sample <= sample.rpm_high:
                failures.append((tick, f"RPM sample {sample.rpm_sample} off the stock engine speed"))
        if sample.stock_command is not None and sample.effective_command is not None:
            checked = True
            stock = sample.stock_command
            clipped = max(stock, min(stock + max(trims), slot.floor_command))
            if sample.effective_command not in (stock, clipped):
                failures.append((tick, f"effective command {sample.effective_command}, stock {stock}"))
        input_ticks += checked
    if len(targets) > 1:
        failures.append((samples[start].tick, "the target changes in the run"))
    speeds = [
        sample.speed_kmh * 10 - sample.control_error
        for sample in run
        if sample.speed_kmh is not None and sample.control_error is not None
    ]
    requested = owed = None
    if calibration.hold:
        requested, owed = _consumed_cuts(samples, start, end, failures)
    release_cuts = _release_cuts(samples, end, failures)
    return HoldRun(
        start_tick=samples[start].tick,
        end_tick=samples[end].tick,
        abort_reason=_abort_reason(samples, end),
        law_ticks=law_ticks,
        failures=tuple(sorted(set(failures))),
        target_speed=(
            (min(speeds), max(speeds))
            if speeds and kind == rolling_launch.RegulatorKind.SPEED else None
        ),
        requested_cuts=requested,
        owed=owed,
        floor_ticks=floor_ticks,
        kind=kind,
        actuation_ticks=actuation_ticks,
        input_ticks=input_ticks,
        release_cuts=release_cuts,
    )


def ready_status_consistent(sample):
    """A snapshot without an applied ignition command publishes no cut
    fraction."""
    return (
        sample.cut_fraction is None
        or _bit(sample.status, STATUS_READY_BIT)
        or not sample.cut_fraction
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
        "cut_requests", "control_error", "law_output", "consumed_q_sum",
        "app1_raw", "fuel_inhibit_mask",
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


def _speed_error(sample, kind):
    if sample.speed_error is not None:
        return sample.speed_error
    if kind == rolling_launch.RegulatorKind.SPEED:
        return sample.control_error
    return None


def _speed_targets(samples, times, bus, kind=rolling_launch.RegulatorKind.SPEED):
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
            error = _speed_error(sample, kind)
            if error is None:
                continue
            index = bisect.bisect_right(bus[can_id].times, time)
            words = [
                decode_speed_word(data) - error
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


def release_cut_request_timing(capture, start_index, exit_index, release_ms, rpm_frames):
    """Bound cut-request counter events between adjacent coherent snapshots.

    The counter counts requested cuts, not withheld sparks. Phase is fixed
    page 2, current every tick. The button attribute is host
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
                or previous.cut_requests is None
                or sample.cut_requests is None):
            complete = False
            continue
        deltas[index] = (sample.cut_requests - previous.cut_requests) & 0xFF
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
        "requested_cuts_after_release_bounds": [
            sum(count for i, count in deltas.items() if times[i - 1] >= release_ms),
            sum(count for i, count in deltas.items() if times[i] > release_ms),
        ] if complete else None,
        "requested_cuts_after_phase_exit_snapshot": (
            sum(count for i, count in deltas.items() if i > exit_index)
            if complete else None
        ),
        "inactive_snapshots_checked": stop - exit_index - 1,
        "inactive_observation_ms": times[stop - 1] - times[exit_index],
        "counter_window_complete": complete,
        "last_increment_snapshot_tick": None,
        "last_increment_snapshot_ms": None,
        "last_cut_request_offset_ms_bounds": None,
        "last_cut_request_cycles_bounds": None,
    }
    if not changes:
        return result
    last = changes[-1]
    bounds = [times[last - 1] - release_ms, times[last] - release_ms]
    result.update(last_increment_snapshot_tick=samples[last].tick,
                  last_increment_snapshot_ms=times[last],
                  last_cut_request_offset_ms_bounds=bounds)
    rpm_frame = rpm_frames.before(times[last])
    if rpm_frame is None or len(rpm_frame[1]) < 2:
        return result
    rpm = int.from_bytes(rpm_frame[1][:2], "big") / 8
    cycles = [ms * rpm / 120000 for ms in bounds]
    result.update(last_cut_request_rpm=rpm, last_cut_request_cycles_bounds=cycles,
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
            capture.samples[start_index:end_index], times[:-1], bus, run.kind
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
        cut_timing = release_cut_request_timing(capture, start_index, end_index, release, bus[0x180])
        if run.abort_reason == rolling_launch.AbortReason.BUTTON_RELEASED:
            # The runtime consumes the stable input after the stock ASCD
            # task and aborts in that pass. The input byte itself is absent.
            cut_timing["ecu_release_inferred_ms_bounds"] = [
                capture.timing.first_page_ms[end_index - 1], end,
            ]
            last = cut_timing["last_increment_snapshot_ms"]
            if (last is not None and "last_cut_request_rpm" in cut_timing
                    and cut_timing["counter_window_complete"]):
                upper = max(0, last - capture.timing.first_page_ms[end_index - 1])
                cut_timing["last_cut_request_after_ecu_release_upper_ms"] = upper
                cut_timing["last_cut_request_after_ecu_release_upper_cycles"] = (
                    upper * cut_timing["last_cut_request_rpm"] / 120000
                )
        elif run.abort_reason in (
            rolling_launch.AbortReason.PEDAL_LOW, rolling_launch.AbortReason.RPM_LOW,
        ):
            # A released stable input overrides these gate reasons with
            # BUTTON_RELEASED. It has not been accepted at this abort pass.
            cut_timing["ecu_release_inferred_not_before_ms"] = end
            last = cut_timing["last_increment_snapshot_ms"]
            if (last is not None and "last_cut_request_rpm" in cut_timing
                    and cut_timing["counter_window_complete"]):
                upper = max(0, last - end)
                cut_timing["last_cut_request_after_ecu_release_upper_ms"] = upper
                cut_timing["last_cut_request_after_ecu_release_upper_cycles"] = (
                    upper * cut_timing["last_cut_request_rpm"] / 120000
                )
        row["cut_request_release"] = cut_timing
        last = cut_timing["last_increment_snapshot_ms"]
        row["last_cut_request_after_release_ms"] = (
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
    print(f"{args.image.name} rolling_launch={calibration.endpoint}")
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
            requested = "n/a"
            if run.requested_cuts is not None:
                low, high = run.owed
                requested = f"{run.requested_cuts} owed ({low:.2f}, {high:.2f}]"
            kind = "unknown" if run.kind is None else rolling_launch.RegulatorKind(run.kind).name
            release = "n/a" if run.release_cuts is None else str(run.release_cuts)
            print(
                f"  ticks {run.start_tick}..{run.end_tick}"
                f" kind={kind}"
                f" abort={_reason_name(run.abort_reason)}"
                f" law_ticks={run.law_ticks}"
                f" actuation_ticks={run.actuation_ticks}"
                f" input_ticks={run.input_ticks}"
                f" failed_ticks={len({tick for tick, _ in run.failures})}"
                f" target={target}"
                f" requested_cuts={requested}"
                f" floor_ticks={run.floor_ticks}"
                f" release_cuts={release}"
            )
            for tick, failure in run.failures:
                print(f"    tick {tick}: {failure}")
            failed |= (
                bool(run.failures)
                or run.requested_cuts_inside is False
                or not run.checked_ticks
            )
        if args.bus_json:
            reference = read_mlg(args.reference_mlg) if args.reference_mlg else capture
            reference_runs = audit_hold(reference.samples, calibration)
            failed |= not reference_runs or any(
                run.failures or run.requested_cuts_inside is False
                or not run.checked_ticks
                for run in reference_runs
            )
            result = audit_bus(capture, reference_runs, reference=reference)
            args.bus_json.write_text(json.dumps(result, indent=2) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
