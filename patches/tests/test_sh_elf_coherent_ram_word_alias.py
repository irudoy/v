"""Overlapping RAM word windows preserve one address translation and exact code."""
from dataclasses import replace

import pytest

from patches.tests import test_sh_elf_ram_word_alias as original
from tools.kb.tests import test_injection_start_delay_chain as publication


@pytest.mark.parametrize('nested', (False, True))
@pytest.mark.parametrize('reverse', (False, True))
def test_coherent_overlap_preserves_pool_bytes_code_and_shared_storage(nested, reverse):
    stock, region, image = original.inputs()
    image = bytearray(image)
    image[0x1002:0x1004] = bytes.fromhex('84ee' if nested else '84ef')
    rows = ((0x1000, 0xffff84ec, 0x7e00, 8),
            (0x1002, 0xffff84ee if nested else 0xffff84ef,
             0x7e02 if nested else 0x7e03, 3 if nested else 6))
    if reverse:
        rows = rows[::-1]
    region = replace(region, ram_word_literals=rows)
    assert stock.ram_word_aliases(region, image) == rows
    expected = bytearray(image)
    for pool, _, alias, _ in rows:
        expected[pool:pool + 2] = alias.to_bytes(2, 'big')
    expected[0x1004:0x1008] = bytes.fromhex('0100128c')
    expected[0x2010:0x2014] = bytes.fromhex('000b0009')
    fixture = stock.build_fixture(region, image)
    assert fixture == expected
    assert fixture[region.start:region.end] == image[region.start:region.end]
    first, second = rows
    lower = max(first[1], second[1])
    upper = min(first[1] + first[3], second[1] + second[3])
    assert lower < upper
    storage = bytearray(0x8000)
    for address in range(lower, upper):
        first_alias = first[2] + address - first[1]
        second_alias = second[2] + address - second[1]
        assert first_alias == second_alias
        storage[first_alias] = (address * 17) & 255
        assert storage[second_alias] == (address * 17) & 255


@pytest.mark.parametrize('reverse', (False, True))
def test_exact_feedback_words_bind_nested_windows_without_instruction_changes(reverse):
    stock = publication.stock_module()
    image = stock.stock_image('JK08A')
    rows = ((0x5cbe8, 0xffff88b4, 0x6000, 0x124),
            (0x5d744, 0xffff89cc, 0x6118, 14))
    assert image[0x5cbe8:0x5cbea] == bytes.fromhex('88b4')
    assert image[0x5d744:0x5d746] == bytes.fromhex('89cc')
    if reverse:
        rows = rows[::-1]
    region = stock.Region(key='coherent-feedback-word-contract', rom='JK08A',
        source='probe.s', harness='probe.c', start=0x5ca8c, end=0x5cbe8,
        callees=((0x5d66c, 0x5d6ae),), pools=((0x5cbe8, 4), (0x5d744, 4)),
        ram_literals=(), cases=0, boundary=False, ram_word_literals=rows)
    assert stock.ram_word_aliases(region, image) == rows
    expected = bytearray(image)
    expected[0x5cbe8:0x5cbea] = bytes.fromhex('6000')
    expected[0x5d744:0x5d746] = bytes.fromhex('6118')
    assert stock.build_fixture(region, image) == expected
    for start, end in region.code_spans:
        assert expected[start:end] == image[start:end]


@pytest.mark.parametrize('reverse', (False, True))
@pytest.mark.parametrize('kind', ('translation-plus', 'translation-minus', 'same-origin-extent',
                                'origin-only-overlap', 'alias-only-overlap', 'duplicate-pool'))
def test_partial_overlap_refuses_conflicting_translation_extent_and_pool(kind, reverse):
    stock, region, image = original.inputs()
    image = bytearray(image)
    rows = [(0x1000, 0xffff84ec, 0x7e00, 8), (0x1002, 0xffff84ee, 0x7e02, 3)]
    if kind == 'translation-plus':
        rows[1] = (0x1002, 0xffff84ee, 0x7e03, 3)
    elif kind == 'translation-minus':
        rows[1] = (0x1002, 0xffff84ee, 0x7e01, 3)
    elif kind == 'same-origin-extent':
        rows[1] = (0x1002, 0xffff84ec, 0x7e00, 3)
    elif kind == 'origin-only-overlap':
        rows[1] = (0x1002, 0xffff84ee, 0x7d00, 3)
    elif kind == 'alias-only-overlap':
        rows[1] = (0x1002, 0xffff85ec, 0x7e02, 3)
    elif kind == 'duplicate-pool':
        rows[1] = rows[0]
    for pool, address, _, _ in rows:
        image[pool:pool + 2] = (address & 65535).to_bytes(2, 'big')
    if reverse:
        rows.reverse()
    region = replace(region, ram_word_literals=tuple(rows))
    with pytest.raises(stock.VerificationError):
        stock.build_fixture(region, image)
