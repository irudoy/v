"""Calibration ranges partition the builder window on every registered ROM."""

from functools import lru_cache
from pathlib import Path
import tomllib

import pytest

from patches import calibration_ranges
from patches import map_switching_layout
from patches import runtime_targets
from tools.mapkit import rom as romkit


ROOT = Path(__file__).resolve().parents[2]
TELEMETRY_STARTUP_SWITCHES = frozenset(
    ("CAN Telemetry at Startup", "can_telemetry_startup")
)


@lru_cache(maxsize=None)
def target(rom):
    return runtime_targets.load_runtime_target(rom)


def offsets(ranges):
    return {offset for item in ranges for offset in range(item.start, item.end)}


def definition_switches(rom):
    """Return {name: address} of the editor switches of ``rom``."""
    if rom in runtime_targets.EXACT_ROMS:
        with (ROOT / "defs/JK08A.overrides.toml").open("rb") as source:
            raw = tomllib.load(source)
        return {
            item["name"]: int(item["storageaddress"], 16)
            for item in raw["switch"]
        }
    with (ROOT / "defs/definition-projections.toml").open("rb") as source:
        raw = tomllib.load(source)
    return dict(raw["projection"][rom]["switch"])


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_ranges_are_ordered_disjoint_and_builder_owned_elsewhere(rom):
    ranges = calibration_ranges.load(rom)
    ordered = ranges.ranges
    assert all(left.end <= right.start for left, right in zip(ordered, ordered[1:]))
    for item in ranges.window:
        assert calibration_ranges.WINDOW_START <= item.start
        assert item.end <= calibration_ranges.WINDOW_END
    window = offsets(ranges.window)
    assert window.isdisjoint(ranges.write_offsets)
    assert window.isdisjoint(ranges.checksum_offsets)
    assert window.isdisjoint(calibration_ranges.stock_pinned_offsets(target(rom)))
    copies = offsets(ranges.map_copies)
    assert copies <= ranges.write_offsets
    assert copies.isdisjoint(ranges.checksum_offsets)


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_every_alternate_map_slot_is_a_calibration_range(rom):
    layout = target(rom).map_layout
    keys = {item.key for item in calibration_ranges.load(rom).map_copies}
    assert keys == {
        f"{family.key}.map_{slot}"
        for family in layout.families
        for slot in range(2, layout.slot_count + 1)
    }


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_map_1_tables_lie_inside_the_window_ranges(rom):
    ranges = calibration_ranges.load(rom)
    window = offsets(ranges.window)
    for family in target(rom).map_layout.families:
        table = range(
            family.canonical_address,
            family.canonical_address + family.byte_length,
        )
        assert window.issuperset(table), family.key


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_editor_switches_are_calibration_or_profile_settings(rom):
    ranges = calibration_ranges.load(rom)
    switches = definition_switches(rom)
    assert switches
    for name, address in switches.items():
        if name in TELEMETRY_STARTUP_SWITCHES:
            assert address in ranges.write_offsets, name
        else:
            assert ranges.containing(address) is not None, name


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_compatible_image_contract_accepts_every_window_range(rom):
    stock = target(rom).stock_image
    data = bytearray(stock.data)
    for item in calibration_ranges.load(rom).window:
        for offset in range(item.start, item.end):
            data[offset] ^= 0xFF
    map_switching_layout.validate_compatible_image(
        target(rom).map_layout, romkit.Image(rom, "inverted", bytes(data)), stock
    )


@pytest.mark.parametrize("rom", runtime_targets.SUPPORTED_ROMS)
def test_compatible_image_contract_rejects_pinned_window_bytes(rom):
    stock = target(rom).stock_image
    ranges = calibration_ranges.load(rom)
    pinned = sorted(
        offset
        for offset in calibration_ranges.stock_pinned_offsets(target(rom))
        if calibration_ranges.WINDOW_START <= offset < calibration_ranges.WINDOW_END
        and offset not in ranges.write_offsets
    )
    assert pinned
    # The first and last byte of each pinned run bound the excluded spans.
    boundaries = {
        offset
        for index, offset in enumerate(pinned)
        if index in (0, len(pinned) - 1)
        or pinned[index - 1] != offset - 1
        or pinned[index + 1] != offset + 1
    }
    for offset in sorted(boundaries):
        data = bytearray(stock.data)
        data[offset] ^= 0xFF
        with pytest.raises(ValueError):
            map_switching_layout.validate_compatible_image(
                target(rom).map_layout,
                romkit.Image(rom, f"pinned {offset:#x}", bytes(data)),
                stock,
            )


def test_containing_returns_the_range_or_none():
    ranges = calibration_ranges.load("JK08A")
    first = ranges.ranges[0]
    assert ranges.containing(first.start) == first
    assert ranges.containing(first.end - 1) == first
    assert ranges.containing(map_switching_layout.COMPATIBLE_IDENTITY_START) is None
    assert ranges.containing(calibration_ranges.WINDOW_END) is None


@pytest.mark.parametrize("rom", runtime_targets.EXACT_ROMS)
def test_the_efficiency_table_is_a_builder_write_and_not_calibration(rom):
    layout = target(rom).rolling_layout
    ranges = calibration_ranges.load(rom)
    table = set(range(layout.efficiency.start, layout.efficiency.end))
    assert table <= ranges.write_offsets
    assert table.isdisjoint(ranges.offsets())
    assert ranges.containing(layout.efficiency.start) is None
