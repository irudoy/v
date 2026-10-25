"""Actual originals govern each family and unchanged physical namespaces."""

from copy import deepcopy
import json
import pytest

from kb import compile, copy_evidence, repo, test_evidence
from kb import injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import calculation_dependency_contract as contract
from kb import calculation_dependency_evidence as proof
from kb.model import Link


@pytest.fixture(scope='module')
def original():
    rows = contract.rows(repo.ROOT)
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        for row in rows:
            record['candidate']['witness'][row['component']]
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires all exact calculation originals')
        pytest.skip('the complete original calculation components are unavailable')
    model = compile.build(repo.ROOT)
    result = proof.require_primary(model, record)
    return rows, model, record, result


def test_all_dispositions_use_the_same_original_and_only_AAFA_has_owned_scale(original):
    rows, _, record, result = original
    assert set(result['original_claims']) == {row['operation_id'] for row in rows}
    assert set(result['components']) == {row['component'] for row in rows}
    assert set(result['owned_scales']) == {'natural-hedgehog/tbl'}
    assert result['owned_scales']['natural-hedgehog/tbl']['owned_factor_scale_admission'] is True
    assert result['original_process_sha256'] == record['process_sha256']
    assert result['physical_reader_inference'] is result['general_scale_admission'] is False
    assert not hasattr(proof, 'RECEIPT')


@pytest.mark.parametrize('family', tuple(row[0] for row in contract.FAMILIES))
def test_a_missing_actual_original_component_refuses_its_family(original, family):
    rows, model, record, _ = original
    row = next(row for row in rows if row['family'] == family)
    changed = deepcopy(record)
    changed['candidate']['witness'].pop(row['component'])
    with pytest.raises((ValueError, KeyError)):
        proof.require_primary(model, changed, family=family)


@pytest.mark.parametrize('module', (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence))
def test_all_exact_replacements_preserve_original_namespaces_without_new_normalization(original, module):
    rows, model, _, _ = original
    baseline = module.scope_digest(model)
    meanings = {meaning.key: meaning for meaning in model.meanings}
    saved = list(model.links)
    owner_links = [(meaning, list(meaning.links)) for meaning in model.meanings]
    try:
        for dependency in (False, True):
            for row in rows:
                index = next(index for index, link in enumerate(model.links)
                             if contract.original(row, link) or contract.dependency(row, link))
                claim = json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
                model.links[index] = Link(meanings[claim['owner']], claim['type'], meanings[claim['to']],
                    claim['slot'], claim['offset'], deepcopy(claim['props']), [contract.item(row)] if dependency else [],
                    set(claim['stated']), set(claim['sources']), set(claim['roles']))
            for meaning, _ in owner_links:
                meaning.links = [link for link in model.links if link.owner is meaning]
            assert module.scope_digest(model) == baseline
    finally:
        model.links[:] = saved
        for meaning, links in owner_links:
            meaning.links = links


def test_sample_disposition_preserves_every_original_TEST_origin_packet(original):
    from kb import test_origins
    rows,model,_,_=original
    row=next(row for row in rows if row['family']=='closed-loop-sample')
    meanings={meaning.key:meaning for meaning in model.meanings}
    baseline={key:origin.packet() for key,origin in test_origins.index(model).items()}
    saved=list(model.links);owner=meanings[row['owner']];saved_owner=list(owner.links)
    try:
        index=next(index for index,link in enumerate(model.links)
            if contract.original(row,link) or contract.dependency(row,link))
        for dependency in (False,True):
            claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
            model.links[index]=Link(owner,claim['type'],meanings[claim['to']],claim['slot'],claim['offset'],
                deepcopy(claim['props']),[contract.item(row)] if dependency else [],
                set(claim['stated']),set(claim['sources']),set(claim['roles']))
            owner.links=[link for link in model.links if link.owner is owner]
            assert {key:origin.packet() for key,origin in test_origins.index(model).items()}==baseline
    finally:
        model.links[:]=saved;owner.links=saved_owner


