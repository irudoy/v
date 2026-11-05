"""Runtime endpoint classification is scoped to the selected ROM, and each
registered historical endpoint is placed by its own addresses."""

from dataclasses import replace
from functools import lru_cache

import pytest

from patches import build_rom
from patches import calibration_ranges
from patches import can_telemetry
from patches import can_telemetry_history
from patches import extract_calibration
from patches import map_switching_compose
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
# The fuel-path values of the flashed endpoints at the restored stock words:
# scheduler entry 28 at the fuel-cut wrapper, and the request and ceiling DID
# pointers.
FUEL_PATH_WORDS = (
    (0x000219DC, 0x000D6000),
    (0x00022914, 0xFFFF5D54),
    (0x00022960, 0xFFFF5D58),
)
# The flashed endpoints redirect the GR11A spark vector to their spark cut;
# the current runtime keeps the stock handler there.
SPARK_VECTOR_WORD = (0x000202E4, 0x000D60C0)
RESTORED_ENDPOINT_WORDS = FUEL_PATH_WORDS + (SPARK_VECTOR_WORD,)


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


@lru_cache(maxsize=None)
def map_only_image():
    """The JK08A stock image with the current Map Switching runtime alone."""
    current = target("JK08A")
    return map_switching_compose.compose(
        layout=current.map_layout,
        image=current.stock_image,
        blobs=current.map_payloads,
    ).data


def absent_state(source):
    """Classify the Rolling Launch layer of ``source``; the absent state reads
    no payload bytes, so empty payloads of the layout units serve it."""
    layout = target("JK08A").rolling_layout
    payloads = {unit.key: b"" for unit in layout.assembly_units}
    return runtime_endpoints.require_coherent_rolling_endpoint(
        source, layout, payloads, "map only", "JK08A"
    )


def test_map_only_image_has_an_absent_rolling_layer():
    assert {address for address, _ in RESTORED_ENDPOINT_WORDS} == {
        item.address for item in target("JK08A").rolling_layout.restored_words
    }
    assert absent_state(map_only_image()) == "absent"


@pytest.mark.parametrize("address,value", RESTORED_ENDPOINT_WORDS)
def test_absent_rolling_layer_refuses_each_leftover_endpoint_word(address, value):
    data = bytearray(map_only_image())
    data[address : address + 4] = value.to_bytes(4, "big")
    with pytest.raises(
        runtime_endpoints.EndpointError,
        match="partial or unknown Rolling Launch state",
    ):
        absent_state(bytes(data))


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


def test_current_write_set_holds_the_derived_table_and_the_restored_words():
    """The current layer composes the efficiency table, keeps its removed
    spans erased and restores the stock words of the removed fuel path."""
    current = target("JK08A")
    layout = current.rolling_layout
    offsets = runtime_endpoints._current_write_offsets(layout)
    stock = runtime_endpoints._layout_stock_bytes(layout)
    for span in (layout.efficiency, *layout.erased_rom_ranges):
        assert set(range(span.start, span.end)) <= offsets, span.key
        assert all(stock[offset] == 0xFF for offset in range(span.start, span.end))
    assert layout.restored_words
    for item in layout.restored_words:
        words = range(item.address, item.address + item.width)
        value = item.value.to_bytes(item.width, layout.byte_order)
        assert set(words) <= offsets, item.key
        assert bytes(stock[offset] for offset in words) == value
        assert current.stock_image.data[item.address : item.address + item.width] == value


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


def changed_target(*, telemetry=False):
    """Return the JK08A target with a different current ignition adapter;
    ``telemetry`` also changes the current CAN telemetry capture unit."""
    current = target("JK08A")
    if telemetry:
        telemetry_payloads = dict(current.telemetry_payloads)
        capture = telemetry_payloads["capture"]
        telemetry_payloads["capture"] = bytes([capture[0] ^ 1]) + capture[1:]
        current = replace(current, telemetry_payloads=telemetry_payloads)
    payloads = dict(current.rolling_payloads)
    blob = payloads["ignition_adapter"]
    payloads["ignition_adapter"] = blob[:-1] + bytes([blob[-1] ^ 0x5A])
    return replace(current, rolling_payloads=payloads)


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


