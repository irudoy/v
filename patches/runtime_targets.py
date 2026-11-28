#!/usr/bin/env python3
"""Project and validate production runtime layouts for registered ROMs.

The canonical SH-2E sources and layouts remain in JK08A coordinates. Exact
8MFK address profiles provide every nonuniform stock binding, while this module
applies the audited uniform injected-ROM and injected-RAM relocations. The
JK08A values of the key tables of the feature targets, the hook keys of each
target, and the MAIN switch bit of the ASCD flag byte, the active cut bit of
the RPM fuel-cut state, and the high-detonation bit of the knock surface state
of each layout come from the generated numeric runtime bindings. Target
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
from patches import ignition_literal_consumers
from patches import map_switching_assembly
from patches import map_switching_compose
from patches import map_switching_layout
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout
from patches import rom_address_profiles
from patches import rom_checksums
from patches import runtime_bindings
from patches import can_telemetry_compose
from tools import rom_homology
from tools.mapkit import rom as romkit


DEFAULT_PAYLOADS = Path(__file__).with_name("runtime-target-payloads.toml")
EXACT_FAMILY = "sh7058_7mfkavn86"
RELOCATED_8MFK_FAMILY = "sh7058_8mfk"
SH7059_1ND_FAMILY = "sh7059_1nd"
SH7059_1ME3B_FAMILY = "sh7059_1me3b"
SH7059_1EK7A_FAMILY = "sh7059_1ek7a"
SH7058_JK78C_FAMILY = "sh7058_jk78c"
EXACT_ROMS = ("JK00A", "JK03A", "JK03B", "JK08A")
RELOCATED_8MFK_ROMS = ("JK00C", "JK00D")
SH7059_1ND_ROMS = ("1ND0A", "1ND3B")
SH7059_1ME3B_ROMS = ("1ME3B",)
SH7059_1EK7A_ROMS = ("1EK7A",)
SH7058_JK78C_ROMS = ("JK78C",)
VQ37_RUNTIME_ROMS = (
    SH7059_1ND_ROMS + SH7059_1ME3B_ROMS + SH7059_1EK7A_ROMS + SH7058_JK78C_ROMS
)
VQ37_MAP_VARIANTS = rom_address_profiles.VQ37_MAP_VARIANTS
RELOCATED_ROMS = RELOCATED_8MFK_ROMS + VQ37_RUNTIME_ROMS
SUPPORTED_ROMS = EXACT_ROMS + RELOCATED_ROMS
ZERO_SHA256 = "0" * 64

NUMBER_RE = re.compile(r"(?<![A-Za-z0-9_])0x[0-9A-Fa-f]+")

# The dynamic telemetry page reads only on-chip RAM. The canonical source
# starts its window at the SH7058S RAM, and an SH7059 layout starts it at the
# larger RAM of its MCU; both windows end at 0x00FFC000.
CAN_DYNAMIC_WINDOW_START = 0x00FF0000
SH7059_CAN_DYNAMIC_WINDOW_START = 0x00FE8000

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

# The selector host aborts while the MAIN switch bit of the ASCD flag byte is
# set. Its canonical source tests the bit of the canonical layout, and each
# target tests the bit of its own layout.
ASCD_STATE = "ascd_state/ram"
CANONICAL_ASCD_MAIN_MASK = 0x80
# A one-bit telemetry field carries the bit of the canonical layout, which the
# hosts decode. The capture of a layout that keeps the bit elsewhere moves it
# into the wire bit of the bank byte once the fixed pages are copied, and
# clears the other bits of the byte. A field of the dynamic page moves only
# while the page carries its default row, whose configuration byte is 0; the
# bytes of an installed configuration stay as their slots read them.
# A bank page holds its header byte and seven source bytes.
BANK_PAGE_BYTES = 8
# The capture reaches every moved byte from one base register through the
# 4-bit displacement of mov.b.
BIT_MOVE_REACH = 15
FIXED_PAGE_LOOP_END = (
    "add 0x1,r6\nmov r6,r0\ncmp/eq 0x9,r0\nbf telemetry_build_page_loop\n"
)


class RuntimeTargetError(ValueError):
    """Raised when a target projection or payload lock is incomplete."""


def _binding(read, *args):
    """Read a generated binding without loading the knowledge model."""
    try:
        return read(*args)
    except runtime_bindings.RuntimeBindingsError as error:
        raise RuntimeTargetError(f"runtime bindings: {error}") from error


@lru_cache(maxsize=None)
def canonical_symbols(feature):
    """{key: value} of the JK08A target of a feature: symbol addresses,
    numbers, and record words."""
    return _binding(runtime_bindings.canonical_symbols, feature)


@lru_cache(maxsize=None)
def map_hook_keys(rom):
    """{JK08A hook word: key} of the map hooks of the layout of a ROM."""
    return _binding(runtime_bindings.map_hook_keys, rom)


@lru_cache(maxsize=None)
def ignition_state_template():
    """{family key: (table, pointer table)} that the ignition state adapter
    source names: the table base of each state-code family on the template
    layout and the pointer table of its storage there, less the ROM
    relocation of the layout."""
    return _binding(runtime_bindings.ignition_state_template)


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


def can_dynamic_window_overrides(profile):
    """Bind the dynamic telemetry window to the on-chip RAM of a layout."""
    if profile.family in rom_address_profiles.SH7059_FAMILIES:
        return {CAN_DYNAMIC_WINDOW_START: SH7059_CAN_DYNAMIC_WINDOW_START}
    return {}


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


@lru_cache(maxsize=None)
def ascd_main_mask(layout):
    """The mask of the MAIN switch bit of the ASCD flag byte on a layout."""
    return 1 << _binding(runtime_bindings.layout, layout)["ascd_main_bit"]


@lru_cache(maxsize=None)
def field_bits(layout):
    """{field: (source bit, wire bit)} of the one-bit telemetry fields that a
    layout reads: the bit of the layout and the bit of the canonical layout,
    which the wire carries."""
    wire = _binding(
        runtime_bindings.layout, runtime_bindings.CANONICAL
    )["field_bits"]
    return {
        field: (bit, wire[field])
        for field, bit in _binding(
            runtime_bindings.layout, layout
        )["field_bits"].items()
    }


@dataclass(frozen=True)
class BitMove:
    """A move of the capture: the bank byte of a one-bit field, its source
    and wire bits, and the bank byte of the dynamic page configuration that
    must be 0 for the move, or None for a field of a fixed page."""

    field: str
    byte: int
    source: int
    wire: int
    configuration: int | None


@lru_cache(maxsize=None)
def bit_moves(layout):
    """The moves of the capture of a layout in bank byte order: one for each
    one-bit field whose source bit differs from its wire bit."""
    manifest = can_telemetry_profile.load_manifest()
    fields = {item.name: item for item in manifest.fields}
    moves = []
    for name, (bit, wire) in field_bits(layout).items():
        if bit == wire:
            continue
        field = fields.get(name)
        if (
            field is None
            or field.page is None
            or field.page >= manifest.fixed_page_count
            or field.width != 1
            or field.kind != "ecu_ram"
        ):
            raise RuntimeTargetError(
                f"{name}: expected one fixed byte field of ECU RAM"
            )
        pages = {
            profile.dynamic
            for profile in manifest.profiles
            if profile.name in field.profiles and profile.dynamic is not None
            and profile.dynamic.page == field.page
        }
        if len(pages) > 1:
            raise RuntimeTargetError(f"{name}: dynamic pages differ")
        dynamic = next(iter(pages), None)
        moves.append(BitMove(
            name,
            field.page * BANK_PAGE_BYTES + field.offset,
            bit,
            wire,
            None if dynamic is None
            else dynamic.page * BANK_PAGE_BYTES
            + dynamic.configuration_offset,
        ))
    return tuple(sorted(moves, key=lambda move: move.byte))


def _move_field_bits(source, profile):
    """Move the bits of the one-bit fields that the layout of a ROM keeps in
    another bit than the canonical layout into their wire bits, after the
    fixed pages. The fixed page loop leaves r4 at the end of the fixed pages;
    the code that follows loads r0, r1 and T before it reads them."""
    context = "capture fixed page loop"
    moves = bit_moves(_binding(runtime_bindings.layout_of, profile.rom))
    if not moves:
        return _replace_source_once(
            source, FIXED_PAGE_LOOP_END, FIXED_PAGE_LOOP_END, context
        )
    manifest = can_telemetry_profile.load_manifest()
    if f"cmp/eq 0x{manifest.fixed_page_count:X},r0" not in FIXED_PAGE_LOOP_END:
        raise RuntimeTargetError(f"{context}: fixed page count differs")
    end = manifest.fixed_page_count * BANK_PAGE_BYTES
    reached = [move.byte for move in moves] + [
        move.configuration for move in moves if move.configuration is not None
    ]
    base = min(reached)
    if max(reached) - base > BIT_MOVE_REACH or not -128 <= base - end < 0:
        raise RuntimeTargetError(f"{context}: field is out of reach")
    lines = [
        "// Move the bits of the one-bit fields into their wire bits.",
        "mov r4,r1",
        f"add -0x{end - base:X},r1",
    ]
    for move in moves:
        offset = move.byte - base
        done = f"telemetry_bit_move_{move.field}_done"
        comment = (
            f"// Move bit {move.source} of {move.field} into wire bit "
            f"{move.wire}"
        )
        if move.configuration is not None:
            lines.extend((
                f"{comment} while the dynamic page carries its default row.",
                f"mov.b @(0x{move.configuration - base:X},r1),r0",
                "tst r0,r0",
                f"bf {done}",
            ))
        else:
            lines.append(f"{comment}.")
        distance = abs(move.source - move.wire)
        shift = "shlr" if move.source > move.wire else "shll"
        lines.extend((
            f"mov.b @(0x{offset:X},r1),r0",
            f"and 0x{1 << move.source:02X},r0",
            *[f"{shift}2 r0"] * (distance // 2),
            *[f"{shift} r0"] * (distance % 2),
            f"mov.b r0,@(0x{offset:X},r1)",
        ))
        if move.configuration is not None:
            lines.append(f"{done}:")
    return _replace_source_once(
        source,
        FIXED_PAGE_LOOP_END,
        FIXED_PAGE_LOOP_END + "\n".join(lines) + "\n",
        context,
    )


def _mask_source(
    source, profile, mask_of, canonical_mask, canonical, template, context
):
    """Bind a bit test, which the canonical source makes at the bit of the
    canonical layout, to the bit of the target layout."""
    home = mask_of(runtime_bindings.CANONICAL)
    if home != canonical_mask:
        raise RuntimeTargetError(
            f"{context}: the canonical source tests 0x{canonical_mask:02X}, "
            f"and the bit of {runtime_bindings.CANONICAL} is 0x{home:02X}"
        )
    mask = mask_of(_binding(runtime_bindings.layout_of, profile.rom))
    if mask == home:
        return _replace_source_once(source, canonical, canonical, context)
    return _replace_source_once(
        source, canonical, template.format(mask=mask), context
    )


def _replace_label_directive(source, label, directive, value_text, context):
    pattern = re.compile(
        rf"^({re.escape(label)}:\n{re.escape(directive)} )0x[0-9A-Fa-f]+$",
        re.MULTILINE,
    )
    matches = list(pattern.finditer(source))
    if len(matches) != 1:
        raise RuntimeTargetError(
            f"{context}: expected 1 {directive} after {label}, found {len(matches)}"
        )
    return pattern.sub(rf"\g<1>{value_text}", source, count=1)


def _replace_label_long(source, label, value, context):
    return _replace_label_directive(
        source, label, ".long", f"0x{value:08X}", context
    )


def _replace_label_word(source, label, value, context):
    return _replace_label_directive(
        source, label, ".word", f"0x{value:04X}", context
    )


def _render_selector_host(profile, mapping):
    cf = profile.cruise_free
    layout_id = _binding(runtime_bindings.layout_of, profile.rom)
    mask = ascd_main_mask(layout_id)
    source = _replace_source_once(
        _read_source("map-switching-jk08a-selector-host.s"),
        "tst 0x80,r0\nbf host_abort_selector\n",
        f"tst 0x{mask:02X},r0\nbf host_abort_selector\n",
        f"{profile.rom} selector host ASCD MAIN bit",
    )
    overrides = {
        0x000D6BA0: cf.rom.start + 0x3A0,
        0x000D6900: cf.rom.start + 0x100,
    }
    return _render_source(source, profile, mapping, overrides)


def _render_feedback_engine(profile, mapping):
    cf = profile.cruise_free
    map_symbols = profile.map_symbol_by_key
    source = _read_source("map-switching-jk08a-feedback-engine.s")
    old_mil = """// Channel 1: MIL request (0x551 byte 3, bit 5, active-high 0x20).
