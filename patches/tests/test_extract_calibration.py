"""Extraction moves calibration and settings off an image of a stock build."""

from dataclasses import replace
from functools import lru_cache
from unittest import mock

import pytest

from patches import build_rom
from patches import calibration_file
from patches import calibration_ranges
from patches import extract_calibration
from patches import rolling_launch_layout
from patches import rom_checksums
from patches import runtime_endpoints
from patches import runtime_targets


@lru_cache(maxsize=None)
def target(rom):
    return runtime_targets.load_runtime_target(rom)


@lru_cache(maxsize=None)
def built(rom):
    return build_rom.build_image(
        target(rom).stock_image.data, source_name=f"{rom} stock"
    ).data


def closed(rom, data):
    return bytes(rom_checksums.recalculate(bytearray(data), target(rom).checksum_layout))


def edited(rom, data, edits):
    data = bytearray(data)
    for address, value in edits:
        data[address] ^= value
    return closed(rom, data)


def calibrated(rom, data, elements):
    data = bytearray(data)
    for element in elements:
        data[element.address : element.end] = element.data
    return closed(rom, data)


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_stock_image_has_no_runtime_settings_or_elements(rom):
    extraction = extract_calibration.extract(
        target(rom).stock_image.data, source_name="stock"
    )
    calibration = extraction.calibration
    assert calibration.rom == rom
    assert dict(calibration.source)["sha256"] == calibration.stock_sha256
    assert {key: value for key, value in calibration.source[1:]} == {
        "map_switching": "absent",
        "rolling_launch": "absent",
        "can_telemetry": "absent",
    }
    assert calibration.settings == ()
    assert calibration.elements == ()
    assert not extraction.has_profile


def test_calibrated_stock_yields_exact_runs_and_no_profile():
    family = target("JK08A").map_layout.families[0]
    source = edited("JK08A", target("JK08A").stock_image.data, (
        (0x8725, 0x01),
        (family.canonical_address, 0x10),
        (family.canonical_address + 1, 0x20),
    ))
    extraction = extract_calibration.extract(source, source_name="calibrated")
    assert extraction.calibration.elements == (
        calibration_file.Element(0x8725, source[0x8725:0x8726]),
        calibration_file.Element(
            family.canonical_address,
            source[family.canonical_address : family.canonical_address + 2],
        ),
    )
    assert not extraction.has_profile
    assert calibrated(
        "JK08A", target("JK08A").stock_image.data, extraction.calibration.elements
    ) == source


def test_runs_split_at_adjacent_range_boundaries():
    ranges = calibration_ranges.load("JK08A")
    copies = ranges.map_copies
    left, right = next(
        (first, second) for first, second in zip(copies, copies[1:])
        if first.end == second.start
    )
    reference = bytes(target("JK08A").stock_image.data)
    source = bytearray(reference)
    source[left.end - 1] ^= 0xFF
    source[right.start] ^= 0xFF
    assert extract_calibration._elements(source, reference, ranges) == (
        calibration_file.Element(left.end - 1, bytes(source[left.end - 1 : left.end])),
        calibration_file.Element(right.start, bytes(source[right.start : right.start + 1])),
    )


@pytest.mark.parametrize(
    ("address", "name"),
    (
        (0x2378C, "Engine Torque load axis"),
        (0x8210, "ROM identity"),
        (0x9766, "feedback CAN record"),
        (0x8090, "vector prefix"),
    ),
)
def test_change_outside_the_ranges_is_rejected_by_address(address, name):
    source = edited("JK08A", target("JK08A").stock_image.data, ((address, 0x01),))
    with pytest.raises(
        extract_calibration.ExtractionError,
        match=f"change at {address:#x} is outside the calibration ranges of JK08A",
    ):
        extract_calibration.extract(source, rom="JK08A", source_name=name)


