"""Bind the complete registered command set to its primary read-only producers."""

from copy import deepcopy
from pathlib import Path
from subprocess import CompletedProcess
from types import SimpleNamespace

import pytest

from tools import check_projection_contract as contract


@pytest.fixture
def entry(tmp_path):
    (tmp_path / 'producer.py').write_text('fixture')
    return {'path': 'output.csv', 'generator': 'uv run python producer.py --pack source.toml',
            'check': ['uv', 'run', 'python', 'producer.py', '--pack', 'source.toml', '--check']}


def test_every_production_command_has_its_own_read_only_recipe():
    entries = contract.project.load(contract.ROOT)
    expected = [item['path'] for item in entries if not contract.project.rendered(item)]
    assert [name for name, argv in contract.commands()] == expected
    assert len(expected) == 16


@pytest.mark.parametrize('value', [None, [], '', [True], [''], ['producer.py']])
def test_missing_or_invalid_check_is_refused(tmp_path, entry, value):
    entry['check'] = value
    with pytest.raises(contract.ContractError):
        contract.commands(tmp_path, [entry])


@pytest.mark.parametrize('change', ['write', 'different-producer', 'different-source', 'extra-check', 'remove-source'])
def test_a_checker_cannot_change_the_producer_or_its_inputs(tmp_path, entry, change):
    argv = entry['check']
    if change == 'write':
        argv.append('--write')
    elif change == 'different-producer':
        argv[3] = 'other.py'
    elif change == 'different-source':
        argv[5] = 'other.toml'
    elif change == 'extra-check':
        argv.append('--check')
    else:
        del argv[4:6]
    with pytest.raises(contract.ContractError, match='same producer'):
        contract.commands(tmp_path, [entry])


def test_write_mode_is_replaced_by_check_mode(tmp_path, entry):
    entry['generator'] += ' --write'
    assert contract.commands(tmp_path, [entry]) == [(entry['path'], entry['check'])]


@pytest.mark.parametrize('script', ['missing.py', '../producer.py', '/producer.py'])
def test_producer_must_be_a_repository_file(tmp_path, entry, script):
    entry['generator'] = f'python {script}'
    entry['check'] = ['python', script, '--check']
    with pytest.raises(contract.ContractError, match='absent or outside'):
        contract.commands(tmp_path, [entry])


def test_a_symlink_cannot_select_an_external_producer(tmp_path, entry):
    outside = tmp_path.parent / (tmp_path.name + '-outside.py')
    outside.write_text('fixture')
    path = tmp_path / 'producer.py'
    path.unlink()
    path.symlink_to(outside)
    with pytest.raises(contract.ContractError, match='outside'):
        contract.commands(tmp_path, [entry])


@pytest.mark.parametrize('entries', [None, {}, [None], [{'generator': None}]])
def test_malformed_entries_are_refused(tmp_path, monkeypatch, entries):
    monkeypatch.setattr(contract.project, 'load', lambda root: entries)
    with pytest.raises(contract.ContractError):
        contract.commands(tmp_path)


def test_registry_read_error_is_a_contract_failure(tmp_path, monkeypatch):
    def unavailable(root):
        raise FileNotFoundError('fixture missing')
    monkeypatch.setattr(contract.project, 'load', unavailable)
    with pytest.raises(contract.ContractError, match='fixture missing'):
        contract.commands(tmp_path)


def test_a_future_command_requires_a_declared_checker(tmp_path, entry):
    other = deepcopy(entry)
    other['path'] = 'new.csv'
    del other['check']
    with pytest.raises(contract.ContractError, match='new.csv'):
        contract.commands(tmp_path, [entry, other])


def test_native_projections_use_the_native_checker(tmp_path):
    assert contract.commands(tmp_path, [{'path': 'native.txt', 'generator': 'kb.project:fixture'}]) == []


def test_external_source_placeholder_requires_an_explicit_path_variable(tmp_path, entry):
    entry['generator'] = 'python producer.py <checkout>'
    entry['check'] = ['python', 'producer.py', '{VQ_SOURCE}', '--check']
    recipes = contract.commands(tmp_path, [entry])
    source = tmp_path / 'source with spaces'
    source.mkdir()
    assert contract.resolved(recipes, {'VQ_SOURCE': str(source)})[0][1] == [
        'python', 'producer.py', str(source.resolve()), '--check']
    entry['check'][2] = '<checkout>'
    with pytest.raises(contract.ContractError):
        contract.commands(tmp_path, [entry])


@pytest.mark.parametrize('value', [None, '', '--alternate', 'https://example.org/source', '/absent/source'])
def test_missing_source_stops_before_fingerprinting_or_execution(tmp_path, monkeypatch, value):
    monkeypatch.setattr(contract, 'commands', lambda root: [('source', ['producer.py', '{VQ_SOURCE}', '--check'])])
    def forbidden(*args, **kwargs):
        pytest.fail('no work may start before source preflight succeeds')
    with pytest.raises(contract.ContractError, match='VQ_SOURCE'):
        contract.run(tmp_path, environment={'VQ_SOURCE': value}, execute=forbidden, compute=forbidden)


def test_all_checks_run_once_and_preserve_primary_failures(tmp_path, monkeypatch):
    recipes = [('one', ['python', 'one.py', '--check']), ('two', ['python', 'two.py', '--check'])]
    monkeypatch.setattr(contract, 'commands', lambda root: recipes)
    calls, fingerprints = [], []
    def execute(argv, **kwargs):
        calls.append((argv, kwargs))
        return CompletedProcess(argv, 1 if len(calls) == 2 else 0, b'output\n', b'error\n')
    def compute(root):
        fingerprints.append(root)
        return SimpleNamespace(value='same source')
    output, errors, failed = contract.run(tmp_path, environment={}, execute=execute, compute=compute)
    assert calls == [(argv, {'cwd': tmp_path, 'capture_output': True}) for argv in [
        ['uv', 'run', 'kb', 'project', '--check'], *[argv for name, argv in recipes]]]
    assert fingerprints == [tmp_path, tmp_path]
    assert (output, errors, failed) == (b'output\n' * 3, b'error\n' * 3, ['one: exit 1'])


def test_source_change_withholds_all_collected_output(tmp_path, monkeypatch):
    monkeypatch.setattr(contract, 'commands', lambda root: [])
    values = iter(['before', 'after'])
    with pytest.raises(contract.ContractError, match='withheld'):
        contract.run(tmp_path, environment={},
                     execute=lambda argv, **kwargs: CompletedProcess(argv, 0, b'not published', b''),
                     compute=lambda root: SimpleNamespace(value=next(values)))


def test_primary_checker_start_failure_has_no_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(contract, 'commands', lambda root: [('one', ['producer.py', '--check'])])
    calls = []
    def execute(argv, **kwargs):
        calls.append(argv)
        raise FileNotFoundError('primary missing')
    with pytest.raises(contract.ContractError, match='primary checker cannot start'):
        contract.run(tmp_path, environment={}, execute=execute,
                     compute=lambda root: SimpleNamespace(value='same'))
    assert calls == [['uv', 'run', 'kb', 'project', '--check']]
