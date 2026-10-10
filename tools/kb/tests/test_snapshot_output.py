"""Snapshot output failures are actionable and cannot overwrite receipts."""
import json

import pytest

from kb import transition
from kb.repo import KbError


def test_missing_snapshot_parent_is_created_under_tmp(tmp_path):
    output = tmp_path / 'tmp' / 'acceptance' / 'snapshot.json'
    assert transition._snapshot_path(output, tmp_path) == output
    assert output.parent.is_dir() and not output.exists()
    transition._write_snapshot(output, {'source_commit': 'accepted'})
    assert json.loads(output.read_text()) == {'source_commit': 'accepted'}


@pytest.mark.parametrize('case', ['existing', 'outside', 'symlink', 'file-parent'])
def test_invalid_output_paths_refuse_before_compilation(tmp_path, monkeypatch, case):
    base = tmp_path / 'tmp'
    base.mkdir()
    output = base / 'snapshot.json'
    if case == 'existing':
        output.write_text('original receipt')
    elif case == 'outside':
        output = tmp_path / 'outside.json'
    elif case == 'symlink':
        (base / 'escape').symlink_to(tmp_path, target_is_directory=True)
        output = base / 'escape' / 'outside.json'
    else:
        (base / 'blocked').write_text('file, not a directory')
        output = base / 'blocked' / 'snapshot.json'
    monkeypatch.setattr(transition.compile, 'build', lambda *args, **kwargs: pytest.fail('invalid output must refuse before compilation'))
    with pytest.raises(KbError) as refused:
        transition.snapshot('accepted', output, tmp_path)
    assert refused.value.code == 2
    if case == 'existing':
        assert output.read_text() == 'original receipt'


def test_output_created_after_validation_is_preserved(tmp_path):
    output = transition._snapshot_path(tmp_path / 'tmp' / 'snapshot.json', tmp_path)
    output.write_text('another completed receipt')
    with pytest.raises(KbError) as refused:
        transition._write_snapshot(output, {'source_commit': 'accepted'})
    assert refused.value.code == 2
    assert output.read_text() == 'another completed receipt'
