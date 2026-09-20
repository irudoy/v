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

    def test_items_stack_above_the_row_frames_that_hold_them(self):
        self.bar.layout(2000)
        self.root.update_idletasks()
        order = self.bar.winfo_children()
        frames = [
            index
            for index, child in enumerate(order)
            if child.winfo_class() == "Frame"
        ]
        for widget, _align in self.bar._items:
            self.assertGreater(order.index(widget), max(frames))

    def test_wrapped_items_stay_above_their_row_frames(self):
        self.bar.layout(240)
        self.root.update_idletasks()
        order = self.bar.winfo_children()
        for widget, _align in self.bar._items:
            frame = widget.nametowidget(widget.pack_info()["in"])
            self.assertGreater(order.index(widget), order.index(frame))

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
