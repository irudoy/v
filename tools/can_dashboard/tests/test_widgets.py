import tkinter as tk
import unittest

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


def _monospace(text, cell=7):
    return len(text) * cell


class TextFittingTest(unittest.TestCase):
    def test_text_that_fits_is_returned_unchanged(self):
        self.assertEqual(
            widgets.elide("Source: demo", _monospace, 200),
            "Source: demo",
        )

    def test_unknown_width_keeps_the_full_text(self):
        self.assertEqual(
            widgets.elide("Source: demo", _monospace, 0),
            "Source: demo",
        )

    def test_long_text_is_shortened_to_the_available_width(self):
        shortened = widgets.elide(
            "MLG: no complete snapshots, file not created",
            _monospace,
            140,
        )
        self.assertTrue(shortened.endswith(widgets.ELLIPSIS))
        self.assertLessEqual(_monospace(shortened), 140)
        self.assertTrue(
            "MLG: no complete snapshots, file not created".startswith(
                shortened[: -len(widgets.ELLIPSIS)]
            )
        )

    def test_hopeless_width_still_returns_the_ellipsis(self):
        self.assertEqual(widgets.elide("value", _monospace, 3), "...")


class MiddleElisionTest(unittest.TestCase):
    def test_text_that_fits_is_returned_unchanged(self):
        self.assertEqual(
            widgets.elide_middle("CVTC duty B1", _monospace, 200),
            "CVTC duty B1",
        )

    def test_unknown_width_keeps_the_full_text(self):
        self.assertEqual(
            widgets.elide_middle("CVTC duty B1", _monospace, 0),
            "CVTC duty B1",
        )

    def test_both_ends_of_a_long_text_are_kept(self):
        full = "Intake CVTC duty command B1"
        shortened = widgets.elide_middle(full, _monospace, 126)
        head, _ellipsis, tail = shortened.partition(widgets.ELLIPSIS)
        self.assertLessEqual(_monospace(shortened), 126)
        self.assertTrue(head and full.startswith(head))
        self.assertTrue(tail and full.endswith(tail))
        self.assertGreater(len(head), len(tail))

    def test_a_trailing_bank_suffix_keeps_labels_distinct(self):
        shortened = {
            widgets.elide_middle(full, _monospace, 119)
            for full in (
                "Exhaust CVTC actual B1",
                "Exhaust CVTC actual B2",
                "Exhaust CVTC duty B1 word",
                "Exhaust CVTC duty B2 word",
            )
        }
        self.assertEqual(len(shortened), 4)

    def test_hopeless_width_still_returns_the_ellipsis(self):
        self.assertEqual(widgets.elide_middle("value", _monospace, 3), "...")


class RowWrappingTest(unittest.TestCase):
    def test_items_stay_on_one_row_while_they_fit(self):
        self.assertEqual(
            widgets.wrap_rows((100, 100, 100), 340, 20),
            ((0, 1, 2),),
        )

    def test_narrow_width_wraps_into_more_rows(self):
        self.assertEqual(
            widgets.wrap_rows((100, 100, 100), 230, 20),
            ((0, 1), (2,)),
        )

    def test_single_item_wider_than_the_row_keeps_its_own_row(self):
        self.assertEqual(
            widgets.wrap_rows((400, 100), 200, 10),
            ((0,), (1,)),
        )

    def test_row_width_counts_the_gaps(self):
        self.assertEqual(widgets.row_width((100, 100, 100), 20), 340)
        self.assertEqual(widgets.row_width((), 20), 0)


class BalancedColumnsTest(unittest.TestCase):
    def test_a_full_row_is_kept(self):
        self.assertEqual(widgets.balanced_columns(4, 4), 4)
        self.assertEqual(widgets.balanced_columns(4, 9), 4)

    def test_a_leftover_item_is_avoided(self):
        self.assertEqual(widgets.balanced_columns(4, 3), 2)
        self.assertEqual(widgets.balanced_columns(5, 4), 3)
        self.assertEqual(widgets.balanced_columns(6, 4), 3)
        self.assertEqual(widgets.balanced_columns(3, 2), 2)

    def test_one_column_and_empty_grids(self):
        self.assertEqual(widgets.balanced_columns(4, 1), 1)
        self.assertEqual(widgets.balanced_columns(0, 3), 0)
        self.assertEqual(widgets.balanced_columns(4, 0), 0)


