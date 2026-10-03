"""Nominal running VVEL/CVTC RPM grids over independently retained stock bytes.

The unchanged PathSh2 executes bounded producer, real copy, selected PID0C
byte-writer and integer argument/first-axis-word paths. Every window declares
incoming state, permitted writes, executed-PC and ROM-load closure. Float
prologues and CVTC call delay slots have static bindings only. No instructions,
stubs, relocations or calculated producer-output seeds are supplied by this gate.
"""
from __future__ import annotations

import ast
from contextlib import contextmanager
from copy import deepcopy
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import tomllib

import pytest

from tools.mapkit import rom
from tools.mapkit.sh2_interpreter import MASK, RETURN, STACK_TOP, sext
from tools.mapkit.tests.test_candidate_identity_paths import PathSh2
from tools.mapkit.tests.test_rpm_axis_scale import _validate_source

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_vq37_running_rpm_scale.py"
SPEC = "defs/VQ37.running-rpm-axis-scale.md"
FIXTURE_PATH = "tools/mapkit/tests/fixtures/vq37_running_rpm_pid0c.json"
FIXTURE_SHA256 = "e1b1b0bea866eaedf734e7c9e1b9f8a086b7fb501a8a099174c12c9f20a7ba53"
TEST_KEYS = {
    "vvel_duration_running_axis": "test_vvel_duration_running_nominal_rpm_scale",
    "intake_cvtc_target_running_axis": "test_intake_cvtc_target_running_nominal_rpm_scale",
}
IMAGE_FIXTURES = {
    "JK78C": "86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d",
    "1ND0A": "650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978",
    "1ND3B": "0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e",
    "1ME3B": "f905b78901b4ca96002a31c2fca8f1cd00dee57b02bea1921a341caa6db2a6f3",
}
STOCK_AXIS = (128, 192, 256, 384, 512, 640, 768, 896,
              1024, 1152, 1408, 1664, 1920, 2176, 2240, 2304)
NOMINAL_AXIS = tuple(Fraction(25 * x, 8) for x in STOCK_AXIS)
MACL_GUARD, MACH_GUARD = 0x31415926, 0x27182818

JK = dict(
    layout="jk78c", word=0xFFFF1186, fine=0xFFFF11DA, coarse=0xFFFF11E0,
    coordinate=0xFFFF11A6, copied_coarse=0xFFFF11AC, source=0xFFFF11C0,
    destination=0xFFFF118C, source_size=0x34, destination_size=0x34,
    producer=0x3B886, producer_read=0x3B88A, producer_stop=0x3B7EE,
    intermediate=0xFFFF11D4, old=0xFFFF11C6, old_store=0x3B8C2,
    coefficient=0x863D, fine_store=0x3B8CA,
    coarse_store=0x3B8EA, fifth=0xFFFF218E, capped=0xFFFF21E8,
    copy_start=0x20FCA, copy_stop=0x20FD0, selected=0x39190, selected_stop=0x39384,
    miss=0x391C6, pid_read=0x39198, writer=0x3AF20, response_store=0x3AF2A,
    cursor_store=0x3AF34, response=0xFFFF3D11, cursor=0xFFFF4294,
    call1=0x391B6, call2=0x391BE, frame_entry=0x564A4, frame=0x70,
    argument_start=0x5545A, argument_read=0x56528, argument_register=12,
    argument_offset=0xA4, vvel_axis=0x16CA4, cvtc_axis=0x16E74,
    vvel_values=0x16BB4, cvtc_values=0x16DC4, wrapper=0x28320,
    kernel=0x287AC, first_axis_read=0x287AE, axis_stop=0x287B4,
    vvel_call=0x5658C, cvtc_call=0x565A6,
)
ND = dict(
    layout="1nd", word=0xFFFE818E, fine=0xFFFE81E8, coarse=0xFFFE81EE,
    coordinate=0xFFFE81B0, copied_coarse=0xFFFE81B6, source=0xFFFE81CC,
    destination=0xFFFE818C, source_size=0x38, destination_size=0x40,
    producer=0x3EF48, producer_read=0x3EF54, producer_stop=0x3EFC4,
    fine_store=0x3EF92, coarse_store=0x3EFC0, intermediate=0xFFFE81E2,
    old=0xFFFE81D4, old_store=0x3EF8C, coefficient=0x869B,
    fifth=0xFFFE922E, capped=0xFFFE928C, copy_start=0x21318,
    copy_stop=0x21364, copy_load=0x21322, copy_store=0x2133A,
    selected=0x3BD18, selected_stop=RETURN, miss=0x3BD5C,
    pid_read=0x3BD20, writer=0x3E410, response_store=0x3E41E,
    cursor_store=0x3E42C, response=0xFFFEAF89, cursor=0xFFFEB568,
    call1=0x3BD44, call2=0x3BD58, frame_entry=0x5F468, frame=0x60,
    argument_start=0x5E644, argument_read=0x5F4F0, argument_register=13,
    argument_offset=0x8C, main_target=0x5F468, main_call=0x5E6B8,
    argument_push=0x5E64A, push_size=0x30, vvel_axis=0x172B2,
    cvtc_axis=0x17472, vvel_values=0x171C2, cvtc_values=0x173C2,
    wrapper=0x2893C, kernel=0x28DC8, first_axis_read=0x28DCA,
    axis_stop=0x28DD0, vvel_call=0x5F5DE, cvtc_call=0x5F5F6,
    gbr=0xFFFEF5CC,
    unrelated=((0xFFFE81AD, 1), (0xFFFEA448, 1), (0xFFFE80BE, 2),
               (0xFFFE9796, 1), (0xFFFE977A, 2), (0xFFFE977C, 2),
               (0xFFFEA734, 2), (0xFFFEA784, 2), (0xFFFEA786, 2),
               (0xFFFEA9FA, 2)),
)
ME = dict(
    layout="1me3b", word=0xFFFE8176, fine=0xFFFE81D0, coarse=0xFFFE81D6,
    coordinate=0xFFFE8198, copied_coarse=0xFFFE819E, source=0xFFFE81B4,
    destination=0xFFFE8174, source_size=0x38, destination_size=0x40,
    producer=0x420C8, producer_read=0x420D4, producer_stop=0x42144,
    fine_store=0x42114, coarse_store=0x42140, intermediate=0xFFFE81C8,
    old=0xFFFE8FA4, old_store=0x4210E, coefficient=0x86A5,
    fifth=0xFFFE91F6, capped=0xFFFE9254, copy_start=0x2133E,
    copy_stop=0x2138A, copy_load=0x2134A, copy_store=0x21362,
    selected=0x3ED64, selected_stop=RETURN, miss=0x3EDA0,
    pid_read=0x3ED6C, writer=0x4145C, response_store=0x4146A,
    cursor_store=0x41478, response=0xFFFEB0CD, cursor=0xFFFEB6B8,
    call1=0x3ED90, call2=0x3ED98, frame_entry=0x62FAC, frame=0x60,
    argument_start=0x62180, argument_read=0x6304C, argument_register=11,
    argument_offset=0x94, main_target=0x62FAC, main_call=0x62200,
    argument_push=0x62186, push_size=0x38, vvel_axis=0x17366,
    cvtc_axis=0x17546, vvel_values=0x17276, cvtc_values=0x17496,
    wrapper=0x2AF88, kernel=0x2AF88, first_axis_read=0x2AF8E,
    axis_stop=0x2AF94, vvel_call=0x63142, cvtc_call=0x6315E,
    gbr=0xFFFEF56C,
    unrelated=((0xFFFEB8CA, 2), (0xFFFE93DA, 2), (0xFFFE8195, 1),
               (0xFFFEA510, 1), (0xFFFE80BA, 2), (0xFFFE97A6, 2),
               (0xFFFE97A8, 2), (0xFFFEA820, 2), (0xFFFEA872, 2),
               (0xFFFEA874, 2), (0xFFFEAB22, 2), (0xFFFE8215, 1)),
)
PROFILES = {"JK78C": JK, "1ND0A": ND, "1ND3B": ND, "1ME3B": ME}


def _fixtures() -> dict:
    raw = (ROOT / FIXTURE_PATH).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == FIXTURE_SHA256, "retained fixture identity"
    f = json.loads(raw)
    assert f["schema"] == 1 and set(f["images"]) == set(IMAGE_FIXTURES)
    assert {n: row["sha256"] for n, row in f["images"].items()} == IMAGE_FIXTURES
    assert set(f["owners"]) == set(TEST_KEYS)
    return f


