"""Controlled protocol fixtures, not GNU execution or hardware evidence."""

from copy import deepcopy
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import copy_evidence as access, graph, levels, match, passes, reconciliation, repo, write
from kb import sid22_evidence as proof, sid22_matrix as matrix, sid22_witness as producer
from kb.model import Issue, SymbolKey
from kb.test_evidence import digest, json_text
from tools.kb.tests.test_sid22_evidence import model_of, controlled_observation


@pytest.fixture
def qualified(tmp_path, monkeypatch):
    contract = proof.descriptor()
    stock = repo.images()['JK08A'].path.read_bytes()
    model = model_of(contract)
    model.root = tmp_path
    configuration = tmp_path / repo.CONFIG
    configuration.parent.mkdir(parents=True, exist_ok=True)
    configuration.write_bytes((repo.ROOT / repo.CONFIG).read_bytes())
    (tmp_path / 'fixture.bin').write_bytes(stock)
    for path in producer.CONSUMED:
        target = tmp_path / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((repo.ROOT / path).read_bytes())
    current = tmp_path / 'current.txt'
    current.write_bytes(b'current')
    monkeypatch.setattr(proof, 'descriptor', lambda root=repo.ROOT: contract)
    monkeypatch.setattr(repo, 'images', lambda root=repo.ROOT: {
        'JK08A': repo.Image('JK08A', Path(root) / 'fixture.bin', proof.IMAGE_SHA256)})
    def inputs(root):
        return {path: hashlib.sha256(proof._read(root, path)).hexdigest()
                for path in (*producer.CONSUMED, 'fixture.bin', 'current.txt')}
    monkeypatch.setattr(proof, 'inputs', inputs)
    cases = matrix.cases(contract, stock)
    fixture, aliases = matrix.fixture(stock, contract)
    witness = dict(region=proof.REGION, cases=cases,
        observations=[controlled_observation(case) for case in cases],
        consumed={path: (tmp_path / path).read_bytes().hex() for path in producer.CONSUMED},
        code=[dict(start=start, end=end, stock=stock[start:end].hex(), reconstructed=stock[start:end].hex())
              for start, end in contract.body],
        pools=[dict(address=address, stock=stock[address:address + size].hex(),
                    reconstructed=stock[address:address + size].hex())
               for address, size in (*contract.pools, *((start, end - start) for _, start, end, _ in proof.TABLES))],
        aliases=aliases, image_sha256=proof.IMAGE_SHA256, fixture_sha256=hashlib.sha256(fixture).hexdigest(),
        elf_sha256='c' * 64, toolchain=dict(simulator_version='16.3', gcc_version='13.3.0',
            binaries={name: 'd' * 64 for name in ('as', 'ld', 'objcopy', 'gcc', 'run')}))
    candidate = dict(schema=1, key=proof.KEY, mode='full', complete=True, production=True,
        scope=proof.scope_digest(model), inputs=inputs(tmp_path), native_model='a' * 64,
        producer_inputs={'controlled': 'b' * 64}, witness=witness)
    terminal = dict(actual_exit_code=0, timed_out=False,
        command=['tools/sh-elf-run/run.sh', '--can-copy-witness', '--sid22-witness'],
        inclusive_process_seconds=0.1, declared_limit_seconds=300,
        started_utc='2026-10-15T10:00:00+00:00', finished_utc='2026-10-15T10:00:00.1+00:00')
    record = dict(schema=1, candidate=candidate, terminal=terminal,
                  native_model=candidate['native_model'], native_inputs=digest(candidate['producer_inputs']))
    def save(value=None):
        held = deepcopy(record if value is None else value)
        stdout = ('VQ_SH_ELF_VERIFY status=PASS controlled=true\n' + proof.MARKER + json_text(held['candidate']) + '\n').encode()
        for name, data in (('stdout', stdout), ('stderr', b'')):
            path = name + '.txt'
            (tmp_path / path).write_bytes(data)
            held['terminal'][name] = path
            held['terminal'][name + '_sha256'] = hashlib.sha256(data).hexdigest()
        process = json.dumps({key: value for key, value in held['terminal'].items()
                              if key not in ('stdout', 'stderr')}).encode()
        (tmp_path / 'process.json').write_bytes(process)
        held['process_path'], held['process_sha256'] = 'process.json', hashlib.sha256(process).hexdigest()
        target = tmp_path / proof.RECEIPT
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(held))
        return held
    save()
    symbol = model.symbols[SymbolKey('7mfk', 'ram', contract.members[0].address)]
    return SimpleNamespace(root=tmp_path, model=model, symbol=symbol, candidate=candidate,
                           record=record, save=save, current=current, contract=contract)


