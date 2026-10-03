"""The architecture registry view of owned entities and meaning placements.

Entity order preserves the original block voting and display order. Addresses
are projections of references on the home layout, never separate facts.
"""

from copy import deepcopy
import tomllib

from kb import compile, repo, store
from kb.adapters import architecture
from kb.model import SymbolKey
from kb.repo import KbError

SUMMARY = ('Hitachi SH7058 engine control of the VQ25HR: sensor capture, engine-state '
           'estimation, control calculations, protection, and ATU-II actuator output, '
           'with diagnostic, communication, and platform support lanes.')
SOURCES = {'functions': 'defs/JK08A.funcs.csv', 'variables': 'defs/JK08A.vars.csv',
           'findings': 'defs/JK08A.findings.csv', 'maps': 'defs/JK08A.maps.csv',
           'axes': 'defs/JK08A.axes.csv', 'presentation': 'defs/JK08A.overrides.toml'}
HEADER = ('# Functional architecture of the exact JK08A family.\n'
          '# Generated from architecture entities and meaning placements by kb project.\n')


def identifier(reference):
    if isinstance(reference, tuple):
        return reference[1].replace('_', '-')
    return reference.split('/')[0].replace('_', '-')


def address(model, reference, kinds=architecture.CHAIN_KINDS):
    """An exact home symbol, with a kind prefix only to resolve ambiguity."""
    if not isinstance(reference, SymbolKey):
        meaning = next((item for item in model.meanings if item.key == reference), None)
        symbol = meaning.symbols.get(architecture.CANONICAL) if meaning else None
    else:
        symbol = model.symbols.get(reference)
    if symbol is None or symbol.layout != architecture.CANONICAL:
        raise KbError(f'architecture reference {reference!r} has no {architecture.CANONICAL} '
                      'symbol', code=3)
    present = {key.kind for key in model.symbols
               if key.layout == symbol.layout and key.address == symbol.address}
    first = next((kind for kind in kinds if kind in present), None)
    if first == symbol.kind:
        return f'{symbol.address:08x}'
    prefix = next((prefix for prefix, kind in architecture.PREFIXES.items()
                   if kind == symbol.kind), None)
    if prefix is None:
        raise KbError(f'architecture reference {reference!r} cannot select its kind', code=3)
    return f'{prefix}:{symbol.address:08x}'


def document(model):
    found = {'schema_version': architecture.SCHEMA_VERSION, 'rom': 'JK08A',
             'summary': SUMMARY, 'sources': dict(SOURCES)}
    for kind in ('stage', 'block', 'endpoint', 'chain'):
        entities = sorted((item for item in model.entities.values() if item.kind == kind),
                          key=lambda item: (item.props.get('order', 0), item.slug))
        rows = []
        for entity in entities:
            row = {'id': identifier((kind, entity.slug)), 'name': entity.props.get('title')}
            row.update({key: value for key, value in entity.props.items()
                        if key not in ('title', 'home', 'order') and value is not None})
            for field, refs in entity.refs.items():
                if field in ('stage', 'block'):
                    if len(refs) != 1:
                        raise KbError(f'{entity.key}: no unique {field}', code=3)
                    row[field] = identifier(refs[0])
                elif field == 'output':
                    if len(refs) != 1:
                        raise KbError(f'{entity.key}: no unique output', code=3)
                    row[field] = address(model, refs[0])
                else:
                    kinds = ('fn',) if field == 'functions' else ('reg', 'ram')
                    row[field] = [address(model, ref, kinds) for ref in refs]
            if kind == 'block':
                for field, kinds in architecture.BLOCK_LISTS.items():
                    row[field] = sorted({address(model, symbol.key, kinds)
                        for meaning in model.meanings
                        if meaning.props.get('block') == entity.key and meaning.kind in kinds
                        for symbol in [meaning.symbols.get(architecture.CANONICAL)]
                        if symbol is not None})
            if kind == 'chain':
                row['step'] = [{**{key: value for key, value in step.items()
                                  if key not in ('from', 'to', 'via') and value is not None},
                                'from': address(model, step['from']),
                                'to': address(model, step['to']),
                                **({'via': [address(model, ref, ('fn',))
                                            for ref in step['via']]} if step.get('via') else {})}
                               for step in entity.steps]
            rows.append(row)
        found[kind] = rows
    return found


