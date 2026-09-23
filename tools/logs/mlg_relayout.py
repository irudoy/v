#!/usr/bin/env python3
"""Carry a dashboard MLVLG recording into the channel layout of the current profile.

The output declares the channels the dashboard recorder writes for the
current profile, in the recorder's order and with its descriptors. A recorded
channel whose name, without the candidate marker, names a current channel
keeps every recorded value. A current channel the recording lacks reads NaN in
every record, as the recorder writes a field it has not received, and a
recorded channel the current profile does not bind is left out. Blocks keep
their order, counters, and timestamps, and markers keep their text, so the
time base, the bridge records, and the markers of the recording stay
unchanged; the header keeps the start time. The result is written to a new
file.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import math
import os
from pathlib import Path
import struct
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.can_dashboard import recording
from tools.logs import mlvlg

DEFAULT_PROFILE = "tuning"
# A dashboard recording carries its wall-clock second, its time base, and the
# producer tick that orders its snapshots.
REQUIRED_SOURCES = ("date", "elapsed", "tick16")


@dataclass(frozen=True)
class RelayoutSummary:
    source: Path
    output: Path
    fields: int
    data_records: int
    marker_records: int
    missing: tuple[str, ...]
    dropped: tuple[str, ...]


def channel_key(name: str) -> str:
    """Return the identity a channel keeps across candidate-marker moves."""

    return recording.current_channel_name(name).lower()


def _same_file(left: Path, right: Path) -> bool:
    try:
        return left.resolve() == right.resolve()
    except OSError:
        return False


def relayout(
    source: Path,
    output: Path,
    *,
    profile: str = DEFAULT_PROFILE,
    schema_path: Path = recording.DEFAULT_SCHEMA,
    force: bool = False,
) -> RelayoutSummary:
    source = Path(source)
    output = Path(output)
    if _same_file(source, output):
        raise ValueError(f"{output}: output would overwrite the source recording")
    if output.exists() and not force:
        raise FileExistsError(
            f"{output}: output already exists; use --force to replace it"
        )
    mlvlg.validate_mlg(source)

    data = source.read_bytes()
    (
        _format,
        _version,
        start_epoch,
        _info_start,
        data_begin,
        record_length,
        _field_count,
    ) = struct.unpack(">6sHIIIHH", data[: mlvlg.MLG_HEADER_SIZE])
    recorded = mlvlg.read_fields(source)
    positions = {}
    for index, spec in enumerate(recorded):
        key = channel_key(spec.name)
        if key in positions:
            raise mlvlg.MlvlgError(
                f"{source}: channels {recorded[positions[key]].name!r} and "
                f"{spec.name!r} name one channel"
            )
        positions[key] = index

    bindings = recording.build_bindings(profile, schema_path)
    fields = tuple(binding.spec for binding in bindings)
    sources = [positions.get(channel_key(spec.name)) for spec in fields]
    for binding, position in zip(bindings, sources):
        if binding.source in REQUIRED_SOURCES and position is None:
            raise mlvlg.MlvlgError(
                f"{source}: no {binding.spec.name!r} channel, so it is not a "
                "dashboard recording"
            )
    bound = {position for position in sources if position is not None}

    reader = struct.Struct(
        ">"
        + "".join(mlvlg.FIELD_STRUCTS[spec.field_type][1:] for spec in recorded)
    )
    payload = bytearray(mlvlg.encode_header(fields, start_epoch))
    for spec in fields:
        payload += mlvlg.encode_field(spec)
    data_records = 0
    marker_records = 0
    offset = data_begin
    while offset < len(data):
        prefix = data[offset : offset + 4]
        if prefix[0] != 0:
            end = offset + 4 + mlvlg.MLG_MARKER_MESSAGE_SIZE
            payload += data[offset:end]
            offset = end
            marker_records += 1
            continue
        values = reader.unpack_from(data, offset + 4)
        row = []
        for position in sources:
            row.append(math.nan if position is None else values[position])
        record = mlvlg.encode_record_data(fields, row)
        payload += prefix + record + bytes((sum(record) & 0xFF,))
        offset += 4 + record_length + 1
        data_records += 1

    _write(output, bytes(payload))
    return RelayoutSummary(
        source=source,
        output=output,
        fields=len(fields),
        data_records=data_records,
        marker_records=marker_records,
        missing=tuple(
            spec.name
            for spec, position in zip(fields, sources)
            if position is None
        ),
        dropped=tuple(
            spec.name
            for index, spec in enumerate(recorded)
            if index not in bound
        ),
    )


def _write(output: Path, payload: bytes) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
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


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="+", type=Path, help="dashboard MLVLG files")
    destination = parser.add_mutually_exclusive_group(required=True)
    destination.add_argument(
        "-o", "--output", type=Path, help="output path; valid only with one input"
    )
    destination.add_argument(
        "--output-dir",
        type=Path,
        help="write every output under its source file name to this directory",
    )
    parser.add_argument(
        "--profile",
        default=DEFAULT_PROFILE,
        help="telemetry profile whose recorder layout the output takes",
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=recording.DEFAULT_SCHEMA,
        help="telemetry wire-schema JSON",
    )
    parser.add_argument(
        "--force", action="store_true", help="replace existing output files"
    )
    args = parser.parse_args(argv)
    if args.output is not None and len(args.logs) != 1:
        parser.error("--output requires exactly one input")

    try:
        for source in args.logs:
            output = args.output or args.output_dir / source.name
            summary = relayout(
                source,
                output,
                profile=args.profile,
                schema_path=args.schema,
                force=args.force,
            )
            print(
                f"{summary.source} -> {summary.output}: {summary.fields} "
                f"fields, {summary.data_records} records, "
                f"{summary.marker_records} markers"
            )
            if summary.missing:
                print("  NaN in every record: " + ", ".join(summary.missing))
            if summary.dropped:
                print("  left out: " + ", ".join(summary.dropped))
    except (mlvlg.MlvlgError, OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
