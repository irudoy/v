"""Returned reciprocal values distinguish zero divisors from zero quotients."""

import pytest

from kb import compile, repo
from kb import reciprocal_curves_argument_contract as arguments
from kb import reciprocal_curves_contract as contract
from kb import reciprocal_curves_matrix as matrix
from kb import reciprocal_curves_semantics as numeric
from kb.model import SymbolKey


def test_bounded_fixture_restores_the_fault_pointer_and_both_returns():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    assert aliases == [dict(address=0x21CD8, original=0xFFFF9818, alias=0x01009818)]
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    assert [row['address'] for row in boundaries] == [0x69628, 0x696CC]
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


@pytest.mark.parametrize('kind', matrix.KINDS)
def test_independent_divisor_changes_and_genuine_zero_fault(kind):
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)
    cases = matrix.cases(declared, image)

    def one(pattern):
        case = next(row for row in cases if row['kind'] == kind and row['pattern'] == pattern
                    and row['axis'] == 'strict' and row['coordinate'] == 64)
        return numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case), case)

    first, second, zero, maximum = (one(pattern) for pattern in ('one', 'two', 'zero', 'maximum'))
    assert first['divisor'] == 1 and first['quotient'] == 256
    assert second['divisor'] == 2 and second['quotient'] == 128
    assert first['dividend'] == second['dividend'] == 256
    assert zero['quotient'] == maximum['quotient'] == 0
    assert zero['fault'] == bytes.fromhex('0000044e')
    assert maximum['fault'] == bytes.fromhex('a5c3d2e1')


def test_both_exact_dispositions_match_the_original_signed_reader_claims():
    model = compile.build(repo.ROOT)
    rows = arguments.descriptor(repo.ROOT)['reference']
    assert [row['owner'] for row in rows] == ['peach-skunk/tbl', 'strange-sturgeon/tbl']
    for row in rows:
        symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
        link = next(item for item in model.links if item.owner is symbol.meaning
                    and item.type == 'reader' and item.to.key == arguments.TARGET)
        assert arguments.original(row, link)


def test_document_binds_actual_call_delay_and_fault_alias():
    text = (repo.ROOT / 'defs/JK08A.reciprocal-curves.md').read_text()
    for address in (0x6961A, 0x237C4, 0x23804, 0x69624, 0x69626, 0x696BC, 0x696C8, 0x696CA, 0x21CD8):
        assert f'`{address:08X}`' in text
    assert '`FFFF9818`' in text and 'control-memory stores' in text
