"""Bind bounded dual-channel conversion to exact stock execution and owners."""
import copy

import pytest

from tools.kb.tests import closed_loop_conversion_contract as contract


def test_conversion_owner_contract():
    contract.owner_contract()


def test_conversion_preserves_every_previous_registered_region_and_fixture():
    contract.previous_regions_contract()


def test_registered_conversion_stock_contract(jk08a_stock_bytes):
    contract.registered_stock_contract(jk08a_stock_bytes)


def test_every_bound_conversion_byte_refuses_mutation(jk08a_stock_bytes):
    contract.all_bound_mutations_fail(jk08a_stock_bytes)


def test_conversion_published_counts_follow_registered_region():
    contract.publication_contract()


def test_conversion_literals_match_independent_exact_arithmetic():
    contract.literal_contract()


def test_conversion_five_formulas_match_both_channels_of_every_literal():
    contract.formula_contract()


@pytest.mark.parametrize('field', list(range(17,38)))
def test_conversion_rejects_changed_independent_observations(field):
    rows = contract.literals().copy()
    rows[0] = copy.deepcopy(rows[0])
    if isinstance(rows[0][field], list):
        rows[0][field][-1] ^= 1
    else:
        rows[0][field] ^= 1
    with pytest.raises(AssertionError):
        contract.literal_contract(rows)
