"""Controlled protocol checks; these fixtures are not GNU execution evidence."""

from copy import copy, deepcopy
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import compile, copy_evidence as proof, copy_matrix, copy_witness
from kb import checks, graph, levels, match, passes, reconciliation, repo, write
from kb.model import Builder, Issue, SymbolKey


def model_of(root):
    config = repo.config()
    functions = {'7mfk': frozenset({proof.FUNCTION.address})}
    b = Builder(repo.layouts(), compile.spaces(config), functions, {}, config)
    fn = b.symbol(*('7mfk', 'fn', proof.FUNCTION.address), 'kb/fn/coherent_snapshot.toml')
    b.props(fn, {'level': 'code'}, 'kb/fn/coherent_snapshot.toml')
    for direction, (meaning, address) in proof.MEMBERS.items():
        path = f'kb/ram/{meaning.split("/")[0]}.toml'
        symbol = b.symbol('7mfk', 'ram', address, path)
        b.props(symbol, {'level': 'code'}, path)
        b.link(symbol, direction, fn, path, props=dict(layouts=['7mfk'], relies='structure', supports='identity'))
    model = b.finish()
    model.symbols[fn].meaning.name = 'coherent_snapshot'
    for meaning, address in proof.MEMBERS.values():
        model.symbols[SymbolKey('7mfk', 'ram', address)].meaning.name = meaning.split('/')[0]
    model.root, model.config, model.functions = root, config, functions
    model.names, model.spaces, model.overlay = [], compile.spaces(config), {}
    return model


