import contextlib
from dataclasses import replace
import io
from pathlib import Path
import tempfile
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


if __name__ == "__main__":
    unittest.main()