class LabelValueSplitTest(unittest.TestCase):
    def test_a_wide_row_keeps_both_widths(self):
        self.assertEqual(widgets.split_label_value(400, 120, 150, 80), (120, 150))

    def test_the_value_gives_way_before_the_label(self):
        self.assertEqual(widgets.split_label_value(240, 120, 150, 80), (120, 120))

    def test_the_label_shrinks_after_the_value_reaches_its_floor(self):
        self.assertEqual(widgets.split_label_value(180, 120, 150, 80), (100, 80))

    def test_the_parts_never_exceed_the_row(self):
        for available in range(1, 400, 7):
            with self.subTest(available=available):
                label, value = widgets.split_label_value(available, 170, 150, 80)
                self.assertLessEqual(label + value, max(available, 0))
                self.assertGreaterEqual(label, 0)
                self.assertGreater(value, 0)

    def test_an_unmeasured_row_keeps_the_declared_widths(self):
        self.assertEqual(widgets.split_label_value(0, 120, 150, 80), (120, 150))


class ColumnCountTest(unittest.TestCase):
    def test_columns_shrink_with_the_available_width(self):
        self.assertEqual(widgets.responsive_columns(8, 164, 1358, 5), 8)
        self.assertEqual(widgets.responsive_columns(8, 164, 700, 5), 4)
        self.assertEqual(widgets.responsive_columns(8, 164, 300, 5), 1)

    def test_column_count_never_exceeds_the_item_count(self):
        self.assertEqual(widgets.responsive_columns(4, 268, 4000, 6), 4)

    def test_unmeasured_width_keeps_the_declared_count(self):
        self.assertEqual(widgets.responsive_columns(4, 268, 0, 6), 4)


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class StatusFieldTest(unittest.TestCase):
    def setUp(self):
        self.root = ROOT
        self.variable = tk.StringVar(master=self.root, value="Control: idle")
        self.field = widgets.StatusField(
            self.root,
            self.variable,
            title="Last stream command",
            background="#1d2430",
            foreground="#e6edf3",
        )
        self.addCleanup(self.field.destroy)

    def test_field_follows_its_variable(self):
        self.variable.set("Control error: connect PCAN first")
        self.assertEqual(self.field.text, "Control error: connect PCAN first")

    def test_narrow_width_elides_the_displayed_text_only(self):
        self.variable.set("Control error: reconnect with Active/ACK enabled")
        self.field.set_available_width(90)
        self.assertTrue(self.field.cget("text").endswith(widgets.ELLIPSIS))
        self.assertEqual(
            self.field.text,
            "Control error: reconnect with Active/ACK enabled",
        )

    def test_tooltip_reports_the_title_and_the_full_text(self):
        self.variable.set("MLG: no complete snapshots, file not created")
        self.field.set_available_width(60)
        tooltip = self.field.tooltip_text()
        self.assertIn("Last stream command", tooltip)
        self.assertIn("MLG: no complete snapshots, file not created", tooltip)
        self.assertIn("Click to copy", tooltip)

    def test_reserved_width_survives_a_shorter_value(self):
        field = widgets.StatusField(
            self.root,
            self.variable,
            title="Loss counters",
            background="#1d2430",
            foreground="#8b949e",
            sample="Loss: 0 | Incomplete: 0 | Malformed: 0",
        )
        self.addCleanup(field.destroy)
        field.set_available_width(600)
        self.variable.set("Loss: 0 | Incomplete: 0 | Malformed: 0")
        self.root.update_idletasks()
        wide = field.winfo_reqwidth()
        self.variable.set("Loss: 0")
        self.root.update_idletasks()
        self.assertEqual(field.winfo_reqwidth(), wide)

    def test_reserved_field_elides_beyond_its_reserve(self):
        field = widgets.StatusField(
            self.root,
            self.variable,
            title="Loss counters",
            background="#1d2430",
            foreground="#8b949e",
            sample="Loss: 0",
        )
        self.addCleanup(field.destroy)
        field.set_available_width(600)
        self.variable.set("Loss: 4 | Incomplete: 12 | Malformed: 3")
        self.assertTrue(field.cget("text").endswith(widgets.ELLIPSIS))

    def test_outer_width_of_a_reserving_field_counts_its_border(self):
        field = widgets.StatusField(
            self.root,
            self.variable,
            title="Value",
            background="#1d2430",
            foreground="#e6edf3",
            anchor="e",
            reserve=150,
        )
        self.addCleanup(field.destroy)
        self.assertEqual(field.outer_width(150), field.winfo_reqwidth())
        self.assertLess(field.outer_width(104), field.outer_width(150))

    def test_outer_width_limit_keeps_the_whole_field_within_it(self):
        field = widgets.StatusField(
            self.root,
            self.variable,
            title="Value",
            background="#1d2430",
            foreground="#e6edf3",
            anchor="e",
            reserve=150,
        )
        self.addCleanup(field.destroy)
        for limit in (158, 131, 110, 64):
            with self.subTest(limit=limit):
                field.set_outer_width(limit)
                self.assertLessEqual(field.winfo_reqwidth(), limit)
        field.set_outer_width(400)
        self.assertEqual(field.winfo_reqwidth(), field.outer_width(150))

    def test_click_copies_the_full_text(self):
        self.variable.set("Source: PCAN_USBBUS1, 500000 bit/s, active/ACK")
        self.field.set_available_width(50)
        self.field.copy()
        self.assertEqual(
            self.root.clipboard_get(),
            "Source: PCAN_USBBUS1, 500000 bit/s, active/ACK",
        )


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class FlowBarTest(unittest.TestCase):
    def setUp(self):
        self.root = ROOT
        self.bar = widgets.FlowBar(self.root, spacing_x=10)
        for index in range(4):
            self.bar.add(
                tk.Label(self.bar, text=f"field {index}", width=14),
                align="left" if index < 2 else "right",
            )
        self.root.update_idletasks()
        self.addCleanup(self.bar.destroy)

    def test_wide_bar_keeps_one_row(self):
        self.bar.layout(2000)
        self.assertEqual(self.bar.rows, 1)

    def test_narrow_bar_wraps_instead_of_clipping(self):
        self.bar.layout(240)
        self.assertGreater(self.bar.rows, 1)

    def shown(self, width):
        window = tk.Toplevel(self.root)
        self.addCleanup(window.destroy)
        bar = widgets.FlowBar(window, spacing_x=10, spacing_y=6, pad_x=4, pad_y=3)
        bar.pack(fill="x")
        items = [
            bar.add(
                tk.Label(bar, text=f"field {index}", width=14),
                align="left" if index < 2 else "right",
            )
            for index in range(4)
        ]
        window.geometry(f"{width}x200")
        window.deiconify()
        window.update_idletasks()
        bar.layout(width)
        window.update_idletasks()
        window.update()
        return bar, items

    def test_items_are_placed_inside_the_bar_itself(self):
        bar, items = self.shown(1200)
        for item in items:
            self.assertEqual(item.winfo_manager(), "place")
            self.assertEqual(str(item.place_info()["in"]), str(bar))
        self.assertEqual(
            [child for child in bar.winfo_children() if child not in items],
            [],
        )

    def test_one_row_aligns_the_right_group_to_the_right_edge(self):
        bar, items = self.shown(1200)
        self.assertEqual(bar.rows, 1)
        self.assertEqual(len({item.winfo_y() for item in items}), 1)
        self.assertEqual(items[0].winfo_x(), 4)
        self.assertEqual(
            items[3].winfo_x() + items[3].winfo_reqwidth(),
            1200 - 4,
        )
        self.assertEqual(
            items[3].winfo_x() - (items[2].winfo_x() + items[2].winfo_reqwidth()),
            10,
        )
        self.assertLess(
            items[1].winfo_x() + items[1].winfo_reqwidth(),
            items[2].winfo_x(),
        )

    def test_wrapped_rows_flow_left_and_never_overlap(self):
        bar, items = self.shown(260)
        self.assertGreater(bar.rows, 1)
        boxes = [
            (
                item.winfo_x(),
                item.winfo_y(),
                item.winfo_x() + item.winfo_reqwidth(),
                item.winfo_y() + item.winfo_reqheight(),
            )
            for item in items
        ]
        for index, first in enumerate(boxes):
            self.assertLessEqual(first[2], 260)
            for second in boxes[index + 1:]:
                apart = (
                    first[2] <= second[0]
                    or second[2] <= first[0]
                    or first[3] <= second[1]
                    or second[3] <= first[1]
                )
                self.assertTrue(apart, (first, second))
        self.assertEqual({box[0] for box in boxes if box[1] == 3}, {4})

    def test_bar_height_follows_the_row_count(self):
        bar, items = self.shown(1200)
        row = items[0].winfo_reqheight()
        self.assertEqual(int(bar.cget("height")), row + 2 * 3)
        bar.layout(260)
        self.assertEqual(
            int(bar.cget("height")),
            bar.rows * row + (bar.rows - 1) * 3 + 2 * 3,
        )

    def test_a_wider_item_moves_its_neighbours(self):
        bar, items = self.shown(1200)
        before = items[1].winfo_x()
        items[0].configure(width=20)
        bar.update_idletasks()
        bar.layout(1200)
        bar.update_idletasks()
        self.assertGreater(items[1].winfo_x(), before)

    def test_available_width_reaches_status_fields(self):
        variable = tk.StringVar(
            master=self.root,
            value="Loss: 0 | Incomplete: 0 | Malformed: 0",
        )
        field = widgets.StatusField(
            self.bar,
            variable,
            title="Loss counters",
            background="#1d2430",
            foreground="#8b949e",
        )
        self.bar.add(field)
        self.root.update_idletasks()
        self.bar.layout(120)
        self.assertTrue(field.cget("text").endswith(widgets.ELLIPSIS))


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class ResponsiveGridTest(unittest.TestCase):
    def setUp(self):
        self.root = ROOT
        self.grid = widgets.ResponsiveGrid(
            self.root,
            min_column_width=100,
            spacing=6,
            min_from_children=False,
        )
        for index in range(8):
            self.grid.add(tk.Frame(self.grid, width=80, height=40))
        self.root.update_idletasks()
        self.addCleanup(self.grid.destroy)

    def test_wide_grid_uses_every_column(self):
        self.grid.layout(1000)
        self.assertEqual(self.grid.columns, 8)

    def test_narrow_grid_folds_into_fewer_columns(self):
        self.grid.layout(350)
        self.assertEqual(self.grid.columns, 3)
        self.grid.layout(120)
        self.assertEqual(self.grid.columns, 1)

    def test_cells_shrink_below_their_request_before_the_grid_folds(self):
        grid = widgets.ResponsiveGrid(
            self.root,
            min_column_width=100,
            spacing=6,
            min_from_children=False,
            balanced=True,
        )
        self.addCleanup(grid.destroy)
        for _ in range(4):
            grid.add(tk.Frame(grid, width=300, height=40))
        self.root.update_idletasks()
        grid.layout(430)
        self.assertEqual(grid.columns, 4)

    def test_a_balanced_grid_folds_four_cells_into_two_rows_of_two(self):
        grid = widgets.ResponsiveGrid(
            self.root,
            min_column_width=100,
            spacing=6,
            min_from_children=False,
            balanced=True,
        )
        self.addCleanup(grid.destroy)
        for _ in range(4):
            grid.add(tk.Frame(grid, width=300, height=40))
        self.root.update_idletasks()
        grid.layout(400)
        self.assertEqual(grid.columns, 2)
        grid.layout(150)
        self.assertEqual(grid.columns, 1)

    def test_columns_never_go_below_the_widest_child(self):
        grid = widgets.ResponsiveGrid(self.root, min_column_width=50, spacing=6)
        self.addCleanup(grid.destroy)
        for _ in range(4):
            grid.add(tk.Frame(grid, width=200, height=40))
        self.root.update_idletasks()
        grid.layout(500)
        self.assertEqual(grid.columns, 2)


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class ScrollableFrameTest(unittest.TestCase):
    def setUp(self):
        self.window = tk.Toplevel(ROOT)
        self.window.geometry("260x180+80+80")
        self.addCleanup(self.window.destroy)
        self.outside = tk.Label(self.window, text="outside")
        self.outside.pack(side="top", fill="x")
        self.scroller = widgets.ScrollableFrame(self.window, background="#0d1117")
        self.scroller.pack(side="top", fill="both", expand=True)
        self.tall = tk.Frame(
            self.scroller.content,
            width=200,
            height=1200,
            bg="#161b22",
        )
        self.tall.pack(fill="both", expand=True)
        self.window.update()

    def _offset(self):
        return self.scroller.canvas.yview()[0]

    @staticmethod
    def _gesture(delta_y):
        return delta_y & 0xFFFF

    def test_the_scrollbar_appears_for_taller_content(self):
        self.assertTrue(self.scroller.scrollbar.winfo_ismapped())

    def test_wheel_over_the_content_scrolls(self):
        self.tall.event_generate("<MouseWheel>", delta=-120)
        self.window.update_idletasks()
        self.assertGreater(self._offset(), 0)

    def test_trackpad_gesture_over_the_content_scrolls(self):
        for _ in range(widgets.TOUCHPAD_INTERVAL):
            self.tall.event_generate("<TouchpadScroll>", delta=self._gesture(-3))
        self.window.update_idletasks()
        moved = self._offset()
        self.assertGreater(moved, 0)
        for _ in range(widgets.TOUCHPAD_INTERVAL):
            self.tall.event_generate("<TouchpadScroll>", delta=self._gesture(3))
        self.window.update_idletasks()
        self.assertLess(self._offset(), moved)

    def test_scroll_events_outside_the_scroller_are_ignored(self):
        self.outside.event_generate("<MouseWheel>", delta=-120)
        for _ in range(widgets.TOUCHPAD_INTERVAL):
            self.outside.event_generate("<TouchpadScroll>", delta=self._gesture(-3))
        self.window.update_idletasks()
        self.assertEqual(self._offset(), 0.0)

    def test_events_over_the_scrollbar_leave_it_to_the_stock_bindings(self):
        self.assertFalse(
            self.scroller._targets(
                type("Event", (), {"widget": self.scroller.scrollbar})()
            )
        )


