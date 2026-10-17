"""Shared qualification entry points and local snapshots for access witnesses."""

import hashlib
import json
from pathlib import Path
import tomllib
from datetime import datetime
import math
from contextlib import contextmanager
from contextvars import ContextVar

from kb import local_paths, repo, sh2
from kb.model import SymbolKey
from kb.test_evidence import digest, encode, json_text, publish

SCHEMA = 2
PREFIX = 'can-copy-'
KEY = 'can-copy-v1:jk08a-latch-12'
DESCRIPTOR = 'defs/JK08A.can-latch-copy.toml'
RECEIPT = '.kb/copy-receipts/jk08a-latch-12.json'
REGION = 'jk08a-can-latch-copy'
FUNCTION = SymbolKey('7mfk', 'fn', 0x20dfe)
MEMBERS = {'reader': ('tunneling-swift/ram', 0xffff419b),
           'writer': ('prehistoric-horse/ram', 0xffff418f)}
MEMBER_KEYS = frozenset(SymbolKey('7mfk', 'ram', address) for _, address in MEMBERS.values())
EXECUTION_FILES = (
    DESCRIPTOR, 'tools/kb/src/kb/copy_evidence.py', 'tools/kb/src/kb/local_paths.py',
    'tools/sh-elf-run/run.sh', 'tools/sh-elf-run/docker_lifecycle.py', 'tools/sh-elf-run/Dockerfile',
    'tools/sh-elf-run/verify_map_switching.py',
    'tools/sh-elf-run/execution_report.py',
    'tools/sh-elf-run/qualified_gate.py', 'tools/sh-elf-run/process_record.py',
    'tools/sh-elf-run/verify_stock_code.py',
    'tools/sh-elf-run/elf_storage_layout.py',
    'tools/sh-elf-run/stock_jk08a_can_latch_copy.s',
    'tools/sh-elf-run/harness-stock-jk08a-can-latch-copy.c',
    'tools/sh-elf-run/invoke-can-latch-copy.s',
    'tools/sh-elf-run/can-latch-copy-cases.h',
    'tools/sh-elf-run/can_latch_copy.py',
    'defs/JK08A.injection-copy.toml',
    'tools/sh-elf-run/injection_snapshot_copy.py',
    'tools/sh-elf-run/harness-injection-snapshot-capture.c',
    'tools/sh-elf-run/stock_jk08a_injection_snapshot.s',
    'tools/sh-elf-run/harness-stock-jk08a-injection-snapshot.c',
    'tools/sh-elf-run/injection-snapshot-cases.h',
    'tools/sh-elf-run/stock_injection_start_delay_invoke.s',
)
MARKER = 'kb-copy-candidate '
_CONSUMED = ContextVar('can_copy_consumed_outputs', default=None)


def _registered(item, symbol=None):
    key = item.get('key')
    return ((isinstance(key, str) and key.startswith(PREFIX))
            or item.get('path') == DESCRIPTOR
            or item.get('mode') == 'block-copy')


def registered(item, symbol=None):
    from kb import injection_copy_evidence, sid22_evidence
    return (_registered(item, symbol) or sid22_evidence.registered(item, symbol)
            or injection_copy_evidence.registered(item, symbol))


def item(direction):
    return dict(kind='indirect', mode='block-copy', key=KEY, path=DESCRIPTOR,
                at='7mfk:00021096', to=FUNCTION, supports='identity',
                value=dict(direction=direction, offset_bytes=7, width_bits=8))


def _read(root, path):
    path = Path(path)
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('a copy proof input must be inside the repository')
    return read_output(root, path)


def read_output(root, path):
    """Read one local proof output from the verdict's primitive snapshot."""
    from kb import match
    path = Path(path)
    if '..' in path.parts:
        raise ValueError('a local proof output cannot traverse parent directories')
    match.READ.add(path.as_posix())
    bound = _CONSUMED.get()
    if bound is not None and Path(root).resolve() == bound[0] and path.as_posix() in bound[1]:
        data = bound[1][path.as_posix()]
        if data is None:
            raise FileNotFoundError(path)
        return data
    return local_paths.read_path(path, root).read_bytes()


