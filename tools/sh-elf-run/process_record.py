"""Capture one bounded original child and exact live streams for qualification."""

from datetime import datetime, timezone
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

from docker_lifecycle import write_json
from kb import local_paths


class ProcessInterrupted(BaseException):
    """Cancellation must not be swallowed as an ordinary interrupted I/O call."""


@dataclass(frozen=True)
class Snapshot:
    paths: tuple
    process_bytes: bytes
    streams: tuple
    record: dict


def snapshot(paths):
    paths = tuple(Path(path) for path in paths)
    original = paths[0].read_bytes()
    record = json.loads(original)
    streams = tuple(path.read_bytes() for path in paths[1:])
    for name, data in zip(('stdout', 'stderr'), streams):
        if hashlib.sha256(data).hexdigest() != record[name + '_sha256']:
            raise ValueError('the original process stream hash disagrees')
    return Snapshot(paths, original, streams, record)


def require_unchanged(value):
    if any(path.read_bytes() != data for path, data in
           zip(value.paths, (value.process_bytes, *value.streams))):
        raise ValueError('an original process or stream changes after capture')


def _utc():
    return datetime.now(timezone.utc).isoformat()


def run(root, directory, name, command, limit, *, live=True):
    """Write a terminal only after the original child terminates.

    SIGKILL can prevent a terminal record. Missing records cannot qualify;
    the primary lifecycle independently refuses a surviving Docker child.
    """
    root = Path(root).resolve()
    directory = local_paths.owned(directory, root).resolve()
    if (type(limit) is not int or limit <= 0
            or not command or any(type(arg) is not str for arg in command)):
        raise ValueError('a local original command and positive finite bound are required')
    directory.mkdir(parents=True, exist_ok=True)
    terminal_path = directory / (name + '-process.json')
    out_path, err_path = (directory / (name + '.' + kind) for kind in ('stdout', 'stderr'))
    start_path = directory / (name + '-started.json')
    if any(path.exists() for path in (terminal_path, out_path, err_path, start_path)):
        raise ValueError('an original process output already exists')
    started, clock = _utc(), time.monotonic()
    deadline = clock + limit
    process, interrupted, timed_out, drain_deadline = None, None, False, None
    previous_term = signal.getsignal(signal.SIGTERM)

    def terminate(signum, frame):
        raise ProcessInterrupted(f'original process interrupted by signal {signum}')

    def kill():
        if process is not None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass

    signal.signal(signal.SIGTERM, terminate)
    try:
        with out_path.open('xb') as out, err_path.open('xb') as err:
            try:
                process = subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE, start_new_session=True)
            except OSError as error:
                write_json(directory / (name + '-start-error.json'), dict(
                    command=command, started_utc=started, child_started=False,
                    error=type(error).__name__ + ': ' + str(error)))
                raise
            write_json(start_path, dict(command=command, started_utc=started,
                pid=process.pid, pgid=process.pid, declared_limit_seconds=limit))
            destinations = {'stdout': out, 'stderr': err}

            def consume(kind, data):
                destinations[kind].write(data)
                destinations[kind].flush()
                if live:
                    stream = sys.stdout if kind == 'stdout' else sys.stderr
                    stream.buffer.write(data)
                    stream.buffer.flush()

            try:
                with selectors.DefaultSelector() as selector:
                    selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
                    selector.register(process.stderr, selectors.EVENT_READ, 'stderr')
                    while selector.get_map():
                        if time.monotonic() >= deadline and not timed_out:
                            timed_out = True
                            kill()
                            drain_deadline = time.monotonic() + 5
                        if drain_deadline is not None and time.monotonic() >= drain_deadline:
                            break
                        for key, _ in selector.select(timeout=0.1):
                            data = os.read(key.fileobj.fileno(), 65536)
                            if data:
                                consume(key.data, data)
                            else:
                                selector.unregister(key.fileobj)
                    try:
                        process.wait(timeout=max(0, deadline - time.monotonic()))
                    except subprocess.TimeoutExpired:
                        timed_out = True
                        kill()
                        process.wait(timeout=5)
            except BaseException as error:
                interrupted = type(error).__name__
                kill()
                remaining_out, remaining_err = process.communicate(timeout=5)
                consume('stdout', remaining_out)
                consume('stderr', remaining_err)
                if not isinstance(error, (KeyboardInterrupt, ProcessInterrupted)):
                    raise
    finally:
        signal.signal(signal.SIGTERM, previous_term)
        if process is not None and process.poll() is None:
            kill()
            process.wait(timeout=5)
    record = dict(command=command, started_utc=started, finished_utc=_utc(),
        inclusive_process_seconds=time.monotonic() - clock,
        actual_exit_code=process.returncode, timed_out=timed_out,
        interrupted=interrupted is not None, interruption_type=interrupted,
        declared_limit_seconds=limit,
        stdout_sha256=hashlib.sha256(out_path.read_bytes()).hexdigest(),
        stderr_sha256=hashlib.sha256(err_path.read_bytes()).hexdigest())
    write_json(terminal_path, record)
    return terminal_path, out_path, err_path


def require_success(record):
    if (type(record['actual_exit_code']) is not int or record['actual_exit_code'] != 0
            or record['timed_out'] is not False or record['interrupted'] is not False):
        raise ValueError('the original child did not complete successfully')
