"""Bounded timing entry, exact return boundary and independent value equations."""

import pytest
from kb import repo,timing_tail_contract as contract,timing_tail_matrix as matrix,timing_tail_semantics as numeric


def test_tail_fixture_retains_every_stock_instruction_and_declares_only_its_aliases_and_return():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases,boundaries=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        assert row['alias']==0x01000000+(row['original']&65535)
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert len(boundaries)==1
    boundary=boundaries[0];restored[boundary['address']:boundary['end']]=bytes.fromhex(boundary['stock'])
    assert bytes(restored)==image
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]
    assert declared['window_entry']==matrix.ENTRY==0x4B3F2
    assert boundary['address']==0x4B4A4 and boundary['bytes']=='57f6472a000b0009'
    assert boundary['parent_reachability_admitted'] is False


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_tail_descriptor_refuses_parent_reachability_or_other_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text();changed=original.replace(flag+' = false',flag+' = true',1)
    assert changed!=original
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_synthetic_curves_preserve_the_foreign_physical_neighbor_without_an_extra_semantic_point():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    calibration=matrix.calibrations(declared,image,{'pattern':'255'})
    assert calibration[0x11EFA]==bytes([255])*8+image[0x11F02:0x11F03]
    assert calibration[0x147CA]==bytes.fromhex('00ff')*8+image[0x147DA:0x147DC]


@pytest.mark.parametrize('minimum,enabled,coefficient,output',((9350,1,2000,255),(7350,1,0,0),(7349,1,0,0),(9350,0,2000,0)))
def test_tail_equation_keeps_its_speed_coefficient_gate_and_post_lookup_division(minimum,enabled,coefficient,output):
    ram=bytearray(65536);ram[0x41AB]=enabled*64
    ram[0x28B8:0x28BA]=minimum.to_bytes(2,'big');ram[0x28BA:0x28BC]=minimum.to_bytes(2,'big')
    ram[0x1347]=17;ram[0x1349]=19;ram[0x134B]=23
    axis=b''.join(value.to_bytes(2,'big') for value in range(32,160,16))
    calibration={0x11EFA:bytes([255])*8+bytes([100]),0x147CA:bytes.fromhex('00ff')*8+bytes(2),
        0x1460A:axis,0x11EEA:bytes(range(48,176,16)),0x9010:(7350).to_bytes(2,'big')}
    result=numeric.caller(calibration,bytes(ram))
    assert result['coefficient']==coefficient and result['output']==output
    assert result['memory'][0x1900:0x1902]==coefficient.to_bytes(2,'big')
    assert result['memory'][0x12D5]==output
    if minimum==9350 and enabled:
        assert result['dividend']==130050000 and result['quotient']==260 and result['divisor']==500000
    if not result['lookup_enabled']:
        assert tuple(result['memory'][at] for at in (0x1347,0x1349,0x134B))==(17,19,23)


def test_document_binds_the_explicit_parent_window_and_physical_calibration_addresses():
    text=(repo.ROOT/'defs/JK08A.timing-tail.md').read_text();declared=contract.descriptor(repo.ROOT)
    assert f"`{declared['window_entry']:08X}`" in text
    for address in (0x4AFDC,0x4B4A4,0x11EFA,0x147CA,0x11F02,0x147DA):assert f'`{address:08X}`' in text
