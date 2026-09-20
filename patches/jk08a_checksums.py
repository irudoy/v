#!/usr/bin/env python3
"""Compatibility API for the exact 7MFKAVN86 checksum layout."""

from __future__ import annotations

from patches import rom_checksums


LAYOUT = rom_checksums.layout_for_rom("JK08A")

ROM_SIZE = LAYOUT.rom_size

SUM16_A_FIELD = LAYOUT.sum16_a_field
SUM16_A_START = LAYOUT.sum16_a_start
SUM16_A_END = LAYOUT.sum16_a_end

RUNTIME_A_START = LAYOUT.runtime_a_start
RUNTIME_A_END = LAYOUT.runtime_a_end
RUNTIME_A_XOR_FIELD = LAYOUT.runtime_a_xor_field
RUNTIME_A_SUM_FIELD = LAYOUT.runtime_a_sum_field
RUNTIME_A_EXCLUSIONS = LAYOUT.runtime_a_exclusions

SUM16_B_FIELD = LAYOUT.sum16_b_field
SUM16_B_START = LAYOUT.sum16_b_start
SUM16_B_END = LAYOUT.sum16_b_end

RUNTIME_B_SUM_FIELD = LAYOUT.runtime_b_sum_field
RUNTIME_B_XOR_FIELD = LAYOUT.runtime_b_xor_field
RUNTIME_B_START = LAYOUT.runtime_b_start
RUNTIME_B_END = LAYOUT.runtime_b_end

CHECKSUM_FIELDS = LAYOUT.checksum_fields


ChecksumError = rom_checksums.ChecksumError
ChecksumValues = rom_checksums.ChecksumValues
ChecksumVerification = rom_checksums.ChecksumVerification


def verify(image):
    """Return stored and calculated values without mutating the image."""
    return rom_checksums.verify(image, LAYOUT)


def require_valid(image, context="JK08A image"):
    """Return verification or raise with every mismatched field."""
    return rom_checksums.require_valid(image, LAYOUT, context)


def recalculate(image):
    """Return a self-consistent image using the documented dependency order."""
    return rom_checksums.recalculate(image, LAYOUT)


def checksum_byte_offsets():
    """Return the complete set of bytes owned by checksum references."""
    return rom_checksums.checksum_byte_offsets(LAYOUT)
