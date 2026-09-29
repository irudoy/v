#!/usr/bin/env python3
"""Verify exact JK08A Rolling Launch instructions with GNU SH-2E tools."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys
import tempfile


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

ROOT = TOOL_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import verify_map_switching as base_verifier

from patches import map_switching_assembly
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout


EXPECTED_COMPOSITION_SHA256 = (
    "4e59f3a291af4e636ee1caf8588632b1b2a6468fcd5bdbc4af3d31a121d0a811"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 1976
EXPECTED_COMPOSITION_WRITE_BYTES = 2328
EXPECTED_INSTRUCTION_COUNT = 878
EXPECTED_CODE_ENTRY_COUNT = 8
EXPECTED_DIAGNOSTIC_COUNT = 9
EXPECTED_DYNAMIC_CASES = 122
RETURN_STUB = bytes.fromhex("000b0009")
FEEDBACK_SERIALIZER_STUB = bytes.fromhex(
    "d103e0b52100000b00090009000901003ada"
)


class VerificationError(RuntimeError):
    """Raised when the Rolling Launch executable contract fails."""


def assemble_all_units(layout, parsed_by_unit, build_dir, verbose=False):
    """GNU-assemble every new unit and require tracked byte identity."""
    tracked = rolling_launch_assembly.load_payloads(layout)
    assembled = {}
    for unit in layout.assembly_units:
        blob = base_verifier.assemble_unit(
            unit, parsed_by_unit[unit.key], build_dir
        )
        digest = hashlib.sha256(blob).hexdigest()
        if blob != tracked[unit.key]:
            first = next(
                index
                for index, (actual, expected) in enumerate(
                    zip(blob, tracked[unit.key])
                )
                if actual != expected
            )
            raise VerificationError(
                f"{unit.key}: GNU output differs from tracked payload at "
                f"ROM address {unit.span.start + first:#x}"
            )
        if digest != unit.expected_sha256:
            raise VerificationError(
                f"{unit.key}: GNU SHA-256 is {digest}, expected "
                f"{unit.expected_sha256}"
            )
        if verbose:
            print(
                f"GNU_ASSEMBLY rolling_launch_unit={unit.key} "
                f"bytes={len(blob)} sha256={digest}"
            )
        assembled[unit.key] = blob
    return assembled


def require_composition(layout, blobs):
    """Compose and lock the non-flashable Rolling Launch endpoint."""
    result = rolling_launch_compose.compose(layout=layout, blobs=blobs)
    actual = (
        result.sha256,
        result.changed_bytes,
        result.permitted_write_bytes,
        result.instruction_count,
        result.code_entry_count,
        result.diagnostic_count,
    )
    expected = (
        EXPECTED_COMPOSITION_SHA256,
        EXPECTED_COMPOSITION_CHANGED_BYTES,
        EXPECTED_COMPOSITION_WRITE_BYTES,
        EXPECTED_INSTRUCTION_COUNT,
        EXPECTED_CODE_ENTRY_COUNT,
        EXPECTED_DIAGNOSTIC_COUNT,
    )
    if actual != expected:
        raise VerificationError(
            f"Rolling Launch composition differs: actual={actual} "
            f"expected={expected}"
        )
    return result


def install_stock_return_stubs(fixture, base_layout, rolling_layout):
    """Stub external stock callees reached by Rolling Launch tests."""
    base_hooks = {hook.key: hook for hook in base_layout.hooks}
    rolling_hooks = rolling_layout.hook_by_key
    targets = {
        base_hooks["selector_host_call"].stock,
        base_hooks["startup_initializer"].stock,
        rolling_hooks["displaced_periodic_task"].stock,
        rolling_hooks["primary_ignition_command"].stock,
    }
    expected = {0x000D09D8, 0x0002C648, 0x000A9554, 0x0002A892}
    if targets != expected:
        raise VerificationError(
            f"Rolling Launch stock stub targets differ: {sorted(targets)}"
        )
    for address in targets:
        fixture[address : address + len(RETURN_STUB)] = RETURN_STUB
    serializer = base_hooks["cruise_feedback_serializer"].stock
    if serializer != 0x000C5372:
        raise VerificationError(
            f"feedback serializer target differs: {serializer:#x}"
        )
    fixture[
        serializer : serializer + len(FEEDBACK_SERIALIZER_STUB)
    ] = FEEDBACK_SERIALIZER_STUB
    return len(targets) + 1


def build_dynamic_fixture(
    composition,
    rolling_parsed,
    base_layout,
    rolling_layout,
):
    """Apply documented simulator-only transformations after byte identity."""
    fixture = bytearray(composition.data)
    if len(fixture) != base_verifier.ROM_SIZE:
        raise VerificationError(
            f"composition size is {len(fixture)}, expected "
            f"{base_verifier.ROM_SIZE}"
        )
    base_parsed = map_switching_assembly.validate_assembly_sources(
        base_layout
    )
    base_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, base_parsed
    )
    rolling_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, rolling_parsed
    )
    differentiated = base_verifier.differentiate_map_copies(
        fixture, base_layout
    )
    stubs = install_stock_return_stubs(
        fixture, base_layout, rolling_layout
    )
    return (
        bytes(fixture),
        base_relocated,
        rolling_relocated,
        differentiated,
        stubs,
    )


def build_rom_object(fixture, build_dir):
    fixture_path = build_dir / "rolling-launch.sim-fixture"
    object_path = build_dir / "rolling-launch-rom.o"
    fixture_path.write_bytes(fixture)
    base_verifier.run_command([
        base_verifier.OBJCOPY,
        "-I",
        "binary",
        "-O",
        "elf32-sh",
        "-B",
        "sh",
        "--rename-section",
        ".data=.rom,alloc,load,code,data,contents",
        fixture_path,
        object_path,
    ])
    return object_path


def build_and_run_dynamic_harness(fixture, build_dir):
    """Execute state, gate, output, and wrapper behavior cases."""
    rom_object = build_rom_object(fixture, build_dir)
    invoke_object = build_dir / "rolling-launch-invoke.o"
    harness_elf = build_dir / "rolling-launch-harness.elf"
    base_verifier.run_command([
        base_verifier.AS,
        "--big",
        "--isa=sh2e",
        "-o",
        invoke_object,
        TOOL_DIR / "invoke.s",
    ])
    base_verifier.run_command(
        [
            base_verifier.GCC,
            "-m2e",
            "-mb",
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            f"-Wl,-Ttext-segment={base_verifier.DRIVER_TEXT_BASE:#x}",
            "-Wl,--section-start=.rom=0",
            "-o",
            harness_elf,
            TOOL_DIR / "rolling_launch_harness.c",
            invoke_object,
            rom_object,
        ],
        timeout=120,
    )
    result = base_verifier.run_command(
        [
            base_verifier.RUN,
            f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k",
            harness_elf,
        ],
        timeout=180,
    )
    marker = (
        "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=122 "
        "structural=11 gates=27 config=24 threshold=4 activation=5 "
        "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 entries=8"
    )
    if marker not in result.stdout:
        raise VerificationError(
            "Rolling Launch harness returned zero without the exact marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    return result.stdout.strip()


def verify(verbose=False, check_toolchain=True):
    simulator = None
    gcc_version = None
    if check_toolchain:
        simulator, gcc_version = base_verifier.require_toolchain_version()
    base_layout = map_switching_layout.load_layout()
    rolling_layout = rolling_launch_layout.load_layout()
    parsed = rolling_launch_assembly.validate_assembly_sources(
        rolling_layout
    )
    with tempfile.TemporaryDirectory(
        prefix="vq-sh-elf-rolling-launch-"
    ) as directory:
        build_dir = Path(directory)
        blobs = assemble_all_units(
            rolling_layout, parsed, build_dir, verbose=verbose
        )
        audit = rolling_launch_assembly.validate_instruction_semantics(
            rolling_layout, parsed, blobs
        )
        composition = require_composition(rolling_layout, blobs)
        (
            fixture,
            base_relocated,
            rolling_relocated,
            differentiated,
            stubs,
        ) = build_dynamic_fixture(
            composition,
            parsed,
            base_layout,
            rolling_layout,
        )
        dynamic_marker = build_and_run_dynamic_harness(
            fixture, build_dir
        )

    print(dynamic_marker)
    print(
        "VQ_SH_ELF_ROLLING_VERIFY status=PASS"
        f" units={len(rolling_layout.assembly_units)}"
        f" instructions={audit.instructions}"
        f" delayed_transfers={audit.delayed_transfers}"
        f" pc_relative_references={audit.pc_relative_references}"
        f" direct_branches={audit.direct_branches}"
        f" indirect_transfers={audit.indirect_transfers}"
        f" composition_sha256={composition.sha256}"
        f" dynamic_cases={EXPECTED_DYNAMIC_CASES}"
        f" diagnostics={composition.diagnostic_count}"
        f" base_ram_literals_relocated={base_relocated}"
        f" rolling_ram_literals_relocated={rolling_relocated}"
        f" differentiated_bytes={differentiated}"
        f" stock_stubs={stubs}"
    )
    if verbose and simulator is not None:
        print(f"ROLLING_TOOLCHAIN {simulator} gcc={gcc_version}")
    return {
        "composition": composition,
        "audit": audit,
        "dynamic_cases": EXPECTED_DYNAMIC_CASES,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="print each independently assembled unit digest",
    )
    args = parser.parse_args(argv)
    try:
        verify(verbose=args.verbose)
    except (OSError, ValueError, VerificationError) as error:
        print(
            f"VQ_SH_ELF_ROLLING_VERIFY status=FAIL error={error}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
