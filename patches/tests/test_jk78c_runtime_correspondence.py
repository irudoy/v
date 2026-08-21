import csv
from pathlib import Path
import re

from patches import can_telemetry_compose
from patches import can_telemetry_profile
from patches import map_switching_compose
from patches import runtime_targets


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "patches" / "jk78c-runtime-correspondence.csv"
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


def test_jk78c_runtime_correspondence_is_strict_and_unique():
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


def test_jk78c_telemetry_correspondence_covers_the_complete_schema():
    rows = [row for row in _rows() if row["domain"] == "telemetry"]
    assert {row["key"] for row in rows} == _canonical_telemetry_keys()
    unsupported = [row["key"] for row in rows if row["status"] == "unsupported"]
    assert unsupported == ["knock_timing_state_raw"]
    for row in rows:
        if row["status"] != "unsupported":
            assert 0xFFFF0000 <= int(row["target"], 16) < 0xFFFFC000


def test_jk78c_runtime_capabilities_are_explicit():
    rows = {
        row["key"]: row for row in _rows() if row["domain"] == "capability"
    }
    assert set(rows) == {"map_switching", "rolling_launch", "can_telemetry"}
    assert rows["map_switching"]["status"] == "target-specific"
    assert rows["rolling_launch"]["status"] == "unsupported"
    assert rows["can_telemetry"]["status"] == "target-specific"


def test_jk78c_erased_stock_references_remain_outside_runtime_writes():
    target = runtime_targets.project_relocated_target("JK78C")
    writes = map_switching_compose.composition_write_ranges(target.map_layout)
    writes += can_telemetry_compose.composition_write_ranges(
        target.telemetry_layout
    )
    stock_references = (0x0001E30C, 0x0001FE00, 0x0001FFFE, 0x0001FFFF)
    assert all(
        not any(span.start <= address < span.end for span in writes)
        for address in stock_references
    )
