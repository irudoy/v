import argparse
import hashlib
import io
import itertools
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

neo4j = types.ModuleType("neo4j")
neo4j.GraphDatabase = object
sys.modules.setdefault("neo4j", neo4j)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sweep"))

import build_artifacts  # noqa: E402


class FakeRecord(dict):
    def data(self):
        return dict(self)


class FakeResult:
    def __init__(self, rows):
        self.rows = [row if isinstance(row, FakeRecord) else FakeRecord(row) for row in rows]

    def __iter__(self):
        return iter(self.rows)

    def single(self):
        return self.rows[0]


class AxisContextSession:
    def __init__(self, rows):
        self.rows = rows
        self.parameters = None

    def run(self, query, **parameters):
        if query != build_artifacts.AXIS_CONTEXTS:
            raise AssertionError(f"unexpected query: {query}")
        self.parameters = parameters
        return FakeResult(self.rows)


class ArtifactImage:
    data = b""

    def table(self, addr, _width, _height, _storagetype):
        return [[int(addr, 16)]]


class AxisBuildSession:
    def __init__(self, reverse=False):
        map_rows = [
            {
                "addr": "00001010", "family": "explicit", "dims": 1,
                "width": 2, "height": 0, "storagetype": "uint8",
                "vmin": 3, "vmax": 4, "values_hash": "map-b",
                "via": ["00003020", "00003010"],
                "kernel": ["00004020", "00004010"],
                "axis_x": ["00002000"], "axis_y": [],
            },
            {
                "addr": "00001000", "family": "explicit", "dims": 2,
                "width": 2, "height": 2, "storagetype": "uint8",
                "vmin": 1, "vmax": 2, "values_hash": "map-a",
                "via": ["00003010"], "kernel": ["00004010"],
                "axis_x": ["00002000"], "axis_y": ["00002010"],
            },
        ]
        axis_rows = [
            {
                "addr": "00002010", "len": 2, "storagetype": "uint8",
                "values": [1, 2], "monotonic": True,
            },
            {
                "addr": "00002000", "len": 2, "storagetype": "uint16",
                "values": [10, 20], "monotonic": True,
            },
        ]
        site_rows = [
            {
                "accessor": "00005010", "name": "second", "size": 20,
                "tbl": "00001010", "callsite": "00005014", "r4": "00001010",
                "r5": "00002000", "r6": "", "kind": "pool", "kind5": "pool",
                "kind6": "", "verdict": "df_only",
            },
            {
                "accessor": "00005000", "name": "first", "size": 18,
                "tbl": "00001000", "callsite": "00005004", "r4": "00001000",
                "r5": "00002000", "r6": "00002010", "kind": "pool",
                "kind5": "pool", "kind6": "pool", "verdict": "df_only",
            },
        ]
        if reverse:
            map_rows.reverse()
            axis_rows.reverse()
            site_rows.reverse()
            for row in map_rows:
                for field in ("via", "kernel", "axis_x", "axis_y"):
                    row[field] = list(reversed(row[field]))
        self.rows = {
            build_artifacts.MAP_FACTS: map_rows,
            build_artifacts.AXIS_FACTS: axis_rows,
            build_artifacts.SITES: site_rows,
            build_artifacts.KERNELS: [],
            build_artifacts.CALLERS: [],
            build_artifacts.USES: [],
            build_artifacts.WRITE_REGS: [],
            build_artifacts.FUNC_REGS: [],
            build_artifacts.CONSUMERS: [],
            build_artifacts.CALLED: [],
            build_artifacts.CONTRACTS: [],
            build_artifacts.MAP_ANSWERS: [
                {
                    "addr": addr, "semantics": "", "note": "", "role": "",
                    "units": "", "scale_expr": "", "to_byte": "",
                    "confidence": "", "evidence": "", "scale_evidence": "",
                }
                for addr in ("00001010", "00001000")
            ],
            build_artifacts.AXIS_ANSWERS: [
                {
                    "addr": addr, "kind": "", "units": "", "scale_expr": "",
                    "to_byte": "", "note": "", "confidence": "",
                    "scale_evidence": "",
                }
                for addr in ("00002010", "00002000")
            ],
            build_artifacts.FUNC_ANSWERS: [],
        }
        self.calls = []

    def run(self, query, **parameters):
        self.calls.append((query, parameters))
        if query == build_artifacts.ALL_REGS:
            return FakeResult([{"addrs": []}])
        if query == build_artifacts.CONSUMERS_OF:
            return FakeResult([])
        if query not in self.rows:
            raise AssertionError(f"unexpected query: {query}")
        return FakeResult(self.rows[query])

    def parameters_for(self, query):
        return [parameters for called, parameters in self.calls if called == query]


