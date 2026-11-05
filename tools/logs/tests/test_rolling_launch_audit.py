import contextlib
from dataclasses import replace
import io
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from patches import rolling_launch as model
from tools.logs import can_telemetry
from tools.logs import rolling_launch_audit as audit


CALIBRATION = replace(
    model.Calibration(),
    mode=model.Mode.HOLD,
    enable_mask=0x01,
    slots=(model.Slot(integral_gain=3),) * model.SLOT_COUNT,
)
# Native RPM counts of 12.5 RPM: 4000 RPM.
RPM = 320
SPEEDS = (500, 505, 512, 520, 526, 530, 528, 522, 515, 510, 506, 503, 500, 498)


def inputs(speed, button=model.BUTTON_CANCEL, active_index=0):
    return model.Inputs(
        button=button,
        active_index=active_index,
        speed=speed,
        rpm_native=RPM,
        pedal=100,
        coolant=120,
    )


def simulate(
    speeds, *, idle_before=2, released_after=6, calibration=CALIBRATION,
    active_index=0,
):
    """Snapshots of the model with the spark actuator between ticks.

    The events of the interval before a snapshot see the state of the
    previous tick, and their count follows the engine speed of the tick.
    """
    state = model.RuntimeState()
    cut = model.SparkCutState(accumulators=model.SPARK_CYLINDER_OFFSETS)
    schedule = (
        [inputs(speeds[0], model.BUTTON_RELEASED, active_index)] * idle_before
        + [
            inputs(speed, active_index=active_index)
            for speed in speeds
        ]
        + [inputs(speeds[-1], model.BUTTON_RELEASED, active_index)]
        * released_after
    )
    samples = []
    pending = 0.0
    cylinder = 0
    for tick, step_inputs in enumerate(schedule):
        pending += RPM * audit.EVENTS_PER_COUNT_TICK
        while pending >= 1:
            pending -= 1
            event = model.SparkEvent(cylinder=cylinder % 6 + 1)
            cut = model.spark_event(state, cut, event).state
            cylinder += 1
        state = model.step(state, step_inputs, calibration).state
        samples.append(replace(
            sample(tick, step_inputs.speed, state, cut),
            map_index=step_inputs.active_index,
        ))
    return samples


def sample(tick, speed, state, cut):
    return audit.Sample(
        tick=tick,
        button=None,
        dashboard=None,
        speed_kmh=speed / 10,
        coolant_raw=None,
        rpm_raw=RPM,
        rpm_low=RPM - audit.STOCK_RPM_MARGIN,
        rpm_high=RPM + audit.STOCK_RPM_MARGIN,
        fuel_inhibit_mask=0,
        final_timing_raw=20,
        apc_command_raw=90,
        app1_raw=600,
        bfs_raw=1000,
        knock_surface_state=0,
        exhaust_cvtc_target_raw=0,
        phase=int(state.phase),
        abort_reason=int(state.abort_reason),
        integrator=state.integrator,
        speed_error=state.speed_error,
        torque_fraction=state.torque_fraction,
        cut_counter=cut.cut_count,
    )


def launch_law(samples):
    """The snapshots of configuration 1, which lacks the integrator."""
    return [replace(s, integrator=None, configuration=1) for s in samples]


def launch_law_integrator(samples, offset=0):
    """The snapshots of configuration 2, whose groups alternate per tick:
    group 0 carries the error and the fraction, group 1 the integrator, and
    both the cut counter."""
    result = []
    for s in samples:
        if (s.tick + offset) % 2:
            result.append(replace(
                s, speed_error=None, torque_fraction=None, configuration=0x82
            ))
        else:
            result.append(replace(s, integrator=None, configuration=2))
    return result


