import unittest

from tools.can_dashboard import layout


def _monospace(text, cell=7):
    return len(text) * cell


class TextFittingTest(unittest.TestCase):
    def test_text_that_fits_is_returned_unchanged(self):
        self.assertEqual(
            layout.elide("Source: demo", _monospace, 200),
            "Source: demo",
        )

    def test_unknown_width_keeps_the_full_text(self):
        self.assertEqual(
            layout.elide("Source: demo", _monospace, 0),
            "Source: demo",
        )

    def test_long_text_is_shortened_to_the_available_width(self):
        shortened = layout.elide(
            "MLG: no complete snapshots, file not created",
            _monospace,
            140,
        )
        self.assertTrue(shortened.endswith(layout.ELLIPSIS))
        self.assertLessEqual(_monospace(shortened), 140)
        self.assertTrue(
            "MLG: no complete snapshots, file not created".startswith(
                shortened[: -len(layout.ELLIPSIS)]
            )
        )

    def test_hopeless_width_still_returns_the_ellipsis(self):
        self.assertEqual(layout.elide("value", _monospace, 3), "...")


class MiddleElisionTest(unittest.TestCase):
    def test_text_that_fits_is_returned_unchanged(self):
        self.assertEqual(
            layout.elide_middle("CVTC duty B1", _monospace, 200),
            "CVTC duty B1",
        )

    def test_unknown_width_keeps_the_full_text(self):
        self.assertEqual(
            layout.elide_middle("CVTC duty B1", _monospace, 0),
            "CVTC duty B1",
        )

    def test_both_ends_of_a_long_text_are_kept(self):
        full = "Intake CVTC duty command B1"
        shortened = layout.elide_middle(full, _monospace, 126)
        head, _ellipsis, tail = shortened.partition(layout.ELLIPSIS)
        self.assertLessEqual(_monospace(shortened), 126)
        self.assertTrue(head and full.startswith(head))
        self.assertTrue(tail and full.endswith(tail))
        self.assertGreater(len(head), len(tail))

    def test_a_trailing_bank_suffix_keeps_labels_distinct(self):
        shortened = {
            layout.elide_middle(full, _monospace, 119)
            for full in (
                "Exhaust CVTC actual B1",
                "Exhaust CVTC actual B2",
                "Exhaust CVTC duty B1 word",
                "Exhaust CVTC duty B2 word",
            )
        }
        self.assertEqual(len(shortened), 4)

    def test_hopeless_width_still_returns_the_ellipsis(self):
        self.assertEqual(layout.elide_middle("value", _monospace, 3), "...")


class RowWrappingTest(unittest.TestCase):
    def test_items_stay_on_one_row_while_they_fit(self):
        self.assertEqual(
            layout.wrap_rows((100, 100, 100), 340, 20),
            ((0, 1, 2),),
        )

    def test_narrow_width_wraps_into_more_rows(self):
        self.assertEqual(
            layout.wrap_rows((100, 100, 100), 230, 20),
            ((0, 1), (2,)),
        )

    def test_single_item_wider_than_the_row_keeps_its_own_row(self):
        self.assertEqual(
            layout.wrap_rows((400, 100), 200, 10),
            ((0,), (1,)),
        )

    def test_row_width_counts_the_gaps(self):
        self.assertEqual(layout.row_width((100, 100, 100), 20), 340)
        self.assertEqual(layout.row_width((), 20), 0)


class BalancedColumnsTest(unittest.TestCase):
    def test_a_full_row_is_kept(self):
        self.assertEqual(layout.balanced_columns(4, 4), 4)
        self.assertEqual(layout.balanced_columns(4, 9), 4)

    def test_a_leftover_item_is_avoided(self):
        self.assertEqual(layout.balanced_columns(4, 3), 2)
        self.assertEqual(layout.balanced_columns(5, 4), 3)
        self.assertEqual(layout.balanced_columns(6, 4), 3)
        self.assertEqual(layout.balanced_columns(3, 2), 2)

    def test_one_column_and_empty_grids(self):
        self.assertEqual(layout.balanced_columns(4, 1), 1)
        self.assertEqual(layout.balanced_columns(0, 3), 0)
        self.assertEqual(layout.balanced_columns(4, 0), 0)


class LabelValueSplitTest(unittest.TestCase):
    def test_a_wide_row_keeps_both_widths(self):
        self.assertEqual(layout.split_label_value(400, 120, 150, 80), (120, 150))

    def test_the_value_gives_way_before_the_label(self):
        self.assertEqual(layout.split_label_value(240, 120, 150, 80), (120, 120))

    def test_the_label_shrinks_after_the_value_reaches_its_floor(self):
        self.assertEqual(layout.split_label_value(180, 120, 150, 80), (100, 80))

    def test_the_parts_never_exceed_the_row(self):
        for available in range(1, 400, 7):
            with self.subTest(available=available):
                label, value = layout.split_label_value(available, 170, 150, 80)
                self.assertLessEqual(label + value, max(available, 0))
                self.assertGreaterEqual(label, 0)
                self.assertGreater(value, 0)

    def test_an_unmeasured_row_keeps_the_declared_widths(self):
        self.assertEqual(layout.split_label_value(0, 120, 150, 80), (120, 150))


class ColumnCountTest(unittest.TestCase):
    def test_columns_shrink_with_the_available_width(self):
        self.assertEqual(layout.responsive_columns(8, 164, 1358, 5), 8)
        self.assertEqual(layout.responsive_columns(8, 164, 700, 5), 4)
        self.assertEqual(layout.responsive_columns(8, 164, 300, 5), 1)

    def test_column_count_never_exceeds_the_item_count(self):
        self.assertEqual(layout.responsive_columns(4, 268, 4000, 6), 4)

    def test_unmeasured_width_keeps_the_declared_count(self):
        self.assertEqual(layout.responsive_columns(4, 268, 0, 6), 4)


class HeroValueSizeTest(unittest.TestCase):
    def test_wide_cards_use_the_largest_value_font(self):
        self.assertEqual(layout.hero_value_size(400), 22)
        self.assertEqual(layout.hero_value_size(170), 22)

    def test_value_font_steps_down_with_the_card_width(self):
        sizes = [layout.hero_value_size(width) for width in (169, 129, 99, 75)]
        self.assertEqual(sizes, [18, 15, 12, layout.HERO_VALUE_SIZE_FLOOR])

    def test_value_font_never_grows_as_the_card_narrows(self):
        sizes = [layout.hero_value_size(width) for width in range(300, 0, -1)]
        self.assertEqual(sizes, sorted(sizes, reverse=True))
