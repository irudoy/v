#!/usr/bin/env python3
"""Extract complete DTC descriptor catalogs from configured stock ROMs."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from check_projection import check as check_projection
import tomllib
from pathlib import Path

from catalog import (
    CatalogError,
    REFS,
    ROM_IMAGES,
    ROOT,
    require_unique,
    sha256_file,
    sha256_text,
    write_csv,
    write_jsonl,
)


DEFAULT_LAYOUTS = REFS / "rom-dtc" / "layouts.toml"
DEFAULT_OUTPUT = REFS / "rom-dtc" / "rom_dtc_descriptors.csv"
DOCUMENT_FIELDS = (
    "id",
    "dataset_id",
    "filename",
    "title",
    "kind",
    "sha256",
    "applicability_status",
)
FIELDS = (
    "id",
    "dataset_id",
    "rom",
    "index",
    "record_addr",
    "record_hex",
    "dtc_raw",
    "code",
    "attribute_addr",
    "attribute_hex",
    "source_path",
    "source_sha256",
    "applicability_status",
    "source_fragment_id",
)


def decode_dtc(raw: int) -> str:
    """Decode the two-byte SAE J2012 packed DTC representation."""
    prefix = "PCBU"[(raw >> 14) & 0x3]
    first = (raw >> 12) & 0x3
    return f"{prefix}{first:X}{raw & 0x0FFF:03X}"


def rom_registry() -> dict[str, dict[str, str]]:
    path = ROM_IMAGES / "roms.csv"
    with path.open(newline="", encoding="utf-8") as source:
        rows = list(csv.DictReader(source))
    return {row["rom"]: row for row in rows if row["rom"]}


def load_layouts(path: Path) -> tuple[str, list[dict[str, object]]]:
    with path.open("rb") as source:
        raw = tomllib.load(source)
    dataset_id = str(raw.get("dataset_id", "")).strip()
    layouts = raw.get("layout", [])
    if not dataset_id or not isinstance(layouts, list) or not layouts:
        raise CatalogError(f"{path}: dataset_id and at least one [[layout]] are required")
    return dataset_id, layouts


def extract_one(
    layout: dict[str, object],
    dataset_id: str,
    registry: dict[str, dict[str, str]],
) -> list[dict[str, object]]:
    rom = str(layout["rom"])
    if rom not in registry:
        raise CatalogError(f"{rom}: absent from rom-images/roms.csv")
    registry_row = registry[rom]
    image_path = ROM_IMAGES / registry_row["path"]
    actual_sha = sha256_file(image_path)
    if actual_sha != registry_row["sha256"]:
        raise CatalogError(
            f"{image_path}: SHA-256 {actual_sha}, expected {registry_row['sha256']}"
        )
    data = image_path.read_bytes()

    start = int(layout["descriptor_start"])
    record_size = int(layout["record_size"])
    count = int(layout["count"])
    code_offset = int(layout["code_offset"])
    pointer_start = int(layout["pointer_start"])
    pointer_size = int(layout.get("pointer_size", 4))
    attribute_size = int(layout.get("attribute_size", 2))
    expected_unique = int(layout["expected_unique"])

    descriptor_end = start + record_size * count
    pointer_end = pointer_start + pointer_size * count
    if descriptor_end > len(data) or pointer_end > len(data):
        raise CatalogError(f"{rom}: configured table exceeds image size")
    if not 0 <= code_offset <= record_size - 2:
        raise CatalogError(f"{rom}: code_offset is outside a descriptor")

    rows = []
    for index in range(count):
        record_addr = start + index * record_size
        record = data[record_addr : record_addr + record_size]
        raw = int.from_bytes(record[code_offset : code_offset + 2], "big")
        code = decode_dtc(raw)
        pointer_addr = pointer_start + index * pointer_size
        attribute_addr = int.from_bytes(
            data[pointer_addr : pointer_addr + pointer_size], "big"
        )
        if attribute_addr + attribute_size > len(data):
            raise CatalogError(
                f"{rom}[{index}]: attribute pointer 0x{attribute_addr:08x} "
                "is outside the image"
            )
        attribute = data[attribute_addr : attribute_addr + attribute_size]
        rows.append(
            {
                "id": f"{rom.lower()}:{record_addr:08x}",
                "dataset_id": dataset_id,
                "rom": rom,
                "index": index,
                "record_addr": f"{record_addr:08x}",
                "record_hex": record.hex(),
                "dtc_raw": f"{raw:04x}",
                "code": code,
                "attribute_addr": f"{attribute_addr:08x}",
                "attribute_hex": attribute.hex(),
                "source_path": image_path.relative_to(ROOT).as_posix(),
                "source_sha256": actual_sha,
                "applicability_status": "silicon_catalog",
                "source_fragment_id": f"{rom.lower()}:{record_addr:08x}:source",
            }
        )

    unique = len({row["code"] for row in rows})
    if unique != expected_unique:
        raise CatalogError(
            f"{rom}: {unique} unique DTC codes, expected {expected_unique}"
        )
    return rows


def build(layout_path: Path = DEFAULT_LAYOUTS) -> list[dict[str, object]]:
    dataset_id, layouts = load_layouts(layout_path)
    registry = rom_registry()
    rows = []
    for layout in layouts:
        rows.extend(extract_one(layout, dataset_id, registry))
    require_unique(rows, ("id",))
    return sorted(rows, key=lambda row: (str(row["rom"]), int(row["index"])))


def source_projection(
    rows: list[dict[str, object]],
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    documents = []
    fragments = []
    seen_documents = set()
    for row in rows:
        rom = str(row["rom"])
        document_id = f"{row['dataset_id']}:rom-image:{rom.lower()}"
        if document_id not in seen_documents:
            seen_documents.add(document_id)
            documents.append(
                {
                    "id": document_id,
                    "dataset_id": row["dataset_id"],
                    "filename": row["source_path"],
                    "title": rom,
                    "kind": "rom_image",
                    "sha256": row["source_sha256"],
                    "applicability_status": "silicon_catalog",
                }
            )
        text = json.dumps(
            {
                "rom": rom,
                "descriptor_index": row["index"],
                "record_addr": row["record_addr"],
                "record_hex": row["record_hex"],
                "attribute_addr": row["attribute_addr"],
                "attribute_hex": row["attribute_hex"],
                "dtc": row["code"],
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        fragments.append(
            {
                "id": row["source_fragment_id"],
                "dataset_id": row["dataset_id"],
                "document_id": document_id,
                "kind": "rom_dtc_descriptor",
                "heading": f"{rom} descriptor {row['index']}",
                "rom": rom,
                "byte_start": row["record_addr"],
                "byte_length": 12,
                "attribute_addr": row["attribute_addr"],
                "dtc_codes": [row["code"]],
                "text_sha256": sha256_text(text),
                "text": text,
            }
        )
    require_unique(documents, ("id",))
    require_unique(fragments, ("id",))
    return documents, fragments


def write(output: Path, rows: list[dict[str, object]]) -> None:
    documents, fragments = source_projection(rows)
    write_csv(output, FIELDS, rows)
    write_csv(output.parent / "documents.csv", DOCUMENT_FIELDS, documents)
    write_jsonl(output.parent / "fragments.jsonl", fragments)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("--layouts", type=Path, default=DEFAULT_LAYOUTS)
    result.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    result.add_argument("--check", action="store_true", help="validate and byte-compare outputs without writing")
    return result


def main() -> int:
    args = parser().parse_args()
    try:
        rows = build(args.layouts)
        if args.check:
            check_projection(args.output.parent, rows,
                             lambda output, rows: write(output / args.output.name, rows))
    except (OSError, KeyError, CatalogError, tomllib.TOMLDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    by_rom: dict[str, list[dict[str, object]]] = {}
    for row in rows:
        by_rom.setdefault(str(row["rom"]), []).append(row)
    for rom, items in sorted(by_rom.items()):
        print(
            f"{rom}: descriptors={len(items)}, "
            f"unique_codes={len({item['code'] for item in items})}"
        )
    if not args.check:
        write(args.output, rows)
        try:
            shown = args.output.relative_to(ROOT)
        except ValueError:
            shown = args.output
        print(f"Wrote {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
