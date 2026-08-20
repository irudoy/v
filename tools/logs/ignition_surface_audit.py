#!/usr/bin/env python3
"""Replay JK08A hot ignition surfaces against a verified wide54 TRC."""

from __future__ import annotations

import argparse
from bisect import bisect_right
from collections import Counter
from dataclasses import dataclass
import hashlib
from pathlib import Path
import statistics
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches.map_switching_layout import load_layout
from tools.can_dashboard.model import DashboardModel, FrameRecord
from tools.logs import peak_trc_audit
from tools.logs.cvtc_target_audit import explicit_axis_position
from tools.logs.load_axis_audit import internal_load_raw
from tools.mapkit import rom as romkit


INTERNAL_LOAD_SCALER_ADDRESS = 0x9534
IGNITION_MAIN_MAP_ADDRESS = 0x9A1A
IGNITION_HIGH_DET_MAP_ADDRESS = 0x9B1A
IGNITION_RPM_AXIS_ADDRESS = 0x11ECE
IGNITION_LOAD_AXIS_ADDRESS = 0x11EBE
IGNITION_MAP_SIZE = 16
KNOCK_RECOVERY_STEP_ADDRESS = 0x8EAA
KNOCK_EVENT_STEP_ADDRESS = 0x8EAE
KNOCK_FORCED_STATE_ADDRESS = 0x821F

ASCD_BUTTON_ID = 0x239
RELEASED = 0x20
CANCEL = 0x02
SET_COAST = 0x08
SLOT_COUNT = 5


@dataclass(frozen=True)
class ExplicitU8Map:
    address: int
    row_axis: tuple[int, ...]
    column_axis: tuple[int, ...]
    table: tuple[tuple[int, ...], ...]


@dataclass(frozen=True)
class MapCommit:
    timestamp: float
    map_number: int


@dataclass(frozen=True)
class IgnitionCalibration:
    image_source: Path
    image_sha256: str
    load_scaler: int
    main_by_slot: tuple[ExplicitU8Map, ...]
    high_det_by_slot: tuple[ExplicitU8Map, ...]
    recovery_step_q8: int
    event_step_q8: int
    forced_state_raw: int


@dataclass(frozen=True)
class IgnitionSample:
    timestamp: float
    tick: int
    bfs_raw: int
    rpm_raw: int
    state_q8: int
    surface_state: int
    knock_count: int
    knock_channel_mask: int
    map_number: int


@dataclass(frozen=True)
class ReplayPoint:
    load_raw: int
    rpm50_raw: int
    main_raw: int
    high_det_raw: int
    map_delta_raw: int
    map_term_q8: int


@dataclass(frozen=True)
class DistributionSummary:
    comparisons: int
    minimum: int
    maximum: int
    mean: float
    median: float
    common_values: tuple[tuple[int, int], ...]


@dataclass(frozen=True)
class ExpectationSummary:
    comparisons: int
    exact: int
    mean_absolute_error: float
    maximum_absolute_error: int


@dataclass(frozen=True)
class AlignmentSummary:
    source_lag: int
    comparisons: int
    map_delta_range: tuple[int, int]
    implied_direct_base_range: tuple[int, int]
    main_vs_stock_differences: int
    high_det_vs_stock_differences: int
    main_flagged_results: int
    high_det_flagged_results: int


@dataclass(frozen=True)
class TraceIgnitionAudit:
    source: Path
    source_sha256: str
    calibration_image_source: Path
    calibration_image_sha256: str
    source_frames: int
    complete_snapshots: int
    analyzed_snapshots: int
    commits: tuple[MapCommit, ...]
    samples_by_map: tuple[tuple[int, int], ...]
    recovery_step_q8: int
    event_step_q8: int
    forced_state_raw: int
    state_q8_range: tuple[int, int]
    high_det_selected: int
    knock_event_samples: int
    knock_event_total: int
    quiet_state_steps: DistributionSummary
    event_state_steps: DistributionSummary | None
    negative_quiet_recovery: ExpectationSummary | None
    event_response: ExpectationSummary | None
    map_commit_state_steps: DistributionSummary | None
    alignments: tuple[AlignmentSummary, ...]


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as source:
        for chunk in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _signed_u8(value: int) -> int:
    return value - 0x100 if value & 0x80 else value


def _signed_u16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value & 0x8000 else value


