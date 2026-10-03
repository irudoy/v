"""Architecture gates reject broken identities before a model is written."""

import copy

import pytest

from kb import checks, compile, repo
from kb.model import Builder, SymbolKey


@pytest.fixture
def model():
    b = Builder(repo.layouts(), compile.spaces(repo.config()),
                {'7mfk': frozenset({0x26740, 0x2642c}),
                 'jk00d': frozenset({0x27344})}, {})
    source = b.symbol('7mfk', 'ram', 0xffff102c, 'fixture')
    result = b.symbol('7mfk', 'ram', 0xffff106a, 'fixture')
    function = b.symbol('7mfk', 'fn', 0x26740, 'fixture')
    b.symbol('7mfk', 'fn', 0x2642c, 'fixture')
    b.symbol('jk00d', 'fn', 0x27344, 'fixture')
    b.props(function, {'level': 'code', 'block': 'calculation/block'}, 'fixture')
    b.entity('stage', 'control', 'fixture')
    b.entity('block', 'calculation', 'fixture', refs={'stage': [('stage', 'control')]})
    b.entity('endpoint', 'observed', 'fixture', refs={
        'block': [('block', 'calculation')], 'registers': [result], 'functions': [function]})
    chain = b.entity('chain', 'calculation', 'fixture', props={'home': '7mfk'},
                     refs={'output': [result]})
    chain.steps = [{'from': source, 'to': result, 'via': [function],
                    'effect': 'converts', 'sign': 'positive'}]
    return b.finish()


def messages(check, model):
    return '\n'.join(issue.message for issue in check(model))


def chain(model):
    return model.entities[('chain', 'calculation')]


def test_a_placed_function_and_logical_ram_endpoint_pass(model):
    assert checks.blocks(model) == []
    assert checks.chains(model) == []


@pytest.mark.parametrize('reference', [[], ['control/stage'], [('block', 'calculation')],
                                       [('stage', 'missing')], [{'stage': 'control'}],
                                       [('stage', {})], [('stage',)]])
def test_a_block_requires_one_declared_stage(model, reference):
    model.entities[('block', 'calculation')].refs['stage'] = reference
    assert 'one declared stage' in messages(checks.blocks, model)


@pytest.mark.parametrize('block', [None, '', 'missing/block', {'name': 'calculation'}])
def test_a_reviewed_function_requires_a_declared_placement(model, block):
    meaning = model.meaning_of(SymbolKey('7mfk', 'fn', 0x26740))
    meaning.props['block'] = block
    assert checks.blocks(model)


def test_the_home_symbol_level_override_requires_a_block(model):
    meaning = model.meaning_of(SymbolKey('7mfk', 'fn', 0x26740))
    meaning.props.pop('block')
    meaning.props['level'] = 'candidate'
    meaning.symbols['7mfk'].props['level'] = 'code'
    assert 'reviewed function needs a block' in messages(checks.blocks, model)


def test_an_unreviewed_function_does_not_gain_a_placement_or_level(model):
    symbol = model.symbols[SymbolKey('7mfk', 'fn', 0x2642c)]
    assert symbol.value('block') is None and symbol.value('level') is None
    assert checks.blocks(model) == []


@pytest.mark.parametrize('reference', [[], ['calculation/block'], [('stage', 'control')],
                                       [('block', 'missing')], [('block', {})]])
def test_an_endpoint_requires_one_declared_block(model, reference):
    model.entities[('endpoint', 'observed')].refs['block'] = reference
    assert 'endpoint needs one declared block' in messages(checks.blocks, model)


@pytest.mark.parametrize(('field', 'member'), [
    ('registers', SymbolKey('7mfk', 'fn', 0x26740)),
    ('functions', SymbolKey('7mfk', 'ram', 0xffff106a)),
    ('functions', SymbolKey('7mfk', 'fn', 0x12340)),
])
def test_endpoint_members_have_the_declared_kind_and_an_actual_symbol(model, field, member):
    model.entities[('endpoint', 'observed')].refs[field] = [member]
    assert f'{field} contain an invalid member' in messages(checks.blocks, model)


def test_an_empty_endpoint_is_rejected(model):
    model.entities[('endpoint', 'observed')].refs.update(registers=[], functions=[])
    assert 'endpoint needs registers or functions' in messages(checks.blocks, model)


def test_a_chain_needs_steps_and_exactly_one_output(model):
    chain(model).steps = []
    chain(model).refs['output'] = []
    text = messages(checks.chains, model)
    assert 'one symbol output' in text and 'ordered steps' in text


@pytest.mark.parametrize(('field', 'value'), [('effect', 'guesses'), ('sign', 'unknown')])
def test_step_effects_and_signs_use_their_vocabularies(model, field, value):
    chain(model).steps[0][field] = value
    assert f'{field} {value!r}' in messages(checks.chains, model)


@pytest.mark.parametrize('field', ['from', 'to', 'via'])
def test_a_chain_cannot_substitute_a_function_of_another_layout(model, field):
    other = SymbolKey('jk00d', 'fn', 0x27344)
    chain(model).steps[0][field] = [other] if field == 'via' else other
    assert 'every reference needs a symbol on 7mfk' in messages(checks.chains, model)


def test_a_chain_refuses_an_unknown_symbol(model):
    chain(model).steps[0]['from'] = SymbolKey('7mfk', 'ram', 0xffff1234)
    assert 'every reference needs a symbol on 7mfk' in messages(checks.chains, model)


def test_via_is_an_ordered_list_of_functions(model):
    step = chain(model).steps[0]
    step['via'] = (SymbolKey('7mfk', 'fn', 0x26740),)
    assert 'via must be an ordered array' in messages(checks.chains, model)
    step['via'] = [step['from']]
    assert 'via must name functions' in messages(checks.chains, model)


def test_repeated_calls_keep_their_order_and_do_not_form_a_dataflow_cycle(model):
    step = chain(model).steps[0]
    first, second = SymbolKey('7mfk', 'fn', 0x26740), SymbolKey('7mfk', 'fn', 0x2642c)
    step['via'] = [first, second, first]
    assert checks.chains(model) == []
    assert step['via'] == [first, second, first]


def test_a_chain_output_must_be_a_destination_rather_than_only_an_input(model):
    chain(model).refs['output'] = [chain(model).steps[0]['from']]
    assert 'output must be a step destination' in messages(checks.chains, model)


def test_a_duplicate_dataflow_pair_is_rejected(model):
    chain(model).steps.append(copy.deepcopy(chain(model).steps[0]))
    assert 'source/destination pair is repeated' in messages(checks.chains, model)


def test_a_dataflow_cycle_is_rejected(model):
    step = copy.deepcopy(chain(model).steps[0])
    step['from'], step['to'] = step['to'], step['from']
    chain(model).steps.append(step)
    assert 'steps form a cycle' in messages(checks.chains, model)
