"""Prepared checksum words preserve independent scalar arithmetic and live input."""

import random
from unittest import mock

import pytest

from patches import rom_checksums as checksums
from tools import rom_homology


def scalar(data, start, end, width, excluded):
    total, xor_value = 0, 0
    for offset in range(start, end, width):
        if offset not in excluded:
            value = int.from_bytes(data[offset:offset + width], 'big')
            total += value
            xor_value ^= value
    return total & ((1 << (8 * width)) - 1), xor_value


@pytest.mark.parametrize('width', [2, 4])
@pytest.mark.parametrize('prefix', [0, 1, 3])
@pytest.mark.parametrize('excluded', [frozenset(), frozenset([0, 2, 4, 6, 15, 16, 1024])])
def test_full_and_unaligned_word_ranges_match_independent_scalar_arithmetic(width, prefix, excluded):
    generator = random.Random(8127)
    words = [0, 1, 255, 256, 32767, 32768, 65534, 65535]
    if width == 4:
        words += [65536, 0x7fffffff, 0x80000000, 0xfffffffe, 0xffffffff]
    words += [generator.randrange(1 << (8 * width)) for _ in range(256)]
    data = b'X' * prefix + b''.join(value.to_bytes(width, 'big') for value in words) + b'Y'
    end = len(data) - 1
    expected, xor_value = scalar(data, prefix, end, width, excluded)
    if width == 2:
        assert checksums._sum16(data, prefix, end, excluded) == expected
    else:
        assert checksums._runtime32(data, prefix, end, excluded) == (xor_value, expected)


def test_every_unsigned_16_bit_value_and_wraparound_match_scalar_arithmetic():
    data = b''.join(value.to_bytes(2, 'big') for value in range(65536))
    expected, _ = scalar(data, 0, len(data), 2, frozenset())
    assert expected == 32768
    assert checksums._sum16(data, 0, len(data)) == expected


@pytest.mark.parametrize('width', [2, 4])
def test_exclusions_zero_only_visited_words_and_preserve_input(width):
    words = [1, (1 << (8 * width)) - 1, 256, 7]
    data = bytearray(b'P' + b''.join(value.to_bytes(width, 'big') for value in words) + b'S')
    original = bytes(data)
    excluded = frozenset([1, 1 + 2 * width, 2, len(data), -1])
    prepared = checksums._native_words(data, 1, len(data) - 1, width, excluded)
    assert list(prepared) == [0, words[1], 0, 7]
    assert bytes(data) == original
    prepared[-1] = 0
    assert bytes(data) == original


@pytest.mark.parametrize('width', [2, 4])
def test_every_call_recomputes_current_bytes_without_sharing_a_result(width):
    data = bytearray((1).to_bytes(width, 'big') + (2).to_bytes(width, 'big'))
    first = checksums._native_words(data, 0, len(data), width, frozenset())
    data[-1] = 3
    second = checksums._native_words(data, 0, len(data), width, frozenset())
    assert list(first) == [1, 2] and list(second) == [1, 3]
    expected, xor_value = scalar(data, 0, len(data), width, frozenset())
    if width == 2:
        assert checksums._sum16(data, 0, len(data)) == expected
    else:
        assert checksums._runtime32(data, 0, len(data)) == (xor_value, expected)


@pytest.mark.parametrize('width', [2, 4])
@pytest.mark.parametrize('start,end', [(0, 0), (4, 4), (4, 0), (0, 5), (-3, 12), (0, 16)])
@pytest.mark.parametrize('excluded', [frozenset([0, 2]), {0, 2}, [0, 2], frozenset([0.0, 'x'])])
def test_partial_empty_and_general_arguments_preserve_scalar_behavior(width, start, end, excluded):
    data = bytes(range(11))
    expected, xor_value = scalar(data, start, end, width, excluded)
    if width == 2:
        assert checksums._sum16(data, start, end, excluded) == expected
    else:
        assert checksums._runtime32(data, start, end, excluded) == (xor_value, expected)


@pytest.mark.parametrize('width', [2, 4])
def test_nonstandard_buffers_and_native_widths_keep_the_scalar_reader(width):
    data = memoryview(bytes(range(12)))
    expected, xor_value = scalar(data, 0, len(data), width, frozenset())
    assert checksums._native_words(data, 0, len(data), width, frozenset()) is None
    with mock.patch.object(checksums, 'array', return_value=mock.Mock(itemsize=8)):
        if width == 2:
            assert checksums._sum16(bytes(data), 0, len(data)) == expected
        else:
            assert checksums._runtime32(bytes(data), 0, len(data)) == (xor_value, expected)


@pytest.mark.slow
def test_registered_image_domains_match_scalar_words_and_stored_references():
    images = rom_homology.load_images()
    for name, image in images.items():
        layout = checksums.layout_for_rom(name)
        before = image.data
        actual = checksums.calculate_values(before, layout)
        for domain in layout.sum16_domains:
            expected, _ = scalar(before, domain.start, domain.end, 2, domain.exclusions)
            assert getattr(actual, domain.key) == expected
        for domain in layout.runtime32_domains:
            expected, xor_value = scalar(before, domain.start, domain.end, 4, domain.exclusions)
            assert getattr(actual, domain.key + '_sum') == expected
            assert getattr(actual, domain.key + '_xor') == xor_value
        build_layout = checksums.layout_for_rom(name, for_build=True)
        verified = checksums.require_valid(before, build_layout)
        assert actual == verified.calculated
        assert image.data == before

