import csv
import struct
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM_PATH = ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin"
FINDINGS_PATH = ROOT / "defs/registries/JK08A.findings.csv"
MAPS_PATH = ROOT / "defs/registries/JK08A.maps.csv"
OVERRIDES_PATH = ROOT / "defs/JK08A.overrides.toml"

TABLE_ADDRESS = 0x1202E
TABLE_POINTER_LITERAL = 0x3E3E4
CLASS_BREAKPOINTS = (4, 8, 12)
RESTORE_FLOORS_RPM25 = (36, 48, 54, 62)


def _rows_by_addr(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key].lower(): row for row in csv.DictReader(source)}


def _filter_step(current_rpm125: int, old_rpm125: int, previous_q8: int) -> int:
    drop = max(old_rpm125 - current_rpm125, 0)
    return min(0xFFFF, 64 * drop + 192 * previous_q8 // 256)


def _published_drop(retained: int, upstream_mode: bool, ph1: bool, q8: int) -> int:
    if not upstream_mode:
        return 0
    if retained != 0 and not ph1:
        return 0
    return q8 >> 8


def _drop_class(value: int) -> int:
    for index, threshold in enumerate(CLASS_BREAKPOINTS):
        if value < threshold:
            return index
    return 3


def test_exact_rom_binds_table_to_rpm_drop_path() -> None:
    rom = ROM_PATH.read_bytes()

    assert rom[TABLE_ADDRESS : TABLE_ADDRESS + 4] == bytes([200] * 4)
    assert struct.unpack_from(">I", rom, TABLE_POINTER_LITERAL)[0] == TABLE_ADDRESS
    assert struct.unpack_from(">I", rom, 0x3E150)[0] == 0xA2C2
    assert struct.unpack_from(">I", rom, 0x3E154)[0] == 0x21BBC
    assert rom[0x84A4] == 64
    assert tuple(rom[0x11CB5 : 0x11CB9]) == (4, 8, 12, 32)
    assert tuple(rom[0x1299C : 0x129A0]) == RESTORE_FLOORS_RPM25

    # PHDR bit 1 (PH1DR, tst #2) is tested and copied directly to ffff2451.bit7.
    assert rom[0x3870E : 0x3871C] == bytes.fromhex(
        "8522600dc80260d38d01c97fcb80"
    )


def test_filter_and_boolean_gate_model() -> None:
    assert _filter_step(100, 100, 0) == 0
    assert _filter_step(80, 100, 0) == 20 * 64
    assert _filter_step(80, 100, 256) == 20 * 64 + 192
    assert _filter_step(0, 0xFFFF, 0xFFFF) == 0xFFFF

    q8 = 9 << 8
    assert _published_drop(200, False, False, q8) == 0
    assert _published_drop(200, True, False, q8) == 0
    assert _published_drop(1, True, False, q8) == 0
    assert _published_drop(200, True, True, q8) == 9
    assert _published_drop(0, True, False, q8) == 9


def test_rpm_nodes_and_downstream_classes_are_exact() -> None:
    assert tuple((q + 96) * 12.5 for q in (0, 64, 128, 192)) == (
        1200.0,
        2000.0,
        2800.0,
        3600.0,
    )

    expected = {
        0: 0,
        3: 0,
        4: 1,
        7: 1,
        8: 2,
        11: 2,
        12: 3,
        31: 3,
        32: 3,
        255: 3,
    }
    assert {value: _drop_class(value) for value in expected} == expected
    assert tuple(value * 25 for value in RESTORE_FLOORS_RPM25) == (
        900,
        1200,
        1350,
        1550,
    )


def test_catalog_and_presentation_use_code_proven_semantics() -> None:
    findings = _rows_by_addr(FINDINGS_PATH, "addr")
    maps = _rows_by_addr(MAPS_PATH, "table")
    overrides = tomllib.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))

    for rows in (findings, maps):
        row = rows["0001202e"]
        assert row["confidence"] == "code"
        assert row["role"] == "table"
        assert "RPM-drop" in row["semantics"]
        assert "Initial Retard Quantity" not in row["semantics"]

    table = overrides["table"]["0001202e"]
    assert table["emit"] is False
    assert table["static_axis_name"] == "Engine Speed [RPM]"
    assert table["static_axis"] == [1200, 2000, 2800, 3600]
