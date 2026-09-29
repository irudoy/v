"""Gates for the intake CVTC solenoid output stage of the VQ37 layouts.

The stock ROM bytes of the channel-7 cycle programming, the buffer-register
programmers, the scheduler copies of the duty words and of the duty bytes, and
the live-byte writers of JK78C, 1ND0A, 1ND3B, and 1ME3B run in the minimal
SH-2 interpreter of tools/mapkit/sh2_interpreter.py and are compared with the
closed-form model of defs/JK78C.cvtc.md. The interpreter implements only the
instructions of the executed paths and rejects any other opcode, any read of
an unset RAM cell, any store into the image, and any branch or PC-relative load
in a delay slot.

A span that starts inside a function runs in segments over one machine state:
short segments execute the image instructions that set its base registers,
and the harness seeds only registers whose values reach other outputs. No
instruction of the function between the instruction that sets a kept
register and the segment that uses it writes that register; the calls between
them rely on the calling convention, under which a callee preserves R8 to R14
and GBR. The variants with bit 2 of the scheme byte cleared or with another
factor byte run on copies of the image that differ only in that byte.
"""

from __future__ import annotations

import csv
import tomllib
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

import pytest

from kb import match, sh2, targets
from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import STACK_TOP, Sh2, u16


ROOT = Path(__file__).resolve().parents[3]
DOC_PATH = ROOT / "defs/JK78C.cvtc.md"
VARS_PATH = ROOT / "defs/JK08A.vars.csv"
PROFILE_PATH = ROOT / "patches/can-telemetry-profile.toml"
THIS_TEST = "tools/mapkit/tests/test_vq37_intake_duty_scheme.py"

CYLR7A, CYLR7B = 0xFFFFF588, 0xFFFFF58A
BFR7A, BFR7B = 0xFFFFF590, 0xFFFFF592
SCHEME_BIT = 0x04

CYCLE_FACTORS = (1, 3, 66, 255)
PROGRAMMER_FACTORS = (1, 3)

COMMAND = ("intake_cvtc_duty_command_b1/ram", "intake_cvtc_duty_command_b2/ram")
LIVE = ("intake_cvtc_duty_b1/ram", "intake_cvtc_duty_b2/ram")
CELL_SCALE = "x*25/64"
WIRE_SCALE = Fraction(39, 100)
# The unit of the 7mfk cells in the variable ledger and the decoding of their
# telemetry fields.
LEDGER_UNIT = "percent*100/39"
WIRE_DECODING = "raw * 39 / 100 percent"

# Duty words and duty bytes of bank 1 and bank 2; the pairs differ so that a
# swapped bank or a sign-extended load shows.
WORDS = ((0x0000, 0x0000), (0x1234, 0xABCD), (0xFF00, 0x8000),
         (0xFFFF, 0x0100), (0x7FFF, 0x80FF))
BYTES = ((0x00, 0x00), (0x12, 0xAB), (0xFF, 0x80), (0x7F, 0x01))


def _fill(size: int, start: int) -> bytes:
    return bytes((start + 7 * index) & 0xFF for index in range(size))


@dataclass(frozen=True)
class Span:
    """Stock instructions that run in segments over one machine state.

    Each segment runs from its start until it reaches one of its stops.
    `values` seeds registers whose values reach only other outputs, and
    `reads` holds the RAM blocks other than the cells under test that the
    span reads. `kept` lists (register, set at, resume): the segment that
    ends with the instruction at `set at` sets the register, and the segment
    that starts at `resume` uses it.
    """

    segments: tuple[tuple[int, tuple[int, ...]], ...]
    values: tuple[tuple[int, int], ...] = ()
    reads: tuple[tuple[int, bytes], ...] = ()
    kept: tuple[tuple[str, int, int], ...] = ()


