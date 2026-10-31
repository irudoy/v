import json
from pathlib import Path

import pytest

from tools.romviz import build
from tools.romviz import model


REGISTERED_ROMS = (
    "1ME3B",
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


@pytest.fixture(scope="module")
def architecture_cache():
    """Share a graph snapshot while each read-only test builds a fresh ROM model."""
    return {}


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


@pytest.mark.slow
def test_all_models_build_with_exact_registered_identities():
    atlas = model.build_atlas(["all"])
    by_id = {rom["id"]: rom for rom in atlas["roms"]}

    assert tuple(by_id) == REGISTERED_ROMS
    assert by_id["1ME3B"]["size"] == 0x180000
    assert by_id["1ND0A"]["size"] == 0x180000
    assert by_id["1ND3B"]["size"] == 0x180000
    assert all(
        by_id[rom]["size"] == 0x100000
        for rom in set(REGISTERED_ROMS) - {"1ME3B", "1ND0A", "1ND3B"}
    )
    assert by_id["JK78C"]["warnings"]
    assert by_id["JK78C"]["structuralFunctions"] > by_id["JK78C"]["reviewedFunctions"] > 0


def kb_expected(knowledge, rom):
    """Count the KB functions and the KB tables and axes that no definition publishes."""
    layout = rom["architecture"]["layout"]
    bound = {"fn": set(), "tbl": set(), "axis": set()}
    for meaning, symbols in knowledge.symbols.items():
        symbol = symbols.get(layout)
        if (symbol and symbol["kind"] in bound
                and knowledge.binding(meaning, layout, rom["id"])["symbol"]):
            bound[symbol["kind"]].add(symbol["address"])
    published = {
        kind: {item["start"] for item in rom["objects"] if item["kind"] == source}
        for kind, source in (("tbl", "definition-map"), ("axis", "definition-axis"))
    }
    return (len(bound["fn"]), len(bound["tbl"] - published["tbl"]),
            len(bound["axis"] - published["axis"]))


# One bound function and one hidden table of each layout without ledgers.
KB_ANCHORS = (
    ("JK78C", 0x42882, "dual_curve_word_converter", 0x13608, "timing_compositor_byte_multiplier"),
    ("1ND0A", 0x44C70, "base_fuel_schedule_producer", 0x085B0, "bfs_correction_gain"),
    ("1ND3B", 0x44C70, "base_fuel_schedule_producer", 0x085B0, "bfs_correction_gain"),
    ("1ME3B", 0x48298, "base_fuel_schedule_producer", 0x085B0, "bfs_correction_gain"),
    ("JK00C", 0x20E30, "coherent_snapshot", 0x094CE, "speed_limiter_filter_blend_gain_q10"),
    ("JK00D", 0x20E30, "coherent_snapshot", 0x094DC, "speed_limiter_filter_blend_gain_q10"),
)


@pytest.mark.slow
@pytest.mark.parametrize(("rom_id", "function", "function_name", "table", "table_name"),
                         KB_ANCHORS)
def test_ledgerless_models_carry_kb_functions_and_hidden_tables(
    rom_id, function, function_name, table, table_name, architecture_cache
):
    rom = model.build_rom_model(model.resolve_manifest(rom_id), architecture_cache)
    by_id = {item["id"]: item for item in rom["objects"]}

    reviewed = by_id[f"function:{function:08x}"]
    assert (reviewed["kind"], reviewed["label"]) == ("reviewed-function", function_name)
    assert reviewed["reviewed"] and "kb" in reviewed["tags"]
    assert reviewed["binding"]["meaning"] == f"{function_name}/fn"
    hidden = by_id[f"kb-map:{table:08x}"]
    assert hidden["label"] == table_name and "hidden" in hidden["tags"]
    assert hidden["binding"]["meaning"] == f"{table_name}/tbl"
    assert not any("Reviewed function annotations" in item for item in rom["warnings"])

    functions, tables, axes = kb_expected(architecture_cache["_knowledge"], rom)
    kinds = [item["kind"] for item in rom["objects"]]
    assert rom["reviewedFunctions"] == functions
    assert kinds.count("kb-map") == tables
    assert kinds.count("kb-axis") == axes
    assert rom["counts"]["maps"] == tables + sum(
        item["layer"] == "maps" and item["kind"] != "kb-map" for item in rom["objects"])
    assert rom["counts"]["axes"] == axes + sum(
        item["layer"] == "axes" and item["kind"] != "kb-axis" for item in rom["objects"])


@pytest.mark.slow
def test_1me3b_model_carries_definition_structure_and_checksum_layers(architecture_cache):
    """The Branch D image publishes its projection beside its own structure."""
    rom = model.build_rom_model(model.resolve_manifest("1ME3B"), architecture_cache)

    assert rom["size"] == 0x180000
    assert rom["metadata"]["ECU ID"] == "11ME3B"
    assert rom["metadata"]["Engine"] == "VQ37VHR"
    assert rom["metadata"]["MCU"] == "SH7059"
    assert rom["counts"]["diagnostics"] == 76
    assert rom["counts"]["integrity"] == 11
    assert {
        item["id"]
        for item in rom["objects"]
        if item["kind"] == "checksum-field"
    } == {
        "checksum-field:boot_sum16",
        "checksum-field:vector_sum16",
        "checksum-field:sum16_a",
        "checksum-field:sum16_b",
        "checksum-field:runtime_a_xor",
        "checksum-field:runtime_a_sum",
    }
    maf_factor = next(
        item for item in rom["objects"] if item["label"] == "MAF Factor"
    )
    assert maf_factor["start"] == 0x8965
    assert maf_factor["source"] == "defs/1ME3B.xml"
    immobilizer = next(
        item
        for item in rom["objects"]
        if item["label"] == "Developer Immobilizer"
    )
    assert immobilizer["start"] == 0x8671
    running_duration = next(
        item
        for item in rom["objects"]
        if item["label"] == "VVEL Duration Target - Running [stored count]"
    )
    assert running_duration["start"] == 0x17276
    assert running_duration["source"] == "defs/1ME3B.xml"
    assert all(
        item["source"].startswith("defs/1ME3B.dtc.csv:")
        for item in rom["objects"]
        if item["kind"] in {"dtc-record", "dtc-attribute"}
    )
    assert rom["structuralFunctions"] > rom["reviewedFunctions"] > 0
    assert not any(
        "checksum layout is not registered" in warning
        for warning in rom["warnings"]
    )
    by_id = {item["id"]: item for item in rom["objects"]}
    runtime = by_id[
        "patch:runtime-address-profile:patch-claim:injected-rom"
    ]
    assert runtime["patchStatus"] == "composed"
    assert runtime["start"] == 0x0013B108
    assert runtime["end"] == 0x0013F000
    assert "patch:runtime-address-profile:patch-hook:map-selector_host_call" in by_id
    assert (
        "patch:runtime-address-profile:patch-hook:map-ignition_state_lookup"
    ) in by_id
    assert (
        "patch:runtime-address-profile:patch-hook:"
        "rolling-fuel_cut_coordinator"
    ) in by_id
    assert "patch:runtime-address-profile:patch-hook:can-hcan1_primary_init" in by_id
    for address, stock in (
        (0x79404, 0x293D8),
        (0x79420, 0x29BA8),
        (0x796F4, 0x29BA8),
        (0x799A4, 0x29BA8),
    ):
        [hook] = [item for item in rom["objects"]
                  if item["id"].startswith("patch:runtime-address-profile:patch-hook:map-")
                  and item["start"] == address]
        assert hook["start"] == address and hook["end"] == address + 4
        metadata = {item["label"]: item["value"] for item in hook["meta"]}
        assert int(metadata["Stock"], 16) == stock
        assert runtime["start"] <= int(metadata["Replacement"], 16) < runtime["end"]
    assert any(
        item["label"] == "Rolling Launch Minimum Engine Speed"
        and item["start"] == 0x13CF6A
        for item in rom["objects"]
    )
    assert not any("runtime address profile" in warning for warning in rom["warnings"])


@pytest.mark.slow
@pytest.mark.parametrize("rom_id", REGISTERED_ROMS)
def test_every_registered_rom_carries_its_dtc_registry(rom_id, architecture_cache):
    """The DTC layer precedes analysis, so no target leaves it undeclared."""
    manifest = model._load_manifest(model.resolve_manifest(rom_id))
    registry = manifest["dtc"]
    rows = model._read_csv(model._repo_path(registry))
    rom = model.build_rom_model(model.resolve_manifest(rom_id), architecture_cache)
    by_id = {item["id"]: item for item in rom["objects"]}

    assert rows
    for row in rows:
        record = int(row["record_addr"], 16)
        attribute = int(row["attribute_addr"], 16)
        for kind, address in (("dtc-record", record), ("dtc-attribute", attribute)):
            item = by_id[f"{kind}:{row['index']}:{address:08x}"]
            assert item["layer"] == "diagnostics"
            assert item["source"] == f"{registry}:{row['_line']}"
            assert row["dtc"] in item["label"]


@pytest.mark.slow
def test_jk78c_model_includes_target_runtime_and_checksum_evidence(architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest("JK78C"), architecture_cache)
    by_id = {item["id"]: item for item in rom["objects"]}

    assert rom["metadata"]["ECU ID"] == "1JK78C"
    assert rom["metadata"]["MCU"] == "SH7058"
    assert any(
        item["label"] == "Map 1 - Fuel Compensation - Main - Default"
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
    # The census supplies the extent of a KB table without KB geometry.
    multiplier = by_id["kb-map:00013608"]
    assert (multiplier["end"] - multiplier["start"], multiplier["exactExtent"]) == (8, True)
    assert not any("checksum layout" in warning for warning in rom["warnings"])
    assert not any("runtime address profile" in warning for warning in rom["warnings"])


@pytest.mark.slow
def test_jk08a_model_covers_reviewed_sources_and_composed_patches(architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest("JK08A"), architecture_cache)

    assert rom["size"] == 0x100000
    assert rom["reviewedFunctions"] == 706
    assert rom["structuralFunctions"] >= rom["reviewedFunctions"]
    assert rom["counts"]["maps"] == 516
    assert rom["counts"]["axes"] == 79
    # Ledger annotations own the family; KB-only objects stay out of it.
    assert not any(item["kind"].startswith("kb-") for item in rom["objects"])

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


@pytest.mark.slow
def test_jk08a_object_ids_and_ranges_are_valid(architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest("JK08A"), architecture_cache)
    ids = [item["id"] for item in rom["objects"]]

    assert len(ids) == len(set(ids))
    assert all(0 <= item["start"] < item["end"] <= rom["size"] for item in rom["objects"])
    assert all(item["layer"] in {entry[0] for entry in model.LAYERS} for item in rom["objects"])


@pytest.mark.slow
@pytest.mark.parametrize("rom_id", ("1ND0A", "1ND3B"))
def test_1nd_models_include_definition_identity_and_all_checksum_fields(rom_id, architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest(rom_id), architecture_cache)
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


@pytest.mark.slow
def test_exact_family_materializes_only_explicit_target_tokens(architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest("JK00A"), architecture_cache)
    switch = next(
        item
        for item in rom["objects"]
        if item["label"] == "Developer Immobilizer"
    )

    assert rom["metadata"]["ECU ID"] == "1JK00A"
    assert "Exact JK00A only." in switch["description"]
    assert switch["source"] == "defs/JK08A.overrides.toml"


@pytest.mark.slow
@pytest.mark.parametrize(
    ("rom_id", "intake_address", "exhaust_address"),
    (("JK00C", 0x0B7BE, 0x0B6BE), ("JK00D", 0x0B7CE, 0x0B6CE)),
)
def test_relocated_definitions_use_target_map_addresses(
    rom_id, intake_address, exhaust_address, architecture_cache
):
    rom = model.build_rom_model(model.resolve_manifest(rom_id), architecture_cache)
    intake = next(
        item
        for item in rom["objects"]
        if item["label"] == "Map 1 - Intake CVTC Target - Main"
    )
    exhaust = next(
        item
        for item in rom["objects"]
        if item["label"] == "Map 1 - Exhaust CVTC Target - Main"
    )
    profile = next(
        item
        for item in rom["objects"]
        if item["id"]
        == "patch:runtime-address-profile:patch-claim:injected-rom"
    )

    assert intake["start"] == intake_address
    assert intake["source"] == f"defs/{rom_id}.xml"
    assert exhaust["start"] == exhaust_address
    assert exhaust["source"] == f"defs/{rom_id}.xml"
    assert profile["patchStatus"] == "composed"
    assert profile["label"] == "Unified production runtime profile composed allocation"
    assert profile["description"] == (
        "Exact target allocation emitted by the current production builder."
    )
    assert any(item["id"] == "checksum-field:sum16_a" for item in rom["objects"])


@pytest.mark.slow
def test_map_and_axis_extents_are_derived_from_geometry(architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest("JK08A"), architecture_cache)
    by_id = {item["id"]: item for item in rom["objects"]}

    exhaust_cvtc_target = by_id["map:0000b33a"]
    assert (
        exhaust_cvtc_target["end"] - exhaust_cvtc_target["start"]
        == 16 * 16
    )

    rpm_axis = by_id["axis:00012f3e"]
    assert rpm_axis["exactExtent"] is True
    assert rpm_axis["end"] - rpm_axis["start"] == 16


@pytest.mark.slow
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


@pytest.mark.slow
def test_telemetry_layout_is_labeled_composed(architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest("JK08A"), architecture_cache)
    telemetry = [item for item in rom["objects"] if item["patch"] == "can-telemetry"]
    assert telemetry
    assert {item["patchStatus"] for item in telemetry} == {"composed"}


@pytest.mark.slow
def test_custom_map_copies_remain_visible_as_patch_allocations_and_maps(architecture_cache):
    rom = model.build_rom_model(model.resolve_manifest("JK08A"), architecture_cache)
    custom_maps = [item for item in rom["objects"] if item["kind"] == "custom-map"]
    patch_copies = [item for item in rom["objects"] if item["kind"] == "patch-map-copy"]

    assert len(custom_maps) == 48
    assert len(patch_copies) == len(custom_maps)
    assert {item["patch"] for item in custom_maps} == {"map-switching"}
