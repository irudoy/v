"""A meaning with more than one symbol and none on 7mfk states its home, and a
stated home is the layout of one of its symbols."""

import pytest

from kb import checks, compile, repo
from kb.model import Builder


def model_of(layouts, home=None):
    builder = Builder(repo.layouts(), compile.spaces(repo.config()), {}, {})
    first, *others = [builder.symbol(layout, 'ram', 0xffff1100, 'fixture') for layout in layouts]
    for other in others:
        builder.join(first, other, 'fixture')
    builder.name(first, 'home_probe', 'symbol_key', 'fixture')
    if home is not None:
        builder.props(first, {'home': home}, 'fixture')
    model = builder.finish()
    model.config = repo.config()
    return model, model.meaning_of(first)


@pytest.mark.parametrize('layouts, home', [
    (['jk78c'], None),
    (['7mfk', 'jk78c'], None),
    (['7mfk', 'jk78c'], 'jk78c'),
    (['jk78c', '1nd', '1me3b'], 'jk78c'),
    (['jk00c', 'jk00d'], 'jk00d'),
])
def test_an_accepted_home_passes(layouts, home):
    model, _ = model_of(layouts, home)
    assert checks.schema(model) == []


@pytest.mark.parametrize('layouts, home, message', [
    (['jk78c', '1nd', '1me3b'], None, '3 symbols, none on 7mfk, and no stated home'),
    (['jk00c', 'jk00d'], None, '2 symbols, none on 7mfk, and no stated home'),
    (['jk78c', '1nd'], '1me3b', "home '1me3b' holds no symbol of the meaning"),
    (['jk78c'], '7mfk', "home '7mfk' holds no symbol of the meaning"),
])
def test_a_missing_or_foreign_home_fails(layouts, home, message):
    model, meaning = model_of(layouts, home)
    issues = checks.schema(model)
    assert [(issue.check, issue.subject, issue.message) for issue in issues] == [
        ('schema', meaning.key, message)]