def descriptor(root):
    value = tomllib.loads(_read(root, DESCRIPTOR).decode('utf-8'))
    if (type(value['schema']) is not int or value['schema'] != 1 or value['id'] != KEY
            or value['layout'] != '7mfk' or value['image'] != 'JK08A'
            or value['copy'] != dict(source=0xffff4194, destination=0xffff4188,
                                    length_bytes=12, member_offset_bytes=7, overlap=False)):
        raise ValueError('the descriptor describes another copy')
    caller = value['caller']
    for name, expected in dict(meaning='coherent_snapshot/fn', function=0x20dfe,
            entry=0x21094, call=0x21096, delay_slot=0x21098, end=0x2109a,
            callee=0x22558, callee_end=0x22590, r1_load=0x21066,
            r11_load=0x20eea, context_end=0x21094).items():
        if caller.get(name) != expected:
            raise ValueError(f'the descriptor has another {name}')
    expected_members = [dict(direction=direction, meaning=meaning, address=address,
                             width_bits=8, declared_width='unset')
                        for direction, (meaning, address) in MEMBERS.items()]
    if value['member'] != expected_members:
        raise ValueError('the descriptor has other copy members')
    image = repo.images(root)['JK08A']
    image_path = image.path.relative_to(root).as_posix()
    data = _read(root, image_path)
    if hashlib.sha256(data).hexdigest() != image.sha256:
        raise ValueError('the stock image disagrees with its catalog')
    spans = [(0x21066, 0x2109a), (0x22558, 0x22590)]
    if len(value['code']) != len(spans):
        raise ValueError('the descriptor omits code')
    for row, (start, end) in zip(value['code'], spans):
        if row['start'] != start or bytes.fromhex(row['bytes']) != data[start:end]:
            raise ValueError('the descriptor disagrees with exact stock code')
    pools = [(0x21234, 0xffff4188), (0x2125c, 0xffff4194), (0x210f4, 0x22558)]
    if value['pool'] != [dict(address=address, value=word) for address, word in pools]:
        raise ValueError('the descriptor has other pointer pools')
    for address, word in pools:
        if int.from_bytes(data[address:address + 4], 'big') != word:
            raise ValueError('the stock pointer pool changed')
    for site, register, pool in ((0x21066, 1, 0x21234), (0x21094, 2, 0x2125c),
                                  (0x20eea, 11, 0x210f4)):
        word = int.from_bytes(data[site:site + 2], 'big')
        if word >> 8 != 0xd0 + register or (site & ~3) + 4 + (word & 255) * 4 != pool:
            raise ValueError('a declared pointer load changed')
    for site in range(0x21068, 0x21094, 2):
        instruction = sh2.decode(int.from_bytes(data[site:site + 2], 'big'), site)
        if instruction.flow is not None or instruction.writes & {1, 11}:
            raise ValueError('the straight-line entry liveness changed')
    if data[0x21096:0x2109a] != bytes.fromhex('4b0be00c'):
        raise ValueError('the caller JSR or length delay slot changed')
    if (value['simulation']['ram_base'], value['simulation']['ram_size'],
            value['simulation']['boundary'], value['simulation']['frame_bytes_below_sp']) != (
            0x01000000, 65536, 0x2109a, 64):
        raise ValueError('the simulation boundary changed')
    return value


def _member(model, symbol):
    if (model is None or symbol is None or model.symbols.get(symbol.key) is not symbol
            or FUNCTION not in model.symbols):
        raise ValueError('the copy requires full model and symbol context')
    for direction, (meaning, address) in MEMBERS.items():
        if (symbol.key == SymbolKey('7mfk', 'ram', address)
                and symbol.meaning is not None and symbol.meaning.key == meaning
                and symbol.value('width') is None):
            return direction
    raise ValueError('the copy supports another owner, layout, address or width')


def _link(model, symbol, direction):
    function = model.symbols[FUNCTION]
    if function.meaning is None or function.meaning.key != 'coherent_snapshot/fn':
        raise ValueError('the caller meaning changed')
    found = [link for link in model.links if link.owner is symbol.meaning
             and link.to is function.meaning and link.type == direction
             and '7mfk' in (link.props.get('layouts') or ['7mfk'])]
    if len(found) != 1 or found[0].slot is not None or found[0].offset is not None:
        raise ValueError('the copy needs one original relation with unset slot/offset')
    link = found[0]
    if (link.roles or link.props != dict(layouts=['7mfk'], relies='structure', supports='identity')
            or set(link.stated) != {'7mfk'}
            or set(link.sources) != {f'kb/ram/{symbol.meaning.name}.toml'}):
        raise ValueError('the supported relation semantics changed')
    return link