class HoldAuditTest(unittest.TestCase):
    def test_a_model_run_passes_every_law(self):
        samples = simulate(SPEEDS)
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertEqual(run.start_tick, 2)
        self.assertEqual(run.end_tick, 2 + len(SPEEDS) - 1)
        self.assertEqual(run.law_ticks, len(SPEEDS))
        self.assertEqual(run.failures, ())
        self.assertEqual(run.abort_reason, model.AbortReason.BUTTON_RELEASED)
        self.assertEqual(run.target_speed, (500.0, 500.0))
        self.assertGreater(run.cuts, 0)
        self.assertTrue(run.cuts_inside)

    def test_the_one_group_configuration_replays_every_step(self):
        samples = launch_law(simulate(SPEEDS))
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertEqual(run.law_ticks, len(SPEEDS))
        self.assertEqual(run.failures, ())
        self.assertTrue(run.cuts_inside)

    def test_the_one_group_configuration_catches_a_fraction_off_the_model(self):
        samples = launch_law(simulate(SPEEDS))
        index = 9
        samples[index] = replace(
            samples[index], torque_fraction=samples[index].torque_fraction - 1
        )
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertIn(samples[index].tick, {tick for tick, _ in run.failures})

    def test_the_two_group_configuration_bounds_two_tick_steps(self):
        for offset in (0, 1):
            with self.subTest(offset=offset):
                samples = launch_law_integrator(simulate(SPEEDS), offset)
                (run,) = audit.audit_hold(samples, CALIBRATION)
                self.assertEqual(run.law_ticks, len(SPEEDS) // 2)
                self.assertEqual(run.failures, ())
                self.assertEqual(run.target_speed, (500.0, 500.0))
                self.assertTrue(run.cuts_inside)

    def test_the_two_group_configuration_catches_a_fraction_off_the_model(self):
        samples = launch_law_integrator(simulate(SPEEDS))
        index = 6
        self.assertIsNotNone(samples[index].torque_fraction)
        samples[index] = replace(
            samples[index],
            torque_fraction=samples[index].torque_fraction
            + 3 * CALIBRATION.u_rate_limit,
        )
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertIn(samples[index].tick, {tick for tick, _ in run.failures})

    def test_the_configuration_byte_selects_the_current_slots(self):
        page = audit.DynamicPage.of(can_telemetry.load_schema()[1]["tuning"])
        self.assertEqual(page.field, "telemetry_page_configuration")
        values = {
            name: 7 for name in (*audit.TELEMETRY_SOURCES, *audit.HOLD_SOURCES)
        }
        expected = {
            1: {"integrator"},
            2: {"integrator"},
            0x82: {"speed_error", "torque_fraction"},
            0: {"integrator", "speed_error", "torque_fraction", "cut_counter"},
        }
        for selector, absent in expected.items():
            with self.subTest(configuration=selector):
                values[page.field] = selector
                sample = audit._sample(0, lambda name: values.get(name), RPM, page)
                self.assertEqual(sample.configuration, selector)
                self.assertEqual(sample.phase, 7)
                for attribute in ("integrator", "speed_error",
                                  "torque_fraction", "cut_counter"):
                    self.assertEqual(
                        getattr(sample, attribute) is None,
                        attribute in absent,
                        attribute,
                    )

    def test_the_integrator_reaches_the_published_fraction(self):
        samples = simulate(SPEEDS)
        integrators = [s.integrator for s in samples if s.phase == model.Phase.ACTIVE]
        self.assertTrue(any(integrators))

    def test_a_fraction_off_the_model_fails(self):
        samples = simulate(SPEEDS)
        index = 6
        samples[index] = replace(
            samples[index], torque_fraction=samples[index].torque_fraction + 1
        )
        (run,) = audit.audit_hold(samples, CALIBRATION)
        ticks = {tick for tick, _ in run.failures}
        # The next step starts from the published fraction, so the rate limit
        # may hold it; the changed tick fails in every case.
        self.assertIn(samples[index].tick, ticks)

    def test_an_integrator_off_the_model_fails(self):
        samples = simulate(SPEEDS)
        index = 8
        samples[index] = replace(
            samples[index], integrator=samples[index].integrator - 16
        )
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertIn(
            (samples[index].tick, f"integrator {samples[index].integrator}, "
             f"model {samples[index].integrator + 16}"),
            run.failures,
        )

    def test_an_error_outside_the_window_fails(self):
        samples = simulate(SPEEDS)
        index = 5
        samples[index] = replace(
            samples[index], speed_error=CALIBRATION.abort_above + 1
        )
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertIn(
            (samples[index].tick, "speed error outside the abort window"),
            run.failures,
        )

    def test_missing_cuts_fall_below_the_owed_bound(self):
        samples = simulate(SPEEDS)
        frozen = samples[2].cut_counter
        samples = [
            replace(s, cut_counter=frozen) if s.tick >= 2 else s for s in samples
        ]
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertEqual(run.cuts, 0)
        self.assertFalse(run.cuts_inside)

    def test_extra_cuts_exceed_the_owed_bound(self):
        samples = simulate(SPEEDS)
        end = 2 + len(SPEEDS)
        samples = [
            replace(s, cut_counter=(s.cut_counter + 8) & 0xFF) if s.tick >= end else s
            for s in samples
        ]
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertFalse(run.cuts_inside)

    def test_a_gap_skips_the_step_and_the_cut_bound(self):
        samples = simulate(SPEEDS)
        del samples[7]
        first, second = audit.audit_hold(samples, CALIBRATION)
        self.assertEqual(first.failures + second.failures, ())
        # Ticks 2..6 and 8..15; tick 8 lacks its predecessor.
        self.assertEqual(first.law_ticks, 5)
        self.assertEqual(second.law_ticks, len(SPEEDS) - 7)
        self.assertIsNone(first.cuts)
        self.assertIsNone(first.abort_reason)
        self.assertIsNone(second.cuts)

    def test_observe_mode_has_no_cut_bound(self):
        calibration = replace(CALIBRATION, mode=model.Mode.OBSERVE)
        samples = simulate(SPEEDS)
        (run,) = audit.audit_hold(samples, calibration)
        self.assertIsNone(run.cuts)
        self.assertIsNone(run.cuts_inside)

    def test_a_capture_without_the_hold_fields_is_refused(self):
        samples = [
            replace(s, integrator=None, speed_error=None)
            for s in simulate(SPEEDS)
        ]
        with self.assertRaisesRegex(ValueError, "hold fields"):
            audit.audit_hold(samples, CALIBRATION)
        samples = [replace(s, phase=None) for s in samples]
        with self.assertRaisesRegex(ValueError, "no Rolling Launch phase"):
            audit.audit_hold(samples, CALIBRATION)

    def test_a_capture_with_a_tick_divisor_is_refused(self):
        samples = [replace(s, tick=2 * s.tick) for s in simulate(SPEEDS)]
        with self.assertRaisesRegex(ValueError, "step by 2 ticks"):
            audit.audit_hold(samples, CALIBRATION)

    def test_a_run_without_its_idle_predecessor_checks_no_fraction(self):
        samples = launch_law(simulate(SPEEDS))[2:]
        (run,) = audit.audit_hold(samples, CALIBRATION)
        self.assertEqual(run.law_ticks, 0)
        self.assertEqual(run.failures, ())

    def test_an_audit_that_checks_nothing_fails(self):
        cases = {
            "model run": (simulate(SPEEDS), 0),
            "no fraction checked": (launch_law(simulate(SPEEDS))[2:], 1),
            "no ACTIVE run": (simulate(SPEEDS)[:2], 1),
        }
        for name, (samples, status) in cases.items():
            with self.subTest(name):
                capture = audit.Capture(Path("hold.mlg"), "0" * 64, tuple(samples))
                with (
                    mock.patch.object(
                        audit, "read_calibration", return_value=CALIBRATION
                    ),
                    mock.patch.object(audit, "read_capture", return_value=capture),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    self.assertEqual(
                        audit.main(["--image", "image.bin", "hold.mlg"]), status
                    )

    def test_the_run_uses_the_slot_of_the_selected_map(self):
        trimmed = model.Slot(
            integral_gain=2, max_trim=20, floor_command=120,
            trim_efficiency=824,
        )
        calibration = replace(
            CALIBRATION,
            enable_mask=0x08,
            slots=(model.Slot(integral_gain=3),) * 3
            + (trimmed, model.Slot(integral_gain=3)),
        )
        samples = simulate(SPEEDS, calibration=calibration, active_index=3)
        (run,) = audit.audit_hold(samples, calibration)
        self.assertEqual(run.failures, ())
        self.assertGreater(run.law_ticks, 0)
        self.assertTrue(run.cuts_inside)
        # A stock command of 90 plus the trim stays below the floor of 120.
        self.assertEqual(run.floor_ticks, 0)

        # The replay with the gain of Map 1 disagrees with the integrator.
        (wrong,) = audit.audit_hold(
            [replace(s, map_index=0) for s in samples], calibration
        )
        self.assertNotEqual(wrong.failures, ())

        with self.assertRaisesRegex(ValueError, "one selected map"):
            audit.audit_hold(
                [replace(s, map_index=None) for s in samples], calibration
            )

    def test_floor_ticks_count_the_clipped_trim(self):
        trimmed = model.Slot(
            integral_gain=3, max_trim=20, floor_command=120,
            trim_efficiency=824,
        )
        calibration = replace(
            CALIBRATION, slots=(trimmed,) * model.SLOT_COUNT
        )
        samples = simulate(SPEEDS, calibration=calibration)
        active = sum(s.phase == model.Phase.ACTIVE for s in samples)
        clipped = [replace(s, apc_command_raw=105) for s in samples]
        (run,) = audit.audit_hold(clipped, calibration)
        self.assertEqual(run.floor_ticks, active)
        # A stock command whose full trim reaches the floor is not clipped.
        (run,) = audit.audit_hold(
            [replace(s, apc_command_raw=100) for s in samples], calibration
        )
        self.assertEqual(run.floor_ticks, 0)

    def test_the_owed_cuts_follow_the_trim_efficiency(self):
        samples = simulate(SPEEDS)
        (stock,) = audit.audit_hold(samples, CALIBRATION)
        trimmed = replace(
            CALIBRATION,
            slots=(model.Slot(
                integral_gain=3, max_trim=20, floor_command=120,
                trim_efficiency=824,
            ),) * model.SLOT_COUNT,
        )
        (run,) = audit.audit_hold(samples, trimmed)
        self.assertLess(run.owed[1], stock.owed[1])

    def test_a_schema_4_image_reads_one_gain_for_every_map(self):
        layout = audit.load_layout()
        span = layout.configuration
        legacy = layout.retired_configuration_for(model.LEGACY_SCHEMA_VERSION)
        head = bytearray(CALIBRATION.to_bytes()[: model.LEGACY_CONFIG_SIZE])
        head[2] = model.LEGACY_SCHEMA_VERSION
        head[0x16:0x18] = (3).to_bytes(2, "big")
        image = bytearray(b"\xff" * max(span.end, legacy.end))
        image[legacy.start : legacy.end] = head
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.bin"
            path.write_bytes(image)
            self.assertEqual(audit.read_calibration(path), CALIBRATION)
            image[span.start : span.end] = CALIBRATION.to_bytes()
            image[legacy.start : legacy.end] = b"\xff" * len(head)
            path.write_bytes(image)
            self.assertEqual(audit.read_calibration(path), CALIBRATION)
            image[span.start : span.end] = b"\xff" * (span.end - span.start)
            path.write_bytes(image)
            with self.assertRaisesRegex(ValueError, "configuration is invalid"):
                audit.read_calibration(path)

    def test_cut_bounds_follow_the_accumulator_offsets(self):
        self.assertAlmostEqual(audit.CUTS_BELOW, 2.75 - 6 - 1)
        self.assertAlmostEqual(audit.CUTS_ABOVE, 2.75 + 1)
        self.assertAlmostEqual(audit.EVENTS_PER_COUNT_TICK, 0.0064)


class BusJoinTest(unittest.TestCase):
    @staticmethod
    def capture(samples=None):
        samples = tuple(simulate(SPEEDS) if samples is None else samples)
        times = tuple(sample.tick * 10.0 for sample in samples)
        # 0x180 and 0x160 agree even while the independent spark veto acts.
        bus = {
            0x180: tuple((t + 5, bytes.fromhex("7d004b04b0000000")) for t in times),
            0x160: tuple((t + 4.8, bytes.fromhex("4b04b000000000")) for t in times),
        }
        release = (2 + len(SPEEDS)) * 10.0
        timing = audit.TraceTiming(
            times, tuple(t + 3 for t in times),
            ((0, model.BUTTON_RELEASED), (10, model.BUTTON_CANCEL),
             (release, model.BUTTON_RELEASED)), (), bus,
        )
        return audit.Capture(Path("test.trc"), "0" * 64, samples, timing)

    def test_speed_decoder_truncates_big_endian_and_handles_invalid_word(self):
        self.assertEqual(audit.decode_speed_word(bytes.fromhex("00000000138d")), 500)
        self.assertEqual(audit.decode_speed_word(bytes.fromhex("00000000ffff")), 0)
        with self.assertRaisesRegex(ValueError, "bytes 4 and 5"):
            audit.decode_speed_word(b"\x00" * 5)

    def test_trc_reader_keeps_standard_bus_frames_without_telemetry(self):
        frames = (
            audit.peak_trc_audit.Frame(1, 10, "Rx", 0x284, b"\x00" * 8),
            audit.peak_trc_audit.Frame(2, 11, "Rx", 0x284, b"\x01" * 8,
                                      is_extended=True),
            audit.peak_trc_audit.Frame(3, 12, "Rx", 0x284, b"", remote=True),
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bus.trc"
            path.write_bytes(b"")
            with mock.patch.object(audit.peak_trc_audit, "load_trace",
                                   return_value=SimpleNamespace(frames=frames)):
                capture = audit.read_trc(path)
        self.assertEqual(capture.timing.bus_frames[0x284], ((10, b"\x00" * 8),))

    def test_equal_estimates_do_not_establish_physical_torque_recovery(self):
        capture = self.capture()
        runs = audit.audit_hold(capture.samples, CALIBRATION)
        (row,) = audit.audit_bus(capture, runs)["holds"]
        self.assertTrue(row["covered"])
        self.assertGreater(row["parallel_pairs"], 0)
        self.assertEqual(row["parallel_equal"], row["parallel_pairs"])
        self.assertIsNone(row["torque_recovery_ms"])
        self.assertIsNone(row["torque_recovery_cycles"])
        self.assertEqual(row["release_rpm"], 4000)
        self.assertEqual(row["next_torque_frame_ms"], 5)
        self.assertAlmostEqual(row["next_torque_frame_cycles"], 1 / 6)

    def test_reference_join_survives_a_tick_wrap_before_the_mlg_starts(self):
        reference = self.capture()
        wrapped = replace(reference, samples=tuple(
            replace(s, tick=s.tick + 65536) for s in reference.samples
        ))
        runs = audit.audit_hold(reference.samples, CALIBRATION)
        (row,) = audit.audit_bus(wrapped, runs, reference=reference)["holds"]
        self.assertTrue(row["covered"])
        self.assertEqual(row["start_ms"], 20)

    def test_hold_ratio_uses_the_same_stable_gear_reference_as_tcm_audit(self):
        capture = self.capture()
        bus = dict(capture.timing.bus_frames)
        times = capture.timing.first_page_ms
        speed = (850).to_bytes(2, "big") + (2000).to_bytes(2, "big") + b"\x00" * 4
        selector = next(iter(audit.tcm_shift_audit.DRIVE_SELECTORS))
        bus.update({
            0x174: tuple((t + 0.2, bytes.fromhex("ffffff2200000000")) for t in times),
            0x176: tuple((t + 0.4, speed) for t in times),
            0x177: tuple((t + 0.6, bytes.fromhex("0000010000780000")) for t in times),
            0x421: tuple((t, bytes([selector])) for t in times),
        })
        capture = replace(capture, timing=replace(capture.timing, bus_frames=bus))
        runs = audit.audit_hold(capture.samples, CALIBRATION)
        result = audit.audit_bus(capture, runs)
        self.assertEqual(result["gear_ratio_medians"], {"2": 0.425})
        (row,) = result["holds"]
        self.assertEqual(row["gears"], [2])
        self.assertEqual(row["ratio_min_median_max"], [0.425] * 3)
        self.assertEqual(row["ratio_reference_median"], 0.425)

    def test_reference_join_reports_a_hold_missing_from_a_truncated_trace(self):
        reference = self.capture()
        truncated = self.capture(reference.samples[5:])
        runs = audit.audit_hold(reference.samples, CALIBRATION)
        (row,) = audit.audit_bus(truncated, runs, reference=reference)["holds"]
        self.assertFalse(row["covered"])
        self.assertNotIn("release_ms", row)

    def test_reference_join_refuses_another_run_or_ambiguous_ticks(self):
        reference = self.capture()
        different = replace(reference, samples=(
            replace(reference.samples[0], rpm_raw=99), *reference.samples[1:]
        ))
        with self.assertRaisesRegex(ValueError, "snapshots differ"):
            audit.audit_bus(different, (), reference=reference)
        ambiguous = replace(reference, samples=(
            *reference.samples, replace(reference.samples[0], tick=65536)
        ))
        with self.assertRaisesRegex(ValueError, "ambiguous repeated tick"):
            audit.audit_bus(ambiguous, (), reference=reference)
        unrelated = replace(reference, samples=tuple(
            replace(s, tick=s.tick + 1000) for s in reference.samples
        ))
        with self.assertRaisesRegex(ValueError, "no matching snapshots"):
            audit.audit_bus(unrelated, (), reference=reference)

    def test_speed_error_selects_the_constant_target_of_284(self):
        samples = [replace(s, speed_error=e) for s, e in zip(
            simulate(SPEEDS), (0, 10, 20)
        )]
        def speed(word):
            return b"\x00" * 4 + word.to_bytes(2, "big")
        bus = {
            0x284: audit._BusIndex([(0, speed(5000)), (20, speed(5100)),
                                   (40, speed(5200))]),
            0x280: audit._BusIndex([(0, speed(6000)), (20, speed(6000)),
                                   (40, speed(6000))]),
        }
        result = audit._speed_targets(samples, (1, 21, 41), bus)
        self.assertEqual(result["0x284"]["target_intersection_raw"], [500, 500])
        self.assertEqual(result["0x284"]["target_candidates_raw"], [500])
        self.assertTrue(result["0x284"]["compatible"])
        self.assertFalse(result["0x280"]["compatible"])
        stale = audit._speed_targets(samples, (101, 121, 141), bus)
        self.assertIsNone(stale["0x284"]["compatible"])

    def test_source_needs_a_common_discrete_word_not_only_overlapping_ranges(self):
        samples = [replace(s, speed_error=0) for s in simulate(SPEEDS)[:3]]
        frames = [(time, b"\x00" * 4 + word.to_bytes(2, "big"))
                  for time, word in [(0, 1000), (10, 3000), (20, 2000), (30, 1000)]]
        bus = {can_id: audit._BusIndex(frames) for can_id in (0x280, 0x284)}
        result = audit._speed_targets(samples, (11, 21, 31), bus)["0x284"]
        self.assertEqual(result["target_intersection_raw"], [200, 200])
        self.assertEqual(result["target_candidates_raw"], [])
        self.assertFalse(result["compatible"])


if __name__ == "__main__":
    unittest.main()
