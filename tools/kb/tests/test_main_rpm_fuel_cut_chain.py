"""Exact-stock and complete raw-domain main-RPM fuel-cut contracts."""
import copy
import pytest
from tools.kb.tests import main_rpm_fuel_cut_contract as contract


def test_main_rpm_fuel_cut_owner_contract(): contract.owner_contract()
def test_main_rpm_fuel_cut_registered_stock_contract(jk08a_stock_bytes): contract.registered_stock_contract(jk08a_stock_bytes)
def test_main_rpm_fuel_cut_preserves_earlier_regions(): contract.earlier_region_contract()
def test_main_rpm_fuel_cut_literal_matrix(): contract.literal_contract()
def test_main_rpm_fuel_cut_both_arithmetic_views(): contract.equation_contract()
def test_main_rpm_fuel_cut_published_counts(): contract.publication_contract()


@pytest.mark.parametrize('number,before,after',[
    ('11','Q-R','Q-R+(1-A)'),
    ('12','Q-R','Q-R+A'),
    ('11','Z = 1-min(1,B*RAM8[ffff24f1]+(1-B)*ROM8[00008c69])','Z = 1'),
    ('12','RAM8[ffff2468]>>4','RAM8[ffff2468]>>5'),
    ('11','F&249','F&0'),
    ('12','R = uint16(from)','R = int16(from)'),
    ('11','K = (1-U)*RAM8[ffff24f1]+U*ROM8[00008c69]','K = RAM8[ffff24f1]'),
    ('12','K = (1-U)*RAM8[ffff24f1]+U*ROM8[00008c69]','K = max(0,RAM8[ffff24f1]-1)'),
])
def test_main_rpm_fuel_cut_rejects_changed_semantics(number,before,after):
    formulas = copy.deepcopy(contract.contracts()['formulas'])
    assert before in formulas[number]
    formulas[number] = formulas[number].replace(before,after)
    with pytest.raises(AssertionError): contract.equation_contract(formulas=formulas)


def test_main_rpm_fuel_cut_existing_arm_retains_nonzero_counter():
    row = contract.equations.model.case(0,flags=2,counter=255,speed=612)
    actual = contract.equations.evaluate(contract.equations.FORMULAS['12'],'12',row)
    assert (actual['to'],actual['K']) == (2,255)


def test_main_rpm_fuel_cut_new_arm_loads_stock_zero_at_equality():
    row = contract.equations.model.case(0,flags=0,counter=255,speed=612)
    actual = contract.equations.evaluate(contract.equations.FORMULAS['12'],'12',row)
    assert (actual['to'],actual['K']) == (6,0)


def test_main_rpm_fuel_cut_active_release_equality_holds():
    row = contract.equations.model.case(0,flags=4,counter=255,speed=596)
    actual = contract.equations.evaluate(contract.equations.FORMULAS['12'],'12',row)
    assert (actual['to'],actual['K']) == (4,255)


def test_main_rpm_fuel_cut_matrix_has_all_six_outcomes_and_sr_controls():
    rows = contract.equations.model.matrix()
    assert {row['outcome'] for row in rows[:6]} == {row['outcome'] for row in rows}
    assert len({row['outcome'] for row in rows}) == 6
    assert {row['sr'] for row in rows} == {t|(i<<4)|(mq<<8) for t in range(2) for i in range(16) for mq in range(4)}
