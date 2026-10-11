"""Default source checkouts are pinned, actionable, and read-only in checks."""

import configparser
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'diagnostics'))
from catalog import CatalogError
import import_370z_logger
import import_ecudocs

MODULES = (import_370z_logger, import_ecudocs)


@pytest.fixture(params=MODULES, ids=lambda module: module.__name__)
def importer(request):
    return request.param


def test_default_checkout_has_the_importer_gitlink_and_source_url(importer):
    path = importer.DEFAULT_SOURCE_ROOT.relative_to(ROOT).as_posix()
    config = configparser.ConfigParser()
    config.read(ROOT / '.gitmodules')
    section = config[f'submodule "{path}"']
    assert section['path'] == path
    assert section['url'] == importer.SOURCE_URL
    entries = subprocess.run(['git', 'ls-files', '--stage', '--', path],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines()
    assert len(entries) == 1
    metadata, actual_path = entries[0].split('\t')
    mode, revision, stage = metadata.split()
    assert (mode, revision, stage, actual_path) == ('160000', importer.REVISION, '0', path)


def test_cli_defaults_to_the_pinned_source(importer, monkeypatch):
    monkeypatch.setattr(sys, 'argv', [importer.__file__, '--check'])
    args = importer.parser().parse_args()
    assert args.source_root == importer.DEFAULT_SOURCE_ROOT
    assert args.check is True


def test_explicit_checkout_argument_remains_supported(importer, tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', [importer.__file__, str(tmp_path), '--check'])
    args = importer.parser().parse_args()
    assert args.source_root == tmp_path


def test_missing_source_has_setup_hint_without_building_or_writing(importer, tmp_path, monkeypatch, capsys):
    source = tmp_path / 'source'
    source.mkdir()
    output = tmp_path / 'output'
    output.mkdir()
    previous = output / 'previous.csv'
    previous.write_bytes(b'previous\n')
    monkeypatch.setattr(importer, 'DEFAULT_SOURCE_ROOT', source)
    monkeypatch.setattr(importer, 'build', lambda *args: pytest.fail('uninitialized source is consumed'))
    monkeypatch.setattr(sys, 'argv', [importer.__file__, '--check', '--output', str(output)])
    assert importer.main() == 1
    captured = capsys.readouterr()
    assert 'run make setup' in captured.err
    assert not captured.out
    assert {p.name: p.read_bytes() for p in output.iterdir()} == {'previous.csv': b'previous\n'}


def test_default_source_still_passes_through_the_pinned_builder(importer, tmp_path, monkeypatch, capsys):
    source = tmp_path / 'source'
    source.mkdir()
    (source / '.git').write_text('gitdir: fixture\n')
    monkeypatch.setattr(importer, 'DEFAULT_SOURCE_ROOT', source)
    calls = []

    def refuse(actual):
        calls.append(actual)
        raise CatalogError('selected source does not match its pin')

    monkeypatch.setattr(importer, 'build', refuse)
    monkeypatch.setattr(sys, 'argv', [importer.__file__, '--check'])
    assert importer.main() == 1
    assert calls == [source]
    assert 'does not match its pin' in capsys.readouterr().err


@pytest.mark.parametrize('explicit', [False, True])
def test_check_through_the_selected_checkout_preserves_all_outputs(importer, explicit, tmp_path, monkeypatch):
    source = tmp_path / 'source'
    source.mkdir()
    (source / '.git').write_text('gitdir: fixture\n')
    output = tmp_path / 'output'
    data = {key: [] for key in ('documents', 'fragments', 'diagnostic_parameters',
                               'diagnostic_requests', 'can_frames', 'can_signals',
                               'can_bindings', 'request_parameters')}
    data['documents'] = [{'id': 'fixture-document', 'filename': 'fixture.txt'}]
    data['fragments'] = [{'id': 'fixture-fragment', 'text': 'input text\n'}]
    importer.write(output, data)
    before = {p.name: p.read_bytes() for p in output.iterdir()}
    monkeypatch.setattr(importer, 'DEFAULT_SOURCE_ROOT', source)
    calls = []
    monkeypatch.setattr(importer, 'build', lambda actual: calls.append(actual) or data)
    monkeypatch.setattr(sys, 'argv', [importer.__file__, *([str(source)] if explicit else []),
                                    '--check', '--output', str(output)])
    assert importer.main() == 0
    assert calls == [source]
    assert {p.name: p.read_bytes() for p in output.iterdir()} == before
