#!/usr/bin/env python3
"""Project the canonical DTC disable registry onto other exact ROM images.

Each image stores its diagnostic descriptors as a table of twelve-byte records
followed immediately by one 32-bit attribute pointer per record. The pointer
table is the ECU's own attribute reference: on JK08A it reproduces all
independently established attribute addresses exactly. A target binding is
therefore read out of the target image rather than inferred from an offset.

A canonical record is carried to a target only when exactly one target record is
byte-identical to it. Byte identity fixes the group, the sub-index, the monitor
class, the code and the trailing flag together, so a partial match cannot be
mistaken for the same monitor.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
import re
import struct
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.mapkit import rom as romkit

DEFS = ROOT / "defs"
SOURCE_ROM = "JK08A"
PROJECTED_ROMS = ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B", "1ME3B")
INHERITED_ROMS = ("JK00A", "JK03A", "JK03B")
FIELDS = ("index", "dtc", "record_addr", "attribute_addr", "stock_attribute",
          "disabled_attribute", "group", "confidence", "note")
SOURCE_FIELDS = FIELDS + ("evidence",)
LAYOUTS = Path("refs/diagnostics/rom-dtc/layouts.toml")
ROM_BYTES = re.compile(r"rom_const:([0-9a-f]{8})=((?:0x)?[0-9a-f]+)")
RECORD_SIZE = 12
POINTER_SIZE = 4
SEARCH_START = 0x18000
SEARCH_END = 0x22000
MIN_RECORDS = 50
DISABLED_ATTRIBUTE = "0000"


class DtcProjectionError(Exception):
    """Raised when an image or a tracked projection fails its contract."""


@dataclass(frozen=True)
class DescriptorTables:
    """Located descriptor records and the attribute pointer table behind them."""

    start: int
    count: int
    pointer_base: int

    def record(self, data, index):
        offset = self.start + RECORD_SIZE * index
        return data[offset:offset + RECORD_SIZE]

    def record_address(self, index):
        return self.start + RECORD_SIZE * index

    def attribute_pointer_address(self, index):
        return self.pointer_base + POINTER_SIZE * index

    def attribute_address(self, data, index):
        offset = self.attribute_pointer_address(index)
        return struct.unpack(">I", data[offset:offset + POINTER_SIZE])[0]


def canonical_tables(root=ROOT):
    """The canonical geometry of the SHA-locked diagnostic catalog decoder."""
    with (root / LAYOUTS).open("rb") as source:
        layouts = tomllib.load(source)["layout"]
    [layout] = [item for item in layouts if item["rom"] == SOURCE_ROM]
    if (layout["record_size"], layout["code_offset"],
            layout["pointer_size"], layout["attribute_size"]) != (RECORD_SIZE, 6, POINTER_SIZE, 2):
        raise DtcProjectionError(f"{SOURCE_ROM}: unsupported descriptor geometry")
    tables = DescriptorTables(layout["descriptor_start"], layout["count"], layout["pointer_start"])
    if (tables.start < 0 or tables.count <= 0
            or tables.pointer_base != tables.record_address(tables.count)):
        raise DtcProjectionError(f"{SOURCE_ROM}: invalid descriptor table bounds")
    return tables


def canonical_evidence(row, tables, image_size):
    """Three expected byte spans, bound to the row rather than drawn from an image."""
    try:
        index = int(row["index"], 10)
        record = int(row["record_addr"], 16)
        attribute = int(row["attribute_addr"], 16)
        stock = bytes.fromhex(row["stock_attribute"])
    except (KeyError, TypeError, ValueError) as error:
        raise DtcProjectionError("invalid index, address, or stock_attribute") from error
    if not 0 <= index < tables.count:
        raise DtcProjectionError(f"index {index} outside 0 to {tables.count - 1}")
    if record != tables.record_address(index):
        raise DtcProjectionError(f"record_addr {record:08x} does not name index {index}")
    if (tables.attribute_pointer_address(tables.count) > image_size
            or attribute % 2 or not 0 < attribute < image_size - 1):
        raise DtcProjectionError("descriptor tables or attribute address outside image bounds")
    if len(stock) != 2:
        raise DtcProjectionError("stock_attribute is not two bytes")
    parts = [ROM_BYTES.fullmatch(token.strip())
             for token in (row.get("evidence") or "").split(";")]
    if len(parts) != 3 or not all(parts):
        raise DtcProjectionError("evidence requires three rom_const:<address>=<hex-bytes> items")
    try:
        spans = [(int(part[1], 16), bytes.fromhex(part[2].removeprefix("0x"))) for part in parts]
    except ValueError as error:
        raise DtcProjectionError("evidence values are not whole hexadecimal bytes") from error
    expected = ((record, RECORD_SIZE), (tables.attribute_pointer_address(index), POINTER_SIZE),
                (attribute, 2))
    if sorted((address, len(data)) for address, data in spans) != sorted(expected):
        raise DtcProjectionError("evidence must cover the complete descriptor, pointer slot, and attribute")
    by_address = dict(spans)
    spans = [(address, by_address[address]) for address, _ in expected]
    if dtc_code(spans[0][1]) != row["dtc"]:
        raise DtcProjectionError(f"dtc {row['dtc']} differs from descriptor evidence")
    if int.from_bytes(spans[1][1], "big") != attribute:
        raise DtcProjectionError("attribute_addr differs from pointer-slot evidence")
    if spans[2][1] != stock:
        raise DtcProjectionError("stock_attribute differs from attribute evidence")
    return spans


def validate_canonical(rows, data, root=ROOT):
    """Reject inconsistent rows and bytes before projecting a canonical record."""
    tables = canonical_tables(root)
    seen = set()
    for row in rows:
        spans = canonical_evidence(row, tables, len(data))
        index = int(row["index"], 10)
        if index in seen:
            raise DtcProjectionError(f"{SOURCE_ROM}: duplicate index {index}")
        seen.add(index)
        for address, expected in spans:
            if data[address:address + len(expected)] != expected:
                raise DtcProjectionError(
                    f"{SOURCE_ROM} index {index}: bytes at {address:08x} differ from evidence"
                )
    return tables


def _is_record(chunk):
    return (
        len(chunk) == RECORD_SIZE
        and chunk[3:6] == b"\x00\x00\x00"
        and chunk[1] < 8
        and chunk[9:12] == b"\x00\x00\x00"
    )


def locate_tables(data):
    """Locate the longest ascending descriptor run and validate its pointers."""
    best = None
    cursor = SEARCH_START
    while cursor < min(len(data), SEARCH_END):
        if not _is_record(data[cursor:cursor + RECORD_SIZE]):
            cursor += 4
            continue
        group = -1
        end = cursor
        while _is_record(data[end:end + RECORD_SIZE]) and data[end] >= group:
            group = data[end]
            end += RECORD_SIZE
        if (end - cursor) // RECORD_SIZE > MIN_RECORDS and (
            best is None or end - cursor > best[1] - best[0]
        ):
            best = (cursor, end)
        cursor = max(end, cursor + 4)
    if best is None:
        raise DtcProjectionError("no descriptor table found")
    start, end = best
    while data[start:start + RECORD_SIZE] == b"\x00" * RECORD_SIZE:
        start += RECORD_SIZE
    count = (end - start) // RECORD_SIZE
    tables = DescriptorTables(start=start, count=count, pointer_base=end)
    for index in range(count):
        address = tables.attribute_address(data, index)
        if address % 2 or not 0 < address < len(data) - 1:
            raise DtcProjectionError(
                f"attribute pointer {index} is {address:#x}, "
                "which is not an aligned in-image address"
            )
    return tables


def dtc_code(record):
    """Decode the ISO 15031-6 packed code stored in bytes 6 and 7."""
    high, low = record[6], record[7]
    return (
        "PCBU"[high >> 6]
        + f"{(high >> 4) & 3}{high & 0xF:X}{low >> 4:X}{low & 0xF:X}"
    )


def read_registry(rom):
    path = DEFS / f"{rom}.dtc.csv"
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        header = tuple(reader.fieldnames or ())
        if header != FIELDS and not (rom == SOURCE_ROM and header == SOURCE_FIELDS):
            raise DtcProjectionError(f"{path.name}: unexpected header")
        return list(reader)


def project(target_rom, source_rows=None, source=None, target=None):
    """Return target registry rows carried from the canonical registry."""
    source_rows = read_registry(SOURCE_ROM) if source_rows is None else source_rows
    source = source if source is not None else romkit.load(SOURCE_ROM).data
    target = target if target is not None else romkit.load(target_rom).data
    source_tables = validate_canonical(source_rows, source)
    target_tables = locate_tables(target)
    target_records = {}
    for index in range(target_tables.count):
        target_records.setdefault(
            bytes(target_tables.record(target, index)), []
        ).append(index)

    rows, dropped = [], []
    for source_row in source_rows:
        source_index = int(source_row["index"], 10)
        record = bytes(source_tables.record(source, source_index))
        matches = target_records.get(record, [])
        if len(matches) != 1:
            dropped.append((source_row["dtc"], source_index, len(matches)))
            continue
        index = matches[0]
        attribute = target_tables.attribute_address(target, index)
        stock = target[attribute:attribute + 2]
        if len(stock) != 2:
            raise DtcProjectionError(
                f"{target_rom}: attribute {attribute:#x} extends beyond the image"
            )
        rows.append({
            "index": str(index),
            "dtc": source_row["dtc"],
            "record_addr": f"{target_tables.record_address(index):08x}",
            "attribute_addr": f"{attribute:08x}",
            "stock_attribute": stock.hex(),
            "disabled_attribute": DISABLED_ATTRIBUTE,
            "group": source_row["group"],
            "confidence": source_row["confidence"],
            "note": source_row["note"],
        })
    return rows, dropped


def write_registry(rom, rows):
    path = DEFS / f"{rom}.dtc.csv"
    with path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    return path


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("roms", nargs="*", default=list(PROJECTED_ROMS),
                        help="relocated ROMs to project (default: every one)")
    parser.add_argument("--write", action="store_true",
                        help="rewrite the tracked target registries")
    args = parser.parse_args(argv)

    source_rows = read_registry(SOURCE_ROM)
    source = romkit.load(SOURCE_ROM).data
    failures = []
    for rom in INHERITED_ROMS:
        rows, dropped = project(rom, source_rows=source_rows, source=source)
        inherited = [
            {field: row[field] for field in FIELDS} for row in source_rows
        ]
        if dropped or rows != inherited:
            failures.append(rom)
            print(f"{rom}: exact-code member does not reproduce the "
                  f"{SOURCE_ROM} registry")
        else:
            print(f"{rom}: reproduces the {SOURCE_ROM} registry; "
                  "no separate manifest is tracked")
    for rom in args.roms:
        rows, dropped = project(rom, source_rows=source_rows, source=source)
        if args.write:
            write_registry(rom, rows)
            state = "written"
        else:
            path = DEFS / f"{rom}.dtc.csv"
            state = "matches" if path.exists() and read_registry(rom) == rows \
                else "STALE"
            if state == "STALE":
                failures.append(rom)
        missing = ", ".join(
            f"{code} [{index}]" for code, index, _ in dropped
        ) or "none"
        print(f"{rom}: {len(rows)} codes {state}; absent from target: {missing}")
    if failures:
        print(f"status=FAIL; stale registries: {', '.join(failures)}")
        return 1
    print(f"status=PASS; projected {len(args.roms)} targets from {SOURCE_ROM}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
