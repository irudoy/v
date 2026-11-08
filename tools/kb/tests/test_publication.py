"""Restartable native source publication without graph or guard overrides."""

import contextlib
import io
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import threading
from types import SimpleNamespace

import pytest

from kb import (adapters, cli, compile, fingerprint, lock, names, project, publication,
                repo, store, write)
from kb.adapters import files as file_adapter
from kb.repo import KbError
from tools.kb.tests import writer_sources
from tools.kb.tests.test_lock import virtual_time


@pytest.fixture
def sources(tmp_path):
    previous = {
        Path('kb/ram/first.toml'): b'title = "Before"\r\n',
        Path('kb/ram/removed.toml'): b'title = "Retained"\n',
        repo.OWNER_CONFIG: b'[names]\n',
        repo.CONFIG: b'[lock]\ntimeout = 1.0\n',
        names.PATH: b'old names\n',
    }
    for path, data in previous.items():
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o640)
    changes = {
        Path('kb/ram/first.toml'): 'title = "After"\n',
        Path('kb/ram/removed.toml'): None,
        Path('kb/ram/new.toml'): 'title = "Created"\n',
        repo.OWNER_CONFIG: '[names]\n# changed owner declarations\n',
        repo.CONFIG: '[lock]\ntimeout = 2.0\n',
        names.PATH: 'new names\n',
    }
    return SimpleNamespace(root=tmp_path, previous=previous, changes=changes)


def snapshot(fixture):
    result = {}
    for path in fixture.changes:
        target = fixture.root / path
        result[path] = (target.read_bytes(), target.stat().st_mode & 0o7777) \
            if target.exists() else None
    return result


def fault_after(fixture, monkeypatch, number):
    count = 0
    replace, remove = publication._replace, publication._remove

    def checkpoint(target):
        nonlocal count
        if target.relative_to(fixture.root) in fixture.changes:
            count += 1
            if count == number:
                raise OSError('controlled source interruption')

    def replacing(target, data, mode):
        replace(target, data, mode)
        checkpoint(target)

    def removing(target):
        remove(target)
        checkpoint(target)

    monkeypatch.setattr(publication, '_replace', replacing)
    monkeypatch.setattr(publication, '_remove', removing)


@pytest.mark.parametrize('number', range(1, 7))
def test_every_partial_file_publication_restores_exact_bytes_and_modes(sources, monkeypatch, number):
    before = snapshot(sources)
    with monkeypatch.context() as patch:
        fault_after(sources, patch, number)
        with pytest.raises(KbError, match='controlled source interruption'):
            store.write(sources.root, sources.changes)
    assert publication.pending(sources.root)
    held = snapshot(sources)
    status = publication.recover(sources.root, status=True)
    assert not status['conflicts'] and len(status['paths']) == len(sources.changes)
    assert publication.recover(sources.root, dry_run=True) == status
    assert snapshot(sources) == held and publication.pending(sources.root)
    publication.recover(sources.root)
    assert snapshot(sources) == before
    assert not publication.pending(sources.root)
    assert publication.recover(sources.root)['id'] is None


def test_journal_preparation_failure_changes_no_source(sources, monkeypatch):
    before = snapshot(sources)
    monkeypatch.setattr(publication, '_replace',
                        lambda *args: (_ for _ in ()).throw(OSError('no journal space')))
    with pytest.raises(KbError, match='no journal space'):
        store.write(sources.root, sources.changes)
    assert snapshot(sources) == before
    assert not publication.pending(sources.root)


def incomplete(sources):
    with pytest.raises(KbError, match='post-write census refusal'):
        with publication.transaction(sources.root, sources.changes):
            store.write(sources.root, sources.changes)
            raise KbError('post-write census refusal', code=3)


def test_pending_sources_refuse_compilation_fingerprinting_writes_and_lock_entry(sources):
    sources.changes[repo.CONFIG] = 'incomplete configuration\n'
    incomplete(sources)
    # Even a broken config does not prevent the lock's recovery diagnostic.
    for command in (lambda: compile.build(sources.root),
                    lambda: fingerprint.compute(sources.root),
                    lambda: store.write(sources.root, sources.changes)):
        with pytest.raises(KbError, match='kb recover') as error:
            command()
        assert error.value.code == 6
    with pytest.raises(KbError, match='kb recover'):
        with lock.held(sources.root):
            pytest.fail('an ordinary command accepts the incomplete snapshot')


