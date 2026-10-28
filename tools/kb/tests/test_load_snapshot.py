"""Bind BFS history, the length-selected block copier, and the load byte view."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x20f04, bytes.fromhex('d481d6826241d1822621d6826261d6822421d282460be01c')),
    (0x2110c, bytes.fromhex('ffff1024ffff1028ffff102cffff102600022104ffff1048')),
    (0x22104, bytes.fromhex('2f36d302033e70fc432b032e')),
    (0x22110, bytes.fromhex('00022158')),
    (0x2213a, bytes.fromhex('5025113653241105502311345322110350211132632211012132000b63f6')),
    (0x22174, bytes.fromhex('0002213a')),
)


def verify_snapshot(data):
    for address, expected in SLICES:
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    for at, pool, address in ((0x20f04, 0x2110c, 0xffff1024),
                              (0x20f06, 0x21110, 0xffff1028),
                              (0x20f0a, 0x21114, 0xffff102c),
                              (0x20f0e, 0x21118, 0xffff1026),
                              (0x20f12, 0x2111c, 0x22104),
                              (0x20f16, 0x21120, 0xffff1048)):
        assert instruction(at).value == ('pool', pool, 4)
        assert word(pool, 4) == address
    assert instruction(0x20f08).access == sh2.Access(4, 0, 2, 'load')
    assert instruction(0x20f0c).access == sh2.Access(6, 0, 2, 'store')
    assert instruction(0x20f10).access == sh2.Access(6, 0, 2, 'load')
    assert instruction(0x20f14).access == sh2.Access(4, 0, 2, 'store')
    assert word(0x20f18) == 0x460b and instruction(0x20f18).delayed
    assert instruction(0x20f1a).value == ('const', 28)
    assert word(0x22104) == 0x2f36
    assert instruction(0x22106).value == ('pool', 0x22110, 4)
    assert word(0x22110, 4) + 28 == 0x22174
    assert instruction(0x22108).access == sh2.Access(3, 0, 4, 'load', indexed=True)
    assert instruction(0x2210a).value == ('addi', -4)
    assert word(0x2210c) == 0x432b and instruction(0x2210c).delayed
    assert instruction(0x2210e).access == sh2.Access(2, 0, 4, 'load', indexed=True)
    assert word(0x22174, 4) == 0x2213a
    for at, offset in ((0x2213c, 24), (0x22140, 20), (0x22144, 16),
                       (0x22148, 12), (0x2214c, 8), (0x22150, 4), (0x22152, 0)):
        assert instruction(at).access == sh2.Access(1, offset, 4, 'store')
    assert instruction(0x22154).flow == 'return' and instruction(0x22154).delayed
    assert word(0x22156) == 0x63f6


def test_load_snapshot_history_length_dispatch_delay_load_and_all_seven_word_stores_match_stock():
    verify_snapshot(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address + offset
                                    for address, expected in SLICES
                                    for offset in range(len(expected))])
def test_changed_load_snapshot_endpoints_length_dispatch_delay_store_or_return_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_snapshot(data)


def test_load_snapshot_keeps_byte_view_word_history_and_exact_copy_links():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    assert chain.steps[27]['note'] == 'ffff102c = uint8(ffff1048)'
    assert [ref.address for ref in chain.steps[27]['via']] == [0x20dfe]
    for output, source, width, unit, layouts in (
        (0xffff1024, 0xffff1026, 16, 'ms*2048', {'7mfk'}),
        (0xffff1028, 0xffff1024, 16, 'ms*2048', {'7mfk'}),
        (0xffff102c, 0xffff1048, 8, 'percent', {'7mfk', 'jk00c', 'jk00d', 'jk78c'}),
    ):
        target = model.symbols[SymbolKey('7mfk', 'ram', output)]
        assert target.value('width') == width and target.value('signed') is False
        assert target.value('unit') == unit and target.meaning.props['level'] == 'code'
        [copy] = [link for link in target.meaning.links if link.type == 'copy']
        assert copy.to is model.meaning_of(SymbolKey('7mfk', 'ram', source))
        assert copy.stated == layouts and [ref.address for ref in copy.props['via']] == [0x20dfe]
        assert 'hardware atomicity' in copy.props['note']
        [input_link] = [link for link in target.meaning.links
                        if link.type == 'input' and link.to is copy.to]
        assert input_link.stated == {'7mfk'}
        assert [ref.address for ref in input_link.props['via']] == [0x20dfe]
    snapshot = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff102c))
    assert any('without a direct MOV.B store' in note for note in snapshot.props['note'])
    history = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1028))
    assert any('hardware-validation target' in note for note in history.props['note'])
    scheduler = model.meaning_of(SymbolKey('7mfk', 'fn', 0x20dfe))
    assert any('only 00020f04..00020f1a' in note for note in scheduler.props['note'])
