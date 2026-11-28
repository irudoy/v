#!/usr/bin/env python3
"""Verify exact JK08A Rolling Launch instructions with GNU SH-2E tools.

The gate binds every tracked unit to an independently GNU-assembled blob and
the locked composition, then runs the rows that rolling_launch_rows.py
derives from the schema 6 model in the GNU simulator. A PC trace of the run
must execute every instruction of the covered units, both outcomes of every
conditional branch, every delay slot, every call site with its return, and
every target that a register transfer loads. Three negative runs remove one
covered path each and must fail coverage at exactly that path.

The gate does not execute the ignition adapter, the spark-cut actuator, or
the spark-event helpers; the rolling_ignition stage executes them
functionally. The GR11B timing margin and vehicle acceptance remain open in
issue #150.
"""

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

import rolling_launch_interrupts
import rolling_launch_rows
import verify_map_switching as base_verifier
from elf_storage_layout import ELFStorageError, require_separate_storage

from patches import map_switching_assembly
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout


EXPECTED_COMPOSITION_SHA256 = (
    "34988f873bc1a0051862db941d6522f68749ce0427011f9961f0a7354465911e"
)
EXPECTED_COMPOSITION_CHANGED_BYTES = 3882
EXPECTED_COMPOSITION_WRITE_BYTES = 4904
EXPECTED_INSTRUCTION_COUNT = 1707
EXPECTED_CODE_ENTRY_COUNT = 16
EXPECTED_DIAGNOSTIC_COUNT = 12
RETURN_STUB = bytes.fromhex("000b0009")
# The stock unsigned divider runs unstubbed: r0=divisor, r1=dividend.
STOCK_UNSIGNED_DIVIDER = 0x00021CE0
# Simulator-only stock serializer: it stores 0xb5 in the ASCD status byte
# 0xFFFF3ADA of the serialized frame and returns at offset 6.
FEEDBACK_SERIALIZER_STUB = bytes.fromhex(
    "d103e0b52100000b00090009000901003ada"
)
COVERAGE_UNITS = (
    "wrappers", "engine", "speed_controller", "feedback_arbiter", "rpm",
    "actuation", "slot_validator", "state_check",
)
COVERAGE_REGIONS = (
    "periodic_wrapper", "selector_arbiter", "startup_wrapper", "engine",
    "speed_controller", "feedback_arbiter", "rpm_controller", "rpm_fraction",
    "control_publisher", "ignition_publisher", "actuation", "slot_validator",
    "state_check",
)
# Entries that the harness calls through invoke_regs. The engine also runs
# through the periodic wrapper, and the controllers only from the engine.
HARNESS_ENTRIES = (
    "periodic_wrapper", "selector_arbiter", "startup_wrapper", "engine",
    "feedback_arbiter", "rpm_fraction", "control_publisher", "ignition_publisher",
)
INVOKE_SYMBOLS = frozenset({"_invoke_regs"})
CONDITIONAL = {"bt": 2, "bf": 2, "bt/s": 4, "bf/s": 4}
UNSUPPORTED_CONTROL = {"braf", "bsrf", "rte", "trapa", "sleep", "jsr/n", "rts/n"}
COMPARE_ONLY = {"cmp/eq", "cmp/hs", "cmp/ge", "cmp/hi", "cmp/gt", "cmp/pz", "cmp/pl",
                "cmp/str", "tst"}
JSR_MASK, JSR_WORD = 0xF0FF, 0x400B
BSR_MASK, BSR_WORD = 0xF000, 0xB000
BSRF_MASK, BSRF_WORD = 0xF0FF, 0x0003
RTS_WORD, RTE_WORD = 0x000B, 0x002B
SEMANTIC_PREFIX = "VQ_SH_ELF_ROLLING_LAUNCH status=PASS"
# Fixed harness cases besides the model rows: the startup wrapper and four
# selector-arbiter rows.
WRAPPER_CASES = 5


