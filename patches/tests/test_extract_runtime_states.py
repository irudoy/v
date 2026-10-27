"""Extraction recognizes the current and registered historical runtimes.

Every case starts from a current builder output with the built-in profile and
turns it into a registered earlier endpoint, an editor-edited runtime, or a
partial state.
"""

from dataclasses import replace
from functools import lru_cache
from unittest import mock

import pytest

from patches import apply_calibration
from patches import build_rom
from patches import can_telemetry
from patches import extract_calibration
from patches import rolling_launch
from patches import rom_checksums
from patches import runtime_endpoints
from patches import runtime_targets


pytestmark = pytest.mark.slow

# Exact controller bytes of the registered schema-3 guarded endpoint.
GUARDED_CONTROLLER = bytes.fromhex(
    "4f223248d1178516630d2f368519630d2338891ad1146011610d31368b1560f2"
    "3102890b313830382008890e212e011ad30e430b0009340ca0010009342cd10c"
    "60432100d1077111210060f64f26d009402b0009ffffffffffffffffffffffff"
    "ffffffffffff5d40ffff11bc00021ce0ffff20220002a892ffffffffffffffff"
)
EIGHT_MFK_GUARDED_CONTROLLER = bytes.fromhex(
    "4f223248d1178516630d2f368519630d2338891ad1146011610d31368b1560f2"
    "3102890b313830382008890e212e011ad30e430b0009340ca0010009342cd10c"
    "60432100d1077111210060f64f26d009402b0009ffffffffffffffffffffffff"
    "ffffffffffff6040ffff11ca00021d6cffff11f50002b51affffffffffffffff"
)
ND_GUARDED_CONTROLLER = bytes.fromhex(
    "4f223248d1178516630d2f368519630d2338891ad1146011610d31368b1560f2"
    "3102890b313830382008890e212e011ad30e430b0009340ca0010009342cd10c"
    "60432100d1077111210060f64f26d009402b0009ffffffffffffffffffffffff"
    "ffffffffffff0c40fffe81b600022318fffe81dd0002e464ffffffffffffffff"
)
ME3B_GUARDED_CONTROLLER = bytes.fromhex(
    "4f223248d1178516630d2f368519630d2338891ad1146011610d31368b1560f2"
    "3102890b313830382008890e212e011ad30e430b0009340ca0010009342cd10c"
    "60432100d1077111210060f64f26d009402b0009ffffffffffffffffffffffff"
    "ffffffffffff0c40fffe819e00022394fffe81c3000311b2ffffffffffffffff"
)
JK78C_GUARDED_CONTROLLER = bytes.fromhex(
    "4f223248d1178516630d2f368519630d2338891ad1146011610d31368b1560f2"
    "3102890b313830382008890e212e011ad30e430b0009340ca0010009342cd10c"
    "60432100d1077111210060f64f26d009402b0009ffffffffffffffffffffffff"
    "ffffffffffff0c40ffff11ac00021e0cffff11cf0002d6f6ffffffffffffffff"
)
EDITED_ROMS = ("JK08A", "JK00C", "JK78C", "1ND0A", "1ME3B")


def guarded_controller_for(rom):
    if rom in runtime_targets.EXACT_ROMS:
        return GUARDED_CONTROLLER
    if rom in runtime_targets.RELOCATED_8MFK_ROMS:
        return EIGHT_MFK_GUARDED_CONTROLLER
    if rom in runtime_targets.SH7059_1ND_ROMS:
        return ND_GUARDED_CONTROLLER
    if rom in runtime_targets.SH7059_1ME3B_ROMS:
        return ME3B_GUARDED_CONTROLLER
    if rom == "JK78C":
        return JK78C_GUARDED_CONTROLLER
    raise AssertionError(rom)


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


def extract(source, rom="JK08A"):
    return extract_calibration.extract(closed(rom, source), rom=rom)


def state(extraction):
    return dict(extraction.calibration.source[1:])


def without_telemetry(rom, data):
    return runtime_endpoints.strip_telemetry_endpoint(
        data, target(rom).telemetry_layout, "current", target(rom).checksum_layout
    )