@pytest.fixture
def qualified(tmp_path, monkeypatch):
    from kb import injection_copy_evidence
    # The snapshot domain has separate execution/native mutation contracts.
    # Keep this fixture focused on the existing CAN domain and shared terminal.
    monkeypatch.setattr(injection_copy_evidence, 'scope_digest', lambda model: 'controlled snapshot scope')
    def snapshot(witness, inputs, root):
        if witness != {'controlled_snapshot_boundary': True}:
            raise ValueError('wrong controlled snapshot boundary')
    monkeypatch.setattr(injection_copy_evidence, 'validate_witness', snapshot)
    descriptor = proof.descriptor(repo.ROOT)
    image = repo.images()['JK08A']
    data = image.path.read_bytes()
    model = model_of(tmp_path)
    configuration = tmp_path / repo.CONFIG
    configuration.parent.mkdir(parents=True, exist_ok=True)
    configuration.write_bytes((repo.ROOT / repo.CONFIG).read_bytes())
    reader = model.symbols[SymbolKey('7mfk', 'ram', 0xffff419b)]
    for link in model.links:
        link.evidence.append(proof.item(link.type))
    (tmp_path / 'fixture.bin').write_bytes(data)
    for path in copy_witness.CONSUMED:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(('controlled ' + path).encode())
    source = tmp_path / 'current.txt'
    source.write_bytes(b'current')
    monkeypatch.setattr(proof, 'descriptor', lambda root: deepcopy(descriptor))
    monkeypatch.setattr(repo, 'images', lambda root=repo.ROOT: {
        'JK08A': repo.Image('JK08A', Path(root) / 'fixture.bin', image.sha256)})
    def inputs(root):
        paths = [*copy_witness.CONSUMED, 'fixture.bin', 'current.txt']
        return {path: hashlib.sha256(proof._read(root, path)).hexdigest() for path in paths}
    monkeypatch.setattr(proof, 'inputs', inputs)
    cases = copy_matrix.cases(descriptor)
    observations = []
    for case in cases:
        frame = bytearray(64)
        for offset, value in ((52, case['incoming'][4]), (56, case['incoming'][3]),
                              (60, copy_matrix.alias(case['source']))):
            frame[offset:offset + 4] = value.to_bytes(4, 'big')
        observations.append(dict(index=case['index'], gpr=copy_matrix.expected_registers(case),
            source_before=copy_matrix.source_bytes(case).hex(), source_after=copy_matrix.source_bytes(case).hex(),
            destination_after=copy_matrix.source_bytes(case).hex(), sr_before=case['sr'],
            sr_after=case['sr'] & ~1 | int(case['length'] == 0),
            gbr=case['gbr'], mach=case['mach'], macl=case['macl'],
            sp_before=0x02001000, sp_after=0x02001000,
            pr=0x2109a if case['caller'] else 0x201234, return_pc=0x201234,
            frame_before=bytes(64).hex(), frame_after=frame.hex(),
            ram_checked_bytes=65536, unchanged_outside_destination=True,
            abi_preserved=True, input_preserved=True))
    candidate = dict(schema=proof.SCHEMA, key=proof.KEY, mode='full', complete=True,
        snapshot_scope='controlled snapshot scope',
        scope=proof.scope_digest(model), inputs=inputs(tmp_path), native_model='a' * 64,
        producer_inputs={'controlled': 'b' * 64}, witness=dict(region=proof.REGION,
        cases=cases, observations=observations,
        consumed={path: (tmp_path / path).read_bytes().hex() for path in copy_witness.CONSUMED},
        image_sha256=image.sha256,
        code=[dict(start=a, end=b, stock=data[a:b].hex(), reconstructed=data[a:b].hex())
              for a, b in ((0x21094, 0x2109a), (0x22558, 0x22590))],
        pools=[dict(address=row['address'], stock=row['value'].to_bytes(4, 'big').hex(),
                    reconstructed=row['value'].to_bytes(4, 'big').hex()) for row in descriptor['pool']],
        boundary=dict(address=0x2109a, bytes=copy_matrix.boundary_bytes().hex()),
        aliases=[[0x2125c, 0xffff4194, 0x01004194]],
        entry=dict(r1=0x01004188, r11=0x22558, caller=0x21094,
                   callsite=0x21096, delay_slot=0x21098, length=12),
        elf_sha256='c' * 64, fixture_sha256='d' * 64,
        toolchain=dict(simulator_version='16.3', gcc_version='13.3.0',
                       binaries={key: 'e' * 64 for key in ('as', 'ld', 'objcopy', 'gcc', 'run')})))
    fixture = bytearray(data)
    fixture[0x2125c:0x21260] = (0x01004194).to_bytes(4, 'big')
    fixture[0x2109a:0x2109a + len(copy_matrix.boundary_bytes())] = copy_matrix.boundary_bytes()
    candidate['witness']['fixture_sha256'] = hashlib.sha256(fixture).hexdigest()
    terminal = dict(actual_exit_code=0, timed_out=False,
                    command=['tools/sh-elf-run/run.sh', '--can-copy-witness'],
                    inclusive_process_seconds=0.1, declared_limit_seconds=300,
                    started_utc='2026-10-15T10:00:00+00:00', finished_utc='2026-10-15T10:00:00.1+00:00')
    candidate['witness']['snapshot'] = dict(controlled_snapshot_boundary=True)
    record = dict(schema=proof.SCHEMA, candidate=candidate, terminal=terminal,
                  native_model=candidate['native_model'], native_inputs=proof.digest(candidate['producer_inputs']))
    def save(value=None):
        held = deepcopy(record if value is None else value)
        stdout = (proof.MARKER + proof.json_text(held['candidate']) + '\n').encode()
        for stream, data in (('stdout', stdout), ('stderr', b'')):
            path = stream + '.txt'
            (tmp_path / path).write_bytes(data)
            held['terminal'][stream] = path
            held['terminal'][stream + '_sha256'] = hashlib.sha256(data).hexdigest()
        original = {key: value for key, value in held['terminal'].items() if key not in ('stdout', 'stderr')}
        process = json.dumps(original).encode()
        (tmp_path / 'process.json').write_bytes(process)
        held['process_path'], held['process_sha256'] = 'process.json', hashlib.sha256(process).hexdigest()
        target = tmp_path / proof.RECEIPT
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(held))
        return held
    save()
    return SimpleNamespace(model=model, symbol=reader, record=record, save=save,
                           root=tmp_path, source=source, candidate=candidate)


