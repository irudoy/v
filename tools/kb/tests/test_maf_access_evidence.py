"""Actual original MAF transfers bind joint owners and unchanged physical scopes."""

from copy import deepcopy
import json

import pytest

from kb import compile, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import maf_access_contract as contract, maf_access_evidence as proof
from kb import maf_access_resolution as resolution, repo, test_contract, test_evidence, write
from kb.model import Link


def representation(model, rows, *, qualified):
    result = deepcopy(model)
    owners = {meaning.key: meaning for meaning in result.meanings}
    for row in rows:
        links = [link for link in result.links if contract.original(row, link) or contract.qualified(row, link)]
        if len(links) != 1:
            raise ValueError('the actual MAF model lacks its one complete registered representation')
        index = result.links.index(links[0])
        if contract.correction(row):
            for link in list(result.links):
                if contract.correct_original(row,link):result.links.remove(link)
            index=result.links.index(links[0])
        claim = json.loads(row['proposed_claim_json'] if qualified else row['original_claim_json'])
        result.links[index] = Link(owners[claim['owner']], claim['type'], owners[claim['to']], claim['slot'], claim['offset'],
            deepcopy(claim['props']), deepcopy(claim['evidence']), set(claim['stated']), set(claim['sources']), set(claim['roles']))
        if contract.correction(row) and not qualified:
            correct=contract.base_claim(row)
            result.links.append(Link(owners[correct['owner']],correct['type'],owners[correct['to']],correct['slot'],correct['offset'],
                deepcopy(correct['props']),deepcopy(correct['evidence']),set(correct['stated']),set(correct['sources']),set(correct['roles'])))
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
            pytest.fail('the common B acceptance requires the complete original owning MAF proof')
        pytest.skip('the complete original owning MAF component is unavailable')
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


@pytest.mark.parametrize('owner,field,value', (('imposing-auk/ram', 'signed', False),
    ('imposing-auk/ram', 'width', 16), ('maf_correction_state_b2/ram', 'signed', False),
    ('maf_fallback_latch_b2/ram', 'width', 16), ('camouflaged-cockle/ram','width',16),
    ('camouflaged-cockle/ram','signed',False),('maf_b1/ram','width',8),
    ('maf_b1/ram','signed',True),('maf_b2/ram','width',32),('maf_b2/ram','signed',True),
    ('ivory-gecko/tbl','width',16),('ivory-gecko/tbl','signed',False),
    ('wealthy-woodlouse/tbl','width',16),('wealthy-woodlouse/tbl','signed',False),
    ('tourmaline-jackal/ram','width',8),('tourmaline-jackal/ram','width',24),
    ('tourmaline-jackal/ram','signed',False),('satisfied-oarfish/ram','width',8),
    ('satisfied-oarfish/ram','signed',True)))
def test_changed_actual_native_type_refuses(original, owner, field, value):
    model = deepcopy(original[1])
    symbol = next(member for member in model.symbols.values()
                  if member.meaning is not None and member.meaning.key == owner)
    symbol.props[field] = value
    with pytest.raises(ValueError):
        proof.require_primary(model, original[2])


def test_accumulator_extends_the_existing_MAF_owner_with_exactly_two_proofs():
    rows=contract.descriptor(repo.ROOT)['reference']
    selected=[r for r in rows if r['owner']=='unselfish-okapi/ram']
    assert [r['id'] for r in selected]==['compensation-unselfish-okapi-reader','accumulator-unselfish-okapi-writer']
    assert len(rows)==len(contract.IDENTITIES)==35 and len(proof.COMPONENTS)==5
    assert len({r['proposed_native_sha256'] for r in selected})==1
    original=json.loads(selected[0]['original_native_json']);proposed=json.loads(selected[0]['proposed_native_json'])
    expected=deepcopy(original)
    for row in selected:
        claim=json.loads(row['original_claim_json'])
        link,=[value for value in expected['link'] if value['type']==claim['type'] and value['to']==claim['to']]
        link.setdefault('evidence',[]).append(contract.item(row))
        assert json.loads(row['original_claim_json'])['props']==dict(layouts=['7mfk'],reverse_relies='structure',reverse_supports='identity')
        assert row['declared_width']==32 and row['declared_signed'] is False
    assert expected==proposed
    assert selected[1]['sites']==[0x3AD8A,0x3AE1A,0x3AE74]
    assert selected[1]['component']=='maf_accumulator_update_paths'


@pytest.mark.parametrize('field,value',(('width',16),('signed',True)))
def test_accumulator_native_type_changes_refuse(original,field,value):
    model=deepcopy(original[1]);row=next(r for r in original[0] if r['id']=='accumulator-unselfish-okapi-writer')
    model.symbols[contract.symbol_key(row)].props[field]=value
    with pytest.raises(ValueError):proof.native_rows(model)


def test_MAF_publication_counts_bind_the_executed_owning_descriptor():
    import re
    rows=contract.descriptor(repo.ROOT)['reference']
    text=(repo.ROOT/'defs/JK08A.maf-extended.md').read_text()
    assert int(re.search(r'contains all (\d+) exact original claims',text)[1])==len(rows)==35
    assert int(re.search(r'requires(\d+) exact ordinary',text)[1])==len(rows)
    assert int(re.search(r'batch contains\s*(\d+) complete owner documents',text)[1])==len({row['owner'] for row in rows})==21
    assert sum(contract.correction(row) for row in rows)==2
