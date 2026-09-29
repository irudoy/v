"""Gates for the Cruise Control Switch of patches/cruise-control-switch.md.

The steering switch decoders run in the SH-2 interpreter of
tools/mapkit/sh2_interpreter.py on the stock images and on copies that differ
only in the configuration byte, a selector byte, or ROM8[0x8A23]. Cells outside
the image read zero until a seed or a store sets them, and each pass seeds the
input word of the decoder. The static checks bind the tables of the
specification to the images, the editor definitions, the mailbox tables, the
DTC group bytes, the monitor instructions, the factory manual, the ROM builder,
and the documents that cite the switch.
"""

from __future__ import annotations

import csv
import json
import re
import tomllib
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

from kb import match
from patches import build_rom, rom_checksums
from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import RETURN, STACK_TOP, Sh2, sext, u16


ROOT = Path(__file__).resolve().parents[2]
SPEC_PATH = ROOT / "patches/cruise-control-switch.md"
HOMOLOGY_PATH = ROOT / "rom-images/homology.toml"
OVERRIDES_PATH = ROOT / "defs/JK08A.overrides.toml"
BINDINGS_PATH = ROOT / "defs/JK08A.diagnostic-bindings.csv"
FRAGMENTS_PATH = ROOT / "refs/diagnostics/nissan-esm-2007-g35-sedan/fragments.jsonl"
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
SELECTORS = {"JK00C": 0x8B64, "JK00D": 0x8B65, "1ND0A": 0x8A1D, "1ND3B": 0x8A1D, "1ME3B": 0x8A6E}
# Count 400 lies between the CANCEL and DISTANCE windows of the first ladder and
# in the CANCEL window of the second ladder.
SECOND_LADDER_CANCEL = 400
FIRST_LADDER = 0x24C08
ND_RETURN_GATE = 0x8A23
ND_PAST_DECODE = 0x0012B424
# Mailbox table per layout and the ICC records of JK08A: identifier, type, DLC.
MAILBOXES = {"7mfk": 0x975A, "jk00c": 0x9822, "jk00d": 0x9832, "1nd": 0x975C}
MAILBOX_RECORDS = 32
ICC_RECORDS = {0x975A: (0x239, 3, 5), 0x975E: (0x2B0, 1, 8), 0x979A: (0x1A5, 1, 5)}
COMMON_FRAMES = {0x551, 0x580, 0x6E2}
# DTC group enable table per layout and the byte of the steering switch group.
GROUP_TABLES = {"7mfk": 0x186C8, "jk00c": 0x1B638, "jk00d": 0x1B658, "1nd": 0x1AEDC}
GROUP_BYTE = 0x28
# Monitor entry, literal load of the configuration byte, literal load of the
# group table.
MONITORS = {
    "7mfk": (0x000913D0, 0x000913DC, 0x00091410),
    "jk00c": (0x0009608C, 0x00096098, 0x000960CC),
    "jk00d": (0x00096078, 0x00096084, 0x000960B8),
    "1nd": (0x000D1CBC, 0x000D1CC4, 0x000D1CE8),
}
BUILDS = ("JK00A", "1ND0A")


def _doc() -> str:
    return SPEC_PATH.read_text(encoding="utf-8")


def _flat(text: str) -> str:
    return " ".join(text.split())


def _table(header: str) -> list[list[str]]:
    lines = _doc().splitlines()
    start = lines.index(header)
    rows = []
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        rows.append([cell.strip().strip("`") for cell in line.strip().strip("|").split("|")])
    return rows


