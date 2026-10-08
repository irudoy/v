"""Bind both signed adjustment views to the complete natural stock entry."""
import copy

import pytest

from tools.kb.tests import closed_loop_adjustment_contract as contract

def test_adjustment_owner_contract():
    contract.owner_contract()

def test_adjustment_preserves_every_previous_registered_region_and_fixture():
    contract.previous_regions_contract()

def test_registered_adjustment_stock_contract(jk08a_stock_bytes):
    contract.registered_stock_contract(jk08a_stock_bytes)

def test_every_bound_adjustment_byte_refuses_mutation(jk08a_stock_bytes):
    contract.all_bound_mutations_fail(jk08a_stock_bytes)

def test_adjustment_published_counts_follow_registered_region():
    contract.publication_contract()

def test_adjustment_literals_match_independent_raw_state_cpu_and_frame():
    contract.literal_contract()

def test_adjustment_two_formulas_match_both_channels_of_every_literal():
    contract.formula_contract()

@pytest.mark.parametrize('field',list(range(9,17)))
def test_adjustment_rejects_changed_independent_observations(field):
    rows = contract.literals().copy()
    rows[0] = copy.deepcopy(rows[0])
    rows[0][field][-1] ^= 1
    with pytest.raises(AssertionError):
        contract.literal_contract(rows)
