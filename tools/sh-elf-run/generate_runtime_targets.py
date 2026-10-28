#!/usr/bin/env python3
"""Independently assemble and lock Rolling Launch, telemetry, or relocated payloads."""

from __future__ import annotations

import argparse
from dataclasses import replace
import os
from pathlib import Path
import sys
import tempfile


TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
for item in (TOOL_DIR, ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import verify_map_switching

from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import can_telemetry_locks
from patches import map_switching_assembly
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout
from patches import runtime_targets

TELEMETRY_UPDATE_COMMAND = "tools/sh-elf-run/generate-targets.sh --telemetry --update"


def _assemble(layout, parsed_by_unit, build_dir, *, canonical=False):
    result = {}
    source_texts = layout.source_text_by_unit
    for unit in layout.assembly_units:
        result[unit.key] = verify_map_switching.assemble_unit(
            unit,
            parsed_by_unit[unit.key],
            build_dir,
            source_text=None if canonical else source_texts[unit.key],
        )
    return result


def build_rolling():
    """Reconstruct the canonical manifest with the existing GNU unit assembler."""
    layout = rolling_launch_layout.load_layout()
    rolling_launch_layout.validate_structure(layout)
    parsed = rolling_launch_assembly.validate_assembly_sources(layout)
    with tempfile.TemporaryDirectory(prefix="vq-rolling-payloads-") as directory:
        blobs = _assemble(layout, parsed, Path(directory), canonical=True)
    rolling_launch_assembly.validate_instruction_semantics(layout, parsed, blobs)
    rolling_launch_compose.compose(layout=layout, blobs=blobs)
    return rolling_launch_assembly.render_payloads(layout, blobs)


def _derive_telemetry(layout, assemble):
    """Assemble the telemetry units and derive their locks.

    The unit counts come from the sources, so the full source validation runs
    before the assembled bytes are compared with any lock.
    """
    working = can_telemetry_locks.counted(layout)
    parsed = can_telemetry_assembly.validate_assembly_sources(working)
    with tempfile.TemporaryDirectory(prefix="vq-telemetry-payloads-") as directory:
        blobs = assemble(working, parsed, Path(directory), canonical=True)
    return parsed, blobs, can_telemetry_locks.derive(working, parsed, blobs)


def _checked_telemetry(layout, assemble):
    """Return the manifest of ``layout`` when the assembled bytes keep its locks."""
    parsed, blobs, locks = _derive_telemetry(layout, assemble)
    stale = can_telemetry_locks.changes(layout, locks)
    if stale:
        raise can_telemetry_locks.LockError(
            "telemetry locks differ from the assembled payloads: "
            + ", ".join(field for field, _declared, _derived in stale)
            + f"; after an intentional change run {TELEMETRY_UPDATE_COMMAND}"
        )
    can_telemetry_assembly.validate_instruction_semantics(layout, parsed, blobs)
    can_telemetry_compose.compose(layout=layout, blobs=blobs)
    return can_telemetry_assembly.render_payloads(layout, blobs)


def build_telemetry():
    """Reconstruct the canonical manifest with the existing GNU unit assembler."""
    layout = can_telemetry_layout.load_layout()
    can_telemetry_layout.validate_structure(layout)
    return _checked_telemetry(layout, _assemble)


def update_telemetry(layout, layout_text, assemble=None):
    """Derive the telemetry locks and return the layout text and manifest.

    Returns ``(layout_text, manifest, changes)``. The layout text differs in
    its lock values alone; the reloaded layout then passes the strict path
    that ``--check`` runs.
    """
    assemble = assemble or _assemble
    can_telemetry_layout.validate_structure(layout)
    _parsed, _blobs, locks = _derive_telemetry(layout, assemble)
    rendered = can_telemetry_locks.render(
        layout_text, locks, can_telemetry_layout.DEFAULT_MANIFEST.name
    )
    updated = replace(
        can_telemetry_locks.load_text(rendered), source_texts=layout.source_texts
    )
    can_telemetry_layout.validate_structure(updated)
    manifest = _checked_telemetry(updated, assemble)
    return rendered, manifest, can_telemetry_locks.changes(layout, locks)


def _replace_files(contents):
    """Write every changed file to a sibling temporary file, then replace them."""
    staged = []
    try:
        for path, content in contents.items():
            encoded = content.encode("utf-8")
            if path.exists() and path.read_bytes() == encoded:
                continue
            descriptor, name = tempfile.mkstemp(
                prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
            )
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(encoded)
            staged.append((Path(name), path))
        for temporary, path in staged:
            os.replace(temporary, path)
    finally:
        for temporary, _path in staged:
            temporary.unlink(missing_ok=True)


def build_locks(rom):
    projected = runtime_targets.project_relocated_target(rom)
    map_switching_layout.validate_structure(projected.map_layout)
    if projected.rolling_layout is not None:
        rolling_launch_layout.validate_structure(projected.rolling_layout)
    can_telemetry_layout.validate_structure(projected.telemetry_layout)
    map_parsed = map_switching_assembly.validate_assembly_sources(
        projected.map_layout
    )
    rolling_parsed = (
        rolling_launch_assembly.validate_assembly_sources(
            projected.rolling_layout
        )
        if projected.rolling_layout is not None
        else None
    )
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        projected.telemetry_layout
    )

    with tempfile.TemporaryDirectory(
        prefix=f"vq-runtime-target-{rom.lower()}-"
    ) as directory:
        build_dir = Path(directory)
        map_payloads = _assemble(
            projected.map_layout, map_parsed, build_dir
        )
        rolling_payloads = (
            _assemble(projected.rolling_layout, rolling_parsed, build_dir)
            if projected.rolling_layout is not None
            else {}
        )
        telemetry_payloads = _assemble(
            projected.telemetry_layout, telemetry_parsed, build_dir
        )

    provisional = runtime_targets.PayloadLocks(
        rom=rom,
        stock_sha256=runtime_targets._sha256(
            projected.stock_image.data
        ),
        map_stage_sha256=runtime_targets.ZERO_SHA256,
        rolling_stage_sha256=runtime_targets.ZERO_SHA256,
        telemetry_stage_sha256=runtime_targets.ZERO_SHA256,
        map_payloads=map_payloads,
        rolling_payloads=rolling_payloads,
        telemetry_payloads=telemetry_payloads,
    )
    target = runtime_targets.project_relocated_target(rom, provisional)
    map_switching_layout.validate_structure(target.map_layout)
    if target.rolling_layout is not None:
        rolling_launch_layout.validate_structure(target.rolling_layout)
    can_telemetry_layout.validate_structure(target.telemetry_layout)
    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    rolling_parsed = (
        rolling_launch_assembly.validate_assembly_sources(
            target.rolling_layout
        )
        if target.rolling_layout is not None
        else None
    )
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    map_switching_assembly.validate_instruction_semantics(
        target.map_layout, map_parsed, map_payloads
    )
    if target.rolling_layout is not None:
        rolling_launch_assembly.validate_instruction_semantics(
            target.rolling_layout, rolling_parsed, rolling_payloads
        )
    can_telemetry_assembly.validate_instruction_semantics(
        target.telemetry_layout, telemetry_parsed, telemetry_payloads
    )

    map_result = map_switching_compose.compose(
        layout=target.map_layout,
        image=target.stock_image,
        blobs=map_payloads,
    )
    rolling_result = None
    if target.rolling_layout is not None:
        launch_layout = replace(
            target.rolling_layout,
            base_composition_sha256=map_result.sha256,
        )
        rolling_result = rolling_launch_compose.compose(
            layout=launch_layout,
            base=map_result.data,
            blobs=rolling_payloads,
        )
    telemetry_base = (
        rolling_result.data if rolling_result is not None else map_result.data
    )
    telemetry_base_sha256 = (
        rolling_result.sha256
        if rolling_result is not None
        else map_result.sha256
    )
    telemetry_layout = replace(
        target.telemetry_layout,
        base_composition_sha256=telemetry_base_sha256,
    )
    telemetry_result = can_telemetry_compose.compose(
        layout=telemetry_layout,
        base=telemetry_base,
        blobs=telemetry_payloads,
    )
    return replace(
        provisional,
        map_stage_sha256=map_result.sha256,
        rolling_stage_sha256=telemetry_base_sha256,
        telemetry_stage_sha256=telemetry_result.sha256,
    )


