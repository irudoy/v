#!/usr/bin/env python3
"""Project and validate production runtime layouts for registered ROMs.

The canonical SH-2E sources and layouts remain in JK08A coordinates. Exact
8MFK address profiles provide every nonuniform stock binding, while this module
applies the audited uniform injected-ROM and injected-RAM relocations. Target
machine-code payloads are tracked separately and are accepted only when their
digests match both the projected layout and independently assembled sources.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from functools import lru_cache
import argparse
import hashlib
from pathlib import Path
import re
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching
from patches import can_telemetry_assembly
from patches import can_telemetry_layout
from patches import can_telemetry_profile
from patches import map_switching_assembly
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout
from patches import rom_address_profiles
from patches import rom_checksums
from patches import can_telemetry_compose
from tools import rom_homology
from tools.mapkit import rom as romkit


DEFAULT_PAYLOADS = Path(__file__).with_name("runtime-target-payloads.toml")
EXACT_FAMILY = "sh7058_7mfkavn86"
RELOCATED_FAMILY = "sh7058_8mfk"
EXACT_ROMS = ("JK00A", "JK03A", "JK03B", "JK08A")
RELOCATED_ROMS = ("JK00C", "JK00D")
SUPPORTED_ROMS = EXACT_ROMS + RELOCATED_ROMS
ZERO_SHA256 = "0" * 64

NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])0x[0-9A-Fa-f]+")

MAP_HOOK_KEYS = {
    "selector_host_call": "selector_host_call",
    "startup_initializer": "startup_initializer",
    "overrun_cut_lookup": "overrun_cut_lookup",
    "overrun_restore_lookup": "overrun_restore_lookup",
    "ignition_lookup_493e8": "ignition_lookup_knock",
    "ignition_lookup_4e1c0_a": "ignition_lookup_primary_a",
    "ignition_lookup_4e1c0_b": "ignition_lookup_primary_b",
    "fuel_compensation_lookup_2c648": "fuel_compensation_lookup_startup",
    "fuel_compensation_lookup_3be3c": "fuel_compensation_lookup_runtime",
    "exhaust_cvtc_target_lookup": "exhaust_cvtc_target_lookup_even",
    "rev_fuel_cut_base": "rev_fuel_cut_base",
    "rev_throttle_cluster_base": "rev_throttle_cluster_base",
    "rev_throttle_scalar_base": "rev_throttle_scalar_base",
    "cruise_feedback_serializer": "cruise_feedback_serializer",
    "idle_ignition_lookup": "idle_ignition_lookup",
}

CANONICAL_MAP_SYMBOLS = {
    "selector_function": 0x000D09D8,
    "button_state": 0xFFFF2A85,
    "diagnostic_state": 0xFFFF2A84,
    "ascd_state": 0xFFFF41AE,
    "startup_initializer": 0x0002C648,
    "dfco_lookup": 0x00026388,
    "ignition_lookup": 0x00026230,
    "fuel_compensation_lookup": 0x000261F0,
    "exhaust_lookup": 0x000261B8,
    "idle_ignition_lookup": 0x00026370,
    "feedback_serializer": 0x000C5372,
    "feedback_status_byte": 0xFFFF3ADA,
    "throttle_container": 0x00009424,
    "throttle_runtime": 0xFFFF1796,
}

CANONICAL_ROLLING_SYMBOLS = {
    "scheduler_table": 0x00021970,
    "scheduler_task": 0x000A9554,
    "rpm": 0xFFFF11BC,
    "vehicle_speed": 0xFFFF110E,
    "pedal": 0xFFFF2672,
    "coolant_index": 0xFFFF1077,
    "button_state": 0xFFFF2A85,
    "ascd_state": 0xFFFF41AE,
    "fuel_inhibit": 0xFFFF2497,
    "apc_mode": 0xFFFF24C9,
    "apc_output": 0xFFFF2022,
    "unsigned_divide": 0x00021CE0,
    "stock_ignition_consumer": 0x0002A892,
}

CANONICAL_CAN_SYMBOLS = {
    "coherent_snapshot": 0x00020DFE,
    "knock_function": 0x000493E8,
    "knock_count": 0xFFFF2142,
    "knock_mask": 0xFFFF2150,
    "hcan1_init": 0x000C338A,
    "stock_sle1_isr": 0x000C7914,
    "stock_isr_helper": 0x000C6B68,
    "feedback_config_record_address": 0x00009766,
    "feedback_config_record_value": 0x0308AA20,
    "feedback_dispatch_literal": 0x000C3FA4,
    "feedback_payload_base": 0xFFFF3AB5,
    "feedback_status_byte": 0xFFFF3ADA,
    "mailbox_record_address": 0x000097BE,
    "mailbox_record_stock": 0x05000000,
    "occupied_mailbox_record_address": 0x000097C6,
    "occupied_mailbox_record_stock": 0x04000000,
    "mailbox_index": 26,
    "mailbox_data": 0xFFFFDC48,
    "mailbox_mask": 0x0400,
}


class RuntimeTargetError(ValueError):
    """Raised when a target projection or payload lock is incomplete."""


@dataclass(frozen=True)
class PayloadLocks:
    rom: str
    stock_sha256: str
    map_stage_sha256: str
    rolling_stage_sha256: str
    telemetry_stage_sha256: str
    map_payloads: dict[str, bytes]
    rolling_payloads: dict[str, bytes]
    telemetry_payloads: dict[str, bytes]


@dataclass(frozen=True)
class RuntimeTarget:
    rom: str
    family: str
    stock_image: romkit.Image
    checksum_layout: rom_checksums.ChecksumLayout
    map_layout: map_switching_layout.Layout
    rolling_layout: rolling_launch_layout.Layout
    telemetry_layout: can_telemetry_layout.Layout
    map_payloads: dict[str, bytes]
    rolling_payloads: dict[str, bytes]
    telemetry_payloads: dict[str, bytes]


def _sha256(data):
    return hashlib.sha256(bytes(data)).hexdigest()


def _require_sha256(value, context):
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise RuntimeTargetError(f"{context}: expected lowercase SHA-256")
    return value


def _decode_payloads(row, context):
    if not isinstance(row, dict) or not row:
        raise RuntimeTargetError(f"{context}: expected a nonempty table")
    result = {}
    for key, value in row.items():
        if not isinstance(value, str):
            raise RuntimeTargetError(f"{context}.{key}: expected hex text")
        try:
            result[key] = bytes.fromhex("".join(value.split()))
        except ValueError as error:
            raise RuntimeTargetError(
                f"{context}.{key}: invalid payload hex"
            ) from error
    return result


@lru_cache(maxsize=None)
def load_payload_locks(path=DEFAULT_PAYLOADS):
    path = Path(path)
    try:
        with path.open("rb") as source:
            document = tomllib.load(source)
    except (OSError, tomllib.TOMLDecodeError) as error:
        raise RuntimeTargetError(
            f"target payload registry cannot be loaded: {path}: {error}"
        ) from error
    if set(document) != {"schema_version", "target"}:
        raise RuntimeTargetError(
            f"{path}: expected only schema_version and target"
        )
    if document["schema_version"] != 1:
        raise RuntimeTargetError(f"{path}: unsupported schema_version")
    rows = document["target"]
    if not isinstance(rows, dict) or set(rows) != set(RELOCATED_ROMS):
        raise RuntimeTargetError(
            f"{path}: target set differs from {RELOCATED_ROMS}"
        )
    result = {}
    expected = {
        "stock_sha256", "map_stage_sha256", "rolling_stage_sha256",
        "telemetry_stage_sha256", "map_units", "rolling_units",
        "telemetry_units",
    }
    for rom, row in rows.items():
        if not isinstance(row, dict) or set(row) != expected:
            actual = set(row) if isinstance(row, dict) else set()
            raise RuntimeTargetError(
                f"{path} [target.{rom}]: fields differ; "
                f"missing={sorted(expected - actual)}; "
                f"extra={sorted(actual - expected)}"
            )
        result[rom] = PayloadLocks(
            rom=rom,
            stock_sha256=_require_sha256(
                row["stock_sha256"], f"{rom}.stock_sha256"
            ),
            map_stage_sha256=_require_sha256(
                row["map_stage_sha256"], f"{rom}.map_stage_sha256"
            ),
            rolling_stage_sha256=_require_sha256(
                row["rolling_stage_sha256"],
                f"{rom}.rolling_stage_sha256",
            ),
            telemetry_stage_sha256=_require_sha256(
                row["telemetry_stage_sha256"],
                f"{rom}.telemetry_stage_sha256",
            ),
            map_payloads=_decode_payloads(
                row["map_units"], f"{rom}.map_units"
            ),
            rolling_payloads=_decode_payloads(
                row["rolling_units"], f"{rom}.rolling_units"
            ),
            telemetry_payloads=_decode_payloads(
                row["telemetry_units"], f"{rom}.telemetry_units"
            ),
        )
    return result


def _add_mapping(mapping, source, target, context):
    previous = mapping.setdefault(source, target)
    if previous != target:
        raise RuntimeTargetError(
            f"{context}: {source:#010x} maps to both "
            f"{previous:#010x} and {target:#010x}"
        )


def _canonical_telemetry_fields():
    manifest = can_telemetry_profile.load_manifest()
    return tuple(manifest.fields) + tuple(
        field for context in manifest.contexts for field in context.fields
    )


def _address_mapping(profile):
    mapping = {}
    canonical_map = map_switching_layout.load_layout()
    canonical_rolling = rolling_launch_layout.load_layout()
    canonical_can = can_telemetry_layout.load_layout()

    family_targets = profile.map_family_by_key
    for family in canonical_map.families:
        target_key = (
            "exhaust_cvtc_target_even"
            if family.key == "exhaust_cvtc_target"
            else family.key
        )
        _add_mapping(
            mapping,
            family.canonical_address,
            family_targets[target_key],
            f"{profile.rom}.map_families",
        )
    _add_mapping(
        mapping,
        canonical_map.family_by_key["rev_limit_fuel_cut"].canonical_address
        + 8,
        family_targets["rev_limit_fuel_cut"] + 8,
        f"{profile.rom}.rev_limit_fuel_cut_tail",
    )

    map_hooks = profile.map_hook_by_key
    for hook in canonical_map.hooks:
        target = map_hooks[MAP_HOOK_KEYS[hook.key]]
        _add_mapping(mapping, hook.address, target.address, profile.rom)
        _add_mapping(mapping, hook.stock, target.stock, profile.rom)

    map_symbols = profile.map_symbol_by_key
    for key, source in CANONICAL_MAP_SYMBOLS.items():
        _add_mapping(mapping, source, map_symbols[key], profile.rom)
    _add_mapping(
        mapping,
        canonical_map.feedback.payload_start,
        profile.can_symbol_by_key["feedback_payload_base"]
        + canonical_map.feedback.payload_offset,
        profile.rom,
    )
    _add_mapping(
        mapping,
        canonical_map.ram.reservation.start - 0x10,
        profile.injected_ram.start - 0x10,
        profile.rom,
    )

    rolling_hooks = profile.rolling_hook_by_key
    for hook in canonical_rolling.hooks:
        target = rolling_hooks[hook.key]
        _add_mapping(mapping, hook.address, target.address, profile.rom)
        _add_mapping(mapping, hook.stock, target.base, profile.rom)
    canonical_diagnostics = {
        item.name: item for item in canonical_rolling.diagnostics
    }
    for key, target in profile.rolling_diagnostic_by_key.items():
        source = canonical_diagnostics[key]
        _add_mapping(
            mapping, source.pointer_address, target.pointer_address,
            profile.rom,
        )
        _add_mapping(mapping, source.target, target.target, profile.rom)
    rolling_symbols = profile.rolling_symbol_by_key
    for key, source in CANONICAL_ROLLING_SYMBOLS.items():
        _add_mapping(mapping, source, rolling_symbols[key], profile.rom)

    can_hooks = profile.can_hook_by_key
    for hook in canonical_can.hooks:
        target = can_hooks[hook.key]
        _add_mapping(mapping, hook.address, target.address, profile.rom)
        _add_mapping(mapping, hook.stock, target.base, profile.rom)
    can_symbols = profile.can_symbol_by_key
    for key, source in CANONICAL_CAN_SYMBOLS.items():
        _add_mapping(mapping, source, can_symbols[key], profile.rom)

    target_sources = profile.telemetry_source_by_name
    for field in _canonical_telemetry_fields():
        if field.kind != "ecu_ram":
            continue
        target = target_sources[field.name]
        for index in range(field.width):
            _add_mapping(
                mapping, field.source + index, target + index, profile.rom
            )
    return mapping


def _project_value(value, profile, mapping):
    if value in mapping:
        return mapping[value]
    if 0x000D2108 <= value < 0x000D6000:
        return value + profile.rom_delta
    if 0xFFFF5D00 <= value < 0xFFFF6000:
        return value + profile.ram_delta
    return value


def _render_source(source, profile, mapping, overrides=None):
    overrides = overrides or {}

    def replace_number(match):
        value = int(match.group(0), 16)
        projected = overrides.get(
            value, _project_value(value, profile, mapping)
        )
        width = len(match.group(0)) - 2
        return f"0x{projected:0{width}X}"

    rendered = []
    for raw_line in source.splitlines():
        code, marker, comment = raw_line.partition("//")
        code = NUMBER_RE.sub(replace_number, code)
        rendered.append(code + (marker + comment if marker else ""))
    return "\n".join(rendered) + "\n"


def render_target_text(rom, source, overrides=None):
    """Render numeric target bindings in arbitrary canonical source text."""
    profile = rom_address_profiles.profile_for_rom(str(rom).upper())
    return _render_source(
        source, profile, _address_mapping(profile), overrides
    )


def _read_source(name):
    return (Path(__file__).parent / name).read_text(encoding="utf-8")


def _render_unaligned_throttle_limiter(profile, mapping):
    """Render the 8MFK limiter with a two-byte-aligned stock container."""
    source = _read_source("map-switching-limiter-commit.s")
    canonical = """mov #0x7,r1
