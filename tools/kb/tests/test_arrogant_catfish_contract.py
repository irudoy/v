"""Conditional lookup products and the explicit divisor bypass."""

import pytest

from kb import compile, repo
from kb import arrogant_catfish_argument_contract as arguments
from kb import arrogant_catfish_contract as contract
from kb import arrogant_catfish_matrix as matrix
from kb import arrogant_catfish_semantics as numeric
from kb.model import SymbolKey


def test_natural_fixture_preserves_the_owned_instructions_and_stock_neighbor():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    assert bytes(restored) == image
    assert contract.ENTRY == 0x4BBEE and contract.SITE == 0x4BCEC
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


def test_selected_curve_changes_both_signed_arguments_and_the_clamped_phase():
    image = repo.images()['JK08A'].path.read_bytes()
    declared = contract.descriptor(repo.ROOT)
    cases = matrix.cases(declared, image)

    def one(pattern):
        case = next(row for row in cases if row['pattern'] == pattern and row['mode'] == 1
                    and row['coordinate'] == 112 and row['numerator'] == 64)
        return numeric.caller(matrix.calibrations(declared, image, case), matrix.memory(case))

    first, second, bypass = one('one'), one('two'), one('128')
    assert first['divisor'] == 127 and second['divisor'] == 126
    assert first['dividend'] == 12600 and second['dividend'] == 12400
    assert first['phase'] == 99 and second['phase'] == 98
    assert bypass['opened'] is False and bypass['phase'] == 0
    assert bypass['fault'] == bytes.fromhex('a5c3d2e1')


def test_exact_disposition_preserves_other_claim_properties_and_ledger_selectors():
    model = compile.build(repo.ROOT)
    rows = arguments.descriptor(repo.ROOT)['reference']
    assert len(rows) == 1 and rows[0]['owner'] == 'arrogant-catfish/tbl'
    row = rows[0]
    symbol = model.symbols[SymbolKey('7mfk', 'tbl', row['address'])]
    link = next(item for item in model.links if item.owner is symbol.meaning
                and item.type == 'reader' and item.to.key == arguments.TARGET)
    assert arguments.original(row, link)
    assert row['component'] == 'arrogant_catfish_paths'


def test_document_binds_the_lookup_delay_slot_and_actual_store():
    text = (repo.ROOT / 'defs/JK08A.arrogant-catfish.md').read_text()
    for address in (0x4BBEE, 0x1244A, 0x26388, 0x4BCEC, 0x4BCEE, 0x21BBC):
        assert f'`{address:08X}`' in text
    assert '`FFFF9818`' in text and '`FFFF15EA`' in text
