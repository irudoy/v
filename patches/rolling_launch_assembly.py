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
from patches import rolling_launch_flow as flow_model
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
    "spark_cut": "rolling_launch_spark_cut",
    "spark_events": "rolling_launch_spark_events",
    "slot_validator": "rolling_launch_slot_validator",
    "rpm_controller": "rolling_launch_rpm_controller",
    "rpm_fraction": "rolling_launch_rpm_fraction",
    "control_publisher": "rolling_launch_control_publisher",
    "ignition_publisher": "rolling_launch_ignition_publisher",
    "actuation": "rolling_launch_actuation",
    "state_check": "rolling_launch_state_check",
}
# Literals that name an entry or a table of another unit. Each value must
# equal the address of the label in the assembled source of that unit.
INTERNAL_ENTRIES = (
    ("wrappers", "rolling_launch_engine_entry", "engine", "rolling_launch_engine"),
    ("engine", "rl_state_check_entry", "state_check", "rolling_launch_state_check_masked"),
    ("engine", "rl_load_views_entry", "state_check", "rolling_launch_load_views"),
    ("engine", "rl_slot_validator_entry", "slot_validator", "rolling_launch_slot_validator"),
    ("engine", "rl_speed_controller_entry", "speed_controller", "rolling_launch_speed_controller"),
    ("engine", "rl_rpm_controller_entry", "rpm", "rolling_launch_rpm_controller"),
    ("speed_controller", "rl_spd_control_publisher", "actuation", "rolling_launch_control_publisher"),
    ("rpm", "rl_rpm_control_publisher", "actuation", "rolling_launch_control_publisher"),
    ("actuation", "rl_act_state_check", "state_check", "rolling_launch_state_check"),
    ("actuation", "rl_act_views", "state_check", "rolling_launch_views"),
    ("state_check", "rl_sc_q_entry", "actuation", "rolling_launch_q"),
    ("state_check", "rl_sc_byte_limits", "state_check", "rl_sc_byte_limit_table"),
)
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
    """Load SHA-validated executable spans only for a ready layout."""
    layout = layout or layout_model.load_layout()
    if not layout.payloads_ready:
        return {}
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
        # GNU as relaxes an out-of-reach BT/BF into a longer sequence, which
        # moves every later address away from the parsed layout.
        if mnemonic in ("bt", "bf"):
            target = parsed.labels[statement.text.split()[1]]
            if not -256 <= target - (statement.address + 4) <= 254:
                raise ValueError(
                    f"{parsed.path}:{statement.line_number}: {mnemonic} "
                    "target lies beyond the 8-bit branch reach"
                )


def _stores(texts):
    return sorted(
        text for text in texts
        if text.startswith(("mov.b r", "mov.w r", "mov.l r"))
        and not text.endswith(",@-r15")
    )


def _registers(texts):
    registers = set()
    for text in texts:
        registers.update(common.REGISTER_RE.findall(text))
    return registers


def _writes(texts, *registers):
    """True when an instruction other than a compare or test targets a register."""
    targets = tuple(f",{name}" for name in registers)
    return any(
        text.endswith(targets) and not text.startswith(("cmp/", "tst "))
        for text in texts
    )


def _region(parsed, start, end=None):
    """Instruction texts from label start up to label end or the unit end."""
    low = parsed.labels[start]
    high = parsed.labels[end] if end is not None else None
    return [
        item.text.lower() for item in _instructions(parsed)
        if low <= item.address and (high is None or item.address < high)
    ]


def _masked_group(save, group):
    """A store group between a mask to SR.I=15 and the restore of the saved SR."""
    return [
        f"stc sr,{save}", f"mov {save},r0", "or 0xf0,r0", "ldc r0,sr",
        *group, f"ldc {save},sr",
    ]


def _sr_texts(texts):
    return [text for text in texts if text.startswith(("stc", "ldc"))]


def _validate_wrapper_abi(parsed):
    texts = _texts(parsed)
    if texts[:1] != ["sts.l pr,@-r15"]:
        raise ValueError("periodic wrapper does not save PR")
    if texts[7:10] != ["lds.l @r15+,pr", "rts", "nop"]:
        raise ValueError("periodic wrapper does not restore PR")
    jsr = [index for index, text in enumerate(texts) if text == "jsr @r0"]
    if jsr != [2, 5, 38] or any(texts[index + 1] != "nop" for index in jsr):
        raise ValueError("wrapper JSR/NOP call order differs")
    if texts.count("jmp @r0") != 2:
        raise ValueError("selector arbiter needs two tail jumps")
    startup = [
        "sts.l pr,@-r15",
        "mov.l @(rolling_launch_state_address_startup,pc),r1",
        "mov #0x0,r0",
        "mov #0xb,r2",
        "mov.l r0,@r1",
        "add 0x4,r1",
        "dt r2",
        "bf rolling_launch_startup_clear_state",
        "mov.l @(rolling_launch_extension_address_startup,pc),r1",
        "mov #0x8,r2",
        "mov.l r0,@r1",
        "add 0x4,r1",
        "dt r2",
        "bf rolling_launch_startup_clear_extension",
        "mov.l @(rolling_launch_default_efficiency,pc),r0",
        "add -0x14,r1",
        "mov.l r0,@r1",
        "mov.l @(rolling_launch_base_startup,pc),r0",
        "jsr @r0",
        "nop",
        "lds.l @r15+,pr",
        "rts",
        "nop",
    ]
    if _region(parsed, "rolling_launch_startup_wrapper") != startup:
        raise ValueError(
            "startup wrapper must clear the base state and the extension and "
            "store the default efficiency before the base startup"
        )


