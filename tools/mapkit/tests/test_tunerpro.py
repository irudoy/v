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

    def test_categories_use_tunerpro_indices_and_functional_names(self):
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
        expected = {
            "Developer Immobilizer": "NATS / Immobilizer",
            "Target AFR - Power (0xB33A)": "AFR / Lambda",
            "Dual-Channel Contribution Curve B - MAF candidate (0x141F4)": "Airflow",
            "Cold Ignition Timing Map (0x991A)": "Ignition Timing / Main",
            "Engine Speed Axis [RPM] (ref)": "Reference Axes",
        }
        for title, category in expected.items():
            with self.subTest(title=title):
                item = patches[title] if title in patches else tables[title]
                self.assertEqual(self.item_category(item), category)

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

    def test_xdf_has_expected_tables_patches_and_no_checksum(self):
        patches = self.root.findall("./XDFPATCH")
        tables = self.root.findall("./XDFTABLE")
        self.assertEqual(len(patches), 36)
        self.assertEqual(len(tables), 150)
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
        low = by_title["Cold Ignition Timing Map (0x991A)"]
        flag = by_title[
            "Cold Ignition Timing Map Knock Window (0x991A bit7)"
        ]
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
