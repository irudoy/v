#!/usr/bin/env python3
"""Independently assemble and lock telemetry or relocated runtime payloads."""

from __future__ import annotations

import argparse
from dataclasses import replace
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
from patches import map_switching_assembly
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout
from patches import runtime_targets


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


def build_telemetry():
    """Reconstruct the canonical manifest with the existing GNU unit assembler."""
    layout = can_telemetry_layout.load_layout()
    can_telemetry_layout.validate_structure(layout)
    parsed = can_telemetry_assembly.validate_assembly_sources(layout)
    with tempfile.TemporaryDirectory(prefix="vq-telemetry-payloads-") as directory:
        blobs = _assemble(layout, parsed, Path(directory), canonical=True)
    can_telemetry_assembly.validate_instruction_semantics(layout, parsed, blobs)
    can_telemetry_compose.compose(layout=layout, blobs=blobs)
    return can_telemetry_assembly.render_payloads(layout, blobs)


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
    args = parser.parse_args(argv)
    output = args.output or (
        can_telemetry_assembly.DEFAULT_PAYLOADS if args.telemetry
        else runtime_targets.DEFAULT_PAYLOADS
    )
    if args.telemetry:
        content = build_telemetry()
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
