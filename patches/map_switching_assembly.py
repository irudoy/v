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
# `.include "<name>"` names a generated header of this directory. Its
# `#define NAME value` lines whose value is one number define symbols that
# later statements write in place of the number; a define of another value
# serves C alone.
INCLUDE_RE = re.compile(r'^\.include\s+"(?P<name>[A-Za-z0-9_.-]+\.h)"$')
DEFINE_RE = re.compile(r"^#define\s+(?P<name>[A-Z][A-Z0-9_]*)\s+(?P<value>.+)$")
SYMBOL_RE = re.compile(r"(?<![A-Za-z0-9_])[A-Z][A-Z0-9_]*(?![A-Za-z0-9_])")
INCLUDE_DIR = Path(__file__).resolve().parent
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
    "cmp/ge",
    "cmp/gt",
    "cmp/hi",
    "cmp/hs",
    "cmp/pl",
    "cmp/pz",
    "dt",
    "exts.b",
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
    "muls.w",
    "mulu.w",
    "neg",
    "nop",
    "not",
    "or",
    "rte",
    "rts",
    "shar",
    "shll",
    "shll2",
    "shll8",
    "shll16",
    "shlr",
    "shlr2",
    "shlr8",
    "shlr16",
    "stc",
    "sts.l",
    "sts",
    "sub",
    "tst",
    "xor",
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


def _header_symbols(name, path, line_number):
    """Return the integer symbols of one included header."""
    try:
        header = (INCLUDE_DIR / name).read_text(encoding="utf-8")
    except OSError as error:
        raise ValueError(
            f"{path}:{line_number}: cannot read the included {name}"
        ) from error
    symbols = {}
    for header_line, raw_line in enumerate(header.splitlines(), 1):
        line = _strip_comment(raw_line).strip()
        if not line:
            continue
        match = DEFINE_RE.fullmatch(line)
        if match is None:
            raise ValueError(
                f"{name}:{header_line}: an included header holds only "
                "comments and #define lines"
            )
        try:
            symbols[match["name"]] = _number(match["value"])
        except ValueError:
            continue
    return symbols


def expand_includes(source, path="<source>"):
    """Return `source` with each `.include` line blanked and the integer
    symbols of its header written as hexadecimal numbers after it.

    The statements, the GNU input, and the assembled bytes are those of the
    numbers themselves, and every line keeps its number.
    """
    symbols = {}
    lines = []
    for line_number, raw_line in enumerate(source.splitlines(), 1):
        match = INCLUDE_RE.fullmatch(_strip_comment(raw_line).strip())
        if match:
            symbols.update(
                _header_symbols(match["name"], path, line_number)
            )
            lines.append("")
            continue
        if symbols:
            raw_line = SYMBOL_RE.sub(
                lambda item: (
                    f"0x{symbols[item[0]]:X}"
                    if item[0] in symbols
                    else item[0]
                ),
                raw_line,
            )
        lines.append(raw_line)
    return "\n".join(lines) + "\n"


def _values(text, path, line_number):
    values = [value.strip() for value in text.split(",")]
    if not values or any(not value for value in values):
        raise ValueError(f"{path}:{line_number}: invalid data directive")
    return values


