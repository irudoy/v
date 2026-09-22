import json
from pathlib import Path
import sys
import tempfile
import tkinter as tk
import types
import unittest

from tools.can_dashboard import acceleration
from tools.can_dashboard import app
from tools.can_dashboard import icons
from tools.can_dashboard import replay
from tools.can_dashboard import selected_map
from tools.can_dashboard import settings
from tools.can_dashboard import widgets
from tools.can_dashboard.descriptions import describe


try:
    ROOT = tk.Tk()
    ROOT.withdraw()
except tk.TclError:
    ROOT = None

TK_AVAILABLE = ROOT is not None


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


def tool_buttons(widget):
    """Every tool button under widget, in creation order."""
    found = []
    for child in widget.winfo_children():
        if isinstance(child, widgets.ToolButton):
            found.append(child)
        found.extend(tool_buttons(child))
    return found


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

    def test_the_transmission_gear_and_the_selected_map_are_optional_rows(self):
        for key in ("tcm_gear", "selected_map"):
            with self.subTest(key=key):
                self.assertIn(key, app.HERO_CATALOG)
                self.assertNotIn(key, app.DEFAULT_HERO_KEYS)
        context = dict(app.PANELS)["Temperatures and context"]
        labels = {metric.key: metric.label for metric in context}
        self.assertEqual(labels["tcm_gear"], "Gear")
        self.assertEqual(labels["selected_map"], "Selected map")

    def test_every_offered_metric_carries_its_description(self):
        for choice in app.HERO_CHOICES:
            with self.subTest(key=choice.key):
                self.assertEqual(choice.description, describe(choice.key))
                self.assertTrue(choice.description)

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

    def test_every_button_carries_an_icon(self):
        dashboard = self.dashboard()
        buttons = tool_buttons(self.window)
        self.assertEqual(
            [(button.cget("text"), button.cget("icon")) for button in buttons],
            [
                ("ACK", "exchange"),
                ("CONNECT", "plug"),
                ("DEMO", "flask"),
                ("REPLAY", "folder"),
                ("STREAM", "broadcast"),
                ("REC", "dot"),
                ("FEED", "share"),
                ("CARDS", "grid"),
                ("0-100", "stopwatch"),
                ("LIGHT", "sun"),
                ("RESET TIMES", "circular-arrow"),
                ("PLAY", "play"),
                ("LOOP", "repeat"),
                ("IN", "mark-in"),
                ("OUT", "mark-out"),
                ("SAVE LOOP", "floppy"),
                ("1x", "fast-forward"),
                ("PRIMARY", "gauge"),
                ("EXTENDED", "list"),
            ],
        )
        for button in buttons:
            with self.subTest(button=button.cget("text")):
                self.assertIn(button.cget("icon"), icons.ICONS)
        self.assertEqual(dashboard.theme_button.cget("icon"), "sun")
        self.assertEqual(
            [button.cget("icon") for button in dashboard.tab_buttons],
            ["gauge", "list"],
        )
        dashboard.toggle_theme()
        self.assertEqual(dashboard.theme_button.cget("icon"), "moon")

    def test_the_record_button_shows_the_action_it_takes_next(self):
        dashboard = self.dashboard()
        button = dashboard.record_button
        self.assertEqual((button.cget("icon"), button.lit), ("dot", False))
        dashboard.recorder = object()
        dashboard._sync_record_button()
        self.assertEqual((button.cget("icon"), button.lit), ("stop", True))
        self.assertEqual(button.cget("bg"), dashboard.palette.red)
        dashboard.recorder = None
        dashboard._sync_record_button()
        self.assertEqual((button.cget("icon"), button.lit), ("dot", False))

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


