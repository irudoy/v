#!/usr/bin/env python3
"""Upgrade the known pre-fix JK08A map-switching runtime in place.

The input must already contain the complete previous map-switching runtime.
Calibration bytes, including all manually edited slot copies, remain unchanged.
Only the fallback zero-fill literal, startup-wrapper span, and checksum fields
may differ in the output.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching as patcher
from patches import jk08a_checksums as checksums
from patches import map_switching_compose as composer
from patches import map_switching_layout as layout_model
from tools.mapkit import rom as romkit


OLD_CLEAR_START = 0xFFFF5D00
OLD_STARTUP_SHA256 = (
    "fbab3032582bfced276a09c737de62e0c82e58f28d1a1e17e58d8b4d42474dca"
)
OLD_STARTUP_BLOB = bytes.fromhex(
    "4f22d00f400b0009d10e6410644cd00e400b00094f26000b0009"
    "ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    "ffffffffffff"
    "0002c648ffff5d00000d3660"
    "ffffffffffffffffffffffffffffffffffffffff"
)


class UpgradeError(ValueError):
    """Raised when the source is not the exact supported pre-fix runtime."""


@dataclass(frozen=True)
class UpgradeResult:
    data: bytes
    source_sha256: str
    output_sha256: str
    changed_bytes: int
    permitted_write_bytes: int
    checksum_changed_bytes: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def default_output_path(source):
    source = Path(source)
    return source.with_name(f"{source.stem}-fixed-reset.bin")


def _read_unsigned(data, address, width):
    return int.from_bytes(data[address : address + width], "big")


def _require_value(data, address, width, expected, label):
    actual = _read_unsigned(data, address, width)
    if actual != expected:
        raise UpgradeError(
            f"{label} at {address:#x} is {actual:#x}, expected {expected:#x}"
        )


def _validated_blobs(layout, blobs):
    expected = set(layout.assembly_unit_by_key)
    actual = set(blobs)
    if actual != expected:
        raise UpgradeError(
            "runtime payload set differs; "
            f"missing={sorted(expected - actual)}; "
            f"extra={sorted(actual - expected)}"
        )
    try:
        return {
            unit.key: layout_model.validate_assembled_blob(
                unit, blobs[unit.key]
            )
            for unit in layout.assembly_units
        }
    except (OSError, ValueError) as error:
        raise UpgradeError(str(error)) from error


def _require_runtime(layout, blobs, data, old_startup):
    stock = romkit.load(layout.rom).data
    identity = slice(
        layout_model.COMPATIBLE_IDENTITY_START,
        layout_model.COMPATIBLE_IDENTITY_END,
    )
    if data[identity] != stock[identity]:
        raise UpgradeError("calibration identity differs from exact JK08A")

    startup = layout.assembly_unit_by_key["startup_wrapper"]
    expected_startup = OLD_STARTUP_BLOB if old_startup else blobs[startup.key]
    actual_startup = data[startup.span.start : startup.span.end]
    if actual_startup != expected_startup:
        raise UpgradeError(
            "startup wrapper does not match the supported "
            + ("pre-fix" if old_startup else "fixed")
            + " payload"
        )

    for unit in layout.assembly_units:
        if unit.key == startup.key:
            continue
        actual = data[unit.span.start : unit.span.end]
        if actual != blobs[unit.key]:
            raise UpgradeError(
                f"{unit.key} does not match the tracked runtime payload"
            )

    for hook in layout.hooks:
        _require_value(
            data,
            hook.address,
            hook.width,
            hook.replacement,
            hook.key,
        )

    for family in layout.families:
        expected = b"".join(
            address.to_bytes(4, layout.byte_order)
            for address in family.all_slot_addresses
        )
        start = family.pointer_table
        actual = data[start : start + len(expected)]
        if actual != expected:
            raise UpgradeError(
                f"{family.key} pointer table differs from the layout"
            )

    managed = set(checksums.checksum_byte_offsets())
    for region in composer.composition_write_ranges(layout):
        managed.update(range(region.start, region.end))
    for offset in range(
            layout_model.COMPATIBLE_PROTECTED_START, len(data)):
        if offset not in managed and data[offset] != stock[offset]:
            raise UpgradeError(
                "protected upper ROM differs from exact JK08A outside "
                f"managed map-switching/checksum ranges at {offset:#x}"
            )


def upgrade_image(source, layout=None, blobs=None, source_name="<memory>"):
    """Return the fixed-reset image while preserving every calibration byte."""
    layout = layout or layout_model.load_layout()
    blobs = _validated_blobs(
        layout, blobs if blobs is not None else patcher.load_payloads(layout)
    )
    source = bytes(source)
    try:
        checksums.require_valid(source, source_name)
        startup = layout.assembly_unit_by_key["startup_wrapper"]
        anchor = layout.anchor_by_key["startup_clear_start_stock"]
        if hashlib.sha256(OLD_STARTUP_BLOB).hexdigest() != OLD_STARTUP_SHA256:
            raise UpgradeError("internal pre-fix startup fixture hash differs")
        _require_value(
            source,
            anchor.address,
            anchor.width,
            OLD_CLEAR_START,
            "pre-fix startup clear",
        )
        _require_runtime(layout, blobs, source, old_startup=True)

        upgraded = bytearray(source)
        upgraded[
            anchor.address : anchor.address + anchor.width
        ] = anchor.value.to_bytes(anchor.width, layout.byte_order)
        upgraded[startup.span.start : startup.span.end] = blobs[startup.key]
        upgraded = checksums.recalculate(upgraded)
        checksums.require_valid(upgraded, "fixed-reset output")
        _require_value(
            upgraded,
            anchor.address,
            anchor.width,
            anchor.value,
            anchor.key,
        )
        _require_runtime(layout, blobs, upgraded, old_startup=False)
    except (checksums.ChecksumError, KeyError, ValueError) as error:
        if isinstance(error, UpgradeError):
            raise
        raise UpgradeError(str(error)) from error

    permitted = set(
        range(anchor.address, anchor.address + anchor.width)
    ) | set(range(startup.span.start, startup.span.end))
    permitted |= set(checksums.checksum_byte_offsets())
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, upgraded))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise UpgradeError(
            f"upgrade changed undeclared byte at {min(outside):#x}"
        )
    checksum_offsets = checksums.checksum_byte_offsets()
    return UpgradeResult(
        data=upgraded,
        source_sha256=sha256(source),
        output_sha256=sha256(upgraded),
        changed_bytes=len(changed),
        permitted_write_bytes=len(permitted),
        checksum_changed_bytes=sum(
            source[offset] != upgraded[offset]
            for offset in checksum_offsets
        ),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="pre-fix map-switching ROM")
    parser.add_argument(
        "--output",
        type=Path,
        help="output path; defaults to INPUT-fixed-reset.bin",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="validate and upgrade in memory without writing files",
    )
    args = parser.parse_args(argv)

    try:
        source = args.input.read_bytes()
        result = upgrade_image(source, source_name=str(args.input))
    except (OSError, UpgradeError, patcher.PatchError) as error:
        parser.error(str(error))

    print(
        f"status=PASS source={args.input} "
        f"source_sha256={result.source_sha256}"
    )
    print(
        f"output_sha256={result.output_sha256} "
        f"changed_bytes={result.changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes}"
    )
    if args.verify_only:
        print("no ROM file was written")
        return 0

    output = args.output or default_output_path(args.input)
    if output.resolve() == args.input.resolve():
        parser.error("input and output paths must differ")
    try:
        created = patcher.write_output(output, result.data)
        patcher.write_md5_sidecar(output, result.data)
    except (OSError, patcher.PatchError) as error:
        parser.error(str(error))
    print(f"output={output} status={'created' if created else 'already_exact'}")
    print(f"md5={patcher.md5(result.data)} sidecar={output.name}.md5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
