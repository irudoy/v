from pathlib import Path
import unittest

from patches import rom_checksums


ROOT = Path(__file__).resolve().parents[2]
STOCKS = {
    "JK00A": ROOT / "rom-images/23710-JK00A/1JK00A-20260804-stock.bin",
    "JK00C": ROOT / "rom-images/23710-JK00C/1JK00C-20260803-stock.bin",
    "JK00D": ROOT / "rom-images/23710-JK00D/1JK00D-20260726-stock.bin",
    "JK03A": ROOT / "rom-images/23710-JK03A/1JK03A-20260715-stock.bin",
    "JK03B": ROOT / "rom-images/23710-JK03B/1JK03B-20260804-stock.bin",
    "JK08A": ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin",
}
EXPECTED = {
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
