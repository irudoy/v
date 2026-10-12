"""Exact completion, destructive dependency, and primary publication contracts."""

from contextlib import contextmanager
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import compatibility, compatibility_state as state, fingerprint, graph
from kb.repo import KbError


class Projection:
    """Model only completion storage and the retained builders' owned outputs."""

    def __init__(self):
        self.records = {}
        self.events = []
        self.facts = {}
        self.edges = set()
        self.meta = None
        self.driver = self

    def run(self, query, **params):
        self.events.append((query, deepcopy(params)))
        if query.startswith('MATCH (s:Kb:CompatibilityState) RETURN'):
            return list(deepcopy(self.records).values())
        if query.startswith('MATCH (s:Kb:CompatibilityState {key:$key})'):
            self.records.pop(params['key'], None)
        elif query.startswith('MERGE (s:Kb:CompatibilityState'):
            self.records[params['key']] = deepcopy(params['props'])
        elif query.startswith('MATCH (n:') and 'DETACH DELETE n' in query and 'rom' in params:
            label = query.split(':', 1)[1].split(' ', 1)[0]
            self.facts.pop((params['rom'], label), None)
            self.edges = {edge for edge in self.edges if (params['rom'], label) not in edge}
        elif 'RETURN DISTINCT n.rom AS rom' in query:
            return [{'rom': rom} for rom in sorted({rom for rom, label in self.facts})]
        elif query == 'CREATE (m:Kb:Meta) SET m = $props':
            self.meta = deepcopy(params['props'])
        return []

    def drain(self, query):
        self.events.append((query, {}))
        if query == 'MATCH (n:Kb)':
            self.records.clear()

    def rows(self, query, rows):
        assert not rows
        return 0


def write(path, text='fixture\n'):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_digest_binds_logical_names_bytes_presence_and_arguments(tmp_path):
    left = write(tmp_path / 'first-random-directory/view.csv', 'a,b\n1,2\n')
    right = write(tmp_path / 'second-random-directory/view.csv', left.read_text())
    def digest(path, name='catalog:Func', values=None):
        return state.Inputs(((name, path),), values or {'rom': 'A'}).digest()
    assert digest(left) == digest(right)
    assert digest(left, name='catalog:Reg') != digest(left)
    assert digest(left, values={'rom': 'B'}) != digest(left)
    original = digest(left)
    write(left, 'a,b\n2,1\n')
    assert digest(left) != original
    left.unlink()
    absent = digest(left)
    write(left, '')
    assert digest(left) != absent
    with pytest.raises(KbError, match='duplicate compatibility input'):
        state.Inputs((('same', left), ('same', right)), {}).digest()
    with pytest.raises(KbError, match='missing compatibility input'):
        state.Inputs((('producer', tmp_path / 'missing.py'),), {}, ('producer',)).digest()


def test_failure_invalidates_before_writes_and_preserves_independent_completion(tmp_path):
    source = write(tmp_path / 'input')
    inputs = state.Inputs((('source', source),), {})
    projection = Projection()
    completed = state.Completed(projection, lambda text: None)
    completed.run('rom:A', inputs, lambda captured: None, kind='rom', rom='A')
    completed.run('rom:B', inputs, lambda captured: None, kind='rom', rom='B')
    retained = deepcopy(projection.records['rom:B'])
    write(source, 'changed\n')
    def fail(captured):
        assert 'rom:A' not in projection.records
        assert projection.records['rom:B'] == retained
        raise KbError('loader failure')
    with pytest.raises(KbError, match='loader failure'):
        completed.run('rom:A', inputs, fail, kind='rom', rom='A')
    assert projection.records == {'rom:B': retained}
    resumed = state.Completed(projection, lambda text: None)
    resumed.run('rom:A', inputs, lambda captured: None, kind='rom', rom='A')
    assert set(projection.records) == {'rom:A', 'rom:B'}


@pytest.mark.parametrize('drift', ['bytes', 'arguments', 'inventory'])
def test_drift_never_records_completion(tmp_path, drift):
    source = write(tmp_path / 'source')
    values = {'rom': 'A'}
    files = lambda: tuple((path.name, path) for path in sorted(tmp_path.iterdir()))
    inputs = state.Inputs(files, values)
    projection = Projection()
    def build(captured):
        if drift == 'bytes':
            write(source, 'changed\n')
        elif drift == 'arguments':
            values['rom'] = 'B'
        else:
            write(tmp_path / 'new-file')
    with pytest.raises(KbError, match='inputs change'):
        state.Completed(projection, lambda text: None).run('rom:A', inputs, build,
                                                        kind='rom', rom='A')
    assert not projection.records


