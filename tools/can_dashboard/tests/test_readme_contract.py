"""The README states the replay, map, and timer constants the code runs."""

from pathlib import Path
import unittest

from tools.can_dashboard import acceleration, replay, selected_map
from tools.logs.can_telemetry import PRODUCER_RUN_TICK_MAX

try:
    from tools.can_dashboard import app
except ImportError:  # pragma: no cover - Tk is unavailable
    app = None


README = Path(__file__).resolve().parents[1] / "README.md"


def readme_text():
    return " ".join(README.read_text(encoding="utf-8").split())


class ReadmeContractTest(unittest.TestCase):
    def assert_states(self, *phrases):
        text = readme_text()
        for phrase in phrases:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_replay_constants(self):
        speeds = [f"{speed:g}x" for speed in replay.SPEEDS]
        self.assert_states(
            f"cycles through {', '.join(speeds[:-1])}, and {speeds[-1]}",
            f"The model replays the {replay.WARMUP_SECONDS:g} s before "
            "the target",
            f"every {replay.CHECKPOINT_SECONDS:g} s of source time",
        )

    @unittest.skipIf(app is None, "Tk is unavailable")
    def test_replay_step(self):
        self.assert_states(
            f"move {app.REPLAY_STEP_SECONDS:g} s back or forward",
        )

    def test_selected_map_constants(self):
        self.assert_states(
            f"tick16 at most `0x{PRODUCER_RUN_TICK_MAX:02X}` after at least "
            f"{selected_map.BUS_SILENCE_SECONDS:g} s without any frame",
            f"within {selected_map.FEEDBACK_START_SECONDS:g} s of the release",
            "ON phases of at most "
            f"{selected_map.FEEDBACK_PHASE_MAX_SECONDS:g} s",
            f"closed by {selected_map.FEEDBACK_END_SECONDS:g} s of state 0",
            f"display state {selected_map.DISPLAY_STATE_ON} on frame `0x551`",
        )

    def test_acceleration_constants(self):
        timer = acceleration.AccelerationTimer()
        zero, hundred = timer.run("0-100"), timer.run("100-200")
        self.assert_states(
            f"arms below {hundred.arm_below_kmh:g} km/h",
            f"crosses {hundred.start_kmh:g} km/h",
            f"falls more than {acceleration.DROP_KMH:g} km/h below its peak",
            f"gains nothing for {acceleration.STALL_SECONDS:g} s",
            f"exceeds {zero.max_seconds:g} s for 0-100 or "
            f"{hundred.max_seconds:g} s for 100-200",
            "samples stop for more than "
            f"{acceleration.MAX_SAMPLE_GAP_SECONDS:g} s",
        )


if __name__ == "__main__":
    unittest.main()
