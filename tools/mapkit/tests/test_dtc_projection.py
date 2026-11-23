"""The DTC registry projection must be reproducible from the exact images."""

import io
from itertools import permutations
from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from tools.mapkit import dtc_projection
from tools.mapkit import rom as romkit


DEFS = Path(dtc_projection.DEFS)
EXPECTED_CODE_COUNT = {
    "JK00C": 48,
    "JK00D": 48,
    "JK78C": 39,
    "1ND0A": 39,
    "1ND3B": 39,
    "1ME3B": 38,
    "1EK7A": 26,
}
EXHAUST_VTC_CODES = ["P0014", "P0024", "P0078", "P0084", "P1078", "P1078", "P1084", "P1084"]
EXPECTED_OMITTED = {
    "JK00C": [],
    "JK00D": [],
    "JK78C": EXHAUST_VTC_CODES + ["P1422"],
    "1ND0A": EXHAUST_VTC_CODES + ["P1422"],
    "1ND3B": EXHAUST_VTC_CODES + ["P1422"],
    "1ME3B": ["P0014", "P0024", "P0078", "P0084", "P0443", "P1078", "P1078", "P1084", "P1084", "P1422"],
    "1EK7A": sorted(EXHAUST_VTC_CODES + [
        "P0137", "P0138", "P0139", "P0157", "P0158", "P0159", "P0420",
        "P0430", "P0441", "P0442", "P0443", "P0455", "P0456", "P1422",
    ]),
}
ATTRIBUTE_ALPHABET = {"00a0", "0030", "00b0", "0020", "02a0", "0000"}


@pytest.fixture(scope="module")
def source():
    return dtc_projection.read_registry(dtc_projection.SOURCE_ROM), \
        romkit.load(dtc_projection.SOURCE_ROM).data


def test_evidence_header_is_only_accepted_for_the_canonical_registry(monkeypatch):
    header = ",".join(dtc_projection.SOURCE_FIELDS) + "\n"
    monkeypatch.setattr(Path, "open", lambda *args, **kwargs: io.StringIO(header))
    assert dtc_projection.read_registry(dtc_projection.SOURCE_ROM) == []
    for rom in dtc_projection.PROJECTED_ROMS:
        with pytest.raises(dtc_projection.DtcProjectionError, match="unexpected header"):
            dtc_projection.read_registry(rom)


def test_projected_writer_keeps_the_nine_column_header(source):
    rows, data = source
    projected, _ = dtc_projection.project("JK00D", source_rows=rows, source=data)
    assert all(tuple(row) == dtc_projection.FIELDS for row in projected)
    handle = mock_open()
    with patch.object(Path, "open", handle):
        dtc_projection.write_registry("JK00D", projected)
    rendered = "".join(call.args[0] for call in handle().write.call_args_list)
    assert rendered.splitlines()[0] == ",".join(dtc_projection.FIELDS)
    assert "evidence" not in rendered
    assert "rom_const:" not in rendered


@pytest.mark.parametrize("part,offset", [(0, 8), (1, 3), (2, 1)])
def test_a_changed_source_span_is_rejected_not_projected(part, offset, source):
    rows, data = source
    row = next(row for row in rows if row["index"] == "17")
    spans = dtc_projection.canonical_evidence(row, dtc_projection.canonical_tables(), len(data))
    address = spans[part][0]
    changed = bytearray(data)
    changed[address + offset] ^= 1
    with pytest.raises(dtc_projection.DtcProjectionError, match=f"at {address:08x} differ"):
        dtc_projection.project("JK00D", source_rows=[row], source=changed, target=data)


def test_canonical_evidence_accepts_0x_without_losing_leading_zeroes(source):
    rows, data = source
    row = next(row for row in rows if row["index"] == "17")
    prefixed = ";".join(token.replace("=", "=0x", 1) for token in row["evidence"].split(";"))
    tables = dtc_projection.canonical_tables()
    spans = dtc_projection.canonical_evidence(row, tables, len(data))
    assert dtc_projection.canonical_evidence({**row, "evidence": prefixed}, tables, len(data)) == spans
    assert [len(raw) for _, raw in spans] == [12, 4, 2]


def test_canonical_evidence_binds_spans_by_address_in_every_token_order(source):
    rows, data = source
    row = next(row for row in rows if row["index"] == "17")
    tables = dtc_projection.canonical_tables()
    expected = dtc_projection.canonical_evidence(row, tables, len(data))
    for parts in permutations(row["evidence"].split(";")):
        assert dtc_projection.canonical_evidence(
            {**row, "evidence": ";".join(parts)}, tables, len(data)) == expected
    parts = row["evidence"].split(";")
    with pytest.raises(dtc_projection.DtcProjectionError, match="complete"):
        dtc_projection.canonical_evidence(
            {**row, "evidence": ";".join([parts[0], parts[0], parts[2]])},
            tables, len(data))


