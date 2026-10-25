"""Exact fixture and mode premises for the conditional K-dependent BFS path."""

import pytest
from kb import repo
from kb import bfs_path_contract as contract,bfs_path_matrix as matrix


@pytest.fixture(scope='module')
def sources():
    declared=contract.descriptor(repo.ROOT)
    image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image)
    return declared,image,fixture,aliases


def test_natural_BFS_fixture_changes_only_declared_RAM_pointer_pools(sources):
    declared,image,fixture,aliases=sources
    restored=bytearray(fixture)
    for row in aliases:restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image
    assert fixture[0x9284:0x9286]==image[0x9284:0x9286]
    for start,end in contract.SPANS:assert fixture[start:end]==image[start:end]


@pytest.mark.parametrize('fault',(*contract.FLAGS,'entry','pool','function'))
def test_BFS_descriptor_refuses_changed_exact_inputs_or_broader_scope(tmp_path,fault):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    if fault in contract.FLAGS:text=original.replace(fault+' = false',fault+' = true',1)
    elif fault=='entry':text=original.replace('start = 0x0003b75c','start = 0x0003b75e',1)
    elif fault=='function':text=original.replace('0x0003b75c,','0x0003b75e,',1)
    else:text=original.replace('stock_value = 0xffff1dec','stock_value = 0xffff1dee',1)
    assert text!=original
    destination=tmp_path/contract.DESCRIPTOR
    destination.parent.mkdir(parents=True)
    destination.write_text(text)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_K_and_mode_inputs_keep_published_BFS_and_quarter_output_unseeded(sources):
    declared,image,_,_=sources
    cases=matrix.cases(declared,image)
    stock=int.from_bytes(image[0x9284:0x9286],'big')
    for case in cases:
        ram=matrix.memory(case)
        assert ram[0x1026:0x1028]==b'\0\0' and ram[0x1E40:0x1E44]==bytes(4)
        assert int.from_bytes(ram[0x1E38:0x1E3C],'big')==case['aggregate']
        assert int.from_bytes(ram[0x11E8:0x11EA],'big')==case['rpm']
        assert ram[0x2449]==case['mode']*128
        assert matrix.calibrations(declared,image,case)=={0x9284:case['k'].to_bytes(2,'big')}
        if case['stock_input']:assert case['k']==stock
    assert {case['k'] for case in cases}>={stock,*matrix.K_VALUES}
    assert {case['mode'] for case in cases}=={0,1}
    assert {case['aggregate'] for case in cases}>={0,0x80000000,0xFFFFFFFF}


def test_BFS_document_uses_current_physical_source_and_scope_flags(sources):
    declared,_,_,_=sources
    text=(repo.ROOT/'defs/JK08A.bfs-path.md').read_text()
    assert '`0003B75C`' in text and 0x3B75C in declared['function_entries']
    assert '`FFFF1026`' in text and '`1208`' in text and '`00009284`' in text
    for flag in contract.FLAGS:assert '`'+flag+' = false`' in text
