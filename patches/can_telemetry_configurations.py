#!/usr/bin/env python3
"""Load the host-defined configurations of the dynamic telemetry page and
render their ROM-neutral schema entries and their JK08A command frames."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import sys
import tomllib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import rolling_launch
from tools.logs import can_telemetry_schema


DEFAULT_SOURCE = Path(__file__).with_name("can-telemetry-configurations.toml")
DEFAULT_FRAMES = Path(__file__).with_name("can-telemetry-configurations.json")
ROLLING_LAUNCH_LAYOUT = Path(__file__).with_name("rolling-launch-layout.toml")
# The on-chip RAM of the SH7058 that the slot check of JK08A admits: the
# literals telemetry_dynamic_window_start and _end of can-telemetry-capture.s
# above the fixed high byte 0xFF of a slot address.
RAM_WINDOW = (0xFFFF0000, 0xFFFFC000)
SLOT_WIDTHS = (1, 2, 4)
OPCODE_DEFAULT = 0xC0
OPCODE_SET = 0xC1
OPCODE_COMMIT = 0xC2
MAXIMUM_ID = 0x7F
MAXIMUM_GROUPS = 2
SLOT_KEYS = {"name", "width", "signed", "scale", "source", "dashboard"}
CONFIGURATION_KEYS = {"id", "name", "label", "status", "groups"}
# A current configuration has command frames; a historical one keeps its
# schema entry so that a recorded trace decodes.
STATUSES = ("current", "historical")
STATE_FORMATS = {"B": (1, False), "H": (2, False), "h": (2, True), "I": (4, False)}


@dataclass(frozen=True)
class Slot:
    name: str
    width: int
    signed: bool
    scale: str
    address: int
    # Where the address comes from: a Rolling Launch view or ECU RAM.
    origin: str
    dashboard: dict


@dataclass(frozen=True)
class Configuration:
    configuration_id: int
    name: str
    label: str
    status: str
    groups: tuple[tuple[str, ...], ...]


@dataclass(frozen=True)
class Catalog:
    profile: str
    rom: str
    slots: dict
    configurations: tuple[Configuration, ...]

    def group_slots(self, configuration):
        return tuple(
            tuple(self.slots[name] for name in group)
            for group in configuration.groups
        )


def _require(table, keys, context):
    if not isinstance(table, dict) or set(table) != set(keys):
        raise ValueError(f"{context}: expected exactly the keys {sorted(keys)}")


def _layout_sources(path=ROLLING_LAUNCH_LAYOUT):
    """The Rolling Launch views by name and the addresses and formats of the
    fields of the runtime state record and its extension by name in the
    JK08A layout."""
    with Path(path).open("rb") as source:
        layout = tomllib.load(source)
    ram = layout["ram"]
    state = {}
    for start, rows in (
        (ram["state_start"], rolling_launch.STATE_FIELDS["base"]),
        (ram["extension_start"], rolling_launch.STATE_FIELDS["extension"]),
    ):
        for name, offset, fmt in rows:
            state[name] = (start + offset, fmt)
    return {row["name"]: row for row in layout["diagnostic"]}, state


def _slot_address(source, width, signed, context, sources):
    """Return (address, origin) of the JK08A source of a slot."""
    diagnostics, state = sources
    if not isinstance(source, dict):
        raise ValueError(f"{context}: source must be a table")
    if set(source) == {"rolling_launch_state"}:
        name = source["rolling_launch_state"]
        if name not in state:
            raise ValueError(f"{context}: no Rolling Launch state field {name!r}")
        address, fmt = state[name]
        if STATE_FORMATS[fmt] != (width, signed):
            raise ValueError(f"{context}: the width or signedness differs from the state field")
        return address, f"rolling_launch_state.{name}"
    if set(source) in ({"rolling_launch"}, {"rolling_launch", "byte"}):
        view = diagnostics.get(source["rolling_launch"])
        byte = source.get("byte", 0)
        if view is None:
            raise ValueError(f"{context}: no Rolling Launch view {source['rolling_launch']!r}")
        if type(byte) is not int or not 0 <= byte or byte + width > view["width"]:
            raise ValueError(f"{context}: the slot lies outside its Rolling Launch view")
        return view["target"] + byte, f"rolling_launch.{view['name']}"
    if set(source) == {"ecu_ram", "specification"}:
        specification = source["specification"]
        if type(source["ecu_ram"]) is not int or not (ROOT / specification).is_file():
            raise ValueError(f"{context}: ECU RAM needs an address and a specification")
        return source["ecu_ram"], f"ecu_ram ({specification})"
    raise ValueError(f"{context}: source names no Rolling Launch view, state field or ECU RAM")


def load_catalog(path=DEFAULT_SOURCE, layout_path=ROLLING_LAUNCH_LAYOUT):
    """Load and validate the catalog: unique slots that fit the RAM window
    at their alignment, and current or historical configuration IDs 1..127
    with one or two groups of one to six slots that fit six bytes."""
    with Path(path).open("rb") as source:
        raw = tomllib.load(source)
    _require(raw, {"schema_version", "profile", "rom", "configuration", "slot"}, "catalog")
    if raw["schema_version"] != 1 or raw["rom"] != "JK08A":
        raise ValueError("catalog: schema_version 1 of JK08A is supported")
    sources = _layout_sources(layout_path)
    slots = {}
    for index, row in enumerate(raw["slot"]):
        context = f"slot[{index}]"
        _require(row, SLOT_KEYS, context)
        name, width = row["name"], row["width"]
        if not isinstance(name, str) or not name or name in slots:
            raise ValueError(f"{context}: missing or repeated name")
        if width not in SLOT_WIDTHS or type(row["signed"]) is not bool:
            raise ValueError(f"{context}: width must be 1, 2 or 4 with a signedness")
        address, origin = _slot_address(row["source"], width, row["signed"], context, sources)
        if address % width or not RAM_WINDOW[0] <= address <= RAM_WINDOW[1] - width:
            raise ValueError(f"{context}: 0x{address:08X} is unaligned or outside the RAM window")
        slots[name] = Slot(name, width, row["signed"], row["scale"], address, origin,
                           row["dashboard"])
    configurations = []
    for index, row in enumerate(raw["configuration"]):
        context = f"configuration[{index}]"
        _require(row, CONFIGURATION_KEYS, context)
        groups = row["groups"]
        if type(row["id"]) is not int or not 1 <= row["id"] <= MAXIMUM_ID:
            raise ValueError(f"{context}: ID must be in 1..{MAXIMUM_ID}")
        if row["status"] not in STATUSES:
            raise ValueError(f"{context}: status must be one of {', '.join(STATUSES)}")
        if not isinstance(groups, list) or not 1 <= len(groups) <= MAXIMUM_GROUPS:
            raise ValueError(f"{context}: one or two groups")
        for group in groups:
            if not isinstance(group, list) or not 1 <= len(group) <= 6:
                raise ValueError(f"{context}: a group holds one to six slots")
            if any(name not in slots for name in group) or len(set(group)) != len(group):
                raise ValueError(f"{context}: a group names an unknown or repeated slot")
            if sum(slots[name].width for name in group) > 6:
                raise ValueError(f"{context}: a group exceeds six bytes")
        configurations.append(Configuration(
            row["id"], row["name"], row["label"], row["status"],
            tuple(tuple(group) for group in groups),
        ))
    for key in ("configuration_id", "name", "label"):
        values = [getattr(item, key) for item in configurations]
        if len(set(values)) != len(values):
            raise ValueError(f"catalog: configurations repeat a {key}")
    used = {name for item in configurations for group in item.groups for name in group}
    if used != set(slots):
        raise ValueError(f"catalog: unused slots {sorted(set(slots) - used)}")
    return Catalog(raw["profile"], raw["rom"], slots, tuple(configurations))


def slot_field(slot):
    """The host contract of a slot: the field contract of a context field."""
    try:
        terms = can_telemetry_schema.scale_terms(slot.scale)
    except ValueError as error:
        raise ValueError(f"{slot.name}: {error}") from error
    return {
        "name": slot.name,
        "width": slot.width,
        "signed": slot.signed,
        "scale": slot.scale,
        **terms,
        "dashboard": slot.dashboard,
    }


def schema_entries(catalog):
    """The ROM-neutral schema keys of the catalog profile: the slot fields
    and the configurations with their groups of slot names."""
    return {
        "dynamic_fields": [slot_field(slot) for slot in catalog.slots.values()],
        "configurations": [
            {
                "id": item.configuration_id,
                "name": item.name,
                "label": item.label,
                "groups": [list(group) for group in item.groups],
            }
            for item in catalog.configurations
        ],
    }


def command(opcode, *data):
    """One control frame: the opcode, five data bytes and their CRC."""
    body = bytes((opcode, *data, *(0,) * (5 - len(data))))
    return body + can_telemetry_schema.crc16_ccitt_false(body).to_bytes(2, "big")


def configuration_frames(catalog, configuration):
    """SET for every slot of every group, then COMMIT."""
    frames = []
    groups = catalog.group_slots(configuration)
    for group_index, group in enumerate(groups):
        for slot_index, slot in enumerate(group):
            descriptor = group_index << 7 | slot_index << 4 | slot.width
            address = (slot.address & 0x00FFFFFF).to_bytes(3, "big")
            frames.append(command(
                OPCODE_SET, configuration.configuration_id, descriptor, *address
            ))
    counts = [len(group) for group in groups] + [0] * (MAXIMUM_GROUPS - len(groups))
    frames.append(command(
        OPCODE_COMMIT, configuration.configuration_id, len(groups), *counts
    ))
    return frames


def render_frames(catalog):
    """The JK08A slot addresses and command frames of every current
    configuration."""
    document = {
        "schema_version": 1,
        "rom": catalog.rom,
        "profile": catalog.profile,
        "can_id": can_telemetry_schema.CONTROL_CAN_ID_EXPRESSION,
        "default": command(OPCODE_DEFAULT).hex().upper(),
        "configurations": [
            {
                "id": item.configuration_id,
                "name": item.name,
                "slots": [
                    {
                        "group": group_index,
                        "slot": slot_index,
                        "name": slot.name,
                        "address": f"0x{slot.address:08X}",
                        "width": slot.width,
                        "source": slot.origin,
                    }
                    for group_index, group in enumerate(catalog.group_slots(item))
                    for slot_index, slot in enumerate(group)
                ],
                "frames": [
                    frame.hex().upper() for frame in configuration_frames(catalog, item)
                ],
            }
            for item in catalog.configurations
            if item.status == "current"
        ],
    }
    return json.dumps(document, indent=2, sort_keys=True) + "\n"
