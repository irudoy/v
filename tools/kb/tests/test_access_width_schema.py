"""RAM and register access widths are bit counts, including symbol overrides."""

import pytest

from kb import checks, compile, repo
from kb.model import Builder


@pytest.fixture(params=['ram', 'reg'])
def meaning(request):
    kind = request.param
    address = 0xffff1100 if kind == 'ram' else 0xfffff456
    builder = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
    home = builder.symbol('7mfk', kind, address, 'fixture')
    other = builder.symbol('jk00d', kind, address, 'fixture')
    builder.join(home, other, 'fixture')
    builder.name(home, 'access_probe', 'symbol_key', 'fixture')
    builder.props(home, {'width': 16}, 'fixture')
    builder.keys(other, {'width': 8}, 'fixture')
    model = builder.finish()
    model.config = repo.config()
    return model, model.meaning_of(home)


def props(meaning, scope):
    return meaning.props if scope == 'meaning' else meaning.symbols['jk00d'].props


@pytest.mark.parametrize('scope', ['meaning', 'symbol'])
@pytest.mark.parametrize('width', [8, 16, 32])
def test_bit_widths_pass_for_meanings_and_layout_overrides(meaning, scope, width):
    model, owner = meaning
    props(owner, scope)['width'] = width
    assert checks.schema(model) == []


@pytest.mark.parametrize('scope', ['meaning', 'symbol'])
@pytest.mark.parametrize('width', [1, 2, 4, 64, 0, -8, 8.0, '8', True, False, None, [], {}])
def test_unsupported_widths_and_scalar_types_fail(meaning, scope, width):
    model, owner = meaning
    props(owner, scope)['width'] = width
    issues = checks.schema(model)
    assert len(issues) == 1 and issues[0].check == 'schema'
    assert issues[0].subject == (owner.key if scope == 'meaning' else owner.symbols['jk00d'].key.key)
    assert f'width {width!r} of a {owner.kind} must be 8, 16, or 32 bits' == issues[0].message


def test_undeclared_access_widths_wait_for_independent_reconciliation(meaning):
    model, owner = meaning
    owner.props.pop('width')
    owner.symbols['jk00d'].props.pop('width')
    assert checks.schema(model) == []


def test_field_byte_widths_and_other_meaning_widths_keep_their_own_contracts():
    builder = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
    table = builder.symbol('7mfk', 'tbl', 0xa4aa, 'fixture')
    builder.props(table, {'width': 4}, 'fixture')
    builder.entity('field', 'probe', 'fixture', props={'width': 2, 'origin': 'ecu_ram'})
    model = builder.finish()
    model.config = repo.config()
    assert checks.schema(model) == []
