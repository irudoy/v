import csv
import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM_PATH = ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin"
FINDINGS_PATH = ROOT / "defs/JK08A.findings.csv"
MAPS_PATH = ROOT / "defs/JK08A.maps.csv"

ZERO_SURFACES = {
    "0001050e": 16 * 16,
    "0001070e": 16 * 16,
    "00017cc8": 16 * 16,
    "00017ec8": 16 * 16,
    "000154c0": 16,
    "000154e0": 16,
}
CENTERED_SURFACE = "00016948"
EXPECTED_ROLES = {
    "0001050e": "dead",
    "0001070e": "dead",
    "00017cc8": "dead",
    "00017ec8": "dead",
    "000154c0": "table",
    "000154e0": "table",
    CENTERED_SURFACE: "dead",
}


def _rows_by_addr(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key].lower(): row for row in csv.DictReader(source)}


def _rom_u16_values(rom: bytes, address: str, count: int) -> tuple[int, ...]:
    offset = int(address, 16)
    return struct.unpack_from(f">{count}H", rom, offset)


def _normalize_endpoint(lower: int, upper: int, signed_input: int) -> int:
    base = max(0, 32768 + signed_input - lower)
    span = max(0, upper - lower)
    if span == 0:
        return 800
    return min(800, base * 800 // span)


def test_remaining_constant_maps_have_code_semantics() -> None:
    findings = _rows_by_addr(FINDINGS_PATH, "addr")

    for address, expected_role in EXPECTED_ROLES.items():
        row = findings[address]
        assert row["confidence"] == "code"
        assert row["role"] == expected_role
        assert row["semantics"]
        assert row["note"]

    for address in ("0001050e", "0001070e", "00017cc8", "00017ec8"):
        assert "rom_const:000089fb=0x20" in findings[address]["evidence"]
        assert "Result disposition: dead_control_flow" in findings[address]["note"]

    assert "rom_const:000083c1=0x2c" in findings[CENTERED_SURFACE]["evidence"]
    assert "Result disposition: dead_control_flow" in findings[CENTERED_SURFACE]["note"]


def test_exact_rom_constant_map_values_and_selectors() -> None:
    rom = ROM_PATH.read_bytes()

    for address, count in ZERO_SURFACES.items():
        assert set(_rom_u16_values(rom, address, count)) == {0}

    assert set(_rom_u16_values(rom, CENTERED_SURFACE, 16 * 16)) == {0x8000}
    assert rom[0x89FB] == 0x20
    assert rom[0x83C1] == 0x2C
    assert rom[0x89FB] & 0x08 == 0
    assert rom[0x83C1] & 0x02 == 0


def test_stock_constant_arithmetic_is_invariant() -> None:
    for weight in (0, 1, 0x7FFF, 0x8000, 0xFFFF):
        assert (0 * (65536 - weight) + 0 * weight) // 65536 == 0

    for signed_input in (-32768, -1, 0, 1, 32767):
        assert _normalize_endpoint(0, 0, signed_input) == 800

    assert 0x8000 - 32768 == 0


def test_generated_catalog_has_no_empty_map_semantics() -> None:
    maps = _rows_by_addr(MAPS_PATH, "table")
    empty = sorted(address for address, row in maps.items() if not row["semantics"])
    assert empty == []

    for address, expected_role in EXPECTED_ROLES.items():
        assert maps[address]["confidence"] == "code"
        assert maps[address]["role"] == expected_role