@pytest.mark.parametrize('progress_at,release_at', [(None, 40), (50, 120)])
def test_pending_publication_keeps_the_publishers_timeout_and_progress(
        sources, monkeypatch, progress_at, release_at):
    # A stage longer than recovery's 30 s still has the configured 90 s.
    # The second case also needs a real progress renewal past that deadline.
    sources.changes[repo.CONFIG] = 'interrupted configuration\n'
    monkeypatch.setattr(lock, 'timeout_of', lambda root: 90)
    with contextlib.ExitStack() as publisher:
        publisher.enter_context(lock.held(sources.root))
        publisher.enter_context(publication.transaction(sources.root, sources.changes))
        progress = publisher.enter_context(lock.syncing(sources.root, 'map loading'))
        store.write(sources.root, sources.changes)
        assert publication.wait_timeout(sources.root) == 90

        def no_config(root):
            pytest.fail('the waiter reads a potentially interrupted configuration')

        monkeypatch.setattr(lock, 'timeout_of', no_config)

        def advance(now):
            if now == progress_at:
                progress('map relationships')
            if now == release_at:
                publisher.close()

        now = virtual_time(monkeypatch, advance)
        output = io.StringIO()
        with lock.held(sources.root, log=output):
            assert now[0] == release_at
        assert 'graph sync: map loading' in output.getvalue()
        if progress_at is not None:
            assert 'graph sync: map relationships' in output.getvalue()
    assert not publication.pending(sources.root)


@pytest.mark.parametrize('command', [
    ['instance', action] for action in ('up', 'down', 'status', 'prune')
] + [['guard', 'status', '--session', '12345678-1234-1234-1234-123456789abc']])
def test_pending_sources_keep_instance_controls_and_guard_status_available(sources, monkeypatch, command):
    incomplete(sources)
    monkeypatch.setattr(cli.repo, 'ROOT', sources.root)
    called = []

    def control(args):
        called.append((args.command, args.action))
        return 0

    monkeypatch.setattr(cli, 'command_instance', control)
    monkeypatch.setattr(cli, 'command_guard', control)
    monkeypatch.setattr(lock, 'held', lambda *args, **kwargs: pytest.fail('control waits on sources'))
    assert cli.main(command) == 0
    assert called == [(command[0], command[1])]
    assert publication.pending(sources.root)


@pytest.mark.parametrize('mode', ['on', 'off'])
def test_pending_sources_still_require_recovery_before_guard_changes(sources, monkeypatch, capsys, mode):
    incomplete(sources)
    monkeypatch.setattr(cli.repo, 'ROOT', sources.root)
    monkeypatch.setattr(cli, 'command_guard', lambda args: pytest.fail('guard mutation accepted'))
    assert cli.main(['guard', mode, '--session', '12345678-1234-1234-1234-123456789abc']) == 6
    assert 'kb recover' in capsys.readouterr().err


@pytest.mark.parametrize('mutation', ['edit', 'chmod', 'unexpected', 'directory'])
def test_any_external_change_refuses_the_whole_recovery(sources, mutation):
    incomplete(sources)
    if mutation == 'edit':
        (sources.root / 'kb/ram/first.toml').write_text('manual source edit\n')
    elif mutation == 'chmod':
        (sources.root / 'kb/ram/first.toml').chmod(0o600)
    elif mutation == 'unexpected':
        (sources.root / 'kb/ram/removed.toml').write_text('unexpected replacement\n')
    else:
        source = sources.root / 'kb/ram/first.toml'
        source.unlink()
        source.mkdir()
        with pytest.raises(KbError, match='nothing is restored'):
            publication.recover(sources.root)
        assert source.is_dir() and publication.pending(sources.root)
        return
    held = snapshot(sources)
    assert publication.recover(sources.root, status=True)['conflicts']
    with pytest.raises(KbError, match='nothing is restored') as refused:
        publication.recover(sources.root)
    assert 'recorded state' in str(refused.value)
    assert 'KB batch after recovery' in str(refused.value)
    assert 'do not delete the journal' in str(refused.value)
    assert snapshot(sources) == held and publication.pending(sources.root)


