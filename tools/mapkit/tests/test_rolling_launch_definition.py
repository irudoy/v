from copy import deepcopy
from pathlib import Path
import tomllib
import unittest
import xml.etree.ElementTree as ET

from patches import rolling_launch_layout
from tools.mapkit import emit_def, rolling_launch, tunerpro


ROOT = Path(__file__).resolve().parents[3]
# Offsets and widths of the unsigned schema-5 head fields that the editors show.
FIELD_OFFSETS = {
    "coolant_min": 0x06, "min_speed": 0x08, "max_speed": 0x0A,
    "min_rpm_native": 0x0C, "window_width": 0x12, "window_top": 0x13,
    "u_rate_limit": 0x14, "integrator_limit": 0x18,
    "abort_above": 0x1A, "abort_below": 0x1B,
    "rpm_ceiling_offset_native": 0x1C, "speed_frame_age_limit": 0x22,
    "rpm_ceiling_hysteresis_native": 0x23,
}
FIELD_WIDTHS = {
    "coolant_min": 1, "min_speed": 2, "max_speed": 2,
    "min_rpm_native": 2, "window_width": 1, "window_top": 1,
    "u_rate_limit": 2, "integrator_limit": 2,
    "abort_above": 1, "abort_below": 1,
    "rpm_ceiling_offset_native": 2, "speed_frame_age_limit": 1,
    "rpm_ceiling_hysteresis_native": 1,
}


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
        self.assertEqual(projection.configuration_address, "000d6220")
        self.assertEqual(projection.enable_mask_address, "000d6224")
        self.assertEqual(projection.pedal_requirement_address, "000d622e")
        self.assertEqual(dict(projection.control_addresses), {
            "coolant_min": "000d6226",
            "min_speed": "000d6228",
            "max_speed": "000d622a",
            "min_rpm_native": "000d622c",
            "speed_frame_age_limit": "000d6242",
            "window_width": "000d6232",
            "window_top": "000d6233",
            "u_rate_limit": "000d6234",
            "integrator_limit": "000d6238",
            "abort_above": "000d623a",
            "abort_below": "000d623b",
            "rpm_ceiling_offset_native": "000d623c",
            "rpm_ceiling_hysteresis_native": "000d6243",
        })
        self.assertEqual(projection.table_count, 13)
        self.assertEqual(projection.masked_view_count, 0)
        self.assertEqual(projection.switch_count, 1)
        self.assertEqual(projection.bitwise_switch_count, 1)
        self.assertEqual(projection.enable_bit_count, 5)
        self.assertEqual(projection.editor_view_count, 15)

    def test_controls_match_the_record_layout(self):
        projection = self.project()
        start = int(projection.configuration_address, 16)
        for control in rolling_launch.CONTROLS:
            with self.subTest(control=control.key):
                # The field order of the reference record fixes each offset.
                width = 2 if control.storagetype == "uint16" else 1
                offset = FIELD_OFFSETS[control.key]
                self.assertEqual(control.offset, offset)
                self.assertEqual(width, FIELD_WIDTHS[control.key])
                self.assertEqual(
                    projection.address(control.key), f"{start + offset:08x}"
                )

    def test_target_label_is_independent_from_layout_rom(self):
        projection = rolling_launch.project_definition_model(
            self.maps,
            self.overrides,
            self.layout,
            target_rom="JK00A",
        )
        enable = projection.overrides["bitwise_switch"][-1]
        pedal = projection.overrides["switch"][-1]

        self.assertEqual(projection.configuration_address, "000d6220")
        self.assertIn("Exact JK00A.", enable["description"])
        self.assertIn("Exact JK00A.", pedal["description"])
        self.assertNotIn("Exact JK08A.", enable["description"])
        self.assertNotIn("Exact JK08A.", pedal["description"])

    def test_projection_exposes_activation_and_controller_controls(self):
        projection = self.project()
        expected = {
            "coolant_min": (
                "uint8", "deg C", "x*0.625-40",
                "Rolling Launch Minimum Coolant Temperature",
            ),
            "min_speed": (
                "uint16", "km/h", "x/10",
                "Rolling Launch Minimum Vehicle Speed",
            ),
            "max_speed": (
                "uint16", "km/h", "x/10",
                "Rolling Launch Maximum Vehicle Speed",
            ),
            "min_rpm_native": (
                "uint16", "RPM", "x*12.5",
                "Rolling Launch Minimum Engine Speed",
            ),
            "speed_frame_age_limit": (
                "uint8", "ms", "x*10.24",
                "Rolling Launch Speed Frame Age Limit",
            ),
            "window_width": (
                "uint8", "km/h", "x/10",
                "Rolling Launch Speed Window Width",
            ),
            "u_rate_limit": (
                "uint16", "%", "x/10",
                "Rolling Launch Torque Fraction Rate Limit",
            ),
            "rpm_ceiling_offset_native": (
                "uint16", "RPM", "x*12.5",
                "Rolling Launch RPM Ceiling Offset",
            ),
            "rpm_ceiling_hysteresis_native": (
                "uint8", "RPM", "x*12.5",
                "Rolling Launch RPM Ceiling Hysteresis",
            ),
        }
        for key, values in expected.items():
            with self.subTest(control=key):
                address = projection.address(key)
                model = projection.maps[address]
                presentation = projection.overrides["table"][address]
                self.assertEqual(model["storagetype"], values[0])
                self.assertEqual(model["units"], values[1])
                self.assertEqual(model["scale_expr"], values[2])
                self.assertEqual(presentation["name"], values[3])

    def test_projection_exposes_one_bitwise_switch_with_one_bit_per_map(self):
        projection = self.project()
        switches = [
            entry
            for entry in projection.overrides["bitwise_switch"]
            if entry["storageaddress"] == "0xD6224"
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
        self.assertIn('storageaddress="0xD6224"', romraider)
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
            [flag.findtext("./mask") for flag in flags],
            ["0x01", "0x02", "0x04", "0x08", "0x10"],
        )
        self.assertTrue(all(
            flag.find("./EMBEDDEDDATA").get("mmedaddress") == "0xD6224"
            for flag in flags
        ))

    def test_romraider_and_tunerpro_use_a_reversible_pedal_switch(self):
        projection = self.project()
        switches = [
            entry
            for entry in projection.overrides["switch"]
            if entry["storageaddress"] == "0xD622E"
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
        self.assertIn('storageaddress="0xD622E"', romraider)

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
        entry = root.find("./XDFPATCH/XDFPATCHENTRY")
        self.assertEqual(entry.get("address"), "0xD622E")
        self.assertEqual(entry.get("basedata"), "0001")
        self.assertEqual(entry.get("patchdata"), "0000")

    def test_romraider_and_tunerpro_render_controller_tables(self):
        projection = self.project()
        models = [
            projection.maps[projection.address(key)]
            for key in ("window_width", "integrator_limit", "speed_frame_age_limit")
        ]
        romraider = "\n".join(
            line
            for model in models
            for line in emit_def.table_xml(
                model, projection.overrides, self.axes, "JK08A"
            )
        )
        self.assertIn('name="Rolling Launch Speed Window Width"', romraider)
        self.assertIn('storageaddress="0xD6232"', romraider)
        self.assertIn('storageaddress="0xD6238"', romraider)
        self.assertIn('storageaddress="0xD6242"', romraider)
        self.assertIn('expression="x/10"', romraider)
        self.assertIn('expression="x*10.24"', romraider)

        image = bytearray([0xFF] * 0x100000)
        xdf, stats = tunerpro.render(
            "JK08A",
            image,
            models,
            self.axes,
            projection.overrides,
            {},
            [],
            [],
        )
        self.assertEqual(stats["calibration_tables"], 3)
        self.assertIn('mmedaddress="0xD6232"', xdf)
        self.assertIn('mmedaddress="0xD6242"', xdf)
        self.assertIn('equation="X/10"', xdf)

    def test_common_definition_applies_both_projections(self):
        self.assertTrue(emit_def.rolling_launch_enabled(self.overrides))

    def test_projection_rejects_address_collisions(self):
        for address in ("000d6224", "000d622e", "000d6228", "000d6242"):
            with self.subTest(address=address):
                maps = deepcopy(self.maps)
                maps[address] = deepcopy(maps["00001000"])
                maps[address]["addr"] = address
                with self.assertRaisesRegex(ValueError, "collides"):
                    rolling_launch.project_definition_model(
                        maps, self.overrides, self.layout
                    )


if __name__ == "__main__":
    unittest.main()
