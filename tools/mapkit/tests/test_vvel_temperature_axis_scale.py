"""Nominal selected/current encoded-temperature grids over retained stock slices.

The unchanged PathSh2 executes publications, the refresh/retain decision, copies,
argument packing and exact/end-point lookups. FPU prologues have static geometry
contracts only. Every window has explicit incoming operands and allowed writes.
No output seed, stub, relocation, opcode extension or fractional-path claim is
part of this contract. Hardware accuracy and flashing eligibility are excluded.
"""
from __future__ import annotations

import ast
from copy import deepcopy
import hashlib
from itertools import product
import json
from pathlib import Path
import re

import pytest

from tools.mapkit import rom
from tools.mapkit.sh2_interpreter import MASK, RETURN, STACK_TOP, sext
from tools.mapkit.tests import test_vvel_cold_axis_scale as cold

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_vvel_temperature_axis_scale.py"
FIXTURE_PATH = "tools/mapkit/tests/fixtures/vvel_temperature_axis_paths.json"
FIXTURE_SHA256 = "4a097e212ea6548d9730eea75320f9b5537aa8318c61d62df54f0feac43ddd8a"
SPEC = "defs/VQ37.temperature-axis-scale.md"
STARTUP_TEST = "test_vvel_duration_startup_axis_nominal_temperature"
BLEND_TEST = "test_vvel_duration_startup_blend_axis_nominal_temperature"
RAMP_TEST = "test_vvel_duration_throttled_ramp_delay_axis_nominal_temperature"
STARTUP_AXIS = tuple(range(10, 161, 10))
BLEND_AXIS = tuple(range(100, 171, 10))
RAMP_AXIS = tuple(range(20, 91, 10))
STARTUP_VALUES = (1000, 1000, *([700] * 14))
BLEND_VALUES = (1300,) * 8
RAMP_VALUES = (30, 30, 30, 30, 20, 12, 5, 0)

JK = dict(gate=0x3CC82, flag=0xFFFF44E0, flag_mask=0x40,
          threshold=0xFFFF1174, latch=0xFFFF2413, latch_mask=8,
          previous=0xFFFF1072, selected=0xFFFF106C, snapshot=0xFFFF1066,
          current_normal=0xFFFF106D, previous_normal=0xFFFF1074,
          pointer=0x3CB16, gate_call=0x3CB1E, publication_stop=0x3CB40,
          selected_load=0x3CB26, previous_load=0x3CB32, selected_store=0x3CB3C,
          compare=0x3CC98, latch_or=0x3CCAA, latch_and=0x3CCA0,
          axis=0x17204, values=0x15E32, leaf=0x28320, search=0x287AC,
          setup=0x56B78, lookup_call=0x56B7E, lookup_return=0x56B82,
          caller_read=0x55476, caller_store=0x5547C,
          packed_load=0x56544, packed_literal=0x56626, packed_offset=0xB0,
          packed_read=0x56546, packed_store=0x5654A,
          startup_entry=0x56AB4, startup_frame=0x1C,
          save=0x56AC8, request=0x56ACA, branch=0x56B42)
ND = dict(gate=0x4039E, flag=0xFFFEB7F4, flag_mask=0x10,
          threshold=0xFFFE817C, latch=0xFFFE94DA, latch_mask=2,
          previous=0xFFFE807C, selected=0xFFFE8076, snapshot=0xFFFE8070,
          current_normal=0xFFFE8077, previous_normal=0xFFFE807E,
          pointer=0x40212, gate_call=0x4021A, publication_stop=0x4023C,
          selected_load=0x4022E, previous_load=0x40224, selected_store=0x40238,
          compare=0x403AE, latch_or=0x403BA, latch_and=0x403CA,
          axis=0x17812, values=0x16440, leaf=0x2893C, search=0x28DC8,
          setup=0x5FAA8, lookup_call=0x5FAAE, lookup_return=0x5FAB2,
          caller_read=0x5E622, caller_store=0x5E626,
          packed_load=0x5F4CE, packed_literal=0x5F560, packed_offset=0x9C,
          packed_read=0x5F4D0, packed_store=0x5F502,
          startup_entry=0x5F9F0, startup_frame=0x1C,
          save=0x5FA04, request=0x5FA10, branch=0x5FA80)
ME = dict(gate=0x4351A, flag=0xFFFEB954, flag_mask=0x10,
          threshold=0xFFFE8164, latch=0xFFFE94AB, latch_mask=0x10,
          previous=0xFFFE807C, selected=0xFFFE8076, snapshot=0xFFFE8070,
          current_normal=0xFFFE8077, previous_normal=0xFFFE807E,
          pointer=0x4338E, gate_call=0x43396, publication_stop=0x433B8,
          selected_load=0x433AA, previous_load=0x433A0, selected_store=0x433B4,
          compare=0x43528, latch_or=0x43534, latch_and=0x43544,
          axis=0x178D6, values=0x163E4, leaf=0x2AF88,
          setup=0x6388E, lookup_call=0x63894, lookup_return=0x63898,
          caller_read=0x6215E, caller_store=0x62162,
          packed_load=0x63022, packed_literal=0x630C0, packed_offset=0xA4,
          packed_read=0x63024, packed_store=0x6305A,
          startup_entry=0x6375E, startup_frame=0x20,
          save=0x63776, request=0x63782, branch=0x6385C,
          blend_axis=0x17186, blend_values=0x17136, blend_leaf=0x2AEAC,
          blend_setup=0x63860, blend_call=0x63866, blend_return=0x6386A,
          ramp_axis=0x14582, ramp_values=0x1457A, ramp_leaf=0x2AC9C,
          ramp_setup=0x63554, ramp_call=0x6355C, ramp_return=0x63560)
PROFILES = {"JK78C": JK, "1ND0A": ND, "1ND3B": ND, "1ME3B": ME}


def _fixtures() -> dict:
    raw = (ROOT / FIXTURE_PATH).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "retained fixture identity"
    result = json.loads(raw)
    assert result["schema"] == 1
    assert result["inherited_fixture"] == {"path": cold.FIXTURE_PATH, "sha256": cold.FIXTURE_SHA256}
    assert {n: f["sha256"] for n, f in result["images"].items()} == cold.IMAGE_FIXTURES
    return result


FIXTURES = _fixtures()


def _ranges(name: str, executed: bool = False) -> tuple[tuple[int, int], ...]:
    f = FIXTURES["images"][name]
    added = (tuple((int(a, 16), int(b, 16)) for a, b in f["execution_windows"])
             if executed else
             tuple((int(s["address"], 16), int(s["address"], 16) + len(bytes.fromhex(s["hex"])))
                   for s in f["spans"]))
    return cold._ranges(name, executed) + added


def _bind(data: bytes, name: str, *, image_hash: bool = True) -> None:
    cold._bind(data, name, image_hash=image_hash)
    spans = _ranges(name)
    for a, b in _ranges(name, True):
        assert a % 2 == b % 2 == 0 and 0 <= a < b <= len(data)
        assert all(any(left <= pc and pc + 2 <= right for left, right in spans)
                   for pc in range(a, b, 2)), "execution-window retention"
    for s in FIXTURES["images"][name]["spans"]:
        at, expected = int(s["address"], 16), bytes.fromhex(s["hex"])
        assert data[at:at + len(expected)] == expected, f"retained span {at:08x}"


@pytest.fixture(scope="module", params=tuple(cold.IMAGE_FIXTURES))
def image(request):
    name = request.param
    data = rom.load(name).data
    _bind(data, name)
    return name, data, PROFILES[name]


@pytest.fixture(scope="module")
def me_image():
    data = rom.load("1ME3B").data
    _bind(data, "1ME3B")
    return "1ME3B", data, ME


class Context(cold.Context):
    """Union input/trace closure around the unchanged cold-path interpreter."""

    def __init__(self, name: str, data: bytes):
        super().__init__(name, data, cold.PROFILES[name])
        self.s = PROFILES[name]
        self.marker(self.s["selected"], 1)
        self.marker(self.s["snapshot"], 1)
        self.pc_ranges, self.rom_ranges = _ranges(name, True), _ranges(name)

    def closure(self) -> None:
        m = self.m
        assert m.unset is None
        assert all(any(a <= pc and pc + 2 <= b for a, b in self.pc_ranges)
                   for pc in m.executed), "executed-PC closure"
        assert all(any(a <= at and at + n <= b for a, b in self.rom_ranges)
                   for _, at, n in m.loads if at < len(m.data)), "ROM-load closure"
        available = self.known | m.written()
        assert set(m.ram) == available, "RAM cells outside input/write manifest"
        assert all(set(range(at, at + n)) <= available
                   for _, at, n in m.loads if at >= len(m.data)), "incoming RAM manifest"
        assert all(m.peek(at) == value for at, value in self.guards.items()), "neighbor guards"
        assert all(m.data[pc] >> 4 != 0xF for pc in m.executed), "excluded FPU instruction"


