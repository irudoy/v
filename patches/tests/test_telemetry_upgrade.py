"""Transfer a real previous telemetry endpoint through the production builder."""

from dataclasses import replace
from functools import lru_cache

import pytest

from patches import build_rom, calibration_ranges, can_telemetry, can_telemetry_history
from patches import extract_calibration, rom_checksums, runtime_endpoints, runtime_targets


@lru_cache(maxsize=1)
def previous_image():
    target = runtime_targets.load_runtime_target("JK08A")
    base = build_rom.builtin_profile("JK08A")
    profile = replace(base, calibration=replace(base.calibration, min_speed=0),
                      telemetry=can_telemetry.Configuration(True, 0x6E0, "tuning", 3))
    data = bytearray(build_rom.build_image(target.stock_image.data, profile=profile).data)
    endpoint = can_telemetry_history.endpoint("schema2-profile7")
    for unit in endpoint.units:
        data[unit.start:unit.end] = unit.payload
    data[endpoint.configuration_address:endpoint.configuration_end] = endpoint.encode(profile.telemetry)
    family = target.map_layout.families[0]
    data[family.canonical_address] ^= 1
    data[family.copies[1] + 3] ^= 0x11
    return bytes(rom_checksums.recalculate(data, target.checksum_layout))


def test_exact_previous_endpoint_is_accepted_when_current_payload_differs():
    target = runtime_targets.load_runtime_target("JK08A")
    expected = dict(target.telemetry_payloads)
    expected["capture"] = bytes([expected["capture"][0] ^ 1]) + expected["capture"][1:]
    assert runtime_endpoints.require_coherent_telemetry_endpoint(
        previous_image(), target.telemetry_layout, expected, "previous",
        target.rolling_layout, rom="JK08A") == "schema2-profile7"


def test_upgrade_preserves_all_calibration_and_matches_rolling_settings():
    source = previous_image()
    result = build_rom.upgrade_image(source)
    target = runtime_targets.load_runtime_target("JK08A")
    for offset in calibration_ranges.load("JK08A").offsets():
        assert result.data[offset] == source[offset], hex(offset)
    assert result.calibration_transfer["settings"]["rolling_launch"] == "matched"
    rolling = target.rolling_layout.configuration
    assert result.data[rolling.start:rolling.end] == source[rolling.start:rolling.end]
    assert result.profile.telemetry == can_telemetry.Configuration(True, 0x6E0, "tuning", 3)
    extraction = extract_calibration.extract(result.data)
    assert dict(extraction.calibration.source)["can_telemetry"] == "current"
    document = build_rom.manifest_data(result, "previous.bin", "upgraded.bin")
    assert document["stages"]["calibration_sha256"] == result.output_sha256
    assert document["calibration_transfer"]["settings"]["rolling_launch"] == "matched"
    current_id = can_telemetry.Configuration.from_bytes(result.telemetry_configuration).profile_spec.profile_id
    if current_id != 7:
        assert result.calibration_transfer["source_runtime"]["can_telemetry"] == "schema2-profile7"
        assert "can_telemetry" not in result.calibration_transfer["settings"]


@pytest.mark.parametrize("damage", ("unit", "profile", "crc", "hook", "mailbox", "reserve"))
def test_upgrade_rejects_partial_or_unknown_previous_endpoint(damage):
    target = runtime_targets.load_runtime_target("JK08A")
    endpoint = can_telemetry_history.endpoint("schema2-profile7")
    data = bytearray(previous_image())
    address = {
        "unit": endpoint.units[0].start,
        "profile": endpoint.configuration_address + 4,
        "crc": endpoint.configuration_address + 10,
        "hook": endpoint.hooks[0].address,
        "mailbox": endpoint.mailbox_record_address,
        "reserve": endpoint.reserved_rom_start,
    }[damage]
    data[address] ^= 1
    data = bytes(rom_checksums.recalculate(data, target.checksum_layout))
    with pytest.raises(build_rom.BuildError):
        build_rom.upgrade_image(data)


def test_previous_signature_is_scoped_to_its_exact_rom_family():
    target = runtime_targets.load_runtime_target("JK08A")
    expected = dict(target.telemetry_payloads)
    expected["capture"] = b"\x00" * len(expected["capture"])
    with pytest.raises(runtime_endpoints.EndpointError):
        runtime_endpoints.require_coherent_telemetry_endpoint(
            previous_image(), target.telemetry_layout, expected, "other ROM",
            target.rolling_layout, rom="JK00D")
