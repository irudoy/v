"""Conversions of legacy registries into entity files (tools/kb/SPEC.md,
sections 20 and 21.1).

`uv run python -m kb.convert <registry> [--dry-run]` converts a registry
whose adapter `adapters.CONVERTED` lists. It compiles the model with the
adapters of the compiler and the registry's adapter in the order of
`adapters.ORDER`, writes the facts that the registry's adapter states into
the files of their meanings through `write.Change`, and compiles the model
from those files with the adapters of the compiler. It refuses the
conversion with exit code 3 when the two models differ beyond the rules of
the registry, when the files add an issue of a model check or a registry
disagreement, or when a projection of the registry differs from its file;
otherwise it writes the files and `kb/names.csv` under the lock and loads
the result into the graph. On a converted tree it writes nothing. The files
adapter runs first, so the notes that a file states precede those of the
registries in the note of a symbol.

The interpolation registries (section 20.3):

- The meaning of every symbol that the registries state takes `[interp]`
  and each of its symbols an entry with the override of its layout and the
  typed evidence of the registries, whose `to` becomes a location.
- A wrapper symbol that no other registry states takes `l0` identity
  evidence at the first instruction of its body that calls its kernel entry,
  or at its entry when it is its own kernel.
- An `unsupported` correspondence becomes an `unresolved` status with the L0
  digest of its layout and without the registry evidence.

The native registries (section 20.4):

- A meaning takes `home` where the registries state it, and each key that
  they state for its symbols where one of them has the value of the meaning.
- Each symbol that they declare takes an entry with its overrides of those
  keys, its `images`, its notes, and its evidence; a symbol that they only
  name, as an axis link names its axis, must be one that another registry
  declares.
- Each link takes an entry with its slot, its role, and the evidence of every
  symbol that states it, and each `absent` status an entry with its note and
  evidence; a status that cites the registry as its evidence is refused.

The definition registries (section 20.3):

- Each target symbol of a row takes its row item first in its entry, with the
  prose of the row as its note: the item toward the `7mfk` symbol that
  `kb.match.typed` gives, whose kind must be the kind of the row; for an `l0`
  row, `l0` homology evidence toward the `7mfk` symbol; for a
  `reviewed-target` row, `l0` identity evidence; and for a `stock-inert-path`
  row, `l0` homology evidence toward the `7mfk` symbol. An `l0` item lies at
  the first census operand of the storage of its symbol, or else at the first
  instruction that touches the storage, where it verifies.
- A `7mfk` symbol that only the registries and the entity files state takes an
  entry, and `l0` identity evidence of the same placement when its entry
  states no evidence.
- An `absent` status is one that the file of its meaning states with its
  evidence; an `unresolved` status takes the search of the `7mfk` symbol on
  its layout with the L0 digest of the layout and the prose of the row as its
  note. The registry evidence of a status is dropped.
- `feature/definitions.toml` takes a `[[target]]` for each layout that a
  projection targets, with its images, the meanings that its rows require,
  its variants, and its omitted surfaces.
"""

import argparse
from collections import defaultdict
import sys

from kb import adapters, compile, graph, lock, match, repo, store, write
from kb.adapters import definitions, interp, native
from kb.model import Ref, SymbolKey
from kb.repo import KbError

# Differences that a refusal lists.
SHOWN = 20
# The keys of an unresolved status that a conversion states.
UNRESOLVED = ("method", "target", "count", "l0", "note")


def _location(item):
    """An evidence item as the files state it: a symbol `to` as its location,
    without the registry path and the legacy token."""
    return {key: value.location if isinstance(value, SymbolKey) else value
            for key, value in item.items() if key not in ("path", "legacy")}


def _table(model, table):
    """A table of `[interp]` with its kernel as the reference of its meaning."""
    found = dict(table)
    held = model.symbols.get(found.get("kernel"))
    if held is None or held.meaning is None:
        raise KbError(f"the kernel {found.get('kernel')} of an [interp] has no meaning", code=3)
    found["kernel"] = held.meaning.key
    return found