class VerificationError(RuntimeError):
    """Raised when the Rolling Launch executable contract fails."""


def assemble_all_units(layout, parsed_by_unit, build_dir, verbose=False):
    """GNU-assemble every new unit and require tracked byte identity."""
    tracked = rolling_launch_assembly.load_payloads(layout)
    assembled = {}
    for unit in layout.assembly_units:
        blob = base_verifier.assemble_unit(unit, parsed_by_unit[unit.key], build_dir)
        digest = hashlib.sha256(blob).hexdigest()
        if blob != tracked[unit.key]:
            first = next(index for index, (actual, expected)
                         in enumerate(zip(blob, tracked[unit.key])) if actual != expected)
            raise VerificationError(
                f"{unit.key}: GNU output differs from tracked payload at "
                f"ROM address {unit.span.start + first:#x}")
        if digest != unit.expected_sha256:
            raise VerificationError(
                f"{unit.key}: GNU SHA-256 is {digest}, expected {unit.expected_sha256}")
        if verbose:
            print(f"GNU_ASSEMBLY rolling_launch_unit={unit.key} bytes={len(blob)} sha256={digest}")
        assembled[unit.key] = blob
    return assembled


def require_composition(layout, blobs):
    """Compose and lock the non-flashable Rolling Launch endpoint."""
    result = rolling_launch_compose.compose(layout=layout, blobs=blobs)
    actual = (result.sha256, result.changed_bytes, result.permitted_write_bytes,
              result.instruction_count, result.code_entry_count, result.diagnostic_count)
    expected = (EXPECTED_COMPOSITION_SHA256, EXPECTED_COMPOSITION_CHANGED_BYTES,
                EXPECTED_COMPOSITION_WRITE_BYTES, EXPECTED_INSTRUCTION_COUNT,
                EXPECTED_CODE_ENTRY_COUNT, EXPECTED_DIAGNOSTIC_COUNT)
    if actual != expected:
        raise VerificationError(
            f"Rolling Launch composition differs: actual={actual} expected={expected}")
    return result


def install_stock_return_stubs(fixture, base_layout, rolling_layout):
    """Stub the external stock callees of the Rolling Launch layer.

    The displaced periodic task, the stock ASCD host, the stock startup
    initializer and the primary ignition consumer return at once, and the
    serializer stores its fixed ASCD status byte.
    """
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
        raise VerificationError(f"Rolling Launch stock stub targets differ: {sorted(targets)}")
    if base_layout.eeprom_persistence is not None:
        targets.add(base_layout.eeprom_persistence.stock_sci2_acquire)
        targets.add(base_layout.eeprom_persistence.stock_sci2_release)
    for address in targets:
        fixture[address:address + len(RETURN_STUB)] = RETURN_STUB
    serializer = base_hooks["cruise_feedback_serializer"].stock
    if serializer != 0x000C5372:
        raise VerificationError(f"feedback serializer target differs: {serializer:#x}")
    fixture[serializer:serializer + len(FEEDBACK_SERIALIZER_STUB)] = FEEDBACK_SERIALIZER_STUB
    return len(targets) + 1


def build_dynamic_fixture(composition, rolling_parsed, base_layout, rolling_layout):
    """Apply documented simulator-only transformations after byte identity."""
    fixture = bytearray(composition.data)
    if len(fixture) != base_verifier.ROM_SIZE:
        raise VerificationError(
            f"composition size is {len(fixture)}, expected {base_verifier.ROM_SIZE}")
    base_parsed = map_switching_assembly.validate_assembly_sources(base_layout)
    base_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, base_parsed, keep_mmio=(base_layout.eeprom_persistence is not None)
    )
    rolling_relocated = base_verifier.relocate_assembly_ram_literals(fixture, rolling_parsed)
    differentiated = base_verifier.differentiate_map_copies(fixture, base_layout)
    stubs = install_stock_return_stubs(fixture, base_layout, rolling_layout)
    return bytes(fixture), base_relocated, rolling_relocated, differentiated, stubs


