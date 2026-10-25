"""Finite shared owner postimages, exact claims and native preservation refusals."""
from copy import deepcopy
import json
from pathlib import Path
from types import SimpleNamespace
import pytest
from kb import repo
from kb.model import SymbolKey
from kb import channel_target_builder_access_contract as contract, channel_target_builder_access_evidence as proof
from kb import channel_target_reader_access_contract as reader


def row():
    return contract.descriptor(repo.ROOT)['reference'][0]


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']), to=SimpleNamespace(key=document['to']),
        type=document['type'], slot=document['slot'], offset=document['offset'], roles=list(document['roles']),
        props=deepcopy(document['props']), evidence=deepcopy(document['evidence']),
        stated=list(document['stated']), sources=list(document['sources']))


def test_two_finite_declarations_share_one_exact_owner_postimage_and_preserve_all_other_facts():
    selected = row()
    peer = reader.descriptor(repo.ROOT)['reference'][0]
    assert selected['original_native_json'] == peer['original_native_json']
    assert selected['proposed_native_json'] == peer['proposed_native_json']
    before, after = (json.loads(selected[name + '_native_json']) for name in ('original', 'proposed'))
    stripped = deepcopy(after)
    for attachment in (selected, peer):
        original_claim = json.loads(attachment['original_claim_json'])
        proposed_claim = json.loads(attachment['proposed_claim_json'])
        expected_claim = deepcopy(original_claim); expected_claim['evidence'].append(contract.item(attachment))
        assert proposed_claim == expected_claim
        target = next(value for value in stripped['link'] if (value['type'], value['to']) ==
                      (original_claim['type'], original_claim['to']))
        original = next(value for value in before['link'] if (value['type'], value['to']) ==
                        (original_claim['type'], original_claim['to']))
        assert target['evidence'].pop() == contract.item(attachment)
        if not target['evidence'] and 'evidence' not in original:
            target.pop('evidence')
    assert stripped == before and after['width'] == 16 and 'signed' not in after
    assert after['unit'] == 'percent' and after['scale'] == 'x*34285/1114112'
    assert selected['original_ledger_json'] == selected['proposed_ledger_json']
    retained = contract.descriptor(repo.ROOT)['retained_functions']
    assert [(value['owner'], value['address']) for value in retained] == [
        ('throttle_target_scaler/fn', 0xCB1CA), ('channel_throttle_target_builder/fn', 0x6F48C)]
    assert contract.item(selected)['value']['native_index_premise'] == dict(register=4, low_byte=1, upper24_bits_independent=True)


@pytest.mark.parametrize('fault', ('own-only', 'peer-only', 'duplicate-own', 'duplicate-peer', 'changed-peer', 'wrong-owner', 'scale'))
def test_only_the_two_exact_known_normal_link_operations_form_the_batch(fault):
    own = contract.operation(row())
    peer = contract.companion_operation(repo.ROOT)
    assert contract.operations([deepcopy(peer), deepcopy(own)], repo.ROOT)
    assert reader.operations([deepcopy(peer), deepcopy(own)], repo.ROOT)
    operations = [own, peer]
    if fault == 'own-only':
        operations = [own]
    elif fault == 'peer-only':
        operations = [peer]
        assert contract.operations(operations, repo.ROOT) is False
        with pytest.raises(ValueError):
            reader.operations(operations, repo.ROOT)
        return
    elif fault == 'duplicate-own':
        operations.append(deepcopy(own))
    elif fault == 'duplicate-peer':
        operations.append(deepcopy(peer))
    elif fault == 'changed-peer':
        peer['to'] = 'channel_throttle_target_builder/fn'
    elif fault == 'wrong-owner':
        own['meaning'] = 'throttle_target_channel_0/ram'
    else:
        own['evidence'][0]['supports'] = 'scale'
    with pytest.raises(ValueError):
        contract.operations(operations, repo.ROOT)


def model_for(document, phase, monkeypatch):
    declared = contract.descriptor(repo.ROOT)
    selected = declared['reference'][0]
    companion = declared['companion']
    owner = SimpleNamespace(key=selected['owner'])
    symbol = SimpleNamespace(meaning=owner, evidence=json.loads(selected['original_symbol_evidence_json']),
        value=lambda name: {'width': 16, 'signed': None}[name])
    symbols = {contract.symbol_key(selected): symbol}
    documents = {selected['source']: document}
    for retained in declared['retained_functions']:
        symbols[SymbolKey('7mfk', 'fn', retained['address'])] = SimpleNamespace(meaning=SimpleNamespace(key=retained['owner']))
        documents[retained['source']] = json.loads(retained['native_json'])
    model = SimpleNamespace(root=repo.ROOT, symbols=symbols, overlay={}, stash={},
        links=[link(json.loads(attachment[phase + '_claim_json'])) for attachment in (selected, companion)])
    monkeypatch.setattr(proof.store, 'load', lambda root, path, overlay: deepcopy(documents[str(Path(path))]))
    monkeypatch.setattr(proof, 'native_ledger', lambda model, owner: json.loads(selected['original_ledger_json']))
    return model


@pytest.mark.parametrize('phase', ('original', 'proposed'))
def test_native_guards_admit_only_the_exact_complete_before_or_joint_after(phase, monkeypatch):
    selected = row()
    model = model_for(json.loads(selected[phase + '_native_json']), phase, monkeypatch)
    assert proof.native_rows(model) == [selected]


@pytest.mark.parametrize('fault', ('writer-only', 'reader-only', 'extra-evidence', 'other-note', 'width', 'signed', 'ledger'))
def test_partial_or_unrelated_owner_changes_cannot_match_the_finite_native_boundary(fault, monkeypatch):
    selected = row()
    document = json.loads(selected['proposed_native_json'])
    if fault in ('writer-only', 'reader-only'):
        direction = 'reader' if fault == 'writer-only' else 'writer'
        target = next(value for value in document['link'] if value['type'] == direction
                      and value['to'] in ('throttle_target_scaler/fn', 'channel_throttle_target_builder/fn'))
        target.pop('evidence')
    elif fault == 'extra-evidence':
        next(value for value in document['link'] if value['type'] == 'writer')['evidence'].append(dict(kind='trace', supports='identity'))
    elif fault == 'other-note':
        document['note'].append('Unrelated source assertion')
    elif fault == 'width':
        document['width'] = 8
    elif fault == 'signed':
        document['signed'] = False
    else:
        document['ledger'][0]['identity'].append(3)
    model = model_for(document, 'proposed', monkeypatch)
    with pytest.raises(ValueError):
        proof.native_rows(model)


def test_publication_requires_the_unique_exact_writer_relation_and_keeps_other_namespaces_separate():
    selected = row()
    item = contract.item(selected)
    current = link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current, item)
    current.evidence.append(deepcopy(item))
    assert not contract.publication(current, item)
    for mode in ('channel-target-reader-access', 'maf-access', 'scalar-ram-leaf-withdrawal', 'register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