def award(state, route):
    item = proof.item('reader')
    if route == 'verify':
        return match.verify(state.model, state.symbol, item) is None
    if route == 'rank':
        return match.rank(item, state.symbol, state.model, 'identity') == match.vocab.LEVEL_RANK['code']
    if route == 'anchor':
        return match._anchor(state.model, state.symbol, []) == match.vocab.LEVEL_RANK['code']
    link = proof._link(state.model, state.symbol, 'reader')
    return proof.accepted(state.model, state.symbol, state.model.symbols[proof.FUNCTION],
                          proof.claim_fields(link, '7mfk')) is not None


@pytest.mark.parametrize('route', ['verify', 'rank', 'anchor', 'access'])
@pytest.mark.parametrize('fault', ['none', 'missing', 'source', 'receipt', 'terminal', 'stream',
    'subset', 'incomplete', 'omitted-case', 'wrong-case', 'no-copy', 'register', 'frame', 'layout', 'width',
    'missing-snapshot', 'snapshot', 'snapshot-scope', 'old-schema'])
def test_current_packet_and_refusals(qualified, route, fault):
    assert award(qualified, route)
    record = deepcopy(qualified.record)
    if fault == 'missing':
        (qualified.root / proof.RECEIPT).unlink()
    elif fault == 'source':
        qualified.source.write_bytes(b'changed')
    elif fault == 'receipt':
        (qualified.root / proof.RECEIPT).write_bytes(b'{}')
    elif fault == 'terminal':
        (qualified.root / 'process.json').write_bytes(b'{}')
    elif fault == 'stream':
        (qualified.root / 'stderr.txt').write_bytes(b'changed')
    elif fault == 'width':
        qualified.symbol.props['width'] = 8
    elif fault == 'layout':
        record['candidate']['witness']['entry']['callsite'] = 0x21314
        qualified.save(record)
    elif fault != 'none':
        candidate = record['candidate']
        if fault == 'subset': candidate['mode'] = 'early'
        if fault == 'incomplete': candidate['complete'] = False
        if fault == 'omitted-case': candidate['witness']['observations'].pop()
        if fault == 'wrong-case': candidate['witness']['cases'][0]['source'] += 1
        if fault == 'no-copy': candidate['witness']['observations'][0]['destination_after'] = '00' * 12
        if fault == 'register': candidate['witness']['observations'][0]['gpr'][7] ^= 1
        if fault == 'frame': candidate['witness']['observations'][0]['frame_after'] = 'ff' * 64
        if fault == 'missing-snapshot': candidate['witness'].pop('snapshot')
        if fault == 'snapshot': candidate['witness']['snapshot'] = {}
        if fault == 'snapshot-scope': candidate['snapshot_scope'] = 'another scope'
        if fault == 'old-schema': candidate['schema'] = 1
        qualified.save(record)
    assert award(qualified, route) is (fault == 'none')


@pytest.mark.parametrize('field,value', [('kind', 'spec'), ('mode', 'base'), ('key', 'unknown'),
    ('path', 'defs/other.toml'), ('at', '7mfk:00021314'), ('supports', 'scale'),
    ('to', SymbolKey('7mfk', 'fn', 0x22558))])
def test_namespace_mutation_never_uses_generic_award(qualified, field, value):
    item = {**proof.item('reader'), field: value}
    assert match.verify(qualified.model, qualified.symbol, item) is not None
    assert match.rank(item, qualified.symbol, qualified.model, 'identity') == -1
    assert match.verify_status(qualified.model, '7mfk', item) is not None


@pytest.mark.parametrize('name,value', [('slot', 'x'), ('offset', 7), ('roles', ['new']),
                                      ('layout', '1nd'), ('type', 'writer')])
def test_access_checks_the_supplied_full_context(qualified, name, value):
    link = proof._link(qualified.model, qualified.symbol, 'reader')
    claim = deepcopy(proof.claim_fields(link, '7mfk'))
    claim[name] = value
    assert proof.accepted(qualified.model, qualified.symbol,
                          qualified.model.symbols[proof.FUNCTION], claim) is None


