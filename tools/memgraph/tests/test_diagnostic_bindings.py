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

    def test_homologous_community_applicability_is_supported(self):
        rows = bindings.validate_rows(
            [self.row(applicability="homologous_community")],
            "fixture.csv",
        )
        self.assertEqual(rows[0]["applicability"], "homologous_community")

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
        self.assertEqual(len(rows), 149)
        self.assertEqual(len(inherited), 33)
        self.assertEqual(
            sum(row["rom_scope"] == "exact-rom" for row in rows), 116
        )
        self.assertTrue(
            any(row["kind"] == "calibration_context" for row in rows)
        )
        self.assertEqual(
            {
                row["id"]
                for row in rows
                if row["id"].startswith((
                    "ignition-timing-did-",
                    "short-term-fuel-trim-",
                    "long-term-fuel-trim-",
                    "injection-pulse-",
                    "intake-valve-",
                    "accelerator-pedal-position-",
                ))
            },
            {
                "ignition-timing-did-1107",
                "ignition-timing-did-1108",
                "ignition-timing-did-1109",
                "ignition-timing-did-110a",
                "short-term-fuel-trim-bank-1-did-1123",
                "short-term-fuel-trim-bank-2-did-1124",
                "long-term-fuel-trim-bank-1-did-1125",
                "long-term-fuel-trim-bank-2-did-1126",
                "injection-pulse-bank-1",
                "injection-pulse-bank-2",
                "intake-valve-timing-bank-1",
                "accelerator-pedal-position-1",
                "accelerator-pedal-position-2",
            },
        )
        by_id = {row["id"]: row for row in rows}
        maf_targets = {
            "mass-airflow-sensor-bank-1-did-1204": (
                "ffff101c", "diagnostic-parameter:request:221204"
            ),
            "mass-airflow-sensor-bank-2-did-1205": (
                "ffff101e", "diagnostic-parameter:request:221205"
            ),
            "mass-airflow-rate-did-1209": (
                "ffff3852", "diagnostic-parameter:request:221209"
            ),
        }
        for binding_id, (firmware_addr, diagnostic_key) in maf_targets.items():
            self.assertEqual(by_id[binding_id]["firmware_addr"], firmware_addr)
            self.assertEqual(by_id[binding_id]["diagnostic_key"], diagnostic_key)
            self.assertEqual(by_id[binding_id]["rom_scope"], "exact-code")
            self.assertEqual(by_id[binding_id]["confidence"], "code")
        self.assertEqual(
            by_id["maf-transfer-bank-1"]["firmware_addr"], "00014274"
        )
        self.assertEqual(
            by_id["maf-transfer-bank-2"]["firmware_addr"], "000141f4"
        )
        misfire_ids = {
            *(f"misfire-result-dispatch-p030{cylinder}" for cylinder in range(7)),
            *(f"misfire-coordinator-p030{cylinder}" for cylinder in range(7)),
            *(f"misfire-detection-core-p030{cylinder}" for cylinder in range(7)),
            "misfire-aggregate-select-p0300",
            *(f"misfire-cylinder-select-p030{cylinder}" for cylinder in range(1, 7)),
        }
        self.assertEqual(
            {row["id"] for row in rows if row["id"].startswith("misfire-")},
            misfire_ids,
        )
        for binding_id in misfire_ids:
            self.assertEqual(by_id[binding_id]["rom_scope"], "exact-rom")
            self.assertEqual(by_id[binding_id]["applicability"], "exact_rom")
        self.assertEqual(
            by_id["misfire-result-dispatch-p0306"]["source_claim_id"],
            "jk08a:000193d8",
        )
        self.assertEqual(
            by_id["misfire-result-dispatch-p0300"]["source_claim_id"],
            "jk08a:00019420",
        )
        rear_o2_and_catalyst_ids = {
            "rear-o2-main-slow-response-p0139",
            "rear-o2-main-slow-response-p0159",
            "rear-o2-main-low-p0137",
            "rear-o2-main-low-p0157",
            "rear-o2-main-high-a-p0138",
            "rear-o2-main-high-a-p0158",
            "rear-o2-alt-high-b-p0138",
            "rear-o2-alt-high-b-p0158",
            "rear-o2-slow-metric-a-p0139",
            "rear-o2-slow-metric-a-p0159",
            "rear-o2-slow-metric-b-p0139",
            "rear-o2-slow-metric-b-p0159",
            "rear-o2-low-metric-p0137",
            "rear-o2-low-metric-p0157",
            "rear-o2-high-a-metric-p0138",
            "rear-o2-high-a-metric-p0158",
            "rear-o2-high-b-working-a-p0138",
            "rear-o2-high-b-working-a-p0158",
            "rear-o2-high-b-working-b-p0138",
            "rear-o2-high-b-working-b-p0158",
            "catalyst-result-dispatch-p0420",
            "catalyst-result-dispatch-p0430",
            "catalyst-limit-monitor-p0420",
            "catalyst-limit-monitor-p0430",
            "catalyst-limit-accessor-p0420",
            "catalyst-limit-accessor-p0430",
            "catalyst-limit-table-p0420",
            "catalyst-limit-table-p0430",
            "catalyst-limit-state-p0420",
            "catalyst-limit-state-p0430",
            "catalyst-metric-p0420",
            "catalyst-metric-p0430",
            "rear-o2-heater-monitor-high-p0038",
            "rear-o2-heater-monitor-high-p0058",
            "rear-o2-heater-monitor-low-p0037",
            "rear-o2-heater-monitor-low-p0057",
            "rear-o2-heater-feedback-high-p0038",
            "rear-o2-heater-feedback-high-p0058",
            "rear-o2-heater-feedback-low-p0037",
            "rear-o2-heater-feedback-low-p0057",
        }
        self.assertEqual(
            {
                row["id"]
                for row in rows
                if row["id"].startswith(("rear-o2-", "catalyst-"))
            },
            rear_o2_and_catalyst_ids,
        )
        for binding_id in rear_o2_and_catalyst_ids:
            self.assertEqual(by_id[binding_id]["rom_scope"], "exact-rom")
            self.assertEqual(
                by_id[binding_id]["applicability"], "exact_rom"
            )
        self.assertEqual(
            by_id["rear-o2-main-high-a-p0138"]["source_claim_id"],
            "jk08a:00019b4c",
        )
        self.assertEqual(
            by_id["rear-o2-alt-high-b-p0138"]["source_claim_id"],
            "jk08a:00019b7c",
        )
        self.assertEqual(
            by_id["catalyst-limit-table-p0420"]["firmware_addr"],
            "00011fb6",
        )
        self.assertIn(
            "consumer:000a2f56@confidence",
            by_id["catalyst-limit-table-p0420"]["evidence"],
        )
        heater_did_ids = {
            "ho2s2-heater-bank-1-did-130b",
            "ho2s2-heater-bank-2-did-130b",
        }
        self.assertTrue(
            heater_did_ids
            <= {row["id"] for row in inherited}
        )
        self.assertEqual(
            by_id["ho2s2-heater-bank-1-did-130b"]["diagnostic_key"],
            "diagnostic-parameter:semantic:cid-130bh-bit1-ho2s2-htr-b1",
        )
        self.assertEqual(
            by_id["ho2s2-heater-bank-2-did-130b"]["source_claim_id"],
            "ecudocs-p32m-997c5a9:data:cid-130bh-bit0-ho2s2-htr-b2-6435fe15",
        )
        for binding_id in heater_did_ids:
            self.assertEqual(by_id[binding_id]["rom_scope"], "exact-code")
            self.assertEqual(by_id[binding_id]["firmware_addr"], "ffff2c57")
            self.assertIn(
                "rom_const:00022a38=ffff2c57",
                by_id[binding_id]["evidence"],
            )
        evap_ids = {
            "evap-purge-circuit-p0443",
            "evap-vent-short-p0448",
            "evap-gross-leak-p0455",
            "evap-vent-open-a-p0447",
            "evap-pressure-range-p0451",
            "evap-purge-open-p0444",
            "evap-purge-short-p0445",
            "evap-pressure-low-p0452",
            "evap-pressure-high-p0453",
            "evap-purge-flow-p0441",
            "evap-vent-open-b-p0447",
            "evap-very-small-leak-result-p0456",
            "evap-small-leak-p0442",
            "evap-purge-circuit-producer-p0443",
            "evap-vent-short-state-p0448",
            "evap-gross-leak-metric-p0455",
            "evap-vent-open-a-state-p0447",
            "evap-pressure-range-metric-p0451",
            "evap-purge-open-state-p0444",
            "evap-purge-short-state-p0445",
            "evap-pressure-low-state-p0452",
            "evap-pressure-high-state-p0453",
            "evap-purge-flow-state-p0441",
            "evap-vent-open-b-input-p0447",
            "evap-very-small-leak-metric-p0456",
            "evap-small-leak-metric-p0442",
        }
        self.assertEqual(
            {
                row["id"]
                for row in rows
                if row["id"].startswith("evap-")
            },
            evap_ids,
        )
        for binding_id in evap_ids:
            self.assertEqual(by_id[binding_id]["rom_scope"], "exact-rom")
            self.assertEqual(by_id[binding_id]["applicability"], "exact_rom")
        self.assertEqual(
            by_id["evap-vent-open-a-p0447"]["source_claim_id"],
            "jk08a:000195ac",
        )
        self.assertEqual(
            by_id["evap-vent-open-b-p0447"]["source_claim_id"],
            "jk08a:00019d74",
        )
        self.assertIn(
            "rom_const:00018700=0x00",
            by_id["evap-vent-open-b-p0447"]["evidence"],
        )
        self.assertIn(
            "rom_const:0000850a=0x00",
            by_id["evap-purge-short-state-p0445"]["evidence"],
        )
        self.assertEqual(
            (
                by_id["evap-purge-circuit-producer-p0443"]["firmware_label"],
                by_id["evap-purge-circuit-producer-p0443"]["firmware_addr"],
            ),
            ("Func", "000acc54"),
        )
        self.assertFalse(
            any(
                row["diagnostic_key"] == "P0443"
                and row["firmware_label"] == "Reg"
                and row["firmware_addr"] == "ffff247f"
                for row in rows
            )
        )
        self.assertIn(
            "consumer:000b4ef8@structural",
            by_id["evap-very-small-leak-result-p0456"]["evidence"],
        )
        self.assertNotIn(
            "consumer:0007d8b8@structural",
            by_id["evap-very-small-leak-result-p0456"]["evidence"],
        )
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
        for binding_id in (
            "ignition-timing-did-1107",
            "ignition-timing-did-1108",
            "ignition-timing-did-1109",
            "ignition-timing-did-110a",
        ):
            self.assertEqual(by_id[binding_id]["firmware_addr"], "ffff2022")
            self.assertEqual(by_id[binding_id]["rom_scope"], "exact-code")
            self.assertIn(
                "writes:0004df82@structural",
                by_id[binding_id]["evidence"],
            )
            self.assertIn(
                "from_map:000147da@structural",
                by_id[binding_id]["evidence"],
            )
        fuel_trim_targets = {
            "short-term-fuel-trim-bank-1-did-1123": (
                "ffff22dc",
                "writes:0005c910@structural",
            ),
            "short-term-fuel-trim-bank-2-did-1124": (
                "ffff22de",
                "writes:0005c910@structural",
            ),
            "long-term-fuel-trim-bank-1-did-1125": (
                "ffff2302",
                "writes:00057b26@structural",
            ),
            "long-term-fuel-trim-bank-2-did-1126": (
                "ffff2304",
                "writes:00057b26@structural",
            ),
        }
        for binding_id, (firmware_addr, writer) in fuel_trim_targets.items():
            self.assertEqual(by_id[binding_id]["firmware_addr"], firmware_addr)
            self.assertEqual(by_id[binding_id]["rom_scope"], "exact-code")
            self.assertIn(writer, by_id[binding_id]["evidence"])
            self.assertIn(
                "consumer:00035856@structural",
                by_id[binding_id]["evidence"],
            )
        self.assertEqual(
            {
                row["id"]
                for row in inherited
                if row["id"].startswith("throttle-")
            },
            {
                "throttle-position-sensor-1-bank-1",
                "throttle-position-sensor-2-bank-1",
                "throttle-position-sensor-1-bank-2",
                "throttle-position-sensor-2-bank-2",
                "throttle-control-motor-relay",
            },
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
