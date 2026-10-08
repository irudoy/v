"""Verify independent stock publication, grid selection and bounded learning."""
import copy

import pytest

from tools.kb.tests import closed_loop_publication_contract as contract


def test_stft_owner_contract():
    contract.owner_contract('stft')


def test_grid_selection_owner_contract():
    contract.owner_contract('selection')


def test_grid_learning_owner_contract():
    contract.owner_contract('learning')


def test_closed_loop_preserves_every_previous_registered_region_and_fixture():
    contract.previous_regions_contract()


@pytest.mark.parametrize('packet', ['stft', 'selection', 'learning'])
def test_registered_closed_loop_stock_contract(packet, jk08a_stock_bytes):
    contract.registered_stock_contract(packet, jk08a_stock_bytes)


@pytest.mark.parametrize('packet', ['stft', 'selection', 'learning'])
def test_every_bound_closed_loop_byte_refuses_mutation(packet, jk08a_stock_bytes):
    contract.all_bound_mutations_fail(packet, jk08a_stock_bytes)


@pytest.mark.parametrize('packet', ['stft', 'selection', 'learning'])
def test_closed_loop_publication_counts_follow_registered_regions(packet):
    contract.publication_contract(packet)


@pytest.mark.parametrize('packet', ['stft', 'selection', 'learning'])
def test_closed_loop_literal_arithmetic_and_observed_registers(packet):
    contract.literal_contract(packet)


@pytest.mark.parametrize('packet', ['stft', 'selection', 'learning'])
def test_closed_loop_formulas_match_independent_literals(packet):
    contract.formula_contract(packet)


@pytest.mark.parametrize('packet,index,field', [
    ('stft', 0, 4), ('stft', 0, 5), ('stft', 1, 4), ('stft', 1, 6),
    ('selection', 0, 11), ('selection', 1, 12), ('selection', 2, 14),
    ('selection', 2, 15), ('selection', 0, 16), ('selection', 1, 17),
    ('learning', 0, 13), ('learning', 2, 15), ('learning', 2, 16),
    ('learning', 0, 17), ('learning', 2, 18), ('learning', 0, 20),
    ('learning', 0, 21),
])
def test_closed_loop_rejects_changed_independent_observations(packet, index, field):
    rows = contract.literals(packet).copy()
    rows[index] = copy.deepcopy(rows[index])
    if isinstance(rows[index][field], list):
        rows[index][field][-1] ^= 1
    else:
        rows[index][field] ^= 1
    with pytest.raises(AssertionError):
        contract.literal_contract(packet, rows)
