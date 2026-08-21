from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
TARGETS = {
    "JK00C": {
        "checksum_sum": "0x97A0",
        "checksum_xor": "0x9798",
        "exhaust_bank_1": "0x0B7BE",
        "exhaust_bank_2": "0x0B6BE",
        "switches": {
            "CAN Telemetry at Startup": "0xE1503",
            "Rolling Launch Require Accelerator Pedal": "0xE066C",
        },
    },
    "JK00D": {
        "checksum_sum": "0x97B0",
        "checksum_xor": "0x97A8",
        "exhaust_bank_1": "0x0B7CE",
        "exhaust_bank_2": "0x0B6CE",
        "switches": {
            "Developer Immobilizer": "0x8740",
            "CAN Telemetry at Startup": "0xE1503",
            "Rolling Launch Require Accelerator Pedal": "0xE066C",
        },
    },
}

JK78C_MAP_ADDRESSES = {
    "Fuel Compensation - Main - Bank 1": "0x09EBA",
    "Fuel Compensation - Main - Bank 2": "0x09FBA",
    "Timing-State Addend - Warm DFCO Transition - Bank 1": "0x137E8",
    "Timing-State Addend - Warm DFCO Transition - Bank 2": "0x137F0",
}


def _xml_tables(rom):
    root = ET.parse(DEFS / f"{rom}.xml").getroot()
    target = root.find("./rom")
    return target, {
        table.get("name"): table
        for table in target.findall("table")
    }


def _xdf_tables(root):
    return {
        table.findtext("title"): table
        for table in root.findall("XDFTABLE")
    }


def _xdf_table_address(table):
    return table.find("./XDFAXIS[@id='z']/EMBEDDEDDATA").get(
        "mmedaddress"
    )


def test_relocated_romraider_artifacts_keep_target_addresses_and_provenance():
    for rom, expected in TARGETS.items():
        target, tables = _xml_tables(rom)
        romid = target.find("romid")
        checksums = {entry.get("type"): entry for entry in target.findall("checksum")}

        assert romid.findtext("xmlid") == rom
        assert romid.findtext("internalidstring") == rom
        assert romid.find("flashmethod") is None
        assert checksums["alt"].get("end") == "0x22628"
        assert checksums["alt2"].get("sumloc") == expected["checksum_sum"]
        assert checksums["alt2"].get("xorloc") == expected["checksum_xor"]
        assert not any(name.startswith("DTC ") for name in tables)

        for name, address in expected["switches"].items():
            assert tables[name].get("storageaddress") == address
        if rom == "JK00C":
            assert "Developer Immobilizer" not in tables

        assert (
            tables["Map 1 - Exhaust CVTC Target - Main - Bank 1"].get(
                "storageaddress"
            )
            == expected["exhaust_bank_1"]
        )
        assert (
            tables["Map 1 - Exhaust CVTC Target - Main - Bank 2"].get(
                "storageaddress"
            )
            == expected["exhaust_bank_2"]
        )

        text = (DEFS / f"{rom}.xml").read_text(encoding="utf-8")
        correspondence = f"JK08A-{rom}.definition-addresses.csv"
        assert correspondence in text
        assert f"{rom}-{rom}.definition-addresses.csv" not in text
        assert "flashmethod" not in text


def test_relocated_tunerpro_artifacts_match_romraider_projection():
    for rom, expected in TARGETS.items():
        root = ET.parse(DEFS / f"{rom}.xdf").getroot()
        header = root.find("XDFHEADER")
        tables = _xdf_tables(root)
        description = header.findtext("description")

        assert header.findtext("deftitle") == f"{rom} - VQ HR ECU"
        assert f"defs/JK08A-{rom}.definition-addresses.csv" in description
        assert f"defs/{rom}-{rom}.definition-addresses.csv" not in description
        assert f"defs/{rom}.dtc.csv" not in description
        assert len(root.findall("XDFTABLE")) == 99
        assert len(root.findall("XDFFLAG")) == 5
        assert root.find("XDFCHECKSUM") is None

        assert _xdf_table_address(
            tables["Map 1 - Exhaust CVTC Target - Main - Bank 1"]
        ) == expected["exhaust_bank_1"].replace("0x0", "0x")
        assert _xdf_table_address(
            tables["Map 1 - Exhaust CVTC Target - Main - Bank 2"]
        ) == expected["exhaust_bank_2"].replace("0x0", "0x")
        assert _xdf_table_address(
            tables["Rolling Launch Minimum Coolant Temperature"]
        ) == "0xE0666"


def test_jk78c_artifacts_expose_only_reviewed_definition_capabilities():
    target, tables = _xml_tables("JK78C")
    romid = target.find("romid")

    assert romid.findtext("xmlid") == "JK78C"
    assert romid.findtext("internalidstring") == "JK78C"
    assert romid.find("flashmethod") is None
    assert target.findall("checksum") == []
    assert len(target.findall("table")) == 34
    assert not any(name.startswith("DTC ") for name in tables)
    assert not any(name.startswith("Rolling Launch") for name in tables)
    assert not any(name.startswith("Map 2 -") for name in tables)
    for name, address in JK78C_MAP_ADDRESSES.items():
        assert tables[name].get("storageaddress") == address

    xml_text = (DEFS / "JK78C.xml").read_text(encoding="utf-8")
    assert "defs/JK08A-JK78C.definition-addresses.csv" in xml_text
    assert "storageaddress=\"0x099DB0\"" not in xml_text

    root = ET.parse(DEFS / "JK78C.xdf").getroot()
    description = root.find("XDFHEADER").findtext("description")
    xdf_tables = _xdf_tables(root)
    assert len(root.findall("XDFTABLE")) == 34
    assert root.findall("XDFPATCH") == []
    assert root.findall("XDFFLAG") == []
    assert "no verified JK78C checksum layout" in description
    for name, address in JK78C_MAP_ADDRESSES.items():
        assert _xdf_table_address(xdf_tables[name]) == address.replace(
            "0x0", "0x"
        )
