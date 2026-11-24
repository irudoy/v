"""Bind MAF bank selection, guard modes, arithmetic, and returns to stock."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x87f8, "8779"),
    (0x92be, "8000"),
    (0x3c408, "2fd62fe64f227ffcd21ede1f420b6d4c4d0062e3722e60d3042d65f3d21b420b7e2e60d302ed9321622d32308b0263f173012f3165f1e6ff666d655d356789006653d21360d3720402657f044f266ef6000b6df6"),
    (0x3c474, "03ff"),
    (0x3c48c, "00067188ffff1d34000671d8ffff1018"),
    (0x67188, "d60f8466620c6023c8088b16d70d9016d40d057d8441655d620c421835238b066240662c461835678901a006e255d607900562610725e2aa622c000b6023"),
    (0x671c6, "0418ffff424cffff4558000087f8000092be"),
    (0x671d8, "4f12d624644d9044026d662d0647e6ff666d021a4219420942094209420132668b0062632521000b4f16"),
    (0x6726a, "0418ffff4558"),
)


def verify_scaling(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert instruction(0x3c410).value == ('pool', 0x3c48c, 4)
    assert word(0x3c48c, 4) == 0x67188
    assert instruction(0x3c412).value == ('pool', 0x3c490, 4)
    assert word(0x3c490, 4) + 0x2e == 0xffff1d62
    assert word(0x3c490, 4) + 0x30 == 0xffff1d64
    assert instruction(0x3c416).value == ('extu', 8, 4)
    assert instruction(0x3c418).value == ('shl', 1)
    assert instruction(0x3c420).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert instruction(0x3c424).value == ('pool', 0x3c494, 4)
    assert word(0x3c494, 4) == 0x671d8
    for address in (0x3c414, 0x3c426):
        assert instruction(address).flow == 'call' and instruction(address).delayed
    assert instruction(0x3c42c).access == sh2.Access(14, 0, 2, 'load', indexed=True)
    assert instruction(0x3c42e).value == ('pool', 0x3c474, 2)
    assert word(0x3c474) == 0x03ff
    assert instruction(0x3c434).target == 0x3c43c
    assert instruction(0x3c438).value == ('addi', 1)
    assert instruction(0x3c43a).access == sh2.Access(15, 0, 2, 'store')
    assert instruction(0x3c442).value == ('extu', 16, 5)
    assert word(0x3c444) == 0x3567  # Signed CMP/GT follows the unsigned-word extension.
    assert instruction(0x3c446).target == 0x3c44a
    assert instruction(0x3c44a).value == ('pool', 0x3c498, 4)
    assert word(0x3c498, 4) + 4 == 0xffff101c
    assert word(0x3c498, 4) + 6 == 0xffff101e
    assert instruction(0x3c450).access == sh2.Access(2, 0, 2, 'store', indexed=True)

    assert instruction(0x67188).value == ('pool', 0x671c8, 4)
    assert word(0x671c8, 4) + 6 == 0xffff4252
    assert instruction(0x6718a).access == sh2.Access(6, 6, 1, 'load')
    assert word(0x67190) == 0xc808  # TST #8,R0 selects guard bypass.
    assert instruction(0x67192).target == 0x671c2
    assert instruction(0x67196).value == ('pool', 0x671c6, 2)
    assert word(0x671cc, 4) + word(0x671c6) == 0xffff4970
    assert instruction(0x6719a).access == sh2.Access(7, 0, 2, 'load', indexed=True)
    assert instruction(0x6719e).value == ('extu', 16, 5)
    assert word(0x671d0, 4) == 0x87f8
    assert instruction(0x6719c).access == sh2.Access(4, 1, 1, 'load')
    assert word(0x87f9, 1) << 8 == 0x7900
    assert word(0x87f8, 1) << 8 == 0x8700
    assert word(0x671a4) == 0x3523  # Inclusive lower CMP/GE.
    assert word(0x671ae) == 0x3567  # Strict upper CMP/GT.
    assert instruction(0x671a6).target == instruction(0x671b0).target == 0x671b6
    assert instruction(0x671b2).target == 0x671c2 and instruction(0x671b2).delayed
    assert instruction(0x671b4).value == ('const', 0x55)
    assert word(0x671d4, 4) == 0x92be and word(0x92be) == 0x8000
    assert instruction(0x671bc).access == sh2.Access(7, 0, 2, 'store', indexed=True)
    assert instruction(0x671c0).value == ('extu', 8, 2)

    assert word(0x671d8) == 0x4f12  # STS.L MACL,@-R15.
    assert instruction(0x671dc).value == ('extu', 16, 4)
    assert word(0x6726c, 4) + word(0x6726a) == 0xffff4970
    assert instruction(0x671e0).access == sh2.Access(6, 0, 2, 'load', indexed=True)
    assert instruction(0x671e2).value == ('extu', 16, 2)
    assert word(0x671e4) == 0x0647  # MUL.L R4,R6; both operands are unsigned words.
    assert word(0x671ea) == 0x021a  # STS MACL,R2.
    for address, shift in ((0x671ec, 8), (0x671ee, 2), (0x671f0, 2),
                           (0x671f2, 2), (0x671f4, 1)):
        assert instruction(address).value == ('shr', shift)
    assert word(0x671f6) == 0x3266  # Unsigned CMP/HI clamps at 0xffff.
    assert instruction(0x671f8).target == 0x671fc
    assert instruction(0x671fc).access == sh2.Access(5, 0, 2, 'store')
    for address in (0x3c458, 0x671c2, 0x671fe):
        assert instruction(address).flow == 'return' and instruction(address).delayed
    assert word(0x67200) == 0x4f16  # LDS.L @R15+,MACL in the scaler's return delay slot.


def test_maf_scaling_guard_and_order_match_stock():
    verify_scaling(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address + offset
                                    for address, text in SLICES
                                    for offset in range(0, len(bytes.fromhex(text)), 2)])
@pytest.mark.parametrize('byte', (0, 1))
def test_changed_maf_instruction_literal_bound_or_default_fails(address, byte):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + byte] ^= 1
    with pytest.raises(AssertionError):
        verify_scaling(data)


def test_maf_equations_widths_and_typed_conditions_keep_the_scoped_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    for index, raw, output in ((2, 0xffff1d62, 0xffff101c),
                               (3, 0xffff1d64, 0xffff101e)):
        step = chain.steps[index]
        assert step['note'] == (
            f'{output:08x} = min(65535, floor(uint16({raw:08x})*uint16(ffff4970)/32768))')
        assert [ref.address for ref in step['via']] == [0x3c408, 0x671d8]
        symbol = model.symbols[SymbolKey('7mfk', 'ram', output)]
        assert symbol.value('width') == 16 and symbol.value('signed') is False
        assert symbol.meaning.props['level'] == 'code'
        inputs = [link for link in symbol.meaning.links
                  if link.type == 'input' and '7mfk' in link.stated]
        assert {link.to.key for link in inputs} == {
            model.meaning_of(SymbolKey('7mfk', 'ram', raw)).key, 'satisfied-oarfish/ram'}
        for link in inputs:
            assert link.stated == {'7mfk'}
            assert {ref.address for ref in link.props['via']} == {0x3c408, 0x671d8}
        [selector] = [link for link in symbol.meaning.links if link.type == 'selector']
        assert selector.to is model.meaning_of(SymbolKey('7mfk', 'ram', raw))
        assert selector.slot is None and selector.stated == {'7mfk'}
        assert [ref.address for ref in selector.props['via']] == [0x3c408]
        assert '== 0x03ff' in selector.props['note'] and 'after the scaler returns' in selector.props['note']

    coefficient = model.symbols[SymbolKey('7mfk', 'ram', 0xffff4970)]
    mode = model.symbols[SymbolKey('7mfk', 'ram', 0xffff4252)]
    assert coefficient.value('width') == 16 and coefficient.value('signed') is False
    assert mode.value('width') == 8 and mode.value('signed') is False
    assert coefficient.meaning.props['level'] == mode.meaning.props['level'] == 'code'
    [selector] = [link for link in coefficient.meaning.links if link.type == 'selector']
    assert selector.to is mode.meaning and selector.slot == 'bit3'
    assert selector.stated == {'7mfk'}
    assert [ref.address for ref in selector.props['via']] == [0x67188]
    assert all(text in selector.props['note'] for text in ('0x7900..0x8700', '0x8000', '0x55', '0xaa'))
    guard = model.meaning_of(SymbolKey('7mfk', 'fn', 0x67188))
    [threshold] = [link for link in guard.links if link.type == 'threshold']
    assert threshold.to is coefficient.meaning and threshold.stated == {'7mfk'}
    assert '>= ROM8[0x87f9]<<8' in threshold.props['note']
    assert '<= ROM8[0x87f8]<<8' in threshold.props['note']
    # The JK08A execution proof grants no signedness claim to another layout.
    assert model.symbols[SymbolKey('jk78c', 'ram', 0xffff1024)].value('signed') is None
