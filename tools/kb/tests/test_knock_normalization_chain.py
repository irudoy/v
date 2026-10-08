"""Verify bounded software normalization and parallel sample/cache publication."""
from tools.kb.tests import knock_software_contract as contract
import copy
import pytest
def test_knock_normalization_chain_owner_contract():contract.owner_contract('normalization')
def test_knock_normalization_registered_stock_contract(jk08a_stock_bytes):
    contract.registered_stock_contract('normalization',jk08a_stock_bytes)
def test_knock_normalization_every_bound_byte_refuses_mutation(jk08a_stock_bytes):
    contract.all_bound_mutations_fail('normalization',jk08a_stock_bytes)
def test_knock_normalization_publication_counts_follow_the_registered_region():
    contract.publication_contract('normalization')
def test_knock_normalization_literals_bind_registers_full_sr_and_saved_stack():
    contract.normalization_literal_contract()
def test_knock_normalization_formula_matches_all_eight_outputs():
    contract.formula_contract('normalization')
@pytest.mark.parametrize('field',range(9,16))
def test_knock_normalization_rejects_changed_independent_observations(field):
    rows=contract.literals('normalization').copy();rows[0]=copy.deepcopy(rows[0])
    if isinstance(rows[0][field],list):rows[0][field][-1]^=1
    else:rows[0][field]^=1
    with pytest.raises(AssertionError):contract.normalization_literal_contract(rows)
