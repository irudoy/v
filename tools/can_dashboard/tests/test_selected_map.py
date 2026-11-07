import unittest

from tools.can_dashboard import selected_map
from tools.can_dashboard.selected_map import (
    BUTTON_CANCEL,
    BUTTON_RELEASED,
    BUTTON_SET,
    MapTracker,
)


DISPLAY_OFF = 0x02
DISPLAY_ON = 0x42
DISPLAY_GESTURE = 0x52
FRAME_0X551_PERIOD = 0.1024
PHASE_SECONDS = 0.205


def started_tracker():
    tracker = MapTracker()
    tracker.activity(2.0)
    tracker.tick(2.0, 1)
    return tracker


def gesture(tracker, start, taps):
    """Hold SET, tap CANCEL taps times, release; return the release time."""
    time = start
    tracker.button(time, BUTTON_RELEASED)
    time += 0.1
    tracker.button(time, BUTTON_SET)
    for _ in range(taps):
        time += 0.15
        tracker.button(time, BUTTON_CANCEL)
        tracker.dashboard(time, DISPLAY_GESTURE)
        time += 0.1
        tracker.button(time, BUTTON_SET)
    time += 0.2
    tracker.button(time, BUTTON_RELEASED)
    return time


def feedback_frames(released, pulses, *, delay=0.09, until=3.0):
    """0x551 frames with pulses ON/OFF phases after a release."""
    first = released + delay
    time = released + 0.03
    frames = []
    while time < released + until:
        offset = time - first
        on = (
            0 <= offset < 2 * PHASE_SECONDS * pulses
            and offset % (2 * PHASE_SECONDS) < PHASE_SECONDS
        )
        frames.append((time, DISPLAY_ON if on else DISPLAY_OFF))
        time += FRAME_0X551_PERIOD
    return frames


def feedback(tracker, released, pulses, **options):
    frames = feedback_frames(released, pulses, **options)
    for time, code in frames:
        tracker.dashboard(time, code)
    return frames[-1][0]


