from collections import Counter
from dataclasses import replace
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
    assert end == 0x328C0
    assert sum(end - start for start, end in sid22_inventory.PUBLISHER_BODY_RANGES) == 1256
    assert image[0x328B4:0x328B8] == bytes.fromhex('000b6cf6')
    assert image[0x328B8:0x328C0] == bytes.fromhex('0002ec9a00034114')


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


def test_1ek7a_publisher_literals_bind_the_six_tables():
    layout = sid22_inventory.VQ37_1EK7A
    image = sid22_inventory.load_exact_rom(layout=layout)
    assert (layout.publisher_start, layout.publisher_end) == (0x3BF98, 0x3C57C)
    assert image[0x3C542:0x3C546] == bytes.fromhex("000b69f6")
    literals = (0x3C574, 0x3C560, 0x3C548, 0x3C284, 0x3C264, 0x3C280)
    assert [
        int.from_bytes(image[address:address + 4], "big") for address in literals
    ] == [family.table_start for family in layout.families]
    assert image[0x3C288:0x3C290] == bytes.fromhex("fffed8aafffeded5")


def test_1ek7a_inventory_reports_exact_declared_sources():
    entries = sid22_inventory.read_inventory(layout=sid22_inventory.VQ37_1EK7A)
    assert Counter(entry.did >> 8 for entry in entries) == {
        0x11: 87, 0x12: 68, 0x13: 19, 0x14: 31, 0x15: 20, 0x16: 64,
    }
    by_did = {entry.did: entry for entry in entries}
    expected = {
        0x1100: (4, (0x00013A79,), "sequential"),
        0x1101: (1, (0xFFFE809D,), "single"),
        0x1201: (2, (0xFFFE81FC,), "sequential"),
        0x120B: (2, (), "dynamic"),
        0x1302: (2, (0xFFFEAA9C, 0x00013B39), "paired"),
        0x1401: (1, (0xFFFED8AA,), "conditional"),
        0x1402: (1, (0xFFFED8AB,), "conditional"),
        0x1517: (2, (0xFFFEA141, 0x00013727), "paired"),
        0x1600: (4, (0x00013AA5,), "sequential"),
        0x1601: (1, (0x000230E2,), "single"),
    }
    for did, contract in expected.items():
        entry = by_did[did]
        assert (entry.width, entry.sources, entry.source_layout) == contract
    assert not {0x1315, 0x1316, 0x1317}.intersection(by_did)


def test_1ek7a_rejects_changed_images_and_table_contracts(tmp_path):
    layout = sid22_inventory.VQ37_1EK7A
    image = sid22_inventory.load_exact_rom(layout=layout)
    changed = tmp_path / "1EK7A.bin"
    changed.write_bytes(image[:-1] + bytes([image[-1] ^ 1]))
    with pytest.raises(sid22_inventory.InventoryError, match="expected 1EK7A SHA-256"):
        sid22_inventory.read_inventory(changed, layout=layout)
    with pytest.raises(sid22_inventory.InventoryError, match="publisher bytes"):
        sid22_inventory.read_inventory(layout=replace(layout, publisher_start=0x3BF9A))
    first, *rest = layout.families
    families = (replace(first, table_end=first.table_end - 4), *rest)
    with pytest.raises(sid22_inventory.InventoryError, match="family 0x11 table bytes"):
        sid22_inventory.read_inventory(layout=replace(layout, families=families))


