#!/usr/bin/env python3
"""Static and machine-byte audits for JK08A Rolling Launch SH sources."""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_assembly as common
from patches import rolling_launch_layout as layout_model


DEFAULT_PAYLOADS = Path(__file__).with_name("rolling-launch-payloads.toml")


def render_payloads(layout, blobs):
    """Render the canonical payload manifest from assembled unit bytes."""
    expected = set(layout.assembly_unit_by_key)
    if set(blobs) != expected:
        raise ValueError(
            f"payload set differs; missing={sorted(expected - set(blobs))}; "
            f"extra={sorted(set(blobs) - expected)}"
        )
    lines = [
        "# SHA-locked GNU SH-2E payloads for exact JK08A Rolling Launch.",
        "# Each value covers the complete assembly-unit span, including 0xFF fill.",
        "",
        "schema_version = 1",
        "",
        "[units]",
    ]
    for unit in layout.assembly_units:
        blob = layout_model.validate_assembled_blob(unit, blobs[unit.key])
        encoded = blob.hex()
        lines.append(f'{unit.key} = """')
        lines.extend(
            encoded[index : index + 64]
            for index in range(0, len(encoded), 64)
        )
        lines.append('"""')
    return "\n".join(lines) + "\n"


SOURCE_LABELS = {
    "periodic_wrapper": "rolling_launch_periodic_wrapper",
    "selector_arbiter": "rolling_launch_selector_arbiter",
    "startup_wrapper": "rolling_launch_startup_wrapper",
    "engine": "rolling_launch_engine",
    "ignition_adapter": "rolling_launch_ignition_adapter",
    "speed_controller": "rolling_launch_speed_controller",
    "feedback_arbiter": "rolling_launch_feedback_arbiter",
    "fuel_cut_wrapper": "rolling_launch_fuel_cut_wrapper",
    "rpm_ceiling": "rolling_launch_rpm_ceiling",
}
ALLOWED_MNEMONICS = common.SH7058S_SH2E_MNEMONICS | {"bsr"}
DISPLACEMENT_LOAD = re.compile(
    r"^mov\.(?P<width>[bw])\s+@\((?P<disp>[^,]+),r\d+\),"
    r"(?P<dest>r(?:1[0-5]|[0-9]))$",
    re.IGNORECASE,
)
DISPLACEMENT_STORE = re.compile(
    r"^mov\.(?P<width>[bw])\s+(?P<src>r(?:1[0-5]|[0-9])),"
    r"@\((?P<disp>[^,]+),r\d+\)$",
    re.IGNORECASE,
)
IMMEDIATE_R0_ONLY = re.compile(
    r"^(?:cmp/eq|and|or|tst)\s+[-]?(?:0x[0-9a-f]+|\d+),"
    r"(?P<dest>r(?:1[0-5]|[0-9]))$",
    re.IGNORECASE,
)


def load_payloads(layout=None, path=DEFAULT_PAYLOADS):
    """Load and SHA-validate every tracked Ghidra assembly span."""
    layout = layout or layout_model.load_layout()
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    if raw.get("schema_version") != 1 or not isinstance(raw.get("units"), dict):
        raise ValueError(f"{path}: unsupported or missing payload table")
    units = raw["units"]
    expected = set(layout.assembly_unit_by_key)
    if set(units) != expected:
        raise ValueError(
            f"{path}: payload set differs; "
            f"missing={sorted(expected - set(units))}; "
            f"extra={sorted(set(units) - expected)}"
        )
    result = {}
    for unit in layout.assembly_units:
        value = units[unit.key]
        if not isinstance(value, str):
            raise ValueError(f"{path}: {unit.key} payload is not text")
        try:
            blob = bytes.fromhex("".join(value.split()))
        except ValueError as error:
            raise ValueError(f"{path}: {unit.key} is not hexadecimal") from error
        result[unit.key] = layout_model.validate_assembled_blob(unit, blob)
    return result


def _instructions(parsed):
    return [item for item in parsed.statements if item.kind == "instruction"]


def _texts(parsed):
    return [item.text.lower() for item in _instructions(parsed)]


