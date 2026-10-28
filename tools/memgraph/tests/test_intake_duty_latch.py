import csv
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
VARS = ROOT / "defs" / "JK08A.vars.csv"
PROFILE = ROOT / "patches" / "can-telemetry-profile.toml"
HARDWARE = ROOT / "patches" / "hardware-results.toml"

LIVE_BASE = 0xFFFF23BC
LATCH_BASE = 0xFFFF2330
PAIR_OFFSET = 0x84


def u16(data, offset):
    return int.from_bytes(data[offset : offset + 2], "big")


def u32(data, offset):
    return int.from_bytes(data[offset : offset + 4], "big")


def mov_l_literal(data, address):
    """Return the literal a PC-relative MOV.L at address loads."""
    opcode = u16(data, address)
    assert opcode >> 12 == 0xD, hex(opcode)
    return u32(data, ((address + 4) & ~3) + (opcode & 0xFF) * 4)


class IntakeDutyLatchTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rom = ROM.read_bytes()
        with VARS.open(newline="", encoding="utf-8") as source:
            cls.vars = {row["addr"]: row for row in csv.DictReader(source)}
        with PROFILE.open("rb") as source:
            contexts = tomllib.load(source)["context"]
        cls.fields = {
            field["name"]: dict(field, page=context["page"], tag=context["tag"])
            for context in contexts
            for field in context["field"]
        }
        with HARDWARE.open("rb") as source:
            cls.hardware = tomllib.load(source)

    def test_scheduler_block_copy_latches_the_live_pair(self):
        # FUN_00020DFE: r11 = byte copier, r12 = extu.b(-16) = 240.
        self.assertEqual(mov_l_literal(self.rom, 0x20EEA), 0x00022558)
        self.assertEqual(u16(self.rom, 0x20E14), 0xECF0)
        self.assertEqual(u16(self.rom, 0x20E16), 0x6CCC)
        # r12 += -100, then the copy at 0x21318 moves r0 = r12 = 140 bytes.
        self.assertEqual(u16(self.rom, 0x2130A), 0x7C9C)
        self.assertEqual(mov_l_literal(self.rom, 0x21314), LATCH_BASE)
        self.assertEqual(mov_l_literal(self.rom, 0x21316), LIVE_BASE)
        self.assertEqual(u16(self.rom, 0x21318), 0x4B0B)
        self.assertEqual(u16(self.rom, 0x2131A), 0x60C3)
        length = ((-16 & 0xFF) - 100) & 0xFF
        self.assertEqual(length, 140)
        self.assertLess(PAIR_OFFSET + 1, length)

        for channel, (live, latch) in enumerate(
            (("ffff2440", "ffff23b4"), ("ffff2441", "ffff23b5"))
        ):
            with self.subTest(channel=channel):
                self.assertEqual(int(live, 16), LIVE_BASE + PAIR_OFFSET + channel)
                self.assertEqual(int(latch, 16), LATCH_BASE + PAIR_OFFSET + channel)
                self.assertIn("scheduler latch", self.vars[latch]["semantics"])
                self.assertIn(
                    "writes:00020dfe@structural", self.vars[latch]["evidence"]
                )
                self.assertIn(
                    "writes:000be814@structural", self.vars[live]["evidence"]
                )
                self.assertEqual(
                    self.vars[live]["units"], self.vars[latch]["units"]
                )

    def test_profile_keeps_the_live_pair_without_scheduler_copies(self):
        pairs = (
            ("intake_cvtc_duty_b1_raw", 0xFFFF2440),
            ("intake_cvtc_duty_b2_raw", 0xFFFF2441),
        )
        for name, source in pairs:
            with self.subTest(field=name):
                field = self.fields[name]
                self.assertEqual(field["source"], source)
                self.assertEqual(field["scale"], "raw * 39 / 100 percent")
        self.assertEqual({self.fields[name]["tag"] for name, _ in pairs}, {1})
        self.assertEqual({self.fields[name]["page"] for name, _ in pairs}, {9})
        for bank in (1, 2):
            self.assertNotIn(f"intake_cvtc_duty_command_b{bank}_raw", self.fields)

    def test_recorded_pairs_are_equal_in_every_record(self):
        result = self.hardware["can_telemetry"]["intake_duty_latch_2026_09_21"]
        drive = self.hardware["can_telemetry"][
            "schema2_profile5_drive_2026_09_21"
        ]
        self.assertEqual(result["live_pair"], [0xFFFF2440, 0xFFFF2441])
        self.assertEqual(result["command_pair"], [0xFFFF23B4, 0xFFFF23B5])
        self.assertEqual(result["profile_id"], drive["profile_id"])
        self.assertEqual(result["profile_crc16"], drive["profile_crc16"])
        self.assertEqual(
            result["capture_count"],
            len(self.hardware["can_telemetry"]["schema2_profile5_captures"]),
        )
        self.assertLessEqual(
            result["record_count_with_both_pairs"], drive["record_count_total"]
        )
        self.assertEqual(
            result["equal_record_count"], result["record_count_with_both_pairs"]
        )
        self.assertGreater(result["nonzero_record_count"], 0)


if __name__ == "__main__":
    unittest.main()
