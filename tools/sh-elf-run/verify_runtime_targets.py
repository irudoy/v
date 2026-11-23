#!/usr/bin/env python3
"""Execute every relocated runtime target with GNU SH-2E tools."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import sys
import tempfile


TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
for item in (TOOL_DIR, ROOT):
    if str(item) not in sys.path:
        sys.path.insert(0, str(item))

import verify_can_telemetry as can_verifier
import verify_map_switching as base_verifier
from elf_storage_layout import ELFStorageError, require_separate_storage

from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import map_switching_assembly
from patches import map_switching_compose
from patches import runtime_targets
from tools.mapkit import vq37_native_fuel_cut


# Harness target define and exact PASS marker of every VQ37 map variant.
VQ37_MAP_HARNESS_BY_VARIANT = {
    "sh7059-1nd": (
        "TARGET_1ND",
        "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=197 selector=18 "
        "adapters=136 limiter=14 native_fuel=20 feedback=9 "
        "feedback_invocations=17 entries=14",
    ),
    "sh7059-1me3b": (
        "TARGET_1ME3B",
        "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=195 selector=18 "
        "adapters=134 limiter=14 native_fuel=20 feedback=9 "
        "feedback_invocations=17 entries=14",
    ),
    "sh7059-1ek7a": (
        "TARGET_1EK7A",
        "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=195 selector=18 "
        "adapters=134 limiter=14 native_fuel=20 feedback=9 "
        "feedback_invocations=17 entries=14",
    ),
    "sh7058-jk78": (
        "TARGET_JK78",
        "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=168 selector=18 "
        "adapters=107 limiter=14 native_fuel=20 feedback=9 "
        "feedback_invocations=17 entries=13",
    ),
}
# The map harness names the four SH7059 state-code ignition bases by
# placeholders that no canonical address uses.
IGNITION_STATE_HARNESS_BASES = {
    "ignition_surface_state_3": 0x0000F610,
    "ignition_surface_state_4": 0x0000F710,
    "ignition_surface_state_5": 0x0000F690,
    "ignition_surface_state_6_7": 0x0000F6D0,
}
MEASURED_CAN_ROMS = ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B", "1ME3B", "1EK7A")
MEASURED_MAP_ROMS = ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B", "1EK7A")
RETURN_STUB = bytes.fromhex("000b0009")
RETURN_ONE_STUB = bytes.fromhex("e001000b0009")
RTE_STUB = bytes.fromhex("002b0009")
FEEDBACK_SERIALIZER_PREFIX = bytes.fromhex(
    "d103e0b52100000b000900090009"
)


class VerificationError(RuntimeError):
    """Raised when a relocated target violates its executable contract."""


def _first_difference(actual, expected):
    for index, pair in enumerate(zip(actual, expected)):
        if pair[0] != pair[1]:
            return index
    return min(len(actual), len(expected))


def _feedback_serializer_stub(address, status_alias):
    """Build an aligned simulator-only status-byte serializer stub."""
    literal_address = ((address + 4) & ~3) + 12
    padding_size = literal_address - (
        address + len(FEEDBACK_SERIALIZER_PREFIX)
    )
    if padding_size not in {0, 2}:
        raise VerificationError(
            f"serializer stub cannot align its literal at {address:#x}"
        )
    return (
        FEEDBACK_SERIALIZER_PREFIX
        + bytes.fromhex("0009") * (padding_size // 2)
        + status_alias.to_bytes(4, "big")
    )


def _assemble_stage(
    label,
    layout,
    parsed_by_unit,
    tracked,
    build_dir,
    verbose,
):
    """Assemble rendered target sources and require tracked byte identity."""
    expected_keys = {unit.key for unit in layout.assembly_units}
    if set(tracked) != expected_keys:
        raise VerificationError(
            f"{label}: tracked unit set differs; "
            f"actual={sorted(tracked)} expected={sorted(expected_keys)}"
        )
    source_texts = layout.source_text_by_unit
    assembled = {}
    for unit in layout.assembly_units:
        blob = base_verifier.assemble_unit(
            unit,
            parsed_by_unit[unit.key],
            build_dir,
            source_text=source_texts[unit.key],
        )
        expected = tracked[unit.key]
        if blob != expected:
            difference = _first_difference(blob, expected)
            raise VerificationError(
                f"{label}.{unit.key}: GNU output differs from the tracked "
                f"payload at ROM address {unit.span.start + difference:#x}"
            )
        digest = hashlib.sha256(blob).hexdigest()
        if digest != unit.expected_sha256:
            raise VerificationError(
                f"{label}.{unit.key}: GNU SHA-256 is {digest}, expected "
                f"{unit.expected_sha256}"
            )
        if verbose:
            print(
                f"GNU_ASSEMBLY runtime_target={layout.rom} stage={label} "
                f"unit={unit.key} bytes={len(blob)} sha256={digest}"
            )
        assembled[unit.key] = blob
    return assembled


def _compose_and_lock(target, locks, map_blobs, can_blobs):
    """Compose the exact target stages from independently assembled bytes.

    A relocated target carries no Rolling Launch stage, so its lock repeats
    the map stage digest and telemetry composes on the map stage.
    """
    map_result = map_switching_compose.compose(
        layout=target.map_layout,
        image=target.stock_image,
        blobs=map_blobs,
    )
    can_result = can_telemetry_compose.compose(
        layout=target.telemetry_layout,
        base=map_result.data,
        blobs=can_blobs,
    )
    actual = (map_result.sha256, map_result.sha256, can_result.sha256)
    expected = (
        locks.map_stage_sha256,
        locks.rolling_stage_sha256,
        locks.telemetry_stage_sha256,
    )
    if actual != expected:
        raise VerificationError(
            f"{target.rom}: independently assembled composition differs; "
            f"actual={actual} expected={expected}"
        )
    return map_result, can_result


def _install_stock_stubs(fixture, target):
    """Install only target-specific unchanged stock-call simulator stubs."""
    profiles = runtime_targets.rom_address_profiles
    map_hooks = {hook.key: hook for hook in target.map_layout.hooks}
    can_hooks = target.telemetry_layout.hook_by_key
    if target.map_layout.variant in runtime_targets.VQ37_MAP_VARIANTS:
        map_keys = {
            "selector_host_call",
            "startup_initializer",
            "overrun_cut_lookup",
            "overrun_restore_lookup",
            "fuel_compensation_lookup_startup",
            "fuel_compensation_lookup_runtime",
            "idle_ignition_lookup_pool_1",
            "idle_ignition_lookup_pool_2",
        }
        map_keys.update(
            key
            for key in profiles.MAP_HOOK_KEYS_BY_VARIANT[
                target.map_layout.variant
            ]
            if key.startswith("ignition_lookup_")
        )
        if target.map_layout.variant in profiles.IGNITION_STATE_MAP_VARIANTS:
            map_keys.add("ignition_state_lookup")
    else:
        map_keys = {
            "selector_host_call",
            "startup_initializer",
            "overrun_cut_lookup",
            "overrun_restore_lookup",
            "ignition_lookup_knock",
            "ignition_lookup_primary_a",
            "ignition_lookup_primary_b",
            "fuel_compensation_lookup_startup",
            "fuel_compensation_lookup_runtime",
            "intake_cvtc_target_lookup",
            "exhaust_cvtc_target_lookup",
            "idle_ignition_lookup",
        }
    missing = map_keys - map_hooks.keys()
    if missing:
        raise VerificationError(
            f"{target.rom}: map layout lacks stock hooks {sorted(missing)}"
        )
    stubs = {
        map_hooks[key].stock: RETURN_STUB
        for key in map_keys
    }
    stubs.update({
        can_hooks["coherent_snapshot_call"].stock: RETURN_STUB,
        can_hooks["knock_interval_latch"].stock: RETURN_STUB,
    })
    for key in ("hcan1_primary_init", "hcan1_recovery_init"):
        stubs[can_hooks[key].stock] = RETURN_ONE_STUB
    evaluator = can_hooks["knock_margin_latch"].stock
    stubs[evaluator] = can_verifier.knock_evaluator_stub(evaluator)

    serializer = map_hooks["cruise_feedback_serializer"].stock
    status_alias = base_verifier.alias_high_ram(
        target.map_layout.feedback.status_byte_address
    )
    stubs[serializer] = _feedback_serializer_stub(serializer, status_alias)
    stock_isr = can_hooks["hcan1_sle1_vector"].stock
    stubs[stock_isr] = RTE_STUB

    for address, stub in stubs.items():
        end = address + len(stub)
        if address < 0 or end > len(fixture):
            raise VerificationError(
                f"{target.rom}: stock stub is outside ROM at {address:#x}"
            )
        fixture[address:end] = stub
    return len(stubs)


def _build_dynamic_fixture(
    target,
    composition,
    map_parsed,
    can_parsed,
):
    """Apply simulator-only transforms after exact target identity passes."""
    fixture = bytearray(composition.data)
    map_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, map_parsed
    )
    if target.map_layout.variant in runtime_targets.VQ37_MAP_VARIANTS:
        native = vq37_native_fuel_cut.load_registry()[target.rom]
        for binding in (
            native.pointer_bindings + native.ram_pointer_bindings
        ):
            actual = int.from_bytes(
                fixture[binding.site : binding.site + 4], "big"
            )
            if actual < base_verifier.HIGH_RAM_BASE:
                raise VerificationError(
                    f"{target.rom}: native fuel-cut pointer at "
                    f"{binding.site:#x} is not bound to high RAM: "
                    f"{actual:#x}"
                )
            fixture[binding.site : binding.site + 4] = (
                base_verifier.alias_high_ram(actual).to_bytes(4, "big")
            )
            map_relocated += 1
    can_relocated = can_verifier.relocate_telemetry_ram_literals(
        fixture, can_parsed
    )
    differentiated = base_verifier.differentiate_map_copies(
        fixture, target.map_layout
    )
    stubs = _install_stock_stubs(fixture, target)
    fixture[
        can_verifier.TRAPA_VECTOR_ADDRESS:
        can_verifier.TRAPA_VECTOR_ADDRESS + 4
    ] = target.telemetry_layout.code_region_by_key[
        "sle1_isr"
    ].entry.to_bytes(4, "big")
    return (
        bytes(fixture),
        map_relocated,
        can_relocated,
        differentiated,
        stubs,
    )


def _build_rom_object(rom, fixture, build_dir):
    fixture_path = build_dir / f"{rom.lower()}.sim-fixture"
    object_path = build_dir / f"{rom.lower()}-rom.o"
    fixture_path.write_bytes(fixture)
    base_verifier.run_command([
        base_verifier.OBJCOPY,
        "-I", "binary",
        "-O", "elf32-sh",
        "-B", "sh",
        "--rename-section",
        ".data=.rom,alloc,load,code,data,contents",
        fixture_path,
        object_path,
    ])
    return object_path


def _render_harness(target, name, build_dir):
    source = (TOOL_DIR / name).read_text(encoding="utf-8")
    overrides = None
    if (
        name == "map_switching_harness.c"
        and target.map_layout.variant == "dual-cvtc"
    ):
        odd = target.map_layout.family_by_key[
            "exhaust_cvtc_target"
        ].canonical_address
        overrides = {0x0000B43A: odd, 0x0000B43B: odd + 1}
    elif (
        name == "map_switching_harness.c"
        and target.map_layout.variant in runtime_targets.VQ37_MAP_VARIANTS
    ):
        families = target.map_layout.family_by_key
        native = vq37_native_fuel_cut.load_registry()[target.rom]
        source = (
            f"#define NATIVE_ACTIVE_MASK {native.state_active_mask:#04x}U\n"
            f"#define NATIVE_ARMED_MASK {native.state_armed_mask:#04x}U\n"
            + source
        )
        symbols = runtime_targets.rom_address_profiles.profile_for_rom(
            target.rom
        ).map_symbol_by_key
        overrides = {
            0x00009040: families[
                "rev_limit_fuel_cut_caps"
            ].canonical_address,
            0x00016BF4: families[
                "rev_limit_fuel_cut_curves"
            ].canonical_address,
            0x0006AEB8: native.function_address,
            0xFFFF10E5: native.selector_address,
            0xFFFF11AC: native.rpm_address,
            0xFFFF23F5: native.state_address,
            0xFFFF2449: native.delay_address,
        }
        profiles = runtime_targets.rom_address_profiles
        if target.map_layout.variant in profiles.GATED_IGNITION_MAP_VARIANTS:
            overrides.update({
                0x0000991A: symbols["ignition_gated_surface_1"],
                0x0000E91A: symbols["ignition_gated_surface_2"],
                0x0000EA1A: symbols["ignition_gated_surface_3"],
            })
        if target.map_layout.variant in profiles.IGNITION_STATE_MAP_VARIANTS:
            for key, placeholder in IGNITION_STATE_HARNESS_BASES.items():
                overrides[placeholder] = families[key].canonical_address
            unknown = IGNITION_STATE_HARNESS_BASES["ignition_surface_state_3"]
            overrides[unknown + 1] = (
                families["ignition_surface_state_3"].canonical_address + 1
            )
    elif name == "can_telemetry_harness.c":
        overrides = runtime_targets.can_dynamic_window_overrides(
            runtime_targets.rom_address_profiles.profile_for_rom(target.rom)
        )
    rendered = runtime_targets.render_target_text(
        target.rom, source, overrides
    )
    path = build_dir / f"{target.rom.lower()}-{name}"
    path.write_text(rendered, encoding="utf-8")
    return path


def _build_invoke_objects(build_dir):
    invoke = build_dir / "invoke.o"
    exception = build_dir / "invoke-exception.o"
    base_verifier.run_command([
        base_verifier.AS,
        "--big", "--isa=sh2e",
        "-o", invoke,
        TOOL_DIR / "invoke.s",
    ])
    base_verifier.run_command([
        base_verifier.AS,
        "--big", "--isa=sh2e",
        "-o", exception,
        TOOL_DIR / "invoke_exception.s",
    ])
    return invoke, exception


def _can_omissions(layout, parsed, fixture):
    """Shared harness edits that each remove one measured telemetry outcome."""
    control = parsed["control"]
    config_entry = control.labels["telemetry_control_config_valid"]
    magic = next(
        row for row in control.statements
        if row.kind == "instruction" and row.address >= config_entry
        and map_switching_assembly._mnemonic(row) == "bf"
    )
    magic_word = int.from_bytes(fixture[magic.address:magic.address + 2], "big")
    magic_target = map_switching_assembly._validate_direct_branch_encoding(
        control, magic, magic_word
    )
    capture = parsed["capture"]
    measured_capture = can_verifier._measured_statements("capture", capture, layout)
    zero = next(
        row for row in measured_capture
        if row.kind == "instruction" and row.text == "bt telemetry_margin_return"
        and capture.statement_by_address[row.address - 2].text == "tst r4,r4"
    )
    zero_word = int.from_bytes(fixture[zero.address:zero.address + 2], "big")
    zero_target = map_switching_assembly._validate_direct_branch_encoding(
        capture, zero, zero_word
    )
    clamp = next(
        row for row in measured_capture
        if row.kind == "instruction" and row.text == "bf telemetry_build_context_valid"
    )
    capture_fail = min(
        (row for row in measured_capture
         if row.kind == "instruction" and row.text == "bf telemetry_capture_return"),
        key=lambda row: row.address,
    )
    capture_word = int.from_bytes(fixture[capture_fail.address:capture_fail.address + 2], "big")
    capture_target = map_switching_assembly._validate_direct_branch_encoding(
        capture, capture_fail, capture_word
    )
    completion = parsed["completion"]
    measured_completion = can_verifier._measured_statements("completion", completion, layout)
    idle_ack = next(
        row for row in measured_completion
        if row.kind == "instruction" and row.text == "bt telemetry_completion_busy_valid"
    )
    request_entry = layout.code_region_by_key["request_page"].entry
    request_copy = (
        "{{\n        size_t index;\n        for (index = 0; index < 8; ++index)\n"
        "            ram_pointer(MAILBOX_DATA)[index] = ram_pointer({bank})[{offset} + index];\n    }}"
    )
    isr_standin = (
        "{\n        size_t index;\n        for (index = 0; index < 8; ++index)\n"
        "            registers[index] = (uint32_t)index + 1U;\n"
        "        if (((txack | aback) & MAILBOX26_MASK) != 0)\n"
        "            write_u16(ram_pointer(IRR1), 0x0100);\n    }"
    )
    def one(name, old, new, reason):
        return name, ((old, new),), reason

    return (
        one("main",
            "(void)invoke_r4(MAIN_WRAPPER, 0);",
            "(void)invoke_r4(CONTROL_POLL, 0);\n    (void)invoke_r4(CAPTURE, 0);",
            f"uncovered CAN wrapper entry {layout.code_region_by_key['main_wrapper'].entry:#010x}"),
        one("config-magic",
            "mutate_configuration(mutation);\n    (void)invoke_r4(CONTROL_POLL, 0);",
            "mutate_configuration(mutation);\n    if (mutation != CONFIG_MAGIC)\n"
            "        (void)invoke_r4(CONTROL_POLL, 0);",
            f"uncovered CAN wrapper outcome {magic.address:#010x}->{magic_target:#010x}"),
        one("margin-zero",
            "(void)invoke_r4(KNOCK_MARGIN_WRAPPER, 0);",
            "(void)invoke_r4((selector == 0 && primary == 0 && channel == 0) ? "
            f"{layout.hook_by_key['knock_margin_latch'].stock:#010x}U : KNOCK_MARGIN_WRAPPER, 0);",
            f"uncovered CAN wrapper outcome {zero.address:#010x}->{zero_target:#010x}"),
        ("request-page", (
            ("(void)invoke_r4(REQUEST_PAGE, 0);\n    if (!expect_bytes(\n            \"request-a\"",
             request_copy.format(bank="BANK_A", offset=80)
             + "\n    if (!expect_bytes(\n            \"request-a\""),
            ("(void)invoke_r4(REQUEST_PAGE, 0);\n    if (!expect_bytes(\n            \"request-b\"",
             request_copy.format(bank="BANK_B", offset=32)
             + "\n    if (!expect_bytes(\n            \"request-b\""),
        ), f"uncovered CAN request invoke return {request_entry:#010x}"),
        one("build-clamp",
            "    state[6] = 0xFF;\n",
            "    state[6] = 0;\n",
            f"uncovered CAN wrapper outcome {clamp.address:#010x}->{clamp.address + 2:#010x}"),
        one("capture-magic",
            "        mutate_configuration(mutation);\n        (void)invoke_r4(CAPTURE, 0);",
            "        mutate_configuration(mutation);\n"
            "        if (mutation != CONFIG_MAGIC)\n"
            "            (void)invoke_r4(CAPTURE, 0);",
            f"uncovered CAN wrapper outcome {capture_fail.address:#010x}->{capture_target:#010x}"),
        one("ack-idle",
            "    state[3] = 4;\n    signal_ack(MAILBOX26_MASK);\n"
            "    (void)invoke_r4(COMPLETION, 0);\n",
            "    state[3] = 4;\n    signal_ack(MAILBOX26_MASK);\n",
            f"uncovered CAN wrapper outcome {idle_ack.address:#010x}->{idle_ack.address + 2:#010x}"),
        one("sle1-entry",
            "    invoke_exception_probe(registers);",
            "    " + isr_standin,
            f"uncovered CAN wrapper entry {layout.code_region_by_key['sle1_isr'].entry:#010x}"),
    )


def _measure_can_telemetry(
    target, source, command, invoke, elf, fixture, composed, parsed, build_dir, marker,
):
    """Trace one relocated telemetry harness and require its measured regions."""
    rom = target.rom
    layout = target.telemetry_layout
    can_verifier.require_wrapper_instruction_bytes(fixture, composed, parsed, layout)
    snapshot = source.read_text(encoding="utf-8")

    def execute(path):
        try:
            ranges, invokes = base_verifier._invoke_trace_bindings(
                path, invoke, fixture, build_dir
            )
            trace = build_dir / f"{path.stem}.pc-trace"
            environment = {
                **os.environ,
                "VQ_SH_PC_TRACE_FILE": str(trace),
                "VQ_SH_PC_TRACE_FORMAT": "v1",
                "VQ_SH_PC_TRACE_RANGES": ",".join(
                    f"{begin:x}:{end:x}" for begin, end in ((0, len(fixture)), *ranges)
                ),
            }
            before = path.read_bytes()
            result = base_verifier.run_command(
                [base_verifier.RUN, f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k", path],
                timeout=180, env=environment,
            )
            if path.read_bytes() != before:
                raise VerificationError(f"{rom} telemetry ELF changes during execution")
            records = base_verifier.read_pc_trace(trace)
        except base_verifier.VerificationError as error:
            raise VerificationError(f"{rom} telemetry execution binding: {error}") from error
        return result, records, invokes

    def coverage(records, invokes):
        try:
            return can_verifier.require_wrapper_coverage(
                records, fixture, layout, parsed, invokes
            )
        except can_verifier.VerificationError as error:
            raise VerificationError(f"{rom} telemetry coverage: {error}") from error

    result, records, invokes = execute(elf)
    covered = coverage(records, invokes)
    if marker not in result.stdout:
        detail = result.stdout.rstrip()
        raise VerificationError(
            f"{rom} telemetry lacks its semantic PASS marker"
            + (f"\n{detail}" if detail else "")
        )
    negatives = []
    for name, edits, reason in _can_omissions(layout, parsed, fixture):
        text = snapshot
        for old, new in edits:
            if text.count(old) != 1:
                raise VerificationError(f"{rom} telemetry negative lacks its unique {name} edit")
            text = text.replace(old, new, 1)
        negative_source = build_dir / f"{rom.lower()}-can-no-{name}.c"
        negative_source.write_text(text, encoding="utf-8")
        negative_elf = build_dir / f"{rom.lower()}-can-no-{name}.elf"
        negative_command = list(command)
        negative_command[negative_command.index("-o") + 1] = negative_elf
        negative_command[negative_command.index(source)] = negative_source
        base_verifier.run_command(negative_command, timeout=120)
        try:
            require_separate_storage(negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
        except (ELFStorageError, OSError) as error:
            raise VerificationError(
                f"{rom} telemetry negative ELF storage separation: {error}"
            ) from error
        negative, records, invokes = execute(negative_elf)
        if marker not in negative.stdout:
            detail = negative.stdout.rstrip()
            raise VerificationError(
                f"{rom} telemetry negative loses its semantic PASS marker"
                + (f"\n{detail}" if detail else "")
            )
        try:
            coverage(records, invokes)
        except VerificationError as error:
            if str(error) != f"{rom} telemetry coverage: {reason}":
                raise VerificationError(
                    f"{rom} telemetry negative fails outside its omitted outcome: {error}"
                ) from error
        else:
            raise VerificationError(f"{rom} telemetry coverage accepts the omitted {name} case")
        if negative_source.read_text(encoding="utf-8") != text:
            raise VerificationError(f"{rom} telemetry negative source changes during execution")
        negatives.append(
            f"VQ_SH_ELF_RUNTIME_CAN_NEGATIVE status=PASS rom={rom} "
            f"omitted={name} {reason}"
        )
    if source.read_text(encoding="utf-8") != snapshot:
        raise VerificationError(f"{rom} rendered telemetry source changes during execution")
    scope = ",".join((
        "wrappers", "control",
        *can_verifier.CAPTURE_MEASURED_REGIONS,
        *can_verifier.COMPLETION_MEASURED_REGIONS,
    ))
    report = (
        f"VQ_SH_ELF_RUNTIME_CAN_COVERAGE status=PASS rom={rom} scope={scope} "
        + " ".join(f"{key}={value}" for key, value in covered.items())
    )
    return "\n".join((result.stdout.strip(), report, *negatives))


def _compile_and_run(
    target,
    name,
    source,
    rom_object,
    objects,
    build_dir,
    marker,
    defines=(),
    *,
    map_parsed=None,
    can_parsed=None,
    fixture=None,
    composed_image=None,
):
    measured = target.rom in MEASURED_MAP_ROMS and name == "map-switching"
    source_snapshot = None
    if measured:
        if map_parsed is None or fixture is None or composed_image is None:
            raise VerificationError(f"{target.rom} map coverage requires typed/composed/fixture context")
        if len(fixture) != len(target.stock_image.data):
            raise VerificationError(f"{target.rom} map fixture extent differs from the owned image")
        try:
            base_verifier.require_map_fixture_bindings(
                fixture, composed_image, map_parsed, target.map_layout)
        except base_verifier.VerificationError as error:
            raise VerificationError(f"{target.rom} map binding: {error}") from error
        source_snapshot = source.read_text(encoding="utf-8")
    output = build_dir / f"{target.rom.lower()}-{name}.elf"
    driver_text_base = max(
        base_verifier.DRIVER_TEXT_BASE,
        len(target.stock_image.data) + 0x10000,
    )
    command = [
        base_verifier.GCC,
        "-m2e", "-mb", "-std=c11", "-O2",
        "-Wall", "-Wextra", "-Werror",
        "-I", can_verifier.HARNESS_INCLUDE_DIR,
    ]
    command.extend(f"-D{define}=1" for define in defines)
    command.extend([
        f"-Wl,-Ttext-segment={driver_text_base:#x}",
        "-Wl,--section-start=.rom=0",
        "-o", output,
        source,
        *objects,
        rom_object,
    ])
    base_verifier.run_command(command, timeout=120)
    try:
        require_separate_storage(output, ((base_verifier.TEST_RAM_BASE, 65536),))
    except (ELFStorageError, OSError) as error:
        raise VerificationError(f"{target.rom}.{name}: ELF storage separation: {error}") from error
    if name == "can-telemetry" and target.rom in MEASURED_CAN_ROMS:
        if can_parsed is None or fixture is None or composed_image is None:
            raise VerificationError(
                f"{target.rom} telemetry coverage requires typed/composed/fixture context"
            )
        return _measure_can_telemetry(
            target, source, command, objects[0], output, fixture, composed_image,
            can_parsed, build_dir, marker,
        )
    if not measured:
        result = base_verifier.run_command(
            [base_verifier.RUN, f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k", output],
            timeout=180,
        )
        if marker not in result.stdout:
            raise VerificationError(
                f"{target.rom}.{name}: zero exit without exact PASS marker"
                + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
            )
        return result.stdout.strip()

    def execute(elf):
        try:
            base_verifier.require_map_fixture_bindings(
                fixture, composed_image, map_parsed, target.map_layout)
            ranges, invokes = base_verifier._invoke_trace_bindings(elf, objects[0], fixture, build_dir)
            trace = build_dir / f"{elf.stem}.pc-trace"
            environment = {
                **os.environ,
                "VQ_SH_PC_TRACE_FILE": str(trace),
                "VQ_SH_PC_TRACE_FORMAT": "v1",
                "VQ_SH_PC_TRACE_RANGES": ",".join(
                    f"{begin:x}:{end:x}" for begin, end in ((0, len(fixture)), *ranges)),
            }
            before = elf.read_bytes()
            result = base_verifier.run_command(
                [base_verifier.RUN, f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k", elf],
                timeout=180, env=environment)
            if elf.read_bytes() != before:
                raise VerificationError(f"{target.rom} map ELF changes during execution")
            records = base_verifier.read_pc_trace(trace)
        except base_verifier.VerificationError as error:
            raise VerificationError(f"{target.rom} map execution binding: {error}") from error
        return result, records, invokes

    def coverage(records, invokes):
        return base_verifier.require_payload_coverage(
            records, fixture, map_parsed, invokes, composed_image=composed_image,
            adapter_layout=target.map_layout)

    result, records, invokes = execute(output)
    try:
        covered = coverage(records, invokes)
    except base_verifier.VerificationError as error:
        raise VerificationError(f"{target.rom} map coverage: {error}") from error
    if marker not in result.stdout:
        raise VerificationError(f"{target.rom} map lacks its semantic PASS marker")
    layout = target.map_layout
    def entry(key):
        return min(layout.code_region_by_key[region].entry
                   for region in layout.assembly_unit_by_key[key].code_regions)
    adapter_entries = [entry(key) for key in base_verifier._adapter_coverage_units(layout)]
    omissions = (
        ("limiter", "if (!run_limiter_cases())", entry("startup_wrapper")),
        ("adapters", "if (!run_adapter_cases())", min(adapter_entries)),
        ("selector", "if (!run_selector_cases())", entry("selector_host")),
        ("feedback", "if (!run_feedback_cases(&feedback_invocations))", entry("cruise_feedback_wrapper")),
    )
    negatives = []
    for omitted, call, expected_entry in omissions:
        if source_snapshot.count(call) != 1:
            raise VerificationError(f"{target.rom} negative lacks its unique {omitted} call")
        negative_source = build_dir / f"{target.rom.lower()}-no-{omitted}-cases.c"
        negative_text = source_snapshot.replace(call, call.replace("if (", "if (0 && ", 1))
        negative_source.write_text(negative_text, encoding="utf-8")
        negative_elf = build_dir / f"{target.rom.lower()}-no-{omitted}-cases.elf"
        negative_command = list(command)
        negative_command[negative_command.index("-o") + 1] = negative_elf
        negative_command[negative_command.index(source)] = negative_source
        base_verifier.run_command(negative_command, timeout=120)
        try:
            require_separate_storage(negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
        except (ELFStorageError, OSError) as error:
            raise VerificationError(f"{target.rom} negative ELF storage separation: {error}") from error
        negative, records, invokes = execute(negative_elf)
        if marker not in negative.stdout:
            raise VerificationError(f"{target.rom} negative loses its semantic PASS marker")
        expected_reason = f"uncovered entry {expected_entry:#010x}"
        try:
            coverage(records, invokes)
        except base_verifier.VerificationError as error:
            if str(error) != expected_reason:
                raise VerificationError(f"{target.rom} negative fails outside its omitted entry: {error}") from error
        else:
            raise VerificationError(f"{target.rom} coverage accepts the omitted {omitted} cases")
        if negative_source.read_text(encoding="utf-8") != negative_text:
            raise VerificationError(f"{target.rom} negative source changes during execution")
        negatives.append(f"VQ_SH_ELF_RUNTIME_MAP_NEGATIVE status=PASS rom={target.rom} omitted={omitted} {expected_reason}")
    if source.read_text(encoding="utf-8") != source_snapshot:
        raise VerificationError(f"{target.rom} rendered source changes during execution")
    scope = ",".join(layout.assembly_unit_by_key)
    report = f"VQ_SH_ELF_RUNTIME_MAP_COVERAGE status=PASS rom={target.rom} scope={scope} "
    report += " ".join(f"{key}={value}" for key, value in covered.items())
    return "\n".join((result.stdout.strip(), report, *negatives))


def _run_harnesses(target, fixture, build_dir, *, map_parsed, composed_image, can_parsed=None):
    rom_object = _build_rom_object(target.rom, fixture, build_dir)
    invoke, exception = _build_invoke_objects(build_dir)
    map_source = _render_harness(
        target, "map_switching_harness.c", build_dir
    )
    can_source = _render_harness(
        target, "can_telemetry_harness.c", build_dir
    )
    if target.map_layout.variant == "dual-cvtc":
        map_marker = (
            "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=140 selector=18 "
            "adapters=99 limiter=14 feedback=9 feedback_invocations=17 "
            "entries=13"
        )
        map_defines = ("TARGET_DUAL_CVTC",)
    elif target.map_layout.variant in VQ37_MAP_HARNESS_BY_VARIANT:
        map_define, map_marker = VQ37_MAP_HARNESS_BY_VARIANT[
            target.map_layout.variant
        ]
        map_defines = ("TARGET_VQ37", map_define)
    else:
        raise VerificationError(
            f"{target.rom}: unsupported map harness variant "
            f"{target.map_layout.variant!r}"
        )

    if target.rom in MEASURED_MAP_ROMS:
        map_marker = "VQ_SH_ELF_MAP_SWITCHING status=PASS "
        map_defines += ("VERIFY_SELECTOR_FEEDBACK_GUARDS",)

    markers = [
        _compile_and_run(
            target,
            "map-switching",
            map_source,
            rom_object,
            (invoke,),
            build_dir,
            map_marker,
            defines=map_defines,
            map_parsed=map_parsed, fixture=fixture, composed_image=composed_image,
        )
    ]
    if (target.rom in MEASURED_MAP_ROMS
            and f"VQ_SH_ELF_RUNTIME_MAP_COVERAGE status=PASS rom={target.rom} " not in markers[0]):
        raise VerificationError(f"{target.rom} map lacks its measured coverage terminal")
    can_defines = (
        ("TELEMETRY_TAIL_CHAIN",)
        if target.telemetry_layout.variant.endswith("-tail-chain")
        else ()
    ) + (
        (VQ37_MAP_HARNESS_BY_VARIANT[target.map_layout.variant][0],)
        if target.map_layout.variant in VQ37_MAP_HARNESS_BY_VARIANT
        else ()
    )
    can_output = _compile_and_run(
        target,
        "can-telemetry",
        can_source,
        rom_object,
        (invoke, exception),
        build_dir,
        "VQ_SH_ELF_CAN_TELEMETRY status=PASS "
        f"cases={150 if target.rom == '1ME3B' else 160 if target.rom in MEASURED_CAN_ROMS else 129} entries=13 "
        "profiles=1 contexts=10 isr_rte=5",
        defines=can_defines + (
            ("MEASURE_CAN_TELEMETRY",) if target.rom in MEASURED_CAN_ROMS else ()
        ),
        can_parsed=can_parsed,
        fixture=fixture,
        composed_image=composed_image,
    )
    markers.append(can_output)
    if (
        target.rom in MEASURED_CAN_ROMS
        and f"VQ_SH_ELF_RUNTIME_CAN_COVERAGE status=PASS rom={target.rom} " not in can_output
    ):
        raise VerificationError(f"{target.rom} telemetry lacks its measured coverage terminal")
    return tuple(markers)


def verify_target(rom, locks, verbose=False):
    target = runtime_targets.load_runtime_target(rom)
    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    can_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    with tempfile.TemporaryDirectory(
        prefix=f"vq-sh-elf-{rom.lower()}-"
    ) as directory:
        build_dir = Path(directory)
        map_blobs = _assemble_stage(
            "map", target.map_layout, map_parsed,
            target.map_payloads, build_dir, verbose,
        )
        can_blobs = _assemble_stage(
            "telemetry", target.telemetry_layout, can_parsed,
            target.telemetry_payloads, build_dir, verbose,
        )
        map_audit = map_switching_assembly.validate_instruction_semantics(
            target.map_layout, map_parsed, map_blobs
        )
        can_audit = can_telemetry_assembly.validate_instruction_semantics(
            target.telemetry_layout, can_parsed, can_blobs
        )
        _, composition = _compose_and_lock(
            target, locks, map_blobs, can_blobs
        )
        (
            fixture,
            map_relocated,
            can_relocated,
            differentiated,
            stubs,
        ) = _build_dynamic_fixture(
            target,
            composition,
            map_parsed,
            can_parsed,
        )
        markers = _run_harnesses(target, fixture, build_dir,
                                 map_parsed=map_parsed,
                                 can_parsed=can_parsed, composed_image=composition.data)
        if rom in ("1ME3B", "1EK7A"):
            import verify_ignition_consumers
            markers = (*markers, verify_ignition_consumers.verify(
                target, fixture, build_dir
            ))
    for marker in markers:
        print(marker)
    instructions = map_audit.instructions + can_audit.instructions
    dynamic_cases = sum(
        can_verifier.marker_cases(marker) for marker in markers
    )
    print(
        f"VQ_SH_ELF_RUNTIME_TARGET status=PASS rom={rom} "
        f"family={target.family} instructions={instructions} "
        f"dynamic_cases={dynamic_cases} "
        f"map_ram_literals_relocated={map_relocated} "
        f"telemetry_ram_literals_relocated={can_relocated} "
        f"differentiated_bytes={differentiated} stock_stubs={stubs} "
        f"composition_sha256={composition.sha256}"
    )
    return {
        "rom": rom,
        "instructions": instructions,
        "dynamic_cases": dynamic_cases,
    }


def verify(verbose=False, roms=runtime_targets.RELOCATED_ROMS):
    locks = runtime_targets.load_payload_locks()
    results = [
        verify_target(rom, locks[rom], verbose=verbose)
        for rom in roms
    ]
    print(
        "VQ_SH_ELF_RUNTIME_TARGETS status=PASS "
        f"targets={len(results)} "
        f"instructions={sum(item['instructions'] for item in results)} "
        f"dynamic_cases={sum(item['dynamic_cases'] for item in results)}"
    )
    return results


if __name__ == "__main__":
    verify(verbose="--verbose" in sys.argv[1:])
