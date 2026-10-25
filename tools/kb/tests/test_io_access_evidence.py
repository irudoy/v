"""Owning I/O proof requires its actual original and unchanged namespaces."""

from copy import deepcopy
import json

import pytest

from kb import compile, copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence
from kb import io_access_claim_contract as contract, io_access_evidence as proof
from kb import io_access_resolution as resolution, match, repo, test_contract, test_evidence
from kb.model import Link, SymbolKey


@pytest.fixture(scope='module')
def original():
    try:
        record = json.loads(copy_evidence._read(repo.ROOT, copy_evidence.RECEIPT))
        record['candidate']['witness']['io_access_paths']
    except (FileNotFoundError, KeyError):
        if test_evidence.REQUIRE_CONTEXTS:
            pytest.fail('the common B acceptance requires the complete original owning I/O proof')
        pytest.skip('the complete original owning I/O component is unavailable')
    rows = contract.descriptor(repo.ROOT)['reference']
    model = representation(compile.build(repo.ROOT), rows, proposed=False)
    result = proof.require_primary(model, record)
    return rows, model, record, result


def representation(model, rows, *, proposed):
    after = deepcopy(model)
    owners = {meaning.key: meaning for meaning in after.meanings}
    for row in rows:
        matches = [link for link in after.links if contract.original(row, link) or contract.qualified(row, link)]
        if len(matches) > 1 or not matches and row['disposition'] != 'relocate-site-evidence':
            raise ValueError('the actual I/O test model has no unique registered representation')
        claim = json.loads(row['proposed_claim_json'] if proposed else row['original_claim_json'])
        index = after.links.index(matches[0]) if matches else len(after.links)
        if matches:
            del after.links[index]
        if claim is not None:
            after.links.insert(index, Link(owners[claim['owner']], claim['type'], owners[claim['to']], claim['slot'], claim['offset'],
                deepcopy(claim['props']), deepcopy(claim['evidence']), set(claim['stated']), set(claim['sources']), set(claim['roles'])))
        symbol = after.symbols[contract.symbol_key(row)]
        before_evidence, after_evidence = (json.loads(row[key]) for key in
            ('original_symbol_evidence_json', 'proposed_symbol_evidence_json'))
        if not (test_contract.exact(symbol.evidence, before_evidence) or test_contract.exact(symbol.evidence, after_evidence)):
            raise ValueError('the actual I/O test model changes a retained evidence position')
        symbol.evidence = after_evidence if proposed else before_evidence
    for meaning in after.meanings:
        meaning.links = [link for link in after.links if link.owner is meaning]
    return after


def proposed(model, rows):
    return representation(model, rows, proposed=True)


def test_one_complete_original_supplies_three_bounded_identities_without_other_admission(original):
    rows, model, record, result = original
    assert result['original_claims'] == {row['id']: row['original_claim_sha256'] for row in rows}
    assert result['original_process_sha256'] == record['process_sha256']
    assert SymbolKey('7mfk', 'fn', 0x2040) not in model.symbols
    for key in ('universal_no_read_claim', 'native_function_publication', 'physical_units_inference',
                'scale_admission', 'natural_scheduling_inference', 'peripheral_side_effects_admission', 'hardware_qualification'):
        assert result[key] is False
    assert not hasattr(proof, 'RECEIPT')


@pytest.mark.parametrize('module', (copy_evidence, injection_copy_evidence, coherent_copy_evidence, sid22_evidence))
def test_all_three_exact_native_changes_preserve_existing_physical_namespaces_without_normalization(original, module):
    rows, model, _, _ = original
    after = proposed(model, rows)
    assert module.scope_digest(model) == module.scope_digest(after)


def test_full_transition_keeps_actual_TEST_origins_and_native_publication_view(original):
    from kb import write
    rows, model, _, _ = original
    after = proposed(model, rows)
    resolutions = {row['id']: row['original_claim_sha256'] for row in rows}
    expected = resolution.publication_expected(model, after, resolutions,
        write.publication_view(model), write.publication_view(after))
    assert test_contract.exact(expected, write.publication_view(after))


@pytest.mark.parametrize('index', (0, 1, 2))
def test_original_relation_cannot_stand_in_for_qualified_owning_attachment(original, index):
    rows, model, _, _ = original
    row = rows[index]
    item = contract.item(row)
    symbol = model.symbols[contract.symbol_key(row)]
    assert proof.failure(item, symbol, model, 'identity') is not None
    assert match.rank(item, symbol, model, 'identity') == -1


@pytest.mark.parametrize('index', (0, 1, 2))
def test_proof_cannot_supply_scale_or_another_symbol(original, index):
    rows, model, _, _ = original
    after = proposed(model, rows)
    row = rows[index]
    item = contract.item(row)
    own = after.symbols[contract.symbol_key(row)]
    other = after.symbols[contract.symbol_key(rows[(index + 1) % len(rows)])]
    assert proof.failure(item, own, after, 'identity') is None
    assert proof.failure(item, own, after, 'scale') is not None
    assert proof.failure(item, other, after, 'identity') is not None


def test_missing_actual_original_component_refuses(original):
    record = deepcopy(original[2])
    record['candidate']['witness'].pop('io_access_paths')
    with pytest.raises((ValueError, KeyError)):
        proof.require_primary(original[1], record)
