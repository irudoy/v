"""Inactive owner documents retain names and refuse incoming consumers."""

from kb.model import SymbolKey


def records(model):
    return getattr(model, 'stash', {}).get('retired', ())


def aliases(kind, name, document):
    """Semantic, generated and former names retained by an inactive document."""
    found = {name}
    found.update(item.split('/', 1)[0] for item in document.get('former', ()))
    for entry in document.get('symbol', ()):
        if entry.get('name'):
            found.add(entry['name'])
        found.update(item.split('/', 1)[0] for item in entry.get('former', ()))
    return found


def nodes(model):
    """Name-only inactive index; no claim or executable symbol is emitted."""
    found = []
    for kind, name, document, source in records(model):
        references = {f'{name}/{kind}'}
        for entry in document.get('symbol', ()):
            for alias in aliases(kind, name, document):
                references.add(f'{alias}/{kind}/{entry["layout"]}-{entry["address"]}')
            references.update(entry.get('former', ()))
        found.append(dict(key=f'{name}/{kind}', kind=kind, names=sorted(aliases(kind, name, document)),
                          references=sorted(references), src=[source], producer='claim'))
    return found


def touches(value, key, symbol_keys):
    if isinstance(value, SymbolKey):
        return value in symbol_keys
    if isinstance(value, dict):
        return any(touches(item, key, symbol_keys) for item in value.values())
    if isinstance(value, (list, tuple, set, frozenset)):
        if isinstance(value, tuple) and len(value) == 2 and all(isinstance(item, str) for item in value):
            if f'{value[1]}/{value[0]}' == key:
                return True
        return any(touches(item, key, symbol_keys) for item in value)
    return isinstance(value, str) and (value == key or value.startswith(key + '/'))


def consumers(model, subject):
    """Every structured incoming claim, required binding and generated view."""
    key = subject.key
    symbols = set(symbol.key for symbol in subject.symbols.values()) if hasattr(subject, 'symbols') else set()
    found = set()
    if any(not source.startswith('kb/') for source in subject.sources):
        found.add('an unconverted registry still declares this entity')
    for symbol_key in symbols:
        symbol = model.symbols[symbol_key]
        if any(not source.startswith('kb/') for source in symbol.sources):
            found.add('an unconverted registry still declares a symbol')
        if symbol.props.get('curated'):
            found.add('a curated-name projection selects the symbol')
    props = subject.props
    tables = getattr(subject, 'tables', {})
    if any(props.get(name) for name in ('editor', 'logparam', 'interp', 'catalog')) or tables.get('diagnostic'):
        found.add('a generated consumer selects this entity')
    if any(owner is subject for owner, _ in model.files.values()):
        from kb import store
        for (kind, name), (owner, source) in model.files.items():
            if owner is subject and store.load(model.root, source, model.overlay).get('ledger'):
                found.add('a ledger projection selects this meaning')
    for link in model.links:
        if link.owner is not subject and (link.to is subject or touches(link.props, key, symbols)
                                          or touches(link.evidence, key, symbols)):
            found.add(f'{link.owner.key}: incoming {link.type} relation')
    for meaning in model.meanings:
        if meaning is subject:
            continue
        values = [meaning.props, meaning.tables,
                  *(symbol.props for symbol in meaning.symbols.values()),
                  *(symbol.evidence for symbol in meaning.symbols.values())]
        if touches(values, key, symbols):
            found.add(f'{meaning.key}: incoming owned reference')
    for entity in model.entities.values():
        if entity is not subject and touches([entity.refs, entity.steps, entity.props], key, symbols):
            found.add(f'{entity.key}: incoming designed reference')
    for (feature, layout), target in model.targets.items():
        if f'{feature}/feature' != key and touches(target.props, key, symbols):
            found.add(f'{feature}/feature on {layout}: incoming target reference')
    return sorted(found)


def preserved(before, after):
    """An inactive document cannot be removed, rewritten or reactivated."""
    held = {(kind, name): (document, source) for kind, name, document, source in records(after)}
    return [f'{source}: inactive owner and its reserved names must remain unchanged'
            for kind, name, document, source in records(before)
            if held.get((kind, name)) != (document, source)]