class MapTrackerTest(unittest.TestCase):
    def test_the_map_is_unknown_before_any_observation(self):
        tracker = MapTracker()
        self.assertIsNone(tracker.number)
        self.assertEqual(tracker.reason, selected_map.UNKNOWN_REASON)

    def test_a_run_opening_after_bus_silence_is_a_controller_start(self):
        tracker = MapTracker()
        tracker.activity(5.0)
        tracker.tick(5.0, 3)
        self.assertEqual(tracker.number, 1)
        self.assertEqual(tracker.reason, "controller start observed")
        self.assertEqual(tracker.since, 5.0)

    def test_a_stream_joined_mid_run_leaves_the_map_unknown(self):
        tracker = MapTracker()
        tracker.activity(5.0)
        tracker.tick(5.0, 0x1234)
        tracker.activity(5.01)
        tracker.tick(5.01, 0x1235)
        self.assertIsNone(tracker.number)

    def test_a_tick_reset_inside_the_stream_is_a_controller_start(self):
        tracker = MapTracker()
        tracker.activity(5.0)
        tracker.tick(5.0, 0x4000)
        tracker.activity(5.2)
        tracker.tick(5.2, 2)
        self.assertEqual(tracker.number, 1)
        self.assertEqual(tracker.since, 5.2)

    def test_a_tick_step_the_receive_time_cannot_explain_is_a_controller_start(self):
        for before in (0x4000, 0x9000):
            with self.subTest(before=hex(before)):
                tracker = MapTracker()
                tracker.activity(5.0)
                tracker.tick(5.0, before)
                tracker.activity(5.8)
                tracker.tick(5.8, 0x0300)
                self.assertEqual(tracker.number, 1)
                self.assertEqual(tracker.since, 5.8)

    def test_a_reordered_group_is_not_a_controller_start(self):
        tracker = MapTracker()
        for time, tick in ((5.0, 0x4000), (5.01, 0x4001), (5.02, 0x4000)):
            tracker.activity(time)
            tracker.tick(time, tick)
        self.assertIsNone(tracker.number)

    def test_the_step_after_a_stale_group_counts_from_the_accepted_group(self):
        tracker = MapTracker()
        for time, tick in ((5.0, 0x4000), (5.01, 0x4001), (5.02, 0x3F00),
                           (5.03, 0x4002)):
            tracker.activity(time)
            tracker.tick(time, tick)
        self.assertIsNone(tracker.number)

    def test_the_first_run_after_a_silent_bus_restarts_the_map(self):
        tracker = started_tracker()
        released = gesture(tracker, 3.0, 3)
        end = feedback(tracker, released, 3)
        self.assertEqual(tracker.number, 3)
        tracker.activity(end + 1.5)
        tracker.tick(end + 1.5, 0x20)
        self.assertEqual(tracker.number, 1)

    def test_a_confirmed_gesture_selects_the_counted_map(self):
        for taps in range(1, 6):
            with self.subTest(taps=taps):
                tracker = started_tracker()
                released = gesture(tracker, 3.0, taps)
                feedback(tracker, released, taps)
                self.assertEqual(tracker.number, taps)
                noun = "pulse" if taps == 1 else "pulses"
                self.assertEqual(
                    tracker.reason,
                    f"selection confirmed by {taps} feedback {noun}",
                )

    def test_a_pulse_count_other_than_the_gesture_makes_the_map_unknown(self):
        tracker = started_tracker()
        released = gesture(tracker, 3.0, 3)
        feedback(tracker, released, 2)
        self.assertIsNone(tracker.number)
        self.assertEqual(
            tracker.reason,
            "selection of Map 3 answered by 2 pulses",
        )

    def test_a_gesture_without_feedback_keeps_the_map(self):
        tracker = started_tracker()
        released = gesture(tracker, 3.0, 2)
        feedback(tracker, released, 0)
        self.assertEqual(tracker.number, 1)
        self.assertEqual(tracker.reason, "controller start observed")

    def test_a_steady_on_state_after_a_gesture_is_not_counted(self):
        tracker = started_tracker()
        released = gesture(tracker, 3.0, 1)
        time = released + 0.05
        while time < released + 1.5:
            tracker.dashboard(time, DISPLAY_ON)
            time += FRAME_0X551_PERIOD
        self.assertIsNone(tracker.number)
        self.assertEqual(
            tracker.reason,
            "selection of Map 1 without countable pulses",
        )

    def test_selector_input_during_the_feedback_is_ignored(self):
        tracker = started_tracker()
        released = gesture(tracker, 3.0, 2)
        events = [
            (time, tracker.dashboard, code)
            for time, code in feedback_frames(released, 2)
        ]
        time = released + 0.2
        for code in (
            BUTTON_SET,
            BUTTON_CANCEL,
            BUTTON_SET,
            BUTTON_CANCEL,
            BUTTON_SET,
            BUTTON_RELEASED,
        ):
            events.append((time, tracker.button, code))
            time += 0.1
        for time, handler, code in sorted(events, key=lambda event: event[0]):
            handler(time, code)
        self.assertEqual(tracker.number, 2)

    def test_a_gesture_that_counts_past_five_is_abandoned(self):
        tracker = started_tracker()
        released = gesture(tracker, 3.0, 6)
        feedback(tracker, released, 5)
        self.assertEqual(tracker.number, 1)

    def test_a_held_cancel_is_not_a_selection(self):
        tracker = started_tracker()
        tracker.button(3.0, BUTTON_RELEASED)
        tracker.button(3.1, BUTTON_CANCEL)
        time = 3.15
        while time < 5.0:
            tracker.dashboard(time, DISPLAY_ON)
            time += FRAME_0X551_PERIOD
        tracker.button(5.0, BUTTON_RELEASED)
        feedback(tracker, 5.0, 0)
        self.assertEqual(tracker.number, 1)


if __name__ == "__main__":
    unittest.main()
