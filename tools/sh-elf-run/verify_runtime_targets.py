#!/usr/bin/env python3
"""Execute every relocated runtime target with GNU SH-2E tools."""

from __future__ import annotations

import hashlib
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


def _compile_and_run(
    target,
    name,
    source,
    rom_object,
    objects,
    build_dir,
    marker,
    defines=(),
):
    output = build_dir / f"{target.rom.lower()}-{name}.elf"
    driver_text_base = max(
        base_verifier.DRIVER_TEXT_BASE,
        len(target.stock_image.data) + 0x10000,
    )
    command = [
        base_verifier.GCC,
        "-m2e", "-mb", "-std=c11", "-O2",
        "-Wall", "-Wextra", "-Werror",
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
    result = base_verifier.run_command(
        [
            base_verifier.RUN,
            f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k",
            output,
        ],
        timeout=180,
    )
    if marker not in result.stdout:
        raise VerificationError(
            f"{target.rom}.{name}: zero exit without exact PASS marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    return result.stdout.strip()


def _run_harnesses(target, fixture, build_dir):
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
        )
    ]
    if target.rolling_layout is not None:
        rolling_source = _render_harness(
            target, "rolling_launch_harness.c", build_dir
        )
        vq37_rolling = (
            target.rolling_layout.variant == "vq37-fuel-coordinator"
        )
        rolling_marker = (
            "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=137 "
            "structural=11 gates=27 config=24 threshold=4 activation=6 "
            "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 "
            "fuel_coordinator=3 hold=11 entries=9"
            if vq37_rolling
            else
            "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=123 "
            "structural=11 gates=27 config=24 threshold=4 activation=6 "
            "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 "
            "entries=8"
        )
        markers.append(_compile_and_run(
            target,
            "rolling-launch",
            rolling_source,
            rom_object,
            (invoke,),
            build_dir,
            rolling_marker,
            defines=(
                ("TARGET_VQ37_ROLLING",) if vq37_rolling else ()
            ) + (
                ("TARGET_8MFK",)
                if target.rom in runtime_targets.RELOCATED_8MFK_ROMS
                else ()
            ) + (
                (VQ37_MAP_HARNESS_BY_VARIANT[target.map_layout.variant][0],)
                if target.map_layout.variant in VQ37_MAP_HARNESS_BY_VARIANT
                else ()
            ),
        ))
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
            "VQ_SH_ELF_CAN_TELEMETRY status=PASS cases=80 entries=11 "
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
        markers = _run_harnesses(target, fixture, build_dir)
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