def build_rom_object(fixture, build_dir):
    fixture_path = build_dir / "rolling-launch.sim-fixture"
    object_path = build_dir / "rolling-launch-rom.o"
    fixture_path.write_bytes(fixture)
    base_verifier.run_command([
        base_verifier.OBJCOPY, "-I", "binary", "-O", "elf32-sh", "-B", "sh",
        "--rename-section", ".data=.rom,alloc,load,code,data,contents",
        fixture_path, object_path,
    ])
    return object_path


def _writes(text, register):
    """Whether one instruction can change ``register``."""
    mnemonic = text.split(None, 1)[0].lower()
    operands = text.split(None, 1)[1].lower() if " " in text else ""
    if mnemonic in COMPARE_ONLY:
        return False
    if mnemonic in {"jsr", "bsr"}:
        return int(register[1:]) <= 7
    if f"@{register}+" in operands or f"@-{register}" in operands:
        return True
    return operands.rsplit(",", 1)[-1].strip() == register


UNCONDITIONAL = {"bra", "braf", "jmp", "rts", "rte"}
LOCAL_BRANCHES = {"bt", "bf", "bt/s", "bf/s", "bra"}


def _transfer_targets(parsed, row, fixture):
    """Return the literal targets that can reach one JSR or JMP register.

    The scan walks the control-flow predecessors of the transfer inside its
    unit. Each path ends at a PC-relative long load into the register, whose
    literal is a target; a path that reaches another write of the register,
    the unit entry or a call fails the binding. Execution must reach each
    collected target, and a target outside the set fails the trace.
    """
    register = row.text.split("@", 1)[1].strip().lower()
    statements = [item for item in parsed.statements if item.kind == "instruction"]
    index_by_address = {item.address: index for index, item in enumerate(statements)}
    mnemonics = [item.text.split(None, 1)[0].lower() for item in statements]
    sources = {}
    for index, item in enumerate(statements):
        if mnemonics[index] in LOCAL_BRANCHES:
            target = parsed.labels[item.text.split()[1]]
            delayed = mnemonics[index] in {"bra", "bt/s", "bf/s"}
            sources.setdefault(target, []).append(index + 1 if delayed else index)

    def predecessors(index):
        found = list(sources.get(statements[index].address, ()))
        if index and not (index >= 2 and mnemonics[index - 2] in UNCONDITIONAL):
            found.append(index - 1)
        return found

    targets, visited = set(), set()
    pending = predecessors(index_by_address[row.address])
    if not pending:
        raise VerificationError(f"unbound register transfer at {row.address:#010x}")
    while pending:
        index = pending.pop()
        if index in visited:
            continue
        visited.add(index)
        item = statements[index]
        literal = map_switching_assembly.PC_RELATIVE_RE.fullmatch(item.text)
        if (literal and literal.group("width") == "l"
                and literal.group("register").lower() == register):
            pool = parsed.labels[literal.group("label")]
            targets.add(int.from_bytes(fixture[pool:pool + 4], "big"))
            continue
        if _writes(item.text, register) or mnemonics[index] in {"jsr", "bsr", "jmp", "rts"}:
            raise VerificationError(f"unbound register transfer at {row.address:#010x}")
        found = predecessors(index)
        if not found:
            raise VerificationError(f"unbound register transfer at {row.address:#010x}")
        pending.extend(found)
    return frozenset(targets)


