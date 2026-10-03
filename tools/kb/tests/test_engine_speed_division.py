"""Bind the primary RPM division, saturation, and zero paths to stock bytes."""

import re

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0x38272, "4f22d63e6060c8208b0bd63dd23ed13e420b506ae6ff666d30668f036203a0016263e200d53a4f26000b2521"),
    (0x38370, "ffff417fffff11d400021ce001e84800ffff1196"),
    (0x21ce0, "2f2620088941620d3020"),
    (0x21d6a, "d117d2172122e000000b62f6"),
    (0x21dc8, "ffff98180000044e"),
)
FORMULA = 'ffff1196 = min(65535, floor(32000000 / ffff11fc))'


def verify_conditions(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0x38370, 4) == 0xffff417f
    assert word(0x38374, 4) + 0x28 == 0xffff11fc
    assert word(0x38378, 4) == 0x21ce0
    assert word(0x3837c, 4) == 32000000
    assert word(0x38380, 4) == 0xffff1196
    assert word(0x38278) == 0xc820  # tst #0x20,r0
    assert instruction(0x3827a).target == 0x38294
    assert instruction(0x38282).flow == 'call'
    assert instruction(0x38284).access == sh2.Access(6, 0x28, 4, 'load')
    assert instruction(0x38288).value == ('extu', 16, 6)
    assert word(0x3828a) == 0x3066  # cmp/hi r6,r0
    assert instruction(0x3828c).target == 0x38296
    assert instruction(0x38290).target == 0x38296
    assert instruction(0x38292).value == ('copy', 6)
    assert instruction(0x38294).value == ('const', 0)
    assert instruction(0x3829c).access == sh2.Access(5, 0, 2, 'store')
    assert word(0x21ce2) == 0x2008  # tst r0,r0
    assert instruction(0x21ce4).target == 0x21d6a
    assert instruction(0x21d6a).value == ('pool', 0x21dc8, 4)
    assert instruction(0x21d6c).value == ('pool', 0x21dcc, 4)
    assert instruction(0x21d6e).access == sh2.Access(1, 0, 4, 'store')
    assert instruction(0x21d70).value == ('const', 0)


def test_rpm_division_modes_zero_and_saturation_match_stock():
    verify_conditions(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0x38278, 0x3827a, 0x38282, 0x38284, 0x38288,
                                    0x3828a, 0x3828c, 0x38292, 0x38294, 0x3829c,
                                    0x38370, 0x38374, 0x38378, 0x3837c, 0x38380,
                                    0x21ce2, 0x21ce4, 0x21d6e, 0x21d70, 0x21dc8])
def test_changed_division_modes_branches_operands_and_literals_fail(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_conditions(data)


def test_primary_rpm_step_and_selectors_keep_the_reviewed_contract():
    model = compile.cached(repo.ROOT)
    step = model.entities[('chain', 'engine_speed')].steps[7]
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', FORMULA)
    output = model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff1196))
    selectors = {(link.to.key, link.slot): link for link in output.links
                 if link.type == 'selector'}
    assert set(selectors) == {('nice-silkworm/ram', 'bit5'), ('imported-kudu/ram', None)}
    for link in selectors.values():
        assert link.stated == {'7mfk'}
        assert link.props['via'] == [SymbolKey('7mfk', 'fn', 0x38272)]
    assert 'min(65535' in output.props['summary']
