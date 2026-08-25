import copy
from pathlib import Path
import tomllib

import pytest

from tools.mapkit import definition_projections
from tools.mapkit import rom as romkit
from tools.mapkit import vq37_native_fuel_cut


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
TARGETS = ("JK00C", "JK00D", "JK78C", "1ND0A", "1ND3B")
SH7058_HR_UNSUPPORTED = frozenset()
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
        assert values["native_maps"] == 0
        assert values["rolling_configuration"] == 0xE0660
    assert stats["JK78C"]["mapped"] == 44
    assert stats["JK78C"]["unsupported"] == len(VQ37_UNSUPPORTED)
    assert stats["JK78C"]["checksum"] is True
    assert stats["JK78C"]["romraider_checksum"] is True
    assert stats["JK78C"]["map_families"] == 14
    assert stats["JK78C"]["native_maps"] == 2
    assert stats["JK78C"]["rolling_configuration"] == 0x1E960
    for rom in ("1ND0A", "1ND3B"):
        values = stats[rom]
        assert values["mapped"] == 44
        assert values["unsupported"] == len(VQ37_UNSUPPORTED)
        assert values["checksum"] is True
        assert values["romraider_checksum"] is True
        assert values["map_families"] == 14
        assert values["native_maps"] == 2
        assert values["rolling_configuration"] == 0x133F60


CVTC_TARGET_CORRESPONDENCE = {
    "JK00C": {
        "0000ab5a": "0000aede",
        "0000b33a": "0000b6be",
        "0000b43a": "0000b7be",
        "0000b53a": "0000b8be",
    },
    "JK00D": {
        "0000ab5a": "0000aeee",
        "0000b33a": "0000b6ce",
        "0000b43a": "0000b7ce",
        "0000b53a": "0000b8ce",
    },
}


def test_cvtc_targets_bind_one_intake_and_one_exhaust_path():
    for rom, expected in CVTC_TARGET_CORRESPONDENCE.items():
        projection = definition_projections.projection_for_rom(rom)
        rows = [
            binding
            for binding in projection.bindings
            if binding.entity == "Map" and binding.source in expected
        ]
        assert {row.source: row.target for row in rows} == expected
        assert all(row.status == "reviewed-target" for row in rows)
        assert all(row.variant == "" for row in rows)


LIMITER_CORRESPONDENCE = {
    "JK00C": {
        "000085d9": "000085e4",
        "00008fdc": "00009030",
        "0000911c": "00009174",
        "000124d2": "000147cf",
    },
    "JK00D": {
        "000085d9": "000085e4",
        "00008fdc": "0000903e",
        "0000911c": "00009182",
        "000124d2": "000147ef",
    },
}


def test_limiter_and_pedal_thresholds_bind_target_literals():
    for rom, expected in LIMITER_CORRESPONDENCE.items():
        projection = definition_projections.projection_for_rom(rom)
        rows = [
            binding
            for binding in projection.bindings
            if binding.entity == "Map" and binding.source in expected
        ]
        assert {row.source: row.target for row in rows} == expected
        assert all(row.status == "reviewed-target" for row in rows)
        assert all(row.variant == "" for row in rows)
        assert all(row.function_kinds == "normalized-shape" for row in rows)


def test_runtime_definition_layouts_use_target_allocation():
    for rom in ("JK00C", "JK00D"):
        projection = definition_projections.projection_for_rom(rom)
        maps = definition_projections.map_switching_definition_layout(projection)
        launch = definition_projections.rolling_launch_definition_layout(projection)

        assert maps.rom == rom
        assert maps.slot_count == 5
        assert len(maps.families) == 13
        assert {
            "intake_cvtc_target",
            "exhaust_cvtc_target",
        } <= set(maps.family_by_key)
        assert launch.rom == rom
        assert launch.configuration.start == 0xE0660

    for rom in ("JK78C", "1ND0A", "1ND3B"):
        projection = definition_projections.projection_for_rom(rom)
        maps = definition_projections.map_switching_definition_layout(projection)

        assert maps.rom == rom
        assert maps.variant == (
            "sh7058-jk78" if rom == "JK78C" else "sh7059-1nd"
        )
        assert maps.slot_count == 5
        assert len(maps.families) == 14
        assert {
            "fuel_compensation_main_bank_1",
            "fuel_compensation_main_bank_2",
            "idle_ignition_timing_bank_1",
            "idle_ignition_timing_bank_2",
            "rev_limit_fuel_cut_caps",
            "rev_limit_fuel_cut_curves",
            "rev_limit_throttle_cut",
        } <= set(maps.family_by_key)
        assert "rev_limit_fuel_cut" not in maps.family_by_key
        launch = definition_projections.rolling_launch_definition_layout(
            projection
        )
        assert launch.variant == "vq37-fuel-coordinator"
        assert launch.configuration.start == (
            0x1E960 if rom == "JK78C" else 0x133F60
        )


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
        ("JK00C", "00008a4c", "0x97A0", 2),
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
        "romraider_checksum",
        "map_switching",
        "immobilizer_address",
        "switch_address",
    ),
    (
        ("JK78C", "00008896", True, True, True, "0x861C", "0x1F803"),
        ("1ND0A", "00008939", True, True, True, "0x8668", "0x134E03"),
        ("1ND3B", "00008939", True, True, True, "0x8668", "0x134E03"),
    ),
)
def test_vq37_projection_exposes_only_declared_editor_runtime_capabilities(
    rom,
    target_address,
    checksum_verified,
    romraider_checksum,
    map_switching,
    immobilizer_address,
    switch_address,
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
    assert projection.romraider_checksum is romraider_checksum
    native = vq37_native_fuel_cut.load_registry()[rom]
    caps_address = f"{native.caps_address:08x}"
    curves_address = f"{native.curves_address:08x}"
    assert set(result.maps) == {
        target_address,
        caps_address,
        curves_address,
    }
    assert result.overrides["table"][caps_address]["name"] == (
        "Engine Speed Limit - Fuel Cut Caps"
    )
    assert result.overrides["table"][curves_address]["name"] == (
        "Engine Speed Limit - Fuel Cut Curves"
    )
    assert ("checksum" in result.overrides) is romraider_checksum
    switches = result.overrides["switch"]
    assert [entry["name"] for entry in switches] == [
        "CAN Telemetry at Startup",
        "Developer Immobilizer",
    ]
    assert switches[0]["storageaddress"] == switch_address
    assert switches[1]["storageaddress"] == immobilizer_address
    assert result.overrides["map_switching"] == {"enabled": map_switching}
    assert result.overrides["rolling_launch"] == {"enabled": True}


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
