#!/usr/bin/env python3
"""Inventory the exact JK08A service-0x22 publication tables.

The output is deliberately semantic-free.  It records only behavior established
by the SHA-locked ROM image and publisher at 0x0003235C: declared DIDs, response
widths, and the byte sources dereferenced for each response.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import struct
import sys


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ROM = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)
ROM_SHA256 = "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23"
ROM_SIZE = 0x100000
PUBLISHER_ADDRESS = 0x0003235C
PUBLISHER_BODY_RANGES = (
    (0x0003235C, 0x00032474),
    (0x00032484, 0x00032578),
    (0x000325A8, 0x0003270E),
    (0x00032712, 0x00032834),
    (0x00032864, 0x000328B8),
)
# The contiguous backing includes every body range and PC-relative pool.
PUBLISHER_SIZE = 0x000328C0 - PUBLISHER_ADDRESS
PUBLISHER_SHA256 = (
    "21589cdc96127a922d7f81f9305f49779718749aede97d8cbc915c5101598986"
)


class InventoryError(ValueError):
    pass


@dataclass(frozen=True)
class Family:
    high_byte: int
    table_start: int
    table_end: int
    stride: int
    default_width: int
    sequential_width_lows: tuple[int, ...]
    bounded_in_publisher: bool
    table_sha256: str

    @property
    def record_count(self) -> int:
        size = self.table_end - self.table_start
        if size <= 0 or size % self.stride:
            raise InventoryError(
                f"family 0x{self.high_byte:02X} has an invalid table extent"
            )
        return size // self.stride


FAMILIES = (
    Family(
        0x11,
        0x000226AC,
        0x0002289C,
        4,
        1,
        (0x00, 0x20, 0x40, 0x60),
        False,
        "62b8faefae6c8fe0215d39182f4dc1b8a3e89ff543c32a827dc2f824997a46ab",
    ),
    Family(
        0x12,
        0x0002289C,
        0x000229E0,
        4,
        2,
        (0x00, 0x20, 0x40),
        False,
        "a34f7cacef6d860458d79e2b37dbe2408420f3278ee94169f50b492f3424e7bc",
    ),
    Family(
        0x13,
        0x000229E0,
        0x00022A88,
        8,
        2,
        (0x00,),
        True,
        "f1cb955cc44ac3df8636351958968cf73d132f6189c73ed0af82e085af44b8de",
    ),
    Family(
        0x14,
        0x00022A88,
        0x00022B0C,
        4,
        1,
        (0x00, 0x20),
        False,
        "828101e79d7a14734a198fa0686383948f3dd088b4ebf5e84a500dee9f9aaf1c",
    ),
    Family(
        0x15,
        0x00022B0C,
        0x00022BAC,
        8,
        2,
        (0x00,),
        True,
        "9e3a0279c73e0dc9e22ba65c254abacb75e8de09f473358bf47d8be58be8c393",
    ),
    Family(
        0x16,
        0x00022BB0,
        0x00022CB0,
        4,
        1,
        (0x00, 0x20),
        True,
        "4d488d917abab28e4271484b0f0a2ab81462e090e0889268330f380953b3c696",
    ),
)


@dataclass(frozen=True)
class Entry:
    did: int
    width: int
    record_address: int
    sources: tuple[int, ...]
    source_layout: str
    bounded_in_publisher: bool

    def as_dict(self) -> dict[str, object]:
        return {
            "did": f"0x{self.did:04X}",
            "width": self.width,
            "record_address": f"0x{self.record_address:08X}",
            "source_0": f"0x{self.sources[0]:08X}" if self.sources else "",
            "source_1": (
                f"0x{self.sources[1]:08X}" if len(self.sources) > 1 else ""
            ),
            "source_layout": self.source_layout,
            "bounded_in_publisher": self.bounded_in_publisher,
        }


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_exact_rom(path: Path = DEFAULT_ROM) -> bytes:
    path = Path(path)
    try:
        data = path.read_bytes()
    except OSError as error:
        raise InventoryError(f"ROM image not found: {path}") from error
    if len(data) != ROM_SIZE:
        raise InventoryError(
            f"{path}: expected {ROM_SIZE} bytes, found {len(data)}"
        )
    digest = _sha256(data)
    if digest != ROM_SHA256:
        raise InventoryError(
            f"{path}: expected JK08A SHA-256 {ROM_SHA256}, found {digest}"
        )
    publisher = data[PUBLISHER_ADDRESS : PUBLISHER_ADDRESS + PUBLISHER_SIZE]
    if _sha256(publisher) != PUBLISHER_SHA256:
        raise InventoryError("service-0x22 publisher bytes do not match JK08A")
    for family in FAMILIES:
        table = data[family.table_start : family.table_end]
        if _sha256(table) != family.table_sha256:
            raise InventoryError(
                f"family 0x{family.high_byte:02X} table bytes do not match JK08A"
            )
    return data


def _words(data: bytes, address: int, count: int) -> tuple[int, ...]:
    return struct.unpack_from(">" + "I" * count, data, address)


def build_inventory(data: bytes) -> tuple[Entry, ...]:
    if len(data) != ROM_SIZE:
        raise InventoryError(f"expected {ROM_SIZE} ROM bytes, found {len(data)}")
    entries = []
    for family in FAMILIES:
        words_per_record = family.stride // 4
        for low_byte in range(family.record_count):
            record_address = family.table_start + low_byte * family.stride
            pointers = _words(data, record_address, words_per_record)
            did = family.high_byte << 8 | low_byte

            # DID 0x120B is built by a dedicated two-byte publisher branch.  Its
            # pointer slot remains 0xFFFFFFFF and must not be treated as absent.
            if did == 0x120B:
                if pointers[0] != 0xFFFFFFFF:
                    raise InventoryError("DID 0x120B no longer has its sentinel slot")
                entries.append(
                    Entry(
                        did,
                        2,
                        record_address,
                        (),
                        "dynamic",
                        family.bounded_in_publisher,
                    )
                )
                continue

            if pointers[0] == 0xFFFFFFFF:
                continue
            if low_byte in family.sequential_width_lows:
                entries.append(
                    Entry(
                        did,
                        4,
                        record_address,
                        (pointers[0],),
                        "sequential",
                        family.bounded_in_publisher,
                    )
                )
                continue
            if family.default_width == 1:
                entries.append(
                    Entry(
                        did,
                        1,
                        record_address,
                        (pointers[0],),
                        "single",
                        family.bounded_in_publisher,
                    )
                )
                continue
            if len(pointers) == 1:
                entries.append(
                    Entry(
                        did,
                        2,
                        record_address,
                        (pointers[0],),
                        "sequential",
                        family.bounded_in_publisher,
                    )
                )
                continue
            if pointers[1] == 0xFFFFFFFF:
                raise InventoryError(f"DID 0x{did:04X} has no second byte source")
            entries.append(
                Entry(
                    did,
                    2,
                    record_address,
                    pointers[:2],
                    "paired",
                    family.bounded_in_publisher,
                )
            )
    return tuple(entries)


def read_inventory(path: Path = DEFAULT_ROM) -> tuple[Entry, ...]:
    return build_inventory(load_exact_rom(path))


def _write_csv(entries: tuple[Entry, ...]) -> None:
    rows = [entry.as_dict() for entry in entries]
    writer = csv.DictWriter(sys.stdout, fieldnames=tuple(rows[0]))
    writer.writeheader()
    writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inventory exact JK08A service-0x22 response sources"
    )
    parser.add_argument("--rom", type=Path, default=DEFAULT_ROM)
    parser.add_argument("--format", choices=("csv", "json"), default="csv")
    args = parser.parse_args(argv)
    try:
        entries = read_inventory(args.rom)
    except InventoryError as error:
        parser.error(str(error))
    if args.format == "json":
        json.dump([entry.as_dict() for entry in entries], sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        _write_csv(entries)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
