import unittest

from tools.can_dashboard.settings import HeroChoice, HeroSelection


CHOICES = (
    HeroChoice("rpm", "Engine speed", "Primary"),
    HeroChoice("speed", "Vehicle speed", "Primary"),
    HeroChoice("load", "Calculated load", "Primary"),
    HeroChoice("gear", "Selector", "Context"),
)


class HeroSelectionTest(unittest.TestCase):
    def selection(self, selected=("rpm", "load"), limit=3):
        return HeroSelection(CHOICES, selected, limit)

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
