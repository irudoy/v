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
    def test_dtc_manifest_emits_only_contiguous_p1610_switch(self):
        switches = emit_def.dtc_switches("JK08A")
        self.assertEqual(len(switches), 1)
        switch = switches[0]
        self.assertEqual(switch["name"], "DTC P1610 (NATS LOCK MODE)")
        self.assertEqual(switch["storageaddress"], "0x19540")
        self.assertEqual(switch["sizey"], "12")
        self.assertNotIn("sizex", switch)
        self.assertEqual(
            switch["state"][0]["data"],
            "0D 05 00 00 00 00 16 10 00 00 00 00",
        )
        self.assertEqual(
            switch["state"][1]["data"],
            "00 00 00 00 00 00 00 00 00 00 00 00",
        )

    def test_multibyte_switch_uses_sizey_and_preserves_state_bytes(self):
        switch = emit_def.dtc_switches("JK08A")[0]
        xml = "\n".join(emit_def.switch_xml(switch, 2))
        self.assertIn('type="Switch"', xml)
        self.assertIn('storageaddress="0x19540"', xml)
        self.assertIn('sizey="12"', xml)
        self.assertNotIn('sizex=', xml)
        self.assertIn(
            'data="0D 05 00 00 00 00 16 10 00 00 00 00"',
            xml,
        )

    def test_switch_rejects_state_with_wrong_byte_count(self):
        switch = emit_def.dtc_switches("JK08A")[0]
        switch["state"][1]["data"] = "00"
        with self.assertRaisesRegex(SystemExit, "12 hexadecimal bytes"):
            emit_def.switch_xml(switch, 2)

    def test_tracked_xml_contains_exact_generated_p1610_switch(self):
        rom = ET.parse(ROOT / "defs" / "JK08A.xml").getroot().find("./rom")
        switches = {
            table.get("name"): table
            for table in rom.findall("./table")
            if table.get("type") == "Switch"
        }
        self.assertEqual(
            set(switches),
            {"Developer Immobilizer", "DTC P1610 (NATS LOCK MODE)"},
        )
        p1610 = switches["DTC P1610 (NATS LOCK MODE)"]
        self.assertEqual(p1610.get("storageaddress"), "0x19540")
        self.assertEqual(p1610.get("sizey"), "12")
        states = {
            state.get("name"): state.get("data")
            for state in p1610.findall("./state")
        }
        self.assertEqual(
            states,
            {
                "Enabled (Stock)": "0D 05 00 00 00 00 16 10 00 00 00 00",
                "Disabled": "00 00 00 00 00 00 00 00 00 00 00 00",
            },
        )


if __name__ == "__main__":
    unittest.main()
