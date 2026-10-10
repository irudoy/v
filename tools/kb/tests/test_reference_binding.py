"""Bounded pin-identity and actual A2L-byte refusal contracts."""

from types import SimpleNamespace

import pytest

from kb import compatibility, fingerprint
from kb.repo import KbError


@pytest.mark.parametrize('failure', [None, 'checkout', 'bytes', 'conflict', 'absent'])
def test_reference_requires_exact_checkout_pin_and_file_bytes(monkeypatch, tmp_path, failure):
    expected, actual = 'a' * 40, 'a' * 40
    if failure == 'checkout':
        actual = 'b' * 40
    elif failure == 'absent':
        actual = 'absent'
    monkeypatch.setattr(compatibility, 'reference_commit', lambda root: actual)
    path = tmp_path / compatibility.A2L
    path.parent.mkdir(parents=True)
    data = b'<definition />\n'
    path.write_bytes(data if failure != 'bytes' else data + b'changed')
    def git(root, *args):
        if args[:2] == ('ls-files', '--stage'):
            line = f'160000 {expected} 0\t{compatibility.REFERENCE.as_posix()}'
            return line + '\n' + line if failure == 'conflict' else line
        assert root == tmp_path / compatibility.REFERENCE
        assert args == ('rev-parse', f'{expected}:{compatibility.A2L.relative_to(compatibility.REFERENCE).as_posix()}')
        return fingerprint.blob(data)
    monkeypatch.setattr(compatibility, '_git', git)
    if failure:
        with pytest.raises(KbError):
            compatibility.check_reference(tmp_path)
    else:
        assert compatibility.check_reference(tmp_path) == expected


def test_missing_checkout_is_an_explicit_fingerprint_identity_without_parent_git_discovery(monkeypatch, tmp_path):
    def unexpected(*args):
        pytest.fail('missing submodule falls back to the parent repository')
    monkeypatch.setattr(compatibility, '_git', unexpected)
    assert compatibility.reference_commit(tmp_path) == 'absent'


def test_primary_fingerprint_changes_with_reference_identity_even_when_file_bytes_match(monkeypatch, tmp_path):
    monkeypatch.setattr(fingerprint, 'inputs', lambda root: [])
    actual = SimpleNamespace(value='a' * 40)
    monkeypatch.setattr(compatibility, 'reference_commit', lambda root: actual.value)
    before = fingerprint.compute(tmp_path)
    actual.value = 'b' * 40
    after = fingerprint.compute(tmp_path)
    assert before.blobs == {compatibility.PIN: 'a' * 40}
    assert after.blobs == {compatibility.PIN: 'b' * 40}
    assert before.value != after.value
