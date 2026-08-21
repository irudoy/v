#!/usr/bin/env python3
"""Calculate and verify registered ROM checksum layouts."""

from __future__ import annotations

from dataclasses import dataclass, fields
from functools import lru_cache
from pathlib import Path
import tomllib


DEFAULT_REGISTRY = Path(__file__).with_name("checksum-layouts.toml")
LAYOUT_FIELDS = frozenset(
    {
        "roms",
        "rom_size",
        "sum16_a_field",
        "sum16_a_start",
        "sum16_a_end",
        "runtime_a_xor_field",
        "runtime_a_sum_field",
        "runtime_a_start",
        "runtime_a_end",
        "runtime_a_exclusions",
        "sum16_b_field",
        "sum16_b_start",
        "sum16_b_end",
        "runtime_b_xor_field",
        "runtime_b_sum_field",
        "runtime_b_start",
        "runtime_b_end",
        "runtime_b_exclusions",
        "evidence",
    }
)


class ChecksumError(ValueError):
    """Raised when a checksum layout or ROM does not satisfy its contract."""


@dataclass(frozen=True)
class ChecksumLayout:
    key: str
    roms: tuple[str, ...]
    rom_size: int
    sum16_a_field: int
    sum16_a_start: int
    sum16_a_end: int
    runtime_a_xor_field: int
    runtime_a_sum_field: int
    runtime_a_start: int
    runtime_a_end: int
    runtime_a_exclusions: frozenset[int]
    sum16_b_field: int
    sum16_b_start: int
    sum16_b_end: int
    runtime_b_xor_field: int
    runtime_b_sum_field: int
    runtime_b_start: int
    runtime_b_end: int
    runtime_b_exclusions: frozenset[int]
    evidence: str

    @property
    def checksum_fields(self):
        return (
            ("sum16_a", self.sum16_a_field, 2),
            ("runtime_a_xor", self.runtime_a_xor_field, 4),
            ("runtime_a_sum", self.runtime_a_sum_field, 4),
            ("sum16_b", self.sum16_b_field, 2),
            ("runtime_b_sum", self.runtime_b_sum_field, 4),
            ("runtime_b_xor", self.runtime_b_xor_field, 4),
        )


@dataclass(frozen=True)
class ChecksumValues:
    sum16_a: int
    sum16_b: int
    runtime_a_xor: int
    runtime_a_sum: int
    runtime_b_sum: int
    runtime_b_xor: int

    def items(self):
        return tuple(
            (field.name, getattr(self, field.name))
            for field in fields(self)
        )


@dataclass(frozen=True)
class ChecksumVerification:
    stored: ChecksumValues
    calculated: ChecksumValues

    @property
    def mismatches(self):
        return tuple(
            name
            for name, value in self.stored.items()
            if value != getattr(self.calculated, name)
        )

    @property
    def valid(self):
        return not self.mismatches


def _require_int(row, key, context):
    value = row[key]
    if type(value) is not int or value < 0:
        raise ChecksumError(f"{context}.{key} must be a nonnegative integer")
    return value


def _validate_range(start, end, alignment, limit, context):
    if start >= end or start % alignment or end % alignment or end > limit:
        raise ChecksumError(
            f"{context} must be a nonempty {alignment}-byte-aligned range "
            f"inside 0x0..{limit:#x}"
        )


