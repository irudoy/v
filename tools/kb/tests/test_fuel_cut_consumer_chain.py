"""Mandatory exact-stock and arithmetic fuel-cut consumer contracts."""
import copy
import pytest
from tools.kb.tests import fuel_cut_consumer_contract as contract

def test_fuel_cut_consumer_owner_contract(): contract.owner_contract()
def test_fuel_cut_consumer_registered_stock_contract(jk08a_stock_bytes): contract.registered_stock_contract(jk08a_stock_bytes)
def test_fuel_cut_consumer_preserves_all_regions_and_fixtures(): contract.all_regions_contract()
def test_fuel_cut_consumer_literal_headers_match_independent_models(): contract.literal_contract()
def test_fuel_cut_consumer_all_counter_and_event_equations(): contract.equation_contract()
def test_fuel_cut_consumer_published_counts_and_boundaries(): contract.publication_contract()

@pytest.mark.parametrize('number,before,after',[
    ('23','M&(uint8(from)|RAM8[ffff1935])','(1<<I)&(uint8(from)|RAM8[ffff1935])'),
    ('23','to = uint16(prev+E*S*A)','to = min(65535,prev+E*S*A)'),
    ('25','D-J*RAM16[ffff23aa]','D'),
    ('25','+1000*C','+999*C'),
    ('24','(uint8(prev)&(255^M))','uint8(prev)'),
    ('24','min(1,RAM8[ffff22e0])','(RAM8[ffff22e0]&1)'),
    ('24','to = H|(K*M)','to = H'),
    ('24','K = E*min(1,M&63)','K = min(1,M&63)')])
def test_fuel_cut_consumer_rejects_changed_semantics(number,before,after):
    formulas=copy.deepcopy(contract.contracts()['formulas'])
    assert before in formulas[number]
    formulas[number]=formulas[number].replace(before,after)
    with pytest.raises(AssertionError): contract.equation_contract(formulas=formulas)

def test_fuel_cut_consumer_multi_bit_mask_selects_other_selected_channel():
    row=contract.equations.oneshot.case(1,argument=3,inhibit=2,history=0,opening=7,
        started=0,diagnostic=0,durations=[100]*6,counters=[0]*6)
    values=contract.equations.counter_values(row,0,'23')
    output=contract.equations.evaluate(contract.equations.FORMULAS['23'],**values)['to']
    assert output==row['output'][0]==21

def test_fuel_cut_consumer_history_updates_with_disabled_outputs():
    row=contract.equations.event.case(0,pending=3,enable=0,release=255,history=255,inhibit=2)
    output=contract.equations.evaluate(contract.equations.FORMULAS['24'],**contract.equations.event_values(row))
    assert (output['to'],output['R'])==(255,254)

def test_fuel_cut_consumer_high_only_mask_has_no_oneshot_history_store():
    row=contract.equations.event.case(0,pending=128,enable=128,release=0,history=255,inhibit=128)
    output=contract.equations.evaluate(contract.equations.FORMULAS['24'],**contract.equations.event_values(row))
    assert (output['to'],output['R'])==(127,0)