def test_captured_bytes_and_arguments_are_immutable_independent_values(tmp_path):
    source = write(tmp_path / 'input', 'A')
    values = {'items': [1, 2]}
    inputs = state.Inputs((('input', source),), values)
    captured = inputs.capture()
    held = captured.digest()
    write(source, 'B')
    values['items'].append(3)
    assert captured.digest() == held
    assert inputs.digest() != held
    with captured.tree(tmp_path, {'input': 'nested/input'}) as root:
        target = root / 'nested/input'
        assert target.read_text() == 'A'
        assert not target.is_symlink()
        assert target.stat().st_ino != source.stat().st_ino
        assert target.stat().st_mode & 0o777 == 0o444
        directory = root
    assert not directory.exists()


def test_captured_tree_refuses_path_escape_and_conflicting_destinations(tmp_path):
    left, right = write(tmp_path / 'left', 'A'), write(tmp_path / 'right', 'B')
    captured = state.Inputs((('left', left), ('right', right)), {}).capture()
    for destination in ('../outside', '/absolute', '.'):
        with pytest.raises(KbError, match='invalid captured input destination'):
            with captured.tree(tmp_path, {'left': destination}):
                pytest.fail('invalid destination is accepted')
    with pytest.raises(KbError, match='conflicting captured input destination'):
        with captured.tree(tmp_path, {'left': 'same', 'right': 'same'}):
            pytest.fail('conflicting bytes are accepted')
    same = state.Inputs((('left', left), ('alias', left)), {}).capture()
    with same.tree(tmp_path, {'left': 'same', 'alias': 'same'}) as root:
        assert (root / 'same').read_text() == 'A'


@dataclass(frozen=True)
class Source:
    target: str
    source: str
    kind: str = 'exact-code'
    target_sha256: str = 'target'
    source_sha256: str = 'source'
    ranges: tuple = ((0, 16),)
    evidence: str = 'fixture'