def _parse_layout(key, row, context):
    if not isinstance(row, dict) or set(row) != LAYOUT_FIELDS:
        actual = set(row) if isinstance(row, dict) else set()
        raise ChecksumError(
            f"{context}: fields differ; "
            f"missing={sorted(LAYOUT_FIELDS - actual)}; "
            f"extra={sorted(actual - LAYOUT_FIELDS)}"
        )
    roms = row["roms"]
    if (
        not isinstance(roms, list)
        or not roms
        or len(set(roms)) != len(roms)
        or any(not isinstance(rom, str) or not rom for rom in roms)
    ):
        raise ChecksumError(f"{context}.roms must be a unique nonempty array")
    if not isinstance(row["evidence"], str) or not row["evidence"].strip():
        raise ChecksumError(f"{context}.evidence must be nonempty text")

    values = {
        name: _require_int(row, name, context)
        for name in LAYOUT_FIELDS
        if name not in {"roms", "runtime_a_exclusions", "runtime_b_exclusions", "evidence"}
    }
    rom_size = values["rom_size"]
    if rom_size <= 0:
        raise ChecksumError(f"{context}.rom_size must be positive")
    _validate_range(
        values["sum16_a_start"], values["sum16_a_end"], 2, rom_size,
        f"{context}.sum16_a",
    )
    _validate_range(
        values["sum16_b_start"], values["sum16_b_end"], 2, rom_size,
        f"{context}.sum16_b",
    )
    _validate_range(
        values["runtime_a_start"], values["runtime_a_end"], 4, rom_size,
        f"{context}.runtime_a",
    )
    _validate_range(
        values["runtime_b_start"], values["runtime_b_end"], 4, rom_size,
        f"{context}.runtime_b",
    )
    for name, width in (
        ("sum16_a_field", 2),
        ("sum16_b_field", 2),
        ("runtime_a_xor_field", 4),
        ("runtime_a_sum_field", 4),
        ("runtime_b_xor_field", 4),
        ("runtime_b_sum_field", 4),
    ):
        offset = values[name]
        if offset % width or offset + width > rom_size:
            raise ChecksumError(
                f"{context}.{name} is not an in-image {width}-byte field"
            )

    exclusions = {}
    for domain in ("runtime_a", "runtime_b"):
        name = f"{domain}_exclusions"
        raw = row[name]
        if (
            not isinstance(raw, list)
            or len(raw) != len(set(raw))
            or any(type(value) is not int for value in raw)
        ):
            raise ChecksumError(f"{context}.{name} must be a unique integer array")
        start, end = values[f"{domain}_start"], values[f"{domain}_end"]
        if any(value % 4 or not start <= value < end for value in raw):
            raise ChecksumError(
                f"{context}.{name} contains an unaligned or out-of-range word"
            )
        exclusions[name] = frozenset(raw)

    required_a = {
        values["runtime_a_xor_field"],
        values["runtime_a_sum_field"],
    }
    if not required_a <= exclusions["runtime_a_exclusions"]:
        raise ChecksumError(
            f"{context}.runtime_a_exclusions must contain both Runtime A fields"
        )

    return ChecksumLayout(
        key=key,
        roms=tuple(roms),
        evidence=row["evidence"],
        **values,
        **exclusions,
    )


@lru_cache(maxsize=None)
def load_registry(path=DEFAULT_REGISTRY):
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise ChecksumError(f"checksum registry cannot be loaded: {path}: {error}") from error
    if set(document) != {"schema_version", "layout"}:
        raise ChecksumError(f"{path}: expected only schema_version and layout")
    if document["schema_version"] != 1:
        raise ChecksumError(f"{path}: unsupported schema_version")
    raw_layouts = document["layout"]
    if not isinstance(raw_layouts, dict) or not raw_layouts:
        raise ChecksumError(f"{path}: no [layout.*] entries")
    layouts = {
        key: _parse_layout(key, row, f"{path} [layout.{key}]")
        for key, row in raw_layouts.items()
    }
    by_rom = {}
    for layout in layouts.values():
        for rom in layout.roms:
            if rom in by_rom:
                raise ChecksumError(f"{path}: ROM {rom} belongs to two layouts")
            by_rom[rom] = layout
    return layouts, by_rom


def layout_for_rom(rom, path=DEFAULT_REGISTRY):
    """Return the checksum layout registered for one exact ROM label."""
    _layouts, by_rom = load_registry(Path(path))
    try:
        return by_rom[rom]
    except KeyError as error:
        raise ChecksumError(f"no checksum layout is registered for {rom}") from error


def _validated_data(image, layout):
    data = bytes(image)
    if len(data) != layout.rom_size:
        raise ChecksumError(
            f"image has {len(data)} bytes, expected {layout.rom_size} for {layout.key}"
        )
    return data


def _read_unsigned(data, offset, width):
    return int.from_bytes(data[offset : offset + width], "big")


def _write_unsigned(data, offset, width, value):
    data[offset : offset + width] = value.to_bytes(width, "big")


def _sum16(data, start, end):
    total = 0
    for offset in range(start, end, 2):
        total = (total + _read_unsigned(data, offset, 2)) & 0xFFFF
    return total


