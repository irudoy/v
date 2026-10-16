"""Strict execution envelope shared by explicitly registered TEST adapters.

Collection and successful phases establish execution, not the supported facts.
Each adapter must independently bind its claim, observations and consumed inputs.
"""

from dataclasses import dataclass, fields, is_dataclass
from datetime import datetime
import hashlib
import json
import math
from pathlib import Path
import struct
import uuid

SCHEMA = 3
MARKER = 'kb-test-candidate sha256='
OPTION = '--kb-test-candidate='
PHASES = ('setup', 'call', 'teardown')


def encode(value):
    """Portable typed values; no model identities, reprs or set iteration."""
    if value is None or type(value) in (bool, int, str):
        return [type(value).__name__, value]
    if type(value) is float:
        return ['float64', struct.pack('>d', value).hex()]
    if isinstance(value, Path):
        return ['path', str(value)]
    if type(value) is bytes:
        return ['bytes', value.hex()]
    if type(value) in (list, tuple):
        return [type(value).__name__, [encode(v) for v in value]]
    if type(value) in (set, frozenset):
        return [type(value).__name__, sorted((encode(v) for v in value), key=json_text)]
    if type(value) is dict:
        return ['dict', sorted(([encode(k), encode(v)] for k, v in value.items()), key=json_text)]
    if is_dataclass(value) and not isinstance(value, type):
        return [type(value).__module__ + '.' + type(value).__qualname__,
                [[f.name, encode(getattr(value, f.name))] for f in fields(value)]]
    raise ValueError(f'unsupported witness value {type(value).__name__}')


