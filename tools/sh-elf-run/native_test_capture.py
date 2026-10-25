"""Declared ABI and raw observations for existing stock harness invocations.

The capture surrounds the existing driver ABI. Its memory-before packet is
driver memory, while native entry/exit frames remain in the observer output.
No packet or captured subset grants a semantic claim or replaces the full gate.
"""

from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import re

TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
HEADER = 'tools/sh-elf-run/native-test-capture.h'
WRAPPER = 'tools/sh-elf-run/native_test_capture.c'
NAME = re.compile(r'[A-Za-z_][A-Za-z0-9_]*')
REGION = re.compile(r'[A-Za-z0-9_-]+')
CTYPE = re.compile(r'(?:struct )?[A-Za-z_][A-Za-z0-9_]*')
MEMBER = re.compile(r'[A-Za-z_][A-Za-z0-9_]*(?:\[[0-9]+\])?(?:\.[A-Za-z_][A-Za-z0-9_]*(?:\[[0-9]+\])?)*')
PREFIX = 'vq-native-test-'


def integer(value, low=0, high=0xffffffff):
    if type(value) is not int or not low <= value <= high:
        raise ValueError('native TEST capture requires an exact bounded integer')
    return value


def name(value, pattern=NAME):
    if type(value) is not str or pattern.fullmatch(value) is None:
        raise ValueError('native TEST capture requires a declared identifier')
    return value


@dataclass(frozen=True)
class Field:
    side: str
    member: str
    offset: int
    size: int

    def packet(self, context_size, observation_size):
        if self.side not in ('context', 'observation'):
            raise ValueError('native TEST ABI fields select their declared side')
        name(self.member, MEMBER)
        integer(self.offset)
        integer(self.size, 1, 65536)
        if self.offset + self.size > (context_size if self.side == 'context' else observation_size):
            raise ValueError('native TEST ABI field exceeds its actual structure')
        return dict(side=self.side, name=self.member, offset=self.offset, size=self.size)


@dataclass(frozen=True)
class Span:
    key: str
    original: int
    alias: int
    size: int

    def packet(self):
        name(self.key)
        integer(self.original)
        integer(self.alias)
        integer(self.size, 1, 65536)
        if max(self.original, self.alias) + self.size > 0x100000000:
            raise ValueError('native TEST memory span wraps its address space')
        return dict(name=self.key, original=self.original, alias=self.alias, size=self.size)


@dataclass(frozen=True)
class Selection:
    index: int
    entry: int

    def packet(self, invocations):
        return dict(index=integer(self.index, 0, invocations - 1), entry=integer(self.entry))


@dataclass(frozen=True)
class Spec:
    region: str
    observer_symbol: str
    context_type: str
    observation_type: str
    context_size: int
    observation_size: int
    fields: tuple[Field, ...]
    spans: tuple[Span, ...]
    selected: tuple[Selection, ...]
    invocations: int

    @classmethod
    def from_packet(cls, packet):
        """Consume an explicit repository declaration without parameter inference."""
        if type(packet) is not dict:
            raise ValueError('native TEST capture requires a complete specification packet')
        spec = cls(region=packet['region'], observer_symbol=packet['observer_symbol'],
            context_type=packet['context_type'], observation_type=packet['observation_type'],
            context_size=packet['context_size'], observation_size=packet['observation_size'],
            fields=tuple(Field(row['side'], row['name'], row['offset'], row['size'])
                         for row in packet['fields']),
            spans=tuple(Span(row['name'], row['original'], row['alias'], row['size'])
                        for row in packet['spans']),
            selected=tuple(Selection(row['index'], row['entry']) for row in packet['selected']),
            invocations=packet['invocations'])
        if _canonical(spec.packet()) != _canonical(packet):
            raise ValueError('native TEST capture declaration changes its exact specification schema')
        return spec

    def packet(self):
        name(self.region, REGION)
        name(self.observer_symbol)
        name(self.context_type, CTYPE)
        name(self.observation_type, CTYPE)
        integer(self.context_size, 1, 4096)
        integer(self.observation_size, 1, 65536)
        integer(self.invocations, 1)
        if any(type(value) is not tuple or not value for value in (self.fields, self.spans, self.selected)):
            raise ValueError('native TEST capture requires explicit immutable fields, spans and selections')
        fields = [field.packet(self.context_size, self.observation_size) for field in self.fields]
        spans = [span.packet() for span in self.spans]
        selected = [case.packet(self.invocations) for case in self.selected]
        if len({(field['side'], field['name']) for field in fields}) != len(fields):
            raise ValueError('native TEST ABI repeats a field')
        if len({span['name'] for span in spans}) != len(spans):
            raise ValueError('native TEST capture repeats a memory identity')
        indices = [case['index'] for case in selected]
        if indices != sorted(set(indices)):
            raise ValueError('native TEST capture selections omit their unique original order')
        for index, first in enumerate(spans):
            for second in spans[index + 1:]:
                if (first['alias'] < second['alias'] + second['size']
                        and second['alias'] < first['alias'] + first['size']
                        and first['original'] - first['alias'] != second['original'] - second['alias']):
                    raise ValueError('native TEST overlapping aliases refer to different physical bytes')
        return dict(schema=1, region=self.region, observer_symbol=self.observer_symbol,
            context_type=self.context_type, observation_type=self.observation_type,
            context_size=self.context_size, observation_size=self.observation_size,
            fields=fields, spans=spans, selected=selected, invocations=self.invocations)

    def abi_packet(self):
        packet = self.packet()
        return {key: packet[key] for key in ('schema', 'region', 'context_size',
                                            'observation_size', 'fields', 'spans')}


