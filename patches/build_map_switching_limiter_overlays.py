#!/usr/bin/env python3
"""Build cumulative atomic JK08A limiter overlays for hardware isolation.

Every output is a complete one-MiB ROM suitable for a normal PCMFlash write.
The chain starts from the exact successful selector-init readback and adds one
functional component per image: inactive limiter payload and storage, startup
execution, then each of the three direct limiter-shadow hooks. No intermediate
hardware readback is used as an input to the next image.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching as file_writer
from patches import build_map_switching_limiter as limiter_gate
from patches import jk08a_checksums as checksums
from patches import map_switching_layout as layout_model


SOURCE_STEM_SUFFIX = "-startup-selector-init-d22a0_readback"
EXPECTED_OUTPUT_SHA256 = (
    "9bb1704f93a6050593abbf30b450cc1b75bc4d141ed4455b7528148de69f56c4",
    "135512525ed64b7728348a2b8859e9a7b607f931f57f6a7951e0d2d7dc847da5",
    "22f824be2e9ca941b42760de27accc7cd1c7365e23a0b19eda29387fd1dd196c",
    "3aa4bce11eb9030dc688c04744170e8aee61b1b9f8e3dd99a57a4d5ca1f626db",
    limiter_gate.HARDWARE_OUTPUT_SHA256,
)


class LimiterOverlayError(ValueError):
    """Raised when an overlay or its cumulative chain violates the contract."""


@dataclass(frozen=True)
class OverlaySpec:
    sequence: int
    key: str
    filename_suffix: str
    component_kind: str
    hook_key: str | None
    active_hook_keys: tuple[str, ...]


OVERLAY_SPECS = (
    OverlaySpec(
        sequence=1,
        key="payload_map1",
        filename_suffix="payload-map1",
        component_kind="payload",
        hook_key=None,
        active_hook_keys=(),
    ),
    OverlaySpec(
        sequence=2,
        key="startup_commit",
        filename_suffix="startup-commit",
        component_kind="startup",
        hook_key=None,
        active_hook_keys=(),
    ),
    OverlaySpec(
        sequence=3,
        key="fuel_hook",
        filename_suffix="fuel-hook-4f468",
        component_kind="hook",
        hook_key="rev_fuel_cut_base",
        active_hook_keys=("rev_fuel_cut_base",),
    ),
    OverlaySpec(
        sequence=4,
        key="throttle_cluster_hook",
        filename_suffix="throttle-cluster-hook-75964",
        component_kind="hook",
        hook_key="rev_throttle_cluster_base",
        active_hook_keys=(
            "rev_fuel_cut_base",
            "rev_throttle_cluster_base",
        ),
    ),
    OverlaySpec(
        sequence=5,
        key="throttle_scalar_hook",
        filename_suffix="throttle-scalar-hook-77bac",
        component_kind="hook",
        hook_key="rev_throttle_scalar_base",
        active_hook_keys=(
            "rev_fuel_cut_base",
            "rev_throttle_cluster_base",
            "rev_throttle_scalar_base",
        ),
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
    if stem.endswith(SOURCE_STEM_SUFFIX):
        stem = stem[: -len(SOURCE_STEM_SUFFIX)]
    return source.with_name(f"{stem}-limiter-overlay")


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
    return prefix.with_name(f"{prefix.name}.sha256")


def _hook_by_key(layout, key):
    try:
        return next(hook for hook in layout.hooks if hook.key == key)
    except StopIteration as error:
        raise LimiterOverlayError(f"layout has no hook {key!r}") from error


def _payload_offsets(layout):
    copy_offsets, pointer_offsets = limiter_gate._limiter_storage_offsets(
        layout
    )
    return (
        set(
            range(
                limiter_gate.LIMITER_COMMIT_START,
                limiter_gate.LIMITER_COMMIT_END,
            )
        )
        | copy_offsets
        | pointer_offsets
    )


def _component_offsets(layout, spec):
    if spec.component_kind == "payload":
        return _payload_offsets(layout)
    if spec.component_kind == "startup":
        return set(
            range(
                limiter_gate.STARTUP_WRAPPER_START,
                limiter_gate.STARTUP_WRAPPER_END,
            )
        )
    if spec.component_kind == "hook" and spec.hook_key is not None:
        hook = _hook_by_key(layout, spec.hook_key)
        return set(range(hook.address, hook.address + hook.width))
    raise LimiterOverlayError(f"unsupported component for {spec.key}")


def _require_hooks(layout, data, active_hook_keys, context):
    active_hook_keys = set(active_hook_keys)
    if not active_hook_keys <= limiter_gate.LIMITER_HOOK_KEYS:
        raise LimiterOverlayError(
            f"{context}: unknown active limiter hook set"
        )
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        active = hook.key == "startup_initializer" or (
            hook.key in active_hook_keys
        )
        expected = hook.replacement if active else hook.stock
        if actual != expected:
            raise LimiterOverlayError(
                f"{context}: {hook.key} at {hook.address:#x} is "
                f"{actual:#x}, expected {expected:#x}"
            )


def _apply_component(layout, base, current, payloads, spec):
    patched = bytearray(current)
    if spec.component_kind == "payload":
        patched[
            limiter_gate.LIMITER_COMMIT_START :
            limiter_gate.LIMITER_COMMIT_END
        ] = payloads["limiter_commit"]
        limiter_gate._materialize_limiter_storage(layout, base, patched)
    elif spec.component_kind == "startup":
        patched[
            limiter_gate.STARTUP_WRAPPER_START :
            limiter_gate.STARTUP_WRAPPER_END
        ] = payloads["startup_wrapper"]
    elif spec.component_kind == "hook" and spec.hook_key is not None:
        hook = _hook_by_key(layout, spec.hook_key)
        patched[hook.address : hook.address + hook.width] = (
            hook.replacement.to_bytes(hook.width, layout.byte_order)
        )
    else:
        raise LimiterOverlayError(f"unsupported component for {spec.key}")
    return checksums.recalculate(patched)


def _require_stage_contract(
    layout,
    base,
    data,
    payloads,
    spec,
    cumulative_component_offsets,
):
    context = f"limiter overlay {spec.sequence:02d} {spec.key}"
    try:
        verification = checksums.require_valid(data, context)
    except checksums.ChecksumError as error:
        raise LimiterOverlayError(str(error)) from error
    if not verification.valid:
        raise LimiterOverlayError(f"{context}: checksum verification failed")

    if data[
        limiter_gate.LIMITER_COMMIT_START :
        limiter_gate.LIMITER_COMMIT_END
    ] != payloads["limiter_commit"]:
        raise LimiterOverlayError(f"{context}: limiter payload differs")
    limiter_gate._require_limiter_storage(layout, base, data)

    startup = data[
        limiter_gate.STARTUP_WRAPPER_START :
        limiter_gate.STARTUP_WRAPPER_END
    ]
    if spec.sequence == 1:
        expected_startup = base[
            limiter_gate.STARTUP_WRAPPER_START :
            limiter_gate.STARTUP_WRAPPER_END
        ]
    else:
        expected_startup = payloads["startup_wrapper"]
    if startup != expected_startup:
        raise LimiterOverlayError(f"{context}: startup payload differs")

    _require_hooks(layout, data, spec.active_hook_keys, context)
    limiter_gate._require_stock_anchors(layout, data, context)
    if data[
        limiter_gate.MARKER_LINE_START :
        limiter_gate.STARTUP_WRAPPER_START
    ] != bytes(
        limiter_gate.STARTUP_WRAPPER_START
        - limiter_gate.MARKER_LINE_START
    ):
        raise LimiterOverlayError(f"{context}: marker prefix differs")

    changed_from_base = {
        offset
        for offset, (before, after) in enumerate(zip(base, data))
        if before != after
    }
    permitted_from_base = (
        cumulative_component_offsets
        | set(checksums.checksum_byte_offsets())
    )
    outside = changed_from_base - permitted_from_base
    if outside:
        raise LimiterOverlayError(
            f"{context}: cumulative undeclared byte at {min(outside):#x}"
        )
    return len(changed_from_base)


def build_overlays(
    source,
    layout=None,
    payloads=None,
    source_name="<memory>",
    expected_source_sha256=limiter_gate.HARDWARE_READBACK_SHA256,
    expected_output_sha256=EXPECTED_OUTPUT_SHA256,
):
    """Return the checked cumulative five-image limiter overlay chain."""
    layout = layout or layout_model.load_layout()
    source = bytes(source)
    if payloads is None:
        payloads = limiter_gate.load_gate_payloads(layout)
    try:
        combined = limiter_gate.build_image(
            source,
            layout=layout,
            payloads=payloads,
            source_name=source_name,
            expected_source_sha256=expected_source_sha256,
        )
    except limiter_gate.LimiterGateError as error:
        raise LimiterOverlayError(str(error)) from error

    if expected_output_sha256:
        if len(expected_output_sha256) != len(OVERLAY_SPECS):
            raise LimiterOverlayError(
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
            raise LimiterOverlayError(
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
            raise LimiterOverlayError(
                f"overlay {spec.sequence:02d} changed undeclared byte "
                f"at {min(outside):#x}"
            )
        component_changed = len(changed & component_offsets)
        if component_changed == 0:
            raise LimiterOverlayError(
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

    if current != combined.data:
        raise LimiterOverlayError(
            "final overlay differs from the combined limiter gate"
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
        raise LimiterOverlayError(f"existing output differs: {path}")


def write_overlays(prefix, results):
    """Write a preflighted chain, MD5 sidecars, and ordered SHA manifest."""
    paths = output_paths(prefix)
    if len(results) != len(paths):
        raise LimiterOverlayError("result count differs from output count")
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
        "input", type=Path, help="exact successful selector-init readback ROM"
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
    except (OSError, LimiterOverlayError) as error:
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
    print("final_equals_combined_limiter_gate=true checksums=PASS")

    if args.verify_only:
        print("no ROM files were written")
        return 0

    prefix = args.output_prefix or default_output_prefix(args.input)
    try:
        paths, manifest, created = write_overlays(prefix, results)
    except (OSError, LimiterOverlayError, file_writer.PatchError) as error:
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
