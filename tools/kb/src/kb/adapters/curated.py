"""Curated function names of `tools/ghidra/symbols/<layout>.csv`.

Each row names the `fn` meaning of a function entry of the layout; the name is
the semantic name of the meaning with the `curated` tier, and the note is its
title when it fits one line and a note otherwise.
"""

import csv
from pathlib import Path

DIRECTORY = Path("tools/ghidra/symbols")
TITLE = 72


def inputs(root):
    return [path.relative_to(root).as_posix()
            for path in sorted((root / DIRECTORY).glob("*.csv")) if path.stem != "7mfk"]


def rows(root, layout):
    path = root / DIRECTORY / f"{layout}.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as source:
        return list(csv.DictReader(line for line in source if not line.startswith("#")))


def declare(b, root):
    for layout in b.layouts:
        if layout == "7mfk":
            continue
        declare_layout(b, root, layout)


def declare_layout(b, root, layout):
    """Names of one layout, including the stage 5 ledger conversion."""
    src = (DIRECTORY / f"{layout}.csv").as_posix()
    for row in rows(root, layout):
        key = b.symbol(layout, "fn", int(row["addr"], 16), src)
        b.name(key, row["name"], "curated", src)
        note = row.get("note", "").strip()
        if note:
            b.props(key, {"title" if len(note) <= TITLE else "note": note}, src)


def relate(b, root):
    pass