FIXTURES = _fixtures()
ROM_RANGES = {
    n: tuple((int(s["address"], 16), int(s["address"], 16) + len(bytes.fromhex(s["hex"])))
             for s in f["spans"])
    for n, f in FIXTURES["images"].items()
}
PC_SETS = {
    n: frozenset(pc for a, b in f["execution_windows"]
                 for pc in range(int(a, 16), int(b, 16), 2))
    for n, f in FIXTURES["images"].items()
}


def _bind(data: bytes, name: str, *, image_hash: bool = True) -> None:
    if image_hash:
        assert hashlib.sha256(data).hexdigest() == IMAGE_FIXTURES[name], "full image identity"
    for s in FIXTURES["images"][name]["spans"]:
        at, expected = int(s["address"], 16), bytes.fromhex(s["hex"])
        assert data[at:at + len(expected)] == expected, f"retained span {at:08x}"
    assert all(any(a <= pc and pc + 2 <= b for a, b in ROM_RANGES[name])
               for pc in PC_SETS[name]), "execution-window retention"


@pytest.fixture(scope="module", params=tuple(IMAGE_FIXTURES))
def image(request):
    name = request.param
    data = rom.load(name).data
    _bind(data, name)
    return name, data, PROFILES[name]


def _patch(data: bytes, at: int, value: int | bytes) -> bytes:
    value = value.to_bytes(2, "big") if isinstance(value, int) else value
    changed = bytearray(data)
    changed[at:at + len(value)] = value
    return bytes(changed)


def _word(data: bytes, at: int) -> int:
    return int.from_bytes(data[at:at + 2], "big")


def _cells(at: int, size: int) -> set[int]:
    return set(range(at, at + size))


class Context:
    """Memory and window manifest around PathSh2, with no opcode overrides."""

    def __init__(self, name: str, data: bytes, p: dict):
        self.name, self.p, self.m = name, p, PathSh2(data)
        self.m.macl, self.m.mach = MACL_GUARD, MACH_GUARD
        self.known = _cells(STACK_TOP - 4, 20)
        self.inputs = [(STACK_TOP - 4, 20, "constructor stack context")]
        self.outputs: set[int] = set()
        self.guards: dict[int, int] = {}
        self.window_inputs: list[tuple] = []
        self.guard(STACK_TOP - 0x200, 0xA5)
        self.guard(STACK_TOP + 0x180, 0x5A)
        self.marker(p["fine"], 2)
        self.marker(p["coarse"], 2)
        self.marker(p["destination"], p["destination_size"])
        self.marker(p["response"] + 5, 2)

    def seed(self, at: int, values: bytes, role: str) -> None:
        cells = _cells(at, len(values))
        for cell in cells:
            self.guards.pop(cell, None)
        self.m.seed(at, values)
        self.known.update(cells)
        self.inputs.append((at, len(values), role))

    def guard(self, at: int, value: int) -> None:
        self.seed(at, bytes([value]), "neighbor guard")
        self.guards[at] = value

    def marker(self, at: int, size: int) -> None:
        self.seed(at, b"\xcc" * size, "destination marker, not a computed output")
        self.guard(at - 1, 0xA5)
        self.guard(at + size, 0x5A)

    def closure(self) -> None:
        m = self.m
        assert m.unset is None
        assert set(m.executed) <= PC_SETS[self.name], "executed-PC closure"
        assert all(any(a <= at and at + n <= b for a, b in ROM_RANGES[self.name])
                   for _, at, n in m.loads if at < len(m.data)), "ROM-load closure"
        available = self.known | self.outputs
        assert set(m.ram) == available, "RAM cells outside input/write manifest"
        assert all(_cells(at, n) <= available for _, at, n in m.loads
                   if at >= len(m.data)), "incoming RAM manifest"
        assert all(m.peek(at) == v for at, v in self.guards.items()), "neighbor guards"
        assert all(m.data[pc] >> 4 != 0xF for pc in m.executed), "excluded FPU instruction"

    def run(self, start: int, stop: int, writes=(), *, stack: int = 0,
            extra_stops: tuple[int, ...] = ()) -> None:
        m, sp = self.m, self.m.r[15]
        first_pc, first_load, first_store = len(m.executed), len(m.loads), len(m.stores)
        allowed = set(writes) | set(range(sp - stack, sp))
        self.window_inputs.append((start, stop, tuple(m.r), m.pr, m.gbr,
                                   m.macl, m.mach, tuple(self.inputs), frozenset(allowed)))
        assert all(0 <= r <= MASK for r in m.r)
        result = m.run(start, (stop, *extra_stops), limit=2048)
        assert result == stop, "execution exits declared window"
        assert set(m.executed[first_pc:]) <= PC_SETS[self.name], "executed-PC closure"
        assert all(any(a <= at and at + n <= b for a, b in ROM_RANGES[self.name])
                   for _, at, n in m.loads[first_load:] if at < len(m.data)), "ROM-load closure"
        written = {at + i for _, at, n, _ in m.stores[first_store:] for i in range(n)}
        assert written <= allowed, "allowed writes"
        self.outputs.update(written)
        assert set(m.ram) == self.known | self.outputs, "RAM cells outside input/write manifest"
        assert all(m.peek(at) == v for at, v in self.guards.items()), "neighbor guards"
        assert all(m.data[pc] >> 4 != 0xF for pc in m.executed[first_pc:]), "excluded FPU instruction"


def _loaded(c: Context, pc: int, at: int, width: int) -> None:
    assert (pc, at, width) in c.m.loads, f"actual load {pc:08x}/{at:08x}/{width}"


def _stored(c: Context, pc: int, at: int, width: int, value: int) -> None:
    assert (pc, at, width, value) in c.m.stores, f"actual store {pc:08x}/{at:08x}/{width}"


def _producer(c: Context, u: int, *, old: int = 0) -> tuple[int, int]:
    p, m = c.p, c.m
    assert 0 <= u <= 65535 and 0 <= old <= 65535
    c.seed(p["word"], u.to_bytes(2, "big"), "incoming producer U16")
    m.r[15], m.pr = STACK_TOP, RETURN
    c.seed(p["old"], old.to_bytes(2, "big"), "incoming independent filter state")
    writes = set().union(*(_cells(p[key], 2) for key in
                          ("fine", "coarse", "intermediate", "old", "fifth")))
    c.run(p["producer"], p["producer_stop"], writes | {p["capped"]},
          stack=0 if p is JK else 16)
    q, k = u >> 3, m.data[p["coefficient"]]
    expected = ((old * (256 - k) + q * k) >> 8) & 65535
    if expected == old and expected < q:
        expected += 1
    assert m.peek(p["old"], 2) == expected, "actual independent filter state"
    assert m.peek(p["intermediate"], 2) == q
    if p is JK:
        assert m.r[15] == STACK_TOP
        assert {0x3B898, 0x3B8C0, 0x3B8C2, 0x3B8E8, 0x3B8EA} <= set(m.executed)
        assert m.pr == 0x3B8EC, "producer BSR and real word-store delay slot"
    else:
        assert m.r[15] == STACK_TOP - 16
    a, r = m.peek(p["fine"], 2), m.peek(p["coarse"], 2)
    assert (a, r) == (u >> 4, u >> 6), "fine/coarse shifts from the same U16"
    assert a == 4 * r + ((u >> 4) & 3), "quantization retains two fine-count bits"
    assert m.peek(p["fifth"], 2) == u >> 5
    assert m.peek(p["capped"]) == min(u >> 5, 255)
    _loaded(c, p["producer_read"], p["word"], 2)
    _stored(c, p["fine_store"], p["fine"], 2, a)
    _stored(c, p["coarse_store"], p["coarse"], 2, r)
    return a, r


