import unittest

from tools.logs import cvtc_target_audit


class CvtcTargetFormulaTest(unittest.TestCase):
    def test_exhaust_calibration_uses_exhaust_surfaces_and_reference(self):
        calibration = cvtc_target_audit.load_calibration(target="exhaust")
        self.assertEqual(calibration.main.address, 0xB33A)
        self.assertEqual(calibration.cold.address, 0xB2FA)
        self.assertEqual(calibration.correction.address, 0xAB4A)
        self.assertEqual(calibration.conditioned_reference, "reference_b_raw")
        with self.assertRaisesRegex(ValueError, "unknown CVTC target"):
            cvtc_target_audit.load_calibration(target="unknown")

    def test_explicit_axis_clamps_and_returns_q016_fraction(self):
        axis = (10, 20, 40)
        self.assertEqual(cvtc_target_audit.explicit_axis_position(axis, 0), (0, 0))
        self.assertEqual(cvtc_target_audit.explicit_axis_position(axis, 10), (0, 0))
        self.assertEqual(
            cvtc_target_audit.explicit_axis_position(axis, 15),
            (0, 0x8000),
        )
        self.assertEqual(cvtc_target_audit.explicit_axis_position(axis, 20), (1, 0))
        self.assertEqual(cvtc_target_audit.explicit_axis_position(axis, 40), (2, 0))
        self.assertEqual(cvtc_target_audit.explicit_axis_position(axis, 255), (2, 0))

    def test_two_dimensional_interpolation_matches_stock_operation_order(self):
        calibration = cvtc_target_audit.ExplicitU8Map(
            address=0,
            row_axis=(10, 20),
            column_axis=(30, 40),
            table=((0, 100), (200, 255)),
        )
        self.assertEqual(
            cvtc_target_audit.interpolate_explicit_u8(calibration, 15, 35),
            138,
        )
        self.assertEqual(
            cvtc_target_audit.interpolate_explicit_u8(calibration, 0, 255),
            100,
        )
        self.assertEqual(cvtc_target_audit._linear_u8(10, 0, 0x5555), 7)

    def test_conditional_correction_is_centered_and_saturated(self):
        self.assertEqual(
            cvtc_target_audit.conditional_main_target(180, 150, 0),
            180,
        )
        self.assertEqual(
            cvtc_target_audit.conditional_main_target(180, 150, 0x40),
            158,
        )
        self.assertEqual(
            cvtc_target_audit.conditional_main_target(20, 200, 0x40),
            0,
        )
        self.assertEqual(
            cvtc_target_audit.conditional_main_target(255, 0, 0x40),
            255,
        )

    def test_coolant_selector_uses_signed_division_toward_zero(self):
        self.assertEqual(
            cvtc_target_audit.coolant_selected_target(128, 180, 100, 106, 131),
            (128, "cold"),
        )
        self.assertEqual(
            cvtc_target_audit.coolant_selected_target(128, 180, 132, 106, 131),
            (180, "warm"),
        )
        self.assertEqual(
            cvtc_target_audit.coolant_selected_target(128, 180, 118, 106, 131),
            (152, "blend"),
        )
        self.assertEqual(
            cvtc_target_audit.coolant_selected_target(180, 128, 118, 106, 131),
            (156, "blend"),
        )

    def test_invalid_axis_and_thresholds_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "nondecreasing"):
            cvtc_target_audit.explicit_axis_position((2, 1), 1)
        with self.assertRaisesRegex(ValueError, "below warm"):
            cvtc_target_audit.coolant_selected_target(1, 2, 3, 10, 10)

    def test_error_summary_uses_nearest_rank_percentile(self):
        summary = cvtc_target_audit._error_summary([0] * 18 + [1, 10])
        self.assertEqual(summary.exact, 18)
        self.assertEqual(summary.within_one, 19)
        self.assertEqual(summary.p95_absolute, 1)
        self.assertEqual(summary.maximum_absolute, 10)

    def test_alignment_separates_conditioned_neutralization(self):
        def sample(tick, reference):
            return cvtc_target_audit.CvtcSample(
                timestamp=tick / 100.0,
                run=0,
                tick=tick,
                bfs_raw=1,
                rpm_raw=4,
                coolant_raw=140,
                coolant_age_ms=0.0,
                knock_surface_state=0,
                reference_a_raw=reference,
                reference_b_raw=128,
                intake_actual_b1_raw=128,
                intake_actual_b2_raw=128,
            )

        def point(selected):
            return cvtc_target_audit.ReplayPoint(
                load_raw=1,
                rpm50_raw=1,
                cold_raw=selected,
                main_base_raw=selected,
                correction_raw=128,
                main_selected_raw=selected,
                coolant_selected_raw=selected,
                coolant_band="warm",
                correction_active=False,
            )

        samples = [
            sample(0, 150),
            sample(1, 128),
            sample(2, 150),
            sample(3, 160),
            sample(4, 160),
            sample(5, 160),
        ]
        points = [point(value) for value in (150, 150, 150, 160, 160, 160)]
        summary = cvtc_target_audit._alignment_summary(
            samples, points, 0, 1, (1,)
        )

        self.assertEqual(summary.conditioned_neutralization_count, 1)
        self.assertEqual(summary.conditioned_neutralization_runs, 1)
        self.assertEqual(
            summary.without_conditioned_neutralization.comparisons, 5
        )
        self.assertEqual(summary.active_to_active.exact, 5)
        self.assertEqual(summary.stable_active[0].errors.exact, 3)

    def test_all_neutral_alignment_has_no_active_comparison(self):
        samples = [
            cvtc_target_audit.CvtcSample(
                timestamp=tick / 100.0,
                run=0,
                tick=tick,
                bfs_raw=1,
                rpm_raw=4,
                coolant_raw=140,
                coolant_age_ms=0.0,
                knock_surface_state=0,
                reference_a_raw=128,
                reference_b_raw=128,
                intake_actual_b1_raw=128,
                intake_actual_b2_raw=128,
            )
            for tick in range(3)
        ]
        points = [
            cvtc_target_audit.ReplayPoint(
                load_raw=1,
                rpm50_raw=1,
                cold_raw=128,
                main_base_raw=128,
                correction_raw=128,
                main_selected_raw=128,
                coolant_selected_raw=128,
                coolant_band="warm",
                correction_active=False,
            )
            for _ in samples
        ]

        summary = cvtc_target_audit._alignment_summary(
            samples, points, 0, 1, (1,)
        )
        self.assertIsNone(summary.active_to_active)
        self.assertEqual(summary.stable_active, ())
        self.assertEqual(
            cvtc_target_audit._format_errors("active", None),
            "    active: n=0",
        )

    def test_exhaust_alignment_conditions_against_reference_b(self):
        sample = cvtc_target_audit.CvtcSample(
            timestamp=0.0,
            run=0,
            tick=0,
            bfs_raw=1,
            rpm_raw=4,
            coolant_raw=140,
            coolant_age_ms=0.0,
            knock_surface_state=0,
            reference_a_raw=200,
            reference_b_raw=150,
            intake_actual_b1_raw=128,
            intake_actual_b2_raw=128,
        )
        point = cvtc_target_audit.ReplayPoint(
            load_raw=1,
            rpm50_raw=1,
            cold_raw=150,
            main_base_raw=150,
            correction_raw=128,
            main_selected_raw=150,
            coolant_selected_raw=150,
            coolant_band="warm",
            correction_active=False,
        )
        summary = cvtc_target_audit._alignment_summary(
            [sample],
            [point],
            0,
            1,
            (),
            "reference_b_raw",
        )
        self.assertEqual(summary.active_to_active.exact, 1)
        with self.assertRaisesRegex(ValueError, "reference A or B"):
            cvtc_target_audit._alignment_summary(
                [sample], [point], 0, 1, (), "invalid"
            )


if __name__ == "__main__":
    unittest.main()
