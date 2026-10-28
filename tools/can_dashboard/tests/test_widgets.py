import time
from tools.can_dashboard.tests.tk_support import event_supported, require_tk

tk = require_tk()
import unittest

from tools.can_dashboard import widgets


try:
    ROOT = tk.Tk()
    ROOT.withdraw()
except tk.TclError:
    ROOT = None

TK_AVAILABLE = ROOT is not None


class EventCapabilityTest(unittest.TestCase):
    def test_unrelated_tcl_errors_are_not_treated_as_missing_events(self):
        class BrokenWidget:
            def event_generate(self, sequence, **options):
                raise tk.TclError("unexpected binding failure")

        with self.assertRaisesRegex(tk.TclError, "unexpected binding failure"):
            event_supported(BrokenWidget(), "<TouchpadScroll>")


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


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

    def _settle(self, predicate, timeout=3.0):
        """Run the event loop until predicate holds, or time runs out."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            self.window.update()
            if predicate():
                return True
            time.sleep(0.02)
        return False

    def test_the_scrollbar_appears_for_taller_content(self):
        self.assertTrue(self.scroller.scrollbar.winfo_ismapped())

    def test_the_wheel_keeps_the_scrollbar_and_the_offset(self):
        self.tall.event_generate("<MouseWheel>", delta=-120)
        self.window.update()
        self.assertTrue(self.scroller.scrollbar.winfo_ismapped())
        self.assertGreater(self._offset(), 0)

    def test_content_that_asks_for_less_room_puts_the_scrollbar_away(self):
        self.tall.configure(height=40)
        self.assertTrue(
            self._settle(lambda: not self.scroller.scrollbar.winfo_ismapped()),
            "the scrollbar stayed for content that fits",
        )

    def test_content_that_asks_for_more_room_brings_the_scrollbar_back(self):
        self.tall.configure(height=40)
        self.assertTrue(
            self._settle(lambda: not self.scroller.scrollbar.winfo_ismapped())
        )
        self.tall.configure(height=1200)
        self.assertTrue(
            self._settle(lambda: self.scroller.scrollbar.winfo_ismapped()),
            "the scrollbar stayed away from content that overflows",
        )
        region = self.scroller.canvas.bbox("all")
        self.assertGreaterEqual(region[3], 1200)
        self.tall.event_generate("<MouseWheel>", delta=-120)
        self.window.update()
        self.assertGreater(self._offset(), 0)

    def test_the_canvas_keeps_one_width_in_both_scrollbar_states(self):
        self.window.update()
        with_bar = self.scroller.canvas.winfo_width()
        self.tall.configure(height=40)
        self.assertTrue(
            self._settle(lambda: not self.scroller.scrollbar.winfo_ismapped())
        )
        self.assertEqual(self.scroller.canvas.winfo_width(), with_bar)

    def test_wheel_over_the_content_scrolls(self):
        self.tall.event_generate("<MouseWheel>", delta=-120)
        self.window.update_idletasks()
        self.assertGreater(self._offset(), 0)

    def test_trackpad_gesture_over_the_content_scrolls(self):
        if not event_supported(ROOT, "<TouchpadScroll>"):
            self.skipTest("TouchpadScroll is unavailable in this Tk build")
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
        self.window.update_idletasks()
        self.assertEqual(self._offset(), 0.0)

    def test_touchpad_events_outside_the_scroller_are_ignored(self):
        if not event_supported(ROOT, "<TouchpadScroll>"):
            self.skipTest("TouchpadScroll is unavailable in this Tk build")
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
            icon="plug",
            tooltip="Open the PCAN channel",
        )
        self.addCleanup(self.button.destroy)

    def items(self, tag, button=None):
        face = (button or self.button).face
        return face.find_withtag(tag)

    def caption(self, button=None):
        face = (button or self.button).face
        (item,) = face.find_withtag("caption")
        return face.itemcget(item, "text")

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

    def test_the_face_draws_no_ring_of_its_own(self):
        face = self.button.face
        self.assertEqual(face.winfo_class(), "Canvas")
        self.assertEqual(int(face.cget("highlightthickness")), 0)
        self.assertEqual(int(face.cget("borderwidth")), 0)
        self.assertEqual(int(tk.Frame.cget(self.button, "highlightthickness")), 0)

    def test_the_frame_background_is_the_one_pixel_border(self):
        self.assertEqual(self.button.border_color(), BUTTON_COLORS["border"])
        self.assertEqual(
            self.button.winfo_reqwidth(),
            self.button.face.winfo_reqwidth() + 2,
        )
        self.assertEqual(
            self.button.winfo_reqheight(),
            self.button.face.winfo_reqheight() + 2,
        )
        self.button.configure(lit=True)
        self.assertEqual(self.button.border_color(), BUTTON_COLORS["lit"])

    def test_keyboard_focus_shows_in_the_border(self):
        self.button._on_focus_in()
        self.assertEqual(self.button.border_color(), BUTTON_COLORS["focus"])
        self.button._on_focus_out()
        self.assertEqual(self.button.border_color(), BUTTON_COLORS["border"])

    def test_face_and_frame_options_share_configure_and_cget(self):
        self.button.configure({"text": "ACK"}, cursor="arrow", icon="exchange")
        self.assertEqual(self.button.cget("text"), "ACK")
        self.assertEqual(self.caption(), "ACK")
        self.assertEqual(self.button.cget("icon"), "exchange")
        self.assertEqual(str(self.button.cget("cursor")), "arrow")

    def test_the_pointer_reaches_the_button_through_its_face(self):
        for widget in (self.button, self.button.face):
            for sequence in ("<Button-1>", "<Enter>", "<Leave>"):
                with self.subTest(widget=str(widget), sequence=sequence):
                    self.assertTrue(widget.bind(sequence))
        self.assertIs(self.button.tooltip.widget, self.button.face)

    def test_the_icon_precedes_the_caption_and_takes_its_color(self):
        left, top, right, bottom = self.button.icon_box()
        face = self.button.face
        (caption,) = self.items("caption")
        self.assertLess(right, face.coords(caption)[0])
        self.assertGreater(top, 0)
        self.assertLess(bottom, face.winfo_reqheight())
        ink = self.items(widgets.icons.INK_FILL)
        self.assertGreater(len(ink), 1)
        for item in ink:
            self.assertEqual(face.itemcget(item, "fill"), BUTTON_COLORS["text"])
        self.button.configure(lit=True)
        for item in ink:
            self.assertEqual(
                face.itemcget(item, "fill"), BUTTON_COLORS["lit_text"]
            )

    def test_a_cut_takes_the_face_color_of_every_state(self):
        moon = widgets.ToolButton(
            ROOT,
            text="DARK",
            command=lambda: None,
            colors=BUTTON_COLORS,
            icon="moon",
        )
        self.addCleanup(moon.destroy)
        (cut,) = self.items(widgets.icons.CUT_FILL, moon)
        self.assertEqual(moon.face.itemcget(cut, "fill"), BUTTON_COLORS["face"])
        moon._on_enter()
        self.assertEqual(moon.face.itemcget(cut, "fill"), BUTTON_COLORS["hover"])
        moon.configure(lit=True)
        self.assertEqual(moon.face.itemcget(cut, "fill"), BUTTON_COLORS["lit"])

    def test_the_icon_and_its_gap_widen_the_button(self):
        plain = widgets.ToolButton(
            ROOT,
            text="CONNECT",
            command=lambda: None,
            colors=BUTTON_COLORS,
        )
        self.addCleanup(plain.destroy)
        self.assertIsNone(plain.icon_box())
        left, _top, right, _bottom = self.button.icon_box()
        side = right - left
        self.assertEqual(
            self.button.winfo_reqwidth() - plain.winfo_reqwidth(),
            side + round(side * widgets.ToolButton.ICON_GAP),
        )
        self.button.configure(text="")
        self.assertEqual(self.items("caption"), ())
        self.assertEqual(
            self.button.face.winfo_reqwidth(),
            side + 2 * (8 + 2),
        )

    def test_an_unknown_icon_is_refused(self):
        with self.assertRaises(ValueError):
            self.button.configure(icon="rocket")
        self.assertEqual(self.button.cget("icon"), "plug")

    def test_a_stretched_face_centers_the_icon_and_the_caption(self):
        window = tk.Toplevel(ROOT)
        self.addCleanup(window.destroy)
        button = widgets.ToolButton(
            window,
            text="ADD",
            command=lambda: None,
            colors=BUTTON_COLORS,
            icon="plus",
        )
        button.pack(fill="x")
        window.geometry("300x60")
        window.update()
        face = button.face
        left = button.icon_box()[0]
        (caption,) = self.items("caption", button)
        right = face.bbox(caption)[2]
        self.assertAlmostEqual(left, face.winfo_width() - right, delta=3)

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
