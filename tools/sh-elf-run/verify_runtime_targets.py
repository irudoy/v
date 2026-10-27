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
import verify_rolling_launch as rolling_verifier
from elf_storage_layout import ELFStorageError, require_separate_storage

from patches import can_telemetry_assembly
from patches import can_telemetry_compose
from patches import map_switching_assembly
from patches import map_switching_compose
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
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
MEASURED_ROLLING_ROMS = ("JK00C", "JK00D")
MEASURED_VQ37_ROLLING_ROMS = ("JK78C", "1ND0A", "1ND3B")
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


def _fuel_coordinator_stub(address, mask_alias):
    """Return a stock-first stub that publishes a distinct base mask.

    The stub writes the base mask to the aliased final-mask byte and
    returns the same value zero-extended in r0, matching the unsigned
    byte contract of the stock coordinator.
    """
    if address % 4:
        raise VerificationError(
            f"fuel coordinator stub is not aligned at {address:#x}"
        )
    return (
        bytes.fromhex("d102e080600c2100000b0009")
        + mask_alias.to_bytes(4, "big")
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


def _compose_and_lock(target, locks, map_blobs, rolling_blobs, can_blobs):
    """Compose the exact target stages from independently assembled bytes."""
    map_result = map_switching_compose.compose(
        layout=target.map_layout,
        image=target.stock_image,
        blobs=map_blobs,
    )
    rolling_result = (
        rolling_launch_compose.compose(
            layout=target.rolling_layout,
            base=map_result.data,
            blobs=rolling_blobs,
        )
        if target.rolling_layout is not None
        else None
    )
    can_result = can_telemetry_compose.compose(
        layout=target.telemetry_layout,
        base=(
            rolling_result.data
            if rolling_result is not None
            else map_result.data
        ),
        blobs=can_blobs,
    )
    actual = (
        map_result.sha256,
        (
            rolling_result.sha256
            if rolling_result is not None
            else map_result.sha256
        ),
        can_result.sha256,
    )
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
    return map_result, rolling_result, can_result


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
    if target.rolling_layout is not None:
        rolling_hooks = target.rolling_layout.hook_by_key
        stubs.update({
            rolling_hooks["displaced_periodic_task"].stock: RETURN_STUB,
            rolling_hooks["primary_ignition_command"].stock: RETURN_STUB,
        })
        if target.rolling_layout.variant == "vq37-fuel-coordinator":
            profile = runtime_targets.rom_address_profiles.profile_for_rom(
                target.rom
            )
            mask_alias = base_verifier.alias_high_ram(
                profile.rolling_symbol_by_key["fuel_inhibit_mask"]
            )
            coordinator = rolling_hooks["fuel_cut_coordinator"].stock
            stubs[coordinator] = _fuel_coordinator_stub(
                coordinator, mask_alias
            )
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
    rolling_parsed,
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
    rolling_relocated = (
        base_verifier.relocate_assembly_ram_literals(
            fixture, rolling_parsed
        )
        if rolling_parsed is not None
        else 0
    )
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
        rolling_relocated,
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
        name in {
            "map_switching_harness.c",
            "rolling_launch_harness.c",
        }
        and target.map_layout.variant in runtime_targets.VQ37_MAP_VARIANTS
    ):
        families = target.map_layout.family_by_key
        native = vq37_native_fuel_cut.load_registry()[target.rom]
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


def _rolling_serializer_stub(target):
    """Return the installed feedback serializer address and its stub bytes."""
    map_hooks = {hook.key: hook for hook in target.map_layout.hooks}
    serializer = map_hooks["cruise_feedback_serializer"].stock
    status_alias = base_verifier.alias_high_ram(
        target.map_layout.feedback.status_byte_address
    )
    return serializer, _feedback_serializer_stub(serializer, status_alias)


def _rolling_measured(rom):
    return rom in MEASURED_ROLLING_ROMS or rom in MEASURED_VQ37_ROLLING_ROMS


def _rolling_coverage_names(layout):
    """Regions and units measured for one layout, including a VQ37 fuel wrapper."""
    regions = list(rolling_verifier.COVERAGE_REGIONS)
    units = list(rolling_verifier.COVERAGE_UNITS)
    if "fuel_cut_wrapper" in layout.code_region_by_key:
        regions.append("fuel_cut_wrapper")
        units.append("fuel_cut_wrapper")
    return tuple(regions), tuple(units)