def _snapshot(c: Context) -> int:
    p, m = c.p, c.m
    a, r = m.peek(p["fine"], 2), m.peek(p["coarse"], 2)
    # Incoming unused lanes exclude every cell produced by the prior windows.
    # In particular A/R and the SH7059 filter state are never calculated seeds.
    for i in range(p["source_size"]):
        at = p["source"] + i
        if at not in c.outputs:
            c.seed(at, bytes([(37 + 3 * i) & 255]), "incoming unrelated copy lane")
    if p is JK:
        expected_block = bytes(m.peek(p["source"]+i) for i in range(p["source_size"]))
        initial_sp = m.r[15]
        c.run(0x20F6C, 0x20F6E)
        c.run(0x20FC0, 0x20FC2)
        c.run(p["copy_start"], p["copy_stop"],
              _cells(p["destination"], p["destination_size"]), stack=4)
        assert m.pr == 0x20FD0
        assert {0x20FCC, 0x20FCE, 0x22238, 0x2223A, 0x22280, 0x22282} <= set(m.executed)
        assert m.r[15] == initial_sp, "real copy stack restoration"
        actual_block = bytes(m.peek(p["destination"]+i) for i in range(p["destination_size"]))
        assert actual_block == expected_block, "actual complete declared copy count and lanes"
        _loaded(c, 0x22234, 0x222B8, 4)
        _loaded(c, 0x22262, p["fine"] - 2, 4)
        _stored(c, 0x22268, p["coordinate"] - 2, 4, m.peek(p["fine"] - 2, 4))
    else:
        c.seed(p["source"] + 0x39, b"\x5a", "incoming unrelated flag byte")
        c.run(p["copy_start"], p["copy_stop"], _cells(p["destination"], p["destination_size"]))
        _loaded(c, p["copy_load"], p["fine"], 4)
        _stored(c, p["copy_store"], p["coordinate"], 4, m.peek(p["fine"], 4))
    assert (m.peek(p["coordinate"], 2), m.peek(p["copied_coarse"], 2)) == (a, r), "actual snapshot lanes"
    return a


def _pid(c: Context, *, selector: int = 0x0C) -> bytes:
    p, m = c.p, c.m
    m.r[15], m.r[0] = STACK_TOP, selector
    c.seed(p["cursor"], b"\x05", "incoming selected-response cursor")
    if p is not JK:
        c.seed(STACK_TOP + 0x10, bytes(20), "incoming saved selected-handler registers")
        c.seed(STACK_TOP + 0x18, RETURN.to_bytes(4, "big"), "incoming selected-handler return")
    first_load, first_store, first_pc = len(m.loads), len(m.stores), len(m.executed)
    if selector != 0x0C:
        c.run(p["selected"], p["miss"])
        assert not m.loads[first_load:] and not m.stores[first_store:], "other selector does not read RPM RAM or publish"
        return b""
    r = m.peek(p["coarse"], 2)
    writes = {p["cursor"]} | _cells(p["response"] + 5, 2)
    writes |= _cells(STACK_TOP + 0x1C, 8) if p is JK else _cells(STACK_TOP + 8, 2)
    c.run(p["selected"], p["selected_stop"], writes, extra_stops=(p["miss"],))
    expected = min(50 * r, 65535)
    payload = bytes([m.peek(p["response"] + 5), m.peek(p["response"] + 6)])
    assert payload == expected.to_bytes(2, "big"), "PID0C multiplier, saturation and high/low order"
    assert m.peek(p["cursor"]) == 7
    _loaded(c, p["pid_read"], p["coarse"], 2)
    actual = [s for s in m.stores[first_store:] if s[0] == p["response_store"]]
    assert actual == [(p["response_store"], p["response"] + 5, 1, payload[0]),
                      (p["response_store"], p["response"] + 6, 1, payload[1])], "two actual byte writer stores"
    executed = m.executed[first_pc:]
    assert executed.count(p["writer"]) == 2
    for call in (p["call1"], p["call2"]):
        assert call in executed and call + 2 in executed, "real PID call and delay slot"
    assert m.r[15] == (STACK_TOP if p is JK else STACK_TOP + 36)
    return payload


def _frame_contract(data: bytes, p: dict) -> None:
    start = p["frame_entry"]
    pushes = tuple(_word(data, start + 2 * i) for i in range(12))
    assert pushes == (0x2F86, 0x2F96, 0x2FA6, 0x2FB6, 0x2FC6, 0x2FD6,
                      0x2FE6, 0x4F22, 0xFFCB, 0xFFEB, 0xFFFB, 0x4F13)
    allocate = _word(data, start + 28)
    assert allocate >> 8 == 0x7F
    assert 48 - sext(allocate & 255, 8) == p["frame"], "static FPU-inclusive net frame"
    assert _word(data, p["cvtc_call"]) & 0xF0FF == 0x400B
    assert _word(data, p["cvtc_call"] + 2) >> 12 == 0xF, "CVTC call has an excluded FPU delay slot"


def _static_preservation(data: bytes, name: str) -> None:
    # The structural decoder checks conservation, not floating-point results.
    # Every slice has explicit exits. Called bodies are independently closed.
    from kb import sh2

    def decode(pc):
        return sh2.decode(_word(data, pc), pc)

    bodies, windows, pcs = {}, [], set()
    for item in FIXTURES["static_preservation"][name]:
        for window in item["windows"]:
            start, end = (int(window[key], 16) for key in ("start", "end"))
            assert start < end and start % 2 == end % 2 == 0, "static window geometry"
            assert window["kind"] in ("slice", "body"), "static window kind"
            assert window["fallthrough_exit"] == (
                window["end"] if window["kind"] == "slice" else None), "static exit declaration"
            nodes = set(range(start, end, 2))
            for pc in nodes:
                assert any(a <= pc and pc+2 <= b for a, b in ROM_RANGES[name]), "static preservation retention"
                assert item["register"] not in decode(pc).writes, "static incoming-register conservation"
            pcs.update(nodes)
            if window["kind"] == "body":
                assert start not in bodies or bodies[start] == nodes, "static called-body geometry"
                bodies[start] = nodes
            windows.append((window, start, end, nodes))

    indirect = {}
    for item in FIXTURES["static_calls"][name]:
        call, load, pool, target = (int(item[key], 16) for key in ("call", "load", "pool", "target"))
        assert any(a <= pool and pool+4 <= b for a, b in ROM_RANGES[name]), "static call literal retention"
        assert {call, call+2, load, target} <= pcs, "static called-body/delay retention"
        loaded, transfer = decode(load), decode(call)
        assert loaded.value == ("pool", pool, 4), "static call pointer load"
        assert loaded.dest == ((_word(data, call) >> 8) & 15), "static call pointer register"
        assert int.from_bytes(data[pool:pool+4], "big") == target, "static call target"
        assert transfer.flow in ("call", "jump") and transfer.delayed, "static indirect transfer kind"
        assert target in bodies, "static complete called-body entry"
        assert call not in indirect, "static indirect transfer uniqueness"
        indirect[call] = (load, target, loaded.dest)

    successors = {}
    for window, start, end, nodes in windows:
        declared = {int(pc, 16): int(target, 16)
                    for pc, target in window["branch_exits"].items()}
        edges = [{"pc": f"{pc:08x}", "flow": insn.flow,
                  "target": f"{insn.target:08x}" if insn.target is not None else None,
                  "delayed": insn.delayed}
                 for pc in sorted(nodes) if (insn := decode(pc)).flow]
        assert edges == window["edges"], "static transfer contract"
        assert set(declared) <= {int(edge["pc"], 16) for edge in edges
                                if edge["flow"] in ("branch", "cbranch")}, "static boundary declaration"
        slots = {pc+2 for pc in nodes if decode(pc).delayed}
        for slot in slots:
            assert slot in nodes, "static transfer delay retention"
            assert decode(slot).flow is None, "static delay-slot flow"
        for pc in sorted(nodes - slots):
            insn = decode(pc)
            following = pc + (4 if insn.delayed else 2)
            if insn.flow in ("branch", "cbranch"):
                assert insn.target in nodes or declared.get(pc) == insn.target, "static branch closure"
                targets = (insn.target,) if insn.flow == "branch" else (insn.target, following)
            elif insn.flow in ("call", "jump"):
                target = insn.target if insn.target is not None else indirect.get(pc, (None, None, None))[1]
                assert target in bodies, "static called-body closure"
                targets = (following,) if insn.flow == "call" else ()
            elif insn.flow == "return":
                assert window["kind"] == "body" and insn.word == 0x000B, "static return boundary"
                targets = ()
            else:
                assert insn.flow is None, "static known control flow"
                targets = (following,)
            for target in targets:
                if target not in nodes:
                    if insn.flow in ("branch", "cbranch") and declared.get(pc) == target:
                        assert target in pcs or target == end, "static declared branch exit"
                    else:
                        assert target == end and window["fallthrough_exit"] == f"{end:08x}", "static fallthrough closure"
            row = (targets, pc+2 if insn.delayed else None)
            # Overlapping register proofs can end at different explicit slices.
            # Their internal instruction successors must nevertheless agree.
            assert pc not in successors or successors[pc] == row, "static shared flow contract"
            successors[pc] = row

    def preserves(target, register, visited):
        assert target in bodies, "static pointer called-body closure"
        if target in visited:
            return True
        visited = visited | {target}
        for pc in bodies[target]:
            insn = decode(pc)
            if register in insn.writes:
                return False
            if insn.flow in ("call", "jump"):
                nested = insn.target if insn.target is not None else indirect[pc][1]
                if not preserves(nested, register, visited):
                    return False
        return True

    for call, (load, target, register) in indirect.items():
        containing = [(start, nodes) for _, start, _, nodes in windows
                      if call in nodes and load in nodes]
        assert containing, "static pointer definition window"
        start, nodes = max(containing, key=lambda item: len(item[1]))
        pending, seen, reached = [(start, False)], set(), False
        while pending:
            pc, live = pending.pop()
            if pc not in nodes or (pc, live) in seen:
                continue
            seen.add((pc, live))
            insn = decode(pc)
            if pc == call:
                assert live, "static call pointer reaching definition"
                reached = True
                continue
            if pc == load:
                live = True
            elif register in insn.writes:
                live = False
            destinations, slot = successors[pc]
            if slot is not None and register in decode(slot).writes:
                live = False
            if insn.flow == "call":
                nested = insn.target if insn.target is not None else indirect[pc][1]
                live = live and preserves(nested, register, set())
            pending.extend((destination, live) for destination in destinations)
        assert reached, "static call pointer definition reaches transfer"


