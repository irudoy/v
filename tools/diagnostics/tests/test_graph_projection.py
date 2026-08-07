from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "memgraph"))
sys.path.insert(0, str(ROOT / "tools" / "diagnostics"))

import ingest_diagnostics  # noqa: E402


class DiagnosticProjectionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = ingest_diagnostics.load_catalog()
        cls.projection = ingest_diagnostics.collect_projection(cls.catalog)

    def test_dataset_and_projection_counts(self) -> None:
        self.assertEqual(6, len(self.catalog.datasets))
        expected = {
            "SourcePack": 6,
            "SourceDocument": 45,
            "SourceFragment": 5138,
            "DtcDefinition": 1635,
            "RomDtcDescriptor": 889,
            "DiagnosticParameter": 2455,
            "ParameterDefinition": 3773,
            "DiagnosticRequest": 872,
            "DiagnosticOperation": 356,
            "CanSignalDefinition": 228,
            "CanFrameDefinition": 46,
            "CanSignalBinding": 10,
        }
        counts = ingest_diagnostics.projection_counts(self.projection)
        for label, count in expected.items():
            self.assertEqual(count, counts[label], label)

    def test_every_claim_rests_on_a_source_fragment(self) -> None:
        source_edges = self.projection["claim_source"]
        by_label = {}
        for edge in source_edges:
            by_label.setdefault(edge["label"], set()).add(edge["from"])
        for label in (
            "DtcDefinition",
            "DiagnosticSection",
            "RomDtcDescriptor",
            "ParameterDefinition",
            "DiagnosticRequest",
            "DiagnosticOperation",
            "CanSignalDefinition",
            "CanFrameDefinition",
            "CanSignalBinding",
        ):
            claims = {row["id"] for row in self.projection[label]}
            self.assertEqual(claims, by_label.get(label, set()), label)

    def test_active_operations_are_not_executable(self) -> None:
        operations = self.projection["DiagnosticOperation"]
        self.assertTrue(operations)
        self.assertTrue(all(row["executable"] is False for row in operations))

    def test_request_inputs_are_not_return_values(self) -> None:
        inputs = self.projection["request_input_parameter"]
        outputs = self.projection["request_output_parameter"]
        self.assertEqual(105, len(inputs))
        self.assertEqual(1344, len(outputs))
        self.assertEqual({"send"}, {row["direction"] for row in inputs})
        self.assertNotIn("send", {row.get("direction") for row in outputs})
        self.assertTrue(
            {row["id"] for row in inputs}.isdisjoint(
                {row.get("id") for row in outputs if row.get("id")}
            )
        )

    def test_binding_only_can_signals_exist_in_projection(self) -> None:
        defined = {edge["to"] for edge in self.projection["signal_definition"]}
        bound = {edge["to"] for edge in self.projection["binding_signal"]}
        self.assertTrue(bound - defined)

    def test_replacement_audits_inside_the_transaction(self) -> None:
        calls = []
        with (
            patch.object(
                ingest_diagnostics,
                "delete_graph_scope_claims",
                side_effect=lambda _tx: calls.append("delete"),
            ),
            patch.object(
                ingest_diagnostics,
                "write_projection",
                side_effect=lambda _tx, _projection: calls.append("write"),
            ),
            patch.object(
                ingest_diagnostics,
                "cleanup_orphans",
                side_effect=lambda _tx: calls.append("cleanup"),
            ),
            patch.object(
                ingest_diagnostics,
                "audit",
                side_effect=lambda _tx, _counts: calls.append("audit"),
            ),
        ):
            ingest_diagnostics.replace_projection(object(), {}, {})
        self.assertEqual(["delete", "write", "cleanup", "audit"], calls)

    def test_corpus_replacement_invalidates_static_bindings(self) -> None:
        queries = []

        class Result:
            @staticmethod
            def consume():
                return None

        class Transaction:
            @staticmethod
            def run(query, **_parameters):
                queries.append(query)
                return Result()

        ingest_diagnostics.delete_graph_scope_claims(Transaction())
        self.assertIn(
            "MATCH (b:DiagnosticBinding) DETACH DELETE b",
            queries,
        )


if __name__ == "__main__":
    unittest.main()
