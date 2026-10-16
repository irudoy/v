"""Real parametrized pytest reports and original-terminal refusal contracts."""

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from kb import repo, test_contract as execution


CONTRACT = execution.Contract('controlled-values', (
    execution.Case('test_probe.py::test_value[False]', {'value': False}),
    execution.Case('test_probe.py::test_value[0]', {'value': 0}),
))


def capture():
    state = execution.Capture(CONTRACT, {'mode': 'rewrite', 'python_optimize': 0})
    state.collect([(case.nodeid, case.parameters) for case in CONTRACT.cases])
    for case in CONTRACT.cases:
        for phase in execution.PHASES:
            state.report(case.nodeid, phase, 'passed', False)
    return state


def test_observations_cannot_replace_actual_execution_reports():
    with pytest.raises(ValueError, match='cannot replace execution fields'):
        capture().candidate(0, complete=True, reports=[])


def test_proof_outputs_cannot_traverse_parent_directories(tmp_path):
    from kb import copy_evidence
    with pytest.raises(ValueError, match='parent directories'):
        copy_evidence.read_output(tmp_path, '../other-proof.json')


@pytest.mark.parametrize('fault', [
    'contract', 'unregistered', 'missing', 'duplicate', 'reordered', 'parameters',
    'parameter-type', 'missing-phase', 'failed', 'skipped', 'xfail', 'xpass',
    'unrelated-report', 'complete-int', 'exit-bool', 'schema-float', 'xfail-int',
    'plain-assertions', 'optimized', 'optimize-bool', 'invalid-run', 'missing-field',
])
def test_changed_execution_cannot_qualify_the_expected_contract(fault):
    candidate = capture().candidate(0, complete=True)
    assert CONTRACT.failure(candidate) is None
    if fault == 'contract':
        candidate['contract']['name'] = 'different-facts'
    elif fault == 'unregistered':
        candidate['contract']['cases'][0]['nodeid'] = 'test_unregistered.py::test_value'
    elif fault == 'missing':
        candidate['collected'].pop()
    elif fault == 'duplicate':
        candidate['collected'].append(candidate['collected'][0])
    elif fault == 'reordered':
        candidate['collected'].reverse()
    elif fault == 'parameters':
        candidate['parameters'][CONTRACT.cases[0].nodeid] = execution.encode({'value': 1})
    elif fault == 'parameter-type':
        candidate['parameters'][CONTRACT.cases[0].nodeid] = execution.encode({'value': 0})
    elif fault == 'missing-phase':
        candidate['reports'].pop()
    elif fault in ('failed', 'skipped'):
        candidate['reports'][1][2] = fault
    elif fault == 'xfail':
        candidate['reports'][1][2:] = ['skipped', True]
    elif fault == 'xpass':
        candidate['reports'][1][3] = True
    elif fault == 'unrelated-report':
        candidate['reports'].append(['test_other', 'call', 'passed', False])
    elif fault == 'complete-int':
        candidate['complete'] = 1
    elif fault == 'exit-bool':
        candidate['exitstatus'] = False
    elif fault == 'schema-float':
        candidate['schema'] = float(execution.SCHEMA)
    elif fault == 'xfail-int':
        candidate['reports'][1][3] = 0
    elif fault == 'plain-assertions':
        candidate['assertions']['mode'] = 'plain'
    elif fault == 'optimized':
        candidate['assertions']['python_optimize'] = 1
    elif fault == 'optimize-bool':
        candidate['assertions']['python_optimize'] = False
    elif fault == 'invalid-run':
        candidate['run_id'] = 'previous-pass'
    else:
        del candidate['reports']
    assert CONTRACT.failure(candidate) is not None