def _argument(c: Context, a: int) -> int:
    p, m = c.p, c.m
    m.r[15] = STACK_TOP
    if p is JK:
        c.seed(STACK_TOP + 0x34, bytes.fromhex("81a5cccc"), "incoming upper packed lane and destination markers")
        c.run(0x553F4, 0x553F6)
        c.run(p["argument_start"], 0x55464, _cells(STACK_TOP + 0x36, 2))
        _loaded(c, 0x5545A, p["coordinate"], 2)
        _stored(c, 0x55462, STACK_TOP + 0x36, 2, a)
        assert m.peek(STACK_TOP + 0x34, 4) == (0x81A50000 | a)
        entry_sp = STACK_TOP
    else:
        c.seed(STACK_TOP, b"\xa5" * 0x120, "incoming unrelated caller stack lanes")
        for i, (at, width) in enumerate(p["unrelated"]):
            c.seed(at, (0x31 + i).to_bytes(width, "big"), "incoming unrelated caller operand")
        if p is ME:
            m.r[14] = 0xFFFE80BA  # Separate incoming pointer from an excluded caller prefix.
        c.run(p["argument_start"], p["main_target"], stack=p["push_size"])
        entry_sp = STACK_TOP - p["push_size"]
        assert m.r[15] == entry_sp and m.pr == p["main_call"] + 4
        _loaded(c, p["argument_start"] + 2, p["coordinate"], 2)
        _stored(c, p["argument_push"], STACK_TOP - 4, 4, a)
        assert {p["main_call"], p["main_call"] + 2} <= set(m.executed)
    # FPU pushes are bound statically, not executed. This is an explicit local
    # frame context and does not claim that the full callee prologue executed.
    local_sp = entry_sp - p["frame"]
    m.r[15] = local_sp
    c.run(p["argument_read"], p["argument_read"] + 4)
    _loaded(c, p["argument_read"] + 2, local_sp + p["argument_offset"], 4)
    expected = (0x81A50000 | a) if p is JK else a
    assert m.r[p["argument_register"]] == expected, "actual packed RPM argument"
    return local_sp


def _first_axis_word(c: Context, axis: int, a: int) -> None:
    p, m = c.p, c.m
    _loaded(c, p["first_axis_read"], axis + 30, 2)
    assert m.r[1] == STOCK_AXIS[-1], "first unsigned word is the final breakpoint"
    assert (m.r[5] if p is not ME else m.r[6]) == a, "actual unscaled fine-count operand"


def _axes(c: Context, a: int, claim: str) -> None:
    p, m = c.p, c.m
    local_sp = _argument(c, a)
    if p is JK:
        m.r[2] = 0  # Independent clipped-state operand of the integer call delay slot.
        c.run(0x56584, p["vvel_call"])
        assert (m.r[4], m.r[5], m.r[6]) == (p["vvel_values"], p["vvel_axis"], a), "unsigned caller RPM operand"
        c.run(p["vvel_call"], p["axis_stop"], stack=8)
    elif p is ND:
        c.run(0x5F514, 0x5F516)  # Actual wrapper pointer, retained across excluded float slices.
        c.run(0x5F5BE, 0x5F5C4)
        m.r[4] = 0  # Incoming mode-status byte of the separated integer window.
        m.gbr = p["gbr"]  # Explicit excluded-prologue GBR context.
        c.run(0x5F5D6, 0x5F5DA)
        c.run(0x5F5DC, p["axis_stop"], {p["gbr"] + 0x35}, stack=8)
        assert m.r[9] == a, "VVEL call delay conserves the actual RPM operand in R9"
    else:
        c.run(0x6306C, 0x6306E)
        c.run(0x6313C, p["axis_stop"])
        assert m.r[9] == a, "VVEL call delay conserves the actual RPM operand in R9"
    assert {p["vvel_call"], p["vvel_call"] + 2} <= set(m.executed), "real VVEL call/delay"
    _first_axis_word(c, p["vvel_axis"], a)
    if claim == "vvel_duration_running_axis":
        return
    assert claim == "intake_cvtc_target_running_axis"
    if p is JK:
        c.run(0x56596, 0x56598)
        c.run(0x565A0, 0x565A4)
    elif p is ND:
        c.run(0x5F5EE, 0x5F5F0)
        c.run(0x5F5F2, 0x5F5F6)
    else:
        c.run(0x63156, 0x6315E)
    assert (m.r[4], m.r[5], m.r[6]) == (p["cvtc_values"], p["cvtc_axis"], a)
    assert p["cvtc_call"] not in m.executed and p["cvtc_call"] + 2 not in m.executed
    # CVTC's call and FPU delay slot are statically bound only. The callee's
    # incoming SP/PR are declared separately, without pretending to return
    # from the unfinished VVEL lookup or execute an unsupported delay slot.
    m.r[15], m.pr = local_sp, p["cvtc_call"] + 4
    c.run(p["wrapper"], p["axis_stop"], stack=8 if p is not ME else 0)
    _first_axis_word(c, p["cvtc_axis"], a)


def _decoder_records() -> dict:
    base = ROOT / "refs/diagnostics/public/370z-can-logger"
    expected = FIXTURES["source"]
    result = {"pack": tomllib.loads((base / "source_pack.toml").read_text())}
    for key, filename, field, value in (
        ("document", "documents.csv", "id", expected["document"]["id"]),
        ("parameter", "diagnostic_parameters.csv", "source_fragment_id", expected["fragment"]["id"]),
        ("request", "diagnostic_requests.csv", "source_fragment_id", expected["fragment"]["id"]),
    ):
        with (base / filename).open(newline="", encoding="utf-8") as stream:
            rows = [r for r in csv.DictReader(stream) if r[field] == value]
        assert len(rows) == 1
        result[key] = rows[0]
    rows = [r for line in (base / "fragments.jsonl").read_text().splitlines()
            if (r := json.loads(line))["id"] == expected["fragment"]["id"]]
    assert len(rows) == 1
    result["fragment"], result["row"] = rows[0], json.loads(rows[0]["text"])
    return result


def _assert_decoder(records: dict, *, digests: bool = True) -> None:
    for key, expected in FIXTURES["source"].items():
        for field, value in expected.items():
            if not digests and field in ("sha256", "text_sha256"):
                continue
            assert records[key][field] == value, f"independent decoder {key}.{field}"
    f = records["fragment"]
    assert records["row"] == json.loads(f["text"]), "independent decoder row consistency"
    if digests:
        assert hashlib.sha256(f["text"].encode()).hexdigest() == FIXTURES["source"]["fragment"]["text_sha256"]
    _validate_source(records["pack"], records["document"], f)


def _decode(payload: bytes) -> Fraction:
    assert len(payload) == 2
    return Fraction(int.from_bytes(payload, "big"), 4)