def _validate_engine_abi(parsed):
    texts = _texts(parsed)
    saves = [f"mov.l r{number},@-r15" for number in range(8, 15)]
    prologue = [
        "sts.l pr,@-r15",
        *saves,
        "mov.l @(rl_state_address,pc),r8",
        "mov.l @(rl_extension_address,pc),r9",
        "mov.l @(rl_config_address,pc),r10",
        "mov.l @(rl_state_check_entry,pc),r0",
        "jsr @r0",
        "nop",
        "bt rl_state_valid",
        "bra rl_corrupt_state",
        "nop",
        "bsr rl_validate_config",
        "nop",
        "mov r0,r12",
    ]
    if texts[:len(prologue)] != prologue:
        raise ValueError(
            "engine must check the record and the configuration before the pass"
        )
    restores = [f"mov.l @r15+,r{number}" for number in range(14, 7, -1)]
    # The ignition publisher rewrites the trim, ready mark and efficiency from
    # the crank-tooth interrupt, so the views are read, computed and stored
    # under one mask.
    exit_sequence = [
        "stc sr,r6",
        "mov r6,r0",
        "or 0xf0,r0",
        "ldc r0,sr",
        "mov r9,r7",
        "mov.l @(rl_load_views_entry,pc),r0",
        "jsr @r0",
        "nop",
        "mov.l r3,@(0xc,r9)",
        "mov r1,r0",
        "mov.w r0,@(0x1e,r9)",
        "ldc r6,sr",
        *restores,
        "lds.l @r15+,pr",
        "rts",
        "nop",
    ]
    if _region(parsed, "rl_engine_exit")[:len(exit_sequence)] != exit_sequence:
        raise ValueError("engine exit does not store the wire views under one mask")
    if texts.count("jsr @r0") != 4:
        raise ValueError(
            "engine must call the record check, the limiter commit, one "
            "controller and the wire views"
        )
    # Map 1 first, then base 0x00..0x1B, the trim and reserved byte at 0x1E/0x1F
    # and the extension, e = 1000, and COOLDOWN with reason 16.
    corrupt = [
        "mov #0x0,r4",
        "mov.l @(rl_limiter_commit,pc),r0",
        "jsr @r0",
        "nop",
        "mov r8,r1",
        "mov #0x0,r0",
        "mov #0x7,r2",
        "mov.l r0,@r1",
        "add 0x4,r1",
        "dt r2",
        "bf rl_corrupt_clear_base",
        "mov #0x1e,r0",
        "mov.w r2,@(r0,r8)",
        "mov r9,r1",
        "mov #0x0,r0",
        "mov #0x8,r2",
        "mov.l r0,@r1",
        "add 0x4,r1",
        "dt r2",
        "bf rl_corrupt_clear_extension",
        "mov #0x7d,r0",
        "shll2 r0",
        "shll r0",
        "mov.w r0,@(0xc,r9)",
        "mov #0x2,r0",
        "mov.b r0,@r8",
        "mov #0x10,r0",
        "mov.b r0,@(0x1,r8)",
    ]
    if _region(parsed, "rl_corrupt_state", "rl_engine_exit") != corrupt:
        raise ValueError("corrupt-state recovery differs")
    slot_tail = [
        "mov.l @(rl_slot_validator_entry,pc),r0",
        "jmp @r0",
        "nop",
    ]
    if texts.count("jmp @r0") != 1 or not _contains(texts, slot_tail):
        raise ValueError("configuration validation does not end in the slot validator")
    controller_call = [
        "mov r10,r4",
        "mov r8,r5",
        "mov r14,r0",
        "cmp/eq 0x1,r0",
        "mov.l @(rl_speed_controller_entry,pc),r0",
        "bf rl_publish_controller",
        "mov.l @(rl_rpm_controller_entry,pc),r0",
        "jsr @r0",
        "nop",
    ]
    if not _contains(texts, controller_call):
        raise ValueError("engine controller call differs")
    table_override = [
        "mov r12,r0",
        "tst 0x2,r0",
        "bf rl_gate_table_valid",
        "mov #-0x2,r0",
        "and r0,r11",
        "mov #0x1,r13",
    ]
    if not _contains(texts, table_override):
        raise ValueError("an invalid efficiency table keeps CONFIG_VALID")
    rearm = ["mov r12,r0", "cmp/eq 0x3,r0", "bt rl_cooldown_valid"]
    if not _contains(texts, rearm):
        raise ValueError("COOLDOWN rearms without a valid configuration and table")
    if [text for text in texts if text.startswith(("stc", "ldc"))] != [
            "stc sr,r6", "ldc r0,sr", "ldc r6,sr"]:
        raise ValueError("engine changes SR outside its masked wire views")
    destination = re.compile(r"@(?:\([^)]*,r[89]\)|r[189]|-r15)$")
    if any(not destination.search(text) for text in _stores(texts)):
        raise ValueError("engine stores outside the base state and the extension")
    if texts.count("mov.l r0,@r1") != 2:
        raise ValueError("engine stores through r1 outside its clear loops")
    required = {
        "rl_state_valid",
        "rl_corrupt_state",
        "rl_validate_config",
        "rl_gate_inputs",
        "rl_activate",
        "rl_active_post",
        "rl_publish_active",
        "rl_abort",
        "rl_engine_exit",
        "rl_window",
        "rl_gate_valid",
        "rl_gate_fail",
    }
    if not required <= set(parsed.labels):
        raise ValueError("engine state-machine label set is incomplete")
    # The valid gate tests the validator result without a scratch register:
    # r3 holds the sampled button through the gate chain.
    if _region(parsed, "rl_gate_valid", "rl_gate_pass_t") != ["cmp/pl r12"]:
        raise ValueError("engine valid gate must only test r12")


def _contains(texts, sequence):
    return any(
        texts[index : index + len(sequence)] == sequence
        for index in range(len(texts) - len(sequence) + 1)
    )


