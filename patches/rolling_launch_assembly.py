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
SOURCE_LABELS = {
    "periodic_wrapper": "rolling_launch_periodic_wrapper",
    "selector_arbiter": "rolling_launch_selector_arbiter",
    "startup_wrapper": "rolling_launch_startup_wrapper",
    "engine": "rolling_launch_engine",
    "ignition_adapter": "rolling_launch_ignition_adapter",
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


def _validate_engine_abi(parsed):
    texts = _texts(parsed)
    if texts[0] != "sts.l pr,@-r15":
        raise ValueError("Rolling Launch engine does not save PR")
    if texts.count("lds.l @r15+,pr") != 2:
        raise ValueError("engine and gate helper must each restore PR")
    if texts.count("jsr @r0") != 2:
        raise ValueError("engine must have two limiter-commit call sites")
    if texts.count("stc sr,r7") != 1 or texts.count("ldc r7,sr") != 1:
        raise ValueError("fuel overlay does not preserve SR exactly once")
    try:
        mask = texts.index("ldc r0,sr")
        restore = texts.index("ldc r7,sr")
    except ValueError as error:
        raise ValueError("fuel overlay lacks SR mask or restore") from error
    word_stores = [
        index
        for index, text in enumerate(texts)
        if text == "mov.w r0,@r4"
    ]
    if len(word_stores) != 4 or not all(
        mask < index < restore for index in word_stores
    ):
        raise ValueError("fuel overlay must contain four protected word stores")
    required = {
        "rl_idle",
        "rl_active",
        "rl_cooldown",
        "rl_corrupt_state",
        "rl_evaluate_gates",
        "rl_validate_config",
        "rl_apply_fuel_overlay",
        "rl_publish_active_flags",
    }
    if not required <= set(parsed.labels):
        raise ValueError("engine state-machine label set is incomplete")


def _validate_ignition_abi(parsed):
    texts = _texts(parsed)
    if any(text.startswith(("jsr ", "bsr ", "rts")) for text in texts):
        raise ValueError("ignition adapter must be one tail-call leaf")
    if texts[-2:] != ["jmp @r0", "nop"]:
        raise ValueError("ignition adapter lacks stock tail jump")
    if texts.count("mov.b r0,@r1") != 2:
        raise ValueError("ignition output/effective store count differs")
    if texts.count("mov.b r0,@r2") != 2:
        raise ValueError("ignition diagnostic store count differs")
    if texts.count("cmp/hs r2,r4") != 1:
        raise ValueError("ignition max(stock,target) comparison differs")
    gate = [
        "mov.l @(rl_ign_apc_mode_address,pc),r3",
        "mov.b @r3,r0",
        "tst 0x40,r0",
        "bf rl_ign_tail",
    ]
    gate_start = next(
        (
            index
            for index in range(len(texts) - len(gate) + 1)
            if texts[index : index + len(gate)] == gate
        ),
        None,
    )
    if gate_start is None:
        raise ValueError("ignition adapter lacks APC fallback-mode gate")
    if gate_start > texts.index("cmp/eq 0x1,r0"):
        raise ValueError("ignition APC fallback gate follows mode validation")
    registers = set()
    for statement in _instructions(parsed):
        registers.update(common.REGISTER_RE.findall(statement.text.lower()))
    if not registers <= {"r0", "r1", "r2", "r3", "r4"}:
        raise ValueError("ignition adapter clobbers an undeclared register")


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
            "rl_config_address": 0x000D3F60,
            "rl_rpm_address": 0xFFFF11BC,
            "rl_limiter_commit": 0x000D3660,
            "rl_button_address": 0xFFFF2A85,
            "rl_gate_state_address": 0xFFFF5D40,
            "rl_gate_selector_address": 0xFFFF5D00,
            "rl_gate_map_enable_masks": 0x000D3D1C,
            "rl_gate_config_address": 0x000D3F60,
            "rl_gate_ascd_address": 0xFFFF41AE,
            "rl_gate_button_address": 0xFFFF2A85,
            "rl_gate_speed_address": 0xFFFF110E,
            "rl_gate_rpm_address": 0xFFFF11BC,
            "rl_gate_pedal_address": 0xFFFF2672,
            "rl_gate_coolant_address": 0xFFFF1077,
            "rl_gate_brake_address": 0xFFFF2451,
            "rl_helper_config_address": 0x000D3F60,
            "rl_helper_state_address": 0xFFFF5D40,
            "rl_helper_fuel_shadow_address": 0xFFFF5D10,
            "rl_helper_fuel_cut_status": 0xFFFF2497,
        },
        "ignition_adapter": {
            "rl_ign_state_address": 0xFFFF5D40,
            "rl_ign_config_address": 0x000D3F60,
            "rl_ign_output_address": 0xFFFF2022,
            "rl_ign_stock_consumer": 0x0002A892,
            "rl_ign_enable_masks": 0x000D3F4C,
            "rl_ign_integrity_markers": 0xADB3A55A,
            "rl_ign_apc_mode_address": 0xFFFF24C9,
        },
    }


def validate_assembly_sources(layout=None):
    """Validate source boundaries, ABI, literals, and SH-2E forms."""
    layout = layout or layout_model.load_layout()
    source_dir = layout_model.DEFAULT_MANIFEST.parent
    parsed_by_unit = {}
    expected_literals = _expected_long_literals()
    for unit in layout.assembly_units:
        parsed = common.parse_source(
            source_dir / unit.source, unit.span.start, unit.span.end
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
