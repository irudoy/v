"""The DTC registry projection must be reproducible from the exact images."""

from pathlib import Path

import pytest

from tools.mapkit import dtc_projection
from tools.mapkit import rom as romkit


DEFS = Path(dtc_projection.DEFS)
EXPECTED_CODE_COUNT = {
    "JK00C": 36,
    "JK00D": 36,
    "JK78C": 35,
    "1ND0A": 35,
    "1ND3B": 35,
}
ATTRIBUTE_ALPHABET = {"00a0", "0030", "00b0", "0000"}


@pytest.fixture(scope="module")
def source():
    return dtc_projection.read_registry(dtc_projection.SOURCE_ROM), \
        romkit.load(dtc_projection.SOURCE_ROM).data


def test_canonical_attributes_come_from_the_pointer_table(source):
    """Every canonical attribute address is the image's own stored pointer."""
    rows, data = source
    tables = dtc_projection.locate_tables(data)
    for row in rows:
        index = int(row["index"], 10)
        assert tables.record_address(index) == int(row["record_addr"], 16)
        assert tables.attribute_address(data, index) == int(
            row["attribute_addr"], 16
        )


@pytest.mark.parametrize("rom", sorted(EXPECTED_CODE_COUNT))
def test_tracked_registry_matches_projection(rom, source):
    rows, data = source
    projected, _ = dtc_projection.project(rom, source_rows=rows, source=data)
    assert dtc_projection.read_registry(rom) == projected
    assert len(projected) == EXPECTED_CODE_COUNT[rom]


@pytest.mark.parametrize("rom", sorted(EXPECTED_CODE_COUNT))
def test_projected_records_hold_their_code_and_attribute(rom):
    data = romkit.load(rom).data
    for row in dtc_projection.read_registry(rom):
        record_addr = int(row["record_addr"], 16)
        record = data[record_addr:record_addr + dtc_projection.RECORD_SIZE]
        assert dtc_projection.dtc_code(record) == row["dtc"]
        attribute = int(row["attribute_addr"], 16)
        assert data[attribute:attribute + 2].hex() == row["stock_attribute"]
        assert row["stock_attribute"] in ATTRIBUTE_ALPHABET


@pytest.mark.parametrize("rom", sorted(dtc_projection.INHERITED_ROMS))
def test_exact_code_members_reproduce_the_canonical_registry(rom, source):
    """Same-address family members share one registry instead of tracking a copy."""
    rows, data = source
    projected, dropped = dtc_projection.project(rom, source_rows=rows, source=data)
    assert dropped == []
    assert projected == [
        {field: row[field] for field in dtc_projection.FIELDS} for row in rows
    ]
    assert not (DEFS / f"{rom}.dtc.csv").exists()


def test_p1422_is_absent_from_vq37():
    """VQ37 declares no P1422 record, so the code is dropped rather than guessed."""
    for rom in ("JK78C", "1ND0A", "1ND3B"):
        _, dropped = dtc_projection.project(rom)
        assert [code for code, _, _ in dropped] == ["P1422"]
