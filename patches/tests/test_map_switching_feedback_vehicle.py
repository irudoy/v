from collections import Counter
import csv
import hashlib
from pathlib import Path
import tomllib
import unittest

from kb import targets as kb_targets

from patches import map_switching_layout as layout_model
from patches import rolling_launch


ROOT = Path(__file__).resolve().parents[2]
HARDWARE_RESULTS = ROOT / "patches" / "hardware-results.toml"
CAN_DEFS = ROOT / "defs" / "JK08A.can.md"
VARS = ROOT / "defs" / "JK08A.vars.csv"
DIAGNOSTIC_BINDINGS = ROOT / "defs" / "JK08A.diagnostic-bindings.csv"
ROLLING_LAUNCH = ROOT / "patches" / "rolling-launch.md"
SELECTOR = ROOT / "patches" / "map-switching-selector.md"
STOCK_IMAGE = ROOT / "rom-images" / "23710-JK08A" / "1JK08A-20260726-stock.bin"
KEY = "map_switching.feedback_vehicle_2026_09_21"
KEY_2026_09_22 = "map_switching.feedback_vehicle_2026_09_22"
KEY_MAIN = "map_switching.ascd_main_vehicle_2026_09_21"
LOGS_2026_09_21 = ROOT / "tmp" / "logs-09-21"
LOGS_2026_09_22 = ROOT / "tmp" / "logs-09-22"
# The JK08A steering-switch chain: the decoder reads SWITCH_INPUT and accepts
# its one-hot code in SWITCH_DECODE, the sample window at SWITCH_WINDOW lies in
# the block that the scheduler copies from COPY_SOURCE to COPY_DESTINATION,
# and ROM8[SWITCH_OPTIONS] enables the window and selects the stable code.
SWITCH_INPUT = 0xFFFF3630
SWITCH_DECODE = 0xFFFF36D8
SWITCH_WINDOW = 0xFFFF2805
COPY_SOURCE = 0xFFFF277E
COPY_DESTINATION = 0xFFFF267A
COPY_LENGTH = 0x104
SWITCH_OPTIONS = 0x8B28
# The MAIN state that each press toggles and the flag of ASCD display state 4.
MAIN_STATE = 0xFFFF4251
DISPLAY_STATE_4 = 0xFFFF424E
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


def _trace_switch(path):
    """The offset, byte 2, and switch code of each frame 0x239 of a TRC."""
    from tools.logs import peak_trc_audit

    frames = peak_trc_audit.load_trace(path).frames
    return [
        (frame.offset_ms, frame.data[2], frame.data[3])
        for frame in frames
        if frame.can_id == 0x239 and len(frame.data) >= 4
    ]


def _u16(data, address):
    return int.from_bytes(data[address : address + 2], "big")


def _mov_l_literal(data, address):
    """The literal of the PC-relative mov.l at an address."""
    word = _u16(data, address)
    assert word >> 12 == 0xD, f"{address:08X}: {word:04X}"
    pool = (address & ~3) + 4 + (word & 0xFF) * 4
    return int.from_bytes(data[pool : pool + 4], "big")


def _mov_w_literal(data, address):
    """The sign-extended literal of the PC-relative mov.w at an address."""
    word = _u16(data, address)
    assert word >> 12 == 0x9, f"{address:08X}: {word:04X}"
    pool = address + 4 + (word & 0xFF) * 2
    return int.from_bytes(data[pool : pool + 2], "big", signed=True)


def _mov_immediate(data, address, register):
    """The zero-extended byte that mov #imm at an address loads into a register."""
    word = _u16(data, address)
    assert word >> 8 == 0xE0 | register, f"{address:08X}: {word:04X}"
    return word & 0xFF


def _branch_target(data, address):
    """The target of the bt, bf, bt/s, or bf/s at an address."""
    word = _u16(data, address)
    assert word >> 8 in (0x89, 0x8B, 0x8D, 0x8F), f"{address:08X}: {word:04X}"
    displacement = (word & 0xFF) - 0x100 if word & 0x80 else word & 0xFF
    return address + 4 + displacement * 2


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


class AscdMainVehicleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with HARDWARE_RESULTS.open("rb") as source:
            cls.registry = tomllib.load(source)
        section, name = KEY_MAIN.split(".")
        cls.result = cls.registry[section][name]
        cls.rom = STOCK_IMAGE.read_bytes()
        cls.symbols = kb_targets.canonical_symbols("map_switching")

    def _assert_words(self, *words):
        for address, word in words:
            with self.subTest(address=f"{address:08X}"):
                self.assertEqual(_u16(self.rom, address), word)

    def _assert_named_in_basis(self, *addresses):
        for address in addresses:
            with self.subTest(named=f"{address:08X}"):
                self.assertIn(f"0x{address:08X}", self.result["code_basis"])

    def test_observation_uses_the_registered_session_capture(self):
        result = self.result
        section, name = result["capture_registry"].split(".")
        captures = {row["capture_name"] for row in self.registry[section][name]}
        session = self.registry["can_telemetry"]["schema2_profile5_drive_2026_09_21"]
        self.assertEqual(result["image_sha256"], session["image_sha256"])
        self.assertEqual(result["recorded_on"], session["recorded_on"])
        self.assertIn(result["capture_name"], captures)
        section, name = result["feedback_record"].split(".")
        feedback = self.registry[section][name]
        self.assertEqual(feedback["cruise_main_capture"], result["capture_name"])
        self.assertEqual(feedback["image_sha256"], result["image_sha256"])

    def test_presses_and_toggles_are_consistent(self):
        result = self.result
        main = result["main_code"]
        released = result["released_code"]
        self.assertEqual(result["switch_codes"], sorted((main, released)))
        self.assertEqual(released, rolling_launch.BUTTON_RELEASED)
        # MAIN has a one-hot code of its own.
        self.assertEqual(main & (main - 1), 0)
        self.assertNotIn(main, (rolling_launch.BUTTON_SET, rolling_launch.BUTTON_CANCEL, released))
        count = result["main_press_count"]
        held = result["main_press_frames"]
        changes = result["main_state_change_frames_after_press"]
        starts = result["main_press_start_seconds"]
        self.assertEqual([len(held), len(changes), len(starts)], [count] * 3)
        self.assertEqual(starts, sorted(starts))
        for press, (frames, change) in enumerate(zip(held, changes, strict=True)):
            with self.subTest(press=press):
                self.assertLess(change, frames)
        self.assertLess(sum(held), result["switch_frame_count"])
        mask = result["main_state_mask"]
        sequence = result["byte2_sequence"]
        self.assertEqual(mask & (mask - 1), 0)
        self.assertEqual(len(sequence), count + 1)
        self.assertEqual(sorted(set(sequence)), result["byte2_values"])
        self.assertEqual({left ^ right for left, right in zip(sequence, sequence[1:])}, {mask})

    def test_decoded_code_reaches_the_stable_code(self):
        rom = self.rom
        stable = self.symbols["button_state"]
        # FUN_000D185C reads the switch word on both of its decode paths.
        for load, read in ((0x000D18AE, 0x000D18BA), (0x000D190E, 0x000D1918)):
            with self.subTest(read=f"{read:08X}"):
                self.assertEqual(_mov_l_literal(rom, load) + 4, SWITCH_INPUT)
                self.assertEqual(_u16(rom, read), 0x8522)  # mov.w @(4,r2),r0
        # It accepts the decode r8 when it equals the decode of the previous
        # run, which it keeps two bytes above the accepted code.
        self.assertEqual(_mov_l_literal(rom, 0x000D19D2), SWITCH_DECODE)
        self.assertEqual(_mov_l_literal(rom, 0x000D1A78), SWITCH_DECODE)
        self._assert_words(
            (0x000D1A04, 0x8442),  # mov.b @(2,r4),r0
            (0x000D1A06, 0x660C),  # extu.b r0,r6
            (0x000D1A08, 0x3680),  # cmp/eq r8,r6
            (0x000D1A0C, 0x2480),  # mov.b r8,@r4
            (0x000D1A7C, 0x6083),  # mov r8,r0
            (0x000D1A7E, 0x8042),  # mov.b r0,@(2,r4)
        )
        self.assertEqual(_branch_target(rom, 0x000D1A0A), 0x000D1A0E)
        # 0x000D0F44 moves four bytes of the window up by one byte and stores
        # the decode in its first byte while bit 0 of ROM8[0x8B28] is set.
        self.assertEqual(_mov_l_literal(rom, 0x000D0F92), SWITCH_OPTIONS)
        self.assertEqual(rom[SWITCH_OPTIONS] & 0x01, 0x01)
        self._assert_words(
            (0x000D0F94, 0x6020),  # mov.b @r2,r0
            (0x000D0F96, 0xC801),  # tst #0x01,r0
            (0x000D0FA2, 0x655C),  # extu.b r5,r5
            (0x000D0FA6, 0x3B5C),  # add r5,r11
            (0x000D0FB2, 0x7B03),  # add #3,r11
            (0x000D0FBE, 0x60B0),  # mov.b @r11,r0
            (0x000D0FC0, 0x80B1),  # mov.b r0,@(1,r11)
            (0x000D0FC2, 0x7BFF),  # add #-1,r11
            (0x000D0FE0, 0x4A10),  # dt r10
            (0x000D1092, 0x600C),  # extu.b r0,r0
            (0x000D1094, 0x6260),  # mov.b @r6,r2
            (0x000D1098, 0x0524),  # mov.b r2,@(r0,r5)
        )
        self.assertEqual(_branch_target(rom, 0x000D0F98), 0x000D0F9E)
        self.assertEqual(_mov_l_literal(rom, 0x000D0F9E), COPY_SOURCE)
        top = COPY_SOURCE + _mov_immediate(rom, 0x000D0FA0, 5) + 3
        self.assertEqual(top, SWITCH_WINDOW + 3)
        self.assertEqual(_mov_immediate(rom, 0x000D0FB6, 10), 4)
        self.assertEqual(_branch_target(rom, 0x000D0FE2), 0x000D0FB8)
        self.assertEqual(_mov_l_literal(rom, 0x000D108C), SWITCH_DECODE)
        self.assertEqual(_mov_l_literal(rom, 0x000D1090), COPY_SOURCE)
        self.assertEqual(COPY_SOURCE + _mov_immediate(rom, 0x000D108E, 0), SWITCH_WINDOW)
        # FUN_00020DFE copies the block through FUN_00022558, which takes the
        # destination in r1, the source in r2, and the length in r0.
        self.assertEqual(_mov_l_literal(rom, 0x00020EEA), 0x00022558)
        self.assertEqual(_mov_l_literal(rom, 0x00020FB2), COPY_DESTINATION)
        self.assertEqual(_mov_l_literal(rom, 0x00020FCA), COPY_SOURCE)
        self.assertEqual(_mov_immediate(rom, 0x00020FC8, 0) << 2, COPY_LENGTH)
        self._assert_words(
            (0x00020FCC, 0x4B0B),  # jsr @r11
            (0x00020FCE, 0x4008),  # shll2 r0
        )
        self.assertLess(top + 1 - COPY_SOURCE, COPY_LENGTH)
        latch = COPY_DESTINATION + SWITCH_WINDOW - COPY_SOURCE
        # FUN_000CF020 stores the first latched sample in the stable code only
        # when each pair of adjacent samples of the five is equal.
        samples = [
            _mov_l_literal(rom, load) + _mov_immediate(rom, offset, 0)
            for load, offset in (
                (0x000CF166, 0x000CF168),
                (0x000CF166, 0x000CF16E),
                (0x000CF166, 0x000CF17E),
                (0x000CF192, 0x000CF190),
                (0x000CF1A0, 0x000CF1A2),
            )
        ]
        self.assertEqual(samples, [latch + index for index in range(5)])
        self._assert_words(
            (0x000CF16C, 0x054C),  # mov.b @(r0,r4),r5
            (0x000CF178, 0x3570),  # cmp/eq r7,r5
            (0x000CF18A, 0x3370),  # cmp/eq r7,r3
            (0x000CF19C, 0x3370),  # cmp/eq r7,r3
            (0x000CF1AA, 0x3740),  # cmp/eq r4,r7
            (0x000CF1B2, 0x0354),  # mov.b r5,@(r0,r3)
        )
        for branch in (0x000CF17A, 0x000CF18C, 0x000CF19E, 0x000CF1AC):
            with self.subTest(branch=f"{branch:08X}"):
                self.assertEqual(_branch_target(rom, branch), 0x000CF1B4)
        self.assertEqual(
            _mov_l_literal(rom, 0x000CF1AE) + _mov_w_literal(rom, 0x000CF1B0), stable
        )
        self._assert_named_in_basis(
            SWITCH_INPUT,
            SWITCH_DECODE,
            0x000D1A0C,
            SWITCH_WINDOW,
            SWITCH_WINDOW + 3,
            0x000D1098,
            COPY_SOURCE,
            COPY_DESTINATION,
            0x00020FCC,
            latch,
            latch + 4,
            stable,
            0x000CF1B2,
        )

    def test_main_switch_bit_follows_bit_0_of_the_stable_code(self):
        rom = self.rom
        main = self.result["main_code"]
        bit = 1 << kb_targets.bit("ascd_state/ram", "7mfk", "main")
        # Clear bit 7 of ROM8[0x8B28] selects the stable code as the source.
        self.assertEqual(_mov_l_literal(rom, 0x000D01CC), SWITCH_OPTIONS)
        self.assertEqual(rom[SWITCH_OPTIONS] & 0x80, 0)
        self._assert_words(
            (0x000D01D2, 0x6030),  # mov.b @r3,r0
            (0x000D01D4, 0xC880),  # tst #0x80,r0
            (0x000D01DA, 0x009C),  # mov.b @(r0,r9),r0
            (0x000D01DC, 0xC800 | main),  # tst #main,r0
            (0x000D01E0, 0xA00C),  # bra 0x000D01FC
            (0x000D01EC, 0x6063),  # mov r6,r0
            (0x000D01EE, 0xA007),  # bra 0x000D0200
            (0x000D01F0, 0xCB00 | bit),  # or #bit,r0
            (0x000D01FC, 0x6063),  # mov r6,r0
            (0x000D01FE, 0xC900 | (~bit & 0xFF)),  # and #~bit,r0
            (0x000D0200, 0x80C9),  # mov.b r0,@(9,r12)
        )
        self.assertEqual(_branch_target(rom, 0x000D01D6), 0x000D01E4)
        self.assertEqual(_branch_target(rom, 0x000D01DE), 0x000D01EC)
        self.assertEqual(
            _mov_l_literal(rom, 0x000D012C) + _mov_w_literal(rom, 0x000D01D8),
            self.symbols["button_state"],
        )
        self.assertEqual(_mov_l_literal(rom, 0x000CFFFE) + 9, self.symbols["ascd_state"])
        self._assert_named_in_basis(0x000D01F0, 0x000D01FE, self.symbols["ascd_state"])

    def test_serializer_sends_the_decode_and_the_main_state(self):
        rom = self.rom
        mask = self.result["main_state_mask"]
        self.assertEqual(_mov_l_literal(rom, 0x000C5BE4), SWITCH_DECODE)
        self.assertEqual(_mov_l_literal(rom, 0x000C5B14) + 5, MAIN_STATE)
        # Bytes 3 and 2 of the payload at r14 + 2.
        self._assert_words(
            (0x000C5BEC, 0x62E3),  # mov r14,r2
            (0x000C5BEE, 0x6050),  # mov.b @r5,r0
            (0x000C5BF0, 0x7202),  # add #2,r2
            (0x000C5BF4, 0x8023),  # mov.b r0,@(3,r2)
            (0x000C5B3E, 0x66E3),  # mov r14,r6
            (0x000C5B40, 0x8455),  # mov.b @(5,r5),r0
            (0x000C5B42, 0x7602),  # add #2,r6
            (0x000C5B44, 0xC800 | mask),  # tst #mask,r0
            (0x000C5B46, 0x8462),  # mov.b @(2,r6),r0
            (0x000C5B4A, 0xC900 | (~mask & 0xFF)),  # and #~mask,r0
            (0x000C5B4C, 0xCB00 | mask),  # or #mask,r0
            (0x000C5B50, 0x8062),  # mov.b r0,@(2,r6)
        )
        self.assertEqual(_branch_target(rom, 0x000C5B48), 0x000C5B4E)
        self._assert_named_in_basis(0x000C5ABE, 0x000C5BF4, MAIN_STATE, 0x000C5B50)

    def test_gate_inputs_exclude_the_toggled_main_state(self):
        for feature in ("map_switching", "rolling_launch"):
            symbols = kb_targets.canonical_symbols(feature)
            with self.subTest(feature=feature):
                self.assertEqual(symbols["ascd_state"], self.symbols["ascd_state"])
                self.assertTrue({MAIN_STATE, DISPLAY_STATE_4}.isdisjoint(symbols.values()))

    def test_gate_names_describe_the_pressed_main_switch(self):
        bit = 1 << kb_targets.bit("ascd_state/ram", "7mfk", "main")
        self.assertEqual(rolling_launch.MAIN_PRESSED_MASK, bit)
        self.assertEqual(rolling_launch.AbortReason(6).name, "MAIN_PRESSED")
        self.assertEqual(rolling_launch.Flag(1 << 4).name, "MAIN_RELEASED")
        self.assertIn(
            "6. The MAIN switch bit of the stock ASCD flag byte is clear.",
            _normalized(ROLLING_LAUNCH),
        )

    def test_published_statements_follow_the_record(self):
        result = self.result
        main = result["main_code"]
        released = result["released_code"]
        mask = result["main_state_mask"]
        changes = result["main_state_change_frames_after_press"]
        main_state = f"`0x{MAIN_STATE:08X}.bit{mask.bit_length() - 1}`"
        can_defs = _normalized(CAN_DEFS)
        for statement in (
            f"The {result['recorded_on']} stationary CRUISE MAIN capture establishes "
            f"`0x239` byte 3 value `0x{main:02X}` for MAIN.",
            f"Byte 3 reads `0x{main:02X}` only during the "
            f"{NUMBER_WORDS[result['main_press_count']]} MAIN presses, for "
            f"{_series(result['main_press_frames'])} frames, and `0x{released:02X}` in "
            "every other frame.",
            f"Byte 2 changes only in bit {mask.bit_length() - 1}, once within each press "
            f"and {min(changes)} or {max(changes)} frames after its first `0x{main:02X}` "
            f"frame, so each MAIN press toggles {main_state}.",
            f"`0x239` byte 2 bit {mask.bit_length() - 1} receives {main_state}",
            f"`{KEY_MAIN}`",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, can_defs)
        selector = _normalized(SELECTOR)
        for statement in (
            f"| `0x{main:02X}` | MAIN |",
            f"Bit {main.bit_length() - 1} of the stable switch code is the MAIN code "
            f"`0x{main:02X}`",
            f"The MAIN state that each press toggles, {main_state},",
            "are not selector inputs",
            f"`{KEY_MAIN}`",
            "Gestures are made with the cruise MAIN state off.",
            "The selector does not read the state",
            "The same rule covers the CANCEL hold of Rolling Launch.",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, selector)
        launch = _normalized(ROLLING_LAUNCH)
        for statement in (
            "On JK08A, gate 6 follows the MAIN switch itself: the MAIN switch bit is set "
            "only while MAIN is pressed.",
            f"The MAIN state that each press toggles, {main_state},",
            "are not gate inputs",
            "The CANCEL hold is therefore made with the cruise MAIN state off",
        ):
            with self.subTest(statement=statement):
                self.assertIn(statement, launch)
        with VARS.open(encoding="utf-8", newline="") as source:
            variables = {row["addr"]: row for row in csv.DictReader(source)}
        stable = variables[f"{self.symbols['button_state']:08x}"]
        self.assertNotIn(f"spec:hardware-results:{KEY_MAIN}",
                         [token.strip() for token in stable["evidence"].split(";")])
        self.assertEqual(stable["confidence"], "code")
        self.assertIn(KEY_MAIN, stable["note"])
        self.assertIn(f"accepted code 0x{main:02X} to physical MAIN presses", stable["note"])
        self.assertIn("Those RAM/flag bindings are code-derived", stable["note"])
        self.assertIn(
            f"The toggled state {MAIN_STATE:08x}.bit"
            f"{mask.bit_length() - 1}",
            stable["note"],
        )
        with DIAGNOSTIC_BINDINGS.open(encoding="utf-8", newline="") as source:
            bindings = {row["id"]: row for row in csv.DictReader(source)}
        self.assertIn(
            "the MAIN bit is set only while the MAIN switch is pressed",
            bindings["ascd-steering-switch-did-130d"]["note"],
        )

    @unittest.skipUnless(LOGS_2026_09_21.is_dir(), "road captures are local and untracked")
    def test_trace_reproduces_the_record(self):
        result = self.result
        path = LOGS_2026_09_21 / result["capture_name"]
        if not path.is_file():
            self.skipTest(f"missing capture: {path.name}")
        section, name = result["capture_registry"].split(".")
        registered = next(
            row for row in self.registry[section][name] if row["capture_name"] == path.name
        )
        self.assertEqual(
            hashlib.sha256(path.read_bytes()).hexdigest(), registered["capture_sha256"]
        )
        switch = _trace_switch(path)
        codes = [code for _, _, code in switch]
        self.assertEqual(len(switch), result["switch_frame_count"])
        self.assertEqual(sorted(set(codes)), result["switch_codes"])
        presses = _runs([code == result["main_code"] for code in codes])
        self.assertEqual(len(presses), result["main_press_count"])
        self.assertEqual([stop - begin for begin, stop in presses], result["main_press_frames"])
        self.assertEqual(
            [round(switch[begin][0] / 1000, 3) for begin, _ in presses],
            result["main_press_start_seconds"],
        )
        byte2 = [value for _, value, _ in switch]
        changes = [index for index in range(1, len(byte2)) if byte2[index] != byte2[index - 1]]
        self.assertEqual(sorted(set(byte2)), result["byte2_values"])
        self.assertEqual([byte2[0], *(byte2[index] for index in changes)], result["byte2_sequence"])
        self.assertEqual(len(changes), len(presses))
        for (begin, stop), change in zip(presses, changes, strict=True):
            with self.subTest(change=change):
                self.assertLessEqual(begin, change)
                self.assertLess(change, stop)
        self.assertEqual(
            [change - begin for (begin, _), change in zip(presses, changes, strict=True)],
            result["main_state_change_frames_after_press"],
        )


if __name__ == "__main__":
    unittest.main()
