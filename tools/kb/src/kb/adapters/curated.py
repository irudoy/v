"""Curated function names of `tools/ghidra/symbols/<layout>.csv`.

Each row names the `fn` meaning of a function entry of the layout; the name is
the semantic name of the meaning with the `curated` tier, and the note is its
title when it fits one line and a note otherwise.
"""

import csv
import io
from pathlib import Path

from kb import repo
from kb.repo import KbError

DIRECTORY = Path("tools/ghidra/symbols")
TITLE = 72
HEADERS = {
    "1nd": (
        "# Curated function names of layout 1nd, whose L0 image is 1ND0A.\n"
        "# RenameFuncs.java applies them to a Ghidra program of the layout; the Memgraph\n"
        "# loaders and the ROM atlas read them with tools/rom_sources.py.\n"
        "# Format: addr,name,note (addr is eight hexadecimal digits; note becomes the\n"
        "# function plate comment and holds no comma).\n"),
}


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


def render(model):
    """Exact remaining curated CSV views selected by owned function entries."""
    selected = {layout: {} for layout in HEADERS}
    for symbol in model.symbols.values():
        marker = symbol.props.get("curated")
        if marker is None:
            continue
        layout, order = symbol.layout, marker.get("order")
        if (layout not in HEADERS or symbol.kind != "fn" or type(order) is not int
                or order < 0 or order in selected[layout]):
            raise KbError(f"{symbol.key.key}: invalid or duplicate curated selector", code=3)
        meaning = symbol.meaning
        name = marker.get("name", meaning.name)
        aliases = {meaning.name, *(alias for alias, _, _ in meaning.other_names)}
        if name not in aliases:
            raise KbError(f"{symbol.key.key}: curated name is not an owned alias", code=3)
        notes = meaning.props.get("note", ())
        notes = [notes] if isinstance(notes, str) else notes
        indices = marker.get("notes", [])
        if (not isinstance(indices, list) or any(type(index) is not int or index < 0
                                                or index >= len(notes) for index in indices)
                or len(indices) > 1 or (marker.get("title") and indices)
                or ("title" in marker and type(marker["title"]) is not bool)
                or (marker.get("title") and not meaning.props.get("title"))):
            raise KbError(f"{symbol.key.key}: invalid curated note selector", code=3)
        note = meaning.props.get("title", "") if marker.get("title") else (
            notes[indices[0]] if indices else "")
        selected[layout][order] = dict(addr=f"{symbol.address:08x}", name=name, note=note)
    output = {}
    for layout, entries in selected.items():
        if sorted(entries) != list(range(len(entries))):
            raise KbError(f"{layout}: curated row order is incomplete", code=3)
        text = io.StringIO(newline="")
        text.write(HEADERS[layout])
        writer = csv.DictWriter(text, ["addr", "name", "note"], lineterminator="\n")
        writer.writeheader()
        writer.writerows(entries[index] for index in sorted(entries))
        output[(DIRECTORY / f"{layout}.csv").as_posix()] = text.getvalue()
    return output


def registry(root=repo.ROOT):
    """The 1nd curated view of the primary compiler model."""
    from kb import compile
    return render(compile.cached(root))[(DIRECTORY / "1nd.csv").as_posix()]
