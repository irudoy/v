"""Bind RPM row arguments, axis element widths, and fraction scaling to stock."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x26984, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be500"),
    (0x269c4, "6343014c611c4108315089183156891233408914351845286343330c61308431611c600c4f22d20730184008420b61534f26000b650374ff441189e2e400000be500"),
    (0x26c78, "200889462f26e20000194124" + "32044124" * 32 + "62f6000b6013000be000"),
    (0x269c0, "00026c78"),
    (0x26a08, "00026c78"),
    (0x11cf0, "08101820283840485860687880848c94"),
    (0x11ece, "080c1018202830384048586878808894"),
    (0x14b4a, "0080010001800200028003000380040004800500058006000680078008800980"),
    (0x2cc8c, "d39f80f3e0200e3dd49ed59fd69fd2a0420b67ed"),
    (0x2cf0c, "ffff11d40000a29a00011cf000011d4c000261f0"),
    (0x3c092, "d96d6073"),
    (0x3c248, "ffff11d4"),
    (0x3c0c4, "e02065200c9d625c02676ccd"),
    (0x3c284, "e05cd43d00ac67c3d53cd63dd23d420b80f3"),
    (0x3c37c, "0000a29a00011cf000011d4c000261f0"),
    (0x495e4, "d82060a0d43280f3e020028ddc31de32672ddd3265c34d0b66e3c97fd43080fc65c360a066e380f3e020028d4d0b672d"),
    (0x49668, "ffff119c"),
    (0x496b4, "00009a1a00011ece00011ebe0002623000009b1a"),
    (0x4e1d2, "d09f401e"),
    (0x4e450, "00011ebe"),
    (0x4e290, "db77622cd47ae010d3760f24602e80f3e020051202bd75100612672d430b1f33"),
    (0x4e304, "db5a60a0d45d80f3e020051202bd75100612d357672d430b1f33"),
    (0x4e470, "ffff119c00026230ffff128cffff102c0000991a"),
    (0x6597e, "d7480d25602381f1857dd454d555d255420b670d"),
    (0x65aa0, "ffff119c"),
    (0x65adc, "00010b8e00014b4a000262a8"),
    (0x261f0, "4f222f46677d60536573d70c470be40f"),
    (0x2622c, "000269c4"),
    (0x26230, "4f222f46677d60536573d70c470be40f"),
    (0x2626c, "000269c4"),
    (0x262a8, "4f222f46677d60536573d70a470be41e"),
    (0x262dc, "00026984"),
)


def verify_arguments(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert instruction(0x26986).access == sh2.Access(4, 0, 2, 'load', indexed=True)
    assert instruction(0x26988).value == ('extu', 16, 1)
    assert instruction(0x269c6).access == sh2.Access(4, 0, 1, 'load', indexed=True)
    assert instruction(0x269c8).value == ('extu', 8, 1)
    assert instruction(0x269ca).value == instruction(0x269ee).value == ('shl', 2)
    assert instruction(0x269b4).value == ('addi', -2)
    assert instruction(0x269fa).value == ('addi', -1)
    for address, pool, last_offset, core in ((0x261f0, 0x2622c, 15, 0x269c4),
                                            (0x26230, 0x2626c, 15, 0x269c4),
                                            (0x262a8, 0x262dc, 30, 0x26984)):
        assert instruction(address + 4).value == ('extu', 16, 7)
        assert instruction(address + 6).value == ('copy', 5)
        assert instruction(address + 8).value == ('copy', 7)
        assert word(pool, 4) == core
        assert instruction(address + 12).flow == 'call'
        assert instruction(address + 14).value == ('const', last_offset)
    assert word(0x2cf0c, 4) + 0x20 == word(0x3c248, 4) + 0x20 == 0xffff11f4
    assert instruction(0x2cc92).access == sh2.Access(3, 0, 2, 'load', indexed=True)
    assert instruction(0x2cc9c).flow == 'call'
    assert instruction(0x2cc9e).value == ('extu', 16, 14)
    assert instruction(0x3c0c8).access == sh2.Access(9, 0, 2, 'load', indexed=True)
    assert instruction(0x3c0ce).value == ('extu', 16, 12)
    assert instruction(0x3c28a).value == ('copy', 12)
    assert word(0x2cf14, 4) == word(0x3c380, 4) == 0x11cf0
    assert word(0x2cf1c, 4) == word(0x3c388, 4) == 0x261f0
    assert word(0x49668, 4) + 0x20 == 0xffff11bc
    assert instruction(0x495ee).access == instruction(0x4960e).access == sh2.Access(
        8, 0, 2, 'load', indexed=True)
    assert instruction(0x495f4).value == instruction(0x49612).value == ('extu', 16, 2)
    assert word(0x496b8, 4) == 0x11ece and word(0x496c0, 4) == 0x26230
    assert instruction(0x4e1d2).value == ('pool', 0x4e450, 4)
    assert word(0x4e450, 4) + 0x10 == 0x11ece
    assert word(0x4e470, 4) + 0x20 == 0xffff11bc
    assert word(0x4e474, 4) == 0x26230 and word(0x4e480, 4) == 0x991a
    assert instruction(0x4e2a4).access == instruction(0x4e310).access == sh2.Access(
        11, 0, 2, 'load', indexed=True)
    assert instruction(0x4e2aa).value == instruction(0x4e318).value == ('extu', 16, 2)
    assert instruction(0x4e2ac).flow == instruction(0x4e31a).flow == 'call'
    assert word(0x65aa0, 4) + 0x1a == 0xffff11b6
    assert instruction(0x65986).access == sh2.Access(7, 0x1a, 2, 'load')
    assert instruction(0x65990).value == ('extu', 16, 0)
    assert word(0x65ae0, 4) == 0x14b4a and word(0x65ae4, 4) == 0x262a8


def test_rpm_axis_arguments_widths_and_fraction_scaling_match_stock():
    verify_arguments(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x26986, 0x26988, 0x2698a, 0x2698e, 0x26998,
                                    0x269a0, 0x269aa, 0x269b4, 0x269bc, 0x269be,
                                    0x269c6, 0x269c8, 0x269ca, 0x269d0, 0x269da,
                                    0x269ee, 0x269f0, 0x269fa, 0x26a02, 0x26a04,
                                    0x269c0, 0x26a08, 0x26c7a, 0x26c80, 0x26c84,
                                    0x26d00, 0x26d0c, 0x11cf0, 0x11ece, 0x14b4a,
                                    0x2cc92, 0x2cc96, 0x2cc9c, 0x2cc9e, 0x2cf0c,
                                    0x2cf14, 0x2cf1c, 0x3c092, 0x3c248, 0x3c0c8,
                                    0x3c0ce, 0x3c28a, 0x3c28c, 0x3c292, 0x3c380,
                                    0x3c388, 0x495ee, 0x495f4, 0x495fa, 0x4960e,
                                    0x49612, 0x49668, 0x496b8, 0x496c0, 0x65986,
                                    0x6598a, 0x6598e, 0x65990, 0x65aa0, 0x65ae0,
                                    0x65ae4, 0x261f4, 0x261fc, 0x2622c, 0x26234,
                                    0x2623c, 0x2626c, 0x262ac, 0x262b4, 0x262dc,
                                    0x4e1d2, 0x4e1d4, 0x4e450, 0x4e470, 0x4e474,
                                    0x4e480, 0x4e2a4, 0x4e2a6, 0x4e2aa, 0x4e2ac,
                                    0x4e310, 0x4e312, 0x4e318, 0x4e31a])
def test_changed_axis_sources_widths_factors_pools_and_calls_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_arguments(data)


def test_three_rpm_row_arguments_have_arithmetic_notes_and_typed_paths():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'engine_speed')]
    paths = ((19, 0xffff11f4, 0x11cf0, {0x2c648, 0x3bd74}),
             (20, 0xffff11bc, 0x11ece, {0x493e8, 0x4e1c0}),
             (21, 0xffff11b6, 0x14b4a, {0x65928}))
    for position, source, axis, functions in paths:
        assert chain.steps[position]['note'] == f'x = uint16({source:08x})'
        owner = model.meaning_of(SymbolKey('7mfk', 'axis', axis))
        links = [link for link in owner.links if link.type == 'index'
                 and link.to is model.meaning_of(SymbolKey('7mfk', 'ram', source))]
        assert len(links) == 1 and links[0].stated == {'7mfk'}
        assert {ref.address for ref in links[0].props['via']} == functions
        if axis == 0x14b4a:
            assert 'without a point multiplier' in links[0].props['note']
        else:
            assert 'quarter-point' in links[0].props['note']
