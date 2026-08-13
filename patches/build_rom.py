#!/usr/bin/env python3
"""Build one complete production ROM with every supported firmware runtime.

The CLI detects the ROM series from immutable image bytes by default or accepts
an explicit ``--rom`` selector.  Only JK08A is currently registered.  Its
handler installs the current map-switching and Rolling Launch runtimes directly
from their SHA-locked payload bundles through the current layout and composer
contracts.

Compatible unpatched inputs retain their lower calibration and configuration.
A complete current or historical JK08A composition may also be rebuilt: all
alternate-map bytes are preserved while every builder-owned executable span,
hook, diagnostic pointer, configuration record, and checksum is regenerated.
Unknown or partial patch states are rejected before an output is written.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import hashlib
from itertools import chain
import json
from pathlib import Path
import struct
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import apply_map_switching
from patches import apply_rolling_launch
from patches import jk08a_checksums as checksums
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout
from tools.mapkit import rom as romkit


AUTO_ROM = "auto"
SUPPORTED_ROMS = ("JK08A",)
PROFILE_SCHEMA_VERSION = 2
MANIFEST_SCHEMA_VERSION = 1
TOOL_NAME = "patches/build_rom.py"

PROFILE_ROOT_KEYS = frozenset(
    ("schema_version", "rom", "name", "rolling_launch")
)
ROLLING_PROFILE_KEYS = frozenset(
    (
        "mode",
        "enabled_maps",
        "coolant_min",
        "coolant_max",
        "min_speed",
        "retard_ramp_native",
        "min_rpm_native",
        "min_pedal",
        "rpm_offset_native",
        "min_hysteresis_native",
        "max_hysteresis_native",
        "hysteresis_ratio_tenths",
        "run_timeout_ticks",
        "rearm_ticks",
        "target_commands",
    )
)
MODE_NAMES = {
    "observe": rolling_launch.Mode.OBSERVE,
    "rpm_hold": rolling_launch.Mode.RPM_HOLD,
    "rpm_hold_retard": rolling_launch.Mode.RPM_HOLD_RETARD,
}


class BuildError(ValueError):
    """Raised when ROM selection, composition, or artifact checks fail."""


@dataclass(frozen=True)
class Profile:
    name: str
    rom: str
    calibration: rolling_launch.Calibration
    source: str
    sha256: str | None


@dataclass(frozen=True)
class RollingEndpointSignature:
    key: str
    configuration_schema_version: int
    unit_sha256: tuple[tuple[str, str], ...]
    hook_values: tuple[tuple[str, int], ...]


PRE_FEEDBACK_ROLLING_HOOK_VALUES = (
    ("periodic_scheduler_index_0", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D35E0),
)
ERASED_FEEDBACK_ARBITER_SHA256 = (
    "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539"
)


# Exact code fingerprints for registered Rolling Launch endpoints that the
# current builder can migrate. Configuration bytes remain calibration-specific
# and are validated against the applicable record contract.
HISTORICAL_ROLLING_ENDPOINTS = (
    RollingEndpointSignature(
        key="schema-1-bandless",
        configuration_schema_version=1,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "599c859dffe2f2b88eefa0c2add63ceecf3232a08625b1acc2481bd9c4658673",
            ),
            (
                "ignition_adapter",
                "542aab5999c39903c6614daa4b44ca41a77fe37273ee57dc2c4390e53844311d",
            ),
            (
                "ignition_controller",
                "e9175db65a9789096ca9cb5524d3abc2107df03e3c9ba3af1aca628f9c5d3bd2",
            ),
            (
                "threshold_helper",
                "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-2-speed-required",
        configuration_schema_version=2,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "6fbe61494983b09c45565b02409f1d768c1633cbe3c088d6e378d10c0ed9d3c6",
            ),
            (
                "ignition_adapter",
                "82452974b158d34cc8d7c69b990f327428ff01f92e047c6a15cb2f9251e90952",
            ),
            (
                "ignition_controller",
                "465b6e90325fa6aecffa94eeffa40b9c7b65f5095ed4bf768e52ee55f1407e3c",
            ),
            (
                "threshold_helper",
                "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-2-zero-speed",
        configuration_schema_version=2,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "e7e940b866526ea9feeab044f072fdee1ce157de600dd61482fbbe2905203661",
            ),
            (
                "ignition_adapter",
                "82452974b158d34cc8d7c69b990f327428ff01f92e047c6a15cb2f9251e90952",
            ),
            (
                "ignition_controller",
                "465b6e90325fa6aecffa94eeffa40b9c7b65f5095ed4bf768e52ee55f1407e3c",
            ),
            (
                "threshold_helper",
                "0052516839b94ee314a4e3b398c8036de3790d672194987a394ee60323848539",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
    RollingEndpointSignature(
        key="schema-3-pre-feedback-indicators",
        configuration_schema_version=3,
        unit_sha256=(
            (
                "wrappers",
                "7e650ae06bbfdd33f9da9b99488de8202de64160440bced19719a07c74881e45",
            ),
            (
                "engine",
                "6420e4f75b36a1ac86691f2d16952c235862db62b57d297a51b8efc0f3379729",
            ),
            (
                "ignition_adapter",
                "ed76618204bb4f3838f806e090d45882409ad1fb0aa9462ae91d531806d9ca7b",
            ),
            (
                "ignition_controller",
                "ebb3cbeb3464ac3f53c6e8738a9b4f1fe729965fa7e24bccc0a5d790038b57f7",
            ),
            (
                "threshold_helper",
                "c1ab086bc1930c841e96be4cae34126af95e44821a03c2c177c33761a6336af7",
            ),
            ("feedback_arbiter", ERASED_FEEDBACK_ARBITER_SHA256),
        ),
        hook_values=PRE_FEEDBACK_ROLLING_HOOK_VALUES,
    ),
)

HISTORICAL_FEEDBACK_FRAME_COUNTS = ((10, 10), (15, 15))
HISTORICAL_FEEDBACK_ENGINE_SHA256 = frozenset(
    {
        "925a7ebc321e965bfed0fdfdc7e06287b6b794b0525226c4bd9a11187bc1f66f",
        "22c9c42f228cd827610a7e5ef848942e219e0461cbd2c9ba362ca8817130435f",
        "22c69075abb5f0c48207eb3c14a8c538f0fc17cf14f79951d55799186fc1a448",
    }
)


@dataclass(frozen=True)
class BuildResult:
    data: bytes
    rom: str
    detection: str
    input_state: str
    profile: Profile
    configuration: bytes
    source_sha256: str
    normalized_sha256: str
    map_stage_sha256: str
    output_sha256: str
    output_md5: str
    source_checksums: checksums.ChecksumValues
    output_checksums: checksums.ChecksumValues
    changed_bytes: int
    permitted_write_bytes: int
    checksum_changed_bytes: int
    preserved_map_copy_bytes: int
    map_instruction_count: int
    rolling_instruction_count: int
    rolling_code_entry_count: int
    diagnostic_count: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def md5(data):
    return hashlib.md5(data).hexdigest()


def _require_exact_keys(table, expected, context):
    if not isinstance(table, dict):
        raise BuildError(f"{context}: expected a TOML table")
    actual = set(table)
    if actual != set(expected):
        missing = sorted(set(expected) - actual)
        extra = sorted(actual - set(expected))
        raise BuildError(
            f"{context}: fields differ; missing={missing}; extra={extra}"
        )


def _require_integer(value, context):
    if type(value) is not int:
        raise BuildError(f"{context}: expected an integer")
    return value


def builtin_profile():
    """Return the conservative Map 1 RPM Hold profile."""
    return Profile(
        name=apply_rolling_launch.PROFILE_NAME,
        rom="JK08A",
        calibration=apply_rolling_launch.PROFILE_CALIBRATION,
        source="builtin",
        sha256=None,
    )


def load_profile(path):
    """Load one strict local TOML profile for the unified builder."""
    path = Path(path)
    try:
        raw_bytes = path.read_bytes()
        raw = tomllib.loads(raw_bytes.decode("utf-8"))
    except (OSError, UnicodeError, tomllib.TOMLDecodeError) as error:
        raise BuildError(f"{path}: cannot load profile: {error}") from error

    _require_exact_keys(raw, PROFILE_ROOT_KEYS, str(path))
    if (
        type(raw["schema_version"]) is not int
        or raw["schema_version"] != PROFILE_SCHEMA_VERSION
    ):
        raise BuildError(
            f"{path}: unsupported profile schema "
            f"{raw['schema_version']!r}"
        )
    rom = raw["rom"]
    if not isinstance(rom, str) or not rom.strip():
        raise BuildError(f"{path}: rom must be a non-empty string")
    rom = rom.strip().upper()
    name = raw["name"]
    if not isinstance(name, str) or not name.strip():
        raise BuildError(f"{path}: name must be a non-empty string")

    values = raw["rolling_launch"]
    _require_exact_keys(
        values, ROLLING_PROFILE_KEYS, f"{path} [rolling_launch]"
    )
    mode_name = values["mode"]
    if not isinstance(mode_name, str) or mode_name not in MODE_NAMES:
        raise BuildError(
            f"{path}: unsupported Rolling Launch mode {mode_name!r}; "
            f"expected one of {tuple(MODE_NAMES)}"
        )

    enabled_maps = values["enabled_maps"]
    if not isinstance(enabled_maps, list) or any(
        type(item) is not int for item in enabled_maps
    ):
        raise BuildError(f"{path}: enabled_maps must be an integer array")
    if len(enabled_maps) != len(set(enabled_maps)):
        raise BuildError(f"{path}: enabled_maps contains duplicates")
    if any(item < 1 or item > rolling_launch.SLOT_COUNT for item in enabled_maps):
        raise BuildError(f"{path}: enabled_maps values must be in 1..5")
    enable_mask = sum(1 << (item - 1) for item in enabled_maps)

    targets = values["target_commands"]
    if not isinstance(targets, list) or any(
        type(item) is not int for item in targets
    ):
        raise BuildError(f"{path}: target_commands must be an integer array")

    calibration = rolling_launch.Calibration(
        mode=MODE_NAMES[mode_name],
        enable_mask=enable_mask,
        coolant_min=_require_integer(values["coolant_min"], "coolant_min"),
        coolant_max=_require_integer(values["coolant_max"], "coolant_max"),
        min_speed=_require_integer(values["min_speed"], "min_speed"),
        retard_ramp_native=_require_integer(
            values["retard_ramp_native"], "retard_ramp_native"
        ),
        min_rpm_native=_require_integer(
            values["min_rpm_native"], "min_rpm_native"
        ),
        min_pedal=_require_integer(values["min_pedal"], "min_pedal"),
        rpm_offset_native=_require_integer(
            values["rpm_offset_native"], "rpm_offset_native"
        ),
        min_hysteresis_native=_require_integer(
            values["min_hysteresis_native"], "min_hysteresis_native"
        ),
        max_hysteresis_native=_require_integer(
            values["max_hysteresis_native"], "max_hysteresis_native"
        ),
        hysteresis_ratio_tenths=_require_integer(
            values["hysteresis_ratio_tenths"],
            "hysteresis_ratio_tenths",
        ),
        run_timeout_ticks=_require_integer(
            values["run_timeout_ticks"], "run_timeout_ticks"
        ),
        rearm_ticks=_require_integer(values["rearm_ticks"], "rearm_ticks"),
        target_commands=tuple(targets),
    )
    if not calibration.is_valid():
        raise BuildError(f"{path}: Rolling Launch calibration is invalid")
    configuration = calibration.to_bytes()
    if rolling_launch.Calibration.from_bytes(configuration) != calibration:
        raise BuildError(
            f"{path}: Rolling Launch calibration round trip differs"
        )
    return Profile(
        name=name.strip(),
        rom=rom,
        calibration=calibration,
        source=str(path),
        sha256=sha256(raw_bytes),
    )


def _range_offsets(ranges):
    return set(chain.from_iterable(
        range(item.start, item.end) for item in ranges
    ))


def _component_ranges(map_layout, launch_layout):
    return (
        map_switching_compose.composition_write_ranges(map_layout)
        + rolling_launch_compose.composition_write_ranges(launch_layout)
    )


def _component_offsets(map_layout, launch_layout):
    result = _range_offsets(_component_ranges(map_layout, launch_layout))
    overlap = result & set(checksums.checksum_byte_offsets())
    if overlap:
        raise BuildError(
            f"component write set overlaps checksum field at {min(overlap):#x}"
        )
    return result


def _read_integer(data, address, width, byte_order="big"):
    return int.from_bytes(data[address : address + width], byte_order)


def _expected_pointer_table(layout, family):
    return b"".join(
        address.to_bytes(4, layout.byte_order)
        for address in family.all_slot_addresses
    )


def _historical_configuration_is_valid(configuration, schema_version):
    if schema_version == rolling_launch.CONFIG_SCHEMA_VERSION:
        try:
            return rolling_launch.Calibration.from_bytes(
                configuration
            ).is_valid()
        except (TypeError, ValueError):
            return False
    if schema_version not in (1, 2):
        raise BuildError(
            "internal historical Rolling Launch schema is unsupported"
        )
    try:
        values = struct.unpack(">H8B6H5sBHH", bytes(configuration))
        rolling_launch.Mode(values[2])
        options = rolling_launch.Option(values[4])
    except (TypeError, ValueError, struct.error):
        return False
    common = all((
        values[0] == rolling_launch.CONFIG_MAGIC,
        values[1] == schema_version,
        0 <= values[3] <= 0x1F,
        options == rolling_launch.Option.NONE,
        0 <= values[5] <= values[6] <= 0xFF,
        0 < values[9] <= 0xFFFF,
        0 <= values[10] <= 0xFFFF,
        0 < values[11] <= 0xFFFF,
        0 < values[12] < values[9],
        0 < values[13] <= 0x7FFF,
        0 < values[14] <= 0x7FFF,
        len(values[15]) == rolling_launch.SLOT_COUNT,
        all(110 <= value <= 117 for value in values[15]),
        values[16] == 0,
        values[17] == rolling_launch.CONFIG_MAGIC_INVERSE,
        values[18] == rolling_launch.CONFIG_END_MARKER,
    ))
    if schema_version == 1:
        return common and 0 < values[7] <= 0xFF and values[8] == 0
    return all((
        common,
        0 <= values[7] <= 0xFF,
        0 < values[8] <= 0xFF,
        values[12] < values[8] <= values[11],
    ))


def _require_coherent_rolling_endpoint(
    source, layout, payloads, context
):
    """Accept only an absent, current, or registered historical endpoint."""
    expected_units = set(layout.assembly_unit_by_key)
    if set(payloads) != expected_units:
        raise BuildError(
            "internal Rolling Launch payload set differs from the layout"
        )

    unit_bytes = {
        unit.key: source[unit.span.start : unit.span.end]
        for unit in layout.assembly_units
    }
    hook_values = {
        hook.key: _read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        for hook in layout.hooks
    }
    did_values = {
        item.did: _read_integer(
            source, item.pointer_address, 4, layout.byte_order
        )
        for item in layout.diagnostics
    }
    configuration = source[
        layout.configuration.start : layout.configuration.end
    ]

    claimed_erased = all(
        source[span.start : span.end] == bytes([0xFF]) * span.size
        for span in layout.claimed_rom_ranges
    )
    hooks_stock = all(
        hook_values[hook.key] == hook.stock for hook in layout.hooks
    )
    dids_stock = all(
        did_values[item.did] == item.stock for item in layout.diagnostics
    )
    if claimed_erased and hooks_stock and dids_stock:
        return "absent"

    hooks_current = all(
        hook_values[hook.key] == hook.replacement for hook in layout.hooks
    )
    dids_current = all(
        did_values[item.did] == item.target for item in layout.diagnostics
    )
    if hooks_current and dids_current:
        current_units = all(
            unit_bytes[unit.key] == payloads[unit.key]
            for unit in layout.assembly_units
        )
        try:
            current_configuration = rolling_launch.Calibration.from_bytes(
                configuration
            ).is_valid()
        except (TypeError, ValueError):
            current_configuration = False
        if current_units and current_configuration:
            return "current"

    if dids_current:
        actual_hashes = {
            key: sha256(value) for key, value in unit_bytes.items()
        }
        for endpoint in HISTORICAL_ROLLING_ENDPOINTS:
            expected_hashes = dict(endpoint.unit_sha256)
            expected_hooks = dict(endpoint.hook_values)
            if (
                len(expected_hashes) != len(endpoint.unit_sha256)
                or set(expected_hashes) != expected_units
                or any(
                    len(digest) != 64
                    or any(
                        character not in "0123456789abcdef"
                        for character in digest
                    )
                    for digest in expected_hashes.values()
                )
                or len(expected_hooks) != len(endpoint.hook_values)
                or set(expected_hooks) != set(layout.hook_by_key)
                or any(
                    expected_hooks[hook.key]
                    not in (hook.stock, hook.replacement)
                    for hook in layout.hooks
                )
            ):
                raise BuildError(
                    f"internal historical Rolling Launch endpoint "
                    f"{endpoint.key!r} is invalid"
                )
            if (
                actual_hashes == expected_hashes
                and hook_values == expected_hooks
                and _historical_configuration_is_valid(
                    configuration, endpoint.configuration_schema_version
                )
            ):
                return endpoint.key

    raise BuildError(
        f"{context}: partial or unknown Rolling Launch state"
    )


def _require_complete_map_endpoint(
    source,
    map_layout,
    launch_layout,
    map_payloads,
    launch_payloads,
    context,
):
    """Accept one current map endpoint with an optional Rolling Launch layer."""
    for unit in map_layout.assembly_units:
        expected = map_switching_compose.endpoint_unit_bytes(
            map_layout, map_payloads, unit
        )
        actual = source[unit.span.start : unit.span.end]
        if actual != expected and unit.key == "cruise_feedback_engine":
            offset = (
                map_layout.feedback.phase_counts_address - unit.span.start
            )
            historical = []
            for on_frames, off_frames in HISTORICAL_FEEDBACK_FRAME_COUNTS:
                candidate = bytearray(expected)
                candidate[offset : offset + 2] = bytes(
                    (on_frames, off_frames)
                )
                historical.append(bytes(candidate))
            if (
                actual in historical
                or sha256(actual) in HISTORICAL_FEEDBACK_ENGINE_SHA256
            ):
                continue
        if actual != expected:
            raise BuildError(
                f"{context}: partial or unknown patch state; "
                f"map unit {unit.key} differs"
            )

    rolling_hook_values = {
        hook.address: hook.replacement for hook in launch_layout.hooks
    }
    for hook in map_layout.hooks:
        actual = _read_integer(
            source, hook.address, hook.width, map_layout.byte_order
        )
        allowed = {hook.replacement}
        if hook.address in rolling_hook_values:
            allowed.add(rolling_hook_values[hook.address])
        if actual not in allowed:
            raise BuildError(
                f"{context}: partial or unknown patch state; "
                f"map hook {hook.key} is {actual:#x}"
            )

    for family in map_layout.families:
        start = family.pointer_table
        expected = _expected_pointer_table(map_layout, family)
        actual = source[start : start + len(expected)]
        if actual != expected:
            raise BuildError(
                f"{context}: partial or unknown patch state; "
                f"pointer table {family.key} differs"
            )

    _require_coherent_rolling_endpoint(
        source, launch_layout, launch_payloads, context
    )


def _capture_map_copies(source, layout):
    return {
        (family.key, address): source[
            address : address + family.byte_length
        ]
        for family in layout.families
        for address in family.copies
    }


def _restore_map_copies(image, layout, copies):
    data = bytearray(image)
    for family in layout.families:
        for address in family.copies:
            key = (family.key, address)
            data[address : address + family.byte_length] = copies[key]
    return bytes(checksums.recalculate(data))


def _normalize_jk08a(source, source_name):
    map_layout = map_switching_layout.load_layout()
    launch_layout = rolling_launch_layout.load_layout()
    stock_image = romkit.load("JK08A")
    stock = stock_image.data
    source = bytes(source)

    try:
        source_verification = checksums.require_valid(source, source_name)
    except checksums.ChecksumError as error:
        raise BuildError(str(error)) from error

    map_payloads = apply_map_switching.load_payloads(map_layout)
    launch_payloads = rolling_launch_assembly.load_payloads(launch_layout)
    component_offsets = _component_offsets(map_layout, launch_layout)
    is_unpatched = all(
        source[offset] == stock[offset] for offset in component_offsets
    )
    saved_copies = None
    if is_unpatched:
        input_state = "compatible-base"
    else:
        _require_complete_map_endpoint(
            source,
            map_layout,
            launch_layout,
            map_payloads,
            launch_payloads,
            source_name,
        )
        saved_copies = _capture_map_copies(source, map_layout)
        input_state = "complete-runtime-migration"

    normalized = bytearray(source)
    for offset in component_offsets:
        normalized[offset] = stock[offset]
    normalized = bytes(checksums.recalculate(normalized))
    try:
        image = romkit.Image("JK08A", source_name, normalized)
        map_switching_layout.validate_compatible_image(
            map_layout, image, stock_image
        )
    except ValueError as error:
        raise BuildError(str(error)) from error

    return (
        normalized,
        input_state,
        saved_copies,
        source_verification,
        map_layout,
        launch_layout,
        map_payloads,
        launch_payloads,
        component_offsets,
    )


def _probe_jk08a(source):
    stock = romkit.load("JK08A").data
    if len(source) != len(stock):
        return False
    start = map_switching_layout.COMPATIBLE_IDENTITY_START
    end = map_switching_layout.COMPATIBLE_IDENTITY_END
    return source[start:end] == stock[start:end]


def _rom_probes():
    """Return the immutable-byte probe registry."""
    return {"JK08A": _probe_jk08a}


def select_rom(source, selector=AUTO_ROM):
    """Return ``(ROM, detection mode)`` after immutable-byte selection."""
    source = bytes(source)
    requested = str(selector).strip()
    probes = _rom_probes()
    if tuple(probes) != SUPPORTED_ROMS:
        raise BuildError("internal ROM probe registry differs from support list")
    if requested.lower() == AUTO_ROM:
        try:
            matches = [
                rom for rom, probe in probes.items() if probe(source)
            ]
        except (OSError, ValueError) as error:
            raise BuildError(f"ROM series detection failed: {error}") from error
        if not matches:
            raise BuildError(
                "ROM series could not be detected from immutable image bytes; "
                f"supported series: {', '.join(SUPPORTED_ROMS)}"
            )
        if len(matches) != 1:
            raise BuildError(
                f"ROM series detection is ambiguous: {', '.join(matches)}"
            )
        return matches[0], AUTO_ROM

    selected = requested.upper()
    if selected not in SUPPORTED_ROMS:
        raise BuildError(
            f"unsupported ROM series {selector!r}; supported series: "
            f"{', '.join(SUPPORTED_ROMS)}"
        )
    return selected, "explicit"


def _validate_preservation(source, output, component_offsets):
    checksum_offsets = set(checksums.checksum_byte_offsets())
    permitted = component_offsets | checksum_offsets
    changed = {
        offset
        for offset, (before, after) in enumerate(zip(source, output))
        if before != after
    }
    outside = changed - permitted
    if outside:
        raise BuildError(
            f"final image changes undeclared input byte at {min(outside):#x}"
        )
    return len(changed), len(permitted), len(changed & checksum_offsets)


def build_image(
    source,
    *,
    rom=AUTO_ROM,
    profile=None,
    source_name="<memory>",
):
    """Build and verify one complete ROM without writing files."""
    source = bytes(source)
    selected_rom, detection = select_rom(source, rom)
    profile = profile or builtin_profile()
    if not isinstance(profile, Profile):
        raise BuildError("profile must be a build_rom.Profile")
    if profile.rom != selected_rom:
        raise BuildError(
            f"profile ROM {profile.rom!r} does not match selected "
            f"ROM {selected_rom!r}"
        )
    if selected_rom != "JK08A":
        raise BuildError(f"no builder is registered for {selected_rom}")

    try:
        (
            normalized,
            input_state,
            saved_copies,
            source_verification,
            map_layout,
            launch_layout,
            map_payloads,
            launch_payloads,
            component_offsets,
        ) = _normalize_jk08a(source, source_name)

        map_result = apply_map_switching.patch_image(
            normalized,
            layout=map_layout,
            blobs=map_payloads,
            source_name=f"{source_name} normalized JK08A",
        )
        map_stage = map_result.data
        preserved_map_copy_bytes = 0
        if saved_copies is not None:
            map_stage = _restore_map_copies(
                map_stage, map_layout, saved_copies
            )
            preserved_map_copy_bytes = sum(
                len(blob) for blob in saved_copies.values()
            )
            checksums.require_valid(map_stage, "restored map stage")

        launch_result = apply_rolling_launch.patch_image(
            map_stage,
            calibration=profile.calibration,
            map_layout=map_layout,
            rolling_layout=launch_layout,
            map_payloads=map_payloads,
            rolling_payloads=launch_payloads,
            source_name=f"{source_name} complete map stage",
            expected_source_sha256=sha256(map_stage),
        )
        output_verification = checksums.require_valid(
            launch_result.data, "complete JK08A output"
        )
    except (
        BuildError,
        ValueError,
        checksums.ChecksumError,
        apply_map_switching.PatchError,
        apply_rolling_launch.PatchError,
    ) as error:
        if isinstance(error, BuildError):
            raise
        raise BuildError(str(error)) from error

    changed, permitted, checksum_changed = _validate_preservation(
        source, launch_result.data, component_offsets
    )
    if saved_copies is not None:
        final_copies = _capture_map_copies(launch_result.data, map_layout)
        if final_copies != saved_copies:
            raise BuildError("final image changes preserved alternate maps")

    return BuildResult(
        data=launch_result.data,
        rom=selected_rom,
        detection=detection,
        input_state=input_state,
        profile=profile,
        configuration=launch_result.configuration,
        source_sha256=sha256(source),
        normalized_sha256=sha256(normalized),
        map_stage_sha256=sha256(map_stage),
        output_sha256=sha256(launch_result.data),
        output_md5=md5(launch_result.data),
        source_checksums=source_verification.stored,
        output_checksums=output_verification.stored,
        changed_bytes=changed,
        permitted_write_bytes=permitted,
        checksum_changed_bytes=checksum_changed,
        preserved_map_copy_bytes=preserved_map_copy_bytes,
        map_instruction_count=map_layout.assembled_instruction_count,
        rolling_instruction_count=launch_result.instruction_count,
        rolling_code_entry_count=launch_result.code_entry_count,
        diagnostic_count=launch_result.diagnostic_count,
    )


def default_output_path(source):
    source = Path(source)
    return source.with_name(f"{source.stem}-complete.bin")


def _checksum_dict(values):
    return {name: value for name, value in values.items()}


def manifest_data(result, input_path, output_path):
    """Return the deterministic JSON manifest payload for one output."""
    calibration = result.profile.calibration
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "rom": result.rom,
        "detection": result.detection,
        "input": {
            "path": str(input_path),
            "state": result.input_state,
            "sha256": result.source_sha256,
            "checksums": _checksum_dict(result.source_checksums),
        },
        "profile": {
            "name": result.profile.name,
            "rom": result.profile.rom,
            "source": result.profile.source,
            "sha256": result.profile.sha256,
            "mode": calibration.mode.name,
            "enabled_maps": [
                index + 1
                for index in range(rolling_launch.SLOT_COUNT)
                if calibration.enabled_for(index)
            ],
            "configuration_hex": result.configuration.hex(),
        },
        "stages": {
            "normalized_sha256": result.normalized_sha256,
            "map_switching_sha256": result.map_stage_sha256,
        },
        "output": {
            "path": str(output_path),
            "sha256": result.output_sha256,
            "md5": result.output_md5,
            "checksums": _checksum_dict(result.output_checksums),
            "hardware_status": "UNTESTED",
        },
        "audit": {
            "changed_bytes": result.changed_bytes,
            "permitted_write_bytes": result.permitted_write_bytes,
            "checksum_changed_bytes": result.checksum_changed_bytes,
            "preserved_map_copy_bytes": result.preserved_map_copy_bytes,
            "map_instruction_count": result.map_instruction_count,
            "rolling_instruction_count": result.rolling_instruction_count,
            "rolling_code_entry_count": result.rolling_code_entry_count,
            "diagnostic_count": result.diagnostic_count,
        },
    }


def artifact_contents(result, input_path, output_path):
    output_path = Path(output_path)
    sha_path = output_path.with_name(f"{output_path.name}.sha256")
    md5_path = output_path.with_name(f"{output_path.name}.md5")
    manifest_path = output_path.with_name(f"{output_path.name}.manifest.json")
    manifest = json.dumps(
        manifest_data(result, input_path, output_path),
        indent=2,
        sort_keys=True,
    ) + "\n"
    return {
        output_path: result.data,
        sha_path: (
            f"{result.output_sha256} *{output_path.name}\n".encode("ascii")
        ),
        md5_path: (
            f"{result.output_md5} *{output_path.name}\n".encode("ascii")
        ),
        manifest_path: manifest.encode("utf-8"),
    }


def write_artifacts(result, input_path, output_path):
    """Create all output artifacts exclusively or accept an identical set."""
    artifacts = artifact_contents(result, input_path, output_path)
    for path, content in artifacts.items():
        if path.exists() and path.read_bytes() != content:
            raise BuildError(f"existing output artifact differs: {path}")
    created = []
    for path, content in artifacts.items():
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as output:
            output.write(content)
        created.append(path)
    return tuple(created)


def _format_checksums(values):
    return ",".join(f"{name}={value:#x}" for name, value in values.items())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="input ROM image")
    parser.add_argument(
        "--rom",
        default=AUTO_ROM,
        metavar="auto|JK08A",
        help="ROM series selector; defaults to immutable-byte detection",
    )
    parser.add_argument(
        "--profile",
        type=Path,
        help="strict local TOML calibration profile",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output path; defaults to INPUT-complete.bin",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="build and verify in memory without writing artifacts",
    )
    args = parser.parse_args(argv)

    try:
        source = args.input.read_bytes()
        profile = load_profile(args.profile) if args.profile else None
        result = build_image(
            source,
            rom=args.rom,
            profile=profile,
            source_name=str(args.input),
        )
    except (OSError, BuildError) as error:
        parser.error(str(error))

    calibration = result.profile.calibration
    print(
        f"status=PASS rom={result.rom} detection={result.detection} "
        f"input_state={result.input_state}"
    )
    print(
        f"source={args.input} source_sha256={result.source_sha256} "
        f"source_checksums={_format_checksums(result.source_checksums)}"
    )
    print(
        f"profile={result.profile.name} mode={calibration.mode.name} "
        f"enable_mask={calibration.enable_mask:#04x} "
        f"configuration={result.configuration.hex()}"
    )
    print(
        f"normalized_sha256={result.normalized_sha256} "
        f"map_stage_sha256={result.map_stage_sha256}"
    )
    print(
        f"output_sha256={result.output_sha256} md5={result.output_md5} "
        f"output_checksums={_format_checksums(result.output_checksums)}"
    )
    print(
        f"changed_bytes={result.changed_bytes} "
        f"permitted_write_bytes={result.permitted_write_bytes} "
        f"checksum_changed_bytes={result.checksum_changed_bytes} "
        f"preserved_map_copy_bytes={result.preserved_map_copy_bytes}"
    )

    if args.verify_only:
        print("no ROM file was written")
        return 0

    output_path = args.output or default_output_path(args.input)
    if output_path.resolve() == args.input.resolve():
        parser.error("input and output paths must differ")
    try:
        created = write_artifacts(
            result, args.input, output_path
        )
    except (OSError, BuildError) as error:
        parser.error(str(error))
    state = "created" if created else "already_exact"
    print(f"output={output_path} status={state} artifacts=4")
    print(f"manifest={output_path.name}.manifest.json hardware_status=UNTESTED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
