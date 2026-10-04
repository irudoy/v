"""Bind the combined MAF sum, input widths, wrapping, and signed zero clamp."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x3b252, bytes.fromhex('4f13d04e401ec51fd64e6103c6036403c604340ce038026d341c662d346c44118900e4006043c213000b4f17')),
    (0x3b390, bytes.fromhex('ffff1decffff2330')),
)


def verify_aggregate(data):
    for address, expected in SLICES:
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x3b252) == 0x4f13
    assert instruction(0x3b254).value == ('pool', 0x3b390, 4)
    assert word(0x3b390, 4) == 0xffff1dec
    assert instruction(0x3b258).access == sh2.Access('gbr', 0x3e, 2, 'load')
    assert word(0x3b390, 4) + 0x3e == 0xffff1e2a
    assert instruction(0x3b25a).value == ('pool', 0x3b394, 4)
    assert word(0x3b394, 4) == 0xffff2330
    assert instruction(0x3b25c).value == ('copy', 0)
    assert instruction(0x3b25e).access == sh2.Access('gbr', 12, 4, 'load')
    assert instruction(0x3b260).value == ('copy', 0)
    assert instruction(0x3b262).access == sh2.Access('gbr', 16, 4, 'load')
    assert instruction(0x3b264).value == ('add', 0)
    assert instruction(0x3b266).value == ('const', 0x38)
    assert instruction(0x3b268).access == sh2.Access(6, 0, 2, 'load', indexed=True)
    assert word(0x3b394, 4) + 0x38 == 0xffff2368
    assert instruction(0x3b26a).value == ('add', 1)
    assert instruction(0x3b26c).value == ('extu', 16, 2)
    assert instruction(0x3b26e).value == ('add', 6)
    assert word(0x3b270) == 0x4411
    assert instruction(0x3b272).target == 0x3b276 and not instruction(0x3b272).delayed
    assert instruction(0x3b274).value == ('const', 0)
    assert instruction(0x3b276).value == ('copy', 4)
    assert instruction(0x3b278).access == sh2.Access('gbr', 0x4c, 4, 'store')
    assert word(0x3b390, 4) + 0x4c == 0xffff1e38
    assert instruction(0x3b27a).flow == 'return' and instruction(0x3b27a).delayed
    assert word(0x3b27c) == 0x4f17


def test_combined_maf_longword_wrap_signed_correction_unsigned_addition_and_zero_clamp_match_stock():
    verify_aggregate(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address + offset
                                    for address, expected in SLICES
                                    for offset in range(len(expected))])
def test_changed_maf_sum_width_signedness_branch_store_pool_or_return_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_aggregate(data)


def test_combined_maf_sum_keeps_wrapping_arithmetic_scoped_widths_and_typed_inputs():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    formula = ('s = int32(uint32(ffff1df8+ffff1dfc+int16(ffff1e2a)+uint16(ffff2368))); '
               'ffff1e38 = max(0,s)')
    for index in (14, 15):
        assert chain.steps[index]['note'] == formula
        assert [ref.address for ref in chain.steps[index]['via']] == [0x3b252]
    for address, width, signed, unit in (
        (0xffff1df8, 32, True, 'raw MAF contribution'),
        (0xffff1dfc, 32, True, 'raw MAF contribution'),
        (0xffff1e2a, 16, True, 'raw MAF correction'),
        (0xffff2368, 16, False, 'raw MAF correction'),
        (0xffff1e38, 32, True, 'MAF Factor input counts'),
    ):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.value('width') == width and symbol.value('signed') is signed
        assert symbol.value('unit') == unit and symbol.meaning.props['level'] == 'code'
        assert 'width' not in symbol.meaning.props and 'signed' not in symbol.meaning.props
    aggregate = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1e38))
    inputs = [link for link in aggregate.links if link.type == 'input']
    assert {link.to.key for link in inputs} == {
        'jasper-walrus/ram', 'imposing-auk/ram', 'mindful-goose/ram', 'wondrous-sparrow/ram'}
    for link in inputs:
        assert link.stated == {'7mfk'} and [ref.address for ref in link.props['via']] == [0x3b252]
        assert 'signed' in link.props['note'] and 'wrap' in link.props['note']
    function = model.meaning_of(SymbolKey('7mfk', 'fn', 0x3b252))
    [threshold] = [link for link in function.links if link.type == 'threshold']
    assert threshold.to is aggregate and threshold.stated == {'7mfk'}
    assert 'negative result selects zero' in threshold.props['note']
    assert [ref.address for ref in threshold.props['via']] == [0x3b252]
    auxiliary = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff2368))
    assert any('Static analysis cannot exclude' in note for note in auxiliary.props['note'])
    assert any('physical airflow' in note for note in aggregate.props['note'])
