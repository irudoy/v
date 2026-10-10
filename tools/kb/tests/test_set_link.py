"""Existing-link contracts over independently controlled native sources."""
import contextlib
import copy
import io
from pathlib import Path
from unittest import mock

import pytest

from kb import adapters, cli, compile, convert, mcp, repo, store, write
from kb.adapters import files as file_adapter
from kb.repo import KbError
from tools.kb.tests import selector_sources

pytestmark = pytest.mark.usefixtures('reuse_kb_source_parses')

STATE, FUNCTION = selector_sources.STATE, selector_sources.FUNCTION
SP, FP = selector_sources.STATE_PATH, selector_sources.FUNCTION_PATH
OP = {'cmd': 'set-link', 'meaning': STATE, 'type': 'writer', 'to': FUNCTION,
      'keys': {'note': 'A controlled replacement condition.'}}
DEP = {'role': 'writes', 'to': FUNCTION, 'type': 'writer', 'end': 'owner',
       'relies': 'structure', 'supports': 'identity'}


@pytest.fixture(scope='module')
def baseline(tmp_path_factory):
    root = tmp_path_factory.mktemp('set-link-writer')
    hashes = selector_sources.write_sources(root)
    docs = {path: store.load(root, path) for path in (SP, FP)}
    native_writer(docs[SP])['evidence'] = [
        {'kind': 'spec', 'path': 'defs/fixture.md', 'key': 'controlled_identity'}]
    docs[SP]['ledger'][0]['dependency'].append(copy.deepcopy(DEP))
    next(marker for marker in docs[FP]['ledger'] if marker['registry'] == 'funcs')[
        'dependency'].append({**DEP, 'to': STATE, 'end': 'to'})
    overlay = {path: store.render(path.parent.name, doc) for path, doc in docs.items()}
    model = compile.build(root, overlay, order=(file_adapter,))
    assert set(write.checks.CHECKS) == {
        'schema', 'canonical', 'names', 'references', 'symbols', 'homology',
        'links', 'widths', 'image-bytes', 'statuses', 'writers', 'fields',
        'levels', 'ledgers', 'blocks', 'chains', 'catalog', 'code', 'source-bindings',
    }
    assert write._issues(model) == {}
    frozen = convert.dump(model)
    yield model, docs
    assert convert.dump(model) == frozen
    assert selector_sources.unchanged(root, hashes)


@pytest.fixture(autouse=True)
def native_order(request, monkeypatch):
    if request.node.name == 'test_full_repository_plan_retains_every_untouched_document':
        return
    monkeypatch.setattr(adapters, 'ADAPTERS', (file_adapter,))


def plan(baseline, *ops, docs=None):
    model, _ = baseline
    if docs is not None:
        model = compile.build(model.root, {
            **model.overlay,
            **{path: store.render(path.parent.name, doc) for path, doc in docs.items()}})
    return write.plan(list(ops), model, write.model_resolver(model), model.root)


def native_writer(document):
    return next(link for link in document['link'] if link['type'] == 'writer')


def refuse(baseline, *ops, docs=None, code=3, text=None):
    with pytest.raises(KbError) as caught:
        plan(baseline, *ops, docs=docs)
    assert caught.value.code == code, str(caught.value)
    if text:
        assert text in str(caught.value)


def test_changes_only_one_property_with_all_evidence_and_selectors(baseline):
    model, docs = baseline
    change, texts, result = plan(baseline, OP)
    expected = copy.deepcopy(docs[SP])
    native_writer(expected)['note'] = OP['keys']['note']
    assert texts == {SP: store.render('ram', expected)}
    assert not change.removed and not change.rows_changed
    assert result.overlay[FP] == model.overlay[FP]
    assert write._issues(result) == {}
    before = write.ledger_projection.render(model)
    after = write.ledger_projection.render(result)
    assert before == after


def test_repeated_exact_edit_is_idempotent(baseline):
    _, _, result = plan(baseline, OP, OP)
    _, texts, _ = write.plan([OP], result, write.model_resolver(result), result.root)
    assert texts == {}


def test_unset_preserves_evidence_identity_and_other_properties(baseline):
    _, docs = baseline
    _, texts, _ = plan(baseline, {**OP, 'keys': {}, 'unset': ['note']})
    expected = copy.deepcopy(docs[SP])
    del native_writer(expected)['note']
    assert texts == {SP: store.render('ram', expected)}