def _load_map(image, address: int) -> ExplicitU8Map:
    return ExplicitU8Map(
        address=address,
        row_axis=tuple(
            image.values(IGNITION_RPM_AXIS_ADDRESS, IGNITION_MAP_SIZE, "uint8")
        ),
        column_axis=tuple(
            image.values(IGNITION_LOAD_AXIS_ADDRESS, IGNITION_MAP_SIZE, "uint8")
        ),
        table=tuple(
            tuple(row)
            for row in image.table(
                address,
                IGNITION_MAP_SIZE,
                IGNITION_MAP_SIZE,
                "uint8",
            )
        ),
    )


def load_calibration(
    rom: str = "JK08A",
    calibration_image: Path | None = None,
) -> IgnitionCalibration:
    if calibration_image is None:
        image = romkit.load(rom)
        image_source = Path(image.path)
        main_addresses = (IGNITION_MAIN_MAP_ADDRESS,) * SLOT_COUNT
        high_det_addresses = (IGNITION_HIGH_DET_MAP_ADDRESS,) * SLOT_COUNT
    else:
        image_source = Path(calibration_image).resolve()
        data = image_source.read_bytes()
        image = romkit.Image(image_source.name, str(image_source), data)
        families = load_layout().family_by_key
        main_addresses = families[
            "ignition_timing_trim_main"
        ].all_slot_addresses
        high_det_addresses = families[
            "ignition_timing_trim_high_det"
        ].all_slot_addresses
    if len(main_addresses) != SLOT_COUNT or len(high_det_addresses) != SLOT_COUNT:
        raise ValueError("ignition map-switching families must contain five slots")
    return IgnitionCalibration(
        image_source=image_source,
        image_sha256=hashlib.sha256(image.data).hexdigest(),
        load_scaler=image.values(
            INTERNAL_LOAD_SCALER_ADDRESS, 1, "uint16"
        )[0],
        main_by_slot=tuple(_load_map(image, address) for address in main_addresses),
        high_det_by_slot=tuple(
            _load_map(image, address) for address in high_det_addresses
        ),
        recovery_step_q8=image.values(
            KNOCK_RECOVERY_STEP_ADDRESS, 1, "uint16"
        )[0],
        event_step_q8=image.values(
            KNOCK_EVENT_STEP_ADDRESS, 1, "uint16"
        )[0],
        forced_state_raw=_signed_u8(
            image.values(KNOCK_FORCED_STATE_ADDRESS, 1, "uint8")[0]
        ),
    )


def _linear_low7(first: int, second: int, fraction: int) -> int:
    first &= 0x7F
    second &= 0x7F
    if second < first:
        return first - ((first - second) * fraction >> 16)
    return first + ((second - first) * fraction >> 16)


def interpolate_ignition_u8(
    calibration: ExplicitU8Map,
    row_key: int,
    column_key: int,
) -> int:
    """Reproduce wrapper 0x26230 and bit-field finisher 0x267CC."""
    row_index, row_fraction = explicit_axis_position(
        calibration.row_axis, row_key
    )
    column_index, column_fraction = explicit_axis_position(
        calibration.column_axis, column_key
    )
    base = calibration.table[row_index][column_index]
    first = base & 0x7F
    if column_fraction:
        first = _linear_low7(
            base,
            calibration.table[row_index][column_index + 1],
            column_fraction,
        )
    if row_fraction:
        second_base = calibration.table[row_index + 1][column_index]
        second = second_base & 0x7F
        if column_fraction:
            second = _linear_low7(
                second_base,
                calibration.table[row_index + 1][column_index + 1],
                column_fraction,
            )
        first = _linear_low7(first, second, row_fraction)
    return first | (base & 0x80)


def detect_map_commits(trace) -> tuple[MapCommit, ...]:
    """Recover complete released/SET/CANCEL/SET/released selector gestures."""
    previous = None
    phase = "idle"
    count = 0
    commits = []
    for frame in trace.frames:
        if (
            frame.extended
            or frame.remote
            or frame.can_id != ASCD_BUTTON_ID
            or len(frame.data) < 4
        ):
            continue
        current = frame.data[3]
        if current == previous:
            continue
        timestamp = frame.offset_ms / 1000.0
        if previous is None:
            previous = current
            continue
        if phase == "idle":
            if previous == RELEASED and current == SET_COAST:
                phase = "set"
                count = 0
        elif phase == "set":
            if current == CANCEL:
                phase = "cancel"
            elif current == RELEASED:
                if 1 <= count <= SLOT_COUNT:
                    commits.append(MapCommit(timestamp, count))
                phase = "idle"
                count = 0
            elif current != SET_COAST:
                phase = "idle"
                count = 0
        else:
            if current == SET_COAST:
                count += 1
                phase = "set"
            elif current != CANCEL:
                phase = "idle"
                count = 0
        previous = current
    return tuple(commits)


