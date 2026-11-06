import copy
import xml.etree.ElementTree as ET

import pytest

from tools.mapkit import emit_def
from tools.mapkit import rom as romkit
from tools.mapkit import tunerpro
from tools.mapkit import vq37_native_fuel_cut
from tools.mapkit import vq37_native_tables


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
        assert maps[curves]["family"] == "direct-row-major"
        assert maps[curves]["axis_x"] == []
        assert maps[curves]["axis_y"] == [f"{target.axis_address:08x}"]
        assert "static_axis_x" not in overrides["table"][curves]
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


def editor_model(rom):
    """The native fuel-cut and table models of a stock image, as the projection joins them."""
    image = romkit.load(rom)
    native = vq37_native_tables.load_registry()[rom]
    # The canonical axes come from the projection; only the native axes matter here.
    projected = {
        key: {} for key in vq37_native_tables.table_axis_keys(rom)
        if key not in {f"{axis.address:08x}" for axis in native.axes}
    }
    maps, overrides = vq37_native_fuel_cut.apply_target(rom, {}, {"table": {}}, image)
    maps, axes, overrides = vq37_native_tables.apply_target(
        rom, maps, projected, overrides, image
    )
    target = vq37_native_fuel_cut.load_registry()[rom]
    axis = f"{target.axis_address:08x}"
    threshold = next(
        f"{table.address:08x}"
        for table in native.tables
        if table.axis_x == (target.axis_address,)
    )
    return image, maps, axes, overrides, axis, f"{target.curves_address:08x}", threshold


def xml_axes(maps, axes, overrides, key):
    lines = emit_def.table_axes_xml(maps[key], overrides["table"][key], overrides, axes)
    return ET.fromstring("<table>" + "\n".join(lines) + "</table>")


def xdf_axes(maps, axes, overrides, key):
    table = ET.Element("XDFTABLE")
    tunerpro.add_table_axes(table, maps[key], overrides["table"][key], overrides, axes)
    return {axis.get("id"): axis for axis in table.findall("XDFAXIS")}


@pytest.mark.parametrize("rom", TARGETS)
def test_both_tables_read_the_breakpoints_of_the_shared_axis_from_the_image(rom):
    image, maps, axes, overrides, axis, curves, threshold = editor_model(rom)
    assert emit_def.definition_failure(maps[curves], axes, overrides["table"][curves]) is None
    changed = bytearray(image.data)
    stock = image.values(axis, 8, "uint16")
    edited = [value + 2 * index + 1 for index, value in enumerate(stock)]
    for index, value in enumerate(edited):
        start = int(axis, 16) + 2 * index
        changed[start:start + 2] = value.to_bytes(2, "big")
    tuned = romkit.Image(image.rom, image.path, bytes(changed))

    for key in (curves, threshold):
        graph = xml_axes(maps, axes, overrides, key).find("table[@type='X Axis']")
        assert int(graph.get("storageaddress"), 16) == int(axis, 16)
        assert graph.get("storagetype") == "uint16"
        assert graph.get("sizex") == "8"
        address = int(graph.get("storageaddress"), 16)
        assert tuned.values(address, 8, "uint16") == edited
        assert image.values(address, 8, "uint16") == stock

        embedded = xdf_axes(maps, axes, overrides, key)["x"].find("EMBEDDEDDATA")
        assert embedded.get("mmedaddress") == tunerpro.xdf_address(axis)
        assert embedded.get("mmedelementsizebits") == "16"
        assert embedded.get("mmedcolcount") == "8"

    rows = xml_axes(maps, axes, overrides, curves).find("table[@type='Static Y Axis']")
    assert rows.get("name") == "Transition"
    assert [item.text for item in rows.findall("data")] == ["Activation", "Release"]
    labels = xdf_axes(maps, axes, overrides, curves)["y"].findall("LABEL")
    assert [label.get("value") for label in labels] == ["Activation", "Release"]


def changed_curves(change):
    _image, maps, axes, overrides, axis, curves, _threshold = editor_model("JK78C")
    calibration = copy.deepcopy(maps[curves])
    override = copy.deepcopy(overrides["table"][curves])
    axes = copy.deepcopy(axes)
    change(calibration, override, axes, axis)
    return emit_def.definition_failure(calibration, axes, override)


def drop(mapping, key):
    del mapping[key]


@pytest.mark.parametrize(("change", "reason"), (
    (lambda m, o, a, x: drop(o, "static_axis_y"), "only one axis was recovered for a 2D map"),
    (lambda m, o, a, x: o.update(static_axis_y=["Activation"]),
     "only one axis was recovered for a 2D map"),
    (lambda m, o, a, x: o.update(static_axis_x=list(range(8))),
     "only one axis was recovered for a 2D map"),
    (lambda m, o, a, x: m.update(family="interp-2d"), "only one axis was recovered for a 2D map"),
    (lambda m, o, a, x: m.update(axis_x=[x], axis_y=[]),
     "only one axis was recovered for a 2D map"),
    (lambda m, o, a, x: a[x].update(len=6), "has 6 points for 8 columns"),
    (lambda m, o, a, x: drop(a, x), "is absent from the editor model"),
))
def test_a_row_labelled_table_requires_declared_rows_and_a_matching_column_axis(change, reason):
    assert reason in changed_curves(change)