def _runtime32(data, start, end, exclusions=frozenset()):
    xor_value = 0
    sum_value = 0
    for offset in range(start, end, 4):
        if offset in exclusions:
            continue
        value = _read_unsigned(data, offset, 4)
        xor_value ^= value
        sum_value = (sum_value + value) & 0xFFFFFFFF
    return xor_value, sum_value


def stored_values(image, layout):
    """Read all six stored checksum references for one layout."""
    data = _validated_data(image, layout)
    return ChecksumValues(
        sum16_a=_read_unsigned(data, layout.sum16_a_field, 2),
        sum16_b=_read_unsigned(data, layout.sum16_b_field, 2),
        runtime_a_xor=_read_unsigned(data, layout.runtime_a_xor_field, 4),
        runtime_a_sum=_read_unsigned(data, layout.runtime_a_sum_field, 4),
        runtime_b_sum=_read_unsigned(data, layout.runtime_b_sum_field, 4),
        runtime_b_xor=_read_unsigned(data, layout.runtime_b_xor_field, 4),
    )


def calculate_values(image, layout):
    """Calculate all six references from the currently stored image."""
    data = _validated_data(image, layout)
    runtime_a_xor, runtime_a_sum = _runtime32(
        data,
        layout.runtime_a_start,
        layout.runtime_a_end,
        layout.runtime_a_exclusions,
    )
    runtime_b_xor, runtime_b_sum = _runtime32(
        data,
        layout.runtime_b_start,
        layout.runtime_b_end,
        layout.runtime_b_exclusions,
    )
    return ChecksumValues(
        sum16_a=_sum16(data, layout.sum16_a_start, layout.sum16_a_end),
        sum16_b=_sum16(data, layout.sum16_b_start, layout.sum16_b_end),
        runtime_a_xor=runtime_a_xor,
        runtime_a_sum=runtime_a_sum,
        runtime_b_sum=runtime_b_sum,
        runtime_b_xor=runtime_b_xor,
    )


def verify(image, layout):
    """Return stored and calculated values without mutating the image."""
    data = _validated_data(image, layout)
    return ChecksumVerification(
        stored=stored_values(data, layout),
        calculated=calculate_values(data, layout),
    )


def require_valid(image, layout, context="ROM image"):
    """Return verification or raise with every mismatched field."""
    result = verify(image, layout)
    if result.valid:
        return result
    details = ", ".join(
        f"{name}=stored:{getattr(result.stored, name):#x}"
        f"/calculated:{getattr(result.calculated, name):#x}"
        for name in result.mismatches
    )
    raise ChecksumError(f"{context}: checksum mismatch: {details}")


def recalculate(image, layout):
    """Return a self-consistent image using the documented dependency order."""
    data = bytearray(_validated_data(image, layout))

    runtime_b_xor, runtime_b_sum = _runtime32(
        data,
        layout.runtime_b_start,
        layout.runtime_b_end,
        layout.runtime_b_exclusions,
    )
    _write_unsigned(data, layout.runtime_b_sum_field, 4, runtime_b_sum)
    _write_unsigned(data, layout.runtime_b_xor_field, 4, runtime_b_xor)

    runtime_a_xor, runtime_a_sum = _runtime32(
        data,
        layout.runtime_a_start,
        layout.runtime_a_end,
        layout.runtime_a_exclusions,
    )
    _write_unsigned(data, layout.runtime_a_xor_field, 4, runtime_a_xor)
    _write_unsigned(data, layout.runtime_a_sum_field, 4, runtime_a_sum)

    _write_unsigned(
        data,
        layout.sum16_a_field,
        2,
        _sum16(data, layout.sum16_a_start, layout.sum16_a_end),
    )
    _write_unsigned(
        data,
        layout.sum16_b_field,
        2,
        _sum16(data, layout.sum16_b_start, layout.sum16_b_end),
    )

    result = bytes(data)
    require_valid(result, layout, f"recalculated {layout.key} image")
    return result


def checksum_byte_offsets(layout):
    """Return the complete set of bytes owned by checksum references."""
    return frozenset(
        offset
        for _name, start, width in layout.checksum_fields
        for offset in range(start, start + width)
    )
