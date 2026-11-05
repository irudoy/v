from copy import deepcopy
from pathlib import Path
import tomllib
import unittest
import xml.etree.ElementTree as ET

from patches import rolling_launch_layout
from tools.mapkit import emit_def, rolling_launch, tunerpro


ROOT = Path(__file__).resolve().parents[3]
# Offsets and widths of the unsigned schema-6 head fields that the editors show.
FIELD_OFFSETS = {
    "coolant_min": 0x06, "min_speed": 0x08, "max_speed": 0x0A,
    "min_rpm_native": 0x0C, "window_width": 0x12, "window_top": 0x13,
    "u_rate_limit": 0x14, "integrator_limit": 0x18,
    "abort_above": 0x1A, "abort_below": 0x1B,
    "speed_frame_age_limit": 0x22,
}
FIELD_WIDTHS = {
    "coolant_min": 1, "min_speed": 2, "max_speed": 2,
    "min_rpm_native": 2, "window_width": 1, "window_top": 1,
    "u_rate_limit": 2, "integrator_limit": 2,
    "abort_above": 1, "abort_below": 1,
    "speed_frame_age_limit": 1,
}
# The schema-6 record starts at 0xD6320; its 12-byte slots start at +0x28.
SLOT_BASE = 0xD6348
SLOT_STRIDE = 12
# key, relative offset, storage, label, units, expression, inverse
SLOT_FIELDS = (
    ("launch_speed_threshold", 8, "uint16", "Launch Speed Threshold", "km/h", "x/10", "x*10"),
    ("launch_rpm_native", 6, "uint16", "Launch RPM", "RPM", "x*12.5", "x/12.5"),
    ("launch_soft_width_native", 10, "uint16", "Launch Soft Width", "RPM", "x*12.5", "x/12.5"),
    ("max_trim_rpm", 2, "uint8", "RPM Trim", "deg", "x", "x"),
    ("integral_gain", 0, "uint16", "Integral Gain", "raw", "x", "x"),
    ("max_trim_speed", 3, "uint8", "Speed-Hold Trim", "deg", "x", "x"),
    ("floor_command", 4, "uint8", "Timing Floor", "deg ATDC", "x-110", "x+110"),
)