def test_missing_identity_context_status_and_indirect_held_refuse(qualified, monkeypatch):
    item = proof.item('reader')
    assert match.rank(item, qualified.symbol, qualified.model) == -1
    assert match.rank(item, qualified.symbol, qualified.model, 'scale') == -1
    assert match.verify_status(qualified.model, '7mfk', item) is not None
    symbol = qualified.symbol
    symbol.evidence.append({**item, 'key': 'unknown', 'path': 'defs/unknown.toml'})
    monkeypatch.setattr(levels.sites, 'referenced', lambda *args: set())
    assert not levels.held(qualified.model, symbol)


def test_consumed_snapshot_refuses_invalid_valid_invalid_ABA(qualified):
    valid = (qualified.root / proof.RECEIPT).read_bytes()
    target = qualified.root / proof.RECEIPT
    target.write_bytes(b'{}')
    state = proof.proof_state(qualified.root)
    with proof.consuming(qualified.root):
        target.write_bytes(valid)
        assert not award(qualified, 'access')
        target.write_bytes(b'{}')
        assert proof.proof_state(qualified.root, live=True) == state
    target.write_bytes(valid)
    assert award(qualified, 'access')


def test_receipt_and_terminal_hashes_ignore_restored_size_and_mtime(qualified, monkeypatch):
    monkeypatch.setattr(passes.Passes, 'inputs', lambda self, name: set())
    record = passes.Passes(qualified.root)
    names = proof.dependencies(qualified.root)
    first = record.digest('code', names)
    path = qualified.root / 'stderr.txt'
    old = path.stat()
    path.write_bytes(b'x')
    os.utime(path, ns=(old.st_atime_ns, old.st_mtime_ns))
    assert record.digest('code', names) != first
    assert graph.proof_stale({'copy_proof_state': 'old'}, qualified.root)


def test_direct_levels_uses_the_same_qualified_identity(qualified, monkeypatch):
    claim = levels.Claim('controlled', qualified.symbol.key.key, 'identity', 'code',
        items=[(qualified.symbol, proof.item('reader'))], symbol=qualified.symbol)
    monkeypatch.setattr(levels._Collector, 'collect', lambda self: [claim])
    monkeypatch.setattr(levels, 'hardware', lambda root: {})
    monkeypatch.setattr(levels, '_all_items', lambda model: ())
    assert levels.analyze(qualified.model).grounded[id(claim)] == levels.CODE
    (qualified.root / proof.RECEIPT).unlink()
    assert levels.analyze(qualified.model).grounded[id(claim)] < levels.CODE


@pytest.mark.parametrize('fault', ['none', 'roles', 'props', 'stated', 'sources', 'slot', 'offset',
    'width', 'evidence', 'duplicate', 'related-fact', 'stale-review', 'stale-l0'])
def test_review_retirement_requires_full_proof_attachment_CAS(qualified, monkeypatch, fault):
    import tomlkit
    before = deepcopy(qualified.model)
    after = qualified.model
    for link in before.links:
        link.evidence.clear()
    monkeypatch.setattr(reconciliation, 'accesses', lambda *args: ({}, {}))
    monkeypatch.setattr(match, 'l0_digest', lambda *args: '0123456789abcdef')
    records = reconciliation.reviews(before)
    assert len(records) == 2
    before.config['reconciliation'] = {'enabled': True, 'review': deepcopy(records)}
    after.config['reconciliation'] = deepcopy(before.config['reconciliation'])
    link = proof._link(after, qualified.symbol, 'reader')
    if fault == 'roles': link.roles.add('new')
    if fault == 'props': link.props['note'] = 'changed'
    if fault == 'stated': link.stated.add('1nd')
    if fault == 'sources': link.sources.add('kb/ram/other.toml')
    if fault == 'slot': link.slot = 'x'
    if fault == 'offset': link.offset = 7
    if fault == 'width': qualified.symbol.props['width'] = 8
    if fault == 'evidence': link.evidence[0] = {**link.evidence[0], 'note': 'extra'}
    if fault == 'duplicate': after.links.append(copy(link))
    if fault == 'related-fact': after.symbols[proof.FUNCTION].meaning.props['note'] = 'changed'
    if fault == 'stale-review': before.config['reconciliation']['review'][0]['claim_sha256'] = 'a' * 64
    if fault == 'stale-l0': before.config['reconciliation']['review'][0]['l0'] = 'fedcba9876543210'
    path = qualified.root / repo.OWNER_CONFIG
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(tomlkit.dumps({'reconciliation': before.config['reconciliation']}))
    result = reconciliation.rebase(before, after, {}, proof_attachments=True)
    if fault == 'none':
        assert result is not None
        assert tomlkit.parse(result)['reconciliation']['review'] == []
    elif fault in ('stale-review', 'stale-l0'):
        assert result is not None
        assert len(tomlkit.parse(result)['reconciliation']['review']) == 1
    else:
        # A changed supported member invalidates the scope for both attachments.
        assert result is None