def _validate_ignition_abi(parsed):
    texts = _texts(parsed)
    saves = [
        "sts.l pr,@-r15", "sts.l macl,@-r15",
        "mov.l r5,@-r15", "mov.l r6,@-r15", "mov.l r7,@-r15",
        "mov r4,r5",
    ]
    tail = ["mov.l @(rl_ign_stock_consumer,pc),r0", "jmp @r0", "nop"]
    publish_and_apply = [
        "mov.l @(rl_ign_publisher,pc),r0", "jsr @r0", "nop",
        "mov r5,r0", "mov.l @(rl_ign_command_address,pc),r1",
        "mov.b r0,@r1", "mov r5,r4",
        "mov.l @r15+,r7", "mov.l @r15+,r6", "mov.l @r15+,r5",
        "lds.l @r15+,macl", "lds.l @r15+,pr", *tail,
    ]
    if texts[:len(saves)] != saves or texts[-len(publish_and_apply):] != publish_and_apply:
        raise ValueError("ignition adapter must apply the publisher return and restore its caller")
    transfers = [text for text in texts if text.split()[0] in {"jsr", "bsr", "jmp", "rts", "rte"}]
    if transfers != ["jsr @r0", "jmp @r0"]:
        raise ValueError("ignition adapter must call one publisher and tail-jump to stock")
    stores = [text for text in texts if text.startswith(("mov.b r", "mov.w r", "mov.l r"))]
    if stores != ["mov.l r5,@-r15", "mov.l r6,@-r15", "mov.l r7,@-r15", "mov.b r0,@r1"]:
        raise ValueError("ignition adapter store contract differs")
    gates = ["mov.b @r1,r0", "cmp/eq 0x1,r0", "bf rl_ign_publish",
             "mov.b @(0x5,r1),r0", "cmp/eq 0x1,r0", "bf rl_ign_publish"]
    fallback = ["mov.b @r2,r0", "tst 0x40,r0", "bf rl_ign_publish"]
    slot = ["mov.b @(0x4,r1),r0", "extu.b r0,r0", "mov #0x5,r2",
            "cmp/hs r2,r0", "bt rl_ign_publish", "shll2 r0", "mov r0,r2",
            "shll r2", "add r2,r0", "mov.l @(rl_ign_slot_table,pc),r2", "add r0,r2"]
    limits = ["mov.b @(0x4,r2),r0", "extu.b r0,r3", "mov #0x78,r2",
              "cmp/hi r2,r3", "bt rl_ign_publish", "mov #0x1e,r0",
              "mov.b @(r0,r1),r0", "extu.b r0,r0", "mov #0x28,r2",
              "cmp/hi r2,r0", "bt rl_ign_publish"]
    retard_only = ["extu.b r4,r2", "add r2,r0", "cmp/hi r3,r0",
                   "bf rl_ign_floor_ready", "mov r3,r0", "cmp/hi r2,r0",
                   "bf rl_ign_publish", "mov r0,r5"]
    if not all(_contains(texts, item) for item in (gates, fallback, slot, limits, retard_only)):
        raise ValueError("ignition adapter gates differ")
    registers = set()
    for statement in _instructions(parsed):
        registers.update(common.REGISTER_RE.findall(statement.text.lower()))
    if not registers <= {f"r{number}" for number in range(8)} | {"r15", "pr", "macl"}:
        raise ValueError("ignition adapter changes an undeclared register")


def _validate_spark_cut_abi(parsed):
    texts = _texts(parsed)
    if "rolling_launch_spark_events" in parsed.labels:
        if texts[:2] != ["mov r5,r4", "add 0x1c,r4"] or texts[-3:] != ["ldc r7,sr", "rts", "nop"]:
            raise ValueError("spark events helper entry or return differs")
        if [text for text in texts if text.split()[0] in {"jsr", "bsr", "jmp", "rts", "rte"}] != ["rts"]:
            raise ValueError("spark events helper must be a leaf")
        if sorted(_stores(texts)) != sorted(["mov.b r0,@r4"]*2 + ["mov.b r0,@r3"]*2):
            raise ValueError("spark events helper stores outside quiet state and the latch")
        if not _contains(texts, ["stc sr,r7", "mov r7,r0", "or 0xf0,r0", "ldc r0,sr", "mov.b @r3,r0"]):
            raise ValueError("spark events latch check is not masked")
        if texts.count("mov.b @r5,r0") != 1 or texts.count("mov.b @(0x5,r5),r0") != 1:
            raise ValueError("spark events phase and mode read set differs")
        allowed = {"r0", "r1", "r2", "r3", "r4", "r5", "r7", "sr"}
    else:
        saves = ["mov.l r0,@-r15", "sts.l pr,@-r15"] + [f"mov.l r{n},@-r15" for n in range(1, 8)]
        saves += ["stc sr,r0", "mov.l r0,@-r15"]
        restores = ["mov.l @r15+,r0", "ldc r0,sr"] + [f"mov.l @r15+,r{n}" for n in range(7, 0, -1)]
        restores += ["lds.l @r15+,pr", "mov.l @(rl_cut_stock_divider,pc),r0", "jmp @r0", "mov.l @r15+,r0"]
        if texts[:len(saves)] != saves or texts[-len(restores):] != restores:
            raise ValueError("dwell veto must preserve the divider inputs, caller and SR")
        transfers = [text for text in texts if text.split()[0] in {"jsr", "bsr", "jmp", "rts", "rte"}]
        if transfers != ["bsr 0x000d6780", "jmp @r0"]:
            raise ValueError("dwell veto must call its event helper and tail-jump to the divider")
        if texts.count("mov.w @(0x1a,r5),r0") != 1 or any(text.startswith("mov.b @(0x1a,r5)") for text in texts):
            raise ValueError("dwell veto must consume one aligned q word")
        expected = ["mov.w r7,@(r0,r4)", "mov.l r0,@(0x10,r3)", "mov.w r0,@(0x18,r3)",
                    "mov.b r0,@r3", "mov.b r0,@(0x1,r4)"]
        expected += [f"mov.w r0,@(0x{n:x},r4)" for n in range(4, 15, 2)]
        stores = [text for text in _stores(texts) if not text.endswith(",@-r15")]
        if sorted(stores) != sorted(expected):
            raise ValueError("dwell veto actuator/counter store contract differs")
        commit = _region(parsed, "rl_cut_commit", "rl_cut_unmask")
        if not _contains(commit, ["stc sr,r6", "mov r6,r0", "or 0xf0,r0", "ldc r0,sr"]):
            raise ValueError("dwell veto event commit is not masked")
        if _stores_in_order(commit) != expected[:5] or texts[texts.index("ldc r6,sr")+1:texts.index("ldc r6,sr")+3] != ["bra rl_cut_chain", "nop"]:
            raise ValueError("dwell veto event commit order differs")
        if not _contains(texts, ["mov.l @(rl_cut_dwell_mask_address,pc),r3", "mov.b @(0x1,r3),r0", "tst r0,r0", "bf rl_cut_chain", "mov.b @r3,r0"]):
            raise ValueError("dwell veto must use the armed cylinder and the stock guard")
        allowed = {f"r{n}" for n in range(8)} | {"r15", "pr", "sr"}
    registers = set()
    for statement in _instructions(parsed):
        registers.update(common.REGISTER_RE.findall(statement.text.lower()))
    if not registers <= allowed:
        raise ValueError("dwell veto changes an undeclared register")


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