def _alone(symbol, inputs):
    """Whether only the registry and the entity files state a symbol."""
    return all(src in inputs or src.startswith(f"{store.TREE.as_posix()}/")
               for src in symbol.sources)


def _kernel_call(model, symbol):
    """The `l0` identity item of a wrapper: the first call of its kernel
    entry, or its entry when it is its own kernel."""
    found = match.interp_entry(model, symbol)
    if found is None:
        raise KbError(f"{symbol.key.key}: the [interp] names no kernel on {symbol.layout}",
                      code=3)
    kernel, entry = found
    if kernel is symbol:
        site = symbol.address
    else:
        calls = match.kernel_calls(model, symbol, entry)
        if not calls:
            raise KbError(f"{symbol.key.key}: L0 holds no call of the kernel entry {entry:08x}",
                          code=3)
        site = calls[0]
    return {"kind": "l0", "supports": "identity", "at": f"{symbol.layout}:{site:08x}"}


class Conversion:
    """The facts of one registry and the files that state them."""

    def __init__(self, adapter, before, root=repo.ROOT):
        self.adapter, self.before, self.root = adapter, before, root
        self.inputs = set(adapter.inputs(root))
        self.facts = compile.builder_of(root, before.overlay)
        adapter.declare(self.facts, root)
        adapter.relate(self.facts, root)
        # Legacy evidence without the keys of its kind is what a conversion
        # types.
        issues = [issue for issue in self.facts.issues if issue.check != "untyped"]
        if issues:
            lines = [f"the registry has {len(issues)} issues; nothing is written"]
            lines += [f"  {issue.check}: {issue.path}: {issue.subject}: {issue.message}"
                      for issue in issues[:SHOWN]]
            raise KbError("\n".join(lines), code=3)
        self.change = write.Change(before, None, root)
        # {symbol key: (converted items, raw items)}, {(meaning id, layout):
        # (converted status, raw evidence)}, the keys that a converted status
        # adds, and {symbol key: notes of its entry}.
        self.evidence, self.statuses, self.added, self.notes = {}, {}, (), {}

    def run(self):
        getattr(self, self.adapter.__name__.rsplit(".", 1)[1])()
        return self.change.texts()

    def interp(self):
        before, change = self.before, self.change
        self.added = ("l0",)
        grouped = {}
        for key in sorted(self.facts.symbols):
            symbol = before.symbols.get(key)
            if symbol is None or symbol.meaning is None:
                raise KbError(f"{key.key} has no meaning in the model", code=3)
            grouped.setdefault(id(symbol.meaning), (symbol.meaning, []))[1].append(symbol)
        statuses = {}
        for anchor, layout, state, props, evidence, _, _ in self.facts.status_facts:
            meaning = before.meaning_of(anchor)
            if meaning is None:
                raise KbError(f"the status of {anchor.key} on {layout} has no meaning", code=3)
            grouped.setdefault(id(meaning), (meaning, []))
            statuses.setdefault(id(meaning), []).append((layout, state, props, evidence))
        for key, (meaning, symbols) in grouped.items():
            _, document = change.document(meaning)
            if "interp" in meaning.props:
                document["interp"] = _table(before, meaning.props["interp"])
            entries = {(entry["layout"], entry["address"]): entry
                       for entry in document.get("symbol", ())}
            for symbol in symbols:
                entry = entries.get((symbol.layout, f"{symbol.address:08x}"))
                if entry is None:
                    entry = change.adopt(meaning, symbol)
                    document["symbol"] = [*document.get("symbol", ()), entry]
                raw = self.facts.symbols[symbol.key].evidence
                items = [_location(item) for item in raw]
                if isinstance(symbol.value("interp"), dict) and _alone(symbol, self.inputs):
                    items.append(_kernel_call(before, symbol))
                self.evidence[symbol.key] = (items, raw)
                stated = list(entry.get("evidence", ()))
                stated += [item for item in items if item not in stated]
                if stated:
                    entry["evidence"] = stated
                if "interp" in symbol.props:
                    entry["interp"] = _table(before, symbol.props["interp"])
            for layout, state, props, evidence in statuses.get(key, ()):
                kept = [entry for entry in document.get("status", ())
                        if entry.get("layout") != layout]
                held = next((entry for entry in document.get("status", ())
                             if entry.get("layout") == layout
                             and entry.get("method") == props.get("method")), {})
                status = {"layout": layout, "state": state, **props,
                          "l0": held.get("l0") or match.l0_digest(layout, self.root)}
                document["status"] = kept + [status]
                self.statuses[(key, layout)] = (status, evidence)

    def native(self):
        before, facts = self.before, self.facts
        stated = defaultdict(dict)
        for key, props, _ in facts.symbol_keys:
            stated[key].update(props)
        homes = [anchor for anchor, props, _ in facts.meaning_props if "home" in props]
        for key, symbol in sorted(facts.symbols.items()):
            held = before.symbols.get(key)
            if held is None or held.meaning is None or symbol.implicit and held.implicit:
                raise KbError(f"{key.key}: no other registry declares the symbol that the "
                              "registries only name", code=3)
        for _, _, _, _, evidence, _, _ in facts.status_facts:
            if any(item.get("kind") == "registry" for item in evidence):
                raise KbError("a status cites the registry as its evidence", code=3)
        documents = {}

        def document(meaning):
            if id(meaning) not in documents:
                _, found = self.change.document(meaning)
                documents[id(meaning)] = found
            return documents[id(meaning)]

        for anchor in homes:
            meaning = before.by_node[anchor]
            document(meaning)["home"] = meaning.props["home"]
        by_meaning = defaultdict(list)
        for key, symbol in sorted(facts.symbols.items()):
            if not symbol.implicit:
                by_meaning[id(before.symbols[key].meaning)].append(key)
        for keys in by_meaning.values():
            meaning = before.symbols[keys[0]].meaning
            found = document(meaning)
            for name in sorted({name for key in keys for name in stated[key]}):
                values = [stated[key][name] for key in keys if name in stated[key]]
                if meaning.props.get(name) in values:
                    found[name] = meaning.props[name]
            for key in keys:
                self._native_symbol(meaning, found, key, stated[key])
        for fact in facts.link_facts:
            owner = before.symbols[fact.owner].meaning
            self._native_link(document(owner), fact)
        for anchor, layout, state, props, evidence, _, _ in facts.status_facts:
            meaning = before.by_node[anchor]
            found = document(meaning)
            status = {"layout": layout, "state": state, **props,
                      "evidence": [_location(item) for item in evidence]}
            found["status"] = [entry for entry in found.get("status", ())
                               if entry.get("layout") != layout] + [status]
            self.statuses[(id(meaning), layout)] = (status, evidence)

    def _native_symbol(self, meaning, document, key, stated):
        """The entry of a symbol that the native registries state: its
        overrides of their keys, their notes, its images, and their evidence."""
        symbol, fact = self.before.symbols[key], self.facts.symbols[key]
        entries = {(entry["layout"], entry["address"]): entry
                   for entry in document.get("symbol", ())}
        entry = entries.get((key.layout, f"{key.address:08x}"))
        if entry is None:
            entry = self.change.adopt(meaning, symbol)
            document["symbol"] = [*document.get("symbol", ()), entry]
        for name in stated:
            if name in symbol.props:
                entry[name] = symbol.props[name]
        if fact.props.get("images"):
            entry["images"] = fact.props["images"]
        notes = entry.get("note", [])
        notes = [notes] if isinstance(notes, str) else list(notes)
        notes += [note for note in fact.props.get("note", ()) if note not in notes]
        if notes:
            entry["note"] = notes[0] if len(notes) == 1 else notes
            self.notes[key] = notes
        items = [_location(item) for item in fact.evidence]
        self.evidence[key] = (items, fact.evidence)
        found = list(entry.get("evidence", ()))
        found += [item for item in items if item not in found]
        if found:
            entry["evidence"] = found

    def _native_link(self, document, fact):
        """The link entry of a link that the native registries state, with the
        evidence of every symbol that states it."""
        to = self.before.symbols[fact.to].meaning
        slot, role = fact.props.get("slot"), fact.props.get("role")
        entry = next((link for link in document.get("link", ())
                      if (link.get("type"), link.get("to"), link.get("slot"), link.get("role"))
                      == (fact.type, to.key, slot, role)), None)
        if entry is None:
            entry = {"type": fact.type, "to": to.key, "slot": slot, "role": role}
            entry = {name: value for name, value in entry.items() if value is not None}
            document["link"] = [*document.get("link", ()), entry]
        found = list(entry.get("evidence", ()))
        found += [_location(item) for item in fact.evidence if _location(item) not in found]
        entry["evidence"] = found

    def definitions(self):
        before, facts = self.before, self.facts
        self.added = UNRESOLVED
        documents = {}

        def document(meaning):
            if id(meaning) not in documents:
                _, found = self.change.document(meaning)
                documents[id(meaning)] = found
            return documents[id(meaning)]

        ranks = match.grounded(before, sorted(
            key for key in facts.symbols if key.layout == definitions.CANONICAL))
        for key, fact in sorted(facts.symbols.items()):
            symbol = before.symbols.get(key)
            if symbol is None or symbol.meaning is None:
                raise KbError(f"{key.key} has no meaning in the model", code=3)
            if key.layout == definitions.CANONICAL:
                grounded = ranks[key][0] >= match.CANDIDATE
                if grounded and not _alone(symbol, self.inputs):
                    continue
                entry = self._entry(document(symbol.meaning), symbol)
                if grounded:
                    continue
                items = [self._placed(symbol, {"kind": "l0", "supports": "identity"})]
            else:
                items = [self._row_item(symbol, fact.evidence)]
                entry = self._entry(document(symbol.meaning), symbol)
            entry["evidence"] = items + [item for item in entry.get("evidence", ())
                                         if item not in items]
            self.evidence[key] = (items, fact.evidence)
        for anchor, layout, state, props, evidence, _, _ in facts.status_facts:
            meaning = before.meaning_of(anchor)
            if meaning is None:
                raise KbError(f"the status of {anchor.key} on {layout} has no meaning", code=3)
            found = document(meaning)
            held = next((entry for entry in found.get("status", ())
                         if entry.get("layout") == layout), None)
            if held is not None:
                if held.get("state") != state:
                    raise KbError(f"{meaning.key} is {state} on {layout} in the registries and "
                                  f"{held.get('state')} in its file", code=3)
                self.statuses[(id(meaning), layout)] = ({"layout": layout, "state": state},
                                                        evidence)
                continue
            if state != "unresolved":
                raise KbError(f"the {state} status of {meaning.key} on {layout} has no entry "
                              "with its evidence in the file of its meaning", code=3)
            origin = meaning.symbols.get(definitions.CANONICAL)
            if origin is None:
                raise KbError(f"{meaning.key} has no {definitions.CANONICAL} symbol to search "
                              "from", code=3)
            search = match.search(before, origin, layout)
            if search.count == 1:
                [address] = search.candidates
                raise KbError(f"the {search.method} search from {search.target} finds one "
                              f"candidate on {layout}, {address:08x}, for the unresolved "
                              f"status of {meaning.key}", code=3)
            status = {"layout": layout, "state": state, "method": search.method,
                      "target": search.target, "count": search.count,
                      "l0": match.l0_digest(layout, self.root), "note": props.get("note")}
            found["status"] = [*found.get("status", ()), status]
            self.statuses[(id(meaning), layout)] = (status, evidence)
        _, feature = self.change.designed("feature", definitions.FEATURE)
        targets = {entry.get("layout"): entry for entry in feature.get("target", ())}
        for (slug, layout), target in sorted(facts.targets.items()):
            if slug == definitions.FEATURE:
                targets[layout] = self._target(layout, target)
        feature["target"] = [targets[layout] for layout in sorted(targets)]

    def _entry(self, document, symbol):
        """The entry of a symbol in the document of its meaning; a document
        without one adopts the symbol."""
        address = f"{symbol.address:08x}"
        entry = next((item for item in document.get("symbol", ())
                      if (item.get("layout"), item.get("address")) == (symbol.layout, address)),
                     None)
        if entry is None:
            entry = self.change.adopt(symbol.meaning, symbol)
            document["symbol"] = [*document.get("symbol", ()), entry]
        return entry

    def _placed(self, symbol, item):
        """`item` at the first census operand of the symbol's storage, or else
        at the first instruction that touches the storage, where it verifies."""
        here = match.code(symbol.layout, self.root)
        span = range(symbol.address, symbol.address + (match.storage_size(symbol) or 1))
        sites = match.touching(self.before, symbol)
        operands = [site for site in sites
                    if any(address in span and relation.startswith("operand:")
                           for address, relation in here.touches(site))]
        for site in operands + [site for site in sites if site not in operands]:
            found = {**item, "at": f"{symbol.layout}:{site:08x}"}
            if match.verify(self.before, symbol, found) is None:
                return found
        raise KbError(f"{symbol.key.key}: no instruction of the L0 of {symbol.layout} that "
                      "touches its storage places its l0 evidence", code=3)

    def _row_item(self, symbol, raw):
        """The row item of a target symbol from the registry item of its row."""
        rows = [item for item in raw if item.get("legacy")]
        if len(rows) != 1:
            raise KbError(f"{symbol.key.key}: the registries state {len(rows)} rows of the "
                          "symbol", code=3)
        [row] = rows
        marker, note = row["legacy"], row.get("note")
        if marker == definitions.REVIEWED:
            return self._placed(symbol, {"kind": "l0", "supports": "identity", "note": note})
        origin = self.before.symbols.get(row.get("to"))
        if origin is None:
            raise KbError(f"{symbol.key.key}: the row names no {definitions.CANONICAL} symbol",
                          code=3)
        kind = "l0" if marker == definitions.INERT else marker.partition(":")[2]
        if marker != definitions.INERT:
            found = match.typed(self.before, symbol, origin)
            if found is not None:
                if found["kind"] != kind:
                    raise KbError(f"{symbol.key.key}: the row states {kind}, and the first typed "
                                  f"item toward {origin.key.location} is {found['kind']}",
                                  code=3)
                return {**_location(found), "note": note}
        if kind != "l0":
            raise KbError(f"{symbol.key.key}: the row states {kind}, and no typed item toward "
                          f"{origin.key.location} verifies", code=3)
        return self._placed(symbol, {"kind": "l0", "supports": "homology",
                                     "to": origin.key.location, "note": note})

    def _target(self, layout, target):
        """The `[[target]]` entry of the definitions of a layout."""
        props = target.props

        def meaning(key):
            held = self.before.meaning_of(key)
            if held is None:
                raise KbError(f"the {definitions.FEATURE} target of {layout} names "
                              f"{key.key}, which has no meaning", code=3)
            return held.key

        return {
            "layout": layout, "status": target.status,
            "requires": sorted({meaning(key) for key in props.get("requires", ())}),
            "images": props.get("images", {}),
            "variants": [{"symbol": meaning(item["symbol"]), "variant": item["variant"]}
                         for item in props.get("variants", ())],
            "omitted": [{"symbol": meaning(item["symbol"]), "reason": item["reason"]}
                        for item in props.get("omitted", ())],
        }

    # Comparison -------------------------------------------------------------

    def expected(self):
        """The dump of the model before the conversion with the rules of the
        conversion applied."""
        before = self.before
        found = dump(before)
        for key, (items, raw) in self.evidence.items():
            name, generated, former, props, evidence, meaning = found["symbols"][key.location,
                                                                                key.kind]
            evidence = (set(evidence) - {_value(before, item) for item in raw}) | {
                _value(before, item) for item in items}
            found["symbols"][key.location, key.kind] = (
                name, generated, former, props, frozenset(evidence), meaning)
        moved = {key: row for key, row in {row.key: row for row in before.names}.items()
                 if key not in self.change.rows}
        for (layout, kind, address), row in moved.items():
            where = (f"{layout}:{address:08x}", kind)
            name, generated, former, props, evidence, meaning = found["symbols"][where]
            if before.symbols[SymbolKey(layout, kind, address)].meaning.semantic:
                generated, former = None, (row.name, *row.former)
            found["symbols"][where] = (name, generated, former, props, evidence, meaning)
        for key, notes in self.notes.items():
            where = (key.location, key.kind)
            name, generated, former, props, evidence, meaning = found["symbols"][where]
            props = dict(props)
            props["note"] = tuple(notes) + tuple(note for note in props.get("note", ())
                                                 if note not in notes)
            found["symbols"][where] = (name, generated, former, tuple(sorted(props.items())),
                                       evidence, meaning)
        by_id = {id(meaning): meaning for meaning in before.meanings}
        for (key, layout), (status, raw) in self.statuses.items():
            meaning = by_id[key]
            entry = found["meanings"][meaning.key]
            listed = dict(entry["statuses"])
            state, props, evidence = listed[layout]
            props = _value(before, {**dict(props), **{name: status[name] for name in self.added
                                                      if name in status}})
            evidence = frozenset((set(evidence) - {_value(before, item) for item in raw})
                                 | {_value(before, item) for item in status.get("evidence", ())})
            listed[layout] = (state, props, evidence)
            entry["statuses"] = tuple(sorted(listed.items()))
        return found


