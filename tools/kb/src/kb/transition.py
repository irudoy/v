"""One preservation-checked transfer of the remaining knowledge owners.

Preparation writes only a local plan. Application checks its exact source
fingerprint, compiles and gates the complete overlay, then uses the primary
store writer. No graph state changes before the complete source write.
"""

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import time
import tomllib

import tomlkit

from kb import (adapters, catalog, compile, convert, fingerprint, lock, names,
                reconciliation, repo, research, retirement, source_bindings, store, write)
from kb.adapters import curated
from kb.repo import KbError


def sha(data):
    return hashlib.sha256(data).hexdigest()


def head(root):
    result = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise KbError(result.stderr.strip(), code=3)
    return result.stdout.strip()


def payload_digest(data):
    """Bind the complete prepared writer payload independently of report fields."""
    payload = {key: data[key] for key in ('source_commit', 'fingerprint',
                                         'compiler_inputs', 'origins', 'texts')}
    return sha(json.dumps(payload, ensure_ascii=True, sort_keys=True,
                          separators=(',', ':')).encode())


def owned_before(base, root):
    conversion = convert.Conversion(curated, base, root)
    texts = conversion.run()
    order = tuple(item for item in adapters.ADAPTERS if item is not curated)
    owned = compile.build(root, {**base.overlay, **texts}, order=order)
    changed = convert.differences(conversion.expected(), convert.dump(owned))
    if changed:
        raise KbError('curated transfer changes existing facts:\n' + '\n'.join(changed[:30]), code=3)
    return owned


def enforce_preservation(before, result):
    failures = preserve(before, result)
    if failures:
        raise KbError('transfer does not preserve the source model:\n' + '\n'.join(failures[:30]), code=3)


def owner_config(model, root):
    document = tomlkit.document()
    document['schema_version'] = 1
    document['names'] = {}
    reserved = []
    for row in model.names:
        from kb.model import SymbolKey
        if SymbolKey(*row.key) not in model.symbols:
            reserved.append(dict(layout=row.layout, kind=row.kind, address=f'{row.address:08x}',
                name=row.name, former=list(row.former),
                reason='Permanent reservation of an original registry name without an active symbol.'))
    document['names']['owners_checked'] = True
    document['names']['reserved'] = reserved
    reviews = reconciliation.reviews(model)
    document['reconciliation'] = dict(enabled=True, review=reviews)
    document['source_bindings'] = dict(enabled=True, review=source_bindings.missing(model))
    return tomlkit.dumps(document), reviews, reserved


def preserve(before, result):
    """All existing claims survive; source tables and lossless notes are allowed additions."""
    first, last = convert.dump(before), convert.dump(result)
    failures = []
    for section in ('symbols', 'links', 'targets'):
        for key, value in first[section].items():
            if last[section].get(key) != value:
                failures.append(f'{section}: {key}: an existing fact changes')
    for key, value in first['meanings'].items():
        later = last['meanings'].get(key)
        if later is None:
            failures.append(f'meanings: {key}: an existing owner disappears')
            continue
        first_tables, last_tables = dict(value['tables']), dict(later['tables'])
        last_sources = last_tables.pop('source', ())
        for item in first_tables.pop('source', ()):
            if item not in last_sources:
                failures.append(f'meanings: {key}: an existing source binding disappears')
        if {**value, 'tables': tuple(sorted(first_tables.items()))} != {
                **later, 'tables': tuple(sorted(last_tables.items()))}:
            failures.append(f'meanings: {key}: an existing claim changes')
    for key, value in first['entities'].items():
        if key[0] != 'chain' and last['entities'].get(key) != value:
            failures.append(f'entities: {key}: an existing fact changes')
    for (kind, slug), entity in before.entities.items():
        if kind != 'chain':
            continue
        original = store.load(before.root, store.path_of(kind, slug), before.overlay)
        current = store.load(result.root, store.path_of(kind, slug), result.overlay)
        if research.restore(current) != research.restore(original):
            failures.append(f'chain: {slug}: original steps are not preserved exactly')
    failures.extend(research.preservation(before, result))
    failures.extend(retirement.preserved(before, result))
    return failures


def gated(result):
    failures = write._issues(result)
    if failures:
        counts = Counter(item.check for item in failures.values())
        details = [f'{item.check}: {item.path}: {item.subject}: {item.message}'
                   for item in failures.values()]
        raise KbError('complete transfer fails gates: ' + str(dict(counts)) + '\n'
                      + '\n'.join(details[:30]), code=3)


