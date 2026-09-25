"""Property values that Memgraph stores."""

from kb.model import SymbolKey


def value(item):
    """A property value that Memgraph stores: symbol keys become their key strings,
    sets become sorted lists, and empty values vanish."""
    if isinstance(item, SymbolKey):
        return item.key
    if isinstance(item, dict):
        return {str(key): value(entry) for key, entry in item.items()
                if entry is not None and entry != [] and entry != ()}
    if isinstance(item, (set, frozenset)):
        return sorted(value(entry) for entry in item)
    if isinstance(item, (list, tuple)):
        return [value(entry) for entry in item]
    return item


def properties(mapping):
    return {key: stored for key, stored in value(mapping).items() if stored != {}}
