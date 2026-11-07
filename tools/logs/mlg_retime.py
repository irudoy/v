#!/usr/bin/env python3
"""Rebuild MLVLG record times from the telemetry tick channel.

The producer emits one telemetry group per tick at a fixed period, so the tick
channel is the sample index of a running stream. A host clock that timestamps
a frame when the application dequeues it collapses a drained burst onto a
single 10 us block timestamp; the tick index restores the true spacing. STOP
holds the tick, so a stream pause keeps its recorded duration. The result is
written to a new file: block timestamps and the `Date` and `Elapsed` channels
follow the tick index and the pauses, and every other recorded value is copied
unchanged.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import itertools
import math
import os
from pathlib import Path
import struct
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard.model import BASE_TICK_SECONDS
from tools.logs import can_telemetry
from tools.logs import mlvlg

TICK_CHANNEL = "Telemetry tick"
ELAPSED_CHANNEL = "Elapsed"
DATE_CHANNEL = "Date"
TICK_MODULUS = 0x10000
OUTPUT_SUFFIX = "-retimed"
PERIOD_ITERATIONS = 8


@dataclass(frozen=True)
class RetimeSummary:
    source: Path
    output: Path
    records: int
    period_seconds: float
    span_seconds: float
    pauses: int
    pause_seconds: float
    collapsed_before: int
    collapsed_after: int
    written: bool


@dataclass(frozen=True)
class _Channel:
    format: str
    offset: int
    size: int


def _channels(specs) -> dict[str, _Channel]:
    channels = {}
    offset = 0
    for spec in specs:
        fmt = mlvlg.FIELD_STRUCTS[spec.field_type]
        size = struct.calcsize(fmt)
        channels[spec.name.strip()] = _Channel(fmt, offset, size)
        offset += size
    return channels


def _read(data: bytes, base: int, channel: _Channel):
    start = base + channel.offset
    return struct.unpack(channel.format, data[start : start + channel.size])[0]


def unwrap_ticks(values, times=None) -> list[int]:
    """Return the tick sequence unwrapped over its 16-bit modulus.

    ``times`` holds the recorded seconds of the values. With them a tick
    step that the recorded time cannot explain marks a producer restart as
    well as a step back into the opening window (can_telemetry.tick_step).
    """

    unwrapped = []
    offset = 0
    previous = previous_time = None
    times = None if times is None else iter(times)
    for value in values:
        time = None if times is None else next(times)
        tick = int(value)
        if not 0 <= tick < TICK_MODULUS:
            raise mlvlg.MlvlgError(f"telemetry tick is out of range: {value!r}")
        if previous is not None and tick != previous:
            step = can_telemetry.tick_step(
                previous, tick, can_telemetry.receive_gap(previous_time, time)
            )
            if step is can_telemetry.TickStep.RESTART:
                raise mlvlg.MlvlgError(
                    "the telemetry tick restarts at "
                    f"{tick} after {previous}, so the recording spans more "
                    "than one producer run and the tick cannot order it"
                )
            if tick < previous:
                offset += TICK_MODULUS
        unwrapped.append(offset + tick)
        if tick != previous:
            # A bridge record repeats the tick; the step of the next tick
            # counts from the record that carried it first.
            previous, previous_time = tick, time
    return unwrapped


def measure_period(ticks, recorded) -> float:
    """Return the tick period over the running snapshots of a recording.

    The pause floors depend on the period, so the measurement starts from the
    nominal tick and repeats with the measured period until it settles.
    """

    period = BASE_TICK_SECONDS
    for _ in range(PERIOD_ITERATIONS):
        pauses = can_telemetry.stream_pauses(ticks, recorded, period)
        measured = (recorded[-1] - recorded[0] - sum(pauses)) / (
            ticks[-1] - ticks[0]
        )
        settled = measured == period
        period = measured
        if settled:
            break
    return period


def retime(
    path: Path,
    output: Path,
    *,
    period_seconds: float | None = None,
    dry_run: bool = False,
) -> RetimeSummary:
    path = Path(path)
    output = Path(output)
    if output == path:
        raise ValueError("retimed output must be a new file")
    mlvlg.validate_mlg(path)

    data = bytearray(path.read_bytes())
    (
        _format,
        _version,
        start_epoch,
        _info_start,
        data_begin,
        record_length,
        field_count,
    ) = struct.unpack(">6sHIIIHH", bytes(data[: mlvlg.MLG_HEADER_SIZE]))
    specs = mlvlg.read_fields(path)
    if len(specs) != field_count:
        raise mlvlg.MlvlgError(f"{path}: field count does not match the header")
    channels = _channels(specs)
    for name in (TICK_CHANNEL, ELAPSED_CHANNEL, DATE_CHANNEL):
        if name not in channels:
            raise mlvlg.MlvlgError(f"{path}: no {name!r} channel to retime from")

    block = record_length + 5
    starts = []
    offset = data_begin
    while offset + block <= len(data):
        if data[offset] != 0x00:
            raise mlvlg.MlvlgError(
                f"{path}: only field-data blocks can be retimed"
            )
        starts.append(offset + 4)
        offset += block
    if len(starts) < 2:
        raise mlvlg.MlvlgError(f"{path}: too few records to retime")

    tick = channels[TICK_CHANNEL]
    elapsed = channels[ELAPSED_CHANNEL]
    date = channels[DATE_CHANNEL]
    recorded = [_read(data, base, elapsed) for base in starts]
    ticks = unwrap_ticks((_read(data, base, tick) for base in starts), recorded)
    repeats = sum(
        1 for before, after in zip(ticks, ticks[1:]) if after <= before
    )
    if repeats:
        raise mlvlg.MlvlgError(
            f"{path}: {repeats} records repeat a telemetry tick, so the tick "
            "index cannot order them"
        )
    collapsed_before = sum(
        1 for before, after in zip(recorded, recorded[1:]) if after == before
    )

    if period_seconds is None:
        period_seconds = measure_period(ticks, recorded)
    if not math.isfinite(period_seconds) or period_seconds <= 0:
        raise mlvlg.MlvlgError(f"tick period must be positive: {period_seconds!r}")
    pauses = can_telemetry.stream_pauses(ticks, recorded, period_seconds)

    times = [
        recorded[0] + (value - ticks[0]) * period_seconds + offset
        for value, offset in zip(ticks, itertools.accumulate(pauses))
    ]
    collapsed_after = sum(
        1
        for before, after in zip(times, times[1:])
        if round(after * mlvlg.TIMESTAMP_TICKS_PER_SECOND)
        == round(before * mlvlg.TIMESTAMP_TICKS_PER_SECOND)
    )

    if not dry_run:
        for base, value in zip(starts, times):
            struct.pack_into(
                elapsed.format, data, base + elapsed.offset, value
            )
            struct.pack_into(
                date.format,
                data,
                base + date.offset,
                math.floor(start_epoch + value + 1e-9),
            )
            payload = bytes(data[base : base + record_length])
            struct.pack_into(
                ">H",
                data,
                base - 2,
                round(value * mlvlg.TIMESTAMP_TICKS_PER_SECOND) & 0xFFFF,
            )
            data[base + record_length] = sum(payload) & 0xFF
        _write(output, bytes(data))

    return RetimeSummary(
        source=path,
        output=output,
        records=len(starts),
        period_seconds=period_seconds,
        span_seconds=times[-1] - times[0],
        pauses=sum(1 for pause in pauses if pause),
        pause_seconds=sum(pauses),
        collapsed_before=collapsed_before,
        collapsed_after=collapsed_after,
        written=not dry_run,
    )


def _write(output: Path, payload: bytes) -> None:
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.", suffix=".tmp", dir=output.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        mlvlg.validate_mlg(temporary)
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise


def default_output(path: Path) -> Path:
    return path.with_name(f"{path.stem}{OUTPUT_SUFFIX}{path.suffix}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="MLVLG files")
    parser.add_argument(
        "--output",
        type=Path,
        help="destination for a single input log",
    )
    parser.add_argument(
        "--period-ms",
        type=float,
        help="telemetry tick period; measured over running snapshots when omitted",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="report the reconstruction without writing",
    )
    args = parser.parse_args(argv)
    if args.output is not None and len(args.logs) != 1:
        parser.error("--output accepts a single input log")

    period = None if args.period_ms is None else args.period_ms / 1000.0
    try:
        for source in args.logs:
            summary = retime(
                source,
                args.output or default_output(source),
                period_seconds=period,
                dry_run=args.dry_run,
            )
            state = "would write" if args.dry_run else "wrote"
            print(
                f"{summary.source}: {state} {summary.output.name}, "
                f"{summary.records} records, "
                f"period {summary.period_seconds * 1000:.4f} ms, "
                f"span {summary.span_seconds:.3f} s, "
                f"{summary.pauses} stream pauses of "
                f"{summary.pause_seconds:.3f} s"
            )
            print(
                f"  records sharing a block timestamp: "
                f"{summary.collapsed_before} -> {summary.collapsed_after}"
            )
    except (mlvlg.MlvlgError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
