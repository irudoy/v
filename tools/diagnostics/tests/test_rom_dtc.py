from __future__ import annotations

import csv
import sys
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tools" / "diagnostics"))

import extract_rom_dtc  # noqa: E402


class RomDtcCatalogTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = extract_rom_dtc.build()

    def test_descriptor_and_unique_counts(self) -> None:
        expected = {
            "JK00D": (295, 225),
            "JK03A": (297, 227),
            "JK08A": (297, 227),
        }
        for rom, (descriptors, unique_codes) in expected.items():
            rows = [row for row in self.rows if row["rom"] == rom]
            self.assertEqual(descriptors, len(rows))
            self.assertEqual(unique_codes, len({row["code"] for row in rows}))

    def test_jk03a_and_jk08a_tables_are_identical(self) -> None:
        def projection(rom: str) -> list[tuple[object, ...]]:
            return [
                (
                    row["index"],
                    row["record_hex"],
                    row["code"],
                    row["attribute_addr"],
                    row["attribute_hex"],
                )
                for row in self.rows
                if row["rom"] == rom
            ]

        self.assertEqual(projection("JK03A"), projection("JK08A"))

    def test_duplicate_public_code_descriptors_are_preserved(self) -> None:
        for rom in ("JK00D", "JK03A", "JK08A"):
            counts = Counter(
                row["code"] for row in self.rows if row["rom"] == rom
            )
            self.assertEqual(32, counts["P0605"])

    def test_curated_jk08a_rows_join_exactly(self) -> None:
        by_index = {
            int(row["index"]): row
            for row in self.rows
            if row["rom"] == "JK08A"
        }
        path = ROOT / "defs" / "JK08A.dtc.csv"
        with path.open(newline="", encoding="utf-8") as source:
            curated = list(csv.DictReader(source))
        self.assertEqual(48, len(curated))
        for row in curated:
            descriptor = by_index[int(row["index"])]
            self.assertEqual(row["dtc"], descriptor["code"])
            self.assertEqual(row["record_addr"], descriptor["record_addr"])
            self.assertEqual(row["attribute_addr"], descriptor["attribute_addr"])
            self.assertEqual(row["stock_attribute"], descriptor["attribute_hex"])


if __name__ == "__main__":
    unittest.main()
