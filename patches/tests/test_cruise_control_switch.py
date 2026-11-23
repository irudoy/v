"""Gates for the Cruise Control Switch of patches/cruise-control-switch.md.

The steering switch decoders run in the SH-2 interpreter of
tools/mapkit/sh2_interpreter.py on the stock images and on copies that differ
only in the configuration byte, a selector byte, or ROM8[0x8A23]. Cells outside
the image read zero until a seed or a store sets them, and each pass seeds the
input word of the decoder. The static checks bind the switch tables below to
the images, the editor definitions, the mailbox tables, the DTC group bytes,
the monitor instructions, and the calibration transfer of the ROM builder.
"""

from __future__ import annotations

import csv
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from kb import match
from patches import apply_calibration, build_rom, extract_calibration, rom_checksums
from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import RETURN, STACK_TOP, Sh2, sext, u16


ROOT = Path(__file__).resolve().parents[2]
HOMOLOGY_PATH = ROOT / "rom-images/homology.toml"
OVERRIDES_PATH = ROOT / "defs/JK08A.overrides.toml"
BINDINGS_PATH = ROOT / "defs/JK08A.diagnostic-bindings.csv"
NAME = "Cruise Control Switch"
NOT_INSTALLED = "Not Installed"
ICC = "ICC Switch (5 Buttons)"
OUTSIDE = 0x80
STEPS = 200000
# Stores of a decoder that returns before the decode stay in its stack frame.
FRAME = 0x200

# Layouts without the switch: image, configuration byte.
WITHOUT_SWITCH = {"jk78c": ("JK78C", 0x894F), "1me3b": ("1ME3B", 0x8A62)}
# The selector byte of the second ICC ladder per image.
SELECTORS = {
    "JK00C": 0x8B64, "JK00D": 0x8B65, "1ND0A": 0x8A1D, "1ND3B": 0x8A1D,
    "1ME3B": 0x8A6E, "1EK7A": 0x8AE6,
}
# Count 400 lies between the CANCEL and DISTANCE windows of the first ladder and
# in the CANCEL window of the second ladder.
SECOND_LADDER_CANCEL = 400
FIRST_LADDERS = {"JK08A": 0x24C08, "1EK7A": 0x26BD0}
RETURN_GATES = {"1ND0A": (0x8A23, 0x0012B424), "1ND3B": (0x8A23, 0x0012B424),
                "1EK7A": (0x8AEC, 0x0015A0D4)}
# Mailbox table per layout and the ICC records of JK08A: identifier, type, DLC.
MAILBOXES = {"7mfk": (0x975A, 32), "jk00c": (0x9822, 32), "jk00d": (0x9832, 32),
             "1nd": (0x975C, 32), "1ek7a": (0x9944, 36)}
ICC_RECORDS = {0x975A: (0x239, 3, 5), 0x975E: (0x2B0, 1, 8), 0x979A: (0x1A5, 1, 5)}
COMMON_FRAMES = {0x551, 0x580, 0x6E2}
# DTC group enable table per layout and the byte of the steering switch group.
GROUP_TABLES = {"7mfk": 0x186C8, "jk00c": 0x1B638, "jk00d": 0x1B658, "1nd": 0x1AEDC,
                "1ek7a": 0x1B9E0}
GROUP_BYTE = 0x28
# Monitor entry, literal load of the configuration byte, literal load of the
# group table.
MONITORS = {
    "7mfk": (0x000913D0, 0x000913DC, 0x00091410),
    "jk00c": (0x0009608C, 0x00096098, 0x000960CC),
    "jk00d": (0x00096078, 0x00096084, 0x000960B8),
    "1nd": (0x000D1CBC, 0x000D1CC4, 0x000D1CE8),
    "1ek7a": (0x000E6828, 0x000E6830, 0x000E6854),
}
BUILDS = ("JK00A", "1ND0A", "1EK7A")


