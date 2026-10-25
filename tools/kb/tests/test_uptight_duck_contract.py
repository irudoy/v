"""Natural uptight-duck entry: the lookup is published, not divided."""

import pytest
from kb import compile,repo
from kb import uptight_duck_contract as contract, uptight_duck_matrix as matrix, uptight_duck_semantics as numeric
from kb import uptight_duck_argument_contract as arguments
from kb.model import SymbolKey


def test_uptight_duck_fixture_retains_every_stock_instruction():
    declared=contract.descriptor(repo.ROOT);image=repo.images()['JK08A'].path.read_bytes()
    fixture,aliases=contract.independent_fixture(declared,image);restored=bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address']+4]=row['original'].to_bytes(4,'big')
    assert bytes(restored)==image and contract.ENTRY==0xB784E and contract.DIVISOR==0xF4240
    for first,last in contract.SPANS:assert fixture[first:last]==image[first:last]


@pytest.mark.parametrize('flag',contract.FLAGS)
def test_uptight_duck_descriptor_refuses_implicit_admission(tmp_path,flag):
    original=(repo.ROOT/contract.DESCRIPTOR).read_text()
    changed=original.replace(flag+' = false',flag+' = true',1)
    path=tmp_path/contract.DESCRIPTOR;path.parent.mkdir(parents=True);path.write_text(changed)
    with pytest.raises(ValueError):contract.descriptor(tmp_path)


def test_signed_call_keeps_the_incoming_dividend_while_the_curve_changes_publication():
    image=repo.images()['JK08A'].path.read_bytes();declared=contract.descriptor(repo.ROOT)
    cases=matrix.cases(declared,image)
    varied=next(case for case in cases if case['pattern']=='constant' and case['axis']=='strict' and case['coordinate']==150)
    replaced=next(case for case in cases if case['threshold']==150)
    published=numeric.caller(matrix.calibrations(declared,image,varied),matrix.memory(varied),varied['dividend'],varied['coordinate'])
    constant=numeric.caller(matrix.calibrations(declared,image,replaced),matrix.memory(replaced),replaced['dividend'],replaced['coordinate'])
    assert published['divisor']==0xF4240 and published['dividend']==varied['dividend']
    assert published['chosen']==published['third']['value']==1000
    assert constant['chosen']==1 and constant['dividend']==replaced['dividend']
    assert published['fault']==constant['fault']==bytes.fromhex('a5c3d2e1')


def test_document_binds_the_constant_divisor_and_the_lookup():
    text=(repo.ROOT/'defs/JK08A.uptight-duck.md').read_text()
    for address in (0xB784E,0x15C80,0x13CA8,0x26524,0xB7892,0xB7894,0x21BBC):
        assert f'`{address:08X}`' in text
    assert '`000F4240`' in text and '`FFFF9818`' in text


def test_pinned_disposition_matches_the_current_signed_reader_claim():
    model=compile.build(repo.ROOT)
    row=arguments.descriptor(repo.ROOT)['reference'][0]
    symbol=model.symbols[SymbolKey('7mfk','tbl',row['address'])]
    link=next(item for item in model.links if item.owner is symbol.meaning and item.type=='reader'
              and item.to.key==arguments.TARGET)
    assert arguments.original(row,link)
    assert row['component']=='uptight_duck_paths'
