"""Bind RPM shifts and the 56-byte scheduler snapshot to stock instructions.

These slices establish register arithmetic and copy geometry. They do not
execute complete producers, establish sample simultaneity, or prove hardware
behavior. Fixed bytes are independent of the image and model under test.
"""

import re

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SCALING = (
    (0x384fe, "2fd64f224f124f13d028401ed62a6261d62a622d420942016d2d626060d3c10a642cc504e2014218650d32480527061a0d47021a362c4619646d35408b023d478b0074016043c10460d34001e5ffc10d62d34209d416655c902032568f0104256253901c4d094d01042460d3bf80c110bfad0009c50ae5ff655c660d46094609460136568b0066536063bf04c012bf6400094f174f164f26000b6df6"),
    (0x3846e, "d14ee6ff666c851a620d42094201326689006623d54be01a005cc8408909d7479033057c90320754e016041c902da0070744d742656390296463076490250764e0160164666c644c36478b06655c34578b03901ce201000b0724000b0009"),
    (0x384cc, "d536e2ff622c855a660d4609460936268b006623e017000b0564"),
    (0x385a8, "ffff11d4ffff1ff4ffff421dffff119600008743"),
    (0x384f8, "02a602a70225"),
    (0x3859a, "024602a5"),
)
SNAPSHOT = (
    (0x20efe, "de82"),
    (0x20f60, "d17c2621d67c62612421d27c4e0be038"),
    (0x21108, "000220f8"),
    (0x21154, "ffff119c"),
    (0x2115c, "ffff11d4"),
    (0x220f8, "2f36d305033e70fc432b002e"),
    (0x22110, "00022158"),
    (0x2211e, "532c110d502b113c532a110b5029113a5328110950271138532611075025113653241105502311345322110350211132632211012132000b63f6"),
    (0x22190, "0002211e"),
)
FORMULAS = {
    9: (0xffff1196, 0xffff11e8, 0x384fe, 'ffff11e8 = ffff1196 >> 3'),
    10: (0xffff1196, 0xffff11ee, 0x384fe, 'ffff11ee = ffff1196 >> 4'),
    11: (0xffff1196, 0xffff11f4, 0x384fe, 'ffff11f4 = ffff1196 >> 6'),
    12: (0xffff1196, 0xffff11e6, 0x384fe, 'ffff11e6 = min(255, ffff1196 >> 8)'),
    13: (0xffff11e8, 0xffff11eb, 0x384cc,
         'ffff11eb = min(255, ffff11e8 >> 4) = min(255, ffff1196 >> 7)'),
    14: (0xffff11e8, 0xffff11ea, 0x3846e,
         'ffff11ea = min(255, ffff11e8 >> 3) = min(255, ffff1196 >> 6)'),
    15: (0xffff11ee, 0xffff11b6, 0x20dfe, 'ffff11b6 = ffff11ee'),
    16: (0xffff11f4, 0xffff11bc, 0x20dfe, 'ffff11bc = ffff11f4'),
    17: (0xffff11e6, 0xffff11ae, 0x20dfe, 'ffff11ae = ffff11e6'),
    18: (0xffff11eb, 0xffff11b3, 0x20dfe, 'ffff11b3 = ffff11eb'),
    19: (0xffff11ea, 0xffff11b2, 0x20dfe, 'ffff11b2 = ffff11ea'),
}


def locks(data, spans):
    for address, hex_bytes in spans:
        raw = bytes.fromhex(hex_bytes)
        assert data[address:address + len(raw)] == raw, f'{address:08x}'


def uint(data, address, size=4):
    raw = data[address:address + size]
    assert len(raw) == size
    return int.from_bytes(raw, 'big')


def insn(data, pc):
    return sh2.decode(uint(data, pc, 2), pc)


def verify_scaling(data):
    locks(data, SCALING)
    base = uint(data, 0x385a8)
    assert uint(data, 0x385b4) == 0xffff1196
    assert insn(data, 0x38506).value == ('pool', 0x385a8, 4)
    assert insn(data, 0x38508).gbr == ('copy', 0)
    assert insn(data, 0x3850a).value == ('pool', 0x385b4, 4)
    assert insn(data, 0x3850c).access == sh2.Access(6, 0, 2, 'load')
    assert insn(data, 0x38510).value == ('extu', 16, 2)
    for pc, count in ((0x38512, 2), (0x38514, 1), (0x38548, 1),
                      (0x38562, 2), (0x38564, 1),
                      (0x3857a, 2), (0x3857c, 2), (0x3857e, 1),
                      (0x384d6, 2), (0x384d8, 2),
                      (0x38478, 2), (0x3847a, 1)):
        assert insn(data, pc).value == ('shr', count)
    for pc, offset, width in ((0x3851c, 0x14, 2), (0x3854c, 0x1a, 2),
                              (0x3856c, 0x20, 2), (0x3858a, 0x12, 1)):
        assert insn(data, pc).access == sh2.Access('gbr', offset, width, 'store')
    assert [base + offset for offset in (0x14, 0x1a, 0x20, 0x12)] == [
        0xffff11e8, 0xffff11ee, 0xffff11f4, 0xffff11e6]
    assert insn(data, 0x3856a).target == 0x3846e
    assert insn(data, 0x3856e).target == 0x384cc
    assert insn(data, 0x38582).target == 0x38586
    assert insn(data, 0x384dc).target == 0x384e0
    assert insn(data, 0x3847e).target == 0x38482
    # The byte-12.5 history branches converge before the current-byte store.
    assert insn(data, 0x3848a).target == 0x384a0
    assert insn(data, 0x3849c).target == 0x384ae
    assert insn(data, 0x384b0).access == sh2.Access(1, 0, 1, 'store', True)
    assert insn(data, 0x384e4).access == sh2.Access(5, 0, 1, 'store', True)