@pytest.fixture(scope='module')
def actual_pytest_runs(tmp_path_factory):
    """Keep pytest collection, fixture phases, assertion handling and reports real."""
    root = tmp_path_factory.mktemp('test-contract-pytest')
    (root / 'test_probe.py').write_text('''import os
import pytest

@pytest.fixture(autouse=True)
def setup():
    if os.environ['PROBE_MODE'] == 'setup-failed':
        raise RuntimeError('controlled setup failure')
    yield
    if os.environ['PROBE_MODE'] == 'teardown-failed':
        raise RuntimeError('controlled teardown failure')

@pytest.mark.parametrize('value', [False, 0])
@pytest.mark.xfail(os.environ['PROBE_MODE'] == 'xpass', reason='controlled xpass', strict=False)
def test_value(value):
    mode = os.environ['PROBE_MODE']
    if mode == 'skipped':
        pytest.skip('controlled skip')
    if mode == 'xfail':
        pytest.xfail('controlled xfail')
    assert mode != 'failed', 'controlled call failure'
    assert type(value) in (bool, int)
''')
    (root / 'conftest.py').write_text('''import json
import os
from pathlib import Path
import pytest
from kb import test_contract as execution

contract = execution.Contract('controlled-values', (
    execution.Case('test_probe.py::test_value[False]', {'value': False}),
    execution.Case('test_probe.py::test_value[0]', {'value': 0})))

def pytest_configure(config):
    config.capture = execution.Capture(contract, {
        'mode': config.getoption('assertmode'), 'python_optimize': 0})

def pytest_addoption(parser):
    parser.addoption('--kb-test-candidate')

def pytest_collection_finish(session):
    session.config.capture.collect([(item.nodeid, item.callspec.params)
                                    for item in session.items])

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    result = yield
    report = result.get_result()
    item.config.capture.report(item.nodeid, report.when, report.outcome,
                               hasattr(report, 'wasxfail'))

def pytest_sessionfinish(session, exitstatus):
    candidate = session.config.capture.candidate(exitstatus, complete=True)
    Path(os.environ['PROBE_CANDIDATE']).write_text(json.dumps(candidate))
    print('\\n' + execution.MARKER + execution.digest(candidate))
''')
    results = {}
    for mode in ('passed', 'failed', 'skipped', 'xfail', 'xpass', 'setup-failed', 'teardown-failed'):
        candidate = root / (mode + '-candidate.json')
        out, err = root / (mode + '.stdout'), root / (mode + '.stderr')
        command = [sys.executable, '-m', 'pytest', '-q', '--tb=short', '--rootdir=' + str(root),
                   *[case.nodeid for case in CONTRACT.cases],
                   execution.OPTION + str(candidate)]
        env = {**os.environ, 'PYTHONPATH': str(repo.ROOT / 'tools/kb/src'),
               'PYTEST_DISABLE_PLUGIN_AUTOLOAD': '1', 'PROBE_MODE': mode,
               'PROBE_CANDIDATE': str(candidate)}
        started, clock = datetime.now(timezone.utc).isoformat(), time.monotonic()
        with out.open('wb') as stdout, err.open('wb') as stderr:
            result = subprocess.run(command, cwd=root, env=env, stdout=stdout,
                                    stderr=stderr, timeout=15)
        process = {'command': command, 'actual_exit_code': result.returncode,
                   'timed_out': False, 'declared_limit_seconds': 15,
                   'inclusive_process_seconds': time.monotonic() - clock,
                   'started_utc': started, 'finished_utc': datetime.now(timezone.utc).isoformat(),
                   'stdout_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
                   'stderr_sha256': hashlib.sha256(err.read_bytes()).hexdigest()}
        process_path = root / (mode + '-process.json')
        process_path.write_text(json.dumps(process))
        results[mode] = {'candidate': json.loads(candidate.read_bytes()), 'process': process,
                         'candidate_path': candidate,
                         'process_path': process_path, 'stdout': out, 'stderr': err}
    return results


def test_actual_parametrized_collection_preserves_boolean_and_integer(actual_pytest_runs):
    result = actual_pytest_runs['passed']
    candidate = result['candidate']
    assert result['process']['actual_exit_code'] == 0
    assert CONTRACT.failure(candidate) is None
    assert candidate['parameters'][CONTRACT.cases[0].nodeid] != candidate['parameters'][CONTRACT.cases[1].nodeid]
    record = execution.bind_terminal(candidate, result['process_path'], result['stdout'],
                                     result['stderr'], result['candidate_path'].parent,
                                     CONTRACT, result['candidate_path'])
    assert execution.terminal_failure(record, result['candidate_path'].parent, CONTRACT) is None


@pytest.mark.parametrize('mode', ['failed', 'skipped', 'xfail', 'xpass', 'setup-failed', 'teardown-failed'])
def test_real_unsuccessful_or_incomplete_pytest_never_qualifies(actual_pytest_runs, mode):
    candidate = actual_pytest_runs[mode]['candidate']
    assert candidate['complete'] is False
    assert CONTRACT.failure(candidate) is not None


