"""Exact owning attachments of TEST evidence in a compiled native model.

An origin identifies an attachment and its current semantic context. It grants
no evidence level, infers no supported fact and supplies no execution receipt.
"""

from dataclasses import dataclass
import json
import re

from kb.model import SymbolKey
from kb.test_contract import digest, encode, exact, json_text

SYMBOL_KEY = re.compile(r'([0-9a-z]+)-([0-9a-f]{8})/([a-z]+)')


def _snapshot(value):
    """Immutable typed text; callers cannot mutate a retained model snapshot."""
    return json_text(encode(value))


@dataclass(frozen=True)
class Origin:
    kind: str
    owner: str
    locator_text: str
    context_text: str
    evidence_text: str
    path: str
    selector: str
    explicit_support: str | None

    @property
    def key(self):
        """Stable attachment identity; changed facts are checked separately."""
        return digest({'locator': json.loads(self.locator_text),
                       'path': self.path, 'selector': self.selector})

    @property
    def context_digest(self):
        return digest({'context': json.loads(self.context_text),
                       'evidence': json.loads(self.evidence_text)})

    def packet(self):
        return {'key': self.key, 'kind': self.kind, 'owner': self.owner,
                'locator': json.loads(self.locator_text),
                'context': json.loads(self.context_text),
                'evidence': json.loads(self.evidence_text),
                'path': self.path, 'selector': self.selector,
                'explicit_support': self.explicit_support,
                'context_digest': self.context_digest}


def _make(kind, owner, route, evidence, context):
    if not isinstance(evidence, dict):
        raise ValueError('a TEST origin requires a typed evidence table')
    if evidence.get('kind') != 'test':
        return None
    path, selector = evidence.get('path'), evidence.get('key')
    if type(path) is not str or not path or type(selector) is not str or not selector:
        raise ValueError('a TEST origin requires its exact source path and selector')
    support = evidence.get('supports')
    if support is not None and type(support) is not str:
        raise ValueError('a TEST origin preserves one explicit supported fact')
    context = context() if callable(context) else context
    return Origin(kind, owner, json_text(route), _snapshot(context),
                  _snapshot(evidence), path, selector, support)


def _symbol_state(symbol):
    meaning = symbol.meaning
    return {'symbol': symbol.key, 'meaning': None if meaning is None else meaning.key,
            'name': symbol.name, 'generated': symbol.generated, 'former': symbol.former,
            'properties': symbol.props, 'sources': symbol.sources,
            'implicit': symbol.implicit,
            'width': symbol.value('width'), 'signed': symbol.value('signed')}


def _meaning_state(meaning):
    return {'meaning': meaning.key, 'kind': meaning.kind,
            'semantic': meaning.semantic, 'properties': meaning.props,
            'tables': meaning.tables, 'names': meaning.other_names,
            'sources': meaning.sources,
            'symbols': {layout: _symbol_state(symbol)
                        for layout, symbol in sorted(meaning.symbols.items())},
            'statuses': {layout: {'state': status.state, 'properties': status.props,
                                  'evidence': status.evidence, 'sources': status.sources}
                         for layout, status in sorted(meaning.statuses.items())}}


def _symbol_context(symbol):
    return {'subject': _symbol_state(symbol),
            'meaning': None if symbol.meaning is None else _meaning_state(symbol.meaning)}


def _link_identity(link):
    return {'owner': link.owner.key, 'type': link.type, 'to': link.to.key,
            'slot': link.slot, 'offset': link.offset}


def _link_context(link):
    return {'link': {**_link_identity(link), 'properties': link.props,
                     'roles': link.roles, 'stated': link.stated, 'sources': link.sources},
            'owner': _meaning_state(link.owner), 'to': _meaning_state(link.to)}


def symbol_attachment(model, symbol, index):
    """An exact direct symbol attachment, without an implicit identity support."""
    if model.symbols.get(symbol.key) is not symbol:
        raise ValueError('the TEST symbol origin belongs to another model')
    if type(index) is not int or not 0 <= index < len(symbol.evidence):
        raise ValueError('the TEST symbol origin requires its evidence position')
    if symbol.evidence[index].get('kind') != 'test':
        return None
    return _make('symbol', symbol.key.key,
                 ('symbol', symbol.key.key, 'evidence', index),
                 symbol.evidence[index], _symbol_context(symbol))