def render(document):
    """Canonical TOML with ordered arrays and explicit empty block lists."""
    lines = [HEADER.rstrip()]

    def fields(item, keys):
        for key in keys:
            if key in item and item[key] is not None:
                lines.extend(store._assignment(key, item[key], store.PLAIN))

    fields(document, ('schema_version', 'rom', 'summary'))
    lines.extend(('', '[sources]'))
    fields(document['sources'], tuple(SOURCES))
    keys = {'stage': ('id', 'name', 'lane', 'summary'),
            'block': ('id', 'name', 'stage', 'summary', 'specs', 'generic', 'functions',
                      'maps', 'signals'),
            'endpoint': ('id', 'name', 'direction', 'block', 'peripheral', 'summary',
                         'registers', 'functions', 'specs'),
            'chain': ('id', 'name', 'summary', 'quantity', 'output', 'specs')}
    for kind, ordered in keys.items():
        for item in document.get(kind, ()):
            lines.extend(('', f'[[{kind}]]'))
            fields(item, ordered)
            if kind == 'chain':
                for step in item.get('step', ()):
                    lines.extend(('', '[[chain.step]]'))
                    fields(step, ('from', 'to', 'effect', 'sign', 'via', 'note', 'specs'))
    return '\n'.join(lines) + '\n'


def registry(root=repo.ROOT):
    return render(document(compile.cached(root)))


def comparable(document, model):
    """Nonsemantic ordering and omitted empty lists do not change a view."""
    found = deepcopy(document)
    at = {}
    for key in model.symbols:
        if key.layout == architecture.CANONICAL:
            at.setdefault(key.address, set()).add(key.kind)

    def reference(text, kinds):
        match = architecture.REFERENCE.fullmatch(text if isinstance(text, str) else '')
        if match is None:
            raise KbError(f'architecture reference {text!r} is invalid', code=3)
        address = int(match[2], 16)
        kind = (architecture.PREFIXES[match[1]] if match[1] else
                next((kind for kind in kinds if kind in at.get(address, ())), None))
        if kind not in kinds or kind not in at.get(address, ()):
            raise KbError(f'architecture reference {text!r} names no permitted symbol', code=3)
        return kind, f'{address:08x}'

    for kind in ('block', 'endpoint', 'chain'):
        for row in found.get(kind, ()):
            if kind == 'block':
                row.setdefault('generic', False)
                for field, kinds in architecture.BLOCK_LISTS.items():
                    row[field] = sorted(reference(text, kinds) for text in row.get(field, []))
            if kind == 'endpoint':
                for field in ('registers', 'functions'):
                    kinds = ('reg', 'ram') if field == 'registers' else ('fn',)
                    row[field] = sorted(reference(text, kinds) for text in row.get(field, []))
            for field in ('specs',):
                row.setdefault(field, [])
            if kind == 'chain':
                row['output'] = reference(row['output'], architecture.CHAIN_KINDS)
                for step in row.get('step', ()):
                    for field in ('via', 'specs'):
                        step.setdefault(field, [])
                    for field in ('from', 'to'):
                        step[field] = reference(step[field], architecture.CHAIN_KINDS)
                    step['via'] = [reference(text, ('fn',)) for text in step['via']]
                    if step.get('note') is None:
                        step.pop('note', None)
    return found


def validate_conversion(original, generated, model):
    before, after = (comparable(tomllib.loads(text), model) for text in (original, generated))
    if before != after:
        kinds = [kind for kind in sorted(set(before) | set(after))
                 if before.get(kind) != after.get(kind)]
        raise KbError(f'{architecture.ARCHITECTURE.as_posix()}: conversion changes '
                      f'architecture facts in {kinds}; nothing is written', code=3)
