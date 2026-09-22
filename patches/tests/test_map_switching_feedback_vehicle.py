from collections import Counter
from pathlib import Path
import tomllib
import unittest

from patches import map_switching_layout as layout_model
from patches import rolling_launch


ROOT = Path(__file__).resolve().parents[2]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
CAN_DEFS = ROOT / "defs" / "JK08A.can.md"
ROLLING_LAUNCH = ROOT / "patches" / "rolling-launch.md"
SELECTOR = ROOT / "patches" / "map-switching-selector.md"
KEY = "map_switching.feedback_vehicle_2026_09_21"
KEY_2026_09_22 = "map_switching.feedback_vehicle_2026_09_22"
LOGS_2026_09_22 = ROOT / "tmp" / "logs-09-22"
# Frame 0x551 leaves the serializer on every tenth 10.24 ms invocation.
SERIALIZER_CALLS_PER_FRAME = 10
NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven")


def _normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


def _series(values):
    words = [str(value) for value in values]
    if len(words) <= 2:
        return " and ".join(words)
    return ", ".join(words[:-1]) + ", and " + words[-1]


def _runs(flags):
    runs = []
    start = None
    for index, flag in enumerate(flags):
        if flag and start is None:
            start = index
        elif not flag and start is not None:
            runs.append((start, index))
            start = None
    if start is not None:
        runs.append((start, len(flags)))
    return runs


def _trace_feedback(path):
    """Measure the selections and pulses of a TRC from frames 0x239 and 0x551."""
    from tools.logs import peak_trc_audit

    frames = peak_trc_audit.load_trace(path).frames
    buttons = [(f.offset_ms, f.data[3]) for f in frames if f.can_id == 0x239 and len(f.data) >= 4]
    dashboard = [(f.offset_ms, f.data[5]) for f in frames if f.can_id == 0x551 and len(f.data) >= 6]
    codes = [code for _, code in buttons]
    states = [(value & rolling_launch.ASCD_FEEDBACK_MASK) >> 4 for _, value in dashboard]
    set_runs = _runs([code == rolling_launch.BUTTON_SET for code in codes])
    selections = []
    index = 0
    while index < len(set_runs):
        begin, stop = set_runs[index]
        taps = 0
        # A CANCEL run between two SET runs is one tap of the gesture.
        while (
            index + 1 < len(set_runs)
            and all(code == rolling_launch.BUTTON_CANCEL for code in codes[stop : set_runs[index + 1][0]])
            and stop < set_runs[index + 1][0]
        ):
            taps += 1
            index += 1
            stop = set_runs[index][1]
        selections.append((buttons[begin][0], buttons[stop][0], taps))
        index += 1
    active = _runs([state == 4 for state in states])
    failed = _runs([state == 5 for state in states])
    measured = []
    for begin, commit, taps in selections:
        pressed = next(
            (time for time, code in buttons if time > commit and code != rolling_launch.BUTTON_RELEASED),
            float("inf"),
        )
        pulses = [(first, stop) for first, stop in active if commit < dashboard[first][0] < pressed]
        measured.append(
            {
                "begin_ms": begin,
                "commit_ms": commit,
                "taps": taps,
                "pulse_starts_ms": [dashboard[first][0] for first, _ in pulses],
                "pulse_on_frames": [stop - first for first, stop in pulses],
                "pulse_off_frames": [
                    later[0] - earlier[1] for earlier, later in zip(pulses, pulses[1:])
                ],
                "tap_failed_frames": [
                    stop - first for first, stop in failed if begin < dashboard[first][0] < commit
                ],
            }
        )
    return Counter(value for _, value in dashboard), len(dashboard), measured


class MapFeedbackVehicleSessionTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        section, name = KEY.split(".")
        cls.result = cls.registry[section][name]
        cls.feedback = layout_model.load_layout().feedback
        cls.can_defs = _normalized(CAN_DEFS)
        cls.rolling_launch = _normalized(ROLLING_LAUNCH)
        cls.selector = _normalized(SELECTOR)

    def test_observation_uses_the_registered_session_captures(self):
        result = self.result
        section, name = result["capture_registry"].split(".")
        captures = {row["capture_name"] for row in self.registry[section][name]}
        session = self.registry["can_telemetry"][
            "schema2_profile5_drive_2026_09_21"
        ]
        self.assertEqual(result["image_sha256"], session["image_sha256"])
        self.assertEqual(result["recorded_on"], session["recorded_on"])
        named = {
            *result["selected_maps"],
            result["cruise_main_capture"],
            result["moving_cancel_capture"],
        }
        self.assertLessEqual(named, captures)

    def test_states_are_the_runtime_insertions_over_the_stock_byte(self):
        result = self.result
        mask = result["status_mask"]
        stock = result["stock_byte5"]
        self.assertEqual(mask, self.feedback.status_mask)
        self.assertEqual(mask, rolling_launch.ASCD_FEEDBACK_MASK)
        self.assertEqual(stock & mask, 0)
        insertions = (
            ("map_feedback", self.feedback.lamp_on_value),
            ("failed_held_attempt", rolling_launch.ASCD_FEEDBACK_CRUISE),
            ("rolling_launch_active", rolling_launch.ASCD_FEEDBACK_CRUISE_SET),
        )
        for prefix, inserted in insertions:
            with self.subTest(state=prefix):
                state = result[f"{prefix}_state"]
                self.assertEqual(state << 4, inserted)
                self.assertEqual(result[f"{prefix}_byte5"], stock | inserted)
        self.assertEqual(result["cruise_main_byte5_values"], [stock])

    def test_pulse_frames_match_the_layout_default_timing(self):
        result = self.result
        self.assertEqual(
            result["map_feedback_on_frames"] * SERIALIZER_CALLS_PER_FRAME,
            self.feedback.default_on_frames,
        )
        self.assertEqual(
            result["map_feedback_off_frames"] * SERIALIZER_CALLS_PER_FRAME,
            self.feedback.default_off_frames,
        )
        low, high = result["failed_held_attempt_frames"]
        self.assertLessEqual(1, low)
        self.assertLessEqual(low, high)

    def test_selections_and_moving_holds_are_consistent(self):
        result = self.result
        for capture, maps in result["selected_maps"].items():
            with self.subTest(capture=capture):
                self.assertTrue(maps)
                self.assertTrue(all(1 <= index <= 5 for index in maps))
        holds = result["moving_cancel_hold_count"]
        self.assertEqual(result["moving_cancel_state_4_interval_count"], holds)
        self.assertLessEqual(
            result["moving_cancel_full_inhibit_interval_count"], holds
        )
        self.assertEqual(
            result["moving_cancel_full_inhibit_mask"],
            self.registry["main_fuel_cut"]["vehicle_2026_09_21"][
                "fuel_cut_mask"
            ],
        )
        self.assertEqual(result["moving_cancel_failed_attempt_record_count"], 0)
        self.assertEqual(
            result["moving_cancel_full_inhibit_outside_record_count"], 0
        )

    def test_published_figures_match_the_registry(self):
        result = self.result
        selections = sum(len(maps) for maps in result["selected_maps"].values())
        low, high = result["failed_held_attempt_frames"]
        holds = NUMBER_WORDS[result["moving_cancel_hold_count"]]
        on = NUMBER_WORDS[result["map_feedback_on_frames"]]
        off = NUMBER_WORDS[result["map_feedback_off_frames"]]
        stock = f"`0x{result['stock_byte5']:02X}`"
        for text, name in (
            (self.can_defs, "can"),
            (self.rolling_launch, "rolling-launch"),
        ):
            with self.subTest(published=name):
                self.assertIn(f"`{KEY}`", text)
                self.assertIn(f"of the {holds} moving CANCEL holds", text)
        self.assertIn(f"contain {selections} map selections", self.can_defs)
        self.assertIn(
            f"{NUMBER_WORDS[low]}- or {NUMBER_WORDS[high]}-frame "
            f"`0x{result['failed_held_attempt_byte5']:02X}` run",
            self.can_defs,
        )
        self.assertIn(f"{on} frames ON and {off} frames OFF", self.can_defs)
        self.assertIn(f"leaves byte 5 at {stock}", self.can_defs)
        full_inhibit = NUMBER_WORDS[
            result["moving_cancel_full_inhibit_interval_count"]
        ]
        self.assertIn(
            f"{full_inhibit} of the intervals carry the full "
            f"`0x{result['moving_cancel_full_inhibit_mask']:02X}`",
            self.rolling_launch,
        )

    def test_lamp_statements_follow_the_registered_status(self):
        result = self.result
        both_lamps = result["map_feedback_lamp_status"] == "pass"
        # A later session may observe the CRUISE-alone lamp of state 5.
        section, name = KEY_2026_09_22.split(".")
        cruise_alone_open = all(
            record["failed_held_attempt_lamp_status"] == "untested"
            for record in (result, self.registry[section][name])
        )
        statements = (
            (
                self.can_defs,
                "each state-4 map feedback pulse lights SET together with CRUISE",
                both_lamps,
            ),
            (
                self.rolling_launch,
                "state 4 lights SET together with CRUISE on the exact target",
                both_lamps,
            ),
            (
                self.selector,
                "map feedback pulses shows SET lighting together with CRUISE",
                both_lamps,
            ),
            (
                self.can_defs,
                "the lamp response to state 5 is not separately observed",
                cruise_alone_open,
            ),
            (
                self.rolling_launch,
                "The CRUISE-alone result of state 5 remains a hardware "
                "acceptance item",
                cruise_alone_open,
            ),
        )
        for text, statement, registered in statements:
            with self.subTest(statement=statement):
                self.assertEqual(statement in text, registered)
        self.assertIn(f"`{KEY}`", self.selector)