@pytest.mark.parametrize("part", range(3))
@pytest.mark.parametrize("mutation", ("short", "address", "missing"))
def test_canonical_evidence_requires_every_complete_expected_span(part, mutation, source):
    rows, data = source
    row = dict(next(row for row in rows if row["index"] == "17"))
    parts = row["evidence"].split(";")
    address, value = parts[part].strip().removeprefix("rom_const:").split("=")
    if mutation == "short":
        parts[part] = f"rom_const:{address}={value[:-2]}"
    elif mutation == "address":
        parts[part] = f"rom_const:{int(address, 16) + 4:08x}={value}"
    else:
        parts.pop(part)
    row["evidence"] = ";".join(parts)
    with pytest.raises(dtc_projection.DtcProjectionError):
        dtc_projection.canonical_evidence(row, dtc_projection.canonical_tables(), len(data))


@pytest.mark.parametrize("changes", [
    {"index": "-1"}, {"index": "297"}, {"index": "18"},
    {"dtc": "P0430"}, {"dtc": "C0420"}, {"record_addr": "00019438"},
    {"attribute_addr": "0001603c"}, {"stock_attribute": "00b0"},
    {"stock_attribute": "a0"}, {"evidence": ""},
])
def test_inconsistent_canonical_rows_are_rejected(changes, source):
    rows, data = source
    row = next(row for row in rows if row["index"] == "17")
    with pytest.raises(dtc_projection.DtcProjectionError):
        dtc_projection.project("JK00D", source_rows=[{**row, **changes}], source=data, target=data)


def test_duplicate_canonical_indices_are_rejected(source):
    rows, data = source
    with pytest.raises(dtc_projection.DtcProjectionError, match="duplicate index"):
        dtc_projection.project("JK00D", source_rows=[rows[0], rows[0]], source=data, target=data)


@pytest.mark.parametrize("prefix", "PCBU")
def test_canonical_evidence_decodes_the_full_packed_code(prefix, source):
    rows, data = source
    row = dict(next(row for row in rows if row["index"] == "17"))
    parts = row["evidence"].split(";")
    record_part = next(index for index, part in enumerate(parts)
                       if part.strip().startswith(f"rom_const:{row['record_addr']}="))
    record = bytearray.fromhex(parts[record_part].split("=")[1])
    record[6] = ("PCBU".index(prefix) << 6) | 0x04
    parts[record_part] = f"rom_const:{row['record_addr']}={record.hex()}"
    row.update(dtc=f"{prefix}0420", evidence=";".join(parts))
    tables = dtc_projection.canonical_tables()
    assert dtc_projection.canonical_evidence(row, tables, len(data))[0][1] == record
    with pytest.raises(dtc_projection.DtcProjectionError, match="differs from descriptor"):
        dtc_projection.canonical_evidence({**row, "dtc": f"{prefix}0430"}, tables, len(data))


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
    attributes = {"0000", "00a0", "00a8", "00b8"} if rom == "1EK7A" else ATTRIBUTE_ALPHABET
    for row in dtc_projection.read_registry(rom):
        record_addr = int(row["record_addr"], 16)
        record = data[record_addr:record_addr + dtc_projection.RECORD_SIZE]
        assert dtc_projection.dtc_code(record) == row["dtc"]
        attribute = int(row["attribute_addr"], 16)
        assert data[attribute:attribute + 2].hex() == row["stock_attribute"]
        assert row["stock_attribute"] in attributes


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


@pytest.mark.parametrize("rom", sorted(EXPECTED_OMITTED))
def test_editor_requires_exactly_one_identical_target_record(rom, source):
    rows, data = source
    _, dropped = dtc_projection.project(rom, source_rows=rows, source=data)
    assert sorted(record.code for record in dropped) == EXPECTED_OMITTED[rom]


def test_1ek7a_distinguishes_unpublished_descriptors_from_absent_codes(source):
    rows, data = source
    projected, dropped = dtc_projection.project("1EK7A", source_rows=rows, source=data)
    absent = sorted(record.code for record in dropped if not record.target_indices)
    assert absent == EXHAUST_VTC_CODES + ["P1422"]
    unresolved = [record for record in dropped if record.target_indices]
    assert len(unresolved) == 13
    assert all(record.exact_matches == 0 for record in unresolved)
    assert next(record for record in unresolved if record.code == "P0443").target_indices == (
        24, 48,
    )
    published_codes = {row["dtc"] for row in projected}
    assert {record.code for record in unresolved} & published_codes == {"P0138", "P0158"}