@pytest.mark.parametrize("telemetry", (False, True))
@pytest.mark.parametrize("key", FLASHED_ENDPOINTS)
def test_flashed_endpoint_survives_a_change_of_the_current_runtime(
    selected_target, key, telemetry
):
    changed = changed_target(telemetry=telemetry)
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
    changed = changed_target()
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


def test_current_runtime_refuses_each_leftover_fuel_path_part():
    """A current image holds no fuel-path part of a flashed endpoint: the
    current layout keeps the fuel units erased and restores the stock
    coordinator hook and DID slots."""
    current = target("JK08A")
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
    assert len(parts) == len(FUEL_PATH_UNITS | FUEL_PATH_HOOKS | FUEL_PATH_DIDS)
    clean = built_image()
    assert runtime_endpoints.classify_runtime(clean, current, "clean").rolling == "current"
    for start, end, payload in parts:
        leftover = bytearray(clean)
        leftover[start:end] = payload
        with pytest.raises(runtime_endpoints.EndpointError, match="partial or unknown"):
            runtime_endpoints.classify_runtime(closed(leftover), current, hex(start))


def test_current_runtime_keeps_retired_and_removed_spans_erased():
    current = target("JK08A")
    layout = current.rolling_layout
    for span in (*layout.retired_configuration_spans, *layout.erased_rom_ranges):
        source = bytearray(built_image())
        source[span.end - 1] = 0x00
        with pytest.raises(
            runtime_endpoints.EndpointError,
            match="partial or unknown Rolling Launch state",
        ):
            runtime_endpoints.classify_runtime(closed(source), current, span.key)


SCHEMA_5_SLOTS = (
    "0000" "00" "00" "03e8",
    "0002" "00" "00" "03e8",
    "0004" "00" "00" "03e8",
    "0002" "14" "78" "0338",
    "0000" "00" "00" "03e8",
)


# The CAN telemetry endpoint of both flashed images.
FLASHED_TELEMETRY = "schema2-profile9"
TELEMETRY_CHANGES = (
    "unit-span", "configuration-span", "hook-value", "hook-address", "protocol"
)


def changed_telemetry(change, monkeypatch):
    """Return ``changed_target()`` with one change of the current CAN
    telemetry: the control unit or the configuration record moved into the
    reserve, a hook word with a new value or at a new address, or a new
    configuration protocol."""
    current = changed_target()
    layout = current.telemetry_layout
    reserve = layout.reserved_rom
    if change == "unit-span":
        units = tuple(
            replace(unit, span=replace(
                unit.span, start=reserve.start, end=reserve.start + unit.span.size
            )) if unit.key == "control" else unit
            for unit in layout.assembly_units
        )
        layout = replace(
            layout,
            assembly_units=units,
            reserved_rom=replace(reserve, start=reserve.start + 0x200),
        )
    elif change == "configuration-span":
        size = layout.configuration.size
        layout = replace(
            layout,
            configuration=replace(
                layout.configuration, start=reserve.start, end=reserve.start + size
            ),
            reserved_rom=replace(reserve, start=reserve.start + size),
        )
    elif change == "hook-value":
        layout = replace(layout, hooks=tuple(
            replace(hook, replacement=hook.replacement + 4)
            if hook.key == "knock_margin_latch" else hook
            for hook in layout.hooks
        ))
    elif change == "hook-address":
        stock = current.stock_image.data
        moved = layout.hook_by_key["hcan1_recovery_init"]
        address = moved.address + 4
        assert not runtime_endpoints.historical_write_offsets("JK08A").intersection(
            range(address, address + moved.width)
        )
        moved = replace(moved, address=address, stock=int.from_bytes(
            stock[address : address + moved.width], layout.byte_order
        ))
        layout = replace(layout, hooks=tuple(
            moved if hook.key == moved.key else hook for hook in layout.hooks
        ))
    else:
        monkeypatch.setattr(can_telemetry, "CONFIG_VERSION", 3)
        monkeypatch.setattr(can_telemetry, "CONFIG_INTEGRITY", 0x54454C33)
    return replace(current, telemetry_layout=layout)


