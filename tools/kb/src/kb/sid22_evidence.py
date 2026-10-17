"""Exact typed scope of the JK08A DID-table pointer-read witness.

Descriptor validation establishes byte and ownership bindings. It does not
qualify an execution or award a knowledge level without an independent receipt.
"""

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import tomllib

from kb import repo
from kb.model import SymbolKey

SCHEMA = 1
KEY = 'sid22-v1:jk08a-pointer-read'
PREFIX = 'sid22-'
DESCRIPTOR = 'defs/JK08A.sid22-pointer-read.toml'
RECEIPT = '.kb/sid22-receipts/jk08a-pointer-read.json'
REGION = 'jk08a-sid22-pointer-read'
MARKER = 'kb-sid22-candidate '
FUNCTION = SymbolKey('7mfk', 'fn', 0x3235c)
FUNCTION_MEANING = 'married-moth/fn'
IMAGE_SHA256 = 'ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23'
BACKING_SHA256 = '21589cdc96127a922d7f81f9305f49779718749aede97d8cbc915c5101598986'
BODY = ((0x3235c, 0x32474), (0x32484, 0x32578), (0x325a8, 0x3270e),
        (0x32712, 0x32834), (0x32864, 0x328b8))
TABLES = ((0x11, 0x226ac, 0x2289c, 4), (0x12, 0x2289c, 0x229e0, 4),
          (0x13, 0x229e0, 0x22a88, 8))
MEMBERS_DIGEST = '5f5b383d5aa037828329c0df244526a30db52478813eb8d21cc3a3a9d4e90a1b'
BINDINGS_DIGEST = '6b0bfd6233fbe91727809ee42fa15c2349aa0ef34057d9b1e7e00cb406ea6040'
EXECUTION_FILES = (
    DESCRIPTOR, 'tools/diagnostics/sid22_inventory.py',
    'tools/sh-elf-run/run.sh', 'tools/sh-elf-run/docker_lifecycle.py', 'tools/sh-elf-run/Dockerfile',
    'tools/sh-elf-run/verify_map_switching.py', 'tools/sh-elf-run/verify_stock_code.py',
    'tools/sh-elf-run/execution_report.py',
    'tools/sh-elf-run/qualified_gate.py', 'tools/sh-elf-run/process_record.py',
    'tools/sh-elf-run/elf_storage_layout.py', 'tools/sh-elf-run/can_latch_copy.py',
    'defs/JK08A.can-latch-copy.toml',
    'tools/sh-elf-run/sid22_pointer_read.py',
    'tools/sh-elf-run/stock_jk08a_sid22_pointer_read.s',
    'tools/sh-elf-run/harness-stock-jk08a-sid22-pointer-read.c',
    'tools/sh-elf-run/invoke-sid22-pointer-read.s',
    'tools/sh-elf-run/sid22-pointer-read-cases.h',
)


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def _read(root, path):
    from kb import copy_evidence
    return copy_evidence._read(root, path)


def inputs(root=repo.ROOT):
    """Exact interpreter, executable sources, configuration and stock identity."""
    root = Path(root)
    paths = {*EXECUTION_FILES, 'rom-images/roms.csv', 'rom-images/homology.toml',
             repo.CONFIG.as_posix()}
    paths.update(path.relative_to(root).as_posix()
                 for path in (root / 'tools/kb/src/kb').rglob('*.py'))
    image = repo.images(root)['JK08A']
    paths.add(image.path.relative_to(root).as_posix())
    return {path: hashlib.sha256(_read(root, path)).hexdigest() for path in sorted(paths)}


@dataclass(frozen=True)
class Member:
    meaning: str
    address: int
    declared_width: int | None
    claim_sha256: str


@dataclass(frozen=True)
class Binding:
    member: str
    did: int
    record: int
    source_offset: int | None
    # Each element is the independently addressed source of one output byte.
    read_addresses: tuple[int, ...]


