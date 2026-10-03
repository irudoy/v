"""Bind median ordering, mode selection, and zero-period behavior to stock bytes."""

import re

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x3df2c, "2fe64f22d6858461c8208907d687e016026ce086d686600ca03c0624de859066d67f04ec9064d17f0e44906202ec905e0e24905b026dd67c460b602de5ff660d625c3627890062639053652c662c0e54904d04ec644c364089189049354307ec8d06677c34778b073573890fa009000935778b0b34738b04d66de086600ca0090644d66be086600ca0040674d668e086600c06544f26000b6ef6"),
    (0x3e018, "02c8047104720470"),
    (0x3e148, "ffff24c8ffff1ff40000a2c200021bbcffff11d4ffff277effff39c4"),
    (0x21bbc, "2f26200889562f36210703294015890170ff60074115890171ff6117620d30208b4e"),
    (0x21c70, "d119d21a2122e000000b62f6"),
    (0x21cd8, "ffff98180000044e"),
)
FORMULA = ('ffff3e36 = ffff3e35; ffff3e35 = ffff3e34; '
           'ffff3e34 = min(255, floor(0xA2C2 / ffff22bc)); '
           'ffff2804 = median(ffff3e34, ffff3e35, ffff3e36)')


def verify_conditions(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x3e148, 4) + 1 == 0xffff24c9
    assert word(0x3e14c, 4) + word(0x3e018) == 0xffff22bc
    assert word(0x3e150, 4) == 41666
    assert word(0x3e154, 4) == 0x21bbc
    assert word(0x3e158, 4) + 0x16 == 0xffff11ea
    assert word(0x3e15c, 4) + 0x86 == 0xffff2804
    assert [word(0x3e160, 4) + word(address)
            for address in (0x3e01e, 0x3e01a, 0x3e01c)] == [0xffff3e34, 0xffff3e35, 0xffff3e36]
    assert word(0x3df34) == 0xc820
    assert instruction(0x3df36).target == 0x3df48
    assert instruction(0x3df44).target == 0x3dfc0
    assert instruction(0x3df64).flow == 'call'
    assert instruction(0x3df66).value == ('extu', 16, 2)
    assert instruction(0x3df6a).value == ('extu', 16, 0)
    assert instruction(0x3df70).target == 0x3df74
    assert instruction(0x3df72).value == ('copy', 6)
    for site, target in ((0x3df84, 0x3dfb8), (0x3df8c, 0x3df9c),
                         (0x3df92, 0x3dfa4), (0x3df96, 0x3dfb8),
                         (0x3df9e, 0x3dfb8), (0x3dfa2, 0x3dfae)):
        assert instruction(site).target == target
    assert instruction(0x21bc0).target == 0x21c70
    assert instruction(0x21c70).value == ('pool', 0x21cd8, 4)
    assert instruction(0x21c72).value == ('pool', 0x21cdc, 4)
    assert instruction(0x21c74).access == sh2.Access(1, 0, 4, 'store')
    assert instruction(0x21c76).value == ('const', 0)


def test_rpm_median_history_modes_and_zero_period_match_stock():
    verify_conditions(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x3df34, 0x3df36, 0x3df44, 0x3df54, 0x3df5c,
                                    0x3df64, 0x3df66, 0x3df6a, 0x3df70, 0x3df7a,
                                    0x3df84, 0x3df8c, 0x3df92, 0x3df96, 0x3df9e,
                                    0x3dfa2, 0x3dfac, 0x3dfb6, 0x3dfbe,
                                    0x3e018, 0x3e01a, 0x3e01c, 0x3e01e,
                                    0x3e148, 0x3e14c, 0x3e150, 0x3e154,
                                    0x3e158, 0x3e15c, 0x3e160, 0x21bc0,
                                    0x21c74, 0x21c76, 0x21cd8, 0x21cdc])
def test_changed_median_order_modes_branches_and_literals_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_conditions(data)


def test_median_step_history_and_selectors_keep_the_reviewed_contract():
    model = compile.cached(repo.ROOT)
    step = model.entities[('chain', 'engine_speed')].steps[4]
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff2804))
    sample = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff3e34))
    expected = {
        output: {('apc_mode/ram', 'bit5')},
        sample: {('apc_mode/ram', 'bit5'), ('spry-koel/ram', None)},
    }
    for owner, choices in expected.items():
        selectors = {(link.to.key, link.slot): link for link in owner.links
                     if link.type == 'selector'}
        assert set(selectors) == choices
        for link in selectors.values():
            assert link.stated == {'7mfk'}
            assert link.props['via'] == [SymbolKey('7mfk', 'fn', 0x3df2c)]
    copies = [link for link in output.links if link.type == 'copy']
    assert len(copies) == 1 and copies[0].to.key == 'angelic-shark/ram'
    assert any(link.type == 'input' and link.to is sample for link in output.links)
    assert '10-degree' in output.props['summary'] and '120-degree' not in output.props['summary']
