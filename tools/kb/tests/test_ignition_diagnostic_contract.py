"""Word-curve boundaries and explicit limits of ignition diagnostic preparation."""

import pytest
from kb import repo
from kb import ignition_diagnostic_contract as contract,ignition_diagnostic_semantics as numeric
from kb import ignition_diagnostic_matrix as matrix


def test_preparation_pins_actual_wrapper_bound_stride_and_neighbor_operands():
    declared=contract.descriptor(repo.ROOT)
    contract.require_image(declared,repo.images()['JK08A'].path.read_bytes())
    assert declared['curve']['semantic_table_bytes']==16
    assert declared['curve']['physical_read_extent_bytes']==18
    assert declared['native_control_bytes']['addresses']==[0xFFFF99C4,0xFFFF9926]
    assert len(declared['diagnostic']['dids'])==len(set(declared['diagnostic']['dids']))


def test_last_neighbor_is_a_physical_operand_with_no_endpoint_weight():
    axis=b''.join(value.to_bytes(2,'big') for value in range(0,8000,1000))
    points=tuple(index*100 for index in range(8))
    table=b''.join(value.to_bytes(2,'big') for value in (*points,65535))
    changed=table[:-2]+bytes(2)
    first=numeric.word_curve(table,axis,65535)
    second=numeric.word_curve(changed,axis,65535)
    assert first==second
    assert first['value']==700 and first['fraction']==0 and first['operand_offsets']==(14,16)
    assert first['neighbor_contribution'] is False
    assert numeric.word_curve(table,axis,1500)['value']==150


def test_decreasing_curve_uses_directed_integer_truncation():
    axis=b''.join(value.to_bytes(2,'big') for value in range(0,8000,1000))
    points=(1,0,0,0,0,0,0,0,65535)
    table=b''.join(value.to_bytes(2,'big') for value in points)
    assert numeric.word_curve(table,axis,500)['value']==1


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_preparation_cannot_grant_geometry_relation_or_hardware_scope(tmp_path,flag):
    before=(repo.ROOT/contract.DESCRIPTOR).read_text()
    after=before.replace(flag+' = false',flag+' = true',1)
    assert after!=before
    path=tmp_path/contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text(after)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_normal_conditional_chain_keeps_explicit_override_separate():
    correction=numeric.event_correction(5,100)['correction']
    coordinate=numeric.normal_coordinate(correction,-7,50,110)
    assert correction==coordinate==-5
    assert numeric.command(coordinate,110)==115
    assert numeric.command(coordinate,110,True)==90


def test_scheduler_sink_has_an_explicit_post_store_boundary_and_no_hardware_admission():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases,boundaries=contract.independent_fixture(declared,image)
    assert boundaries==[dict(address=0x2A892,end=0x2A898,stock=image[0x2A892:0x2A898].hex(),
        bytes='e000000b0009',source=contract.SCHEDULER['source'],
        stock_body_admitted=False,hardware_effects_admitted=False)]
    restored=bytearray(fixture)
    restored[0x2A892:0x2A898]=image[0x2A892:0x2A898]
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]


def test_sequenced_inputs_preserve_the_physical_neighbor_and_keep_outputs_unseeded():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    cases=matrix.cases(declared,image)
    for index,case in enumerate(cases):
        assert case['index']==index and case['stage']==index%3
        assert case['entry']==contract.SEQUENCE[case['stage']]
        assert case['parent']==index//3
        ram=matrix.initial_memory(case)
        assert ram[0x2000:0x2002]==bytes(2) and ram[0x12D6]==ram[0x11D4]==ram[0x2022]==0
        assert matrix.native_controls(ram)==bytes(256)
        values=matrix.calibrations(declared,image,case)
        assert values[0x147DA][-2:]==image[0x147EA:0x147EC]
        assert values[0x13C48]==image[0x13C48:0x13C58]


def test_documented_curve_extent_and_scheduler_scope_come_from_the_exact_contract():
    declared=contract.descriptor(repo.ROOT)
    text=(repo.ROOT/'defs/JK08A.ignition-diagnostic-path.md').read_text()
    assert str(declared['curve']['semantic_table_bytes'])+' bytes' in text
    assert str(declared['curve']['physical_read_extent_bytes'])+' bytes' in text
    assert f"`{declared['scheduler_boundary']['address']:08X}`" in text
    for flag in contract.FLAGS:assert '`'+flag+' = false`' in text
