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

from patches import can_telemetry
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
    "knock_margin_wrapper": "telemetry_knock_margin_wrapper",
    "request_page": "telemetry_request_page",
    "sle1_isr": "telemetry_sle1_isr",
    "completion": "telemetry_handle_completion",
    "hcan1_init_wrapper": "telemetry_hcan1_init_wrapper",
    "control_poll": "telemetry_control_poll",
}
ALLOWED_MNEMONICS = common.SH7058S_SH2E_MNEMONICS | {"bsr", "not", "rte"}
IDENTITY_HEADER = can_telemetry_profile.DEFAULT_IDENTITY.name
# The configuration guards compare the configuration record with the symbols
# of the generated identity header, not with numbers of their own.
IDENTITY_STATEMENTS = {
    "capture": (
        "cmp/eq TELEMETRY_PROFILE_ID,r0",
        "mov #TELEMETRY_PAGE_COUNT,r6",
        ".word TELEMETRY_PROFILE_CRC",
    ),
    "control": (
        "cmp/eq TELEMETRY_PROFILE_ID,r0",
        "cmp/eq TELEMETRY_PAGE_COUNT,r0",
        ".word TELEMETRY_PROFILE_CRC",
    ),
}


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
            "telemetry_startup_margin_latch": 0xFFFF5E10,
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
            "telemetry_context_page_10_table": 0x000D4D74,
            "telemetry_margin_stock": 0x0004A238,
            "telemetry_margin_selector": 0x00008B3D,
            "telemetry_margin_channel_alternate": 0xFFFF2143,
            "telemetry_margin_channel_primary": 0xFFFF11DE,
            "telemetry_margin_metric": 0xFFFF21D8,
            "telemetry_margin_threshold": 0xFFFF2144,
            "telemetry_margin_bias": 0x80000000,
            "telemetry_margin_latch": 0xFFFF5E10,
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


def _manifest_identity(manifest):
    """Wire identity the ROM configuration guard accepts.

    The guard admits exactly one profile, so every value it compares against
    is a projection of the manifest and of the configuration record model.
    """
    if len(manifest.profiles) != 1:
        raise ValueError(
            "the configuration guard admits exactly one profile"
        )
    profile = manifest.profiles[0]
    return {
        "magic": can_telemetry.CONFIG_MAGIC,
        "version": can_telemetry.CONFIG_VERSION,
        "can_id_max": can_telemetry.MAX_DATA_CAN_ID,
        "profile_id": profile.profile_id,
        "page_count": profile.page_count,
        "crc16": profile.crc16,
    }


def _expected_word_literals(identity):
    return {
        "capture": {
            "telemetry_config_magic": identity["magic"],
            "telemetry_config_can_id_max": identity["can_id_max"],
            "telemetry_config_crc": identity["crc16"],
        },
        "control": {
            "telemetry_control_config_magic": identity["magic"],
            "telemetry_control_data_can_id_max": identity["can_id_max"],
            "telemetry_control_profile_crc": identity["crc16"],
        },
    }


def _validate_identity_immediates(parsed, unit_key, identity, page_form):
    """Require the guard to compare against the manifest identity itself."""
    texts = _texts(parsed)
    required = (
        f"cmp/eq {identity['version']:#x},r0",
        f"cmp/eq {identity['profile_id']:#x},r0",
        page_form.format(pages=f"{identity['page_count']:#x}"),
    )
    for instruction in required:
        if instruction not in texts:
            raise ValueError(
                f"{unit_key}: configuration guard lacks {instruction}, "
                "which the manifest requires"
            )


def _validate_identity_symbols(source, unit_key):
    """Require the guard to take the identity from the generated header."""
    lines = {
        common._strip_comment(line).strip() for line in source.splitlines()
    }
    for statement in (
        f'.include "{IDENTITY_HEADER}"', *IDENTITY_STATEMENTS[unit_key]
    ):
        if statement not in lines:
            raise ValueError(
                f"{unit_key}: configuration guard lacks {statement}, the "
                f"identity of the generated {IDENTITY_HEADER}"
            )


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
    if texts.count("mov.l r0,@r1") != 1 or texts.count("dt r2") != 2:
        raise ValueError("startup clear or knock margin arm loop differs")
    if "mov #0x40,r2" not in texts:
        raise ValueError("startup does not clear exactly 256 active RAM bytes")
    clear = texts.index("mov.l r0,@r1")
    arm = [
        "mov.l @(telemetry_startup_margin_latch,pc),r1",
        "mov.w @(telemetry_startup_margin_idle,pc),r0",
        "mov #0x6,r2", "mov.w r0,@r1", "add 0x2,r1", "dt r2",
        "bf telemetry_startup_margin_loop",
        "mov.l @(telemetry_startup_stock,pc),r0",
    ]
    if texts[clear + 4 : clear + 4 + len(arm)] != arm:
        raise ValueError("startup does not arm exactly six knock margin latches")


