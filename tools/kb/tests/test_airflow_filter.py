"""Bind MAF word copies, bit5 selection, weighted history, and anti-stall."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x870a, bytes.fromhex('1a')),
    (0x3a982, bytes.fromhex('d579644c44006253720c6043062d626de6ff666d32678b00626342118900e20075106043000b0525')),
    (0x3a9aa, bytes.fromhex('4f124f13d070401ed26d614cd56f410072106013062d84510212c820666d72048d1e6013042dd269644d6720e2014218677c07673278051a0247021a352c4519675d3670890734708b0536478b01a002770177ff677d021272046013a001027502654f17000b4f16')),
    (0x3ab68, bytes.fromhex('ffff1048')),
    (0x3ab70, bytes.fromhex('ffff1decffff24600000870a')),
)


def verify_filter(data):
    for address, expected in SLICES:
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x870a, 1) == 26
    assert instruction(0x3a982).value == ('pool', 0x3ab68, 4)
    assert word(0x3ab68, 4) + 12 == 0xffff1054
    assert word(0x3ab68, 4) + 14 == 0xffff1056
    assert instruction(0x3a984).value == ('extu', 8, 4)
    assert instruction(0x3a986).value == ('shl', 1)
    assert instruction(0x3a98e).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert instruction(0x3a990).value == ('extu', 16, 6)
    assert instruction(0x3a992).value == ('const', 0xffffffff)
    assert instruction(0x3a994).value == ('extu', 16, 6)
    assert word(0x3a996) == 0x3267 and instruction(0x3a998).target == 0x3a99c
    assert word(0x3a99c) == 0x4211 and instruction(0x3a99e).target == 0x3a9a2
    assert instruction(0x3a9a0).value == ('const', 0)
    assert word(0x3ab68, 4) + 16 == 0xffff1058
    assert word(0x3ab68, 4) + 18 == 0xffff105a
    assert instruction(0x3a9a6).flow == 'return' and instruction(0x3a9a6).delayed
    assert instruction(0x3a9a8).access == sh2.Access(5, 0, 2, 'store', indexed=True)

    assert word(0x3a9aa) == 0x4f12 and word(0x3a9ac) == 0x4f13
    assert instruction(0x3a9ae).value == ('pool', 0x3ab70, 4)
    assert word(0x3ab70, 4) + 4 == 0xffff1df0
    assert word(0x3ab70, 4) + 6 == 0xffff1df2
    assert instruction(0x3a9b4).value == ('extu', 8, 4)
    assert instruction(0x3a9b8).value == ('shl', 1)
    assert instruction(0x3a9be).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert word(0x3ab74, 4) + 1 == 0xffff2461
    assert instruction(0x3a9c0).access == sh2.Access(5, 1, 1, 'load')
    assert word(0x3a9c4) == 0xc820
    assert instruction(0x3a9c6).value == ('extu', 16, 6)
    assert instruction(0x3a9ca).target == 0x3aa0a and instruction(0x3a9ca).delayed
    assert instruction(0x3a9cc).value == ('copy', 1)
    assert instruction(0x3a9ce).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert instruction(0x3a9d2).value == ('extu', 16, 4)
    assert word(0x3ab78, 4) == 0x870a
    assert instruction(0x3a9d4).access == sh2.Access(2, 0, 1, 'load')
    assert instruction(0x3a9d6).value == ('const', 1)
    assert instruction(0x3a9d8).value == ('shl', 8)
    assert instruction(0x3a9da).value == ('extu', 8, 7)
    assert word(0x3a9dc) == 0x0767 and word(0x3a9de) == 0x3278
    assert word(0x3a9e0) == 0x051a and word(0x3a9e2) == 0x0247
    assert instruction(0x3a9e6).value == ('add', 2)
    assert instruction(0x3a9e8).value == ('shr', 8)
    assert instruction(0x3a9ea).value == ('extu', 16, 5)
    assert word(0x3a9ec) == 0x3670 and instruction(0x3a9ee).target == 0x3aa00
    assert word(0x3a9f0) == 0x3470 and instruction(0x3a9f2).target == 0x3aa00
    assert word(0x3a9f4) == 0x3647 and instruction(0x3a9f6).target == 0x3a9fc
    assert instruction(0x3a9f8).target == 0x3aa00 and instruction(0x3a9f8).delayed
    assert instruction(0x3a9fa).value == ('addi', 1)
    assert instruction(0x3a9fc).value == ('addi', -1)
    assert instruction(0x3a9fe).value == ('extu', 16, 7)
    assert instruction(0x3aa06).target == 0x3aa0c and instruction(0x3aa06).delayed
    assert instruction(0x3aa08).access == sh2.Access(2, 0, 2, 'store', indexed=True)
    assert instruction(0x3aa0a).access == sh2.Access(2, 0, 2, 'store', indexed=True)
    assert word(0x3aa0c) == 0x4f17
    assert instruction(0x3aa0e).flow == 'return' and instruction(0x3aa0e).delayed
    assert word(0x3aa10) == 0x4f16


def test_maf_working_copy_mode_previous_word_weight_and_anti_stall_match_stock():
    verify_filter(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address + offset
                                    for address, expected in SLICES
                                    for offset in range(len(expected))])
def test_changed_maf_copy_flag_weight_history_correction_store_or_return_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_filter(data)


def test_maf_working_copy_bit5_history_and_anti_stall_keep_the_scoped_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    for index, raw, work, output in (
        (10, 0xffff1054, 0xffff1058, 0xffff1df0),
        (11, 0xffff1056, 0xffff105a, 0xffff1df2),
    ):
        assert chain.steps[index]['note'] == (
            f'{work:08x} = uint16({raw:08x}); prev = uint16({output:08x}); k = ROM8[0x0000870a]; '
            f'f = floor((k*{work:08x}+(256-k)*prev)/256); {output:08x} = uint16(f)')
        assert [ref.address for ref in chain.steps[index]['via']] == [0x3a904, 0x3a982, 0x3a9aa]
        working = model.symbols[SymbolKey('7mfk', 'ram', work)]
        filtered = model.symbols[SymbolKey('7mfk', 'ram', output)]
        for symbol in (working, filtered):
            assert symbol.value('width') == 16 and symbol.value('signed') is False
            assert symbol.meaning.props['level'] == 'code'
            assert symbol.value('unit') == 'raw MAF quantity'
        [copy] = [link for link in working.meaning.links if link.type == 'copy']
        assert copy.to is model.meaning_of(SymbolKey('7mfk', 'ram', raw))
        assert copy.stated == {'7mfk'} and [ref.address for ref in copy.props['via']] == [0x3a982]
        [input_link] = [link for link in working.meaning.links if link.type == 'input']
        assert input_link.to is copy.to and input_link.stated == {'7mfk'}
        assert [ref.address for ref in input_link.props['via']] == [0x3a982]
        [copy] = [link for link in filtered.meaning.links if link.type == 'copy']
        assert copy.to is working.meaning and copy.stated == {'7mfk'}
        assert [ref.address for ref in copy.props['via']] == [0x3a9aa]
        assert 'bit5 clear' in copy.props['note']
        [input_link] = [link for link in filtered.meaning.links if link.type == 'input']
        assert input_link.to is working.meaning and input_link.stated == {'7mfk'}
        assert [ref.address for ref in input_link.props['via']] == [0x3a9aa]
        [selector] = [link for link in filtered.meaning.links if link.type == 'selector']
        assert selector.to.key == 'satisfied-bulldog/ram' and selector.slot == 'bit5'
        assert selector.stated == {'7mfk'} and '26/256' in selector.props['note']
        assert [ref.address for ref in selector.props['via']] == [0x3a9aa]

    flags = model.symbols[SymbolKey('7mfk', 'ram', 0xffff2461)]
    assert flags.value('width') == 8 and flags.value('signed') is False
    assert flags.value('unit') == 'bitfield' and flags.meaning.props['level'] == 'code'
    assert 'bit 3' in flags.meaning.props['summary']
    assert any('bit5 selects' in note for note in flags.meaning.props['note'])
    filt = model.meaning_of(SymbolKey('7mfk', 'fn', 0x3a9aa))
    assert filt.props['level'] == 'code'
    thresholds = [link for link in filt.links if link.type == 'threshold']
    assert {link.to.key for link in thresholds} == {'vegan-polecat/ram', 'spiked-dalmatian/ram'}
    for link in thresholds:
        assert link.stated == {'7mfk'} and [ref.address for ref in link.props['via']] == [0x3a9aa]
        assert 'Previous unsigned word' in link.props['note'] and 'weight 230' in link.props['note']
        assert 'unreachable from entry' in link.props['note'] and 'post-arithmetic' in link.props['note']
    assert any('physical time constant remains unresolved' in note for note in filt.props['note'])