def _map_number_at(
    timestamp: float,
    commit_times: tuple[float, ...],
    commits: tuple[MapCommit, ...],
) -> int:
    index = bisect_right(commit_times, timestamp) - 1
    return 1 if index < 0 else commits[index].map_number


def _samples(trace, commits, profile: str, can_id: int, tick_divisor: int):
    model = DashboardModel(profile, can_id, tick_divisor)
    commit_times = tuple(commit.timestamp for commit in commits)
    samples = []
    required = (
        "bfs_raw",
        "rpm_raw",
        "knock_timing_state_raw",
        "knock_surface_state",
        "knock_count_latched",
        "knock_channel_mask_latched",
    )
    for frame in trace.frames:
        timestamp = frame.offset_ms / 1000.0
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
        if snapshot is None or not model.schema_verified:
            continue
        if not all(name in model.raw for name in required):
            continue
        samples.append(
            IgnitionSample(
                timestamp=timestamp,
                tick=snapshot.unwrapped_tick,
                bfs_raw=model.raw["bfs_raw"],
                rpm_raw=model.raw["rpm_raw"],
                state_q8=model.raw["knock_timing_state_raw"],
                surface_state=model.raw["knock_surface_state"],
                knock_count=model.raw["knock_count_latched"],
                knock_channel_mask=model.raw["knock_channel_mask_latched"],
                map_number=_map_number_at(
                    timestamp, commit_times, commits
                ),
            )
        )
    return model, samples


def replay_point(
    calibration: IgnitionCalibration,
    source: IgnitionSample,
    map_number: int,
) -> ReplayPoint:
    if not 1 <= map_number <= SLOT_COUNT:
        raise ValueError("map number must be in 1..5")
    load_raw = internal_load_raw(source.bfs_raw, calibration.load_scaler)
    rpm50_raw = min(0xFF, source.rpm_raw >> 2)
    main_raw = interpolate_ignition_u8(
        calibration.main_by_slot[map_number - 1], rpm50_raw, load_raw
    )
    high_det_raw = interpolate_ignition_u8(
        calibration.high_det_by_slot[map_number - 1], rpm50_raw, load_raw
    )
    delta = (main_raw & 0x7F) - (high_det_raw & 0x7F)
    return ReplayPoint(
        load_raw=load_raw,
        rpm50_raw=rpm50_raw,
        main_raw=main_raw,
        high_det_raw=high_det_raw,
        map_delta_raw=delta,
        map_term_q8=delta << 8,
    )


def _distribution(values: list[int]) -> DistributionSummary | None:
    if not values:
        return None
    return DistributionSummary(
        comparisons=len(values),
        minimum=min(values),
        maximum=max(values),
        mean=statistics.fmean(values),
        median=statistics.median(values),
        common_values=tuple(Counter(values).most_common(5)),
    )


def _expectation(errors: list[int]) -> ExpectationSummary | None:
    if not errors:
        return None
    absolute = [abs(error) for error in errors]
    return ExpectationSummary(
        comparisons=len(errors),
        exact=sum(error == 0 for error in errors),
        mean_absolute_error=statistics.fmean(absolute),
        maximum_absolute_error=max(absolute),
    )


def _state_dynamics(
    samples: list[IgnitionSample],
    recovery_step_q8: int,
    event_step_q8: int,
    tick_divisor: int,
):
    quiet_steps = []
    event_steps = []
    recovery_errors = []
    event_errors = []
    commit_steps = []
    for previous, current in zip(samples, samples[1:]):
        if current.tick - previous.tick != tick_divisor:
            continue
        delta = current.state_q8 - previous.state_q8
        if current.knock_count == 0:
            quiet_steps.append(delta)
            if previous.state_q8 < 0:
                expected = min(recovery_step_q8, -previous.state_q8)
                recovery_errors.append(delta - expected)
        else:
            event_steps.append(delta)
            event_errors.append(delta + event_step_q8 * current.knock_count)
        if current.map_number != previous.map_number:
            commit_steps.append(delta)
    return (
        _distribution(quiet_steps),
        _distribution(event_steps),
        _expectation(recovery_errors),
        _expectation(event_errors),
        _distribution(commit_steps),
    )