def scope_digest(model):
    """Supported facts; exact registered proof attachments are publication metadata."""
    from kb import convert
    if any(not hasattr(model, name) for name in
           ('layouts', 'spaces', 'functions', 'config', 'overlay', 'names')):
        raise ValueError('a complete model is required')
    for path in model.overlay:
        path = Path(path)
        if path.is_absolute() or '..' in path.parts or (
                (not path.parts or path.parts[0] != 'kb') and path != repo.OWNER_CONFIG):
            raise ValueError('an overlay changes execution inputs')
    value = lambda data: convert._value(model, data)
    meanings = []
    for direction, (_, address) in MEMBERS.items():
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        _member(model, symbol)
        _link(model, symbol, direction)
        meaning = symbol.meaning
        meanings.append(meaning)
    meanings.append(model.symbols[FUNCTION].meaning)
    owners = []
    for meaning in meanings:
        links = []
        for link in model.links:
            if link.owner is not meaning and link.to is not meaning:
                continue
            evidence = semantic_evidence(link)
            links.append((link.owner.key, link.type, link.to.key, link.slot, link.offset,
                          value(link.props), value(evidence), link.roles, link.stated, link.sources))
        owners.append(dict(key=meaning.key, kind=meaning.kind, semantic=meaning.semantic,
            props=value(meaning.props), tables=value(meaning.tables), names=meaning.other_names,
            sources=meaning.sources, tier=meaning.tier, name_sources=meaning.name_sources,
            groups=value(meaning.groups),
            statuses={key: (status.state, value(status.props), value(status.evidence), status.sources)
                      for key, status in meaning.statuses.items()},
            symbols={key: (member.key, member.name, member.generated, member.former,
                           value(member.props), value(member.evidence), member.sources, member.implicit)
                     for key, member in meaning.symbols.items()}, links=links))
    settings = {key: data for key, data in model.config.items()
                if key not in ('names', 'reconciliation', 'source_bindings')}
    return digest(encode(dict(owners=owners, layouts=model.layouts, spaces=model.spaces,
                              functions=model.functions, settings=settings)))


def semantic_evidence(link):
    """Exclude unique, exactly scoped publication attachments from fact hashes."""
    from kb import injection_copy_evidence
    result = []
    for entry in link.evidence:
        can = (link.type in MEMBERS and link.owner.key == MEMBERS[link.type][0]
               and link.to.key == 'coherent_snapshot/fn' and link.slot is None
               and link.offset is None and encode(entry) == encode(item(link.type)))
        if (sum(encode(other) == encode(entry) for other in link.evidence) == 1
                and (can or injection_copy_evidence.publication(link, entry))):
            continue
        result.append(entry)
    return result


def inputs(root):
    from kb import l0
    paths = {*EXECUTION_FILES, 'rom-images/roms.csv', 'rom-images/homology.toml',
             (repo.L0 / '7mfk' / l0.MANIFEST).as_posix()}
    paths.update(image.path.relative_to(root).as_posix() for image in repo.images(root).values()
                 if image.rom == 'JK08A')
    paths.update(path.relative_to(root).as_posix()
                 for path in (root / 'tools/kb/src/kb').rglob('*.py'))
    paths.update(path.relative_to(root).as_posix()
                 for path in (root / repo.L0 / '7mfk').iterdir() if path.is_file())
    return {path: hashlib.sha256(_read(root, path)).hexdigest() for path in sorted(paths)}


def _dependencies(root, *, receipt=None):
    """Local outputs are read dependencies even before they exist."""
    paths = {RECEIPT}
    try:
        record = json.loads(_read(root, RECEIPT) if receipt is None else receipt)
        named = [record['process_path'], *(record['terminal'][name] for name in ('stdout', 'stderr'))]
        if any(type(path) is not str or Path(path).is_absolute() or '..' in Path(path).parts
               for path in named):
            raise ValueError('invalid local proof paths')
        paths.update(named)
    except (OSError, ValueError, TypeError, KeyError):
        pass
    return paths


def dependencies(root, *, receipt=None):
    from kb import sid22_evidence, test_evidence
    return (_dependencies(root, receipt=receipt) | sid22_evidence.dependencies(root)
            | test_evidence.dependencies(root))


def _snapshot(root):
    def read(path):
        try:
            return local_paths.read_path(path, root).read_bytes()
        except (OSError, ValueError):
            return None
    from kb import sid22_evidence, test_evidence
    test_receipt = str(test_evidence.RECEIPT)
    receipts = {path: read(path) for path in (RECEIPT, sid22_evidence.RECEIPT, test_receipt)}
    paths = set(receipts)
    for path, dependency in ((RECEIPT, _dependencies),
                             (sid22_evidence.RECEIPT, sid22_evidence.dependencies),
                             (test_receipt, test_evidence.dependencies)):
        if receipts[path] is not None:
            paths.update(dependency(root, receipt=receipts[path]))
    return {path: receipts[path] if path in receipts else read(path) for path in sorted(paths)}


