from pathlib import Path
import tomllib
import unittest

from patches import rolling_launch
from patches import rolling_launch_layout
from tools.can_dashboard import recording
from tools.logs import mlg_relation_audit


ROOT = Path(__file__).resolve().parents[2]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
ROLLING_LAUNCH = ROOT / "patches" / "rolling-launch.md"
KEY = "rolling_launch.map_3_vehicle_2026_09_21"
FEEDBACK_KEY = "map_switching.feedback_vehicle_2026_09_21"
SESSION_KEY = "can_telemetry.schema2_profile5_drive_2026_09_21"
# Frame 0x551 leaves the serializer on every tenth 10.24 ms invocation.
SERIALIZER_CALLS_PER_FRAME = 10
RPM_PER_NATIVE = recording.MLG_CALIBRATIONS["rpm_raw"].factor
NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven")
ORDINALS = ("first", "second", "third", "fourth", "fifth", "sixth")
FUNCTIONAL_TERMS = (
    "moving_activation",
    "active_indication",
    "full_mask_cycles",
    "rearm",
    "retard_bound",
    "identity_localization",
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
    "activation_full_mask_cycles",
    "activation_post_release_full_mask_cycles",
    "activation_full_mask_rpm",
    "activation_apc_max",
    "activation_apc_target_records",
    "activation_apc_outside_bound_records",
    "activation_stock_command_range",
    "activation_identity_differences_hold",
    "activation_identity_differences_post_release",
    "activation_release_full_mask",
    "activation_release_clear_bound_ms",
    "activation_release_clear_by_window_removal",
)


def _normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def _entry(registry, dotted):
    section, name = dotted.split(".")
    return registry[section][name]


def _number(value):
    return f"{value:g}"


def _series(values):
    words = [str(value) for value in values]
    if len(words) <= 2:
        return " and ".join(words)
    return ", ".join(words[:-1]) + ", and " + words[-1]


def _holds(numbers):
    """Render one-based hold numbers the way the document lists them."""
    numbers = list(numbers)
    if len(numbers) > 2 and numbers == list(range(numbers[0], numbers[-1] + 1)):
        return f"{numbers[0]} to {numbers[-1]}"
    return _series(numbers)


def _window(calibration, slot, captured):
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
    return state.cut_rpm_native, state.restore_rpm_native


