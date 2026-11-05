import math
from pathlib import Path
import tempfile
import unittest

from tools.can_dashboard import recording
from tools.logs import mlg_relation_audit, mlvlg
from tools.logs.load_axis_audit import calculated_load_raw


def synthetic_values(calibration, index):
    """Return one record whose channels satisfy the audited relations."""
    step = index // 10
    rpm = 60 + step % 200
    maf_b1 = 100 + (step * 37) % 600
    maf_b2 = maf_b1 + 2
    output_a, output_b, total = mlg_relation_audit.maf_total_raw(
        calibration, maf_b1, maf_b2
    )
    bfs = mlg_relation_audit.bfs_reference_raw(
        calibration, output_a + output_b, 2 * rpm
    )
    duty = 20 + index % 150
    final = 12 + index % 30
    knock = -307 if 100 <= index < 110 else 0
    if index >= 110:
        knock = min(0, -307 + 13 * ((index - 110) // 10 + 1))
    values = {
        # The RPM/12.5 coordinate of the pass, which no channel records, and
        # the stock engine-speed frame that carries it.
        "engine_speed_counts": rpm,
        "stock_rpm": rpm * 12.5,
        "maf_b1_raw": maf_b1,
        "maf_b2_raw": maf_b2,
        "maf_total_raw": total,
        "bfs_raw": bfs,
        "calculated_load_raw": calculated_load_raw(
            bfs, rpm, calibration.calculated_load_reference
        ),
        "af_state_factor_raw": 0x4000,
        "fuel_inhibit_mask": 0x3F if 200 <= index < 205 else 0,
        "stft_b1_raw": 0x6400,
        "stft_b2_raw": 26112,
        "injection_0_raw": round(0.885 * bfs / 2048 * 100 + 45),
        "injection_1_raw": round(0.885 * bfs * 26112 / 25600 / 2048 * 100 + 45),
        "intake_cvtc_duty_b1_raw": duty,
        "intake_cvtc_duty_command_b1_raw": duty,
        "intake_cvtc_duty_b2_raw": duty + 1,
        "intake_cvtc_duty_command_b2_raw": duty,
        "intake_cvtc_target_raw": 160,
        "intake_cvtc_actual_b1_raw": 160 + (index % 3 == 0),
        "intake_cvtc_actual_b2_raw": 159,
        "exhaust_cvtc_target_raw": 128 if index < 150 else 140,
        "exhaust_cvtc_actual_b1_raw": 128 if index < 150 else 140,
        "exhaust_cvtc_actual_b2_raw": 128 if index < 150 else 142,
        "final_timing_raw": final,
        "apc_command_raw": 110 - final,
        "knock_timing_state_raw": knock,
        "high_detonation_selected": 0,
        "ltft_b1_raw": 0x6400,
        "ltft_b2_raw": 0x6400,
        "coolant_raw": 141,
        "iat_raw": 80 + index % 5,
        "battery_voltage_raw": 165,
    }
    return values


def sparse_values(calibration, index):
    """Return a record of a recording whose channels carry no value at times.

    The first records precede every frame, and the exhaust actual of bank 1
    is a dynamic-page field that the active configuration omits until
    record 100; the recorder writes NaN for both.
    """
    values = synthetic_values(calibration, index)
    if index < 10:
        return {name: math.nan for name in values}
    if index < 100:
        values["exhaust_cvtc_actual_b1_raw"] = math.nan
    return values


def chain_values(calibration, index):
    """Return one record whose pulse words follow the code chain exactly."""
    values = synthetic_values(calibration, index)
    gain = mlg_relation_audit.common_pulse_gain_raw(
        calibration,
        values["bfs_raw"],
        values["iat_raw"],
        min(0xFF, values["engine_speed_counts"] >> 1),
    )
    for bank, channel in ((1, 0), (2, 1)):
        values[f"injection_{channel}_raw"] = mlg_relation_audit.pulse_reference_raw(
            calibration,
            values["bfs_raw"],
            gain,
            values[f"stft_b{bank}_raw"],
            values[f"ltft_b{bank}_raw"],
            values["battery_voltage_raw"],
        )
    return values


def write_synthetic_log(
    path,
    calibration,
    records=300,
    producer=synthetic_values,
    bindings=None,
):
    if bindings is None:
        bindings = list(recording.build_bindings("tuning"))
        present = {binding.source for binding in bindings}
        for bank in (1, 2):
            source = f"intake_cvtc_duty_command_b{bank}_raw"
            if source not in present:
                bindings.append(recording.FieldBinding(
                    mlvlg.FieldSpec(f"Intake CVTC duty command B{bank}", "%", "CVTC"),
                    source,
                ))
    specs = [binding.spec for binding in bindings]
    with path.open("wb") as stream:
        writer = mlvlg.StreamWriter(stream, specs, 1_789_600_000)
        for index in range(records):
            values = producer(calibration, index)
            row = []
            for binding in bindings:
                if binding.source == "date":
                    row.append(1_789_600_000 + index // 100)
                elif binding.source == "elapsed":
                    row.append(index / 100)
                else:
                    row.append(values.get(binding.source, 0))
            writer.write(row, index / 100)
    return specs


class MlgRelationAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calibration = mlg_relation_audit.load_calibration()

    def test_stock_constants_are_read_from_the_registered_image(self):
        calibration = self.calibration
        self.assertEqual(len(calibration.maf_curve_b1), 64)
        self.assertEqual(calibration.maf_curve_b1[0], 211)
        self.assertEqual(calibration.maf_curve_b2[0], 222)
        self.assertEqual(calibration.maf_sum_offset, 0)
        self.assertEqual(calibration.maf_did_factor, 105)
        self.assertEqual(
            (calibration.bfs_f, calibration.bfs_k, calibration.bfs_e),
            (109, 26806, 3),
        )
        self.assertEqual(calibration.load_scaler, 0x6A5A)

    def test_maf_total_and_bfs_reference_follow_the_exact_formulas(self):
        output_a, output_b, total = mlg_relation_audit.maf_total_raw(
            self.calibration, 0, 0
        )
        self.assertEqual((output_a, output_b), (211, 222))
        self.assertEqual(total, 105 * 433 // 256)
        self.assertEqual(
            mlg_relation_audit.bfs_reference_raw(self.calibration, 0, 100), 0
        )
        reference = mlg_relation_audit.bfs_reference_raw(
            self.calibration, 20000, 400
        )
        fixed = min((109 * 26806 * 20000 // 256) // (3 * 400), 0x726F9)
        self.assertEqual(reference, fixed * 9163 // 65536)
        floored = mlg_relation_audit.bfs_reference_raw(
            self.calibration, 20000, 10
        )
        self.assertEqual(
            floored,
            mlg_relation_audit.bfs_reference_raw(self.calibration, 20000, 64),
        )

    def test_synthetic_recording_reproduces_every_relation(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "synthetic.mlg"
            write_synthetic_log(log, self.calibration)
            result = mlg_relation_audit.audit_recording(
                mlg_relation_audit.read_recording(log),
                self.calibration,
                hold=6,
                target_hold=20,
            )

        self.assertEqual(result["record_count"], 300)

        self.assertEqual(result["intake_duty_b1_nonzero_pair_count"], 300)
        self.assertEqual(result["intake_duty_b1_monitor_minus_command_mean"], 0)
        self.assertEqual(result["intake_duty_b1_equal_share"], 1.0)
        self.assertEqual(result["intake_duty_b2_equal_share"], 0.0)
        self.assertEqual(result["intake_duty_b1_within_three_share"], 1.0)
        self.assertAlmostEqual(result["intake_duty_b1_correlation"], 1.0)
        self.assertEqual(result["intake_duty_b2_monitor_minus_command_mean"], 1)

        self.assertEqual(
            result["intake_cvtc_b1_steady_target_sample_count"], 280
        )
        self.assertEqual(result["intake_cvtc_b1_steady_target_within_two_share"], 1.0)
        self.assertEqual(result["intake_cvtc_b2_steady_target_error_p5"], -1)
        self.assertEqual(
            result["exhaust_cvtc_b1_steady_target_sample_count"], 260
        )
        self.assertEqual(result["exhaust_cvtc_b2_steady_target_error_p95"], 2)

        self.assertGreater(result["maf_chain_steady_sample_count"], 0)
        self.assertEqual(result["maf_chain_exact_share"], 1.0)
        self.assertEqual(result["maf_chain_within_one_share"], 1.0)
        self.assertAlmostEqual(
            result["maf_total_over_transfer_sum_median"], 105 / 256, places=3
        )

        self.assertEqual(result["calculated_load_same_record_exact_share"], 1.0)
        self.assertLess(result["calculated_load_prior_record_exact_share"], 1.0)

        self.assertGreater(result["bfs_steady_sample_count"], 0)
        self.assertEqual(result["bfs_over_producer_reference_median"], 1.0)

        self.assertEqual(result["injection_b1_closed_loop_sample_count"], 295)
        self.assertAlmostEqual(result["injection_b1_closed_loop_slope"], 0.885, places=2)
        self.assertAlmostEqual(
            result["injection_b1_closed_loop_intercept_raw"], 45, delta=1
        )
        self.assertAlmostEqual(result["injection_b2_closed_loop_slope"], 0.885, places=2)
        self.assertGreater(result["injection_b2_closed_loop_correlation"], 0.999)

        self.assertEqual(result["final_timing_apc_identity_share"], 1.0)
        self.assertEqual(result["fuel_inhibit_mask_values"], [0, 63])
        self.assertEqual(result["fuel_inhibit_full_mask_sample_count"], 5)
        self.assertEqual(result["knock_state_min"], -307)
        self.assertEqual(result["knock_state_event_step_count"], 1)
        self.assertEqual(result["knock_state_recovery_step_count"], 19)
        self.assertEqual(result["high_detonation_selected_count"], 0)
        self.assertEqual(result["ltft_b1_values"], [0x6400])
        self.assertEqual(result["coolant_raw_range"], [141, 141])
        self.assertEqual(result["battery_raw_range"], [165, 165])

    def test_pulse_chain_constants_are_read_from_the_registered_image(self):
        calibration = self.calibration
        self.assertEqual(
            calibration.pulse_gain_load_curve,
            (34, 54, 74, 94, 114, 134, 154, 174, 194, 214, 234, 255, 255, 255, 255, 255),
        )
        self.assertEqual(
            calibration.pulse_gain_speed_curve,
            (33, 26, 18, 14, 11, 11, 5, 4, 8, 3, 0, 0, 0, 0, 0, 0),
        )
        self.assertEqual(
            (
                calibration.pulse_gain_pressure,
                calibration.pulse_gain_pressure_slope,
                calibration.pulse_gain_ratio_floor,
                calibration.pulse_gain_temperature_floor,
                calibration.pulse_gain_temperature_ceiling,
                calibration.pulse_gain_rail,
                calibration.pulse_gain_scalar,
            ),
            (51865, 0, 128, 51, 215, 175, 13972),
        )
        self.assertEqual(
            calibration.pulse_gain_pressure,
            mlg_relation_audit.PULSE_GAIN_PRESSURE_DIVISOR,
        )
        self.assertEqual(
            (
                calibration.pulse_precursor_floor,
                calibration.pulse_opening_slope,
                calibration.pulse_opening_base,
            ),
            (170, 92, 70),
        )

    def test_common_gain_and_pulse_reference_follow_the_stage_arithmetic(self):
        calibration = self.calibration
        gain = mlg_relation_audit.common_pulse_gain_raw
        self.assertEqual(gain(calibration, 6631, 97, 26), 12935)
        self.assertEqual(gain(calibration, 0, 75, 0), 12607)
        self.assertEqual(gain(calibration, 20000, 60, 120), 13808)
        self.assertEqual(gain(calibration, 65535, 75, 255), 255 * 13972 >> 8)

        pulse = mlg_relation_audit.pulse_reference_raw
        self.assertEqual(pulse(calibration, 6631, 12935, 27412, 25600, 165), 350)
        self.assertEqual(pulse(calibration, 6631, 12935, 25600, 25600, 175), 325)
        # Below the precursor floor the pulse is floor * 100 / 256 plus opening time.
        self.assertEqual(pulse(calibration, 1000, 12935, 25600, 25600, 175), 136)
        # At unity gain and neutral trims the chain is the schedule over 20.48.
        for bfs in (4096, 8192, 20480):
            self.assertEqual(
                pulse(calibration, bfs, 16384, 25600, 25600, 175) - 70,
                bfs * 100 // 2048,
            )

    def test_chain_recording_matches_the_reference_exactly(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "chain.mlg"
            write_synthetic_log(log, self.calibration, producer=chain_values)
            result = mlg_relation_audit.audit_recording(
                mlg_relation_audit.read_recording(log),
                self.calibration,
                hold=6,
                target_hold=20,
                schedule_hold=5,
            )

        self.assertEqual(result["steady_schedule_hold_records"], 5)
        for bank in (1, 2):
            prefix = f"injection_b{bank}_chain"
            self.assertGreater(result[f"{prefix}_sample_count"], 100)
            self.assertEqual(result[f"{prefix}_over_reference_median"], 1.0)
            self.assertEqual(result[f"{prefix}_over_reference_p5"], 1.0)
            self.assertEqual(result[f"{prefix}_over_reference_p95"], 1.0)
            self.assertEqual(result[f"{prefix}_within_two_percent_share"], 1.0)
            low, high = result[f"{prefix}_gain_range"]
            self.assertGreaterEqual(low, 225 * 13972 // 256 / 16384)
            self.assertLessEqual(high, 255 * 13972 // 256 / 16384)

    def test_channel_names_with_stale_marker_still_resolve(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "stale.mlg"
            specs = [
                mlvlg.FieldSpec("Date", "sec", "Time", mlvlg.MLG_U32, mlvlg.MLG_DATE),
                mlvlg.FieldSpec("Stock CAN RPM*", "rpm", "Context"),
            ]
            with log.open("wb") as stream:
                writer = mlvlg.StreamWriter(stream, specs, 1_789_600_000)
                for index in range(4):
                    writer.write((1_789_600_000, 1000.0), index / 100)
            decoded = mlg_relation_audit.read_recording(log)
        self.assertEqual(decoded.record_count, 4)
        self.assertEqual(decoded.columns["stock_rpm"], [1000.0] * 4)
        self.assertEqual(mlg_relation_audit.engine_speed_counts(decoded), [80] * 4)

    def test_the_stock_frame_supplies_the_count_of_the_current_profile(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "current.mlg"
            write_synthetic_log(log, self.calibration, records=20)
            decoded = mlg_relation_audit.read_recording(log)
        self.assertEqual(
            mlg_relation_audit.engine_speed_counts(decoded),
            [
                synthetic_values(self.calibration, index)["engine_speed_counts"]
                for index in range(20)
            ],
        )

    def test_records_without_a_value_leave_every_relation(self):
        with tempfile.TemporaryDirectory() as directory:
            log = Path(directory) / "sparse.mlg"
            write_synthetic_log(log, self.calibration, producer=sparse_values)
            decoded = mlg_relation_audit.read_recording(log)
        self.assertTrue(
            math.isnan(decoded.columns["exhaust_cvtc_actual_b1_raw"][50])
        )
        result = mlg_relation_audit.audit_recording(
            decoded, self.calibration, hold=6, target_hold=20
        )

        self.assertEqual(result["record_count"], 300)
        self.assertEqual(result["intake_duty_b1_nonzero_pair_count"], 290)
        self.assertEqual(
            result["exhaust_cvtc_b2_steady_target_sample_count"], 250
        )
        self.assertEqual(
            result["exhaust_cvtc_b1_steady_target_sample_count"], 180
        )
        self.assertEqual(result["exhaust_cvtc_b1_steady_target_within_two_share"], 1.0)
        self.assertEqual(result["maf_chain_exact_share"], 1.0)
        self.assertEqual(result["calculated_load_same_record_comparison_count"], 290)
        self.assertEqual(result["calculated_load_same_record_exact_share"], 1.0)
        self.assertEqual(result["bfs_over_producer_reference_median"], 1.0)
        self.assertEqual(result["injection_b1_closed_loop_sample_count"], 285)
        self.assertEqual(result["final_timing_apc_pair_count"], 290)
        self.assertEqual(result["final_timing_apc_identity_share"], 1.0)
        self.assertEqual(result["fuel_inhibit_mask_values"], [0, 63])
        self.assertEqual(result["knock_state_min"], -307)
        self.assertEqual(result["knock_state_event_step_count"], 1)
        self.assertEqual(result["ltft_b1_values"], [0x6400])
        self.assertEqual(result["coolant_raw_range"], [141, 141])

    def test_a_channel_without_any_value_is_absent(self):
        source = mlg_relation_audit.Recording(
            Path("absent.mlg"), "0" * 64, (),
            {"final_timing_raw": [math.nan] * 3, "apc_command_raw": [98.0] * 3}, 3,
        )
        self.assertEqual(mlg_relation_audit.audit_timing_command(source), {})

    def test_live_only_recording_reports_unavailable_latch_comparison(self):
        source = mlg_relation_audit.Recording(
            Path("live.mlg"), "0" * 64, (),
            {"intake_cvtc_duty_b1_raw": [20.0], "intake_cvtc_duty_b2_raw": [30.0]}, 1,
        )
        result = mlg_relation_audit.audit_duty_pairs(source)
        self.assertEqual(result, {"intake_duty_b1_pair_available": False,
                                  "intake_duty_b2_pair_available": False})

    def test_rotating_injection_angle_reports_only_observed_range(self):
        source = mlg_relation_audit.Recording(Path("rotating.mlg"), "0" * 64, (),
            {"injection_end_angle_raw": [float("nan"), 300.0, 300.0, 330.0]}, 4)
        self.assertEqual(mlg_relation_audit.audit_states(source),
                         {"injection_end_angle_raw_range": [300, 330]})

    def test_toml_value_formatting(self):
        self.assertEqual(mlg_relation_audit.format_value(3), "3")
        self.assertEqual(mlg_relation_audit.format_value(0.5), "0.500000")
        self.assertEqual(mlg_relation_audit.format_value([1, 2]), "[1, 2]")
        self.assertEqual(mlg_relation_audit.format_value("a.mlg"), '"a.mlg"')


if __name__ == "__main__":
    unittest.main()