def json_text(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


def digest(value):
    return hashlib.sha256(json_text(value).encode()).hexdigest()


def exact(left, right):
    """Equality that distinguishes booleans, integers and container types."""
    return encode(left) == encode(right)


@dataclass(frozen=True)
class Case:
    nodeid: str
    parameters: dict

    def packet(self):
        if (type(self.nodeid) is not str or not self.nodeid
                or type(self.parameters) is not dict
                or any(type(key) is not str for key in self.parameters)):
            raise ValueError('a TEST case requires a node ID and named typed parameters')
        return {'nodeid': self.nodeid, 'parameters': encode(self.parameters)}


@dataclass(frozen=True)
class Contract:
    name: str
    cases: tuple[Case, ...]

    def packet(self):
        if type(self.name) is not str or not self.name or not self.cases:
            raise ValueError('a TEST contract requires a name and explicit cases')
        cases = [case.packet() for case in self.cases]
        if len({case['nodeid'] for case in cases}) != len(cases):
            raise ValueError('a TEST contract repeats a collected node ID')
        return {'name': self.name, 'cases': cases}

    def failure(self, candidate):
        try:
            return self._failure(candidate)
        except (ValueError, TypeError, KeyError, AttributeError, RecursionError):
            return 'missing or invalid TEST execution candidate'

    def _failure(self, candidate):
        expected = self.packet()
        if type(candidate['schema']) is not int or candidate['schema'] != SCHEMA:
            return 'incompatible TEST execution candidate'
        if not exact(candidate['contract'], expected):
            return 'wrong registered TEST contract or parameters'
        run = candidate['run_id']
        if type(run) is not str or str(uuid.UUID(run)) != run:
            return 'TEST execution lacks a canonical run identity'
        nodeids = [case.nodeid for case in self.cases]
        parameters = {case.nodeid: encode(case.parameters) for case in self.cases}
        if (not exact(candidate['collected'], nodeids)
                or not exact(candidate['parameters'], parameters)):
            return 'wrong collected TEST cases or actual parameters'
        reports = [[nodeid, phase, 'passed', False] for nodeid in nodeids for phase in PHASES]
        if not exact(candidate['reports'], reports):
            return 'TEST execution has missing, skipped, failed, xfail or unrelated phases'
        if (candidate['complete'] is not True or type(candidate['exitstatus']) is not int
                or candidate['exitstatus'] != 0):
            return 'TEST execution candidate is unfinished or failing'
        if not exact(candidate['assertions'], {'mode': 'rewrite', 'python_optimize': 0}):
            return 'TEST execution requires enabled pytest assertion rewriting'
        return None


class Capture:
    """Actual pytest collection and reports, including unexpected cases."""

    def __init__(self, contract, assertions):
        self.contract, self.assertions = contract, assertions
        self.collected, self.parameters, self.reports = [], {}, []

    def collect(self, cases):
        self.collected = [nodeid for nodeid, _ in cases]
        self.parameters = {nodeid: encode(parameters) for nodeid, parameters in cases}

    def report(self, nodeid, phase, outcome, wasxfail):
        self.reports.append([nodeid, phase, outcome, wasxfail])

    def candidate(self, exitstatus, *, complete, **observations):
        candidate = {'schema': SCHEMA, 'run_id': str(uuid.uuid4()),
                     'contract': self.contract.packet(), 'collected': self.collected,
                     'parameters': self.parameters, 'reports': self.reports,
                     'assertions': self.assertions, 'complete': complete,
                     'exitstatus': int(exitstatus)}
        if set(candidate) & set(observations):
            raise ValueError('TEST observations cannot replace execution fields')
        candidate.update(observations)
        if self.contract.failure(candidate) is not None:
            candidate['complete'] = False
        return candidate


def terminal_check(process, contract, candidate_option):
    if (type(process['actual_exit_code']) is not int or process['actual_exit_code'] != 0
            or process['timed_out'] is not False
            or process.get('interrupted', False) is not False):
        raise ValueError('the actual TEST process did not finish successfully')
    command = process['command']
    if (type(command) is not list or any(type(arg) is not str for arg in command)
            or not candidate_option.startswith(OPTION) or candidate_option == OPTION
            or [arg for arg in command if arg.startswith(OPTION)] != [candidate_option]
            or any(case.nodeid not in command for case in contract.cases)):
        raise ValueError('the actual TEST process names another case or candidate')
    bound, elapsed = process['declared_limit_seconds'], process['inclusive_process_seconds']
    if (type(bound) is not int or bound <= 0 or type(elapsed) not in (int, float)
            or not math.isfinite(elapsed) or not 0 <= elapsed <= bound + 1):
        raise ValueError('the TEST process lacks its actual finite execution bound')
    start, end = (datetime.fromisoformat(process[key]) for key in ('started_utc', 'finished_utc'))
    if start.tzinfo is None or end.tzinfo is None or end < start:
        raise ValueError('the TEST process lacks its actual terminal interval')


def _read(root, path):
    from kb import copy_evidence
    return copy_evidence.read_output(root, path)


def terminal_failure(record, root, contract):
    """Re-read original terminal and streams; never substitute a stored verdict."""
    refused = contract.failure(record['candidate'])
    if refused:
        return refused
    process_bytes = _read(root, record['process_path'])
    if hashlib.sha256(process_bytes).hexdigest() != record['process_sha256']:
        return 'TEST execution original process receipt changed'
    original = json.loads(process_bytes)
    terminal = record['terminal']
    terminal_check(original, contract, record['candidate_option'])
    expected = {**original, **{name: terminal[name] for name in ('stdout', 'stderr')}}
    if not exact(terminal, expected):
        return 'TEST execution terminal disagrees with its original process'
    for stream in ('stdout', 'stderr'):
        data = _read(root, terminal[stream])
        if hashlib.sha256(data).hexdigest() != original[stream + '_sha256']:
            return 'TEST execution terminal streams changed'
    markers = [line for line in _read(root, terminal['stdout']).decode().splitlines()
               if line.startswith(MARKER)]
    if markers != [MARKER + digest(record['candidate'])]:
        return 'TEST execution candidate is not bound to terminal output'
    return None


def bind_terminal(candidate, process_path, stdout_path, stderr_path, root, contract, candidate_path):
    """Bind a candidate to one completed original runner invocation."""
    from kb import local_paths
    refused = contract.failure(candidate)
    if refused:
        raise ValueError(refused)
    process_bytes = Path(process_path).read_bytes()
    original = json.loads(process_bytes)
    option = OPTION + str(candidate_path)
    terminal_check(original, contract, option)
    root = Path(root).resolve()
    record = {'candidate': candidate, 'process_path': str(Path(process_path).resolve()),
              'process_sha256': hashlib.sha256(process_bytes).hexdigest(),
              'candidate_option': option,
              'terminal': {**original, 'stdout': str(Path(stdout_path).resolve()),
                           'stderr': str(Path(stderr_path).resolve())}}
    # Prefer checkout-relative paths; controlled callers may supply external artifacts.
    for container, key in ((record, 'process_path'), (record['terminal'], 'stdout'),
                           (record['terminal'], 'stderr')):
        path = Path(container[key])
        try:
            container[key] = local_paths.owned(path, root).relative_to(root).as_posix()
        except ValueError:
            # Controlled TEST callers already support unrelated external files.
            pass
    refused = terminal_failure(record, root, contract)
    if refused:
        raise ValueError(refused)
    return record
