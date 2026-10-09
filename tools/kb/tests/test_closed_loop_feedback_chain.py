"""Mandatory owner, exact-stock and numerical whole-feedback contracts."""
import copy
import pytest
from tools.kb.tests import closed_loop_feedback_contract as contract

def test_feedback_owner_contract(): contract.owner_contract()
def test_registered_feedback_stock_contract(jk08a_stock_bytes): contract.registered_stock_contract(jk08a_stock_bytes)
def test_feedback_preserves_all_previous_regions_and_fixtures(): contract.previous_regions_contract()
def test_feedback_every_bound_byte_refuses_mutation(jk08a_stock_bytes): contract.all_bound_mutations_fail(jk08a_stock_bytes)
def test_feedback_published_counts_and_boundaries(): contract.publication_contract()
def test_feedback_complete_memory_cpu_and_frame_literals(): contract.literal_contract()
def test_feedback_transition_sensitive_formula_matches_both_banks(): contract.formula_contract()

@pytest.mark.parametrize('field',[0,1,2])
def test_feedback_rejects_changed_terminal_or_frame_literal(field):
    rows=copy.deepcopy(contract.literals()[1]);row=rows[1097]
    if field==1: row[field]^=1
    else: row[field][162 if field==2 else 0]^=1
    with pytest.raises(AssertionError): contract.literal_contract(cpu_rows=rows)

@pytest.mark.parametrize('index',[0,17,1097,1463])
def test_feedback_rejects_changed_shared_memory_literal(index):
    rows=copy.deepcopy(contract.literals()[0]);rows[index][5][-1]^=1
    with pytest.raises(AssertionError): contract.literal_contract(rows=rows)

@pytest.mark.parametrize('before,after',[
    ('K-C','C-K'),('abs(F-1)','abs(F-2)'),('D-V','V-D'),('V-U','U-V'),
    ('(RAM8[0xffff88ec]>>4)&1','(RAM8[0xffff88ec]>>5)&1'),
    ('max(ROM16[0x00008fc4],min(ROM16[0x00008fc6],W))','min(ROM16[0x00008fc4],max(ROM16[0x00008fc6],W))')])
def test_feedback_rejects_changed_transition_or_selection_equation(before,after):
    formula=contract.contracts()['formula'];assert before in formula
    with pytest.raises(AssertionError): contract.formula_contract(formula=formula.replace(before,after))
