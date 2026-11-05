#!/usr/bin/env python3
"""Compose the validated JK08A Rolling Launch stage for the ROM builder.

The caller supplies the calibration record and the efficiency table E that
the builder derives from F. The input must be the exact complete twelve-family
map-switching stage-20 endpoint derived from the hardware-readback lookup
stage and using the target-vehicle 0x20 released-button code. Machine
payloads, hooks, diagnostics, configuration, efficiency, checksums, and the
closed write set are all revalidated before an output can be written.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from itertools import chain
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching as map_runtime
from patches import jk08a_checksums as canonical_checksums
from patches import map_switching_layout as map_layout_model
from patches import map_switching_compose as map_composer
from patches import rolling_launch
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout as rolling_layout_model
from patches import rom_checksums


HARDWARE_RESULTS_PATH = Path(__file__).with_name("hardware-results.toml")


def _load_base_digest():
    try:
        data = tomllib.loads(HARDWARE_RESULTS_PATH.read_text(encoding="utf-8"))
        stages = [
            stage
            for stage in data["map_switching"]["stages"]
            if stage.get("use") == "rolling_launch_base"
        ]
        if len(stages) != 1:
            raise KeyError("one map-switching stage with use rolling_launch_base")
        value = stages[0]["sha256"]
    except (OSError, KeyError, TypeError, tomllib.TOMLDecodeError) as error:
        raise RuntimeError(
            f"cannot load {HARDWARE_RESULTS_PATH}: {error}"
        ) from error
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise RuntimeError(
            f"{HARDWARE_RESULTS_PATH}: invalid SHA-256 base identity"
        )
    return value


# The map-switching endpoint that the Rolling Launch stage is applied to.
LOCKED_MAP_SWITCHING_SOURCE_SHA256 = _load_base_digest()


class PatchError(ValueError):
    """Raised when an input, payload, configuration, or output is unsafe."""


@dataclass(frozen=True)
class PatchResult:
    data: bytes
    configuration: bytes
    efficiency: bytes
    source_sha256: str
    output_sha256: str
    source_checksums: rom_checksums.ChecksumValues
    output_checksums: rom_checksums.ChecksumValues
    composition_changed_bytes: int
    final_changed_bytes: int
    permitted_write_bytes: int
    checksum_changed_bytes: int
    instruction_count: int
    code_entry_count: int
    diagnostic_count: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def md5(data):
    return hashlib.md5(data).hexdigest()


def _read_integer(data, address, width, byte_order):
    return int.from_bytes(data[address : address + width], byte_order)


def _require_map_switching_endpoint(
    source, layout, payloads, context
):
    for unit in layout.assembly_units:
        actual = source[unit.span.start : unit.span.end]
        expected = map_composer.endpoint_unit_bytes(
            layout, payloads, unit
        )
        if actual != expected:
            raise PatchError(
                f"{context}: map-switching unit {unit.key} differs"
            )
    for hook in layout.hooks:
        actual = _read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        expected = hook.replacement
        if actual != expected:
            raise PatchError(
                f"{context}: map-switching hook {hook.key} is "
                f"{actual:#x}, expected {expected:#x}"
            )


def _require_rolling_base(source, layout, context):
    for span in layout.claimed_rom_ranges:
        erased = bytes([0xFF]) * span.size
        actual = source[span.start : span.end]
        if actual != erased:
            raise PatchError(
                f"{context}: Rolling Launch ROM allocation is occupied "
                f"({span.key})"
            )
    for hook in layout.hooks:
        value = _read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        if value != hook.stock:
            raise PatchError(
                f"{context}: Rolling Launch base hook {hook.key} is "
                f"{value:#x}, expected {hook.stock:#x}"
            )
    for item in layout.diagnostics:
        value = _read_integer(
            source, item.pointer_address, 4, layout.byte_order
        )
        if value != item.stock:
            raise PatchError(
                f"{context}: DID {item.did:#06x} pointer is occupied"
            )


def _validate_source(
    source,
    map_layout,
    rolling_layout,
    map_payloads,
    source_name,
    expected_source_sha256,
    checksum_layout,
):
    source = bytes(source)
    if len(source) != checksum_layout.rom_size:
        raise PatchError(
            f"{source_name}: source has {len(source)} bytes, expected "
            f"{checksum_layout.rom_size}"
        )
    digest = sha256(source)
    if expected_source_sha256 is not None and digest != expected_source_sha256:
        raise PatchError(
            f"{source_name}: source SHA-256 is {digest}, expected "
            f"{expected_source_sha256}"
        )
    try:
        verification = rom_checksums.require_valid(
            source, checksum_layout, source_name
        )
    except rom_checksums.ChecksumError as error:
        raise PatchError(str(error)) from error
    _require_map_switching_endpoint(
        source, map_layout, map_payloads, source_name
    )
    _require_rolling_base(source, rolling_layout, source_name)
    return source, digest, verification


def _validate_calibration(calibration):
    if not isinstance(calibration, rolling_launch.Calibration):
        raise PatchError("calibration must be a Rolling Launch Calibration")
    if not calibration.is_valid():
        raise PatchError("Rolling Launch calibration is invalid")
    configuration = calibration.to_bytes()
    if rolling_launch.Calibration.from_bytes(configuration) != calibration:
        raise PatchError("Rolling Launch calibration round trip differs")
    return calibration, configuration


def _final_write_offsets(layout, checksum_layout=None):
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    composition = set(chain.from_iterable(
        range(item.start, item.end)
        for item in rolling_launch_compose.composition_write_ranges(layout)
    ))
    checksum = set(rom_checksums.checksum_byte_offsets(checksum_layout))
    overlap = composition & checksum
    if overlap:
        raise PatchError(
            f"checksum field overlaps Rolling Launch write set at "
            f"{min(overlap):#x}"
        )
    return composition | checksum, checksum


def _validate_final_preservation(
    source, patched, layout, checksum_layout
):
    permitted, checksum_offsets = _final_write_offsets(
        layout, checksum_layout
    )
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, patched))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise PatchError(
            f"final image changes undeclared source byte at {min(outside):#x}"
        )
    return len(changed), len(permitted), len(changed & checksum_offsets)


def patch_image(
    source,
    *,
    calibration,
    efficiency,
    map_layout=None,
    rolling_layout=None,
    map_payloads=None,
    rolling_payloads=None,
    source_name="<memory>",
    expected_source_sha256=LOCKED_MAP_SWITCHING_SOURCE_SHA256,
    checksum_layout=None,
):
    """Return one checksum-valid Rolling Launch image after strict checks.

    ``efficiency`` is the table E that the builder derives from F of its
    stock input."""
    map_layout = map_layout or map_layout_model.load_layout()
    rolling_layout = rolling_layout or rolling_layout_model.load_layout()
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    try:
        map_payloads = map_payloads or map_runtime.load_payloads(map_layout)
        rolling_payloads = rolling_payloads or (
            rolling_launch_assembly.load_payloads(rolling_layout)
        )
    except (OSError, ValueError, map_runtime.PatchError) as error:
        raise PatchError(str(error)) from error

    expected_map_units = set(map_layout.assembly_unit_by_key)
    if set(map_payloads) != expected_map_units:
        raise PatchError("map-switching payload set differs from layout")
    try:
        map_payloads = {
            unit.key: map_layout_model.validate_assembled_blob(
                unit, map_payloads[unit.key]
            )
            for unit in map_layout.assembly_units
        }
        rolling_payloads = rolling_launch_compose._validated_blobs(
            rolling_layout, rolling_payloads
        )
    except (OSError, ValueError) as error:
        raise PatchError(str(error)) from error

    source, source_digest, source_verification = _validate_source(
        source,
        map_layout,
        rolling_layout,
        map_payloads,
        source_name,
        expected_source_sha256,
        checksum_layout,
    )
    calibration, configuration = _validate_calibration(calibration)
    try:
        efficiency = rolling_launch_compose._validate_efficiency(
            rolling_layout, efficiency
        )
    except (TypeError, ValueError) as error:
        raise PatchError(f"Rolling Launch efficiency table is invalid: {error}") from error
    try:
        composed = rolling_launch_compose._build_expected(
            rolling_layout, source, rolling_payloads, configuration, efficiency
        )
        (
            composition_changed,
            _,
            instruction_count,
            code_entry_count,
        ) = rolling_launch_compose._validate_composed(
            rolling_layout,
            source,
            composed,
            rolling_payloads,
            configuration,
            efficiency,
        )
        patched = bytes(rom_checksums.recalculate(
            composed, checksum_layout
        ))
        output_verification = rom_checksums.require_valid(
            patched, checksum_layout, "Rolling Launch output"
        )
    except (rom_checksums.ChecksumError, ValueError) as error:
        raise PatchError(str(error)) from error

    final_changed, permitted, checksum_changed = _validate_final_preservation(
        source, patched, rolling_layout, checksum_layout
    )
    checksum_offsets = set(
        rom_checksums.checksum_byte_offsets(checksum_layout)
    )
    for offset, (before, after) in enumerate(zip(composed, patched)):
        if before != after and offset not in checksum_offsets:
            raise PatchError(
                f"checksum recalculation changed payload byte at {offset:#x}"
            )
    if patched[
        rolling_layout.configuration.start : rolling_layout.configuration.end
    ] != configuration:
        raise PatchError("final Rolling Launch configuration differs")
    if patched[rolling_layout.efficiency.start : rolling_layout.efficiency.end] != efficiency:
        raise PatchError("final Rolling Launch efficiency table differs")

    output_digest = sha256(patched)

    return PatchResult(
        data=patched,
        configuration=configuration,
        efficiency=efficiency,
        source_sha256=source_digest,
        output_sha256=output_digest,
        source_checksums=source_verification.stored,
        output_checksums=output_verification.stored,
        composition_changed_bytes=composition_changed,
        final_changed_bytes=final_changed,
        permitted_write_bytes=permitted,
        checksum_changed_bytes=checksum_changed,
        instruction_count=instruction_count,
        code_entry_count=code_entry_count,
        diagnostic_count=len(rolling_layout.diagnostics),
    )
