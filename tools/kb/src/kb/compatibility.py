"""Fingerprint-bound compatibility layers for the existing graph consumers.

The tracked layer algorithms share the primary compiler's driver and lock.
Owned CSV views are rendered from the model into a private temporary directory;
stale generated files in the working tree cannot supply graph facts.
"""

from contextlib import contextmanager, redirect_stdout
from dataclasses import asdict
import csv
import io
import hashlib
import json
from pathlib import Path
import sys
import subprocess
import tempfile
import time

from kb import compatibility_state as state, repo

REFERENCE = Path('defs/reference/Pytrex-NissanDefinitions')
A2L = REFERENCE / 'Nissan Definitions/A2L.xml'
PIN = REFERENCE.as_posix() + '#commit'
MODULES = (
    'tools/rom_sources.py', 'tools/mapkit/rom.py',
    'tools/memgraph/load_graph.py', 'tools/memgraph/load_xrefs.py',
    'tools/memgraph/load_maps.py', 'tools/memgraph/load_code.py',
    'tools/memgraph/load_diagnostic_bindings.py', 'tools/memgraph/ingest_diagnostics.py',
    'tools/memgraph/load_vendor.py', 'tools/memgraph/load_a2l.py',
    'tools/memgraph/provenance.py', 'tools/diagnostics/catalog.py',
    'tools/kb/src/kb/ledger_projection.py', 'tools/kb/src/kb/adapters/interp.py',
    'tools/kb/src/kb/adapters/curated.py',
)
EXTERNAL = (
    '.gitmodules', A2L.as_posix(), 'defs/rom-inheritance.toml',
    'tools/memgraph/docker-compose.yml',
    'refs/vendor/catalog.csv', 'refs/vendor/facts.csv',
)
FRAMEWORK = (
    'tools/kb/src/kb/compatibility.py', 'tools/kb/src/kb/compatibility_state.py',
    'tools/memgraph/docker-compose.yml', 'pyproject.toml', 'uv.lock',
)
CORPUS_CODE = ('tools/memgraph/ingest_diagnostics.py', 'tools/diagnostics/catalog.py')
EXTERNAL_CODE = ('tools/memgraph/load_vendor.py', 'tools/memgraph/load_a2l.py')
ROM_CODE = tuple(path for path in MODULES if path not in CORPUS_CODE + EXTERNAL_CODE) + (
    'tools/kb/src/kb/l0.py', 'tools/kb/src/kb/repo.py',
)
ROM_LABELS = ('DiagnosticBinding', 'Map', 'Axis', 'Interp', 'Reg', 'Func')


def inputs(root=repo.ROOT):
    """Every retained layer's code and source file, excluding owned CSV views."""
    found = set(MODULES) | set(EXTERNAL)
    owned = {f'defs/JK08A.{kind}.csv' for kind in
             ('funcs', 'vars', 'findings', 'axes', 'diagnostic-bindings')}
    for kind in ('funcs', 'vars', 'findings', 'axes', 'diagnostic-bindings'):
        found.update(path.relative_to(root).as_posix()
                     for path in (root / 'defs').glob(f'*.{kind}.csv')
                     if path.relative_to(root).as_posix() not in owned)
    directory = root / 'refs/diagnostics'
    found.update(path.relative_to(root).as_posix() for path in directory.rglob('*')
                 if path.is_file() and path.suffix in ('.toml', '.csv', '.jsonl'))
    return sorted(found)


def modules(root=repo.ROOT):
    """Import the repository-contained builders without opening a connection."""
    sys.path.insert(0, str(root / 'tools'))
    from memgraph import (ingest_diagnostics, load_a2l, load_code, load_diagnostic_bindings,
                          load_graph, load_maps, load_vendor, load_xrefs)
    import rom_sources
    return dict(diagnostics=ingest_diagnostics, a2l=load_a2l, code=load_code,
                bindings=load_diagnostic_bindings, functions=load_graph,
                maps=load_maps, vendor=load_vendor, accesses=load_xrefs,
                sources=rom_sources)


def _git(root, *args):
    result = subprocess.run(['git', *args], cwd=root, capture_output=True, text=True)
    if result.returncode:
        raise repo.KbError(f'pinned reference command fails: {result.stderr.strip()}', code=3)
    return result.stdout.strip()


