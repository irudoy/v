"""Prepared records supply a scoped read view and never publish receipts."""

import hashlib
import json

import pytest

from kb import copy_evidence as proof, sid22_evidence, test_evidence


@pytest.fixture
def prepared(tmp_path):
    root = tmp_path
    results = root / 'tmp/local-results'
    results.mkdir(parents=True)
    names = (proof.RECEIPT, sid22_evidence.RECEIPT, str(test_evidence.RECEIPT))
    references, old, new = {}, {}, {}
    for index, name in enumerate(names):
        actual = root / name
        actual.parent.mkdir(parents=True, exist_ok=True)
        old[name] = json.dumps({'old':index}).encode()
        actual.write_bytes(old[name])
        path = results / f'prepared-{index}.json'
        new[name] = json.dumps({'prepared':index}).encode()
        path.write_bytes(new[name])
        references[name] = dict(path=str(path), sha256=hashlib.sha256(new[name]).hexdigest())
    return root, references, old, new


def test_three_prepared_records_replace_only_the_primitive_view(prepared):
    root, references, old, new = prepared
    with proof.consuming(root):
        assert {name:proof.read_output(root, name) for name in old} == old
        with proof.prepared_publication(root, references):
            assert {name:proof.read_output(root, name) for name in old} == new
            assert {name:(root / name).read_bytes() for name in old} == old
            assert proof.failure(proof.item('reader'), record=json.loads(new[proof.RECEIPT])) is not None
        assert {name:proof.read_output(root, name) for name in old} == old
    assert {name:(root / name).read_bytes() for name in old} == old


@pytest.mark.parametrize('fault', ('missing', 'extra', 'seal', 'schema', 'outside-results'))
def test_an_unsealed_or_incomplete_prepared_set_refuses_before_consumption(prepared, fault):
    root, held, old, _ = prepared
    references = {name:dict(value) for name,value in held.items()}
    first = next(iter(references))
    if fault == 'missing':
        references.pop(first)
    elif fault == 'extra':
        references['unregistered-receipt.json'] = dict(references[first])
    elif fault == 'seal':
        references[first]['sha256'] = '0' * 64
    elif fault == 'schema':
        references[first]['exclude'] = []
    else:
        path = root / 'outside.json'
        path.write_bytes(b'{}')
        references[first] = dict(path=str(path), sha256=hashlib.sha256(b'{}').hexdigest())
    with pytest.raises(ValueError):
        with proof.prepared_publication(root, references):
            pytest.fail('invalid prepared set reaches a consumer')
    assert proof._PREPARED_PUBLICATION.get() is None
    assert {name:(root / name).read_bytes() for name in old} == old


def test_changed_prepared_bytes_restore_the_outer_snapshot_and_refuse(prepared):
    root, references, old, _ = prepared
    with proof.consuming(root):
        with pytest.raises(ValueError, match='changes during native writes'):
            with proof.prepared_publication(root, references):
                path = next(iter(references.values()))['path']
                from pathlib import Path
                Path(path).write_bytes(b'{"changed":true}')
        assert {name:proof.read_output(root, name) for name in old} == old
    assert proof._PREPARED_PUBLICATION.get() is None
    assert {name:(root / name).read_bytes() for name in old} == old
