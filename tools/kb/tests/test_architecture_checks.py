"""Architecture gates reject broken identities before a model is written."""

import copy

import pytest

from kb import architecture_projection, checks, compile, repo
from kb.model import Builder, Entity, Link, SymbolKey


@pytest.fixture
def model():
    b = Builder(repo.layouts(), compile.spaces(repo.config()),
                {'7mfk': frozenset({0x26740, 0x2642c}),
                 'jk00d': frozenset({0x27344})}, {},
                config=repo.config(repo.ROOT, {repo.OWNER_CONFIG: None}))
    source = b.symbol('7mfk', 'ram', 0xffff102c, 'fixture')
    result = b.symbol('7mfk', 'ram', 0xffff106a, 'fixture')
    function = b.symbol('7mfk', 'fn', 0x26740, 'fixture')
    b.symbol('7mfk', 'fn', 0x2642c, 'fixture')
    b.symbol('jk00d', 'fn', 0x27344, 'fixture')
    b.props(function, {'level': 'code', 'block': 'calculation/block'}, 'fixture')
    b.entity('stage', 'control', 'fixture', props={
        'title': 'Control', 'summary': 'Control calculations.', 'lane': 'flow'})
    b.entity('block', 'calculation', 'fixture', props={
        'title': 'Calculation', 'summary': 'A fixture calculation.'},
        refs={'stage': [('stage', 'control')]})
    b.entity('endpoint', 'observed', 'fixture', props={
        'title': 'Observed', 'summary': 'A logical observation.',
        'direction': 'output', 'peripheral': 'RAM'}, refs={
        'block': [('block', 'calculation')], 'registers': [result], 'functions': [function]})
    chain = b.entity('chain', 'calculation', 'fixture', props={
        'home': '7mfk', 'title': 'Calculation', 'summary': 'A fixture flow.',
        'quantity': 'Load counts'},
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


def test_jk08a_projection_keeps_its_own_architecture_when_foreign_entities_exist(model):
    baseline = architecture_projection.document(model)
    foreign_function = SymbolKey('jk00d', 'fn', 0x27344)
    model.entities[('block', 'foreign')] = Entity(
        'block', 'foreign', {'home': 'jk00d', 'title': 'Foreign block'},
        {'stage': [('stage', 'control')]})
    model.entities[('endpoint', 'foreign')] = Entity(
        'endpoint', 'foreign', {'title': 'Foreign endpoint'},
        {'block': [('block', 'foreign')], 'functions': [foreign_function]})
    model.entities[('chain', 'foreign')] = Entity(
        'chain', 'foreign', {'home': 'jk00d', 'title': 'Foreign chain'},
        {'output': [foreign_function]})
    model.entities[('endpoint', 'observed')].props['layouts'] = ['7mfk']
    model.entities[('endpoint', 'observed')].refs['functions'].append(foreign_function)
    assert architecture_projection.document(model) == baseline


def test_chain_layouts_admit_its_home_with_other_declared_layouts(model):
    chain(model).props['layouts'] = ['7mfk', 'jk00d']
    assert checks.chains(model) == []


@pytest.mark.parametrize('layouts', [[], ['7mfk', '7mfk'], ['7mfk', 'missing'], ['jk00d']])
def test_chain_layouts_require_distinct_declared_layouts_including_its_home(model, layouts):
    chain(model).props['layouts'] = layouts
    assert 'layouts must' in messages(checks.chains, model)


def test_a_function_result_can_select_an_arithmetic_alternative(model):
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff102c))
    predicate = model.meaning_of(SymbolKey('7mfk', 'fn', 0x26740))
    model.links.append(Link(output, 'selector', predicate, None, None))
    assert checks.links(model) == []


@pytest.mark.parametrize('slot', ['bit5', 'x'])
def test_a_function_result_selector_has_no_bit_or_axis_slot(model, slot):
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff102c))
    predicate = model.meaning_of(SymbolKey('7mfk', 'fn', 0x26740))
    model.links.append(Link(output, 'selector', predicate, slot, None))
    assert 'function-result selector has no bit or axis slot' in messages(checks.links, model)


