"""Read-only byte and file-set checks for editor definitions and ledgers."""

from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest

from kb.repo import KbError
from tools import projection_check
from tools.mapkit import definition_targets, emit_def
from tools.maps import build_tracker


TARGETS = definition_targets.registered_targets()
SOURCES = definition_targets.registered_sources()
FILES = [(emit_def, f'{rom}.{suffix}') for rom in TARGETS for suffix in ('xml', 'xdf')]
FILES += [(build_tracker, f'{rom}.maps.csv') for rom in SOURCES]


@pytest.fixture
def renderer(tmp_path, monkeypatch):
    def prepare(module, *, fail=None):
        output = tmp_path / module.__name__.split('.')[-1]
        output.mkdir()
        active = []
        transaction = object()
        events = []

        @contextmanager
        def session():
            events.append('begin')
            active.append(transaction)
            try:
                yield transaction
            finally:
                active.pop()
                events.append('end')

        def write(rom, *paths, graph=None, **kwargs):
            assert active == [transaction]
            assert graph is transaction
            if rom == fail:
                raise RuntimeError('render failure')
            if module is build_tracker:
                paths = (kwargs['tracker'],)
            for name in paths:
                path = Path(name)
                assert not path.is_relative_to(output)
                path.write_bytes(f'rendered {path.name}\n'.encode())

        monkeypatch.setattr(module.reader, 'session', session)
        monkeypatch.setattr(module, 'emit_target' if module is emit_def else 'emit_tracker', write)
        for owner, name in FILES:
            if owner is module:
                (output / name).write_bytes(f'rendered {name}\n'.encode())
        return output, active, events

    return prepare


def snapshot(directory):
    return {p.name: p.read_bytes() for p in directory.iterdir() if p.is_file()}


@pytest.mark.parametrize('module', [emit_def, build_tracker])
def test_check_retains_one_transaction_through_comparison_and_writes_no_outputs(renderer, module):
    output, active, events = renderer(module)
    before = snapshot(output)
    compare = projection_check.compare

    def compare_inside_read(*args, **kwargs):
        assert len(active) == 1
        events.append('compare')
        return compare(*args, **kwargs)

    with mock.patch.object(projection_check, 'compare', side_effect=compare_inside_read), \
            mock.patch.object(module.os, 'replace', side_effect=AssertionError('replace')):
        module.emit_all(output, check=True)
    assert events == ['begin', 'compare', 'end']
    assert snapshot(output) == before
    assert len(list(output.iterdir())) == len(before)


@pytest.mark.parametrize('module,name', FILES)
@pytest.mark.parametrize('drift', ['changed', 'missing'])
def test_every_registered_output_is_checked_and_preserved(renderer, module, name, drift):
    output, active, events = renderer(module)
    path = output / name
    if drift == 'changed':
        path.write_bytes(path.read_bytes() + b'drift\n')
    else:
        path.unlink()
    before = snapshot(output)
    with pytest.raises(ValueError, match='differs from its rendering' if drift == 'changed' else 'missing'):
        module.emit_all(output, check=True)
    assert snapshot(output) == before
    assert active == []
    assert events == ['begin', 'end']


@pytest.mark.parametrize('module,extra', [(emit_def, 'EXTRA.xml'), (emit_def, 'EXTRA.xdf'),
                                       (build_tracker, 'EXTRA.maps.csv')])
def test_unexpected_outputs_are_rejected_without_deletion(renderer, module, extra):
    output, _, _ = renderer(module)
    (output / extra).write_bytes(b'extra\n')
    before = snapshot(output)
    with pytest.raises(ValueError, match='unexpected projection file'):
        module.emit_all(output, check=True)
    assert snapshot(output) == before


@pytest.mark.parametrize('module', [emit_def, build_tracker])
def test_render_failure_preserves_every_existing_output(renderer, module):
    output, active, events = renderer(module, fail=TARGETS[0] if module is emit_def else SOURCES[0])
    before = snapshot(output)
    with pytest.raises(RuntimeError, match='render failure'):
        module.emit_all(output, check=True)
    assert snapshot(output) == before
    assert active == []
    assert events == ['begin', 'end']


@pytest.mark.parametrize('module', [emit_def, build_tracker])
def test_primary_read_failure_is_propagated_without_rendering_or_writing(renderer, module, monkeypatch):
    output, _, _ = renderer(module)
    before = snapshot(output)
    with mock.patch.object(module.reader, 'session', side_effect=KbError('unavailable', code=6)):
        with pytest.raises(KbError, match='unavailable'):
            module.emit_all(output, check=True)
    assert snapshot(output) == before


@pytest.mark.parametrize('module', [emit_def, build_tracker])
def test_final_source_change_prevents_success_status(renderer, module, monkeypatch, capsys):
    output, _, _ = renderer(module)
    before = snapshot(output)
    original = module.emit_all
    original_session = module.reader.session

    @contextmanager
    def changed_read():
        with original_session() as transaction:
            yield transaction
        raise KbError('source fingerprint changes', code=6)

    monkeypatch.setattr(module.reader, 'session', changed_read)
    monkeypatch.setattr(module, 'emit_all', lambda output_dir=output, **kw: original(output_dir, **kw))
    # The normal comparison succeeds; the final read check still refuses success.
    with pytest.raises(KbError, match='source fingerprint changes'):
        module.main(['all', '--check'])
    assert 'status=PASS' not in capsys.readouterr().out
    assert snapshot(output) == before


@pytest.mark.parametrize('module', [emit_def, build_tracker])
@pytest.mark.parametrize('args', [[], ['all']])
def test_check_cli_defaults_to_all_and_selects_check_mode(module, args):
    with mock.patch.object(module, 'emit_all') as emit:
        module.main(args + ['--check'])
    emit.assert_called_once_with(check=True)


@pytest.mark.parametrize('module', [emit_def, build_tracker])
@pytest.mark.parametrize('args', [['JK08A', '--check'], ['all', 'out', '--check'],
                                ['--check', '--check']])
def test_check_cli_refuses_partial_sets_or_explicit_output_paths(module, args):
    with mock.patch.object(module, 'emit_all') as emit:
        with pytest.raises(SystemExit):
            module.main(args)
    emit.assert_not_called()


def test_definition_fetch_borrows_the_existing_transaction():
    transaction = mock.Mock()
    transaction.run.return_value = []
    with mock.patch.object(emit_def.reader, 'session', side_effect=AssertionError('nested read')):
        assert emit_def.fetch('JK08A', graph=transaction) == ({}, {})
    assert transaction.run.call_count > 0