def _select(c: Context, current: int, previous: int, flag: int, threshold: int, latch: int) -> int:
    s, m = c.s, c.m
    for at, value, role in ((s["flag"], flag, "incoming selected-refresh flag"),
                            (s["threshold"], threshold, "incoming refresh threshold"),
                            (s["latch"], latch, "incoming latch and unrelated bits"),
                            (s["previous"], previous, "incoming previous selected byte"),
                            (s["current_normal"], 0x21, "incoming current normalized-pair lane"),
                            (s["previous_normal"], 0x76, "incoming previous normalized-pair lane")):
        c.seed(at, bytes([value]), role)
    c.run(s["pointer"], s["pointer"] + 2)
    first_load, first_store, sp = len(m.loads), len(m.stores), m.r[15]
    c.run(s["gate_call"], s["publication_stop"], (s["selected"], s["latch"]))
    active = bool(flag & s["flag_mask"]) and threshold < 100
    refresh = active or not (latch & s["latch_mask"])
    expected_latch = ((latch & ~s["latch_mask"]) if active else (latch | s["latch_mask"]))
    result = current if refresh else previous
    assert m.peek(s["latch"]) == expected_latch, "selected latch relation and unrelated bits"
    assert m.peek(s["selected"]) == result, "selected refresh/retain relation"
    cold._stored(c, s["selected_store"], s["selected"], 1, result)
    source = s["selected_load"] if refresh else s["previous_load"]
    address = c.p["published"] if refresh else s["previous"]
    assert (source, address, 1) in m.loads[first_load:], "selected source and byte width"
    other = s["previous_load"] if refresh else s["selected_load"]
    assert other not in m.executed, "actual selected branch outcome"
    assert s["gate_call"] in m.executed and s["gate_call"] + 2 in m.executed
    assert s["gate_call"] + 4 in m.executed, "real helper call/delay/return"
    helper_returns = [pc for pc in m.executed if s["gate"] <= pc < s["gate"] + 0x34
                      and cold._word(m.data, pc) == 0x000B]
    assert len(helper_returns) == 1 and helper_returns[0] + 2 in m.executed
    latch_stores = [item for item in m.stores[first_store:] if item[1] == s["latch"]]
    assert bool(latch_stores) == refresh
    assert not latch_stores or all(n == 1 and value == expected_latch for _, _, n, value in latch_stores)
    assert bool(s["compare"] in m.executed) == bool(flag & s["flag_mask"])
    if flag & s["flag_mask"]:
        threshold_pc = 0x3CC94 if s is JK else 0x403AA if s is ND else 0x43526
        assert (threshold_pc, s["threshold"], 1) in m.loads[first_load:], "actual threshold byte source"
    assert m.r[15] == sp and m.peek(c.p["published"]) == current
    return result


def _snapshot(c: Context, selected: int, coolant: int) -> None:
    s, m, p = c.s, c.m, c.p
    if s is JK:
        c.marker(0xFFFF1064, 6)
        # Produced selected and P lanes are not initialized by this copy input.
        for at, value in ((0xFFFF106A, 0x11), (0xFFFF106B, 0x22),
                          (0xFFFF106D, 0x21), (0xFFFF106E, 0x44)):
            c.seed(at, bytes([value]), "incoming unrelated copy-group lane")
        c.run(0x20F3C, 0x20F3E)
        c.run(0x20F58, 0x20F5A)
        assert (m.r[14], m.r[12]) == (6, 0x225C0)
        c.run(0x20F98, 0x20FA0, range(0xFFFF1064, 0xFFFF106A), stack=12)
        assert bytes(m.peek(0xFFFF1064 + i) for i in range(6)) == bytes([0x11, 0x22, selected, 0x21, 0x44, coolant])
        group_reads = [(at, n) for pc, at, n in m.loads if 0x225CE <= pc <= 0x225E6 and at >= 0xFFFF0000]
        assert group_reads == [(0xFFFF106A + i, 1) for i in range(6)]
        cold._stored(c, 0x225E0, s["snapshot"], 1, selected)
        cold._stored(c, 0x225D8, p["coordinate"], 1, coolant)
        assert all(pc in m.executed for pc in (0x20F9C, 0x20F9E, 0x225F6, 0x225F4))
    elif s is ND:
        c.marker(0xFFFE806E, 1)
        c.seed(0xFFFE8074, b"\x11", "incoming unrelated copy source lane")
        for a, b in ((0x21264, 0x21266), (0x212C2, 0x212C6),
                     (0x212C8, 0x212CA), (0x212CC, 0x212CE)):
            c.run(a, b)
        assert (m.r[4], m.r[8]) == (0xFFFE8074, 0xFFFE806E)
        c.run(0x212D0, 0x212D6, (s["snapshot"],))
        cold._loaded(c, 0x212D0, s["selected"], 1)
        cold._stored(c, 0x212D4, s["snapshot"], 1, selected)
        c.run(0x212E2, 0x212E8, (0xFFFE806E, p["coordinate"]))
        cold._stored(c, 0x212E4, 0xFFFE806E, 1, 0x11)
    else:
        for a in (0x212A4, 0x212AA, 0x212B0, 0x212B6, 0x212BC):
            c.run(a, a + 2)
        assert (m.r[6], m.r[13]) == (0xFFFE8074, 0xFFFE806E)
        c.run(0x212FC, 0x21300, (s["snapshot"],))
        cold._loaded(c, 0x212FC, s["selected"], 1)
        cold._stored(c, 0x212FE, s["snapshot"], 1, selected)
        c.run(0x21308, 0x2130C, (p["coordinate"],))
    if s is not JK:
        cold._loaded(c, p["copy_read"], p["published"], 1)
        cold._stored(c, p["copy_store"], p["coordinate"], 1, coolant)
    assert (m.peek(s["snapshot"]), m.peek(p["coordinate"])) == (selected, coolant)


def _chain(name: str, data: bytes, *, q: int = 200, old: int = 0,
           forced: int | None = None, previous: int = 106,
           flag: int | None = None, threshold: int = 99,
           latch: int | None = None) -> tuple[Context, int, int, int, int]:
    c = Context(name, data)
    coolant = cold._publish(c, q, old, forced)
    a = cold._pid(c)
    flag = c.s["flag_mask"] if flag is None else flag
    latch = c.s["latch_mask"] if latch is None else latch
    selected = _select(c, coolant, previous, flag, threshold, latch)
    _snapshot(c, selected, coolant)
    return c, selected, coolant, c.m.peek(c.p["transfer"]), a


