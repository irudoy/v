"""Natural denominator entries, zero bypass and independent value equations."""

import pytest
from kb import compile,repo,timing_denominator_contract as contract,timing_denominator_matrix as matrix
from kb import timing_denominator_semantics as numeric,denominator_argument_contract as arguments
from kb.model import SymbolKey


def test_denominator_fixture_retains_every_stock_instruction_and_declares_only_its_aliases():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        assert row['alias']==0x01000000+(row['original']&65535)
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    assert {0x7B2C8,0x7B3F4}<=set(contract.FUNCTIONS)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_denominator_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text();changed=original.replace(flag+' = false',flag+' = true',1)
    assert changed!=original
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_synthetic_curves_preserve_the_foreign_physical_neighbor_and_the_gate_bit():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    case=dict(pattern='255',gate=1,row=100,column=100,curve=100,override=0,high=0x7FFF,low=0x8000,variant=0,sr=0,entry=0x7B2C8,kind='parent-a')
    calibration=matrix.calibrations(declared,image,case)
    assert calibration[0x14AFA]==bytes.fromhex('00ff')*8+image[0x14B0A:0x14B0C]
    assert calibration[0x18DD6]==bytes.fromhex('00ff')*8+image[0x18DE6:0x18DE8]
    assert calibration[0x83C1]==bytes([image[0x83C1]|2])


def _ram(row=100,high=0x7FFF,low=0x8000,override=0):
    return matrix.memory(dict(row=row,column=100,curve=100,high=high,low=low,override=override))


def _calibration(curve,gate=1):
    surface=bytes.fromhex('00ff')*256
    curve_bytes=curve.to_bytes(2,'big')*8+b'\x00\x00'
    axis16=b''.join(value.to_bytes(2,'big') for value in range(0,1600,100))
    axis8=b''.join(value.to_bytes(2,'big') for value in range(0,800,100))
    return {0xC98E:surface,0x16948:surface,0x13478:axis16,0x13498:axis16,0x18846:axis16,0x18866:axis16,
        0x14AFA:curve_bytes,0x18DD6:curve_bytes,0x134B8:axis8,0x18886:axis8,0x83C1:bytes([2 if gate else 0])}


@pytest.mark.parametrize('kind',('parent-a','parent-b'))
def test_zero_curve_bypasses_unsigned_division_without_the_callee_fault_store(kind):
    result=numeric.caller(kind,_calibration(0),_ram())
    assert result['zero_bypass'] is True and result['unsigned'] is None
    assert result['fault']==bytes.fromhex('a5c3d2e1')
    assert result['memory'][0x2CFD if kind=='parent-a' else 0x35D6]==255


@pytest.mark.parametrize('kind',('parent-a','parent-b'))
def test_positive_curve_uses_the_post_delay_divisor_and_row_times_255(kind):
    result=numeric.caller(kind,_calibration(255),_ram())
    assert result['unsigned']['divisor']==255 and result['unsigned']['dividend']==100*255
    assert result['unsigned']['quotient']==100 and result['fault']==bytes.fromhex('a5c3d2e1')


def test_clear_gate_and_parent_b_override_skip_both_lookups():
    skipped=numeric.caller('parent-a',_calibration(255,gate=0),_ram())
    assert skipped['active'] is False and skipped['output']==0x1357
    overridden=numeric.caller('parent-b',_calibration(255),_ram(override=0x10))
    assert overridden['active'] is False and overridden['unsigned'] is None and overridden['output']==0x8000


def test_pinned_dispositions_match_the_current_unsigned_reader_claims():
    model=compile.build(repo.ROOT)
    declared=arguments.descriptor(repo.ROOT)
    for row in declared['reference']:
        symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
        link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
                  and item.to.key==arguments.TARGET)
        assert arguments.original(row,link)
        assert row['component']=='timing_denominator_paths'


def test_document_binds_both_natural_entries_delay_slots_and_denominator_tables():
    text=(repo.ROOT/'defs/JK08A.timing-denominator.md').read_text()
    for address in (0x7B2C8,0x7B3F4,0x14AFA,0x18DD6,0x7B32E,0x7B330,0x7B482,0x7B484,0x21CE0,0x83C1):
        assert f'`{address:08X}`' in text
    assert '`FFFF41FB`' in text and '`FFFF4214`' in text