throttle_copy_loop:
mov.l @r5+,r2
mov.l r2,@r6
add 0x4,r6
"""
    target = """mov #0xE,r1
throttle_copy_loop:
mov.w @r5+,r2
mov.w r2,@r6
add 0x2,r6
"""
    if source.count(canonical) != 1:
        raise RuntimeTargetError(
            "canonical limiter throttle-copy sequence differs"
        )
    return _render_source(
        source.replace(canonical, target), profile, mapping
    )


def _source_literals(source_texts, units):
    result = []
    for unit in units:
        parsed = map_switching_assembly.parse_source_text(
            source_texts[unit.key], unit.source,
            unit.span.start, unit.span.end,
        )
        literals = (
            {}
            if unit.key == "tables"
            else map_switching_assembly._long_literals(parsed)
        )
        result.append((unit.key, tuple(sorted(literals.items()))))
    return tuple(result)


def _projected_unit(unit, source, start, end, regions, payloads):
    parsed = map_switching_assembly.parse_source_text(
        source, unit.source, start, end
    )
    blob = None if payloads is None else payloads.get(unit.key)
    return map_switching_layout.AssemblyUnit(
        key=unit.key,
        source=unit.source,
        span=map_switching_layout.AddressRange(
            start, end, f"assembly.{unit.key}"
        ),
        fill=unit.fill,
        language=unit.language,
        expected_sha256=ZERO_SHA256 if blob is None else _sha256(blob),
        instruction_count=parsed.instruction_count,
        data_bytes=parsed.data_bytes,
        code_regions=tuple(regions),
    )


def _project_map(profile, source_sha256, mapping, payloads=None):
    base = map_switching_layout.load_layout()
    delta = profile.rom_delta
    ram_delta = profile.ram_delta
    source_texts = {
        unit.key: _render_source(
            _read_source(unit.source), profile, mapping
        )
        for unit in base.assembly_units
    }
    source_texts["limiter_commit"] = _render_unaligned_throttle_limiter(
        profile, mapping
    )

    odd_template = _read_source("map-switching-exhaust-odd-adapter.s")
    odd_overrides = {
        0x0000B33A: profile.map_family_by_key[
            "exhaust_cvtc_target_odd"
        ],
        0x000261B8: profile.map_symbol_by_key["exhaust_lookup"],
        0x000D5050: profile.extra_exhaust_storage.pointer_table,
    }
    source_texts["exhaust_odd_adapter"] = _render_source(
        odd_template, profile, mapping, odd_overrides
    )

    code_regions = tuple(
        replace(
            item,
            span=map_switching_layout.AddressRange(
                item.span.start + delta,
                item.span.end + delta,
                item.span.key,
            ),
            entry=item.entry + delta,
        )
        for item in base.code_regions
    ) + (
        map_switching_layout.CodeRegion(
            "exhaust_cvtc_target_odd_adapter",
            map_switching_layout.AddressRange(
                profile.extra_exhaust_storage.adapter.start,
                profile.extra_exhaust_storage.adapter.end,
                "exhaust_cvtc_target_odd_adapter",
            ),
            profile.extra_exhaust_storage.adapter.start,
        ),
    )

    units = tuple(
        _projected_unit(
            unit,
            source_texts[unit.key],
            unit.span.start + delta,
            unit.span.end + delta,
            unit.code_regions,
            payloads,
        )
        for unit in base.assembly_units
    )
    odd_proto = map_switching_layout.AssemblyUnit(
        key="exhaust_odd_adapter",
        source="map-switching-exhaust-odd-adapter.s",
        span=map_switching_layout.AddressRange(
            0x000D5000, 0x000D5040, "assembly.exhaust_odd_adapter"
        ),
        fill=0xFF,
        language="SuperH:BE:32:SH-2A",
        expected_sha256=ZERO_SHA256,
        instruction_count=0,
        data_bytes=0,
        code_regions=("exhaust_cvtc_target_odd_adapter",),
    )
    units += (
        _projected_unit(
            odd_proto,
            source_texts["exhaust_odd_adapter"],
            profile.extra_exhaust_storage.adapter.start,
            profile.extra_exhaust_storage.adapter.end,
            odd_proto.code_regions,
            payloads,
        ),
    )

    target_families = profile.map_family_by_key
    families = []
    for family in base.families:
        key = (
            "exhaust_cvtc_target_even"
            if family.key == "exhaust_cvtc_target"
            else family.key
        )
        canonical_address = target_families[key]
        families.append(replace(
            family,
            key=key,
            name=(
                f"{family.name} - Even Bank"
                if family.key == "exhaust_cvtc_target"
                else family.name
            ),
            canonical_address=canonical_address,
            copies=tuple(address + delta for address in family.copies),
            pointer_table=family.pointer_table + delta,
            stock_container_start=(
                canonical_address - family.selected_offset
            ),
            shadow_start=(
                None
                if family.shadow_start is None
                else family.shadow_start + ram_delta
            ),
            runtime_shadow_address=(
                None
                if family.runtime_shadow_address is None
                else profile.map_symbol_by_key["throttle_runtime"]
            ),
        ))
    exhaust = base.family_by_key["exhaust_cvtc_target"]
    odd_address = target_families["exhaust_cvtc_target_odd"]
    families.append(replace(
        exhaust,
        key="exhaust_cvtc_target_odd",
        name=f"{exhaust.name} - Odd Bank",
        canonical_address=odd_address,
        copies=profile.extra_exhaust_storage.copies,
        pointer_table=profile.extra_exhaust_storage.pointer_table,
        stock_container_start=odd_address,
        adapter="exhaust_cvtc_target_odd_adapter",
    ))

    hooks = tuple(
        map_switching_layout.Hook(
            key=item.key,
            address=item.address,
            width=4,
            stock=item.stock,
            replacement=item.replacement,
            purpose=f"Projected {item.key} binding for {profile.rom}.",
        )
        for item in profile.map_hooks
    )

    feedback_base = base.feedback
    map_symbols = profile.map_symbol_by_key
    can_symbols = profile.can_symbol_by_key
    payload_literal_delta = 0x56
    feedback = replace(
        feedback_base,
        config_record_address=can_symbols["feedback_config_record_address"],
        config_record=can_symbols["feedback_config_record_value"],
        serializer=map_symbols["feedback_serializer"],
        dispatch_literal=can_symbols["feedback_dispatch_literal"],
        serializer_payload_base_literal=(
            map_symbols["feedback_serializer"] + payload_literal_delta
        ),
        serializer_payload_base=can_symbols["feedback_payload_base"],
        payload_start=(
            can_symbols["feedback_payload_base"]
            + feedback_base.payload_offset
        ),
        status_byte_address=map_symbols["feedback_status_byte"],
        phase_counts_address=feedback_base.phase_counts_address + delta,
        encoding_evidence=(
            "exact_8mfk_serializer_three_bit_state_and_target_binding"
        ),
    )
    ram = replace(
        base.ram,
        reservation=map_switching_layout.AddressRange(
            base.ram.reservation.start + ram_delta,
            base.ram.reservation.end + ram_delta,
            base.ram.reservation.key,
        ),
        selector=map_switching_layout.AddressRange(
            base.ram.selector.start + ram_delta,
            base.ram.selector.end + ram_delta,
            base.ram.selector.key,
        ),
        fuel_cut_shadow=map_switching_layout.AddressRange(
            base.ram.fuel_cut_shadow.start + ram_delta,
            base.ram.fuel_cut_shadow.end + ram_delta,
            base.ram.fuel_cut_shadow.key,
        ),
        throttle_shadow=map_switching_layout.AddressRange(
            base.ram.throttle_shadow.start + ram_delta,
            base.ram.throttle_shadow.end + ram_delta,
            base.ram.throttle_shadow.key,
        ),
        stock_throttle_runtime=map_symbols["throttle_runtime"],
    )
    layout = replace(
        base,
        rom=profile.rom,
        source_sha256=source_sha256,
        free_rom=map_switching_layout.AddressRange(
            profile.free_rom.start, profile.free_rom.end, "free_rom"
        ),
        claimed_rom=map_switching_layout.AddressRange(
            profile.injected_rom.start,
            profile.injected_rom.end,
            "claimed_rom",
        ),
        ram=ram,
        feedback=feedback,
        code_regions=code_regions,
        assembly_units=units,
        hooks=hooks,
        families=tuple(families),
        variant="dual-exhaust",
        source_texts=tuple(sorted(source_texts.items())),
    )
    return replace(
        layout,
        source_literals=_source_literals(source_texts, layout.assembly_units),
    )


def _shift_range(item, delta):
    return map_switching_layout.AddressRange(
        item.start + delta, item.end + delta, item.key
    )


def _project_rolling(
    profile, source_sha256, mapping, payloads=None,
    map_stage_sha256=ZERO_SHA256,
    rolling_stage_sha256=ZERO_SHA256,
):
    base = rolling_launch_layout.load_layout()
    delta = profile.rom_delta
    ram_delta = profile.ram_delta
    source_texts = {
        unit.key: _render_source(
            _read_source(unit.source), profile, mapping
        )
        for unit in base.assembly_units
    }
    code_regions = tuple(
        replace(
            item,
            span=_shift_range(item.span, delta),
            entry=item.entry + delta,
        )
        for item in base.code_regions
    )
    units = tuple(
        _projected_unit(
            unit, source_texts[unit.key],
            unit.span.start + delta, unit.span.end + delta,
            unit.code_regions, payloads,
        )
        for unit in base.assembly_units
    )
    rolling_symbols = profile.rolling_symbol_by_key
    hooks = tuple(
        map_switching_layout.Hook(
            key=item.key,
            address=item.address,
            width=4,
            stock=item.base,
            replacement=item.replacement,
            purpose=f"Projected {item.key} binding for {profile.rom}.",
        )
        for item in profile.rolling_hooks
    )
    diagnostic_by_key = profile.rolling_diagnostic_by_key
    diagnostics = tuple(
        rolling_launch_layout.Diagnostic(
            did=diagnostic_by_key[item.name].did,
            pointer_address=diagnostic_by_key[item.name].pointer_address,
            stock=0xFFFFFFFF,
            target=diagnostic_by_key[item.name].target,
            width=diagnostic_by_key[item.name].width,
            name=item.name,
        )
        for item in base.diagnostics
    )
    ram = replace(
        base.ram,
        proven_free=map_switching_layout.AddressRange(
            profile.free_ram.start, profile.free_ram.end, "ram.proven_free"
        ),
        base_reservation=_shift_range(base.ram.base_reservation, ram_delta),
        state=_shift_range(base.ram.state, ram_delta),
        fuel_shadow=_shift_range(base.ram.fuel_shadow, ram_delta),
    )
    layout = replace(
        base,
        rom=profile.rom,
        source_sha256=source_sha256,
        base_composition_sha256=map_stage_sha256,
        expected_composition_sha256=rolling_stage_sha256,
        free_rom=map_switching_layout.AddressRange(
            profile.free_rom.start, profile.free_rom.end, "free_rom"
        ),
        claimed_rom=_shift_range(base.claimed_rom, delta),
        claimed_rom_extensions=tuple(
            _shift_range(item, delta)
            for item in base.claimed_rom_extensions
        ),
        configuration=_shift_range(base.configuration, delta),
        scheduler=replace(
            base.scheduler,
            table_address=rolling_symbols["scheduler_table"],
        ),
        ram=ram,
        code_regions=code_regions,
        assembly_units=units,
        hooks=hooks,
        diagnostics=diagnostics,
        variant="relocated-8mfk",
        source_texts=tuple(sorted(source_texts.items())),
    )
    return replace(
        layout,
        source_literals=_source_literals(source_texts, layout.assembly_units),
    )


def _project_can(
    profile, source_sha256, mapping, payloads=None,
    rolling_stage_sha256=ZERO_SHA256,
    telemetry_stage_sha256=ZERO_SHA256,
):
    base = can_telemetry_layout.load_layout()
    delta = profile.rom_delta
    ram_delta = profile.ram_delta
    source_texts = {}
    for unit in base.assembly_units:
        if unit.key == "completion":
            wrapper = _render_source(
                _read_source("can-telemetry-tail-chain-wrapper.s"),
                profile, mapping,
            )
            canonical = _read_source(unit.source)
            marker = ".org 0x000D4900"
            _prefix, separator, core = canonical.partition(marker)
            if not separator:
                raise RuntimeTargetError(
                    "canonical completion source lacks the shared core"
                )
            source_texts[unit.key] = wrapper + _render_source(
                marker + core, profile, mapping
            )
        else:
            source_texts[unit.key] = _render_source(
                _read_source(unit.source), profile, mapping
            )
    code_regions = tuple(
        replace(
            item,
            span=_shift_range(item.span, delta),
            entry=item.entry + delta,
        )
        for item in base.code_regions
    )
    units = tuple(
        _projected_unit(
            unit, source_texts[unit.key],
            unit.span.start + delta, unit.span.end + delta,
            unit.code_regions, payloads,
        )
        for unit in base.assembly_units
    )
    hooks = tuple(
        map_switching_layout.Hook(
            key=item.key,
            address=item.address,
            width=4,
            stock=item.base,
            replacement=item.replacement,
            purpose=f"Projected {item.key} binding for {profile.rom}.",
        )
        for item in profile.can_hooks
    )
    ram = replace(
        base.ram,
        proven_free=map_switching_layout.AddressRange(
            profile.free_ram.start, profile.free_ram.end, "ram.proven_free"
        ),
        lower_runtime_end=base.ram.lower_runtime_end + ram_delta,
        reservation=_shift_range(base.ram.reservation, ram_delta),
        active=_shift_range(base.ram.active, ram_delta),
        future=_shift_range(base.ram.future, ram_delta),
        state=_shift_range(base.ram.state, ram_delta),
        bank_a=_shift_range(base.ram.bank_a, ram_delta),
        bank_b=_shift_range(base.ram.bank_b, ram_delta),
        event=_shift_range(base.ram.event, ram_delta),
        active_reserved=_shift_range(base.ram.active_reserved, ram_delta),
    )
    extra = profile.extra_exhaust_storage
    extra_end = max(
        extra.adapter.end,
        extra.pointer_table + 20,
        *(address + 0x100 for address in extra.copies),
    )
    can_symbols = profile.can_symbol_by_key
    layout = replace(
        base,
        rom=profile.rom,
        source_sha256=source_sha256,
        base_composition_sha256=rolling_stage_sha256,
        expected_composition_sha256=telemetry_stage_sha256,
        free_rom=map_switching_layout.AddressRange(
            profile.free_rom.start, profile.free_rom.end, "free_rom"
        ),
        owned_rom=_shift_range(base.owned_rom, delta),
        reserved_rom=map_switching_layout.AddressRange(
            extra_end, base.owned_rom.end + delta, "reserved_rom"
        ),
        configuration=_shift_range(base.configuration, delta),
        mailbox_record_address=can_symbols["mailbox_record_address"],
        mailbox_record_stock=can_symbols["mailbox_record_stock"],
        ram=ram,
        code_regions=code_regions,
        assembly_units=units,
        hooks=hooks,
        variant="mailbox24-tail-chain",
        source_texts=tuple(sorted(source_texts.items())),
    )
    return replace(
        layout,
        source_literals=_source_literals(source_texts, layout.assembly_units),
    )


def project_relocated_target(rom, locks=None):
    rom = str(rom).upper()
    if rom not in RELOCATED_ROMS:
        raise RuntimeTargetError(f"no relocated runtime target for {rom}")
    profile = rom_address_profiles.profile_for_rom(rom)
    images = rom_homology.load_images()
    stock = images[rom]
    rom_address_profiles.validate_stock_profile(profile, stock.data)
    stock_sha256 = _sha256(stock.data)
    if locks is not None and locks.stock_sha256 != stock_sha256:
        raise RuntimeTargetError(
            f"{rom}: payload lock stock SHA-256 differs"
        )
    mapping = _address_mapping(profile)
    map_payloads = None if locks is None else locks.map_payloads
    rolling_payloads = None if locks is None else locks.rolling_payloads
    telemetry_payloads = None if locks is None else locks.telemetry_payloads
    map_layout = _project_map(
        profile, stock_sha256, mapping, map_payloads
    )
    rolling_layout = _project_rolling(
        profile,
        stock_sha256,
        mapping,
        rolling_payloads,
        ZERO_SHA256 if locks is None else locks.map_stage_sha256,
        ZERO_SHA256 if locks is None else locks.rolling_stage_sha256,
    )
    telemetry_layout = _project_can(
        profile,
        stock_sha256,
        mapping,
        telemetry_payloads,
        ZERO_SHA256 if locks is None else locks.rolling_stage_sha256,
        ZERO_SHA256 if locks is None else locks.telemetry_stage_sha256,
    )
    return RuntimeTarget(
        rom=rom,
        family=profile.family,
        stock_image=romkit.Image(rom, str(stock.path), stock.data),
        checksum_layout=rom_checksums.layout_for_rom(rom),
        map_layout=map_layout,
        rolling_layout=rolling_layout,
        telemetry_layout=telemetry_layout,
        map_payloads={} if map_payloads is None else map_payloads,
        rolling_payloads=(
            {} if rolling_payloads is None else rolling_payloads
        ),
        telemetry_payloads=(
            {} if telemetry_payloads is None else telemetry_payloads
        ),
    )


@lru_cache(maxsize=None)
def load_runtime_target(rom, payload_path=DEFAULT_PAYLOADS):
    rom = str(rom).upper()
    images = rom_homology.load_images()
    if rom in EXACT_ROMS:
        map_layout = map_switching_layout.load_layout()
        rolling_layout = rolling_launch_layout.load_layout()
        telemetry_layout = can_telemetry_layout.load_layout()
        stock = images[rom]
        return RuntimeTarget(
            rom=rom,
            family=EXACT_FAMILY,
            stock_image=romkit.Image(rom, str(stock.path), stock.data),
            checksum_layout=rom_checksums.layout_for_rom(rom),
            map_layout=map_layout,
            rolling_layout=rolling_layout,
            telemetry_layout=telemetry_layout,
            map_payloads=apply_map_switching.load_payloads(map_layout),
            rolling_payloads=rolling_launch_assembly.load_payloads(
                rolling_layout
            ),
            telemetry_payloads=can_telemetry_assembly.load_payloads(
                telemetry_layout
            ),
        )
    if rom in RELOCATED_ROMS:
        locks = load_payload_locks(Path(payload_path))[rom]
        return project_relocated_target(rom, locks)
    raise RuntimeTargetError(
        f"unsupported runtime target {rom!r}; supported ROMs: "
        f"{', '.join(SUPPORTED_ROMS)}"
    )


def _validate_projected_bindings(target):
    """Bind a projected layout back to every authoritative profile row."""
    profile = rom_address_profiles.profile_for_rom(target.rom)
    family_addresses = {
        item.key: item.canonical_address
        for item in target.map_layout.families
    }
    if family_addresses != profile.map_family_by_key:
        raise RuntimeTargetError(
            f"{target.rom}: projected map-family bindings differ"
        )

    actual_map_hooks = {
        item.key: (item.address, item.stock, item.replacement)
        for item in target.map_layout.hooks
    }
    expected_map_hooks = {
        item.key: (item.address, item.stock, item.replacement)
        for item in profile.map_hooks
    }
    if actual_map_hooks != expected_map_hooks:
        raise RuntimeTargetError(
            f"{target.rom}: projected map hooks differ"
        )

    actual_rolling_hooks = {
        item.key: (item.address, item.stock, item.replacement)
        for item in target.rolling_layout.hooks
    }
    expected_rolling_hooks = {
        item.key: (item.address, item.base, item.replacement)
        for item in profile.rolling_hooks
    }
    if actual_rolling_hooks != expected_rolling_hooks:
        raise RuntimeTargetError(
            f"{target.rom}: projected Rolling Launch hooks differ"
        )

    actual_diagnostics = {
        item.name: (
            item.did, item.pointer_address, item.target, item.width
        )
        for item in target.rolling_layout.diagnostics
    }
    expected_diagnostics = {
        item.key: (
            item.did, item.pointer_address, item.target, item.width
        )
        for item in profile.rolling_diagnostics
    }
    if actual_diagnostics != expected_diagnostics:
        raise RuntimeTargetError(
            f"{target.rom}: projected diagnostic bindings differ"
        )

    actual_can_hooks = {
        item.key: (item.address, item.stock, item.replacement)
        for item in target.telemetry_layout.hooks
    }
    expected_can_hooks = {
        item.key: (item.address, item.base, item.replacement)
        for item in profile.can_hooks
    }
    if actual_can_hooks != expected_can_hooks:
        raise RuntimeTargetError(
            f"{target.rom}: projected CAN hooks differ"
        )

    odd = target.map_layout.family_by_key["exhaust_cvtc_target_odd"]
    can_symbols = profile.can_symbol_by_key
    if any((
        target.map_layout.claimed_rom.start
        != profile.injected_rom.start,
        target.map_layout.claimed_rom.end != profile.injected_rom.end,
        target.map_layout.ram.reservation.start
        != profile.injected_ram.start,
        odd.copies != profile.extra_exhaust_storage.copies,
        odd.pointer_table != profile.extra_exhaust_storage.pointer_table,
        target.telemetry_layout.mailbox_record_address
        != can_symbols["mailbox_record_address"],
        target.telemetry_layout.mailbox_record_stock
        != can_symbols["mailbox_record_stock"],
    )):
        raise RuntimeTargetError(
            f"{target.rom}: projected allocation bindings differ"
        )


def validate_relocated_target(target, locks):
    """Validate one projected target through all three raw compositions."""
    _validate_projected_bindings(target)
    map_switching_layout.validate_structure(target.map_layout)
    rolling_launch_layout.validate_structure(target.rolling_layout)
    can_telemetry_layout.validate_structure(target.telemetry_layout)
    map_parsed = map_switching_assembly.validate_assembly_sources(
        target.map_layout
    )
    rolling_parsed = rolling_launch_assembly.validate_assembly_sources(
        target.rolling_layout
    )
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    map_switching_assembly.validate_instruction_semantics(
        target.map_layout, map_parsed, target.map_payloads
    )
    rolling_launch_assembly.validate_instruction_semantics(
        target.rolling_layout, rolling_parsed, target.rolling_payloads
    )
    can_telemetry_assembly.validate_instruction_semantics(
        target.telemetry_layout,
        telemetry_parsed,
        target.telemetry_payloads,
    )
    map_result = map_switching_compose.compose(
        layout=target.map_layout,
        image=target.stock_image,
        blobs=target.map_payloads,
    )
    rolling_result = rolling_launch_compose.compose(
        layout=target.rolling_layout,
        base=map_result.data,
        blobs=target.rolling_payloads,
    )
    telemetry_result = can_telemetry_compose.compose(
        layout=target.telemetry_layout,
        base=rolling_result.data,
        blobs=target.telemetry_payloads,
    )
    actual = (
        map_result.sha256,
        rolling_result.sha256,
        telemetry_result.sha256,
    )
    expected = (
        locks.map_stage_sha256,
        locks.rolling_stage_sha256,
        locks.telemetry_stage_sha256,
    )
    if actual != expected:
        raise RuntimeTargetError(
            f"{target.rom}: composition locks differ; "
            f"actual={actual} expected={expected}"
        )
    return target


def validate_all_relocated_targets(path=DEFAULT_PAYLOADS):
    """Validate all registered relocated target layouts and payloads."""
    locks = load_payload_locks(Path(path))
    profiles = rom_address_profiles.validate_all_stock_profiles()
    if set(profiles) != set(RELOCATED_ROMS):
        raise RuntimeTargetError("relocated address-profile set differs")
    return {
        rom: validate_relocated_target(
            project_relocated_target(rom, locks[rom]), locks[rom]
        )
        for rom in RELOCATED_ROMS
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--payloads", type=Path, default=DEFAULT_PAYLOADS)
    args = parser.parse_args(argv)
    if not args.check:
        parser.error("--check is required")
    try:
        targets = validate_all_relocated_targets(args.payloads)
    except (OSError, ValueError, RuntimeTargetError) as error:
        print(f"status=FAIL reason={error}", file=sys.stderr)
        return 1
    print(
        f"status=PASS targets={len(targets)} "
        f"map_families={sum(len(x.map_layout.families) for x in targets.values())} "
        f"instructions={sum(x.map_layout.assembled_instruction_count + x.rolling_layout.assembled_instruction_count + x.telemetry_layout.assembled_instruction_count for x in targets.values())}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
