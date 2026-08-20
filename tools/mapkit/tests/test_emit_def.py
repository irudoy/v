from pathlib import Path
import tomllib
import unittest
import xml.etree.ElementTree as ET

from tools.mapkit import emit_def, presentation


ROOT = Path(__file__).resolve().parents[3]
ROMRAIDER_DTC_CATEGORY = "Diagnostics//DTC"


def romraider_category(category):
    return category.replace(" / ", "//")

COMMON_TABLES = {
    "Developer Immobilizer": "NATS / Immobilizer",
    "MAF Factor": "Fuelling / MAF Scaling",
    "Base Fuel Schedule K-Value": "Fuelling / MAF Scaling",
    "Calculated Load": "Fuelling / Engine Load",
    "Ignition Timing Trim Cold": "Ignition Timing / Main",
    "Knock Control Enable - Cold": "Ignition Timing / Knock Control",
    "Knock Sensitivity": "Ignition Timing / Knock Control",
    "MAF Sensor Scaling Bank 1": "Fuelling / MAF Scaling",
    "MAF Sensor Scaling Bank 2": "Fuelling / MAF Scaling",
    "Stationary Rev Limiter": "Limiters / Stationary Rev Limiter",
    "Rolling Launch Enable by Map": "Rolling Launch / Map Enable",
    "Rolling Launch Require Accelerator Pedal": "Rolling Launch / Activation",
    "Rolling Launch Minimum Coolant Temperature": "Rolling Launch / Activation",
    "Rolling Launch Minimum Vehicle Speed": "Rolling Launch / Activation",
    "Rolling Launch Minimum Engine Speed": "Rolling Launch / Activation",
    "Rolling Launch Minimum Retard Ramp Width": "Rolling Launch / Ignition Retard",
    "Rolling Launch RPM Offset": "Rolling Launch / RPM Hold",
    "Rolling Launch Minimum RPM Hysteresis": "Rolling Launch / RPM Hold",
    "Rolling Launch Maximum RPM Hysteresis": "Rolling Launch / RPM Hold",
    "Rolling Launch RPM Hysteresis Ratio (%)": "Rolling Launch / RPM Hold",
}

DEFAULT_VISIBLE_TABLES = {
    "Accelerator Pedal High-State Hysteresis (0x8FDC)":
        "Electronic Throttle Control / Accelerator Pedal / Thresholds",
    "Stationary Rev Limiter Readiness Threshold (0x911C)":
        "Limiters / Stationary Rev Limiter",
    "Intake Cam Timing Conditional Correction": "Variable Valve Timing / Intake Cam",
    "Knock Sensor Circuit Monitor Surface A (0xABBA)":
        "Diagnostics / Knock Sensor Monitor",
    "Knock Sensor Circuit Monitor Surface B (0xABFA)":
        "Diagnostics / Knock Sensor Monitor",
    "Intake Cam Timing Main": "Variable Valve Timing / Intake Cam",
    "Intake Cam Timing Cold": "Variable Valve Timing / Intake Cam",
    "QH0 / Torque Conversion Map": "Electronic Throttle Control / Main",
    "Engine Torque Map": "Transmission / Shifting Performance",
    "Knock Slice Map - parallel bank (0x10F8E)":
        "Ignition Timing / Knock Control / Thresholds",
    "Initial Retard Quantity - unresolved mode (0x1202E)":
        "Ignition Timing / Transient Correction",
    "Conditional DFCO Entry Delay - scheduler counts (0x120F6)": "Fuelling / Overrun",
    "Fuel enrichment vs MBT-like axis (0x1236A)": "Fuelling / Enrichment",
    "Stationary Rev Limiter Accumulator Step (0x124D2)":
        "Limiters / Stationary Rev Limiter",
    "Injection Pulse Channel Multiplier (0x129C0)": "Fuel Delivery / Main",
    "Target Throttle Valve Opening Table": "Electronic Throttle Control / Main",
    "Engine Torque Scaled Correction vs RPM": "Transmission / Shifting Performance",
    "Engine Torque Base Correction vs RPM": "Transmission / Shifting Performance",
    "QH0 / Torque Conversion Map Trustful": "Electronic Throttle Control / Main",
    "Target Throttle Valve Opening Table Trustful": "Electronic Throttle Control / Main",
}

