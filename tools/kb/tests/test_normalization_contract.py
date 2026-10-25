"""Independent K/U changes and exact sequenced normalization dispositions."""

import pytest

from kb import compile, repo
from kb import normalization_argument_contract as arguments
from kb import normalization_contract as contract
from kb import normalization_matrix as matrix
from kb import normalization_semantics as numeric
from kb.model import SymbolKey


def test_stock_fixture_and_both_private_continuations_restore_exactly():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    assert aliases == []
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    assert [row['address'] for row in boundaries] == [0x627B8, 0x6284A]
    assert all(row['stack_return_offset'] == 28 for row in contract.BOUNDARIES)
    observer = (repo.ROOT / 'tools/sh-elf-run/stock_normalization_invoke.s').read_text()
    assert 'mov.l r0,@(24,r15)' in observer and 'mov.l r0,@(28,r15)' in observer
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


@pytest.mark.parametrize('selected', ('branch-a', 'branch-b'))
def test_separate_u_and_k_changes_propagate_through_the_published_word(selected):
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)
    cases = matrix.cases(declared, image)

    def one(pattern):
        case = next(row for row in cases if row['kind'] == 'coefficient' and row['selected'] == selected
                    and row['pattern'] == pattern and row['coordinate'] == 4096)
        first = numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case), case)
        following = {**case, 'kind': selected}
        return first, numeric.caller(matrix.calibrations(declared, image, following), first['memory'], following)

    first, one_u = one('U-one')
    second, two_u = one('U-two')
    assert first['coefficient'] == second['coefficient'] == 50000
    assert one_u['output'] == 1000 and two_u['output'] == 2000
    first_k, one_k = one('K-one')
    second_k, two_k = one('K-two')
    assert first_k['coefficient'] == 1000 and second_k['coefficient'] == 2000
    assert one_k['output'] == 200 and two_k['output'] == 400
    assert one_k['fault'] == two_k['fault'] == bytes.fromhex('a5c3d2e1')
    _, maximum = one('maximum')
    assert maximum['quotient'] > 65535 and maximum['output'] == 65535


def test_four_exact_dispositions_preserve_the_current_original_claims():
    model = compile.build(repo.ROOT)
    rows = arguments.descriptor(repo.ROOT)['reference']
    assert [row['owner'] for row in rows] == ['brown-jackrabbit/tbl', 'placid-mastiff/tbl',
                                           'tested-dragon/tbl', 'nice-raven/ram']
    for row in rows:
        symbol = model.symbols[SymbolKey('7mfk', row['symbol_kind'], row['address'])]
        link = next(item for item in model.links if item.owner is symbol.meaning
                    and item.type == 'reader' and item.to.key == row['target'])
        assert arguments.original(row, link)


def test_document_names_the_actual_load_product_delay_and_separate_entries():
    text = (repo.ROOT / 'defs/JK08A.normalization.md').read_text()
    for address in (0x627A6, 0x627C2, 0x627C8, 0x1495A, 0x1459A, 0x145CA, 0x627D6, 0x627E0, 0x627E2):
        assert f'`{address:08X}`' in text
    assert '`FFFF2B68`' in text and 'SP+28' in text
