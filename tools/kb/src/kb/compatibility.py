"""Fingerprint-bound compatibility layers for the existing graph consumers.

The tracked layer algorithms share the primary compiler's driver and lock.
Owned CSV views are rendered from the model into a private temporary directory;
stale generated files in the working tree cannot supply graph facts.
"""

from contextlib import contextmanager, redirect_stdout
import csv
import io
import hashlib
from pathlib import Path
import sys
import subprocess
import tempfile
import time

from kb import repo

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


def load(graph, model, root=repo.ROOT, log=print):
    """Build every retained layer before the primary loader publishes Meta."""
    check_reference(root)
    builders = modules(root)
    summary = {}
    def run(name, function, *args):
        started = time.monotonic()
        with redirect_stdout(io.StringIO()):
            result = function(graph.driver, *args)
        summary[name] = (result or {}, time.monotonic() - started, {})
        log(f'graph layer: {name} complete')

    run('diagnostic corpus', builders['diagnostics'].load, root / 'refs/diagnostics')
    with views(model, root) as projected:
        sources = builders['sources']
        for layout in model.layouts.values():
            for rom in layout.images:
                outdir = root / repo.L0 / layout.id
                source = sources.resolve(rom, root / 'defs/rom-inheritance.toml')
                sources.verify_image_binding(source, root / 'rom-images/roms.csv')
                declared = sources.definition_paths(source, root)
                paths = {label: selected_path(projected, path, root)
                         for label, path in declared.items()}
                run(f'{rom} functions', builders['functions'].load, rom, outdir,
                    curated_names(projected, layout.id, root))
                run(f'{rom} accesses', builders['accesses'].load, rom, outdir)
                census = model.config.get('l0', {}).get('census', {}).get(layout.id)
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
                    run(f'{rom} maps', builders['maps'].load, rom, outdir, registry,
                        paths['Map'], paths['Axis'], root)
                if paths['Func'].exists():
                    missing = [label for label in ('Reg', 'Map', 'Axis')
                               if not paths[label].exists()]
                    if missing:
                        raise repo.KbError(f'{rom}: reviewed catalog lacks {missing}', code=3)
                    run(f'{rom} claims', builders['code'].load, rom, paths, root)
                if paths['DiagnosticBinding'].exists():
                    run(f'{rom} bindings', builders['bindings'].load, rom,
                        paths['DiagnosticBinding'], root)
    run('vendor vocabulary', builders['vendor'].load, 'HR',
        root / 'refs/vendor/catalog.csv', root / 'refs/vendor/facts.csv')
    run('reference A2L', builders['a2l'].load, root / A2L, 'HR',
        root / 'refs/vendor/catalog.csv')
    return summary
