#!/usr/bin/env python3
"""Convert PEAK PCAN-View TRC 1.1 JK08A telemetry to MLVLG v2."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime, timedelta
import math
import os
from pathlib import Path
import sys
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard.model import DashboardModel, FrameRecord
from tools.can_dashboard.recording import TelemetryMlgRecorder
from tools.logs import peak_trc_audit


OLE_AUTOMATION_EPOCH = datetime(1899, 12, 30)


class ConversionError(ValueError):
    """Raised when a TRC capture cannot be converted without ambiguity."""


@dataclass(frozen=True)
class ConversionSummary:
    source: Path
    output: Path
    source_frames: int
    telemetry_frames: int
    complete_snapshots: int
    mlg_fields: int
    mlg_records: int
    bridge_records: int
    first_snapshot_offset_ms: float
    output_size: int


def trace_start_epoch(trace, timezone_name: str) -> float:
    if trace.start_time is None:
        raise ConversionError(
            f"{trace.path}: TRC does not declare $STARTTIME"
        )
    try:
        ole_days = float(trace.start_time)
    except ValueError as error:
        raise ConversionError(
            f"{trace.path}: invalid $STARTTIME value {trace.start_time!r}"
        ) from error
    if not math.isfinite(ole_days):
        raise ConversionError(
            f"{trace.path}: invalid $STARTTIME value {trace.start_time!r}"
        )
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as error:
        raise ConversionError(f"unknown timezone: {timezone_name}") from error
    try:
        local_start = OLE_AUTOMATION_EPOCH + timedelta(days=ole_days)
        candidates = set()
        for fold in (0, 1):
            aware = local_start.replace(tzinfo=zone, fold=fold)
            candidate = aware.timestamp()
            round_trip = datetime.fromtimestamp(candidate, zone).replace(
                tzinfo=None
            )
            if round_trip == local_start:
                candidates.add(candidate)
    except (OverflowError, OSError, ValueError) as error:
        raise ConversionError(
            f"{trace.path}: $STARTTIME is outside the supported range"
        ) from error
    if len(candidates) != 1:
        raise ConversionError(
            f"{trace.path}: $STARTTIME is ambiguous or nonexistent in "
            f"timezone {timezone_name}"
        )
    timestamp = candidates.pop()
    if not math.isfinite(timestamp) or not 0 <= timestamp <= 0xFFFFFFFF:
        raise ConversionError(
            f"{trace.path}: $STARTTIME is outside the MLVLG timestamp range"
        )
    return timestamp


def _same_file(left: Path, right: Path) -> bool:
    try:
        if left.exists() and right.exists() and os.path.samefile(left, right):
            return True
    except OSError:
        pass
    return left.resolve() == right.resolve()


def convert_trace(
    source: Path,
    output: Path,
    *,
    profile: str = "tuning",
    can_id: int = 0x6F0,
    tick_divisor: int = 1,
    timezone_name: str = "Asia/Vladivostok",
    force: bool = False,
) -> ConversionSummary:
    source = Path(source)
    output = Path(output)
    if _same_file(source, output):
        raise ConversionError(f"{output}: output would overwrite the source trace")
    if output.exists() and not force:
        raise ConversionError(
            f"{output}: output already exists; use --force to replace it"
        )
    try:
        trace = peak_trc_audit.load_trace(source)
    except peak_trc_audit.TraceError as error:
        raise ConversionError(str(error)) from error
    start_epoch = trace_start_epoch(trace, timezone_name)
    model = DashboardModel(profile, can_id, tick_divisor)
    recorder = None
    first_snapshot_seconds = None
    telemetry_frames = 0

    try:
        for frame in trace.frames:
            timestamp = frame.offset_ms / 1000.0
            if frame.can_id == can_id and not frame.extended:
                telemetry_frames += 1
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
            if snapshot is None:
                continue
            if recorder is None:
                first_snapshot_seconds = timestamp
                recorder = TelemetryMlgRecorder(
                    output,
                    profile,
                    start_epoch + first_snapshot_seconds,
                    force=force,
                )
            recorder.append(model, timestamp - first_snapshot_seconds)

        if recorder is None or first_snapshot_seconds is None:
            raise ConversionError(
                f"{source}: no complete telemetry snapshots for CAN ID "
                f"0x{can_id:03X}"
            )
        recording = recorder.close()
        recorder = None
    except Exception:
        if recorder is not None:
            recorder.abort()
        raise

    return ConversionSummary(
        source=source,
        output=output,
        source_frames=len(trace.frames),
        telemetry_frames=telemetry_frames,
        complete_snapshots=model.decoder.completed_groups,
        mlg_fields=recording.fields,
        mlg_records=recording.event_records,
        bridge_records=recording.bridge_records,
        first_snapshot_offset_ms=first_snapshot_seconds * 1000,
        output_size=recording.output_size,
    )


def _output_path(
    source: Path,
    explicit_output: Path | None,
    output_directory: Path | None,
) -> Path:
    if explicit_output is not None:
        return explicit_output
    if output_directory is not None:
        return output_directory / source.with_suffix(".mlg").name
    return source.with_suffix(".mlg")


def _format_size(size: int) -> str:
    value = float(size)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if value < 1024 or unit == "GiB":
            return f"{value:.1f} {unit}"
        value /= 1024
    raise AssertionError("unreachable")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="output path; valid only with one input",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="write every MLVLG file to this directory",
    )
    parser.add_argument(
        "--profile", choices=("tuning",), default="tuning"
    )
    parser.add_argument(
        "--can-id", type=lambda value: int(value, 0), default=0x6F0
    )
    parser.add_argument("--tick-divisor", type=int, default=1)
    parser.add_argument(
        "--timezone",
        default="Asia/Vladivostok",
        help="IANA timezone used to interpret PEAK local $STARTTIME",
    )
    parser.add_argument(
        "--force", action="store_true", help="replace existing output files"
    )
    args = parser.parse_args(argv)

    if args.output is not None and len(args.inputs) != 1:
        parser.error("--output requires exactly one input")
    if args.output is not None and args.output_dir is not None:
        parser.error("--output and --output-dir are mutually exclusive")
    if not 1 <= args.can_id <= 0x7FF:
        parser.error("CAN ID must be in 0x001..0x7FF")
    if not 1 <= args.tick_divisor <= 0xFF:
        parser.error("tick divisor must be in 1..255")

    try:
        for source in args.inputs:
            output = _output_path(source, args.output, args.output_dir)
            summary = convert_trace(
                source,
                output,
                profile=args.profile,
                can_id=args.can_id,
                tick_divisor=args.tick_divisor,
                timezone_name=args.timezone,
                force=args.force,
            )
            print(
                f"{summary.source} -> {summary.output}: "
                f"{summary.source_frames} source frames, "
                f"{summary.telemetry_frames} telemetry frames, "
                f"{summary.mlg_records} snapshots, "
                f"{summary.mlg_fields} fields, "
                f"{summary.bridge_records} bridge records, "
                f"{_format_size(summary.output_size)}"
            )
    except (ConversionError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