def appendix(spec):
    """Compile actual sizeof/offsetof facts in the original harness translation unit."""
    packet = spec.packet()
    lines = ['', '#include <stddef.h>', '#include "native-test-capture.h"',
        f'_Static_assert(sizeof({spec.context_type}) == {spec.context_size}U, "native TEST context ABI");',
        f'_Static_assert(sizeof({spec.observation_type}) == {spec.observation_size}U, "native TEST observation ABI");']
    for field in spec.fields:
        type_ = spec.context_type if field.side == 'context' else spec.observation_type
        for indexed in re.finditer(r'\[([0-9]+)\]', field.member):
            array = field.member[:indexed.start()]
            lines.append(f'_Static_assert({int(indexed[1])}U < '
                f'sizeof((({type_} *)0)->{array}) / sizeof((({type_} *)0)->{array}[0]), '
                '"native TEST field array bound");')
        lines += [f'_Static_assert(offsetof({type_}, {field.member}) == {field.offset}U, "native TEST field offset");',
                  f'_Static_assert(sizeof((({type_} *)0)->{field.member}) == {field.size}U, "native TEST field size");']
    lines.append('static const struct vq_native_capture_field vq_native_fields[] = {')
    for field in spec.fields:
        type_ = spec.context_type if field.side == 'context' else spec.observation_type
        lines.append('    {' + f'{json.dumps(field.side)}, {json.dumps(field.member)}, '
            f'offsetof({type_}, {field.member}), sizeof((({type_} *)0)->{field.member})' + '},')
    lines += ['};', 'static const struct vq_native_capture_span vq_native_spans[] = {']
    for span in packet['spans']:
        lines.append('    {' + f'{json.dumps(span["name"])}, {span["original"]:#x}U, '
            f'{span["alias"]:#x}U, {span["size"]}U' + '},')
    lines += ['};', 'static const uint32_t vq_native_selected[] = {',
              '    ' + ', '.join(str(row['index']) + 'U' for row in packet['selected']), '};',
              'const struct vq_native_capture_spec vq_native_capture_spec = {',
              f'    {json.dumps(spec.region)}, sizeof({spec.context_type}), sizeof({spec.observation_type}),',
              f'    {len(spec.fields)}U, vq_native_fields, {len(spec.spans)}U, vq_native_spans,',
              f'    {len(spec.selected)}U, vq_native_selected', '};', '']
    return '\n'.join(lines).encode('ascii')


def _source_path(root, path):
    path = Path(path).resolve()
    try:
        relative = path.relative_to(root)
    except ValueError as error:
        raise ValueError('native TEST capture source escapes its checkout') from error
    if not relative.parts or not (relative.parts[:2] == ('tools', 'sh-elf-run') or relative.parts[0] == 'patches'):
        raise ValueError('native TEST capture accepts only declared executable source trees')
    if path.suffix not in ('.c', '.h', '.s', '.inc'):
        raise ValueError('native TEST capture has an unsupported executable include')
    return relative