def test_held_model_rechecks_changed_receipt_stream_and_facts(qualified, monkeypatch):
    calls = []
    def check(model):
        calls.append(True)
        return [] if award(qualified, 'verify') else [Issue('code', 'controlled', 'copy', 'unqualified')]
    monkeypatch.setattr(checks, 'CHECKS', {'code': check})
    monkeypatch.setattr(checks, 'audit', lambda *args: {})
    assert write._issues(qualified.model) == {}
    assert write._issues(qualified.model) == {}
    assert len(calls) == 1
    (qualified.root / 'stderr.txt').write_bytes(b'changed')
    assert write._issues(qualified.model)
    qualified.save()
    assert write._issues(qualified.model) == {}
    qualified.symbol.props['width'] = 8
    assert write._issues(qualified.model)
    assert len(calls) == 4


def test_third_member_unknown_key_and_definition_cannot_borrow_CAN_rank(qualified):
    from copy import copy
    other = copy(qualified.symbol)
    other.key = SymbolKey('7mfk', 'ram', 0xffff419c)
    qualified.model.symbols[other.key] = other
    entry = {**proof.item('reader'), 'key': 'unknown', 'path': 'defs/unknown.toml'}
    assert match.rank(entry, other, qualified.model, 'identity') == -1
    assert match.verify(qualified.model, other, entry) is not None
    assert proof.failure(proof.item('reader'), qualified.symbol, qualified.model, 'scale') is not None


def test_unrelated_fact_preserves_supported_scope(qualified):
    from copy import copy
    unrelated = copy(qualified.symbol.meaning)
    unrelated.name, unrelated.props = 'unrelated', {'note': 'other knowledge'}
    qualified.model.meanings.append(unrelated)
    assert award(qualified, 'access')


def test_legacy_base_remains_outside_the_registered_copy_protocol(qualified):
    entry = dict(kind='indirect', mode='base', at='7mfk:00021094',
                 key='legacy_base', path='defs/other.toml')
    assert not proof.registered(entry, qualified.symbol)


def test_pass_cache_never_records_valid_middle_state_for_invalid_ABA(qualified, monkeypatch):
    monkeypatch.setattr(passes.Passes, 'inputs', lambda self, name: set())
    target = qualified.root / proof.RECEIPT
    valid = target.read_bytes()
    target.write_bytes(b'{}')
    held = passes.Passes(qualified.root)
    def check(root):
        target.write_bytes(valid)
        try:
            return [] if award(qualified, 'verify') else [Issue('code', 'controlled', 'copy', 'unqualified')]
        finally:
            target.write_bytes(b'{}')
    assert held.run('code', check)
    assert 'code' not in held.passed
    held.save()
    assert 'code' not in json.loads((qualified.root / passes.RECORD).read_text())


def test_primary_reader_rolls_back_when_receipt_changes_during_read(tmp_path, monkeypatch):
    from contextlib import contextmanager
    from kb import reader
    from tools.kb.tests.test_reader import Transaction, context
    transaction = Transaction()
    original = {'copy_proof_state': proof.proof_state(tmp_path)}
    source = SimpleNamespace(driver=SimpleNamespace(session=lambda **kwargs:
        context(SimpleNamespace(begin_transaction=lambda: transaction))), run=lambda query: [])
    monkeypatch.setattr(reader.lock, 'held', lambda root: context(None))
    monkeypatch.setattr(reader.graph, 'fresh', lambda *args, **kwargs: context(source))
    monkeypatch.setattr(reader.graph, 'meta', lambda source: original)
    monkeypatch.setattr(reader.graph, 'stale', lambda *args: False)
    monkeypatch.setattr(reader.fingerprint, 'compute', lambda root: None)
    with pytest.raises(repo.KbError, match='copy execution proof changes during'):
        with reader.session(tmp_path):
            target = tmp_path / proof.RECEIPT
            target.parent.mkdir(parents=True)
            target.write_bytes(b'{}')
    assert transaction.rolled_back == 1