@dataclass(frozen=True)
class Layout:
    key: str
    images: tuple[str, ...]
    scheme: int
    factor: int
    cycle: Span
    programmer: int
    programmer_reads: tuple[tuple[int, bytes], ...]
    words: tuple[int, int]
    word_loads: tuple[int, int]
    cells: tuple[int, int]
    cell_loads: tuple[int, int]
    word_stores: tuple[int, int]
    cell_stores: tuple[int, int]
    word_copy: Span
    copied: tuple[int, int]
    writers: tuple[Span, Span]
    live: tuple[int, int]
    live_stores: tuple[int, int]
    byte_copy: Span
    byte_block: tuple[int, int, int]


LAYOUTS = (
    Layout(
        key="jk78c",
        images=("JK78C",),
        scheme=0x0000852A,
        factor=0x00008B5E,
        cycle=Span(
            segments=((0x0002900A, (0x0002900E,)), (0x0002915E, (0x00029160,)),
                      (0x00029190, (0x00029192,)), (0x00029194, (0x0002923E,))),
            values=((5, 0x5A5A), (14, 0x11)),
            kept=(("gbr", 0x0002900C, 0x00029194), ("r4", 0x0002915E, 0x00029194),
                  ("r2", 0x00029190, 0x00029194)),
        ),
        programmer=0x000E7994,
        programmer_reads=((0xFFFF45BF, b"\x00"), (0xFFFF45C2, b"\x00"), (0xFFFF2406, b"\x00")),
        words=(0xFFFF25C4, 0xFFFF25C6),
        word_loads=(0x000E7A6C, 0x000E7B10),
        cells=(0xFFFF2308, 0xFFFF2309),
        cell_loads=(0x000E7A86, 0x000E7B1C),
        word_stores=(0x000E7AF2, 0x000E7B58),
        cell_stores=(0x000E7AF2, 0x000E7B58),
        word_copy=Span(
            segments=((0x00020FEE, (0x00020FF0,)), (0x00020FF4, (0x00021008,))),
            reads=((0xFFFF2578, _fill(8, 0xC0)), (0xFFFF25A8, _fill(32, 0x40))),
            kept=(("r14", 0x00020FEE, 0x00020FF4),),
        ),
        copied=(0xFFFF25A4, 0xFFFF25A6),
        writers=(
            Span(segments=((0x000E5938, (0x000E625A,)),), values=((0, 0x33),)),
            Span(segments=((0x000E593E, (0x000E625A,)),)),
        ),
        live=(0xFFFF239A, 0xFFFF239B),
        live_stores=(0x000E6258, 0x000E6258),
        byte_copy=Span(
            segments=((0x00020F30, (0x00020F34,)), (0x00020F58, (0x00020F5A,)),
                      (0x00021316, (0x00021332,))),
            reads=((0xFFFF227A, _fill(4, 0xE0)),),
            kept=(("r11", 0x00020F32, 0x00021316), ("r12", 0x00020F58, 0x00021316)),
        ),
        byte_block=(0xFFFF2314, 0xFFFF2282, 0x92),
    ),
    Layout(
        key="1nd",
        images=("1ND0A", "1ND3B"),
        scheme=0x00008561,
        factor=0x00008C4B,
        cycle=Span(
            segments=((0x000298CC, (0x000298CE,)), (0x000298D8, (0x000298DA,)),
                      (0x000298DC, (0x00029960,))),
            values=((1, 0x11), (5, 0x5A5A)),
            kept=(("r6", 0x000298CC, 0x000298D8), ("r6", 0x000298D8, 0x000298DC)),
        ),
        programmer=0x001108D0,
        programmer_reads=((0xFFFE94CD, b"\x00"), (0xFFFE8D94, b"\x00"), (0xFFFE9469, b"\x00"),
                          (0xFFFE94E9, b"\x00"), (0xFFFEB8EE, b"\x00"), (0xFFFEB8F3, b"\x00")),
        words=(0xFFFE96BC, 0xFFFE96BE),
        word_loads=(0x00110948, 0x001109C6),
        cells=(0xFFFE93BF, 0xFFFE93C0),
        cell_loads=(0x00110942, 0x001109BE),
        word_stores=(0x001109AC, 0x00110A26),
        cell_stores=(0x001109AC, 0x00110A00),
        word_copy=Span(
            segments=((0x0002122A, (0x0002122E,)), (0x000213F4, (0x000213F8,))),
            kept=(("gbr", 0x0002122C, 0x000213F4),),
        ),
        copied=(0xFFFE9694, 0xFFFE9696),
        writers=(
            Span(segments=((0x0010DD3A, (0x0010EB0C, 0x0010EB96)),), values=((0, 0x33),),
                 reads=((0xFFFE92CC, _fill(4, 0x90)), (0xFFFE81D6, b"\x00"))),
            Span(segments=((0x0010DD40, (0x0010EB0C, 0x0010EB96)),),
                 reads=((0xFFFE92CC, _fill(4, 0x90)), (0xFFFE81D6, b"\x00"))),
        ),
        live=(0xFFFE945B, 0xFFFE945C),
        live_stores=(0x0010EB0A, 0x0010EB0A),
        byte_copy=Span(
            segments=((0x0002122A, (0x0002122E,)), (0x00021722, (0x0002174A,))),
            reads=((0xFFFE9324, _fill(6, 0xE0)),),
            kept=(("gbr", 0x0002122C, 0x00021722),),
        ),
        byte_block=(0xFFFE93CC, 0xFFFE9330, 0x9C),
    ),
    Layout(
        key="1me3b",
        images=("1ME3B",),
        scheme=0x00008576,
        factor=0x00008CA1,
        cycle=Span(
            segments=((0x0002C61C, (0x0002C61E,)), (0x0002C628, (0x0002C62A,)),
                      (0x0002C62C, (0x0002C6B0,))),
            values=((1, 0x11), (5, 0x5A5A)),
            kept=(("r6", 0x0002C61C, 0x0002C628), ("r6", 0x0002C628, 0x0002C62C)),
        ),
        programmer=0x0011C3A6,
        programmer_reads=((0xFFFE949D, b"\x00"), (0xFFFE8D38, b"\x00"), (0xFFFE9439, b"\x00"),
                          (0xFFFE94BA, b"\x00"), (0xFFFEBA5B, b"\x00"), (0xFFFEBA60, b"\x00")),
        words=(0xFFFE9692, 0xFFFE9694),
        word_loads=(0x0011C41E, 0x0011C49C),
        cells=(0xFFFE938F, 0xFFFE9390),
        cell_loads=(0x0011C418, 0x0011C494),
        word_stores=(0x0011C482, 0x0011C4FC),
        cell_stores=(0x0011C482, 0x0011C4D6),
        word_copy=Span(
            segments=((0x00021252, (0x00021256,)), (0x00021414, (0x0002141C,))),
            reads=((0xFFFE9690, _fill(8, 0x60)),),
            kept=(("gbr", 0x00021254, 0x00021414),),
        ),
        copied=(0xFFFE966A, 0xFFFE966C),
        writers=(
            Span(segments=((0x00119B1C, (0x0011AA3E,)),), values=((0, 0x33),)),
            Span(segments=((0x00119B12, (0x00119B16,)), (0x00119B22, (0x00119B3E,))),
                 kept=(("gbr", 0x00119B14, 0x00119B22),)),
        ),
        live=(0xFFFE942B, 0xFFFE942C),
        live_stores=(0x0011AA3C, 0x00119B3C),
        byte_copy=Span(
            segments=((0x00021252, (0x00021256,)), (0x00021776, (0x000217B0,))),
            reads=((0xFFFE92F0, _fill(8, 0xE0)),),
            kept=(("gbr", 0x00021254, 0x00021776),),
        ),
        byte_block=(0xFFFE939C, 0xFFFE9300, 0x9C),
    ),
)

