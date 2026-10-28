from pathlib import Path
import re
import tomllib
import unittest

import pytest

from patches import rolling_launch
from patches import rolling_launch_layout
from tools.can_dashboard import model


ROOT = Path(__file__).resolve().parents[2]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
ENGINE_SOURCE = ROOT / "patches" / "rolling-launch-engine.s"
LOGS = ROOT / "tmp" / "logs-09-22"
IMAGE = ROOT / "tmp" / "1JK08A-tune-v3-1.bin"
KEY = "rolling_launch.map_2_vehicle_2026_09_22"
MAP_3_KEY = "rolling_launch.map_3_vehicle_2026_09_21"
SESSION_KEY = "can_telemetry.schema2_profile5_drive_2026_09_22"
# Frame 0x551 leaves the serializer on every tenth 10.24 ms invocation.
SERIALIZER_CALLS_PER_FRAME = 10
RPM_PER_NATIVE = model.RPM_PER_COUNT
NEUTRAL_EXHAUST_TARGET = 0x80
MAP_3_SLOT = 2
CONFIGURATION_FIELDS = (
    "configuration_address",
    "configuration_hex",
    "mode",
    "enabled_maps",
    "min_speed",
    "min_pedal",
    "min_rpm_native",
    "coolant_range",
    "rpm_offset_native",
    "min_hysteresis_native",
    "max_hysteresis_native",
    "hysteresis_ratio_tenths",
    "retard_ramp_native",
    "run_timeout_ticks",
    "rearm_ticks",
    "target_command",
)
PER_ACTIVATION = (
    "activation_start_seconds",
    "activation_hold_seconds",
    "activation_active_indication_seconds",
    "activation_speed_range_kmh",
    "activation_app1_range_v",
    "activation_rpm_range",
    "activation_captured_rpm_native",
    "activation_captured_rpm",
    "activation_cut_rpm",
    "activation_restore_rpm",
    "activation_capture_records",
    "activation_full_mask_cycles",
    "activation_post_release_full_mask_cycles",
    "activation_full_mask_rpm",
    "activation_apc_max",
    "activation_apc_target_records",
    "activation_apc_outside_bound_records",
    "activation_stock_command_range",
    "activation_identity_differences_hold",
    "activation_identity_differences_post_release",
    "activation_exit_records",
    "activation_active_ticks_bound",
    "activation_release_exit_bound_ms",
    "activation_release_full_mask",
    "activation_release_clear_bound_ms",
    "activation_release_clear_by_window_removal",
    "trace_activation_active_delay_ms",
    "trace_activation_inactive_frames_held",
    "trace_activation_release_clear_ms",
)
PER_HOLD = (
    "trace_hold_start_seconds",
    "trace_hold_seconds",
    "trace_hold_active_frames",
    "trace_hold_failed_frames",
)
# The record comes from the TRC, whose snapshots published the engine-speed
# coordinate 0xFFFF11F4 and whose frames carry their times. The recording
# converted from it takes engine speed from stock frame 0x180 and holds no
# frame times, so the figures that the coordinate or a frame time enters
# remain the record; the stock-frame bracket record test binds the recording
# to the engine-speed figures among them.
RECORD_ONLY = frozenset(
    {
        "exhaust_cvtc_slot_exact_counts",
        "activation_rpm_range",
        "activation_captured_rpm_native",
        "activation_captured_rpm",
        "activation_cut_rpm",
        "activation_restore_rpm",
        "activation_capture_records",
        "activation_full_mask_rpm",
        "activation_exit_records",
        "activation_active_ticks_bound",
        "activation_release_exit_bound_ms",
        "activation_release_clear_by_window_removal",
    }
)


def _entry(registry, dotted):
    section, name = dotted.split(".")
    return registry[section][name]


def _number(value):
    return f"{value:g}"


