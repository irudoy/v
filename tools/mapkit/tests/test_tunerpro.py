import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from tools.mapkit import emit_def, rom as romkit, tunerpro


ROOT = Path(__file__).resolve().parents[3]
XDF = ROOT / "defs" / "JK08A.xdf"

COMMON_TABLES = {
    "MAF Factor": "Fuelling / MAF Scaling",
    "Target Mixture - Main": "Fuelling / Target Mixture",
    "Target Mixture Multiplier - High-Detonation State": "Fuelling / Target Mixture",
    "Base Fuel Schedule K-Value": "Fuelling / MAF Scaling",
    "Internal Load Normalization Reference": "Fuelling / Load Model",
    "Ignition Timing Surface - Cold State":
        "Ignition Timing / State Surfaces",
    "Knock-State Path Enable - Cold State":
        "Ignition Timing / State Control",
    "Knock Threshold by Evaluator Channel":
        "Ignition Timing / Knock Control / Thresholds",
    "MAF Sensor Transfer - Bank 1": "Fuelling / MAF Scaling",
    "MAF Sensor Transfer - Bank 2": "Fuelling / MAF Scaling",
    "Stationary Engine Speed Limit": "Limiters / Engine Speed / Stationary",
    "Rolling Launch Minimum Coolant Temperature": "Rolling Launch / Activation",
    "Rolling Launch Minimum Vehicle Speed": "Rolling Launch / Activation",
    "Rolling Launch Maximum Vehicle Speed": "Rolling Launch / Activation",
    "Rolling Launch Minimum Engine Speed": "Rolling Launch / Activation",
    "Rolling Launch Speed Frame Age Limit": "Rolling Launch / Activation",
    "Rolling Launch Speed Window Width": "Rolling Launch / Speed Hold",
    "Rolling Launch Speed Window Top": "Rolling Launch / Speed Hold",
    "Rolling Launch Torque Fraction Rate Limit": "Rolling Launch / Speed Hold",
    "Rolling Launch Integral Gain": "Rolling Launch / Speed Hold",
    "Rolling Launch Integrator Limit": "Rolling Launch / Speed Hold",
    "Rolling Launch Abort Above Target": "Rolling Launch / Speed Hold",
    "Rolling Launch Abort Below Target": "Rolling Launch / Speed Hold",
    "Rolling Launch RPM Ceiling Offset": "Rolling Launch / RPM Ceiling",
    "Rolling Launch RPM Ceiling Hysteresis": "Rolling Launch / RPM Ceiling",
}

DEFAULT_VISIBLE_TABLES = {
    "Accelerator Pedal High-State Hysteresis":
        "Electronic Throttle Control / Accelerator Pedal / Thresholds",
    "Stationary Limiter Readiness Threshold":
        "Limiters / Engine Speed / Stationary",
    "Intake CVTC Target Correction - High-Detonation State":
        "Variable Valve Timing / Intake Cam",
    "Intake CVTC Target - Main": "Variable Valve Timing / Intake Cam",
    "Intake CVTC Target - Cold": "Variable Valve Timing / Intake Cam",
    "Exhaust CVTC Target - Cold": "Variable Valve Timing / Exhaust Cam",
    "Exhaust CVTC Target Correction - High-Detonation State":
        "Variable Valve Timing / Exhaust Cam",
    "Exhaust CVTC Target - Standstill Override":
        "Variable Valve Timing / Exhaust Cam",
    "Exhaust CVTC Standstill Override - RPM Floor":
        "Variable Valve Timing / Exhaust Cam",
    "Exhaust CVTC Standstill Override - RPM Ceiling":
        "Variable Valve Timing / Exhaust Cam",
    "Exhaust CVTC Standstill Override - Speed Threshold":
        "Variable Valve Timing / Exhaust Cam",
    "Requested Torque Conversion by QH0 - Primary":
        "Electronic Throttle Control / Requested Torque",
    "Engine Torque Surface": "Torque Model / Engine Torque",
    "Stationary Limiter Readiness Step":
        "Limiters / Engine Speed / Stationary",
    "Injection Pulse Channel Multiplier": "Fuelling / Injection",
    "End of Injection Angle - Base": "Fuelling / Injection",
    "End of Injection Angle - Conditional": "Fuelling / Injection",
    "Throttle Angle-to-Area Conversion - Primary":
        "Electronic Throttle Control / Throttle Geometry",
    "Engine Torque Correction Coefficient vs RPM":
        "Torque Model / Engine Torque",
    "Engine Torque Base Term vs RPM": "Torque Model / Engine Torque",
    "Requested Torque Conversion by QH0 - Validation Copy":
        "Electronic Throttle Control / Requested Torque",
    "Throttle Angle-to-Area Conversion - Validation Copy":
        "Electronic Throttle Control / Throttle Geometry",
}