def reference_commit(root=repo.ROOT):
    """The initialized reference checkout's actual identity, or explicit absence."""
    directory = root / REFERENCE
    if not (directory / '.git').exists():
        return 'absent'
    return _git(directory, 'rev-parse', 'HEAD')


def check_reference(root=repo.ROOT):
    """Bind A2L to the exact gitlink and its immutable tracked file bytes."""
    actual = reference_commit(root)
    if actual == 'absent':
        raise repo.KbError('pinned A2L reference is not initialized; run `make setup`', code=3)
    entries = _git(root, 'ls-files', '--stage', '--', REFERENCE.as_posix()).splitlines()
    if len(entries) != 1:
        raise repo.KbError('pinned A2L reference needs one unconflicted gitlink', code=3)
    metadata, path = entries[0].split('\t', 1)
    mode, expected, stage = metadata.split()
    if (mode, stage, path) != ('160000', '0', REFERENCE.as_posix()) or actual != expected:
        raise repo.KbError('A2L checkout differs from the repository gitlink', code=3)
    relative = A2L.relative_to(REFERENCE).as_posix()
    expected_blob = _git(root / REFERENCE, 'rev-parse', f'{expected}:{relative}')
    data = (root / A2L).read_bytes()
    actual_blob = hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()
    if actual_blob != expected_blob:
        raise repo.KbError('A2L bytes differ from the pinned immutable source', code=3)
    return actual


@contextmanager
def views(model, root=repo.ROOT):
    """Paths of exact current-model views, never a second durable authority."""
    from kb import ledger_projection
    from kb.adapters import curated, interp

    rendered = ledger_projection.render(model)
    rendered.update(interp.render_registries(model))
    if any('curated' in symbol.props for symbol in model.symbols.values()):
        rendered.update(curated.render(model))
    cache = root / repo.STATE / 'cache'
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='graph-views-', dir=cache) as temporary:
        found = {}
        for name, text in rendered.items():
            path = Path(temporary) / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
            found[name] = path
        yield found


def selected_path(paths, path, root):
    return paths.get(path.relative_to(root).as_posix(), path)


def curated_names(paths, layout, root):
    path = selected_path(paths, root / f'tools/ghidra/symbols/{layout}.csv', root)
    if not path.exists():
        return {}
    with path.open(newline='', encoding='utf-8') as source:
        return {row['addr']: row['name'] for row in
                csv.DictReader(line for line in source if not line.startswith('#'))}


def empty_views(paths, code):
    """Represent an absent manual catalog as no rows, without inferred claims."""
    headers = {'Map': code.MAP_FIELDS, 'Axis': code.AXIS_FIELDS}
    for label, fields in headers.items():
        path = paths[label]
        if path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(','.join(fields) + '\n', encoding='utf-8')


def producer_files(root, code):
    return [(f'producer:{name}', root / name) for name in FRAMEWORK + code]


def group_inputs(files, values, code):
    return state.Inputs(files, values,
                        tuple(f'producer:{name}' for name in FRAMEWORK + code))


def corpus_inputs(root):
    def files():
        found = producer_files(root, CORPUS_CODE)
        directory = root / 'refs/diagnostics'
        found.extend((f'corpus:{path.relative_to(directory).as_posix()}', path)
                     for path in sorted(directory.rglob('*'))
                     if path.is_file() and path.suffix in ('.toml', '.csv', '.jsonl'))
        return found
    return group_inputs(files, {'scope': 'diagnostic corpus'}, CORPUS_CODE)


def external_inputs(root):
    files = producer_files(root, EXTERNAL_CODE)
    files.extend((name, root / name) for name in
                 ('.gitmodules', A2L.as_posix(), 'refs/vendor/catalog.csv', 'refs/vendor/facts.csv'))
    return group_inputs(tuple(files),
                        lambda: {'family': 'HR', 'reference_commit': check_reference(root)},
                        EXTERNAL_CODE)


