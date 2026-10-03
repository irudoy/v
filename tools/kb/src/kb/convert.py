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
- An item of an entry states an item of the registries when it equals the
  item or adds only the note of a correspondence row to it.
- An `unsupported` correspondence becomes an `unresolved` status with the L0
  digest of its layout and without the registry evidence.

The native registries (section 20.4):

- A meaning takes `home` where the registries state it, and each key that
  they state for its symbols where one of them has the value of the meaning.
- Each symbol that they declare takes an entry with its overrides of those
  keys, its `images`, its notes, and its evidence; a symbol that they only
  name, as an axis link names its axis, must be one that another registry
  declares. An item of an entry states an evidence item of the registries
  when it equals the item or adds only the note of a correspondence row to
  it.
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

The address profiles and the correspondence files (section 20.3):

- A symbol that a correspondence row states takes its row item first in its
  entry, with the text of the row as its note: an item of its entry that
  states the row, or else, for a `mapped` row, the homology item toward the
  `7mfk` symbol of its meaning and, for a `target-specific` row, the identity
  item of its own layout. The homology item is the item that
  `kb.match.typed` gives, a `manual` item for a symbol at the address of its
  origin that the hardware manual of the MCU or its vector table places, or
  an `l0` item. The identity item is the test of a row whose symbol no
  instruction reaches, the entry of a function, the `did-table` item of a
  DID slot, an `l0` item, or the `indirect` base item of a hook with the
  `rom-bytes` item of its stock word. An `l0` item of a function lies at its
  entry, and another at the first census operand of the storage of its
  symbol, the first instruction that touches the storage, the first load of
  a word of the storage from a literal pool, or else the first place whose
  L0 references name the storage, where it verifies.
- A symbol that only the registries and the entity files state, and that no
  row states, takes the homology item toward the `7mfk` symbol of its
  meaning, or else the identity item; a `7mfk` symbol that a homology item of
  the conversion reaches and that no evidence grounds takes its identity
  item.
- A wrapper with `[interp]` that only the registries and the entity files
  state takes the `l0` identity item of the interpolation conversion, at the
  first call of its kernel entry.
- The registries state no other evidence than the `rom-bytes` items of the
  image-byte keys, which the entries keep; a note that only the registries
  state for a symbol is dropped, the names that only the registries state
  become `former` names, and a record meaning takes its `storage`.
- The `target` link of each hook word of another layout than `7mfk` takes the
  `rom-bytes` item of the word.
- A status that the file of its meaning states keeps its entry; an
  `unresolved` status takes the search of the `7mfk` symbol of its meaning on
  its layout with the L0 digest of the layout and the text of its row as its
  note, and an `absent` status that its file does not state is refused.
- `feature/<feature>.toml` of `runtime`, `map_switching`, `rolling_launch`,
  and `can_telemetry` takes a `[[target]]` for each layout with the keys of
  its target, each symbol as the key of its meaning.

The telemetry profile (section 20.5):

- Each field takes `field/<name>.toml` with its keys, its `signal` as the
  reference of its signal, and its `source` as the reference of the meaning
  of its `7mfk` symbol for an `ecu_ram` field, or else as its allocation; the
  entry of the symbol must hold evidence where only the profile and the
  entity files state the symbol.
- The file of a source meaning takes the keys that its scale gives, which
  must equal those of the meaning; the remaining text becomes the summary of
  a meaning that it summarizes and no file does, or else a note of its file.
  The names that only the profile states become `former` names.
- `feature/can_telemetry.toml` takes the wire constants, `profiles`, and
  `contexts`, and the existing `7mfk` target of each feature takes the keys
  and the allocations that the profile gives it.
- The profile becomes the projection of the fields; the conversion lists each
  `ecu_ram` scale that the projection renders from its meaning in another
  string, and refuses any other change of the file.

The signal catalog (section 20.5):

- Each signal takes `signal/<id>.toml` with its keys and, in `observes`, the
  reference of the meaning of each `7mfk` symbol that it observes and each
  allocation, in the order of `sources`; the entry of an observed symbol that
  no evidence grounds, as a byte that only the DID table resolves, takes its
  identity item.
- The `width` of each observed symbol becomes the key of its meaning where
  the meaning has that width, or else the override of its entry.
- `feature/can_telemetry.toml` takes the catalog keys, and the catalog
  becomes the projection of the signals, which must equal the file.

The editor presentation (section 20.5):

- The file of the meaning of each `7mfk` symbol that the overrides state
  takes its `[editor]` or `[logparam]` as the table of the meaning, the
  operand of a static axis as the reference of its meaning; a symbol whose
  meaning holds another table keeps its own as the override of its entry.
- `feature/definitions.toml` takes `default_emit`, the switches, and the
  `7mfk` target with the JK08A image.
- The overrides file becomes the projection of the tables and of
  `definitions`, which must parse to the document of the file; the
  conversion lists the comments of the file that the projection drops.
"""

import argparse
from collections import Counter, defaultdict
from pathlib import Path
import sys

from kb import adapters, compile, graph, lock, match, repo, sites, store, tokens, write
from kb.adapters import (curated, definitions, interp, ledgers, native, overrides, profiles,
                         signals, telemetry)
from kb.model import Ref, SymbolKey
from kb.repo import KbError

# Differences that a refusal lists.
SHOWN = 20
# The keys of an unresolved status that a conversion states.
UNRESOLVED = ("method", "target", "count", "l0", "note")
# Identity items of the correspondence rows whose symbol no instruction of L0
# reaches: a test binds the routine that no pointer or branch enters.
ROW_TESTS = {
    "ignition_unreferenced_routine": {
        "kind": "test", "supports": "identity",
        "path": "patches/tests/test_rom_address_profiles.py",
        "key": "test_1me3b_unreferenced_ignition_routine_is_bound_to_the_image"},
}


def _location(item):
    """An evidence item as the files state it: a symbol `to` as its location,
    without the registry path and the legacy token."""
    return {key: value.location if isinstance(value, SymbolKey) else value
            for key, value in item.items() if key not in ("path", "legacy")}


def _notes(value):
    """The notes of a `note` key: none, one text, or a list of texts."""
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def _ledger_equal(first, second):
    """Compare selectors after the store's canonical ordering of nested tables."""
    return (store.render("fn", {"ledger": [first]})
            == store.render("fn", {"ledger": [second]}))


def _native_notes(held, stated, carriers, subject):
    """Keep owner notes when every carrier projects to the registry text.

    Image prefixes identify separate owner paragraphs. Their removal in the
    projection does not create another fact to append on reconversion.
    Non-equivalent or incomplete notes retain the ordinary strict rendering.
    """
    kept, incoming = _notes(held), _notes(stated)
    if kept and incoming and all(
            native._note(kept, carriers, image, subject)
            == native._note(incoming, carriers, image, subject)
            for image in carriers):
        return kept
    return kept + [note for note in incoming if note not in kept]


