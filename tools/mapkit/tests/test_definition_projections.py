import copy
from pathlib import Path
import tomllib

import pytest

from tools.mapkit import definition_projections
from tools.mapkit import rom as romkit


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
TARGETS = ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B")
SH7058_HR_UNSUPPORTED = {
    "000085d9",
    "00008fdc",
    "0000911c",
    "0000ab5a",
    "0000b43a",
    "0000b53a",
    "000124d2",
}
JK78C_UNSUPPORTED = {
    "0000934e",
    "0000ab5a",
    "0000b33a",
    "0000b43a",
    "0000b53a",
}
VQ37_UNSUPPORTED = JK78C_UNSUPPORTED


def test_registry_binds_relocated_targets_without_a_default():
    projections = definition_projections.load_registry()
    assert set(projections) == set(TARGETS)
    assert definition_projections.projection_for_rom("JK08A") is None
    for projection in projections.values():
        definition_projections.verify_image_binding(projection)
        assert projection.source == "JK08A"
    assert projections["JK00C"].unsupported_maps == SH7058_HR_UNSUPPORTED
    assert projections["JK00D"].unsupported_maps == SH7058_HR_UNSUPPORTED
    for rom in ("JK78C", "1ND0A", "1ND3B"):
        assert projections[rom].unsupported_maps == VQ37_UNSUPPORTED


def test_complete_registry_validation_covers_every_target_capability_set():
    stats = definition_projections.validate_registry()
    assert set(stats) == set(TARGETS)
    for rom in ("JK00C", "JK00D"):
        values = stats[rom]
        assert values["mapped"] > 0
        assert values["unsupported"] == len(SH7058_HR_UNSUPPORTED)
        assert values["checksum"] is True
        assert values["romraider_checksum"] is True
        assert values["map_families"] == 13
        assert values["rolling_configuration"] == 0xE0660
    assert stats["JK78C"]["mapped"] == 44
    assert stats["JK78C"]["unsupported"] == len(VQ37_UNSUPPORTED)
    assert stats["JK78C"]["checksum"] is False
    assert stats["JK78C"]["romraider_checksum"] is False
    assert stats["JK78C"]["map_families"] == 0
    assert stats["JK78C"]["rolling_configuration"] is None
    for rom in ("1ND0A", "1ND3B"):
        values = stats[rom]
        assert values["mapped"] == 44
        assert values["unsupported"] == len(VQ37_UNSUPPORTED)
        assert values["checksum"] is True
        assert values["romraider_checksum"] is False
        assert values["map_families"] == 12
        assert values["rolling_configuration"] is None


def test_exhaust_target_has_two_explicit_bank_variants():
    for rom in ("JK00C", "JK00D"):
        projection = definition_projections.projection_for_rom(rom)
        rows = [
            binding
            for binding in projection.bindings
            if binding.entity == "Map"
            and binding.source == "0000b33a"
        ]
        assert {row.variant for row in rows} == {"bank_1", "bank_2"}
        assert all(row.status == "reviewed-target" for row in rows)


def test_runtime_definition_layouts_use_target_allocation():
    for rom in ("JK00C", "JK00D"):
        projection = definition_projections.projection_for_rom(rom)
        maps = definition_projections.map_switching_definition_layout(projection)
        launch = definition_projections.rolling_launch_definition_layout(projection)

        assert maps.rom == rom
        assert maps.slot_count == 5
        assert len(maps.families) == 13
        assert {
            "exhaust_cvtc_target_even",
            "exhaust_cvtc_target_odd",
        } <= set(maps.family_by_key)
        assert launch.rom == rom
        assert launch.configuration.start == 0xE0660

    for rom in ("1ND0A", "1ND3B"):
        projection = definition_projections.projection_for_rom(rom)
        maps = definition_projections.map_switching_definition_layout(projection)

        assert maps.rom == rom
        assert maps.variant == "sh7059-1nd"
        assert maps.slot_count == 5
        assert len(maps.families) == 12
        assert {
            "fuel_compensation_main_bank_1",
            "fuel_compensation_main_bank_2",
            "idle_ignition_timing_bank_1",
            "idle_ignition_timing_bank_2",
            "rev_limit_throttle_cut",
        } <= set(maps.family_by_key)
        assert "rev_limit_fuel_cut" not in maps.family_by_key
        with pytest.raises(
            definition_projections.DefinitionProjectionError,
            match="Rolling Launch runtime is unavailable",
        ):
            definition_projections.rolling_launch_definition_layout(projection)


