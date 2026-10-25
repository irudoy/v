"""Actual original bounded RPM contributor transfers bind joint owners and unchanged physical scopes."""

from copy import deepcopy
import json

import pytest

from kb import compile, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import rpm_inhibit_access_contract as contract, rpm_inhibit_access_evidence as proof
from kb import rpm_inhibit_access_resolution as resolution, repo, test_contract, test_evidence, write
from kb.model import Link


def representation(model, rows, *, qualified):
    result = deepcopy(model)
    owners = {meaning.key: meaning for meaning in result.meanings}
    for row in rows:
        links = [link for link in result.links if contract.original(row, link) or contract.qualified(row, link)]
        if len(links) != 1:
            raise ValueError('the actual bounded RPM contributor model lacks its one complete registered representation')
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
            pytest.fail('the common B acceptance requires the complete original owning bounded RPM contributor proof')
        pytest.skip('the complete original owning bounded RPM contributor component is unavailable')
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


@pytest.mark.parametrize('flag',('exact_bounded_rpm_inhibit_accesses','exact_summary_bit_accesses',
    'exact_composite_status_accesses'))
def test_owning_admission_requires_every_independent_domain_flag(original,monkeypatch,flag):
    _,model,record,result=original
    changed=dict(result['components']['rpm_inhibit_paths']);changed[flag]=False
    monkeypatch.setattr(proof.capture_consumer,'require_primary',lambda *args:changed)
    with pytest.raises(ValueError):proof.require_primary(model,record)


def test_owning_admission_requires_the_separate_conditional_remaining_RPM_component(original,monkeypatch):
    _,model,record,result=original
    changed=dict(result['components']['rpm_remaining_inhibit_paths']);changed['exact_remaining_rpm_accesses']=False
    monkeypatch.setattr(proof.remaining_consumer,'require_primary',lambda *args:changed)
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


@pytest.mark.parametrize('owner',sorted({row[2] for row in contract.IDENTITIES}))
@pytest.mark.parametrize('field,value',(('width',16),('signed',True)))
def test_changed_actual_native_type_refuses(original, owner, field, value):
    model = deepcopy(original[1])
    symbol = next(member for member in model.symbols.values()
                  if member.meaning is not None and member.meaning.key == owner)
    symbol.props[field] = not symbol.value('signed') if field=='signed' else value
    with pytest.raises(ValueError):
        proof.require_primary(model, original[2])


@pytest.mark.parametrize('owner',('rev_limit_fuel_cut/tbl','stirring-mayfly/ram',
    'resourceful-scorpion/ram','obedient-stoat/ram','accomplished-chicken/ram',
    'resolute-bullfinch/ram','agate-kingfisher/ram','gifted-jackrabbit/tbl',
    'ochre-jacamar/ram','blue-oyster/ram','heavenly-whippet/ram'))
@pytest.mark.parametrize('field,value',(('width',8),('signed',False)))
def test_physical_word_or_byte_read_does_not_fill_an_unset_semantic_type(original,owner,field,value):
    model=deepcopy(original[1])
    symbol=next(member for member in model.symbols.values()
        if member.meaning is not None and member.meaning.key==owner)
    assert symbol.value(field) is None
    symbol.props[field]=value
    with pytest.raises(ValueError):proof.require_primary(model,original[2])


def test_CAN_flag_declared_byte_does_not_supply_an_unset_semantic_signedness(original):
    model=deepcopy(original[1])
    symbol=next(member for member in model.symbols.values()
        if member.meaning is not None and member.meaning.key=='jovial-buzzard/ram')
    assert symbol.value('width')==8 and symbol.value('signed') is None
    symbol.props['signed']=False
    with pytest.raises(ValueError):proof.require_primary(model,original[2])