def _alignment_summary(
    samples: list[IgnitionSample],
    calibration: IgnitionCalibration,
    source_lag: int,
    tick_divisor: int,
) -> AlignmentSummary:
    rows = []
    for target_index in range(source_lag, len(samples)):
        source_index = target_index - source_lag
        source = samples[source_index]
        target = samples[target_index]
        if target.tick - source.tick != source_lag * tick_divisor:
            continue
        point = replay_point(calibration, source, target.map_number)
        base = _signed_u16(target.state_q8 - point.map_term_q8)
        rows.append((target_index, target, point, base))
    if not rows:
        raise ValueError(f"no contiguous samples for source lag {source_lag}")

    points = [row[2] for row in rows]
    bases = [row[3] for row in rows]
    stock_points = [
        replay_point(calibration, samples[index - source_lag], 1)
        for index, _, _, _ in rows
    ]
    return AlignmentSummary(
        source_lag=source_lag,
        comparisons=len(rows),
        map_delta_range=(
            min(point.map_delta_raw for point in points),
            max(point.map_delta_raw for point in points),
        ),
        implied_direct_base_range=(min(bases), max(bases)),
        main_vs_stock_differences=sum(
            (point.main_raw & 0x7F) != (stock.main_raw & 0x7F)
            for point, stock in zip(points, stock_points)
        ),
        high_det_vs_stock_differences=sum(
            (point.high_det_raw & 0x7F) != (stock.high_det_raw & 0x7F)
            for point, stock in zip(points, stock_points)
        ),
        main_flagged_results=sum(bool(point.main_raw & 0x80) for point in points),
        high_det_flagged_results=sum(
            bool(point.high_det_raw & 0x80) for point in points
        ),
    )


def audit_trace(
    source: Path,
    *,
    rom: str = "JK08A",
    calibration_image: Path | None = None,
    profile: str = "wide54",
    can_id: int = 0x6F0,
    tick_divisor: int = 1,
    source_lags: tuple[int, ...] = (0, 1, 2),
) -> TraceIgnitionAudit:
    source = Path(source)
    source_sha256 = _sha256_file(source)
    trace = peak_trc_audit.load_trace(source)
    if _sha256_file(source) != source_sha256:
        raise ValueError(f"{source}: capture changed while it was being parsed")
    commits = detect_map_commits(trace)
    calibration = load_calibration(rom, calibration_image)
    model, samples = _samples(trace, commits, profile, can_id, tick_divisor)
    if len(samples) < 3:
        raise ValueError(f"{source}: fewer than three verified ignition snapshots")
    if not source_lags or any(type(lag) is not int or lag < 0 for lag in source_lags):
        raise ValueError("source lags must be nonnegative integers")
    dynamics = _state_dynamics(
        samples,
        calibration.recovery_step_q8,
        calibration.event_step_q8,
        tick_divisor,
    )
    return TraceIgnitionAudit(
        source=source,
        source_sha256=source_sha256,
        calibration_image_source=calibration.image_source,
        calibration_image_sha256=calibration.image_sha256,
        source_frames=len(trace.frames),
        complete_snapshots=model.decoder.completed_groups,
        analyzed_snapshots=len(samples),
        commits=commits,
        samples_by_map=tuple(
            sorted(Counter(sample.map_number for sample in samples).items())
        ),
        recovery_step_q8=calibration.recovery_step_q8,
        event_step_q8=calibration.event_step_q8,
        forced_state_raw=calibration.forced_state_raw,
        state_q8_range=(
            min(sample.state_q8 for sample in samples),
            max(sample.state_q8 for sample in samples),
        ),
        high_det_selected=sum(
            bool(sample.surface_state & 0x40) for sample in samples
        ),
        knock_event_samples=sum(sample.knock_count != 0 for sample in samples),
        knock_event_total=sum(sample.knock_count for sample in samples),
        quiet_state_steps=dynamics[0],
        event_state_steps=dynamics[1],
        negative_quiet_recovery=dynamics[2],
        event_response=dynamics[3],
        map_commit_state_steps=dynamics[4],
        alignments=tuple(
            _alignment_summary(
                samples, calibration, lag, tick_divisor
            )
            for lag in source_lags
        ),
    )


