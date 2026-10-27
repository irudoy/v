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
    "96ab4fad355be6e97ebf9361712ea2d19538d3bb6aaae6419401a7fade2f5e16"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 1922
EXPECTED_COMPOSITION_WRITE_BYTES = 3488
EXPECTED_INSTRUCTION_COUNT = 720
EXPECTED_CODE_ENTRY_COUNT = 11
DYNAMIC_MARKER_PATTERN = (
    r"^VQ_SH_ELF_CAN_TELEMETRY status=PASS cases=[1-9][0-9]* entries=11 "
    r"profiles=1 contexts=10 isr_rte=5$"
)
CAN_COVERAGE_UNITS = ("wrappers", "control", "capture", "completion")
CAPTURE_MEASURED_REGIONS = ("capture", "build_bank", "knock_margin_wrapper", "request_page")
COMPLETION_MEASURED_REGIONS = ("sle1_isr", "completion")
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


def _bounded_capture_callers(parsed_by_unit):
    """Return call sites into measured capture leaves without qualifying their bodies."""
    found = []
    for parsed in parsed_by_unit.values():
        statements = getattr(parsed, "statements", ())
        if not statements:
            continue
        by_address = parsed.statement_by_address
        for row in statements:
            if row.kind != "instruction":
                continue
            pool = None
            if row.text == "jsr @r0":
                previous = by_address.get(row.address - 2)
                if not (previous and previous.kind == "instruction"
                        and previous.text == "mov.l @(telemetry_completion_request_page,pc),r0"):
                    continue
                pool = parsed.labels["telemetry_completion_request_page"]
            elif row.text not in {"bsr telemetry_request_page", "bsr telemetry_build_bank"}:
                continue
            delay = by_address.get(row.address + 2)
            if delay is None or delay.kind != "instruction" or delay.text != "nop":
                raise VerificationError("bounded capture caller lacks its delay nop")
            found.append((row.address, pool))
    return tuple(found)


def _in_measured_region(address, layout):
    for key in ("capture", "completion"):
        for name in _measured_regions(key):
            span = layout.code_region_by_key[name].span
            if span.start <= address < span.end:
                return True
    return False


def _measured_regions(key):
    if key == "capture":
        return CAPTURE_MEASURED_REGIONS
    if key == "completion":
        return COMPLETION_MEASURED_REGIONS
    return None


def _measured_statements(key, parsed, layout):
    """Select fixed regions without qualifying the other entries of a unit."""
    if not parsed.statements:
        return parsed.statements
    regions = _measured_regions(key)
    if regions is None:
        return parsed.statements
    spans = tuple(layout.code_region_by_key[name].span for name in regions)
    return tuple(
        row for row in parsed.statements
        if any(span.start <= row.address < span.end for span in spans)
    )


def require_wrapper_instruction_bytes(fixture, composed, parsed_by_unit, layout):
    """Bind wrapper instruction words and ROM call operands after all stubs."""
    for key in CAN_COVERAGE_UNITS:
        parsed = parsed_by_unit[key]
        for row in _measured_statements(key, parsed, layout):
            if row.kind != "instruction":
                continue
            if fixture[row.address:row.address + 2] != composed[row.address:row.address + 2]:
                raise VerificationError(f"simulator changes CAN wrapper instruction at {row.address:#010x}")
            if map_switching_assembly._mnemonic(row) != "jsr":
                continue
            previous = parsed.statement_by_address.get(row.address - 2)
            literal = map_switching_assembly.PC_RELATIVE_RE.fullmatch(previous.text) if previous and previous.kind == "instruction" else None
            if (row.text != "jsr @r0" or literal is None or literal.group("width") != "l"
                    or literal.group("register") != "r0"):
                raise VerificationError(f"unbound CAN wrapper call at {row.address:#010x}")
            pool = parsed.labels[literal.group("label")]
            operand = parsed.statement_by_address.get(pool)
            if operand is None or operand.kind != "long" or operand.size != 4:
                raise VerificationError(f"CAN wrapper call pool is not one typed long at {pool:#010x}")
            if fixture[pool:pool + 4] != composed[pool:pool + 4]:
                raise VerificationError(f"simulator changes CAN wrapper control literal at {pool:#010x}")
    for address, pool in _bounded_capture_callers(parsed_by_unit):
        if fixture[address:address + 4] != composed[address:address + 4]:
            raise VerificationError("simulator changes bounded capture caller")
        if pool is not None and fixture[pool:pool + 4] != composed[pool:pool + 4]:
            raise VerificationError("simulator changes bounded capture caller")