def test_alternate_map_slot_edit_without_a_runtime_is_a_partial_state():
    copy = calibration_ranges.load("JK08A").map_copies[0]
    source = edited("JK08A", target("JK08A").stock_image.data, ((copy.start, 0x01),))
    with pytest.raises(extract_calibration.ExtractionError, match="partial or unknown"):
        extract_calibration.extract(source, source_name="slot edit")


def test_invalid_checksum_is_rejected():
    source = bytearray(target("JK08A").stock_image.data)
    source[0x8725] ^= 0x01
    with pytest.raises(extract_calibration.ExtractionError):
        extract_calibration.extract(bytes(source), source_name="unclosed")


def test_calibration_file_round_trips_and_rejects_foreign_elements():
    family = target("JK08A").map_layout.families[0]
    source = edited("JK08A", target("JK08A").stock_image.data, (
        (0x8725, 0x01), (family.canonical_address, 0x10),
    ))
    calibration = extract_calibration.extract(source).calibration
    text = calibration_file.dumps(calibration)
    assert calibration_file.loads(text, "round trip") == calibration
    for bad, message in (
        (text.replace("0x00008725", "0x0002378C"), "outside the calibration ranges"),
        (text.replace("size = 1", "size = 2", 1), "data must be 2 bytes"),
        (text.replace("schema_version = 1", "schema_version = 2"), "unsupported"),
        (text + "extra = 1\n", "fields differ"),
    ):
        with pytest.raises(calibration_file.CalibrationFileError, match=message):
            calibration_file.loads(bad, "bad")


def test_local_paths_exclude_tracked_repository_locations(tmp_path):
    root = calibration_file.ROOT
    assert calibration_file.require_local_path(root / "tmp/x-calibration.toml")
    assert calibration_file.require_local_path(tmp_path / "x-calibration.toml")
    with pytest.raises(calibration_file.CalibrationFileError, match="Git ignores"):
        calibration_file.require_local_path(root / "patches/x-calibration.toml")


@pytest.mark.parametrize("rom", ("sh7058_7mfkavn86", "sh7059_1nd"))
def test_profile_text_round_trips_through_the_strict_loader(rom):
    profile = build_rom.builtin_profile(rom)
    for telemetry in (None, replace(profile.telemetry, enabled=True, can_id=0x123)):
        text = build_rom.profile_text("round-trip", rom, profile.calibration, telemetry)
        parsed = build_rom.parse_profile(text.encode(), "round trip")
        assert parsed.calibration == profile.calibration
        assert parsed.telemetry == (telemetry or profile.telemetry)


@pytest.mark.slow
@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_builder_output_yields_its_profile_and_no_calibration(rom):
    data = built(rom)
    extraction = extract_calibration.extract(data, source_name="built")
    calibration = extraction.calibration
    rolling_layout = target(rom).rolling_layout
    assert dict(calibration.source)["map_switching"] == "current"
    assert dict(calibration.source)["rolling_launch"] == (
        "absent" if rolling_layout is None else "current"
    )
    assert dict(calibration.source)["can_telemetry"] == "current"
    assert calibration.elements == ()
    profile = build_rom.builtin_profile(build_rom._series_context(rom).key)
    assert extraction.rolling == profile.calibration
    assert extraction.telemetry == profile.telemetry
    telemetry = target(rom).telemetry_layout.configuration
    settings = {
        "can_telemetry": extract_calibration.sha256(data[telemetry.start : telemetry.end]),
    }
    if rolling_layout is not None:
        rolling = rolling_layout.configuration
        settings["rolling_launch"] = extract_calibration.sha256(
            data[rolling.start : rolling.end]
        )
    assert dict(calibration.settings) == settings


@pytest.mark.slow
@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_calibration_and_profile_rebuild_the_source(rom):
    families = target(rom).map_layout.families
    edits = [(family.canonical_address, 0x01) for family in families]
    edits += [
        (address + family.byte_length - 1, 0x02 + slot)
        for family in families
        for slot, address in enumerate(family.copies)
    ]
    source = edited(rom, built(rom), edits)
    extraction = extract_calibration.extract(source, source_name="calibrated build")
    profile = build_rom.parse_profile(
        extract_calibration.profile_bytes(extraction, "rebuild"), "rebuild"
    )
    fresh = build_rom.build_image(
        target(rom).stock_image.data, profile=profile, source_name="stock"
    ).data
    assert calibrated(rom, fresh, extraction.calibration.elements) == source