class MapFeedbackVehicle20260922Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        section, name = KEY_2026_09_22.split(".")
        cls.result = cls.registry[section][name]
        section, name = cls.result["rolling_launch_record"].split(".")
        cls.launch = cls.registry[section][name]
        cls.feedback = layout_model.load_layout().feedback
        cls.can_defs = _normalized(CAN_DEFS)

    def test_observation_uses_the_registered_session_capture(self):
        result = self.result
        section, name = result["capture_registry"].split(".")
        captures = {row["capture_name"] for row in self.registry[section][name]}
        session = self.registry["can_telemetry"]["schema2_profile5_drive_2026_09_22"]
        self.assertEqual(result["image_sha256"], session["image_sha256"])
        self.assertEqual(result["recorded_on"], session["recorded_on"])
        self.assertLessEqual({*result["selected_maps"], result["capture_name"]}, captures)
        self.assertEqual(self.launch["capture_name"], result["capture_name"])

    def test_states_are_the_runtime_insertions_over_the_stock_byte(self):
        result = self.result
        stock = result["stock_byte5"]
        self.assertEqual(result["status_mask"], self.feedback.status_mask)
        for prefix, inserted in (
            ("map_feedback", self.feedback.lamp_on_value),
            ("failed_held_attempt", rolling_launch.ASCD_FEEDBACK_CRUISE),
            ("rolling_launch_active", rolling_launch.ASCD_FEEDBACK_CRUISE_SET),
        ):
            with self.subTest(state=prefix):
                self.assertEqual(result[f"{prefix}_state"] << 4, inserted)
                self.assertEqual(result[f"{prefix}_byte5"], stock | inserted)
        self.assertEqual(
            result["byte5_values"],
            [stock, result["map_feedback_byte5"], result["failed_held_attempt_byte5"]],
        )
        self.assertEqual(result["rearm_refusal_byte5_values"], [stock])

    def test_counts_are_consistent_with_the_rolling_launch_record(self):
        result = self.result
        launch = self.launch
        counts = dict(zip(result["byte5_values"], result["byte5_frame_counts"], strict=True))
        self.assertEqual(sum(counts.values()), result["dashboard_frame_count"])
        self.assertEqual(counts[result["map_feedback_byte5"]], launch["trace_active_frame_count"])
        self.assertEqual(
            counts[result["failed_held_attempt_byte5"]], launch["trace_failed_frame_count"]
        )
        selections = [index for maps in result["selected_maps"].values() for index in maps]
        self.assertEqual(result["map_feedback_pulse_counts"], selections)
        self.assertEqual(len(result["selection_commit_seconds"]), len(selections))
        self.assertEqual(len(result["map_feedback_first_on_after_release_ms"]), len(selections))
        self.assertEqual(
            len(result["map_feedback_mean_period_ms"]),
            sum(1 for count in selections if count >= 2),
        )
        self.assertEqual(result["gesture_tap_count"], sum(selections))
        low, high = result["failed_held_attempt_frames"]
        self.assertLessEqual(low * result["gesture_tap_count"], result["gesture_tap_failed_frame_count"])
        self.assertLessEqual(result["gesture_tap_failed_frame_count"], high * result["gesture_tap_count"])
        self.assertEqual(result["held_attempt_failed_frames"], launch["trace_hold_failed_frames"][0])
        self.assertEqual(result["held_attempt_active_frames"], launch["trace_hold_active_frames"][0])
        self.assertEqual(result["held_attempt_seconds"], launch["trace_hold_seconds"][0])
        rearm_ms = launch["rearm_seconds"] * 1000
        self.assertEqual(
            result["rearm_refusal_press_count"],
            sum(1 for value in launch["trace_hold_since_previous_release_ms"] if value < rearm_ms),
        )
        # A pulse repeats every ON plus OFF frames of the 102.4 ms frame 0x551.
        period = (
            (result["map_feedback_on_frames"] + result["map_feedback_off_frames"])
            * launch["dashboard_frame_period_ms"]
        )
        for value in result["map_feedback_mean_period_ms"]:
            with self.subTest(period=value):
                self.assertLess(abs(value - period), 2)
        self.assertEqual(
            result["map_feedback_on_frames"] * SERIALIZER_CALLS_PER_FRAME,
            self.feedback.default_on_frames,
        )
        self.assertEqual(
            result["map_feedback_off_frames"] * SERIALIZER_CALLS_PER_FRAME,
            self.feedback.default_off_frames,
        )

    def test_published_figures_match_the_registry(self):
        result = self.result
        counts = dict(zip(result["byte5_values"], result["byte5_frame_counts"], strict=True))
        selections = [index for maps in result["selected_maps"].values() for index in maps]
        low, high = result["failed_held_attempt_frames"]
        first = result["map_feedback_first_on_after_release_ms"]
        period = result["map_feedback_mean_period_ms"]
        statements = (
            f"`{KEY_2026_09_22}`",
            f"carries {result['dashboard_frame_count']:,} frames of `0x551`, in which byte 5 "
            + ", ".join(
                f"holds `0x{value:02X}` {count:,} times"
                if index == 0
                else (
                    f"and `0x{value:02X}` {count:,} times"
                    if index == len(counts) - 1
                    else f"`0x{value:02X}` {count:,} times"
                )
                for index, (value, count) in enumerate(counts.items())
            ),
            f"Four SET gestures select Maps {_series(selections)}",
            f"Each of the {result['gesture_tap_count']} CANCEL taps appears as a "
            f"{NUMBER_WORDS[low]}- or {NUMBER_WORDS[high]}-frame "
            f"`0x{result['failed_held_attempt_byte5']:02X}` run",
            f"{NUMBER_WORDS[result['map_feedback_on_frames']]} frames ON and "
            f"{NUMBER_WORDS[result['map_feedback_off_frames']]} frames OFF",
            f"The first ON frame follows SET release by {min(first)} to {max(first)} ms",
            f"the pulse starts of one selection lie {min(period)} to {max(period)} ms apart "
            "on average",
            f"A {result['held_attempt_seconds']} s CANCEL hold on Map "
            f"{result['held_attempt_map']}, where Rolling Launch is disabled, shows "
            f"{result['held_attempt_failed_frames']} frames of "
            f"`0x{result['failed_held_attempt_byte5']:02X}` and no "
            f"`0x{result['map_feedback_byte5']:02X}`",
            "presses inside the Rolling Launch rearm period keep byte 5 at "
            f"`0x{result['stock_byte5']:02X}`",
        )
        for statement in statements:
            with self.subTest(statement=statement):
                self.assertIn(statement, self.can_defs)

    def test_operator_observation_is_published(self):
        result = self.result
        self.assertEqual(result["map_feedback_lamp_status"], "pass")
        self.assertEqual(result["failed_held_attempt_lamp_status"], "pass")
        self.assertIs(result["ascd_engaged"], False)
        # The observed pulse trains are the selections with more than one pulse.
        selections = [index for maps in result["selected_maps"].values() for index in maps]
        pulsed = list(dict.fromkeys(index for index in selections if index >= 2))
        held = result["held_attempt_map"]
        self.assertIn(
            "Operator observation in the same session establishes that the "
            + " and ".join(f"Map {index}" for index in pulsed)
            + " pulses light SET together with CRUISE, that the CANCEL hold on "
            f"Map {held} lights CRUISE alone, and that ASCD does not engage.",
            self.can_defs,
        )
        self.assertIn(
            f"In the {result['recorded_on']} road session a CANCEL hold on Map {held} "
            "shows state 5 for its whole length and lights CRUISE alone; "
            "`hardware-results.toml` records the observation under "
            f"`{KEY_2026_09_22}`.",
            _normalized(ROLLING_LAUNCH),
        )
        self.assertIn(f"`{KEY_2026_09_22}`", _normalized(SELECTOR))

    def test_dtc_read_is_the_uncleared_session_read(self):
        session = self.registry["can_telemetry"]["schema2_profile5_drive_2026_09_22"]
        self.assertIs(session["dtc_cleared_before_session"], False)
        self.assertEqual(session["dtc_read_after_session"], ["U1000", "U1001"])
        self.assertIn("not dated to the session", session["dtc_read_boundary"])
        self.assertIn(
            "can_telemetry.schema2_profile5_drive_2026_09_22", self.result["evidence_boundary"]
        )
        self.assertIn("TCM behavior is not observed", self.result["evidence_boundary"])

    @unittest.skipUnless(LOGS_2026_09_22.is_dir(), "road captures are local and untracked")
    def test_trace_reproduces_the_record(self):
        result = self.result
        path = LOGS_2026_09_22 / result["capture_name"]
        if not path.is_file():
            self.skipTest(f"missing capture: {path.name}")
        counts, total, selections = _trace_feedback(path)
        self.assertEqual(total, result["dashboard_frame_count"])
        self.assertEqual(
            [counts[value] for value in result["byte5_values"]], result["byte5_frame_counts"]
        )
        self.assertEqual(sum(counts.values()), total)
        self.assertEqual([row["taps"] for row in selections], result["selected_maps"][path.name])
        self.assertEqual(
            [round(row["commit_ms"] / 1000, 3) for row in selections],
            result["selection_commit_seconds"],
        )
        self.assertEqual(
            [len(row["pulse_starts_ms"]) for row in selections], result["map_feedback_pulse_counts"]
        )
        self.assertEqual(
            {frames for row in selections for frames in row["pulse_on_frames"]},
            {result["map_feedback_on_frames"]},
        )
        self.assertEqual(
            {frames for row in selections for frames in row["pulse_off_frames"]},
            {result["map_feedback_off_frames"]},
        )
        self.assertEqual(
            [round(row["pulse_starts_ms"][0] - row["commit_ms"], 1) for row in selections],
            result["map_feedback_first_on_after_release_ms"],
        )
        self.assertEqual(
            [
                round(
                    (row["pulse_starts_ms"][-1] - row["pulse_starts_ms"][0])
                    / (len(row["pulse_starts_ms"]) - 1),
                    1,
                )
                for row in selections
                if len(row["pulse_starts_ms"]) >= 2
            ],
            result["map_feedback_mean_period_ms"],
        )
        taps = [frames for row in selections for frames in row["tap_failed_frames"]]
        self.assertEqual(len(taps), result["gesture_tap_count"])
        self.assertEqual([min(taps), max(taps)], result["failed_held_attempt_frames"])
        self.assertEqual(sum(taps), result["gesture_tap_failed_frame_count"])


if __name__ == "__main__":
    unittest.main()
