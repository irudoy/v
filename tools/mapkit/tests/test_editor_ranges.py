"""Editor writes fit builder storage; protected axis labels retain stock data."""

from pathlib import Path
from unittest.mock import patch
import xml.etree.ElementTree as ET

import pytest

from patches import rom_checksums
from tools.mapkit import definition_targets, editor_ranges, rom as romkit


ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("kind", ("table", "axis", "switch", "flag", "patch"))
def test_complete_editor_extent_must_fit_one_builder_range(kind):
    xml, xdf = "<roms/>", "<XDFFORMAT/>"
    if kind in {"table", "axis"}:
        xml = ('<roms><table type="2D" name="probe" storageaddress="0x10" '
               'storagetype="uint16" sizex="2"/></roms>')
    elif kind == "switch":
        xml = ('<roms><table type="Switch" name="probe" storageaddress="0x10">'
               '<state data="00 01 02 03"/></table></roms>')
    elif kind == "flag":
        xdf = ('<XDFFORMAT><XDFFLAG><EMBEDDEDDATA mmedaddress="0x10" '
               'mmedelementsizebits="32"/></XDFFLAG></XDFFORMAT>')
    else:
        xdf = ('<XDFFORMAT><XDFPATCHENTRY address="0x10" datasize="0x4"/>'
               '</XDFFORMAT>')
    editor_ranges.require_coverage("probe", xml, xdf, ((0x10, 0x14),))
    with pytest.raises(ValueError, match="outside builder"):
        editor_ranges.require_coverage("probe", xml, xdf, ((0x10, 0x13),))
    with pytest.raises(ValueError, match="outside builder"):
        editor_ranges.require_coverage("probe", xml, xdf, ((0x10, 0x12), (0x12, 0x14)))


def test_protected_axis_labels_use_exact_image_points_without_mutating_facts():
    image = romkit.Image("probe", None, bytes.fromhex("00001000"))
    axis = dict(addr="00000000", len=2, storagetype="uint16", scale_expr="x*100/40960")
    with patch.object(editor_ranges, "writable_ranges", return_value=((10, 20),)):
        result = editor_ranges.bind_axes("probe", image, {axis["addr"]: axis}, {axis["addr"]})
    assert result[axis["addr"]]["read_only_values"] == ["0", "10"]
    assert "read_only_values" not in axis


def test_editor_without_runtime_uses_stock_checksum_domain():
    rom = 'editor-probe'
    layout = rom_checksums.layout_for_rom('1ME3B')
    with patch.object(editor_ranges.rom_checksums, 'layout_for_rom', return_value=layout):
        ranges = editor_ranges.writable_ranges(rom)
    assert editor_ranges.contains(ranges, 0x9000, 2)
    assert not editor_ranges.contains(ranges, 0x8204, 2)
    assert not editor_ranges.contains(ranges, layout.runtime_a_xor_field, 4)
    assert not editor_ranges.contains(ranges, 0x20000, 2)


@pytest.mark.parametrize("rom", definition_targets.registered_targets())
def test_registered_editor_artifacts_fit_builder_ranges(rom):
    editor_ranges.require_coverage(
        rom, (ROOT / f"defs/{rom}.xml").read_text(),
        (ROOT / f"defs/{rom}.xdf").read_text(),
    )


@pytest.mark.parametrize("rom", definition_targets.registered_targets())
def test_registered_torque_axis_labels_match_each_stock_image(rom):
    target = definition_targets.load_target(rom)
    address = "0002378c"
    if target.definition_projection is not None:
        bindings = [row.target for row in target.definition_projection.bindings
                    if row.entity == "Axis" and row.source == address and row.mapped]
        assert len(set(bindings)) == 1
        address = bindings[0]
    expected = [format(value * 100 / 40960, ".15g")
                for value in target.image.values(address, 16, "uint16")]
    xml = ET.parse(ROOT / f"defs/{rom}.xml").getroot()
    table = next(row for row in xml.iter("table")
                 if row.get("name") == "Engine Torque Surface")
    axis = table.find("./table[@type='Static X Axis']")
    assert axis is not None
    assert "storageaddress" not in axis.attrib
    assert [item.text for item in axis.findall("data")] == expected
    xdf = ET.parse(ROOT / f"defs/{rom}.xdf").getroot()
    table = next(row for row in xdf.iter("XDFTABLE")
                 if row.findtext("title") == "Engine Torque Surface")
    axis = table.find("./XDFAXIS[@id='x']")
    assert "mmedaddress" not in axis.find("EMBEDDEDDATA").attrib
    assert [item.get("value") for item in axis.findall("LABEL")] == expected
