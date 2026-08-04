from copy import deepcopy
from pathlib import Path
import tomllib
import unittest

from patches import map_switching_layout
from tools.mapkit import emit_def, map_switching, tunerpro


ROOT = Path(__file__).resolve().parents[3]


def axis(address, length=16):
    return {
        "addr": address,
        "len": length,
        "storagetype": "uint16",
        "kind": "rpm",
        "units": "raw",
        "scale_expr": "x",
        "to_byte": "x",
        "scale_conf": "code",
        "confidence": "code",
        "note": "",
    }


def calibration(family):
    dims = 2 if family.height > 1 else 1
    if family.key == "rev_limit_fuel_cut":
        access_family = "direct-row-major"
        axis_x = []
        axis_y = []
        steps = []
    elif family.key == "rev_limit_throttle_cut":
        access_family = "direct-indexed"
        axis_x = []
        axis_y = []
        steps = []
    elif family.group == "overrun":
        access_family = "implicit"
        axis_x = []
        axis_y = []
        steps = [1]
    else:
        access_family = "interpolated"
        axis_x = ["00008000"]
        axis_y = ["00008020"]
        steps = []
    return {
        "addr": map_switching.address_key(family.canonical_address),
        "family": access_family,
        "dims": dims,
        "width": family.width,
        "height": family.height if dims == 2 else None,
        "storagetype": family.storage_type,
        "confidence": "code",
        "role": "table",
        "semantics": family.name,
        "units": "raw",
        "scale_expr": "x",
        "to_byte": "x",
        "scale_conf": "code",
        "note": "",
        "wrappers": [],
        "kernels": [],
        "steps": steps,
        "accessors": ["00001000"],
        "resolver_kinds": ["manual"],
        "axis_x": axis_x,
        "axis_y": axis_y,
        "diagnostic_bindings": [],
    }


def cold_ignition():
    family = deepcopy(
        calibration(
            map_switching_layout.load_layout().family_by_key[
                "ignition_timing_trim_main"
            ]
        )
    )
    family["addr"] = "0000991a"
    family["semantics"] = "Ignition Timing Trim Cold"
    return family


class MapSwitchingDefinitionProjectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.layout = map_switching_layout.load_layout()
        with open(
            ROOT / "defs" / "JK08A.overrides.toml", "rb"
        ) as source:
            cls.overrides = tomllib.load(source)
        cls.maps = {
            map_switching.address_key(family.canonical_address):
            calibration(family)
            for family in cls.layout.families
        }
        cls.maps["0000991a"] = cold_ignition()
        cls.axes = {
            "00008000": axis("00008000"),
            "00008020": axis("00008020"),
        }

    def project(self):
        return map_switching.project_definition_model(
            self.maps, self.overrides, self.layout
        )

    def test_projection_contains_fifty_tables_and_sixty_slot_views(self):
        projection = self.project()
        self.assertEqual(projection.slot_table_count, 50)
        self.assertEqual(projection.slot_masked_view_count, 10)
        self.assertEqual(projection.slot_editor_view_count, 60)
        self.assertEqual(len(projection.switchable_addresses), 50)

    def test_projection_uses_manifest_addresses_names_and_categories(self):
        projection = self.project()
        for family in self.layout.families:
            for slot, address in enumerate(
                family.all_slot_addresses, 1
            ):
                key = map_switching.address_key(address)
                with self.subTest(family=family.key, slot=slot):
                    self.assertEqual(
                        projection.maps[key]["map_switching_source"],
                        map_switching.address_key(
                            family.canonical_address
                        ),
                    )
                    self.assertEqual(
                        projection.maps[key]["map_switching_slot"], slot
                    )
                    presentation = projection.overrides["table"][key]
                    self.assertTrue(
                        presentation["name"].startswith(f"Map {slot} - ")
                    )
                    self.assertEqual(
                        presentation["category"],
                        self.overrides["table"][
                            map_switching.address_key(
                                family.canonical_address
                            )
                        ]["category"],
                    )

    def test_projection_propagates_metadata_changes_to_every_slot(self):
        maps = deepcopy(self.maps)
        overrides = deepcopy(self.overrides)
        family = self.layout.family_by_key[
            "ignition_timing_trim_main"
        ]
        source = map_switching.address_key(family.canonical_address)

        map_changes = {
            "semantics": "Mutated ignition timing semantics",
            "units": "mutated timing unit",
            "scale_expr": "x*2-17",
            "to_byte": "(x+17)/2",
            "scale_conf": "hardware",
            "axis_x": ["00008020"],
            "axis_y": ["00008000"],
        }
        maps[source].update(map_changes)

        presentation_changes = {
            "name": "Mutated Ignition Timing Main",
            "category": "Ignition Timing / Mutated",
            "mask": "3F",
            "format": "0.0",
            "fine": 0.5,
            "coarse": 2.0,
        }
        overrides["table"][source].update(presentation_changes)

        masked_source = next(
            view
            for view in overrides["masked_view"]
            if view["source"] == source
        )
        masked_changes = {
            "name": "Mutated Knock Control Main",
            "category": "Ignition Timing / Mutated Mask",
            "mask": "C0",
            "units": "mutated flag unit",
            "expression": "x*3",
            "to_byte": "x/3",
            "format": "0.00",
            "fine": 0.25,
            "coarse": 1.5,
        }
        masked_source.update(masked_changes)

        projection = map_switching.project_definition_model(
            maps, overrides, self.layout
        )
        projected_views = projection.overrides["masked_view"]

        for slot, address in enumerate(family.all_slot_addresses, 1):
            target = map_switching.address_key(address)
            with self.subTest(slot=slot, address=target):
                projected_map = projection.maps[target]
                for key, value in map_changes.items():
                    self.assertEqual(projected_map[key], value)

                presentation = projection.overrides["table"][target]
                self.assertEqual(
                    presentation["name"],
                    map_switching.slot_name(
                        slot, presentation_changes["name"]
                    ),
                )
                for key in (
                    "category",
                    "mask",
                    "format",
                    "fine",
                    "coarse",
                ):
                    self.assertEqual(
                        presentation[key], presentation_changes[key]
                    )

                masked = next(
                    view
                    for view in projected_views
                    if view["source"] == target
                    and view["name"] == map_switching.slot_name(
                        slot, masked_changes["name"]
                    )
                )
                for key in (
                    "category",
                    "mask",
                    "units",
                    "expression",
                    "to_byte",
                    "format",
                    "fine",
                    "coarse",
                ):
                    self.assertEqual(masked[key], masked_changes[key])

    def test_projection_clones_only_switchable_masked_views(self):
        projection = self.project()
        views = projection.overrides["masked_view"]
        cold = [view for view in views if view["source"] == "0000991a"]
        main = [
            view
            for view in views
            if "Knock Control Enable - Main" in view["name"]
        ]
        high_det = [
            view
            for view in views
            if "Knock Control Enable - High Det" in view["name"]
        ]
        self.assertEqual(len(cold), 1)
        self.assertEqual(len(main), 5)
        self.assertEqual(len(high_det), 5)
        self.assertEqual(
            {view["source"] for view in main},
            {
                map_switching.address_key(address)
                for address in self.layout.family_by_key[
                    "ignition_timing_trim_main"
                ].all_slot_addresses
            },
        )

    def test_source_models_and_global_entries_remain_unchanged(self):
        maps = deepcopy(self.maps)
        overrides = deepcopy(self.overrides)
        projection = map_switching.project_definition_model(
            maps, overrides, self.layout
        )
        self.assertEqual(maps, self.maps)
        self.assertEqual(overrides, self.overrides)
        self.assertEqual(
            projection.maps["0000991a"], self.maps["0000991a"]
        )
        self.assertEqual(
            projection.overrides["table"]["0000991a"],
            self.overrides["table"]["0000991a"],
        )

    def test_projection_rejects_geometry_drift(self):
        maps = deepcopy(self.maps)
        maps["00009a1a"]["width"] = 8
        with self.assertRaisesRegex(ValueError, "graph geometry"):
            map_switching.project_definition_model(
                maps, self.overrides, self.layout
            )

    def test_projection_rejects_copy_address_collision(self):
        maps = deepcopy(self.maps)
        maps["000d2500"] = deepcopy(maps["00009a1a"])
        maps["000d2500"]["addr"] = "000d2500"
        with self.assertRaisesRegex(ValueError, "collides"):
            map_switching.project_definition_model(
                maps, self.overrides, self.layout
            )

    def test_romraider_fragments_describe_projected_storage(self):
        projection = self.project()
        emitted = {
            address: model
            for address, model in projection.maps.items()
            if address in projection.overrides["table"]
            and projection.overrides["table"][address].get("emit", False)
        }
        _, views_by_source = emit_def.masked_views(
            projection.overrides, emitted
        )
        target = "000d2600"
        xml = "\n".join(
            emit_def.table_xml(
                projection.maps[target],
                projection.overrides,
                self.axes,
                "JK08A",
            )
        )
        self.assertIn('name="Map 3 - Ignition Timing Trim Main"', xml)
        self.assertIn(
            'category="Ignition Timing / Main"',
            xml,
        )
        self.assertIn('storageaddress="0xD2600"', xml)
        self.assertIn(
            "common-definition Map 3 storage projected from 0x09A1A", xml
        )
        view_xml = "\n".join(
            emit_def.masked_view_xml(
                projection.maps[target],
                views_by_source[target][0],
                projection.overrides,
                self.axes,
                "JK08A",
            )
        )
        self.assertIn('name="Map 3 - Knock Control Enable - Main"', view_xml)
        self.assertIn('mask="80"', view_xml)

    def test_tunerpro_renderer_accepts_the_same_projected_model(self):
        projection = self.project()
        calibrations = [
            model
            for address, model in projection.maps.items()
            if projection.overrides["table"].get(address, {}).get(
                "emit", False
            )
        ]
        _, views_by_source = emit_def.masked_views(
            projection.overrides,
            {model["addr"]: model for model in calibrations},
        )
        image = map_switching_layout.materialize_calibration_copies(
            self.layout
        )
        xdf, stats = tunerpro.render(
            "JK08A",
            image,
            calibrations,
            self.axes,
            projection.overrides,
            views_by_source,
            [],
            [],
        )
        self.assertEqual(stats["calibration_tables"], 51)
        self.assertEqual(stats["masked_views"], 11)
        self.assertIn("<title>Map 5 - Fuel Targets</title>", xdf)
        self.assertIn('mmedaddress="0xD3000"', xdf)
        self.assertNotIn("JK08A-MS5", xdf)
        self.assertIn(
            "Stock firmware does not reference this allocated storage",
            xdf,
        )

    def test_common_jk08a_definition_enables_the_projection(self):
        maps, overrides, projection = emit_def.apply_definition_projections(
            "JK08A", self.maps, self.overrides
        )
        self.assertIsNotNone(projection)
        self.assertEqual(projection.slot_editor_view_count, 60)
        self.assertEqual(maps, projection.maps)
        self.assertEqual(overrides, projection.overrides)


if __name__ == "__main__":
    unittest.main()
