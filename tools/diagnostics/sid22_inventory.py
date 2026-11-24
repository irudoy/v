#!/usr/bin/env python3
"""Inventory the exact service-0x22 publication tables.

The output is deliberately semantic-free.  It records only behavior established
by the SHA-locked ROM images and their publishers: declared DIDs, response
widths, and the byte sources available to each response.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, replace
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
    conditional_dids=(0x1401, 0x1402),
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
VQ37_1ME3B = InventoryLayout(
    "1ME3B",
    ROOT / "rom-images" / "23710-1ME3B" / "11ME3B-20260825-stock.bin",
    0x180000,
    "f905b78901b4ca96002a31c2fca8f1cd00dee57b02bea1921a341caa6db2a6f3",
    0x0003B008,
    0x0003B5EC,
    "7761b0b2ba31714d3ee5479d96e324cd7850508528fe54c7de1245705139d087",
    (
        Family(
            0x11, 0x00022AE4, 0x00022CE4, 4, 1, (0x00, 0x20, 0x40, 0x60), False,
            "807df3b54a2df9183f705bb1e03bd466de41ed05ac57722385663b9c2735f525",
        ),
        Family(
            0x12, 0x00022CE4, 0x00022E60, 4, 2, (0x00, 0x20, 0x40), False,
            "12f147db0c11810d5cf47714180057c88f2ba7f0fef24caeeb57a2423a3ccfd7",
        ),
        # The 0x18 index check extends into the adjacent 0x14 table.
        Family(
            0x13, 0x00022E60, 0x00022F08, 8, 2, (0x00,), True,
            "1bc55f12f5832847a1a9be9cd8c622a7d6448ed3826e1ddfc47aa6973c4c1ae8",
        ),
        Family(
            0x14, 0x00022F08, 0x00022F8C, 4, 1, (0x00, 0x20), False,
            "d6c89237c0efaaf5d0f50ef14cee73a9f60fc68a56ad6ffb759c9a05359143c4",
        ),
        Family(
            0x15, 0x00022F8C, 0x0002304C, 8, 2, (0x00,), True,
            "2e10bf3d0fb50ec9080010439459ead24931c54ca8e914e96f079eca1d43900d",
        ),
        Family(
            0x16, 0x00023050, 0x00023150, 4, 1, (0x00, 0x20), True,
            "d3e10c4d230b0bc146c5fdc936b66f21ab7349ae86a130bbc40c248b60f14dd4",
        ),
    ),
    # The publisher returns zero when all 0xF0 bits at 0xFFFED89C are clear.
    conditional_dids=(0x1401, 0x1402),
)
VQ37_1ND0A = InventoryLayout(
    "1ND0A",
    ROOT / "rom-images" / "23710-1ND0A" / "11ND0A-20260715-stock.bin",
    0x180000,
    "650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978",
    0x00037FF8,
    0x000385DC,
    "86ae4dc751fb2b43736c70df09466fe55b30dda24c5b7af173281afeb721761b",
    (
        Family(
            0x11, 0x00022A70, 0x00022C70, 4, 1, (0x00, 0x20, 0x40, 0x60), False,
            "c8babc7fad1962fdf68844e6973ea1a6837f260ebbffbacab0882711023f253b",
        ),
        Family(
            0x12, 0x00022C70, 0x00022DEC, 4, 2, (0x00, 0x20, 0x40), False,
            "2b9f8a671c37df345e8b8d536b7386764780a90c7986ea7513bfd978295573b9",
        ),
        Family(
            0x13, 0x00022DEC, 0x00022E94, 8, 2, (0x00,), True,
            "79f168e8d1930cfd3cfc89e789bb045ca88c63ea4692fa4c62e67793d7cc10ab",
        ),
        Family(
            0x14, 0x00022E94, 0x00022F18, 4, 1, (0x00, 0x20), False,
            "fa1adf8352ced1b5500817609e15d42b92f0680898ce593a59689ad7840fcdcb",
        ),
        Family(
            0x15, 0x00022F18, 0x00022FD8, 8, 2, (0x00,), True,
            "8eef2fd8625f1e5ed6d41cf45963492d44e231869951298e3b7b8665a7e0ca3e",
        ),
        Family(
            0x16, 0x00022FDC, 0x000230DC, 4, 1, (0x00, 0x20), True,
            "26946ca726f33c0d42ae3f5b6e27e0a12149a1e71c368626619695ddcea94453",
        ),
    ),
    conditional_dids=(0x1401, 0x1402),
)
VQ37_1ND3B = replace(
    VQ37_1ND0A,
    rom="1ND3B",
    path=ROOT / "rom-images" / "23710-1ND3B" / "11ND3B-20260715-stock.bin",
    sha256="0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e",
)
SH7058_JK00C = InventoryLayout(
    "JK00C",
    ROOT / "rom-images" / "23710-JK00C" / "1JK00C-20260803-stock.bin",
    0x100000,
    "b287ef26373cd6d06a0b9f206648e9b8890a2a5b6cde982bb9d918d77eb69289",
    0x00032F9C,
    0x00033500,
    "708e0b46e798019760d8971baa8fbf2b08ebe4a1f8843a49d238c2b02bfeeb29",
    (
        Family(
            0x11, 0x00022738, 0x00022938, 4, 1, (0x00, 0x20, 0x40, 0x60), False,
            "dbcf8012d318274eee74a3687facc90b2745041e509b0a1c0e3d67092d6fc6dd",
        ),
        Family(
            0x12, 0x00022938, 0x00022AB4, 4, 2, (0x00, 0x20, 0x40), False,
            "37d9ee17fa3c79974827908c93b79122104059ee5b75df5438862aaf43ec6617",
        ),
        Family(
            0x13, 0x00022AB4, 0x00022B5C, 8, 2, (0x00,), True,
            "c1cd4988fea1d69859f7d9595e062f00f0416bc082727d5c5c042401b944639c",
        ),
        Family(
            0x14, 0x00022B5C, 0x00022BE0, 4, 1, (0x00, 0x20), False,
            "8e9260b320a21308018dec4ada1a6b2a540fb42a5cf72242b9b853133d849823",
        ),
        Family(
            0x15, 0x00022BE0, 0x00022CA0, 8, 2, (0x00,), True,
            "82d6e82daba276f29327154721283bcde8967ed43ad26eec112961be04d43685",
        ),
        Family(
            0x16, 0x00022CA4, 0x00022DA4, 4, 1, (0x00, 0x20), True,
            "36f126b86d0dce4834ae752562f5039d483dd68bf50d8b7fe2515eca66fea1ca",
        ),
    ),
    conditional_dids=(0x1401, 0x1402),
)
SH7058_JK00D = replace(
    SH7058_JK00C,
    rom="JK00D",
    path=ROOT / "rom-images" / "23710-JK00D" / "1JK00D-20260726-stock.bin",
    sha256="e2d7a374b4f7cb42d1963e7aeea424f2147ef01afd231f31b599d83f87f315d3",
    publisher_sha256="08723ba831d1f9d6625c3898bb677e9950aeb0a25ce3e0e0817c4f5b45d0164e",
    families=tuple(
        replace(family, table_sha256=digest)
        for family, digest in zip(
            SH7058_JK00C.families,
            (
                "25aa0499e9d6087f63823dcd28b9106d269cd1aef2cc7d390f1720de03ef7d98",
                "2260185adcd7e7f1899220149e45d248b2b02ee5fca3f86a7e5a0ad6eb2f4a4c",
                "7d47d82d49605838388e2e41ead2e6987cee213edfa337e4f60663aed8153a12",
                "91b33cec248f8f6a57da16d27dbaf3080f5af1d14e8e62979249c4f107d12ad1",
                "a7234a9677c26ec0aa04c202fecac537d496d7429dc05fb2f198a97d42b0dbc2",
                "e46d4dfeedd566016b085dc3752ee226d6106a9a9f08ec874f65456e8ce02d15",
            ),
            strict=True,
        )
    ),
)
SH7058_JK78C = InventoryLayout(
    "JK78C",
    ROOT / "rom-images" / "23710-JK78C" / "1JK78C-20260715-stock.bin",
    0x100000,
    "86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d",
    0x00035B80,
    0x000360E4,
    "aa08ebd04b01076650fe0b10d5a4d831b7d134349b83072d170993433b879d88",
    (
        Family(
            0x11, 0x00022718, 0x00022918, 4, 1, (0x00, 0x20, 0x40, 0x60), False,
            "cc5304bd0bcd6094585b6336b6f36656215bc18ef7897f03914ed9a827ca3290",
        ),
        Family(
            0x12, 0x00022918, 0x00022A94, 4, 2, (0x00, 0x20, 0x40), False,
            "6cb36f13e53e2822167a46d81292fd673a91f76c89028c5548f0ef77eb3735dd",
        ),
        Family(
            0x13, 0x00022A94, 0x00022B3C, 8, 2, (0x00,), True,
            "d0bce5fc392adf2e61f498db00a441003cb94f3b7f80057baa3abf696c01189f",
        ),
        Family(
            0x14, 0x00022B3C, 0x00022BC0, 4, 1, (0x00, 0x20), False,
            "e95ecc07d3697278a167db3cce5a325faa1e3e89cf56a64c590441c18f097bfd",
        ),
        Family(
            0x15, 0x00022BC0, 0x00022C80, 8, 2, (0x00,), True,
            "4a58254d9715e87a54e796002de412ecc9cfcee63b3dc6cb46b9325c191b4c39",
        ),
        Family(
            0x16, 0x00022C84, 0x00022D84, 4, 1, (0x00, 0x20), True,
            "51a423a289d8e79c05a6990b696cd4af7777965c42e136973f8c39d0b44b3211",
        ),
    ),
    conditional_dids=(0x1401, 0x1402),
)
LAYOUTS = {
    layout.rom: layout
    for layout in (
        JK08A, VQ37_1EK7A, VQ37_1ME3B, VQ37_1ND0A, VQ37_1ND3B,
        SH7058_JK00C, SH7058_JK00D, SH7058_JK78C,
    )
}


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
