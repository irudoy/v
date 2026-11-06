"""Shared presentation policy for generated ECU definitions."""

import re


CATEGORY_CONFIDENCE_SUFFIX = re.compile(
    r"(?: \((?:traced|candidate)\))+$"
)
CATEGORY_PATH_SEPARATOR = " / "
ROMRAIDER_CATEGORY_SEPARATOR = "//"


def category_name(category):
    """Return a functional category without confidence annotations."""
    return CATEGORY_CONFIDENCE_SUFFIX.sub("", str(category))


def romraider_category_name(category):
    """Render a functional category as a RomRaider hierarchy path."""
    return category_name(category).replace(
        CATEGORY_PATH_SEPARATOR,
        ROMRAIDER_CATEGORY_SEPARATOR,
    )


def row_labelled(calibration, override):
    """Whether a direct row-major map has a graph column axis and declared row labels.

    The ROM array indexes the columns (axis_y, the X axis of both editors),
    and the presentation declares one static_axis_y label per row. A map
    without both declarations, including a two-dimensional map with one
    recovered axis of an interpolated pair, does not take this form.
    """
    return (
        calibration["dims"] == 2
        and calibration["family"] == "direct-row-major"
        and not calibration["axis_x"]
        and len(calibration["axis_y"]) == 1
        and "static_axis_x" not in override
        and len(override.get("static_axis_y", [])) == calibration["height"]
    )
