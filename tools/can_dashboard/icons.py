"""Vector icons of the dashboard buttons, drawn on a Tk canvas.

An icon is a list of strokes and shapes on a square grid of GRID units, so it
scales with the text of its button and stays sharp at every display scale,
where a bitmap would be resampled. Ink items take the text color of the
button and cut items take its face color; `INK_FILL`, `INK_OUTLINE`, and
`CUT_FILL` tag the items, so the button repaints an icon without drawing it
again.
"""

from __future__ import annotations

from dataclasses import dataclass
import math


GRID = 16.0
STROKE = 1.7
INK_FILL = "ink-fill"
INK_OUTLINE = "ink-outline"
CUT_FILL = "cut-fill"


@dataclass(frozen=True)
class Stroke:
    """Open polyline in ink with round ends and joins."""

    points: tuple
    width: float = STROKE


@dataclass(frozen=True)
class Outline:
    """Closed polygon outline in ink."""

    points: tuple
    width: float = STROKE


@dataclass(frozen=True)
class Fill:
    """Filled polygon in ink."""

    points: tuple


@dataclass(frozen=True)
class Disc:
    """Filled circle in ink, or in the face color when it cuts the ink."""

    x: float
    y: float
    radius: float
    cut: bool = False


@dataclass(frozen=True)
class Ring:
    """Circle outline in ink."""

    x: float
    y: float
    radius: float
    width: float = STROKE


def arc(x, y, radius, start, extent, step=10.0):
    """Points of a circle arc; angles in degrees, counterclockwise from +x."""
    count = max(2, math.ceil(abs(extent) / step) + 1)
    points = []
    for index in range(count):
        angle = math.radians(start + extent * index / (count - 1))
        points.append((x + radius * math.cos(angle), y - radius * math.sin(angle)))
    return tuple(points)


def head(base, angle, length=3.6, half_width=2.9):
    """Arrowhead whose base centre is base, pointing along angle in degrees."""
    dx = math.cos(math.radians(angle))
    dy = -math.sin(math.radians(angle))
    tip = (base[0] + dx * length, base[1] + dy * length)
    return Fill((
        tip,
        (base[0] - dy * half_width, base[1] + dx * half_width),
        (base[0] + dy * half_width, base[1] - dx * half_width),
    ))


def arc_arrow(x, y, radius, start, extent):
    """Arc stroke with an arrowhead at its end, along the arc direction."""
    points = arc(x, y, radius, start, extent)
    end = start + extent
    return (Stroke(points), head(points[-1], end + math.copysign(90.0, extent)))


def rectangle(left, top, right, bottom):
    return ((left, top), (right, top), (right, bottom), (left, bottom))


def _broadcast():
    parts = [Disc(8.0, 8.0, 1.9)]
    for radius in (4.2, 7.0):
        parts.append(Stroke(arc(8.0, 8.0, radius, -40.0, 80.0)))
        parts.append(Stroke(arc(8.0, 8.0, radius, 140.0, 80.0)))
    return tuple(parts)


def _sun():
    parts = [Disc(8.0, 8.0, 3.0)]
    for step in range(8):
        angle = math.radians(step * 45.0)
        parts.append(Stroke(
            (
                (8.0 + 5.0 * math.cos(angle), 8.0 - 5.0 * math.sin(angle)),
                (8.0 + 7.0 * math.cos(angle), 8.0 - 7.0 * math.sin(angle)),
            ),
            1.5,
        ))
    return tuple(parts)


def _plug():
    return (
        Stroke(((6.0, 1.3), (6.0, 5.0))),
        Stroke(((10.0, 1.3), (10.0, 5.0))),
        Fill((
            (3.5, 4.6), (12.5, 4.6), (12.5, 8.4), (10.0, 11.4),
            (6.0, 11.4), (3.5, 8.4),
        )),
        Stroke(((8.0, 11.0), (8.0, 14.8))),
    )


