"""Natural quiet-cat: each indexed byte curve scales its own signed dividend."""

import pytest
from kb import compile,repo
from kb import quiet_cat_contract as contract, quiet_cat_matrix as matrix
from kb import quiet_cat_semantics as numeric, quiet_cat_argument_contract as arguments
from kb.model import SymbolKey


def test_quiet_cat_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0xBE32A and contract.DIVISOR==100
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_quiet_cat_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_each_index_scales_only_its_curve_and_keeps_divisor_100():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    cases=matrix.cases(declared,image)
    zero=next(case for case in cases if case['input']==0 and case['pattern']=='stock' and case['source']==0x90)
    changed=next(case for case in cases if case['input']==0 and case['pattern']=='constant' and case['source']==0x90)
    other=next(case for case in cases if case['input']==1 and case['pattern']=='stock')
    moved=next(case for case in cases if case['input']==1 and case['pattern']=='constant')
    first=numeric.caller(image,matrix.calibrations(declared,image,zero),matrix.memory(zero),zero['input'])
    second=numeric.caller(image,matrix.calibrations(declared,image,changed),matrix.memory(changed),changed['input'])
    third=numeric.caller(image,matrix.calibrations(declared,image,other),matrix.memory(other),other['input'])
    fourth=numeric.caller(image,matrix.calibrations(declared,image,moved),matrix.memory(moved),moved['input'])
    assert first['divisor']==second['divisor']==third['divisor']==fourth['divisor']==100
    assert first['table']==second['table']==0x123EA and third['table']==fourth['table']==0x12412
    assert first['dividend']!=second['dividend'] and third['dividend']!=fourth['dividend']
    assert first['fault']==fourth['fault']==bytes.fromhex('a5c3d2e1')


def test_document_binds_both_curves_and_the_constant_divisor():
    text=(repo.ROOT/'defs/JK08A.quiet-cat.md').read_text()
    for address in (0xBE32A,0x123EA,0x12412,0x26474,0xBE41E,0xBE420,0x21BBC):
        assert f'`{address:08X}`' in text
    assert '100' in text and '`FFFF1224`' in text


def test_pinned_dispositions_match_the_current_signed_reader_claims():
    model=compile.build(repo.ROOT)
    rows=arguments.descriptor(repo.ROOT)['reference']
    assert [row['owner'] for row in rows]==['belligerent-potoo/tbl','red-bullmastiff/tbl']
    for row in rows:
        symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
        link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
                  and item.to.key==arguments.TARGET)
        assert arguments.original(row,link)
        assert row['component']=='quiet_cat_paths'