def link_attachment(model, link, index):
    """An exact relation attachment, independent of global link-list order."""
    if not any(held is link for held in model.links):
        raise ValueError('the TEST relation origin belongs to another model')
    if type(index) is not int or not 0 <= index < len(link.evidence):
        raise ValueError('the TEST relation origin requires its evidence position')
    if link.evidence[index].get('kind') != 'test':
        return None
    identity = _link_identity(link)
    return _make('link', link.owner.key,
                 ('link', identity, 'evidence', index),
                 link.evidence[index], _link_context(link))


def _walk(kind, owner, value, route, context):
    """Preserve nested evidence positions and their complete enclosing value."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key == 'evidence' and isinstance(child, (list, tuple)):
                for index, evidence in enumerate(child):
                    if isinstance(evidence, dict):
                        found = _make(kind, owner, (*route, key, index), evidence,
                            lambda: {'owner': context() if callable(context) else context,
                                     'enclosing': value})
                        if found is not None:
                            yield found
            else:
                yield from _walk(kind, owner, child, (*route, key), context)
    elif isinstance(value, (list, tuple)):
        for index, child in enumerate(value):
            yield from _walk(kind, owner, child, (*route, index), context)


def occurrences(model):
    """Every owned TEST attachment, with no execution or semantic admission."""
    for symbol in sorted(model.symbols.values(), key=lambda item: item.key):
        for index in range(len(symbol.evidence)):
            found = symbol_attachment(model, symbol, index)
            if found is not None:
                yield found
        yield from _walk('symbol-property', symbol.key.key, symbol.props,
                         ('symbol', symbol.key.key, 'properties'),
                         lambda symbol=symbol: _symbol_context(symbol))
    for meaning in sorted(model.meanings, key=lambda item: item.key):
        state = lambda meaning=meaning: _meaning_state(meaning)
        yield from _walk('meaning', meaning.key, meaning.props,
                         ('meaning', meaning.key, 'properties'), state)
        yield from _walk('meaning-table', meaning.key, meaning.tables,
                         ('meaning', meaning.key, 'tables'), state)
        for layout, status in sorted(meaning.statuses.items()):
            yield from _walk('status', meaning.key,
                             {'evidence': status.evidence, 'properties': status.props},
                             ('status', meaning.key, layout), state)
    for link in model.links:
        for index in range(len(link.evidence)):
            found = link_attachment(model, link, index)
            if found is not None:
                yield found
        yield from _walk('link-property', link.owner.key, link.props,
                         ('link', _link_identity(link), 'properties'),
                         lambda link=link: _link_context(link))
    for entity in sorted(model.entities.values(), key=lambda item: item.key):
        state = {'entity': entity.key, 'properties': entity.props,
                 'references': entity.refs, 'steps': entity.steps, 'sources': entity.sources}
        yield from _walk('entity', entity.key, entity.props,
                         ('entity', entity.key, 'properties'), state)
        yield from _walk('entity-step', entity.key, entity.steps,
                         ('entity', entity.key, 'steps'), state)
    for key, target in sorted(model.targets.items()):
        owner = f'{target.feature}/{target.layout}'
        state = {'feature': target.feature, 'layout': target.layout,
                 'status': target.status, 'properties': target.props, 'sources': target.sources}
        yield from _walk('target', owner, target.props, ('target', key), state)


def index(model):
    """An immutable-origin index that refuses an ambiguous attachment key."""
    found = {}
    for origin in occurrences(model):
        if origin.key in found:
            raise ValueError('duplicate TEST owning-origin identity')
        found[origin.key] = origin
    return found


def rebind(model, origin):
    """Resolve the exact current attachment without reconstructing its item."""
    if not isinstance(origin, Origin):
        raise ValueError('TEST qualification requires its explicit owning origin')
    held = _resolve(model, json.loads(origin.locator_text))
    if held is None or not exact(held.packet(), origin.packet()):
        raise ValueError('the TEST owning attachment or semantic context changed')
    return held


def current(model, origin, evidence):
    """Rebind a supplied origin to current native values before admission."""
    held = rebind(model, origin)
    if held.evidence_text != _snapshot(evidence):
        raise ValueError('the TEST evidence belongs to another owning attachment')
    return held


@dataclass(frozen=True)
class Unavailable:
    reason: str


def capture(model, route):
    """Keep failed owning-context capture distinct from an absent request."""
    try:
        origin = _resolve(model, json.loads(json_text(route)))
        if origin is not None:
            return origin
    except (ValueError, TypeError, KeyError, AttributeError, IndexError, RecursionError):
        pass
    return Unavailable('the TEST owning attachment has no complete current context')


def symbol_route(symbol, index):
    return ('symbol', symbol.key.key, 'evidence', index)


def link_route(link, index):
    return ('link', _link_identity(link), 'evidence', index)


def _meaning(model, key):
    found = [meaning for meaning in model.meanings if meaning.key == key]
    if len(found) != 1:
        raise ValueError('the TEST origin requires one current owning meaning')
    return found[0]


def _nested(kind, owner, route, value, path, context):
    if len(path) < 2 or path[-2] != 'evidence' or type(path[-1]) is not int:
        raise ValueError('the TEST origin has no exact nested evidence position')
    for part in path[:-2]:
        if isinstance(value, dict) and type(part) is str and part in value:
            value = value[part]
        elif isinstance(value, (list, tuple)) and type(part) is int and 0 <= part < len(value):
            value = value[part]
        else:
            raise ValueError('the nested TEST owning context changed')
    if not isinstance(value, dict) or not isinstance(value.get('evidence'), (list, tuple)):
        raise ValueError('the nested TEST owner has no evidence list')
    index_ = path[-1]
    if not 0 <= index_ < len(value['evidence']):
        raise ValueError('the nested TEST attachment was removed')
    return _make(kind, owner, route, value['evidence'][index_],
                 {'owner': context, 'enclosing': value})


def _resolve(model, route):
    """Resolve one current owner; do not resnapshot the entire TEST inventory."""
    if type(route) is not list or len(route) < 3:
        raise ValueError('the TEST origin has no complete owning route')
    category, owner = route[:2]
    if category == 'symbol':
        match = SYMBOL_KEY.fullmatch(owner) if type(owner) is str else None
        if match is None:
            raise ValueError('the TEST origin has another symbol identity')
        symbol = model.symbols.get(SymbolKey(match[1], match[3], int(match[2], 16)))
        if symbol is None:
            raise ValueError('the TEST symbol origin was removed')
        if route[2] == 'evidence' and len(route) == 4:
            return symbol_attachment(model, symbol, route[3])
        if route[2] == 'properties':
            return _nested('symbol-property', owner, route, symbol.props, route[3:],
                           _symbol_context(symbol))
    elif category == 'meaning':
        meaning = _meaning(model, owner)
        if route[2] in ('properties', 'tables'):
            value = meaning.props if route[2] == 'properties' else meaning.tables
            kind = 'meaning' if route[2] == 'properties' else 'meaning-table'
            return _nested(kind, owner, route, value, route[3:], _meaning_state(meaning))
    elif category == 'link':
        if type(owner) is not dict or set(owner) != {'owner', 'type', 'to', 'slot', 'offset'}:
            raise ValueError('the TEST relation origin has another identity')
        meaning = _meaning(model, owner['owner'])
        found = [link for link in meaning.links if exact(_link_identity(link), owner)
                 and any(held is link for held in model.links)]
        if len(found) != 1:
            raise ValueError('the TEST origin requires one current owning relation')
        link = found[0]
        if route[2] == 'evidence' and len(route) == 4:
            return link_attachment(model, link, route[3])
        if route[2] == 'properties':
            return _nested('link-property', link.owner.key, route, link.props, route[3:],
                           _link_context(link))
    elif category == 'status':
        meaning = _meaning(model, owner)
        status = meaning.statuses.get(route[2])
        if status is None:
            raise ValueError('the TEST status origin was removed')
        value = {'evidence': status.evidence, 'properties': status.props}
        return _nested('status', owner, route, value, route[3:], _meaning_state(meaning))
    elif category == 'entity':
        if type(owner) is not str or '/' not in owner:
            raise ValueError('the TEST entity origin has another identity')
        slug, kind = owner.rsplit('/', 1)
        entity = model.entities.get((kind, slug))
        if entity is None:
            raise ValueError('the TEST entity origin was removed')
        state = {'entity': entity.key, 'properties': entity.props,
                 'references': entity.refs, 'steps': entity.steps, 'sources': entity.sources}
        if route[2] in ('properties', 'steps'):
            value = entity.props if route[2] == 'properties' else entity.steps
            category = 'entity' if route[2] == 'properties' else 'entity-step'
            return _nested(category, owner, route, value, route[3:], state)
    elif category == 'target':
        if type(owner) is not list:
            raise ValueError('the TEST target origin has another identity')
        target = model.targets.get(tuple(owner))
        if target is None:
            raise ValueError('the TEST feature target origin was removed')
        state = {'feature': target.feature, 'layout': target.layout,
                 'status': target.status, 'properties': target.props, 'sources': target.sources}
        return _nested('target', f'{target.feature}/{target.layout}', route, target.props,
                       route[2:], state)
    raise ValueError('the TEST origin has an unsupported owning route')
