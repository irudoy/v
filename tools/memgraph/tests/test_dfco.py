import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FINDINGS = ROOT / "defs" / "JK08A.findings.csv"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
CONTRACT = ROOT / "defs" / "JK08A.dfco.md"


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
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def test_stock_restore_classifier_constants(self):
        self.assertEqual(self.rom[0x8B3F], 0x18)
        self.assertEqual(self.rom[0x8B3F] & 0x80, 0)
        self.assertEqual(self.rom[0x870C], 0x44)
        self.assertEqual(self.rom[0x870C] & 0x80, 0)
        self.assertEqual(self.rom[0x85FA], 4)
        self.assertEqual(self.rom[0x8A3A], 42)
        self.assertEqual(self.rom[0x8A3F], 48)

    def test_moving_classifier_uses_only_lower_restore_map(self):
        classifier = self.funcs["00050018"]
        lower = self.findings["00012818"]
        upper = self.findings["0001298c"]

        self.assertIn("every branch reachable", classifier["note"])
        self.assertIn("ignores the upper threshold", classifier["note"])
        self.assertIn("isolates 00012818", classifier["note"])
        self.assertIn("class 0 begins only above it", lower["note"])
        self.assertIn("speed-count-4-or-above", upper["note"])
        self.assertIn("ignores it", upper["note"])
        self.assertIn("strictly above", self.vars["ffff16aa"]["note"])
        self.assertIn("stock compile-time flags ignores", self.vars["ffff1778"]["note"])

    def test_documented_boundaries_match_structured_claims(self):
        self.assertIn("RPM <= lower threshold", self.contract)
        self.assertIn("lower threshold < RPM <= upper threshold", self.contract)
        self.assertIn("class 0 only when RPM is strictly above it", self.contract)
        self.assertIn("changing only `0x12818` is sufficient", self.contract)
        self.assertIn("raw threshold of 200 vetoes DFCO through", self.contract)


if __name__ == "__main__":
    unittest.main()