def test_a_failed_recovery_is_restartable(sources, monkeypatch):
    before = snapshot(sources)
    incomplete(sources)
    with monkeypatch.context() as patch:
        fault_after(sources, patch, 2)
        with pytest.raises(KbError, match='journal retained'):
            publication.recover(sources.root)
    assert publication.pending(sources.root)
    publication.recover(sources.root)
    assert snapshot(sources) == before


def test_nested_name_enrollment_joins_the_native_publication(sources):
    original = (sources.root / names.PATH).read_bytes()
    changes = {Path('kb/ram/first.toml'): 'title = "Native write"\n'}
    with pytest.raises(KbError, match='post-write census refusal'):
        with publication.transaction(sources.root, changes):
            store.write(sources.root, changes)
            names.write([names.Row('probe', 'ram', 0x100, 'probe-otter', ())], sources.root)
            assert publication.pending(sources.root)
            # A second enrollment state must not hide the first produced state.
            names.write([names.Row('probe', 'ram', 0x102, 'probe-heron', ())], sources.root)
            raise KbError('post-write census refusal', code=3)
    publication.recover(sources.root)
    assert (sources.root / names.PATH).read_bytes() == original


def test_source_paths_cannot_escape_or_follow_symlinks(sources, tmp_path):
    outside = tmp_path / 'outside.toml'
    outside.write_bytes(b'private unrelated bytes')
    linked = sources.root / 'kb/ram/link.toml'
    linked.symlink_to(outside)
    for path in (Path('../outside.toml'), outside, Path('kb/ram/link.toml'), Path('.git/config')):
        with pytest.raises(KbError):
            store.write(sources.root, {path: 'replacement'})
    assert outside.read_bytes() == b'private unrelated bytes'
    assert not publication.pending(sources.root)


def test_a_source_symlink_after_interruption_is_not_followed(sources):
    incomplete(sources)
    outside = sources.root / 'outside.txt'
    outside.write_bytes(b'keep this')
    source = sources.root / 'kb/ram/first.toml'
    source.unlink()
    source.symlink_to(outside)
    with pytest.raises(KbError, match='symlink'):
        publication.recover(sources.root)
    assert outside.read_bytes() == b'keep this' and publication.pending(sources.root)


@pytest.mark.parametrize('corrupt', [None, [], {'version': 9}, 'invalid'])
def test_invalid_journals_remain_available_without_source_changes(sources, corrupt):
    incomplete(sources)
    before = snapshot(sources)
    (sources.root / publication.PATH).write_text(json.dumps(corrupt))
    with pytest.raises(KbError, match='invalid recovery journal'):
        publication.recover(sources.root)
    assert snapshot(sources) == before and publication.pending(sources.root)


@pytest.mark.parametrize('mutation', ['root', 'before', 'path', 'duplicate', 'state'])
def test_journal_integrity_refuses_restoration(sources, mutation):
    incomplete(sources)
    before = snapshot(sources)
    journal = sources.root / publication.PATH
    document = json.loads(journal.read_text())
    key = next(iter(document['entries']))
    if mutation == 'root':
        document['root'] += '/different-checkout'
    elif mutation == 'before':
        document['entries'][key]['before']['data'] = 'Y29ycnVwdA=='
    elif mutation == 'path':
        document['entries']['.git/config'] = document['entries'].pop(key)
    elif mutation == 'state':
        document['entries'][key]['states'] = [{'sha256': 0, 'bytes': 'x', 'mode': None}]
    text = json.dumps(document)
    if mutation == 'duplicate':
        text = text[:-1] + ', "version": 1}'
    journal.write_text(text)
    with pytest.raises(KbError):
        publication.recover(sources.root)
    assert snapshot(sources) == before and publication.pending(sources.root)


