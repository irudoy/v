import contextlib
from dataclasses import replace
from functools import lru_cache
import io
from pathlib import Path
import struct
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock

from patches import build_rom
from patches import rolling_launch as model
from patches import rom_checksums
from patches import runtime_endpoints
from patches import runtime_targets
from patches.tests import rolling_endpoint_images as endpoint_images
from tools.logs import can_telemetry
from tools.logs import rolling_launch_audit as audit


SLOT = model.Slot(integral_gain=3)
MODEL_CALIBRATION = replace(
    model.Calibration(),
    mode=model.Mode.HOLD,
    enable_mask=0x01,
    slots=(SLOT,) * model.SLOT_COUNT,
)
TABLE = model.EfficiencyTable()
# A shared table whose trim of 20 delivers 82.4 percent of the torque.
TRIM_TABLE = model.EfficiencyTable(
    tuple(model.U_ONE - 9 * trim if trim < 20 else 824 for trim in range(41))
)


def current_calibration(calibration=MODEL_CALIBRATION, table=TABLE):
    """The audit settings of the current record of a model calibration."""
    return audit.endpoint_calibration(
        calibration.to_bytes(), "current", table.to_bytes()
    )


def historical_calibration(calibration=MODEL_CALIBRATION, slots=None, hold=True):
    """The settings of a schema 5 endpoint whose speed hold is the speed
    regulator of a model calibration."""
    return audit.HoldCalibration(
        endpoint="schema-5-fixed-trim",
        hold=hold,
        window_top=calibration.window_top,
        window_width=calibration.window_width,
        u_rate_limit=calibration.u_rate_limit,
        integrator_limit=calibration.integrator_limit,
        abort_above=calibration.abort_above,
        abort_below=calibration.abort_below,
        slots=slots or tuple(
            audit.HoldSlot(slot.integral_gain) for slot in calibration.slots
        ),
        schema=5,
    )


CALIBRATION = current_calibration()
HISTORICAL = historical_calibration()
# Native RPM counts of 12.5 RPM: 4000 RPM.
RPM = 320
SPEEDS = (500, 505, 512, 520, 526, 530, 528, 522, 515, 510, 506, 503, 500, 498)
# The RPM regulator: a standing launch at the target of the slot.
RPM_SLOT = model.Slot(
    integral_gain=3, max_trim_rpm=10, floor_command=120, launch_rpm_native=300,
    launch_soft_width_native=40,
)
RPM_CALIBRATION = replace(MODEL_CALIBRATION, slots=(RPM_SLOT,) * model.SLOT_COUNT)
RPMS = (320, 310, 302, 299, 290, 281, 268, 275, 288, 297, 301, 305)
# The schema 6 views of every snapshot, and the historical slots.
VIEWS = audit.CURRENT_VIEWS + (
    "integrator", "speed_error", "torque_fraction", "cut_requests",
)


def inputs(speed, button=model.BUTTON_CANCEL, active_index=0, rpm=RPM):
    return model.Inputs(
        button=button,
        active_index=active_index,
        speed=speed,
        rpm_native=rpm,
        pedal=100,
        coolant=120,
        hcan1_state=model.HCAN1_INITIALIZED_MASK,
        port_input_state=model.PL4_READY_MASK,
        speed_wire_word=speed * 10,
    )


def simulate(
    speeds, *, rpms=None, idle_before=2, released_after=6,
    calibration=MODEL_CALIBRATION, table=TABLE, active_index=0,
    stock_command=90,
):
    """Snapshots of the model with the spark actuator and the ignition
    adapter between ticks.

    The events of the interval before a snapshot see the state of the
    previous tick, and their count follows the engine speed of the tick.
    """
    rpms = rpms or (RPM,) * len(speeds)
    state = model.RuntimeState()
    cut = model.SparkCutState(accumulators=model.SPARK_CYLINDER_OFFSETS)
    schedule = (
        [inputs(speeds[0], model.BUTTON_RELEASED, active_index, rpms[0])]
        * idle_before
        + [
            inputs(speed, active_index=active_index, rpm=rpm)
            for speed, rpm in zip(speeds, rpms)
        ]
        + [inputs(speeds[-1], model.BUTTON_RELEASED, active_index, rpms[-1])]
        * released_after
    )
    samples = []
    pending = 0.0
    cylinder = 0
    for tick, step_inputs in enumerate(schedule):
        pending += step_inputs.rpm_native * audit.EVENTS_PER_COUNT_TICK
        while pending >= 1:
            pending -= 1
            event = model.SparkEvent(cylinder=cylinder % 6 + 1)
            cut = model.spark_event(state, cut, event).state
            cylinder += 1
        state = model.ignition_step(state, stock_command, calibration, table)
        state = model.step(state, step_inputs, calibration, table).state
        samples.append(sample(tick, step_inputs, state, cut))
    return samples


