import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
BINDINGS = ROOT / "defs" / "JK08A.diagnostic-bindings.csv"
CONTRACT = ROOT / "defs" / "JK08A.start-signal-temperature-selector.md"
HARDWARE = ROOT / "patches" / "hardware-results.toml"


def read_by(path, key):
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key]: row for row in csv.DictReader(source)}


def u32be(data, offset):
    return int.from_bytes(data[offset : offset + 4], "big")


class StartSignalTemperatureSelectorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.funcs = read_by(FUNCS, "addr")
        cls.vars = read_by(VARS, "addr")
        cls.bindings = read_by(BINDINGS, "id")
        cls.contract = CONTRACT.read_text(encoding="utf-8")
        with HARDWARE.open("rb") as source:
            cls.hardware = tomllib.load(source)

    def test_exact_did_response_pointers_and_support_mask(self):
        self.assertEqual(u32be(self.rom, 0x226B8), 0xFFFF1188)
        self.assertEqual(u32be(self.rom, 0x229F0), 0xFFFF3342)
        self.assertEqual(u32be(self.rom, 0x229F4), 0x00011E41)
        self.assertEqual(self.rom[0x11E41], 0x3F)

    def test_exact_selector_comparison_is_strictly_below_raw_100(self):
        self.assertEqual(
            self.rom[0x39682:0x39694],
            bytes.fromhex("6060c8408908d61ae074026ce66432628902"),
        )
        selector = self.funcs["0003967a"]
        self.assertIn("START SIGNAL", selector["semantics"])
        self.assertIn("below 100", selector["semantics"])
        self.assertIn("8.00 V", selector["note"])

    def test_an0_mux_paths_are_bound_to_named_diagnostics(self):
        self.assertEqual(
            int.from_bytes(self.rom[0x2C644:0x2C646], "big"),
            0xE000,
        )
        sampler = self.funcs["000280d8"]
        self.assertIn("code 000", sampler["semantics"])
        self.assertIn("code 001", sampler["semantics"])
        self.assertIn("code 111", sampler["semantics"])
        self.assertIn("battery voltage", self.vars["ffff1d6e"]["note"])
        self.assertIn("DID 0x1103", self.vars["ffff1188"]["semantics"])

    def test_start_signal_bit_chain_is_structured(self):
        producer = self.funcs["00038d44"]
        packer = self.funcs["0002e0d4"]
        self.assertIn("ffff4185.bit6", producer["semantics"])
        self.assertIn("ffff24ae.bit7", producer["semantics"])
        self.assertIn("ffff3342.bit1", packer["note"])
        self.assertIn("computed START SIGNAL", self.vars["ffff4185"]["semantics"])
        self.assertIn("START SIGNAL", self.vars["ffff3342"]["note"])

    def test_diagnostic_bindings_cover_voltage_and_start_signal(self):
        battery = self.bindings["battery-voltage-did-1103"]
        start = self.bindings["start-signal-did-1302-bit1"]
        self.assertEqual(battery["firmware_addr"], "ffff1188")
        self.assertEqual(
            battery["diagnostic_key"],
            "diagnostic-parameter:request:221103",
        )
        self.assertEqual(start["firmware_addr"], "ffff4185")
        self.assertEqual(
            start["diagnostic_key"],
            "diagnostic-parameter:semantic:cid-1302h-bit1-start-signal",
        )
        self.assertIn("rom_const:000229f0=ffff3342", start["evidence"])

    def test_zero_branch_is_a_sentinel_not_a_temperature(self):
        for address in ("ffff107e", "ffff1080"):
            with self.subTest(address=address):
                self.assertEqual(self.vars[address]["units"], "sentinel")
        self.assertIn("must not be rendered as `-50 deg C`", self.contract)
        self.assertIn("post-start or low-voltage-transition qualifier", self.contract)

    def test_target_observations_keep_their_timing_boundary(self):
        telemetry = self.hardware["can_telemetry"]["current_wide54_divisor1"]
        self.assertEqual(telemetry["carscanner_control_module_voltage_v"], 13.92)
        self.assertEqual(telemetry["carscanner_starter_label"], "[NC] Starter")
        self.assertEqual(telemetry["carscanner_starter_value"], 0)
        self.assertIn(
            "not synchronized",
            telemetry["carscanner_selector_evidence_boundary"],
        )


if __name__ == "__main__":
    unittest.main()
