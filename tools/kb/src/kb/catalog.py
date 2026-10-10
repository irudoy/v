"""Source-bound parity features, with explicit unresolved ECU requirements."""

from collections import defaultdict
import csv
import hashlib
import json
from pathlib import Path
import re

from kb import repo, store, write
from kb.answer import Answer, DETAIL, FACTS, IDENTITY
from kb.model import Issue
from kb.repo import KbError

PATH = Path('refs/vendor/catalog.csv')
COLUMNS = ('vendor', 'doc', 'section', 'group', 'name', 'dims', 'axis_x', 'axis_y',
           'output', 'origin', 'level', 'concept', 'source', 'note')
IDENTITY_KEYS = ('vendor', 'doc', 'section', 'group', 'name')


def exact(row):
    return json.dumps(row, sort_keys=True, ensure_ascii=False, separators=(',', ':'))


def digest(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def rows(root=repo.ROOT):
    with (root / PATH).open(newline='', encoding='utf-8') as source:
        reader = csv.DictReader(source)
        if tuple(reader.fieldnames or ()) != COLUMNS:
            raise KbError(f'{PATH}: unexpected catalog columns', code=3)
        found = list(reader)
    if any(set(row) != set(COLUMNS) or any(not isinstance(value, str)
                                         for value in row.values()) for row in found):
        raise KbError(f'{PATH}: malformed catalog row', code=3)
    return found


def documents(inventory, layouts):
    """Group only declared concepts; unrelated rows retain separate identities."""
    groups = defaultdict(list)
    identities = set()
    for order, row in enumerate(inventory):
        identity = exact({key: row[key] for key in IDENTITY_KEYS})
        if identity in identities:
            raise KbError('catalog contains duplicate entry identities', code=3)
        identities.add(identity)
        concept = row['concept']
        slug = 'parity_' + (concept.replace('-', '_') if concept else digest(identity)[:16])
        if not re.fullmatch(r'[a-z][a-z0-9]*(_[a-z0-9]+)*', slug) or len(slug) > 48:
            raise KbError(f'catalog concept has no valid feature slug: {concept!r}', code=3)
        if groups[slug] and groups[slug][0][0]['concept'] != concept:
            raise KbError(f'distinct catalog concepts collide at {slug}', code=3)
        original = exact(row)
        groups[slug].append((row, {'order': order, 'source': PATH.as_posix(),
                                   'sha256': digest(original), 'original': original}))
    output = {}
    for slug, entries in sorted(groups.items()):
        row = entries[0][0]
        title = row['concept'].replace('-', ' ').capitalize() if row['concept'] else row['name']
        output[slug] = {
            'title': title,
            'summary': 'Competitor inventory: ' + '; '.join(entry['name'] for entry, _ in entries) + '.',
            'acceptance': (
                'Every listed catalog item has explicit ECU meaning bindings and a reviewed '
                'mechanism. Bench or vehicle observations reproduce its documented behavior, '
                'including the named input axes and output quantities where the source states them.'),
            'requirements_state': 'unresolved',
            'vendor': sorted({entry['vendor'] for entry, _ in entries}),
            'catalog': [marker for _, marker in entries],
            'target': [dict(layout=layout, status='planned',
                            note='ECU requirements and behavior evidence are unresolved.')
                       for layout in sorted(layouts)],
        }
    return output


def plan(model, root=repo.ROOT):
    """Prepare new source-bound features through the primary document writer."""
    change = write.Change(model, None, root)
    for slug, expected in documents(rows(root), model.layouts).items():
        path, document = change.designed('feature', slug)
        if document:
            if document.get('catalog') != expected['catalog']:
                raise KbError(f'{path}: catalog identity changes need an explicit owner edit', code=3)
        else:
            document.update(expected)
    return change.texts()


def check(model, inventory=None):
    """Every exact source row belongs to one feature with a target per layout."""
    inventory = rows(model.root) if inventory is None else inventory
    selected, issues = {}, []
    for (kind, slug), feature in model.entities.items():
        markers = feature.props.get('catalog') if kind == 'feature' else None
        if markers is None:
            continue
        path, subject = store.path_of('feature', slug).as_posix(), feature.key
        def refuse(message):
            issues.append(Issue('catalog', path, subject, message))
        if not feature.props.get('acceptance') or not feature.props.get('vendor'):
            refuse('catalog feature lacks acceptance or vendor products')
        state = feature.props.get('requirements_state')
        if state not in ('unresolved', 'bound'):
            refuse('catalog requirements_state must be unresolved or bound')
        if state == 'bound' and not feature.refs.get('requires'):
            refuse('bound catalog requirements need explicit ECU references')
        if {layout for (owner, layout) in model.targets if owner == slug} != set(model.layouts):
            refuse('catalog feature needs an explicit target on every project layout')
        if not isinstance(markers, list) or any(not isinstance(marker, dict) for marker in markers):
            refuse('catalog must be an array of source selectors')
            continue
        for marker in markers:
            order = marker.get('order')
            if (type(order) is not int or not 0 <= order < len(inventory)
                    or order in selected):
                refuse('catalog row selector is invalid or duplicated')
                continue
            selected[order] = subject
            original = marker.get('original', '')
            if (marker.get('source') != PATH.as_posix()
                    or not isinstance(original, str)
                    or original != exact(inventory[order])
                    or marker.get('sha256') != digest(original)):
                refuse(f'catalog row {order} differs from its exact source')
    missing = sorted(set(range(len(inventory))) - set(selected))
    if missing:
        issues.append(Issue('catalog', PATH.as_posix(), 'parity catalog',
                            f'{len(missing)} source entries have no feature owner'))
    return issues


def report(model, layout=None):
    """Catalog and project features, acceptance and explicit status on every layout."""
    if layout is not None and layout not in model.layouts:
        raise KbError(f'no layout {layout}', code=2)
    answer = Answer('kb gaps --catalog --json')
    features = []
    for (kind, slug), entity in sorted(model.entities.items()):
        if kind != 'feature':
            continue
        props = entity.props
        targets = {name: model.targets.get((slug, name))
                   for name in model.layouts if layout is None or layout == name}
        features.append(dict(feature=entity.key, title=props.get('title', slug),
                             acceptance=props.get('acceptance', ''), specs=props.get('specs', []),
                             vendor=props.get('vendor', []), entries=len(props.get('catalog', [])),
                             requirements_state=props.get('requirements_state', 'project'),
                             requires=sorted(str(ref) for ref in entity.refs.get('requires', [])),
                             targets={name: target.status if target else 'no target'
                                      for name, target in targets.items()}))
    answer.section(None, IDENTITY, [f'Parity catalog: {len(features)} features; '
                                    f'{sum(item["entries"] for item in features)} competitor entries'])
    for feature in features:
        targets = ', '.join(f'{name} {state}' for name, state in feature['targets'].items())
        answer.section(None, FACTS, [f'{feature["feature"]}: {targets}; '
                                     f'requirements {feature["requirements_state"]}'])
        answer.section(None, DETAIL, [f'  acceptance: {feature["acceptance"] or ", ".join(feature["specs"])}'])
    answer.data = {'features': features,
                   'unresolved_requirements': sum(item['requirements_state'] == 'unresolved'
                                                  for item in features)}
    return answer