def award(state, route):
    evidence = proof.item(state.symbol.meaning.key)
    if route == 'verify':
        return match.verify(state.model, state.symbol, evidence) is None
    if route == 'rank':
        return match.rank(evidence, state.symbol, state.model, 'identity') == levels.CODE
    if route == 'anchor':
        return match._anchor(state.model, state.symbol, []) == levels.CODE
    member = state.contract.member(state.symbol.meaning.key)
    link = proof._link(state.model, state.symbol, member, state.contract, attached=True)
    return access.accepted(state.model, state.symbol, state.model.symbols[proof.FUNCTION],
                           access.claim_fields(link, '7mfk')) is not None


@pytest.mark.parametrize('route', ['verify', 'rank', 'anchor', 'access'])
def test_shared_consumers_recheck_current_receipt_and_inputs(qualified, route):
    assert award(qualified, route)
    qualified.current.write_bytes(b'changed')
    assert not award(qualified, route)
    qualified.current.write_bytes(b'current')
    assert award(qualified, route)
    (qualified.root / 'stderr.txt').write_bytes(b'changed')
    assert not award(qualified, route)


@pytest.mark.parametrize('fault', ['missing', 'record', 'process', 'early', 'incomplete',
    'non-production', 'production-missing', 'production-type',
    'omit', 'reorder', 'observation', 'body', 'pool', 'aliases', 'fixture', 'source',
    'consumed', 'tools', 'native', 'scope', 'unknown-item', 'status', 'scale'])
def test_qualified_protocol_refuses_corruption(qualified, fault):
    evidence = proof.item(qualified.symbol.meaning.key)
    record = deepcopy(qualified.record)
    candidate, witness = record['candidate'], record['candidate']['witness']
    if fault == 'missing': (qualified.root / proof.RECEIPT).unlink()
    elif fault == 'record': (qualified.root / proof.RECEIPT).write_bytes(b'{}')
    elif fault == 'process': (qualified.root / 'process.json').write_bytes(b'{}')
    elif fault == 'unknown-item': evidence['key'] = 'sid22-unknown'
    elif fault == 'status':
        assert match.verify_status(qualified.model, '7mfk', evidence) is not None
        return
    elif fault == 'scale':
        assert match.rank(evidence, qualified.symbol, qualified.model, 'scale') == -1
        return
    else:
        if fault == 'early': candidate['mode'] = 'early'
        elif fault == 'incomplete': candidate['complete'] = False
        elif fault == 'non-production': candidate['production'] = False
        elif fault == 'production-missing': candidate.pop('production')
        elif fault == 'production-type': candidate['production'] = 1
        elif fault == 'omit': witness['cases'].pop()
        elif fault == 'reorder': witness['cases'][:2] = witness['cases'][1::-1]
        elif fault == 'observation': witness['observations'][0]['sources_after'][0] ^= 1
        elif fault == 'body': witness['code'].pop()
        elif fault == 'pool': witness['pools'].pop()
        elif fault == 'aliases': witness['aliases'].pop()
        elif fault == 'fixture': witness['fixture_sha256'] = 'f' * 64
        elif fault == 'source': witness['consumed'].pop(producer.CONSUMED[1])
        elif fault == 'consumed': witness['consumed'][producer.CONSUMED[1]] = '00'
        elif fault == 'tools': witness['toolchain']['binaries'].pop('run')
        elif fault == 'native': record['native_model'] = 'f' * 64
        elif fault == 'scope': candidate['scope'] = 'f' * 64
        qualified.save(record)
    assert access.failure(evidence, qualified.symbol, qualified.model, 'identity') is not None


def test_all_fifty_readers_are_scoped_without_width_or_source_offset_changes(qualified):
    for member in qualified.contract.members:
        qualified.symbol = qualified.model.symbols[SymbolKey('7mfk', 'ram', member.address)]
        assert award(qualified, 'access')
        assert qualified.symbol.value('width') == member.declared_width
    links = graph.claim_rows(qualified.model)['symbol_links']
    readers = [row for row in links['READER'] if row['props'].get('pointer_proof')]
    assert len(readers) == 50
    assert all(row['props']['verified'] and row['props']['verification_scope'] == 'did-pointer-read'
               and row['props']['pointer_publisher'] == '7mfk:0003235c'
               and not row['props'].get('copy_proof') for row in readers)


