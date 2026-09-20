#!/usr/bin/env python3
"""Static contract checks for the JK08A map-switching SH assembly slices.

Ghidra remains the assembler and round-trip decoder. This module checks the
source-level address, ABI, literal, region-ownership, and delay-slot contract.
For SHA-locked Ghidra blobs it also decodes every control transfer and every
PC-relative reference independently from the machine word. It never assembles
code or writes a ROM.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches.map_switching_layout import (
    DEFAULT_MANIFEST,
    VQ37_VARIANTS,
    load_layout,
    validate_assembled_blob,
)


LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):$")
REGISTER_RE = re.compile(r"\b(?:r(?:1[0-5]|[0-9])|pr|gbr|sr|mach|macl)\b")
CONTROL_RE = re.compile(r"^(bra|bsr|bt|bf|jmp|jsr|rts)\b", re.IGNORECASE)
PC_RELATIVE_RE = re.compile(
    r"^(mov\.(?P<width>[wl])|mova)\s+"
    r"@\((?P<label>[A-Za-z_][A-Za-z0-9_]*),\s*pc\),"
    r"(?P<register>r(?:1[0-5]|[0-9]))$",
    re.IGNORECASE,
)
DIRECT_BRANCH_MNEMONICS = frozenset({
    "bra", "bsr", "bt", "bf", "bt/s", "bf/s",
})
INDIRECT_CONTROL_MNEMONICS = frozenset({
    "braf", "bsrf", "jmp", "jsr", "rts", "rte",
})
DELAYED_CONTROL_MNEMONICS = frozenset({
    "bra", "bsr", "braf", "bsrf", "jmp", "jsr", "rts", "rte",
    "bt/s", "bf/s",
})
ALLOWED_REGISTERS = {"r0", "r1", "r2", "r3", "r4"}

# Renesas REJ09B0177 section 2.4.1 lists these mnemonics for the
# SH-2E core in the SH7058S. Keeping the injected source inside this explicit
# subset prevents the SH-2A Ghidra assembler profile from admitting a newer
# instruction that the target silicon cannot execute.
SH7058S_SH2E_MNEMONICS = frozenset({
    "add",
    "and",
    "bf",
    "bra",
    "bsr",
    "bt",
    "cmp/eq",
    "cmp/hi",
    "cmp/hs",
    "dt",
    "extu.b",
    "extu.w",
    "jmp",
    "jsr",
    "ldc",
    "lds.l",
    "mov",
    "mov.b",
    "mov.l",
    "mov.w",
    "mulu.w",
    "nop",
    "not",
    "or",
    "rte",
    "rts",
    "shll",
    "shll2",
    "shlr8",
    "stc",
    "sts.l",
    "sts",
    "sub",
    "tst",
})


@dataclass(frozen=True)
class SourceStatement:
    line_number: int
    address: int
    kind: str
    text: str
    size: int


@dataclass(frozen=True)
class ParsedSource:
    path: Path
    labels: dict[str, int]
    statements: tuple[SourceStatement, ...]

    @property
    def instruction_count(self):
        return sum(item.kind == "instruction" for item in self.statements)

    @property
    def data_bytes(self):
        return sum(
            item.size
            for item in self.statements
            if item.kind != "instruction"
        )

    @property
    def statement_by_address(self):
        return {item.address: item for item in self.statements}


@dataclass(frozen=True)
class InstructionAudit:
    instructions: int
    delayed_transfers: int
    pc_relative_references: int
    direct_branches: int
    indirect_transfers: int


def _mnemonic(statement):
    return statement.text.split(None, 1)[0].lower()


def _sign_extend(value, bits):
    sign = 1 << (bits - 1)
    return (value ^ sign) - sign


def _source_target(parsed, statement):
    operand = statement.text.split(None, 1)[1].strip()
    if operand in parsed.labels:
        return parsed.labels[operand]
    try:
        return _number(operand)
    except ValueError as error:
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: unresolved control-flow "
            f"target {operand!r}"
        ) from error


def _validate_delay_slots(parsed, *, allow_tail_restore=False):
    """Require an audited instruction after every delayed SH-2E transfer."""
    statements = parsed.statement_by_address
    for statement in parsed.statements:
        if (
            statement.kind != "instruction"
            or _mnemonic(statement) not in DELAYED_CONTROL_MNEMONICS
        ):
            continue
        slot = statements.get(statement.address + 2)
        safe_tail_restore = (
            allow_tail_restore
            and statement.text.lower() == "jmp @r0"
            and slot is not None
            and slot.kind == "instruction"
            and slot.text.lower() == "mov.l @r15+,r0"
        )
        if (
            slot is None
            or slot.kind != "instruction"
            or (slot.text.lower() != "nop" and not safe_tail_restore)
        ):
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: "
                f"{_mnemonic(statement).upper()} delay slot is not NOP"
            )


def _validate_direct_branch_encoding(parsed, statement, word):
    mnemonic = _mnemonic(statement)
    if mnemonic in {"bra", "bsr"}:
        expected_prefix = 0xA000 if mnemonic == "bra" else 0xB000
        if word & 0xF000 != expected_prefix:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: {mnemonic.upper()} "
                f"machine word is {word:#06x}"
            )
        displacement = _sign_extend(word & 0x0FFF, 12)
    else:
        prefixes = {
            "bt": 0x8900,
            "bf": 0x8B00,
            "bt/s": 0x8D00,
            "bf/s": 0x8F00,
        }
        if word & 0xFF00 != prefixes[mnemonic]:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: {mnemonic.upper()} "
                f"machine word is {word:#06x}"
            )
        displacement = _sign_extend(word & 0x00FF, 8)
    actual = statement.address + 4 + displacement * 2
    expected = _source_target(parsed, statement)
    if actual != expected:
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: {mnemonic.upper()} "
            f"targets {actual:#x}, expected {expected:#x}"
        )
    return actual


def _register_number(text, prefix):
    match = re.fullmatch(
        re.escape(prefix) + r"\s+@?r(?P<register>1[0-5]|[0-9])",
        text,
        re.IGNORECASE,
    )
    if match is None:
        raise ValueError(f"invalid {prefix.upper()} register operand: {text}")
    return int(match.group("register"))


def _validate_indirect_control_encoding(parsed, statement, word):
    mnemonic = _mnemonic(statement)
    text = statement.text.lower()
    if mnemonic == "rts":
        expected = 0x000B
    elif mnemonic == "rte":
        expected = 0x002B
    else:
        register = _register_number(text, mnemonic)
        suffixes = {
            "braf": 0x0023,
            "bsrf": 0x0003,
            "jmp": 0x402B,
            "jsr": 0x400B,
        }
        expected = suffixes[mnemonic] | register << 8
    if word != expected:
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: {mnemonic.upper()} "
            f"machine word is {word:#06x}, expected {expected:#06x}"
        )


def _validate_pc_relative_encoding(parsed, statement, word):
    match = PC_RELATIVE_RE.fullmatch(statement.text)
    if match is None:
        return False
    label = match.group("label")
    if label not in parsed.labels:
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: unresolved PC-relative "
            f"label {label!r}"
        )
    mnemonic = _mnemonic(statement)
    register = int(match.group("register")[1:])
    displacement = word & 0xFF
    if mnemonic == "mov.w":
        if word & 0xF000 != 0x9000 or (word >> 8) & 0xF != register:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: MOV.W PC-relative "
                f"machine word is {word:#06x}"
            )
        actual = statement.address + 4 + displacement * 2
        expected_kind = "word"
    elif mnemonic == "mov.l":
        if word & 0xF000 != 0xD000 or (word >> 8) & 0xF != register:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: MOV.L PC-relative "
                f"machine word is {word:#06x}"
            )
        actual = ((statement.address + 4) & ~3) + displacement * 4
        expected_kind = "long"
    else:
        if word & 0xFF00 != 0xC700 or register != 0:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: MOVA PC-relative "
                f"machine word is {word:#06x}"
            )
        actual = ((statement.address + 4) & ~3) + displacement * 4
        expected_kind = None
    expected = parsed.labels[label]
    if actual != expected:
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: PC-relative reference "
            f"resolves to {actual:#x}, expected {expected:#x}"
        )
    target = parsed.statement_by_address.get(expected)
    if expected_kind is not None and (
        target is None or target.kind != expected_kind
    ):
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: PC-relative {mnemonic} "
            f"target {label!r} is not .{expected_kind} data"
        )
    if expected_kind == "long" and expected & 3:
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: MOV.L literal is not "
            "four-byte aligned"
        )
    if expected_kind == "word" and expected & 1:
        raise ValueError(
            f"{parsed.path}:{statement.line_number}: MOV.W literal is not "
            "two-byte aligned"
        )
    return True


def validate_source_blob(
    parsed, blob, start, valid_instruction_addresses=None,
    *, allow_tail_restore=False,
):
    """Independently audit control flow and PC-relative machine encodings."""
    blob = bytes(blob)
    _validate_sh7058s_instruction_subset(parsed)
    _validate_delay_slots(parsed, allow_tail_restore=allow_tail_restore)
    instruction_addresses = {
        statement.address
        for statement in parsed.statements
        if statement.kind == "instruction"
    }
    valid_targets = (
        instruction_addresses
        if valid_instruction_addresses is None
        else set(valid_instruction_addresses)
    )
    delayed = 0
    pc_relative = 0
    direct = 0
    indirect = 0
    for statement in parsed.statements:
        if statement.kind != "instruction":
            continue
        offset = statement.address - start
        if offset < 0 or offset + 2 > len(blob):
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: instruction bytes "
                "are outside the supplied blob"
            )
        word = int.from_bytes(blob[offset : offset + 2], "big")
        mnemonic = _mnemonic(statement)
        if mnemonic in DELAYED_CONTROL_MNEMONICS:
            delayed += 1
            slot_offset = offset + 2
            slot = parsed.statement_by_address.get(statement.address + 2)
            safe_tail_restore = (
                allow_tail_restore
                and statement.text.lower() == "jmp @r0"
                and slot is not None
                and slot.kind == "instruction"
                and slot.text.lower() == "mov.l @r15+,r0"
                and blob[slot_offset : slot_offset + 2] == b"\x60\xf6"
            )
            if (
                slot_offset + 2 > len(blob)
                or (
                    blob[slot_offset : slot_offset + 2] != b"\x00\x09"
                    and not safe_tail_restore
                )
            ):
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: binary "
                    f"{mnemonic.upper()} delay slot is not NOP"
                )
        if _validate_pc_relative_encoding(parsed, statement, word):
            pc_relative += 1
        if mnemonic in DIRECT_BRANCH_MNEMONICS:
            target = _validate_direct_branch_encoding(parsed, statement, word)
            if target not in valid_targets:
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: branch target "
                    f"{target:#x} is not a declared instruction"
                )
            direct += 1
        elif mnemonic in INDIRECT_CONTROL_MNEMONICS:
            _validate_indirect_control_encoding(parsed, statement, word)
            indirect += 1
    return InstructionAudit(
        instructions=parsed.instruction_count,
        delayed_transfers=delayed,
        pc_relative_references=pc_relative,
        direct_branches=direct,
        indirect_transfers=indirect,
    )


def validate_instruction_semantics(layout, parsed_by_unit, blobs):
    """Audit every tracked instruction against the SHA-locked raw blobs."""
    all_instruction_addresses = {
        statement.address
        for parsed in parsed_by_unit.values()
        for statement in parsed.statements
        if statement.kind == "instruction"
    }
    audits = []
    for unit in layout.assembly_units:
        blob = validate_assembled_blob(unit, blobs[unit.key])
        audits.append(
            validate_source_blob(
                parsed_by_unit[unit.key],
                blob,
                unit.span.start,
                all_instruction_addresses,
            )
        )
    return InstructionAudit(
        instructions=sum(item.instructions for item in audits),
        delayed_transfers=sum(item.delayed_transfers for item in audits),
        pc_relative_references=sum(
            item.pc_relative_references for item in audits
        ),
        direct_branches=sum(item.direct_branches for item in audits),
        indirect_transfers=sum(item.indirect_transfers for item in audits),
    )


def _strip_comment(line):
    indexes = [
        index
        for marker in ("//", ";")
        if (index := line.find(marker)) >= 0
    ]
    return line[: min(indexes)] if indexes else line


def _number(text):
    value = text.strip().replace("_", "")
    if value.lower().startswith("0x"):
        return int(value, 16)
    return int(value, 10)


def _values(text, path, line_number):
    values = [value.strip() for value in text.split(",")]
    if not values or any(not value for value in values):
        raise ValueError(f"{path}:{line_number}: invalid data directive")
    return values


def parse_source_text(source, path, start, end):
    """Parse the deliberately small source subset accepted by AssembleSh2."""
    path = Path(path)
    labels = {}
    statements = []
    cursor = start
    for line_number, raw_line in enumerate(
        source.splitlines(), 1
    ):
        line = _strip_comment(raw_line).strip()
        if not line:
            continue
        match = LABEL_RE.fullmatch(line)
        if match:
            label = match.group(1)
            if label in labels:
                raise ValueError(f"{path}:{line_number}: duplicate {label}")
            labels[label] = cursor
            continue
        if line.startswith(".org "):
            address = _number(line[5:])
            if address < cursor:
                raise ValueError(
                    f"{path}:{line_number}: .org moves backward"
                )
            cursor = address
            if not start <= cursor <= end:
                raise ValueError(
                    f"{path}:{line_number}: .org is outside assembly unit"
                )
            continue
        if line.startswith(".align "):
            alignment = _number(line[7:])
            if alignment <= 0 or alignment & (alignment - 1):
                raise ValueError(
                    f"{path}:{line_number}: invalid .align"
                )
            cursor = (cursor + alignment - 1) & -alignment
            if cursor > end:
                raise ValueError(
                    f"{path}:{line_number}: alignment exceeds assembly unit"
                )
            continue

        directive = next(
            (
                (prefix, kind, width)
                for prefix, kind, width in (
                    (".byte ", "byte", 1),
                    (".word ", "word", 2),
                    (".long ", "long", 4),
                )
                if line.startswith(prefix)
            ),
            None,
        )
        if directive:
            prefix, kind, width = directive
            text = line[len(prefix) :].strip()
            size = width * len(_values(text, path, line_number))
        elif line.startswith("."):
            raise ValueError(
                f"{path}:{line_number}: unsupported directive"
            )
        else:
            kind = "instruction"
            text = line
            size = 2
            if cursor & 1:
                raise ValueError(
                    f"{path}:{line_number}: unaligned instruction"
                )
        if not start <= cursor or cursor + size > end:
            raise ValueError(
                f"{path}:{line_number}: statement is outside assembly unit"
            )
        statements.append(
            SourceStatement(line_number, cursor, kind, text, size)
        )
        cursor += size
    return ParsedSource(path, labels, tuple(statements))


def parse_source(path, start, end):
    """Parse one tracked assembly source file."""
    path = Path(path)
    return parse_source_text(
        path.read_text(encoding="utf-8"), path, start, end
    )


def _hook_stock_for_adapter(layout, adapter_key):
    entry = layout.code_region_by_key[adapter_key].entry
    stocks = {
        hook.stock
        for hook in layout.hooks
        if hook.replacement == entry
    }
    if len(stocks) != 1:
        raise ValueError(
            f"{adapter_key}: expected one stock wrapper, found {stocks}"
        )
    return stocks.pop()


def _expected_long_literals(layout):
    family = layout.family_by_key
    hooks = {hook.key: hook for hook in layout.hooks}
    code = layout.code_region_by_key
    fuel_cut = family["rev_limit_fuel_cut"]
    throttle = family["rev_limit_throttle_cut"]
    return {
        "host_stock_function": hooks["selector_host_call"].stock,
        "host_selector_state": layout.ram.selector.start,
        "host_current_code": 0xFFFF2A85,
        "host_ascd_status": 0xFFFF41AE,
        "host_diagnostic_status": 0xFFFF2A84,
        "host_limiter_commit": code["limiter_commit"].entry,
        "feedback_stock_serializer": layout.feedback.serializer,
        "feedback_engine_entry":
            code["cruise_feedback_engine"].entry,
        "feedback_selector_state": layout.ram.selector.start,
        "feedback_status_byte": layout.feedback.status_byte_address,
        "selector_state_address": layout.ram.selector.start,
        "startup_stock_initializer": hooks["startup_initializer"].stock,
        "startup_selector_state": layout.ram.selector.start,
        "startup_commit_entry": code["limiter_commit"].entry,
        "overrun_cut_base":
            family["over_run_fuel_cut"].canonical_address,
        "overrun_restore_base":
            family["over_run_fuel_restore"].canonical_address,
        "overrun_stock_wrapper": 0x00026388,
        "overrun_cut_pointers":
            family["over_run_fuel_cut"].pointer_table,
        "overrun_restore_pointers":
            family["over_run_fuel_restore"].pointer_table,
        "full_dfco_hold_base":
            family["over_run_fuel_hold"].canonical_address,
        "full_dfco_entry_base":
            family["over_run_fuel_cut"].canonical_address,
        "full_dfco_full_restore_base":
            family["over_run_fuel_restore"].canonical_address,
        "full_dfco_intermediate_restore_base":
            family["over_run_fuel_intermediate_restore"].canonical_address,
        "full_dfco_stock_wrapper":
            _hook_stock_for_adapter(layout, "full_dfco_adapter"),
        "full_dfco_hold_pointers":
            family["over_run_fuel_hold"].pointer_table,
        "full_dfco_entry_pointers":
            family["over_run_fuel_cut"].pointer_table,
        "full_dfco_full_restore_pointers":
            family["over_run_fuel_restore"].pointer_table,
        "full_dfco_intermediate_restore_pointers":
            family["over_run_fuel_intermediate_restore"].pointer_table,
        "high_octane_timing_state_base":
            family["high_octane_timing_state"].canonical_address,
        "high_detonation_timing_state_base":
            family["high_detonation_timing_state"].canonical_address,
        "ignition_stock_wrapper":
            _hook_stock_for_adapter(layout, "ignition_adapter"),
        "high_octane_timing_state_pointers":
            family["high_octane_timing_state"].pointer_table,
        "high_detonation_timing_state_pointers":
            family["high_detonation_timing_state"].pointer_table,
        "fuel_compensation_base":
            family["fuel_compensation_main"].canonical_address,
        "fuel_compensation_stock_wrapper":
            _hook_stock_for_adapter(
                layout, "fuel_compensation_adapter"
            ),
        "fuel_compensation_pointers":
            family["fuel_compensation_main"].pointer_table,
        "cvtc_target_base":
            family["exhaust_cvtc_target"].canonical_address,
        "cvtc_target_stock_wrapper":
            _hook_stock_for_adapter(
                layout, "cvtc_target_adapter"
            ),
        "cvtc_target_pointers":
            family["exhaust_cvtc_target"].pointer_table,
        "cold_idle_ignition_base":
            family["cold_idle_ignition_timing"].canonical_address,
        "idle_ignition_base":
            family["idle_ignition_timing"].canonical_address,
        "idle_ignition_stock_wrapper":
            _hook_stock_for_adapter(layout, "idle_ignition_adapter"),
        "map_switching_selector":
            code["adapter_select_helper"].entry,
        "cold_idle_ignition_pointers":
            family["cold_idle_ignition_timing"].pointer_table,
        "idle_ignition_pointers":
            family["idle_ignition_timing"].pointer_table,
        "fuel_cut_pointer_table": fuel_cut.pointer_table,
        "fuel_cut_shadow": fuel_cut.shadow_start,
        "fuel_cut_stock_tail":
            fuel_cut.stock_container_start + fuel_cut.byte_length,
        "throttle_stock_cluster": throttle.stock_container_start,
        "throttle_shadow": throttle.shadow_start,
        "throttle_pointer_table": throttle.pointer_table,
        "throttle_selected_shadow":
            throttle.shadow_start + throttle.selected_offset,
        "throttle_runtime_scalar": throttle.runtime_shadow_address,
        "selector_state": layout.ram.selector.start,
    }


def _long_literals(parsed):
    statement_by_address = parsed.statement_by_address
    literals = {}
    for label, address in parsed.labels.items():
        statement = statement_by_address.get(address)
        if statement is None or statement.kind != "long":
            continue
        values = _values(
            statement.text, parsed.path, statement.line_number
        )
        if len(values) != 1:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: labeled .long "
                "must contain one value"
            )
        literals[label] = _number(values[0])
    return literals


def _validate_registers_and_control_flow(
    parsed, helper_entry, *, allowed_jump_registers=("r3",)
):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    for index, statement in enumerate(instructions):
        text = statement.text.lower()
        registers = set(REGISTER_RE.findall(text))
        forbidden = registers - ALLOWED_REGISTERS
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: protected "
                f"registers used: {', '.join(sorted(forbidden))}"
            )
        control = CONTROL_RE.match(text)
        if not control:
            continue
        mnemonic = control.group(1)
        if mnemonic in {"bsr", "jsr", "rts"}:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: "
                f"{mnemonic} changes the adapter call contract"
            )
        if mnemonic == "bra":
            operand = text.split(None, 1)[1]
            if _number(operand) != helper_entry:
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: "
                    "external branch does not target the shared helper"
                )
            if index + 1 >= len(instructions) or (
                instructions[index + 1].text.lower() != "nop"
            ):
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: "
                    "BRA delay slot is not NOP"
                )
        elif mnemonic == "jmp":
            if text not in {
                f"jmp @{register}" for register in allowed_jump_registers
            }:
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: "
                    "tail jump uses an unapproved register"
                )
            if index + 1 >= len(instructions) or (
                instructions[index + 1].text.lower() != "nop"
            ):
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: "
                    "JMP delay slot is not NOP"
                )


def _instruction_texts(parsed):
    return [
        item.text.lower()
        for item in parsed.statements
        if item.kind == "instruction"
    ]


def _validate_sh7058s_instruction_subset(parsed):
    for statement in parsed.statements:
        if statement.kind != "instruction":
            continue
        mnemonic = statement.text.split(None, 1)[0].lower()
        if mnemonic not in SH7058S_SH2E_MNEMONICS:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: instruction "
                f"{mnemonic} is outside the audited SH7058S SH-2E subset"
            )


def _validate_limiter_commit(parsed, variant="single-cvtc"):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {f"r{number}" for number in range(8)} | {"sr"}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: limiter commit "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    if texts[0] != "stc sr,r7" or texts[-2:] != ["rts", "nop"]:
        raise ValueError(
            f"{parsed.path}: limiter commit does not save SR first and "
            "return through RTS/NOP"
        )
    if any(text.startswith(("jsr ", "bsr ")) for text in texts):
        raise ValueError(f"{parsed.path}: limiter commit must be a leaf")
    try:
        mask = texts.index("ldc r0,sr")
        publish = texts.index("mov.b r4,@r5")
        restore = texts.index("ldc r7,sr")
    except ValueError as error:
        raise ValueError(
            f"{parsed.path}: limiter commit lacks mask/publish/restore"
        ) from error
    stores = [
        index
        for index, text in enumerate(texts)
        if re.match(r"^mov\.[bwl]\s+r[0-7],@", text)
    ]
    if not stores or not mask < stores[0] <= stores[-1] == publish < restore:
        raise ValueError(
            f"{parsed.path}: runtime writes are outside the SR-protected "
            "publication interval"
        )
    if texts.count("mov.b r4,@r5") != 1:
        raise ValueError(
            f"{parsed.path}: active index must be published exactly once"
        )
    if variant in VQ37_VARIANTS:
        if (
            texts.count("mov.w @r2,r0") != 1
            or texts.count("mov.w r0,@r5") != 1
            or texts.count("mov #0x2,r1") != 1
            or texts.count("mov #0x10,r1") != 1
            or texts.count("mov.w @r2+,r6") != 2
            or texts.count("mov.w r6,@r5") != 2
            or texts.count("dt r1") != 2
            or "fuel_cap_copy_loop" not in parsed.labels
            or "fuel_curve_copy_loop" not in parsed.labels
            or "fuel_cap_pointer_table" not in parsed.labels
            or "fuel_curve_pointer_table" not in parsed.labels
            or "fuel_cap_shadow" not in parsed.labels
            or "fuel_curve_shadow" not in parsed.labels
        ):
            raise ValueError(
                f"{parsed.path}: VQ37 limiter must atomically commit the "
                "native fuel caps, both eight-point curves, and one "
                "throttle scalar"
            )
    elif (
        "mov.w @r2+,r0" not in texts
        or "mov.w @r5+,r0" not in texts
        or any(text.startswith("mov.l @r2") for text in texts)
    ):
        raise ValueError(
            f"{parsed.path}: the 2-byte-aligned fuel cluster must use "
            "word copies"
        )


def _validate_startup_wrapper(parsed):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {"r0", "r1", "r4", "r15", "pr"}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: startup wrapper "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    if texts[0] != "sts.l pr,@-r15":
        raise ValueError(f"{parsed.path}: startup wrapper does not save PR")
    if texts[-3:] != ["lds.l @r15+,pr", "rts", "nop"]:
        raise ValueError(
            f"{parsed.path}: startup wrapper does not restore PR"
        )
    jsr_indexes = [
        index for index, text in enumerate(texts) if text == "jsr @r0"
    ]
    if len(jsr_indexes) != 2 or any(
        index + 1 >= len(texts) or texts[index + 1] != "nop"
        for index in jsr_indexes
    ):
        raise ValueError(
            f"{parsed.path}: startup calls need two JSR/NOP pairs"
        )
    if texts.count("mov #0x0,r0") != 1 or texts.count("mov #0x0,r4") != 1:
        raise ValueError(
            f"{parsed.path}: startup wrapper must select map 1 before "
            "and after the stock initializer"
        )
    try:
        preinitializer_store = texts.index("mov.b r0,@r1")
    except ValueError as error:
        raise ValueError(
            f"{parsed.path}: startup wrapper does not publish map 1 "
            "before the stock initializer"
        ) from error
    preinitializer_zero = texts.index("mov #0x0,r0")
    commit_zero = texts.index("mov #0x0,r4")
    if not (
        preinitializer_zero < preinitializer_store < jsr_indexes[0]
        < commit_zero < jsr_indexes[1]
    ):
        raise ValueError(
            f"{parsed.path}: map-1 startup publication/commit order differs"
        )


def _validate_selector_host(parsed):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {f"r{number}" for number in range(8)} | {"r15", "pr"}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: selector host "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    if texts[0] != "sts.l pr,@-r15":
        raise ValueError(f"{parsed.path}: selector host does not save PR")
    if texts[-3:] != ["lds.l @r15+,pr", "rts", "nop"]:
        raise ValueError(f"{parsed.path}: selector host does not restore PR")
    jsr_indexes = [
        index for index, text in enumerate(texts) if text == "jsr @r0"
    ]
    if len(jsr_indexes) != 3 or any(
        index + 1 >= len(texts) or texts[index + 1] != "nop"
        for index in jsr_indexes
    ):
        raise ValueError(
            f"{parsed.path}: selector host calls need three JSR/NOP pairs"
        )
    if texts.count("mov.b r0,@r1") != 1:
        raise ValueError(
            f"{parsed.path}: diagnostic mirror must have one byte store"
        )


def _validate_feedback_wrapper(parsed):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {"r0", "r15", "pr"}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: feedback wrapper "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    if texts[0] != "sts.l pr,@-r15":
        raise ValueError(f"{parsed.path}: feedback wrapper does not save PR")
    if texts[-3:] != ["lds.l @r15+,pr", "rts", "nop"]:
        raise ValueError(
            f"{parsed.path}: feedback wrapper does not restore PR"
        )
    jsr_indexes = [
        index for index, text in enumerate(texts) if text == "jsr @r0"
    ]
    if len(jsr_indexes) != 2 or any(
        index + 1 >= len(texts) or texts[index + 1] != "nop"
        for index in jsr_indexes
    ):
        raise ValueError(
            f"{parsed.path}: feedback calls need two JSR/NOP pairs"
        )


def _validate_feedback_engine(parsed, layout):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {f"r{number}" for number in range(8)}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: feedback engine "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    if any(text.startswith(("jsr ", "bsr ")) for text in texts):
        raise ValueError(f"{parsed.path}: feedback engine must be a leaf")
    if texts[-2:] != ["rts", "nop"]:
        raise ValueError(f"{parsed.path}: feedback engine lacks RTS/NOP")
    if texts.count("mov.b r0,@r4") != 1:
        raise ValueError(
            f"{parsed.path}: feedback status must have one byte store"
        )
    clear_mask = (~layout.feedback.status_mask) & 0xFF
    if texts.count(f"and {clear_mask:#x},r0") != 1:
        raise ValueError(
            f"{parsed.path}: feedback status clear mask differs"
        )
    if texts.count(
        f"mov #{layout.feedback.lamp_on_value:#x},r0"
    ) != 1:
        raise ValueError(
            f"{parsed.path}: feedback lamp-on value differs"
        )
    if layout.feedback.lamp_off_value != 0:
        raise ValueError(
            f"{parsed.path}: feedback lamp-off value must be zero"
        )
    config_address = parsed.labels.get("feedback_phase_counts")
    statement = parsed.statement_by_address.get(config_address)
    expected = (
        layout.feedback.payload_on_frames << 8
        | layout.feedback.payload_off_frames
    )
    if (
        config_address != layout.feedback.phase_counts_address
        or statement is None
        or statement.kind != "word"
        or _number(statement.text) != expected
    ):
        raise ValueError(
            f"{parsed.path}: feedback frame-count configuration differs"
        )


def _validate_secondary_cvtc_adapter(parsed):
    _validate_registers_and_control_flow(parsed, 0)
    texts = _instruction_texts(parsed)
    required = {
        "mov #0x5,r1",
        "cmp/hs r1,r0",
        "mov #0x0,r0",
        "shll2 r0",
        "mov.l @(r0,r2),r4",
        "jmp @r3",
        "nop",
    }
    if not required <= set(texts):
        raise ValueError(
            f"{parsed.path}: second CVTC adapter contract differs"
        )
    if texts.count("jmp @r3") != 2:
        raise ValueError(
            f"{parsed.path}: second CVTC adapter tail count differs"
        )


def _validate_ignition_state_adapter(parsed):
    _validate_registers_and_control_flow(parsed, 0)
    texts = _instruction_texts(parsed)
    required = {
        "mov #0x5,r1",
        "cmp/hs r1,r0",
        "mov #0x0,r0",
        "shll2 r0",
        "mov.l @(r0,r2),r4",
        "jmp @r3",
        "nop",
    }
    if not required <= set(texts):
        raise ValueError(
            f"{parsed.path}: ignition state adapter contract differs"
        )
    if texts.count("cmp/eq r0,r4") != 4 or texts.count("jmp @r3") != 2:
        raise ValueError(
            f"{parsed.path}: ignition state adapter branch count differs"
        )


def validate_assembly_sources(layout=None):
    """Cross-check all implemented source slices with the exact layout."""
    layout = layout or load_layout()
    source_dir = DEFAULT_MANIFEST.parent
    literal_by_unit = layout.source_literal_by_unit
    expected_literals = (
        {
            key: value
            for values in literal_by_unit.values()
            for key, value in values.items()
        }
        if literal_by_unit
        else _expected_long_literals(layout)
    )
    actual_literals = {}
    parsed_by_unit = {}
    source_texts = layout.source_text_by_unit

    for unit in layout.assembly_units:
        source_path = source_dir / unit.source
        if unit.key in source_texts:
            parsed = parse_source_text(
                source_texts[unit.key],
                source_path,
                unit.span.start,
                unit.span.end,
            )
        else:
            parsed = parse_source(
                source_path, unit.span.start, unit.span.end
            )
        parsed_by_unit[unit.key] = parsed
        _validate_sh7058s_instruction_subset(parsed)
        _validate_delay_slots(parsed)
        if parsed.instruction_count != unit.instruction_count:
            raise ValueError(
                f"{unit.key}: source has {parsed.instruction_count} "
                f"instructions, expected {unit.instruction_count}"
            )
        if parsed.data_bytes != unit.data_bytes:
            raise ValueError(
                f"{unit.key}: source has {parsed.data_bytes} data bytes, "
                f"expected {unit.data_bytes}"
            )
        for key in unit.code_regions:
            entry = layout.code_region_by_key[key].entry
            if parsed.labels.get(key) != entry:
                raise ValueError(
                    f"{unit.key}: label {key} does not match "
                    f"entry {entry:#x}"
                )
        if unit.key == "selector_host":
            _validate_selector_host(parsed)
        elif unit.key == "cruise_feedback_wrapper":
            _validate_feedback_wrapper(parsed)
        elif unit.key == "cruise_feedback_engine":
            _validate_feedback_engine(parsed, layout)
        elif unit.key in {
            "adapter_select_helper",
            "lookup_adapters",
            "full_dfco_adapter",
            "idle_ignition_adapter",
        }:
            _validate_registers_and_control_flow(
                parsed,
                layout.code_region_by_key["adapter_select_helper"].entry,
                allowed_jump_registers=(
                    ("r0", "r3")
                    if unit.key == "idle_ignition_adapter"
                    else ("r3",)
                ),
            )
        elif unit.key == "limiter_commit":
            _validate_limiter_commit(parsed, layout.variant)
        elif unit.key == "startup_wrapper":
            _validate_startup_wrapper(parsed)
        elif unit.key == "secondary_cvtc_adapter":
            _validate_secondary_cvtc_adapter(parsed)
        elif unit.key == "ignition_state_adapter":
            _validate_ignition_state_adapter(parsed)
        else:
            raise ValueError(
                f"{unit.key}: no source-level ABI validator is registered"
            )
        overlap = actual_literals.keys() & _long_literals(parsed).keys()
        if overlap:
            raise ValueError(
                "assembly literal labels repeat: "
                + ", ".join(sorted(overlap))
            )
        actual_literals.update(_long_literals(parsed))

    if actual_literals != expected_literals:
        missing = expected_literals.keys() - actual_literals.keys()
        extra = actual_literals.keys() - expected_literals.keys()
        wrong = {
            key
            for key in expected_literals.keys() & actual_literals.keys()
            if expected_literals[key] != actual_literals[key]
        }
        raise ValueError(
            "assembly literals differ"
            f"; missing={sorted(missing)}"
            f"; extra={sorted(extra)}"
            f"; wrong={sorted(wrong)}"
        )
    return parsed_by_unit


def _blob_argument(text):
    key, separator, path = text.partition("=")
    if not separator or not key or not path:
        raise argparse.ArgumentTypeError("expected KEY=PATH")
    return key, Path(path)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blob",
        action="append",
        type=_blob_argument,
        default=[],
        metavar="KEY=PATH",
        help="validate one Ghidra output blob against its manifest SHA-256",
    )
    args = parser.parse_args(argv)
    layout = load_layout()
    parsed = validate_assembly_sources(layout)
    unit_by_key = layout.assembly_unit_by_key
    seen = set()
    blobs = {}
    all_instruction_addresses = {
        statement.address
        for unit_source in parsed.values()
        for statement in unit_source.statements
        if statement.kind == "instruction"
    }
    for key, path in args.blob:
        if key not in unit_by_key:
            parser.error(f"unknown assembly unit {key!r}")
        if key in seen:
            parser.error(f"duplicate blob for {key!r}")
        blob = validate_assembled_blob(unit_by_key[key], path)
        validate_source_blob(
            parsed[key],
            blob,
            unit_by_key[key].span.start,
            all_instruction_addresses,
        )
        blobs[key] = blob
        seen.add(key)
    audit = (
        validate_instruction_semantics(layout, parsed, blobs)
        if seen == set(unit_by_key)
        else None
    )
    print(
        "status=PASS"
        f" sources={len(parsed)}"
        f" instructions={sum(unit.instruction_count for unit in layout.assembly_units)}"
        f" data_bytes={sum(unit.data_bytes for unit in layout.assembly_units)}"
        f" blobs={len(seen)}"
        + (
            f" delayed_transfers={audit.delayed_transfers}"
            f" pc_relative_references={audit.pc_relative_references}"
            f" direct_branches={audit.direct_branches}"
            f" indirect_transfers={audit.indirect_transfers}"
            if audit is not None
            else ""
        )
    )


if __name__ == "__main__":
    main()
