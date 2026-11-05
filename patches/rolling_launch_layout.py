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
DEFAULT_RESERVATIONS = Path(__file__).with_name("jk08a-runtime-reservations.toml")
# The record size of each retired configuration schema.
RETIRED_CONFIG_SIZES = {1: 32, 2: 32, 3: 32, 4: 40, 5: 72}


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
    extension: common.AddressRange

    @property
    def active_spans(self):
        return self.state, self.extension


@dataclass(frozen=True)
class RestoredWord:
    key: str
    address: int
    value: int
    width: int = 4


@dataclass(frozen=True)
class SpeedInputs:
    word_address: int
    age_address: int
    hcan1_state_address: int
    initialized_mask: int
    port_state_address: int
    port_ready_mask: int
    raw_high_address: int
    raw_low_address: int


@dataclass(frozen=True)
class RetiredConfiguration:
    span: common.AddressRange
    schema_versions: tuple[int, ...]


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
    efficiency: common.AddressRange
    erased_rom_ranges: tuple[common.AddressRange, ...]
    retired_configurations: tuple[RetiredConfiguration, ...]
    default_configuration: bytes
    hold_actuator: bool
    payloads_ready: bool
    scheduler: SchedulerLayout
    speed_inputs: SpeedInputs
    ram: RamLayout
    code_regions: tuple[common.CodeRegion, ...]
    assembly_units: tuple[common.AssemblyUnit, ...]
    hooks: tuple[common.Hook, ...]
    diagnostics: tuple[Diagnostic, ...]
    restored_words: tuple[RestoredWord, ...]
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

    def retired_configuration_for(self, schema_version):
        """Return the span that holds a retired schema's record."""
        for item in self.retired_configurations:
            if schema_version in item.schema_versions:
                return item.span
        raise ValueError(
            f"no retired span holds configuration schema {schema_version}"
        )

    @property
    def retired_configuration_spans(self):
        return tuple(item.span for item in self.retired_configurations)

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
            "efficiency_address",
            "efficiency_size",
            "erased_rom",
            "retired_configuration",
            "default_configuration",
            "hold_actuator",
            "payloads_ready",
            "scheduler",
            "speed_inputs",
            "ram",
            "code_region",
            "assembly_unit",
            "hook",
            "diagnostic",
            "restored_word",
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
            "extension_start",
            "extension_size",
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
        extension=common.AddressRange(
            ram_raw["extension_start"],
            ram_raw["extension_start"] + ram_raw["extension_size"],
            "ram.extension",
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

    retired_configurations = []
    for index, item in enumerate(raw["retired_configuration"]):
        _require_keys(
            item,
            ("address", "size", "schema_versions"),
            f"retired_configuration[{index}]",
        )
        retired_configurations.append(RetiredConfiguration(
            span=common.AddressRange(
                item["address"],
                item["address"] + item["size"],
                f"retired_configuration[{index}]",
            ),
            schema_versions=tuple(item["schema_versions"]),
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
        efficiency=common.AddressRange(
            raw["efficiency_address"],
            raw["efficiency_address"] + raw["efficiency_size"], "efficiency",
        ),
        erased_rom_ranges=tuple(common.AddressRange(
            item["start"], item["end"], f"erased_rom[{index}]")
            for index, item in enumerate(raw["erased_rom"])),
        retired_configurations=tuple(retired_configurations),
        default_configuration=default_configuration,
        hold_actuator=raw["hold_actuator"],
        payloads_ready=raw["payloads_ready"],
        scheduler=scheduler,
        speed_inputs=SpeedInputs(**raw["speed_inputs"]),
        ram=ram,
        code_regions=tuple(code_regions),
        assembly_units=tuple(assembly_units),
        hooks=tuple(hooks),
        diagnostics=tuple(diagnostics),
        restored_words=tuple(RestoredWord(**item) for item in raw["restored_word"]),
    )
    validate_structure(layout)
    validate_reservations(layout)
    return layout


def validate_structure(layout):
    """Validate every manifest invariant that does not need ROM bytes."""
    if layout.schema_version != 4:
        raise ValueError(
            f"unsupported Rolling Launch layout schema {layout.schema_version}"
        )
    if not isinstance(layout.hold_actuator, bool):
        raise ValueError("hold_actuator must be a boolean")
    if not isinstance(layout.payloads_ready, bool):
        raise ValueError("payloads_ready must be a boolean")
    if not layout.payloads_ready and layout.hold_actuator:
        raise ValueError("unassembled payloads cannot declare a hold actuator")
    if (
        layout.byte_order != "big"
        or layout.variant != "canonical"
        or layout.rom != "JK08A"
    ):
        raise ValueError(
            f"unsupported Rolling Launch target {layout.rom!r} "
            f"variant={layout.variant!r}"
        )
    _sha256_text(layout.source_sha256, "source_sha256")
    _sha256_text(
        layout.base_composition_sha256, "base_composition_sha256"
    )
    if layout.payloads_ready:
        _sha256_text(layout.expected_composition_sha256, "expected_composition_sha256")
    elif layout.expected_composition_sha256 != "":
        raise ValueError("unassembled payloads must not claim a composition digest")
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
    if layout.configuration.start % 2 or layout.efficiency.start % 2:
        raise ValueError("configuration and efficiency must be word aligned")
    if layout.efficiency.size != contract.EFFICIENCY_TABLE_SIZE:
        raise ValueError("efficiency size differs from the runtime contract")
    if not any(span.contains(layout.efficiency) for span in claimed_ranges):
        raise ValueError("efficiency lies outside claimed ROM")
    schemas = [
        version
        for item in layout.retired_configurations
        for version in item.schema_versions
    ]
    if sorted(schemas) != list(range(1, contract.CONFIG_SCHEMA_VERSION)):
        raise ValueError("retired configuration schemas differ")
    records = sorted(
        layout.retired_configuration_spans + (layout.configuration, layout.efficiency),
        key=lambda item: (item.start, item.end),
    )
    for left, right in zip(records, records[1:]):
        if left.overlaps(right):
            raise ValueError("configuration records overlap")
    for item in layout.retired_configurations:
        if not any(span.contains(item.span) for span in claimed_ranges):
            raise ValueError("retired configuration lies outside claimed ROM")
        if any(
            RETIRED_CONFIG_SIZES[version] != item.span.size
            for version in item.schema_versions
        ):
            raise ValueError("retired configuration size differs")
    if layout.default_configuration != contract.Calibration().to_bytes():
        raise ValueError("default configuration differs from the reference model")
    calibration = contract.Calibration.from_bytes(layout.default_configuration)
    if not calibration.is_valid() or calibration.enable_mask != 0:
        raise ValueError("default configuration is not valid and fail-closed")

    scheduler = layout.scheduler
    if (
        scheduler.table_address % 4
        or scheduler.table_index < 0
        or scheduler.tick_numerator != 204800
        or scheduler.pphi_hz != 20_000_000
        or scheduler.tick_microseconds
        != scheduler.tick_numerator * 1_000_000
        // scheduler.pphi_hz
    ):
        raise ValueError("periodic scheduler timing contract differs")
    if scheduler.table_address != 0x0002196C:
        raise ValueError("canonical scheduler table address differs")
    if layout.speed_inputs != SpeedInputs(
        0xFFFF113C, 0xFFFF3B38, 0xFFFF4195, 1,
        0xFFFF4185, 0x80, 0xFFFF3B3D, 0xFFFF3B3E,
    ):
        raise ValueError("canonical speed input binding differs")
    periodic_hook = layout.hook_by_key.get("displaced_periodic_task")
    if (
        periodic_hook is not None
        and periodic_hook.address
        != scheduler.table_address + 4 * scheduler.table_index
    ):
        raise ValueError("displaced periodic task lies outside its table entry")

    if not layout.ram.proven_free.contains(layout.ram.base_reservation):
        raise ValueError("map-switching RAM lies outside the proven free range")
    if not layout.ram.proven_free.contains(layout.ram.state):
        raise ValueError("Rolling Launch state lies outside the proven free range")
    if layout.ram.base_reservation.overlaps(layout.ram.state):
        raise ValueError("Rolling Launch state overlaps map-switching RAM")
    if layout.ram.state.size != contract.STATE_SIZE:
        raise ValueError("runtime RAM sizes differ from the implementation")
    if (not layout.ram.proven_free.contains(layout.ram.extension)
            or layout.ram.extension.size != contract.EXTENSION_SIZE
            or layout.ram.extension.start % 4):
        raise ValueError("runtime extension differs from the implementation")
    if (layout.ram.extension.overlaps(layout.ram.state)
            or layout.ram.extension.overlaps(layout.ram.base_reservation)):
        raise ValueError("runtime extension overlaps another state allocation")

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
    if layout.payloads_ready and owned != set(code):
        raise ValueError("not every code region has one assembly owner")
    pending_spans = [region.span for region in layout.code_regions if region.key not in owned]
    for span in layout.erased_rom_ranges:
        if not any(claimed.contains(span) for claimed in claimed_ranges):
            raise ValueError("erased ROM lies outside claimed ROM")
    occupied_spans = sorted(
        unit_spans + pending_spans + list(layout.erased_rom_ranges)
        + [layout.configuration, layout.efficiency, *layout.retired_configuration_spans],
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
            "runtime and configuration records do not partition claimed ROM "
            "ranges"
        )

    required_hooks = {
        "displaced_periodic_task",
        "selector_arbitration",
        "startup_state_clear",
        "primary_ignition_command",
        "feedback_arbitration",
        "spark_handler",
    }
    if set(layout.hook_by_key) != required_hooks:
        raise ValueError("Rolling Launch hook set differs")
    canonical_hooks = {
        "displaced_periodic_task": (0x21970, 0xA9554, 0xD3860),
        "selector_arbitration": (0xCE8DC, 0xD2108, 0xD3880),
        "startup_state_clear": (0x27D28, 0xD22A0, 0xD38A0),
        "primary_ignition_command": (0x4E198, 0x2A892, 0xD3EA0),
        "feedback_arbitration": (0xC3FA4, 0xD35E0, 0xD41E0),
        "spark_handler": (0x202E4, 0x2AB24, 0xD60C0),
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
            (hook.address, hook.stock, hook.replacement)
            != canonical_hooks[hook.key]
        ):
            raise ValueError(f"{hook.key}: canonical hook binding differs")

    # DID and state offset of every view. The first nine read the first 18
    # bytes; the spark-cut counters share one view at +0x1C.
    expected_views = (
        (0x1211, 0x00), (0x1212, 0x02), (0x1213, 0x04), (0x1216, 0x06),
        (0x1217, 0x08), (0x1224, 0x0A), (0x1227, 0x0C), (0x1228, 0x0E),
        (0x1229, 0x10), (0x121D, 0x12), (0x121F, 0x16), (0x1232, 0x1C),
    )
    if tuple(item.did for item in layout.diagnostics) != tuple(
        did for did, _offset in expected_views
    ):
        raise ValueError("diagnostic DID set or order differs")
    for item, (_did, offset) in zip(layout.diagnostics, expected_views):
        if (
            item.did >> 8 != 0x12
            or item.pointer_address % 4
            or item.stock != 0xFFFFFFFF
            or item.target != layout.ram.state.start + offset
            or item.width != 2
            or not item.name
        ):
            raise ValueError(f"DID {item.did:#06x}: diagnostic contract differs")
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
    writes.append(layout.efficiency)
    writes.extend(layout.erased_rom_ranges)
    writes.extend(pending_spans)
    writes.extend(layout.retired_configuration_spans)
    writes.extend(common.AddressRange(
        hook.address, hook.address + hook.width, f"hook.{hook.key}"
    ) for hook in layout.hooks)
    writes.extend(common.AddressRange(
        item.pointer_address,
        item.pointer_address + 4,
        f"did.{item.did:04x}",
    ) for item in layout.diagnostics)
    expected_restores = {
        "stock_fuel_coordinator": (0x219DC, 0x4ED88),
        "retired_request_did": (0x22914, 0xFFFFFFFF),
        "retired_ceiling_did": (0x22960, 0xFFFFFFFF),
    }
    if {item.key: (item.address, item.value) for item in layout.restored_words} != expected_restores:
        raise ValueError("restored stock words differ")
    _unique(layout.restored_words, lambda item: item.key, "restored word keys")
    for item in layout.restored_words:
        if item.width != 4 or item.address % 4:
            raise ValueError("restored word width or alignment differs")
        writes.append(common.AddressRange(item.address, item.address + 4, item.key))
    writes.sort(key=lambda item: (item.start, item.end))
    for left, right in zip(writes, writes[1:]):
        if left.overlaps(right):
            raise ValueError(f"write ranges overlap: {left.key} and {right.key}")


def validate_reservations(layout, path=DEFAULT_RESERVATIONS):
    """Check the ABI against every active and future shared allocation.

    This check needs no assembled image. Executable and checksum ownership
    remain obligations of the complete cross-runtime composition gate.
    """
    with Path(path).open("rb") as source:
        raw = tomllib.load(source)
    owners = {"map_switching", "rolling_launch", "can_telemetry"}
    if (raw["schema_version"] != 1 or raw["rom"] != layout.rom
            or (raw["ram_proven_free_start"], raw["ram_proven_free_end"])
            != (layout.ram.proven_free.start, layout.ram.proven_free.end)):
        raise ValueError("shared reservation identity or proven-free RAM differs")
    groups = {}
    for kind in ("active_ram", "future_ram", "future_rom"):
        rows = raw[kind]
        if {item["owner"] for item in rows} != owners:
            raise ValueError(f"{kind}: runtime owner set differs")
        spans = []
        for index, item in enumerate(rows):
            span = common.AddressRange(item["start"], item["end"], f"{kind}[{index}]")
            if span.size <= 0 or not item["purpose"].strip():
                raise ValueError(f"{kind}: empty span or purpose")
            if kind != "future_rom" and not layout.ram.proven_free.contains(span):
                raise ValueError(f"{kind}: allocation lies outside proven-free RAM")
            spans.append((item["owner"], span))
        groups[kind] = spans
    for name, spans in (
        ("RAM", groups["active_ram"] + groups["future_ram"]),
        ("future ROM", groups["future_rom"]),
    ):
        ordered = sorted(spans, key=lambda item: item[1].start)
        for left, right in zip(ordered, ordered[1:]):
            if left[1].overlaps(right[1]):
                raise ValueError(f"{name}: allocations overlap")
    active = sorted((span.start, span.end) for owner, span in groups["active_ram"]
                    if owner == "rolling_launch")
    if active != sorted((span.start, span.end) for span in layout.ram.active_spans):
        raise ValueError("rolling_launch: active RAM differs from the ABI")
    for _owner, span in groups["future_rom"]:
        if any(span.overlaps(claimed) for claimed in layout.claimed_rom_ranges):
            raise ValueError("future ROM overlaps the Rolling Launch write set")


def validate_base_composition(layout, data):
    """Require the exact complete map-switching in-memory endpoint."""
    if not layout.payloads_ready:
        raise ValueError("schema 6 executable payloads are not assembled and qualified")
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
