"""Runtime endpoint classification is scoped to the selected ROM, and each
registered historical endpoint is placed by its own addresses."""

from dataclasses import replace
from functools import lru_cache

import pytest

from patches import build_rom
from patches import calibration_ranges
from patches import extract_calibration
from patches import rom_checksums
from patches import runtime_endpoints
from patches import runtime_targets
from patches.tests import rolling_endpoint_images as endpoint_images


# The two endpoints flashed on JK08A: the uniform-gain speed hold and the
# per-map slots with the fixed retard trim.
FLASHED_ENDPOINTS = ("schema-4-uniform-gain", "schema-5-fixed-trim")
# The Rolling Launch parts that the fuel path owns in the flashed endpoints.
FUEL_PATH_UNITS = frozenset({"fuel_cut_wrapper", "rpm_ceiling"})
FUEL_PATH_HOOKS = frozenset({"fuel_cut_coordinator"})
FUEL_PATH_DIDS = frozenset({0x121E, 0x1231})


@lru_cache(maxsize=None)
def target(rom):
    return runtime_targets.load_runtime_target(rom)


def installed_rolling_layer(rom, configuration):
    """Stock bytes with the current Rolling Launch units, hooks and DIDs."""
    layout = target(rom).rolling_layout
    data = bytearray(target(rom).stock_image.data)
    for unit in layout.assembly_units:
        data[unit.span.start : unit.span.end] = target(rom).rolling_payloads[unit.key]
    for hook in layout.hooks:
        data[hook.address : hook.address + hook.width] = hook.replacement.to_bytes(
            hook.width, layout.byte_order
        )
    for item in layout.diagnostics:
        data[item.pointer_address : item.pointer_address + 4] = item.target.to_bytes(
            4, layout.byte_order
        )
    data[layout.configuration.start : layout.configuration.end] = configuration
    return bytes(data)


def test_signature_keys_are_unique_and_name_supported_roms():
    keys = [endpoint.key for endpoint in runtime_endpoints.HISTORICAL_ROLLING_ENDPOINTS]
    assert len(keys) == len(set(keys))
    for endpoint in runtime_endpoints.HISTORICAL_ROLLING_ENDPOINTS:
        assert endpoint.roms
        assert set(endpoint.roms) <= set(runtime_targets.SUPPORTED_ROMS)


@pytest.mark.parametrize("rom", runtime_targets.RELOCATED_ROMS)
def test_a_relocated_rom_has_no_rolling_launch_endpoint(rom):
    assert target(rom).rolling_layout is None
    assert not runtime_endpoints.historical_endpoints(rom)


@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_corrupt_configuration_is_a_named_state_on_every_rom(rom):
    layout = target(rom).rolling_layout
    corrupt = bytes([0xA5]) * layout.configuration.size
    source = installed_rolling_layer(rom, corrupt)
    with pytest.raises(
        runtime_endpoints.EndpointError,
        match="partial or unknown Rolling Launch state",
    ):
        runtime_endpoints.require_coherent_rolling_endpoint(
            source, layout, target(rom).rolling_payloads, "corrupt", rom
        )


@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_every_signature_of_a_rom_is_placed_in_erased_stock_rom(rom):
    endpoints = runtime_endpoints.historical_endpoints(rom)
    assert endpoints
    stock = target(rom).stock_image.data
    for endpoint in endpoints:
        runtime_endpoints.require_valid_signature(endpoint)
        for item in (*endpoint.units, endpoint.record):
            assert stock[item.start : item.end] == bytes([0xFF]) * (
                item.end - item.start
            ), (endpoint.key, item)
        assert max(endpoint.write_offsets()) < len(stock)


