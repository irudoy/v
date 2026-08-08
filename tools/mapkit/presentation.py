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
