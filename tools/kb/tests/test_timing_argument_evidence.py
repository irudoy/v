"""Actual same-primary argument proof and unchanged physical namespaces."""

from copy import deepcopy
import json
import pytest
from kb import compile,copy_evidence,repo,test_evidence
from kb import injection_copy_evidence,coherent_copy_evidence,sid22_evidence
from kb import timing_argument_contract as contract,timing_argument_evidence as proof
from kb.model import Link


@pytest.fixture(scope='module')
def original():
    try:
        record=json.loads(copy_evidence._read(repo.ROOT,copy_evidence.RECEIPT))
        for key in ('timing_division_paths','timing_tail_paths','division_callees_paths'):record['candidate']['witness'][key]
    except (FileNotFoundError,KeyError):
        if test_evidence.REQUIRE_CONTEXTS:pytest.fail('the common B acceptance requires its complete timing argument original')
        pytest.skip('the original complete timing argument components are unavailable')
    model=compile.build(repo.ROOT)
    result=proof.require_primary(model,record)
    return model,record,result


def test_argument_admission_requires_all_complete_original_components(original):
    result=original[2]
    assert set(result['components'])=={'timing_division_paths','timing_tail_paths','division_callees_paths'}
    assert result['bounded_argument_lineage'] is True
    for key in ('physical_reader_inference','scale_admission','natural_scheduling_inference','hardware_qualification'):
        assert result[key] is False
    assert not hasattr(proof,'RECEIPT')


@pytest.mark.parametrize('component',('timing_division_paths','timing_tail_paths','division_callees_paths'))
def test_argument_proof_cannot_replace_any_original_component(original,component):
    model,record,_=original
    changed=deepcopy(record);changed['candidate']['witness'].pop(component)
    with pytest.raises((ValueError,KeyError)):proof.require_primary(model,changed)


@pytest.mark.parametrize('module',(copy_evidence,injection_copy_evidence,coherent_copy_evidence,sid22_evidence))
def test_exact_argument_representations_preserve_existing_namespace_without_normalization(original,module):
    model=original[0];baseline=module.scope_digest(model)
    meanings={meaning.key:meaning for meaning in model.meanings}
    saved=list(model.links)
    try:
        for dependency in (False,True):
            for row in contract.descriptor(model.root)['reference']:
                index=next(index for index,link in enumerate(model.links)
                    if contract.original(row,link) or contract.dependency(row,link))
                claim=json.loads(row['proposed_claim_json'] if dependency else row['original_claim_json'])
                model.links[index]=Link(meanings[claim['owner']],claim['type'],meanings[claim['to']],
                    claim['slot'],claim['offset'],deepcopy(claim['props']),[contract.item(row)] if dependency else [],
                    set(claim['stated']),set(claim['sources']),set(claim['roles']))
            assert module.scope_digest(model)==baseline
    finally:model.links[:]=saved
