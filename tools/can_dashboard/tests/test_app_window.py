import json
from pathlib import Path
import sys
import tempfile
import tkinter as tk
import unittest

from tools.can_dashboard import app
from tools.can_dashboard import settings
from tools.can_dashboard import widgets


try:
    ROOT = tk.Tk()
    ROOT.withdraw()
except tk.TclError:
    ROOT = None

TK_AVAILABLE = ROOT is not None


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


class HeroCatalogTest(unittest.TestCase):
    def test_default_hero_row_leaves_the_selector_out(self):
        self.assertNotIn("gear", app.DEFAULT_HERO_KEYS)
        self.assertTrue(app.DEFAULT_HERO_KEYS)
        self.assertLessEqual(len(app.DEFAULT_HERO_KEYS), settings.HERO_LIMIT)

    def test_default_hero_keys_come_from_the_catalog(self):
        self.assertEqual(
            settings.normalize_hero(app.DEFAULT_HERO_KEYS, app.HERO_CATALOG),
            app.DEFAULT_HERO_KEYS,
        )

    def test_selector_stays_available_as_a_card_and_as_a_panel_row(self):
        self.assertIn("gear", app.HERO_CATALOG)
        panel_keys = {
            metric.key
            for _title, metrics in app.PANELS
            for metric in metrics
        }
        self.assertIn("gear", panel_keys)

    def test_every_panel_metric_is_offered_once(self):
        keys = [choice.key for choice in app.HERO_CHOICES]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertEqual(set(keys), set(app.HERO_CATALOG))
        for _tab, panels in app.TABS:
            for _title, metrics in panels:
                for metric in metrics:
                    self.assertIn(metric.key, app.HERO_CATALOG)


class PaletteTest(unittest.TestCase):
    def test_both_themes_define_the_same_roles(self):
        self.assertEqual(set(app.PALETTES), set(settings.THEMES))
        self.assertEqual(app.DARK.bg, "#000000")
        self.assertEqual(app.LIGHT.bg, "#ffffff")
        self.assertEqual(len(app.DARK.traces), len(app.LIGHT.traces))

    def test_button_colors_cover_every_tool_button_role(self):
        for palette in app.PALETTES.values():
            with self.subTest(theme=palette.name):
                self.assertEqual(
                    set(palette.button_colors()),
                    {
                        "face",
                        "hover",
                        "text",
                        "border",
                        "focus",
                        "lit",
                        "record",
                        "lit_text",
                    },
                )

    def test_theme_captions_name_the_other_theme(self):
        self.assertEqual(app.THEME_CAPTIONS, {"dark": "LIGHT", "light": "DARK"})