def edited_runtime(rom, *, rolling=False, telemetry=False):
    """Return a current build whose settings an editor changed."""
    edited = bytearray(built(rom))
    if rolling:
        start = target(rom).rolling_layout.configuration.start
        # Editor fields in the current 32-byte Rolling Launch record.
        edited[start + 3] = rolling_launch.Mode.RPM_HOLD
        edited[start + 4] = 0x02  # Map 1 disabled, Map 2 enabled.
        edited[start + 8] = 0  # Vehicle-speed activation gate disabled.
        edited[start + 18 : start + 20] = (301).to_bytes(2, "big")
        edited[start + 22] = 114  # Map 1 target command.
    if telemetry:
        layout = target(rom).telemetry_layout
        start = layout.configuration.start
        # Editor fields in the current 16-byte telemetry record.
        edited[start + 3] = 1  # Enable sampling after reset.
        edited[start + 6] = 7  # Snapshot divisor.
        edited[start + 8 : start + 10] = (0x6E0).to_bytes(2, "big")
        configuration = can_telemetry.Configuration.from_bytes(
            edited[start : layout.configuration.end]
        )
        record = layout.mailbox_record_address
        edited[record : record + 4] = configuration.mailbox_record()
    return closed(rom, edited)


def previous_current_image(*, telemetry=True, custom=False):
    source = (
        edited_runtime("JK08A", rolling=True, telemetry=True)
        if custom else built("JK08A")
    )
    if not telemetry:
        source = without_telemetry("JK08A", source)
    historical = bytearray(source)
    unit = target("JK08A").rolling_layout.assembly_unit_by_key["ignition_controller"]
    historical[unit.span.start : unit.span.end] = GUARDED_CONTROLLER
    return closed("JK08A", historical)


def state_6_7_arbiter_image():
    layout = target("JK08A").rolling_layout
    unit = layout.assembly_unit_by_key["feedback_arbiter"]
    active_immediate = unit.span.start + 0x2D
    failed_immediate = unit.span.start + 0x41
    historical = bytearray(built("JK08A"))
    assert historical[active_immediate] == 0x40
    assert historical[failed_immediate] == 0x50
    historical[active_immediate] = 0x70
    historical[failed_immediate] = 0x60
    controller = layout.assembly_unit_by_key["ignition_controller"]
    historical[controller.span.start : controller.span.end] = GUARDED_CONTROLLER
    endpoint = next(
        item for item in runtime_endpoints.HISTORICAL_ROLLING_ENDPOINTS
        if item.key == "schema-3-state-6-7-indicators"
    )
    assert dict(endpoint.unit_sha256)["feedback_arbiter"] == build_rom.sha256(
        historical[unit.span.start : unit.span.end]
    )
    return closed("JK08A", historical)


def test_current_builder_output_is_the_current_runtime():
    extraction = extract(built("JK08A"))
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "current",
        "can_telemetry": "current",
    }
    assert extraction.calibration.elements == ()
    assert extraction.rolling == build_rom.builtin_profile().calibration


def test_map_switching_endpoint_carries_no_settings():
    layout = target("JK08A").rolling_layout
    map_only = bytearray(without_telemetry("JK08A", built("JK08A")))
    for span in layout.claimed_rom_ranges:
        map_only[span.start : span.end] = bytes([0xFF]) * span.size
    for hook in layout.hooks:
        map_only[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
            hook.width, layout.byte_order
        )
    for diagnostic in layout.diagnostics:
        map_only[diagnostic.pointer_address : diagnostic.pointer_address + 4] = (
            diagnostic.stock.to_bytes(4, layout.byte_order)
        )
    extraction = extract(map_only)
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "absent",
        "can_telemetry": "absent",
    }
    assert extraction.calibration.settings == ()
    assert extraction.calibration.elements == ()
    assert not extraction.has_profile


@pytest.mark.parametrize("status_mask", (0x8F, 0x9F))
def test_state_6_feedback_engines_are_registered_map_endpoints(status_mask):
    map_layout = target("JK08A").map_layout
    engine = map_layout.assembly_unit_by_key["cruise_feedback_engine"]
    status_mask_immediate = engine.span.start + 0x41
    lamp_on_immediate = engine.span.start + 0x4B
    phase_counts = map_layout.feedback.phase_counts_address
    historical = bytearray(built("JK08A"))
    assert historical[status_mask_immediate] == 0x8F
    assert historical[lamp_on_immediate] == 0x40
    assert historical[phase_counts : phase_counts + 2] == bytes((20, 20))
    historical[status_mask_immediate] = status_mask
    historical[lamp_on_immediate] = 0x60
    historical[phase_counts : phase_counts + 2] = bytes((30, 30))
    assert build_rom.sha256(
        historical[engine.span.start : engine.span.end]
    ) in runtime_endpoints.HISTORICAL_FEEDBACK_ENGINE_SHA256
    extraction = extract(historical)
    assert state(extraction)["map_switching"] == "current"
    assert extraction.calibration.elements == ()


