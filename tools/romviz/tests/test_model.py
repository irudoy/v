import json

import pytest

from tools.romviz import build
from tools.romviz import model


def test_dimension_contract():
    assert model._dimension("1D-16") == (16, 1)
    assert model._dimension("4x3") == (4, 3)
    with pytest.raises(model.ModelError, match="unsupported map dimension"):
        model._dimension("16 by 16")


def test_jk08a_model_covers_reviewed_sources_and_composed_patches():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))

    assert rom["size"] == 0x100000
    assert rom["reviewedFunctions"] == 583
    assert rom["structuralFunctions"] >= rom["reviewedFunctions"]
    assert rom["counts"]["maps"] == 512
    assert rom["counts"]["axes"] == 76

    by_id = {item["id"]: item for item in rom["objects"]}
    assert by_id["definition-switch:0:00008725"]["label"] == "Developer Immobilizer"
    assert by_id["patch:map-switching:patch-code:selector_host"]["start"] == 0xD2108
    assert by_id["custom-map:map-switching:fuel_targets:map-2"]["start"] == 0xD2D00
    assert by_id["custom-map:map-switching:fuel_targets:map-2"]["layer"] == "maps"
    assert by_id["patch:rolling-launch:patch-code:engine"]["end"] == 0xD3EA0
    assert by_id["checksum-field:sum16_a"]["start"] == 0x8200


def test_jk08a_object_ids_and_ranges_are_valid():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))
    ids = [item["id"] for item in rom["objects"]]

    assert len(ids) == len(set(ids))
    assert all(0 <= item["start"] < item["end"] <= rom["size"] for item in rom["objects"])
    assert all(item["layer"] in {entry[0] for entry in model.LAYERS} for item in rom["objects"])


def test_map_and_axis_extents_are_derived_from_geometry():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))
    by_id = {item["id"]: item for item in rom["objects"]}

    fuel_targets = by_id["map:0000b33a"]
    assert fuel_targets["end"] - fuel_targets["start"] == 16 * 16

    rpm_axis = by_id["axis:00012f3e"]
    assert rpm_axis["exactExtent"] is True
    assert rpm_axis["end"] - rpm_axis["start"] == 16


def test_generated_document_is_self_contained(tmp_path):
    output = tmp_path / "atlas.html"
    written, atlas = build.write_atlas(["JK08A"], output)
    text = written.read_text(encoding="utf-8")

    assert written == output
    assert atlas["roms"][0]["id"] == "JK08A"
    assert "__ROMVIZ_DATA__" not in text
    assert "/*__ROMVIZ_CSS__*/" not in text
    assert "/*__ROMVIZ_JS__*/" not in text
    assert "<script id=\"romviz-data\" type=\"application/json\">" in text
    assert "fetch(" not in text

    start = text.index("<script id=\"romviz-data\" type=\"application/json\">")
    start = text.index(">", start) + 1
    end = text.index("</script>", start)
    payload = json.loads(text[start:end])
    assert payload["schemaVersion"] == 1
    assert payload["roms"][0]["objects"]


def test_telemetry_layout_is_labeled_composed():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))
    telemetry = [item for item in rom["objects"] if item["patch"] == "can-telemetry"]
    assert telemetry
    assert {item["patchStatus"] for item in telemetry} == {"composed"}


def test_custom_map_copies_remain_visible_as_patch_allocations_and_maps():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))
    custom_maps = [item for item in rom["objects"] if item["kind"] == "custom-map"]
    patch_copies = [item for item in rom["objects"] if item["kind"] == "patch-map-copy"]

    assert len(custom_maps) == 48
    assert len(patch_copies) == len(custom_maps)
    assert {item["patch"] for item in custom_maps} == {"map-switching"}
