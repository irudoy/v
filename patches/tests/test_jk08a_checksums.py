from pathlib import Path
import unittest

from patches import jk08a_checksums as checksums


ROOT = Path(__file__).resolve().parents[2]
STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK08A"
    / "1JK08A-20260726-stock.bin"
)
JK00A_STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK00A"
    / "1JK00A-20260804-stock.bin"
)
JK03B_STOCK = (
    ROOT
    / "rom-images"
    / "23710-JK03B"
    / "1JK03B-20260804-stock.bin"
)


class Jk08aChecksumsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.stock = STOCK.read_bytes()
        cls.jk00a_stock = JK00A_STOCK.read_bytes()
        cls.jk03b_stock = JK03B_STOCK.read_bytes()

    def test_stock_values_match_the_documented_contract(self):
        result = checksums.require_valid(self.stock)
        self.assertEqual(
            result.stored,
            checksums.ChecksumValues(
                sum16_a=0x2CAE,
                sum16_b=0xEEE1,
                runtime_a_xor=0x47A28253,
                runtime_a_sum=0x094AA8CF,
                runtime_b_sum=0xAC399870,
                runtime_b_xor=0x07131670,
            ),
        )

    def test_jk03b_values_match_the_documented_contract(self):
        result = checksums.require_valid(self.jk03b_stock, "JK03B stock")
        self.assertEqual(
            result.stored,
            checksums.ChecksumValues(
                sum16_a=0x9A0A,
                sum16_b=0xEEE1,
                runtime_a_xor=0xFF15D54A,
                runtime_a_sum=0x2EC1B4D2,
                runtime_b_sum=0xAC399870,
                runtime_b_xor=0x07131670,
            ),
        )

    def test_jk00a_values_match_the_documented_contract(self):
        result = checksums.require_valid(self.jk00a_stock, "JK00A stock")
        self.assertEqual(
            result.stored,
            checksums.ChecksumValues(
                sum16_a=0xECBD,
                sum16_b=0xEEE1,
                runtime_a_xor=0xBA979B43,
                runtime_a_sum=0x1E132E15,
                runtime_b_sum=0xAC399870,
                runtime_b_xor=0x07131670,
            ),
        )

    def test_mutation_is_detected_and_recalculation_is_self_consistent(self):
        changed = bytearray(self.stock)
        changed[0x8725] ^= 0x01
        changed[0x09A1A] ^= 0x12
        changed[0x0D2108] = 0x34
        self.assertFalse(checksums.verify(changed).valid)

        fixed = checksums.recalculate(changed)
        self.assertTrue(checksums.verify(fixed).valid)
        for offset in (0x8725, 0x09A1A, 0x0D2108):
            with self.subTest(offset=offset):
                self.assertEqual(fixed[offset], changed[offset])

    def test_recalculation_changes_only_checksum_fields_on_valid_stock(self):
        self.assertEqual(checksums.recalculate(self.stock), self.stock)

    def test_wrong_image_size_is_rejected(self):
        with self.assertRaisesRegex(
            checksums.ChecksumError, "expected 1048576"
        ):
            checksums.verify(self.stock[:-1])


if __name__ == "__main__":
    unittest.main()
