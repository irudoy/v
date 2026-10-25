"""Source boundaries and exact conditional premises of exhaust-target paths."""

import pytest
from kb import repo
from kb import exhaust_target_contract as contract,exhaust_target_matrix as matrix


@pytest.fixture(scope='module')
def sources():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    return declared,image,fixture,aliases


def test_fixture_changes_only_explicit_pointer_pools_and_keeps_natural_instructions(sources):
    declared,image,fixture,aliases=sources
    restored=bytearray(fixture)
    for row in aliases:
        assert row['alias']==0x01000000+(row['original']&65535)
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    assert {row['address'] for row in aliases}==set(contract.ALIASES)
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]


@pytest.mark.parametrize('fault',(*contract.FLAGS,'entry','pool','function'))
def test_descriptor_refuses_expanded_scope_or_changed_exact_sources(tmp_path,fault):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    if fault in contract.FLAGS:
        text=original.replace(fault+' = false',fault+' = true',1)
    elif fault=='entry':text=original.replace('start = 0x000bfe88','start = 0x000bfe8a',1)
    elif fault=='function':text=original.replace('0x000bfe88,0x000259d0','0x000bfdc0,0x000259d0',1)
    else:text=original.replace('stock_value = 0xffff128c','stock_value = 0xffff128d',1)
    assert text!=original
    destination=tmp_path/contract.DESCRIPTOR
    destination.parent.mkdir(parents=True)
    destination.write_text(text)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_mode_inputs_do_not_seed_the_result_into_the_frame_or_previous_output(sources):
    declared,image,_,_=sources
    cases=[case for case in matrix.cases(declared,image) if case['kind']=='conditioned']
    for case in cases:
        ram=matrix.memory(case)
        assert ram[0x2327]==91 and ram[0x1C90]==255
        assert ram[0x1284]==1
        assert ram[0x248B]=={0:5,1:0,2:1}[case['mode']]
        assert ram[0x1071]==(0 if case['selected']==0 else 255)
        assert ram[0x1C5F if case['selected']==0 else 0x1C5D]==case['value']
        assert len(matrix.context(declared,case))==20
    assert {(case['selected'],case['mode'],case['value']) for case in cases}=={
        (selected,mode,value) for selected in (0,1) for mode in (0,1,2) for value in matrix.VALUES}


def test_documented_output_and_modes_bind_to_the_executed_descriptor(sources):
    declared,_,_,_=sources
    text=(repo.ROOT/'defs/JK08A.exhaust-target-path.md').read_text()
    for address in declared['function_entries']:assert f'`{address:08X}`' in text
    for flag in contract.FLAGS:assert '`'+flag+' = false`' in text
    assert '`FFFF2327`' in text and '`1166`' in text
    assert '`FFFF2022`' in text and '`147DA`' in text
