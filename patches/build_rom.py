#!/usr/bin/env python3
"""Build one complete production ROM with every supported firmware runtime.

The CLI detects the exact ROM identity from immutable image bytes by default or
accepts an explicit ``--rom`` selector. Exact-code families share their
canonical executable profile, while near-code and cross-generation targets use
explicit address layouts and independently assembled payloads. Each member
retains its own calibration, identity, capabilities, and checksum layout.

The default input is byte-identical to the registered stock image of the
selected ROM. ``--upgrade`` validates an existing image, extracts its calibration
and expressed runtime settings, and transfers them over a fresh stock build.
The separate ``extract_calibration.py`` and ``apply_calibration.py`` commands
expose those transfer stages for an explicit local workflow.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from functools import lru_cache
import hashlib
from itertools import chain
import json
from pathlib import Path
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
from tools import rom_homology


AUTO_ROM = "auto"
ROM_SERIES = "sh7058_7mfkavn86"
CANONICAL_ROM = "JK08A"
SUPPORTED_ROMS = runtime_targets.SUPPORTED_ROMS
PROFILE_SCHEMA_VERSION = 3
MANIFEST_SCHEMA_VERSION = 4
TOOL_NAME = "patches/build_rom.py"
OBSERVE_PROFILE_NAME = "observe"

PROFILE_REQUIRED_ROOT_KEYS = frozenset(
    ("schema_version", "rom", "name", "rolling_launch")
)
PROFILE_OPTIONAL_ROOT_KEYS = frozenset(("can_telemetry",))
ROLLING_INTEGER_KEYS = (
    "coolant_min",
    "coolant_max",
    "min_speed",
    "max_speed",
    "min_rpm_native",
    "min_pedal",
    "target_speed_offset",
    "window_width",
    "window_top",
    "u_rate_limit",
    "integral_gain",
    "integrator_limit",
    "abort_above",
    "abort_below",
    "rpm_ceiling_offset_native",
    "run_timeout_ticks",
    "rearm_ticks",
    "speed_frame_age_limit",
)
ROLLING_PROFILE_KEYS = frozenset(
    ("mode", "enabled_maps", *ROLLING_INTEGER_KEYS)
)
MODE_NAMES = {
    "observe": rolling_launch.Mode.OBSERVE,
    "hold": rolling_launch.Mode.HOLD,
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
class BuildResult:
    data: bytes
    rom: str
    series: str
    detection: str
    profile: Profile
    configuration: bytes
    telemetry_configuration: bytes
    telemetry_mailbox_record: bytes
    source_sha256: str
    map_stage_sha256: str
    rolling_stage_sha256: str
    output_sha256: str
    output_md5: str
    source_checksums: rom_checksums.ChecksumValues
    output_checksums: rom_checksums.ChecksumValues
    changed_bytes: int
    permitted_write_bytes: int
    checksum_changed_bytes: int
    map_instruction_count: int
    rolling_instruction_count: int
    rolling_code_entry_count: int
    telemetry_instruction_count: int
    telemetry_code_entry_count: int
    diagnostic_count: int
    calibration_transfer: dict | None = None


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
        runtime_targets.RELOCATED_8MFK_FAMILY,
        runtime_targets.SH7059_1ND_FAMILY,
        runtime_targets.SH7059_1ME3B_FAMILY,
        runtime_targets.SH7058_JK78C_FAMILY,
    } or str(rom).upper() in runtime_targets.RELOCATED_ROMS
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
    except OSError as error:
        raise BuildError(f"{path}: cannot load profile: {error}") from error
    return parse_profile(raw_bytes, path)


def parse_profile(raw_bytes, path):
    """Parse the bytes of one strict local TOML profile named by ``path``."""
    try:
        raw = tomllib.loads(raw_bytes.decode("utf-8"))
    except (UnicodeError, tomllib.TOMLDecodeError) as error:
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

    calibration = rolling_launch.Calibration(
        mode=MODE_NAMES[mode_name],
        enable_mask=enable_mask,
        **{
            key: _require_integer(values[key], key)
            for key in ROLLING_INTEGER_KEYS
        },
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


def profile_text(name, rom, calibration, telemetry=None):
    """Return a strict local TOML profile; ``telemetry=None`` omits the
    optional CAN telemetry table."""
    mode_names = {mode: key for key, mode in MODE_NAMES.items()}
    enabled_maps = [
        slot for slot in range(1, rolling_launch.SLOT_COUNT + 1)
        if calibration.enable_mask & (1 << (slot - 1))
    ]
    lines = [
        f"schema_version = {PROFILE_SCHEMA_VERSION}",
        f"rom = {json.dumps(rom)}",
        f"name = {json.dumps(name)}",
        "",
        "[rolling_launch]",
        f"mode = {json.dumps(mode_names[calibration.mode])}",
        f"enabled_maps = {json.dumps(enabled_maps)}",
    ]
    lines += [
        f"{key} = {getattr(calibration, key)}"
        for key in ROLLING_INTEGER_KEYS
    ]
    if telemetry is not None:
        lines += [
            "",
            "[can_telemetry]",
            f"enabled = {str(telemetry.enabled).lower()}",
            f"can_id = 0x{telemetry.can_id:03X}",
            f"profile = {json.dumps(telemetry.profile)}",
            f"tick_divisor = {telemetry.tick_divisor}",
        ]
    return "\n".join(lines) + "\n"


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


def _require_stock(source, source_name, target):
    """Require the registered stock image of ``target`` and return the
    verification of its checksums."""
    if target.family == runtime_targets.EXACT_FAMILY:
        jk08a_runtime_reservations.load_ledger()
    if source != target.stock_image.data:
        raise BuildError(
            f"{source_name}: input is not the registered {target.rom} stock "
            f"image (SHA-256 {sha256(source)}); build from the stock image "
            "and move calibration with make rom-extract and make rom-calibrate"
        )
    try:
        return rom_checksums.require_valid(
            source, target.checksum_layout, source_name
        )
    except rom_checksums.ChecksumError as error:
        raise BuildError(str(error)) from error


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


def build_image(
    source,
    *,
    rom=AUTO_ROM,
    profile=None,
    source_name="<memory>",
):
    """Build and verify one complete ROM from its registered stock image
    without writing files."""
    source = bytes(source)
    selected_rom, detection = select_rom(source, rom)
    context = _series_context(selected_rom)
    try:
        target = runtime_targets.load_runtime_target(selected_rom)
    except runtime_targets.RuntimeTargetError as error:
        raise BuildError(str(error)) from error
    source_verification = _require_stock(source, source_name, target)
    if profile is None:
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
    if target.rolling_layout is None and (
        profile.calibration.mode != rolling_launch.Mode.OBSERVE
        or profile.calibration.enable_mask != 0
    ):
        raise BuildError(
            f"{selected_rom}: Rolling Launch is unsupported; profile "
            "must use observe mode with no enabled maps"
        )
    map_layout = target.map_layout
    launch_layout = target.rolling_layout
    telemetry_layout = target.telemetry_layout
    map_payloads = target.map_payloads
    launch_payloads = target.rolling_payloads
    telemetry_payloads = target.telemetry_payloads
    checksum_layout = target.checksum_layout
    try:
        component_offsets = _component_offsets(
            map_layout, launch_layout, telemetry_layout, checksum_layout
        )
        map_result = apply_map_switching.patch_image(
            source,
            layout=map_layout,
            blobs=map_payloads,
            source_name=f"{source_name} {selected_rom}",
            stock_image=target.stock_image,
            checksum_layout=checksum_layout,
        )
        map_stage = map_result.data

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

    return BuildResult(
        data=telemetry_result.data,
        rom=selected_rom,
        series=context.key,
        detection=detection,
        profile=profile,
        configuration=(
            b"" if launch_result is None else launch_result.configuration
        ),
        telemetry_configuration=telemetry_result.configuration,
        telemetry_mailbox_record=telemetry_result.mailbox_record,
        source_sha256=sha256(source),
        map_stage_sha256=sha256(map_stage),
        rolling_stage_sha256=sha256(rolling_stage),
        output_sha256=sha256(telemetry_result.data),
        output_md5=md5(telemetry_result.data),
        source_checksums=source_verification.stored,
        output_checksums=output_verification.stored,
        changed_bytes=changed,
        permitted_write_bytes=permitted,
        checksum_changed_bytes=checksum_changed,
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


def upgrade_image(source, *, rom=AUTO_ROM, source_name="<memory>"):
    """Compose the current runtime while preserving an existing calibration."""
    from patches import apply_calibration, extract_calibration

    source = bytes(source)
    try:
        extraction = extract_calibration.extract(source, rom=rom, source_name=source_name)
        if extraction.unexpressed or extraction.rolling is None:
            raise BuildError("upgrade requires an existing runtime with expressible Rolling Launch settings")
        selected = extraction.calibration.rom
        target = runtime_targets.load_runtime_target(selected)
        profile = Profile(name="Preserved input settings", rom=selected,
                          calibration=replace(extraction.rolling,
                              mode=rolling_launch.Mode(extraction.rolling.mode),
                              options=rolling_launch.Option(extraction.rolling.options)),
                          telemetry=extraction.telemetry or can_telemetry.default_configuration(),
                          source=source_name, sha256=None)
        fresh = build_image(target.stock_image.data, rom=selected, profile=profile,
                            source_name=f"{selected} stock")
        application = apply_calibration.apply(fresh.data, extraction.calibration)
        if any(state != "matched" for _, state in application.settings):
            raise BuildError("upgrade settings do not match the extracted source")
        changed, permitted, checksum_changed = _validate_preservation(
            source, application.data,
            _component_offsets(target.map_layout, target.rolling_layout, target.telemetry_layout,
                               target.checksum_layout),
            target.checksum_layout)
        checksums = rom_checksums.require_valid(source, target.checksum_layout, source_name)
    except (ValueError, runtime_targets.RuntimeTargetError) as error:
        raise BuildError(str(error)) from error
    return replace(fresh, data=application.data, source_sha256=sha256(source),
                   source_checksums=checksums.stored,
                   output_sha256=sha256(application.data), output_md5=md5(application.data),
                   output_checksums=application.output_checksums,
                   changed_bytes=changed, permitted_write_bytes=permitted,
                   checksum_changed_bytes=checksum_changed,
                   calibration_transfer={
                       "source_runtime": dict(extraction.calibration.source[1:]),
                       "settings": dict(application.settings),
                       "elements": len(extraction.calibration.elements),
                       "fresh_build_sha256": fresh.output_sha256,
                   })


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
    document = {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "tool": TOOL_NAME,
        "series": result.series,
        "rom": result.rom,
        "detection": result.detection,
        "input": {
            "path": str(Path(input_path).resolve()),
            "sha256": result.source_sha256,
            "checksums": _checksum_dict(result.source_checksums),
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
    if result.calibration_transfer is not None:
        document["calibration_transfer"] = result.calibration_transfer
        document["stages"]["can_telemetry_sha256"] = result.calibration_transfer["fresh_build_sha256"]
        document["stages"]["calibration_sha256"] = result.output_sha256
    return document


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
    parser.add_argument("--upgrade", action="store_true",
                        help="preserve calibration and runtime settings from a registered existing image")
    args = parser.parse_args(argv)

    try:
        source = args.input.read_bytes()
        profile = load_profile(args.profile) if args.profile else None
        if args.upgrade:
            if profile is not None:
                raise BuildError("--upgrade preserves input settings and takes no --profile")
            result = upgrade_image(source, rom=args.rom, source_name=str(args.input))
        else:
            result = build_image(source, rom=args.rom, profile=profile, source_name=str(args.input))
    except (OSError, BuildError) as error:
        parser.error(str(error))

    calibration = result.profile.calibration
    print(
        f"status=PASS series={result.series} rom={result.rom} "
        f"detection={result.detection}"
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
        f"checksum_changed_bytes={result.checksum_changed_bytes}"
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