def _validate_speed_controller_abi(parsed):
    texts = _texts(parsed)
    if texts[:1] != ["sts.l pr,@-r15"]:
        raise ValueError("speed controller does not save PR")
    tail = [
        "mov r2,r3",
        "lds.l @r15+,pr",
        "mov.l @(rl_spd_control_publisher,pc),r0",
        "jmp @r0",
        "nop",
    ]
    if texts[-5:] != tail or texts.count("jmp @r0") != 1:
        raise ValueError(
            "speed controller does not pass u in r3 to the control publisher"
        )
    # The ignition publisher checks control_error == speed_error.
    error_pair = _masked_group(
        "r6", ["mov r2,r0", "mov.w r0,@(0x10,r5)", "mov.w r0,@(0x2,r7)"]
    )
    if not _contains(texts, error_pair) or _sr_texts(texts) != _sr_texts(error_pair):
        raise ValueError("speed controller error pair is not one masked store group")
    divider_call = [
        "mov.l @(rl_spd_unsigned_divide,pc),r3",
        "jsr @r3",
        "nop",
    ]
    if (
        texts.count("jsr @r3") != 1
        or not _contains(texts, divider_call)
        or any(text.startswith(("jsr @r0", "bsr", "rts")) for text in texts)
    ):
        raise ValueError("speed controller divider call differs")
    slot_gain = [
        "mov.b @(0x4,r5),r0", "extu.b r0,r0", "shll2 r0", "mov r0,r1",
        "shll r1", "add r1,r0", "add r4,r0", "add 0x28,r0",
        "mov.w @r0,r0", "muls.w r0,r2",
    ]
    if not _contains(texts, slot_gain):
        raise ValueError("speed controller does not read the slot gain")
    if texts.count("mulu.w r0,r1") != 1 or texts.count("muls.w r0,r2") != 1:
        raise ValueError("speed controller arithmetic differs")
    expected = sorted([
        "mov.w r0,@(0x10,r5)",
        "mov.w r0,@(0x2,r7)",
        "mov.w r0,@(0x12,r5)",
        "mov.w r0,@(0x16,r5)",
    ])
    if _stores(texts) != expected:
        raise ValueError("speed controller store contract differs")
    allowed = {f"r{number}" for number in range(8)} | {"r15", "pr", "sr", "macl"}
    if not _registers(texts) <= allowed or _writes(texts, "r4", "r5"):
        raise ValueError("speed controller clobbers an undeclared register")


def _validate_rpm_abi(parsed):
    controller = _region(
        parsed, "rolling_launch_rpm_controller", "rolling_launch_rpm_fraction"
    )
    fraction = _region(parsed, "rolling_launch_rpm_fraction")
    tail = [
        "lds.l @r15+,pr",
        "mov.l @(rl_rpm_control_publisher,pc),r0",
        "jmp @r0",
        "nop",
    ]
    if controller[:1] != ["sts.l pr,@-r15"] or controller[-4:] != tail:
        raise ValueError("RPM controller does not end in the control publisher")
    width = ["add r4,r1", "add 0x28,r1", "mov.w @(0xa,r1),r0"]
    call = [
        "mov.l r4,@-r15",
        "mov.l r5,@-r15",
        "extu.w r0,r5",
        "mov r6,r4",
        "bsr rolling_launch_rpm_fraction",
        "nop",
        "mov.l @r15+,r5",
        "mov.l @r15+,r4",
        "mov r0,r3",
    ]
    if not _contains(controller, width + call):
        raise ValueError("RPM controller does not pass p in r3 to the control publisher")
    # The ignition publisher checks control_error == rpm_error.
    error_pair = _masked_group(
        "r3", ["mov r6,r0", "mov.w r0,@(0x18,r5)", "mov.w r0,@(0x2,r7)"]
    )
    if (
        not _contains(controller, error_pair)
        or _sr_texts(controller) != _sr_texts(error_pair)
    ):
        raise ValueError("RPM controller error pair is not one masked store group")
    if _stores(controller) != sorted([
        "mov.w r0,@(0x18,r5)",
        "mov.w r0,@(0x2,r7)",
    ]):
        raise ValueError("RPM controller store contract differs")
    divider_call = [
        "sts.l pr,@-r15",
        "mov r4,r1",
        "neg r1,r1",
        "mulu.w r0,r1",
        "sts macl,r1",
        "mov r5,r0",
        "mov.l @(rl_rpm_unsigned_divide,pc),r2",
        "jsr @r2",
        "nop",
        "lds.l @r15+,pr",
    ]
    if (
        fraction[:3] != ["mov #0x0,r0", "cmp/pz r4", "bt rl_rpm_fraction_return"]
        or fraction[-2:] != ["rts", "nop"]
        or fraction.count("rts") != 1
        or fraction.count("jsr @r2") != 1
        or not _contains(fraction, divider_call)
        or _stores(fraction)
    ):
        raise ValueError("RPM fraction must be a store-free divider leaf")
    if not _registers(fraction) <= {"r0", "r1", "r2", "r4", "r5", "r15", "pr", "macl"}:
        raise ValueError("RPM fraction uses an undeclared register")
    if _writes(fraction, "r4", "r5"):
        raise ValueError("RPM fraction changes its arguments")
    allowed = {f"r{number}" for number in range(8)} | {"r15", "pr", "sr", "macl"}
    if not _registers(controller) <= allowed:
        raise ValueError("RPM controller clobbers an undeclared register")