def _format_distribution(
    label: str, summary: DistributionSummary | None
) -> str:
    if summary is None:
        return f"    {label}: n=0"
    common = ",".join(
        f"{value:+d}:{count}" for value, count in summary.common_values
    )
    return (
        f"    {label}: n={summary.comparisons}, range={summary.minimum}.."
        f"{summary.maximum}, mean={summary.mean:.6f}, "
        f"median={summary.median:g}, common={common}"
    )


def _format_expectation(
    label: str, summary: ExpectationSummary | None
) -> str:
    if summary is None:
        return f"    {label}: n=0"
    exact = 100 * summary.exact / summary.comparisons
    return (
        f"    {label}: exact={summary.exact}/{summary.comparisons} "
        f"({exact:.3f}%), MAE={summary.mean_absolute_error:.6f}, "
        f"max_abs={summary.maximum_absolute_error}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "--calibration-image",
        type=Path,
        help="exact full ROM image whose active ignition slots should be replayed",
    )
    parser.add_argument(
        "--can-id", type=lambda value: int(value, 0), default=0x6F0
    )
    parser.add_argument("--tick-divisor", type=int, default=1)
    parser.add_argument(
        "--source-lags",
        type=lambda value: tuple(int(item, 0) for item in value.split(",")),
        default=(0, 1, 2),
        help="comma-separated snapshot lags used as RPM/BFS map inputs",
    )
    args = parser.parse_args(argv)
    if not 1 <= args.can_id <= 0x7FF:
        parser.error("CAN ID must be in 0x001..0x7FF")
    if not 1 <= args.tick_divisor <= 0xFF:
        parser.error("tick divisor must be in 1..255")

    try:
        for source in args.inputs:
            result = audit_trace(
                source,
                calibration_image=args.calibration_image,
                can_id=args.can_id,
                tick_divisor=args.tick_divisor,
                source_lags=args.source_lags,
            )
            print(f"{result.source}:")
            print(f"  capture_sha256={result.source_sha256}")
            print(f"  image={result.calibration_image_source}")
            print(f"  image_sha256={result.calibration_image_sha256}")
            print(
                f"  frames={result.source_frames}, complete={result.complete_snapshots}, "
                f"analyzed={result.analyzed_snapshots}"
            )
            commits = ",".join(
                f"{commit.timestamp:.4f}s:Map{commit.map_number}"
                for commit in result.commits
            ) or "none"
            print(f"  commits={commits}")
            print(
                "  samples_by_map="
                + ",".join(
                    f"Map{number}:{count}"
                    for number, count in result.samples_by_map
                )
            )
            print(
                f"  recovery_step_q8={result.recovery_step_q8}, "
                f"event_step_q8={result.event_step_q8}, "
                f"forced_state_raw={result.forced_state_raw}"
            )
            print(
                f"  state_q8={result.state_q8_range[0]}..{result.state_q8_range[1]}, "
                f"high_det_selected={result.high_det_selected}/{result.analyzed_snapshots}, "
                f"event_samples={result.knock_event_samples}, "
                f"event_total={result.knock_event_total}"
            )
            print(_format_distribution("quiet_state_step", result.quiet_state_steps))
            print(_format_distribution("event_state_step", result.event_state_steps))
            print(
                _format_expectation(
                    "negative_quiet_recovery", result.negative_quiet_recovery
                )
            )
            print(_format_expectation("event_response", result.event_response))
            print(
                _format_distribution(
                    "map_commit_state_step", result.map_commit_state_steps
                )
            )
            for alignment in result.alignments:
                print(
                    f"  source_lag={alignment.source_lag}: "
                    f"n={alignment.comparisons}, "
                    f"map_delta={alignment.map_delta_range[0]}.."
                    f"{alignment.map_delta_range[1]}, "
                    f"implied_direct_base_q8={alignment.implied_direct_base_range[0]}.."
                    f"{alignment.implied_direct_base_range[1]}, "
                    f"main_vs_stock={alignment.main_vs_stock_differences}, "
                    f"high_det_vs_stock={alignment.high_det_vs_stock_differences}, "
                    f"main_flagged={alignment.main_flagged_results}, "
                    f"high_det_flagged={alignment.high_det_flagged_results}"
                )
    except (OSError, ValueError, peak_trc_audit.TraceError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
