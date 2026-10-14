"""Conditional nominal encoded-temperature grid, not physical coolant accuracy.

Retained image, byte and community-decoder expectations are independent of the
ROM under test. PathSh2 is unchanged. Independent windows have explicit incoming
operands and fail-closed PC, ROM-read, RAM-read, write and guard contracts. FPU,
ADC, scheduler, fail-safe, parser/transport and hardware behavior are excluded.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
from copy import deepcopy
import csv
import hashlib
import json
from pathlib import Path
import re
import tomllib

import pytest

from tools.mapkit import rom
from tools.mapkit.sh2_interpreter import MASK, RETURN, STACK_TOP, sext
from tools.mapkit.tests.test_candidate_identity_paths import PathSh2

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_vvel_cold_axis_scale.py"
TEST_KEY = "test_vvel_cold_axis_pid05_code_domain"
SPEC = "defs/VQ37.cold-axis-scale.md"
FIXTURE_PATH = "tools/mapkit/tests/fixtures/vvel_cold_axis_pid05.json"
FIXTURE_SHA256 = "cfa7faca6ac0c2b01fb6bd2bd92593d5938d6b2ffcaa21db5df7c893ef08ac61"
IMAGE_FIXTURES = {
    "JK78C": "86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d",
    "1ND0A": "650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978",
    "1ND3B": "0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e",
    "1ME3B": "f905b78901b4ca96002a31c2fca8f1cd00dee57b02bea1921a341caa6db2a6f3",
}
STOCK_AXIS = (20, 30, 40, 50, 60, 70, 80, 90)
NOMINAL_AXIS = (-30, -20, -10, 0, 10, 20, 30, 40)
WORD_INPUTS = (0, 3, 4, 1023, 1024, 1027, 65535)
ARITHMETIC_INPUTS = (9, 10, 11)
NORMAL_INPUTS = tuple((q, old) for q in (3, 100, 200, 220, 230, 239, 241)
                      for old in (0, 20, 90, 255)) + ((220, 42), (220, 43), (220, 44))
OVERRIDE_INPUTS = tuple(range(256))  # Service operands, not physical reachability.
MACL_GUARD, MACH_GUARD = 0xA5B6C7D8, 0x87654321

JK = dict(layout="jk78c", table=0x141E8, kernel=0x281C8, word=0xFFFF1CEE,
          q=0xFFFF1172, transfer=0xFFFF1173, published=0xFFFF106F,
          old=0xFFFF1075, coordinate=0xFFFF1069, axis=0x16AC4,
          service=0xFFFF98F8, override=0xFFFF9858, flag=0xFFFF23C1,
          coordinator=0x3CADC, publish_stop=0x3CC42, fail_entry=0x3CBC0,
          word_start=0x3CB6C, word_stop=RETURN, word_read=0x3CB74,
          q_store=0x3CB7E, transfer_store=0x3CB9C, rom_flag=0x896B,
          rise=0x3CBBA, fall=0x3CBB8, p_store=0x3CB1C,
          producer=0xA2700, producer_stop=RETURN, slice=0xA2710,
          pid=0xFFFF44BA, pid_read=0xA2708, pid_store=0xA2724,
          selected=0x3907C, selected_stop=0x39384, selected_miss=0x390A4,
          response=0xFFFF3D11, cursor=0xFFFF4294,
          response_store=0x3AF2A, cursor_store=0x3AF34, selected_read=0x39088,
          table_reads=(0x288D4, 0x288D6), endpoint_read=0x281DA,
          copy_read=0x225CE, copy_store=0x225D8,
          caller_read=0x5547E, caller_store=0x55484,
          argument_read=0x56536, frame_entry=0x564A4, frame=0x70,
          argument_literal=0x5661E, argument_offset=0xB4,
          reader_call=0x566F4, reader=0x56A14, wrapper=0x282F4)
ND = dict(layout="1nd", table=0x1468E, kernel=0x287E4, word=0xFFFE8D74,
          q=0xFFFE817A, transfer=0xFFFE817B, published=0xFFFE8079,
          old=0xFFFE807F, coordinate=0xFFFE8073, axis=0x170D2,
          service=0xFFFEEBD8, override=0xFFFEEB38, flag=0xFFFE9483,
          coordinator=0x40188, publish_stop=0x4034C, fail_entry=0x402D2,
          word_start=0x40188, word_stop=0x401BE, word_read=0x40196,
          q_store=0x401A2, transfer_store=0x401BC, rom_flag=0x8A31,
          rise=0x401FA, fall=0x401F4, p_store=0x40218,
          producer=0xBF62C, producer_stop=0xBF64C, slice=0xBF63C,
          pid=0xFFFEB7CA, pid_read=0xBF630, pid_store=0xBF64A,
          status=0xFFFEB797, selected=0x3BBC8, selected_stop=RETURN,
          selected_miss=0x3BBE2, response=0xFFFEAF89, cursor=0xFFFEB568,
          response_store=0x3E41E, cursor_store=0x3E42C, selected_read=0x3BBD2,
          table_reads=(0x28EF0, 0x28EF2), endpoint_read=0x287F6,
          copy_read=0x212E2, copy_store=0x212E6,
          caller_read=0x5E61C, caller_store=0x5E620,
          argument_read=0x5F506, frame_entry=0x5F468, frame=0x60,
          argument_literal=0x5F572, argument_offset=0xA0,
          reader_call=0x5E6B8, reader=0x5F468, wrapper=0x28910)
ME = dict(layout="1me3b", table=0x1451A, kernel=0x2AA98, word=0xFFFE8D18,
          q=0xFFFE8162, transfer=0xFFFE8163, published=0xFFFE8079,
          old=0xFFFE807F, coordinate=0xFFFE8073, axis=0x17176,
          service=0xFFFEEC08, override=0xFFFEEB68, flag=0xFFFE9453,
          coordinator=0x43304, publish_stop=0x434C8, fail_entry=0x4344E,
          word_start=0x43304, word_stop=0x4333A, word_read=0x43312,
          q_store=0x4331E, transfer_store=0x43338, rom_flag=0x8A82,
          rise=0x43376, fall=0x43370, p_store=0x43394,
          producer=0xC9086, producer_stop=0xC90A6, slice=0xC9096,
          pid=0xFFFEB92A, pid_read=0xC908A, pid_store=0xC90A4,
          status=0xFFFEB8F9, selected=0x3EC14, selected_stop=RETURN,
          selected_miss=0x3EC2E, response=0xFFFEB0CD, cursor=0xFFFEB6B8,
          response_store=0x4146A, cursor_store=0x41478, selected_read=0x3EC1E,
          table_reads=(0x2AAB2, 0x2AAB4), endpoint_read=0x2AAE6,
          copy_read=0x21308, copy_store=0x2130A,
          caller_read=0x62158, caller_store=0x6215C,
          argument_read=0x63000, frame_entry=0x62FAC, frame=0x60,
          argument_literal=0x630B4, argument_offset=0xA8,
          reader_call=0x62200, reader=0x62FAC, wrapper=0x2AEAC)
PROFILES = {"JK78C": JK, "1ND0A": ND, "1ND3B": ND, "1ME3B": ME}


def _fixtures() -> dict:
    raw = (ROOT / FIXTURE_PATH).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "retained fixture identity"
    result = json.loads(raw)
    assert result["schema"] == 1 and set(result["images"]) == set(IMAGE_FIXTURES)
    assert {n: f["sha256"] for n, f in result["images"].items()} == IMAGE_FIXTURES
    return result


FIXTURES = _fixtures()


def _ranges(name: str, executed: bool = False) -> tuple[tuple[int, int], ...]:
    f = FIXTURES["images"][name]
    if executed:
        return tuple((int(a, 16), int(b, 16)) for a, b in f["execution_windows"])
    return tuple((int(s["address"], 16), int(s["address"], 16) + len(bytes.fromhex(s["hex"])))
                 for s in f["spans"])


def _bind(data: bytes, name: str, *, image_hash: bool = True) -> None:
    if image_hash:
        assert hashlib.sha256(data).hexdigest() == IMAGE_FIXTURES[name], "full image identity"
    spans = _ranges(name)
    for start, end in _ranges(name, True):
        assert start % 2 == end % 2 == 0 and 0 <= start < end <= len(data)
        assert all(any(a <= pc and pc + 2 <= b for a, b in spans)
                   for pc in range(start, end, 2)), "execution-window retention"
    for s in FIXTURES["images"][name]["spans"]:
        at, expected = int(s["address"], 16), bytes.fromhex(s["hex"])
        assert data[at:at + len(expected)] == expected, f"retained span {at:08x}"


@pytest.fixture(scope="module", params=tuple(IMAGE_FIXTURES))
def image(request):
    name = request.param
    data = rom.load(name).data
    _bind(data, name)
    return name, data, PROFILES[name]


def _patch(data: bytes, at: int, value: int | bytes) -> bytes:
    replacement = value.to_bytes(2, "big") if isinstance(value, int) else value
    result = bytearray(data)
    result[at:at + len(replacement)] = replacement
    return bytes(result)


def _word(data: bytes, at: int) -> int:
    return int.from_bytes(data[at:at + 2], "big")


class Context:
    """Input/write manifest around an unchanged interpreter, not opcode handlers."""

    def __init__(self, name: str, data: bytes, p: dict):
        self.name, self.p, self.m = name, p, PathSh2(data)
        self.m.macl, self.m.mach = MACL_GUARD, MACH_GUARD
        self.known = set(range(STACK_TOP - 4, STACK_TOP + 16))  # PathSh2 constructor context.
        self.inputs = [(STACK_TOP - 4, 20, "constructor stack/return context")]
        # Constructor register zeros/RETURN are incoming operands. Subsequent
        # windows consume the state actually left by the preceding stock slices.
        self.window_inputs: list[tuple] = []
        self.guards: dict[int, int] = {}
        self.guard(STACK_TOP - 0x180, 0xA5)
        self.guard(STACK_TOP + 0x140, 0x5A)
        for a, n in ((p["q"], 2), (p["published"], 1), (p["coordinate"], 1),
                     (p["pid"], 1), (p["flag"], 1)):
            self.marker(a, n)
        if "status" in p:
            self.marker(p["status"] + 1, 1)
        self.marker(p["response"] + 5, 1)

    def seed(self, at: int, value: bytes, role: str) -> None:
        cells = set(range(at, at + len(value)))
        for cell in cells:
            self.guards.pop(cell, None)
        self.m.seed(at, value)
        self.known.update(cells)
        self.inputs.append((at, len(value), role))

    def guard(self, at: int, value: int) -> None:
        self.seed(at, bytes([value]), "neighbor guard")
        self.guards[at] = value

    def marker(self, at: int, size: int) -> None:
        self.seed(at, b"\xcc" * size, "uninitialized destination marker, not a producer output")
        self.guard(at - 1, 0xA5)
        self.guard(at + size, 0x5A)

    def incoming(self, at: int, value: bytes, role: str) -> None:
        self.seed(at, value, role)
        self.guard(at - 1, 0xA5)
        self.guard(at + len(value), 0x5A)

    def closure(self) -> None:
        m = self.m
        assert m.unset is None
        assert all(any(a <= pc and pc + 2 <= b for a, b in _ranges(self.name, True))
                   for pc in m.executed), "executed-PC closure"
        assert all(any(a <= at and at + n <= b for a, b in _ranges(self.name))
                   for _, at, n in m.loads if at < len(m.data)), "ROM-load closure"
        available = self.known | m.written()
        assert set(m.ram) == available, "RAM cells outside input/write manifest"
        assert all(set(range(at, at + n)) <= available
                   for _, at, n in m.loads if at >= len(m.data)), "incoming RAM manifest"
        assert all(m.peek(at) == value for at, value in self.guards.items()), "neighbor guards"
        assert all(m.data[pc] >> 4 != 0xF for pc in m.executed), "excluded FPU instruction"

    def run(self, start: int, stop: int, writes=(), *, stack: int = 0,
            extra_stops: tuple[int, ...] = ()) -> None:
        sp, first = self.m.r[15], len(self.m.stores)
        allowed = set(writes) | set(range(sp - stack, sp))
        self.window_inputs.append((start, stop, tuple(self.m.r), self.m.pr,
                                   self.m.gbr, self.m.macl, self.m.mach,
                                   tuple(self.inputs), frozenset(allowed)))
        assert all(0 <= r <= MASK for r in self.m.r)
        actual = self.m.run(start, (stop, *extra_stops), limit=4096)
        assert actual == stop, "execution exits declared window"
        written = {a + i for _, a, n, _ in self.m.stores[first:] for i in range(n)}
        assert written <= allowed, "allowed writes"
        self.closure()


def _stored(c: Context, pc: int, at: int, n: int, value: int) -> None:
    assert (pc, at, n, value) in c.m.stores, f"actual store {pc:08x}/{at:08x}/{n}"


def _loaded(c: Context, pc: int, at: int, n: int) -> None:
    assert (pc, at, n) in c.m.loads, f"actual load {pc:08x}/{at:08x}/{n}"


def _table(p: dict, name: str) -> tuple[int, ...]:
    at = p["table"]
    rows = [bytes.fromhex(s["hex"]) for s in FIXTURES["images"][name]["spans"]
            if int(s["address"], 16) == at]
    assert len(rows) == 1 and len(rows[0]) == 32
    return tuple(rows[0])


def _oracle(q: int, p: dict, name: str) -> int:
    values = _table(p, name)
    if q >= 248:
        return values[31]
    i, remainder = divmod(q, 8)
    left, right = values[i:i + 2]
    delta = abs(right - left) * remainder // 8
    return left + delta if right >= left else left - delta


def _kernel_reads(c: Context, q: int, begin: int = 0) -> None:
    p = c.p
    got = [(pc, at, n) for pc, at, n in c.m.loads[begin:]
           if p["table"] <= at < p["table"] + 32]
    expected = ([(p["endpoint_read"], p["table"] + 31, 1)] if q >= 248 else
                [(p["table_reads"][0], p["table"] + q // 8, 1),
                 (p["table_reads"][1], p["table"] + q // 8 + 1, 1)])
    assert got == expected, "actual transfer-table reads"


def _source_word(c: Context, w: int) -> tuple[int, int]:
    p, m = c.p, c.m
    c.incoming(p["word"], w.to_bytes(2, "big"), "incoming W, not an ADC producer")
    m.pr = RETURN  # Standalone window context, not scheduler continuation.
    begin, sp = len(m.loads), m.r[15]
    c.run(p["word_start"], p["word_stop"], range(p["q"], p["q"] + 2), stack=32)
    q, t = m.peek(p["q"]), m.peek(p["transfer"])
    _loaded(c, p["word_read"], p["word"], 2)
    _stored(c, p["q_store"], p["q"], 1, (w >> 2) & 255)
    assert q == (w >> 2) & 255 and t == _oracle(q, p, c.name)
    _stored(c, p["transfer_store"], p["transfer"], 1, t)
    assert any(at == p["rom_flag"] and n == 1 for _, at, n in m.loads[begin:])
    assert m.data[p["rom_flag"]] == 0xE0
    _kernel_reads(c, q, begin)
    call = 0x3CB8E if p is JK else 0x401B0 if p is ND else 0x4332C
    assert all(pc in m.executed for pc in (call, call + 2, call + 4)), "source call/delay/return"
    assert m.r[15] == sp - (0 if p is JK else 12)
    assert m.macl == MACL_GUARD and m.mach == MACH_GUARD
    return q, t


def _pid(c: Context, *, incoming_t: int | None = None) -> int:
    p, m = c.p, c.m
    begin = len(m.loads)
    if incoming_t is None:
        if p is JK:
            m.pr = RETURN
        else:
            m.r[4], m.r[6] = p["status"], 0  # Incoming unrelated fuel-status operands.
        start, stack = p["producer"], 16
    else:
        # These are separately declared slice inputs, not computed lookup outputs.
        assert incoming_t in ARITHMETIC_INPUTS
        m.r[0] = incoming_t
        if p is JK:
            m.r[15] = STACK_TOP - 4
            c.seed(m.r[15], RETURN.to_bytes(4, "big"), "incoming arithmetic-slice return context")
        start, stack = p["slice"], 0
    writes = {p["pid"]} | ({p["status"] + 1} if incoming_t is None and p is not JK else set())
    c.run(start, p["producer_stop"], writes, stack=stack)
    t = incoming_t if incoming_t is not None else _oracle(m.peek(p["q"]), p, c.name)
    a = m.peek(p["pid"])
    assert a == max(t - 10, 0), "PID subtraction/clipping"
    assert (p["slice"] + 8 in m.executed) == (t < 10), "actual PID clipping arm"
    _stored(c, p["pid_store"], p["pid"], 1, a)
    if incoming_t is None:
        _loaded(c, p["pid_read"], p["q"], 1)
        _kernel_reads(c, m.peek(p["q"]), begin)
        call = 0xA270C if p is JK else 0xBF638 if p is ND else 0xC9092
        assert all(pc in m.executed for pc in (call, call + 2, call + 4)), "PID call/delay/return"
        if p is not JK:
            _stored(c, p["slice"] - 10, p["status"] + 1, 1, 0)
    return a


def _wire(c: Context, a: int) -> None:
    p, m = c.p, c.m
    incoming_sp = m.r[15]
    m.r[0] = 5  # Incoming parsed PID selector; not parser or mode-dispatch execution.
    c.incoming(p["cursor"], b"\x05", "incoming response cursor")
    if p is not JK:
        m.r[15] = STACK_TOP
        c.seed(STACK_TOP + 0x10, bytes(20), "incoming selected-handler saved registers")
        c.seed(STACK_TOP + 0x18, RETURN.to_bytes(4, "big"), "incoming handler return context")
    c.run(p["selected"], p["selected_stop"], (p["response"] + 5, p["cursor"]),
          extra_stops=(p["selected_miss"],))
    _loaded(c, p["selected_read"], p["pid"], 1)
    _stored(c, p["response_store"], p["response"] + 5, 1, a)
    _stored(c, p["cursor_store"], p["cursor"], 1, 6)
    assert m.peek(p["response"] + 5) == a and m.peek(p["cursor"]) == 6
    call = 0x39086 if p is JK else p["selected"] + 0x16
    assert call in m.executed and call + 2 in m.executed
    assert m.r[15] == (incoming_sp if p is JK else STACK_TOP + 36)


def _publish(c: Context, q: int, old: int, forced: int | None = None) -> int:
    p, m = c.p, c.m
    c.incoming(p["word"], (q * 4).to_bytes(2, "big"), "incoming W")
    c.incoming(p["old"], bytes([old]), "incoming previous publication")
    c.incoming(p["service"], bytes([forced is not None]), "incoming service state")
    c.incoming(p["override"], bytes([0 if forced is None else forced]), "incoming override")
    c.seed(p["flag"], b"\xff", "incoming unrelated validity-flag bits")
    begin = len(m.loads)
    c.run(p["coordinator"], p["publish_stop"],
          (p["q"], p["transfer"], p["published"], p["flag"]), stack=32,
          extra_stops=(p["fail_entry"],))
    t, value = _oracle(q, p, c.name), m.peek(p["published"])
    assert m.peek(p["q"]) == q and m.peek(p["transfer"]) == t
    _stored(c, p["q_store"], p["q"], 1, q)
    _stored(c, p["transfer_store"], p["transfer"], 1, t)
    _kernel_reads(c, q, begin)
    if forced is not None:
        expected = forced
        assert p["rise"] not in m.executed and p["fall"] not in m.executed
    else:
        expected = t if t > old else (old if t + 2 > old else t + 2)
        arm = "rise" if t > old else ("retain" if t + 2 > old else "fall")
        observed = "fall" if p["fall"] in m.executed else ("rise" if p["rise"] in m.executed else "retain")
        assert observed == arm, "actual publication predicate arm"
    assert value == expected, "conditioned publication"
    assert m.peek(p["flag"]) == (0xBF if forced is None else 0xFF)
    if forced is None:
        _stored(c, 0x3CB14 if p is JK else 0x40200 if p is ND else 0x4337C,
                p["flag"], 1, 0xBF)
    _loaded(c, p["word_read"], p["word"], 2)
    _stored(c, p["p_store"], p["published"], 1, value)
    return value


def _invalid_source_boundary(c: Context, q: int) -> None:
    """Execute the validity decision; stop before the excluded fail-safe body."""
    p, m = c.p, c.m
    assert q < 3 or q >= 242
    c.incoming(p["word"], (q * 4).to_bytes(2, "big"), "incoming invalid source sample")
    c.incoming(p["service"], b"\0", "incoming disabled service override")
    c.run(p["coordinator"], p["fail_entry"], (p["q"], p["transfer"]), stack=32,
          extra_stops=(p["publish_stop"],))
    _stored(c, p["q_store"], p["q"], 1, q)
    _stored(c, p["transfer_store"], p["transfer"], 1, _oracle(q, p, c.name))
    assert not m.stored(p["published"]) and not m.stored(p["coordinate"])
    assert p["fail_entry"] not in m.executed
    invalid_call = 0x3CB08 if p is JK else 0x40202 if p is ND else 0x4337E
    assert invalid_call in m.executed and invalid_call + 2 in m.executed


def _copy(c: Context, value: int) -> None:
    p, m = c.p, c.m
    if p is JK:
        c.marker(0xFFFF1064, 6)
        c.seed(0xFFFF106A, b"\x11\x22\x33\x44\x55", "incoming unrelated source copy lanes")
        c.guard(0xFFFF1063, 0xA5)
        c.guard(0xFFFF1070, 0x5A)
        c.run(0x20F3C, 0x20F3E)
        c.run(0x20F58, 0x20F5A)
        assert (m.r[14], m.r[12]) == (6, 0x225C0)
        c.run(0x20F98, 0x20FA0, range(0xFFFF1064, 0xFFFF106A), stack=12)
        assert bytes(m.peek(0xFFFF1064 + i) for i in range(6)) == bytes([0x11, 0x22, 0x33, 0x44, 0x55, value])
        loads = [(at, n) for pc, at, n in m.loads if 0x225CE <= pc <= 0x225E6 and at >= 0xFFFF0000]
        assert loads == [(0xFFFF106A + i, 1) for i in range(6)]
        _stored(c, 0x225D8, p["coordinate"], 1, value)
        assert 0x20F9C in m.executed and 0x20F9E in m.executed and 0x225F6 in m.executed
    elif p is ND:
        c.marker(0xFFFE806E, 1)
        m.r[9] = 0  # Incoming unrelated destination-lane operand.
        for a, b in ((0x21264, 0x21266), (0x212C2, 0x212C6),
                     (0x212C8, 0x212CA), (0x212CC, 0x212CE)):
            c.run(a, b)
        assert (m.r[4], m.r[8]) == (0xFFFE8074, 0xFFFE806E)
        c.run(0x212E2, 0x212E8, (0xFFFE806E, p["coordinate"]))
        _stored(c, 0x212E4, 0xFFFE806E, 1, 0)
    else:
        for a in (0x212A4, 0x212AA, 0x212B0, 0x212B6, 0x212BC):
            c.run(a, a + 2)
        assert (m.r[6], m.r[13]) == (0xFFFE8074, 0xFFFE806E)
        c.run(0x21308, 0x2130C, (p["coordinate"],))
    if p is not JK:
        _loaded(c, p["copy_read"], p["published"], 1)
        _stored(c, p["copy_store"], p["coordinate"], 1, value)
    assert m.peek(p["coordinate"]) == value


ND_CALLER_INPUTS = ((0xFFFE9446, 2), (0xFFFEA568, 2), (0xFFFE81AD, 1),
                    (0xFFFE81B0, 2), (0xFFFEA448, 1), (0xFFFE80BE, 2),
                    (0xFFFE9796, 1), (0xFFFE977A, 4), (0xFFFEA734, 2),
                    (0xFFFEA784, 4), (0xFFFEA9FA, 2), (0xFFFE8070, 1))
ME_CALLER_INPUTS = ((0xFFFE9416, 2), (0xFFFEA63E, 2), (0xFFFE8195, 1),
                    (0xFFFE8198, 2), (0xFFFEB8CA, 2), (0xFFFE93DA, 2),
                    (0xFFFEA510, 1), (0xFFFE80BA, 2), (0xFFFE97A6, 4),
                    (0xFFFEA820, 2), (0xFFFEA872, 4), (0xFFFEAB22, 2),
                    (0xFFFE8215, 1), (0xFFFE8070, 1))


def _caller(c: Context, x: int) -> None:
    p, m = c.p, c.m
    initial_sp = m.r[15]
    c.seed(initial_sp, bytes(260), "incoming unrelated caller stack lanes")
    if p is JK:
        c.seed(initial_sp + 0x44, b"\x12\x34\x56\xcc", "incoming upper argument lanes and unwritten low lane")
        c.run(0x5545C, 0x5545E)
        c.run(0x5547E, 0x55486, (initial_sp + 0x47,))
        _stored(c, 0x55484, initial_sp + 0x47, 1, x)
        m.r[15] -= p["frame"]  # Explicit incoming net frame; excluded FPU prologue.
        c.run(0x56534, 0x56538)
        _loaded(c, p["argument_read"], initial_sp + 0x44, 4)
        assert m.r[8] == 0x12345600 | x
        c.run(0x566F0, 0x566F2)
        assert m.r[4] == x, "unsigned intermediate operand"
        c.run(0x56A14, 0x282F4, stack=16)
        assert (m.r[4], m.r[5], m.r[6]) == (0x16A54, p["axis"], x)
        assert 0x56A2A in m.executed and 0x56A2C in m.executed
    else:
        for at, n in ND_CALLER_INPUTS if p is ND else ME_CALLER_INPUTS:
            c.seed(at, bytes(n), "incoming unrelated caller RAM")
        if p is ME:
            c.run(0x6202E, 0x62030)
            c.run(0x62034, 0x62036)
            assert (m.r[13], m.r[14]) == (0xFFFE8070, 0xFFFE80BA)
        start = 0x5E61A if p is ND else 0x62158
        c.run(start, p["reader"], stack=0x70)
        call_sp = m.r[15]
        slot = call_sp + (0x40 if p is ND else 0x48)
        _stored(c, p["caller_store"], slot, 4, x)
        assert p["reader_call"] in m.executed and p["reader_call"] + 2 in m.executed
        m.r[15] -= p["frame"]  # Explicit net frame operand, not FPU execution.
        if p is ND:
            c.run(0x5F504, 0x5F508)
            assert m.r[11] == x, "unsigned packed argument"
            c.run(0x5F6BC, 0x5F6C0)
            assert (m.r[14], m.r[6]) == (p["axis"], x)
        else:
            c.run(0x62FFE, 0x63002)
            assert m.r[0] == 0xA8 and m.r[8] == x, "unsigned packed argument"
            local_sp = m.r[15]
            c.run(0x63036, 0x6303A, (local_sp + 0xAB,))
            _stored(c, 0x63038, local_sp + 0xAB, 1, x)
            c.run(0x631FC, 0x6320E, (local_sp + 0x28, local_sp + 0x29))
            _loaded(c, 0x631FE, local_sp + 0xAB, 1)
            _stored(c, 0x63208, local_sp + 0x28, 2, x)
            assert (m.r[5], m.r[6], m.r[4]) == (p["axis"], x, 0x170F6)
        _loaded(c, p["argument_read"], slot, 4)
    _loaded(c, p["caller_read"], p["coordinate"], 1)


def _pc_literal(data: bytes, pc: int, size: int, register: int) -> int:
    op = _word(data, pc)
    assert op >> 12 == (0xD if size == 4 else 0x9)
    assert (op >> 8) & 15 == register
    return ((pc & ~3) if size == 4 else pc) + 4 + (op & 255) * size


def _static_bindings(data: bytes, p: dict) -> None:
    at = p["frame_entry"]
    words = tuple(_word(data, at + i * 2) for i in range(15))
    assert words[:8] == (0x2F86, 0x2F96, 0x2FA6, 0x2FB6, 0x2FC6, 0x2FD6, 0x2FE6, 0x4F22)
    assert words[8:12] == (0xFFCB, 0xFFEB, 0xFFFB, 0x4F13)
    assert words[14] == (0x7FC0 if p is JK else 0x7FD0)
    assert 8 * 4 + 3 * 4 + 4 - sext(words[14] & 255, 8) == p["frame"]
    assert _word(data, p["argument_literal"]) == p["argument_offset"]
    offset_load = p["argument_read"] - 2
    assert _pc_literal(data, offset_load, 2, 0) == p["argument_literal"]
    assert _word(data, p["argument_read"]) == (0x0BFE if p is ND else 0x08FE)
    expected_slot = 0x44 if p is JK else 0x40 if p is ND else 0x48
    assert p["argument_offset"] - p["frame"] == expected_slot
    assert _word(data, p["reader_call"]) >> 12 == 0xB
    target = p["reader_call"] + 4 + sext(_word(data, p["reader_call"]) & 0xFFF, 12) * 2
    assert target == p["reader"]
    if p is JK:
        assert _pc_literal(data, 0x554AA, 4, 3) == 0x555DC
        assert int.from_bytes(data[0x555DC:0x555E0], "big") == p["frame_entry"]
        assert _word(data, 0x554AC) == 0x430B
        assert _pc_literal(data, 0x56A1C, 4, 0) == 0x56C88
        assert _pc_literal(data, 0x56A24, 4, 7) == 0x56C8C
        assert int.from_bytes(data[0x56C8C:0x56C90], "big") == p["wrapper"]
        assert _word(data, 0x566F6) >> 12 == 0xF  # Excluded call delay slot.
        assert int.from_bytes(data[0x56C88:0x56C8C], "big") + 0x70 == p["axis"]
    elif p is ND:
        assert _pc_literal(data, 0x5F6BE, 4, 14) == 0x5F7B0
        assert _pc_literal(data, 0x5F6C2, 4, 4) == 0x5F7B4
        assert _pc_literal(data, 0x5F6C4, 4, 10) == 0x5F7B8
        assert int.from_bytes(data[0x5F7B4:0x5F7B8], "big") == 0x17062
        assert int.from_bytes(data[0x5F7B0:0x5F7B4], "big") == p["axis"]
        assert int.from_bytes(data[0x5F7B8:0x5F7BC], "big") == p["wrapper"]
        assert _word(data, 0x5F6D2) == 0x4A0B
    else:
        assert _pc_literal(data, 0x63114, 4, 8) == 0x633F0
        assert int.from_bytes(data[0x63430:0x63434], "big") == p["axis"]
        assert int.from_bytes(data[0x633F0:0x633F4], "big") == p["wrapper"]
        assert _word(data, 0x63114) == 0xD8B6
        assert _word(data, 0x6320E) == 0x480B


def _decoder_records() -> dict:
    base = ROOT / "refs/diagnostics/public/370z-can-logger"
    expected = FIXTURES["source"]
    result = {"pack": tomllib.loads((base / "source_pack.toml").read_text())}
    for key, file, field, value in (
        ("document", "documents.csv", "id", expected["document"]["id"]),
        ("parameter", "diagnostic_parameters.csv", "source_fragment_id", expected["fragment"]["id"]),
        ("request", "diagnostic_requests.csv", "source_fragment_id", expected["fragment"]["id"]),
    ):
        with (base / file).open() as stream:
            found = [row for row in csv.DictReader(stream) if row[field] == value]
        assert len(found) == 1
        result[key] = found[0]
    found = [json.loads(line) for line in (base / "fragments.jsonl").read_text().splitlines()
             if json.loads(line)["id"] == expected["fragment"]["id"]]
    assert len(found) == 1
    result["fragment"] = found[0]
    result["row"] = json.loads(found[0]["text"])
    return result


def _assert_decoder(records: dict, *, digests: bool = True) -> None:
    expected = FIXTURES["source"]
    for key, fields in expected.items():
        for field, value in fields.items():
            if not digests and field in ("sha256", "text_sha256"):
                continue
            assert records[key][field] == value, f"independent decoder {key}.{field}"
    f = records["fragment"]
    assert records["row"] == json.loads(f["text"])
    if digests:
        assert hashlib.sha256(f["text"].encode()).hexdigest() == expected["fragment"]["text_sha256"]
    assert records["parameter"]["source_fragment_id"] == f["id"]
    assert records["request"]["source_fragment_id"] == f["id"]
    assert records["pack"]["source_tier"] == "community"
    assert records["parameter"]["verification_status"] == "standard_definition"
    assert records["request"]["verification_status"] == "community_reported"


def _normalized(text: str) -> str:
    return " ".join(text.split())


def assert_vvel_cold_axis_specification(text: str) -> None:
    s = _normalized(text)
    assert f"{THIS_TEST}#{TEST_KEY}" in s and FIXTURE_PATH in s
    for label, key in (("Source W", "word"), ("Stored q", "q"), ("Transfer T", "transfer"),
                       ("Transfer table", "table"), ("Transfer kernel", "kernel"),
                       ("Published P", "published"), ("Previous publication", "old"),
                       ("Coordinate x", "coordinate"), ("Stock axis", "axis"), ("PID05 A", "pid")):
        row = f"| {label} | " + " | ".join(f"`{PROFILES[n][key]:08x}`" for n in IMAGE_FIXTURES) + " |"
        assert row in s, f"published {label} bindings"
    required = (
        "eight-point big-endian `uint16` axis whose runtime coordinate is an unsigned byte",
        "20, 30, 40, 50, 60, 70, 80, and 90 display as -30..40 degC",
        "`x+50` is the inverse of that coordinate grid, not an inverse of the sensor, transfer lookup, conditioned publication, or snapshot chain",
        "conditional nominal encoded-temperature interpretation at level `code`",
        "does not establish measured coolant temperature, sensor calibration, physical accuracy, or physical reachability of every breakpoint",
        "q = (W >> 2) & 255", "A = max(T - 10, 0)", "x = snapshot(P)",
        "P = T if T > old", "P = old if T <= old and T + 2 > old", "P = T + 2 otherwise",
        "normal source-validity branch q=3..241", "`T>=10` implies `A-40=T-50`",
        "additionally requires `x=T` and corresponding samples", "Neither permits unconditional equality with a live PID",
        "not primary SAE, factory, or hardware evidence", "`community`", "`homologous_community`", "`community_reported`",
        "T=9/10/11 as independent slice operands", "JK78C `0x70`, 1ND `0x60`, and 1ME3B `0x60`",
        "1ME3B `00062ffe` argument-offset load, the coordinate load at `00063000`",
        "and the JK78C selected PID branch/helper",
        "upper endpoint at 248", "q=240/241", "T=8/7 and A=0", "old=42/43", "old=44",
        "old=90 produces P=x=44", "q=200 retains x=57", "q=220 gives A=32", "W=1023/1024 yields q=255/0",
        "sensor/ADC production and calibration", "snapshot-age bounds", "complete scheduler/interrupt behavior",
        "fail-safe runtime/timers", "startup/initialization", "FPU prologues and consumers", "complete cold lookup",
        "parser/dispatcher/transport readiness", "hardware or engine eligibility", "Software gates do not grant flashing approval",
        "Binding mutants reject each retained span", "without treating snapshot rejection as execution",
    )
    for fragment in required:
        assert fragment in s, f"published boundary: {fragment}"
    assert FIXTURES["source"]["fragment"]["id"] in s
    assert "supplies PID 05, one data byte, coolant temperature" in s
    assert "retained request record binds it to service 01 and request 0105" in s


def test_vvel_cold_axis_pid05_code_domain(image) -> None:
    name, data, p = image
    _static_bindings(data, p)
    _assert_decoder(_decoder_records())
    assert_vvel_cold_axis_specification((ROOT / SPEC).read_text())
    axis = tuple(int.from_bytes(data[p["axis"] + i:p["axis"] + i + 2], "big") for i in range(0, 16, 2))
    assert axis == STOCK_AXIS and tuple(x - 50 for x in axis) == NOMINAL_AXIS
    assert tuple(degc + 50 for degc in NOMINAL_AXIS) == axis
    for q in range(256):
        c = Context(name, data, p)
        got_q, t = _source_word(c, q * 4)
        assert got_q == q
        a = _pid(c)
        _wire(c, a)
        if t >= 10:
            assert a - 40 == t - 50
        else:
            assert a == 0 and a - 40 != t - 50
    for q in (*range(3), *range(242, 256)):
        _invalid_source_boundary(Context(name, data, p), q)
    for w in WORD_INPUTS:
        _source_word(Context(name, data, p), w)
    for t in ARITHMETIC_INPUTS:
        c = Context(name, data, p)
        assert _pid(c, incoming_t=t) == {9: 0, 10: 0, 11: 1}[t]
    arms = set()
    for q, old in NORMAL_INPUTS:
        c = Context(name, data, p)
        value = _publish(c, q, old)
        arms.add("fall" if p["fall"] in c.m.executed else "rise" if p["rise"] in c.m.executed else "retain")
        _copy(c, value)
        _caller(c, value)
    assert arms == {"rise", "retain", "fall"}
    for forced in OVERRIDE_INPUTS:
        c = Context(name, data, p)
        assert _publish(c, 200, 0, forced) == forced
        _copy(c, forced)
        _caller(c, forced)


def test_executed_clipping_hysteresis_wrap_and_independent_refresh(image) -> None:
    name, data, p = image
    for q, t in ((240, 8), (241, 7)):
        c = Context(name, data, p)
        assert _publish(c, q, 0) == t  # Accepted normal source branch, not fail-safe.
        _copy(c, t)
        assert _pid(c) == 0 and t - 50 in (-42, -43)
    c = Context(name, data, p)
    assert _publish(c, 220, 90) == 44
    _copy(c, 44)
    a = _pid(c)
    assert (c.m.peek(p["coordinate"]) - 50, a - 40) == (-6, -8)
    for old, expected_arm in ((42, "retain"), (43, "retain"), (44, "fall")):
        c = Context(name, data, p)
        assert _publish(c, 220, old) == old
        assert ("fall" if p["fall"] in c.m.executed else "retain") == expected_arm
    c = Context(name, data, p)
    assert _publish(c, 200, 0) == 57
    _copy(c, 57)
    assert _source_word(c, 220 * 4) == (220, 42)  # Later source refresh, not a new publication.
    assert _pid(c) == 32 and c.m.peek(p["coordinate"]) == 57
    _wire(c, 32)
    assert 57 - 50 != 32 - 40
    assert _source_word(Context(name, data, p), 1023)[0] == 255
    assert _source_word(Context(name, data, p), 1024)[0] == 0
    # Distinct source words share q: the nominal grid inverse is not a sensor inverse.
    assert [_source_word(Context(name, data, p), w)[0] for w in (0, 3, 1024)] == [0, 0, 0]


def test_binding_mutants_reject_every_retained_span_and_image_pin(image) -> None:
    name, data, _ = image
    for span in FIXTURES["images"][name]["spans"]:
        at, count = int(span["address"], 16), len(bytes.fromhex(span["hex"]))
        for changed in (at, at + count - 1):
            with pytest.raises(AssertionError, match="retained span"):
                _bind(_patch(data, changed, bytes([data[changed] ^ 1])), name, image_hash=False)
    with pytest.raises(AssertionError, match="full image identity"):
        _bind(_patch(data, len(data) - 1, bytes([data[-1] ^ 1])), name)


@contextmanager
def _executed_rejection(c: Context, at: int):
    # Binding rejection is tested separately. These mutants must reach the
    # mutated instruction or the instruction consuming a changed literal. Fail
    # semantics, a declared boundary, or memory, not an unsupported decoder.
    with pytest.raises(AssertionError) as failure:
        yield
    assert at in c.m.executed, "mutant must execute, not fail snapshot binding"
    message = str(failure.value).lower()
    assert "unsupported" not in message and "opcode" not in message, "mutant opcode must be supported"
    assert "step limit" not in message and "execution limit" not in message


@pytest.mark.parametrize("mutation", ("word-source", "word-width", "word-shift", "lookup-slot"))
def test_executed_source_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, p = image
    at = {"word-source": p["word_read"] - 4, "word-width": p["word_read"],
          "word-shift": 0x3CB7C if p is JK else p["word_read"] + 6,
          "lookup-slot": 0x3CB90 if p is JK else 0x401B2 if p is ND else 0x4332E}[mutation]
    if mutation == "word-source":
        value = _word(data, at) + 1  # Incoming source displacement, not a pointer snapshot.
    elif mutation == "word-width":
        value = _word(data, at) - 1  # MOV.W indexed -> MOV.B indexed.
    elif mutation == "word-shift":
        # SHAR and SHLR are equivalent after uint16 zero-extension. Removing
        # one SHAR changes the reduction; the JK78C single SHLR2 becomes SHLR.
        value = 0x4501 if p is JK else 0x0009
    else:
        value = 0xE500  # Actual lookup-call delay slot supplies zero.
    c = Context(name, _patch(data, at, value), p)
    with _executed_rejection(c, at):
        _source_word(c, 4)


@pytest.mark.parametrize("mutation", ("subtract", "clip", "pid-destination", "pid-width"))
def test_executed_pid_arithmetic_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, p = image
    at = p["slice"] + {"subtract": 2, "clip": 6, "pid-destination": 0,
                       "pid-width": p["pid_store"] - p["slice"]}[mutation]
    literal = None
    if mutation == "pid-destination":
        at = 0xA271E if p is JK else 0xBF646 if p is ND else 0xC90A0
        if p is JK:
            value = 0xE053  # MOV #83,r0 instead of #82: neighboring RAM destination.
        else:
            literal = 0xBF85C if p is ND else 0xC9138
            assert _pc_literal(data, at, 4, 4) == literal
            assert int.from_bytes(data[literal:literal + 4], "big") == p["pid"]
            # Execute the original pointer-load instruction on a changed literal,
            # not an invented null/ROM destination or a seeded producer result.
            value = (p["pid"] + 1).to_bytes(4, "big")
    elif mutation == "subtract":
        value = _word(data, at) + 1
    elif mutation == "clip":
        value = _word(data, at) ^ 0x0200  # BT -> BF.
    else:
        value = _word(data, at) + 1  # Byte -> word store.
    c = Context(name, _patch(data, literal if literal is not None else at, value), p)
    with _executed_rejection(c, at):
        _pid(c, incoming_t=9 if mutation == "clip" else 11)
    if literal is not None:
        _loaded(c, at, literal, 4)


@pytest.mark.parametrize("mutation", ("rise-equality", "retained-equality", "plus-two", "published-width", "override-source"))
def test_executed_publication_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, p = image
    sites = ((0x3CBAC, 0x3CBB4, 0x3CBB8, 0x3CB1C, 0x3CAEE) if p is JK else
             (0x401E2, 0x401EE, 0x401F4, 0x40218, 0x40210) if p is ND else
             (0x4335E, 0x4336A, 0x43370, 0x43394, 0x4338C))
    at = sites[("rise-equality", "retained-equality", "plus-two", "published-width", "override-source").index(mutation)]
    if mutation.endswith("equality"):
        value = _word(data, at) - 4  # CMP/GT -> CMP/GE for positive byte operands.
    elif mutation == "plus-two":
        value = _word(data, at) - 1
    elif mutation == "published-width":
        value = _word(data, at) + 0x0100  # MOV.B displacement -> MOV.W displacement.
    else:
        value = 0x0009  # No override load; incoming non-output register is retained.
    c = Context(name, _patch(data, at, value), p)
    with _executed_rejection(c, at):
        _publish(c, 220, 42 if mutation == "rise-equality" else 44 if mutation == "retained-equality" else 90,
                 255 if mutation == "override-source" else None)


@pytest.mark.parametrize("mutation", ("copy-source", "copy-width", "copy-lane"))
def test_executed_snapshot_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, p = image
    if p is JK:
        at = 0x225CE if mutation != "copy-lane" else 0x225D8
        value = 0x6034 if mutation == "copy-source" else 0x6026 if mutation == "copy-width" else 0x8012
    else:
        at = p["copy_read"] if mutation != "copy-lane" else p["copy_store"]
        value = _word(data, at) - 1 if mutation in ("copy-source", "copy-lane") else _word(data, at) + 0x0100
    c = Context(name, _patch(data, at, value), p)
    value = _publish(c, 200, 0)
    with _executed_rejection(c, at):
        _copy(c, value)


def test_executed_jk_copy_length_and_call_slot_mutants(image) -> None:
    name, data, p = image
    if p is not JK:
        return  # Other images use explicit byte lanes, not this block helper.
    for at, value in ((0x20F3C, 0xEE05), (0x20F9E, 0xE000)):
        c = Context(name, _patch(data, at, value), p)
        current = _publish(c, 200, 0)
        with _executed_rejection(c, at):
            _copy(c, current)


@pytest.mark.parametrize("mutation", ("caller-source", "argument-width", "unsigned-extension", "call-slot"))
def test_executed_caller_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, p = image
    if mutation == "caller-source":
        at, value = p["caller_read"], _word(data, p["caller_read"]) - 1
    elif mutation == "argument-width":
        at = p["caller_store"]
        value = _word(data, at) + 1 if p is JK else 0x2F11
    elif mutation == "unsigned-extension":
        at = 0x566F0 if p is JK else p["caller_read"] + 2
        value = 0x6483 if p is JK else (_word(data, at) & 0xFFF0) | 0xE
    else:
        at = 0x56A2C if p is JK else p["reader_call"] + 2
        value = 0xE600 if p is JK else 0x7F04
    c = Context(name, _patch(data, at, value), p)
    x = _publish(c, 200, 0, 128)
    _copy(c, x)
    with _executed_rejection(c, at):
        _caller(c, x)


@pytest.mark.parametrize("mutation", ("selector", "pid-source", "response-width", "response-slot"))
def test_executed_selected_pid_writer_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, p = image
    if mutation == "selector":
        at, value = p["selected"], 0x8806
    elif mutation == "pid-source":
        at = p["selected"] + 6
        value = _word(data, at) + 1
    elif mutation == "response-width":
        at, value = p["response_store"], _word(data, p["response_store"]) + 1
    else:
        at, value = p["cursor_store"], 0x0009
    c = Context(name, _patch(data, at, value), p)
    _source_word(c, 220 * 4)
    a = _pid(c)
    with _executed_rejection(c, at):
        _wire(c, a)


@pytest.mark.parametrize("mutation", ("formula", "quantity", "byte-width", "revision", "request", "quality"))
def test_independent_decoder_context_rejects_rehashed_mutants(mutation: str) -> None:
    records = _decoder_records()
    _assert_decoder(records)
    if mutation in ("formula", "quantity", "byte-width"):
        key = {"formula": "Formula", "quantity": "Description", "byte-width": "Bytes"}[mutation]
        records["row"][key] = {"formula": "A-50", "quantity": "Engine oil temperature", "byte-width": "2.0"}[mutation]
        records["fragment"]["text"] = json.dumps(records["row"], ensure_ascii=False)
        records["fragment"]["text_sha256"] = hashlib.sha256(records["fragment"]["text"].encode()).hexdigest()
    elif mutation == "revision":
        records["pack"]["revision"] = "0" * 40
    elif mutation == "request":
        records["request"]["service_id"] = "0x22"
    else:
        records["pack"]["source_tier"] = "factory"
    with pytest.raises(AssertionError, match="independent decoder"):
        _assert_decoder(records, digests=False)  # Semantic expectations survive bypassed digest checks.
    with pytest.raises(AssertionError):
        _assert_decoder(records)


@pytest.mark.parametrize("mutation", ("address", "physical", "unconditional", "inverse", "frame", "offset", "argument-offset", "source-quality", "exclusion"))
def test_specification_rejects_prose_mutants(mutation: str) -> None:
    text = (ROOT / SPEC).read_text()
    assert_vvel_cold_axis_specification(text)
    before, after = {
        "address": ("`ffff1069`", "`ffff1068`"),
        "physical": ("does not establish measured coolant temperature", "establishes measured coolant temperature"),
        "unconditional": ("additionally requires `x=T` and corresponding samples", "requires neither `x=T` nor corresponding samples"),
        "inverse": ("not an inverse", "an inverse"),
        "frame": ("JK78C `0x70`", "JK78C `0x60`"),
        "offset": ("A = max(T - 10, 0)", "A = max(T - 9, 0)"),
        "argument-offset": ("`00062ffe` argument-offset load", "`00062ffe` coordinate load"),
        "source-quality": ("not primary SAE, factory, or hardware evidence", "primary SAE, factory, and hardware evidence"),
        "exclusion": ("Software gates do not grant flashing approval", "Software gates grant flashing approval"),
    }[mutation]
    assert before in text
    with pytest.raises(AssertionError):
        assert_vvel_cold_axis_specification(text.replace(before, after, 1))


def test_fail_closed_memory_pc_and_write_contract(image) -> None:
    name, data, p = image
    c = Context(name, data, p)
    with pytest.raises(AssertionError, match="unset cell"):
        c.m._read(0xFFFE0000, 1, p["kernel"])
    with pytest.raises(AssertionError, match="unset cell"):
        c.m.run(p["word_start"], (p["word_stop"],))  # Actual source read with W absent.
    assert p["word_read"] in c.m.executed
    c = Context(name, _patch(data, p["word_start"], 0xFFFF), p)
    with pytest.raises(AssertionError, match="opcode ffff"):
        c.m.run(p["word_start"], (p["word_stop"],))
    # This is an interpreter fail-closed contract, not a semantic mutant pass.
    assert p["word_start"] in c.m.executed
    c = Context(name, data, p)
    with pytest.raises(AssertionError, match="store into the image"):
        c.m._write(p["axis"], 1, 0, p["kernel"])
    c.m.executed.append(p["axis"])
    with pytest.raises(AssertionError, match="executed-PC closure"):
        c.closure()
    c = Context(name, data, p)
    c.m.loads.append((p["kernel"], 0, 1))
    with pytest.raises(AssertionError, match="ROM-load closure"):
        c.closure()
    c = Context(name, data, p)
    c.m.r[4], c.m.r[5] = p["table"], 200
    c.run(p["kernel"], RETURN, stack=16)
    c.m.seed(STACK_TOP + 0x140, b"\0")
    with pytest.raises(AssertionError, match="neighbor guards"):
        c.closure()


def assert_compiled_vvel_cold_axis_owner_contract(model) -> None:
    """Integration helper: requires the actual owner batch, not synthetic evidence.

    The caller compiles committed sources and invokes this after the owner batch
    is integrated. No repository or graph state is modified. Removal of the
    named TEST item fails even when its SPEC item remains valid scale grounding.
    """
    from kb import levels, match
    from kb.model import SymbolKey

    key = SymbolKey("jk78c", "axis", JK["axis"])
    meaning = model.symbols[key].meaning
    expected = dict(unit="degC", scale="x-50", to_raw="x+50", scale_level="code",
                    level="code", points=8, storage="uint16", quantity="temp")
    assert {k: meaning.props[k] for k in expected} == expected
    assert meaning.home == "jk78c"
    assert meaning.props["editor"] == {"name": "Coolant Temperature [degC]",
                                        "format": "0", "fine": 1, "coarse": 5}
    assert {s.layout: s.address for s in meaning.symbols.values()} == {
        "jk78c": JK["axis"], "1nd": ND["axis"], "1me3b": ME["axis"]}
    functions = {n.name for n in ast.parse((ROOT / THIS_TEST).read_text()).body if isinstance(n, ast.FunctionDef)}
    assert TEST_KEY in functions

    def actual_contract(symbol) -> None:
        assert {k: symbol.value(k) for k in expected} == expected
        notes = symbol.props.get("note", "")
        notes = notes if isinstance(notes, list) else [notes]
        if symbol.layout == "1nd":
            assert len(notes) == 2 and all(note.startswith(label) for note, label in
                                          zip(notes, ("1ND0A:", "1ND3B:"))), "separate image-labelled owner notes"
        for note in notes:
            note = re.sub(r"\s*(>=|=)\s*", r"\1", _normalized(note).lower())
            for token in ("nominal encoded-temperature", "t>=10", "x=t", "corresponding samples",
                          "not a sensor inverse", "no hardware proof"):
                assert token in note, f"qualified nominal owner note {token}"
        named = [e for e in symbol.evidence if e.get("kind") == "test" and e.get("supports") == "scale"
                 and e.get("path") == THIS_TEST and e.get("key") == TEST_KEY]
        assert len(named) == 1, "actual named scale TEST item is required even with SPEC"
        specs = [e for e in symbol.evidence if e.get("kind") == "spec" and e.get("supports") == "scale"
                 and e.get("path") == SPEC]
        assert len(specs) == 1
        assert match.verify(model, symbol, named[0]) is None
        assert match.verify(model, symbol, specs[0]) is None

    for symbol in meaning.symbols.values():
        actual_contract(symbol)
        saved = deepcopy(symbol.evidence)
        try:
            symbol.evidence = [e for e in saved if not (e.get("kind") == "test" and e.get("path") == THIS_TEST)]
            assert any(e.get("kind") == "spec" and e.get("path") == SPEC for e in symbol.evidence)
            with pytest.raises(AssertionError, match="actual named scale TEST"):
                actual_contract(symbol)
            assert all(e in symbol.evidence for e in saved if e.get("supports") == "identity")
            symbol.evidence = deepcopy(saved)
            named = next(e for e in symbol.evidence if e.get("kind") == "test" and e.get("path") == THIS_TEST)
            named["key"] = "test_missing_vvel_cold_axis_scale"
            assert "defines no function" in match.verify(model, symbol, named)
            with pytest.raises(AssertionError, match="actual named scale TEST"):
                actual_contract(symbol)
        finally:
            symbol.evidence = saved
    assert not [i for i in levels.check(model, subjects={meaning.key})
                if i.subject == meaning.key and "scale" in i.message]
    assert_vvel_cold_axis_specification((ROOT / SPEC).read_text())


def test_owner_helper_ast_contract_without_live_source_integration() -> None:
    functions = {n.name for n in ast.parse((ROOT / THIS_TEST).read_text()).body if isinstance(n, ast.FunctionDef)}
    assert TEST_KEY in functions and "assert_compiled_vvel_cold_axis_owner_contract" in functions
    assert "test_missing_vvel_cold_axis_scale" not in functions