def verify_snapshot(data):
    locks(data, SNAPSHOT)
    source, destination = uint(data, 0x2115c), uint(data, 0x21154)
    assert (source, destination) == (0xffff11d4, 0xffff119c)
    assert insn(data, 0x20efe).value == ('pool', 0x21108, 4)
    assert uint(data, 0x21108) == 0x220f8
    assert insn(data, 0x20f60).value == ('pool', 0x21154, 4)
    assert insn(data, 0x20f6a).value == ('pool', 0x2115c, 4)
    assert insn(data, 0x20f6c).flow == 'call' and insn(data, 0x20f6c).delayed
    assert insn(data, 0x20f6e).value == ('const', 56)
    assert insn(data, 0x220fa).value == ('pool', 0x22110, 4)
    table = uint(data, 0x22110)
    assert insn(data, 0x220fc).access == sh2.Access(3, 0, 4, 'load', True)
    assert uint(data, table + 56) == 0x2211e
    assert insn(data, 0x220fe).value == ('addi', -4)
    assert insn(data, 0x22100).flow == 'jump' and insn(data, 0x22100).delayed
    assert insn(data, 0x22102).access == sh2.Access(2, 0, 4, 'load', True)
    # Track source offsets through the actual tail, including its first load
    # in the indirect-jump delay slot. The tail has fourteen longword stores.
    registers = {0: 52}
    copies = []
    for pc in range(0x2211e, 0x22154, 2):
        instruction = insn(data, pc)
        access = instruction.access
        assert access is not None and access.size == 4 and not access.indexed
        if access.mode == 'load':
            assert access.base == 2
            registers[instruction.dest] = access.disp
        else:
            assert access.mode == 'store' and access.base == 1
            copies.append((access.disp, registers[(instruction.word >> 4) & 15]))
    assert sorted(copies) == [(offset, offset) for offset in range(0, 56, 4)]
    assert insn(data, 0x22154).flow == 'return' and insn(data, 0x22154).delayed
    assert insn(data, 0x22156).access == sh2.Access(15, 0, 4, 'load')
    for ordinal in range(15, 20):
        live, snapshot, _, _ = FORMULAS[ordinal]
        assert 0 <= live - source < 56
        assert snapshot - destination == live - source


def test_rpm_shifts_saturation_and_operands_match_stock():
    verify_scaling(derive.image_bytes(repo.layout('7mfk')))


def test_rpm_snapshot_dispatch_and_all_fourteen_words_match_stock():
    verify_snapshot(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize(('verify', 'address'), [
    (verify_scaling, address) for address in
    (0x3850c, 0x38512, 0x3851c, 0x38548, 0x3854c, 0x38562, 0x3856c,
     0x3856a, 0x3856e, 0x3857e, 0x38582, 0x3858a, 0x3847e, 0x384b0,
     0x384d8, 0x384dc, 0x384e4, 0x385a8, 0x385b4)
] + [
    (verify_snapshot, address) for address in
    (0x20efe, 0x20f60, 0x20f6a, 0x20f6c, 0x20f6e, 0x21108, 0x21154,
     0x2115c, 0x220fc, 0x220fe, 0x22102, 0x22110, 0x22120, 0x22152, 0x22190)
])
def test_changed_scaling_or_snapshot_bytes_fail_the_binding(verify, address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify(data)


@pytest.mark.parametrize('ordinal', FORMULAS)
def test_reviewed_steps_keep_only_their_bound_arithmetic(ordinal):
    model = compile.cached(repo.ROOT)
    live, output, function, formula = FORMULAS[ordinal]
    step = model.entities[('chain', 'engine_speed')].steps[ordinal - 1]
    assert step['from'] == SymbolKey('7mfk', 'ram', live)
    assert step['to'] == SymbolKey('7mfk', 'ram', output)
    assert step['via'] == [SymbolKey('7mfk', 'fn', function)]
    assert re.sub(r'\s+', '', step['note']) == re.sub(r'\s+', '', formula)
    if ordinal >= 15:
        meaning = model.meaning_of(step['to'])
        link = next(item for item in meaning.links
                    if item.type == 'copy' and item.to == model.meaning_of(step['from']))
        assert link.stated == {'7mfk'}
        assert link.props['via'] == step['via']
