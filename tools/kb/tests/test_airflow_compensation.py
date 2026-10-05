"""Bind bank initialization, prior-word compensation, and word wrap to stock."""

import pytest

from kb import compile, derive, repo, sh2
from tools.kb.tests.stock_corruption import slice_word_ids, slice_word_samples
from kb.model import SymbolKey


SLICES = (
    (0x9586, "014f"),
    (0x958c, "0050"),
    (0x3ae8a, "2fc62fd62fe64f224f124f13d098401e7ffcd297654cc40e6d534d007204670c60d3062d6253720127288f082f61d2917501275b722c02656073a035c00ede8d60d3d48d62e3722c072d8543e4ff677d6c0d627332cc644d32478b01a0046743d3868533660d376c27788b01a016e5ff0412d381743060534008054e6073673162534229677d0727655d041a0757021a4229342cd27a420b6143650366f17e2c60d3666d36580e657f044f174f164f266ef66df6000b6cf6"),
    (0x3b0f8, "ffff3968ffff1018ffff1e1c0000958600021ce0"),
    (0x21ce0, "2f2620088941620d30208b440019401830168b0b"
     + "3104" * 8 + "412462f6000b601c2f36631d40184129"
     + "3104" * 16 + "621d212a322e4228313c"
     + "3104" * 16 + "4124601d302c63f6000b62f6d117d2172122e000000b62f6"
     + "0019621d422841294224" + "31044224" * 16 + "6023000b62f6"),
    (0x21dc8, "ffff98180000044e"),
)


def verify_compensation(data):
    for address, text in SLICES:
        expected = bytes.fromhex(text)
        assert data[address:address + len(expected)] == expected, f'{address:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert instruction(0x3ae96).value == ('pool', 0x3b0f8, 4)
    assert instruction(0x3ae98).gbr == ('copy', 0)
    assert instruction(0x3ae9e).value == ('extu', 8, 4)
    assert word(0x3b0f8, 4) + 0xe == 0xffff3976
    assert instruction(0x3aea0).access == sh2.Access('gbr', 0xe, 1, 'load')
    assert instruction(0x3aea4).value == ('shl', 1)
    assert word(0x3b0fc, 4) + 4 == 0xffff101c
    assert word(0x3b0fc, 4) + 6 == 0xffff101e
    assert instruction(0x3aeac).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert instruction(0x3aeb0).value == ('addi', 1)
    assert word(0x3aeb2) == 0x2728  # TST R2,R7 tests mask bank+1, not a bit number.
    assert instruction(0x3aeb4).target == 0x3aec8 and instruction(0x3aeb4).delayed
    assert instruction(0x3aeb6).access == sh2.Access(15, 0, 2, 'store')
    assert instruction(0x3aeba).value == ('addi', 1)
    assert word(0x3aebc) == 0x275b  # OR R5,R7 preserves the other flag bits.
    assert instruction(0x3aec0).access == sh2.Access(2, 0, 2, 'store', indexed=True)
    assert instruction(0x3aec4).target == 0x3af32 and instruction(0x3aec4).delayed
    assert instruction(0x3aec6).access == sh2.Access('gbr', 0xe, 1, 'store')
    assert word(0x3b100, 4) + 0x2c == 0xffff1e48
    assert word(0x3b100, 4) + 0x2e == 0xffff1e4a
    assert instruction(0x3aed2).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert word(0x3b104, 4) == 0x9586
    assert instruction(0x3aed4).access == sh2.Access(4, 6, 2, 'load')
    assert word(0x958c) == 80
    assert instruction(0x3aed8).value == ('extu', 16, 7)
    assert instruction(0x3aeda).value == ('extu', 16, 0)
    assert instruction(0x3aede).value == ('add', 12)
    assert instruction(0x3aee0).value == ('extu', 16, 4)
    assert word(0x3aee2) == 0x3247 and instruction(0x3aee4).target == 0x3aeea
    assert instruction(0x3aee8).value == ('copy', 4)
    assert word(0x3aef2) == 0x2778 and instruction(0x3aef4).target == 0x3aefa
    assert instruction(0x3aef6).target == 0x3af26 and instruction(0x3aef6).delayed
    assert instruction(0x3aef8).value == ('const', 0xffffffff)
    assert word(0x3b0f8, 4) + 0x30 == 0xffff3998
    assert word(0x3b0f8, 4) + 0x34 == 0xffff399c
    assert instruction(0x3af02).value == ('shl', 2)
    assert instruction(0x3af04).access == sh2.Access(4, 0, 4, 'load', indexed=True)
    assert word(0x9586) == 335
    assert instruction(0x3af0c).value == ('shr', 16)
    assert instruction(0x3af0e).value == ('extu', 16, 7)
    assert word(0x3af10) == 0x0727 and word(0x3af16) == 0x0757
    assert instruction(0x3af12).value == ('extu', 16, 5)
    assert word(0x3af14) == 0x041a and word(0x3af18) == 0x021a
    assert instruction(0x3af1a).value == ('shr', 16)
    assert instruction(0x3af1c).value == ('add', 2)
    assert word(0x3b108, 4) == 0x21ce0
    assert instruction(0x3af20).flow == 'call' and instruction(0x3af20).delayed
    assert instruction(0x3af22).value == ('copy', 4)
    assert instruction(0x3af2c).value == ('extu', 16, 6)
    assert word(0x3af2e) == 0x3658
    assert instruction(0x3af30).access == sh2.Access(14, 0, 2, 'store', indexed=True)
    assert word(0x3af34) == 0x4f17 and word(0x3af36) == 0x4f16
    assert word(0x3af38) == 0x4f26
    assert instruction(0x3af3e).flow == 'return' and instruction(0x3af3e).delayed
    assert word(0x3af40) == 0x6cf6
    assert instruction(0x21ce4).target == 0x21d6a
    assert word(0x21dc8, 4) == 0xffff9818 and word(0x21dcc, 4) == 0x44e