def prepare(source_commit, output, root=repo.ROOT):
    output = Path(output).resolve()
    if output.exists() or not (output.is_relative_to(root / 'tmp')
                               or output.is_relative_to(root / repo.STATE)):
        raise KbError('a transfer plan needs a new path under tmp/ or .kb/', code=2)
    with lock.held(root):
        if head(root) != source_commit:
            raise KbError('transfer source commit differs from HEAD', code=3)
        started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
        before_fp = fingerprint.compute(root)
        legacy_order = tuple(item for item in adapters.ORDER
                             if item not in adapters.CONVERTED or item is curated)
        target_order = tuple(item for item in adapters.ADAPTERS if item is not curated)
        base = compile.build(root, order=legacy_order)
        conversion = convert.Conversion(curated, base, root)
        texts = conversion.run()
        owned = compile.build(root, texts, order=target_order)
        changed = convert.differences(conversion.expected(), convert.dump(owned))
        if changed:
            raise KbError('curated transfer changes existing facts:\n' + '\n'.join(changed[:30]), code=3)
        ops, statements = research.operations(owned, source_commit, root)
        change = write.Change(owned, write.model_resolver(owned), root)
        for index, operation in enumerate(ops, 1):
            change.run(operation, index)
        texts.update(change.texts())
        texts.update(catalog.plan(owned, root))
        texts.update(source_bindings.plan(owned, root))
        model = compile.build(root, texts, order=target_order)
        config, reviews, reservations = owner_config(model, root)
        texts[repo.OWNER_CONFIG] = config
        result = compile.build(root, texts, order=target_order)
        failures = preserve(owned, result)
        if failures:
            raise KbError('transfer does not preserve the source model:\n' + '\n'.join(failures[:30]), code=3)
        gated(result)
        after_fp = fingerprint.compute(root)
        if before_fp != after_fp:
            raise KbError('transfer source changes during preparation', code=3)
        origins = {path.as_posix(): (sha((root / path).read_bytes()) if (root / path).exists() else None)
                   for path in texts}
        legacy_path = curated.DIRECTORY / '1nd.csv'
        origins[legacy_path.as_posix()] = sha((root / legacy_path).read_bytes())
        data = dict(version=2, source_commit=source_commit, fingerprint=before_fp.value,
            compiler_inputs=before_fp.blobs, origins=origins,
            texts={path.as_posix(): text for path, text in texts.items()},
            started_utc=started, finished_utc=datetime.now(timezone.utc).isoformat(),
            inclusive_elapsed_seconds=time.monotonic()-clock, knowledge_written=False,
            graph_changed=False, research=statements, unresolved_code=Counter(item['kind'] for item in reviews),
            inactive_names=len(reservations), catalog_features=len(catalog.documents(catalog.rows(root), model.layouts)),
            source_anchors=len(source_bindings.records(root)), curated_selectors=len(conversion.curated_tables))
        data['payload_sha256'] = payload_digest(data)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')
        print(json.dumps({key: data[key] for key in ('curated_selectors', 'source_anchors',
            'catalog_features', 'inactive_names', 'unresolved_code', 'inclusive_elapsed_seconds',
            'knowledge_written', 'graph_changed')}))


def apply(path, root=repo.ROOT):
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    if data.get('version') != 2:
        raise KbError('unknown consolidated transfer version', code=2)
    if data.get('payload_sha256') != payload_digest(data):
        raise KbError('prepared transfer payload differs from its exact binding', code=3)
    with lock.held(root):
        if head(root) != data['source_commit'] or fingerprint.compute(root).value != data['fingerprint']:
            raise KbError('prepared transfer has stale source inputs', code=3)
        texts = {Path(name): text for name, text in data['texts'].items()}
        for target in texts:
            if (target.is_absolute() or '..' in target.parts
                    or (target not in (repo.CONFIG, repo.OWNER_CONFIG, names.PATH)
                        and not (target.parts[0] == 'kb' and len(target.parts) == 3
                                 and target.suffix == '.toml'))):
                raise KbError(f'{target}: not a primary transfer owner', code=2)
        for name, expected in data['origins'].items():
            path = root / name
            actual = sha(path.read_bytes()) if path.exists() else None
            if actual != expected:
                raise KbError(f'{name}: prepared transfer has stale owner bytes', code=3)
        legacy_order = tuple(item for item in adapters.ORDER
                             if item not in adapters.CONVERTED or item is curated)
        base = compile.build(root, order=legacy_order)
        before = owned_before(base, root)
        result = compile.build(root, texts)
        enforce_preservation(before, result)
        if not (result.config.get('reconciliation', {}).get('enabled')
                and result.config.get('source_bindings', {}).get('enabled')
                and result.config.get('names', {}).get('owners_checked')):
            raise KbError('prepared transfer must retain all exact owner and source checks', code=3)
        gated(result)
        if head(root) != data['source_commit'] or fingerprint.compute(root).value != data['fingerprint']:
            raise KbError('prepared transfer sources change during application gates', code=3)
        store.write(root, texts)
        compile.cached.cache_clear()
        print(f'consolidated transfer: {len(texts)} primary files; source model gates pass; graph not changed')


