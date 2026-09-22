"""The README states the replay, map, and timer constants the code runs."""

from pathlib import Path
import tempfile
import unittest

from tools.can_dashboard import acceleration, replay, selected_map
from tools.logs.can_telemetry import PRODUCER_RUN_TICK_MAX

try:
    import tkinter as tk
    from tools.can_dashboard import app, widgets
except ImportError:  # pragma: no cover - Tk is unavailable
    app = None

try:
    ROOT = tk.Tk() if app is not None else None
    if ROOT is not None:
        ROOT.withdraw()
except tk.TclError:  # pragma: no cover - no display
    ROOT = None


README = Path(__file__).resolve().parents[1] / "README.md"


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


def readme_text():
    return " ".join(README.read_text(encoding="utf-8").split())


def header_button_rows():
    """Rows of the tool button table, keyed by their Button cell."""
    rows = {}
    lines = iter(README.read_text(encoding="utf-8").splitlines())
    for line in lines:
        if line.startswith("| Button | Icon |"):
            next(lines)
            break
    for line in lines:
        if not line.startswith("| "):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        rows[cells[0]] = cells
    return rows


def tool_buttons(widget):
    found = []
    for child in widget.winfo_children():
        if isinstance(child, widgets.ToolButton):
            found.append(child)
        found.extend(tool_buttons(child))
    return found


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

    @unittest.skipIf(ROOT is None, "Tk is unavailable")
    def test_button_icons(self):
        self.assert_states(
            f"The icon is {widgets.ToolButton.ICON_EM:g} em on a side",
        )
        window = tk.Toplevel(ROOT)
        window.withdraw()
        self.addCleanup(window.destroy)
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        args = app.build_parser().parse_args([
            "--no-auto-connect",
            "--settings",
            str(Path(directory.name) / "settings.json"),
        ])
        dashboard = app.DashboardApp(window, args)
        dashboard.open_hero_picker()
        dashboard.open_feed_dialog()
        rows = header_button_rows()
        text = readme_text()
        buttons = tool_buttons(window)
        self.assertGreater(len(buttons), 25)
        for button in buttons:
            caption, icon = button.cget("text"), button.cget("icon")
            row = next(
                (
                    cells
                    for key, cells in rows.items()
                    if f"`{caption}`" in key
                ),
                None,
            )
            with self.subTest(caption=caption):
                if row is not None:
                    self.assertIn(f"`{icon}`", row[1])
                elif button is dashboard.speed_button:
                    self.assertIn(f"`{icon}` for the speed button", text)
                else:
                    self.assertIn(f"`{icon}` for `{caption}`", text)
        stream = rows["`STREAM`"][1]
        self.assertIn(f"`{app.STREAM_ICONS['stop']}` while STOP is offered", stream)
        record = rows["`REC`"][1]
        self.assertIn(f"`{app.RECORD_ICONS[True]}` while recording", record)
        self.assertEqual(
            rows["`LIGHT` / `DARK`"][1],
            f"`{app.THEME_ICONS['dark']}` / `{app.THEME_ICONS['light']}`",
        )
        self.assertIn(
            f"`{app.PLAY_ICONS[True]}` for `{app.PLAY_CAPTIONS[True]}`", text
        )


if __name__ == "__main__":
    unittest.main()