def test_shared_snapshot_dependencies_include_absence_and_invalid_ABA(qualified):
    target = qualified.root / proof.RECEIPT
    valid = target.read_bytes()
    assert {proof.RECEIPT, access.RECEIPT, 'process.json', 'stdout.txt', 'stderr.txt'} <= access.dependencies(qualified.root)
    target.write_bytes(b'{}')
    before = access.proof_state(qualified.root)
    with access.consuming(qualified.root):
        target.write_bytes(valid)
        assert not award(qualified, 'verify')
        target.write_bytes(b'{}')
        assert access.proof_state(qualified.root, live=True) == before
    target.write_bytes(valid)
    assert award(qualified, 'verify')
    assert graph.proof_stale({'copy_proof_state': before}, qualified.root)


def test_held_model_cache_rechecks_SID22_outputs_and_owned_facts(qualified, monkeypatch):
    calls = []
    def check(model):
        calls.append(True)
        return [] if award(qualified, 'verify') else [Issue('code', 'controlled', 'SID22', 'unqualified')]
    monkeypatch.setattr(write.checks, 'CHECKS', {'code': check})
    monkeypatch.setattr(write.checks, 'audit', lambda *args: {})
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


def test_direct_levels_share_the_qualified_identity_scope(qualified, monkeypatch):
    claim = levels.Claim('controlled', qualified.symbol.key.key, 'identity', 'code',
        items=[(qualified.symbol, proof.item(qualified.symbol.meaning.key))], symbol=qualified.symbol)
    monkeypatch.setattr(levels._Collector, 'collect', lambda self: [claim])
    monkeypatch.setattr(levels, 'hardware', lambda root: {})
    monkeypatch.setattr(levels, '_all_items', lambda model: ())
    assert levels.analyze(qualified.model).grounded[id(claim)] == levels.CODE
    (qualified.root / proof.RECEIPT).unlink()
    assert levels.analyze(qualified.model).grounded[id(claim)] < levels.CODE


@pytest.mark.parametrize('fault', ['none', 'width', 'role', 'slot', 'offset', 'DID-source',
                                  'publisher', 'missing-proof', 'stale-review', 'stale-l0'])
def test_review_rebase_removes_only_exact_qualified_reader_attachments(qualified, monkeypatch, fault):
    import tomlkit
    before, after = deepcopy(qualified.model), qualified.model
    for link in before.links:
        if link.type == 'reader': link.evidence.clear()
    monkeypatch.setattr(reconciliation, 'accesses', lambda *args: ({}, {}))
    monkeypatch.setattr(match, 'l0_digest', lambda *args: '0123456789abcdef')
    reviews = reconciliation.reviews(before)
    assert len(reviews) == 50
    width_debt = dict(kind='width', subject='controlled-independent-width', claim_sha256='f' * 64,
                      state='unresolved', reason='independent width review')
    before.config['reconciliation'] = dict(enabled=True, review=[*deepcopy(reviews), width_debt])
    after.config['reconciliation'] = deepcopy(before.config['reconciliation'])
    member = qualified.contract.member(qualified.symbol.meaning.key)
    link = proof._link(after, qualified.symbol, member, qualified.contract, attached=True)
    if fault == 'width': qualified.symbol.props['width'] = 8
    elif fault == 'role': link.roles.add('indexed_by')
    elif fault == 'slot': link.slot = 'changed'
    elif fault == 'offset': link.offset = 1
    elif fault == 'DID-source':
        next(row for row in after.links if row.type == 'source').offset = 1
    elif fault == 'publisher': after.symbols[proof.FUNCTION].meaning.props['note'] = 'changed'
    elif fault == 'missing-proof': link.evidence.clear()
    elif fault == 'stale-review': before.config['reconciliation']['review'][0]['claim_sha256'] = 'e' * 64
    elif fault == 'stale-l0': before.config['reconciliation']['review'][0]['l0'] = 'fedcba9876543210'
    path = qualified.root / repo.OWNER_CONFIG
    path.write_text(tomlkit.dumps({'reconciliation': before.config['reconciliation']}))
    result = reconciliation.rebase(before, after, {}, proof_attachments=True)
    if fault in ('width', 'role', 'slot', 'offset', 'DID-source', 'publisher'):
        assert result is None
    else:
        assert result is not None
        remaining = tomlkit.parse(result)['reconciliation']['review']
        assert dict(remaining[-1]) == width_debt
        assert len(remaining) == (1 if fault == 'none' else 2)