def test_link_layouts_cover_the_layouts_of_its_evidence(model):
    datum = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff102c))
    reader = model.meaning_of(SymbolKey('7mfk', 'fn', 0x26740))
    link = Link(datum, 'reader', reader, None, None, props={'layouts': ['7mfk']},
                evidence=[{'kind': 'l0', 'at': 'jk00d:00027350'}])
    model.links.append(link)
    assert 'has evidence on jk00d outside its layouts 7mfk' in messages(checks.links, model)
    link.props['layouts'] = ['7mfk', 'jk00d']
    assert checks.links(model) == []


def test_the_entries_of_one_link_join_their_layouts():
    b = Builder(repo.layouts(), compile.spaces(repo.config()),
                {'7mfk': frozenset({0x26740})}, {},
                config=repo.config(repo.ROOT, {repo.OWNER_CONFIG: None}))
    datum = b.symbol('7mfk', 'ram', 0xffff102c, 'fixture')
    reader = b.symbol('7mfk', 'fn', 0x26740, 'fixture')
    b.link(datum, 'reader', reader, 'fixture', props={'layouts': ['7mfk']}, layouts={'7mfk'})
    b.link(datum, 'reader', reader, 'fixture', props={'layouts': ['jk00d']},
           evidence=[{'kind': 'l0', 'at': 'jk00d:00027350'}], layouts={'jk00d'})
    model = b.finish()
    [link] = model.links
    assert (link.props['layouts'], link.stated) == (['7mfk', 'jk00d'], {'7mfk', 'jk00d'})
    assert checks.links(model) == []


@pytest.mark.parametrize(('kind', 'slug', 'field'), [
    ('stage', 'control', 'title'), ('stage', 'control', 'summary'),
    ('stage', 'control', 'lane'), ('block', 'calculation', 'title'),
    ('block', 'calculation', 'summary'), ('endpoint', 'observed', 'title'),
    ('endpoint', 'observed', 'summary'), ('endpoint', 'observed', 'direction'),
    ('endpoint', 'observed', 'peripheral'), ('chain', 'calculation', 'title'),
    ('chain', 'calculation', 'summary'), ('chain', 'calculation', 'quantity'),
])
def test_architecture_entities_require_the_metadata_of_their_view(model, kind, slug, field):
    model.entities[(kind, slug)].props.pop(field)
    check = checks.chains if kind == 'chain' else checks.blocks
    assert f'{field} must be a nonempty string' in messages(check, model)


@pytest.mark.parametrize('value', ['', False, 3, {}, ['text']])
def test_metadata_text_is_a_nonempty_string(model, value):
    chain(model).props['title'] = value
    assert 'title must be a nonempty string' in messages(checks.chains, model)


@pytest.mark.parametrize('value', [0, -1, True, 1.5, '1'])
def test_architecture_order_is_a_positive_integer(model, value):
    chain(model).props['order'] = value
    assert 'order must be a positive integer' in messages(checks.chains, model)


@pytest.mark.parametrize('value', ['missing', {}, False])
def test_architecture_home_names_a_declared_layout(model, value):
    chain(model).props['home'] = value
    assert 'home must name a declared layout' in messages(checks.chains, model)


def test_generic_block_is_a_boolean(model):
    model.entities[('block', 'calculation')].props['generic'] = 'false'
    assert 'generic must be a boolean' in messages(checks.blocks, model)


@pytest.mark.parametrize('value', ['defs/spec.md', [3]])
def test_named_specs_are_an_array_of_paths(model, value):
    chain(model).props['specs'] = value
    assert 'specs must be an array of paths' in messages(checks.chains, model)


def test_specs_use_the_models_repository_root(model, tmp_path):
    model.root = tmp_path
    (tmp_path / 'spec.md').write_text('Fixture specification.')
    chain(model).props['specs'] = ['spec.md']
    chain(model).steps[0]['specs'] = ['spec.md']
    assert checks.chains(model) == []
    chain(model).steps[0]['specs'] = ['missing.md']
    assert 'specs names no repository file' in messages(checks.chains, model)


@pytest.mark.parametrize('absolute', [False, True])
def test_specs_refuse_files_outside_the_repository(model, tmp_path, absolute):
    model.root = tmp_path / 'repo'
    model.root.mkdir()
    outside = tmp_path / 'outside.md'
    outside.write_text('Outside specification.')
    chain(model).props['specs'] = [str(outside) if absolute else '../outside.md']
    assert 'specs names no repository file' in messages(checks.chains, model)


def test_step_notes_are_text(model):
    chain(model).steps[0]['note'] = {'value': 'x'}
    assert 'note must be a string' in messages(checks.chains, model)


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
