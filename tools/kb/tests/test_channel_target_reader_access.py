"""Exact native owning append and cross-namespace/type refusal controls."""
from copy import deepcopy
import json
from types import SimpleNamespace
import pytest
from kb import repo
from kb import channel_target_reader_access_contract as contract


def row():
    return contract.descriptor(repo.ROOT)['reference'][0]


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']), to=SimpleNamespace(key=document['to']),
                           type=document['type'], slot=document['slot'], offset=document['offset'], roles=list(document['roles']),
                           props=deepcopy(document['props']), evidence=deepcopy(document['evidence']),
                           stated=list(document['stated']), sources=list(document['sources']))


def test_single_append_preserves_all_native_symbols_types_scale_relations_and_ledger():
    selected = row()
    before, after = (json.loads(selected[name + '_native_json']) for name in ('original', 'proposed'))
    stripped = deepcopy(after)
    companion = contract.descriptor(repo.ROOT)['companion']
    for attachment in (selected, companion):
        claim = json.loads(attachment['original_claim_json'])
        target = next(value for value in stripped['link'] if (value['type'], value['to']) == (claim['type'], claim['to']))
        original = next(value for value in before['link'] if (value['type'], value['to']) == (claim['type'], claim['to']))
        assert target['evidence'].pop() == contract.item(attachment)
        if not target['evidence'] and 'evidence' not in original:
            target.pop('evidence')
    assert stripped == before and after['width'] == 16 and 'signed' not in after
    assert after['unit'] == 'percent' and after['scale'] == 'x*34285/1114112'
    assert selected['original_ledger_json'] == selected['proposed_ledger_json']
    assert any(value['type'] == 'writer' and value['to'] == 'channel_throttle_target_builder/fn' for value in after['link'])
    retained = contract.descriptor(repo.ROOT)['retained_functions']
    assert [(value['owner'], value['address']) for value in retained] == [('throttle_target_scaler/fn', 0xCB1CA)]
    value = contract.item(selected)['value']
    assert (value['actual_read_site'], value['owner_selected_index'], value['actual_store_site']) == (0xCB1D4, 1, 0xCB1F6)
    for name in ('scale_admission', 'units_admission', 'native_geometry_inference', 'natural_scheduling_inference', 'hardware_qualification'):
        assert value[name] is False


@pytest.mark.parametrize('fault', ('duplicate', 'other-target', 'other-owner', 'scale-support', 'forged-original', 'partial-index-scope'))
def test_normal_link_writer_refuses_a_changed_or_partial_owning_append(fault):
    selected = row()
    operation = contract.operation(selected)
    companion = contract.companion_operation(repo.ROOT)
    assert contract.operations([deepcopy(operation), deepcopy(companion)], repo.ROOT)
    changed = deepcopy(operation)
    if fault == 'duplicate':
        operations = [changed, deepcopy(changed)]
    else:
        if fault == 'other-target':
            changed['to'] = 'channel_throttle_target_builder/fn'
        elif fault == 'other-owner':
            changed['meaning'] = 'throttle_target_channel_0/ram'
        elif fault == 'scale-support':
            changed['evidence'][0]['supports'] = 'scale'
        elif fault == 'forged-original':
            changed['evidence'][0]['value']['original_claim_sha256'] = '0' * 64
        else:
            changed['evidence'][0]['value'].pop('owner_selected_index')
        operations = [changed]
    with pytest.raises(ValueError):
        contract.operations([*operations, companion], repo.ROOT)


@pytest.mark.parametrize('fault', ('duplicate-evidence', 'wrong-direction', 'owner-zero', 'other-role', 'other-native-fact'))
def test_only_the_exact_owning_relation_has_publication_support(fault):
    selected = row()
    item = contract.item(selected)
    current = link(json.loads(selected['proposed_claim_json']))
    assert contract.publication(current, item)
    if fault == 'duplicate-evidence':
        current.evidence.append(deepcopy(item))
    elif fault == 'wrong-direction':
        current.type = 'writer'
    elif fault == 'owner-zero':
        current.evidence[0]['value']['owner_selected_index'] = 0
    elif fault == 'other-role':
        current.roles.append('arithmetic-factor')
    else:
        current.props['note'] = 'changed unrelated native note'
    assert not contract.publication(current, item)


def test_namespace_does_not_fall_back_to_other_positive_or_withdrawal_components():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('maf-access', 'request-boundary-publication-access', 'scalar-ram-leaf-withdrawal', 'register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    original = link(json.loads(row()['original_claim_json']))
    assert contract.looks_like_access(original)
    original.owner.key = 'unrelated/ram'
    assert not contract.looks_like_access(original)


@pytest.mark.parametrize('fault', ('missing-companion', 'duplicate-companion', 'altered-companion', 'own-only'))
def test_shared_owner_requires_the_one_finite_known_writer_operation(fault):
    own = contract.operation(row())
    companion = contract.companion_operation(repo.ROOT)
    operations = [own, companion]
    if fault in ('missing-companion', 'own-only'):
        operations.pop()
    elif fault == 'duplicate-companion':
        operations.append(deepcopy(companion))
    else:
        operations[1]['to'] = 'throttle_target_scaler/fn'
    with pytest.raises(ValueError):
        contract.operations(operations, repo.ROOT)
