"""Bind tooth normalization, sync selection, and fallback word width to stock."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x2911c, "84f42008891c9013008c88088b1896136ddd901206d7021a42290925900e079d900d677d0677021a4229a00f0925"),
    (0x2915c, "905709d59056079d90550975"),
    (0x2914a, "84fb0126012706e084e8555502a202c602c8"),
    (0x2920e, "02a202c602c8"),
    (0x28ed0, "d9548566da54"),
    (0x28ee8, "092684a1c8408902d34e432b0009"),
    (0x28f06, "d846"),
    (0x29020, "ffff128cffff1ff4ffff24c80002a294"),
    (0x29060, "84e6c98080f4"),
    (0x28fea, "9e18400896110844e400900f084484e6cb8080e6"),
    (0x2901e, "84fb"),
    (0x2b7a0, "da34"),
    (0x2b7a4, "905805ac655c6253720132c78b01a002e2ff75016253904d3678666d65230a2446089048460846000b75346890444409440902ae655c44011a24e20235238d020a46a258000950a688ff8967"),
    (0x2b858, "02b8"),
    (0x2b8c0, "964d6eec954c6060cb802600"),
    (0x2b95e, "8501"),
    (0x2b800, "dc1d6163902b52cad41c0a66e00c2f22440b1c6a62039023d5190a2590210a25"),
    (0x2b85e, "02e002c802c6"),
    (0x2b874, "ffff1ff4ffff11d400021ce0ffff2465"),
    (0x21ce0, "2f2620088941620d3020"),
    (0x21dc8, "ffff98180000044e"),
)


def verify_conditions(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x29020, 4) + word(0x2914c) == 0xffff13b2
    assert word(0x29024, 4) + word(0x29158) == 0xffff22ba
    assert word(0x29024, 4) + word(0x2915a) == 0xffff22bc
    assert word(0x29028, 4) + 1 == 0xffff24c9
    assert word(0x2902c, 4) == 0x2a294
    assert word(0x28eec) == 0xc840 and instruction(0x28eee).target == 0x28ef6
    assert (int.from_bytes(data[0x2914a:0x2914c], 'big', signed=True) & 0xffffffff) + 6 == 0xffff8501
    assert word(0x29062) == 0xc980
    assert instruction(0x29064).access == sh2.Access(15, 4, 1, 'store')
    assert int.from_bytes(data[0x2901e:0x29020], 'big', signed=True) + 6 == -0x7aff
    assert word(0x28ffa) == word(0x2b8c8) == 0xcb80
    assert instruction(0x28ffc).access == sh2.Access(14, 6, 1, 'store')
    assert int.from_bytes(data[0x2b95e:0x2b960], 'big', signed=True) & 0xffffffff == 0xffff8501
    assert instruction(0x2b8ca).access == sh2.Access(6, 0, 1, 'store')
    assert instruction(0x2911c).access == sh2.Access(15, 4, 1, 'load')
    assert instruction(0x29120).target == instruction(0x29128).target == 0x2915c
    assert word(0x29126) == 0x8808
    assert word(0x29154) == 21845
    assert instruction(0x2912c).value == ('extu', 16, 13)
    assert instruction(0x2913e).value == ('extu', 16, 7)
    assert word(0x29130) == 0x06d7 and word(0x29140) == 0x0677
    assert instruction(0x29134).value == instruction(0x29144).value == ('shr', 16)
    assert instruction(0x29146).delayed and instruction(0x29146).target == 0x29168
    assert instruction(0x29148).access == sh2.Access(9, 0, 2, 'store', indexed=True)
    assert instruction(0x29166).access == sh2.Access(9, 0, 2, 'store', indexed=True)
    assert word(0x2b874, 4) == word(0x29024, 4)
    assert word(0x2b874, 4) + word(0x2b858) == 0xffff22ac
    assert instruction(0x2b7a6).access == sh2.Access(10, 0, 1, 'load', indexed=True)
    assert instruction(0x2b7ba).value == ('pool', 0x2b858, 2)
    assert instruction(0x2b7c2).access == sh2.Access(10, 0, 1, 'store', indexed=True)
    assert word(0x2b7de) == 0xe202 and word(0x2b7e0) == 0x3523
    assert instruction(0x2b7e2).target == 0x2b7ea and instruction(0x2b7e2).delayed
    assert instruction(0x2b7e6).target == 0x2bc9a
    assert word(0x2b874, 4) + 0x18 == 0xffff200c
    assert instruction(0x2b7ea).access == sh2.Access(10, 0x18, 4, 'load')
    assert word(0x2b7ec) == 0x88ff and instruction(0x2b7ee).target == 0x2b8c0
    assert word(0x2b878, 4) + 0x28 == 0xffff11fc
    assert word(0x2b874, 4) + word(0x2b85e) == 0xffff22d4
    assert word(0x2b874, 4) + word(0x2b860) == 0xffff22bc
    assert word(0x2b874, 4) + word(0x2b862) == 0xffff22ba
    assert instruction(0x2b802).value == ('copy', 6)
    assert instruction(0x2b80c).value == ('const', 12)
    assert instruction(0x2b810).flow == 'call' and instruction(0x2b810).delayed
    assert word(0x2b87c, 4) == 0x21ce0
    assert instruction(0x2b812).access == sh2.Access(12, 0x28, 4, 'store')
    assert instruction(0x2b81a).access == instruction(0x2b81e).access == sh2.Access(
        10, 0, 2, 'store', indexed=True)


def test_tooth_normalization_sync_multiplier_and_fallback_match_stock():
    verify_conditions(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x29120, 0x29122, 0x29126, 0x29128, 0x2912a,
                                    0x2912c, 0x29130, 0x29134, 0x29136, 0x2913a,
                                    0x2913e, 0x29140, 0x29144, 0x29146, 0x29148,
                                    0x2915e, 0x29162, 0x29166, 0x2914a, 0x2914c,
                                    0x29154, 0x29156, 0x29158, 0x2915a, 0x2920e,
                                    0x29210, 0x29212, 0x28ed0, 0x28eec, 0x28eee,
                                    0x28ef2, 0x28f06, 0x29020, 0x29024, 0x29028,
                                    0x2902c, 0x29060, 0x29062, 0x29064, 0x2b7a0,
                                    0x2b802, 0x2b80a, 0x2b80c, 0x2b810, 0x2b812,
                                    0x2b81a, 0x2b81e, 0x2b85e, 0x2b860, 0x2b862,
                                    0x2b874, 0x2b878, 0x2b87c, 0x21ce4, 0x21dc8,
                                    0x28fea, 0x2901e, 0x28ffa, 0x28ffc,
                                    0x2b7a6, 0x2b7c2, 0x2b7e0, 0x2b7e2,
                                    0x2b7e6, 0x2b7ea, 0x2b7ec, 0x2b7ee,
                                    0x2b858, 0x2b8c8, 0x2b8ca, 0x2b95e])
def test_changed_normalization_conditions_arithmetic_and_width_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_conditions(data)


def test_normalization_keeps_the_exact_arithmetic_and_typed_conditions():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'engine_speed')]
    assert ''.join(chain.steps[2]['note'].split()) == 'ffff22bc=ffff22ba'
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff22bc))
    selectors = {(link.to.key, link.slot): link for link in output.links
                 if link.type == 'selector'}
    assert set(selectors) == {('engine_sync_flags/ram', 'bit7'),
                              ('tunneling-doberman/ram', None), ('apc_mode/ram', 'bit6'),
                              ('cam_fallback_previous_capture/ram', None),
                              ('cam_fallback_event_count/ram', None)}
    fixed_point = 'floor(21845*uint16(ffff22ba)/65536)'
    for key in (('engine_sync_flags/ram', 'bit7'), ('tunneling-doberman/ram', None)):
        assert fixed_point in ''.join(selectors[key].props['note'].split())
    assert 'uint16(floor(ffff11fc/12))' in ''.join(output.props['note'][-1].split())
    for key, link in selectors.items():
        layouts = {'7mfk'}
        if key == ('tunneling-doberman/ram', None):
            layouts.update(('jk00c', 'jk00d'))
        assert link.stated == layouts
        address = 0x2b768 if key[0].startswith('cam_fallback_') else 0x28ea2
        assert link.props['via'] == [SymbolKey('7mfk', 'fn', address)]
    copies = [link for link in output.links if link.type == 'copy']
    assert len(copies) == 1 and copies[0].to.key == 'pistachio-porcupine/ram'
    sync = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff8501))
    assert sync.key == 'engine_sync_flags/ram' and sync.props['width'] == 8
    assert [(bit['bit'], bit['name']) for bit in sync.props['bit']] == [(7, 'synchronized')]
    previous = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff200c))
    count = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff22ac))
    assert previous.key == 'cam_fallback_previous_capture/ram' and previous.props['width'] == 32
    assert count.key == 'cam_fallback_event_count/ram' and count.props['width'] == 8
