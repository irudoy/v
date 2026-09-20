#!/usr/bin/env python3
"""Compose the exact JK08A CAN telemetry verification endpoint in memory."""

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

from patches import can_telemetry
from patches import can_telemetry_assembly
from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import map_switching_layout as common
from patches import rolling_launch_compose


@dataclass(frozen=True)
class Composition:
    data: bytes
    base_sha256: str
    sha256: str
    configuration: bytes
    mailbox_record: bytes
    changed_bytes: int
    permitted_write_bytes: int
    instruction_count: int
    code_entry_count: int
    checksums_recalculated: bool = False


def build_base_composition():
    return rolling_launch_compose.compose().data


def composition_write_ranges(layout):
    ranges = [
        common.AddressRange(unit.span.start, unit.span.end, f"assembly.{unit.key}")
        for unit in layout.assembly_units
    ]
    ranges.append(layout.configuration)
    ranges.append(common.AddressRange(
        layout.mailbox_record_address,
        layout.mailbox_record_address + 4,
        "mailbox_record",
    ))
    ranges.extend(
        common.AddressRange(hook.address, hook.address + hook.width, f"hook.{hook.key}")
        for hook in layout.hooks
    )
    ranges.sort(key=lambda item: (item.start, item.end, item.key))
    for left, right in zip(ranges, ranges[1:]):
        if left.overlaps(right):
            raise ValueError(f"telemetry writes overlap: {left.key} and {right.key}")
    return tuple(ranges)


def _validated_blobs(layout, blobs):
    expected = set(layout.assembly_unit_by_key)
    if set(blobs) != expected:
        raise ValueError(
            f"assembly blob set differs; missing={sorted(expected - set(blobs))}; "
            f"extra={sorted(set(blobs) - expected)}"
        )
    return {
        unit.key: can_telemetry_layout.validate_assembled_blob(unit, blobs[unit.key])
        for unit in layout.assembly_units
    }


def _validated_configuration(configuration):
    manifest = can_telemetry_profile.load_manifest()
    if configuration is None:
        configuration = can_telemetry.default_configuration()
    if isinstance(configuration, can_telemetry.Configuration):
        model = configuration
        data = model.to_bytes(manifest)
    else:
        data = bytes(configuration)
        model = can_telemetry.Configuration.from_bytes(data, manifest)
    if not model.is_valid(manifest) or model.to_bytes(manifest) != data:
        raise ValueError("CAN telemetry configuration round trip differs")
    return model, data


def _build_expected(layout, base, blobs, configuration, mailbox_record):
    data = bytearray(base)
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = blobs[unit.key]
    data[layout.configuration.start : layout.configuration.end] = configuration
    start = layout.mailbox_record_address
    data[start : start + 4] = mailbox_record
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = hook.replacement.to_bytes(
            hook.width, layout.byte_order
        )
    return bytes(data)


def _validate_write_set(base, composed, ranges):
    permitted = set(chain.from_iterable(range(item.start, item.end) for item in ranges))
    changed = {
        index
        for index, (before, after) in enumerate(zip(base, composed))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise ValueError(f"telemetry composition changes undeclared byte at {min(outside):#x}")
    return len(changed), len(permitted)


def _validate_instruction_placement(layout, composed, blobs):
    parsed = can_telemetry_assembly.validate_assembly_sources(layout)
    can_telemetry_assembly.validate_instruction_semantics(layout, parsed, blobs)
    instructions = 0
    entries = set()
    for unit in layout.assembly_units:
        unit_instructions = {
            item.address for item in parsed[unit.key].statements if item.kind == "instruction"
        }
        for item in parsed[unit.key].statements:
            if item.kind != "instruction":
                continue
            offset = item.address - unit.span.start
            if composed[item.address : item.address + item.size] != blobs[unit.key][offset : offset + item.size]:
                raise ValueError(f"{unit.key}: instruction bytes differ at {item.address:#x}")
            instructions += 1
        for key in unit.code_regions:
            entry = layout.code_region_by_key[key].entry
            if entry not in unit_instructions:
                raise ValueError(f"{key}: code entry is not an instruction")
            entries.add(entry)
    if instructions != layout.assembled_instruction_count:
        raise ValueError(
            f"instruction count is {instructions}, expected {layout.assembled_instruction_count}"
        )
    return instructions, len(entries)


def _validate_composed(layout, base, composed, blobs, configuration, mailbox_record):
    if len(composed) != len(base):
        raise ValueError("telemetry composition length differs from its base")
    expected = _build_expected(layout, base, blobs, configuration, mailbox_record)
    if composed != expected:
        first = next(
            index for index, pair in enumerate(zip(composed, expected)) if pair[0] != pair[1]
        )
        raise ValueError(f"telemetry composition differs at {first:#x}")
    for hook in layout.hooks:
        actual = int.from_bytes(composed[hook.address : hook.address + hook.width], layout.byte_order)
        if actual != hook.replacement:
            raise ValueError(f"{hook.key}: composed hook differs")
    start = layout.mailbox_record_address
    if composed[start : start + 4] != mailbox_record:
        raise ValueError("mailbox-26 record differs")
    if composed[layout.reserved_rom.start : layout.reserved_rom.end] != bytes([0xFF]) * layout.reserved_rom.size:
        raise ValueError("telemetry future ROM reserve is not erased")
    instructions, entries = _validate_instruction_placement(layout, composed, blobs)
    changed, permitted = _validate_write_set(base, composed, composition_write_ranges(layout))
    return changed, permitted, instructions, entries


def compose(layout=None, base=None, blobs=None, configuration=None):
    layout = layout or can_telemetry_layout.load_layout()
    base = build_base_composition() if base is None else bytes(base)
    base = can_telemetry_layout.validate_base_composition(layout, base)
    blobs = _validated_blobs(layout, blobs or can_telemetry_assembly.load_payloads(layout))
    model, configuration = _validated_configuration(configuration)
    mailbox_record = model.mailbox_record()
    data = _build_expected(layout, base, blobs, configuration, mailbox_record)
    changed, permitted, instructions, entries = _validate_composed(
        layout, base, data, blobs, configuration, mailbox_record
    )
    output_sha256 = hashlib.sha256(data).hexdigest()
    if (
        model == can_telemetry.default_configuration()
        and layout.expected_composition_sha256 != "0" * 64
        and output_sha256 != layout.expected_composition_sha256
    ):
        raise ValueError(
            f"default telemetry composition SHA-256 is {output_sha256}, expected {layout.expected_composition_sha256}"
        )
    return Composition(
        data=data,
        base_sha256=hashlib.sha256(base).hexdigest(),
        sha256=output_sha256,
        configuration=configuration,
        mailbox_record=mailbox_record,
        changed_bytes=changed,
        permitted_write_bytes=permitted,
        instruction_count=instructions,
        code_entry_count=entries,
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payloads", type=Path, default=can_telemetry_assembly.DEFAULT_PAYLOADS)
    args = parser.parse_args(argv)
    layout = can_telemetry_layout.load_layout()
    result = compose(layout=layout, blobs=can_telemetry_assembly.load_payloads(layout, args.payloads))
    print(
        "status=PASS"
        f" rom={layout.rom}"
        f" base_sha256={result.base_sha256}"
        f" in_memory_sha256={result.sha256}"
        f" changed_bytes={result.changed_bytes}"
        f" permitted_write_bytes={result.permitted_write_bytes}"
        f" instructions={result.instruction_count}"
        f" entries={result.code_entry_count}"
    )
    print("flashable=false checksums_recalculated=false no ROM file was written")


if __name__ == "__main__":
    main()