def _validate_16_bit_source_forms(parsed):
    for statement in _instructions(parsed):
        text = statement.text.lower()
        mnemonic = text.split(None, 1)[0]
        if mnemonic not in ALLOWED_MNEMONICS:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: {mnemonic} is "
                "outside the audited SH7058S SH-2E subset"
            )
        match = DISPLACEMENT_LOAD.fullmatch(text)
        if (
            match
            and match.group("disp").lower() != "r0"
            and match.group("dest") != "r0"
        ):
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: byte/word "
                "displacement load requires r0 on SH-2E"
            )
        match = DISPLACEMENT_STORE.fullmatch(text)
        if (
            match
            and match.group("disp").lower() != "r0"
            and match.group("src") != "r0"
        ):
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: byte/word "
                "displacement store requires r0 on SH-2E"
            )
        match = IMMEDIATE_R0_ONLY.fullmatch(text)
        if match and match.group("dest") != "r0":
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: immediate form "
                "requires r0 on SH-2E"
            )


def _validate_wrapper_abi(parsed):
    texts = _texts(parsed)
    if texts[:1] != ["sts.l pr,@-r15"]:
        raise ValueError("periodic wrapper does not save PR")
    if texts[7:10] != ["lds.l @r15+,pr", "rts", "nop"]:
        raise ValueError("periodic wrapper does not restore PR")
    jsr = [index for index, text in enumerate(texts) if text == "jsr @r0"]
    if jsr != [2, 5, 29] or any(texts[index + 1] != "nop" for index in jsr):
        raise ValueError("wrapper JSR/NOP call order differs")
    if texts.count("jmp @r0") != 2:
        raise ValueError("selector arbiter needs two tail jumps")
    if texts.count("mov.l r0,@r1") != 1 or texts.count("dt r2") != 1:
        raise ValueError("startup state clear loop differs")
    if texts.count("mov #0x7,r2") != 1:
        raise ValueError("startup state clear size differs")


def _validate_engine_abi(parsed):
    texts = _texts(parsed)
    if texts[:4] != [
        "sts.l pr,@-r15",
        "mov.l @(rl_state_address,pc),r5",
        "mov #0x0,r0",
        "mov.w r0,@(0x14,r5)",
    ]:
        raise ValueError("engine does not clear the fuel-cut request on entry")
    if texts.count("lds.l @r15+,pr") != 2:
        raise ValueError("engine and gate helper must each restore PR")
    if texts.count("jsr @r0") != 2:
        raise ValueError(
            "engine must have one corrupt-state limiter commit and one "
            "controller call"
        )
    if texts.count("stc sr,r7") or texts.count("ldc r7,sr"):
        raise ValueError("engine writes the fuel-cut shadow")
    if texts.count("mov #0x7,r2") != 1:
        raise ValueError("corrupt-state clear size differs")
    if texts.count("mov.w r0,@(0x18,r5)") != 2:
        raise ValueError(
            "engine must release the ceiling latch on activation and abort"
        )
    if texts.count("mov.w r0,@(0x14,r5)") != 1 or "mov #0x3f,r0" in texts:
        raise ValueError("engine publishes the fuel-cut request outside the controller")
    if texts.count("mov.w r0,@(0x16,r5)") or texts.count("mov.w r0,@(0x10,r5)"):
        raise ValueError("engine writes a controller output field")
    validator = [
        item.text.lower()
        for item in _instructions(parsed)
        if parsed.labels["rl_validate_config"]
        <= item.address
        < parsed.labels["rl_helper_config_address"]
    ]
    speed_bound = [
        "mov.w @(0x8,r3),r0",
        "extu.w r0,r2",
        "tst r2,r2",
        "bt rl_config_speed_ordered",
    ]
    if not _contains(validator, speed_bound):
        raise ValueError("configuration validation rejects a disabled minimum speed")
    controller_call = [
        "mov.l @(rl_controller_entry,pc),r0",
        "jsr @r0",
        "nop",
    ]
    if not _contains(texts, controller_call):
        raise ValueError("engine controller call differs")
    age_gate = [
        "mov.l @(rl_gate_speed_age_address,pc),r4",
        "mov.b @r4,r2",
        "extu.b r2,r2",
    ]
    if not _contains(texts, age_gate) or texts.count("mov #0xd,r0") != 1:
        raise ValueError("engine speed-frame age gate differs")
    required = {
        "rl_idle",
        "rl_active",
        "rl_cooldown",
        "rl_corrupt_state",
        "rl_evaluate_gates",
        "rl_validate_config",
        "rl_run_controller",
        "rl_gate_speed_frame",
        "rl_gate_speed_window",
    }
    if not required <= set(parsed.labels):
        raise ValueError("engine state-machine label set is incomplete")
    mask_pointer = common._long_literals(parsed).get(
        "rl_gate_map_enable_masks"
    )
    if mask_pointer != parsed.labels.get("rl_gate_map_enable_mask_bytes"):
        raise ValueError("map-enable mask literal does not point to its table")