CASES = [(layout, image) for layout in LAYOUTS for image in layout.images]
IDS = [image for _, image in CASES]


def _image(rom: str) -> bytes:
    return romkit.load(rom).data


def _patched(data: bytes, address: int, value: int) -> bytes:
    patched = bytearray(data)
    patched[address] = value
    return bytes(patched)


def _writes(word: int, register: str) -> bool:
    insn = sh2.decode(word, 0)
    if register == "gbr":
        return insn.gbr is not None
    return int(register[1:]) in insn.writes


def _check_kept(layout: Layout, data: bytes, span: Span) -> None:
    owner = match.code(layout.key).owner
    for register, set_at, resume in span.kept:
        function = owner.get(set_at)
        assert function is not None and owner.get(resume) == function, (hex(set_at), hex(resume))
        assert _writes(u16(data, set_at), register), (register, hex(set_at))
        assert any(stops[-1] == set_at + 2 for _, stops in span.segments), hex(set_at)
        assert any(start == resume for start, _ in span.segments), hex(resume)
        writers = [hex(pc) for pc in range(set_at + 2, resume, 2)
                   if owner.get(pc) == function and _writes(u16(data, pc), register)]
        assert not writers, (layout.key, register, writers)


def _machine(data: bytes, span: Span) -> Sh2:
    machine = Sh2(data)
    for register, value in span.values:
        machine.r[register] = value
    for address, values in span.reads:
        machine.seed(address, values)
    return machine


