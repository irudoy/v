import csv
from pathlib import Path
import re

from patches import can_telemetry_profile
from patches import rom_address_profiles
from tools.mapkit import vq37_native_fuel_cut


ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "patches" / "1me3b-runtime-correspondence.csv"
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


def test_1me3b_runtime_correspondence_is_strict_and_unique():
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


def test_1me3b_telemetry_correspondence_covers_the_complete_schema():
    rows = [row for row in _rows() if row["domain"] == "telemetry"]
    assert {row["key"] for row in rows} == _canonical_telemetry_keys()
    unsupported = {row["key"] for row in rows if row["status"] == "unsupported"}
    assert unsupported == {
        "ltft_publication_neutral_control_raw",
        "torque_transition_state_raw",
        "knock_state_snapshot_raw",
        "knock_branch_state_raw",
        "knock_timing_state_raw",
        "transmission_reduction_state_raw",
    }
    for row in rows:
        if row["status"] != "unsupported":
            assert 0xFFFE8000 <= int(row["target"], 16) < 0xFFFF0000


def test_1me3b_runtime_capabilities_are_explicit():
    rows = {
        row["key"]: row for row in _rows() if row["domain"] == "capability"
    }
    assert set(rows) == {"map_switching", "rolling_launch", "can_telemetry"}
    assert rows["map_switching"]["status"] == "target-specific"
    assert rows["rolling_launch"]["status"] == "target-specific"
    assert rows["can_telemetry"]["status"] == "target-specific"


def test_1me3b_native_fuel_cut_evidence_matches_the_exact_registry():
    rows = {(row["domain"], row["key"]): row for row in _rows()}
    native = vq37_native_fuel_cut.load_registry()["1ME3B"]

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


def test_1me3b_correspondence_targets_equal_the_address_profile():
    rows = _rows()
    profile = rom_address_profiles.profile_for_rom("1ME3B")

    telemetry = {
        row["key"]: row for row in rows if row["domain"] == "telemetry"
    }
    assert {
        key: int(row["target"], 16)
        for key, row in telemetry.items()
        if row["status"] != "unsupported"
    } == dict(profile.telemetry_source_by_name)
    assert tuple(sorted(
        key
        for key, row in telemetry.items()
        if row["status"] == "unsupported"
    )) == profile.telemetry_unavailable

    for domain, hooks in (
        ("rolling_hook", profile.rolling_hook_by_key),
        ("can_hook", profile.can_hook_by_key),
    ):
        ledger = {
            row["key"]: (int(row["target"], 16), int(row["stock"], 16))
            for row in rows
            if row["domain"] == domain
        }
        assert ledger == {
            key: (hook.address, hook.stock) for key, hook in hooks.items()
        }

    map_hooks = {
        row["key"]: (int(row["target"], 16), int(row["stock"], 16))
        for row in rows
        if row["domain"] == "map_hook"
    }
    assert map_hooks == {
        key: (hook.address, hook.stock)
        for key, hook in profile.map_hook_by_key.items()
    }

    for domain, symbols in (
        ("map_symbol", profile.map_symbol_by_key),
        ("rolling_symbol", profile.rolling_symbol_by_key),
    ):
        ledger = {
            row["key"]: int(row["target"], 16)
            for row in rows
            if row["domain"] == domain
        }
        for key, address in symbols.items():
            assert ledger[key] == address

    routine = profile.ignition_unreferenced_routine
    symbol_rows = {
        row["key"]: row for row in rows if row["domain"] == "map_symbol"
    }
    assert int(
        symbol_rows["ignition_unreferenced_routine"]["target"], 16
    ) == routine.start