@pytest.fixture
def cohorts(tmp_path, monkeypatch):
    root = tmp_path
    projection = Projection()
    for name in set(compatibility.FRAMEWORK + compatibility.ROM_CODE
                    + compatibility.CORPUS_CODE + compatibility.EXTERNAL_CODE):
        write(root / name)
    for name in ('.gitmodules', compatibility.A2L.as_posix(), 'refs/vendor/catalog.csv',
                 'refs/vendor/facts.csv', 'defs/rom-inheritance.toml', 'rom-images/roms.csv',
                 'refs/diagnostics/pack/source_pack.toml', 'refs/diagnostics/pack/documents.csv'):
        write(root / name)
    sources = {rom: Source(rom, 'A') for rom in ('A', 'B')}
    paths = {rom: {label: root / f'defs/{rom}.{label}.csv'
                   for label in ('Func', 'Reg', 'Map', 'Axis', 'Interp', 'DiagnosticBinding')}
             for rom in sources}
    for catalogs in paths.values():
        for path in catalogs.values():
            write(path)
    catalog = {}
    layouts = {}
    config = {'l0': {'census': {}}}
    for rom, layout in (('A', 'a'), ('B', 'b')):
        catalog[rom] = SimpleNamespace(path=write(root / f'rom-images/{rom}.bin'))
        layouts[layout] = SimpleNamespace(id=layout, images=[rom])
        outdir = root / 'l0' / layout
        for name in ('funcs.csv', 'calls.csv', 'xrefs.csv', 'accessors.00000001.csv'):
            write(outdir / name)
        write(root / f'tools/ghidra/symbols/{layout}.csv', 'addr,name\n00000001,function\n')
        config['l0']['census'][layout] = {'interp': f'defs/{rom}.Interp.csv'}
    model = SimpleNamespace(layouts=layouts, config=config)
    calls = []
    failure = set()
    mutate = {}
    def loader(label):
        def load(driver, *args):
            rom = args[0] if label not in ('corpus', 'vendor', 'a2l') else None
            calls.append((rom, label))
            if (rom, label) in failure:
                raise KbError(f'{rom} {label} fails')
            if label == 'corpus':
                assert not any(row['kind'] == 'rom' for row in projection.records.values())
                projection.facts = {key: value for key, value in projection.facts.items()
                                    if key[1] != 'DiagnosticBinding'}
                projection.edges = {edge for edge in projection.edges
                                    if not any(part[1] == 'DiagnosticBinding' for part in edge)}
            elif rom:
                assert f'rom:{rom}' not in projection.records
                if label == 'functions':
                    projection.facts[(rom, 'Func')] = {'addr': '00000001', 'community': 1}
                elif label == 'accesses':
                    assert (rom, 'Func') in projection.facts
                    projection.facts[(rom, 'Reg')] = {'addr': 'ffff0000'}
                    projection.edges.add(((rom, 'Func'), (rom, 'Reg')))
                elif label == 'maps':
                    assert (rom, 'Reg') in projection.facts
                    projection.facts[(rom, 'Map')] = {'value': 42}
                    projection.facts[(rom, 'Axis')] = {'value': 12}
                elif label == 'claims':
                    assert (rom, 'Map') in projection.facts
                    projection.facts[(rom, 'Func')]['claim'] = 'reviewed'
                    projection.edges.add(((rom, 'Map'), (rom, 'Func')))
                elif label == 'bindings':
                    projection.facts[(rom, 'DiagnosticBinding')] = {'did': '0100'}
                    projection.edges.add(((rom, 'DiagnosticBinding'), (rom, 'Reg')))
            if (rom, label) in mutate:
                mutate[(rom, label)]()
            return {'facts': 1}
        return load
    builders = {name: SimpleNamespace(load=loader(label)) for name, label in
                (('diagnostics', 'corpus'), ('functions', 'functions'), ('accesses', 'accesses'),
                 ('maps', 'maps'), ('code', 'claims'), ('bindings', 'bindings'),
                 ('vendor', 'vendor'), ('a2l', 'a2l'))}
    builders['sources'] = SimpleNamespace(resolve=lambda rom, path: sources[rom],
                                         verify_image_binding=lambda *args: None,
                                         definition_paths=lambda source, root: paths[source.target])
    builders['maps'].read_registry = lambda path: [{'kernel': 1}]
    builders['maps'].census_path = lambda directory, kernel: str(directory / f'accessors.{kernel:08x}.csv')
    builders['code'].MAP_FIELDS = ['map']
    builders['code'].AXIS_FIELDS = ['axis']
    projected = {f'defs/{rom}.Interp.csv': catalogs['Interp'] for rom, catalogs in paths.items()}
    @contextmanager
    def views(model, root):
        yield projected
    monkeypatch.setattr(compatibility, 'check_reference', lambda root: 'pinned')
    monkeypatch.setattr(compatibility, 'modules', lambda root: builders)
    monkeypatch.setattr(compatibility, 'views', views)
    monkeypatch.setattr(compatibility.repo, 'images', lambda root: {
        rom: SimpleNamespace(path=root / image.path.relative_to(tmp_path))
        for rom, image in catalog.items()})
    return SimpleNamespace(root=root, graph=projection, model=model, calls=calls,
                           failure=failure, mutate=mutate, paths=paths, sources=sources,
                           projected=projected,
                           builders=builders,
                           load=lambda: compatibility.load(projection, model, root, lambda text: None))


def test_changed_common_fingerprint_reuses_all_cohorts_and_exact_outputs(cohorts, monkeypatch):
    c = cohorts
    first = c.load()
    assert len(first) == 13
    assert set(c.graph.records) == {'diagnostic corpus', 'rom:A', 'rom:B', 'external vocabularies'}
    original = deepcopy((c.graph.facts, c.graph.edges, c.graph.records))
    c.calls.clear()
    # store.py is a common compiler input, while exact rendered cohort inputs
    # remain identical. Publication must exercise load(), not unchanged Meta.
    write(c.root / 'tools/kb/src/kb/store.py', 'changed source-only compiler input\n')
    changed = fingerprint.Fingerprint('different common fingerprint', {})
    monkeypatch.setattr(fingerprint, 'compute', lambda root: changed)
    monkeypatch.setattr(fingerprint, 'head', lambda root: ('commit', {}))
    assert graph.publish(c.graph, c.model, changed, c.root, {}, True, lambda text: None) == {}
    assert c.calls == []
    assert (c.graph.facts, c.graph.edges, c.graph.records) == original
    assert c.graph.meta['fingerprint'] == changed.value


