"""Bind complete per-bank MAF arithmetic, mode selection, state, and stock return."""

import hashlib

import pytest

from kb import compile, derive, repo, sh2
from kb.model import SymbolKey


SPANS = (
    (0x224fa, 0x22508, '425d05c23b3b52262420a2b20dd9f3a5475c099e0ccb66737be91ebbbcc2c2c6'),
    (0x3af42, 0x3b098, 'e1e0972607e366267948addbcc6f229f657fa2f16f6ebcb5dca303835079b8aa'),
    (0x3b09a, 0x3b0f0, '6f436b9963e35215dd981042976b0ce82b6a33fe5429ba6102571e39c43a91fa'),
    (0x3b12c, 0x3b224, '5fb95346e215e4338bec4d032f6451830998000e088017af8cc7f9b0193d278c'),
    (0x82b6, 0x82b9, '61bbfa4ac8e6b33dab39b0f94ee6abe694277ff5cd81b92c4dec609518371a80'),
    (0x82bd, 0x82be, '3973e022e93220f9212c18d0d0c543ae7c309e46640da93a4a0314de999f5112'),
    (0x8ac3, 0x8ac4, '76be8b528d0075f7aae98d6fa57a6d3c83ae480a8469e668d7b0af968995ac71'),
    (0x3b098, 0x3b09a, '4b3a43f592f577fcfcb5b0e1f42bec5182c9edc414e1f667528f56e7cf0be11d'),
    (0x3b0f0, 0x3b0f2, 'fc5c2283015b212d975b85e56b2a75aac4b50bd5aba30cbe74f62857c380bd47'),
    (0x3b10c, 0x3b12c, 'eba6bc74c0be6929801f8c67ba8249eeaed98c05426d7f9c828797b4b4baf871'),
    (0x3b37c, 0x3b38c, '9f8f6bbfa6e3ecf00d92032e4da1f5fa91865ad42ff4301b29abccb06969c9ac'),
)


def verify_contribution(data):
    for start, end, expected in SPANS:
        assert hashlib.sha256(data[start:end]).hexdigest() == expected, f'{start:08x}'

    def word(address, size=2):
        return int.from_bytes(data[address:address + size], 'big')

    def instruction(address):
        return sh2.decode(word(address), address)

    assert instruction(0x3af4c).value == ('pool', 0x3b10c, 4)
    assert word(0x3b10c, 4) == 0xffff1dec
    assert instruction(0x3af68).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert instruction(0x3af70).value == ('extu', 16, 5)
    for address, opcode in ((0x3af60, 0xc980), (0x3af76, 0xc808), (0x3af88, 0xc801)):
        assert word(address) == opcode
    assert instruction(0x3af82).access == sh2.Access(2, 0, 1, 'store', indexed=True)
    assert word(0x3b118, 4) + 3 == 0xffff43ca
    assert instruction(0x3afbe).access == sh2.Access(2, 0, 2, 'load', indexed=True)
    assert instruction(0x3afd8).access == sh2.Access(5, 0, 2, 'load', indexed=True)
    assert instruction(0x3b02e).access == sh2.Access(6, 0, 2, 'store', indexed=True)
    assert instruction(0x3b080).access == sh2.Access(6, 0, 2, 'load', indexed=True)
    assert instruction(0x3b0b8).access == sh2.Access(6, 0, 2, 'load', indexed=True)
    assert word(0x3b136) == 0x4611
    assert instruction(0x3b13a).access == sh2.Access(2, 0, 2, 'store', indexed=True)
    assert instruction(0x3b154).flow == 'call' and instruction(0x3b154).delayed
    assert word(0x3b380, 4) == 0x224fa
    assert word(0x3b156) == 0x6023
    assert [word(address) for address in range(0x224fa, 0x22508, 2)] == [0x4021]*5 + [0x000b, 0x4021]
    assert instruction(0x3b190).access == sh2.Access(2, 0, 4, 'store', indexed=True)
    assert instruction(0x3b1c2).access == sh2.Access(2, 0, 2, 'store', indexed=True)
    assert instruction(0x3b1d4).access == sh2.Access(2, 0, 4, 'load', indexed=True)
    assert instruction(0x3b202).access == sh2.Access(2, 0, 4, 'store', indexed=True)
    assert instruction(0x3b214).access == sh2.Access(2, 0, 2, 'store', indexed=True)
    assert instruction(0x3b220).flow == 'return' and instruction(0x3b220).delayed
    assert word(0x3b222) == 0x6df6
    assert data[0x82b6:0x82b9] == bytes((77, 12, 255))
    assert data[0x82bd] == 45 and data[0x8ac3] == 128


def test_maf_contribution_modes_signed_rounding_state_caps_and_natural_return_match_stock():
    verify_contribution(derive.image_bytes(repo.layout('7mfk')))


