"""Source-bound access differences retained as explicit unresolved claims.

Review records never verify a relation, raise a claim level, or suppress a
new difference. They bind one exact difference and the normalized L0 digest.
"""

from collections import defaultdict
from functools import lru_cache
import hashlib
import json

from kb import graph, l0graph, match, repo
from kb.model import Issue


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                     separators=(',', ':'), default=str).encode()).hexdigest()


@lru_cache(maxsize=24)
def accesses(layout, spaces, root, source_digest):
    rows = l0graph.l0_rows(layout, dict(spaces), root)
    found, locations = defaultdict(list), defaultdict(list)
    for row in rows['accesses']:
        found[(row['from'], row['to'])].extend(row['props']['sites'])
        locations[row['to']].extend((row['from'], site) for site in row['props']['sites'])
    return dict(found), dict(locations)


def access_claims(model):
    """Eligible declared accesses, including those reproduced by L0."""
    for link in model.links:
        if graph.L0_VERIFIED.get(link.type.upper()) is None:
            continue
        allowed = link.props.get('layouts')
        for layout in sorted(set(link.owner.symbols) & set(link.to.symbols)):
            if allowed and layout not in allowed:
                continue
            claim = dict(owner=link.owner.key, to=link.to.key, type=link.type,
                         layout=layout, slot=link.slot, offset=link.offset,
                         roles=sorted(link.roles), props=link.props, evidence=link.evidence,
                         stated=sorted(link.stated), sources=sorted(link.sources))
            yield link.owner.symbols[layout], link.to.symbols[layout], claim


def claim_identity(claim):
    return tuple(claim[key] for key in ('owner', 'to', 'type', 'layout', 'slot', 'offset'))


def difference_key(item):
    return item['kind'], item['subject'], item['claim_sha256']


def differences(model):
    """Exact missing accesses and storage-width contradictions of the model."""
    indices, digests = {}, {}
    def index(layout):
        if layout not in indices:
            source_digest = match.l0_digest(layout, model.root)
            digests[layout] = source_digest
            indices[layout] = accesses(model.layouts[layout],
                tuple(sorted(model.spaces[model.layouts[layout].mcu].items())),
                model.root, source_digest)
        return indices[layout]
    found = []
    for storage, function, claim in access_claims(model):
        layout = claim['layout']
        modes = graph.L0_VERIFIED[claim['type'].upper()]
        actual = index(layout)[0].get((function.key.location, storage.key.location), ())
        if any(site['mode'] in modes for site in actual):
            continue
        found.append(dict(kind='access', subject=storage.key.key, layout=layout,
            claim_sha256=digest(claim), l0=digests[layout],
            detail=f'{claim["type"]} {storage.key.key} -> {function.key.key}: no matching '
                   'normalized L0 access; the original claim remains unresolved',
            sources=claim['sources']))
    for symbol in model.symbols.values():
        bits = symbol.value('width')
        if symbol.kind not in ('ram', 'reg') or type(bits) is not int:
            continue
        observed = sorted({(function, site['site'], site['mode'], site['width'])
            for function, site in index(symbol.layout)[1].get(symbol.key.location, ())
            if site['mode'] in l0graph.RAM_ACCESS_MODES
            and type(site.get('width')) is int and site['width'] * 8 > bits})
        if observed:
            claim = dict(symbol=symbol.key.key, width=bits, observed=observed)
            found.append(dict(kind='width', subject=symbol.key.key, layout=symbol.layout,
                claim_sha256=digest(claim), l0=digests[symbol.layout],
                detail=f'{symbol.key.key}: declared {bits} bits; normalized L0 includes '
                       f'wider accesses of {sorted({item[3] * 8 for item in observed})} bits',
                sources=sorted(symbol.sources)))
    return sorted(found, key=lambda item: (item['kind'], item['subject'], item['claim_sha256']))


def reviews(model):
    """An exact unresolved inventory for the primary consolidated transfer."""
    return [{**item, 'state': 'unresolved', 'reason': item['detail']} for item in differences(model)]