@pytest.mark.parametrize('value', [None, True, -1, float('inf'), float('nan'), '300'])
def test_invalid_recorded_timeouts_refuse_the_journal(sources, value):
    incomplete(sources)
    before = snapshot(sources)
    journal = sources.root / publication.PATH
    document = json.loads(journal.read_text())
    document['lock_timeout'] = value
    journal.write_text(json.dumps(document))
    for operation in (lambda: publication.wait_timeout(sources.root),
                      lambda: publication.recover(sources.root)):
        with pytest.raises(KbError, match='invalid recovery journal'):
            operation()
    assert snapshot(sources) == before and publication.pending(sources.root)


def test_a_previous_journal_without_a_timeout_keeps_recovery_available(sources):
    before = snapshot(sources)
    incomplete(sources)
    journal = sources.root / publication.PATH
    document = json.loads(journal.read_text())
    document['version'] = 1
    del document['lock_timeout']
    journal.write_text(json.dumps(document))
    assert publication.wait_timeout(sources.root) == 300
    publication.recover(sources.root)
    assert snapshot(sources) == before and not publication.pending(sources.root)


@pytest.mark.parametrize('link', ['state', 'lock'])
def test_recovery_does_not_open_a_lock_through_a_symlink(sources, link):
    before = snapshot(sources)
    incomplete(sources)
    outside = sources.root.parent / (sources.root.name + '-external-lock')
    outside.mkdir()
    external_lock = outside / 'lock'
    external_lock.write_bytes(b'unrelated lock bytes')
    state = sources.root / repo.STATE
    if link == 'state':
        saved = sources.root / 'saved-publication-state'
        state.rename(saved)
        state.symlink_to(outside, target_is_directory=True)
    else:
        (state / 'lock').symlink_to(external_lock)
    with pytest.raises(KbError, match='symlink'):
        publication.recover(sources.root)
    assert external_lock.read_bytes() == b'unrelated lock bytes'
    if link == 'state':
        state.unlink()
        saved.rename(state)
    else:
        (state / 'lock').unlink()
    publication.recover(sources.root)
    assert snapshot(sources) == before


def child_environment():
    return {**os.environ, 'PYTHONPATH': str(Path(publication.__file__).parents[1])}


@pytest.mark.parametrize('phase', ['publish', 'recover'])
def test_sigkill_leaves_a_recoverable_journal(sources, phase):
    before = snapshot(sources)
    if phase == 'recover':
        incomplete(sources)
    program = '''
import os, signal, sys
from pathlib import Path
from kb import publication, store
root = Path(sys.argv[1])
replace = publication._replace
def interrupted(target, data, mode):
    replace(target, data, mode)
    if target.relative_to(root).parts[0] == 'kb':
        os.kill(os.getpid(), signal.SIGKILL)
publication._replace = interrupted
if sys.argv[2] == 'recover':
    publication.recover(root)
else:
    store.write(root, {Path('kb/ram/first.toml'): 'after kill\\n',
                       Path('kb/ram/new.toml'): 'created\\n'})
'''
    result = subprocess.run([sys.executable, '-c', program, str(sources.root), phase],
                            env=child_environment(), capture_output=True, text=True, timeout=20)
    assert result.returncode == -signal.SIGKILL, result.stderr
    assert publication.pending(sources.root)
    publication.recover(sources.root)
    assert snapshot(sources) == before


def test_a_live_publication_finishes_before_an_ordinary_waiter_reads(sources):
    program = '''
import sys
from pathlib import Path
from kb import lock, publication, store
root = Path(sys.argv[1])
changes = {Path('kb/ram/first.toml'): 'live publication\\n'}
with lock.held(root, timeout=1):
    with publication.transaction(root, changes):
        store.write(root, changes)
        print('ready', flush=True)
        sys.stdin.readline()
'''
    acquired = threading.Event()
    started = threading.Event()
    errors = []

    def waiting():
        started.set()
        try:
            with lock.held(sources.root):
                acquired.set()
        except Exception as error:
            errors.append(error)

    with subprocess.Popen([sys.executable, '-c', program, str(sources.root)],
                          env=child_environment(), stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE, text=True) as child:
        assert child.stdout.readline().strip() == 'ready', child.stderr.read()
        waiter = threading.Thread(target=waiting)
        waiter.start()
        assert started.wait(1)
        assert not acquired.wait(0.05)
        child.stdin.write('finish\n')
        child.stdin.flush()
        assert child.wait(timeout=5) == 0, child.stderr.read()
        waiter.join(timeout=5)
    assert not waiter.is_alive() and not errors and acquired.is_set()
    assert not publication.pending(sources.root)


