"""Grouped existing-owner appends preserve all other native facts and TEST origins."""

from copy import deepcopy
import json
from types import SimpleNamespace

import pytest

from kb import maf_access_contract as contract, maf_access_evidence as proof
from kb import maf_access_resolution as resolution
from kb import copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import levels, match, repo, test_contract, write
from kb.model import Link, Meaning, Model, Symbol, SymbolKey
from kb.repo import KbError


def relation(row, meanings, qualified=False, correct=False):
    claim = json.loads(row['correct_original_claim_json'] if correct else
        row['proposed_claim_json'] if qualified else row['original_claim_json'])
    return Link(meanings[claim['owner']], claim['type'], meanings[claim['to']], claim['slot'], claim['offset'],
        deepcopy(claim['props']), deepcopy(claim['evidence']), set(claim['stated']), set(claim['sources']), set(claim['roles']))


@pytest.fixture
def transition(tmp_path, monkeypatch):
    declared = contract.descriptor(repo.ROOT)
    rows = declared['reference']
    monkeypatch.setattr(contract, 'descriptor', lambda root: deepcopy(declared))
    before = Model({}, {}, {}, {}, [])
    before.root, before.spaces, before.functions, before.names = tmp_path, {}, {'7mfk': sorted({row['function'] for row in rows}|{0x3B27E})}, []
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
            before.stash.setdefault('ledger_rows', []).append((symbol.kind, row['owner'].rsplit('/', 1)[0],
                json.loads(row['original_ledger_json']), row['source']))
        add(claim['to'], SymbolKey('7mfk', 'fn', 0x3B27E if contract.correction(row) else row['function']))
        before.links.append(relation(row, meanings))
        if contract.correction(row):
            add(contract.base_claim(row)['to'],SymbolKey('7mfk','fn',row['function']))
            before.links.append(relation(row,meanings,correct=True))
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
    return rows, before, after, [*[contract.removal(row) for row in rows if contract.correction(row)],
                                *[contract.operation(row) for row in rows]]


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
    assert len(rows)==34 and len(documents)==21
    change = object.__new__(write.Change)
    change.model, change.lines = model, []
    change._ends = lambda op: (owners[op['meaning']], owners[op['to']], op['type'])
    change.document = lambda meaning: (None, documents[meaning.key])
    change._held = lambda meaning: documents.get(meaning.key)
    for op in ops:
        getattr(change,op['cmd'])(op)
    for row in rows:
        assert test_contract.exact(documents[row['owner']], json.loads(row['proposed_native_json']))


@pytest.mark.parametrize('owner,count',(('maf_b1/ram',2),('maf_b2/ram',4)))
def test_shared_bank_owner_appends_preserve_every_other_layout_manual_and_ledger_value(transition,owner,count):
    rows,_,_,_=transition
    selected=[row for row in rows if row['owner']==owner]
    assert len(selected)==count
    before=json.loads(selected[0]['original_native_json'])
    after=json.loads(selected[0]['proposed_native_json'])
    assert test_contract.exact({key:value for key,value in before.items() if key!='link'},
                               {key:value for key,value in after.items() if key!='link'})
    assert before['symbol']==after['symbol']
    assert before.get('ledger')==after.get('ledger')


def test_unattached_original_refuses_before_full_native_relation_scan(transition, monkeypatch):
    rows, model, _, _ = transition
    monkeypatch.setattr(proof, 'native_rows', lambda model: pytest.fail('an unattached claim performs full MAF admission'))
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
        ops[0]['type'] = 'writer'
    elif fault == 'wrong-sha':
        next(op for op in ops if op['cmd']=='link')['evidence'][0]['value']['original_claim_sha256'] = '0' * 64
    else:
        ops[0]['keys'] = {'supports': 'scale'}
    with pytest.raises(KbError):
        write.require_publication_operations(ops)


@pytest.mark.parametrize('fault',('missing','duplicate','wrong-owner','wrong-target','wrong-direction','extra-key','only-unlinks'))
def test_only_both_exact_MAF_unlinks_inside_the_complete_joint_batch_are_allowed(transition,fault):
    _,_,_,ops=transition;ops=deepcopy(ops)
    if fault=='missing':ops.pop(0)
    elif fault=='duplicate':ops.append(deepcopy(ops[0]))
    elif fault=='wrong-owner':ops[0]['meaning']='other/tbl'
    elif fault=='wrong-target':ops[0]['to']='dual_bank_maf_coordinator/fn'
    elif fault=='wrong-direction':ops[0]['type']='writer'
    elif fault=='extra-key':ops[0]['keys']={'slot':'other'}
    else:ops=[op for op in ops if op['cmd']=='unlink']
    with pytest.raises(KbError):write.require_publication_operations(ops)


@pytest.mark.parametrize('identity',('source-copy-read','curve-attribution-000141f4-reader','curve-attribution-00014274-reader',
    'record0129-00025e20-member-reader','record0129-0003c3ac-member-reader','battery-satisfied-oarfish-reader'))
@pytest.mark.parametrize('fault',('changed-proof','duplicate-proof','native-property','wrong-owner'))
def test_only_unique_exact_MAF_owning_appends_are_neutral_to_existing_physical_scopes(transition,identity,fault):
    rows,_,after,_=transition;row=next(row for row in rows if row['id']==identity)
    link=deepcopy(next(link for link in after.links if contract.qualified(row,link)));item=link.evidence[-1]
    assert contract.publication(link,item) is True
    assert copy_evidence.semantic_evidence(link)==contract.base_claim(row)['evidence']
    if fault=='changed-proof':item['value']['native_address']^=1
    elif fault=='duplicate-proof':link.evidence.append(deepcopy(item))
    elif fault=='native-property':link.props['supports']='scale'
    else:link.owner=deepcopy(next(value.owner for value in after.links if value.owner.key!=row['owner']))
    assert item in copy_evidence.semantic_evidence(link)


@pytest.mark.parametrize('fault',('missing-correct-before','changed-correct-before','duplicate-correct-before',
    'changed-evidence-before','unqualified-correct-after'))
def test_reader_correction_preserves_the_exact_existing_correct_relation(transition,fault):
    rows,before,after,_=transition
    row=next(row for row in rows if contract.correction(row))
    link=next(link for link in before.links if contract.correct_original(row,link))
    if fault=='missing-correct-before':before.links.remove(link)
    elif fault=='changed-correct-before':link.props['reverse_supports']='scale'
    elif fault=='duplicate-correct-before':before.links.append(deepcopy(link))
    elif fault=='changed-evidence-before':link.evidence.append(dict(kind='spec',path='other.md',key='other'))
    else:after.links.append(deepcopy(link))
    with pytest.raises(ValueError):resolution.require_transition(before,after)


@pytest.mark.parametrize('fault', ('ledger', 'symbol-evidence', 'TEST-position', 'property', 'width', 'signed', 'scope', 'reverse', 'duplicate'))
def test_publication_refuses_other_native_values_or_original_positions(transition, fault):
    rows, before, after, ops = transition
    symbol = next(member for member in after.symbols.values()
                  if member.meaning.key == 'spiked-dalmatian/ram')
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


@pytest.mark.parametrize('field,value', (('mode', 'base'), ('mode', 'maf-copy-filter'),
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
