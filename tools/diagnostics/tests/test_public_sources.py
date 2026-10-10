from __future__ import annotations

import argparse
import csv
import io
import json
import subprocess
import sys
import tomllib
import types
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "refs" / "diagnostics"
PUBLIC = ROOT / "refs" / "diagnostics" / "public"
sys.path.insert(0, str(ROOT / "tools" / "diagnostics"))

import query  # noqa: E402
import catalog  # noqa: E402


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(source))


class PublicCatalogTest(unittest.TestCase):
    def test_tracked_csv_files_use_lf_line_endings(self) -> None:
        csv_paths = sorted(CORPUS.rglob("*.csv"))
        self.assertTrue(csv_paths)
        for path in csv_paths:
            self.assertNotIn(b"\r\n", path.read_bytes(), str(path))

    def test_license_metadata_does_not_remove_source_packs(self) -> None:
        manifests = sorted(CORPUS.rglob("source_pack.toml"))
        packs = []
        for path in manifests:
            with path.open("rb") as source:
                packs.append(tomllib.load(source))
        self.assertEqual(7, len(packs))
        self.assertEqual(
            {
                "nissan-esm-2007-g35-sedan-v1",
                "nissan-esm-2013-g37-sedan-v1",
                "vq-hr-sh7058-rom-dtc-v1",
                "370z-can-logger-2025-07-05",
                "obd2tools-d27c9a2",
                "ecudocs-p32m-997c5a9",
                "generic-nissan-datatable-2003-v1",
            },
            {pack["id"] for pack in packs},
        )
        self.assertTrue(all(pack.get("license") for pack in packs))

    def test_expected_source_counts(self) -> None:
        expected = {
            "370z-can-logger": {
                "diagnostic_parameters.csv": 487,
                "diagnostic_requests.csv": 379,
                "can_frames.csv": 46,
                "can_signals.csv": 122,
                "can_bindings.csv": 10,
            },
            "obd2tools": {
                "diagnostic_parameters.csv": 847,
                "diagnostic_requests.csv": 372,
            },
            "ecudocs-p32m": {
                "diagnostic_parameters.csv": 1226,
                "diagnostic_requests.csv": 104,
                "request_parameters.csv": 698,
            },
            "nissan-datatable": {
                "diagnostic_parameters.csv": 93,
                "diagnostic_requests.csv": 17,
                "diagnostic_operations.csv": 40,
            },
        }
        for directory, files in expected.items():
            for filename, count in files.items():
                self.assertEqual(
                    count,
                    len(read_csv(PUBLIC / directory / filename)),
                    f"{directory}/{filename}",
                )

    def test_known_rpm_formula_conflict_is_preserved(self) -> None:
        logger = [
            row
            for row in read_csv(
                PUBLIC / "370z-can-logger" / "diagnostic_parameters.csv"
            )
            if row["request_hex"].lower() == "221201"
        ]
        obd2tools = [
            row
            for row in read_csv(PUBLIC / "obd2tools" / "diagnostic_parameters.csv")
            if row["request_hex"].lower() == "221201"
            and row["verification_status"] == "community_defined"
        ]
        p32m_requests = {
            row["id"]: row
            for row in read_csv(
                PUBLIC / "ecudocs-p32m" / "diagnostic_requests.csv"
            )
        }
        p32m_parameters = {
            row["id"]: row
            for row in read_csv(
                PUBLIC / "ecudocs-p32m" / "diagnostic_parameters.csv"
            )
        }
        p32m_links = read_csv(PUBLIC / "ecudocs-p32m" / "request_parameters.csv")
        linked = [
            p32m_parameters[link["parameter_id"]]
            for link in p32m_links
            if p32m_requests[link["request_id"]]["request_hex"].lower() == "221201"
            and link["direction"] == "receive"
        ]
        self.assertEqual(1, len(logger))
        self.assertEqual("12.5", obd2tools[0]["factor"])
        self.assertEqual("12.5", linked[0]["factor"])
        self.assertIn("*10", logger[0]["formula"].replace(" ", ""))

    def test_all_operations_remain_non_executable(self) -> None:
        for path in PUBLIC.rglob("diagnostic_operations.csv"):
            rows = read_csv(path)
            self.assertEqual({"false"}, {row["executable"] for row in rows})

    def test_dbc_export_has_no_unverified_source_data(self) -> None:
        bindings = read_csv(
            PUBLIC / "370z-can-logger" / "can_bindings.csv"
        )
        self.assertNotIn(
            "hardware_verified",
            {row["verification_status"] for row in bindings},
        )
        self.assertIn(
            "binding.verification_status = 'hardware_verified'",
            query.DBC_QUERY,
        )
        self.assertEqual(
            'VERSION "VQ diagnostic catalog hardware-verified export"',
            query.render_dbc([]).splitlines()[0],
        )

    def test_optional_dtc_evidence_drops_null_maps(self) -> None:
        rows = query.clean_optional_evidence(
            [
                {
                    "code": "B1033",
                    "descriptors": [{"rom": None, "index": None}],
                    "definitions": [{"title": "SENSOR", "dataset_id": "manual"}],
                    "details": [{"heading": None, "pdf_page": None}],
                }
            ]
        )
        self.assertEqual([], rows[0]["descriptors"])
        self.assertEqual([], rows[0]["details"])
        self.assertEqual(1, len(rows[0]["definitions"]))
        self.assertIn("RETURN DISTINCT rom.id AS rom", query.DTC_DESCRIPTOR_QUERY)

    def test_dtc_evidence_is_assembled_from_flat_queries(self) -> None:
        responses = {
            query.DTC_EXISTS_QUERY: [{"code": "U1000"}],
            query.DTC_DESCRIPTOR_QUERY: [{"rom": "JK08A", "index": 1}],
            query.DTC_DEFINITION_QUERY: [
                {"title": "CAN COMM CIRCUIT", "dataset_id": "manual"}
            ],
            query.DTC_DETAIL_QUERY: [
                {
                    "heading": "U1000 CAN COMM CIRCUIT",
                    "primary": True,
                    "pdf_page": 42,
                    "text": None,
                }
            ],
        }

        class Session:
            def __init__(self) -> None:
                self.calls: list[tuple[str, dict[str, object]]] = []

            def run(self, statement: str, **parameters: object) -> list[dict]:
                self.calls.append((statement, parameters))
                return responses[statement]

        session = Session()
        rows = query.query_dtc(
            session,
            "U1000",
            include_mentions=False,
            include_detail_text=False,
        )
        self.assertEqual(1, len(rows))
        self.assertEqual(1, len(rows[0]["descriptors"]))
        self.assertEqual(1, len(rows[0]["definitions"]))
        self.assertEqual(1, len(rows[0]["details"]))
        self.assertNotIn("text", rows[0]["details"][0])
        self.assertEqual(4, len(session.calls))
        self.assertFalse(
            any("collect(" in statement.lower() for statement, _ in session.calls)
        )

    def test_monitor_query_keeps_requests_with_their_source(self) -> None:
        self.assertIn(
            "request.dataset_id = definition.dataset_id",
            query.MONITOR_QUERY,
        )
        self.assertIn("$is_identifier", query.MONITOR_QUERY)
        self.assertIn("AS requests", query.MONITOR_QUERY)
        self.assertNotIn(
            "request.request_hex AS request_hex",
            query.MONITOR_QUERY,
        )

    def test_semantic_search_expands_domain_terms(self) -> None:
        self.assertEqual(
            ["intake", "valve", "timing"],
            query.semantic_search_tokens(" Intake valve timing "),
        )
        self.assertEqual(
            ["int/v", "intake camshaft"],
            query.semantic_search_aliases("intake valve timing"),
        )
        self.assertEqual(
            ["vvel"],
            query.semantic_search_aliases("Valve lift"),
        )
        self.assertEqual(
            ["vvel"],
            query.semantic_search_aliases("Variable valve event and lift"),
        )
        self.assertEqual(
            ["air", "fuel", "ratio"],
            query.semantic_search_tokens("the air-fuel ratio"),
        )
        self.assertIn(
            "air-fuel ratio",
            query.semantic_search_phrases("the air fuel ratio"),
        )
        self.assertNotIn(
            "ect",
            query.semantic_search_aliases("engine coolant temperature"),
        )
        self.assertIn(
            "ect sen",
            query.dtc_search_aliases("engine coolant temperature"),
        )

    def test_monitor_semantic_search_is_ranked_and_exposes_ecu(self) -> None:
        self.assertIn("coalesce(definition.description", query.MONITOR_QUERY)
        self.assertIn("coalesce(definition.conditions", query.MONITOR_QUERY)
        self.assertIn("coalesce(definition.remarks", query.MONITOR_QUERY)
        self.assertIn("$phrases", query.MONITOR_QUERY)
        self.assertIn("$aliases", query.MONITOR_QUERY)
        self.assertIn("definition.ecu_id AS ecu_id", query.MONITOR_QUERY)
        self.assertIn("WHEN 'exact_manual' THEN 0", query.MONITOR_QUERY)
        self.assertIn("AS match_scope", query.MONITOR_QUERY)

    def test_dtc_semantic_search_uses_definition_titles_only(self) -> None:
        self.assertIn("MATCH (definition:DtcDefinition)", query.DTC_SEARCH_QUERY)
        self.assertIn("$phrases", query.DTC_SEARCH_QUERY)
        self.assertIn("$aliases", query.DTC_SEARCH_QUERY)
        self.assertIn("AS match_scope", query.DTC_SEARCH_QUERY)
        self.assertNotIn("fragment.text", query.DTC_SEARCH_QUERY)
        args = query.parser().parse_args(
            ["dtc-search", "intake valve timing", "--limit", "5"]
        )
        self.assertEqual("dtc-search", args.command)
        self.assertEqual(5, args.limit)

    def test_monitor_identifier_normalization_accepts_byte_formats(self) -> None:
        self.assertEqual(
            "221201",
            query.canonical_monitor_identifier("22 12 01"),
        )
        self.assertEqual(
            "221201",
            query.canonical_monitor_identifier("0x22-0x12-0x01"),
        )
        self.assertEqual(
            "221201",
            query.canonical_monitor_identifier("22:12:01"),
        )
        self.assertEqual("1201", query.canonical_monitor_identifier("0X1201"))
        self.assertIsNone(query.canonical_monitor_identifier("ENGINE SPEED"))

    def test_can_query_separates_definitions_from_bindings(self) -> None:
        self.assertIn("MATCH (signal:CanSignal)", query.CAN_QUERY)
        self.assertIn(
            "OPTIONAL MATCH (definition:CanSignalDefinition)-[:DEFINES]->(signal)",
            query.CAN_QUERY,
        )
        self.assertIn("AS definitions", query.CAN_QUERY)
        self.assertIn("AS bindings", query.CAN_QUERY)
        self.assertIn("binding_fragment", query.CAN_QUERY)
        self.assertNotIn(
            "coalesce(fragment.document_id, binding_fragment.document_id)",
            query.CAN_QUERY,
        )
        self.assertIn("pack.applicability_status", query.CAN_QUERY)
        self.assertIn("source_tier:pack.source_tier", query.CAN_QUERY)
        self.assertIn("$phrases", query.CAN_QUERY)
        self.assertIn(
            "definition.applicability = 'exact_manual'",
            query.CAN_QUERY,
        )

    def test_can_identifier_normalization_accepts_common_forms(self) -> None:
        self.assertEqual("0x180", query.canonical_can_term("180"))
        self.assertEqual("0x180", query.canonical_can_term("0x180"))
        self.assertEqual("0x1F9", query.canonical_can_term("0X1f9"))
        self.assertEqual("Engine speed", query.canonical_can_term("Engine speed"))
        self.assertEqual(
            "0x180",
            query.canonical_can_identifier("0x180"),
        )
        self.assertIsNone(
            query.canonical_can_identifier("Engine speed")
        )

    def test_can_id_search_filters_unrelated_signal_bindings(self) -> None:
        rows = [
            {
                "signal": "Engine speed",
                "definitions": [],
                "bindings": [
                    {"can_id": "0x180", "byte_offset": 0},
                    {"can_id": "0x1F9", "byte_offset": 2},
                ],
            },
            {
                "signal": "Other signal",
                "definitions": [{"can_id": "0x1F9"}],
                "bindings": [],
            },
        ]
        filtered = query.filter_can_evidence(rows, "0x180")
        self.assertEqual(1, len(filtered))
        self.assertEqual("Engine speed", filtered[0]["signal"])
        self.assertEqual(
            [{"can_id": "0x180", "byte_offset": 0}],
            filtered[0]["bindings"],
        )
        self.assertEqual([], filtered[0]["definitions"])
        self.assertEqual(
            rows,
            query.filter_can_evidence(rows, None),
        )

    def test_can_evidence_is_sorted_by_applicability(self) -> None:
        rows = [
            {
                "signal": "Engine speed",
                "definitions": [
                    {
                        "dataset_id": "community",
                        "applicability": "homologous_community",
                    },
                    {
                        "dataset_id": "manual",
                        "applicability": "exact_manual",
                    },
                ],
                "bindings": [],
            }
        ]
        sorted_rows = query.sort_can_evidence(rows)
        self.assertEqual(
            ["manual", "community"],
            [
                row["dataset_id"]
                for row in sorted_rows[0]["definitions"]
            ],
        )

    def test_dtc_query_exposes_detail_fragments_without_text_by_default(self) -> None:
        rows = query.prepare_dtc_rows(
            [
                {
                    "code": "P0455",
                    "details": [
                        {
                            "heading": "secondary",
                            "primary": False,
                            "pdf_page": 4,
                            "text": "contents",
                        },
                        {
                            "heading": "P0455",
                            "primary": True,
                            "pdf_page": 310,
                            "text": "diagnosis",
                        },
                    ],
                }
            ],
            include_detail_text=False,
        )
        self.assertEqual("P0455", rows[0]["details"][0]["heading"])
        self.assertNotIn("text", rows[0]["details"][0])
        self.assertIn("DESCRIBES_DTC", query.DTC_DETAIL_QUERY)
        self.assertIn("$include_mentions", query.DTC_DETAIL_QUERY)
        self.assertIn("$include_detail_text", query.DTC_DETAIL_QUERY)

    def test_dtc_code_normalization_accepts_case_and_outer_space(self) -> None:
        self.assertEqual("P0605", query.canonical_dtc_code(" p0605 "))
        self.assertIsNone(query.canonical_dtc_code("P06"))

    def test_operation_kind_and_limit_input_are_normalized(self) -> None:
        self.assertEqual(
            "active_test",
            query.canonical_operation_kind("Active Test"),
        )
        self.assertEqual(
            "work_support",
            query.canonical_operation_kind("work-support"),
        )
        self.assertEqual(0, query.nonnegative_int("0"))
        with self.assertRaises(argparse.ArgumentTypeError):
            query.nonnegative_int("-1")
        self.assertIn("coalesce(operation.description", query.OPERATION_QUERY)
        self.assertIn("coalesce(operation.conditions", query.OPERATION_QUERY)
        self.assertIn("coalesce(operation.usage", query.OPERATION_QUERY)
        self.assertIn("WHEN 'exact_manual' THEN 0", query.OPERATION_QUERY)

    def test_database_connection_error_is_reported_without_traceback(self) -> None:
        class DriverError(Exception):
            pass

        class Neo4jError(Exception):
            pass

        class OfflineSession:
            def __enter__(self) -> "OfflineSession":
                return self

            def __exit__(self, *args: object) -> None:
                return None

            def run(self, *args: object, **kwargs: object) -> list[dict]:
                raise DriverError("database offline")

        class OfflineDriver:
            def session(self, **kwargs: object) -> OfflineSession:
                return OfflineSession()

            def close(self) -> None:
                return None

        neo4j_module = types.ModuleType("neo4j")
        exceptions_module = types.ModuleType("neo4j.exceptions")
        exceptions_module.DriverError = DriverError
        exceptions_module.Neo4jError = Neo4jError
        error_output = io.StringIO()
        with (
            patch.dict(
                sys.modules,
                {
                    "neo4j": neo4j_module,
                    "neo4j.exceptions": exceptions_module,
                },
            ),
            patch.object(sys, "argv", ["query.py", "coverage"]),
            patch.object(query.reader, "session", return_value=OfflineSession()),
            redirect_stderr(error_output),
        ):
            self.assertEqual(1, query.main())
        self.assertEqual("database offline", error_output.getvalue().strip())
        self.assertNotIn("Traceback", error_output.getvalue())

    def test_human_output_preserves_sections_and_nested_evidence(self) -> None:
        rows = [
            {"section": "ROM coverage", "rom": "JK08A", "unique_codes": 227},
            {
                "section": "Source coverage",
                "dataset_id": "manual",
                "kind": "factory_manual",
            },
        ]
        output = io.StringIO()
        with redirect_stdout(output):
            query.print_table(rows)
        rendered = output.getvalue()
        self.assertIn("ROM coverage", rendered)
        self.assertIn("Source coverage", rendered)
        self.assertIn("factory_manual", rendered)

        long_value = "complete semantic evidence " * 8
        output = io.StringIO()
        with redirect_stdout(output):
            query.print_table(
                [{"code": "P0455", "details": [{"text": long_value}]}]
            )
        self.assertIn(
            " ".join(long_value.split()),
            " ".join(output.getvalue().split()),
        )
        self.assertNotIn("...", output.getvalue())

    def test_equivalent_affine_formulas_are_not_conflicts(self) -> None:
        equivalent = [
            {
                "request_hex": "221101",
                "definitions": [
                    {
                        "dataset_id": "logger",
                        "formula": "°C = A-50, °F = (A - 50)*9/5+32",
                        "factor": None,
                        "addend": None,
                        "unit": "",
                    },
                    {
                        "dataset_id": "profile",
                        "formula": "raw * 1 / 1 + -50.0",
                        "factor": 1.0,
                        "addend": -50.0,
                        "unit": "deg",
                    },
                ],
            }
        ]
        self.assertEqual([], query.conflicting_interpretations(equivalent, 100))

    def test_different_rpm_factors_remain_a_conflict(self) -> None:
        conflict = [
            {
                "request_hex": "221201",
                "definitions": [
                    {
                        "dataset_id": "logger",
                        "formula": "RPM = (A*256+B)*10",
                        "factor": None,
                        "addend": None,
                        "unit": "",
                    },
                    {
                        "dataset_id": "profile",
                        "formula": "raw * 125 / 10",
                        "factor": 12.5,
                        "addend": 0,
                        "unit": "rpm",
                    },
                ],
            }
        ]
        rows = query.conflicting_interpretations(conflict, 100)
        self.assertEqual(["221201"], [row["request_hex"] for row in rows])

    def test_pinned_git_tree_rejects_modified_source_files(self) -> None:
        clean_head = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="abc123\n", stderr=""
        )
        dirty_diff = subprocess.CompletedProcess(
            args=[], returncode=1, stdout="", stderr=""
        )
        with patch.object(
            catalog.subprocess, "run", side_effect=[clean_head, dirty_diff]
        ):
            with self.assertRaisesRegex(
                catalog.CatalogError, "pinned source files differ"
            ):
                catalog.require_pinned_git_tree(
                    Path("/source"), "abc123", ("input.csv",)
                )


if __name__ == "__main__":
    unittest.main()
