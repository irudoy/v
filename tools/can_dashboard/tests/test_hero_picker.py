import tkinter as tk
import unittest

from tools.can_dashboard import hero_picker


try:
    ROOT = tk.Tk()
    ROOT.withdraw()
except tk.TclError:
    ROOT = None

TK_AVAILABLE = ROOT is not None


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


CHOICES = (
    hero_picker.HeroChoice("rpm", "Engine speed", "Primary"),
    hero_picker.HeroChoice("speed", "Vehicle speed", "Primary"),
    hero_picker.HeroChoice("load", "Calculated load", "Primary"),
    hero_picker.HeroChoice("gear", "Selector", "Context"),
)


class HeroSelectionTest(unittest.TestCase):
    def selection(self, selected=("rpm", "load"), limit=3):
        return hero_picker.HeroSelection(CHOICES, selected, limit)

    def test_caption_names_the_group_and_the_metric(self):
        self.assertEqual(CHOICES[3].caption, "Context: Selector")

    def test_available_keys_follow_the_catalog_order(self):
        self.assertEqual(self.selection().available(), ("speed", "gear"))

    def test_added_cards_go_to_the_right_end(self):
        selection = self.selection()
        self.assertTrue(selection.add("gear"))
        self.assertEqual(selection.selected, ["rpm", "load", "gear"])

    def test_the_limit_refuses_more_cards(self):
        selection = self.selection()
        selection.add("gear")
        self.assertTrue(selection.full)
        self.assertFalse(selection.add("speed"))
        self.assertEqual(selection.selected, ["rpm", "load", "gear"])

    def test_unknown_and_repeated_keys_are_refused(self):
        selection = self.selection()
        self.assertFalse(selection.add("rpm"))
        self.assertFalse(selection.add("boost"))
        self.assertEqual(selection.selected, ["rpm", "load"])

    def test_initial_keys_pass_the_same_checks(self):
        selection = self.selection(("load", "boost", "load", "rpm", "gear", "speed"))
        self.assertEqual(selection.selected, ["load", "rpm", "gear"])

    def test_removed_cards_return_to_the_available_list(self):
        selection = self.selection()
        self.assertTrue(selection.remove("rpm"))
        self.assertFalse(selection.remove("rpm"))
        self.assertEqual(selection.available(), ("rpm", "speed", "gear"))

    def test_cards_move_inside_the_row_only(self):
        selection = self.selection(("rpm", "load", "gear"))
        self.assertTrue(selection.move("gear", -1))
        self.assertEqual(selection.selected, ["rpm", "gear", "load"])
        self.assertFalse(selection.move("rpm", -1))
        self.assertFalse(selection.move("load", 1))
        self.assertFalse(selection.move("speed", 1))
        self.assertEqual(selection.selected, ["rpm", "gear", "load"])


COLORS = {
    "bg": "#000000",
    "panel": "#0b0b0b",
    "border": "#363636",
    "text": "#f5f5f5",
    "muted": "#a3a3a3",
    "heading": "#ffb000",
    "select": "#4da3ff",
    "select_text": "#000000",
}
BUTTON_COLORS = {
    "face": "#161616",
    "hover": "#262626",
    "text": "#f5f5f5",
    "border": "#363636",
    "focus": "#4da3ff",
    "lit": "#2fd35a",
    "record": "#ff453a",
    "lit_text": "#000000",
}
FONTS = {
    "label": ("Helvetica", 9),
    "heading": ("Helvetica", 9, "bold"),
    "list": ("Helvetica", 10),
    "button": ("Helvetica", 9, "bold"),
}


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class HeroPickerTest(unittest.TestCase):
    def setUp(self):
        self.applied = []
        self.picker = hero_picker.HeroPicker(
            ROOT,
            choices=CHOICES,
            selected=("rpm", "load"),
            defaults=("rpm", "speed", "load"),
            limit=3,
            colors=COLORS,
            button_colors=BUTTON_COLORS,
            fonts=FONTS,
            on_apply=self.applied.append,
            scrollbar_style="Vertical.TScrollbar",
        )
        self.picker.withdraw()
        self.addCleanup(self._close)

    def _close(self):
        if self.picker.winfo_exists():
            self.picker.destroy()

    def rows(self, listbox):
        return list(listbox.get(0, "end"))

    def test_the_lists_are_wide_enough_for_the_catalog_captions(self):
        self.assertGreaterEqual(hero_picker.LIST_WIDTH_CHARS, 46)
        for listbox in (self.picker.available_list, self.picker.shown_list):
            with self.subTest(listbox=str(listbox)):
                self.assertEqual(
                    int(listbox.cget("width")),
                    hero_picker.LIST_WIDTH_CHARS,
                )
        self.assertEqual(
            tuple(self.picker.minsize()),
            (hero_picker.PICKER_MIN_WIDTH, hero_picker.PICKER_MIN_HEIGHT),
        )

    def test_lists_split_the_catalog(self):
        self.assertEqual(
            self.rows(self.picker.available_list),
            ["Primary: Vehicle speed", "Context: Selector"],
        )
        self.assertEqual(
            self.rows(self.picker.shown_list),
            ["Primary: Engine speed", "Primary: Calculated load"],
        )
        self.assertIn("2 of 3 cards", self.picker.count_var.get())

    def test_add_moves_the_chosen_metric_to_the_shown_list(self):
        self.picker.available_list.selection_set(1)
        self.picker.add_selected()
        self.assertEqual(self.picker.selection.selected, ["rpm", "load", "gear"])
        self.assertEqual(
            self.rows(self.picker.available_list),
            ["Primary: Vehicle speed"],
        )
        self.assertIn("3 of 3 cards", self.picker.count_var.get())

    def test_add_without_a_chosen_row_changes_nothing(self):
        self.picker.add_selected()
        self.assertEqual(self.picker.selection.selected, ["rpm", "load"])

    def test_remove_and_move_follow_the_chosen_card(self):
        self.picker.shown_list.selection_set(1)
        self.picker.move_selected(-1)
        self.assertEqual(self.picker.selection.selected, ["load", "rpm"])
        self.assertEqual(self.picker.shown_list.curselection(), (0,))
        self.picker.remove_selected()
        self.assertEqual(self.picker.selection.selected, ["rpm"])

    def test_defaults_replace_the_shown_cards(self):
        self.picker.restore_defaults()
        self.assertEqual(
            self.picker.selection.selected,
            ["rpm", "speed", "load"],
        )

    def test_apply_reports_the_ordered_keys_and_closes(self):
        self.picker.available_list.selection_set(0)
        self.picker.add_selected()
        self.picker.apply()
        self.assertEqual(self.applied, [("rpm", "load", "speed")])
        self.assertFalse(self.picker.winfo_exists())


if __name__ == "__main__":
    unittest.main()
