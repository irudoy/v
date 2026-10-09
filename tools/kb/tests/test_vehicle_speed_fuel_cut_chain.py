"""Exact-stock and bounded raw-domain vehicle-speed fuel-cut contracts."""
import pytest
from tools.kb.tests import vehicle_speed_fuel_cut_contract as contract

def test_vehicle_speed_fuel_cut_owner_contract(): contract.owner_contract()
def test_vehicle_speed_fuel_cut_registered_stock_contract(jk08a_stock_bytes): contract.registered_stock_contract(jk08a_stock_bytes)
def test_vehicle_speed_fuel_cut_preserves_earlier_regions(): contract.earlier_region_contract()
def test_vehicle_speed_fuel_cut_literal_matrix(): contract.literal_contract()
def test_vehicle_speed_fuel_cut_arithmetic_view(): contract.equation_contract()
def test_vehicle_speed_fuel_cut_published_counts(): contract.publication_contract()
def test_vehicle_speed_fuel_cut_rejects_each_bound_byte_change(jk08a_stock_bytes): contract.bound_byte_contract(jk08a_stock_bytes)

@pytest.mark.parametrize('before,after',[
    ('S-L+1','S-L'), ('S-H+1','S-H'), ('D = (1-G)*','D = 1*'),
    ('Z = 1-min(1,K)','Z = 1'), ('F&254','F&0'), ('C&127','C&0'),
    ('C>>5','C>>4'), ('C>>7','C>>6'),
    ('K = (1-U)*RAM8[ffff24f6]+U*ROM8[00008caf]','K = RAM8[ffff24f6]'),
    ('K = (1-U)*RAM8[ffff24f6]+U*ROM8[00008caf]','K = max(0,RAM8[ffff24f6]-1)'),
    ('S = uint8(from)','S = int8(from)'),
    ('E = A*V*B+(1-A)*N','E = (1-G)*(A*V*B+(1-A)*N)'),
])
def test_vehicle_speed_fuel_cut_rejects_changed_semantics(before,after):
    formula = contract.equations.FORMULA
    assert formula.count(before) == 1
    with pytest.raises(AssertionError): contract.equation_contract(formula=formula.replace(before,after,1))

@pytest.mark.parametrize('flags,control,counter,speed,wanted',[
    (0,0,255,93,(1,128,0,1)),
    (0,128,255,93,(0,128,255,0)),
    (1,160,255,91,(0,160,255,0)),
    (1,128,255,91,(1,128,255,1)),
    (0,0,255,255,(1,128,0,1)),
])
def test_vehicle_speed_fuel_cut_boundary_witnesses(flags,control,counter,speed,wanted):
    row = contract.equations.model.case(0,flags=flags,control=control,counter=counter,speed=speed)
    result = contract.equations.evaluate(contract.equations.FORMULA,row)
    assert (result['to'],result['J'],result['K'],result['D']) == wanted

def test_vehicle_speed_fuel_cut_matrix_domains_and_cpu_controls():
    rows = contract.equations.model.matrix()
    assert len(rows) == 12544
    assert len({row['outcome'] for row in rows}) == 10
    assert {row['outcome'] for row in rows[:10]} == {row['outcome'] for row in rows}
    for key in ('flags','control','counter'): assert {row[key] for row in rows} == set(range(256))
    assert {row['sr'] for row in rows} == {t|(i<<4)|(mq<<8) for t in range(2) for i in range(16) for mq in range(4)}