def rom_inputs(root, builders, rom, layout, source, declared, paths, names_path,
               census, registry, corpus_digest, original_paths):
    """Bind physical L0/images and logical, current-model catalog views."""
    files = producer_files(root, ROM_CODE)
    files.extend((name, root / name) for name in
                 ('defs/rom-inheritance.toml', repo.CATALOG.as_posix()))
    outdir = root / repo.L0 / layout.id
    files.extend((f'l0:{layout.id}/{name}', outdir / name)
                 for name in ('funcs.csv', 'calls.csv', 'xrefs.csv'))
    files.append((f'names:{layout.id}', names_path))
    files.extend((f'catalog:{label}', paths[label])
                 for label in ('Func', 'Reg', 'Map', 'Axis', 'DiagnosticBinding'))
    if census:
        files.append(('interpolation', registry))
    catalog = repo.images(root)
    for image in sorted({rom, source.source}):
        files.append((f'image:{image}', catalog[image].path))
    def current_files():
        found = list(files)
        if census:
            # The builder also refuses extra census filenames. Bind and capture
            # their complete inventory, rather than selecting only declared cores.
            selected = set(outdir.glob('accessors.*.csv'))
            selected.update(Path(builders['maps'].census_path(outdir, entry['kernel']))
                            for entry in builders['maps'].read_registry(registry))
            found.extend((f'census:{layout.id}/{path.name}', path) for path in sorted(selected))
        return found
    def values():
        return dict(rom=rom, layout=layout.id, source=asdict(source), census=census,
                    catalogs={label: path.relative_to(root).as_posix()
                              for label, path in declared.items()},
                    image_paths={image: catalog[image].path.relative_to(root).as_posix()
                                 for image in sorted({rom, source.source})},
                    presence={label: path.exists() for label, path in original_paths.items()},
                    diagnostic_corpus=corpus_digest)
    return group_inputs(current_files, values, ROM_CODE)


def rom_destinations(captured):
    values = json.loads(captured.arguments)
    found = {name: name for name in ('defs/rom-inheritance.toml', repo.CATALOG.as_posix())}
    for name, data in captured.files:
        if name.startswith('l0:'):
            found[name] = repo.L0 / name.removeprefix('l0:')
        elif name.startswith('census:'):
            found[name] = repo.L0 / name.removeprefix('census:')
        elif name.startswith('names:'):
            found[name] = f'tools/ghidra/symbols/{name.removeprefix("names:")}.csv'
        elif name.startswith('catalog:'):
            found[name] = values['catalogs'][name.removeprefix('catalog:')]
        elif name.startswith('image:'):
            found[name] = values['image_paths'][name.removeprefix('image:')]
        elif name == 'interpolation':
            found[name] = values['census']['interp']
    return found


def clear_rom(graph, rom):
    """Remove only this cohort's outputs, including absent optional stages."""
    for label in ROM_LABELS:
        graph.run(f'MATCH (n:{label} {{rom:$rom}}) DETACH DELETE n', rom=rom)
    graph.run('MATCH (r:Rom {id:$rom})-[e:ANNOTATIONS_FROM]->() DELETE e', rom=rom)
    graph.run('MATCH (r:Rom {id:$rom}) REMOVE r.annotation_source, r.source_kind, '
              'r.source_evidence, r.target_sha256, r.source_sha256, r.source_ranges', rom=rom)


def existing_roms(graph):
    query = ' UNION '.join(f'MATCH (n:{label}) RETURN DISTINCT n.rom AS rom'
                           for label in ROM_LABELS)
    return {row['rom'] for row in graph.run(query) if row['rom'] is not None}


