from pathlib import Path
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
TARGETS = {
    "JK00C": {
        "checksum_sum": "0x97A0",
        "checksum_xor": "0x9798",
        "intake_cvtc_target": "0x0B7BE",
        "exhaust_cvtc_target": "0x0B6BE",
        "switches": {
            "CAN Telemetry at Startup": "0xE1503",
            "Rolling Launch Require Accelerator Pedal": "0xE066C",
        },
    },
    "JK00D": {
        "checksum_sum": "0x97B0",
        "checksum_xor": "0x97A8",
        "intake_cvtc_target": "0x0B7CE",
        "exhaust_cvtc_target": "0x0B6CE",
        "switches": {
            "Developer Immobilizer": "0x8740",
            "CAN Telemetry at Startup": "0xE1503",
            "Rolling Launch Require Accelerator Pedal": "0xE066C",
        },
    },
}

JK78C_MAP_ADDRESSES = {
    "Map 1 - Fuel Compensation - Main - Bank 1": "0x09EBA",
    "Map 1 - Fuel Compensation - Main - Bank 2": "0x09FBA",
    "Map 1 - Engine Speed Limit - Fuel Cut Caps": "0x09040",
    "Map 1 - Engine Speed Limit - Fuel Cut Curves": "0x16BF4",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Bank 1": "0x137E8",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Bank 2": "0x137F0",
    "Rolling Launch Minimum Engine Speed": "0x1E96A",
}

ONE_ND_MAP_ADDRESSES = {
    "MAF Factor": "0x08939",
    "Map 1 - Fuel Compensation - Main - Bank 1": "0x0A1C0",
    "Map 1 - Fuel Compensation - Main - Bank 2": "0x0A2C0",
    "Map 1 - Engine Speed Limit - Fuel Cut Caps": "0x091D2",
    "Map 1 - Engine Speed Limit - Fuel Cut Curves": "0x17202",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Bank 1": "0x13C1A",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Bank 2": "0x13C22",
    "Rolling Launch Minimum Engine Speed": "0x133F6A",
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
            tables["Map 1 - Intake CVTC Target - Main"].get(
                "storageaddress"
            )
            == expected["intake_cvtc_target"]
        )
        assert (
            tables["Map 1 - Exhaust CVTC Target - Main"].get(
                "storageaddress"
            )
            == expected["exhaust_cvtc_target"]
        )
        assert "Intake CVTC Target - Cold" in tables
        assert "Intake CVTC Target Correction - High-Detonation State" in tables
        assert "Stationary Engine Speed Limit" in tables
        assert "Stationary Limiter Readiness Threshold" in tables
        assert "Stationary Limiter Readiness Step" in tables
        assert "Accelerator Pedal High-State Hysteresis" in tables

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
        assert len(root.findall("XDFTABLE")) == 105
        assert len(root.findall("XDFFLAG")) == 5
        assert root.find("XDFCHECKSUM") is None

        assert _xdf_table_address(
            tables["Map 1 - Intake CVTC Target - Main"]
        ) == expected["intake_cvtc_target"].replace("0x0", "0x")
        assert _xdf_table_address(
            tables["Map 1 - Exhaust CVTC Target - Main"]
        ) == expected["exhaust_cvtc_target"].replace("0x0", "0x")
        assert _xdf_table_address(
            tables["Rolling Launch Minimum Coolant Temperature"]
        ) == "0xE0666"


def test_jk78c_artifacts_expose_reviewed_runtime_capabilities():
    target, tables = _xml_tables("JK78C")
    romid = target.find("romid")
    checksums = {
        entry.get("type"): entry for entry in target.findall("checksum")
    }

    assert romid.findtext("xmlid") == "JK78C"
    assert romid.findtext("internalidstring") == "JK78C"
    assert romid.findtext("memmodel") == "SH7058"
    assert romid.findtext("filesize") == "1024kb"
    assert romid.find("flashmethod") is None
    assert checksums["alt"].get("end") == "0x22604"
    assert checksums["alt"].get("sumloc") == "0x20404"
    assert checksums["alt"].get("xorloc") == "0x20408"
    assert checksums["alt2"].get("sumloc") == "0x93DC"
    assert checksums["alt2"].get("xorloc") == "0x93D4"
    assert len(target.findall("table")) == 111
    assert not any(name.startswith("DTC ") for name in tables)
    assert tables["Rolling Launch Enable by Map"].get(
        "storageaddress"
    ) == "0x1E964"
    assert tables["Rolling Launch Require Accelerator Pedal"].get(
        "storageaddress"
    ) == "0x1E96C"
    assert any(name.startswith("Map 2 -") for name in tables)
    assert "Map 2 - Engine Speed Limit - Fuel Cut" not in tables
    assert "Map 2 - Engine Speed Limit - Fuel Cut Caps" in tables
    assert "Map 2 - Engine Speed Limit - Fuel Cut Curves" in tables
    assert "Map 2 - Engine Speed Limit - Throttle Request" in tables
    assert "Map 2 - Fuel Compensation - Main - Bank 1" in tables
    assert "Map 2 - Fuel Compensation - Main - Bank 2" in tables
    assert tables["CAN Telemetry at Startup"].get(
        "storageaddress"
    ) == "0x1F803"
    for name, address in JK78C_MAP_ADDRESSES.items():
        assert tables[name].get("storageaddress") == address

    xml_text = (DEFS / "JK78C.xml").read_text(encoding="utf-8")
    assert "defs/JK08A-JK78C.definition-addresses.csv" in xml_text
    assert "storageaddress=\"0x099DB0\"" not in xml_text

    root = ET.parse(DEFS / "JK78C.xdf").getroot()
    description = root.find("XDFHEADER").findtext("description")
    xdf_tables = _xdf_tables(root)
    assert len(root.findall("XDFTABLE")) == 108
    patches = root.findall("XDFPATCH")
    patches_by_title = {patch.findtext("title"): patch for patch in patches}
    assert set(patches_by_title) == {
        "CAN Telemetry at Startup",
        "Rolling Launch Require Accelerator Pedal",
    }
    assert patches_by_title["CAN Telemetry at Startup"].find(
        "XDFPATCHENTRY"
    ).get("address") == "0x1F803"
    assert patches_by_title[
        "Rolling Launch Require Accelerator Pedal"
    ].find("XDFPATCHENTRY").get("address") == "0x1E96C"
    assert {
        flag.findtext("title") for flag in root.findall("XDFFLAG")
    } == {f"Map {slot} - Rolling Launch Enable" for slot in range(1, 6)}
    assert root.find("XDFCHECKSUM") is None
    assert "No editor-side checksum is declared" in description
    assert "no verified" not in description.lower()
    for name, address in JK78C_MAP_ADDRESSES.items():
        assert _xdf_table_address(xdf_tables[name]) == address.replace(
            "0x0", "0x"
        )


