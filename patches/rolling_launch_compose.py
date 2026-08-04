#!/usr/bin/env python3
"""Compose the JK08A Rolling Launch verification fixture in memory.

The deterministic base is the complete SHA-locked map-switching composition.
Rolling Launch assembly spans, hooks, diagnostic DID pointers, and one validated
configuration record are applied through a closed write set. Stored checksum
fields remain unchanged and this module has no output-file operation.
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

from patches import apply_map_switching
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch
from patches import rolling_launch_assembly
from patches import rolling_launch_layout


@dataclass(frozen=True)
class Composition:
    data: bytes
    base_sha256: str
    sha256: str
    changed_bytes: int
    permitted_write_bytes: int
    instruction_count: int
    code_entry_count: int
    diagnostic_count: int
    checksums_recalculated: bool = False


def build_base_composition():
    """Build the exact complete ten-family map-switching endpoint."""
    layout = map_switching_layout.load_layout()
    payloads = apply_map_switching.load_payloads(layout)
    return map_switching_compose.compose(layout=layout, blobs=payloads)


def composition_write_ranges(layout):
    """Return the complete non-overlapping Rolling Launch write set."""
    ranges = [
        map_switching_layout.AddressRange(
            unit.span.start, unit.span.end, f"assembly.{unit.key}"
        )
        for unit in layout.assembly_units
    ]
    ranges.append(layout.configuration)
    ranges.extend(map_switching_layout.AddressRange(
        hook.address, hook.address + hook.width, f"hook.{hook.key}"
    ) for hook in layout.hooks)
    ranges.extend(map_switching_layout.AddressRange(
        item.pointer_address,
        item.pointer_address + 4,
        f"did.{item.did:04x}",
    ) for item in layout.diagnostics)
    ranges.sort(key=lambda item: (item.start, item.end, item.key))
    for left, right in zip(ranges, ranges[1:]):
        if left.overlaps(right):
            raise ValueError(
                f"composition writes overlap: {left.key} and {right.key}"
            )
    return tuple(ranges)


def _validate_configuration(layout, configuration):
    if isinstance(configuration, rolling_launch.Calibration):
        configuration = configuration.to_bytes()
    configuration = bytes(configuration)
    if len(configuration) != layout.configuration.size:
        raise ValueError(
            f"configuration is {len(configuration)} bytes, expected "
            f"{layout.configuration.size}"
        )
    calibration = rolling_launch.Calibration.from_bytes(configuration)
    if not calibration.is_valid():
        raise ValueError("Rolling Launch configuration is invalid")
    return configuration


def _validated_blobs(layout, blobs):
    expected = set(layout.assembly_unit_by_key)
    if set(blobs) != expected:
        raise ValueError(
            "assembly blob set differs"
            f"; missing={sorted(expected - set(blobs))}"
            f"; extra={sorted(set(blobs) - expected)}"
        )
    return {
        unit.key: rolling_launch_layout.validate_assembled_blob(
            unit, blobs[unit.key]
        )
        for unit in layout.assembly_units
    }


def _build_expected(layout, base, blobs, configuration):
    data = bytearray(base)
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = blobs[unit.key]
    data[layout.configuration.start : layout.configuration.end] = configuration
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = (
            hook.replacement.to_bytes(hook.width, layout.byte_order)
        )
    for item in layout.diagnostics:
        data[item.pointer_address : item.pointer_address + 4] = (
            item.target.to_bytes(4, layout.byte_order)
        )
    return bytes(data)


def _validate_write_set(base, composed, ranges):
    permitted = set(chain.from_iterable(
        range(item.start, item.end) for item in ranges
    ))
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(base, composed))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise ValueError(
            f"composed image changes undeclared byte at {min(outside):#x}"
        )
    return len(changed), len(permitted)


def _validate_instruction_placement(layout, composed, blobs):
    parsed = rolling_launch_assembly.validate_assembly_sources(layout)
    rolling_launch_assembly.validate_instruction_semantics(
        layout, parsed, blobs
    )
    instructions = 0
    entries = set()
    for unit in layout.assembly_units:
        unit_instructions = {
            item.address
            for item in parsed[unit.key].statements
            if item.kind == "instruction"
        }
        for item in parsed[unit.key].statements:
            if item.kind != "instruction":
                continue
            offset = item.address - unit.span.start
            expected = blobs[unit.key][offset : offset + item.size]
            actual = composed[item.address : item.address + item.size]
            if actual != expected:
                raise ValueError(
                    f"{unit.key}: instruction bytes differ at {item.address:#x}"
                )
            instructions += 1
        for key in unit.code_regions:
            entry = layout.code_region_by_key[key].entry
            if entry not in unit_instructions:
                raise ValueError(f"{key}: code entry is not an instruction")
            entries.add(entry)
    if instructions != layout.assembled_instruction_count:
        raise ValueError(
            f"instruction count is {instructions}, expected "
            f"{layout.assembled_instruction_count}"
        )
    return instructions, len(entries)


def _validate_composed(layout, base, composed, blobs, configuration):
    if len(composed) != len(base):
        raise ValueError("composed image length differs from its base")
    expected = _build_expected(layout, base, blobs, configuration)
    if composed != expected:
        first = next(
            offset
            for offset, (actual, wanted) in enumerate(zip(composed, expected))
            if actual != wanted
        )
        raise ValueError(
            f"composed byte at {first:#x} is {composed[first]:#04x}, "
            f"expected {expected[first]:#04x}"
        )
    for hook in layout.hooks:
        actual = int.from_bytes(
            composed[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        if actual != hook.replacement:
            raise ValueError(f"{hook.key}: composed hook differs")
    for item in layout.diagnostics:
        actual = int.from_bytes(
            composed[item.pointer_address : item.pointer_address + 4],
            layout.byte_order,
        )
        if actual != item.target:
            raise ValueError(f"DID {item.did:#06x}: composed pointer differs")
    instructions, entries = _validate_instruction_placement(
        layout, composed, blobs
    )
    changed, permitted = _validate_write_set(
        base, composed, composition_write_ranges(layout)
    )
    return changed, permitted, instructions, entries


def compose(
    layout=None,
    base=None,
    blobs=None,
    configuration=None,
):
    """Return a strictly validated, non-flashable in-memory composition."""
    layout = layout or rolling_launch_layout.load_layout()
    if base is None:
        base = build_base_composition().data
    base = rolling_launch_layout.validate_base_composition(layout, base)
    blobs = _validated_blobs(
        layout,
        blobs or rolling_launch_assembly.load_payloads(layout),
    )
    configuration = _validate_configuration(
        layout,
        layout.default_configuration if configuration is None else configuration,
    )
    data = _build_expected(layout, base, blobs, configuration)
    changed, permitted, instructions, entries = _validate_composed(
        layout, base, data, blobs, configuration
    )
    output_sha256 = hashlib.sha256(data).hexdigest()
    if (
        configuration == layout.default_configuration
        and output_sha256 != layout.expected_composition_sha256
    ):
        raise ValueError(
            f"default composition SHA-256 is {output_sha256}, expected "
            f"{layout.expected_composition_sha256}"
        )
    return Composition(
        data=data,
        base_sha256=hashlib.sha256(base).hexdigest(),
        sha256=output_sha256,
        changed_bytes=changed,
        permitted_write_bytes=permitted,
        instruction_count=instructions,
        code_entry_count=entries,
        diagnostic_count=len(layout.diagnostics),
    )


def validate_composed(
    layout=None,
    base=None,
    composed=None,
    blobs=None,
    configuration=None,
):
    """Validate caller-supplied bytes against the deterministic fixture."""
    layout = layout or rolling_launch_layout.load_layout()
    if base is None:
        base = build_base_composition().data
    base = rolling_launch_layout.validate_base_composition(layout, base)
    if composed is None:
        raise ValueError("composed image bytes are required")
    blobs = _validated_blobs(
        layout,
        blobs or rolling_launch_assembly.load_payloads(layout),
    )
    configuration = _validate_configuration(
        layout,
        layout.default_configuration if configuration is None else configuration,
    )
    composed = bytes(composed)
    changed, permitted, instructions, entries = _validate_composed(
        layout, base, composed, blobs, configuration
    )
    output_sha256 = hashlib.sha256(composed).hexdigest()
    if (
        configuration == layout.default_configuration
        and output_sha256 != layout.expected_composition_sha256
    ):
        raise ValueError(
            f"default composition SHA-256 is {output_sha256}, expected "
            f"{layout.expected_composition_sha256}"
        )
    return Composition(
        data=composed,
        base_sha256=hashlib.sha256(base).hexdigest(),
        sha256=output_sha256,
        changed_bytes=changed,
        permitted_write_bytes=permitted,
        instruction_count=instructions,
        code_entry_count=entries,
        diagnostic_count=len(layout.diagnostics),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--payloads",
        type=Path,
        default=rolling_launch_assembly.DEFAULT_PAYLOADS,
        help="tracked Ghidra payload bundle",
    )
    args = parser.parse_args(argv)
    layout = rolling_launch_layout.load_layout()
    blobs = rolling_launch_assembly.load_payloads(layout, args.payloads)
    result = compose(layout=layout, blobs=blobs)
    print(
        "status=PASS"
        f" rom={layout.rom}"
        f" base_sha256={result.base_sha256}"
        f" in_memory_sha256={result.sha256}"
    )
    print(
        f"changed_bytes={result.changed_bytes}"
        f" permitted_write_bytes={result.permitted_write_bytes}"
        f" instruction_placements={result.instruction_count}"
        f" code_entries={result.code_entry_count}"
        f" diagnostics={result.diagnostic_count}"
    )
    print("flashable=false checksums_recalculated=false no ROM file was written")


if __name__ == "__main__":
    main()