SLOT_TABLES = {
    "Fuel Targets": "Fuelling / Fuel Targets",
    "Fuel Compensation Main": "Fuelling / Fuel Compensation",
    "DFCO Entry RPM Threshold": "Fuelling / Overrun",
    "DFCO Full Restore RPM Threshold": "Fuelling / Overrun",
    "DFCO Hold RPM Threshold": "Fuelling / Overrun",
    "DFCO Low-Speed Intermediate Restore RPM Threshold":
        "Fuelling / Overrun",
    "Ignition Timing Trim Main": "Ignition Timing / Main",
    "Knock Control Enable - Main": "Ignition Timing / Knock Control",
    "Ignition Timing Trim High Det": "Ignition Timing / Main",
    "Knock Control Enable - High Det": "Ignition Timing / Knock Control",
    "Rev Limit - Fuel Cut": "Limiters / Rev Limit",
    "Rev Limit - Throttle Cut": "Limiters / Rev Limit",
    "Default/Post-Transition Timing-State Addend (x-128) (0x12196)":
        "Ignition Timing / State Accumulators",
    "Warm DFCO-Transition Timing-State Addend (x-128) (0x1219E)":
        "Ignition Timing / State Accumulators",
}


def slot_name(slot, name):
    return f"Map {slot} - {name}"


