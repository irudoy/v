"""Minimal MLVLG v2 writer and structural validator.

The wire format follows "Binary MLG Logging (MLVLG) file format specification"
Rev. 0.94 by Philip Tobin. All integers and floating point values are stored in
big-endian byte order. A data block holds a 16-bit timestamp at 10 us per bit,
a rolling record counter, and a CRC that is the unsigned byte sum of the record
payload. The specification writes that counter as ``Counter % 255``; it rolls
over an unsigned byte here, as in the rusEFI reference writer whose logs
MegaLogViewer reads.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import struct
from typing import BinaryIO, Iterable, Sequence


MLG_FORMAT_VERSION = 2
MLG_HEADER_SIZE = 24
MLG_FIELD_SIZE = 89
MLG_FIELD_NAME_SIZE = 34
MLG_FIELD_UNITS_SIZE = 10
MLG_FIELD_CATEGORY_SIZE = 34
MLG_MARKER_MESSAGE_SIZE = 50

MLG_U08 = 0
MLG_S08 = 1
MLG_U16 = 2
MLG_S16 = 3
MLG_U32 = 4
MLG_S32 = 5
MLG_S64 = 6
MLG_F32 = 7

MLG_FLOAT = 0
MLG_HEX = 1
MLG_BITS = 2
MLG_DATE = 3
MLG_ON_OFF = 4
MLG_YES_NO = 5
MLG_HIGH_LOW = 6
MLG_ACTIVE_INACTIVE = 7
MLG_TRUE_FALSE = 8

TIMESTAMP_TICKS_PER_SECOND = 100_000
BLOCK_COUNTER_MODULUS = 256

FIELD_STRUCTS = {
    MLG_U08: ">B",
    MLG_S08: ">b",
    MLG_U16: ">H",
    MLG_S16: ">h",
    MLG_U32: ">I",
    MLG_S32: ">i",
    MLG_S64: ">q",
    MLG_F32: ">f",
}


class MlvlgError(ValueError):
    """Raised when an MLVLG file cannot be encoded or validated safely."""


@dataclass(frozen=True)
class FieldSpec:
    """One scalar MLVLG field descriptor."""

    name: str
    units: str = ""
    category: str = ""
    field_type: int = MLG_F32
    display_style: int = MLG_FLOAT
    scale: float = 1.0
    transform: float = 0.0
    digits: int = 3

    @property
    def data_size(self) -> int:
        try:
            return struct.calcsize(FIELD_STRUCTS[self.field_type])
        except KeyError as error:
            raise MlvlgError(
                f"unsupported MLVLG field type {self.field_type}"
            ) from error


@dataclass(frozen=True)
class ValidationSummary:
    fields: int
    record_length: int
    data_records: int
    marker_records: int

    @property
    def records(self) -> int:
        return self.data_records + self.marker_records


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


def encode_text(value: str, size: int) -> bytes:
    encoded = _ascii_text(value).encode("ascii")
    if len(encoded) >= size:
        raise MlvlgError(
            f"MLVLG text field exceeds {size - 1} bytes: {value!r}"
        )
    return encoded + bytes(size - len(encoded))


def encode_field(field: FieldSpec) -> bytes:
    if not -128 <= field.digits <= 127:
        raise MlvlgError(f"digits is outside signed-byte range: {field.digits}")
    field.data_size
    result = b"".join(
        (
            struct.pack(">B", field.field_type),
            encode_text(field.name, MLG_FIELD_NAME_SIZE),
            encode_text(field.units, MLG_FIELD_UNITS_SIZE),
            struct.pack(
                ">Bffb",
                field.display_style,
                field.scale,
                field.transform,
                field.digits,
            ),
            encode_text(field.category, MLG_FIELD_CATEGORY_SIZE),
        )
    )
    if len(result) != MLG_FIELD_SIZE:
        raise AssertionError(f"encoded MLVLG field is {len(result)} bytes")
    return result


def decode_text(raw: bytes) -> str:
    return raw.split(b"\x00", 1)[0].decode("ascii", "replace")


def decode_field(descriptor: bytes) -> FieldSpec:
    if len(descriptor) != MLG_FIELD_SIZE:
        raise MlvlgError(
            f"MLVLG field descriptor must be {MLG_FIELD_SIZE} bytes"
        )
    field_type = descriptor[0]
    if field_type not in FIELD_STRUCTS:
        raise MlvlgError(f"unsupported MLVLG field type {field_type}")
    name_end = 1 + MLG_FIELD_NAME_SIZE
    units_end = name_end + MLG_FIELD_UNITS_SIZE
    scaling_end = units_end + struct.calcsize(">Bffb")
    display_style, scale, transform, digits = struct.unpack(
        ">Bffb", descriptor[units_end:scaling_end]
    )
    return FieldSpec(
        name=decode_text(descriptor[1:name_end]),
        units=decode_text(descriptor[name_end:units_end]),
        category=decode_text(descriptor[scaling_end:MLG_FIELD_SIZE]),
        field_type=field_type,
        display_style=display_style,
        scale=scale,
        transform=transform,
        digits=digits,
    )


def read_fields(path: Path) -> tuple[FieldSpec, ...]:
    """Return the field descriptors declared by an MLVLG header."""

    data = Path(path).read_bytes()
    if len(data) < MLG_HEADER_SIZE:
        raise MlvlgError(f"{path}: truncated MLVLG header")
    field_count = struct.unpack(">H", data[22:MLG_HEADER_SIZE])[0]
    end = MLG_HEADER_SIZE + field_count * MLG_FIELD_SIZE
    if len(data) < end:
        raise MlvlgError(f"{path}: truncated MLVLG field descriptors")
    return tuple(
        decode_field(
            data[
                MLG_HEADER_SIZE
                + index * MLG_FIELD_SIZE : MLG_HEADER_SIZE
                + (index + 1) * MLG_FIELD_SIZE
            ]
        )
        for index in range(field_count)
    )


def record_length(fields: Iterable[FieldSpec]) -> int:
    return sum(field.data_size for field in fields)


def encode_header(
    fields: Sequence[FieldSpec], start_timestamp: int
) -> bytes:
    if not 0 <= start_timestamp <= 0xFFFFFFFF:
        raise MlvlgError(
            f"Unix timestamp is outside the MLVLG U32 range: {start_timestamp}"
        )
    if len(fields) > 0xFFFF:
        raise MlvlgError(f"too many MLVLG fields: {len(fields)}")
    data_size = record_length(fields)
    if data_size > 0xFFFF:
        raise MlvlgError(f"MLVLG record is too large: {data_size} bytes")
    data_begin = MLG_HEADER_SIZE + len(fields) * MLG_FIELD_SIZE
    return struct.pack(
        ">6sHIIIHH",
        b"MLVLG",
        MLG_FORMAT_VERSION,
        start_timestamp,
        0,
        data_begin,
        data_size,
        len(fields),
    )


def encode_value(field: FieldSpec, value: int | float) -> bytes:
    format_string = FIELD_STRUCTS.get(field.field_type)
    if format_string is None:
        raise MlvlgError(f"unsupported MLVLG field type {field.field_type}")
    if field.field_type == MLG_F32:
        try:
            numeric = float(value)
        except (TypeError, ValueError) as error:
            raise MlvlgError(
                f"field {field.name!r} is not numeric: {value!r}"
            ) from error
    else:
        if isinstance(value, bool):
            numeric = int(value)
        elif isinstance(value, int):
            numeric = value
        elif isinstance(value, float) and value.is_integer():
            numeric = int(value)
        else:
            raise MlvlgError(
                f"integer field {field.name!r} has non-integer value {value!r}"
            )
    try:
        return struct.pack(format_string, numeric)
    except (OverflowError, struct.error) as error:
        raise MlvlgError(
            f"field {field.name!r} value is outside its wire range: {value!r}"
        ) from error


def encode_record_data(
    fields: Sequence[FieldSpec], values: Sequence[int | float]
) -> bytes:
    if len(values) != len(fields):
        raise MlvlgError(
            f"record has {len(values)} values for {len(fields)} fields"
        )
    return b"".join(
        encode_value(field, value) for field, value in zip(fields, values)
    )


def encode_data_block(
    fields: Sequence[FieldSpec],
    values: Sequence[int | float],
    counter: int,
    elapsed_seconds: float,
) -> bytes:
    data = encode_record_data(fields, values)
    return encode_payload_block(data, counter, elapsed_seconds)


def encode_payload_block(
    data: bytes, counter: int, elapsed_seconds: float
) -> bytes:
    """Encode one data block from an already packed record payload."""

    if not math.isfinite(elapsed_seconds) or elapsed_seconds < 0:
        raise MlvlgError(
            f"elapsed time must be finite and nonnegative: {elapsed_seconds!r}"
        )
    timestamp = round(elapsed_seconds * TIMESTAMP_TICKS_PER_SECOND) & 0xFFFF
    return (
        b"\x00"
        + bytes((counter % BLOCK_COUNTER_MODULUS,))
        + struct.pack(">H", timestamp)
        + data
        + bytes((sum(data) & 0xFF,))
    )


class StreamWriter:
    """Write a fixed-schema MLVLG stream without owning the destination."""

    def __init__(
        self,
        destination: BinaryIO,
        fields: Sequence[FieldSpec],
        start_timestamp: int,
    ):
        self.destination = destination
        self.fields = tuple(fields)
        self.record_length = record_length(self.fields)
        self.data_records = 0
        self.marker_records = 0
        self._counter = 0
        self._last_elapsed: float | None = None
        destination.write(encode_header(self.fields, start_timestamp))
        for field in self.fields:
            destination.write(encode_field(field))

    def write(self, values: Sequence[int | float], elapsed_seconds: float) -> None:
        if (
            self._last_elapsed is not None
            and elapsed_seconds < self._last_elapsed
        ):
            raise MlvlgError(
                f"elapsed time decreased from {self._last_elapsed} "
                f"to {elapsed_seconds}"
            )
        self.destination.write(
            encode_data_block(
                self.fields,
                values,
                self._counter,
                elapsed_seconds,
            )
        )
        self._counter = (self._counter + 1) % BLOCK_COUNTER_MODULUS
        self._last_elapsed = elapsed_seconds
        self.data_records += 1

    def flush(self) -> None:
        self.destination.flush()


def _descriptor_record_length(descriptors: bytes, field_count: int) -> int:
    total = 0
    for index in range(field_count):
        field_type = descriptors[index * MLG_FIELD_SIZE]
        format_string = FIELD_STRUCTS.get(field_type)
        if format_string is None:
            raise MlvlgError(
                f"unsupported MLVLG field type {field_type} at index {index}"
            )
        total += struct.calcsize(format_string)
    return total


def validate_mlg(path: Path, *, require_data: bool = True) -> ValidationSummary:
    path = Path(path)
    with path.open("rb") as stream:
        header = stream.read(MLG_HEADER_SIZE)
        if len(header) != MLG_HEADER_SIZE:
            raise MlvlgError(f"{path}: truncated MLVLG header")
        (
            file_format,
            version,
            _timestamp,
            info_data_start,
            data_begin,
            declared_record_length,
            field_count,
        ) = struct.unpack(">6sHIIIHH", header)
        if file_format != b"MLVLG\x00":
            raise MlvlgError(f"{path}: invalid MLVLG signature")
        if version != MLG_FORMAT_VERSION:
            raise MlvlgError(f"{path}: unsupported MLVLG version {version}")
        if info_data_start != 0:
            raise MlvlgError(f"{path}: unexpected MLVLG info-data section")
        expected_data_begin = MLG_HEADER_SIZE + field_count * MLG_FIELD_SIZE
        if data_begin != expected_data_begin:
            raise MlvlgError(
                f"{path}: data begins at {data_begin}, expected "
                f"{expected_data_begin}"
            )
        descriptors = stream.read(field_count * MLG_FIELD_SIZE)
        if len(descriptors) != field_count * MLG_FIELD_SIZE:
            raise MlvlgError(f"{path}: truncated MLVLG field descriptors")
        actual_record_length = _descriptor_record_length(
            descriptors, field_count
        )
        if declared_record_length != actual_record_length:
            raise MlvlgError(
                f"{path}: record length is {declared_record_length}, "
                f"descriptors require {actual_record_length}"
            )

        data_records = 0
        marker_records = 0
        block_counter = 0
        while True:
            prefix = stream.read(4)
            if not prefix:
                break
            if len(prefix) != 4:
                raise MlvlgError(f"{path}: truncated MLVLG block header")
            block_type, counter = prefix[0], prefix[1]
            if counter != block_counter % BLOCK_COUNTER_MODULUS:
                raise MlvlgError(
                    f"{path}: invalid block counter at block {block_counter}"
                )
            if block_type == 0:
                data = stream.read(declared_record_length)
                crc = stream.read(1)
                if len(data) != declared_record_length or len(crc) != 1:
                    raise MlvlgError(f"{path}: truncated MLVLG data block")
                if sum(data) & 0xFF != crc[0]:
                    raise MlvlgError(
                        f"{path}: CRC mismatch at data record {data_records}"
                    )
                data_records += 1
            elif block_type == 1:
                message = stream.read(MLG_MARKER_MESSAGE_SIZE)
                if len(message) != MLG_MARKER_MESSAGE_SIZE:
                    raise MlvlgError(f"{path}: truncated MLVLG marker block")
                marker_records += 1
            else:
                raise MlvlgError(
                    f"{path}: unsupported MLVLG block type {block_type}"
                )
            block_counter += 1

    if require_data and data_records == 0:
        raise MlvlgError(f"{path}: MLVLG contains no data records")
    return ValidationSummary(
        fields=field_count,
        record_length=declared_record_length,
        data_records=data_records,
        marker_records=marker_records,
    )
