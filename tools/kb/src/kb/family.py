"""Primary family onboarding with comment-preserving TOML and stock gates."""

import hashlib
from pathlib import Path
import re
import tomllib

import tomlkit

from kb import compile, graph, l0, lock, publication, repo, store, vocab, write
from kb.repo import KbError

REPORT = re.compile(r'(?P<source>[A-Z0-9]+)-(?P<target>[A-Z0-9]+)\.census-correspondence\.csv')
IDENTIFIER = re.compile(r'[a-z][a-z0-9_]{2,63}')
LAYOUT = re.compile(r'[0-9a-z]{2,8}')


def prepared(text, operation, *, image, layout, family_id, evidence, metadata=None):
    """Change only the selected family, preserving every unrelated TOML byte."""
    document = tomlkit.parse(text)
    before = tomllib.loads(text)
    if not IDENTIFIER.fullmatch(family_id):
        raise KbError('family id must be a stable lowercase identifier', code=2)
    families = document['family']
    occupied = {member for row in families.values() for member in row['members']}
    if image in occupied:
        raise KbError(f'{image} already belongs to a family', code=3)
    if operation == 'new':
        if layout is None:
            raise KbError('a new family needs a layout id', code=2)
        if family_id in families:
            raise KbError(f'family {family_id} exists', code=3)
        if metadata is None:
            raise KbError('new family needs explicit MCU and identity metadata', code=2)
        row = tomlkit.table()
        row.update({**metadata, 'members': [image], 'canonical': image,
                    'same_address_inheritance': metadata['kind'] == 'exact-code',
                    'layouts': {layout: image}, 'evidence': evidence})
        families.add(family_id, row)
    elif operation == 'add':
        if family_id not in families:
            raise KbError(f'no family {family_id}', code=5)
        row = families[family_id]
        row['members'].append(image)
        if row['same_address_inheritance']:
            if layout is not None:
                raise KbError('exact-code inheritance keeps the existing layout', code=2)
        else:
            if layout is None:
                raise KbError('a non-inheriting family needs a new layout', code=2)
            row['layouts'][layout] = image
        row['evidence'] = str(row['evidence']) + ' ' + evidence
    else:
        raise KbError('family operation must be new or add', code=2)
    layouts = [key for row in families.values() for key in row['layouts']]
    if (any(not LAYOUT.fullmatch(key) or key in vocab.KINDS for key in layouts)
            or len(layouts) != len(set(layouts))):
        raise KbError('layout ids must be valid, globally unique and disjoint from kinds', code=3)
    result = tomlkit.dumps(document)
    after = tomllib.loads(result)
    expected = {**before, 'family': {**before['family'], family_id: after['family'][family_id]}}
    if after != expected:
        raise KbError('family writer changes unrelated facts', code=3)
    return result


def census(path, image, root=repo.ROOT):
    """Validate the declared stock-bound census through its tracked implementation."""
    from tools import census_homology
    path = Path(path).resolve()
    if not path.is_relative_to(root / 'defs') or not path.is_file():
        raise KbError('family census must be a declared report under defs/', code=2)
    identity = REPORT.fullmatch(path.name)
    if identity is None or identity['target'] != image:
        raise KbError('census filename does not bind the requested target image', code=3)
    registered = repo.images(root)
    source = identity['source']
    if source == image or source not in registered or image not in registered:
        raise KbError('census needs distinct registered source and target images', code=3)
    images = (registered[source].path.read_bytes(), registered[image].path.read_bytes())
    for name, data in zip((source, image), images):
        if hashlib.sha256(data).hexdigest() != registered[name].sha256:
            raise KbError(f'{name}: stock bytes differ from the image catalog', code=3)
    rows = census_homology.read_ledger(path)
    census_homology.validate_ledger(rows, source, image, images)
    return f'Census {path.relative_to(root).as_posix()} SHA-256 {repo.sha256_file(path)}.'


def apply(operation, family_id, image, layout, report, metadata=None, *, root=repo.ROOT,
          dry_run=False, log=print):
    """Prepare registry and report, publish both through synchronization."""
    from tools import rom_homology
    try:
        return _apply(operation, family_id, image, layout, report, metadata,
                      root=root, dry_run=dry_run, log=log)
    except rom_homology.HomologyError as error:
        raise KbError(str(error), code=3) from error


def _apply(operation, family_id, image, layout, report, metadata, *, root, dry_run, log):
    from tools import rom_homology
    with lock.held(root):
        path = root / repo.HOMOLOGY
        original = path.read_text(encoding='utf-8')
        evidence = census(root / report, image, root)
        text = prepared(original, operation, image=image, layout=layout,
                        family_id=family_id, evidence=evidence, metadata=metadata)
        document = tomllib.loads(text)
        images = rom_homology.load_images(root / repo.CATALOG)
        rom_homology.validate_families(images, document['family'], path)
        rom_homology.validate_software_ids(images, document['family'], path)
        rom_homology.validate_relationships(document['family'], document.get('relationship', []), path)
        for changed in repo.layouts(root, {repo.HOMOLOGY: text}).values():
            if changed.family != family_id:
                continue
            failures = l0.check_layout(changed, root)
            if failures:
                raise KbError('family L0 gate fails: ' + '; '.join(
                    f'{item.path}: {item.message}' for item in failures), code=3)
        model = compile.build(root, {repo.HOMOLOGY: text})
        failures = write._issues(model)
        if failures:
            raise KbError('family model adds unresolved gate failures: ' + '; '.join(
                f'{item.check}: {item.subject}: {item.message}' for item in failures.values()), code=3)
        projection = Path('rom-images/homology.csv')
        rendered = rom_homology.build_report(root / repo.CATALOG, path, homology_text=text)
        texts = {repo.HOMOLOGY: text, projection: rendered}
        if dry_run:
            import difflib
            differences = []
            for relative, after in texts.items():
                target = root / relative
                before = target.read_bytes().decode('utf-8') if target.exists() else ''
                differences.extend(difflib.unified_diff(
                    before.splitlines(True), after.splitlines(True),
                    'a/' + relative.as_posix(), 'b/' + relative.as_posix()))
            return ''.join(differences)
        with publication.transaction(root, texts):
            store.write(root, texts)
            try:
                # Rebuild from the published registry and images, independently of
                # the proposed text used to prepare the publication.
                checked = rom_homology.build_report(root / repo.CATALOG, path)
                rom_homology.check_report(root / projection, checked)
                compile.cached.cache_clear()
                graph.sync_held(root, False, log, model)
            except rom_homology.HomologyError as error:
                raise KbError(f"{error}; publication journal retained; "
                              "run `uv run kb recover --status`", code=3) from error
        return f'family {operation} {family_id}: {image}; source and stock gates pass'
