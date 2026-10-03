"""Bind event timing, unsigned wrap correction, and holdoff to stock bytes."""

import re

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x28af8, "9123d6138461c8208b1dd612846420088903d511e2ffa011152ad6109016046e601234028d01340874ffd60d44094409d50960604401154acb202600d6079005006e000b2102000b0009"),
    (0x28b42, "84cc05d0"),
    (0x28b48, "ffff24c8ffff25fbffff11d4ffff128cffff2465"),
    (0x20908, "d28a420b0009"),
    (0x20b34, "00028af8"),
    (0x2093e, "d5816253720735228d0c6653626022288903626072ff622c262076016253720736228bf3"),
    (0x20b44, "ffff25fb"),
    (0x2c92e, "d6a40124e0018064"),
    (0x2cbc0, "ffff25fb"),
    (0x2966a, "88078b01a09e0009"),
    (0x29838, "d239420b0009"),
    (0x29920, "000208f8"),
)
FORMULA = 'ffff11fc = uint32(ffff185c - ffff84cc) >> 5; ffff84cc = ffff185c'


def verify_conditions(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert int.from_bytes(data[0x28b42:0x28b44], 'big', signed=True) & 0xffffffff == 0xffff84cc
    assert word(0x28b48, 4) + 1 == 0xffff24c9
    assert word(0x28b4c, 4) + 4 == 0xffff25ff
    assert word(0x28b50, 4) + 0x28 == 0xffff11fc
    assert word(0x28b54, 4) + word(0x28b44) == 0xffff185c
    assert word(0x28b58, 4) == 0xffff2465
    assert word(0x28afe) == 0xc820
    assert instruction(0x28b00).target == 0x28b3e
    assert word(0x28b06) == 0x2008
    assert instruction(0x28b08).target == 0x28b12
    assert instruction(0x28b0c).value == ('const', 0xffffffff)
    assert instruction(0x28b0e).target == 0x28b34
    assert instruction(0x28b10).access == sh2.Access(5, 0x28, 4, 'store')
    assert word(0x28b1a) == 0x3402  # cmp/hs r0,r4
    assert instruction(0x28b1c).target == 0x28b22
    assert word(0x28b1e) == 0x3408  # sub r0,r4 in the delay slot
    assert instruction(0x28b20).value == ('addi', -1)
    assert [instruction(address).value for address in (0x28b24, 0x28b26, 0x28b2c)] == [
        ('shr', 2), ('shr', 2), ('shr', 1)]
    assert instruction(0x28b2e).access == sh2.Access(5, 0x28, 4, 'store')
    assert word(0x28b30) == 0xcb20
    assert instruction(0x28b3c).access == sh2.Access(1, 0, 4, 'store')
    assert instruction(0x2090a).flow == 'call' and word(0x20b34, 4) == 0x28af8
    assert instruction(0x2093e).value == ('pool', 0x20b44, 4)
    assert word(0x20b44, 4) == 0xffff25fb
    assert instruction(0x20942).value == ('addi', 7)
    assert instruction(0x2094e).target == 0x20958
    assert instruction(0x20952).value == ('addi', -1)
    assert instruction(0x20960).target == 0x2094a
    assert instruction(0x2c92e).value == ('pool', 0x2cbc0, 4)
    assert word(0x2cbc0, 4) + 4 == 0xffff25ff
    assert instruction(0x2c932).value == ('const', 1)
    assert instruction(0x2c934).access == sh2.Access(6, 4, 1, 'store')
    assert instruction(0x2966e).target == 0x297ae
    assert instruction(0x2983a).flow == 'call' and word(0x29920, 4) == 0x208f8


def test_event_interval_modes_wrap_holdoff_and_calls_match_stock():
    verify_conditions(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x28af8, 0x28afe, 0x28b00, 0x28b06, 0x28b08,
                                    0x28b0c, 0x28b10, 0x28b1a, 0x28b1c, 0x28b1e,
                                    0x28b20, 0x28b24, 0x28b26, 0x28b2c, 0x28b2e,
                                    0x28b30, 0x28b32, 0x28b3c, 0x28b42, 0x28b44,
                                    0x28b48, 0x28b4c, 0x28b50, 0x28b54, 0x28b58,
                                    0x2090a, 0x20b34, 0x20942, 0x2094e, 0x20952,
                                    0x20960, 0x20b44, 0x2c932, 0x2c934, 0x2cbc0,
                                    0x2966e, 0x2983a, 0x29920])
def test_changed_event_masks_wrap_shifts_history_and_calls_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_conditions(data)


def test_event_step_and_typed_alternatives_keep_the_reviewed_contract():
    model = compile.cached(repo.ROOT)
    step = model.entities[('chain', 'engine_speed')].steps[6]
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff11fc))
    previous = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff84cc))
    holdoff = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff25ff))
    assert holdoff.key == 'event_interval_holdoff/ram'
    selectors = {(link.to.key, link.slot): link for link in output.links
                 if link.type == 'selector'}
    assert set(selectors) == {('apc_mode/ram', 'bit5'), ('event_interval_holdoff/ram', None),
                              ('busy-horse/ram', None)}
    for link in selectors.values():
        assert link.stated == {'7mfk'}
        assert link.props['via'] == [SymbolKey('7mfk', 'fn', 0x28af8)]
    copies = [link for link in previous.links if link.type == 'copy']
    assert len(copies) == 1 and copies[0].to.key == 'classy-bull/ram'
    assert any(link.type == 'selector' and link.to.key == 'apc_mode/ram'
               and link.slot == 'bit5' for link in previous.links)
