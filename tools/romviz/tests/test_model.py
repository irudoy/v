import json
from pathlib import Path

import pytest

from tools.romviz import build
from tools.romviz import model


REGISTERED_ROMS = (
    "1ND0A",
    "1ND3B",
    "JK00A",
    "JK00C",
    "JK00D",
    "JK03A",
    "JK03B",
    "JK08A",
    "JK78C",
)


def test_dimension_contract():
    assert model._dimension("1D-16") == (16, 1)
    assert model._dimension("4x3") == (4, 3)
    with pytest.raises(model.ModelError, match="unsupported map dimension"):
        model._dimension("16 by 16")


def test_all_selection_covers_every_registered_flash_rom():
    assert model.registered_roms() == REGISTERED_ROMS
    assert tuple(path.stem for path in model.registered_manifests()) == REGISTERED_ROMS
    assert tuple(
        Path(value).stem for value in model.expand_manifest_values([])
    ) == REGISTERED_ROMS
    assert tuple(
        Path(value).stem for value in model.expand_manifest_values(["all"])
    ) == REGISTERED_ROMS
    with pytest.raises(model.ModelError, match="cannot be combined"):
        model.expand_manifest_values(["all", "JK08A"])


def test_all_models_build_with_exact_registered_identities():
    atlas = model.build_atlas(["all"])
    by_id = {rom["id"]: rom for rom in atlas["roms"]}

    assert tuple(by_id) == REGISTERED_ROMS
    assert by_id["1ND0A"]["size"] == 0x180000
    assert by_id["1ND3B"]["size"] == 0x180000
    assert all(
        by_id[rom]["size"] == 0x100000
        for rom in set(REGISTERED_ROMS) - {"1ND0A", "1ND3B"}
    )
    assert by_id["JK78C"]["warnings"]
    assert by_id["JK78C"]["reviewedFunctions"] == 0
    assert by_id["JK78C"]["structuralFunctions"] == 2969
    for rom_id in ("JK78C", "1ND0A", "1ND3B"):
        assert by_id[rom_id]["counts"]["maps"] == 108


def test_jk78c_model_includes_target_runtime_and_checksum_evidence():
    rom = model.build_rom_model(model.resolve_manifest("JK78C"))
    by_id = {item["id"]: item for item in rom["objects"]}

    assert rom["metadata"]["ECU ID"] == "1JK78C"
    assert rom["metadata"]["MCU"] == "SH7058"
    assert any(
        item["label"] == "Map 1 - Fuel Compensation - Main - Bank 1"
        and item["start"] == 0x09EBA
        for item in rom["objects"]
    )
    assert any(
        item["label"] == "Map 1 - Engine Speed Limit - Fuel Cut Caps"
        and item["start"] == 0x09040
        for item in rom["objects"]
    )
    assert any(
        item["label"] == "Map 1 - Engine Speed Limit - Fuel Cut Curves"
        and item["start"] == 0x16BF4
        for item in rom["objects"]
    )
    assert any(
        item["label"] == "Rolling Launch Minimum Engine Speed"
        and item["start"] == 0x1E96A
        for item in rom["objects"]
    )
    runtime = by_id[
        "patch:runtime-address-profile:patch-claim:injected-rom"
    ]
    assert runtime["patchStatus"] == "composed"
    assert runtime["start"] == 0x0001CB08
    assert runtime["end"] == 0x00020000
    assert "patch:runtime-address-profile:patch-hook:map-selector_host_call" in by_id
    assert (
        "patch:runtime-address-profile:patch-hook:"
        "rolling-fuel_cut_coordinator"
    ) in by_id
    assert "patch:runtime-address-profile:patch-hook:can-hcan1_primary_init" in by_id
    assert "checksum-field:runtime_b_xor" in by_id
    assert "checksum-domain:runtime_b" in by_id
    assert "function:0006af76" in by_id
    assert not any("checksum layout" in warning for warning in rom["warnings"])
    assert not any("runtime address profile" in warning for warning in rom["warnings"])


def test_jk08a_model_covers_reviewed_sources_and_composed_patches():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))

    assert rom["size"] == 0x100000
    assert rom["reviewedFunctions"] == 589
    assert rom["structuralFunctions"] >= rom["reviewedFunctions"]
    assert rom["counts"]["maps"] == 512
    assert rom["counts"]["axes"] == 76

    by_id = {item["id"]: item for item in rom["objects"]}
    assert by_id["definition-switch:0:00008725"]["label"] == "Developer Immobilizer"
    assert by_id["patch:map-switching:patch-code:selector_host"]["start"] == 0xD2108
    assert by_id[
        "custom-map:map-switching:exhaust_cvtc_target:map-2"
    ]["start"] == 0xD2D00
    assert by_id[
        "custom-map:map-switching:exhaust_cvtc_target:map-2"
    ]["layer"] == "maps"
    assert by_id["patch:rolling-launch:patch-code:engine"]["end"] == 0xD3EA0
    assert by_id["checksum-field:sum16_a"]["start"] == 0x8200


