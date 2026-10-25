"""Grouped existing-owner appends preserve all other native facts and TEST origins."""

from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from kb import counter_access_contract as contract, counter_access_evidence as proof
from kb import counter_access_resolution as resolution
from kb import copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import levels, match, repo, test_contract, write
from kb.model import Link, Meaning, Model, Symbol, SymbolKey
from kb.repo import KbError


def relation(row, meanings, qualified=False):
    claim = json.loads(row['proposed_claim_json'] if qualified else row['original_claim_json'])
    return Link(meanings[claim['owner']], claim['type'], meanings[claim['to']], claim['slot'], claim['offset'],
        deepcopy(claim['props']), deepcopy(claim['evidence']), set(claim['stated']), set(claim['sources']), set(claim['roles']))


@pytest.fixture
def transition(tmp_path, monkeypatch):
    declared = contract.descriptor(repo.ROOT)
    rows = declared['reference']
    monkeypatch.setattr(contract, 'descriptor', lambda root: deepcopy(declared))
    before = Model({}, {}, {}, {}, [])
    before.root, before.spaces, before.functions, before.names = tmp_path, {}, {'7mfk': sorted({row['function'] for row in rows})}, []
    before.config = {'reconciliation': {'enabled': True, 'review': []}}
    meanings = {}

    def add(owner, key):
        if owner in meanings:
            return before.symbols[key], False
        meaning = Meaning(key.kind, name=owner.rsplit('/', 1)[0], sources={'controlled-native.toml'})
        meanings[owner] = meaning
        before.meanings.append(meaning)
        symbol = Symbol(key, meaning=meaning, sources={'controlled-native.toml'})
        before.symbols[key] = symbol
        meaning.symbols['7mfk'] = symbol
        return symbol, True

    for row in rows:
        claim = json.loads(row['original_claim_json'])
        symbol, added = add(row['owner'], contract.symbol_key(row))
        symbol.props.update(width=contract.native_type(row,'width'), signed=contract.native_type(row,'signed'))
        symbol.evidence = json.loads(row['original_symbol_evidence_json'])
        if added and json.loads(row['original_ledger_json']) is not None:
            before.stash.setdefault('ledger_rows', []).append(('ram', row['owner'].rsplit('/', 1)[0],
                json.loads(row['original_ledger_json']), row['source']))
        add(claim['to'], SymbolKey('7mfk', 'fn', row['function']))
        before.links.append(relation(row, meanings))
    for meaning in before.meanings:
        meaning.links = [link for link in before.links if link.owner is meaning]
    after = deepcopy(before)
    after_owners = {meaning.key: meaning for meaning in after.meanings}
    after.links = [relation(row, after_owners, True) for row in rows]
    for meaning in after.meanings:
        meaning.links = [link for link in after.links if link.owner is meaning]
    monkeypatch.setattr(proof, 'require_current', lambda model: dict(controlled_admission=True))
    # Controlled publication tests provide no original execution or namespace admission.
    for module in (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence):
        monkeypatch.setattr(module, 'scope_digest', lambda model: 'controlled-scope')
    return rows, before, after, [contract.operation(row) for row in rows]


def test_exact_joint_appends_change_only_existing_relation_evidence(transition):
    _, before, after, ops = transition
    expected = resolution.publication_expected(before, after, write.publication_view(before))
    assert test_contract.exact(expected, write.publication_view(after))
    assert contract.operations(ops, before.root) is True
    write.require_metadata_only(before, after, ops, SimpleNamespace(width_resolutions={}), {})


def test_existing_link_writer_preserves_complete_grouped_owner_documents(transition):
    rows, model, _, ops = transition
    owners = {meaning.key: meaning for meaning in model.meanings}
    documents = {row['owner']: json.loads(row['original_native_json']) for row in rows}
    change = object.__new__(write.Change)
    change.model, change.lines = model, []
    change._ends = lambda op: (owners[op['meaning']], owners[op['to']], op['type'])
    change.document = lambda meaning: (None, documents[meaning.key])
    for op in ops:
        change.link(op)
    for row in rows:
        assert test_contract.exact(documents[row['owner']], json.loads(row['proposed_native_json']))


@pytest.mark.parametrize('fault',('changed-proof','duplicate-proof','changed-native-property','wrong-owner'))
def test_only_the_unique_exact_owning_append_is_neutral_to_physical_scopes(transition,fault):
    rows,before,after,_=transition
    link=deepcopy(after.links[0]);item=link.evidence[-1]
    assert contract.publication(link,item) is True
    assert copy_evidence.semantic_evidence(link)==before.links[0].evidence
    if fault=='changed-proof':item['value']['native_address']^=1
    elif fault=='duplicate-proof':link.evidence.append(deepcopy(item))
    elif fault=='changed-native-property':link.props['supports']='scale'
    else:link.owner=deepcopy(after.links[-1].owner)
    assert item in copy_evidence.semantic_evidence(link)


