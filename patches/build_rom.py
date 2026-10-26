#!/usr/bin/env python3
"""Build one complete production ROM with every supported firmware runtime.

The CLI detects the exact ROM identity from immutable image bytes by default or
accepts an explicit ``--rom`` selector. Exact-code families share their
canonical executable profile, while near-code and cross-generation targets use
explicit address layouts and independently assembled payloads. Each member
retains its own calibration, identity, capabilities, and checksum layout.

Compatible unpatched inputs retain their calibration and configuration. A
complete current or historical composition may also be rebuilt: all alternate
map bytes are preserved while every builder-owned executable span, hook,
diagnostic pointer, configuration record, and checksum is regenerated. A
current-schema configuration that differs from the built-in profile requires
an explicit replacement profile. Unknown or partial patch states are rejected
before an output is written.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from functools import lru_cache
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
from patches import apply_can_telemetry
from patches import can_telemetry
from patches import can_telemetry_compose
from patches import can_telemetry_layout
from patches import jk08a_checksums as canonical_checksums
from patches import jk08a_runtime_reservations
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch
from patches import rolling_launch_compose
from patches import rom_checksums
from patches import runtime_targets
from tools.mapkit import rom as romkit
from tools import rom_homology


AUTO_ROM = "auto"
ROM_SERIES = "sh7058_7mfkavn86"
CANONICAL_ROM = "JK08A"
SUPPORTED_ROMS = runtime_targets.SUPPORTED_ROMS
PROFILE_SCHEMA_VERSION = 2
MANIFEST_SCHEMA_VERSION = 3
TOOL_NAME = "patches/build_rom.py"
OBSERVE_PROFILE_NAME = "observe"

PROFILE_REQUIRED_ROOT_KEYS = frozenset(
    ("schema_version", "rom", "name", "rolling_launch")
)
PROFILE_OPTIONAL_ROOT_KEYS = frozenset(("can_telemetry",))
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
TELEMETRY_PROFILE_KEYS = frozenset(
    ("enabled", "can_id", "profile", "tick_divisor")
)


class BuildError(ValueError):
    """Raised when ROM selection, composition, or artifact checks fail."""


@dataclass(frozen=True)
class SeriesContext:
    key: str
    canonical_rom: str
    members: tuple[str, ...]
    images: dict[str, rom_homology.Image]


@dataclass(frozen=True)
class Profile:
    name: str
    rom: str
    calibration: rolling_launch.Calibration
    telemetry: can_telemetry.Configuration
    source: str
    sha256: str | None


@dataclass(frozen=True)
class RollingEndpointSignature:
    key: str
    configuration_schema_version: int
    unit_sha256: tuple[tuple[str, str], ...]
    hook_values: tuple[tuple[str, int], ...]
    carries_current_telemetry: bool = False


PRE_FEEDBACK_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D35E0),
)
CURRENT_ROLLING_HOOK_VALUES = (
    ("displaced_periodic_task", 0x000D3860),
    ("selector_arbitration", 0x000D3880),
    ("startup_state_clear", 0x000D38A0),
    ("primary_ignition_command", 0x000D3EA0),
    ("feedback_arbitration", 0x000D41E0),
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
    # The arbiter of this endpoint emits ASCD state 6 for a failed held attempt
    # and state 7 for ACTIVE. Every other unit and every hook equals the
    # current endpoint, so the current CAN telemetry layer is valid above it.
    RollingEndpointSignature(
        key="schema-3-state-6-7-indicators",
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
            (
                "feedback_arbiter",
                "0ec18b26a0ef6556bcb5f6056a2a9b988f8c895f65ec6b2b3665352ce73fb4dc",
            ),
        ),
        hook_values=CURRENT_ROLLING_HOOK_VALUES,
        carries_current_telemetry=True,
    ),
)
TELEMETRY_LOWER_ROLLING_STATES = frozenset(
    {"current"}
    | {
        endpoint.key
        for endpoint in HISTORICAL_ROLLING_ENDPOINTS
        if endpoint.carries_current_telemetry
    }
)

HISTORICAL_FEEDBACK_FRAME_COUNTS = ((10, 10), (15, 15))
# Exact JK08A engine fingerprints that emit ASCD state 6 during the ON phase:
# the partial 0x9F mask and the full 0x8F mask, each with 10/10, 15/15, and
# 30/30 phase counts.
HISTORICAL_FEEDBACK_ENGINE_SHA256 = frozenset(
    {
        "925a7ebc321e965bfed0fdfdc7e06287b6b794b0525226c4bd9a11187bc1f66f",
        "22c9c42f228cd827610a7e5ef848942e219e0461cbd2c9ba362ca8817130435f",
        "22c69075abb5f0c48207eb3c14a8c538f0fc17cf14f79951d55799186fc1a448",
        "0e0501f3d91e18a17c6a9bf7c4ebd187809c094fbf701f9d2864fd4792f9b32e",
        "017a1c01d0f2fba835a93714d1ce9e20a07e5ff709fc41ed997bf92e7124a13a",
        "d64600dd5be497cf49df077956e2ac86159b0366ecc485b33c5633e146b4e66a",
    }
)


@dataclass(frozen=True)
class BuildResult:
    data: bytes
    rom: str
    series: str
    detection: str
    input_state: str
    profile: Profile
    input_configuration: bytes
    input_telemetry_configuration: bytes
    input_telemetry_mailbox_record: bytes
    configuration: bytes
    telemetry_configuration: bytes
    telemetry_mailbox_record: bytes
    source_sha256: str
    normalized_sha256: str
    map_stage_sha256: str
    rolling_stage_sha256: str
    output_sha256: str
    output_md5: str
    source_checksums: rom_checksums.ChecksumValues
    output_checksums: rom_checksums.ChecksumValues
    changed_bytes: int
    permitted_write_bytes: int
    checksum_changed_bytes: int
    preserved_map_copy_bytes: int
    map_instruction_count: int
    rolling_instruction_count: int
    rolling_code_entry_count: int
    telemetry_instruction_count: int
    telemetry_code_entry_count: int
    diagnostic_count: int


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def md5(data):
    return hashlib.md5(data).hexdigest()


@lru_cache(maxsize=None)
def _series_context(rom=CANONICAL_ROM):
    """Load and validate the registered runtime family for one exact ROM."""
    try:
        images = rom_homology.load_images()
        _settings, families, relationships = rom_homology.load_homology()
        rom_homology.validate_families(images, families)
        rom_homology.validate_relationships(families, relationships)
    except rom_homology.HomologyError as error:
        raise BuildError(f"ROM family registry is invalid: {error}") from error

    rom = str(rom).upper()
    family_key = next(
        (
            key for key, row in families.items()
            if rom in row.get("members", ())
        ),
        None,
    )
    family = families.get(family_key)
    if not isinstance(family, dict):
        raise BuildError(f"ROM family registry has no runtime family for {rom}")
    members = tuple(family.get("members", ()))
    expected = {
        runtime_targets.EXACT_FAMILY: {
            "kind": "exact-code",
            "canonical": CANONICAL_ROM,
            "mcu": "SH7058",
            "flash_size": 0x100000,
            "same_address_inheritance": True,
            "members": runtime_targets.EXACT_ROMS,
        },
        runtime_targets.RELOCATED_8MFK_FAMILY: {
            "kind": "near-code",
            "canonical": "JK00D",
            "mcu": "SH7058",
            "flash_size": 0x100000,
            "same_address_inheritance": False,
            "members": runtime_targets.RELOCATED_8MFK_ROMS,
        },
        runtime_targets.SH7059_1ND_FAMILY: {
            "kind": "exact-code",
            "canonical": "1ND0A",
            "mcu": "SH7059",
            "flash_size": 0x180000,
            "same_address_inheritance": True,
            "members": runtime_targets.SH7059_1ND_ROMS,
        },
        runtime_targets.SH7059_1ME3B_FAMILY: {
            "kind": "distinct-code",
            "canonical": "1ME3B",
            "mcu": "SH7059",
            "flash_size": 0x180000,
            "same_address_inheritance": False,
            "members": runtime_targets.SH7059_1ME3B_ROMS,
        },
        runtime_targets.SH7058_JK78C_FAMILY: {
            "kind": "distinct-code",
            "canonical": "JK78C",
            "mcu": "SH7058",
            "flash_size": 0x100000,
            "same_address_inheritance": False,
            "members": runtime_targets.SH7058_JK78C_ROMS,
        },
    }.get(family_key)
    if expected is None or any((
        family.get("kind") != expected["kind"],
        family.get("canonical") != expected["canonical"],
        family.get("mcu") != expected["mcu"],
        family.get("flash_size") != expected["flash_size"],
        family.get("same_address_inheritance")
        is not expected["same_address_inheritance"],
        members != expected["members"],
    )):
        raise BuildError(
            "ROM family registry differs from the locked builder contract"
        )
    return SeriesContext(
        key=family_key,
        canonical_rom=expected["canonical"],
        members=members,
        images={rom: images[rom] for rom in members},
    )


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


def builtin_profile(rom=ROM_SERIES):
    """Return the conservative profile permitted by the target family."""
    observe_only = str(rom).lower() in {
        runtime_targets.SH7059_1ND_FAMILY,
        runtime_targets.SH7059_1ME3B_FAMILY,
        runtime_targets.SH7058_JK78C_FAMILY,
    }
    calibration = (
        rolling_launch.Calibration()
        if observe_only
        else apply_rolling_launch.PROFILE_CALIBRATION
    )
    return Profile(
        name=(
            OBSERVE_PROFILE_NAME
            if observe_only
            else apply_rolling_launch.PROFILE_NAME
        ),
        rom=rom,
        calibration=calibration,
        telemetry=can_telemetry.default_configuration(),
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

    if not isinstance(raw, dict):
        raise BuildError(f"{path}: expected a TOML table")
    missing = sorted(PROFILE_REQUIRED_ROOT_KEYS - set(raw))
    extra = sorted(
        set(raw) - PROFILE_REQUIRED_ROOT_KEYS - PROFILE_OPTIONAL_ROOT_KEYS
    )
    if missing or extra:
        raise BuildError(
            f"{path}: fields differ; missing={missing}; extra={extra}"
        )
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
    rom = rom.strip()
    rom = rom.lower() if rom.lower().startswith("sh") else rom.upper()
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
    telemetry_values = raw.get("can_telemetry")
    if telemetry_values is None:
        telemetry = can_telemetry.default_configuration()
    else:
        _require_exact_keys(
            telemetry_values,
            TELEMETRY_PROFILE_KEYS,
            f"{path} [can_telemetry]",
        )
        enabled = telemetry_values["enabled"]
        profile_name = telemetry_values["profile"]
        if type(enabled) is not bool:
            raise BuildError(
                f"{path}: can_telemetry.enabled must be a boolean"
            )
        if not isinstance(profile_name, str):
            raise BuildError(
                f"{path}: can_telemetry.profile must be a string"
            )
        telemetry = can_telemetry.Configuration(
            enabled=enabled,
            can_id=_require_integer(
                telemetry_values["can_id"], "can_telemetry.can_id"
            ),
            profile=profile_name,
            tick_divisor=_require_integer(
                telemetry_values["tick_divisor"],
                "can_telemetry.tick_divisor",
            ),
        )
        if not telemetry.is_valid():
            raise BuildError(f"{path}: CAN telemetry configuration is invalid")
        try:
            encoded = telemetry.to_bytes()
            decoded = can_telemetry.Configuration.from_bytes(encoded)
        except ValueError as error:
            raise BuildError(f"{path}: {error}") from error
        if decoded != telemetry:
            raise BuildError(
                f"{path}: CAN telemetry configuration round trip differs"
            )
    return Profile(
        name=name.strip(),
        rom=rom,
        calibration=calibration,
        telemetry=telemetry,
        source=str(path),
        sha256=sha256(raw_bytes),
    )


def _range_offsets(ranges):
    return set(chain.from_iterable(
        range(item.start, item.end) for item in ranges
    ))


def _component_ranges(map_layout, launch_layout, telemetry_layout=None):
    telemetry_layout = telemetry_layout or can_telemetry_layout.load_layout()
    return (
        map_switching_compose.composition_write_ranges(map_layout)
        + (
            ()
            if launch_layout is None
            else rolling_launch_compose.composition_write_ranges(launch_layout)
        )
        + can_telemetry_compose.composition_write_ranges(telemetry_layout)
    )


def _component_offsets(
    map_layout, launch_layout, telemetry_layout=None,
    checksum_layout=None,
):
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    result = _range_offsets(
        _component_ranges(map_layout, launch_layout, telemetry_layout)
    )
    overlap = result & set(
        rom_checksums.checksum_byte_offsets(checksum_layout)
    )
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


def _require_coherent_telemetry_endpoint(
    source, layout, payloads, context, launch_layout=None
):
    """Accept only an absent or complete current CAN telemetry endpoint."""
    expected_units = set(layout.assembly_unit_by_key)
    if set(payloads) != expected_units:
        raise BuildError(
            "internal CAN telemetry payload set differs from the layout"
        )

    erased_units = all(
        source[unit.span.start : unit.span.end]
        == bytes([0xFF]) * unit.span.size
        for unit in layout.assembly_units
    )
    current_units = all(
        source[unit.span.start : unit.span.end] == payloads[unit.key]
        for unit in layout.assembly_units
    )
    configuration = source[
        layout.configuration.start : layout.configuration.end
    ]
    configuration_erased = (
        configuration == bytes([0xFF]) * layout.configuration.size
    )
    reserve_erased = (
        source[layout.reserved_rom.start : layout.reserved_rom.end]
        == bytes([0xFF]) * layout.reserved_rom.size
    )
    hook_values = {
        hook.key: _read_integer(
            source, hook.address, hook.width, layout.byte_order
        )
        for hook in layout.hooks
    }
    lower_hook_values = {}
    if launch_layout is not None:
        lower_hook_values = {
            hook.address: hook.stock for hook in launch_layout.hooks
        }
    hooks_stock = all(
        hook_values[hook.key]
        in ({hook.stock} | (
            {lower_hook_values[hook.address]}
            if hook.address in lower_hook_values
            else set()
        ))
        for hook in layout.hooks
    )
    hooks_current = all(
        hook_values[hook.key] == hook.replacement for hook in layout.hooks
    )
    record_start = layout.mailbox_record_address
    mailbox_record = source[record_start : record_start + 4]
    stock_mailbox_record = layout.mailbox_record_stock.to_bytes(
        4, layout.byte_order
    )
    if all((
        erased_units,
        configuration_erased,
        reserve_erased,
        hooks_stock,
        mailbox_record == stock_mailbox_record,
    )):
        return "absent"

    try:
        model = can_telemetry.Configuration.from_bytes(configuration)
        configuration_current = model.to_bytes() == configuration
    except (TypeError, ValueError):
        model = None
        configuration_current = False
    if all((
        current_units,
        configuration_current,
        reserve_erased,
        hooks_current,
        model is not None and mailbox_record == model.mailbox_record(),
    )):
        return "current"

    raise BuildError(f"{context}: partial or unknown CAN telemetry state")


def _strip_telemetry_endpoint(
    source, layout, state, checksum_layout=None
):
    """Restore the exact lower-layer bytes used by endpoint validation."""
    if state == "absent":
        return bytes(source)
    if state != "current":
        raise BuildError(f"unsupported CAN telemetry endpoint {state!r}")
    data = bytearray(source)
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = (
            bytes([0xFF]) * unit.span.size
        )
    data[layout.configuration.start : layout.configuration.end] = (
        bytes([0xFF]) * layout.configuration.size
    )
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
            hook.width, layout.byte_order
        )
    start = layout.mailbox_record_address
    data[start : start + 4] = layout.mailbox_record_stock.to_bytes(
        4, layout.byte_order
    )
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    return bytes(rom_checksums.recalculate(data, checksum_layout))


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

    rolling_hook_values = (
        {}
        if launch_layout is None
        else {
            hook.address: hook.replacement for hook in launch_layout.hooks
        }
    )
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

    if launch_layout is None:
        if launch_payloads:
            raise BuildError(
                "disabled Rolling Launch has unexpected payloads"
            )
        return "current"
    return _require_coherent_rolling_endpoint(
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


def _restore_map_copies(image, layout, copies, checksum_layout=None):
    data = bytearray(image)
    for family in layout.families:
        for address in family.copies:
            key = (family.key, address)
            data[address : address + family.byte_length] = copies[key]
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    return bytes(rom_checksums.recalculate(data, checksum_layout))


def _normalize_runtime(source, source_name, target):
    if target.family == runtime_targets.EXACT_FAMILY:
        jk08a_runtime_reservations.load_ledger()
    map_layout = target.map_layout
    launch_layout = target.rolling_layout
    telemetry_layout = target.telemetry_layout
    checksum_layout = target.checksum_layout
    stock_image = target.stock_image
    stock = stock_image.data
    source = bytes(source)

    try:
        source_verification = rom_checksums.require_valid(
            source, checksum_layout, source_name
        )
    except rom_checksums.ChecksumError as error:
        raise BuildError(str(error)) from error

    map_payloads = target.map_payloads
    launch_payloads = target.rolling_payloads
    telemetry_payloads = target.telemetry_payloads
    component_offsets = _component_offsets(
        map_layout, launch_layout, telemetry_layout, checksum_layout
    )
    is_unpatched = all(
        source[offset] == stock[offset] for offset in component_offsets
    )
    saved_copies = None
    input_configuration = b""
    input_telemetry_configuration = b""
    input_telemetry_mailbox_record = b""
    if is_unpatched:
        input_state = "compatible-base"
    else:
        telemetry_state = _require_coherent_telemetry_endpoint(
            source,
            telemetry_layout,
            telemetry_payloads,
            source_name,
            launch_layout,
        )
        lower_source = _strip_telemetry_endpoint(
            source, telemetry_layout, telemetry_state, checksum_layout
        )
        rolling_state = _require_complete_map_endpoint(
            lower_source,
            map_layout,
            launch_layout,
            map_payloads,
            launch_payloads,
            source_name,
        )
        if (
            telemetry_state == "current"
            and rolling_state not in TELEMETRY_LOWER_ROLLING_STATES
        ):
            raise BuildError(
                f"{source_name}: current CAN telemetry is not layered "
                "over the current lower runtime endpoint"
            )
        saved_copies = _capture_map_copies(source, map_layout)
        if launch_layout is not None and rolling_state != "absent":
            input_configuration = source[
                launch_layout.configuration.start : launch_layout.configuration.end
            ]
        if telemetry_state == "current":
            input_telemetry_configuration = source[
                telemetry_layout.configuration.start : telemetry_layout.configuration.end
            ]
            record = telemetry_layout.mailbox_record_address
            input_telemetry_mailbox_record = source[record : record + 4]
        input_state = "complete-runtime-migration"

    normalized = bytearray(source)
    for offset in component_offsets:
        normalized[offset] = stock[offset]
    normalized = bytes(rom_checksums.recalculate(
        normalized, checksum_layout
    ))
    try:
        image = romkit.Image(target.rom, source_name, normalized)
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
        telemetry_layout,
        map_payloads,
        launch_payloads,
        telemetry_payloads,
        component_offsets,
        stock_image,
        checksum_layout,
        input_configuration,
        input_telemetry_configuration,
        input_telemetry_mailbox_record,
    )


def _probe_rom(source, rom, images):
    stock = images[rom].data
    if len(source) != len(stock):
        return False
    start = map_switching_layout.COMPATIBLE_IDENTITY_START
    end = map_switching_layout.COMPATIBLE_IDENTITY_END
    return source[start:end] == stock[start:end]


def _rom_probes():
    """Return the immutable-byte probe registry."""
    _series_context(CANONICAL_ROM)
    _series_context("JK00D")
    _series_context("1ND0A")
    images = rom_homology.load_images()
    return {
        rom: (
            lambda source, rom=rom: _probe_rom(source, rom, images)
        )
        for rom in SUPPORTED_ROMS
    }


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
                "ROM identity could not be detected from immutable image bytes; "
                f"supported ROMs: {', '.join(SUPPORTED_ROMS)}"
            )
        if len(matches) != 1:
            raise BuildError(
                f"ROM series detection is ambiguous: {', '.join(matches)}"
            )
        return matches[0], AUTO_ROM

    selected = requested.upper()
    if selected not in SUPPORTED_ROMS:
        raise BuildError(
            f"unsupported ROM selector {selector!r}; supported ROMs: "
            f"{', '.join(SUPPORTED_ROMS)}"
        )
    return selected, "explicit"


def _validate_preservation(
    source, output, component_offsets, checksum_layout=None
):
    checksum_layout = checksum_layout or canonical_checksums.LAYOUT
    checksum_offsets = set(
        rom_checksums.checksum_byte_offsets(checksum_layout)
    )
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


def _require_profile_for_changed_settings(profile, launch_data, telemetry_data):
    current_launch = None
    if launch_data:
        calibration = rolling_launch.Calibration.from_bytes(launch_data)
        # Older schemas have their own endpoint validation and no current fields.
        if calibration.is_valid():
            current_launch = calibration
    current_telemetry = (
        can_telemetry.Configuration.from_bytes(telemetry_data)
        if telemetry_data else None
    )
    changed = []
    for component, current, expected in (
        ("rolling_launch", current_launch, profile.calibration),
        ("can_telemetry", current_telemetry, profile.telemetry),
    ):
        if current is not None:
            changed.extend(
                f"{component}.{name}"
                for name, value in asdict(current).items()
                if value != getattr(expected, name)
            )
    if changed:
        raise BuildError(
            "input runtime settings differ from the built-in profile: "
            + ", ".join(changed)
            + "; supply --profile to explicitly replace these settings"
        )


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
    context = _series_context(selected_rom)
    profile_supplied = profile is not None
    if not profile_supplied:
        profile = builtin_profile(context.key)
    if not isinstance(profile, Profile):
        raise BuildError("profile must be a build_rom.Profile")
    if profile.rom not in (selected_rom, context.key):
        raise BuildError(
            f"profile scope {profile.rom!r} does not match selected ROM "
            f"{selected_rom!r} or series {context.key!r}"
        )
    if (
        not isinstance(profile.telemetry, can_telemetry.Configuration)
        or not profile.telemetry.is_valid()
    ):
        raise BuildError("profile CAN telemetry configuration is invalid")
    try:
        target = runtime_targets.load_runtime_target(selected_rom)
        if target.rolling_layout is None and (
            profile.calibration.mode != rolling_launch.Mode.OBSERVE
            or profile.calibration.enable_mask != 0
        ):
            raise BuildError(
                f"{selected_rom}: Rolling Launch is unsupported; profile "
                "must use observe mode with no enabled maps"
            )
        (
            normalized,
            input_state,
            saved_copies,
            source_verification,
            map_layout,
            launch_layout,
            telemetry_layout,
            map_payloads,
            launch_payloads,
            telemetry_payloads,
            component_offsets,
            stock_image,
            checksum_layout,
            input_configuration,
            input_telemetry_configuration,
            input_telemetry_mailbox_record,
        ) = _normalize_runtime(
            source, source_name, target
        )
        if not profile_supplied:
            _require_profile_for_changed_settings(
                profile, input_configuration, input_telemetry_configuration
            )

        map_result = apply_map_switching.patch_image(
            normalized,
            layout=map_layout,
            blobs=map_payloads,
            source_name=f"{source_name} normalized {selected_rom}",
            stock_image=stock_image,
            checksum_layout=checksum_layout,
        )
        map_stage = map_result.data
        preserved_map_copy_bytes = 0
        if saved_copies is not None:
            map_stage = _restore_map_copies(
                map_stage, map_layout, saved_copies, checksum_layout
            )
            preserved_map_copy_bytes = sum(
                len(blob) for blob in saved_copies.values()
            )
            rom_checksums.require_valid(
                map_stage, checksum_layout, "restored map stage"
            )

        launch_result = None
        if launch_layout is not None:
            launch_result = apply_rolling_launch.patch_image(
                map_stage,
                calibration=profile.calibration,
                map_layout=map_layout,
                rolling_layout=launch_layout,
                map_payloads=map_payloads,
                rolling_payloads=launch_payloads,
                source_name=f"{source_name} complete map stage",
                expected_source_sha256=sha256(map_stage),
                checksum_layout=checksum_layout,
            )
            rolling_stage = launch_result.data
        else:
            rolling_stage = map_stage
        telemetry_result = apply_can_telemetry.patch_image(
            rolling_stage,
            configuration=profile.telemetry,
            telemetry_layout=telemetry_layout,
            telemetry_payloads=telemetry_payloads,
            launch_layout=launch_layout,
            launch_payloads=launch_payloads,
            source_name=f"{source_name} complete lower runtime stage",
            expected_source_sha256=sha256(rolling_stage),
            checksum_layout=checksum_layout,
            require_rolling_endpoint=launch_layout is not None,
        )
        output_verification = rom_checksums.require_valid(
            telemetry_result.data,
            checksum_layout,
            f"complete {selected_rom} output",
        )
    except (
        BuildError,
        ValueError,
        rom_checksums.ChecksumError,
        runtime_targets.RuntimeTargetError,
        apply_map_switching.PatchError,
        apply_rolling_launch.PatchError,
        apply_can_telemetry.PatchError,
    ) as error:
        if isinstance(error, BuildError):
            raise
        raise BuildError(str(error)) from error

    changed, permitted, checksum_changed = _validate_preservation(
        source, telemetry_result.data, component_offsets, checksum_layout
    )
    if saved_copies is not None:
        final_copies = _capture_map_copies(telemetry_result.data, map_layout)
        if final_copies != saved_copies:
            raise BuildError("final image changes preserved alternate maps")

    return BuildResult(
        data=telemetry_result.data,
        rom=selected_rom,
        series=context.key,
        detection=detection,
        input_state=input_state,
        profile=profile,
        input_configuration=input_configuration,
        input_telemetry_configuration=input_telemetry_configuration,
        input_telemetry_mailbox_record=input_telemetry_mailbox_record,
        configuration=(
            b"" if launch_result is None else launch_result.configuration
        ),
        telemetry_configuration=telemetry_result.configuration,
        telemetry_mailbox_record=telemetry_result.mailbox_record,
        source_sha256=sha256(source),
        normalized_sha256=sha256(normalized),
        map_stage_sha256=sha256(map_stage),
        rolling_stage_sha256=sha256(rolling_stage),
        output_sha256=sha256(telemetry_result.data),
        output_md5=md5(telemetry_result.data),
        source_checksums=source_verification.stored,
        output_checksums=output_verification.stored,
        changed_bytes=changed,
        permitted_write_bytes=permitted,
        checksum_changed_bytes=checksum_changed,
        preserved_map_copy_bytes=preserved_map_copy_bytes,
        map_instruction_count=map_layout.assembled_instruction_count,
        rolling_instruction_count=(
            0 if launch_result is None else launch_result.instruction_count
        ),
        rolling_code_entry_count=(
            0 if launch_result is None else launch_result.code_entry_count
        ),
        telemetry_instruction_count=telemetry_result.instruction_count,
        telemetry_code_entry_count=telemetry_result.code_entry_count,
        diagnostic_count=(
            0 if launch_result is None else launch_result.diagnostic_count
        ),
    )


def default_output_path(source):
    try:
        return apply_map_switching.default_output_path(source, "complete")
    except apply_map_switching.PatchError as error:
        raise BuildError(str(error)) from error


def _checksum_dict(values):
    return {name: value for name, value in values.items()}


def _runtime_configuration_data(launch_data, telemetry_data, mailbox_record):
    launch = None
    if launch_data:
        calibration = rolling_launch.Calibration.from_bytes(launch_data)
        settings = asdict(calibration) if calibration.is_valid() else None
        if settings is not None:
            settings["mode"] = rolling_launch.Mode(calibration.mode).name
        launch = {"configuration_hex": launch_data.hex(), "settings": settings}
    telemetry = None
    if telemetry_data:
        telemetry = {
            "configuration_hex": telemetry_data.hex(),
            "mailbox_record_hex": mailbox_record.hex(),
            "settings": asdict(can_telemetry.Configuration.from_bytes(telemetry_data)),
        }
    return {"rolling_launch": launch, "can_telemetry": telemetry}


def manifest_data(result, input_path, output_path):
    """Return the deterministic JSON manifest payload for one output."""
    calibration = result.profile.calibration
    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "series": result.series,
        "rom": result.rom,
        "detection": result.detection,
        "input": {
            "path": str(Path(input_path).resolve()),
            "state": result.input_state,
            "sha256": result.source_sha256,
            "checksums": _checksum_dict(result.source_checksums),
            "configuration": _runtime_configuration_data(
                result.input_configuration,
                result.input_telemetry_configuration,
                result.input_telemetry_mailbox_record,
            ),
        },
        "profile": {
            "name": result.profile.name,
            "rom": result.profile.rom,
            "source": result.profile.source,
            "sha256": result.profile.sha256,
            "mode": calibration.mode.name,
            "rolling_launch_supported": result.rolling_instruction_count > 0,
            "enabled_maps": [
                index + 1
                for index in range(rolling_launch.SLOT_COUNT)
                if calibration.enabled_for(index)
            ],
            "configuration_hex": result.configuration.hex(),
            "can_telemetry": {
                "enabled": result.profile.telemetry.enabled,
                "can_id": result.profile.telemetry.can_id,
                "wire_profile": result.profile.telemetry.profile,
                "tick_divisor": result.profile.telemetry.tick_divisor,
                "configuration_hex": result.telemetry_configuration.hex(),
                "mailbox_record_hex": result.telemetry_mailbox_record.hex(),
            },
        },
        "stages": {
            "normalized_sha256": result.normalized_sha256,
            "map_switching_sha256": result.map_stage_sha256,
            "rolling_launch_sha256": result.rolling_stage_sha256,
            "can_telemetry_sha256": result.output_sha256,
        },
        "output": {
            "path": str(Path(output_path).resolve()),
            "sha256": result.output_sha256,
            "md5": result.output_md5,
            "checksums": _checksum_dict(result.output_checksums),
            "hardware_status": "UNTESTED",
            "configuration": _runtime_configuration_data(
                result.configuration,
                result.telemetry_configuration,
                result.telemetry_mailbox_record,
            ),
        },
        "audit": {
            "changed_bytes": result.changed_bytes,
            "permitted_write_bytes": result.permitted_write_bytes,
            "checksum_changed_bytes": result.checksum_changed_bytes,
            "preserved_map_copy_bytes": result.preserved_map_copy_bytes,
            "map_instruction_count": result.map_instruction_count,
            "rolling_instruction_count": result.rolling_instruction_count,
            "rolling_code_entry_count": result.rolling_code_entry_count,
            "telemetry_instruction_count": (
                result.telemetry_instruction_count
            ),
            "telemetry_code_entry_count": (
                result.telemetry_code_entry_count
            ),
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
    try:
        return apply_map_switching._publish_artifacts(
            artifacts, Path(output_path)
        )
    except apply_map_switching.PatchError as error:
        raise BuildError(str(error)) from error


def _format_checksums(values):
    return ",".join(f"{name}={value:#x}" for name, value in values.items())


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="input ROM image")
    parser.add_argument(
        "--rom",
        default=AUTO_ROM,
        metavar="auto|ROM",
        help="exact ROM selector; defaults to immutable-byte detection",
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
        f"status=PASS series={result.series} rom={result.rom} "
        f"detection={result.detection} "
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
    telemetry = result.profile.telemetry
    print(
        f"can_telemetry_enabled={str(telemetry.enabled).lower()} "
        f"can_id={telemetry.can_id:#05x} "
        f"wire_profile={telemetry.profile} "
        f"tick_divisor={telemetry.tick_divisor} "
        f"configuration={result.telemetry_configuration.hex()} "
        f"mailbox_record={result.telemetry_mailbox_record.hex()}"
    )
    print(
        f"normalized_sha256={result.normalized_sha256} "
        f"map_stage_sha256={result.map_stage_sha256} "
        f"rolling_stage_sha256={result.rolling_stage_sha256}"
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

    try:
        output_path = args.output or default_output_path(args.input)
        if output_path.resolve() == args.input.resolve():
            parser.error("input and output paths must differ")
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