def load(graph, model, root=repo.ROOT, log=print):
    """Reuse complete exact-input cohorts before publishing overall Meta."""
    check_reference(root)
    builders = modules(root)
    completed = state.Completed(graph, log)
    summary = {}
    def run(name, function, *args):
        started = time.monotonic()
        state.progress(log, f'graph layer: {name} loading')
        with redirect_stdout(io.StringIO()):
            result = function(graph.driver, *args)
        summary[name] = (result or {}, time.monotonic() - started, {})
        state.progress(log, f'graph layer: {name} complete ({summary[name][1]:.1f} s)')

    # Even a missing corpus checkpoint with unchanged bytes requires rebuilding
    # the corpus. Its builder deletes every ROM's DiagnosticBinding nodes.
    corpus = corpus_inputs(root)
    def build_corpus(captured):
        destinations = {name: Path('refs/diagnostics') / name.removeprefix('corpus:')
                        for name, data in captured.files if name.startswith('corpus:')}
        with captured.tree(root, destinations) as frozen:
            run('diagnostic corpus', builders['diagnostics'].load, frozen / 'refs/diagnostics')
    completed.run('diagnostic corpus', corpus,
                  build_corpus,
                  kind='corpus', invalidates=completed.roms())
    corpus_digest = corpus.digest()
    with views(model, root) as projected:
        sources = builders['sources']
        wanted = {f'rom:{rom}' for layout in model.layouts.values() for rom in layout.images}
        retired = existing_roms(graph) - {key.removeprefix('rom:') for key in wanted}
        for key in completed.roms():
            if key not in wanted:
                rom = completed.records[key]['rom']
                completed.invalidate(key)
                retired.add(rom)
        for rom in sorted(retired):
            clear_rom(graph, rom)
        for layout in model.layouts.values():
            for rom in layout.images:
                outdir = root / repo.L0 / layout.id
                source = sources.resolve(rom, root / 'defs/rom-inheritance.toml')
                sources.verify_image_binding(source, root / 'rom-images/roms.csv')
                declared = sources.definition_paths(source, root)
                paths = {label: selected_path(projected, path, root)
                         for label, path in declared.items()}
                original_paths = dict(paths)
                names_path = selected_path(projected, root / f'tools/ghidra/symbols/{layout.id}.csv', root)
                census = model.config.get('l0', {}).get('census', {}).get(layout.id)
                registry = None
                if census:
                    registry = selected_path(projected, root / census['interp'], root)
                    if census['interp'] not in projected:
                        raise repo.KbError(f'{rom}: interpolation view is not model-owned', code=3)
                    # Missing manual catalogs remain empty scratch views. The L0 and
                    # image still determine structure and measured contents.
                    for label in ('Map', 'Axis'):
                        if not paths[label].exists():
                            paths[label] = registry.parent / f'{source.source}.{label}.empty.csv'
                    empty_views(paths, builders['code'])
                if paths['Func'].exists():
                    missing = [label for label in ('Reg', 'Map', 'Axis')
                               if not paths[label].exists()]
                    if missing:
                        raise repo.KbError(f'{rom}: reviewed catalog lacks {missing}', code=3)
                inputs = rom_inputs(root, builders, rom, layout, source, declared, paths,
                                    names_path, census, registry, corpus_digest, original_paths)

                def build_rom(captured):
                    arguments = json.loads(captured.arguments)
                    with captured.tree(root, rom_destinations(captured)) as frozen:
                        actual = sources.resolve(rom, frozen / 'defs/rom-inheritance.toml')
                        if json.loads(json.dumps(asdict(actual))) != arguments['source']:
                            raise repo.KbError(f'{rom}: captured inheritance differs from the plan', code=6)
                        actual_images = repo.images(frozen)
                        if any(actual_images[image].path.relative_to(frozen).as_posix() != path
                               for image, path in arguments['image_paths'].items()):
                            raise repo.KbError(f'{rom}: captured image paths differ from the plan', code=6)
                        sources.verify_image_binding(actual, frozen / repo.CATALOG)
                        selected = {label: frozen / path for label, path in arguments['catalogs'].items()}
                        directory = frozen / repo.L0 / layout.id
                        clear_rom(graph, rom)
                        run(f'{rom} functions', builders['functions'].load, rom, directory,
                            curated_names({}, layout.id, frozen))
                        run(f'{rom} accesses', builders['accesses'].load, rom, directory)
                        if arguments['census']:
                            run(f'{rom} maps', builders['maps'].load, rom, directory,
                                frozen / arguments['census']['interp'], selected['Map'], selected['Axis'], frozen)
                        if selected['Func'].exists():
                            run(f'{rom} claims', builders['code'].load, rom, selected, frozen)
                        if selected['DiagnosticBinding'].exists():
                            run(f'{rom} bindings', builders['bindings'].load, rom,
                                selected['DiagnosticBinding'], frozen)

                completed.run(f'rom:{rom}', inputs, build_rom, kind='rom', rom=rom)

    def build_external(captured):
        destinations = {name: name for name, data in captured.files if not name.startswith('producer:')}
        with captured.tree(root, destinations) as frozen:
            run('vendor vocabulary', builders['vendor'].load, 'HR',
                frozen / 'refs/vendor/catalog.csv', frozen / 'refs/vendor/facts.csv')
            run('reference A2L', builders['a2l'].load, frozen / A2L, 'HR',
                frozen / 'refs/vendor/catalog.csv')
    completed.run('external vocabularies', external_inputs(root),
                  build_external, kind='external')
    return summary