def _value(model, value):
    """A comparable form of a value: symbols as locations, tables as sorted
    pairs, and a kernel of `[interp]` as the key of its meaning."""
    if isinstance(value, SymbolKey):
        return value.location
    if isinstance(value, Ref):
        return repr(value)
    if isinstance(value, dict):
        if "kernel" in value and "access" in value:
            held = model.symbols.get(value["kernel"])
            if held is not None and held.meaning is not None:
                value = {**value, "kernel": held.meaning.key}
        return tuple(sorted((key, _value(model, item)) for key, item in value.items()))
    if isinstance(value, (list, tuple, set, frozenset)):
        items = tuple(_value(model, item) for item in value)
        return tuple(sorted(items, key=repr)) if isinstance(value, (set, frozenset)) else items
    return value


def dump(model):
    """{section: {key: facts}} of a model without the sources of its facts."""
    symbols = {}
    for key, symbol in model.symbols.items():
        symbols[key.location, key.kind] = (
            symbol.name, symbol.generated, tuple(symbol.former), _value(model, symbol.props),
            frozenset(_value(model, item) for item in symbol.evidence),
            symbol.meaning.key if symbol.meaning is not None else None)
    meanings = {}
    for meaning in model.meanings:
        meanings[meaning.key] = {
            "kind": meaning.kind, "semantic": meaning.semantic,
            "symbols": tuple(sorted(symbol.key.location for symbol in meaning.symbols.values())),
            "props": _value(model, meaning.props), "tables": _value(model, meaning.tables),
            "names": tuple(sorted({(name, tier) for name, tier, _ in meaning.other_names})),
            "statuses": tuple(sorted(
                (layout, (status.state, _value(model, status.props),
                          frozenset(_value(model, item) for item in status.evidence)))
                for layout, status in meaning.statuses.items())),
        }
    links = {}
    for link in model.links:
        links[link.owner.key, link.type, link.to.key, link.slot, link.offset] = (
            _value(model, link.props), frozenset(_value(model, item) for item in link.evidence),
            tuple(sorted(link.stated)), tuple(sorted(link.roles)))
    targets = {key: (target.status, _value(model, _target_props(model, target.props)))
               for key, target in model.targets.items()}
    entities = {key: _value(model, entity.props) for key, entity in model.entities.items()}
    return {"symbols": symbols, "meanings": meanings, "links": links, "targets": targets,
            "entities": entities}