@pytest.mark.parametrize("damage", ("unit", "digest", "overlap", "record"))
def test_invalid_signature_is_internal(monkeypatch, damage):
    endpoint = runtime_endpoints.historical_endpoint("schema-5-fixed-trim")
    addresses = endpoint.addresses
    if damage == "unit":
        endpoint = replace(
            endpoint, unit_sha256=endpoint.unit_sha256 + (("absent_unit", "0" * 64),)
        )
    elif damage == "digest":
        key, digest = endpoint.unit_sha256[0]
        endpoint = replace(
            endpoint,
            unit_sha256=((key, digest.upper()),) + endpoint.unit_sha256[1:],
        )
    elif damage == "overlap":
        key, address, width = addresses.hook_words[0]
        moved = (key, addresses.unit_spans[0][1], width)
        endpoint = replace(endpoint, addresses=replace(
            addresses, hook_words=(moved,) + addresses.hook_words[1:]
        ))
    else:
        endpoint = replace(endpoint, configuration_schema_version=6)
    source = endpoint_image("schema-4-uniform-gain", lower=True)
    monkeypatch.setattr(runtime_endpoints, "HISTORICAL_ROLLING_ENDPOINTS", (endpoint,))
    with pytest.raises(runtime_endpoints.EndpointError, match="is invalid"):
        runtime_endpoints.require_coherent_rolling_endpoint(
            source,
            target("JK08A").rolling_layout,
            target("JK08A").rolling_payloads,
            "invalid",
            "JK08A",
        )


def test_flashed_endpoints_are_scoped_to_their_roms():
    assert runtime_endpoints.historical_endpoint("schema-5-fixed-trim").roms == ("JK08A",)
    for rom in set(runtime_targets.EXACT_ROMS) - {"JK08A"}:
        keys = {endpoint.key for endpoint in runtime_endpoints.historical_endpoints(rom)}
        assert "schema-5-fixed-trim" not in keys


@lru_cache(maxsize=None)
def built_image():
    return build_rom.build_image(
        target("JK08A").stock_image.data, source_name="JK08A stock"
    ).data


def closed(data):
    return bytes(rom_checksums.recalculate(bytearray(data), target("JK08A").checksum_layout))


def endpoint_image(key, *, record=None, lower=False):
    """Return the current build with a flashed endpoint at its own addresses
    in place of the current Rolling Launch layer; ``lower`` returns the bytes
    below the CAN telemetry layer."""
    current = target("JK08A")
    source = closed(endpoint_images.with_endpoint(
        current,
        built_image(),
        key,
        endpoint_images.record(key) if record is None else record,
    ))
    if lower:
        source = runtime_endpoints.strip_telemetry_endpoint(
            source, current.telemetry_layout, "current", current.checksum_layout
        )
    return source


def changed_target(*, fuel_path, telemetry=False, adapter=True):
    """Return the JK08A target with a different current ignition adapter and,
    with ``fuel_path`` false, a current layout without the fuel-cut wrapper,
    the RPM ceiling, their hook and DIDs, and the schema 4 record span.
    ``telemetry`` also changes the current CAN telemetry capture unit, and a
    false ``adapter`` keeps the current adapter."""
    current = target("JK08A")
    if telemetry:
        telemetry_payloads = dict(current.telemetry_payloads)
        capture = telemetry_payloads["capture"]
        telemetry_payloads["capture"] = bytes([capture[0] ^ 1]) + capture[1:]
        current = replace(current, telemetry_payloads=telemetry_payloads)
    payloads = dict(current.rolling_payloads)
    if adapter:
        blob = payloads["ignition_adapter"]
        payloads["ignition_adapter"] = blob[:-1] + bytes([blob[-1] ^ 0x5A])
    layout = current.rolling_layout
    if not fuel_path:
        payloads = {
            key: value for key, value in payloads.items() if key not in FUEL_PATH_UNITS
        }
        claimed = tuple(
            replace(span, start=0x000D60C0) if span.start == 0x000D6000 else span
            for span in layout.claimed_rom_extensions
        )
        layout = replace(
            layout,
            claimed_rom_extensions=claimed,
            retired_configurations=tuple(
                item for item in layout.retired_configurations
                if 4 not in item.schema_versions
            ),
            assembly_units=tuple(
                unit for unit in layout.assembly_units if unit.key not in FUEL_PATH_UNITS
            ),
            hooks=tuple(hook for hook in layout.hooks if hook.key not in FUEL_PATH_HOOKS),
            diagnostics=tuple(
                item for item in layout.diagnostics if item.did not in FUEL_PATH_DIDS
            ),
        )
    return replace(current, rolling_layout=layout, rolling_payloads=payloads)


