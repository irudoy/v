#!/usr/bin/env python3
"""Static and machine-byte audits for the JK08A CAN telemetry sources."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry_layout as layout_model
from patches import can_telemetry_profile
from patches import map_switching_assembly as common


DEFAULT_PAYLOADS = Path(__file__).with_name("can-telemetry-payloads.toml")
SOURCE_LABELS = {
    "main_wrapper": "telemetry_main_wrapper",
    "knock_wrapper": "telemetry_knock_wrapper",
    "startup_wrapper": "telemetry_startup_wrapper",
    "capture": "telemetry_capture",
    "build_bank": "telemetry_build_bank",
    "request_page": "telemetry_request_page",
    "sle1_isr": "telemetry_sle1_isr",
    "completion": "telemetry_handle_completion",
    "hcan1_init_wrapper": "telemetry_hcan1_init_wrapper",
    "control_poll": "telemetry_control_poll",
}
ALLOWED_MNEMONICS = common.SH7058S_SH2E_MNEMONICS | {"bsr", "not", "rte"}


def render_payloads(layout, blobs):
    expected = set(layout.assembly_unit_by_key)
    if set(blobs) != expected:
        raise ValueError(
            f"payload set differs; missing={sorted(expected - set(blobs))}; "
            f"extra={sorted(set(blobs) - expected)}"
        )
    lines = [
        "# SHA-locked GNU SH-2E payloads for exact JK08A CAN telemetry.",
        f"schema_version = {layout.schema_version}",
        "",
        "[units]",
    ]
    for unit in layout.assembly_units:
        blob = layout_model.validate_assembled_blob(unit, blobs[unit.key])
        encoded = blob.hex()
        lines.extend((f'{unit.key} = """',))
        lines.extend(
            encoded[index : index + 64]
            for index in range(0, len(encoded), 64)
        )
        lines.append('"""')
    return "\n".join(lines) + "\n"


