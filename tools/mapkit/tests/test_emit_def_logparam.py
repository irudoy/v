import csv
from pathlib import Path
import tomllib
import unittest
import xml.etree.ElementTree as ET

from tools.can_dashboard import live_feed, model
from tools.logs import can_telemetry
from tools.mapkit import emit_def


ROOT = Path(__file__).resolve().parents[3]
SOURCE_ROM = "JK08A"

BINDINGS = {
    "logparam": {
        "ffff11ae": {"id": "X_VQ_Engine_Speed", "units": "RPM"},
        "ffff102c": {"id": "X_VQ_Engine_Load", "units": "Normalized BFS [%]"},
        "ffff106f": {
            "id": "X_VQ_Coolant_Temperature",
            "static_axis_name": "Coolant Temperature [deg C]",
        },
    }
}


def implicit_map(**changes):
    row = {
        "addr": "000126e4",
        "confidence": "code",
        "evidence": (
            "consumer:0004fbe2@structural;indexed_by:ffff106f@structural;"
            "indexed_by:ffff11b3@structural;site:0004fc02"
        ),
    }
    row.update(changes)
    return row


def labelled_table(**changes):
    row = {
        "static_axis": [-40, -30, -20, -10, 0, 10, 20, 30],
        "static_axis_name": "Coolant Temperature [deg C]",
        "static_axis_operand": "ffff106f",
    }
    row.update(changes)
    return row


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


def stream_fields():
    """Return the fields of the telemetry profile, fixed pages and context tags."""
    path = ROOT / "patches" / "can-telemetry-profile.toml"
    with path.open("rb") as stream:
        profile = tomllib.load(stream)
    return list(profile["field"]) + [
        field for context in profile["context"] for field in context["field"]
    ]


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

    def test_a_declared_scale_binds_an_axis_of_any_confidence(self):
        # The overlay compares domains, so a declaration that repeats the axis
        # expression binds the axis while the physical quantity stays a candidate.
        declared = {
            "logparam": {
                "ffff11ae": {
                    "id": "X_VQ_Engine_Speed",
                    "units": "RPM",
                    "scale": "x*50",
                }
            }
        }
        self.assertEqual(
            emit_def.axis_logparam(axis(scale_conf="candidate"), declared),
            "X_VQ_Engine_Speed",
        )
        self.assertEqual(
            emit_def.axis_logparam(axis(), declared), "X_VQ_Engine_Speed"
        )

    def test_a_scale_other_than_the_axis_expression_stays_without_live_data(self):
        declared = {
            "logparam": {
                "ffff11ae": {
                    "id": "X_VQ_Engine_Speed",
                    "units": "RPM",
                    "scale": "x*12.5",
                }
            }
        }
        for conf in ("candidate", "code"):
            with self.subTest(scale_conf=conf):
                self.assertIsNone(
                    emit_def.axis_logparam(axis(scale_conf=conf), declared)
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
            {"logparam": {"ffff11ae": {"units": "RPM"}}},
            {"logparam": {"ffff11ae": {"id": "X_A", "static_axis_name": ""}}},
            {"logparam": {"ffff11ae": {"id": "", "units": "RPM"}}},
            {"logparam": {"ffff11ae": {"id": "X A", "units": "RPM"}}},
            {"logparam": {"ffff11ae": {"id": "X_A", "units": 1}}},
            {"logparam": {"ffff11ae": {"id": "X_A", "units": "RPM", "x": 1}}},
            {"logparam": {"ffff11ae": {"id": "X_A", "units": "RPM", "scale": ""}}},
            # A scale is the expression of stored points, which static labels lack.
            {
                "logparam": {
                    "ffff11ae": {
                        "id": "X_A",
                        "static_axis_name": "Engine Speed [RPM]",
                        "scale": "x*50",
                    }
                }
            },
        )
        for overrides in rejected:
            with self.subTest(overrides=overrides):
                with self.assertRaises(SystemExit):
                    emit_def.logparam_bindings(overrides)
        self.assertEqual(emit_def.logparam_bindings({}), {})
        binding = emit_def.logparam_bindings(BINDINGS)["ffff102c"]
        self.assertEqual(binding.id, "X_VQ_Engine_Load")
        self.assertEqual(binding.units, "Normalized BFS [%]")
        self.assertIsNone(binding.scale)
        self.assertIsNone(binding.static_axis_name)

    def test_tracked_declaration_names_published_feed_parameters(self):
        published = {channel.logger_id for channel in live_feed.CHANNELS}
        bindings = emit_def.logparam_bindings(tracked_overrides())
        self.assertTrue(bindings)
        for operand, binding in bindings.items():
            with self.subTest(operand=operand):
                self.assertIn(binding.id, published)

    def test_tracked_declarations_publish_the_domain_of_their_axes(self):
        # Overlay Log places the published value on the stored points of every
        # axis a declaration binds. Where the operand is a stream field, the chain
        # is checked end to end: the operand address names the field, the
        # dashboard converts that field into the value the channel publishes, and
        # the axis expression is that conversion of the stored point times the
        # power of two its interpolation core multiplies each point by. A declared
        # scale is the conversion itself, so its multiplier is one.
        overrides = tracked_overrides()
        declarations = emit_def.logparam_bindings(overrides)
        fields = {
            field["source"]: field["name"]
            for field in stream_fields()
            if "source" in field
        }
        channels = {channel.logger_id: channel for channel in live_feed.CHANNELS}
        conversions = {
            calibration.target: (source, calibration)
            for table in (
                can_telemetry.RAW_CALIBRATIONS,
                model.DASHBOARD_CALIBRATIONS,
            )
            for source, calibration in table.items()
        }
        checked = set()
        for row in tracked_axes().values():
            parameter = emit_def.axis_logparam(row, overrides)
            if not parameter:
                continue
            (operand,) = [
                token.target_addr
                for token in emit_def.provenance.parse_evidence(
                    row["scale_evidence"], "scale_conf"
                )
                if token.role == "indexed_by"
            ]
            field = fields.get(int(operand, 16))
            if field is None:
                continue
            with self.subTest(axis=row["addr"], operand=operand):
                source, calibration = conversions[channels[parameter].source]
                self.assertEqual(source, field)
                self.assertEqual(calibration.offset, 0)
                point = eval(  # the scaling vocabulary the ledger validates
                    row["scale_expr"], {"__builtins__": {}}, {"x": 1}
                )
                multiplier = point / calibration.factor
                declared = declarations[operand].scale
                self.assertIn(
                    round(multiplier),
                    (1,) if declared else tuple(1 << shift for shift in range(8)),
                )
                self.assertAlmostEqual(multiplier, round(multiplier))
                if declared:
                    for raw in (0, 1, 1000, 3172):
                        self.assertAlmostEqual(
                            calibration.apply(raw),
                            eval(declared, {"__builtins__": {}}, {"x": raw}),
                        )
            checked.add(row["addr"])
        # The throttle target axis, a load axis, and a speed axis whose core
        # multiplies each point by four.
        self.assertLessEqual({"000155a0", "00011ebe", "00011cf0"}, checked)

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
        for table in overrides["table"].values():
            operand = table.get("static_axis_operand")
            if operand:
                used.add(operand)
        self.assertEqual(used, set(emit_def.logparam_bindings(overrides)))