@pytest.mark.parametrize('dependency', ['l0', 'image', 'names', 'catalog', 'census', 'source-model'])
def test_only_the_changed_rom_cohort_reloads(cohorts, dependency):
    c = cohorts
    c.load()
    c.calls.clear()
    if dependency == 'l0':
        write(c.root / 'l0/b/xrefs.csv', 'changed\n')
    elif dependency == 'image':
        write(c.root / 'rom-images/B.bin', 'changed\n')
    elif dependency == 'names':
        write(c.root / 'tools/ghidra/symbols/b.csv', 'addr,name\n00000001,renamed\n')
    elif dependency == 'catalog':
        write(c.paths['B']['Func'], 'changed\n')
    elif dependency == 'census':
        write(c.root / 'l0/b/accessors.00000001.csv', 'changed\n')
    else:
        c.sources['B'] = Source('B', 'A', evidence='different evidence')
    retained = deepcopy((c.graph.facts[('A', 'Func')], c.graph.records['rom:A']))
    c.load()
    assert c.calls == [('B', name) for name in ('functions', 'accesses', 'maps', 'claims', 'bindings')]
    assert (c.graph.facts[('A', 'Func')], c.graph.records['rom:A']) == retained


def test_shared_image_and_producer_changes_reload_all_affected_roms(cohorts):
    c = cohorts
    c.load()
    for path in ('rom-images/A.bin', 'tools/memgraph/load_xrefs.py'):
        c.calls.clear()
        write(c.root / path, f'changed {path}\n')
        c.load()
        assert c.calls == [(rom, name) for rom in ('A', 'B')
                           for name in ('functions', 'accesses', 'maps', 'claims', 'bindings')]


def test_owned_views_ignore_stale_projection_and_temporary_directory_identity(cohorts):
    c = cohorts
    view = write(c.root / 'scratch-one/Func.csv', 'current model\n')
    c.projected['defs/B.Func.csv'] = view
    c.load()
    c.calls.clear()
    write(c.paths['B']['Func'], 'stale generated projection\n')
    c.projected['defs/B.Func.csv'] = write(c.root / 'scratch-two/Func.csv', view.read_text())
    assert c.load() == {}
    assert c.calls == []
    write(c.projected['defs/B.Func.csv'], 'different current model\n')
    c.load()
    assert c.calls == [('B', name) for name in ('functions', 'accesses', 'maps', 'claims', 'bindings')]


def test_shared_canonical_view_rebuilds_every_inheriting_rom(cohorts):
    c = cohorts
    c.paths['B'] = c.paths['A']
    c.load()
    c.calls.clear()
    write(c.paths['A']['Func'], 'changed shared reviewed claims\n')
    c.load()
    assert c.calls == [(rom, name) for rom in ('A', 'B')
                       for name in ('functions', 'accesses', 'maps', 'claims', 'bindings')]


@pytest.mark.parametrize('reset', ['missing-marker', 'changed-bytes'])
def test_corpus_reset_rebuilds_bindings_even_when_its_bytes_are_unchanged(cohorts, reset):
    c = cohorts
    c.load()
    original = deepcopy((c.graph.facts, c.graph.edges))
    c.calls.clear()
    if reset == 'missing-marker':
        c.graph.records.pop('diagnostic corpus')
    else:
        write(c.root / 'refs/diagnostics/pack/documents.csv', 'changed\n')
    c.load()
    assert c.calls == [(None, 'corpus')] + [(rom, name) for rom in ('A', 'B')
                                           for name in ('functions', 'accesses', 'maps', 'claims', 'bindings')]
    assert (c.graph.facts, c.graph.edges) == original


def test_failed_rom_resumes_without_repeating_completed_groups(cohorts):
    c = cohorts
    c.failure.add(('B', 'accesses'))
    with pytest.raises(KbError, match='B accesses fails'):
        c.load()
    assert set(c.graph.records) == {'diagnostic corpus', 'rom:A'}
    retained = deepcopy(c.graph.records['rom:A'])
    c.failure.clear()
    c.calls.clear()
    c.load()
    assert c.calls == [('B', name) for name in ('functions', 'accesses', 'maps', 'claims', 'bindings')] + [
        (None, 'vendor'), (None, 'a2l')]
    assert c.graph.records['rom:A'] == retained


