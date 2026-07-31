#!/usr/bin/env python3
"""Static contract checks for the JK08A map-switching SH assembly slices.

Ghidra remains the assembler and round-trip decoder. This module checks the
source-level address, ABI, literal, region-ownership, and delay-slot contract,
and can validate raw Ghidra output blobs against the SHA-256 locks in the
authoritative layout. It never assembles code or writes a ROM.
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
    load_layout,
    validate_assembled_blob,
)


LABEL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):$")
REGISTER_RE = re.compile(r"\b(?:r(?:1[0-5]|[0-9])|pr|gbr|sr|mach|macl)\b")
CONTROL_RE = re.compile(r"^(bra|bsr|bt|bf|jmp|jsr|rts)\b", re.IGNORECASE)
ALLOWED_REGISTERS = {"r0", "r1", "r2", "r3", "r4"}


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


def parse_source(path, start, end):
    """Parse the deliberately small source subset accepted by AssembleSh2."""
    path = Path(path)
    labels = {}
    statements = []
    cursor = start
    for line_number, raw_line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
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
        "overrun_stock_wrapper":
            _hook_stock_for_adapter(layout, "overrun_adapter"),
        "overrun_cut_pointers":
            family["over_run_fuel_cut"].pointer_table,
        "overrun_restore_pointers":
            family["over_run_fuel_restore"].pointer_table,
        "ignition_main_base":
            family["ignition_timing_trim_main"].canonical_address,
        "ignition_high_det_base":
            family["ignition_timing_trim_high_det"].canonical_address,
        "ignition_stock_wrapper":
            _hook_stock_for_adapter(layout, "ignition_adapter"),
        "ignition_main_pointers":
            family["ignition_timing_trim_main"].pointer_table,
        "ignition_high_det_pointers":
            family["ignition_timing_trim_high_det"].pointer_table,
        "fuel_compensation_base":
            family["fuel_compensation_main"].canonical_address,
        "fuel_compensation_stock_wrapper":
            _hook_stock_for_adapter(
                layout, "fuel_compensation_adapter"
            ),
        "fuel_compensation_pointers":
            family["fuel_compensation_main"].pointer_table,
        "fuel_targets_base": family["fuel_targets"].canonical_address,
        "fuel_targets_stock_wrapper":
            _hook_stock_for_adapter(layout, "fuel_targets_adapter"),
        "fuel_targets_pointers": family["fuel_targets"].pointer_table,
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


def _validate_registers_and_control_flow(parsed, helper_entry):
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
            if index + 1 >= len(instructions) or not instructions[
                index + 1
            ].text.lower().startswith("mov.l "):
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: "
                    "BRA delay slot does not load the stock wrapper"
                )
        elif mnemonic == "jmp":
            if text != "jmp @r3":
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: "
                    "tail jump does not use r3"
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


def _validate_limiter_commit(parsed):
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
    if (
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
    config_address = parsed.labels.get("feedback_phase_counts")
    statement = parsed.statement_by_address.get(config_address)
    expected = (
        layout.feedback.default_on_frames << 8
        | layout.feedback.default_off_frames
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


def validate_assembly_sources(layout=None):
    """Cross-check all implemented source slices with the exact layout."""
    layout = layout or load_layout()
    source_dir = DEFAULT_MANIFEST.parent
    expected_literals = _expected_long_literals(layout)
    actual_literals = {}
    parsed_by_unit = {}

    for unit in layout.assembly_units:
        parsed = parse_source(
            source_dir / unit.source, unit.span.start, unit.span.end
        )
        parsed_by_unit[unit.key] = parsed
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
        elif unit.key in {"adapter_select_helper", "lookup_adapters"}:
            _validate_registers_and_control_flow(
                parsed,
                layout.code_region_by_key["adapter_select_helper"].entry,
            )
        elif unit.key == "limiter_commit":
            _validate_limiter_commit(parsed)
        elif unit.key == "startup_wrapper":
            _validate_startup_wrapper(parsed)
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
    for key, path in args.blob:
        if key not in unit_by_key:
            parser.error(f"unknown assembly unit {key!r}")
        if key in seen:
            parser.error(f"duplicate blob for {key!r}")
        validate_assembled_blob(unit_by_key[key], path)
        seen.add(key)
    print(
        "status=PASS"
        f" sources={len(parsed)}"
        f" instructions={sum(unit.instruction_count for unit in layout.assembly_units)}"
        f" data_bytes={sum(unit.data_bytes for unit in layout.assembly_units)}"
        f" blobs={len(seen)}"
    )


if __name__ == "__main__":
    main()
