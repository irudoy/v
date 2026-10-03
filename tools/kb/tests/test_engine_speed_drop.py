"""Bind the RPM-drop branch conditions and recurrence to stock bytes."""

import re

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x3e1e2, "d07b401e7ff0d27a420b000920088b4ed6798464c8408b01a04de000c593d272660de036052d655d36538b2cc593e701d1724718660d647384113658620c61033428620cc5040267620d061a04274618021a362ce2ff4619622d36268911c593d166660d84113658620c0267640cc5043748660d6103021a07674218061a326c4219a0016023e000c100c5922f02c193c5911f01c192c5901f02c191c58fa0121f03024e024c024a024802c87a12d3526230602c4018d24cc100e036052d6053c193c192c191de4dc1906053c18f"),
    (0x3e3cc, "ffff1114ffff1e5000025e4effff24b4000084a3"),
    (0x84a3, "ff40"),
)
FORMULA = 'ffff1e50 = min(65535, 64*(ffff1f76 - ffff114a) + floor(192*ffff1e58/256))'


def verify_conditions(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x3e3d0, 4) == 0xffff1e50
    assert word(0x3e3cc, 4) + 0x36 == 0xffff114a
    assert word(0x3e3d8, 4) + 4 == 0xffff24b8
    assert instruction(0x3e1e8).value == ('pool', 0x3e3d4, 4)
    assert word(0x3e3d4, 4) == 0x25e4e
    assert instruction(0x3e1ea).flow == 'call'
    assert word(0x3e1ee) == 0x2008  # tst r0,r0
    assert instruction(0x3e1f0).target == 0x3e290
    assert word(0x3e1f6) == 0xc840  # tst #0x40,r0
    assert instruction(0x3e1f8).target == 0x3e1fe
    assert instruction(0x3e1fa).target == 0x3e298
    assert instruction(0x3e1fc).value == ('const', 0)
    assert instruction(0x3e202).value == ('extu', 16, 0)
    assert instruction(0x3e208).value == ('extu', 16, 5)
    assert word(0x3e20a) == 0x3653  # cmp/ge r5,r6
    assert instruction(0x3e20c).target == 0x3e268
    assert instruction(0x3e268).value == ('const', 0)
    assert instruction(0x3e26a).access == sh2.Access('gbr', 0, 2, 'store')
    assert instruction(0x3e23e).target == 0x3e264
    assert instruction(0x3e264).target == 0x3e26a
    assert instruction(0x3e290).value == ('pool', 0x3e3dc, 4)
    assert instruction(0x3e296).value == ('shl', 8)
    assert word(0x84a3, 1) == 255 and word(0x84a4, 1) == 64
    assert instruction(0x3e29a).access == sh2.Access('gbr', 0, 2, 'store')


def test_rpm_drop_modes_rising_branch_and_operands_match_stock():
    verify_conditions(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x3e1ea, 0x3e1ee, 0x3e1f0, 0x3e1f6, 0x3e1f8,
                                    0x3e1fc, 0x3e20a, 0x3e20c, 0x3e23e, 0x3e268,
                                    0x3e26a, 0x3e290, 0x3e296, 0x3e29a,
                                    0x3e3cc, 0x3e3d0, 0x3e3d4, 0x3e3d8, 0x3e3dc,
                                    0x84a3])
def test_changed_rpm_drop_modes_branches_and_coefficients_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_conditions(data)


def test_rpm_drop_arithmetic_and_three_selectors_keep_the_reviewed_contract():
    model = compile.cached(repo.ROOT)
    step = model.entities[('chain', 'engine_speed')].steps[5]
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1e50))
    selectors = {(link.to.key, link.slot): link for link in output.links
                 if link.type == 'selector'}
    assert set(selectors) == {('glaring-cuckoo/fn', None),
                              ('splendid-cheetah/ram', 'bit6'),
                              ('cinnamon-crayfish/ram', None)}
    for link in selectors.values():
        assert link.stated == {'7mfk'}
        assert link.props['via'] == [SymbolKey('7mfk', 'fn', 0x3e1da)]
    assert 'max(' not in output.props['summary']
    specification = (repo.ROOT / 'defs/JK08A.rpm-drop-state.md').read_text()
    assert 'if H4 < R:' in specification and 'F = 0' in specification
    assert 'D = H4 - R' in specification and 'D = max(' not in specification
