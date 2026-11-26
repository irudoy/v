#!/usr/bin/env python3
"""Validated storage model for registered map-switching runtime targets.

The manifest is the single source for slot addresses shared by the firmware
contract and definition projection. JK08A is the canonical layout image;
relocated targets carry explicit source, address, and payload bindings. This
module can materialize calibration copies in memory for tests. It never writes
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

from patches import map_switching_cruise_free as cruise_free_model
from patches import map_switching_eeprom as eeprom_model
from tools.mapkit import rom as romkit


DEFAULT_MANIFEST = Path(__file__).with_name("map-switching-layout.toml")
STORAGE_BYTES = {"uint8": 1, "uint16": 2, "uint32": 4}
COMPATIBLE_IDENTITY_START = 0x008204
COMPATIBLE_IDENTITY_END = 0x00821A
COMPATIBLE_CALIBRATION_START = 0x008200
COMPATIBLE_CALIBRATION_END = 0x020000
COMPATIBLE_PROTECTED_RANGES = (
    (0x000000, COMPATIBLE_CALIBRATION_START),
    (COMPATIBLE_CALIBRATION_END, 0x100000),
)
FUSED_IGNITION_VARIANTS = frozenset({"sh7059-1me3b", "sh7059-1ek7a"})
VQ37_VARIANTS = FUSED_IGNITION_VARIANTS | {"sh7059-1nd", "sh7058-jk78"}
# The SH7059 ignition coordinators read four 8x8 state-code surfaces through
# a lookup of their own; JK78C has no state-code dispatch.
IGNITION_STATE_VARIANTS = FUSED_IGNITION_VARIANTS | {"sh7059-1nd"}
IGNITION_STATE_FAMILY_KEYS = (
    "ignition_surface_state_3",
    "ignition_surface_state_4",
    "ignition_surface_state_5",
    "ignition_surface_state_6_7",
)


def compatible_protected_ranges(rom_size):
    """Return immutable ranges for one complete supported ROM image."""
    if rom_size < COMPATIBLE_CALIBRATION_END:
        raise ValueError("compatible ROM is smaller than the calibration window")
    return (
        (0x000000, COMPATIBLE_CALIBRATION_START),
        (COMPATIBLE_CALIBRATION_END, rom_size),
    )


@dataclass(frozen=True, order=True)
class AddressRange:
    start: int
    end: int
    key: str = ""

    def __post_init__(self):
        if self.start < 0 or self.end <= self.start:
            raise ValueError(
                f"{self.key or 'range'}: invalid half-open range "
                f"[{self.start:#x}, {self.end:#x})"
            )

    @property
    def size(self):
        return self.end - self.start

    def contains(self, other):
        return self.start <= other.start and other.end <= self.end

    def overlaps(self, other):
        return self.start < other.end and other.start < self.end


@dataclass(frozen=True)
class CodeRegion:
    key: str
    span: AddressRange
    entry: int


@dataclass(frozen=True)
class AssemblyUnit:
    key: str
    source: str
    span: AddressRange
    fill: int
    language: str
    expected_sha256: str
    instruction_count: int
    data_bytes: int
    code_regions: tuple[str, ...]


@dataclass(frozen=True)
class Hook:
    key: str
    address: int
    width: int
    stock: int
    replacement: int
    purpose: str


@dataclass(frozen=True)
class Anchor:
    key: str
    address: int
    width: int
    value: int
    purpose: str


@dataclass(frozen=True)
class Family:
    key: str
    group: str
    name: str
    canonical_address: int
    width: int
    height: int
    storage_type: str
    access_kind: str
    adapter: str | None
    copy_alignment: int
    copies: tuple[int, ...]
    pointer_table: int
    stock_container_start: int
    stock_container_size: int
    selected_offset: int
    shadow_start: int | None
    runtime_shadow_address: int | None

    @property
    def element_size(self):
        return STORAGE_BYTES[self.storage_type]

    @property
    def byte_length(self):
        return self.width * self.height * self.element_size

    @property
    def all_slot_addresses(self):
        return (self.canonical_address,) + self.copies

    def slot_address(self, active_index):
        if not 0 <= active_index < len(self.all_slot_addresses):
            active_index = 0
        return self.all_slot_addresses[active_index]


@dataclass(frozen=True)
class RamLayout:
    reservation: AddressRange
    selector: AddressRange
    fuel_cut_shadow: AddressRange
    throttle_shadow: AddressRange
    throttle_selected_offset: int
    stock_throttle_runtime: int
    extension: AddressRange | None = None

    @property
    def active_spans(self):
        if self.extension is None:
            return (self.reservation,)
        return (self.reservation, self.extension)


@dataclass(frozen=True)
class CruiseFreeLayout:
    config: AddressRange
    default_configuration: bytes
    ram: AddressRange
    rpm_fine_address: int
    rpm_coarse_address: int
    brake_address: int
    brake_mask: int
    app1_address: int
    app2_address: int
    port_state_address: int
    port_ready_mask: int
    hcan1_state_address: int
    hcan1_init_mask: int
    rx_state_address: int
    rx_new_frame_mask: int
    rx_raw_speed_address: int
    mil_byte_address: int
    mil_mask: int
    tach_180_payload_address: int
    tach_1f9_payload_address: int
    diagnostic_state_address: int = 0xFFFF2A84


@dataclass(frozen=True)
class EepromPersistenceLayout:
    config: AddressRange
    default_configuration: bytes
    ram: AddressRange
    page_a_address: int
    page_b_address: int
    sci2_base_address: int
    pcdr_address: int
    pcdr_cs_mask: int
    pldr_address: int
    pldr_ig_mask: int
    stock_sci2_acquire: int
    stock_sci2_release: int
    stock_busy_address: int
    port_state_address: int
    shutdown_req_address: int
    shutdown_state_address: int
    reinit_mode_address: int
    vbat_address: int
    vbat_min_raw: int
    ig_on_mask: int = 0x80
    start_mask: int = 0x40
    shutdown_req_mask: int = 0x80
    startup_cold_return_pc: int | None = None
    startup_warm_return_pc: int | None = None
    startup_shared_pointer: bool = True
    startup_can_return_pc: int | None = None


@dataclass(frozen=True)
class FeedbackLayout:
    can_channel: int
    mailbox_index: int
    config_record_address: int
    config_record: int
    frame_id: int
    dlc: int
    serializer: int
    dispatch_literal: int
    serializer_payload_base_literal: int
    serializer_payload_base: int
    payload_offset: int
    payload_start: int
    status_byte_index: int
    status_byte_address: int
    status_mask: int
    lamp_on_value: int
    lamp_off_value: int
    phase_counts_address: int
    payload_on_frames: int
    payload_off_frames: int
    default_on_frames: int
    default_off_frames: int
    encoding_evidence: str

    def counts_bytes(self, *, payload=False):
        on_frames = (
            self.payload_on_frames if payload else self.default_on_frames
        )
        off_frames = (
            self.payload_off_frames if payload else self.default_off_frames
        )
        return bytes((on_frames, off_frames))


@dataclass(frozen=True)
class Layout:
    schema_version: int
    rom: str
    source_sha256: str
    slot_count: int
    byte_order: str
    free_rom: AddressRange
    claimed_rom: AddressRange
    ram: RamLayout
    feedback: FeedbackLayout
    code_regions: tuple[CodeRegion, ...]
    assembly_units: tuple[AssemblyUnit, ...]
    anchors: tuple[Anchor, ...]
    hooks: tuple[Hook, ...]
    families: tuple[Family, ...]
    variant: str = "single-cvtc"
    claimed_rom_extensions: tuple[AddressRange, ...] = ()
    free_rom_extensions: tuple[AddressRange, ...] = ()
    cruise_free: CruiseFreeLayout | None = None
    eeprom_persistence: EepromPersistenceLayout | None = None
    source_texts: tuple[tuple[str, str], ...] = ()
    source_literals: tuple[
        tuple[str, tuple[tuple[str, int], ...]], ...
    ] = ()

    @property
    def claimed_rom_ranges(self):
        return (self.claimed_rom,) + self.claimed_rom_extensions

    @property
    def free_rom_ranges(self):
        return (self.free_rom,) + self.free_rom_extensions

    def claimed_contains(self, span):
        return any(part.contains(span) for part in self.claimed_rom_ranges)

    @property
    def family_by_key(self):
        return {family.key: family for family in self.families}

    @property
    def family_by_address(self):
        return {
            family.canonical_address: family for family in self.families
        }

    @property
    def code_region_by_key(self):
        return {region.key: region for region in self.code_regions}

    @property
    def pointer_table_size(self):
        return self.slot_count * 4

    @property
    def assembly_unit_by_key(self):
        return {unit.key: unit for unit in self.assembly_units}

    @property
    def anchor_by_key(self):
        return {anchor.key: anchor for anchor in self.anchors}

    @property
    def assembled_region_keys(self):
        return frozenset(
            key
            for unit in self.assembly_units
            for key in unit.code_regions
        )

    @property
    def unassembled_region_keys(self):
        return frozenset(self.code_region_by_key) - self.assembled_region_keys

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

    def reserved_rom_ranges(self):
        ranges = [
            AddressRange(region.span.start, region.span.end, region.key)
            for region in self.code_regions
        ]
        for family in self.families:
            ranges.extend(
                AddressRange(
                    address,
                    address + family.byte_length,
                    f"{family.key}.map_{slot}",
                )
                for slot, address in enumerate(family.copies, 2)
            )
            ranges.append(
                AddressRange(
                    family.pointer_table,
                    family.pointer_table + self.pointer_table_size,
                    f"{family.key}.pointer_table",
                )
            )
        if self.cruise_free is not None:
            ranges.append(self.cruise_free.config)
        if self.eeprom_persistence is not None:
            ranges.append(self.eeprom_persistence.config)
        return tuple(ranges)


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


def load_layout(path=DEFAULT_MANIFEST):
    """Load a manifest without reading or modifying a ROM image."""
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    _require_keys(
        raw,
        (
            "schema_version",
            "rom",
            "source_sha256",
            "slot_count",
            "byte_order",
            "free_rom_start",
            "free_rom_end",
            "claimed_rom_start",
            "claimed_rom_end",
            "ram",
            "feedback",
            "code_region",
            "assembly_unit",
            "anchor",
            "hook",
            "family",
        ),
        path.name,
    )

    ram_raw = raw["ram"]
    _require_keys(
        ram_raw,
        (
            "reservation_start",
            "reservation_end",
            "selector_start",
            "selector_size",
            "fuel_cut_shadow_start",
            "fuel_cut_shadow_size",
            "throttle_shadow_start",
            "throttle_shadow_size",
            "throttle_selected_offset",
            "stock_throttle_runtime",
        ),
        f"{path.name} [ram]",
    )
    extension = None
    if "extension_start" in ram_raw or "extension_size" in ram_raw:
        _require_keys(
            ram_raw,
            ("extension_start", "extension_size"),
            f"{path.name} [ram]",
        )
        extension = AddressRange(
            ram_raw["extension_start"],
            ram_raw["extension_start"] + ram_raw["extension_size"],
            "ram.extension",
        )
    ram = RamLayout(
        reservation=AddressRange(
            ram_raw["reservation_start"],
            ram_raw["reservation_end"],
            "ram.reservation",
        ),
        selector=AddressRange(
            ram_raw["selector_start"],
            ram_raw["selector_start"] + ram_raw["selector_size"],
            "ram.selector",
        ),
        fuel_cut_shadow=AddressRange(
            ram_raw["fuel_cut_shadow_start"],
            ram_raw["fuel_cut_shadow_start"]
            + ram_raw["fuel_cut_shadow_size"],
            "ram.fuel_cut_shadow",
        ),
        throttle_shadow=AddressRange(
            ram_raw["throttle_shadow_start"],
            ram_raw["throttle_shadow_start"]
            + ram_raw["throttle_shadow_size"],
            "ram.throttle_shadow",
        ),
        throttle_selected_offset=ram_raw["throttle_selected_offset"],
        stock_throttle_runtime=ram_raw["stock_throttle_runtime"],
        extension=extension,
    )

    claimed_rom_extensions = []
    for index, item in enumerate(raw.get("claimed_rom_extension", ())):
        _require_keys(item, ("start", "end"), "claimed_rom_extension")
        claimed_rom_extensions.append(
            AddressRange(
                item["start"],
                item["end"],
                f"claimed_rom_extension[{index}]",
            )
        )

    cruise_free = None
    if "cruise_free" in raw:
        cf_raw = raw["cruise_free"]
        _require_keys(
            cf_raw,
            (
                "config_address",
                "config_size",
                "default_configuration",
                "ram_start",
                "ram_size",
                "rpm_fine_address",
                "rpm_coarse_address",
                "brake_address",
                "brake_mask",
                "app1_address",
                "app2_address",
                "port_state_address",
                "port_ready_mask",
                "hcan1_state_address",
                "hcan1_init_mask",
                "rx_state_address",
                "rx_new_frame_mask",
                "rx_raw_speed_address",
                "mil_byte_address",
                "mil_mask",
                "tach_180_payload_address",
                "tach_1f9_payload_address",
            ),
            f"{path.name} [cruise_free]",
        )
        try:
            default_cfg = bytes.fromhex(
                "".join(cf_raw["default_configuration"].split())
            )
        except (AttributeError, ValueError) as error:
            raise ValueError(
                "cruise_free.default_configuration is not hexadecimal"
            ) from error
        cruise_free = CruiseFreeLayout(
            config=AddressRange(
                cf_raw["config_address"],
                cf_raw["config_address"] + cf_raw["config_size"],
                "cruise_free.configuration",
            ),
            default_configuration=default_cfg,
            ram=AddressRange(
                cf_raw["ram_start"],
                cf_raw["ram_start"] + cf_raw["ram_size"],
                "cruise_free.ram",
            ),
            rpm_fine_address=cf_raw["rpm_fine_address"],
            rpm_coarse_address=cf_raw["rpm_coarse_address"],
            brake_address=cf_raw["brake_address"],
            brake_mask=cf_raw["brake_mask"],
            app1_address=cf_raw["app1_address"],
            app2_address=cf_raw["app2_address"],
            port_state_address=cf_raw["port_state_address"],
            port_ready_mask=cf_raw["port_ready_mask"],
            hcan1_state_address=cf_raw["hcan1_state_address"],
            hcan1_init_mask=cf_raw["hcan1_init_mask"],
            rx_state_address=cf_raw["rx_state_address"],
            rx_new_frame_mask=cf_raw["rx_new_frame_mask"],
            rx_raw_speed_address=cf_raw["rx_raw_speed_address"],
            mil_byte_address=cf_raw["mil_byte_address"],
            mil_mask=cf_raw["mil_mask"],
            tach_180_payload_address=cf_raw["tach_180_payload_address"],
            tach_1f9_payload_address=cf_raw["tach_1f9_payload_address"],
        )

    eeprom_persistence = None
    if "eeprom_persistence" in raw:
        ee_raw = raw["eeprom_persistence"]
        _require_keys(
            ee_raw,
            (
                "config_address",
                "config_size",
                "default_configuration",
                "ram_start",
                "ram_size",
                "page_a_address",
                "page_b_address",
                "sci2_base_address",
                "pcdr_address",
                "pcdr_cs_mask",
                "pldr_address",
                "pldr_ig_mask",
                "stock_sci2_acquire",
                "stock_sci2_release",
                "stock_busy_address",
                "port_state_address",
                "shutdown_req_address",
                "shutdown_state_address",
                "reinit_mode_address",
                "vbat_address",
                "vbat_min_raw",
            ),
            f"{path.name} [eeprom_persistence]",
        )
        try:
            default_ee_cfg = bytes.fromhex(
                "".join(ee_raw["default_configuration"].split())
            )
        except (AttributeError, ValueError) as error:
            raise ValueError(
                "eeprom_persistence.default_configuration is not hexadecimal"
            ) from error
        eeprom_persistence = EepromPersistenceLayout(
            config=AddressRange(
                ee_raw["config_address"],
                ee_raw["config_address"] + ee_raw["config_size"],
                "eeprom_persistence.configuration",
            ),
            default_configuration=default_ee_cfg,
            ram=AddressRange(
                ee_raw["ram_start"],
                ee_raw["ram_start"] + ee_raw["ram_size"],
                "eeprom_persistence.ram",
            ),
            page_a_address=ee_raw["page_a_address"],
            page_b_address=ee_raw["page_b_address"],
            sci2_base_address=ee_raw["sci2_base_address"],
            pcdr_address=ee_raw["pcdr_address"],
            pcdr_cs_mask=ee_raw["pcdr_cs_mask"],
            pldr_address=ee_raw["pldr_address"],
            pldr_ig_mask=ee_raw["pldr_ig_mask"],
            stock_sci2_acquire=ee_raw["stock_sci2_acquire"],
            stock_sci2_release=ee_raw["stock_sci2_release"],
            stock_busy_address=ee_raw["stock_busy_address"],
            port_state_address=ee_raw["port_state_address"],
            shutdown_req_address=ee_raw["shutdown_req_address"],
            shutdown_state_address=ee_raw["shutdown_state_address"],
            reinit_mode_address=ee_raw["reinit_mode_address"],
            vbat_address=ee_raw["vbat_address"],
            vbat_min_raw=ee_raw["vbat_min_raw"],
        )

    feedback_raw = raw["feedback"]
    _require_keys(
        feedback_raw,
        (
            "can_channel",
            "mailbox_index",
            "config_record_address",
            "config_record",
            "frame_id",
            "dlc",
            "serializer",
            "dispatch_literal",
            "serializer_payload_base_literal",
            "serializer_payload_base",
            "payload_offset",
            "payload_start",
            "status_byte_index",
            "status_byte_address",
            "status_mask",
            "lamp_on_value",
            "lamp_off_value",
            "phase_counts_address",
            "payload_on_frames",
            "payload_off_frames",
            "default_on_frames",
            "default_off_frames",
            "encoding_evidence",
        ),
        f"{path.name} [feedback]",
    )
    feedback = FeedbackLayout(**feedback_raw)

    code_regions = []
    for item in raw["code_region"]:
        _require_keys(item, ("key", "start", "end", "entry"), "code_region")
        code_regions.append(
            CodeRegion(
                key=item["key"],
                span=AddressRange(item["start"], item["end"], item["key"]),
                entry=item["entry"],
            )
        )

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
        assembly_units.append(
            AssemblyUnit(
                key=item["key"],
                source=item["source"],
                span=AddressRange(
                    item["start"],
                    item["end"],
                    f"assembly.{item['key']}",
                ),
                fill=item["fill"],
                language=item["language"],
                expected_sha256=item["expected_sha256"],
                instruction_count=item["instruction_count"],
                data_bytes=item["data_bytes"],
                code_regions=tuple(item["code_regions"]),
            )
        )

    anchors = []
    for item in raw["anchor"]:
        _require_keys(
            item,
            ("key", "address", "width", "value", "purpose"),
            "anchor",
        )
        anchors.append(Anchor(**item))

    hooks = []
    for item in raw["hook"]:
        _require_keys(
            item,
            ("key", "address", "width", "stock", "replacement", "purpose"),
            "hook",
        )
        hooks.append(Hook(**item))

    families = []
    for item in raw["family"]:
        _require_keys(
            item,
            (
                "key",
                "group",
                "name",
                "canonical_address",
                "width",
                "height",
                "storage_type",
                "access_kind",
                "copy_alignment",
                "copies",
                "pointer_table",
            ),
            "family",
        )
        canonical = item["canonical_address"]
        element_size = STORAGE_BYTES.get(item["storage_type"])
        if element_size is None:
            raise ValueError(
                f"{item['key']}: unsupported storage_type "
                f"{item['storage_type']!r}"
            )
        byte_length = item["width"] * item["height"] * element_size
        families.append(
            Family(
                key=item["key"],
                group=item["group"],
                name=item["name"],
                canonical_address=canonical,
                width=item["width"],
                height=item["height"],
                storage_type=item["storage_type"],
                access_kind=item["access_kind"],
                adapter=item.get("adapter"),
                copy_alignment=item["copy_alignment"],
                copies=tuple(item["copies"]),
                pointer_table=item["pointer_table"],
                stock_container_start=item.get(
                    "stock_container_start", canonical
                ),
                stock_container_size=item.get(
                    "stock_container_size", byte_length
                ),
                selected_offset=item.get("selected_offset", 0),
                shadow_start=item.get("shadow_start"),
                runtime_shadow_address=item.get("runtime_shadow_address"),
            )
        )

    layout = Layout(
        schema_version=raw["schema_version"],
        rom=raw["rom"],
        source_sha256=raw["source_sha256"],
        slot_count=raw["slot_count"],
        byte_order=raw["byte_order"],
        free_rom=AddressRange(
            raw["free_rom_start"], raw["free_rom_end"], "free_rom"
        ),
        claimed_rom=AddressRange(
            raw["claimed_rom_start"],
            raw["claimed_rom_end"],
            "claimed_rom",
        ),
        ram=ram,
        feedback=feedback,
        code_regions=tuple(code_regions),
        assembly_units=tuple(assembly_units),
        anchors=tuple(anchors),
        hooks=tuple(hooks),
        families=tuple(families),
        claimed_rom_extensions=tuple(claimed_rom_extensions),
        cruise_free=cruise_free,
        eeprom_persistence=eeprom_persistence,
    )
    validate_structure(layout)
    return layout


def validate_structure(layout):
    """Validate all manifest invariants that do not require image bytes."""
    if layout.schema_version != 2:
        raise ValueError(
            f"unsupported map-switching layout schema {layout.schema_version}"
        )
    if (
        (layout.variant == "single-cvtc" and layout.rom != "JK08A")
        or (
            layout.variant == "dual-cvtc"
            and layout.rom not in {"JK00C", "JK00D"}
        )
        or (
            layout.variant == "sh7059-1nd"
            and layout.rom not in {"1ND0A", "1ND3B"}
        )
        or (
            layout.variant == "sh7059-1me3b"
            and layout.rom != "1ME3B"
        )
        or (
            layout.variant == "sh7059-1ek7a"
            and layout.rom != "1EK7A"
        )
        or (
            layout.variant == "sh7058-jk78"
            and layout.rom != "JK78C"
        )
        or layout.variant not in {
            "single-cvtc", "dual-cvtc", *VQ37_VARIANTS
        }
    ):
        raise ValueError(
            f"unsupported map-switching target {layout.rom!r} "
            f"variant={layout.variant!r}"
        )
    if layout.byte_order != "big":
        raise ValueError("map-switching layouts must use big-endian words")
    if layout.slot_count != 5:
        raise ValueError("the pilot contract requires exactly five slots")
    if len(layout.source_sha256) != 64:
        raise ValueError("source_sha256 must contain 64 hexadecimal digits")
    try:
        bytes.fromhex(layout.source_sha256)
    except ValueError as error:
        raise ValueError("source_sha256 is not hexadecimal") from error
    for span in layout.claimed_rom_ranges:
        if not any(free.contains(span) for free in layout.free_rom_ranges):
            raise ValueError("claimed ROM range is outside the audited free region")
    ordered_claimed = sorted(
        layout.claimed_rom_ranges, key=lambda item: (item.start, item.end)
    )
    for left, right in zip(ordered_claimed, ordered_claimed[1:]):
        if left.overlaps(right):
            raise ValueError(
                f"claimed ROM ranges overlap: {left.key} and {right.key}"
            )
    required_family_keys = {
        "over_run_fuel_hold",
        "over_run_fuel_cut",
        "over_run_fuel_restore",
        "over_run_fuel_intermediate_restore",
        "high_octane_timing_state",
        "high_detonation_timing_state",
        "cold_idle_ignition_timing",
        "idle_ignition_timing",
        "exhaust_cvtc_target",
        "fuel_compensation_main",
        "rev_limit_fuel_cut",
        "rev_limit_throttle_cut",
    }
    if layout.variant == "dual-cvtc":
        required_family_keys.remove("exhaust_cvtc_target")
        required_family_keys.update({
            "intake_cvtc_target",
            "exhaust_cvtc_target",
        })
    elif layout.variant in VQ37_VARIANTS:
        required_family_keys = {
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
        if layout.variant in IGNITION_STATE_VARIANTS:
            required_family_keys.update(IGNITION_STATE_FAMILY_KEYS)
    if len(layout.families) != len(required_family_keys):
        raise ValueError(
            "the production family count differs from the target variant"
        )
    actual_family_keys = {family.key for family in layout.families}
    if actual_family_keys != required_family_keys:
        raise ValueError(
            "pilot family set differs: "
            + ", ".join(sorted(actual_family_keys ^ required_family_keys))
        )

    _unique(layout.code_regions, lambda item: item.key, "code_region keys")
    _unique(layout.assembly_units, lambda item: item.key, "assembly_unit keys")
    _unique(
        layout.assembly_units,
        lambda item: item.source,
        "assembly_unit sources",
    )
    _unique(layout.anchors, lambda item: item.key, "anchor keys")
    _unique(layout.anchors, lambda item: item.address, "anchor addresses")
    _unique(layout.hooks, lambda item: item.key, "hook keys")
    _unique(layout.hooks, lambda item: item.address, "hook addresses")
    startup_anchor = layout.anchor_by_key.get("startup_clear_start_stock")
    if layout.variant in VQ37_VARIANTS:
        allowed_vq37_anchors = (
            {"stock_sci2_acquire_entry", "stock_sci2_release_entry"}
            if layout.eeprom_persistence is not None
            else set()
        )
        unexpected = set(layout.anchor_by_key) - allowed_vq37_anchors
        if unexpected:
            raise ValueError(
                "VQ37 target must not inherit canonical anchors: "
                + ", ".join(sorted(unexpected))
            )
    elif (
        startup_anchor is None
        or startup_anchor.address != 0x000029CC
        or startup_anchor.width != 4
        or startup_anchor.value != 0xFFFF7000
    ):
        raise ValueError(
            "startup fallback clear must remain a stock read-only anchor"
        )
    _unique(layout.families, lambda item: item.key, "family keys")
    _unique(
        layout.families,
        lambda item: item.canonical_address,
        "family canonical addresses",
    )

    code = layout.code_region_by_key
    for region in layout.code_regions:
        if not layout.claimed_contains(region.span):
            raise ValueError(f"{region.key}: code region is outside claimed ROM")
        if not region.span.start <= region.entry < region.span.end:
            raise ValueError(f"{region.key}: entry is outside its code region")

    owned_code_regions = set()
    assembly_spans = []
    for unit in layout.assembly_units:
        if not layout.claimed_contains(unit.span):
            raise ValueError(
                f"{unit.key}: assembly unit is outside claimed ROM"
            )
        if (
            not unit.source
            or Path(unit.source).name != unit.source
            or not unit.source.endswith(".s")
        ):
            raise ValueError(
                f"{unit.key}: assembly source must be one local .s filename"
            )
        if not 0 <= unit.fill <= 0xFF:
            raise ValueError(f"{unit.key}: assembly fill is not a byte")
        if unit.language != "SuperH:BE:32:SH-2A":
            raise ValueError(
                f"{unit.key}: unsupported assembly language {unit.language!r}"
            )
        if len(unit.expected_sha256) != 64:
            raise ValueError(
                f"{unit.key}: assembly SHA-256 must contain 64 digits"
            )
        try:
            bytes.fromhex(unit.expected_sha256)
        except ValueError as error:
            raise ValueError(
                f"{unit.key}: assembly SHA-256 is not hexadecimal"
            ) from error
        if unit.instruction_count <= 0 or unit.data_bytes < 0:
            raise ValueError(
                f"{unit.key}: invalid assembly instruction/data counts"
            )
        if not unit.code_regions:
            raise ValueError(f"{unit.key}: assembly unit owns no code regions")
        unit_regions = []
        for key in unit.code_regions:
            if key not in code:
                raise ValueError(
                    f"{unit.key}: unknown assembled code region {key!r}"
                )
            if key in owned_code_regions:
                raise ValueError(
                    f"{key}: code region has multiple assembly owners"
                )
            owned_code_regions.add(key)
            unit_regions.append(code[key].span)
        unit_regions.sort(key=lambda item: (item.start, item.end))
        if (
            unit_regions[0].start != unit.span.start
            or unit_regions[-1].end != unit.span.end
        ):
            raise ValueError(
                f"{unit.key}: assembly span differs from owned code regions"
            )
        for left, right in zip(unit_regions, unit_regions[1:]):
            if left.end != right.start:
                raise ValueError(
                    f"{unit.key}: owned code regions are not contiguous"
                )
        assembly_spans.append(
            AddressRange(unit.span.start, unit.span.end, unit.key)
        )
    assembly_spans.sort(key=lambda item: (item.start, item.end))
    for left, right in zip(assembly_spans, assembly_spans[1:]):
        if left.overlaps(right):
            raise ValueError(
                f"assembly units overlap: {left.key} and {right.key}"
            )

    for family in layout.families:
        if family.width <= 0 or family.height <= 0:
            raise ValueError(f"{family.key}: map geometry must be positive")
        if family.copy_alignment <= 0:
            raise ValueError(f"{family.key}: copy_alignment must be positive")
        if family.byte_length % family.element_size:
            raise ValueError(f"{family.key}: map byte length is not integral")
        if len(family.copies) != layout.slot_count - 1:
            raise ValueError(
                f"{family.key}: expected {layout.slot_count - 1} copies"
            )
        for address in family.copies:
            if address % family.copy_alignment:
                raise ValueError(
                    f"{family.key}: copy {address:#x} violates "
                    f"{family.copy_alignment}-byte alignment"
                )
        if family.pointer_table % 4:
            raise ValueError(
                f"{family.key}: pointer table is not four-byte aligned"
            )
        if family.access_kind not in {"adapter", "ram_shadow"}:
            raise ValueError(
                f"{family.key}: unsupported access_kind "
                f"{family.access_kind!r}"
            )
        if family.access_kind == "adapter":
            if family.adapter not in code:
                raise ValueError(
                    f"{family.key}: unknown adapter {family.adapter!r}"
                )
            if family.shadow_start is not None:
                raise ValueError(
                    f"{family.key}: adapter family must not declare a shadow"
                )
        else:
            if family.adapter is not None:
                raise ValueError(
                    f"{family.key}: RAM-shadow family must not use an adapter"
                )
            if family.shadow_start is None:
                raise ValueError(
                    f"{family.key}: RAM-shadow family has no shadow_start"
                )
            if family.stock_container_size < family.byte_length:
                raise ValueError(
                    f"{family.key}: stock container is smaller than the map"
                )
            if not (
                0
                <= family.selected_offset
                <= family.stock_container_size - family.byte_length
            ):
                raise ValueError(
                    f"{family.key}: selected bytes fall outside the container"
                )

    ranges = sorted(
        layout.reserved_rom_ranges(), key=lambda item: (item.start, item.end)
    )
    for region in ranges:
        if not layout.claimed_contains(region):
            raise ValueError(
                f"{region.key}: [{region.start:#x}, {region.end:#x}) "
                "is outside claimed ROM"
            )
    for left, right in zip(ranges, ranges[1:]):
        if left.overlaps(right):
            raise ValueError(
                f"ROM allocations overlap: {left.key} and {right.key}"
            )

    ram_regions = (
        layout.ram.selector,
        layout.ram.fuel_cut_shadow,
        layout.ram.throttle_shadow,
    )
    for region in ram_regions:
        if not layout.ram.reservation.contains(region):
            raise ValueError(f"{region.key}: outside RAM reservation")
    if layout.ram.extension is not None and layout.ram.reservation.overlaps(
        layout.ram.extension
    ):
        raise ValueError("ram.extension overlaps ram.reservation")
    for index, left in enumerate(ram_regions):
        for right in ram_regions[index + 1 :]:
            if left.overlaps(right):
                raise ValueError(
                    f"RAM allocations overlap: {left.key} and {right.key}"
                )

    throttle = layout.family_by_key["rev_limit_throttle_cut"]
    if layout.variant not in VQ37_VARIANTS:
        fuel_cut = layout.family_by_key["rev_limit_fuel_cut"]
        if (
            fuel_cut.shadow_start != layout.ram.fuel_cut_shadow.start
            or fuel_cut.stock_container_size != layout.ram.fuel_cut_shadow.size
        ):
            raise ValueError(
                "fuel-cut family and RAM shadow declarations differ"
            )
    else:
        fuel_caps = layout.family_by_key["rev_limit_fuel_cut_caps"]
        fuel_curves = layout.family_by_key["rev_limit_fuel_cut_curves"]
        if (
            fuel_caps.shadow_start != layout.ram.fuel_cut_shadow.start
            or fuel_caps.stock_container_size != fuel_caps.byte_length
            or fuel_curves.shadow_start
            != fuel_caps.shadow_start + fuel_caps.byte_length
            or fuel_curves.stock_container_size != fuel_curves.byte_length
            or fuel_curves.shadow_start + fuel_curves.byte_length
            != layout.ram.fuel_cut_shadow.end
        ):
            raise ValueError(
                "VQ37 fuel-cut families do not tile the RAM shadow"
            )
    throttle_differs = (
        throttle.shadow_start != layout.ram.throttle_shadow.start
        or throttle.selected_offset != layout.ram.throttle_selected_offset
    )
    if layout.variant in VQ37_VARIANTS:
        throttle_differs = throttle_differs or (
            throttle.stock_container_size != throttle.byte_length
            or throttle.runtime_shadow_address is not None
            or layout.ram.stock_throttle_runtime != 0
        )
    else:
        throttle_differs = throttle_differs or (
            throttle.stock_container_size != layout.ram.throttle_shadow.size
            or throttle.runtime_shadow_address
            != layout.ram.stock_throttle_runtime
        )
    if throttle_differs:
        raise ValueError("throttle family and RAM shadow declarations differ")

    feedback = layout.feedback
    config_type = (feedback.config_record >> 24) & 0xFF
    config_dlc = (feedback.config_record >> 16) & 0xFF
    config_control = feedback.config_record & 0xFFFF
    config_frame_id = config_control >> 5
    if (
        feedback.can_channel != 1
        or feedback.mailbox_index != 3
        or config_type not in {3, 0xA3}
    ):
        raise ValueError(
            "feedback must use the validated HCAN1 transmit mailbox 3"
        )
    if config_dlc != feedback.dlc or feedback.dlc != 8:
        raise ValueError("feedback CAN configuration must have DLC 8")
    if (
        config_frame_id != feedback.frame_id
        or feedback.frame_id != 0x551
    ):
        raise ValueError("feedback CAN configuration must encode frame 0x551")
    if feedback.payload_start != (
        feedback.serializer_payload_base + feedback.payload_offset
    ):
        raise ValueError(
            "feedback payload start differs from the serializer base and offset"
        )
    if not 0 <= feedback.status_byte_index < feedback.dlc:
        raise ValueError("feedback status byte lies outside the CAN payload")
    if feedback.status_byte_address != (
        feedback.payload_start + feedback.status_byte_index
    ):
        raise ValueError(
            "feedback status address differs from its payload byte index"
        )
    if not 0 < feedback.status_mask <= 0xFF:
        raise ValueError("feedback status mask must select at least one bit")
    if (
        feedback.lamp_on_value & ~feedback.status_mask
        or feedback.lamp_off_value & ~feedback.status_mask
        or feedback.lamp_on_value == feedback.lamp_off_value
    ):
        raise ValueError(
            "feedback lamp values must be distinct values inside the mask"
        )
    if not feedback.encoding_evidence:
        raise ValueError("feedback encoding evidence must be declared")
    for label, on_frames, off_frames in (
        (
            "payload",
            feedback.payload_on_frames,
            feedback.payload_off_frames,
        ),
        (
            "default",
            feedback.default_on_frames,
            feedback.default_off_frames,
        ),
    ):
        if not (
            0 <= on_frames <= 0xFF
            and 0 <= off_frames <= 0xFF
        ):
            raise ValueError(
                f"feedback {label} frame counts must fit in uint8"
            )
        if (on_frames == 0) != (off_frames == 0):
            raise ValueError(
                f"feedback {label} frame counts must both be zero or "
                "both be nonzero"
            )

    for anchor in layout.anchors:
        if anchor.width not in {1, 2, 4}:
            raise ValueError(
                f"{anchor.key}: unsupported anchor width {anchor.width}"
            )
        limit = 1 << (anchor.width * 8)
        if not 0 <= anchor.value < limit:
            raise ValueError(
                f"{anchor.key}: value exceeds anchor width"
            )
        if not anchor.purpose:
            raise ValueError(f"{anchor.key}: anchor purpose is empty")

    code_entries = {region.entry for region in layout.code_regions}
    for hook in layout.hooks:
        if hook.width not in {1, 2, 4}:
            raise ValueError(f"{hook.key}: unsupported hook width {hook.width}")
        limit = 1 << (hook.width * 8)
        if not 0 <= hook.stock < limit:
            raise ValueError(f"{hook.key}: stock value exceeds hook width")
        if not 0 <= hook.replacement < limit:
            raise ValueError(
                f"{hook.key}: replacement value exceeds hook width"
            )
        in_reserved_ram = (
            layout.ram.reservation.start
            <= hook.replacement
            < layout.ram.reservation.end
        )
        if hook.replacement not in code_entries and not in_reserved_ram:
            raise ValueError(
                f"{hook.key}: replacement is neither a code entry nor "
                "reserved RAM"
            )

    writable_ranges = list(layout.reserved_rom_ranges())
    writable_ranges.extend(
        AddressRange(
            hook.address,
            hook.address + hook.width,
            f"hook.{hook.key}",
        )
        for hook in layout.hooks
    )
    for anchor in layout.anchors:
        anchor_range = AddressRange(
            anchor.address,
            anchor.address + anchor.width,
            f"anchor.{anchor.key}",
        )
        for writable in writable_ranges:
            if anchor_range.overlaps(writable):
                raise ValueError(
                    f"{anchor.key}: read-only anchor overlaps writable "
                    f"range {writable.key}"
                )

    feedback_hook = next(
        (
            hook
            for hook in layout.hooks
            if hook.key == "cruise_feedback_serializer"
        ),
        None,
    )
    feedback_region = code.get("cruise_feedback_wrapper")
    feedback_engine = code.get("cruise_feedback_engine")
    if (
        feedback_hook is None
        or feedback_region is None
        or feedback_engine is None
        or feedback_hook.address != feedback.dispatch_literal
        or feedback_hook.stock != feedback.serializer
        or feedback_hook.replacement != feedback_region.entry
    ):
        raise ValueError(
            "feedback metadata, serializer hook, and wrapper entry differ"
        )
    phase_counts = AddressRange(
        feedback.phase_counts_address,
        feedback.phase_counts_address + 2,
        "feedback_phase_counts",
    )
    if not feedback_engine.span.contains(phase_counts):
        raise ValueError(
            "feedback phase-count configuration is outside the engine"
        )

    adapter_count = sum(
        family.access_kind == "adapter" for family in layout.families
    )
    shadow_count = sum(
        family.access_kind == "ram_shadow" for family in layout.families
    )
    expected_access_split = {
        "single-cvtc": (10, 2),
        "dual-cvtc": (11, 2),
        "sh7059-1nd": (11 + len(IGNITION_STATE_FAMILY_KEYS), 3),
        "sh7059-1me3b": (11 + len(IGNITION_STATE_FAMILY_KEYS), 3),
        "sh7059-1ek7a": (11 + len(IGNITION_STATE_FAMILY_KEYS), 3),
        "sh7058-jk78": (11, 3),
    }[layout.variant]
    if (adapter_count, shadow_count) != expected_access_split:
        raise ValueError(
            "production adapter and RAM-shadow split differs"
        )

    expected_assembled_regions = {
        "selector_host",
        "adapter_select_helper",
        "startup_wrapper",
        "overrun_adapter",
        "full_dfco_adapter",
        "ignition_adapter",
        "fuel_compensation_adapter",
        "cvtc_target_adapter",
        "idle_ignition_adapter",
        "limiter_commit",
        "cruise_feedback_wrapper",
        "cruise_feedback_engine",
    }
    if layout.variant == "dual-cvtc":
        expected_assembled_regions.add("secondary_cvtc_target_adapter")
    elif layout.variant in VQ37_VARIANTS:
        expected_assembled_regions.remove("cvtc_target_adapter")
        expected_assembled_regions.add("idle_ignition_pool_2_adapter")
        if layout.variant in IGNITION_STATE_VARIANTS:
            expected_assembled_regions.add("ignition_state_adapter")
    if layout.cruise_free is not None:
        cf = layout.cruise_free
        if cf.config.size != cruise_free_model.CONFIG_SIZE:
            raise ValueError("cruise_free configuration size differs")
        if len(cf.default_configuration) != cf.config.size:
            raise ValueError(
                "cruise_free default configuration length differs"
            )
        decoded_cf = cruise_free_model.CruiseFreeConfig.from_bytes(
            cf.default_configuration
        )
        if not decoded_cf.is_valid() or (
            decoded_cf.to_bytes() != cf.default_configuration
        ):
            raise ValueError("cruise_free default configuration is invalid")
        if layout.eeprom_persistence is None:
            if layout.ram.extension is None or (
                cf.ram.start != layout.ram.extension.start
                or cf.ram.end != layout.ram.extension.end
            ):
                raise ValueError(
                    "cruise_free RAM range differs from ram.extension"
                )
        else:
            ee = layout.eeprom_persistence
            if layout.ram.extension is None or (
                cf.ram.overlaps(ee.ram)
                or cf.ram.start != layout.ram.extension.start
                or cf.ram.end != ee.ram.start
                or ee.ram.end != layout.ram.extension.end
            ):
                raise ValueError(
                    "cruise_free and eeprom_persistence RAM ranges do not tile ram.extension"
                )
        hook_by_key = {hook.key: hook for hook in layout.hooks}
        for hook_key, region_key in (
            ("stationary_rx_dispatch", "stationary_rx_wrapper"),
            ("tach_180_serializer", "tach_180_wrapper"),
            ("tach_1f9_serializer", "tach_1f9_wrapper"),
        ):
            hook = hook_by_key.get(hook_key)
            region = code.get(region_key)
            if hook is None or region is None or hook.replacement != region.entry:
                raise ValueError(
                    f"cruise_free hook {hook_key!r} and code region "
                    f"{region_key!r} differ"
                )
        expected_assembled_regions.update({
            "cruise_free_startup_init",
            "stationary_rx_wrapper",
            "cruise_free_step",
            "cruise_free_ascd_enabled",
            "cruise_free_feedback_ext",
            "tach_180_wrapper",
            "tach_1f9_wrapper",
            "tach_override_apply",
        })
    if layout.eeprom_persistence is not None:
        if layout.cruise_free is None:
            raise ValueError(
                "eeprom_persistence requires cruise_free layout"
            )
        ee = layout.eeprom_persistence
        if ee.config.size != eeprom_model.EEPROM_CONFIG_SIZE:
            raise ValueError("eeprom_persistence configuration size differs")
        if len(ee.default_configuration) != ee.config.size:
            raise ValueError(
                "eeprom_persistence default configuration length differs"
            )
        decoded_ee = eeprom_model.EepromPersistenceConfig.from_bytes(
            ee.default_configuration
        )
        if (
            not decoded_ee.is_valid()
            or decoded_ee.to_bytes() != ee.default_configuration
            or decoded_ee != eeprom_model.EepromPersistenceConfig()
        ):
            raise ValueError(
                "eeprom_persistence default configuration differs from model default"
            )
        if ee.ram.size != 64:
            raise ValueError("eeprom_persistence RAM size must be 64 bytes")
        if (
            ee.page_a_address != eeprom_model.PAGE_A_ADDRESS
            or ee.page_b_address != eeprom_model.PAGE_B_ADDRESS
        ):
            raise ValueError(
                "eeprom_persistence pages must match 0x0680 and 0x0700"
            )
        hook_by_key = {hook.key: hook for hook in layout.hooks}
        ee_hook = hook_by_key.get("eeprom_periodic_task")
        ee_region = code.get("eeprom_task_wrapper")
        if (
            ee_hook is None
            or ee_region is None
            or ee_hook.replacement != ee_region.entry
        ):
            raise ValueError(
                "eeprom_persistence hook and eeprom_task_wrapper entry differ"
            )
        acq_anchor = layout.anchor_by_key.get("stock_sci2_acquire_entry")
        rel_anchor = layout.anchor_by_key.get("stock_sci2_release_entry")
        if (
            acq_anchor is None
            or rel_anchor is None
            or acq_anchor.address != ee.stock_sci2_acquire
            or rel_anchor.address != ee.stock_sci2_release
        ):
            raise ValueError(
                "eeprom_persistence SCI2 acquire/release anchors differ"
            )
        expected_assembled_regions.update({
            "eeprom_boot_restore",
            "eeprom_task_wrapper",
        })
    if layout.assembled_region_keys != expected_assembled_regions:
        raise ValueError(
            "implemented assembly region set differs: "
            + ", ".join(
                sorted(
                    layout.assembled_region_keys
                    ^ expected_assembled_regions
                )
            )
        )


def erased_rom(layout):
    """Return the region that every input image keeps erased."""
    return layout.free_rom if layout.variant == "sh7058-jk78" else layout.claimed_rom


def _validate_image_contract(layout, image):
    """Validate byte anchors shared by exact and compatible input images."""
    if layout.free_rom.end > len(image.data):
        raise ValueError("audited free region extends beyond the ROM image")
    erased = erased_rom(layout)
    erased_bytes = image.data[erased.start : erased.end]
    if erased_bytes != bytes([0xFF]) * erased.size:
        first = next(
            index for index, value in enumerate(erased_bytes) if value != 0xFF
        )
        region = "free" if layout.variant == "sh7058-jk78" else "claimed"
        raise ValueError(
            f"{region} ROM is not erased at {erased.start + first:#x}"
        )
    for extension in layout.claimed_rom_extensions:
        ext_bytes = image.data[extension.start : extension.end]
        if ext_bytes != bytes([0xFF]) * extension.size:
            first = next(
                index for index, value in enumerate(ext_bytes) if value != 0xFF
            )
            raise ValueError(
                f"claimed ROM extension is not erased at "
                f"{extension.start + first:#x}"
            )

    for anchor in layout.anchors:
        actual = int.from_bytes(
            image.data[
                anchor.address : anchor.address + anchor.width
            ],
            layout.byte_order,
        )
        if actual != anchor.value:
            raise ValueError(
                f"{anchor.key}: anchor at {anchor.address:#x} is "
                f"{actual:#x}, expected {anchor.value:#x}"
            )

    for hook in layout.hooks:
        actual = int.from_bytes(
            image.data[hook.address : hook.address + hook.width],
            layout.byte_order,
        )
        if actual != hook.stock:
            raise ValueError(
                f"{hook.key}: stock literal at {hook.address:#x} is "
                f"{actual:#x}, expected {hook.stock:#x}"
            )

    feedback = layout.feedback
    config_record = int.from_bytes(
        image.data[
            feedback.config_record_address :
            feedback.config_record_address + 4
        ],
        layout.byte_order,
    )
    if config_record != feedback.config_record:
        raise ValueError(
            "feedback CAN configuration at "
            f"{feedback.config_record_address:#x} is {config_record:#x}, "
            f"expected {feedback.config_record:#x}"
        )
    payload_base = int.from_bytes(
        image.data[
            feedback.serializer_payload_base_literal :
            feedback.serializer_payload_base_literal + 4
        ],
        layout.byte_order,
    )
    if payload_base != feedback.serializer_payload_base:
        raise ValueError(
            "feedback serializer payload base at "
            f"{feedback.serializer_payload_base_literal:#x} is "
            f"{payload_base:#x}, expected "
            f"{feedback.serializer_payload_base:#x}"
        )

    for family in layout.families:
        source_end = family.canonical_address + family.byte_length
        container_end = (
            family.stock_container_start + family.stock_container_size
        )
        if source_end > len(image.data) or container_end > len(image.data):
            raise ValueError(f"{family.key}: source extends beyond the ROM")
        if (
            family.stock_container_start + family.selected_offset
            != family.canonical_address
        ):
            raise ValueError(
                f"{family.key}: canonical map is not at selected container offset"
            )
    return image


def validate_image(layout=None, image=None):
    """Validate the layout against the exact stock image and return the image."""
    layout = layout or load_layout()
    image = image or romkit.load(layout.rom)
    digest = hashlib.sha256(image.data).hexdigest()
    if digest != layout.source_sha256:
        raise ValueError(
            f"{layout.rom}: image sha256 is {digest}, layout declares "
            f"{layout.source_sha256}"
        )
    return _validate_image_contract(layout, image)


def validate_compatible_image(layout=None, image=None, stock_image=None):
    """Validate a calibrated target image against its stock baseline.

    Compatible inputs may differ only in the calibration/configuration
    partition. The vector prefix, complete upper partition, all patch anchors,
    the ROM identity, and the claimed erased region must still match the
    selected stock image. A supplied baseline must itself retain the protected
    ranges declared by the selected target layout. JK78C requires the complete
    audited free region to remain erased.
    """
    layout = layout or load_layout()
    if image is None:
        raise ValueError("compatible input image is required")
    canonical_image = validate_image(layout, romkit.load(layout.rom))
    if stock_image is None:
        stock_image = canonical_image
    else:
        _validate_image_contract(layout, stock_image)
        if len(stock_image.data) != len(canonical_image.data):
            raise ValueError(
                f"{stock_image.rom}: stock image has {len(stock_image.data)} "
                f"bytes, expected {len(canonical_image.data)}"
            )
        for start, end in compatible_protected_ranges(len(stock_image.data)):
            if stock_image.data[start:end] != canonical_image.data[start:end]:
                relative = next(
                    offset
                    for offset, (actual, expected) in enumerate(
                        zip(
                            stock_image.data[start:end],
                            canonical_image.data[start:end],
                        )
                    )
                    if actual != expected
                )
                raise ValueError(
                    f"{stock_image.rom}: stock protected ROM differs from "
                    f"canonical {layout.rom} at {start + relative:#x}"
                )
    if len(image.data) != len(stock_image.data):
        raise ValueError(
            f"{image.rom}: compatible image has {len(image.data)} bytes, "
            f"expected {len(stock_image.data)}"
        )
    _validate_image_contract(layout, image)

    identity = image.data[
        COMPATIBLE_IDENTITY_START : COMPATIBLE_IDENTITY_END
    ]
    expected_identity = stock_image.data[
        COMPATIBLE_IDENTITY_START : COMPATIBLE_IDENTITY_END
    ]
    if identity != expected_identity:
        raise ValueError(
            f"{image.rom}: calibration identity at "
            f"{COMPATIBLE_IDENTITY_START:#x} differs from selected stock"
        )

    for start, end in compatible_protected_ranges(len(stock_image.data)):
        candidate = image.data[start:end]
        baseline = stock_image.data[start:end]
        if candidate != baseline:
            relative = next(
                offset
                for offset, (actual, expected) in enumerate(
                    zip(candidate, baseline)
                )
                if actual != expected
            )
            raise ValueError(
                f"{image.rom}: protected "
                f"{'upper ROM' if start >= COMPATIBLE_CALIBRATION_END else 'ROM'} "
                f"differs from selected stock at {start + relative:#x}"
            )
    return image


def _validate_source_image(layout, image, source_policy, stock_image=None):
    if source_policy == "exact":
        return validate_image(layout, image)
    if source_policy == "compatible":
        return validate_compatible_image(layout, image, stock_image)
    raise ValueError(
        f"unsupported source policy {source_policy!r}; "
        "expected 'exact' or 'compatible'"
    )


def materialize_calibration_copies(
    layout=None, image=None, source_policy="exact", stock_image=None
):
    """Return an in-memory image with identical slot copies and pointer tables.

    Hook literals and injected code remain untouched. The result is suitable
    for unit tests and definition rendering only, not for flashing.
    """
    layout = layout or load_layout()
    image = _validate_source_image(
        layout, image, source_policy, stock_image=stock_image
    )
    data = bytearray(image.data)
    for family in layout.families:
        source = image.data[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for address in family.copies:
            data[address : address + family.byte_length] = source
        pointers = b"".join(
            address.to_bytes(4, layout.byte_order)
            for address in family.all_slot_addresses
        )
        start = family.pointer_table
        data[start : start + len(pointers)] = pointers
    return bytes(data)


def validate_assembled_blob(unit, blob):
    """Validate one raw Ghidra assembly output against its manifest lock."""
    if isinstance(blob, (str, Path)):
        blob = Path(blob).read_bytes()
    else:
        blob = bytes(blob)
    if len(blob) != unit.span.size:
        raise ValueError(
            f"{unit.key}: blob has {len(blob)} bytes, expected "
            f"{unit.span.size}"
        )
    digest = hashlib.sha256(blob).hexdigest()
    if digest != unit.expected_sha256:
        raise ValueError(
            f"{unit.key}: blob SHA-256 is {digest}, expected "
            f"{unit.expected_sha256}"
        )
    return blob


def main():
    layout = load_layout()
    validate_image(layout)
    reserved = layout.reserved_rom_ranges()
    used = sum(region.size for region in reserved)
    print(
        f"{DEFAULT_MANIFEST.relative_to(ROOT)}: "
        f"{len(layout.families)} families, {layout.slot_count} slots, "
        f"{len(layout.hooks)} verified hooks"
    )
    print(
        f"claimed ROM [{layout.claimed_rom.start:#x}, "
        f"{layout.claimed_rom.end:#x}): {layout.claimed_rom.size} bytes, "
        f"{used} bytes allocated"
    )
    print(
        f"RAM [{layout.ram.reservation.start:#x}, "
        f"{layout.ram.reservation.end:#x}): "
        f"{layout.ram.reservation.size} bytes reserved"
    )
    assembly_status = (
        "pending: "
        + ", ".join(sorted(layout.unassembled_region_keys))
        if layout.unassembled_region_keys
        else "complete"
    )
    print(
        f"assembly: {len(layout.assembly_units)} units, "
        f"{layout.assembled_instruction_count} instructions, "
        f"{layout.assembled_data_bytes} data bytes; {assembly_status}"
    )


if __name__ == "__main__":
    main()
