"""Natural signed-curve entry, zero bypass and post-delay arguments."""

import pytest
from kb import compile,repo,signed_curve_contract as contract,signed_curve_matrix as matrix,signed_curve_semantics as numeric
from kb import signed_curve_argument_contract as argument
from kb.model import SymbolKey


def test_signed_curve_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0x7B0A0
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_signed_curve_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_zero_difference_bypasses_signed_division_and_a_positive_curve_does_not():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    zero=next(case for case in matrix.cases(declared,image) if case['second']=='zero' and case['first']=='zero')
    positive=next(case for case in matrix.cases(declared,image) if case['second']=='constant' and case['first']=='zero' and case['mode']==0)
    bypass=numeric.caller(matrix.calibrations(declared,image,zero),matrix.memory(zero))
    divided=numeric.caller(matrix.calibrations(declared,image,positive),matrix.memory(positive))
    assert bypass['zero_bypass'] is True and bypass['calls']==() and bypass['fault']==bytes.fromhex('a5c3d2e1')
    assert divided['divisor']>0 and divided['calls'][0]['divisor']==divided['divisor']
    assert divided['calls'][0]['quotient']==800 or divided['calls'][0]['dividend']==divided['calls'][0]['quotient']*divided['divisor']


def test_pinned_disposition_matches_the_current_signed_reader_claim():
    model=compile.build(repo.ROOT)
    row=argument.descriptor(repo.ROOT)['reference'][0]
    symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader' and item.to.key==argument.TARGET)
    assert argument.original(row,link)


def test_document_binds_the_natural_entry_delay_slots_and_signed_curve():
    text=(repo.ROOT/'defs/JK08A.signed-curve.md').read_text()
    for address in (0x7B0A0,0x18DE6,0x18E06,0x18E26,0x266E8,0x7B152,0x7B16A,0x7B182,0x21BBC,0x83C1):
        assert f'`{address:08X}`' in text
