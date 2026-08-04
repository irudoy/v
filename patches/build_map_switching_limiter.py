#!/usr/bin/env python3
"""Build the aggregate JK08A Map 1 limiter-shadow endpoint.

The source is locked to the successful startup selector-init readback. The
output installs only the final startup wrapper, the atomic limiter commit, the
two rev-limiter families initialized identically across all five slots, their
pointer tables, and the three direct limiter-shadow hooks. Lookup adapters, the
selector host, and CAN feedback remain absent. The cumulative hardware sequence
is emitted by build_map_switching_limiter_overlays.py; this aggregate is its
final byte-equivalence target rather than its first hardware image.
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

from patches import apply_map_switching as runtime
from patches import build_map_switching_selector_init as selector_init
from patches import jk08a_checksums as checksums
from patches import map_switching_assembly as assembly
from patches import map_switching_layout as layout_model


HARDWARE_READBACK_SHA256 = (
    "7dcb43b2181c030bde772999b674afb72a8cd196e93a0aae3fecf90069ed62d3"
)
HARDWARE_OUTPUT_SHA256 = (
    "1833922fc7d3428ed9f9998a99281d4c02b66c027cc39f7620aa3a79d541964a"
)
ROM_SIZE = 0x100000
RESET_SELECTOR_LINE_START = 0x00008080
RESET_SELECTOR_LINE_END = 0x00008100
CLAIMED_ROM_START = 0x000D2108
CLAIMED_ROM_END = 0x000D3860
MARKER_LINE_START = 0x000D2280
MARKER_LINE_END = 0x000D2300
STARTUP_WRAPPER_START = 0x000D22A0
STARTUP_WRAPPER_END = 0x000D2300
LIMITER_COMMIT_START = 0x000D3660
LIMITER_COMMIT_END = 0x000D3760
STARTUP_WRAPPER_SHA256 = (
    "352db08c013f1f3b91551afea5a12db60cb160698d7239e1e8ac7271054ac4a3"
)
LIMITER_COMMIT_SHA256 = (
    "e1e296e0d2f1dccef21982f14f4e3e1aebdc39fba6b68ae8b3e2ecbc16d5a5aa"
)
LIMITER_FAMILY_KEYS = (
    "rev_limit_fuel_cut",
    "rev_limit_throttle_cut",
)
LIMITER_HOOK_KEYS = frozenset(
    {
        "rev_fuel_cut_base",
        "rev_throttle_cluster_base",
        "rev_throttle_scalar_base",
    }
)


class LimiterGateError(ValueError):
    """Raised when the source or limiter-gate output violates the contract."""


@dataclass(frozen=True)
class LimiterGateResult:
    data: bytes
    source_sha256: str
    output_sha256: str
    startup_wrapper_sha256: str
    limiter_commit_sha256: str
    changed_bytes: int
    startup_wrapper_changed_bytes: int
    limiter_commit_changed_bytes: int
    limiter_copy_changed_bytes: int
    pointer_table_changed_bytes: int
    hook_changed_bytes: int
    checksum_changed_bytes: int
    permitted_write_bytes: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def default_output_path(source):
    source = Path(source)
    return source.with_name(
        f"{source.stem}-startup-limiter-map1-d3660.bin"
    )


def load_gate_payloads(layout=None):
    """Load and validate only the two final runtime units used by this gate."""
    layout = layout or layout_model.load_layout()
    try:
        parsed = assembly.validate_assembly_sources(layout)
        payloads = runtime.load_payloads(layout)
    except (OSError, ValueError, runtime.PatchError) as error:
        raise LimiterGateError(str(error)) from error

    startup = payloads["startup_wrapper"]
    limiter = payloads["limiter_commit"]
    if sha256(startup) != STARTUP_WRAPPER_SHA256:
        raise LimiterGateError("startup-wrapper payload SHA-256 differs")
    if sha256(limiter) != LIMITER_COMMIT_SHA256:
        raise LimiterGateError("limiter-commit payload SHA-256 differs")
    if (
        parsed["startup_wrapper"].instruction_count != 14
        or parsed["startup_wrapper"].data_bytes != 12
    ):
        raise LimiterGateError("startup-wrapper source contract differs")
    if (
        parsed["limiter_commit"].instruction_count != 56
        or parsed["limiter_commit"].data_bytes != 36
    ):
        raise LimiterGateError("limiter-commit source contract differs")
    return {
        "startup_wrapper": startup,
        "limiter_commit": limiter,
    }


def _startup_hook(layout):
    hooks = {hook.key: hook for hook in layout.hooks}
    try:
        hook = hooks["startup_initializer"]
    except KeyError as error:
        raise LimiterGateError(
            "layout has no startup initializer hook"
        ) from error
    if (
        hook.address != 0x00027D28
        or hook.width != 4
        or hook.stock != 0x0002C648
        or hook.replacement != STARTUP_WRAPPER_START
    ):
        raise LimiterGateError("layout startup initializer hook differs")
    return hook


def _limiter_families(layout):
    families = layout.family_by_key
    try:
        selected = tuple(families[key] for key in LIMITER_FAMILY_KEYS)
    except KeyError as error:
        raise LimiterGateError(
            f"layout has no limiter family {error.args[0]!r}"
        ) from error
    if any(family.access_kind != "ram_shadow" for family in selected):
        raise LimiterGateError("limiter family is not a RAM-shadow family")
    if tuple(family.key for family in selected) != LIMITER_FAMILY_KEYS:
        raise LimiterGateError("limiter family order differs")
    return selected


def _require_hooks(layout, data, context, limiter_active):
    startup = _startup_hook(layout)
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        active = hook.key == startup.key or (
            limiter_active and hook.key in LIMITER_HOOK_KEYS
        )
        expected = hook.replacement if active else hook.stock
        if actual != expected:
            raise LimiterGateError(
                f"{context}: {hook.key} at {hook.address:#x} is "
                f"{actual:#x}, expected {expected:#x}"
            )


def _require_stock_anchors(layout, data, context):
    for anchor in layout.anchors:
        actual = int.from_bytes(
            data[anchor.address : anchor.address + anchor.width],
            layout.byte_order,
        )
        if actual != anchor.value:
            raise LimiterGateError(
                f"{context}: {anchor.key} at {anchor.address:#x} is "
                f"{actual:#x}, expected {anchor.value:#x}"
            )


def _require_source_runtime(source):
    expected = bytearray(
        [0xFF] * (CLAIMED_ROM_END - CLAIMED_ROM_START)
    )
    marker_start = MARKER_LINE_START - CLAIMED_ROM_START
    marker_end = MARKER_LINE_END - CLAIMED_ROM_START
    expected[marker_start:marker_end] = bytes(
        MARKER_LINE_END - MARKER_LINE_START
    )
    payload_start = STARTUP_WRAPPER_START - CLAIMED_ROM_START
    payload_end = selector_init.SELECTOR_INIT_END - CLAIMED_ROM_START
    expected[payload_start:payload_end] = selector_init.SELECTOR_INIT_BLOB
    actual = source[CLAIMED_ROM_START:CLAIMED_ROM_END]
    if actual != expected:
        first = next(
            index
            for index, (actual_byte, expected_byte) in enumerate(
                zip(actual, expected)
            )
            if actual_byte != expected_byte
        )
        address = CLAIMED_ROM_START + first
        raise LimiterGateError(
            f"source staged runtime differs at {address:#x}: "
            f"{actual[first]:#04x}, expected {expected[first]:#04x}"
        )


def _limiter_storage_offsets(layout):
    copy_offsets = set()
    pointer_offsets = set()
    for family in _limiter_families(layout):
        copy_offsets.update(
            chain.from_iterable(
                range(address, address + family.byte_length)
                for address in family.copies
            )
        )
        pointer_offsets.update(
            range(
                family.pointer_table,
                family.pointer_table + layout.pointer_table_size,
            )
        )
    return copy_offsets, pointer_offsets


def _materialize_limiter_storage(layout, source, patched):
    for family in _limiter_families(layout):
        map_1 = source[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for address in family.copies:
            patched[address : address + family.byte_length] = map_1
        pointers = b"".join(
            address.to_bytes(4, layout.byte_order)
            for address in family.all_slot_addresses
        )
        start = family.pointer_table
        patched[start : start + len(pointers)] = pointers


def _require_limiter_storage(layout, source, patched):
    for family in _limiter_families(layout):
        map_1 = source[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for slot, address in enumerate(family.copies, 2):
            actual = patched[address : address + family.byte_length]
            if actual != map_1:
                raise LimiterGateError(
                    f"{family.key} Map {slot} differs from input Map 1"
                )
        expected_pointers = b"".join(
            address.to_bytes(4, layout.byte_order)
            for address in family.all_slot_addresses
        )
        start = family.pointer_table
        if patched[start : start + len(expected_pointers)] != expected_pointers:
            raise LimiterGateError(
                f"{family.key} pointer table differs"
            )


def build_image(
    source,
    layout=None,
    payloads=None,
    source_name="<memory>",
    expected_source_sha256=HARDWARE_READBACK_SHA256,
):
    """Return a checked limiter-shadow gate without writing a file."""
    layout = layout or layout_model.load_layout()
    source = bytes(source)
    source_digest = sha256(source)
    if source_digest != expected_source_sha256:
        raise LimiterGateError(
            f"{source_name}: source sha256 is {source_digest}, expected "
            f"{expected_source_sha256}"
        )
    if len(source) != ROM_SIZE:
        raise LimiterGateError(
            f"{source_name}: source has {len(source)} bytes, expected {ROM_SIZE}"
        )
    try:
        source_verification = checksums.require_valid(source, source_name)
    except checksums.ChecksumError as error:
        raise LimiterGateError(str(error)) from error
    if source[RESET_SELECTOR_LINE_START:RESET_SELECTOR_LINE_END] != bytes(128):
        raise LimiterGateError("source reset-selector line is not all zero")
    _require_source_runtime(source)
    _require_hooks(layout, source, source_name, limiter_active=False)
    _require_stock_anchors(layout, source, source_name)

    if payloads is None:
        payloads = load_gate_payloads(layout)
    expected_payload_keys = {"startup_wrapper", "limiter_commit"}
    if set(payloads) != expected_payload_keys:
        raise LimiterGateError(
            "limiter-gate payload set differs; "
            f"expected={sorted(expected_payload_keys)}; "
            f"actual={sorted(payloads)}"
        )
    try:
        startup = layout_model.validate_assembled_blob(
            layout.assembly_unit_by_key["startup_wrapper"],
            payloads["startup_wrapper"],
        )
        limiter = layout_model.validate_assembled_blob(
            layout.assembly_unit_by_key["limiter_commit"],
            payloads["limiter_commit"],
        )
    except (OSError, ValueError) as error:
        raise LimiterGateError(str(error)) from error

    patched = bytearray(source)
    patched[STARTUP_WRAPPER_START:STARTUP_WRAPPER_END] = startup
    patched[LIMITER_COMMIT_START:LIMITER_COMMIT_END] = limiter
    _materialize_limiter_storage(layout, source, patched)
    for hook in layout.hooks:
        if hook.key in LIMITER_HOOK_KEYS:
            patched[hook.address : hook.address + hook.width] = (
                hook.replacement.to_bytes(hook.width, layout.byte_order)
            )
    patched = checksums.recalculate(patched)

    try:
        output_verification = checksums.require_valid(
            patched, "startup limiter Map 1 output"
        )
    except checksums.ChecksumError as error:
        raise LimiterGateError(str(error)) from error
    if not source_verification.valid or not output_verification.valid:
        raise LimiterGateError("internal checksum verification did not pass")
    if patched[STARTUP_WRAPPER_START:STARTUP_WRAPPER_END] != startup:
        raise LimiterGateError("startup-wrapper payload differs after checksums")
    if patched[LIMITER_COMMIT_START:LIMITER_COMMIT_END] != limiter:
        raise LimiterGateError("limiter-commit payload differs after checksums")
    if patched[MARKER_LINE_START:STARTUP_WRAPPER_START] != bytes(
        STARTUP_WRAPPER_START - MARKER_LINE_START
    ):
        raise LimiterGateError("marker bytes before startup wrapper changed")
    _require_limiter_storage(layout, source, patched)
    _require_hooks(layout, patched, "startup limiter Map 1 output", True)
    _require_stock_anchors(layout, patched, "startup limiter Map 1 output")

    copy_offsets, pointer_offsets = _limiter_storage_offsets(layout)
    startup_offsets = set(
        range(STARTUP_WRAPPER_START, STARTUP_WRAPPER_END)
    )
    limiter_offsets = set(
        range(LIMITER_COMMIT_START, LIMITER_COMMIT_END)
    )
    hook_offsets = {
        offset
        for hook in layout.hooks
        if hook.key in LIMITER_HOOK_KEYS
        for offset in range(hook.address, hook.address + hook.width)
    }
    checksum_offsets = set(checksums.checksum_byte_offsets())
    permitted = (
        startup_offsets
        | limiter_offsets
        | copy_offsets
        | pointer_offsets
        | hook_offsets
        | checksum_offsets
    )
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, patched))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise LimiterGateError(
            f"limiter gate changed undeclared byte at {min(outside):#x}"
        )

    return LimiterGateResult(
        data=bytes(patched),
        source_sha256=source_digest,
        output_sha256=sha256(patched),
        startup_wrapper_sha256=sha256(startup),
        limiter_commit_sha256=sha256(limiter),
        changed_bytes=len(changed),
        startup_wrapper_changed_bytes=sum(
            source[offset] != patched[offset] for offset in startup_offsets
        ),
        limiter_commit_changed_bytes=sum(
            source[offset] != patched[offset] for offset in limiter_offsets
        ),
        limiter_copy_changed_bytes=sum(
            source[offset] != patched[offset] for offset in copy_offsets
        ),
        pointer_table_changed_bytes=sum(
            source[offset] != patched[offset] for offset in pointer_offsets
        ),
        hook_changed_bytes=sum(
            source[offset] != patched[offset] for offset in hook_offsets
        ),
        checksum_changed_bytes=sum(
            source[offset] != patched[offset] for offset in checksum_offsets
        ),
        permitted_write_bytes=len(permitted),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, help="exact successful selector-init readback ROM"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output path; defaults to INPUT-startup-limiter-map1-d3660.bin",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="build and verify in memory without writing files",
    )
    args = parser.parse_args(argv)

    try:
        source = args.input.read_bytes()
        result = build_image(source, source_name=str(args.input))
    except (OSError, LimiterGateError) as error:
        parser.error(str(error))

    print(
        f"status=PASS source={args.input} "
        f"source_sha256={result.source_sha256}"
    )
    print(
        "startup_hook=preserved:0x27d28->0xd22a0 "
        f"startup_wrapper_sha256={result.startup_wrapper_sha256} "
        f"limiter_commit_sha256={result.limiter_commit_sha256}"
    )
    print(
        "limiter_families=rev_limit_fuel_cut,rev_limit_throttle_cut "
        "maps_2_to_5=input_map_1 direct_limiter_hooks=replaced:3"
    )
    print(
        f"output_sha256={result.output_sha256} "
        f"changed_bytes={result.changed_bytes} "
        f"startup_wrapper_changed_bytes={result.startup_wrapper_changed_bytes} "
        f"limiter_commit_changed_bytes={result.limiter_commit_changed_bytes} "
        f"limiter_copy_changed_bytes={result.limiter_copy_changed_bytes} "
        f"pointer_table_changed_bytes={result.pointer_table_changed_bytes} "
        f"hook_changed_bytes={result.hook_changed_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes}"
    )
    print(
        "selector_host=absent lookup_adapters=absent can_feedback=absent "
        "checksums=PASS"
    )

    if args.verify_only:
        print("no ROM file was written")
        return 0

    output = args.output or default_output_path(args.input)
    if output.resolve() == args.input.resolve():
        parser.error("input and output paths must differ")
    try:
        created = runtime.write_output(output, result.data)
        runtime.write_md5_sidecar(output, result.data)
    except (OSError, runtime.PatchError) as error:
        parser.error(str(error))
    print(f"output={output} status={'created' if created else 'already_exact'}")
    print(f"md5={runtime.md5(result.data)} sidecar={output.name}.md5")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
