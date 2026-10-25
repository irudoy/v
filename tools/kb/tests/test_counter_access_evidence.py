"""Actual original counter array transfers bind joint owners and unchanged physical scopes."""

from copy import deepcopy
import json

import pytest

from kb import compile, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import counter_access_contract as contract, counter_access_evidence as proof
from kb import counter_access_resolution as resolution, repo, test_contract, test_evidence, write
from kb.model import Link


def representation(model, rows, *, qualified):
    result = deepcopy(model)
    owners = {meaning.key: meaning for meaning in result.meanings}
    for row in rows:
        links = [link for link in result.links if contract.original(row, link) or contract.qualified(row, link)]
        if len(links) != 1:
            raise ValueError('the actual counter array model lacks its one complete registered representation')
        index = result.links.index(links[0])
        claim = json.loads(row['proposed_claim_json'] if qualified else row['original_claim_json'])
        result.links[index] = Link(owners[claim['owner']], claim['type'], owners[claim['to']], claim['slot'], claim['offset'],
            deepcopy(claim['props']), deepcopy(claim['evidence']), set(claim['stated']), set(claim['sources']), set(claim['roles']))
    for meaning in result.meanings:
        meaning.links = [link for link in result.links if link.owner is meaning]
    return result


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        for component in proof.COMPONENTS:
            record['candidate']['witness'][component]
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original owning counter array proof')
        pytest.skip('the complete original owning counter array component is unavailable')
    rows = contract.descriptor(repo.ROOT)['reference']
    model = representation(compile.build(repo.ROOT), rows, qualified=False)
    result = proof.require_primary(model, record)
    return rows, model, record, result


def test_exact_owning_transfer_admission_uses_one_original_without_other_claims(original):
    rows, _, record, result = original
    assert result['original_claims'] == {row['id']: row['original_claim_sha256'] for row in rows}
    assert result['original_process_sha256'] == record['process_sha256']
    for key in ('units_admission', 'scale_admission', 'natural_scheduling_inference', 'hardware_qualification'):
        assert result[key] is False
    assert not hasattr(proof, 'RECEIPT')


@pytest.mark.parametrize('flag',('exact_counter_array_writes','exact_holdoff_byte'))
def test_owning_admission_requires_the_complete_array_and_exact_holdoff_domain(original,monkeypatch,flag):
    _,model,record,result=original
    changed=dict(result['components']['counter_array_paths']);changed[flag]=False
    monkeypatch.setattr(proof.COMPONENTS['counter_array_paths'],'require_primary',lambda *args:changed)
    with pytest.raises(ValueError):proof.require_primary(model,record)


@pytest.mark.parametrize('module', (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence))
def test_joint_exact_appends_preserve_existing_physical_namespaces_without_normalization(original, module):
    rows, before, _, _ = original
    after = representation(before, rows, qualified=True)
    assert module.scope_digest(before) == module.scope_digest(after)


def test_full_actual_transition_preserves_all_other_native_values_and_TEST_positions(original):
    from kb import test_origins
    rows, before, _, _ = original
    after = representation(before, rows, qualified=True)
    assert test_contract.exact({key: value.packet() for key, value in test_origins.index(before).items()},
                               {key: value.packet() for key, value in test_origins.index(after).items()})
    expected = resolution.publication_expected(before, after, write.publication_view(before))
    assert test_contract.exact(expected, write.publication_view(after))


@pytest.mark.parametrize('index', range(len(contract.IDENTITIES)))
def test_each_exact_attachment_supports_only_its_owning_identity(original, index):
    rows, before, _, _ = original
    after = representation(before, rows, qualified=True)
    row = rows[index]
    symbol = after.symbols[contract.symbol_key(row)]
    item = contract.item(row)
    assert proof.failure(item, before.symbols[symbol.key], before, 'identity') is not None
    assert proof.failure(item, symbol, after, 'identity') is None
    assert proof.failure(item, symbol, after, 'scale') is not None
    changed = deepcopy(item)
    changed['value']['direction'] = 'writer' if row['direction'] == 'reader' else 'reader'
    assert proof.failure(changed, symbol, after, 'identity') is not None


@pytest.mark.parametrize('component', proof.COMPONENTS)
def test_missing_actual_original_component_refuses(original, component):
    record = deepcopy(original[2])
    record['candidate']['witness'].pop(component)
    with pytest.raises(ValueError):
        proof.require_primary(original[1], record)


@pytest.mark.parametrize('owner,field,value', (('competent-scorpion/ram','width',8),
    ('prehistoric-polecat/ram','signed',False),('authentic-monkey/ram','width',8),
    ('affable-prawn/ram','signed',False),('silent-elephant/ram','width',16),
    ('aboriginal-dinosaur/ram','signed',False)))
def test_changed_actual_native_type_refuses(original, owner, field, value):
    model = deepcopy(original[1])
    symbol = next(member for member in model.symbols.values()
                  if member.meaning is not None and member.meaning.key == owner)
    symbol.props[field] = value
    with pytest.raises(ValueError):
        proof.require_primary(model, original[2])