def _require_rolling_fixture_bytes(rom, fixture, composed, parsed_by_unit, units):
    """Bind measured Rolling Launch words to the composed image."""
    for unit in units:
        parsed = parsed_by_unit[unit]
        for row in parsed.statements:
            if row.kind != "instruction":
                continue
            if fixture[row.address:row.address + 2] != composed[row.address:row.address + 2]:
                raise VerificationError(
                    f"{rom} simulator changes rolling instruction at {row.address:#010x}"
                )
            if map_switching_assembly._mnemonic(row) not in {"jsr", "jmp"}:
                continue
            previous = parsed.statement_by_address[row.address - 2]
            literal = map_switching_assembly.PC_RELATIVE_RE.fullmatch(previous.text)
            if literal is None:
                raise VerificationError(f"{rom} rolling transfer lacks its source literal")
            pool = parsed.labels[literal.group("label")]
            if fixture[pool:pool + 4] != composed[pool:pool + 4]:
                raise VerificationError(f"{rom} simulator changes rolling control literal")


def _rolling_boundaries(target, regions):
    map_hooks = {hook.key: hook for hook in target.map_layout.hooks}
    rolling_hooks = target.rolling_layout.hook_by_key
    return {
        regions["periodic_wrapper"].entry: rolling_hooks["displaced_periodic_task"].stock,
        regions["selector_arbiter"].entry: map_hooks["selector_host_call"].stock,
        regions["startup_wrapper"].entry: map_hooks["startup_initializer"].stock,
    }


def _rolling_omissions(parsed, regions, fixture):
    """Name the shared harness edits that each remove one measured outcome."""
    periodic = regions["periodic_wrapper"].entry
    adapter = parsed["ignition_adapter"]
    phase = next(
        row for row in adapter.statements
        if row.kind == "instruction" and row.text == "bf rl_ign_tail"
        and adapter.statement_by_address[row.address - 2].text == "cmp/eq 0x1,r0"
    )
    phase_word = int.from_bytes(fixture[phase.address:phase.address + 2], "big")
    phase_target = map_switching_assembly._validate_direct_branch_encoding(
        adapter, phase, phase_word
    )
    engine = parsed["engine"]
    map_edge = next(
        row for row in engine.statements
        if row.kind == "instruction" and row.text == "bf rl_gate_selector"
        and engine.statement_by_address[row.address + 2].text == "mov #0x2,r0"
    )
    map_word = int.from_bytes(fixture[map_edge.address:map_edge.address + 2], "big")
    map_target = map_switching_assembly._validate_direct_branch_encoding(
        engine, map_edge, map_word
    )
    controller = parsed["ignition_controller"]
    zero_edges = [
        row for row in controller.statements
        if row.kind == "instruction" and row.text == "bt rl_ctrl_tail"
    ]
    if len(zero_edges) != 1:
        raise VerificationError("rolling controller zero-band outcome is not unique")
    zero_edge = zero_edges[0]
    zero_word = int.from_bytes(fixture[zero_edge.address:zero_edge.address + 2], "big")
    zero_target = map_switching_assembly._validate_direct_branch_encoding(
        controller, zero_edge, zero_word
    )
    zero_call = '    if (!invoke_ignition("ign-zero-band-start", 110, 308, 110))'
    idle_clear = (
        "        \"feedback-idle-clear-held\", PHASE_IDLE, REASON_NONE,\n"
        "        FLAG_BUTTON_HELD, {0, 0, 0, 0}, 0xB5, {0, 0, 0, 0},"
    )
    feedback = parsed["feedback_arbiter"]
    idle_edge = next(
        row for row in feedback.statements
        if row.kind == "instruction" and row.text == "bt rl_feedback_return"
        and feedback.statement_by_address[row.address - 2].text == "tst r0,r0"
        and feedback.statement_by_address[row.address - 4].text == "mov.b @(0x1,r1),r0"
    )
    idle_word = int.from_bytes(fixture[idle_edge.address:idle_edge.address + 2], "big")
    idle_target = map_switching_assembly._validate_direct_branch_encoding(
        feedback, idle_edge, idle_word
    )
    idle = (
        "    set_ignition_state(PHASE_IDLE, MODE_OBSERVE, 0);\n"
        "    if (!invoke_ignition(\"ign-inactive\", 110, 316, 110))"
    )
    held = (
        "    write_u16(rom_pointer(RL_CONFIG), 0);\n"
        "    ram_pointer(SELECTOR_STATE)[0] = 5;\n"
        "    run_engine();\n"
        "    if (!expect_phase_reason(\n"
        "            \"gate-config-and-map-index\", PHASE_IDLE, REASON_CONFIG_INVALID))"
    )
    return (
        (
            "periodic",
            "(void)invoke_r4(PERIODIC_WRAPPER, 0);",
            "(void)invoke_r4(RL_ENGINE, 0);",
            f"uncovered wrapper entry {periodic:#010x}",
        ),
        (
            "adapter-idle",
            idle,
            idle.replace("PHASE_IDLE", "PHASE_ACTIVE", 1),
            f"uncovered wrapper branch {phase.address:#010x}->{phase_target:#010x}",
        ),
        (
            "engine-map",
            held,
            held.replace("[0] = 5;", "[0] = 0;", 1),
            f"uncovered wrapper branch {map_edge.address:#010x}->{map_target:#010x}",
        ),
        (
            "controller-zero-band",
            zero_call,
            "    ram_pointer(APC_MODE_SNAPSHOT)[0] = 0x40;\n" + zero_call,
            f"uncovered wrapper branch {zero_edge.address:#010x}->{zero_target:#010x}",
        ),
        (
            "feedback-idle-clear",
            idle_clear,
            idle_clear.replace("REASON_NONE", "REASON_RPM_LOW", 1).replace(
                "FLAG_BUTTON_HELD", "0", 1
            ),
            f"uncovered wrapper branch {idle_edge.address:#010x}->{idle_target:#010x}",
        ),
    )


