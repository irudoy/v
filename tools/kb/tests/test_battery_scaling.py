"""Bind the battery publisher's distinct byte-width contract to stock."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x39a9e, "4f224f13d082401e7ffcd681e03ad57f006dc1b2620d909242090524d27e420b0009d57a908b025c642cd27b420b65f365f1e6ff626c655d3527890062536623d277e07402647f044f174f26000b0009"),
    (0x39bdc, "0166"),
    (0x39cac, "ffff1e60ffff1d3400067188000671d8ffff1114"),
    (0x67190, "c8088b16"),
    (0x87f8, "8779"),
    (0x92be, "8000"),
)


def verify_battery(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert instruction(0x39aa2).value == ('pool', 0x39cac, 4)
    assert instruction(0x39aa4).gbr == ('copy', 0)
    assert word(0x39cb0, 4) + 0x3a == 0xffff1d6e
    assert instruction(0x39aae).access == sh2.Access(6, 0, 2, 'load', indexed=True)
    assert word(0x39cac, 4) + 0x164 == 0xffff1fc4
    assert instruction(0x39ab0).access == sh2.Access('gbr', 0x164, 2, 'store')
    assert instruction(0x39ab2).value == ('extu', 16, 0)
    assert instruction(0x39ab6).value == ('shr', 2)
    assert word(0x39cac, 4) + word(0x39bdc) == 0xffff1fc6
    assert instruction(0x39ab8).access == sh2.Access(5, 0, 1, 'store', indexed=True)
    assert instruction(0x39aba).value == ('pool', 0x39cb4, 4)
    assert instruction(0x39ac8).value == ('pool', 0x39cb8, 4)
    assert word(0x39cb4, 4) == 0x67188 and word(0x39cb8, 4) == 0x671d8
    for address in (0x39abc, 0x39aca):
        assert instruction(address).flow == 'call' and instruction(address).delayed
    assert instruction(0x39ac4).access == sh2.Access(5, 0, 1, 'load', indexed=True)
    assert instruction(0x39ac6).value == ('extu', 8, 2)
    assert instruction(0x39acc).value == ('copy', 15)
    assert instruction(0x39ace).access == sh2.Access(15, 0, 2, 'load')
    assert instruction(0x39ad2).value == ('extu', 8, 6)
    assert instruction(0x39ad4).value == ('extu', 16, 5)
    assert word(0x39ad6) == 0x3527 and instruction(0x39ad8).target == 0x39adc
    assert word(0x39cbc, 4) + 0x74 == 0xffff1188
    assert instruction(0x39ae2).access == sh2.Access(2, 0, 1, 'store', indexed=True)
    assert word(0x39ae6) == 0x4f17  # LDC.L @R15+,GBR.
    assert word(0x39ae8) == 0x4f26  # LDS.L @R15+,PR.
    assert instruction(0x39aea).flow == 'return' and instruction(0x39aea).delayed
    assert word(0x39aec) == 0x0009
    assert instruction(0x67192).target == 0x671c2


def test_battery_shift_byte_truncation_guard_calls_and_cap_match_stock():
    verify_battery(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address + offset
                                    for address, text in SLICES
                                    for offset in range(0, len(bytes.fromhex(text)), 2)])
@pytest.mark.parametrize('byte', (0, 1))
def test_changed_battery_width_shift_call_pool_cap_or_return_fails(address, byte):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + byte] ^= 1
    with pytest.raises(AssertionError):
        verify_battery(data)


def test_battery_inputs_mode_and_widths_preserve_the_distinct_byte_contract():
    model = compile.cached(repo.ROOT)
    for address, width in ((0xffff1d6e, 16), (0xffff1fc4, 16),
                           (0xffff1fc6, 8), (0xffff1188, 8)):
        symbol = model.symbols[SymbolKey('7mfk', 'ram', address)]
        assert symbol.value('width') == width and symbol.value('signed') is False
    source = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1d6e))
    copied = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1fc4))
    byte = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1fc6))
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1188))
    assert copied.props.get('level') is None and byte.props.get('level') is None
    assert source.props['level'] == output.props['level'] == 'code'
    [copy] = [link for link in copied.links if link.type == 'copy']
    assert copy.to is source and copy.stated == {'7mfk'}
    assert [ref.address for ref in copy.props['via']] == [0x39a9e]
    [input_link] = [link for link in byte.links if link.type == 'input']
    assert input_link.to is source and input_link.stated == {'7mfk'}
    assert 'uint8(uint16(ffff1d6e)>>2)' in input_link.props['note']
    [selector] = [link for link in output.links if link.type == 'selector']
    assert selector.to.key == 'shrewd-manul/ram' and selector.slot == 'bit3'
    assert selector.stated == {'7mfk'}
    assert [ref.address for ref in selector.props['via']] == [0x39a9e, 0x67188]
    assert '0x7900..0x8700' in selector.props['note'] and '0x8000' in selector.props['note']
    inputs = {link.to.key: link for link in output.links if link.type == 'input'}
    assert set(inputs) == {'eager-alligator/ram', 'satisfied-oarfish/ram', 'amaranth-swine/ram'}
    for link in inputs.values():
        assert link.stated == {'7mfk'}
        assert [ref.address for ref in link.props['via']] == [0x39a9e, 0x671d8]
    assert 'min(255' in inputs['amaranth-swine/ram'].props['note']
    assert model.symbols[SymbolKey('jk78c', 'ram', 0xffff1174)].value('signed') is None