def _active_state(calibration, slot, captured):
    inputs = rolling_launch.Inputs(
        active_index=slot,
        button=rolling_launch.BUTTON_CANCEL,
        speed=calibration.min_speed,
        rpm_native=captured,
        pedal=calibration.min_pedal,
        coolant=calibration.coolant_min,
    )
    state = rolling_launch.step(
        rolling_launch.RuntimeState(), inputs, calibration
    ).state
    if state.phase != rolling_launch.Phase.ACTIVE:
        raise AssertionError(f"captured word {captured} does not activate")
    return state


class RollingLaunchMap2VehicleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        cls.result = _entry(cls.registry, KEY)
        cls.status = cls.result["term_status"]
        cls.reference = _entry(cls.registry, cls.result["reference"])
        cls.feedback = _entry(cls.registry, cls.result["feedback_record"])
        cls.session = _entry(cls.registry, SESSION_KEY)
        cls.map_3 = _entry(cls.registry, MAP_3_KEY)
        cls.layout = rolling_launch_layout.load_layout()
        cls.calibration = rolling_launch.Calibration.from_bytes(
            bytes.fromhex(cls.result["configuration_hex"])
        )
        cls.tick_ms = cls.layout.scheduler.tick_microseconds / 1000
        cls.selections = [
            index
            for maps in cls.feedback["selected_maps"].values()
            for index in maps
        ]
        # Trace holds are ordered in time: the held attempt on Map 1 comes
        # first, and each hold that activates shows the ACTIVE state.
        frames = cls.result["trace_hold_active_frames"]
        cls.activation_holds = [index for index, count in enumerate(frames) if count]

    def test_record_names_the_session_capture_and_image(self):
        result = self.result
        captures = {
            row["capture_name"]: row
            for row in _entry(self.registry, result["capture_registry"])
        }
        capture = captures[result["capture_name"]]
        self.assertEqual(capture["capture_sha256"], result["capture_sha256"])
        self.assertEqual(capture["converted_mlg_sha256"], result["converted_mlg_sha256"])
        self.assertEqual(
            capture["record_count"],
            result["snapshot_count"] + result["unverified_record_count"],
        )
        self.assertLessEqual(
            result["unverified_record_count"],
            self.session["record_count_total"] - self.session["identity_record_count"],
        )
        self.assertEqual(self.session["capture_registry"], result["capture_registry"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        self.assertEqual(result["observed_on"], self.session["recorded_on"])
        self.assertEqual(self.feedback["capture_name"], result["capture_name"])
        self.assertEqual(self.feedback["rolling_launch_record"], KEY)
        self.assertEqual(self.map_3["map_2_record"], KEY)
        self.assertTrue((ROOT / result["audit_tool"]).is_file())

    def test_configuration_is_the_record_of_the_map_3_drive(self):
        result = self.result
        self.assertEqual(result["image_sha256"], self.map_3["image_sha256"])
        for name in CONFIGURATION_FIELDS:
            with self.subTest(field=name):
                self.assertEqual(result[name], self.map_3[name])
        self.assertTrue(self.calibration.is_valid())
        self.assertIn(result["selected_map"], result["enabled_maps"])
        self.assertNotIn(self.feedback["held_attempt_map"], result["enabled_maps"])
        self.assertEqual(
            result["target_command"],
            self.calibration.target_commands[result["selected_map"] - 1],
        )

    def test_time_figures_follow_the_scheduler_tick(self):
        result = self.result
        tick_ms = self.tick_ms
        tick_s = tick_ms / 1000
        self.assertEqual(result["snapshot_period_ms"], tick_ms)
        self.assertEqual(
            result["dashboard_frame_period_ms"],
            round(SERIALIZER_CALLS_PER_FRAME * tick_ms, 3),
        )
        self.assertEqual(
            result["span_seconds"], round((result["snapshot_count"] - 1) * tick_s, 3)
        )
        self.assertEqual(
            result["timeout_seconds"], round(result["run_timeout_ticks"] * tick_s, 3)
        )
        self.assertEqual(result["rearm_seconds"], round(result["rearm_ticks"] * tick_s, 3))
        holds = result["activation_hold_seconds"]
        self.assertEqual(result["longest_hold_seconds"], max(holds))
        self.assertEqual(result["timeout_exercised"], max(holds) > result["timeout_seconds"])
        self.assertEqual(
            result["minimum_rearm_spacing_seconds"],
            min(result["activation_rearm_spacing_seconds"]),
        )
        for seconds in (
            *result["activation_start_seconds"],
            *holds,
            *result["activation_active_indication_seconds"],
            *result["activation_rearm_spacing_seconds"],
        ):
            with self.subTest(seconds=seconds):
                self.assertEqual(round(round(seconds / tick_s) * tick_s, 3), seconds)
        for bound in result["activation_release_clear_bound_ms"]:
            if not bound:
                continue
            first, last = (round(value / tick_ms) for value in bound)
            with self.subTest(bound=bound):
                self.assertEqual(last - first, 2)
        # The ACTIVE bound runs from the capture pass to the exit pass.
        for capture, exit_records, active in zip(
            result["activation_capture_records"],
            result["activation_exit_records"],
            result["activation_active_ticks_bound"],
            strict=True,
        ):
            if not exit_records:
                self.assertEqual(active, [])
                continue
            self.assertEqual(
                active, [exit_records[0] - capture[1], exit_records[1] - capture[0]]
            )

    def test_windows_follow_the_configuration_replay(self):
        result = self.result
        slot = result["selected_map"] - 1
        for index, (low, high) in enumerate(result["activation_captured_rpm_native"]):
            with self.subTest(activation=index + 1):
                states = [
                    _active_state(self.calibration, slot, captured)
                    for captured in range(low, high + 1)
                ]
                self.assertEqual(
                    result["activation_captured_rpm"][index],
                    [low * RPM_PER_NATIVE, high * RPM_PER_NATIVE],
                )
                self.assertEqual(
                    result["activation_cut_rpm"][index],
                    [
                        states[0].cut_rpm_native * RPM_PER_NATIVE,
                        states[-1].cut_rpm_native * RPM_PER_NATIVE,
                    ],
                )
                self.assertEqual(
                    result["activation_restore_rpm"][index],
                    [
                        min(state.restore_rpm_native for state in states) * RPM_PER_NATIVE,
                        max(state.restore_rpm_native for state in states) * RPM_PER_NATIVE,
                    ],
                )
                rpm_high = result["activation_rpm_range"][index][1]
                band = min(state.retard_band_start_native for state in states)
                if result["activation_full_mask_cycles"][index]:
                    self.assertGreaterEqual(rpm_high, result["activation_cut_rpm"][index][0])
                else:
                    # Below the retard band the controller keeps the stock command.
                    self.assertLess(rpm_high, band * RPM_PER_NATIVE)
                    self.assertEqual(result["activation_apc_target_records"][index], 0)
                    self.assertEqual(
                        result["activation_apc_max"][index],
                        result["activation_stock_command_range"][index][1],
                    )

    def test_counts_are_consistent_across_the_registry(self):
        result = self.result
        feedback = self.feedback
        count = result["activation_count"]
        for name in PER_ACTIVATION:
            with self.subTest(field=name):
                self.assertEqual(len(result[name]), count)
        for name in PER_HOLD:
            with self.subTest(field=name):
                self.assertEqual(len(result[name]), result["trace_hold_count"])
        self.assertEqual(
            len(result["trace_hold_since_previous_release_ms"]),
            result["trace_hold_count"] - 1,
        )
        self.assertEqual(len(result["activation_rearm_spacing_seconds"]), count - 1)
        self.assertEqual(result["cancel_hold_count"], count + result["refused_hold_count"])
        # Map-selection taps are CANCEL holds at the snapshot level only.
        self.assertEqual(
            result["cancel_hold_count"],
            result["trace_hold_count"] + result["trace_gesture_tap_count"],
        )
        self.assertEqual(result["gesture_tap_count"], result["trace_gesture_tap_count"])
        self.assertEqual(result["gesture_tap_count"], feedback["gesture_tap_count"])
        # A selection of map N counts N CANCEL taps inside N + 1 SET holds.
        self.assertEqual(result["gesture_tap_count"], sum(self.selections))
        self.assertEqual(
            result["set_hold_count"], sum(index + 1 for index in self.selections)
        )
        self.assertEqual(
            result["active_indication_interval_count"],
            count + sum(feedback["map_feedback_pulse_counts"]),
        )
        values = dict(zip(feedback["byte5_values"], feedback["byte5_frame_counts"], strict=True))
        self.assertEqual(
            result["trace_active_frame_count"], values[result["dashboard_active_byte5"]]
        )
        self.assertEqual(
            result["trace_active_frame_count"],
            sum(result["trace_hold_active_frames"])
            + feedback["map_feedback_on_frames"] * sum(feedback["map_feedback_pulse_counts"]),
        )
        self.assertEqual(
            result["trace_failed_frame_count"], values[feedback["failed_held_attempt_byte5"]]
        )
        self.assertEqual(
            result["trace_failed_frame_count"],
            sum(result["trace_hold_failed_frames"])
            + feedback["gesture_tap_failed_frame_count"],
        )
        self.assertEqual(result["identity_pair_count"], result["snapshot_count"])
        self.assertEqual(
            result["identity_count"]
            + result["identity_difference_inside_count"]
            + result["identity_difference_outside_count"],
            result["identity_pair_count"],
        )
        self.assertEqual(
            sum(result["activation_identity_differences_hold"])
            + sum(result["activation_identity_differences_post_release"]),
            result["identity_difference_inside_count"],
        )
        self.assertEqual(
            result["dashboard_active_state"] << 4, rolling_launch.ASCD_FEEDBACK_CRUISE_SET
        )
        self.assertEqual(
            result["dashboard_active_byte5"],
            feedback["stock_byte5"] | rolling_launch.ASCD_FEEDBACK_CRUISE_SET,
        )
        self.assertEqual(
            result["full_fuel_inhibit_mask"], self.reference["full_fuel_inhibit_mask"]
        )
        comparisons = result["exhaust_cvtc_comparison_count"]
        self.assertEqual(
            comparisons, result["snapshot_count"] - 1 - result["snapshot_gap_count"]
        )
        exact = result["exhaust_cvtc_slot_exact_counts"]
        shared = [value for slot, value in enumerate(exact) if slot != MAP_3_SLOT]
        self.assertEqual(len(set(shared)), 1)
        # The flat Map 3 surface reproduces exactly the neutral targets.
        self.assertEqual(
            exact[MAP_3_SLOT],
            comparisons - result["exhaust_cvtc_target_above_neutral_count"],
        )
        self.assertTrue(all(value < comparisons for value in exact))

    def test_trace_holds_follow_the_runtime_phases(self):
        result = self.result
        feedback = self.feedback
        holds = self.activation_holds
        self.assertEqual(len(holds), result["activation_count"])
        failed = result["trace_hold_failed_frames"]
        self.assertEqual(
            [index for index, frames in enumerate(failed) if frames], [0]
        )
        self.assertEqual(failed[0], feedback["held_attempt_failed_frames"])
        self.assertEqual(result["trace_hold_active_frames"][0], 0)
        self.assertEqual(result["trace_hold_seconds"][0], feedback["held_attempt_seconds"])
        rearm_ms = result["rearm_seconds"] * 1000
        spacing = result["trace_hold_since_previous_release_ms"]
        inside = [index + 1 for index, value in enumerate(spacing) if value < rearm_ms]
        self.assertEqual(len(inside), feedback["rearm_refusal_press_count"])
        self.assertEqual(sorted(set(holds) | set(inside)), list(range(1, len(spacing) + 1)))
        self.assertFalse(set(holds) & set(inside))
        self.assertEqual(
            round(min(spacing[index - 1] for index in holds) / 1000, 1),
            round(result["minimum_rearm_spacing_seconds"], 1),
        )
        timeout_frames = result["timeout_seconds"] / (result["dashboard_frame_period_ms"] / 1000)
        for activation, hold in enumerate(holds):
            seconds = result["trace_hold_seconds"][hold]
            frames = result["trace_hold_active_frames"][hold]
            held = result["trace_activation_inactive_frames_held"][activation]
            with self.subTest(activation=activation + 1):
                if seconds > result["timeout_seconds"]:
                    self.assertLessEqual(abs(frames - timeout_frames), 1)
                    self.assertGreater(held, 0)
                else:
                    self.assertLess(frames, timeout_frames)
                    self.assertEqual(held, 0)
        ticks = result["run_timeout_ticks"]
        for low, high in result["activation_active_ticks_bound"]:
            if low <= ticks <= high:
                break
        else:
            self.fail("no ACTIVE bound admits the run timeout")

    def test_term_statuses_follow_the_figures(self):
        result = self.result
        status = self.status
        speeds = result["activation_speed_range_kmh"]
        moving = [index for index, (low, _) in enumerate(speeds) if low > 0]
        standing = [index for index, (_, high) in enumerate(speeds) if high == 0]
        self.assertEqual(status["moving_activation"] == "pass", len(moving) >= 2)
        self.assertEqual(status["neutral_activation"] == "pass", len(standing) >= 1)
        self.assertEqual(
            status["disabled_map_refusal"] == "pass",
            self.feedback["held_attempt_active_frames"] == 0
            and self.feedback["held_attempt_failed_frames"] > 0,
        )
        self.assertEqual(
            status["active_indication"] == "pass",
            all(result["trace_hold_active_frames"][hold] for hold in self.activation_holds)
            and result["full_mask_outside_record_count"] == 0,
        )
        cycles = result["activation_full_mask_cycles"]
        self.assertEqual(
            status["full_mask_cycles"] == "pass",
            sum(1 for value in cycles if value >= 2) >= 2
            and result["full_mask_outside_record_count"] == 0
            and result["partial_mask_record_count"] == 0
            and all(result["activation_captured_rpm_native"]),
        )
        low, high = self.reference["activation_rpm_range"]
        inside = sum(
            1 for first, last in result["activation_captured_rpm"] if low <= first and last <= high
        )
        self.assertEqual(result["reference_range_activation_count"], inside)
        self.assertEqual(
            [
                index
                for index, (first, last) in enumerate(result["activation_captured_rpm"])
                if low <= first and last <= high
            ],
            moving,
        )
        coverage = (
            "not_covered"
            if inside == 0
            else "covered" if inside == result["activation_count"] else "partially_covered"
        )
        self.assertEqual(status["reference_capture_range"], coverage)
        floor, ceiling = self.reference["post_release_full_inhibit_clear_latency_ms"]
        bounds = [bound for bound in result["trace_activation_release_clear_ms"] if bound]
        self.assertTrue(bounds)
        if any(last < floor or first > ceiling for first, last in bounds):
            latency = "fail"
        elif all(floor <= first and last <= ceiling for first, last in bounds):
            latency = "pass"
        else:
            latency = "unresolved"
        self.assertEqual(status["release_clear_latency"], latency)
        self.assertEqual(
            status["rearm"] == "pass",
            result["minimum_rearm_spacing_seconds"] > result["rearm_seconds"],
        )
        self.assertEqual(
            status["rearm_refusal"] == "pass", self.feedback["rearm_refusal_press_count"] > 0
        )
        self.assertEqual(status["run_timeout"] == "pass", result["timeout_exercised"])
        self.assertEqual(status["timeout_reason"], "untested")
        target = result["target_command"]
        reached = all(
            records > 0
            for records, cut, rpm in zip(
                result["activation_apc_target_records"],
                result["activation_cut_rpm"],
                result["activation_rpm_range"],
                strict=True,
            )
            if rpm[1] >= cut[0]
        )
        self.assertEqual(
            status["retard_bound"] == "pass",
            reached
            and not any(result["activation_apc_outside_bound_records"])
            and max(result["activation_apc_max"]) <= target,
        )
        self.assertEqual(
            status["identity_localization"] == "pass",
            result["identity_difference_outside_count"] == 0,
        )
        self.assertEqual(status["physical_outputs"], "outside_measurement")
        open_terms = [
            name
            for name, value in status.items()
            if value != "pass" and name != "physical_outputs"
        ]
        self.assertEqual(
            result["hardware_status"],
            "functional_pass_with_open_boundaries"
            if open_terms
            else "functional_pass_with_physical_output_boundaries",
        )

    def test_published_figures_match_the_registry(self):
        result = self.result
        reference = self.reference
        speeds = result["activation_speed_range_kmh"]
        moving = [index for index, (low, _) in enumerate(speeds) if low > 0]
        captured = result["activation_captured_rpm"]

        def captured_word(index):
            first, last = captured[index]
            return _number(first) if first == last else f"{_number(first)} to {_number(last)}"

        holds = self.activation_holds
        seconds = result["trace_hold_seconds"]
        timed_out = [
            activation
            for activation, hold in enumerate(holds)
            if seconds[hold] > result["timeout_seconds"]
        ]
        moving_timeout = [activation for activation in timed_out if activation in moving]
        carrying = [
            index for index, full in enumerate(result["activation_release_full_mask"]) if full
        ]
        self.assertEqual(len(carrying), 1)
        low, high = reference["activation_rpm_range"]
        self.assertEqual(moving_timeout, [1])
        self.assertEqual(carrying, [2])

    def test_button_sources_are_the_published_codes(self):
        source = ENGINE_SOURCE.read_text(encoding="utf-8")
        match = re.search(r"^rl_button_address:\n\.long (0x[0-9A-F]+)$", source, re.MULTILINE)
        self.assertIsNotNone(match)
        self.assertEqual(match.group(1), "0xFFFF2A85")

    @pytest.mark.slow
    @unittest.skipUnless(LOGS.is_dir() and IMAGE.is_file(), "road captures are local and untracked")
    def test_audit_reproduces_the_record(self):
        from tools.logs import rolling_launch_audit as audit

        result = self.result
        path = LOGS / Path(result["capture_name"]).with_suffix(".mlg").name
        if not path.is_file():
            self.skipTest(f"missing capture: {path.name}")
        calibration = audit.load_calibration(IMAGE, "JK08A")
        self.assertEqual(calibration.image_sha256, result["image_sha256"])
        capture = audit.read_capture(path)
        self.assertEqual(capture.sha256, result["converted_mlg_sha256"])
        output = audit.audit_capture(capture, calibration, selected_map=result["selected_map"])
        compared = [
            key
            for key in output
            if key in result
            and key not in RECORD_ONLY
            and key not in ("capture_name", "capture_sha256")
        ]
        per_event = {
            key
            for key, value in result.items()
            if key.startswith("activation_") and not isinstance(value, str)
        }
        self.assertLessEqual(per_event - RECORD_ONLY, set(compared))
        for key in compared:
            with self.subTest(key=key):
                self.assertEqual(output[key], result[key])
        samples = capture.samples
        above = sum(
            1
            for prior, current in zip(samples, samples[1:])
            if current.tick - prior.tick == 1
            and prior.coolant_raw is not None
            and current.exhaust_cvtc_target_raw != NEUTRAL_EXHAUST_TARGET
        )
        self.assertEqual(above, result["exhaust_cvtc_target_above_neutral_count"])
        tables = [replay.main.table for replay in calibration.exhaust_replays]
        self.assertEqual(
            {value for row in tables[MAP_3_SLOT] for value in row}, {NEUTRAL_EXHAUST_TARGET}
        )
        shared = [table for slot, table in enumerate(tables) if slot != MAP_3_SLOT]
        self.assertTrue(all(table == shared[0] for table in shared))


if __name__ == "__main__":
    unittest.main()
