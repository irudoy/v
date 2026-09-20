import tempfile
import tkinter as tk
import unittest

from tools.can_dashboard import feed_dialog, live_feed
from tools.can_dashboard.settings import FeedSettings


try:
    ROOT = tk.Tk()
    ROOT.withdraw()
except tk.TclError:
    ROOT = None

TK_AVAILABLE = ROOT is not None

COLORS = {
    "bg": "#000000",
    "panel": "#101010",
    "border": "#303030",
    "text": "#ffffff",
    "muted": "#909090",
    "heading": "#c0c0c0",
    "select": "#3060ff",
    "ok": "#30c060",
    "error": "#ff4040",
}
BUTTON_COLORS = {
    "face": "#101010",
    "hover": "#202020",
    "text": "#ffffff",
    "border": "#303030",
    "focus": "#3060ff",
    "lit": "#30c060",
    "record": "#ff4040",
    "lit_text": "#000000",
}
FONTS = {
    "label": ("TkDefaultFont", 9),
    "heading": ("TkDefaultFont", 9, "bold"),
    "entry": ("TkFixedFont", 10),
    "button": ("TkDefaultFont", 9, "bold"),
}


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


class FormTest(unittest.TestCase):
    def test_the_form_builds_feed_settings(self):
        self.assertEqual(
            feed_dialog.parse_form(True, " 127.0.0.1:5000 "),
            FeedSettings(True, "127.0.0.1", 5000),
        )
        self.assertEqual(
            feed_dialog.parse_form(False, "47809"),
            FeedSettings(False, live_feed.DEFAULT_HOST, 47809),
        )

    def test_the_form_rejects_an_invalid_endpoint(self):
        for endpoint in ("", "host:", ":5000", "0", "70000", "host:port"):
            with self.subTest(endpoint=endpoint):
                with self.assertRaises(ValueError):
                    feed_dialog.parse_form(True, endpoint)

    def test_the_default_endpoint_round_trips(self):
        defaults = FeedSettings()
        self.assertEqual(
            feed_dialog.parse_form(
                False,
                feed_dialog.endpoint_text(defaults.host, defaults.port),
            ),
            defaults,
        )

    def test_the_load_note_names_the_table_the_plugin_file_binds(self):
        self.assertIn(live_feed.LOAD_REFERENCE_TABLE, feed_dialog.LOAD_HINT)
        self.assertIn(
            f"={live_feed.LOAD_REFERENCE_TABLE}\n",
            live_feed.plugin_properties(),
        )


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class FeedDialogTest(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.plugin_path = live_feed.plugin_path(directory.name)

    def dialog(self, feed=FeedSettings()):
        self.applied = []
        dialog = feed_dialog.FeedDialog(
            ROOT,
            feed=feed,
            colors=COLORS,
            button_colors=BUTTON_COLORS,
            fonts=FONTS,
            on_apply=self.applied.append,
            plugin_path=self.plugin_path,
        )
        self.addCleanup(
            lambda: dialog.destroy() if dialog.winfo_exists() else None
        )
        return dialog

    def test_the_dialog_shows_the_current_feed(self):
        dialog = self.dialog(FeedSettings(True, "127.0.0.1", 5000))
        self.assertTrue(dialog.publish_button.lit)
        self.assertEqual(dialog.endpoint_var.get(), "127.0.0.1:5000")

    def test_a_first_run_needs_no_typing(self):
        dialog = self.dialog()
        self.assertFalse(dialog.publish_button.lit)
        entries = [
            widget
            for widget in dialog.winfo_children()
            for widget in [widget, *widget.winfo_children()]
            if isinstance(widget, tk.Entry)
        ]
        self.assertEqual(entries, [dialog.endpoint_entry])
        dialog.toggle_enabled()
        self.assertTrue(dialog.publish_button.lit)
        dialog.apply()
        self.assertEqual(
            self.applied,
            [
                FeedSettings(
                    True, live_feed.DEFAULT_HOST, live_feed.DEFAULT_PORT
                )
            ],
        )
        self.assertFalse(dialog.winfo_exists())

    def test_an_invalid_field_keeps_the_dialog_open_with_the_reason(self):
        dialog = self.dialog()
        dialog.endpoint_var.set("host:")
        dialog.apply()
        self.assertEqual(self.applied, [])
        self.assertTrue(dialog.winfo_exists())
        self.assertIn("port", dialog.message_var.get())
        self.assertEqual(
            str(dialog.message_label.cget("fg")), COLORS["error"]
        )

    def test_cancel_applies_nothing(self):
        dialog = self.dialog()
        dialog.toggle_enabled()
        dialog.destroy()
        self.assertEqual(self.applied, [])

    def test_one_click_installs_the_plugin_file_for_the_typed_endpoint(self):
        dialog = self.dialog()
        self.assertEqual(dialog.plugin_var.get(), "not installed")
        dialog.endpoint_var.set("127.0.0.1:5000")

        self.assertEqual(dialog.install_plugin(), self.plugin_path)

        self.assertEqual(
            self.plugin_path.read_text(encoding="ascii"),
            live_feed.plugin_properties("127.0.0.1", 5000),
        )
        self.assertEqual(dialog.plugin_var.get(), "installed for this endpoint")
        self.assertEqual(str(dialog.plugin_label.cget("fg")), COLORS["ok"])
        self.assertIn("Restart RomRaider Logger", dialog.message_var.get())
        self.assertEqual(self.applied, [])

    def test_the_plugin_state_follows_the_typed_endpoint(self):
        live_feed.install_plugin(self.plugin_path)
        dialog = self.dialog()
        self.assertEqual(dialog.plugin_var.get(), "installed for this endpoint")
        dialog.endpoint_var.set("127.0.0.1:5000")
        self.assertEqual(
            dialog.plugin_var.get(), "out of date, install again"
        )
        self.assertEqual(str(dialog.plugin_label.cget("fg")), COLORS["error"])
        dialog.endpoint_var.set("host:")
        self.assertEqual(dialog.plugin_var.get(), "")

    def test_a_plugin_file_of_another_channel_table_is_out_of_date(self):
        self.plugin_path.parent.mkdir(parents=True)
        current = live_feed.plugin_properties()
        self.plugin_path.write_text(
            "".join(
                line
                for line in current.splitlines(keepends=True)
                if ".expression=" not in line and ".table." not in line
            ),
            encoding="ascii",
        )
        dialog = self.dialog()
        self.assertEqual(
            dialog.plugin_var.get(), "out of date, install again"
        )
        dialog.install_plugin()
        self.assertEqual(dialog.plugin_var.get(), "installed for this endpoint")
        self.assertEqual(
            self.plugin_path.read_text(encoding="ascii"), current
        )

    def test_a_write_failure_is_reported(self):
        self.plugin_path.parent.parent.mkdir(parents=True)
        self.plugin_path.parent.write_text("a file, not a folder")
        dialog = self.dialog()
        self.assertIsNone(dialog.install_plugin())
        self.assertIn("not written", dialog.message_var.get())
        self.assertEqual(
            str(dialog.message_label.cget("fg")), COLORS["error"]
        )

    def test_an_invalid_endpoint_writes_no_plugin_file(self):
        dialog = self.dialog()
        dialog.endpoint_var.set("host:")
        self.assertIsNone(dialog.install_plugin())
        self.assertFalse(self.plugin_path.exists())
        self.assertIn("port", dialog.message_var.get())

if __name__ == "__main__":
    unittest.main()