def assert_vq37_running_rpm_specification(text: str) -> None:
    normalized = " ".join(text.split())
    assert FIXTURE_PATH in normalized
    for key in TEST_KEYS.values():
        assert f"{THIS_TEST}#{key}" in normalized
    for label, field in (("Source U16", "word"), ("Fine source A", "fine"),
                         ("Coarse source R", "coarse"), ("Axis coordinate x", "coordinate"),
                         ("Coarse snapshot", "copied_coarse"), ("Running VVEL axis", "vvel_axis"),
                         ("Running CVTC axis", "cvtc_axis")):
        row = f"| {label} | " + " | ".join(f"`{PROFILES[n][field]:08x}`" for n in IMAGE_FIXTURES) + " |"
        assert row in normalized, f"published {label} bindings"
    for required in (
        "nominal RPM grid", "A = U >> 4", "R = U >> 6", "Q = min(50*R, 65535)",
        "A = 4*R + ((U >> 4) & 3)", "x = snapshot(A)", "3.125*x", "x/3.125",
        "0, 3.125, 6.25, or 9.375 RPM", "corresponding samples", "quantization",
        "independent snapshot age", "not a measuring-producer proof", "not a sensor inverse",
        "no hardware proof", "community", "homologous_community", "community_reported",
        "not primary SAE, factory, or hardware evidence", "service 01 and request 010C",
        "JK78C `0x70`, 1ND `0x60`, and 1ME3B `0x60`", "first word at `axis+30`",
        "1310/1311", "outside the U16 producer domain", "FPU prologues and CVTC delay slots",
        "complete interpolation", "clock frequency", "crank-event geometry", "parser/dispatcher/transport",
        "Software gates do not grant flashing approval", "unchanged `PathSh2`",
        "no opcode extensions, stubs, relocations, or calculated producer-output seeds",
        "continuous integer prefix `0003b886..0003b7ee`",
        "independent incoming word at `ffff11c6`", "`fffe81d4` and `fffe8fa4`",
        "Each static slice declares start/end, fallthrough exits and exact branch boundaries",
        "delay-slot closure, returns and fallthrough closure",
        "Every indirect call requires a reaching definition of the actual live pointer",
        "Prior nested calls must conserve that pointer register",
    ):
        assert required in normalized, f"published boundary: {required}"
    assert FIXTURES["source"]["fragment"]["id"] in normalized


def _nominal_scale(image, claim: str) -> None:
    name, data, p = image
    _frame_contract(data, p)
    _static_preservation(data, name)
    _assert_decoder(_decoder_records())
    assert_vq37_running_rpm_specification((ROOT / SPEC).read_text())
    axis = p["vvel_axis"] if claim == "vvel_duration_running_axis" else p["cvtc_axis"]
    points = tuple(_word(data, axis + 2*i) for i in range(16))
    assert points == STOCK_AXIS
    assert tuple(Fraction(25*x, 8) for x in points) == NOMINAL_AXIS
    assert tuple(rpm / Fraction(25, 8) for rpm in NOMINAL_AXIS) == points
    # Every fine count, all two-bit residual classes and both low-nibble ends
    # are covered by the producer-domain test; named claims execute their own
    # complete placement on representative word, axis and residual boundaries.
    values = sorted({0, 1, 7, 8, 15, 16, 31, 32, 47, 48, 63, 64, 65, 127, 128,
                     255, 256, 4095, 4096, 16383, 16384, 32767, 32768, 65535}
                    | {min(65535, 16*a + low) for a in (1, 7, 8, 15, 127, 128, 255,
                         256, 511, 512, 1023, 1024, 2047, 2048, 4095, *STOCK_AXIS)
                       for low in (0, 15, 16, 32, 48, 63)})
    for u in values:
        c = Context(name, data, p)
        a, r = _producer(c, u)
        assert _snapshot(c) == a
        payload = _pid(c)
        residual = Fraction(25*a, 8) - _decode(payload)
        assert residual == Fraction(25*(a % 4), 8)
        assert residual in (Fraction(0), Fraction(25, 8), Fraction(25, 4), Fraction(75, 8))
        _axes(c, a, claim)
        c.closure()


def test_vvel_duration_running_nominal_rpm_scale(image) -> None:
    _nominal_scale(image, "vvel_duration_running_axis")


def test_intake_cvtc_target_running_nominal_rpm_scale(image) -> None:
    _nominal_scale(image, "intake_cvtc_target_running_axis")


def test_every_fine_count_low_nibble_end_and_residual_class(image) -> None:
    name, data, p = image
    reached, residuals = set(), set()
    for a in range(4096):
        for low in (0, 15):
            c = Context(name, data, p)
            got, r = _producer(c, 16*a + low)
            assert got == a and r == a >> 2
            residuals.add(Fraction(25*got - 100*r, 8))
            reached.update(c.m.executed)
    assert residuals == {Fraction(0), Fraction(25, 8), Fraction(25, 4), Fraction(75, 8)}
    cap = 0x3B8DC if p is JK else 0x3EFAA if p is ND else 0x4212A
    assert cap in reached, "actual U>>5 byte-cap arm"
    if p is not JK:
        assert p["coarse_store"] in reached and p["coarse_store"]-2 in reached


@pytest.mark.parametrize("old", (0, 1, 1023, 8191, 32768, 65535))
def test_filter_state_does_not_change_fine_and_coarse_words(image, old) -> None:
    name, data, p = image
    for u in (0, 1, 7, 8, 15, 16, 65535):
        _producer(Context(name, data, p), u, old=old)


@pytest.mark.parametrize("word", (0, 1, 3, 4, 255, 256, 1023, 1310, 1311, 32768, 65535))
def test_independent_pid_word_saturation_unsigned_width_and_real_byte_order(image, word) -> None:
    name, data, p = image
    c = Context(name, data, p)
    c.seed(p["coarse"], word.to_bytes(2, "big"), "independent publisher word, not produced from U16")
    payload = _pid(c)
    assert _decode(payload) == Fraction(min(50*word, 65535), 4)
    c.closure()


@pytest.mark.parametrize("selector", (0, 5, 11, 13, 255))
def test_other_pid_selectors_read_no_rpm_source_and_write_no_response(image, selector) -> None:
    name, data, p = image
    c = Context(name, data, p)
    assert _pid(c, selector=selector) == b""
    assert not c.m.loads and not c.m.stores


@pytest.mark.parametrize("a", (0, 1, 127, 128, 255, 256, 4095, 32767, 32768, 65535))
def test_independent_full_word_coordinate_argument_and_first_unsigned_breakpoint(image, a) -> None:
    name, data, p = image
    c = Context(name, data, p)
    c.seed(p["coordinate"], a.to_bytes(2, "big"), "independent coordinate beyond produced A<=4095")
    _axes(c, a, "intake_cvtc_target_running_axis")
    c.closure()


def test_independent_refresh_keeps_the_snapshot_and_breaks_live_pid_equality(image) -> None:
    name, data, p = image
    c = Context(name, data, p)
    assert _producer(c, 16*640) == (640, 160)
    _snapshot(c)
    assert _producer(c, 16*800) == (800, 200)
    assert c.m.peek(p["coordinate"], 2) == 640
    payload = _pid(c)
    assert Fraction(25*640, 8) == 2000 and _decode(payload) == 2500
    _axes(c, 640, "intake_cvtc_target_running_axis")
    # Distinct U16 samples share a fine coordinate; the grid inverse cannot
    # recover discarded source bits or an independently measured engine speed.
    for u in (16*640, 16*640+15):
        assert _producer(Context(name, data, p), u)[0] == 640
    c.closure()


def test_binding_mutants_reject_each_retained_span_and_each_image_pin(image) -> None:
    name, data, _ = image
    for s in FIXTURES["images"][name]["spans"]:
        at, n = int(s["address"], 16), len(bytes.fromhex(s["hex"]))
        for changed in (at, at+n-1):
            with pytest.raises(AssertionError, match="retained span"):
                _bind(_patch(data, changed, bytes([data[changed] ^ 1])), name, image_hash=False)
    with pytest.raises(AssertionError, match="full image identity"):
        _bind(_patch(data, len(data)-1, bytes([data[-1] ^ 1])), name)


@contextmanager
def _executed_rejection(c: Context, site: int):
    with pytest.raises(AssertionError) as failure:
        yield
    assert site in c.m.executed, "mutant must reach the changed instruction or literal consumer"
    message = str(failure.value).lower()
    assert "opcode" not in message and "unsupported" not in message
    assert "step limit" not in message and "execution limit" not in message
    assert "retained span" not in message, "binding rejection is not executable semantics"


