#!/usr/bin/env python3
"""Verify exact JK08A CAN telemetry instructions with GNU SH-2E tools."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import sys
import tempfile


TOOL_DIR = Path(__file__).resolve().parent
if str(TOOL_DIR) not in sys.path:
    sys.path.insert(0, str(TOOL_DIR))

ROOT = TOOL_DIR.parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import verify_map_switching as base_verifier
import verify_rolling_launch as rolling_verifier

from patches import can_telemetry
from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import map_switching_assembly
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_layout


EXPECTED_COMPOSITION_SHA256 = (
    "567f7e67166cd87ddbc99e33aafde292598a08887960bb27b3c50e78459a8adb"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 1922
EXPECTED_COMPOSITION_WRITE_BYTES = 3488
EXPECTED_INSTRUCTION_COUNT = 720
EXPECTED_CODE_ENTRY_COUNT = 11
REQUIRED_DYNAMIC_MARKER = (
    "VQ_SH_ELF_CAN_TELEMETRY status=PASS cases=78 entries=11 "
    "profiles=1 contexts=10 isr_rte=5"
)
HARNESS_SOURCE = TOOL_DIR / "can_telemetry_harness.c"
HARNESS_CONFIGURATION = re.compile(
    r"static const uint8_t configuration\[16\] = \{(?P<bytes>[^}]*)\};"
)
RETURN_STUB = bytes.fromhex("000b0009")
RETURN_ONE_STUB = bytes.fromhex("e001000b0009")
# Simulator-only staging block of the knock evaluator stub inside the test RAM
# window: destination address, 32-bit value, call count.
EVALUATOR_STAGE_ADDRESS = 0x0100FF00
EVALUATOR_STUB_CODE = bytes.fromhex(
    "d105621253112232501270011102e4ffe5ffe6ff000be7ff"
)
TRAPA_VECTOR_ADDRESS = 0x00000100


class VerificationError(RuntimeError):
    """Raised when the CAN telemetry executable contract fails."""


def assemble_all_units(layout, parsed_by_unit, build_dir, verbose=False):
    """GNU-assemble every telemetry unit and require tracked identity."""
    tracked = can_telemetry_assembly.load_payloads(layout)
    assembled = {}
    for unit in layout.assembly_units:
        blob = base_verifier.assemble_unit(
            unit, parsed_by_unit[unit.key], build_dir
        )
        digest = hashlib.sha256(blob).hexdigest()
        if blob != tracked[unit.key]:
            first = next(
                index
                for index, pair in enumerate(zip(blob, tracked[unit.key]))
                if pair[0] != pair[1]
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
                f"GNU_ASSEMBLY can_telemetry_unit={unit.key} "
                f"bytes={len(blob)} sha256={digest}"
            )
        assembled[unit.key] = blob
    return assembled


def require_composition(layout, blobs):
    result = can_telemetry_compose.compose(layout=layout, blobs=blobs)
    actual = (
        result.sha256,
        result.changed_bytes,
        result.permitted_write_bytes,
        result.instruction_count,
        result.code_entry_count,
    )
    expected = (
        EXPECTED_COMPOSITION_SHA256,
        EXPECTED_COMPOSITION_CHANGED_BYTES,
        EXPECTED_COMPOSITION_WRITE_BYTES,
        EXPECTED_INSTRUCTION_COUNT,
        EXPECTED_CODE_ENTRY_COUNT,
    )
    if actual != expected:
        raise VerificationError(
            f"CAN telemetry composition differs: actual={actual} "
            f"expected={expected}"
        )
    return result


def knock_evaluator_stub(address):
    """Build the simulator-only stand-in of the stock knock slice evaluator.

    The stub stores the staged value at the staged destination, counts the
    call, overwrites r0 through r7, and returns. The harness stages the
    offset-binary metric of the evaluated channel, so a wrapper that reads the
    channel state before the stock call observes the stale metric instead.
    """
    if address % 4:
        raise VerificationError(
            f"knock evaluator stub is not aligned at {address:#x}"
        )
    return EVALUATOR_STUB_CODE + EVALUATOR_STAGE_ADDRESS.to_bytes(4, "big")


def install_stock_return_stubs(fixture, layout):
    """Stub only the five external stock callees reached by this gate."""
    hooks = layout.hook_by_key
    targets = {
        hooks["coherent_snapshot_call"].stock,
        hooks["knock_interval_latch"].stock,
        hooks["hcan1_primary_init"].stock,
        0x000C6B68,
    }
    expected = {0x00020DFE, 0x000493E8, 0x000C338A, 0x000C6B68}
    if targets != expected:
        raise VerificationError(
            f"CAN telemetry stock stub targets differ: {sorted(targets)}"
        )
    for address in targets:
        stub = RETURN_ONE_STUB if address == 0x000C338A else RETURN_STUB
        fixture[address : address + len(stub)] = stub
    evaluator = hooks["knock_margin_latch"].stock
    if evaluator != 0x0004A238 or evaluator in targets:
        raise VerificationError(
            f"knock evaluator stub target differs: {evaluator:#x}"
        )
    stub = knock_evaluator_stub(evaluator)
    fixture[evaluator : evaluator + len(stub)] = stub
    return len(targets) + 1


def relocate_telemetry_ram_literals(fixture, parsed_by_unit):
    """Relocate validated single and generated multi-value RAM literals."""
    relocated = 0
    for parsed in parsed_by_unit.values():
        for statement in parsed.statements:
            if statement.kind != "long":
                continue
            values = [
                int(item.strip().replace("_", ""), 0)
                for item in statement.text.split(",")
            ]
            if statement.size != len(values) * 4:
                raise VerificationError(
                    f"literal width differs at {statement.address:#x}"
                )
            for index, value in enumerate(values):
                if value < base_verifier.HIGH_RAM_BASE:
                    continue
                address = statement.address + index * 4
                encoded = value.to_bytes(4, "big")
                if fixture[address : address + 4] != encoded:
                    raise VerificationError(
                        f"RAM literal differs at {address:#x}"
                    )
                fixture[address : address + 4] = (
                    base_verifier.alias_high_ram(value).to_bytes(4, "big")
                )
                relocated += 1
    return relocated


def build_dynamic_fixture(
    composition,
    base_layout,
    launch_layout,
    telemetry_layout,
    telemetry_parsed,
):
    """Apply documented simulator-only relocations and stock stubs."""
    fixture = bytearray(composition.data)
    base_parsed = map_switching_assembly.validate_assembly_sources(
        base_layout
    )
    launch_parsed = rolling_launch_assembly.validate_assembly_sources(
        launch_layout
    )
    base_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, base_parsed
    )
    launch_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, launch_parsed
    )
    telemetry_relocated = relocate_telemetry_ram_literals(
        fixture, telemetry_parsed
    )
    differentiated = base_verifier.differentiate_map_copies(
        fixture, base_layout
    )
    lower_stubs = rolling_verifier.install_stock_return_stubs(
        fixture, base_layout, launch_layout
    )
    telemetry_stubs = install_stock_return_stubs(
        fixture, telemetry_layout
    )
    fixture[TRAPA_VECTOR_ADDRESS : TRAPA_VECTOR_ADDRESS + 4] = (
        telemetry_layout.code_region_by_key["sle1_isr"].entry.to_bytes(
            4, "big"
        )
    )
    return (
        bytes(fixture),
        base_relocated,
        launch_relocated,
        telemetry_relocated,
        differentiated,
        lower_stubs + telemetry_stubs,
    )


def build_rom_object(fixture, build_dir):
    fixture_path = build_dir / "can-telemetry.sim-fixture"
    object_path = build_dir / "can-telemetry-rom.o"
    fixture_path.write_bytes(fixture)
    base_verifier.run_command([
        base_verifier.OBJCOPY,
        "-I", "binary",
        "-O", "elf32-sh",
        "-B", "sh",
        "--rename-section",
        ".data=.rom,alloc,load,code,data,contents",
        fixture_path,
        object_path,
    ])
    return object_path


def build_and_run_dynamic_harness(fixture, build_dir):
    rom_object = build_rom_object(fixture, build_dir)
    invoke_object = build_dir / "can-telemetry-invoke.o"
    exception_object = build_dir / "can-telemetry-exception.o"
    harness_elf = build_dir / "can-telemetry-harness.elf"
    base_verifier.run_command([
        base_verifier.AS,
        "--big", "--isa=sh2e",
        "-o", invoke_object,
        TOOL_DIR / "invoke.s",
    ])
    base_verifier.run_command([
        base_verifier.AS,
        "--big", "--isa=sh2e",
        "-o", exception_object,
        TOOL_DIR / "invoke_exception.s",
    ])
    base_verifier.run_command(
        [
            base_verifier.GCC,
            "-m2e", "-mb", "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror",
            f"-Wl,-Ttext-segment={base_verifier.DRIVER_TEXT_BASE:#x}",
            "-Wl,--section-start=.rom=0",
            "-o", harness_elf,
            TOOL_DIR / "can_telemetry_harness.c",
            invoke_object,
            exception_object,
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
    if REQUIRED_DYNAMIC_MARKER not in result.stdout:
        raise VerificationError(
            "CAN telemetry harness returned zero without the exact marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    return result.stdout.strip()


def marker_cases(output):
    """Read the case count a harness reports about itself."""
    counts = re.findall(r"\bcases=(\d+)\b", output)
    if len(counts) != 1:
        raise VerificationError(
            "a harness output reports its case count exactly once, "
            f"this one reports it {len(counts)} times"
        )
    return int(counts[0])


def require_harness_configuration():
    """Require the harness fixture to be the manifest configuration record."""
    manifest = can_telemetry_profile.load_manifest()
    if len(manifest.profiles) != 1:
        raise VerificationError(
            "the harness fixture stands for exactly one profile"
        )
    expected = can_telemetry.Configuration(
        enabled=True,
        can_id=manifest.candidate_can_id,
        profile=manifest.profiles[0].name,
        tick_divisor=manifest.candidate_tick_divisor,
    ).to_bytes(manifest)
    source = HARNESS_SOURCE.read_text(encoding="utf-8")
    match = HARNESS_CONFIGURATION.search(source)
    if match is None:
        raise VerificationError(
            f"{HARNESS_SOURCE.name} declares no 16-byte configuration fixture"
        )
    carried = bytes(
        int(item, 0)
        for item in match.group("bytes").replace("\n", " ").split(",")
        if item.strip()
    )
    if carried != expected:
        raise VerificationError(
            f"{HARNESS_SOURCE.name} configuration fixture is "
            f"{carried.hex()}, the manifest requires {expected.hex()}"
        )
    return expected


def verify(verbose=False, check_toolchain=True):
    simulator = None
    gcc_version = None
    if check_toolchain:
        simulator, gcc_version = base_verifier.require_toolchain_version()
    base_layout = map_switching_layout.load_layout()
    launch_layout = rolling_launch_layout.load_layout()
    telemetry_layout = can_telemetry_layout.load_layout()
    parsed = can_telemetry_assembly.validate_assembly_sources(
        telemetry_layout
    )
    require_harness_configuration()
    with tempfile.TemporaryDirectory(
        prefix="vq-sh-elf-can-telemetry-"
    ) as directory:
        build_dir = Path(directory)
        blobs = assemble_all_units(
            telemetry_layout, parsed, build_dir, verbose=verbose
        )
        audit = can_telemetry_assembly.validate_instruction_semantics(
            telemetry_layout, parsed, blobs
        )
        composition = require_composition(telemetry_layout, blobs)
        (
            fixture,
            base_relocated,
            launch_relocated,
            telemetry_relocated,
            differentiated,
            stubs,
        ) = build_dynamic_fixture(
            composition,
            base_layout,
            launch_layout,
            telemetry_layout,
            parsed,
        )
        dynamic_marker = build_and_run_dynamic_harness(
            fixture, build_dir
        )
    dynamic_cases = marker_cases(dynamic_marker)
    print(dynamic_marker)
    print(
        "VQ_SH_ELF_CAN_TELEMETRY_VERIFY status=PASS"
        f" units={len(telemetry_layout.assembly_units)}"
        f" instructions={audit.instructions}"
        f" delayed_transfers={audit.delayed_transfers}"
        f" pc_relative_references={audit.pc_relative_references}"
        f" direct_branches={audit.direct_branches}"
        f" indirect_transfers={audit.indirect_transfers}"
        f" composition_sha256={composition.sha256}"
        f" dynamic_cases={dynamic_cases}"
        f" base_ram_literals_relocated={base_relocated}"
        f" rolling_ram_literals_relocated={launch_relocated}"
        f" telemetry_ram_literals_relocated={telemetry_relocated}"
        f" differentiated_bytes={differentiated}"
        f" stock_stubs={stubs}"
        f" trapa_vector={TRAPA_VECTOR_ADDRESS:#x}"
    )
    if verbose and simulator is not None:
        print(f"CAN_TELEMETRY_TOOLCHAIN {simulator} gcc={gcc_version}")
    return {
        "composition": composition,
        "audit": audit,
        "dynamic_cases": dynamic_cases,
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
            f"VQ_SH_ELF_CAN_TELEMETRY_VERIFY status=FAIL error={error}",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