def _validate_actuation_abi(parsed):
    control = _region(
        parsed, "rolling_launch_control_publisher", "rolling_launch_ignition_publisher"
    )
    ignition = _region(
        parsed, "rolling_launch_ignition_publisher", "rolling_launch_actuation"
    )
    body = _region(parsed, "rolling_launch_actuation", "rl_act_ignition_ready")
    ready = _region(parsed, "rl_act_ignition_ready", "rolling_launch_q")
    q = _region(parsed, "rolling_launch_q")
    # The control publisher masks interrupts before it stores the law output
    # and keeps them masked through the commit of the body, so the law, the
    # torque fraction, the command tuple it reads, e, q and the views form one
    # store group for the ignition publisher.
    control_law = [
        "stc sr,r0",
        "mov.l r0,@-r15",
        "or 0xf0,r0",
        "ldc r0,sr",
        "mov.l @(rl_act_extension_address,pc),r7",
        "mov r3,r0",
        "mov.w r0,@(0x16,r7)",
        "mov.b @r7,r0",
        "cmp/eq 0x2,r0",
        "bf rl_act_control_tuple",
        "mov r3,r0",
        "mov.w r0,@(0xe,r5)",
    ]
    control_ready = [
        "mov.b @r5,r0",
        "cmp/eq 0x1,r0",
        "bf rl_act_control_idle",
        "mov.b @(0x5,r5),r0",
        "cmp/eq 0x1,r0",
        "bt rl_act_control_publish",
        "mov #0x0,r2",
        "bra rolling_launch_actuation",
        "nop",
    ]
    if (
        control[:len(control_law)] != control_law
        or control[-len(control_ready):] != control_ready
        or _stores(control) != sorted(["mov.w r0,@(0x16,r7)", "mov.w r0,@(0xe,r5)"])
        or _sr_texts(control) != ["stc sr,r0", "ldc r0,sr"]
    ):
        raise ValueError(
            "control publisher must store the law under the mask of the "
            "publication and pass ready only in ACTIVE hold"
        )
    ignition_prefix = [
        "stc sr,r0",
        "mov.l r0,@-r15",
        "sts.l pr,@-r15",
        "mov.l @(rl_act_state_check,pc),r0",
        "jsr @r0",
        "nop",
        "lds.l @r15+,pr",
        "bf rl_act_ignition_stock",
        "mov.l @(rl_act_state_address,pc),r3",
        "mov.w @(0x2,r3),r0",
        "tst 0x1,r0",
        "bt rl_act_ignition_stock",
    ]
    trim_bound = ["mov #0x28,r0", "cmp/hi r0,r1", "bt rl_act_ignition_stock"]
    if (
        ignition[:len(ignition_prefix)] != ignition_prefix
        or not _contains(ignition, trim_bound)
        or _stores(ignition)
    ):
        raise ValueError(
            "ignition publisher must check the record, CONFIG_VALID and the "
            "trim bound before publishing"
        )
    fallback = [
        "mov.l @(rl_act_apc_mode_address,pc),r0",
        "mov.b @r0,r0",
        "tst 0x40,r0",
        "bf rl_act_ignition_stock",
    ]
    # P reaches the body only after ready = 1: no branch of any section of the
    # unit enters the publish path, so the phase, mode, fallback and trim
    # checks all lead to stock.
    latched = [
        "mov #0x1e,r0",
        "mov.b @(r0,r3),r0",
        "cmp/hs r1,r0",
        "bf rl_act_ignition_stock",
        "mov #0x1,r2",
        "shll8 r6",
        "extu.b r5,r0",
        "or r0,r6",
        "bra rolling_launch_actuation",
        "nop",
    ]
    if any(text.split()[-1] == "rl_act_ignition_publish"
           for text in control + ignition + body + ready + q if text[0] == "b"):
        raise ValueError("ignition publisher publishes P without ready")
    # The stock path returns the stock command as the command to apply.
    stock = [
        "mov r4,r5",
        "extu.b r4,r6",
        "mov r6,r0",
        "shll8 r6",
        "or r0,r6",
        "mov #0x0,r1",
        "mov #0x0,r2",
        "bra rolling_launch_actuation",
        "nop",
    ]
    if (
        not _contains(ready, fallback)
        or not _contains(ready, latched)
        or ready[-len(stock):] != stock
        or _stores(ready)
    ):
        raise ValueError("ignition ready or stock publication differs")
    if (
        _writes(control, "r4", "r5")
        or _writes(ignition + ready, "r4")
        or [text for text in ignition + ready if text.endswith(",r5")] != ["mov r4,r5"]
        or _sr_texts(ignition + ready) != ["stc sr,r0"]
    ):
        raise ValueError("publishers change their arguments or SR")
    if (
        body[:3] != ["mov.l r4,@-r15", "mov.l r5,@-r15", "sts.l pr,@-r15"]
        or body[-7:] != [
            "lds.l @r15+,pr", "mov.l @r15+,r5", "mov.l @r15+,r4",
            "mov.l @r15+,r0", "ldc r0,sr", "rts", "nop",
        ]
    ):
        raise ValueError(
            "actuation body does not preserve r4, r5 and PR and restore the "
            "SR of its caller"
        )
    commit = [
        "mov.l @(rl_act_views,pc),r0",
        "jsr @r0",
        "nop",
        "mov.l @(rl_act_state_address,pc),r4",
        "stc sr,r0",
        "or 0xf0,r0",
        "ldc r0,sr",
        "mov.l r6,@(0x8,r7)",
        "mov.l r3,@(0xc,r7)",
        "mov r1,r0",
        "mov.w r0,@(0x1e,r7)",
        "mov r5,r0",
        "mov.w r0,@(0x1a,r4)",
        "lds.l @r15+,pr",
    ]
    if (
        not _contains(body, commit)
        or _sr_texts(body) != ["stc sr,r0", "ldc r0,sr", "ldc r0,sr"]
    ):
        raise ValueError("actuation must publish with interrupts masked and q last")
    if _stores(body) != sorted([
        "mov.l r6,@(0x8,r7)",
        "mov.l r3,@(0xc,r7)",
        "mov.w r0,@(0x1e,r7)",
        "mov.w r0,@(0x1a,r4)",
    ]):
        raise ValueError("actuation store contract differs")
    if body.count("bsr rolling_launch_q") != 1:
        raise ValueError("actuation q call differs")
    divider_call = [
        "mov.l @(rl_act_unsigned_divide,pc),r2",
        "jsr @r2",
        "nop",
    ]
    if (
        q[:3] != ["mov r1,r0", "cmp/eq 0x1,r0", "bt rl_q_rpm"]
        or q.count("jsr @r2") != 1
        or not _contains(q, divider_call)
        or q.count("rts") != 2
        or _stores(q)
        or not _registers(q) <= {"r0", "r1", "r2", "r3", "r15", "pr", "macl"}
        or _writes(q, "r3")
    ):
        raise ValueError("q must be a store-free leaf of r1..r3")
    texts = _texts(parsed)
    if texts.count("jsr @r0") != 2 or texts.count("jmp @r0"):
        raise ValueError("actuation calls differ")
    allowed = {f"r{number}" for number in range(8)} | {"r15", "pr", "sr", "macl"}
    if not _registers(texts) <= allowed:
        raise ValueError("actuation uses an undeclared register")