def test_unregistered_feedback_engine_is_rejected():
    engine = target("JK08A").map_layout.assembly_unit_by_key["cruise_feedback_engine"]
    historical = bytearray(built("JK08A"))
    historical[engine.span.start + 0x4B] = 0x50
    with pytest.raises(
        extract_calibration.ExtractionError, match="cruise_feedback_engine differs"
    ):
        extract(historical)


def test_state_6_7_arbiter_endpoint_is_recognized_under_telemetry():
    extraction = extract(state_6_7_arbiter_image())
    assert state(extraction) == {
        "map_switching": "current",
        "rolling_launch": "schema-3-state-6-7-indicators",
        "can_telemetry": "current",
    }
    assert extraction.has_profile


def test_telemetry_over_an_unflagged_historical_endpoint_is_rejected():
    with mock.patch.object(
        runtime_endpoints, "TELEMETRY_LOWER_ROLLING_STATES", frozenset({"current"})
    ):
        with pytest.raises(extract_calibration.ExtractionError, match="not layered"):
            extract(state_6_7_arbiter_image())


def test_pre_feedback_indicator_endpoint_is_recognized():
    layout = target("JK08A").rolling_layout
    historical = bytearray(without_telemetry("JK08A", built("JK08A")))
    unit = layout.assembly_unit_by_key["feedback_arbiter"]
    historical[unit.span.start : unit.span.end] = bytes([0xFF]) * unit.span.size
    hook = layout.hook_by_key["feedback_arbitration"]
    assert int.from_bytes(
        historical[hook.address : hook.address + hook.width], layout.byte_order
    ) == hook.replacement
    historical[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
        hook.width, layout.byte_order
    )
    controller = layout.assembly_unit_by_key["ignition_controller"]
    historical[controller.span.start : controller.span.end] = GUARDED_CONTROLLER
    extraction = extract(historical)
    assert state(extraction)["rolling_launch"] == "schema-3-pre-feedback-indicators"
    assert state(extraction)["can_telemetry"] == "absent"
    assert extraction.rolling == build_rom.builtin_profile().calibration
    assert extraction.telemetry is None


@pytest.mark.parametrize("telemetry", (False, True))
def test_previous_guarded_controller_is_recognized_with_or_without_telemetry(telemetry):
    extraction = extract(previous_current_image(telemetry=telemetry))
    assert state(extraction)["rolling_launch"] == "schema-3-guarded-controller"
    assert state(extraction)["can_telemetry"] == ("current" if telemetry else "absent")


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_previous_guarded_controller_is_recognized_on_every_rom(rom):
    unit = target(rom).rolling_layout.assembly_unit_by_key["ignition_controller"]
    source = bytearray(built(rom))
    source[unit.span.start : unit.span.end] = guarded_controller_for(rom)
    extraction = extract(source, rom)
    assert state(extraction)["rolling_launch"].startswith("schema-3-guarded-controller")
    assert extraction.calibration.elements == ()


@pytest.mark.parametrize("rom", ("JK00C", "1ND0A", "JK78C"))
def test_relocated_guarded_controller_hybrid_is_refused(rom):
    unit = target(rom).rolling_layout.assembly_unit_by_key["ignition_controller"]
    source = bytearray(built(rom))
    source[unit.span.start : unit.span.end] = guarded_controller_for(rom)
    source[unit.span.start] ^= 1
    with pytest.raises(
        extract_calibration.ExtractionError, match="partial or unknown Rolling Launch"
    ):
        extract(source, rom)


@pytest.mark.parametrize("part", ("ignition_controller", "engine", "configuration"))
def test_previous_guarded_controller_hybrid_and_malformed_endpoint_are_refused(part):
    layout = target("JK08A").rolling_layout
    address = (
        layout.configuration.start if part == "configuration"
        else layout.assembly_unit_by_key[part].span.start
    )
    source = bytearray(previous_current_image())
    source[address] ^= 1
    with pytest.raises(
        extract_calibration.ExtractionError, match="partial or unknown Rolling Launch"
    ):
        extract(source)


def test_previous_endpoint_carries_its_editor_settings_into_the_profile():
    extraction = extract(previous_current_image(custom=True))
    assert extraction.rolling.mode == rolling_launch.Mode.RPM_HOLD
    assert extraction.rolling.enable_mask == 0x02
    assert extraction.rolling.min_speed == 0
    assert extraction.telemetry == can_telemetry.Configuration(True, 0x6E0, "tuning", 7)


