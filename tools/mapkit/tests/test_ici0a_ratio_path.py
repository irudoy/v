"""Bounded ICI0A ratio-cell action, not full interrupt or hardware semantics.

Independent exact-image bytes bind the vector, bases, writer, reader and signed
integer divider. PathSh2 is unchanged. The declared unsigned incoming operands
select only the supported nonzero divider paths. Zero current bypasses division.
No computed output seed, stub, relocation, RTE or complete ISR is executed.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
import hashlib
from itertools import product
import json
from pathlib import Path
import random

import pytest

from tools.mapkit import rom
from tools.mapkit.sh2_interpreter import MASK, RETURN, STACK_TOP, sext
from tools.mapkit.tests.test_candidate_identity_paths import PathSh2

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_ici0a_ratio_path.py"
IDENTITY_TEST = "test_ici0a_ratio_cell_path"
CONTRACT_TEST = "test_ici0a_ratio_numeric_contract"
FIXTURE_PATH = "tools/mapkit/tests/fixtures/ici0a_ratio_path.json"
FIXTURE_SHA256 = "f0a426256e74aa0ea6ec43a37459b14338b0608be2ad6f66db2521c45eff1199"
SPEC = "defs/JK08A.ici0a-ratio.md"
IMAGE_SHA256 = {
    "JK00A": "ed0941de8435d9c61ac093a293757b93ad81bd413270a348c44a8fb6b78b6118",
    "JK03A": "f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4",
    "JK03B": "a9aa7a337375b7c9419b0970c32674e98f12ea4215c079898190c5c771a96f1a",
    "JK08A": "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23",
}
ENTRY, VECTOR = 0x28EA2, 0x20154
BASE, CELL, GATE = 0xFFFF128C, 0xFFFF196C, 0xFFFF8505
BASE_LOAD, BASE_POOL, GATE_LOAD, GATE_POOL = 0x28F06, 0x29020, 0x2904A, 0x2914A
WRITER, READER, DIVIDER = 0x290CC, 0x2927C, 0x21BBC
WRITE_OFFSET, READ_OFFSET = 0x29150, 0x2938E
THRESHOLD_POOL, THRESHOLD_ADDRESS, THRESHOLD = 0x2945C, 0x8C89, 118
START, WRITTEN_STOP, SKIP_STOP = 0x2909A, 0x290CE, 0x2911C
READ_START, READ_STOP, READ_SKIP = 0x29272, 0x29286, 0x292EC
MACH_GUARD, MACL_GUARD, GBR_GUARD = 0x87654321, 0xA5B6C7D8, 0xF2345678
DOMAIN_BOUNDARIES = (0, 1, 2, 63, 64, 65, 127, 128, 255, 256, 32767, 32768, 65534, 65535)


def _fixture() -> dict:
    raw = (ROOT / FIXTURE_PATH).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "retained fixture identity"
    result = json.loads(raw)
    assert result["schema"] == 1
    assert result["entry_anchor"] == {"address": "00020154", "value": "00028ea2"}
    assert {n: f["sha256"] for n, f in result["images"].items()} == IMAGE_SHA256
    assert {key: result[key] for key in ("cell", "base", "writer", "reader", "divider", "threshold_address", "threshold")} == {
        "cell": "ffff196c", "base": "ffff128c", "writer": "000290cc", "reader": "0002927c",
        "divider": "00021bbc", "threshold_address": "00008c89", "threshold": 118,
    }
    return result


FIXTURE = _fixture()


def _ranges(name: str, executed: bool = False) -> tuple[tuple[int, int], ...]:
    if executed:
        return tuple((int(a, 16), int(b, 16)) for a, b in FIXTURE["images"][name]["execution_windows"])
    return tuple((int(s["address"], 16), int(s["address"], 16) + len(bytes.fromhex(s["hex"])))
                 for s in FIXTURE["images"][name]["spans"])


def _bind(data: bytes, name: str, *, image_hash: bool = True) -> None:
    if image_hash:
        assert hashlib.sha256(data).hexdigest() == IMAGE_SHA256[name], "full image identity"
    spans = _ranges(name)
    for a, b in _ranges(name, True):
        assert a % 2 == b % 2 == 0 and 0 <= a < b <= len(data)
        assert all(any(lo <= pc and pc + 2 <= hi for lo, hi in spans)
                   for pc in range(a, b, 2)), "execution-window retention"
    for span in FIXTURE["images"][name]["spans"]:
        at, expected = int(span["address"], 16), bytes.fromhex(span["hex"])
        assert data[at:at + len(expected)] == expected, f"retained span {at:08x}"


@pytest.fixture(scope="module", params=tuple(IMAGE_SHA256))
def image(request):
    name = request.param
    data = rom.load(name).data
    _bind(data, name)
    return name, data


def _word(data: bytes, at: int) -> int:
    return int.from_bytes(data[at:at + 2], "big")


def _patch(data: bytes, at: int, replacement: int | bytes) -> bytes:
    value = replacement.to_bytes(2, "big") if isinstance(replacement, int) else replacement
    result = bytearray(data)
    result[at:at + len(value)] = value
    return bytes(result)


def _pc_literal(data: bytes, pc: int, width: int, register: int) -> int:
    opcode = _word(data, pc)
    assert opcode >> 12 == (0xD if width == 4 else 0x9)
    assert (opcode >> 8) & 15 == register
    return ((pc & ~3) if width == 4 else pc) + 4 + (opcode & 255) * width


class Context:
    """Input/write/trace manifests without interpreter extensions."""

    def __init__(self, name: str, data: bytes):
        self.name, self.m = name, PathSh2(data)
        self.known = set(self.m.ram)
        self.inputs = [(STACK_TOP - 4, 20, "PathSh2 constructor stack context")]
        self.windows = []
        self.guards = {}
        self.pc_ranges, self.rom_ranges = _ranges(name, True), _ranges(name)
        self.m.mach, self.m.macl, self.m.gbr = MACH_GUARD, MACL_GUARD, GBR_GUARD
        for at, value in ((STACK_TOP - 0x20, 0xA5), (STACK_TOP + 0x20, 0x5A),
                          (CELL - 1, 0xA5), (CELL + 1, 0x5A),
                          (GATE - 1, 0xA5), (GATE + 1, 0x5A)):
            self.guard(at, value)

    def seed(self, at: int, value: bytes, role: str) -> None:
        assert role
        self.m.seed(at, value)
        self.known.update(range(at, at + len(value)))
        self.inputs.append((at, len(value), role))

    def guard(self, at: int, value: int) -> None:
        self.seed(at, bytes([value]), "neighbor guard")
        self.guards[at] = value

    def closure(self) -> None:
        m = self.m
        assert m.unset is None
        assert all(any(a <= pc and pc + 2 <= b for a, b in self.pc_ranges)
                   for pc in m.executed), "executed-PC closure"
        assert all(any(a <= at and at + n <= b for a, b in self.rom_ranges)
                   for _, at, n in m.loads if at < len(m.data)), "ROM-load closure"
        assert set(m.ram) == self.known | m.written(), "RAM cells outside input/write manifest"
        assert all(m.peek(at) == value for at, value in self.guards.items()), "neighbor guards"
        assert all(m.data[pc] >> 4 != 0xF for pc in m.executed), "FPU outside declared integer windows"
        assert 0x2A2BA not in m.executed and 0x29588 != ENTRY, "no RTE or false entry execution"

    def run(self, start: int, stops: tuple[int, ...], writes=()) -> int:
        m = self.m
        loads, stores = len(m.loads), len(m.stores)
        incoming = self.known | m.written()
        allowed = frozenset(writes)
        self.windows.append((start, stops, tuple(m.r), m.pr, m.gbr, m.mach, m.macl,
                             m.t, tuple(self.inputs), incoming.copy(), allowed))
        assert all(0 <= value <= MASK for value in m.r)
        actual = m.run(start, stops, limit=512)
        assert actual in stops, "execution exits declared window"
        new_stores = m.stores[stores:]
        produced = {at + offset for _, at, size, _ in new_stores for offset in range(size)}
        assert produced <= allowed, "allowed writes"
        # Divider stack accesses may revisit PCs; chronological read validity
        # is enforced by the unchanged fail-closed interpreter itself. This
        # union contract additionally excludes every undeclared memory cell.
        assert all(set(range(at, at + n)) <= incoming | produced
                   for _, at, n in m.loads[loads:] if at >= len(m.data)), "incoming RAM manifest"
        self.closure()
        return actual


def _bases(c: Context) -> None:
    c.run(BASE_LOAD, (BASE_LOAD + 2,))
    assert c.m.r[8] == BASE and (BASE_LOAD, BASE_POOL, 4) in c.m.loads, "actual R8 base literal"
    c.run(GATE_LOAD, (GATE_LOAD + 2,))
    assert c.m.r[14] == 0xFFFF84FB and (GATE_LOAD, GATE_POOL, 2) in c.m.loads, "actual sign-extended R14 base literal"


def _producer(c: Context, previous: int, current: int, *, gate: int = 0x80,
              retained: int = 91, mode: int = 0, upper_previous: int = 0,
              upper_current: int = 0) -> int:
    assert 0 <= previous <= 65535 and 0 <= current <= 65535
    assert 0 <= gate <= 255 and 0 <= retained <= 255 and 0 <= mode <= 255
    assert upper_previous & 0xFFFF == upper_current & 0xFFFF == 0
    m = c.m
    m.r[12], m.r[13] = upper_previous | previous, upper_current | current
    m.r[4] = mode  # Independent incoming byte mode used only by the skip tail.
    c.seed(GATE, bytes([gate]), "incoming gate byte and unrelated bits")
    c.seed(CELL, bytes([retained]), "incoming previous ratio cell for retain branch, not computed output")
    _bases(c)
    initial_sp, initial_r3, initial_r4 = m.r[15], m.r[3], m.r[4]
    first_load, first_store, first_pc = len(m.loads), len(m.stores), len(m.executed)
    allowed = {CELL, GATE} | set(range(initial_sp - 12, initial_sp)) | set(range(initial_sp + 8, initial_sp + 12))
    reached = c.run(START, (WRITTEN_STOP, SKIP_STOP), allowed)
    executed, loads, stores = m.executed[first_pc:], m.loads[first_load:], m.stores[first_store:]
    assert (0x2909A, GATE, 1) in loads, "actual gate byte load"
    assert 0x2909E in executed and 0x290A0 in executed, "gate branch and real delay slot"
    assert m.r[15] == initial_sp, "divider stack restore"
    assert m.mach == MACH_GUARD and m.macl == MACL_GUARD and m.gbr == GBR_GUARD
    if not gate & 0x80:
        assert reached == SKIP_STOP and WRITER not in executed and DIVIDER not in executed
        assert m.peek(CELL) == retained and not m.stored(CELL), "gate-clear cell retention"
        expected_gate = gate | 0x80 if mode >= 2 else gate
        assert m.peek(GATE) == expected_gate, "skip-tail gate arming relation"
        assert [(pc, at, n, value) for pc, at, n, value in stores if at == GATE] == (
            [(0x2911A, GATE, 1, expected_gate)] if mode >= 2 else [])
        return retained
    assert reached == WRITTEN_STOP
    assert m.peek(GATE) == gate and not m.stored(GATE), "producer preserves gate and unrelated bits"
    expected = 255 if current == 0 else min(255, 64 * previous // current)
    assert m.peek(CELL) == expected, "saturated previous/current integer ratio"
    assert (WRITER, CELL, 1, expected) in stores, "actual writer location and byte width"
    assert (0x290CA, WRITE_OFFSET, 2) in loads, "actual writer offset literal"
    assert len([item for item in stores if item[1] == CELL]) == 1
    if current == 0:
        assert DIVIDER not in executed and 0x290BC in executed and 0x290BE in executed
        assert not any(pc == 0x290AE for pc, _, _, _ in stores)
        assert not any(DIVIDER <= pc < 0x21CD6 for pc, _, _ in loads), "zero current bypasses divider"
    else:
        assert all(pc in executed for pc in (0x290AC, 0x290B0, 0x290B4, 0x290B6, 0x290B8, 0x290BA))
        assert (0x290AA, 0x29228, 4) in loads, "real divider target literal"
        assert (0x290AE, initial_sp + 8, 4, current) in stores
        assert DIVIDER in executed and m.pr == 0x290B8
        assert m.r[3] == initial_r3 and m.r[4] == initial_r4, "divider preserves incoming R3/R4"
        actual_return = 0x21C04 if 64 * previous < current * 256 else 0x21C6C
        assert actual_return in executed and actual_return + 2 in executed, "actual divider return/delay slot"
        assert (0x290C8 in executed) == (64 * previous // current > 255), "strict unsigned clamp outcome"
        assert not any(at == CELL for pc, at, _ in loads if DIVIDER <= pc < 0x21CD6), "divider does not read ratio RAM"
        assert not any(at >= 0xFFFF0000 for pc, at, _ in loads if DIVIDER <= pc < 0x21CD6)
    assert m.r[8] == BASE and m.r[14] == 0xFFFF84FB
    return expected


def _reader(c: Context, value: int, status: int = 0) -> int | None:
    assert 0 <= status <= 255 and 0 <= value <= 255
    m = c.m
    m.r[0] = status  # Independent reader-entry status, not a ratio value seed.
    first_load, first_store = len(m.loads), len(m.stores)
    reached = c.run(READ_START, (READ_STOP, READ_SKIP))
    loads = m.loads[first_load:]
    assert not m.stores[first_store:], "reader writes no RAM"
    if status & 0x80:
        assert reached == READ_SKIP and not loads and READER not in m.executed[-3:], "reader status skip"
        return None
    assert reached == READ_STOP
    assert loads == [(0x29278, READ_OFFSET, 2), (0x2927A, THRESHOLD_POOL, 4),
                     (READER, CELL, 1), (0x2927E, THRESHOLD_ADDRESS, 1)], "actual reader and threshold widths/addresses"
    assert (m.r[5], m.r[4]) == (value, THRESHOLD), "reader unsigned operands"
    assert m.t == int(value > THRESHOLD), "strict reader threshold relation"
    assert m.peek(CELL) == value
    return m.t


def _static(data: bytes) -> None:
    assert int.from_bytes(data[VECTOR:VECTOR + 4], "big") == ENTRY, "actual vector anchor"
    assert int.from_bytes(data[0x970:0x974], "big") == 0x29588 and VECTOR != 0x970
    assert _pc_literal(data, BASE_LOAD, 4, 8) == BASE_POOL
    assert int.from_bytes(data[BASE_POOL:BASE_POOL + 4], "big") == BASE
    assert _pc_literal(data, GATE_LOAD, 2, 14) == GATE_POOL
    assert sext(_word(data, GATE_POOL), 16) & MASK == 0xFFFF84FB
    assert _pc_literal(data, 0x290CA, 2, 0) == WRITE_OFFSET
    assert _pc_literal(data, 0x29278, 2, 0) == READ_OFFSET
    assert _word(data, WRITE_OFFSET) == _word(data, READ_OFFSET) == CELL - BASE == 0x6E0
    assert _word(data, WRITER) == 0x0824 and _word(data, READER) == 0x058C
    assert _word(data, 0x290B6) == 0x4108 and data[THRESHOLD_ADDRESS] == THRESHOLD
    assert _pc_literal(data, 0x2927A, 4, 7) == THRESHOLD_POOL
    assert int.from_bytes(data[THRESHOLD_POOL:THRESHOLD_POOL + 4], "big") == THRESHOLD_ADDRESS
    pushes = tuple(_word(data, ENTRY + i * 2) for i in range(18))
    assert pushes == (*tuple(0x2F06 + i * 0x10 for i in range(15)), 0x4F22, 0x4F12, 0x4F13)
    assert _word(data, 0x28ECA) == 0x7FE4 and 18 * 4 + 0x1C == 0x64, "static software frame geometry"
    tail = (0x7F1C, 0x4F17, 0x4F16, 0x4F26, *tuple(0x6EF6 - i * 0x100 for i in range(15)), 0x002B, 0x0009)
    assert tuple(_word(data, 0x2A294 + i * 2) for i in range(21)) == tail, "static borrowed-frame restore and RTE, not execution"
    assert _word(data, 0x29586) == 0x2228 and _word(data, 0x29588) == 0x8B0C
    assert 0x29588 + 4 + sext(_word(data, 0x29588) & 255, 8) * 2 == 0x295A4


def test_ici0a_ratio_cell_path(image) -> None:
    """Future identity evidence for the byte cell and action sites, not L0 ownership."""
    name, data = image
    _static(data)
    assert_ici0a_ratio_specification((ROOT / SPEC).read_text())
    for previous, current in ((0, 0), (0, 1), (1, 1), (1, 2), (118, 64), (119, 64),
                              (255, 64), (256, 64), (65535, 1), (65535, 65535)):
        c = Context(name, data)
        value = _producer(c, previous, current)
        _reader(c, value)
        assert c.m.stored(CELL) == [(WRITER, 1, value)]
    c = Context(name, data)
    assert _producer(c, 1, 1, gate=0, retained=203) == 203
    assert _reader(c, 203) == 1


def test_ici0a_ratio_numeric_contract(image) -> None:
    """Bounded fixed-point ratio for declared incoming unsigned interval operands."""
    name, data = image
    cases = list(product(DOMAIN_BOUNDARIES, repeat=2))
    rng = random.Random(0x28EA2)
    cases += [(rng.randrange(65536), rng.randrange(1, 65536)) for _ in range(192)]
    returns = set()
    for previous, current in cases:
        c = Context(name, data)
        value = _producer(c, previous, current)
        assert value == (255 if current == 0 else min(255, 64 * previous // current))
        _reader(c, value)
        returns.update(pc for pc in c.m.executed if pc in (0x21C04, 0x21C6C))
    assert returns == {0x21C04, 0x21C6C}


def test_every_produced_byte_reaches_unsigned_reader_threshold(image) -> None:
    name, data = image
    for byte in range(256):
        c = Context(name, data)
        assert _producer(c, byte, 64) == byte
        assert _reader(c, byte) == int(byte > 118)


def test_every_gate_byte_preserves_unrelated_bits_and_retains_cell(image) -> None:
    name, data = image
    for gate in range(256):
        for mode in (0, 1, 2, 255):
            c = Context(name, data)
            value = _producer(c, 37, 64, gate=gate, retained=203, mode=mode)
            assert value == (37 if gate & 0x80 else 203)
            assert c.m.peek(GATE) & 0x7F == gate & 0x7F


def test_every_independent_reader_status_byte(image) -> None:
    name, data = image
    for status in range(256):
        c = Context(name, data)
        byte = _producer(c, 128, 64)
        assert _reader(c, byte, status) == (None if status & 0x80 else 1)


@pytest.mark.parametrize("upper", (0, 0x00010000, 0x7FFF0000, 0x80000000, 0xFFFF0000))
def test_unsigned_interval_width_discards_independent_upper_bits(image, upper: int) -> None:
    name, data = image
    for previous, current in ((0, 1), (1, 1), (127, 128), (32767, 32768), (65535, 65535)):
        c = Context(name, data)
        byte = _producer(c, previous, current, upper_previous=upper, upper_current=upper)
        assert byte == min(255, 64 * previous // current)
        _reader(c, byte)


def test_fragment_branch_consumes_live_preceding_tst_not_a_new_entry(image) -> None:
    name, data = image
    for flag in (0, 1, 127, 128, 255):
        c = Context(name, data)
        c.seed(BASE + 0x146, bytes([flag]), "independent fragment branch source byte")
        _bases(c)
        result = c.run(0x29582, (0x2958A, 0x295A4))
        assert (0x29584, BASE + 0x146, 1) in c.m.loads
        assert all(pc in c.m.executed for pc in (0x29582, 0x29584, 0x29586, 0x29588))
        assert result == (0x295A4 if flag else 0x2958A)
        assert not c.m.stores and c.m.r[15] == STACK_TOP
        assert 0x2A2BA not in c.m.executed


def test_binding_refuses_every_retained_span_and_full_image_change(image) -> None:
    name, data = image
    for span in FIXTURE["images"][name]["spans"]:
        at, size = int(span["address"], 16), len(bytes.fromhex(span["hex"]))
        for point in (at, at + size - 1):
            with pytest.raises(AssertionError, match="retained span"):
                _bind(_patch(data, point, bytes([data[point] ^ 1])), name, image_hash=False)
    with pytest.raises(AssertionError, match="full image identity"):
        _bind(_patch(data, len(data) - 1, bytes([data[-1] ^ 1])), name)


@contextmanager
def _executed_rejection(c: Context, at: int):
    """Require the changed instruction to execute without binding as the failure."""
    with pytest.raises(AssertionError) as failure:
        yield
    assert at in c.m.executed, "mutant must execute, not fail binding"
    message = str(failure.value).lower()
    assert not any(token in message for token in ("opcode", "unsupported", "step limit", "execution limit", "retained span", "full image identity")), "semantic mutant cannot pass via unsupported runner or snapshot refusal"


@pytest.mark.parametrize("mutation", ("gate-arm", "gate-width", "previous-width", "current-width", "delay-shift", "writer-width", "writer-offset", "clamp-boundary", "zero-value"))
def test_supported_producer_mutants_execute_without_binding(image, mutation: str) -> None:
    name, data = image
    previous, current, gate = 255, 64, 0x80
    upper_previous = upper_current = 0
    patch_at = None
    if mutation == "gate-arm":
        at, replacement = 0x2909C, 0xC840
    elif mutation == "gate-width":
        at, replacement = 0x2909A, 0x85EA
    elif mutation == "previous-width":
        at, replacement = 0x290A8, 0x61CC
        previous = 256
    elif mutation == "current-width":
        at, replacement = 0x290A2, 0x67DC
        previous, current = 128, 256
    elif mutation == "delay-shift":
        at, replacement = 0x290B6, 0x0009
        previous, current = 3, 64
    elif mutation == "writer-width":
        at, replacement = WRITER, 0x0825
    elif mutation == "writer-offset":
        at, patch_at, replacement = 0x290CA, WRITE_OFFSET, b"\x06\xe1"
    elif mutation == "clamp-boundary":
        at, replacement = 0x290C4, 0x3262
    else:
        at, replacement = 0x290BC, 0xE600
        previous, current = 1, 0
    changed = _patch(data, patch_at if patch_at is not None else at, replacement)
    c = Context(name, changed)
    with _executed_rejection(c, at):
        _producer(c, previous, current, gate=gate, upper_previous=upper_previous, upper_current=upper_current)


@pytest.mark.parametrize("mutation", ("status-bit", "source-offset", "load-width", "unsigned-extension", "threshold-literal", "strict-compare"))
def test_supported_reader_mutants_execute_without_binding(image, mutation: str) -> None:
    name, data = image
    value, status, patch_at = 128, 0, None
    if mutation == "status-bit":
        at, replacement, status = 0x29274, 0xC840, 64
    elif mutation == "source-offset":
        at, patch_at, replacement = 0x29278, READ_OFFSET, b"\x06\xe1"
    elif mutation == "load-width":
        at, replacement = READER, 0x058D
    elif mutation == "unsigned-extension":
        at, replacement = 0x29280, 0x655E
    elif mutation == "threshold-literal":
        at, patch_at, replacement = 0x2927A, THRESHOLD_POOL, (THRESHOLD_ADDRESS + 1).to_bytes(4, "big")
    else:
        at, replacement, value = 0x29284, 0x3543, 118
    c = Context(name, _patch(data, patch_at if patch_at is not None else at, replacement))
    byte = _producer(c, value, 64)
    with _executed_rejection(c, at):
        _reader(c, byte, status)


@pytest.mark.parametrize("mutation", ("dividend-shift", "result-transfer", "divider-return-delay", "divider-threshold"))
def test_supported_divider_flow_mutants_execute_without_binding(image, mutation: str) -> None:
    name, data = image
    previous, current = 1, 1
    if mutation == "dividend-shift":
        at, replacement = 0x290AC, 0x4101
    elif mutation == "result-transfer":
        at, replacement = 0x290BA, 0xE200
    elif mutation == "divider-return-delay":
        at, replacement = 0x21C06, 0x0009
    else:
        at, replacement = 0x21BE2, 0x3012
        previous, current = 4, 1
    c = Context(name, _patch(data, at, replacement))
    with _executed_rejection(c, at):
        _producer(c, previous, current)


def test_fail_closed_missing_inputs_and_trace_manifest(image) -> None:
    name, data = image
    c = Context(name, data)
    _bases(c)
    with pytest.raises(AssertionError, match="unset cell"):
        c.m.run(START, (WRITTEN_STOP, SKIP_STOP))
    c = Context(name, _patch(data, START, 0xFFFF))
    _bases(c)
    with pytest.raises(AssertionError, match="opcode ffff"):
        c.m.run(START, (WRITTEN_STOP, SKIP_STOP))
    # Explicit runner-boundary checks are not semantic mutant evidence.
    c = Context(name, data)
    c.m.executed.append(CELL)
    with pytest.raises(AssertionError, match="executed-PC closure"):
        c.closure()
    c = Context(name, data)
    c.m.loads.append((WRITER, 0, 1))
    with pytest.raises(AssertionError, match="ROM-load closure"):
        c.closure()
    c = Context(name, data)
    c.m.seed(0xFFFF0000, b"\x00")
    with pytest.raises(AssertionError, match="RAM cells outside"):
        c.closure()
    c = Context(name, data)
    c.m.seed(CELL + 1, b"\x00")
    with pytest.raises(AssertionError, match="neighbor guards"):
        c.closure()
    c = Context(name, data)
    with pytest.raises(AssertionError, match="store into the image"):
        c.m._write(VECTOR, 4, ENTRY, WRITER)


def assert_ici0a_ratio_specification(text: str) -> None:
    normalized = " ".join(text.split())
    for key in (IDENTITY_TEST, CONTRACT_TEST):
        assert f"{THIS_TEST}#{key}" in normalized, "named proof declaration"
    assert FIXTURE_PATH in normalized
    required = (
        "JK00A, JK03A, JK03B, and JK08A retain separate exact-image SHA-256 bindings",
        "ROM32[00020154] = 00028ea2 is the entry anchor",
        "ROM32[00000970] = 00029588 is not used as this ISR vector anchor",
        "Live TST at `00029586` controls BF at `00029588`",
        "The fragment borrows the software frame of `00028ea2`",
        "static software frame is 0x64 bytes", "The restore tail at `0002a294` ends in RTE at `0002a2ba`",
        "No prologue, restore tail, or RTE is executed",
        "R8 loads `ffff128c` at `00028f06` from `00029020`",
        "R14 loads sign-extended `ffff84fb` at `0002904a` from `0002914a`",
        "ROM16[00029150] = ROM16[0002938e] = 06e0", "ffff128c + 06e0 = ffff196c",
        "MOV.B writer at `000290cc`", "MOV.B reader at `0002927c`",
        "R12 previous and R13 current are independent incoming unsigned 16-bit operands",
        "The gate byte at `ffff8505` is an independent input",
        "The reader's incoming R0 status is independent",
        "byte = retained if gate bit 7 is clear", "byte = 255 if current == 0",
        "byte = min(255, floor(64 * previous / current)) otherwise",
        "The JSR delay slot at `000290b6` executes the third SHLL2",
        "The real divider at `00021bbc` executes in place and returns to `000290b8`",
        "Zero current bypasses the divider", "The divider does not read the ratio cell",
        "Producer execution begins at `0002909a` and stops at `000290ce` or `0002911c`",
        "Reader execution begins at `00029272` and stops at `00029286` or `000292ec`",
        "ROM8[00008c89] = 118", "The reader compares unsigned byte > 118",
        "The following maximum/minimum state-store paths are excluded",
        "The unchanged PathSh2", "no opcode extensions, stubs, relocations, or computed output seeds",
        "Binding refusal, unsupported instructions, and step limits are not semantic passes",
        "The test does not certify tracked function ownership or accepted L0",
        "full ISR", "physical tooth", "crank degree", "measuring producer", "every-tooth runtime",
        "hardware eligibility", "Software gates do not grant flashing approval",
    )
    for phrase in required:
        assert phrase in normalized, f"published boundary: {phrase}"
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body if isinstance(node, ast.FunctionDef)}
    assert {IDENTITY_TEST, CONTRACT_TEST} <= functions


def test_ici0a_specification_is_a_bounded_standalone_claim() -> None:
    assert_ici0a_ratio_specification((ROOT / SPEC).read_text())


@pytest.mark.parametrize("before,after", (
    ("ROM32[00020154] = 00028ea2", "ROM32[00000970] = 00029588"),
    ("ffff128c + 06e0 = ffff196c", "ffff128c + 06e0 = ffff196e"),
    ("MOV.B writer", "MOV.W writer"),
    ("third SHLL2", "second SHLL2"),
    ("byte = retained if gate bit 7 is clear", "byte = 0 if gate bit 7 is clear"),
    ("floor(64 * previous / current)", "floor(16 * previous / current)"),
    ("byte = 255 if current == 0", "byte = 0 if current == 0"),
    ("unsigned byte > 118", "signed byte >= 118"),
    ("No prologue, restore tail, or RTE is executed", "The complete ISR is executed"),
    ("does not certify tracked function ownership", "certifies tracked function ownership"),
    ("Software gates do not grant flashing approval", "Software gates grant flashing approval"),
))
def test_ici0a_specification_refuses_prose_mutants(before: str, after: str) -> None:
    text = " ".join((ROOT / SPEC).read_text().split())
    assert before in text
    with pytest.raises(AssertionError, match="published boundary"):
        assert_ici0a_ratio_specification(text.replace(before, after, 1))
