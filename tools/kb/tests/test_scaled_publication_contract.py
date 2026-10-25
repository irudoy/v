"""Paired scaled outputs retain exact stores and both original dispositions."""

import pytest

from kb import compile, repo
from kb import scaled_publication_contract as contract
from kb import scaled_publication_matrix as matrix
from kb import scaled_publication_output_contract as outputs
from kb import scaled_publication_semantics as numeric
from kb.model import SymbolKey


def test_bounded_fixtures_restore_every_stock_byte_and_both_returns():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    for row in aliases:
        restored[row['address']:row['address'] + 4] = row['original'].to_bytes(4, 'big')
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    assert [row['address'] for row in boundaries] == [0x7A796, 0x7A982]
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


@pytest.mark.parametrize('kind,address', (('signed', 0x1210), ('unsigned', 0x1248)))
def test_zero_exact_quotient_and_upper_word_input_keep_the_complete_footprint(kind, address):
    for value, output in ((0, 0), (800, 727), (65535, 59554)):
        before = matrix.memory(dict(value=value))
        result = numeric.caller(before, kind, value)
        expected = bytearray(before)
        expected[address:address + 2] = output.to_bytes(2, 'big')
        if kind == 'unsigned':
            expected[0x35CC:0x35CE] = value.to_bytes(2, 'big')
        assert result['memory'] == bytes(expected)
        assert result['divisor'] == 800 and result['dividend'] == value * 727
        assert result['fault'] == bytes.fromhex('a5c3d2e1')


def test_both_exact_dispositions_match_the_current_original_reader_claims():
    model = compile.build(repo.ROOT)
    rows = outputs.descriptor(repo.ROOT)['reference']
    assert [row['owner'] for row in rows] == ['jasper-taipan/ram', 'snobbish-bird/ram']
    for row in rows:
        symbol = model.symbols[SymbolKey('7mfk', 'ram', row['address'])]
        link = next(item for item in model.links if item.owner is symbol.meaning
                    and item.type == 'reader' and item.to.key == row['target'])
        assert outputs.original(row, link)


def test_document_binds_the_two_actual_call_delay_and_store_paths():
    text = (repo.ROOT / 'defs/JK08A.scaled-publication.md').read_text()
    for address in (0x7A778, 0x7A784, 0x7A786, 0x7A794, 0x7A968, 0x7A976, 0x7A978, 0x7A980):
        assert f'`{address:08X}`' in text
    assert '`FFFF1210`' in text and '`FFFF1248`' in text
