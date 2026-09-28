#!/usr/bin/env python3
"""Project and validate production runtime layouts for registered ROMs.

The canonical SH-2E sources and layouts remain in JK08A coordinates. Exact
8MFK address profiles provide every nonuniform stock binding, while this module
applies the audited uniform injected-ROM and injected-RAM relocations. The
JK08A values of the key tables of the feature targets and the hook keys of
each target come from the entity files through `kb.targets`. Target
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
# The firmware gate runs this module outside the project environment, where
# the `kb` package is importable only from its source tree.
for _path in (ROOT / "tools" / "kb" / "src", ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

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
from kb import targets as kb_targets
from kb.repo import KbError


DEFAULT_PAYLOADS = Path(__file__).with_name("runtime-target-payloads.toml")
EXACT_FAMILY = "sh7058_7mfkavn86"
RELOCATED_8MFK_FAMILY = "sh7058_8mfk"
SH7059_1ND_FAMILY = "sh7059_1nd"
SH7059_1ME3B_FAMILY = "sh7059_1me3b"
SH7058_JK78C_FAMILY = "sh7058_jk78c"
EXACT_ROMS = ("JK00A", "JK03A", "JK03B", "JK08A")
RELOCATED_8MFK_ROMS = ("JK00C", "JK00D")
SH7059_1ND_ROMS = ("1ND0A", "1ND3B")
SH7059_1ME3B_ROMS = ("1ME3B",)
SH7058_JK78C_ROMS = ("JK78C",)
VQ37_RUNTIME_ROMS = (
    SH7059_1ND_ROMS + SH7059_1ME3B_ROMS + SH7058_JK78C_ROMS
)
VQ37_MAP_VARIANTS = rom_address_profiles.VQ37_MAP_VARIANTS
RELOCATED_ROMS = RELOCATED_8MFK_ROMS + VQ37_RUNTIME_ROMS
SUPPORTED_ROMS = EXACT_ROMS + RELOCATED_ROMS
ZERO_SHA256 = "0" * 64

NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])0x[0-9A-Fa-f]+")

# The dual-CVTC layout reuses the canonical exhaust-target family
# allocation for the target intake-cam family and allocates separate
# storage for the target exhaust-cam family.
INTAKE_CVTC_TARGET_NAME = "Intake CVTC Target - Main"

# The SH7059 VQ37 layouts switch the four 8x8 state-code ignition surfaces
# through an adapter of their own. Its source names the stock lookup and each
# table base of the template layout and the canonical coordinate of each
# pointer table; the projection binds all of them from the address profile.
IGNITION_STATE_ADAPTER_SOURCE = "map-switching-ignition-state-adapter.s"
IGNITION_STATE_TEMPLATE_LAYOUT = "1nd"
IGNITION_STATE_TEMPLATE_LOOKUP = 0x000285B4
IGNITION_STATE_FAMILY_NAMES = {
    "ignition_surface_state_3": (
        "Ignition Timing Surface - VVEL State Code 3"
    ),
    "ignition_surface_state_4": (
        "Ignition Timing Surface - VVEL State Code 4"
    ),
    "ignition_surface_state_5": (
        "Ignition Timing Surface - VVEL State Code 5"
    ),
    "ignition_surface_state_6_7": (
        "Ignition Timing Surface - VVEL State Codes 6 and 7"
    ),
}


class RuntimeTargetError(ValueError):
    """Raised when a target projection or payload lock is incomplete."""


def _kb(read, *args):
    """A read of the entity files through `kb.targets`."""
    try:
        return read(*args, root=ROOT)
    except KbError as error:
        raise RuntimeTargetError(f"kb: {error}") from error


@lru_cache(maxsize=None)
def canonical_symbols(feature):
    """{key: value} of the JK08A target of a feature: symbol addresses,
    numbers, and record words."""
    return _kb(kb_targets.canonical_symbols, feature)


@lru_cache(maxsize=None)
def map_hook_keys(rom):
    """{JK08A hook word: key} of the map hooks of the layout of a ROM."""
    return _kb(
        kb_targets.hook_keys,
        "map_switching",
        _kb(kb_targets.layout_of, rom),
    )


@lru_cache(maxsize=None)
def ignition_state_template():
    """{family key: (table, pointer table)} that the ignition state adapter
    source names: the table base of each state-code family on the template
    layout and the pointer table of its storage there, less the ROM
    relocation of the layout."""
    layout = IGNITION_STATE_TEMPLATE_LAYOUT
    maps = _kb(kb_targets.target, "map_switching", layout)
    delta = _kb(kb_targets.target, "runtime", layout)["rom_delta"]
    storage = maps["ignition_state_storage"]
    return {
        key: (
            _kb(kb_targets.address, maps["families"][key], layout),
            int(storage[key]["pointer_table"], 16) - delta,
        )
        for key in IGNITION_STATE_FAMILY_NAMES
    }


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
    rolling_layout: rolling_launch_layout.Layout | None
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


def _decode_payloads(row, context, *, allow_empty=False):
    if not isinstance(row, dict) or (not row and not allow_empty):
        qualifier = "a table" if allow_empty else "a nonempty table"
        raise RuntimeTargetError(f"{context}: expected {qualifier}")
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
                row["rolling_units"],
                f"{rom}.rolling_units",
                allow_empty=True,
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
    if profile.map_variant == "dual-cvtc":
        family_keys = {
            family.key: (
                "intake_cvtc_target"
                if family.key == "exhaust_cvtc_target"
                else family.key
            )
            for family in canonical_map.families
        }
    else:
        family_keys = {
            "over_run_fuel_hold": "over_run_fuel_hold",
            "over_run_fuel_cut": "over_run_fuel_cut",
            "over_run_fuel_restore": "over_run_fuel_restore",
            "over_run_fuel_intermediate_restore": (
                "over_run_fuel_intermediate_restore"
            ),
            "high_octane_timing_state": "ignition_surface_hot",
            "high_detonation_timing_state": "ignition_surface_cold",
            "cold_idle_ignition_timing": "cold_idle_ignition_timing",
            "idle_ignition_timing": "idle_ignition_timing_default",
            "fuel_compensation_main": "fuel_compensation_main_default",
            "rev_limit_throttle_cut": "rev_limit_throttle_cut",
        }
    for family in canonical_map.families:
        target_key = family_keys.get(family.key)
        if target_key is None:
            continue
        _add_mapping(
            mapping,
            family.canonical_address,
            family_targets[target_key],
            f"{profile.rom}.map_families",
        )
    if profile.map_variant in VQ37_MAP_VARIANTS:
        _add_mapping(
            mapping,
            canonical_map.family_by_key[
                "exhaust_cvtc_target"
            ].canonical_address,
            family_targets["fuel_compensation_main_alternate"],
            f"{profile.rom}.fuel_compensation_main_alternate",
        )
        _add_mapping(
            mapping,
            canonical_map.family_by_key[
                "rev_limit_fuel_cut"
            ].canonical_address,
            family_targets["idle_ignition_timing_alternate"],
            f"{profile.rom}.idle_ignition_timing_alternate",
        )
    if "rev_limit_fuel_cut" in family_targets:
        _add_mapping(
            mapping,
            canonical_map.family_by_key[
                "rev_limit_fuel_cut"
            ].canonical_address
            + 8,
            family_targets["rev_limit_fuel_cut"] + 8,
            f"{profile.rom}.rev_limit_fuel_cut_tail",
        )

    map_hooks = profile.map_hook_by_key
    hook_keys = map_hook_keys(profile.rom)
    for hook in canonical_map.hooks:
        target_key = hook_keys.get(hook.address)
        if target_key is None:
            continue
        target = map_hooks[target_key]
        _add_mapping(mapping, hook.address, target.address, profile.rom)
        _add_mapping(mapping, hook.stock, target.stock, profile.rom)

    map_symbols = profile.map_symbol_by_key
    for key, source in canonical_symbols("map_switching").items():
        if key in map_symbols:
            _add_mapping(mapping, source, map_symbols[key], profile.rom)
    _add_mapping(
        mapping,
        canonical_map.feedback.payload_start,
        profile.can_symbol_by_key["feedback_payload_base"]
        + profile.can_symbol_by_key["feedback_payload_offset"],
        profile.rom,
    )
    _add_mapping(
        mapping,
        canonical_map.ram.reservation.start - 0x10,
        profile.injected_ram.start - 0x10,
        profile.rom,
    )

    if profile.capabilities.rolling_launch:
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
                mapping,
                source.pointer_address,
                target.pointer_address,
                profile.rom,
            )
            _add_mapping(mapping, source.target, target.target, profile.rom)
        rolling_symbols = profile.rolling_symbol_by_key
        for key, source in canonical_symbols("rolling_launch").items():
            _add_mapping(mapping, source, rolling_symbols[key], profile.rom)
    if profile.capabilities.can_telemetry:
        can_hooks = profile.can_hook_by_key
        for hook in canonical_can.hooks:
            target = can_hooks[hook.key]
            _add_mapping(mapping, hook.address, target.address, profile.rom)
            _add_mapping(mapping, hook.stock, target.base, profile.rom)
        can_symbols = profile.can_symbol_by_key
        for key, source in canonical_symbols("can_telemetry").items():
            if key in can_symbols:
                _add_mapping(mapping, source, can_symbols[key], profile.rom)

    target_sources = profile.telemetry_source_by_name
    for field in _canonical_telemetry_fields():
        if field.kind != "ecu_ram":
            continue
        target = target_sources.get(
            field.name, profile.telemetry_zero_source
        )
        if target is None:
            raise RuntimeTargetError(
                f"{profile.rom}: telemetry field {field.name} has no source"
            )
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


def _replace_source_once(source, old, new, context):
    if source.count(old) != 1:
        raise RuntimeTargetError(f"{context}: canonical source differs")
    return source.replace(old, new)


def _ascd_mask_source(source, profile, canonical, template, context):
    """Bind the ASCD-enabled bit test to the target flag layout."""
    if profile.ascd_enabled_mask == (
        rom_address_profiles.DEFAULT_ASCD_ENABLED_MASK
    ):
        return source
    return _replace_source_once(
        source,
        canonical,
        template.format(mask=profile.ascd_enabled_mask),
        context,
    )


def _render_selector_host(profile, mapping):
    source = _ascd_mask_source(
        _read_source("map-switching-selector-host.s"),
        profile,
        "mov #-0x80,r1\ntst r1,r0\nbf host_abort_selector\n",
        "mov #0x{mask:02X},r1\ntst r1,r0\nbf host_abort_selector\n",
        "selector host ASCD-enabled mask",
    )
    return _render_source(source, profile, mapping)


def _render_vq37_rolling_wrappers(profile, mapping):
    source = _read_source("rolling-launch-wrappers.s")
    source = _replace_source_once(
        source,
        "dedicated 20-byte Rolling Launch state",
        "dedicated 24-byte Rolling Launch state",
        "VQ37 startup wrapper description",
    )
    source = _replace_source_once(
        source,
        "mov #0x5,r2\nrolling_launch_startup_clear_loop:",
        "mov #0x6,r2\nrolling_launch_startup_clear_loop:",
        "VQ37 startup clear count",
    )
    return _render_source(source, profile, mapping)


def _render_vq37_rolling_engine(profile, mapping):
    source = _read_source("rolling-launch-engine.s")
    source = _replace_source_once(
        source,
        "// hold, and 2 RPM hold plus band-limited retard. Only modes 1 "
        "and 2 write the\n"
        "// fuel shadow.\n",
        "// hold, and 2 RPM hold plus band-limited retard. Only modes 1 and 2 publish\n"
        "// the exact all-cylinder request; selected VQ37 maps remain unchanged.\n",
        "VQ37 actuator description",
    )
    source = _replace_source_once(
        source,
        "//   +0x12 u16 captured ignition-retard band start\n",
        "//   +0x12 u16 captured ignition-retard band start\n"
        "//   +0x14 u16 exact all-cylinder fuel-cut request\n"
        "//   +0x16 u16 reserved and cleared\n",
        "VQ37 state description",
    )
    source = _replace_source_once(
        source,
        "mov.l @(rl_state_address,pc),r5\nmov.b @r5,r0\n",
        "mov.l @(rl_state_address,pc),r5\n"
        "mov #0x0,r0\n"
        "mov.w r0,@(0x14,r5)\n"
        "mov.b @r5,r0\n",
        "VQ37 per-tick fuel request clear",
    )
    source = _replace_source_once(
        source,
        "mov.b @(0x5,r5),r0\n"
        "cmp/eq 0x0,r0\n"
        "bt rl_activate_publish\n"
        "bsr rl_apply_fuel_overlay\n"
        "nop\n"
        "rl_activate_publish:\n",
        "rl_activate_publish:\n",
        "VQ37 activation actuator",
    )
    source = _replace_source_once(
        source,
        "mov #0x5,r2\nrl_corrupt_clear_loop:",
        "mov #0x6,r2\nrl_corrupt_clear_loop:",
        "VQ37 corrupt-state clear count",
    )
    source = _replace_source_once(
        source,
        "tst r2,r2\n"
        "bt rl_active_flags_fuel\n"
        "mov r3,r0\n",
        "tst r2,r2\n"
        "bt rl_active_flags_fuel\n"
        "mov #0x3F,r0\n"
        "mov.w r0,@(0x14,r5)\n"
        "mov r3,r0\n",
        "VQ37 active fuel request publication",
    )
    overlay_start = source.index(
        "// Atomically replace only the first eight bytes"
    )
    overlay_end = source.index(
        "// Publish active/output flags", overlay_start
    )
    source = source[:overlay_start] + source[overlay_end:]
    source = _replace_source_once(
        source,
        "rl_helper_fuel_shadow_address:\n.long 0xFFFF5D10\n",
        "",
        "VQ37 fuel-shadow literal removal",
    )
    source = _ascd_mask_source(
        source,
        profile,
        "mov.b @r4,r0\ntst 0x80,r0\nbf rl_gate_ascd_fail\n",
        "mov.b @r4,r0\ntst 0x{mask:02X},r0\nbf rl_gate_ascd_fail\n",
        "Rolling Launch ASCD-enabled mask",
    )
    return _render_source(source, profile, mapping)


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
    custom_sources = {}
    if profile.map_variant in VQ37_MAP_VARIANTS:
        custom_sources = {
            "lookup_adapters": "map-switching-vq37-adapters.s",
            "limiter_commit": "map-switching-vq37-limiter-commit.s",
        }
    unit_prototypes = []
    for unit in base.assembly_units:
        prototype = replace(
            unit, source=custom_sources.get(unit.key, unit.source)
        )
        if profile.map_variant in VQ37_MAP_VARIANTS:
            if unit.key == "startup_wrapper":
                prototype = replace(
                    prototype,
                    span=map_switching_layout.AddressRange(
                        unit.span.start,
                        0x000D22EC,
                        unit.span.key,
                    ),
                )
            elif unit.key == "limiter_commit":
                prototype = replace(
                    prototype,
                    span=map_switching_layout.AddressRange(
                        unit.span.start,
                        0x000D36E0,
                        unit.span.key,
                    ),
                )
        if (
            profile.map_variant in VQ37_MAP_VARIANTS
            and unit.key == "lookup_adapters"
        ):
            prototype = replace(
                prototype,
                code_regions=tuple(
                    (
                        "idle_ignition_pool_2_adapter"
                        if key == "cvtc_target_adapter"
                        else key
                    )
                    for key in unit.code_regions
                ),
            )
        unit_prototypes.append(prototype)

    source_texts = {
        unit.key: _render_source(
            _read_source(unit.source), profile, mapping
        )
        for unit in unit_prototypes
    }
    source_texts["selector_host"] = _render_selector_host(profile, mapping)
    if profile.map_variant == "dual-cvtc":
        source_texts["limiter_commit"] = _render_unaligned_throttle_limiter(
            profile, mapping
        )
        secondary_template = _read_source(
            "map-switching-secondary-cvtc-adapter.s"
        )
        secondary_overrides = {
            0x0000B33A: profile.map_family_by_key[
                "exhaust_cvtc_target"
            ],
            0x000261B8: profile.map_symbol_by_key["exhaust_lookup"],
            0x000D5050: profile.extra_cvtc_storage.pointer_table,
        }
        source_texts["secondary_cvtc_adapter"] = _render_source(
            secondary_template, profile, mapping, secondary_overrides
        )
    state_storage = profile.ignition_state_storage
    if state_storage is not None:
        state_overrides = {
            IGNITION_STATE_TEMPLATE_LOOKUP: profile.map_hook_by_key[
                "ignition_state_lookup"
            ].stock,
        }
        for key, (table, pointers) in ignition_state_template().items():
            state_overrides[table] = profile.map_family_by_key[key]
            state_overrides[pointers] = state_storage.family_by_key[
                key
            ].pointer_table
        source_texts["ignition_state_adapter"] = _render_source(
            _read_source(IGNITION_STATE_ADAPTER_SOURCE),
            profile,
            mapping,
            state_overrides,
        )

    code_regions = []
    for item in base.code_regions:
        if (
            profile.map_variant in VQ37_MAP_VARIANTS
            and item.key == "cvtc_target_adapter"
        ):
            code_regions.append(replace(
                item,
                key="idle_ignition_pool_2_adapter",
                span=map_switching_layout.AddressRange(
                    item.span.start + delta,
                    item.span.end + delta,
                    "idle_ignition_pool_2_adapter",
                ),
                entry=item.entry + delta,
            ))
            continue
        target_end = item.span.end
        if profile.map_variant in VQ37_MAP_VARIANTS:
            if item.key == "startup_wrapper":
                target_end = 0x000D22EC
            elif item.key == "limiter_commit":
                target_end = 0x000D36E0
        code_regions.append(replace(
            item,
            span=map_switching_layout.AddressRange(
                item.span.start + delta,
                target_end + delta,
                item.span.key,
            ),
            entry=item.entry + delta,
        ))
    if profile.map_variant == "dual-cvtc":
        code_regions.append(map_switching_layout.CodeRegion(
            "secondary_cvtc_target_adapter",
            map_switching_layout.AddressRange(
                profile.extra_cvtc_storage.adapter.start,
                profile.extra_cvtc_storage.adapter.end,
                "secondary_cvtc_target_adapter",
            ),
            profile.extra_cvtc_storage.adapter.start,
        ))
    if state_storage is not None:
        code_regions.append(map_switching_layout.CodeRegion(
            "ignition_state_adapter",
            map_switching_layout.AddressRange(
                state_storage.adapter.start,
                state_storage.adapter.end,
                "ignition_state_adapter",
            ),
            state_storage.adapter.start,
        ))
    code_regions = tuple(code_regions)

    units = tuple(
        _projected_unit(
            unit,
            source_texts[unit.key],
            unit.span.start + delta,
            unit.span.end + delta,
            unit.code_regions,
            payloads,
        )
        for unit in unit_prototypes
    )
    if profile.map_variant == "dual-cvtc":
        secondary_proto = map_switching_layout.AssemblyUnit(
            key="secondary_cvtc_adapter",
            source="map-switching-secondary-cvtc-adapter.s",
            span=map_switching_layout.AddressRange(
                0x000D5000, 0x000D5040, "assembly.secondary_cvtc_adapter"
            ),
            fill=0xFF,
            language="SuperH:BE:32:SH-2A",
            expected_sha256=ZERO_SHA256,
            instruction_count=0,
            data_bytes=0,
            code_regions=("secondary_cvtc_target_adapter",),
        )
        units += (
            _projected_unit(
                secondary_proto,
                source_texts["secondary_cvtc_adapter"],
                profile.extra_cvtc_storage.adapter.start,
                profile.extra_cvtc_storage.adapter.end,
                secondary_proto.code_regions,
                payloads,
            ),
        )
    if state_storage is not None:
        state_proto = map_switching_layout.AssemblyUnit(
            key="ignition_state_adapter",
            source=IGNITION_STATE_ADAPTER_SOURCE,
            span=map_switching_layout.AddressRange(
                state_storage.adapter.start - delta,
                state_storage.adapter.end - delta,
                "assembly.ignition_state_adapter",
            ),
            fill=0xFF,
            language="SuperH:BE:32:SH-2A",
            expected_sha256=ZERO_SHA256,
            instruction_count=0,
            data_bytes=0,
            code_regions=("ignition_state_adapter",),
        )
        units += (
            _projected_unit(
                state_proto,
                source_texts["ignition_state_adapter"],
                state_storage.adapter.start,
                state_storage.adapter.end,
                state_proto.code_regions,
                payloads,
            ),
        )

    target_families = profile.map_family_by_key
    families = []
    if profile.map_variant == "dual-cvtc":
        for family in base.families:
            key = (
                "intake_cvtc_target"
                if family.key == "exhaust_cvtc_target"
                else family.key
            )
            canonical_address = target_families[key]
            families.append(replace(
                family,
                key=key,
                name=(
                    INTAKE_CVTC_TARGET_NAME
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
        exhaust_address = target_families["exhaust_cvtc_target"]
        families.append(replace(
            exhaust,
            key="exhaust_cvtc_target",
            canonical_address=exhaust_address,
            copies=profile.extra_cvtc_storage.copies,
            pointer_table=profile.extra_cvtc_storage.pointer_table,
            stock_container_start=exhaust_address,
            adapter="secondary_cvtc_target_adapter",
        ))
    else:
        storage_keys = {
            "idle_ignition_timing_alternate": "rev_limit_fuel_cut",
            "fuel_compensation_main_alternate": "exhaust_cvtc_target",
        }
        source_keys = {
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
        }
        # The executed VQ37 ignition pair has no canonical counterpart; it
        # reuses the geometry and storage of the two canonical 16x16 ignition
        # families and is named by the selector arm that reaches it.
        family_names = {
            "ignition_surface_hot": "Ignition Timing Surface - Hot",
            "ignition_surface_cold": "Ignition Timing Surface - Cold",
        }
        for key, source_key in source_keys.items():
            source = base.family_by_key[source_key]
            storage = base.family_by_key[storage_keys.get(key, source_key)]
            canonical_address = target_families[key]
            families.append(replace(
                source,
                key=key,
                name=family_names.get(
                    key,
                    f"{source.name} - {key.rsplit('_', 1)[-1].title()}",
                ),
                canonical_address=canonical_address,
                copies=tuple(address + delta for address in storage.copies),
                pointer_table=storage.pointer_table + delta,
                stock_container_start=canonical_address,
                adapter=(
                    "idle_ignition_pool_2_adapter"
                    if key == "idle_ignition_timing_alternate"
                    else source.adapter
                ),
            ))
        if state_storage is not None:
            for item in state_storage.families:
                state_address = target_families[item.key]
                families.append(map_switching_layout.Family(
                    key=item.key,
                    group="ignition",
                    name=IGNITION_STATE_FAMILY_NAMES[item.key],
                    canonical_address=state_address,
                    width=8,
                    height=8,
                    storage_type="uint8",
                    access_kind="adapter",
                    adapter="ignition_state_adapter",
                    copy_alignment=64,
                    copies=item.copies,
                    pointer_table=item.pointer_table,
                    stock_container_start=state_address,
                    stock_container_size=64,
                    selected_offset=0,
                    shadow_start=None,
                    runtime_shadow_address=None,
                ))
        throttle = base.family_by_key["rev_limit_throttle_cut"]
        throttle_address = target_families["rev_limit_throttle_cut"]
        fuel_shadow_start = base.ram.fuel_cut_shadow.start + ram_delta
        throttle_shadow_start = (
            base.ram.throttle_shadow.start + ram_delta + 0x18
        )
        families.extend((
            map_switching_layout.Family(
                key="rev_limit_fuel_cut_caps",
                group="rev_limiter",
                name="Engine Speed Limit - Fuel Cut Caps",
                canonical_address=target_families[
                    "rev_limit_fuel_cut_caps"
                ],
                width=2,
                height=1,
                storage_type="uint16",
                access_kind="ram_shadow",
                adapter=None,
                copy_alignment=4,
                copies=tuple(
                    address + delta
                    for address in (
                        0x000D24F4,
                        0x000D24F8,
                        0x000D24FC,
                        0x000D353C,
                    )
                ),
                pointer_table=0x000D22EC + delta,
                stock_container_start=target_families[
                    "rev_limit_fuel_cut_caps"
                ],
                stock_container_size=4,
                selected_offset=0,
                shadow_start=fuel_shadow_start,
                runtime_shadow_address=None,
            ),
            map_switching_layout.Family(
                key="rev_limit_fuel_cut_curves",
                group="rev_limiter",
                name="Engine Speed Limit - Fuel Cut Curves",
                canonical_address=target_families[
                    "rev_limit_fuel_cut_curves"
                ],
                width=8,
                height=2,
                storage_type="uint16",
                access_kind="ram_shadow",
                adapter=None,
                copy_alignment=32,
                copies=tuple(
                    address + delta
                    for address in (
                        0x000D36E0,
                        0x000D3700,
                        0x000D3720,
                        0x000D3740,
                    )
                ),
                pointer_table=0x000D4068 + delta,
                stock_container_start=target_families[
                    "rev_limit_fuel_cut_curves"
                ],
                stock_container_size=32,
                selected_offset=0,
                shadow_start=fuel_shadow_start + 4,
                runtime_shadow_address=None,
            ),
        ))
        families.append(replace(
            throttle,
            canonical_address=throttle_address,
            copies=tuple(address + delta for address in throttle.copies),
            pointer_table=throttle.pointer_table + delta,
            stock_container_start=throttle_address,
            stock_container_size=throttle.byte_length,
            selected_offset=0,
            shadow_start=throttle_shadow_start,
            runtime_shadow_address=None,
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
    feedback = replace(
        feedback_base,
        config_record_address=can_symbols["feedback_config_record_address"],
        config_record=can_symbols["feedback_config_record_value"],
        serializer=map_symbols["feedback_serializer"],
        dispatch_literal=can_symbols["feedback_dispatch_literal"],
        serializer_payload_base_literal=can_symbols[
            "feedback_payload_base_literal"
        ],
        serializer_payload_base=can_symbols["feedback_payload_base"],
        payload_offset=can_symbols["feedback_payload_offset"],
        payload_start=(
            can_symbols["feedback_payload_base"]
            + can_symbols["feedback_payload_offset"]
        ),
        status_byte_address=map_symbols["feedback_status_byte"],
        phase_counts_address=feedback_base.phase_counts_address + delta,
        encoding_evidence=(
            f"exact_{profile.map_variant}_serializer_target_binding"
        ),
    )
    vq37 = profile.map_variant in VQ37_MAP_VARIANTS
    fuel_shadow_start = base.ram.fuel_cut_shadow.start + ram_delta
    throttle_shadow_start = base.ram.throttle_shadow.start + ram_delta
    if vq37:
        throttle_shadow_start += 0x18
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
            fuel_shadow_start,
            (
                fuel_shadow_start + 36
                if vq37
                else base.ram.fuel_cut_shadow.end + ram_delta
            ),
            base.ram.fuel_cut_shadow.key,
        ),
        throttle_shadow=map_switching_layout.AddressRange(
            throttle_shadow_start,
            (
                throttle_shadow_start + 2
                if vq37
                else base.ram.throttle_shadow.end + ram_delta
            ),
            base.ram.throttle_shadow.key,
        ),
        throttle_selected_offset=(
            base.ram.throttle_selected_offset
            if profile.map_variant == "dual-cvtc"
            else 0
        ),
        stock_throttle_runtime=map_symbols.get("throttle_runtime", 0),
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
        anchors=base.anchors if profile.map_variant == "dual-cvtc" else (),
        hooks=hooks,
        families=tuple(families),
        variant=profile.map_variant,
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
    vq37 = profile.map_variant in VQ37_MAP_VARIANTS
    source_texts = {}
    for unit in base.assembly_units:
        if vq37 and unit.key == "wrappers":
            source_texts[unit.key] = _render_vq37_rolling_wrappers(
                profile, mapping
            )
        elif vq37 and unit.key == "engine":
            source_texts[unit.key] = _render_vq37_rolling_engine(
                profile, mapping
            )
        else:
            source_texts[unit.key] = _render_source(
                _read_source(unit.source), profile, mapping
            )
    if vq37:
        source_texts["fuel_cut_wrapper"] = _render_source(
            _read_source("rolling-launch-fuel-cut-wrapper.s"),
            profile,
            mapping,
            {
                0x000A0000: profile.rolling_symbol_by_key[
                    "fuel_cut_coordinator"
                ]
            },
        )
    code_regions = [
        replace(
            item,
            span=_shift_range(item.span, delta),
            entry=item.entry + delta,
        )
        for item in base.code_regions
    ]
    if vq37:
        code_regions.append(map_switching_layout.CodeRegion(
            "fuel_cut_wrapper",
            map_switching_layout.AddressRange(
                0x000D5000 + delta,
                0x000D5080 + delta,
                "fuel_cut_wrapper",
            ),
            0x000D5000 + delta,
        ))
    code_regions = tuple(code_regions)
    units = [
        _projected_unit(
            unit, source_texts[unit.key],
            unit.span.start + delta, unit.span.end + delta,
            unit.code_regions, payloads,
        )
        for unit in base.assembly_units
    ]
    if vq37:
        fuel_wrapper = map_switching_layout.AssemblyUnit(
            key="fuel_cut_wrapper",
            source="rolling-launch-fuel-cut-wrapper.s",
            span=map_switching_layout.AddressRange(
                0x000D5000,
                0x000D5080,
                "assembly.fuel_cut_wrapper",
            ),
            fill=0xFF,
            language="SuperH:BE:32:SH-2A",
            expected_sha256=ZERO_SHA256,
            instruction_count=1,
            data_bytes=0,
            code_regions=("fuel_cut_wrapper",),
        )
        units.append(_projected_unit(
            fuel_wrapper,
            source_texts[fuel_wrapper.key],
            fuel_wrapper.span.start + delta,
            fuel_wrapper.span.end + delta,
            fuel_wrapper.code_regions,
            payloads,
        ))
    units = tuple(units)
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
    state = _shift_range(base.ram.state, ram_delta)
    if vq37:
        state = map_switching_layout.AddressRange(
            state.start, state.end + 4, state.key
        )
    fuel_shadow = _shift_range(base.ram.fuel_shadow, ram_delta)
    if vq37:
        fuel_shadow = map_switching_layout.AddressRange(
            fuel_shadow.start, fuel_shadow.start + 36, fuel_shadow.key
        )
    ram = replace(
        base.ram,
        proven_free=map_switching_layout.AddressRange(
            profile.free_ram.start, profile.free_ram.end, "ram.proven_free"
        ),
        base_reservation=_shift_range(base.ram.base_reservation, ram_delta),
        state=state,
        fuel_shadow=fuel_shadow,
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
        ) + ((map_switching_layout.AddressRange(
            0x000D5000 + delta,
            0x000D5080 + delta,
            "claimed_rom_extension.vq37_fuel_cut_wrapper",
        ),) if vq37 else ()),
        configuration=_shift_range(base.configuration, delta),
        scheduler=replace(
            base.scheduler,
            table_address=rolling_symbols["periodic_task_table"],
            table_index=(
                rolling_symbols["periodic_task_slot"]
                - rolling_symbols["periodic_task_table"]
            )
            // 4,
        ),
        ram=ram,
        code_regions=code_regions,
        assembly_units=units,
        hooks=hooks,
        diagnostics=diagnostics,
        variant=(
            "vq37-fuel-coordinator" if vq37 else "relocated-8mfk"
        ),
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
    extra = profile.extra_cvtc_storage
    state_storage = profile.ignition_state_storage
    extra_end = (
        max(item.end for item in state_storage.ranges)
        if state_storage is not None
        else base.reserved_rom.start + delta + 0x80
        if profile.map_variant in VQ37_MAP_VARIANTS
        else base.reserved_rom.start + delta
        if extra is None
        else max(
            extra.adapter.end,
            extra.pointer_table + 20,
            *(address + 0x100 for address in extra.copies),
        )
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
        owned_rom=map_switching_layout.AddressRange(
            base.owned_rom.start + delta,
            profile.injected_rom.end,
            "owned_rom",
        ),
        reserved_rom=map_switching_layout.AddressRange(
            extra_end, profile.injected_rom.end, "reserved_rom"
        ),
        configuration=_shift_range(base.configuration, delta),
        mailbox_record_address=can_symbols["mailbox_record_address"],
        mailbox_record_stock=can_symbols["mailbox_record_stock"],
        ram=ram,
        code_regions=code_regions,
        assembly_units=units,
        hooks=hooks,
        variant=profile.telemetry_completion_variant,
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
    rolling_layout = (
        _project_rolling(
            profile,
            stock_sha256,
            mapping,
            rolling_payloads,
            ZERO_SHA256 if locks is None else locks.map_stage_sha256,
            ZERO_SHA256 if locks is None else locks.rolling_stage_sha256,
        )
        if profile.capabilities.rolling_launch
        else None
    )
    telemetry_base_sha256 = (
        ZERO_SHA256
        if locks is None
        else (
            locks.rolling_stage_sha256
            if profile.capabilities.rolling_launch
            else locks.map_stage_sha256
        )
    )
    telemetry_layout = _project_can(
        profile,
        stock_sha256,
        mapping,
        telemetry_payloads,
        telemetry_base_sha256,
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

    if profile.capabilities.rolling_launch:
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
    elif target.rolling_layout is not None or target.rolling_payloads:
        raise RuntimeTargetError(
            f"{target.rom}: disabled Rolling Launch has runtime artifacts"
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

    can_symbols = profile.can_symbol_by_key
    allocation_differs = any((
        target.map_layout.claimed_rom.start
        != profile.injected_rom.start,
        target.map_layout.claimed_rom.end != profile.injected_rom.end,
        target.map_layout.ram.reservation.start
        != profile.injected_ram.start,
        target.telemetry_layout.mailbox_record_address
        != can_symbols["mailbox_record_address"],
        target.telemetry_layout.mailbox_record_stock
        != can_symbols["mailbox_record_stock"],
    ))
    if profile.map_variant == "dual-cvtc":
        exhaust = target.map_layout.family_by_key["exhaust_cvtc_target"]
        allocation_differs = allocation_differs or any((
            exhaust.copies != profile.extra_cvtc_storage.copies,
            exhaust.pointer_table
            != profile.extra_cvtc_storage.pointer_table,
        ))
    if profile.ignition_state_storage is not None:
        projected = target.map_layout.family_by_key
        allocation_differs = allocation_differs or any(
            projected[item.key].copies != item.copies
            or projected[item.key].pointer_table != item.pointer_table
            for item in profile.ignition_state_storage.families
        )
    if allocation_differs:
        raise RuntimeTargetError(
            f"{target.rom}: projected allocation bindings differ"
        )
    if profile.map_variant in rom_address_profiles.GATED_IGNITION_MAP_VARIANTS:
        _validate_vq37_ignition_halves(target, profile)
    if profile.ignition_unreferenced_routine is not None:
        _validate_state_dispatch_coordinator(target, profile)
    if profile.ignition_state_storage is not None:
        _validate_ignition_state_pool(target, profile)


def _aligned_literal_sites(data, value):
    needle = value.to_bytes(4, "big")
    sites = []
    position = data.find(needle)
    while position != -1:
        if position % 4 == 0:
            sites.append(position)
        position = data.find(needle, position + 1)
    return sites


def _literal_loaders(data, site):
    """Return every PC-relative long load that addresses one literal site."""
    loaders = []
    for address in range(max(0, site - 0x400), site, 2):
        word = int.from_bytes(data[address:address + 2], "big")
        if (
            word & 0xF000 == 0xD000
            and (address & ~3) + 4 + (word & 0xFF) * 4 == site
        ):
            loaders.append(address)
    return loaders


def _live_literal_sites(data, value, profile):
    """Return the literal sites that code outside the unreferenced routine
    loads, or that no PC-relative load reaches at all."""
    routine = profile.ignition_unreferenced_routine
    live = []
    for site in _aligned_literal_sites(data, value):
        loaders = _literal_loaders(data, site)
        owned = (
            routine is not None
            and loaders
            and all(routine.start <= item < routine.end for item in loaders)
        )
        if not owned:
            live.append(site)
    return live


def _validate_ignition_state_pool(target, profile):
    """Bind the state-code ignition families to the hooked literal.

    The coordinator takes each 8x8 table base and the lookup pointer from its
    literal pool in adjacent loads. Every family base must have one live
    literal in the stock image, and every load of it must be followed by a
    load of the hooked literal, so no other pointer to the lookup serves a
    switched surface.
    """
    data = bytes(target.stock_image.data)
    hook = profile.map_hook_by_key["ignition_state_lookup"]
    families = target.map_layout.family_by_key
    hook_loaders = set(_literal_loaders(data, hook.address))
    for key in rom_address_profiles.IGNITION_STATE_FAMILY_KEYS:
        sites = _live_literal_sites(
            data, families[key].canonical_address, profile
        )
        loaders = _literal_loaders(data, sites[0]) if len(sites) == 1 else []
        if not loaders or any(
            item + 2 not in hook_loaders for item in loaders
        ):
            raise RuntimeTargetError(
                f"{target.rom}.{key}: table base is not a single literal of "
                "the hooked lookup pool"
            )
    if hook.address not in _aligned_literal_sites(data, hook.stock):
        raise RuntimeTargetError(
            f"{target.rom}: ignition state lookup literal differs"
        )


def _validate_state_dispatch_coordinator(target, profile):
    """Bind the 16x16 ignition families to the live state-code dispatch.

    The image holds an unreferenced earlier copy of the ignition coordinator
    beside the periodic one. Bit 3 of the stock configuration byte sends the
    periodic coordinator through its state-code dispatch, which reads the two
    16x16 families. Every literal of the 16x16 lookup must be hooked or owned
    by the unreferenced copy, so no executed pointer bypasses the adapter.
    """
    symbols = profile.map_symbol_by_key
    data = bytes(target.stock_image.data)
    if not data[symbols["ignition_coordinator_config_byte"]] & 0x08:
        raise RuntimeTargetError(
            f"{target.rom}: stock configuration gates the state-code "
            "ignition dispatch off"
        )
    hooks = {
        item.address: item
        for item in profile.map_hooks
        if item.key.startswith("ignition_lookup_")
    }
    stocks = {item.stock for item in hooks.values()}
    if len(stocks) != 1:
        raise RuntimeTargetError(
            f"{target.rom}: 16x16 ignition hooks name different lookups"
        )
    live = _live_literal_sites(data, stocks.pop(), profile)
    if set(live) != set(hooks):
        raise RuntimeTargetError(
            f"{target.rom}: live 16x16 ignition lookup literals differ from "
            "the hooked literals"
        )


def _validate_vq37_ignition_halves(target, profile):
    """Bind the VQ37 ignition families to the executed coordinator half.

    Bit 5 of the stock configuration byte sends the ignition coordinator
    through its mode-selected half, whose two 16x16 surfaces are the ignition
    families. The hooked literals also serve the gated half; its three
    surfaces hold identical stock bytes and stay outside every family, so the
    adapter passes them through unchanged.
    """
    symbols = profile.map_symbol_by_key
    data = target.stock_image.data
    if not data[symbols["ignition_coordinator_config_byte"]] & 0x20:
        raise RuntimeTargetError(
            f"{target.rom}: stock configuration gates the mode-selected "
            "ignition half off"
        )
    families = target.map_layout.family_by_key
    size = families["ignition_surface_hot"].byte_length
    gated = [
        symbols[f"ignition_gated_surface_{index}"] for index in (1, 2, 3)
    ]
    family_bases = {
        item.canonical_address for item in target.map_layout.families
    }
    if family_bases.intersection(gated):
        raise RuntimeTargetError(
            f"{target.rom}: a gated ignition surface is a map family"
        )
    blocks = {bytes(data[base:base + size]) for base in gated}
    if len(blocks) != 1:
        raise RuntimeTargetError(
            f"{target.rom}: gated ignition surfaces differ in the stock image"
        )


def validate_relocated_target(target, locks):
    """Validate one projected target through all three raw compositions."""
    _validate_projected_bindings(target)
    map_switching_layout.validate_structure(target.map_layout)
    if target.rolling_layout is not None:
        rolling_launch_layout.validate_structure(target.rolling_layout)
    can_telemetry_layout.validate_structure(target.telemetry_layout)
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
    telemetry_parsed = can_telemetry_assembly.validate_assembly_sources(
        target.telemetry_layout
    )
    map_switching_assembly.validate_instruction_semantics(
        target.map_layout, map_parsed, target.map_payloads
    )
    if target.rolling_layout is not None:
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
    rolling_result = (
        rolling_launch_compose.compose(
            layout=target.rolling_layout,
            base=map_result.data,
            blobs=target.rolling_payloads,
        )
        if target.rolling_layout is not None
        else None
    )
    telemetry_base = (
        rolling_result.data if rolling_result is not None else map_result.data
    )
    telemetry_result = can_telemetry_compose.compose(
        layout=target.telemetry_layout,
        base=telemetry_base,
        blobs=target.telemetry_payloads,
    )
    actual = (
        map_result.sha256,
        (
            rolling_result.sha256
            if rolling_result is not None
            else map_result.sha256
        ),
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
    instructions = sum(
        target.map_layout.assembled_instruction_count
        + (
            0
            if target.rolling_layout is None
            else target.rolling_layout.assembled_instruction_count
        )
        + target.telemetry_layout.assembled_instruction_count
        for target in targets.values()
    )
    print(
        f"status=PASS targets={len(targets)} "
        f"map_families={sum(len(x.map_layout.families) for x in targets.values())} "
        f"instructions={instructions}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
