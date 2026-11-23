from pathlib import Path
import xml.etree.ElementTree as ET

from tools.mapkit import rom as romkit


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
ROMS = ("JK00A", "JK03A", "JK03B", "JK08A")


def _romraider_signature(path):
    root = ET.parse(path).getroot()
    rom = root.find("rom")
    romid = rom.find("romid")
    tables = rom.findall("table")
    checksums = rom.findall("checksum")
    return {
        "xmlid": romid.findtext("xmlid"),
        "internalid": romid.findtext("internalidstring"),
        "flashmethod": romid.findtext("flashmethod"),
        "table_addresses": sorted(
            table.get("storageaddress") for table in tables
        ),
        "checksums": sorted(
            tuple(sorted(checksum.attrib.items())) for checksum in checksums
        ),
    }


def _tunerpro_signature(path):
    root = ET.parse(path).getroot()
    header = root.find("XDFHEADER")
    return {
        "title": header.findtext("deftitle"),
        "description": header.findtext("description"),
        "tables": len(root.findall("XDFTABLE")),
        "patches": len(root.findall("XDFPATCH")),
        "flags": len(root.findall("XDFCONSTANT")),
    }


def test_exact_family_editor_artifacts_share_structure_and_keep_identity():
    xml = {
        rom: _romraider_signature(DEFS / f"{rom}.xml")
        for rom in ROMS
    }
    xdf = {
        rom: _tunerpro_signature(DEFS / f"{rom}.xdf")
        for rom in ROMS
    }
    canonical_xml = xml["JK08A"]
    canonical_xdf = xdf["JK08A"]

    for rom in ROMS:
        assert xml[rom]["xmlid"] == rom
        assert xml[rom]["internalid"] == rom
        assert xml[rom]["flashmethod"] is None
        assert xml[rom]["table_addresses"] == canonical_xml["table_addresses"]
        assert xml[rom]["checksums"] == canonical_xml["checksums"]
        assert xdf[rom]["title"] == f"{rom} - VQ HR ECU"
        assert xdf[rom]["tables"] == canonical_xdf["tables"]
        assert xdf[rom]["patches"] == canonical_xdf["patches"]
        assert xdf[rom]["flags"] == canonical_xdf["flags"]
        assert f"Exact {rom} definition" in xdf[rom]["description"]
        if rom != "JK08A":
            assert "canonical JK08A Memgraph facts" in xdf[rom]["description"]
            xml_text = (DEFS / f"{rom}.xml").read_text(encoding="utf-8")
            assert f"defs/analysis/calibration/{rom}.notes.md" not in xml_text
            assert "defs/analysis/calibration/JK08A.notes.md" in xml_text


def test_1ek7a_editors_publish_the_1me3b_stock_calibration_roles():
    extra_banks = tuple(f"Map {bank} - " for bank in range(2, 6))
    for extension in ("xml", "xdf"):
        stock_names = {}
        for rom in ("1ME3B", "1EK7A"):
            root = ET.parse(DEFS / f"{rom}.{extension}").getroot()
            if extension == "xml":
                names = [table.get("name") for table in root.findall("rom/table")
                         if table.get("type") in {"1D", "2D", "3D"}]
            else:
                names = [table.findtext("title") for table in root.findall("XDFTABLE")]
            stock = [name.removeprefix("Map 1 - ").removesuffix(" [stored count]")
                     for name in names
                     if not name.startswith(extra_banks)]
            stock_names[rom] = set(stock)
            assert len(stock_names[rom]) == len(stock)
        assert stock_names["1EK7A"] == stock_names["1ME3B"]


def test_1ek7a_xdf_describes_calibration_with_the_runtime_slots():
    xdf = _tunerpro_signature(DEFS / "1EK7A.xdf")
    assert "No editor-side checksum is declared" in xdf["description"]
    assert "target-specific Map 1 through Map 5 storage" in xdf["description"]


def test_1ek7a_knock_threshold_uses_its_stock_engine_speed_grid():
    image = romkit.load("1EK7A")
    rpm = [str(int(raw * 12.5)) for raw in image.values(0x1767E, 16, "uint16")]
    xml = ET.parse(DEFS / "1EK7A.xml").getroot()
    table = xml.find("rom/table[@storageaddress='0x12264']")
    assert table.find("scaling").get("units") == "Stored count"
    assert [cell.text for cell in table.findall("table[@type='Static X Axis']/data")] == rpm

    xdf = ET.parse(DEFS / "1EK7A.xdf").getroot()
    table = xdf.find("XDFTABLE[title='Knock Threshold by Evaluator Channel']")
    assert table.findtext("XDFAXIS[@id='z']/units") == "Stored count"
    assert [label.get("value") for label in table.findall("XDFAXIS[@id='x']/LABEL")] == rpm