def _stating(items, item):
    """The item of an entry that states an item of a registry: the item
    itself, or the item with the note of a correspondence row that states its
    symbol; None for none."""
    for other in items:
        if other == item or ("note" not in item and "note" in other
                             and {key: value for key, value in other.items()
                                  if key != "note"} == item):
            return other
    return None


def _states_row(symbol, item, origin):
    """Whether an evidence item of a symbol states its correspondence row:
    homology toward the layout of the `7mfk` symbol `origin` of a `mapped`
    row, whose `to` names the symbol or a site of its match there, or else
    identity of the symbol other than image bytes."""
    if origin is not None:
        to = match.location(item.get("to"))
        return (item.get("supports") == "homology" and item.get("kind") in match.HOMOLOGY_KINDS
                and to is not None and to[0] == origin.layout)
    at = match.location(item.get("at"))
    return (item.get("supports", "identity") == "identity" and item.get("kind") != "rom-bytes"
            and (at is None or at[0] == symbol.layout))


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
        if adapter is telemetry:
            # The fields take the signals whose current fields list them.
            self.facts.stash["signal_fields"] = {
                slug: entity.refs["signal"][0][1]
                for (kind, slug), entity in before.entities.items()
                if kind == "field" and entity.refs.get("signal")}
        if adapter is overrides:
            # The overrides name the symbols of the model before them.
            self.facts.index(before.symbols)
        if adapter is ledgers:
            self.facts.index(before.symbols)
            self.facts.stash["telemetry_units"] = before.stash.get("telemetry_units", set())
        adapter.declare(self.facts, root)
        if adapter is signals:
            # The signals relate their sources to the RAM that the features
            # allocate, the DIDs that return them, the allocations of the
            # targets, and the fields of the model.
            self.facts.stash.update({name: before.stash[name]
                                     for name in ("feature_ram", "did_sources")})
            signals.relate_signals(self.facts, signals.allocations(before.targets),
                                   signals.served(before.entities))
        else:
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
        # {symbol key: registry notes that leave its keys}, {meaning key:
        # (names that leave it, former names that it takes)}, and {link key:
        # evidence items that its file entry adds}.
        self.dropped, self.names, self.linked = {}, {}, {}
        # {meaning id: document}, and {symbol key: items that a conversion
        # plans for the entry of the symbol after its row item}.
        self.documents, self.planned = {}, defaultdict(list)
        # {meaning key: notes of its file that precede those of the
        # registries}, [(field, scale before, scale after)] of the strings
        # that a projection renders from the model, and [(line, comment)] of
        # the comments of a registry that its projection drops.
        self.meaning_notes, self.changed, self.comments = {}, [], []
        self.ledger_tables = {}

    def run(self):
        getattr(self, self.adapter.__name__.rsplit(".", 1)[1])()
        return self.change.texts()

    def _document(self, meaning):
        """The document of the file of a meaning in the change."""
        if id(meaning) not in self.documents:
            _, found = self.change.document(meaning)
            self.documents[id(meaning)] = found
        return self.documents[id(meaning)]

    def ledgers(self):
        """Move ledger facts and retain selectors for the legacy CSV views."""
        from kb import ledger_projection as projection
        before, facts = self.before, self.facts
        keys = set(facts.symbols)
        for fact in facts.link_facts:
            keys.update((fact.owner, fact.to))
        for symbol in facts.symbols.values():
            keys.update(item["to"] for item in symbol.evidence
                        if isinstance(item.get("to"), SymbolKey))
        for _, _, table, _ in facts.meaning_tables:
            keys.update(item["to"] for item in table.get("evidence", ())
                        if isinstance(item.get("to"), SymbolKey))
        for key in sorted(keys):
            symbol = before.symbols.get(key)
            if symbol is None or symbol.meaning is None:
                raise KbError(f"{key.key}: no meaning before ledger conversion", code=3)
            self._entry(self._document(symbol.meaning), symbol)
        for anchor, props, _ in facts.meaning_props:
            meaning = before.meaning_of(anchor)
            document = self._document(meaning)
            for name, value in props.items():
                if value not in (None, "", []):
                    document[name] = meaning.props[name]
        for key, symbol in facts.symbols.items():
            held = before.symbols[key]
            entry = self._entry(self._document(held.meaning), held)
            for name in symbol.props:
                entry[name] = held.props[name]
            for item in symbol.evidence:
                if "legacy" not in item:
                    typed = {name: value.location if isinstance(value, SymbolKey) else value
                             for name, value in item.items()}
                    if typed not in entry.setdefault("evidence", []):
                        entry["evidence"].append(typed)
        # Lift each already merged link once, preserving both directions.
        wanted = {(before.meaning_of(fact.owner).key, fact.type,
                   before.meaning_of(fact.to).key, fact.props.get("slot"),
                   fact.props.get("offset")) for fact in facts.link_facts}
        for link in before.links:
            key = (link.owner.key, link.type, link.to.key, link.slot, link.offset)
            if key not in wanted:
                continue
            document = self._document(link.owner)
            entry = {"type": link.type, "to": link.to.key, **link.props}
            if link.slot is not None:
                entry["slot"] = link.slot
            if link.offset is not None:
                entry["offset"] = link.offset
            if link.roles:
                if len(link.roles) != 1:
                    raise KbError(f"{key}: multiple roles cannot project one link", code=3)
                entry["role"] = next(iter(link.roles))
            entry["layouts"] = sorted(link.stated)
            if link.evidence:
                entry["evidence"] = [_location(item) for item in link.evidence]
            existing = [item for item in document.get("link", ())
                        if (item.get("type"), item.get("to"), item.get("slot"),
                            item.get("offset")) != (link.type, link.to.key, link.slot,
                                                   link.offset)]
            document["link"] = [*existing, entry]
        for fact in before.self_links:
            if fact.type == "base":
                continue
            owner = before.by_node[fact.owner]
            if (owner.key, fact.type, owner.key, fact.props.get("slot"),
                    fact.props.get("offset")) not in wanted:
                continue
            document = self._document(owner)
            entry = {"type": fact.type, "to": owner.key, **fact.props,
                     "layouts": sorted(fact.layouts) if fact.layouts else [owner.home]}
            if entry not in document.get("link", ()):
                document["link"] = [*document.get("link", ()), entry]
        self._ledger_raw = defaultdict(list)
        self._ledger_items = defaultdict(list)
        for registry in ledgers.PATHS:
            for ordinal, row in enumerate(ledgers.rows(self.root, registry)):
                symbol = projection.subject(before, registry, row)
                document = self._document(symbol.meaning)
                entry = self._entry(document, symbol)
                if registry == "diagnostic-bindings":
                    self._ledger_diagnostic(symbol, document, row, projection)
                    marker = {"registry": registry, "order": ordinal, "binding": row["id"]}
                    existing = next((item for item in document.get("ledger", ())
                                     if item.get("binding") == row["id"]), None)
                    if existing is None:
                        document["ledger"] = [*document.get("ledger", ()), marker]
                    elif not _ledger_equal(existing, marker):
                        raise KbError(f"{row['id']}: diagnostic selector differs", code=3)
                    continue
                marker = {"registry": registry, "order": ordinal,
                          "fields": [name for name, value in row.items()
                                     if value and name not in projection.PLACEMENT
                                     and name not in tokens.SUPPORTS and name != "note"]}
                if registry == "dtc" and row.get("note"):
                    marker["fields"].append("note")
                notes = _notes(document.get("note"))
                if row.get("note") and registry != "dtc":
                    marker["notes"] = [notes.index(row["note"])]
                if registry == "vars" and row["units"] != (symbol.value("unit") or ""):
                    marker["storage_description"] = row["units"]
                for column, supports in tokens.SUPPORTS.items():
                    if column not in row:
                        continue
                    indices, dependencies = [], []
                    for token in tokens.parse(row[column]):
                        if token.role in tokens.PROCESS:
                            self.changed.append((f"{registry}:{symbol.key.location}:{column}",
                                                 token.text, "review history"))
                            continue
                        if token.role in tokens.DEPENDENCY and token.role != "trace":
                            to = self.facts.resolve(symbol.layout, token.address,
                                                    tokens.TARGET_KINDS[token.role],
                                                    ledgers.PATHS[registry].as_posix())
                            dependency = {"role": token.role,
                                          "to": before.meaning_of(to).key,
                                          "relies": token.relies, "supports": supports}
                            _, type_, _, end, props = ledgers.dependency(
                                symbol.key, to, token, supports, facts.row_tokens)
                            dependency.update(type=type_, end=end)
                            if props.get("role"):
                                dependency["link_role"] = props["role"]
                            if token.offset is not None:
                                dependency["offset"] = token.offset
                                dependency["offset_text"] = token.value.partition("+")[2]
                            dependencies.append(dependency)
                            continue
                        item, raw = self._ledger_item(symbol, registry, row, token, supports)
                        self._ledger_items[symbol.key].append(item)
                        self._ledger_raw[symbol.key].append(raw)
                        evidence = entry.setdefault("evidence", [])
                        if item not in evidence:
                            evidence.append(item)
                        index = evidence.index(item)
                        indices.append(index)
                        if token.role == "indirect_base":
                            marker.setdefault("offset", []).append({
                                "evidence": index, "text": token.value.partition("+")[2]})
                    if indices:
                        marker[supports] = indices
                    if dependencies:
                        marker["dependency"] = [*marker.get("dependency", ()), *dependencies]
                held = next((item for item in document.get("ledger", ())
                             if item["registry"] == registry), None)
                if held is None:
                    document["ledger"] = [*document.get("ledger", ()), marker]
                elif not _ledger_equal(held, marker):
                    raise KbError(f"{symbol.key.key}: ledger selector differs: "
                                  f"{held!r} != {marker!r}", code=3)
        for key in self._ledger_raw:
            self.evidence[key] = (self._ledger_items[key], self._ledger_raw[key])
        for ordinal, row in enumerate(curated.rows(self.root, ledgers.LAYOUT)):
            symbol = before.symbols[SymbolKey(ledgers.LAYOUT, "fn", int(row["addr"], 16))]
            document = self._document(symbol.meaning)
            marker = {"registry": "curated", "order": ordinal, "fields": ["name"]}
            if row["name"] != symbol.meaning.name:
                marker["name"] = row["name"]
            if row.get("note"):
                if len(row["note"]) <= curated.TITLE:
                    marker["title"] = True
                else:
                    marker["notes"] = [_notes(document.get("note")).index(row["note"])]
            held = next((item for item in document.get("ledger", ())
                         if item["registry"] == "curated"), None)
            if held is None:
                document["ledger"] = [*document.get("ledger", ()), marker]
            elif not _ledger_equal(held, marker):
                raise KbError(f"{symbol.key.key}: curated selector differs", code=3)
            # The file tier owns the selected name; retain previous curated
            # aliases as former names, as the other registry conversions do.
            old = {(name, tier) for name, tier, src in symbol.meaning.other_names
                   if src == (curated.DIRECTORY / "7mfk.csv").as_posix()}
            added = {(name, "former") for name, _ in old if name != symbol.meaning.name}
            if added:
                document["former"] = sorted(set(document.get("former", ()))
                                             | {name for name, _ in added})
            self.names[symbol.meaning.key] = (old, added)
        for key in sorted(keys):
            symbol = before.symbols[key]
            entry = self._entry(self._document(symbol.meaning), symbol)
            anchored = any(item.get("supports", "identity") == "identity"
                           and match.rank(item, symbol, before) >= match.CANDIDATE
                           and match._complete(item)
                           and match.verify(before, symbol, item) is None
                           for item in entry.get("evidence", ()))
            if anchored:
                continue
            item = ({"kind": "l0", "supports": "identity", "at": key.location}
                    if key.kind == "fn" else None)
            if item is not None and match.verify(before, symbol, item) is not None:
                item = None
            item = item or self._try_placed(symbol, {"kind": "l0", "supports": "identity"})
            item = item or match.base_item(before, symbol)
            if item is None or match.verify(before, symbol, item) is not None:
                raise KbError(f"{key.key}: L0 places no independent identity item; "
                              "nothing is written", code=3)
            entry.setdefault("evidence", []).append(item)
            converted, raw = self.evidence.setdefault(key, ([], []))
            converted.append(item)
            self.changed.append((key.location, "identity evidence", repr(item)))

    def _ledger_item(self, symbol, registry, row, token, supports=None):
        """Type one terminal without inventing a byte binding or a scale."""
        manual = repo.config(self.root).get("tokens", {}).get("manual", ())
        if token.role == "trace":
            to = self.facts.resolve(symbol.layout, token.address, tokens.TARGET_KINDS["trace"],
                                    ledgers.PATHS[registry].as_posix())
            raw = {"kind": "trace", "to": to, "relies": token.relies, "legacy": token.text}
        else:
            raw = tokens.evidence(token, symbol.layout, manual)
            if token.role not in tokens.TYPED_TERMINAL and registry != "dtc":
                raw["legacy"] = token.text
        if supports is not None:
            raw = {"kind": raw["kind"], "supports": supports,
                   **{key: value for key, value in raw.items() if key != "kind"}}
        item = {key: value.location if isinstance(value, SymbolKey) else value
                for key, value in raw.items() if key != "legacy"}
        if token.role == "trace":
            item["to"] = f"{self.before.meaning_of(to).key}/{to.layout}"
        if token.role == "site":
            named, span = sites.row_footprint(registry, row)
            layout = symbol.layout
            classification = sites.classify(
                int(token.value, 16), symbol.address, span, named,
                sites.references(layout, self.root), sites.owners(layout, self.root),
                match.images(self.before, layout)[0][1], sites.linkers(layout, self.root))
            item["kind"] = "l0-context" if classification else "unverified-site"
            if classification:
                footprint = {"span": span}
                if named:
                    footprint["named"] = [f"{addr:08x}" for addr in sorted(named)]
                item.update(key=classification, value=footprint)
            self.changed.append((f"{registry}:{symbol.key.location}", token.text,
                                 classification or "unverified site"))
        elif token.role == "rom_const" and (not match._complete(item)
                                               or match.verify(self.before, symbol, item)):
            item = {"kind": "unbound-constant", "value": token.value}
            if supports is not None:
                item["supports"] = supports
            self.changed.append((f"{registry}:{symbol.key.location}", token.text,
                                 "unbound constant: no grounded byte assertion"))
        return item, raw

    def _ledger_diagnostic(self, symbol, document, row, projection):
        """A diagnostic table retains its prose and typed terminal or trace items."""
        binding = next(item for item in symbol.meaning.tables.get("diagnostic", ())
                       if item["id"] == row["id"])
        typed = []
        for token in tokens.parse(row["evidence"]):
            if token.role in tokens.PROCESS:
                continue
            if token.role in tokens.DEPENDENCY:
                to = self.facts.resolve(symbol.layout, token.address,
                                        tokens.TARGET_KINDS[token.role],
                                        ledgers.PATHS["diagnostic-bindings"].as_posix())
                item = {"kind": "trace", "to": f"{self.before.meaning_of(to).key}/{to.layout}",
                        "relies": token.relies, "note": token.role}
            else:
                item, _ = self._ledger_item(symbol, "diagnostic-bindings", row, token)
            typed.append(item)
        found = {**binding, "evidence": typed}
        existing = [item for item in document.get("diagnostic", ()) if item["id"] != row["id"]]
        document["diagnostic"] = [*existing, found]
        self.ledger_tables.setdefault(symbol.meaning.key, {})[row["id"]] = found

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
                stated = list(entry.get("evidence", ()))
                items = [_stating(stated, item) or item for item in items]
                self.evidence[symbol.key] = (items, raw)
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
        document = self._document
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
        carriers = entry.get("images") or list(self.before.layouts[key.layout].images)
        incoming = _notes(fact.props.get("note"))
        notes = _native_notes(entry.get("note"), incoming, carriers,
                              f"{meaning.key}@{key.layout}")
        if notes:
            entry["note"] = notes[0] if len(notes) == 1 else notes
            self.notes[key] = notes
        # Only redundant registry prose leaves the comparison model. The
        # owner's image-specific paragraphs and all evidence remain intact.
        dropped = [note for note in incoming if note not in notes]
        if dropped:
            self.dropped[key] = dropped
        found = list(entry.get("evidence", ()))
        items = [_stating(found, _location(item)) or _location(item) for item in fact.evidence]
        self.evidence[key] = (items, fact.evidence)
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
        document = self._document
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
        found = self._try_placed(symbol, item)
        if found is None:
            raise KbError(f"{symbol.key.key}: no instruction of the L0 of {symbol.layout} that "
                          "touches its storage places its l0 evidence", code=3)
        return found

    def _try_placed(self, symbol, item):
        """`item` at the first census operand of the symbol's storage, at the
        first instruction that touches the storage, at the first load of a
        word of the storage from a literal pool, or else at the first place
        whose L0 references name the storage, where it verifies; None where
        no place does."""
        here = match.code(symbol.layout, self.root)
        span = range(symbol.address, symbol.address + (match.storage_size(symbol) or 1))
        sites = match.touching(self.before, symbol)
        operands = [site for site in sites
                    if any(address in span and relation.startswith("operand:")
                           for address, relation in here.touches(site))]
        ordered = [*operands, *sites, *match.loads(self.before, symbol),
                   *match.referencing(self.before, symbol)]
        for site in dict.fromkeys(ordered):
            found = {**item, "at": f"{symbol.layout}:{site:08x}"}
            if match.verify(self.before, symbol, found) is None:
                return found
        return None

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

    def profiles(self):
        before, facts = self.before, self.facts
        state = facts.stash[profiles.__name__]
        self.added = UNRESOLVED
        for key, fact in sorted(facts.symbols.items()):
            held = before.symbols.get(key)
            if held is None or held.meaning is None:
                raise KbError(f"{key.key} has no meaning in the model", code=3)
            if any(item.get("kind") != "rom-bytes" for item in fact.evidence):
                raise KbError(f"{key.key}: the registries state other evidence than image "
                              "bytes", code=3)
        rows = defaultdict(list)
        for row in state.resolved:
            first = row.hook is None or row.hook is state.words[(row.layout, row.hook.address)][0]
            if not row.role and row.right is not None and first:
                rows[row.right].append(row)
        # {symbol key: row item} and {symbol key: file items that the row
        # item replaces}.
        heads, replaced = {}, defaultdict(list)
        for key, fact in sorted(facts.symbols.items()):
            symbol = before.symbols[key]
            if fact.implicit:
                if symbol.implicit:
                    self.planned[key].append(self._identity(symbol, None))
                continue
            entry = self._entry(self._document(symbol.meaning), symbol)
            if key in rows:
                heads[key], replaced[key] = self._row_evidence(symbol, entry, rows[key])
            for item in fact.evidence:
                found = {name: item[name] for name in ("kind", "supports", "at", "value")}
                if found not in self.planned[key]:
                    self.planned[key].append(found)
            notes = set(fact.props.get("note", ())) - set(_notes(entry.get("note")))
            if notes:
                self.dropped[key] = notes
        for key, fact in sorted(facts.symbols.items()):
            symbol = before.symbols[key]
            if (fact.implicit or key in heads or self.planned.get(key)
                    or not _alone(symbol, self.inputs)):
                continue
            if not self._entry(self._document(symbol.meaning), symbol).get("evidence"):
                self.planned[key].append(self._grounding(symbol))
        # A wrapper that only the registries and the entity files state takes
        # the item of the interpolation registries at the call of its kernel.
        for key, fact in sorted(facts.symbols.items()):
            symbol = before.symbols[key]
            if (not fact.implicit and isinstance(symbol.value("interp"), dict)
                    and _alone(symbol, self.inputs)):
                self._plan(key, _kernel_call(before, symbol))
        self._ground_origins(heads)
        for key in sorted(set(heads) | set(self.planned)):
            symbol = before.symbols[key]
            entry = self._entry(self._document(symbol.meaning), symbol)
            head = [heads[key]] if key in heads else []
            items = head + [item for item in entry.get("evidence", ())
                            if not any(item is other for other in head)]
            items += [item for item in self.planned.get(key, ()) if item not in items]
            entry["evidence"] = items
            fact = facts.symbols.get(key)
            self.evidence[key] = (items, [*(fact.evidence if fact else ()), *replaced[key]])
        self._profile_links()
        for anchor, props, _ in facts.meaning_props:
            meaning = before.by_node[anchor]
            document = self._document(meaning)
            for name in props:
                document[name] = meaning.props[name]
        self._profile_names()
        self._profile_statuses()
        slugs = defaultdict(dict)
        for (slug, layout), target in sorted(facts.targets.items()):
            slugs[slug][layout] = self._profile_target(target)
        for slug, targets in sorted(slugs.items()):
            _, feature = self.change.designed("feature", slug)
            held = {entry.get("layout"): entry for entry in feature.get("target", ())}
            for layout, entry in targets.items():
                held[layout] = _over(held.get(layout, {}), entry)
            feature["target"] = [held[layout] for layout in sorted(held)]

    def _row_evidence(self, symbol, entry, rows):
        """(row item, replaced file items) of a symbol that correspondence rows
        state: an item of its entry that states the row, with the text of the
        row as its note, or else the homology item toward the `7mfk` symbol
        of a `mapped` row and the identity item of a `target-specific` row."""
        found = {(row.row["status"], row.row["evidence"], row.left) for row in rows}
        if len(found) != 1:
            raise KbError(f"{symbol.key.key}: {len(rows)} correspondence rows state the symbol "
                          "with different statuses, texts, or sources", code=3)
        [(status, text, left)] = found
        origin = None
        if status == "mapped":
            origin = self.before.symbols.get(left)
            if origin is None or origin.meaning is not symbol.meaning:
                raise KbError(f"{symbol.key.key}: its mapped row names no {profiles.CANONICAL} "
                              "symbol of its meaning", code=3)
        for item in entry.get("evidence", ()):
            if not _states_row(symbol, item, origin):
                continue
            if item.get("note") == text:
                return item, []
            if item.get("note") is not None:
                raise KbError(f"{symbol.key.key}: the {item.get('kind')} item of its entry "
                              "states another text than its row", code=3)
            original = dict(item)
            item["note"] = text
            return item, [original]
        if origin is not None:
            item = self._homology(symbol, origin)
            if item is None:
                raise KbError(f"{symbol.key.key}: no typed, manual, or l0 item toward "
                              f"{origin.key.location} verifies", code=3)
        else:
            item = self._identity(symbol, rows[0].row["key"])
        return {**item, "note": text}, []

    def _homology(self, symbol, origin):
        """The homology item of a symbol toward the `7mfk` symbol of its
        meaning: the typed item, a manual item for a symbol at the address
        of its origin that the hardware manual of the MCU places, or an `l0`
        item; None when none verifies."""
        found = match.typed(self.before, symbol, origin)
        if found is not None:
            return _location(found)
        if symbol.address == origin.address:
            key = next((item.get("key") for item in origin.evidence
                        if item.get("kind") == "manual"
                        and item.get("supports", "identity") == "identity"
                        and match.mcu_manual(self.before, item.get("key"))), None)
            vector = match.vector_item(self.before, origin)
            if key is None and vector is not None:
                key = self.before.config.get("manual", {}).get("vectors")
                if key:
                    self._vector(origin, key)
                    self._vector(symbol, key)
            if key:
                return {"kind": "manual", "supports": "homology", "to": origin.key.location,
                        "key": key}
        item = {"kind": "l0", "supports": "homology", "to": origin.key.location}
        if symbol.kind == "fn":
            found = {**item, "at": symbol.key.location}
            return found if match.verify(self.before, symbol, found) is None else None
        return self._try_placed(symbol, item)

    def _identity(self, symbol, row):
        """The identity item of a symbol on its own layout: the test that
        binds the symbol of a row, the entry of a function, an `l0` item, or
        an `indirect` base item."""
        if row in ROW_TESTS:
            return dict(ROW_TESTS[row])
        if symbol.kind == "fn":
            return {"kind": "l0", "supports": "identity",
                    "at": f"{symbol.layout}:{symbol.address:08x}"}
        if symbol.kind == "did":
            return self._slot(symbol)
        found = self._try_placed(symbol, {"kind": "l0", "supports": "identity"})
        if found is not None:
            return found
        found = match.base_item(self.before, symbol)
        if found is None:
            raise KbError(f"{symbol.key.key}: no instruction of the L0 of {symbol.layout} "
                          "places identity evidence", code=3)
        if symbol.kind == "hook":
            self._plan(symbol.key, self._word(symbol))
        return found

    def _plan(self, key, item):
        """Plan an item for the entry of a symbol after its row item."""
        if item not in self.planned[key]:
            self.planned[key].append(item)

    def _word(self, symbol):
        """The `rom-bytes` item of the stock word of a hook, which every image
        of its layout holds."""
        words = {data[symbol.address:symbol.address + 4].hex()
                 for _, data in match.images(self.before, symbol.layout)}
        if len(words) != 1:
            raise KbError(f"{symbol.key.key}: the images of {symbol.layout} hold different "
                          "stock words", code=3)
        return {"kind": "rom-bytes", "supports": "identity", "at": symbol.key.location,
                "value": words.pop()}

    def _vector(self, symbol, key):
        """Identity items of a slot of the vector table that VBR bases: the
        key of the table in the hardware manual, the base item at the load of
        VBR, and the stock word of the slot."""
        vector = match.vector_item(self.before, symbol)
        if vector is None:
            raise KbError(f"{symbol.key.key}: the slot lies outside the vector table", code=3)
        for item in ({"kind": "manual", "supports": "identity", "key": key}, vector,
                     self._word(symbol)):
            self._plan(symbol.key, item)

    def _slot(self, symbol):
        """The `did-table` item of a DID slot: the pointer word that every
        image of its layout holds at the slot."""
        words = {int.from_bytes(data[symbol.address:symbol.address + 4], "big")
                 for _, data in match.images(self.before, symbol.layout)}
        if len(words) != 1:
            raise KbError(f"{symbol.key.key}: the images of {symbol.layout} hold different "
                          "words at the slot", code=3)
        return {"kind": "did-table", "supports": "identity", "at": symbol.key.location,
                "value": f"{words.pop():08x}"}

    def _grounding(self, symbol):
        """The item that grounds a symbol that only the registries state:
        homology toward the `7mfk` symbol of its meaning, or else identity."""
        origin = symbol.meaning.symbols.get(profiles.CANONICAL)
        if origin is not None and origin is not symbol:
            found = self._homology(symbol, origin)
            if found is not None:
                return found
        return self._identity(symbol, None)

    def _ground_origins(self, heads):
        """Identity items of the `7mfk` symbols that the homology items of the
        conversion reach, where no evidence grounds them."""
        before = self.before
        origins = set()
        for key in set(heads) | set(self.planned):
            symbol = before.symbols[key]
            for item in ([heads[key]] if key in heads else []) + self.planned[key]:
                if item.get("supports") == "homology":
                    other = match.context(before, symbol, item).other
                    if other is not None and other is not symbol:
                        origins.add(other.key)
        ranks = match.grounded(before, sorted(origins))
        for key in sorted(origins):
            identity = [item for item in self.planned.get(key, ())
                        if item.get("supports", "identity") == "identity"]
            if ranks[key][0] < match.CANDIDATE and not identity:
                self.planned[key].append(self._identity(before.symbols[key], None))

    def _profile_links(self):
        """The `target` link of each hook word of another layout than `7mfk`
        to the meaning at its stock word, with the image bytes of the word."""
        for fact in self.facts.link_facts:
            owner, to = self.before.symbols[fact.owner], self.before.symbols[fact.to]
            document = self._document(owner.meaning)
            entry = next((link for link in document.get("link", ())
                          if (link.get("type"), link.get("to")) == (fact.type, to.meaning.key)
                          and "slot" not in link and "offset" not in link), None)
            if entry is None:
                entry = {"type": fact.type, "to": to.meaning.key}
                document["link"] = [*document.get("link", ()), entry]
            item = {"kind": "rom-bytes", "supports": "identity", "at": owner.key.location,
                    "value": f"{to.address:08x}"}
            found = entry.setdefault("evidence", [])
            if item not in found:
                found.append(item)
            key = (owner.meaning.key, fact.type, to.meaning.key, None, None)
            self.linked.setdefault(key, []).append(item)

    def _profile_names(self):
        """Former names of the meanings whose other names only the registries
        state."""
        for meaning in self.before.meanings:
            if id(meaning) not in self.documents:
                continue
            sources = defaultdict(set)
            for name, tier, src in meaning.other_names:
                sources[name, tier].add(src)
            leaving = {pair for pair, found in sources.items() if found <= self.inputs}
            kept = {name for name, _ in set(sources) - leaving}
            former = {name for name, _ in leaving if name not in kept and name != meaning.name}
            if not leaving:
                continue
            document = self.documents[id(meaning)]
            if former:
                document["former"] = sorted(set(document.get("former", ())) | former)
            self.names[meaning.key] = (leaving, {(name, "former") for name in former})

    def _profile_statuses(self):
        """The statuses of the rows: a status of the file of its meaning keeps
        its entry, and an `unresolved` status takes the search of the `7mfk`
        symbol of its meaning."""
        before = self.before
        for anchor, layout, state, props, evidence, _, yields in self.facts.status_facts:
            meaning = before.by_node[anchor]
            if yields and layout in meaning.symbols:
                continue
            key = (id(meaning), layout)
            if key in self.statuses:
                status, raw = self.statuses[key]
                self.statuses[key] = (status, [*raw, *evidence])
                continue
            document = self._document(meaning)
            held = next((entry for entry in document.get("status", ())
                         if entry.get("layout") == layout), None)
            if held is not None:
                if held.get("state") != state:
                    raise KbError(f"{meaning.key} is {state} on {layout} in the registries and "
                                  f"{held.get('state')} in its file", code=3)
                self.statuses[key] = ({"layout": layout, "state": state}, evidence)
                continue
            if state != "unresolved":
                raise KbError(f"the {state} status of {meaning.key} on {layout} has no entry "
                              "with its evidence in the file of its meaning", code=3)
            origin = meaning.symbols.get(profiles.CANONICAL)
            if origin is None:
                raise KbError(f"{meaning.key} has no {profiles.CANONICAL} symbol to search "
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
            document["status"] = [*document.get("status", ()), status]
            self.statuses[key] = (status, evidence)

    def _profile_target(self, target):
        """The `[[target]]` entry of a feature on a layout, with each symbol
        as the key of its meaning."""
        def value(item):
            if isinstance(item, SymbolKey):
                held = self.before.meaning_of(item)
                if held is None:
                    raise KbError(f"the {target.feature} target of {target.layout} names "
                                  f"{item.key}, which has no meaning", code=3)
                return held.key
            if isinstance(item, dict):
                return {name: value(entry) for name, entry in item.items()}
            if isinstance(item, list):
                return [value(entry) for entry in item]
            return item

        props = value(target.props)
        if "requires" in props:
            props["requires"] = sorted(set(props["requires"]))
        if isinstance(props.get("note"), list) and len(props["note"]) == 1:
            props["note"] = props["note"][0]
        return {"layout": target.layout, "status": target.status, **props}

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

    def telemetry(self):
        before, facts = self.before, self.facts
        for key in sorted(facts.symbols):
            symbol = before.symbols.get(key)
            if symbol is None or symbol.meaning is None:
                raise KbError(f"{key.key} has no meaning in the model", code=3)
            if _alone(symbol, self.inputs) and key not in before.file_evidence:
                raise KbError(f"{key.key}: only the profile and the entity files state the "
                              "source, and its entry holds no evidence", code=3)
            self._entry(self._document(symbol.meaning), symbol)
        for anchor, props, _ in facts.meaning_props:
            meaning = before.by_node[anchor]
            document = self._document(meaning)
            for name, value in props.items():
                if name == "summary":
                    self._rest(meaning, document, value)
                    continue
                if name in telemetry.NAMED:
                    # The profile names the values or bits that the meaning
                    # states with their summaries, levels, and evidence.
                    held = [(item.get(name), item.get("name"))
                            for item in meaning.props.get(name) or ()]
                    stated = [(item[name], item["name"]) for item in value]
                    if held and sorted(held) != sorted(stated):
                        raise KbError(f"{meaning.key}: {name} {stated} of the profile disagrees "
                                      f"with {held}", code=3)
                    if not held:
                        document[name] = value
                    continue
                if meaning.props.get(name) != value:
                    raise KbError(f"{meaning.key}: {name} = {value!r} of the profile disagrees "
                                  f"with {meaning.props.get(name)!r}", code=3)
                document[name] = value
        self._profile_names()
        for (kind, name), entity in sorted(facts.entities.items()):
            if kind == "field":
                _, document = self.change.designed(kind, name)
                _agree(document, self._field(entity), f"{name}/field")
        _, document = self.change.designed("feature", telemetry.FEATURE)
        _agree(document, facts.entities[("feature", telemetry.FEATURE)].props,
               f"{telemetry.FEATURE}/feature")
        for (slug, layout), target in sorted(facts.targets.items()):
            _, document = self.change.designed("feature", slug)
            entry = next((item for item in document.get("target", ())
                          if item.get("layout") == layout), None)
            if entry is None:
                raise KbError(f"{slug}/feature has no {layout} target for the keys of the "
                              "profile", code=3)
            _agree(entry, target.props, f"{slug}/feature@{layout}")

    def _field(self, entity):
        """The document of a field: its keys, its signal, and its source."""
        found = dict(entity.props)
        if entity.refs.get("signal"):
            found["signal"] = "{1}/{0}".format(*entity.refs["signal"][0])
        if entity.refs.get("source"):
            [key] = entity.refs["source"]
            found["source"] = self.before.symbols[key].meaning.key
        return found

    def _rest(self, meaning, document, text):
        """The remaining text of a scale: the summary of a meaning that it
        summarizes and no file does, or else a note of its file."""
        if meaning.props.get("summary") == text and document.get("summary") in (None, text):
            document["summary"] = text
            return
        notes = _notes(document.get("note"))
        if text not in notes:
            notes.append(text)
            document["note"] = notes[0] if len(notes) == 1 else notes
        self.meaning_notes[meaning.key] = notes

    def signals(self):
        before, facts = self.before, self.facts
        keys = sorted({key for key, _, _ in facts.symbol_keys})
        ranks = match.grounded(before, keys)
        for key in keys:
            symbol = before.symbols.get(key)
            if symbol is None or symbol.meaning is None:
                raise KbError(f"{key.key} has no meaning in the model", code=3)
            entry = self._entry(self._document(symbol.meaning), symbol)
            if ranks[key][0] < match.CANDIDATE:
                # A symbol that no evidence grounds, as one that only the DID
                # table resolves, takes its identity item.
                items = list(entry.get("evidence", ()))
                found = self._identity(symbol, None)
                if found not in items:
                    items.append(found)
                entry["evidence"] = items
                self.evidence[key] = (items, [])
        for key, props, _ in facts.symbol_keys:
            symbol = before.symbols[key]
            document = self._document(symbol.meaning)
            entry = self._entry(document, symbol)
            for name, value in props.items():
                if symbol.value(name) != value:
                    raise KbError(f"{key.key}: {name} = {value!r} of the signals disagrees "
                                  f"with {symbol.value(name)!r}", code=3)
                # The key of the meaning, or else the override of the symbol.
                if symbol.meaning.props.get(name) == value:
                    _agree(document, {name: value}, symbol.meaning.key)
                else:
                    _agree(entry, {name: value}, key.key)
        for (kind, slug), entity in sorted(facts.entities.items()):
            if kind == "signal":
                _, document = self.change.designed(kind, slug)
                _agree(document, self._signal(entity), f"{slug}/signal")
        _, document = self.change.designed("feature", signals.FEATURE)
        _agree(document, facts.entities[("feature", signals.FEATURE)].props,
               f"{signals.FEATURE}/feature")

    def _signal(self, entity):
        """The document of a signal: its keys, and in `observes` the meanings
        of its symbols and its allocations in the order of the catalog."""
        found = {key: value for key, value in entity.props.items()
                 if key not in ("observes", "note")}
        observes = [self.before.symbols[item].meaning.key if isinstance(item, SymbolKey)
                    else item for item in entity.refs.get("observes", ())]
        if observes:
            found["observes"] = observes
        notes = _notes(entity.props.get("note"))
        if notes:
            found["note"] = notes[0] if len(notes) == 1 else notes
        return found

    def overrides(self):
        before, facts = self.before, self.facts
        for key, props, _ in facts.symbol_keys:
            symbol = before.symbols.get(key)
            if symbol is None or symbol.meaning is None:
                raise KbError(f"{key.key} has no meaning in the model", code=3)
            document = self._document(symbol.meaning)
            for name, value in props.items():
                if symbol.value(name) != value:
                    raise KbError(f"{key.key}: the {name} of the overrides disagrees with "
                                  f"{symbol.value(name)!r}", code=3)
                # The table of the meaning, or else the override of the symbol.
                stated = {name: self._stated(value)}
                if symbol.meaning.props.get(name) == value:
                    _agree(document, stated, symbol.meaning.key)
                else:
                    _agree(self._entry(document, symbol), stated, key.key)
        _, document = self.change.designed("feature", overrides.FEATURE)
        _agree(document, facts.entities[("feature", overrides.FEATURE)].props,
               f"{overrides.FEATURE}/feature")
        targets = {entry.get("layout"): entry for entry in document.get("target", ())}
        for (slug, layout), target in sorted(facts.targets.items()):
            if slug != overrides.FEATURE:
                continue
            props = {"status": target.status, **target.props}
            if layout in targets:
                _agree(targets[layout], props, f"{slug}/feature@{layout}")
            else:
                targets[layout] = {"layout": layout, **props}
        document["target"] = [targets[layout] for layout in sorted(targets)]

    def _stated(self, table):
        """A table of a meaning as its file states it: the operand of a static
        axis as the reference of its meaning."""
        operand = table.get(overrides.OPERAND)
        if not isinstance(operand, SymbolKey):
            return table
        held = self.before.meaning_of(operand)
        if held is None:
            raise KbError(f"the static axis operand {operand.key} has no meaning", code=3)
        return {**table, overrides.OPERAND: held.key}

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
        for key, notes in self.dropped.items():
            where = (key.location, key.kind)
            name, generated, former, props, evidence, meaning = found["symbols"][where]
            props = dict(props)
            kept = tuple(note for note in props.get("note", ()) if note not in notes)
            if kept:
                props["note"] = kept
            else:
                props.pop("note", None)
            found["symbols"][where] = (name, generated, former, tuple(sorted(props.items())),
                                       evidence, meaning)
        for key, (leaving, added) in self.names.items():
            entry = found["meanings"][key]
            entry["names"] = tuple(sorted((set(entry["names"]) - leaving) | added))
        for key, notes in self.meaning_notes.items():
            entry = found["meanings"][key]
            props = dict(entry["props"])
            props["note"] = tuple(notes) + tuple(note for note in props.get("note", ())
                                                 if note not in notes)
            entry["props"] = tuple(sorted(props.items()))
        for key, items in self.linked.items():
            props, evidence, stated, roles = found["links"][key]
            found["links"][key] = (props, evidence | {_value(before, item) for item in items},
                                   stated, roles)
        if self.adapter is ledgers:
            for key, rows in self.ledger_tables.items():
                entry = found["meanings"][key]
                tables = dict(entry["tables"])
                meaning = next(item for item in before.meanings if item.key == key)
                bindings = [item for item in meaning.tables.get("diagnostic", ())
                            if item["id"] not in rows]
                tables["diagnostic"] = tuple(sorted(
                    _value(before, bindings + list(rows.values())), key=repr))
                entry["tables"] = tuple(sorted(tables.items()))
            for link in before.links:
                # Layout selection is explicit in a converted link; its
                # semantic endpoints, claims, roles, and evidence stay intact.
                if id(link.owner) not in self.documents:
                    continue
                key = (link.owner.key, link.type, link.to.key, link.slot, link.offset)
                props, evidence, stated, roles = found["links"][key]
                props = dict(props)
                document = self.documents[id(link.owner)]
                held = next((item for item in document.get("link", ())
                             if (item["type"], item["to"], item.get("slot"), item.get("offset"))
                             == (link.type, link.to.key, link.slot, link.offset)), None)
                if held is not None and held.get("layouts"):
                    props["layouts"] = tuple(held["layouts"])
                    found["links"][key] = (tuple(sorted(props.items())), evidence, stated, roles)
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


def _over(held, entry):
    """The target entry of a registry over the entry of its file: a key of
    the registry replaces that of the file, and a table of named entries keeps
    the entries of the file that the registry lacks, which a later conversion
    owns."""
    found = dict(held)
    for name, value in entry.items():
        current = found.get(name)
        found[name] = ({**current, **value} if isinstance(value, dict)
                       and isinstance(current, dict) else value)
    return found


def _agree(document, props, subject):
    """Merge keys into a document; a key that holds another value refuses, and
    a table of named entries takes the entries that it lacks."""
    for name, value in props.items():
        held = document.get(name)
        if isinstance(held, dict) and isinstance(value, dict):
            _agree(held, value, f"{subject}.{name}")
        elif held is None:
            document[name] = value
        elif held != value:
            raise KbError(f"{subject}: {name} = {value!r} of the registry disagrees with "
                          f"{held!r} of its file", code=3)


def _value(model, value):
    """A comparable form of a value: symbols as locations, tables as sorted
    pairs, and a kernel of `[interp]` as the key of its meaning."""
    if isinstance(value, SymbolKey):
        return value.location
    if isinstance(value, Ref):
        return repr(value)
    if isinstance(value, dict):
        if value.get("kind") == "trace" and isinstance(value.get("to"), str) \
                and "/" in value["to"]:
            name, kind, layout = value["to"].split("/")
            meaning = next((item for item in model.meanings if item.key == f"{name}/{kind}"), None)
            if meaning is not None and layout in meaning.symbols:
                value = {**value, "to": meaning.symbols[layout].key}
        if "kernel" in value and "access" in value:
            held = model.symbols.get(value["kernel"])
            if held is not None and held.meaning is not None:
                value = {**value, "kernel": held.meaning.key}
        result = {}
        for key, item in value.items():
            converted = _value(model, item)
            if key in ("evidence", "diagnostic") and isinstance(item, (list, tuple)):
                converted = tuple(sorted(set(converted) if key == "evidence" else converted,
                                         key=repr))
            result[key] = converted
        return tuple(sorted(result.items()))
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
    entities = {key: (_value(model, entity.props), tuple(sorted(
        (name, frozenset(_value(model, item) for item in items))
        for name, items in entity.refs.items())))
        for key, entity in model.entities.items()}
    return {"symbols": symbols, "meanings": meanings, "links": links, "targets": targets,
            "entities": entities}


def _target_props(model, props):
    """The keys of a target with `requires` as the set of its meanings and the
    symbol of an `unsupported` entry as its meaning, which a registry states
    by their symbols and a file by their references."""
    def meaning(key):
        found = model.meaning_of(key) if isinstance(key, SymbolKey) else None
        return found.key if found is not None else key

    found = dict(props)
    if "requires" in props:
        found["requires"] = frozenset(meaning(key) for key in props["requires"])
    if "unsupported" in props:
        found["unsupported"] = [{**item, "symbol": meaning(item.get("symbol"))}
                                for item in props["unsupported"]]
    return found


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
        counts = Counter(issue.check for issue in refused)
        shown = [issue for check in sorted(counts)
                 for issue in [item for item in refused if item.check == check][:5]]
        raise KbError("\n".join(
            [f"the conversion adds {len(refused)} issues; nothing is written"]
            + [f"  {check}: {count} issues" for check, count in sorted(counts.items())]
            + [f"  {issue.check}: {issue.path}: {issue.subject}: {issue.message}"
               for issue in shown[:SHOWN]]), code=3)
    rendered = projections(adapter, result)
    if adapter is ledgers:
        from kb import ledger_projection
        for path, text in rendered.items():
            original = (root / path).read_text(encoding="utf-8")
            ledger_projection.validate_conversion(path, original, text)
            if original != text:
                texts[Path(path)] = text
    if adapter is overrides:
        # The projection renders the file without its comments and wraps its
        # notes.
        path = overrides.OVERRIDES
        text, found = (root / path).read_text(encoding="utf-8"), rendered[path.as_posix()]
        conversion.comments, conversion.changed = overrides.dropped(text, found)
        if found != text:
            texts = {**texts, path: found}
    if adapter is telemetry:
        # The projection renders each ecu_ram scale from its meaning.
        path = telemetry.PROFILE
        conversion.changed = telemetry.scale_changes(
            (root / path).read_text(encoding="utf-8"), telemetry.profile_document(result))
        if conversion.changed:
            texts = {**texts, path: rendered[path.as_posix()]}
    differ = [path for path, text in rendered.items()
              if Path(path) not in texts and (not (root / path).exists()
                                              or (root / path).read_text(encoding="utf-8")
                                              != text)]
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
    if adapter is profiles:
        return profiles.render_registries(model)
    if adapter is telemetry:
        return {telemetry.PROFILE.as_posix(): telemetry.render_profile(
            telemetry.profile_document(model))}
    if adapter is signals:
        return {signals.SIGNALS.as_posix(): signals.render_catalog(
            signals.catalog_document(model))}
    if adapter is overrides:
        return {overrides.OVERRIDES.as_posix(): overrides.render_presentation(
            overrides.presentation_document(model))}
    if adapter is ledgers:
        from kb import ledger_projection
        return ledger_projection.render(model)
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
    for name, old, new in conversion.changed:
        print(f"{name}: {old!r} -> {new!r}")
    for line, comment in conversion.comments:
        print(f"dropped {line}: {comment}")
    print(f"{args.registry}: {len(conversion.evidence)} symbols, {len(conversion.statuses)} "
          f"statuses, {len(texts)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