def test_pass_cache_preserves_invalid_SID22_snapshot_under_ABA(qualified, monkeypatch):
    monkeypatch.setattr(passes.Passes, 'inputs', lambda self, name: set())
    target = qualified.root / proof.RECEIPT
    valid = target.read_bytes()
    target.write_bytes(b'{}')
    held = passes.Passes(qualified.root)
    def check(root):
        target.write_bytes(valid)
        try:
            return [] if award(qualified, 'verify') else [Issue('code', 'controlled', 'SID22', 'unqualified')]
        finally:
            target.write_bytes(b'{}')
    assert held.run('code', check)
    assert 'code' not in held.passed
    held.save()
    assert 'code' not in json.loads((qualified.root / passes.RECORD).read_text())


@pytest.mark.parametrize('fault', ['none', 'timeout', 'interrupted', 'exit', 'early', 'missing-marker',
    'duplicate', 'provenance', 'scope', 'source-race', 'stream-race', 'non-production'])
@pytest.mark.parametrize('storage', ['native', 'external'])
def test_independent_finalizer_preserves_previous_record_on_refusal(qualified, monkeypatch, fault, storage):
    current = {key: deepcopy(value) for key, value in qualified.candidate.items() if key != 'witness'}
    current['complete'] = False
    monkeypatch.setattr(producer, 'begin', lambda root: deepcopy(current))
    candidate = deepcopy(qualified.candidate)
    if fault == 'provenance': candidate['native_model'] = 'f' * 64
    if fault == 'scope': candidate['scope'] = 'f' * 64
    if fault == 'non-production': candidate['production'] = False
    text = proof.MARKER + json_text(candidate) + '\n'
    if fault != 'missing-marker': text = 'VQ_SH_ELF_VERIFY status=PASS controlled=true\n' + text
    if fault == 'duplicate': text += proof.MARKER + json_text(candidate) + '\n'
    terminal = deepcopy(qualified.record['terminal'])
    if fault == 'timeout': terminal['timed_out'] = True
    if fault == 'interrupted': terminal['interrupted'] = True
    if fault == 'exit': terminal['actual_exit_code'] = 1
    if fault == 'early': terminal['command'] = ['tools/sh-elf-run/run.sh', '--sid22-early']
    directory = qualified.root
    if storage == 'external':
        directory = qualified.root.parent / (qualified.root.name + '-data')
        directory.mkdir()
        (qualified.root / 'tmp').mkdir()
        (qualified.root / 'tmp/local-results').symlink_to(directory, target_is_directory=True)
    stdout, stderr = directory / 'later.stdout', directory / 'later.stderr'
    stdout.write_text(text)
    stderr.write_bytes(b'')
    for stream, path in (('stdout', stdout), ('stderr', stderr)):
        terminal[stream + '_sha256'] = hashlib.sha256(path.read_bytes()).hexdigest()
    process = directory / 'later-process.json'
    process.write_text(json.dumps(terminal))
    previous = (qualified.root / proof.RECEIPT).read_bytes()
    if fault in ('source-race', 'stream-race'):
        original_read = Path.read_bytes
        changed = False
        def read(path):
            nonlocal changed
            data = original_read(path)
            if path.resolve() == stdout.resolve() and not changed:
                changed = True
                if fault == 'stream-race': stdout.write_text(text + 'changed\n')
                else: current['producer_inputs']['controlled'] = 'f' * 64
            return data
        monkeypatch.setattr(Path, 'read_bytes', read)
    if fault == 'none':
        from kb import lock
        with lock.held(qualified.root, timeout=1):
            prepared = producer.prepare(process, stdout, stderr, qualified.root)
        assert prepared['candidate'] == candidate
        if storage == 'external':
            assert prepared['process_path'] == 'tmp/local-results/later-process.json'
            assert prepared['terminal']['stdout'] == 'tmp/local-results/later.stdout'
            assert prepared['terminal']['stderr'] == 'tmp/local-results/later.stderr'
        assert (qualified.root / proof.RECEIPT).read_bytes() == previous
        producer.finalize(process, stdout, stderr, qualified.root)
        assert award(qualified, 'verify')
    else:
        with pytest.raises((ValueError, KeyError)):
            producer.finalize(process, stdout, stderr, qualified.root)
        assert (qualified.root / proof.RECEIPT).read_bytes() == previous
        assert award(qualified, 'verify')
