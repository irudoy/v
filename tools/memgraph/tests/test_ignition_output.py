import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
CONTRACT = ROOT / "defs" / "JK08A.ignition-output.md"


def read_by_addr(path):
    with path.open(newline="", encoding="utf-8") as source:
        return {row["addr"]: row for row in csv.DictReader(source)}


class IgnitionOutputContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.funcs = read_by_addr(FUNCS)
        cls.vars = read_by_addr(VARS)
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def test_normal_timing_coordinate_constants(self):
        self.assertEqual(self.rom[0x83D5], 110)
        self.assertEqual(self.rom[0x821E], 50)
        self.assertEqual(self.rom[0x8221] - 256, -7)

    def test_secondary_offset_cannot_wrap_admitted_target(self):
        self.assertEqual(self.rom[0x8B87], 114)
        self.assertEqual(self.rom[0x8B88], 6)
        self.assertEqual(self.rom[0x8649], 0)
        maximum_reset_offset = 120 - 0
        self.assertEqual(117 + maximum_reset_offset, 237)
        self.assertLess(117 + maximum_reset_offset, 256)

    def test_timing_state_selector_stock_constants(self):
        self.assertEqual(self.rom[0x870B], 0x46)
        self.assertEqual(self.rom[0x870B] & 0x01, 0)
        self.assertEqual(self.rom[0x86A2:0x86A5], bytes([0x9E, 0x55, 0x6E]))
        self.assertEqual(
            self.rom[0x12196:0x1219E],
            bytes([0x80, 0x89, 0x89, 0x89, 0x8A, 0x8C, 0x8F, 0x91]),
        )
        self.assertEqual(
            self.rom[0x1219E:0x121A6],
            bytes([0x80, 0x89, 0x8C, 0x90, 0x94, 0x98, 0x9C, 0xA0]),
        )
        self.assertEqual(
            self.rom[0x121A6:0x121AE],
            self.rom[0x12196:0x1219E],
        )

    def test_timing_state_selector_contract_is_complete(self):
        selector = self.funcs["0004afdc"]
        for token in (
            "000121a6",
            "0001219e",
            "000086a2",
            "00012196",
            "ffff2318",
            "ffff2590",
            "ffff22ff",
        ):
            with self.subTest(token=token):
                self.assertIn(token, selector["semantics"] + selector["note"])

        self.assertIn("strictly below 0x4000", self.vars["ffff2318"]["semantics"])
        self.assertIn("85", self.vars["ffff2590"]["semantics"])
        self.assertIn("default/post-transition", self.vars["ffff1511"]["semantics"])
        self.assertIn("warm DFCO-transition", self.vars["ffff1511"]["semantics"])
        self.assertIn("every other case", self.contract)
        self.assertIn("maximum selection window of `870.4 ms`", self.contract)
        self.assertIn("whole-application p-code census found no other writer", self.contract)

    def test_compare_schedulers_record_position_fallback_gate(self):
        for address in ("0002a892", "0002acba"):
            with self.subTest(address=address):
                self.assertIn("ffff24c9", self.funcs[address]["evidence"])
                self.assertIn("bit6", self.funcs[address]["note"])
        self.assertIn("P0335", self.funcs["00099a48"]["semantics"])
        self.assertIn("ffff24cf", self.vars["ffff24c9"]["semantics"])
        self.assertIn("must preserve", self.vars["ffff24c9"]["note"])

    def test_contract_requires_fail_closed_target_validation(self):
        self.assertIn("0xFFFF24C9.bit6 != 0` forces stock pass-through", self.contract)
        self.assertIn("each target is in `110..117`", self.contract)
        self.assertIn("effective command is `max(stock, target)`", self.contract)


if __name__ == "__main__":
    unittest.main()
