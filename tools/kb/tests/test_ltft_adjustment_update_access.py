"""Exact three-owner composition, preserved reverse roles and finite operation refusals."""
from copy import deepcopy
import hashlib
import json
from types import SimpleNamespace
import pytest
from kb import repo
from kb.model import SymbolKey
from kb import ltft_adjustment_update_access_contract as contract, ltft_adjustment_update_access_evidence as proof


def declared():
    return contract.descriptor(repo.ROOT)


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']), to=SimpleNamespace(key=document['to']),
        type=document['type'], slot=document['slot'], offset=document['offset'], roles=list(document['roles']),
        props=deepcopy(document['props']), evidence=deepcopy(document['evidence']),
        stated=list(document['stated']), sources=list(document['sources']))


def test_exact_nine_appends_preserve_all_other_owner_facts_and_individual_claims():
    value = declared(); rows = value['reference']; peers = value['companions']
    assert len(rows) == 3 and len(peers) == 6 and len({row['owner'] for row in rows}) == 3
    before = {row['owner']: json.loads(row['original_native_json']) for row in rows}
    after = {row['owner']: json.loads(row['proposed_native_json']) for row in rows}
    stripped = deepcopy(after)
    for row in (*peers, *rows):
        old = json.loads(row['original_claim_json']); new = json.loads(row['proposed_claim_json'])
        expected = deepcopy(old); expected['evidence'].append(contract.item(row))
        assert new == expected
        target = next(item for item in stripped[row['owner']]['link'] if (item['type'], item['to']) == (old['type'], old['to']))
        original = next(item for item in before[row['owner']]['link'] if (item['type'], item['to']) == (old['type'], old['to']))
        assert target['evidence'].pop() == contract.item(row)
        if not target['evidence'] and 'evidence' not in original:
            target.pop('evidence')
    assert stripped == before
    for row in rows:
        old = json.loads(row['original_claim_json']); new = json.loads(row['proposed_claim_json'])
        assert old['props'] == new['props'] and old['roles'] == new['roles']
        if row['direction'] == 'reader':
            assert old['roles'] == ['indexed_by'] and 'supports' not in old['props'] and 'relies' not in old['props']
            assert old['props']['reverse_supports'] == 'identity'
        assert row['declared_width'] == 16 and row['declared_signed'] == 'unset'
        assert row['original_ledger_json'] == row['proposed_ledger_json']
    for path, wanted in value['companion_source_sha256'].items():
        assert hashlib.sha256((repo.ROOT / path).read_bytes()).hexdigest() == wanted


@pytest.mark.parametrize('fault', ('missing-own', 'missing-peer', 'duplicate-own', 'duplicate-peer', 'changed-peer', 'scale', 'extra-evidence'))
def test_only_three_exact_new_and_six_known_existing_operations_are_admitted(fault):
    value = declared()
    own = [contract.operation(row) for row in value['reference']]
    peers = contract.companion_operations(repo.ROOT)
    assert contract.operations([*reversed(peers), *reversed(own)], repo.ROOT)
    operations = deepcopy([*own, *peers])
    if fault == 'missing-own':
        operations.pop(0)
    elif fault == 'missing-peer':
        operations.pop()
    elif fault == 'duplicate-own':
        operations.append(deepcopy(own[0]))
    elif fault == 'duplicate-peer':
        operations.append(deepcopy(peers[0]))
    elif fault == 'changed-peer':
        operations[-1]['meaning'] = 'unrelated/ram'
    elif fault == 'scale':
        operations[0]['evidence'][0]['supports'] = 'scale'
    else:
        operations[-1]['evidence'].append(dict(kind='trace', supports='identity'))
    with pytest.raises(ValueError):
        contract.operations(operations, repo.ROOT)


def model_for(documents, phases, monkeypatch):
    value = declared(); symbols = {}
    source_documents = {}
    ledgers = {}
    for row in value['reference']:
        symbols[contract.symbol_key(row)] = SimpleNamespace(meaning=SimpleNamespace(key=row['owner']),
            evidence=json.loads(row['original_symbol_evidence_json']), value=lambda name: {'width': 16, 'signed': None}[name])
        source_documents[row['source']] = documents[row['owner']]
        ledgers[row['owner']] = json.loads(row['original_ledger_json'])
    for row in value['retained_functions']:
        symbols[SymbolKey('7mfk', 'fn', row['address'])] = SimpleNamespace(meaning=SimpleNamespace(key=row['owner']))
        source_documents[row['source']] = json.loads(row['native_json'])
    model = SimpleNamespace(root=repo.ROOT, symbols=symbols, overlay={}, stash={},
        links=[link(json.loads(row[phases[row['owner']] + '_claim_json'])) for row in (*value['reference'], *value['companions'])])
    monkeypatch.setattr(proof.store, 'load', lambda root, path, overlay: deepcopy(source_documents[str(path)]))
    monkeypatch.setattr(proof, 'native_ledger', lambda model, owner: deepcopy(ledgers[owner]))
    return model


@pytest.mark.parametrize('phase', ('original', 'proposed'))
def test_only_one_complete_common_native_phase_is_admitted(phase, monkeypatch):
    value = declared()
    documents = {row['owner']: json.loads(row[phase + '_native_json']) for row in value['reference']}
    model = model_for(documents, {owner: phase for owner in documents}, monkeypatch)
    assert proof.native_rows(model) == value['reference']


@pytest.mark.parametrize('fault', ('mixed-phase', 'missing-old-append', 'missing-new-append', 'extra-append', 'other-note', 'width', 'signed'))
def test_partial_mixed_or_unrelated_owner_changes_refuse_the_whole_composition(fault, monkeypatch):
    value = declared(); rows = value['reference']
    documents = {row['owner']: json.loads(row['proposed_native_json']) for row in rows}
    phases = {owner: 'proposed' for owner in documents}
    selected = rows[0]
    if fault == 'mixed-phase':
        documents[selected['owner']] = json.loads(selected['original_native_json']); phases[selected['owner']] = 'original'
    elif fault in ('missing-old-append', 'missing-new-append'):
        attachment = value['companions'][0] if fault == 'missing-old-append' else selected
        claim = json.loads(attachment['original_claim_json'])
        target = next(item for item in documents[attachment['owner']]['link'] if (item['type'], item['to']) == (claim['type'], claim['to']))
        target['evidence'].pop()
        if not target['evidence']:
            target.pop('evidence')
    elif fault == 'extra-append':
        next(item for item in documents[selected['owner']]['link'] if item.get('evidence'))['evidence'].append(dict(kind='trace', supports='identity'))
    elif fault == 'other-note':
        documents[selected['owner']]['note'].append('Unrelated assertion')
    elif fault == 'width':
        documents[selected['owner']]['width'] = 8
    else:
        documents[selected['owner']]['signed'] = False
    model = model_for(documents, phases, monkeypatch)
    with pytest.raises(ValueError):
        proof.native_rows(model)


def test_publication_requires_the_unique_exact_owning_claim_and_namespace():
    for row in declared()['reference']:
        item = contract.item(row); current = link(json.loads(row['proposed_claim_json']))
        assert contract.publication(current, item)
        current.evidence.append(deepcopy(item))
        assert not contract.publication(current, item)
    for mode in ('learning-transfer-access', 'bank-pulse-access', 'scalar-ram-leaf-withdrawal', 'register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