SLOT_TABLES = {
    "Exhaust CVTC Target - Main": "Variable Valve Timing / Exhaust Cam",
    "Fuel Compensation - Main": "Fuelling / Compensation",
    "DFCO Entry RPM Threshold": "Fuelling / Deceleration Fuel Cut",
    "DFCO Full Restore RPM Threshold": "Fuelling / Deceleration Fuel Cut",
    "DFCO Hold RPM Threshold": "Fuelling / Deceleration Fuel Cut",
    "DFCO Low-Speed Intermediate Restore RPM Threshold":
        "Fuelling / Deceleration Fuel Cut",
    "Ignition Timing Surface - High-Octane State":
        "Ignition Timing / State Surfaces",
    "Knock-State Path Enable - High-Octane State":
        "Ignition Timing / State Control",
    "Ignition Timing Surface - High-Detonation State":
        "Ignition Timing / State Surfaces",
    "Knock-State Path Enable - High-Detonation State":
        "Ignition Timing / State Control",
    "Engine Speed Limit - Fuel Cut": "Limiters / Engine Speed / Driving",
    "Engine Speed Limit - Throttle Request":
        "Limiters / Engine Speed / Driving",
    "Timing-State Addend - Default/Post-Transition":
        "Ignition Timing / State Corrections",
    "Timing-State Addend - Warm DFCO Transition":
        "Ignition Timing / State Corrections",
}