@pytest.mark.parametrize("mutation", ("fine-shift", "coarse-shift", "fine-width", "coarse-width", "source-literal"))
def test_executed_producer_mutants_without_binding_shortcut(image, mutation) -> None:
    name, data, p = image
    if mutation == "fine-shift":
        at = 0x3B8C6 if p is JK else 0x3EF90 if p is ND else 0x42112
        value = 0x0009
    elif mutation == "coarse-shift":
        at = 0x3B8E2 if p is JK else 0x3EFB8 if p is ND else 0x42138
        value = 0x0009
    elif mutation == "fine-width":
        at, value = p["fine_store"], (_word(data, p["fine_store"]) & 0xFF00) - 0x100 + (_word(data, p["fine_store"]) & 255)
    elif mutation == "coarse-width":
        at = p["coarse_store"]
        value = (_word(data, at) & 0xFF00) - 0x100 + (_word(data, at) & 255)
    else:
        literal = 0x3B930 if p is JK else 0x3F064 if p is ND else 0x421E4
        at = 0x3B886 if p is JK else 0x3EF50 if p is ND else 0x420D0
        value = (p["word"] + 2).to_bytes(4, "big")
        changed = _patch(data, literal, value)
        c = Context(name, changed, p)
        c.seed(p["word"]+2, b"\x11\x23", "independent alternate source mutant lane")
        with _executed_rejection(c, at):
            _producer(c, 0x8FED)
        _loaded(c, at, literal, 4)
        return
    c = Context(name, _patch(data, at, value), p)
    with _executed_rejection(c, at):
        _producer(c, 0x8FED)



def test_jk_filter_register_clobber_is_executed_and_rejected(image) -> None:
    name, data, p = image
    if p is not JK:
        return
    at = 0x3B8C0
    changed = _patch(data, at, 0xED00)  # Supported MOV #0,R13.
    with pytest.raises(AssertionError, match="retained span"):
        _bind(changed, name, image_hash=False)
    c = Context(name, changed, p)
    with _executed_rejection(c, at):
        _producer(c, 0x8FED, old=0)
    assert (c.m.peek(p["fine"], 2), c.m.peek(p["coarse"], 2)) == (0, 0)
    assert (0x8FED >> 4, 0x8FED >> 6) == (2302, 575)

@pytest.mark.parametrize("mutation", ("source-lane", "destination-lane", "copy-width"))
def test_executed_snapshot_mutants_reach_real_copy_instructions(image, mutation) -> None:
    name, data, p = image
    if p is JK:
        at = 0x22262 if mutation != "destination-lane" else 0x22268
        value = _word(data, at) - 1 if mutation != "copy-width" else 0x0009
    else:
        at = p["copy_load"] if mutation != "destination-lane" else p["copy_store"]
        value = _word(data, at) - 1 if mutation != "copy-width" else 0x0009
    c = Context(name, _patch(data, at, value), p)
    _producer(c, 0x8FED)
    with _executed_rejection(c, at):
        _snapshot(c)


def test_jk_executed_copy_count_and_jump_slot_mutants(image) -> None:
    name, data, p = image
    if p is not JK:
        return
    for changed_at, value, executed_at in ((0x20FCE, 0xE030, 0x20FCE),
                                           (0x222B8, (0x22252).to_bytes(4, "big"), 0x22234)):
        c = Context(name, _patch(data, changed_at, value), p)
        _producer(c, 0x8FED)
        with _executed_rejection(c, executed_at):
            _snapshot(c)


@pytest.mark.parametrize("mutation", ("selector", "multiplier", "saturation", "byte-order", "source", "writer-width", "cursor-slot"))
def test_executed_pid_mutants_reach_supported_changed_sites(image, mutation) -> None:
    name, data, p = image
    locations = ((0x39190, 0x3919C, 0x391A8, 0x391B4, 0x39196) if p is JK else
                 (0x3BD18, 0x3BD22, 0x3BD30, 0x3BD38, 0x3BD1E) if p is ND else
                 (0x3ED64, 0x3ED6E, 0x3ED7C, 0x3ED84, 0x3ED6A))
    if mutation == "selector":
        at, value = locations[0], 0x880D
    elif mutation == "multiplier":
        at, value = locations[1], _word(data, locations[1])-1
    elif mutation == "saturation":
        at, value = locations[2], _word(data, locations[2]) ^ 0x0200
    elif mutation == "byte-order":
        at, value = locations[3], 0x0009
    elif mutation == "source":
        at, value = locations[4], _word(data, locations[4])+2
    elif mutation == "writer-width":
        at, value = p["response_store"], _word(data, p["response_store"])+1
    else:
        at, value = p["cursor_store"], 0x0009
    c = Context(name, _patch(data, at, value), p)
    c.seed(p["coarse"], (1311 if mutation == "saturation" else 160).to_bytes(2, "big"),
           "independent publisher mutant operand")
    c.seed(p["coarse"]+2, b"\x00\x07", "independent alternate word lane")
    with _executed_rejection(c, at):
        _pid(c)


@pytest.mark.parametrize("mutation", ("caller-source", "packed-width", "unsigned-argument", "vvel-axis", "vvel-slot", "kernel-width", "cvtc-axis"))
def test_executed_argument_and_axis_mutants_without_binding_shortcut(image, mutation) -> None:
    name, data, p = image
    if mutation == "caller-source":
        at = 0x5545A if p is JK else p["argument_start"]+2
        value = _word(data, at)-1
    elif mutation == "packed-width":
        at = 0x55462 if p is JK else p["argument_push"]
        # A direct word store is supported by the original interpreter. A
        # predecrement word store is not and must not masquerade as semantics.
        value = _word(data, at)-1 if p is JK else 0x2F21 if p is ND else 0x2F61
    elif mutation == "unsigned-argument":
        at = 0x56586 if p is JK else 0x5E648 if p is ND else 0x62184
        value = (_word(data, at) & 0xFFF0) | 0xF  # Supported EXTS.W instead of EXTU.W.
    elif mutation in ("vvel-axis", "cvtc-axis"):
        literal = (0x56684 if p is JK else 0x5F760 if p is ND else 0x633FC) if mutation == "vvel-axis" else (
            0x56694 if p is JK else 0x5F76C if p is ND else 0x63408)
        at = (0x56588 if p is JK else 0x5F5BE if p is ND else 0x6313C) if mutation == "vvel-axis" else (
            0x565A0 if p is JK else 0x5F5EE if p is ND else 0x63156)
        original = p["vvel_axis"] if mutation == "vvel-axis" else p["cvtc_axis"]
        c = Context(name, _patch(data, literal, (original+2).to_bytes(4, "big")), p)
        c.seed(p["coordinate"], b"\x80\x37", "independent coordinate mutant operand")
        with _executed_rejection(c, at):
            _axes(c, 0x8037, "intake_cvtc_target_running_axis")
        _loaded(c, at, literal, 4)
        return
    elif mutation == "vvel-slot":
        at = p["vvel_call"]+2
        value = 0xE600 if p is JK else 0xE900
    elif mutation == "kernel-width":
        at, value = p["first_axis_read"], _word(data, p["first_axis_read"])-1
    else:
        at = p["first_axis_read"]+2
        value = 0x0009
    c = Context(name, _patch(data, at, value), p)
    c.seed(p["coordinate"], b"\x80\x37", "independent unsigned-coordinate mutant operand")
    with _executed_rejection(c, at):
        _axes(c, 0x8037, "intake_cvtc_target_running_axis")


@pytest.mark.parametrize("mutation", ("formula", "unit", "bytes", "revision", "request", "quality", "parameter-quality", "request-quality"))
def test_decoder_semantic_mutants_fail_even_after_fragment_rehash(mutation) -> None:
    records = _decoder_records()
    _assert_decoder(records)
    if mutation in ("formula", "unit", "bytes"):
        key, value = {"formula": ("Formula", "((A*256)+B)/8"),
                      "unit": ("Units", "rad/s"), "bytes": ("Bytes", "1.0")}[mutation]
        records["row"][key] = value
        records["fragment"]["text"] = json.dumps(records["row"])
        records["fragment"]["text_sha256"] = hashlib.sha256(records["fragment"]["text"].encode()).hexdigest()
    elif mutation == "revision":
        records["pack"]["revision"] = "0"*40
    elif mutation == "request":
        records["request"]["service_id"] = "0x22"
    elif mutation == "quality":
        records["pack"]["source_tier"] = "factory"
    else:
        records["parameter" if mutation == "parameter-quality" else "request"]["verification_status"] = "hardware_pass"
    with pytest.raises(AssertionError, match="independent decoder"):
        _assert_decoder(records, digests=False)