def _validate_slot_validator_abi(parsed):
    texts = _texts(parsed)
    if texts[:3] != [
        "mov.l @(rl_val_config_address,pc),r3", "tst r7,r7", "bt rl_val_return",
    ]:
        raise ValueError("slot validator does not reject an invalid head")
    # The table is checked only after five valid slots, so an invalid record
    # returns 0 and a valid one a positive result.
    if any(text.split()[-1] == "rl_val_table" for text in texts if text[0] == "b"):
        raise ValueError("slot validator branches to the table check")
    if texts[-3:] != ["mov r7,r0", "rts", "nop"] or texts.count("rts") != 1:
        raise ValueError("slot validator return differs")
    if any(
        text.startswith(("jsr", "bsr", "jmp", "sts.l", "lds.l"))
        for text in texts
    ) or _stores(texts):
        raise ValueError("slot validator must be a leaf without stores")
    required = ["mov #0x5,r5", "mov #0x1,r7", "mov #0x28,r5", "add 0x2,r7"]
    if any(texts.count(text) != 1 for text in required):
        raise ValueError("slot validator slot or table bounds differ")
    if not _registers(texts) <= {f"r{number}" for number in range(8)}:
        raise ValueError("slot validator uses an undeclared register")


def _validate_state_check_abi(parsed):
    texts = _texts(parsed)
    check = _region(
        parsed, "rolling_launch_state_check", "rolling_launch_load_views"
    )
    views = _region(parsed, "rolling_launch_load_views")
    # The interrupt entry keeps SR; the engine entry masks interrupts so that
    # a publication cannot split the fields it reads. Both save the SR of the
    # caller and restore it before they set T.
    entries = [
        "stc sr,r0",
        "mov.l r0,@-r15",
        "bra rl_check_begin",
        "nop",
        "stc sr,r0",
        "mov.l r0,@-r15",
        "or 0xf0,r0",
        "ldc r0,sr",
        "sts.l pr,@-r15",
        "mov.l @(rl_sc_state_address,pc),r6",
        "mov.l @(rl_sc_extension_address,pc),r7",
    ]
    entry = parsed.labels["rolling_launch_state_check"]
    if (
        check[:len(entries)] != entries
        or parsed.labels["rolling_launch_state_check_masked"] != entry + 8
        or parsed.labels["rl_check_begin"] != entry + 16
    ):
        raise ValueError(
            "record check entries do not save SR, mask the engine entry and "
            "load the base state and the extension"
        )
    q_call = ["mov.l @(rl_sc_q_entry,pc),r0", "jsr @r0", "nop"]
    compare = [
        "bsr rolling_launch_load_views",
        "nop",
        "mov.l @(0xc,r7),r0",
        "cmp/eq r0,r3",
        "bf rl_check_fail",
        "mov.w @(0x1e,r7),r0",
        "extu.w r0,r0",
        "xor r0,r1",
        "lds.l @r15+,pr",
        "mov.l @r15+,r0",
        "ldc r0,sr",
        "tst r1,r1",
        "rts",
        "nop",
    ]
    fail = ["mov #0x1,r1", "bra rl_check_return", "nop"]
    if (
        check.count("jsr @r0") != 1
        or not _contains(check, q_call)
        or not _contains(check, compare)
        or check[-len(fail):] != fail
        or check.count("rts") != 1
        or texts.count("bsr rolling_launch_load_views") != 1
        or _sr_texts(texts) != ["stc sr,r0", "stc sr,r0", "ldc r0,sr", "ldc r0,sr"]
    ):
        raise ValueError("record check calls or returns differ")
    loads = [
        "mov.b @(0xa,r7),r0",
        "extu.b r0,r1",
        "mov.b @(0xb,r7),r0",
        "extu.b r0,r2",
        "mov.w @(0xc,r7),r0",
        "extu.w r0,r3",
    ]
    if (
        views[:len(loads)] != loads
        or parsed.labels["rolling_launch_views"]
        != parsed.labels["rolling_launch_load_views"] + 2 * len(loads)
        or views[-2:] != ["rts", "nop"]
        or views.count("rts") != 1
        or any(text.startswith(("jsr", "bsr", "jmp", "sts", "lds")) for text in views)
        or not _registers(views) <= {"r0", "r1", "r2", "r3", "r7"}
    ):
        raise ValueError("wire views must be a leaf of r0..r3 and the extension")
    if _stores(texts):
        raise ValueError("record check and wire views must not store")
    if _writes(texts, "r4", "r5") or not _registers(texts) <= (
        {f"r{number}" for number in range(8)} | {"r15", "pr", "sr"}
    ):
        raise ValueError("record check changes a preserved register")


