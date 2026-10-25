"""Conditional lookup products and the explicit divisor bypass."""

import pytest

from kb import compile, repo
from kb import viridian_armadillo_argument_contract as arguments
from kb import viridian_armadillo_contract as contract
from kb import viridian_armadillo_matrix as matrix
from kb import viridian_armadillo_semantics as numeric
from kb.model import SymbolKey


def test_natural_fixture_preserves_the_owned_instructions_and_stock_neighbor():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    assert bytes(restored) == image
    assert contract.ENTRY == 0xB7A3C and contract.SITE == 0xB7AE8
    for first, last in contract.SPANS:
        assert fixture[first:last] == image[first:last]


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path, flag):
    source = (repo.ROOT / contract.DESCRIPTOR).read_text()
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text(source.replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


def test_curve_changes_the_dividend_with_the_same_explicit_divisor():
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)
    cases = matrix.cases(declared, image)

    def one(pattern, divisor=10):
        case = next(row for row in cases if row['pattern'] == pattern and row['axis'] == 'strict'
                    and row['coordinate'] == 14 and row['divisor'] == divisor and row['factor'] == 4
                    and row['selector'] == 0 and row['stage_factor'] == 0)
        return numeric.caller(image, matrix.calibrations(declared, image, case), matrix.memory(case), case)

    first, second = one('thousand'), one('two-thousand')
    assert first['lookup']['value'] == 1000 and second['lookup']['value'] == 2000
    assert first['divisor'] == second['divisor'] == 10
    assert first['dividend'] == (-80000 & 0xFFFFFFFF)
    assert second['dividend'] == (-160000 & 0xFFFFFFFF)
    bypass = one('thousand', 0)
    assert all(row['site'] != contract.SITE for row in bypass['calls'])
    assert bypass['fault'] == bytes.fromhex('a5c3d2e1')


def test_exact_disposition_preserves_other_claim_properties_and_ledger_selectors():
    model = compile.build(repo.ROOT)
    rows = arguments.descriptor(repo.ROOT)['reference']
    assert len(rows) == 1 and rows[0]['owner'] == 'sassy-flamingo/tbl'
    row = rows[0]
    symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
    link = next(item for item in model.links if item.owner is symbol.meaning
                and item.type == 'reader' and item.to.key == arguments.TARGET)
    assert arguments.original(row, link)
    assert row['component'] == 'viridian_armadillo_paths'


def test_document_binds_the_lookup_delay_slot_and_actual_store():
    text = (repo.ROOT / 'defs/JK08A.viridian-armadillo.md').read_text()
    for address in (0xB7A3C, 0x14E42, 0x264CC, 0xB7AE8, 0xB7AEA, 0x21BBC):
        assert f'`{address:08X}`' in text
    assert '`FFFF9818`' in text and '`FFFF3228`' in text
