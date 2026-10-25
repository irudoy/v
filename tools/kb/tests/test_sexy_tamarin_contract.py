"""Natural sexy-tamarin: each indexed byte curve scales its own signed dividend."""

import pytest
from kb import compile,repo
from kb import sexy_tamarin_contract as contract, sexy_tamarin_matrix as matrix
from kb import sexy_tamarin_semantics as numeric, sexy_tamarin_argument_contract as arguments
from kb.model import SymbolKey


def test_byte_curve_retains_the_natural_next_then_current_read_order():
    result=numeric.curve_byte(bytes(range(0,256,32))+b'\x5a',bytes(range(0,256,32)),112)
    assert result['value']==112 and result['offsets']==(4,3)


def test_sexy_tamarin_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0xC0D90 and contract.DIVISOR==100
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_sexy_tamarin_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_each_selected_curve_scales_its_dividend_and_keeps_divisor_100():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    cases=matrix.cases(declared,image)

    def one(index,which,pattern):
        case=next(item for item in cases if item['input']==index and item['which']==which and item['pattern']==pattern
                  and item['source']==(0x90 if index==0 else 0xA0))
        return numeric.caller(image,matrix.calibrations(declared,image,case),matrix.memory(case),case['input'])

    stock=one(0,0,'stock');changed=one(0,1,'constant');second=one(0,2,'constant')
    other=one(1,0,'stock');moved=one(1,1,'constant');paired=one(1,2,'constant')
    assert stock['divisor']==changed['divisor']==second['divisor']==paired['divisor']==100
    assert stock['first_table']==0x1252A and stock['second_table']==0x123F2
    assert other['first_table']==0x12532 and other['second_table']==0x123FA
    assert stock['first_dividend']!=changed['first_dividend'] and stock['dividend']==changed['dividend']
    assert stock['dividend']!=second['dividend'] and stock['first_dividend']==second['first_dividend']
    assert other['first_dividend']!=moved['first_dividend'] and other['dividend']!=paired['dividend']
    assert stock['fault']==paired['fault']==bytes.fromhex('a5c3d2e1')


def test_document_binds_the_four_curves_and_the_constant_divisor():
    text=(repo.ROOT/'defs/JK08A.sexy-tamarin.md').read_text()
    for address in (0xC0D90,0x1252A,0x12532,0x123F2,0x123FA,0x26474,0xC0DF6,0xC0DF8,0xC0F28,0xC0F2A,0x21BBC):
        assert f'`{address:08X}`' in text
    assert '100' in text and '`FFFF1240`' in text


def test_pinned_dispositions_match_the_current_signed_reader_claims():
    model=compile.build(repo.ROOT)
    rows=arguments.descriptor(repo.ROOT)['reference']
    assert [row['owner'] for row in rows]==['sturdy-worm/tbl','foamy-cuckoo/tbl','strange-salmon/tbl','greedy-chamois/tbl']
    for row in rows:
        symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
        link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
                  and item.to.key==arguments.TARGET)
        assert arguments.original(row,link)
        assert row['component']=='sexy_tamarin_paths'
