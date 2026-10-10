"""References of the read commands (tools/kb/SPEC.md, section 5.2).

`resolve` accepts, in order of precedence, a full reference, `<layout>:<address>`,
`<name>/<kind>/<layout>` or `<name>/<layout>`, `<name>/<kind>` or `<name>`, a
former name or reference, and a bare address. An input that names several
entities raises exit code 4 with the candidates; one that names none raises
exit code 5.
"""

from dataclasses import dataclass
import re

from kb import repo
from kb.repo import KbError

KINDS = ("fn", "ram", "reg", "tbl", "axis", "const", "hook", "did", "dtc", "stage", "block",
         "endpoint", "chain", "signal", "field", "feature")
FULL = re.compile(r"(?P<name>[a-z][a-z0-9_-]*)/(?P<kind>[a-z]+)/(?P<layout>[0-9a-z]+)-"
                  r"(?P<address>[0-9a-f]{8})")
LOCATION = re.compile(r"(?P<layout>[0-9a-z]+):(?:0x)?(?P<address>[0-9a-fA-F]{1,8})")
ADDRESS = re.compile(r"(?:0x)?(?P<address>[0-9a-fA-F]{1,8})")
NAMED = re.compile(r"(?P<name>[a-z][a-z0-9_-]*)(?:/(?P<second>[0-9a-z]+))?"
                   r"(?:/(?P<third>[0-9a-z]+))?")

SYMBOL_RETURN = "OPTIONAL MATCH (m:Kb:Meaning)-[:HAS]->(s) RETURN s, m ORDER BY s.layout, s.kind"


@dataclass
class Ref:
    """A resolved reference: a symbol with its meaning, a meaning, a designed
    entity, or a location of a layout that holds no symbol."""

    kind: str
    node: dict | None = None
    meaning: dict | None = None
    layout: str | None = None
    address: int | None = None
    note: str | None = None

    @property
    def text(self):
        if self.kind == "symbol":
            return symbol_ref(self.node)
        if self.kind in ("meaning", "entity"):
            return self.node["key"]
        return location_ref(self.layout, self.address)


def symbol_ref(node):
    return f"{node['name']}/{node['kind']}/{node['layout']}-{node['address']:08x}"


def location_ref(layout, address):
    return f"{layout}:{address:08x}"


def _symbols(graph, where, match="MATCH (s:Kb:Symbol)", **params):
    return [(dict(row["s"]), dict(row["m"]) if row["m"] is not None else None)
            for row in graph.run(f"{match} WHERE {where} {SYMBOL_RETURN}", **params)]


def _meanings(graph, where, **params):
    return [dict(row["m"]) for row in
            graph.run(f"MATCH (m:Kb:Meaning) WHERE {where} RETURN m ORDER BY m.kind", **params)]


def _entities(graph, where, **params):
    return [dict(row["e"]) for row in
            graph.run(f"MATCH (e:Kb:Entity) WHERE {where} RETURN e ORDER BY e.kind", **params)]


def _symbol(found, note=None):
    node, meaning = found
    return Ref("symbol", node, meaning, node["layout"], node["address"], note)


def _ambiguous(text, candidates):
    lines = [f"{text!r} names {len(candidates)} entities; use one of:"]
    lines.extend(f"  {ref.text}" for ref in candidates)
    return KbError("\n".join(lines), code=4)


def _known_layout(layout_id, root):
    repo.layout(layout_id, root)
    return layout_id


def _narrow(graph, ref, layout):
    """The symbol of a meaning on a layout, or the meaning with a note."""
    if layout is None or ref.kind != "meaning":
        return ref
    found = _symbols(graph, "s.layout = $layout",
                     match="MATCH (:Kb:Meaning {key: $key})-[:HAS]->(s:Kb:Symbol)",
                     layout=layout, key=ref.node["key"])
    if found:
        return _symbol(found[0], ref.note)
    ref.layout = layout
    ref.note = "; ".join(filter(None, (ref.note, f"no symbol on {layout}")))
    return ref


def _single(text, refs):
    if len(refs) > 1:
        raise _ambiguous(text, refs)
    return refs[0]