class StableArtifactOrderTest(unittest.TestCase):
    def test_kinds_by_addr_preserves_all_kinds(self):
        rows = [
            {"addr": "ffff1000", "kind": "R"},
            {"addr": "ffff1000", "kind": "W"},
            {"addr": "ffff1000", "kind": "R"},
            {"addr": "ffff1002", "kind": "L"},
            {"addr": "ffff1002", "kind": "D"},
        ]
        expected = {0xFFFF1000: "RW", 0xFFFF1002: "DL"}
        for permutation in itertools.permutations(rows):
            self.assertEqual(build_artifacts.kinds_by_addr(permutation), expected)

    def test_addresses_are_unique_and_sorted(self):
        self.assertEqual(
            build_artifacts.stable_addrs(["00000020", "00000010", "00000020"]),
            ["00000010", "00000020"],
        )

    def test_sites_use_complete_key(self):
        rows = [
            {"accessor": "00000020", "callsite": "00000030", "tbl": "00000050"},
            {"accessor": "00000010", "callsite": "00000040", "tbl": "00000060"},
            {"accessor": "00000010", "callsite": "00000030", "tbl": "00000070"},
            {"accessor": "00000010", "callsite": "00000030", "tbl": "00000050"},
        ]
        expected = [rows[3], rows[2], rows[1], rows[0]]
        for permutation in itertools.permutations(rows):
            self.assertEqual(build_artifacts.stable_sites(permutation), expected)

    def test_callees_are_sorted(self):
        rows = [
            {"addr": "00026984", "size": 60},
            {"addr": "00026740", "size": 46},
            {"addr": None, "size": None},
        ]
        expected = [rows[2], rows[1], rows[0]]
        for permutation in itertools.permutations(rows):
            self.assertEqual(build_artifacts.stable_callees(permutation), expected)


class AxisFocusTest(unittest.TestCase):
    def test_jobs_aggregate_every_related_map_and_accessor_stably(self):
        rows = [
            {"axis": "00011ece", "map": "00009b1a", "accessor": "000493e8"},
            {"axis": "00011ece", "map": "00009a1a", "accessor": "0004e1c0"},
            {"axis": "00011ece", "map": "0000991a", "accessor": "0004e1c0"},
            {"axis": "00011ece", "map": "00009a1a", "accessor": "000493e8"},
            {"axis": "00011ece", "map": "00009a1a", "accessor": "000493e8"},
        ]
        expected_context = {
            "key": "00011ece",
            "maps": ["0000991a", "00009a1a", "00009b1a"],
            "accessors": ["000493e8", "0004e1c0"],
        }

        for permutation in itertools.permutations(rows):
            session = AxisContextSession(permutation)
            jobs = build_artifacts.axis_focus_jobs(session, "JK03A", ["00011ece"])
            self.assertEqual(
                jobs,
                [(expected_context, None, "00011ece", "axis-00011ece.md")],
            )
            self.assertEqual(
                session.parameters,
                {"rom": "JK03A", "addrs": ["00011ece"]},
            )

    def test_focus_file_is_normalized_deduplicated_and_sorted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "axes.txt"
            path.write_text("00002000\n00001000\n00002000\n", encoding="utf-8")

            self.assertEqual(
                build_artifacts.focus_addrs(["00003000", "00001000"], path),
                ["00001000", "00002000", "00003000"],
            )

    def test_axis_build_is_complete_and_deterministic(self):
        comp = {
            "key": "00002000",
            "maps": ["00001010", "00001000"],
            "accessors": ["00005010", "00005000"],
        }
        catalog = {"a2l": {}, "vendor": [], "consts": []}
        outputs = []
        sessions = [AxisBuildSession(), AxisBuildSession(reverse=True)]

        for session in sessions:
            text, leaks = build_artifacts.build(
                session,
                ArtifactImage(),
                "JK03A",
                comp,
                "/path/that/does/not/exist",
                catalog,
                8,
                focus_axis="00002000",
            )
            self.assertEqual(leaks, [])
            outputs.append(text)
            self.assertEqual(
                session.parameters_for(build_artifacts.MAP_FACTS)[0]["addrs"],
                ["00001000", "00001010"],
            )
            self.assertEqual(
                session.parameters_for(build_artifacts.KERNELS)[0]["maps"],
                ["00001000", "00001010"],
            )
            self.assertEqual(
                session.parameters_for(build_artifacts.SITES)[0]["addrs"],
                ["00005000", "00005010"],
            )

        self.assertEqual(outputs[0], outputs[1])
        text = outputs[0]
        self.assertIn("# Axis `00002000` (JK03A)", text)
        self.assertIn("`00002000` - TARGET", text)
        self.assertLess(text.index("### Map `00001000`"),
                        text.index("### Map `00001010`"))
        for addr in comp["maps"] + comp["accessors"]:
            self.assertIn(f"`{addr}`", text)