def test_maf_initialization_previous_word_numerator_and_wrap_match_stock():
    verify_compensation(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', slice_word_samples(SLICES), ids=slice_word_ids(SLICES))
@pytest.mark.parametrize('byte', (0, 1))
def test_changed_maf_bank_mask_numerator_denominator_width_or_return_fails(address, byte, jk08a_stock_bytes):
    data = bytearray(jk08a_stock_bytes)
    data[address + byte] ^= 1
    with pytest.raises(AssertionError):
        verify_compensation(data)


def test_maf_recurrences_initialization_bits_and_widths_keep_the_scoped_contract():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    for index, bit, raw, output, correction in (
        (4, 0, 0xffff101c, 0xffff1e48, 0xffff3998),
        (5, 1, 0xffff101e, 0xffff1e4a, 0xffff399c),
    ):
        step = chain.steps[index]
        assert step['note'] == (
            f'prev = uint16({output:08x}); K = uint32({correction:08x}); '
            f'c = floor(floor(K*335/65536)/min(65535,prev+80)); '
            f'{output:08x} = uint16(uint16({raw:08x})-c)')
        assert [ref.address for ref in step['via']] == [0x3ae8a, 0x21ce0]
        source = model.meaning_of(SymbolKey('7mfk', 'ram', raw))
        symbol = model.symbols[SymbolKey('7mfk', 'ram', output)]
        assert symbol.value('width') == 16 and symbol.value('signed') is False
        assert symbol.meaning.props['level'] == 'code'
        [copy] = [link for link in symbol.meaning.links if link.type == 'copy']
        assert copy.to is source and copy.stated == {'7mfk'}
        assert [ref.address for ref in copy.props['via']] == [0x3ae8a]
        [selector] = [link for link in symbol.meaning.links if link.type == 'selector']
        assert selector.to.key == 'shapeless-bandicoot/ram' and selector.slot == f'bit{bit}'
        assert selector.stated == {'7mfk'}
        assert f'initialization mask {bit + 1}' in selector.props['note']
        inputs = [link for link in symbol.meaning.links if link.type == 'input']
        assert len(inputs) == 2
        assert {link.to.key for link in inputs} == {
            source.key, model.meaning_of(SymbolKey('7mfk', 'ram', correction)).key}
        for link in inputs:
            assert link.stated == {'7mfk'}
            assert [ref.address for ref in link.props['via']] == [0x3ae8a, 0x21ce0]
        numerator = model.symbols[SymbolKey('7mfk', 'ram', correction)]
        assert numerator.value('width') == 32 and numerator.value('signed') is False
        assert numerator.meaning.props.get('level') is None

    flags = model.symbols[SymbolKey('7mfk', 'ram', 0xffff3976)]
    assert flags.value('width') == 8 and flags.value('signed') is False
    assert flags.value('unit') == 'bitfield' and flags.meaning.props.get('level') is None
    producer = model.meaning_of(SymbolKey('7mfk', 'fn', 0x3ae8a))
    assert producer.props['level'] == 'code'
    thresholds = [link for link in producer.links if link.type == 'threshold']
    assert {link.to.key for link in thresholds} == {'ginger-stingray/ram', 'careful-penguin/ram'}
    for link in thresholds:
        assert link.stated == {'7mfk'} and 'strictly positive' in link.props['note']
        assert 'uint16(raw+1)' in link.props['note'] and 'explicit direct entry' in link.props['note']
    assert 'masks 1 and 2' in producer.props['summary'] and 'bit0 and bit1' in producer.props['summary']
