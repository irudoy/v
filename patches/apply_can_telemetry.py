#!/usr/bin/env python3
"""Apply the validated JK08A CAN telemetry layer to a complete runtime."""

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

from patches import apply_map_switching as map_runtime
from patches import can_telemetry
from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import jk08a_checksums as checksums
from patches import rolling_launch
from patches import rolling_launch_assembly
from patches import rolling_launch_layout


ROM_SIZE = 0x100000


class PatchError(ValueError):
    """Raised when a source, configuration, payload, or output is unsafe."""


@dataclass(frozen=True)
class PatchResult:
    data: bytes
    configuration: bytes
    mailbox_record: bytes
    source_sha256: str
    output_sha256: str
    source_checksums: checksums.ChecksumValues
    output_checksums: checksums.ChecksumValues
    composition_changed_bytes: int
    final_changed_bytes: int
    permitted_write_bytes: int
    checksum_changed_bytes: int
    instruction_count: int
    code_entry_count: int


def sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def default_output_path(source):
    source = Path(source)
    return source.with_name(f"{source.stem}-can-telemetry.bin")


def _read_integer(data, address, width, byte_order="big"):
    return int.from_bytes(data[address : address + width], byte_order)


def _require_complete_rolling_endpoint(source, layout, payloads, context):
    for unit in layout.assembly_units:
        actual = source[unit.span.start : unit.span.end]
        if actual != payloads[unit.key]:
            raise PatchError(f"{context}: Rolling Launch unit {unit.key} differs")
    for hook in layout.hooks:
        actual = _read_integer(source, hook.address, hook.width, layout.byte_order)
        if actual != hook.replacement:
            raise PatchError(f"{context}: Rolling Launch hook {hook.key} differs")
    for item in layout.diagnostics:
        actual = _read_integer(source, item.pointer_address, 4, layout.byte_order)
        if actual != item.target:
            raise PatchError(f"{context}: Rolling Launch DID {item.did:#06x} differs")
    configuration = source[layout.configuration.start : layout.configuration.end]
    try:
        valid = rolling_launch.Calibration.from_bytes(configuration).is_valid()
    except (TypeError, ValueError):
        valid = False
    if not valid:
        raise PatchError(f"{context}: Rolling Launch configuration is invalid")


def _require_telemetry_base(source, layout, context):
    for unit in layout.assembly_units:
        if source[unit.span.start : unit.span.end] != bytes([0xFF]) * unit.span.size:
            raise PatchError(f"{context}: telemetry unit {unit.key} is occupied")
    if source[layout.configuration.start : layout.configuration.end] != bytes([0xFF]) * layout.configuration.size:
        raise PatchError(f"{context}: telemetry configuration is occupied")
    if source[layout.reserved_rom.start : layout.reserved_rom.end] != bytes([0xFF]) * layout.reserved_rom.size:
        raise PatchError(f"{context}: telemetry future ROM reserve is occupied")
    for hook in layout.hooks:
        actual = _read_integer(source, hook.address, hook.width, layout.byte_order)
        if actual != hook.stock:
            raise PatchError(f"{context}: telemetry base hook {hook.key} differs")
    record = source[layout.mailbox_record_address : layout.mailbox_record_address + 4]
    if record != can_telemetry.STOCK_MAILBOX_RECORD:
        raise PatchError(f"{context}: mailbox-26 stock record differs")


def _final_write_offsets(layout):
    composition = set(chain.from_iterable(
        range(item.start, item.end)
        for item in can_telemetry_compose.composition_write_ranges(layout)
    ))
    checksum = set(checksums.checksum_byte_offsets())
    overlap = composition & checksum
    if overlap:
        raise PatchError(f"checksum overlaps telemetry write set at {min(overlap):#x}")
    return composition | checksum, checksum


