"""Bind the final RPM byte-table inputs and the CVTC load alternative."""

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SLICES = (
    (0xbda72, "d013401e7ffcd6128464c8088925d011cc018922a023eeff"),
    (0xbdacc, "d68b6e60db8b60e380f3e01205120dbc7520d4890612d289da89420b67dc620390a7e694d48705120a24666c60e380f3e012d285356c0dbc06127674420b67dc"),
    (0xbdac0, "00012eaaffff2464ffff576b"),
    (0xbdcfc, "ffff102cffff119c0000b53a00026140ffff128c0000b43a000261b8"),
    (0x8615, "ab"),
    (0x261b8, "4f222f46677c60536573d70a470be40f2f462f56606355f4655c470be40f61f660f66243635364f64f26d701472be5100002677000026944"),
    (0x26944, "6343014c611c3510891635168b103340891235184528304c61008401611c600c4f22d2063018420b61534f26000b650374ff441189e5e400000be50000026c78"),
    (0x26370, "9007655c35028902d602462be300000b844700e000026a80"),
    (0x26a80, "450143254501432545014325450143254501432563394019200889064500345c61418541620da005601d345c61408441620c601cd601462b0009000900026740"),
    (0x26740, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c0000"),
    (0x56e2c, "d552e017d452065cd252420b656c620cd34d9094053c665c326ce5d2622d655c32538b01e6d1626c662dd24b908846000265"),
    (0x56f6a, "0b1406a2102c"),
    (0x56f74, "ffff28f8ffff119c0001230200026370ffff128c"),
    (0x4b0ae, "dc5be016d46002ccde5b4e0b652cd552660c8453c9046503626eda4b900b7280dc5a0a24"),
    (0x4b21c, "ffff119c000121a600026370"),
    (0x4b234, "00012196"),
    (0x4b1f8, "ffff128c"),
    (0x4b0e4, "0285"),
    (0x12302, "8585858585858585"),
    (0x12196, "808989898a8c8f91"),
    (0x12f1e, "08101820283038404850586068707880"),
    (0x12f3e, "101214181c2028303840485058607080"),
)


def verify_byte_inputs(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert word(0xbdd00, 4) + 0x12 == 0xffff11ae
    assert instruction(0xbdb02).access == sh2.Access(11, 0, 1, 'load', indexed=True)
    assert instruction(0xbdb0a).value == ('extu', 8, 13)
    assert word(0xbdd10, 4) == 0xb43a and word(0xbdd14, 4) == 0x261b8
    assert word(0xbdac0, 4) + 0x94 == 0x12f3e
    assert word(0xbdac0, 4) + 0x74 == 0x12f1e
    assert word(0xbdac4, 4) + 4 == 0xffff2468
    assert instruction(0xbda7a).access == sh2.Access(6, 4, 1, 'load')
    assert word(0xbda7c) == 0xc808
    assert (word(0xbdac0, 4) + word(0xbdac8, 4)) & 0xffffffff == 0x8615
    assert data[0x8615] & 1 == 1
    assert instruction(0xbda88).value == ('const', 0xffffffff)
    assert word(0xbdcfc, 4) == 0xffff102c
    assert instruction(0xbdace).access == sh2.Access(6, 0, 1, 'load')
    assert instruction(0xbdafa).access == sh2.Access(15, 3, 1, 'store')
    assert instruction(0x261bc).value == ('extu', 8, 7)
    assert instruction(0x261ce).access == sh2.Access(15, 16, 4, 'load')
    assert instruction(0x261d0).value == ('extu', 8, 5)
    assert word(0x261ec, 4) == 0x26944
    assert instruction(0x26946).access == sh2.Access(4, 0, 1, 'load', indexed=True)
    assert instruction(0x26948).value == ('extu', 8, 1)
    assert instruction(0x26372).value == ('extu', 8, 5)
    assert word(0x26382) == 224 and word(0x26384, 4) == 0x26a80
    assert word(0x26abc, 4) == 0x26740
    assert word(0x56f78, 4) + 0x17 == 0xffff11b3
    assert instruction(0x56e32).access == sh2.Access(5, 0, 1, 'load', indexed=True)
    assert instruction(0x56e38).value == ('extu', 8, 6)
    assert word(0x56f7c, 4) == 0x12302 and word(0x56f80, 4) == 0x26370
    assert word(0x56f74, 4) + word(0x56f6a) == 0xffff340c
    assert instruction(0x56e40).access == sh2.Access(3, 0, 1, 'load', indexed=True)
    assert instruction(0x56e42).value == ('extu', 8, 5)
    assert instruction(0x56e44).value == ('add', 6)
    assert instruction(0x56e50).value == ('const', 0xffffffd1)
    assert instruction(0x56e5a).value == ('shl', 1)
    assert word(0x56f84, 4) + word(0x56f6c) == 0xffff192e
    assert instruction(0x56e5c).access == sh2.Access(2, 0, 2, 'store', indexed=True)
    assert word(0x4b21c, 4) + 0x16 == 0xffff11b2
    assert instruction(0x4b0b4).access == sh2.Access(12, 0, 1, 'load', indexed=True)
    assert instruction(0x4b0ba).value == ('extu', 8, 2)
    assert word(0x4b234, 4) == 0x12196 and word(0x4b224, 4) == 0x26370
    assert word(0x4b1f8, 4) + word(0x4b0e4) == 0xffff1511
    assert instruction(0x4b0cc).value == ('addi', -128)
    assert instruction(0x4b0d0).access == sh2.Access(10, 0, 1, 'store', indexed=True)


def test_last_rpm_byte_inputs_and_cvtc_load_selection_match_stock():
    verify_byte_inputs(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [0xbda7a, 0xbda7c, 0xbda7e, 0xbda82, 0xbda84,
                                    0xbda88, 0xbdace, 0xbdafa, 0xbdb02, 0xbdb08,
                                    0xbdb0a, 0xbdac0, 0xbdac4, 0xbdac8, 0xbdcfc,
                                    0xbdd00, 0xbdd10, 0xbdd14, 0x8614, 0x261bc,
                                    0x261ce, 0x261d0, 0x261ec, 0x26946, 0x26948,
                                    0x26968, 0x26980, 0x26372, 0x26374, 0x26376,
                                    0x26380, 0x26382, 0x26384, 0x26a80, 0x26a92,
                                    0x26a98, 0x26aa0, 0x26aaa, 0x26abc, 0x26742,
                                    0x2674a, 0x26756, 0x26760, 0x2676c, 0x56e32,
                                    0x56e38, 0x56e40, 0x56e42, 0x56e44, 0x56e4c,
                                    0x56e4e, 0x56e50, 0x56e5a, 0x56e5c, 0x56f6a,
                                    0x56f6c, 0x56f74, 0x56f78, 0x56f7c, 0x56f80,
                                    0x56f84, 0x4b0b4, 0x4b0b8, 0x4b0ba, 0x4b0cc,
                                    0x4b0d0, 0x4b21c, 0x4b224, 0x4b234, 0x4b1f8,
                                    0x4b0e4, 0x12302, 0x12196, 0x12f1e, 0x12f3e])
def test_changed_byte_input_and_table_binding_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address + 1] ^= 1
    with pytest.raises(AssertionError):
        verify_byte_inputs(data)


def test_rpm_byte_table_notes_and_cvtc_alternative_are_typed():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'engine_speed')]
    for position, source, table, function in ((22, 0xffff11ae, 0xb43a, 0xbda64),
                                             (23, 0xffff11b3, 0x12302, 0x56bd0),
                                             (24, 0xffff11b2, 0x12196, 0x4afdc)):
        assert chain.steps[position]['note'] == f'x = uint8({source:08x})'
        owner = model.meaning_of(SymbolKey('7mfk', 'tbl', table))
        links = [link for link in owner.links if link.type == 'index'
                 and link.to is model.meaning_of(SymbolKey('7mfk', 'ram', source))]
        assert len(links) == 1 and links[0].stated == {'7mfk'}
        assert [ref.address for ref in links[0].props['via']] == [function]
    table = model.meaning_of(SymbolKey('7mfk', 'tbl', 0xb43a))
    selectors = [link for link in table.links if link.type == 'selector'
                 and link.to is model.meaning_of(SymbolKey('7mfk', 'ram', 0xffff2468))]
    assert len(selectors) == 1 and selectors[0].slot == 'bit3'
    assert selectors[0].stated == {'7mfk'}
    assert '255' in selectors[0].props['note'] and '00008615' in selectors[0].props['note']
