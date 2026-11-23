from pathlib import Path
import unittest

from patches import rom_checksums


ROOT = Path(__file__).resolve().parents[2]
STOCKS = {
    "1ND0A": ROOT / "rom-images/23710-1ND0A/11ND0A-20260715-stock.bin",
    "1ND3B": ROOT / "rom-images/23710-1ND3B/11ND3B-20260715-stock.bin",
    "JK00A": ROOT / "rom-images/23710-JK00A/1JK00A-20260804-stock.bin",
    "JK00C": ROOT / "rom-images/23710-JK00C/1JK00C-20260803-stock.bin",
    "JK00D": ROOT / "rom-images/23710-JK00D/1JK00D-20260726-stock.bin",
    "JK03A": ROOT / "rom-images/23710-JK03A/1JK03A-20260715-stock.bin",
    "JK03B": ROOT / "rom-images/23710-JK03B/1JK03B-20260804-stock.bin",
    "JK08A": ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin",
    "JK78C": ROOT / "rom-images/23710-JK78C/1JK78C-20260715-stock.bin",
}
EXPECTED = {
    "1ND0A": rom_checksums.ChecksumValues(
        sum16_a=0x2F52,
        sum16_b=0xB7DD,
        runtime_a_xor=0xE0F04D48,
        runtime_a_sum=0x7131B24A,
        extra=(("boot_sum16", 0xE629), ("vector_sum16", 0x41D8)),
    ),
    "1ND3B": rom_checksums.ChecksumValues(
        sum16_a=0x5DD1,
        sum16_b=0xB7DD,
        runtime_a_xor=0x5A01B3C1,
        runtime_a_sum=0xAB671F91,
        extra=(("boot_sum16", 0xE629), ("vector_sum16", 0x41D8)),
    ),
    "JK00A": rom_checksums.ChecksumValues(
        sum16_a=0xECBD,
        sum16_b=0xEEE1,
        runtime_a_xor=0xBA979B43,
        runtime_a_sum=0x1E132E15,
        runtime_b_sum=0xAC399870,
        runtime_b_xor=0x07131670,
    ),
    "JK00C": rom_checksums.ChecksumValues(
        sum16_a=0xA02A,
        sum16_b=0xB095,
        runtime_a_xor=0xEBAEE2DD,
        runtime_a_sum=0x3BA6FCA3,
        runtime_b_sum=0xD38BA003,
        runtime_b_xor=0xDA585443,
    ),
    "JK00D": rom_checksums.ChecksumValues(
        sum16_a=0xD2C8,
        sum16_b=0xD962,
        runtime_a_xor=0xD1850CAA,
        runtime_a_sum=0x0B2CD270,
        runtime_b_sum=0xD396725D,
        runtime_b_xor=0xDA5E998D,
    ),
    "JK03A": rom_checksums.ChecksumValues(
        sum16_a=0xD58A,
        sum16_b=0xEEE1,
        runtime_a_xor=0xE93FB358,
        runtime_a_sum=0xD61BC71C,
        runtime_b_sum=0xAC399870,
        runtime_b_xor=0x07131670,
    ),
    "JK03B": rom_checksums.ChecksumValues(
        sum16_a=0x9A0A,
        sum16_b=0xEEE1,
        runtime_a_xor=0xFF15D54A,
        runtime_a_sum=0x2EC1B4D2,
        runtime_b_sum=0xAC399870,
        runtime_b_xor=0x07131670,
    ),
    "JK08A": rom_checksums.ChecksumValues(
        sum16_a=0x2CAE,
        sum16_b=0xEEE1,
        runtime_a_xor=0x47A28253,
        runtime_a_sum=0x094AA8CF,
        runtime_b_sum=0xAC399870,
        runtime_b_xor=0x07131670,
    ),
    "JK78C": rom_checksums.ChecksumValues(
        sum16_a=0x1F44,
        sum16_b=0xCCFA,
        runtime_a_xor=0xE1E877CF,
        runtime_a_sum=0x0AF99D87,
        runtime_b_sum=0x2BAC8C8C,
        runtime_b_xor=0xC83320EC,
    ),
}


class RomChecksumsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stocks = {
            rom: path.read_bytes() for rom, path in STOCKS.items()
        }

    def test_registered_stock_values_match_firmware_contracts(self):
        for rom, stock in self.stocks.items():
            with self.subTest(rom=rom):
                layout = rom_checksums.layout_for_rom(rom)
                result = rom_checksums.require_valid(stock, layout, f"{rom} stock")
                self.assertEqual(result.stored, EXPECTED[rom])

    def test_member_specific_runtime_a_fields_are_not_conflated(self):
        jk00c = rom_checksums.layout_for_rom("JK00C")
        jk00d = rom_checksums.layout_for_rom("JK00D")
        self.assertEqual(jk00c.runtime_a_xor_field, 0x9798)
        self.assertEqual(jk00c.runtime_a_sum_field, 0x97A0)
        self.assertEqual(jk00d.runtime_a_xor_field, 0x97A8)
        self.assertEqual(jk00d.runtime_a_sum_field, 0x97B0)
        self.assertEqual(jk00c.runtime_b_end, jk00d.runtime_b_end)

    def test_jk78c_uses_its_exact_runtime_fields_and_b_boundary(self):
        layout = rom_checksums.layout_for_rom("JK78C")
        self.assertEqual(layout.runtime_a_xor_field, 0x93D4)
        self.assertEqual(layout.runtime_a_sum_field, 0x93DC)
        self.assertEqual(layout.runtime_b_end, 0x22604)
        self.assertEqual(
            layout.runtime_a_exclusions,
            frozenset({0x93D4, 0x93DC, 0x20000}),
        )

    def test_sh7059_layout_covers_both_firmware_verifiers(self):
        layout = rom_checksums.layout_for_rom("1ND0A")
        self.assertEqual(layout, rom_checksums.layout_for_rom("1ND3B"))
        self.assertEqual(len(layout.checksum_fields), 6)
        self.assertEqual(
            {domain.key for domain in layout.sum16_domains},
            {"sum16_a", "sum16_b", "boot_sum16", "vector_sum16"},
        )
        self.assertEqual(
            layout.runtime_a_exclusions,
            frozenset({0x8200, 0x9610, 0x9618, 0x20000}),
        )

    def test_sh7059_lower_code_mutations_close_auxiliary_sum16_fields(self):
        layout = rom_checksums.layout_for_rom("1ND0A")
        changed = bytearray(self.stocks["1ND0A"])
        changed[0x1000] ^= 0x55
        changed[0x6500] ^= 0xAA
        fixed = rom_checksums.recalculate(changed, layout)
        self.assertTrue(rom_checksums.verify(fixed, layout).valid)
        self.assertNotEqual(fixed[0x5FFE:0x6000], changed[0x5FFE:0x6000])
        self.assertNotEqual(fixed[0x6EFE:0x6F00], changed[0x6EFE:0x6F00])

    def test_1ek7a_read_reproduces_calibration_and_application_checksums(self):
        stock = (ROOT / "rom-images/23710-1EK7A/11EK7A-20261122-stock.bin").read_bytes()
        layout = rom_checksums.layout_for_rom("1EK7A")
        result = rom_checksums.verify(stock, layout)
        self.assertEqual(result.stored.sum16_a, 0x99C0)
        self.assertEqual(result.stored.sum16_b, 0x020D)
        self.assertEqual(result.stored.boot_sum16, 0x93D6)
        self.assertEqual(result.stored.runtime_a_xor, 0x3A58C08F)
        self.assertEqual(result.stored.runtime_a_sum, 0xFC0CEBF1)
        self.assertEqual(result.stored.vector_sum16, 0x7C56)
        self.assertEqual(result.calculated.vector_sum16, 0x73DA)
        self.assertEqual(result.mismatches, ("vector_sum16",))
        with self.assertRaisesRegex(rom_checksums.ChecksumError, "vector_sum16"):
            rom_checksums.require_valid(stock, layout)
        fixed = rom_checksums.recalculate(stock, layout)
        self.assertEqual(fixed, stock[:0x6EFE] + b"\x73\xDA" + stock[0x6F00:])
        self.assertTrue(rom_checksums.verify(fixed, layout).valid)

        edited = bytearray(stock)
        edited[0x9000] ^= 1
        result = rom_checksums.verify(edited, layout)
        self.assertEqual(set(result.mismatches), {
            "sum16_a", "runtime_a_xor", "runtime_a_sum", "vector_sum16",
        })
        fixed = rom_checksums.recalculate(edited, layout)
        self.assertTrue(rom_checksums.verify(fixed, layout).valid)
        self.assertEqual(fixed[0x9000], edited[0x9000])

    def test_each_layout_recalculates_only_its_checksum_fields(self):
        for rom, stock in self.stocks.items():
            with self.subTest(rom=rom):
                layout = rom_checksums.layout_for_rom(rom)
                changed = bytearray(stock)
                changed[0x8725] ^= 0x01
                changed[0x09A1A] ^= 0x12
                changed[0xDE900] ^= 0x34
                self.assertFalse(rom_checksums.verify(changed, layout).valid)
                fixed = rom_checksums.recalculate(changed, layout)
                self.assertTrue(rom_checksums.verify(fixed, layout).valid)
                permitted = rom_checksums.checksum_byte_offsets(layout)
                actual = {
                    offset
                    for offset, (before, after) in enumerate(zip(changed, fixed))
                    if before != after
                }
                self.assertLessEqual(actual, permitted)
                for offset in (0x8725, 0x09A1A, 0xDE900):
                    self.assertEqual(fixed[offset], changed[offset])

    def test_unknown_rom_is_rejected(self):
        with self.assertRaisesRegex(
            rom_checksums.ChecksumError, "no checksum layout"
        ):
            rom_checksums.layout_for_rom("UNKNOWN")


if __name__ == "__main__":
    unittest.main()