@dataclass(frozen=True)
class Descriptor:
    members: tuple[Member, ...]
    bindings: tuple[Binding, ...]
    body: tuple[tuple[int, int], ...]
    pools: tuple[tuple[int, int], ...]

    def member(self, meaning):
        matches = [row for row in self.members if row.meaning == meaning]
        if len(matches) != 1:
            raise ValueError('the DID witness does not support this storage meaning')
        return matches[0]


def registered(evidence, symbol=None):
    key = evidence.get('key')
    return (isinstance(key, str) and key.startswith(PREFIX)
            or evidence.get('path') == DESCRIPTOR
            or evidence.get('mode') == 'did-pointer')


def item(meaning):
    return dict(kind='indirect', mode='did-pointer', key=KEY, path=DESCRIPTOR,
                at='7mfk:0003235c', to=FUNCTION, supports='identity',
                value=dict(reader=meaning))


def _integer(value, expected=None):
    return type(value) is int and (expected is None or value == expected)


def descriptor(root=repo.ROOT, *, value=None):
    """Validate complete code/pools, immutable membership and actual pointers."""
    if value is None:
        value = tomllib.loads(_read(root, DESCRIPTOR).decode('utf-8'))
    if (not _integer(value['schema'], SCHEMA) or value['id'] != KEY
            or value['layout'] != '7mfk' or value['image'] != 'JK08A'
            or value['image_sha256'] != IMAGE_SHA256):
        raise ValueError('the descriptor identifies another DID witness')
    for key, expected in dict(entry=0x3235c, natural_return=0x328b4,
            return_delay=0x328b6, body_bytes=1256,
            backing_start=0x3235c, backing_end=0x328c0).items():
        if not _integer(value[key], expected):
            raise ValueError(f'the descriptor has another {key}')
    image = repo.images(root)['JK08A']
    data = _read(root, image.path.relative_to(root).as_posix())
    if hashlib.sha256(data).hexdigest() != IMAGE_SHA256 or image.sha256 != IMAGE_SHA256:
        raise ValueError('the exact DID stock image changed')
    if (value['backing_sha256'] != BACKING_SHA256
            or hashlib.sha256(data[0x3235c:0x328c0]).hexdigest() != BACKING_SHA256):
        raise ValueError('the complete publisher backing changed')
    if len(value['code']) != len(BODY):
        raise ValueError('the descriptor omits a publisher body range')
    for row, (start, end) in zip(value['code'], BODY):
        if (set(row) != {'start', 'end', 'sha256'}
                or not _integer(row['start'], start) or not _integer(row['end'], end)
                or row['sha256'] != hashlib.sha256(data[start:end]).hexdigest()):
            raise ValueError('the descriptor truncates or changes a body range')
    # Decode PC-relative literal addressing directly from exact instruction words.
    expected_pools = {}
    for start, end in BODY:
        for site in range(start, end, 2):
            word = int.from_bytes(data[site:site + 2], 'big')
            opcode = word >> 12
            if opcode not in (9, 13):
                continue
            width = 2 if opcode == 9 else 4
            pool = site + 4 if width == 2 else (site & ~3) + 4
            pool += (word & 255) * width
            row = expected_pools.setdefault(pool, dict(address=pool, width_bytes=width,
                value=int.from_bytes(data[pool:pool + width], 'big'), loads=[]))
            if row['width_bytes'] != width:
                raise ValueError('the publisher has overlapping literal widths')
            row['loads'].append(site)
    expected = [expected_pools[key] for key in sorted(expected_pools)]
    if _digest(value['pool']) != _digest(expected):
        raise ValueError('the descriptor omits or changes a PC-relative pool or load')
    if len(value['table']) != len(TABLES):
        raise ValueError('the descriptor has other DID families')
    for row, (high, start, end, stride) in zip(value['table'], TABLES):
        expected = dict(family=high, start=start, end=end, stride=stride,
            sha256=hashlib.sha256(data[start:end]).hexdigest(),
            firmware_index_bound='after-first-pointer-load' if high == 0x13 else 'none')
        if _digest(row) != _digest(expected):
            raise ValueError('the table bytes, stride or actual bounds order changed')
    if _digest(value['member']) != MEMBERS_DIGEST or _digest(value['binding']) != BINDINGS_DIGEST:
        raise ValueError('the exact 50 members or 55 source bindings changed')
    members = tuple(Member(row['meaning'], row['address'],
        None if row['declared_width'] == 'unset' else row['declared_width'],
        row['claim_sha256']) for row in value['member'])
    by_meaning = {row.meaning: row for row in members}
    bindings = []
    for row in value['binding']:
        did = row['did']
        high, low = did >> 8, did & 255
        _, start, end, stride = next(table for table in TABLES if table[0] == high)
        record = start + low * stride
        if row['record'] != record or record + stride > end or did == 0x120b:
            raise ValueError('the proof selector does not name a supported pointer record')
        pointers = tuple(int.from_bytes(data[site:site + 4], 'big')
                         for site in range(record, record + stride, 4))
        special = low in ({0x00, 0x20, 0x40, 0x60} if high == 0x11
                          else {0x00, 0x20, 0x40} if high == 0x12 else {0x00})
        if special:
            addresses = tuple(pointers[0] + offset for offset in range(4))
        elif high == 0x13:
            addresses = pointers
        else:
            addresses = tuple(pointers[0] + offset for offset in range(1 if high == 0x11 else 2))
        offset = None if row['source_offset'] == 'unset' else row['source_offset']
        expected_address = addresses[0 if offset is None else offset]
        if expected_address != by_meaning[row['member']].address or 0xffffffff in pointers:
            raise ValueError('the pointer record does not read its claimed RAM source')
        bindings.append(Binding(row['member'], did, record, offset, addresses))
    return Descriptor(members, tuple(bindings), BODY,
                      tuple((row['address'], row['width_bytes']) for row in value['pool']))


