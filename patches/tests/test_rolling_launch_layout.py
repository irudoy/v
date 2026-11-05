from dataclasses import replace
from pathlib import Path
import tomllib

import pytest

from patches import extract_calibration
from patches import rolling_launch as rl
from patches import rolling_launch_layout as storage
from patches import runtime_endpoints


@pytest.fixture
def layout():
    return storage.load_layout()


def test_schema6_regions_and_state_are_declared_without_executable_qualification(layout):
    assert (layout.configuration.start, layout.configuration.size) == (0xD6320, 102)
    assert (layout.efficiency.start, layout.efficiency.size) == (0xD6390, 82)
    assert [(x.start, x.end) for x in layout.ram.active_spans] == [
        (0xFFFF5D40, 0xFFFF5D6C), (0xFFFF6100, 0xFFFF6120)]
    assert not layout.payloads_ready and not layout.hold_actuator
    assert layout.expected_composition_sha256 == ""
    assert layout.default_configuration == rl.Calibration().to_bytes()
    assert layout.code_region_by_key["startup_wrapper"].entry == 0xD38A0
    with pytest.raises(ValueError, match="not assembled"):
        storage.validate_base_composition(layout, bytes(0x100000))


def test_old_fuel_path_is_absent_but_stock_restorations_are_explicit(layout):
    assert "fuel_cut_coordinator" not in layout.hook_by_key
    assert not hasattr(layout.scheduler, "fuel_cut_index")
    assert not ({"fuel_cut_wrapper", "rpm_ceiling", "trim"} & set(layout.assembly_unit_by_key))
    assert 0x121E not in layout.diagnostic_by_did and 0x1231 not in layout.diagnostic_by_did
    assert {(item.address, item.value) for item in layout.restored_words} == {
        (0x219DC, 0x4ED88), (0x22914, 0xFFFFFFFF), (0x22960, 0xFFFFFFFF)}
    assert layout.retired_configuration_for(5).start == 0xD6220
    assert layout.retired_configuration_for(4).start == 0xD6040


def test_speed_inputs_require_the_raw_bytes_and_both_ready_bits(layout):
    assert layout.speed_inputs == storage.SpeedInputs(
        0xFFFF113C, 0xFFFF3B38, 0xFFFF4195, 1,
        0xFFFF4185, 0x80, 0xFFFF3B3D, 0xFFFF3B3E)
    assert layout.speed_inputs.raw_high_address % 2 == 1
    assert layout.scheduler.tick_microseconds == 10240


@pytest.mark.parametrize("change,match", [
    ({"payloads_ready": True}, "SHA-256|hexadecimal|digits"),
    ({"hold_actuator": True}, "unassembled"),
    ({"configuration": storage.common.AddressRange(0xD6320, 0xD637D, "bad")}, "size"),
    ({"efficiency": storage.common.AddressRange(0xD6390, 0xD63E0, "bad")}, "size"),
    ({"restored_words": ()}, "restored"),
])
def test_layout_cannot_hide_partial_or_conflicting_contracts(layout, change, match):
    with pytest.raises(ValueError, match=match):
        storage.validate_structure(replace(layout, **change))


def test_extension_cannot_overlap_another_active_or_future_owner(layout):
    overlapping = replace(layout.ram, extension=storage.common.AddressRange(
        0xFFFF5D40, 0xFFFF5D60, "overlap"))
    with pytest.raises(ValueError, match="overlaps"):
        storage.validate_structure(replace(layout, ram=overlapping))
    wrong_owner = replace(layout.ram, extension=storage.common.AddressRange(
        0xFFFF6000, 0xFFFF6020, "map_future"))
    with pytest.raises(ValueError, match="active RAM differs"):
        storage.validate_reservations(replace(layout, ram=wrong_owner))


def test_ready_flag_cannot_qualify_unowned_executable_budgets(layout):
    with pytest.raises(ValueError, match="assembly owner"):
        storage.validate_structure(replace(layout, payloads_ready=True,
                                           expected_composition_sha256="0"*64))


def test_reservation_checks_reject_real_future_overlap(layout, tmp_path):
    data = storage.DEFAULT_RESERVATIONS.read_text()
    # A future allocation cannot include the active extension.
    path = tmp_path / "reservations.toml"
    path.write_text(data.replace("start = 0xFFFF6120", "start = 0xFFFF6110"))
    with pytest.raises(ValueError, match="overlap"):
        storage.validate_reservations(layout, path)


@pytest.mark.parametrize("key,schema", [("schema-4-uniform-gain", 4), ("schema-5-fixed-trim", 5)])
def test_flashed_settings_remain_frozen_unexpressed_fields(layout, key, schema):
    fixture = Path(__file__).with_name("data") / f"rolling-launch-schema-{schema}.toml"
    with fixture.open("rb") as source:
        raw = tomllib.load(source)
    record = bytes.fromhex(raw["configuration"])
    endpoint = runtime_endpoints.historical_endpoint(key)
    data = bytearray(endpoint.record.end)
    data[endpoint.record.start:endpoint.record.end] = record
    actual, settings, unexpressed = extract_calibration._rolling_settings(data, layout, key)
    assert actual == record and settings is None
    ((component, name, version, values),) = unexpressed
    assert (component, name, version) == ("rolling_launch", key, schema)
    assert values["rpm_ceiling_offset_native"] == 80
    assert "launch_rpm_native" not in values
    assert not hasattr(rl.Calibration, "from_legacy_bytes")
