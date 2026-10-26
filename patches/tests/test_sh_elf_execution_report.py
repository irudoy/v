"""Ordinary tracebacks, flushed interruption evidence and checked stage coverage."""

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
def report(monkeypatch):
    monkeypatch.syspath_prepend(str(ROOT / 'tools/sh-elf-run'))
    return importlib.import_module('execution_report')


@pytest.mark.parametrize('fault', ['duration-bool', 'duration-nan', 'unfinished', 'name', 'status'])
def test_malformed_or_unfinished_stage_never_becomes_complete(report, capsys, fault):
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


def test_original_python_traceback_is_complete_and_exception_propagates(report):
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


def test_killed_process_leaves_flushed_start_and_no_success(report):
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