def test_failed_a2l_resumes_the_whole_external_group_and_retains_roms(cohorts):
    c = cohorts
    c.failure.add((None, 'a2l'))
    with pytest.raises(KbError, match='a2l fails'):
        c.load()
    retained = deepcopy(c.graph.records)
    assert set(retained) == {'diagnostic corpus', 'rom:A', 'rom:B'}
    c.failure.clear()
    c.calls.clear()
    c.load()
    assert c.calls == [(None, 'vendor'), (None, 'a2l')]
    assert all(c.graph.records[key] == row for key, row in retained.items())


def test_final_common_source_drift_refuses_meta_but_retains_exact_cohorts(cohorts, monkeypatch):
    c = cohorts
    held = fingerprint.Fingerprint('before', {})
    changed = fingerprint.Fingerprint('after', {})
    monkeypatch.setattr(fingerprint, 'compute', lambda root: changed)
    monkeypatch.setattr(fingerprint, 'head', lambda root: ('commit', {}))
    with pytest.raises(KbError, match='Meta is absent'):
        graph.publish(c.graph, c.model, held, c.root, {}, True, lambda text: None)
    assert c.graph.meta is None
    retained = deepcopy(c.graph.records)
    c.calls.clear()
    graph.publish(c.graph, c.model, changed, c.root, {}, True, lambda text: None)
    assert c.calls == []
    assert c.graph.records == retained
    assert c.graph.meta['fingerprint'] == changed.value


def test_corpus_inventory_drift_refuses_before_any_rom_is_accepted(cohorts):
    c = cohorts
    c.mutate[(None, 'corpus')] = lambda: write(c.root / 'refs/diagnostics/new/source_pack.toml')
    with pytest.raises(KbError, match='inputs change'):
        c.load()
    assert c.graph.records == {}
    assert c.calls == [(None, 'corpus')]


@pytest.mark.parametrize('layer', ['corpus', 'functions', 'accesses', 'maps', 'claims', 'bindings', 'vendor', 'a2l'])
def test_every_builder_consumes_captured_inputs_during_live_mutation_and_restore(cohorts, layer):
    c = cohorts
    c.load()
    c.calls.clear()
    locations = {
        'corpus': ('diagnostics', 'refs/diagnostics/pack/documents.csv'),
        'functions': ('functions', 'l0/b/funcs.csv'),
        'accesses': ('accesses', 'l0/b/xrefs.csv'),
        'maps': ('maps', 'rom-images/B.bin'),
        'claims': ('code', 'defs/B.Func.csv'),
        'bindings': ('bindings', 'defs/B.DiagnosticBinding.csv'),
        'vendor': ('vendor', 'refs/vendor/catalog.csv'),
        'a2l': ('a2l', compatibility.A2L.as_posix()),
    }
    builder, relative = locations[layer]
    live = c.root / relative
    checkpoint = ('diagnostic corpus' if layer == 'corpus' else
                  'external vocabularies' if layer in ('vendor', 'a2l') else 'rom:B')
    c.graph.records.pop(checkpoint)
    original = c.builders[builder].load
    consumed = []
    def transient(driver, *args):
        target = None
        if layer == 'corpus':
            target = args[0] / 'pack/documents.csv'
        elif args[0] == 'B' or layer in ('vendor', 'a2l'):
            target = {
                'functions': lambda: args[1] / 'funcs.csv',
                'accesses': lambda: args[1] / 'xrefs.csv',
                'maps': lambda: args[-1] / 'rom-images/B.bin',
                'claims': lambda: args[1]['Func'],
                'bindings': lambda: args[1],
                'vendor': lambda: args[1],
                'a2l': lambda: args[0],
            }[layer]()
        if target:
            before = live.read_bytes()
            live.write_bytes(b'transient incompatible bytes\n')
            consumed.append(target.read_bytes())
            live.write_bytes(before)
            assert target != live
            assert consumed[-1] == before
        return original(driver, *args)
    c.builders[builder].load = transient
    c.load()
    assert consumed
    assert checkpoint in c.graph.records


