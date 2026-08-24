#!/usr/bin/env python3
"""Validated storage contract for registered Rolling Launch targets.

The manifest extends the complete map-switching in-memory composition. This
module validates ROM/RAM ownership, hooks, diagnostic DID pointers, the
fail-closed default calibration, and SHA-locked assembly blobs. It never writes
a ROM image.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_layout as common
from patches import rolling_launch as contract


DEFAULT_MANIFEST = Path(__file__).with_name("rolling-launch-layout.toml")


@dataclass(frozen=True)
class SchedulerLayout:
    table_address: int
    table_index: int
    tick_numerator: int
    pphi_hz: int
    tick_microseconds: int


@dataclass(frozen=True)
class RamLayout:
    proven_free: common.AddressRange
    base_reservation: common.AddressRange
    state: common.AddressRange
    fuel_shadow: common.AddressRange


@dataclass(frozen=True)
class Diagnostic:
    did: int
    pointer_address: int
    stock: int
    target: int
    width: int
    name: str


@dataclass(frozen=True)
class Layout:
    schema_version: int
    rom: str
    byte_order: str
    source_sha256: str
    base_composition_sha256: str
    expected_composition_sha256: str
    free_rom: common.AddressRange
    claimed_rom: common.AddressRange
    claimed_rom_extensions: tuple[common.AddressRange, ...]
    configuration: common.AddressRange
    default_configuration: bytes
    scheduler: SchedulerLayout
    ram: RamLayout
    code_regions: tuple[common.CodeRegion, ...]
    assembly_units: tuple[common.AssemblyUnit, ...]
    hooks: tuple[common.Hook, ...]
    diagnostics: tuple[Diagnostic, ...]
    variant: str = "canonical"
    source_texts: tuple[tuple[str, str], ...] = ()
    source_literals: tuple[
        tuple[str, tuple[tuple[str, int], ...]], ...
    ] = ()

    @property
    def code_region_by_key(self):
        return {region.key: region for region in self.code_regions}

    @property
    def assembly_unit_by_key(self):
        return {unit.key: unit for unit in self.assembly_units}

    @property
    def hook_by_key(self):
        return {hook.key: hook for hook in self.hooks}

    @property
    def diagnostic_by_did(self):
        return {item.did: item for item in self.diagnostics}

    @property
    def assembled_instruction_count(self):
        return sum(unit.instruction_count for unit in self.assembly_units)

    @property
    def assembled_data_bytes(self):
        return sum(unit.data_bytes for unit in self.assembly_units)

    @property
    def source_text_by_unit(self):
        return dict(self.source_texts)

    @property
    def source_literal_by_unit(self):
        return {
            key: dict(values) for key, values in self.source_literals
        }

    @property
    def claimed_rom_ranges(self):
        return (self.claimed_rom,) + self.claimed_rom_extensions


def _require_keys(table, keys, context):
    missing = [key for key in keys if key not in table]
    if missing:
        raise ValueError(f"{context}: missing fields {', '.join(missing)}")


def _unique(items, key, context):
    seen = set()
    for item in items:
        value = key(item)
        if value in seen:
            raise ValueError(f"{context}: duplicate value {value}")
        seen.add(value)


def _sha256_text(value, context):
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{context} must contain 64 hexadecimal digits")
    try:
        bytes.fromhex(value)
    except ValueError as error:
        raise ValueError(f"{context} is not hexadecimal") from error


def load_layout(path=DEFAULT_MANIFEST):
    """Load and structurally validate a Rolling Launch manifest."""
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    _require_keys(
        raw,
        (
            "schema_version",
            "rom",
            "byte_order",
            "source_sha256",
            "base_composition_sha256",
            "expected_composition_sha256",
            "free_rom_start",
            "free_rom_end",
            "claimed_rom_start",
            "claimed_rom_end",
            "claimed_rom_extension",
            "configuration_address",
            "configuration_size",
            "default_configuration",
            "scheduler",
            "ram",
            "code_region",
            "assembly_unit",
            "hook",
            "diagnostic",
        ),
        path.name,
    )

    scheduler_raw = raw["scheduler"]
    _require_keys(
        scheduler_raw,
        (
            "table_address",
            "table_index",
            "tick_numerator",
            "pphi_hz",
            "tick_microseconds",
        ),
        f"{path.name} [scheduler]",
    )
    scheduler = SchedulerLayout(**scheduler_raw)

    ram_raw = raw["ram"]
    _require_keys(
        ram_raw,
        (
            "proven_free_start",
            "proven_free_end",
            "base_reservation_start",
            "base_reservation_end",
            "state_start",
            "state_size",
            "fuel_shadow_start",
            "fuel_shadow_size",
        ),
        f"{path.name} [ram]",
    )
    ram = RamLayout(
        proven_free=common.AddressRange(
            ram_raw["proven_free_start"],
            ram_raw["proven_free_end"],
            "ram.proven_free",
        ),
        base_reservation=common.AddressRange(
            ram_raw["base_reservation_start"],
            ram_raw["base_reservation_end"],
            "ram.base_reservation",
        ),
        state=common.AddressRange(
            ram_raw["state_start"],
            ram_raw["state_start"] + ram_raw["state_size"],
            "ram.state",
        ),
        fuel_shadow=common.AddressRange(
            ram_raw["fuel_shadow_start"],
            ram_raw["fuel_shadow_start"] + ram_raw["fuel_shadow_size"],
            "ram.fuel_shadow",
        ),
    )

    code_regions = []
    for item in raw["code_region"]:
        _require_keys(item, ("key", "start", "end", "entry"), "code_region")
        code_regions.append(common.CodeRegion(
            key=item["key"],
            span=common.AddressRange(item["start"], item["end"], item["key"]),
            entry=item["entry"],
        ))

    assembly_units = []
    for item in raw["assembly_unit"]:
        _require_keys(
            item,
            (
                "key",
                "source",
                "start",
                "end",
                "fill",
                "language",
                "expected_sha256",
                "instruction_count",
                "data_bytes",
                "code_regions",
            ),
            "assembly_unit",
        )
        assembly_units.append(common.AssemblyUnit(
            key=item["key"],
            source=item["source"],
            span=common.AddressRange(
                item["start"], item["end"], f"assembly.{item['key']}"
            ),
            fill=item["fill"],
            language=item["language"],
            expected_sha256=item["expected_sha256"],
            instruction_count=item["instruction_count"],
            data_bytes=item["data_bytes"],
            code_regions=tuple(item["code_regions"]),
        ))

    hooks = []
    for item in raw["hook"]:
        _require_keys(
            item,
            ("key", "address", "width", "stock", "replacement", "purpose"),
            "hook",
        )
        hooks.append(common.Hook(**item))

    diagnostics = []
    for item in raw["diagnostic"]:
        _require_keys(
            item,
            ("did", "pointer_address", "stock", "target", "width", "name"),
            "diagnostic",
        )
        diagnostics.append(Diagnostic(**item))

    claimed_rom_extensions = []
    for index, item in enumerate(raw["claimed_rom_extension"]):
        _require_keys(
            item,
            ("start", "end"),
            f"claimed_rom_extension[{index}]",
        )
        claimed_rom_extensions.append(common.AddressRange(
            item["start"],
            item["end"],
            f"claimed_rom_extension[{index}]",
        ))

    try:
        default_configuration = bytes.fromhex(raw["default_configuration"])
    except (TypeError, ValueError) as error:
        raise ValueError("default_configuration is not hexadecimal") from error

    layout = Layout(
        schema_version=raw["schema_version"],
        rom=raw["rom"],
        byte_order=raw["byte_order"],
        source_sha256=raw["source_sha256"],
        base_composition_sha256=raw["base_composition_sha256"],
        expected_composition_sha256=raw["expected_composition_sha256"],
        free_rom=common.AddressRange(
            raw["free_rom_start"], raw["free_rom_end"], "free_rom"
        ),
        claimed_rom=common.AddressRange(
            raw["claimed_rom_start"], raw["claimed_rom_end"], "claimed_rom"
        ),
        claimed_rom_extensions=tuple(claimed_rom_extensions),
        configuration=common.AddressRange(
            raw["configuration_address"],
            raw["configuration_address"] + raw["configuration_size"],
            "configuration",
        ),
        default_configuration=default_configuration,
        scheduler=scheduler,
        ram=ram,
        code_regions=tuple(code_regions),
        assembly_units=tuple(assembly_units),
        hooks=tuple(hooks),
        diagnostics=tuple(diagnostics),
    )
    validate_structure(layout)
    return layout


def validate_structure(layout):
    """Validate every manifest invariant that does not need ROM bytes."""
    if layout.schema_version != 2:
        raise ValueError(
            f"unsupported Rolling Launch layout schema {layout.schema_version}"
        )
    vq37 = layout.variant == "vq37-fuel-coordinator"
    if (
        layout.byte_order != "big"
        or (
            layout.variant == "canonical" and layout.rom != "JK08A"
        )
        or (
            layout.variant == "relocated-8mfk"
            and layout.rom not in {"JK00C", "JK00D"}
        )
        or (
            vq37
            and layout.rom not in {"JK78C", "1ND0A", "1ND3B"}
        )
        or layout.variant not in {
            "canonical", "relocated-8mfk", "vq37-fuel-coordinator"
        }
    ):
        raise ValueError(
            f"unsupported Rolling Launch target {layout.rom!r} "
            f"variant={layout.variant!r}"
        )
    _sha256_text(layout.source_sha256, "source_sha256")
    _sha256_text(
        layout.base_composition_sha256, "base_composition_sha256"
    )
    _sha256_text(
        layout.expected_composition_sha256,
        "expected_composition_sha256",
    )
    claimed_ranges = sorted(
        layout.claimed_rom_ranges,
        key=lambda item: (item.start, item.end),
    )
    for span in claimed_ranges:
        if not layout.free_rom.contains(span):
            raise ValueError("claimed ROM lies outside the audited free region")
    for left, right in zip(claimed_ranges, claimed_ranges[1:]):
        if left.overlaps(right):
            raise ValueError("claimed ROM ranges overlap")
    if not any(span.contains(layout.configuration) for span in claimed_ranges):
        raise ValueError("configuration lies outside claimed ROM")
    if layout.configuration.size != contract.CONFIG_SIZE:
        raise ValueError("configuration size differs from the runtime contract")
    if layout.default_configuration != contract.Calibration().to_bytes():
        raise ValueError("default configuration differs from the reference model")
    calibration = contract.Calibration.from_bytes(layout.default_configuration)
    if not calibration.is_valid() or calibration.enable_mask != 0:
        raise ValueError("default configuration is not valid and fail-closed")

    scheduler = layout.scheduler
    if (
        scheduler.table_address % 4
        or scheduler.table_index != 0
        or scheduler.tick_numerator != 204800
        or scheduler.pphi_hz != 20_000_000
        or scheduler.tick_microseconds
        != scheduler.tick_numerator * 1_000_000
        // scheduler.pphi_hz
    ):
        raise ValueError("periodic scheduler timing contract differs")
    if (
        layout.variant == "canonical"
        and scheduler.table_address != 0x00021970
    ):
        raise ValueError("canonical scheduler table address differs")

    if not layout.ram.proven_free.contains(layout.ram.base_reservation):
        raise ValueError("map-switching RAM lies outside the proven free range")
    if not layout.ram.proven_free.contains(layout.ram.state):
        raise ValueError("Rolling Launch state lies outside the proven free range")
    if layout.ram.base_reservation.overlaps(layout.ram.state):
        raise ValueError("Rolling Launch state overlaps map-switching RAM")
    if not layout.ram.base_reservation.contains(layout.ram.fuel_shadow):
        raise ValueError("fuel shadow lies outside map-switching RAM")
    expected_state_size = 24 if vq37 else 20
    expected_fuel_shadow_size = 36 if vq37 else 12
    if (
        layout.ram.state.size != expected_state_size
        or layout.ram.fuel_shadow.size != expected_fuel_shadow_size
    ):
        raise ValueError("runtime RAM sizes differ from the implementation")

    _unique(layout.code_regions, lambda item: item.key, "code region keys")
    _unique(layout.assembly_units, lambda item: item.key, "assembly unit keys")
    _unique(layout.assembly_units, lambda item: item.source, "assembly sources")
    _unique(layout.hooks, lambda item: item.key, "hook keys")
    _unique(layout.hooks, lambda item: item.address, "hook addresses")
    _unique(layout.diagnostics, lambda item: item.did, "diagnostic DIDs")
    _unique(
        layout.diagnostics,
        lambda item: item.pointer_address,
        "diagnostic pointer addresses",
    )

    code = layout.code_region_by_key
    for region in layout.code_regions:
        if not any(span.contains(region.span) for span in claimed_ranges):
            raise ValueError(f"{region.key}: code lies outside claimed ROM")
        if not region.span.start <= region.entry < region.span.end:
            raise ValueError(f"{region.key}: entry lies outside its region")

    owned = set()
    unit_spans = []
    for unit in layout.assembly_units:
        if not any(span.contains(unit.span) for span in claimed_ranges):
            raise ValueError(f"{unit.key}: assembly lies outside claimed ROM")
        if Path(unit.source).name != unit.source or not unit.source.endswith(".s"):
            raise ValueError(f"{unit.key}: source must be one local .s file")
        if unit.language != "SuperH:BE:32:SH-2A" or unit.fill != 0xFF:
            raise ValueError(f"{unit.key}: unsupported language or fill")
        _sha256_text(unit.expected_sha256, f"{unit.key} assembly SHA-256")
        if unit.instruction_count <= 0 or unit.data_bytes < 0:
            raise ValueError(f"{unit.key}: invalid instruction/data counts")
        regions = []
        for key in unit.code_regions:
            if key not in code or key in owned:
                raise ValueError(f"{unit.key}: invalid owned region {key!r}")
            owned.add(key)
            regions.append(code[key].span)
        regions.sort(key=lambda item: item.start)
        if (
            not regions
            or regions[0].start != unit.span.start
            or regions[-1].end != unit.span.end
        ):
            raise ValueError(f"{unit.key}: span differs from owned code")
        for left, right in zip(regions, regions[1:]):
            if left.end != right.start:
                raise ValueError(f"{unit.key}: owned regions are not contiguous")
        unit_spans.append(unit.span)
    if owned != set(code):
        raise ValueError("not every code region has one assembly owner")
    occupied_spans = sorted(
        unit_spans + [layout.configuration],
        key=lambda item: (item.start, item.end),
    )
    occupied_groups = []
    for span in occupied_spans:
        if occupied_groups and occupied_groups[-1][1] == span.start:
            occupied_groups[-1] = (occupied_groups[-1][0], span.end)
        else:
            occupied_groups.append((span.start, span.end))
    expected_groups = [(span.start, span.end) for span in claimed_ranges]
    if occupied_groups != expected_groups:
        raise ValueError(
            "runtime and configuration do not partition claimed ROM ranges"
        )

    required_hooks = {
        "periodic_scheduler_index_0",
        "selector_arbitration",
        "startup_state_clear",
        "primary_ignition_command",
        "feedback_arbitration",
    }
    if vq37:
        required_hooks.add("fuel_cut_coordinator")
    if set(layout.hook_by_key) != required_hooks:
        raise ValueError("Rolling Launch hook set differs")
    canonical_hooks = {
        "periodic_scheduler_index_0": (0x21970, 0xA9554, 0xD3860),
        "selector_arbitration": (0xCE8DC, 0xD2108, 0xD3880),
        "startup_state_clear": (0x27D28, 0xD22A0, 0xD38A0),
        "primary_ignition_command": (0x4E198, 0x2A892, 0xD3EA0),
        "feedback_arbitration": (0xC3FA4, 0xD35E0, 0xD41E0),
    }
    entries = {region.entry for region in layout.code_regions}
    for hook in layout.hooks:
        if (
            hook.address % 4
            or hook.width != 4
            or hook.replacement not in entries
            or not hook.purpose
        ):
            raise ValueError(f"{hook.key}: hook contract differs")
        if (
            layout.variant == "canonical"
            and (hook.address, hook.stock, hook.replacement)
            != canonical_hooks[hook.key]
        ):
            raise ValueError(f"{hook.key}: canonical hook binding differs")

    expected_dids = (0x1211, 0x1212, 0x1213, 0x1216, 0x1217,
                     0x1224, 0x1227, 0x1228, 0x1229)
    if tuple(item.did for item in layout.diagnostics) != expected_dids:
        raise ValueError("diagnostic DID set or order differs")
    expected_targets = tuple(range(
        layout.ram.state.start, layout.ram.state.start + 18, 2
    ))
    for item, target in zip(layout.diagnostics, expected_targets):
        if (
            item.did >> 8 != 0x12
            or item.pointer_address % 4
            or item.stock != 0xFFFFFFFF
            or item.target != target
            or item.width != 2
            or not item.name
        ):
            raise ValueError(f"DID {item.did:#06x}: diagnostic contract differs")
        if layout.variant == "canonical":
            low = item.did & 0xFF
            expected_pointer = 0x0002289C + low * 4
            if item.pointer_address != expected_pointer:
                raise ValueError(
                    f"DID {item.did:#06x}: canonical pointer differs"
                )

    writes = [
        common.AddressRange(unit.span.start, unit.span.end, f"unit.{unit.key}")
        for unit in layout.assembly_units
    ]
    writes.append(layout.configuration)
    writes.extend(common.AddressRange(
        hook.address, hook.address + hook.width, f"hook.{hook.key}"
    ) for hook in layout.hooks)
    writes.extend(common.AddressRange(
        item.pointer_address,
        item.pointer_address + 4,
        f"did.{item.did:04x}",
    ) for item in layout.diagnostics)
    writes.sort(key=lambda item: (item.start, item.end))
    for left, right in zip(writes, writes[1:]):
        if left.overlaps(right):
            raise ValueError(f"write ranges overlap: {left.key} and {right.key}")


def validate_base_composition(layout, data):
    """Require the exact complete map-switching in-memory endpoint."""
    data = bytes(data)
    actual_sha256 = hashlib.sha256(data).hexdigest()
    if actual_sha256 != layout.base_composition_sha256:
        raise ValueError(
            "base map-switching composition SHA-256 is "
            f"{actual_sha256}, expected {layout.base_composition_sha256}"
        )
    for hook in layout.hooks:
        actual = int.from_bytes(
            data[hook.address : hook.address + hook.width], layout.byte_order
        )
        if actual != hook.stock:
            raise ValueError(f"{hook.key}: base hook value is {actual:#x}")
    for item in layout.diagnostics:
        actual = int.from_bytes(
            data[item.pointer_address : item.pointer_address + 4],
            layout.byte_order,
        )
        if actual != item.stock:
            raise ValueError(f"DID {item.did:#06x}: base pointer is {actual:#x}")
    for span in layout.claimed_rom_ranges:
        erased = bytes([0xFF]) * span.size
        if data[span.start : span.end] != erased:
            raise ValueError(
                f"Rolling Launch claimed ROM {span.key} is not erased in the base"
            )
    return data


def validate_assembled_blob(unit, blob):
    """Validate one raw Ghidra assembly span against its manifest lock."""
    return common.validate_assembled_blob(unit, blob)