class BudgetValidationTest(unittest.TestCase):
    def test_budgets_reject_negative_values_at_cli_boundary(self):
        self.assertEqual(build_artifacts.nonnegative_int("0"), 0)
        self.assertEqual(build_artifacts.nonnegative_int("24"), 24)
        with self.assertRaises(argparse.ArgumentTypeError):
            build_artifacts.nonnegative_int("-1")

        for flag in ("--max-readers", "--max-consumer-decomp"):
            argv = ["build_artifacts.py", "/tmp/unused", flag, "-1"]
            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(sys, "stderr", io.StringIO()),
                self.assertRaises(SystemExit) as raised,
            ):
                build_artifacts.main()
            self.assertEqual(raised.exception.code, 2)


class BlindAuditOutputTest(unittest.TestCase):
    def test_main_writes_verified_focus_map_audit(self):
        comp = {
            "key": "00005000",
            "maps": ["00001000"],
            "accessors": ["00005000"],
        }
        session = mock.MagicMock()
        driver = mock.MagicMock()
        driver.session.return_value.__enter__.return_value = session
        graph_database = types.SimpleNamespace(
            driver=mock.Mock(return_value=driver),
        )

        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "artifacts"
            audit_path = Path(tmp) / "blind-audit.json"
            argv = [
                "build_artifacts.py",
                str(out_dir),
                "--rom", "JK03A",
                "--focus-map", "00001000",
                "--export-dir", str(Path(tmp) / "exports"),
                "--audit-output", str(audit_path),
            ]
            with (
                mock.patch.object(sys, "argv", argv),
                mock.patch.object(build_artifacts, "GraphDatabase", graph_database),
                mock.patch.object(build_artifacts.romkit, "load", return_value=ArtifactImage()),
                mock.patch.object(build_artifacts, "components", return_value=[comp]),
                mock.patch.object(
                    build_artifacts,
                    "load_catalog",
                    return_value={"a2l": {}, "vendor": [], "consts": []},
                ),
                mock.patch.object(build_artifacts, "build", return_value=("blind\n", [])),
            ):
                build_artifacts.main()

            artifact_path = out_dir / "map-00001000.md"
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            self.assertEqual(audit["schema"], "vq.blind-artifact-audit/v1")
            self.assertEqual(audit["mode"], "focus-maps")
            self.assertEqual(audit["targets"], ["00001000"])
            self.assertEqual(len(audit["artifacts"]), 1)
            record = audit["artifacts"][0]
            self.assertEqual(record["path"], str(artifact_path.resolve()))
            self.assertEqual(
                record["sha256"],
                hashlib.sha256(artifact_path.read_bytes()).hexdigest(),
            )
            self.assertTrue(record["blind_verified"])
            driver.close.assert_called_once_with()


