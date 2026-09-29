#!/usr/bin/env python3
"""Execute stock instruction regions whose behavior the entity files state.

A region is a run of stock instructions of one image at their original
addresses. The verifier links the GNU reconstruction of the region and of the
pool words it loads at the same addresses and requires byte identity with the
image. It then builds a simulator-only fixture from the image: the pool words
that hold high-RAM addresses point into simulator test RAM, and an RTS/NOP
pair replaces the two instruction words that follow the region, outside it.
The harness seeds the RAM inputs, calls the region with the registers that it
reads on entry, and checks every store against the symbols and the named bits
of the entity files, which the verifier passes to it.
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
    # The first address after the region, where the boundary RTS/NOP goes.
    end: int
    pool: int
    pool_size: int
    # Pool words that hold high-RAM addresses.
    ram_literals: tuple[int, ...]
    # The stock MOV.L @(disp,PC),R12 that loads the base register before the
    # region.
    base_load: int
    cases: int


REGIONS = (
    Region(
        key="jk78c-ascd-main",
        rom="JK78C",
        source="stock_jk78c_ascd_main.s",
        harness="stock_ascd_main_harness.c",
        start=0x000FCBB0,
        end=0x000FCBEE,
        pool=0x000FCD60,
        pool_size=0x10,
        ram_literals=(0x000FCD60, 0x000FCD6C),
        base_load=0x000FC9CA,
        cases=8,
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
    """Link the reconstruction at the region start and require the image
    bytes of the region and of its pool words."""
    stem = build_dir / region.key
    base_verifier.run_command([
        base_verifier.AS, "--big", "--isa=sh2e",
        "-o", stem.with_suffix(".o"), TOOL_DIR / region.source,
    ])
    base_verifier.run_command([
        base_verifier.LD, "-EB", f"-Ttext={region.start:#x}",
        f"--entry={region.start:#x}",
        "-o", stem.with_suffix(".elf"), stem.with_suffix(".o"),
    ])
    base_verifier.run_command([
        base_verifier.OBJCOPY, "-O", "binary",
        stem.with_suffix(".elf"), stem.with_suffix(".raw"),
    ])
    raw = stem.with_suffix(".raw").read_bytes()
    spans = ((region.start, region.end), (region.pool, region.pool + region.pool_size))
    for start, end in spans:
        actual = raw[start - region.start : end - region.start]
        if actual != image[start:end]:
            raise VerificationError(
                f"{region.key}: the reconstruction of {start:#010x}.."
                f"{end:#010x} differs from the {region.rom} image"
            )
    return (region.end - region.start) // 2


def build_fixture(region, image):
    """The simulator-only fixture of a region; the region bytes stay stock."""
    fixture = bytearray(image)
    for address in region.ram_literals:
        if not region.pool <= address < region.pool + region.pool_size:
            raise VerificationError(
                f"{region.key}: {address:#010x} lies outside the pool"
            )
        value = _word(fixture, address)
        fixture[address : address + 4] = base_verifier.alias_high_ram(
            value
        ).to_bytes(4, "big")
    fixture[region.end : region.end + len(RETURN_STUB)] = RETURN_STUB
    if fixture[region.start : region.end] != image[region.start : region.end]:
        raise VerificationError(f"{region.key}: the fixture alters the region")
    return bytes(fixture)


def harness_defines(region, image):
    """The symbols and named bits of the entity files, and the stock base
    register value, as harness definitions."""
    layout = kb_targets.layout_of(region.rom, root=ROOT)
    return {
        "ASCD_FLAGS": kb_targets.address("ascd_state/ram", layout, root=ROOT),
        "ASCD_MAIN_MASK": 1 << kb_targets.bit(
            "ascd_state/ram", layout, "main", root=ROOT
        ),
        "BUTTON_STATE": kb_targets.address(
            "button_state/ram", layout, root=ROOT
        ),
        "REGION_R12": base_register(region, image),
    }


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
