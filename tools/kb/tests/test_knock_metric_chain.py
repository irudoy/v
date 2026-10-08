"""Verify bounded post-acquisition differences, signed scaling and raw publication."""
from tools.kb.tests import knock_software_contract as contract
import copy
import pytest
def test_knock_metric_chain_owner_contract():contract.owner_contract('metric')
def test_knock_metric_registered_stock_contract(jk08a_stock_bytes):
    contract.registered_stock_contract('metric',jk08a_stock_bytes)
def test_knock_metric_every_bound_byte_refuses_mutation(jk08a_stock_bytes):
    contract.all_bound_mutations_fail('metric',jk08a_stock_bytes)
def test_knock_metric_publication_counts_follow_the_registered_region():
    contract.publication_contract('metric')
def test_knock_metric_literals_bind_full_registers_and_saturation_neighbors():
    contract.metric_literal_contract()
def test_knock_metric_formulas_match_every_independent_literal():
    contract.formula_contract('metric')
@pytest.mark.parametrize('index,field',[(0,8),(0,9),(0,10),(0,11),(0,12),(0,13),(0,14),
    (6488,9),(6488,10),(6488,13),(6488,14),(7460,11),(7460,12),(7460,13),(7460,14)])
def test_knock_metric_rejects_changed_independent_observations(index,field):
    rows=contract.literals('metric').copy();rows[index]=copy.deepcopy(rows[index])
    if isinstance(rows[index][field],list):rows[index][field][-1]^=1
    else:rows[index][field]^=1
    with pytest.raises(AssertionError):contract.metric_literal_contract(rows)