def _run(machine: Sh2, span: Span) -> None:
    for start, stops in span.segments:
        machine.run(start, stops)


def _cycle(data: bytes, layout: Layout) -> dict[int, int]:
    machine = _machine(data, layout.cycle)
    _run(machine, layout.cycle)
    values = {}
    for register in (CYLR7A, CYLR7B):
        found = machine.stored(register)
        assert len(found) == 1 and found[0][1] == 2, (hex(register), found)
        values[register] = found[0][2]
    return values


def _program(data: bytes, layout: Layout, words, cells) -> Sh2:
    machine = Sh2(data)
    for address, values in layout.programmer_reads:
        machine.seed(address, values)
    for address, value in zip(layout.words, words):
        machine.seed_word(address, value)
    for address, value in zip(layout.cells, cells):
        machine.seed(address, bytes([value]))
    machine.call(layout.programmer)
    assert machine.r[15] == STACK_TOP
    return machine


@pytest.mark.parametrize(("layout", "image"), CASES, ids=IDS)
def test_stock_images_select_the_16_bit_scheme(layout: Layout, image: str) -> None:
    data = _image(image)
    assert data[layout.scheme] & SCHEME_BIT
    assert data[layout.factor] == 1


@pytest.mark.parametrize(("layout", "image"), CASES, ids=IDS)
def test_cycle_registers_count_1000_steps_with_bit_2_set_and_125_with_bit_2_clear(
    layout: Layout, image: str
) -> None:
    stock = _image(image)
    _check_kept(layout, stock, layout.cycle)
    for factor in CYCLE_FACTORS:
        data = _patched(stock, layout.factor, factor)
        cycle = min(1000 * factor, 0xFFFF)
        assert _cycle(data, layout) == {CYLR7A: cycle, CYLR7B: cycle}
        cleared = _patched(data, layout.scheme, data[layout.scheme] & ~SCHEME_BIT)
        assert _cycle(cleared, layout) == {CYLR7A: 125 * factor, CYLR7B: 125 * factor}


@pytest.mark.parametrize(("layout", "image"), CASES, ids=IDS)
def test_buffer_programmers_program_the_duty_words_with_bit_2_set(
    layout: Layout, image: str
) -> None:
    stock = _image(image)
    for factor in PROGRAMMER_FACTORS:
        data = _patched(stock, layout.factor, factor)
        for words, cells in zip(WORDS, BYTES + BYTES):
            machine = _program(data, layout, words, cells)
            for register, store_at, word in zip((BFR7B, BFR7A), layout.word_stores, words):
                assert machine.stored(register) == [(store_at, 2, (word * factor * 125) >> 13)]
            assert machine.loaded(layout.words) == list(zip(layout.word_loads, layout.words))
            assert machine.loaded(layout.cells) == []


