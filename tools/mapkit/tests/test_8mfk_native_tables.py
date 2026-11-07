"""End-of-injection word curves of the 8MFK images in the native table registry.

JK00C and JK00D hold each end-of-injection curve as eight uint16 cells on an
explicit eight-word engine-speed axis, where JK08A holds eight uint8 cells on
an implicit axis. The relocated JK08A byte curves stay unsupported on both
targets, and the native table registry publishes the word curves.
"""

from pathlib import Path
import xml.etree.ElementTree as ET

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit import vq37_native_tables


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
BASE = "injection_end_angle_base"
CONDITIONAL = "injection_end_angle_conditional"
AXIS = "injection_end_angle_axis"
# The address of each curve and of their axis, with the literal words through
# which the end-of-injection writer loads it.
END_OF_INJECTION = {
    "JK00C": {
        "writer": 0x58AE4,
        BASE: (0x1715C, {0x58E94}),
        CONDITIONAL: (0x1717C, {0x58D10}),
        AXIS: (0x1716C, {0x58D14, 0x58E98}),
    },
    "JK00D": {
        "writer": 0x58AE0,
        BASE: (0x1717C, {0x58E90}),
        CONDITIONAL: (0x1719C, {0x58D0C}),
        AXIS: (0x1718C, {0x58D10, 0x58E94}),
    },
}
ROMS = sorted(END_OF_INJECTION)
# The stock words of both images: the axis spans 0 to 7600 RPM, the base cells
# end the pulse 58 degrees before and the conditional cells 50 degrees after
# intake TDC.
AXIS_WORDS = [0, 64, 128, 192, 256, 352, 464, 608]
CELLS = {BASE: [133] * 8, CONDITIONAL: [160] * 8}
NAMES = {
    BASE: "End of Injection Angle - Base",
    CONDITIONAL: "End of Injection Angle - Conditional",
}


def _words(image, address):
    return [
        int.from_bytes(image.data[at : at + 2], "big")
        for at in range(address, address + 16, 2)
    ]


def _bindings(entity):
    return {(p.site, p.accessor, p.offset) for p in entity.pointer_bindings}


@pytest.mark.parametrize("rom", ROMS)
def test_registry_binds_the_word_curves_to_the_writer_literals(rom):
    expected = END_OF_INJECTION[rom]
    writer = expected["writer"]
    target = vq37_native_tables.load_registry()[rom]
    tables = {table.identifier: table for table in target.tables}
    axes = {axis.identifier: axis for axis in target.axes}

    assert set(tables) == {BASE, CONDITIONAL}
    assert set(axes) == {AXIS}
    assert target.absent == {}
    axis_address, axis_sites = expected[AXIS]
    axis = axes[AXIS]
    assert (axis.address, axis.length, axis.storagetype, axis.kind) == (
        axis_address, 8, "uint16", "rpm")
    assert (axis.scale_expr, axis.scale_conf) == ("x*12.5", "code")
    assert _bindings(axis) == {(site, writer, 0) for site in axis_sites}
    for role in (BASE, CONDITIONAL):
        address, sites = expected[role]
        table = tables[role]

        assert (table.address, table.width, table.height, table.storagetype) == (
            address, 8, 1, "uint16")
        assert table.axis_x == (axis_address,)
        assert (table.units, table.scale_expr, table.scale_conf) == (
            "deg after intake TDC", "x*4-590", "code")
        assert table.name == NAMES[role]
        assert _bindings(table) == {(site, writer, 0) for site in sites}


@pytest.mark.parametrize("rom", ROMS)
def test_apply_target_publishes_the_stock_word_curves(rom):
    expected = END_OF_INJECTION[rom]
    image = romkit.load(rom)
    maps, axes, overrides = vq37_native_tables.apply_target(
        rom, {}, {}, {"table": {}}, image
    )
    axis_key = f"{expected[AXIS][0]:08x}"

    assert axes[axis_key]["values"] == AXIS_WORDS
    assert _words(image, expected[AXIS][0]) == AXIS_WORDS
    for role in (BASE, CONDITIONAL):
        address = expected[role][0]
        key = f"{address:08x}"
        model = maps[key]

        assert (model["storagetype"], model["width"], model["dims"]) == ("uint16", 8, 1)
        assert model["axis_x"] == [axis_key]
        assert model["accessors"] == [f"{expected['writer']:08x}"]
        assert overrides["table"][key]["name"] == NAMES[role]
        assert _words(image, address) == CELLS[role]


@pytest.mark.parametrize("rom", ROMS)
def test_registry_refuses_a_byte_reading_of_a_word_curve(rom):
    # The relocated JK08A model reads eight uint8 cells, which cover half of
    # the word curve and miss its reviewed digest.
    table = next(
        table for table in vq37_native_tables.load_registry()[rom].tables
        if table.identifier == BASE
    )

    with pytest.raises(vq37_native_tables.NativeTableError, match="values differ"):
        vq37_native_tables._verify_block(
            rom, romkit.load(rom), f"{table.address:08x}", table.address,
            table.width, "uint8", table.values_sha256,
        )


@pytest.mark.parametrize("rom", ROMS)
def test_definitions_publish_the_word_curves_on_the_explicit_axis(rom):
    expected = END_OF_INJECTION[rom]
    axis_address = expected[AXIS][0]
    target = ET.parse(DEFS / f"{rom}.xml").getroot().find("./rom")
    tables = {table.get("name"): table for table in target.findall("table")}
    xdf = ET.parse(DEFS / f"{rom}.xdf").getroot()
    xdf_tables = {table.findtext("title"): table for table in xdf.findall("XDFTABLE")}

    for role in (BASE, CONDITIONAL):
        address = expected[role][0]
        table = tables[NAMES[role]]
        axis = table.find("table")

        assert (table.get("type"), table.get("storagetype"),
                table.get("storageaddress"), table.get("sizex")) == (
            "2D", "uint16", f"0x{address:05X}", "8")
        assert table.find("scaling").get("expression") == "x*4-590"
        assert (axis.get("type"), axis.get("storagetype"),
                axis.get("storageaddress"), axis.get("sizex")) == (
            "X Axis", "uint16", f"0x{axis_address:05X}", "8")
        assert axis.find("scaling").get("expression") == "x*12.5"

        cells = xdf_tables[NAMES[role]].find("./XDFAXIS[@id='z']")
        points = xdf_tables[NAMES[role]].find("./XDFAXIS[@id='x']")
        assert (cells.find("EMBEDDEDDATA").get("mmedaddress"),
                cells.find("EMBEDDEDDATA").get("mmedelementsizebits"),
                cells.find("MATH").get("equation")) == (
            f"0x{address:X}", "16", "X*4-590")
        assert (points.find("EMBEDDEDDATA").get("mmedaddress"),
                points.find("EMBEDDEDDATA").get("mmedelementsizebits"),
                points.find("MATH").get("equation")) == (
            f"0x{axis_address:X}", "16", "X*12.5")


def test_jk08a_keeps_the_byte_curves_on_the_implicit_axis():
    target = ET.parse(DEFS / "JK08A.xml").getroot().find("./rom")
    tables = {table.get("name"): table for table in target.findall("table")}

    for role, address in ((BASE, "0x12302"), (CONDITIONAL, "0x1230A")):
        table = tables[NAMES[role]]

        assert (table.get("storagetype"), table.get("storageaddress"),
                table.get("sizex")) == ("uint8", address, "8")
        assert table.find("table").get("type") == "Static X Axis"