def test_jk08a_object_ids_and_ranges_are_valid():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))
    ids = [item["id"] for item in rom["objects"]]

    assert len(ids) == len(set(ids))
    assert all(0 <= item["start"] < item["end"] <= rom["size"] for item in rom["objects"])
    assert all(item["layer"] in {entry[0] for entry in model.LAYERS} for item in rom["objects"])


@pytest.mark.parametrize("rom_id", ("1ND0A", "1ND3B"))
def test_1nd_models_include_definition_identity_and_all_checksum_fields(rom_id):
    rom = model.build_rom_model(model.resolve_manifest(rom_id))
    maf_factor = next(
        item
        for item in rom["objects"]
        if item["label"] == "MAF Factor"
    )
    checksum_fields = {
        item["id"]
        for item in rom["objects"]
        if item["kind"] == "checksum-field"
    }
    checksum_domains = {
        item["id"]
        for item in rom["objects"]
        if item["kind"] == "checksum-domain"
    }

    assert rom["metadata"]["ECU ID"] == f"1{rom_id}"
    assert rom["metadata"]["MCU"] == "SH7059"
    assert rom["counts"]["maps"] == 108
    assert maf_factor["start"] == 0x08939
    assert maf_factor["source"] == f"defs/{rom_id}.xml"
    assert any(
        item["label"] == "Map 1 - Engine Speed Limit - Fuel Cut Caps"
        and item["start"] == 0x091D2
        for item in rom["objects"]
    )
    assert any(
        item["label"] == "Map 1 - Engine Speed Limit - Fuel Cut Curves"
        and item["start"] == 0x17202
        for item in rom["objects"]
    )
    assert any(
        item["label"] == "Rolling Launch Minimum Engine Speed"
        and item["start"] == 0x133F6A
        for item in rom["objects"]
    )
    by_id = {item["id"]: item for item in rom["objects"]}
    profile = by_id[
        "patch:runtime-address-profile:patch-claim:injected-rom"
    ]
    assert profile["patchStatus"] == "composed"
    assert profile["start"] == 0x132108
    assert profile["end"] == 0x136000
    assert "definition-switch:0:00134e03" in by_id
    assert any(
        item["id"].startswith(
            "patch:runtime-address-profile:patch-hook:map-"
        )
        for item in rom["objects"]
    )
    assert any(
        item["id"].startswith(
            "patch:runtime-address-profile:patch-hook:can-"
        )
        for item in rom["objects"]
    )
    assert (
        "patch:runtime-address-profile:patch-hook:"
        "rolling-fuel_cut_coordinator"
    ) in by_id
    assert checksum_fields == {
        "checksum-field:sum16_a",
        "checksum-field:sum16_b",
        "checksum-field:boot_sum16",
        "checksum-field:vector_sum16",
        "checksum-field:runtime_a_sum",
        "checksum-field:runtime_a_xor",
    }
    assert checksum_domains == {
        "checksum-domain:sum16_a",
        "checksum-domain:sum16_b",
        "checksum-domain:boot_sum16",
        "checksum-domain:vector_sum16",
        "checksum-domain:runtime_a",
    }


def test_exact_family_materializes_only_explicit_target_tokens():
    rom = model.build_rom_model(model.resolve_manifest("JK00A"))
    switch = next(
        item
        for item in rom["objects"]
        if item["label"] == "Developer Immobilizer"
    )

    assert rom["metadata"]["ECU ID"] == "1JK00A"
    assert "Exact JK00A only." in switch["description"]
    assert switch["source"] == "defs/JK08A.overrides.toml"


@pytest.mark.parametrize(
    ("rom_id", "address"),
    (("JK00C", 0x0B7BE), ("JK00D", 0x0B7CE)),
)
def test_relocated_definitions_use_target_map_addresses(rom_id, address):
    rom = model.build_rom_model(model.resolve_manifest(rom_id))
    exhaust = next(
        item
        for item in rom["objects"]
        if item["label"] == "Map 1 - Exhaust CVTC Target - Main - Bank 1"
    )
    profile = next(
        item
        for item in rom["objects"]
        if item["id"]
        == "patch:runtime-address-profile:patch-claim:injected-rom"
    )

    assert exhaust["start"] == address
    assert exhaust["source"] == f"defs/{rom_id}.xml"
    assert profile["patchStatus"] == "composed"
    assert profile["label"] == "Unified production runtime profile composed allocation"
    assert profile["description"] == (
        "Exact target allocation emitted by the current production builder."
    )
    assert any(item["id"] == "checksum-field:sum16_a" for item in rom["objects"])


def test_map_and_axis_extents_are_derived_from_geometry():
    rom = model.build_rom_model(model.resolve_manifest("JK08A"))
    by_id = {item["id"]: item for item in rom["objects"]}

    exhaust_cvtc_target = by_id["map:0000b33a"]
    assert (
        exhaust_cvtc_target["end"] - exhaust_cvtc_target["start"]
        == 16 * 16
    )

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
