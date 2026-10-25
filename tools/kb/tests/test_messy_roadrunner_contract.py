"""The correction preserves the word coordinate, quotient and saturation boundary."""

import pytest

from kb import compile, repo
from kb import messy_roadrunner_argument_contract as arguments
from kb import messy_roadrunner_contract as contract
from kb import messy_roadrunner_matrix as matrix
from kb import messy_roadrunner_semantics as numeric
from kb.model import SymbolKey


def test_observing_return_restores_the_exact_stock_fixture():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    assert aliases == [] and [row['address'] for row in boundaries] == [0x6AEBC]
    restored = bytearray(fixture)
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    for first, last in contract.SPANS:
        assert fixture[first:last] == image[first:last]


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path, flag):
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT / contract.DESCRIPTOR).read_text().replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


def test_byte_product_changes_quotient_and_the_exact_saturation_boundary():
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)

    def one(pattern, base):
        case = dict(index=0, kind='window', entry=matrix.ENTRY, pattern=pattern, axis='strict',
                    word=0x7000, base=base, variant=0, sr=0)
        return numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case), case['word'])

    first, second = one('one', 0), one('two', 0)
    assert first['dividend'] == 64 and first['quotient'] == 0 and first['output'] == 0x7FBE
    assert second['dividend'] == 128 and second['quotient'] == 1 and second['output'] == 0x7FBF
    edge, overflow = one('two', 0x8040), one('two', 0x8041)
    assert edge['output'] == overflow['output'] == 65535
    assert edge['saturated'] is False and overflow['saturated'] is True
    assert edge['fault'] == overflow['fault'] == bytes.fromhex('a5c3d2e1')


def test_exact_disposition_matches_only_the_retained_signed_reader():
    model = compile.build(repo.ROOT)
    row = arguments.descriptor(repo.ROOT)['reference'][0]
    symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
    link = next(item for item in model.links if item.owner is symbol.meaning
                and item.type == 'reader' and item.to.key == arguments.TARGET)
    assert arguments.original(row, link)
    assert row['owner'] == 'messy-roadrunner/tbl' and row['component'] == 'messy_roadrunner_paths'


def test_document_binds_both_actual_stores_and_the_bounded_return():
    text = (repo.ROOT / 'defs/JK08A.messy-roadrunner.md').read_text()
    for at in (0x69374, 0x6AE78, 0x11F3A, 0x11AEF, 0x6AE92, 0x6AE94, 0x6AEA6, 0x6AEBA, 0x6AEBC):
        assert f'{at:08X}' in text
    assert '`FFFF8EC0`' in text and '`FFFF8FDE`' in text
