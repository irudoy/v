import csv
import struct
import tomllib
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
ROM_PATH = ROOT / "rom-images/23710-JK08A/1JK08A-20260726-stock.bin"
FINDINGS_PATH = ROOT / "defs/JK08A.findings.csv"
MAPS_PATH = ROOT / "defs/JK08A.maps.csv"
AXES_PATH = ROOT / "defs/JK08A.axes.csv"
OVERRIDES_PATH = ROOT / "defs/JK08A.overrides.toml"
BINDINGS_PATH = ROOT / "defs/JK08A.diagnostic-bindings.csv"

RPM_FACTOR = 0x1236A
RPM_AXIS = 0x1238A
FACTOR_A = 0x12AC2
FACTOR_B = 0x12868


def _rows_by_addr(path: Path, key: str) -> dict[str, dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as source:
        return {row[key].lower(): row for row in csv.DictReader(source)}


def _composite_threshold(
    rpm_factor: int,
    factor_a: int,
    factor_b: int,
    common: int,
    weight_0: int,
    weight_1: int,
    bank: int,
) -> int:
    combined = min(255, rpm_factor * factor_a * factor_b // 16384)
    scaled = common * combined // 256
    if weight_0 == 0 and weight_1 == 0:
        ratio = 255
    else:
        selected = (weight_0, weight_1)[bank]
        ratio = min(255, selected * scaled // (weight_0 + weight_1))
    return 128 * ratio // 256


def test_exact_rom_binds_shared_factor_to_both_maf_monitors() -> None:
    rom = ROM_PATH.read_bytes()

    assert tuple(rom[RPM_FACTOR : RPM_FACTOR + 16]) == (
        74,
        99,
        99,
        97,
        115,
        116,
        110,
        111,
        110,
        113,
        117,
        123,
        125,
        123,
        125,
        124,
    )
    assert tuple(rom[RPM_AXIS : RPM_AXIS + 16]) == tuple(range(8, 129, 8))

    assert struct.unpack_from(">I", rom, 0x818C0)[0] == RPM_FACTOR
    assert struct.unpack_from(">I", rom, 0x818C4)[0] == RPM_AXIS
    assert struct.unpack_from(">I", rom, 0x82088)[0] == RPM_FACTOR
    assert struct.unpack_from(">I", rom, 0x8208C)[0] == RPM_AXIS
    assert struct.unpack_from(">I", rom, 0x818CC)[0] == FACTOR_A
    assert struct.unpack_from(">I", rom, 0x82094)[0] == FACTOR_A
    assert struct.unpack_from(">I", rom, 0x818DC)[0] == FACTOR_B
    assert struct.unpack_from(">I", rom, 0x820A0)[0] == FACTOR_B

    assert rom[0x82BA] == 128
    assert rom[0x8D92] == 0x7A
    assert rom[0x8D92] & 0x20


def test_exact_aggregator_dispatches_p0101_and_p010b() -> None:
    rom = ROM_PATH.read_bytes()

    assert struct.unpack_from(">I", rom, 0x8100C)[0] == 0x0007D8B8
    assert rom[0x80FB6 : 0x80FBE] == bytes.fromhex("d215e3ba420b643c")
    assert rom[0x80FDC : 0x80FE2] == bytes.fromhex("d20b420be407")

    assert struct.unpack_from(">H", rom, 0x19C18 + 6)[0] == 0x0101
    assert struct.unpack_from(">H", rom, 0x193B4 + 6)[0] == 0x010B


def test_composite_threshold_model_preserves_bank_weighting() -> None:
    assert _composite_threshold(255, 255, 255, 255, 0, 0, 0) == 127
    assert _composite_threshold(255, 255, 255, 255, 0, 0, 1) == 127

    first = _composite_threshold(100, 150, 80, 200, 300, 100, 0)
    second = _composite_threshold(100, 150, 80, 200, 300, 100, 1)
    assert first == 21
    assert second == 7

    low = _composite_threshold(74, 154, 56, 255, 300, 100, 0)
    high = _composite_threshold(125, 154, 56, 255, 300, 100, 0)
    assert low < high


def test_catalog_and_presentation_reject_fuel_enrichment_semantics() -> None:
    findings = _rows_by_addr(FINDINGS_PATH, "addr")
    maps = _rows_by_addr(MAPS_PATH, "table")
    axes = _rows_by_addr(AXES_PATH, "addr")
    overrides = tomllib.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))

    for rows in (findings, maps):
        row = rows["0001236a"]
        assert row["confidence"] == "code"
        assert row["role"] == "table"
        assert "P0101/P010B" in row["semantics"]
        assert "fuel enrichment" not in row["semantics"].lower()

    for address in ("00012868", "00012ac2"):
        assert "P0101/P010B" in findings[address]["semantics"]

    axis = axes["0001238a"]
    assert axis["scale_conf"] == "code"
    assert axis["scale_expr"] == "x*50"

    table = overrides["table"]["0001236a"]
    assert table["emit"] is False
    assert table["static_axis_name"] == "Engine Speed [RPM]"
    assert table["static_axis"] == list(range(400, 6401, 400))


def test_diagnostic_bindings_cover_both_banks_and_all_factors() -> None:
    with BINDINGS_PATH.open(newline="", encoding="utf-8") as source:
        rows = {row["id"]: row for row in csv.DictReader(source)}

    expected = {
        "maf-range-monitor-bank1-p0101": ("0008152a", "P0101"),
        "maf-range-monitor-bank2-p010b": ("00081d74", "P010B"),
        "maf-range-rpm-factor-p0101": ("0001236a", "P0101"),
        "maf-range-rpm-factor-p010b": ("0001236a", "P010B"),
        "maf-range-composite-factor-a-p0101": ("00012ac2", "P0101"),
        "maf-range-composite-factor-a-p010b": ("00012ac2", "P010B"),
        "maf-range-composite-factor-b-p0101": ("00012868", "P0101"),
        "maf-range-composite-factor-b-p010b": ("00012868", "P010B"),
    }
    for binding_id, (address, dtc) in expected.items():
        row = rows[binding_id]
        assert row["firmware_addr"] == address
        assert row["diagnostic_key"] == dtc
        assert row["confidence"] == "code"
        assert row["applicability"] == "exact_rom"
