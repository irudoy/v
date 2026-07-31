"""Common-definition projection for the JK08A five-slot map-switching pilot.

The input maps remain graph-backed canonical facts. This module clones only
their storage addresses and tuner presentation for the slot copies declared by
``patches/map-switching-layout.toml``. ``emit_def.py`` places the projection
inside the shared JK08A XML/XDF outputs. Slot numbers are added to table names;
each copy remains in the canonical functional category. This module does not
write artifacts.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass

from patches.map_switching_layout import Layout, load_layout


@dataclass(frozen=True)
class DefinitionProjection:
    maps: dict
    overrides: dict
    switchable_addresses: frozenset[str]
    slot_table_count: int
    slot_masked_view_count: int

    @property
    def slot_editor_view_count(self):
        return self.slot_table_count + self.slot_masked_view_count


def address_key(address):
    return f"{address:08x}"


def slot_name(slot, name):
    return f"Map {slot} - {name}"


def _masked_view_entries(overrides):
    entries = overrides.get("masked_view", [])
    if isinstance(entries, dict):
        entries = [entries]
    if not isinstance(entries, list):
        raise ValueError("masked_view must be a table or an array of tables")
    return entries


def _validate_family_model(family, calibration, presentation):
    if calibration.get("addr") != address_key(family.canonical_address):
        raise ValueError(f"{family.key}: canonical map address differs")
    if calibration.get("storagetype") != family.storage_type:
        raise ValueError(f"{family.key}: storage type differs from the manifest")
    width = calibration.get("width")
    height = calibration.get("height") or 1
    if width != family.width or height != family.height:
        raise ValueError(
            f"{family.key}: graph geometry {width}x{height} differs from "
            f"manifest geometry {family.width}x{family.height}"
        )
    if not presentation.get("name") or not presentation.get("category"):
        raise ValueError(
            f"{family.key}: canonical presentation needs name and category"
        )
    if not presentation.get("emit", False):
        raise ValueError(
            f"{family.key}: canonical table is not enabled for definitions"
        )


def project_definition_model(maps, overrides, layout: Layout | None = None):
    """Project canonical maps and presentation into five storage slots.

    Global maps, axes, switches, checksum declarations, and ROM identification
    remain unchanged. The shared JK08A identity intentionally covers stock and
    project map-switching images with the same exact ROM layout.
    """
    layout = layout or load_layout()
    projected_maps = deepcopy(maps)
    projected_overrides = deepcopy(overrides)
    table_overrides = projected_overrides.get("table")
    if not isinstance(table_overrides, dict):
        raise ValueError("definition overrides must contain a table mapping")

    canonical_to_family = {
        address_key(family.canonical_address): family
        for family in layout.families
    }
    switchable_addresses = {
        address_key(address)
        for family in layout.families
        for address in family.all_slot_addresses
    }
    canonical_addresses = set(canonical_to_family)
    copy_addresses = switchable_addresses - canonical_addresses
    collisions = copy_addresses & set(projected_maps)
    if collisions:
        raise ValueError(
            "slot storage collides with canonical graph maps: "
            + ", ".join(sorted(collisions))
        )

    for canonical, family in canonical_to_family.items():
        calibration = maps.get(canonical)
        presentation = overrides.get("table", {}).get(canonical)
        if calibration is None:
            raise ValueError(f"{family.key}: canonical map is absent")
        if presentation is None:
            raise ValueError(f"{family.key}: presentation override is absent")
        _validate_family_model(family, calibration, presentation)

        for slot, address in enumerate(family.all_slot_addresses, 1):
            target = address_key(address)
            projected = deepcopy(calibration)
            projected["addr"] = target
            projected["map_switching_source"] = canonical
            projected["map_switching_slot"] = slot
            projected_maps[target] = projected

            slot_presentation = deepcopy(presentation)
            slot_presentation["name"] = slot_name(
                slot, presentation["name"]
            )
            slot_presentation["category"] = presentation["category"]
            slot_presentation["emit"] = True
            slot_presentation["order"] = (
                slot * 100000 + presentation.get("order", 0)
            )
            table_overrides[target] = slot_presentation

    projected_views = []
    slot_masked_view_count = 0
    for view in _masked_view_entries(overrides):
        source = str(view.get("source", "")).lower()
        family = canonical_to_family.get(source)
        if family is None:
            projected_views.append(deepcopy(view))
            continue
        for slot, address in enumerate(family.all_slot_addresses, 1):
            projected_view = deepcopy(view)
            projected_view["source"] = address_key(address)
            projected_view["name"] = slot_name(slot, view["name"])
            projected_view["category"] = view["category"]
            projected_views.append(projected_view)
            slot_masked_view_count += 1
    if projected_views:
        projected_overrides["masked_view"] = projected_views
    elif "masked_view" in projected_overrides:
        projected_overrides["masked_view"] = []

    projection = DefinitionProjection(
        maps=projected_maps,
        overrides=projected_overrides,
        switchable_addresses=frozenset(switchable_addresses),
        slot_table_count=len(layout.families) * layout.slot_count,
        slot_masked_view_count=slot_masked_view_count,
    )
    validate_projection(projection, maps, overrides, layout)
    return projection


def validate_projection(projection, source_maps, source_overrides, layout=None):
    """Validate cardinality, addresses, and preservation of global objects."""
    layout = layout or load_layout()
    expected_addresses = {
        address_key(address)
        for family in layout.families
        for address in family.all_slot_addresses
    }
    if projection.switchable_addresses != expected_addresses:
        raise ValueError("definition projection address set differs from layout")
    if projection.slot_table_count != len(expected_addresses):
        raise ValueError("definition projection has the wrong slot table count")

    for address in expected_addresses:
        if address not in projection.maps:
            raise ValueError(f"projected map {address} is absent")
        if address not in projection.overrides["table"]:
            raise ValueError(f"projected presentation {address} is absent")

    canonical = {
        address_key(family.canonical_address)
        for family in layout.families
    }
    for address, calibration in source_maps.items():
        if address not in canonical:
            if projection.maps.get(address) != calibration:
                raise ValueError(f"global map {address} changed during projection")
    for address, presentation in source_overrides.get("table", {}).items():
        if address not in canonical:
            if projection.overrides["table"].get(address) != presentation:
                raise ValueError(
                    f"global presentation {address} changed during projection"
                )

    for family in layout.families:
        source = address_key(family.canonical_address)
        for slot, address in enumerate(family.all_slot_addresses, 1):
            target = address_key(address)
            calibration = projection.maps[target]
            presentation = projection.overrides["table"][target]
            if calibration["map_switching_source"] != source:
                raise ValueError(f"{target}: projection source differs")
            if calibration["map_switching_slot"] != slot:
                raise ValueError(f"{target}: projection slot differs")
            if not presentation["name"].startswith(f"Map {slot} - "):
                raise ValueError(f"{target}: slot is absent from table name")
            source_category = source_overrides["table"][source]["category"]
            if presentation["category"] != source_category:
                raise ValueError(
                    f"{target}: slot category differs from canonical table"
                )

    return projection
