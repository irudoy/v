from copy import deepcopy
from pathlib import Path
import tomllib
import unittest

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

    def test_projection_uses_exact_enable_mask_address(self):
        projection = self.project()
        self.assertEqual(projection.configuration_address, "000d3f60")
        self.assertEqual(projection.enable_mask_address, "000d3f64")
        self.assertEqual(projection.table_count, 1)
        self.assertEqual(projection.masked_view_count, 5)
        self.assertEqual(projection.editor_view_count, 6)

    def test_projection_exposes_one_independent_bit_per_map(self):
        projection = self.project()
        views = [
            view
            for view in projection.overrides["masked_view"]
            if view["source"] == "000d3f64"
        ]
        self.assertEqual(
            [view["name"] for view in views],
            [
                f"Map {slot} - Rolling Launch Enable"
                for slot in range(1, 6)
            ],
        )
        self.assertEqual(
            [view["mask"] for view in views],
            ["01", "02", "04", "08", "10"],
        )

    def test_projection_preserves_source_models(self):
        maps = deepcopy(self.maps)
        overrides = deepcopy(self.overrides)
        rolling_launch.project_definition_model(
            maps, overrides, self.layout
        )
        self.assertEqual(maps, self.maps)
        self.assertEqual(overrides, self.overrides)

    def test_romraider_and_tunerpro_preserve_neighbor_enable_bits(self):
        projection = self.project()
        model = projection.maps[projection.enable_mask_address]
        view_overrides = deepcopy(projection.overrides)
        view_overrides["masked_view"] = [
            view
            for view in projection.overrides["masked_view"]
            if view["source"] == projection.enable_mask_address
        ]
        _, grouped = emit_def.masked_views(
            view_overrides,
            {projection.enable_mask_address: model},
        )
        views = grouped[projection.enable_mask_address]
        romraider = "\n".join(
            emit_def.masked_view_xml(
                model, views[3], view_overrides, self.axes, "JK08A"
            )
        )
        self.assertIn('storageaddress="0xD3F64"', romraider)
        self.assertIn('mask="08"', romraider)

        image = bytearray([0xFF] * 0x100000)
        xdf, stats = tunerpro.render(
            "JK08A",
            image,
            [model],
            self.axes,
            view_overrides,
            grouped,
            [],
            [],
        )
        self.assertEqual(stats["calibration_tables"], 1)
        self.assertEqual(stats["masked_views"], 5)
        self.assertIn("Map 4 - Rolling Launch Enable", xdf)
        self.assertIn("(B&amp;247)", xdf)

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


if __name__ == "__main__":
    unittest.main()