# Configuration byte per switch state.
STATES = {NOT_INSTALLED: 0x00, ICC: 0x2B}
# Images with the switch: image, layout, configuration byte, stock byte, stock state.
SITES = [
    ("JK08A", "7mfk", 0x8B28, 0x2B, ICC),
    ("JK00A", "7mfk", 0x8B28, 0x00, NOT_INSTALLED),
    ("JK03A", "7mfk", 0x8B28, 0x00, NOT_INSTALLED),
    ("JK03B", "7mfk", 0x8B28, 0x00, NOT_INSTALLED),
    ("JK00C", "jk00c", 0x8B59, 0x00, NOT_INSTALLED),
    ("JK00D", "jk00d", 0x8B5A, 0x00, NOT_INSTALLED),
    ("1ND0A", "1nd", 0x8A11, 0x00, NOT_INSTALLED),
    ("1ND3B", "1nd", 0x8A11, 0x00, NOT_INSTALLED),
    ("1EK7A", "1ek7a", 0x8AD9, 0x00, NOT_INSTALLED),
]
# Steering switch decoder per layout: entry, input word, code, accepted code.
DECODERS = {
    "7mfk": (0x000D185C, 0xFFFF3630, 0xFFFF36D9, 0xFFFF36D8),
    "jk00c": (0x000DD6F4, 0xFFFF3728, 0xFFFF37E5, 0xFFFF37E4),
    "jk00d": (0x000DDE30, 0xFFFF373C, 0xFFFF37F9, 0xFFFF37F8),
    "1nd": (0x0012B270, 0xFFFEAAC0, 0xFFFEAB76, 0xFFFEAB74),
    "jk78c": (0x000FE2B8, 0xFFFF3854, 0xFFFF3909, 0xFFFF3908),
    "1me3b": (0x001386A4, 0xFFFEAC00, 0xFFFEACBC, 0xFFFEACBA),
    "1ek7a": (0x00159F20, 0xFFFEAF30, 0xFFFEAFEE, 0xFFFEAFEC),
}
# Window of the first ladder in A/D counts and the code of each button.
WINDOWS = [
    ("MAIN", 0, 108, 0x01),
    ("CANCEL", 224, 317, 0x02),
    ("DISTANCE", 416, 489, 0x04),
    ("SET/COAST", 578, 636, 0x08),
    ("RESUME/ACCELERATE", 720, 764, 0x10),
    ("all released", 850, 883, 0x20),
    ("open input", 940, 65535, 0x40),
]
IMAGES = [site[0] for site in SITES]


def _layouts() -> dict[str, str]:
    families = tomllib.loads(HOMOLOGY_PATH.read_text(encoding="utf-8"))["family"]
    layouts = {}
    for family in families.values():
        for layout, image in family.get("layouts", {}).items():
            layouts[image] = layout
        if family.get("same_address_inheritance"):
            (layout,) = family["layouts"]
            for member in family["members"]:
                layouts.setdefault(member, layout)
    return layouts


def _site(image: str) -> tuple[str, str, int, int, str]:
    (site,) = [site for site in SITES if site[0] == image]
    return site


def _patched(data: bytes, changes: dict[int, int]) -> bytes:
    patched = bytearray(data)
    for address, value in changes.items():
        patched[address] = value
    return bytes(patched)


def _image(image: str, state: str | None = None) -> bytes:
    data = romkit.load(image).data
    if state is None:
        return data
    return _patched(data, {_site(image)[2]: STATES[state]})


class Decoder:
    """Consecutive passes of one decoder over one machine state."""

    def __init__(self, data: bytes, layout: str) -> None:
        self.machine = Sh2(data, unset=0)
        self.entry, self.word, self.code, self.accepted = DECODERS[layout]

    def run(self, level: int) -> Sh2:
        machine = self.machine
        machine.r = [0] * 16
        machine.r[15] = STACK_TOP
        machine.loads.clear()
        machine.stores.clear()
        machine.seed_word(self.word, level)
        machine.call(self.entry, STEPS)
        return machine

    def code_of(self, level: int) -> int | None:
        return self.run(level).ram.get(self.code)


def _outside_frame(machine: Sh2) -> list[tuple[int, int]]:
    return [(pc, at) for pc, at, _, _ in machine.stores if not STACK_TOP - FRAME <= at < STACK_TOP]


def _level(button: str) -> int:
    (low,) = [low for name, low, _, _ in WINDOWS if name == button]
    return low


