"""Natural APC reset offset: the byte curve scales the signed dividend."""

import pytest
from kb import compile,repo
from kb import apc_reset_offset_contract as contract, apc_reset_offset_matrix as matrix
from kb import apc_reset_offset_semantics as numeric, apc_reset_offset_argument_contract as arguments
from kb.model import SymbolKey


def test_apc_reset_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0x4C1E4 and contract.DIVISOR==0x14000
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_apc_reset_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_curve_change_scales_the_signed_dividend_and_keeps_the_constant_divisor():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    cases=matrix.cases(declared,image)
    low=next(case for case in cases if case['pattern']=='constant' and case['gate']==0 and case['source']==80)
    high=next(case for case in cases if case['pattern']=='high' and case['gate']==0 and case['source']==80)
    first=numeric.caller(matrix.calibrations(declared,image,low),matrix.memory(low))
    second=numeric.caller(matrix.calibrations(declared,image,high),matrix.memory(high))
    assert first['divisor']==second['divisor']==0x14000
    assert first['dividend']!=second['dividend']
    assert first['first']['value']!=second['first']['value']
    assert first['fault']==second['fault']==bytes.fromhex('a5c3d2e1')


def test_document_binds_the_curve_and_the_constant_divisor():
    text=(repo.ROOT/'defs/JK08A.apc-reset-offset.md').read_text()
    for address in (0x4C1E4,0x1208E,0x12096,0x26370,0x4C34E,0x4C350,0x21BBC):
        assert f'`{address:08X}`' in text
    assert '`00014000`' in text and '`FFFF4184`' in text


def test_pinned_disposition_matches_the_current_signed_reader_claim():
    model=compile.build(repo.ROOT)
    row=arguments.descriptor(repo.ROOT)['reference'][0]
    symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
              and item.to.key==arguments.TARGET)
    assert arguments.original(row,link)
    assert row['component']=='apc_reset_offset_paths'
