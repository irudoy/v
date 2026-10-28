import csv
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
FUNCS = ROOT / "defs" / "JK08A.funcs.csv"
VARS = ROOT / "defs" / "JK08A.vars.csv"

DEAD_WORD = 0xFFFF162E
DEAD_WORD_POINTER_SITES = (
    0x22770,
    0x22774,
    0x22778,
    0x227A0,
    0x24D30,
    0x24D34,
    0x24D38,
    0x24D60,
)


def read_by(path, key):
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key]: row for row in csv.DictReader(source)}


def u16be(data, offset):
    return int.from_bytes(data[offset : offset + 2], "big")


def u32be(data, offset):
    return int.from_bytes(data[offset : offset + 4], "big")


class BaseFuelScheduleScaleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        cls.funcs = read_by(FUNCS, "addr")
        cls.vars = read_by(VARS, "addr")

    def test_precursor_stage_normalizers_are_bound_to_instruction_bytes(self):
        rom = self.rom
        # mov #0x64,r9 ; shll8 r9: bank-multiplier divisor 0x6400.
        self.assertEqual(rom[0x4E9EC:0x4E9EE].hex(), "e964")
        self.assertEqual(rom[0x4E9F4:0x4E9F6].hex(), "4918")
        # mul.l r13,r2 ; shlr16 r13 ; shlr r13: schedule * multiplier >> 17.
        self.assertEqual(rom[0x4E9FA:0x4E9FC].hex(), "02d7")
        self.assertEqual(rom[0x4EA00:0x4EA04].hex(), "4d294d01")
        # mov r9,r0 ; jsr @r6 with r6 = 00021ce0: division by 0x6400.
        self.assertEqual(rom[0x4EA1E:0x4EA22].hex(), "6093460b")
        self.assertEqual(u32be(rom, 0x4EBFC), 0x00021CE0)
        # mov #-2,r6 before 0002657c: common gain over 16384.
        self.assertEqual(rom[0x4EA2E:0x4EA30].hex(), "e6fe")
        self.assertEqual(u32be(rom, 0x4EC10), 0x0002657C)
        self.assertEqual(u16be(rom, 0x94E8), 170)

    def test_trim_stage_neutral_and_shift_are_bound_to_instruction_bytes(self):
        rom = self.rom
        # Closed-loop constant -0xC800 and open-loop constant -0x6400.
        self.assertEqual(u32be(rom, 0x4EC1C), 0xFFFF3800)
        self.assertEqual(rom[0x4EB2E:0x4EB30].hex(), "e29c")
        self.assertEqual(rom[0x4EB32:0x4EB34].hex(), "4218")
        # mul.l r4,r6 ; ... sts macl,r2 ; shlr16 r2: precursor * delta >> 16.
        self.assertEqual(rom[0x4EB64:0x4EB66].hex(), "0647")
        self.assertEqual(rom[0x4EB6A:0x4EB6E].hex(), "021a4229")
        # mov #0x64,r5 and the init stores of both third-trim words.
        self.assertEqual(rom[0x2C6F6:0x2C6F8].hex(), "e564")
        self.assertEqual(rom[0x2C976:0x2C978].hex(), "0655")
        self.assertEqual(rom[0x2C97C:0x2C97E].hex(), "0655")
        self.assertEqual(u32be(rom, 0x5B7C4), 0xFFFF2A24)
        self.assertEqual((rom[0x82E4], rom[0x82E5]), (90, 110))

    def test_fixed_normalizers_multiply_to_one_hundred_over_2048(self):
        for schedule in range(0, 65536, 8):
            scheduled = schedule * 0x4000 >> 17
            banked = scheduled * 0x6400 // 0x6400
            pulse = banked * 0x6400 >> 16
            self.assertEqual(pulse, schedule * 100 // 2048)
        for schedule in (1, 7, 6631, 33333, 65535):
            pulse = (schedule * 0x4000 >> 17) * 0x6400 >> 16
            self.assertLessEqual(schedule * 100 // 2048 - pulse, 1)
            self.assertGreaterEqual(schedule * 100 // 2048 - pulse, 0)

    def test_common_gain_constants_and_range(self):
        rom = self.rom
        self.assertEqual(u16be(rom, 0x93C6), 51865)
        self.assertEqual(u32be(rom, 0x538A8), 51865)
        self.assertEqual(rom[0x89FE], 0)
        self.assertEqual(rom[0x8AE7], 175)
        self.assertEqual(u32be(rom, 0x538D0), 76288)
        self.assertEqual(u16be(rom, 0x53896), 5259)
        self.assertEqual(u16be(rom, 0x53898), 10000)
        self.assertEqual(u32be(rom, 0x538F4), 0x128500)
        self.assertEqual(u16be(rom, 0x9332), 13972)

        def gain(fraction):
            difference = 51865 * (256 - fraction) >> 8
            ratio = min(255, (175 << 18) // ((175 << 10) + difference))
            factor = min(255, (ratio * 5259 + 0x128500) // 10000)
            return ratio, factor, factor * 13972 >> 8

        self.assertEqual(gain(0), (198, 225, 12280))
        self.assertEqual(gain(255), (255, 255, 13917))
        gains = [gain(fraction)[2] for fraction in range(256)]
        self.assertEqual(gains, sorted(gains))
        # The adjacent power-of-two scales would need half or double the gain.
        self.assertLess(max(gains) / 16384, 1.0)
        self.assertGreater(min(gains) / 16384, 0.5)
        # One count of 1/512 kPa reads the two constants as 350 and 101.3 kPa.
        self.assertEqual((175 << 10) / 512, 350.0)
        self.assertAlmostEqual(51865 / 512, 101.3, places=1)

    def test_dead_diagnostic_word_is_referenced_only_by_the_pointer_tables(self):
        rom = self.rom
        needle = DEAD_WORD.to_bytes(4, "big")
        hits = tuple(
            offset for offset in range(0, len(rom) - 3, 2)
            if rom[offset : offset + 4] == needle
        )
        self.assertEqual(hits, DEAD_WORD_POINTER_SITES)
        row = self.vars["ffff162e"]
        self.assertIn("without a runtime producer", row["semantics"])
        self.assertIn("writes:00027c50@structural", row["evidence"])
        for site in DEAD_WORD_POINTER_SITES:
            self.assertIn(f"rom_const:{site:08x}=ffff162e", row["evidence"])

    def test_ledgers_state_the_code_closed_schedule_scale(self):
        for address in ("ffff1024", "ffff1026"):
            self.assertEqual(self.vars[address]["units"], "ms*2048")
        for address in ("ffff2a24", "ffff2a26"):
            self.assertEqual(self.vars[address]["units"], "percent*256")
            self.assertIn("0x6400", self.vars[address]["semantics"])
        for address in ("ffff160d", "ffff17ee", "ffff31d8", "ffff17b9", "ffff13b1"):
            self.assertIn("writes:00053698@structural", self.vars[address]["evidence"])
        # Full-word producer semantics retain wrap and offset boundaries.
        self.assertIn("low32 multiplication", self.funcs["0004ead4"]["semantics"])
        self.assertIn("unsigned offset underflow", self.funcs["0004ead4"]["semantics"])


if __name__ == "__main__":
    unittest.main()
