"""Default source snapshots are pinned, actionable, and read-only in checks."""

from pathlib import Path
import sys
import tomllib

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'diagnostics'))
from catalog import CatalogError, require_pinned_snapshot
import import_370z_logger
import import_ecudocs

MODULES = (import_370z_logger, import_ecudocs)


@pytest.fixture(params=MODULES, ids=lambda module: module.__name__)
def importer(request):
    return request.param


def snapshot_paths(importer):
    if importer is import_370z_logger:
        return importer.SOURCE_FILES
    return (importer.PROFILE_PATH, 'LICENSE')


def test_default_snapshot_has_the_importer_pin_and_valid_sources(importer):
    with (importer.DEFAULT_SOURCE_ROOT / 'source.toml').open('rb') as source:
        manifest = tomllib.load(source)
    assert manifest['source_url'] == importer.SOURCE_URL
    assert manifest['revision'] == importer.REVISION
    assert manifest['license'] == ('MIT' if importer is import_370z_logger else 'GPL-3.0')
    require_pinned_snapshot(importer.DEFAULT_SOURCE_ROOT, importer.REVISION,
                            importer.SOURCE_URL, snapshot_paths(importer),
                            expected_license=importer.SOURCE_LICENSE)


def test_default_build_preserves_the_projected_document_set(importer, monkeypatch):
    monkeypatch.setattr(importer, 'require_pinned_git_tree',
                        lambda *args: pytest.fail('default snapshot requires Git'))
    data = importer.build(importer.DEFAULT_SOURCE_ROOT)
    projected_paths = (importer.SOURCE_FILES if importer is import_370z_logger
                       else (importer.PROFILE_PATH,))
    assert {row['filename'] for row in data['documents']} == set(projected_paths)
    assert len(data['documents']) == len(projected_paths)


def test_cli_defaults_to_the_pinned_source(importer, monkeypatch):
    monkeypatch.setattr(sys, 'argv', [importer.__file__, '--check'])
    args = importer.parser().parse_args()
    assert args.source_root == importer.DEFAULT_SOURCE_ROOT
    assert args.check is True


def test_explicit_checkout_argument_remains_supported(importer, tmp_path, monkeypatch):
    monkeypatch.setattr(sys, 'argv', [importer.__file__, str(tmp_path), '--check'])
    args = importer.parser().parse_args()
    assert args.source_root == tmp_path


def test_missing_snapshot_has_restore_hint_without_writing(importer, tmp_path, monkeypatch, capsys):
    source = tmp_path / 'source'
    source.mkdir()
    output = tmp_path / 'output'
    output.mkdir()
    previous = output / 'previous.csv'
    previous.write_bytes(b'previous\n')
    monkeypatch.setattr(importer, 'DEFAULT_SOURCE_ROOT', source)
    monkeypatch.setattr(importer, 'write', lambda *args: pytest.fail('missing snapshot writes outputs'))
    monkeypatch.setattr(sys, 'argv', [importer.__file__, '--check', '--output', str(output)])
    assert importer.main() == 1
    captured = capsys.readouterr()
    assert 'restore the source snapshot from this repository' in captured.err
    assert 'make setup' not in captured.err
    assert not captured.out
    assert {p.name: p.read_bytes() for p in output.iterdir()} == {'previous.csv': b'previous\n'}


def test_resolved_default_source_selects_the_snapshot_validator(importer, tmp_path, monkeypatch):
    source = tmp_path / 'source'
    source.mkdir()
    monkeypatch.setattr(importer, 'DEFAULT_SOURCE_ROOT', source)
    calls = []

    def refuse(*args, **kwargs):
        calls.append((args, kwargs))
        raise CatalogError('snapshot validator reached')

    monkeypatch.setattr(importer, 'require_pinned_snapshot', refuse)
    monkeypatch.setattr(importer, 'require_pinned_git_tree',
                        lambda *args: pytest.fail('default snapshot requires Git'))
    equivalent = source / '..' / source.name
    with pytest.raises(CatalogError, match='snapshot validator reached'):
        importer.build(equivalent)
    assert calls == [((equivalent, importer.REVISION, importer.SOURCE_URL, snapshot_paths(importer)),
                     {'expected_license': importer.SOURCE_LICENSE})]


def test_external_snapshot_cannot_replace_the_git_pin_contract(importer, tmp_path, monkeypatch):
    source = tmp_path / 'external'
    source.mkdir()
    (source / 'source.toml').write_bytes((importer.DEFAULT_SOURCE_ROOT / 'source.toml').read_bytes())
    calls = []

    def refuse(*args):
        calls.append(args)
        raise CatalogError('external Git pin validator reached')

    monkeypatch.setattr(importer, 'require_pinned_git_tree', refuse)
    monkeypatch.setattr(importer, 'require_pinned_snapshot',
                        lambda *args: pytest.fail('external snapshot bypasses the Git pin'))
    with pytest.raises(CatalogError, match='external Git pin validator reached'):
        importer.build(source)
    git_paths = importer.SOURCE_FILES if importer is import_370z_logger else (importer.PROFILE_PATH,)
    assert calls == [(source, importer.REVISION, git_paths)]


@pytest.mark.parametrize('explicit', [False, True])
def test_check_through_the_selected_source_preserves_all_outputs(importer, explicit, tmp_path, monkeypatch):
    source = tmp_path / 'source'
    source.mkdir()
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
