from dataclasses import replace
import unittest

from patches import rolling_launch as model
from tools.logs import can_telemetry
from tools.logs import rolling_launch_audit as audit


CALIBRATION = replace(
    model.Calibration(),
    mode=model.Mode.HOLD,
    enable_mask=0x01,
    integral_gain=3,
)
# Native RPM counts of 12.5 RPM: 4000 RPM.
RPM = 320
SPEEDS = (500, 505, 512, 520, 526, 530, 528, 522, 515, 510, 506, 503, 500, 498)


def inputs(speed, button=model.BUTTON_CANCEL):
    return model.Inputs(
        button=button,
        speed=speed,
        rpm_native=RPM,
        pedal=100,
        coolant=120,
    )


def simulate(speeds, *, idle_before=2, released_after=6):
    """Snapshots of the model with the spark actuator between ticks.

    The events of the interval before a snapshot see the state of the
    previous tick, and their count follows the engine speed of the tick.
    """
    state = model.RuntimeState()
    cut = model.SparkCutState(accumulators=model.SPARK_CYLINDER_OFFSETS)
    schedule = (
        [inputs(speeds[0], model.BUTTON_RELEASED)] * idle_before
        + [inputs(speed) for speed in speeds]
        + [inputs(speeds[-1], model.BUTTON_RELEASED)] * released_after
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
        state = model.step(state, step_inputs, CALIBRATION).state
        samples.append(sample(tick, step_inputs.speed, state, cut))
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

    def test_cut_bounds_follow_the_accumulator_offsets(self):
        self.assertAlmostEqual(audit.CUTS_BELOW, 2.75 - 6 - 1)
        self.assertAlmostEqual(audit.CUTS_ABOVE, 2.75 + 1)
        self.assertAlmostEqual(audit.EVENTS_PER_COUNT_TICK, 0.0064)


if __name__ == "__main__":
    unittest.main()
