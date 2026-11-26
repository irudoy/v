"""Bind the OSBR1 word capture and first-sample interval to stock bytes."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x28f16, "907ad648058d85bb64039075084590740c9d8461c8408d056603906f34586d43a0070945906aedffd23f09d56063cb4080219062966309d5"),
    (0x28f0e, "9b7d"),
    (0x2900c, "f44002fe02c602a084e8"),
    (0x2903c, "ffff24c0"),
    (0x28ed0, "d9548566da54"),
    (0x28f06, "d846"),
    (0x29020, "ffff128cffff1ff4ffff24c80002a294"),
    (0x28ee8, "092684a1c8408902d34e432b0009"),
)
CAPTURE = 'prev = ffff158a; ffff158a = fffff456'
PERIOD = 'ffff22ba = uint16(ffff158a - prev)'


def verify_conditions(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    mmio_base = int.from_bytes(data[0x2900c:0x2900e], 'big', signed=True) & 0xffffffff
    assert mmio_base == 0xfffff440 and mmio_base + 0x16 == 0xfffff456
    assert mmio_base + 0x16 != 0xfffff434
    assert instruction(0x28f0e).value == ('pool', 0x2900c, 2)
    assert word(0x29020, 4) + word(0x2900e) == 0xffff158a
    assert word(0x29024, 4) + word(0x29010) == 0xffff22ba
    assert word(0x29024, 4) + word(0x29012) == 0xffff2294
    assert word(0x2903c, 4) + 1 == 0xffff24c1
    assert word(0x29028, 4) + 1 == 0xffff24c9
    assert word(0x2902c, 4) == 0x2a294
    assert word(0x28eec) == 0xc840
    assert instruction(0x28eee).target == 0x28ef6
    assert instruction(0x28f18).value == instruction(0x28f3e).value == ('pool', 0x2903c, 4)
    assert instruction(0x28f1a).access == sh2.Access(8, 0, 2, 'load', indexed=True)
    assert instruction(0x28f1c).access == sh2.Access(11, 0x16, 2, 'load')
    assert instruction(0x28f1e).value == ('copy', 0)
    assert instruction(0x28f22).access == sh2.Access(8, 0, 2, 'store', indexed=True)
    assert instruction(0x28f26).access == sh2.Access(9, 0, 2, 'load', indexed=True)
    assert instruction(0x28f28).access == sh2.Access(6, 1, 1, 'load')
    assert word(0x28f2a) == 0xc840
    assert instruction(0x28f2c).target == 0x28f3a and instruction(0x28f2c).delayed
    assert instruction(0x28f2e).value == ('copy', 0)
    assert instruction(0x28f32).value == ('sub', 5)
    assert instruction(0x28f34).value == ('copy', 4)
    assert instruction(0x28f36).target == 0x28f48 and instruction(0x28f36).delayed
    assert instruction(0x28f38).access == instruction(0x28f40).access == sh2.Access(
        9, 0, 2, 'store', indexed=True)
    assert instruction(0x28f3c).value == ('const', 0xffffffff)
    assert instruction(0x28f42).value == ('copy', 6)
    assert word(0x28f44) == 0xcb40
    assert instruction(0x28f46).access == sh2.Access(2, 1, 1, 'store')
    assert instruction(0x28f4c).access == sh2.Access(9, 0, 2, 'store', indexed=True)


def test_osbr1_word_capture_first_sample_and_interval_match_stock():
    verify_conditions(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x28f0e, 0x28f16, 0x28f18, 0x28f1a, 0x28f1c,
                                    0x28f1e, 0x28f20, 0x28f22, 0x28f24, 0x28f26,
                                    0x28f28, 0x28f2a, 0x28f2c, 0x28f2e, 0x28f30,
                                    0x28f32, 0x28f34, 0x28f36, 0x28f38, 0x28f3a,
                                    0x28f3c, 0x28f3e, 0x28f40, 0x28f42, 0x28f44,
                                    0x28f46, 0x28f48, 0x28f4a, 0x28f4c, 0x2900c,
                                    0x2900e, 0x29010, 0x29012, 0x29014, 0x2903c,
                                    0x28ed0, 0x28f06, 0x29020, 0x29024, 0x29028,
                                    0x2902c, 0x28eec, 0x28eee, 0x28ef2])
def test_changed_capture_source_history_width_masks_and_stores_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_conditions(data)


def test_capture_equations_and_selectors_keep_the_word_history():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'engine_speed')]
    assert chain.steps[0]['from'].kind == 'reg'
    assert chain.steps[0]['from'].address == 0xfffff456
    assert chain.steps[0]['to'].address == chain.steps[1]['from'].address == 0xffff158a
    assert chain.steps[0]['note'] == CAPTURE and chain.steps[1]['note'] == PERIOD
    register = model.meaning_of(SymbolKey('7mfk', 'reg', 0xfffff456))
    capture = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff158a))
    period = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff22ba))
    flags = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff24c1))
    assert register.key == 'atu1_osbr1/reg' and register.props['width'] == 16
    assert capture.props['width'] == period.props['width'] == 16
    assert flags.key == 'crank_capture_state/ram' and flags.props['width'] == 8
    assert [(bit['bit'], bit['name']) for bit in flags.props['bit']] == [(6, 'initialized')]
    selectors = {(link.to.key, link.slot): link for link in period.links
                 if link.type == 'selector'}
    assert set(selectors) == {('crank_capture_state/ram', 'bit6'), ('apc_mode/ram', 'bit6')}
    assert '0xffff' in selectors[('crank_capture_state/ram', 'bit6')].props['note']
    for link in selectors.values():
        assert link.stated == {'7mfk'} and link.props['via'] == [SymbolKey('7mfk', 'fn', 0x28ea2)]
    inputs = [link for link in period.links if link.type == 'input']
    assert any(link.to.key == capture.key for link in inputs)
    readers = [link for link in register.links if link.type == 'reader']
    assert any(link.to.key == 'crank_tooth_ici0a_capture_and_dispatch_isr/fn' for link in readers)
    # The separate longword capture root remains available to the tooth-nine path.
    assert model.meaning_of(SymbolKey('7mfk', 'reg', 0xfffff434)).key == 'abstract-pudu/reg'
