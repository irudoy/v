import csv
from pathlib import Path
import re

from patches import can_telemetry_profile


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "patches" / "1nd-runtime-correspondence.csv"
HEADER = (
    "domain",
    "key",
    "source",
    "target",
    "stock",
    "variant",
    "status",
    "evidence",
)
STATUSES = {"mapped", "target-specific", "unsupported"}
HEX_ADDRESS = re.compile(r"^[0-9a-f]{8}$")


def _rows():
    with EVIDENCE.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        assert tuple(reader.fieldnames or ()) == HEADER
        return list(reader)


def _canonical_telemetry_keys():
    manifest = can_telemetry_profile.load_manifest()
    fields = list(manifest.fields)
    fields.extend(field for context in manifest.contexts for field in context.fields)
    return {field.name for field in fields if field.kind == "ecu_ram"}


def test_1nd_runtime_correspondence_is_strict_and_unique():
    rows = _rows()
    assert rows
    assert all(row["domain"] and row["key"] and row["evidence"] for row in rows)
    assert {row["status"] for row in rows} <= STATUSES
    assert len({(row["domain"], row["key"], row["variant"]) for row in rows}) == len(rows)
    for row in rows:
        for field in ("source", "target", "stock"):
            assert not row[field] or HEX_ADDRESS.fullmatch(row[field])
        if row["status"] == "unsupported":
            assert not row["target"]


def test_1nd_telemetry_correspondence_covers_the_complete_schema():
    rows = [row for row in _rows() if row["domain"] == "telemetry"]
    assert {row["key"] for row in rows} == _canonical_telemetry_keys()
    unsupported = [row["key"] for row in rows if row["status"] == "unsupported"]
    assert unsupported == ["knock_timing_state_raw"]
    for row in rows:
        if row["status"] != "unsupported":
            assert 0xFFFE8000 <= int(row["target"], 16) < 0xFFFF0000


def test_1nd_runtime_capabilities_are_explicit():
    rows = {
        row["key"]: row for row in _rows() if row["domain"] == "capability"
    }
    assert set(rows) == {"map_switching", "rolling_launch", "can_telemetry"}
    assert rows["map_switching"]["status"] == "target-specific"
    assert rows["rolling_launch"]["status"] == "unsupported"
    assert rows["can_telemetry"]["status"] == "target-specific"
