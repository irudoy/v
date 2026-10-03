"""Preserve a generated function name across a reviewed legacy L0 entry repair.

The corrected legacy owners and the verified L0 are accepted before this
operation. It moves one existing generated-name reservation and does not
adopt a symbol into an entity document, edit a legacy owner, or draw a name.
A fresh model is compiled under the primary writer lock before graph sync,
so sync cannot assign the destination a different generated name first.
"""
from __future__ import annotations

from dataclasses import dataclass
import difflib
from pathlib import Path

from kb import compile, graph, l0, lock, names, refs, repo, sites, store, write
from kb.model import SymbolKey
from kb.repo import KbError


@dataclass
class Change:
    root: object
    before: str
    after: str
    lines: list[str]

    def diff(self, texts=None):
        path = names.PATH.as_posix()
        return "".join(difflib.unified_diff(
            self.before.splitlines(keepends=True), self.after.splitlines(keepends=True),
            f"a/{path}", f"b/{path}"))


def reviewed_join(layout, old, new, root):
    """The exact registered seed/fragment join and its accepted L0 ownership."""
    from kb import ghidra_preparation as preparation

    plan = preparation.plan(layout.id, root)
    seed = next((item for item in plan.seeds if item.entry == new), None) if plan else None
    if seed is None or old not in {item.entry for item in seed.fragments}:
        raise KbError("the address repair has no registered seed/fragment preparation", code=3)
    if (new, old) not in plan.joins:
        raise KbError("the address repair has no matching reviewed merge", code=3)
    failures = l0.check_layout(layout, root)
    if failures:
        raise KbError("the accepted L0 does not pass its preparation and manifest checks", code=3)
    body = sites.bodies(layout.id, root)
    owned = sites.owners(layout.id, root)
    if old in body or new not in body or owned.get(old) != {new}:
        raise KbError("the old entry is not an instruction of the repaired L0 function", code=3)
    if any(owned.get(at) != {new} for at in seed.sites):
        raise KbError("a cited preparation site has a different L0 owner", code=3)


def plan_move(symbol, to, base, root=repo.ROOT):
    """Plan one reservation transfer over already corrected legacy owners."""
    source, destination = refs.FULL.fullmatch(symbol.strip()), refs.LOCATION.fullmatch(to.strip())
    if source is None or destination is None or source.group("kind") != "fn":
        raise KbError("a legacy reservation move requires a full generated fn reference "
                      "and a destination location", code=2)
    layout_id = source.group("layout")
    if destination.group("layout") != layout_id:
        raise KbError("a legacy reservation moves within its layout", code=2)
    layout = repo.layout(layout_id, root)
    old, new = int(source.group("address"), 16), int(destination.group("address"), 16)
    if old == new:
        raise KbError("the reservation already has that address", code=2)
    key, target = (layout_id, "fn", old), (layout_id, "fn", new)
    held = [row for row in base.names if row.key == key]
    if len(held) != 1 or held[0].name != source.group("name"):
        raise KbError("the full reference does not name one existing generated reservation", code=3)
    row = held[0]
    if any(item.key == target for item in base.names):
        raise KbError("the destination already has a generated reservation", code=3)
    old_key, new_key = SymbolKey(*key), SymbolKey(*target)
    if old_key in base.symbols:
        raise KbError("a legacy owner still states the old function entry", code=3)
    current = base.symbols.get(new_key)
    if current is None or current.implicit or current.meaning is None or current.meaning.semantic:
        raise KbError("the destination is not an unnamed function of corrected legacy owners", code=3)
    if new_key in base.file_names or any(
            store.TREE == Path(src) or store.TREE in Path(src).parents
            for src in current.sources | current.meaning.sources):
        raise KbError("an entity document owns the destination", code=3)
    reviewed_join(layout, old, new, root)
    moved = names.Row(layout_id, "fn", new, row.name, row.former)
    rows = [moved if item is row else item for item in base.names]
    text = names.render(rows)
    result = compile.build(root, {**base.overlay, names.PATH: text})
    actual = result.symbols.get(new_key)
    if actual is None or actual.meaning is None or actual.meaning.key != f"{row.name}/fn" \
            or actual.generated != row.name or actual.former != row.former \
            or old_key in result.symbols or actual.props != current.props \
            or actual.evidence != current.evidence or actual.sources != current.sources:
        raise KbError("the compiled result does not preserve the generated identity and "
                      "legacy symbol facts", code=3)
    if actual.meaning.props != current.meaning.props or actual.meaning.tables != current.meaning.tables:
        raise KbError("the reservation move changes a legacy meaning fact", code=3)
    failures = write.refusals(base, result)
    if failures:
        details = "\n".join(f"  {item.check}: {item.subject}: {item.message}" for item in failures)
        raise KbError("the reservation move adds model issues; nothing is written\n" + details, code=3)
    before = names.render(base.names)
    change = Change(root, before, text, [f"move legacy reservation {symbol} to {layout_id}:{new:08x}"])
    return change, {names.PATH: text}, result


def apply(symbol, to, root=repo.ROOT, *, dry_run=False, log=print):
    """Use the primary lock and writer without a pre-migration name enrollment."""
    with lock.held(root):
        base = compile.build(root)
        change, texts, result = plan_move(symbol, to, base, root)
        if not dry_run:
            store.write(root, texts)
            compile.cached.cache_clear()
            graph.sync_held(root, False, log, result)
    return change, texts