def slot_address(index, relative):
    return SLOT_BASE + index * SLOT_STRIDE + relative


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
        self.assertEqual(projection.configuration_address, "000d6320")
        self.assertEqual(projection.enable_mask_address, "000d6324")
        self.assertEqual(projection.pedal_requirement_address, "000d632e")
        expected = {
            "coolant_min": "000d6326",
            "min_speed": "000d6328",
            "max_speed": "000d632a",
            "min_rpm_native": "000d632c",
            "speed_frame_age_limit": "000d6342",
            "window_width": "000d6332",
            "window_top": "000d6333",
            "u_rate_limit": "000d6334",
            "integrator_limit": "000d6338",
            "abort_above": "000d633a",
            "abort_below": "000d633b",
        }
        expected.update({
            f"map_{index + 1}_{key}": f"{slot_address(index, relative):08x}"
            for index in range(5)
            for key, relative, *_ in SLOT_FIELDS
        })
        self.assertEqual(dict(projection.control_addresses), expected)
        self.assertEqual(projection.table_count, 46)
        self.assertEqual(projection.masked_view_count, 0)
        self.assertEqual(projection.switch_count, 1)
        self.assertEqual(projection.bitwise_switch_count, 1)
        self.assertEqual(projection.enable_bit_count, 5)
        self.assertEqual(projection.editor_view_count, 48)

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

        self.assertEqual(projection.configuration_address, "000d6320")
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
            if entry["storageaddress"] == "0xD6324"
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
        self.assertIn('storageaddress="0xD6324"', romraider)
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
            flag.find("./EMBEDDEDDATA").get("mmedaddress") == "0xD6324"
            for flag in flags
        ))

    def test_romraider_and_tunerpro_use_a_reversible_pedal_switch(self):
        projection = self.project()
        switches = [
            entry
            for entry in projection.overrides["switch"]
            if entry["storageaddress"] == "0xD632E"
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
        self.assertIn('storageaddress="0xD632E"', romraider)

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
        self.assertEqual(entry.get("address"), "0xD632E")
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
        self.assertIn('storageaddress="0xD6332"', romraider)
        self.assertIn('storageaddress="0xD6338"', romraider)
        self.assertIn('storageaddress="0xD6342"', romraider)
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
        self.assertIn('mmedaddress="0xD6332"', xdf)
        self.assertIn('mmedaddress="0xD6342"', xdf)
        self.assertIn('equation="X/10"', xdf)

    def test_common_definition_applies_both_projections(self):
        self.assertTrue(emit_def.rolling_launch_enabled(self.overrides))

    def test_projection_rejects_address_collisions(self):
        for address in ("000d6324", "000d632e", "000d6328", "000d6342", "000d634e"):
            with self.subTest(address=address):
                maps = deepcopy(self.maps)
                maps[address] = deepcopy(maps["00001000"])
                maps[address]["addr"] = address
                with self.assertRaisesRegex(ValueError, "collides"):
                    rolling_launch.project_definition_model(
                        maps, self.overrides, self.layout
                    )


    def test_projection_hides_retired_and_derived_fields(self):
        projection = self.project()
        keys = {control.key for control in rolling_launch.ALL_CONTROLS}
        self.assertFalse(any("rpm_ceiling" in key for key in keys))
        self.assertFalse(any(key.endswith("_max_trim") for key in keys))
        hidden = [0xD633C, 0xD633D, 0xD6343]
        hidden += [slot_address(index, 5) for index in range(5)]
        hidden += range(self.layout.efficiency.start, self.layout.efficiency.end, 2)
        for address in hidden:
            with self.subTest(address=f"{address:#x}"):
                self.assertNotIn(f"{address:08x}", projection.maps)
                self.assertNotIn(
                    f"{address:08x}", projection.overrides["table"]
                )

    def test_map_slot_views_have_exact_width_units_and_reversible_timing_floor(self):
        projection = self.project()
        self.assertEqual(len(rolling_launch.SLOT_CONTROLS), 35)
        for index in range(5):
            for key, relative, storage, _label, units, expression, inverse in SLOT_FIELDS:
                address = f"{slot_address(index, relative):08x}"
                self.assertEqual(projection.address(f"map_{index + 1}_{key}"), address)
                model = projection.maps[address]
                self.assertEqual((model["storagetype"], model["units"], model["scale_expr"], model["to_byte"]),
                                 (storage, units, expression, inverse))
                if key.startswith("max_trim_"):
                    self.assertIn("refresh_rolling_launch.py", model["note"])
        for command, atdc in ((0, -110), (110, 0), (120, 10), (255, 145)):
            floor = projection.maps[projection.address("map_1_floor_command")]
            self.assertEqual(eval(floor["scale_expr"], {"__builtins__": {}}, {"x": command}), atdc)
            self.assertEqual(eval(floor["to_byte"], {"__builtins__": {}}, {"x": atdc}), command)
        for native, rpm in ((0, 0), (240, 3000), (32767, 409587.5)):
            launch = projection.maps[projection.address("map_1_launch_rpm_native")]
            self.assertEqual(eval(launch["scale_expr"], {"__builtins__": {}}, {"x": native}), rpm)
            self.assertEqual(eval(launch["to_byte"], {"__builtins__": {}}, {"x": rpm}), native)

    def test_both_formats_render_every_slot_and_hide_derived_efficiency(self):
        projection = self.project()
        models = [projection.maps[projection.address(control.key)]
                  for control in rolling_launch.SLOT_CONTROLS]
        xml = ET.fromstring("<rom>" + "\n".join(
            line for model in models
            for line in emit_def.table_xml(model, projection.overrides, self.axes, "JK08A")
        ) + "</rom>")
        xdf, stats = tunerpro.render(
            "JK08A", bytearray([0xFF] * 0x100000), models, self.axes,
            projection.overrides, {}, [], [],
        )
        root = ET.fromstring(xdf)
        self.assertEqual(stats["calibration_tables"], 35)
        efficiency = f"0x{self.layout.efficiency.start:X}"
        self.assertNotIn(f'storageaddress="{efficiency}"', ET.tostring(xml, encoding="unicode"))
        self.assertNotIn(f'mmedaddress="{efficiency}"', xdf)
        for index in range(5):
            for _key, relative, storage, label, *_ in SLOT_FIELDS:
                bits = 16 if storage == "uint16" else 8
                name = f"Rolling Launch Map {index + 1} {label}"
                address = f"0x{slot_address(index, relative):X}"
                table = next(t for t in xml.findall("table") if t.get("name") == name)
                self.assertEqual(table.get("storageaddress"), address)
                table = next(t for t in root.findall("XDFTABLE") if t.findtext("title") == name)
                data = table.find("./XDFAXIS[@id='z']/EMBEDDEDDATA")
                self.assertEqual(data.get("mmedaddress"), address)
                self.assertEqual(data.get("mmedelementsizebits"), str(bits))
                if label == "Timing Floor":
                    self.assertEqual(table.find("./XDFAXIS[@id='z']/MATH").get("equation"), "X-110")


if __name__ == "__main__":
    unittest.main()