@pytest.mark.slow
@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_corrupt_rolling_record_is_a_partial_state_on_every_exact_rom(rom):
    configuration = target(rom).rolling_layout.configuration
    source = bytearray(built(rom))
    for offset in range(configuration.start, configuration.end):
        source[offset] ^= 0xA5
    with pytest.raises(
        extract_calibration.ExtractionError,
        match="partial or unknown Rolling Launch state",
    ):
        extract_calibration.extract(closed(rom, source), source_name="corrupt")


@pytest.mark.slow
def test_schema_1_record_is_reported_and_only_calibration_is_written(tmp_path, capsys):
    layout = rolling_launch_layout.load_layout()
    telemetry_layout = target("JK08A").telemetry_layout
    historical = bytearray(runtime_endpoints.strip_telemetry_endpoint(
        built("JK08A"), telemetry_layout, "current"
    ))
    controller = layout.assembly_unit_by_key["speed_controller"]
    historical[controller.span.start : controller.span.end] = (
        bytes([0xFF]) * controller.span.size
    )
    # A historical endpoint keeps its 32-byte record in the retired span.
    historical[layout.configuration.start : layout.configuration.end] = (
        bytes([0xFF]) * layout.configuration.size
    )
    retired = layout.retired_configuration_for(3)
    historical[retired.start : retired.end] = bytes.fromhex(
        "524c0101050000ff010000a00001001000"
        "04012c0064737373737300adb3a55a"
    )
    historical[0x8725] ^= 0x01
    # A historical endpoint leaves the pointer slots of the later views stock.
    for item in layout.diagnostics:
        if item.did not in runtime_endpoints.HISTORICAL_ROLLING_DIDS:
            historical[item.pointer_address : item.pointer_address + 4] = (
                item.stock.to_bytes(4, layout.byte_order)
            )
    historical = closed("JK08A", historical)
    signature = runtime_endpoints.RollingEndpointSignature(
        key="test-schema-1-endpoint",
        roms=("JK08A",),
        configuration_schema_version=1,
        unit_sha256=tuple(
            (unit.key, build_rom.sha256(historical[unit.span.start : unit.span.end]))
            for unit in layout.assembly_units
        ),
        hook_values=tuple(
            (
                hook.key,
                int.from_bytes(
                    historical[hook.address : hook.address + hook.width],
                    layout.byte_order,
                ),
            )
            for hook in layout.hooks
        ),
    )
    image = tmp_path / "historical.bin"
    image.write_bytes(historical)
    calibration = tmp_path / "historical-calibration.toml"
    profile = tmp_path / "historical-profile.toml"
    with mock.patch.object(
        runtime_endpoints, "HISTORICAL_ROLLING_ENDPOINTS", (signature,)
    ):
        extraction = extract_calibration.extract(historical, source_name="schema 1")
        status = extract_calibration.main([
            str(image), "--calibration", str(calibration), "--profile", str(profile),
        ])
    ((component, record, schema_version, fields),) = extraction.unexpressed
    assert (component, record, schema_version) == (
        "rolling_launch", "test-schema-1-endpoint", 1
    )
    assert fields["mode"] == "rpm_hold" and fields["speed_padding"] == 0
    assert "rolling_launch" in dict(extraction.calibration.settings)
    assert status == extract_calibration.EXIT_SETTINGS_NOT_EXPRESSED
    assert calibration_file.load(calibration).elements == (
        calibration_file.Element(0x8725, historical[0x8725:0x8726]),
    )
    assert not profile.exists()
    output = capsys.readouterr().out
    assert "record=test-schema-1-endpoint schema=1" in output
    assert "status=PARTIAL profile=not_written" in output
