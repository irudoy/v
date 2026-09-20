import csv
from pathlib import Path
import tomllib
import unittest
import xml.etree.ElementTree as ET

from tools.can_dashboard import live_feed
from tools.mapkit import emit_def


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROM = "JK08A"

BINDINGS = {
    "logparam": {
        "ffff11ae": {"id": "X_VQ_Engine_Speed", "units": "RPM"},
        "ffff102c": {"id": "X_VQ_Engine_Load", "units": "Normalized BFS [%]"},
    }
}


def axis(**changes):
    row = {
        "addr": "00012f2e",
        "kind": "rpm",
        "units": "RPM",
        "scale_expr": "x*50",
        "to_byte": "x/50",
        "scale_conf": "code",
        "scale_evidence": (
            "site:000bfe1c;indexed_by:ffff11ae@confidence;spec:4*12.5=50"
        ),
        "storagetype": "uint8",
        "len": 16,
    }
    row.update(changes)
    return row


def tracked_overrides():
    with (ROOT / "defs" / f"{SOURCE_ROM}.overrides.toml").open("rb") as stream:
        return tomllib.load(stream)


def tracked_axes():
    with (ROOT / "defs" / f"{SOURCE_ROM}.axes.csv").open(newline="") as stream:
        return {row["addr"]: row for row in csv.DictReader(stream)}


class AxisLogparamRuleTest(unittest.TestCase):
    def test_code_scaled_axis_names_the_parameter_of_its_single_operand(self):
        self.assertEqual(
            emit_def.axis_logparam(axis(), BINDINGS), "X_VQ_Engine_Speed"
        )

    def test_axis_without_a_declaration_section_stays_without_live_data(self):
        self.assertIsNone(emit_def.axis_logparam(axis(), {}))

    def test_scaling_below_code_stays_without_live_data(self):
        self.assertIsNone(
            emit_def.axis_logparam(axis(scale_conf="candidate"), BINDINGS)
        )

    def test_axis_without_an_operand_stays_without_live_data(self):
        self.assertIsNone(
            emit_def.axis_logparam(
                axis(scale_evidence="site:0004e250;spec:4*12.5=50"), BINDINGS
            )
        )
        self.assertIsNone(
            emit_def.axis_logparam(axis(scale_evidence=None), BINDINGS)
        )

    def test_undeclared_operand_stays_without_live_data(self):
        self.assertIsNone(
            emit_def.axis_logparam(
                axis(scale_evidence="indexed_by:ffff11b6@structural"), BINDINGS
            )
        )

    def test_two_operands_stay_without_live_data(self):
        self.assertIsNone(
            emit_def.axis_logparam(
                axis(
                    scale_evidence=(
                        "indexed_by:ffff11ae@structural;"
                        "indexed_by:ffff102c@structural"
                    )
                ),
                BINDINGS,
            )
        )

    def test_operand_with_an_offset_stays_without_live_data(self):
        self.assertIsNone(
            emit_def.axis_logparam(
                axis(scale_evidence="indexed_by:ffff11ae+2@structural"),
                BINDINGS,
            )
        )

    def test_units_other_than_the_declared_units_stay_without_live_data(self):
        self.assertIsNone(
            emit_def.axis_logparam(
                axis(
                    units="Base Fuel Schedule (ms)",
                    scale_evidence="indexed_by:ffff102c@structural",
                ),
                BINDINGS,
            )
        )

    def test_malformed_scale_evidence_stops_generation(self):
        with self.assertRaises(SystemExit):
            emit_def.axis_logparam(
                axis(scale_evidence="indexed_by:ffff11ae"), BINDINGS
            )

    def test_axis_xml_carries_the_attribute_only_for_a_bound_axis(self):
        bound = "\n".join(emit_def.axis_xml("Y Axis", axis(), BINDINGS, "sizey"))
        self.assertIn('logparam="X_VQ_Engine_Speed"', bound)
        ET.fromstring(bound)
        unbound = "\n".join(
            emit_def.axis_xml(
                "Y Axis", axis(scale_conf="candidate"), BINDINGS, "sizey"
            )
        )
        self.assertNotIn("logparam", unbound)