def test_multiple_properties_are_one_retained_update(baseline):
    _, docs = baseline
    keys = {'note': 'One atomic edit.', 'layouts': ['7mfk']}
    _, texts, _ = plan(baseline, {**OP, 'keys': keys})
    expected = copy.deepcopy(docs[SP])
    native_writer(expected).update(keys)
    assert texts == {SP: store.render('ram', expected)}


@pytest.mark.parametrize('variant', [
    {'evidence': []}, {'extra': 'x'}, {'selector': []}, {'selector': ''},
    {'keys': []}, {'keys': False}, {'unset': {}}, {'unset': ''}, {'unset': False},
    {'unset': ['note', 'note']}, {'unset': ['note']}, {'unset': ['evidence']},
    {'keys': {}}, {'selector': {'offset': True}}, {'selector': {'offset': 1.0}},
    {'selector': {'offset': -1}}, {'selector': {'slot': []}},
    {'selector': {'note': 'x'}}, {'keys': {'slot': 'x'}},
    {'keys': {'offset': 0}}, {'keys': {'type': 'reader'}}, {'keys': {'to': STATE}},
    {'keys': {'evidence': []}}, {'keys': {'layouts': '7mfk'}},
    {'keys': {'relies': 'unknown'}}, {'keys': {'supports': ['unknown']}},
])
def test_refuses_invalid_input_and_immutable_fields(baseline, variant):
    refuse(baseline, {**OP, **variant}, code=2)


def test_missing_unset_property_is_refused(baseline):
    refuse(baseline, {**OP, 'keys': {}, 'unset': ['via']}, text='no via')


def test_absent_and_zero_offset_are_distinct_native_identities(baseline):
    _, docs = baseline
    docs = copy.deepcopy(docs)
    second = copy.deepcopy(native_writer(docs[SP]))
    second['offset'] = 0
    second['note'] = 'The explicit-zero relation.'
    docs[SP]['link'].append(second)
    _, texts, result = plan(baseline, {**OP, 'selector': {'offset': 0}}, docs=docs)
    edited = store.load(result.root, SP, result.overlay)
    absent = [link for link in edited['link'] if link['type'] == 'writer' and 'offset' not in link]
    assert absent == [native_writer(docs[SP])]
    zero = [link for link in edited['link'] if link.get('offset') == 0]
    assert zero == [{**second, 'note': OP['keys']['note']}]
    assert set(texts) == {SP}


def test_slot_selects_one_existing_relation(baseline):
    _, docs = baseline
    docs = copy.deepcopy(docs)
    native_writer(docs[SP])['slot'] = 'bit0'
    refuse(baseline, OP, docs=docs, text='found 0')
    _, _, result = plan(baseline, {**OP, 'selector': {'slot': 'bit0'}}, docs=docs)
    edited = store.load(result.root, SP, result.overlay)
    assert native_writer(edited)['slot'] == 'bit0'


def test_missing_and_duplicate_native_links_are_refused(baseline):
    _, docs = baseline
    for links, count in (([], 0), ([native_writer(docs[SP])] * 2, 2)):
        candidate = copy.deepcopy(docs)
        candidate[SP]['link'] = copy.deepcopy(links)
        refuse(baseline, OP, docs=candidate, text=f'found {count}')


def test_new_relation_cannot_be_adopted_from_earlier_operation(baseline):
    refuse(baseline,
           {'cmd': 'link', 'meaning': STATE, 'type': 'copy', 'to': 'unrelated_probe/ram',
            'keys': {'layouts': ['7mfk']}},
           {**OP, 'type': 'copy', 'to': 'unrelated_probe/ram'}, text='found 0')


def test_symbol_references_resolve_the_held_meanings(baseline):
    _, expected, _ = plan(baseline, OP)
    _, actual, _ = plan(baseline, {**OP, 'meaning': '7mfk:ffff121a',
                                 'to': '7mfk:000493e8'})
    assert actual == expected


def test_final_batch_refuses_unlink_and_conflicting_replacement(baseline):
    refuse(baseline, OP,
           {'cmd': 'unlink', 'meaning': STATE, 'type': 'writer', 'to': FUNCTION},
           text='updated native link is not retained')
    refuse(baseline, OP, {**OP, 'keys': {'note': 'A contradictory edit.'}},
           text='updated native link is not retained')


def test_final_batch_retains_both_ends_ledger_dependencies(baseline):
    for owner, target in ((STATE, 'capture_copy/fn'), ('unrelated_probe/ram', FUNCTION)):
        refuse(baseline, OP, {'cmd': 'unlink', 'meaning': owner,
                             'type': 'reader' if owner == STATE else 'writer', 'to': target},
               text='does not retain ledger dependencies')


