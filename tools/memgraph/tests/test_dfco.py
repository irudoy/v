import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FINDINGS = ROOT / "defs" / "registries" / "JK08A.findings.csv"
FUNCS = ROOT / "defs" / "registries" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "registries" / "JK08A.vars.csv"


def read_by_addr(path):
    with path.open(newline="", encoding="utf-8") as source:
        return {row["addr"]: row for row in csv.DictReader(source)}


class DfcoContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.findings = read_by_addr(FINDINGS)
        cls.funcs = read_by_addr(FUNCS)
        cls.vars = read_by_addr(VARS)

    def test_stock_restore_classifier_constants(self):
        self.assertEqual(self.rom[0x8B3F], 0x18)
        self.assertEqual(self.rom[0x8B3F] & 0x80, 0)
        self.assertEqual(self.rom[0x870C], 0x44)
        self.assertEqual(self.rom[0x870C] & 0x80, 0)
        self.assertEqual(self.rom[0x85FA], 4)
        self.assertEqual(self.rom[0x8A3A], 42)
        self.assertEqual(self.rom[0x8A3F], 48)


if __name__ == "__main__":
    unittest.main()
