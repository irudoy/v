import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
FINDINGS = ROOT / "defs" / "JK08A.findings.csv"
CONTRACT = ROOT / "defs" / "JK08A.throttle-control.md"
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
        cls.contract = CONTRACT.read_text(encoding="utf-8")
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

    def test_rotational_speed_limiter_calibrations_are_reviewed_sources(self):
        required = {
            "00009424": ("blend", "1024"),
            "00009426": ("normal", "128"),
            "00009428": ("fast", "q7"),
            "0000942a": ("final", "128"),
            "0000942c": ("base threshold", "0xffff"),
            "0000942e": ("cap", "ffff4188"),
            "00009430": ("decrement", "ffff84c3"),
            "00009434": ("alternate", "ffff249e"),
            "00009436": ("increment", "ffff84c3"),
            "0000943a": ("recovery", "ffff19dc"),
            "0000943c": ("recovery", "ffff19dc"),
            "0000943e": ("duration", "ffff413c"),
            "000094b2": ("lower floor", "ffff4162"),
            "00014384": ("auxiliary", "ffff2400"),
        }
        for address, tokens in required.items():
            row = self.findings[address]
            text = (row["semantics"] + row["note"]).lower()
            for token in tokens:
                with self.subTest(address=address, token=token):
                    self.assertIn(token, text)

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

        function_tokens = {
            "00077352": ("00077892", "00077dec", "000777fa"),
            "000777fa": ("ffff4162", "ffff3480", "ffff3484"),
            "00077892": ("ffff418f", "ffff41a6", "ffff4413"),
            "00079030": ("ffff3480", "ffff3484", "ffff19c6"),
            "000c3b14": ("0x174", "0x177", "shifted left by five"),
            "000c47ea": ("target gear", "current gear", "ffff1087"),
            "000c4ace": ("gear-phase", "ffff1066", "0x177"),
            "000c5cb2": ("ffff1086", "ffff1087", "invalid"),
        }
        for address, tokens in function_tokens.items():
            text = (
                self.funcs[address]["semantics"]
                + self.funcs[address]["note"]
            ).lower()
            for token in tokens:
                with self.subTest(address=address, token=token):
                    self.assertIn(token, text)

    def test_transmission_context_and_secondary_scalar_gate_are_canonical(self):
        required_variables = {
            "ffff1064": ("0x177", "gear-phase", "30"),
            "ffff1066": ("byte 2", "0x07", "gear-phase"),
            "ffff1082": ("current gear", "low nibble"),
            "ffff1083": ("target gear", "high nibble"),
            "ffff1086": ("current gear", "0x174"),
            "ffff1087": ("target gear", "0x174"),
            "ffff25b0": ("no countdown", "100"),
            "ffff32ec": ("0x942c", "ffff4162"),
            "ffff3480": ("ffff4162", "ffff19c6"),
            "ffff3484": ("ffff4162", "ffff19c6"),
            "ffff4162": ("ffff41a6", "307.2 ms", "4-3 and 3-2 downshifts"),
            "ffff418f": ("ffff419b", "byte 4", "0x174"),
            "ffff41a6": ("ffff4252", "ffff4413", "bit 3"),
            "ffff4252": ("current gear", "target gear", "4-3 and 3-2 downshifts"),
            "ffff4253": ("bit 6", "inhibit"),
            "ffff4413": ("0x1e", "0002040c", "307.2 ms"),
        }
        for address, tokens in required_variables.items():
            text = (
                self.vars[address]["semantics"] + self.vars[address]["note"]
            ).lower()
            for token in tokens:
                with self.subTest(address=address, token=token):
                    self.assertIn(token, text)

        normalized_contract = " ".join(self.contract.lower().split())
        for token in (
            "0x44 -> 0x34 -> 0x33",
            "0x22 -> 0x32 -> 0x33",
            "secondary candidate constrains `ffff19c6` only during such an episode and its hold",
            "calibration-only `0x942c` a/b test is isolated from this secondary path only outside such episodes",
        ):
            with self.subTest(contract_token=token):
                self.assertIn(token, normalized_contract)

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
            row["scale_evidence"].split(";"),
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

        limiters = " ".join(
            (ROOT / "defs" / "JK08A.limiters.md").read_text(encoding="utf-8").split()
        )
        for slot in (1, 4):
            before = "/".join(map(str, dict.fromkeys(result[f"map_{slot}_tps_before"])))
            minimum = "/".join(map(str, result[f"map_{slot}_tps_min"]))
            low, high = result[f"map_{slot}_hold_stock_can_rpm"]
            with self.subTest(published_slot=slot):
                self.assertIn(f"{before} to {minimum} counts", row["note"])
                self.assertIn(f"{before} -> {minimum}", limiters)
                self.assertIn(f"{low}..{high} RPM", row["note"])
                self.assertIn(f"{low}..{high} RPM", limiters)

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

        coordinator = self.funcs["000730fc"]
        text = coordinator["semantics"] + coordinator["note"]
        for token in ("ffff1984", "ffff198a", "ffff183e", "0x870c"):
            with self.subTest(token=token):
                self.assertIn(token, text)

        self.assertIn("not the stock-active actuator coordinate", self.vars["ffff1984"]["note"])
        self.assertIn("stock-active", self.vars["ffff198a"]["semantics"].lower())
        self.assertIn("stock-active request is the shared", self.contract)

    def test_request_to_channel_target_path_is_recorded(self):
        required = {
            "00075590": ("ffff266e", "ffff1e6c"),
            "00075540": ("ffff19d2", "ffff243c"),
            "0007584e": ("ffff243c", "ffff19d8"),
            "000730fc": ("ffff198a", "ffff183e"),
            "00072c3c": ("ffff1340", "ffff19b2"),
            "0006f48c": ("ffff19b2", "ffff28bc"),
            "000cb1ca": ("ffff28bc", "ffff387a"),
            "000cb614": ("ffff37b8", "ffff2628"),
            "000cc5f0": ("ffff37b8", "ffff374c"),
            "000407c0": ("fffff510", "fffff516"),
        }
        for address, tokens in required.items():
            text = self.funcs[address]["semantics"] + self.funcs[address]["note"]
            for token in tokens:
                with self.subTest(address=address, token=token):
                    self.assertIn(token, text)

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

        self.assertIn("does not become zero merely because the pedal", self.contract)
        self.assertIn("DFCO entry and hold calibrations decide fuel", self.contract)
        self.assertIn("not a channel target", self.vars["ffff40c6"]["note"])

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
        self.assertIn("not ffff36b8", self.funcs["000cc5f0"]["note"])

    def test_atu2_boundary_preserves_unverified_physical_assignments(self):
        publisher = self.funcs["000407c0"]
        for token in ("BFR6A", "BFR6C", "fffff510", "fffff516"):
            with self.subTest(token=token):
                self.assertIn(token, publisher["semantics"])

        for address, register, pin in (
            ("fffff510", "BFR6A", "145"),
            ("fffff512", "BFR6B", "146"),
            ("fffff514", "BFR6C", "147"),
            ("fffff516", "BFR6D", "149"),
        ):
            row = self.vars[address]
            with self.subTest(address=address):
                self.assertIn(register, row["semantics"])
                self.assertIn(pin, row["note"])
                self.assertIn("unverified", row["note"])

        self.assertIn("channel 0", self.contract)
        self.assertIn("Neither bank assignment", self.contract)

    def test_throttle_rev_limiter_claim_reaches_the_throttle_plates(self):
        finding = self.findings["0000942c"]
        text = finding["semantics"] + finding["note"]
        self.assertIn("ATU-II BFR6A-D", text)
        self.assertIn("closes both throttle sensors", finding["note"])
        self.assertIn("Plate response time", finding["note"])
        self.assertIn("fuel mask ffff22e0", finding["note"])

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

        required_variables = {
            "ffff1794": "newly stored",
            "ffff1796": "dynamic",
            "ffff1798": "blended",
            "ffff19d8": "equality",
            "ffff19da": "fast",
            "ffff19dc": "recovery",
            "ffff2400": "auxiliary",
            "ffff249e": "255",
            "ffff24a3": "nonpositive",
            "ffff25b0": "fast-ramp",
            "ffff413c": "duration",
            "ffff4188": "cap",
            "ffff4252": "forced-neutral",
        }
        for address, token in required_variables.items():
            row = self.vars[address]
            text = (row["semantics"] + row["note"]).lower()
            with self.subTest(address=address, token=token):
                self.assertIn(token, text)

        normalized_contract = " ".join(self.contract.lower().split())
        for token in (
            "exact one-sample split",
            "equality takes the inactive branch",
            "51 state and sweep cases",
            "253522 stock instructions",
            "not a vehicle prediction",
        ):
            with self.subTest(contract_token=token):
                self.assertIn(token, normalized_contract)


if __name__ == "__main__":
    unittest.main()
