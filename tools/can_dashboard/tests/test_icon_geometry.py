import unittest

from tools.can_dashboard import icons


def part_points(part):
    if isinstance(part, (icons.Stroke, icons.Outline, icons.Fill)):
        return part.points
    return (
        (part.x - part.radius, part.y - part.radius),
        (part.x + part.radius, part.y + part.radius),
    )


class IconGeometryTest(unittest.TestCase):
    def test_every_icon_stays_inside_its_grid_square(self):
        for name, parts in icons.ICONS.items():
            for part in parts:
                margin = getattr(part, "width", 0.0) / 2
                for x, y in part_points(part):
                    with self.subTest(icon=name, part=type(part).__name__):
                        self.assertGreaterEqual(min(x, y) - margin, -0.2)
                        self.assertLessEqual(max(x, y) + margin, icons.GRID + 0.2)

    def test_an_arc_arrow_points_along_its_arc(self):
        stroke, head = icons.arc_arrow(8.0, 8.0, 5.0, 0.0, 90.0)
        self.assertAlmostEqual(stroke.points[0][0], 13.0)
        self.assertAlmostEqual(stroke.points[-1][1], 3.0)
        tip = head.points[0]
        self.assertLess(tip[0], stroke.points[-1][0])
        self.assertAlmostEqual(tip[1], 3.0)
