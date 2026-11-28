from pathlib import Path
import tempfile
from tools.can_dashboard.tests.tk_support import require_tk

tk = require_tk()
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
        return [
            panel
            for panel, _metrics in self.dashboard.data_panels
            if isinstance(panel, app.DataPanel)
        ]

    def single_column_panels(self):
        return [panel for panel in self.panels() if not panel._multi_column]

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
                widget.winfo_pixels(widget.cget("highlightthickness")),
                0,
                str(widget),
            )
        self.assertGreater(labels, 10)

    def test_data_panels_render_on_one_canvas_with_shared_fonts(self):
        panels = self.panels()
        self.assertTrue(panels)
        title_fonts = set()
        label_fonts = set()
        value_fonts = set()
        for panel in panels:
            self.assertEqual(panel.winfo_children(), [panel.canvas])
            title_fonts.add(id(panel._title_font))
            label_fonts.add(id(panel._label_font))
            value_fonts.add(id(panel._value_font))
        self.assertEqual(len(title_fonts), 1)
        self.assertEqual(len(label_fonts), 1)
        self.assertEqual(len(value_fonts), 1)

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
                    button.face.winfo_reqwidth() + 2,
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

    def test_tab_panels_share_one_row_down_to_the_cell_minimum(self):
        for panels, (_tab, definitions) in zip(
                self.dashboard.panel_grids, self.dashboard.presentation.tabs):
            if isinstance(panels, app.DynamicTabView):
                panels.layout(1482)
                self.assertEqual(panels.columns, app.DYNAMIC_MAX_COLUMNS)
                self.assertIsInstance(panels.strip, app.PageConfigStrip)
                self.assertIsInstance(panels.panel, app.DataPanel)
                self.assertTrue(panels.panel._multi_column)
                continue
            count = len(definitions)
            panels.layout(1482)
            self.assertEqual(panels.columns, count)
            panels.layout(row_of(panels, count))
            self.assertEqual(panels.columns, count)

    def test_a_narrower_window_balances_two_rows_before_folding_further(self):
        for panels, (_tab, definitions) in zip(
                self.dashboard.panel_grids, self.dashboard.presentation.tabs):
            if isinstance(panels, app.DynamicTabView):
                panels.layout(700)
                self.assertEqual(panels.columns, 2)
                panels.layout(400)
                self.assertEqual(panels.columns, 1)
                continue
            count = len(definitions)
            panels.layout(row_of(panels, count) - 1)
            self.assertEqual(panels.columns, (count + 1) // 2)
            panels.layout(row_of(panels, 2))
            self.assertEqual(panels.columns, 2)
            panels.layout(row_of(panels, 2) - 1)
            self.assertEqual(panels.columns, 1)

    def test_a_wide_panel_shows_full_labels_and_the_full_value_reserve(self):
        for panel in self.single_column_panels():
            panel.fit(600)
            for metric in panel.metrics:
                self.assertEqual(panel.shown_label(metric.key), metric.label)
            self.assertEqual(panel._value_limit, app.PANEL_VALUE_WIDTH)

    def test_a_fitted_panel_requests_less_than_its_width(self):
        for panel in self.panels():
            for width in range(app.PANEL_MIN_WIDTH, 420):
                panel.fit(width)
                panel.update_idletasks()
                self.assertLessEqual(
                    panel.winfo_reqwidth(), width - app.PANEL_FIT_SLACK, width
                )

    def test_values_give_way_before_the_labels(self):
        for panel in self.single_column_panels():
            panel.fit(600)
            chrome = 2 * (1 + app.PANEL_PAD) + app.PANEL_GAP + app.PANEL_FIT_SLACK
            panel.fit(chrome + panel._widest_label + app.PANEL_VALUE_MIN_WIDTH)
            for metric in panel.metrics:
                self.assertEqual(panel.shown_label(metric.key), metric.label)
            self.assertEqual(panel._value_limit, app.PANEL_VALUE_MIN_WIDTH)

    def test_the_narrowest_panel_fits_its_rows_and_preserves_full_tooltip_labels(self):
        elided = 0
        for panel in self.single_column_panels():
            panel.fit(app.PANEL_MIN_WIDTH)
            tooltips = [panel.label_tooltip(metric) for metric in panel.metrics]
            self.assertEqual(len(set(tooltips)), len(tooltips), tooltips)
            for metric in panel.metrics:
                shown = panel.shown_label(metric.key)
                elided += shown != metric.label
                self.assertLessEqual(
                    panel._label_font.measure(shown),
                    panel._label_limit,
                    metric.label,
                )
                self.assertTrue(
                    panel.label_tooltip(metric).startswith(metric.label + "\n\n"),
                    metric.label,
                )
        self.assertGreater(elided, 0)

    def test_a_widened_panel_restores_its_labels(self):
        for panel in self.single_column_panels():
            panel.fit(app.PANEL_MIN_WIDTH)
            panel.fit(600)
            for metric in panel.metrics:
                self.assertEqual(panel.shown_label(metric.key), metric.label)


if __name__ == "__main__":
    unittest.main()
