#!/usr/bin/env python3
"""Execute every relocated runtime target with GNU SH-2E tools."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
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
MEASURED_MAP_ROMS = ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B", "1ME3B", "1EK7A")
DUAL_BANK_MMIO_BASE = 0x01020000
DUAL_BANK_MMIO_SIZE = 36864
SH7059_DUAL_BANK_MMIO_SIZE = 40960
SH7059_VARIANTS = frozenset({"sh7059-1nd", "sh7059-1me3b", "sh7059-1ek7a"})
SIMULATOR_MEMORY_ENV_KEYS = (
    "VQ_SH_HIGH_RAM_BASE",
    "VQ_SH_HIGH_RAM_LAYOUT",
    "VQ_SH_M95320_BASE",
    "VQ_SH_M95320_SCI2_BASE",
    "VQ_SH_M95320_CS_ADDR",
    "VQ_SH_M95320_CS_MASK",
)


def _simulator_env(base_env, *, trace_file=None, trace_ranges=None,
                   dual_bank_mmio=False, sim_layout=None, eeprom_layout=None):
    """Build a clean simulator environment with all host memory/EEPROM vars scrubbed or pinned."""
    env = dict(base_env)
    for key in SIMULATOR_MEMORY_ENV_KEYS:
        env.pop(key, None)
    if trace_file is not None:
        env["VQ_SH_PC_TRACE_FILE"] = str(trace_file)
        env["VQ_SH_PC_TRACE_FORMAT"] = "v1"
        env["VQ_SH_PC_TRACE_RANGES"] = trace_ranges
    if dual_bank_mmio:
        if eeprom_layout is None:
            raise VerificationError("dual-bank MMIO run requires typed eeprom_persistence layout")
        env["VQ_SH_HIGH_RAM_BASE"] = f"{base_verifier.TEST_RAM_BASE:#x}"
        env["VQ_SH_HIGH_RAM_LAYOUT"] = sim_layout
        env["VQ_SH_M95320_BASE"] = f"{base_verifier.M95320_BASE:#x}"
        env["VQ_SH_M95320_SCI2_BASE"] = f"{eeprom_layout.sci2_base_address:#x}"
        env["VQ_SH_M95320_CS_ADDR"] = f"{eeprom_layout.pcdr_address:#x}"
        env["VQ_SH_M95320_CS_MASK"] = f"{eeprom_layout.pcdr_cs_mask:#x}"
    return env
RETURN_STUB = bytes.fromhex("000b0009")
POP_PR_RETURN_STUB = bytes.fromhex("4f26000b0009")
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


def _stock_warm_binding(target, composed_image, map_image=None):
    """Validate and describe the stock warm-reinit call window for a relocated ROM."""
    ee = target.map_layout.eeprom_persistence
    if ee is None or not ee.startup_warm_return_pc:
        return None
    stock = target.stock_image.data
    hook = next(item for item in target.map_layout.hooks if item.key == "startup_initializer")
    can_wrap = target.telemetry_layout.code_region_by_key["startup_wrapper"].entry
    map_wrap = target.map_layout.code_region_by_key["startup_wrapper"].entry
    warm_return = ee.startup_warm_return_pc
    warm_call = warm_return - 4
    if stock[warm_return : warm_return + len(POP_PR_RETURN_STUB)] != composed_image[warm_return : warm_return + len(POP_PR_RETURN_STUB)]:
        raise VerificationError(f"{target.rom}: composed image alters warm return boundary at {warm_return:#x}")
    if ee.startup_shared_pointer:
        if stock[warm_call : warm_call + 4] != composed_image[warm_call : warm_call + 4]:
            raise VerificationError(f"{target.rom}: composed image alters stock warm BSR at {warm_call:#x}")
        bsr_word = int.from_bytes(stock[warm_call : warm_call + 2], "big")
        nop_word = int.from_bytes(stock[warm_call + 2 : warm_call + 4], "big")
        if (bsr_word & 0xF000) != 0xB000 or nop_word != 0x0009:
            raise VerificationError(f"{target.rom}: unexpected warm call opcode {bsr_word:04x}/{nop_word:04x} at {warm_call:#x}")
        disp = bsr_word & 0x0FFF
        if disp & 0x0800:
            disp -= 0x1000
        trampoline = warm_call + 4 + disp * 2
        if stock[trampoline : trampoline + 6] != composed_image[trampoline : trampoline + 6]:
            raise VerificationError(f"{target.rom}: composed image alters warm trampoline at {trampoline:#x}")
        mov_word = int.from_bytes(stock[trampoline : trampoline + 2], "big")
        jmp_word = int.from_bytes(stock[trampoline + 2 : trampoline + 4], "big")
        tramp_nop = int.from_bytes(stock[trampoline + 4 : trampoline + 6], "big")
        if (mov_word & 0xFF00) != 0xD200 or jmp_word != 0x422B or tramp_nop != 0x0009:
            raise VerificationError(f"{target.rom}: unexpected warm trampoline at {trampoline:#x}")
        cell = ((trampoline + 4) & ~3) + (mov_word & 0xFF) * 4
        if cell != hook.address:
            raise VerificationError(f"{target.rom}: warm trampoline loads {cell:#x}, expected shared hook {hook.address:#x}")
        if int.from_bytes(stock[cell : cell + 4], "big") != hook.stock:
            raise VerificationError(f"{target.rom}: stock shared pointer at {cell:#x} differs")
        if int.from_bytes(composed_image[cell : cell + 4], "big") != can_wrap:
            raise VerificationError(f"{target.rom}: composed shared pointer at {cell:#x} differs from CAN wrapper {can_wrap:#x}")
        if map_image is not None and int.from_bytes(map_image[cell : cell + 4], "big") != map_wrap:
            raise VerificationError(f"{target.rom}: map-stage shared pointer at {cell:#x} differs from map wrapper {map_wrap:#x}")
        return {
            "shared": True,
            "entry": warm_call,
            "call": warm_call,
            "return_pc": warm_return,
            "trampoline": trampoline,
            "cell": cell,
            "stock_callee": hook.stock,
            "can_wrapper": can_wrap,
            "map_wrapper": map_wrap,
        }
    warm_entry = warm_call - 2
    if stock[warm_entry : warm_entry + 6] != composed_image[warm_entry : warm_entry + 6]:
        raise VerificationError(f"{target.rom}: composed image alters stock warm load/JSR at {warm_entry:#x}")
    mov_word = int.from_bytes(stock[warm_entry : warm_entry + 2], "big")
    jsr_word = int.from_bytes(stock[warm_call : warm_call + 2], "big")
    nop_word = int.from_bytes(stock[warm_call + 2 : warm_call + 4], "big")
    if (mov_word & 0xFF00) != 0xD100 or jsr_word != 0x410B or nop_word != 0x0009:
        raise VerificationError(f"{target.rom}: unexpected SH7059 warm sequence at {warm_entry:#x}")
    cell = ((warm_entry + 4) & ~3) + (mov_word & 0xFF) * 4
    if cell == hook.address:
        raise VerificationError(f"{target.rom}: separate SH7059 warm pointer aliases cold hook {hook.address:#x}")
    stock_ptr = int.from_bytes(stock[cell : cell + 4], "big")
    comp_ptr = int.from_bytes(composed_image[cell : cell + 4], "big")
    if stock_ptr != hook.stock or comp_ptr != hook.stock:
        raise VerificationError(
            f"{target.rom}: SH7059 warm pointer at {cell:#x} differs: stock={stock_ptr:#x} composed={comp_ptr:#x} expected={hook.stock:#x}"
        )
    if map_image is not None and int.from_bytes(map_image[cell : cell + 4], "big") != hook.stock:
        raise VerificationError(f"{target.rom}: SH7059 map-stage warm pointer at {cell:#x} differs from stock")
    return {
        "shared": False,
        "entry": warm_entry,
        "call": warm_call,
        "return_pc": warm_return,
        "trampoline": None,
        "cell": cell,
        "stock_callee": hook.stock,
        "can_wrapper": can_wrap,
        "map_wrapper": map_wrap,
    }


def _require_stock_warm_trace(records, target, warm):
    """Require ordered PC trace execution of the stock warm-reinit call window."""
    if warm is None:
        return
    code = target.map_layout.code_region_by_key
    limiter_entry = code["limiter_commit"].entry
    forbidden_entries = {
        code["cruise_free_startup_init"].entry,
        code["eeprom_boot_restore"].entry,
        code["eeprom_task_wrapper"].entry,
    }
    entry_pc = warm["entry"]
    call_pc = warm["call"]
    ret_pc = warm["return_pc"]
    stock_callee = warm["stock_callee"]
    can_wrap = warm["can_wrapper"]
    map_wrap = warm["map_wrapper"]

    windows = []
    idx = 0
    while idx < len(records):
        if records[idx][0] == entry_pc and not records[idx][2]:
            end = idx + 1
            while end < len(records) and not (records[end][0] == ret_pc and not records[end][2]):
                end += 1
            if end + 2 >= len(records):
                raise VerificationError(
                    f"{target.rom}: stock warm window starting at {entry_pc:#010x} never completed return boundary {ret_pc:#010x}"
                )
            windows.append(records[idx : end + 3])
            idx = end + 3
        else:
            idx += 1

    if not windows:
        raise VerificationError(f"uncovered stock warm entry {entry_pc:#010x}")

    expected_ret_edge = [
        (ret_pc, 0x4F26, 0),
        (ret_pc + 2, 0x000B, 0),
        (ret_pc + 4, 0x0009, 1),
    ]
    if warm["shared"]:
        if len(windows) != 2:
            raise VerificationError(
                f"{target.rom}: expected 2 SH7058 stock warm windows (CAN + direct), got {len(windows)}"
            )
        tramp = warm["trampoline"]
        saw_can = False
        saw_direct = False
        for window in windows:
            if window[-3:] != expected_ret_edge:
                raise VerificationError(f"{target.rom}: stock warm return boundary edge differs")
            pcs = [pc for pc, _word, _delay in window]
            if pcs[:5] != [call_pc, call_pc + 2, tramp, tramp + 2, tramp + 4]:
                raise VerificationError(
                    f"{target.rom}: stock warm prefix differs: {[hex(p) for p in pcs[:5]]}"
                )
            if set(pcs) & forbidden_entries:
                raise VerificationError(
                    f"{target.rom}: stock warm window entered cold/periodic code: {sorted(hex(p) for p in set(pcs) & forbidden_entries)}"
                )
            if pcs.count(stock_callee) != 1 or pcs.count(limiter_entry) != 1:
                raise VerificationError(
                    f"{target.rom}: stock warm window call counts differ "
                    f"(stock={pcs.count(stock_callee)}, limiter={pcs.count(limiter_entry)})"
                )
            if pcs.index(stock_callee) >= pcs.index(limiter_entry):
                raise VerificationError(
                    f"{target.rom}: stock warm window called limiter_commit before stock initializer"
                )
            after_tramp = pcs[5]
            if after_tramp == can_wrap:
                if pcs.count(can_wrap) != 1 or pcs.count(map_wrap) != 1 or pcs.index(can_wrap) >= pcs.index(map_wrap):
                    raise VerificationError(
                        f"{target.rom}: CAN-wrapped warm window did not chain once CAN -> Map startup"
                    )
                saw_can = True
            elif after_tramp == map_wrap:
                if can_wrap in pcs or pcs.count(map_wrap) != 1:
                    raise VerificationError(
                        f"{target.rom}: direct warm window unexpectedly entered CAN wrapper or repeated map wrapper"
                    )
                saw_direct = True
            else:
                raise VerificationError(
                    f"{target.rom}: stock warm trampoline jumped to unexpected target {after_tramp:#010x}"
                )
        if not (saw_can and saw_direct):
            raise VerificationError(
                f"{target.rom}: stock warm trace missing route (can={saw_can}, direct={saw_direct})"
            )
    else:
        if len(windows) != 1:
            raise VerificationError(
                f"{target.rom}: expected 1 SH7059 stock warm bypass window, got {len(windows)}"
            )
        window = windows[0]
        expected_bypass = [
            (entry_pc, 0),
            (call_pc, 0),
            (call_pc + 2, 1),
            (stock_callee, 0),
            (stock_callee + 2, 1),
            (ret_pc, 0),
            (ret_pc + 2, 0),
            (ret_pc + 4, 1),
        ]
        actual_bypass = [(pc, delay) for pc, _word, delay in window]
        if actual_bypass != expected_bypass or window[-3:] != expected_ret_edge:
            raise VerificationError(
                f"{target.rom}: SH7059 stock warm bypass trace differs: {actual_bypass}"
            )


def _install_stock_stubs(fixture, target, *, dual_bank_mmio=False):
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
    if target.map_layout.cruise_free is not None:
        map_keys.update({
            "stationary_rx_dispatch",
            "tach_180_serializer",
            "tach_1f9_serializer",
        })
    if target.map_layout.eeprom_persistence is not None:
        map_keys.add("eeprom_periodic_task")
    missing = map_keys - map_hooks.keys()
    if missing:
        raise VerificationError(
            f"{target.rom}: map layout lacks stock hooks {sorted(missing)}"
        )
    stubs = {
        map_hooks[key].stock: RETURN_STUB
        for key in map_keys
    }
    if target.map_layout.eeprom_persistence is not None:
        ee = target.map_layout.eeprom_persistence
        stubs[ee.stock_sci2_acquire] = RETURN_STUB
        stubs[ee.stock_sci2_release] = RETURN_STUB
        if dual_bank_mmio and ee.startup_cold_return_pc:
            stubs[ee.startup_cold_return_pc] = POP_PR_RETURN_STUB
        if dual_bank_mmio and ee.startup_warm_return_pc:
            stubs[ee.startup_warm_return_pc] = POP_PR_RETURN_STUB
    stubs.update({
        can_hooks["coherent_snapshot_call"].stock: RETURN_STUB,
        can_hooks["knock_interval_latch"].stock: RETURN_STUB,
    })
    for key in ("hcan1_primary_init", "hcan1_recovery_init"):
        stubs[can_hooks[key].stock] = RETURN_ONE_STUB
    evaluator = can_hooks["knock_margin_latch"].stock
    stubs[evaluator] = can_verifier.knock_evaluator_stub(evaluator)

    serializer = map_hooks["cruise_feedback_serializer"].stock
    status_target = (
        target.map_layout.feedback.status_byte_address
        if dual_bank_mmio
        else base_verifier.alias_high_ram(
            target.map_layout.feedback.status_byte_address
        )
    )
    stubs[serializer] = _feedback_serializer_stub(serializer, status_target)
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


def _build_p3_map_fixture(target, composition):
    """Build a dual-bank MMIO map-switching fixture with zero RAM literal rewrites."""
    fixture = bytearray(composition.data)
    differentiated = base_verifier.differentiate_map_copies(
        fixture, target.map_layout
    )
    stubs = _install_stock_stubs(fixture, target, dual_bank_mmio=True)
    return bytes(fixture), differentiated, stubs


def _marker_cases(output):
    """Read the reported dynamic case count(s) from one harness stdout."""
    counts = [int(item) for item in re.findall(r"\bcases=(\d+)\b", output)]
    if "VQ_SH_ELF_MAP_SWITCHING_CRUISE_FREE " in output:
        expected_lines = 4 if "VQ_SH_ELF_MAP_SWITCHING_WARM " in output else 3
        if len(counts) != expected_lines:
            raise VerificationError(
                f"Package 3 map harness must report {expected_lines} case counts "
                f"(cruise-free, eeprom, warm, core), got {len(counts)}"
            )
        return sum(counts)
    return can_verifier.marker_cases(output)


def _build_dynamic_fixture(
    target,
    composition,
    map_parsed,
    can_parsed,
):
    """Apply simulator-only transforms after exact target identity passes."""
    fixture = bytearray(composition.data)
    map_relocated = base_verifier.relocate_assembly_ram_literals(
        fixture, map_parsed, keep_mmio=True
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
            environment = _simulator_env(
                os.environ,
                trace_file=trace,
                trace_ranges=",".join(
                    f"{begin:x}:{end:x}" for begin, end in ((0, len(fixture)), *ranges)
                ),
            )
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


def _write_p3_bindings_header(target, build_dir, warm_binding=None):
    """Emit typed Package 3 C defines straight from the projected layout."""
    layout = target.map_layout
    cf = layout.cruise_free
    ee = layout.eeprom_persistence
    code = layout.code_region_by_key
    hook = next(item for item in layout.hooks if item.key == "startup_initializer")
    can_wrap = target.telemetry_layout.code_region_by_key["startup_wrapper"].entry
    warm_entry = (
        warm_binding["entry"]
        if warm_binding is not None
        else (ee.startup_warm_return_pc - 4 if ee.startup_shared_pointer else ee.startup_warm_return_pc - 6)
    )
    lines = [
        f"#define STARTUP_WRAPPER 0x{code['startup_wrapper'].entry:08x}U",
        f"#define FEEDBACK_ENGINE 0x{code['cruise_feedback_engine'].entry:08x}U",
        "#define FEEDBACK_MIL_PRESERVES_STOCK 1",
        "#define CF_RPM_COARSE_U16 1",
        f"#define CF_CONFIG_ADDR 0x{cf.config.start:08x}U",
        f"#define CF_STARTUP_INIT 0x{code['cruise_free_startup_init'].entry:08x}U",
        f"#define CF_STATIONARY_WRAPPER 0x{code['stationary_rx_wrapper'].entry:08x}U",
        f"#define CF_STEP_ENTRY 0x{code['cruise_free_step'].entry:08x}U",
        f"#define CF_ASCD_ENABLED_ENTRY 0x{code['cruise_free_ascd_enabled'].entry:08x}U",
        f"#define CF_FEEDBACK_EXT_ENTRY 0x{code['cruise_free_feedback_ext'].entry:08x}U",
        f"#define CF_TACH_180_WRAPPER 0x{code['tach_180_wrapper'].entry:08x}U",
        f"#define CF_TACH_1F9_WRAPPER 0x{code['tach_1f9_wrapper'].entry:08x}U",
        f"#define CF_TACH_APPLY_ENTRY 0x{code['tach_override_apply'].entry:08x}U",
        f"#define CF_RAM_BASE 0x{cf.ram.start:08x}U",
        f"#define CF_RAM_SIZE {cf.ram.size}U",
        f"#define CF_RPM_FINE 0x{cf.rpm_fine_address:08x}U",
        f"#define CF_RPM_COARSE 0x{cf.rpm_coarse_address:08x}U",
        f"#define CF_BRAKE_BYTE 0x{cf.brake_address:08x}U",
        f"#define CF_APP1_ADDR 0x{cf.app1_address:08x}U",
        f"#define CF_APP2_ADDR 0x{cf.app2_address:08x}U",
        f"#define CF_PORT_STATE 0x{cf.port_state_address:08x}U",
        f"#define CF_HCAN1_STATE 0x{cf.hcan1_state_address:08x}U",
        f"#define CF_RX_STATE 0x{cf.rx_state_address:08x}U",
        f"#define CF_RX_RAW_HI 0x{cf.rx_raw_speed_address:08x}U",
        f"#define CF_MIL_BYTE 0x{cf.mil_byte_address:08x}U",
        f"#define CF_TACH_180_PAYLOAD 0x{cf.tach_180_payload_address:08x}U",
        f"#define CF_TACH_1F9_PAYLOAD 0x{cf.tach_1f9_payload_address:08x}U",
        f"#define CF_PORT_READY_MASK 0x{cf.port_ready_mask:02x}U",
        f"#define CF_HCAN1_INIT_MASK 0x{cf.hcan1_init_mask:02x}U",
        f"#define CF_BRAKE_MASK 0x{cf.brake_mask:02x}U",
        f"#define EE_CONFIG_ADDR 0x{ee.config.start:08x}U",
        f"#define EE_BOOT_RESTORE 0x{code['eeprom_boot_restore'].entry:08x}U",
        f"#define EE_TASK_WRAPPER 0x{code['eeprom_task_wrapper'].entry:08x}U",
        f"#define EE_RAM_BASE 0x{ee.ram.start:08x}U",
        f"#define EE_RAM_SIZE {ee.ram.size}U",
        f"#define EE_STOCK_BUSY 0x{ee.stock_busy_address:08x}U",
        f"#define EE_PORT_STATE 0x{ee.port_state_address:08x}U",
        f"#define EE_SHUTDOWN_REQ 0x{ee.shutdown_req_address:08x}U",
        f"#define EE_SHUTDOWN_STATE 0x{ee.shutdown_state_address:08x}U",
        f"#define EE_REINIT_MODE 0x{ee.reinit_mode_address:08x}U",
        f"#define EE_VBAT 0x{ee.vbat_address:08x}U",
        f"#define EE_PCDR_ADDR 0x{ee.pcdr_address:08x}U",
        f"#define EE_PLDR_ADDR 0x{ee.pldr_address:08x}U",
        f"#define EE_IG_ON_MASK 0x{ee.ig_on_mask:02x}U",
        f"#define EE_START_MASK 0x{ee.start_mask:02x}U",
        f"#define EE_SHUTDOWN_REQ_MASK 0x{ee.shutdown_req_mask:02x}U",
        f"#define EE_STARTUP_COLD_CALL_PC 0x{ee.startup_cold_return_pc - 4:08x}U",
        f"#define EE_STARTUP_COLD_RETURN_PC 0x{ee.startup_cold_return_pc:08x}U",
        f"#define EE_STARTUP_WARM_ENTRY_PC 0x{warm_entry:08x}U",
        f"#define EE_STARTUP_WARM_CALL_PC 0x{ee.startup_warm_return_pc - 4:08x}U",
        f"#define EE_STARTUP_WARM_RETURN_PC 0x{ee.startup_warm_return_pc:08x}U",
        f"#define EE_STARTUP_SHARED_POINTER {1 if ee.startup_shared_pointer else 0}",
        f"#define EE_STARTUP_CAN_RETURN_PC 0x{ee.startup_can_return_pc:08x}U",
        f"#define EE_CAN_STARTUP_WRAPPER 0x{can_wrap:08x}U",
        f"#define EE_STARTUP_HOOK_SLOT 0x{hook.address:08x}U",
    ]
    header_name = f"{target.rom.lower()}-p3-bindings.h"
    (build_dir / header_name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return header_name


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
    dual_bank_mmio=False,
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
        "-I", build_dir,
    ]
    command.extend(
        f"-D{define}" if "=" in define else f"-D{define}=1"
        for define in defines
    )
    command.extend([
        f"-Wl,-Ttext-segment={driver_text_base:#x}",
        "-Wl,--section-start=.rom=0",
        "-o", output,
        source,
        *objects,
        rom_object,
    ])
    base_verifier.run_command(command, timeout=120)
    sim_layout = (
        "sh7059-mmio"
        if getattr(getattr(target, "map_layout", None), "variant", None) in SH7059_VARIANTS
        else "sh7058-mmio"
    )
    dual_mmio_size = (
        SH7059_DUAL_BANK_MMIO_SIZE
        if sim_layout == "sh7059-mmio"
        else DUAL_BANK_MMIO_SIZE
    )
    storage_regions = (
        (
            (base_verifier.TEST_RAM_BASE, 65536),
            (base_verifier.M95320_BASE, base_verifier.M95320_SIZE),
            (DUAL_BANK_MMIO_BASE, dual_mmio_size),
        )
        if dual_bank_mmio
        else ((base_verifier.TEST_RAM_BASE, 65536),)
    )
    try:
        require_separate_storage(output, storage_regions)
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
            env=_simulator_env(os.environ),
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
            environment = _simulator_env(
                os.environ,
                trace_file=trace,
                trace_ranges=",".join(
                    f"{begin:x}:{end:x}" for begin, end in ((0, len(fixture)), *ranges)
                ),
                dual_bank_mmio=dual_bank_mmio,
                sim_layout=sim_layout,
                eeprom_layout=getattr(target.map_layout, "eeprom_persistence", None),
            )
            run_args = [
                base_verifier.RUN,
                f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k",
            ]
            if dual_bank_mmio:
                run_args.append(f"--memory-region={base_verifier.M95320_BASE:#x},8k")
                run_args.append(
                    f"--memory-region={DUAL_BANK_MMIO_BASE:#x},{dual_mmio_size // 1024}k"
                )
            run_args.append(elf)
            before = elf.read_bytes()
            result = base_verifier.run_command(
                run_args,
                timeout=180, env=environment)
            if elf.read_bytes() != before:
                raise VerificationError(f"{target.rom} map ELF changes during execution")
            records = base_verifier.read_pc_trace(trace)
        except base_verifier.VerificationError as error:
            raise VerificationError(f"{target.rom} map execution binding: {error}") from error
        return result, records, invokes

    warm_binding = None
    if dual_bank_mmio:
        warm_binding = _stock_warm_binding(target, composed_image)

    def coverage(records, invokes):
        covered_map = base_verifier.require_payload_coverage(
            records, fixture, map_parsed, invokes, composed_image=composed_image,
            adapter_layout=target.map_layout)
        _require_stock_warm_trace(records, target, warm_binding)
        return covered_map

    result, records, invokes = execute(output)
    try:
        covered = coverage(records, invokes)
    except (base_verifier.VerificationError, VerificationError) as error:
        raise VerificationError(f"{target.rom} map coverage: {error}") from error
    if marker not in result.stdout:
        raise VerificationError(f"{target.rom} map lacks its semantic PASS marker")
    layout = target.map_layout
    def entry(key):
        return min(layout.code_region_by_key[region].entry
                   for region in layout.assembly_unit_by_key[key].code_regions)
    adapter_entries = [entry(key) for key in base_verifier._adapter_coverage_units(layout)]
    omissions = [
        (
            "limiter",
            (
                ("if (!run_limiter_cases())", "if (!run_stock_warm_reinit_cases())")
                if warm_binding is not None and warm_binding["shared"]
                else ("if (!run_limiter_cases())",)
            ),
            f"uncovered entry {entry('startup_wrapper'):#010x}",
        ),
        ("adapters", ("if (!run_adapter_cases())",), f"uncovered entry {min(adapter_entries):#010x}"),
        ("selector", ("if (!run_selector_cases())",), f"uncovered entry {entry('selector_host'):#010x}"),
        ("feedback", ("if (!run_feedback_cases(&feedback_invocations))",), f"uncovered entry {entry('cruise_feedback_wrapper'):#010x}"),
    ]
    if layout.cruise_free is not None:
        omissions.append((
            "cruise-free",
            ("if (!run_cruise_free_cases())",),
            f"uncovered entry {layout.code_region_by_key['stationary_rx_wrapper'].entry:#010x}",
        ))
    if layout.eeprom_persistence is not None:
        omissions.append((
            "eeprom",
            ("if (!run_eeprom_cases())",),
            f"uncovered entry {layout.code_region_by_key['eeprom_task_wrapper'].entry:#010x}",
        ))
    if warm_binding is not None:
        omissions.append((
            "stock-warm",
            ("if (!run_stock_warm_reinit_cases())",),
            f"uncovered stock warm entry {warm_binding['entry']:#010x}",
        ))
    negatives = []
    for omitted, calls, expected_reason in omissions:
        negative_text = source_snapshot
        for call in calls:
            if negative_text.count(call) != 1:
                raise VerificationError(f"{target.rom} negative lacks its unique {omitted} call {call!r}")
            negative_text = negative_text.replace(call, call.replace("if (", "if (0 && ", 1))
        negative_source = build_dir / f"{target.rom.lower()}-no-{omitted}-cases.c"
        negative_source.write_text(negative_text, encoding="utf-8")
        negative_elf = build_dir / f"{target.rom.lower()}-no-{omitted}-cases.elf"
        negative_command = list(command)
        negative_command[negative_command.index("-o") + 1] = negative_elf
        negative_command[negative_command.index(source)] = negative_source
        base_verifier.run_command(negative_command, timeout=120)
        try:
            require_separate_storage(negative_elf, storage_regions)
        except (ELFStorageError, OSError) as error:
            raise VerificationError(f"{target.rom} negative ELF storage separation: {error}") from error
        negative, records, invokes = execute(negative_elf)
        if marker not in negative.stdout:
            raise VerificationError(f"{target.rom} negative loses its semantic PASS marker")
        try:
            coverage(records, invokes)
        except (base_verifier.VerificationError, VerificationError) as error:
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


def _run_harnesses(
    target,
    fixture,
    build_dir,
    *,
    map_parsed,
    composed_image,
    map_image=None,
    can_parsed=None,
    map_fixture=None,
):
    if map_fixture is None:
        map_fixture = fixture
    rom_object = _build_rom_object(target.rom, fixture, build_dir)
    map_rom_object = (
        rom_object
        if map_fixture is fixture
        else _build_rom_object(f"{target.rom}-map", map_fixture, build_dir)
    )
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
    has_p3 = (
        getattr(target.map_layout, "cruise_free", None) is not None
        and getattr(target.map_layout, "eeprom_persistence", None) is not None
    )
    if has_p3:
        warm_binding = _stock_warm_binding(target, composed_image, map_image=map_image)
        header_name = _write_p3_bindings_header(target, build_dir, warm_binding=warm_binding)
        map_defines += (
            "VERIFY_CRUISE_FREE",
            "VERIFY_EEPROM_PERSISTENCE",
            "TARGET_DUAL_BANK_MMIO",
            f'P3_BINDINGS_HEADER="{header_name}"',
        )

    markers = [
        _compile_and_run(
            target,
            "map-switching",
            map_source,
            map_rom_object if has_p3 else rom_object,
            (invoke,),
            build_dir,
            map_marker,
            defines=map_defines,
            map_parsed=map_parsed,
            fixture=map_fixture if has_p3 else fixture,
            composed_image=composed_image,
            dual_bank_mmio=has_p3,
        )
    ]
    if has_p3:
        for required_marker in (
            "VQ_SH_ELF_MAP_SWITCHING_CRUISE_FREE status=PASS ",
            "VQ_SH_ELF_MAP_SWITCHING_EEPROM status=PASS ",
            "VQ_SH_ELF_MAP_SWITCHING_WARM status=PASS ",
        ):
            if required_marker not in markers[0]:
                raise VerificationError(
                    f"{target.rom} map lacks {required_marker.strip()}"
                )
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
        map_composition, composition = _compose_and_lock(
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
        map_fixture, _, _ = _build_p3_map_fixture(target, composition)
        markers = _run_harnesses(target, fixture, build_dir,
                                 map_parsed=map_parsed,
                                 can_parsed=can_parsed, composed_image=composition.data,
                                 map_image=map_composition.data,
                                 map_fixture=map_fixture)
        if rom in ("1ME3B", "1EK7A"):
            import verify_ignition_consumers
            markers = (*markers, verify_ignition_consumers.verify(
                target, fixture, build_dir
            ))
        if getattr(target.map_layout, "variant", None) in SH7059_VARIANTS:
            import verify_sh7059_ram_test
            markers = (*markers, verify_sh7059_ram_test.verify(
                target, map_fixture, composition.data, build_dir
            ))
    for marker in markers:
        print(marker)
    instructions = map_audit.instructions + can_audit.instructions
    dynamic_cases = sum(
        _marker_cases(marker) for marker in markers
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
