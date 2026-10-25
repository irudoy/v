"""Natural fine-gopher entry, zero-word bypass and post-delay arguments."""

import pytest
from kb import compile,repo,fine_gopher_contract as contract,fine_gopher_matrix as matrix,fine_gopher_semantics as numeric
from kb import fine_gopher_argument_contract as arguments
from kb.model import SymbolKey


def test_fine_gopher_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0x6062C
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_fine_gopher_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_scaled_curve_uses_the_constant_divisor_and_a_zero_word_bypasses():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    positive=next(case for case in matrix.cases(declared,image)
                  if case['word_a']==65535 and case['word_b']==129 and case['curve_a']=='stock' and case['left']==0)
    bypass=next(case for case in matrix.cases(declared,image) if case['divisor']==0 and case['curve_e']=='constant')
    divided=numeric.caller(matrix.calibrations(declared,image,positive),matrix.memory(positive))
    skipped=numeric.caller(matrix.calibrations(declared,image,bypass),matrix.memory(bypass))
    assert divided['rare_call']['divisor']==0x3FC and divided['rare_call']['dividend']==44880
    assert divided['rare_call']['quotient']==44 and divided['fault']==bytes.fromhex('a5c3d2e1')
    assert skipped['zero_bypass'] is True and skipped['beetle_call'] is None
    assert skipped['fault']==bytes.fromhex('a5c3d2e1') and skipped['beetle_byte']==255


def test_pinned_dispositions_match_the_current_unsigned_reader_claims():
    model=compile.build(repo.ROOT)
    declared=arguments.descriptor(repo.ROOT)
    for row in declared['reference']:
        symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
        link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
                  and item.to.key==arguments.TARGET)
        assert arguments.original(row,link)
        assert row['component']=='fine_gopher_paths'


def test_document_binds_the_natural_entry_curves_and_absolute_windows():
    text=(repo.ROOT/'defs/JK08A.fine-gopher.md').read_text()
    for address in (0x6062C,0x14F42,0x14F52,0x15002,0x13C58,0x13BD8,0x264CC,0x21CE0,0x93E8,0x60712,0x607B8,0x608C4):
        assert f'`{address:08X}`' in text
    assert '`FFFF8C54`' in text and '`FFFF99FC`' in text