@pytest.mark.parametrize('fault', ['none', 'exit', 'timeout', 'interrupted', 'early', 'bound', 'unfinished',
                                  'full-marker', 'duplicate-packet', 'native', 'scope', 'stream-race'])
@pytest.mark.parametrize('storage', ['native', 'external'])
def test_independent_finalizer_refuses_and_preserves_the_previous_record(qualified, monkeypatch, fault, storage):
    candidate = deepcopy(qualified.candidate)
    current = {key: value for key, value in deepcopy(candidate).items() if key != 'witness'}
    current['complete'] = False
    monkeypatch.setattr(copy_witness, 'begin', lambda root: deepcopy(current))
    if fault == 'unfinished': candidate['complete'] = False
    if fault == 'native': candidate['native_model'] = 'f' * 64
    if fault == 'scope': candidate['scope'] = 'f' * 64
    prefix = '' if fault == 'full-marker' else 'VQ_SH_ELF_VERIFY status=PASS controlled=true\n'
    output = prefix + proof.MARKER + proof.json_text(candidate) + '\n'
    if fault == 'duplicate-packet': output += proof.MARKER + proof.json_text(candidate) + '\n'
    terminal = deepcopy(qualified.record['terminal'])
    if fault == 'exit': terminal['actual_exit_code'] = 1
    if fault == 'timeout': terminal['timed_out'] = True
    if fault == 'interrupted': terminal['interrupted'] = True
    if fault == 'early': terminal['command'] = ['tools/sh-elf-run/run.sh', '--can-copy-early']
    if fault == 'bound': terminal.pop('declared_limit_seconds')
    directory = qualified.root
    if storage == 'external':
        directory = qualified.root.parent / (qualified.root.name + '-data')
        directory.mkdir()
        (qualified.root / 'tmp').mkdir()
        (qualified.root / 'tmp/local-results').symlink_to(directory, target_is_directory=True)
    stdout, stderr = directory / 'later.stdout', directory / 'later.stderr'
    stdout.write_text(output); stderr.write_bytes(b'')
    for stream, path in (('stdout', stdout), ('stderr', stderr)):
        terminal[stream + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    process = directory / 'later-process.json'
    process.write_text(json.dumps(terminal))
    previous = (qualified.root / proof.RECEIPT).read_bytes()
    if fault == 'stream-race':
        original_read = Path.read_bytes
        changed = False
        substitute = {**candidate, 'controlled_nonce': 'substitution between hash and parse'}
        replacement = prefix + proof.MARKER + proof.json_text(substitute) + '\n'
        def read(path):
            nonlocal changed
            data = original_read(path)
            if path.resolve() == stdout.resolve() and not changed:
                changed = True
                stdout.write_text(replacement)
            return data
        monkeypatch.setattr(Path, 'read_bytes', read)
    if fault == 'none':
        from kb import lock
        with lock.held(qualified.root, timeout=1):
            prepared = copy_witness.prepare(process, stdout, stderr, qualified.root)
        assert prepared['candidate'] == candidate
        if storage == 'external':
            assert prepared['process_path'] == 'tmp/local-results/later-process.json'
            assert prepared['terminal']['stdout'] == 'tmp/local-results/later.stdout'
            assert prepared['terminal']['stderr'] == 'tmp/local-results/later.stderr'
        assert (qualified.root / proof.RECEIPT).read_bytes() == previous
        copy_witness.finalize(process, stdout, stderr, qualified.root)
        assert award(qualified, 'access')
    else:
        with pytest.raises((ValueError, KeyError)):
            copy_witness.finalize(process, stdout, stderr, qualified.root)
        assert (qualified.root / proof.RECEIPT).read_bytes() == previous
        assert award(qualified, 'access')