def require_wrapper_coverage(records, fixture, layout, parsed_by_unit, invoke_words):
    """Measure only canonical CAN wrapper entries, loops and call/return paths."""
    evaluator = layout.hook_by_key["knock_margin_latch"].stock
    evaluator_return = evaluator + len(EVALUATOR_STUB_CODE) - 4
    stub = knock_evaluator_stub(evaluator)
    if fixture[evaluator:evaluator + len(stub)] != stub:
        raise VerificationError("CAN knock evaluator stand-in differs")
    control = parsed_by_unit["control"]
    config_entry = control.labels["telemetry_control_config_valid"]
    private_returns = {row.address for row in control.statements if row.kind == "instruction"
                       and row.address >= config_entry and map_switching_assembly._mnemonic(row) == "rts"}
    entries = {config_entry}
    request_entry = layout.code_region_by_key["request_page"].entry
    build_entry = layout.code_region_by_key["build_bank"].entry
    isr_entry = layout.code_region_by_key["sle1_isr"].entry
    isr_span = layout.code_region_by_key["sle1_isr"].span
    completion_entry = layout.code_region_by_key["completion"].entry
    capture_callees = {request_entry, build_entry}
    instructions, outcomes, slots, call_targets, direct_targets, config_calls = {}, set(), set(), {}, {}, set()
    for key in CAN_COVERAGE_UNITS:
        parsed = parsed_by_unit[key]
        regions = _measured_regions(key)
        if regions is None:
            regions = layout.assembly_unit_by_key[key].code_regions
        entries.update(layout.code_region_by_key[name].entry for name in regions)
        for row in _measured_statements(key, parsed, layout):
            if row.kind != "instruction":
                continue
            pc = row.address
            instructions[pc] = int.from_bytes(fixture[pc:pc + 2], "big")
            mnemonic = map_switching_assembly._mnemonic(row)
            if mnemonic == "rte" and not (isr_span.start <= pc < isr_span.end):
                raise VerificationError(f"unsupported CAN wrapper transfer at {pc:#010x}")
            if mnemonic in (map_switching_assembly.DIRECT_BRANCH_MNEMONICS
                            | map_switching_assembly.INDIRECT_CONTROL_MNEMONICS) - {"bt", "bf", "bra", "bsr", "jsr", "rts", "rte"}:
                raise VerificationError(f"unsupported CAN wrapper transfer at {pc:#010x}")
            if mnemonic in {"bt", "bf", "bra", "bsr"}:
                target = map_switching_assembly._validate_direct_branch_encoding(parsed, row, instructions[pc])
                if mnemonic in {"bt", "bf"}:
                    outcomes.update(((pc, target), (pc, pc + 2)))
                elif mnemonic == "bra":
                    direct_targets[pc] = target
                else:
                    if key == "control" and target == config_entry:
                        call_targets[pc] = target
                        config_calls.add(pc)
                    elif target in capture_callees or _in_measured_region(target, layout):
                        call_targets[pc] = target
                    else:
                        raise VerificationError(f"unsupported CAN BSR target at {pc:#010x}")
            if mnemonic in {"jsr", "rts", "bra", "bsr", "rte"}:
                slots.add(pc + 2)
            if mnemonic == "jsr":
                previous = parsed.statement_by_address.get(pc - 2)
                literal = map_switching_assembly.PC_RELATIVE_RE.fullmatch(previous.text) if previous else None
                if (row.text != "jsr @r0" or literal is None or literal.group("width") != "l"
                        or literal.group("register") != "r0"):
                    raise VerificationError(f"unbound CAN wrapper call at {pc:#010x}")
                pool = parsed.labels[literal.group("label")]
                call_targets[pc] = int.from_bytes(fixture[pool:pool + 4], "big")
    if not entries <= instructions.keys() or not private_returns or not config_calls:
        raise VerificationError("CAN entries/private returns lack typed instructions")
    expected_config_returns = {(call, config_entry, returned, call + 4)
                               for call in config_calls for returned in private_returns}
    observed_config_returns = set()
    bounded_callers = {address for address, _pool in _bounded_capture_callers(parsed_by_unit)}
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
        if pc == isr_entry and not frames:
            frames.append((None, isr_entry, None))
        if pc in instructions and not frames:
            raise VerificationError(f"CAN wrapper instruction lacks its invoke frame at {pc:#010x}")
        if pc in instructions and word & 0xff00 in {0x8900, 0x8b00}:
            successor = base_verifier._trace_successor(records, index, False)
            if (pc, successor) not in outcomes:
                raise VerificationError(f"executed CAN conditional successor differs at {pc:#010x}")
            observed_outcomes.add((pc, successor))
        if pc + 2 in slots and word != 0x002b:
            base_verifier._trace_successor(records, index, True)
        if pc in direct_targets and base_verifier._trace_successor(records, index, True) != direct_targets[pc]:
            raise VerificationError(f"executed CAN BRA successor differs at {pc:#010x}")
        is_call = word & 0xf0ff == 0x400b or word & 0xf000 == 0xb000
        if is_call:
            target = base_verifier._trace_successor(records, index, True)
            if pc in call_targets and target != call_targets[pc]:
                raise VerificationError(f"executed CAN callee differs at {pc:#010x}")
            if target == config_entry and pc not in config_calls:
                raise VerificationError(f"unbound CAN config caller at {pc:#010x}")
            if (not frames and target in entries and pc not in invoke_words
                    and pc not in bounded_callers):
                raise VerificationError(f"CAN wrapper origin is outside bound invoke code at {pc:#010x}")
            if frames or target in entries or pc in call_targets:
                frames.append((pc, target, pc + 4))
        elif word == 0x002b and pc in instructions:
            following = index + 1
            if following >= len(records) or records[following][0::2] != (pc + 2, 1):
                raise VerificationError(f"missing executed delay slot at {pc + 2:#010x}")
            if not frames:
                raise VerificationError(f"CAN exception return lacks its frame at {pc:#010x}")
            call, entry, continuation = frames.pop()
            if entry != isr_entry or continuation is not None or call is not None:
                raise VerificationError(f"CAN exception return leaves frame {entry:#010x}")
            returned.add(entry)
        elif word == 0x000b and (frames or pc in instructions):
            target = base_verifier._trace_successor(records, index, True)
            if (pc not in instructions and len(frames) == 1 and frames[0][1] == isr_entry
                    and frames[0][2] is None):
                continue
            if not frames:
                raise VerificationError(f"CAN wrapper return lacks its invoke frame at {pc:#010x}")
            call, entry, continuation = frames.pop()
            if continuation is None or target != continuation:
                raise VerificationError(f"executed CAN return differs at {pc:#010x}")
            if entry == evaluator and pc != evaluator_return:
                raise VerificationError(f"unsupported CAN evaluator return path at {pc:#010x}")
            if entry == config_entry:
                if call not in config_calls or pc not in private_returns:
                    raise VerificationError(f"unsupported CAN config return path at {pc:#010x}")
                observed_config_returns.add((call, entry, pc, continuation))
            if entry in entries:
                returned.add(entry)
            if entry in entries or call in call_targets:
                call_returns.add((call, entry, continuation))
        elif word == 0x002b and pc not in instructions and frames:
            raise VerificationError(f"unsupported transfer in active CAN wrapper frame at {pc:#010x}")
        elif frames and (word & 0xff00 == 0xc300
                         or word & 0xf0ff in {0x0003, 0x0023, 0x402b}):
            raise VerificationError(f"unsupported transfer in active CAN wrapper frame at {pc:#010x}")
    for missing in sorted(entries - seen):
        raise VerificationError(f"uncovered CAN wrapper entry {missing:#010x}")
    for pc, target in sorted(outcomes - observed_outcomes):
        raise VerificationError(f"uncovered CAN wrapper outcome {pc:#010x}->{target:#010x}")
    for missing in sorted(instructions.keys() - seen):
        raise VerificationError(f"uncovered CAN wrapper instruction {missing:#010x}")
    for call, entry, returned_pc, continuation in sorted(expected_config_returns - observed_config_returns):
        raise VerificationError(f"uncovered CAN config return {call:#010x}->{returned_pc:#010x}->{continuation:#010x}")
    if frames or entries - returned or call_targets.keys() - {row[0] for row in call_returns}:
        raise VerificationError("uncovered CAN wrapper call/return path")
    for missing in sorted(slots - observed_slots):
        raise VerificationError(f"uncovered CAN wrapper delay slot {missing:#010x}")
    for name, entry in (("request", request_entry), ("build", build_entry),
                        ("completion", completion_entry)):
        if not any(call in invoke_words and returned_entry == entry
                   for call, returned_entry, _continuation in call_returns):
            raise VerificationError(f"uncovered CAN {name} invoke return {entry:#010x}")
    return dict(entries=len(entries & seen), instructions=len(instructions.keys() & seen),
                outcomes=len(outcomes & observed_outcomes), delay_slots=len(slots & observed_slots),
                call_return_paths=len(call_returns), config_return_paths=len(observed_config_returns & expected_config_returns))


