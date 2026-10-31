#!/usr/bin/env python3
"""Load and verify exact stock-address profiles for relocated runtimes.

The registry has no implicit ROM selection. A caller must request one exact
ROM label, and every stock hook is verified against that ROM image before the
profile can participate in composition.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import map_switching_layout
from tools import rom_homology


DEFAULT_REGISTRY = Path(__file__).with_name("rom-address-profiles.toml")

PROFILE_BASE_FIELDS = frozenset(
    {
        "family",
        "layout_source",
        "rom_size",
        "rom_delta",
        "ram_delta",
        "free_rom_start",
        "free_rom_end",
        "injected_rom_start",
        "injected_rom_end",
        "free_ram_start",
        "free_ram_end",
        "injected_ram_start",
        "injected_ram_end",
        "map_variant",
        "telemetry_completion_variant",
        "capabilities",
        "telemetry_unavailable",
        "evidence",
    }
)

CAPABILITY_KEYS = frozenset(
    {"map_switching", "rolling_launch", "can_telemetry"}
)

DUAL_CVTC_MAP_FAMILY_KEYS = frozenset(
    {
        "over_run_fuel_hold",
        "over_run_fuel_cut",
        "over_run_fuel_restore",
        "over_run_fuel_intermediate_restore",
        "high_octane_timing_state",
        "high_detonation_timing_state",
        "cold_idle_ignition_timing",
        "idle_ignition_timing",
        "intake_cvtc_target",
        "exhaust_cvtc_target",
        "fuel_compensation_main",
        "rev_limit_fuel_cut",
        "rev_limit_throttle_cut",
    }
)

VQ37_MAP_VARIANTS = frozenset(
    {"sh7059-1nd", "sh7059-1me3b", "sh7058-jk78"}
)
# The SH7059 VQ37 images dispatch four 8x8 state-code ignition surfaces
# through a lookup of their own and place ECU RAM below 0xFFFF0000.
IGNITION_STATE_MAP_VARIANTS = frozenset({"sh7059-1nd", "sh7059-1me3b"})
# These coordinators also reach a gated half of three equal-byte surfaces
# through the hooked 16x16 literals.
GATED_IGNITION_MAP_VARIANTS = frozenset({"sh7059-1nd", "sh7058-jk78"})
SH7059_FAMILIES = frozenset({"sh7059_1nd", "sh7059_1me3b"})

VQ37_MAP_FAMILY_KEYS = frozenset(
    {
        "over_run_fuel_hold",
        "over_run_fuel_cut",
        "over_run_fuel_restore",
        "over_run_fuel_intermediate_restore",
        "ignition_surface_hot",
        "ignition_surface_cold",
        "cold_idle_ignition_timing",
        "idle_ignition_timing_default",
        "idle_ignition_timing_alternate",
        "fuel_compensation_main_default",
        "fuel_compensation_main_alternate",
        "rev_limit_fuel_cut_caps",
        "rev_limit_fuel_cut_curves",
        "rev_limit_throttle_cut",
    }
)

IGNITION_STATE_FAMILY_KEYS = map_switching_layout.IGNITION_STATE_FAMILY_KEYS
IGNITION_STATE_FAMILY_BYTES = 64

VQ37_1ND_MAP_FAMILY_KEYS = VQ37_MAP_FAMILY_KEYS | frozenset(
    IGNITION_STATE_FAMILY_KEYS
)

MAP_FAMILY_KEYS_BY_VARIANT = {
    "dual-cvtc": DUAL_CVTC_MAP_FAMILY_KEYS,
    "sh7059-1nd": VQ37_1ND_MAP_FAMILY_KEYS,
    "sh7059-1me3b": VQ37_1ND_MAP_FAMILY_KEYS,
    "sh7058-jk78": VQ37_MAP_FAMILY_KEYS,
}

DUAL_CVTC_MAP_HOOK_KEYS = frozenset(
    {
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
        "rev_fuel_cut_base",
        "rev_throttle_cluster_base",
        "rev_throttle_scalar_base",
        "cruise_feedback_serializer",
        "idle_ignition_lookup",
    }
)

VQ37_COMMON_MAP_HOOK_KEYS = frozenset(
    {
        "selector_host_call",
        "startup_initializer",
        "overrun_cut_lookup",
        "overrun_restore_lookup",
        "ignition_lookup_1",
        "ignition_lookup_2",
        "ignition_lookup_3",
        "ignition_lookup_4",
        "fuel_compensation_lookup_startup",
        "fuel_compensation_lookup_runtime",
        "idle_ignition_lookup_pool_1",
        "idle_ignition_lookup_pool_2",
        "rev_throttle_scalar_base",
        "cruise_feedback_serializer",
    }
)

VQ37_1ND_MAP_HOOK_KEYS = VQ37_COMMON_MAP_HOOK_KEYS | {
    "ignition_state_lookup",
    "rev_fuel_cut_caps_base",
    "rev_fuel_cut_activation_curve_base",
    "rev_fuel_cut_release_curve_base",
}

# Every declared 1ME3B lookup pool is redirected independently of reachability.
VQ37_1ME3B_MAP_HOOK_KEYS = VQ37_1ND_MAP_HOOK_KEYS | {
    "ignition_lookup_5",
    "ignition_state_lookup_earlier",
}

VQ37_JK78_MAP_HOOK_KEYS = VQ37_COMMON_MAP_HOOK_KEYS | {
    "rev_fuel_cut_caps_base",
    "rev_fuel_cut_release_cap_base",
    "rev_fuel_cut_curves_base",
}

MAP_HOOK_KEYS_BY_VARIANT = {
    "dual-cvtc": DUAL_CVTC_MAP_HOOK_KEYS,
    "sh7059-1nd": VQ37_1ND_MAP_HOOK_KEYS,
    "sh7059-1me3b": VQ37_1ME3B_MAP_HOOK_KEYS,
    "sh7058-jk78": VQ37_JK78_MAP_HOOK_KEYS,
}

DUAL_CVTC_MAP_SYMBOL_KEYS = frozenset(
    {
        "selector_function",
        "button_state",
        "diagnostic_state",
        "ascd_state",
        "startup_initializer",
        "dfco_lookup",
        "ignition_lookup",
        "fuel_compensation_lookup",
        "exhaust_lookup",
        "idle_ignition_lookup",
        "feedback_serializer",
        "feedback_status_byte",
        "throttle_container",
        "throttle_runtime",
    }
)

VQ37_MAP_SYMBOL_KEYS = frozenset(
    {
        "selector_function",
        "button_state",
        "diagnostic_state",
        "ascd_state",
        "startup_initializer",
        "dfco_lookup",
        "ignition_lookup",
        "fuel_compensation_lookup",
        "idle_ignition_lookup",
        "feedback_serializer",
        "feedback_status_byte",
        "ignition_coordinator_config_byte",
        "ignition_gated_surface_1",
        "ignition_gated_surface_2",
        "ignition_gated_surface_3",
    }
)

VQ37_1ME3B_MAP_SYMBOL_KEYS = VQ37_MAP_SYMBOL_KEYS - {
    "ignition_gated_surface_1",
    "ignition_gated_surface_2",
    "ignition_gated_surface_3",
}

MAP_SYMBOL_KEYS_BY_VARIANT = {
    "dual-cvtc": DUAL_CVTC_MAP_SYMBOL_KEYS,
    "sh7059-1nd": VQ37_MAP_SYMBOL_KEYS,
    "sh7059-1me3b": VQ37_1ME3B_MAP_SYMBOL_KEYS,
    "sh7058-jk78": VQ37_MAP_SYMBOL_KEYS,
}

ROLLING_HOOK_KEYS = frozenset(
    {
        "displaced_periodic_task",
        "selector_arbitration",
        "startup_state_clear",
        "primary_ignition_command",
        "feedback_arbitration",
    }
)

VQ37_ROLLING_HOOK_KEYS = ROLLING_HOOK_KEYS | {
    "fuel_cut_coordinator",
}

ROLLING_HOOK_KEYS_BY_VARIANT = {
    "dual-cvtc": ROLLING_HOOK_KEYS,
    "sh7059-1nd": VQ37_ROLLING_HOOK_KEYS,
    "sh7059-1me3b": VQ37_ROLLING_HOOK_KEYS,
    "sh7058-jk78": VQ37_ROLLING_HOOK_KEYS,
}

ROLLING_DIAGNOSTIC_KEYS = frozenset(
    {
        "phase_abort_reason",
        "flags",
        "map_mode_snapshot",
        "run_ticks",
        "rearm_ticks",
        "captured_rpm_native",
        "cut_rpm_native",
        "restore_rpm_native",
        "stock_effective_ignition_command",
    }
)

ROLLING_SYMBOL_KEYS = frozenset(
    {
        "periodic_task_slot",
        "periodic_task_table",
        "scheduler_task",
        "rpm",
        "vehicle_speed",
        "pedal",
        "coolant_index",
        "button_state",
        "ascd_state",
        "fuel_inhibit",
        "apc_mode",
        "apc_output",
        "unsigned_divide",
        "stock_ignition_consumer",
    }
)

VQ37_ROLLING_SYMBOL_KEYS = ROLLING_SYMBOL_KEYS | {
    "fuel_cut_coordinator",
    "fuel_inhibit_mask",
}

ROLLING_SYMBOL_KEYS_BY_VARIANT = {
    "dual-cvtc": ROLLING_SYMBOL_KEYS,
    "sh7059-1nd": VQ37_ROLLING_SYMBOL_KEYS,
    "sh7059-1me3b": VQ37_ROLLING_SYMBOL_KEYS,
    "sh7058-jk78": VQ37_ROLLING_SYMBOL_KEYS,
}

CAN_HOOK_KEYS = frozenset(
    {
        "coherent_snapshot_call",
        "knock_interval_latch",
        "knock_margin_latch",
        "startup_state_clear",
        "hcan1_sle1_vector",
        "hcan1_primary_init",
        "hcan1_recovery_init",
    }
)

CAN_SYMBOL_KEYS_COMMON = frozenset(
    {
        "coherent_snapshot",
        "knock_function",
        "knock_count",
        "knock_mask",
        "knock_selector_config",
        "knock_channel_primary",
        "knock_channel_alternate",
        "knock_metric_base",
        "knock_threshold_base",
        "hcan1_init",
        "stock_sle1_isr",
        "feedback_config_record_address",
        "feedback_config_record_value",
        "feedback_dispatch_literal",
        "feedback_payload_base_literal",
        "feedback_payload_base",
        "feedback_payload_offset",
        "feedback_status_byte",
        "mailbox_record_address",
        "mailbox_record_stock",
        "occupied_mailbox_record_address",
        "occupied_mailbox_record_stock",
        "mailbox_index",
        "mailbox_data",
        "mailbox_mask",
    }
)

CAN_COMPLETION_VARIANTS = frozenset({"mailbox26-tail-chain"})

# The dual-CVTC profiles also bind the stock mailbox-28 completion helper.
CAN_SYMBOL_KEYS_BY_VARIANT = {
    "dual-cvtc": CAN_SYMBOL_KEYS_COMMON | {"stock_isr_helper"},
    "sh7059-1nd": CAN_SYMBOL_KEYS_COMMON,
    "sh7059-1me3b": CAN_SYMBOL_KEYS_COMMON,
    "sh7058-jk78": CAN_SYMBOL_KEYS_COMMON,
}

EVIDENCE_KEYS = frozenset(
    {"free_rom", "free_ram", "maps", "rolling", "can", "telemetry"}
)

EXTRA_STORAGE_KEYS = frozenset(
    {"adapter_start", "adapter_end", "pointer_table", "copies"}
)

IGNITION_STATE_STORAGE_KEYS = frozenset(
    {"adapter_start", "adapter_end", *IGNITION_STATE_FAMILY_KEYS}
)
IGNITION_STATE_FAMILY_STORAGE_KEYS = frozenset({"pointer_table", "copies"})
IGNITION_STATE_ADAPTER_BYTES = 0x80
# The SH7059 state-code ignition adapter follows the 0x80-byte canonical slot
# 0x000D5000..0x000D5080, which the VQ37VHR layouts leave unused.
IGNITION_STATE_ADAPTER_CANONICAL = 0x000D5080
UNREFERENCED_ROUTINE_KEYS = frozenset({"start", "end"})


class AddressProfileError(ValueError):
    """Raised when an exact address profile is incomplete or inconsistent."""


@dataclass(frozen=True, order=True)
class AddressRange:
    start: int
    end: int

    def __post_init__(self):
        if self.start < 0 or self.end <= self.start:
            raise AddressProfileError(
                f"invalid half-open range [{self.start:#x}, {self.end:#x})"
            )

    @property
    def size(self):
        return self.end - self.start

    def contains(self, other):
        return self.start <= other.start and other.end <= self.end

    def overlaps(self, other):
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True)
class HookBinding:
    key: str
    address: int
    stock: int
    base: int
    replacement: int


@dataclass(frozen=True)
class DiagnosticBinding:
    key: str
    did: int
    pointer_address: int
    target: int
    width: int


@dataclass(frozen=True)
class ExtraCvtcStorage:
    adapter: AddressRange
    pointer_table: int
    copies: tuple[int, ...]


@dataclass(frozen=True)
class FamilyStorage:
    key: str
    pointer_table: int
    copies: tuple[int, ...]


@dataclass(frozen=True)
class IgnitionStateStorage:
    adapter: AddressRange
    families: tuple[FamilyStorage, ...]

    @property
    def family_by_key(self):
        return {item.key: item for item in self.families}

    @property
    def ranges(self):
        result = [self.adapter]
        for item in self.families:
            result.append(
                AddressRange(item.pointer_table, item.pointer_table + 20)
            )
            result.extend(
                AddressRange(address, address + IGNITION_STATE_FAMILY_BYTES)
                for address in item.copies
            )
        return tuple(result)


@dataclass(frozen=True)
class Capabilities:
    map_switching: bool
    rolling_launch: bool
    can_telemetry: bool


@dataclass(frozen=True)
class AddressProfile:
    rom: str
    family: str
    layout_source: str
    rom_size: int
    rom_delta: int
    ram_delta: int
    free_rom: AddressRange
    injected_rom: AddressRange
    free_ram: AddressRange
    injected_ram: AddressRange
    map_variant: str
    telemetry_completion_variant: str
    capabilities: Capabilities
    map_families: tuple[tuple[str, int], ...]
    map_hooks: tuple[HookBinding, ...]
    map_symbols: tuple[tuple[str, int], ...]
    rolling_hooks: tuple[HookBinding, ...]
    rolling_diagnostics: tuple[DiagnosticBinding, ...]
    rolling_symbols: tuple[tuple[str, int], ...]
    can_hooks: tuple[HookBinding, ...]
    can_symbols: tuple[tuple[str, int], ...]
    telemetry_sources: tuple[tuple[str, int], ...]
    telemetry_unavailable: tuple[str, ...]
    telemetry_zero_source: int | None
    extra_cvtc_storage: ExtraCvtcStorage | None
    ignition_state_storage: IgnitionStateStorage | None
    evidence: tuple[tuple[str, str], ...]
    ignition_unreferenced_routine: AddressRange | None = None

    @property
    def map_family_by_key(self):
        return dict(self.map_families)

    @property
    def map_hook_by_key(self):
        return {item.key: item for item in self.map_hooks}

    @property
    def map_symbol_by_key(self):
        return dict(self.map_symbols)

    @property
    def rolling_hook_by_key(self):
        return {item.key: item for item in self.rolling_hooks}

    @property
    def rolling_diagnostic_by_key(self):
        return {item.key: item for item in self.rolling_diagnostics}

    @property
    def rolling_symbol_by_key(self):
        return dict(self.rolling_symbols)

    @property
    def can_hook_by_key(self):
        return {item.key: item for item in self.can_hooks}

    @property
    def can_symbol_by_key(self):
        return dict(self.can_symbols)

    @property
    def telemetry_source_by_name(self):
        return dict(self.telemetry_sources)

    @property
    def enabled_capabilities(self):
        return frozenset(
            key
            for key in CAPABILITY_KEYS
            if getattr(self.capabilities, key)
        )


def _require_table(row, expected, context):
    if not isinstance(row, dict):
        raise AddressProfileError(f"{context}: expected a TOML table")
    actual = set(row)
    if actual != set(expected):
        raise AddressProfileError(
            f"{context}: fields differ; missing={sorted(set(expected) - actual)}; "
            f"extra={sorted(actual - set(expected))}"
        )


def _uint(value, context, *, maximum=0xFFFFFFFF):
    if type(value) is not int or not 0 <= value <= maximum:
        raise AddressProfileError(
            f"{context}: expected an integer in 0x0..{maximum:x}"
        )
    return value


def _sint(value, context, *, minimum=-0xFFFFFFFF, maximum=0xFFFFFFFF):
    if type(value) is not int or not minimum <= value <= maximum:
        raise AddressProfileError(
            f"{context}: expected an integer in {minimum}..{maximum}"
        )
    return value


def _capabilities(row, context):
    _require_table(row, CAPABILITY_KEYS, context)
    if any(type(value) is not bool for value in row.values()):
        raise AddressProfileError(f"{context}: capability values must be booleans")
    result = Capabilities(**row)
    if not result.map_switching and result.rolling_launch:
        raise AddressProfileError(
            f"{context}: Rolling Launch requires Map Switching"
        )
    if not result.map_switching and not result.can_telemetry:
        raise AddressProfileError(f"{context}: profile enables no runtime component")
    return result


def _address_table(row, expected, context):
    _require_table(row, expected, context)
    return tuple(
        (key, _uint(row[key], f"{context}.{key}"))
        for key in sorted(expected)
    )


def _hooks(row, expected, context, *, chained):
    _require_table(row, expected, context)
    bindings = []
    length = 4 if chained else 3
    for key in sorted(expected):
        values = row[key]
        if not isinstance(values, list) or len(values) != length:
            raise AddressProfileError(
                f"{context}.{key}: expected {length} integers"
            )
        values = tuple(
            _uint(value, f"{context}.{key}[{index}]")
            for index, value in enumerate(values)
        )
        if chained:
            address, stock, base, replacement = values
        else:
            address, stock, replacement = values
            base = stock
        if address % 4:
            raise AddressProfileError(f"{context}.{key}: hook is not aligned")
        bindings.append(HookBinding(key, address, stock, base, replacement))
    addresses = [item.address for item in bindings]
    if len(addresses) != len(set(addresses)):
        duplicates = sorted(
            address for address in set(addresses) if addresses.count(address) > 1
        )
        raise AddressProfileError(
            f"{context}: duplicate hook addresses {duplicates}"
        )
    return tuple(bindings)


def _diagnostics(row, context):
    _require_table(row, ROLLING_DIAGNOSTIC_KEYS, context)
    result = []
    for key in sorted(ROLLING_DIAGNOSTIC_KEYS):
        values = row[key]
        if not isinstance(values, list) or len(values) != 4:
            raise AddressProfileError(
                f"{context}.{key}: expected DID, pointer, target, and width"
            )
        did, pointer, target, width = (
            _uint(value, f"{context}.{key}[{index}]")
            for index, value in enumerate(values)
        )
        if width != 2 or pointer % 4 or not 0x1000 <= did <= 0xFFFF:
            raise AddressProfileError(f"{context}.{key}: invalid DID binding")
        result.append(DiagnosticBinding(key, did, pointer, target, width))
    if len({item.did for item in result}) != len(result):
        raise AddressProfileError(f"{context}: duplicate DIDs")
    if len({item.pointer_address for item in result}) != len(result):
        raise AddressProfileError(f"{context}: duplicate pointer addresses")
    return tuple(result)


def _extra_storage(row, context):
    _require_table(row, EXTRA_STORAGE_KEYS, context)
    copies = row["copies"]
    if (
        not isinstance(copies, list)
        or len(copies) != 4
        or len(set(copies)) != len(copies)
    ):
        raise AddressProfileError(f"{context}.copies: expected four addresses")
    result = ExtraCvtcStorage(
        adapter=AddressRange(
            _uint(row["adapter_start"], f"{context}.adapter_start"),
            _uint(row["adapter_end"], f"{context}.adapter_end"),
        ),
        pointer_table=_uint(row["pointer_table"], f"{context}.pointer_table"),
        copies=tuple(
            _uint(value, f"{context}.copies[{index}]")
            for index, value in enumerate(copies)
        ),
    )
    if result.adapter.size != 0x40 or result.pointer_table % 4:
        raise AddressProfileError(f"{context}: invalid adapter or pointer table")
    if any(address % 0x100 for address in result.copies):
        raise AddressProfileError(f"{context}: copies must be 256-byte aligned")
    return result


def _unreferenced_routine(row, context):
    _require_table(row, UNREFERENCED_ROUTINE_KEYS, context)
    result = AddressRange(
        _uint(row["start"], f"{context}.start"),
        _uint(row["end"], f"{context}.end"),
    )
    if result.size <= 0 or result.start % 2 or result.end % 2:
        raise AddressProfileError(f"{context}: invalid routine range")
    return result


def _ignition_state_storage(row, context):
    _require_table(row, IGNITION_STATE_STORAGE_KEYS, context)
    families = []
    for key in IGNITION_STATE_FAMILY_KEYS:
        family_context = f"{context}.{key}"
        family_row = row[key]
        _require_table(
            family_row, IGNITION_STATE_FAMILY_STORAGE_KEYS, family_context
        )
        copies = family_row["copies"]
        if (
            not isinstance(copies, list)
            or len(copies) != 4
            or len(set(copies)) != len(copies)
        ):
            raise AddressProfileError(
                f"{family_context}.copies: expected four addresses"
            )
        families.append(FamilyStorage(
            key=key,
            pointer_table=_uint(
                family_row["pointer_table"], f"{family_context}.pointer_table"
            ),
            copies=tuple(
                _uint(value, f"{family_context}.copies[{index}]")
                for index, value in enumerate(copies)
            ),
        ))
    result = IgnitionStateStorage(
        adapter=AddressRange(
            _uint(row["adapter_start"], f"{context}.adapter_start"),
            _uint(row["adapter_end"], f"{context}.adapter_end"),
        ),
        families=tuple(families),
    )
    if result.adapter.size != IGNITION_STATE_ADAPTER_BYTES:
        raise AddressProfileError(f"{context}: invalid adapter range")
    for item in result.families:
        if item.pointer_table % 4:
            raise AddressProfileError(
                f"{context}.{item.key}: pointer table is not four-byte aligned"
            )
        if any(
            address % IGNITION_STATE_FAMILY_BYTES for address in item.copies
        ):
            raise AddressProfileError(
                f"{context}.{item.key}: copies must be 64-byte aligned"
            )
    return result


def _telemetry_source_keys():
    manifest = can_telemetry_profile.load_manifest()
    fields = list(manifest.fields)
    fields.extend(field for item in manifest.contexts for field in item.fields)
    return frozenset(field.name for field in fields if field.kind == "ecu_ram")


def _profile_fields(capabilities, map_variant, telemetry_unavailable):
    expected = set(PROFILE_BASE_FIELDS)
    if capabilities.map_switching:
        expected.update({"map_families", "map_hooks", "map_symbols"})
    if capabilities.rolling_launch:
        expected.update(
            {"rolling_hooks", "rolling_diagnostics", "rolling_symbols"}
        )
    if capabilities.map_switching or capabilities.can_telemetry:
        expected.add("can_symbols")
    if capabilities.can_telemetry:
        expected.update({"can_hooks", "telemetry_sources"})
    if map_variant == "dual-cvtc":
        expected.add("extra_cvtc_storage")
    if map_variant in IGNITION_STATE_MAP_VARIANTS:
        expected.add("ignition_state_storage")
    if map_variant == "sh7059-1me3b":
        expected.add("ignition_unreferenced_routine")
    if telemetry_unavailable:
        expected.add("telemetry_zero_source")
    return frozenset(expected)


def _telemetry_unavailable(value, expected, context):
    if (
        not isinstance(value, list)
        or any(not isinstance(item, str) or not item for item in value)
        or len(value) != len(set(value))
    ):
        raise AddressProfileError(
            f"{context}: expected a list of unique telemetry field names"
        )
    unknown = set(value) - set(expected)
    if unknown:
        raise AddressProfileError(
            f"{context}: unknown telemetry fields {sorted(unknown)}"
        )
    return tuple(sorted(value))


def _parse_profile(rom, row, context):
    if not isinstance(row, dict):
        raise AddressProfileError(f"{context}: expected a TOML table")
    missing = PROFILE_BASE_FIELDS - set(row)
    if missing:
        raise AddressProfileError(
            f"{context}: fields differ; missing={sorted(missing)}; extra=[]"
        )
    capabilities = _capabilities(
        row["capabilities"], f"{context}.capabilities"
    )
    telemetry_keys = _telemetry_source_keys()
    unavailable = _telemetry_unavailable(
        row["telemetry_unavailable"],
        telemetry_keys,
        f"{context}.telemetry_unavailable",
    )
    map_variant = row["map_variant"]
    if map_variant not in MAP_FAMILY_KEYS_BY_VARIANT:
        raise AddressProfileError(
            f"{context}.map_variant: unsupported value {map_variant!r}"
        )
    completion_variant = row["telemetry_completion_variant"]
    if completion_variant not in CAN_COMPLETION_VARIANTS:
        raise AddressProfileError(
            f"{context}.telemetry_completion_variant: unsupported value "
            f"{completion_variant!r}"
        )
    _require_table(
        row,
        _profile_fields(capabilities, map_variant, unavailable),
        context,
    )
    scalar_ints = {
        key: _uint(row[key], f"{context}.{key}")
        for key in (
            "rom_size",
            "free_rom_start",
            "free_rom_end",
            "injected_rom_start",
            "injected_rom_end",
            "free_ram_start",
            "free_ram_end",
            "injected_ram_start",
            "injected_ram_end",
        )
    }
    scalar_ints["rom_delta"] = _sint(
        row["rom_delta"], f"{context}.rom_delta"
    )
    scalar_ints["ram_delta"] = _sint(
        row["ram_delta"], f"{context}.ram_delta"
    )
    for key in (
        "family",
        "layout_source",
        "map_variant",
        "telemetry_completion_variant",
    ):
        if not isinstance(row[key], str) or not row[key].strip():
            raise AddressProfileError(f"{context}.{key}: expected nonempty text")

    evidence = row["evidence"]
    evidence_keys = (
        EVIDENCE_KEYS
        if capabilities.rolling_launch
        else EVIDENCE_KEYS - {"rolling"}
    )
    _require_table(evidence, evidence_keys, f"{context}.evidence")
    for key, value in evidence.items():
        if not isinstance(value, str) or not value.strip():
            raise AddressProfileError(
                f"{context}.evidence.{key}: expected nonempty text"
            )

    profile = AddressProfile(
        rom=rom,
        family=row["family"],
        layout_source=row["layout_source"],
        rom_size=scalar_ints["rom_size"],
        rom_delta=scalar_ints["rom_delta"],
        ram_delta=scalar_ints["ram_delta"],
        free_rom=AddressRange(
            scalar_ints["free_rom_start"], scalar_ints["free_rom_end"]
        ),
        injected_rom=AddressRange(
            scalar_ints["injected_rom_start"],
            scalar_ints["injected_rom_end"],
        ),
        free_ram=AddressRange(
            scalar_ints["free_ram_start"], scalar_ints["free_ram_end"]
        ),
        injected_ram=AddressRange(
            scalar_ints["injected_ram_start"],
            scalar_ints["injected_ram_end"],
        ),
        map_variant=map_variant,
        telemetry_completion_variant=completion_variant,
        capabilities=capabilities,
        map_families=(
            _address_table(
                row["map_families"],
                MAP_FAMILY_KEYS_BY_VARIANT[map_variant],
                f"{context}.map_families",
            )
            if capabilities.map_switching
            else ()
        ),
        map_hooks=(
            _hooks(
                row["map_hooks"],
                MAP_HOOK_KEYS_BY_VARIANT[map_variant],
                f"{context}.map_hooks",
                chained=False,
            )
            if capabilities.map_switching
            else ()
        ),
        map_symbols=(
            _address_table(
                row["map_symbols"],
                MAP_SYMBOL_KEYS_BY_VARIANT[map_variant],
                f"{context}.map_symbols",
            )
            if capabilities.map_switching
            else ()
        ),
        rolling_hooks=(
            _hooks(
                row["rolling_hooks"],
                ROLLING_HOOK_KEYS_BY_VARIANT[map_variant],
                f"{context}.rolling_hooks",
                chained=True,
            )
            if capabilities.rolling_launch
            else ()
        ),
        rolling_diagnostics=(
            _diagnostics(
                row["rolling_diagnostics"],
                f"{context}.rolling_diagnostics",
            )
            if capabilities.rolling_launch
            else ()
        ),
        rolling_symbols=(
            _address_table(
                row["rolling_symbols"],
                ROLLING_SYMBOL_KEYS_BY_VARIANT[map_variant],
                f"{context}.rolling_symbols",
            )
            if capabilities.rolling_launch
            else ()
        ),
        can_hooks=(
            _hooks(
                row["can_hooks"],
                CAN_HOOK_KEYS,
                f"{context}.can_hooks",
                chained=True,
            )
            if capabilities.can_telemetry
            else ()
        ),
        can_symbols=(
            _address_table(
                row["can_symbols"],
                CAN_SYMBOL_KEYS_BY_VARIANT[map_variant],
                f"{context}.can_symbols",
            )
            if capabilities.map_switching or capabilities.can_telemetry
            else ()
        ),
        telemetry_sources=(
            _address_table(
                row["telemetry_sources"],
                telemetry_keys - set(unavailable),
                f"{context}.telemetry_sources",
            )
            if capabilities.can_telemetry
            else ()
        ),
        telemetry_unavailable=unavailable,
        telemetry_zero_source=(
            _uint(
                row["telemetry_zero_source"],
                f"{context}.telemetry_zero_source",
            )
            if unavailable
            else None
        ),
        extra_cvtc_storage=(
            _extra_storage(
                row["extra_cvtc_storage"],
                f"{context}.extra_cvtc_storage",
            )
            if map_variant == "dual-cvtc"
            else None
        ),
        ignition_state_storage=(
            _ignition_state_storage(
                row["ignition_state_storage"],
                f"{context}.ignition_state_storage",
            )
            if map_variant in IGNITION_STATE_MAP_VARIANTS
            else None
        ),
        evidence=tuple(sorted(evidence.items())),
        ignition_unreferenced_routine=(
            _unreferenced_routine(
                row["ignition_unreferenced_routine"],
                f"{context}.ignition_unreferenced_routine",
            )
            if map_variant == "sh7059-1me3b"
            else None
        ),
    )
    _validate_structure(profile)
    return profile


def _rebased(value, delta):
    return value + delta


def _map_family_sources(profile):
    if profile.map_variant == "dual-cvtc":
        result = {
            key: key
            for key in DUAL_CVTC_MAP_FAMILY_KEYS
            if key != "intake_cvtc_target"
        }
        result["intake_cvtc_target"] = "exhaust_cvtc_target"
        return result
    if profile.map_variant in VQ37_MAP_VARIANTS:
        return {
            "over_run_fuel_hold": "over_run_fuel_hold",
            "over_run_fuel_cut": "over_run_fuel_cut",
            "over_run_fuel_restore": "over_run_fuel_restore",
            "over_run_fuel_intermediate_restore": (
                "over_run_fuel_intermediate_restore"
            ),
            "ignition_surface_hot": "high_octane_timing_state",
            "ignition_surface_cold": "high_detonation_timing_state",
            "cold_idle_ignition_timing": "cold_idle_ignition_timing",
            "idle_ignition_timing_default": "idle_ignition_timing",
            "idle_ignition_timing_alternate": "idle_ignition_timing",
            "fuel_compensation_main_default": "fuel_compensation_main",
            "fuel_compensation_main_alternate": "fuel_compensation_main",
            "rev_limit_throttle_cut": "rev_limit_throttle_cut",
        }
    raise AddressProfileError(
        f"{profile.rom}: unsupported map variant {profile.map_variant!r}"
    )


def _validate_extra_storage(profile, telemetry_layout):
    extra = profile.extra_cvtc_storage
    if profile.map_variant != "dual-cvtc":
        if extra is not None:
            raise AddressProfileError(
                f"{profile.rom}: unexpected extra CVTC storage"
            )
        return
    if extra is None:
        raise AddressProfileError(
            f"{profile.rom}: missing extra CVTC storage"
        )
    if extra.adapter.start != (
        telemetry_layout.reserved_rom.start + profile.rom_delta
    ):
        raise AddressProfileError(
            f"{profile.rom}: extra exhaust adapter does not start at the "
            "future reserve"
        )
    extra_ranges = [
        extra.adapter,
        AddressRange(extra.pointer_table, extra.pointer_table + 20),
        *(AddressRange(address, address + 0x100) for address in extra.copies),
    ]
    for span in extra_ranges:
        if not profile.injected_rom.contains(span):
            raise AddressProfileError(
                f"{profile.rom}: extra exhaust storage lies outside injected ROM"
            )
    for index, left in enumerate(extra_ranges):
        for right in extra_ranges[index + 1 :]:
            if left.overlaps(right):
                raise AddressProfileError(
                    f"{profile.rom}: extra exhaust storage overlaps"
                )


def _validate_ignition_state_storage(profile):
    storage = profile.ignition_state_storage
    if profile.map_variant not in IGNITION_STATE_MAP_VARIANTS:
        if storage is not None:
            raise AddressProfileError(
                f"{profile.rom}: unexpected ignition state storage"
            )
        return
    if storage is None:
        raise AddressProfileError(
            f"{profile.rom}: missing ignition state storage"
        )
    if storage.adapter.start != _rebased(
        IGNITION_STATE_ADAPTER_CANONICAL, profile.rom_delta
    ):
        raise AddressProfileError(
            f"{profile.rom}: ignition state adapter does not follow the "
            "fuel-cut coordinator wrapper"
        )
    ranges = storage.ranges
    for span in ranges:
        if not profile.injected_rom.contains(span):
            raise AddressProfileError(
                f"{profile.rom}: ignition state storage lies outside "
                "injected ROM"
            )
    for index, left in enumerate(ranges):
        for right in ranges[index + 1 :]:
            if left.overlaps(right):
                raise AddressProfileError(
                    f"{profile.rom}: ignition state storage overlaps"
                )


def _validate_map_bindings(profile, map_layout):
    family = profile.map_family_by_key
    canonical_families = map_layout.family_by_key
    spans = []
    for key, source_key in _map_family_sources(profile).items():
        source = canonical_families[source_key]
        span = AddressRange(family[key], family[key] + source.byte_length)
        if span.end > profile.rom_size:
            raise AddressProfileError(f"{profile.rom}.{key}: map exceeds ROM")
        spans.append(span)
    if profile.map_variant in VQ37_MAP_VARIANTS:
        for key, byte_length in (
            ("rev_limit_fuel_cut_caps", 4),
            ("rev_limit_fuel_cut_curves", 32),
        ):
            address = family[key]
            span = AddressRange(address, address + byte_length)
            if span.end > profile.rom_size:
                raise AddressProfileError(
                    f"{profile.rom}.{key}: map exceeds ROM"
                )
            spans.append(span)
    if profile.map_variant in IGNITION_STATE_MAP_VARIANTS:
        for key in IGNITION_STATE_FAMILY_KEYS:
            span = AddressRange(
                family[key], family[key] + IGNITION_STATE_FAMILY_BYTES
            )
            if span.end > profile.rom_size:
                raise AddressProfileError(
                    f"{profile.rom}.{key}: map exceeds ROM"
                )
            spans.append(span)
    for index, left in enumerate(spans):
        for right in spans[index + 1 :]:
            if left.overlaps(right):
                raise AddressProfileError(f"{profile.rom}: stock maps overlap")

    code = map_layout.code_region_by_key
    rom_delta = profile.rom_delta
    ram_delta = profile.ram_delta
    common = {
        "selector_host_call": _rebased(code["selector_host"].entry, rom_delta),
        "startup_initializer": _rebased(
            code["startup_wrapper"].entry, rom_delta
        ),
        "overrun_cut_lookup": _rebased(
            code["full_dfco_adapter"].entry, rom_delta
        ),
        "overrun_restore_lookup": _rebased(
            code["full_dfco_adapter"].entry, rom_delta
        ),
        "cruise_feedback_serializer": _rebased(
            code["cruise_feedback_wrapper"].entry, rom_delta
        ),
    }
    if profile.map_variant == "dual-cvtc":
        extra = profile.extra_cvtc_storage
        expected = common | {
            "ignition_lookup_knock": _rebased(
                code["ignition_adapter"].entry, rom_delta
            ),
            "ignition_lookup_primary_a": _rebased(
                code["ignition_adapter"].entry, rom_delta
            ),
            "ignition_lookup_primary_b": _rebased(
                code["ignition_adapter"].entry, rom_delta
            ),
            "fuel_compensation_lookup_startup": _rebased(
                code["fuel_compensation_adapter"].entry, rom_delta
            ),
            "fuel_compensation_lookup_runtime": _rebased(
                code["fuel_compensation_adapter"].entry, rom_delta
            ),
            "intake_cvtc_target_lookup": _rebased(
                code["cvtc_target_adapter"].entry, rom_delta
            ),
            "exhaust_cvtc_target_lookup": extra.adapter.start,
            "rev_fuel_cut_base": _rebased(
                map_layout.ram.fuel_cut_shadow.start, ram_delta
            ),
            "rev_throttle_cluster_base": _rebased(
                map_layout.ram.throttle_shadow.start, ram_delta
            ),
            "rev_throttle_scalar_base": _rebased(
                map_layout.ram.throttle_shadow.start
                + map_layout.ram.throttle_selected_offset,
                ram_delta,
            ),
            "idle_ignition_lookup": _rebased(
                code["idle_ignition_adapter"].entry, rom_delta
            ),
        }
    else:
        expected = common | {
            **{
                key: _rebased(code["ignition_adapter"].entry, rom_delta)
                for key in MAP_HOOK_KEYS_BY_VARIANT[profile.map_variant]
                if key.startswith("ignition_lookup_")
            },
            "fuel_compensation_lookup_startup": _rebased(
                code["fuel_compensation_adapter"].entry, rom_delta
            ),
            "fuel_compensation_lookup_runtime": _rebased(
                code["fuel_compensation_adapter"].entry, rom_delta
            ),
            "idle_ignition_lookup_pool_1": _rebased(
                code["idle_ignition_adapter"].entry, rom_delta
            ),
            "idle_ignition_lookup_pool_2": _rebased(
                code["cvtc_target_adapter"].entry, rom_delta
            ),
            "rev_fuel_cut_caps_base": _rebased(
                map_layout.ram.fuel_cut_shadow.start, ram_delta
            ),
            "rev_throttle_scalar_base": _rebased(
                map_layout.ram.throttle_shadow.start + 0x18, ram_delta
            ),
        }
        fuel_curve_shadow = _rebased(
            map_layout.ram.fuel_cut_shadow.start + 4, ram_delta
        )
        if profile.map_variant in IGNITION_STATE_MAP_VARIANTS:
            expected.update({
                "ignition_state_lookup": (
                    profile.ignition_state_storage.adapter.start
                ),
                "rev_fuel_cut_activation_curve_base": fuel_curve_shadow,
                "rev_fuel_cut_release_curve_base": fuel_curve_shadow + 0x10,
            })
            if profile.map_variant == "sh7059-1me3b":
                expected["ignition_state_lookup_earlier"] = (
                    profile.ignition_state_storage.adapter.start
                )
        else:
            expected["rev_fuel_cut_curves_base"] = fuel_curve_shadow
            expected["rev_fuel_cut_release_cap_base"] = _rebased(
                map_layout.ram.fuel_cut_shadow.start + 2, ram_delta
            )
    for key, replacement in expected.items():
        binding = profile.map_hook_by_key[key]
        if binding.replacement != replacement or binding.base != binding.stock:
            raise AddressProfileError(f"{profile.rom}.{key}: map hook chain differs")


def _validate_can_bindings(profile, telemetry_layout):
    if not profile.capabilities.can_telemetry:
        return
    rom_delta = profile.rom_delta
    telemetry_code = telemetry_layout.code_region_by_key
    expected = {
        "coherent_snapshot_call": _rebased(
            telemetry_code["main_wrapper"].entry, rom_delta
        ),
        "knock_interval_latch": _rebased(
            telemetry_code["knock_wrapper"].entry, rom_delta
        ),
        "knock_margin_latch": _rebased(
            telemetry_code["knock_margin_wrapper"].entry, rom_delta
        ),
        "startup_state_clear": _rebased(
            telemetry_code["startup_wrapper"].entry, rom_delta
        ),
        "hcan1_sle1_vector": _rebased(
            telemetry_code["sle1_isr"].entry, rom_delta
        ),
        "hcan1_primary_init": _rebased(
            telemetry_code["hcan1_init_wrapper"].entry, rom_delta
        ),
        "hcan1_recovery_init": _rebased(
            telemetry_code["hcan1_init_wrapper"].entry, rom_delta
        ),
    }
    hooks = profile.can_hook_by_key
    for key, replacement in expected.items():
        if hooks[key].replacement != replacement:
            raise AddressProfileError(
                f"{profile.rom}.{key}: CAN replacement differs"
            )
    startup_base = profile.map_hook_by_key["startup_initializer"].replacement
    if hooks["startup_state_clear"].base != startup_base:
        raise AddressProfileError(f"{profile.rom}: CAN startup hook chain is open")
    for key in CAN_HOOK_KEYS - {"startup_state_clear"}:
        if hooks[key].base != hooks[key].stock:
            raise AddressProfileError(
                f"{profile.rom}.{key}: unexpected CAN base hook"
            )

    symbols = profile.can_symbol_by_key
    contracts = {
        "mailbox26-tail-chain": (26, 0xFFFFDC48, 0x0400),
    }
    mailbox_index, mailbox_data, mailbox_mask = contracts[
        profile.telemetry_completion_variant
    ]
    feedback_record = (
        0xA308AA20
        if profile.family in SH7059_FAMILIES
        else 0x0308AA20
    )
    if (
        symbols["mailbox_index"] != mailbox_index
        or symbols["mailbox_data"] != mailbox_data
        or symbols["mailbox_mask"] != mailbox_mask
        or symbols["mailbox_record_stock"] != 0x05000000
        or symbols["occupied_mailbox_record_stock"] != 0x04000000
        or symbols["feedback_config_record_value"] != feedback_record
    ):
        raise AddressProfileError(f"{profile.rom}: mailbox contract differs")
    if (
        symbols["feedback_status_byte"]
        != profile.map_symbol_by_key["feedback_status_byte"]
        or symbols["feedback_status_byte"]
        != symbols["feedback_payload_base"]
        + symbols["feedback_payload_offset"]
        + 5
    ):
        raise AddressProfileError(f"{profile.rom}: feedback status binding differs")

    manifest = can_telemetry_profile.load_manifest()
    widths = {
        field.name: field.width
        for field in tuple(manifest.fields)
        + tuple(
            field for context in manifest.contexts for field in context.fields
        )
        if field.kind == "ecu_ram"
    }
    telemetry = profile.telemetry_source_by_name
    telemetry_addresses = list(telemetry.values())
    if len(telemetry_addresses) != len(set(telemetry_addresses)):
        raise AddressProfileError(f"{profile.rom}: duplicate telemetry sources")
    if profile.family in SH7059_FAMILIES:
        lower_bound, upper_bound = 0xFFFE8000, 0xFFFF0000
    else:
        lower_bound, upper_bound = 0xFFFF0000, 0xFFFFC000
    for key, address in telemetry.items():
        span = AddressRange(address, address + widths[key])
        if (
            address < lower_bound
            or span.end > upper_bound
            or span.overlaps(profile.free_ram)
        ):
            raise AddressProfileError(
                f"{profile.rom}.{key}: telemetry source enters injected RAM"
            )
    if profile.telemetry_unavailable:
        active_reserved = AddressRange(
            telemetry_layout.ram.active_reserved.start + profile.ram_delta,
            telemetry_layout.ram.active_reserved.end + profile.ram_delta,
        )
        zero_width = max(widths[key] for key in profile.telemetry_unavailable)
        zero_span = AddressRange(
            profile.telemetry_zero_source,
            profile.telemetry_zero_source + zero_width,
        )
        if not active_reserved.contains(zero_span):
            raise AddressProfileError(
                f"{profile.rom}: unavailable telemetry zero source is not "
                "cleared runtime RAM"
            )
    elif profile.telemetry_zero_source is not None:
        raise AddressProfileError(
            f"{profile.rom}: unexpected telemetry zero source"
        )


def _validate_structure(profile):
    contracts = {
        "dual-cvtc": (
            "sh7058_8mfk",
            0x100000,
            "mailbox26-tail-chain",
            Capabilities(True, False, True),
        ),
        "sh7059-1nd": (
            "sh7059_1nd",
            0x180000,
            "mailbox26-tail-chain",
            Capabilities(True, False, True),
        ),
        "sh7059-1me3b": (
            "sh7059_1me3b",
            0x180000,
            "mailbox26-tail-chain",
            Capabilities(True, False, True),
        ),
        "sh7058-jk78": (
            "sh7058_jk78c",
            0x100000,
            "mailbox26-tail-chain",
            Capabilities(True, False, True),
        ),
    }
    family, rom_size, can_variant, capabilities = contracts[profile.map_variant]
    if profile.layout_source != "JK08A" or profile.family != family:
        raise AddressProfileError(
            f"{profile.rom}: unsupported runtime family or layout source"
        )
    if profile.rom_size != rom_size:
        raise AddressProfileError(f"{profile.rom}: unexpected ROM size")
    if profile.telemetry_completion_variant != can_variant:
        raise AddressProfileError(f"{profile.rom}: unsupported runtime variant")
    if profile.capabilities != capabilities:
        raise AddressProfileError(f"{profile.rom}: capability contract differs")
    if profile.rom_delta % 0x100 or profile.ram_delta % 0x100:
        raise AddressProfileError(
            f"{profile.rom}: ROM and RAM deltas must preserve 256-byte alignment"
        )

    map_layout = map_switching_layout.load_layout()
    telemetry_layout = can_telemetry_layout.load_layout()
    expected_rom_start = map_layout.free_rom.start + profile.rom_delta
    active_rom_end = telemetry_layout.reserved_rom.start + profile.rom_delta
    maximum_rom_end = telemetry_layout.owned_rom.end + profile.rom_delta
    expected_ram = AddressRange(
        map_layout.ram.reservation.start + profile.ram_delta,
        telemetry_layout.ram.reservation.end + profile.ram_delta,
    )
    if (
        profile.injected_rom.start != expected_rom_start
        or not active_rom_end <= profile.injected_rom.end <= maximum_rom_end
    ):
        raise AddressProfileError(
            f"{profile.rom}: injected ROM does not contain the active "
            "rebased layout or exceeds its canonical budget"
        )
    if profile.injected_ram != expected_ram:
        raise AddressProfileError(
            f"{profile.rom}: injected RAM does not match the rebased layout"
        )
    if not profile.free_rom.contains(profile.injected_rom):
        raise AddressProfileError(f"{profile.rom}: injected ROM is not audited free")
    if not profile.free_ram.contains(profile.injected_ram):
        raise AddressProfileError(f"{profile.rom}: injected RAM is not audited free")

    _validate_extra_storage(profile, telemetry_layout)
    _validate_ignition_state_storage(profile)
    _validate_map_bindings(profile, map_layout)
    _validate_can_bindings(profile, telemetry_layout)


@lru_cache(maxsize=None)
def load_registry(path=DEFAULT_REGISTRY):
    """Load all exact profiles without selecting a default ROM."""
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise AddressProfileError(
            f"address profile registry cannot be loaded: {path}: {error}"
        ) from error
    return parse_registry(document, str(path))


def parse_registry(document, source):
    """Parse an explicit current projection without using the file-load cache."""
    _require_table(document, {"schema_version", "profile"}, source)
    if document["schema_version"] != 2:
        raise AddressProfileError(f"{source}: unsupported schema_version")
    rows = document["profile"]
    if not isinstance(rows, dict) or not rows:
        raise AddressProfileError(f"{source}: no exact profiles")
    profiles = {}

    def resolve(rom, stack=()):
        if rom in profiles:
            return profiles[rom]
        if rom not in rows:
            raise AddressProfileError(
                f"{source}: inherited profile {rom!r} does not exist"
            )
        if rom in stack:
            chain = " -> ".join((*stack, rom))
            raise AddressProfileError(f"{source}: profile inheritance cycle {chain}")
        row = rows[rom]
        context = f"{source} [profile.{rom}]"
        if isinstance(row, dict) and set(row) == {"inherits"}:
            base_rom = row["inherits"]
            if not isinstance(base_rom, str) or not base_rom:
                raise AddressProfileError(
                    f"{context}.inherits: expected a ROM label"
                )
            profile = replace(resolve(base_rom, (*stack, rom)), rom=rom)
        else:
            profile = _parse_profile(rom, row, context)
        profiles[rom] = profile
        return profile

    for rom in rows:
        resolve(rom)
    return profiles


def profile_for_rom(rom, path=DEFAULT_REGISTRY):
    """Return one explicitly selected profile or reject the ROM label."""
    if not isinstance(rom, str) or not rom:
        raise AddressProfileError("an exact ROM label is required")
    profiles = load_registry(Path(path))
    try:
        return profiles[rom.upper()]
    except KeyError as error:
        raise AddressProfileError(
            f"no runtime address profile is registered for {rom}"
        ) from error


def _read_u32(image, address, context):
    if address % 2 or address + 4 > len(image):
        raise AddressProfileError(f"{context}: invalid 32-bit stock address")
    return int.from_bytes(image[address : address + 4], "big")


def _validate_unreferenced_routine(profile, data):
    """Preserve the bounded scan attached to the legacy region identifier.

    The scan rejects aligned pointer values into the region and encoded
    direct branches to its entry. It establishes neither instruction
    boundaries nor absence of interior or computed control-flow entries.
    Lookup-literal coverage has no exemption based on this scan.
    """
    routine = profile.ignition_unreferenced_routine
    occupied = data[: profile.free_rom.start]
    high = routine.start >> 16
    if routine.end - 1 >> 16 != high:
        raise AddressProfileError(
            f"{profile.rom}: unreferenced routine crosses a 64 KiB boundary"
        )
    prefix = high.to_bytes(2, "big")
    position = occupied.find(prefix)
    while position != -1:
        value = int.from_bytes(occupied[position : position + 4], "big")
        if position % 2 == 0 and routine.start <= value < routine.end:
            raise AddressProfileError(
                f"{profile.rom}: stock word at {position:#x} points into the "
                "unreferenced ignition routine"
            )
        position = occupied.find(prefix, position + 1)
    for address in range(
        max(0, routine.start - 0x1004), routine.end + 0x1000, 2
    ):
        if routine.start <= address < routine.end:
            continue
        word = int.from_bytes(occupied[address : address + 2], "big")
        if word & 0xE000 == 0xA000:
            displacement = word & 0x0FFF
            if displacement & 0x0800:
                displacement -= 0x1000
        elif word & 0xF900 == 0x8900:
            displacement = word & 0x00FF
            if displacement & 0x0080:
                displacement -= 0x0100
        else:
            continue
        if address + 4 + displacement * 2 == routine.start:
            raise AddressProfileError(
                f"{profile.rom}: branch at {address:#x} enters the "
                "unreferenced ignition routine"
            )


def validate_stock_profile(profile, image):
    """Bind a profile to its exact stock image and verify every stock anchor."""
    data = bytes(image)
    if len(data) != profile.rom_size:
        raise AddressProfileError(
            f"{profile.rom}: image has {len(data)} bytes, expected {profile.rom_size}"
        )
    free = data[profile.free_rom.start : profile.free_rom.end]
    if free != bytes([0xFF]) * profile.free_rom.size:
        first = next(index for index, value in enumerate(free) if value != 0xFF)
        raise AddressProfileError(
            f"{profile.rom}: audited free ROM is occupied at "
            f"{profile.free_rom.start + first:#x}"
        )

    hooks = profile.map_hooks + profile.rolling_hooks + profile.can_hooks
    checked = {}
    for hook in hooks:
        actual = _read_u32(data, hook.address, f"{profile.rom}.{hook.key}")
        if actual != hook.stock:
            raise AddressProfileError(
                f"{profile.rom}.{hook.key}: stock is {actual:#010x}, "
                f"expected {hook.stock:#010x}"
            )
        previous = checked.setdefault(hook.address, hook.stock)
        if previous != hook.stock:
            raise AddressProfileError(
                f"{profile.rom}: conflicting stock hook at {hook.address:#x}"
            )

    for item in profile.rolling_diagnostics:
        actual = _read_u32(
            data, item.pointer_address, f"{profile.rom}.{item.key}"
        )
        if actual != 0xFFFFFFFF:
            raise AddressProfileError(
                f"{profile.rom}.{item.key}: diagnostic pointer is occupied"
            )

    can = profile.can_symbol_by_key
    if can:
        for key in (
            "feedback_config_record",
            "mailbox_record",
            "occupied_mailbox_record",
        ):
            address = can[f"{key}_address"]
            expected = (
                can[f"{key}_value"]
                if key == "feedback_config_record"
                else can[f"{key}_stock"]
            )
            actual = _read_u32(data, address, f"{profile.rom}.{key}")
            if actual != expected:
                raise AddressProfileError(
                    f"{profile.rom}.{key}: stock is {actual:#010x}, "
                    f"expected {expected:#010x}"
                )

        actual_payload_base = _read_u32(
            data,
            can["feedback_payload_base_literal"],
            f"{profile.rom}.feedback_payload_base",
        )
        if actual_payload_base != can["feedback_payload_base"]:
            raise AddressProfileError(
                f"{profile.rom}.feedback_payload_base: stock is "
                f"{actual_payload_base:#010x}, expected "
                f"{can['feedback_payload_base']:#010x}"
            )

    canonical = map_switching_layout.load_layout().family_by_key
    for key, source_key in _map_family_sources(profile).items():
        address = profile.map_family_by_key[key]
        size = canonical[source_key].byte_length
        if data[address : address + size] == bytes([0xFF]) * size:
            raise AddressProfileError(f"{profile.rom}.{key}: stock map is erased")
    if profile.ignition_unreferenced_routine is not None:
        _validate_unreferenced_routine(profile, data)
    return profile


def validate_all_stock_profiles(path=DEFAULT_REGISTRY):
    """Verify the registry, ROM identities, family membership, and anchors."""
    profiles = load_registry(Path(path))
    images = rom_homology.load_images()
    _settings, families, _relationships = rom_homology.load_homology()
    rom_homology.validate_families(images, families)
    family_by_rom = {
        rom: key
        for key, row in families.items()
        for rom in row["members"]
    }
    for rom, profile in profiles.items():
        if rom not in images:
            raise AddressProfileError(f"{rom}: stock image is not registered")
        if family_by_rom.get(rom) != profile.family:
            raise AddressProfileError(
                f"{rom}: profile family {profile.family} differs from homology"
            )
        validate_stock_profile(profile, images[rom].data)
    return profiles


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify all profiles")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("--check is required")
    try:
        profiles = validate_all_stock_profiles(args.registry)
    except (AddressProfileError, ValueError) as error:
        print(f"status=FAIL reason={error}", file=sys.stderr)
        return 1
    telemetry_count = sum(len(item.telemetry_sources) for item in profiles.values())
    hook_count = sum(
        len(item.map_hooks) + len(item.rolling_hooks) + len(item.can_hooks)
        for item in profiles.values()
    )
    print(
        f"status=PASS profiles={len(profiles)} hooks={hook_count} "
        f"telemetry_sources={telemetry_count}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