def parse_source_text(source, path, start, end):
    """Parse the deliberately small SH-2E source subset this module accepts."""
    path = Path(path)
    labels = {}
    statements = []
    cursor = start
    for line_number, raw_line in enumerate(
        expand_includes(source, path).splitlines(), 1
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
    literals = {
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
    if layout.cruise_free is not None:
        cf = layout.cruise_free
        literals.pop("host_diagnostic_status")
        literals.update({
            "host_ascd_enabled": code["cruise_free_ascd_enabled"].entry,
            "host_cf_finalize": code["cruise_free_step"].entry,
            "startup_cruise_free_init": code["cruise_free_startup_init"].entry,
            "feedback_mil_byte": cf.mil_byte_address,
            "feedback_cf_ext": code["cruise_free_feedback_ext"].entry,
            "cf_init_ram": cf.ram.start,
            "stat_stock_rx_dispatch": hooks["stationary_rx_dispatch"].stock,
            "stat_cf_ram": cf.ram.start,
            "stat_port_state": cf.port_state_address,
            "stat_hcan1_state": cf.hcan1_state_address,
            "stat_rx_state": cf.rx_state_address,
            "stat_rx_raw_hi": cf.rx_raw_speed_address,
            "stat_config_addr": cf.config.start,
            "cf_ram_base": cf.ram.start,
            "cf_config_base": cf.config.start,
            "cf_selector_state": layout.ram.selector.start,
            "cf_limiter_commit": code["limiter_commit"].entry,
            "cf_diag_status": cf.diagnostic_state_address,
            "cf_rpm_fine": cf.rpm_fine_address,
            "cf_rpm_coarse": cf.rpm_coarse_address,
            "cf_brake_byte": cf.brake_address,
            "cf_app1_addr": cf.app1_address,
            "cf_app2_addr": cf.app2_address,
            "cf_magic_word": 0x4D534346,
            "cf_sentinel_word": 0xA55A5AA5,
            "cf_unobserved": 0x00FFFFFF,
            "ascd_en_cf_ram": cf.ram.start,
            "ascd_en_cfg": cf.config.start,
            "ascd_en_sel": layout.ram.selector.start,
            "fbext_config": cf.config.start,
            "fbext_cf_ram": cf.ram.start,
            "fbext_rpm_fine": cf.rpm_fine_address,
            "fbext_rpm_coarse": cf.rpm_coarse_address,
            "cf_live_port": cf.port_state_address,
            "cf_live_hcan": cf.hcan1_state_address,
            "tach_stock_180": hooks["tach_180_serializer"].stock,
            "tach_180_payload": cf.tach_180_payload_address,
            "tach_stock_1f9": hooks["tach_1f9_serializer"].stock,
            "tach_1f9_payload": cf.tach_1f9_payload_address,
            "tach_config": cf.config.start,
            "tach_cf_ram": cf.ram.start,
            "tach_rpm_fine": cf.rpm_fine_address,
            "tach_rpm_coarse": cf.rpm_coarse_address,
        })
    if layout.eeprom_persistence is not None:
        ee = layout.eeprom_persistence
        literals.pop("startup_cruise_free_init")
        if ee.startup_cold_return_pc is not None:
            literals.update({
                "startup_can_pr": ee.startup_can_return_pc,
                "startup_cold_pr": ee.startup_cold_return_pc,
                "startup_eeprom_boot_restore": code["eeprom_boot_restore"].entry,
            })
        else:
            literals.update({
                "startup_eeprom_boot_restore": code["eeprom_boot_restore"].entry,
                "startup_warm_pr": 0x00027C4C,
            })
        literals.update({
            "ee_cruise_free_init_1": code["cruise_free_startup_init"].entry,
            "ee_ram_base_1": ee.ram.start,
            "ee_selector_state_1": layout.ram.selector.start,
            "ee_sci2_acquire_1": ee.stock_sci2_acquire,
            "ee_sci2_release_1": ee.stock_sci2_release,
            "ee_half_range_const": 0x80000000,
            "ee_ram_base_2": ee.ram.start,
            "ee_cfg_base_2": ee.config.start,
            "ee_selector_state_2": layout.ram.selector.start,
            "ee_stock_sched_2": hooks["eeprom_periodic_task"].stock,
            "ee_stock_busy_2": ee.stock_busy_address,
            "ee_sci2_acquire_2": ee.stock_sci2_acquire,
            "ee_sci2_release_2": ee.stock_sci2_release,
            "ee_valid_marker_2": 0xA65DC39E,
            "ee_cfg_addr_3": ee.config.start,
            "ee_cfg_magic_3": 0x4D535045,
            "ee_cfg_sentinel_3": 0x5AA5A55A,
            "ee_pldr_addr": ee.pldr_address,
            "ee_port_state_addr": ee.port_state_address,
            "ee_shutdown_req_addr": ee.shutdown_req_address,
            "ee_shutdown_state_addr": ee.shutdown_state_address,
            "ee_reinit_mode_addr": ee.reinit_mode_address,
            "ee_vbat_addr": ee.vbat_address,
            "ee_crc_poly": 0xEDB88320,
            "ee_valid_marker_3": 0xA65DC39E,
            "ee_pcdr_addr": ee.pcdr_address,
            "ee_sci2_base": ee.sci2_base_address,
        })
    return literals


def _labeled_literals(parsed, kind):
    statement_by_address = parsed.statement_by_address
    literals = {}
    for label, address in parsed.labels.items():
        statement = statement_by_address.get(address)
        if statement is None or statement.kind != kind:
            continue
        values = _values(
            statement.text, parsed.path, statement.line_number
        )
        if len(values) != 1:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: labeled .{kind} "
                "must contain one value"
            )
        literals[label] = _number(values[0])
    return literals


def _long_literals(parsed):
    return _labeled_literals(parsed, "long")


def _word_literals(parsed):
    return _labeled_literals(parsed, "word")


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


def _validate_startup_wrapper(parsed, layout):
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
    if layout.eeprom_persistence is not None:
        expected_calls = 4
    elif layout.cruise_free is not None:
        expected_calls = 3
    else:
        expected_calls = 2
    if len(jsr_indexes) != expected_calls or any(
        index + 1 >= len(texts) or texts[index + 1] != "nop"
        for index in jsr_indexes
    ):
        raise ValueError(
            f"{parsed.path}: startup calls need {expected_calls} JSR/NOP pairs"
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
    if layout.eeprom_persistence is not None:
        if not (
            preinitializer_zero < preinitializer_store < jsr_indexes[0]
            < jsr_indexes[1] < jsr_indexes[2]
            < commit_zero < jsr_indexes[3]
        ):
            raise ValueError(
                f"{parsed.path}: cold/warm startup publication/commit order differs"
            )
    elif not (
        preinitializer_zero < preinitializer_store < jsr_indexes[0]
        < commit_zero < jsr_indexes[1]
    ):
        raise ValueError(
            f"{parsed.path}: map-1 startup publication/commit order differs"
        )


def _validate_selector_host(parsed, layout):
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
    expected_calls = 5 if layout.cruise_free is not None else 3
    if len(jsr_indexes) != expected_calls or any(
        index + 1 >= len(texts) or texts[index + 1] != "nop"
        for index in jsr_indexes
    ):
        raise ValueError(
            f"{parsed.path}: selector host calls need {expected_calls} JSR/NOP pairs"
        )
    if layout.cruise_free is None and texts.count("mov.b r0,@r1") != 1:
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
    has_cf = layout.cruise_free is not None
    allowed = {f"r{number}" for number in range(8)} | (
        {"r15", "pr"} if has_cf else set()
    )
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: feedback engine "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    if has_cf:
        if texts[0] != "sts.l pr,@-r15":
            raise ValueError(
                f"{parsed.path}: feedback engine does not save PR"
            )
        if texts[-4:] != ["add 0x4,r15", "lds.l @r15+,pr", "rts", "nop"]:
            raise ValueError(
                f"{parsed.path}: feedback engine does not restore stack and PR"
            )
        jsr_indexes = [
            index for index, text in enumerate(texts) if text == "jsr @r0"
        ]
        if len(jsr_indexes) != 1:
            raise ValueError(
                f"{parsed.path}: feedback engine needs one JSR to cruise_free_feedback_ext"
            )
        if texts.count("mov.b r0,@r4") != 2:
            raise ValueError(
                f"{parsed.path}: multi-channel feedback engine must have two byte stores"
            )
        mil_clear = (~layout.cruise_free.mil_mask) & 0xFF
        canonical_mil = (
            texts.count(f"and {mil_clear:#x},r0") == 1
            and texts.count(f"mov #{layout.cruise_free.mil_mask:#x},r0") == 1
        )
        preserving_mil = (
            texts.count(f"or {layout.cruise_free.mil_mask:#x},r0") == 1
            and texts.count(f"and {mil_clear:#x},r0") == 0
        )
        valid_mil = canonical_mil if layout.rom == "JK08A" else preserving_mil
        if not valid_mil:
            raise ValueError(
                f"{parsed.path}: MIL mask handling differs"
            )
    else:
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


def _validate_cruise_free_selector(parsed, layout):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {f"r{number}" for number in range(8)} | {"r15", "pr"}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: cruise_free_selector "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    if texts.count("mov.b r0,@r1") != 1:
        raise ValueError(
            f"{parsed.path}: diagnostic mirror must have one byte store"
        )
    cf = layout.cruise_free
    if parsed.labels.get("cf_validate_cfg_local") != cf.config.start + 0x2E8:
        raise ValueError(
            f"{parsed.path}: cf_validate_cfg_local anchor differs"
        )
    live_call = f"bsr 0x{cf.config.start + 0x460:08x}"
    if (
        texts.count("jsr @r0") != 2
        or texts.count("bsr cf_validate_cfg_local") != 3
        or texts.count(live_call) != 2
    ):
        raise ValueError(
            f"{parsed.path}: cruise_free_selector call structure differs"
        )


def _validate_cruise_free_feedback(parsed, layout):
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {f"r{number}" for number in range(8)} | {"r15", "pr", "macl"}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: cruise_free_feedback "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    cf = layout.cruise_free
    if parsed.labels.get("cf_stationary_live") != cf.config.start + 0x460:
        raise ValueError(
            f"{parsed.path}: cf_stationary_live anchor differs"
        )
    val_call = f"bsr 0x{cf.config.start + 0x2E8:08x}"
    if (
        texts.count("jsr @r0") != 2
        or texts.count("bsr tach_override_apply") != 2
        or texts.count(val_call) != 2
        or texts.count("bsr cf_stationary_live") != 2
    ):
        raise ValueError(
            f"{parsed.path}: cruise_free_feedback wrapper call structure differs"
        )
    if texts.count("mulu.w r2,r3") != 1 or texts.count("sts macl,r1") != 1:
        raise ValueError(
            f"{parsed.path}: tachometer wire multiplication differs"
        )
    words = _word_literals(parsed)
    if words.get("tach_wire_step") != 0x1F40:
        raise ValueError(
            f"{parsed.path}: tach_wire_step literal must be 0x1F40"
        )


def _validate_eeprom_persistence(parsed, layout):
    ee = layout.eeprom_persistence
    if ee is None:
        raise ValueError(
            f"{parsed.path}: eeprom_persistence unit requires [eeprom_persistence]"
        )
    instructions = [
        item for item in parsed.statements if item.kind == "instruction"
    ]
    texts = [item.text.lower() for item in instructions]
    allowed = {f"r{number}" for number in range(13)} | {"r15", "pr"}
    for statement in instructions:
        forbidden = set(REGISTER_RE.findall(statement.text.lower())) - allowed
        if forbidden:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: eeprom_persistence "
                f"uses protected registers: {', '.join(sorted(forbidden))}"
            )
    words = _word_literals(parsed)
    expected_words = {
        "ee_page_a_const": ee.page_a_address,
        "ee_page_b_const": ee.page_b_address,
        "ee_page_a_2": ee.page_a_address,
        "ee_page_b_2": ee.page_b_address,
        "ee_cs_clear_mask": (~ee.pcdr_cs_mask) & 0xFFFF,
    }
    if words != expected_words:
        raise ValueError(
            f"{parsed.path}: eeprom_persistence word literals differ: "
            f"actual={words} expected={expected_words}"
        )
    if (
        "eeprom_boot_restore" not in parsed.labels
        or "eeprom_task_wrapper" not in parsed.labels
        or texts.count("jsr @r0") != 17
    ):
        raise ValueError(
            f"{parsed.path}: eeprom_persistence entry or JSR contract differs"
        )
    expected_immediates = {
        f"tst 0x{ee.pldr_ig_mask:x},r0",
        f"tst 0x{ee.ig_on_mask:x},r0",
        f"tst 0x{ee.start_mask:x},r0",
        f"tst 0x{ee.shutdown_req_mask:x},r0",
        f"or 0x{ee.pcdr_cs_mask:x},r0",
        (
            f"mov #-0x{(0x100 - ee.vbat_min_raw) & 0xFF:x},r3"
            if ee.vbat_min_raw >= 0x80
            else f"mov #0x{ee.vbat_min_raw:x},r3"
        ),
    }
    missing_immediates = expected_immediates - set(texts)
    if missing_immediates:
        raise ValueError(
            f"{parsed.path}: eeprom_persistence immediate operands disagree "
            f"with [eeprom_persistence]: {sorted(missing_immediates)}"
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
            _validate_selector_host(parsed, layout)
        elif unit.key == "cruise_feedback_wrapper":
            _validate_feedback_wrapper(parsed)
        elif unit.key == "cruise_feedback_engine":
            _validate_feedback_engine(parsed, layout)
        elif unit.key == "cruise_free_selector":
            _validate_cruise_free_selector(parsed, layout)
        elif unit.key == "cruise_free_feedback":
            _validate_cruise_free_feedback(parsed, layout)
        elif unit.key == "eeprom_persistence":
            _validate_eeprom_persistence(parsed, layout)
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
            _validate_startup_wrapper(parsed, layout)
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