def _target_props(model, props):
    """The keys of a target with `requires` as the set of its meanings, which
    a registry states by their symbols and a file by their references."""
    if "requires" not in props:
        return props
    found = set()
    for key in props["requires"]:
        meaning = model.meaning_of(key) if isinstance(key, SymbolKey) else None
        found.add(meaning.key if meaning is not None else key)
    return {**props, "requires": frozenset(found)}


def differences(expected, found):
    """Lines of the facts that differ between two dumps."""
    lines = []
    for section in expected:
        mine, theirs = expected[section], found[section]
        for key in sorted(set(mine) | set(theirs), key=repr):
            if mine.get(key) != theirs.get(key):
                lines.append(f"{section} {key}: expected {mine.get(key)!r}, "
                             f"found {theirs.get(key)!r}")
    return lines


def plan(name, root=repo.ROOT):
    """(conversion, texts, result) of the conversion of a registry; exit code 3
    when the result differs from the model before it, adds an issue, or
    projects the registry differently."""
    adapter = next((item for item in adapters.CONVERTED
                    if item.__name__.rsplit(".", 1)[1] == name), None)
    if adapter is None:
        known = ", ".join(item.__name__.rsplit(".", 1)[1] for item in adapters.CONVERTED)
        raise KbError(f"no conversion {name!r}; the conversions are {known}", code=2)
    before = compile.build(root, order=tuple(
        item for item in adapters.ORDER if item not in adapters.CONVERTED or item is adapter))
    conversion = Conversion(adapter, before, root)
    texts = conversion.run()
    result = compile.build(root, {**before.overlay, **texts})
    lines = differences(conversion.expected(), dump(result))
    if lines:
        raise KbError("\n".join([f"the files differ from the model in {len(lines)} facts; "
                                 "nothing is written"] + lines[:SHOWN]), code=3)
    refused = write.refusals(before, result)
    if refused:
        raise KbError("\n".join(
            [f"the conversion adds {len(refused)} issues; nothing is written"]
            + [f"  {issue.check}: {issue.path}: {issue.subject}: {issue.message}"
               for issue in refused[:SHOWN]]), code=3)
    differ = [path for path, text in projections(adapter, result).items()
              if not (root / path).exists()
              or (root / path).read_text(encoding="utf-8") != text]
    if differ:
        raise KbError(f"the projections of {', '.join(differ)} differ from their files; "
                      "nothing is written", code=3)
    return conversion, texts, result


