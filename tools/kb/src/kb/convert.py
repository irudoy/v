"""Comparable model facts used by writer and ledger preservation checks."""

from kb.model import Ref, SymbolKey

SHOWN = 20
_ATOM_TYPES = (type(None), bool, int, float, str, bytes)


def _value(model, value):
    """A comparable form of a value: symbols as locations, tables as sorted
    pairs, and a kernel of `[interp]` as the key of its meaning."""
    if type(value) in _ATOM_TYPES:
        return value
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
        for name, items in entity.refs.items())), _value(model, entity.steps))
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