def test_1me3b_rear_oxygen_dids_use_the_family_11_byte_publisher():
    layout = sid22_inventory.VQ37_1ME3B
    image = sid22_inventory.load_exact_rom(layout=layout)
    literals = (0x3B5E4, 0x3B5D0, 0x3B5B8, 0x3B2F4, 0x3B2D4, 0x3B2F0)
    assert [
        int.from_bytes(image[address:address + 4], "big") for address in literals
    ] == [family.table_start for family in layout.families]
    entries = sid22_inventory.build_inventory(image, layout=layout)
    assert Counter(entry.did >> 8 for entry in entries) == {
        0x11: 85, 0x12: 68, 0x13: 19, 0x14: 31, 0x15: 20, 0x16: 64,
    }
    by_did = {entry.did: entry for entry in entries}
    for did, record, source in (
        (0x111A, 0x22B4C, 0xFFFE8168),
        (0x111B, 0x22B50, 0xFFFE8169),
    ):
        entry = by_did[did]
        assert (entry.record_address, entry.width, entry.sources, entry.source_layout) == (
            record, 1, (source,), "single",
        )
    assert by_did[0x120B].source_layout == "dynamic"
    assert by_did[0x1401].source_layout == "conditional"


@pytest.mark.parametrize(
    ("rom", "table", "coolant", "intake_air"),
    [
        ("JK08A", 0x226AC, 0xFFFF1079, 0xFFFF2837),
        ("1ND0A", 0x22A70, 0xFFFE8079, 0xFFFE98AA),
        ("1ND3B", 0x22A70, 0xFFFE8079, 0xFFFE98AA),
        ("JK00C", 0x22738, 0xFFFF107F, 0xFFFF28D6),
        ("JK00D", 0x22738, 0xFFFF107F, 0xFFFF28EA),
        ("JK78C", 0x22718, 0xFFFF106F, 0xFFFF278A),
    ],
)
def test_temperature_records_and_conditional_status_bytes(rom, table, coolant, intake_air):
    layout = sid22_inventory.LAYOUTS[rom]
    entries = sid22_inventory.read_inventory(layout=layout)
    by_did = {entry.did: entry for entry in entries}
    for low, source in ((1, coolant), (6, intake_air)):
        entry = by_did[0x1100 | low]
        assert (entry.record_address, entry.width, entry.sources, entry.source_layout) == (
            table + low * 4, 1, (source,), "single",
        )
    assert (by_did[0x120B].width, by_did[0x120B].source_layout) == (2, "dynamic")
    assert by_did[0x1401].source_layout == by_did[0x1402].source_layout == "conditional"


@pytest.mark.parametrize("rom", ["JK00A", "JK03A", "JK03B"])
def test_7mfk_images_share_the_exact_publisher_and_pointer_tables(rom, entries):
    assert sid22_inventory.read_inventory(layout=sid22_inventory.LAYOUTS[rom]) == entries


@pytest.mark.parametrize(
    ("rom", "table", "bank1", "bank2", "total"),
    [
        ("JK08A", 0x2289C, 0xFFFF101C, 0xFFFF101E, 0xFFFF3852),
        ("JK00C", 0x22938, 0xFFFF1024, 0xFFFF1026, 0xFFFF396E),
        ("JK00D", 0x22938, 0xFFFF1024, 0xFFFF1026, 0xFFFF3982),
        ("JK78C", 0x22918, 0xFFFF1024, 0xFFFF1026, 0xFFFF3A9A),
        ("1ND0A", 0x22C70, 0xFFFE8024, 0xFFFE8026, 0xFFFEAD0A),
        ("1ND3B", 0x22C70, 0xFFFE8024, 0xFFFE8026, 0xFFFEAD0A),
        ("1ME3B", 0x22CE4, 0xFFFE8024, 0xFFFE8026, 0xFFFEAE4E),
        ("1EK7A", 0x22D78, 0xFFFE8028, 0xFFFE802A, 0xFFFEB186),
    ],
)
def test_maf_records_return_two_sequential_bytes(rom, table, bank1, bank2, total):
    entries = sid22_inventory.read_inventory(layout=sid22_inventory.LAYOUTS[rom])
    by_did = {entry.did: entry for entry in entries}
    for low, source in ((4, bank1), (5, bank2), (9, total)):
        entry = by_did[0x1200 | low]
        assert (entry.record_address, entry.width, entry.sources, entry.source_layout) == (
            table + low * 4, 2, (source,), "sequential",
        )
