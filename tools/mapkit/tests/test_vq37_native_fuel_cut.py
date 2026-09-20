import pytest

from tools.mapkit import rom as romkit
from tools.mapkit import vq37_native_fuel_cut


TARGETS = ("JK78C", "1ND0A", "1ND3B", "1ME3B")


def test_registry_requires_the_complete_vq37_target_set(tmp_path):
    path = tmp_path / "native.toml"
    path.write_text(
        "schema_version = 1\n[target.JK78C]\n",
        encoding="utf-8",
    )

    with pytest.raises(
        vq37_native_fuel_cut.NativeFuelCutError,
        match="target set differs",
    ):
        vq37_native_fuel_cut.load_registry(path)


def test_registry_binds_exact_stock_functions_calibrations_and_pointers():
    registry = vq37_native_fuel_cut.load_registry()

    assert set(registry) == set(TARGETS)
    for rom in TARGETS:
        target = registry[rom]
        image = romkit.load(rom)
        pointer_site = target.coordinator_pointer_site
        coordinator_pointer = int.from_bytes(
            image.data[pointer_site : pointer_site + 4],
            "big",
        )
        maps, overrides = vq37_native_fuel_cut.apply_target(
            rom, {}, {"table": {}}, image
        )
        caps = f"{target.caps_address:08x}"
        curves = f"{target.curves_address:08x}"

        assert set(maps) == {caps, curves}
        assert coordinator_pointer == target.coordinator_address
        assert vq37_native_fuel_cut._bsr_target(
            image.data,
            target.predicate_call_site,
            f"{rom}.predicate_call_site",
        ) == target.function_address
        assert image.data[target.delay_calibration_address] == (
            target.delay_calibration_value
        )
        assert maps[caps]["width"] == 2
        assert maps[caps]["storagetype"] == "uint16"
        assert maps[curves]["width"] == 8
        assert maps[curves]["height"] == 2
        assert overrides["table"][caps]["static_axis"] == [
            "Activation", "Release"
        ]
        assert overrides["table"][curves]["static_axis_x"] == list(
            target.axis_values
        )
        assert overrides["table"][curves]["static_axis_y"] == [
            "Activation", "Release"
        ]


def test_1nd_targets_share_code_and_native_layout_but_keep_image_identity():
    registry = vq37_native_fuel_cut.load_registry()
    zero = registry["1ND0A"]
    three = registry["1ND3B"]

    assert zero.function_address == three.function_address
    assert zero.function_sha256 == three.function_sha256
    assert zero.coordinator_address == three.coordinator_address
    assert zero.coordinator_pointer_site == three.coordinator_pointer_site
    assert zero.predicate_call_site == three.predicate_call_site
    assert (
        zero.predicate_instruction_ordinal
        == three.predicate_instruction_ordinal
    )
    assert zero.delay_calibration_address == three.delay_calibration_address
    assert zero.delay_calibration_value == three.delay_calibration_value
    assert zero.pointer_bindings == three.pointer_bindings
    assert zero.ram_pointer_bindings == three.ram_pointer_bindings
    assert zero.caps_values == three.caps_values
    assert zero.curve_values == three.curve_values
    assert zero.stock_sha256 != three.stock_sha256


def test_stock_image_tamper_stops_native_map_projection():
    image = romkit.load("JK78C")
    changed = bytearray(image.data)
    changed[0] ^= 1
    damaged = romkit.Image(image.rom, image.path, bytes(changed))

    try:
        vq37_native_fuel_cut.apply_target(
            "JK78C", {}, {"table": {}}, damaged
        )
    except vq37_native_fuel_cut.NativeFuelCutError as error:
        assert "stock SHA-256" in str(error)
    else:
        raise AssertionError("tampered stock image was accepted")
