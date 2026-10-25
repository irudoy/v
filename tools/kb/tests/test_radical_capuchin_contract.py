"""A threshold changes a Boolean while timer/10 remains independent."""

import pytest
from kb import compile, repo
from kb import radical_capuchin_contract as contract
from kb import radical_capuchin_matrix as matrix
from kb import radical_capuchin_semantics as numeric
from kb import radical_capuchin_output_contract as output
from kb.model import SymbolKey


def test_exact_alias_and_observing_return_restore_the_stock_fixture():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    assert aliases == [dict(address=0x61730, original=0xFFFF267A, alias=0x0100267A)]
    assert [row['address'] for row in boundaries] == [0x61630]
    restored = bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path, flag):
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT / contract.DESCRIPTOR).read_text().replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


def test_threshold_changes_without_a_change_to_either_divider_operand():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()

    def one(pattern, timer=10):
        case = dict(index=0, kind='window', entry=matrix.ENTRY, pattern=pattern, axis='strict',
                    coordinate=112, timer=timer, variant=0, sr=0)
        return numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case))

    first, second = one('zero'), one('one')
    assert first['lookup'] == 0 and second['lookup'] == 1
    assert first['dividend'] == second['dividend'] == 10
    assert first['divisor'] == second['divisor'] == 10
    assert first['quotient'] == second['quotient'] == 1
    assert first['output'] == 0 and second['output'] == 1
    assert one('one', 19)['output'] == 1 and one('one', 20)['output'] == 0


def test_repeated_stock_knots_preserve_natural_equal_and_endpoint_reads():
    table, axis = bytes(range(9)), bytes([50]) * 8
    assert numeric.curve(table, axis, 49) == dict(value=0, reads=(1, 0))
    assert numeric.curve(table, axis, 50) == dict(value=7, reads=(8, 7))
    assert numeric.curve(table, axis, 255) == dict(value=7, reads=(8, 7))


def test_exact_output_disposition_matches_the_original_reader_and_output_owner():
    model = compile.build(repo.ROOT)
    row = output.descriptor(repo.ROOT)['reference'][0]
    symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
    link = next(item for item in model.links if item.owner is symbol.meaning
                and item.type == 'reader' and item.to.key == 'pompous-firefly/fn')
    assert output.original(row, link)
    assert model.symbols[SymbolKey('7mfk', 'ram', row['RAM_address'])].meaning.key == row['RAM_owner']
