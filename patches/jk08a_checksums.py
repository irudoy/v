#!/usr/bin/env python3
"""Calculate and verify the exact JK00A/JK03A/JK03B/JK08A checksum layout."""

from __future__ import annotations

from dataclasses import dataclass, fields


ROM_SIZE = 0x100000

SUM16_A_FIELD = 0x008200
SUM16_A_START = 0x008202
SUM16_A_END = 0x020000

RUNTIME_A_START = 0x008204
RUNTIME_A_END = 0x100000
RUNTIME_A_XOR_FIELD = 0x0096D4
RUNTIME_A_SUM_FIELD = 0x0096DC
RUNTIME_A_EXCLUSIONS = frozenset(
    (RUNTIME_A_XOR_FIELD, RUNTIME_A_SUM_FIELD, 0x020000)
)

SUM16_B_FIELD = 0x020000
SUM16_B_START = 0x020002
SUM16_B_END = 0x100000

RUNTIME_B_SUM_FIELD = 0x020404
RUNTIME_B_XOR_FIELD = 0x020408
RUNTIME_B_START = 0x02040C
RUNTIME_B_END = 0x02259C

CHECKSUM_FIELDS = (
    ("sum16_a", SUM16_A_FIELD, 2),
    ("runtime_a_xor", RUNTIME_A_XOR_FIELD, 4),
    ("runtime_a_sum", RUNTIME_A_SUM_FIELD, 4),
    ("sum16_b", SUM16_B_FIELD, 2),
    ("runtime_b_sum", RUNTIME_B_SUM_FIELD, 4),
    ("runtime_b_xor", RUNTIME_B_XOR_FIELD, 4),
)


class ChecksumError(ValueError):
    """Raised when a ROM does not satisfy the exact checksum contract."""


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


def _validated_data(image):
    data = bytes(image)
    if len(data) != ROM_SIZE:
        raise ChecksumError(
            f"image has {len(data)} bytes, expected {ROM_SIZE}"
        )
    return data


def _read_unsigned(data, offset, width):
    return int.from_bytes(data[offset : offset + width], "big")


def _write_unsigned(data, offset, width, value):
    data[offset : offset + width] = value.to_bytes(width, "big")


def _sum16(data, start, end):
    total = 0
    for offset in range(start, end, 2):
        total = (
            total + _read_unsigned(data, offset, 2)
        ) & 0xFFFF
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


def stored_values(image):
    """Read all six stored checksum references."""
    data = _validated_data(image)
    return ChecksumValues(
        sum16_a=_read_unsigned(data, SUM16_A_FIELD, 2),
        sum16_b=_read_unsigned(data, SUM16_B_FIELD, 2),
        runtime_a_xor=_read_unsigned(data, RUNTIME_A_XOR_FIELD, 4),
        runtime_a_sum=_read_unsigned(data, RUNTIME_A_SUM_FIELD, 4),
        runtime_b_sum=_read_unsigned(data, RUNTIME_B_SUM_FIELD, 4),
        runtime_b_xor=_read_unsigned(data, RUNTIME_B_XOR_FIELD, 4),
    )


def calculate_values(image):
    """Calculate all six references from the currently stored image."""
    data = _validated_data(image)
    runtime_a_xor, runtime_a_sum = _runtime32(
        data,
        RUNTIME_A_START,
        RUNTIME_A_END,
        RUNTIME_A_EXCLUSIONS,
    )
    runtime_b_xor, runtime_b_sum = _runtime32(
        data,
        RUNTIME_B_START,
        RUNTIME_B_END,
    )
    return ChecksumValues(
        sum16_a=_sum16(data, SUM16_A_START, SUM16_A_END),
        sum16_b=_sum16(data, SUM16_B_START, SUM16_B_END),
        runtime_a_xor=runtime_a_xor,
        runtime_a_sum=runtime_a_sum,
        runtime_b_sum=runtime_b_sum,
        runtime_b_xor=runtime_b_xor,
    )


def verify(image):
    """Return stored and calculated values without mutating the image."""
    data = _validated_data(image)
    return ChecksumVerification(
        stored=stored_values(data),
        calculated=calculate_values(data),
    )


def require_valid(image, context="JK08A image"):
    """Return verification or raise with every mismatched field."""
    result = verify(image)
    if result.valid:
        return result
    details = ", ".join(
        f"{name}=stored:{getattr(result.stored, name):#x}"
        f"/calculated:{getattr(result.calculated, name):#x}"
        for name in result.mismatches
    )
    raise ChecksumError(f"{context}: checksum mismatch: {details}")


def recalculate(image):
    """Return a self-consistent image using the documented dependency order."""
    data = bytearray(_validated_data(image))

    runtime_b_xor, runtime_b_sum = _runtime32(
        data,
        RUNTIME_B_START,
        RUNTIME_B_END,
    )
    _write_unsigned(data, RUNTIME_B_SUM_FIELD, 4, runtime_b_sum)
    _write_unsigned(data, RUNTIME_B_XOR_FIELD, 4, runtime_b_xor)

    runtime_a_xor, runtime_a_sum = _runtime32(
        data,
        RUNTIME_A_START,
        RUNTIME_A_END,
        RUNTIME_A_EXCLUSIONS,
    )
    _write_unsigned(data, RUNTIME_A_XOR_FIELD, 4, runtime_a_xor)
    _write_unsigned(data, RUNTIME_A_SUM_FIELD, 4, runtime_a_sum)

    _write_unsigned(
        data,
        SUM16_A_FIELD,
        2,
        _sum16(data, SUM16_A_START, SUM16_A_END),
    )
    _write_unsigned(
        data,
        SUM16_B_FIELD,
        2,
        _sum16(data, SUM16_B_START, SUM16_B_END),
    )

    result = bytes(data)
    require_valid(result, "recalculated JK08A image")
    return result


def checksum_byte_offsets():
    """Return the complete set of bytes owned by checksum references."""
    return frozenset(
        offset
        for _name, start, width in CHECKSUM_FIELDS
        for offset in range(start, start + width)
    )
