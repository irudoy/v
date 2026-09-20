#!/usr/bin/env python3
"""Audit the exact JK08A internal-load and diagnostic-load formulas in a TRC."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import statistics
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard.model import DashboardModel, FrameRecord
from tools.logs import peak_trc_audit
from tools.mapkit import rom as romkit


INTERNAL_LOAD_SCALER_ADDRESS = 0x9534
CALCULATED_LOAD_REFERENCE_ADDRESS = 0x1491A
CALCULATED_LOAD_REFERENCE_POINTS = 16
IMPLICIT_REFERENCE_STEP = 0x1000


@dataclass(frozen=True)
class LoadCalibration:
    scaler: int
    calculated_load_reference: tuple[int, ...]


@dataclass(frozen=True)
class LoadSample:
    timestamp: float
    run: int
    tick: int
    bfs_raw: int
    rpm_raw: int
    calculated_load_raw: int


@dataclass(frozen=True)
class ErrorSummary:
    comparisons: int
    exact: int
    within_one: int
    mean_absolute: float
    median_absolute: float
    maximum_absolute: int


@dataclass(frozen=True)
class TraceLoadAudit:
    source: Path
    source_frames: int
    complete_snapshots: int
    analyzed_snapshots: int
    scaler: int
    internal_raw_range: tuple[int, int]
    internal_percent_range: tuple[float, float]
    diagnostic_raw_range: tuple[int, int]
    same_snapshot: ErrorSummary
    prior_snapshot: ErrorSummary


def load_calibration(rom: str = "JK08A") -> LoadCalibration:
    image = romkit.load(rom)
    scaler = image.values(INTERNAL_LOAD_SCALER_ADDRESS, 1, "uint16")[0]
    reference = tuple(
        image.values(
            CALCULATED_LOAD_REFERENCE_ADDRESS,
            CALCULATED_LOAD_REFERENCE_POINTS,
            "uint16",
        )
    )
    return LoadCalibration(scaler, reference)


def _require_u16(value: int, name: str) -> None:
    if type(value) is not int or not 0 <= value <= 0xFFFF:
        raise ValueError(f"{name} must be an unsigned 16-bit integer")


def interpolate_implicit_u16(
    values: tuple[int, ...], coordinate: int, step: int
) -> int:
    """Reproduce the unsigned implicit-axis lookup and Q0.16 finisher."""
    if len(values) < 2:
        raise ValueError("at least two interpolation points are required")
    if type(coordinate) is not int or coordinate < 0:
        raise ValueError("coordinate must be a nonnegative integer")
    if type(step) is not int or step <= 0:
        raise ValueError("step must be a positive integer")
    if any(type(value) is not int or not 0 <= value <= 0xFFFF for value in values):
        raise ValueError("interpolation values must be unsigned 16-bit integers")

    last_coordinate = step * (len(values) - 1)
    if coordinate >= last_coordinate:
        return values[-1]
    index, remainder = divmod(coordinate, step)
    fraction = (remainder << 16) // step
    first = values[index]
    second = values[index + 1]
    if second < first:
        return first - ((first - second) * fraction >> 16)
    return first + ((second - first) * fraction >> 16)


def internal_load_raw(bfs_raw: int, scaler: int) -> int:
    """Return the byte written to ffff1048 before the scheduler snapshot."""
    _require_u16(bfs_raw, "bfs_raw")
    _require_u16(scaler, "scaler")
    if scaler == 0:
        return 0
    return min(0xFF, (bfs_raw << 7) // scaler)


def calculated_load_raw(
    bfs_raw: int,
    rpm_raw: int,
    reference: tuple[int, ...],
) -> int:
    """Return the stock normal-path J1979 Mode 01 PID 0x04 byte."""
    _require_u16(bfs_raw, "bfs_raw")
    _require_u16(rpm_raw, "rpm_raw")
    rpm_over_25 = min(0xFF, rpm_raw >> 1)
    divisor = interpolate_implicit_u16(
        reference,
        rpm_over_25 << 8,
        IMPLICIT_REFERENCE_STEP,
    )
    quotient = 0 if divisor == 0 else (bfs_raw << 8) // divisor
    return min(0xFF, quotient)


def _error_summary(errors: list[int]) -> ErrorSummary:
    if not errors:
        raise ValueError("at least one comparison is required")
    absolute = [abs(error) for error in errors]
    return ErrorSummary(
        comparisons=len(errors),
        exact=sum(error == 0 for error in errors),
        within_one=sum(error <= 1 for error in absolute),
        mean_absolute=statistics.fmean(absolute),
        median_absolute=statistics.median(absolute),
        maximum_absolute=max(absolute),
    )


def _samples(trace, profile: str, can_id: int, tick_divisor: int):
    model = DashboardModel(profile, can_id, tick_divisor)
    samples = []
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
        required = ("bfs_raw", "rpm_raw", "calculated_load_raw")
        if not all(name in model.raw for name in required):
            continue
        samples.append(
            LoadSample(
                timestamp=timestamp,
                run=snapshot.run,
                tick=snapshot.unwrapped_tick,
                bfs_raw=model.raw["bfs_raw"],
                rpm_raw=model.raw["rpm_raw"],
                calculated_load_raw=model.raw["calculated_load_raw"],
            )
        )
    return model, samples


def audit_trace(
    source: Path,
    *,
    rom: str = "JK08A",
    profile: str = "tuning",
    can_id: int = 0x6F0,
    tick_divisor: int = 1,
) -> TraceLoadAudit:
    source = Path(source)
    trace = peak_trc_audit.load_trace(source)
    calibration = load_calibration(rom)
    model, samples = _samples(trace, profile, can_id, tick_divisor)
    if len(samples) < 2:
        raise ValueError(f"{source}: fewer than two verified load snapshots")

    internal = [
        internal_load_raw(sample.bfs_raw, calibration.scaler)
        for sample in samples
    ]
    same_errors = [
        calculated_load_raw(
            sample.bfs_raw,
            sample.rpm_raw,
            calibration.calculated_load_reference,
        )
        - sample.calculated_load_raw
        for sample in samples
    ]
    prior_errors = []
    for previous, current in zip(samples, samples[1:]):
        if (
            current.run != previous.run
            or current.tick - previous.tick != tick_divisor
        ):
            continue
        prediction = calculated_load_raw(
            previous.bfs_raw,
            previous.rpm_raw,
            calibration.calculated_load_reference,
        )
        prior_errors.append(prediction - current.calculated_load_raw)

    return TraceLoadAudit(
        source=source,
        source_frames=len(trace.frames),
        complete_snapshots=model.decoder.completed_groups,
        analyzed_snapshots=len(samples),
        scaler=calibration.scaler,
        internal_raw_range=(min(internal), max(internal)),
        internal_percent_range=(
            min(internal) * 100 / 128,
            max(internal) * 100 / 128,
        ),
        diagnostic_raw_range=(
            min(sample.calculated_load_raw for sample in samples),
            max(sample.calculated_load_raw for sample in samples),
        ),
        same_snapshot=_error_summary(same_errors),
        prior_snapshot=_error_summary(prior_errors),
    )


def _format_errors(label: str, summary: ErrorSummary) -> str:
    exact = 100 * summary.exact / summary.comparisons
    within_one = 100 * summary.within_one / summary.comparisons
    return (
        f"  {label}: n={summary.comparisons}, exact={summary.exact} "
        f"({exact:.3f}%), within_one={summary.within_one} "
        f"({within_one:.3f}%), MAE={summary.mean_absolute:.6f}, "
        f"median_abs={summary.median_absolute:g}, "
        f"max_abs={summary.maximum_absolute}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "--can-id", type=lambda value: int(value, 0), default=0x6F0
    )
    parser.add_argument("--tick-divisor", type=int, default=1)
    args = parser.parse_args(argv)
    if not 1 <= args.can_id <= 0x7FF:
        parser.error("CAN ID must be in 0x001..0x7FF")
    if not 1 <= args.tick_divisor <= 0xFF:
        parser.error("tick divisor must be in 1..255")

    try:
        for source in args.inputs:
            result = audit_trace(
                source,
                rom="JK08A",
                profile="tuning",
                can_id=args.can_id,
                tick_divisor=args.tick_divisor,
            )
            print(result.source)
            print(
                f"  frames={result.source_frames}, "
                f"complete={result.complete_snapshots}, "
                f"analyzed={result.analyzed_snapshots}"
            )
            print(f"  internal_load_scaler=0x{result.scaler:04X}")
            print(
                "  internal_load="
                f"raw {result.internal_raw_range[0]}..{result.internal_raw_range[1]}, "
                f"normalized {result.internal_percent_range[0]:.5f}.."
                f"{result.internal_percent_range[1]:.5f}%"
            )
            print(
                "  diagnostic_load="
                f"raw {result.diagnostic_raw_range[0]}.."
                f"{result.diagnostic_raw_range[1]}"
            )
            print(_format_errors("same_snapshot", result.same_snapshot))
            print(_format_errors("prior_snapshot", result.prior_snapshot))
    except (OSError, ValueError, peak_trc_audit.TraceError) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