feedback_check_mil:
mov.l @r15,r0
tst 0x2,r0
bt feedback_advance
mov.l @(feedback_mil_byte,pc),r4
mov.b @r4,r0
and 0xDF,r0
mov r0,r7
mov r6,r0
cmp/eq 0x1,r0
bf feedback_mil_store
mov #0x20,r0
or r0,r7
feedback_mil_store:
mov r7,r0
mov.b r0,@r4
"""
    new_mil = f"""// Channel 1: MIL request (0x551 byte 3, bit 5, active-high 0x{cf.mil_mask:02X}).
// Preserve any independently asserted stock MIL during the OFF phase.
feedback_check_mil:
mov.l @r15,r0
tst 0x2,r0
bt feedback_advance
mov r6,r0
cmp/eq 0x1,r0
bf feedback_advance
mov.l @(feedback_mil_byte,pc),r4
mov.b @r4,r0
or 0x{cf.mil_mask:02X},r0
mov.b r0,@r4
"""
    source = _replace_source_once(
        source, old_mil, new_mil, f"{profile.rom} feedback MIL preservation"
    )
    overrides = {
        0x000D6BE0: cf.rom.start + 0x3E0,
        0xFFFF3AD8: map_symbols["mil_byte_address"],
    }
    return _render_source(source, profile, mapping, overrides)


def _render_startup_wrapper(
    profile,
    sw_start,
    ee_rom_start,
    sel_ram,
    limiter_commit,
    can_return_pc,
):
    ee = profile.eeprom_persistence
    stock_init = profile.map_hook_by_key["startup_initializer"].stock
    return (
        f"// Relocated startup wrapper for {profile.rom} (direct at 0x{sw_start:08X}, no thunk).\n"
        f".org 0x{sw_start:08X}\n"
        "startup_wrapper:\n"
        "sts.l pr,@-r15\n"
        "mov.l @r15,r0\n"
        "mov.l @(startup_can_pr,pc),r1\n"
        "cmp/eq r1,r0\n"
        "bf startup_check_cold\n"
        "mov.l @(0x4,r15),r0\n"
        "startup_check_cold:\n"
        "mov.l @(startup_cold_pr,pc),r1\n"
        "cmp/eq r1,r0\n"
        "bf startup_warm_reinit\n"
        "\n"
        "// Cold boot path: safe map 1 before stock init, then cruise-free + EEPROM restore.\n"
        "mov.l @(startup_selector_state,pc),r1\n"
        "mov #0x0,r0\n"
        "mov.b r0,@r1\n"
        "mov.l @(startup_stock_initializer,pc),r0\n"
        "jsr @r0\n"
        "nop\n"
        "mov.l @(startup_eeprom_boot_restore,pc),r0\n"
        "jsr @r0\n"
        "nop\n"
        "mov r0,r4\n"
        "bra startup_do_commit\n"
        "nop\n"
        "\n"
        "// Warm reinit / non-cold path: keep selector, cruise-free, and EEPROM state intact,\n"
        "// re-mirroring telemetry autostart bits cleared by telemetry_startup_wrapper.\n"
        "startup_warm_reinit:\n"
        "mov.l @(startup_stock_initializer,pc),r0\n"
        "jsr @r0\n"
        "nop\n"
        "mov.l @(startup_eeprom_warm_sync,pc),r0\n"
        "jsr @r0\n"
        "nop\n"
        "mov r0,r4\n"
        "\n"
        "startup_do_commit:\n"
        "mov.l @(startup_commit_entry,pc),r0\n"
        "jsr @r0\n"
        "nop\n"
        "lds.l @r15+,pr\n"
        "rts\n"
        "nop\n"
        "\n"
        ".align 4\n"
        "startup_can_pr:\n"
        f".long 0x{can_return_pc:08X}\n"
        "startup_cold_pr:\n"
        f".long 0x{ee.startup_cold_return_pc:08X}\n"
        "startup_stock_initializer:\n"
        f".long 0x{stock_init:08X}\n"
        "startup_selector_state:\n"
        f".long 0x{sel_ram:08X}\n"
        "startup_commit_entry:\n"
        f".long 0x{limiter_commit:08X}\n"
        "startup_eeprom_boot_restore:\n"
        f".long 0x{ee_rom_start + 0x10:08X}\n"
        "startup_eeprom_warm_sync:\n"
        f".long 0x{ee_rom_start + 0x130:08X}\n"
    )


def _render_cruise_free_selector(profile, sel_ram, limiter_commit):
    cf = profile.cruise_free
    sym = profile.map_symbol_by_key
    hooks = profile.map_hook_by_key
    c = cf.rom.start
    cr = cf.ram.start
    ctx = f"{profile.rom}.cruise_free_selector"
    source = _read_source("map-switching-cruise-free.s")
    for old_org, new_org in (
        (0x000D6820, c + 0x020),
        (0x000D6840, c + 0x040),
        (0x000D6900, c + 0x100),
        (0x000D6AE8, c + 0x2E8),
        (0x000D6BA0, c + 0x3A0),
    ):
        source = _replace_source_once(
            source, f".org 0x{old_org:08X}\n", f".org 0x{new_org:08X}\n", ctx
        )
    old_live_bsr = "bsr 0x000D6C60\n"
    new_live_bsr = f"bsr 0x{c + 0x460:08X}\n"
    if source.count(old_live_bsr) != 2:
        raise RuntimeTargetError(f"{ctx}: expected 2 cf_stationary_live calls")
    source = source.replace(old_live_bsr, new_live_bsr)
    # 16-bit unsigned coarse RPM checks on all relocated layouts.
    old_rpm = "mov.l @(cf_rpm_coarse,pc),r1\nmov.b @r1,r0\nextu.b r0,r0\n"
    new_rpm = "mov.l @(cf_rpm_coarse,pc),r1\nmov.w @r1,r0\nextu.w r0,r0\n"
    if source.count(old_rpm) != 2:
        raise RuntimeTargetError(f"{ctx}: expected 2 coarse RPM sites")
    source = source.replace(old_rpm, new_rpm)
    # Target-specific RX gate and brake masks.
    for old, new in (
        (
            "mov.l @(stat_port_state,pc),r1\nmov.b @r1,r0\ntst 0x80,r0\n",
            f"mov.l @(stat_port_state,pc),r1\nmov.b @r1,r0\ntst 0x{cf.port_ready_mask:02X},r0\n",
        ),
        (
            "mov.l @(stat_hcan1_state,pc),r1\nmov.b @r1,r0\ntst 0x1,r0\n",
            f"mov.l @(stat_hcan1_state,pc),r1\nmov.b @r1,r0\ntst 0x{cf.hcan1_init_mask:02X},r0\n",
        ),
        (
            "mov.l @(cf_brake_byte,pc),r1\nmov.b @r1,r0\ntst 0x80,r0\n",
            f"mov.l @(cf_brake_byte,pc),r1\nmov.b @r1,r0\ntst 0x{cf.brake_mask:02X},r0\n",
        ),
    ):
        source = _replace_source_once(source, old, new, ctx)
    pool = {
        "cf_init_ram": cr,
        "stat_stock_rx_dispatch": hooks["stationary_rx_dispatch"].stock,
        "stat_cf_ram": cr,
        "stat_config_addr": c,
        "stat_port_state": sym["port_state_address"],
        "stat_hcan1_state": sym["hcan1_state_address"],
        "stat_rx_state": sym["rx_state_address"],
        "stat_rx_raw_hi": sym["rx_raw_speed_address"],
        "cf_ram_base": cr,
        "cf_config_base": c,
        "cf_selector_state": sel_ram,
        "cf_limiter_commit": limiter_commit,
        "cf_diag_status": sym["diagnostic_state"],
        "cf_rpm_fine": sym["rpm_fine_address"],
        "cf_rpm_coarse": sym["rpm_coarse_address"],
        "cf_brake_byte": sym["brake_address"],
        "cf_app1_addr": sym["app1_address"],
        "cf_app2_addr": sym["app2_address"],
        "ascd_en_cf_ram": cr,
        "ascd_en_cfg": c,
        "ascd_en_sel": sel_ram,
    }
    for label, value in pool.items():
        source = _replace_label_long(source, label, value, ctx)
    return source


def _render_cruise_free_feedback(profile):
    cf = profile.cruise_free
    sym = profile.map_symbol_by_key
    hooks = profile.map_hook_by_key
    c = cf.rom.start
    cr = cf.ram.start
    ctx = f"{profile.rom}.cruise_free_feedback"
    source = _read_source("map-switching-cruise-free-feedback.s")
    for old_org, new_org in (
        (0x000D6BE0, c + 0x3E0),
        (0x000D6C60, c + 0x460),
        (0x000D6CA0, c + 0x4A0),
        (0x000D6CC0, c + 0x4C0),
        (0x000D6CE0, c + 0x4E0),
    ):
        source = _replace_source_once(
            source, f".org 0x{old_org:08X}\n", f".org 0x{new_org:08X}\n", ctx
        )
    old_val_bsr = "bsr 0x000D6AE8\n"
    new_val_bsr = f"bsr 0x{c + 0x2E8:08X}\n"
    if source.count(old_val_bsr) != 2:
        raise RuntimeTargetError(f"{ctx}: expected 2 cf_validate_cfg_local calls")
    source = source.replace(old_val_bsr, new_val_bsr)
    for old, new in (
        (
            "mov.l @(cf_live_port,pc),r1\nmov.b @r1,r0\ntst 0x80,r0\n",
            f"mov.l @(cf_live_port,pc),r1\nmov.b @r1,r0\ntst 0x{cf.port_ready_mask:02X},r0\n",
        ),
        (
            "mov.l @(cf_live_hcan,pc),r1\nmov.b @r1,r0\ntst 0x1,r0\n",
            f"mov.l @(cf_live_hcan,pc),r1\nmov.b @r1,r0\ntst 0x{cf.hcan1_init_mask:02X},r0\n",
        ),
    ):
        source = _replace_source_once(source, old, new, ctx)
    for label in ("fbext_rpm_coarse", "tach_rpm_coarse"):
        source = _replace_source_once(
            source,
            f"mov.l @({label},pc),r1\nmov.b @r1,r0\nextu.b r0,r0\n",
            f"mov.l @({label},pc),r1\nmov.w @r1,r0\nextu.w r0,r0\n",
            ctx,
        )
    pool = {
        "fbext_config": c,
        "fbext_cf_ram": cr,
        "fbext_rpm_fine": sym["rpm_fine_address"],
        "fbext_rpm_coarse": sym["rpm_coarse_address"],
        "cf_live_port": sym["port_state_address"],
        "cf_live_hcan": sym["hcan1_state_address"],
        "tach_stock_180": hooks["tach_180_serializer"].stock,
        "tach_180_payload": sym["tach_180_payload_address"],
        "tach_stock_1f9": hooks["tach_1f9_serializer"].stock,
        "tach_1f9_payload": sym["tach_1f9_payload_address"],
        "tach_config": c,
        "tach_cf_ram": cr,
        "tach_rpm_fine": sym["rpm_fine_address"],
        "tach_rpm_coarse": sym["rpm_coarse_address"],
    }
    for label, value in pool.items():
        source = _replace_label_long(source, label, value, ctx)
    return source


def _render_eeprom_persistence(profile, sel_ram):
    cf = profile.cruise_free
    ee = profile.eeprom_persistence
    sym = profile.map_symbol_by_key
    hooks = profile.map_hook_by_key
    c = cf.rom.start
    e = ee.rom.start
    er = ee.ram.start
    ctx = f"{profile.rom}.eeprom_persistence"
    source = _read_source("map-switching-eeprom.s")
    for old_org, new_org in (
        (0x000D7210, e + 0x010),
        (0x000D7330, e + 0x130),
        (0x000D73A0, e + 0x1A0),
    ):
        source = _replace_source_once(
            source, f".org 0x{old_org:08X}\n", f".org 0x{new_org:08X}\n", ctx
        )
    vbat_imm = (
        f"mov #-0x{(0x100 - ee.vbat_min_raw) & 0xFF:X},r3"
        if ee.vbat_min_raw >= 0x80
        else f"mov #0x{ee.vbat_min_raw:X},r3"
    )
    for old, new in (
        (
            "mov.l @(ee_pldr_addr,pc),r1\nmov.w @r1,r0\ntst 0x10,r0\n",
            f"mov.l @(ee_pldr_addr,pc),r1\nmov.w @r1,r0\ntst 0x{ee.pldr_ig_mask:02X},r0\n",
        ),
        (
            "mov.l @(ee_port_state_addr,pc),r1\nmov.b @r1,r0\ntst 0x80,r0\nbt ee_admit_no\ntst 0x40,r0\n",
            f"mov.l @(ee_port_state_addr,pc),r1\nmov.b @r1,r0\ntst 0x{ee.ig_on_mask:02X},r0\nbt ee_admit_no\ntst 0x{ee.start_mask:02X},r0\n",
        ),
        (
            "mov.l @(ee_shutdown_req_addr,pc),r1\nmov.b @r1,r0\ntst 0x80,r0\n",
            f"mov.l @(ee_shutdown_req_addr,pc),r1\nmov.b @r1,r0\ntst 0x{ee.shutdown_req_mask:02X},r0\n",
        ),
        (
            "mov.l @(ee_vbat_addr,pc),r1\nmov.b @r1,r0\nextu.b r0,r2\nmov #-0x76,r3\n",
            f"mov.l @(ee_vbat_addr,pc),r1\nmov.b @r1,r0\nextu.b r0,r2\n{vbat_imm}\n",
        ),
    ):
        source = _replace_source_once(source, old, new, ctx)
    telem_status = 0xFFFF5E07 + profile.ram_delta
    pool_longs = {
        "ee_cruise_free_init_1": c + 0x020,
        "ee_ram_base_1": er,
        "ee_selector_state_1": sel_ram,
        "ee_telemetry_status_1": telem_status,
        "ee_sci2_acquire_1": sym["stock_sci2_acquire"],
        "ee_sci2_release_1": sym["stock_sci2_release"],
        "ee_ram_base_2": er,
        "ee_cfg_base_2": e,
        "ee_selector_state_2": sel_ram,
        "ee_telemetry_status_2": telem_status,
        "ee_stock_sched_2": hooks["eeprom_periodic_task"].stock,
        "ee_stock_busy_2": sym["stock_busy_address"],
        "ee_sci2_acquire_2": sym["stock_sci2_acquire"],
        "ee_sci2_release_2": sym["stock_sci2_release"],
        "ee_cfg_addr_3": e,
        "ee_pldr_addr": sym["pldr_address"],
        "ee_port_state_addr": sym["port_state_address"],
        "ee_shutdown_req_addr": sym["eeprom_shutdown_req_address"],
        "ee_shutdown_state_addr": sym["eeprom_shutdown_state_address"],
        "ee_reinit_mode_addr": sym["eeprom_reinit_mode_address"],
        "ee_vbat_addr": sym["vbat_address"],
        "ee_pcdr_addr": sym["pcdr_address"],
        "ee_sci2_base": sym["sci2_base_address"],
    }
    for label, value in pool_longs.items():
        source = _replace_label_long(source, label, value, ctx)
    pool_words = {
        "ee_page_a_const": ee.page_a_address,
        "ee_page_b_const": ee.page_b_address,
        "ee_page_a_2": ee.page_a_address,
        "ee_page_b_2": ee.page_b_address,
        "ee_cs_clear_mask": (~ee.pcdr_cs_mask) & 0xFFFF,
    }
    for label, value in pool_words.items():
        source = _replace_label_word(source, label, value, ctx)
    return source


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
    can_base = can_telemetry_layout.load_layout()
    delta = profile.rom_delta
    ram_delta = profile.ram_delta
    cf_prof = profile.cruise_free
    ee_prof = profile.eeprom_persistence
    c_start = cf_prof.rom.start
    e_start = ee_prof.rom.start
    sel_ram = base.ram.selector.start + ram_delta
    limiter_commit = base.code_region_by_key["limiter_commit"].entry + delta
    can_return_pc = (
        can_base.code_region_by_key["startup_wrapper"].entry + delta + 0x24
    )
    custom_sources = {
        "selector_host": "map-switching-jk08a-selector-host.s",
        "startup_wrapper": "map-switching-jk08a-startup-wrapper.s",
        "cruise_feedback_engine": "map-switching-jk08a-feedback-engine.s",
    }
    if profile.map_variant in VQ37_MAP_VARIANTS:
        custom_sources.update({
            "lookup_adapters": "map-switching-vq37-adapters.s",
            "limiter_commit": "map-switching-vq37-limiter-commit.s",
        })
    unit_prototypes = []
    for unit in base.assembly_units:
        prototype = replace(
            unit, source=custom_sources.get(unit.key, unit.source)
        )
        if profile.map_variant in VQ37_MAP_VARIANTS:
            if unit.key == "limiter_commit":
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

    explicit_units = {
        "selector_host",
        "startup_wrapper",
        "cruise_feedback_engine",
        "cruise_free_selector",
        "cruise_free_feedback",
        "eeprom_persistence",
    }
    source_texts = {
        unit.key: _render_source(
            _read_source(unit.source), profile, mapping
        )
        for unit in unit_prototypes
        if unit.key not in explicit_units
    }
    source_texts["selector_host"] = _render_selector_host(profile, mapping)
    source_texts["cruise_feedback_engine"] = _render_feedback_engine(
        profile, mapping
    )
    source_texts["startup_wrapper"] = _render_startup_wrapper(
        profile,
        cf_prof.startup_wrapper.start,
        e_start,
        sel_ram,
        limiter_commit,
        can_return_pc,
    )
    source_texts["cruise_free_selector"] = _render_cruise_free_selector(
        profile, sel_ram, limiter_commit
    )
    source_texts["cruise_free_feedback"] = _render_cruise_free_feedback(
        profile
    )
    source_texts["eeprom_persistence"] = _render_eeprom_persistence(
        profile, sel_ram
    )
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

    extension_region_bounds = {
        "startup_wrapper": (
            cf_prof.startup_wrapper.start,
            cf_prof.startup_wrapper.end,
        ),
        "cruise_free_startup_init": (c_start + 0x020, c_start + 0x040),
        "stationary_rx_wrapper": (c_start + 0x040, c_start + 0x100),
        "cruise_free_step": (c_start + 0x100, c_start + 0x3A0),
        "cruise_free_ascd_enabled": (c_start + 0x3A0, c_start + 0x3E0),
        "cruise_free_feedback_ext": (c_start + 0x3E0, c_start + 0x4A0),
        "tach_180_wrapper": (c_start + 0x4A0, c_start + 0x4C0),
        "tach_1f9_wrapper": (c_start + 0x4C0, c_start + 0x4E0),
        "tach_override_apply": (c_start + 0x4E0, c_start + 0x5C0),
        "eeprom_boot_restore": (e_start + 0x010, e_start + 0x130),
        "eeprom_warm_sync": (e_start + 0x130, e_start + 0x1A0),
        "eeprom_task_wrapper": (e_start + 0x1A0, e_start + 0x800),
    }
    code_regions = []
    for item in base.code_regions:
        if item.key in extension_region_bounds:
            start, end = extension_region_bounds[item.key]
            code_regions.append(replace(
                item,
                span=map_switching_layout.AddressRange(
                    start, end, item.span.key
                ),
                entry=start,
            ))
            continue
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
            if item.key == "limiter_commit":
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

    extension_unit_bounds = {
        "startup_wrapper": (
            cf_prof.startup_wrapper.start,
            cf_prof.startup_wrapper.end,
        ),
        "cruise_free_selector": (c_start + 0x020, c_start + 0x3E0),
        "cruise_free_feedback": (c_start + 0x3E0, c_start + 0x5C0),
        "eeprom_persistence": (e_start + 0x010, e_start + 0x800),
    }
    units = tuple(
        _projected_unit(
            unit,
            source_texts[unit.key],
            extension_unit_bounds[unit.key][0]
            if unit.key in extension_unit_bounds
            else unit.span.start + delta,
            extension_unit_bounds[unit.key][1]
            if unit.key in extension_unit_bounds
            else unit.span.end + delta,
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
        extension=map_switching_layout.AddressRange(
            cf_prof.ram.start,
            ee_prof.ram.end,
            "ram.extension",
        ),
    )
    cruise_free_layout = map_switching_layout.CruiseFreeLayout(
        config=map_switching_layout.AddressRange(
            c_start, c_start + 0x20, "cruise_free.configuration"
        ),
        default_configuration=base.cruise_free.default_configuration,
        ram=map_switching_layout.AddressRange(
            cf_prof.ram.start, cf_prof.ram.end, "cruise_free.ram"
        ),
        rpm_fine_address=map_symbols["rpm_fine_address"],
        rpm_coarse_address=map_symbols["rpm_coarse_address"],
        brake_address=map_symbols["brake_address"],
        brake_mask=cf_prof.brake_mask,
        app1_address=map_symbols["app1_address"],
        app2_address=map_symbols["app2_address"],
        port_state_address=map_symbols["port_state_address"],
        port_ready_mask=cf_prof.port_ready_mask,
        hcan1_state_address=map_symbols["hcan1_state_address"],
        hcan1_init_mask=cf_prof.hcan1_init_mask,
        rx_state_address=map_symbols["rx_state_address"],
        rx_new_frame_mask=cf_prof.rx_new_frame_mask,
        rx_raw_speed_address=map_symbols["rx_raw_speed_address"],
        mil_byte_address=map_symbols["mil_byte_address"],
        mil_mask=cf_prof.mil_mask,
        tach_180_payload_address=map_symbols["tach_180_payload_address"],
        tach_1f9_payload_address=map_symbols["tach_1f9_payload_address"],
        diagnostic_state_address=map_symbols["diagnostic_state"],
    )
    eeprom_layout = map_switching_layout.EepromPersistenceLayout(
        config=map_switching_layout.AddressRange(
            e_start, e_start + 0x10, "eeprom_persistence.configuration"
        ),
        default_configuration=base.eeprom_persistence.default_configuration,
        ram=map_switching_layout.AddressRange(
            ee_prof.ram.start, ee_prof.ram.end, "eeprom_persistence.ram"
        ),
        page_a_address=ee_prof.page_a_address,
        page_b_address=ee_prof.page_b_address,
        sci2_base_address=map_symbols["sci2_base_address"],
        pcdr_address=map_symbols["pcdr_address"],
        pcdr_cs_mask=ee_prof.pcdr_cs_mask,
        pldr_address=map_symbols["pldr_address"],
        pldr_ig_mask=ee_prof.pldr_ig_mask,
        stock_sci2_acquire=map_symbols["stock_sci2_acquire"],
        stock_sci2_release=map_symbols["stock_sci2_release"],
        stock_busy_address=map_symbols["stock_busy_address"],
        port_state_address=map_symbols["port_state_address"],
        shutdown_req_address=map_symbols["eeprom_shutdown_req_address"],
        shutdown_state_address=map_symbols["eeprom_shutdown_state_address"],
        reinit_mode_address=map_symbols["eeprom_reinit_mode_address"],
        vbat_address=map_symbols["vbat_address"],
        vbat_min_raw=ee_prof.vbat_min_raw,
        ig_on_mask=ee_prof.ig_on_mask,
        start_mask=ee_prof.start_mask,
        shutdown_req_mask=ee_prof.shutdown_req_mask,
        startup_cold_return_pc=ee_prof.startup_cold_return_pc,
        startup_warm_return_pc=ee_prof.startup_warm_return_pc,
        startup_shared_pointer=ee_prof.startup_shared_pointer,
        startup_can_return_pc=can_return_pc,
        telemetry_status_address=0xFFFF5E07 + ram_delta,
    )
    rom_extensions = (
        map_switching_layout.AddressRange(
            cf_prof.rom.start, cf_prof.rom.end, "claimed_rom_extension[0]"
        ),
        map_switching_layout.AddressRange(
            ee_prof.rom.start, ee_prof.rom.end, "claimed_rom_extension[1]"
        ),
    )
    sci2_anchors = (
        map_switching_layout.Anchor(
            key="stock_sci2_acquire_entry",
            address=map_symbols["stock_sci2_acquire"],
            width=2,
            value=ee_prof.acquire_entry_word,
            purpose=f"Exact {profile.rom} stock SCI2 acquire helper entry word.",
        ),
        map_switching_layout.Anchor(
            key="stock_sci2_release_entry",
            address=map_symbols["stock_sci2_release"],
            width=2,
            value=ee_prof.release_entry_word,
            purpose=f"Exact {profile.rom} stock SCI2 release helper entry word.",
        ),
    )
    base_anchors = (
        tuple(
            anchor
            for anchor in base.anchors
            if anchor.key == "startup_clear_start_stock"
        )
        if profile.map_variant == "dual-cvtc"
        else ()
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
        anchors=base_anchors + sci2_anchors,
        hooks=hooks,
        families=tuple(families),
        variant=profile.map_variant,
        claimed_rom_extensions=rom_extensions,
        free_rom_extensions=rom_extensions,
        cruise_free=cruise_free_layout,
        eeprom_persistence=eeprom_layout,
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


def _project_can(
    profile, source_sha256, mapping, payloads=None,
    rolling_stage_sha256=ZERO_SHA256,
    telemetry_stage_sha256=ZERO_SHA256,
):
    base = can_telemetry_layout.load_layout()
    control_mailbox = dict(base.control_mailbox_overrides).get(
        profile.rom, base.control_mailbox
    )
    control_layout = replace(base, control_mailbox=control_mailbox)
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
                _read_source(unit.source), profile, mapping,
                overrides={
                    base.control_mailbox_address:
                        control_layout.control_mailbox_address,
                    base.control_mailbox_mask:
                        control_layout.control_mailbox_mask,
                } if unit.key == "control"
                else can_dynamic_window_overrides(profile)
                if unit.key == "capture" else None,
            )
            if unit.key == "capture":
                source_texts[unit.key] = _move_field_bits(
                    source_texts[unit.key], profile
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
        dynamic=_shift_range(base.ram.dynamic, ram_delta),
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
        control_mailbox=control_mailbox,
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
    telemetry_payloads = None if locks is None else locks.telemetry_payloads
    map_layout = _project_map(
        profile, stock_sha256, mapping, map_payloads
    )
    # A relocated target carries no Rolling Launch stage, and telemetry
    # composes on the map stage.
    telemetry_layout = _project_can(
        profile,
        stock_sha256,
        mapping,
        telemetry_payloads,
        ZERO_SHA256 if locks is None else locks.map_stage_sha256,
        ZERO_SHA256 if locks is None else locks.telemetry_stage_sha256,
    )
    return RuntimeTarget(
        rom=rom,
        family=profile.family,
        stock_image=romkit.Image(rom, str(stock.path), stock.data),
        checksum_layout=rom_checksums.layout_for_rom(rom, for_build=True),
        map_layout=map_layout,
        rolling_layout=None,
        telemetry_layout=telemetry_layout,
        map_payloads={} if map_payloads is None else map_payloads,
        rolling_payloads={},
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

    if target.rolling_layout is not None or target.rolling_payloads:
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
    if profile.cruise_free is not None:
        cf = target.map_layout.cruise_free
        allocation_differs = allocation_differs or (
            cf is None
            or cf.config.start != profile.cruise_free.rom.start
            or cf.ram.start != profile.cruise_free.ram.start
            or cf.ram.end != profile.cruise_free.ram.end
            or target.map_layout.code_region_by_key["startup_wrapper"].entry
            != profile.cruise_free.startup_wrapper.start
        )
    if profile.eeprom_persistence is not None:
        ee = target.map_layout.eeprom_persistence
        allocation_differs = allocation_differs or (
            ee is None
            or ee.config.start != profile.eeprom_persistence.rom.start
            or ee.ram.start != profile.eeprom_persistence.ram.start
            or ee.ram.end != profile.eeprom_persistence.ram.end
        )
    if allocation_differs:
        raise RuntimeTargetError(
            f"{target.rom}: projected allocation bindings differ"
        )
    if profile.map_variant in rom_address_profiles.GATED_IGNITION_MAP_VARIANTS:
        _validate_vq37_ignition_halves(target, profile)
    if profile.map_variant in map_switching_layout.FUSED_IGNITION_VARIANTS:
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


def _validate_ignition_state_pool(target, profile):
    """Bind state-family bases to their declared lookup-load/call relations.

    Fused coordinators permit multiple base pools only with positive paired consumers and
    both explicit lookup hooks. The 1ND binding requires one pool per family.
    Neither binding derives routine reachability from an address interval.
    """
    data = bytes(target.stock_image.data)
    if profile.map_variant in map_switching_layout.FUSED_IGNITION_VARIANTS:
        adapter = target.map_layout.code_region_by_key["ignition_state_adapter"].entry
        families = target.map_layout.family_by_key
        try:
            ignition_literal_consumers.require_state_hooks(profile, adapter)
            ignition_literal_consumers.paired_state_loads(
                data,
                tuple(families[key].canonical_address
                      for key in rom_address_profiles.IGNITION_STATE_FAMILY_KEYS),
                tuple(profile.map_hook_by_key[key].address for key in (
                    "ignition_state_lookup", "ignition_state_lookup_earlier")),
                rom=target.rom,
            )
        except ignition_literal_consumers.LiteralConsumerError as error:
            raise RuntimeTargetError(f"{target.rom}: {error}") from error
        return
    hook = profile.map_hook_by_key["ignition_state_lookup"]
    families = target.map_layout.family_by_key
    hook_loaders = set(_literal_loaders(data, hook.address))
    for key in rom_address_profiles.IGNITION_STATE_FAMILY_KEYS:
        sites = _aligned_literal_sites(data, families[key].canonical_address)
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
    """Bind every declared 16x16 literal and its positive call operands.

    Bit 3 selects the state-code dispatch. All aligned stock lookup literals
    require the same adapter and explicit byte-bound consumers, including
    those in the earlier region. These obligations do not establish routine
    reachability or exclude arbitrary computed consumers.
    """
    symbols = profile.map_symbol_by_key
    data = bytes(target.stock_image.data)
    if not data[symbols["ignition_coordinator_config_byte"]] & 0x08:
        raise RuntimeTargetError(
            f"{target.rom}: stock configuration gates the state-code "
            "ignition dispatch off"
        )
    try:
        ignition_literal_consumers.require_hooks(
            profile, target.map_layout.code_region_by_key["ignition_adapter"].entry
        )
        binding = ignition_literal_consumers.binding_for_rom(target.rom)
        if tuple(_aligned_literal_sites(data, binding.lookup)) != binding.literals:
            raise ignition_literal_consumers.LiteralConsumerError(
                "16x16 ignition lookup literals differ from the hooked literals"
            )
        ignition_literal_consumers.require_consumers(data, rom=target.rom)
    except ignition_literal_consumers.LiteralConsumerError as error:
        raise RuntimeTargetError(f"{target.rom}: {error}") from error


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
