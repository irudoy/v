import sys
from pathlib import Path
import tempfile
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if "neo4j" not in sys.modules:
    neo4j = types.ModuleType("neo4j")
    neo4j.GraphDatabase = object
    sys.modules["neo4j"] = neo4j

import ingest  # noqa: E402
import load_code  # noqa: E402
from kb import l0 as kb_l0  # noqa: E402


class ExportValidationTest(unittest.TestCase):
    def valid_exports(self):
        return {
            "funcs.csv": [
                {
                    "addr": "00000010", "size": "2",
                    "is_thunk": "false", "is_external": "false",
                },
                {
                    "addr": "00000020", "size": "4",
                    "is_thunk": "true", "is_external": "false",
                },
            ],
            "calls.csv": [{"src": "00000010", "dst": "00000020"}],
            "xrefs.csv": [
                {"func_addr": "00000010", "periph_addr": "ffff1000", "kind": "R"}
            ],
        }

    def test_headers_are_the_l0_columns(self):
        for name, header in ingest.EXPORT_HEADERS.items():
            with self.subTest(name=name):
                self.assertEqual(header, [column for column, _ in kb_l0.columns_of(name)])

    def test_valid_exports_return_function_inventory(self):
        addrs = ingest.validate_exports(self.valid_exports(), Path("/export"))
        self.assertEqual(addrs, {"00000010", "00000020"})

    def test_invalid_xref_address_is_rejected(self):
        exported = self.valid_exports()
        exported["xrefs.csv"][0]["periph_addr"] = "not-hex"
        with self.assertRaisesRegex(ingest.IngestError, "periph_addr"):
            ingest.validate_exports(exported, Path("/export"))

    def test_dangling_call_is_rejected(self):
        exported = self.valid_exports()
        exported["calls.csv"][0]["dst"] = "00000030"
        with self.assertRaisesRegex(ingest.IngestError, "absent from funcs.csv"):
            ingest.validate_exports(exported, Path("/export"))

    def test_dangling_xref_is_rejected(self):
        exported = self.valid_exports()
        exported["xrefs.csv"][0]["func_addr"] = "00000030"
        with self.assertRaisesRegex(ingest.IngestError, "absent from funcs.csv"):
            ingest.validate_exports(exported, Path("/export"))

    def test_dry_run_command_uses_stable_uv_prefix(self):
        shown = ingest.display_command(["/tmp/uv-python", "/repo/load.py", "JK03A"])
        self.assertEqual(
            shown[: len(ingest.STABLE_PYTHON)],
            ingest.STABLE_PYTHON,
        )
        self.assertEqual(
            shown[len(ingest.STABLE_PYTHON):],
            ["/repo/load.py", "JK03A"],
        )

    def test_binding_loader_runs_after_code_and_before_audit(self):
        paths = {
            "Map": Path("/defs/maps.csv"),
            "Axis": Path("/defs/axes.csv"),
        }
        steps = ingest.commands(
            Path("/export"),
            "TEST",
            Path("/defs/interp.csv"),
            paths,
            False,
        )
        scripts = [Path(command[1]).name for command in steps]
        self.assertEqual(
            scripts[-3:],
            [
                "load_code.py",
                "load_diagnostic_bindings.py",
                "provenance_report.py",
            ],
        )


class SourceCsvValidationTest(unittest.TestCase):
    def source(self, text):
        temp = tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False)
        self.addCleanup(Path(temp.name).unlink, missing_ok=True)
        temp.write(text)
        temp.close()
        return temp.name

    def test_extra_columns_are_rejected_before_projection(self):
        path = self.source("addr,role\n00000010,driver,extra\n")
        with self.assertRaisesRegex(load_code.LoadError, "extra columns"):
            load_code.read_rows(path, ["addr", "role"])

    def test_missing_columns_are_rejected_before_projection(self):
        path = self.source("addr,role\n00000010\n")
        with self.assertRaisesRegex(load_code.LoadError, "missing columns"):
            load_code.read_rows(path, ["addr", "role"])


class FakeTransaction:
    def __init__(self, rows):
        self.rows = rows

    def run(self, _query, **_parameters):
        return iter(self.rows)


class SourceProjectionTest(unittest.TestCase):
    def test_catalog_gap_is_rejected_before_projection(self):
        with self.assertRaisesRegex(load_code.LoadError, "catalog gaps"):
            load_code.require_no_gaps(["Func:00000010.confidence from_map:00001000"])

    def test_missing_source_node_is_rejected(self):
        rows = [{
            "addr": "00000010", "scale_conf": "candidate", "scale_evidence": "",
        }]
        with self.assertRaisesRegex(load_code.LoadError, "missing nodes"):
            load_code.check_source_claim_properties(
                FakeTransaction([]), "TEST", "Axis", rows
            )

    def test_stale_source_property_is_rejected(self):
        rows = [{
            "addr": "00000010", "scale_conf": "candidate", "scale_evidence": "",
        }]
        graph = [{
            "addr": "00000010", "scale_conf": "pattern", "scale_evidence": "",
        }]
        with self.assertRaisesRegex(load_code.LoadError, "scale_conf"):
            load_code.check_source_claim_properties(
                FakeTransaction(graph), "TEST", "Axis", rows
            )


class SourceEvidenceGateTest(unittest.TestCase):
    @staticmethod
    def map_row(**updates):
        row = {
            "addr": "00000010",
            "confidence": "",
            "evidence": "",
            "scale_conf": "",
            "scale_evidence": "",
        }
        row.update(updates)
        return row

    @staticmethod
    def axis_row(**updates):
        row = {
            "addr": "00000020",
            "scale_conf": "",
            "scale_evidence": "",
        }
        row.update(updates)
        return row

    @staticmethod
    def claims(label, row):
        return load_code.source_claims("TEST", [(label, [row], "fixture.csv")])

    def test_map_semantics_code_without_evidence_is_rejected(self):
        with self.assertRaisesRegex(load_code.LoadError, "Map:00000010.confidence"):
            self.claims("Map", self.map_row(confidence="code"))

    def test_map_scale_silicon_without_evidence_is_rejected(self):
        with self.assertRaisesRegex(load_code.LoadError, "Map:00000010.scale_conf"):
            self.claims("Map", self.map_row(scale_conf="silicon"))

    def test_axis_scale_code_without_evidence_is_rejected(self):
        with self.assertRaisesRegex(load_code.LoadError, "Axis:00000020.scale_conf"):
            self.claims("Axis", self.axis_row(scale_conf="code"))

    def test_process_metadata_is_not_factual_evidence(self):
        with self.assertRaisesRegex(load_code.LoadError, "without evidence"):
            self.claims(
                "Map",
                self.map_row(
                    confidence="code", evidence="wave:backfill;arg:00000010"
                ),
            )

    def test_factual_terminal_passes_local_gate(self):
        claims = self.claims(
            "Axis",
            self.axis_row(scale_conf="code", scale_evidence="site:00000030"),
        )
        self.assertEqual(len(claims), 1)
        self.assertTrue(claims[0]["strict"])

    def test_candidate_without_evidence_is_allowed(self):
        claims = self.claims(
            "Map",
            self.map_row(confidence="candidate", scale_conf="candidate"),
        )
        self.assertEqual(len(claims), 2)

    def test_semantics_and_scale_evidence_are_independent(self):
        row = self.map_row(
            confidence="code",
            evidence="site:00000030",
            scale_conf="code",
            scale_evidence="arg:scale-only",
        )
        with self.assertRaisesRegex(load_code.LoadError, "Map:00000010.scale_conf"):
            self.claims("Map", row)


if __name__ == "__main__":
    unittest.main()