def sample(tick, step_inputs, state, cut):
    rpm = step_inputs.rpm_native
    return audit.Sample(
        tick=tick,
        button=None,
        dashboard=None,
        speed_kmh=step_inputs.speed / 10,
        coolant_raw=None,
        rpm_raw=rpm,
        rpm_low=rpm - audit.STOCK_RPM_MARGIN,
        rpm_high=rpm + audit.STOCK_RPM_MARGIN,
        fuel_inhibit_mask=0,
        final_timing_raw=20,
        app1_raw=600,
        bfs_raw=1000,
        knock_surface_state=0,
        exhaust_cvtc_target_raw=0,
        phase=int(state.phase),
        abort_reason=int(state.abort_reason),
        integrator=state.integrator,
        speed_error=state.speed_error,
        torque_fraction=state.torque_fraction,
        cut_requests=cut.cut_count,
        control_error=state.control_error,
        law_output=state.law_output,
        mode_trim=state.wire_mode_trim,
        consumed_q_sum=cut.consumed_q_sum,
        cut_fraction=state.cut_fraction,
        efficiency=state.wire_efficiency,
        speed_sample=state.speed_sample,
        selected_target=state.selected_target,
        status=state.wire_status,
        rpm_sample=state.rpm_sample_native,
        stock_command=state.stock_command,
        effective_command=state.effective_command,
        accepted_button=state.accepted_button,
        speed_age=state.speed_age,
        map_index=step_inputs.active_index,
    )


def configure(samples, *groups, offset=0):
    """The snapshots of a configuration whose groups alternate per tick:
    each group is its configuration byte and the views it carries."""
    result = []
    for s in samples:
        selector, names = groups[(s.tick + offset) % len(groups)]
        result.append(replace(
            s, configuration=selector,
            **{name: None for name in VIEWS if name not in names},
        ))
    return result


LAUNCH_LAW = ((1, {"speed_error", "torque_fraction", "cut_requests"}),)
LAUNCH_LAW_INTEGRATOR = (
    (2, {"speed_error", "torque_fraction", "cut_requests"}),
    (0x82, {"integrator", "cut_requests"}),
)
RL6_LAW = ((3, {"control_error", "law_output", "cut_requests", "mode_trim"}),)
RL6_ACTUATION = (
    (4, {"consumed_q_sum", "cut_requests", "mode_trim"}),
    (0x84, {"cut_fraction", "law_output", "efficiency"}),
)
RL6_INPUTS = (
    (5, {"speed_sample", "selected_target", "status"}),
    (0x85, {"rpm_sample", "stock_command", "effective_command",
            "accepted_button", "speed_age"}),
)
RL6_RELEASE = (
    (6, {"cut_fraction", "cut_requests", "accepted_button", "status", "speed_age"}),
)


def launch_law(samples):
    """The snapshots of configuration 1, which lacks the integrator."""
    return configure(samples, *LAUNCH_LAW)


def launch_law_integrator(samples, offset=0):
    """The snapshots of configuration 2, whose groups alternate per tick:
    group 0 carries the error and the fraction, group 1 the integrator, and
    both the cut counter."""
    return configure(samples, *LAUNCH_LAW_INTEGRATOR, offset=offset)


def failed_ticks(run):
    return {tick for tick, _failure in run.failures}


