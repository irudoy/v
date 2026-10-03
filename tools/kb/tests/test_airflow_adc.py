"""Bind both MAF ADC word inputs, unsigned shifts, and word stores to stock."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x28098, "e4f8d5d244188542600d40094009400981558543600d40094009400981548544d5cb620d420942094209e02e0525e026024de030622d420942094209000b0525"),
    (0x283e4, "ffff362cffff1d34"),
)


def verify_adc(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert instruction(0x28098).value == ('const', 0xfffffff8)
    assert instruction(0x2809c).value == ('shl', 8)
    assert (0xfffffff8 << 8) & 0xffffffff == 0xfffff800
    assert instruction(0x280b6).access == sh2.Access(4, 8, 2, 'load')
    assert instruction(0x280ba).value == ('extu', 16, 0)
    assert instruction(0x280c6).value == ('const', 0x26)
    assert instruction(0x280c8).access == sh2.Access(4, 0, 2, 'load', indexed=True)
    assert instruction(0x280cc).value == ('extu', 16, 2)
    for address in (0x280bc, 0x280be, 0x280c0, 0x280ce, 0x280d0, 0x280d2):
        assert instruction(address).value == ('shr', 2)
    assert instruction(0x280b8).value == ('pool', 0x283e8, 4)
    assert word(0x283e8, 4) + 0x2e == 0xffff1d62
    assert word(0x283e8, 4) + 0x30 == 0xffff1d64
    assert instruction(0x280c2).value == ('const', 0x2e)
    assert instruction(0x280ca).value == ('const', 0x30)
    assert instruction(0x280c4).access == instruction(0x280d6).access == sh2.Access(
        5, 0, 2, 'store', indexed=True)
    assert instruction(0x280d4).flow == 'return' and instruction(0x280d4).delayed


def test_maf_adc_unsigned_word_sources_and_shifts_match_stock():
    verify_adc(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [*range(0x28098, 0x280d8, 2), 0x283e4, 0x283e8])
def test_changed_adc_base_channels_width_shifts_or_stores_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_adc(data)


def test_maf_adc_notes_and_layout_widths_bind_both_banks():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    for index, register, sample in ((0, 0xfffff808, 0xffff1d62),
                                     (1, 0xfffff826, 0xffff1d64)):
        assert chain.steps[index]['note'] == f'{sample:08x} = uint16({register:08x}) >> 6'
        source = model.symbols[SymbolKey('7mfk', 'reg', register)]
        output = model.symbols[SymbolKey('7mfk', 'ram', sample)]
        assert source.value('width') == output.value('width') == 16
        assert source.value('signed') is output.value('signed') is False
        links = [link for link in output.meaning.links if link.type == 'input'
                 and link.to is source.meaning]
        assert len(links) == 1 and links[0].stated == {'7mfk'}
        assert [ref.address for ref in links[0].props['via']] == [0x28098]
