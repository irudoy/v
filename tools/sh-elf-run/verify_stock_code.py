#!/usr/bin/env python3
"""Execute stock instruction regions whose behavior the entity files state.

A region is a run of stock instructions of one image at their original
addresses: a whole function, or a block inside one. The verifier links the
GNU reconstruction of the region and of the pool words it loads at the same
addresses and requires byte identity with the image. It then builds a
simulator-only fixture from the image: the pool words that hold high-RAM
addresses point into simulator test RAM. A block returns through a boundary
outside the tested instructions: RTS/NOP normally, or a stack-held PR restore
followed by RTS/NOP after a stock call replaces PR. A whole function returns
through its own RTS. The harness seeds the RAM and
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
    # A region without a stock return uses the RTS/NOP pair that the fixture
    # places at `end`; another region returns through its own instructions.
    boundary: bool = True
    # The stack offset of a simulator return continuation for a block whose
    # stock calls replace PR. The boundary restores PR outside all tested
    # instructions; None uses the ordinary RTS/NOP boundary.
    return_address_offset: int | None = None
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
    # Additional stock instruction spans executed by this region, including
    # callees or a selection path separated by pool data, at stock addresses.
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
        key="jk08a-load-normalization",
        rom="JK08A",
        source="stock_jk08a_load_normalization.s",
        harness="stock_load_normalization_harness.c",
        start=0x0003BD1C,
        end=0x0003BD5C,
        pools=((0x00009534, 2), (0x00021DC8, 8),
               (0x0003BDF0, 4), (0x0003BE10, 12)),
        ram_literals=(0x00021DC8, 0x0003BDF0, 0x0003BE10),
        cases=44,
        return_address_offset=0,
        symbols=(("BFS_INPUT", "bfs/ram"), ("LIVE_LOAD", "benign-cassowary/ram"),
                 ("REFERENCE_ADDRESS", "precise-nuthatch/tbl")),
        constants=(("DIVIDER_ENTRY", 0x00021CE0), ("FAULT_ADDRESS", 0xFFFF9818)),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-maf-aggregate",
        rom="JK08A",
        source="stock_jk08a_maf_aggregate.s",
        harness="stock_maf_aggregate_harness.c",
        start=0x0003B252,
        end=0x0003B27E,
        pools=((0x0003B390, 8),),
        ram_literals=(0x0003B390, 0x0003B394),
        cases=32,
        boundary=False,
        symbols=(("MAF_BANK1", "jasper-walrus/ram"),
                 ("MAF_BANK2", "imposing-auk/ram"),
                 ("MAF_CORRECTION", "mindful-goose/ram"),
                 ("MAF_AUXILIARY", "wondrous-sparrow/ram"),
                 ("MAF_AGGREGATE", "polar-viper/ram")),
    ),
    Region(
        key="jk08a-maf-filter",
        rom="JK08A",
        source="stock_jk08a_maf_filter.s",
        harness="stock_maf_filter_harness.c",
        start=0x0003A982,
        end=0x0003A9AA,
        pools=((0x0000870A, 1), (0x0003AB68, 4), (0x0003AB70, 12)),
        ram_literals=(0x0003AB68, 0x0003AB70, 0x0003AB74),
        cases=110,
        boundary=False,
        symbols=(("MAF_SOURCE_B1", "vague-pony/ram"),
                 ("MAF_SOURCE_B2", "opalescent-pronghorn/ram"),
                 ("MAF_WORKING_B1", "precious-adder/ram"),
                 ("MAF_WORKING_B2", "dancing-hippo/ram"),
                 ("MAF_FILTERED_B1", "vegan-polecat/ram"),
                 ("MAF_FILTERED_B2", "spiked-dalmatian/ram"),
                 ("MODE_FLAGS", "satisfied-bulldog/ram"),
                 ("FILTER_ENTRY", "sandy-chameleon/fn")),
        constants=(("COPY_CAP_ENTRY", 0x0003A996), ("ANTI_STALL_ENTRY", 0x0003A9EC),
                   ("COEFFICIENT_ADDRESS", 0x0000870A), ("FILTER_BASE", 0xFFFF1DEC)),
        callees=((0x0003A9AA, 0x0003AA12),),
    ),
    Region(
        key="jk08a-maf-transfer",
        rom="JK08A",
        source="stock_jk08a_maf_transfer.s",
        harness="stock_maf_transfer_harness.c",
        start=0x0003A922,
        end=0x0003A950,
        pools=((0x000086F9, 1), (0x00008782, 1), (0x00008B3F, 1),
               (0x000141F4, 256), (0x00026424, 2), (0x00026428, 4),
               (0x00026ABC, 4), (0x0003AB60, 16), (0x0003B374, 2),
               (0x0003B3AC, 16), (0x0003B3E8, 12)),
        ram_literals=(0x0003AB68, 0x0003B3AC, 0x0003B3EC, 0x0003B3F0),
        cases=82,
        return_address_offset=0,
        symbols=(("MAF_INPUT_B1", "ginger-stingray/ram"),
                 ("MAF_INPUT_B2", "careful-penguin/ram"),
                 ("MAF_OUTPUT_B1", "vague-pony/ram"),
                 ("MAF_OUTPUT_B2", "opalescent-pronghorn/ram"),
                 ("MAF_TABLE_B1", "wealthy-woodlouse/tbl"),
                 ("MAF_TABLE_B2", "ivory-gecko/tbl"),
                 ("CURVE_ENTRY", "xanthic-kagu/fn")),
        constants=(("BODY_ENTRY", 0x00026A74), ("INPUT_BASE", 0xFFFF1E1C),
                   ("CORRECTION_OUTPUT", 0xFFFF1E2A)),
        callees=((0x00026410, 0x00026424), (0x00026740, 0x0002676E),
                 (0x00026A74, 0x00026ABA), (0x0003B320, 0x0003B374),
                 (0x0003B376, 0x0003B37C), (0x0003B3BC, 0x0003B3E6)),
    ),
    Region(
        key="jk08a-maf-compensation",
        rom="JK08A",
        source="stock_jk08a_maf_compensation.s",
        harness="stock_maf_compensation_harness.c",
        start=0x0003AE8A,
        end=0x0003AF42,
        pools=((0x00009586, 2), (0x0000958C, 2), (0x00021DC8, 8), (0x0003B0F8, 20)),
        ram_literals=(0x00021DC8, 0x0003B0F8, 0x0003B0FC, 0x0003B100),
        cases=90,
        boundary=False,
        symbols=(("MAF_INPUT_B1", "maf_b1/ram"), ("MAF_INPUT_B2", "maf_b2/ram"),
                 ("MAF_OUTPUT_B1", "ginger-stingray/ram"),
                 ("MAF_OUTPUT_B2", "careful-penguin/ram"),
                 ("CORRECTION_B1", "annoying-foxhound/ram"),
                 ("CORRECTION_B2", "unselfish-okapi/ram"),
                 ("INIT_FLAGS", "shapeless-bandicoot/ram"),
                 ("DIVIDER_ENTRY", "unsigned_divide/fn")),
        constants=(("ZERO_DEN_ENTRY", 0x0003AEF2), ("MULTIPLIER_ADDRESS", 0x00009586),
                   ("BIAS_ADDRESS", 0x0000958C), ("FAULT_ADDRESS", 0xFFFF9818)),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-battery-scaling",
        rom="JK08A",
        source="stock_jk08a_maf_scaling.s",
        harness="stock_battery_scaling_harness.c",
        start=0x00039A9E,
        end=0x00039AEE,
        pools=((0x000087F8, 2), (0x000092BE, 2), (0x00039BDC, 2),
               (0x00039CAC, 20), (0x000671C6, 18), (0x0006726A, 6)),
        ram_literals=(0x00039CAC, 0x00039CB0, 0x00039CBC, 0x000671C8,
                      0x000671CC, 0x0006726C),
        cases=32,
        boundary=False,
        symbols=(("BATTERY_SAMPLE", "eager-alligator/ram"),
                 ("BATTERY_COPY", "crouching-mole/ram"),
                 ("BATTERY_BYTE", "amaranth-swine/ram"),
                 ("BATTERY_OUTPUT", "battery_voltage/ram"),
                 ("COEFFICIENT", "satisfied-oarfish/ram"),
                 ("MODE_FLAGS", "shrewd-manul/ram")),
        callees=((0x00067188, 0x000671C6), (0x000671D8, 0x00067202)),
    ),
    Region(
        key="jk08a-maf-scaling",
        rom="JK08A",
        source="stock_jk08a_maf_scaling.s",
        harness="stock_maf_scaling_harness.c",
        start=0x0003C408,
        end=0x0003C45C,
        pools=((0x000087F8, 2), (0x000092BE, 2), (0x0003C474, 2),
               (0x0003C48C, 16), (0x000671C6, 18), (0x0006726A, 6)),
        ram_literals=(0x0003C490, 0x0003C498, 0x000671C8, 0x000671CC, 0x0006726C),
        cases=107,
        boundary=False,
        symbols=(("MAF_SAMPLE_B1", "enthusiastic-pillbug/ram"),
                 ("MAF_SAMPLE_B2", "hairy-dalmatian/ram"),
                 ("MAF_OUTPUT_B1", "maf_b1/ram"), ("MAF_OUTPUT_B2", "maf_b2/ram"),
                 ("COEFFICIENT", "satisfied-oarfish/ram"),
                 ("MODE_FLAGS", "shrewd-manul/ram")),
        constants=(("GUARD_ENTRY", 0x00067188), ("SCALE_ENTRY", 0x000671D8),
                   ("CAP_ENTRY", 0x0003C444), ("BOUNDS_ADDRESS", 0x000087F8),
                   ("DEFAULT_ADDRESS", 0x000092BE)),
        callees=((0x00067188, 0x000671C6), (0x000671D8, 0x00067202)),
    ),
    Region(
        key="jk08a-maf-adc",
        rom="JK08A",
        source="stock_jk08a_maf_adc.s",
        harness="stock_maf_adc_harness.c",
        start=0x000280B6,
        end=0x000280D8,
        pools=((0x000283E8, 4),),
        ram_literals=(0x000283E8,),
        cases=12,
        boundary=False,
        symbols=(("ADDR4", "real-sawfish/reg"), ("ADDR15", "zircon-stallion/reg"),
                 ("MAF_SAMPLE_B1", "enthusiastic-pillbug/ram"),
                 ("MAF_SAMPLE_B2", "hairy-dalmatian/ram")),
        constants=(("ADC_BASE", 0xFFFFF800),),
    ),
    Region(
        key="jk08a-direct-byte-axis",
        rom="JK08A",
        source="stock_jk08a_direct_byte_axis.s",
        harness="stock_direct_byte_axis_harness.c",
        start=0x00026944,
        end=0x00026980,
        pools=((0x00026980, 4),),
        ram_literals=(),
        cases=29,
        boundary=False,
        symbols=(("CVTC_RPM_AXIS", "scrupulous-ladybug/axis"),
                 ("CVTC_LOAD_AXIS", "witty-bobcat/axis")),
        constants=(("LAST_OFFSET", 15), ("AXIS_BYTES", 16), ("DIVIDER_ENTRY", 0x00026C78)),
        callees=((0x00026C78, 0x00026D0E),),
    ),
    Region(
        key="jk08a-implicit-byte-curve",
        rom="JK08A",
        source="stock_jk08a_implicit_byte_curve.s",
        harness="stock_implicit_byte_curve_harness.c",
        start=0x00026370,
        end=0x00026382,
        pools=((0x00026382, 2), (0x00026384, 4), (0x00026ABC, 4)),
        ram_literals=(),
        cases=40,
        boundary=False,
        symbols=(("INJECTION_TABLE", "tangible-gharial/tbl"),
                 ("COLD_TIMING_TABLE", "cold_idle_ignition_timing/tbl")),
        constants=(("BODY_ENTRY", 0x00026A80),),
        callees=((0x00026740, 0x0002676E), (0x00026A80, 0x00026ABA)),
    ),
    Region(
        key="jk08a-byte-axis",
        rom="JK08A",
        source="stock_jk08a_byte_axis.s",
        harness="stock_byte_axis_harness.c",
        start=0x000269C4,
        end=0x00026A06,
        pools=((0x00026A08, 4),),
        ram_literals=(),
        cases=38,
        boundary=False,
        symbols=(("FUEL_AXIS", "fascinating-hog/axis"),
                 ("IGNITION_AXIS", "able-butterfly/axis")),
        constants=(("LAST_OFFSET", 15), ("AXIS_BYTES", 16), ("DIVIDER_ENTRY", 0x00026C78)),
        callees=((0x00026C78, 0x00026D0E),),
    ),
    Region(
        key="jk08a-word-axis",
        rom="JK08A",
        source="stock_jk08a_word_axis.s",
        harness="stock_word_axis_harness.c",
        start=0x00026984,
        end=0x000269C0,
        pools=((0x000269C0, 4),),
        ram_literals=(),
        cases=22,
        boundary=False,
        symbols=(("TORQUE_AXIS", "functional-jackrabbit/axis"),),
        constants=(("LAST_OFFSET", 30), ("AXIS_BYTES", 32), ("DIVIDER_ENTRY", 0x00026C78)),
        callees=((0x00026C78, 0x00026D0E),),
    ),
    Region(
        key="jk08a-crank-capture",
        rom="JK08A",
        source="stock_jk08a_crank_capture.s",
        harness="stock_crank_capture_harness.c",
        start=0x00028F16,
        end=0x00028F4E,
        pools=((0x0002900C, 10), (0x0002903C, 4)),
        ram_literals=(0x0002903C,),
        cases=16,
        symbols=(
            ("OSBR1", "atu1_osbr1/reg"),
            ("CRANK_CAPTURE", "soft-seagull/ram"),
            ("RAW_PERIOD", "pistachio-porcupine/ram"),
            ("CAPTURE_FLAGS", "crank_capture_state/ram"),
        ),
        bits=(("INIT_MASK", "crank_capture_state/ram", "initialized"),),
        constants=(("CRANK_BASE", 0xFFFF128C), ("CORE_BASE", 0xFFFF1FF4),
                   ("MMIO_BASE", 0xFFFFF440), ("REFERENCE_PERIOD", 0xFFFF2294)),
    ),
    Region(
        key="jk08a-tooth-normalization",
        rom="JK08A",
        source="stock_jk08a_tooth_normalization.s",
        harness="stock_tooth_normalization_harness.c",
        start=0x0002915C,
        end=0x00029168,
        pools=((0x0002914A, 0x12), (0x0002920E, 6)),
        ram_literals=(),
        cases=20,
        symbols=(
            ("TOOTH_COUNTER", "tunneling-doberman/ram"),
            ("RAW_PERIOD", "pistachio-porcupine/ram"),
            ("NORMALIZED_PERIOD", "spry-koel/ram"),
        ),
        bits=(("SYNC_MASK", "engine_sync_flags/ram", "synchronized"),),
        constants=(("NORMALIZATION_ENTRY", 0x0002911C), ("REFERENCE_PERIOD", 0xFFFF2296),
                   ("CRANK_BASE", 0xFFFF128C), ("CORE_BASE", 0xFFFF1FF4)),
        # The selection path enters before its pool words and branches to
        # the ordinary copy or to the return boundary after both paths.
        callees=((0x0002911C, 0x0002914A),),
    ),
    Region(
        key="jk08a-tooth-fallback",
        rom="JK08A",
        source="stock_jk08a_tooth_fallback.s",
        harness="stock_tooth_fallback_harness.c",
        start=0x0002B800,
        end=0x0002B820,
        pools=((0x00021DC8, 8), (0x0002B85E, 6), (0x0002B878, 12)),
        ram_literals=(0x00021DC8, 0x0002B878, 0x0002B880),
        cases=13,
        return_address_offset=8,
        symbols=(
            ("EVENT_INTERVAL", "imported-kudu/ram"),
            ("RAW_PERIOD", "pistachio-porcupine/ram"),
            ("NORMALIZED_PERIOD", "spry-koel/ram"),
            ("CAM_INTERVAL", "berserk-woodlouse/ram"),
        ),
        constants=(("CORE_BASE", 0xFFFF1FF4),),
        callees=((0x00021CE0, 0x00021DC6),),
    ),
    Region(
        key="jk08a-event-interval",
        rom="JK08A",
        source="stock_jk08a_event_interval.s",
        harness="stock_event_interval_harness.c",
        start=0x00028AFA,
        end=0x00028B42,
        pools=((0x00028B42, 4), (0x00028B48, 0x14)),
        ram_literals=(0x00028B48, 0x00028B4C, 0x00028B50,
                      0x00028B54, 0x00028B58),
        cases=18,
        boundary=False,
        symbols=(
            ("MODE_FLAGS", "apc_mode/ram"),
            ("CURRENT_CAPTURE", "classy-bull/ram"),
            ("PREVIOUS_CAPTURE", "busy-horse/ram"),
            ("EVENT_INTERVAL", "imported-kudu/ram"),
            ("PUBLISHED_FLAGS", "eggplant-curassow/ram"),
            ("HOLDOFF", "event_interval_holdoff/ram"),
        ),
    ),
    Region(
        key="jk08a-rpm-median",
        rom="JK08A",
        source="stock_jk08a_rpm_median.s",
        harness="stock_rpm_median_harness.c",
        start=0x0003DF2C,
        end=0x0003DFC6,
        pools=((0x00021CD8, 8), (0x0003E018, 8), (0x0003E148, 0x1C)),
        ram_literals=(0x00021CD8, 0x0003E148, 0x0003E14C,
                      0x0003E158, 0x0003E15C, 0x0003E160),
        cases=35,
        boundary=False,
        symbols=(
            ("MODE_FLAGS", "apc_mode/ram"),
            ("TOOTH_PERIOD", "spry-koel/ram"),
            ("MEDIAN_OUTPUT", "statuesque-husky/ram"),
            ("LIVE_SPEED", "angelic-shark/ram"),
            ("HISTORY_NEWEST", "meek-iguana/ram"),
            ("DIVIDER_ENTRY", "pompous-firefly/fn"),
        ),
        constants=(("FAULT_POINTER", 0x00021CD8), ("FAULT_VALUE", 0x00021CDC),
                   ("HISTORY_PREVIOUS", 0xFFFF3E35), ("HISTORY_OLDER", 0xFFFF3E36)),
        callees=((0x00021BBC, 0x00021CD6),),
    ),
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


def return_stub(region):
    """The simulator boundary, with an optional stack-held return address."""
    offset = region.return_address_offset
    if offset is None:
        return RETURN_STUB
    if type(offset) is not int or not 0 <= offset <= 60 or offset % 4:
        raise VerificationError(f"{region.key}: return address offset is a multiple of four in 0..60")
    # MOV.L @(offset,R15),R5; LDS R5,PR; RTS; NOP. R0 remains the result.
    return b''.join(word.to_bytes(2, 'big')
                    for word in (0x55F0 | (offset // 4), 0x452A, 0x000B, 0x0009))


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
        boundary = return_stub(region)
        end = region.end + len(boundary)
        if end > len(fixture) or any(region.end < address + size and address < end
                                     for address, size in region.pools):
            raise VerificationError(f"{region.key}: return boundary overlaps a pool or leaves the image")
        fixture[region.end : end] = boundary
    elif region.return_address_offset is not None:
        raise VerificationError(f"{region.key}: a natural stock return takes no boundary return address")
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
