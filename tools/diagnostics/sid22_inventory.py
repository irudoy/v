#!/usr/bin/env python3
"""Inventory the exact service-0x22 publication tables.

The output is deliberately semantic-free.  It records only behavior established
by the SHA-locked ROM images and their publishers: declared DIDs, response
widths, and the byte sources available to each response.
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
class InventoryLayout:
    rom: str
    path: Path
    size: int
    sha256: str
    publisher_start: int
    publisher_end: int
    publisher_sha256: str
    families: tuple[Family, ...]
    conditional_dids: tuple[int, ...] = ()


JK08A = InventoryLayout(
    "JK08A", DEFAULT_ROM, ROM_SIZE, ROM_SHA256,
    PUBLISHER_ADDRESS, PUBLISHER_ADDRESS + PUBLISHER_SIZE, PUBLISHER_SHA256,
    FAMILIES,
)
VQ37_1EK7A = InventoryLayout(
    "1EK7A",
    ROOT / "rom-images" / "23710-1EK7A" / "11EK7A-20261122-stock.bin",
    0x180000,
    "b66734ed04238b150d44fc3b1307f99e65b5eebf24bd14110a46ac27adeef5e6",
    0x0003BF98,
    0x0003C57C,
    "71a021b7cff17d6e9b81ff6b5df5f01db538c11ddacd43b873874b9aad897662",
    (
        Family(
            0x11, 0x00022B78, 0x00022D78, 4, 1, (0x00, 0x20, 0x40, 0x60), False,
            "bcab2f6f3e87dfb691d2e862c0859aff4b4336b0fb9ebbec0914752d765e2d9e",
        ),
        Family(
            0x12, 0x00022D78, 0x00022EF4, 4, 2, (0x00, 0x20, 0x40), False,
            "eecf692e5c9f5d5efed3dcfc983d0bc568951746babadc8ff708db803521b049",
        ),
        # The 0x18 index check extends into the adjacent 0x14 table.
        Family(
            0x13, 0x00022EF4, 0x00022F9C, 8, 2, (0x00,), True,
            "e0107e3f0142326a5ac1dc2837740bc18539cb92695a396bbf7cdb67b6165b98",
        ),
        Family(
            0x14, 0x00022F9C, 0x00023020, 4, 1, (0x00, 0x20), False,
            "24c50f3b65bc10c062edaa2cd4056a47ace8340892d14a6f0b305a3bd42f6c8c",
        ),
        Family(
            0x15, 0x00023020, 0x000230E0, 8, 2, (0x00,), True,
            "03a0adb613e5963b46e572f56bbe96861f4a15d42219e345ed89d07ed41c3391",
        ),
        Family(
            0x16, 0x000230E4, 0x000231E4, 4, 1, (0x00, 0x20), True,
            "194e29775d7567d7120cbd3c243855debf79f357658c1dd21e2daaa261ac0164",
        ),
    ),
    # The publisher returns zero when all 0x78 bits at 0xFFFEDED5 are clear.
    conditional_dids=(0x1401, 0x1402),
)
LAYOUTS = {layout.rom: layout for layout in (JK08A, VQ37_1EK7A)}


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


def load_exact_rom(path: Path | None = None, *, layout: InventoryLayout = JK08A) -> bytes:
    path = layout.path if path is None else Path(path)
    try:
        data = path.read_bytes()
    except OSError as error:
        raise InventoryError(f"ROM image not found: {path}") from error
    if len(data) != layout.size:
        raise InventoryError(
            f"{path}: expected {layout.size} bytes, found {len(data)}"
        )
    digest = _sha256(data)
    if digest != layout.sha256:
        raise InventoryError(
            f"{path}: expected {layout.rom} SHA-256 {layout.sha256}, found {digest}"
        )
    publisher = data[layout.publisher_start : layout.publisher_end]
    if _sha256(publisher) != layout.publisher_sha256:
        raise InventoryError(f"service-0x22 publisher bytes do not match {layout.rom}")
    for family in layout.families:
        table = data[family.table_start : family.table_end]
        if _sha256(table) != family.table_sha256:
            raise InventoryError(
                f"family 0x{family.high_byte:02X} table bytes do not match {layout.rom}"
            )
    return data


def _words(data: bytes, address: int, count: int) -> tuple[int, ...]:
    return struct.unpack_from(">" + "I" * count, data, address)


def build_inventory(data: bytes, *, layout: InventoryLayout = JK08A) -> tuple[Entry, ...]:
    if len(data) != layout.size:
        raise InventoryError(f"expected {layout.size} ROM bytes, found {len(data)}")
    entries = []
    for family in layout.families:
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
                        "conditional" if did in layout.conditional_dids else "single",
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


def read_inventory(
    path: Path | None = None, *, layout: InventoryLayout = JK08A
) -> tuple[Entry, ...]:
    return build_inventory(load_exact_rom(path, layout=layout), layout=layout)


def _write_csv(entries: tuple[Entry, ...]) -> None:
    rows = [entry.as_dict() for entry in entries]
    writer = csv.DictWriter(sys.stdout, fieldnames=tuple(rows[0]))
    writer.writeheader()
    writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inventory exact service-0x22 response sources"
    )
    parser.add_argument("--layout", choices=LAYOUTS, default=JK08A.rom)
    parser.add_argument("--rom", type=Path)
    parser.add_argument("--format", choices=("csv", "json"), default="csv")
    args = parser.parse_args(argv)
    try:
        entries = read_inventory(args.rom, layout=LAYOUTS[args.layout])
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
