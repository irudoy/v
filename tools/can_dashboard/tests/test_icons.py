from tools.can_dashboard.tests.tk_support import require_tk

tk = require_tk()
import unittest

from tools.can_dashboard import icons


try:
    ROOT = tk.Tk()
    ROOT.withdraw()
except tk.TclError:
    ROOT = None

TK_AVAILABLE = ROOT is not None


def tearDownModule():
    if ROOT is not None:
        ROOT.destroy()


@unittest.skipUnless(TK_AVAILABLE, "Tk display is unavailable")
class IconDrawingTest(unittest.TestCase):
    def setUp(self):
        self.canvas = tk.Canvas(ROOT, width=80, height=80)
        self.addCleanup(self.canvas.destroy)

    def test_every_icon_draws_inside_its_square_at_button_size(self):
        for name in icons.ICONS:
            with self.subTest(icon=name):
                self.canvas.delete("all")
                items = icons.draw(self.canvas, name, 10, 20, 13, tags=("icon",))
                self.assertTrue(items)
                left, top, right, bottom = self.canvas.bbox("icon")
                self.assertGreaterEqual(left, 10 - 2)
                self.assertGreaterEqual(top, 20 - 2)
                self.assertLessEqual(right, 10 + 13 + 2)
                self.assertLessEqual(bottom, 20 + 13 + 2)

    def test_paint_colors_ink_and_cut_items(self):
        icons.draw(self.canvas, "moon", 0, 0, 16)
        icons.draw(self.canvas, "stopwatch", 20, 0, 16)
        icons.paint(self.canvas, "#112233", "#445566")
        for item in self.canvas.find_withtag(icons.INK_FILL):
            self.assertEqual(self.canvas.itemcget(item, "fill"), "#112233")
        for item in self.canvas.find_withtag(icons.INK_OUTLINE):
            self.assertEqual(self.canvas.itemcget(item, "outline"), "#112233")
        (cut,) = self.canvas.find_withtag(icons.CUT_FILL)
        self.assertEqual(self.canvas.itemcget(cut, "fill"), "#445566")

    def test_an_unknown_part_is_refused(self):
        icons.ICONS["test-unknown"] = (object(),)
        self.addCleanup(icons.ICONS.pop, "test-unknown")
        with self.assertRaises(TypeError):
            icons.draw(self.canvas, "test-unknown", 0, 0, 16)


if __name__ == "__main__":
    unittest.main()