def test_changed_claim_cannot_invalidate_selected_dependencies(baseline):
    for key in ('relies', 'reverse_relies'):
        refuse(baseline, {**OP, 'unset': [key]}, text='owned documents')
    for key in ('supports', 'reverse_supports'):
        refuse(baseline, {**OP, 'keys': {key: 'contract'}}, text='owned documents')


def test_earlier_operations_cannot_replace_identity_or_evidence(baseline):
    unlink = {'cmd': 'unlink', 'meaning': STATE, 'type': 'writer', 'to': FUNCTION}
    link = {**unlink, 'cmd': 'link', 'keys': {'layouts': ['7mfk'],
           'relies': 'structure', 'supports': 'identity',
           'reverse_relies': 'structure', 'reverse_supports': 'identity'}}
    refuse(baseline, unlink, link, OP, text='identity and evidence')


def test_late_refusal_writes_no_file_or_graph(baseline):
    model, _ = baseline
    build = compile.build

    def current_or_result(root, overlay=None, **kwargs):
        return model if overlay is None else build(root, overlay, **kwargs)

    @contextlib.contextmanager
    def fresh(*args, **kwargs):
        yield object()
    with mock.patch.object(write.graph, 'fresh', fresh), \
         mock.patch.object(write.compile, 'build', side_effect=current_or_result), \
         mock.patch.object(write, 'graph_resolver', return_value=write.model_resolver(model)), \
         mock.patch.object(write.store, 'write') as write_file, \
         mock.patch.object(write.graph, 'sync_held') as sync:
        with pytest.raises(KbError):
            write.apply([OP, {'cmd': 'set-link', 'meaning': STATE, 'type': 'writer',
                             'to': FUNCTION, 'keys': {'note': 'Contradiction.'}}], model.root)
    write_file.assert_not_called()
    sync.assert_not_called()


def test_public_apply_dry_run_and_write_use_the_checked_result(baseline):
    model, _ = baseline
    build = compile.build

    def current_or_result(root, overlay=None, **kwargs):
        return model if overlay is None else build(root, overlay, **kwargs)

    @contextlib.contextmanager
    def fresh(*args, **kwargs):
        yield object()

    for dry_run in (True, False):
        with mock.patch.object(write.graph, 'fresh', fresh), \
             mock.patch.object(write.compile, 'build', side_effect=current_or_result), \
             mock.patch.object(write, 'graph_resolver', return_value=write.model_resolver(model)), \
             mock.patch.object(write.store, 'write') as write_file, \
             mock.patch.object(write.graph, 'sync_held') as sync:
            _, texts = write.apply([OP], model.root, dry_run=dry_run)
        assert set(texts) == {SP}
        if dry_run:
            write_file.assert_not_called()
            sync.assert_not_called()
        else:
            write_file.assert_called_once_with(model.root, texts)
            sync.assert_called_once()
            result = sync.call_args.args[3]
            assert write._issues(result) == {}
            assert result.overlay[SP] == texts[SP]


def test_cli_keeps_selectors_separate_from_mutable_keys(baseline):
    model, _ = baseline
    args = cli.build_parser().parse_args([
        'set-link', STATE, 'writer', FUNCTION, 'note=Condition.', 'via=',
        '--offset', '0x20', '--slot', 'bit0', '--dry-run'])
    with mock.patch.object(cli, '_write', return_value=0) as apply:
        assert args.handler(args, root=model.root) == 0
    assert apply.call_args.args == (args, [{
        'cmd': 'set-link', 'meaning': STATE, 'type': 'writer', 'to': FUNCTION,
        'selector': {'slot': 'bit0', 'offset': 32},
        'keys': {'note': 'Condition.'}, 'unset': ['via']}], model.root)
    args = cli.build_parser().parse_args(['set-link', STATE, 'writer', FUNCTION, 'note=Plain.'])
    with mock.patch.object(cli, '_write', return_value=0) as apply:
        args.handler(args)
    assert apply.call_args.args[1][0]['selector'] == {}