@pytest.mark.parametrize("mutation", ("source", "coordinate", "formula", "residual", "frame", "inverse", "hardware", "producer-window", "branch-boundary", "live-pointer"))
def test_specification_prose_mutants_fail(mutation) -> None:
    text = (ROOT / SPEC).read_text()
    assert_vq37_running_rpm_specification(text)
    before, after = {
        "source": ("`fffe818e`", "`fffe8190`"),
        "coordinate": ("`ffff11a6`", "`ffff11a8`"),
        "formula": ("Q = min(50*R, 65535)", "Q = min(25*R, 65535)"),
        "residual": ("0, 3.125, 6.25, or 9.375 RPM", "0 RPM"),
        "frame": ("JK78C `0x70`", "JK78C `0x60`"),
        "inverse": ("not a sensor inverse", "a sensor inverse"),
        "hardware": ("Software gates do not grant flashing approval", "Software gates grant flashing approval"),
        "producer-window": ("`0003b886..0003b7ee`", "`0003b886..0003b898`"),
        "branch-boundary": ("exact branch boundaries", "unspecified branch boundaries"),
        "live-pointer": ("requires a reaching definition", "does not require a reaching definition"),
    }[mutation]
    assert before in text
    with pytest.raises(AssertionError):
        assert_vq37_running_rpm_specification(text.replace(before, after, 1))


def test_fail_closed_pc_memory_write_and_unsupported_opcode_contract(image) -> None:
    name, data, p = image
    c = Context(name, data, p)
    with pytest.raises(AssertionError, match="unset cell"):
        c.m._read(0xFFFE0000, 1, p["producer_read"])
    c = Context(name, _patch(data, p["producer"], 0xFFFF), p)
    with pytest.raises(AssertionError, match="opcode ffff"):
        c.m.run(p["producer"], (p["producer_stop"],))
    # Unsupported opcodes are an explicit fail-closed test, never a semantic
    # mutant acceptance or a replacement runtime path.
    c = Context(name, data, p)
    with pytest.raises(AssertionError, match="store into the image"):
        c.m._write(p["vvel_axis"], 2, 0, p["first_axis_read"])
    c.m.executed.append(p["vvel_axis"])
    with pytest.raises(AssertionError, match="executed-PC closure"):
        c.closure()
    c = Context(name, data, p)
    c.m.loads.append((p["producer"], 0, 1))
    with pytest.raises(AssertionError, match="ROM-load closure"):
        c.closure()
    c = Context(name, data, p)
    c.m.seed(STACK_TOP + 0x180, b"\0")
    with pytest.raises(AssertionError, match="neighbor guards"):
        c.closure()
    c = Context(name, data, p)
    with pytest.raises(AssertionError, match="allowed writes"):
        _producer_without_write_permission(c)


def _producer_without_write_permission(c: Context) -> None:
    p = c.p
    c.seed(p["word"], b"\x01\x00", "incoming fail-closed source")
    c.seed(p["old"], b"\0\0", "incoming filter")
    c.run(p["producer"], p["producer_stop"])


def assert_compiled_vq37_running_rpm_owner_contract(model) -> None:
    """Require real named TEST and SPEC items on actual compiled owner symbols."""
    from kb import levels, match
    from kb.model import SymbolKey

    functions = {n.name for n in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(n, ast.FunctionDef)}
    assert set(TEST_KEYS.values()) <= functions
    subjects = set()
    for claim, test_key in TEST_KEYS.items():
        expected = FIXTURES["owners"][claim]
        field = "vvel_axis" if claim == "vvel_duration_running_axis" else "cvtc_axis"
        meaning = model.symbols[SymbolKey("jk78c", "axis", JK[field])].meaning
        subjects.add(meaning.key)
        assert meaning.key == claim + "/axis"
        assert {k: meaning.props[k] for k in expected["props"]} == expected["props"]
        assert meaning.home == "jk78c"
        assert {layout: f"{s.address:08x}" for layout, s in meaning.symbols.items()} == {
            layout: row["address"] for layout, row in expected["symbols"].items()}
        assert not meaning.statuses and not expected["statuses"]
        for layout, symbol in meaning.symbols.items():
            assert {k: symbol.value(k) for k in expected["props"]} == expected["props"]
            identities = [e for e in symbol.evidence if e.get("supports", "identity") == "identity"]
            assert identities == expected["symbols"][layout]["identity"], "original identity evidence is preserved"
            for e in identities:
                assert match.verify(model, symbol, e) is None
            notes = symbol.props.get("note", "")
            notes = notes if isinstance(notes, list) else [notes]
            if layout == "1nd":
                assert len(notes) == 2 and all(note.startswith(label) for note, label in
                                              zip(notes, ("1ND0A:", "1ND3B:"))), "separate image-labelled owner notes"
            else:
                assert len(notes) == 1
            for note in notes:
                normalized = " ".join(note.lower().split())
                for token in ("nominal rpm grid", "corresponding samples", "quantization",
                              "independent snapshot age", "not a measuring-producer proof",
                              "not a sensor inverse", "no hardware proof"):
                    assert token in normalized, f"qualified nominal owner note {token}"
            named = [e for e in symbol.evidence if e.get("kind") == "test" and e.get("supports") == "scale"
                     and e.get("path") == THIS_TEST and e.get("key") == test_key]
            assert len(named) == 1, "actual named scale TEST item is required even with SPEC"
            all_scale_tests = [e for e in symbol.evidence
                               if e.get("kind") == "test" and e.get("supports") == "scale"]
            assert all_scale_tests == named, "scale TEST belongs to the actual axis meaning"
            specs = [e for e in symbol.evidence if e.get("kind") == "spec" and e.get("supports") == "scale"
                     and e.get("path") == SPEC]
            assert len(specs) == 1
            assert match.verify(model, symbol, named[0]) is None
            assert match.verify(model, symbol, specs[0]) is None
        actual_links = {(link.type, link.to.key, tuple(sorted(link.roles))): link.evidence
                        for link in meaning.links if link.type == "reader"}
        expected_links = {(link["type"], link["to"], (link["role"],)): link["evidence"]
                          for link in expected["links"]}
        assert actual_links == expected_links, "all original reader roles and evidence are preserved"
    assert not [i for i in levels.check(model) if i.subject in subjects and "scale" in i.message]
    assert_vq37_running_rpm_specification((ROOT / SPEC).read_text())


def test_owner_helper_and_named_claims_have_real_top_level_ast_keys() -> None:
    functions = {n.name for n in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(n, ast.FunctionDef)}
    assert set(TEST_KEYS.values()) <= functions
    assert "assert_compiled_vq37_running_rpm_owner_contract" in functions
    assert "test_missing_running_rpm_scale" not in functions


def test_static_conservation_mutants_are_separate_from_executable_semantics(image) -> None:
    name, data, p = image
    _static_preservation(data, name)
    checks = FIXTURES["static_preservation"][name]
    for item in checks:
        pc = int(item["windows"][0]["start"], 16)
        changed = _patch(data, pc, 0xE000 | (item["register"] << 8))
        with pytest.raises(AssertionError, match="static incoming-register conservation"):
            _static_preservation(changed, name)
    for item in FIXTURES["static_calls"][name]:
        pool = int(item["pool"], 16)
        changed = _patch(data, pool, bytes([data[pool] ^ 1]))
        with pytest.raises(AssertionError, match="static call target"):
            _static_preservation(changed, name)
    # These static negatives are not executed mutants, and do not claim that
    # float intervals, nested helpers or their full returns execute here.



def test_static_conditional_branch_exit_mutant_is_refused_without_binding(image) -> None:
    name, data, p = image
    if p is not JK:
        return
    at = 0x5657E
    changed = _patch(data, at, 0x8D8E)  # Supported BT/S to 0005649e.
    with pytest.raises(AssertionError, match="retained span"):
        _bind(changed, name, image_hash=False)
    with pytest.raises(AssertionError, match="static transfer contract"):
        _static_preservation(changed, name)
    m = PathSh2(changed)
    m.t, m.r[12], m.r[6] = True, 640, 87
    m.seed(m.r[15], bytes.fromhex("12345678"))
    assert m.run(at, (0x564A0,)) == 0x564A0
    assert {at, at+2, 0x5649E} <= set(m.executed)
    assert m.r[12] == 0x12345678
    # A separate real integer negative explains the rejected static edge.
    # It is not execution of the excluded floating-point caller.