def coverage_model(fixture, parsed_by_unit, regions):
    """Return the static obligations of the covered units."""
    spans = [(regions[key].span.start, regions[key].span.end) for key in COVERAGE_REGIONS]
    model = dict(instructions={}, outcomes=set(), slots=set(), branches={}, calls=set(),
                 transfers={}, sequential=set(), direct={}, entries=set(), spans=spans)
    model["entries"] = {regions[key].entry for key in COVERAGE_REGIONS}
    for unit in COVERAGE_UNITS:
        parsed = parsed_by_unit[unit]
        for row in parsed.statements:
            if row.kind != "instruction":
                continue
            pc = row.address
            if sum(start <= pc < end for start, end in spans) != 1:
                raise VerificationError(f"covered instruction lacks its region at {pc:#010x}")
            word = int.from_bytes(fixture[pc:pc + 2], "big")
            model["instructions"][pc] = word
            mnemonic = map_switching_assembly._mnemonic(row)
            if mnemonic in UNSUPPORTED_CONTROL:
                raise VerificationError(f"unsupported covered control form at {pc:#010x}")
            if mnemonic in map_switching_assembly.DELAYED_CONTROL_MNEMONICS:
                model["slots"].add(pc + 2)
            if mnemonic in CONDITIONAL:
                target = map_switching_assembly._validate_direct_branch_encoding(parsed, row, word)
                fall = pc + CONDITIONAL[mnemonic]
                model["branches"][pc] = (mnemonic.endswith("/s"), target, fall)
                model["outcomes"].update(((pc, target), (pc, fall)))
            elif mnemonic in {"bra", "bsr"}:
                target = map_switching_assembly._validate_direct_branch_encoding(parsed, row, word)
                model["direct"][pc] = target
                if mnemonic == "bsr":
                    model["calls"].add(pc)
                    model["entries"].add(target)
            elif mnemonic in {"jsr", "jmp"}:
                targets = _transfer_targets(parsed, row, fixture)
                model["transfers"][pc] = (mnemonic, targets)
                if mnemonic == "jsr":
                    model["calls"].add(pc)
            elif mnemonic != "rts":
                model["sequential"].add(pc)
    return model


GAP_MESSAGES = {
    "entry": "uncovered entry {pc:#010x}",
    "branch": "uncovered branch {pc:#010x}->{target:#010x}",
    "instruction": "uncovered instruction {pc:#010x}",
    "slot": "uncovered delay slot {pc:#010x}",
    "transfer": "uncovered register transfer {pc:#010x}->{target:#010x}",
    "call": "uncovered call return {pc:#010x}",
}


def gap_message(kind, pc, target=None):
    return GAP_MESSAGES[kind].format(pc=pc, target=target)


def coverage_obligations(model, span=None):
    """Every coverage obligation of the static model as (kind, pc, target), in
    reporting order, or only those whose instruction lies in ``span``."""
    items = ([("entry", pc, None) for pc in sorted(model["entries"])]
             + [("branch", pc, target) for pc, target in sorted(model["outcomes"])]
             + [("instruction", pc, None) for pc in sorted(model["instructions"])]
             + [("slot", pc, None) for pc in sorted(model["slots"])]
             + [("transfer", pc, target)
                for pc, (_kind, targets) in sorted(model["transfers"].items())
                for target in sorted(targets)]
             + [("call", pc, None) for pc in sorted(model["calls"])])
    return [item for item in items if span is None or span[0] <= item[1] < span[1]]


