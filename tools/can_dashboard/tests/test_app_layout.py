from pathlib import Path
import tempfile
import tkinter as tk
import unittest

from tools.can_dashboard import PRODUCT_NAME, PRODUCT_SHORT_NAME, __version__
from tools.can_dashboard import app
from tools.can_dashboard import widgets


try:
    ROOT = tk.Tk()
    ROOT.withdraw()
except tk.TclError:
    ROOT = None

TK_AVAILABLE = ROOT is not None
PANEL_SPACING = 6


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


def row_of(panels, columns):
    return columns * app.PANEL_MIN_WIDTH + (columns - 1) * PANEL_SPACING


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class WindowLayoutTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.window = tk.Toplevel(ROOT)
        self.window.withdraw()
        self.addCleanup(self._close)
        args = app.build_parser().parse_args([
            "--no-auto-connect",
            "--settings",
            str(Path(directory.name) / "settings.json"),
        ])
        args.publish_udp = None
        self.dashboard = app.DashboardApp(self.window, args)
        self.window.update_idletasks()

    def _close(self):
        if self.window.winfo_exists():
            self.window.destroy()

    def panels(self):
        return [panel for panel, _metrics in self.dashboard.data_panels]

    def test_header_title_is_the_short_name_with_the_version(self):
        self.assertEqual(PRODUCT_SHORT_NAME, "VQCT")
        self.assertEqual(
            self.dashboard.title_label.cget("text"),
            f"VQCT v{__version__}",
        )
        self.assertEqual(self.window.title(), f"{PRODUCT_NAME} v{__version__}")

    def test_header_items_are_placed_inside_the_header_bar(self):
        header = self.dashboard.title_label.master
        self.assertIsInstance(header, widgets.FlowBar)
        header.layout(1400)
        for item in header.winfo_children():
            with self.subTest(item=str(item)):
                self.assertEqual(item.winfo_manager(), "place")
                self.assertEqual(str(item.place_info()["in"]), str(header))

    def test_no_label_of_the_window_draws_a_highlight_ring(self):
        pending = [self.window]
        labels = 0
        while pending:
            widget = pending.pop()
            pending.extend(widget.winfo_children())
            if widget.winfo_class() != "Label":
                continue
            labels += 1
            self.assertEqual(
                int(widget.cget("highlightthickness")),
                0,
                str(widget),
            )
        self.assertGreater(labels, 50)

    def test_tool_buttons_keep_their_border_outside_the_label(self):
        buttons = [
            self.dashboard.source_button,
            self.dashboard.stream_button,
            self.dashboard.record_button,
            self.dashboard.theme_button,
            *self.dashboard.tab_buttons,
        ]
        for button in buttons:
            with self.subTest(button=button.cget("text")):
                self.assertIsInstance(button, widgets.ToolButton)
                self.assertEqual(button.winfo_class(), "Frame")
                self.assertEqual(
                    button.winfo_reqwidth(),
                    button.label.winfo_reqwidth() + 2,
                )

    def test_a_hero_card_asks_for_a_width_its_value_cannot_change(self):
        card = next(iter(self.dashboard.hero_cards.values()))
        card.fit(160)
        self.window.update_idletasks()
        requested = card.winfo_reqwidth()
        card.update_value("HIGH DETONATION")
        self.window.update_idletasks()
        self.assertEqual(card.winfo_reqwidth(), requested)
        self.assertTrue(card.value_label.cget("text").endswith(widgets.ELLIPSIS))

    def test_the_value_row_holds_the_height_of_its_labels(self):
        card = next(iter(self.dashboard.hero_cards.values()))
        for width in (400, 169, 80):
            card.fit(width)
            self.window.update_idletasks()
            expected = card.value_label.winfo_reqheight()
            if card.unit_shown:
                expected = max(
                    expected,
                    card.unit_label.winfo_reqheight() + app.HERO_UNIT_TOP,
                )
            with self.subTest(width=width):
                self.assertEqual(int(card.value_row.cget("height")), expected)

    def test_a_long_value_leaves_the_hero_row_its_width(self):
        row = self.dashboard.hero_row
        for card in row.cards:
            card.fit(160)
        self.window.update_idletasks()
        requested = row.winfo_reqwidth()
        for card in row.cards:
            card.update_value("HIGH DETONATION")
        self.window.update_idletasks()
        self.assertEqual(row.winfo_reqwidth(), requested)

    def test_panel_minimum_ignores_the_panel_content(self):
        for panels in self.dashboard.panel_grids:
            self.assertEqual(
                panels.minimum_column_width(),
                app.PANEL_MIN_WIDTH,
            )

    def test_four_panels_share_one_row_down_to_the_cell_minimum(self):
        for panels in self.dashboard.panel_grids:
            panels.layout(1482)
            self.assertEqual(panels.columns, 4)
            panels.layout(row_of(panels, 4))
            self.assertEqual(panels.columns, 4)

    def test_a_narrower_window_folds_the_panels_into_two_rows_of_two(self):
        for panels in self.dashboard.panel_grids:
            panels.layout(row_of(panels, 4) - 1)
            self.assertEqual(panels.columns, 2)
            panels.layout(row_of(panels, 2))
            self.assertEqual(panels.columns, 2)
            panels.layout(row_of(panels, 2) - 1)
            self.assertEqual(panels.columns, 1)

    def test_a_wide_panel_shows_full_labels_and_the_full_value_reserve(self):
        for panel in self.panels():
            panel.fit(600)
            for label, full in panel.labels:
                self.assertEqual(label.cget("text"), full)
            for field in panel.fields:
                self.assertEqual(
                    field.winfo_reqwidth(),
                    field.outer_width(app.PANEL_VALUE_WIDTH),
                )

    def test_values_give_way_before_the_labels(self):
        for panel in self.panels():
            panel.fit(600)
            widest = max(label.winfo_reqwidth() for label, _full in panel.labels)
            field = panel.fields[0]
            floor = field.outer_width(app.PANEL_VALUE_MIN_WIDTH)
            chrome = 2 * (1 + app.PANEL_PAD + app.PANEL_GAP)
            panel.fit(chrome + widest + floor)
            for label, full in panel.labels:
                self.assertEqual(label.cget("text"), full)
            for field in panel.fields:
                self.assertEqual(field.winfo_reqwidth(), floor)

    def test_the_narrowest_panel_fits_its_rows_and_keeps_labels_distinct(self):
        elided = 0
        chrome = 2 * (1 + app.PANEL_PAD + app.PANEL_GAP)
        for panel in self.panels():
            panel.fit(app.PANEL_MIN_WIDTH)
            shown = [label.cget("text") for label, _full in panel.labels]
            self.assertEqual(len(set(shown)), len(shown), shown)
            for (label, full), field in zip(panel.labels, panel.fields):
                elided += label.cget("text") != full
                self.assertLessEqual(
                    chrome + label.winfo_reqwidth() + field.winfo_reqwidth(),
                    app.PANEL_MIN_WIDTH,
                    full,
                )
                self.assertTrue(
                    label.tooltip.provider().startswith(full + "\n\n"),
                    full,
                )
        self.assertGreater(elided, 0)

    def test_a_widened_panel_restores_its_labels(self):
        for panel in self.panels():
            panel.fit(app.PANEL_MIN_WIDTH)
            panel.fit(600)
            for label, full in panel.labels:
                self.assertEqual(label.cget("text"), full)


if __name__ == "__main__":
    unittest.main()