@pytest.mark.parametrize(("layout", "image"), CASES, ids=IDS)
def test_buffer_programmers_program_the_command_cells_with_bit_2_clear(
    layout: Layout, image: str
) -> None:
    stock = _image(image)
    cleared = _patched(stock, layout.scheme, stock[layout.scheme] & ~SCHEME_BIT)
    for factor in PROGRAMMER_FACTORS:
        data = _patched(cleared, layout.factor, factor)
        for words, cells in zip(WORDS, BYTES + BYTES):
            machine = _program(data, layout, words, cells)
            for register, store_at, cell in zip((BFR7B, BFR7A), layout.cell_stores, cells):
                assert machine.stored(register) == [(store_at, 2, cell * factor * 39 // 80)]
            assert machine.loaded(layout.cells) == list(zip(layout.cell_loads, layout.cells))
            assert machine.loaded(layout.words) == []


@pytest.mark.parametrize(("layout", "image"), CASES, ids=IDS)
def test_scheduler_copies_the_duty_words(layout: Layout, image: str) -> None:
    data = _image(image)
    _check_kept(layout, data, layout.word_copy)
    for words in WORDS:
        machine = _machine(data, layout.word_copy)
        for address, value in zip(layout.words, words):
            machine.seed_word(address, value)
        _run(machine, layout.word_copy)
        assert tuple(machine.peek(copied, 2) for copied in layout.copied) == words


@pytest.mark.parametrize(("layout", "image"), CASES, ids=IDS)
def test_live_byte_writers_store_the_high_byte_of_the_copied_words(
    layout: Layout, image: str
) -> None:
    stock = _image(image)
    cleared = _patched(stock, layout.scheme, stock[layout.scheme] & ~SCHEME_BIT)
    for writer in layout.writers:
        _check_kept(layout, stock, writer)
    for data in (stock, cleared):
        for bank, (writer, store_at) in enumerate(zip(layout.writers, layout.live_stores)):
            for words in WORDS:
                machine = _machine(data, writer)
                for address, value in zip(layout.copied, words):
                    machine.seed_word(address, value)
                _run(machine, writer)
                expected = [(store_at, 1, words[bank] >> 8)] if data is stock else []
                assert machine.stored(layout.live[bank]) == expected
                assert machine.stored(layout.live[1 - bank]) == []


@pytest.mark.parametrize(("layout", "image"), CASES, ids=IDS)
def test_scheduler_copies_the_live_bytes_into_the_command_cells(
    layout: Layout, image: str
) -> None:
    data = _image(image)
    _check_kept(layout, data, layout.byte_copy)
    source, target, count = layout.byte_block
    for live, cell in zip(layout.live, layout.cells):
        assert cell - target == live - source < count
    for start in (0x3D, 0xC2):
        machine = _machine(data, layout.byte_copy)
        block = _fill(count, start)
        machine.seed(source, block)
        _run(machine, layout.byte_copy)
        assert bytes(machine.peek(target + index) for index in range(count)) == block
        written = machine.written()
        assert target + count not in written
        assert not written & set(range(source, source + count))


def test_cell_scale_bounds_the_programmed_duty() -> None:
    """A command cell holds x = w >> 8 of the duty word w that the 16-bit
    scheme programs as floor(w*K*125/8192) of 1000*K steps."""
    scale = Fraction(25, 64)
    for x in range(256):
        assert Fraction(x * 100, 256) == x * scale
    for word in range(0x10000):
        x = word >> 8
        programmed = Fraction((word * 125) >> 13, 10)
        assert Fraction(word * 100, 65536) - Fraction(1, 10) < programmed
        assert programmed <= Fraction(word * 100, 65536)
        assert x * scale - Fraction(1, 10) < programmed < (x + 1) * scale
    # The 8-bit scheme programs floor(x*K*39/80) of 125*K steps: the scale of
    # the wire and of the 7mfk cells.
    for x in range(256):
        programmed = Fraction(x * 39 // 80 * 100, 125)
        assert x * WIRE_SCALE - Fraction(8, 10) < programmed <= x * WIRE_SCALE
    # The wire carries the cell on the 7mfk scale: the difference stays below
    # half a wire step, and the cell percent re-encoded on the wire scale
    # returns the cell.
    difference = max(abs(x * scale - x * WIRE_SCALE) for x in range(256))
    assert difference == Fraction(159375, 1000000)
    assert difference < WIRE_SCALE / 2
    assert all(round(x * scale / WIRE_SCALE) == x for x in range(256))


def test_entity_files_carry_the_cells_and_the_scale() -> None:
    with VARS_PATH.open(encoding="utf-8", newline="") as source:
        units = {int(row["addr"], 16): row["units"] for row in csv.DictReader(source)}
    profile = tomllib.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    fields = {field["name"]: field for context in profile["context"]
              for field in context.get("field", ())}
    for meaning in (*COMMAND, *LIVE):
        canonical = targets.address(meaning, "7mfk", root=ROOT)
        assert units[canonical] == LEDGER_UNIT, meaning
        field = fields[f"{meaning.rpartition('/')[0]}_raw"]
        assert (field["source"], field["width"], field["signed"]) == (canonical, 1, False)
        assert field["scale"] == WIRE_DECODING, meaning
    for layout in LAYOUTS:
        for meanings, addresses in ((COMMAND, layout.cells), (LIVE, layout.live)):
            for meaning, address in zip(meanings, addresses):
                entry = targets.symbol(meaning, layout.key, root=ROOT)
                assert int(entry["address"], 16) == address, (meaning, layout.key)
                assert entry["scale"] == CELL_SCALE, (meaning, layout.key)
                scale = {(item["kind"], item.get("path"), item.get("key"))
                         for item in entry.get("evidence", ())
                         if item.get("supports") == "scale"}
                assert scale == {
                    ("spec", "defs/JK78C.cvtc.md", None),
                    ("test", THIS_TEST, "test_cell_scale_bounds_the_programmed_duty"),
                }, (meaning, layout.key)


def _doc() -> str:
    return " ".join(DOC_PATH.read_text(encoding="utf-8").split())


def _factors(factors: tuple[int, ...]) -> str:
    head = ", ".join(str(factor) for factor in factors[:-1])
    return f"`K` = {head}{',' if len(factors) > 2 else ''} and {factors[-1]}"


def test_document_states_the_output_stage() -> None:
    doc = _doc()
    for layout in LAYOUTS:
        owner = match.code(layout.key).owner
        functions = {owner[layout.cycle.segments[-1][0]],
                     owner[layout.word_copy.segments[-1][0]],
                     owner[layout.byte_copy.segments[-1][0]],
                     *(owner[store_at] for store_at in layout.live_stores)}
        source, target, count = layout.byte_block
        stated = [
            f"`ROM8[0x{layout.scheme:04X}]`",
            f"`ROM8[0x{layout.factor:04X}]`",
            f"`0x{count:02X}` bytes from `0x{source:08X}` to `0x{target:08X}`",
            *(f"`0x{address:08X}`" for address in (
                layout.programmer, *sorted(functions), *layout.words, *layout.copied,
                *layout.live, *layout.cells,
                *(address for address, _ in layout.programmer_reads))),
        ]
        missing = [text for text in stated if text not in doc]
        assert not missing, (layout.key, missing)
    for text in (
        "CYLR7A = CYLR7B = min(1000 * K, 0xFFFF)",
        "CYLR7A = CYLR7B = 125 * K",
        "BFR = floor(w * K * 125 / 8192)",
        "BFR = floor(x * K * 39 / 80)",
        "percent = w * 100 / 65536, less at most 0.1 / K",
        "percent = x * 25 / 64",
        "percent = x * 39 / 100",
        f"`x = 255` reads {255 * 25 / 64:.2f} percent",
        "at most `x / 1600` percentage points, 0.159375 at `x = 255`",
        f"the cycle programming at {_factors(CYCLE_FACTORS)}",
        f"the buffer programmers at {_factors(PROGRAMMER_FACTORS)}",
        f"override the scale with `{CELL_SCALE.replace('*', ' * ').replace('/', ' / ')}`",
    ):
        assert text in doc, text
