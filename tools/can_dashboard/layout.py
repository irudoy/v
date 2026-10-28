"""Pure layout and text measurements of the telemetry dashboard."""

import math


ELLIPSIS = "..."
SCROLLBAR_RESERVE = 14
RELAYOUT_DELAY_MS = 16
CONTENT_WATCH_MS = 100
WHEEL_NOTCH = 120.0
WHEEL_PIXELS = 60
TOUCHPAD_PIXELS = 20
TOUCHPAD_INTERVAL = 5


def elide(text, measure, available, ellipsis=ELLIPSIS):
    """Shorten text with a trailing ellipsis until it fits a pixel width."""
    if not text or available <= 0 or measure(text) <= available:
        return text
    low = 0
    high = len(text)
    shortened = ellipsis
    while low <= high:
        middle = (low + high) // 2
        candidate = text[:middle].rstrip() + ellipsis
        if measure(candidate) <= available:
            shortened = candidate
            low = middle + 1
        else:
            high = middle - 1
    return shortened


def elide_middle(text, measure, available, ellipsis=ELLIPSIS, tail_share=0.4):
    """Shorten text around a middle ellipsis until it fits a pixel width.

    The kept tail holds tail_share of the kept characters, so labels that
    differ only in a trailing bank or channel suffix stay distinct.
    """
    if not text or available <= 0 or measure(text) <= available:
        return text
    low = 0
    high = len(text)
    shortened = ellipsis
    while low <= high:
        kept = (low + high) // 2
        tail = min(kept, math.ceil(kept * tail_share - 1e-9))
        head = kept - tail
        candidate = (
            text[:head].rstrip()
            + ellipsis
            + (text[len(text) - tail:].lstrip() if tail else "")
        )
        if measure(candidate) <= available:
            shortened = candidate
            low = kept + 1
        else:
            high = kept - 1
    return shortened


def row_width(widths, spacing):
    """Return the width one row of items needs, gaps included."""
    if not widths:
        return 0
    return sum(widths) + spacing * (len(widths) - 1)


def wrap_rows(widths, available, spacing):
    """Group item indexes into rows that stay inside the available width."""
    rows = []
    current = []
    used = 0
    for index, width in enumerate(widths):
        needed = width if not current else width + spacing
        if current and used + needed > available:
            rows.append(tuple(current))
            current = [index]
            used = width
            continue
        current.append(index)
        used += needed
    if current:
        rows.append(tuple(current))
    return tuple(rows)


def responsive_columns(count, minimum_width, available, spacing):
    """Return how many equal columns of at least minimum_width fit."""
    if count <= 0:
        return 0
    if available <= 0 or minimum_width <= 0:
        return count
    columns = (available + spacing) // (minimum_width + spacing)
    return max(1, min(count, int(columns)))


def balanced_columns(count, maximum):
    """Return the column count that fills every row evenly.

    Four items that fit three to a row use two rows of two instead of a row
    of three and a single leftover item.
    """
    if count <= 0 or maximum <= 0:
        return 0
    maximum = min(count, maximum)
    rows = -(-count // maximum)
    return -(-count // rows)


def split_label_value(available, label_width, value_width, value_minimum):
    """Share the width of a panel row between its label and its value.

    The value keeps value_width while the label fits beside it and gives way
    down to value_minimum; only then does the label lose width. Returns the
    pixel widths (label, value).
    """
    if available <= 0:
        return label_width, value_width
    floor = min(value_minimum, value_width)
    value = max(floor, min(value_width, available - label_width))
    value = min(value, available)
    return max(0, min(label_width, available - value)), value


HERO_VALUE_SIZES = ((170, 22), (130, 18), (100, 15), (76, 12))
HERO_VALUE_SIZE_FLOOR = 10


def hero_value_size(width):
    """Return the value font size a hero card of this pixel width uses."""
    for minimum, size in HERO_VALUE_SIZES:
        if width >= minimum:
            return size
    return HERO_VALUE_SIZE_FLOOR