def _measure_rolling_launch(
    target, source, command, invoke, elf, fixture, composed, parsed, build_dir, marker,
):
    """Trace one relocated Rolling Launch harness and require its measured regions."""
    rom = target.rom
    region_names, unit_names = _rolling_coverage_names(target.rolling_layout)
    _require_rolling_fixture_bytes(rom, fixture, composed, parsed, unit_names)
    regions = {
        key: target.rolling_layout.code_region_by_key[key]
        for key in region_names
    }
    boundaries = _rolling_boundaries(target, regions)
    serializer, stub = _rolling_serializer_stub(target)
    ignition = target.rolling_layout.hook_by_key["primary_ignition_command"].stock
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
                raise VerificationError(f"{rom} rolling ELF changes during execution")
            records = base_verifier.read_pc_trace(trace)
        except base_verifier.VerificationError as error:
            raise VerificationError(f"{rom} rolling execution binding: {error}") from error
        return result, records, invokes

    def coverage(records, invokes):
        try:
            return rolling_verifier.require_wrapper_coverage(
                records, fixture, parsed, regions, boundaries, invokes,
                serializer, ignition, serializer_stub=stub,
                coverage_regions=region_names, coverage_units=unit_names,
            )
        except rolling_verifier.VerificationError as error:
            raise VerificationError(f"{rom} rolling coverage: {error}") from error

    result, records, invokes = execute(elf)
    covered = coverage(records, invokes)
    if marker not in result.stdout:
        detail = result.stdout.rstrip()
        raise VerificationError(
            f"{rom} rolling lacks its semantic PASS marker"
            + (f"\n{detail}" if detail else "")
        )
    negatives = []
    for name, old, new, reason in _rolling_omissions(parsed, regions, fixture):
        if snapshot.count(old) != 1:
            raise VerificationError(f"{rom} rolling negative lacks its unique {name} edit")
        text = snapshot.replace(old, new, 1)
        negative_source = build_dir / f"{rom.lower()}-rolling-no-{name}.c"
        negative_source.write_text(text, encoding="utf-8")
        negative_elf = build_dir / f"{rom.lower()}-rolling-no-{name}.elf"
        negative_command = list(command)
        negative_command[negative_command.index("-o") + 1] = negative_elf
        negative_command[negative_command.index(source)] = negative_source
        base_verifier.run_command(negative_command, timeout=120)
        try:
            require_separate_storage(negative_elf, ((base_verifier.TEST_RAM_BASE, 65536),))
        except (ELFStorageError, OSError) as error:
            raise VerificationError(
                f"{rom} rolling negative ELF storage separation: {error}"
            ) from error
        negative, records, invokes = execute(negative_elf)
        if marker not in negative.stdout:
            detail = negative.stdout.rstrip()
            raise VerificationError(
                f"{rom} rolling negative loses its semantic PASS marker"
                + (f"\n{detail}" if detail else "")
            )
        try:
            coverage(records, invokes)
        except VerificationError as error:
            if str(error) != f"{rom} rolling coverage: {reason}":
                raise VerificationError(
                    f"{rom} rolling negative fails outside its omitted outcome: {error}"
                ) from error
        else:
            raise VerificationError(
                f"{rom} rolling coverage accepts the omitted {name} case"
            )
        if negative_source.read_text(encoding="utf-8") != text:
            raise VerificationError(f"{rom} rolling negative source changes during execution")
        negatives.append(
            f"VQ_SH_ELF_RUNTIME_ROLLING_NEGATIVE status=PASS rom={rom} "
            f"omitted={name} {reason}"
        )
    if source.read_text(encoding="utf-8") != snapshot:
        raise VerificationError(f"{rom} rendered rolling source changes during execution")
    scope = ",".join(region_names)
    report = (
        f"VQ_SH_ELF_RUNTIME_ROLLING_COVERAGE status=PASS rom={rom} scope={scope} "
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
    rolling_parsed=None,
    fixture=None,
    composed_image=None,
):
    measured = target.rom in ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B") and name == "map-switching"
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
    if name == "rolling-launch" and _rolling_measured(target.rom):
        if rolling_parsed is None or fixture is None or composed_image is None:
            raise VerificationError(
                f"{target.rom} rolling coverage requires typed/composed/fixture context"
            )
        return _measure_rolling_launch(
            target, source, command, objects[0], output, fixture, composed_image,
            rolling_parsed, build_dir, marker,
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


def _run_harnesses(target, fixture, build_dir, *, map_parsed, rolling_parsed, composed_image):
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

    if target.rom in ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B"):
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
    if target.rom in ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B") and f"VQ_SH_ELF_RUNTIME_MAP_COVERAGE status=PASS rom={target.rom} " not in markers[0]:
        raise VerificationError(f"{target.rom} map lacks its measured coverage terminal")
    if target.rolling_layout is not None:
        rolling_source = _render_harness(
            target, "rolling_launch_harness.c", build_dir
        )
        vq37_rolling = (
            target.rolling_layout.variant == "vq37-fuel-coordinator"
        )
        rolling_marker = (
            "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=144 "
            "structural=11 gates=32 config=24 threshold=4 activation=6 "
            "active=9 cooldown=5 ignition=25 wrappers=6 feedback=8 "
            "fuel_coordinator=3 hold=11 entries=9"
            if vq37_rolling and target.rom in MEASURED_VQ37_ROLLING_ROMS
            else
            "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=142 "
            "structural=11 gates=32 config=24 threshold=4 activation=6 "
            "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 "
            "fuel_coordinator=3 hold=11 entries=9"
            if vq37_rolling
            else
            "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=130 "
            "structural=11 gates=32 config=24 threshold=4 activation=6 "
            "active=9 cooldown=5 ignition=25 wrappers=6 feedback=8 "
            "entries=8"
            if target.rom in MEASURED_ROLLING_ROMS
            else
            "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=128 "
            "structural=11 gates=32 config=24 threshold=4 activation=6 "
            "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 "
            "entries=8"
        )
        rolling_output = _compile_and_run(
            target,
            "rolling-launch",
            rolling_source,
            rom_object,
            (invoke,),
            build_dir,
            rolling_marker,
            rolling_parsed=rolling_parsed,
            fixture=fixture,
            composed_image=composed_image,
            defines=(
                ("TARGET_VQ37_ROLLING",) if vq37_rolling else ()
            ) + (
                ("TARGET_8MFK",)
                if target.rom in runtime_targets.RELOCATED_8MFK_ROMS
                else ()
            ) + (
                ("MEASURE_ROLLING_COVERAGE",)
                if _rolling_measured(target.rom)
                else ()
            ) + (
                (VQ37_MAP_HARNESS_BY_VARIANT[target.map_layout.variant][0],)
                if target.map_layout.variant in VQ37_MAP_HARNESS_BY_VARIANT
                else ()
            ),
        )
        markers.append(rolling_output)
        if (
            _rolling_measured(target.rom)
            and f"VQ_SH_ELF_RUNTIME_ROLLING_COVERAGE status=PASS rom={target.rom} "
            not in rolling_output
        ):
            raise VerificationError(f"{target.rom} rolling lacks its measured coverage terminal")
    can_defines = (
        ("TELEMETRY_TAIL_CHAIN",)
        if target.telemetry_layout.variant.endswith("-tail-chain")
        else ()
    ) + (
        (VQ37_MAP_HARNESS_BY_VARIANT[target.map_layout.variant][0],)
        if target.map_layout.variant in VQ37_MAP_HARNESS_BY_VARIANT
        else ()
    )
    markers.append(
        _compile_and_run(
            target,
            "can-telemetry",
            can_source,
            rom_object,
            (invoke, exception),
            build_dir,
            "VQ_SH_ELF_CAN_TELEMETRY status=PASS "
            f"cases={89 if target.rom == '1ME3B' else 83} entries=11 "
            "profiles=1 contexts=10 isr_rte=5",
            defines=can_defines,
        )
    )
    return tuple(markers)


def verify_target(rom, locks, verbose=False):
    target = runtime_targets.load_runtime_target(rom)
    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    rolling_parsed = (
        rolling_launch_assembly.validate_assembly_sources(
            target.rolling_layout
        )
        if target.rolling_layout is not None
        else None
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
        rolling_blobs = (
            _assemble_stage(
                "rolling", target.rolling_layout, rolling_parsed,
                target.rolling_payloads, build_dir, verbose,
            )
            if target.rolling_layout is not None
            else {}
        )
        can_blobs = _assemble_stage(
            "telemetry", target.telemetry_layout, can_parsed,
            target.telemetry_payloads, build_dir, verbose,
        )
        map_audit = map_switching_assembly.validate_instruction_semantics(
            target.map_layout, map_parsed, map_blobs
        )
        rolling_audit = (
            rolling_launch_assembly.validate_instruction_semantics(
                target.rolling_layout, rolling_parsed, rolling_blobs
            )
            if target.rolling_layout is not None
            else None
        )
        can_audit = can_telemetry_assembly.validate_instruction_semantics(
            target.telemetry_layout, can_parsed, can_blobs
        )
        _, _, composition = _compose_and_lock(
            target, locks, map_blobs, rolling_blobs, can_blobs
        )
        (
            fixture,
            map_relocated,
            rolling_relocated,
            can_relocated,
            differentiated,
            stubs,
        ) = _build_dynamic_fixture(
            target,
            composition,
            map_parsed,
            rolling_parsed,
            can_parsed,
        )
        markers = _run_harnesses(target, fixture, build_dir,
                                 map_parsed=map_parsed, rolling_parsed=rolling_parsed,
                                 composed_image=composition.data)
        if rom == "1ME3B":
            import verify_ignition_consumers
            markers = (*markers, verify_ignition_consumers.verify(
                target, fixture, build_dir
            ))
    for marker in markers:
        print(marker)
    instructions = (
        map_audit.instructions
        + (0 if rolling_audit is None else rolling_audit.instructions)
        + can_audit.instructions
    )
    dynamic_cases = sum(
        can_verifier.marker_cases(marker) for marker in markers
    )
    print(
        f"VQ_SH_ELF_RUNTIME_TARGET status=PASS rom={rom} "
        f"family={target.family} instructions={instructions} "
        f"dynamic_cases={dynamic_cases} "
        f"map_ram_literals_relocated={map_relocated} "
        f"rolling_ram_literals_relocated={rolling_relocated} "
        f"telemetry_ram_literals_relocated={can_relocated} "
        f"differentiated_bytes={differentiated} stock_stubs={stubs} "
        f"composition_sha256={composition.sha256}"
    )
    return {
        "rom": rom,
        "instructions": instructions,
        "dynamic_cases": dynamic_cases,
    }


def verify(verbose=False):
    locks = runtime_targets.load_payload_locks()
    results = [
        verify_target(rom, locks[rom], verbose=verbose)
        for rom in runtime_targets.RELOCATED_ROMS
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