@pytest.fixture(params=['native', 'external'])
def bound_terminal(tmp_path, request):
    directory = tmp_path
    if request.param == 'external':
        directory = tmp_path.parent / (tmp_path.name + '-data')
        directory.mkdir()
        (tmp_path / 'tmp').mkdir()
        (tmp_path / 'tmp/local-results').symlink_to(directory, target_is_directory=True)
    candidate_path = directory / 'candidate.json'
    out, err, process_path = (directory / name for name in ('stdout', 'stderr', 'process.json'))
    candidate = capture().candidate(0, complete=True)
    candidate_path.write_text(execution.json_text(candidate))
    out.write_text(execution.MARKER + execution.digest(candidate) + '\n')
    err.write_bytes(b'')
    process = {'actual_exit_code': 0, 'timed_out': False,
               'command': ['pytest', *[case.nodeid for case in CONTRACT.cases],
                           execution.OPTION + str(candidate_path)],
               'declared_limit_seconds': 15, 'inclusive_process_seconds': 1.0,
               'started_utc': '2026-10-16T00:00:00+00:00',
               'finished_utc': '2026-10-16T00:00:01+00:00',
               'stdout_sha256': hashlib.sha256(out.read_bytes()).hexdigest(),
               'stderr_sha256': hashlib.sha256(err.read_bytes()).hexdigest()}
    process_path.write_text(json.dumps(process))
    record = execution.bind_terminal(candidate, process_path, out, err, tmp_path,
                                     CONTRACT, candidate_path)
    if request.param == 'external':
        assert record['process_path'] == 'tmp/local-results/process.json'
        assert record['terminal']['stdout'] == 'tmp/local-results/stdout'
        assert record['terminal']['stderr'] == 'tmp/local-results/stderr'
    return tmp_path, record


@pytest.mark.parametrize('fault', ['process-deleted', 'process-changed', 'terminal', 'stdout',
                                 'stderr', 'duplicate-marker', 'candidate', 'option'])
def test_original_process_and_streams_are_live_dependencies(bound_terminal, fault):
    root, record = bound_terminal
    assert execution.terminal_failure(record, root, CONTRACT) is None
    if fault == 'process-deleted':
        (root / record['process_path']).unlink()
    elif fault == 'process-changed':
        (root / record['process_path']).write_bytes(b'{}')
    elif fault == 'terminal':
        record['terminal']['inclusive_process_seconds'] = 0.5
    elif fault in ('stdout', 'stderr'):
        (root / record['terminal'][fault]).write_bytes(b'changed')
    elif fault == 'duplicate-marker':
        path = root / record['terminal']['stdout']
        path.write_bytes(path.read_bytes() * 2)
        process = json.loads((root / record['process_path']).read_bytes())
        process['stdout_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
        (root / record['process_path']).write_text(json.dumps(process))
        record['process_sha256'] = hashlib.sha256((root / record['process_path']).read_bytes()).hexdigest()
        record['terminal']['stdout_sha256'] = process['stdout_sha256']
    elif fault == 'candidate':
        record['candidate']['run_id'] = 'aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee'
    else:
        record['candidate_option'] += '-other'
    try:
        refused = execution.terminal_failure(record, root, CONTRACT)
    except (OSError, ValueError):
        refused = 'invalid original process'
    assert refused is not None


@pytest.mark.parametrize('fault', ['exit-bool', 'timeout-int', 'timeout', 'interrupted', 'elapsed-bool',
                                 'elapsed-nan', 'bound-bool', 'naive-time', 'reversed-time',
                                 'wrong-case', 'extra-candidate'])
def test_actual_terminal_requires_strict_success_and_finite_bound(bound_terminal, fault):
    _, record = bound_terminal
    process = deepcopy(record['terminal'])
    if fault == 'exit-bool':
        process['actual_exit_code'] = False
    elif fault == 'timeout-int':
        process['timed_out'] = 0
    elif fault == 'timeout':
        process['timed_out'] = True
    elif fault == 'interrupted':
        process['interrupted'] = True
    elif fault == 'elapsed-bool':
        process['inclusive_process_seconds'] = True
    elif fault == 'elapsed-nan':
        process['inclusive_process_seconds'] = float('nan')
    elif fault == 'bound-bool':
        process['declared_limit_seconds'] = True
    elif fault == 'naive-time':
        process['started_utc'] = '2026-10-16T00:00:00'
    elif fault == 'reversed-time':
        process['finished_utc'] = '2026-10-15T00:00:00+00:00'
    elif fault == 'wrong-case':
        process['command'].remove(CONTRACT.cases[0].nodeid)
    else:
        process['command'].append(execution.OPTION + 'other')
    with pytest.raises(ValueError):
        execution.terminal_check(process, CONTRACT, record['candidate_option'])
