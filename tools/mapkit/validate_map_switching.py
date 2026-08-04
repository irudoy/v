#!/usr/bin/env python3
"""Validate map-switching models against the common JK08A definitions."""

from pathlib import Path
import sys
import tomllib
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patches import map_switching_layout
from tools.mapkit import emit_def, tunerpro


def validate():
    layout = map_switching_layout.load_layout()
    image = map_switching_layout.validate_image(layout)
    overrides_path = ROOT / "defs" / f"{layout.rom}.overrides.toml"
    with overrides_path.open("rb") as source:
        overrides = tomllib.load(source)
    maps, axes = emit_def.fetch(layout.rom)
    canonical_map_count = len(maps)
    maps, overrides, projection = emit_def.apply_definition_projections(
        layout.rom, maps, overrides
    )
    if projection is None:
        raise ValueError("common JK08A definition disables map switching")

    default_emit = emit_def.presentation_default_emit(
        projection.overrides
    )
    calibrations = []
    for address, calibration in sorted(projection.maps.items()):
        presentation = projection.overrides.get("table", {}).get(
            address, {}
        )
        if not emit_def.table_emit_enabled(
            presentation, default_emit, address
        ):
            continue
        why = emit_def.emittable(calibration, axes, presentation)
        if why:
            raise ValueError(
                f"projected table {address} fails emission gate: {why}"
            )
        calibrations.append(calibration)

    emitted = {
        calibration["addr"]: calibration
        for calibration in calibrations
    }
    view_entries, views_by_source = emit_def.masked_views(
        projection.overrides, emitted
    )
    romraider_fragments = []
    for calibration in calibrations:
        romraider_fragments.extend(
            emit_def.table_xml(
                calibration,
                projection.overrides,
                axes,
                layout.rom,
            )
        )
        for view in views_by_source.get(calibration["addr"], []):
            romraider_fragments.extend(
                emit_def.masked_view_xml(
                    calibration,
                    view,
                    projection.overrides,
                    axes,
                    layout.rom,
                )
            )
    romraider_model = "\n".join(romraider_fragments)

    native_switches = projection.overrides.get("switch", [])
    if isinstance(native_switches, dict):
        native_switches = [native_switches]
    records = emit_def.dtc_records(layout.rom, image=image)
    xdf, xdf_stats = tunerpro.render(
        layout.rom,
        image,
        calibrations,
        axes,
        projection.overrides,
        views_by_source,
        records,
        native_switches,
    )
    ET.fromstring(xdf)

    materialized = map_switching_layout.materialize_calibration_copies(
        layout, image
    )
    for family in layout.families:
        source = materialized[
            family.canonical_address :
            family.canonical_address + family.byte_length
        ]
        for address in family.all_slot_addresses:
            if (
                materialized[address : address + family.byte_length]
                != source
            ):
                raise ValueError(
                    f"{family.key}: slot at {address:#x} differs from map 1"
                )

    if 'name="Map 5 - Fuel Targets"' not in romraider_model:
        raise ValueError("RomRaider projection lacks Map 5 Fuel Targets")
    if 'category="Fuelling / Fuel Targets"' not in romraider_model:
        raise ValueError("RomRaider projection lacks the canonical fuel group")
    if "Map Switching /" in romraider_model:
        raise ValueError(
            "RomRaider projection creates a separate map-switching group"
        )
    if "Map 5 - Fuel Targets" not in xdf:
        raise ValueError("TunerPro projection lacks Map 5 Fuel Targets")
    if projection.slot_editor_view_count != 60:
        raise ValueError(
            "runtime does not expose 60 slot-specific editor views"
        )

    xml_path = ROOT / "defs" / f"{layout.rom}.xml"
    xdf_path = ROOT / "defs" / f"{layout.rom}.xdf"
    xml_text = xml_path.read_text(encoding="utf-8")
    xdf_text = xdf_path.read_text(encoding="utf-8")
    if "JK08A-MS5" in xml_text or "JK08A-MS5" in xdf_text:
        raise ValueError("common definitions contain a separate MS5 identity")
    xml_root = ET.fromstring(xml_text)
    xml_id = xml_root.findtext("./rom/romid/xmlid")
    if xml_id != layout.rom:
        raise ValueError(
            f"common RomRaider identity is {xml_id!r}, expected {layout.rom}"
        )
    xml_tables = {
        (
            table.get("name"),
            table.get("storageaddress"),
            table.get("category"),
        )
        for table in xml_root.findall("./rom/table")
    }
    for family in layout.families:
        for slot, address in enumerate(family.all_slot_addresses, 1):
            key = f"{address:08x}"
            name = projection.overrides["table"][key]["name"]
            category = projection.overrides["table"][key]["category"]
            expected = (name, emit_def.hexa(address), category)
            if expected not in xml_tables:
                raise ValueError(
                    f"common RomRaider definition lacks {name} at "
                    f"{address:#x}"
                )
    if xdf_text != xdf:
        raise ValueError(
            "tracked common TunerPro definition differs from the projection"
        )

    return {
        "canonical_graph_maps": canonical_map_count,
        "projected_maps": len(maps),
        "calibration_tables": len(calibrations),
        "masked_views": len(view_entries),
        "slot_tables": projection.slot_table_count,
        "slot_masked_views": projection.slot_masked_view_count,
        "slot_editor_views": projection.slot_editor_view_count,
        "xdf_tables": xdf_stats["calibration_tables"],
        "xdf_masked_views": xdf_stats["masked_views"],
        "common_definition_files": 2,
    }


def main():
    stats = validate()
    print(
        "map-switching definition model: "
        + ", ".join(f"{key}={value}" for key, value in stats.items())
    )
    print("status=PASS; common XML/XDF matched; no ROM file was written")


if __name__ == "__main__":
    main()