def _member(model, symbol, contract):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or symbol.meaning is None or FUNCTION not in model.symbols):
        raise ValueError('the DID proof requires its owning model and symbol')
    member = contract.member(symbol.meaning.key)
    if (symbol.key != SymbolKey('7mfk', 'ram', member.address)
            or symbol.value('width') != member.declared_width):
        raise ValueError('the DID source layout, address or declared width changed')
    return member


def _link(model, symbol, member, contract, *, attached=False):
    from kb import copy_evidence, reconciliation
    evidence = item(member.meaning)
    function = model.symbols[FUNCTION]
    if function.meaning is None or function.meaning.key != FUNCTION_MEANING:
        raise ValueError('the DID publisher meaning changed')
    links = [link for link in model.links if link.owner is symbol.meaning
             and link.to is function.meaning and link.type == 'reader'
             and '7mfk' in (link.props.get('layouts') or ['7mfk'])]
    if len(links) != 1:
        raise ValueError('the DID proof requires one exact original reader')
    link = links[0]
    count = sum(entry == evidence for entry in link.evidence)
    if count not in ((1,) if attached else (0, 1)):
        raise ValueError('the DID proof requires its unique owning link attachment')
    original = copy_evidence.claim_fields(link, '7mfk')
    original['evidence'] = [entry for entry in original['evidence'] if entry != evidence]
    if reconciliation.digest(original) != member.claim_sha256:
        raise ValueError('the supported reader semantics changed')
    for binding in contract.bindings:
        if binding.member != member.meaning:
            continue
        did = model.symbols.get(SymbolKey('7mfk', 'did', binding.record))
        if (did is None or did.meaning is None or did.value('number') != binding.did
                or did.value('width') != len(binding.read_addresses)):
            raise ValueError('the decoder-owned DID identity or response width changed')
        sources = [entry for entry in model.links if entry.owner is did.meaning
                   and entry.to is symbol.meaning and entry.type == 'source']
        if (len(sources) != 1 or sources[0].slot is not None
                or sources[0].offset != binding.source_offset or sources[0].roles):
            raise ValueError('the DID SOURCE pointer-slot binding changed')
    return link


