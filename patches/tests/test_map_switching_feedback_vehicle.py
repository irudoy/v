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
# Frame 0x551 leaves the serializer on every tenth 10.24 ms invocation.
SERIALIZER_CALLS_PER_FRAME = 10
NUMBER_WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven")


def _normalized(path):
    return " ".join(path.read_text(encoding="utf-8").split())


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
        cruise_alone_open = (
            result["failed_held_attempt_lamp_status"] == "untested"
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


if __name__ == "__main__":
    unittest.main()
