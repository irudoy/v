"""Fixed inactive-owner, incoming-consumer and permanent-name contracts."""

from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace
import tomllib

import pytest

from kb import cli, names, refs, retirement, store, write
from kb.adapters import files
from kb.model import Builder, Entity
from kb.repo import KbError


def source_model(tmp_path):
    path = Path('kb/block/unused.toml')
    document = {'title': 'Unused block', 'summary': 'Preserved context.'}
    store.write(tmp_path, {path: store.render('block', document)})
    entity = Entity('block', 'unused', props=deepcopy(document), sources={path.as_posix()})
    model = SimpleNamespace(root=tmp_path, overlay={}, names=[],
                            entities={('block', 'unused'): entity}, meanings=[],
                            symbols={}, files={}, file_names={}, targets={}, links=[], stash={})
    return model, path, document


def test_retirement_keeps_the_entire_owner_and_emits_only_the_inactive_index(tmp_path):
    model, path, original = source_model(tmp_path)
    change = write.Change(model, None, tmp_path)
    change.run({'cmd': 'retire', 'ref': 'unused/block'})
    texts = change.texts()
    assert tomllib.loads(texts[path]) == {**original, 'retired': True}
    assert tomllib.loads((tmp_path / path).read_text()) == original
    builder = Builder({}, {}, {}, {}, {})
    builder.overlay = texts
    files.declare(builder, tmp_path)
    result = builder.finish()
    assert result.entities == {} and result.symbols == {} and result.meanings == []
    assert names.reserved(result, []) == {'unused'}
    assert retirement.nodes(result)[0]['key'] == 'unused/block'
    assert change.expected[0](result) is None


@pytest.mark.parametrize('consumer', ['registry', 'designed-reference', 'catalog-selector'])
def test_remaining_consumers_refuse_before_any_source_write(tmp_path, consumer):
    model, path, original = source_model(tmp_path)
    entity = model.entities['block', 'unused']
    if consumer == 'registry':
        entity.sources.add('defs/legacy-source.toml')
    elif consumer == 'designed-reference':
        model.entities['endpoint', 'reader'] = Entity('endpoint', 'reader',
                                                     refs={'block': [('block', 'unused')]})
    else:
        entity.props['catalog'] = [{'original': 'retained'}]
    with pytest.raises(KbError) as error:
        write.Change(model, None, tmp_path).run({'cmd': 'retire', 'ref': 'unused/block'})
    assert error.value.code == 3
    assert tomllib.loads((tmp_path / path).read_text()) == original


def test_all_generated_former_and_semantic_names_remain_reserved():
    document = {'retired': True, 'former': ['old_meaning'], 'symbol': [
        {'layout': 'home', 'address': '00000100', 'name': 'quiet-mouse',
         'former': ['small-bird/fn/home-00000100']}]}
    model = SimpleNamespace(stash={'retired': [('fn', 'meaning', document, 'kb/fn/meaning.toml')]},
                            file_names={}, meanings=[], entities={})
    assert names.reserved(model, []) == {'meaning', 'old_meaning', 'quiet-mouse', 'small-bird'}
    node = retirement.nodes(model)[0]
    assert 'small-bird/fn/home-00000100' in node['references']


@pytest.mark.parametrize('mutation', ['remove', 'reactivate', 'rewrite'])
def test_inactive_owner_cannot_leave_or_change_through_a_generic_batch(mutation):
    record = ('block', 'unused', {'retired': True, 'title': 'Preserved'}, 'kb/block/unused.toml')
    before = SimpleNamespace(stash={'retired': [record]})
    after = SimpleNamespace(stash={'retired': [deepcopy(record)]})
    if mutation != 'rewrite':
        after.stash['retired'] = []
    else:
        after.stash['retired'][0][2]['title'] = 'Changed'
    assert retirement.preserved(before, after)
    assert retirement.preserved(before, before) == []


def test_inactive_reference_reports_the_reserved_identity():
    graph = SimpleNamespace(run=lambda *args, **kwargs: [{'key': 'unused/block'}])
    with pytest.raises(KbError) as error:
        refs._retired(graph, 'unused')
    assert error.value.code == 5
    assert 'retired' in str(error.value) and 'reserved' in str(error.value)
    assert cli.build_parser().parse_args(['retire', 'unused/block', '--dry-run']).dry_run