def rebase(before, after, renames):
    """Rebind exact renamed claims or withdraw reviews of deleted access claims.

    New differences and changed conditions, evidence, widths or L0 never gain
    a review. Every retained record keeps its state and reason.
    """
    configured = before.config.get('reconciliation', {})
    if not configured.get('enabled'):
        return None
    from kb import store, write
    import tomlkit
    path = before.root / repo.OWNER_CONFIG
    if repo.OWNER_CONFIG in before.overlay:
        text = before.overlay[repo.OWNER_CONFIG]
    elif path.is_file():
        text = path.read_text(encoding='utf-8')
    else:
        return None
    if text is None:
        return None
    original = {difference_key(item): item for item in differences(before)}
    current = {difference_key(item): item for item in differences(after)}
    claims = {('access', storage.key.key, digest(claim)): claim
              for storage, _, claim in access_claims(before)}
    remaining = {claim_identity(claim) for _, _, claim in access_claims(after)}
    owners = {meaning.key: meaning for meaning in before.meanings}
    paths = {store.path_of(old.split('/')[1], old.split('/')[0]).as_posix():
             store.path_of(new.split('/')[1], new.split('/')[0]).as_posix()
             for old, new in renames.items()}

    def renamed_claim(claim):
        for old, new in renames.items():
            owner = owners[old]
            aliases = {owner.name, *(symbol.generated for symbol in owner.symbols.values())} - {None}
            claim, _ = write.renamed(claim, aliases, owner.kind, new.split('/')[0])
        return {**claim, 'sources': sorted(paths.get(item, item) for item in claim['sources'])}

    found, changed = [], False
    for record in configured.get('review', ()):
        if not isinstance(record, dict) or not all(key in record for key in
                                                 ('kind', 'subject', 'claim_sha256')):
            found.append(record)
            continue
        key = difference_key(record)
        item = original.get(key)
        if (item is None or set(record) != set(item) | {'state', 'reason'}
                or record.get('state') != 'unresolved'
                or not isinstance(record.get('reason'), str) or not record['reason'].strip()
                or any(record.get(name) != value for name, value in item.items())):
            found.append(record)
            continue
        expected = {**item, 'sources': sorted(paths.get(src, src) for src in item['sources'])}
        claim = renamed_claim(claims[key]) if key in claims else None
        if claim is not None:
            expected['claim_sha256'] = digest(claim)
        candidate = current.get(difference_key(expected))
        if candidate == expected:
            updated = {**record, **candidate}
            found.append(updated)
            changed |= updated != record
        elif claim is not None and claim_identity(claim) not in remaining:
            changed = True
        else:
            found.append(record)
    if not changed:
        return None
    document = tomlkit.parse(text)
    document['reconciliation']['review'] = found
    return tomlkit.dumps(document)


def check(model):
    configured = model.config.get('reconciliation', {})
    if not configured.get('enabled'):
        return []
    actual = {(item['kind'], item['subject'], item['claim_sha256']): item
              for item in differences(model)}
    held, issues = {}, []
    for item in configured.get('review', ()):
        if (not isinstance(item, dict) or set(item) != {
                'kind', 'subject', 'layout', 'claim_sha256', 'l0', 'detail', 'sources',
                'state', 'reason'} or item.get('state') != 'unresolved'
                or not isinstance(item.get('reason'), str) or not item['reason'].strip()):
            issues.append(Issue('code', repo.OWNER_CONFIG.as_posix(), 'review',
                                'an exception needs exact source binding and an unresolved reason'))
            continue
        key = (item['kind'], item['subject'], item['claim_sha256'])
        if key in held:
            issues.append(Issue('code', repo.OWNER_CONFIG.as_posix(), item['subject'],
                                'duplicate source-bound review'))
        held[key] = item
    for key, item in actual.items():
        record = held.get(key)
        if record is None:
            issues.append(Issue('code', ';'.join(item['sources']), item['subject'], item['detail']))
        elif any(record.get(name) != value for name, value in item.items()):
            issues.append(Issue('code', repo.OWNER_CONFIG.as_posix(), item['subject'],
                                'the unresolved review differs from its current claim or L0'))
    for key in held.keys() - actual.keys():
        issues.append(Issue('code', repo.OWNER_CONFIG.as_posix(), key[1],
                            'the source-bound difference no longer reproduces'))
    return issues
