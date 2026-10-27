#!/usr/bin/env python3
"""Verify exact JK08A CAN telemetry instructions with GNU SH-2E tools."""

from __future__ import annotations

import argparse
import hashlib
import os
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
from elf_storage_layout import ELFStorageError, require_separate_storage

from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import map_switching_assembly
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_layout


EXPECTED_COMPOSITION_SHA256 = (
    "151d522d71c56d88a5a2dd29fc7611325dca99fb3a6ce55a039b5a0a962a674b"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 1922
EXPECTED_COMPOSITION_WRITE_BYTES = 3488
EXPECTED_INSTRUCTION_COUNT = 720
EXPECTED_CODE_ENTRY_COUNT = 11
REQUIRED_DYNAMIC_MARKER = (
    "VQ_SH_ELF_CAN_TELEMETRY status=PASS cases=80 entries=11 "
    "profiles=1 contexts=10 isr_rte=5"
)
HARNESS_SOURCE = TOOL_DIR / "can_telemetry_harness.c"
HARNESS_INCLUDE_DIR = ROOT / "patches"
# The harness takes its configuration fixture from the generated identity
# header, whose freshness the profile generator checks.
HARNESS_CONFIGURATION = (
    f'#include "{can_telemetry_profile.DEFAULT_IDENTITY.name}"',
    "static const uint8_t configuration[16] = TELEMETRY_CONFIGURATION;",
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


def require_wrapper_instruction_bytes(fixture, composed, parsed_by_unit):
    """Preserve every independently assembled wrapper word after all stubs."""
    for row in parsed_by_unit["wrappers"].statements:
        if row.kind == "instruction" and fixture[row.address:row.address + 2] != composed[row.address:row.address + 2]:
            raise VerificationError(f"simulator changes CAN wrapper instruction at {row.address:#010x}")


def require_wrapper_coverage(records, fixture, layout, parsed_by_unit, invoke_words):
    """Measure only canonical CAN wrapper entries, loops and call/return paths."""
    parsed = parsed_by_unit["wrappers"]
    entries = {layout.code_region_by_key[key].entry
               for key in layout.assembly_unit_by_key["wrappers"].code_regions}
    instructions, outcomes, slots, call_targets = {}, set(), set(), {}
    for row in parsed.statements:
        if row.kind != "instruction":
            continue
        pc = row.address
        instructions[pc] = int.from_bytes(fixture[pc:pc + 2], "big")
        mnemonic = map_switching_assembly._mnemonic(row)
        if mnemonic in (map_switching_assembly.DIRECT_BRANCH_MNEMONICS
                        | map_switching_assembly.INDIRECT_CONTROL_MNEMONICS) - {"bf", "jsr", "rts"}:
            raise VerificationError(f"unsupported CAN wrapper transfer at {pc:#010x}")
        if mnemonic == "bf":
            target = map_switching_assembly._validate_direct_branch_encoding(parsed, row, instructions[pc])
            outcomes.update(((pc, target), (pc, pc + 2)))
        if mnemonic in {"jsr", "rts"}:
            slots.add(pc + 2)
        if mnemonic == "jsr":
            previous = parsed.statement_by_address.get(pc - 2)
            literal = map_switching_assembly.PC_RELATIVE_RE.fullmatch(previous.text) if previous else None
            if (row.text != "jsr @r0" or literal is None or literal.group("width") != "l"
                    or literal.group("register") != "r0"):
                raise VerificationError(f"unbound CAN wrapper call at {pc:#010x}")
            pool = parsed.labels[literal.group("label")]
            call_targets[pc] = int.from_bytes(fixture[pool:pool + 4], "big")
    if not entries or not entries <= instructions.keys():
        raise VerificationError("CAN wrapper entries lack typed instructions")
    seen, observed_outcomes, observed_slots, returned, call_returns = set(), set(), set(), set(), set()
    frames = []
    for index, (pc, word, delay) in enumerate(records):
        if 0 <= pc < len(fixture) - 1:
            expected = int.from_bytes(fixture[pc:pc + 2], "big")
        elif pc in invoke_words:
            expected = invoke_words[pc]
        else:
            raise VerificationError(f"executed CAN PC outside bound ROM/invoke code at {pc:#010x}")
        if word != expected:
            raise VerificationError(f"executed CAN opcode differs at {pc:#010x}")
        seen.add(pc)
        if delay:
            if not index or records[index - 1][0] != pc - 2 or records[index - 1][2]:
                raise VerificationError(f"orphan CAN delay slot at {pc:#010x}")
            observed_slots.add(pc)
            continue
        if pc in instructions and not frames:
            raise VerificationError(f"CAN wrapper instruction lacks its invoke frame at {pc:#010x}")
        if pc in instructions and word & 0xff00 == 0x8b00:
            observed_outcomes.add((pc, base_verifier._trace_successor(records, index, False)))
        if pc + 2 in slots:
            base_verifier._trace_successor(records, index, True)
        is_call = word & 0xf0ff == 0x400b or word & 0xf000 == 0xb000
        if is_call:
            target = base_verifier._trace_successor(records, index, True)
            if pc in call_targets and target != call_targets[pc]:
                raise VerificationError(f"executed CAN callee differs at {pc:#010x}")
            if not frames and target in entries and pc not in invoke_words:
                raise VerificationError(f"CAN wrapper origin is outside bound invoke code at {pc:#010x}")
            if frames or target in entries:
                frames.append((pc, target, pc + 4))
        elif word == 0x000b and (frames or pc in instructions):
            target = base_verifier._trace_successor(records, index, True)
            if not frames:
                raise VerificationError(f"CAN wrapper return lacks its invoke frame at {pc:#010x}")
            call, entry, continuation = frames.pop()
            if target != continuation:
                raise VerificationError(f"executed CAN return differs at {pc:#010x}")
            if entry in entries:
                returned.add(entry)
            if entry in entries or call in call_targets:
                call_returns.add((call, entry, continuation))
        elif frames and (word == 0x002b or word & 0xff00 == 0xc300
                         or word & 0xf0ff in {0x0003, 0x0023, 0x402b}):
            raise VerificationError(f"unsupported transfer in active CAN wrapper frame at {pc:#010x}")
    for missing in sorted(entries - seen):
        raise VerificationError(f"uncovered CAN wrapper entry {missing:#010x}")
    for pc, target in sorted(outcomes - observed_outcomes):
        raise VerificationError(f"uncovered CAN wrapper outcome {pc:#010x}->{target:#010x}")
    for missing in sorted(instructions.keys() - seen):
        raise VerificationError(f"uncovered CAN wrapper instruction {missing:#010x}")
    if frames or entries - returned or call_targets.keys() - {row[0] for row in call_returns}:
        raise VerificationError("uncovered CAN wrapper call/return path")
    for missing in sorted(slots - observed_slots):
        raise VerificationError(f"uncovered CAN wrapper delay slot {missing:#010x}")
    return dict(entries=len(entries & seen), instructions=len(instructions.keys() & seen),
                outcomes=len(outcomes & observed_outcomes), delay_slots=len(slots & observed_slots),
                call_return_paths=len(call_returns))


def build_and_run_dynamic_harness(fixture, build_dir, *, layout, parsed_by_unit, composed_image):
    require_wrapper_instruction_bytes(fixture, composed_image, parsed_by_unit)
    rom_object = build_rom_object(fixture, build_dir)
    invoke_object = build_dir / "can-telemetry-invoke.o"
    exception_object = build_dir / "can-telemetry-exception.o"
    harness_elf = build_dir / "can-telemetry-harness.elf"
    source = HARNESS_SOURCE.read_text(encoding="utf-8")
    positive_source = build_dir / "can-telemetry-positive.c"
    positive_source.write_text(source, encoding="utf-8")
    base_verifier.run_command([
        base_verifier.AS, "--big", "--isa=sh2e", "-o", invoke_object, TOOL_DIR / "invoke.s",
    ])
    base_verifier.run_command([
        base_verifier.AS, "--big", "--isa=sh2e", "-o", exception_object, TOOL_DIR / "invoke_exception.s",
    ])
    command = [
        base_verifier.GCC, "-m2e", "-mb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
        "-I", HARNESS_INCLUDE_DIR,
        f"-Wl,-Ttext-segment={base_verifier.DRIVER_TEXT_BASE:#x}", "-Wl,--section-start=.rom=0",
        "-o", harness_elf, positive_source, invoke_object, exception_object, rom_object,
    ]
    base_verifier.run_command(command, timeout=120)
    try:
        require_separate_storage(harness_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
    except (ELFStorageError, OSError) as error:
        raise VerificationError(f"can-telemetry: ELF storage separation: {error}") from error

    def execute(elf):
        ranges, invoke_words = base_verifier._invoke_trace_bindings(elf, invoke_object, fixture, build_dir)
        trace = build_dir / f"{elf.stem}.pc-trace"
        environment = {
            **os.environ,
            "VQ_SH_PC_TRACE_FILE": str(trace), "VQ_SH_PC_TRACE_FORMAT": "v1",
            "VQ_SH_PC_TRACE_RANGES": ",".join(
                f"{start:x}:{end:x}" for start, end in ((0, len(fixture)), *ranges)),
        }
        before = elf.read_bytes()
        result = base_verifier.run_command([
            base_verifier.RUN, f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k", elf,
        ], timeout=180, env=environment)
        if elf.read_bytes() != before:
            raise VerificationError("CAN harness ELF changes during execution")
        return result, base_verifier.read_pc_trace(trace), invoke_words

    result, records, invoke_words = execute(harness_elf)
    covered = require_wrapper_coverage(records, fixture, layout, parsed_by_unit, invoke_words)
    if REQUIRED_DYNAMIC_MARKER not in result.stdout:
        raise VerificationError("CAN telemetry harness returned zero without the exact marker")
    call = "(void)invoke_r4(MAIN_WRAPPER, 0);"
    if source.count(call) != 1:
        raise VerificationError("CAN negative lacks its unique main-wrapper invocation")
    negative_text = source.replace(call, "(void)invoke_r4(CONTROL_POLL, 0);\n    (void)invoke_r4(CAPTURE, 0);")
    negative_source = build_dir / "can-telemetry-bypass-main.c"
    negative_source.write_text(negative_text, encoding="utf-8")
    negative_elf = build_dir / "can-telemetry-bypass-main.elf"
    negative_command = list(command)
    negative_command[negative_command.index("-o") + 1] = negative_elf
    negative_command[negative_command.index(positive_source)] = negative_source
    base_verifier.run_command(negative_command, timeout=120)
    require_separate_storage(negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
    negative, records, invoke_words = execute(negative_elf)
    if REQUIRED_DYNAMIC_MARKER not in negative.stdout:
        raise VerificationError("CAN main bypass does not preserve the existing semantic PASS marker")
    reason = f"uncovered CAN wrapper entry {layout.code_region_by_key['main_wrapper'].entry:#010x}"
    try:
        require_wrapper_coverage(records, fixture, layout, parsed_by_unit, invoke_words)
    except VerificationError as error:
        if str(error) != reason:
            raise VerificationError(f"CAN bypass fails outside its omitted entry: {error}") from error
    else:
        raise VerificationError("CAN coverage accepts the bypassed main wrapper")
    if (HARNESS_SOURCE.read_text(encoding="utf-8") != source
            or positive_source.read_text(encoding="utf-8") != source
            or negative_source.read_text(encoding="utf-8") != negative_text):
        raise VerificationError("CAN harness source changes during verification")
    marker = "VQ_SH_ELF_CAN_WRAPPER_COVERAGE status=PASS scope=JK08A:wrappers "
    marker += " ".join(f"{key}={value}" for key, value in covered.items())
    return "\n".join((result.stdout.strip(), marker,
                      "VQ_SH_ELF_CAN_WRAPPER_COVERAGE_NEGATIVE status=PASS " + reason))


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
    """Require the harness fixture to be the generated configuration record."""
    lines = {
        line.strip()
        for line in HARNESS_SOURCE.read_text(encoding="utf-8").splitlines()
    }
    for statement in HARNESS_CONFIGURATION:
        if statement not in lines:
            raise VerificationError(
                f"{HARNESS_SOURCE.name} lacks {statement!r}, the "
                "configuration fixture of the generated identity header"
            )


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
            fixture, build_dir, layout=telemetry_layout, parsed_by_unit=parsed,
            composed_image=composition.data,
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