def _masked_flags(texts, masked=False):
    """SR.I=15 state at each instruction of a straight-line region."""
    flags = []
    for index, text in enumerate(texts):
        flags.append(masked)
        if text.startswith("ldc ") and text.endswith(",sr"):
            masked = text == "ldc r0,sr" and index and texts[index - 1] == "or 0xf0,r0"
    return flags


def _validate_publication_atomicity(parsed_by_unit):
    """Keep every record state that the ignition publisher can observe valid.

    The engine runs with interrupts enabled and the ignition publisher runs
    from the crank-tooth interrupt. In a steady ACTIVE pass every store that a
    record check couples to another field lies in a masked section: the
    controller error pairs, the law output with the torque fraction, the
    command tuple, e, q and the views, and the exit views. The integrator and
    the controller command have no coupled field. Transitions keep a store
    order instead: activation stores the phase first, the mode after the map,
    the law output 1000 before the kind and the latched trim last, and an
    abort leaves ACTIVE with its first store.
    """
    regions = (
        ("speed_controller", "rolling_launch_speed_controller", None, False,
         {"mov.w r0,@(0x12,r5)", "mov.w r0,@(0x16,r5)"}),
        ("rpm", "rolling_launch_rpm_controller", "rolling_launch_rpm_fraction", False, set()),
        ("actuation", "rolling_launch_control_publisher",
         "rolling_launch_ignition_publisher", False, set()),
        ("actuation", "rolling_launch_actuation", "rl_act_ignition_ready", False, set()),
    )
    for unit, start, end, masked, uncoupled in regions:
        texts = _region(parsed_by_unit[unit], start, end)
        flags = _masked_flags(texts, masked)
        if any(text in _stores([text]) and text not in uncoupled and not flag
               for text, flag in zip(texts, flags)):
            raise ValueError(f"{unit}: a coupled store lies outside a masked section")
    engine = parsed_by_unit["engine"]
    texts = _texts(engine)
    flags = _masked_flags(texts)
    views = {"mov.l r3,@(0xc,r9)", "mov.w r0,@(0x1e,r9)"}
    if any(text in views and not flag for text, flag in zip(texts, flags)) or sum(
            text in views for text in texts) != 2:
        raise ValueError("engine stores the wire views outside its masked exit")
    activation = _stores_in_order(_region(engine, "rl_activate", "rl_active_post"))
    if (
        activation[:1] != ["mov.b r0,@r8"]
        or activation[-1:] != ["mov.b r2,@(r0,r8)"]
        or activation.index("mov.b r0,@(0x4,r8)") > activation.index("mov.b r0,@(0x5,r8)")
    ):
        raise ValueError(
            "activation must store the phase first, the mode after the map and "
            "the latched trim last"
        )
    law = _region(engine, "rl_activate", "rl_active_post")
    kind = law.index("mov.b r0,@r9") if law.count("mov.b r0,@r9") == 1 else -1
    if kind < 4 or law[kind - 5:kind - 1] != [
            "mov #0x7d,r0", "shll2 r0", "shll r0", "mov.w r0,@(0x16,r9)"]:
        raise ValueError("activation must store the law output 1000 before the kind")
    abort = _stores_in_order(_region(engine, "rl_abort", "rl_corrupt_state"))
    if abort[:1] != ["mov.b r0,@r8"] or not {
            "mov.w r0,@(0x1a,r8)", "mov.b r0,@(0xb,r9)"} <= set(abort):
        raise ValueError("abort must leave ACTIVE with its first store and clear q and ready")


def _stores_in_order(texts):
    return [text for text in texts if _stores([text])]


def _validate_internal_entries(parsed_by_unit):
    """Check that entry literals name the labels of their target units."""
    for unit, literal, target, label in INTERNAL_ENTRIES:
        if unit not in parsed_by_unit or target not in parsed_by_unit:
            continue
        value = common._long_literals(parsed_by_unit[unit]).get(literal)
        if value != parsed_by_unit[target].labels.get(label):
            raise ValueError(f"{unit}: {literal} does not name {target}:{label}")