def slot_name(slot, name):
    return f"Map {slot} - {name}"


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
        self.assertEqual(len(self.individual), 48)
        self.assertEqual(len(self.groups), 9)
        self.assertEqual(
            sum(len(patch["entries"]) for patch in self.individual),
            95,
        )
        self.assertEqual(
            sum(len(patch["entries"]) for patch in self.groups),
            95,
        )
        self.assertFalse(any("all" in patch["key"] for patch in self.groups))

    def test_group_record_and_range_counts_follow_manifest_groups(self):
        expected = {
            "catalyst": (2, 4),
            "evap": (13, 26),
            "exhaust_vtc": (8, 16),
            "intake_vtc": (4, 8),
            "manufacturer_specific": (1, 2),
            "misfire": (7, 14),
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
        flags = {
            flag.findtext("./title"): flag
            for flag in self.root.findall("./XDFFLAG")
        }
        expected_tables = dict(COMMON_TABLES)
        expected_tables.update(DEFAULT_VISIBLE_TABLES)
        expected_tables.update({
            slot_name(slot, name): category
            for slot in range(1, 6)
            for name, category in SLOT_TABLES.items()
        })
        self.assertEqual(set(tables), set(expected_tables))
        for title, category in expected_tables.items():
            with self.subTest(title=title):
                self.assertEqual(self.item_category(tables[title]), category)

        expected_flags = {
            f"Map {slot} - Rolling Launch Enable":
                "Rolling Launch / Map Enable"
            for slot in range(1, 6)
        }
        self.assertEqual(set(flags), set(expected_flags))
        for title, category in expected_flags.items():
            with self.subTest(title=title):
                self.assertEqual(self.item_category(flags[title]), category)

        expected_patches = {
            "Developer Immobilizer": "NATS / Immobilizer",
            "Cruise Control Switch": "Cruise Control / Steering Switch",
            "CAN Telemetry at Startup": "Logging / CAN Telemetry",
            "Rolling Launch Require Accelerator Pedal":
                "Rolling Launch / Activation",
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
            | set(expected_flags.values())
            | {
                tunerpro.DTC_INDIVIDUAL_CATEGORY,
                tunerpro.DTC_GROUP_CATEGORY,
            },
        )

    def test_exhaust_cvtc_target_uses_centered_degree_scaling(self):
        table = next(
            table for table in self.root.findall("./XDFTABLE")
            if table.findtext("./title") == slot_name(1, "Exhaust CVTC Target - Main")
        )
        axis = table.find("./XDFAXIS[@id='z']")
        self.assertEqual(axis.findtext("./units"), "degCA")
        self.assertEqual(axis.findtext("./decimalpl"), "1")
        self.assertEqual(axis.find("./MATH").get("equation"), "(X-128)*0.5")

    def test_ignition_trim_is_labeled_in_crank_degrees(self):
        by_title = {
            table.findtext("./title"): table
            for table in self.root.findall("./XDFTABLE")
        }
        for title in (
            "Ignition Timing Surface - Cold State",
            slot_name(1, "Ignition Timing Surface - High-Octane State"),
            slot_name(1, "Ignition Timing Surface - High-Detonation State"),
        ):
            with self.subTest(title=title):
                axis = by_title[title].find("./XDFAXIS[@id='z']")
                self.assertEqual(axis.findtext("./units"), "deg")
                self.assertEqual(axis.findtext("./decimalpl"), "0")

    def test_xdf_has_expected_tables_patches_and_no_checksum(self):
        patches = self.root.findall("./XDFPATCH")
        tables = self.root.findall("./XDFTABLE")
        flags = self.root.findall("./XDFFLAG")
        self.assertEqual(len(patches), 61)
        self.assertEqual(len(tables), 117)
        self.assertEqual(len(flags), 5)
        self.assertEqual(self.root.findall("./XDFCHECKSUM"), [])

        individual = [
            patch for patch in patches
            if self.patch_category(patch) == tunerpro.DTC_INDIVIDUAL_CATEGORY
        ]
        groups = [
            patch for patch in patches
            if self.patch_category(patch) == tunerpro.DTC_GROUP_CATEGORY
        ]
        self.assertEqual(len(individual), 48)
        self.assertEqual(len(groups), 9)
        self.assertEqual(
            sum(len(patch.findall("./XDFPATCHENTRY")) for patch in groups),
            95,
        )
        self.assertFalse(any(
            "Disable all" in (patch.findtext("./title") or "")
            for patch in patches
        ))

    def test_rolling_launch_uses_native_flags_without_raw_mask_table(self):
        flags = {
            flag.findtext("./title"): flag
            for flag in self.root.findall("./XDFFLAG")
        }
        self.assertEqual(
            [flags[f"Map {slot} - Rolling Launch Enable"].findtext("./mask")
             for slot in range(1, 6)],
            ["0x01", "0x02", "0x04", "0x08", "0x10"],
        )
        self.assertTrue(all(
            flags[f"Map {slot} - Rolling Launch Enable"]
            .find("./EMBEDDEDDATA")
            .get("mmedaddress") == "0xD6044"
            for slot in range(1, 6)
        ))
        self.assertNotIn(
            "Rolling Launch Enable Mask (Raw)",
            {
                table.findtext("./title")
                for table in self.root.findall("./XDFTABLE")
            },
        )

    def test_internal_tables_remain_outside_the_working_definition(self):
        addresses = {
            table.find("./XDFAXIS[@id='z']/EMBEDDEDDATA").get("mmedaddress")
            for table in self.root.findall("./XDFTABLE")
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
        by_address = {
            table.find("./XDFAXIS[@id='z']/EMBEDDEDDATA").get("mmedaddress"):
                table
            for table in self.root.findall("./XDFTABLE")
        }
        expected = {
            "0x12196": slot_name(
                1,
                "Timing-State Addend - Default/Post-Transition",
            ),
            "0x1219E": slot_name(
                1,
                "Timing-State Addend - Warm DFCO Transition",
            ),
        }
        for address, title in expected.items():
            with self.subTest(address=address):
                table = by_address[address]
                self.assertEqual(table.findtext("./title"), title)
                self.assertEqual(
                    self.item_category(table),
                    "Ignition Timing / State Corrections",
                )
                axis = table.find("./XDFAXIS[@id='z']")
                self.assertEqual(axis.findtext("./units"), "deg")
                self.assertEqual(axis.find("./MATH").get("equation"), "X-128")
                x_axis = table.find("./XDFAXIS[@id='x']")
                self.assertEqual(
                    x_axis.findtext("./units"),
                    "Engine Speed [RPM]",
                )
                self.assertEqual(
                    [int(label.get("value")) for label in x_axis.findall("./LABEL")],
                    [0, 400, 800, 1200, 1600, 2000, 2400, 2800],
                )

        self.assertNotIn("0x121A6", by_address)

    def test_default_visible_tables_reach_the_working_definition(self):
        addresses = {
            table.find("./XDFAXIS[@id='z']/EMBEDDEDDATA").get("mmedaddress")
            for table in self.root.findall("./XDFTABLE")
        }
        self.assertTrue({
            "0x8FDC",
            "0x911C",
            "0x1108E",
            "0x124D2",
        } <= addresses)

    def test_maf_tables_use_reviewed_candidate_voltage_axes(self):
        tables = {
            table.findtext("./title"): table
            for table in self.root.findall("./XDFTABLE")
        }
        for title in (
            "MAF Sensor Transfer - Bank 1",
            "MAF Sensor Transfer - Bank 2",
        ):
            with self.subTest(title=title):
                axis = tables[title].find("./XDFAXIS[@id='x']")
                self.assertEqual(
                    axis.findtext("./units"),
                    "MAF Sensor Voltage [V, cand]",
                )
                labels = [
                    float(node.get("value"))
                    for node in axis.findall("./LABEL")
                ]
                self.assertEqual(len(labels), 64)
                self.assertEqual(labels[0], 0.0)
                self.assertEqual(labels[-1], 5.04)

    def test_dfco_thresholds_use_coolant_axis_and_rpm_scale(self):
        expected = {
            slot_name(1, "DFCO Hold RPM Threshold"): "0x126E4",
            slot_name(1, "DFCO Entry RPM Threshold"): "0x12718",
            slot_name(1, "DFCO Full Restore RPM Threshold"): "0x12818",
            slot_name(1, "DFCO Low-Speed Intermediate Restore RPM Threshold"):
                "0x1298C",
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

    def test_working_fuel_cut_uses_exact_2x2_layout_and_code_scale(self):
        table = next(
            table for table in self.root.findall("./XDFTABLE")
            if table.findtext("./title") == slot_name(
                1, "Engine Speed Limit - Fuel Cut"
            )
        )
        axis_x = table.find("./XDFAXIS[@id='x']")
        axis_y = table.find("./XDFAXIS[@id='y']")
        axis_z = table.find("./XDFAXIS[@id='z']")
        data = axis_z.find("./EMBEDDEDDATA")
        self.assertEqual(data.get("mmedaddress"), "0x934E")
        self.assertEqual(data.get("mmedelementsizebits"), "16")
        self.assertEqual(data.get("mmedrowcount"), "2")
        self.assertEqual(data.get("mmedcolcount"), "2")
        self.assertEqual(axis_z.findtext("./units"), "RPM")
        self.assertEqual(axis_z.find("./MATH").get("equation"), "X*12.5")
        self.assertEqual(
            [node.get("value") for node in axis_x.findall("./LABEL")],
            ["Normal", "Reverse"],
        )
        self.assertEqual(
            [node.get("value") for node in axis_y.findall("./LABEL")],
            ["Cut", "Restore"],
        )

    def test_throttle_rev_limiter_uses_exact_scalar_and_hardware_scale(self):
        table = next(
            table for table in self.root.findall("./XDFTABLE")
            if table.findtext("./title") == slot_name(
                1, "Engine Speed Limit - Throttle Request"
            )
        )
        axis = table.find("./XDFAXIS[@id='z']")
        data = axis.find("./EMBEDDEDDATA")
        self.assertEqual(data.get("mmedaddress"), "0x942C")
        self.assertEqual(data.get("mmedelementsizebits"), "16")
        self.assertEqual(data.get("mmedrowcount"), "1")
        self.assertEqual(data.get("mmedcolcount"), "1")
        self.assertEqual(axis.findtext("./units"), "RPM")
        self.assertEqual(axis.find("./MATH").get("equation"), "X*0.78125")
        description = table.findtext("./description")
        self.assertIn("shared signed request ffff19c6", description)
        self.assertIn("continuous command path to ATU-II BFR6A-D", description)

    def test_units_mark_only_scales_below_code_and_hardware(self):
        self.assertEqual(tunerpro.units_with_confidence("RPM", "candidate"), "RPM [cand]")
        self.assertEqual(tunerpro.units_with_confidence("RPM", "code"), "RPM")
        self.assertEqual(tunerpro.units_with_confidence("RPM", "silicon"), "RPM")

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
                    runtime_controls = {
                        "Rolling Launch Require Accelerator Pedal": (
                            0xD604E,
                            b"\x00\x01",
                            b"\x00\x00",
                        ),
                        "CAN Telemetry at Startup": (
                            0xD4E03,
                            b"\x00",
                            b"\x01",
                        ),
                    }
                    title = patch.findtext("./title")
                    if title in runtime_controls:
                        # These controls occupy erased stock space and are
                        # based on the validated installed runtime profile.
                        expected = runtime_controls[title]
                        self.assertEqual(address, expected[0])
                        self.assertEqual(basedata, expected[1])
                        self.assertEqual(patchdata, expected[2])
                        continue
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
        low = by_title["Ignition Timing Surface - Cold State"]
        flag = by_title["Knock-State Path Enable - Cold State"]
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