def coverage_gaps(records, fixture, model, invoke_words, harness_entries):
    """Walk one PC trace against the static model and return the message of
    every unmet obligation. Execution outside the model raises."""
    instructions = model["instructions"]
    spans = model["spans"]

    def successor(index, delayed):
        try:
            return base_verifier._trace_successor(records, index, delayed)
        except base_verifier.VerificationError as error:
            raise VerificationError(str(error)) from error

    seen, outcomes, slots, returned, taken, frames = set(), set(), set(), set(), set(), []
    for index, (pc, word, delay) in enumerate(records):
        expected = (int.from_bytes(fixture[pc:pc + 2], "big") if 0 <= pc < len(fixture) - 1
                    else invoke_words.get(pc))
        if expected is None or word != expected:
            raise VerificationError(f"executed opcode differs at {pc:#010x}")
        if pc not in instructions and any(start <= pc < end for start, end in spans):
            raise VerificationError(f"executed covered data at {pc:#010x}")
        if delay:
            if not index or records[index - 1][0] != pc - 2 or records[index - 1][2]:
                raise VerificationError(f"orphan delay slot at {pc:#010x}")
            slots.add(pc)
            if pc in instructions:
                seen.add(pc)
            continue
        if pc in instructions:
            seen.add(pc)
            if pc in model["sequential"] and successor(index, False) != pc + 2:
                raise VerificationError(f"executed sequential successor differs at {pc:#010x}")
            if pc in model["branches"]:
                delayed, target, fall = model["branches"][pc]
                following = successor(index, delayed)
                if following not in (target, fall):
                    raise VerificationError(f"executed branch differs at {pc:#010x}")
                outcomes.add((pc, following))
            if pc in model["direct"] and successor(index, True) != model["direct"][pc]:
                raise VerificationError(f"executed direct branch differs at {pc:#010x}")
            if pc in model["transfers"]:
                following = successor(index, True)
                if following not in model["transfers"][pc][1]:
                    raise VerificationError(f"executed register transfer differs at {pc:#010x}")
                taken.add((pc, following))
        is_call = (word & JSR_MASK == JSR_WORD or word & BSR_MASK == BSR_WORD
                   or word & BSRF_MASK == BSRF_WORD)
        if is_call:
            target = successor(index, True)
            if pc in invoke_words and target not in harness_entries:
                raise VerificationError(f"invoke calls an undeclared entry {target:#010x}")
            frames.append((pc, pc + 4))
        elif word == RTS_WORD:
            if not frames:
                if pc not in invoke_words:
                    raise VerificationError(f"return lacks its call at {pc:#010x}")
                continue
            call, continuation = frames.pop()
            if successor(index, True) != continuation:
                raise VerificationError(f"executed return differs at {pc:#010x}")
            if call in instructions:
                returned.add(call)
        elif word == RTE_WORD:
            raise VerificationError(f"exception return without an exception at {pc:#010x}")
    if frames:
        raise VerificationError("trace ends inside a call")
    met = ({("entry", pc, None) for pc in seen} | {("instruction", pc, None) for pc in seen}
           | {("branch", pc, target) for pc, target in outcomes}
           | {("slot", pc, None) for pc in slots}
           | {("transfer", pc, target) for pc, target in taken}
           | {("call", pc, None) for pc in returned})
    return [gap_message(*item) for item in coverage_obligations(model) if item not in met]


def require_coverage(records, fixture, model, invoke_words, harness_entries):
    """Walk one PC trace against the static model and require full coverage."""
    gaps = coverage_gaps(records, fixture, model, invoke_words, harness_entries)
    if gaps:
        raise VerificationError(gaps[0])
    return dict(entries=len(model["entries"]), instructions=len(model["instructions"]),
                outcomes=len(model["outcomes"]), delay_slots=len(model["slots"]),
                call_return_paths=len(model["calls"]),
                register_transfers=sum(len(targets) for _kind, targets
                                       in model["transfers"].values()))


UNCONDITIONAL_TRANSFERS = frozenset({"bra", "braf", "jmp", "rts", "rte"})


def omitted_path(parsed, text, model):
    """Gap messages of the fall-through edge of one unique source branch and of
    the block that only this edge reaches.

    The block starts at the fall-through and ends at the next label, where
    other paths join, or after the delay slot of the next unconditional
    transfer.
    """
    rows = [row for row in parsed.statements if row.kind == "instruction"]
    matches = [index for index, row in enumerate(rows) if row.text == text]
    if len(matches) != 1:
        raise VerificationError(f"negative edge {text!r} is not unique")
    branch = rows[matches[0]]
    start = branch.address + (4 if branch.text.split()[0].endswith("/s") else 2)
    labels = set(parsed.labels.values())
    end, transfer = start, False
    for row in rows[matches[0] + 1:]:
        if row.address < start:
            continue
        if row.address != end or row.address in labels:
            break
        end = row.address + row.size
        if transfer:
            break
        transfer = row.text.split()[0] in UNCONDITIONAL_TRANSFERS
    if (branch.address, start) not in model["outcomes"]:
        raise VerificationError(f"negative edge {text!r} is not a branch outcome")
    edge = ("branch", branch.address, start)
    return [gap_message(*item) for item in coverage_obligations(model)
            if item == edge or start <= item[1] < end]