class EmitDefStaticAxesTest(unittest.TestCase):
    def setUp(self):
        self.map = {
            "addr": "0001108e",
            "family": "direct-row-major",
            "dims": 2,
            "width": 16,
            "height": 6,
            "storagetype": "uint16",
            "confidence": "code",
            "role": "table",
            "semantics": "Knock Slice Map",
            "units": "knock strength",
            "scale_expr": "x*0.0015259",
            "to_byte": "x/0.0015259",
            "scale_conf": "candidate",
            "note": "",
            "wrappers": [],
            "kernels": [],
            "steps": [],
            "accessors": ["00049ffc"],
            "resolver_kinds": ["manual"],
            "axis_x": [],
            "axis_y": [],
        }
        self.presentation = {
            "name": "Knock Slice Map",
            "category": "Ignition Timing / Knock Control",
            "mask": "FFFF",
            "static_axis_x_name": "Engine Speed [RPM]",
            "static_axis_x": [400 * (index + 1) for index in range(16)],
            "static_axis_y_name": "Cylinder",
            "static_axis_y": [1, 2, 3, 4, 5, 6],
        }

    def test_direct_row_major_map_accepts_two_static_axes(self):
        self.assertIsNone(
            emit_def.emittable(self.map, {}, self.presentation)
        )

    def test_definition_gate_requires_presentation_metadata(self):
        presentation = dict(self.presentation)
        del presentation["category"]
        self.assertEqual(
            emit_def.definition_failure(self.map, {}, presentation),
            "missing presentation name/category",
        )

    def test_definition_gate_accepts_a_complete_visible_map(self):
        self.assertIsNone(
            emit_def.definition_failure(self.map, {}, self.presentation)
        )

    def test_direct_row_major_map_rejects_wrong_axis_length(self):
        presentation = dict(self.presentation)
        presentation["static_axis_y"] = [1, 2, 3]
        self.assertEqual(
            emit_def.emittable(self.map, {}, presentation),
            "a Static Y Axis with 6 points is required",
        )

    def test_direct_indexed_map_accepts_named_static_axis(self):
        direct_map = dict(
            self.map,
            addr="000129c0",
            family="direct-indexed",
            dims=1,
            width=6,
            height=None,
            storagetype="uint8",
            semantics="Per-channel injection pulse multiplier",
            units="ratio",
            scale_expr="x/128",
            to_byte="x*128",
            scale_conf="code",
            accessors=["0004eba2"],
        )
        presentation = {
            "name": "Injection Pulse Channel Multiplier",
            "category": "Fuel Delivery / Main",
            "static_axis_name": "Channel",
            "static_axis": [1, 2, 3, 4, 5, 6],
        }
        self.assertIsNone(
            emit_def.emittable(direct_map, {}, presentation)
        )
        overrides = {"table": {direct_map["addr"]: presentation}}
        xml = "\n".join(
            emit_def.table_xml(direct_map, overrides, {}, "JK08A")
        )
        self.assertIn('type="Static X Axis" name="Channel"', xml)
        self.assertEqual(xml.count("<data>"), 6)

    def test_implicit_map_accepts_reviewed_physical_axis_labels(self):
        implicit_map = dict(
            self.map,
            family="implicit",
            dims=1,
            width=16,
            height=None,
            axis_x=[],
            axis_y=[],
            steps=[16],
        )
        presentation = {
            "name": "Coolant-indexed RPM threshold",
            "category": "Fuel Delivery / Fuel Cut / Main",
            "static_axis_name": "Coolant Temperature [deg C]",
            "static_axis": list(range(-40, 120, 10)),
        }
        self.assertIsNone(
            emit_def.emittable(implicit_map, {}, presentation)
        )
        overrides = {"table": {implicit_map["addr"]: presentation}}
        xml = "\n".join(
            emit_def.table_xml(implicit_map, overrides, {}, "JK08A")
        )
        self.assertIn(
            'name="Coolant Temperature [deg C]"',
            xml,
        )
        self.assertIn("<data>-40</data>", xml)
        self.assertNotIn("Raw input", xml)

    def test_direct_scalar_accepts_one_reviewed_label(self):
        scalar = dict(
            self.map,
            family="direct-scalar",
            dims=1,
            width=1,
            height=None,
            axis_x=[],
            axis_y=[],
            steps=[],
        )
        presentation = {
            "name": "Base Fuel Schedule K-Value",
            "category": "Fuelling / MAF Scaling",
            "static_axis": ["K-Value"],
        }
        self.assertIsNone(
            emit_def.emittable(scalar, {}, presentation)
        )
        overrides = {"table": {scalar["addr"]: presentation}}
        xml = "\n".join(
            emit_def.table_xml(scalar, overrides, {}, "JK08A")
        )
        self.assertIn("<data>K-Value</data>", xml)

    def test_xml_keeps_row_major_geometry_mask_and_axis_types(self):
        overrides = {"table": {self.map["addr"]: self.presentation}}
        xml = "\n".join(emit_def.table_xml(self.map, overrides, {}, "JK08A"))
        self.assertIn('sizex="16"', xml)
        self.assertIn('sizey="6"', xml)
        self.assertIn('mask="FFFF"', xml)
        self.assertIn('type="Static X Axis"', xml)
        self.assertIn('name="Engine Speed [RPM]"', xml)
        self.assertIn('type="Static Y Axis"', xml)
        self.assertIn('name="Cylinder"', xml)

    def test_candidate_map_keeps_a_functional_category(self):
        self.map["confidence"] = "candidate"
        presentation = dict(self.presentation)
        presentation["category"] = (
            "Ignition Timing / Knock Control (traced) (candidate)"
        )
        overrides = {"table": {self.map["addr"]: presentation}}
        xml = "\n".join(
            emit_def.table_xml(self.map, overrides, {}, "JK08A")
        )
        self.assertIn(
            'category="Ignition Timing//Knock Control"',
            xml,
        )
        self.assertNotIn("(traced)", xml)
        self.assertIn("map [candidate]", xml)

    def test_xml_comment_includes_static_diagnostic_context(self):
        self.map["diagnostic_bindings"] = [{
            "diagnostic_label": "DtcCode",
            "diagnostic_key": "P0327",
            "diagnostic_name": "P0327",
            "confidence": "code",
            "applicability": "exact_rom",
            "priority": 100,
        }]
        overrides = {"table": {self.map["addr"]: self.presentation}}
        xml = "\n".join(
            emit_def.table_xml(self.map, overrides, {}, "JK08A")
        )
        self.assertIn(
            "static diagnostic context: DTC P0327 [code, exact_rom]",
            xml,
        )

    def test_masked_view_reuses_source_geometry_and_has_independent_scaling(self):
        presentation = dict(self.presentation)
        presentation["mask"] = "7F"
        overrides = {
            "table": {self.map["addr"]: presentation},
            "masked_view": [{
                "source": self.map["addr"],
                "name": "Knock Window",
                "category": "Ignition Timing / Knock Control",
                "mask": "8000",
                "units": "Knock Window (0: Off | 1: On)",
                "expression": "x",
                "to_byte": "x",
            }],
        }
        entries, grouped = emit_def.masked_views(
            overrides, {self.map["addr"]: self.map}
        )
        self.assertEqual(len(entries), 1)
        xml = "\n".join(emit_def.masked_view_xml(
            self.map, grouped[self.map["addr"]][0], overrides, {}, "JK08A"
        ))
        self.assertIn('sizex="16"', xml)
        self.assertIn('sizey="6"', xml)
        self.assertIn('mask="8000"', xml)
        self.assertIn('expression="x"', xml)
        self.assertIn('type="Static X Axis"', xml)
        self.assertIn('type="Static Y Axis"', xml)


