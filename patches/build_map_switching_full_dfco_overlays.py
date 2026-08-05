#!/usr/bin/env python3
"""Build the corrected cumulative JK08A full-DFCO hardware overlays.

Every output is a complete one-MiB ROM suitable for a normal PCMFlash write.
The chain starts from the exact successful revision-2 lookup Overlay 14
readback. Stage 15 installs the inactive four-family DFCO adapter and Map
1-equivalent Hold and Intermediate Restore storage. Stages 16 and 17 activate
the shared cut and restore hooks independently. Stage 18 installs the selector
host while keeping the CAN serializer stock; no selection gesture is permitted
because queued feedback could not drain. Stage 19 installs the CAN feedback
runtime and produces the complete ten-family endpoint. The selector uses the
target-vehicle 0x20 released-button code.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching as runtime
from patches import build_map_switching_limiter as limiter_gate
from patches import build_map_switching_lookup_overlays as lookup_overlays
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model


SOURCE_STEM_SUFFIX = "-14-fuel-comp-startup-hook-2cf1c"
HARDWARE_SOURCE_SHA256 = (
    "f0a03f6fef205aa1ac42e4471dd0bad995a7082c35d24bdb639fc342ccdda892"
)
EXPECTED_OUTPUT_SHA256 = (
    "5b7816f7be70e12f1312dbff9727df9a5677192811515ce8f6b66d1793bea7f2",
    "84796d58bdd3c45ba4c6774f936bedd54109cbee7a60053dcecf0b38c4777e58",
    "e89bd22402e416c9178286b554b1d1d054586c49096574d1c88d9bd5e96f9e0d",
    "f42f2ec56b590c7e82b17a343dc966c7c27c1981dde528815020e7d974d30b8c",
    "52568ec1006df01c2524afe505a4ed9c8b00aa15bf5ea2a946d74107bbd97b84",
)
HISTORICAL_OUTPUT_SHA256 = (
    "5b7816f7be70e12f1312dbff9727df9a5677192811515ce8f6b66d1793bea7f2",
    "84796d58bdd3c45ba4c6774f936bedd54109cbee7a60053dcecf0b38c4777e58",
    "e89bd22402e416c9178286b554b1d1d054586c49096574d1c88d9bd5e96f9e0d",
    "4732168ad4aa0f8b8bf11e0b25b1ae506eed50713c789d3fb4297fafa9c37ac0",
    "e2fb90d5d9f2ba23c09cb55ee77732175ae0753aabe77f8e7363a84554218ea1",
)
FULL_DFCO_UNIT_KEYS = ("full_dfco_adapter",)
FULL_DFCO_FAMILY_KEYS = (
    "over_run_fuel_hold",
    "over_run_fuel_intermediate_restore",
)
FULL_DFCO_HOOK_KEYS = (
    "overrun_cut_lookup",
    "overrun_restore_lookup",
)
BASE_UNIT_KEYS = frozenset(
    {
        "startup_wrapper",
        "limiter_commit",
        *lookup_overlays.LOOKUP_UNIT_KEYS,
    }
)
BASE_HOOK_KEYS = frozenset(
    {
        "startup_initializer",
        *limiter_gate.LIMITER_HOOK_KEYS,
        *lookup_overlays.LOOKUP_HOOK_ORDER,
    }
)
SELECTOR_UNIT_KEYS = ("selector_host",)
SELECTOR_HOOK_KEYS = ("selector_host_call",)
FEEDBACK_UNIT_KEYS = (
    "cruise_feedback_wrapper",
    "cruise_feedback_engine",
)
FEEDBACK_HOOK_KEYS = ("cruise_feedback_serializer",)


class FullDfcoOverlayError(ValueError):
    """Raised when a full-DFCO overlay violates its contract."""


@dataclass(frozen=True)
class OverlaySpec:
    sequence: int
    key: str
    filename_suffix: str
    unit_keys: tuple[str, ...]
    hook_keys: tuple[str, ...]
    storage_family_keys: tuple[str, ...]
    active_unit_keys: frozenset[str]
    active_hook_keys: frozenset[str]
    full_dfco_hook_keys: frozenset[str]
    functional_selection_allowed: bool


OVERLAY_SPECS = (
    OverlaySpec(
        sequence=15,
        key="full_dfco_payload_map1",
        filename_suffix="full-dfco-payload-map1",
        unit_keys=FULL_DFCO_UNIT_KEYS,
        hook_keys=(),
        storage_family_keys=FULL_DFCO_FAMILY_KEYS,
        active_unit_keys=BASE_UNIT_KEYS | set(FULL_DFCO_UNIT_KEYS),
        active_hook_keys=BASE_HOOK_KEYS,
        full_dfco_hook_keys=frozenset(),
        functional_selection_allowed=False,
    ),
    OverlaySpec(
        sequence=16,
        key="dfco_hold_entry_hook",
        filename_suffix="dfco-hold-entry-hook-4fdd0",
        unit_keys=(),
        hook_keys=(FULL_DFCO_HOOK_KEYS[0],),
        storage_family_keys=(),
        active_unit_keys=BASE_UNIT_KEYS | set(FULL_DFCO_UNIT_KEYS),
        active_hook_keys=BASE_HOOK_KEYS,
        full_dfco_hook_keys=frozenset(FULL_DFCO_HOOK_KEYS[:1]),
        functional_selection_allowed=False,
    ),
    OverlaySpec(
        sequence=17,
        key="dfco_restore_hooks",
        filename_suffix="dfco-full-intermediate-restore-hook-50258",
        unit_keys=(),
        hook_keys=(FULL_DFCO_HOOK_KEYS[1],),
        storage_family_keys=(),
        active_unit_keys=BASE_UNIT_KEYS | set(FULL_DFCO_UNIT_KEYS),
        active_hook_keys=BASE_HOOK_KEYS,
        full_dfco_hook_keys=frozenset(FULL_DFCO_HOOK_KEYS),
        functional_selection_allowed=False,
    ),
    OverlaySpec(
        sequence=18,
        key="selector_host_boot_only",
        filename_suffix="selector-host-boot-only-no-map-gesture",
        unit_keys=SELECTOR_UNIT_KEYS,
        hook_keys=SELECTOR_HOOK_KEYS,
        storage_family_keys=(),
        active_unit_keys=(
            BASE_UNIT_KEYS
            | set(FULL_DFCO_UNIT_KEYS)
            | set(SELECTOR_UNIT_KEYS)
        ),
        active_hook_keys=BASE_HOOK_KEYS | set(SELECTOR_HOOK_KEYS),
        full_dfco_hook_keys=frozenset(FULL_DFCO_HOOK_KEYS),
        functional_selection_allowed=False,
    ),
    OverlaySpec(
        sequence=19,
        key="can_feedback",
        filename_suffix="can-feedback-full-runtime",
        unit_keys=FEEDBACK_UNIT_KEYS,
        hook_keys=FEEDBACK_HOOK_KEYS,
        storage_family_keys=(),
        active_unit_keys=(
            BASE_UNIT_KEYS
            | set(FULL_DFCO_UNIT_KEYS)
            | set(SELECTOR_UNIT_KEYS)
            | set(FEEDBACK_UNIT_KEYS)
        ),
        active_hook_keys=(
            BASE_HOOK_KEYS
            | set(SELECTOR_HOOK_KEYS)
            | set(FEEDBACK_HOOK_KEYS)
        ),
        full_dfco_hook_keys=frozenset(FULL_DFCO_HOOK_KEYS),
        functional_selection_allowed=True,
    ),
)


@dataclass(frozen=True)
class OverlayResult:
    spec: OverlaySpec
    data: bytes
    source_sha256: str
    output_sha256: str
    output_md5: str
    changed_bytes: int
    component_changed_bytes: int
    checksum_changed_bytes: int
    permitted_write_bytes: int
    cumulative_changed_bytes: int


def default_output_prefix(source):
    source = Path(source)
    stem = source.stem
    if stem.endswith("_readback"):
        stem = stem[: -len("_readback")]
    if stem.endswith(SOURCE_STEM_SUFFIX):
        stem = stem[: -len(SOURCE_STEM_SUFFIX)]
    return source.with_name(f"{stem}-map-switching-safe-v4")


def output_paths(prefix):
    prefix = Path(prefix)
    return tuple(
        prefix.with_name(
            f"{prefix.name}-{spec.sequence:02d}-{spec.filename_suffix}.bin"
        )
        for spec in OVERLAY_SPECS
    )


def manifest_path(prefix):
    prefix = Path(prefix)
    return prefix.with_name(f"{prefix.name}-full-dfco.sha256")


def _hook_by_key(layout, key):
    try:
        return next(hook for hook in layout.hooks if hook.key == key)
    except StopIteration as error:
        raise FullDfcoOverlayError(
            f"layout has no hook {key!r}"
        ) from error


def _unit_offsets(layout, keys):
    offsets = set()
    for key in keys:
        try:
            unit = layout.assembly_unit_by_key[key]
        except KeyError as error:
            raise FullDfcoOverlayError(
                f"layout has no assembly unit {key!r}"
            ) from error
        offsets.update(range(unit.span.start, unit.span.end))
    return offsets


def _hook_offsets(layout, keys):
    return {
        offset
        for key in keys
        for hook in (_hook_by_key(layout, key),)
        for offset in range(hook.address, hook.address + hook.width)
    }


def _family_storage_offsets(layout, keys):
    offsets = set()
    for key in keys:
        try:
            family = layout.family_by_key[key]
        except KeyError as error:
            raise FullDfcoOverlayError(
                f"layout has no family {key!r}"
            ) from error
        for address in family.copies:
            offsets.update(range(address, address + family.byte_length))
        offsets.update(
            range(
                family.pointer_table,
                family.pointer_table + layout.pointer_table_size,
            )
        )
    return offsets


def _component_offsets(layout, spec):
    return (
        _unit_offsets(layout, spec.unit_keys)
        | _hook_offsets(layout, spec.hook_keys)
        | _family_storage_offsets(layout, spec.storage_family_keys)
    )


def _require_unit_state(
    layout, data, payloads, active_unit_keys, context
):
    active_unit_keys = set(active_unit_keys)
    known = set(layout.assembly_unit_by_key)
    if not active_unit_keys <= known:
        raise FullDfcoOverlayError(
            f"{context}: unknown active assembly unit set"
        )
    for unit in layout.assembly_units:
        actual = data[unit.span.start : unit.span.end]
        expected = (
            payloads[unit.key]
            if unit.key in active_unit_keys
            else bytes([unit.fill]) * unit.span.size
        )
        if actual != expected:
            raise FullDfcoOverlayError(
                f"{context}: assembly unit {unit.key} differs"
            )


def _require_hook_state(
    layout,
    data,
    active_hook_keys,
    full_dfco_hook_keys,
    context,
):
    active_hook_keys = set(active_hook_keys)
    full_dfco_hook_keys = set(full_dfco_hook_keys)
    known = {hook.key for hook in layout.hooks}
    if not active_hook_keys <= known:
        raise FullDfcoOverlayError(
            f"{context}: unknown active hook set"
        )
    if not full_dfco_hook_keys <= set(FULL_DFCO_HOOK_KEYS):
        raise FullDfcoOverlayError(
            f"{context}: unknown full-DFCO hook set"
        )
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        if hook.key not in active_hook_keys:
            expected = hook.stock
        elif (
            hook.key in FULL_DFCO_HOOK_KEYS
            and hook.key not in full_dfco_hook_keys
        ):
            expected = lookup_overlays.LEGACY_OVERRUN_ADAPTER_ENTRY
        else:
            expected = hook.replacement
        if actual != expected:
            raise FullDfcoOverlayError(
                f"{context}: {hook.key} at {hook.address:#x} is "
                f"{actual:#x}, expected {expected:#x}"
            )


def _full_dfco_families(layout):
    return tuple(layout.family_by_key[key] for key in FULL_DFCO_FAMILY_KEYS)


def _materialize_full_dfco_storage(layout, source, patched):
    for family in _full_dfco_families(layout):
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


def _require_full_dfco_storage(layout, source, data, context):
    for family in _full_dfco_families(layout):
        map_1 = source[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for slot, address in enumerate(family.copies, 2):
            actual = data[address : address + family.byte_length]
            if actual != map_1:
                raise FullDfcoOverlayError(
                    f"{context}: {family.key} Map {slot} differs from Map 1"
                )
        expected_pointers = b"".join(
            address.to_bytes(4, layout.byte_order)
            for address in family.all_slot_addresses
        )
        start = family.pointer_table
        actual = data[start : start + layout.pointer_table_size]
        if actual != expected_pointers:
            raise FullDfcoOverlayError(
                f"{context}: {family.key} pointer table differs"
            )


def _require_storage(
    layout, source, data, context, *, require_full_dfco
):
    try:
        limiter_gate._require_limiter_storage(layout, source, data)
        lookup_overlays._require_lookup_storage(
            layout, source, data, context
        )
    except (
        limiter_gate.LimiterGateError,
        lookup_overlays.LookupOverlayError,
    ) as error:
        raise FullDfcoOverlayError(str(error)) from error
    if require_full_dfco:
        _require_full_dfco_storage(layout, source, data, context)


def _require_source_contract(layout, source, payloads, source_name):
    digest = limiter_gate.sha256(source)
    if len(source) != limiter_gate.ROM_SIZE:
        raise FullDfcoOverlayError(
            f"{source_name}: source has {len(source)} bytes, expected "
            f"{limiter_gate.ROM_SIZE}"
        )
    try:
        checksums.require_valid(source, source_name)
        limiter_gate._require_stock_anchors(layout, source, source_name)
    except (
        checksums.ChecksumError,
        limiter_gate.LimiterGateError,
    ) as error:
        raise FullDfcoOverlayError(str(error)) from error
    if source[
        limiter_gate.RESET_SELECTOR_LINE_START :
        limiter_gate.RESET_SELECTOR_LINE_END
    ] != bytes(128):
        raise FullDfcoOverlayError(
            f"{source_name}: reset-selector line is not all zero"
        )
    _require_unit_state(
        layout, source, payloads, BASE_UNIT_KEYS, source_name
    )
    _require_hook_state(
        layout, source, BASE_HOOK_KEYS, (), source_name
    )
    _require_storage(
        layout,
        source,
        source,
        source_name,
        require_full_dfco=False,
    )
    return digest


def _apply_component(layout, current, payloads, spec):
    patched = bytearray(current)
    for key in spec.unit_keys:
        unit = layout.assembly_unit_by_key[key]
        patched[unit.span.start : unit.span.end] = payloads[key]
    for key in spec.hook_keys:
        hook = _hook_by_key(layout, key)
        patched[hook.address : hook.address + hook.width] = (
            hook.replacement.to_bytes(hook.width, layout.byte_order)
        )
    if spec.storage_family_keys:
        _materialize_full_dfco_storage(layout, current, patched)
    return bytes(checksums.recalculate(patched))


def _require_stage_contract(
    layout,
    source,
    data,
    payloads,
    spec,
    cumulative_component_offsets,
):
    context = f"full-DFCO overlay {spec.sequence:02d} {spec.key}"
    try:
        checksums.require_valid(data, context)
        limiter_gate._require_stock_anchors(layout, data, context)
    except (
        checksums.ChecksumError,
        limiter_gate.LimiterGateError,
    ) as error:
        raise FullDfcoOverlayError(str(error)) from error
    if data[
        limiter_gate.RESET_SELECTOR_LINE_START :
        limiter_gate.RESET_SELECTOR_LINE_END
    ] != bytes(128):
        raise FullDfcoOverlayError(
            f"{context}: reset-selector line differs"
        )
    _require_unit_state(
        layout, data, payloads, spec.active_unit_keys, context
    )
    _require_hook_state(
        layout,
        data,
        spec.active_hook_keys,
        spec.full_dfco_hook_keys,
        context,
    )
    _require_storage(
        layout,
        source,
        data,
        context,
        require_full_dfco=True,
    )

    changed_from_source = {
        offset
        for offset, (before, after) in enumerate(zip(source, data))
        if before != after
    }
    permitted_from_source = cumulative_component_offsets | set(
        checksums.checksum_byte_offsets()
    )
    outside = changed_from_source - permitted_from_source
    if outside:
        raise FullDfcoOverlayError(
            f"{context}: cumulative undeclared byte at {min(outside):#x}"
        )
    return len(changed_from_source)


def _build_final_endpoint(layout, source, payloads):
    patched = bytearray(source)
    for key in (
        *FULL_DFCO_UNIT_KEYS,
        *SELECTOR_UNIT_KEYS,
        *FEEDBACK_UNIT_KEYS,
    ):
        unit = layout.assembly_unit_by_key[key]
        patched[unit.span.start : unit.span.end] = payloads[key]
    _materialize_full_dfco_storage(layout, source, patched)
    for key in (
        *FULL_DFCO_HOOK_KEYS,
        *SELECTOR_HOOK_KEYS,
        *FEEDBACK_HOOK_KEYS,
    ):
        hook = _hook_by_key(layout, key)
        patched[hook.address : hook.address + hook.width] = (
            hook.replacement.to_bytes(hook.width, layout.byte_order)
        )
    return bytes(checksums.recalculate(patched))


def build_overlays(
    source,
    layout=None,
    payloads=None,
    source_name="<memory>",
    expected_source_sha256=HARDWARE_SOURCE_SHA256,
    expected_output_sha256=EXPECTED_OUTPUT_SHA256,
):
    """Return the checked cumulative full-DFCO hardware overlay chain."""
    layout = layout or layout_model.load_layout()
    source = bytes(source)
    if payloads is None:
        try:
            payloads = runtime.load_payloads(layout)
        except (OSError, runtime.PatchError) as error:
            raise FullDfcoOverlayError(str(error)) from error
    if set(payloads) != set(layout.assembly_unit_by_key):
        raise FullDfcoOverlayError(
            "full-DFCO payload set differs from layout"
        )
    try:
        payloads = {
            unit.key: layout_model.validate_assembled_blob(
                unit, payloads[unit.key]
            )
            for unit in layout.assembly_units
        }
    except (OSError, ValueError) as error:
        raise FullDfcoOverlayError(str(error)) from error

    source_digest = _require_source_contract(
        layout, source, payloads, source_name
    )
    if (
        expected_source_sha256 is not None
        and source_digest != expected_source_sha256
    ):
        raise FullDfcoOverlayError(
            f"{source_name}: source sha256 is {source_digest}, expected "
            f"{expected_source_sha256}"
        )

    if expected_output_sha256 is not None:
        if len(expected_output_sha256) != len(OVERLAY_SPECS):
            raise FullDfcoOverlayError(
                "expected overlay SHA-256 count differs from stage count"
            )
    else:
        expected_output_sha256 = (None,) * len(OVERLAY_SPECS)

    current = source
    results = []
    cumulative_component_offsets = set()
    checksum_offsets = set(checksums.checksum_byte_offsets())
    for spec, expected_digest in zip(
        OVERLAY_SPECS, expected_output_sha256
    ):
        component_offsets = _component_offsets(layout, spec)
        cumulative_component_offsets.update(component_offsets)
        patched = _apply_component(layout, current, payloads, spec)
        digest = limiter_gate.sha256(patched)
        if expected_digest is not None and digest != expected_digest:
            raise FullDfcoOverlayError(
                f"overlay {spec.sequence:02d} SHA-256 is {digest}, "
                f"expected {expected_digest}"
            )

        changed = {
            offset
            for offset, (before, after) in enumerate(zip(current, patched))
            if before != after
        }
        permitted = component_offsets | checksum_offsets
        outside = changed - permitted
        if outside:
            raise FullDfcoOverlayError(
                f"overlay {spec.sequence:02d} changed undeclared byte "
                f"at {min(outside):#x}"
            )
        component_changed = len(changed & component_offsets)
        if component_changed == 0:
            raise FullDfcoOverlayError(
                f"overlay {spec.sequence:02d} changes no component byte"
            )
        cumulative_changed = _require_stage_contract(
            layout,
            source,
            patched,
            payloads,
            spec,
            cumulative_component_offsets,
        )
        results.append(
            OverlayResult(
                spec=spec,
                data=patched,
                source_sha256=limiter_gate.sha256(current),
                output_sha256=digest,
                output_md5=runtime.md5(patched),
                changed_bytes=len(changed),
                component_changed_bytes=component_changed,
                checksum_changed_bytes=len(changed & checksum_offsets),
                permitted_write_bytes=len(permitted),
                cumulative_changed_bytes=cumulative_changed,
            )
        )
        current = patched

    if current != _build_final_endpoint(layout, source, payloads):
        raise FullDfcoOverlayError(
            "final overlay differs from the complete runtime endpoint"
        )
    return tuple(results)


def _manifest_content(results, paths):
    return "".join(
        f"{result.output_sha256} *{path.name}\n"
        for result, path in zip(results, paths)
    )


def _require_output_available(path, expected):
    path = Path(path)
    if path.exists() and path.read_bytes() != expected:
        raise FullDfcoOverlayError(
            f"existing output differs: {path}"
        )


def write_overlays(prefix, results):
    """Write both images, MD5 sidecars, and the ordered SHA manifest."""
    paths = output_paths(prefix)
    if len(results) != len(paths):
        raise FullDfcoOverlayError(
            "result count differs from output count"
        )
    manifest = manifest_path(prefix)
    manifest_bytes = _manifest_content(results, paths).encode("ascii")

    for result, path in zip(results, paths):
        _require_output_available(path, result.data)
        sidecar = path.with_name(f"{path.name}.md5")
        expected_sidecar = (
            f"{result.output_md5} *{path.name}\n"
        ).encode("ascii")
        _require_output_available(sidecar, expected_sidecar)
    _require_output_available(manifest, manifest_bytes)

    created = 0
    for result, path in zip(results, paths):
        created += int(runtime.write_output(path, result.data))
        created += int(runtime.write_md5_sidecar(path, result.data))
    if not manifest.exists():
        manifest.parent.mkdir(parents=True, exist_ok=True)
        manifest.write_bytes(manifest_bytes)
        created += 1
    return paths, manifest, created


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, help="exact successful lookup Overlay 14 readback"
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        help="output prefix; defaults beside INPUT",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="build and verify all overlays without writing files",
    )
    args = parser.parse_args(argv)

    try:
        source = args.input.read_bytes()
        results = build_overlays(source, source_name=str(args.input))
    except (OSError, FullDfcoOverlayError) as error:
        parser.error(str(error))

    print(
        f"status=PASS source={args.input} "
        f"source_sha256={limiter_gate.sha256(source)} stages={len(results)}"
    )
    for result in results:
        print(
            f"stage={result.spec.sequence:02d} key={result.spec.key} "
            f"source_sha256={result.source_sha256} "
            f"output_sha256={result.output_sha256} "
            f"md5={result.output_md5} "
            f"changed_bytes={result.changed_bytes} "
            f"component_changed_bytes={result.component_changed_bytes} "
            f"checksum_changed_bytes={result.checksum_changed_bytes} "
            f"permitted_write_bytes={result.permitted_write_bytes} "
            f"cumulative_changed_bytes={result.cumulative_changed_bytes} "
            "functional_selection_allowed="
            f"{str(result.spec.functional_selection_allowed).lower()}"
        )
    print(
        "final_equals_complete_runtime_endpoint=true checksums=PASS "
        "stage18_boot_only=true stage18_selection_gesture=forbidden"
    )

    if args.verify_only:
        print("no ROM files were written")
        return 0

    prefix = args.output_prefix or default_output_prefix(args.input)
    try:
        paths, manifest, created = write_overlays(prefix, results)
    except (
        OSError,
        FullDfcoOverlayError,
        runtime.PatchError,
    ) as error:
        parser.error(str(error))
    for result, path in zip(results, paths):
        print(
            f"stage={result.spec.sequence:02d} output={path} "
            f"sidecar={path.name}.md5"
        )
    print(f"manifest={manifest} files_created={created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