def speed_trace(path, speeds):
    """Write a PEAK TRC of one 0x280 frame per 100 ms at the given speeds."""
    lines = [";$FILEVERSION=1.1", ";$STARTTIME=46250.0", ";"]
    for number, kmh in enumerate(speeds, start=1):
        raw = round(kmh * 100)
        payload = f"00 00 00 00 {raw >> 8:02X} {raw & 0xFF:02X} 00 00"
        lines.append(
            f"{number:6d}) {number * 100.0:11.1f}  Rx         0280  8  {payload}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="ascii")
    return path


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class DashboardReplayWindowTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        self.window = tk.Toplevel(ROOT)
        self.window.withdraw()
        self.addCleanup(self._close)
        args = app.build_parser().parse_args([
            "--no-auto-connect",
            "--settings",
            str(self.directory / "settings.json"),
        ])
        self.dashboard = app.DashboardApp(self.window, args)
        self.window.update_idletasks()

    def _close(self):
        if self.window.winfo_exists():
            self.window.destroy()

    def open_replay(self, speeds=(0.0, 10.0, 20.0, 30.0, 40.0, 50.0)):
        path = speed_trace(self.directory / "drive.trc", speeds)
        timeline = replay.load_timeline(path, self.dashboard.model.can_id)
        self.dashboard._open_replay(timeline)
        self.window.update_idletasks()
        return timeline

    def panel_value(self, key):
        for panel, _metrics in self.dashboard.data_panels:
            if key in panel.variables:
                return panel.variables[key].get()
        raise KeyError(key)

    def stored(self):
        path = self.directory / "settings.json"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_the_timer_bar_is_hidden_until_the_0_100_button_shows_it(self):
        dashboard = self.dashboard
        dashboard._refresh(0.0)
        self.assertEqual(dashboard.timer_bar.winfo_manager(), "")
        self.assertFalse(dashboard.timer_button.lit)
        self.assertEqual(dashboard.replay_bar.winfo_manager(), "")

        dashboard.toggle_timer()
        dashboard._refresh(0.0)
        self.assertEqual(dashboard.timer_bar.winfo_manager(), "pack")
        self.assertTrue(dashboard.timer_button.lit)
        self.assertIs(self.stored()["timer"], True)
        for name in app.RUN_TOOLTIPS:
            self.assertEqual(dashboard.run_value_vars[name].get(), "--")
            self.assertEqual(dashboard.run_best_vars[name].get(), "best --")

        dashboard.toggle_theme()
        self.assertEqual(dashboard.timer_bar.winfo_manager(), "pack")
        dashboard.toggle_timer()
        self.assertEqual(dashboard.timer_bar.winfo_manager(), "")
        self.assertIs(self.stored()["timer"], False)

    def test_the_timer_bar_shows_the_run_times(self):
        dashboard = self.dashboard
        dashboard.toggle_timer()
        zero_to_100 = dashboard.model.drive.acceleration.run("0-100")
        zero_to_100.last = zero_to_100.best = acceleration.RunResult(8.5, 1.0)
        dashboard._refresh(0.0)
        self.assertEqual(dashboard.run_value_vars["0-100"].get(), "8.50 s")
        self.assertEqual(dashboard.run_best_vars["0-100"].get(), "best 8.50 s")
        self.assertEqual(dashboard._metric_value("zero_to_100_s"), 8.5)
        dashboard.reset_acceleration()
        dashboard._refresh(0.0)
        self.assertEqual(dashboard.run_value_vars["0-100"].get(), "--")

    def test_the_replay_bar_follows_the_timer_bar(self):
        dashboard = self.dashboard
        self.open_replay()
        order = dashboard.root.pack_slaves()
        self.assertEqual(
            order.index(dashboard.replay_bar),
            order.index(dashboard.status_bar) + 1,
        )
        dashboard.toggle_timer()
        order = dashboard.root.pack_slaves()
        self.assertEqual(
            order.index(dashboard.timer_bar),
            order.index(dashboard.status_bar) + 1,
        )
        self.assertEqual(
            order.index(dashboard.replay_bar),
            order.index(dashboard.timer_bar) + 1,
        )

    def test_the_selected_map_and_the_gear_are_panel_values(self):
        dashboard = self.dashboard
        dashboard._refresh(0.0)
        self.assertEqual(self.panel_value("selected_map"), "--")
        self.assertEqual(self.panel_value("tcm_gear"), "--")
        dashboard.model.drive.map.number = 3
        dashboard.model.tcm_gear = 4
        dashboard._refresh(0.0)
        self.assertEqual(self.panel_value("selected_map"), "3")
        self.assertEqual(self.panel_value("tcm_gear"), "4")
        self.assertEqual(dashboard._metric_value("selected_map"), 3)
        self.assertEqual(dashboard._metric_value("tcm_gear"), 4)

    def test_hover_over_a_metric_name_describes_the_metric(self):
        dashboard = self.dashboard
        for panel, metrics in dashboard.data_panels:
            for metric in metrics:
                with self.subTest(key=metric.key):
                    text = panel.label_tooltip(metric)
                    if metric.key == "selected_map":
                        self.assertEqual(
                            text,
                            f"Selected map\n\n{describe('selected_map')}"
                            "\n\nLast observation: "
                            f"{selected_map.UNKNOWN_REASON}.",
                        )
                    else:
                        self.assertEqual(
                            text,
                            f"{metric.label}\n\n{describe(metric.key)}",
                        )
        card = dashboard.hero_cards["rpm"]
        self.assertEqual(
            card.tooltip_text(),
            f"ENGINE SPEED [RPM]\n--\n\n{describe('rpm')}",
        )

    def test_save_loop_writes_the_loop_region_as_a_new_trace(self):
        dashboard = self.dashboard
        self.open_replay()
        dashboard.toggle_play()
        self.assertEqual(dashboard.replay_note.winfo_manager(), "")
        dashboard._replay_seek(0.2)
        dashboard.toggle_loop_in()
        dashboard._replay_seek(0.4)
        dashboard.toggle_loop_out()
        output = self.directory / "loop.trc"
        dashboard.save_loop(output)
        self.assertEqual(dashboard.replay_note_var.get(), "saved loop.trc")
        self.assertEqual(dashboard.replay_note.winfo_manager(), "pack")

        saved = replay.load_timeline(output, dashboard.model.can_id)
        self.assertEqual(list(saved.times), [0.0, 0.1, 0.2])
        self.assertEqual(
            [int.from_bytes(data[4:6], "big") for data in saved.payloads],
            [1000, 2000, 3000],
        )

        dashboard.save_loop(output)
        self.assertEqual(
            dashboard.replay_note_var.get(),
            "loop not saved: loop.trc already exists",
        )
        dashboard.toggle_theme()
        self.assertEqual(dashboard.replay_note.winfo_manager(), "pack")
        self.open_replay()
        self.assertEqual(dashboard.replay_note_var.get(), "")
        self.assertEqual(dashboard.replay_note.winfo_manager(), "")

    def test_a_loaded_replay_shows_its_transport_and_plays(self):
        dashboard = self.dashboard
        timeline = self.open_replay()
        player = dashboard.player
        self.assertIs(player.timeline, timeline)
        self.assertTrue(player.playing)
        self.assertEqual(dashboard.replay_bar.winfo_manager(), "pack")
        self.assertEqual(
            dashboard.play_button.cget("text"), app.PLAY_CAPTIONS[True]
        )
        self.assertEqual(dashboard.play_button.cget("icon"), "pause")
        self.assertTrue(dashboard.source_is_active())

        dashboard.toggle_play()
        dashboard._refresh(0.0)
        self.assertFalse(player.playing)
        self.assertEqual(dashboard.status_var.get(), "PAUSED")
        self.assertEqual(
            dashboard.play_button.cget("text"), app.PLAY_CAPTIONS[False]
        )
        self.assertEqual(dashboard.play_button.cget("icon"), "play")

        dashboard.toggle_loop()
        dashboard.cycle_speed()
        self.assertTrue(dashboard.loop_button.lit)
        self.assertEqual(dashboard.speed_button.cget("text"), "2x")
        self.assertEqual(dashboard.replay_time_var.get(), "0:00.0 / 0:00.6")

        dashboard.stop_source()
        self.assertIsNone(dashboard.player)
        self.assertEqual(dashboard.replay_bar.winfo_manager(), "")

    def test_a_seek_rebuilds_the_model_at_the_target(self):
        dashboard = self.dashboard
        self.open_replay()
        dashboard.toggle_play()
        dashboard._replay_seek(0.35)
        self.assertEqual(dashboard.player.position, 0.35)
        self.assertEqual(dashboard.model.vehicle_speed_kmh, 20.0)
        dashboard.replay_step(-app.REPLAY_STEP_SECONDS)
        self.assertEqual(dashboard.player.position, 0.0)
        self.assertIsNone(dashboard.model.vehicle_speed_kmh)

    def test_a_release_on_the_timeline_seeks_there(self):
        dashboard = self.dashboard
        timeline = self.open_replay()
        dashboard.toggle_play()
        dashboard._on_timeline_drag(types.SimpleNamespace(x=10_000))
        self.assertEqual(dashboard.scrub_position, timeline.duration)
        self.assertEqual(dashboard.player.position, 0.0)
        dashboard._on_timeline_release(types.SimpleNamespace(x=10_000))
        self.assertIsNone(dashboard.scrub_position)
        self.assertEqual(dashboard.player.position, timeline.duration)
        self.assertEqual(dashboard.model.vehicle_speed_kmh, 50.0)

    def test_playing_to_the_end_pauses_or_loops(self):
        dashboard = self.dashboard
        timeline = self.open_replay()
        dashboard._advance_replay(dashboard.player._anchor_host + 5.0)
        self.assertFalse(dashboard.player.playing)
        self.assertEqual(dashboard.player.position, timeline.duration)
        dashboard.toggle_play()
        self.assertTrue(dashboard.player.playing)
        self.assertEqual(dashboard.player.position, 0.0)
        dashboard.toggle_loop()
        dashboard._advance_replay(dashboard.player._anchor_host + 5.0)
        self.assertTrue(dashboard.player.playing)
        self.assertEqual(dashboard.player.position, 0.0)

    def test_turning_the_loop_on_after_the_region_jumps_to_its_start(self):
        dashboard = self.dashboard
        self.open_replay()
        player = dashboard.player
        dashboard._replay_seek(0.2)
        dashboard.toggle_loop_in()
        dashboard._replay_seek(0.4)
        dashboard.toggle_loop_out()
        dashboard._replay_seek(0.3)
        dashboard.toggle_loop()
        self.assertTrue(player.loop)
        self.assertEqual(player.position, 0.3)
        dashboard.toggle_loop()
        dashboard._replay_seek(0.5)
        dashboard.toggle_loop()
        self.assertTrue(player.loop)
        self.assertTrue(player.playing)
        self.assertEqual(player.position, 0.2)
        self.assertEqual(dashboard.model.vehicle_speed_kmh, 10.0)
        dashboard._replay_seek(0.5)
        dashboard.toggle_loop()
        self.assertFalse(player.loop)
        self.assertEqual(player.position, 0.5)

        dashboard.toggle_loop_in()
        dashboard.toggle_loop_out()
        dashboard._advance_replay(player._anchor_host + 5.0)
        self.assertFalse(player.playing)
        dashboard.toggle_loop()
        self.assertFalse(player.playing)
        self.assertEqual(player.position, 0.0)

    def test_a_theme_change_keeps_the_replay_bar(self):
        dashboard = self.dashboard
        self.open_replay()
        dashboard.toggle_theme()
        self.window.update_idletasks()
        self.assertEqual(dashboard.replay_bar.winfo_manager(), "pack")
        self.assertEqual(
            dashboard.play_button.cget("text"), app.PLAY_CAPTIONS[True]
        )


if __name__ == "__main__":
    unittest.main()
