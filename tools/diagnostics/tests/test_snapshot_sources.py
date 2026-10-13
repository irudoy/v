"""Repository source snapshots require exact metadata and retained bytes."""

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'tools' / 'diagnostics'))
from catalog import CatalogError, require_pinned_snapshot, sha256_file

REVISION = '0123456789abcdef0123456789abcdef01234567'
SOURCE_URL = 'https://example.com/pinned-source'
SOURCE_FILES = ('data/profile.json', 'LICENSE')


def write_manifest(root, *, schema=1, revision=REVISION, source_url=SOURCE_URL,
                   files=SOURCE_FILES, digest=None, source_license='MIT'):
    rows = [f'schema = {schema}', f'source_url = "{source_url}"',
            f'revision = "{revision}"', f'license = "{source_license}"', '', '[files]']
    rows.extend(f'"{relative}" = "{digest or sha256_file(root / relative)}"'
                for relative in files)
    (root / 'source.toml').write_text('\n'.join(rows) + '\n', encoding='utf-8')


@pytest.fixture
def snapshot(tmp_path):
    (tmp_path / 'data').mkdir()
    (tmp_path / 'data/profile.json').write_bytes(b'{"data":{}}\n')
    (tmp_path / 'LICENSE').write_bytes(b'MIT license fixture\n')
    write_manifest(tmp_path)
    return tmp_path


def validate(root):
    require_pinned_snapshot(root, REVISION, SOURCE_URL, SOURCE_FILES, expected_license='MIT')


def test_exact_snapshot_is_read_only(snapshot):
    before = {p.relative_to(snapshot): p.read_bytes()
              for p in snapshot.rglob('*') if p.is_file()}
    validate(snapshot)
    assert {p.relative_to(snapshot): p.read_bytes()
            for p in snapshot.rglob('*') if p.is_file()} == before


@pytest.mark.parametrize('mutation', ['changed', 'missing', 'directory'])
def test_changed_or_missing_source_is_rejected(snapshot, mutation):
    path = snapshot / SOURCE_FILES[0]
    if mutation == 'changed':
        path.write_bytes(b'{"data":[]}\n')
        reason = 'SHA-256 does not match'
    else:
        path.unlink()
        if mutation == 'directory':
            path.mkdir()
        reason = 'required regular source file is missing'
    with pytest.raises(CatalogError, match=reason):
        validate(snapshot)


@pytest.mark.parametrize(('metadata', 'reason'), [
    ({'schema': 2}, 'schema 1'),
    ({'schema': 'true'}, 'schema 1'),
    ({'revision': 'another-revision'}, 'revision does not match'),
    ({'source_url': 'https://example.com/another-source'}, 'source URL does not match'),
    ({'source_license': 'GPL-3.0'}, 'source license does not match MIT'),
    ({'files': ('LICENSE',)}, 'file keys do not match'),
    ({'digest': 'not-a-hash'}, 'invalid SHA-256'),
])
def test_wrong_manifest_is_rejected(snapshot, metadata, reason):
    write_manifest(snapshot, **metadata)
    with pytest.raises(CatalogError, match=reason):
        validate(snapshot)


def test_extra_manifest_file_is_rejected(snapshot):
    (snapshot / 'extra.txt').write_bytes(b'extra\n')
    write_manifest(snapshot, files=(*SOURCE_FILES, 'extra.txt'))
    with pytest.raises(CatalogError, match='file keys do not match'):
        validate(snapshot)


@pytest.mark.parametrize('symlink', ['source', 'parent', 'manifest'])
def test_symlinked_snapshot_inputs_are_rejected(snapshot, symlink):
    path = snapshot / {'source': SOURCE_FILES[0], 'parent': 'data',
                       'manifest': 'source.toml'}[symlink]
    retained = path.with_name(path.name + '.retained')
    path.rename(retained)
    path.symlink_to(retained.name, target_is_directory=symlink == 'parent')
    with pytest.raises(CatalogError, match='non-symlink'):
        validate(snapshot)


def test_missing_manifest_has_repository_restore_hint(snapshot):
    (snapshot / 'source.toml').unlink()
    with pytest.raises(CatalogError, match='restore the source snapshot from this repository'):
        validate(snapshot)


def test_malformed_manifest_is_rejected(snapshot):
    (snapshot / 'source.toml').write_text('schema = [', encoding='utf-8')
    with pytest.raises(CatalogError, match='cannot read source manifest'):
        validate(snapshot)
