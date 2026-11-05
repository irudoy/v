"""Editor changes keep the derived efficiency table and survive calibration transfer."""

import pytest

from patches import apply_calibration, build_rom, extract_calibration, preflash
from patches import refresh_rolling_launch, rolling_launch, rom_checksums
from patches.tests.test_preflash import built, target


SLOT_STRIDE = 12


@pytest.fixture(autouse=True, params=("JK08A",))
def rom(request):
    """Bind these exact-image cases to the preflash --rom selector."""
    return request.param


def slot_address(index):
    start = target("JK08A").rolling_layout.configuration.start
    return start + rolling_launch.SLOT_OFFSET + SLOT_STRIDE * index


def efficiency(data):
    span = target("JK08A").rolling_layout.efficiency
    return rolling_launch.EfficiencyTable.from_bytes(bytes(data[span.start:span.end]))


def editor_image(*, tuned_f=False):
    """Edit the slot fields that the editors expose and, optionally, F."""
    data = bytearray(built("JK08A"))
    for index, trim in enumerate((0, 10, 20, 30, 40)):
        address = slot_address(index)
        data[address:address + 2] = (index + 1).to_bytes(2, "big")
        data[address + 2] = trim
        data[address + 3] = 40 - trim
        data[address + 4] = 110 + index
        data[address + 6:address + 8] = (400 + 8 * index).to_bytes(2, "big")
        data[address + 8:address + 10] = (50 + index).to_bytes(2, "big")
        data[address + 10:address + 12] = (16 * index).to_bytes(2, "big")
    if tuned_f:
        # The F point of a trim of 20 APC counts.
        data[build_rom.TRIM_TABLE_ADDRESS + 7] = 46
    return bytes(rom_checksums.recalculate(data, target("JK08A").checksum_layout))


@pytest.mark.parametrize("tuned_f", (False, True))
def test_editor_slots_round_trip_and_qualify_with_image_efficiencies(tuned_f):
    edited = editor_image(tuned_f=tuned_f)
    if tuned_f:
        with pytest.raises(preflash.PreflashError, match="refresh_rolling_launch.py"):
            preflash.check_image(edited, "JK08A")
    else:
        # Slot settings do not enter the table; only F does.
        assert preflash.check_image(edited, "JK08A").runtime == "current"
    refreshed, report = refresh_rolling_launch.refresh(edited)
    assert report.runtime == "current"
    assert efficiency(refreshed).at(20) == (820 if tuned_f else 824)
    assert efficiency(refreshed) == build_rom.efficiency_table(refreshed)
    extraction = extract_calibration.extract(refreshed)
    slots = extraction.rolling.slots
    assert [slot.integral_gain for slot in slots] == [1, 2, 3, 4, 5]
    assert [slot.max_trim_rpm for slot in slots] == [0, 10, 20, 30, 40]
    assert [slot.max_trim_speed for slot in slots] == [40, 30, 20, 10, 0]
    assert [slot.floor_command for slot in slots] == [110, 111, 112, 113, 114]
    assert [slot.launch_rpm_native for slot in slots] == [400, 408, 416, 424, 432]
    assert [slot.launch_speed_threshold for slot in slots] == [50, 51, 52, 53, 54]
    assert [slot.launch_soft_width_native for slot in slots] == [0, 16, 32, 48, 64]
    profile = build_rom.parse_profile(extract_calibration.profile_bytes(extraction, "slots"), "slots")
    fresh = build_rom.build_image(target("JK08A").stock_image.data, profile=profile).data
    transferred = apply_calibration.apply(fresh, extraction.calibration)
    assert transferred.data == refreshed
    assert dict(transferred.settings)["rolling_launch"] == "matched"
    assert preflash.check_image(transferred.data, "JK08A").runtime == "current"
    allowed = rom_checksums.checksum_byte_offsets(target("JK08A").checksum_layout)
    span = target("JK08A").rolling_layout.efficiency
    allowed |= set(range(span.start, span.end))
    assert {i for i, (a, b) in enumerate(zip(edited, refreshed)) if a != b} <= allowed
    assert refresh_rolling_launch.refresh(refreshed)[0] == refreshed


@pytest.mark.parametrize("word", (0, 20, 40))
def test_refresh_rewrites_every_word_of_a_stale_table(word):
    data = bytearray(editor_image())
    span = target("JK08A").rolling_layout.efficiency
    data[span.start + 2 * word:span.start + 2 * word + 2] = (999).to_bytes(2, "big")
    stale = bytes(rom_checksums.recalculate(data, target("JK08A").checksum_layout))
    with pytest.raises(preflash.PreflashError, match="refresh_rolling_launch.py"):
        preflash.check_image(stale, "JK08A")
    result, _ = refresh_rolling_launch.refresh(stale)
    assert efficiency(result) == build_rom.efficiency_table(result)
    assert result == editor_image()


@pytest.mark.parametrize(
    "kind", ("payload", "gain", "trim", "floor", "sentinel", "schema")
)
def test_refresh_refuses_unrelated_corruption_or_invalid_controls(kind):
    data = bytearray(editor_image())
    start = target("JK08A").rolling_layout.configuration.start
    if kind == "payload":
        data[0xD6000] ^= 1
    elif kind == "gain":
        data[slot_address(0)] = 0x80
    elif kind == "trim":
        data[slot_address(0) + 3] = 41
    elif kind == "floor":
        data[slot_address(0) + 4] = 121
    elif kind == "sentinel":
        data[start] ^= 1
    else:
        data[start + 2] = 5
    with pytest.raises(refresh_rolling_launch.RefreshError) as error:
        refresh_rolling_launch.refresh(data)
    if kind in ("gain", "trim", "floor", "sentinel", "schema"):
        assert "refresh normalizes current images only" in str(error.value)


def test_refresh_cli_publishes_a_new_valid_image_and_never_replaces_input(tmp_path):
    source = tmp_path / "edited.bin"
    output = tmp_path / "ready.bin"
    data = editor_image(tuned_f=True)
    source.write_bytes(data)
    assert refresh_rolling_launch.main([str(source), "--output", str(output)]) == 0
    assert source.read_bytes() == data
    assert preflash.check_image(output.read_bytes(), "JK08A").runtime == "current"
    assert output.with_suffix(".bin.manifest.json").is_file()
    with pytest.raises(SystemExit):
        refresh_rolling_launch.main([str(source), "--output", str(source)])