def _hex_block(data):
    value = data.hex()
    return "\n".join(
        value[index : index + 64]
        for index in range(0, len(value), 64)
    )


def render(locks):
    lines = [
        "# Generated by make runtime-targets-generate. Do not edit.",
        "# Payloads are independently assembled with GNU SH-2E binutils.",
        "",
        "schema_version = 1",
    ]
    for item in locks:
        lines.extend([
            "",
            f"[target.{item.rom}]",
            f'stock_sha256 = "{item.stock_sha256}"',
            f'map_stage_sha256 = "{item.map_stage_sha256}"',
            f'rolling_stage_sha256 = "{item.rolling_stage_sha256}"',
            f'telemetry_stage_sha256 = "{item.telemetry_stage_sha256}"',
        ])
        for label, payloads in (
            ("map_units", item.map_payloads),
            ("rolling_units", item.rolling_payloads),
            ("telemetry_units", item.telemetry_payloads),
        ):
            lines.extend(["", f"[target.{item.rom}.{label}]"])
            for key, data in payloads.items():
                lines.extend([
                    f'{key} = """',
                    _hex_block(data),
                    '"""',
                ])
    return "\n".join(lines) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        help="manifest destination (defaults to the selected payload family)",
    )
    parser.add_argument("--check", action="store_true")
    parser.add_argument(
        "--telemetry", action="store_true",
        help="reconstruct canonical JK08A telemetry instead of relocated targets",
    )
    parser.add_argument(
        "--rolling", action="store_true",
        help="reconstruct canonical JK08A Rolling Launch instead of relocated targets",
    )
    parser.add_argument(
        "--update", action="store_true",
        help=(
            "with --telemetry, derive the layout locks from the assembled units "
            "and rewrite them with the manifest"
        ),
    )
    args = parser.parse_args(argv)
    if args.rolling and args.telemetry:
        parser.error("--rolling and --telemetry are mutually exclusive")
    if args.update and (not args.telemetry or args.check):
        parser.error("--update requires --telemetry and excludes --check")
    output = args.output or (
        rolling_launch_assembly.DEFAULT_PAYLOADS if args.rolling
        else can_telemetry_assembly.DEFAULT_PAYLOADS if args.telemetry
        else runtime_targets.DEFAULT_PAYLOADS
    )
    if args.update:
        layout_path = can_telemetry_layout.DEFAULT_MANIFEST
        try:
            layout_text, content, changed = update_telemetry(
                can_telemetry_layout.load_layout(layout_path),
                layout_path.read_text(encoding="utf-8"),
            )
        except ValueError as error:
            parser.error(str(error))
        _replace_files({layout_path: layout_text, output: content})
        for field, declared, derived in changed:
            print(f"lock {field}: {declared} -> {derived}")
        print(
            f"status=PASS output={output} layout={layout_path} "
            f"family=telemetry changed_locks={len(changed)}"
        )
        return 0
    if args.rolling:
        content = build_rolling()
        scope = "family=rolling"
    elif args.telemetry:
        try:
            content = build_telemetry()
        except can_telemetry_locks.LockError as error:
            parser.error(str(error))
        scope = "family=telemetry"
    else:
        content = render([
            build_locks(rom) for rom in runtime_targets.RELOCATED_ROMS
        ])
        scope = f"targets={len(runtime_targets.RELOCATED_ROMS)}"
    encoded = content.encode("utf-8")
    if args.check:
        try:
            current = output.read_bytes()
        except OSError as error:
            parser.error(str(error))
        if current != encoded:
            parser.error(f"generated payloads differ: {output}")
        print(f"status=PASS output={output} {scope}")
        return 0
    output.write_bytes(encoded)
    print(f"status=PASS output={output} {scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
