"""One map's calibration overwrites other maps and the image still rebuilds."""

import hashlib
import json

import pytest

from patches import copy_map_slot, preflash, rom_checksums
from patches.tests.test_preflash import built, target
from patches.tests.test_extract_runtime_states import previous_current_image


def slot(family, index):
    return range(*copy_map_slot.slot_range(family, index))


def distinct_maps(rom, families=None):
    """A built image whose maps differ in the first byte of each slot."""
    data = bytearray(built(rom))
    for family in target(rom).map_layout.families:
        if families is not None and family.key not in families:
            continue
        for index in range(1, target(rom).map_layout.slot_count + 1):
            data[family.slot_address(index - 1)] ^= index
    return bytes(rom_checksums.recalculate(data, target(rom).checksum_layout))


def changed(left, right):
    return {index for index, pair in enumerate(zip(left, right)) if pair[0] != pair[1]}


@pytest.mark.parametrize("rom", ("JK08A", "1ND0A"))
def test_every_map_takes_the_source_map(rom):
    layout = target(rom).map_layout
    source = distinct_maps(rom)
    data, report = copy_map_slot.copy_image(source, 3)
    assert report.rom == rom
    assert report.target_maps == (1, 2, 4, 5)
    assert report.families == tuple(family.key for family in layout.families)
    assert report.runtime == "current"
    for family in layout.families:
        tables = {bytes(data[item.start:item.stop]) for item in (
            slot(family, index) for index in range(1, 6)
        )}
        assert tables == {bytes(source[slot(family, 3).start:slot(family, 3).stop])}
    checksum = set(rom_checksums.checksum_byte_offsets(target(rom).checksum_layout))
    expected = {
        family.slot_address(index - 1)
        for family in layout.families
        for index in (1, 2, 4, 5)
    }
    assert changed(source, data) - checksum == expected
    assert report.changed_bytes == len(expected)
    rom_checksums.require_valid(data, target(rom).checksum_layout)
    assert preflash.check_image(data, rom).runtime == "current"
    assert copy_map_slot.copy_image(data, 3)[1].changed_bytes == 0


def test_selected_target_maps_leave_the_others():
    layout = target("JK08A").map_layout
    families = {layout.families[0].key, layout.families[-1].key}
    source = distinct_maps("JK08A", families)
    data, report = copy_map_slot.copy_image(source, 2, (5, 1))
    assert report.target_maps == (1, 5)
    assert report.families == tuple(
        family.key for family in layout.families if family.key in families
    )
    checksum = set(rom_checksums.checksum_byte_offsets(target("JK08A").checksum_layout))
    assert changed(source, data) - checksum == {
        layout.family_by_key[key].slot_address(index - 1)
        for key in families
        for index in (1, 5)
    }


def test_a_stock_build_copies_nothing():
    data, report = copy_map_slot.copy_image(built("JK08A"), 3)
    assert data == built("JK08A")
    assert report.families == ()
    assert report.changed_bytes == 0


@pytest.mark.parametrize(
    "source_map, maps, message",
    (
        (0, None, "source map 0 is not in 1..5"),
        (6, None, "source map 6 is not in 1..5"),
        (3, (), "no target map"),
        (3, (6,), "target map 6 is not in 1..5"),
        (3, (1, 1), "target maps repeat"),
        (3, (3, 4), "map 3 is both the source and a target"),
    ),
)
def test_map_selection_is_refused(source_map, maps, message):
    with pytest.raises(copy_map_slot.CopyError, match=message):
        copy_map_slot.copy_image(distinct_maps("JK08A"), source_map, maps)


def test_an_image_without_map_switching_is_refused():
    with pytest.raises(copy_map_slot.CopyError, match="Map Switching state 'absent'"):
        copy_map_slot.copy_image(target("JK08A").stock_image.data, 3)


def test_an_image_with_unexpressed_settings_is_refused():
    with pytest.raises(copy_map_slot.CopyError, match="cannot express"):
        copy_map_slot.copy_image(previous_current_image(), 3)


def test_a_change_outside_the_target_slots_is_refused(monkeypatch):
    layout = target("JK08A").map_layout
    copy = copy_map_slot.copy_slots
    outside = layout.families[0].slot_address(2)

    def leaking(data, layout, source_map, maps):
        data = bytearray(copy(data, layout, source_map, maps))
        data[outside] ^= 0xFF
        return bytes(data)

    monkeypatch.setattr(copy_map_slot, "copy_slots", leaking)
    with pytest.raises(copy_map_slot.CopyError, match=f"{outside:#x} lies outside"):
        copy_map_slot.copy_image(distinct_maps("JK08A"), 3, (5,))


def test_an_output_that_does_not_rebuild_is_refused(monkeypatch):
    rebuild = preflash._rebuild

    def differing(stock, target, extraction):
        data, runtime = rebuild(stock, target, extraction)
        return bytes([data[0] ^ 1]) + data[1:], runtime

    monkeypatch.setattr(preflash, "_rebuild", differing)
    with pytest.raises(copy_map_slot.CopyError, match="differs from its rebuild at 0x0"):
        copy_map_slot.copy_image(distinct_maps("JK08A"), 3)


def test_the_command_publishes_a_new_image(tmp_path, capsys):
    source = distinct_maps("JK08A")
    path = tmp_path / "input.bin"
    path.write_bytes(source)
    output = tmp_path / "copied.bin"
    assert copy_map_slot.main([str(path), "--source-map", "3", "--output", str(output)]) == 0
    data = output.read_bytes()
    assert data == copy_map_slot.copy_image(source, 3)[0]
    digest = hashlib.sha256(data).hexdigest()
    assert (tmp_path / "copied.bin.sha256").read_text() == f"{digest} *copied.bin\n"
    manifest = json.loads((tmp_path / "copied.bin.manifest.json").read_text())
    assert manifest["source_map"] == 3
    assert manifest["target_maps"] == [1, 2, 4, 5]
    assert manifest["changed_bytes"] == 4 * len(target("JK08A").map_layout.families)
    assert manifest["hardware_status"] == "UNTESTED"
    assert "status=PASS" in capsys.readouterr().out
    assert path.read_bytes() == source


def test_the_command_refuses_to_overwrite_its_input(tmp_path):
    path = tmp_path / "input.bin"
    path.write_bytes(distinct_maps("JK08A"))
    with pytest.raises(SystemExit):
        copy_map_slot.main([str(path), "--source-map", "3", "--output", str(path)])
    assert path.read_bytes() == distinct_maps("JK08A")