def _caller(c: Context, selected: int, coolant: int, *, upper: int = 0,
            request: int = 0) -> int:
    s, m, p = c.s, c.m, c.p
    m.r[15] = STACK_TOP  # Independent caller-entry stack context, not a producer result.
    initial = m.r[15]
    c.seed(initial, bytes(260), "incoming unrelated main-caller stack lanes")
    high = upper.to_bytes(3, "big")
    if s is JK:
        c.seed(initial + 0x40, high + b"\xcc", "incoming selected packed upper lanes and destination marker")
        c.seed(initial + 0x44, high + b"\xcc", "incoming coolant packed upper lanes and destination marker")
        c.run(0x5545C, 0x5545E)
        c.run(0x55476, 0x55486, (initial + 0x43, initial + 0x47))
        cold._stored(c, s["caller_store"], initial + 0x43, 1, selected)
        cold._stored(c, p["caller_store"], initial + 0x47, 1, coolant)
        call_sp = initial
    else:
        inputs = cold.ND_CALLER_INPUTS if s is ND else cold.ME_CALLER_INPUTS
        for at, n in inputs:
            if at != s["snapshot"]:
                c.seed(at, bytes(n), "incoming unrelated main-caller RAM")
        if s is ME:
            c.run(0x6202E, 0x62030)
            c.run(0x62034, 0x62036)
        start = 0x5E61A if s is ND else 0x62158
        c.run(start, p["frame_entry"], stack=0x70)
        call_sp = m.r[15]
        assert call_sp == initial - (0x44 if s is ND else 0x4C)
        selected_slot = call_sp + (0x3C if s is ND else 0x44)
        coolant_slot = call_sp + (0x40 if s is ND else 0x48)
        cold._stored(c, s["caller_store"], selected_slot, 4, selected)
        cold._stored(c, p["caller_store"], coolant_slot, 4, coolant)
        assert p["reader_call"] in m.executed and p["reader_call"] + 2 in m.executed
        # Only independent upper bytes change. The executed low-byte results remain.
        c.seed(selected_slot, high, "incoming selected packed upper-lane variant")
        c.seed(coolant_slot, high, "incoming coolant packed upper-lane variant")
    cold._loaded(c, s["caller_read"], s["snapshot"], 1)
    cold._loaded(c, p["caller_read"], p["coordinate"], 1)
    m.r[15] -= p["frame"]  # Static FPU-prologue frame supplied as an incoming operand.
    local = m.r[15]
    packed = (upper << 8) | selected
    if s is JK:
        c.run(0x56534, 0x56538)
        assert m.r[8] == (upper << 8) | coolant
        c.run(0x56544, 0x5654C, (local + 0xB3,))
        assert m.r[2] == packed
        for at, value in ((local + 0x8B, bytes([request])), (local + 0x8E, b"\x12\x34"),
                          (local + 0xBB, b"\x01")):
            c.seed(at, value, "incoming unrelated startup request/RPM/state operand")
        c.run(0x566F8, s["startup_entry"])
        assert (m.r[4], m.r[6]) == (selected, request)
        assert all(pc in m.executed for pc in (0x5670E, 0x56710))
    elif s is ND:
        c.run(0x5F4CE, 0x5F4D2)
        assert m.r[6] == packed
        c.run(0x5F500, 0x5F504, (local + 0x9F,))
        for at, value in ((local + 0x7B, bytes([request])), (local + 0x82, b"\x12\x34"),
                          (local + 0xA7, b"\x01")):
            c.seed(at, value, "incoming unrelated startup request/RPM/state operand")
        c.run(0x5F7CE, s["startup_entry"], range(local + 0x2C, local + 0x30))
        assert (m.r[4], m.r[6]) == (selected, request)
        assert all(pc in m.executed for pc in (0x5F7E8, 0x5F7EA))
    else:
        c.run(0x63022, 0x63026)
        assert m.r[6] == packed
        c.run(0x63058, 0x6305C, (local + 0xA7,))
        c.run(0x62FFE, 0x63002)
        assert m.r[8] == (upper << 8) | coolant
        c.run(0x63036, 0x6303A, (local + 0xAB,))
        c.seed(local + 0xB, bytes([request]), "incoming throttled request byte")
        c.seed(local + 0x9E, b"\x12\x34", "incoming unrelated RPM argument word")
        m.r[9] = 0xBEEF  # Independent unrelated ramp argument.
        c.run(0x631E2, 0x63534, range(local + 0x24, local + 0x28))
        assert m.r[4] == m.r[12] == selected
        assert all(pc in m.executed for pc in (0x631F8, 0x631FA))
    cold._loaded(c, s["packed_read"], call_sp + (0x40 if s is JK else 0x3C if s is ND else 0x44), 4)
    cold._stored(c, s["packed_store"], local + (0xB3 if s is JK else 0x9F if s is ND else 0xA7), 1, selected)
    return local


def _startup(c: Context, selected: int, coolant: int, *, blend: bool = False,
             upper: int = 0) -> tuple[int, int, int, int, int]:
    s, m = c.s, c.m
    assert not blend or s is ME
    request = int(blend)
    local = _caller(c, selected, coolant, upper=upper, request=request)
    if s is ME:
        # Independent selector continuation. The intervening FPU callee is excluded.
        c.run(0x631FC, 0x6320E, (local + 0x28, local + 0x29))
        assert m.r[11] == coolant
        c.seed(local + 0xAF, b"\x01", "incoming startup state byte")
        c.seed(local + 0x7F, bytes([request]), "incoming startup request byte")
        c.seed(local + 0x82, b"\x12\x34", "incoming startup RPM word")
        c.run(0x63298, s["startup_entry"], range(local + 0x2C, local + 0x30), stack=4)
        assert m.r[4] == selected
        cold._stored(c, 0x632A0, local - 4, 4, coolant)
        assert all(pc in m.executed for pc in (0x632AE, 0x632B0))
    incoming = m.r[15]
    m.r[15] -= s["startup_frame"]  # Bound static frame, not execution of the FPU prologue.
    if s is ME:
        c.run(0x63772, 0x63778)
        cold._loaded(c, 0x63772, incoming, 4)
        assert m.r[13] == coolant
    else:
        c.run(s["save"], s["save"] + 4)
    assert m.r[14] == selected, "executed saved selected-temperature operand"
    if s is not JK:
        c.run(s["request"], s["request"] + 2)
        assert m.r[1] == request
    target = s["blend_setup"] if blend else s["setup"]
    other = 0x56B46 if s is JK else 0x5FA84 if s is ND else (s["setup"] if blend else s["blend_setup"])
    c.run(s["branch"], target, extra_stops=(other,))
    leaf = s["blend_leaf"] if blend else s["leaf"]
    axis = s["blend_axis"] if blend else s["axis"]
    values = s["blend_values"] if blend else s["values"]
    call = s["blend_call"] if blend else s["lookup_call"]
    stop = s["blend_return"] if blend else s["lookup_return"]
    coordinate = coolant if blend else selected
    c.run(target, leaf)
    assert (m.r[4], m.r[5], m.r[6]) == (values, axis, coordinate), "actual axis and coordinate arguments"
    assert call in m.executed and call + 2 in m.executed, "actual lookup call/delay slot"
    assert m.pr == stop
    return leaf, stop, axis, values, coordinate


def _ramp(c: Context, selected: int, coolant: int, *, upper: int = 0) -> tuple[int, int, int, int, int]:
    assert c.s is ME
    _caller(c, selected, coolant, upper=upper)
    c.m.r[15] -= 0x34  # Static ramp FPU-prologue frame, not a simulated return.
    c.run(ME["ramp_setup"], ME["ramp_leaf"])
    assert (c.m.r[4], c.m.r[5], c.m.r[6]) == (ME["ramp_values"], ME["ramp_axis"], selected)
    assert all(pc in c.m.executed for pc in (ME["ramp_call"], ME["ramp_call"] + 2))
    assert c.m.pr == ME["ramp_return"]
    return ME["ramp_leaf"], ME["ramp_return"], ME["ramp_axis"], ME["ramp_values"], selected


def _eligible(x: int, axis: tuple[int, ...]) -> bool:
    return x <= axis[0] or x >= axis[-1] or x in axis


def _lookup(c: Context, args: tuple[int, int, int, int, int], points: tuple[int, ...],
            values: tuple[int, ...], width: int = 2) -> int:
    leaf, stop, axis, table, x = args
    assert _eligible(x, points), "only declared exact/end-point lookup execution"
    index = 0 if x <= points[0] else len(points) - 1 if x >= points[-1] else points.index(x)
    m, first, sp = c.m, len(c.m.loads), c.m.r[15]
    c.run(leaf, stop, stack=12)
    assert (m.r[0] & (0xFFFF if width == 2 else 0xFF)) == values[index], "actual exact/end-point result"
    assert m.r[15] == sp and m.pr == stop
    assert m.macl == cold.MACL_GUARD and m.mach == cold.MACH_GUARD
    reads = m.loads[first:]
    axis_reads = [(pc, at, n) for pc, at, n in reads if axis <= at < axis + len(points) * width]
    indices = list(range(len(points) - 1, index - 1, -1))
    if c.s in (JK, ND):
        assert axis_reads == [(c.s["search"] + 2, axis + i * 2, 2) for i in indices]
        actual = [(pc, at, n) for pc, at, n in reads if table <= at < table + (len(values) + 1) * 2]
        assert actual == [(leaf + 0x12, table + index * 2 + 2, 2),
                          (leaf + 0x18, table + index * 2, 2)], "real current/next value reads including upper endpoint"
        assert m.r[3] == 0, "exact/end-point phase is zero"
        assert all(pc in m.executed for pc in (leaf + 10, leaf + 12, leaf + 14, leaf + 0x1E, leaf + 0x20))
    else:
        offsets = (6, 0x10, 0x1E, 0x2C, 0x3A, 0x48, 0x56, 0x64, 0x72, 0x80,
                   0x8E, 0x9C, 0xAA, 0xB8, 0xC6, 0xD4) if len(points) == 16 else (6, 0x10, 0x1E, 0x2C, 0x3A, 0x48, 0x56, 0x64)
        assert axis_reads == [(leaf + offsets[j], axis + i * width, width)
                              for j, i in enumerate(indices)]
        return_pc = 0x2B0CE if len(points) == 16 else 0x2AF82 if width == 2 else 0x2AD68
        table_reads = [(pc, at, n) for pc, at, n in reads if table <= at < table + len(values) * width]
        assert table_reads == [(return_pc + 2, table + index * width, width)], "actual selected-cell read"
        assert return_pc in m.executed and return_pc + 2 in m.executed
    return m.r[0] & (0xFFFF if width == 2 else 0xFF)