class RollingLaunchMap3VehicleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        cls.result = _entry(cls.registry, KEY)
        cls.reference = _entry(cls.registry, cls.result["reference"])
        cls.feedback = _entry(cls.registry, FEEDBACK_KEY)
        cls.session = _entry(cls.registry, SESSION_KEY)
        cls.layout = rolling_launch_layout.load_layout()
        cls.calibration = rolling_launch.Calibration.from_bytes(
            bytes.fromhex(cls.result["configuration_hex"])
        )
        cls.tick_ms = cls.layout.scheduler.tick_microseconds / 1000
        cls.document = _normalized(ROLLING_LAUNCH)

    def test_record_names_the_session_capture_and_image(self):
        result = self.result
        captures = {
            row["capture_name"]: row
            for row in _entry(self.registry, result["capture_registry"])
        }
        capture = captures[result["capture_name"]]
        self.assertEqual(capture["capture_sha256"], result["capture_sha256"])
        self.assertEqual(capture["record_count"], result["snapshot_count"])
        self.assertEqual(result["image_sha256"], self.session["image_sha256"])
        self.assertEqual(result["observed_on"], self.session["recorded_on"])
        self.assertEqual(result["capture_name"], self.feedback["moving_cancel_capture"])
        self.assertTrue((ROOT / result["audit_tool"]).is_file())

    def test_configuration_fields_follow_the_record(self):
        result = self.result
        calibration = self.calibration
        configuration = self.layout.configuration
        self.assertTrue(calibration.is_valid())
        self.assertEqual(result["configuration_address"], configuration.start)
        self.assertEqual(
            len(bytes.fromhex(result["configuration_hex"])),
            configuration.end - configuration.start,
        )
        self.assertEqual(
            result["mode"], rolling_launch.Mode(calibration.mode).name.lower()
        )
        self.assertEqual(
            result["enabled_maps"],
            [
                index + 1
                for index in range(rolling_launch.SLOT_COUNT)
                if calibration.enabled_for(index)
            ],
        )
        for name in (
            "min_speed",
            "min_pedal",
            "min_rpm_native",
            "rpm_offset_native",
            "min_hysteresis_native",
            "max_hysteresis_native",
            "hysteresis_ratio_tenths",
            "retard_ramp_native",
            "run_timeout_ticks",
            "rearm_ticks",
        ):
            with self.subTest(field=name):
                self.assertEqual(result[name], getattr(calibration, name))
        self.assertEqual(
            result["coolant_range"], [calibration.coolant_min, calibration.coolant_max]
        )
        self.assertIn(result["selected_map"], result["enabled_maps"])
        self.assertEqual(
            result["target_command"],
            calibration.target_commands[result["selected_map"] - 1],
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
            result["timeout_seconds"], round(result["run_timeout_ticks"] * tick_s, 3)
        )
        self.assertEqual(
            result["rearm_seconds"], round(result["rearm_ticks"] * tick_s, 3)
        )
        holds = result["activation_hold_seconds"]
        self.assertEqual(result["longest_hold_seconds"], max(holds))
        self.assertEqual(
            result["minimum_rearm_spacing_seconds"],
            min(result["activation_rearm_spacing_seconds"]),
        )
        # Every duration is a whole number of snapshot intervals.
        for seconds in (
            *result["activation_start_seconds"],
            *holds,
            *result["activation_active_indication_seconds"],
            *result["activation_rearm_spacing_seconds"],
        ):
            with self.subTest(seconds=seconds):
                self.assertEqual(round(round(seconds / tick_s) * tick_s, 3), seconds)
        # One snapshot of uncertainty lies on each side of the release and
        # of the clear.
        for bound in result["activation_release_clear_bound_ms"]:
            if not bound:
                continue
            first, last = (round(value / tick_ms) for value in bound)
            with self.subTest(bound=bound):
                self.assertEqual(last - first, 2)
                self.assertEqual(
                    bound, [round(first * tick_ms, 1), round(last * tick_ms, 1)]
                )

    def test_windows_follow_the_configuration_replay(self):
        result = self.result
        slot = result["selected_map"] - 1
        for index, (low, high) in enumerate(
            result["activation_captured_rpm_native"]
        ):
            with self.subTest(activation=index + 1):
                windows = [
                    _window(self.calibration, slot, captured)
                    for captured in range(low, high + 1)
                ]
                self.assertEqual(
                    result["activation_captured_rpm"][index],
                    [low * RPM_PER_NATIVE, high * RPM_PER_NATIVE],
                )
                self.assertEqual(
                    result["activation_cut_rpm"][index],
                    [windows[0][0] * RPM_PER_NATIVE, windows[-1][0] * RPM_PER_NATIVE],
                )
                self.assertEqual(
                    result["activation_restore_rpm"][index],
                    [
                        min(window[1] for window in windows) * RPM_PER_NATIVE,
                        max(window[1] for window in windows) * RPM_PER_NATIVE,
                    ],
                )
                cut_low = result["activation_cut_rpm"][index][0]
                rpm_high = result["activation_rpm_range"][index][1]
                if result["activation_full_mask_cycles"][index]:
                    self.assertGreaterEqual(rpm_high, cut_low)
                else:
                    self.assertLess(rpm_high, cut_low)

    def test_counts_are_consistent_across_the_registry(self):
        result = self.result
        count = result["activation_count"]
        for name in PER_ACTIVATION:
            with self.subTest(field=name):
                self.assertEqual(len(result[name]), count)
        self.assertEqual(len(result["activation_rearm_spacing_seconds"]), count - 1)
        self.assertEqual(
            result["cancel_hold_count"], count + result["refused_hold_count"]
        )
        self.assertEqual(result["active_indication_interval_count"], count)
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
            result["dashboard_active_state"] << 4,
            rolling_launch.ASCD_FEEDBACK_CRUISE_SET,
        )
        self.assertEqual(
            result["dashboard_active_byte5"],
            self.feedback["stock_byte5"] | rolling_launch.ASCD_FEEDBACK_CRUISE_SET,
        )
        self.assertEqual(
            result["full_fuel_inhibit_mask"], self.reference["full_fuel_inhibit_mask"]
        )
        self.assertEqual(
            result["full_fuel_inhibit_mask"],
            self.registry["main_fuel_cut"]["vehicle_2026_09_21"]["fuel_cut_mask"],
        )
        comparisons = result["exhaust_cvtc_comparison_count"]
        self.assertEqual(
            comparisons, result["snapshot_count"] - 1 - result["snapshot_gap_count"]
        )
        for slot, exact in enumerate(result["exhaust_cvtc_slot_exact_counts"]):
            with self.subTest(slot=slot + 1):
                if slot + 1 == result["selected_map"]:
                    self.assertEqual(exact, comparisons)
                else:
                    self.assertLess(exact, comparisons)
        self.assertEqual(result["set_hold_count"], 0)

    def test_moving_holds_agree_with_the_map_feedback_record(self):
        result = self.result
        feedback = self.feedback
        cycled = [
            inside + after
            for inside, after in zip(
                result["activation_full_mask_cycles"],
                result["activation_post_release_full_mask_cycles"],
                strict=True,
            )
        ]
        self.assertEqual(
            feedback["moving_cancel_hold_count"], result["cancel_hold_count"]
        )
        self.assertEqual(
            feedback["moving_cancel_state_4_interval_count"],
            result["active_indication_interval_count"],
        )
        self.assertEqual(
            feedback["moving_cancel_full_inhibit_interval_count"],
            sum(1 for cycles in cycled if cycles),
        )
        self.assertEqual(
            feedback["moving_cancel_full_inhibit_outside_record_count"],
            result["full_mask_outside_record_count"],
        )
        self.assertEqual(
            feedback["moving_cancel_failed_attempt_record_count"],
            result["failed_attempt_record_count"],
        )
        speeds = result["activation_speed_range_kmh"]
        self.assertEqual(
            feedback["moving_cancel_speed_kmh"],
            [
                round(min(low for low, _ in speeds), 1),
                round(max(high for _, high in speeds), 1),
            ],
        )
        # The map feedback record spans the first to the last CANCEL record,
        # one snapshot less than the hold that ends at the first released one.
        tick_s = self.tick_ms / 1000
        holds = result["activation_hold_seconds"]
        self.assertEqual(
            feedback["moving_cancel_hold_seconds"],
            [round(min(holds) - tick_s, 2), round(max(holds) - tick_s, 2)],
        )

    def test_term_statuses_follow_the_figures(self):
        result = self.result
        status = result["term_status"]
        count = result["activation_count"]
        speeds = result["activation_speed_range_kmh"]
        moving = (
            count >= 2
            and result["refused_hold_count"] == 0
            and min(low for low, _ in speeds) > 0
        )
        self.assertEqual(status["moving_activation"] == "pass", moving)
        self.assertEqual(
            status["active_indication"] == "pass",
            result["active_indication_interval_count"] == count
            and result["failed_attempt_record_count"] == 0,
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
            1
            for first, last in result["activation_captured_rpm"]
            if low <= first and last <= high
        )
        self.assertEqual(result["reference_range_activation_count"], inside)
        coverage = (
            "not_covered"
            if inside == 0
            else "covered" if inside == count else "partially_covered"
        )
        self.assertEqual(status["reference_capture_range"], coverage)

        floor, ceiling = self.reference["post_release_full_inhibit_clear_latency_ms"]
        bounds = [
            bound for bound in result["activation_release_clear_bound_ms"] if bound
        ]
        if any(last < floor or first > ceiling for first, last in bounds):
            latency = "fail"
        elif all(floor <= first and last <= ceiling for first, last in bounds):
            latency = "pass"
        else:
            latency = "unresolved"
        self.assertEqual(status["release_clear_latency"], latency)

        rearm = result["rearm_seconds"]
        spacing = result["minimum_rearm_spacing_seconds"]
        self.assertEqual(
            status["rearm"] == "pass",
            result["refused_hold_count"] == 0 and spacing > rearm,
        )
        self.assertEqual(status["rearm_refusal"] == "untested", spacing > rearm)
        self.assertEqual(
            status["run_timeout"] == "untested",
            result["longest_hold_seconds"] < result["timeout_seconds"],
        )

        target = result["target_command"]
        reached = all(
            records > 0 or stock[0] >= target
            for records, stock in zip(
                result["activation_apc_target_records"],
                result["activation_stock_command_range"],
                strict=True,
            )
        )
        self.assertEqual(
            status["retard_bound"] == "pass",
            reached and not any(result["activation_apc_outside_bound_records"]),
        )
        self.assertEqual(
            status["identity_localization"] == "pass",
            result["identity_difference_outside_count"] == 0,
        )
        self.assertEqual(status["physical_outputs"], "outside_measurement")

        self.assertTrue(all(status[name] == "pass" for name in FUNCTIONAL_TERMS))
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

        selected = {
            index for maps in self.feedback["selected_maps"].values() for index in maps
        }
        self.assertIn(2, result["enabled_maps"])
        self.assertEqual(result["map_2_status"] == "untested", 2 not in selected)

    def test_published_figures_match_the_registry(self):
        result = self.result
        reference = self.reference
        text = self.document
        selected = result["selected_map"]
        target = result["target_command"]
        label = reference["firmware_label"]

        speeds = result["activation_speed_range_kmh"]
        captured = result["activation_captured_rpm"]
        cycles = result["activation_full_mask_cycles"]
        cycled = [value for value in cycles if value]
        idle = cycles.index(0)
        app_low, app_high = result["activation_app1_range_v"][idle]
        rpm_low, rpm_high = result["activation_rpm_range"][idle]
        cut_low, cut_high = result["activation_cut_rpm"][idle]
        stock_low, stock_high = result["activation_stock_command_range"][idle]
        self.assertEqual(stock_low, stock_high)
        self.assertGreater(stock_low, target)
        reached = [value for value in result["activation_apc_target_records"] if value]
        pairs = result["identity_pair_count"]
        failed_state = rolling_launch.ASCD_FEEDBACK_CRUISE >> 4

        full_at_release = result["activation_release_full_mask"]
        post_release = result["activation_post_release_full_mask_cycles"]
        without = [n for n, full in enumerate(full_at_release, 1) if not full]
        carrying = [n for n, full in enumerate(full_at_release, 1) if full]
        continuing = [n for n in carrying if not post_release[n - 1]]
        restarting = [n for n in carrying if post_release[n - 1]]
        self.assertTrue(
            all(
                result["activation_release_clear_by_window_removal"][n - 1]
                for n in carrying
            )
        )
        floor, ceiling = reference["post_release_full_inhibit_clear_latency_ms"]
        bounds = result["activation_release_clear_bound_ms"]

        def phrase(numbers):
            return " and ".join(
                f"{_number(bounds[n - 1][0])} to {_number(bounds[n - 1][1])} ms "
                f"for hold {n}"
                for n in numbers
            )

        within = [
            n
            for n in carrying
            if floor <= bounds[n - 1][0] and bounds[n - 1][1] <= ceiling
        ]
        straddling = [n for n in carrying if n not in within]
        self.assertEqual(result["snapshot_gap_count"], 0)
        self.assertTrue(result["capture_name"].endswith(".mlg"))

        low, high = reference["activation_rpm_range"]
        statements = (
            f"`{KEY}`",
            f"`../{result['audit_tool']}`",
            f"The mixed Map {selected} drive of the {result['observed_on']} road "
            "session",
            f"The recording holds {result['snapshot_count']:,} consecutive telemetry "
            "snapshots and no TRC accompanies it",
            f"bounded by the {_number(result['snapshot_period_ms'])} ms snapshot "
            "spacing and each dashboard state by the "
            f"{_number(result['dashboard_frame_period_ms'])} ms period of frame "
            "`0x551`",
            f"only the Map {selected} exhaust CVTC target surface reproduces all "
            f"{result['exhaust_cvtc_comparison_count']:,} recorded targets",
            f"All {NUMBER_WORDS[result['activation_count']]} moving CANCEL holds, at "
            f"{_number(round(min(first for first, _ in speeds), 1))} to "
            f"{_number(round(max(last for _, last in speeds), 1))} km/h, enter "
            f"`ACTIVE` state {result['dashboard_active_state']}, and no record shows "
            f"state {failed_state}",
            "bounds the captured words of the "
            f"{NUMBER_WORDS[len(captured)]} holds between "
            f"{_number(min(first for first, _ in captured))} and "
            f"{_number(max(last for _, last in captured))} RPM",
            f"{NUMBER_WORDS[result['reference_range_activation_count']]} of them lie "
            f"inside the {_number(low)} to {_number(high)} RPM activation range of "
            f"the firmware `{label}` capture",
            f"{NUMBER_WORDS[len(cycled)].capitalize()} holds reach their cut word "
            f"and cycle the full `0x{result['full_fuel_inhibit_mask']:02X}` mask "
            f"{_series(cycled)} times while CANCEL is held",
            f"The {ORDINALS[idle]} hold keeps APP1 between {_number(app_low)} and "
            f"{_number(app_high)} V while engine speed stays between "
            f"{_number(rpm_low)} and {_number(rpm_high)} RPM, below its "
            f"{_number(cut_low)} to {_number(cut_high)} RPM cut word, and its stock "
            f"command {stock_low} is already later than the target {target}",
            f"reaches the target {target} in the other "
            f"{NUMBER_WORDS[len(reached)]} holds",
            f"with `stock = {mlg_relation_audit.APC_COMMAND_BASE} - final_timing`",
            f"`final_timing = {mlg_relation_audit.APC_COMMAND_BASE} - APC command` "
            f"holds in {result['identity_count']:,} of the {pairs:,} snapshots; all "
            f"{result['identity_difference_inside_count']:,} differences fall inside "
            "the activation windows, "
            f"{sum(result['activation_identity_differences_hold'])} while CANCEL is "
            f"held and {sum(result['activation_identity_differences_post_release'])} "
            "after its release",
            f"Holds {_holds(without)} carry no full mask at the release",
            f"Holds {_holds(carrying)} show a full mask at or after the first "
            f"released `0x239` record: hold {_holds(continuing)} continues its "
            f"cycle, and holds {_holds(restarting)} start one more",
            f"The release-to-clear distance lies within {phrase(within)}, inside "
            f"the `{_number(floor)}..{_number(ceiling)} ms` range of the firmware "
            f"`{label}` trace",
            f"and within {phrase(straddling)}, which the snapshot spacing does not "
            f"place on either side of {_number(ceiling)} ms",
            "Each later hold starts at least "
            f"{_number(result['minimum_rearm_spacing_seconds'])} s after the "
            f"preceding release, beyond the {_number(result['rearm_seconds'])} s "
            "rearm period, and activates",
            f"The longest hold lasts {_number(result['longest_hold_seconds'])} s, "
            f"and the {_number(result['timeout_seconds'])} s run timeout is not "
            "exercised",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                self.assertIn(statement, text)

    def test_open_boundaries_follow_the_registered_status(self):
        status = self.result["term_status"]
        statements = (
            (
                "which the snapshot spacing does not place on either side",
                status["release_clear_latency"] == "unresolved",
            ),
            (
                "the refusal inside that period is not exercised",
                status["rearm_refusal"] == "untested",
            ),
            (
                "run timeout is not exercised",
                status["run_timeout"] == "untested",
            ),
            (
                "No capture of the recorded image selects Map 2",
                self.result["map_2_status"] == "untested",
            ),
            (
                "spark angle at the crankshaft and electrical injector output "
                "remain outside the measurement",
                status["physical_outputs"] == "outside_measurement",
            ),
        )
        for statement, registered in statements:
            with self.subTest(statement=statement):
                self.assertEqual(statement in self.document, registered)


if __name__ == "__main__":
    unittest.main()
