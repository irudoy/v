"""Explicit withdrawal of ledger selectors for vanished function entries."""

from contextlib import nullcontext
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import tomllib

import pytest

from kb import cli, fingerprint, l0, names, retirement, store, write
from kb.adapters import files
from kb.model import Builder, Entity, Meaning, Symbol, SymbolKey
from kb.repo import KbError


def source_model(tmp_path):
    path = Path('kb/fn/discarded-copy.toml')
    document = {'role': 'service', 'ledger': [
        {'registry': 'funcs', 'order': 36, 'fields': ['role']}],
        'symbol': [{'layout': 'home', 'address': '00000100', 'name': 'discarded-copy'}]}
    store.write(tmp_path, {path: store.render('fn', document)})
    key = SymbolKey('home', 'fn', 0x100)
    symbol = Symbol(key, sources={path.as_posix()}, implicit=False, name='discarded-copy')
    meaning = Meaning('fn', name='discarded-copy', symbols={'home': symbol}, sources={path.as_posix()})
    symbol.meaning = meaning
    model = SimpleNamespace(root=tmp_path, overlay={}, names=[], entities={}, meanings=[meaning],
        symbols={key: symbol}, files={('fn', meaning.name): (meaning, path)}, file_names={},
        functions={'home': frozenset()}, targets={}, links=[], stash={})
    return model, path, document, meaning


def retire(model, root, selectors):
    change = write.Change(model, write.model_resolver(model), root)
    change.run({'cmd': 'retire', 'ref': 'discarded-copy/fn', 'withdraw_ledger': selectors})
    return change


def test_vanished_function_retains_its_entire_owner_including_withdrawn_selectors(tmp_path):
    model, path, original, _ = source_model(tmp_path)
    change = retire(model, tmp_path, ['funcs:36'])
    assert tomllib.loads(change.texts()[path]) == {**original, 'retired': True}
    assert tomllib.loads((tmp_path / path).read_text()) == original
    assert any('withdraw active ledger selectors: funcs:36' in line for line in change.lines)
    builder = Builder({}, {}, {}, {}, {})
    builder.overlay = change.texts()
    files.declare(builder, tmp_path)
    result = builder.finish()
    assert result.symbols == {} and result.meanings == []
    assert not result.stash.get('ledger_rows')
    assert retirement.records(result)[0][2] == {**original, 'retired': True}
    assert names.reserved(result, []) == {'discarded-copy'}
    assert change.expected[0](result) is None


@pytest.mark.parametrize('selectors', (['funcs:35'], ['funcs:36', 'funcs:36'],
                                     ['funcs:036'], ['funcs'], [36], 'funcs:36'))
def test_inexact_or_invalid_selectors_refuse_without_an_owner_write(tmp_path, selectors):
    model, path, original, _ = source_model(tmp_path)
    with pytest.raises(KbError):
        retire(model, tmp_path, selectors)
    assert tomllib.loads((tmp_path / path).read_text()) == original


@pytest.mark.parametrize('mutation', ('live-entry', 'missing-layout', 'incoming', 'curated',
                                    'unselected-ledger', 'legacy-owner', 'another-native-owner'))
def test_withdrawal_does_not_remove_live_entries_or_other_consumers(tmp_path, mutation):
    model, path, original, subject = source_model(tmp_path)
    if mutation == 'live-entry':
        model.functions['home'] = {0x100}
    elif mutation == 'missing-layout':
        model.functions = {}
    elif mutation == 'incoming':
        model.entities['endpoint', 'reader'] = Entity('endpoint', 'reader', refs={'fn': [subject.key]})
    elif mutation == 'curated':
        subject.symbols['home'].props['curated'] = True
    elif mutation == 'unselected-ledger':
        original['ledger'].append({'registry': 'funcs', 'order': 37, 'fields': ['role']})
        store.write(tmp_path, {path: store.render('fn', original)})
    elif mutation == 'legacy-owner':
        subject.sources.add('defs/legacy.csv')
    else:
        model.files['fn', 'another'] = subject, Path('kb/fn/another.toml')
    with pytest.raises(KbError):
        retire(model, tmp_path, ['funcs:36'])
    assert tomllib.loads((tmp_path / path).read_text()) == original


def test_default_retirement_still_refuses_a_ledger_selector(tmp_path):
    model, _, _, _ = source_model(tmp_path)
    change = write.Change(model, write.model_resolver(model), tmp_path)
    with pytest.raises(KbError, match='retirement has consumers'):
        change.run({'cmd': 'retire', 'ref': 'discarded-copy/fn'})


@pytest.mark.parametrize('dry_run', (False, True))
def test_withdrawal_uses_the_model_and_checks_l0_before_writing(tmp_path, dry_run):
    model, path, _, _ = source_model(tmp_path)
    texts = {path: 'retired = true\n'}
    with patch.object(write.lock, 'held', return_value=nullcontext()), \
            patch.object(write.compile, 'build', return_value=model), \
            patch.object(write, 'plan', return_value=(None, texts, model)), \
            patch.object(fingerprint, 'compute', return_value='stable'), \
            patch.object(l0, 'check_all', return_value=[]) as check, \
            patch.object(write.graph, 'fresh') as fresh, \
            patch.object(write.graph, 'sync_held') as sync, \
            patch.object(write.store, 'write') as save:
        write.apply([{'cmd': 'retire', 'ref': 'discarded-copy/fn',
                      'withdraw_ledger': ['funcs:36']}], tmp_path, dry_run=dry_run)
    check.assert_called_once_with(tmp_path, only=['home'])
    fresh.assert_not_called()
    assert save.call_count == sync.call_count == (0 if dry_run else 1)


@pytest.mark.parametrize('failure', ('l0', 'fingerprint'))
def test_invalid_or_changing_sources_refuse_before_withdrawal(tmp_path, failure):
    model, path, _, _ = source_model(tmp_path)
    with patch.object(write.lock, 'held', return_value=nullcontext()), \
            patch.object(write.compile, 'build', return_value=model), \
            patch.object(write, 'plan', return_value=(None, {path: 'retired = true\n'}, model)), \
            patch.object(fingerprint, 'compute', side_effect=['before', 'after']
                         if failure == 'fingerprint' else None, return_value='stable'), \
            patch.object(l0, 'check_all', return_value=['invalid export'] if failure == 'l0' else []), \
            patch.object(write.store, 'write') as save, \
            patch.object(write.graph, 'sync_held') as sync:
        with pytest.raises(KbError):
            write.apply([{'cmd': 'retire', 'ref': 'discarded-copy/fn',
                          'withdraw_ledger': ['funcs:36']}], tmp_path)
    save.assert_not_called()
    sync.assert_not_called()


def test_cli_exposes_explicit_repeatable_selectors():
    args = cli.build_parser().parse_args([
        'retire', 'discarded-copy/fn', '--withdraw-ledger', 'funcs:36', '--dry-run'])
    assert args.withdraw_ledger == ['funcs:36'] and args.dry_run
