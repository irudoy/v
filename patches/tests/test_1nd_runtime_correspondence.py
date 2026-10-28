import csv
from pathlib import Path
import re

from patches import can_telemetry_profile
from tools.mapkit import vq37_native_fuel_cut


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
    unsupported = {row["key"] for row in rows if row["status"] == "unsupported"}
    assert unsupported == {
        "request_flow_raw",
        "normalized_load_raw",
        "fuel_learning_permit_b_raw",
        "fuel_learning_permit_a_raw",
        "ltft_publication_neutral_control_raw",
        "torque_transition_state_raw",
        "knock_state_snapshot_raw",
        "knock_branch_state_raw",
        "transmission_reduction_state_raw",
        "ltft_learned_b2_raw",
        "ltft_adjustment_b2_raw",
        "alpha_n_flow_raw",
    }
    for row in rows:
        if row["status"] != "unsupported":
            assert 0xFFFE8000 <= int(row["target"], 16) < 0xFFFF0000


def test_1nd_runtime_capabilities_are_explicit():
    rows = {
        row["key"]: row for row in _rows() if row["domain"] == "capability"
    }
    assert set(rows) == {"map_switching", "rolling_launch", "can_telemetry"}
    assert rows["map_switching"]["status"] == "target-specific"
    assert rows["rolling_launch"]["status"] == "target-specific"
    assert rows["can_telemetry"]["status"] == "target-specific"


def test_1nd_native_fuel_cut_evidence_matches_the_exact_registry():
    rows = {(row["domain"], row["key"]): row for row in _rows()}
    native = vq37_native_fuel_cut.load_registry()["1ND0A"]

    assert int(rows[("map_native", "rev_limit_fuel_cut_caps")]["target"], 16) == (
        native.caps_address
    )
    assert int(rows[("map_native", "rev_limit_fuel_cut_curves")]["target"], 16) == (
        native.curves_address
    )
    assert int(rows[("map_symbol", "rev_fuel_cut_state_machine")]["target"], 16) == (
        native.function_address
    )
    assert int(rows[("map_symbol", "rev_fuel_cut_selector")]["target"], 16) == (
        native.selector_address
    )
    assert int(rows[("map_symbol", "rev_fuel_cut_state")]["target"], 16) == (
        native.state_address
    )
    delay = rows[("map_symbol", "rev_fuel_cut_delay")]
    assert int(delay["target"], 16) == native.delay_address
    assert int(
        rows[(
            "map_native", "rev_limit_fuel_cut_delay_calibration"
        )]["target"],
        16,
    ) == native.delay_calibration_address
    assert int(
        rows[("rolling_symbol", "fuel_cut_coordinator")]["target"], 16
    ) == native.coordinator_address
    coordinator_hook = rows[("rolling_hook", "fuel_cut_coordinator")]
    assert int(coordinator_hook["target"], 16) == (
        native.coordinator_pointer_site
    )
    assert int(coordinator_hook["stock"], 16) == native.coordinator_address
    hook_keys = (
        "rev_fuel_cut_caps_base",
        "rev_fuel_cut_activation_curve_base",
        "rev_fuel_cut_release_curve_base",
    )
    assert tuple(
        (
            int(rows[("map_hook", key)]["target"], 16),
            int(rows[("map_hook", key)]["stock"], 16),
        )
        for key in hook_keys
    ) == tuple(
        (binding.site, binding.target)
        for binding in native.pointer_bindings
    )