class LogparamDeclarationTest(unittest.TestCase):
    def test_declaration_is_validated(self):
        rejected = (
            {"logparam": []},
            {"logparam": {"FFFF11AE": {"id": "X_A", "units": "RPM"}}},
            {"logparam": {"ffff11ae": "X_A"}},
            {"logparam": {"ffff11ae": {"id": "X_A"}}},
            {"logparam": {"ffff11ae": {"id": "", "units": "RPM"}}},
            {"logparam": {"ffff11ae": {"id": "X A", "units": "RPM"}}},
            {"logparam": {"ffff11ae": {"id": "X_A", "units": 1}}},
            {"logparam": {"ffff11ae": {"id": "X_A", "units": "RPM", "x": 1}}},
        )
        for overrides in rejected:
            with self.subTest(overrides=overrides):
                with self.assertRaises(SystemExit):
                    emit_def.logparam_bindings(overrides)
        self.assertEqual(emit_def.logparam_bindings({}), {})
        self.assertEqual(
            emit_def.logparam_bindings(BINDINGS)["ffff102c"],
            ("X_VQ_Engine_Load", "Normalized BFS [%]"),
        )

    def test_tracked_declaration_names_published_feed_parameters(self):
        published = {channel.logger_id for channel in live_feed.CHANNELS}
        bindings = emit_def.logparam_bindings(tracked_overrides())
        self.assertTrue(bindings)
        for operand, (logger_id, _units) in bindings.items():
            with self.subTest(operand=operand):
                self.assertIn(logger_id, published)

    def test_every_tracked_declaration_binds_an_axis(self):
        overrides = tracked_overrides()
        used = set()
        for row in tracked_axes().values():
            if emit_def.axis_logparam(row, overrides):
                used.update(
                    token.target_addr
                    for token in emit_def.provenance.parse_evidence(
                        row["scale_evidence"], "scale_conf"
                    )
                    if token.role == "indexed_by"
                )
        self.assertEqual(used, set(emit_def.logparam_bindings(overrides)))


class TrackedDefinitionLogparamTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.overrides = tracked_overrides()
        cls.axes = tracked_axes()
        cls.rom = ET.parse(ROOT / "defs" / f"{SOURCE_ROM}.xml").getroot().find("rom")

    def axis_elements(self):
        for table in self.rom.findall("table"):
            for element in table.findall("table"):
                if element.get("type") in {"X Axis", "Y Axis"}:
                    yield table, element

    def test_every_rom_axis_follows_the_declared_rule(self):
        checked = 0
        for table, element in self.axis_elements():
            address = f'{int(element.get("storageaddress"), 16):08x}'
            with self.subTest(table=table.get("name"), axis=address):
                self.assertEqual(
                    element.get("logparam"),
                    emit_def.axis_logparam(self.axes[address], self.overrides),
                )
            checked += 1
        self.assertGreater(checked, 0)

    def test_ignition_and_cam_surfaces_support_the_overlay(self):
        expected = {
            "Ignition Timing Surface - Cold State",
            "Map 1 - Ignition Timing Surface - High-Octane State",
            "Map 5 - Ignition Timing Surface - High-Detonation State",
            "Target Mixture - Main",
            "Intake CVTC Target - Main",
        }
        params = {}
        for table in self.rom.findall("table"):
            if table.get("type") == "3D":
                axes = {
                    element.get("type"): element.get("logparam")
                    for element in table.findall("table")
                }
                params[table.get("name")] = (
                    axes.get("X Axis"), axes.get("Y Axis")
                )
        for name in sorted(expected):
            with self.subTest(table=name):
                self.assertEqual(
                    params[name], ("X_VQ_Engine_Load", "X_VQ_Engine_Speed")
                )


if __name__ == "__main__":
    unittest.main()