ICONS = {
    # Transport and recording.
    "play": (Fill(((4.0, 2.2), (13.8, 8.0), (4.0, 13.8))),),
    "pause": (
        Fill(rectangle(3.5, 2.5, 6.6, 13.5)),
        Fill(rectangle(9.4, 2.5, 12.5, 13.5)),
    ),
    "stop": (Fill(rectangle(3.0, 3.0, 13.0, 13.0)),),
    "dot": (Disc(8.0, 8.0, 5.5),),
    "broadcast": _broadcast(),
    "fast-forward": (
        Fill(((1.5, 3.2), (8.0, 8.0), (1.5, 12.8))),
        Fill(((8.0, 3.2), (14.5, 8.0), (8.0, 12.8))),
    ),
    "repeat": (
        Stroke(((2.8, 9.6), (2.8, 5.0), (11.0, 5.0))),
        head((11.0, 5.0), 0.0),
        Stroke(((13.2, 6.4), (13.2, 11.0), (5.0, 11.0))),
        head((5.0, 11.0), 180.0),
    ),
    "mark-in": (
        Stroke(((6.2, 2.2), (2.8, 2.2), (2.8, 13.8), (6.2, 13.8))),
        Fill(((7.6, 4.2), (13.8, 8.0), (7.6, 11.8))),
    ),
    "mark-out": (
        Fill(((2.2, 4.2), (8.4, 8.0), (2.2, 11.8))),
        Stroke(((9.8, 2.2), (13.2, 2.2), (13.2, 13.8), (9.8, 13.8))),
    ),
    "floppy": (
        Outline(((2.4, 2.4), (11.2, 2.4), (13.6, 4.8), (13.6, 13.6), (2.4, 13.6))),
        Fill(rectangle(5.0, 2.4, 10.4, 6.4)),
        Fill(rectangle(5.0, 9.4, 11.0, 13.6)),
    ),
    # Sources and outputs.
    "plug": _plug(),
    "exchange": (
        Stroke(((2.2, 5.0), (10.6, 5.0))),
        head((10.6, 5.0), 0.0),
        Stroke(((13.8, 11.0), (5.4, 11.0))),
        head((5.4, 11.0), 180.0),
    ),
    "flask": (
        Outline((
            (6.2, 1.8), (9.8, 1.8), (9.8, 6.2), (13.8, 13.6),
            (2.2, 13.6), (6.2, 6.2),
        )),
        Fill(((4.5, 9.4), (11.5, 9.4), (13.8, 13.6), (2.2, 13.6))),
    ),
    "folder": (
        Outline((
            (1.6, 2.8), (6.2, 2.8), (7.8, 4.6), (14.4, 4.6), (14.4, 13.4),
            (1.6, 13.4),
        )),
        Fill(rectangle(1.6, 6.6, 14.4, 13.4)),
    ),
    "share": (
        Stroke(((4.0, 8.0), (12.0, 3.5)), 1.4),
        Stroke(((4.0, 8.0), (12.0, 12.5)), 1.4),
        Disc(12.0, 3.5, 2.3),
        Disc(4.0, 8.0, 2.3),
        Disc(12.0, 12.5, 2.3),
    ),
    "download": (
        Stroke(((8.0, 1.6), (8.0, 7.2))),
        head((8.0, 7.2), -90.0),
        Stroke(((2.4, 10.2), (2.4, 14.0), (13.6, 14.0), (13.6, 10.2))),
    ),
    # Views.
    "grid": (
        Fill(rectangle(2.0, 2.0, 7.0, 7.0)),
        Fill(rectangle(9.0, 2.0, 14.0, 7.0)),
        Fill(rectangle(2.0, 9.0, 7.0, 14.0)),
        Fill(rectangle(9.0, 9.0, 14.0, 14.0)),
    ),
    "stopwatch": (
        Ring(8.0, 9.4, 5.6),
        Fill(rectangle(6.2, 0.8, 9.8, 2.4)),
        Stroke(((8.0, 2.4), (8.0, 3.8))),
        Stroke(((8.0, 9.4), (10.6, 6.8))),
    ),
    "sun": _sun(),
    "moon": (
        Disc(7.6, 8.4, 6.2),
        Disc(11.0, 5.0, 5.0, cut=True),
    ),
    "gauge": (
        Stroke(arc(8.0, 10.6, 6.6, 0.0, 180.0)),
        Stroke(((8.0, 10.6), (11.6, 6.4))),
        Disc(8.0, 10.6, 1.7),
    ),
    "list": tuple(
        part
        for row in (3.5, 8.0, 12.5)
        for part in (Disc(2.8, row, 1.3), Stroke(((6.2, row), (14.0, row))))
    ),
    # Editing.
    "circular-arrow": arc_arrow(8.4, 8.6, 5.4, 110.0, -290.0),
    "plus": (
        Stroke(((8.0, 2.4), (8.0, 13.6)), 2.0),
        Stroke(((2.4, 8.0), (13.6, 8.0)), 2.0),
    ),
    "minus": (Stroke(((2.4, 8.0), (13.6, 8.0)), 2.0),),
    "up": (
        Stroke(((8.0, 14.0), (8.0, 6.4)), 1.9),
        Fill(((2.8, 7.6), (8.0, 1.8), (13.2, 7.6))),
    ),
    "down": (
        Stroke(((8.0, 2.0), (8.0, 9.6)), 1.9),
        Fill(((2.8, 8.4), (8.0, 14.2), (13.2, 8.4))),
    ),
    "cross": (
        Stroke(((3.4, 3.4), (12.6, 12.6)), 2.0),
        Stroke(((12.6, 3.4), (3.4, 12.6)), 2.0),
    ),
    "check": (Stroke(((2.4, 8.6), (6.2, 12.4), (13.6, 3.8)), 2.0),),
}