def resolve(graph, text, layout=None, root=repo.ROOT, many=False):
    """The Ref of `text`, narrowed to `layout` when given. With `many`, a
    location or a bare address returns every symbol at it as a list."""
    text = text.strip()
    if layout is not None:
        _known_layout(layout, root)

    match = FULL.fullmatch(text)
    if match:
        address = int(match.group("address"), 16)
        key = f"{match.group('layout')}-{address:08x}/{match.group('kind')}"
        found = _symbols(graph, "s.key = $key", key=key)
        if found:
            ref = _symbol(found[0])
            if ref.text != text:
                ref.note = f"stale reference {text}; current {ref.text}"
            return ref
        found = _symbols(graph, "s.layout = $layout AND s.kind = $kind AND "
                         "(s.name = $name OR $name IN s.former)",
                         layout=match.group("layout"), kind=match.group("kind"),
                         name=match.group("name"))
        if found:
            ref = _symbol(found[0])
            ref.note = f"stale reference {text}; current {ref.text}"
            return ref
        _retired(graph, text)
        raise KbError(f"no symbol {text}", code=5)

    match = LOCATION.fullmatch(text)
    if match:
        location_layout = _known_layout(match.group("layout"), root)
        if layout is not None and layout != location_layout:
            raise KbError(f"{text!r} and --layout {layout} disagree", code=2)
        address = int(match.group("address"), 16)
        refs = [_symbol(found) for found in
                _symbols(graph, "s.layout = $layout AND s.address = $address",
                         layout=location_layout, address=address)]
        if not refs:
            refs = [Ref("location", layout=location_layout, address=address)]
        return refs if many else _single(text, refs)

    match = NAMED.fullmatch(text)
    if match:
        name, second, third = match.group("name", "second", "third")
        kind = second if second in KINDS else None
        on = third if kind else second
        if second and not kind and third:
            raise KbError(f"{text!r}: {second!r} is no kind; kinds: {', '.join(KINDS)}", code=2)
        if on is not None:
            _known_layout(on, root)
            if layout is not None and layout != on:
                raise KbError(f"{text!r} and --layout {layout} disagree", code=2)
            layout = on
        refs = _named(graph, name, kind)
        if refs:
            refs = [_narrow(graph, ref, layout) for ref in refs]
            return _single(text, refs)
        refs = _former(graph, name, kind)
        if refs:
            refs = [_narrow(graph, ref, layout) for ref in refs]
            return _single(text, refs)

    match = ADDRESS.fullmatch(text)
    if match:
        address = int(match.group("address"), 16)
        where = "s.address = $address" + (" AND s.layout = $layout" if layout else "")
        refs = [_symbol(found) for found in _symbols(graph, where, address=address, layout=layout)]
        if not refs and layout is not None:
            refs = [Ref("location", layout=layout, address=address)]
        if refs:
            return refs if many else _single(text, refs)
    _retired(graph, text)
    raise KbError(f"no entity {text!r}", code=5)


def _retired(graph, text):
    rows = graph.run('MATCH (n:Kb:Retired) WHERE n.key = $text OR $text IN n.references '
                     'OR $text IN n.names RETURN n.key AS key', text=text)
    if rows:
        raise KbError(f'{rows[0]["key"]} is retired; its names remain reserved', code=5)


def _named(graph, name, kind):
    kind_clause = " AND m.kind = $kind" if kind else ""
    refs = [Ref("meaning", node) for node in
            _meanings(graph, "m.name = $name" + kind_clause, name=name, kind=kind)]
    refs += [Ref("entity", node) for node in
             _entities(graph, "e.key = $key" if kind else "e.key STARTS WITH $prefix",
                       key=f"{name}/{kind}", prefix=f"{name}/")]
    meanings = {ref.node["key"] for ref in refs}
    symbol_clause = " AND s.kind = $kind" if kind else ""
    for found in _symbols(graph, "s.generated = $name" + symbol_clause, name=name, kind=kind):
        if found[1] is None or found[1]["key"] not in meanings:
            refs.append(_symbol(found))
    return refs


def _former(graph, name, kind):
    kind_clause = " AND m.kind = $kind" if kind else ""
    refs = [Ref("meaning", node, note=f"former name {name}; current {node['key']}") for node in
            _meanings(graph, "$name IN m.former" + kind_clause, name=name, kind=kind)]
    symbol_clause = " AND s.kind = $kind" if kind else ""
    for found in _symbols(graph, "$name IN s.former" + symbol_clause, name=name, kind=kind):
        ref = _symbol(found)
        ref.note = f"former name {name}; current {ref.text}"
        refs.append(ref)
    return refs