def validate_item(evidence, symbol, model, claim='identity', *, contract=None):
    """Bind an item to its exact existing reader, not merely a DID SOURCE edge."""
    from kb.test_evidence import encode
    if model is None:
        raise ValueError('the DID proof requires its owning model')
    contract = contract or descriptor(model.root)
    member = _member(model, symbol, contract)
    if encode(evidence) != encode(item(member.meaning)):
        raise ValueError('the DID proof item has another exact typed scope')
    if claim != 'identity' and (getattr(claim, 'name', None) != 'identity'
            or getattr(claim, 'subject', None) not in (
                symbol.key.key, member.meaning, member.meaning.rsplit('/', 1)[0])):
        raise ValueError('the DID witness supports only its identity-claim context')
    _link(model, symbol, member, contract, attached=True)
    return member


def scope_digest(model):
    """Full incident facts of the exact readers, publisher and selected DIDs."""
    from kb import convert
    from kb.test_evidence import digest, encode
    contract = descriptor(model.root)
    for path in model.overlay:
        path = Path(path)
        if path.is_absolute() or '..' in path.parts or (
                (not path.parts or path.parts[0] != 'kb') and path != repo.OWNER_CONFIG):
            raise ValueError('an overlay changes SID22 execution inputs')
    meanings = {FUNCTION_MEANING: model.symbols[FUNCTION].meaning}
    for member in contract.members:
        symbol = model.symbols[SymbolKey('7mfk', 'ram', member.address)]
        _member(model, symbol, contract)
        _link(model, symbol, member, contract)
        meanings[member.meaning] = symbol.meaning
    for binding in contract.bindings:
        meaning = model.symbols[SymbolKey('7mfk', 'did', binding.record)].meaning
        meanings[meaning.key] = meaning
    value = lambda data: convert._value(model, data)
    members = {row.meaning for row in contract.members}
    owners = []
    for key, meaning in sorted(meanings.items()):
        links = []
        for link in model.links:
            if link.owner is not meaning and link.to is not meaning:
                continue
            from kb import copy_evidence
            evidence = copy_evidence.semantic_evidence(link)
            if link.owner.key in members and link.to.key == FUNCTION_MEANING and link.type == 'reader':
                evidence = [entry for entry in evidence if entry != item(link.owner.key)]
            links.append((link.owner.key, link.type, link.to.key, link.slot, link.offset,
                          value(link.props), value(evidence), link.roles, link.stated, link.sources))
        owners.append(dict(key=key, kind=meaning.kind, semantic=meaning.semantic,
            props=value(meaning.props), tables=value(meaning.tables), names=meaning.other_names,
            sources=meaning.sources, tier=meaning.tier, name_sources=meaning.name_sources,
            groups=value(meaning.groups),
            statuses={name: (status.state, value(status.props), value(status.evidence), status.sources)
                      for name, status in meaning.statuses.items()},
            symbols={name: (symbol.key, symbol.name, symbol.generated, symbol.former,
                           value(symbol.props), value(symbol.evidence), symbol.sources, symbol.implicit)
                     for name, symbol in meaning.symbols.items()}, links=links))
    settings = {key: data for key, data in model.config.items()
                if key not in ('names', 'reconciliation', 'source_bindings')}
    return digest(encode(dict(owners=owners, layouts=model.layouts, spaces=model.spaces,
                              functions=model.functions, settings=settings)))


def dependencies(root, *, receipt=None):
    paths = {RECEIPT}
    try:
        record = json.loads(_read(root, RECEIPT) if receipt is None else receipt)
        named = [record['process_path'], *(record['terminal'][name] for name in ('stdout', 'stderr'))]
        if any(type(path) is not str or Path(path).is_absolute() or '..' in Path(path).parts for path in named):
            raise ValueError('invalid SID22 local proof paths')
        paths.update(named)
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return paths