def test_unattached_original_refuses_before_full_native_relation_scan(transition, monkeypatch):
    rows, model, _, _ = transition
    monkeypatch.setattr(proof, 'native_rows', lambda model: pytest.fail('an unattached claim performs full counter array admission'))
    for row in rows:
        symbol = model.symbols[contract.symbol_key(row)]
        function = model.symbols[SymbolKey('7mfk', 'fn', row['function'])]
        claim = json.loads(row['original_claim_json'])
        assert proof.accepted(model, symbol, function, claim) is None


def test_registered_attachment_keeps_full_native_admission_path(transition, monkeypatch):
    rows, _, model, _ = transition
    seen = []
    def refuse(current):
        seen.append(current)
        raise ValueError('controlled exact native refusal')
    monkeypatch.setattr(proof, 'native_rows', refuse)
    row = rows[0]
    symbol = model.symbols[contract.symbol_key(row)]
    function = model.symbols[SymbolKey('7mfk', 'fn', row['function'])]
    assert proof.accepted(model, symbol, function, json.loads(row['proposed_claim_json'])) is None
    assert seen == [model]


@pytest.mark.parametrize('fault', ('partial', 'duplicate', 'wrong-owner', 'wrong-direction', 'wrong-sha', 'other-property'))
def test_batch_preflight_refuses_incomplete_or_changed_normal_link_operations(transition, fault):
    _, _, _, ops = transition
    ops = deepcopy(ops)
    if fault == 'partial':
        ops.pop()
    elif fault == 'duplicate':
        ops[-1] = deepcopy(ops[0])
    elif fault == 'wrong-owner':
        ops[0]['meaning'] = 'other/ram'
    elif fault == 'wrong-direction':
        ops[0]['type'] = 'reader'
    elif fault == 'wrong-sha':
        ops[0]['evidence'][0]['value']['original_claim_sha256'] = '0' * 64
    else:
        ops[0]['keys'] = {'supports': 'scale'}
    with pytest.raises(KbError):
        write.require_publication_operations(ops)


@pytest.mark.parametrize('fault', ('ledger', 'symbol-evidence', 'TEST-position', 'property', 'width', 'signed', 'scope', 'reverse', 'duplicate'))
def test_publication_refuses_other_native_values_or_original_positions(transition, fault):
    rows, before, after, ops = transition
    symbol = next(member for member in after.symbols.values()
                  if member.meaning.key == 'crimson-binturong/ram')
    if fault == 'ledger':
        after.stash['ledger_rows'][0][2][0]['notes'] = []
    elif fault == 'symbol-evidence':
        symbol.evidence.pop()
    elif fault == 'TEST-position':
        symbol.evidence.reverse()
    elif fault == 'property':
        symbol.meaning.props['unit'] = 'g/s'
    elif fault == 'width':
        symbol.props['width'] = 8
    elif fault == 'signed':
        symbol.props['signed'] = not symbol.props['signed']
    elif fault == 'scope':
        after.links[-1].evidence[-1]['value']['native_address'] += 2
    elif fault == 'reverse':
        after.links[-1].props['reverse_supports'] = 'scale'
    else:
        after.links[-1].evidence.append(deepcopy(after.links[-1].evidence[-1]))
    with pytest.raises((ValueError, KbError)):
        write.require_metadata_only(before, after, ops, SimpleNamespace(width_resolutions={}), {})


@pytest.mark.parametrize('field,value', (('mode', 'base'), ('mode', 'block-copy'),
                                       ('key', contract.PREFIX + 'unknown'), ('supports', 'scale')))
def test_reserved_item_never_receives_generic_indirect_rank(transition, field, value):
    rows, _, model, _ = transition
    symbol = model.symbols[contract.symbol_key(rows[0])]
    item = deepcopy(contract.item(rows[0]))
    item[field] = value
    assert copy_evidence.failure(item, symbol, model, 'identity') is not None
    assert match.verify(model, symbol, item) is not None
    assert match.rank(item, symbol, model, 'identity') == -1


@pytest.mark.parametrize('failure', (None, 'unqualified original'))
def test_only_owning_identity_receives_proof_without_reverse_function_donation(transition, monkeypatch, failure):
    _, _, model, _ = transition
    link = model.links[0]
    own = levels.Claim('controlled', 'owner', 'identity', 'code')
    scale = levels.Claim('controlled', 'scale', 'scale', 'code')
    reverse = levels.Claim('controlled', 'function', 'identity', 'code')
    collector = object.__new__(levels._Collector)
    collector.model, collector.pointed, collector.symbols = model, set(), {}
    collector.meanings = {(id(link.owner), 'identity'): own, (id(link.owner), 'scale'): scale,
                          (id(link.to), 'identity'): reverse}
    monkeypatch.setattr(proof, 'link_failure', lambda model, link: failure)
    collector._link(link)
    assert scale.items == scale.deps == reverse.items == reverse.deps == []
    if failure is None:
        assert own.deps == [] and own.items == [(link.owner.symbols['7mfk'], link.evidence[-1])]
    else:
        assert own.items == [] and len(own.deps) == 1 and own.deps[0].lacks == failure
