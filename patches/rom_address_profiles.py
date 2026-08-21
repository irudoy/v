#!/usr/bin/env python3
"""Load and verify exact stock-address profiles for relocated runtimes.

The registry has no implicit ROM selection. A caller must request one exact
ROM label, and every stock hook is verified against that ROM image before the
profile can participate in composition.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
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
from patches import rolling_launch_layout
from tools import rom_homology


DEFAULT_REGISTRY = Path(__file__).with_name("rom-address-profiles.toml")

PROFILE_FIELDS = frozenset(
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
        "exhaust_variant",
        "telemetry_completion_variant",
        "map_families",
        "map_hooks",
        "map_symbols",
        "rolling_hooks",
        "rolling_diagnostics",
        "rolling_symbols",
        "can_hooks",
        "can_symbols",
        "telemetry_sources",
        "extra_exhaust_storage",
        "evidence",
    }
)

MAP_FAMILY_KEYS = frozenset(
    {
        "over_run_fuel_hold",
        "over_run_fuel_cut",
        "over_run_fuel_restore",
        "over_run_fuel_intermediate_restore",
        "high_octane_timing_state",
        "high_detonation_timing_state",
        "cold_idle_ignition_timing",
        "idle_ignition_timing",
        "exhaust_cvtc_target_even",
        "exhaust_cvtc_target_odd",
        "fuel_compensation_main",
        "rev_limit_fuel_cut",
        "rev_limit_throttle_cut",
    }
)

MAP_HOOK_KEYS = frozenset(
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
        "exhaust_cvtc_target_lookup_even",
        "exhaust_cvtc_target_lookup_odd",
        "rev_fuel_cut_base",
        "rev_throttle_cluster_base",
        "rev_throttle_scalar_base",
        "cruise_feedback_serializer",
        "idle_ignition_lookup",
    }
)

MAP_SYMBOL_KEYS = frozenset(
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

ROLLING_HOOK_KEYS = frozenset(
    {
        "periodic_scheduler_index_0",
        "selector_arbitration",
        "startup_state_clear",
        "primary_ignition_command",
        "feedback_arbitration",
    }
)

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
        "scheduler_table",
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

CAN_HOOK_KEYS = frozenset(
    {
        "coherent_snapshot_call",
        "knock_interval_latch",
        "startup_state_clear",
        "hcan1_sle1_vector",
        "hcan1_primary_init",
        "hcan1_recovery_init",
    }
)

CAN_SYMBOL_KEYS = frozenset(
    {
        "coherent_snapshot",
        "knock_function",
        "knock_count",
        "knock_mask",
        "hcan1_init",
        "stock_sle1_isr",
        "stock_isr_helper",
        "feedback_config_record_address",
        "feedback_config_record_value",
        "feedback_dispatch_literal",
        "feedback_payload_base",
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

EVIDENCE_KEYS = frozenset(
    {"free_rom", "free_ram", "maps", "rolling", "can", "telemetry"}
)

EXTRA_STORAGE_KEYS = frozenset(
    {"adapter_start", "adapter_end", "pointer_table", "copies"}
)


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
class ExtraExhaustStorage:
    adapter: AddressRange
    pointer_table: int
    copies: tuple[int, ...]


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
    exhaust_variant: str
    telemetry_completion_variant: str
    map_families: tuple[tuple[str, int], ...]
    map_hooks: tuple[HookBinding, ...]
    map_symbols: tuple[tuple[str, int], ...]
    rolling_hooks: tuple[HookBinding, ...]
    rolling_diagnostics: tuple[DiagnosticBinding, ...]
    rolling_symbols: tuple[tuple[str, int], ...]
    can_hooks: tuple[HookBinding, ...]
    can_symbols: tuple[tuple[str, int], ...]
    telemetry_sources: tuple[tuple[str, int], ...]
    extra_exhaust_storage: ExtraExhaustStorage
    evidence: tuple[tuple[str, str], ...]

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
    result = ExtraExhaustStorage(
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


def _telemetry_source_keys():
    manifest = can_telemetry_profile.load_manifest()
    fields = list(manifest.fields)
    fields.extend(field for item in manifest.contexts for field in item.fields)
    return frozenset(field.name for field in fields if field.kind == "ecu_ram")


def _parse_profile(rom, row, context):
    _require_table(row, PROFILE_FIELDS, context)
    scalar_ints = {
        key: _uint(row[key], f"{context}.{key}")
        for key in (
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
        )
    }
    for key in (
        "family",
        "layout_source",
        "exhaust_variant",
        "telemetry_completion_variant",
    ):
        if not isinstance(row[key], str) or not row[key].strip():
            raise AddressProfileError(f"{context}.{key}: expected nonempty text")

    telemetry_keys = _telemetry_source_keys()
    evidence = row["evidence"]
    _require_table(evidence, EVIDENCE_KEYS, f"{context}.evidence")
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
        exhaust_variant=row["exhaust_variant"],
        telemetry_completion_variant=row["telemetry_completion_variant"],
        map_families=_address_table(
            row["map_families"], MAP_FAMILY_KEYS, f"{context}.map_families"
        ),
        map_hooks=_hooks(
            row["map_hooks"], MAP_HOOK_KEYS, f"{context}.map_hooks", chained=False
        ),
        map_symbols=_address_table(
            row["map_symbols"], MAP_SYMBOL_KEYS, f"{context}.map_symbols"
        ),
        rolling_hooks=_hooks(
            row["rolling_hooks"],
            ROLLING_HOOK_KEYS,
            f"{context}.rolling_hooks",
            chained=True,
        ),
        rolling_diagnostics=_diagnostics(
            row["rolling_diagnostics"], f"{context}.rolling_diagnostics"
        ),
        rolling_symbols=_address_table(
            row["rolling_symbols"],
            ROLLING_SYMBOL_KEYS,
            f"{context}.rolling_symbols",
        ),
        can_hooks=_hooks(
            row["can_hooks"], CAN_HOOK_KEYS, f"{context}.can_hooks", chained=True
        ),
        can_symbols=_address_table(
            row["can_symbols"], CAN_SYMBOL_KEYS, f"{context}.can_symbols"
        ),
        telemetry_sources=_address_table(
            row["telemetry_sources"],
            telemetry_keys,
            f"{context}.telemetry_sources",
        ),
        extra_exhaust_storage=_extra_storage(
            row["extra_exhaust_storage"], f"{context}.extra_exhaust_storage"
        ),
        evidence=tuple(sorted(evidence.items())),
    )
    _validate_structure(profile)
    return profile


def _rebased(value, delta):
    return value + delta


def _validate_structure(profile):
    if profile.family != "sh7058_8mfk" or profile.layout_source != "JK08A":
        raise AddressProfileError(
            f"{profile.rom}: only explicit JK08A-to-8MFK profiles are supported"
        )
    if profile.rom_size != 0x100000:
        raise AddressProfileError(f"{profile.rom}: unexpected ROM size")
    if profile.rom_delta % 0x100 or profile.ram_delta % 0x100:
        raise AddressProfileError(
            f"{profile.rom}: ROM and RAM deltas must preserve 256-byte alignment"
        )
    if (
        profile.exhaust_variant != "dual-bank"
        or profile.telemetry_completion_variant != "mailbox24-tail-chain"
    ):
        raise AddressProfileError(f"{profile.rom}: unsupported runtime variant")

    map_layout = map_switching_layout.load_layout()
    launch_layout = rolling_launch_layout.load_layout()
    telemetry_layout = can_telemetry_layout.load_layout()
    expected_rom = AddressRange(
        map_layout.free_rom.start + profile.rom_delta,
        telemetry_layout.owned_rom.end + profile.rom_delta,
    )
    expected_ram = AddressRange(
        map_layout.ram.reservation.start + profile.ram_delta,
        telemetry_layout.ram.reservation.end + profile.ram_delta,
    )
    if profile.injected_rom != expected_rom:
        raise AddressProfileError(
            f"{profile.rom}: injected ROM does not match the rebased layout"
        )
    if profile.injected_ram != expected_ram:
        raise AddressProfileError(
            f"{profile.rom}: injected RAM does not match the rebased layout"
        )
    if not profile.free_rom.contains(profile.injected_rom):
        raise AddressProfileError(f"{profile.rom}: injected ROM is not audited free")
    if not profile.free_ram.contains(profile.injected_ram):
        raise AddressProfileError(f"{profile.rom}: injected RAM is not audited free")

    extra = profile.extra_exhaust_storage
    if extra.adapter.start != telemetry_layout.reserved_rom.start + profile.rom_delta:
        raise AddressProfileError(
            f"{profile.rom}: extra exhaust adapter does not start at the future reserve"
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

    family = profile.map_family_by_key
    canonical_families = map_layout.family_by_key
    source_keys = {
        key: key for key in MAP_FAMILY_KEYS if not key.startswith("exhaust_cvtc")
    }
    source_keys["exhaust_cvtc_target_even"] = "exhaust_cvtc_target"
    source_keys["exhaust_cvtc_target_odd"] = "exhaust_cvtc_target"
    spans = []
    for key, source_key in source_keys.items():
        source = canonical_families[source_key]
        span = AddressRange(family[key], family[key] + source.byte_length)
        if span.end > profile.rom_size:
            raise AddressProfileError(f"{profile.rom}.{key}: map exceeds ROM")
        spans.append(span)
    for index, left in enumerate(spans):
        for right in spans[index + 1 :]:
            if left.overlaps(right):
                raise AddressProfileError(f"{profile.rom}: stock maps overlap")

    code = map_layout.code_region_by_key
    ram_delta = profile.ram_delta
    rom_delta = profile.rom_delta
    map_expected_replacements = {
        "selector_host_call": _rebased(code["selector_host"].entry, rom_delta),
        "startup_initializer": _rebased(code["startup_wrapper"].entry, rom_delta),
        "overrun_cut_lookup": _rebased(code["full_dfco_adapter"].entry, rom_delta),
        "overrun_restore_lookup": _rebased(code["full_dfco_adapter"].entry, rom_delta),
        "ignition_lookup_knock": _rebased(code["ignition_adapter"].entry, rom_delta),
        "ignition_lookup_primary_a": _rebased(code["ignition_adapter"].entry, rom_delta),
        "ignition_lookup_primary_b": _rebased(code["ignition_adapter"].entry, rom_delta),
        "fuel_compensation_lookup_startup": _rebased(
            code["fuel_compensation_adapter"].entry, rom_delta
        ),
        "fuel_compensation_lookup_runtime": _rebased(
            code["fuel_compensation_adapter"].entry, rom_delta
        ),
        "exhaust_cvtc_target_lookup_even": _rebased(
            code["exhaust_cvtc_target_adapter"].entry, rom_delta
        ),
        "exhaust_cvtc_target_lookup_odd": extra.adapter.start,
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
        "cruise_feedback_serializer": _rebased(
            code["cruise_feedback_wrapper"].entry, rom_delta
        ),
        "idle_ignition_lookup": _rebased(
            code["idle_ignition_adapter"].entry, rom_delta
        ),
    }
    for key, expected in map_expected_replacements.items():
        binding = profile.map_hook_by_key[key]
        if binding.replacement != expected or binding.base != binding.stock:
            raise AddressProfileError(f"{profile.rom}.{key}: map hook chain differs")

    launch_code = launch_layout.code_region_by_key
    rolling = profile.rolling_hook_by_key
    rolling_expected_replacements = {
        "periodic_scheduler_index_0": _rebased(
            launch_code["periodic_wrapper"].entry, rom_delta
        ),
        "selector_arbitration": _rebased(
            launch_code["selector_arbiter"].entry, rom_delta
        ),
        "startup_state_clear": _rebased(
            launch_code["startup_wrapper"].entry, rom_delta
        ),
        "primary_ignition_command": _rebased(
            launch_code["ignition_adapter"].entry, rom_delta
        ),
        "feedback_arbitration": _rebased(
            launch_code["feedback_arbiter"].entry, rom_delta
        ),
    }
    for key, replacement in rolling_expected_replacements.items():
        if rolling[key].replacement != replacement:
            raise AddressProfileError(
                f"{profile.rom}.{key}: rolling replacement differs"
            )
    if rolling["selector_arbitration"].base != profile.map_hook_by_key[
        "selector_host_call"
    ].replacement:
        raise AddressProfileError(f"{profile.rom}: selector hook chain is open")
    if rolling["startup_state_clear"].base != profile.map_hook_by_key[
        "startup_initializer"
    ].replacement:
        raise AddressProfileError(f"{profile.rom}: startup hook chain is open")
    if rolling["feedback_arbitration"].base != profile.map_hook_by_key[
        "cruise_feedback_serializer"
    ].replacement:
        raise AddressProfileError(f"{profile.rom}: feedback hook chain is open")

    state_start = launch_layout.ram.state.start + ram_delta
    diagnostics = profile.rolling_diagnostic_by_key
    canonical_diagnostics = {item.name: item for item in launch_layout.diagnostics}
    for key, binding in diagnostics.items():
        source = canonical_diagnostics[key]
        if (
            binding.did != source.did
            or binding.width != source.width
            or binding.target != source.target + ram_delta
            or not state_start <= binding.target < state_start + launch_layout.ram.state.size
        ):
            raise AddressProfileError(
                f"{profile.rom}.{key}: rolling diagnostic differs"
            )

    telemetry_code = telemetry_layout.code_region_by_key
    can_expected_replacements = {
        "coherent_snapshot_call": _rebased(
            telemetry_code["main_wrapper"].entry, rom_delta
        ),
        "knock_interval_latch": _rebased(
            telemetry_code["knock_wrapper"].entry, rom_delta
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
    can_hooks = profile.can_hook_by_key
    for key, replacement in can_expected_replacements.items():
        if can_hooks[key].replacement != replacement:
            raise AddressProfileError(
                f"{profile.rom}.{key}: CAN replacement differs"
            )
    if can_hooks["startup_state_clear"].base != rolling[
        "startup_state_clear"
    ].replacement:
        raise AddressProfileError(f"{profile.rom}: CAN startup hook chain is open")

    symbols = profile.can_symbol_by_key
    if (
        symbols["mailbox_index"] != 24
        or symbols["mailbox_data"] != 0xFFFFDC08
        or symbols["mailbox_mask"] != 0x0100
        or symbols["mailbox_record_stock"] != 0x05000000
        or symbols["occupied_mailbox_record_stock"] != 0x04000000
        or symbols["feedback_config_record_value"] != 0x0308AA20
    ):
        raise AddressProfileError(f"{profile.rom}: mailbox contract differs")
    if symbols["feedback_status_byte"] != profile.map_symbol_by_key[
        "feedback_status_byte"
    ]:
        raise AddressProfileError(f"{profile.rom}: feedback status binding differs")

    telemetry_addresses = list(profile.telemetry_source_by_name.values())
    if len(telemetry_addresses) != len(set(telemetry_addresses)):
        raise AddressProfileError(f"{profile.rom}: duplicate telemetry sources")
    if any(
        not 0xFFFF0000 <= address < profile.free_ram.start
        for address in telemetry_addresses
    ):
        raise AddressProfileError(
            f"{profile.rom}: telemetry source enters injected RAM"
        )


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
    _require_table(document, {"schema_version", "profile"}, str(path))
    if document["schema_version"] != 1:
        raise AddressProfileError(f"{path}: unsupported schema_version")
    rows = document["profile"]
    if not isinstance(rows, dict) or not rows:
        raise AddressProfileError(f"{path}: no exact profiles")
    return {
        rom: _parse_profile(rom, row, f"{path} [profile.{rom}]")
        for rom, row in rows.items()
    }


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
    for key in (
        "feedback_config_record",
        "mailbox_record",
        "occupied_mailbox_record",
    ):
        address = can[f"{key}_address"]
        expected = can[f"{key}_value"] if key == "feedback_config_record" else can[f"{key}_stock"]
        actual = _read_u32(data, address, f"{profile.rom}.{key}")
        if actual != expected:
            raise AddressProfileError(
                f"{profile.rom}.{key}: stock is {actual:#010x}, "
                f"expected {expected:#010x}"
            )

    payload_literal = (
        profile.map_symbol_by_key["feedback_serializer"] + 0x56
    )
    actual_payload_base = _read_u32(
        data, payload_literal, f"{profile.rom}.feedback_payload_base"
    )
    if actual_payload_base != can["feedback_payload_base"]:
        raise AddressProfileError(
            f"{profile.rom}.feedback_payload_base: stock is "
            f"{actual_payload_base:#010x}, expected "
            f"{can['feedback_payload_base']:#010x}"
        )

    canonical = map_switching_layout.load_layout().family_by_key
    source_keys = {
        key: key for key in MAP_FAMILY_KEYS if not key.startswith("exhaust_cvtc")
    }
    source_keys["exhaust_cvtc_target_even"] = "exhaust_cvtc_target"
    source_keys["exhaust_cvtc_target_odd"] = "exhaust_cvtc_target"
    for key, source_key in source_keys.items():
        address = profile.map_family_by_key[key]
        size = canonical[source_key].byte_length
        if data[address : address + size] == bytes([0xFF]) * size:
            raise AddressProfileError(f"{profile.rom}.{key}: stock map is erased")
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
