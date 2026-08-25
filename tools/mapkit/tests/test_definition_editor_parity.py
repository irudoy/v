"""RomRaider and TunerPro artifacts must publish the same entities.

The two editors use different constructs for the same control: RomRaider models
a reversible two-state range as a `Switch` table, TunerPro as an `XDFPATCH`
entry. Parity is therefore asserted over exact ROM ranges and their stock and
patched bytes rather than over element names.

TunerPro additionally publishes one group patch per DTC group. RomRaider has no
construct for a switch spanning discontiguous ranges, so that asymmetry is
permitted and constrained: every group entry must repeat an individual entry.
"""

from pathlib import Path
import re
import xml.etree.ElementTree as ET

import pytest


ROOT = Path(__file__).resolve().parents[3]
DEFS = ROOT / "defs"
ROMS = sorted(path.stem for path in DEFS.glob("*.xml"))
GROUP_TITLE = "Disable DTC group:"
TABLE_TYPES = {"2D", "3D"}


def _xdf_blocks(text, tag):
    return re.findall(rf"<{tag}[ >].*?</{tag}>", text, re.S)


def _title(block):
    return re.search(r"<title>(.*?)</title>", block, re.S).group(1)


def _romraider_ranges(rom):
    """Return every reversible RomRaider range as address, stock and patched."""
    root = ET.parse(DEFS / f"{rom}.xml").getroot().find("./rom")
    ranges = set()
    for table in root.findall("table"):
        if table.get("type") != "Switch":
            continue
        states = table.findall("state")
        assert len(states) == 2, f"{rom}: {table.get('name')} is not two-state"
        address = int(table.get("storageaddress"), 16)
        stock, patched = (
            state.get("data").replace(" ", "").lower() for state in states
        )
        assert len(stock) == len(patched)
        ranges.add((address, len(stock) // 2, stock, patched))
    return ranges


def _tunerpro_ranges(text):
    """Return individual and group TunerPro patch ranges separately."""
    individual, group = set(), set()
    for block in _xdf_blocks(text, "XDFPATCH"):
        target = group if _title(block).startswith(GROUP_TITLE) else individual
        for entry in re.finditer(
            r'<XDFPATCHENTRY[^>]*address="0x([0-9A-Fa-f]+)"[^>]*'
            r'datasize="0x([0-9A-Fa-f]+)"[^>]*'
            r'patchdata="([0-9A-Fa-f]*)"[^>]*'
            r'basedata="([0-9A-Fa-f]*)"',
            block,
        ):
            address, size, patched, stock = entry.groups()
            target.add((int(address, 16), int(size, 16),
                        stock.lower(), patched.lower()))
    return individual, group


@pytest.mark.parametrize("rom", ROMS)
def test_calibration_tables_match(rom):
    root = ET.parse(DEFS / f"{rom}.xml").getroot().find("./rom")
    xml_names = sorted(
        table.get("name") for table in root.findall("table")
        if table.get("type") in TABLE_TYPES
    )
    xdf_names = sorted(
        _title(block)
        for block in _xdf_blocks((DEFS / f"{rom}.xdf").read_text(), "XDFTABLE")
    )
    assert xml_names == xdf_names


@pytest.mark.parametrize("rom", ROMS)
def test_reversible_ranges_match(rom):
    individual, _ = _tunerpro_ranges((DEFS / f"{rom}.xdf").read_text())
    assert _romraider_ranges(rom) == individual


@pytest.mark.parametrize("rom", ROMS)
def test_group_patches_repeat_individual_ranges(rom):
    individual, group = _tunerpro_ranges((DEFS / f"{rom}.xdf").read_text())
    assert group <= individual


@pytest.mark.parametrize("rom", ROMS)
def test_bitwise_switch_bits_match_flags(rom):
    root = ET.parse(DEFS / f"{rom}.xml").getroot().find("./rom")
    xml_bits = set()
    for table in root.findall("table"):
        if table.get("type") != "BitwiseSwitch":
            continue
        address = int(table.get("storageaddress"), 16)
        for bit in table.findall("bit"):
            xml_bits.add((address, 1 << int(bit.get("position")),
                          bit.get("name")))
    xdf_bits = set()
    for block in _xdf_blocks((DEFS / f"{rom}.xdf").read_text(), "XDFFLAG"):
        address = re.search(r'mmedaddress="0x([0-9A-Fa-f]+)"', block).group(1)
        mask = re.search(r"<mask>0x([0-9A-Fa-f]+)</mask>", block).group(1)
        xdf_bits.add((int(address, 16), int(mask, 16), _title(block)))
    assert xml_bits == xdf_bits
