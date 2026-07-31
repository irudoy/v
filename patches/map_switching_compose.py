#!/usr/bin/env python3
"""Compose and validate a JK08A map-switching fixture in memory.

The default input is the exact stock ROM selected by the authoritative layout.
Callers may explicitly select the compatible-input policy for a calibrated
JK08A image that retains the exact protected code partition and patch anchors.
The tool applies calibration copies, pointer tables, hook literals, and all
SHA-locked Ghidra assembly units, then verifies the complete byte result
against the declared write set.

There is intentionally no output-file option. Stored checksum fields remain
unchanged, so the resulting bytes are a non-flashable verification fixture.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from itertools import chain
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_layout as layout_model
from patches import map_switching_assembly as assembly_model


@dataclass(frozen=True)
class Composition:
    data: bytes
    sha256: str
    changed_bytes: int
    permitted_write_bytes: int
    instruction_count: int
    code_entry_count: int
    checksums_recalculated: bool = False


def composition_write_ranges(layout):
    """Return the complete, non-overlapping ROM write set."""
    ranges = [
        layout_model.AddressRange(
            unit.span.start,
            unit.span.end,
            f"assembly.{unit.key}",
        )
        for unit in layout.assembly_units
    ]
    for family in layout.families:
        ranges.extend(
            layout_model.AddressRange(
                address,
                address + family.byte_length,
                f"{family.key}.map_{slot}",
            )
            for slot, address in enumerate(family.copies, 2)
        )
        ranges.append(
            layout_model.AddressRange(
                family.pointer_table,
                family.pointer_table + layout.pointer_table_size,
                f"{family.key}.pointer_table",
            )
        )
    ranges.extend(
        layout_model.AddressRange(
            hook.address,
            hook.address + hook.width,
            f"hook.{hook.key}",
        )
        for hook in layout.hooks
    )
    ranges.sort(key=lambda item: (item.start, item.end, item.key))
    for left, right in zip(ranges, ranges[1:]):
        if left.overlaps(right):
            raise ValueError(
                f"composition writes overlap: {left.key} and {right.key}"
            )
    return tuple(ranges)


def _validated_blobs(layout, blobs):
    expected = set(layout.assembly_unit_by_key)
    actual = set(blobs)
    missing = expected - actual
    extra = actual - expected
    if missing or extra:
        raise ValueError(
            "assembly blob set differs"
            f"; missing={sorted(missing)}"
            f"; extra={sorted(extra)}"
        )
    return {
        unit.key: layout_model.validate_assembled_blob(
            unit, blobs[unit.key]
        )
        for unit in layout.assembly_units
    }


def _validate_source(layout, image, source_policy):
    if source_policy == "exact":
        return layout_model.validate_image(layout, image)
    if source_policy == "compatible":
        return layout_model.validate_compatible_image(layout, image)
    raise ValueError(
        f"unsupported source policy {source_policy!r}; "
        "expected 'exact' or 'compatible'"
    )


def _build_expected(layout, image, blobs, source_policy):
    data = bytearray(
        layout_model.materialize_calibration_copies(
            layout, image, source_policy=source_policy
        )
    )
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = (
            hook.replacement.to_bytes(hook.width, layout.byte_order)
        )
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = blobs[unit.key]
    return bytes(data)


def _validate_write_set(stock, composed, ranges):
    permitted = set(
        chain.from_iterable(range(region.start, region.end) for region in ranges)
    )
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(stock, composed))
        if before != after
    }
    outside = changed - permitted
    if outside:
        first = min(outside)
        raise ValueError(
            f"composed image changes undeclared byte at {first:#x}"
        )
    return len(changed), len(permitted)


def _validate_instruction_placement(layout, composed, blobs):
    parsed_by_unit = assembly_model.validate_assembly_sources(layout)
    instruction_count = 0
    code_entries = set()
    for unit in layout.assembly_units:
        parsed = parsed_by_unit[unit.key]
        instruction_addresses = {
            statement.address
            for statement in parsed.statements
            if statement.kind == "instruction"
        }
        for statement in parsed.statements:
            if statement.kind != "instruction":
                continue
            offset = statement.address - unit.span.start
            expected = blobs[unit.key][offset : offset + statement.size]
            actual = composed[
                statement.address : statement.address + statement.size
            ]
            if actual != expected:
                raise ValueError(
                    f"{unit.key}: instruction bytes differ at "
                    f"{statement.address:#x}"
                )
            instruction_count += 1
        for key in unit.code_regions:
            entry = layout.code_region_by_key[key].entry
            if entry not in instruction_addresses:
                raise ValueError(
                    f"{unit.key}: code entry {key} at {entry:#x} "
                    "is not an instruction"
                )
            code_entries.add(entry)
    if instruction_count != layout.assembled_instruction_count:
        raise ValueError(
            f"composed instruction count is {instruction_count}, expected "
            f"{layout.assembled_instruction_count}"
        )
    return instruction_count, len(code_entries)


def _validate_composed_contract(
    layout, image, composed, blobs, source_policy
):
    if len(composed) != len(image.data):
        raise ValueError(
            f"composed image has {len(composed)} bytes, "
            f"expected {len(image.data)}"
        )
    expected = _build_expected(layout, image, blobs, source_policy)
    if composed != expected:
        first = next(
            offset
            for offset, (actual, wanted) in enumerate(
                zip(composed, expected)
            )
            if actual != wanted
        )
        raise ValueError(
            f"composed byte at {first:#x} is {composed[first]:#04x}, "
            f"expected {expected[first]:#04x}"
        )

    counts = (
        layout.feedback.default_on_frames << 8
        | layout.feedback.default_off_frames
    ).to_bytes(2, layout.byte_order)
    start = layout.feedback.phase_counts_address
    if composed[start : start + 2] != counts:
        raise ValueError("composed feedback frame counts differ from layout")

    instruction_count, code_entry_count = _validate_instruction_placement(
        layout, composed, blobs
    )
    ranges = composition_write_ranges(layout)
    changed_bytes, permitted_write_bytes = _validate_write_set(
        image.data, composed, ranges
    )
    return (
        changed_bytes,
        permitted_write_bytes,
        instruction_count,
        code_entry_count,
    )


def compose(layout=None, image=None, blobs=None, source_policy="exact"):
    """Return a strictly validated in-memory composition."""
    layout = layout or layout_model.load_layout()
    image = _validate_source(layout, image, source_policy)
    blobs = _validated_blobs(layout, blobs or {})
    data = _build_expected(layout, image, blobs, source_policy)
    (
        changed_bytes,
        permitted_write_bytes,
        instruction_count,
        code_entry_count,
    ) = _validate_composed_contract(
        layout, image, data, blobs, source_policy
    )
    return Composition(
        data=data,
        sha256=hashlib.sha256(data).hexdigest(),
        changed_bytes=changed_bytes,
        permitted_write_bytes=permitted_write_bytes,
        instruction_count=instruction_count,
        code_entry_count=code_entry_count,
    )


def validate_composed(
    layout=None,
    image=None,
    composed=None,
    blobs=None,
    source_policy="exact",
):
    """Validate caller-supplied bytes against the deterministic composition."""
    layout = layout or layout_model.load_layout()
    image = _validate_source(layout, image, source_policy)
    blobs = _validated_blobs(layout, blobs or {})
    if composed is None:
        raise ValueError("composed image bytes are required")
    composed = bytes(composed)
    (
        changed_bytes,
        permitted_write_bytes,
        instruction_count,
        code_entry_count,
    ) = _validate_composed_contract(
        layout, image, composed, blobs, source_policy
    )
    return Composition(
        data=composed,
        sha256=hashlib.sha256(composed).hexdigest(),
        changed_bytes=changed_bytes,
        permitted_write_bytes=permitted_write_bytes,
        instruction_count=instruction_count,
        code_entry_count=code_entry_count,
    )


def _blob_argument(text):
    key, separator, path = text.partition("=")
    if not separator or not key or not path:
        raise argparse.ArgumentTypeError("expected KEY=PATH")
    return key, Path(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blob",
        action="append",
        type=_blob_argument,
        default=[],
        metavar="KEY=PATH",
        help="one SHA-locked Ghidra assembly blob",
    )
    args = parser.parse_args(argv)
    blobs = {}
    for key, path in args.blob:
        if key in blobs:
            parser.error(f"duplicate blob for {key!r}")
        blobs[key] = path

    layout = layout_model.load_layout()
    result = compose(layout=layout, blobs=blobs)
    print(
        "status=PASS"
        f" rom={layout.rom}"
        f" units={len(layout.assembly_units)}"
        f" hooks={len(layout.hooks)}"
        f" families={len(layout.families)}"
    )
    print(
        f"in_memory_sha256={result.sha256}"
        f" changed_bytes={result.changed_bytes}"
        f" permitted_write_bytes={result.permitted_write_bytes}"
    )
    print(
        f"instruction_placements={result.instruction_count}"
        f" code_entries={result.code_entry_count}"
    )
    print(
        "feedback_frame_counts="
        f"{layout.feedback.default_on_frames},"
        f"{layout.feedback.default_off_frames}"
        " flashable=false checksums_recalculated=false"
    )
    print("no ROM file was written")


if __name__ == "__main__":
    main()
