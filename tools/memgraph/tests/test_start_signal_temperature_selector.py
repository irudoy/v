import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "registries" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "registries" / "JK08A.vars.csv"
BINDINGS = ROOT / "defs" / "registries" / "JK08A.diagnostic-bindings.csv"
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

    def test_an0_mux_paths_are_bound_to_named_diagnostics(self):
        self.assertEqual(
            int.from_bytes(self.rom[0x2C644:0x2C646], "big"),
            0xE000,
        )
        sampler = self.funcs["000280d8"]
        self.assertIn("code 000", sampler["semantics"])
        self.assertIn("code 001", sampler["semantics"])
        self.assertIn("code 111", sampler["semantics"])
        self.assertIn("DID 0x1103", self.vars["ffff1188"]["semantics"])

    def test_start_signal_bit_chain_is_structured(self):
        producer = self.funcs["00038d44"]
        self.assertIn("ffff4185.bit6", producer["semantics"])
        self.assertIn("ffff24ae.bit7", producer["semantics"])
        self.assertIn("computed START SIGNAL", self.vars["ffff4185"]["semantics"])

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

    def test_hold_branch_reads_the_previous_pass_image_of_the_selected_pair(self):
        # Entry 24 of the 69-entry periodic table is the coordinator.
        self.assertEqual(u32be(self.rom, 0x21834 + 4 * 24), 0x000394B8)
        # jsr @r5 with mov #8,r0 in the delay slot: copy 0xFFFF1072..0xFFFF1079.
        self.assertEqual(self.rom[0x20CBA:0x20CBE], bytes.fromhex("450be008"))
        self.assertEqual(u32be(self.rom, 0x20E6C), 0xFFFF107A)
        self.assertEqual(u32be(self.rom, 0x20E70), 0x00022558)
        self.assertEqual(u32be(self.rom, 0x20E74), 0xFFFF1072)
        # mov.b @(0xc,gbr),r0 and mov.b @(0xe,gbr),r0 with GBR = 0xFFFF1072.
        self.assertEqual(u32be(self.rom, 0x396DC), 0xFFFF1072)
        self.assertEqual(self.rom[0x39510:0x39512], bytes.fromhex("c40c"))
        self.assertEqual(self.rom[0x39514:0x39516], bytes.fromhex("c40e"))
        expected_units = {
            "ffff1076": "degC+50",
            "ffff107e": "degC+50",
            "ffff106e": "degC+50",
            "ffff1078": "normalized coolant index",
            "ffff1080": "normalized coolant index",
            "ffff1070": "normalized coolant index",
        }
        for address, units in expected_units.items():
            with self.subTest(address=address):
                self.assertEqual(self.vars[address]["units"], units)
        for address in ("ffff107e", "ffff1080"):
            with self.subTest(image=address):
                self.assertIn("Previous-pass image", self.vars[address]["semantics"])
                self.assertIn("writes:000209d8@structural", self.vars[address]["evidence"])
        self.assertIn("00020cba", self.funcs["000209d8"]["semantics"])

    def test_readiness_latches_match_factory_driving_pattern_a(self):
        # mov #0x20,r2: RPM/12.5 of 400 rpm; mov #0x14,r2: rise of 20 counts;
        # mov #0x78,r6: raw coolant of 70 deg C.
        self.assertEqual(self.rom[0x804E8:0x804EA], bytes.fromhex("e220"))
        self.assertEqual(self.rom[0x8055A:0x8055C], bytes.fromhex("e214"))
        self.assertEqual(self.rom[0x80576:0x80578], bytes.fromhex("e678"))
        updater = self.funcs["000804ce"]
        self.assertIn("start-latched raw coolant ffff106e", updater["semantics"])
        self.assertIn("spec:esm-2013-g-ec150-driving-pattern-a", updater["evidence"])

    def test_coolant_fail_safe_ramp_spans_raw_90_to_130(self):
        # add #0x5a,r6 and mov #-0x7e,r5: min(90 + counter, 130).
        self.assertEqual(self.rom[0x395FA:0x395FC], bytes.fromhex("e582"))
        self.assertEqual(self.rom[0x395FE:0x39600], bytes.fromhex("765a"))
        # mov #6,r2: countdown reload.
        self.assertEqual(self.rom[0x395EC:0x395EE], bytes.fromhex("e206"))
        ramp = self.funcs["000395ae"]
        self.assertIn("min(90 + counter, 130)", ramp["semantics"])

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