def _minimal_overrides():
    with (DEFS / "JK08A.overrides.toml").open("rb") as source:
        overrides = copy.deepcopy(tomllib.load(source))
    overrides["table"] = {
        "00008a27": overrides["table"]["00008a27"]
    }
    overrides["map_switching"] = {"enabled": False}
    overrides["rolling_launch"] = {"enabled": False}
    return overrides


def _direct_scalar_model():
    return {
        "addr": "00008a27",
        "family": "direct-scalar",
        "dims": 1,
        "width": 1,
        "height": None,
        "storagetype": "uint8",
        "confidence": "code",
        "role": "table",
        "semantics": "MAF factor",
        "units": "kg/hr",
        "scale_expr": "x*0.0001",
        "to_byte": "x/0.0001",
        "scale_conf": "candidate",
        "note": "Reviewed source model.",
        "wrappers": [],
        "kernels": [],
        "steps": [],
        "accessors": [],
        "resolver_kinds": [],
        "axis_x": [],
        "axis_y": [],
        "diagnostic_bindings": [],
    }


@pytest.mark.parametrize(
    ("rom", "target_address", "runtime_a_sum", "switch_count"),
    (
        ("JK00C", "00008a4c", "0x97A0", 1),
        ("JK00D", "00008a4d", "0x97B0", 2),
    ),
)
def test_projection_applies_target_map_checksums_and_switches(
    rom, target_address, runtime_a_sum, switch_count
):
    projection = definition_projections.projection_for_rom(rom)
    result = definition_projections.apply_projection(
        projection,
        {"00008a27": _direct_scalar_model()},
        {},
        _minimal_overrides(),
        romkit.load(rom),
        required_maps={"00008a27"},
    )

    assert set(result.maps) == {target_address}
    assert result.maps[target_address]["addr"] == target_address
    assert result.overrides["checksum"][1]["sumloc"] == runtime_a_sum
    assert len(result.overrides["switch"]) == switch_count
    assert "flashmethod" not in result.overrides["rom"]


@pytest.mark.parametrize(
    (
        "rom",
        "target_address",
        "checksum_verified",
        "map_switching",
        "switch_count",
    ),
    (
        ("JK78C", "00008896", False, False, 0),
        ("1ND0A", "00008939", True, True, 1),
        ("1ND3B", "00008939", True, True, 1),
    ),
)
def test_vq37_projection_exposes_only_declared_editor_runtime_capabilities(
    rom, target_address, checksum_verified, map_switching, switch_count
):
    projection = definition_projections.projection_for_rom(rom)
    result = definition_projections.apply_projection(
        projection,
        {"00008a27": _direct_scalar_model()},
        {},
        _minimal_overrides(),
        romkit.load(rom),
        required_maps={"00008a27"},
    )

    assert projection.checksum is checksum_verified
    assert projection.romraider_checksum is False
    assert set(result.maps) == {target_address}
    assert "checksum" not in result.overrides
    assert len(result.overrides["switch"]) == switch_count
    if switch_count:
        assert result.overrides["switch"][0]["name"] == (
            "CAN Telemetry at Startup"
        )
        assert result.overrides["switch"][0]["storageaddress"] == "0x134E03"
    assert result.overrides["map_switching"] == {"enabled": map_switching}
    assert result.overrides["rolling_launch"] == {"enabled": False}


def test_visible_map_without_binding_stops_projection():
    projection = definition_projections.projection_for_rom("JK00D")
    with pytest.raises(
        definition_projections.DefinitionProjectionError,
        match="visible source maps lack correspondence",
    ):
        definition_projections.apply_projection(
            projection,
            {"00008a27": _direct_scalar_model()},
            {},
            _minimal_overrides(),
            romkit.load("JK00D"),
            required_maps={"0000ffff"},
        )
