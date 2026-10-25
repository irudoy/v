"""Physical timing closure, independent interpolation and argument boundaries."""

import pytest
from kb import repo,timing_division_contract as contract,timing_division_semantics as numeric


def test_timing_fixture_preserves_every_instruction_and_changes_only_exact_RAM_pointers():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    restored=bytearray(fixture)
    for row in aliases:
        assert row['alias']==0x01000000+(row['original']&65535)
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]
    assert 0x4BE80 in range(*contract.SPANS[-1])
    assert contract.POOLS[0x4BF60]==(4,500000)


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_timing_descriptor_refuses_native_or_implicit_inference(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    assert changed!=original
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_word_surface_uses_separate_integer_interpolation_and_only_needed_neighbors():
    table=b''.join(value.to_bytes(2,'big') for value in range(64))
    axis=b''.join(value.to_bytes(2,'big') for value in range(0,800,100))
    middle=numeric.surface(table,axis,axis,50,50)
    assert middle['value']==4 and middle['operand_offsets']==[0,2,16,18]
    assert middle['column_fraction']==middle['row_fraction']==32768
    endpoint=numeric.surface(table,axis,axis,65535,65535)
    assert endpoint['value']==63 and endpoint['operand_offsets']==[126]
    asymmetric=numeric.surface(table,axis,axis,100,0)
    assert asymmetric['value']==8 and asymmetric['operand_offsets']==[16]
    assert asymmetric['row']==1 and asymmetric['column']==0


def test_byte_curve_keeps_zero_weight_physical_neighbor_outside_semantic_values():
    table=bytes((*range(8),231));axis=bytes(range(16,144,16))
    result=numeric.curve(table,axis,255)
    assert result['value']==7 and result['fraction']==0 and result['operand_offsets']==[8,7]
    assert result['semantic_bytes']==8 and result['physical_bytes']==9
    assert numeric.curve(table[:-1]+bytes([13]),axis,255)['value']==7


def test_caller_equation_binds_exact_dividend_then_independent_byte_and_signed_clamps():
    memory=bytearray(65536)
    memory[0x41AB]=64;memory[0x1900:0x1902]=bytes.fromhex('ffff');memory[0x1A7D]=128
    axis=b''.join(value.to_bytes(2,'big') for value in range(0,800,100))
    calibration={0xC50E:bytes.fromhex('00ff')*64,0x1461A:axis,0x1464A:axis,
        0x11F02:bytes([255])*8+bytes([73]),0x11EEA:bytes(range(0,128,16)),0x9012:bytes(2)}
    result=numeric.caller(calibration,bytes(memory))
    assert result['divisor']==500000 and result['dividend']==4261413375
    assert result['quotient']==8522 and result['memory'][0x134A]==255 and result['output']==127
    memory[0x2458]=32;memory[0x1348]=17;memory[0x134A]=19;memory[0x134C]=23;memory[0x12D4]=29
    bypass=numeric.caller(calibration,bytes(memory))
    assert bypass['dividend'] is None and bypass['quotient'] is None
    assert tuple(bypass['memory'][at] for at in (0x1348,0x134A,0x134C,0x12D4))==(17,19,23,29)


def test_published_geometry_and_divisor_bind_to_current_source_contract():
    text=(repo.ROOT/'defs/JK08A.timing-division.md').read_text()
    declared=contract.descriptor(repo.ROOT)
    assert '`0004BDC2`' in text and '`0004BE82`' in text and '500000' in text
    assert 0x26270 in declared['function_entries'] and 0x26474 in declared['function_entries']
