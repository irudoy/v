#!/usr/bin/env python3
"""Validated ROM, RAM, hook, and reserve model for telemetry targets."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import can_telemetry
from patches import can_telemetry_profile
from patches import map_switching_layout as common


DEFAULT_MANIFEST = Path(__file__).with_name("can-telemetry-layout.toml")


@dataclass(frozen=True)
class RamLayout:
    proven_free: common.AddressRange
    lower_runtime_end: int
    reservation: common.AddressRange
    active: common.AddressRange
    future: common.AddressRange
    state: common.AddressRange
    bank_a: common.AddressRange
    bank_b: common.AddressRange
    event: common.AddressRange
    active_reserved: common.AddressRange


@dataclass(frozen=True)
class Layout:
    schema_version: int
    rom: str
    byte_order: str
    source_sha256: str
    base_composition_sha256: str
    expected_composition_sha256: str
    free_rom: common.AddressRange
    owned_rom: common.AddressRange
    reserved_rom: common.AddressRange
    configuration: common.AddressRange
    mailbox_record_address: int
    mailbox_record_stock: int
    ram: RamLayout
    code_regions: tuple[common.CodeRegion, ...]
    assembly_units: tuple[common.AssemblyUnit, ...]
    hooks: tuple[common.Hook, ...]
    variant: str = "combined-mailbox26"
    source_texts: tuple[tuple[str, str], ...] = ()
    source_literals: tuple[
        tuple[str, tuple[tuple[str, int], ...]], ...
    ] = ()

    @property
    def code_region_by_key(self):
        return {item.key: item for item in self.code_regions}

    @property
    def assembly_unit_by_key(self):
        return {item.key: item for item in self.assembly_units}

    @property
    def hook_by_key(self):
        return {item.key: item for item in self.hooks}

    @property
    def assembled_instruction_count(self):
        return sum(item.instruction_count for item in self.assembly_units)

    @property
    def assembled_data_bytes(self):
        return sum(item.data_bytes for item in self.assembly_units)

    @property
    def source_text_by_unit(self):
        return dict(self.source_texts)

    @property
    def source_literal_by_unit(self):
        return {
            key: dict(values) for key, values in self.source_literals
        }


def _require_keys(table, keys, context):
    missing = sorted(set(keys) - set(table))
    if missing:
        raise ValueError(f"{context}: missing fields {missing}")


def _range(raw, start, end, key):
    return common.AddressRange(raw[start], raw[end], key)


def _sha(value, context):
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"{context}: expected 64 hexadecimal digits")
    try:
        bytes.fromhex(value)
    except ValueError as error:
        raise ValueError(f"{context}: digest is not hexadecimal") from error


def _unique(items, key, context):
    values = [key(item) for item in items]
    if len(values) != len(set(values)):
        raise ValueError(f"{context}: duplicate values")


def load_layout(path=DEFAULT_MANIFEST):
    path = Path(path)
    with path.open("rb") as source:
        raw = tomllib.load(source)
    _require_keys(
        raw,
        (
            "schema_version", "rom", "byte_order", "source_sha256",
            "base_composition_sha256", "expected_composition_sha256",
            "free_rom_start", "free_rom_end", "owned_rom_start",
            "owned_rom_end", "reserved_rom_start", "reserved_rom_end",
            "configuration_address", "configuration_size",
            "mailbox_record_address", "mailbox_record_stock", "ram",
            "code_region", "assembly_unit", "hook",
        ),
        path.name,
    )
    ram_raw = raw["ram"]
    _require_keys(
        ram_raw,
        (
            "proven_free_start", "proven_free_end", "lower_runtime_end",
            "reservation_start", "reservation_end", "active_start",
            "active_end", "future_start", "future_end", "state_start",
            "state_size", "bank_a_start", "bank_size", "bank_b_start",
            "event_start", "event_size", "active_reserved_start",
            "active_reserved_size",
        ),
        f"{path.name} [ram]",
    )
    ram = RamLayout(
        proven_free=_range(ram_raw, "proven_free_start", "proven_free_end", "ram.proven_free"),
        lower_runtime_end=ram_raw["lower_runtime_end"],
        reservation=_range(ram_raw, "reservation_start", "reservation_end", "ram.reservation"),
        active=_range(ram_raw, "active_start", "active_end", "ram.active"),
        future=_range(ram_raw, "future_start", "future_end", "ram.future"),
        state=common.AddressRange(ram_raw["state_start"], ram_raw["state_start"] + ram_raw["state_size"], "ram.state"),
        bank_a=common.AddressRange(ram_raw["bank_a_start"], ram_raw["bank_a_start"] + ram_raw["bank_size"], "ram.bank_a"),
        bank_b=common.AddressRange(ram_raw["bank_b_start"], ram_raw["bank_b_start"] + ram_raw["bank_size"], "ram.bank_b"),
        event=common.AddressRange(ram_raw["event_start"], ram_raw["event_start"] + ram_raw["event_size"], "ram.event"),
        active_reserved=common.AddressRange(
            ram_raw["active_reserved_start"],
            ram_raw["active_reserved_start"] + ram_raw["active_reserved_size"],
            "ram.active_reserved",
        ),
    )
    code_regions = tuple(
        common.CodeRegion(
            item["key"],
            common.AddressRange(item["start"], item["end"], item["key"]),
            item["entry"],
        )
        for item in raw["code_region"]
    )
    assembly_units = tuple(
        common.AssemblyUnit(
            key=item["key"],
            source=item["source"],
            span=common.AddressRange(item["start"], item["end"], f"assembly.{item['key']}"),
            fill=item["fill"],
            language=item["language"],
            expected_sha256=item["expected_sha256"],
            instruction_count=item["instruction_count"],
            data_bytes=item["data_bytes"],
            code_regions=tuple(item["code_regions"]),
        )
        for item in raw["assembly_unit"]
    )
    hooks = tuple(common.Hook(**item) for item in raw["hook"])
    layout = Layout(
        schema_version=raw["schema_version"],
        rom=raw["rom"],
        byte_order=raw["byte_order"],
        source_sha256=raw["source_sha256"],
        base_composition_sha256=raw["base_composition_sha256"],
        expected_composition_sha256=raw["expected_composition_sha256"],
        free_rom=_range(raw, "free_rom_start", "free_rom_end", "free_rom"),
        owned_rom=_range(raw, "owned_rom_start", "owned_rom_end", "owned_rom"),
        reserved_rom=_range(raw, "reserved_rom_start", "reserved_rom_end", "reserved_rom"),
        configuration=common.AddressRange(
            raw["configuration_address"],
            raw["configuration_address"] + raw["configuration_size"],
            "configuration",
        ),
        mailbox_record_address=raw["mailbox_record_address"],
        mailbox_record_stock=raw["mailbox_record_stock"],
        ram=ram,
        code_regions=code_regions,
        assembly_units=assembly_units,
        hooks=hooks,
    )
    validate_structure(layout)
    return layout


def validate_structure(layout):
    if layout.schema_version != 2:
        raise ValueError(f"unsupported CAN telemetry layout schema {layout.schema_version}")
    if (
        layout.byte_order != "big"
        or (
            layout.variant == "combined-mailbox26"
            and layout.rom != "JK08A"
        )
        or (
            layout.variant == "mailbox24-tail-chain"
            and layout.rom not in {"JK00C", "JK00D"}
        )
        or (
            layout.variant == "mailbox26-tail-chain"
            and layout.rom not in {"1ND0A", "1ND3B", "1ME3B", "JK78C"}
        )
        or layout.variant not in {
            "combined-mailbox26",
            "mailbox24-tail-chain",
            "mailbox26-tail-chain",
        }
    ):
        raise ValueError(
            f"unsupported CAN telemetry target {layout.rom!r} "
            f"variant={layout.variant!r}"
        )
    _sha(layout.source_sha256, "source_sha256")
    _sha(layout.base_composition_sha256, "base_composition_sha256")
    _sha(layout.expected_composition_sha256, "expected_composition_sha256")
    if not layout.free_rom.contains(layout.owned_rom):
        raise ValueError("owned ROM lies outside the audited free region")
    if not layout.owned_rom.contains(layout.reserved_rom):
        raise ValueError("reserved ROM lies outside the telemetry budget")
    if layout.configuration.size != can_telemetry.CONFIG_SIZE:
        raise ValueError("configuration size differs from the runtime contract")
    if not layout.owned_rom.contains(layout.configuration):
        raise ValueError("configuration lies outside owned ROM")
    if layout.variant == "combined-mailbox26":
        if (
            layout.owned_rom.start != 0x000D4280
            or layout.owned_rom.end != 0x000D6000
            or layout.configuration.start != 0x000D4E00
            or layout.configuration.end != 0x000D4E10
            or layout.reserved_rom.start != 0x000D5000
            or layout.reserved_rom.end != layout.owned_rom.end
            or layout.mailbox_record_address != 0x000097BE
            or layout.mailbox_record_stock != 0x05000000
        ):
            raise ValueError("fixed canonical ROM ownership differs")
    elif (
        layout.configuration.size != 16
        or layout.reserved_rom.end != layout.owned_rom.end
        or layout.mailbox_record_address % 2
        or layout.mailbox_record_stock != 0x05000000
    ):
        raise ValueError("relocated ROM ownership contract differs")

    _unique(layout.code_regions, lambda item: item.key, "code regions")
    _unique(layout.code_regions, lambda item: item.entry, "code entries")
    _unique(layout.assembly_units, lambda item: item.key, "assembly units")
    _unique(layout.hooks, lambda item: item.key, "hooks")
    _unique(layout.hooks, lambda item: item.address, "hook addresses")
    code = layout.code_region_by_key
    owned_code = set()
    spans = []
    for unit in layout.assembly_units:
        if not layout.owned_rom.contains(unit.span):
            raise ValueError(f"{unit.key}: assembly lies outside owned ROM")
        if unit.span.overlaps(layout.reserved_rom) or unit.span.overlaps(layout.configuration):
            raise ValueError(f"{unit.key}: assembly overlaps configuration or reserve")
        if Path(unit.source).name != unit.source or not unit.source.endswith(".s"):
            raise ValueError(f"{unit.key}: source must be one local .s file")
        if unit.fill != 0xFF or unit.language != "SuperH:BE:32:SH-2A":
            raise ValueError(f"{unit.key}: unsupported fill or language")
        _sha(unit.expected_sha256, f"{unit.key} SHA-256")
        if unit.instruction_count < 0 or unit.data_bytes < 0:
            raise ValueError(f"{unit.key}: invalid instruction or data count")
        regions = [code[key].span for key in unit.code_regions]
        if unit.key == "tables":
            if regions or unit.instruction_count != 0:
                raise ValueError("generated tables unit must contain only data")
        else:
            if not regions or regions[0].start != unit.span.start or regions[-1].end != unit.span.end:
                raise ValueError(f"{unit.key}: code regions do not cover its span")
            for left, right in zip(regions, regions[1:]):
                if left.end != right.start:
                    raise ValueError(f"{unit.key}: code regions are not contiguous")
        for key in unit.code_regions:
            if key in owned_code:
                raise ValueError(f"{unit.key}: code region {key} has multiple owners")
            owned_code.add(key)
        spans.append(unit.span)
    if owned_code != set(code):
        raise ValueError("not every code region has one assembly owner")
    active_spans = sorted(spans + [layout.configuration], key=lambda item: item.start)
    if active_spans[0].start != layout.owned_rom.start:
        raise ValueError("active ROM does not start at the owned boundary")
    for left, right in zip(active_spans, active_spans[1:]):
        if left.end != right.start:
            raise ValueError("active ROM spans are not contiguous")
    if active_spans[-1].end > layout.reserved_rom.start:
        raise ValueError("active ROM overlaps the reserve boundary")
    if (
        layout.variant == "combined-mailbox26"
        and active_spans[-1].end != layout.reserved_rom.start
    ):
        raise ValueError("canonical active ROM does not end at the reserve")

    required_hooks = {
        "coherent_snapshot_call", "knock_interval_latch",
        "knock_margin_latch", "startup_state_clear", "hcan1_sle1_vector",
        "hcan1_primary_init", "hcan1_recovery_init",
    }
    if set(layout.hook_by_key) != required_hooks:
        raise ValueError("CAN telemetry hook set differs")
    canonical_hooks = {
        "coherent_snapshot_call": (0x28090, 0x20DFE, 0xD4280),
        "knock_interval_latch": (0x21A70, 0x493E8, 0xD42B0),
        "knock_margin_latch": (0x4A9C0, 0x4A238, 0xD4600),
        "startup_state_clear": (0x27D28, 0xD38A0, 0xD42F0),
        "hcan1_sle1_vector": (0x203A0, 0xC7914, 0xD4800),
        "hcan1_primary_init": (0x2D7FC, 0xC338A, 0xD4E10),
        "hcan1_recovery_init": (0xC3B10, 0xC338A, 0xD4E10),
    }
    entries = {item.entry for item in layout.code_regions}
    for hook in layout.hooks:
        if (
            hook.address % 4
            or hook.width != 4
            or hook.replacement not in entries
            or not hook.purpose
        ):
            raise ValueError(f"{hook.key}: hook contract differs")
        if (
            layout.variant == "combined-mailbox26"
            and (hook.address, hook.stock, hook.replacement)
            != canonical_hooks[hook.key]
        ):
            raise ValueError(f"{hook.key}: canonical hook binding differs")

    ram = layout.ram
    if not ram.proven_free.contains(ram.reservation):
        raise ValueError("telemetry RAM lies outside the proven free range")
    if ram.lower_runtime_end > ram.reservation.start:
        raise ValueError("telemetry RAM overlaps the lower runtime")
    if (
        ram.active.start != ram.reservation.start
        or ram.active.end != ram.future.start
        or ram.future.end != ram.reservation.end
        or ram.active.size != 0x100
        or ram.future.size != 0x100
    ):
        raise ValueError("telemetry RAM budget differs")
    if (
        layout.variant == "combined-mailbox26"
        and (
            ram.reservation.start != 0xFFFF5E00
            or ram.reservation.end != 0xFFFF6000
        )
    ):
        raise ValueError("canonical telemetry RAM reservation differs")
    partitions = (ram.state, ram.bank_a, ram.bank_b, ram.event, ram.active_reserved)
    if partitions[0].start != ram.active.start or partitions[-1].end != ram.active.end:
        raise ValueError("active RAM partition boundaries differ")
    for left, right in zip(partitions, partitions[1:]):
        if left.end != right.start:
            raise ValueError("active RAM partitions are not contiguous")
    if tuple(item.size for item in partitions) != (32, 88, 88, 16, 32):
        raise ValueError("active RAM partition sizes differ")

    if layout.variant == "combined-mailbox26":
        profile = can_telemetry_profile.load_manifest()
        if (
            profile.table_address
            != layout.assembly_unit_by_key["tables"].span.start
            or profile.table_end
            != layout.assembly_unit_by_key["tables"].span.end
            or profile.configuration_address != layout.configuration.start
            or profile.state_address != ram.state.start
        ):
            raise ValueError("wire profile addresses differ from the layout")


def validate_base_composition(layout, data):
    data = bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    if digest != layout.base_composition_sha256:
        raise ValueError(
            f"base Rolling Launch composition SHA-256 is {digest}, expected {layout.base_composition_sha256}"
        )
    for unit in layout.assembly_units:
        if data[unit.span.start : unit.span.end] != bytes([0xFF]) * unit.span.size:
            raise ValueError(f"{unit.key}: base telemetry ROM is not erased")
    if data[layout.configuration.start : layout.configuration.end] != bytes([0xFF]) * layout.configuration.size:
        raise ValueError("base telemetry configuration is not erased")
    if data[layout.reserved_rom.start : layout.reserved_rom.end] != bytes([0xFF]) * layout.reserved_rom.size:
        raise ValueError("base telemetry reserve is not erased")
    for hook in layout.hooks:
        actual = int.from_bytes(data[hook.address : hook.address + hook.width], layout.byte_order)
        if actual != hook.stock:
            raise ValueError(f"{hook.key}: base hook value is {actual:#x}")
    actual_record = int.from_bytes(data[layout.mailbox_record_address : layout.mailbox_record_address + 4], layout.byte_order)
    if actual_record != layout.mailbox_record_stock:
        raise ValueError("base telemetry mailbox record differs")
    return data


def validate_assembled_blob(unit, blob):
    return common.validate_assembled_blob(unit, blob)


if __name__ == "__main__":
    item = load_layout()
    print(
        "status=PASS"
        f" rom={item.rom}"
        f" instructions={item.assembled_instruction_count}"
        f" data_bytes={item.assembled_data_bytes}"
        f" rom_budget={item.owned_rom.size}"
        f" ram_budget={item.ram.reservation.size}"
    )