@pytest.fixture
def selected_target(monkeypatch):
    """Serve a replaced JK08A target to classification and extraction. The
    current target and its build are cached first."""
    target("JK08A")
    built_image()
    selected = {}
    original = runtime_targets.load_runtime_target

    def load(rom, *args, **kwargs):
        return selected.get(rom) or original(rom, *args, **kwargs)

    monkeypatch.setattr(runtime_targets, "load_runtime_target", load)
    calibration_ranges.load.cache_clear()
    yield selected
    calibration_ranges.load.cache_clear()


@pytest.mark.parametrize(
    ("fuel_path", "telemetry"), ((True, False), (False, False), (False, True))
)
@pytest.mark.parametrize("key", FLASHED_ENDPOINTS)
def test_flashed_endpoint_survives_a_change_of_the_current_runtime(
    selected_target, key, fuel_path, telemetry
):
    changed = changed_target(fuel_path=fuel_path, telemetry=telemetry)
    telemetry_state = "schema2-profile9" if telemetry else "current"
    source = bytearray(endpoint_image(key))
    family = changed.map_layout.families[0]
    source[family.canonical_address] ^= 1
    source = closed(source)
    selected_target["JK08A"] = changed
    classification = runtime_endpoints.classify_runtime(source, changed, "flashed")
    assert classification == runtime_endpoints.Classification(
        telemetry=telemetry_state, rolling=key
    )
    extraction = extract_calibration.extract(source, rom="JK08A")
    states = dict(extraction.calibration.source)
    assert states["rolling_launch"] == key
    assert states["can_telemetry"] == telemetry_state
    assert extraction.telemetry is not None
    assert any(
        element.address == family.canonical_address
        for element in extraction.calibration.elements
    )
    record = runtime_endpoints.historical_endpoint(key).record
    assert runtime_endpoints.configuration_record(
        source, changed.rolling_layout, key
    ) == source[record.start : record.end]


@pytest.mark.parametrize("part", ("schema-4-engine", "fuel-hook", "fuel-did", "record"))
def test_mixed_flashed_endpoint_is_refused_by_a_changed_runtime(part):
    changed = changed_target(fuel_path=False)
    source = bytearray(endpoint_image("schema-5-fixed-trim"))
    stock = target("JK08A").stock_image.data
    if part == "schema-4-engine":
        unit = endpoint_images.unit("schema-4-uniform-gain", "engine")
        source[unit.start : unit.end] = endpoint_images.unit_payload(
            "schema-4-uniform-gain", "engine"
        )
    elif part == "fuel-hook":
        hook = endpoint_images.hook("schema-5-fixed-trim", "fuel_cut_coordinator")
        source[hook.address : hook.address + 4] = stock[hook.address : hook.address + 4]
    elif part == "fuel-did":
        item = next(
            item for item in runtime_endpoints.historical_endpoint("schema-5-fixed-trim").dids
            if item.did == 0x121E
        )
        end = item.pointer_address + 4
        source[item.pointer_address : end] = stock[item.pointer_address : end]
    else:
        # The schema 4 record joins the schema 5 record.
        legacy = runtime_endpoints.historical_endpoint("schema-4-uniform-gain").record
        source[legacy.start : legacy.end] = endpoint_images.record("schema-4-uniform-gain")
    with pytest.raises(runtime_endpoints.EndpointError, match="partial or unknown"):
        runtime_endpoints.classify_runtime(closed(source), changed, "mixed")


