"""Shared presentation policy for generated ECU definitions."""

import re


CATEGORY_CONFIDENCE_SUFFIX = re.compile(
    r"(?: \((?:traced|candidate)\))+$"
)


def category_name(category):
    """Return a functional category without confidence annotations."""
    return CATEGORY_CONFIDENCE_SUFFIX.sub("", str(category))
