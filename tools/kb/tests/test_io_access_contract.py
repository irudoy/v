"""Bounded I/O fixtures preserve stock bytes and separate storage domains."""

import pytest

from kb import io_access_contract as contract, io_access_matrix as matrix
from kb import io_access_semantics as numeric, repo


def test_fixture_changes_only_four_separately_assembled_returns():
    declared = contract.descriptor(repo.ROOT)
    image = repo.images()['JK08A'].path.read_bytes()
    fixture, aliases, boundaries = contract.independent_fixture(declared, image)
    restored = bytearray(fixture)
    assert aliases == []
    assert [row['address'] for row in boundaries] == [0x205A, 0xA6DE8, 0xA6EB0, 0xC307A]
    for row in boundaries:
        restored[row['address']:row['end']] = bytes.fromhex(row['stock'])
    assert bytes(restored) == image
    for first, last in contract.SPANS:
        assert fixture[first:last] == image[first:last]
    assert declared['native_io'] == [dict(start=start, size=size) for start, size in matrix.NATIVE_IO]


@pytest.mark.parametrize('flag', contract.FLAGS)
def test_descriptor_refuses_implicit_admission(tmp_path, flag):
    path = tmp_path / contract.DESCRIPTOR
    path.parent.mkdir(parents=True)
    path.write_text((repo.ROOT / contract.DESCRIPTOR).read_text().replace(flag + ' = false', flag + ' = true', 1))
    with pytest.raises(ValueError):
        contract.descriptor(tmp_path)


def test_capture_keeps_uint32_native_word_separate_from_low_word_operand():
    assert numeric.capture(0xF00DCAFE, 0xA1B2C3D4) == dict(
        raw_word=0xA1B2C3D4, low_word=0xC3D4, packed=0xCAFEC3D4)


def test_mailbox26_stock_inactive_record_has_exact_word_lanes_without_hardware_admission():
    before = bytes([0xA5]) * 65536
    result = numeric.mailbox(bytes.fromhex('05000000'), 25, 0x12345678, before)
    assert result['address'] == 0xFFFFDC40
    assert result['words'] == ((0, 0), (2, 0), (4, 0x0700), (6, 0), (16, 0), (18, 0))
    assert result['mask'] == 0x12345678
    assert result['memory'][0xDC44:0xDC46] == bytes.fromhex('0700')
    assert result['memory'][0xDC48:0xDC50] == before[0xDC48:0xDC50]


def test_monitor_entry_six_keeps_its_own_mask_and_disabled_caller_premise():
    image = repo.images()['JK08A'].path.read_bytes()
    table = image[0x23AC4:0x23AC4 + 392]
    assert image[0x18700] == 0
    assert numeric.monitor(table, 6, 4) == dict(offset=336, pointer=0xFFFFF754, mask=4, unmasked=False)
    assert numeric.monitor(table, 6, 0x0800)['unmasked'] is True
    assert numeric.monitor(table, 0, 0x0800)['unmasked'] is False


def test_document_identifies_actual_sites_and_explicit_return_boundaries():
    text = (repo.ROOT / 'defs/JK08A.io-accesses.md').read_text()
    for address in (0x2040, 0x204E, 0x205A, 0x2B768, 0xA6DC8, 0xA6EA4, 0xC3058,
                    0xFFFFDC40, 0xFFFFF430, 0xFFFFF754):
        assert f'`{address:08X}`' in text
    assert 'flat storage' in text and 'configured-disabled' in text
