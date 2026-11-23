"""Bounded refusal contracts for the compiler's retained graph layers."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import compatibility, fingerprint, graph
from kb.repo import KbError


def test_group_framework_inputs_are_covered_by_common_freshness():
    assert set(compatibility.FRAMEWORK) <= set(fingerprint.inputs())


@pytest.mark.parametrize('failure', ['loader', 'changed-source', None])
def test_freshness_is_published_only_after_complete_exact_construction(monkeypatch, failure):
    events = []
    source = SimpleNamespace(run=lambda query, **params: events.append((query, params)))
    held = fingerprint.Fingerprint('held', {})
    def layers(*args):
        events.append('all layers')
        if failure == 'loader':
            raise KbError('binding source is missing')
        return {'retained': ({'facts': 1}, 0.0, {})}
    monkeypatch.setattr(compatibility, 'load', layers)
    monkeypatch.setattr(fingerprint, 'compute',
                        lambda root: fingerprint.Fingerprint('changed' if failure == 'changed-source' else 'held', {}))
    monkeypatch.setattr(fingerprint, 'head', lambda root: ('commit', {}))
    if failure:
        with pytest.raises(KbError):
            graph.publish(source, 'model', held, Path('/unused'), {}, True)
        assert events == ['all layers']
    else:
        result = graph.publish(source, 'model', held, Path('/unused'), {}, True)
        assert result['retained'][0] == {'facts': 1}
        assert events[0] == 'all layers'
        assert len(events) == 2
        assert events[1][0] == 'CREATE (m:Kb:Meta) SET m = $props'
        assert events[1][1]['props']['fingerprint'] == 'held'


def test_current_graph_reuses_all_layers_without_reconstruction(monkeypatch):
    def unexpected(*args):
        pytest.fail('unchanged graph reconstructs its retained layers')
    monkeypatch.setattr(compatibility, 'load', unexpected)
    held = fingerprint.Fingerprint('held', {})
    monkeypatch.setattr(fingerprint, 'compute', lambda root: held)
    monkeypatch.setattr(fingerprint, 'head', lambda root: ('commit', {}))
    source = SimpleNamespace(run=lambda *args, **kwargs: None)
    assert graph.publish(source, 'model', held, Path('/unused'), {}, False) == {}


def test_publish_passes_structured_progress_to_retained_layers(monkeypatch):
    stages = []
    held = fingerprint.Fingerprint('held', {})
    def layers(*args, progress):
        progress('fixture accesses')
        return {}
    monkeypatch.setattr(compatibility, 'load', layers)
    monkeypatch.setattr(fingerprint, 'compute', lambda root: held)
    monkeypatch.setattr(fingerprint, 'head', lambda root: ('commit', {}))
    source = SimpleNamespace(run=lambda *args, **kwargs: None)
    graph.publish(source, 'model', held, Path('/unused'), {}, True, progress=stages.append)
    assert stages == ['fixture accesses', 'validating source fingerprint']


def test_layer_sources_bind_corpora_and_builders_but_exclude_owned_registry_files(tmp_path):
    for path in ('refs/diagnostics/sample/source_pack.toml',
                 'refs/diagnostics/sample/parameters.csv',
                 'refs/diagnostics/sample/fragments.jsonl',
                 'defs/registries/JK08A.funcs.csv', 'defs/registries/OTHER.funcs.csv'):
        full = tmp_path / path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text('unchanged fixture')
    selected = set(compatibility.inputs(tmp_path))
    assert 'defs/registries/JK08A.funcs.csv' not in selected
    assert 'defs/registries/OTHER.funcs.csv' in selected
    assert 'refs/diagnostics/sample/source_pack.toml' in selected
    assert 'refs/diagnostics/sample/parameters.csv' in selected
    assert 'refs/diagnostics/sample/fragments.jsonl' in selected
    assert compatibility.A2L.as_posix() in selected
    assert set(compatibility.MODULES) <= selected


def test_catalog_paths_are_selected_from_exact_model_views_without_reading_stale_output(tmp_path):
    path = tmp_path / 'defs/registries/JK08A.funcs.csv'
    chosen = Path('/model-view/JK08A.funcs.csv')
    assert compatibility.selected_path({'defs/registries/JK08A.funcs.csv': chosen}, path, tmp_path) == chosen
    assert compatibility.selected_path({}, tmp_path / 'defs/registries/OTHER.funcs.csv', tmp_path) == tmp_path / 'defs/registries/OTHER.funcs.csv'


def test_image_registry_resolves_paths_beside_its_own_catalog(tmp_path):
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from mapkit import rom
    path = tmp_path / 'roms.csv'
    path.write_text('rom,path,sha256\nTEST,nested/image.bin,declared\n')
    rows = rom.registry(path)
    assert rows[0]['path'] == str(tmp_path / 'nested/image.bin')