def test_static_indirect_pointer_clobber_is_refused_without_binding(image) -> None:
    name, data, p = image
    if p is not ME:
        return
    at = 0x63128
    changed = _patch(data, at, 0x6803)  # Supported MOV R0,R8.
    with pytest.raises(AssertionError, match="retained span"):
        _bind(changed, name, image_hash=False)
    with pytest.raises(AssertionError, match="static call pointer reaching definition"):
        _static_preservation(changed, name)
    m = PathSh2(changed)
    assert m.run(0x63114, (0x63116,)) == 0x63116
    assert m.r[8] == 0x2AEAC
    m.r[0], m.r[11], m.r[6], m.r[13] = 0x6320C, 640, 87, 0
    assert m.run(at, (0x6320E,)) == 0x6320E
    assert {at, 0x63130, 0x63132, 0x6320C} <= set(m.executed)
    assert 0x2AEAC not in m.executed and m.r[11] == 87
    # This negative reaches the actual redirected integer target. It does not
    # execute a floating-point helper or fabricate a completed helper return.

def test_first_axis_unsigned_extension_has_an_observable_independent_negative(image) -> None:
    name, data, p = image
    changed_axis = _patch(data, p["vvel_axis"]+30, bytes.fromhex("8001"))
    extended = p["first_axis_read"]+2
    for remove_extension in (False, True):
        trial = _patch(changed_axis, extended, 0x0009) if remove_extension else changed_axis
        c = Context(name, trial, p)
        c.m.r[4], c.m.r[5], c.m.r[6] = p["vvel_values"], p["vvel_axis"], 0x8037
        c.m.pr = RETURN
        def run_and_assert():
            c.run(p["wrapper"], p["axis_stop"], stack=8 if p is not ME else 0)
            _loaded(c, p["first_axis_read"], p["vvel_axis"]+30, 2)
            assert c.m.r[1] == 0x8001, "unsigned first-word extension"
        if remove_extension:
            with _executed_rejection(c, extended):
                run_and_assert()
        else:
            run_and_assert()
        # The changed breakpoint is an independently declared negative-fixture
        # operand, not a stock calibration or reachable producer coordinate.


@pytest.fixture(scope="module")
def compiled_running_rpm_owners():
    """Compile actual sources without inserting proposed notes or evidence."""
    from kb import compile, repo
    return compile.build(repo.ROOT)


def test_actual_running_rpm_axis_owners_are_integrated(compiled_running_rpm_owners) -> None:
    assert_compiled_vq37_running_rpm_owner_contract(compiled_running_rpm_owners)


@pytest.mark.parametrize("claim", tuple(TEST_KEYS))
@pytest.mark.parametrize("layout", ("jk78c", "1nd", "1me3b"))
@pytest.mark.parametrize("mutation", ("remove-test", "missing-key", "other-claim-key", "remove-spec", "extra-test"))
def test_actual_running_rpm_owner_requires_its_named_test_even_with_spec(
        compiled_running_rpm_owners, claim: str, layout: str, mutation: str) -> None:
    from kb import match
    from kb.model import SymbolKey
    model = compiled_running_rpm_owners
    assert_compiled_vq37_running_rpm_owner_contract(model)
    field = "vvel_axis" if claim == "vvel_duration_running_axis" else "cvtc_axis"
    meaning = model.symbols[SymbolKey("jk78c", "axis", JK[field])].meaning
    symbol, original = meaning.symbols[layout], meaning.symbols[layout].evidence
    try:
        symbol.evidence = deepcopy(original)
        item = next(e for e in symbol.evidence if e.get("kind") == "test" and e.get("supports") == "scale")
        if mutation == "remove-test":
            symbol.evidence.remove(item)
        elif mutation == "missing-key":
            item["key"] = "test_missing_running_rpm_scale"
            assert "defines no function" in match.verify(model, symbol, item)
        elif mutation == "other-claim-key":
            item["key"] = next(key for name, key in TEST_KEYS.items() if name != claim)
            assert match.verify(model, symbol, item) is None
        elif mutation == "remove-spec":
            symbol.evidence = [e for e in symbol.evidence if e.get("kind") != "spec"]
        else:
            extra = deepcopy(item)
            extra["key"] = next(key for name, key in TEST_KEYS.items() if name != claim)
            symbol.evidence.append(extra)
            assert match.verify(model, symbol, extra) is None
        if mutation != "remove-spec":
            assert any(e.get("kind") == "spec" and e.get("supports") == "scale" for e in symbol.evidence)
        assert all(e in symbol.evidence for e in original if e.get("supports") == "identity")
        with pytest.raises(AssertionError):
            assert_compiled_vq37_running_rpm_owner_contract(model)
    finally:
        symbol.evidence = original
    assert_compiled_vq37_running_rpm_owner_contract(model)


@pytest.mark.parametrize("claim", tuple(TEST_KEYS))
@pytest.mark.parametrize("image_index", (0, 1))
@pytest.mark.parametrize("token", ("nominal RPM grid", "corresponding samples", "quantization",
                                   "independent snapshot age", "not a measuring-producer proof",
                                   "not a sensor inverse", "no hardware proof"))
def test_actual_1nd_running_rpm_notes_keep_each_boundary(
        compiled_running_rpm_owners, claim: str, image_index: int, token: str) -> None:
    from kb.model import SymbolKey
    model = compiled_running_rpm_owners
    assert_compiled_vq37_running_rpm_owner_contract(model)
    field = "vvel_axis" if claim == "vvel_duration_running_axis" else "cvtc_axis"
    symbol = model.symbols[SymbolKey("jk78c", "axis", JK[field])].meaning.symbols["1nd"]
    original = symbol.props["note"]
    try:
        notes = original.copy()
        assert token.lower() in notes[image_index].lower()
        notes[image_index] = re.sub(re.escape(token), "", notes[image_index], flags=re.IGNORECASE)
        assert notes[1 - image_index] == original[1 - image_index]
        symbol.props["note"] = notes
        with pytest.raises(AssertionError, match="qualified nominal owner note"):
            assert_compiled_vq37_running_rpm_owner_contract(model)
    finally:
        symbol.props["note"] = original
    assert_compiled_vq37_running_rpm_owner_contract(model)


@pytest.mark.parametrize("claim", tuple(TEST_KEYS))
@pytest.mark.parametrize("image_index", (0, 1))
def test_actual_1nd_running_rpm_notes_keep_each_image_label(
        compiled_running_rpm_owners, claim: str, image_index: int) -> None:
    from kb.model import SymbolKey
    model = compiled_running_rpm_owners
    assert_compiled_vq37_running_rpm_owner_contract(model)
    field = "vvel_axis" if claim == "vvel_duration_running_axis" else "cvtc_axis"
    symbol = model.symbols[SymbolKey("jk78c", "axis", JK[field])].meaning.symbols["1nd"]
    original = symbol.props["note"]
    try:
        notes = original.copy()
        notes[image_index] = notes[image_index].split(":", 1)[1]
        symbol.props["note"] = notes
        with pytest.raises(AssertionError, match="separate image-labelled owner notes"):
            assert_compiled_vq37_running_rpm_owner_contract(model)
    finally:
        symbol.props["note"] = original
    assert_compiled_vq37_running_rpm_owner_contract(model)


@pytest.mark.parametrize("claim", tuple(TEST_KEYS))
def test_actual_running_rpm_identity_and_homology_do_not_ground_scale(
        compiled_running_rpm_owners, claim: str) -> None:
    from kb import levels, match
    from kb.model import SymbolKey
    model = compiled_running_rpm_owners
    assert_compiled_vq37_running_rpm_owner_contract(model)
    field = "vvel_axis" if claim == "vvel_duration_running_axis" else "cvtc_axis"
    meaning = model.symbols[SymbolKey("jk78c", "axis", JK[field])].meaning
    saved = {layout: symbol.evidence for layout, symbol in meaning.symbols.items()}
    props, tables = deepcopy(meaning.props), deepcopy(meaning.tables)
    try:
        for symbol in meaning.symbols.values():
            symbol.evidence = [e for e in symbol.evidence if e.get("supports") != "scale"]
            if symbol.layout != meaning.home:
                expected = b"".join(x.to_bytes(2, "big") for x in STOCK_AXIS)
                item = {"kind": "byte-identical", "supports": "homology", "at": symbol.key.location,
                        "to": meaning.home_symbol.key.location, "sha256": hashlib.sha256(expected).hexdigest()}
                assert match.verify(model, symbol, item) is None
                symbol.evidence.append(item)
        assert any(i.subject == meaning.key and "scale level code lacks grounding" in i.message
                   for i in levels.check(model))
        with pytest.raises(AssertionError, match="actual named scale TEST"):
            assert_compiled_vq37_running_rpm_owner_contract(model)
        assert meaning.props == props and meaning.tables == tables
    finally:
        for layout, symbol in meaning.symbols.items():
            symbol.evidence = saved[layout]
    assert_compiled_vq37_running_rpm_owner_contract(model)
