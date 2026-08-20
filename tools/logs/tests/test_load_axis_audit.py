import unittest

from tools.logs import load_axis_audit


class LoadAxisFormulaTest(unittest.TestCase):
    def test_internal_load_uses_q7_scaler_ratio_and_saturates(self):
        scaler = 0x6A5A
        self.assertEqual(load_axis_audit.internal_load_raw(0, scaler), 0)
        self.assertEqual(load_axis_audit.internal_load_raw(scaler, scaler), 128)
        self.assertEqual(load_axis_audit.internal_load_raw(0xFFFF, scaler), 255)
        self.assertEqual(load_axis_audit.internal_load_raw(100, 0), 0)

    def test_implicit_u16_interpolation_matches_unsigned_finisher(self):
        values = (0, 1000, 500, 700)
        self.assertEqual(
            load_axis_audit.interpolate_implicit_u16(values, 0, 0x1000),
            0,
        )
        self.assertEqual(
            load_axis_audit.interpolate_implicit_u16(values, 0x0800, 0x1000),
            500,
        )
        self.assertEqual(
            load_axis_audit.interpolate_implicit_u16(values, 0x1800, 0x1000),
            750,
        )
        self.assertEqual(
            load_axis_audit.interpolate_implicit_u16(values, 0xFFFF, 0x1000),
            700,
        )

    def test_stock_calculated_load_uses_rpm_reference(self):
        reference = tuple(index * 4096 for index in range(16))
        self.assertEqual(
            load_axis_audit.calculated_load_raw(4096, 64, reference),
            128,
        )
        self.assertEqual(
            load_axis_audit.calculated_load_raw(0xFFFF, 64, reference),
            255,
        )
        self.assertEqual(
            load_axis_audit.calculated_load_raw(100, 0, reference),
            0,
        )

    def test_invalid_formula_inputs_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "unsigned 16-bit"):
            load_axis_audit.internal_load_raw(-1, 1)
        with self.assertRaisesRegex(ValueError, "at least two"):
            load_axis_audit.interpolate_implicit_u16((1,), 0, 1)


if __name__ == "__main__":
    unittest.main()