def projections(adapter, model):
    """{path: text} of the projections of a converted registry."""
    if adapter is interp:
        return {**interp.render_registries(model), **interp.render_correspondences(model)}
    if adapter is native:
        return {native.TABLES.as_posix(): native.render_tables(native.tables_document(model)),
                native.FUEL_CUT.as_posix(): native.render_fuel_cut(
                    native.fuel_cut_document(model))}
    if adapter is definitions:
        return {**definitions.render_addresses(model),
                definitions.PROJECTIONS.as_posix(): definitions.render_projections(model)}
    return {}


def main(argv=None):
    parser = argparse.ArgumentParser(prog="kb.convert", description=__doc__.split("\n\n")[0])
    parser.add_argument("registry", help="the adapter of a converted registry")
    parser.add_argument("--dry-run", action="store_true", help="plan and write nothing")
    args = parser.parse_args(argv)
    try:
        with lock.held(repo.ROOT):
            conversion, texts, result = plan(args.registry)
            if texts and not args.dry_run:
                store.write(repo.ROOT, texts)
                compile.cached.cache_clear()
                graph.sync_held(repo.ROOT, False, print, result)
    except KbError as error:
        print(error, file=sys.stderr)
        return error.code
    for path in texts:
        print(f"{path.as_posix()}: {'planned' if args.dry_run else 'written'}")
    print(f"{args.registry}: {len(conversion.evidence)} symbols, {len(conversion.statuses)} "
          f"statuses, {len(texts)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
