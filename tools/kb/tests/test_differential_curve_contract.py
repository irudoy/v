"""Independent two-curve changes retain exact signed argument identities."""

import pytest

from kb import compile, repo
from kb import differential_curve_argument_contract as arguments
from kb import differential_curve_contract as contract
from kb import differential_curve_matrix as matrix
from kb import differential_curve_semantics as numeric
from kb.model import SymbolKey


def test_bounded_fixture_and_private_return_restore_every_stock_byte():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    assert aliases == []
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    assert contract.BOUNDARY['address'] == 0x44ABC
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


def test_independent_curves_change_the_signed_arguments_and_bounded_result():
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)
    cases = matrix.cases(declared, image)

    def one(pattern, observed=64):
        case = next(row for row in cases if row['pattern'] == pattern and row['coordinate'] == 112
                    and row['observed'] == observed)
        return numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case))

    first, moved_a, moved_b = one('a-low'), one('a-high'), one('b-high')
    assert (first['divisor'], first['dividend'], first['output']) == (80, 7200, 90)
    assert (moved_a['divisor'], moved_a['dividend'], moved_a['output']) == (100, 11200, 112)
    assert (moved_b['divisor'], moved_b['dividend'], moved_b['output']) == (60, 7200, 120)
    assert one('bypass')['opened'] is False and one('bypass')['output'] == 0
    assert one('maximum', 0)['output'] == 255 and one('a-low', 255)['output'] == 0
    assert moved_b['fault'] == bytes.fromhex('a5c3d2e1')


def test_both_exact_dispositions_match_current_reader_claims():
    model = compile.build(repo.ROOT)
    rows = arguments.descriptor(repo.ROOT)['reference']
    assert [row['owner'] for row in rows] == ['unique-spider/tbl', 'dexterous-bobcat/tbl']
    for row in rows:
        symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
        link = next(item for item in model.links if item.owner is symbol.meaning
                    and item.type == 'reader' and item.to.key == row['target'])
        assert arguments.original(row, link)


def test_document_binds_the_actual_call_delay_and_store():
    text = (repo.ROOT / 'defs/JK08A.differential-curve.md').read_text()
    for address in (0x44A58, 0x12738, 0x12748, 0x12930, 0x44A9C, 0x44A9E, 0x44ABA):
        assert f'`{address:08X}`' in text
    assert '`FFFF171D`' in text and '`FFFF16AB`' in text