def consumed_sources(root, region, observer):
    """Read the complete declared local quoted-include closure."""
    root = Path(root).resolve()
    if any(type(filename) is not str or Path(filename).name != filename
           for filename in (region.harness, region.source, observer)):
        raise ValueError('the standard native TEST ABI requires declared stock source basenames')
    consumed = {}
    pending = [root / 'tools/sh-elf-run' / name_ for name_ in (region.harness, region.source, observer)]
    pending += [root / HEADER, root / WRAPPER]
    include = re.compile(rb'^\s*(?:#include|\.include)\s+"([^"]+)"', re.M)
    while pending:
        source = pending.pop()
        relative = _source_path(root, source)
        name_ = relative.as_posix()
        if name_ in consumed:
            continue
        data = source.read_bytes()
        consumed[name_] = data
        pending += [source.parent / match[1].decode('ascii') for match in include.finditer(data)]
    return consumed


def snapshot(root, region, observer, spec, directory):
    """Private consumed bytes preserve the complete original harness as a prefix."""
    packet = spec.packet()
    if spec.region != region.key or spec.invocations != region.cases:
        raise ValueError('the standard native TEST ABI requires the complete one-invocation-per-case region')
    consumed = consumed_sources(root, region, observer)
    private = Path(directory) / 'native-test-consumed'
    for name_, data in consumed.items():
        target = private / name_
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    source_dir = private / 'tools/sh-elf-run'
    original = consumed['tools/sh-elf-run/' + region.harness]
    generated = original + appendix(spec)
    harness = source_dir / ('native-' + region.harness)
    harness.write_bytes(generated)
    return dict(spec=packet, consumed=consumed, harness=harness, source_dir=source_dir,
        generated_harness=generated, original_harness=original,
        linker_symbol='_' + spec.observer_symbol,
        wrapper_symbol='__wrap__' + spec.observer_symbol,
        real_symbol='__real__' + spec.observer_symbol)


def require_snapshot(root, captured):
    """Refuse changes to either the original source or its consumed private copy."""
    root = Path(root).resolve()
    private = captured['source_dir'].parents[1]
    for path, data in captured['consumed'].items():
        if (root / path).read_bytes() != data or (private / path).read_bytes() != data:
            raise ValueError('native TEST executable source changes during consumption')
    if captured['harness'].read_bytes() != captured['generated_harness']:
        raise ValueError('native TEST augmented harness changes during consumption')


class Session:
    """Explicit raw-capture obligations carried by one complete stock producer.

    The stock verifier still executes every mandatory region. A completed
    session is an observation packet, not a qualified TEST or access receipt.
    """

    def __init__(self, specs):
        if type(specs) is not tuple or not specs:
            raise ValueError('native TEST capture requires immutable explicit region specifications')
        self._specs, self._packets, self._records = {}, {}, {}
        for spec in specs:
            if type(spec) is not Spec:
                raise ValueError('native TEST capture requires a declared standard ABI specification')
            packet = spec.packet()
            if spec.region in self._specs:
                raise ValueError('native TEST capture repeats a stock region')
            self._specs[spec.region] = spec
            self._packets[spec.region] = _canonical(packet)
        self._bound = False
        self._finished = False

    def bind(self, regions, observers, reserved):
        if self._bound or self._records or self._finished:
            raise ValueError('native TEST capture belongs to one original stock invocation')
        current = {region.key: region for region in regions}
        if len(current) != len(regions):
            raise ValueError('the stock registry repeats a region identity')
        for key, spec in self._specs.items():
            if key in reserved:
                raise ValueError('native TEST capture cannot replace an existing primary witness protocol')
            region = current.get(key)
            if region is None or key not in observers or spec.invocations != region.cases:
                raise ValueError('native TEST capture lacks its complete registered stock ABI region')
            for case in spec.selected:
                if case.entry % 2 or not any(start <= case.entry < end for start, end in region.code_spans):
                    raise ValueError('native TEST capture selects an entry outside its reconstructed stock code')
            self._require_spec(key)
        self._bound = True

    def _require_spec(self, key):
        spec = self._specs[key]
        if _canonical(spec.packet()) != self._packets[key]:
            raise ValueError('native TEST capture specification changes during execution')
        return spec

    def select(self, region):
        if not self._bound or self._finished:
            raise ValueError('native TEST capture has no live bound stock invocation')
        if region.key not in self._specs:
            return None
        if region.key in self._records:
            raise ValueError('native TEST capture repeats an original region execution')
        return self._require_spec(region.key)

    def record(self, root, region, captured, *, image, fixture, executable,
               observer_object, reconstruction, command, result, toolchain):
        spec = self.select(region)
        if spec is None:
            raise ValueError('native TEST capture receives an unregistered region')
        require_snapshot(root, captured)
        if result.returncode != 0:
            raise ValueError('native TEST capture lacks a successful original simulator exit')
        marker = f'VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} cases={region.cases}'
        if result.stdout.splitlines().count(marker) != 1:
            raise ValueError('native TEST capture lacks its unique complete original PASS marker')
        observations = observe(result.stdout, spec)
        self._records[region.key] = dict(
            region=json.loads(_canonical(asdict(region))), capture=observations,
            consumed={path: data.hex() for path, data in sorted(captured['consumed'].items())},
            augmented_harness=captured['generated_harness'].hex(),
            code=reconstruction['code'], pools=reconstruction['pools'],
            image_sha256=hashlib.sha256(image).hexdigest(),
            fixture_sha256=hashlib.sha256(fixture).hexdigest(),
            elf_sha256=hashlib.sha256(executable).hexdigest(),
            observer_object_sha256=hashlib.sha256(observer_object).hexdigest(),
            command=[str(arg) for arg in command],
            simulator=dict(returncode=result.returncode,
                stdout_sha256=hashlib.sha256(result.stdout.encode()).hexdigest(),
                stderr_sha256=hashlib.sha256(result.stderr.encode()).hexdigest()),
            stdout=result.stdout, stderr=result.stderr,
            toolchain=toolchain, semantic_admission=False)

    def finish(self):
        if not self._bound or self._finished or self._records.keys() != self._specs.keys():
            raise ValueError('native TEST capture omits or repeats a complete original region')
        for key in self._specs:
            self._require_spec(key)
        self._finished = True
        return dict(schema=1, kind='native-test-raw', semantic_admission=False,
                    regions=[self._records[key] for key in self._specs])


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True, separators=(',', ':'), allow_nan=False)


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate native TEST observation key')
        result[key] = value
    return result