def draw(canvas, name, x, y, size, tags=()):
    """Draw icon name with its grid square at x, y and size pixels wide."""
    scale = size / GRID
    tags = tuple(tags)

    def at(points):
        return [
            value
            for px, py in points
            for value in (x + px * scale, y + py * scale)
        ]

    def width(value):
        return max(1.0, value * scale)

    items = []
    for part in ICONS[name]:
        if isinstance(part, Stroke):
            items.append(canvas.create_line(
                *at(part.points),
                width=width(part.width),
                capstyle="round",
                joinstyle="round",
                tags=(*tags, INK_FILL),
            ))
        elif isinstance(part, Outline):
            items.append(canvas.create_polygon(
                *at(part.points),
                fill="",
                width=width(part.width),
                joinstyle="round",
                tags=(*tags, INK_OUTLINE),
            ))
        elif isinstance(part, Fill):
            items.append(canvas.create_polygon(
                *at(part.points),
                outline="",
                tags=(*tags, INK_FILL),
            ))
        elif isinstance(part, Disc):
            items.append(canvas.create_oval(
                *at((
                    (part.x - part.radius, part.y - part.radius),
                    (part.x + part.radius, part.y + part.radius),
                )),
                outline="",
                tags=(*tags, CUT_FILL if part.cut else INK_FILL),
            ))
        elif isinstance(part, Ring):
            items.append(canvas.create_oval(
                *at((
                    (part.x - part.radius, part.y - part.radius),
                    (part.x + part.radius, part.y + part.radius),
                )),
                fill="",
                width=width(part.width),
                tags=(*tags, INK_OUTLINE),
            ))
        else:
            raise TypeError(f"unknown icon part {part!r}")
    return items


def paint(canvas, ink, cut, tag=None):
    """Color the ink and cut items of the icons on canvas, or of tag."""
    def selector(role):
        return role if tag is None else f"{role}&&{tag}"

    canvas.itemconfigure(selector(INK_FILL), fill=ink)
    canvas.itemconfigure(selector(INK_OUTLINE), outline=ink)
    canvas.itemconfigure(selector(CUT_FILL), fill=cut)