def _code(button: str) -> int:
    (code,) = [code for name, _, _, code in WINDOWS if name == button]
    return code


def test_sites_hold_the_stated_stock_bytes() -> None:
    layouts = _layouts()
    assert set(STATES) == {NOT_INSTALLED, ICC}
    assert {site[4] for site in SITES} == set(STATES)
    for image, layout, byte, stock, state in SITES:
        assert layouts[image] == layout, image
        assert layout in DECODERS, image
        assert romkit.load(image).data[byte] == stock == STATES[state], image
    assert not set(WITHOUT_SWITCH) & {site[1] for site in SITES}
    for layout, (image, byte) in WITHOUT_SWITCH.items():
        assert layouts[image] == layout
        value = romkit.load(image).data[byte]
        assert value & 0x01, image


@pytest.mark.parametrize("image", IMAGES)
def test_not_installed_stores_nothing_outside_the_stack_frame(image: str) -> None:
    layout = _site(image)[1]
    decoder = Decoder(_image(image, NOT_INSTALLED), layout)
    for _, low, high, _ in WINDOWS:
        for level in (low, high):
            machine = decoder.run(level)
            assert machine.stores or machine.loads, (image, level)
            assert not _outside_frame(machine), (image, level)


@pytest.mark.parametrize("image", IMAGES)
def test_icc_switch_decodes_every_window_at_both_bounds(image: str) -> None:
    layout = _site(image)[1]
    decoder = Decoder(_image(image, ICC), layout)
    for button, low, high, code in WINDOWS:
        assert decoder.code_of(low) == code, (image, button, low)
        assert decoder.code_of(high) == code, (image, button, high)
        if low > 0:
            assert decoder.code_of(low - 1) == OUTSIDE, (image, button, low - 1)
        if high < 0xFFFF:
            assert decoder.code_of(high + 1) == OUTSIDE, (image, button, high + 1)


@pytest.mark.parametrize("image", IMAGES)
def test_icc_switch_accepts_a_code_that_two_passes_give(image: str) -> None:
    layout = _site(image)[1]
    decoder = Decoder(_image(image, ICC), layout)
    sequence = (
        ("MAIN", "MAIN"),
        ("MAIN", "MAIN"),
        ("CANCEL", "MAIN"),
        ("CANCEL", "CANCEL"),
        ("SET/COAST", "CANCEL"),
        ("all released", "CANCEL"),
        ("SET/COAST", "CANCEL"),
        ("SET/COAST", "SET/COAST"),
        ("RESUME/ACCELERATE", "SET/COAST"),
        ("all released", "SET/COAST"),
        ("all released", "all released"),
    )
    for index, (button, accepted) in enumerate(sequence):
        machine = decoder.run(_level(button))
        assert machine.ram[decoder.code] == _code(button), (image, index)
        assert machine.ram[decoder.accepted] == _code(accepted), (image, index)


@pytest.mark.parametrize("image", RETURN_GATES)
def test_decoder_returns_only_while_the_second_gate_bit_is_clear(image: str) -> None:
    gate, past_decode = RETURN_GATES[image]
    data = _image(image, NOT_INSTALLED)
    assert not data[gate] & 0x01
    decoder = Decoder(_patched(data, {gate: data[gate] | 0x01}), _site(image)[1])
    machine = decoder.machine
    machine.seed_word(decoder.word, _level("CANCEL"))
    machine.pr = RETURN
    assert machine.run(decoder.entry, (past_decode, RETURN), STEPS) == past_decode
    assert not machine.stored(decoder.code)


@pytest.mark.parametrize("layout", sorted(WITHOUT_SWITCH))
def test_layouts_without_the_switch_decode_in_stock_form(layout: str) -> None:
    image, byte = WITHOUT_SWITCH[layout]
    data = romkit.load(image).data
    decoder = Decoder(data, layout)
    machine = decoder.run(_level("MAIN"))
    assert decoder.code in machine.written() and decoder.accepted in machine.written(), image
    cleared = Decoder(_patched(data, {byte: data[byte] & 0xFE}), layout).run(_level("MAIN"))
    assert not _outside_frame(cleared), image