def _static_bindings(data: bytes, s: dict, p: dict) -> None:
    cold._static_bindings(data, p)
    assert cold._word(data, s["packed_literal"]) == s["packed_offset"]
    assert cold._pc_literal(data, s["packed_load"], 2, 0) == s["packed_literal"]
    assert cold._word(data, s["packed_read"]) == (0x02FE if s is JK else 0x06FE)
    start = s["startup_entry"]
    if s is JK:
        assert tuple(cold._word(data, start + i * 2) for i in range(6)) == (0x2FB6, 0x2FC6, 0x2FE6, 0x4F22, 0xFFEB, 0x4F13)
        assert cold._word(data, start + 0x10) == 0x7FFC
        frame = 3 * 4 + 4 + 4 + 4 + 4
    elif s is ND:
        assert tuple(cold._word(data, start + i * 2) for i in range(7)) == (0x2FB6, 0x2FC6, 0x2FD6, 0x2FE6, 0x4F22, 0xFFEB, 0x7FFC)
        frame = 4 * 4 + 4 + 4 + 4
    else:
        assert tuple(cold._word(data, start + i * 2) for i in range(8)) == (0x2FA6, 0x2FB6, 0x2FC6, 0x2FD6, 0x2FE6, 0x4F22, 0xFFEB, 0x7FFC)
        frame = 5 * 4 + 4 + 4 + 4
        assert cold._word(data, 0x63772) == 0x5DF8 and (cold._word(data, 0x63772) & 15) * 4 == frame
        assert tuple(cold._word(data, 0x63534 + i * 2) for i in range(11)) == (0x2FA6, 0x2FB6, 0x2FC6, 0x2FD6, 0x2FE6, 0x4F22, 0xFFCB, 0xFFEB, 0xFFFB, 0x4F12, 0x4F13)
        assert cold._word(data, 0x6354E) == 0x7FF8
        assert 5 * 4 + 4 + 3 * 4 + 4 + 4 + 8 == 0x34
    assert frame == s["startup_frame"]
    assert int.from_bytes(data[s["axis"]:s["axis"] + 32], "big") == int.from_bytes(b"".join(x.to_bytes(2, "big") for x in STARTUP_AXIS), "big")
    assert tuple(cold._word(data, s["values"] + i * 2) for i in range(16)) == STARTUP_VALUES
    if s is ME:
        assert tuple(cold._word(data, s["blend_axis"] + i * 2) for i in range(8)) == BLEND_AXIS
        assert tuple(cold._word(data, s["blend_values"] + i * 2) for i in range(8)) == BLEND_VALUES
        assert tuple(data[s["ramp_axis"]:s["ramp_axis"] + 8]) == RAMP_AXIS
        assert tuple(data[s["ramp_values"]:s["ramp_values"] + 8]) == RAMP_VALUES


def _nominal(x: int) -> int:
    assert 0 <= x <= 255
    result = x - 50
    assert result + 50 == x
    return result


def test_vvel_duration_startup_axis_nominal_temperature(image) -> None:
    name, data, s = image
    _static_bindings(data, s, cold.PROFILES[name])
    cold._assert_decoder(cold._decoder_records())
    assert_vvel_temperature_axis_specification((ROOT / SPEC).read_text())
    assert tuple(_nominal(x) for x in STARTUP_AXIS) == tuple(range(-40, 111, 10))
    for q in range(3, 242):
        c, selected, coolant, t, a = _chain(name, data, q=q)
        assert selected == coolant == t
        assert (_nominal(selected) == a - 40) == (t >= 10), "conditional current PID relation"
        args = _startup(c, selected, coolant)
        if _eligible(selected, STARTUP_AXIS):
            _lookup(c, args, STARTUP_AXIS, STARTUP_VALUES)
    # Override and previous-selection domains are byte inputs, not physical reachability.
    for x in range(256):
        c, selected, coolant, _, _ = _chain(name, data, forced=x)
        assert selected == coolant == x
        args = _startup(c, selected, coolant, upper=0xABCDEF)
        assert _nominal(args[-1]) == x - 50
        if _eligible(x, STARTUP_AXIS):
            _lookup(c, args, STARTUP_AXIS, STARTUP_VALUES)
    for selected, coolant in ((106, 87), (0, 255), (255, 0), (127, 128), (128, 127)):
        c, actual, current, _, _ = _chain(name, data, forced=coolant, previous=selected, flag=0)
        assert (actual, current) == (selected, coolant)
        assert _startup(c, actual, current, upper=0x123456)[-1] == selected


def test_vvel_duration_startup_blend_axis_nominal_temperature(me_image) -> None:
    name, data, s = me_image
    _static_bindings(data, s, cold.ME)
    cold._assert_decoder(cold._decoder_records())
    assert_vvel_temperature_axis_specification((ROOT / SPEC).read_text())
    assert tuple(_nominal(x) for x in BLEND_AXIS) == tuple(range(50, 121, 10))
    for q in range(3, 242):
        c, selected, coolant, t, a = _chain(name, data, q=q, flag=0)
        assert selected == 106 and coolant == t
        assert (_nominal(coolant) == a - 40) == (t >= 10)
        args = _startup(c, selected, coolant, blend=True)
        if _eligible(coolant, BLEND_AXIS):
            _lookup(c, args, BLEND_AXIS, BLEND_VALUES)
    for x in range(256):
        c, selected, coolant, _, _ = _chain(name, data, forced=x, previous=(x + 71) & 255, flag=0)
        assert selected != coolant and coolant == x
        args = _startup(c, selected, coolant, blend=True, upper=0xABCDEF)
        assert args[-1] == x and args[-1] != selected
        if _eligible(x, BLEND_AXIS):
            _lookup(c, args, BLEND_AXIS, BLEND_VALUES)


def test_vvel_duration_throttled_ramp_delay_axis_nominal_temperature(me_image) -> None:
    name, data, s = me_image
    _static_bindings(data, s, cold.ME)
    cold._assert_decoder(cold._decoder_records())
    assert_vvel_temperature_axis_specification((ROOT / SPEC).read_text())
    assert tuple(_nominal(x) for x in RAMP_AXIS) == tuple(range(-30, 41, 10))
    for q in range(3, 242):
        c, selected, coolant, t, a = _chain(name, data, q=q)
        assert selected == coolant == t
        assert (_nominal(selected) == a - 40) == (t >= 10)
        args = _ramp(c, selected, coolant)
        if _eligible(selected, RAMP_AXIS):
            _lookup(c, args, RAMP_AXIS, RAMP_VALUES, 1)
    for x in range(256):
        c, selected, coolant, _, _ = _chain(name, data, forced=(x + 71) & 255, previous=x, flag=0)
        assert selected == x and selected != coolant
        args = _ramp(c, selected, coolant, upper=0xABCDEF)
        assert args[-1] == selected and args[-1] != coolant
        if _eligible(x, RAMP_AXIS):
            _lookup(c, args, RAMP_AXIS, RAMP_VALUES, 1)


@pytest.mark.parametrize("flag_on,latch_on", tuple(product((False, True), repeat=2)))
def test_every_refresh_threshold_byte_and_latch_arm(image, flag_on: bool, latch_on: bool) -> None:
    name, data, s = image
    for threshold in range(256):
        c = Context(name, data)
        current = cold._publish(c, 200, 0)
        assert current == 57
        flag = (0xA5 & ~s["flag_mask"]) | (s["flag_mask"] if flag_on else 0)
        latch = (0x5A & ~s["latch_mask"]) | (s["latch_mask"] if latch_on else 0)
        selected = _select(c, current, 106, flag, threshold, latch)
        expected = current if flag_on and threshold < 100 or not latch_on else 106
        assert selected == expected
        assert bool(s["compare"] in c.m.executed) == flag_on


@pytest.mark.parametrize("threshold", (0, 99, 100, 127, 128, 255))
def test_every_latch_byte_preserves_unrelated_bits(image, threshold: int) -> None:
    name, data, s = image
    for latch in range(256):
        c = Context(name, data)
        current = cold._publish(c, 200, 0)
        _select(c, current, 0, 255, threshold, latch)
        assert (c.m.peek(s["latch"]) & ~s["latch_mask"]) == (latch & ~s["latch_mask"])
        assert c.m.peek(s["flag"]) == 255 and c.m.peek(s["threshold"]) == threshold


