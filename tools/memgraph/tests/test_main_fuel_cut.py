import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FINDINGS = ROOT / "defs" / "JK08A.findings.csv"
LAYOUT = ROOT / "patches" / "map-switching-layout.toml"
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"


class MainFuelCutVehicleSessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rom = ROM.read_bytes()
        cls.stock_words = [
            int.from_bytes(rom[0x934E + 2 * index:0x934E + 2 * index + 2], "big")
            for index in range(4)
        ]
        with FINDINGS.open(newline="", encoding="utf-8") as source:
            cls.row = {
                row["addr"]: row for row in csv.DictReader(source)
            }["0000934e"]
        with LAYOUT.open("rb") as source:
            cls.family = next(
                family
                for family in tomllib.load(source)["family"]
                if family["key"] == "rev_limit_fuel_cut"
            )
        with HARDWARE_RESULTS.open("rb") as source:
            cls.result = tomllib.load(source)["main_fuel_cut"]["vehicle_2026_09_21"]

    def test_scale_rests_on_the_vehicle_session(self):
        self.assertEqual(self.row["scale_conf"], "silicon")
        self.assertIn(
            "spec:hardware-results:main_fuel_cut.vehicle_2026_09_21",
            [token.strip() for token in self.row["scale_evidence"].split(";")],
        )
        self.assertEqual(self.result["hardware_status"], "pass")
        self.assertEqual(self.result["scale_expr"], self.row["scale_expr"])
        self.assertEqual(self.result["fuel_cut_mask"], 0x3F)

    def test_session_ran_a_slot_copy_of_the_stock_table(self):
        result = self.result
        self.assertEqual(result["table_address"], 0x934E)
        self.assertEqual(self.family["canonical_address"], result["table_address"])
        self.assertEqual(
            self.family["copies"][result["selected_map"] - 2], result["slot_address"]
        )
        self.assertEqual(self.stock_words, [612, 596, 596, 368])
        differing = [
            index
            for index, (slot, stock) in enumerate(
                zip(result["slot_words"], self.stock_words, strict=True)
            )
            if slot != stock
        ]
        self.assertEqual(differing, [2])
        self.assertEqual(result["column"], 0)

    def test_transitions_bound_the_compared_words(self):
        result = self.result
        activation = result["slot_words"][0]
        release = result["slot_words"][2]
        activations = result["activation_transitions_raw"]
        releases = result["release_transitions_raw"]
        self.assertEqual(len(activations), result["activation_count"])
        self.assertEqual(len(releases), result["release_count"])

        for pair in activations:
            with self.subTest(activation=pair):
                self.assertGreaterEqual(max(pair), activation)
        for pair in releases:
            with self.subTest(release=pair):
                self.assertLess(min(pair), release)

        low, high = result["activation_bound_raw"]
        self.assertEqual(high, min(max(pair) for pair in activations))
        self.assertLessEqual(low, activation)
        self.assertLessEqual(activation, high)
        low, high = result["release_bound_raw"]
        self.assertEqual(low, max(min(pair) for pair in releases) + 1)
        self.assertLessEqual(low, release)
        self.assertLessEqual(release, high)

        stock_release = self.stock_words[2]
        self.assertLess(stock_release, low)
        for pair in releases:
            with self.subTest(stock_release=pair):
                self.assertGreaterEqual(min(pair), stock_release)


if __name__ == "__main__":
    unittest.main()
