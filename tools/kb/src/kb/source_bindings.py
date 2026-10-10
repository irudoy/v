"""Lossless source bindings for the documented JK78C VVEL and CAN model.

Typed function anchors and explicitly selected RAM roles become owned symbols.
Source prose remains a narrow specification. A source binding is provenance,
not evidence of a claim level or of executable behavior.
"""

from collections import defaultdict
import hashlib
from pathlib import Path
import re

from kb import match, repo, store, write
from kb.model import Issue, SymbolKey
from kb.repo import KbError

PATHS = (Path('defs/JK78C.vvel.md'), Path('defs/JK78C.can.md'))
FUNCTION = re.compile(r'\bFUN_([0-9a-fA-F]{8})\b')
FUNCTION_LAYOUTS = {
    'defs/JK78C.vvel.md': {
        0x0004c4b8: '1nd', 0x00050310: '1me3b',
        0x0007448c: '1me3b', 0x00070514: '1nd',
    },
}
ROLES = {
    'defs/JK78C.vvel.md': {
        0xffffa22f: ('ram', 'mode byte'),
        0xffff44aa: ('ram', 'command word'),
        0xffff443e: ('ram', 'latched command word'),
        0xffff2670: ('ram', 'shaft angle input'),
        0xffff2672: ('ram', 'shaft angle input'),
    },
    'defs/JK78C.can.md': {
        0xffff3d33: ('ram', 'HCAN1 shadow base'),
        0xffff3e5f: ('ram', 'HCAN0 shadow base'),
        0xffff41ac: ('ram', 'received frame word'),
        0xffff41ae: ('ram', 'received frame word'),
    },
}


def records(root=repo.ROOT):
    """Explicit typed anchors, grouped without matching or joining meanings."""
    found = defaultdict(list)
    for path in PATHS:
        data = (root / path).read_bytes()
        text = data.decode('utf-8')
        sha256 = hashlib.sha256(data).hexdigest()
        section, functions = 'Introduction', defaultdict(set)
        for line in text.splitlines():
            if line.startswith('## '):
                section = line[3:].strip()
            for address in FUNCTION.findall(line):
                functions[int(address, 16)].add(section)
        for address, sections in functions.items():
            layout = FUNCTION_LAYOUTS.get(path.as_posix(), {}).get(address, 'jk78c')
            found[SymbolKey(layout, 'fn', address)].append(dict(layout=layout,
                path=path.as_posix(), sha256=sha256, sections=sorted(sections),
                anchor=f'FUN_{address:08X}'))
        for address, (kind, role) in ROLES[path.as_posix()].items():
            if f'{address:08x}' not in text.lower():
                raise KbError(f'{path}: selected role {address:08x} lacks its source anchor', code=3)
            found[SymbolKey('jk78c', kind, address)].append(dict(
                layout='jk78c', path=path.as_posix(), sha256=sha256,
                anchor=f'0x{address:08X}', role=role))
    return {key: sorted(items, key=lambda item: (item['path'], item['anchor']))
            for key, items in found.items()}


def plan(model, root=repo.ROOT):
    change = write.Change(model, write.model_resolver(model), root)
    for key, sources in sorted(records(root).items()):
        symbol = model.symbols.get(key)
        if symbol is None:
            if key.kind == 'fn':
                if key.address not in model.functions[key.layout]:
                    continue
                evidence = dict(kind='l0', supports='identity', at=key.location)
            else:
                from kb.model import Symbol
                temporary = Symbol(key)
                evidence = next((item for site in match.referencing(model, temporary)
                    for item in [dict(kind='l0', supports='identity', at=f'jk78c:{site:08x}')]
                    if match.verify(model, temporary, item) is None), None)
                if evidence is None:
                    raise KbError(f'{key.location}: selected source role lacks verified L0 identity', code=3)
            change.new(dict(kind=key.kind, symbol=key.location, evidence=[evidence]))
            meaning, _ = change.resolve(key.location)
        else:
            meaning = symbol.meaning
        _, document = change.document(meaning)
        held = document.setdefault('source', [])
        for item in sources:
            if item not in held:
                held.append(item)
    return change.texts()


def missing(model):
    """Source function anchors without an exported entry remain unresolved."""
    selected = [(key, items) for key, items in records(model.root).items()
                if key.kind == 'fn' and key.address not in model.functions[key.layout]]
    if not selected:
        return []
    digests = {key.layout: match.l0_digest(key.layout, model.root) for key, _ in selected}
    return [dict(location=key.location, kind=key.kind, sources=items, l0=digests[key.layout],
                 state='unresolved', reason='The documented function anchor has no entry in normalized L0.')
            for key, items in sorted(selected)]


def check(model):
    actual = defaultdict(list)
    for meaning in model.meanings:
        sources = meaning.tables.get('source', ())
        for item in sources:
            if item.get('path') not in {path.as_posix() for path in PATHS}:
                continue
            symbol = meaning.symbols.get(item.get('layout'))
            if symbol is not None:
                actual[symbol.key].append(item)
    if not actual and not model.config.get('source_bindings', {}).get('enabled'):
        return []
    expected = records(model.root)
    issues = []
    held = model.config.get('source_bindings', {}).get('review', [])
    absent = missing(model)
    if held != absent:
        issues.append(Issue('source-bindings', repo.OWNER_CONFIG.as_posix(), 'unresolved anchors',
                            'the source-bound missing-function inventory differs from current L0'))
    for item in absent:
        layout, address = item['location'].split(':')
        expected.pop(SymbolKey(layout, item['kind'], int(address, 16)))
    for key in sorted(set(actual) | set(expected)):
        if sorted(actual.get(key, []), key=lambda item: item['path']) != sorted(
                expected.get(key, []), key=lambda item: item['path']):
            issues.append(Issue('source-bindings', 'defs/JK78C.vvel.md;defs/JK78C.can.md',
                                key.key, 'the typed source anchors differ from their exact owned bindings'))
    return issues
