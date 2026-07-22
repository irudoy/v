import sys
from pathlib import Path
import types
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if "neo4j" not in sys.modules:
    neo4j = types.ModuleType("neo4j")
    neo4j.GraphDatabase = object
    sys.modules["neo4j"] = neo4j

import ingest  # noqa: E402
import load_code  # noqa: E402


class ExportValidationTest(unittest.TestCase):
    def valid_exports(self):
        return {
            "funcs.csv": [
                {
                    "addr": "00000010", "name": "first", "size": "2",
                    "is_thunk": "false", "is_external": "false",
                },
                {
                    "addr": "00000020", "name": "second", "size": "4",
                    "is_thunk": "true", "is_external": "false",
                },
            ],
            "calls.csv": [{"src": "00000010", "dst": "00000020"}],
            "xrefs.csv": [
                {"func_addr": "00000010", "periph_addr": "ffff1000", "kind": "R"}
            ],
        }

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
        with self.assertRaisesRegex(ingest.IngestError, "отсутствует в funcs.csv"):
            ingest.validate_exports(exported, Path("/export"))

    def test_dangling_xref_is_rejected(self):
        exported = self.valid_exports()
        exported["xrefs.csv"][0]["func_addr"] = "00000030"
        with self.assertRaisesRegex(ingest.IngestError, "отсутствует в funcs.csv"):
            ingest.validate_exports(exported, Path("/export"))

    def test_dry_run_command_uses_stable_uv_prefix(self):
        shown = ingest.display_command(["/tmp/uv-python", "/repo/load.py", "JK03A"])
        self.assertEqual(shown[:6], ingest.STABLE_PYTHON)
        self.assertEqual(shown[6:], ["/repo/load.py", "JK03A"])


class FakeTransaction:
    def __init__(self, rows):
        self.rows = rows

    def run(self, _query, **_parameters):
        return iter(self.rows)


class SourceProjectionTest(unittest.TestCase):
    def test_catalog_gap_is_rejected_before_projection(self):
        with self.assertRaisesRegex(load_code.LoadError, "пробелы каталога"):
            load_code.require_no_gaps(["Func:00000010.confidence from_map:00001000"])

    def test_missing_source_node_is_rejected(self):
        rows = [{
            "addr": "00000010", "scale_conf": "candidate", "scale_evidence": "",
        }]
        with self.assertRaisesRegex(load_code.LoadError, "нет узлов"):
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


if __name__ == "__main__":
    unittest.main()