def historical_owners(commit, root):
    """Validated immutable primary owner bytes, read without a filesystem checkout."""
    if not research.COMMIT.fullmatch(commit):
        raise KbError('historical owners need a complete immutable source commit', code=2)
    result = subprocess.run(['git', 'archive', '--format=tar', commit, 'kb',
                             repo.CONFIG.as_posix()], cwd=root, capture_output=True)
    if result.returncode:
        raise KbError('immutable primary owner source is unavailable: '
                      + result.stderr.decode().strip(), code=3)
    original = {}
    with tarfile.open(fileobj=io.BytesIO(result.stdout), mode='r:') as archive:
        for entry in archive:
            if not entry.isfile():
                continue
            path = Path(entry.name)
            if path.is_absolute() or '..' in path.parts or not (
                    path == repo.CONFIG or path.parts[0] == 'kb'):
                raise KbError('immutable archive contains a non-owner path', code=3)
            original[path] = archive.extractfile(entry).read().decode('utf-8')
    return original


def separated_owner_texts(current, original):
    """Move only owner additions, retaining exact accepted execution settings."""
    current_document, original_document = tomllib.loads(current), tomllib.loads(original)
    owners = {'schema_version': 1}
    owners['names'] = {key: current_document['names'].pop(key)
                       for key in ('owners_checked', 'reserved')}
    for key in ('reconciliation', 'source_bindings'):
        owners[key] = current_document.pop(key)
    if current_document != original_document:
        raise KbError('execution configuration has changes beyond owner declarations', code=3)
    return {repo.CONFIG: original, repo.OWNER_CONFIG: tomlkit.dumps(owners)}


def separate_owners(source_commit, output, root=repo.ROOT):
    """Prepare the exact owner separation through the existing transfer writer."""
    output = Path(output).resolve()
    if output.exists() or not output.is_relative_to(root / 'tmp'):
        raise KbError('owner separation needs a new plan under tmp/', code=2)
    with lock.held(root):
        if head(root) != source_commit or (root / repo.OWNER_CONFIG).exists():
            raise KbError('owner separation needs the current immutable source and no prior owner file', code=3)
        fp = fingerprint.compute(root)
        original = historical_owners(source_commit, root)[repo.CONFIG]
        texts = separated_owner_texts((root / repo.CONFIG).read_text(), original)
        before, result = compile.build(root), compile.build(root, texts)
        enforce_preservation(before, result)
        gated(result)
        if fingerprint.compute(root) != fp:
            raise KbError('owner-separation inputs change during preparation', code=3)
        data = dict(version=2, source_commit=source_commit, fingerprint=fp.value,
            compiler_inputs=fp.blobs, origins={path.as_posix():
                sha((root / path).read_bytes()) if (root / path).exists() else None for path in texts},
            texts={path.as_posix(): text for path, text in texts.items()})
        data['payload_sha256'] = payload_digest(data)
        output.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n')
        print('owner separation: exact accepted execution config; existing facts preserved; no source write')


