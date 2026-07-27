import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "defs" / "JK08A.dtc.csv"
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"


class DtcManifestTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        with MANIFEST.open(newline="", encoding="utf-8") as source:
            cls.rows = list(csv.DictReader(source))

    def test_expected_inventory_size_and_unique_indices(self):
        self.assertEqual(len(self.rows), 29)
        indices = [int(row["index"]) for row in self.rows]
        self.assertEqual(len(indices), len(set(indices)))

    def test_record_address_code_pointer_and_stock_attribute(self):
        for row in self.rows:
            with self.subTest(dtc=row["dtc"], index=row["index"]):
                index = int(row["index"])
                record = int(row["record_addr"], 16)
                attribute = int(row["attribute_addr"], 16)
                self.assertEqual(record, 0x19360 + index * 12)
                self.assertEqual(
                    int.from_bytes(self.rom[record + 6 : record + 8], "big"),
                    int(row["dtc"][1:], 16),
                )
                pointer_offset = 0x1A14C + index * 4
                self.assertEqual(
                    int.from_bytes(self.rom[pointer_offset : pointer_offset + 4], "big"),
                    attribute,
                )
                self.assertEqual(
                    self.rom[attribute : attribute + 2].hex(),
                    row["stock_attribute"],
                )
                self.assertEqual(row["disabled_attribute"], "0000")


if __name__ == "__main__":
    unittest.main()