def build_and_run_dynamic_harness(fixture, build_dir, *, layout, parsed_by_unit, composed_image):
    require_wrapper_instruction_bytes(fixture, composed_image, parsed_by_unit, layout)
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
        "-DVERIFY_7MFK_CAN_CONTROL", "-DVERIFY_7MFK_CAN_MARGIN",
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
    semantic = re.findall(DYNAMIC_MARKER_PATTERN, result.stdout, re.MULTILINE)
    if len(semantic) != 1:
        raise VerificationError("CAN telemetry harness lacks one exact semantic marker")
    main_call = "(void)invoke_r4(MAIN_WRAPPER, 0);"
    config_call = "mutate_configuration(mutation);\n    (void)invoke_r4(CONTROL_POLL, 0);"
    control = parsed_by_unit["control"]
    config_entry = control.labels["telemetry_control_config_valid"]
    magic = next(row for row in control.statements if row.kind == "instruction"
                 and row.address >= config_entry and map_switching_assembly._mnemonic(row) == "bf")
    target = map_switching_assembly._validate_direct_branch_encoding(
        control, magic, int.from_bytes(fixture[magic.address:magic.address + 2], "big"))
    margin = parsed_by_unit["capture"]
    zero = next(row for row in _measured_statements("capture", margin, layout)
                if row.kind == "instruction" and row.text == "bt telemetry_margin_return"
                and margin.statement_by_address[row.address - 2].text == "tst r4,r4")
    zero_target = map_switching_assembly._validate_direct_branch_encoding(
        margin, zero, int.from_bytes(fixture[zero.address:zero.address + 2], "big"))
    evaluator = layout.hook_by_key["knock_margin_latch"].stock
    request_entry = layout.code_region_by_key["request_page"].entry
    measured_capture = _measured_statements("capture", parsed_by_unit["capture"], layout)
    clamp = next(row for row in measured_capture
                 if row.kind == "instruction" and row.text == "bf telemetry_build_context_valid")
    magic_fail = min((row for row in measured_capture
                      if row.kind == "instruction" and row.text == "bf telemetry_capture_return"),
                     key=lambda row: row.address)
    magic_target = map_switching_assembly._validate_direct_branch_encoding(
        parsed_by_unit["capture"], magic_fail,
        int.from_bytes(fixture[magic_fail.address:magic_fail.address + 2], "big"))
    measured_completion = _measured_statements("completion", parsed_by_unit["completion"], layout)
    abort_edge = next(row for row in measured_completion
                      if row.kind == "instruction" and row.text == "bt telemetry_isr_restore")
    idle_ack = next(row for row in measured_completion
                    if row.kind == "instruction"
                    and row.text == "bt telemetry_completion_busy_valid")
    request_copy = (
        "{{\n        size_t index;\n        for (index = 0; index < 8; ++index)\n"
        "            ram_pointer(MAILBOX_DATA)[index] = ram_pointer({bank})[{offset} + index];\n    }}"
    )
    omissions = (
        ("main", ((main_call, "(void)invoke_r4(CONTROL_POLL, 0);\n    (void)invoke_r4(CAPTURE, 0);"),),
         f"uncovered CAN wrapper entry {layout.code_region_by_key['main_wrapper'].entry:#010x}",
         "VQ_SH_ELF_CAN_WRAPPER_COVERAGE_NEGATIVE"),
        ("config-magic", ((config_call,
         "mutate_configuration(mutation);\n    if (mutation != CONFIG_MAGIC)\n        (void)invoke_r4(CONTROL_POLL, 0);"),),
         f"uncovered CAN wrapper outcome {magic.address:#010x}->{target:#010x}",
         "VQ_SH_ELF_CAN_CONTROL_COVERAGE_NEGATIVE"),
        ("margin-zero", (("(void)invoke_r4(KNOCK_MARGIN_WRAPPER, 0);",
         f"(void)invoke_r4((selector == 0 && primary == 0 && channel == 0) ? {evaluator:#010x}U : KNOCK_MARGIN_WRAPPER, 0);"),),
         f"uncovered CAN wrapper outcome {zero.address:#010x}->{zero_target:#010x}",
         "VQ_SH_ELF_CAN_MARGIN_COVERAGE_NEGATIVE"),
        ("request-page", (
            ("(void)invoke_r4(REQUEST_PAGE, 0);\n    if (!expect_bytes(\n            \"request-a\"",
             request_copy.format(bank="BANK_A", offset=80) + "\n    if (!expect_bytes(\n            \"request-a\""),
            ("(void)invoke_r4(REQUEST_PAGE, 0);\n    if (!expect_bytes(\n            \"request-b\"",
             request_copy.format(bank="BANK_B", offset=32) + "\n    if (!expect_bytes(\n            \"request-b\""),
        ),
         f"uncovered CAN request invoke return {request_entry:#010x}",
         "VQ_SH_ELF_CAN_REQUEST_COVERAGE_NEGATIVE"),
        ("build-clamp", (("    state[6] = 0xff;\n", "    state[6] = 0;\n"),),
         f"uncovered CAN wrapper outcome {clamp.address:#010x}->{clamp.address + 2:#010x}",
         "VQ_SH_ELF_CAN_BUILD_COVERAGE_NEGATIVE"),
        ("capture-magic", (
            ("        mutate_configuration(mutation);\n        (void)invoke_r4(CAPTURE, 0);",
             "        mutate_configuration(mutation);\n"
             "        if (mutation != CONFIG_MAGIC)\n"
             "            (void)invoke_r4(CAPTURE, 0);"),
        ),
         f"uncovered CAN wrapper outcome {magic_fail.address:#010x}->{magic_target:#010x}",
         "VQ_SH_ELF_CAN_CAPTURE_COVERAGE_NEGATIVE"),
        ("isr-abort", (
            ('if (!run_isr_case("isr-stock-abort", 0, MAILBOX28_MASK, 0))',
             'if (!run_isr_case("isr-stock-abort", 0, 0, 0))'),
            ('if (!run_isr_case(\n            "isr-simultaneous-ack",\n'
             '            MAILBOX26_MASK, MAILBOX28_MASK, 1))',
             'if (!run_isr_case(\n            "isr-simultaneous-ack",\n'
             '            MAILBOX26_MASK, 0, 1))'),
        ),
         f"uncovered CAN wrapper outcome {abort_edge.address:#010x}->{abort_edge.address + 2:#010x}",
         "VQ_SH_ELF_CAN_ISR_COVERAGE_NEGATIVE"),
        ("ack-idle", (
            ("    state[3] = 4;\n    signal_ack(MAILBOX26_MASK);\n"
             "    (void)invoke_r4(COMPLETION, 0);\n",
             "    state[3] = 4;\n    signal_ack(MAILBOX26_MASK);\n"),
        ),
         f"uncovered CAN wrapper outcome {idle_ack.address:#010x}->{idle_ack.address + 2:#010x}",
         "VQ_SH_ELF_CAN_COMPLETION_COVERAGE_NEGATIVE"),
    )
    negative_sources, negative_markers = [], []
    for name, edits, reason, prefix in omissions:
        negative_text = source
        for call, replacement in edits:
            if negative_text.count(call) != 1:
                raise VerificationError(f"CAN negative lacks its unique {name} invocation")
            negative_text = negative_text.replace(call, replacement)
        negative_source = build_dir / f"can-telemetry-bypass-{name}.c"
        negative_source.write_text(negative_text, encoding="utf-8")
        negative_sources.append((negative_source, negative_text))
        negative_elf = build_dir / f"can-telemetry-bypass-{name}.elf"
        negative_command = list(command)
        negative_command[negative_command.index("-o") + 1] = negative_elf
        negative_command[negative_command.index(positive_source)] = negative_source
        base_verifier.run_command(negative_command, timeout=120)
        require_separate_storage(negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
        negative, records, invoke_words = execute(negative_elf)
        if semantic[0] not in negative.stdout:
            raise VerificationError(f"CAN {name} bypass does not preserve the semantic output")
        try:
            require_wrapper_coverage(records, fixture, layout, parsed_by_unit, invoke_words)
        except VerificationError as error:
            if str(error) != reason:
                raise VerificationError(f"CAN bypass fails outside its obligation: {error}") from error
        else:
            raise VerificationError(f"CAN coverage accepts the {name} bypass")
        negative_markers.append(f"{prefix} status=PASS {reason}")
    if (HARNESS_SOURCE.read_text(encoding="utf-8") != source
            or positive_source.read_text(encoding="utf-8") != source
            or any(path.read_text(encoding="utf-8") != text for path, text in negative_sources)):
        raise VerificationError("CAN harness source changes during verification")
    marker = (
        "VQ_SH_ELF_CAN_WRAPPER_COVERAGE status=PASS scope=JK08A:wrappers,control,"
        + ",".join((*CAPTURE_MEASURED_REGIONS, *COMPLETION_MEASURED_REGIONS)) + " "
    )
    marker += " ".join(f"{key}={value}" for key, value in covered.items())
    return "\n".join((result.stdout.strip(), marker, *negative_markers))


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
