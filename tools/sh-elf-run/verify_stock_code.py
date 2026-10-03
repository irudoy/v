#!/usr/bin/env python3
"""Execute stock instruction regions whose behavior the entity files state.

A region is a run of stock instructions of one image at their original
addresses: a whole function, or a block inside one. The verifier links the
GNU reconstruction of the region and of the pool words it loads at the same
addresses and requires byte identity with the image. It then builds a
simulator-only fixture from the image: the pool words that hold high-RAM
addresses point into simulator test RAM, and for a block an RTS/NOP pair
replaces the two instruction words that follow it, outside the region; a
whole function returns through its own RTS. The harness seeds the RAM and
calibration inputs, calls the region with the registers that it reads on
entry, and checks every store and the return value against the symbols and
the named bits of the entity files, which the verifier passes to it with the
region constants.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
import hashlib
from pathlib import Path
import sys
import tempfile


TOOL_DIR = Path(__file__).resolve().parent
ROOT = TOOL_DIR.parents[1]
# The firmware gate runs outside the project environment, where the `kb`
# package is importable only from its source tree.
for _path in (TOOL_DIR, ROOT / "tools" / "kb" / "src", ROOT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))

import verify_map_switching as base_verifier

from kb import targets as kb_targets


RETURN_STUB = bytes.fromhex("000b0009")


@dataclass(frozen=True)
class Region:
    key: str
    rom: str
    source: str
    harness: str
    start: int
    # The first address after the region.
    end: int
    # The pool spans that the region loads, as (address, size).
    pools: tuple[tuple[int, int], ...]
    # Pool words that hold high-RAM addresses.
    ram_literals: tuple[int, ...]
    cases: int
    # A block returns through the RTS/NOP pair that the fixture places at
    # `end`; a whole function returns through its own RTS.
    boundary: bool = True
    # The stock MOV.L @(disp,PC),R12 that loads the base register before a
    # block that reads it on entry.
    base_load: int | None = None
    # Harness definitions of the address of a meaning on the layout, as
    # (definition, meaning).
    symbols: tuple[tuple[str, str], ...] = ()
    # Harness definitions of the mask of a named bit, as (definition,
    # meaning, bit).
    bits: tuple[tuple[str, str, str], ...] = ()
    # Harness definitions of the addresses inside the region that no entity
    # file names, as (definition, value).
    constants: tuple[tuple[str, int], ...] = ()
    # Additional stock instruction spans executed by this region, with
    # their independently assembled callees at the original addresses.
    callees: tuple[tuple[int, int], ...] = ()

    @property
    def code_spans(self):
        return ((self.start, self.end), *self.callees)


FUEL_CUT_SYMBOLS = (
    ("FUEL_INHIBIT", "fuel_inhibit/ram"),
    ("ENGINE_SPEED", "rpm/ram"),
    ("FUEL_CUT_TABLE", "rev_limit_fuel_cut/tbl"),
)
FUEL_CUT_BITS = (
    ("ARMED_MASK", "fuel_inhibit/ram", "armed"),
    ("ACTIVE_MASK", "fuel_inhibit/ram", "active"),
)

REGIONS = (
    Region(
        key="jk08a-rpm-division",
        rom="JK08A",
        source="stock_jk08a_rpm_division.s",
        harness="stock_rpm_division_harness.c",
        start=0x00038272,
        end=0x0003829E,
        pools=((0x00021DC8, 8), (0x00038370, 0x14)),
        ram_literals=(0x00021DC8, 0x00038370, 0x00038374, 0x00038380),
        cases=20,
        boundary=False,
        symbols=(
            ("MODE_FLAGS", "nice-silkworm/ram"),
            ("EVENT_INTERVAL", "imported-kudu/ram"),
            ("ENGINE_SPEED", "classic-caracal/ram"),
            ("DIVIDER_ENTRY", "unsigned_divide/fn"),
        ),
        constants=(("FAULT_POINTER", 0x00021DC8), ("FAULT_VALUE", 0x00021DCC)),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-rpm-drop-arithmetic",
        rom="JK08A",
        source="stock_jk08a_rpm_drop.s",
        harness="stock_rpm_drop_harness.c",
        start=0x0003E1FE,
        end=0x0003E26C,
        pools=((0x0003E3CC, 4), (0x0003E3DC, 4)),
        ram_literals=(0x0003E3CC,),
        cases=14,
        symbols=(
            ("DROP_WORD", "satisfied-macaque/ram"),
            ("CURRENT_SPEED", "sophisticated-magpie/ram"),
            ("HISTORY_SPEED", "cinnamon-crayfish/ram"),
            ("PREVIOUS_DROP", "teal-curassow/ram"),
        ),
        constants=(("DROP_COEFFICIENT", 0x000084A4),),
    ),
    Region(
        key="jk78c-ascd-main",
        rom="JK78C",
        source="stock_jk78c_ascd_main.s",
        harness="stock_ascd_main_harness.c",
        start=0x000FCBB0,
        end=0x000FCBEE,
        pools=((0x000FCD60, 0x10),),
        ram_literals=(0x000FCD60, 0x000FCD6C),
        cases=8,
        base_load=0x000FC9CA,
        symbols=(
            ("ASCD_FLAGS", "ascd_state/ram"),
            ("BUTTON_STATE", "button_state/ram"),
        ),
        bits=(("ASCD_MAIN_MASK", "ascd_state/ram", "main"),),
    ),
    # The main RPM fuel-cut state machines of the two relocated 8MFK layouts:
    # the delay counter, the pair selector, the configuration byte, and the
    # delay byte have no symbols on them.
    Region(
        key="jk00c-rpm-fuel-cut",
        rom="JK00C",
        source="stock_jk00c_rpm_fuel_cut.s",
        harness="stock_rpm_fuel_cut_harness.c",
        start=0x00050BF8,
        end=0x00050C9A,
        pools=((0x00050D68, 4), (0x00050D88, 0x10)),
        ram_literals=(0x00050D68, 0x00050D88),
        cases=14,
        boundary=False,
        symbols=FUEL_CUT_SYMBOLS,
        bits=FUEL_CUT_BITS,
        constants=(
            ("DELAY_COUNTER", 0xFFFF2579),
            ("PAIR_SELECTOR", 0xFFFF24EC),
            ("CUT_CONFIG", 0x00008B6B),
            ("CUT_DELAY", 0x00008C97),
        ),
    ),
    Region(
        key="jk00d-rpm-fuel-cut",
        rom="JK00D",
        source="stock_jk00d_rpm_fuel_cut.s",
        harness="stock_rpm_fuel_cut_harness.c",
        start=0x00050BF4,
        end=0x00050C96,
        pools=((0x00050D64, 4), (0x00050D84, 0x10)),
        ram_literals=(0x00050D64, 0x00050D84),
        cases=14,
        boundary=False,
        symbols=FUEL_CUT_SYMBOLS,
        bits=FUEL_CUT_BITS,
        constants=(
            ("DELAY_COUNTER", 0xFFFF2581),
            ("PAIR_SELECTOR", 0xFFFF24F4),
            ("CUT_CONFIG", 0x00008B6C),
            ("CUT_DELAY", 0x00008C99),
        ),
    ),
)


class VerificationError(RuntimeError):
    """Raised when a stock-code executable contract fails."""


def stock_image(rom):
    """The bytes of the stock image of a ROM after its digest check."""
    with (ROOT / "rom-images" / "roms.csv").open(encoding="utf-8") as handle:
        rows = [row for row in csv.DictReader(handle) if row["rom"] == rom]
    if len(rows) != 1:
        raise VerificationError(f"{rom}: {len(rows)} rows in rom-images/roms.csv")
    data = (ROOT / "rom-images" / rows[0]["path"]).read_bytes()
    if hashlib.sha256(data).hexdigest() != rows[0]["sha256"]:
        raise VerificationError(f"{rom}: stock image digest differs")
    return data


def _word(data, address, size=4):
    return int.from_bytes(data[address : address + size], "big")


def base_register(region, image):
    """The value that the stock MOV.L at `base_load` gives R12."""
    word = _word(image, region.base_load, 2)
    if word & 0xFF00 != 0xDC00:
        raise VerificationError(
            f"{region.key}: {region.base_load:#010x} holds {word:04x}, "
            "no MOV.L @(disp,PC),R12"
        )
    pool = (region.base_load & ~3) + 4 + (word & 0xFF) * 4
    return _word(image, pool)


def require_reconstruction(region, image, build_dir):
    """Link on the four-byte boundary at or before the first code or pool and require
    the image bytes of the region and of its pool words. A two-byte-aligned
    entry has two padding bytes before its reconstruction, outside the region.
    This preserves the alignment of PC-relative longword loads."""
    starts = [start for start, _ in region.code_spans]
    starts.extend(address for address, _ in region.pools)
    origin = min(starts) & ~3
    stem = build_dir / region.key
    base_verifier.run_command([
        base_verifier.AS, "--big", "--isa=sh2e",
        "-o", stem.with_suffix(".o"), TOOL_DIR / region.source,
    ])
    base_verifier.run_command([
        base_verifier.LD, "-EB", f"-Ttext={origin:#x}",
        f"--entry={region.start:#x}",
        "-o", stem.with_suffix(".elf"), stem.with_suffix(".o"),
    ])
    base_verifier.run_command([
        base_verifier.OBJCOPY, "-O", "binary",
        stem.with_suffix(".elf"), stem.with_suffix(".raw"),
    ])
    raw = stem.with_suffix(".raw").read_bytes()
    spans = (
        *region.code_spans,
        *((address, address + size) for address, size in region.pools),
    )
    for start, end in spans:
        actual = raw[start - origin : end - origin]
        if actual != image[start:end]:
            raise VerificationError(
                f"{region.key}: the reconstruction of {start:#010x}.."
                f"{end:#010x} differs from the {region.rom} image"
            )
    return sum((end - start) // 2 for start, end in region.code_spans)


def build_fixture(region, image):
    """The simulator-only fixture of a region; the region bytes stay stock."""
    fixture = bytearray(image)
    for address in region.ram_literals:
        if not any(start <= address <= start + size - 4
                   for start, size in region.pools):
            raise VerificationError(
                f"{region.key}: {address:#010x} lies outside the pools"
            )
        value = _word(fixture, address)
        fixture[address : address + 4] = base_verifier.alias_high_ram(
            value
        ).to_bytes(4, "big")
    if region.boundary:
        fixture[region.end : region.end + len(RETURN_STUB)] = RETURN_STUB
    for start, end in region.code_spans:
        if fixture[start:end] != image[start:end]:
            raise VerificationError(f"{region.key}: the fixture alters the region")
    return bytes(fixture)


def harness_defines(region, image):
    """The entry of a region, the symbols and named bits of the entity files
    on its layout, its constants, and the stock base register value, as
    harness definitions."""
    layout = kb_targets.layout_of(region.rom, root=ROOT)
    defines = {"REGION_ENTRY": region.start}
    defines.update(
        (name, kb_targets.address(ref, layout, root=ROOT))
        for name, ref in region.symbols
    )
    defines.update(
        (name, 1 << kb_targets.bit(ref, layout, bit, root=ROOT))
        for name, ref, bit in region.bits
    )
    defines.update(region.constants)
    if region.base_load is not None:
        defines["REGION_R12"] = base_register(region, image)
    return defines


def run_region(region, invoke, build_dir):
    image = stock_image(region.rom)
    instructions = require_reconstruction(region, image, build_dir)
    fixture = build_fixture(region, image)
    fixture_path = build_dir / f"{region.key}.sim-fixture"
    rom_object = build_dir / f"{region.key}-rom.o"
    fixture_path.write_bytes(fixture)
    base_verifier.run_command([
        base_verifier.OBJCOPY, "-I", "binary", "-O", "elf32-sh", "-B", "sh",
        "--rename-section", ".data=.rom,alloc,load,code,data,contents",
        fixture_path, rom_object,
    ])
    output = build_dir / f"{region.key}-harness.elf"
    text_base = max(base_verifier.DRIVER_TEXT_BASE, len(fixture) + 0x10000)
    defines = harness_defines(region, image)
    base_verifier.run_command(
        [
            base_verifier.GCC, "-m2e", "-mb", "-std=c11", "-O2",
            "-Wall", "-Wextra", "-Werror",
            f'-DREGION_KEY="{region.key}"',
            *(f"-D{name}={value:#x}U" for name, value in defines.items()),
            f"-Wl,-Ttext-segment={text_base:#x}",
            "-Wl,--section-start=.rom=0",
            "-o", output,
            TOOL_DIR / region.harness, invoke, rom_object,
        ],
        timeout=120,
    )
    result = base_verifier.run_command(
        [
            base_verifier.RUN,
            f"--memory-region={base_verifier.TEST_RAM_BASE:#x},64k",
            output,
        ],
        timeout=120,
    )
    marker = (
        f"VQ_SH_ELF_STOCK_CODE status=PASS region={region.key} "
        f"cases={region.cases}"
    )
    if marker not in result.stdout:
        raise VerificationError(
            f"{region.key}: zero exit without the exact PASS marker"
            + (f"\n{result.stdout.rstrip()}" if result.stdout else "")
        )
    return instructions


def verify(verbose=False):
    with tempfile.TemporaryDirectory(prefix="vq-sh-elf-stock-") as directory:
        build_dir = Path(directory)
        invoke = build_dir / "stock-invoke.o"
        base_verifier.run_command([
            base_verifier.AS, "--big", "--isa=sh2e",
            "-o", invoke, TOOL_DIR / "stock_invoke.s",
        ])
        instructions = 0
        for region in REGIONS:
            count = run_region(region, invoke, build_dir)
            instructions += count
            if verbose:
                print(
                    f"STOCK_CODE region={region.key} rom={region.rom} "
                    f"start={region.start:#010x} instructions={count} "
                    f"cases={region.cases}"
                )
    result = {
        "regions": len(REGIONS),
        "instructions": instructions,
        "dynamic_cases": sum(region.cases for region in REGIONS),
    }
    print(
        f"VQ_SH_ELF_STOCK_CODE status=PASS regions={result['regions']} "
        f"instructions={instructions} cases={result['dynamic_cases']}"
    )
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)
    try:
        verify(verbose=args.verbose)
    except (OSError, ValueError, VerificationError,
            base_verifier.VerificationError) as error:
        print(f"VQ_SH_ELF_STOCK_CODE status=FAIL error={error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