def test_an_unexpected_census_rebuilds_and_preserves_the_actual_builder_refusal(cohorts):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from memgraph import load_maps

    c = cohorts
    entry = dict(kernel='00000001', wrapper='00000002', family='1d', width='2', height='',
                 step='', storagetype='uint16', axistype_x='uint16', axistype_y='')
    c.builders['maps'].read_registry = lambda path: [entry]
    c.builders['maps'].census_path = load_maps.census_path
    for layout in ('a', 'b'):
        (c.root / f'l0/{layout}/accessors.00000001.csv').unlink()
        write(c.root / f'l0/{layout}/accessors.1.csv', 'wrapper\n00000002\n')
    original = c.builders['maps'].load
    def checked(driver, rom, outdir, registry, *args):
        load_maps.read_censuses(outdir, [entry], registry)
        return original(driver, rom, outdir, registry, *args)
    c.builders['maps'].load = checked
    c.load()
    retained = deepcopy(c.graph.records['rom:A'])
    c.calls.clear()
    write(c.root / 'l0/b/accessors.2.csv', 'unexpected\n')
    with pytest.raises(SystemExit, match='censuses outside the registry: accessors.2.csv'):
        c.load()
    assert c.calls == [('B', 'functions'), ('B', 'accesses')]
    assert 'rom:B' not in c.graph.records
    assert c.graph.records['rom:A'] == retained
    assert c.graph.meta is None


def test_absent_optional_catalogs_remove_previous_outputs_and_bind_presence(cohorts):
    c = cohorts
    c.load()
    c.calls.clear()
    c.model.config['l0']['census'].pop('b')
    c.paths['B']['Func'].unlink()
    c.paths['B']['DiagnosticBinding'].unlink()
    c.load()
    assert c.calls == [('B', 'functions'), ('B', 'accesses')]
    assert ('B', 'Map') not in c.graph.facts
    assert ('B', 'Axis') not in c.graph.facts
    assert ('B', 'DiagnosticBinding') not in c.graph.facts
    assert 'claim' not in c.graph.facts[('B', 'Func')]
    assert not any((('B', 'Map'), ('B', 'Func')) == edge for edge in c.graph.edges)


def test_external_dependencies_rebuild_vendor_and_a2l_together(cohorts):
    c = cohorts
    c.load()
    c.calls.clear()
    write(c.root / 'refs/vendor/catalog.csv', 'changed\n')
    c.load()
    assert c.calls == [(None, 'vendor'), (None, 'a2l')]


def test_removed_rom_is_cleaned_even_without_its_checkpoint(cohorts):
    c = cohorts
    c.load()
    c.graph.records.pop('rom:B')
    c.model.layouts.pop('b')
    c.calls.clear()
    c.load()
    assert c.calls == []
    assert not any(rom == 'B' for rom, label in c.graph.facts)
    assert not any(any(part[0] == 'B' for part in edge) for edge in c.graph.edges)


def test_force_full_native_load_clears_completion_before_compatibility(monkeypatch, tmp_path):
    projection = Projection()
    projection.records['rom:A'] = {'key': 'rom:A', 'kind': 'rom'}
    model = SimpleNamespace(layouts={}, spaces={})
    held = fingerprint.Fingerprint('full', {})
    monkeypatch.setattr(graph, 'ensure_schema', lambda source: None)
    monkeypatch.setattr(graph, 'meta', lambda source: None)
    monkeypatch.setattr(graph, 'structure_rows', lambda model, root: ({key: [] for key in ('Family', 'Image', 'Layout')}, []))
    monkeypatch.setattr(graph.repo, 'images', lambda root: {})
    monkeypatch.setattr(graph, 'claim_rows', lambda model: dict(
        meanings=[], symbols=[], has=[], links={}, symbol_links={}, statuses=[], analogs=[],
        cites={}, entities=[], steps=[], entity_links={}, targets=[]))
    monkeypatch.setattr(graph.retirement, 'nodes', lambda model: [])
    monkeypatch.setattr(graph, 'at_rows', lambda model: {})
    def load(*args):
        assert not projection.records
        return {}
    monkeypatch.setattr(compatibility, 'load', load)
    monkeypatch.setattr(fingerprint, 'compute', lambda root: held)
    monkeypatch.setattr(fingerprint, 'head', lambda root: ('commit', {}))
    graph.load(projection, model, held, tmp_path, full=True, log=lambda text: None)
    assert state.LABEL in graph.LABELS
    assert state.LABEL not in graph.CLAIM_LABELS
    assert projection.meta['fingerprint'] == held.value
