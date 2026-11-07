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
        "exhaust_cvtc_cold": "0x0B67E",
        "exhaust_cvtc_correction": "0x0AECE",
        "switches": {
            "Developer Immobilizer": "0x873F",
            "Cruise Control Switch": "0x8B59",
            "CAN Telemetry at Startup": "0xE1503",
        },
    },
    "JK00D": {
        "checksum_sum": "0x97B0",
        "checksum_xor": "0x97A8",
        "intake_cvtc_target": "0x0B7CE",
        "exhaust_cvtc_target": "0x0B6CE",
        "exhaust_cvtc_cold": "0x0B68E",
        "exhaust_cvtc_correction": "0x0AEDE",
        "switches": {
            "Developer Immobilizer": "0x8740",
            "Cruise Control Switch": "0x8B5A",
            "CAN Telemetry at Startup": "0xE1503",
        },
    },
}

JK78C_MAP_ADDRESSES = {
    "Map 1 - Fuel Compensation - Main - Default": "0x09EBA",
    "Map 1 - Fuel Compensation - Main - Alternate [stored count]": "0x09FBA",
    "Map 1 - Engine Speed Limit - Fuel Cut Caps": "0x09040",
    "Map 1 - Engine Speed Limit - Fuel Cut Curves": "0x16BF4",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Default": "0x137E8",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Alternate": "0x137F0",
    "Target Mixture - Main": "0x0A3CA",
    "Target Mixture Multiplier - High-Detonation State": "0x13AD8",
}

