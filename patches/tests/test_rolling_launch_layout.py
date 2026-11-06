from dataclasses import replace
import hashlib
from pathlib import Path
import tomllib

import pytest

from patches import extract_calibration
from patches import rolling_launch as rl
from patches import rolling_launch_assembly
from patches import rolling_launch_compose
from patches import rolling_launch_layout as storage
from patches import runtime_endpoints


@pytest.fixture
def layout():
    return storage.load_layout()


def pending(layout):
    return replace(layout, payloads_ready=False, expected_composition_sha256="")


def test_schema6_regions_state_and_payloads_are_declared(layout):
    assert (layout.configuration.start, layout.configuration.size) == (0xD6320, 102)
    assert (layout.efficiency.start, layout.efficiency.size) == (0xD6390, 82)
    assert [(x.start, x.end) for x in layout.ram.active_spans] == [
        (0xFFFF5D40, 0xFFFF5D6C), (0xFFFF6100, 0xFFFF6120)]
    assert layout.payloads_ready and layout.hold_actuator
    assert len(layout.expected_composition_sha256) == 64
    assert layout.default_configuration == rl.Calibration().to_bytes()
    assert layout.code_region_by_key["startup_wrapper"].entry == 0xD38A0
    assert layout.code_region_by_key["state_check"].entry == 0xD7000
    assert (0xD7000, 0xD7200) in [(x.start, x.end) for x in layout.claimed_rom_ranges]
    assert {
        region for unit in layout.assembly_units for region in unit.code_regions
    } == set(layout.code_region_by_key)
    with pytest.raises(ValueError, match="not assembled"):
        storage.validate_base_composition(pending(layout), bytes(0x100000))


def test_old_fuel_path_is_absent_but_stock_restorations_are_explicit(layout):
    assert "fuel_cut_coordinator" not in layout.hook_by_key
    assert not hasattr(layout.scheduler, "fuel_cut_index")
    assert not ({"fuel_cut_wrapper", "rpm_ceiling", "trim"} & set(layout.assembly_unit_by_key))
    assert 0x121E not in layout.diagnostic_by_did and 0x1231 not in layout.diagnostic_by_did
    assert {(item.address, item.value) for item in layout.restored_words} == {
        (0x219DC, 0x4ED88), (0x22914, 0xFFFFFFFF), (0x22960, 0xFFFFFFFF),
        (0x202E4, 0x2AB24)}
    assert "spark_handler" not in layout.hook_by_key
    assert layout.hook_by_key["dwell_arming_divider"].address == 0x296C0
    assert layout.retired_configuration_for(5).start == 0xD6220
    assert layout.retired_configuration_for(4).start == 0xD6040


def test_speed_inputs_require_the_raw_bytes_and_both_ready_bits(layout):
    assert layout.speed_inputs == storage.SpeedInputs(
        0xFFFF113C, 0xFFFF3B38, 0xFFFF4195, 1,
        0xFFFF4185, 0x80, 0xFFFF3B3D, 0xFFFF3B3E)
    assert layout.speed_inputs.raw_high_address % 2 == 1
    assert layout.scheduler.tick_microseconds == 10240


@pytest.mark.parametrize("change,match", [
    ({"expected_composition_sha256": ""}, "SHA-256|hexadecimal|digits"),
    ({"payloads_ready": False}, "unassembled"),
    ({"payloads_ready": False, "expected_composition_sha256": "", "hold_actuator": True},
     "unassembled"),
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
    units = tuple(unit for unit in layout.assembly_units if unit.key != "state_check")
    with pytest.raises(ValueError, match="assembly owner"):
        storage.validate_structure(replace(layout, assembly_units=units))


def test_pending_payloads_do_not_read_a_manifest(layout, tmp_path):
    assert rolling_launch_assembly.load_payloads(pending(layout), tmp_path / "absent.toml") == {}
    assert set(rolling_launch_assembly.load_payloads(layout)) == set(layout.assembly_unit_by_key)


def test_pending_composition_refuses_before_using_payloads(layout):
    with pytest.raises(ValueError, match="schema 6 executable payloads are not assembled and qualified"):
        rolling_launch_compose.compose(layout=pending(layout), base=bytes(0x100000))


@pytest.mark.parametrize("damage,message", (
    (None, None),
    ("missing", "payload set differs"),
    ("extra", "payload set differs"),
    ("hash", "blob SHA-256"),
    ("size", "blob has"),
))
def test_ready_payloads_require_the_exact_unit_set_and_bytes(layout, tmp_path, damage, message):
    unit = layout.assembly_units[0]
    blob = bytes(unit.span.size)
    unit = replace(unit, expected_sha256=hashlib.sha256(blob).hexdigest())
    ready = replace(layout, payloads_ready=True, assembly_units=(unit,))
    units = {unit.key: blob.hex()}
    if damage == "missing":
        units.clear()
    elif damage == "extra":
        units["unexpected"] = blob.hex()
    elif damage == "hash":
        units[unit.key] = (b"\x01" + blob[1:]).hex()
    elif damage == "size":
        units[unit.key] = blob[1:].hex()
    path = tmp_path / "payloads.toml"
    path.write_text("schema_version = 1\n[units]\n" + "".join(
        f'{key} = "{value}"\n' for key, value in units.items()
    ))
    if message is None:
        assert rolling_launch_assembly.load_payloads(ready, path) == {unit.key: blob}
    else:
        with pytest.raises(ValueError, match=message):
            rolling_launch_assembly.load_payloads(ready, path)


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
