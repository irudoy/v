#!/usr/bin/env python3
"""Verify exact JK08A Rolling Launch instructions with GNU SH-2E tools."""

from __future__ import annotations

import argparse
import hashlib
import os
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
from elf_storage_layout import ELFStorageError, require_separate_storage

from patches import map_switching_assembly
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout


EXPECTED_COMPOSITION_SHA256 = (
    "78788d1cdbc012114d16a3febcd57524383967b2b61742ea8e9b74f0ac8bfff2"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 1972
EXPECTED_COMPOSITION_WRITE_BYTES = 2328
EXPECTED_INSTRUCTION_COUNT = 876
EXPECTED_CODE_ENTRY_COUNT = 8
EXPECTED_DIAGNOSTIC_COUNT = 9
EXPECTED_DYNAMIC_CASES = 136
RETURN_STUB = bytes.fromhex("000b0009")
FEEDBACK_SERIALIZER_STUB = bytes.fromhex(
    "d103e0b52100000b00090009000901003ada"
)
WRAPPER_REGIONS = ("periodic_wrapper", "selector_arbiter", "startup_wrapper")
COVERAGE_UNITS = ("wrappers", "engine", "threshold_helper", "feedback_arbiter", "ignition_adapter", "ignition_controller")
COVERAGE_REGIONS = (*WRAPPER_REGIONS, "engine", "threshold_helper", "feedback_arbiter", "ignition_adapter", "ignition_controller")


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


def bind_threshold_engine_window(fixture, composed, parsed, regions):
    """Bind only the engine entry and its exact helper call window."""
    loads = [row for row in parsed.statements if row.kind == "instruction"
             and row.text == "mov.l @(rl_threshold_helper_entry,pc),r0"]
    if len(loads) != 1:
        raise VerificationError("threshold helper lacks its unique engine call window")
    load = loads[0].address
    rows = parsed.statement_by_address
    if (rows.get(load + 2) is None or rows.get(load + 4) is None
            or rows[load + 2].text != "jsr @r0" or rows[load + 4].text != "nop"
            or not regions["engine"].span.start <= load < load + 6 <= regions["engine"].span.end):
        raise VerificationError("unsupported threshold engine call window")
    pool = parsed.labels["rl_threshold_helper_entry"]
    entry = regions["engine"].entry
    for start, size in ((entry, 2), (load, 6), (pool, 4)):
        if fixture[start:start + size] != composed[start:start + size]:
            raise VerificationError("simulator changes threshold engine call binding")
    if (int.from_bytes(fixture[pool:pool + 4], "big") != regions["threshold_helper"].entry
            or int.from_bytes(fixture[load:load + 2], "big") !=
            0xD000 | ((pool - ((load + 4) & ~3)) // 4)
            or fixture[load + 2:load + 6] != bytes.fromhex("400b0009")):
        raise VerificationError("threshold engine call window differs from its source")
    return entry, load + 2


def bind_ignition_adapter_windows(fixture, composed, parsed, regions, stock):
    """Bind only adapter entry and its two literal tail windows."""
    entry = regions["ignition_adapter"].entry
    if fixture[entry:entry + 2] != composed[entry:entry + 2]:
        raise VerificationError("simulator changes ignition adapter entry")
    jumps = []
    for label, target in (("rl_ign_controller_entry", regions["ignition_controller"].entry),
                          ("rl_ign_stock_consumer", stock)):
        rows = [row for row in parsed.statements if row.kind == "instruction"
                and row.text == f"mov.l @({label},pc),r0"]
        if len(rows) != 1:
            raise VerificationError("ignition adapter lacks its unique tail window")
        pc, pool = rows[0].address, parsed.labels[label]
        for start, size in ((pc, 6), (pool, 4)):
            if fixture[start:start + size] != composed[start:start + size]:
                raise VerificationError("simulator changes ignition adapter tail binding")
        expected = 0xD000 | ((pool - ((pc + 4) & ~3)) // 4)
        if (int.from_bytes(fixture[pc:pc + 2], "big") != expected
                or fixture[pc + 2:pc + 6] != bytes.fromhex("402b0009")
                or int.from_bytes(fixture[pool:pool + 4], "big") != target):
            raise VerificationError("ignition adapter tail differs from its source binding")
        jumps.append(pc + 2)
    return entry, *jumps


def require_wrapper_coverage(records, fixture, parsed_by_unit, regions, stock_boundaries, invoke_words, serializer_entry, ignition_stock_entry):
    """Measure the fixed canonical wrapper, threshold and feedback scope."""
    wrapper_entries = {regions[key].entry for key in WRAPPER_REGIONS}
    helper = regions["threshold_helper"].entry
    arbiter = regions["feedback_arbiter"].entry
    controller = regions["ignition_controller"].entry
    entries = wrapper_entries | {helper, arbiter, controller}
    adapter, adapter_controller_tail, adapter_stock_tail = bind_ignition_adapter_windows(
        fixture, fixture, parsed_by_unit["ignition_adapter"], regions, ignition_stock_entry)
    entries.add(adapter)
    engine, engine_call = bind_threshold_engine_window(
        fixture, fixture, parsed_by_unit["engine"], regions)
    entries.add(engine)
    instructions, owners, outcomes, slots, transfers, direct = {}, {}, set(), set(), {}, {}
    for unit in COVERAGE_UNITS:
        parsed = parsed_by_unit[unit]
        for row in parsed.statements:
            if row.kind != "instruction":
                continue
            pc = row.address
            owner = [regions[key].entry for key in COVERAGE_REGIONS
                     if regions[key].span.start <= pc < regions[key].span.end]
            if len(owner) != 1:
                raise VerificationError(f"wrapper instruction lacks its declared region at {pc:#010x}")
            owners[pc] = owner[0]
            instructions[pc] = int.from_bytes(fixture[pc:pc + 2], "big")
            mnemonic = map_switching_assembly._mnemonic(row)
            if mnemonic in {"braf", "bsrf", "rte", "trapa"} or mnemonic == "bsr" and unit != "engine":
                raise VerificationError(f"unsupported measured control form at {pc:#010x}")
            if mnemonic == "bsr":
                target = map_switching_assembly._validate_direct_branch_encoding(
                    parsed, row, instructions[pc])
                span = regions["engine"].span
                if not span.start <= target < span.end:
                    raise VerificationError(f"unsupported measured control form at {pc:#010x}")
            if mnemonic in map_switching_assembly.DELAYED_CONTROL_MNEMONICS:
                slots.add(pc + 2)
            if mnemonic in {"bt", "bf", "bt/s", "bf/s", "bra"}:
                target = map_switching_assembly._validate_direct_branch_encoding(parsed, row, instructions[pc])
                if mnemonic == "bra":
                    direct[pc] = target
                else:
                    outcomes.update(((pc, target), (pc, pc + (4 if mnemonic.endswith("/s") else 2))))
            if mnemonic in {"jsr", "jmp"}:
                previous = parsed.statement_by_address.get(pc - 2)
                literal = map_switching_assembly.PC_RELATIVE_RE.fullmatch(previous.text) if previous else None
                register = "r3" if (unit == "threshold_helper" or unit == "ignition_controller" and mnemonic == "jsr") else "r0"
                if (literal is None or literal.group("width") != "l"
                        or literal.group("register") != register or row.text != f"{mnemonic} @{register}"
                        or unit not in {"wrappers", "ignition_controller", "ignition_adapter"} and mnemonic != "jsr"):
                    raise VerificationError(f"unbound wrapper transfer at {pc:#010x}")
                pool = parsed.labels[literal.group("label")]
                transfers[pc] = (mnemonic, pool, int.from_bytes(fixture[pool:pool + 4], "big"))
    helper_calls = [pc for pc in transfers if owners[pc] == helper]
    helper_returns = [pc for pc, word in instructions.items() if owners[pc] == helper and word == 11]
    if len(helper_calls) != 1 or len(helper_returns) != 1:
        raise VerificationError("threshold helper lacks its unique divider call and native RTS")
    divider_call, helper_return = helper_calls[0], helper_returns[0]
    arbiter_calls = [pc for pc in transfers if owners[pc] == arbiter]
    arbiter_returns = [pc for pc, word in instructions.items() if owners[pc] == arbiter and word == 11]
    if len(arbiter_calls) != 1 or len(arbiter_returns) != 1:
        raise VerificationError("feedback arbiter lacks its unique Map call and native RTS")
    arbiter_call, arbiter_return = arbiter_calls[0], arbiter_returns[0]
    base_feedback = transfers[arbiter_call][2]
    if fixture[serializer_entry:serializer_entry + len(FEEDBACK_SERIALIZER_STUB)] != FEEDBACK_SERIALIZER_STUB:
        raise VerificationError("feedback serializer boundary differs from its declared fixture stub")
    controller_calls = [pc for pc in transfers if owners[pc] == controller and transfers[pc][0] == "jsr"]
    controller_tails = [pc for pc in transfers if owners[pc] == controller and transfers[pc][0] == "jmp"]
    if len(controller_calls) != 1 or len(controller_tails) != 1 or any(
            word == 11 and owners[pc] == controller for pc, word in instructions.items()):
        raise VerificationError("controller lacks its unique divider call and stock tail")
    controller_call, controller_tail = controller_calls[0], controller_tails[0]
    if (transfers[controller_tail][2] != ignition_stock_entry
            or fixture[ignition_stock_entry:ignition_stock_entry + 4] != RETURN_STUB):
        raise VerificationError("controller stock return boundary is not its declared RTS/NOP stub")
    for entry, boundary in stock_boundaries.items():
        if entry not in wrapper_entries or fixture[boundary:boundary + 4] != RETURN_STUB:
            raise VerificationError("wrapper stock return boundary is not its RTS/NOP stub")
    if set(stock_boundaries) != wrapper_entries:
        raise VerificationError("wrapper stock return boundaries are incomplete")

    def successor(index, delayed):
        try:
            return base_verifier._trace_successor(records, index, delayed)
        except base_verifier.VerificationError as error:
            raise VerificationError(str(error)) from error

    seen, branches, delayed_slots, returned, calls, tails = set(), set(), set(), set(), set(), set()
    frames = []
    previous_frame = None
    for index, (pc, word, delay) in enumerate(records):
        expected = (int.from_bytes(fixture[pc:pc + 2], "big") if 0 <= pc < len(fixture) - 1
                    else invoke_words.get(pc))
        if expected is None or word != expected:
            raise VerificationError(f"executed wrapper-trace opcode differs at {pc:#010x}")
        if any(regions[key].span.start <= pc < regions[key].span.end for key in COVERAGE_REGIONS) and pc not in instructions:
            raise VerificationError(f"executed wrapper data at {pc:#010x}")
        frame = previous_frame if delay else (frames[-1] if frames else None)
        if not delay:
            previous_frame = dict(frame) if frame is not None else None
        if pc in instructions:
            engine_span = regions["engine"].span
            same_engine = (engine_span.start <= pc < engine_span.end
                           and frame is not None
                           and engine_span.start <= frame["entry"] < engine_span.end)
            if frame is None or frame["entry"] != owners[pc] and not same_engine:
                raise VerificationError(f"wrapper lacks its originating invoke frame at {pc:#010x}")
            seen.add(pc)
        if delay:
            if not index or records[index - 1][0] != pc - 2 or records[index - 1][2]:
                raise VerificationError(f"orphan wrapper delay slot at {pc:#010x}")
            delayed_slots.add(pc)
            continue
        if pc in instructions and word & 0xFF00 in {0x8900, 0x8B00, 0x8D00, 0x8F00}:
            branches.add((pc, successor(index, word & 0xFF00 in {0x8D00, 0x8F00})))
        if pc + 2 in slots:
            successor(index, True)
        if pc in direct and successor(index, True) != direct[pc]:
            raise VerificationError(f"executed wrapper BRA differs at {pc:#010x}")
        if pc in {adapter_controller_tail, adapter_stock_tail}:
            target = controller if pc == adapter_controller_tail else ignition_stock_entry
            if (frame is None or frame["entry"] != adapter or frame["origin"]["entry"] != adapter
                    or not index or records[index - 1][0] != pc - 2 or records[index - 1][2]
                    or successor(index, True) != target):
                raise VerificationError("ignition adapter tail lacks its bound invoke origin")
            if target == controller:
                frame["call_entry"] = adapter
                frame["entry"] = controller
            else:
                frame["origin"]["adapter_stock_tail"] = True
        if pc in transfers:
            kind, _pool, target = transfers[pc]
            if pc == controller_call:
                if frame is None or frame["entry"] != controller or not index or records[index - 1][0] != pc - 2:
                    raise VerificationError("controller divider call lacks its bound R3 load")
                frame["origin"]["controller_divider_called"] = True
            if pc == controller_tail:
                frame["origin"]["controller_stock_tail"] = True
            if pc == arbiter_call and (frame is None or frame["entry"] != arbiter
                    or not index or records[index - 1][0] != pc - 2 or records[index - 1][2]):
                raise VerificationError("feedback Map call lacks its bound R0 load and arbiter frame")
            if pc == divider_call and (not index or records[index - 1][0] != pc - 2 or records[index - 1][2]):
                raise VerificationError("threshold divider call lacks its bound R3 load")
            if successor(index, True) != target:
                raise VerificationError(f"executed wrapper {kind.upper()} differs at {pc:#010x}")
            if kind == "jmp":
                tails.add((pc, target))
        is_call = word & 0xF0FF == 0x400B or word & 0xF000 == 0xB000
        if is_call:
            target = successor(index, True)
            if target in wrapper_entries:
                if frames or pc not in invoke_words:
                    raise VerificationError("wrapper entry lacks its originating invoke call")
                origin = {"entry": target, "stock_return": False}
            elif target == controller:
                raise VerificationError("controller entry requires its bound adapter tail")
            elif target == adapter:
                if frames or pc not in invoke_words:
                    raise VerificationError("ignition adapter lacks its originating invoke call")
                origin = {"entry": adapter, "stock_return": False,
                          "adapter_stock_tail": False, "controller_stock_tail": False,
                          "controller_divider_called": False, "controller_divider_return": False}
            elif target == arbiter:
                if frames or pc not in invoke_words:
                    raise VerificationError("feedback arbiter lacks its originating invoke call")
                origin = {"entry": arbiter, "stock_return": False,
                          "serializer_return": False, "base_feedback_return": False}
            elif target == helper:
                if not frames and pc in invoke_words:
                    origin = {"entry": helper, "stock_return": False}
                elif frames and frames[-1]["entry"] == engine and pc == engine_call:
                    if not index or records[index - 1][0] != pc - 2 or records[index - 1][2]:
                        raise VerificationError("threshold engine call lacks its bound load")
                    origin = frames[-1]["origin"]
                else:
                    raise VerificationError("threshold helper lacks its bound engine or invoke origin")
            elif not frames and target == engine and pc in invoke_words:
                origin = {"entry": engine, "stock_return": False}
            elif frames:
                origin = frames[-1]["origin"]
                if target == engine and (pc not in transfers or owners[pc] != regions["periodic_wrapper"].entry):
                    raise VerificationError("threshold engine lacks its bound parent call")
            else:
                continue
            frames.append(dict(call=pc, entry=target, continuation=pc + 4,
                               origin=origin, divider_return=False))
        elif word == 0x000B and (frames or pc in instructions):
            target = successor(index, True)
            if not frames:
                raise VerificationError("wrapper return lacks its originating call")
            frame = frames.pop()
            call, entry, continuation, origin = (frame[key] for key in ("call", "entry", "continuation", "origin"))
            if target != continuation:
                raise VerificationError(f"executed wrapper return differs at {pc:#010x}")
            if origin["entry"] in stock_boundaries and pc == stock_boundaries[origin["entry"]]:
                origin["stock_return"] = True
            if origin["entry"] == arbiter:
                if entry == serializer_entry:
                    if pc != serializer_entry + 6 or not any(
                            parent["call"] == arbiter_call and parent["entry"] == base_feedback
                            and parent["origin"] is origin for parent in frames):
                        raise VerificationError("feedback serializer return lacks its bound Map parent and RTS")
                    origin["serializer_return"] = True
                if call == arbiter_call:
                    if entry != base_feedback or not origin["serializer_return"]:
                        raise VerificationError("feedback Map return lacks its serializer return boundary")
                    origin["base_feedback_return"] = True
            if call == controller_call and frames and frames[-1]["entry"] == controller:
                origin["controller_divider_return"] = True
            if entry == controller:
                if (pc != ignition_stock_entry or not origin["controller_stock_tail"]
                        or origin["controller_divider_called"] and not origin["controller_divider_return"]):
                    raise VerificationError("controller return lacks its divider or declared stock tail boundary")
                returned.add(entry)
            elif entry == adapter:
                if pc != ignition_stock_entry or not origin["adapter_stock_tail"]:
                    raise VerificationError("ignition adapter return lacks its declared stock tail boundary")
                returned.add(entry)
            elif entry == arbiter:
                if pc != arbiter_return or not origin["base_feedback_return"]:
                    raise VerificationError("feedback arbiter return lacks its Map return and native RTS")
                returned.add(entry)
            elif entry == helper:
                if pc != helper_return or not frame["divider_return"]:
                    raise VerificationError("threshold helper return lacks its divider return and native RTS")
                returned.add(entry)
            elif entry == engine:
                returned.add(entry)
            elif entry in wrapper_entries:
                if not origin["stock_return"]:
                    raise VerificationError("wrapper return lacks its stock return boundary")
                returned.add(entry)
            if call == divider_call and frames and frames[-1]["entry"] == helper:
                frames[-1]["divider_return"] = True
            if entry in entries or call in instructions:
                calls.add((call, frame.get("call_entry", entry), continuation))
    for missing in sorted(entries - seen):
        raise VerificationError(f"uncovered wrapper entry {missing:#010x}")
    for pc, target in sorted(outcomes - branches):
        raise VerificationError(f"uncovered wrapper branch {pc:#010x}->{target:#010x}")
    for missing in sorted(instructions.keys() - seen):
        raise VerificationError(f"uncovered wrapper instruction {missing:#010x}")
    if frames or entries - returned or transfers.keys() - {item[0] for item in calls | tails}:
        raise VerificationError("uncovered wrapper call/tail/return path")
    for missing in sorted(slots - delayed_slots):
        raise VerificationError(f"uncovered wrapper delay slot {missing:#010x}")
    return dict(entries=len(entries), instructions=len(instructions), outcomes=len(outcomes),
                delay_slots=len(slots), call_return_paths=len(calls), tail_paths=len(tails))


def build_and_run_dynamic_harness(fixture, build_dir, *, parsed_by_unit, composed_image,
                                  base_layout, rolling_layout):
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
    for unit in COVERAGE_UNITS:
        parsed = parsed_by_unit[unit]
        for row in parsed.statements:
            if row.kind == "instruction" and fixture[row.address:row.address + 2] != composed_image[row.address:row.address + 2]:
                raise VerificationError(f"simulator changes wrapper instruction at {row.address:#010x}")
            if row.kind == "instruction" and map_switching_assembly._mnemonic(row) in {"jsr", "jmp"}:
                previous = parsed.statement_by_address[row.address - 2]
                literal = map_switching_assembly.PC_RELATIVE_RE.fullmatch(previous.text)
                if literal is None:
                    raise VerificationError("wrapper transfer lacks its source literal")
                pool = parsed.labels[literal.group("label")]
                if fixture[pool:pool + 4] != composed_image[pool:pool + 4]:
                    raise VerificationError("simulator changes wrapper control literal")
    source_path = TOOL_DIR / "rolling_launch_harness.c"
    source = source_path.read_text(encoding="utf-8")
    positive = build_dir / "rolling-launch-positive.c"
    positive.write_text(source, encoding="utf-8")
    command = [
            base_verifier.GCC,
            "-m2e",
            "-mb",
            "-std=c11",
            "-DVERIFY_CANONICAL_ROLLING=1",
            "-O2",
            "-Wall",
            "-Wextra",
            "-Werror",
            f"-Wl,-Ttext-segment={base_verifier.DRIVER_TEXT_BASE:#x}",
            "-Wl,--section-start=.rom=0",
            "-o",
            harness_elf,
            positive,
            invoke_object,
            rom_object,
        ]
    base_verifier.run_command(command, timeout=120)
    try:
        require_separate_storage(harness_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
    except (ELFStorageError, OSError) as error:
        raise VerificationError(f"rolling-launch: ELF storage separation: {error}") from error
    def execute(elf):
        try:
            ranges, invoke_words = base_verifier._invoke_trace_bindings(elf, invoke_object, fixture, build_dir)
            bind_threshold_engine_window(fixture, composed_image, parsed_by_unit["engine"], regions)
            bind_ignition_adapter_windows(fixture, composed_image, parsed_by_unit["ignition_adapter"],
                                          regions, rolling_layout.hook_by_key["primary_ignition_command"].stock)
            trace = build_dir / f"{elf.stem}.pc-trace"
            environment = {**os.environ, "VQ_SH_PC_TRACE_FILE": str(trace),
                           "VQ_SH_PC_TRACE_FORMAT": "v1",
                           "VQ_SH_PC_TRACE_RANGES": ",".join(
                               f"{start:x}:{end:x}" for start, end in ((0, len(fixture)), *ranges))}
            before = elf.read_bytes()
            result = base_verifier.run_command(
                [base_verifier.RUN, f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k", elf],
                timeout=180, env=environment)
            if elf.read_bytes() != before:
                raise VerificationError("Rolling Launch ELF changes during execution")
            return result, base_verifier.read_pc_trace(trace), invoke_words
        except base_verifier.VerificationError as error:
            raise VerificationError(str(error)) from error

    regions = {key: rolling_layout.code_region_by_key[key] for key in (*COVERAGE_REGIONS, "engine", "ignition_adapter")}
    base_hooks = {hook.key: hook for hook in base_layout.hooks}
    boundaries = {
        regions["periodic_wrapper"].entry: rolling_layout.hook_by_key["displaced_periodic_task"].stock,
        regions["selector_arbiter"].entry: base_hooks["selector_host_call"].stock,
        regions["startup_wrapper"].entry: base_hooks["startup_initializer"].stock,
    }
    result, records, invoke_words = execute(harness_elf)
    covered = require_wrapper_coverage(records, fixture, parsed_by_unit, regions, boundaries, invoke_words,
                                       base_hooks["cruise_feedback_serializer"].stock,
                                       rolling_layout.hook_by_key["primary_ignition_command"].stock)
    marker = (
        "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=136 "
        "structural=11 gates=32 config=24 threshold=9 activation=6 "
        "active=9 cooldown=5 ignition=26 wrappers=6 feedback=8 entries=8"
    )
    if marker not in result.stdout:
        raise VerificationError(
            "Rolling Launch harness returned zero without the exact marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    call = "(void)invoke_r4(PERIODIC_WRAPPER, 0);"
    if source.count(call) != 1:
        raise VerificationError("negative harness lacks its unique periodic-wrapper call")
    negative_text = source.replace(call, "(void)invoke_r4(RL_ENGINE, 0);")
    negative_source = build_dir / "rolling-launch-bypass-periodic.c"
    negative_source.write_text(negative_text, encoding="utf-8")
    negative_elf = build_dir / "rolling-launch-bypass-periodic.elf"
    negative_command = list(command)
    negative_command[negative_command.index("-o") + 1] = negative_elf
    negative_command[negative_command.index(positive)] = negative_source
    base_verifier.run_command(negative_command, timeout=120)
    require_separate_storage(negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
    negative, records, invoke_words = execute(negative_elf)
    if marker not in negative.stdout:
        raise VerificationError("periodic bypass does not preserve the semantic PASS marker")
    expected = f"uncovered wrapper entry {regions['periodic_wrapper'].entry:#010x}"
    try:
        require_wrapper_coverage(records, fixture, parsed_by_unit, regions, boundaries, invoke_words,
                                       base_hooks["cruise_feedback_serializer"].stock,
                                       rolling_layout.hook_by_key["primary_ignition_command"].stock)
    except VerificationError as error:
        if str(error) != expected:
            raise VerificationError(f"periodic bypass fails outside its omitted entry: {error}") from error
    else:
        raise VerificationError("wrapper coverage accepts the real periodic bypass")
    zero_band_call = '    if (!invoke_ignition("ign-zero-band-start", 110, 308, 110))'
    if source.count(zero_band_call) != 1:
        raise VerificationError("controller negative lacks its unique zero-band case")
    controller_negative_text = source.replace(
        zero_band_call, '    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0x40;\n' + zero_band_call)
    controller_negative_source = build_dir / "rolling-launch-bypass-controller-zero-band.c"
    controller_negative_source.write_text(controller_negative_text, encoding="utf-8")
    controller_negative_elf = build_dir / "rolling-launch-bypass-controller-zero-band.elf"
    controller_negative_command = list(command)
    controller_negative_command[controller_negative_command.index("-o") + 1] = controller_negative_elf
    controller_negative_command[controller_negative_command.index(positive)] = controller_negative_source
    base_verifier.run_command(controller_negative_command, timeout=120)
    require_separate_storage(controller_negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
    controller_negative, records, invoke_words = execute(controller_negative_elf)
    if marker not in controller_negative.stdout:
        raise VerificationError("controller bypass does not preserve the semantic PASS marker")
    zero_edges = [row.address for row in parsed_by_unit["ignition_controller"].statements
                  if row.kind == "instruction" and row.text == "bt rl_ctrl_tail"]
    if len(zero_edges) != 1:
        raise VerificationError("controller zero-band outcome is not its unique source-bound edge")
    tail = parsed_by_unit["ignition_controller"].labels["rl_ctrl_tail"]
    controller_expected = f"uncovered wrapper branch {zero_edges[0]:#010x}->{tail:#010x}"
    try:
        require_wrapper_coverage(records, fixture, parsed_by_unit, regions, boundaries, invoke_words,
                                 base_hooks["cruise_feedback_serializer"].stock,
                                 rolling_layout.hook_by_key["primary_ignition_command"].stock)
    except VerificationError as error:
        if str(error) != controller_expected:
            raise VerificationError(f"controller bypass fails outside its omitted outcome: {error}") from error
    else:
        raise VerificationError("controller coverage accepts the real zero-band bypass")
    idle_case = (
        "    set_ignition_state(PHASE_IDLE, MODE_OBSERVE, 0);\n"
        "    if (!invoke_ignition(\"ign-inactive\", 110, 316, 110))"
    )
    if source.count(idle_case) != 1:
        raise VerificationError("adapter negative lacks its unique idle case")
    adapter_negative_text = source.replace(
        idle_case,
        "    set_ignition_state(PHASE_ACTIVE, MODE_OBSERVE, 0);\n"
        "    if (!invoke_ignition(\"ign-inactive\", 110, 316, 110))",
    )
    adapter_parsed = parsed_by_unit["ignition_adapter"]
    phase_edge = next(
        row for row in adapter_parsed.statements
        if row.kind == "instruction" and row.text == "bf rl_ign_tail"
        and adapter_parsed.statement_by_address[row.address - 2].text == "cmp/eq 0x1,r0")
    phase_target = map_switching_assembly._validate_direct_branch_encoding(
        adapter_parsed, phase_edge,
        int.from_bytes(fixture[phase_edge.address:phase_edge.address + 2], "big"))
    adapter_expected = f"uncovered wrapper branch {phase_edge.address:#010x}->{phase_target:#010x}"
    adapter_negative_source = build_dir / "rolling-launch-bypass-adapter-idle.c"
    adapter_negative_source.write_text(adapter_negative_text, encoding="utf-8")
    adapter_negative_elf = build_dir / "rolling-launch-bypass-adapter-idle.elf"
    adapter_negative_command = list(command)
    adapter_negative_command[adapter_negative_command.index("-o") + 1] = adapter_negative_elf
    adapter_negative_command[adapter_negative_command.index(positive)] = adapter_negative_source
    base_verifier.run_command(adapter_negative_command, timeout=120)
    require_separate_storage(adapter_negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
    adapter_negative, records, invoke_words = execute(adapter_negative_elf)
    if marker not in adapter_negative.stdout:
        raise VerificationError("adapter bypass does not preserve the semantic PASS marker")
    try:
        require_wrapper_coverage(records, fixture, parsed_by_unit, regions, boundaries, invoke_words,
                                 base_hooks["cruise_feedback_serializer"].stock,
                                 rolling_layout.hook_by_key["primary_ignition_command"].stock)
    except VerificationError as error:
        if str(error) != adapter_expected:
            raise VerificationError(f"adapter bypass fails outside its omitted outcome: {error}") from error
    else:
        raise VerificationError("adapter coverage accepts the real idle bypass")
    held_map = (
        "    write_u16(rom_pointer(RL_CONFIG), 0);\n"
        "    ram_pointer(SELECTOR_STATE)[0] = 5;\n"
        "    run_engine();\n"
        "    if (!expect_phase_reason(\n"
        "            \"gate-config-and-map-index\", PHASE_IDLE, REASON_CONFIG_INVALID))"
    )
    if source.count(held_map) != 1:
        raise VerificationError("engine negative lacks its unique held-map case")
    engine_negative_text = source.replace(
        held_map,
        "    write_u16(rom_pointer(RL_CONFIG), 0);\n"
        "    ram_pointer(SELECTOR_STATE)[0] = 0;\n"
        "    run_engine();\n"
        "    if (!expect_phase_reason(\n"
        "            \"gate-config-and-map-index\", PHASE_IDLE, REASON_CONFIG_INVALID))",
    )
    engine_parsed = parsed_by_unit["engine"]
    map_edge = next(
        row for row in engine_parsed.statements
        if row.kind == "instruction" and row.text == "bf rl_gate_selector"
        and engine_parsed.statement_by_address[row.address + 2].text == "mov #0x2,r0")
    map_target = map_switching_assembly._validate_direct_branch_encoding(
        engine_parsed, map_edge,
        int.from_bytes(fixture[map_edge.address:map_edge.address + 2], "big"))
    engine_expected = f"uncovered wrapper branch {map_edge.address:#010x}->{map_target:#010x}"
    engine_negative_source = build_dir / "rolling-launch-bypass-engine-map.c"
    engine_negative_source.write_text(engine_negative_text, encoding="utf-8")
    engine_negative_elf = build_dir / "rolling-launch-bypass-engine-map.elf"
    engine_negative_command = list(command)
    engine_negative_command[engine_negative_command.index("-o") + 1] = engine_negative_elf
    engine_negative_command[engine_negative_command.index(positive)] = engine_negative_source
    base_verifier.run_command(engine_negative_command, timeout=120)
    require_separate_storage(engine_negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
    engine_negative, records, invoke_words = execute(engine_negative_elf)
    if marker not in engine_negative.stdout:
        raise VerificationError("engine bypass does not preserve the semantic PASS marker")
    try:
        require_wrapper_coverage(records, fixture, parsed_by_unit, regions, boundaries, invoke_words,
                                 base_hooks["cruise_feedback_serializer"].stock,
                                 rolling_layout.hook_by_key["primary_ignition_command"].stock)
    except VerificationError as error:
        if str(error) != engine_expected:
            raise VerificationError(f"engine bypass fails outside its omitted outcome: {error}") from error
    else:
        raise VerificationError("engine coverage accepts the real held-map bypass")
    if (source_path.read_text(encoding="utf-8") != source
            or positive.read_text(encoding="utf-8") != source
            or negative_source.read_text(encoding="utf-8") != negative_text
            or controller_negative_source.read_text(encoding="utf-8") != controller_negative_text
            or adapter_negative_source.read_text(encoding="utf-8") != adapter_negative_text
            or engine_negative_source.read_text(encoding="utf-8") != engine_negative_text):
        raise VerificationError("Rolling Launch harness source changes during verification")
    measured = "VQ_SH_ELF_ROLLING_WRAPPER_COVERAGE status=PASS scope=JK08A:"
    measured += ",".join(COVERAGE_REGIONS) + " " + " ".join(f"{key}={value}" for key, value in covered.items())
    return "\n".join((result.stdout.strip(), measured,
                      f"VQ_SH_ELF_ROLLING_WRAPPER_NEGATIVE status=PASS {expected}",
                      f"VQ_SH_ELF_ROLLING_CONTROLLER_NEGATIVE status=PASS {controller_expected}",
                      f"VQ_SH_ELF_ROLLING_ADAPTER_NEGATIVE status=PASS {adapter_expected}",
                      f"VQ_SH_ELF_ROLLING_ENGINE_NEGATIVE status=PASS {engine_expected}"))


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
            fixture, build_dir, parsed_by_unit=parsed, composed_image=composition.data,
            base_layout=base_layout, rolling_layout=rolling_layout,
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