def _contains(texts, sequence):
    return any(
        texts[index : index + len(sequence)] == sequence
        for index in range(len(texts) - len(sequence) + 1)
    )


def _validate_ignition_abi(parsed):
    texts = _texts(parsed)
    if texts != ["mov.l @(rl_ign_stock_consumer,pc),r0", "jmp @r0", "nop"]:
        raise ValueError("ignition adapter must be one stock tail jump")


def _validate_speed_controller_abi(parsed):
    texts = _texts(parsed)
    if texts[:1] != ["sts.l pr,@-r15"]:
        raise ValueError("speed controller does not save PR")
    if texts[-3:] != ["lds.l @r15+,pr", "rts", "nop"]:
        raise ValueError("speed controller does not restore PR")
    divider_call = [
        "mov.l @(rl_spd_unsigned_divide,pc),r3",
        "jsr @r3",
        "nop",
    ]
    if texts.count("jsr @r3") != 1 or not _contains(texts, divider_call):
        raise ValueError("speed controller divider call differs")
    ceiling_call = [
        "mov.l @(rl_spd_ceiling_entry,pc),r0",
        "jsr @r0",
        "nop",
    ]
    if texts.count("jsr @r0") != 1 or not _contains(texts, ceiling_call):
        raise ValueError("speed controller RPM ceiling call differs")
    if texts.count("mulu.w r0,r1") != 1 or texts.count("muls.w r0,r2") != 1:
        raise ValueError("speed controller arithmetic differs")
    stores = sorted(
        text for text in texts
        if text.startswith(("mov.b r", "mov.w r", "mov.l r"))
    )
    expected = sorted([
        "mov.w r0,@(0x10,r5)",
        "mov.w r0,@(0x12,r5)",
        "mov.w r0,@(0x16,r5)",
        "mov.w r0,@(0xe,r5)",
        "mov.b r0,@(0x2,r5)",
    ])
    if stores != expected or texts.count("mov #0x3f,r0"):
        raise ValueError("speed controller store contract differs")
    registers = set()
    for statement in _instructions(parsed):
        registers.update(common.REGISTER_RE.findall(statement.text.lower()))
    allowed = {f"r{number}" for number in range(8)} | {"r15", "pr", "macl"}
    if not registers <= allowed:
        raise ValueError("speed controller clobbers an undeclared register")


def _validate_rpm_ceiling_abi(parsed):
    texts = _texts(parsed)
    if texts[:3] != ["mov.b @(0x5,r5),r0", "cmp/eq 0x1,r0", "bf rl_ceil_release"]:
        raise ValueError("RPM ceiling does not release the latch outside hold")
    if texts.count("rts") != 2 or any(
        text.startswith(("jsr", "bsr", "jmp", "sts.l pr", "lds.l"))
        for text in texts
    ):
        raise ValueError("RPM ceiling must be a leaf with two returns")
    stores = sorted(
        text for text in texts
        if text.startswith(("mov.b r", "mov.w r", "mov.l r"))
    )
    expected = sorted([
        "mov.w r0,@(0x14,r5)",
        "mov.w r0,@(0x18,r5)",
        "mov.w r0,@(0x18,r5)",
    ])
    if stores != expected or texts.count("mov #0x3f,r0") != 1:
        raise ValueError("RPM ceiling store contract differs")
    if {"rl_ceil_latch", "rl_ceil_release"} - set(parsed.labels):
        raise ValueError("RPM ceiling label set is incomplete")
    registers = set()
    for statement in _instructions(parsed):
        registers.update(common.REGISTER_RE.findall(statement.text.lower()))
    allowed = {"r0", "r1", "r2", "r3", "r4", "r5", "r7"}
    if not registers <= allowed:
        raise ValueError("RPM ceiling clobbers an undeclared register")


