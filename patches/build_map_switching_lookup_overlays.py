#!/usr/bin/env python3
"""Build cumulative atomic JK08A lookup overlays for hardware isolation.

Every output is a complete one-MiB ROM suitable for a normal PCMFlash write.
The chain starts from the exact successful limiter Overlay 05 image. Stage 06
installs inactive lookup code, Map 1-equivalent copies, and pointer tables.
Stages 07 through 14 activate one lookup hook at a time. The startup-time fuel
compensation hook is deliberately last. Selector-host and CAN-feedback code and
hooks remain absent, and no intermediate hardware readback is an input.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from itertools import chain
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching as file_writer
from patches import build_map_switching_limiter as limiter_gate
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model


SOURCE_STEM_SUFFIX = "-limiter-overlay-05-throttle-scalar-hook-77bac"
HARDWARE_SOURCE_SHA256 = limiter_gate.HARDWARE_OUTPUT_SHA256
EXPECTED_OUTPUT_SHA256 = (
    "990c7aff5dc62f33682900ff93b30b4888bd7171147689b1d43c58c13452d59f",
    "95049dca436d74375954bf2e8586525573f9c7b864636144e9b5195130a8a6ba",
    "50d6b59b1a236bf141eba2c5f74687fd440962510aa13e49a7414e42c1324e7b",
    "b2941317c94f130833e350065980e96d44e1b60eef7c9e2ca6ce88b4b002bb89",
    "bc93046ef2d22cbe5f109c32745774e707e5246eb2e6b80b7cea44b1d5bd202a",
    "7dae4b294a7833753ef3c3d4b64a61ba417a66bb894209bcabaf315b48f9b0ca",
    "dc7dadadcc679eca88f07093967080051dc00994bbb7085b231596b040df475e",
    "80aa12d99145d1e51861c885f78485075e135b1cd218654d4abb7a5871c2837e",
    "f0a03f6fef205aa1ac42e4471dd0bad995a7082c35d24bdb639fc342ccdda892",
)
LOOKUP_UNIT_KEYS = (
    "adapter_select_helper",
    "lookup_adapters",
)
LOOKUP_HOOK_ORDER = (
    "overrun_cut_lookup",
    "overrun_restore_lookup",
    "ignition_lookup_493e8",
    "ignition_lookup_4e1c0_a",
    "ignition_lookup_4e1c0_b",
    "fuel_compensation_lookup_3be3c",
    "fuel_targets_lookup",
    "fuel_compensation_lookup_2c648",
)
PASSIVE_UNIT_KEYS = (
    "selector_host",
    "cruise_feedback_wrapper",
    "cruise_feedback_engine",
)


class LookupOverlayError(ValueError):
    """Raised when a lookup overlay violates its exact chain contract."""


@dataclass(frozen=True)
class OverlaySpec:
    sequence: int
    key: str
    filename_suffix: str
    component_kind: str
    hook_key: str | None
    active_hook_keys: tuple[str, ...]


_HOOK_STAGE_DATA = (
    (7, "overrun_cut_hook", "overrun-cut-hook-4fdd0", LOOKUP_HOOK_ORDER[0]),
    (
        8,
        "overrun_restore_hook",
        "overrun-restore-hook-50258",
        LOOKUP_HOOK_ORDER[1],
    ),
    (9, "ignition_hook_496c0", "ignition-hook-496c0", LOOKUP_HOOK_ORDER[2]),
    (
        10,
        "ignition_hook_4e474",
        "ignition-hook-4e474",
        LOOKUP_HOOK_ORDER[3],
    ),
    (
        11,
        "ignition_hook_4e58c",
        "ignition-hook-4e58c",
        LOOKUP_HOOK_ORDER[4],
    ),
    (
        12,
        "fuel_compensation_hook_3c388",
        "fuel-comp-hook-3c388",
        LOOKUP_HOOK_ORDER[5],
    ),
    (
        13,
        "fuel_targets_hook_c0020",
        "fuel-targets-hook-c0020",
        LOOKUP_HOOK_ORDER[6],
    ),
    (
        14,
        "fuel_compensation_startup_hook_2cf1c",
        "fuel-comp-startup-hook-2cf1c",
        LOOKUP_HOOK_ORDER[7],
    ),
)


OVERLAY_SPECS = (
    OverlaySpec(
        sequence=6,
        key="lookup_payload_map1",
        filename_suffix="lookup-payload-map1",
        component_kind="payload",
        hook_key=None,
        active_hook_keys=(),
    ),
    *tuple(
        OverlaySpec(
            sequence=sequence,
            key=key,
            filename_suffix=filename_suffix,
            component_kind="hook",
            hook_key=hook_key,
            active_hook_keys=LOOKUP_HOOK_ORDER[: sequence - 6],
        )
        for sequence, key, filename_suffix, hook_key in _HOOK_STAGE_DATA
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
    return source.with_name(f"{stem}-map-switching-overlay-v2")


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
    return prefix.with_name(f"{prefix.name}-lookup.sha256")


def _hook_by_key(layout, key):
    try:
        return next(hook for hook in layout.hooks if hook.key == key)
    except StopIteration as error:
        raise LookupOverlayError(f"layout has no hook {key!r}") from error


def _lookup_families(layout):
    families = tuple(
        family for family in layout.families if family.access_kind == "adapter"
    )
    if len(families) != 6:
        raise LookupOverlayError(
            f"layout has {len(families)} adapter families, expected 6"
        )
    if any(family.adapter is None for family in families):
        raise LookupOverlayError("adapter family has no adapter code region")
    return families


def _lookup_storage_offsets(layout):
    copy_offsets = set()
    pointer_offsets = set()
    for family in _lookup_families(layout):
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


def _payload_offsets(layout):
    unit_offsets = set()
    for key in LOOKUP_UNIT_KEYS:
        unit = layout.assembly_unit_by_key[key]
        unit_offsets.update(range(unit.span.start, unit.span.end))
    copy_offsets, pointer_offsets = _lookup_storage_offsets(layout)
    return unit_offsets | copy_offsets | pointer_offsets


def _component_offsets(layout, spec):
    if spec.component_kind == "payload":
        return _payload_offsets(layout)
    if spec.component_kind == "hook" and spec.hook_key is not None:
        hook = _hook_by_key(layout, spec.hook_key)
        return set(range(hook.address, hook.address + hook.width))
    raise LookupOverlayError(f"unsupported component for {spec.key}")


def _materialize_lookup_storage(layout, source, patched):
    for family in _lookup_families(layout):
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


def _require_lookup_storage(layout, source, data, context):
    for family in _lookup_families(layout):
        map_1 = source[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for slot, address in enumerate(family.copies, 2):
            actual = data[address : address + family.byte_length]
            if actual != map_1:
                raise LookupOverlayError(
                    f"{context}: {family.key} Map {slot} differs from Map 1"
                )
        expected_pointers = b"".join(
            address.to_bytes(4, layout.byte_order)
            for address in family.all_slot_addresses
        )
        start = family.pointer_table
        actual_pointers = data[
            start : start + layout.pointer_table_size
        ]
        if actual_pointers != expected_pointers:
            raise LookupOverlayError(
                f"{context}: {family.key} pointer table differs"
            )


def _require_payloads(layout, data, payloads, context):
    for key in LOOKUP_UNIT_KEYS:
        unit = layout.assembly_unit_by_key[key]
        actual = data[unit.span.start : unit.span.end]
        if actual != payloads[key]:
            raise LookupOverlayError(f"{context}: {key} payload differs")


def _require_hooks(layout, data, active_lookup_hook_keys, context):
    active_lookup_hook_keys = set(active_lookup_hook_keys)
    if not active_lookup_hook_keys <= set(LOOKUP_HOOK_ORDER):
        raise LookupOverlayError(f"{context}: unknown active lookup hook set")
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        active = (
            hook.key == "startup_initializer"
            or hook.key in limiter_gate.LIMITER_HOOK_KEYS
            or hook.key in active_lookup_hook_keys
        )
        expected = hook.replacement if active else hook.stock
        if actual != expected:
            raise LookupOverlayError(
                f"{context}: {hook.key} at {hook.address:#x} is "
                f"{actual:#x}, expected {expected:#x}"
            )


def _require_source_contract(layout, source, payloads, source_name):
    digest = limiter_gate.sha256(source)
    if len(source) != limiter_gate.ROM_SIZE:
        raise LookupOverlayError(
            f"{source_name}: source has {len(source)} bytes, expected "
            f"{limiter_gate.ROM_SIZE}"
        )
    try:
        checksums.require_valid(source, source_name)
    except checksums.ChecksumError as error:
        raise LookupOverlayError(str(error)) from error
    if source[
        limiter_gate.RESET_SELECTOR_LINE_START :
        limiter_gate.RESET_SELECTOR_LINE_END
    ] != bytes(128):
        raise LookupOverlayError("source reset-selector line is not all zero")
    if source[
        limiter_gate.STARTUP_WRAPPER_START :
        limiter_gate.STARTUP_WRAPPER_END
    ] != payloads["startup_wrapper"]:
        raise LookupOverlayError("source startup-wrapper payload differs")
    if source[
        limiter_gate.LIMITER_COMMIT_START :
        limiter_gate.LIMITER_COMMIT_END
    ] != payloads["limiter_commit"]:
        raise LookupOverlayError("source limiter-commit payload differs")
    try:
        limiter_gate._require_limiter_storage(layout, source, source)
        limiter_gate._require_stock_anchors(layout, source, source_name)
    except limiter_gate.LimiterGateError as error:
        raise LookupOverlayError(str(error)) from error
    _require_hooks(layout, source, (), source_name)
    return digest


def _apply_component(layout, base, current, payloads, spec):
    patched = bytearray(current)
    if spec.component_kind == "payload":
        for key in LOOKUP_UNIT_KEYS:
            unit = layout.assembly_unit_by_key[key]
            patched[unit.span.start : unit.span.end] = payloads[key]
        _materialize_lookup_storage(layout, base, patched)
    elif spec.component_kind == "hook" and spec.hook_key is not None:
        hook = _hook_by_key(layout, spec.hook_key)
        patched[hook.address : hook.address + hook.width] = (
            hook.replacement.to_bytes(hook.width, layout.byte_order)
        )
    else:
        raise LookupOverlayError(f"unsupported component for {spec.key}")
    return checksums.recalculate(patched)


def _require_stage_contract(
    layout,
    base,
    data,
    payloads,
    spec,
    cumulative_component_offsets,
):
    context = f"lookup overlay {spec.sequence:02d} {spec.key}"
    try:
        checksums.require_valid(data, context)
    except checksums.ChecksumError as error:
        raise LookupOverlayError(str(error)) from error
    if data[
        limiter_gate.STARTUP_WRAPPER_START :
        limiter_gate.STARTUP_WRAPPER_END
    ] != payloads["startup_wrapper"]:
        raise LookupOverlayError(f"{context}: startup wrapper differs")
    if data[
        limiter_gate.LIMITER_COMMIT_START :
        limiter_gate.LIMITER_COMMIT_END
    ] != payloads["limiter_commit"]:
        raise LookupOverlayError(f"{context}: limiter commit differs")
    try:
        limiter_gate._require_limiter_storage(layout, base, data)
    except limiter_gate.LimiterGateError as error:
        raise LookupOverlayError(str(error)) from error
    _require_payloads(layout, data, payloads, context)
    _require_lookup_storage(layout, base, data, context)
    _require_hooks(layout, data, spec.active_hook_keys, context)
    try:
        limiter_gate._require_stock_anchors(layout, data, context)
    except limiter_gate.LimiterGateError as error:
        raise LookupOverlayError(str(error)) from error

    for key in PASSIVE_UNIT_KEYS:
        unit = layout.assembly_unit_by_key[key]
        if data[unit.span.start : unit.span.end] != base[
            unit.span.start : unit.span.end
        ]:
            raise LookupOverlayError(f"{context}: passive unit {key} differs")

    changed_from_base = {
        offset
        for offset, (before, after) in enumerate(zip(base, data))
        if before != after
    }
    permitted_from_base = cumulative_component_offsets | set(
        checksums.checksum_byte_offsets()
    )
    outside = changed_from_base - permitted_from_base
    if outside:
        raise LookupOverlayError(
            f"{context}: cumulative undeclared byte at {min(outside):#x}"
        )
    return len(changed_from_base)


def _build_final_endpoint(layout, source, payloads):
    patched = bytearray(source)
    for key in LOOKUP_UNIT_KEYS:
        unit = layout.assembly_unit_by_key[key]
        patched[unit.span.start : unit.span.end] = payloads[key]
    _materialize_lookup_storage(layout, source, patched)
    for key in LOOKUP_HOOK_ORDER:
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
    """Return the checked cumulative nine-image lookup overlay chain."""
    layout = layout or layout_model.load_layout()
    source = bytes(source)
    if payloads is None:
        try:
            payloads = file_writer.load_payloads(layout)
        except (OSError, file_writer.PatchError) as error:
            raise LookupOverlayError(str(error)) from error
    required_payloads = {
        "startup_wrapper",
        "limiter_commit",
        *LOOKUP_UNIT_KEYS,
    }
    if not required_payloads <= set(payloads):
        raise LookupOverlayError(
            "lookup overlay payload set is incomplete; missing="
            f"{sorted(required_payloads - set(payloads))}"
        )
    source_digest = _require_source_contract(
        layout, source, payloads, source_name
    )
    if expected_source_sha256 is not None and source_digest != expected_source_sha256:
        raise LookupOverlayError(
            f"{source_name}: source sha256 is {source_digest}, expected "
            f"{expected_source_sha256}"
        )

    if expected_output_sha256 is not None:
        if len(expected_output_sha256) != len(OVERLAY_SPECS):
            raise LookupOverlayError(
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
        patched = bytes(
            _apply_component(layout, source, current, payloads, spec)
        )
        digest = limiter_gate.sha256(patched)
        if expected_digest is not None and digest != expected_digest:
            raise LookupOverlayError(
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
            raise LookupOverlayError(
                f"overlay {spec.sequence:02d} changed undeclared byte "
                f"at {min(outside):#x}"
            )
        component_changed = len(changed & component_offsets)
        if component_changed == 0:
            raise LookupOverlayError(
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
                output_md5=file_writer.md5(patched),
                changed_bytes=len(changed),
                component_changed_bytes=component_changed,
                checksum_changed_bytes=len(changed & checksum_offsets),
                permitted_write_bytes=len(permitted),
                cumulative_changed_bytes=cumulative_changed,
            )
        )
        current = patched

    if current != _build_final_endpoint(layout, source, payloads):
        raise LookupOverlayError(
            "final overlay differs from the combined lookup endpoint"
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
        raise LookupOverlayError(f"existing output differs: {path}")


def write_overlays(prefix, results):
    """Write a preflighted chain, MD5 sidecars, and ordered SHA manifest."""
    paths = output_paths(prefix)
    if len(results) != len(paths):
        raise LookupOverlayError("result count differs from output count")
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
        created += int(file_writer.write_output(path, result.data))
        created += int(file_writer.write_md5_sidecar(path, result.data))
    if not manifest.exists():
        manifest.write_bytes(manifest_bytes)
        created += 1
    return paths, manifest, created


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input", type=Path, help="exact successful limiter Overlay 05 ROM"
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
    except (OSError, LookupOverlayError) as error:
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
            f"cumulative_changed_bytes={result.cumulative_changed_bytes}"
        )
    print(
        "final_equals_combined_lookup_endpoint=true "
        "selector_host=absent can_feedback=absent checksums=PASS"
    )

    if args.verify_only:
        print("no ROM files were written")
        return 0

    prefix = args.output_prefix or default_output_prefix(args.input)
    try:
        paths, manifest, created = write_overlays(prefix, results)
    except (OSError, LookupOverlayError, file_writer.PatchError) as error:
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
