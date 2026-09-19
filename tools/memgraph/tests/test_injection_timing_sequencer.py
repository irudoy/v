import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"
FINDINGS = ROOT / "defs" / "JK08A.findings.csv"
CONTRACT = ROOT / "defs" / "JK08A.fuel.md"


def read_by(path, key):
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key]: row for row in csv.DictReader(source)}


def u32be(data, offset):
    return int.from_bytes(data[offset : offset + 4], "big")


class InjectionTimingSequencerTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.funcs = read_by(FUNCS, "addr")
        cls.vars = read_by(VARS, "addr")
        cls.findings = read_by(FINDINGS, "addr")
        cls.contract = CONTRACT.read_text(encoding="utf-8")

    def test_pulse_angle_constant_gives_four_crank_degrees_per_count(self):
        self.assertEqual(u32be(self.rom, 0x522A8), 0xC49B)
        # shll2 twice: the RPM/12.5 word enters the product times 16.
        self.assertEqual(self.rom[0x521D0:0x521D4], bytes.fromhex("46084608"))
        counts_per_rpm_second = 16 * 0xC49B * 100000 / (12.5 * 2**32)
        self.assertAlmostEqual(6 / counts_per_rpm_second, 4.0, places=3)

    def test_start_delay_is_split_by_the_engine_event_spacing(self):
        # mov #0x78,r0 before the quotient and the remainder helper.
        self.assertEqual(self.rom[0x52244:0x52246], bytes.fromhex("e078"))
        self.assertEqual(self.rom[0x52252:0x52254], bytes.fromhex("e078"))
        self.assertEqual(u32be(self.rom, 0x522B8), 0x00021BBC)
        self.assertEqual(u32be(self.rom, 0x522BC), 0x00021E14)
        # shll r5; shll2 r4; sub r4,r5: delay = 2*E - 4*p.
        self.assertEqual(self.rom[0x52222:0x52228], bytes.fromhex("450044083548"))
        self.assertEqual(self.rom[0x83EA], 30)
        self.assertEqual(self.vars["ffff23f0"]["units"], "engine events")
        self.assertEqual(self.vars["ffff23bf"]["units"], "4 degCA")
        self.assertEqual(self.vars["ffff192e"]["units"], "2 degCA")

    def test_end_of_injection_tables_carry_the_intake_tdc_coordinate(self):
        self.assertEqual(self.rom[0x12302:0x1230A], bytes([133] * 8))
        self.assertEqual(
            self.rom[0x1230A:0x12312], bytes.fromhex("a0a0a0a5aab9c8c8")
        )
        # Reference tooth 7 is 110 degrees before compression TDC of event
        # cylinder c0 and the injected cylinder c0 + 1 fires 120 degrees later.
        self.assertEqual(self.rom[0x83D5], 110)
        offset = 360 - (110 + 120) - 720
        self.assertEqual(offset, -590)
        self.assertEqual(133 * 4 + offset, -58)
        for address in ("00012302", "0001230a"):
            with self.subTest(table=address):
                row = self.findings[address]
                self.assertEqual(row["units"], "deg after intake TDC")
                self.assertEqual(row["scale_expr"], "x*4-590")
                self.assertEqual(row["to_byte"], "(x+590)/4")
                self.assertEqual(row["scale_conf"], "code")
                self.assertIn("consumer:000521a8@structural", row["scale_evidence"])
                self.assertIn("consumer:00054a44@structural", row["scale_evidence"])
                self.assertIn("not measured electrically", row["note"])

    def test_sequencer_is_an_engine_event_task_with_a_default_lead_of_three(self):
        self.assertEqual(u32be(self.rom, 0x21B5C + 4 * 1), 0x00054A44)
        # mov #3,r9 in the delay slot of the default-lead branch.
        self.assertEqual(self.rom[0x54AAA:0x54AAC], bytes.fromhex("e903"))
        # shll2 r5: the start-angle byte is multiplied by four.
        self.assertEqual(self.rom[0x54BD6:0x54BD8], bytes.fromhex("4508"))
        self.assertEqual(self.rom[0x22695:0x2269B], bytes.fromhex("020408102001"))
        self.assertEqual(u32be(self.rom, 0x54C50), 0x0002C13C)
        self.assertEqual(u32be(self.rom, 0x54EA0), 0x0002B64A)
        sequencer = self.funcs["00054a44"]
        self.assertEqual(sequencer["role"], "driver")
        self.assertIn("Sequential-injection sequencer", sequencer["semantics"])
        self.assertIn("rom_const:00021b60=00054a44", sequencer["evidence"])
        self.assertIn("FUN_00054A44", self.contract)
        self.assertIn("## Injection timing", self.contract)

    def test_delayed_start_programmer_uses_the_ten_degree_tooth(self):
        self.assertEqual(u32be(self.rom, 0x2B86C), 0x00028E7C)
        self.assertEqual(u32be(self.rom, 0x2B870), 0x00028DC8)
        # mov #0x78,r6: the P0335 fallback branch counts one 120-degree event.
        self.assertEqual(self.rom[0x2B66A:0x2B66C], bytes.fromhex("e678"))
        programmer = self.funcs["0002b64a"]
        self.assertIn("splits the angle by ten", programmer["semantics"])
        self.assertIn("GR1A", programmer["semantics"])


if __name__ == "__main__":
    unittest.main()