class BlindLeakageTest(unittest.TestCase):
    def test_map_and_axis_to_byte_are_hidden_answers_and_audited(self):
        self.assertIn("m.to_byte AS to_byte", build_artifacts.MAP_ANSWERS)
        self.assertIn("a.to_byte AS to_byte", build_artifacts.AXIS_ANSWERS)
        self.assertIn("to_byte", build_artifacts.ANSWER_TEXT)
        answers = [
            {"addr": "00001000", "to_byte": "x/2"},
            {"addr": "00002000", "to_byte": "x"},
        ]
        text = "short answers: `x/2` and standalone `x`"

        self.assertEqual(
            build_artifacts.verify_blind(text, answers, set()),
            [
                "00001000.to_byte = 'x/2'",
                "00002000.to_byte = 'x'",
            ],
        )
        self.assertFalse(
            build_artifacts.answer_occurs("scale_expr and x/20", "x/2", "to_byte")
        )
        self.assertFalse(
            build_artifacts.answer_occurs("scale_expr and x/20", "x", "to_byte")
        )


class SiteListingTest(unittest.TestCase):
    def test_manual_map_without_callsite_is_not_missing_export(self):
        lines = []

        build_artifacts.render_site_listing(
            lines.append,
            "/unused",
            {"callsite": "", "tbl": "0000a8ea"},
        )

        text = "\n".join(lines)
        self.assertIn("No call site exists", text)
        self.assertNotIn("is missing", text)
        self.assertNotIn("listing_.txt", text)


class OutputAttributionTest(unittest.TestCase):
    def test_comparison_does_not_clear_pool_alias(self):
        syms = {
            "DAT_00000100": (0x100, {"mov.l": 0xFFFF1FF4}),
            "DAT_00000104": (0x104, {"mov.l": 0xFFFF22DC}),
        }
        snapshots = build_artifacts.alias_snapshots(
            [
                "iVar7 = DAT_00000100",
                "if (iVar7 == DAT_00000104)",
                "uVar13 = 0",
            ],
            syms,
        )
        self.assertEqual(snapshots[1]["iVar7"], "DAT_00000100")
        self.assertEqual(snapshots[2]["iVar7"], "DAT_00000100")

    def test_reused_local_base_is_resolved_at_store_position(self):
        data = bytearray(0x200)
        data[0x100:0x104] = (0xFFFF1FF4).to_bytes(4, "big")
        data[0x104:0x108] = (0xFFFF22DC).to_bytes(4, "big")
        data[0x108:0x10A] = (0x0224).to_bytes(2, "big")
        data[0x10C:0x110] = (0x000125B2).to_bytes(4, "big")
        data[0x110:0x114] = (0x00012FE6).to_bytes(4, "big")
        image = types.SimpleNamespace(data=bytes(data))
        text = """
void FUN_00041750(void)
{
  int iVar7;
  uint uVar13;
  iVar7 = DAT_00000100;
  uVar13 = FUN_00026474(DAT_0000010c,DAT_00000110,0);
  *(undefined1 *)(iVar7 + DAT_00000108) = uVar13;
  iVar7 = DAT_00000104;
  *(undefined1 *)(iVar7 + DAT_00000108) = 0;
}
"""
        regs = [{"addr": "ffff2218", "kind": "W"}]

        attributed = build_artifacts.attribute(image, text, regs, {"000125b2"})

        self.assertEqual(len(attributed), 1)
        self.assertEqual(attributed[0]["sink"], "ffff2218")
        self.assertEqual(attributed[0]["kind"], "reg")
        _syms, binds, _raw, _base, _aliases, _stmts = build_artifacts.pool(
            image, text, regs
        )
        self.assertEqual(
            binds[("DAT_00000100", "DAT_00000108")][0], 0xFFFF2218
        )
        self.assertEqual(
            binds[("DAT_00000104", "DAT_00000108")][0], 0xFFFF2500
        )


if __name__ == "__main__":
    unittest.main()