def _validate_capture(parsed):
    texts = _texts(parsed)
    if texts[0] != "sts.l pr,@-r15" or texts.count("lds.l @r15+,pr") != 2:
        raise ValueError("capture or knock margin wrapper does not preserve PR")
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
    if texts.count("mov.b @r4+,r0") != 1 or texts.count("dt r2") != 5:
        raise ValueError("bounded snapshot or mailbox copy loops differ")
    rearm = [
        "mov r6,r0", "cmp/eq 0x4,r0", "bf telemetry_build_context_advance",
        "mov.w @(telemetry_build_margin_idle,pc),r1", "mov r3,r5",
        "add 0x10,r5", "mov #0x6,r2", "mov.w r1,@r5", "add 0x2,r5", "dt r2",
        "bf telemetry_build_margin_rearm_loop", "add 0x1,r6",
    ]
    if texts.count("mov.w r1,@r5") != 1:
        raise ValueError("knock margin rearm loop differs")
    start = texts.index("mov.w r1,@r5") - 7
    if texts[start : start + len(rearm)] != rearm:
        raise ValueError("knock margin rearm is not bound to context 4")
    wrapper = texts.index("sts.l pr,@-r15", 1)
    if texts[wrapper : wrapper + 4] != [
        "sts.l pr,@-r15", "mov.l @(telemetry_margin_stock,pc),r0",
        "jsr @r0", "nop",
    ]:
        raise ValueError("knock margin wrapper does not run stock first")
    if texts.count("jsr @r0") != 1 or texts.count("sts.l pr,@-r15") != 2:
        raise ValueError("knock margin wrapper call graph differs")
    if (
        texts.count("mov.w r2,@(r0,r1)") != 1
        or texts.count("cmp/hi r2,r7") != 1
        or texts.count("cmp/hs r5,r2") != 1
    ):
        raise ValueError("knock margin comparison or latch write differs")
    for required in (
        "telemetry_capture_due", "telemetry_capture_busy_bank",
        "telemetry_capture_idle", "telemetry_build_page_loop",
        "telemetry_build_context_page_9_byte_loop",
        "telemetry_build_context_page_10_byte_loop",
        "telemetry_request_copy_loop",
        "telemetry_margin_primary_channel", "telemetry_margin_exceeded",
        "telemetry_margin_negative", "telemetry_margin_compare",
        "telemetry_margin_return",
    ):
        if required not in parsed.labels:
            raise ValueError(f"capture lacks {required}")


def _validate_completion(parsed, variant="combined-mailbox26"):
    texts = _texts(parsed)
    prologue = [f"mov.l r{index},@-r15" for index in range(8)] + ["sts.l pr,@-r15"]
    if variant == "mailbox26-tail-chain":
        tail = [
            "bsr telemetry_handle_completion",
            "nop",
            "lds.l @r15+,pr",
            *[f"mov.l @r15+,r{index}" for index in range(7, 0, -1)],
            "mov.l @(telemetry_stock_sle1_isr,pc),r0",
            "jmp @r0",
            "mov.l @r15+,r0",
        ]
        if texts[:9] != prologue or texts[9 : 9 + len(tail)] != tail:
            raise ValueError("tail-chain SLE1 wrapper ABI differs")
        if texts.count("rte") != 0 or texts.count("jsr @r0") != 3:
            raise ValueError("tail-chain completion call graph differs")
        if texts.count("mov.w r5,@r4") != 2:
            raise ValueError("custom mailbox acknowledgment behavior differs")
        if "telemetry_queue_corrupt" not in parsed.labels:
            raise ValueError("completion lacks fail-closed corrupt-state path")
        return
    if variant != "combined-mailbox26":
        raise ValueError(f"unsupported completion variant {variant!r}")
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
    identity = _manifest_identity(can_telemetry_profile.load_manifest())
    expected_words = _expected_word_literals(identity)
    source_dir = layout_model.DEFAULT_MANIFEST.parent
    parsed_by_unit = {}
    expected_literals = (
        layout.source_literal_by_unit or _expected_long_literals()
    )
    source_texts = layout.source_text_by_unit
    for unit in layout.assembly_units:
        source_path = source_dir / unit.source
        source = source_texts.get(unit.key)
        if source is None:
            source = source_path.read_text(encoding="utf-8")
        parsed = common.parse_source_text(
            source, source_path, unit.span.start, unit.span.end
        )
        parsed_by_unit[unit.key] = parsed
        _validate_instruction_forms(parsed)
        common._validate_delay_slots(
            parsed,
            allow_tail_restore=(
                layout.variant == "mailbox26-tail-chain"
                and unit.key == "completion"
            ),
        )
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
        if unit.key in expected_words:
            published = common._word_literals(parsed)
            carried = {
                label: published.get(label)
                for label in expected_words[unit.key]
            }
            if carried != expected_words[unit.key]:
                raise ValueError(
                    f"{unit.key}: wire identity literals differ from the manifest"
                )
        if unit.key == "wrappers":
            _validate_wrappers(parsed)
        elif unit.key == "capture":
            _validate_capture(parsed)
            _validate_identity_symbols(source, unit.key)
            _validate_identity_immediates(
                parsed, unit.key, identity, "mov #{pages},r6"
            )
        elif unit.key == "completion":
            _validate_completion(parsed, layout.variant)
        elif unit.key == "control":
            _validate_control(parsed)
            _validate_identity_symbols(source, unit.key)
            _validate_identity_immediates(
                parsed, unit.key, identity, "cmp/eq {pages},r0"
            )
        elif unit.key == "tables":
            expected = can_telemetry_profile.render_tables(
                can_telemetry_profile.load_manifest()
            )
            if not source_texts and source != expected:
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
        audits.append(common.validate_source_blob(
            parsed_by_unit[unit.key],
            blob,
            unit.span.start,
            addresses,
            allow_tail_restore=(
                layout.variant == "mailbox26-tail-chain"
                and unit.key == "completion"
            ),
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
    parser.add_argument("--payloads", type=Path, default=DEFAULT_PAYLOADS)
    args = parser.parse_args(argv)
    layout = layout_model.load_layout()
    parsed = validate_assembly_sources(layout)
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
