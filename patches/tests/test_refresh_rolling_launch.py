"""Editor slot changes derive efficiencies and survive calibration transfer."""

import pytest

from patches import apply_calibration, build_rom, extract_calibration, preflash
from patches import refresh_rolling_launch, rolling_launch, rom_checksums
from patches.tests.test_preflash import built, target, trimmed_map_4


@pytest.fixture(autouse=True, params=("JK08A",))
def rom(request):
    """Bind these exact-image cases to the preflash --rom selector."""
    return request.param


def editor_image(*, tuned_f=False):
    data = bytearray(built("JK08A"))
    start = target("JK08A").rolling_layout.configuration.start
    for index, trim in enumerate((0, 10, 20, 30, 40)):
        address = start + 0x28 + 6 * index
        data[address:address + 2] = (index + 1).to_bytes(2, "big")
        data[address + 2] = trim
        data[address + 3] = 110 + index
    if tuned_f:
        data[build_rom.TRIM_TABLE_ADDRESS + 7] = 46
    return bytes(rom_checksums.recalculate(data, target("JK08A").checksum_layout))


@pytest.mark.parametrize("tuned_f", (False, True))
def test_editor_slots_round_trip_and_qualify_with_image_efficiencies(tuned_f):
    edited = editor_image(tuned_f=tuned_f)
    with pytest.raises(preflash.PreflashError, match="refresh_rolling_launch.py"):
        preflash.check_image(edited, "JK08A")
    refreshed, report = refresh_rolling_launch.refresh(edited)
    assert report.runtime == "current"
    extraction = extract_calibration.extract(refreshed)
    assert [slot.integral_gain for slot in extraction.rolling.slots] == [1, 2, 3, 4, 5]
    assert [slot.max_trim for slot in extraction.rolling.slots] == [0, 10, 20, 30, 40]
    assert [slot.floor_command for slot in extraction.rolling.slots] == [110, 111, 112, 113, 114]
    assert extraction.rolling.slots[2].trim_efficiency == (820 if tuned_f else 824)
    profile = build_rom.parse_profile(extract_calibration.profile_bytes(extraction, "slots"), "slots")
    fresh = build_rom.build_image(target("JK08A").stock_image.data, profile=profile).data
    transferred = apply_calibration.apply(fresh, extraction.calibration)
    assert transferred.data == refreshed
    assert dict(transferred.settings)["rolling_launch"] == "matched"
    assert preflash.check_image(transferred.data, "JK08A").runtime == "current"
    allowed = rom_checksums.checksum_byte_offsets(target("JK08A").checksum_layout)
    start = target("JK08A").rolling_layout.configuration.start
    allowed |= {start + 0x28 + index * 6 + offset for index in range(5) for offset in (4, 5)}
    assert {i for i, (a, b) in enumerate(zip(edited, refreshed)) if a != b} <= allowed
    assert refresh_rolling_launch.refresh(refreshed)[0] == refreshed


def test_disabling_trim_repairs_the_zero_trim_invariant():
    data = bytearray(trimmed_map_4())
    address = target("JK08A").rolling_layout.configuration.start + 0x28 + 3 * 6
    data[address + 2] = 0
    with pytest.raises(preflash.PreflashError, match="refresh_rolling_launch.py"):
        preflash.check_image(rom_checksums.recalculate(data, target("JK08A").checksum_layout), "JK08A")
    result, _ = refresh_rolling_launch.refresh(data)
    assert int.from_bytes(result[address + 4:address + 6], "big") == 1000


@pytest.mark.parametrize("kind", ("payload", "gain", "trim", "sentinel"))
def test_refresh_refuses_unrelated_corruption_or_invalid_controls(kind):
    data = bytearray(editor_image())
    start = target("JK08A").rolling_layout.configuration.start
    if kind == "payload":
        data[0xD6000] ^= 1
    elif kind == "gain":
        data[start + 0x28] = 0x80
    elif kind == "trim":
        data[start + 0x28 + 2] = 41
    else:
        data[start] ^= 1
    with pytest.raises(refresh_rolling_launch.RefreshError):
        refresh_rolling_launch.refresh(data)


def test_refresh_cli_publishes_a_new_valid_image_and_never_replaces_input(tmp_path):
    source = tmp_path / "edited.bin"
    output = tmp_path / "ready.bin"
    data = editor_image()
    source.write_bytes(data)
    assert refresh_rolling_launch.main([str(source), "--output", str(output)]) == 0
    assert source.read_bytes() == data
    assert preflash.check_image(output.read_bytes(), "JK08A").runtime == "current"
    assert output.with_suffix(".bin.manifest.json").is_file()
    with pytest.raises(SystemExit):
        refresh_rolling_launch.main([str(source), "--output", str(source)])