def test_changed_current_runtime_refuses_leftover_fuel_path_bytes():
    """A current image holds no fuel-path byte of a flashed endpoint outside
    the current Rolling Launch layout."""
    changed = changed_target(fuel_path=False, adapter=False)
    layout = changed.rolling_layout
    covered = {
        offset
        for start, end in (
            *((unit.span.start, unit.span.end) for unit in layout.assembly_units),
            *((span.start, span.end) for span in (
                layout.configuration, *layout.retired_configuration_spans
            )),
            *((hook.address, hook.address + hook.width) for hook in layout.hooks),
            *((item.pointer_address, item.pointer_address + 4)
              for item in layout.diagnostics),
        )
        for offset in range(start, end)
    }
    key = "schema-5-fixed-trim"
    endpoint = runtime_endpoints.historical_endpoint(key)
    parts = [
        (unit.start, unit.end, endpoint_images.unit_payload(key, unit.key))
        for unit in endpoint.units if unit.key in FUEL_PATH_UNITS
    ]
    parts += [
        (hook.address, hook.address + hook.width, hook.value.to_bytes(hook.width, "big"))
        for hook in endpoint.hooks if hook.key in FUEL_PATH_HOOKS
    ]
    parts += [
        (item.pointer_address, item.pointer_address + 4, item.target.to_bytes(4, "big"))
        for item in endpoint.dids if item.did in FUEL_PATH_DIDS
    ]
    parts = [
        part for part in parts
        if not covered.intersection(range(part[0], part[1]))
    ]
    assert parts
    stock = target("JK08A").stock_image.data
    clean = bytearray(built_image())
    for start, end, _payload in parts:
        clean[start:end] = stock[start:end]
    assert runtime_endpoints.classify_runtime(closed(clean), changed, "clean").rolling == (
        "current"
    )
    leftover = bytearray(clean)
    for start, end, payload in parts:
        leftover[start:end] = payload
    with pytest.raises(runtime_endpoints.EndpointError, match="partial or unknown"):
        runtime_endpoints.classify_runtime(closed(leftover), changed, "leftover")


SCHEMA_5_SLOTS = (
    "0000" "00" "00" "03e8",
    "0002" "00" "00" "03e8",
    "0004" "00" "00" "03e8",
    "0002" "14" "78" "0338",
    "0000" "00" "00" "03e8",
)


def schema_5_record(*slots):
    head = endpoint_images.record("schema-5-fixed-trim")[:40]
    return head + bytes.fromhex("".join(slots)) + bytes.fromhex("a55a")


@pytest.mark.parametrize(
    ("slot", "valid"),
    (
        ("0002" "14" "78" "0338", True),
        ("0002" "28" "78" "0001", True),
        ("0002" "29" "78" "0338", False),
        ("0002" "14" "78" "0000", False),
        ("0002" "14" "78" "03e9", False),
        ("0002" "00" "00" "0338", False),
        ("8000" "00" "00" "03e8", False),
    ),
)
def test_schema_5_record_contract_is_frozen(slot, valid):
    record = schema_5_record(*SCHEMA_5_SLOTS[:3], slot, SCHEMA_5_SLOTS[4])
    assert runtime_endpoints.historical_configuration_is_valid(record, 5) is valid
    if valid:
        fields = runtime_endpoints.historical_configuration_fields(record, 5)
        assert fields["mode"] == "observe"
        assert fields["slots"][3]["integral_gain"] == 2
        assert fields["slots"][2]["integral_gain"] == 4
        assert fields["rpm_ceiling_offset_native"] == 80


def test_schema_4_record_contract_is_frozen():
    record = bytearray(endpoint_images.record("schema-4-uniform-gain"))
    record[0x16:0x18] = (3).to_bytes(2, "big")
    assert runtime_endpoints.historical_configuration_fields(bytes(record), 4)[
        "integral_gain"
    ] == 3
    record[0x16:0x18] = (0x8000).to_bytes(2, "big")
    assert not runtime_endpoints.historical_configuration_is_valid(bytes(record), 4)
    assert not runtime_endpoints.historical_configuration_is_valid(
        schema_5_record(*SCHEMA_5_SLOTS)[:40], 5
    )


@pytest.mark.parametrize("key", FLASHED_ENDPOINTS)
def test_flashed_endpoint_upgrades_with_its_settings_and_calibration(key):
    """The upgrade composes the current runtime over the flashed calibration.
    The schema 5 endpoint is the current runtime until the runtime changes."""
    record = bytearray(endpoint_images.record(key))
    record[4] = 0x0E  # Maps 2 to 4 enabled.
    source = bytearray(endpoint_image(key, record=bytes(record)))
    family = target("JK08A").map_layout.families[0]
    source[family.copies[1] + 3] ^= 0x11
    source = closed(source)
    result = build_rom.upgrade_image(source)
    assert result.calibration_transfer["source_runtime"]["rolling_launch"] in (key, "current")
    assert result.calibration_transfer["settings"]["rolling_launch"] == "matched"
    assert result.profile.calibration.enable_mask == 0x0E
    for offset in calibration_ranges.load("JK08A").offsets():
        assert result.data[offset] == source[offset], hex(offset)
