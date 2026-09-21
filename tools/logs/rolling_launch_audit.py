#!/usr/bin/env python3
"""Audit JK08A Rolling Launch activations in a tuning MLG or TRC capture.

An activation is a CANCEL hold of stock frame 0x239 during which frame 0x551
starts showing the ACTIVE dashboard state. The Rolling Launch configuration
record is read from the calibration image and replayed through the
independent runtime model in `patches/rolling_launch.py`. The captured native
RPM is bounded by the RPM words around the capture and by every full
fuel-inhibit transition while the runtime certainly holds its window. The
audit also reports the full-mask cycles, the retard-only bound of the APC
command, the `110 - final timing = APC command` identity inside and outside
the activations, the release-to-clear distance, the rearm spacing, and the
timeout margin. Distances are counted in telemetry ticks, so every event time
is bounded by the snapshot spacing rather than resolved inside it. The records
whose compared RPM word can carry the captured word bound the activation pass,
and a stock APC command with a clear mask at RPM words that reach every
consistent cut word bounds the end of `ACTIVE`.

A TRC adds frame times. The `trace_` figures split the 0x239 CANCEL frames
into holds and map-selection taps, count the dashboard states of frame 0x551
in each hold, and measure the release-to-clear distance from the first
released 0x239 frame to the first and the completing frame of the telemetry
group that clears the full mask.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
import hashlib
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_layout
from patches import rolling_launch
from patches import rolling_launch_layout
from tools.can_dashboard import recording
from tools.can_dashboard.model import (
    ASCD_BUTTON_ID,
    DASHBOARD_STATE_ID,
    DashboardModel,
    FrameRecord,
)
from tools.logs import cvtc_target_audit
from tools.logs import mlg_relation_audit
from tools.logs import mlg_retime
from tools.logs import peak_trc_audit
from tools.mapkit import rom as romkit

FULL_MASK = 0x3F
APC_COMMAND_BASE = mlg_relation_audit.APC_COMMAND_BASE
RPM_PER_COUNT = recording.MLG_CALIBRATIONS["rpm_raw"].factor
APP1_VOLTS_PER_COUNT = recording.MLG_CALIBRATIONS["app1_raw"].factor
ACTIVE_STATE = rolling_launch.ASCD_FEEDBACK_CRUISE_SET >> 4
FAILED_STATE = rolling_launch.ASCD_FEEDBACK_CRUISE >> 4
EXHAUST_FAMILY = "exhaust_cvtc_target"
# The capture pass follows the debounced CANCEL, which never precedes the
# first CANCEL frame; three snapshots before the first CANCEL record cover the
# arrival of that frame inside the snapshot interval and the prior-pass copy
# of the RPM word.
CAPTURE_LEAD_RECORDS = 3
# The APC command of a record can follow the compared RPM word of the pass
# before the preceding record.
EXIT_LAG_RECORDS = 2
TELEMETRY_SOURCES = (
    "rpm_raw",
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
class LaunchCalibration:
    image_source: Path
    image_sha256: str
    configuration: rolling_launch.Calibration
    configuration_hex: str
    tick_seconds: float
    exhaust_replays: tuple[cvtc_target_audit.CvtcCalibration, ...]


@dataclass(frozen=True)
class Sample:
    tick: int
    button: int | None
    dashboard: int | None
    speed_kmh: float | None
    coolant_raw: int | None
    rpm_raw: int
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


def load_calibration(
    calibration_image: Path, rom: str = "JK08A"
) -> LaunchCalibration:
    image_source = Path(calibration_image).resolve()
    image = romkit.Image(
        image_source.name, str(image_source), image_source.read_bytes()
    )
    layout = rolling_launch_layout.load_layout()
    record = image.data[layout.configuration.start : layout.configuration.end]
    configuration = rolling_launch.Calibration.from_bytes(record)
    if not configuration.is_valid():
        raise ValueError(
            f"{image_source}: no valid Rolling Launch configuration at "
            f"0x{layout.configuration.start:06X}"
        )
    exhaust = cvtc_target_audit.load_calibration(rom, image_source, "exhaust")
    family = map_switching_layout.load_layout().family_by_key[EXHAUST_FAMILY]
    size = len(exhaust.main.row_axis)
    replays = tuple(
        replace(
            exhaust,
            main=replace(
                exhaust.main,
                address=address,
                table=tuple(
                    tuple(row) for row in image.table(address, size, size, "uint8")
                ),
            ),
        )
        for address in family.all_slot_addresses
    )
    return LaunchCalibration(
        image_source=image_source,
        image_sha256=hashlib.sha256(image.data).hexdigest(),
        configuration=configuration,
        configuration_hex=record.hex(),
        tick_seconds=layout.scheduler.tick_microseconds / 1_000_000,
        exhaust_replays=replays,
    )


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


def _sample(tick: int, value) -> Sample:
    return Sample(
        tick=tick,
        button=_optional_int(value("ascd_button_raw")),
        dashboard=_optional_int(value("dashboard_state_raw")),
        speed_kmh=_optional_float(value("vehicle_speed_kmh")),
        coolant_raw=_optional_int(value("coolant_raw")),
        **{name: int(value(name)) for name in TELEMETRY_SOURCES},
    )


def read_mlg(path: Path) -> Capture:
    """Read the verified snapshots of one dashboard MLVLG recording."""
    recording_ = mlg_relation_audit.read_recording(path)
    columns = recording_.columns
    required = ("tick16", "schema_verified", *TELEMETRY_SOURCES, *CONTEXT_SOURCES)
    missing = [name for name in required if name not in columns]
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
        samples.append(_sample(tick, lambda name: columns[name][index]))
    return Capture(Path(path), recording_.sha256, tuple(samples))


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
        if run is None:
            run = snapshot.run
        elif snapshot.run != run:
            raise ValueError(f"{path}: the capture spans more than one producer run")

        def value(name):
            if name in model.raw:
                return model.raw[name]
            return getattr(model, name, None)

        samples.append(_sample(snapshot.unwrapped_tick, value))
        first_pages.append(group_start)
        last_pages.append(frame.offset_ms)
    timing = TraceTiming(
        tuple(first_pages), tuple(last_pages), tuple(buttons), tuple(dashboard)
    )
    return Capture(path, digest, tuple(samples), timing)


def read_capture(path: Path, **options) -> Capture:
    if Path(path).suffix.lower() == ".trc":
        return read_trc(path, **options)
    return read_mlg(path)


def runs(flags: list[bool]) -> list[tuple[int, int]]:
    """Return maximal half-open index runs where the flag is set."""
    result = []
    start = None
    for index, flag in enumerate(flags):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            result.append((start, index))
            start = None
    if start is not None:
        result.append((start, len(flags)))
    return result


def _active_state(
    configuration: rolling_launch.Calibration, slot: int, captured: int
) -> rolling_launch.RuntimeState | None:
    """Return the model state that captures one RPM word, if it activates."""
    inputs = rolling_launch.Inputs(
        active_index=slot,
        button=rolling_launch.BUTTON_CANCEL,
        speed=configuration.min_speed,
        rpm_native=captured,
        pedal=configuration.min_pedal,
        coolant=configuration.coolant_min,
    )
    state = rolling_launch.step(
        rolling_launch.RuntimeState(), inputs, configuration
    ).state
    if state.phase != rolling_launch.Phase.ACTIVE:
        return None
    return state


def thresholds(
    configuration: rolling_launch.Calibration, slot: int, captured: int
) -> tuple[int, int] | None:
    """Return the model cut and restore words for one captured RPM word."""
    state = _active_state(configuration, slot, captured)
    if state is None:
        return None
    return state.cut_rpm_native, state.restore_rpm_native


def _rpm_hull(samples: tuple[Sample, ...], index: int) -> tuple[int, int] | None:
    """Bound the compared RPM word, copied between two adjacent captures."""
    if index == 0 or samples[index].tick - samples[index - 1].tick != 1:
        return None
    first = samples[index - 1].rpm_raw
    second = samples[index].rpm_raw
    return min(first, second), max(first, second)


def _certain_end(samples, configuration, start, active_start, release) -> int:
    """Return the end of the records in which the runtime certainly holds.

    The runtime keeps the temporary window until the CANCEL release unless the
    run timeout or the minimum-RPM gate aborts it first. The capture pass is
    no earlier than the snapshot before the first CANCEL record.
    """
    timeout_tick = samples[start].tick - 1 + configuration.run_timeout_ticks
    for index in range(active_start, release):
        if samples[index].tick >= timeout_tick:
            return index
        hull = _rpm_hull(samples, index)
        low = hull[0] if hull is not None else samples[index].rpm_raw
        if low < configuration.min_rpm_native:
            return index
    return release


def _mask_constraints(samples, active_start, certain_end, window_end):
    constraints = []
    for index in range(active_start, window_end):
        hull = _rpm_hull(samples, index)
        if hull is None:
            continue
        prior = samples[index - 1].fuel_inhibit_mask
        current = samples[index].fuel_inhibit_mask
        if prior not in (0, FULL_MASK) or current not in (0, FULL_MASK):
            continue
        if current == FULL_MASK:
            # A full mask far below the map limiter needs the temporary window.
            kind = "reach_restore" if prior == FULL_MASK else "reach_cut"
        elif index >= certain_end:
            # After the release or a possible abort the runtime may already
            # have restored the map limiter, so a clear mask no longer bounds
            # the window.
            continue
        else:
            kind = "below_restore" if prior == FULL_MASK else "below_cut"
        constraints.append((kind, hull))
    return constraints


def _satisfies(window: tuple[int, int], constraints) -> bool:
    cut, restore = window
    for kind, (low, high) in constraints:
        if kind == "reach_cut" and high < cut:
            return False
        if kind == "reach_restore" and high < restore:
            return False
        if kind == "below_cut" and low >= cut:
            return False
        if kind == "below_restore" and low >= restore:
            return False
    return True


def _stock_command(sample: Sample) -> int:
    return (APC_COMMAND_BASE - sample.final_timing_raw) & 0xFF


def _identity_differs(sample: Sample) -> bool:
    return _stock_command(sample) != sample.apc_command_raw


def _capture_records(samples, start, lead, active_start, words) -> list[int]:
    """Bound the capture pass by the records that can carry a captured word.

    The offsets count ticks from the first CANCEL record. The pass lies
    between the preceding snapshot and a record whose compared RPM word can
    equal a consistent captured word, and it precedes the ACTIVE indication.
    """
    offsets = []
    for index in range(max(lead, 1), active_start + 1):
        hull = _rpm_hull(samples, index)
        if hull is not None and any(hull[0] <= word <= hull[1] for word in words):
            offsets.append(samples[index].tick - samples[start].tick)
    return [min(offsets), max(offsets)] if offsets else []


def _exit_records(
    samples, configuration, slot, cuts, active_start, window_end
) -> tuple[int, int] | None:
    """Return the last retarded record and the first record that excludes ACTIVE.

    At or above the cut word the ACTIVE controller commands the target and the
    temporary window cuts fuel. A record whose stock command stays below the
    target with a clear mask, while its RPM word and the two before it reach
    every consistent cut word, excludes ACTIVE even when the command follows
    an earlier compared word.
    """
    target = configuration.target_commands[slot]
    last_retarded = None
    for index in range(active_start, min(window_end + 1, len(samples))):
        sample = samples[index]
        stock = _stock_command(sample)
        if sample.apc_command_raw != stock:
            last_retarded = index
            continue
        if (
            last_retarded is not None
            and cuts
            and index >= EXIT_LAG_RECORDS
            and stock < target
            and sample.fuel_inhibit_mask == 0
            and all(
                samples[index - lag].tick == sample.tick - lag
                and samples[index - lag].rpm_raw >= max(cuts)
                for lag in range(EXIT_LAG_RECORDS + 1)
            )
        ):
            return last_retarded, index
    return None


def within_retard_bound(stock: int, command: int, target: int) -> bool:
    """Return whether a command is retard-only and bounded by the target.

    A larger command is later timing. The controller moves from the stock
    command toward the target, retains a stock command that is already equal
    or later, and never commands earlier timing than stock.
    """
    return stock <= command <= max(stock, target)


def exhaust_surface_matches(
    samples: tuple[Sample, ...], calibration: LaunchCalibration
) -> tuple[int, list[int]]:
    """Count records whose exhaust target each map slot's surface reproduces.

    The common target is compared with the replay at the prior snapshot, the
    code-proven coordinate of `cvtc_target_audit.py`.
    """
    comparisons = 0
    counts = [0] * len(calibration.exhaust_replays)
    for index in range(1, len(samples)):
        prior = samples[index - 1]
        current = samples[index]
        if current.tick - prior.tick != 1 or prior.coolant_raw is None:
            continue
        point = cvtc_target_audit.CvtcSample(
            timestamp=0.0,
            run=0,
            tick=prior.tick,
            bfs_raw=prior.bfs_raw,
            rpm_raw=prior.rpm_raw,
            coolant_raw=prior.coolant_raw,
            coolant_age_ms=0.0,
            knock_surface_state=prior.knock_surface_state,
            reference_a_raw=0,
            reference_b_raw=current.exhaust_cvtc_target_raw,
            intake_actual_b1_raw=0,
            intake_actual_b2_raw=0,
        )
        comparisons += 1
        for slot, replay in enumerate(calibration.exhaust_replays):
            selected = cvtc_target_audit.replay_point(replay, point)
            if selected.coolant_selected_raw == current.exhaust_cvtc_target_raw:
                counts[slot] += 1
    return comparisons, counts


def _rounded(value: float, digits: int = 3) -> float:
    return round(value + 0.0, digits)


def _state_runs(frames, state: int) -> list[tuple[float, float, int]]:
    """Return the first time, last time, and frame count of each state run."""
    field = rolling_launch.ASCD_FEEDBACK_MASK
    flags = [
        value is not None and value & field == (state << 4) & field
        for _, value in frames
    ]
    return [
        (frames[first][0], frames[stop - 1][0], stop - first)
        for first, stop in runs(flags)
    ]


def trace_figures(
    timing: TraceTiming,
    activations,
    clears: list[int | None],
    *,
    active_state: int = ACTIVE_STATE,
    failed_state: int = FAILED_STATE,
) -> dict:
    """Split the CANCEL frames into holds and taps and time the activations.

    A hold is a CANCEL frame run between released frames, and a tap is a
    CANCEL frame run next to a SET frame. The dashboard run of a hold is the
    first run of a state that starts after the first CANCEL frame and before
    the next pressed frame after the release. A clear record carries the first
    clear mask after a full mask at or after the release.
    """
    buttons = timing.button_frames
    released = rolling_launch.BUTTON_RELEASED
    holds = []
    taps = 0
    for first, stop in runs(
        [code == rolling_launch.BUTTON_CANCEL for _, code in buttons]
    ):
        neighbours = (
            buttons[first - 1][1] if first else None,
            buttons[stop][1] if stop < len(buttons) else None,
        )
        if rolling_launch.BUTTON_SET in neighbours:
            taps += 1
        elif neighbours == (released, released):
            pressed = next(
                (time for time, code in buttons[stop:] if code != released),
                math.inf,
            )
            holds.append((buttons[first][0], buttons[stop][0], pressed))
    active_runs = _state_runs(timing.dashboard_frames, active_state)
    failed_runs = _state_runs(timing.dashboard_frames, failed_state)

    def hold_run(state_runs, hold):
        begin, _, pressed = hold
        return next((run for run in state_runs if begin < run[0] < pressed), None)

    delays = []
    inactive_held = []
    release_clear = []
    for (start, *_), clear in zip(activations, clears):
        moment = timing.last_page_ms[start]
        hold = next((hold for hold in holds if hold[0] <= moment < hold[1]), None)
        run = hold_run(active_runs, hold) if hold is not None else None
        if run is None:
            raise ValueError(
                f"no ACTIVE frame run follows the CANCEL frames before "
                f"{moment / 1000:.3f} s"
            )
        begin, end, _ = hold
        delays.append(_rounded(run[0] - begin, 1))
        inactive_held.append(
            sum(1 for time, _ in timing.dashboard_frames if run[1] < time < end)
        )
        release_clear.append(
            [
                _rounded(timing.first_page_ms[clear] - end, 1),
                _rounded(timing.last_page_ms[clear] - end, 1),
            ]
            if clear is not None and clear < len(timing.last_page_ms)
            else []
        )
    return {
        "trace_cancel_frame_count": sum(
            1 for _, code in buttons if code == rolling_launch.BUTTON_CANCEL
        ),
        "trace_active_frame_count": sum(run[2] for run in active_runs),
        "trace_failed_frame_count": sum(run[2] for run in failed_runs),
        "trace_gesture_tap_count": taps,
        "trace_hold_count": len(holds),
        "trace_hold_start_seconds": [_rounded(hold[0] / 1000) for hold in holds],
        "trace_hold_seconds": [_rounded((hold[1] - hold[0]) / 1000) for hold in holds],
        "trace_hold_active_frames": [
            run[2] if run is not None else 0
            for run in (hold_run(active_runs, hold) for hold in holds)
        ],
        "trace_hold_failed_frames": [
            run[2] if run is not None else 0
            for run in (hold_run(failed_runs, hold) for hold in holds)
        ],
        "trace_hold_since_previous_release_ms": [
            _rounded(holds[index][0] - holds[index - 1][1], 1)
            for index in range(1, len(holds))
        ],
        "trace_activation_active_delay_ms": delays,
        "trace_activation_inactive_frames_held": inactive_held,
        "trace_activation_release_clear_ms": release_clear,
    }


def audit_capture(
    capture: Capture,
    calibration: LaunchCalibration,
    *,
    selected_map: int,
    active_state: int = ACTIVE_STATE,
    failed_state: int = FAILED_STATE,
) -> dict:
    samples = capture.samples
    if len(samples) < 2:
        raise ValueError(f"{capture.path}: fewer than two verified snapshots")
    configuration = calibration.configuration
    slot = selected_map - 1
    if not configuration.enabled_for(slot):
        raise ValueError(
            f"Map {selected_map} is not enabled for Rolling Launch in "
            f"{calibration.image_source.name}"
        )
    target = configuration.target_commands[slot]
    period = calibration.tick_seconds
    first_tick = samples[0].tick

    def seconds(index: int) -> float:
        return (samples[index].tick - first_tick) * period

    def span(start: int, stop: int) -> float:
        return (samples[stop].tick - samples[start].tick) * period

    field = rolling_launch.ASCD_FEEDBACK_MASK
    active = [
        sample.dashboard is not None
        and sample.dashboard & field == (active_state << 4) & field
        for sample in samples
    ]
    failed = [
        sample.dashboard is not None
        and sample.dashboard & field == (failed_state << 4) & field
        for sample in samples
    ]
    holds = runs([sample.button == rolling_launch.BUTTON_CANCEL for sample in samples])
    set_holds = runs([sample.button == rolling_launch.BUTTON_SET for sample in samples])
    active_runs = runs(active)

    activations = []
    refused = []
    for start, release in holds:
        paired = [run for run in active_runs if start <= run[0] < release]
        if not paired:
            refused.append((start, release))
            continue
        if len(paired) > 1 or release >= len(samples):
            raise ValueError(
                f"{capture.path}: CANCEL hold at {seconds(start):.3f} s has "
                "no single complete ACTIVE interval"
            )
        active_start, active_end = paired[0]
        window_end = max(active_end, release)
        while (
            window_end < len(samples)
            and samples[window_end].fuel_inhibit_mask == FULL_MASK
        ):
            window_end += 1
        activations.append((start, release, active_start, active_end, window_end))

    inside = [False] * len(samples)
    rows = []
    clears = []
    previous_release = None
    for start, release, active_start, active_end, window_end in activations:
        for index in range(start, window_end):
            inside[index] = True
        hold = samples[start:release]
        window = samples[start:window_end]
        lead = max(0, start - CAPTURE_LEAD_RECORDS)
        capture_rpm = [sample.rpm_raw for sample in samples[lead : active_start + 1]]
        certain_end = _certain_end(
            samples, configuration, start, active_start, release
        )
        constraints = _mask_constraints(
            samples, active_start, certain_end, window_end
        )
        candidates = []
        for captured in range(min(capture_rpm), max(capture_rpm) + 1):
            window_words = thresholds(configuration, slot, captured)
            if window_words is not None and _satisfies(window_words, constraints):
                candidates.append((captured, *window_words))
        mask_runs = [
            (first + start, stop + start)
            for first, stop in runs([s.fuel_inhibit_mask == FULL_MASK for s in window])
        ]
        full_rpm = [s.rpm_raw for s in window if s.fuel_inhibit_mask == FULL_MASK]
        after_release = [
            index
            for index in range(release, window_end)
            if samples[index].fuel_inhibit_mask == FULL_MASK
        ]
        clear = after_release[-1] + 1 if after_release else release
        # The release frame arrives between the last hold record and the
        # release record, and the mask clears between the last full record
        # and the clear record.
        full_at_release = bool(after_release) or (
            samples[release - 1].fuel_inhibit_mask == FULL_MASK
        )
        clear_low = (
            samples[clear - 1].tick - samples[release].tick if clear > release else 0
        )
        clear_high = samples[clear].tick - samples[release - 1].tick
        # A clear record whose compared RPM word cannot fall below any
        # consistent restore word needs the removal of the window.
        clear_hull = _rpm_hull(samples, clear)
        removal = (
            full_at_release
            and bool(candidates)
            and clear_hull is not None
            and clear_hull[0] >= max(c[2] for c in candidates)
        )
        clears.append(clear if full_at_release else None)
        stock = [_stock_command(s) for s in samples[active_start:release]]
        words = [c[0] for c in candidates]
        capture_records = _capture_records(
            samples, start, lead, active_start, words
        )
        exit_pair = _exit_records(
            samples,
            configuration,
            slot,
            [c[1] for c in candidates],
            active_start,
            window_end,
        )
        exit_records = (
            [samples[index].tick - samples[start].tick for index in exit_pair]
            if exit_pair is not None
            else []
        )
        # The capture pass follows the snapshot before a capture record. The
        # command of the last retarded record can come from the pass before
        # that record, and the exit pass precedes the witness record.
        active_ticks = (
            [
                exit_records[0] - capture_records[1],
                exit_records[1] - capture_records[0],
            ]
            if capture_records and exit_records
            else []
        )
        # The release frame arrives after the snapshot before the release
        # record, and the exit follows the release only when the last retarded
        # record does.
        release_offset = samples[release].tick - samples[start].tick
        release_exit = (
            [
                _rounded((exit_records[0] - 1 - release_offset) * period * 1000, 1),
                _rounded((exit_records[1] - release_offset + 1) * period * 1000, 1),
            ]
            if exit_records and exit_records[0] - 1 >= release_offset
            else []
        )
        rows.append(
            {
                "start_seconds": _rounded(seconds(start)),
                "hold_seconds": _rounded(span(start, release)),
                "active_indication_seconds": _rounded(span(active_start, active_end)),
                "speed_kmh": _rounded(hold[0].speed_kmh or 0.0, 2),
                "speed_range_kmh": [
                    _rounded(min(s.speed_kmh or 0.0 for s in hold), 2),
                    _rounded(max(s.speed_kmh or 0.0 for s in hold), 2),
                ],
                "app1_range_v": [
                    _rounded(min(s.app1_raw for s in hold) * APP1_VOLTS_PER_COUNT),
                    _rounded(max(s.app1_raw for s in hold) * APP1_VOLTS_PER_COUNT),
                ],
                "rpm_range": [
                    min(s.rpm_raw for s in hold) * RPM_PER_COUNT,
                    max(s.rpm_raw for s in hold) * RPM_PER_COUNT,
                ],
                "captured_rpm_native": (
                    [candidates[0][0], candidates[-1][0]] if candidates else []
                ),
                "captured_rpm": (
                    [
                        candidates[0][0] * RPM_PER_COUNT,
                        candidates[-1][0] * RPM_PER_COUNT,
                    ]
                    if candidates
                    else []
                ),
                "cut_rpm": (
                    [
                        candidates[0][1] * RPM_PER_COUNT,
                        candidates[-1][1] * RPM_PER_COUNT,
                    ]
                    if candidates
                    else []
                ),
                "restore_rpm": (
                    [
                        min(c[2] for c in candidates) * RPM_PER_COUNT,
                        max(c[2] for c in candidates) * RPM_PER_COUNT,
                    ]
                    if candidates
                    else []
                ),
                "capture_records": capture_records,
                "mask_constraint_count": len(constraints),
                "full_mask_cycles": sum(1 for first, _ in mask_runs if first < release),
                "post_release_full_mask_cycles": sum(
                    1 for first, _ in mask_runs if first >= release
                ),
                "full_mask_rpm": (
                    [min(full_rpm) * RPM_PER_COUNT, max(full_rpm) * RPM_PER_COUNT]
                    if full_rpm
                    else []
                ),
                "apc_max": max(s.apc_command_raw for s in window),
                "apc_target_records": sum(
                    1 for s in window if s.apc_command_raw == target
                ),
                "apc_outside_bound_records": sum(
                    1
                    for s in window
                    if not within_retard_bound(
                        _stock_command(s), s.apc_command_raw, target
                    )
                ),
                "stock_command_range": [min(stock), max(stock)],
                "identity_differences_hold": sum(
                    1 for s in hold if _identity_differs(s)
                ),
                "identity_differences_post_release": sum(
                    1 for s in samples[release:window_end] if _identity_differs(s)
                ),
                "exit_records": exit_records,
                "active_ticks_bound": active_ticks,
                "release_exit_bound_ms": release_exit,
                "release_full_mask": full_at_release,
                "release_clear_records": samples[clear].tick - samples[release].tick,
                "release_clear_bound_ms": (
                    [
                        _rounded(clear_low * period * 1000, 1),
                        _rounded(clear_high * period * 1000, 1),
                    ]
                    if full_at_release
                    else []
                ),
                "release_clear_by_window_removal": removal,
                "rearm_spacing_seconds": (
                    _rounded(span(previous_release, start))
                    if previous_release is not None
                    else None
                ),
            }
        )
        previous_release = release

    comparisons, exhaust_counts = exhaust_surface_matches(samples, calibration)
    differences = [_identity_differs(sample) for sample in samples]
    full = [sample.fuel_inhibit_mask == FULL_MASK for sample in samples]
    timeout_seconds = configuration.run_timeout_ticks * period
    hold_lengths = [span(start, stop) for start, stop in holds if stop < len(samples)]
    spacings = [
        row["rearm_spacing_seconds"]
        for row in rows
        if row["rearm_spacing_seconds"] is not None
    ]
    result = {
        "capture_name": capture.path.name,
        "capture_sha256": capture.sha256,
        "calibration_image_sha256": calibration.image_sha256,
        "configuration_hex": calibration.configuration_hex,
        "selected_map": selected_map,
        "mode": rolling_launch.Mode(configuration.mode).name.lower(),
        "enabled_maps": [
            index + 1
            for index in range(rolling_launch.SLOT_COUNT)
            if configuration.enabled_for(index)
        ],
        "target_command": target,
        "tick_seconds": period,
        "snapshot_count": len(samples),
        "snapshot_gap_count": sum(
            1
            for index in range(1, len(samples))
            if samples[index].tick - samples[index - 1].tick != 1
        ),
        "span_seconds": _rounded(seconds(len(samples) - 1)),
        "exhaust_cvtc_comparison_count": comparisons,
        "exhaust_cvtc_slot_exact_counts": exhaust_counts,
        "cancel_hold_count": len(holds),
        "set_hold_count": len(set_holds),
        "active_indication_interval_count": len(active_runs),
        "failed_attempt_record_count": sum(failed),
        "activation_count": len(rows),
        "refused_hold_count": len(refused),
        "gesture_tap_count": sum(
            1
            for start, release in refused
            if (start and samples[start - 1].button == rolling_launch.BUTTON_SET)
            or (
                release < len(samples)
                and samples[release].button == rolling_launch.BUTTON_SET
            )
        ),
        "full_mask_record_count": sum(full),
        "full_mask_outside_record_count": sum(
            1 for flag, within in zip(full, inside) if flag and not within
        ),
        "partial_mask_record_count": sum(
            1 for sample in samples if sample.fuel_inhibit_mask not in (0, FULL_MASK)
        ),
        "identity_pair_count": len(samples),
        "identity_count": len(samples) - sum(differences),
        "identity_difference_inside_count": sum(
            1 for flag, within in zip(differences, inside) if flag and within
        ),
        "identity_difference_outside_count": sum(
            1 for flag, within in zip(differences, inside) if flag and not within
        ),
        "timeout_seconds": _rounded(timeout_seconds),
        "longest_hold_seconds": _rounded(max(hold_lengths, default=0.0)),
        "timeout_exercised": any(length >= timeout_seconds for length in hold_lengths),
        "rearm_seconds": _rounded(configuration.rearm_ticks * period),
        "minimum_rearm_spacing_seconds": _rounded(min(spacings, default=0.0)),
    }
    for key in rows[0] if rows else ():
        values = [row[key] for row in rows]
        if key == "rearm_spacing_seconds":
            values = values[1:]
        result[f"activation_{key}"] = values
    if capture.timing is not None:
        result.update(
            trace_figures(
                capture.timing,
                activations,
                clears,
                active_state=active_state,
                failed_state=failed_state,
            )
        )
    return result


def format_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, (list, tuple)):
        return "[" + ", ".join(format_value(item) for item in value) + "]"
    return '"' + str(value).replace('"', '\\"') + '"'


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("captures", nargs="+", type=Path)
    parser.add_argument("--rom", default="JK08A")
    parser.add_argument("--calibration-image", type=Path, required=True)
    parser.add_argument(
        "--map",
        type=int,
        required=True,
        choices=range(1, rolling_launch.SLOT_COUNT + 1),
        dest="selected_map",
        help="selected map declared for the capture",
    )
    parser.add_argument("--active-state", type=int, default=ACTIVE_STATE)
    parser.add_argument("--failed-state", type=int, default=FAILED_STATE)
    parser.add_argument("--profile", default="tuning")
    parser.add_argument(
        "--can-id", type=lambda value: int(value, 0), default=0x6F0
    )
    parser.add_argument("--tick-divisor", type=int, default=1)
    args = parser.parse_args(argv)
    try:
        calibration = load_calibration(args.calibration_image, args.rom)
        for index, path in enumerate(args.captures):
            if index:
                print()
            options = {}
            if path.suffix.lower() == ".trc":
                options = {
                    "profile": args.profile,
                    "can_id": args.can_id,
                    "tick_divisor": args.tick_divisor,
                }
            result = audit_capture(
                read_capture(path, **options),
                calibration,
                selected_map=args.selected_map,
                active_state=args.active_state,
                failed_state=args.failed_state,
            )
            for key, value in result.items():
                print(f"{key} = {format_value(value)}")
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
