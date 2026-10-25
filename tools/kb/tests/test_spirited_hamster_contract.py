"""Conditional lookup products and the explicit divisor bypass."""

import pytest

from kb import compile, repo
from kb import spirited_hamster_argument_contract as arguments
from kb import spirited_hamster_contract as contract
from kb import spirited_hamster_matrix as matrix
from kb import spirited_hamster_semantics as numeric
from kb.model import SymbolKey


def test_natural_fixture_preserves_the_owned_instructions_and_stock_neighbor():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    assert declared['window_entry'] == 0x7A20A and contract.BOUNDARY['address'] == 0x7A248
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


def test_byte_changes_the_divisor_and_zero_bypasses_without_a_fault():
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)
    cases = matrix.cases(declared, image)

    def one(pattern):
        case = next(row for row in cases if row['pattern'] == pattern
                    and row['coordinate'] == 112 and row['numerator'] == 1 and row['axis'] == 'strict')
        return numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case), case['coordinate'])

    first, second, zero = one('one'), one('two'), one('zero')
    assert first['lookup'] == 1 and second['lookup'] == 2
    assert first['divisor'] == 1 and second['divisor'] == 2
    assert first['dividend'] == second['dividend'] == 200
    assert first['output'] == 200 and second['output'] == 100
    assert zero['divisor'] == 0 and zero['quotient'] is None and zero['output'] == 65535
    assert zero['fault'] == bytes.fromhex('a5c3d2e1')


def test_exact_disposition_preserves_other_claim_properties_and_ledger_selectors():
    model = compile.build(repo.ROOT)
    rows = arguments.descriptor(repo.ROOT)['reference']
    assert len(rows) == 1 and rows[0]['owner'] == 'spirited-hamster/tbl'
    row = rows[0]
    symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
    link = next(item for item in model.links if item.owner is symbol.meaning
                and item.type == 'reader' and item.to.key == arguments.TARGET)
    assert arguments.original(row, link)
    assert row['component'] == 'spirited_hamster_paths'


def test_document_binds_the_lookup_delay_slot_and_actual_store():
    text = (repo.ROOT / 'defs/JK08A.spirited-hamster.md').read_text()
    for address in (0x7A090, 0x11FD6, 0x26474, 0x7A230, 0x7A232, 0x21CE0):
        assert f'`{address:08X}`' in text
    assert '`FFFF9818`' in text and '`FFFF2C74`' in text