def _validate_feedback_arbiter_abi(parsed):
    texts = _texts(parsed)
    prefix = [
        "sts.l pr,@-r15",
        "mov.l @(rl_feedback_selector_state,pc),r1",
        "add 0x4,r1",
        "mov.l @r1,r0",
        "mov.l r0,@-r15",
        "mov.l @(rl_feedback_base_wrapper,pc),r0",
        "jsr @r0",
        "nop",
        "mov.l @r15+,r0",
        "tst r0,r0",
        "bf rl_feedback_return",
    ]
    if texts[:len(prefix)] != prefix:
        raise ValueError("feedback arbiter map-priority prefix differs")
    if texts[-3:] != ["lds.l @r15+,pr", "rts", "nop"]:
        raise ValueError("feedback arbiter does not restore PR")
    if texts.count("jsr @r0") != 1:
        raise ValueError("feedback arbiter base-wrapper call count differs")
    required = {
        "mov #0x0,r2",
        "mov #0x40,r2",
        "mov #0x50,r2",
        "tst 0x20,r0",
        "and 0x8f,r0",
        "or r2,r0",
        "mov.b r0,@r1",
    }
    if not required <= set(texts):
        raise ValueError("feedback arbiter ASCD state contract differs")
    if texts.count("mov.b r0,@r1") != 1:
        raise ValueError("feedback arbiter status store count differs")
    labels = {
        "rl_feedback_active",
        "rl_feedback_idle",
        "rl_feedback_apply",
        "rl_feedback_return",
    }
    if not labels <= set(parsed.labels):
        raise ValueError("feedback arbiter label set is incomplete")
    registers = set()
    for statement in _instructions(parsed):
        registers.update(common.REGISTER_RE.findall(statement.text.lower()))
    allowed = {"r0", "r1", "r2", "r15", "pr"}
    if not registers <= allowed:
        raise ValueError("feedback arbiter clobbers an undeclared register")


def _validate_fuel_cut_wrapper_abi(parsed):
    texts = _texts(parsed)
    expected = [
        "sts.l pr,@-r15",
        "mov.l @(rl_fuel_stock_coordinator,pc),r0",
        "jsr @r0",
        "nop",
        "mov.l r0,@-r15",
        "mov.l @(rl_fuel_state_address,pc),r1",
        "mov.w @(0x14,r1),r0",
        "extu.w r0,r0",
        "tst r0,r0",
        "bt rl_fuel_return",
        "mov #-0x40,r1",
        "tst r1,r0",
        "bf rl_fuel_return",
        "mov.l @(rl_fuel_final_mask_address,pc),r1",
        "mov.b @r1,r2",
        "or r2,r0",
        "mov.b r0,@r1",
        "mov.l @r15+,r0",
        "lds.l @r15+,pr",
        "rts",
        "nop",
    ]
    if texts != expected:
        raise ValueError("fuel-cut wrapper instruction contract differs")
    if parsed.labels.get("rl_fuel_return") != _instructions(parsed)[17].address:
        raise ValueError("fuel-cut wrapper return label differs")


def _expected_long_literals():
    return {
        "wrappers": {
            "rolling_launch_periodic_stock": 0x000A9554,
            "rolling_launch_engine_entry": 0x000D38E4,
            "rolling_launch_state_address": 0xFFFF5D40,
            "rolling_launch_stock_ascd_host": 0x000D09D8,
            "rolling_launch_map_selector_host": 0x000D2108,
            "rolling_launch_state_address_startup": 0xFFFF5D40,
            "rolling_launch_base_startup": 0x000D22A0,
        },
        "engine": {
            "rl_state_address": 0xFFFF5D40,
            "rl_selector_address": 0xFFFF5D00,
            "rl_config_address": 0x000D6040,
            "rl_rpm_address": 0xFFFF11BC,
            "rl_speed_address": 0xFFFF113C,
            "rl_limiter_commit": 0x000D3660,
            "rl_button_address": 0xFFFF2A85,
            "rl_controller_entry": 0x000D40C0,
            "rl_gate_state_address": 0xFFFF5D40,
            "rl_gate_selector_address": 0xFFFF5D00,
            "rl_gate_map_enable_masks": 0x000D3D48,
            "rl_gate_config_address": 0x000D6040,
            "rl_gate_ascd_address": 0xFFFF41AE,
            "rl_gate_button_address": 0xFFFF2A85,
            "rl_gate_speed_address": 0xFFFF113C,
            "rl_gate_speed_age_address": 0xFFFF3B38,
            "rl_gate_rpm_address": 0xFFFF11BC,
            "rl_gate_pedal_address": 0xFFFF2672,
            "rl_gate_coolant_address": 0xFFFF1077,
            "rl_helper_config_address": 0x000D6040,
        },
        "ignition_adapter": {
            "rl_ign_stock_consumer": 0x0002A892,
        },
        "speed_controller": {
            "rl_spd_state_address": 0xFFFF5D40,
            "rl_spd_config_address": 0x000D6040,
            "rl_spd_speed_address": 0xFFFF113C,
            "rl_spd_unsigned_divide": 0x00021CE0,
            "rl_spd_ceiling_entry": 0x000D6068,
            "rl_spd_fuel_cut_status": 0xFFFF2497,
        },
        "feedback_arbiter": {
            "rl_feedback_base_wrapper": 0x000D35E0,
            "rl_feedback_selector_state": 0xFFFF5D00,
            "rl_feedback_state": 0xFFFF5D40,
            "rl_feedback_status_byte": 0xFFFF3ADA,
        },
        "fuel_cut_wrapper": {
            "rl_fuel_stock_coordinator": 0x0004ED88,
            "rl_fuel_state_address": 0xFFFF5D40,
            "rl_fuel_final_mask_address": 0xFFFF22E0,
        },
        "rpm_ceiling": {
            "rl_ceil_rpm_address": 0xFFFF11BC,
        },
    }