@pytest.mark.parametrize("image", sorted(SELECTORS))
def test_selector_bit_0_takes_the_second_icc_ladder(image: str) -> None:
    layouts = _layouts()
    layout = layouts[image]
    if image in IMAGES:
        data = _image(image, ICC)
        assert data[SELECTORS[image]] == 0x00, image
    else:
        data = romkit.load(image).data
        assert data[SELECTORS[image]] == 0x0F, image
    first = _patched(data, {SELECTORS[image]: data[SELECTORS[image]] & 0xFE})
    second = _patched(data, {SELECTORS[image]: data[SELECTORS[image]] | 0x01})
    assert Decoder(first, layout).code_of(SECOND_LADDER_CANCEL) == OUTSIDE, image
    assert Decoder(first, layout).code_of(_level("CANCEL")) == _code("CANCEL"), image
    assert Decoder(second, layout).code_of(SECOND_LADDER_CANCEL) == _code("CANCEL"), image


@pytest.mark.parametrize("image,site", FIRST_LADDERS.items())
def test_first_icc_ladder_is_the_jk08a_ladder(image: str, site: int) -> None:
    data = romkit.load(image).data
    ladder = [u16(data, site + 2 * index) for index in range(2 * len(WINDOWS))]
    assert ladder == [bound for _, low, high, _ in WINDOWS for bound in (low, high)]


def _records(data: bytes, base: int, count: int):
    for index in range(count):
        at = base + 4 * index
        yield at, data[at], data[at + 1], u16(data, at + 2) >> 5


def test_images_with_the_switch_configure_no_icc_mailbox() -> None:
    jk08a = {at: (identifier, kind, length)
             for at, kind, length, identifier in _records(romkit.load("JK08A").data, *MAILBOXES["7mfk"])}
    for at, record in ICC_RECORDS.items():
        assert jk08a[at] == record, hex(at)
    icc = {identifier for identifier, _, _ in ICC_RECORDS.values()}
    for image, layout, _, _, _ in SITES:
        if image == "JK08A":
            continue
        records = list(_records(romkit.load(image).data, *MAILBOXES[layout]))
        identifiers = {identifier for _, _, _, identifier in records}
        assert COMMON_FRAMES <= identifiers, image
        assert not icc & identifiers, image
        if layout == "7mfk":
            by_address = {at: (kind, identifier) for at, kind, _, identifier in records}
            assert all(by_address[at] == (5, 0) for at in ICC_RECORDS), image


def _literal(data: bytes, pc: int) -> tuple[int, int]:
    word = u16(data, pc)
    assert word >> 12 == 0xD, hex(pc)
    at = (pc & ~3) + 4 + (word & 0xFF) * 4
    return (word >> 8) & 0xF, int.from_bytes(data[at:at + 4], "big")


def _branch(pc: int, word: int) -> int:
    if word >> 12 == 0xA:
        return pc + 4 + 2 * sext(word & 0xFFF, 12)
    return pc + 4 + 2 * sext(word & 0xFF, 8)


def _shape(word: int) -> int:
    """The opcode and registers of an instruction without its displacement or immediate."""
    top, group = word >> 12, (word >> 8) & 0xF
    if top in (0xA, 0xB):
        return word & 0xF000
    if top in (0x9, 0xD, 0xE) or (top == 0x8 and group in (0x9, 0xB, 0xD, 0xF)):
        return word & 0xFF00
    return word


def _exit(data: bytes, pc: int) -> int:
    """The exit of the bit 0 test that follows the load of the configuration byte."""
    words = [u16(data, pc + 2 * index) for index in range(5)]
    if words[0] == 0xC801 and words[1] >> 8 == 0x89:
        return _branch(pc + 2, words[1])
    assert words[0] == 0xC901 and words[1] == 0x2008 and words[2] >> 8 == 0x8F, hex(pc)
    assert words[4] >> 12 == 0xA, hex(pc)
    return _branch(pc + 8, words[4])


