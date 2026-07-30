import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.mapkit import emit_def, rom as romkit, tunerpro


ROOT = Path(__file__).resolve().parents[3]
XDF = ROOT / "defs" / "JK08A.xdf"


def apply_patch(stock, patch):
    result = bytearray(stock)
    changed = set()
    for entry in patch["entries"]:
        address = entry["address"]
        basedata = entry["basedata"]
        patchdata = entry["patchdata"]
        assert stock[address:address + len(basedata)] == basedata
        result[address:address + len(patchdata)] = patchdata
        changed.update(range(address, address + len(patchdata)))
    return bytes(result), changed


class TunerProDtcPatchModelTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = romkit.load("JK08A")
        cls.records = emit_def.dtc_records("JK08A", image=cls.image)
        cls.individual, cls.groups = tunerpro.dtc_patches(
            "JK08A", cls.records
        )

    def test_inventory_has_individual_and_group_scopes_without_all_patch(self):
        self.assertEqual(len(self.individual), 29)
        self.assertEqual(len(self.groups), 6)
        self.assertEqual(
            sum(len(patch["entries"]) for patch in self.individual),
            57,
        )
        self.assertEqual(
            sum(len(patch["entries"]) for patch in self.groups),
            57,
        )
        self.assertFalse(any("all" in patch["key"] for patch in self.groups))

    def test_group_record_and_range_counts_follow_manifest_groups(self):
        expected = {
            "catalyst": (2, 4),
            "evap": (13, 26),
            "manufacturer_specific": (1, 2),
            "nats": (1, 1),
            "rear_o2": (8, 16),
            "rear_o2_heater": (4, 8),
        }
        patches = {
            patch["key"].split(":", 1)[1]: patch for patch in self.groups
        }
        records_by_group = {}
        for group in expected:
            records_by_group[group] = [
                record for record in self.records if record["group"] == group
            ]
        self.assertEqual(set(patches), set(expected))
        for group, (record_count, range_count) in expected.items():
            with self.subTest(group=group):
                self.assertEqual(len(records_by_group[group]), record_count)
                self.assertEqual(len(patches[group]["entries"]), range_count)

    def test_each_individual_patch_is_atomic_and_matches_stock(self):
        patches = {patch["key"]: patch for patch in self.individual}
        for record in self.records:
            with self.subTest(dtc=record["dtc"], index=record["index"]):
                patch = patches[f"dtc:{record['index']}"]
                result, changed = apply_patch(self.image.data, patch)
                expected_ranges = tunerpro.dtc_entry_ranges(record)
                expected_changed = {
                    offset
                    for entry in expected_ranges
                    for offset in range(
                        entry["address"],
                        entry["address"] + len(entry["patchdata"]),
                    )
                }
                self.assertEqual(changed, expected_changed)
                for entry in expected_ranges:
                    address = entry["address"]
                    self.assertEqual(
                        result[address:address + len(entry["patchdata"])],
                        entry["patchdata"],
                    )

    def test_p0420_has_two_ranges_and_p1610_has_one(self):
        patches = {patch["key"]: patch for patch in self.individual}
        self.assertEqual(len(patches["dtc:17"]["entries"]), 2)
        self.assertEqual(len(patches["dtc:40"]["entries"]), 1)

    def test_each_group_patch_changes_only_its_manifest_records(self):
        records_by_group = {
            group: [record for record in self.records if record["group"] == group]
            for group in {record["group"] for record in self.records}
        }
        for patch in self.groups:
            group = patch["key"].split(":", 1)[1]
            with self.subTest(group=group):
                result, changed = apply_patch(self.image.data, patch)
                expected_ranges = [
                    entry
                    for record in records_by_group[group]
                    for entry in tunerpro.dtc_entry_ranges(record)
                ]
                expected_changed = {
                    offset
                    for entry in expected_ranges
                    for offset in range(
                        entry["address"],
                        entry["address"] + len(entry["patchdata"]),
                    )
                }
                self.assertEqual(changed, expected_changed)
                for entry in expected_ranges:
                    address = entry["address"]
                    self.assertEqual(
                        result[address:address + len(entry["patchdata"])],
                        entry["patchdata"],
                    )