def test_CVTC_output_preserves_every_original_TEST_origin_packet(original):
    from kb import test_origins
    rows,model,_,_=original;row=next(row for row in rows if row['family']=='cvtc-gain')
    meanings={meaning.key:meaning for meaning in model.meanings}
    baseline={key:origin.packet() for key,origin in test_origins.index(model).items()}
    saved=list(model.links);owner=meanings[row['owner']];saved_owner=list(owner.links)
    try:
        index=next(index for index,link in enumerate(model.links)
            if contract.original(row,link) or contract.dependency(row,link))
        for dependency in (False,True):
            claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
            model.links[index]=Link(owner,claim['type'],meanings[claim['to']],claim['slot'],claim['offset'],
                deepcopy(claim['props']),[contract.item(row)] if dependency else [],
                set(claim['stated']),set(claim['sources']),set(claim['roles']))
            owner.links=[link for link in model.links if link.owner is owner]
            assert {key:origin.packet() for key,origin in test_origins.index(model).items()}==baseline
    finally:
        model.links[:]=saved;owner.links=saved_owner


@pytest.mark.parametrize('flag',(None,False,1))
def test_sample_family_requires_its_actual_fixed_other_output_admission(original,monkeypatch,flag):
    from kb import closed_loop_coordinate_capture_evidence as coordinate
    _,model,record,result=original
    component=deepcopy(result['components']['closed_loop_coordinate_paths'])
    component['exact_sample_argument']=flag
    monkeypatch.setattr(coordinate,'require_witness',lambda *args,**kwargs:deepcopy(component))
    with pytest.raises(ValueError):proof.require_primary(model,record,family='closed-loop-sample')


@pytest.mark.parametrize('flag',(None,False,1))
def test_feedback_arguments_require_their_actual_post_delay_and_fixed_other_admission(original,monkeypatch,flag):
    from kb import closed_loop_feedback_capture_evidence as feedback
    _,model,record,result=original
    component=deepcopy(result['components']['closed_loop_feedback_paths']);component['exact_feedback_arguments']=flag
    monkeypatch.setattr(feedback,'require_witness',lambda *args,**kwargs:deepcopy(component))
    with pytest.raises(ValueError):proof.require_primary(model,record,family='closed-loop-feedback')


def test_feedback_dispositions_preserve_every_original_TEST_origin_packet(original):
    from kb import test_origins
    rows,model,_,_=original;selected=[row for row in rows if row['family']=='closed-loop-feedback']
    meanings={meaning.key:meaning for meaning in model.meanings}
    baseline={key:origin.packet() for key,origin in test_origins.index(model).items()}
    saved=list(model.links);owner_links=[(meanings[row['owner']],list(meanings[row['owner']].links)) for row in selected]
    try:
        for dependency in (False,True):
            for row in selected:
                owner=meanings[row['owner']]
                index=next(index for index,link in enumerate(model.links) if contract.original(row,link) or contract.dependency(row,link))
                claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
                model.links[index]=Link(owner,claim['type'],meanings[claim['to']],claim['slot'],claim['offset'],
                    deepcopy(claim['props']),[contract.item(row)] if dependency else [],set(claim['stated']),
                    set(claim['sources']),set(claim['roles']))
            for owner,_ in owner_links:owner.links=[link for link in model.links if link.owner is owner]
            assert {key:origin.packet() for key,origin in test_origins.index(model).items()}==baseline
    finally:
        model.links[:]=saved
        for owner,links in owner_links:owner.links=links


@pytest.mark.parametrize('owner',('fuzzy-mouse/ram','raspberry-dragon/ram','rpm/ram'))
@pytest.mark.parametrize('field',('width','signed'))
def test_feedback_arguments_preserve_unset_types_and_the_existing_unsigned_RPM_word(original,owner,field):
    model=deepcopy(original[1]);symbol=next(symbol for symbol in model.symbols.values()
        if symbol.meaning is not None and symbol.meaning.key==owner)
    symbol.props[field]=8 if field=='width' else not symbol.value('signed')
    with pytest.raises(ValueError):proof.native_rows(model)