def test_selected_hysteresis_override_and_independent_sample_counterexamples(image) -> None:
    name, data, s = image
    c, x, p, t, a = _chain(name, data, q=220, old=90)
    assert (x, p, t, a) == (44, 44, 42, 32)
    assert _nominal(x) == -6 and a - 40 == -8
    assert _startup(c, x, p)[-1] == 44
    for q, t in ((240, 8), (241, 7)):
        c, x, p, actual, a = _chain(name, data, q=q)
        assert x == p == actual == t and a == 0
        assert _nominal(x) != a - 40
        _startup(c, x, p)
    for old in (42, 43, 44):
        c, x, p, t, a = _chain(name, data, q=220, old=old)
        assert (x, p, t, a) == (old, old, 42, 32)
        _startup(c, x, p)
    # Different selector and publication samples retain the nominal unit, not equality.
    c, x, p, t, a = _chain(name, data, q=200, previous=106, flag=0)
    assert (x, p, t, a) == (106, 57, 57, 47)
    assert _startup(c, x, p)[-1] == 106 and _nominal(x) != a - 40
    c, x, p, _, a = _chain(name, data, q=200, forced=87, previous=106, flag=0)
    assert (x, p, a) == (106, 87, 47)
    assert _nominal(p) != a - 40
    c, x, p, _, _ = _chain(name, data, q=200)
    assert (x, p) == (57, 57)
    assert cold._source_word(c, 220 * 4) == (220, 42)
    assert cold._pid(c) == 32
    assert (c.m.peek(s["snapshot"]), c.m.peek(c.p["coordinate"])) == (57, 57)
    assert _startup(c, 57, 57)[-1] == 57 and _nominal(57) != 32 - 40
    assert [cold._source_word(Context(name, data), w)[0] for w in (0, 3, 1024)] == [0, 0, 0]


@pytest.mark.parametrize("selected,coolant", ((0, 255), (255, 0), (127, 128), (128, 127), (106, 87)))
@pytest.mark.parametrize("consumer", ("startup", "blend", "ramp"))
def test_me_current_coolant_and_selected_temperature_are_distinct(me_image, selected: int, coolant: int, consumer: str) -> None:
    name, data, _ = me_image
    c, x, p, _, _ = _chain(name, data, forced=coolant, previous=selected, flag=0)
    assert x == selected and p == coolant and x != p
    args = (_ramp(c, x, p) if consumer == "ramp" else
            _startup(c, x, p, blend=consumer == "blend"))
    assert args[-1] == (p if consumer == "blend" else x)
    assert args[-1] != (x if consumer == "blend" else p)


@pytest.mark.parametrize("upper", (0, 0x123456, 0xFFFFFF))
def test_packed_upper_bytes_do_not_change_unsigned_coordinate(image, upper: int) -> None:
    name, data, _ = image
    for x in (0, 1, 127, 128, 254, 255):
        c, selected, coolant, _, _ = _chain(name, data, forced=(x + 71) & 255, previous=x, flag=0)
        assert _startup(c, selected, coolant, upper=upper)[-1] == x


def test_startup_endpoint_next_word_is_an_actual_but_phase_zero_read(image) -> None:
    name, data, s = image
    if s is ME:
        c, x, p, _, _ = _chain(name, data, forced=255)
        _lookup(c, _startup(c, x, p), STARTUP_AXIS, STARTUP_VALUES)
        assert not any(at == s["values"] + 32 for _, at, _ in c.m.loads)
        return
    for extra in (0, 1, 700, 65535):
        changed = cold._patch(data, s["values"] + 32, extra)
        c, x, p, _, _ = _chain(name, changed, forced=255)
        assert _lookup(c, _startup(c, x, p), STARTUP_AXIS, STARTUP_VALUES) == 700
        assert (s["leaf"] + 0x12, s["values"] + 32, 2) in c.m.loads
        assert c.m.r[3] == 0


def test_binding_rejects_each_new_span_and_exact_image_pin(image) -> None:
    name, data, _ = image
    for span in FIXTURES["images"][name]["spans"]:
        at, count = int(span["address"], 16), len(bytes.fromhex(span["hex"]))
        for point in (at, at + count - 1):
            with pytest.raises(AssertionError, match="retained span"):
                _bind(cold._patch(data, point, bytes([data[point] ^ 1])), name, image_hash=False)
    with pytest.raises(AssertionError, match="full image identity"):
        _bind(cold._patch(data, len(data) - 1, bytes([data[-1] ^ 1])), name)


@pytest.mark.parametrize("mutation", ("signed-threshold", "threshold-boundary", "latch-set", "latch-clear", "selected-width", "helper-delay"))
def test_executed_selected_gate_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, s = image
    if mutation == "signed-threshold":
        at, value, threshold, flag, latch = s["compare"], cold._word(data, s["compare"]) + 1, 128, s["flag_mask"], s["latch_mask"]
    elif mutation == "threshold-boundary":
        at = 0x3CC96 if s is JK else 0x403AC if s is ND else 0x43524
        value, threshold, flag, latch = cold._word(data, at) - 1, 99, s["flag_mask"], s["latch_mask"]
    elif mutation == "latch-set":
        at, value, threshold, flag, latch = s["latch_or"], 0x0009, 100, 0, 0
    elif mutation == "latch-clear":
        at, value, threshold, flag, latch = s["latch_and"], 0x0009, 99, s["flag_mask"], s["latch_mask"]
    elif mutation == "selected-width":
        at, value, threshold, flag, latch = s["selected_store"], cold._word(data, s["selected_store"]) + 0x100, 99, s["flag_mask"], s["latch_mask"]
    else:
        at, value, threshold, flag, latch = s["gate_call"] + 2, 0x7F04, 99, s["flag_mask"], s["latch_mask"]
    c = Context(name, cold._patch(data, at, value))
    p = cold._publish(c, 200, 0)
    with cold._executed_rejection(c, at):
        _select(c, p, 106, flag, threshold, latch)


@pytest.mark.parametrize("mutation", ("source", "store-width"))
def test_executed_selected_copy_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, s = image
    load = 0x225DE if s is JK else 0x212D0 if s is ND else 0x212FC
    store = 0x225E0 if s is JK else 0x212D4 if s is ND else 0x212FE
    if mutation == "source":
        at = load
        value = 0x0009 if s is JK else cold._word(data, at) + 1
    else:
        at = store
        value = cold._word(data, at) + 0x100
    c = Context(name, cold._patch(data, at, value))
    p = cold._publish(c, 200, 0, 87)
    x = _select(c, p, 106, 0, 100, s["latch_mask"])
    with cold._executed_rejection(c, at):
        _snapshot(c, x, p)


@pytest.mark.parametrize("mutation", ("caller-source", "caller-width", "packed-source", "packed-width", "packed-store", "unsigned", "lookup-source", "axis-literal"))
def test_executed_selected_caller_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, s = image
    if mutation == "caller-source":
        at = s["caller_read"]
        value = cold._word(data, at) - 1 if s is JK else cold._word(data, at) + 0x100
    elif mutation == "caller-width":
        at = s["caller_store"]
        value = cold._word(data, at) + 1 if s is JK else (0x2F21 if s is ND else 0x2F81)
    elif mutation == "packed-source":
        at = s["packed_load"]
        value = cold._word(data, at) + 1
    elif mutation == "packed-width":
        at = s["packed_read"]
        value = cold._word(data, at) - 1
    elif mutation == "packed-store":
        at = s["packed_store"]
        value = cold._word(data, at) + 1
    elif mutation == "unsigned":
        at, value = ((0x56700, 0x642E) if s is JK else (0x5F7EA, 0x64BE) if s is ND else (0x631EC, 0x6CAE))
    elif mutation == "lookup-source":
        at = s["lookup_call"] + 2
        value = 0xE600
    else:
        literal = 0x56CBC if s is JK else 0x5FB04 if s is ND else 0x639E0
        at = s["setup"] + (2 if s is JK else 0)
        value = (s["axis"] + 2).to_bytes(4, "big")
    changed = cold._patch(data, literal if mutation == "axis-literal" else at, value)
    c, x, p, _, _ = _chain(name, changed, forced=87, previous=128, flag=0)
    with cold._executed_rejection(c, at):
        _startup(c, x, p, upper=0x123456)
    if mutation == "axis-literal":
        cold._loaded(c, at, literal, 4)


@pytest.mark.parametrize("consumer", ("blend", "ramp"))
@pytest.mark.parametrize("mutation", ("coordinate", "axis", "argument"))
def test_executed_me_separation_mutants_without_snapshot_binding(me_image, consumer: str, mutation: str) -> None:
    name, data, s = me_image
    if consumer == "blend":
        if mutation == "coordinate":
            at, replacement = 0x63868, 0x66EC  # Selected R14 instead of current-coolant R13.
        elif mutation == "argument":
            at, replacement = 0x63772, 0x5DFC  # Wrong fifth-argument stack slot.
        else:
            literal, at, replacement = 0x639CC, 0x63860, (s["axis"]).to_bytes(4, "big")
    else:
        if mutation == "coordinate":
            at, replacement = 0x63554, 0x665C  # Unrelated RPM R5 instead of selected R4.
        elif mutation == "argument":
            at, replacement = 0x631FA, 0x6403  # Unrelated R0 instead of produced R12.
        else:
            literal, at, replacement = 0x637B8, 0x63556, (s["ramp_axis"] + 1).to_bytes(4, "big")
    changed = cold._patch(data, literal if mutation == "axis" else at, replacement)
    c, x, p, _, _ = _chain(name, changed, forced=87, previous=106, flag=0)
    with cold._executed_rejection(c, at):
        if consumer == "blend":
            _startup(c, x, p, blend=True)
        else:
            _ramp(c, x, p)
    if mutation == "axis":
        cold._loaded(c, at, literal, 4)