@contextmanager
def consuming(root):
    """One primitive output snapshot for a verdict or graph publication."""
    previous = _CONSUMED.get()
    if previous is not None and previous[0] == Path(root).resolve():
        yield
        return
    token = _CONSUMED.set((Path(root).resolve(), _snapshot(root)))
    try:
        yield
    finally:
        _CONSUMED.reset(token)


def proof_state(root, *, live=False):
    """Current local proof dependencies, including missing receipt/terminal paths."""
    bound = _CONSUMED.get()
    files = bound[1] if not live and bound is not None and bound[0] == Path(root).resolve() else _snapshot(root)
    from kb import match
    match.READ.update(files)
    hashes = {path: hashlib.sha256(data).hexdigest() if data is not None else None
              for path, data in files.items()}
    return digest(hashes)


def identity_only(symbol):
    return symbol is not None and symbol.meaning is not None and any(
        registered(entry, symbol) for link in symbol.meaning.links if link.owner is symbol.meaning
        for entry in link.evidence)


def model_state(model):
    from itertools import chain
    from kb import injection_copy_evidence, sid22_evidence
    entries = [entry for entries in chain(
            (link.evidence for link in model.links),
            (symbol.evidence for symbol in model.symbols.values())) for entry in entries]
    has_copy = any(_registered(entry) for entry in entries)
    has_sid22 = any(sid22_evidence.registered(entry) for entry in entries)
    has_snapshot = any(injection_copy_evidence.registered(entry) for entry in entries)
    if not has_copy and not has_sid22 and not has_snapshot:
        return None
    try:
        return (proof_state(model.root),
                (scope_digest(model), injection_copy_evidence.scope_digest(model), inputs(model.root))
                if has_copy or has_snapshot else None,
                (sid22_evidence.scope_digest(model), sid22_evidence.inputs(model.root))
                if has_sid22 else None)
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        from kb import convert
        return proof_state(model.root), 'invalid', digest(encode(convert.dump(model)))


def failure(evidence, symbol=None, model=None, claim=None, *, record=None):
    from kb import injection_copy_evidence, sid22_evidence
    if injection_copy_evidence.registered(evidence, symbol):
        if _registered(evidence, symbol) or sid22_evidence.registered(evidence, symbol):
            return 'ambiguous reserved access execution proof'
        return injection_copy_evidence.failure(evidence, symbol, model, claim, record=record)
    if sid22_evidence.registered(evidence, symbol):
        if _registered(evidence, symbol):
            return 'ambiguous reserved access execution proof'
        return sid22_evidence.failure(evidence, symbol, model, claim, record=record)
    if not registered(evidence, symbol):
        return None
    try:
        direction = _member(model, symbol)
        if encode(evidence) != encode(item(direction)):
            return 'the registered copy requires its exact typed evidence scope'
        if claim != 'identity' and (claim is None or claim.name != 'identity'
                or claim.subject not in (symbol.key.key, symbol.meaning.key,
                                        symbol.meaning.key.rsplit('/', 1)[0])):
            return 'the registered copy requires identity-claim context'
        link = _link(model, symbol, direction)
        if evidence not in link.evidence or sum(entry == evidence for entry in link.evidence) != 1:
            return 'the registered copy requires its unique owning link evidence'
        descriptor(model.root)
        if record is None:
            record = json.loads(_read(model.root, RECEIPT))
        candidate = record['candidate']
        if (type(record['schema']) is not int or record['schema'] != SCHEMA
                or type(candidate['schema']) is not int or candidate['schema'] != SCHEMA
                or candidate['key'] != KEY):
            return 'wrong copy execution protocol'
        if candidate['mode'] != 'full' or candidate['complete'] is not True:
            return 'copy execution is a subset or incomplete'
        if (candidate['scope'] != scope_digest(model) or candidate['inputs'] != inputs(model.root)
                or candidate['snapshot_scope'] != injection_copy_evidence.scope_digest(model)):
            return 'copy execution facts or inputs are stale'
        from kb import copy_witness
        copy_witness.validate(candidate, model.root)
        terminal = record['terminal']
        terminal_check(terminal)
        process_bytes = _read(model.root, record['process_path'])
        if hashlib.sha256(process_bytes).hexdigest() != record['process_sha256']:
            return 'copy execution terminal receipt changed'
        original = json.loads(process_bytes)
        for name, value in original.items():
            if name not in ('stdout', 'stderr') and terminal.get(name) != value:
                return 'copy execution terminal disagrees with its original process'
        for stream in ('stdout', 'stderr'):
            data = _read(model.root, terminal[stream])
            if hashlib.sha256(data).hexdigest() != terminal[stream + '_sha256']:
                return 'copy execution streams changed'
        rows = [line[len(MARKER):] for line in _read(model.root, terminal['stdout']).decode().splitlines()
                if line.startswith(MARKER)]
        if rows != [json_text(candidate)]:
            return 'copy execution packet disagrees with terminal output'
        if record['native_model'] != candidate['native_model'] or record['native_inputs'] != digest(candidate['producer_inputs']):
            return 'copy producer provenance lacks independent finalization'
        return None
    except (OSError, ValueError, TypeError, KeyError, AttributeError, ImportError, RecursionError):
        return 'missing or invalid qualified copy execution context'