def test_cli_and_mcp_batch_take_the_same_primary_writer(baseline, tmp_path):
    model, _ = baseline
    batch = tmp_path / 'set-link.toml'
    batch.write_text('''[[op]]
cmd = "set-link"
meaning = "knock_timing_state/ram"
type = "writer"
to = "knock_function/fn"
[op.keys]
note = "A controlled replacement condition."
''')
    assert write.read_batch(batch) == [OP]
    args = cli.build_parser().parse_args([
        'set-link', STATE, 'writer', FUNCTION, 'note=' + OP['keys']['note'], '--dry-run'])
    stub = mock.Mock(lines=[], diff=mock.Mock(return_value=''))
    with mock.patch.object(write, 'apply', return_value=(stub, {})) as apply, \
         contextlib.redirect_stdout(io.StringIO()):
        args.handler(args, root=model.root)
    assert apply.call_args.args[0][0] == {**OP, 'selector': {}, 'unset': []}
    assert apply.call_args.kwargs['dry_run'] is True
    with mock.patch.object(write, 'apply', return_value=(stub, {})) as apply:
        code, _ = mcp.call('apply', {'batch': str(batch), 'dry_run': True})
    assert code == 0
    assert apply.call_args.args[0] == [OP]
    assert apply.call_args.kwargs['dry_run'] is True
    assert 'kb_set-link' not in {tool['name'] for tool in mcp.tools()}


def test_exact_source_file_reference_does_not_edit_another_owned_file(baseline):
    _, docs = baseline
    docs = copy.deepcopy(docs)
    alias = Path('kb/ram/knock_timing_alias.toml')
    docs[alias] = {'summary': 'A second controlled owned file.',
                   'symbol': copy.deepcopy(docs[SP]['symbol']),
                   'link': [{'type': 'copy', 'to': 'unrelated_probe/ram',
                             'layouts': ['7mfk'], 'note': 'Retain the alias relation.'}]}
    _, texts, result = plan(baseline, {**OP, 'meaning': 'knock_timing_alias/ram',
                                     'type': 'copy', 'to': 'unrelated_probe/ram'}, docs=docs)
    expected = copy.deepcopy(docs[alias])
    expected['link'][0]['note'] = OP['keys']['note']
    assert texts == {alias: store.render('ram', expected)}
    assert result.overlay[SP] == store.render('ram', docs[SP])


def test_no_owned_file_cannot_be_created_by_property_edit(baseline):
    model, _ = baseline
    shallow = copy.copy(model)
    owner, _ = write.model_resolver(model)(STATE)
    shallow.files = {key: value for key, value in model.files.items() if value[0] is not owner}
    with pytest.raises(KbError, match='existing owned file'):
        write.plan([OP], shallow, write.model_resolver(shallow), shallow.root)


def test_full_repository_plan_retains_every_untouched_document():
    model = compile.build(repo.ROOT)
    operation = {**OP, 'keys': {'note': 'Controlled existing-link planning contract.'}}
    change, texts, result = write.plan([operation], model, write.model_resolver(model))
    _, _, path = change._file_of(STATE)
    original = store.load(repo.ROOT, path, model.overlay)
    expected = copy.deepcopy(original)
    selected = [link for link in expected['link']
                if link['type'] == 'writer' and link['to'] == FUNCTION
                and 'slot' not in link and 'offset' not in link]
    assert len(selected) == 1
    selected[0]['note'] = operation['keys']['note']
    assert texts == {path: store.render(path.parent.name, expected)}
    assert not write.refusals(model, result)
    assert write.ledger_projection.render(model) == write.ledger_projection.render(result)


def test_actual_owned_file_write_and_dry_run_are_atomic(baseline, tmp_path):
    _, docs = baseline
    selector_sources.write_sources(tmp_path)
    store.write(tmp_path, {path: store.render(path.parent.name, doc)
                          for path, doc in docs.items()})
    model = compile.build(tmp_path)
    assert write._issues(model) == {}
    before = {path.relative_to(tmp_path): path.read_bytes()
              for path in tmp_path.rglob('*') if path.is_file()}

    @contextlib.contextmanager
    def fresh(*args, **kwargs):
        yield object()

    with mock.patch.object(write.graph, 'fresh', fresh), \
         mock.patch.object(write, 'graph_resolver',
                           side_effect=lambda session, base, *a: write.model_resolver(base)), \
         mock.patch.object(write.graph, 'sync_held') as sync:
        _, dry_texts = write.apply([OP], tmp_path, dry_run=True)
        assert all((tmp_path / path).read_bytes() == data for path, data in before.items())
        sync.assert_not_called()
        _, texts = write.apply([OP], tmp_path)
    assert texts == dry_texts
    assert set(texts) == {SP}
    assert (tmp_path / SP).read_text() == texts[SP]
    assert all((tmp_path / path).read_bytes() == data
               for path, data in before.items() if path != SP)
    sync.assert_called_once()
