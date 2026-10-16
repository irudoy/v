"""Independent adapter dispatch writes only a validated local job artifact."""

import hashlib
import json

import pytest

from kb import prepare_evidence as preparation


@pytest.fixture(params=['native', 'external'])
def controlled(tmp_path, monkeypatch, request):
    config = tmp_path / 'tools/kb/config.toml'
    config.parent.mkdir(parents=True)
    config.write_text('[lock]\ntimeout = 1\n')
    if request.param == 'external':
        external = tmp_path.parent / (tmp_path.name + '-data')
        external.mkdir()
        (tmp_path / 'tmp').mkdir()
        (tmp_path / 'tmp/local-results').symlink_to(external, target_is_directory=True)
    calls = []
    def adapter(name):
        def prepare(*args):
            calls.append((name, args))
            return {'controlled': name}
        return prepare
    monkeypatch.setattr(preparation.copy_witness, 'prepare', adapter('CAN'))
    monkeypatch.setattr(preparation.sid22_witness, 'prepare', adapter('SID22'))
    monkeypatch.setattr(preparation.test_evidence, 'prepare', adapter('TEST'))
    return tmp_path, calls


@pytest.mark.parametrize('protocol', ['CAN', 'SID22', 'TEST'])
def test_exact_adapter_receives_original_paths_and_writes_no_native_receipt(controlled, protocol):
    root, calls = controlled
    output = root / 'tmp/local-results/job/record.json'
    digest = preparation.prepare(protocol, 'process', 'stdout', 'stderr', output,
                                 candidate='candidate', root=root)
    assert calls == [(protocol, ('candidate', 'process', 'stdout', 'stderr', root)
                     if protocol == 'TEST' else ('process', 'stdout', 'stderr', root))]
    assert json.loads(output.read_bytes()) == {'controlled': protocol}
    assert digest == hashlib.sha256(output.read_bytes()).hexdigest()
    assert not list((root / '.kb').rglob('*receipts*'))


@pytest.mark.parametrize('fault', ['outside', 'existing', 'protocol', 'candidate'])
def test_invalid_or_ambiguous_preparation_cannot_publish_a_record(controlled, fault):
    root, calls = controlled
    output = root / 'tmp/local-results/job/record.json'
    protocol, candidate = 'TEST', 'candidate'
    if fault == 'outside': output = root / 'outside.json'
    elif fault == 'existing':
        output.parent.mkdir(parents=True)
        output.write_bytes(b'previous')
    elif fault == 'protocol': protocol = 'other'
    else: candidate = None
    with pytest.raises(ValueError):
        preparation.prepare(protocol, 'process', 'stdout', 'stderr', output,
                            candidate=candidate, root=root)
    assert calls == []
    assert output.read_bytes() == b'previous' if fault == 'existing' else not output.exists()


def test_refused_native_validation_has_no_preparation_output(controlled, monkeypatch):
    root, _ = controlled
    output = root / 'tmp/local-results/job/record.json'
    def refused(*args):
        raise ValueError('controlled semantic refusal')
    monkeypatch.setattr(preparation.copy_witness, 'prepare', refused)
    with pytest.raises(ValueError):
        preparation.prepare('CAN', 'process', 'stdout', 'stderr', output, root=root)
    assert not output.exists()


def test_preparation_hash_cannot_bind_substituted_output_bytes(controlled, monkeypatch):
    root, _ = controlled
    output = root / 'tmp/local-results/job/record.json'
    publish = preparation.test_evidence.publish
    def changed(path, record):
        publish(path, record)
        path.write_text('{"substituted":true}')
    monkeypatch.setattr(preparation.test_evidence, 'publish', changed)
    with pytest.raises(ValueError, match='changes before completion'):
        preparation.prepare('CAN', 'process', 'stdout', 'stderr', output, root=root)
