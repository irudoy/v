"""Bind both MAF coordinates, word interpolation, and delay-slot publication."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


CURVE_ONE = (
    211,211,211,211,211,211,211,224,249,288,341,410,494,595,715,853,
    1011,1191,1394,1620,1871,2148,2454,2788,3153,3550,3981,4446,4949,5490,6072,6696,
    7363,8076,8837,9647,10509,11424,12396,13424,14513,15664,16879,18161,19512,20935,22431,24004,
    25655,27388,29206,31109,33102,35188,37368,39646,42025,44507,47095,49794,52604,55531,58576,61744,
)
CURVE_TWO = (
    222,222,222,222,222,222,222,231,253,290,341,408,491,592,711,850,
    1009,1189,1391,1618,1869,2146,2451,2784,3148,3544,3972,4436,4936,5473,6051,6670,
    7332,8039,8793,9597,10451,11358,12320,13339,14418,15558,16762,18032,19371,20781,22265,23824,
    25462,27182,28985,30875,32854,34925,37091,39356,41721,44190,46766,49452,52252,55168,58203,61362,
)
SLICES = (
    (0x86f9, bytes.fromhex('dc')),
    (0x8782, bytes.fromhex('00')),
    (0x8b3f, bytes.fromhex('18')),
    (0x141f4, b''.join(point.to_bytes(2, 'big') for point in CURVE_TWO + CURVE_ONE)),
    (0x26410, bytes.fromhex('9008655d35028902d603462be300747e000b6041')),
    (0x26424, bytes.fromhex('3f00')),
    (0x26428, bytes.fromhex('00026a74')),
    (0x26740, bytes.fromhex('3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c')),
    (0x26a74, bytes.fromhex('45014325' * 8 + '63394019200889064500345c61418541620da005601d345c61408441620c601cd601462b0009')),
    (0x26abc, bytes.fromhex('00026740')),
    (0x3a922, bytes.fromhex('e02cd48e02edd78e622d42084208470b652dd68cd48d8166e02e02edd789652d45084508470b655dd687b4e88167')),
    (0x3ab60, bytes.fromhex('0001427400026410ffff1048000141f4')),
    (0x3b320, bytes.fromhex('4f124f13d021401ed621d5226060c90162036050c820894122288b51c413e505660c36538b09e57b36538906d51a626f66507285666ca0390627e585655c36538b3be5fb655c36538937d51362509501a001622c')),
    (0x3b374, bytes.fromhex('ff7b')),
    (0x3b376, bytes.fromhex('365ca0280267')),
    (0x3b3ac, bytes.fromhex('ffff1e6000008b3f000086f900008782')),
    (0x3b3bc, bytes.fromhex('2228890cd5096250d509622c84580207001a4021402140214021a0014021e000d50481574f17000b4f16')),
    (0x3b3e8, bytes.fromhex('00008782ffff56b2ffff1e1c')),
)


def verify_transfer(data):
    for address, expected in SLICES:
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert len(CURVE_ONE) == len(CURVE_TWO) == 64
    assert instruction(0x3a922).value == ('const', 0x2c)
    assert instruction(0x3a924).value == ('pool', 0x3ab60, 4)
    assert word(0x3ab60, 4) == 0x14274
    assert instruction(0x3a926).access == sh2.Access(14, 0, 2, 'load', indexed=True)
    assert instruction(0x3a92a).value == ('extu', 16, 2)
    assert instruction(0x3a92c).value == instruction(0x3a92e).value == ('shl', 2)
    assert instruction(0x3a930).flow == 'call' and instruction(0x3a930).delayed
    assert instruction(0x3a932).value == ('extu', 16, 2)
    assert word(0x3ab64, 4) == 0x26410
    assert instruction(0x3a934).value == ('pool', 0x3ab68, 4)
    assert word(0x3ab68, 4) + 0xc == 0xffff1054
    assert instruction(0x3a938).access == sh2.Access(6, 0xc, 2, 'store')
    assert instruction(0x3a93a).value == ('const', 0x2e)
    assert instruction(0x3a93c).access == sh2.Access(14, 0, 2, 'load', indexed=True)
    assert word(0x3ab6c, 4) == 0x141f4
    assert instruction(0x3a940).value == ('extu', 16, 2)
    assert instruction(0x3a942).value == instruction(0x3a944).value == ('shl', 2)
    assert instruction(0x3a946).flow == 'call' and instruction(0x3a946).delayed
    assert instruction(0x3a948).value == ('extu', 16, 5)
    assert instruction(0x3a94a).value == ('pool', 0x3ab68, 4)
    assert instruction(0x3a94c).flow == 'call' and instruction(0x3a94c).target == 0x3b320
    assert instruction(0x3a94c).delayed
    assert word(0x3ab68, 4) + 0xe == 0xffff1056
    assert instruction(0x3a94e).access == sh2.Access(6, 0xe, 2, 'store')

    assert instruction(0x26410).value == ('pool', 0x26424, 2)
    assert word(0x26424) == 63 * 256
    assert instruction(0x26412).value == ('extu', 16, 5)
    assert word(0x26414) == 0x3502 and instruction(0x26416).target == 0x2641e
    assert word(0x26428, 4) == 0x26a74
    assert instruction(0x2641a).flow == 'jump' and instruction(0x2641a).delayed
    assert instruction(0x2641c).value == ('const', 0)
    assert instruction(0x2641e).value == ('addi', 126)
    assert instruction(0x26420).flow == 'return' and instruction(0x26420).delayed
    assert instruction(0x26422).access == sh2.Access(4, 0, 2, 'load')
    for address in range(0x26a74, 0x26a94, 4):
        assert instruction(address).value == ('shr', 1)
        assert word(address + 2) == 0x4325
    assert word(0x26a94) == 0x6339  # SWAP.W R3,R3 aligns the Q0.16 fraction.
    assert instruction(0x26a96).value == ('shr', 8)
    assert instruction(0x26a9a).target == 0x26aaa
    assert instruction(0x26a9c).value == ('shl', 1)
    assert instruction(0x26aa0).access == sh2.Access(4, 0, 2, 'load')
    assert instruction(0x26aa2).access == sh2.Access(4, 2, 2, 'load')
    assert instruction(0x26aa4).value == ('extu', 16, 0)
    assert instruction(0x26aa8).value == ('extu', 16, 1)
    assert word(0x26abc, 4) == 0x26740
    assert instruction(0x26740).target is None and word(0x26740) == 0x3202
    assert instruction(0x26742).target == 0x2675c
    assert word(0x26748) == 0x011a and word(0x2674e) == 0x411a
    assert word(0x2675e) == 0x011a and word(0x26764) == 0x411a

    assert word(0x86f9, 1) & 0x20 == 0 and word(0x8b3f, 1) & 1 == 0
    assert instruction(0x3b336).target == 0x3b3bc
    assert instruction(0x3b3be).target == 0x3b3da
    assert instruction(0x3b3da).value == ('const', 0)
    assert word(0x3b3f0, 4) + 0xe == 0xffff1e2a
    assert instruction(0x3b3de).access == sh2.Access(5, 0xe, 2, 'store')
    assert instruction(0x3b3e2).flow == 'return' and instruction(0x3b3e2).delayed


def test_maf_coordinate_word_curve_and_both_publications_match_stock():
    verify_transfer(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address + offset
                                    for address, expected in SLICES
                                    for offset in range(len(expected))])
def test_changed_maf_coordinate_curve_word_width_delay_slot_or_return_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_transfer(data)


def test_maf_indices_lookups_last_cell_and_unsigned_stores_keep_the_scoped_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    index_via = [0x3a904, 0x26410, 0x26a60]
    lookup_via = index_via + [0x26740]
    for index, source, output, table in (
        (6, 0xffff1e48, 0xffff1054, 0x14274),
        (7, 0xffff1e4a, 0xffff1056, 0x141f4),
    ):
        assert chain.steps[index]['note'] == (
            f'x = uint16({source:08x}<<4); to = min(63,x>>8); frac = uint16(x<<8)')
        assert [ref.address for ref in chain.steps[index]['via']] == index_via
        lookup = chain.steps[index + 2]
        assert lookup['note'] == (
            f'{output:08x} = uint16(lookup(0x{table:08x},uint16({source:08x}<<4)))')
        assert [ref.address for ref in lookup['via']] == lookup_via
        symbol = model.symbols[SymbolKey('7mfk', 'ram', output)]
        assert symbol.value('width') == 16 and symbol.value('signed') is False
        assert symbol.meaning.props['level'] == 'code'
        assert symbol.value('unit') == 'raw MAF quantity'
        [input_link] = [link for link in symbol.meaning.links if link.type == 'input']
        assert input_link.to is model.meaning_of(SymbolKey('7mfk', 'ram', source))
        assert input_link.stated == {'7mfk'}
        assert [ref.address for ref in input_link.props['via']] == lookup_via
        [lookup_link] = [link for link in symbol.meaning.links if link.type == 'lookup']
        assert lookup_link.to is model.meaning_of(SymbolKey('7mfk', 'tbl', table))
        assert lookup_link.stated == {'7mfk'}
        assert [ref.address for ref in lookup_link.props['via']] == lookup_via
        assert 'sign' not in lookup_link.props
        table_meaning = lookup_link.to
        assert table_meaning.props['level'] == 'code'
        assert table_meaning.props['scale_level'] == 'code'
        assert table_meaning.props['scale'] == 'x*0.0041015625'
        [index_link] = [link for link in table_meaning.links if link.type == 'index']
        assert index_link.to is input_link.to and index_link.stated == {'7mfk'}
        assert [ref.address for ref in index_link.props['via']] == index_via
        assert '16 input counts' in index_link.props['note']

    wrapper = model.meaning_of(SymbolKey('7mfk', 'fn', 0x26410))
    signature = wrapper.props['interp']
    assert signature == {'access': 'implicit', 'kernel': SymbolKey('7mfk', 'fn', 0x26a60),
                         'offset': 0x14, 'cols': 64, 'step': 256}
    thresholds = [link for link in wrapper.links if link.type == 'threshold']
    assert {link.to.key for link in thresholds} == {'ginger-stingray/ram', 'careful-penguin/ram'}
    for link in thresholds:
        assert link.stated == {'7mfk'} and 'sign-extended' in link.props['note']
        assert '0x3f00' in link.props['note'] and 'word-cell branch' in link.props['note']
        assert [ref.address for ref in link.props['via']] == [0x26410]
    coordinator = model.meaning_of(SymbolKey('7mfk', 'fn', 0x3a904))
    assert coordinator.props['level'] == 'code'
    assert any('Bank 2 is stored in the BSR' in note for note in coordinator.props['note'])