def harness_cases(rows):
    """Return the case count of the semantic PASS marker of one row set."""
    return (sum(rolling_launch_rows.counts(rows).values()) + WRAPPER_CASES
            + rolling_launch_rows.FEEDBACK_CASES)


def harness_definitions(rolling_layout, base_layout):
    """Compiler definitions of the ROM areas that the harnesses load: the
    Rolling Launch configuration and efficiency table and the Map Switching
    feedback phase counts."""
    return (f"-DRL_CONFIG={rolling_layout.configuration.start:#010x}U",
            f"-DRL_TABLE={rolling_layout.efficiency.start:#010x}U",
            f"-DFEEDBACK_COUNTS={base_layout.feedback.phase_counts_address:#010x}U")


def build_and_run_dynamic_harness(fixture, build_dir, *, parsed_by_unit, composed_image,
                                  rolling_layout, base_layout):
    """Run the model rows, measure coverage and run the negative variants."""
    regions = rolling_layout.code_region_by_key
    definitions = harness_definitions(rolling_layout, base_layout)
    model = coverage_model(fixture, parsed_by_unit, regions)
    for pc in model["instructions"]:
        if fixture[pc:pc + 2] != composed_image[pc:pc + 2]:
            raise VerificationError(f"simulator changes a covered instruction at {pc:#010x}")
    for unit in COVERAGE_UNITS:
        for row in parsed_by_unit[unit].statements:
            literal = (map_switching_assembly.PC_RELATIVE_RE.fullmatch(row.text)
                       if row.kind == "instruction" else None)
            if literal is None or literal.group("width") != "l":
                continue
            pool = parsed_by_unit[unit].labels[literal.group("label")]
            value = int.from_bytes(composed_image[pool:pool + 4], "big")
            if value < 0xFFFF0000 and fixture[pool:pool + 4] != composed_image[pool:pool + 4]:
                raise VerificationError(f"simulator changes a ROM literal at {pool:#010x}")
    harness_entries = {regions[key].entry for key in HARNESS_ENTRIES}

    rom_object = build_rom_object(fixture, build_dir)
    invoke_object = build_dir / "rolling-launch-invoke.o"
    base_verifier.run_command([
        base_verifier.AS, "--big", "--isa=sh2e", "-o", invoke_object, TOOL_DIR / "invoke_rolling.s",
    ])
    source_path = TOOL_DIR / "rolling_launch_harness.c"
    source = source_path.read_text(encoding="utf-8")

    def build(variant):
        name = variant or "positive"
        include = build_dir / f"rows-{name}"
        include.mkdir()
        rows = rolling_launch_rows.build(variant)
        (include / "rolling_launch_rows.h").write_text(
            rolling_launch_rows.render(rows), encoding="utf-8")
        elf = build_dir / f"rolling-launch-{name}.elf"
        base_verifier.run_command([
            base_verifier.GCC, "-m2e", "-mb", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            *definitions, f"-I{include}", f"-Wl,-Ttext-segment={base_verifier.DRIVER_TEXT_BASE:#x}",
            "-Wl,--section-start=.rom=0", "-o", elf, source_path, invoke_object, rom_object,
        ], timeout=120)
        has_eeprom = getattr(base_layout, "eeprom_persistence", None) is not None
        storage_regions = (
            ((base_verifier.TEST_RAM_BASE, 65536),
             (base_verifier.M95320_BASE, base_verifier.M95320_SIZE))
            if has_eeprom
            else ((base_verifier.TEST_RAM_BASE, 65536),)
        )
        try:
            require_separate_storage(elf, storage_regions)
        except (ELFStorageError, OSError) as error:
            raise VerificationError(f"rolling-launch: ELF storage separation: {error}") from error
        return elf, rows

    def execute(elf):
        try:
            ranges, invoke_words = base_verifier._invoke_trace_bindings(
                elf, invoke_object, fixture, build_dir, names=INVOKE_SYMBOLS)
            trace = build_dir / f"{elf.stem}.pc-trace"
            environment = {**os.environ, "VQ_SH_PC_TRACE_FILE": str(trace),
                           "VQ_SH_PC_TRACE_FORMAT": "v1",
                           "VQ_SH_PC_TRACE_RANGES": ",".join(
                               f"{start:x}:{end:x}" for start, end in ((0, len(fixture)), *ranges))}
            run_args = [base_verifier.RUN, f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k"]
            if getattr(base_layout, "eeprom_persistence", None) is not None:
                environment["VQ_SH_HIGH_RAM_BASE"] = f"{base_verifier.TEST_RAM_BASE:#x}"
                environment["VQ_SH_M95320_BASE"] = f"{base_verifier.M95320_BASE:#x}"
                run_args.append(f"--memory-region={base_verifier.M95320_BASE:#x},8k")
            run_args.append(elf)
            before = elf.read_bytes()
            result = base_verifier.run_command(
                run_args, timeout=300, env=environment)
            if elf.read_bytes() != before:
                raise VerificationError("Rolling Launch ELF changes during execution")
            return result, base_verifier.read_pc_trace(trace), invoke_words
        except base_verifier.VerificationError as error:
            raise VerificationError(str(error)) from error

    def marker(rows):
        counts = rolling_launch_rows.counts(rows)
        return (f"{SEMANTIC_PREFIX} cases={harness_cases(rows)} engine={counts['engine']} "
                f"ignition={counts['ignition']} control={counts['control']} "
                f"fraction={counts['fraction']} wrappers={WRAPPER_CASES} "
                f"feedback={rolling_launch_rows.FEEDBACK_CASES}")

    elf, rows = build(None)
    result, records, invoke_words = execute(elf)
    if marker(rows) not in result.stdout.splitlines():
        raise VerificationError("Rolling Launch harness returned zero without the exact marker"
                                + (f"\n{result.stdout.rstrip()}" if result.stdout else ""))
    covered = require_coverage(records, fixture, model, invoke_words, harness_entries)
    interrupts = rolling_launch_interrupts.run_interrupt_rows(
        fixture, build_dir, engine=regions["engine"].entry,
        regulator=(regions["rpm_controller"].span.start, regions["control_publisher"].span.end),
        definitions=definitions, invoke_object=invoke_object, rom_object=rom_object)

    # The periodic variant leaves every obligation of the periodic wrapper
    # unmet, its entry first; each other variant leaves exactly its omitted
    # edge and the block that only the edge reaches.
    periodic = regions["periodic_wrapper"].span
    negatives = (
        ("periodic", [gap_message(*item) for item in coverage_obligations(
            model, (periodic.start, periodic.end))]),
        ("controller", omitted_path(parsed_by_unit["speed_controller"],
                                    rolling_launch_rows.CONTROLLER_NEGATIVE_EDGE, model)),
        ("engine", omitted_path(parsed_by_unit["engine"],
                                rolling_launch_rows.ENGINE_NEGATIVE_EDGE, model)),
    )
    if negatives[0][1][0] != f"uncovered entry {regions['periodic_wrapper'].entry:#010x}":
        raise VerificationError("the periodic wrapper entry is not its first obligation")
    lines = [result.stdout.strip(),
             "VQ_SH_ELF_ROLLING_COVERAGE status=PASS scope=JK08A:" + ",".join(COVERAGE_REGIONS)
             + " " + " ".join(f"{key}={value}" for key, value in covered.items()),
             interrupts]
    for variant, expected in negatives:
        negative_elf, negative_rows = build(variant)
        negative, records, invoke_words = execute(negative_elf)
        if marker(negative_rows) not in negative.stdout.splitlines():
            raise VerificationError(f"{variant} variant does not keep the semantic PASS marker"
                                    + (f"\n{negative.stdout.rstrip()}" if negative.stdout else ""))
        gaps = coverage_gaps(records, fixture, model, invoke_words, harness_entries)
        if not gaps:
            raise VerificationError(f"coverage accepts the {variant} variant")
        if gaps != expected:
            extra = [gap for gap in gaps if gap not in expected]
            missing = [gap for gap in expected if gap not in gaps]
            raise VerificationError(f"{variant} variant leaves gaps outside its omitted path: "
                                    f"extra {extra}, missing {missing}")
        lines.append(f"VQ_SH_ELF_ROLLING_NEGATIVE status=PASS variant={variant} "
                     f"gaps={len(gaps)} {gaps[0]}")
    if source_path.read_text(encoding="utf-8") != source:
        raise VerificationError("Rolling Launch harness source changes during verification")
    return "\n".join(lines), rows


def verify(verbose=False, check_toolchain=True):
    simulator = None
    gcc_version = None
    if check_toolchain:
        simulator, gcc_version = base_verifier.require_toolchain_version()
    base_layout = map_switching_layout.load_layout()
    rolling_layout = rolling_launch_layout.load_layout()
    parsed = rolling_launch_assembly.validate_assembly_sources(rolling_layout)
    with tempfile.TemporaryDirectory(prefix="vq-sh-elf-rolling-launch-") as directory:
        build_dir = Path(directory)
        blobs = assemble_all_units(rolling_layout, parsed, build_dir, verbose=verbose)
        audit = rolling_launch_assembly.validate_instruction_semantics(rolling_layout, parsed, blobs)
        composition = require_composition(rolling_layout, blobs)
        fixture, base_relocated, rolling_relocated, differentiated, stubs = build_dynamic_fixture(
            composition, parsed, base_layout, rolling_layout)
        dynamic_marker, dynamic_rows = build_and_run_dynamic_harness(
            fixture, build_dir, parsed_by_unit=parsed, composed_image=composition.data,
            rolling_layout=rolling_layout, base_layout=base_layout)

    print(dynamic_marker)
    print(
        "VQ_SH_ELF_ROLLING_VERIFY status=PASS"
        f" units={len(rolling_layout.assembly_units)}"
        f" covered_units={len(COVERAGE_UNITS)}"
        f" instructions={audit.instructions}"
        f" delayed_transfers={audit.delayed_transfers}"
        f" pc_relative_references={audit.pc_relative_references}"
        f" direct_branches={audit.direct_branches}"
        f" indirect_transfers={audit.indirect_transfers}"
        f" composition_sha256={composition.sha256}"
        f" model_rows={sum(rolling_launch_rows.counts(dynamic_rows).values())}"
        f" diagnostics={composition.diagnostic_count}"
        f" base_ram_literals_relocated={base_relocated}"
        f" rolling_ram_literals_relocated={rolling_relocated}"
        f" differentiated_bytes={differentiated}"
        f" stock_stubs={stubs}"
    )
    if verbose and simulator is not None:
        print(f"ROLLING_TOOLCHAIN {simulator} gcc={gcc_version}")
    return {"composition": composition, "audit": audit,
            "dynamic_cases": harness_cases(dynamic_rows)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true",
                        help="print each independently assembled unit digest")
    args = parser.parse_args(argv)
    try:
        verify(verbose=args.verbose)
    except (OSError, ValueError, VerificationError) as error:
        print(f"VQ_SH_ELF_ROLLING_VERIFY status=FAIL error={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
