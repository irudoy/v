import itertools
import sys
import types
import unittest
from pathlib import Path

neo4j = types.ModuleType("neo4j")
neo4j.GraphDatabase = object
sys.modules.setdefault("neo4j", neo4j)

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "sweep"))

import build_artifacts  # noqa: E402


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


class SiteListingTest(unittest.TestCase):
    def test_manual_map_without_callsite_is_not_missing_export(self):
        lines = []

        build_artifacts.render_site_listing(
            lines.append,
            "/unused",
            {"callsite": "", "tbl": "0000a8ea"},
        )

        text = "\n".join(lines)
        self.assertIn("Сайт вызова отсутствует", text)
        self.assertNotIn("Нет файла", text)
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
