import csv
from pathlib import Path
import re

import pytest

from patches import build_rom
from patches import can_telemetry_compose
from patches import can_telemetry_profile
from patches import extract_calibration
from patches import map_switching_compose
from patches import rolling_launch_compose
from patches import rom_checksums
from patches import runtime_targets
from tools.mapkit import vq37_native_fuel_cut


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
    unsupported = {row["key"] for row in rows if row["status"] == "unsupported"}
    assert unsupported == {
        "ltft_publication_neutral_control_raw",
        "knock_branch_state_raw",
        "transmission_reduction_state_raw",
    }
    for row in rows:
        if row["status"] != "unsupported":
            assert 0xFFFF0000 <= int(row["target"], 16) < 0xFFFFC000


def test_jk78c_runtime_capabilities_are_explicit():
    rows = {
        row["key"]: row for row in _rows() if row["domain"] == "capability"
    }
    assert set(rows) == {"map_switching", "rolling_launch", "can_telemetry"}
    assert rows["map_switching"]["status"] == "target-specific"
    assert rows["rolling_launch"]["status"] == "target-specific"
    assert rows["can_telemetry"]["status"] == "target-specific"


def test_jk78c_native_fuel_cut_evidence_matches_the_exact_registry():
    rows = {(row["domain"], row["key"]): row for row in _rows()}
    native = vq37_native_fuel_cut.load_registry()["JK78C"]

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
        "rev_fuel_cut_release_cap_base",
        "rev_fuel_cut_curves_base",
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


def test_jk78c_erased_stock_references_remain_outside_runtime_writes():
    target = runtime_targets.project_relocated_target("JK78C")
    writes = map_switching_compose.composition_write_ranges(target.map_layout)
    writes += rolling_launch_compose.composition_write_ranges(target.rolling_layout)
    writes += can_telemetry_compose.composition_write_ranges(
        target.telemetry_layout
    )
    # 0x1E30C feeds CMP/HI at 0xDA35C and 0xDA468, not a ROM dereference.
    # Disjoint audit values remain candidates without assuming pointer semantics.
    protected_candidates = (0x0001FE00, 0x0001FFFE, 0x0001FFFF)
    assert all(
        not any(span.start <= address < span.end for span in writes)
        for address in protected_candidates
    )


@pytest.fixture(scope="module")
def jk78c_inputs():
    target = runtime_targets.project_relocated_target("JK78C")
    stock = target.stock_image.data
    result = build_rom.build_image(stock, rom="JK78C")
    return target, {"base": stock, "runtime": result.data}, result.data


def test_jk78c_builder_accepts_only_the_stock_image(jk78c_inputs):
    _target, images, expected = jk78c_inputs
    assert build_rom.build_image(images["base"], rom="JK78C").data == expected
    with pytest.raises(build_rom.BuildError, match="not the registered JK78C stock"):
        build_rom.build_image(images["runtime"], rom="JK78C")


@pytest.mark.parametrize("state", ("base", "runtime"))
def test_jk78c_erased_envelope_extracts_stock_and_complete_runtime(jk78c_inputs, state):
    _target, images, _expected = jk78c_inputs
    extraction = extract_calibration.extract(images[state], rom="JK78C")
    assert extraction.calibration.elements == ()


@pytest.mark.parametrize("state", ("base", "runtime"))
@pytest.mark.parametrize("address", (0x0001CAB0, 0x0001FFFF))
def test_jk78c_rejects_foreign_bytes_outside_runtime_writes(jk78c_inputs, state, address):
    target, images, _expected = jk78c_inputs
    writes = map_switching_compose.composition_write_ranges(target.map_layout)
    writes += rolling_launch_compose.composition_write_ranges(target.rolling_layout)
    writes += can_telemetry_compose.composition_write_ranges(target.telemetry_layout)
    assert target.map_layout.free_rom.start <= address < target.map_layout.free_rom.end
    assert not any(span.start <= address < span.end for span in writes)
    source = bytearray(images[state])
    assert source[address] == 0xFF
    source[address] = 0x00
    source = rom_checksums.recalculate(source, target.checksum_layout)
    with pytest.raises(
        extract_calibration.ExtractionError,
        match=f"change at {address:#x} is outside the calibration ranges of JK78C",
    ):
        extract_calibration.extract(bytes(source), rom="JK78C")
