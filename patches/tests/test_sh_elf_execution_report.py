"""Ordinary tracebacks, flushed interruption evidence and checked stage coverage."""

from copy import deepcopy
import importlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def modules(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools/sh-elf-run'))
    return importlib.import_module('execution_report'), importlib.import_module('acceptance')


def test_all_groups_partition_the_actual_stock_registry_and_resolve_includes(modules):
    _, contract = modules
    document, regions = contract.declared(), contract.registered()
    result = contract.check(document, regions)
    assert result['categories'] == {'pipeline': 8, 'stock': 11, 'evidence_and_acceptance': 5}
    assert result['groups'] == sum(result['categories'].values())
    stock = next(group for group in document['group'] if group['id'] == 'upstream_fuel')
    sources = contract.direct_sources(stock, regions)
    assert 'tools/sh-elf-run/base-accumulator-cases.h' in sources
    assert 'tools/sh-elf-run/stock_jk08a_base_accumulator.s' in sources


def test_producer_source_manifest_binds_feature_and_shared_dependencies(tmp_path, monkeypatch):
    from kb import copy_witness, fingerprint
    monkeypatch.setattr(fingerprint, 'inputs', lambda root: [])
    monkeypatch.setattr(copy_witness.proof, 'EXECUTION_FILES', ())
    consumed = ('patches/composer.py', 'patches/feature.s', 'patches/identity.h',
                'patches/profile.toml', 'patches/schema.json', 'tools/shared/helper.py',
                'tools/sh-elf-run/harness.c', 'tools/sh-elf-run/cases.h')
    unrelated = ('patches/tests/test_probe.py', 'tools/tests/test_probe.py', 'patches/README.md')
    for path in (*consumed, *unrelated):
        destination = tmp_path / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text('controlled source')
    before = copy_witness.provenance(tmp_path)
    assert set(before) == set(consumed)
    for path in consumed:
        original = (tmp_path / path).read_bytes()
        (tmp_path / path).write_bytes(original + b' changed')
        assert copy_witness.provenance(tmp_path)[path] != before[path]
        (tmp_path / path).write_bytes(original)
    assert copy_witness.provenance(tmp_path) == before


@pytest.mark.parametrize('fault', ['missing-group', 'duplicate-group', 'category', 'scope',
                                 'missing-region', 'duplicate-region', 'foreign-region',
                                 'unknown-source', 'guarded-source', 'minimality', 'schema-bool'])
def test_unchecked_or_weakened_boundaries_refuse(modules, fault):
    _, contract = modules
    document = deepcopy(contract.declared())
    stock = next(group for group in document['group'] if group['category'] == 'stock')
    if fault == 'missing-group': document['group'].pop()
    elif fault == 'duplicate-group': document['group'].append(document['group'][0])
    elif fault == 'category': stock['category'] = 'pipeline'
    elif fault == 'scope': document['qualification_policy'] = 'skip unchanged regions'
    elif fault == 'missing-region': stock['regions'].pop()
    elif fault == 'duplicate-region': stock['regions'].append(stock['regions'][0])
    elif fault == 'foreign-region': stock['regions'][0] = 'unregistered-region'
    elif fault == 'unknown-source': stock['source_anchors'].append('missing-file.py')
    elif fault == 'guarded-source': stock['source_anchors'].append('kb/fn/controlled.toml')
    elif fault == 'minimality': stock['minimality'] = 'minimal'
    else: document['schema'] = True
    with pytest.raises(ValueError):
        contract.check(document, contract.registered())


def test_actual_stage_report_refuses_omission_reordering_and_duplicate_names(modules, capsys):
    report, contract = modules
    regions = contract.registered()
    names = [('pipeline', name) for name in contract.PRIMARY_STAGES]
    names += [('stock', region.key) for region in regions]
    for kind, name in names:
        with report.stage(name, kind=kind):
            pass
    text = capsys.readouterr().out
    assert len(contract.check_stages(text, regions)) == len(names)
    lines = text.splitlines(keepends=True)
    for mutated in (''.join(lines[2:]), ''.join(lines[2:4] + lines[:2] + lines[4:]), text + text):
        with pytest.raises(ValueError):
            contract.check_stages(mutated, regions)


@pytest.mark.parametrize('fault', ['duration-bool', 'duration-nan', 'unfinished', 'name', 'status'])
def test_malformed_or_unfinished_stage_never_becomes_complete(modules, capsys, fault):
    report, _ = modules
    with report.stage('controlled'):
        pass
    packets = [json.loads(line[len(report.PREFIX):]) for line in capsys.readouterr().out.splitlines()]
    if fault == 'duration-bool': packets[1]['elapsed_seconds'] = False
    elif fault == 'duration-nan': packets[1]['elapsed_seconds'] = float('nan')
    elif fault == 'unfinished': packets.pop()
    elif fault == 'name': packets[1]['name'] = 'unrelated'
    else: packets[1]['status'] = 'unknown'
    text = '\n'.join(report.PREFIX + json.dumps(packet) for packet in packets)
    with pytest.raises(ValueError):
        report.read(text, require_complete=True)


def test_original_python_traceback_is_complete_and_exception_propagates(modules):
    report, _ = modules
    source = '''from execution_report import stage
def controlled_failure():
    raise RuntimeError('controlled diagnostic terminal')
with stage('controlled_failure'):
    controlled_failure()
'''
    terminal = subprocess.run([sys.executable, '-c', source],
        env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools/sh-elf-run')},
        text=True, capture_output=True, timeout=10)
    assert terminal.returncode != 0
    assert 'Traceback (most recent call last)' in terminal.stderr
    assert 'in controlled_failure' in terminal.stderr
    assert terminal.stderr.rstrip().endswith('RuntimeError: controlled diagnostic terminal')
    rows = report.read(terminal.stdout)
    assert len(rows) == 1 and rows[0]['finish']['status'] == 'failed'
    assert rows[0]['finish']['error_type'] == 'RuntimeError'
    with pytest.raises(ValueError):
        report.read(terminal.stdout, require_complete=True)


def test_killed_process_leaves_flushed_start_and_no_success(modules):
    report, _ = modules
    source = '''from execution_report import stage
import signal
with stage('controlled_abrupt_loss'):
    signal.pause()
'''
    process = subprocess.Popen([sys.executable, '-c', source],
        env={**os.environ, 'PYTHONPATH': str(ROOT / 'tools/sh-elf-run')},
        text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        import selectors
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            assert selector.select(timeout=5), 'stage start was not flushed'
            started = process.stdout.readline()
        process.send_signal(signal.SIGKILL)
        stdout, stderr = process.communicate(timeout=5)
    finally:
        if process.poll() is None:
            process.kill()
            process.communicate(timeout=5)
    assert process.returncode == -signal.SIGKILL and stderr == ''
    rows = report.read(started + stdout)
    assert len(rows) == 1 and rows[0]['finish'] is None
    with pytest.raises(ValueError):
        report.read(started + stdout, require_complete=True)
