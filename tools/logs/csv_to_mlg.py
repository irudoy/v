#!/usr/bin/env python3
"""Convert long-form diagnostic CSV logs to MLVLG v2 files."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, datetime, time
import hashlib
import math
import os
from pathlib import Path
import re
import struct
import sys
import tempfile
from typing import BinaryIO, Iterator
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


MLG_FORMAT_VERSION = 2
MLG_HEADER_SIZE = 24
MLG_FIELD_SIZE = 89
MLG_FIELD_NAME_SIZE = 34
MLG_FIELD_UNITS_SIZE = 10
MLG_FIELD_CATEGORY_SIZE = 34

MLG_U32 = 4
MLG_F32 = 7

MLG_FLOAT = 0
MLG_DATE = 3
MLG_ON_OFF = 4

# UltraLog recognizes a u16 timestamp wrap only when the raw drop exceeds
# 30,000 ticks. Keeping every interval at or below 0.3 seconds makes each
# wrapped drop at least 35,536 ticks and therefore unambiguous to its parser.
DEFAULT_MAX_GAP_SECONDS = 0.3
MAX_SAFE_GAP_SECONDS = 0.3
TIMESTAMP_TICKS_PER_SECOND = 100_000
BLOCK_COUNTER_MODULUS = 256

REQUIRED_COLUMNS = {
    "SECONDS",
    "PID",
    "VALUE",
    "UNITS",
    "LATITUDE",
    "LONGTITUDE",
}
DATE_PREFIX = re.compile(r"^(?P<date>\d{4}-\d{2}-\d{2})")

UNIT_DIGITS = {
    "": 3,
    "$": 2,
    "%": 1,
    "L": 3,
    "L/100km": 2,
    "L/h": 2,
    "V": 3,
    "bar": 3,
    "deg": 1,
    "degC": 1,
    "g": 3,
    "g/sec": 2,
    "hp": 1,
    "km": 3,
    "km/h": 2,
    "m": 1,
    "ms": 3,
    "mV": 0,
    "rpm": 1,
    "s": 4,
}


class ConversionError(ValueError):
    """Raised when a source log cannot be converted without ambiguity."""


@dataclass
class SourceField:
    source_name: str
    units: str
    all_binary: bool = True
    all_integer: bool = True

    def observe(self, value: float) -> None:
        if value not in (0.0, 1.0):
            self.all_binary = False
        if not value.is_integer():
            self.all_integer = False


@dataclass(frozen=True)
class FieldSpec:
    name: str
    units: str
    category: str
    field_type: int
    display_style: int
    digits: int
    source_name: str | None = None

    @property
    def data_size(self) -> int:
        if self.field_type in (MLG_U32, MLG_F32):
            return 4
        raise ConversionError(f"Unsupported MLG field type: {self.field_type}")


@dataclass(frozen=True)
class ScanResult:
    row_count: int
    unique_timestamps: int
    duplicate_pid_updates: int
    first_seconds: float
    last_seconds: float
    source_fields: tuple[SourceField, ...]
    has_latitude: bool
    has_longitude: bool


@dataclass(frozen=True)
class ConversionSummary:
    source: Path
    output: Path
    source_rows: int
    source_fields: int
    mlg_fields: int
    event_records: int
    bridge_records: int
    record_length: int
    output_size: int

    @property
    def records(self) -> int:
        return self.event_records + self.bridge_records


@dataclass(frozen=True)
class ValidationSummary:
    fields: int
    record_length: int
    records: int


def _parse_number(raw: str, label: str, line_number: int) -> float:
    try:
        value = float(raw)
    except (TypeError, ValueError) as exc:
        raise ConversionError(
            f"line {line_number}: {label} is not numeric: {raw!r}"
        ) from exc
    if not math.isfinite(value):
        raise ConversionError(
            f"line {line_number}: {label} is not finite: {raw!r}"
        )
    return value


def _optional_number(raw: str | None, label: str, line_number: int) -> float | None:
    if raw is None or not raw.strip():
        return None
    return _parse_number(raw, label, line_number)


def _optional_coordinate(
    raw: str | None,
    label: str,
    line_number: int,
    minimum: float,
    maximum: float,
) -> float | None:
    value = _optional_number(raw, label, line_number)
    if value is not None and not minimum <= value <= maximum:
        raise ConversionError(
            f"line {line_number}: {label} is outside "
            f"[{minimum}, {maximum}]: {value}"
        )
    return value


def _open_reader(path: Path):
    stream = path.open(encoding="utf-8-sig", newline="")
    reader = csv.DictReader(stream, delimiter=";")
    missing = REQUIRED_COLUMNS - set(reader.fieldnames or ())
    if missing:
        stream.close()
        names = ", ".join(sorted(missing))
        raise ConversionError(f"{path}: missing CSV columns: {names}")
    return stream, reader


def scan_csv(path: Path) -> ScanResult:
    fields: dict[str, SourceField] = {}
    row_count = 0
    unique_timestamps = 0
    duplicate_pid_updates = 0
    first_seconds: float | None = None
    last_seconds: float | None = None
    current_seconds: float | None = None
    current_pids: set[str] = set()
    has_latitude = False
    has_longitude = False

    stream, reader = _open_reader(path)
    try:
        for line_number, row in enumerate(reader, start=2):
            row_count += 1
            seconds = _parse_number(row["SECONDS"], "SECONDS", line_number)
            if last_seconds is not None and seconds < last_seconds:
                raise ConversionError(
                    f"line {line_number}: SECONDS decreased from "
                    f"{last_seconds} to {seconds}"
                )
            if first_seconds is None:
                first_seconds = seconds
            last_seconds = seconds

            if current_seconds != seconds:
                unique_timestamps += 1
                current_seconds = seconds
                current_pids.clear()

            source_name = row["PID"].strip()
            if not source_name:
                raise ConversionError(f"line {line_number}: PID is empty")
            if source_name in current_pids:
                duplicate_pid_updates += 1
            current_pids.add(source_name)

            units = row["UNITS"].strip()
            field = fields.get(source_name)
            if field is None:
                field = SourceField(source_name=source_name, units=units)
                fields[source_name] = field
            elif field.units != units:
                raise ConversionError(
                    f"line {line_number}: PID {source_name!r} changed units "
                    f"from {field.units!r} to {units!r}"
                )
            field.observe(_parse_number(row["VALUE"], "VALUE", line_number))

            if (
                _optional_coordinate(
                    row["LATITUDE"], "LATITUDE", line_number, -90.0, 90.0
                )
                is not None
            ):
                has_latitude = True
            if (
                _optional_coordinate(
                    row["LONGTITUDE"],
                    "LONGTITUDE",
                    line_number,
                    -180.0,
                    180.0,
                )
                is not None
            ):
                has_longitude = True
    finally:
        stream.close()

    if first_seconds is None or last_seconds is None:
        raise ConversionError(f"{path}: CSV contains no data rows")

    return ScanResult(
        row_count=row_count,
        unique_timestamps=unique_timestamps,
        duplicate_pid_updates=duplicate_pid_updates,
        first_seconds=first_seconds,
        last_seconds=last_seconds,
        source_fields=tuple(fields.values()),
        has_latitude=has_latitude,
        has_longitude=has_longitude,
    )


def _ascii_text(value: str) -> str:
    replacements = {
        "\u00b0": "deg",
        "\u2103": "degC",
        "\u2013": "-",
        "\u2014": "-",
        "\u2192": "->",
        "\u2190": "<-",
    }
    for source, replacement in replacements.items():
        value = value.replace(source, replacement)
    value = value.replace("\x00", "")
    return value.encode("ascii", "replace").decode("ascii")


def _compact_text(value: str, limit: int) -> str:
    value = _ascii_text(value).strip()
    if len(value) <= limit:
        return value
    head = (limit - 1) // 2
    tail = limit - 1 - head
    return f"{value[:head]}~{value[-tail:]}"


def _unique_name(value: str, source_identity: str, used: set[str]) -> str:
    candidate = _compact_text(value, MLG_FIELD_NAME_SIZE - 1)
    if not candidate:
        candidate = "Field"
    if candidate not in used:
        used.add(candidate)
        return candidate

    digest = hashlib.sha1(source_identity.encode("utf-8")).hexdigest()[:8]
    suffix = f"~{digest}"
    prefix_limit = MLG_FIELD_NAME_SIZE - 1 - len(suffix)
    candidate = f"{_ascii_text(value)[:prefix_limit]}{suffix}"
    if candidate in used:
        raise ConversionError(
            f"MLG field-name collision after shortening: {source_identity!r}"
        )
    used.add(candidate)
    return candidate


def _normalise_source_name(source_name: str) -> tuple[str, str]:
    if source_name.startswith("[NC] "):
        return source_name[5:], "Nissan Consult"
    if "(GPS)" in source_name:
        return source_name, "GPS"
    return source_name, "Calculated"


def _normalise_units(units: str) -> str:
    return _compact_text(units, MLG_FIELD_UNITS_SIZE - 1)


def build_field_specs(scan: ScanResult) -> tuple[FieldSpec, ...]:
    used = {"Date", "Elapsed", "gps_lat", "gps_lon"}
    fields = [
        FieldSpec(
            name="Date",
            units="sec",
            category="Time",
            field_type=MLG_U32,
            display_style=MLG_DATE,
            digits=0,
        ),
        FieldSpec(
            name="Elapsed",
            units="s",
            category="Time",
            field_type=MLG_F32,
            display_style=MLG_FLOAT,
            digits=4,
        ),
    ]
    if scan.has_latitude:
        # Matches the canlogger GPS contract used by the local UltraLog map.
        fields.append(
            FieldSpec(
                name="gps_lat",
                units="deg",
                category="GPS",
                field_type=MLG_F32,
                display_style=MLG_FLOAT,
                digits=6,
            )
        )
    if scan.has_longitude:
        # Matches the canlogger GPS contract used by the local UltraLog map.
        fields.append(
            FieldSpec(
                name="gps_lon",
                units="deg",
                category="GPS",
                field_type=MLG_F32,
                display_style=MLG_FLOAT,
                digits=6,
            )
        )

    for source in scan.source_fields:
        base_name, category = _normalise_source_name(source.source_name)
        units = _normalise_units(source.units)
        display_style = (
            MLG_ON_OFF if source.all_binary and not units else MLG_FLOAT
        )
        if display_style == MLG_ON_OFF:
            digits = 0
        elif units in UNIT_DIGITS:
            digits = UNIT_DIGITS[units]
        elif source.all_integer:
            digits = 0
        else:
            digits = 3
        fields.append(
            FieldSpec(
                name=_unique_name(base_name, source.source_name, used),
                units=units,
                category=_compact_text(
                    category, MLG_FIELD_CATEGORY_SIZE - 1
                ),
                field_type=MLG_F32,
                display_style=display_style,
                digits=digits,
                source_name=source.source_name,
            )
        )

    return tuple(fields)


def _encode_text(value: str, size: int) -> bytes:
    encoded = _ascii_text(value).encode("ascii")
    if len(encoded) >= size:
        raise ConversionError(
            f"MLG text field exceeds {size - 1} bytes: {value!r}"
        )
    return encoded + bytes(size - len(encoded))


def _encode_field(field: FieldSpec) -> bytes:
    result = b"".join(
        (
            struct.pack(">B", field.field_type),
            _encode_text(field.name, MLG_FIELD_NAME_SIZE),
            _encode_text(field.units, MLG_FIELD_UNITS_SIZE),
            struct.pack(
                ">Bffb",
                field.display_style,
                1.0,
                0.0,
                field.digits,
            ),
            _encode_text(field.category, MLG_FIELD_CATEGORY_SIZE),
        )
    )
    if len(result) != MLG_FIELD_SIZE:
        raise AssertionError(f"encoded MLG field is {len(result)} bytes")
    return result


def _source_date(path: Path, override: date | None) -> date:
    if override is not None:
        return override
    match = DATE_PREFIX.match(path.name)
    if match is None:
        raise ConversionError(
            f"{path}: filename does not start with YYYY-MM-DD; use --date"
        )
    try:
        return date.fromisoformat(match.group("date"))
    except ValueError as exc:
        raise ConversionError(f"{path}: invalid date in filename") from exc


def _midnight_epoch(log_date: date, zone: ZoneInfo) -> float:
    return datetime.combine(log_date, time.min, tzinfo=zone).timestamp()


def _iter_groups(path: Path) -> Iterator[tuple[float, list[dict[str, str]]]]:
    stream, reader = _open_reader(path)
    try:
        group_seconds: float | None = None
        group: list[dict[str, str]] = []
        for line_number, row in enumerate(reader, start=2):
            seconds = _parse_number(row["SECONDS"], "SECONDS", line_number)
            row["_line_number"] = str(line_number)
            if group_seconds is None:
                group_seconds = seconds
            if seconds != group_seconds:
                yield group_seconds, group
                group_seconds = seconds
                group = []
            group.append(row)
        if group_seconds is not None:
            yield group_seconds, group
    finally:
        stream.close()


def _record_data(
    fields: tuple[FieldSpec, ...],
    current: dict[str, float],
    seconds: float,
    first_seconds: float,
    midnight_epoch: float,
    latitude: float,
    longitude: float,
) -> bytes:
    unix_seconds = math.floor(midnight_epoch + seconds + 1e-9)
    if not 0 <= unix_seconds <= 0xFFFFFFFF:
        raise ConversionError(
            f"Unix timestamp is outside the MLG U32 range: {unix_seconds}"
        )

    parts = [struct.pack(">I", unix_seconds)]
    for field in fields[1:]:
        if field.name == "Elapsed":
            value = seconds - first_seconds
        elif field.name == "gps_lat":
            value = latitude
        elif field.name == "gps_lon":
            value = longitude
        elif field.source_name is not None:
            value = current[field.source_name]
        else:
            raise AssertionError(f"unknown synthetic field: {field.name}")
        parts.append(struct.pack(">f", value))
    return b"".join(parts)


def _write_block(
    output: BinaryIO,
    fields: tuple[FieldSpec, ...],
    current: dict[str, float],
    seconds: float,
    first_seconds: float,
    midnight_epoch: float,
    latitude: float,
    longitude: float,
    record_index: int,
) -> None:
    data = _record_data(
        fields,
        current,
        seconds,
        first_seconds,
        midnight_epoch,
        latitude,
        longitude,
    )
    elapsed = seconds - first_seconds
    timestamp = round(elapsed * TIMESTAMP_TICKS_PER_SECOND) & 0xFFFF
    output.write(
        b"\x00"
        + bytes((record_index % BLOCK_COUNTER_MODULUS,))
        + struct.pack(">H", timestamp)
        + data
        + bytes((sum(data) & 0xFF,))
    )


def validate_mlg(path: Path) -> ValidationSummary:
    with path.open("rb") as stream:
        header = stream.read(MLG_HEADER_SIZE)
        if len(header) != MLG_HEADER_SIZE:
            raise ConversionError(f"{path}: truncated MLG header")
        (
            file_format,
            version,
            _timestamp,
            info_data_start,
            data_begin,
            record_length,
            field_count,
        ) = struct.unpack(">6sHIIIHH", header)
        if file_format != b"MLVLG\x00":
            raise ConversionError(f"{path}: invalid MLG signature")
        if version != MLG_FORMAT_VERSION:
            raise ConversionError(f"{path}: unsupported MLG version {version}")
        if info_data_start != 0:
            raise ConversionError(f"{path}: unexpected MLG info-data section")
        expected_data_begin = MLG_HEADER_SIZE + field_count * MLG_FIELD_SIZE
        if data_begin != expected_data_begin:
            raise ConversionError(
                f"{path}: data begins at {data_begin}, expected "
                f"{expected_data_begin}"
            )
        descriptors = stream.read(field_count * MLG_FIELD_SIZE)
        if len(descriptors) != field_count * MLG_FIELD_SIZE:
            raise ConversionError(f"{path}: truncated MLG field descriptors")

        block_size = record_length + 5
        records = 0
        while True:
            block = stream.read(block_size)
            if not block:
                break
            if len(block) != block_size:
                raise ConversionError(f"{path}: truncated MLG data block")
            if block[0] != 0:
                raise ConversionError(
                    f"{path}: unsupported MLG block type {block[0]}"
                )
            if block[1] != records % BLOCK_COUNTER_MODULUS:
                raise ConversionError(
                    f"{path}: invalid block counter at record {records}"
                )
            data = block[4:-1]
            if sum(data) & 0xFF != block[-1]:
                raise ConversionError(
                    f"{path}: CRC mismatch at record {records}"
                )
            records += 1

    if records == 0:
        raise ConversionError(f"{path}: MLG contains no data records")
    return ValidationSummary(
        fields=field_count,
        record_length=record_length,
        records=records,
    )


def convert_csv(
    source: Path,
    output: Path,
    *,
    timezone_name: str = "Asia/Vladivostok",
    max_gap_seconds: float = DEFAULT_MAX_GAP_SECONDS,
    date_override: date | None = None,
    force: bool = False,
) -> ConversionSummary:
    if not 0 < max_gap_seconds <= MAX_SAFE_GAP_SECONDS:
        raise ConversionError(
            f"max gap must be greater than 0 and no more than "
            f"{MAX_SAFE_GAP_SECONDS} seconds"
        )
    if not source.is_file():
        raise ConversionError(f"{source}: source file does not exist")
    if output.exists() and not force:
        raise ConversionError(
            f"{output}: output already exists; use --force to replace it"
        )
    try:
        zone = ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError as exc:
        raise ConversionError(f"unknown timezone: {timezone_name}") from exc

    scan = scan_csv(source)
    fields = build_field_specs(scan)
    record_length = sum(field.data_size for field in fields)
    if record_length > 0xFFFF:
        raise ConversionError(
            f"MLG record is too large: {record_length} bytes"
        )
    if len(fields) > 0xFFFF:
        raise ConversionError(f"too many MLG fields: {len(fields)}")

    log_date = _source_date(source, date_override)
    midnight_epoch = _midnight_epoch(log_date, zone)
    start_timestamp = math.floor(midnight_epoch + scan.first_seconds + 1e-9)
    data_begin = MLG_HEADER_SIZE + len(fields) * MLG_FIELD_SIZE
    header = struct.pack(
        ">6sHIIIHH",
        b"MLVLG",
        MLG_FORMAT_VERSION,
        start_timestamp,
        0,
        data_begin,
        record_length,
        len(fields),
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output.name}.",
        suffix=".tmp",
        dir=output.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)

    current = {
        field.source_name: math.nan
        for field in fields
        if field.source_name is not None
    }
    latitude = math.nan
    longitude = math.nan
    event_records = 0
    bridge_records = 0
    record_index = 0
    previous_seconds: float | None = None

    try:
        with temporary.open("wb") as destination:
            destination.write(header)
            for field in fields:
                destination.write(_encode_field(field))

            for seconds, rows in _iter_groups(source):
                if previous_seconds is not None:
                    bridge_seconds = previous_seconds + max_gap_seconds
                    while bridge_seconds < seconds - 1e-12:
                        _write_block(
                            destination,
                            fields,
                            current,
                            bridge_seconds,
                            scan.first_seconds,
                            midnight_epoch,
                            latitude,
                            longitude,
                            record_index,
                        )
                        record_index += 1
                        bridge_records += 1
                        bridge_seconds += max_gap_seconds

                for row in rows:
                    line_number = int(row["_line_number"])
                    source_name = row["PID"].strip()
                    current[source_name] = _parse_number(
                        row["VALUE"], "VALUE", line_number
                    )
                    row_latitude = _optional_coordinate(
                        row["LATITUDE"],
                        "LATITUDE",
                        line_number,
                        -90.0,
                        90.0,
                    )
                    row_longitude = _optional_coordinate(
                        row["LONGTITUDE"],
                        "LONGTITUDE",
                        line_number,
                        -180.0,
                        180.0,
                    )
                    if row_latitude is not None:
                        latitude = row_latitude
                    if row_longitude is not None:
                        longitude = row_longitude

                _write_block(
                    destination,
                    fields,
                    current,
                    seconds,
                    scan.first_seconds,
                    midnight_epoch,
                    latitude,
                    longitude,
                    record_index,
                )
                record_index += 1
                event_records += 1
                previous_seconds = seconds

            destination.flush()
            os.fsync(destination.fileno())

        validated = validate_mlg(temporary)
        if validated.fields != len(fields):
            raise AssertionError("validated MLG field count changed")
        if validated.record_length != record_length:
            raise AssertionError("validated MLG record length changed")
        if validated.records != record_index:
            raise AssertionError("validated MLG record count changed")
        if output.exists() and not force:
            raise ConversionError(
                f"{output}: output appeared during conversion; use --force"
            )
        output_mode = source.stat().st_mode & 0o666
        os.chmod(temporary, output_mode or 0o600)
        os.replace(temporary, output)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise

    return ConversionSummary(
        source=source,
        output=output,
        source_rows=scan.row_count,
        source_fields=len(scan.source_fields),
        mlg_fields=len(fields),
        event_records=event_records,
        bridge_records=bridge_records,
        record_length=record_length,
        output_size=output.stat().st_size,
    )


def _parse_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            "date must use YYYY-MM-DD format"
        ) from exc


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
        help="write every MLG file to this directory",
    )
    parser.add_argument(
        "--timezone",
        default="Asia/Vladivostok",
        help="IANA timezone used to reconstruct Unix time",
    )
    parser.add_argument(
        "--date",
        type=_parse_date,
        help="log date override in YYYY-MM-DD format",
    )
    parser.add_argument(
        "--max-gap",
        type=float,
        default=DEFAULT_MAX_GAP_SECONDS,
        help="maximum interval between emitted MLG records in seconds",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace existing output files",
    )
    args = parser.parse_args(argv)

    if args.output is not None and len(args.inputs) != 1:
        parser.error("--output requires exactly one input")
    if args.output is not None and args.output_dir is not None:
        parser.error("--output and --output-dir are mutually exclusive")

    try:
        for source in args.inputs:
            output = _output_path(source, args.output, args.output_dir)
            summary = convert_csv(
                source,
                output,
                timezone_name=args.timezone,
                max_gap_seconds=args.max_gap,
                date_override=args.date,
                force=args.force,
            )
            print(
                f"{summary.source} -> {summary.output}: "
                f"{summary.source_rows} rows, "
                f"{summary.source_fields} source fields, "
                f"{summary.mlg_fields} MLG fields, "
                f"{summary.event_records} event records + "
                f"{summary.bridge_records} bridge records, "
                f"{_format_size(summary.output_size)}"
            )
    except (ConversionError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