class SettingsArgumentTest(unittest.TestCase):
    def test_settings_path_is_optional(self):
        self.assertIsNone(app.build_parser().parse_args([]).settings)

    def test_settings_path_is_parsed_as_a_path(self):
        args = app.build_parser().parse_args(["--settings", "tmp/ui.json"])
        self.assertEqual(args.settings, Path("tmp/ui.json"))


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class DashboardWindowTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "settings.json"
        self.window = tk.Toplevel(ROOT)
        self.window.withdraw()
        self.addCleanup(self._close)

    def _close(self):
        if self.window.winfo_exists():
            self.window.destroy()

    def dashboard(self, *extra, publish_udp=None):
        args = app.build_parser().parse_args(
            ["--no-auto-connect", "--settings", str(self.path), *extra]
        )
        args.publish_udp = publish_udp
        dashboard = app.DashboardApp(self.window, args)
        self.addCleanup(self._close_feed, dashboard)
        self.window.update_idletasks()
        return dashboard

    @staticmethod
    def _close_feed(dashboard):
        if dashboard.feed is not None:
            dashboard.feed.close()

    def stored(self):
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_first_start_shows_the_default_cards_in_the_dark_theme(self):
        dashboard = self.dashboard()
        self.assertEqual(dashboard.palette.name, "dark")
        self.assertEqual(tuple(dashboard.hero_cards), app.DEFAULT_HERO_KEYS)
        self.assertNotIn("gear", dashboard.hero_cards)
        self.assertFalse(self.path.exists())

    def test_a_second_close_leaves_the_first_one_alone(self):
        dashboard = self.dashboard()
        stops = []
        dashboard.stop_source = lambda: stops.append(True)
        dashboard.close()
        dashboard.close()
        self.assertEqual(len(stops), 1)
        self.assertTrue(dashboard.closed)
        self.assertFalse(self.window.winfo_exists())

    @unittest.skipUnless(sys.platform == "darwin", "macOS quit command")
    def test_the_quit_command_of_the_platform_closes_the_window(self):
        dashboard = self.dashboard()
        stops = []
        dashboard.stop_source = lambda: stops.append(True)
        self.window.tk.call("::tk::mac::Quit")
        self.assertTrue(dashboard.closed)
        self.assertEqual(len(stops), 1)

    def test_hero_cards_share_one_row(self):
        dashboard = self.dashboard()
        self.assertIsInstance(dashboard.hero_row, widgets.HeroRow)
        rows = {
            int(card.grid_info()["row"])
            for card in dashboard.hero_cards.values()
        }
        self.assertEqual(rows, {0})

    def test_chosen_cards_are_shown_and_stored(self):
        dashboard = self.dashboard()
        dashboard.apply_hero_keys(("gear", "rpm", "unknown", "gear"))
        self.assertEqual(tuple(dashboard.hero_cards), ("gear", "rpm"))
        self.assertEqual(
            dashboard.hero_row.cards,
            tuple(dashboard.hero_cards.values()),
        )
        self.assertEqual(self.stored()["hero"], ["gear", "rpm"])

    def test_an_empty_hero_row_is_a_valid_choice(self):
        dashboard = self.dashboard()
        dashboard.apply_hero_keys(())
        self.assertEqual(dashboard.hero_cards, {})
        self.assertEqual(self.stored()["hero"], [])

    def test_theme_toggle_rebuilds_the_window_and_is_stored(self):
        dashboard = self.dashboard()
        dashboard.source_var.set("Source: demo")
        dashboard.apply_hero_keys(("rpm", "gear"))

        dashboard.toggle_theme()

        self.assertEqual(dashboard.palette, app.LIGHT)
        self.assertEqual(self.window.cget("bg"), app.LIGHT.bg)
        self.assertEqual(dashboard.theme_button.cget("text"), "DARK")
        self.assertEqual(dashboard.source_var.get(), "Source: demo")
        self.assertEqual(tuple(dashboard.hero_cards), ("rpm", "gear"))
        self.assertEqual(self.stored()["theme"], "light")

    def test_stored_choices_return_on_the_next_start(self):
        settings.save(
            self.path,
            settings.Settings("light", ("coolant_deg_c", "gear")),
        )
        dashboard = self.dashboard()
        self.assertEqual(dashboard.palette, app.LIGHT)
        self.assertEqual(tuple(dashboard.hero_cards), ("coolant_deg_c", "gear"))

    def test_ack_control_follows_the_listen_only_option(self):
        self.assertTrue(self.dashboard().active_button.lit)

    def test_listen_only_start_leaves_the_ack_control_unlit(self):
        dashboard = self.dashboard("--listen-only")
        self.assertFalse(dashboard.active_button.lit)
        dashboard.toggle_active()
        self.assertTrue(dashboard.active_var.get())
        self.assertTrue(dashboard.active_button.lit)

    def test_tabs_show_one_panel_grid_at_a_time(self):
        dashboard = self.dashboard()
        dashboard.select_tab(1)
        self.assertEqual(
            [button.lit for button in dashboard.tab_buttons],
            [False, True],
        )
        self.assertEqual(dashboard.panel_grids[0].winfo_manager(), "")
        self.assertEqual(dashboard.panel_grids[1].winfo_manager(), "pack")

    def test_only_the_shown_tab_follows_live_values(self):
        dashboard = self.dashboard()
        dashboard.select_tab(0)
        dashboard._metric_value = lambda key: 12.0
        dashboard._refresh(0.0)
        shown = [
            panel.variables[metric.key].get()
            for panel, metrics in dashboard.tab_panels[0]
            for metric in metrics
        ]
        hidden = [
            panel.variables[metric.key].get()
            for panel, metrics in dashboard.tab_panels[1]
            for metric in metrics
        ]
        self.assertTrue(all(value != "--" for value in shown))
        self.assertTrue(all(value == "--" for value in hidden))
        dashboard.select_tab(1)
        self.assertTrue(all(
            panel.variables[metric.key].get() != "--"
            for panel, metrics in dashboard.tab_panels[1]
            for metric in metrics
        ))

    def test_card_picker_opens_once_and_applies_into_the_window(self):
        dashboard = self.dashboard()
        dashboard.open_hero_picker()
        picker = dashboard.picker
        dashboard.open_hero_picker()
        self.assertIs(dashboard.picker, picker)
        picker.restore_defaults()
        picker.shown_list.selection_set(0)
        picker.remove_selected()
        picker.apply()
        self.assertEqual(
            tuple(dashboard.hero_cards),
            app.DEFAULT_HERO_KEYS[1:],
        )
        self.assertFalse(picker.winfo_exists())

    def test_first_start_leaves_the_feed_off(self):
        dashboard = self.dashboard()
        self.assertIsNone(dashboard.feed)
        self.assertFalse(dashboard.feed_button.lit)
        self.assertEqual(dashboard.feed_var.get(), "Feed: off")

    def test_the_feed_dialog_turns_the_feed_on_and_stores_it(self):
        dashboard = self.dashboard()
        dashboard.open_feed_dialog()
        dialog = dashboard.feed_dialog
        dashboard.open_feed_dialog()
        self.assertIs(dashboard.feed_dialog, dialog)
        dialog.toggle_enabled()
        dialog.endpoint_var.set("127.0.0.1:5000")
        dialog.apply()

        self.assertFalse(dialog.winfo_exists())
        self.assertEqual(dashboard.feed.endpoint, ("127.0.0.1", 5000))
        self.assertTrue(dashboard.feed_button.lit)
        self.assertEqual(
            dashboard.feed_var.get(), "Feed: udp 127.0.0.1:5000, 0 sent"
        )
        self.assertEqual(
            self.stored()["feed"],
            {"enabled": True, "host": "127.0.0.1", "port": 5000},
        )

    def test_a_stored_feed_runs_on_the_next_start(self):
        settings.save(
            self.path,
            settings.Settings(
                "dark",
                app.DEFAULT_HERO_KEYS,
                settings.FeedSettings(True, "127.0.0.1", 5000),
            ),
        )
        dashboard = self.dashboard()
        self.assertEqual(dashboard.feed.endpoint, ("127.0.0.1", 5000))
        self.assertTrue(dashboard.feed_button.lit)

    def test_a_stored_load_reference_is_dropped(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(
                {
                    "version": settings.SETTINGS_VERSION,
                    "theme": "dark",
                    "hero": list(app.DEFAULT_HERO_KEYS),
                    "feed": {
                        "enabled": True,
                        "host": "127.0.0.1",
                        "port": 5000,
                        "bfs_reference": 27226,
                    },
                }
            ),
            encoding="utf-8",
        )
        dashboard = self.dashboard()
        self.assertEqual(dashboard.feed.endpoint, ("127.0.0.1", 5000))
        dashboard.toggle_theme()
        self.assertEqual(
            self.stored()["feed"],
            {"enabled": True, "host": "127.0.0.1", "port": 5000},
        )

    def test_the_feed_dialog_turns_the_feed_off(self):
        dashboard = self.dashboard()
        dashboard.apply_feed(settings.FeedSettings(True, "127.0.0.1", 5000))
        running = dashboard.feed
        self.assertEqual(
            dashboard.feed_var.get(), "Feed: udp 127.0.0.1:5000, 0 sent"
        )

        dashboard.apply_feed(settings.FeedSettings(False, "127.0.0.1", 5000))

        self.assertIsNone(dashboard.feed)
        self.assertEqual(running._socket.fileno(), -1)
        self.assertFalse(dashboard.feed_button.lit)
        self.assertEqual(dashboard.feed_var.get(), "Feed: off")
        self.assertFalse(self.stored()["feed"]["enabled"])

    def test_the_feed_survives_a_theme_change(self):
        dashboard = self.dashboard()
        dashboard.apply_feed(settings.FeedSettings(True, "127.0.0.1", 5000))
        running = dashboard.feed
        dashboard.toggle_theme()
        self.assertIs(dashboard.feed, running)
        self.assertTrue(dashboard.feed_button.lit)
        self.assertEqual(self.stored()["feed"]["port"], 5000)
        self.assertEqual(self.stored()["theme"], "light")

    def test_the_command_line_endpoint_runs_without_being_stored(self):
        dashboard = self.dashboard(publish_udp=("127.0.0.1", 5001))
        self.assertEqual(dashboard.feed.endpoint, ("127.0.0.1", 5001))
        self.assertEqual(dashboard.settings.feed, settings.FeedSettings())
        dashboard.toggle_theme()
        self.assertEqual(
            self.stored()["feed"],
            {"enabled": False, "host": "127.0.0.1", "port": 47809},
        )

    def test_the_endpoint_override_turns_a_stored_feed_on(self):
        settings.save(
            self.path,
            settings.Settings(
                "dark",
                app.DEFAULT_HERO_KEYS,
                settings.FeedSettings(False, "127.0.0.1", 5000),
            ),
        )
        dashboard = self.dashboard(publish_udp=("127.0.0.1", 5001))
        self.assertEqual(dashboard.feed.endpoint, ("127.0.0.1", 5001))
        self.assertFalse(dashboard.settings.feed.enabled)


if __name__ == "__main__":
    unittest.main()