def terminal_check(process):
    from kb import copy_evidence
    copy_evidence.terminal_check(process)
    if process['command'] != ['tools/sh-elf-run/run.sh', '--can-copy-witness', '--sid22-witness']:
        raise ValueError('the complete primary SID22 witness process did not succeed')


def failure(evidence, symbol=None, model=None, claim=None, *, record=None):
    if not registered(evidence, symbol):
        return None
    try:
        from kb import sid22_witness
        from kb.test_evidence import digest, json_text
        validate_item(evidence, symbol, model, claim)
        record = json.loads(_read(model.root, RECEIPT)) if record is None else record
        candidate = record['candidate']
        if type(record['schema']) is not int or record['schema'] != SCHEMA:
            return 'wrong SID22 execution protocol'
        if candidate['scope'] != scope_digest(model) or candidate['inputs'] != inputs(model.root):
            return 'SID22 execution facts or inputs are stale'
        sid22_witness.validate(candidate, model.root)
        terminal = record['terminal']
        terminal_check(terminal)
        original_bytes = _read(model.root, record['process_path'])
        if hashlib.sha256(original_bytes).hexdigest() != record['process_sha256']:
            return 'SID22 original process receipt changed'
        original = json.loads(original_bytes)
        if any(terminal.get(name) != value for name, value in original.items() if name not in ('stdout', 'stderr')):
            return 'SID22 terminal disagrees with its original process'
        streams = {name: _read(model.root, terminal[name]) for name in ('stdout', 'stderr')}
        if any(hashlib.sha256(data).hexdigest() != terminal[name + '_sha256'] for name, data in streams.items()):
            return 'SID22 execution streams changed'
        lines = streams['stdout'].decode().splitlines()
        if ([line[len(MARKER):] for line in lines if line.startswith(MARKER)] != [json_text(candidate)]
                or sum(line.startswith('VQ_SH_ELF_VERIFY status=PASS ') for line in lines) != 1):
            return 'SID22 execution lacks its unique full primary packet'
        if record['native_model'] != candidate['native_model'] or record['native_inputs'] != digest(candidate['producer_inputs']):
            return 'SID22 producer provenance lacks independent finalization'
        return None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError):
        return 'missing or invalid qualified SID22 execution context'


def accepted(model, symbol, function, claim):
    from kb import copy_evidence
    if function.key != FUNCTION or claim['type'] != 'reader':
        return None
    entries = [entry for entry in claim['evidence'] if registered(entry, symbol)]
    if len(entries) != 1 or failure(entries[0], symbol, model, 'identity') is not None:
        return None
    contract = descriptor(model.root)
    member = _member(model, symbol, contract)
    if claim != copy_evidence.claim_fields(_link(model, symbol, member, contract, attached=True), symbol.layout):
        return None
    return dict(proof=KEY, publisher='7mfk:0003235c', scope='did-pointer-read', support='identity')


def retires(before, after, old_claim):
    from kb import reconciliation
    try:
        if old_claim['to'] != FUNCTION_MEANING or old_claim['type'] != 'reader' or any(
                registered(entry) for entry in old_claim['evidence']):
            return False
        candidates = [(storage, function, claim) for storage, function, claim in reconciliation.access_claims(after)
                      if reconciliation.claim_identity(claim) == reconciliation.claim_identity(old_claim)]
        if len(candidates) != 1:
            return False
        storage, function, claim = candidates[0]
        evidence = item(storage.meaning.key)
        if claim['evidence'] != [*old_claim['evidence'], evidence] or {**claim, 'evidence': old_claim['evidence']} != old_claim:
            return False
        original = before.symbols[storage.key]
        if original.value('width') != storage.value('width') or scope_digest(before) != scope_digest(after):
            return False
        return accepted(after, storage, function, claim) is not None
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return False
