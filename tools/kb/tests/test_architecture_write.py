"""Native batches replace ordered steps and refuse invalid chain writes."""

import contextlib
import copy
import tomllib
from unittest import mock

import pytest

from kb import compile, repo, store, write
from kb.repo import KbError


CHAIN = 'engine_speed/chain'
CHAIN_FILE = store.path_of('chain', 'engine_speed')


@pytest.fixture(scope='module')
def model():
    return compile.build(repo.ROOT)


@pytest.fixture
def document():
    return copy.deepcopy(store.load(repo.ROOT, CHAIN_FILE))


def assign(keys, ref=CHAIN):
    return {'cmd': 'set', 'ref': ref, 'keys': keys}


def plan(model, *ops):
    return write.plan(list(ops), model, write.model_resolver(model))


def replacement(document):
    step = copy.deepcopy(document['step'][0])
    first = step['via'][0]
    step['via'] = [first, document['step'][6]['via'][-1], first]
    step['note'] = 'to = from'
    return {'output': step['to'], 'step': [step]}


def condition():
    return {'cmd': 'link', 'meaning': 'rpm/ram', 'type': 'selector',
            'to': 'fuel_inhibit/ram',
            'keys': {'slot': 'probe', 'note': 'Use the alternate input while the probe is set.'}}


def test_step_replacement_preserves_call_order_and_removes_held_steps(model, document):
    keys = replacement(document)
    _, texts, result = plan(model, assign(keys))
    changed = tomllib.loads(texts[CHAIN_FILE])
    assert changed['step'] == keys['step']
    assert changed['output'] == keys['output']
    assert {key: value for key, value in changed.items() if key not in keys} == {
        key: value for key, value in document.items() if key not in keys}
    before = model.entities[('chain', 'engine_speed')].steps
    expected = [before[0]['via'][0], before[6]['via'][-1], before[0]['via'][0]]
    assert result.entities[('chain', 'engine_speed')].steps[0]['via'] == expected


def test_new_and_set_start_a_complete_chain_in_one_batch(model, document):
    keys = {**replacement(document), 'title': 'Probe chain',
            'summary': 'A capture step with repeated calls.', 'quantity': 'Capture counts',
            'home': '7mfk', 'order': max(entity.props.get('order', 0)
                for (kind, _), entity in model.entities.items() if kind == 'chain') + 1}
    _, texts, result = plan(model, {'cmd': 'new', 'kind': 'chain', 'slug': 'probe_chain'},
                             assign(keys, 'probe_chain/chain'))
    path = store.path_of('chain', 'probe_chain')
    assert tomllib.loads(texts[path]) == keys
    entity = result.entities[('chain', 'probe_chain')]
    before = model.entities[('chain', 'engine_speed')].steps
    assert entity.refs['output'] == [before[0]['to']]
    assert len(entity.steps) == 1
    assert entity.steps[0]['from'] == before[0]['from']
    assert entity.steps[0]['to'] == before[0]['to']
    assert entity.steps[0]['via'] == [before[0]['via'][0], before[6]['via'][-1],
                                      before[0]['via'][0]]
    assert result.entities[('chain', 'engine_speed')].steps == before
    assert ('chain', 'probe_chain') not in model.entities


def test_one_batch_replaces_steps_and_adds_a_typed_condition(model, document):
    _, texts, result = plan(model, assign(replacement(document)), condition())
    assert set(texts) == {CHAIN_FILE, store.path_of('ram', 'rpm')}
    links = tomllib.loads(texts[store.path_of('ram', 'rpm')])['link']
    assert {'type': 'selector', 'to': 'fuel_inhibit/ram',
            **condition()['keys']} in links
    rpm = next(meaning for meaning in result.meanings if meaning.key == 'rpm/ram')
    before = next(meaning for meaning in model.meanings if meaning.key == 'rpm/ram')
    assert rpm.props.get('level') == before.props.get('level')


def test_unset_refuses_the_required_chain_summary(model):
    with pytest.raises(KbError) as refused:
        plan(model, {'cmd': 'set', 'ref': CHAIN, 'unset': ['summary']})
    assert refused.value.code == 3
    assert 'summary must be a nonempty string' in str(refused.value)


@pytest.mark.parametrize(('home', 'code'), [({}, 2), ([], 2), (False, 2),
                                           ('no_layout_fixture', 3)])
def test_invalid_home_is_refused_before_reference_resolution(model, home, code):
    with pytest.raises(KbError) as refused:
        plan(model, assign({'home': home}))
    assert refused.value.code == code
    assert ('home is a string' if code == 2 else 'home must name a declared layout') \
        in str(refused.value)


