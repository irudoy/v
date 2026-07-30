import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.mapkit import emit_def


ROOT = Path(__file__).resolve().parents[3]


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
            'category="Ignition Timing / Knock Control"',
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
        self.assertEqual(len(switches), 57)
        self.assertEqual(len({switch["name"] for switch in switches}), 57)
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
            if table.get("category") == "Diagnostics / DTC"
        }
        self.assertEqual(set(actual), set(expected))
        self.assertEqual(len(actual), 57)
        self.assertEqual(set(switches) - set(actual), {"Developer Immobilizer"})
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
                and table.get("category") == "Diagnostics / DTC"
            ],
            [],
        )

    def test_tracked_xml_uses_functional_categories(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        tables = {
            table.get("name"): table
            for table in rom.findall("./table")
        }
        categories = {
            table.get("category") for table in tables.values()
        }
        self.assertEqual(len(categories), 20)
        self.assertTrue(all(
            "(candidate)" not in category and "(traced)" not in category
            for category in categories
        ))

        expected = {
            "Developer Immobilizer": "NATS / Immobilizer",
            "Target AFR - Power (0xB33A)": "AFR / Lambda",
            "Dual-Channel Contribution Curve B - MAF candidate (0x141F4)": "Airflow",
            "Cold Ignition Timing Map (0x991A)": "Ignition Timing / Main",
            "Stationary Rev Limiter - Fuel Cut/Restore (0x85D9)": (
                "Limiters / Stationary Rev Limiter"
            ),
            "Stationary Rev Limiter Readiness Threshold (0x911C)": (
                "Limiters / Stationary Rev Limiter"
            ),
            "Stationary Rev Limiter Accumulator Step (0x124D2)": (
                "Limiters / Stationary Rev Limiter"
            ),
            "Over Run Fuel Cut - JECS/Hitachi (0x12718)": (
                "Fuel Delivery / Fuel Cut / Main"
            ),
            "Over Run Fuel Restore - JECS/Hitachi (0x12818)": (
                "Fuel Delivery / Fuel Cut / Main"
            ),
            "Rev Limit - Fuel Cut (0x934E)": (
                "Fuel Delivery / Fuel Cut / Main"
            ),
            "Accelerator Pedal High-State Hysteresis (0x8FDC)": (
                "Throttle / Accelerator Pedal / Thresholds"
            ),
            "Throttle Rev Limiter (0x942C)": "Limiters",
            "Engine Speed Axis [RPM] (ref)": "Reference Axes",
            "Cylinder Filling Axis [%] (ref)": "Reference Axes",
        }
        for name, category in expected.items():
            with self.subTest(name=name):
                self.assertEqual(tables[name].get("category"), category)

    def test_stationary_limiter_readiness_uses_exact_scalar_and_code_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        table = next(
            table for table in rom.findall("./table")
            if table.get("name") == (
                "Stationary Rev Limiter Readiness Threshold (0x911C)"
            )
        )
        scaling = table.find("./scaling")
        self.assertEqual(table.get("storageaddress"), "0x0911C")
        self.assertEqual(table.get("storagetype"), "uint16")
        self.assertEqual(table.get("sizex"), "1")
        self.assertEqual(scaling.get("units"), "accumulator counts")
        self.assertEqual(scaling.get("expression"), "x")

    def test_overrun_fuel_cut_uses_coolant_axis_and_code_rpm_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        expected = {
            "Over Run Fuel Cut - Bosch (0x126E4)": "0x126E4",
            "Over Run Fuel Cut - JECS/Hitachi (0x12718)": "0x12718",
            "Over Run Fuel Restore - JECS/Hitachi (0x12818)": "0x12818",
            "Over Run Fuel Restore - Bosch (0x1298C)": "0x1298C",
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

    def test_working_fuel_cut_uses_exact_2x2_layout_and_candidate_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        table = next(
            table for table in rom.findall("./table")
            if table.get("name") == "Rev Limit - Fuel Cut (0x934E)"
        )
        scaling = table.find("./scaling")
        axis_x = table.find("./table[@type='Static X Axis']")
        axis_y = table.find("./table[@type='Static Y Axis']")
        self.assertEqual(table.get("storageaddress"), "0x0934E")
        self.assertEqual(table.get("storagetype"), "uint16")
        self.assertEqual(table.get("sizex"), "2")
        self.assertEqual(table.get("sizey"), "2")
        self.assertEqual(scaling.get("units"), "RPM [cand]")
        self.assertEqual(scaling.get("expression"), "x*12.5")
        self.assertEqual(
            [node.text for node in axis_x.findall("./data")],
            ["Normal", "Reverse"],
        )
        self.assertEqual(
            [node.text for node in axis_y.findall("./data")],
            ["Cut", "Restore"],
        )

    def test_accelerator_pedal_hysteresis_uses_raw_code_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        table = next(
            table for table in rom.findall("./table")
            if table.get("name") == (
                "Accelerator Pedal High-State Hysteresis (0x8FDC)"
            )
        )
        scaling = table.find("./scaling")
        axis = table.find("./table[@type='Static X Axis']")
        self.assertEqual(table.get("storageaddress"), "0x08FDC")
        self.assertEqual(table.get("storagetype"), "uint16")
        self.assertEqual(table.get("sizex"), "2")
        self.assertEqual(scaling.get("units"), "normalized ADC counts")
        self.assertEqual(scaling.get("expression"), "x")
        self.assertEqual(
            [node.text for node in axis.findall("./data")],
            ["activate", "release"],
        )

    def test_throttle_rev_limiter_uses_exact_scalar_and_candidate_scale(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        table = next(
            table for table in rom.findall("./table")
            if table.get("name") == "Throttle Rev Limiter (0x942C)"
        )
        scaling = table.find("./scaling")
        self.assertEqual(table.get("storageaddress"), "0x0942C")
        self.assertEqual(table.get("storagetype"), "uint16")
        self.assertEqual(table.get("sizex"), "1")
        self.assertEqual(scaling.get("units"), "RPM [cand]")
        self.assertEqual(scaling.get("expression"), "x*0.78125")


if __name__ == "__main__":
    unittest.main()
