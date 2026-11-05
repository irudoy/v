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
from tools.mapkit import (
    definition_targets,
    emit_def,
    presentation as presentation_policy,
    tunerpro,
)


def validate():
    layout = map_switching_layout.load_layout()
    image = map_switching_layout.validate_image(layout)
    overrides_path = ROOT / "defs" / f"{layout.rom}.overrides.toml"
    with overrides_path.open("rb") as source:
        overrides = definition_targets.materialize_overrides(
            definition_targets.load_target(layout.rom),
            tomllib.load(source),
        )
    maps, axes = emit_def.fetch(layout.rom)
    canonical_map_count = len(maps)
    maps, overrides, projection = emit_def.apply_definition_projections(
        layout.rom, maps, overrides
    )
    if projection is None:
        raise ValueError("common JK08A definition disables map switching")
    if projection.map_switching is None:
        raise ValueError("common JK08A definition disables map switching")
    if projection.rolling_launch is None:
        raise ValueError("common JK08A definition disables Rolling Launch controls")

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
        why = emit_def.definition_failure(
            calibration, axes, presentation
        )
        if why:
            if presentation.get("emit") is True:
                raise ValueError(
                    f"explicitly visible projected table {address} "
                    f"fails definition gate: {why}"
                )
            continue
        calibrations.append(calibration)
    axes = emit_def.editor_axes(
        layout.rom, image, calibrations, axes, projection.overrides
    )

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
    native_bitwise_switches = emit_def.bitwise_switches(
        projection.overrides
    )
    for index, entry in enumerate(native_bitwise_switches, 1):
        romraider_fragments.extend(
            emit_def.bitwise_switch_xml(entry, index)
        )
    native_switches = projection.overrides.get("switch", [])
    if isinstance(native_switches, dict):
        native_switches = [native_switches]
    native_switches = emit_def.stock_state_first(native_switches, image)
    for index, entry in enumerate(native_switches, 1):
        romraider_fragments.extend(emit_def.switch_xml(entry, index))
    romraider_model = "\n".join(romraider_fragments)
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
        native_bitwise_switches,
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

    if 'name="Map 5 - Exhaust CVTC Target - Main"' not in romraider_model:
        raise ValueError("RomRaider projection lacks Map 5 exhaust CVTC target")
    if 'category="Variable Valve Timing//Exhaust Cam"' not in romraider_model:
        raise ValueError("RomRaider projection lacks the exhaust CVTC group")
    if "Map Switching//" in romraider_model:
        raise ValueError(
            "RomRaider projection creates a separate map-switching group"
        )
    if "Map 5 - Exhaust CVTC Target - Main" not in xdf:
        raise ValueError("TunerPro projection lacks Map 5 exhaust CVTC target")
    if projection.slot_editor_view_count != 70:
        raise ValueError(
            "runtime does not expose 70 slot-specific editor views"
        )
    launch = projection.rolling_launch
    if launch.enable_mask_address != "000d6224":
        raise ValueError("Rolling Launch enable mask address differs")
    if launch.pedal_requirement_address != "000d622e":
        raise ValueError("Rolling Launch pedal_requirement_address differs")
    expected_controls = {
        "coolant_min": ("Rolling Launch Minimum Coolant Temperature", 0xD6226),
        "min_speed": ("Rolling Launch Minimum Vehicle Speed", 0xD6228),
        "max_speed": ("Rolling Launch Maximum Vehicle Speed", 0xD622A),
        "min_rpm_native": ("Rolling Launch Minimum Engine Speed", 0xD622C),
        "window_width": ("Rolling Launch Speed Window Width", 0xD6232),
        "window_top": ("Rolling Launch Speed Window Top", 0xD6233),
        "u_rate_limit": ("Rolling Launch Torque Fraction Rate Limit", 0xD6234),
        "integrator_limit": ("Rolling Launch Integrator Limit", 0xD6238),
        "abort_above": ("Rolling Launch Abort Above Target", 0xD623A),
        "abort_below": ("Rolling Launch Abort Below Target", 0xD623B),
        "rpm_ceiling_offset_native": (
            "Rolling Launch RPM Ceiling Offset", 0xD623C,
        ),
        "speed_frame_age_limit": (
            "Rolling Launch Speed Frame Age Limit", 0xD6242,
        ),
        "rpm_ceiling_hysteresis_native": (
            "Rolling Launch RPM Ceiling Hysteresis", 0xD6243,
        ),
    }
    expected_controls.update({
        f"map_{index + 1}_{key}": (
            f"Rolling Launch Map {index + 1} {label}",
            0xD6248 + index * 6 + relative,
        )
        for index in range(5)
        for key, label, relative in (
            ("integral_gain", "Integral Gain", 0),
            ("max_trim", "Maximum Trim", 2),
            ("floor_command", "Timing Floor", 3),
        )
    })
    if dict(launch.control_addresses) != {
        key: f"{address:08x}" for key, (_name, address) in expected_controls.items()
    }:
        raise ValueError("Rolling Launch control addresses differ")
    if launch.masked_view_count != 0:
        raise ValueError("Rolling Launch still exposes masked table views")
    if launch.table_count != len(expected_controls) or launch.switch_count != 1:
        raise ValueError(
            "runtime does not expose one table per Rolling Launch control and "
            "one pedal switch"
        )
    if launch.bitwise_switch_count != 1 or launch.enable_bit_count != 5:
        raise ValueError(
            "runtime does not expose one five-bit map-enable switch"
        )
    for name, address in expected_controls.values():
        if (
            name not in romraider_model
            or f'storageaddress="0x{address:X}"' not in romraider_model
        ):
            raise ValueError(f"RomRaider projection lacks {name}")
        if name not in xdf or f'mmedaddress="0x{address:X}"' not in xdf:
            raise ValueError(f"TunerPro projection lacks {name}")
    if "Rolling Launch Require Accelerator Pedal" not in romraider_model:
        raise ValueError("RomRaider projection lacks the pedal switch")
    if 'storageaddress="0xD622E"' not in romraider_model:
        raise ValueError("RomRaider pedal-switch address differs")
    if "Rolling Launch Require Accelerator Pedal" not in xdf:
        raise ValueError("TunerPro projection lacks the pedal switch")
    if romraider_model.count('type="BitwiseSwitch"') != 1:
        raise ValueError("RomRaider projection lacks one bitwise switch")
    if romraider_model.count("<bit ") != 5:
        raise ValueError("RomRaider bitwise switch does not contain five bits")
    for slot in range(1, 6):
        if f"Map {slot} - Rolling Launch Enable" not in romraider_model:
            raise ValueError(
                f"RomRaider bitwise switch lacks Map {slot} enable"
            )
        if f"Map {slot} - Rolling Launch Enable" not in xdf:
            raise ValueError(
                f"TunerPro projection lacks Map {slot} Rolling Launch enable"
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
            expected = (
                name,
                emit_def.hexa(address),
                presentation_policy.romraider_category_name(category),
            )
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
        "rolling_launch_tables": projection.rolling_launch.table_count,
        "rolling_launch_switches": projection.rolling_launch.switch_count,
        "rolling_launch_bitwise_switches": (
            projection.rolling_launch.bitwise_switch_count
        ),
        "rolling_launch_enable_bits": projection.rolling_launch.enable_bit_count,
        "xdf_tables": xdf_stats["calibration_tables"],
        "xdf_masked_views": xdf_stats["masked_views"],
        "xdf_bitwise_flags": xdf_stats["bitwise_flags"],
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