@pytest.mark.parametrize(('keys', 'message'), [
    ({'order': []}, 'order is an integer'),
    ({'order': True}, 'order is an integer'),
    ({'summary': {}}, 'summary is a string'),
    ({'specs': {}}, 'specs is an array of strings'),
])
def test_typed_metadata_is_checked_before_canonical_omission(model, keys, message):
    with pytest.raises(KbError) as refused:
        plan(model, assign(keys))
    assert refused.value.code == 2
    assert message in str(refused.value)


@pytest.mark.parametrize(('steps', 'message'), [
    ({'from': 'rpm/ram'}, 'step is an array of tables'),
    (['rpm/ram'], 'step is a table'),
    ([{'unknown': 'rpm/ram'}], 'step takes no unknown'),
])
def test_step_values_must_match_the_array_schema(model, steps, message):
    with pytest.raises(KbError) as refused:
        plan(model, assign({'step': steps}))
    assert refused.value.code == 2
    assert message in str(refused.value)


@pytest.mark.parametrize(('problem', 'message'), [
    ('empty', 'a chain needs ordered steps'),
    ('repeated', 'a source/destination pair is repeated'),
    ('cycle', 'steps form a cycle'),
    ('foreign', 'every reference needs a symbol on 7mfk'),
    ('data_via', 'via must name functions'),
    ('unknown', 'no_chain_input_fixture'),
    ('output', 'the output must be a step destination'),
])
def test_invalid_step_replacements_fail_model_checks(model, document, problem, message):
    keys = replacement(document)
    step = keys['step'][0]
    if problem == 'empty':
        keys['step'] = []
    elif problem == 'repeated':
        keys['step'].append(copy.deepcopy(step))
    elif problem == 'cycle':
        keys['step'].append({**step, 'from': step['to'], 'to': step['from']})
    elif problem == 'foreign':
        step['via'] = ['accelerator_pedal_pair_selector/fn/jk78c-0008d384']
    elif problem == 'data_via':
        step['via'] = [step['from']]
    elif problem == 'unknown':
        step['from'] = 'no_chain_input_fixture/ram'
    elif problem == 'output':
        keys['output'] = step['from']
    with pytest.raises(KbError) as refused:
        plan(model, assign(keys))
    assert refused.value.code == 3
    assert message in str(refused.value)


def test_invalid_chain_prevents_condition_files_and_graph_writes(model):
    with mock.patch.object(write.lock, 'held', return_value=contextlib.nullcontext()), \
            mock.patch.object(write.graph, 'fresh',
                              return_value=contextlib.nullcontext('session')), \
            mock.patch.object(write, 'graph_resolver', side_effect=
                              lambda session, base, root, log: write.model_resolver(base)), \
            mock.patch.object(write.store, 'write') as written, \
            mock.patch.object(write.graph, 'sync_held') as synced:
        with pytest.raises(KbError) as refused:
            write.apply([condition(), assign({'step': []})])
    assert refused.value.code == 3
    assert 'a chain needs ordered steps' in str(refused.value)
    written.assert_not_called()
    synced.assert_not_called()


@pytest.mark.parametrize('note', [
    'to = from while the gate is clear', 'to = min(from)',
    'to = from; use alternate input', 'to = lookup(from, selected)',
])
def test_new_prose_and_malformed_arithmetic_refuse_the_complete_batch(model, document, note):
    keys = replacement(document)
    keys['step'][0]['note'] = note
    with mock.patch.object(write.lock, 'held', return_value=contextlib.nullcontext()), \
            mock.patch.object(write.graph, 'fresh',
                              return_value=contextlib.nullcontext('session')), \
            mock.patch.object(write, 'graph_resolver', side_effect=
                              lambda session, base, root, log: write.model_resolver(base)), \
            mock.patch.object(write.store, 'write') as written, \
            mock.patch.object(write.graph, 'sync_held') as synced:
        with pytest.raises(KbError) as refused:
            write.apply([condition(), assign(keys)])
    assert refused.value.code == 3
    assert 'chain-notes' in str(refused.value)
    assert repr(note) in str(refused.value)
    written.assert_not_called()
    synced.assert_not_called()


def test_held_prose_remains_reported_without_blocking_an_unrelated_metadata_edit(model):
    _, texts, result = plan(model, assign({'summary': 'A checked description of engine speed.'}))
    assert tomllib.loads(texts[CHAIN_FILE])['step'] == store.load(repo.ROOT, CHAIN_FILE)['step']
    assert not write.refusals(model, result)


def test_a_changed_step_cannot_reuse_a_held_prose_rejection(model, document):
    steps = copy.deepcopy(document['step'])
    steps[0]['via'] = document['step'][3]['via']
    with pytest.raises(KbError) as refused:
        plan(model, assign({'step': steps}))
    assert refused.value.code == 3
    assert 'chain-notes' in str(refused.value)
    assert 'engine_speed/chain step 1' in str(refused.value)
