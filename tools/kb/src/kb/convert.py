"""Conversions of legacy registries into entity files (tools/kb/SPEC.md,
sections 20 and 21.1).

`uv run python -m kb.convert <registry> [--dry-run]` converts a registry
whose adapter `adapters.CONVERTED` lists. It compiles the model with the
adapters of `adapters.ORDER`, writes the facts that the registry's adapter
states into the files of their meanings through `write.Change`, and compiles
the model from those files with the adapters of the compiler. It refuses the
conversion with exit code 3 when the two models differ beyond the rules of
the registry, when the files add an issue of a model check or a registry
disagreement, or when a projection of the registry differs from its file;
otherwise it writes the files and `kb/names.csv` under the lock and loads
the result into the graph. On a converted tree it writes nothing.

The interpolation registries (section 20.3):

- The meaning of every symbol that the registries state takes `[interp]`
  and each of its symbols an entry with the override of its layout and the
  typed evidence of the registries, whose `to` becomes a location.
- A wrapper symbol that no other registry states takes `l0` identity
  evidence at the first instruction of its body that calls its kernel entry,
  or at its entry when it is its own kernel.
- An `unsupported` correspondence becomes an `unresolved` status with the L0
  digest of its layout and without the registry evidence.
"""

import argparse
import sys

from kb import adapters, compile, graph, lock, match, repo, store, write
from kb.adapters import interp
from kb.model import Ref, SymbolKey
from kb.repo import KbError

# Differences that a refusal lists.
SHOWN = 20


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
        if self.facts.issues:
            lines = [f"the registry has {len(self.facts.issues)} issues; nothing is written"]
            lines += [f"  {issue.check}: {issue.path}: {issue.subject}: {issue.message}"
                      for issue in self.facts.issues[:SHOWN]]
            raise KbError("\n".join(lines), code=3)
        self.change = write.Change(before, None, root)
        # {symbol key: (converted items, raw items)} and {(meaning id, layout):
        # (converted status, raw evidence)}.
        self.evidence, self.statuses = {}, {}

    def run(self):
        getattr(self, self.adapter.__name__.rsplit(".", 1)[1])()
        return self.change.texts()

    def interp(self):
        before, change = self.before, self.change
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
        by_id = {id(meaning): meaning for meaning in before.meanings}
        for (key, layout), (status, raw) in self.statuses.items():
            meaning = by_id[key]
            entry = found["meanings"][meaning.key]
            listed = dict(entry["statuses"])
            state, props, evidence = listed[layout]
            props = _value(before, {**dict(props), "l0": status["l0"]})
            evidence = frozenset(set(evidence) - {_value(before, item) for item in raw})
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
    targets = {key: (target.status, _value(model, target.props))
               for key, target in model.targets.items()}
    entities = {key: _value(model, entity.props) for key, entity in model.entities.items()}
    return {"symbols": symbols, "meanings": meanings, "links": links, "targets": targets,
            "entities": entities}


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
    before = compile.build(root, order=adapters.ORDER)
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