def _hex(value, size):
    if (type(value) is not str or len(value) != size * 2
            or re.fullmatch(r'[0-9a-f]*', value) is None):
        raise ValueError('native TEST observation has an incomplete raw byte field')
    return value


def observe(stdout, spec):
    """Parse actual ordered packets; raw observations do not qualify a fact."""
    from kb.test_contract import exact
    expected = spec.packet()
    packets = []
    for line in stdout.splitlines():
        if line.startswith(PREFIX):
            tag, separator, body = line.partition(' ')
            if not separator:
                raise ValueError('native TEST capture has a truncated packet')
            packets.append((tag[len(PREFIX):], json.loads(body, object_pairs_hook=_object)))
    order = ['abi', *[tag for _ in spec.selected for tag in ('before', 'after')], 'terminal']
    if [tag for tag, _ in packets] != order:
        raise ValueError('native TEST capture omits, duplicates or reorders actual observations')
    if not exact(packets[0][1], spec.abi_packet()):
        raise ValueError('native TEST capture uses another compiled C ABI or memory view')
    terminal = dict(schema=1, region=spec.region, invocations=spec.invocations, captured=len(spec.selected))
    if not exact(packets[-1][1], terminal):
        raise ValueError('native TEST capture lacks its complete original invocation count')
    observations = []
    for ordinal, selected in enumerate(spec.selected):
        before, after = packets[1 + ordinal * 2][1], packets[2 + ordinal * 2][1]
        if (type(before) is not dict or type(after) is not dict
                or set(before) != {'schema','region','index','entry','driver_context','driver_memory'}
                or set(after) != {'schema','region','index','entry','observation','driver_context_after','driver_memory'}):
            raise ValueError('native TEST capture changes its raw observation schema')
        identity = dict(schema=1, region=spec.region, index=selected.index, entry=selected.entry)
        if not all(exact({key: value[key] for key in identity}, identity) for value in (before, after)):
            raise ValueError('native TEST capture binds another entry or case')
        _hex(before['driver_context'], spec.context_size)
        _hex(after['driver_context_after'], spec.context_size)
        _hex(after['observation'], spec.observation_size)
        if before['driver_context'] != after['driver_context_after']:
            raise ValueError('the native observer changes its declared const input context')
        for packet in (before, after):
            memory = packet['driver_memory']
            if type(memory) is not list or len(memory) != len(spec.spans):
                raise ValueError('native TEST capture omits a declared memory view')
            for value, span in zip(memory, spec.spans):
                _hex(value, span.size)
        observations.append(dict(before=before, after=after))
    return dict(spec=expected, abi=packets[0][1], terminal=terminal, observations=observations,
                stdout_sha256=hashlib.sha256(stdout.encode()).hexdigest(), semantic_admission=False)
