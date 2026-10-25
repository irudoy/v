"""Exact I/O batch transition and positive owning-site evidence attachment."""

from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from kb import io_access_claim_contract as contract, io_access_evidence as proof
from kb import io_access_resolution as resolution
from kb import copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import levels, match, reconciliation, repo, test_contract, vocab, write
from kb.model import Link, Meaning, Model, Symbol, SymbolKey
from kb.repo import KbError


def relation(claim, meanings):
    return Link(meanings[claim['owner']], claim['type'], meanings[claim['to']], claim['slot'], claim['offset'],
                deepcopy(claim['props']), deepcopy(claim['evidence']), set(claim['stated']),
                set(claim['sources']), set(claim['roles']))


def qualified(model, rows):
    meanings = {meaning.key: meaning for meaning in model.meanings}
    for row in rows:
        old = next(link for link in model.links if contract.original(row, link))
        index = model.links.index(old)
        if row['disposition'] == 'relocate-site-evidence':
            del model.links[index]
            model.symbols[contract.symbol_key(row)].evidence = json.loads(row['proposed_symbol_evidence_json'])
        else:
            model.links[index] = relation(json.loads(row['proposed_claim_json']), meanings)
    for meaning in model.meanings:
        meaning.links = [link for link in model.links if link.owner is meaning]


@pytest.fixture
def transition(tmp_path, monkeypatch):
    declared = contract.descriptor(repo.ROOT)
    rows = declared['reference']
    monkeypatch.setattr(contract, 'descriptor', lambda root: deepcopy(declared))
    before = Model({}, {}, {}, {}, [])
    before.root, before.spaces, before.names = tmp_path, {}, []
    before.functions = {'7mfk': [0x2040, 0x2B768, 0xA6DC4, 0xC2FBE]}
    before.config = {'reconciliation': {'enabled': True, 'review': []}}
    meanings = {}

    def add(owner, key):
        meaning = Meaning(key.kind, name=owner.rsplit('/', 1)[0], sources={'controlled-native.toml'})
        meanings[owner] = meaning
        before.meanings.append(meaning)
        symbol = Symbol(key, meaning=meaning, sources={'controlled-native.toml'})
        before.symbols[key] = symbol
        meaning.symbols['7mfk'] = symbol
        return symbol

    for row in rows:
        claim = json.loads(row['original_claim_json'])
        symbol = add(row['owner'], contract.symbol_key(row))
        symbol.evidence = json.loads(row['original_symbol_evidence_json'])
        target = 0x2B768 if row['disposition'] == 'relocate-site-evidence' else row['actual_function']
        add(claim['to'], SymbolKey('7mfk', 'fn', target))
        before.links.append(relation(claim, meanings))
        ledger = json.loads(row['original_ledger_json'])
        if ledger is not None:
            before.stash.setdefault('ledger_rows', []).append(('reg', row['owner'].rsplit('/', 1)[0], ledger, row['source']))
        document = json.loads(row['original_native_json'])
        meanings[row['owner']].tables = {key: deepcopy(document[key]) for key in ('diagnostic',) if key in document}
        path = tmp_path / row['source']
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('controlled native source')
    for link in before.links:
        link.owner.links.append(link)
    after = deepcopy(before)
    qualified(after, rows)
    resolutions = {row['id']: row['original_claim_sha256'] for row in rows}
    ops = [dict(cmd='reconcile-io-access', id=key, claim_sha256=value) for key, value in resolutions.items()]
    monkeypatch.setattr(proof, 'require_current', lambda model: dict(controlled_admission=True))
    # These controlled models grant no original execution or physical namespace admission.
    for module in (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence):
        monkeypatch.setattr(module, 'scope_digest', lambda model: 'controlled-scope')
    return rows, before, after, resolutions, ops


def test_exact_transition_removes_only_capture_reader_and_appends_existing_owning_evidence(transition):
    rows, before, after, resolutions, ops = transition
    before_view, after_view = write.publication_view(before), write.publication_view(after)
    assert test_contract.exact(resolution.publication_expected(before, after, resolutions, before_view, after_view), after_view)
    assert len(before.links) == 3 and len(after.links) == 2
    capture = rows[1]
    symbol = after.symbols[contract.symbol_key(capture)]
    assert symbol.evidence[0] == {'kind': 'l0', 'supports': 'identity', 'at': '7mfk:0000204e'}
    assert symbol.evidence[1] == contract.item(capture)
    assert SymbolKey('7mfk', 'fn', 0x2040) not in after.symbols
    assert not any(f'{name}/{kind}' == capture['owner'] for kind, name, _, _ in after.stash['ledger_rows'])
    change = SimpleNamespace(width_resolutions={}, diagnostic_resolutions={}, argument_resolutions={},
                             calculation_resolutions={}, snapshot_resolutions={}, io_resolutions=resolutions)
    path = before.root / repo.OWNER_CONFIG
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('controlled reviews')
    write.require_metadata_only(before, after, ops, change, {repo.OWNER_CONFIG: 'controlled reviews'})


@pytest.mark.parametrize('fault', ('partial', 'duplicate', 'id', 'sha', 'extra', 'direct-link'))
def test_preflight_requires_three_unique_exact_operations(transition, fault):
    rows, _, _, _, ops = transition
    ops = deepcopy(ops)
    if fault == 'partial':
        ops.pop()
    elif fault == 'duplicate':
        ops[-1] = deepcopy(ops[0])
    elif fault == 'id':
        ops[0]['id'] = 'other'
    elif fault == 'sha':
        ops[0]['claim_sha256'] = '0' * 64
    elif fault == 'extra':
        ops[0]['evidence'] = [contract.item(rows[0])]
    else:
        ops.append(dict(cmd='link', type='writer', meaning=rows[0]['owner'], to='granite-chameleon/fn',
                        evidence=[contract.item(rows[0])]))
    with pytest.raises(KbError):
        write.require_publication_operations(ops)