ONE_ND_MAP_ADDRESSES = {
    "MAF Factor": "0x08939",
    "Map 1 - Fuel Compensation - Main - Default": "0x0A1C0",
    "Map 1 - Fuel Compensation - Main - Alternate [stored count]": "0x0A2C0",
    "Map 1 - Engine Speed Limit - Fuel Cut Caps": "0x091D2",
    "Map 1 - Engine Speed Limit - Fuel Cut Curves": "0x17202",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Default": "0x13C1A",
    "Map 1 - Timing-State Addend - Warm DFCO Transition - Alternate": "0x13C22",
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


def test_native_fuel_artifacts_preserve_stored_counts_and_mixed_axis_storage():
    names = (
        "Fuel Composite - Additional Multiplier [stored count]",
        "Transient Fuel Term - Additional Multiplier [stored count]",
        "Fuel Four-Factor Term - Surface Multiplier [stored count]",
    )
    # Table, row axis, column axis, column element width.
    bindings = {
        "JK78C": ((0xA38A, 0x13BA0, 0x13B98, 8),
                  (0x9B1A, 0x137C0, 0x137B8, 8),
                  (0xB1CA, 0x14258, 0x14250, 8)),
        "1ND0A": ((0xA790, 0x13FFA, 0x13FF2, 8),
                   (0x9E20, 0x13BF2, 0x13BEA, 8),
                   (0xB610, 0x146EE, 0x146E6, 8)),
        "1ME3B": ((0xA684, 0x13E7C, 0x1667C, 16),
                   (0x9D94, 0x139EE, 0x139E6, 8),
                   (0xB6C4, 0x145A2, 0x1459A, 8)),
    }
    bindings["1ND3B"] = bindings["1ND0A"]
    for rom, rows in bindings.items():
        _, xml = _xml_tables(rom)
        xdf = _xdf_tables(ET.parse(DEFS / f"{rom}.xdf").getroot())
        for name, (address, row, column, column_bits) in zip(names, rows):
            table = xml[name]
            assert int(table.get("storageaddress"), 16) == address
            assert (table.get("storagetype"), table.get("sizex"), table.get("sizey")) == (
                "uint8", "8", "8"
            )
            for entity in (table, *table.findall("table")):
                scale = entity.find("scaling")
                assert (scale.get("units"), scale.get("expression"), scale.get("to_byte")) == (
                    "Stored count", "x", "x"
                )
            for kind, axis_address, bits, identifier in (
                ("X Axis", column, column_bits, "x"),
                ("Y Axis", row, 8, "y"),
            ):
                axis = table.find(f"table[@type='{kind}']")
                assert int(axis.get("storageaddress"), 16) == axis_address
                assert axis.get("storagetype") == f"uint{bits}"
                data = xdf[name].find(f"XDFAXIS[@id='{identifier}']/EMBEDDEDDATA")
                assert int(data.get("mmedaddress"), 16) == axis_address
                assert int(data.get("mmedelementsizebits")) == bits
                assert data.get("mmedcolcount") == "8"
            assert int(_xdf_table_address(xdf[name]), 16) == address
            for axis in xdf[name].findall("XDFAXIS"):
                assert axis.findtext("units") == "Stored count"
                assert axis.find("MATH").get("equation") == "X"


def test_sh7059_mixture_artifacts_keep_q7_values_and_candidate_rpm_axes():
    bindings = {
        "1ND0A": (0xA7D0, 0x13F0A, 0x137B9, 0x13640, 0x137C1),
        "1ND3B": (0xA7D0, 0x13F0A, 0x137B9, 0x13640, 0x137C1),
        "1ME3B": (0xA704, 0x13CE6, 0x1350D, 0x13384, 0x13515),
    }
    for rom, (main, high, rpm, load, high_rpm) in bindings.items():
        _, xml = _xml_tables(rom)
        xdf = _xdf_tables(ET.parse(DEFS / f"{rom}.xdf").getroot())
        for name, address, axis_type, rpm_address, identifier in (
            ("Target Mixture - Main", main, "Y Axis", rpm, "y"),
            ("Target Mixture Multiplier - High-Detonation State", high,
             "X Axis", high_rpm, "x"),
        ):
            table = xml[name]
            assert int(table.get("storageaddress"), 16) == address
            assert table.find("scaling").get("expression") == "x/128"
            axis = table.find(f"table[@type='{axis_type}']")
            assert int(axis.get("storageaddress"), 16) == rpm_address
            assert axis.find("scaling").get("units") == "RPM [cand]"
            assert int(_xdf_table_address(xdf[name]), 16) == address
            assert xdf[name].findtext(f"XDFAXIS[@id='{identifier}']/units") == "RPM [cand]"
        load_axis = xml["Target Mixture - Main"].find("table[@type='X Axis']")
        assert int(load_axis.get("storageaddress"), 16) == load
        assert load_axis.find("scaling").get("units") == "Normalized BFS [%]"


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
        assert sum(1 for name in tables if name.startswith("DTC ")) == 95

        for name, address in expected["switches"].items():
            assert tables[name].get("storageaddress") == address
        assert not any("Rolling Launch" in name for name in tables)
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
        assert tables["Exhaust CVTC Target - Cold"].get(
            "storageaddress"
        ) == expected["exhaust_cvtc_cold"]
        assert tables[
            "Exhaust CVTC Target Correction - High-Detonation State"
        ].get("storageaddress") == expected["exhaust_cvtc_correction"]
        assert "Stationary Engine Speed Limit" in tables
        assert "Stationary Limiter Readiness Threshold" in tables
        assert "Stationary Limiter Readiness Step" in tables
        assert "Accelerator Pedal High-State Hysteresis" in tables

        text = (DEFS / f"{rom}.xml").read_text(encoding="utf-8")
        correspondence = f"JK08A-{rom}.definition-addresses.csv"
        assert correspondence in text
        assert f"{rom}-{rom}.definition-addresses.csv" not in text
        assert "flashmethod" not in text


def _scale_confidence_and_logger_bindings(table):
    parts = [table, *table.findall("table")]
    candidate = {
        part.get("type"): part.find("scaling").get("units").endswith(" [cand]")
        for part in parts
        if part.find("scaling") is not None
    }
    # A relocated static axis has no target storage to log against.
    bindings = {
        (part.get("type"), part.get("logparam"))
        for part in parts
        if part.get("logparam") and not part.get("type").startswith("Static")
    }
    return candidate, bindings


def test_8mfk_artifacts_keep_jk08a_scale_confidence_and_logger_bindings():
    _, source = _xml_tables("JK08A")
    for rom in TARGETS:
        _, tables = _xml_tables(rom)
        for name in sorted(set(source) & set(tables)):
            candidate, bindings = _scale_confidence_and_logger_bindings(tables[name])
            expected, expected_bindings = _scale_confidence_and_logger_bindings(
                source[name]
            )
            # A target-native table may store an axis that JK08A leaves implicit.
            parts = candidate.keys() & expected.keys()
            assert {part: candidate[part] for part in parts} == {
                part: expected[part] for part in parts
            }, (rom, name)
            assert bindings == expected_bindings, (rom, name)


def test_relocated_tunerpro_artifacts_match_romraider_projection():
    for rom, expected in TARGETS.items():
        root = ET.parse(DEFS / f"{rom}.xdf").getroot()
        header = root.find("XDFHEADER")
        tables = _xdf_tables(root)
        description = header.findtext("description")

        assert header.findtext("deftitle") == f"{rom} - VQ HR ECU"
        assert f"defs/JK08A-{rom}.definition-addresses.csv" in description
        assert f"defs/{rom}-{rom}.definition-addresses.csv" not in description
        assert f"defs/{rom}.dtc.csv" in description
        assert len(root.findall("XDFTABLE")) == 107
        assert root.findall("XDFFLAG") == []
        assert root.find("XDFCHECKSUM") is None

        assert _xdf_table_address(
            tables["Map 1 - Intake CVTC Target - Main"]
        ) == expected["intake_cvtc_target"].replace("0x0", "0x")
        assert _xdf_table_address(
            tables["Map 1 - Exhaust CVTC Target - Main"]
        ) == expected["exhaust_cvtc_target"].replace("0x0", "0x")
        assert not any("Rolling Launch" in title for title in tables)


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
    assert len(target.findall("table")) == 264
    assert len(tables) == 264
    assert "Engine Speed Limit - Throttle Request - Oil Temperature" in tables
    # The ignition families select the two executed surfaces; the canonical
    # trio reaches only the gated coordinator half and stays unpublished.
    assert tables["Map 1 - Ignition Timing Surface - Hot Coolant [stored count]"].get(
        "storageaddress"
    ) == "0x0A10A"
    assert tables["Map 1 - Ignition Timing Surface - Cold Coolant [stored count]"].get(
        "storageaddress"
    ) == "0x0A20A"
    hot_slot = tables["Map 3 - Ignition Timing Surface - Hot Coolant [stored count]"]
    assert hot_slot.get("storageaddress") == "0x1D000"
    assert hot_slot.get("mask") == "7F"
    assert tables["Map 3 - Ignition Timing Surface - Cold Coolant [stored count]"].get(
        "storageaddress"
    ) == "0x1D400"
    assert not any(
        name.endswith(("Cold State", "High-Octane State", "High-Detonation State"))
        and "Ignition" in name
        for name in tables
    )
    assert not any("Knock-State Path Enable" in name for name in tables)
    assert sum(1 for name in tables if name.startswith("DTC ")) == 77
    assert not any("Rolling Launch" in name for name in tables)
    assert any(name.startswith("Map 2 -") for name in tables)
    assert "Map 2 - Engine Speed Limit - Fuel Cut" not in tables
    assert "Map 2 - Engine Speed Limit - Fuel Cut Caps" in tables
    assert "Map 2 - Engine Speed Limit - Fuel Cut Curves" in tables
    assert "Map 2 - Engine Speed Limit - Throttle Request" in tables
    assert "Map 2 - Fuel Compensation - Main - Default" in tables
    assert "Map 2 - Fuel Compensation - Main - Alternate [stored count]" in tables
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
    assert len(root.findall("XDFTABLE")) == 185
    patches = root.findall("XDFPATCH")
    patches_by_title = {patch.findtext("title"): patch for patch in patches}
    non_dtc_patches = {
        title
        for title in patches_by_title
        if not title.startswith(("DTC ", "Disable DTC group:"))
    }
    assert non_dtc_patches == {
        "Developer Immobilizer",
        "CAN Telemetry at Startup",
    }
    assert sum(
        1 for title in patches_by_title if title.startswith("DTC ")
    ) == 39
    assert sum(
        1
        for title in patches_by_title
        if title.startswith("Disable DTC group:")
    ) == 7
    assert patches_by_title["CAN Telemetry at Startup"].find(
        "XDFPATCHENTRY"
    ).get("address") == "0x1F803"
    assert root.findall("XDFFLAG") == []
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
        checksums = {
            entry.get("type"): entry for entry in target.findall("checksum")
        }
        assert set(checksums) == {"alt2"}
        assert checksums["alt2"].get("start") == "0x8200"
        assert checksums["alt2"].get("end") == "0x180000"
        assert checksums["alt2"].get("skiploc") == "0x20000"
        assert checksums["alt2"].get("sumloc") == "0x9618"
        assert checksums["alt2"].get("xorloc") == "0x9610"
        assert len(target.findall("table")) == 282
        assert len(tables) == 282
        assert "Engine Speed Limit - Throttle Request - Oil Temperature" in tables
        # The ignition families select the two executed 16x16 surfaces and the
        # four 8x8 state-code surfaces; the canonical trio reaches only the
        # gated coordinator half.
        assert tables[
            "Map 1 - Ignition Timing Surface - VVEL State Codes 2 and 8 [stored count]"
        ].get("storageaddress") == "0x0A410"
        assert tables["Map 1 - Ignition Timing Surface - VVEL State Code 1 [stored count]"].get(
            "storageaddress"
        ) == "0x0A510"
        cold_slot = tables["Map 3 - Ignition Timing Surface - VVEL State Code 1 [stored count]"]
        assert cold_slot.get("storageaddress") == "0x132A00"
        assert cold_slot.get("mask") == "7F"
        assert not any(
            name.endswith(
                ("Cold State", "High-Octane State", "High-Detonation State")
            )
            and "Ignition" in name
            for name in tables
        )
        assert not any("Knock-State Path Enable" in name for name in tables)
        assert tables[
            "Map 1 - Ignition Timing Surface - VVEL State Codes 6 and 7 [stored count]"
        ].get("storageaddress") == "0x0A6D0"
        state_slot = tables[
            "Map 3 - Ignition Timing Surface - VVEL State Code 3 [stored count]"
        ]
        assert state_slot.get("storageaddress") == "0x1351C0"
        assert (state_slot.get("sizex"), state_slot.get("sizey")) == ("8", "8")
        assert state_slot.get("mask") == "7F"
        assert tables[
            "Map 5 - Ignition Timing Surface - VVEL State Codes 6 and 7 [stored count]"
        ].get("storageaddress") == "0x135540"
        assert sum(1 for name in tables if name.startswith("DTC ")) == 77
        assert not any("Rolling Launch" in name for name in tables)
        assert any(name.startswith("Map 2 -") for name in tables)
        assert tables["CAN Telemetry at Startup"].get(
            "storageaddress"
        ) == "0x134E03"
        assert tables["Cruise Control Switch"].get(
            "storageaddress"
        ) == "0x8A11"
        assert "Map 2 - Engine Speed Limit - Fuel Cut" not in tables
        assert "Map 2 - Engine Speed Limit - Fuel Cut Caps" in tables
        assert "Map 2 - Engine Speed Limit - Fuel Cut Curves" in tables
        assert "Map 2 - Engine Speed Limit - Throttle Request" in tables
        assert "Map 2 - Fuel Compensation - Main - Default" in tables
        assert "Map 2 - Fuel Compensation - Main - Alternate [stored count]" in tables
        assert (
            "Map 2 - Timing-State Addend - Warm DFCO Transition - Default"
            in tables
        )
        assert (
            "Map 2 - Timing-State Addend - Warm DFCO Transition - Alternate"
            in tables
        )
        for name, address in ONE_ND_MAP_ADDRESSES.items():
            assert tables[name].get("storageaddress") == address

        xml_text = (DEFS / f"{rom}.xml").read_text(encoding="utf-8")
        assert "defs/JK08A-1ND.definition-addresses.csv" in xml_text

        root = ET.parse(DEFS / f"{rom}.xdf").getroot()
        description = root.find("XDFHEADER").findtext("description")
        xdf_tables = _xdf_tables(root)
        assert len(root.findall("XDFTABLE")) == 202
        patches = root.findall("XDFPATCH")
        patches_by_title = {
            patch.findtext("title"): patch for patch in patches
        }
        non_dtc_patches = {
            title
            for title in patches_by_title
            if not title.startswith(("DTC ", "Disable DTC group:"))
        }
        assert non_dtc_patches == {
            "Developer Immobilizer",
            "Cruise Control Switch",
            "CAN Telemetry at Startup",
        }
        assert sum(
            1 for title in patches_by_title if title.startswith("DTC ")
        ) == 39
        assert sum(
            1
            for title in patches_by_title
            if title.startswith("Disable DTC group:")
        ) == 7
        entry = patches_by_title["CAN Telemetry at Startup"].find(
            "XDFPATCHENTRY"
        )
        assert entry.get("address") == "0x134E03"
        assert root.findall("XDFFLAG") == []
        assert (
            "No editor-side checksum is declared; the flashing workflow "
            "handles checksum correction." in description
        )
        assert "no verified" not in description.lower()
        assert "defs/JK08A-1ND.definition-addresses.csv" in description
        for name, address in ONE_ND_MAP_ADDRESSES.items():
            assert _xdf_table_address(xdf_tables[name]) == address.replace(
                "0x0", "0x"
            )


def test_1me3b_artifacts_publish_the_correspondence_and_runtime_allocation():
    target, tables = _xml_tables("1ME3B")
    romid = target.find("romid")

    assert romid.findtext("xmlid") == "1ME3B"
    assert romid.findtext("internalidstring") == "1ME3B"
    assert romid.findtext("ecuid") == "11ME3B"
    assert romid.findtext("caseid") == "9FZ3V5DD1"
    assert romid.findtext("memmodel") == "SH7059"
    assert romid.findtext("filesize") == "1536kb"
    assert romid.find("flashmethod") is None
    checksums = {
        entry.get("type"): entry for entry in target.findall("checksum")
    }
    assert set(checksums) == {"alt2"}
    assert checksums["alt2"].get("start") == "0x8200"
    assert checksums["alt2"].get("end") == "0x180000"
    assert checksums["alt2"].get("skiploc") == "0x20000"
    assert checksums["alt2"].get("sumloc") == "0x96FC"
    assert checksums["alt2"].get("xorloc") == "0x96F4"
    assert len(target.findall("table")) == 284
    assert len(tables) == 284
    assert "Engine Speed Limit - Throttle Request - Oil Temperature" in tables
    assert sum(1 for name in tables if name.startswith("DTC ")) == 75
    assert tables["MAF Factor"].get("storageaddress") == "0x08965"
    assert tables["Map 1 - Fuel Compensation - Main - Default"].get(
        "storageaddress"
    ) == "0x0A0F4"
    assert tables["Map 1 - Fuel Compensation - Main - Alternate [stored count]"].get(
        "storageaddress"
    ) == "0x0A1F4"
    assert tables["VVEL Duration Target - Running [stored count]"].get(
        "storageaddress"
    ) == "0x17276"
    assert tables["VVEL Duration Target - Hot Intake Idle [stored count]"].get(
        "storageaddress"
    ) == "0x0E17C"
    assert tables["Base Fuel Schedule K-Value"].get("storageaddress") == "0x09170"
    assert tables["Developer Immobilizer"].get("storageaddress") == "0x8671"
    assert not any(
        name.endswith(("Cold State", "High-Octane State", "High-Detonation State"))
        and "Ignition" in name
        for name in tables
    )
    # The coordinator dispatches by the VVEL state code alone: two 16x16 and
    # four 8x8 surfaces are the switched ignition families.
    hot = tables["Map 1 - Ignition Timing Surface - VVEL State Codes 2 and 8 [stored count]"]
    assert hot.get("storageaddress") == "0x0A344"
    assert hot.get("mask") == "7F"
    assert tables["Map 1 - Ignition Timing Surface - VVEL State Code 1 [stored count]"].get(
        "storageaddress"
    ) == "0x0A444"
    cold_slot = tables["Map 3 - Ignition Timing Surface - VVEL State Code 1 [stored count]"]
    assert cold_slot.get("storageaddress") == "0x13BA00"
    assert cold_slot.get("mask") == "7F"
    assert tables["Map 1 - Ignition Timing Surface - VVEL State Code 3 [stored count]"].get(
        "storageaddress"
    ) == "0x0A544"
    assert tables[
        "Map 1 - Ignition Timing Surface - VVEL State Codes 6 and 7 [stored count]"
    ].get("storageaddress") == "0x0A604"
    state_slot = tables["Map 3 - Ignition Timing Surface - VVEL State Code 3 [stored count]"]
    assert state_slot.get("storageaddress") == "0x13E1C0"
    assert (state_slot.get("sizex"), state_slot.get("sizey")) == ("8", "8")
    assert state_slot.get("mask") == "7F"
    assert tables[
        "Map 5 - Ignition Timing Surface - VVEL State Codes 6 and 7 [stored count]"
    ].get("storageaddress") == "0x13E540"
    assert not any("Rolling Launch" in name for name in tables)
    assert tables["CAN Telemetry at Startup"].get(
        "storageaddress"
    ) == "0x13DE03"
    assert "Map 2 - Engine Speed Limit - Fuel Cut" not in tables
    assert tables["Map 2 - Engine Speed Limit - Fuel Cut Caps"].get(
        "storageaddress"
    ) == "0x13B4F4"
    assert tables["Map 2 - Engine Speed Limit - Fuel Cut Curves"].get(
        "storageaddress"
    ) == "0x13C6E0"
    assert tables["Map 2 - Engine Speed Limit - Throttle Request"].get(
        "storageaddress"
    ) == "0x13C520"
    assert "Map 2 - Fuel Compensation - Main - Default" in tables
    assert "Map 2 - Fuel Compensation - Main - Alternate [stored count]" in tables

    xml_text = (DEFS / "1ME3B.xml").read_text(encoding="utf-8")
    assert "defs/JK08A-1ME3B.definition-addresses.csv" in xml_text

    root = ET.parse(DEFS / "1ME3B.xdf").getroot()
    xdf_tables = _xdf_tables(root)
    assert len(root.findall("XDFTABLE")) == 207
    assert root.find("XDFCHECKSUM") is None
    assert _xdf_table_address(xdf_tables["MAF Factor"]) == "0x8965"
    patches_by_title = {
        patch.findtext("title"): patch for patch in root.findall("XDFPATCH")
    }
    assert {
        title
        for title in patches_by_title
        if not title.startswith(("DTC ", "Disable DTC group:"))
    } == {
        "Developer Immobilizer",
        "CAN Telemetry at Startup",
    }
    assert patches_by_title["CAN Telemetry at Startup"].find(
        "XDFPATCHENTRY"
    ).get("address") == "0x13DE03"
    assert root.findall("XDFFLAG") == []
