import hashlib

import pytest

from tools.diagnostics import sid22_inventory


@pytest.fixture(scope="module")
def entries():
    return sid22_inventory.read_inventory()


def test_exact_rom_and_publisher_are_sha_locked():
    image = sid22_inventory.load_exact_rom()
    assert hashlib.sha256(image).hexdigest() == sid22_inventory.ROM_SHA256
    start = sid22_inventory.PUBLISHER_ADDRESS
    end = start + sid22_inventory.PUBLISHER_SIZE
    assert hashlib.sha256(image[start:end]).hexdigest() == (
        sid22_inventory.PUBLISHER_SHA256
    )


def test_declared_inventory_counts(entries):
    counts = {
        high: sum(entry.did >> 8 == high for entry in entries)
        for high in range(0x11, 0x17)
    }
    assert counts == {
        0x11: 82,
        0x12: 60,
        0x13: 20,
        0x14: 31,
        0x15: 19,
        0x16: 64,
    }
    assert len(entries) == 276


def test_tuning_sources_match_exact_pointer_records(entries):
    by_did = {entry.did: entry for entry in entries}
    expected = {
        0x1101: (1, (0xFFFF1079,), "single"),
        0x1134: (1, (0xFFFF22E8,), "single"),
        0x1164: (1, (0xFFFF2324,), "single"),
        0x1165: (1, (0xFFFF2325,), "single"),
        0x1201: (2, (0xFFFF11F4,), "sequential"),
        0x1225: (2, (0xFFFF2780,), "sequential"),
        0x1226: (2, (0xFFFF2782,), "sequential"),
        0x122D: (2, (0xFFFF1AB0,), "sequential"),
        0x122E: (2, (0xFFFF1AB2,), "sequential"),
        0x122F: (2, (0xFFFF1AAC,), "sequential"),
        0x1230: (2, (0xFFFF1AAE,), "sequential"),
        0x1249: (2, (0xFFFF45A0,), "sequential"),
        0x124A: (2, (0xFFFF45A2,), "sequential"),
        0x1302: (2, (0xFFFF3342, 0x00011E41), "paired"),
    }
    for did, contract in expected.items():
        entry = by_did[did]
        assert (entry.width, entry.sources, entry.source_layout) == contract


def test_dynamic_did_120b_is_not_lost_as_an_empty_pointer(entries):
    entry = next(entry for entry in entries if entry.did == 0x120B)
    assert entry.width == 2
    assert entry.sources == ()
    assert entry.source_layout == "dynamic"


def test_only_three_families_have_explicit_index_bounds():
    assert {
        family.high_byte: family.bounded_in_publisher
        for family in sid22_inventory.FAMILIES
    } == {
        0x11: False,
        0x12: False,
        0x13: True,
        0x14: False,
        0x15: True,
        0x16: True,
    }