@pytest.mark.slow
def test_dtc_group_byte_and_the_monitors_that_read_it() -> None:
    layouts = {site[1]: site for site in SITES}
    for image, layout, _, _, _ in SITES:
        value = romkit.load(image).data[GROUP_TABLES[layout] + GROUP_BYTE]
        assert value == (0x7F if image == "JK08A" else 0x00), image
    for layout, (entry, configuration, group) in MONITORS.items():
        image, _, byte, _, _ = layouts[layout]
        data = romkit.load(image).data
        owner = match.code(layout).owner
        assert owner[configuration] == owner[group] == entry, layout
        register, value = _literal(data, configuration)
        assert value == byte, layout
        assert u16(data, configuration + 2) == 0x6000 | register << 4, layout
        assert _exit(data, configuration + 4) > group + 4, layout
        register, value = _literal(data, group)
        assert value == GROUP_TABLES[layout], layout
        assert u16(data, group + 2) == 0xE000 | GROUP_BYTE, layout
        assert u16(data, group + 4) == 0x000C | register << 4, layout
    source = romkit.load("JK08A").data
    entry, _, group = MONITORS["7mfk"]
    shapes = [_shape(u16(source, pc)) for pc in range(entry, group + 6, 2)]
    for layout in ("jk00c", "jk00d"):
        image = layouts[layout][0]
        data = romkit.load(image).data
        start, _, end = MONITORS[layout]
        assert [_shape(u16(data, pc)) for pc in range(start, end + 6, 2)] == shapes, layout
    with BINDINGS_PATH.open(encoding="utf-8", newline="") as source_file:
        rows = [row for row in csv.reader(source_file) if f"{entry:08x}" in row]
    assert any("P1564" in row for row in rows)


def _xml_switches(image: str) -> list[ET.Element]:
    root = ET.parse(ROOT / f"defs/{image}.xml").getroot()
    return [table for table in root.iter("table") if table.get("name") == NAME]


def _xdf_patches(image: str) -> list[ET.Element]:
    root = ET.parse(ROOT / f"defs/{image}.xdf").getroot()
    return [patch for patch in root.iter("XDFPATCH") if patch.findtext("title") == NAME]


def test_definitions_list_the_stock_state_first() -> None:
    overrides = tomllib.loads(OVERRIDES_PATH.read_text(encoding="utf-8"))
    (entry,) = [switch for switch in overrides["switch"] if switch["name"] == NAME]
    assert int(entry["storageaddress"], 16) == _site("JK08A")[2]
    assert {state["name"]: int(state["data"], 16) for state in entry["state"]} == STATES
    for image, _, byte, stock, state in SITES:
        (other,) = [name for name in STATES if name != state]
        (table,) = _xml_switches(image)
        assert table.get("type") == "Switch", image
        assert int(table.get("storageaddress"), 16) == byte, image
        states = [(item.get("name"), int(item.get("data"), 16)) for item in table.iter("state")]
        assert states == [(state, stock), (other, STATES[other])], image
        assert table.findtext("description").startswith(f"Exact {image} only."), image
        (patch,) = _xdf_patches(image)
        (patch_entry,) = patch.findall("XDFPATCHENTRY")
        assert int(patch_entry.get("address"), 16) == byte, image
        assert int(patch_entry.get("basedata"), 16) == stock, image
        assert int(patch_entry.get("patchdata"), 16) == STATES[other], image
    for image, _ in WITHOUT_SWITCH.values():
        assert not _xml_switches(image) and not _xdf_patches(image), image


@pytest.mark.parametrize("image", BUILDS)
def test_calibration_transfer_carries_the_configuration_byte(image: str) -> None:
    byte = _site(image)[2]
    layout = rom_checksums.layout_for_rom(image, for_build=True)
    data = bytes(rom_checksums.recalculate(_image(image, ICC), layout))
    calibration = extract_calibration.extract(data, source_name=f"{image} with {ICC}").calibration
    assert [(item.address, item.data) for item in calibration.elements] == [
        (byte, bytes((STATES[ICC],)))
    ]
    build = build_rom.build_image(_image(image), source_name=f"{image} stock")
    result = apply_calibration.apply(build.data, calibration)
    assert result.rom == image
    assert result.data[byte] == STATES[ICC]
    assert rom_checksums.verify(result.data, layout).valid


