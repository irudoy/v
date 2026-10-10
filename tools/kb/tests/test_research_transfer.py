"""Bounded immutable-source transfer, idempotence and batch serialization."""

from copy import deepcopy
import json
from types import SimpleNamespace
import tomllib

import pytest

from kb import research, store
from kb.repo import KbError

SOURCE = b'''title = "Probe"
summary = "Every original fact remains explicit."
home = "7mfk"
output = "output/ram"
[[step]]
from = "input/ram"
to = "output/ram"
via = ["first/fn", "first/fn"]
effect = "selects"
sign = "none"
specs = ["defs/probe.md"]
note = "A mode bit selects an alternate source; the mode producer remains unverified."
[[step]]
from = "earlier/ram"
to = "input/ram"
via = ["second/fn"]
effect = "converts"
sign = "positive"
note = "to = from"
'''
PATH = 'kb/chain/probe.toml'
COMMIT = 'a' * 40
GRAMMAR = SimpleNamespace(validate=lambda note: None if note == 'to = from' else 'prose')


def test_complete_source_with_mixed_steps_restores_exactly_without_promoting_claims():
    original = tomllib.loads(SOURCE.decode())
    prepared, count = research.transfer(original, SOURCE, GRAMMAR, COMMIT, PATH)
    assert count == 1
    assert research.restore(prepared) == original
    assert prepared['step'][1] == original['step'][1]
    assert prepared['step'][0]['research']['state'] == 'unresolved'
    assert json.loads(prepared['step'][0]['research']['original']) == original['step'][0]
    assert original == tomllib.loads(SOURCE.decode())
    assert tomllib.loads(store.render('chain', prepared)) == prepared


def test_a_prepared_transfer_is_idempotent_and_keeps_its_source_record():
    first, _ = research.transfer(tomllib.loads(SOURCE.decode()), SOURCE, GRAMMAR, COMMIT, PATH)
    second, count = research.transfer(first, SOURCE, GRAMMAR, COMMIT, PATH)
    assert count == 0
    assert first == second


@pytest.mark.parametrize('key', ['summary', 'home', 'output'])
def test_unrelated_source_metadata_cannot_change_during_a_lossless_transfer(key):
    document = tomllib.loads(SOURCE.decode())
    document[key] = 'different'
    with pytest.raises(KbError, match='immutable transfer source'):
        research.transfer(document, SOURCE, GRAMMAR, COMMIT, PATH)


def test_a_transfer_batch_preserves_all_operation_and_step_fields():
    prepared, _ = research.transfer(tomllib.loads(SOURCE.decode()), SOURCE, GRAMMAR, COMMIT, PATH)
    operations = [{'cmd': 'set', 'ref': 'probe/chain', 'keys': {'step': prepared['step']}}]
    assert tomllib.loads(store.render_batch(operations)) == {'op': operations}


def test_a_rebound_archived_step_cannot_be_hidden_by_restoring_its_old_original():
    prepared, _ = research.transfer(tomllib.loads(SOURCE.decode()), SOURCE, GRAMMAR, COMMIT, PATH)
    changed = deepcopy(prepared)
    changed['step'][0]['via'] = ['first/fn']
    with pytest.raises(KbError, match='binding'):
        research.transfer(changed, SOURCE, GRAMMAR, COMMIT, PATH)


@pytest.mark.parametrize('target', ['outside', 'existing'])
def test_preparation_refuses_unsafe_or_existing_destinations_before_compiling(monkeypatch, tmp_path, target):
    from kb import cli
    def unexpected(*args):
        pytest.fail('a refused destination compiles knowledge')
    monkeypatch.setattr(cli.compile, 'cached', unexpected)
    root = tmp_path / 'repository'
    output = tmp_path / 'outside.toml' if target == 'outside' else root / 'tmp/existing.toml'
    if target == 'existing':
        output.parent.mkdir(parents=True)
        output.write_text('existing artifact')
    with pytest.raises(KbError):
        cli.command_prepare_research(SimpleNamespace(output=str(output), source_commit=COMMIT), root)
    if target == 'existing':
        assert output.read_text() == 'existing artifact'
    else:
        assert not output.exists()