def validate_assembly_sources(layout=None):
    """Validate source boundaries, ABI, literals, and SH-2E forms."""
    layout = layout or layout_model.load_layout()
    source_dir = layout_model.DEFAULT_MANIFEST.parent
    parsed_by_unit = {}
    expected_literals = (
        layout.source_literal_by_unit or _expected_long_literals()
    )
    source_texts = layout.source_text_by_unit
    for unit in layout.assembly_units:
        source_path = source_dir / unit.source
        if unit.key in source_texts:
            parsed = common.parse_source_text(
                source_texts[unit.key], source_path,
                unit.span.start, unit.span.end,
            )
        else:
            parsed = common.parse_source(
                source_path, unit.span.start, unit.span.end
            )
        parsed_by_unit[unit.key] = parsed
        _validate_16_bit_source_forms(parsed)
        common._validate_delay_slots(parsed)
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
        for region_key in unit.code_regions:
            label = SOURCE_LABELS[region_key]
            entry = layout.code_region_by_key[region_key].entry
            if parsed.labels.get(label) != entry:
                raise ValueError(f"{unit.key}: {label} entry differs")
        actual_literals = common._long_literals(parsed)
        if actual_literals != expected_literals[unit.key]:
            raise ValueError(f"{unit.key}: long literal contract differs")
        if unit.key == "wrappers":
            _validate_wrapper_abi(parsed)
        elif unit.key == "engine":
            _validate_engine_abi(parsed)
        elif unit.key == "ignition_adapter":
            _validate_ignition_abi(parsed)
        elif unit.key == "speed_controller":
            _validate_speed_controller_abi(parsed)
        elif unit.key == "feedback_arbiter":
            _validate_feedback_arbiter_abi(parsed)
        elif unit.key == "fuel_cut_wrapper":
            _validate_fuel_cut_wrapper_abi(parsed)
        elif unit.key == "rpm_ceiling":
            _validate_rpm_ceiling_abi(parsed)
        else:
            raise ValueError(f"{unit.key}: no ABI validator is registered")
    return parsed_by_unit


def validate_instruction_semantics(layout, parsed_by_unit, blobs):
    """Decode every control transfer and PC-relative load from locked bytes."""
    expected = set(layout.assembly_unit_by_key)
    if set(blobs) != expected:
        raise ValueError("assembly blob set differs from the manifest")
    instruction_addresses = {
        item.address
        for parsed in parsed_by_unit.values()
        for item in parsed.statements
        if item.kind == "instruction"
    }
    audits = []
    for unit in layout.assembly_units:
        blob = layout_model.validate_assembled_blob(unit, blobs[unit.key])
        audits.append(common.validate_source_blob(
            parsed_by_unit[unit.key],
            blob,
            unit.span.start,
            instruction_addresses,
        ))
    return common.InstructionAudit(
        instructions=sum(item.instructions for item in audits),
        delayed_transfers=sum(item.delayed_transfers for item in audits),
        pc_relative_references=sum(item.pc_relative_references for item in audits),
        direct_branches=sum(item.direct_branches for item in audits),
        indirect_transfers=sum(item.indirect_transfers for item in audits),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--payloads", type=Path, default=DEFAULT_PAYLOADS,
        help="tracked Ghidra payload bundle",
    )
    args = parser.parse_args(argv)
    layout = layout_model.load_layout()
    parsed = validate_assembly_sources(layout)
    blobs = load_payloads(layout, args.payloads)
    audit = validate_instruction_semantics(layout, parsed, blobs)
    print(
        "status=PASS"
        f" sources={len(parsed)}"
        f" instructions={audit.instructions}"
        f" data_bytes={layout.assembled_data_bytes}"
        f" delayed_transfers={audit.delayed_transfers}"
        f" pc_relative_references={audit.pc_relative_references}"
        f" direct_branches={audit.direct_branches}"
        f" indirect_transfers={audit.indirect_transfers}"
    )


if __name__ == "__main__":
    main()