def load_payloads(layout=None, path=DEFAULT_PAYLOADS):
    layout = layout or layout_model.load_layout()
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    if raw.get("schema_version") != 2 or not isinstance(raw.get("units"), dict):
        raise ValueError(f"{path}: unsupported payload table")
    expected = set(layout.assembly_unit_by_key)
    units = raw["units"]
    if set(units) != expected:
        raise ValueError(
            f"{path}: payload set differs; missing={sorted(expected - set(units))}; "
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
            raise ValueError(f"{path}: {unit.key} payload is not hexadecimal") from error
        result[unit.key] = layout_model.validate_assembled_blob(unit, blob)
    return result


def _instructions(parsed):
    return [item for item in parsed.statements if item.kind == "instruction"]


def _texts(parsed):
    return [item.text.lower() for item in _instructions(parsed)]


def _validate_instruction_forms(parsed):
    for statement in _instructions(parsed):
        mnemonic = statement.text.split(None, 1)[0].lower()
        if mnemonic not in ALLOWED_MNEMONICS:
            raise ValueError(
                f"{parsed.path}:{statement.line_number}: {mnemonic} is outside the audited SH7058S SH-2E subset"
            )


def _expected_long_literals():
    return {
        "wrappers": {
            "telemetry_main_stock": 0x00020DFE,
            "telemetry_control_poll_entry": 0x000D4EA0,
            "telemetry_capture_entry": 0x000D4340,
            "telemetry_knock_state": 0xFFFF5E00,
            "telemetry_knock_count": 0xFFFF2142,
            "telemetry_knock_mask": 0xFFFF2150,
            "telemetry_knock_stock": 0x000493E8,
            "telemetry_startup_state": 0xFFFF5E00,
            "telemetry_startup_stock": 0x000D38A0,
        },
        "capture": {
            "telemetry_capture_config": 0x000D4E00,
            "telemetry_capture_state": 0xFFFF5E00,
            "telemetry_capture_bank_a": 0xFFFF5E20,
            "telemetry_capture_bank_b": 0xFFFF5E78,
            "telemetry_config_integrity": 0x54454C32,
            "telemetry_build_state": 0xFFFF5E00,
            "telemetry_page_table": 0x000D4C00,
            "telemetry_context_page_9_table": 0x000D4CFC,
            "telemetry_context_page_10_table": 0x000D4D5C,
            "telemetry_request_state": 0xFFFF5E00,
            "telemetry_request_bank_a_literal": 0xFFFF5E20,
            "telemetry_request_bank_b": 0xFFFF5E78,
            "telemetry_mailbox_data": 0xFFFFDC48,
            "telemetry_txpr1": 0xFFFFD820,
        },
        "completion": {
            "telemetry_isr_txack1": 0xFFFFD830,
            "telemetry_isr_aback1": 0xFFFFD838,
            "telemetry_isr_irr1": 0xFFFFD808,
            "telemetry_stock_activity_state": 0xFFFFA56F,
            "telemetry_stock_mailbox28_complete": 0x000C6B68,
            "telemetry_completion_state": 0xFFFF5E00,
            "telemetry_completion_txack1": 0xFFFFD830,
            "telemetry_completion_aback1": 0xFFFFD838,
            "telemetry_completion_irr1": 0xFFFFD808,
            "telemetry_completion_request_page": 0x000D4700,
            "telemetry_completion_bank_a": 0xFFFF5E20,
            "telemetry_completion_bank_b": 0xFFFF5E78,
        },
        "control": {
            "telemetry_control_stock_hcan1_init": 0x000C338A,
            "telemetry_control_config": 0x000D4E00,
            "telemetry_control_mailbox31": 0xFFFFDCE0,
            "telemetry_control_rxpr1": 0xFFFFD840,
            "telemetry_control_rfpr1": 0xFFFFD848,
            "telemetry_control_mbimr1": 0xFFFFD850,
            "telemetry_control_umsr1": 0xFFFFD858,
            "telemetry_control_rxpr1_poll": 0xFFFFD840,
            "telemetry_control_rfpr1_poll": 0xFFFFD848,
            "telemetry_control_umsr1_poll": 0xFFFFD858,
            "telemetry_control_mailbox31_poll": 0xFFFFDCE0,
            "telemetry_control_state": 0xFFFF5E00,
            "telemetry_control_config_poll": 0x000D4E00,
            "telemetry_control_command_magic": 0x54454C32,
            "telemetry_control_start_tail": 0x0201B632,
            "telemetry_control_stop_tail": 0x0200A613,
            "telemetry_control_config_integrity": 0x54454C32,
        },
    }


def _validate_wrappers(parsed):
    texts = _texts(parsed)
    if texts[:13] != [
        "sts.l pr,@-r15", "mov.l @(telemetry_main_stock,pc),r0",
        "jsr @r0", "nop",
        "mov.l @(telemetry_control_poll_entry,pc),r0", "jsr @r0", "nop",
        "mov.l @(telemetry_capture_entry,pc),r0",
        "jsr @r0", "nop", "lds.l @r15+,pr", "rts", "nop",
    ]:
        raise ValueError("main telemetry wrapper ABI differs")
    if texts.count("jsr @r0") != 5 or texts.count("lds.l @r15+,pr") != 3:
        raise ValueError("wrapper call or PR preservation count differs")
    if texts.count("mov.l r0,@r1") != 1 or texts.count("dt r2") != 1:
        raise ValueError("startup clear loop differs")
    if "mov #0x40,r2" not in texts:
        raise ValueError("startup does not clear exactly 256 active RAM bytes")


def _validate_capture(parsed):
    texts = _texts(parsed)
    if texts[0] != "sts.l pr,@-r15" or texts.count("lds.l @r15+,pr") != 1:
        raise ValueError("capture does not preserve PR")
    if texts.count("bsr telemetry_build_bank") != 2:
        raise ValueError("capture bank-build publication paths differ")
    if texts.count("bsr telemetry_request_page") != 1:
        raise ValueError("capture idle-start path differs")
    if texts.count("mov.w r0,@r1") != 1:
        raise ValueError("request path must write TXPR exactly once")
    for required in (
        "mov.w @(0x8,r4),r0",
        "mov.w @(0xa,r4),r0",
        "cmp/hi r1,r0",
        "mov.w @(telemetry_config_crc,pc),r1",
    ):
        if required not in texts:
            raise ValueError(
                f"capture configuration guard lacks {required}"
            )
    if texts.count("mov.b @r4+,r0") != 1 or texts.count("dt r2") != 4:
        raise ValueError("bounded snapshot or mailbox copy loops differ")
    for required in (
        "telemetry_capture_due", "telemetry_capture_busy_bank",
        "telemetry_capture_idle", "telemetry_build_page_loop",
        "telemetry_build_context_page_9_byte_loop",
        "telemetry_build_context_page_10_byte_loop",
        "telemetry_request_copy_loop",
    ):
        if required not in parsed.labels:
            raise ValueError(f"capture lacks {required}")


def _validate_completion(parsed):
    texts = _texts(parsed)
    prologue = [f"mov.l r{index},@-r15" for index in range(8)] + ["sts.l pr,@-r15"]
    epilogue = ["lds.l @r15+,pr"] + [f"mov.l @r15+,r{index}" for index in range(7, -1, -1)] + ["rte", "nop"]
    if texts[:9] != prologue:
        raise ValueError("SLE1 handler register prologue differs")
    restore = texts.index("lds.l @r15+,pr")
    if texts[restore : restore + len(epilogue)] != epilogue:
        raise ValueError("SLE1 handler exception epilogue differs")
    if texts.count("rte") != 1 or texts.count("jsr @r0") != 4:
        raise ValueError("SLE1 return or call graph differs")
    if texts.count("mov.b r0,@r4") != 2:
        raise ValueError("stock mailbox-28 activity-state behavior differs")
    if texts.count("mov.w r5,@r6") != 2:
        raise ValueError("stock mailbox-28 acknowledgment behavior differs")
    if texts.count("mov.w r5,@r4") != 2:
        raise ValueError("mailbox-26 acknowledgment behavior differs")
    if "telemetry_queue_corrupt" not in parsed.labels:
        raise ValueError("completion lacks fail-closed corrupt-state path")


def _validate_control(parsed):
    texts = _texts(parsed)
    if texts[:5] != [
        "sts.l pr,@-r15",
        "mov.l @(telemetry_control_stock_hcan1_init,pc),r0",
        "jsr @r0",
        "nop",
        "mov.l r0,@-r15",
    ]:
        raise ValueError("HCAN1 initialization wrapper ABI differs")
    if texts.count("mov.l @r15+,r0") != 1:
        raise ValueError("HCAN1 initialization wrapper loses the stock result")
    if texts.count("bsr telemetry_control_config_valid") != 2:
        raise ValueError("control entries do not share the configuration gate")
    if texts.count("mov.w r0,@(0x4,r1)") != 1:
        raise ValueError("mailbox 31 receive mode must be committed exactly once")
    if texts.count("mov.b r0,@(0xb,r3)") != 2:
        raise ValueError("START and STOP do not publish both runtime overrides")
    if texts.count("mov.b r0,@(0x1,r3)") != 1:
        raise ValueError("STOP does not discard the replaceable pending group")
    if texts.count("mov.w r2,@r3") != 6:
        raise ValueError("control poll does not clear every pending mailbox flag")
    if texts.count("tst 0x8,r0") != 1:
        raise ValueError("control poll does not reject a retained remote frame")
    for required in (
        "telemetry_control_init_return",
        "telemetry_control_poll_data",
        "telemetry_control_poll_clear",
        "telemetry_control_start",
        "telemetry_control_stop",
        "telemetry_control_config_valid",
        "telemetry_control_config_invalid",
    ):
        if required not in parsed.labels:
            raise ValueError(f"control unit lacks {required}")


def validate_assembly_sources(layout=None):
    layout = layout or layout_model.load_layout()
    can_telemetry_profile.generate(check=True)
    source_dir = layout_model.DEFAULT_MANIFEST.parent
    parsed_by_unit = {}
    expected_literals = _expected_long_literals()
    for unit in layout.assembly_units:
        parsed = common.parse_source(source_dir / unit.source, unit.span.start, unit.span.end)
        parsed_by_unit[unit.key] = parsed
        _validate_instruction_forms(parsed)
        common._validate_delay_slots(parsed)
        if parsed.instruction_count != unit.instruction_count:
            raise ValueError(
                f"{unit.key}: source has {parsed.instruction_count} instructions, expected {unit.instruction_count}"
            )
        if parsed.data_bytes != unit.data_bytes:
            raise ValueError(
                f"{unit.key}: source has {parsed.data_bytes} data bytes, expected {unit.data_bytes}"
            )
        for key in unit.code_regions:
            label = SOURCE_LABELS[key]
            if parsed.labels.get(label) != layout.code_region_by_key[key].entry:
                raise ValueError(f"{unit.key}: {label} entry differs")
        if unit.key != "tables" and common._long_literals(parsed) != expected_literals[unit.key]:
            raise ValueError(f"{unit.key}: long literal contract differs")
        if unit.key == "wrappers":
            _validate_wrappers(parsed)
        elif unit.key == "capture":
            _validate_capture(parsed)
        elif unit.key == "completion":
            _validate_completion(parsed)
        elif unit.key == "control":
            _validate_control(parsed)
        elif unit.key == "tables":
            expected = can_telemetry_profile.render_tables(
                can_telemetry_profile.load_manifest()
            )
            if (source_dir / unit.source).read_text(encoding="utf-8") != expected:
                raise ValueError("generated table source differs")
        else:
            raise ValueError(f"{unit.key}: no source validator is registered")
    return parsed_by_unit


def validate_instruction_semantics(layout, parsed_by_unit, blobs):
    expected = set(layout.assembly_unit_by_key)
    if set(blobs) != expected:
        raise ValueError("assembly blob set differs from the layout")
    addresses = {
        statement.address
        for parsed in parsed_by_unit.values()
        for statement in parsed.statements
        if statement.kind == "instruction"
    }
    audits = []
    for unit in layout.assembly_units:
        blob = layout_model.validate_assembled_blob(unit, blobs[unit.key])
        audits.append(common.validate_source_blob(parsed_by_unit[unit.key], blob, unit.span.start, addresses))
    return common.InstructionAudit(
        instructions=sum(item.instructions for item in audits),
        delayed_transfers=sum(item.delayed_transfers for item in audits),
        pc_relative_references=sum(item.pc_relative_references for item in audits),
        direct_branches=sum(item.direct_branches for item in audits),
        indirect_transfers=sum(item.indirect_transfers for item in audits),
    )


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payloads", type=Path, default=DEFAULT_PAYLOADS)
    parser.add_argument(
        "--update-from",
        type=Path,
        help="replace the payload manifest from <unit>.bin GNU outputs",
    )
    args = parser.parse_args(argv)
    layout = layout_model.load_layout()
    parsed = validate_assembly_sources(layout)
    if args.update_from is not None:
        blobs = {
            unit.key: (args.update_from / f"{unit.key}.bin").read_bytes()
            for unit in layout.assembly_units
        }
        args.payloads.write_text(
            render_payloads(layout, blobs), encoding="utf-8"
        )
    blobs = load_payloads(layout, args.payloads)
    audit = validate_instruction_semantics(layout, parsed, blobs)
    print(
        "status=PASS"
        f" units={len(parsed)}"
        f" instructions={audit.instructions}"
        f" data_bytes={layout.assembled_data_bytes}"
        f" delayed_transfers={audit.delayed_transfers}"
    )


if __name__ == "__main__":
    main()