class StaticAxisLogparamRuleTest(unittest.TestCase):
    def test_labels_of_a_declared_operand_name_the_parameter(self):
        self.assertEqual(
            emit_def.static_axis_logparam(
                implicit_map(), labelled_table(), BINDINGS
            ),
            "X_VQ_Coolant_Temperature",
        )

    def test_a_table_without_the_declaration_stays_without_live_data(self):
        self.assertIsNone(
            emit_def.static_axis_logparam(
                implicit_map(),
                labelled_table(static_axis_operand=None),
                BINDINGS,
            )
        )

    def test_an_operand_outside_the_map_evidence_stops_generation(self):
        with self.assertRaises(SystemExit):
            emit_def.static_axis_logparam(
                implicit_map(evidence="consumer:0004fbe2@structural"),
                labelled_table(),
                BINDINGS,
            )

    def test_an_undeclared_operand_stops_generation(self):
        with self.assertRaises(SystemExit):
            emit_def.static_axis_logparam(
                implicit_map(), labelled_table(), {"logparam": {}}
            )

    def test_an_axis_name_other_than_the_declared_name_stops_generation(self):
        with self.assertRaises(SystemExit):
            emit_def.static_axis_logparam(
                implicit_map(),
                labelled_table(static_axis_name="Coolant Temperature"),
                BINDINGS,
            )

    def test_a_rom_axis_declaration_does_not_reach_static_labels(self):
        with self.assertRaises(SystemExit):
            emit_def.static_axis_logparam(
                implicit_map(evidence="indexed_by:ffff11ae@structural"),
                labelled_table(
                    static_axis_operand="ffff11ae",
                    static_axis_name="Engine Speed [RPM]",
                ),
                BINDINGS,
            )

    def test_a_relocated_map_keeps_its_labels_without_live_data(self):
        self.assertIsNone(
            emit_def.static_axis_logparam(
                implicit_map(confidence="candidate"), labelled_table(),
                BINDINGS,
            )
        )

    def test_a_declaration_without_labels_stops_generation(self):
        table = labelled_table()
        del table["static_axis"]
        with self.assertRaises(SystemExit):
            emit_def.static_axis_logparam(implicit_map(), table, BINDINGS)

    def test_static_axis_xml_carries_the_attribute_only_when_bound(self):
        bound = "\n".join(emit_def.static_axis_xml(
            [-40, -30], "Coolant Temperature [deg C]",
            logparam="X_VQ_Coolant_Temperature",
        ))
        self.assertIn('logparam="X_VQ_Coolant_Temperature"', bound)
        ET.fromstring(bound)
        unbound = "\n".join(emit_def.static_axis_xml([-40, -30], "Index"))
        self.assertNotIn("logparam", unbound)


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

    def test_every_static_axis_follows_the_declared_rule(self):
        bound = set()
        for table in self.rom.findall("table"):
            for element in table.findall("table"):
                if not element.get("type", "").startswith("Static"):
                    continue
                if element.get("logparam"):
                    bound.add((table.get("name"), element.get("logparam")))
                    self.assertIsNotNone(element.get("name"))
        parameters = {parameter for _name, parameter in bound}
        self.assertEqual(
            parameters,
            {"X_VQ_Coolant_Temperature", "X_VQ_Engine_Speed"},
        )

    def test_coolant_and_speed_curves_support_the_overlay(self):
        expected = {
            "Map 1 - DFCO Entry RPM Threshold": "X_VQ_Coolant_Temperature",
            "Map 5 - DFCO Hold RPM Threshold": "X_VQ_Coolant_Temperature",
            "Map 1 - Timing-State Addend - Default/Post-Transition":
                "X_VQ_Engine_Speed",
            "End of Injection Angle - Base": "X_VQ_Engine_Speed",
            "End of Injection Angle - Conditional": "X_VQ_Engine_Speed",
        }
        found = {}
        for table in self.rom.findall("table"):
            for element in table.findall("table"):
                if element.get("logparam") and element.get(
                        "type", "").startswith("Static"):
                    found[table.get("name")] = element.get("logparam")
        for name, parameter in expected.items():
            with self.subTest(table=name):
                self.assertEqual(found.get(name), parameter)

    def surface_parameters(self):
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
        return params

    def test_load_and_speed_surfaces_support_the_overlay(self):
        expected = {
            "Ignition Timing Surface - Cold State",
            "Map 1 - Ignition Timing Surface - High-Octane State",
            "Map 5 - Ignition Timing Surface - High-Detonation State",
            "Target Mixture - Main",
            "Intake CVTC Target - Main",
            "Engine Torque Surface",
        }
        params = self.surface_parameters()
        for name in sorted(expected):
            with self.subTest(table=name):
                self.assertEqual(
                    params[name], ("X_VQ_Engine_Load", "X_VQ_Engine_Speed")
                )

    def test_fuel_compensation_rows_follow_engine_speed(self):
        # The column coordinate 0xFFFF1170 has no feed parameter, so the
        # surfaces follow engine speed on the rows alone.
        params = self.surface_parameters()
        for index in range(1, 6):
            name = f"Map {index} - Fuel Compensation - Main"
            with self.subTest(table=name):
                self.assertEqual(params[name], (None, "X_VQ_Engine_Speed"))

    def test_requested_torque_conversion_rows_follow_engine_speed(self):
        # The column coordinates 0xFFFF1980 and 0xFFFF1D0E have no feed
        # parameter, so the surfaces follow engine speed on the rows alone.
        params = self.surface_parameters()
        for name in (
            "Requested Torque Conversion by QH0 - Primary",
            "Requested Torque Conversion by QH0 - Validation Copy",
        ):
            with self.subTest(table=name):
                self.assertEqual(params[name], (None, "X_VQ_Engine_Speed"))


if __name__ == "__main__":
    unittest.main()
