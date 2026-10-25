"""Exact joint owning appends retain native types, reverse relations and full function context."""
from copy import deepcopy
import json
from types import SimpleNamespace
import pytest
from kb import repo
from kb import request_limit_normalization_access_contract as contract


def rows():
    return contract.descriptor(repo.ROOT)['reference']


def link(document):
    return SimpleNamespace(owner=SimpleNamespace(key=document['owner']), to=SimpleNamespace(key=document['to']),
                           type=document['type'], slot=document['slot'], offset=document['offset'], roles=list(document['roles']),
                           props=deepcopy(document['props']), evidence=deepcopy(document['evidence']),
                           stated=list(document['stated']), sources=list(document['sources']))


def test_both_exact_appends_preserve_complete_native_and_reverse_fact_boundaries():
    selected = rows()
    assert {row['owner'] for row in selected} == {'cooperative-elk/tbl', 'glaring-chachalaca/tbl'}
    for row in selected:
        before, after = (json.loads(row[name+'_native_json']) for name in ('original', 'proposed'))
        stripped = deepcopy(after)
        target = next(value for value in stripped['link'] if (value['type'], value['to']) == ('reader', 'malachite-ferret/fn'))
        old = next(value for value in before['link'] if (value['type'], value['to']) == ('reader', 'malachite-ferret/fn'))
        assert target['evidence'].pop() == contract.item(row)
        if not target['evidence'] and 'evidence' not in old:
            target.pop('evidence')
        assert stripped == before and 'width' not in after and 'signed' not in after
        assert (after['unit'], after['scale']) == ('raw', 'x')
        assert row['original_ledger_json'] == row['proposed_ledger_json']
        claim = json.loads(row['proposed_claim_json'])
        assert claim['props']['relies']=='level' and claim['props']['supports']=='identity'
        assert not any(name.startswith('reverse_') for name in claim['props'])
        assert all(contract.item(row)['value'][name] is False for name in
                   ('scale_admission', 'units_admission', 'native_geometry_inference', 'reverse_function_identity_admission', 'natural_scheduling_inference', 'hardware_qualification'))
    functions = contract.descriptor(repo.ROOT)['retained_functions']
    assert {(value['owner'], value['address']) for value in functions} == {
        ('malachite-ferret/fn', 0x7AE80), ('aromatic-coua/fn', 0x7AF78)}


@pytest.mark.parametrize('fault', ('partial', 'duplicate', 'order', 'other-owner', 'other-target', 'scale-support', 'reverse-identity', 'forged-original'))
def test_normal_writer_requires_the_unique_complete_two_row_batch(fault):
    operations = [contract.operation(row) for row in rows()]
    assert contract.operations(deepcopy(operations), repo.ROOT)
    if fault == 'partial':
        operations.pop()
    elif fault == 'duplicate':
        operations.append(deepcopy(operations[0]))
    elif fault == 'order':
        operations.reverse()
    elif fault == 'other-owner':
        operations[0]['meaning'] = 'another/tbl'
    elif fault == 'other-target':
        operations[0]['to'] = 'aromatic-coua/fn'
    elif fault == 'scale-support':
        operations[0]['evidence'][0]['supports'] = 'scale'
    elif fault == 'reverse-identity':
        operations[0]['evidence'][0]['value']['reverse_function_identity_admission'] = True
    else:
        operations[0]['evidence'][0]['value']['original_claim_sha256'] = '0'*64
    with pytest.raises(ValueError):
        contract.operations(operations, repo.ROOT)


@pytest.mark.parametrize('fault', ('duplicate-evidence', 'wrong-direction', 'other-role', 'other-native-fact'))
def test_exact_qualified_relation_has_no_loose_publication_fallback(fault):
    row = rows()[0]
    item = contract.item(row)
    current = link(json.loads(row['proposed_claim_json']))
    assert contract.publication(current, item)
    if fault == 'duplicate-evidence':
        current.evidence.append(deepcopy(item))
    elif fault == 'wrong-direction':
        current.type = 'writer'
    elif fault == 'other-role':
        current.roles.append('arithmetic-factor')
    else:
        current.props['note'] = 'changed unrelated native context'
    assert not contract.publication(current, item)


def test_namespace_has_no_axis_scale_or_other_positive_or_absence_fallback():
    assert contract.registered(dict(mode=contract.MODE))
    for mode in ('endpoint-blend-access', 'conditional-endpoint-blend-access', 'channel-target-reader-access', 'request-boundary-publication-access', 'scalar-ram-leaf-withdrawal', 'register-only-withdrawal'):
        assert not contract.registered(dict(mode=mode))
    original = link(json.loads(rows()[0]['original_claim_json']))
    assert contract.looks_like_access(original)
    original.owner.key = 'proud-beetle/axis'
    assert not contract.looks_like_access(original)