@pytest.mark.parametrize('address', [address for start, end, _ in SPANS
                                    for address in range(start, end)])
def test_changed_maf_contribution_instruction_state_width_coefficient_pool_or_return_fails(address):
    data = bytearray(derive.image_bytes(repo.layout('7mfk')))
    data[address] ^= 1
    with pytest.raises(AssertionError):
        verify_contribution(data)


def test_maf_contribution_keeps_bank_state_widths_arithmetic_inputs_and_mode_boundaries():
    model = compile.cached(repo.ROOT)
    chain = model.entities[('chain', 'airflow_load')]
    for bank, input, reference, delta, correction, magnitude, base, output in (
        (1, 'ffff1df0', 'ffff1e08', 'ffff1e18', 'ffff1e1c', 'ffff1e30', 'ffff1e00', 'ffff1df8'),
        (2, 'ffff1df2', 'ffff1e0a', 'ffff1e1a', 'ffff1e1e', 'ffff1e32', 'ffff1e02', 'ffff1dfc'),
    ):
        step = chain.steps[11 + bank]
        note = step['note']
        assert [ref.address for ref in step['via']] == [0x3af42]
        assert f'uint16({input})-uint16({reference})' in note
        assert 'ROM8[0x000082bd]' in note and '/8)' in note
        assert f'{base} = b' in note and 'clamp(a,0,65535)' in note
        assert f'uint16({magnitude})+a-b,-0xffffff,0xffffff)' in note
        assert f'b-uint16({delta})' in note and '/512)' in note
        assert f'int16({correction})/256),-32768,32767)' in note
        assert f'{correction} = d' in note and '64*min(0,d))/64)' in note
        assert f'{output} = clamp(v+e,0,0xffffff)' in note
        sign = '(ffff1e34&1)' if bank == 1 else '((ffff1e34&2)>>1)'
        assert f'(2*{sign}-1)' in note
        meaning = model.meaning_of(SymbolKey('7mfk', 'ram', int(output, 16)))
        inputs = [link for link in meaning.links if link.type == 'input']
        assert {link.to.key for link in inputs} == {
            'vegan-polecat/ram' if bank == 1 else 'spiked-dalmatian/ram',
            f'maf_base_reference_b{bank}/ram', f'maf_delta_reference_b{bank}/ram',
            f'maf_correction_state_b{bank}/ram', f'maf_residual_magnitude_b{bank}/ram',
            f'maf_fallback_reference_b{bank}/ram', 'maf_residual_signs/ram',
        }
        selectors = [link for link in meaning.links if link.type == 'selector']
        assert {link.to.key for link in selectors} == {
            'burrowing-platypus/ram', 'slick-bullfinch/ram', 'splendid-cheetah/ram',
            f'maf_fallback_latch_b{bank}/ram',
        }
        for link in (*inputs, *selectors):
            assert link.stated == {'7mfk'}
            assert [ref.address for ref in link.props['via']] == [0x3af42]
            assert any(evidence.get('kind') == 'test' for evidence in link.evidence)
        assert any('If v<0' in note and 'even when v+e is positive' in note
                   for note in meaning.props['note'])
        assert 'signed' in meaning.props['summary']
    for name, first, width, signed in (
        ('maf_base',0xffff1e00,16,False), ('maf_base_reference',0xffff1e08,16,False),
        ('maf_fallback_reference',0xffff1e10,32,False), ('maf_delta_reference',0xffff1e18,16,False),
        ('maf_correction_state',0xffff1e1c,16,True), ('maf_residual_magnitude',0xffff1e30,16,False),
    ):
        for bank, offset in ((1,0),(2,4 if width == 32 else 2)):
            symbol = model.symbols[SymbolKey('7mfk','ram',first+offset)]
            assert symbol.meaning.key == f'{name}_b{bank}/ram'
            assert symbol.value('width') == width and symbol.value('signed') is signed
            assert symbol.value('level') == 'code'
            assert 'width' not in symbol.meaning.props and 'signed' not in symbol.meaning.props
            assert any('Physical identity' in note for note in symbol.meaning.props['note'])
    for address, name in ((0xffff1e34,'maf_residual_signs'),
                          (0xffff43ca,'maf_fallback_latch_b1'),
                          (0xffff43cb,'maf_fallback_latch_b2')):
        symbol = model.symbols[SymbolKey('7mfk','ram',address)]
        assert symbol.meaning.key == name+'/ram'
        assert symbol.value('width') == 8 and symbol.value('signed') is False
    flag = model.meaning_of(SymbolKey('7mfk','ram',0xffff24b8))
    assert 'Bit 2' in flag.props['summary'] and any('bit 3' in note for note in flag.props['note'])
    function = model.meaning_of(SymbolKey('7mfk','fn',0x3af42))
    assert any('5782,5939,6094,6249,6403' in note for note in function.props['note'])
    assert any('physical meanings' in note.lower() for note in function.props['note'])