def audit_applied(path, root=repo.ROOT):
    """Repeat preservation against the immutable owner commit, without any write."""
    data = json.loads(Path(path).read_text(encoding='utf-8'))
    with lock.held(root):
        if head(root) != data['source_commit']:
            raise KbError('applied-transfer source commit differs from HEAD', code=3)
        fp = fingerprint.compute(root)
        original = historical_owners(data['source_commit'], root)
        for name, expected in data['origins'].items():
            historical = original.get(Path(name))
            if historical is None and not name.startswith('kb/'):
                historical = (root / name).read_text(encoding='utf-8')
            if (sha(historical.encode()) if historical is not None else None) != expected:
                raise KbError(f'{name}: prepared origin differs from its immutable source', code=3)
        for name, text in data['texts'].items():
            actual = (root / name).read_text(encoding='utf-8') if (root / name).exists() else None
            if actual != text:
                raise KbError(f'{name}: applied owner differs from the exact prepared payload', code=3)
        overlay = {path: None for _, _, path in store.files(root)}
        overlay[repo.OWNER_CONFIG] = None
        overlay.update(original)
        legacy_order = tuple(item for item in adapters.ORDER
                             if item not in adapters.CONVERTED or item is curated)
        source = compile.build(root, overlay, order=legacy_order)
        before = owned_before(source, root)
        result = compile.build(root)
        enforce_preservation(before, result)
        gated(result)
        if fp != fingerprint.compute(root):
            raise KbError('applied owner sources change during preservation audit', code=3)
        print(f'applied transfer: exact payload of {len(data["texts"])} files; '
              'immutable existing facts and original chains preserved; no write or graph change')


def snapshot(source_commit, output, root=repo.ROOT):
    """Freeze acceptance inputs after proving immutable source preservation."""
    output = Path(output).resolve()
    if output.exists() or not output.is_relative_to(root / 'tmp'):
        raise KbError('acceptance snapshot needs a new path under tmp/', code=2)
    with lock.held(root):
        if head(root) != source_commit:
            raise KbError('acceptance snapshot source commit differs from HEAD', code=3)
        fp = fingerprint.compute(root)
        original = historical_owners(source_commit, root)
        overlay = {path: None for _, _, path in store.files(root)}
        overlay[repo.OWNER_CONFIG] = None
        overlay.update(original)
        order = tuple(item for item in adapters.ORDER
                      if item not in adapters.CONVERTED or item is curated)
        before = owned_before(compile.build(root, overlay, order=order), root)
        result = compile.build(root)
        enforce_preservation(before, result)
        gated(result)
        listing = subprocess.run(['git', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                                 cwd=root, capture_output=True, check=True).stdout
        paths = sorted({Path(name.decode()) for name in listing.split(b'\0') if name
                        and (root / name.decode()).is_file()})
        source_hashes = {path.as_posix(): repo.sha256_file(root / path) for path in paths}
        diff = subprocess.run(['git', 'diff', '--binary', 'HEAD'], cwd=root,
                              capture_output=True, check=True).stdout
        if fingerprint.compute(root) != fp:
            raise KbError('acceptance inputs change during snapshot', code=3)
        output.write_text(json.dumps(dict(source_commit=source_commit,
            fingerprint=fp.value, compiler_inputs=fp.blobs, files_sha256=source_hashes,
            tracked_diff_sha256=sha(diff), original_facts_preserved=True,
            original_chains_restored=True, knowledge_written=False, graph_changed=False),
            indent=2, sort_keys=True) + '\n')
        print(f'acceptance snapshot: {len(paths)} files; immutable facts and chains preserved; no write')


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='operation', required=True)
    planned = commands.add_parser('prepare')
    planned.add_argument('--source-commit', required=True)
    planned.add_argument('--output', required=True)
    separated = commands.add_parser('separate-owners')
    separated.add_argument('--source-commit', required=True)
    separated.add_argument('--output', required=True)
    frozen = commands.add_parser('snapshot')
    frozen.add_argument('--source-commit', required=True)
    frozen.add_argument('--output', required=True)
    applied = commands.add_parser('apply')
    applied.add_argument('plan')
    audited = commands.add_parser('audit-applied')
    audited.add_argument('plan')
    args = parser.parse_args(argv)
    try:
        if args.operation == 'prepare':
            prepare(args.source_commit, args.output)
        elif args.operation == 'separate-owners':
            separate_owners(args.source_commit, args.output)
        elif args.operation == 'snapshot':
            snapshot(args.source_commit, args.output)
        elif args.operation == 'apply':
            apply(args.plan)
        else:
            audit_applied(args.plan)
    except KbError as error:
        parser.exit(error.code, f'error: {error}\n')


if __name__ == '__main__':
    main()
