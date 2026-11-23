import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "registries" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "registries" / "JK08A.vars.csv"
FINDINGS = ROOT / "defs" / "registries" / "JK08A.findings.csv"
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"


def read_by_addr(path):
    with path.open(newline="", encoding="utf-8") as source:
        return {row["addr"]: row for row in csv.DictReader(source)}


class ThrottleControlContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.funcs = read_by_addr(FUNCS)
        cls.vars = read_by_addr(VARS)
        cls.findings = read_by_addr(FINDINGS)
        with HARDWARE_RESULTS.open("rb") as source:
            cls.hardware_results = tomllib.load(source)

    def u16(self, address):
        return int.from_bytes(self.rom[address:address + 2], "big")

    def u32(self, address):
        return int.from_bytes(self.rom[address:address + 4], "big")

    def test_stock_pedal_and_target_constants(self):
        self.assertEqual(self.u16(0x8FF2), 1500)
        self.assertEqual(self.u16(0x8FF4), 170)
        self.assertEqual(self.u16(0x8FF6), 45)
        self.assertEqual(self.rom[0x89FB] & 0x20, 0x20)
        self.assertEqual(self.u16(0x94E4), 0)
        self.assertEqual(self.u16(0x94E6), 0)
        self.assertEqual(self.u16(0x94E8), 170)

        self.assertEqual(self.u16(0x9574), 15)
        self.assertEqual(self.u16(0x9576), 227)
        self.assertEqual(self.u16(0x9578), 727)
        self.assertEqual(self.rom[0x8CB6], 0x27)

    def test_rotational_speed_limiter_calibration_is_bound_to_stock_rom(self):
        expected_words = {
            0x9424: 76,
            0x9426: 200,
            0x9428: 1500,
            0x942A: 2000,
            0x942C: 9600,
            0x942E: 0xFFFF,
            0x9430: 0,
            0x9432: 16,
            0x9434: 0xFFFF,
            0x9436: 0,
            0x9438: 5,
            0x943A: 30,
            0x943C: 50,
            0x943E: 182,
            0x94B2: 0x0500,
        }
        for address, expected in expected_words.items():
            with self.subTest(address=f"{address:04x}"):
                self.assertEqual(self.u16(address), expected)

        self.assertEqual(self.rom[0x8A99:0x8A9C], bytes((255, 16, 100)))
        self.assertEqual(self.u16(0x8F2C), 0)
        self.assertEqual(
            tuple(self.u16(0x14384 + index * 2) - 0x8000 for index in range(5)),
            (1000, 1300, 1300, 1000, 1000),
        )

    def test_transmission_can_and_variant_selectors_match_stock_rom(self):
        self.assertEqual(self.rom[0x83C1], 0x2C)
        self.assertEqual(self.rom[0x870C], 0x44)
        self.assertEqual(
            self.rom[0x9782:0x9786], bytes.fromhex("01 06 2e e0")
        )
        self.assertEqual(
            self.rom[0x9786:0x978A], bytes.fromhex("01 08 2e 80")
        )
        self.assertEqual(self.u16(0xC3C56), 0x2E80)
        self.assertEqual(self.u16(0xC3C5A), 0x2EE0)

    def test_hardware_registry_records_transmission_payload_evidence(self):
        result = self.hardware_results["can_telemetry"][
            "current_wide54_divisor1"
        ]
        self.assertEqual(result["transmission_target_current_can_id"], 0x174)
        self.assertEqual(result["transmission_target_current_byte_offset"], 3)
        self.assertEqual(result["transmission_gear_phase_can_id"], 0x177)
        self.assertEqual(result["transmission_gear_phase_byte_offset"], 2)
        self.assertEqual(result["transmission_gear_phase_mask"], 0x07)
        examples = " ".join(result["transmission_transition_examples"])
        for token in ("0x44 -> 0x34 -> 0x33", "0x22 -> 0x32 -> 0x33"):
            with self.subTest(token=token):
                self.assertIn(token, examples)

    def test_rev_limiter_scale_rests_on_the_vehicle_comparison(self):
        row = self.findings["0000942c"]
        result = self.hardware_results["throttle_rev_limiter"][
            "vehicle_2026_09_21"
        ]
        self.assertEqual(row["scale_conf"], "silicon")
        self.assertIn(
            "spec:hardware-results:throttle_rev_limiter.vehicle_2026_09_21",
            [token.strip() for token in row["scale_evidence"].split(";")],
        )
        self.assertEqual(result["hardware_status"], "pass")
        self.assertEqual(result["scale_expr"], row["scale_expr"])
        self.assertEqual(result["scalar_address"], 0x942C)
        self.assertEqual(result["map_slot_addresses"]["map_1"], 0x942C)
        self.assertEqual(result["map_1_scalar"], self.u16(0x942C))

        for slot in (1, 4):
            with self.subTest(map_slot=slot):
                converted = result[f"map_{slot}_scalar"] * 0.78125
                self.assertEqual(result[f"map_{slot}_converted_rpm"], converted)
                onset = result[f"map_{slot}_onset_engine_speed_rpm"]
                self.assertLessEqual(abs(onset - converted), 0.01 * converted)
                for before, minimum in zip(
                    result[f"map_{slot}_tps_before"],
                    result[f"map_{slot}_tps_min"],
                    strict=True,
                ):
                    self.assertLess(2 * minimum, before)

        self.assertEqual(result["map_3_scalar"], 0xFFFF)
        self.assertGreaterEqual(
            result["map_3_first_fuel_cut_engine_speed_rpm"],
            self.u16(0x934E) * 12.5,
        )
        self.assertEqual(result["map_3_fuel_cut_mask"], 0x3F)
        self.assertEqual(result["limiter_interval_fuel_inhibit_record_count"], 0)

    def test_direct_app_area_branch_is_stock_disabled(self):
        self.assertEqual(self.rom[0x870C], 0x44)
        self.assertEqual(self.rom[0x870C] & 0x80, 0)

        self.assertIn("stock-active", self.vars["ffff198a"]["semantics"].lower())

    def test_request_to_channel_target_path_is_recorded(self):

        for address in (
            "ffff243c",
            "ffff19c6",
            "ffff198a",
            "ffff183e",
            "ffff1340",
            "ffff19b2",
            "ffff28bc",
            "ffff387a",
            "ffff37b8",
            "ffff374c",
            "fffff510",
            "fffff516",
        ):
            with self.subTest(address=address):
                self.assertIn(address, self.vars)

    def test_lift_off_base_and_monitor_boundaries_are_explicit(self):
        compositor = self.funcs["00072c3c"]["semantics"]
        for token in ("ffff183e", "ffff1340", "ffff120e", "ffff19b2"):
            with self.subTest(token=token):
                self.assertIn(token, compositor)

    def test_regulator_dispatch_order_is_bound_to_stock_rom(self):
        expected = (
            0x000CAFBC,
            0x000CB078,
            0x000CB140,
            0x000CB1CA,
            0x000CB224,
            0x000CB2B6,
            0x000CB354,
            0x000CB41C,
            0x000CB614,
        )
        actual = tuple(self.u32(0xCC7DC + index * 4) for index in range(len(expected)))
        self.assertEqual(actual, expected)

        coordinator = self.funcs["000cc720"]["semantics"]
        for address in expected:
            with self.subTest(address=address):
                self.assertIn(f"{address:08x}", coordinator)

    def test_regulator_and_duty_caps_match_stock_rom(self):
        self.assertEqual(self.u32(0x96BC), 0x000D0000)
        self.assertEqual(self.u16(0x933A), 0x00D2)
        self.assertEqual(self.u16(0xCC71C), 490)
        self.assertIn("unsigned offset 0xe0", self.funcs["000cc5f0"]["semantics"])

    def test_atu2_boundary_preserves_unverified_physical_assignments(self):
        publisher = self.funcs["000407c0"]
        for token in ("BFR6A", "BFR6C", "fffff510", "fffff516"):
            with self.subTest(token=token):
                self.assertIn(token, publisher["semantics"])

        for address, register in (
            ("fffff510", "BFR6A"),
            ("fffff512", "BFR6B"),
            ("fffff514", "BFR6C"),
            ("fffff516", "BFR6D"),
        ):
            row = self.vars[address]
            with self.subTest(address=address):
                self.assertIn(register, row["semantics"])

    def test_rotational_speed_limiter_state_contract_is_complete(self):
        limiter = self.funcs["0007584e"]
        text = "".join(limiter.values())
        for token in (
            "ffff1794",
            "ffff1796",
            "ffff1798",
            "ffff19d8",
            "ffff19da",
            "ffff19dc",
            "ffff2400",
            "ffff413c",
            "ffff2485",
            "ffff249e",
            "ffff24a3",
            "ffff25b0",
            "ffff84c3",
            "ffff4188",
            "ffff4252",
        ):
            with self.subTest(token=token):
                self.assertIn(token, text)



if __name__ == "__main__":
    unittest.main()