def test_1nd_artifacts_use_shared_sh7059_definition_projection():
    for rom in ("1ND0A", "1ND3B"):
        target, tables = _xml_tables(rom)
        romid = target.find("romid")

        assert romid.findtext("xmlid") == rom
        assert romid.findtext("internalidstring") == rom
        assert romid.findtext("ecuid") == f"1{rom}"
        assert romid.findtext("caseid") == "8FZ35NEE6"
        assert romid.findtext("memmodel") == "SH7059"
        assert romid.findtext("filesize") == "1536kb"
        assert romid.find("flashmethod") is None
        assert target.findall("checksum") == []
        assert len(target.findall("table")) == 111
        assert not any(name.startswith("DTC ") for name in tables)
        assert tables["Rolling Launch Enable by Map"].get(
            "storageaddress"
        ) == "0x133F64"
        assert tables["Rolling Launch Require Accelerator Pedal"].get(
            "storageaddress"
        ) == "0x133F6C"
        assert any(name.startswith("Map 2 -") for name in tables)
        assert tables["CAN Telemetry at Startup"].get(
            "storageaddress"
        ) == "0x134E03"
        assert "Map 2 - Engine Speed Limit - Fuel Cut" not in tables
        assert "Map 2 - Engine Speed Limit - Fuel Cut Caps" in tables
        assert "Map 2 - Engine Speed Limit - Fuel Cut Curves" in tables
        assert "Map 2 - Engine Speed Limit - Throttle Request" in tables
        assert "Map 2 - Fuel Compensation - Main - Bank 1" in tables
        assert "Map 2 - Fuel Compensation - Main - Bank 2" in tables
        assert (
            "Map 2 - Timing-State Addend - Warm DFCO Transition - Bank 1"
            in tables
        )
        assert (
            "Map 2 - Timing-State Addend - Warm DFCO Transition - Bank 2"
            in tables
        )
        for name, address in ONE_ND_MAP_ADDRESSES.items():
            assert tables[name].get("storageaddress") == address

        xml_text = (DEFS / f"{rom}.xml").read_text(encoding="utf-8")
        assert "defs/JK08A-1ND.definition-addresses.csv" in xml_text

        root = ET.parse(DEFS / f"{rom}.xdf").getroot()
        description = root.find("XDFHEADER").findtext("description")
        xdf_tables = _xdf_tables(root)
        assert len(root.findall("XDFTABLE")) == 108
        patches = root.findall("XDFPATCH")
        patches_by_title = {
            patch.findtext("title"): patch for patch in patches
        }
        assert set(patches_by_title) == {
            "CAN Telemetry at Startup",
            "Rolling Launch Require Accelerator Pedal",
        }
        entry = patches_by_title["CAN Telemetry at Startup"].find(
            "XDFPATCHENTRY"
        )
        assert entry.get("address") == "0x134E03"
        pedal = patches_by_title[
            "Rolling Launch Require Accelerator Pedal"
        ].find("XDFPATCHENTRY")
        assert pedal.get("address") == "0x133F6C"
        assert {
            flag.findtext("title") for flag in root.findall("XDFFLAG")
        } == {
            f"Map {slot} - Rolling Launch Enable" for slot in range(1, 6)
        }
        assert "verified checksum implementation must correct" in description
        assert "no verified" not in description.lower()
        assert "defs/JK08A-1ND.definition-addresses.csv" in description
        for name, address in ONE_ND_MAP_ADDRESSES.items():
            assert _xdf_table_address(xdf_tables[name]) == address.replace(
                "0x0", "0x"
            )