STATES = {name: int(byte, 16) for name, byte, _ in _table("| State | Byte | Decoder |")}
SITES = [
    (image, layout, int(byte, 16), int(stock, 16), state)
    for image, layout, byte, stock, state in _table("| Image | Layout | Byte | Stock | Stock state |")
]
DECODERS = {
    layout: tuple(int(cell, 16) for cell in cells)
    for layout, *cells in _table("| Layout | Decoder | Input word | Code | Accepted code |")
}
WINDOWS = [
    (button, *(int(bound) for bound in window.split("..")), int(code, 16), resistance)
    for button, window, code, resistance in _table("| Button | Window | Code | Switch resistance |")
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
    (low,) = [low for name, low, _, _, _ in WINDOWS if name == button]
    return low


def _code(button: str) -> int:
    (code,) = [code for name, _, _, code, _ in WINDOWS if name == button]
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
        assert f"`0x{value:02X}` at `0x{byte:04X}`" in _flat(_doc()), image


@pytest.mark.parametrize("image", IMAGES)
def test_not_installed_stores_nothing_outside_the_stack_frame(image: str) -> None:
    layout = _site(image)[1]
    decoder = Decoder(_image(image, NOT_INSTALLED), layout)
    for _, low, high, _, _ in WINDOWS:
        for level in (low, high):
            machine = decoder.run(level)
            assert machine.stores or machine.loads, (image, level)
            assert not _outside_frame(machine), (image, level)


@pytest.mark.parametrize("image", IMAGES)
def test_icc_switch_decodes_every_window_at_both_bounds(image: str) -> None:
    layout = _site(image)[1]
    decoder = Decoder(_image(image, ICC), layout)
    for button, low, high, code, _ in WINDOWS:
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


def test_1nd_decoder_returns_only_while_the_second_gate_bit_is_clear() -> None:
    for image in ("1ND0A", "1ND3B"):
        data = _image(image, NOT_INSTALLED)
        assert not data[ND_RETURN_GATE] & 0x01, image
        decoder = Decoder(_patched(data, {ND_RETURN_GATE: data[ND_RETURN_GATE] | 0x01}), "1nd")
        machine = decoder.machine
        machine.seed_word(decoder.word, _level("CANCEL"))
        machine.pr = RETURN
        assert machine.run(decoder.entry, (ND_PAST_DECODE, RETURN), STEPS) == ND_PAST_DECODE
        assert not machine.stored(decoder.code), image
    doc = _flat(_doc())
    assert f"bit 0 of `ROM8[0x{ND_RETURN_GATE:04X}]`" in doc
    assert f"continues at `0x{ND_PAST_DECODE:08X}`" in doc


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
    stated = {"JK00C": "on JK00C", "JK00D": "on JK00D", "1ND0A": "on 1ND", "1ND3B": "on 1ND",
              "1ME3B": "on 1ME3B"}[image]
    assert f"`0x{SELECTORS[image]:04X}` {stated}" in _flat(_doc()), image


def test_first_icc_ladder_is_the_jk08a_ladder() -> None:
    data = romkit.load("JK08A").data
    ladder = [u16(data, FIRST_LADDER + 2 * index) for index in range(2 * len(WINDOWS))]
    assert ladder == [bound for _, low, high, _, _ in WINDOWS for bound in (low, high)]
    assert f"JK08A ladder at `0x{FIRST_LADDER:05X}`" in _flat(_doc())


def _fragment(page: str) -> str:
    with FRAGMENTS_PATH.open(encoding="utf-8") as source:
        texts = [json.loads(line)["text"] for line in source
                 if json.loads(line)["page_label"] == page]
    return _flat(" ".join(texts))


def test_manual_resistances_lie_in_the_windows() -> None:
    text = _fragment("CCS-47")
    assert "CHECK ICC STEERING SWITCH" in text and "13 16 DISTANCE" in text
    values = [int(value) for value in re.findall(r"Approx\. (\d+)", text)]
    buttons = ("MAIN", "CANCEL", "DISTANCE", "SET/COAST", "RESUME/ACCELERATE")
    positions = [text.index(f" {button} ") for button in buttons]
    assert positions == sorted(positions)
    released = values[1::2]
    assert len(values) == 2 * len(buttons) and set(released) == {5456}
    manual = dict(zip(buttons, values[0::2]))
    manual["all released"] = released[0]
    stated = {button: resistance for button, _, _, _, resistance in WINDOWS}
    for button, low, high, _, resistance in WINDOWS:
        if resistance == "open":
            count = 1023
        else:
            ohms = int(resistance.removesuffix(" Ohm"))
            assert ohms == manual[button], button
            count = 1023 * ohms / (ohms + 1000)
        assert low <= count <= high, button
    assert set(stated) - {"open input"} == set(manual)
    assert "transmits ICC steering switch signal through CAN communication" in _fragment("CCS-26")


def _records(data: bytes, base: int):
    for index in range(MAILBOX_RECORDS):
        at = base + 4 * index
        yield at, data[at], data[at + 1], u16(data, at + 2) >> 5


def test_images_with_the_switch_configure_no_icc_mailbox() -> None:
    jk08a = {at: (identifier, kind, length)
             for at, kind, length, identifier in _records(romkit.load("JK08A").data, MAILBOXES["7mfk"])}
    for at, record in ICC_RECORDS.items():
        assert jk08a[at] == record, hex(at)
    icc = {identifier for identifier, _, _ in ICC_RECORDS.values()}
    for image, layout, _, _, _ in SITES:
        if image == "JK08A":
            continue
        records = list(_records(romkit.load(image).data, MAILBOXES[layout]))
        identifiers = {identifier for _, _, _, identifier in records}
        assert COMMON_FRAMES <= identifiers, image
        assert not icc & identifiers, image
        if layout == "7mfk":
            by_address = {at: (kind, identifier) for at, kind, _, identifier in records}
            assert all(by_address[at] == (5, 0) for at in ICC_RECORDS), image
    doc = _flat(_doc())
    for layout, base in MAILBOXES.items():
        assert f"`0x{base:04X}`" in doc, layout
    assert "`0x975A`, `0x975E`, and `0x979A` hold type 5" in doc


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
    doc = _flat(_doc())
    for layout, base in GROUP_TABLES.items():
        assert f"`0x{base:05X}`" in doc, layout
    for entry, _, _ in MONITORS.values():
        assert f"`0x{entry:08X}`" in doc, hex(entry)


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
def test_builder_preserves_the_configuration_byte(image: str) -> None:
    byte = _site(image)[2]
    layout = rom_checksums.layout_for_rom(image)
    data = bytes(rom_checksums.recalculate(_image(image, ICC), layout))
    result = build_rom.build_image(data, source_name=f"{image} with {ICC}")
    assert result.rom == image
    assert result.data[byte] == STATES[ICC]
    assert rom_checksums.verify(result.data, layout).valid


def test_documents_cite_the_switch() -> None:
    selector = _flat((ROOT / "patches/map-switching-selector.md").read_text(encoding="utf-8"))
    launch = _flat((ROOT / "patches/rolling-launch.md").read_text(encoding="utf-8"))
    readme = _flat((ROOT / "defs/README.md").read_text(encoding="utf-8"))
    builder = _flat((ROOT / "patches/rom-builder.md").read_text(encoding="utf-8"))
    matrix = (ROOT / "rom-images/support-matrix.md").read_text(encoding="utf-8")
    until = f"until the Cruise Control Switch of their definitions selects {ICC}"
    others = ", ".join(image for image in IMAGES if image != "JK08A")
    assert f"the selector stays on Map 1 {until}" in selector
    assert "`cruise-control-switch.md`" in selector
    assert f"Rolling Launch never arms on them {until}" in launch
    for text in (selector, launch):
        assert others.replace(", 1ND3B", ", and 1ND3B") in text
    assert "The Cruise Control Switch is a definition-controlled data edit" in readme
    assert "`../patches/cruise-control-switch.md`" in readme
    assert "the cruise control configuration byte of the Cruise Control Switch" in builder
    header = "| Family | DTC codes | Developer Immobilizer | Cruise Control Switch | Native RomRaider checksum |"
    lines = matrix.splitlines()
    start = lines.index(header)
    column = {}
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        column[cells[0]] = cells[3]
    families = {"7mfk": "7MFKAVN86", "1nd": "1ND"}
    expected = {families.get(layout, image): f"0x{byte:04X}"
                for image, layout, byte, _, _ in SITES}
    expected.update({image: "none" for image, _ in WITHOUT_SWITCH.values()})
    assert column == expected
    assert "`../patches/cruise-control-switch.md`" in _flat(matrix)
