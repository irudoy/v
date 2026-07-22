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


if __name__ == "__main__":
    unittest.main()
