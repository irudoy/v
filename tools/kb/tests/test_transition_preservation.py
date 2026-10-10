"""Changed valid claims are refused before any primary application write."""

from contextlib import nullcontext
from copy import deepcopy
import json
from types import SimpleNamespace
from unittest.mock import patch

import pytest

from kb import transition
from kb.model import Meaning, Symbol, SymbolKey
from kb.repo import KbError


def model(root):
    key = SymbolKey('7mfk', 'fn', 0x200)
    meaning = Meaning('fn', 'held_function', semantic=True,
                      props={'summary': 'Existing valid description.'})
    symbol = Symbol(key, name=meaning.name, meaning=meaning,
                    evidence=[dict(kind='l0', supports='identity', at=key.location)])
    meaning.symbols['7mfk'] = symbol
    return SimpleNamespace(root=root, overlay={}, stash={}, entities={},
                           targets={}, links=[], meanings=[meaning], symbols={key: symbol})


@pytest.mark.parametrize('alteration', ['meaning', 'symbol', 'deleted', 'source'])
def test_a_changed_valid_claim_refuses_before_the_primary_write(tmp_path, alteration):
    original = model(tmp_path)
    if alteration == 'source':
        original.meanings[0].tables['source'] = [dict(layout='7mfk', path='defs/held.md',
            sha256='a' * 64, anchor='FUN_00000200')]
    result = deepcopy(original)
    if alteration == 'meaning':
        result.meanings[0].props['summary'] = 'Another valid description.'
    elif alteration == 'symbol':
        next(iter(result.symbols.values())).props['note'] = 'Another valid note.'
    elif alteration == 'deleted':
        result.meanings, result.symbols = [], {}
    else:
        result.meanings[0].tables.pop('source')
    data = dict(version=2, source_commit='a' * 40, fingerprint='fixed',
                compiler_inputs={}, origins={}, texts={
                    'kb/fn/held_function.toml': 'summary = "Another valid description."\n'})
    # Rebinding the modified plan cannot defeat independent fact preservation.
    data['payload_sha256'] = transition.payload_digest(data)
    path = tmp_path / 'plan.json'
    path.write_text(json.dumps(data))
    with patch.object(transition.lock, 'held', return_value=nullcontext()), \
         patch.object(transition, 'head', return_value=data['source_commit']), \
         patch.object(transition.fingerprint, 'compute', return_value=SimpleNamespace(value='fixed')), \
         patch.object(transition.compile, 'build', side_effect=[original, result]), \
         patch.object(transition, 'owned_before', return_value=original), \
         patch.object(transition, 'gated') as gate, \
         patch.object(transition.store, 'write') as writer:
        with pytest.raises(KbError, match='does not preserve'):
            transition.apply(path, tmp_path)
        gate.assert_not_called()
        writer.assert_not_called()


def test_changed_prepared_payload_refuses_before_compilation_or_write(tmp_path):
    data = dict(version=2, source_commit='a' * 40, fingerprint='fixed',
                compiler_inputs={}, origins={}, texts={})
    data['payload_sha256'] = transition.payload_digest(data)
    data['texts']['kb/fn/held_function.toml'] = 'summary = "Changed."\n'
    path = tmp_path / 'plan.json'
    path.write_text(json.dumps(data))
    with patch.object(transition.compile, 'build') as builder, \
         patch.object(transition.store, 'write') as writer:
        with pytest.raises(KbError, match='exact binding'):
            transition.apply(path, tmp_path)
        builder.assert_not_called()
        writer.assert_not_called()


def test_unchanged_model_keeps_existing_claims(tmp_path):
    original = model(tmp_path)
    transition.enforce_preservation(original, deepcopy(original))