@pytest.mark.parametrize('fault', ('key', 'path', 'mode', 'scope', 'supports', 'ambiguous'))
def test_reserved_proof_never_falls_back_to_generic_indirect_code(transition, fault):
    rows, _, model, _, _ = transition
    row = rows[0]
    symbol = model.symbols[contract.symbol_key(row)]
    item = deepcopy(contract.item(row))
    if fault == 'key':
        item['key'] = contract.PREFIX + 'unknown'
    elif fault == 'path':
        item['path'] = 'defs/other.toml'
    elif fault == 'mode':
        item['mode'] = 'base'
    elif fault == 'scope':
        item['value']['width_bytes'] = 4
    elif fault == 'supports':
        item['supports'] = 'scale'
    else:
        item['mode'] = 'block-copy'
    assert contract.registered(item)
    assert copy_evidence.failure(item, symbol, model, 'identity') is not None
    assert match.verify(model, symbol, item) is not None
    assert match.rank(item, symbol, model, 'identity') == -1


def test_reserved_io_mode_is_a_declared_schema_mode():
    assert 'io-access' in vocab.INDIRECT_MODES


def test_prepare_preserves_complete_native_documents_and_uses_existing_symbol_evidence_contract(transition, monkeypatch):
    rows, before, _, _, ops = transition
    questions = [dict(kind='access', subject=contract.symbol_key(row).key, claim_sha256=row['original_claim_sha256'])
                 for row in rows]
    before.config['reconciliation']['review'] = [dict(item, state='unresolved', reason='controlled question') for item in questions]
    monkeypatch.setattr(reconciliation, 'differences', lambda model: deepcopy(questions))
    documents = {row['owner']: json.loads(row['original_native_json']) for row in rows}
    paths = {row['owner']: Path(row['source']) for row in rows}
    change = SimpleNamespace(model=before, root=before.root, io_resolutions={}, expected=[], lines=[],
        document=lambda meaning: (paths[meaning.key], documents[meaning.key]))
    for op in ops:
        resolution.prepare(change, op)
    for row in rows:
        assert test_contract.exact(documents[row['owner']], json.loads(row['proposed_native_json']))
    assert len(change.expected) == 1


@pytest.mark.parametrize('fault', ('partial', 'keep-reader', 'duplicate-evidence', 'reorder-evidence', 'ledger',
                                  'diagnostic', 'property', 'geometry', 'TEST', 'function'))
def test_transition_refuses_another_native_value_or_evidence_position(transition, fault):
    rows, before, after, resolutions, _ = transition
    capture = after.symbols[contract.symbol_key(rows[1])]
    if fault == 'partial':
        resolutions.pop(rows[0]['id'])
    elif fault == 'keep-reader':
        meanings = {meaning.key: meaning for meaning in after.meanings}
        after.links.append(relation(json.loads(rows[1]['original_claim_json']), meanings))
    elif fault == 'duplicate-evidence':
        capture.evidence.append(deepcopy(capture.evidence[-1]))
    elif fault == 'reorder-evidence':
        capture.evidence.reverse()
    elif fault == 'ledger':
        after.stash['ledger_rows'].append(('reg', 'ingenious-kagu', [], rows[1]['source']))
    elif fault == 'diagnostic':
        after.symbols[contract.symbol_key(rows[2])].meaning.tables['diagnostic'] = []
    elif fault == 'property':
        capture.meaning.props['unit'] = 'ms'
    elif fault == 'geometry':
        capture.props['width'] = 16
    elif fault == 'TEST':
        capture.evidence.append(dict(kind='test', path='controlled.py', key='test_identity', supports='identity'))
    else:
        after.functions['7mfk'].append(0x204E)
    with pytest.raises((ValueError, KbError)):
        expected = resolution.publication_expected(before, after, resolutions,
            write.publication_view(before), write.publication_view(after))
        if not test_contract.exact(expected, write.publication_view(after)):
            raise ValueError('another native value changes')


@pytest.mark.parametrize('failure', (None, 'unqualified original'))
def test_link_proof_grounds_only_owning_identity_without_reverse_or_scale_donation(transition, monkeypatch, failure):
    _, _, model, _, _ = transition
    link = model.links[0]
    link.props.update(relies='structure', supports='identity', reverse_relies='structure', reverse_supports='identity')
    collector = object.__new__(levels._Collector)
    collector.model, collector.pointed, collector.symbols = model, set(), {}
    own = levels.Claim('controlled', 'owner', 'identity', 'code')
    scale = levels.Claim('controlled', 'scale', 'scale', 'code')
    reverse = levels.Claim('controlled', 'function', 'identity', 'code')
    collector.meanings = {(id(link.owner), 'identity'): own, (id(link.owner), 'scale'): scale,
                          (id(link.to), 'identity'): reverse}
    monkeypatch.setattr(proof, 'link_failure', lambda model, link: failure)
    collector._link(link)
    assert scale.items == scale.deps == reverse.items == reverse.deps == []
    if failure is None:
        assert own.deps == [] and own.items == [(link.owner.symbols['7mfk'], link.evidence[-1])]
    else:
        assert own.items == [] and len(own.deps) == 1 and own.deps[0].lacks == failure
