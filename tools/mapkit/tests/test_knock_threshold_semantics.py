import csv
import struct
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM_PATH = ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin"
FINDINGS_PATH = ROOT / "defs/registries/JK08A.findings.csv"
MAPS_PATH = ROOT / "defs/registries/JK08A.maps.csv"
OVERRIDES_PATH = ROOT / "defs/JK08A.overrides.toml"

UNREFERENCED_BANK = 0x10F8E
ACTIVE_BANK = 0x1108E
ACTIVE_POINTER_LITERAL = 0x4A204
ROW_WORDS = 16
ROW_COUNT = 6


def _rows_by_addr(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key].lower(): row for row in csv.DictReader(source)}


def _bank(rom: bytes, address: int) -> tuple[tuple[int, ...], ...]:
    values = struct.unpack_from(">96H", rom, address)
    return tuple(
        values[row * ROW_WORDS : (row + 1) * ROW_WORDS]
        for row in range(ROW_COUNT)
    )


def _occurrences(data: bytes, needle: bytes) -> list[int]:
    result = []
    offset = 0
    while True:
        offset = data.find(needle, offset)
        if offset < 0:
            return result
        result.append(offset)
        offset += 1


def test_exact_rom_selects_only_active_knock_bank() -> None:
    rom = ROM_PATH.read_bytes()

    assert _occurrences(rom, UNREFERENCED_BANK.to_bytes(4, "big")) == []
    assert _occurrences(rom, ACTIVE_BANK.to_bytes(4, "big")) == [
        ACTIVE_POINTER_LITERAL
    ]
    assert struct.unpack_from(">I", rom, ACTIVE_POINTER_LITERAL)[0] == ACTIVE_BANK

    # mov.l loads 0x4A204 into r4, then the wrapper call occurs at 0x4A02C.
    assert rom[0x4A014:0x4A016] == bytes.fromhex("d47b")
    assert rom[0x4A02C:0x4A030] == bytes.fromhex("420b667d")
    assert rom[0x8B3D] == 0x82
    assert rom[0x8B3D] & 0x08 == 0


def test_stock_disabled_rows_are_explicit() -> None:
    rom = ROM_PATH.read_bytes()

    for address in (UNREFERENCED_BANK, ACTIVE_BANK):
        rows = _bank(rom, address)
        assert set(rows[2]) == {0xFFFF}
        assert set(rows[4]) == {0xFFFF}
        assert any(value != 0xFFFF for value in rows[0])
        assert any(value != 0xFFFF for value in rows[1])
        assert any(value != 0xFFFF for value in rows[3])
        assert any(value != 0xFFFF for value in rows[5])


def test_catalog_and_presentation_keep_unreferenced_bank_inactive() -> None:
    findings = _rows_by_addr(FINDINGS_PATH, "addr")
    maps = _rows_by_addr(MAPS_PATH, "table")
    overrides = tomllib.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))

    for rows in (findings, maps):
        assert rows["00010f8e"]["confidence"] == "code"
        assert rows["00010f8e"]["role"] == "dead"
        assert rows["0001108e"]["confidence"] == "code"
        assert rows["0001108e"]["role"] == "table"

    assert overrides["table"]["00010f8e"]["emit"] is False
    assert overrides["table"]["0001108e"]["emit"] is True
    assert (
        overrides["table"]["0001108e"]["static_axis_y_name"]
        == "Evaluator Channel"
    )
