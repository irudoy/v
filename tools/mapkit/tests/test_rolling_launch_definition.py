from copy import deepcopy
from pathlib import Path
import tomllib
import unittest
import xml.etree.ElementTree as ET

from patches import rolling_launch_layout
from tools.mapkit import emit_def, rolling_launch, tunerpro


ROOT = Path(__file__).resolve().parents[3]


class RollingLaunchDefinitionProjectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = rolling_launch_layout.load_layout()
        with open(
            ROOT / "defs" / "JK08A.overrides.toml", "rb"
        ) as source:
            cls.overrides = tomllib.load(source)
        cls.maps = {
            "00001000": {
                "addr": "00001000",
                "family": "direct-scalar",
                "dims": 1,
                "width": 1,
                "height": None,
                "storagetype": "uint8",
                "confidence": "code",
                "role": "table",
                "semantics": "Unrelated source calibration",
                "units": "raw",
                "scale_expr": "x",
                "to_byte": "x",
                "scale_conf": "code",
                "note": "",
                "wrappers": [],
                "kernels": [],
                "steps": [],
                "accessors": [],
                "resolver_kinds": [],
                "axis_x": [],
                "axis_y": [],
                "diagnostic_bindings": [],
            }
        }
        cls.axes = {}

    def project(self):
        return rolling_launch.project_definition_model(
            self.maps, self.overrides, self.layout
        )

    def test_projection_uses_exact_configuration_addresses(self):
        projection = self.project()
        self.assertEqual(projection.configuration_address, "000d3f60")
        self.assertEqual(projection.enable_mask_address, "000d3f64")
        self.assertEqual(projection.coolant_min_address, "000d3f66")
        self.assertEqual(projection.min_speed_address, "000d3f68")
        self.assertEqual(projection.retard_ramp_address, "000d3f69")
        self.assertEqual(projection.min_rpm_address, "000d3f6a")
        self.assertEqual(projection.pedal_requirement_address, "000d3f6c")
        self.assertEqual(projection.rpm_offset_address, "000d3f6e")
        self.assertEqual(projection.hysteresis_address, "000d3f70")
        self.assertEqual(projection.table_count, 6)
        self.assertEqual(projection.masked_view_count, 0)
        self.assertEqual(projection.switch_count, 1)
        self.assertEqual(projection.bitwise_switch_count, 1)
        self.assertEqual(projection.enable_bit_count, 5)
        self.assertEqual(projection.editor_view_count, 8)

    def test_projection_exposes_activation_and_rpm_controls(self):
        projection = self.project()
        expected = {
            projection.coolant_min_address: (
                "uint8",
                "deg C",
                "x*0.625-40",
                "Rolling Launch Minimum Coolant Temperature",
            ),
            projection.min_speed_address: (
                "uint8",
                "km/h",
                "x*2",
                "Rolling Launch Minimum Vehicle Speed",
            ),
            projection.retard_ramp_address: (
                "uint8",
                "RPM",
                "x*12.5",
                "Rolling Launch Retard Ramp Width",
            ),
            projection.min_rpm_address: (
                "uint16",
                "RPM",
                "x*12.5",
                "Rolling Launch Minimum Engine Speed",
            ),
            projection.rpm_offset_address: (
                "uint16",
                "RPM",
                "x*12.5",
                "Rolling Launch RPM Offset",
            ),
        }
        for address, values in expected.items():
            with self.subTest(address=address):
                model = projection.maps[address]
                presentation = projection.overrides["table"][address]
                self.assertEqual(model["storagetype"], values[0])
                self.assertEqual(model["units"], values[1])
                self.assertEqual(model["scale_expr"], values[2])
                self.assertEqual(presentation["name"], values[3])

    def test_projection_exposes_hysteresis_in_rpm(self):
        projection = self.project()
        model = projection.maps[projection.hysteresis_address]
        presentation = projection.overrides["table"][
            projection.hysteresis_address
        ]
        self.assertEqual(model["storagetype"], "uint16")
        self.assertEqual(model["units"], "RPM")
        self.assertEqual(model["scale_expr"], "x*12.5")
        self.assertEqual(model["to_byte"], "x/12.5")
        self.assertEqual(
            presentation["name"], "Rolling Launch RPM Hysteresis"
        )
        self.assertEqual(
            presentation["category"], "Rolling Launch / RPM Hold"
        )

    def test_projection_exposes_one_bitwise_switch_with_one_bit_per_map(self):
        projection = self.project()
        switches = [
            entry
            for entry in projection.overrides["bitwise_switch"]
            if entry["storageaddress"] == "0xD3F64"
        ]
        self.assertEqual(len(switches), 1)
        self.assertNotIn(projection.enable_mask_address, projection.maps)
        bits = switches[0]["bit"]
        self.assertEqual(
            [bit["name"] for bit in bits],
            [
                f"Map {slot} - Rolling Launch Enable"
                for slot in range(1, 6)
            ],
        )
        self.assertEqual(
            [bit["position"] for bit in bits],
            [0, 1, 2, 3, 4],
        )

    def test_projection_preserves_source_models(self):
        maps = deepcopy(self.maps)
        overrides = deepcopy(self.overrides)
        rolling_launch.project_definition_model(
            maps, overrides, self.layout
        )
        self.assertEqual(maps, self.maps)
        self.assertEqual(overrides, self.overrides)

    def test_romraider_and_tunerpro_use_native_bitwise_controls(self):
        projection = self.project()
        switches = emit_def.bitwise_switches(projection.overrides)
        self.assertEqual(len(switches), 1)
        romraider = "\n".join(
            emit_def.bitwise_switch_xml(switches[0], 1)
        )
        self.assertIn('type="BitwiseSwitch"', romraider)
        self.assertIn('name="Rolling Launch Enable by Map"', romraider)
        self.assertIn('storageaddress="0xD3F64"', romraider)
        self.assertEqual(romraider.count("<bit "), 5)
        self.assertIn(
            '<bit name="Map 4 - Rolling Launch Enable" position="3"/>',
            romraider,
        )

        image = bytearray([0xFF] * 0x100000)
        xdf, stats = tunerpro.render(
            "JK08A",
            image,
            [],
            self.axes,
            projection.overrides,
            {},
            [],
            [],
            switches,
        )
        self.assertEqual(stats["calibration_tables"], 0)
        self.assertEqual(stats["masked_views"], 0)
        self.assertEqual(stats["bitwise_flags"], 5)
        root = ET.fromstring(xdf)
        flags = root.findall("./XDFFLAG")
        self.assertEqual(len(flags), 5)
        self.assertEqual(
            [flag.findtext("./title") for flag in flags],
            [
                f"Map {slot} - Rolling Launch Enable"
                for slot in range(1, 6)
            ],
        )
        self.assertEqual(
            [flag.findtext("./mask") for flag in flags],
            ["0x01", "0x02", "0x04", "0x08", "0x10"],
        )
        self.assertTrue(all(
            flag.find("./EMBEDDEDDATA").get("mmedaddress") == "0xD3F64"
            for flag in flags
        ))

    def test_romraider_and_tunerpro_use_a_reversible_pedal_switch(self):
        projection = self.project()
        switches = [
            entry
            for entry in projection.overrides["switch"]
            if entry["storageaddress"] == "0xD3F6C"
        ]
        self.assertEqual(len(switches), 1)
        pedal = switches[0]
        self.assertEqual(
            [state["data"] for state in pedal["state"]],
            ["00 01", "00 00"],
        )
        romraider = "\n".join(emit_def.switch_xml(pedal, 1))
        self.assertIn('type="Switch"', romraider)
        self.assertIn(
            'name="Rolling Launch Require Accelerator Pedal"', romraider
        )
        self.assertIn('storageaddress="0xD3F6C"', romraider)

        image = bytearray([0xFF] * 0x100000)
        xdf, stats = tunerpro.render(
            "JK08A",
            image,
            [],
            self.axes,
            projection.overrides,
            {},
            [],
            switches,
        )
        self.assertEqual(stats["other_patches"], 1)
        root = ET.fromstring(xdf)
        patch = root.find("./XDFPATCH")
        self.assertEqual(
            patch.findtext("./title"),
            "Rolling Launch Require Accelerator Pedal",
        )
        entry = patch.find("./XDFPATCHENTRY")
        self.assertEqual(entry.get("address"), "0xD3F6C")
        self.assertEqual(entry.get("basedata"), "0001")
        self.assertEqual(entry.get("patchdata"), "0000")

    def test_romraider_and_tunerpro_render_hysteresis_at_exact_address(self):
        projection = self.project()
        model = projection.maps[projection.hysteresis_address]
        romraider = "\n".join(
            emit_def.table_xml(
                model, projection.overrides, self.axes, "JK08A"
            )
        )
        self.assertIn(
            'name="Rolling Launch RPM Hysteresis"', romraider
        )
        self.assertIn('storageaddress="0xD3F70"', romraider)
        self.assertIn('units="RPM"', romraider)
        self.assertIn('expression="x*12.5"', romraider)
        self.assertIn('to_byte="x/12.5"', romraider)

        image = bytearray([0xFF] * 0x100000)
        xdf, stats = tunerpro.render(
            "JK08A",
            image,
            [model],
            self.axes,
            projection.overrides,
            {},
            [],
            [],
        )
        self.assertEqual(stats["calibration_tables"], 1)
        self.assertIn("Rolling Launch RPM Hysteresis", xdf)
        self.assertIn('mmedaddress="0xD3F70"', xdf)
        self.assertIn('equation="X*12.5"', xdf)

    def test_romraider_and_tunerpro_render_retard_ramp_at_exact_address(self):
        projection = self.project()
        model = projection.maps[projection.retard_ramp_address]
        romraider = "\n".join(
            emit_def.table_xml(
                model, projection.overrides, self.axes, "JK08A"
            )
        )
        self.assertIn(
            'name="Rolling Launch Retard Ramp Width"', romraider
        )
        self.assertIn('storageaddress="0xD3F69"', romraider)
        self.assertIn('units="RPM"', romraider)
        self.assertIn('expression="x*12.5"', romraider)

        image = bytearray([0xFF] * 0x100000)
        xdf, stats = tunerpro.render(
            "JK08A",
            image,
            [model],
            self.axes,
            projection.overrides,
            {},
            [],
            [],
        )
        self.assertEqual(stats["calibration_tables"], 1)
        self.assertIn("Rolling Launch Retard Ramp Width", xdf)
        self.assertIn('mmedaddress="0xD3F69"', xdf)
        self.assertIn('equation="X*12.5"', xdf)

    def test_common_definition_applies_both_projections(self):
        self.assertTrue(emit_def.rolling_launch_enabled(self.overrides))

    def test_projection_rejects_address_collision(self):
        maps = deepcopy(self.maps)
        maps["000d3f64"] = deepcopy(maps["00001000"])
        maps["000d3f64"]["addr"] = "000d3f64"
        with self.assertRaisesRegex(ValueError, "collides"):
            rolling_launch.project_definition_model(
                maps, self.overrides, self.layout
            )

    def test_projection_rejects_hysteresis_address_collision(self):
        maps = deepcopy(self.maps)
        maps["000d3f70"] = deepcopy(maps["00001000"])
        maps["000d3f70"]["addr"] = "000d3f70"
        with self.assertRaisesRegex(ValueError, "collides"):
            rolling_launch.project_definition_model(
                maps, self.overrides, self.layout
            )

    def test_projection_rejects_activation_control_address_collision(self):
        maps = deepcopy(self.maps)
        maps["000d3f68"] = deepcopy(maps["00001000"])
        maps["000d3f68"]["addr"] = "000d3f68"
        with self.assertRaisesRegex(ValueError, "collides"):
            rolling_launch.project_definition_model(
                maps, self.overrides, self.layout
            )


if __name__ == "__main__":
    unittest.main()