def patch_image(
    source,
    *,
    configuration=None,
    telemetry_layout=None,
    telemetry_payloads=None,
    launch_layout=None,
    launch_payloads=None,
    source_name="<memory>",
    expected_source_sha256=None,
):
    telemetry_layout = telemetry_layout or can_telemetry_layout.load_layout()
    launch_layout = launch_layout or rolling_launch_layout.load_layout()
    try:
        telemetry_payloads = can_telemetry_compose._validated_blobs(
            telemetry_layout,
            telemetry_payloads or can_telemetry_assembly.load_payloads(telemetry_layout),
        )
        launch_payloads = launch_payloads or rolling_launch_assembly.load_payloads(launch_layout)
    except (OSError, ValueError) as error:
        raise PatchError(str(error)) from error

    source = bytes(source)
    if len(source) != ROM_SIZE:
        raise PatchError(f"{source_name}: source has {len(source)} bytes, expected {ROM_SIZE}")
    source_digest = sha256(source)
    if expected_source_sha256 is not None and source_digest != expected_source_sha256:
        raise PatchError(
            f"{source_name}: source SHA-256 is {source_digest}, expected {expected_source_sha256}"
        )
    try:
        source_verification = checksums.require_valid(source, source_name)
    except checksums.ChecksumError as error:
        raise PatchError(str(error)) from error
    _require_complete_rolling_endpoint(source, launch_layout, launch_payloads, source_name)
    _require_telemetry_base(source, telemetry_layout, source_name)

    try:
        model, configuration_bytes = can_telemetry_compose._validated_configuration(configuration)
        mailbox_record = model.mailbox_record()
        composed = can_telemetry_compose._build_expected(
            telemetry_layout,
            source,
            telemetry_payloads,
            configuration_bytes,
            mailbox_record,
        )
        composition_changed, _, instruction_count, entries = can_telemetry_compose._validate_composed(
            telemetry_layout,
            source,
            composed,
            telemetry_payloads,
            configuration_bytes,
            mailbox_record,
        )
        patched = bytes(checksums.recalculate(composed))
        output_verification = checksums.require_valid(patched, "CAN telemetry output")
    except (checksums.ChecksumError, ValueError) as error:
        raise PatchError(str(error)) from error

    permitted, checksum_offsets = _final_write_offsets(telemetry_layout)
    changed = {
        index for index, pair in enumerate(zip(source, patched)) if pair[0] != pair[1]
    }
    outside = changed - permitted
    if outside:
        raise PatchError(f"telemetry output changes undeclared byte at {min(outside):#x}")
    for index, pair in enumerate(zip(composed, patched)):
        if pair[0] != pair[1] and index not in checksum_offsets:
            raise PatchError(f"checksum recalculation changes telemetry byte at {index:#x}")
    if patched[telemetry_layout.configuration.start : telemetry_layout.configuration.end] != configuration_bytes:
        raise PatchError("final telemetry configuration differs")
    start = telemetry_layout.mailbox_record_address
    if patched[start : start + 4] != mailbox_record:
        raise PatchError("final mailbox-26 record differs")

    return PatchResult(
        data=patched,
        configuration=configuration_bytes,
        mailbox_record=mailbox_record,
        source_sha256=source_digest,
        output_sha256=sha256(patched),
        source_checksums=source_verification.stored,
        output_checksums=output_verification.stored,
        composition_changed_bytes=composition_changed,
        final_changed_bytes=len(changed),
        permitted_write_bytes=len(permitted),
        checksum_changed_bytes=len(changed & checksum_offsets),
        instruction_count=instruction_count,
        code_entry_count=entries,
    )


def _format_checksums(values):
    return ",".join(f"{name}={value:#x}" for name, value in values.items())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, help="checksum-valid complete Rolling Launch ROM"
    )
    parser.add_argument("--output", type=Path, help="output path beside INPUT")
    parser.add_argument("--enabled", action="store_true")
    parser.add_argument(
        "--can-id", type=lambda value: int(value, 0), default=0x6F0
    )
    parser.add_argument(
        "--profile", choices=("tuning",), default="tuning"
    )
    parser.add_argument("--tick-divisor", type=int, default=1)
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="compose and verify without writing a ROM file",
    )
    args = parser.parse_args(argv)
    configuration = can_telemetry.Configuration(
        enabled=args.enabled,
        can_id=args.can_id,
        profile=args.profile,
        tick_divisor=args.tick_divisor,
    )
    try:
        source = args.input.read_bytes()
        result = patch_image(
            source,
            configuration=configuration,
            source_name=str(args.input),
        )
    except (OSError, PatchError, ValueError) as error:
        parser.error(str(error))

    print(
        f"status=PASS source={args.input} "
        f"source_sha256={result.source_sha256} "
        f"source_checksums={_format_checksums(result.source_checksums)}"
    )
    print(
        f"enabled={str(configuration.enabled).lower()} "
        f"can_id={configuration.can_id:#05x} "
        f"profile={configuration.profile} "
        f"tick_divisor={configuration.tick_divisor} "
        f"configuration={result.configuration.hex()} "
        f"mailbox_record={result.mailbox_record.hex()}"
    )
    print(
        f"output_sha256={result.output_sha256} "
        f"output_checksums={_format_checksums(result.output_checksums)} "
        f"changed_bytes={result.final_changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes} "
        f"instructions={result.instruction_count} "
        f"entries={result.code_entry_count}"
    )
    if args.verify_only:
        print("no ROM file was written")
        return 0
    output = args.output or default_output_path(args.input)
    if output.resolve() == args.input.resolve():
        parser.error("input and output paths must differ")
    try:
        created = map_runtime.write_output(output, result.data)
        map_runtime.write_md5_sidecar(output, result.data)
    except (OSError, map_runtime.PatchError) as error:
        parser.error(str(error))
    print(f"output={output} status={'created' if created else 'already_exact'}")
    print(f"sidecar={output.name}.md5 hardware_status=UNTESTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
