"""Exact-input completion records for coupled compatibility projections."""

from contextlib import contextmanager
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
import tempfile

import kb
from kb import repo

LABEL = 'CompatibilityState'
VERSION = 2


def progress(log, text):
    if log is print:
        log(text, flush=True)
    else:
        log(text)


@dataclass(frozen=True)
class Captured:
    """Immutable file bytes and serialized arguments actually used by a group."""

    files: tuple
    arguments: str

    def digest(self):
        from kb import compile
        payload = dict(version=VERSION, compiler=kb.__version__, schema=compile.SCHEMA,
                       python=list(sys.version_info[:3]),
                       files={name: hashlib.sha256(data).hexdigest() if data is not None else None
                              for name, data in self.files}, values=json.loads(self.arguments))
        text = json.dumps(payload, sort_keys=True, separators=(',', ':'), allow_nan=False)
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @contextmanager
    def tree(self, root, destinations):
        """Private byte copies, without links to mutable inputs or temporary path keys."""
        cache = root / repo.STATE / 'cache'
        cache.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='compatibility-inputs-', dir=cache) as temporary:
            directory = Path(temporary)
            written = {}
            for name, data in self.files:
                if name not in destinations or data is None:
                    continue
                relative = Path(destinations[name])
                if relative.is_absolute() or '..' in relative.parts or relative == Path('.'):
                    raise repo.KbError(f'invalid captured input destination {name}: {relative}', code=6)
                if relative in written:
                    if written[relative] != data:
                        raise repo.KbError(f'conflicting captured input destination {relative}', code=6)
                    continue
                written[relative] = data
                path = directory / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
                path.chmod(0o444)
            yield directory


@dataclass(frozen=True)
class Inputs:
    """Current physical readers and logical loader arguments, captured once per attempt."""

    files: object
    values: object
    required: tuple = ()

    def capture(self):
        files = self.files() if callable(self.files) else self.files
        values = self.values() if callable(self.values) else self.values
        found = {}
        for name, path in files:
            if name in found:
                raise repo.KbError(f'duplicate compatibility input {name}', code=6)
            try:
                found[name] = Path(path).read_bytes()
            except FileNotFoundError:
                if name in self.required:
                    raise repo.KbError(f'missing compatibility input {name}', code=6)
                found[name] = None
        arguments = json.dumps(values, sort_keys=True, separators=(',', ':'), allow_nan=False)
        return Captured(tuple(found.items()), arguments)

    def digest(self):
        return self.capture().digest()


class Completed:
    """Writer-owned evidence of complete projection, independent of Meta."""

    def __init__(self, graph, log=print):
        self.graph, self.log = graph, log
        rows = graph.run(f'MATCH (s:Kb:{LABEL}) RETURN s.key AS key, '
                         's.digest AS digest, s.version AS version, s.kind AS kind, s.rom AS rom')
        self.records = {}
        for row in rows:
            key = row.get('key')
            if key in self.records:
                raise repo.KbError(f'duplicate compatibility completion {key}', code=6)
            self.records[key] = row

    def invalidate(self, key):
        self.graph.run(f'MATCH (s:Kb:{LABEL} {{key:$key}}) DETACH DELETE s', key=key)
        self.records.pop(key, None)

    def roms(self):
        return [key for key, row in self.records.items() if row.get('kind') == 'rom']

    def run(self, key, inputs, build, *, kind, rom=None, invalidates=()):
        captured = inputs.capture()
        expected = captured.digest()
        previous = self.records.get(key, {})
        if (previous.get('version') == VERSION and previous.get('digest') == expected
                and previous.get('kind') == kind and previous.get('rom') == rom):
            progress(self.log, f'graph group: {key} current ({expected[:16]})')
            return False
        for dependent in invalidates:
            self.invalidate(dependent)
        self.invalidate(key)
        progress(self.log, f'graph group: {key} loading ({expected[:16]})')
        build(captured)
        if inputs.digest() != expected:
            raise repo.KbError(f'compatibility inputs change while building {key}; '
                               'completion and Meta are absent', code=6)
        props = dict(key=key, digest=expected, version=VERSION, kind=kind,
                     producer='derived', src='compiler')
        if rom is not None:
            props['rom'] = rom
        self.graph.run(f'MERGE (s:Kb:{LABEL} {{key:$key}}) SET s = $props', key=key, props=props)
        self.records[key] = props
        progress(self.log, f'graph group: {key} complete ({expected[:16]})')
        return True