class HoldAuditTest(unittest.TestCase):
    """The speed hold of a historical endpoint."""

    def test_a_model_run_passes_every_law(self):
        samples = simulate(SPEEDS)
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertEqual(run.start_tick, 2)
        self.assertEqual(run.end_tick, 2 + len(SPEEDS) - 1)
        self.assertEqual(run.law_ticks, len(SPEEDS))
        self.assertEqual(run.failures, ())
        self.assertEqual(run.abort_reason, model.AbortReason.BUTTON_RELEASED)
        self.assertEqual(run.target_speed, (500.0, 500.0))
        self.assertGreater(run.requested_cuts, 0)
        self.assertTrue(run.requested_cuts_inside)

    def test_the_one_group_configuration_replays_every_step(self):
        samples = launch_law(simulate(SPEEDS))
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertEqual(run.law_ticks, len(SPEEDS))
        self.assertEqual(run.failures, ())
        self.assertTrue(run.requested_cuts_inside)

    def test_the_one_group_configuration_catches_a_fraction_off_the_model(self):
        samples = launch_law(simulate(SPEEDS))
        index = 9
        samples[index] = replace(
            samples[index], torque_fraction=samples[index].torque_fraction - 1
        )
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertIn(samples[index].tick, failed_ticks(run))

    def test_the_two_group_configuration_bounds_two_tick_steps(self):
        for offset in (0, 1):
            with self.subTest(offset=offset):
                samples = launch_law_integrator(simulate(SPEEDS), offset)
                (run,) = audit.audit_hold(samples, HISTORICAL)
                self.assertEqual(run.law_ticks, len(SPEEDS) // 2)
                self.assertEqual(run.failures, ())
                self.assertEqual(run.target_speed, (500.0, 500.0))
                self.assertTrue(run.requested_cuts_inside)

    def test_the_two_group_configuration_catches_a_fraction_off_the_model(self):
        samples = launch_law_integrator(simulate(SPEEDS))
        index = 6
        self.assertIsNotNone(samples[index].torque_fraction)
        samples[index] = replace(
            samples[index],
            torque_fraction=samples[index].torque_fraction
            + 3 * HISTORICAL.u_rate_limit,
        )
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertIn(samples[index].tick, failed_ticks(run))

    def test_the_configuration_byte_selects_the_current_slots(self):
        page = audit.DynamicPage.of(can_telemetry.load_schema()[1]["tuning"])
        self.assertEqual(page.field, "telemetry_page_configuration")
        values = {
            name: 7 for name in (*audit.TELEMETRY_SOURCES, *audit.HOLD_SOURCES)
        }
        expected = {
            0: set(),
            1: {"speed_error", "torque_fraction", "cut_requests"},
            2: {"speed_error", "torque_fraction", "cut_requests"},
            0x82: {"integrator", "cut_requests"},
            3: RL6_LAW[0][1],
            4: RL6_ACTUATION[0][1],
            0x84: RL6_ACTUATION[1][1],
            5: RL6_INPUTS[0][1],
            0x85: RL6_INPUTS[1][1],
            6: RL6_RELEASE[0][1],
        }
        for selector, carried in expected.items():
            with self.subTest(configuration=selector):
                values[page.field] = selector
                sample = audit._sample(0, lambda name: values.get(name), RPM, page)
                self.assertEqual(sample.configuration, selector)
                self.assertEqual(sample.phase, 7)
                self.assertEqual(
                    {name for name in VIEWS if getattr(sample, name) is not None},
                    carried,
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
        (run,) = audit.audit_hold(samples, HISTORICAL)
        # The next step starts from the published fraction, so the rate limit
        # may hold it; the changed tick fails in every case.
        self.assertIn(samples[index].tick, failed_ticks(run))

    def test_an_integrator_off_the_model_fails(self):
        samples = simulate(SPEEDS)
        index = 8
        samples[index] = replace(
            samples[index], integrator=samples[index].integrator - 16
        )
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertIn(
            (samples[index].tick, f"integrator {samples[index].integrator}, "
             f"model {samples[index].integrator + 16}"),
            run.failures,
        )

    def test_an_error_outside_the_window_fails(self):
        samples = simulate(SPEEDS)
        index = 5
        samples[index] = replace(
            samples[index], speed_error=HISTORICAL.abort_above + 1
        )
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertIn(
            (samples[index].tick, "speed error outside the abort window"),
            run.failures,
        )

    def test_missing_cuts_fall_below_the_owed_bound(self):
        samples = simulate(SPEEDS)
        frozen = samples[2].cut_requests
        samples = [
            replace(s, cut_requests=frozen) if s.tick >= 2 else s for s in samples
        ]
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertEqual(run.requested_cuts, 0)
        self.assertFalse(run.requested_cuts_inside)

    def test_extra_cuts_exceed_the_owed_bound(self):
        samples = simulate(SPEEDS)
        end = 2 + len(SPEEDS)
        samples = [
            replace(s, cut_requests=(s.cut_requests + 8) & 0xFF) if s.tick >= end else s
            for s in samples
        ]
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertFalse(run.requested_cuts_inside)

    def test_a_gap_skips_the_step_and_the_cut_bound(self):
        samples = simulate(SPEEDS)
        del samples[7]
        first, second = audit.audit_hold(samples, HISTORICAL)
        self.assertEqual(first.failures + second.failures, ())
        # Ticks 2..6 and 8..15; tick 8 lacks its predecessor.
        self.assertEqual(first.law_ticks, 5)
        self.assertEqual(second.law_ticks, len(SPEEDS) - 7)
        self.assertIsNone(first.requested_cuts)
        self.assertIsNone(first.abort_reason)
        self.assertIsNone(second.requested_cuts)

    def test_observe_mode_has_no_cut_bound(self):
        samples = simulate(SPEEDS)
        (run,) = audit.audit_hold(samples, replace(HISTORICAL, hold=False))
        self.assertIsNone(run.requested_cuts)
        self.assertIsNone(run.requested_cuts_inside)

    def test_a_capture_without_the_hold_fields_is_refused(self):
        samples = [
            replace(s, integrator=None, speed_error=None)
            for s in simulate(SPEEDS)
        ]
        with self.assertRaisesRegex(ValueError, "hold fields"):
            audit.audit_hold(samples, HISTORICAL)
        samples = [replace(s, phase=None) for s in samples]
        with self.assertRaisesRegex(ValueError, "no Rolling Launch phase"):
            audit.audit_hold(samples, HISTORICAL)

    def test_a_capture_with_a_tick_divisor_is_refused(self):
        samples = [replace(s, tick=2 * s.tick) for s in simulate(SPEEDS)]
        with self.assertRaisesRegex(ValueError, "step by 2 ticks"):
            audit.audit_hold(samples, HISTORICAL)

    def test_a_run_without_its_idle_predecessor_checks_no_fraction(self):
        samples = launch_law(simulate(SPEEDS))[2:]
        (run,) = audit.audit_hold(samples, HISTORICAL)
        self.assertEqual(run.law_ticks, 0)
        self.assertEqual(run.failures, ())

    def test_an_audit_that_checks_nothing_fails(self):
        cases = {
            "model run": (simulate(SPEEDS), HISTORICAL, 0),
            "no fraction checked": (launch_law(simulate(SPEEDS))[2:], HISTORICAL, 1),
            "no ACTIVE run": (simulate(SPEEDS)[:2], HISTORICAL, 1),
            "current runtime": (configure(simulate(SPEEDS), *RL6_LAW), CALIBRATION, 0),
        }
        for name, (samples, calibration, status) in cases.items():
            with self.subTest(name):
                capture = audit.Capture(Path("hold.mlg"), "0" * 64, tuple(samples))
                with (
                    mock.patch.object(
                        audit, "read_calibration", return_value=calibration
                    ),
                    mock.patch.object(audit, "read_capture", return_value=capture),
                    contextlib.redirect_stdout(io.StringIO()),
                ):
                    self.assertEqual(
                        audit.main(["--image", "image.bin", "hold.mlg"]), status
                    )

    def test_the_run_uses_the_slot_of_the_selected_map(self):
        trimmed = model.Slot(integral_gain=2, max_trim_speed=20, floor_command=120)
        model_calibration = replace(
            MODEL_CALIBRATION,
            enable_mask=0x08,
            slots=(SLOT,) * 3 + (trimmed, SLOT),
        )
        calibration = historical_calibration(model_calibration, slots=(
            (audit.HoldSlot(3),) * 3
            + (audit.HoldSlot(2, 20, 120, 824), audit.HoldSlot(3))
        ))
        samples = simulate(
            SPEEDS, calibration=model_calibration, table=TRIM_TABLE,
            active_index=3,
        )
        (run,) = audit.audit_hold(samples, calibration)
        self.assertEqual(run.failures, ())
        self.assertGreater(run.law_ticks, 0)
        self.assertTrue(run.requested_cuts_inside)
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
        calibration = historical_calibration(
            slots=(audit.HoldSlot(3, 20, 120, 824),) * model.SLOT_COUNT
        )
        samples = simulate(SPEEDS)
        active = sum(s.phase == model.Phase.ACTIVE for s in samples)
        # A final timing of 5 is the stock command 105, past the floor of
        # 120 by 5 with the trim of 20.
        clipped = [replace(s, final_timing_raw=5) for s in samples]
        (run,) = audit.audit_hold(clipped, calibration)
        self.assertEqual(run.floor_ticks, active)
        # A stock command whose full trim reaches the floor is not clipped.
        (run,) = audit.audit_hold(
            [replace(s, final_timing_raw=10) for s in samples], calibration
        )
        self.assertEqual(run.floor_ticks, 0)

    def test_the_stock_command_follows_the_final_timing(self):
        self.assertEqual(audit.stock_apc_command(20), 90)
        self.assertEqual(audit.stock_apc_command(0), 110)
        # A final timing past the base wraps modulo 256, as the command byte.
        self.assertEqual(audit.stock_apc_command(120), 246)

    def test_the_owed_cuts_follow_the_trim_efficiency(self):
        samples = simulate(SPEEDS)
        (stock,) = audit.audit_hold(samples, HISTORICAL)
        trimmed = historical_calibration(
            slots=(audit.HoldSlot(3, 20, 120, 824),) * model.SLOT_COUNT
        )
        (run,) = audit.audit_hold(samples, trimmed)
        self.assertLess(run.owed[1], stock.owed[1])

    def test_cut_bounds_follow_the_accumulator_offsets(self):
        self.assertAlmostEqual(audit.CUTS_BELOW, 2.75 - 6 - 1)
        self.assertAlmostEqual(audit.CUTS_ABOVE, 2.75 + 1)
        self.assertAlmostEqual(audit.EVENTS_PER_COUNT_TICK, 0.0064)


TRIM_SLOT = model.Slot(integral_gain=3, max_trim_speed=20, floor_command=120)
TRIM_CALIBRATION = replace(MODEL_CALIBRATION, slots=(TRIM_SLOT,) * model.SLOT_COUNT)


def speed_run(**options):
    """Snapshots of a speed-regulator run with the trim of 20 degrees."""
    return simulate(SPEEDS, calibration=TRIM_CALIBRATION, table=TRIM_TABLE, **options)


def rpm_run(**options):
    """Snapshots of a standing RPM-regulator run."""
    return simulate(
        (0,) * len(RPMS), rpms=RPMS, calibration=RPM_CALIBRATION, **options
    )


SPEED_SETTINGS = current_calibration(TRIM_CALIBRATION, TRIM_TABLE)
RPM_SETTINGS = current_calibration(RPM_CALIBRATION)
KINDS = {
    "SPEED": (speed_run, SPEED_SETTINGS, model.RegulatorKind.SPEED),
    "RPM": (rpm_run, RPM_SETTINGS, model.RegulatorKind.RPM),
}


def changed(samples, index, **values):
    samples = list(samples)
    samples[index] = replace(samples[index], **values)
    return samples


class CurrentRunTest(unittest.TestCase):
    """The schema 6 views of the current runtime."""

    def test_the_packed_views_follow_the_model(self):
        state = next(
            model.decode_state(*model.encode_state(
                replace(model.RuntimeState(), **{
                    "phase": model.Phase.ACTIVE,
                    "active_mode_snapshot": model.Mode.HOLD,
                    "regulator_kind": model.RegulatorKind.SPEED,
                    "run_ticks": 3, "target_speed": 500, "selected_target": 500,
                    "law_output": 700, "torque_fraction": 700,
                    "applied_trim": 20, "active_max_trim": 20,
                    "stock_command": 90, "effective_command": 110,
                    "applied_efficiency": 824, "actuation_ready": True,
                    "cut_fraction": model.cut_fraction(700, 824),
                    "input_status": 7, "accepted_button": model.BUTTON_CANCEL,
                }),
                model.SparkCutState(),
            ))
            for _ in (0,)
        )[0]
        self.assertEqual(state.wire_mode_trim & audit.MODE_TRIM_VALUE_MASK, 20)
        self.assertTrue(state.wire_mode_trim >> audit.MODE_TRIM_SPEED_BIT & 1)
        self.assertTrue(state.wire_mode_trim >> audit.MODE_TRIM_READY_BIT & 1)
        self.assertEqual(state.wire_efficiency & audit.EFFICIENCY_VALUE_MASK, 824)
        self.assertTrue(state.wire_efficiency >> audit.EFFICIENCY_SPEED_BIT & 1)
        self.assertTrue(state.wire_efficiency >> audit.EFFICIENCY_READY_BIT & 1)
        self.assertEqual(state.wire_status & audit.STATUS_KIND_MASK, model.RegulatorKind.SPEED)
        self.assertEqual(state.wire_status & audit.STATUS_INPUTS_MASK, audit.STATUS_INPUTS_MASK)
        self.assertEqual(
            state.wire_status & audit.STATUS_BUTTON_MASK, 1 << audit.STATUS_CANCEL_BIT
        )
        self.assertTrue(state.wire_status >> audit.STATUS_READY_BIT & 1)
        released = replace(state, accepted_button=model.BUTTON_RELEASED)
        self.assertEqual(
            released.wire_status & audit.STATUS_BUTTON_MASK, 1 << audit.STATUS_RELEASED_BIT
        )

    def test_the_regulator_configuration_replays_both_kinds(self):
        for name, (simulation, settings, kind) in KINDS.items():
            with self.subTest(name):
                samples = configure(simulation(), *RL6_LAW)
                (run,) = audit.audit_hold(samples, settings)
                self.assertEqual(run.kind, kind)
                self.assertEqual(run.failures, ())
                self.assertEqual(run.law_ticks, run.end_tick - run.start_tick + 1)
                self.assertEqual(run.abort_reason, model.AbortReason.BUTTON_RELEASED)
                self.assertEqual(run.floor_ticks, 0)
                if kind == model.RegulatorKind.SPEED:
                    self.assertEqual(run.target_speed, (500.0, 500.0))
                else:
                    self.assertIsNone(run.target_speed)

    def test_an_output_off_the_model_fails_in_both_kinds(self):
        for name, (simulation, settings, _kind) in KINDS.items():
            with self.subTest(name):
                samples = configure(simulation(), *RL6_LAW)
                index = 7
                samples = changed(
                    samples, index, law_output=(samples[index].law_output + 7) % 1000
                )
                (run,) = audit.audit_hold(samples, settings)
                self.assertIn(samples[index].tick, failed_ticks(run))

    def test_an_rpm_error_off_the_stock_engine_speed_fails(self):
        samples = configure(rpm_run(), *RL6_LAW)
        index = 6
        samples = changed(samples, index, rpm_low=400, rpm_high=410)
        (run,) = audit.audit_hold(samples, RPM_SETTINGS)
        self.assertIn(samples[index].tick, failed_ticks(run))

    def test_a_speed_run_without_its_idle_predecessor_checks_no_output(self):
        samples = configure(speed_run(), *RL6_LAW)[2:]
        (run,) = audit.audit_hold(samples, SPEED_SETTINGS)
        self.assertEqual(run.law_ticks, 0)
        self.assertEqual(run.failures, ())

    def test_a_trim_above_the_trim_of_the_regulator_fails(self):
        samples = configure(speed_run(), *RL6_LAW)
        index = 6
        samples = changed(samples, index, mode_trim=samples[index].mode_trim + 1)
        (run,) = audit.audit_hold(samples, SPEED_SETTINGS)
        self.assertIn(samples[index].tick, failed_ticks(run))

    def test_the_actuation_configuration_checks_q_and_the_consumed_q_sum(self):
        for name, (simulation, settings, _kind) in KINDS.items():
            for offset in (0, 1):
                with self.subTest(name, offset=offset):
                    samples = configure(simulation(), *RL6_ACTUATION, offset=offset)
                    (run,) = audit.audit_hold(samples, settings)
                    self.assertEqual(run.failures, ())
                    self.assertGreater(run.actuation_ticks, 0)
                    self.assertGreater(run.requested_cuts, 0)
                    self.assertTrue(run.requested_cuts_inside)

    def test_a_published_q_off_the_output_and_efficiency_fails(self):
        for name, (simulation, settings, _kind) in KINDS.items():
            with self.subTest(name):
                samples = configure(simulation(), *RL6_ACTUATION)
                index = next(
                    i for i, s in enumerate(samples)
                    if s.phase == model.Phase.ACTIVE and s.cut_fraction
                )
                samples = changed(samples, index, cut_fraction=samples[index].cut_fraction - 1)
                (run,) = audit.audit_hold(samples, settings)
                self.assertIn(samples[index].tick, failed_ticks(run))

    def test_cut_requests_off_the_consumed_q_sum_fail(self):
        samples = configure(speed_run(), *RL6_ACTUATION)
        frozen = samples[2].cut_requests
        missing = [
            replace(s, cut_requests=frozen)
            if s.tick >= 2 and s.cut_requests is not None else s
            for s in samples
        ]
        (run,) = audit.audit_hold(missing, SPEED_SETTINGS)
        self.assertEqual(run.requested_cuts, 0)
        self.assertFalse(run.requested_cuts_inside)
        # Between two snapshots the requests stay within six of the owed cuts.
        index = next(
            i for i, s in enumerate(samples)
            if s.phase == model.Phase.ACTIVE and s.consumed_q_sum is not None and i > 6
        )
        jump = changed(samples, index, cut_requests=(samples[index].cut_requests + 7) & 0xFF)
        (run,) = audit.audit_hold(jump, SPEED_SETTINGS)
        self.assertIn(samples[index].tick, failed_ticks(run))
        end = 2 + len(SPEEDS)
        extra = [
            replace(s, cut_requests=(s.cut_requests + 8) & 0xFF)
            if s.tick >= end and s.cut_requests is not None else s
            for s in samples
        ]
        (run,) = audit.audit_hold(extra, SPEED_SETTINGS)
        self.assertFalse(run.requested_cuts_inside)

    def test_a_gap_leaves_the_consumed_q_bound_open(self):
        samples = configure(speed_run(), *RL6_ACTUATION)
        del samples[7]
        runs = audit.audit_hold(samples, SPEED_SETTINGS)
        self.assertTrue(all(run.requested_cuts is None for run in runs))

    def test_the_inputs_configuration_checks_sources_targets_and_command(self):
        for name, (simulation, settings, _kind) in KINDS.items():
            with self.subTest(name):
                samples = configure(simulation(), *RL6_INPUTS)
                (run,) = audit.audit_hold(samples, settings)
                self.assertEqual(run.failures, ())
                self.assertEqual(run.input_ticks, run.end_tick - run.start_tick + 1)
        samples = configure(speed_run(), *RL6_INPUTS, offset=1)
        group0 = next(
            i for i, s in enumerate(samples)
            if s.phase == model.Phase.ACTIVE and s.status is not None and i > 4
        )
        group1 = group0 + 1
        cases = {
            "effective command": changed(
                samples, group1,
                effective_command=samples[group1].effective_command + 1,
            ),
            "RPM sample": changed(
                samples, group1, rpm_sample=samples[group1].rpm_sample + 40
            ),
            "target": changed(
                samples, group0,
                selected_target=samples[group0].selected_target + 1,
            ),
            "speed inputs": changed(
                samples, group0,
                status=samples[group0].status & ~audit.STATUS_INPUTS_MASK,
            ),
            "speed frame age": changed(
                samples, group1, speed_age=MODEL_CALIBRATION.speed_frame_age_limit + 1
            ),
            "accepted button": changed(samples, group1, accepted_button=model.BUTTON_SET),
        }
        for name, changed_samples in cases.items():
            with self.subTest(name):
                (run,) = audit.audit_hold(changed_samples, SPEED_SETTINGS)
                self.assertNotEqual(run.failures, ())

    def test_the_release_configuration_checks_the_accepted_release(self):
        for name, (simulation, settings, _kind) in KINDS.items():
            with self.subTest(name):
                samples = configure(simulation(), *RL6_RELEASE)
                (run,) = audit.audit_hold(samples, settings)
                self.assertEqual(run.failures, ())
                self.assertEqual(run.release_cuts, 0)
                self.assertGreater(run.input_ticks, 0)
        samples = configure(speed_run(), *RL6_RELEASE)
        release = 2 + len(SPEEDS)
        late = [
            replace(s, cut_requests=(s.cut_requests + 1) & 0xFF)
            if s.tick > release else s
            for s in samples
        ]
        (run,) = audit.audit_hold(late, SPEED_SETTINGS)
        self.assertEqual(run.release_cuts, 1)
        self.assertIn(release, failed_ticks(run))
        (run,) = audit.audit_hold(changed(samples, release, cut_fraction=5), SPEED_SETTINGS)
        self.assertIn(release, failed_ticks(run))

    def test_a_q_without_an_applied_command_fails(self):
        samples = configure(speed_run(), *RL6_RELEASE)
        index = next(
            i for i, s in enumerate(samples)
            if s.phase == model.Phase.ACTIVE and s.cut_fraction
        )
        status = samples[index].status & ~(1 << audit.STATUS_READY_BIT)
        (run,) = audit.audit_hold(changed(samples, index, status=status), SPEED_SETTINGS)
        self.assertIn(samples[index].tick, failed_ticks(run))

    def test_a_current_run_without_its_views_is_refused(self):
        samples = launch_law(speed_run())
        with self.assertRaisesRegex(ValueError, "hold fields"):
            audit.audit_hold(samples, SPEED_SETTINGS)


# The endpoints of the flashed hold images: one integral gain for every map,
# and per-map slots with the fixed ignition trim.
FLASHED_ENDPOINTS = ("schema-4-uniform-gain", "schema-5-fixed-trim")


def endpoint_record(key, slots=None, **head):
    """The fixture record of a flashed endpoint with changed head fields
    and, by slot index, changed map slots."""
    schema = runtime_endpoints.historical_endpoint(key).configuration_schema_version
    layout = runtime_endpoints.SPEED_HOLD_SCHEMA_FORMATS[schema]
    values = list(struct.unpack(layout, endpoint_images.record(key)))
    for name, value in head.items():
        values[runtime_endpoints.SPEED_HOLD_HEAD_FIELDS.index(name)] = value
    width = len(runtime_endpoints.SPEED_HOLD_SLOT_FIELDS)
    for index, slot in (slots or {}).items():
        start = len(runtime_endpoints.SPEED_HOLD_HEAD_FIELDS) + width * index
        values[start : start + width] = slot
    return struct.pack(layout, *values)


@lru_cache(maxsize=None)
def endpoint_image(key):
    """The current JK08A build with a flashed endpoint in place of the
    current Rolling Launch layer."""
    target = runtime_targets.load_runtime_target("JK08A")
    built = build_rom.build_image(
        target.stock_image.data, source_name="JK08A stock"
    ).data
    source = endpoint_images.with_endpoint(
        target, built, key, endpoint_images.record(key)
    )
    return bytes(
        rom_checksums.recalculate(bytearray(source), target.checksum_layout)
    )


class EndpointCalibrationTest(unittest.TestCase):
    def test_the_current_record_holds_its_slots_and_table(self):
        calibration = current_calibration(TRIM_CALIBRATION, TRIM_TABLE)
        self.assertEqual(calibration.endpoint, "current")
        self.assertEqual(calibration.schema, model.CONFIG_SCHEMA_VERSION)
        self.assertTrue(calibration.hold)
        self.assertEqual(calibration.slots, TRIM_CALIBRATION.slots)
        self.assertEqual(calibration.table, TRIM_TABLE)
        self.assertEqual(
            calibration.speed_frame_age_limit, TRIM_CALIBRATION.speed_frame_age_limit
        )

    def test_a_uniform_gain_record_holds_its_gain_in_every_map(self):
        key = "schema-4-uniform-gain"
        record = endpoint_record(key, mode=1, gain_word=3)
        calibration = audit.endpoint_calibration(record, key)
        fields = runtime_endpoints.historical_configuration_fields(record, 4)
        self.assertEqual(calibration.endpoint, key)
        self.assertTrue(calibration.hold)
        self.assertEqual(
            calibration.slots,
            (audit.HoldSlot(integral_gain=3),)
            * runtime_endpoints.SPEED_HOLD_SLOT_COUNT,
        )
        for name in (
            "window_top", "window_width", "u_rate_limit", "integrator_limit",
            "abort_above", "abort_below",
        ):
            self.assertEqual(getattr(calibration, name), fields[name], name)

    def test_a_fixed_trim_record_keeps_the_trim_of_each_map(self):
        key = "schema-5-fixed-trim"
        record = endpoint_record(key, slots={3: (2, 20, 120, 824)})
        calibration = audit.endpoint_calibration(record, key)
        self.assertFalse(calibration.hold)
        self.assertEqual(calibration.slot(3), audit.HoldSlot(2, 20, 120, 824))
        fixture = audit.endpoint_calibration(endpoint_images.record(key), key)
        for index in (0, 1, 2, 4):
            self.assertEqual(calibration.slot(index), fixture.slot(index))

    def test_a_record_off_its_contract_is_refused(self):
        for key in FLASHED_ENDPOINTS:
            with self.subTest(key):
                record = endpoint_record(key, magic=0)
                with self.assertRaisesRegex(ValueError, "no valid schema"):
                    audit.endpoint_calibration(record, key)
        with self.assertRaisesRegex(ValueError, "record is invalid"):
            audit.endpoint_calibration(b"\xff" * model.CONFIG_SIZE, "current")
        with self.assertRaisesRegex(ValueError, "efficiency table is invalid"):
            audit.endpoint_calibration(
                MODEL_CALIBRATION.to_bytes(), "current", b"\xff" * model.EFFICIENCY_TABLE_SIZE
            )
        earlier = next(
            endpoint for endpoint in runtime_endpoints.HISTORICAL_ROLLING_ENDPOINTS
            if endpoint.configuration_schema_version
            not in runtime_endpoints.SPEED_HOLD_SCHEMA_FORMATS
        )
        with self.assertRaisesRegex(ValueError, "has no speed hold"):
            audit.endpoint_calibration(b"", earlier.key)

    def test_a_flashed_image_reads_the_record_of_its_endpoint(self):
        target = runtime_targets.load_runtime_target("JK08A")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "image.bin"
            for key in FLASHED_ENDPOINTS:
                with self.subTest(key):
                    image = endpoint_image(key)
                    path.write_bytes(image)
                    calibration = audit.read_calibration(path)
                    state = runtime_endpoints.classify_runtime(
                        image, target, key
                    ).rolling
                    # A current runtime that composes the endpoint classifies
                    # as current and reads the same settings.
                    self.assertIn(state, (key, "current"))
                    self.assertEqual(calibration.endpoint, state)
                    self.assertEqual(
                        replace(calibration, endpoint=key),
                        audit.endpoint_calibration(
                            endpoint_images.record(key), key
                        ),
                    )
            path.write_bytes(target.stock_image.data)
            with self.assertRaisesRegex(ValueError, "no Rolling Launch runtime"):
                audit.read_calibration(path)


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
        cut = row["cut_request_release"]
        self.assertEqual(cut["ecu_release_inferred_ms_bounds"], [150, 160])
        self.assertEqual(cut["requested_cuts_after_phase_exit_snapshot"], 0)
        self.assertLessEqual(cut["last_cut_request_after_ecu_release_upper_cycles"], 1)

    def test_pedal_abort_precedes_acceptance_of_the_stable_release(self):
        capture = self.capture()
        (run,) = audit.audit_hold(capture.samples, CALIBRATION)
        run = replace(run, abort_reason=model.AbortReason.PEDAL_LOW)
        (row,) = audit.audit_bus(capture, (run,))["holds"]
        cut = row["cut_request_release"]
        self.assertNotIn("ecu_release_inferred_ms_bounds", cut)
        self.assertEqual(cut["ecu_release_inferred_not_before_ms"], 160)
        self.assertEqual(cut["last_cut_request_after_ecu_release_upper_cycles"], 0)

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


class ReleaseCutTimingTest(unittest.TestCase):
    def capture(self, *, late_cut=False, next_hold=False):
        base = simulate(SPEEDS)[:12]
        counters = [250, 251, 252, 254, 255, 0, 2, 2, 2, 2, 2, 2]
        if late_cut:
            counters[8:] = [3] * 4
        samples = tuple(replace(
            s, phase=1 if 1 <= i < 6 or next_hold and i >= 10 else 2,
            button=2 if i < 3 else 32, cut_requests=counters[i],
        ) for i, s in enumerate(base))
        return BusJoinTest.capture(samples)

    def result(self, capture, release=25):
        return audit.release_cut_request_timing(
            capture, 1, 6, release,
            audit._BusIndex(capture.timing.bus_frames[0x180]),
        )

    def test_transition_interval_counts_are_not_cuts_after_inactive_snapshot(self):
        result = self.result(self.capture())
        self.assertEqual(result["host_release_snapshot_first_page_ms"], 30)
        self.assertEqual(result["host_release_snapshot_ms"], 33)
        self.assertIsNone(result["ecu_release_snapshot_ms"])
        self.assertEqual(result["phase_exit_snapshot_ms"], 60)
        self.assertEqual(result["last_increment_snapshot_ms"], 60)
        self.assertEqual(result["phase_exit_counter_increment"], 2)
        self.assertEqual(result["requested_cuts_after_phase_exit_snapshot"], 0)
        # The counter wraps, and two cuts straddle the raw release frame.
        self.assertEqual(result["requested_cuts_after_release_bounds"], [4, 6])
        self.assertEqual(result["last_cut_request_offset_ms_bounds"], [25, 35])
        self.assertEqual(result["raw_release_one_cycle"], "straddles_one_cycle")

    def test_a_veto_after_the_inactive_snapshot_is_detected(self):
        result = self.result(self.capture(late_cut=True))
        self.assertEqual(result["requested_cuts_after_phase_exit_snapshot"], 1)
        self.assertEqual(result["last_increment_snapshot_ms"], 80)
        self.assertEqual(result["last_cut_request_cycles_bounds"], [1.5, 55 / 30])
        self.assertEqual(result["raw_release_one_cycle"], "beyond_snapshot_bound")

    def test_a_later_hold_is_outside_the_quiet_observation_window(self):
        capture = self.capture(next_hold=True)
        samples = list(capture.samples)
        samples[10] = replace(samples[10], cut_requests=7)
        result = self.result(replace(capture, samples=tuple(samples)))
        self.assertEqual(result["requested_cuts_after_phase_exit_snapshot"], 0)
        self.assertEqual(result["inactive_snapshots_checked"], 3)

    def test_missing_counter_coverage_does_not_pass_the_release_bound(self):
        capture = self.capture()
        samples = list(capture.samples)
        samples[7] = replace(samples[7], cut_requests=None)
        result = self.result(replace(capture, samples=tuple(samples)))
        self.assertFalse(result["counter_window_complete"])
        self.assertIsNone(result["requested_cuts_after_phase_exit_snapshot"])
        self.assertIsNone(result["requested_cuts_after_release_bounds"])
        self.assertEqual(result["raw_release_one_cycle"], "unresolved_window")

    def test_the_last_cut_can_precede_the_raw_button_release(self):
        result = self.result(self.capture(), release=85)
        self.assertEqual(result["requested_cuts_after_release_bounds"], [0, 0])
        self.assertEqual(result["last_cut_request_offset_ms_bounds"], [-35, -25])
        self.assertEqual(result["raw_release_one_cycle"], "within_snapshot_bound")

    def test_a_stream_pause_does_not_form_continuous_counter_coverage(self):
        capture = self.capture()
        times = tuple(t + (100 if i >= 7 else 0)
                      for i, t in enumerate(capture.timing.first_page_ms))
        capture = replace(capture, timing=replace(capture.timing, first_page_ms=times))
        result = self.result(capture)
        self.assertFalse(result["counter_window_complete"])
        self.assertIsNone(result["requested_cuts_after_phase_exit_snapshot"])


if __name__ == "__main__":
    unittest.main()