@pytest.mark.parametrize("mutation", ("axis-width", "result-width", "result-slot", "axis-compare"))
def test_executed_startup_lookup_mutants_without_snapshot_binding(image, mutation: str) -> None:
    name, data, s = image
    if s in (JK, ND):
        if mutation == "axis-width":
            at, value = s["search"] + 2, 0x014C
        elif mutation == "result-width":
            at, value = s["leaf"] + 0x18, 0x6160
        elif mutation == "result-slot":
            at, value = s["leaf"] + 0x10, 0x0009
        else:
            at, value = s["search"] + 6, 0x3516
    else:
        if mutation == "axis-width":
            at, value = 0x2AF8E, 0x012C
        elif mutation == "result-width":
            at, value = 0x2B0D0, 0x6040
        elif mutation == "result-slot":
            at, value = 0x2B090, 0x0009
        else:
            at, value = 0x2AF92, 0x3162  # Swapped operands stay on the integer endpoint path.
    coordinate = 0 if s is ME and mutation == "axis-compare" else 160
    c, x, p, _, _ = _chain(name, cold._patch(data, at, value), forced=coordinate)
    args = _startup(c, x, p)
    with cold._executed_rejection(c, at):
        _lookup(c, args, STARTUP_AXIS, STARTUP_VALUES)


def test_fail_closed_union_pc_rom_ram_and_write_contract(image) -> None:
    name, data, s = image
    c = Context(name, data)
    with pytest.raises(AssertionError, match="unset cell"):
        c.m.run(s["gate"], (RETURN,))
    c = Context(name, cold._patch(data, s["gate"], 0xFFFF))
    with pytest.raises(AssertionError, match="opcode ffff"):
        c.m.run(s["gate"], (RETURN,))
    # A rejected opcode is an interpreter boundary test, never semantic evidence.
    c = Context(name, data)
    c.m.executed.append(s["axis"])
    with pytest.raises(AssertionError, match="executed-PC closure"):
        c.closure()
    c = Context(name, data)
    c.m.loads.append((s["gate"], 0, 1))
    with pytest.raises(AssertionError, match="ROM-load closure"):
        c.closure()
    c = Context(name, data)
    c.m.seed(0xFFFE0000, b"\x01")
    with pytest.raises(AssertionError, match="RAM cells outside"):
        c.closure()
    c = Context(name, data)
    with pytest.raises(AssertionError, match="store into the image"):
        c.m._write(s["axis"], 1, 0, s["gate"])
    c = Context(name, data)
    c.m.seed(STACK_TOP + 0x140, b"\x00")
    with pytest.raises(AssertionError, match="neighbor guards"):
        c.closure()


def assert_vvel_temperature_axis_specification(text: str) -> None:
    """Bind each published placement, grid and conditional execution boundary."""
    normalized = " ".join(text.split())
    for key in (STARTUP_TEST, BLEND_TEST, RAMP_TEST):
        assert f"{THIS_TEST}#{key}" in normalized, "named scale TEST declaration"
    assert FIXTURE_PATH in normalized and cold.FIXTURE_PATH in normalized
    for label, key in (("Refresh helper", "gate"), ("Refresh flag", "flag"),
                       ("Refresh threshold", "threshold"), ("Latch", "latch"),
                       ("Previous selected", "previous"), ("New selected", "selected"),
                       ("Selected coordinate", "snapshot"), ("Startup axis", "axis"),
                       ("Startup values", "values"), ("Startup lookup", "leaf")):
        row = f"| {label} | " + " | ".join(f"`{PROFILES[n][key]:08x}`" for n in cold.IMAGE_FIXTURES) + " |"
        assert row in normalized, f"published {label} bindings"
    row = "| Coolant coordinate | " + " | ".join(f"`{cold.PROFILES[n]['coordinate']:08x}`" for n in cold.IMAGE_FIXTURES) + " |"
    assert row in normalized, "published coolant-coordinate bindings"
    for label, key in (("Flag mask", "flag_mask"), ("Latch mask", "latch_mask")):
        row = f"| {label} | " + " | ".join(f"`0x{PROFILES[n][key]:02x}`" for n in cold.IMAGE_FIXTURES) + " |"
        assert row in normalized, f"published {label} bindings"
    for label, key in (("Blend axis", "blend_axis"), ("Blend values", "blend_values"),
                       ("Blend lookup", "blend_leaf"), ("Ramp-delay axis", "ramp_axis"),
                       ("Ramp-delay values", "ramp_values"), ("Ramp-delay lookup", "ramp_leaf")):
        assert f"| {label} | `{ME[key]:08x}` |" in normalized, f"published {label} binding"
    rows = (
        "| `vvel_duration_startup_axis/axis` | 10..160, step 10 | `uint16`, sixteen points | selected temperature | -40..110 degC |",
        "| `vvel_duration_startup_blend_axis/axis` | 100..170, step 10 | `uint16`, eight points | current coolant-coded byte | 50..120 degC |",
        "| `vvel_duration_throttled_ramp_delay_axis/axis` | 20..90, step 10 | `uint8`, eight points | selected temperature | -30..40 degC |",
    )
    required = (
        *rows,
        "conditional nominal encoded-temperature grid at level `code`",
        "unit is `degC`, the grid is `x-50`, and its inverse is `x+50`",
        "inverse is not a sensor inverse", "There is no hardware proof",
        "does not establish measured coolant temperature, sensor calibration, physical accuracy, or physical reachability",
        "blend and ramp-delay axes exist only on 1ME3B",
        "q = (W >> 2) & 255", "A = max(T - 10, 0)",
        "P = T if T > old", "P = old if T <= old and T + 2 > old", "P = T + 2 otherwise",
        "normal source-validity branch q=3..241", "`T>=10` implies `A-40=T-50`",
        "additionally requires `x=T` and corresponding samples",
        "not primary SAE, factory, or hardware evidence",
        "`community`", "`homologous_community`", "`community_reported`",
        "active = flag bit set and threshold < 100", "clear latch bit", "set latch bit",
        "selected = P if refresh else previous_selected",
        "selected_coordinate = snapshot(selected)", "coolant_coordinate = snapshot(P)",
        "retained selection changes the value and sample age, not the grid",
        "No bound on snapshot age is established",
        "separate coordinates and must not substitute for one another",
        "1ND0A and 1ND3B retain independent exact-image byte fixtures and independent executions",
        "Thresholds 99/100 and 127/128/255", "preserve every unrelated bit",
        "selected lane loads at `000225de` and stores at `000225e0`",
        "current-coolant lane stores at `000225d8`",
        "`000212d0`/`000212d4`", "`000212fc`/`000212fe`",
        "selected argument is saved to R14", "current-coolant argument is loaded into R13",
        "`00063868` zero-extends R13", "`00063896` zero-extends selected R14",
        "selected=106 and current coolant=87",
        "Selector net frames are JK78C `0x70`, 1ND `0x60`, and 1ME3B `0x60`",
        "Startup net frames are JK78C `0x1c`, 1ND `0x1c`, and 1ME3B `0x20`",
        "ramp-delay net frame is 1ME3B `0x34`",
        "`00063772` loads the fifth argument at SP+0x20",
        "No simulator return from an excluded FPU function is claimed",
        "Every coordinate byte executes transport to the actual lookup entry",
        "declared exact breakpoints and clamped endpoints only",
        "Fractional paths are excluded before execution",
        "actually read the next value word at the upper endpoint",
        "phase zero makes the result independent of it",
        "q=240/241 yields T=8/7 and A=0", "old=90 produces selected=P=44 while T=42 and A=32",
        "previous selected=106 differs from current P=57 and A=47", "override P=87",
        "leave both copied coordinates at 57 while A=32",
        "Binding rejection, unsupported opcodes, and step limits are not semantic passes",
        "requires the actual named scale TEST on every applicable symbol even when SPEC remains",
        "each note independently states", "Identity and byte homology alone do not ground a scale",
        "sensor/ADC production and calibration", "scheduler/interrupt execution and snapshot-age bounds",
        "FPU prologues and consumers", "fractional interpolation", "complete VVEL functions",
        "diagnostic parser or wire readiness", "actuator behavior", "hardware or engine eligibility",
        "Software gates do not grant flashing approval",
    )
    for fragment in required:
        assert fragment in normalized, f"published boundary: {fragment}"
    assert cold.FIXTURES["source"]["fragment"]["id"] in normalized