@pytest.mark.parametrize("rom", EDITED_ROMS)
@pytest.mark.parametrize("component", ("rolling_launch", "can_telemetry"))
def test_editor_settings_need_their_profile_or_an_explicit_replacement(rom, component):
    source = edited_runtime(
        rom,
        rolling=component == "rolling_launch",
        telemetry=component == "can_telemetry",
    )
    extraction = extract_calibration.extract(source, rom=rom)
    profile = build_rom.builtin_profile(target(rom).family)
    if component == "rolling_launch":
        assert extraction.rolling.enable_mask == 0x02
        assert extraction.rolling.target_commands[0] == 114
        assert extraction.telemetry == profile.telemetry
    else:
        assert extraction.rolling == profile.calibration
        assert extraction.telemetry == can_telemetry.Configuration(
            True, 0x6E0, "tuning", 7
        )
    assert extraction.calibration.elements == ()
    with pytest.raises(
        apply_calibration.ApplicationError,
        match=f"differ from the extracted settings: {component};",
    ):
        apply_calibration.apply(built(rom), extraction.calibration)


@pytest.mark.parametrize("rom", ("JK08A", "JK00C"))
def test_editor_disabling_only_map_1_rpm_hold_travels_in_the_profile(rom):
    start = target(rom).rolling_layout.configuration.start
    edited = bytearray(built(rom))
    assert edited[start + 3] == rolling_launch.Mode.RPM_HOLD
    assert edited[start + 4] & 1 == 1
    edited[start + 4] &= ~1
    extraction = extract(edited, rom)
    assert extraction.rolling == replace(
        build_rom.builtin_profile(target(rom).family).calibration, enable_mask=0
    )
    with pytest.raises(apply_calibration.ApplicationError, match="rolling_launch"):
        apply_calibration.apply(built(rom), extraction.calibration)


def _rolling_cases():
    layout = target("JK08A").rolling_layout
    base = built("JK08A")
    unknown_payload = bytearray(base)
    unknown_payload[0xD3900] ^= 0x01
    partial_hook = bytearray(base)
    hook = layout.hooks[0]
    partial_hook[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
        hook.width, layout.byte_order
    )
    partial_did = bytearray(base)
    diagnostic = layout.diagnostics[0]
    partial_did[diagnostic.pointer_address : diagnostic.pointer_address + 4] = (
        diagnostic.stock.to_bytes(4, layout.byte_order)
    )
    invalid_configuration = bytearray(base)
    invalid_configuration[layout.configuration.start + 9] = 0
    mixed_schema = bytearray(base)
    mixed_schema[layout.configuration.start : layout.configuration.end] = bytes.fromhex(
        "524c0101050000ff010000a00001001000"
        "04012c0064737373737300adb3a55a"
    )
    return {
        "unknown-payload": unknown_payload,
        "partial-hook": partial_hook,
        "partial-did": partial_did,
        "framed-invalid-configuration": invalid_configuration,
        "current-payload-schema-1": mixed_schema,
    }


@pytest.mark.parametrize(
    "case",
    (
        "unknown-payload",
        "partial-hook",
        "partial-did",
        "framed-invalid-configuration",
        "current-payload-schema-1",
    ),
)
def test_partial_and_unknown_rolling_states_are_rejected(case):
    with pytest.raises(
        extract_calibration.ExtractionError,
        match="partial or unknown Rolling Launch state",
    ):
        extract(_rolling_cases()[case])


def test_partial_map_pointer_state_is_rejected():
    partial = bytearray(built("JK08A"))
    partial[target("JK08A").map_layout.families[0].pointer_table] ^= 1
    with pytest.raises(extract_calibration.ExtractionError, match="pointer table"):
        extract(partial)


@pytest.mark.parametrize(
    "case", ("damaged-unit", "damaged-hook", "damaged-configuration")
)
def test_partial_can_telemetry_states_are_rejected(case):
    layout = target("JK08A").telemetry_layout
    source = bytearray(built("JK08A"))
    if case == "damaged-unit":
        source[layout.assembly_units[0].span.start] ^= 1
    elif case == "damaged-hook":
        hook = layout.hooks[0]
        source[hook.address : hook.address + hook.width] = hook.stock.to_bytes(
            hook.width, layout.byte_order
        )
    else:
        source[layout.configuration.start] ^= 1
    with pytest.raises(
        extract_calibration.ExtractionError,
        match="partial or unknown CAN telemetry state",
    ):
        extract(source)


def test_occupied_telemetry_reserve_is_rejected_by_address():
    reserve = target("JK08A").telemetry_layout.reserved_rom.start
    source = bytearray(built("JK08A"))
    source[reserve] = 0
    with pytest.raises(
        extract_calibration.ExtractionError,
        match=f"change at {reserve:#x} is outside the calibration ranges",
    ):
        extract(source)
