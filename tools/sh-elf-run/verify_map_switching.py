#!/usr/bin/env python3
"""Verify the complete JK08A map-switching implementation with GNU SH tools.

The verifier independently assembles every tracked source with GNU binutils,
requires byte identity with the SHA-locked Ghidra payloads, composes the exact
one-MiB verification fixture, and executes all implementation code entries in
GNU sh-elf-run. It also executes the exact failed Overlay 07 BRA/MOV.L pair at
its original addresses and requires the simulator's illegal-instruction stop.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching
from patches import jk08a_checksums as checksums
from patches import map_switching_assembly as assembly_model
from patches import map_switching_compose as composer
from patches import map_switching_layout as layout_model


TOOL_DIR = Path(__file__).resolve().parent
EXPECTED_SIMULATOR_VERSION = "16.3"
EXPECTED_COMPOSITION_SHA256 = (
    "7eb703d38eef2ab51cd4a2b2b28a7a80e24d475debc1b8ddf69b6ccd7e96b222"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 5803
EXPECTED_COMPOSITION_WRITE_BYTES = 6316
EXPECTED_INSTRUCTION_COUNT = 435
EXPECTED_CODE_ENTRY_COUNT = 12
EXPECTED_DYNAMIC_CASES = 131
TEST_RAM_BASE = 0x01000000
HIGH_RAM_BASE = 0xFFFF0000
ROM_SIZE = 0x00100000
DRIVER_TEXT_BASE = 0x00110000
RETURN_STUB = bytes.fromhex("000b0009")
INCIDENT_ADDRESS = 0x000D2314
INCIDENT_BRANCH_WORD = 0xAFAC
INCIDENT_UNSAFE_SLOT_WORD = 0xD304
INCIDENT_SAFE_SLOT_WORD = 0x0009

AS = "sh-elf-as"
LD = "sh-elf-ld"
OBJCOPY = "sh-elf-objcopy"
GCC = "sh-elf-gcc"
RUN = "sh-elf-run"


class VerificationError(RuntimeError):
    """Raised when a tool or an executable verification contract fails."""


def run_command(
    command,
    *,
    cwd=None,
    input_text=None,
    expected_returncode=0,
    timeout=60,
):
    """Run one command and return its completed process or raise."""
    display = " ".join(str(item) for item in command)
    try:
        result = subprocess.run(
            [str(item) for item in command],
            cwd=cwd,
            input=input_text,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except FileNotFoundError as error:
        raise VerificationError(f"required tool is missing: {command[0]}") \
            from error
    except subprocess.TimeoutExpired as error:
        raise VerificationError(
            f"command timed out after {timeout}s: {display}"
        ) from error
    if result.returncode != expected_returncode:
        details = "\n".join(
            part.rstrip()
            for part in (result.stdout, result.stderr)
            if part.strip()
        )
        raise VerificationError(
            f"command returned {result.returncode}, expected "
            f"{expected_returncode}: {display}"
            + (f"\n{details}" if details else "")
        )
    return result


def preprocess_gnu_source(source):
    """Translate the small Ghidra source dialect to GNU assembler syntax."""
    result = []
    for raw_line in source.splitlines():
        line = raw_line.split("//", 1)[0]
        match = re.match(r"^(\s*)\.align\s+(.+?)\s*$", line)
        if match:
            line = f"{match.group(1)}.balign {match.group(2)}"
        immediate = re.match(
            r"^(\s*)(add|and|cmp/eq|or|tst|xor)\s+"
            r"(?P<value>-?(?:0x[0-9a-f]+|[0-9]+)),",
            line,
            re.IGNORECASE,
        )
        if immediate:
            start, end = immediate.span("value")
            line = line[:start] + "#" + line[start:end] + line[end:]
        result.append(line)
    return "\n".join(result) + "\n"


def _source_value(statement):
    values = [item.strip() for item in statement.text.split(",")]
    if len(values) != 1:
        raise VerificationError(
            f"expected one value at {statement.address:#x}: "
            f"{statement.text}"
        )
    return int(values[0].replace("_", ""), 0)


def assemble_unit(unit, parsed, build_dir):
    """Assemble one absolute source and reconstruct its fill-aware blob."""
    source_path = ROOT / "patches" / unit.source
    object_path = build_dir / f"{unit.key}.o"
    elf_path = build_dir / f"{unit.key}.elf"
    binary_path = build_dir / f"{unit.key}.raw"
    source = preprocess_gnu_source(source_path.read_text(encoding="utf-8"))

    run_command(
        [AS, "--big", "--isa=sh2e", "-o", object_path, "-"],
        input_text=source,
    )
    run_command(
        [
            LD,
            "-EB",
            "-Ttext=0",
            "--entry=0",
            "-o",
            elf_path,
            object_path,
        ]
    )
    run_command([OBJCOPY, "-O", "binary", elf_path, binary_path])
    raw = binary_path.read_bytes()
    blob = bytearray([unit.fill] * unit.span.size)
    for statement in parsed.statements:
        source_end = statement.address + statement.size
        if source_end > len(raw):
            raise VerificationError(
                f"{unit.key}: GNU binary ends before {source_end:#x}"
            )
        destination = statement.address - unit.span.start
        blob[destination : destination + statement.size] = raw[
            statement.address : source_end
        ]
    return bytes(blob)


def assemble_all_units(layout, parsed_by_unit, build_dir, verbose=False):
    """Build all units independently and require tracked payload identity."""
    tracked = apply_map_switching.load_payloads(layout)
    assembled = {}
    for unit in layout.assembly_units:
        blob = assemble_unit(unit, parsed_by_unit[unit.key], build_dir)
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
                f"{unit.key}: GNU output differs from the tracked payload "
                f"at ROM address {unit.span.start + first:#x}"
            )
        if digest != unit.expected_sha256:
            raise VerificationError(
                f"{unit.key}: GNU SHA-256 is {digest}, expected "
                f"{unit.expected_sha256}"
            )
        if verbose:
            print(
                f"GNU_ASSEMBLY unit={unit.key} bytes={len(blob)} "
                f"sha256={digest}"
            )
        assembled[unit.key] = blob
    return assembled


def require_composition(layout, blobs):
    """Build and lock the complete non-flashable verification composition."""
    result = composer.compose(layout=layout, blobs=blobs)
    expected = (
        EXPECTED_COMPOSITION_SHA256,
        EXPECTED_COMPOSITION_CHANGED_BYTES,
        EXPECTED_COMPOSITION_WRITE_BYTES,
        EXPECTED_INSTRUCTION_COUNT,
        EXPECTED_CODE_ENTRY_COUNT,
    )
    actual = (
        result.sha256,
        result.changed_bytes,
        result.permitted_write_bytes,
        result.instruction_count,
        result.code_entry_count,
    )
    if actual != expected:
        raise VerificationError(
            f"composition contract differs: actual={actual} expected={expected}"
        )
    return result


def alias_high_ram(value):
    """Map an exact SH7058S high-RAM address into simulator test RAM."""
    if value < HIGH_RAM_BASE or value > 0xFFFFFFFF:
        raise VerificationError(f"not a high-RAM address: {value:#x}")
    return TEST_RAM_BASE + (value - HIGH_RAM_BASE)


def relocate_assembly_ram_literals(fixture, parsed_by_unit):
    """Relocate only validated assembly data literals, never instructions."""
    relocated = 0
    for parsed in parsed_by_unit.values():
        for statement in parsed.statements:
            if statement.kind != "long":
                continue
            value = _source_value(statement)
            if value < HIGH_RAM_BASE:
                continue
            encoded = value.to_bytes(4, "big")
            address = statement.address
            if fixture[address : address + 4] != encoded:
                raise VerificationError(
                    f"RAM literal at {address:#x} differs before relocation"
                )
            fixture[address : address + 4] = alias_high_ram(value).to_bytes(
                4, "big"
            )
            relocated += 1
    return relocated


def differentiate_map_copies(fixture, layout):
    """Give dynamic-only map copies distinct bytes to expose wrong slots."""
    changed = 0
    for family_index, family in enumerate(layout.families, 1):
        for slot_index, address in enumerate(family.copies, 1):
            for offset in range(family.byte_length):
                fixture[address + offset] = (
                    fixture[address + offset]
                    + family_index * 17
                    + slot_index * 29
                    + offset
                ) & 0xFF
                changed += 1
    return changed


def install_stock_return_stubs(fixture, layout):
    """Replace only documented external stock callees with RTS/NOP."""
    keys = {
        "selector_host_call",
        "startup_initializer",
        "overrun_cut_lookup",
        "overrun_restore_lookup",
        "ignition_lookup_493e8",
        "ignition_lookup_4e1c0_a",
        "ignition_lookup_4e1c0_b",
        "fuel_compensation_lookup_2c648",
        "fuel_compensation_lookup_3be3c",
        "fuel_targets_lookup",
        "idle_ignition_lookup",
        "cruise_feedback_serializer",
    }
    hooks = {hook.key: hook for hook in layout.hooks}
    if not keys <= hooks.keys():
        raise VerificationError(
            f"layout lacks stock-call hooks: {sorted(keys - hooks.keys())}"
        )
    targets = {hooks[key].stock for key in keys}
    for address in targets:
        fixture[address : address + len(RETURN_STUB)] = RETURN_STUB
    return len(targets)


def build_dynamic_fixture(composition, layout, parsed_by_unit):
    """Create a simulator-only fixture after the exact composition passes."""
    fixture = bytearray(composition.data)
    if len(fixture) != ROM_SIZE:
        raise VerificationError(
            f"composition size is {len(fixture)}, expected {ROM_SIZE}"
        )
    relocated = relocate_assembly_ram_literals(fixture, parsed_by_unit)
    differentiated = differentiate_map_copies(fixture, layout)
    stubs = install_stock_return_stubs(fixture, layout)
    return bytes(fixture), relocated, differentiated, stubs


def build_rom_object(fixture, build_dir):
    fixture_path = build_dir / "map-switching.sim-fixture"
    object_path = build_dir / "map-switching-rom.o"
    fixture_path.write_bytes(fixture)
    run_command(
        [
            OBJCOPY,
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
        ]
    )
    return object_path


def build_and_run_dynamic_harness(fixture, build_dir):
    """Execute all map-switching behavior cases in the GNU simulator."""
    rom_object = build_rom_object(fixture, build_dir)
    invoke_object = build_dir / "invoke.o"
    harness_elf = build_dir / "map-switching-harness.elf"
    run_command(
        [
            AS,
            "--big",
            "--isa=sh2e",
            "-o",
            invoke_object,
            TOOL_DIR / "invoke.s",
        ]
    )
    run_command(
        [
            GCC,
            "-m2e",
            "-mb",
            "-std=c11",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            f"-Wl,-Ttext-segment={DRIVER_TEXT_BASE:#x}",
            "-Wl,--section-start=.rom=0",
            "-o",
            harness_elf,
            TOOL_DIR / "map_switching_harness.c",
            invoke_object,
            rom_object,
        ],
        timeout=120,
    )
    result = run_command(
        [
            RUN,
            f"--memory-region={TEST_RAM_BASE:#x},64k",
            harness_elf,
        ],
        timeout=120,
    )
    marker = (
        "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=131 selector=17 "
        "adapters=91 limiter=14 feedback=9 feedback_invocations=17 "
        "entries=12"
    )
    if marker not in result.stdout:
        raise VerificationError(
            "dynamic harness returned zero without the exact PASS marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    return result.stdout.strip()


def build_delay_slot_probe(slot_word, name, build_dir):
    object_path = build_dir / f"delay-slot-{name}.o"
    elf_path = build_dir / f"delay-slot-{name}.elf"
    section_path = build_dir / f"delay-slot-{name}.incident"
    run_command(
        [
            AS,
            "--big",
            "--isa=sh2e",
            "--defsym",
            f"SLOT_WORD={slot_word:#x}",
            "-o",
            object_path,
            TOOL_DIR / "delay_slot_probe.s",
        ]
    )
    run_command(
        [
            GCC,
            "-m2e",
            "-mb",
            "-Wl,--section-start=.incident_target=0x000d2270",
            "-Wl,--section-start=.hardware_literal=0x000d2280",
            "-Wl,--section-start=.incident=0x000d2314",
            "-Wl,--section-start=.static_literal=0x000d2328",
            "-o",
            elf_path,
            TOOL_DIR / "delay_slot_main.c",
            object_path,
        ]
    )
    run_command(
        [
            OBJCOPY,
            "--dump-section",
            f".incident={section_path}",
            elf_path,
        ]
    )
    expected = INCIDENT_BRANCH_WORD.to_bytes(2, "big") + slot_word.to_bytes(
        2, "big"
    )
    actual = section_path.read_bytes()
    if actual != expected:
        raise VerificationError(
            f"{name} incident bytes are {actual.hex()}, expected "
            f"{expected.hex()}"
        )
    return elf_path


def verify_delay_slot_incident(build_dir):
    """Require safe control success and exact incident SIGILL behavior."""
    safe_elf = build_delay_slot_probe(
        INCIDENT_SAFE_SLOT_WORD, "safe", build_dir
    )
    unsafe_elf = build_delay_slot_probe(
        INCIDENT_UNSAFE_SLOT_WORD, "unsafe", build_dir
    )
    run_command([RUN, safe_elf])
    result = run_command(
        [RUN, unsafe_elf], expected_returncode=4, timeout=30
    )
    output = result.stdout + result.stderr
    if "signal 4 (Illegal instruction)" not in output:
        raise VerificationError(
            "unsafe delay-slot probe returned 4 without the SIGILL marker"
        )
    return 4


def require_toolchain_version():
    result = run_command([RUN, "--version"])
    first_line = result.stdout.splitlines()[0]
    if not first_line.endswith(f" {EXPECTED_SIMULATOR_VERSION}"):
        raise VerificationError(
            f"simulator version is {first_line!r}, expected "
            f"{EXPECTED_SIMULATOR_VERSION}"
        )
    gcc = run_command([GCC, "-dumpfullversion"]).stdout.strip()
    return first_line, gcc


def verify(verbose=False):
    simulator, gcc_version = require_toolchain_version()
    layout = layout_model.load_layout()
    parsed_by_unit = assembly_model.validate_assembly_sources(layout)
    with tempfile.TemporaryDirectory(prefix="vq-sh-elf-run-") as directory:
        build_dir = Path(directory)
        blobs = assemble_all_units(
            layout, parsed_by_unit, build_dir, verbose=verbose
        )
        audit = assembly_model.validate_instruction_semantics(
            layout, parsed_by_unit, blobs
        )
        composition = require_composition(layout, blobs)
        fixture, relocated, differentiated, stubs = build_dynamic_fixture(
            composition, layout, parsed_by_unit
        )
        dynamic_marker = build_and_run_dynamic_harness(fixture, build_dir)
        incident_signal = verify_delay_slot_incident(build_dir)

    print(dynamic_marker)
    try:
        import verify_rolling_launch

        rolling_result = verify_rolling_launch.verify(
            verbose=verbose, check_toolchain=False
        )
    except Exception as error:
        raise VerificationError(
            f"Rolling Launch executable gate failed: {error}"
        ) from error
    try:
        import verify_can_telemetry

        telemetry_result = verify_can_telemetry.verify(
            verbose=verbose, check_toolchain=False
        )
    except Exception as error:
        raise VerificationError(
            f"CAN telemetry executable gate failed: {error}"
        ) from error
    print(
        "VQ_SH_ELF_VERIFY status=PASS"
        f" simulator={EXPECTED_SIMULATOR_VERSION}"
        f" gcc={gcc_version}"
        f" units={len(layout.assembly_units)}"
        f" instructions={audit.instructions}"
        f" delayed_transfers={audit.delayed_transfers}"
        f" pc_relative_references={audit.pc_relative_references}"
        f" direct_branches={audit.direct_branches}"
        f" indirect_transfers={audit.indirect_transfers}"
        f" composition_sha256={composition.sha256}"
        f" dynamic_cases={EXPECTED_DYNAMIC_CASES}"
        f" rolling_launch_instructions="
        f"{rolling_result['audit'].instructions}"
        f" rolling_launch_cases={rolling_result['dynamic_cases']}"
        f" can_telemetry_instructions="
        f"{telemetry_result['audit'].instructions}"
        f" can_telemetry_cases={telemetry_result['dynamic_cases']}"
        f" ram_literals_relocated={relocated}"
        f" differentiated_bytes={differentiated}"
        f" stock_stubs={stubs}"
        f" incident_address={INCIDENT_ADDRESS:#x}"
        f" unsafe_signal={incident_signal}"
    )
    if verbose:
        print(f"TOOLCHAIN {simulator}")


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
        print(f"VQ_SH_ELF_VERIFY status=FAIL error={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