def terminal_check(process):
    if (type(process['actual_exit_code']) is not int or process['actual_exit_code'] != 0
            or process['timed_out'] is not False
            or process.get('interrupted', False) is not False
            or process['command'] not in (
                ['tools/sh-elf-run/run.sh', '--can-copy-witness'],
                ['tools/sh-elf-run/run.sh', '--can-copy-witness', '--sid22-witness'])):
        raise ValueError('the complete primary CAN witness process did not succeed')
    bound, elapsed = process['declared_limit_seconds'], process['inclusive_process_seconds']
    if (type(bound) is not int or bound <= 0 or type(elapsed) not in (int, float)
            or not math.isfinite(elapsed) or not 0 <= elapsed <= bound + 1):
        raise ValueError('the copy process lacks its actual finite execution bound')
    start, end = (datetime.fromisoformat(process[key]) for key in ('started_utc', 'finished_utc'))
    if start.tzinfo is None or end.tzinfo is None or end < start:
        raise ValueError('the copy process lacks its actual terminal interval')


def accepted(model, symbol, function, claim):
    from kb import injection_copy_evidence, sid22_evidence
    if function.key == sid22_evidence.FUNCTION:
        return sid22_evidence.accepted(model, symbol, function, claim)
    if function.key != FUNCTION:
        return None
    if symbol.key in injection_copy_evidence.MEMBER_KEYS:
        return injection_copy_evidence.accepted(model, symbol, function, claim)
    entries = [entry for entry in claim['evidence'] if registered(entry, symbol)]
    if len(entries) != 1 or failure(entries[0], symbol, model, 'identity') is not None:
        return None
    if entries[0]['value']['direction'] != claim['type']:
        return None
    link = _link(model, symbol, claim['type'])
    if claim != claim_fields(link, symbol.layout):
        return None
    return dict(proof=KEY, callsite='7mfk:00021096', scope='bounded-copy', support='identity')


def claim_fields(link, layout):
    return dict(owner=link.owner.key, to=link.to.key, type=link.type, layout=layout,
                slot=link.slot, offset=link.offset, roles=sorted(link.roles),
                props=link.props, evidence=link.evidence, stated=sorted(link.stated),
                sources=sorted(link.sources))


def retires(before, after, old_claim):
    """Exact semantic CAS for one proof attachment, never absence-based retirement."""
    try:
        from kb import injection_copy_evidence, sid22_evidence
        if old_claim['to'] == sid22_evidence.FUNCTION_MEANING:
            return sid22_evidence.retires(before, after, old_claim)
        if old_claim['owner'] in {row[2] for row in injection_copy_evidence.MEMBERS}:
            return injection_copy_evidence.retires(before, after, old_claim)
        from kb import reconciliation
        if any(registered(entry) for entry in old_claim['evidence']):
            return False
        candidates = [(storage, function, claim) for storage, function, claim
                      in reconciliation.access_claims(after)
                      if reconciliation.claim_identity(claim) == reconciliation.claim_identity(old_claim)]
        if len(candidates) != 1:
            return False
        storage, function, claim = candidates[0]
        proof = item(claim['type'])
        if claim['evidence'] != [*old_claim['evidence'], proof]:
            return False
        if {**claim, 'evidence': old_claim['evidence']} != old_claim:
            return False
        original = before.symbols[storage.key]
        if (original.key, original.value('width')) != (storage.key, storage.value('width')):
            return False
        if scope_digest(before) != scope_digest(after):
            return False
        return accepted(after, storage, function, claim) is not None
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return False


def main(argv=None):
    from kb.copy_witness import main as finalize_main
    finalize_main(argv)


if __name__ == '__main__':
    main()
