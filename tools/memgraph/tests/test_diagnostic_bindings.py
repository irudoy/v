from pathlib import Path
import sys
import types
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

if "neo4j" not in sys.modules:
    neo4j = types.ModuleType("neo4j")
    neo4j.GraphDatabase = object
    sys.modules["neo4j"] = neo4j

import load_diagnostic_bindings as bindings  # noqa: E402
import rom_sources  # noqa: E402


class BindingSourceTest(unittest.TestCase):
    @staticmethod
    def row(**updates):
        row = {
            "id": "engine-speed",
            "kind": "runtime_value",
            "firmware_label": "Reg",
            "firmware_addr": "ffff11ae",
            "diagnostic_label": "DiagnosticParameter",
            "diagnostic_key": "diagnostic-parameter:semantic:eng-speed",
            "source_claim_label": "ParameterDefinition",
            "source_claim_id": "manual:eng-speed",
            "confidence": "code",
            "applicability": "homologous_vq35hr",
            "rom_scope": "exact-code",
            "priority": "90",
            "evidence": "indexed_by:ffff11ae@confidence;site:000832b6",
            "note": "",
        }
        row.update(updates)
        return row

    def test_valid_row_is_typed(self):
        rows = bindings.validate_rows([self.row()], "fixture.csv")
        self.assertEqual(rows[0]["priority"], 90)
        self.assertEqual(len(rows[0]["tokens"]), 2)

    def test_every_claim_requires_machine_anchor(self):
        with self.assertRaisesRegex(
            bindings.BindingError, "machine-address anchor"
        ):
            bindings.validate_rows(
                [
                    self.row(
                        confidence="candidate",
                        evidence="registry:manual",
                    )
                ],
                "fixture.csv",
            )

    def test_silicon_confidence_is_outside_static_scope(self):
        with self.assertRaisesRegex(bindings.BindingError, "confidence"):
            bindings.validate_rows(
                [self.row(confidence="silicon")], "fixture.csv"
            )

    def test_source_claim_must_match_diagnostic_type(self):
        with self.assertRaisesRegex(bindings.BindingError, "cannot support"):
            bindings.validate_rows(
                [self.row(source_claim_label="RomDtcDescriptor")],
                "fixture.csv",
            )

    def test_exact_rom_rows_do_not_inherit(self):
        model = rom_sources.SourceModel(
            target="JK03A", source="JK08A", kind="exact-code"
        )
        rows = bindings.validate_rows(
            [
                self.row(id="shared"),
                self.row(id="target-only", rom_scope="exact-rom"),
            ],
            "fixture.csv",
        )
        materialized = bindings.materialize_rows(model, rows)
        self.assertEqual([row["id"] for row in materialized], ["shared"])

    def test_tracked_jk08a_projection_has_explicit_scope(self):
        path = Path(__file__).resolve().parents[3] / (
            "defs/JK08A.diagnostic-bindings.csv"
        )
        rows = bindings.validate_rows(bindings.read_rows(path), path)
        inherited = bindings.materialize_rows(
            rom_sources.resolve("JK03A"), rows
        )
        self.assertEqual(len(rows), 25)
        self.assertEqual(len(inherited), 9)
        self.assertEqual(
            sum(row["rom_scope"] == "exact-rom" for row in rows), 16
        )
        self.assertTrue(
            any(row["kind"] == "calibration_context" for row in rows)
        )
        self.assertEqual(
            {
                row["id"]
                for row in rows
                if row["id"].startswith(("injection-pulse-", "intake-valve-"))
            },
            {
                "injection-pulse-bank-1",
                "injection-pulse-bank-2",
                "intake-valve-timing-bank-1",
            },
        )
        by_id = {row["id"]: row for row in rows}
        for binding_id in (
            "injection-pulse-bank-1",
            "injection-pulse-bank-2",
        ):
            self.assertIn(
                "writes:0004eba2@structural",
                by_id[binding_id]["evidence"],
            )
            self.assertIn(
                "from_map:000129c0@structural",
                by_id[binding_id]["evidence"],
            )
        self.assertIn(
            "writes:000bd9f0@structural",
            by_id["intake-valve-timing-bank-1"]["evidence"],
        )


class FakeResult:
    def __init__(self, row):
        self.row = row

    def single(self):
        return FakeRecord(self.row) if self.row is not None else None


class FakeRecord(dict):
    def data(self):
        return dict(self)


class FakeTransaction:
    def __init__(self, answers):
        self.answers = iter(answers)

    def run(self, _query, **_parameters):
        return FakeResult(next(self.answers))


class BindingResolutionTest(unittest.TestCase):
    def test_declared_confidence_cannot_exceed_firmware_target(self):
        row = BindingSourceTest.row()
        validated = bindings.validate_rows([row], "fixture.csv")
        tx = FakeTransaction([
            {"confidence": "candidate", "semantics": "", "note": ""},
        ])
        with self.assertRaisesRegex(
            bindings.BindingError, "exceeds firmware target confidence"
        ):
            bindings.resolve_rows(tx, "TEST", validated)

    def test_axis_binding_uses_scale_confidence(self):
        row = BindingSourceTest.row(
            firmware_label="Axis",
            confidence="code",
            evidence="site:00000030",
        )
        validated = bindings.validate_rows([row], "fixture.csv")
        tx = FakeTransaction([
            {
                "confidence": "pattern",
                "scale_conf": "code",
                "semantics": "",
                "note": "",
            },
            {
                "name": "Engine speed",
                "source_applicability": "homologous_vq35hr",
                "source_verification": "factory_documented",
                "source_dataset_id": "fixture",
            },
        ])
        resolved = bindings.resolve_rows(tx, "TEST", validated)
        self.assertEqual(resolved[0]["firmware_confidence_prop"], "scale_conf")
        self.assertEqual(resolved[0]["firmware_confidence"], "code")


if __name__ == "__main__":
    unittest.main()