def _expected_long_literals():
    return {
        "wrappers": {
            "rolling_launch_periodic_stock": 0x000A9554,
            "rolling_launch_engine_entry": 0x000D38E4,
            "rolling_launch_state_address": 0xFFFF5D40,
            "rolling_launch_stock_ascd_host": 0x000D09D8,
            "rolling_launch_map_selector_host": 0x000D2108,
            "rolling_launch_state_address_startup": 0xFFFF5D40,
            "rolling_launch_extension_address_startup": 0xFFFF6100,
            "rolling_launch_default_efficiency": 0x03E803E8,
            "rolling_launch_base_startup": 0x000D22A0,
        },
        "engine": {
            "rl_state_address": 0xFFFF5D40,
            "rl_extension_address": 0xFFFF6100,
            "rl_config_address": 0x000D6320,
            "rl_state_check_entry": 0x000D7008,
            "rl_speed_address": 0xFFFF113C,
            "rl_rpm_address": 0xFFFF11BC,
            "rl_speed_raw_address": 0xFFFF3B3D,
            "rl_speed_age_address": 0xFFFF3B38,
            "rl_hcan_address": 0xFFFF4195,
            "rl_port_address": 0xFFFF4185,
            "rl_button_address": 0xFFFF2A85,
            "rl_gate_selector_address": 0xFFFF5D00,
            "rl_ascd_address": 0xFFFF41AE,
            "rl_pedal_address": 0xFFFF2672,
            "rl_coolant_address": 0xFFFF1077,
            "rl_speed_controller_entry": 0x000D40C0,
            "rl_rpm_controller_entry": 0x000D6400,
            "rl_limiter_commit": 0x000D3660,
            "rl_load_views_entry": 0x000D7184,
            "rl_slot_validator_entry": 0x000D6680,
        },
        "ignition_adapter": {
            "rl_ign_state_address": 0xFFFF5D40,
            "rl_ign_apc_mode_address": 0xFFFF24C9,
            "rl_ign_slot_table": 0x000D6348,
            "rl_ign_command_address": 0xFFFF2022,
            "rl_ign_publisher": 0x000D6540,
            "rl_ign_stock_consumer": 0x0002A892,
        },
        "speed_controller": {
            "rl_spd_speed_address": 0xFFFF113C,
            "rl_spd_extension_address": 0xFFFF6100,
            "rl_spd_unsigned_divide": 0x00021CE0,
            "rl_spd_control_publisher": 0x000D6500,
        },
        "feedback_arbiter": {
            "rl_feedback_base_wrapper": 0x000D35E0,
            "rl_feedback_selector_state": 0xFFFF5D00,
            "rl_feedback_state": 0xFFFF5D40,
            "rl_feedback_status_byte": 0xFFFF3ADA,
        },
        "spark_cut": {
            "rl_cut_state_address": 0xFFFF5D40,
            "rl_cut_sync_address": 0xFFFF8501,
            "rl_cut_apc_mode_address": 0xFFFF24C9,
            "rl_cut_output_state_address": 0xFFFF84EA,
            "rl_cut_port_state_address": 0xFFFF4185,
            "rl_cut_veto_address": 0xFFFF8511,
            "rl_cut_dwell_mask_address": 0xFFFF13D1,
            "rl_cut_extension_address": 0xFFFF6100,
            "rl_cut_stock_divider": 0x00021CE0,
        },
        "spark_events": {"rl_cut_misfire_latch_address": 0xFFFF436F},
        "rpm": {
            "rl_rpm_input_address": 0xFFFF11BC,
            "rl_rpm_extension_address": 0xFFFF6100,
            "rl_rpm_control_publisher": 0x000D6500,
            "rl_rpm_unsigned_divide": 0x00021CE0,
        },
        "actuation": {
            "rl_act_extension_address": 0xFFFF6100,
            "rl_act_state_address": 0xFFFF5D40,
            "rl_act_efficiency_address": 0x000D6390,
            "rl_act_unsigned_divide": 0x00021CE0,
            "rl_act_state_check": 0x000D7000,
            "rl_act_views": 0x000D7190,
            "rl_act_apc_mode_address": 0xFFFF24C9,
        },
        "slot_validator": {
            "rl_val_config_address": 0x000D6320,
            "rl_val_efficiency_address": 0x000D6390,
        },
        "state_check": {
            "rl_sc_state_address": 0xFFFF5D40,
            "rl_sc_extension_address": 0xFFFF6100,
            "rl_sc_byte_limits": 0x000D71EA,
            "rl_sc_q_entry": 0x000D661A,
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
        # Only the spark wrapper restores r0 in the delay slot of its tail.
        common._validate_delay_slots(
            parsed, allow_tail_restore=unit.key == "spark_cut"
        )
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
        if any(0xD6220 <= value < 0xD6268 for value in actual_literals.values()):
            raise ValueError(f"{unit.key}: literal reads the retired schema-5 configuration")
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
        elif unit.key in {"spark_cut", "spark_events"}:
            _validate_spark_cut_abi(parsed)
        elif unit.key == "rpm":
            _validate_rpm_abi(parsed)
        elif unit.key == "actuation":
            _validate_actuation_abi(parsed)
        elif unit.key == "slot_validator":
            _validate_slot_validator_abi(parsed)
        elif unit.key == "state_check":
            _validate_state_check_abi(parsed)
        else:
            raise ValueError(f"{unit.key}: no ABI validator is registered")
    _validate_internal_entries(parsed_by_unit)
    if {"engine", "speed_controller", "rpm", "actuation"} <= set(parsed_by_unit):
        _validate_publication_atomicity(parsed_by_unit)
    # Register conventions, live registers across calls, and the producers
    # of every consumed T, over the functions of all units.
    flow_model.validate_flow(
        parsed_by_unit,
        [SOURCE_LABELS[key] for key in layout.code_region_by_key],
    )
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
            allow_tail_restore=unit.key == "spark_cut",
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