def test_temperature_axis_specification_binds_placements_and_boundaries() -> None:
    assert_vvel_temperature_axis_specification((ROOT / SPEC).read_text())


@pytest.mark.parametrize("before,after", (
    ("`ffff1066`", "`ffff1065`"),
    ("`fffe8070`", "`fffe8071`"),
    ("`000178d6`", "`000178d8`"),
    ("`00017186`", "`00017176`"),
    ("current coolant-coded byte | 50..120", "selected temperature | 50..120"),
    ("not a sensor inverse", "a sensor inverse"),
    ("There is no hardware proof", "There is hardware proof"),
    ("`T>=10` implies", "`T>=0` implies"),
    ("additionally requires `x=T` and corresponding samples", "requires no corresponding samples"),
    ("threshold < 100", "threshold <= 100"),
    ("selected = P if refresh else previous_selected", "selected = P"),
    ("1ME3B `0x20`", "1ME3B `0x24`"),
    ("SP+0x20", "SP+0x24"),
    ("`00063868` zero-extends R13", "`00063868` zero-extends R14"),
    ("not primary SAE, factory, or hardware evidence", "primary SAE, factory, and hardware evidence"),
    ("Software gates do not grant flashing approval", "Software gates grant flashing approval"),
))
def test_temperature_axis_specification_rejects_prose_mutants(before: str, after: str) -> None:
    text = " ".join((ROOT / SPEC).read_text().split())
    assert before in text
    with pytest.raises(AssertionError, match="published"):
        assert_vvel_temperature_axis_specification(text.replace(before, after, 1))


OWNER_CONTRACTS = (
    dict(name="vvel_duration_startup_axis", home="jk78c", points=16, storage="uint16",
         key=STARTUP_TEST, editor="Selected Temperature [degC]",
         symbols={"jk78c": 0x17204, "1nd": 0x17812, "1me3b": 0x178D6},
         identities={"jk78c": "jk78c:00056cbc", "1nd": "1nd:0005fb04", "1me3b": "1me3b:000639e0"},
         readers={"origami-sawfish/fn": "jk78c:00056cbc", "spicy-waxbill/fn": "1nd:0005fb04", "quantum-narwhal/fn": "1me3b:000639e0"},
         statuses={}, role="selected temperature", points_text="10..160 = -40..110 degC"),
    dict(name="vvel_duration_startup_blend_axis", home="1me3b", points=8, storage="uint16",
         key=BLEND_TEST, editor="Coolant Temperature [degC]", symbols={"1me3b": 0x17186},
         identities={"1me3b": "1me3b:000639cc"}, readers={"quantum-narwhal/fn": "1me3b:000639cc"},
         statuses={"1nd": "1nd:0005f9f0", "jk78c": "jk78c:00056ab4"},
         role="current coolant", points_text="100..170 = 50..120 degC"),
    dict(name="vvel_duration_throttled_ramp_delay_axis", home="1me3b", points=8, storage="uint8",
         key=RAMP_TEST, editor="Selected Temperature [degC]", symbols={"1me3b": 0x14582},
         identities={"1me3b": "1me3b:000637b8"}, readers={"efficient-ant/fn": "1me3b:000637b8"},
         statuses={"1nd": "1nd:0005f468", "jk78c": "jk78c:000564a4"},
         role="selected temperature", points_text="20..90 = -30..40 degC"),
)
NOTE_TOKENS = ("nominal encoded-temperature", "T>=10", "x=T", "corresponding samples",
               "not a sensor inverse", "no hardware proof", "selected", "current coolant", "retained")


def proposed_temperature_axis_owner_notes() -> dict[str, dict[str, str | list[str]]]:
    """Return proposed English notes; do not write owners, projections or graph."""
    result = {}
    for contract in OWNER_CONTRACTS:
        notes = {}
        for layout in contract["symbols"]:
            def note(image: str) -> str:
                return (
                    f"{image}: {contract['points']}-point nominal encoded-temperature axis "
                    f"{contract['points_text']} under x-50, inverse x+50. "
                    f"The coordinate is {contract['role']}. Current coolant is the snapshot of P; "
                    "selected temperature uses P on refresh or a retained previous selected byte. "
                    "Equality with the retained community PID05 decoder requires T>=10, x=T, "
                    "and corresponding samples. The grid is not a sensor inverse; no hardware proof."
                )
            notes[layout] = ([note("1ND0A"), note("1ND3B")] if layout == "1nd" else
                             note("JK78C" if layout == "jk78c" else "1ME3B"))
        result[contract["name"]] = notes
    return result


def _meaning(model, contract: dict):
    from kb.model import SymbolKey
    return model.symbols[SymbolKey(contract["home"], "axis", contract["symbols"][contract["home"]])].meaning


def _owner_symbol(model, symbol, contract: dict) -> None:
    from kb import match
    expected = dict(level="code", quantity="temp", points=contract["points"], storage=contract["storage"],
                    unit="degC", scale="x-50", to_raw="x+50", scale_level="code")
    assert {key: symbol.value(key) for key in expected} == expected, "effective owner properties"
    assert symbol.value("editor") == dict(name=contract["editor"], format="0", fine=1, coarse=5)
    identity = {"kind": "l0", "supports": "identity", "at": contract["identities"][symbol.layout]}
    assert [item for item in symbol.evidence if item.get("supports", "identity") == "identity"] == [identity], "original identity evidence"
    assert match.verify(model, symbol, identity) is None
    notes = symbol.props.get("note", "")
    notes = notes if isinstance(notes, list) else [notes]
    if symbol.layout == "1nd":
        assert len(notes) == 2 and all(note.startswith(label) for note, label in zip(notes, ("1ND0A:", "1ND3B:"))), "separate image-labelled owner notes"
    else:
        assert len(notes) == 1
    for note in notes:
        normalized = re.sub(r"\s*(>=|=)\s*", r"\1", " ".join(note.split()).lower())
        for token in (*NOTE_TOKENS, contract["role"], contract["points_text"]):
            expected_token = re.sub(r"\s*(>=|=)\s*", r"\1", token.lower())
            assert expected_token in normalized, f"qualified nominal owner note {token}"
    named = [item for item in symbol.evidence if item.get("kind") == "test" and item.get("supports") == "scale"
             and item.get("path") == THIS_TEST and item.get("key") == contract["key"]]
    assert len(named) == 1, "actual named scale TEST item is required even with SPEC"
    all_scale_tests = [item for item in symbol.evidence if item.get("kind") == "test" and item.get("supports") == "scale"]
    assert all_scale_tests == named, "scale TEST belongs to the actual axis meaning"
    specs = [item for item in symbol.evidence if item.get("kind") == "spec" and item.get("supports") == "scale"
             and item.get("path") == SPEC]
    assert len(specs) == 1, "actual scale SPEC is required"
    assert match.verify(model, symbol, named[0]) is None
    assert match.verify(model, symbol, specs[0]) is None


def assert_compiled_vvel_temperature_axis_owner_contract(model) -> None:
    """Require integrated compiled owners, original identity and named executables.

    This function never adds evidence. Live-source callers compile the actual
    owners after their batch and invoke it. TEST removal still fails with SPEC
    present. The preview test fixture below has an explicitly different role.
    """
    from kb import levels
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(node, ast.FunctionDef)}
    assert {STARTUP_TEST, BLEND_TEST, RAMP_TEST} <= functions, "actual top-level scale tests"
    level_issues = levels.check(model)
    for contract in OWNER_CONTRACTS:
        meaning = _meaning(model, contract)
        assert meaning.key == f"{contract['name']}/axis" and meaning.home == contract["home"]
        expected = dict(level="code", quantity="temp", points=contract["points"], storage=contract["storage"],
                        unit="degC", scale="x-50", to_raw="x+50", scale_level="code")
        assert {key: meaning.props[key] for key in expected} == expected, "owner properties and geometry"
        assert meaning.props["editor"] == dict(name=contract["editor"], format="0", fine=1, coarse=5), "owner editor presentation"
        assert {symbol.layout: symbol.address for symbol in meaning.symbols.values()} == contract["symbols"], "owner symbol placement"
        assert set(meaning.statuses) == set(contract["statuses"]), "owner absent-layout set"
        for layout, at in contract["statuses"].items():
            status = meaning.statuses[layout]
            assert status.state == "absent", "owner absent status"
            assert status.evidence == [{"kind": "l0", "supports": "identity", "at": at}], "owner absent-status identity"
        readers = {(link.type, link.to.key, tuple(sorted(link.roles))): link.evidence for link in meaning.links}
        assert len(readers) == len(meaning.links), "unique reader links"
        assert readers == {("reader", target, ("accessor",)): [{"kind": "l0", "supports": "identity", "at": at}]
                           for target, at in contract["readers"].items()}, "original reader/accessor links"
        for symbol in meaning.symbols.values():
            _owner_symbol(model, symbol, contract)
        assert not [issue for issue in level_issues
                    if issue.subject == meaning.key and "scale" in issue.message], "actual grounded scale"
    assert_vvel_temperature_axis_specification((ROOT / SPEC).read_text())