class TunerProMaskedTableTest(unittest.TestCase):
    def test_low_seven_bit_equation_preserves_bit_seven(self):
        self.assertEqual(
            tunerpro.masked_equation("x-64", 0x7F, 8),
            "(((X-(B&128))/1))-64",
        )
        for raw in range(256):
            for edited in (-64, -1, 0, 63):
                encoded = edited + 64 + (raw & 0x80)
                self.assertEqual(encoded & 0x80, raw & 0x80)
                self.assertEqual((encoded & 0x7F) - 64, edited)

    def test_bit_seven_equation_preserves_low_seven_bits(self):
        self.assertEqual(
            tunerpro.masked_equation("x", 0x80, 8),
            "(((X-(B&127))/128))",
        )
        for raw in range(256):
            for edited in (0, 1):
                encoded = edited * 128 + (raw & 0x7F)
                self.assertEqual(encoded & 0x7F, raw & 0x7F)
                self.assertEqual((encoded >> 7) & 1, edited)


class TrackedTunerProDefinitionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.image = romkit.load("JK08A")
        cls.root = ET.parse(XDF).getroot()
        cls.categories = {
            int(category.get("index"), 16): category.get("name")
            for category in cls.root.findall("./XDFHEADER/CATEGORY")
        }

    def item_category(self, item):
        member = item.find("./CATEGORYMEM")
        return self.categories[int(member.get("category")) - 1]

    def patch_category(self, patch):
        return self.item_category(patch)

    def test_categories_use_tunerpro_indices_and_vendor_style_names(self):
        self.assertEqual(
            sorted(self.categories),
            list(range(len(self.categories))),
        )
        self.assertTrue(all(
            "(candidate)" not in name and "(traced)" not in name
            for name in self.categories.values()
        ))

        patches = {
            patch.findtext("./title"): patch
            for patch in self.root.findall("./XDFPATCH")
        }
        tables = {
            table.findtext("./title"): table
            for table in self.root.findall("./XDFTABLE")
        }
        expected_tables = {
            "Fuel Targets": "Fuelling / Fuel Targets",
            "Fuel Compensation Main": "Fuelling / Fuel Compensation",
            "Overrun Fuel Cut": "Fuelling / Overrun",
            "Overrun Fuel Cut Restore": "Fuelling / Overrun",
            "Calculated Load": "Fuelling / Engine Load",
            "Ignition Timing Trim Cold": "Ignition Timing / Main",
            "Ignition Timing Trim Main": "Ignition Timing / Main",
            "Ignition Timing Trim High Det": "Ignition Timing / Main",
            "Knock Control Enable - Cold": (
                "Ignition Timing / Knock Control"
            ),
            "Knock Control Enable - Main": (
                "Ignition Timing / Knock Control"
            ),
            "Knock Control Enable - High Det": (
                "Ignition Timing / Knock Control"
            ),
            "Knock Sensitivity": "Ignition Timing / Knock Control",
            "Rev Limit - Fuel Cut": "Limiters / Rev Limit",
            "Rev Limit - Throttle Cut": "Limiters / Rev Limit",
            "Stationary Rev Limiter": (
                "Limiters / Stationary Rev Limiter"
            ),
        }
        self.assertEqual(set(tables), set(expected_tables))
        for title, category in expected_tables.items():
            with self.subTest(title=title):
                self.assertEqual(self.item_category(tables[title]), category)

        expected_patches = {
            "Developer Immobilizer": "NATS / Immobilizer",
        }
        for title, category in expected_patches.items():
            with self.subTest(title=title):
                self.assertEqual(self.item_category(patches[title]), category)

        individual = next(
            patch for title, patch in patches.items()
            if title.startswith("DTC P0420 ")
        )
        group = next(
            patch for title, patch in patches.items()
            if title.startswith("Disable DTC group: Catalyst ")
        )
        self.assertEqual(
            self.patch_category(individual),
            tunerpro.DTC_INDIVIDUAL_CATEGORY,
        )
        self.assertEqual(
            self.patch_category(group),
            tunerpro.DTC_GROUP_CATEGORY,
        )
        self.assertEqual(
            set(self.categories.values()),
            set(expected_tables.values())
            | set(expected_patches.values())
            | {
                tunerpro.DTC_INDIVIDUAL_CATEGORY,
                tunerpro.DTC_GROUP_CATEGORY,
            },
        )

    def test_fuel_targets_use_gasoline_afr_scaling(self):
        table = next(
            table for table in self.root.findall("./XDFTABLE")
            if table.findtext("./title") == "Fuel Targets"
        )
        axis = table.find("./XDFAXIS[@id='z']")
        self.assertEqual(axis.findtext("./units"), "AFR (gasoline scale) [cand]")
        self.assertEqual(axis.findtext("./decimalpl"), "2")
        self.assertEqual(axis.find("./MATH").get("equation"), "1881.6/X")

    def test_ignition_trim_is_labeled_as_relative_adjustment(self):
        by_title = {
            table.findtext("./title"): table
            for table in self.root.findall("./XDFTABLE")
        }
        for title in (
            "Ignition Timing Trim Cold",
            "Ignition Timing Trim Main",
            "Ignition Timing Trim High Det",
        ):
            with self.subTest(title=title):
                axis = by_title[title].find("./XDFAXIS[@id='z']")
                self.assertEqual(
                    axis.findtext("./units"),
                    "Timing adjustment (deg) [cand]",
                )
                self.assertEqual(axis.findtext("./decimalpl"), "0")

    def test_xdf_has_expected_tables_patches_and_no_checksum(self):
        patches = self.root.findall("./XDFPATCH")
        tables = self.root.findall("./XDFTABLE")
        self.assertEqual(len(patches), 36)
        self.assertEqual(len(tables), 15)
        self.assertEqual(self.root.findall("./XDFCHECKSUM"), [])

        individual = [
            patch for patch in patches
            if self.patch_category(patch) == tunerpro.DTC_INDIVIDUAL_CATEGORY
        ]
        groups = [
            patch for patch in patches
            if self.patch_category(patch) == tunerpro.DTC_GROUP_CATEGORY
        ]
        self.assertEqual(len(individual), 29)
        self.assertEqual(len(groups), 6)
        self.assertEqual(
            sum(len(patch.findall("./XDFPATCHENTRY")) for patch in groups),
            57,
        )
        self.assertFalse(any(
            "Disable all" in (patch.findtext("./title") or "")
            for patch in patches
        ))

    def test_research_only_tables_remain_outside_the_working_definition(self):
        addresses = {
            table.find("./XDFAXIS[@id='z']/EMBEDDEDDATA").get("mmedaddress")
            for table in self.root.findall("./XDFTABLE")
        }
        self.assertTrue({
            "0x8FDC",
            "0x911C",
            "0x10F8E",
            "0x124D2",
            "0x126E4",
            "0x1298C",
            "0x141F4",
        }.isdisjoint(addresses))

    def test_overrun_tables_use_coolant_axis_and_rpm_scale(self):
        expected = {
            "Overrun Fuel Cut": "0x12718",
            "Overrun Fuel Cut Restore": "0x12818",
        }
        tables = {
            table.findtext("./title"): table
            for table in self.root.findall("./XDFTABLE")
        }
        for title, address in expected.items():
            with self.subTest(title=title):
                table = tables[title]
                axis_x = table.find("./XDFAXIS[@id='x']")
                axis_z = table.find("./XDFAXIS[@id='z']")
                data = axis_z.find("./EMBEDDEDDATA")
                self.assertEqual(
                    axis_x.findtext("./units"),
                    "Coolant Temperature [deg C]",
                )
                self.assertEqual(
                    [node.get("value") for node in axis_x.findall("./LABEL")],
                    [str(value) for value in range(-40, 120, 10)],
                )
                self.assertEqual(data.get("mmedaddress"), address)
                self.assertEqual(data.get("mmedelementsizebits"), "8")
                self.assertEqual(data.get("mmedrowcount"), "1")
                self.assertEqual(data.get("mmedcolcount"), "16")
                self.assertEqual(axis_z.findtext("./units"), "RPM")
                self.assertEqual(axis_z.find("./MATH").get("equation"), "X*25")

    def test_working_fuel_cut_uses_exact_2x2_layout_and_candidate_scale(self):
        table = next(
            table for table in self.root.findall("./XDFTABLE")
            if table.findtext("./title") == "Rev Limit - Fuel Cut"
        )
        axis_x = table.find("./XDFAXIS[@id='x']")
        axis_y = table.find("./XDFAXIS[@id='y']")
        axis_z = table.find("./XDFAXIS[@id='z']")
        data = axis_z.find("./EMBEDDEDDATA")
        self.assertEqual(data.get("mmedaddress"), "0x934E")
        self.assertEqual(data.get("mmedelementsizebits"), "16")
        self.assertEqual(data.get("mmedrowcount"), "2")
        self.assertEqual(data.get("mmedcolcount"), "2")
        self.assertEqual(axis_z.findtext("./units"), "RPM [cand]")
        self.assertEqual(axis_z.find("./MATH").get("equation"), "X*12.5")
        self.assertEqual(
            [node.get("value") for node in axis_x.findall("./LABEL")],
            ["Normal", "Reverse"],
        )
        self.assertEqual(
            [node.get("value") for node in axis_y.findall("./LABEL")],
            ["Cut", "Restore"],
        )

    def test_throttle_rev_limiter_uses_exact_scalar_and_candidate_scale(self):
        table = next(
            table for table in self.root.findall("./XDFTABLE")
            if table.findtext("./title") == "Rev Limit - Throttle Cut"
        )
        axis = table.find("./XDFAXIS[@id='z']")
        data = axis.find("./EMBEDDEDDATA")
        self.assertEqual(data.get("mmedaddress"), "0x942C")
        self.assertEqual(data.get("mmedelementsizebits"), "16")
        self.assertEqual(data.get("mmedrowcount"), "1")
        self.assertEqual(data.get("mmedcolcount"), "1")
        self.assertEqual(axis.findtext("./units"), "RPM [cand]")
        self.assertEqual(axis.find("./MATH").get("equation"), "X*0.78125")
        description = table.findtext("./description")
        self.assertIn("shared signed airflow/torque-request coordinate ffff19c6", description)
        self.assertIn("no continuous trace reaches a bank-specific throttle-angle command", description)

    def test_patch_base_data_matches_exact_stock_image(self):
        for patch in self.root.findall("./XDFPATCH"):
            for entry in patch.findall("./XDFPATCHENTRY"):
                with self.subTest(
                    patch=patch.findtext("./title"),
                    entry=entry.get("name"),
                ):
                    address = int(entry.get("address"), 16)
                    basedata = bytes.fromhex(entry.get("basedata"))
                    patchdata = bytes.fromhex(entry.get("patchdata"))
                    self.assertEqual(int(entry.get("datasize"), 16), len(patchdata))
                    self.assertEqual(
                        self.image.data[address:address + len(basedata)],
                        basedata,
                    )

    def test_direct_object_ids_are_unique(self):
        identifiers = [
            child.get("uniqueid")
            for child in self.root
            if child.get("uniqueid") is not None
        ]
        self.assertEqual(len(identifiers), len(set(identifiers)))

    def test_masked_tables_have_per_cell_preserving_conversions(self):
        by_title = {
            table.findtext("./title"): table
            for table in self.root.findall("./XDFTABLE")
        }
        low = by_title["Ignition Timing Trim Cold"]
        flag = by_title["Knock Control Enable - Cold"]
        for table, other_mask, divisor in (
            (low, "128", "1"),
            (flag, "127", "128"),
        ):
            math = table.findall("./XDFAXIS[@id='z']/MATH")
            self.assertEqual(len(math), 257)
            self.assertEqual(
                {(entry.get("row"), entry.get("col"))
                 for entry in math[1:]},
                {(str(row), str(column))
                 for row in range(1, 17)
                 for column in range(1, 17)},
            )
            self.assertTrue(all(
                f"B&{other_mask}" in entry.get("equation")
                and f"/{divisor}" in entry.get("equation")
                for entry in math[1:]
            ))
            self.assertTrue(all(
                entry.find("./VAR[@id='B']").get("address")
                for entry in math[1:]
            ))


if __name__ == "__main__":
    unittest.main()
