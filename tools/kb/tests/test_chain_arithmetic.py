"""Arithmetic notation rejects prose without claiming physical correctness."""

import copy

import pytest

from kb import checks, repo
from kb.arithmetic import Grammar
from kb.model import Builder
from kb.repo import KbError


@pytest.fixture
def grammar():
    return Grammar(repo.config())


@pytest.mark.parametrize('note', [
    'ffff114a = floor(0xA2C2 / ffff22bc)',
    'ffff11ea = min(255, ffff11e8 >> 3)',
    'to = from', 'to = int16(from)', 'to = -from + +prev',
    'to = (from & 0xff) | (prev << 8)',
    'to = from ^ ~prev', 'to = clamp(from, -500, 500)',
    'to = median(from[0], from[1], from[2])',
    'K = ffff3998; c = floor(floor(K * 335 / 65536) / min(65535, prev + 80)); to = uint16(from - c)',
    'to = RAM16[0xffff1024] * 128 / ROM16[0x9534]',
    'to = interpolate(0x0000b43a, from, x)',
    'to = lookup(0x00012302, from) + 2.5',
    'to = .5 * from - 1.', 'to = 0Xff',
    'to = min(255, from >> 4) = min(255, ffff1196 >> 7)',
])
def test_equations_follow_the_configured_operators_functions_and_variables(grammar, note):
    assert grammar.validate(note) is None


@pytest.mark.parametrize('note', [
    '', ' ', 'The producer copies the source.',
    'ffff114a = floor(0xA2C2 / ffff22bc) in RPM/12.5',
    'to = from; the gate selects an alternate source',
    'to = from, the working word', 'to = from while x > 0',
    'to = from if x else prev', 'to = from ? x : prev',
    'to = from <= prev', 'to = from != prev', 'to = from == prev',
    'to = from.bit5', 'to = from + missing',
    'to = unknown(from)', 'to = min(from)', 'to = min(from, prev, x)',
    'to = floor()', 'to = ROM16', 'to = ROM16[0x9534',
    'to = (from + prev', 'to = from +', 'to = ;',
    'to = 0xZZ', 'to = 12rpm', 'to = 1..2', 'to = from;',
    'to = 2[0]', 'to = floor(from)[0]', 'to = ROM16[0x9534][0]',
    'to = coefficient * from; coefficient = 128',
    'floor = from', 'ROM16 = from',
])
def test_conditions_prose_and_broken_arithmetic_are_not_equations(grammar, note):
    assert grammar.validate(note)


def test_temporaries_are_local_to_one_note(grammar):
    assert grammar.validate('coefficient = 128; to = coefficient * from') is None
    assert grammar.validate('to = coefficient * from')


def test_configuration_controls_function_arity_and_operator_availability():
    config = copy.deepcopy(repo.config())
    config['chains']['arithmetic']['functions']['lookup'] = 3
    config['chains']['arithmetic']['binary'][-1].remove('%')
    grammar = Grammar(config)
    assert grammar.validate('to = lookup(0x12302, from)')
    assert grammar.validate('to = lookup(0x12302, from, x)') is None
    assert grammar.validate('to = from % 120')


@pytest.mark.parametrize('change', [
    lambda row: row.update(number='['),
    lambda row: row.update(name='.*'),
    lambda row: row.update(binary=[]),
    lambda row: row.update(binary=[['+'], ['+']]),
    lambda row: row.update(binary=[['>']]),
    lambda row: row.update(unary=['if']),
    lambda row: row.update(functions={'floor': True}),
])
def test_malformed_configuration_is_an_explicit_usage_error(change):
    config = copy.deepcopy(repo.config())
    change(config['chains']['arithmetic'])
    with pytest.raises(KbError, match='chains.arithmetic') as refused:
        Grammar(config)
    assert refused.value.code == 2


def test_audit_binds_the_exact_rejected_note_and_does_not_promote_a_claim():
    b = Builder({}, {}, {}, {}, config=repo.config())
    entity = b.entity('chain', 'probe', 'fixture', props={'title': 'Probe'})
    entity.steps = [{'note': 'to = from while the mode is set'}, {'note': 'to = from'}, {}]
    model = b.finish()
    model.config = repo.config()
    issues = checks.audit(model, ('chain-notes',))['chain-notes']
    assert len(issues) == 1
    assert issues[0].subject == 'probe/chain step 1'
    assert repr(entity.steps[0]['note']) in issues[0].message
    entity.steps[0]['via'] = ['a_changed_call/fn']
    assert checks.chain_notes(model)[0] != issues[0]
    entity.steps[0]['note'] = 'to = from while another mode is set'
    assert checks.chain_notes(model)[0] != issues[0]
    assert not model.meanings


def test_excessive_nesting_reports_an_invalid_expression(grammar):
    assert grammar.validate('to = ' + '(' * 2000 + 'from' + ')' * 2000)
