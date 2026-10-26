"""Passive references to repository evidence retained under a Git tag.

The form is ``git:<tag>:<repository-path>[#fragment]``. Parsing verifies
syntax only; it neither resolves a tag nor reads or executes archived files.
"""

from dataclasses import dataclass
from pathlib import PurePosixPath
import re


STOCK_ARCHIVE = "archive/stock-proofs-2026-10-26"


@dataclass(frozen=True)
class ArchiveRef:
    tag: str
    path: str
    fragment: str | None = None

    def __str__(self):
        suffix = "" if self.fragment is None else f"#{self.fragment}"
        return f"git:{self.tag}:{self.path}{suffix}"


def parse(value):
    """Return an archive reference, or None for an ordinary reference.

    A malformed ``git:`` reference raises ValueError rather than falling
    through to a current filesystem path.
    """
    if not isinstance(value, str) or not value.startswith("git:"):
        return None
    parts = value.split(":", 2)
    if len(parts) != 3:
        raise ValueError("archive evidence requires git:<tag>:<repository-path>")
    _, tag, body = parts
    if (not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._/-]*", tag)
            or ".." in tag or any(not part or part.startswith(".")
                                  or part.endswith((".", ".lock")) for part in tag.split("/"))):
        raise ValueError("archive evidence has an invalid Git tag name")
    path, separator, fragment = body.partition("#")
    parsed = PurePosixPath(path)
    if (not path or path == "." or parsed.is_absolute() or ".." in parsed.parts
            or str(parsed) != path or "\\" in path or ":" in path
            or any(ord(char) < 32 or ord(char) == 127 for char in path)):
        raise ValueError("archive evidence requires a canonical repository-relative path")
    if separator and (not fragment or "#" in fragment
                      or any(char.isspace() or ord(char) < 32 for char in fragment)):
        raise ValueError("archive evidence has an invalid fragment")
    return ArchiveRef(tag, path, fragment if separator else None)


def _exact(before, after):
    if type(before) is not type(after):
        return False
    if isinstance(before, dict):
        return before.keys() == after.keys() and all(_exact(value, after[key])
                                                     for key, value in before.items())
    if isinstance(before, (list, tuple)):
        return len(before) == len(after) and all(_exact(old, new)
                                                for old, new in zip(before, after))
    return before == after


def archive_equivalent(before, after):
    """Whether only evidence refs acquire the stock archive prefix.

    Every other value, evidence position and locator fragment stays exact.
    This comparison neither resolves references nor reads archived sources.
    """
    if not isinstance(before, dict) or not isinstance(after, dict):
        return False
    old, new = before.get("evidence"), after.get("evidence")
    if not isinstance(old, list) or not isinstance(new, list) or len(old) != len(new):
        return False
    normalized = []
    for previous, current in zip(old, new):
        if not isinstance(previous, dict) or not isinstance(current, dict):
            return False
        current = dict(current)
        for key in ("path", "key"):
            if previous.get(key) != current.get(key):
                ref = previous.get(key)
                if (not isinstance(ref, str) or ref.startswith("git:")
                        or current.get(key) != f"git:{STOCK_ARCHIVE}:{ref}"):
                    return False
                try:
                    parse(current[key])
                except ValueError:
                    return False
                current[key] = ref
        normalized.append(current)
    return _exact(before, {**after, "evidence": normalized})