class DefinitionPresentationPolicyTest(unittest.TestCase):
    def test_romraider_category_uses_hierarchy_separator(self):
        category = "Ignition Timing / Knock Control / Thresholds"
        self.assertEqual(presentation.category_name(category), category)
        self.assertEqual(
            presentation.romraider_category_name(category),
            "Ignition Timing//Knock Control//Thresholds",
        )

    def test_romraider_category_removes_confidence_suffixes(self):
        self.assertEqual(
            presentation.romraider_category_name(
                "Ignition Timing / Main (traced) (candidate)"
            ),
            "Ignition Timing//Main",
        )

    def test_definitions_remain_opt_out_without_a_presentation_policy(self):
        self.assertTrue(emit_def.presentation_default_emit({}))
        self.assertTrue(emit_def.table_emit_enabled({}, True))
        self.assertFalse(emit_def.table_emit_enabled({"emit": False}, True))

    def test_allowlist_policy_requires_an_explicit_table_opt_in(self):
        overrides = {"presentation": {"default_emit": False}}
        default = emit_def.presentation_default_emit(overrides)
        self.assertFalse(emit_def.table_emit_enabled({}, default))
        self.assertTrue(emit_def.table_emit_enabled({"emit": True}, default))

    def test_visibility_controls_reject_non_boolean_values(self):
        with self.assertRaisesRegex(SystemExit, "default_emit must be a boolean"):
            emit_def.presentation_default_emit(
                {"presentation": {"default_emit": "false"}}
            )
        with self.assertRaisesRegex(SystemExit, "emit must be a boolean"):
            emit_def.table_emit_enabled({"emit": 1}, False, "0000991a")

    def test_jk08a_defaults_visible_and_explicitly_hides_internal_maps(self):
        with open(ROOT / "defs" / "JK08A.overrides.toml", "rb") as source:
            overrides = tomllib.load(source)
        self.assertTrue(emit_def.map_switching_enabled(overrides))
        default = emit_def.presentation_default_emit(overrides)
        self.assertTrue(default)
        hidden_categories = {
            "Internal Calculations",
            "Diagnostics / Internal Calculations",
            "Electronic Throttle Control / Internal Coordinates",
            "Limiters / Rev Limit / Internal State",
            "Unidentified Calibrations",
        }
        explicitly_hidden = {
            address: entry
            for address, entry in overrides["table"].items()
            if entry.get("emit") is False
        }
        self.assertEqual(len(explicitly_hidden), 161)
        self.assertIn("000094b2", explicitly_hidden)
        self.assertTrue(all(
            entry.get("category") in hidden_categories
            for entry in explicitly_hidden.values()
        ))
        self.assertTrue(all(
            entry.get("emit") is False
            for entry in overrides["table"].values()
            if entry.get("category") in hidden_categories
        ))
        self.assertTrue(
            {"000126e4", "0001298c"} <= set(overrides["table"])
        )
        self.assertNotIn("axisview", overrides)

    def test_map_switching_visibility_requires_a_boolean(self):
        self.assertFalse(emit_def.map_switching_enabled({}))
        with self.assertRaisesRegex(
            SystemExit, "map_switching.enabled must be a boolean"
        ):
            emit_def.map_switching_enabled(
                {"map_switching": {"enabled": "true"}}
            )


