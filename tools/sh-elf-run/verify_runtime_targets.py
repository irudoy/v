#!/usr/bin/env python3
"""Execute every relocated 8MFK runtime target with GNU SH-2E tools."""

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


MAP_CASES = 139
ROLLING_CASES = 121
TELEMETRY_CASES = 62
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
    rolling_result = rolling_launch_compose.compose(
        layout=target.rolling_layout,
        base=map_result.data,
        blobs=rolling_blobs,
    )
    can_result = can_telemetry_compose.compose(
        layout=target.telemetry_layout,
        base=rolling_result.data,
        blobs=can_blobs,
    )
    actual = (
        map_result.sha256,
        rolling_result.sha256,
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
    map_hooks = {hook.key: hook for hook in target.map_layout.hooks}
    rolling_hooks = target.rolling_layout.hook_by_key
    can_hooks = target.telemetry_layout.hook_by_key
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
        "exhaust_cvtc_target_lookup_even",
        "exhaust_cvtc_target_lookup_odd",
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
        rolling_hooks["periodic_scheduler_index_0"].stock: RETURN_STUB,
        rolling_hooks["primary_ignition_command"].stock: RETURN_STUB,
        can_hooks["coherent_snapshot_call"].stock: RETURN_STUB,
        can_hooks["knock_interval_latch"].stock: RETURN_STUB,
    })
    for key in ("hcan1_primary_init", "hcan1_recovery_init"):
        stubs[can_hooks[key].stock] = RETURN_ONE_STUB

    serializer = map_hooks["cruise_feedback_serializer"].stock
    status_alias = base_verifier.alias_high_ram(
        target.map_layout.feedback.status_byte_address
    )
    stubs[serializer] = (
        FEEDBACK_SERIALIZER_PREFIX + status_alias.to_bytes(4, "big")
    )
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
    rolling_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, rolling_parsed
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
    if name == "map_switching_harness.c":
        odd = target.map_layout.family_by_key[
            "exhaust_cvtc_target_odd"
        ].canonical_address
        overrides = {0x0000B43A: odd, 0x0000B43B: odd + 1}
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
    command = [
        base_verifier.GCC,
        "-m2e", "-mb", "-std=c11", "-O2",
        "-Wall", "-Wextra", "-Werror",
    ]
    command.extend(f"-D{define}=1" for define in defines)
    command.extend([
        f"-Wl,-Ttext-segment={base_verifier.DRIVER_TEXT_BASE:#x}",
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
    rolling_source = _render_harness(
        target, "rolling_launch_harness.c", build_dir
    )
    can_source = _render_harness(
        target, "can_telemetry_harness.c", build_dir
    )
    markers = (
        _compile_and_run(
            target,
            "map-switching",
            map_source,
            rom_object,
            (invoke,),
            build_dir,
            "VQ_SH_ELF_MAP_SWITCHING status=PASS cases=139 selector=17 "
            "adapters=99 limiter=14 feedback=9 feedback_invocations=17 "
            "entries=13",
            defines=("TARGET_DUAL_EXHAUST",),
        ),
        _compile_and_run(
            target,
            "rolling-launch",
            rolling_source,
            rom_object,
            (invoke,),
            build_dir,
            "VQ_SH_ELF_ROLLING_LAUNCH status=PASS cases=121 "
            "structural=11 gates=26 config=24 threshold=4 activation=5 "
            "active=9 cooldown=5 ignition=24 wrappers=6 feedback=7 "
            "entries=8",
        ),
        _compile_and_run(
            target,
            "can-telemetry",
            can_source,
            rom_object,
            (invoke, exception),
            build_dir,
            "VQ_SH_ELF_CAN_TELEMETRY status=PASS cases=62 entries=10 "
            "profiles=1 contexts=8 isr_rte=5",
            defines=("TELEMETRY_TAIL_CHAIN",),
        ),
    )
    return markers


def verify_target(rom, locks, verbose=False):
    target = runtime_targets.load_runtime_target(rom)
    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    rolling_parsed = rolling_launch_assembly.validate_assembly_sources(
        target.rolling_layout
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
        rolling_blobs = _assemble_stage(
            "rolling", target.rolling_layout, rolling_parsed,
            target.rolling_payloads, build_dir, verbose,
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
        + rolling_audit.instructions
        + can_audit.instructions
    )
    print(
        f"VQ_SH_ELF_RUNTIME_TARGET status=PASS rom={rom} "
        f"family={target.family} instructions={instructions} "
        f"dynamic_cases={MAP_CASES + ROLLING_CASES + TELEMETRY_CASES} "
        f"map_ram_literals_relocated={map_relocated} "
        f"rolling_ram_literals_relocated={rolling_relocated} "
        f"telemetry_ram_literals_relocated={can_relocated} "
        f"differentiated_bytes={differentiated} stock_stubs={stubs} "
        f"composition_sha256={composition.sha256}"
    )
    return {
        "rom": rom,
        "instructions": instructions,
        "dynamic_cases": MAP_CASES + ROLLING_CASES + TELEMETRY_CASES,
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
