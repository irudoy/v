"""Bind the RPM override conditions to the registered 7mfk stock image."""

import pytest

from kb import derive, repo


WORDS = {
    0x3def0: 0xd093,  # GBR base from the literal pool.
    0x3def2: 0x401e,
    0x3def6: 0xd693, 0x3def8: 0x6060,
    0x3defa: 0xc820, 0x3defc: 0x8b0f,  # Bit 5 set selects zero.
    0x3defe: 0xd692, 0x3df00: 0x8461,
    0x3df02: 0xc820, 0x3df04: 0x8902,  # Bit 5 clear selects conversion.
    0x3df06: 0xc570, 0x3df08: 0xa00a, 0x3df0a: 0x2f02,
    0x3df0c: 0xd68f, 0x3df0e: 0x9083, 0x3df10: 0xd18f,
    0x3df12: 0x026d, 0x3df14: 0xd68f, 0x3df16: 0x460b,
    0x3df18: 0x602d, 0x3df1a: 0xa001, 0x3df1c: 0x0009,
    0x3df1e: 0xe000, 0x3df20: 0xc11b,
}
POOLS = {0x3e140: 0xffff1114, 0x3e144: 0xffff417f, 0x3e148: 0xffff24c8,
         0x3e14c: 0xffff1ff4, 0x3e150: 0x0000a2c2, 0x3e154: 0x00021bbc}


def verify_words(data):
    for address, word in WORDS.items():
        assert int.from_bytes(data[address:address + 2], 'big') == word, f'{address:08x}'
    for address, pointer in POOLS.items():
        assert int.from_bytes(data[address:address + 4], 'big') == pointer, f'{address:08x}'
    assert int.from_bytes(data[0x3e018:0x3e01a], 'big') == 0x02c8
    assert 0xffff1114 + 0x36 == 0xffff114a
    assert 0xffff1114 + 0xe0 == 0xffff11f4
    assert 0xffff1ff4 + 0x02c8 == 0xffff22bc
    assert 0x3defc + 4 + 2 * (WORDS[0x3defc] & 0xff) == 0x3df1e
    assert 0x3df04 + 4 + 2 * (WORDS[0x3df04] & 0xff) == 0x3df0c


def test_rpm_override_masks_branches_and_operands_match_stock():
    verify_words(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x3defa, 0x3defc, 0x3df02, 0x3df04, 0x3df06,
                                    0x3df1e, 0x3df20, 0x3e144, 0x3e148])
def test_changed_masks_targets_and_sources_fail_the_binding(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError, match=f'{address:08x}'):
        verify_words(data)