class EmitDefSwitchTest(unittest.TestCase):
    def test_switch_rejects_state_with_wrong_byte_count(self):
        switch = {
            "name": "Test switch",
            "category": "Test",
            "storageaddress": "0x10000",
            "storagetype": "uint8",
            "sizex": "1",
            "endian": "big",
            "userlevel": "5",
            "state": [
                {"name": "Enabled", "data": "01"},
                {"name": "Disabled", "data": "00"},
            ],
        }
        switch["state"][1]["data"] = "00 00"
        with self.assertRaisesRegex(SystemExit, "1 hexadecimal bytes"):
            emit_def.switch_xml(switch, 2)


class EmitDefDtcSwitchTest(unittest.TestCase):
    def test_dtc_manifest_emits_paired_descriptor_attribute_switches(self):
        switches = emit_def.dtc_switches("JK08A")
        self.assertEqual(len(switches), 71)
        self.assertEqual(len({switch["name"] for switch in switches}), 71)
        self.assertEqual({switch["category"] for switch in switches},
                         {"Diagnostics / DTC"})

        p0420_descriptor = next(
            switch for switch in switches
            if switch["name"] == "DTC P0420 [index 17] - 1/2 Descriptor"
        )
        p0420_attribute = next(
            switch for switch in switches
            if switch["name"] == "DTC P0420 [index 17] - 2/2 Attribute"
        )
        self.assertEqual(p0420_descriptor["storageaddress"], "0x1942C")
        self.assertEqual(p0420_descriptor["storagetype"], "uint8")
        self.assertEqual(p0420_descriptor["sizey"], "12")
        self.assertEqual(
            p0420_descriptor["state"],
            [
                {
                    "name": "Enabled (Stock)",
                    "data": "06 06 0C 00 00 00 04 20 10 00 00 00",
                },
                {
                    "name": "Disabled",
                    "data": "00 00 00 00 00 00 00 00 00 00 00 00",
                },
            ],
        )
        self.assertEqual(p0420_attribute["storageaddress"], "0x1603A")
        self.assertEqual(p0420_attribute["storagetype"], "uint8")
        self.assertEqual(p0420_attribute["sizey"], "2")
        self.assertEqual(
            p0420_attribute["state"],
            [
                {"name": "Enabled (Stock)", "data": "00 A0"},
                {"name": "Disabled", "data": "00 00"},
            ],
        )

    def test_p1610_emits_only_descriptor_switch(self):
        switches = emit_def.dtc_switches("JK08A")
        p1610 = [
            switch for switch in switches
            if switch["name"].startswith("DTC P1610 [index 40]")
        ]
        self.assertEqual(len(p1610), 1)
        self.assertEqual(
            p1610[0]["name"],
            "DTC P1610 [index 40] - Descriptor",
        )
        self.assertEqual(p1610[0]["storageaddress"], "0x19540")
        self.assertEqual(
            p1610[0]["state"][0]["data"],
            "0D 05 00 00 00 00 16 10 00 00 00 00",
        )

    def test_tracked_xml_contains_exact_generated_dtc_switches(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        switches = {
            table.get("name"): table
            for table in rom.findall("./table")
            if table.get("type") == "Switch"
        }
        expected = {
            switch["name"]: switch
            for switch in emit_def.dtc_switches("JK08A")
        }
        actual = {
            name: table for name, table in switches.items()
            if table.get("category") == ROMRAIDER_DTC_CATEGORY
        }
        self.assertEqual(set(actual), set(expected))
        self.assertEqual(len(actual), 71)
        self.assertEqual(
            set(switches) - set(actual),
            {
                "Developer Immobilizer",
                "Rolling Launch Require Accelerator Pedal",
            },
        )
        for name, entry in expected.items():
            node = actual[name]
            self.assertEqual(node.get("storageaddress"), entry["storageaddress"])
            self.assertEqual(node.get("storagetype"), entry["storagetype"])
            self.assertEqual(node.get("sizey"), entry["sizey"])
            self.assertEqual(
                [
                    {"name": state.get("name"), "data": state.get("data")}
                    for state in node.findall("./state")
                ],
                entry["state"],
            )
        self.assertEqual(
            [
                table.get("name") for table in rom.findall("./table")
                if table.get("type") == "3D"
                and table.get("category") == ROMRAIDER_DTC_CATEGORY
            ],
            [],
        )

    def test_tracked_xml_exposes_default_visible_inventory(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        tuner_items = {
            table.get("name"): table
            for table in rom.findall("./table")
            if table.get("category") != ROMRAIDER_DTC_CATEGORY
        }
        categories = {
            table.get("category") for table in rom.findall("./table")
        }
        expected = dict(COMMON_TABLES)
        expected.update(DEFAULT_VISIBLE_TABLES)
        expected.update({
            slot_name(slot, name): category
            for slot in range(1, 6)
            for name, category in SLOT_TABLES.items()
        })
        self.assertEqual(set(tuner_items), set(expected))
        for name, category in expected.items():
            with self.subTest(name=name):
                self.assertEqual(
                    tuner_items[name].get("category"),
                    romraider_category(category),
                )
        self.assertEqual(
            categories,
            {romraider_category(value) for value in expected.values()}
            | {ROMRAIDER_DTC_CATEGORY},
        )
        self.assertTrue(all(
            "(candidate)" not in category and "(traced)" not in category
            for category in categories
        ))

    def test_tracked_xml_has_one_rolling_launch_bitwise_switch(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        switches = [
            table
            for table in rom.findall("./table")
            if table.get("type") == "BitwiseSwitch"
        ]
        self.assertEqual(len(switches), 1)
        switch = switches[0]
        self.assertEqual(switch.get("name"), "Rolling Launch Enable by Map")
        self.assertEqual(switch.get("storageaddress"), "0xD3F64")
        self.assertEqual(
            [
                (bit.get("name"), bit.get("position"))
                for bit in switch.findall("./bit")
            ],
            [
                (f"Map {slot} - Rolling Launch Enable", str(slot - 1))
                for slot in range(1, 6)
            ],
        )
        self.assertNotIn(
            "Rolling Launch Enable Mask (Raw)",
            {table.get("name") for table in rom.findall("./table")},
        )

    def test_tracked_xml_has_rolling_launch_activation_controls(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        by_name = {
            table.get("name"): table for table in rom.findall("./table")
        }
        expected = {
            "Rolling Launch Minimum Coolant Temperature": "0xD3F66",
            "Rolling Launch Minimum Vehicle Speed": "0xD3F68",
            "Rolling Launch Minimum Retard Ramp Width": "0xD3F69",
            "Rolling Launch Minimum Engine Speed": "0xD3F6A",
            "Rolling Launch Require Accelerator Pedal": "0xD3F6C",
            "Rolling Launch RPM Offset": "0xD3F6E",
            "Rolling Launch Minimum RPM Hysteresis": "0xD3F70",
            "Rolling Launch Maximum RPM Hysteresis": "0xD3F71",
            "Rolling Launch RPM Hysteresis Ratio (%)": "0xD3F7B",
        }
        for name, address in expected.items():
            with self.subTest(name=name):
                self.assertEqual(by_name[name].get("storageaddress"), address)
        pedal = by_name["Rolling Launch Require Accelerator Pedal"]
        self.assertEqual(pedal.get("type"), "Switch")
        self.assertEqual(
            [state.get("data") for state in pedal.findall("./state")],
            ["00 01", "00 00"],
        )

    def test_tracked_fuel_targets_use_gasoline_afr_scaling(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        table = next(
            table for table in rom.findall("./table")
            if table.get("name") == slot_name(1, "Fuel Targets")
        )
        scale = table.find("./scaling")
        self.assertEqual(scale.get("units"), "AFR (gasoline scale) [cand]")
        self.assertEqual(scale.get("expression"), "1881.6/x")
        self.assertEqual(scale.get("to_byte"), "1881.6/x")
        self.assertEqual(scale.get("format"), "0.00")

    def test_tracked_ignition_trim_is_labeled_as_relative_adjustment(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        by_name = {
            table.get("name"): table
            for table in rom.findall("./table")
        }
        for name in (
            "Ignition Timing Trim Cold",
            slot_name(1, "Ignition Timing Trim Main"),
            slot_name(1, "Ignition Timing Trim High Det"),
        ):
            with self.subTest(name=name):
                table = by_name[name]
                scale = table.find("./scaling")
                self.assertEqual(table.get("mask"), "7F")
                self.assertEqual(
                    scale.get("units"),
                    "Timing adjustment (deg) [cand]",
                )
                self.assertEqual(scale.get("expression"), "x-64")
                self.assertEqual(scale.get("to_byte"), "x+64")

    def test_internal_tables_remain_outside_the_working_definition(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        addresses = {
            table.get("storageaddress")
            for table in rom.findall("./table")
            if table.get("type") != "Switch"
        }
        self.assertTrue({
            "0xAB0A",
            "0xB23A",
            "0x11F6A",
            "0x120BE",
            "0x121A6",
            "0x14E52",
        }.isdisjoint(addresses))

    def test_timing_state_addends_reach_the_working_definition(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        by_address = {
            table.get("storageaddress"): table
            for table in rom.findall("./table")
            if table.get("type") != "Switch"
        }
        expected = {
            "0x12196": slot_name(
                1,
                "Default/Post-Transition Timing-State Addend "
                "(x-128) (0x12196)",
            ),
            "0x1219E": slot_name(
                1,
                "Warm DFCO-Transition Timing-State Addend "
                "(x-128) (0x1219E)",
            ),
        }
        for address, name in expected.items():
            with self.subTest(address=address):
                table = by_address[address]
                self.assertEqual(table.get("name"), name)
                self.assertEqual(
                    table.get("category"),
                    "Ignition Timing//State Accumulators",
                )
                scale = table.find("./scaling")
                self.assertEqual(
                    scale.get("units"),
                    "Timing-state count",
                )
                self.assertEqual(scale.get("expression"), "x-128")
                self.assertEqual(scale.get("to_byte"), "x+128")
                axis = table.find("./table[@type='Static X Axis']")
                self.assertEqual(
                    axis.get("name"),
                    "Engine Speed [RPM] (Candidate)",
                )
                self.assertEqual(
                    [int(cell.text) for cell in axis.findall("./data")],
                    [0, 400, 800, 1200, 1600, 2000, 2400, 2800],
                )

        self.assertNotIn("0x121A6", by_address)

    def test_default_visible_tables_reach_the_working_definition(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        addresses = {
            table.get("storageaddress")
            for table in rom.findall("./table")
            if table.get("type") != "Switch"
        }
        self.assertTrue({
            "0x08FDC",
            "0x0911C",
            "0x10F8E",
            "0x124D2",
        } <= addresses)

    def test_maf_tables_use_reviewed_candidate_voltage_axes(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        by_name = {
            table.get("name"): table
            for table in rom.findall("./table")
        }
        for name in (
            "MAF Sensor Scaling Bank 1",
            "MAF Sensor Scaling Bank 2",
        ):
            with self.subTest(name=name):
                table = by_name[name]
                axis = table.find("./table[@type='Static X Axis']")
                self.assertEqual(
                    axis.get("name"), "MAF Sensor Voltage [V, cand]"
                )
                values = [float(node.text) for node in axis.findall("./data")]
                self.assertEqual(len(values), 64)
                self.assertEqual(values[0], 0.0)
                self.assertEqual(values[-1], 5.04)

    def test_dfco_thresholds_use_coolant_axis_and_code_rpm_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        expected = {
            slot_name(1, "DFCO Hold RPM Threshold"): "0x126E4",
            slot_name(1, "DFCO Entry RPM Threshold"): "0x12718",
            slot_name(1, "DFCO Full Restore RPM Threshold"): "0x12818",
            slot_name(1, "DFCO Low-Speed Intermediate Restore RPM Threshold"):
                "0x1298C",
        }
        for name, address in expected.items():
            with self.subTest(name=name):
                table = next(
                    node for node in rom.findall("./table")
                    if node.get("name") == name
                )
                scaling = table.find("./scaling")
                axis = table.find("./table[@type='Static X Axis']")
                self.assertEqual(table.get("storageaddress"), address)
                self.assertEqual(table.get("storagetype"), "uint8")
                self.assertEqual(table.get("sizex"), "16")
                self.assertEqual(scaling.get("units"), "RPM")
                self.assertEqual(scaling.get("expression"), "x*25")
                self.assertEqual(
                    [node.text for node in axis.findall("./data")],
                    [
                        "-40", "-30", "-20", "-10", "0", "10", "20", "30",
                        "40", "50", "60", "70", "80", "90", "100", "110",
                    ],
                )

    def test_working_fuel_cut_uses_exact_2x2_layout_and_code_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        table = next(
            table for table in rom.findall("./table")
            if table.get("name") == slot_name(1, "Rev Limit - Fuel Cut")
        )
        scaling = table.find("./scaling")
        axis_x = table.find("./table[@type='Static X Axis']")
        axis_y = table.find("./table[@type='Static Y Axis']")
        self.assertEqual(table.get("storageaddress"), "0x0934E")
        self.assertEqual(table.get("storagetype"), "uint16")
        self.assertEqual(table.get("sizex"), "2")
        self.assertEqual(table.get("sizey"), "2")
        self.assertEqual(scaling.get("units"), "RPM")
        self.assertEqual(scaling.get("expression"), "x*12.5")
        self.assertEqual(
            [node.text for node in axis_x.findall("./data")],
            ["Normal", "Reverse"],
        )
        self.assertEqual(
            [node.text for node in axis_y.findall("./data")],
            ["Cut", "Restore"],
        )

    def test_throttle_rev_limiter_uses_exact_scalar_and_candidate_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        table = next(
            table for table in rom.findall("./table")
            if table.get("name") == slot_name(
                1, "Rev Limit - Throttle Cut"
            )
        )
        scaling = table.find("./scaling")
        self.assertEqual(table.get("storageaddress"), "0x0942C")
        self.assertEqual(table.get("storagetype"), "uint16")
        self.assertEqual(table.get("sizex"), "1")
        self.assertEqual(scaling.get("units"), "RPM [cand]")
        self.assertEqual(scaling.get("expression"), "x*0.78125")


if __name__ == "__main__":
    unittest.main()
