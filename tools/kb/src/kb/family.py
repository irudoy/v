"""Primary family onboarding with comment-preserving TOML and stock gates."""

import hashlib
from pathlib import Path
import re
import tempfile
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


def _validate(text, root):
    from tools import rom_homology

    path = root / repo.HOMOLOGY
    document = tomllib.loads(text)
    try:
        images = rom_homology.load_images(root / repo.CATALOG)
        rom_homology.validate_families(images, document['family'], path)
        rom_homology.validate_software_ids(images, document['family'], path)
        rom_homology.validate_relationships(document['family'], document.get('relationship', []), path)
    except rom_homology.HomologyError as error:
        raise KbError(str(error), code=3) from error


def draft(family_id, image, layout, metadata, root=repo.ROOT):
    """Render a new family for L0 preparation before a census exists."""
    original = (root / repo.HOMOLOGY).read_text(encoding='utf-8')
    text = prepared(original, 'new', image=image, layout=layout, family_id=family_id,
                    evidence='Proposed catalog identity and layout.', metadata=metadata)
    _validate(text, root)
    return text


def draft_layout(layout_id, path, root=repo.ROOT):
    """Resolve one new layout without replacing the published family registry."""
    original = tomllib.loads((root / repo.HOMOLOGY).read_text(encoding='utf-8'))
    text = path.read_text(encoding='utf-8')
    try:
        document = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise KbError(f'{path}: {error}', code=2) from error
    existing = original['family']
    families = document.get('family', {})
    if not isinstance(families, dict):
        raise KbError(f'{path}: family must be a table', code=3)
    new = set(families) - set(existing)
    if (len(new) != 1 or {key: value for key, value in families.items() if key not in new} != existing
            or {**document, 'family': existing} != original):
        raise KbError(f'{path}: draft must add one family to the current registry', code=3)
    _validate(text, root)
    layout = repo.layouts(root, {repo.HOMOLOGY: text}).get(layout_id)
    if layout is None or layout.family not in new:
        raise KbError(f'{path}: draft does not introduce layout {layout_id!r}', code=3)
    return layout


def _initial_bindings(ops, layout, model, root, report):
    """Plan the first interpolation owners and check their generated census against L0."""
    from kb.adapters import interp
    from tools import census_homology

    for op in ops:
        if isinstance(op, dict):
            if op.get('cmd') == 'bind' and str(op.get('symbol')).startswith(f'{layout.id}:'):
                continue
            if (op.get('cmd') == 'set' and op.get('layout') == layout.id
                    and isinstance(op.get('keys'), dict) and set(op['keys']) == {'interp'}
                    and not op.get('unset')):
                continue
        raise KbError(f'initial batch can bind symbols and set interpolation on {layout.id}', code=2)
    _, texts, model = write.plan(ops, model, write.model_resolver(model), root, strict=True)
    registries = interp.render_registries(model)
    names = [name for name, owner in interp.owners(model).items() if owner == layout.id]
    if len(names) != 1:
        raise KbError(f'{layout.id}: the initial batch needs an owned interpolation registry', code=3)
    name, = names
    text = registries[name]
    with tempfile.TemporaryDirectory(prefix='kb-family-census-') as scratch:
        proposed = Path(scratch) / Path(name).name
        proposed.write_text(text, encoding='utf-8', newline='')
        plan = l0.census(layout.id, root, proposed)
        _check_layout(layout, root, census_plan=plan)
        export = root / repo.L0 / layout.id
        image = repo.images(root)[layout.image]
        entities = census_homology.read_entities(proposed, export, image.path.stat().st_size)
    reported = {int(row['target'], 16): (row['kind'], row['geometry'])
                for row in census_homology.read_ledger(root / report)}
    if entities != reported:
        raise KbError(f'{report}: target operands differ from the checked L0 census', code=3)
    return {**texts, Path(name): text}, model


def _check_layout(layout, root, **kwargs):
    failures = l0.check_layout(layout, root, **kwargs)
    if failures:
        raise KbError('family L0 gate fails: ' + '; '.join(
            f'{item.path}: {item.message}' for item in failures), code=3)


def apply(operation, family_id, image, layout, report, metadata=None, *, root=repo.ROOT,
          dry_run=False, batch=None, log=print):
    """Prepare registry and report, publish both through synchronization."""
    from tools import rom_homology
    try:
        return _apply(operation, family_id, image, layout, report, metadata,
                      root=root, dry_run=dry_run, batch=batch, log=log)
    except rom_homology.HomologyError as error:
        raise KbError(str(error), code=3) from error


def _apply(operation, family_id, image, layout, report, metadata, *, root, dry_run, batch, log):
    from kb import catalog
    from tools import rom_homology
    with lock.held(root):
        path = root / repo.HOMOLOGY
        original = path.read_text(encoding='utf-8')
        evidence = census(root / report, image, root)
        text = prepared(original, operation, image=image, layout=layout,
                        family_id=family_id, evidence=evidence, metadata=metadata)
        _validate(text, root)
        overlay = {repo.HOMOLOGY: text}
        layouts = repo.layouts(root, overlay)
        if batch is None:
            for changed in layouts.values():
                if changed.family == family_id:
                    _check_layout(changed, root)
        elif operation != 'new':
            raise KbError('initial bindings require a new family', code=2)
        elif not (root / repo.L0 / layout / l0.MANIFEST).is_file():
            raise KbError(f'family L0 gate fails: {layout} has no L0 export', code=3)

        model = compile.build(root, overlay)
        if layout is not None and (root / catalog.PATH).is_file():
            targets = catalog.plan(model, root, layout=layout)
            if targets:
                overlay.update(targets)
                model = compile.build(root, overlay)
        texts = dict(overlay)
        if batch is None:
            failures = write._issues(model)
            if failures:
                raise KbError('family model adds unresolved gate failures: ' + '; '.join(
                    f'{item.check}: {item.subject}: {item.message}' for item in failures.values()), code=3)
        else:
            initial, model = _initial_bindings(write.read_batch(batch), layouts[layout], model,
                                               root, report)
            texts.update(initial)
        projection = Path('rom-images/homology.csv')
        rendered = rom_homology.build_report(root / repo.CATALOG, path, homology_text=text)
        texts[projection] = rendered
        if dry_run:
            import difflib
            differences = []
            for relative, after in texts.items():
                target = root / relative
                before = target.read_bytes().decode('utf-8') if target.exists() else ''
                differences.extend(difflib.unified_diff(
                    before.splitlines(True), (after or '').splitlines(True),
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
