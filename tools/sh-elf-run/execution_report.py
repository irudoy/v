"""Flushed stage boundaries and durations; never firmware qualification."""

from contextlib import contextmanager
import json
import math
import time
import uuid

PREFIX = 'VQ_SH_ELF_STAGE '
SCHEMA = 1


def _emit(value):
    print(PREFIX + json.dumps(value, sort_keys=True, separators=(',', ':')), flush=True)


@contextmanager
def stage(name, *, kind='pipeline'):
    """An abrupt process loss leaves an explicit start without a terminal event."""
    identity = uuid.uuid4().hex
    common = {'schema': SCHEMA, 'id': identity, 'name': name, 'kind': kind}
    started = time.perf_counter()
    _emit({**common, 'event': 'start'})
    try:
        yield
    except BaseException as error:
        _emit({**common, 'event': 'finish', 'status': 'failed',
               'elapsed_seconds': time.perf_counter() - started,
               'error_type': type(error).__name__})
        raise
    else:
        _emit({**common, 'event': 'finish', 'status': 'passed',
               'elapsed_seconds': time.perf_counter() - started})


def read(text, *, require_complete=False):
    """Read exact start/finish pairs without inferring a pass from partial output."""
    records = {}
    for line in text.splitlines():
        if not line.startswith(PREFIX):
            continue
        packet = json.loads(line[len(PREFIX):])
        identity = packet['id']
        if (type(packet['schema']) is not int or packet['schema'] != SCHEMA
                or type(identity) is not str or len(identity) != 32
                or any(char not in '0123456789abcdef' for char in identity)
                or type(packet['name']) is not str or not packet['name']
                or packet['kind'] not in ('pipeline', 'stock')):
            raise ValueError('invalid execution-stage identity')
        if packet['event'] == 'start':
            if identity in records:
                raise ValueError('duplicate execution-stage start')
            records[identity] = {'start': packet, 'finish': None}
        elif packet['event'] == 'finish':
            previous = records.get(identity)
            if previous is None or previous['finish'] is not None:
                raise ValueError('missing or duplicate execution-stage terminal')
            if any(packet[key] != previous['start'][key] for key in ('name', 'kind')):
                raise ValueError('execution-stage terminal names another stage')
            elapsed = packet['elapsed_seconds']
            if (type(elapsed) not in (int, float) or not math.isfinite(elapsed)
                    or elapsed < 0 or packet['status'] not in ('passed', 'failed')):
                raise ValueError('invalid execution-stage duration or status')
            previous['finish'] = packet
        else:
            raise ValueError('unknown execution-stage event')
    if require_complete and (not records or any(
            row['finish'] is None or row['finish']['status'] != 'passed'
            for row in records.values())):
        raise ValueError('execution-stage output is missing, unfinished or failed')
    return list(records.values())
