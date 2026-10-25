"""Natural independent-leopard loop, nonnegative curve and constant divisor."""

import pytest
from kb import compile,repo
from kb import independent_leopard_contract as contract, independent_leopard_matrix as matrix
from kb import independent_leopard_semantics as numeric, independent_leopard_argument_contract as arguments
from kb.model import SymbolKey


def test_independent_leopard_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0x5AC54
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_independent_leopard_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_nonnegative_curve_divides_by_one_hundred_and_a_negative_step_uses_the_other_curve():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    positive=next(case for case in matrix.cases(declared,image) if case['pattern']=='constant' and case['left']==(2000,1500))
    mixed=next(case for case in matrix.cases(declared,image) if case['left']==(1000,0) and case['right']==(100,800))
    divided=numeric.caller(matrix.calibrations(declared,image,positive),matrix.memory(positive))
    other=numeric.caller(matrix.calibrations(declared,image,mixed),matrix.memory(mixed))
    assert [row['divisor'] for row in divided['calls']]==[100,100]
    assert [row['table'] for row in divided['calls']]==[0x12522,0x12522]
    assert divided['open_calls'][0]['dividend']==190000 and divided['open_calls'][0]['quotient']==1900
    assert [row['table'] for row in other['calls']]==[0x12522,0x12526]
    assert divided['fault']==other['fault']==bytes.fromhex('a5c3d2e1')


def test_document_binds_the_loop_curve_and_constant_divisor():
    text=(repo.ROOT/'defs/JK08A.independent-leopard.md').read_text()
    for address in (0x5AC54,0x12522,0x12526,0x26358,0x5AD64,0x21CE0):
        assert f'`{address:08X}`' in text
    assert '`FFFF288C`' in text and '`FFFF40A4`' in text


def test_pinned_disposition_matches_the_current_unsigned_reader_claim():
    model=compile.build(repo.ROOT)
    row=arguments.descriptor(repo.ROOT)['reference'][0]
    symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
              and item.to.key==arguments.TARGET)
    assert arguments.original(row,link)
    assert row['component']=='independent_leopard_paths'