@pytest.mark.parametrize("change", TELEMETRY_CHANGES)
@pytest.mark.parametrize("key", FLASHED_ENDPOINTS)
def test_flashed_telemetry_survives_a_change_of_the_current_telemetry(
    selected_target, monkeypatch, key, change
):
    source = bytearray(endpoint_image(key))
    family = target("JK08A").map_layout.families[0]
    source[family.canonical_address] ^= 1
    source = closed(source)
    changed = changed_telemetry(change, monkeypatch)
    selected_target["JK08A"] = changed
    assert runtime_endpoints.classify_runtime(
        source, changed, "flashed"
    ) == runtime_endpoints.Classification(telemetry=FLASHED_TELEMETRY, rolling=key)
    extraction = extract_calibration.extract(source, rom="JK08A")
    states = dict(extraction.calibration.source)
    assert (states["rolling_launch"], states["can_telemetry"]) == (
        key, FLASHED_TELEMETRY
    )
    assert extraction.telemetry == build_rom.builtin_profile("JK08A").telemetry


@pytest.mark.parametrize("payload_changed", (False, True))
def test_hook_value_at_both_addresses_is_refused(monkeypatch, payload_changed):
    """With the current hook word moved, an image with the hook value at both
    addresses is refused: as the current endpoint with a leftover word of the
    historical endpoint, or, when the current payload differs, as the
    historical endpoint with a current word outside it."""
    changed = changed_telemetry("hook-address", monkeypatch)
    if payload_changed:
        payloads = dict(changed.telemetry_payloads)
        capture = payloads["capture"]
        payloads["capture"] = bytes([capture[0] ^ 1]) + capture[1:]
        changed = replace(changed, telemetry_payloads=payloads)
    hook = changed.telemetry_layout.hook_by_key["hcan1_recovery_init"]
    source = bytearray(endpoint_image("schema-5-fixed-trim"))
    source[hook.address : hook.address + hook.width] = hook.replacement.to_bytes(
        hook.width, "big"
    )
    with pytest.raises(
        runtime_endpoints.EndpointError, match="partial or unknown CAN telemetry state"
    ):
        runtime_endpoints.classify_runtime(closed(source), changed, "mixed")


def test_leftover_historical_telemetry_unit_is_refused(monkeypatch):
    """An image holds no byte of a historical telemetry endpoint outside the
    telemetry layer that it classifies as."""
    changed = changed_telemetry("unit-span", monkeypatch)
    key = "schema-5-fixed-trim"
    clean = endpoint_image(key, lower=True)
    assert runtime_endpoints.classify_runtime(
        clean, changed, "clean"
    ) == runtime_endpoints.Classification(telemetry="absent", rolling=key)
    control = next(
        unit for unit in can_telemetry_history.endpoint(FLASHED_TELEMETRY).units
        if unit.key == "control"
    )
    leftover = bytearray(clean)
    leftover[control.start : control.end] = control.payload
    with pytest.raises(
        runtime_endpoints.EndpointError, match="partial or unknown CAN telemetry state"
    ):
        runtime_endpoints.classify_runtime(closed(leftover), changed, "leftover")


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
def test_flashed_endpoint_reports_unexpressed_settings_and_calibration(key):
    """A historical hold has no implicit launch-RPM or threshold setting."""
    record = bytearray(endpoint_images.record(key))
    record[4] = 0x0E  # Maps 2 to 4 enabled.
    source = bytearray(endpoint_image(key, record=bytes(record)))
    family = target("JK08A").map_layout.families[0]
    source[family.copies[1] + 3] ^= 0x11
    source = closed(source)
    result = extract_calibration.extract(source)
    assert result.rolling is None and not result.has_profile
    ((component, endpoint_key, version, settings),) = result.unexpressed
    assert component == "rolling_launch" and endpoint_key == key
    assert version == runtime_endpoints.historical_endpoint(key).configuration_schema_version
    assert settings["enable_mask"] == 0x0E
    assert "launch_rpm_native" not in settings
    address = family.copies[1] + 3
    assert any(element.address <= address < element.end
               and element.data[address-element.address] == source[address]
               for element in result.calibration.elements)
