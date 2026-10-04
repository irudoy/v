"""Bind the cached BFS context, unsigned divider, byte cap, and publication."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x9534, bytes.fromhex('6a5a')),
    (0x21ce0, bytes.fromhex('2f2620088941620d30208b440019401830168b0b' + '3104'*8 + '412462f6000b601c2f36631d40184129' + '3104'*16 + '621d212a322e4228313c' + '3104'*16 + '4124601d302c63f6000b62f6d117d2172122e000000b62f60019621d422841294224' + '31044224'*16 + '6023000b62f6')),
    (0x21dc8, bytes.fromhex('ffff98180000044e')),
    (0x3bc76, bytes.fromhex('d95e')),
    (0x3bcbe, bytes.fromhex('8591650d3652890236c08b007601606381a2606dd34f401980a2c501660d853d640d44083462890360d3d245a003cb8060d3c97fd243d64280238463c8800029d640ca01640c8464c8800029ca01660c34608904d63bd43a8465cb208045')),
    (0x3bd1c, bytes.fromhex('d63d6153410841086261410841004b0b602de6ff666c3066890ed62ed53685616651610dd2354108410841084100656d420b6053a0016203e2ff6623d22d2260')),
    (0x3bdf0, bytes.fromhex('ffff1024')),
    (0x3be10, bytes.fromhex('ffff10480000953400021ce0')),
)


def verify_normalization(data):
    for address, expected in SLICES:
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x9534) == 27226
    assert instruction(0x3bc76).value == ('pool', 0x3bdf0, 4)
    assert instruction(0x3bc76).dest == 9 and word(0x3bdf0, 4) + 2 == 0xffff1026
    assert instruction(0x3bcbe).access == sh2.Access(9, 2, 2, 'load')
    assert instruction(0x3bcc0).dest == 5 and instruction(0x3bcc0).value == ('extu', 16, 0)
    for address in range(0x3bcc2, 0x3bd1c, 2):
        assert 5 not in instruction(address).writes
        assert instruction(address).flow != 'call'
    assert instruction(0x3bd1c).value == ('pool', 0x3be14, 4)
    assert word(0x3be14, 4) == 0x9534
    assert instruction(0x3bd1e).value == ('copy', 5)
    for address in (0x3bd20, 0x3bd22, 0x3bd26):
        assert instruction(address).value == ('shl', 2)
    assert instruction(0x3bd28).value == ('shl', 1)
    assert instruction(0x3bd24).access == sh2.Access(6, 0, 2, 'load')
    assert word(0x3bd2a) == 0x4b0b and instruction(0x3bd2a).delayed
    assert instruction(0x3bd2c).value == ('extu', 16, 2)
    assert instruction(0x3bd2e).value == ('const', 0xffffffff)
    assert instruction(0x3bd30).value == ('extu', 8, 6)
    assert word(0x3bd32) == 0x3066
    assert instruction(0x3bd34).target == 0x3bd54
    assert instruction(0x3bd36).value == ('pool', 0x3bdf0, 4)
    assert instruction(0x3bd3a).access == sh2.Access(6, 2, 2, 'load')
    assert instruction(0x3bd3c).access == sh2.Access(5, 0, 2, 'load')
    assert instruction(0x3bd3e).value == ('extu', 16, 0)
    assert instruction(0x3bd40).value == ('pool', 0x3be18, 4)
    assert word(0x3be18, 4) == 0x21ce0
    for address in (0x3bd42, 0x3bd44, 0x3bd46):
        assert instruction(address).value == ('shl', 2)
    assert instruction(0x3bd48).value == ('shl', 1)
    assert instruction(0x3bd4a).value == ('extu', 16, 6)
    assert word(0x3bd4c) == 0x420b and instruction(0x3bd4c).delayed
    assert instruction(0x3bd4e).value == ('copy', 5)
    assert instruction(0x3bd50).target == 0x3bd56 and instruction(0x3bd50).delayed
    assert instruction(0x3bd52).value == ('copy', 0)
    assert instruction(0x3bd54).value == ('const', 0xffffffff)
    assert instruction(0x3bd58).value == ('pool', 0x3be10, 4)
    assert word(0x3be10, 4) == 0xffff1048
    assert instruction(0x3bd5a).access == sh2.Access(2, 0, 1, 'store')
    assert word(0x21dc8, 4) == 0xffff9818 and word(0x21dcc, 4) == 0x44e


def test_normalized_bfs_cached_word_division_byte_cap_and_store_match_stock():
    verify_normalization(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address + offset
                                    for address, expected in SLICES
                                    for offset in range(len(expected))])
def test_changed_normalized_load_cache_shift_divider_reference_cap_store_or_pool_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_normalization(data)


def test_normalized_bfs_keeps_cached_cap_zero_reference_and_fixed_scalar_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    formula = 'ffff1048 = min(255,floor(uint16(ffff1026)*128/ROM16[0x00009534]))'
    for index in (25, 26):
        assert chain.steps[index]['note'] == formula
        assert [ref.address for ref in chain.steps[index]['via']] == [0x3b75c]
    bfs = model.symbols[SymbolKey('7mfk', 'ram', 0xffff1026)]
    live = model.symbols[SymbolKey('7mfk', 'ram', 0xffff1048)]
    for symbol, width, unit in ((bfs, 16, 'ms'), (live, 8, 'normalized BFS Q7')):
        assert symbol.value('width') == width and symbol.value('signed') is False
        assert symbol.value('unit') == unit and symbol.meaning.props['level'] == 'code'
    [source] = [link for link in live.meaning.links if link.type == 'input']
    assert source.to is bfs.meaning and source.stated == {'7mfk'}
    assert [ref.address for ref in source.props['via']] == [0x3b75c]
    assert 'coherent cache/RAM' in source.props['note']
    reference = model.meaning_of(SymbolKey('7mfk', 'tbl', 0x9534))
    assert reference.props['access'] == 'direct-scalar' and reference.props['storage'] == 'uint16'
    assert not any(link.type == 'index' and link.to is bfs.meaning for link in reference.links)
    assert reference.props['scale_level'] == 'candidate'
    [lookup] = [link for link in live.meaning.links if link.type == 'lookup']
    assert lookup.to is reference and lookup.stated == {'7mfk'}
    assert [ref.address for ref in lookup.props['via']] == [0x3b75c]
    assert 'fixed ROM address' in lookup.props['note'] and 'zero reference' in lookup.props['note']
    producer = model.meaning_of(SymbolKey('7mfk', 'fn', 0x3b75c))
    thresholds = [link for link in producer.links if link.type == 'threshold']
    assert {link.to.key for link in thresholds} == {'benign-cassowary/ram', 'precise-nuthatch/tbl'}
    for link in thresholds:
        assert link.stated == {'7mfk'} and [ref.address for ref in link.props['via']] == [0x3b75c]
    assert any('stock coherent cached word' in link.props['note'] for link in thresholds)
    assert any('records 0x44e' in link.props['note'] for link in thresholds)