@pytest.fixture(scope="module")
def compiled_owner_live():
    """A fresh actual-source model, with no proposed evidence injected."""
    from kb import compile, repo
    return compile.build(repo.ROOT)


def test_live_compiled_temperature_axis_owners_are_integrated(compiled_owner_live) -> None:
    assert_compiled_vvel_temperature_axis_owner_contract(compiled_owner_live)


@pytest.fixture(scope="module")
def compiled_owner_preview(request):
    """Exercise helper mutations on an actual or explicitly proposed compiled model.

    The preview parameter injects proposed items only in memory and does not
    establish source integration. The live parameter compiles unchanged actual
    sources and requires their accepted contract before each mutation. Neither
    parameter writes a registry or changes the graph.
    """
    from kb import compile, repo
    model = compile.build(repo.ROOT)
    if getattr(request, "param", "preview") == "live":
        assert_compiled_vvel_temperature_axis_owner_contract(model)
        yield model
        return
    proposal = proposed_temperature_axis_owner_notes()
    saved = []
    for contract in OWNER_CONTRACTS:
        meaning = _meaning(model, contract)
        for symbol in meaning.symbols.values():
            saved.append((symbol, symbol.evidence, deepcopy(symbol.props)))
            symbol.props["note"] = deepcopy(proposal[contract["name"]][symbol.layout])
            symbol.evidence = [item for item in symbol.evidence if item.get("supports") != "scale"] + [
                {"kind": "test", "supports": "scale", "path": THIS_TEST, "key": contract["key"]},
                {"kind": "spec", "supports": "scale", "path": SPEC},
            ]
    try:
        yield model
    finally:
        for symbol, evidence, props in saved:
            symbol.evidence, symbol.props = evidence, props


def test_compiled_owner_helper_preview_not_live_source_integration(compiled_owner_preview) -> None:
    assert_compiled_vvel_temperature_axis_owner_contract(compiled_owner_preview)


@pytest.mark.parametrize("compiled_owner_preview", ("preview", "live"), indirect=True)
@pytest.mark.parametrize("contract_index,layout", ((0, "jk78c"), (0, "1nd"), (0, "1me3b"), (1, "1me3b"), (2, "1me3b")))
@pytest.mark.parametrize("mutation", ("remove-test", "missing-key", "wrong-meaning-key", "remove-spec"))
def test_owner_preview_requires_each_named_scale_test_even_with_spec(compiled_owner_preview, contract_index: int, layout: str, mutation: str) -> None:
    from kb import match
    model, contract = compiled_owner_preview, OWNER_CONTRACTS[contract_index]
    symbol = _meaning(model, contract).symbols[layout]
    original = symbol.evidence
    try:
        symbol.evidence = deepcopy(original)
        named = next(item for item in symbol.evidence if item.get("kind") == "test" and item.get("supports") == "scale")
        if mutation == "remove-test":
            symbol.evidence.remove(named)
        elif mutation == "missing-key":
            named["key"] = "test_missing_vvel_temperature_axis_scale"
            assert "defines no function" in match.verify(model, symbol, named)
        elif mutation == "wrong-meaning-key":
            named["key"] = BLEND_TEST if contract_index != 1 else RAMP_TEST
            assert match.verify(model, symbol, named) is None
        else:
            symbol.evidence = [item for item in symbol.evidence if item.get("kind") != "spec"]
        if mutation != "remove-spec":
            assert any(item.get("kind") == "spec" and item.get("supports") == "scale" for item in symbol.evidence)
        assert all(item in symbol.evidence for item in original if item.get("supports") == "identity")
        with pytest.raises(AssertionError):
            _owner_symbol(model, symbol, contract)
    finally:
        symbol.evidence = original
    _owner_symbol(model, symbol, contract)


@pytest.mark.parametrize("compiled_owner_preview", ("preview", "live"), indirect=True)
@pytest.mark.parametrize("image_index", (0, 1))
@pytest.mark.parametrize("token", NOTE_TOKENS)
def test_each_1nd_preview_note_requires_its_own_boundary(compiled_owner_preview, image_index: int, token: str) -> None:
    model, contract = compiled_owner_preview, OWNER_CONTRACTS[0]
    symbol = _meaning(model, contract).symbols["1nd"]
    original = symbol.props["note"]
    try:
        changed = original.copy()
        assert token.lower() in changed[image_index].lower()
        changed[image_index] = re.sub(re.escape(token), "", changed[image_index], flags=re.IGNORECASE)
        assert changed[1 - image_index] == original[1 - image_index]
        symbol.props["note"] = changed
        with pytest.raises(AssertionError, match="qualified nominal owner note"):
            _owner_symbol(model, symbol, contract)
    finally:
        symbol.props["note"] = original
    _owner_symbol(model, symbol, contract)


@pytest.mark.parametrize("compiled_owner_preview", ("preview", "live"), indirect=True)
@pytest.mark.parametrize("image_index", (0, 1))
def test_each_1nd_preview_note_requires_its_image_label(compiled_owner_preview, image_index: int) -> None:
    model, contract = compiled_owner_preview, OWNER_CONTRACTS[0]
    symbol = _meaning(model, contract).symbols["1nd"]
    original = symbol.props["note"]
    try:
        changed = original.copy()
        changed[image_index] = changed[image_index].split(":", 1)[1]
        symbol.props["note"] = changed
        with pytest.raises(AssertionError, match="separate image-labelled owner notes"):
            _owner_symbol(model, symbol, contract)
    finally:
        symbol.props["note"] = original


@pytest.mark.parametrize("compiled_owner_preview", ("preview", "live"), indirect=True)
@pytest.mark.parametrize("contract_index", range(3))
def test_owner_preview_identity_and_homology_do_not_ground_scale(compiled_owner_preview, contract_index: int) -> None:
    from kb import levels, match
    model, contract = compiled_owner_preview, OWNER_CONTRACTS[contract_index]
    meaning = _meaning(model, contract)
    original = {layout: symbol.evidence for layout, symbol in meaning.symbols.items()}
    props, tables = deepcopy(meaning.props), deepcopy(meaning.tables)
    try:
        for symbol in meaning.symbols.values():
            symbol.evidence = [item for item in symbol.evidence if item.get("supports") != "scale"]
            if symbol.layout != meaning.home:
                encoded = b"".join(x.to_bytes(2, "big") for x in STARTUP_AXIS)
                homology = {"kind": "byte-identical", "supports": "homology", "at": symbol.key.location,
                            "to": meaning.home_symbol.key.location, "sha256": hashlib.sha256(encoded).hexdigest()}
                assert match.verify(model, symbol, homology) is None
                symbol.evidence.append(homology)
        assert all(rank >= levels.CODE for rank, _ in match.grounded(model, [symbol.key for symbol in meaning.symbols.values()]).values())
        assert any(issue.subject == meaning.key and "scale level code lacks grounding" in issue.message for issue in levels.check(model))
        with pytest.raises(AssertionError, match="actual named scale TEST"):
            _owner_symbol(model, meaning.home_symbol, contract)
        assert meaning.props == props and meaning.tables == tables
    finally:
        for layout, symbol in meaning.symbols.items():
            symbol.evidence = original[layout]


def test_each_scale_contract_has_a_distinct_actual_top_level_test() -> None:
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body if isinstance(node, ast.FunctionDef)}
    assert {STARTUP_TEST, BLEND_TEST, RAMP_TEST} <= functions
    assert len({STARTUP_TEST, BLEND_TEST, RAMP_TEST}) == len(OWNER_CONTRACTS)
    assert "test_missing_vvel_temperature_axis_scale" not in functions
    assert "assert_compiled_vvel_temperature_axis_owner_contract" in functions


def test_retained_previous_selected_byte_domain_reaches_startup(image) -> None:
    name, data, _ = image
    for x in range(256):
        c, selected, coolant, _, _ = _chain(name, data, forced=(x + 71) & 255, previous=x, flag=0)
        assert selected == x and selected != coolant
        args = _startup(c, selected, coolant)
        if _eligible(x, STARTUP_AXIS):
            _lookup(c, args, STARTUP_AXIS, STARTUP_VALUES)
