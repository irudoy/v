"""Actual original bounded closed-loop coordinate transfers bind joint owners and unchanged physical scopes."""

from copy import deepcopy
import json

import pytest

from kb import compile, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import closed_loop_coordinate_access_contract as contract, closed_loop_coordinate_access_evidence as proof
from kb import closed_loop_coordinate_access_resolution as resolution, repo, test_contract, test_evidence, write
from kb.model import Link


def representation(model, rows, *, qualified):
    result = deepcopy(model)
    owners = {meaning.key: meaning for meaning in result.meanings}
    for row in rows:
        links = [link for link in result.links if contract.original(row, link) or contract.qualified(row, link)]
        if len(links) != 1:
            raise ValueError('the actual bounded closed-loop coordinate model lacks its one complete registered representation')
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
            pytest.fail('the common B acceptance requires the complete original owning bounded closed-loop coordinate proof')
        pytest.skip('the complete original owning bounded closed-loop coordinate component is unavailable')
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


@pytest.mark.parametrize('flag',('exact_feedback_arguments','exact_feedback_stores','exact_transition_counter_accesses'))
def test_owning_publication_requires_every_independent_feedback_admission_flag(original,monkeypatch,flag):
    _,model,record,result=original
    changed=dict(result['components']['closed_loop_feedback_paths']);changed[flag]=False
    monkeypatch.setattr(proof.feedback_consumer,'require_primary',lambda *args:changed)
    with pytest.raises(ValueError):proof.require_primary(model,record)


@pytest.mark.parametrize('flag',('exact_coolant_accesses','exact_selected_coefficient','exact_signed_offset'))
@pytest.mark.parametrize('value',(None,False,1))
def test_owning_publication_requires_every_exact_independent_coolant_domain_flag(original,monkeypatch,flag,value):
    _,model,record,result=original
    changed=dict(result['components']['closed_loop_coolant_paths']);changed[flag]=value
    monkeypatch.setattr(proof.coolant_consumer,'require_primary',lambda *args:changed)
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
    symbol.props[field] = not symbol.value('signed') if field=='signed' else 32 if symbol.value('width')==value else value
    with pytest.raises(ValueError):
        proof.require_primary(model, original[2])


@pytest.mark.parametrize('owner',('closed_loop_speed_gate/ram','placid-jackrabbit/ram'))
def test_parameter_source_reader_questions_and_all_their_original_evidence_remain_exact(original,owner):
    rows,before,_,_=original;after=representation(before,rows,qualified=True)
    old=next(symbol for symbol in before.symbols.values() if symbol.meaning is not None and symbol.meaning.key==owner)
    new=after.symbols[old.key]
    assert test_contract.exact(contract.plain(old.props),contract.plain(new.props))
    assert test_contract.exact(contract.plain(old.evidence),contract.plain(new.evidence))
    assert [contract.canonical(link) for link in before.links if link.owner is old.meaning]==[
        contract.canonical(link) for link in after.links if link.owner is new.meaning]


@pytest.mark.parametrize('direction',('reader','writer'))
@pytest.mark.parametrize('position',(0,1,2))
@pytest.mark.parametrize('fault',('omit','duplicate','key','path','kind','order'))
def test_transition_counter_original_TEST_pair_and_following_spec_positions_cannot_change(original,direction,position,fault):
    _,before,record,_=original;model=deepcopy(before)
    link=next(link for link in model.links if link.owner.key=='closed_loop_feedback_transition_counter_b2/ram'
        and link.type==direction and link.to.key=='closed_loop_feedback_transition/fn')
    item=link.evidence[position]
    if fault=='omit':link.evidence.pop(position)
    elif fault=='duplicate':link.evidence.insert(position,deepcopy(item))
    elif fault=='order':link.evidence.insert((position+1)%3,link.evidence.pop(position))
    else:item[fault]='altered'
    with pytest.raises(ValueError):proof.require_primary(model,record)


@pytest.mark.parametrize('owner',('fuel_coolant_coefficients/const','fuel_coolant_coordinate_offset/const'))
@pytest.mark.parametrize('position',(0,1,2))
@pytest.mark.parametrize('fault',('omit','duplicate','key','path','kind','order','type','props'))
def test_coolant_existing_reader_TEST_spec_class_and_context_cannot_change(original,owner,position,fault):
    _,before,record,_=original;model=deepcopy(before)
    link=next(link for link in model.links if link.owner.key==owner and link.to.key=='knowing-potoo/fn' and link.type=='reader')
    item=link.evidence[position]
    if fault=='omit':link.evidence.pop(position)
    elif fault=='duplicate':link.evidence.insert(position,deepcopy(item))
    elif fault=='order':link.evidence.insert((position+1)%3,link.evidence.pop(position))
    elif fault=='type':link.type='depends'
    elif fault=='props':link.props['supports']='scale'
    else:item[fault]='altered'
    with pytest.raises(ValueError):proof.require_primary(model,record)