def test_an_error_after_journal_cleanup_reports_completed_source_restoration(sources, monkeypatch):
    before = snapshot(sources)
    incomplete(sources)
    sync = publication._sync_directory

    def failing(directory):
        if directory == sources.root / repo.STATE and not publication.pending(sources.root):
            raise OSError('controlled journal cleanup error')
        sync(directory)

    monkeypatch.setattr(publication, '_sync_directory', failing)
    with pytest.raises(KbError, match='previous files restored'):
        publication.recover(sources.root)
    assert snapshot(sources) == before
    assert publication.recover(sources.root)['id'] is None


def test_native_sync_census_refusal_recovers_through_the_guarded_cli(tmp_path, monkeypatch):
    monkeypatch.setattr(adapters, 'ADAPTERS', (file_adapter,))
    writer_sources.write_sources(tmp_path)
    operation = {'cmd': 'rename', 'meaning': 'rpm/ram', 'name': 'recovered_rpm'}
    before = {path.relative_to(tmp_path): path.read_bytes()
              for path in (tmp_path / 'kb').rglob('*') if path.is_file()}
    monkeypatch.setattr(write.graph, 'fresh', lambda *a, **k: contextlib.nullcontext())
    monkeypatch.setattr(write, 'graph_resolver', lambda _, model, *args: write.model_resolver(model))

    def refused(*args, **kwargs):
        assert publication.pending(tmp_path)
        assert (tmp_path / 'kb/ram/recovered_rpm.toml').is_file()
        raise KbError('controlled census refusal after source publication', code=3)

    monkeypatch.setattr(write.graph, 'sync_held', refused)
    with pytest.raises(KbError, match='census refusal'):
        write.apply([operation], root=tmp_path)
    # Execute the real CLI in an isolated checkout of the current package.
    package = tmp_path / 'tools/kb/src/kb'
    shutil.copytree(Path(publication.__file__).parent, package, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(repo.ROOT / 'tools/kb/hook.py', tmp_path / 'tools/kb/hook.py')
    environment = {**os.environ, 'PYTHONPATH': str(package.parent)}
    environment.pop('KB_GUARD', None)
    guard = project.hook.Guard(repo.ROOT)
    assert guard.decide('Bash', {'command': 'uv run kb recover'}) is None
    for command in (['brief', '--no-sync'], ['sync'], ['apply', 'missing-batch.toml']):
        result = subprocess.run([sys.executable, '-m', 'kb.cli', *command], cwd=tmp_path,
                                env=environment, capture_output=True, text=True, timeout=20)
        assert result.returncode == 6 and 'kb recover' in result.stderr
    result = subprocess.run([sys.executable, '-m', 'kb.cli', 'guard', 'status', '--json',
                             '--session', '12345678-1234-1234-1234-123456789abc'], cwd=tmp_path,
                            env=environment, capture_output=True, text=True, timeout=20)
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)['mode'] is None
    assert publication.pending(tmp_path)
    for options in (['--status', '--json'], ['--dry-run', '--json'], ['--json']):
        result = subprocess.run([sys.executable, '-m', 'kb.cli', 'recover', *options], cwd=tmp_path,
                                env=environment, capture_output=True, text=True, timeout=20)
        assert result.returncode == 0, result.stderr
        assert json.loads(result.stdout)['id']
    restored = {path.relative_to(tmp_path): path.read_bytes()
                for path in (tmp_path / 'kb').rglob('*') if path.is_file()}
    assert restored == before and not publication.pending(tmp_path)
    assert write._issues(compile.build(tmp_path)) == {}
    with pytest.raises(KbError, match='outside.*schema|unsupported|takes|width'):
        write.apply([{'cmd': 'set', 'ref': 'rpm/ram', 'keys': {'width': 3}}], root=tmp_path)
    assert not publication.pending(tmp_path)