if __name__ == "__main__":
    unittest.main()


class HeroValueSizeTest(unittest.TestCase):
    def test_wide_cards_use_the_largest_value_font(self):
        self.assertEqual(widgets.hero_value_size(400), 22)
        self.assertEqual(widgets.hero_value_size(170), 22)

    def test_value_font_steps_down_with_the_card_width(self):
        sizes = [widgets.hero_value_size(width) for width in (169, 129, 99, 75)]
        self.assertEqual(sizes, [18, 15, 12, widgets.HERO_VALUE_SIZE_FLOOR])

    def test_value_font_never_grows_as_the_card_narrows(self):
        sizes = [widgets.hero_value_size(width) for width in range(300, 0, -1)]
        self.assertEqual(sizes, sorted(sizes, reverse=True))


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


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class ToolButtonTest(unittest.TestCase):
    def setUp(self):
        self.calls = []
        self.button = widgets.ToolButton(
            ROOT,
            text="CONNECT",
            command=lambda: self.calls.append("pressed"),
            colors=BUTTON_COLORS,
            tooltip="Open the PCAN channel",
        )
        self.addCleanup(self.button.destroy)

    def test_invoke_runs_the_command(self):
        self.button.invoke()
        self.assertEqual(self.calls, ["pressed"])

    def test_unlit_button_uses_the_face_colors(self):
        self.assertFalse(self.button.lit)
        self.assertEqual(self.button.cget("bg"), BUTTON_COLORS["face"])
        self.assertEqual(self.button.cget("fg"), BUTTON_COLORS["text"])

    def test_lit_state_arrives_with_the_label_options(self):
        self.button.configure(text="DISCONNECT", lit=True)
        self.assertTrue(self.button.lit)
        self.assertEqual(self.button.cget("text"), "DISCONNECT")
        self.assertEqual(self.button.cget("bg"), BUTTON_COLORS["lit"])
        self.assertEqual(self.button.cget("fg"), BUTTON_COLORS["lit_text"])
        self.button.config(lit=False)
        self.assertEqual(self.button.cget("bg"), BUTTON_COLORS["face"])

    def test_lit_role_selects_the_lit_color(self):
        record = widgets.ToolButton(
            ROOT,
            text="REC",
            command=lambda: None,
            colors=BUTTON_COLORS,
            lit_role="record",
            lit=True,
        )
        self.addCleanup(record.destroy)
        self.assertEqual(record.cget("bg"), BUTTON_COLORS["record"])

    def test_hover_never_repaints_a_lit_button(self):
        self.button.configure(lit=True)
        self.button._on_enter()
        self.assertEqual(self.button.cget("bg"), BUTTON_COLORS["lit"])
        self.button.configure(lit=False)
        self.assertEqual(self.button.cget("bg"), BUTTON_COLORS["hover"])
        self.button._on_leave()
        self.assertEqual(self.button.cget("bg"), BUTTON_COLORS["face"])


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class HeroRowTest(unittest.TestCase):
    def setUp(self):
        self.window = tk.Toplevel(ROOT)
        self.addCleanup(self.window.destroy)
        self.row = widgets.HeroRow(self.window, spacing=6, min_card_width=40)
        self.row.pack(fill="x")

    def cards(self, count):
        return [
            tk.Frame(self.row, width=300, height=60) for _index in range(count)
        ]

    def show(self, width):
        self.window.geometry(f"{width}x200")
        self.window.deiconify()
        self.window.update_idletasks()
        self.window.update()

    def test_cards_share_one_row_at_every_width(self):
        cards = self.cards(9)
        self.row.set_cards(cards)
        for width in (1400, 700, 420):
            with self.subTest(width=width):
                self.show(width)
                self.assertEqual({card.winfo_y() for card in cards}, {0})
                rows = {int(card.grid_info()["row"]) for card in cards}
                self.assertEqual(rows, {0})

    def test_cards_keep_equal_widths(self):
        cards = self.cards(7)
        self.row.set_cards(cards)
        self.show(1000)
        widths = [card.winfo_width() for card in cards]
        self.assertLessEqual(max(widths) - min(widths), 1)

    def test_fewer_cards_release_their_columns(self):
        cards = self.cards(6)
        self.row.set_cards(cards)
        self.row.set_cards(cards[:2])
        self.show(800)
        self.assertEqual(self.row.cards, tuple(cards[:2]))
        self.assertEqual(cards[3].winfo_manager(), "")
        self.assertGreater(cards[0].winfo_width(), 300)
        self.assertEqual(int(self.row.columnconfigure(4)["weight"]), 0)

    def test_destroyed_cards_are_replaced_without_an_error(self):
        first = self.cards(3)
        self.row.set_cards(first)
        for card in first:
            card.destroy()
        second = self.cards(4)
        self.row.set_cards(second)
        self.assertEqual(self.row.cards, tuple(second))

    def test_an_empty_row_is_accepted(self):
        self.row.set_cards(self.cards(2))
        self.row.set_cards(())
        self.assertEqual(self.row.cards, ())


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class TooltipOptionsTest(unittest.TestCase):
    def test_status_field_forwards_the_tooltip_colors(self):
        variable = tk.StringVar(master=ROOT, value="Schema: VERIFIED")
        field = widgets.StatusField(
            ROOT,
            variable,
            title="Wire schema state",
            background="#ffffff",
            foreground="#000000",
            tooltip_options={"background": "#f2f2f2", "foreground": "#000000"},
        )
        self.addCleanup(field.destroy)
        self.assertEqual(field.tooltip.background, "#f2f2f2")
        self.assertEqual(field.tooltip.foreground, "#000000")
