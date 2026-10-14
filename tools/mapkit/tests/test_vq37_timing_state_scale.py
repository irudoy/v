"""Execute the native uint8 timing-state table, byte store, and signed reader.

The retained image identities and spans are independent of the image loaded
by a test. Calibration and instruction mutants exist only in memory. The
machine helpers record execution; the arithmetic oracle is used by assertions
outside those helpers. No lookup is stubbed and no instruction form is added.
"""
from __future__ import annotations

import ast
from copy import deepcopy
from dataclasses import dataclass
import hashlib
from pathlib import Path
import re

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import MASK, STACK_TOP, sext
from tools.mapkit.tests.test_candidate_identity_paths import PathSh2

ROOT = Path(__file__).resolve().parents[3]

THIS_TEST = "tools/mapkit/tests/test_vq37_timing_state_scale.py"
SPEC = "defs/VQ37.timing-state-addend-scale.md"
OWNER = "kb/tbl/timing_state_addend_alternate.toml"
SCALE_KEY = "test_timing_state_addend_alternate_scale"
IMAGE_FIXTURES = {
    "JK78C": "86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d",
    "1ND0A": "650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978",
    "1ND3B": "0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e",
    "1ME3B": "f905b78901b4ca96002a31c2fca8f1cd00dee57b02bea1921a341caa6db2a6f3",
}
STOCK_CELLS = bytes.fromhex("7b83858c9195999d")
MACL_GUARD = 0xA5B6C7D8
MACH_GUARD = 0x87654321

# End-exclusive spans retain instructions, their delay slots, and literal
# words. Interior entries are deliberate: the earlier word/other-count
# entries of the containing JK78C and 1ND functions are not executed.
SPANS = {
    "jk78c": (
        (0x8966, "50"),
        (0x28198, "9007655c35028902d602462be300000b844700e0000288a8"),
        (0x288A8, "450143254501432545014325450143254501432563394019200889064500345c61418541620da005601d345c61408441620c601cd601462b0009000900028568"),
        (0x28568, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c"),
        (0x646C8, "d657dc586060d45fc801e01602ccde578d36652c4e0b00096203db5590467280d4590b24"),
        (0x64748, "4e0b0009620cd6348463c901a01c6503"),
        (0x64790, "622edb2990427280dc310b24"),
        (0x64734, "901e06bc3627"),
        (0x64A02, "9059677c0cbce0463c5c"),
        (0x64774, "0273"),
        (0x6481C, "0271"),
        (0x64820, "ffff23ac"),
        (0x64828, "00008966ffff118c000137e800028198ffff1274"),
        (0x6484C, "000137f0"),
        (0x64850, "000135f8"),
        (0x64860, "ffff44df"),
        (0x64AB8, "0271"),
    ),
    "1nd": (
        (0x287B4, "9007655c35028902d602462be300000b844700e000028ec4"),
        (0x28EC4, "450143254501432545014325450143254501432563394019200889064500345c61418541620da005601d345c61408441620c601cd601462b0009000900028b84"),
        (0x28B84, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c"),
        (0x6F512, "dd79d47984d4db794b0b650c6203e0140f246ce0c46f1fb4640360c3c920a01f6103"),
        (0x6F572, "622edc6560437280c8108d052c20"),
        (0x6F7C8, "65c06620d9766d0c3d5c"),
        (0x6F6F8, "fffe81a800013c22000287b4"),
        (0x6F70C, "fffe8523"),
    ),
    "1me3b": (
        (0x2A9F4, "9026655c35028921635345094509450161072319431843084300345c61408441611c600c3012890967133108061a0137011a461a60734129000b30183018061a0037001a461a4029000b301c000b844700e0"),
        (0x73370, "dd20d42484d6db214b0b650c6203e0140f246ce0c4791fb4640360c3c920a04b6103"),
        (0x73428, "622edc7f60437280c8108d052c20"),
        (0x7367C, "65c06620d9956d0c3d5c"),
        (0x7384A, "84b669c0620c84c1329c"),
        (0x733F4, "fffe818e00013a360002a9f400013a2600013a2e"),
        (0x73628, "fffe84e8"),
    ),
}


@dataclass(frozen=True)
class Arm:
    call: int
    store: int
    cell: int
    stops: tuple[int, ...]
    reader: tuple[int, int, int]
    add: tuple[int, int, int] | None = None


@dataclass(frozen=True)
class Layout:
    name: str
    table: int
    index: int
    lookup: int
    source: int
    table_load: int
    table_literal: int
    target_register: int
    arms: tuple[Arm, ...]
    threshold: int
    endpoint_rts: int
    endpoint_slot: int
    ascending_rts: int
    ascending_slot: int
    descending_rts: int
    descending_slot: int
    byte_loads: tuple[int, int]
    byte_choice: int | None
    gbr: int = 0
    flag_offset: int = 0
    state_base: int = 0


JK78C = Layout(
    "jk78c", 0x137F0, 0xFFFF11A2, 0x28198, 0x646C8,
    0x646CE, 0x6484C, 14,
    (
        Arm(0x64748, 0x6479A, 0xFFFF14E5, (0x6479C,),
            (0x64A02, 0x64A08, 12), (0x64A08, 0x64A0C, 12)),
        Arm(0x646DC, 0x646EA, 0xFFFF14E7, (0x646EC,),
            (0x64734, 0x64738, 6)),
    ),
    0x281AA, 0x281A6, 0x281A8, 0x28592, 0x28594,
    0x28580, 0x28582, (0x288D4, 0x288D6), 0x288C2,
)
ND = Layout(
    "1nd", 0x13C22, 0xFFFE81AC, 0x287B4, 0x6F512,
    0x6F514, 0x6F6FC, 11,
    (Arm(0x6F51A, 0x6F57E, 0xFFFE8523, (0x6F580, 0x6F58A),
         (0x6F7C8, 0x6F7CA, 5), (0x6F7CE, 0x6F7D2, 13)),),
    0x287C6, 0x287C2, 0x287C4, 0x28BAE, 0x28BB0,
    0x28B9C, 0x28B9E, (0x28EF0, 0x28EF2), 0x28EDE,
    0xFFFEB784, 0x6F, 0xFFFE947A,
)
ME = Layout(
    "1me3b", 0x13A2E, 0xFFFE8194, 0x2A9F4, 0x73370,
    0x73372, 0x73404, 11,
    (Arm(0x73378, 0x73434, 0xFFFE84E8, (0x73436, 0x73440),
         (0x7367C, 0x7367E, 5), (0x73682, 0x73686, 13)),),
    0x2AA44, 0x2AA40, 0x2AA42, 0x2AA3C, 0x2AA3E,
    0x2AA2C, 0x2AA2E, (0x2AA10, 0x2AA12), None,
    0xFFFEB8DA, 0x79, 0xFFFE944A,
)
LAYOUTS = {"JK78C": JK78C, "1ND0A": ND, "1ND3B": ND, "1ME3B": ME}


def _patch(data: bytes, address: int, value: bytes) -> bytes:
    result = bytearray(data)
    result[address:address + len(value)] = value
    return bytes(result)


def _bind_spans(data: bytes, layout: Layout) -> None:
    for start, expected in SPANS[layout.name]:
        retained = bytes.fromhex(expected)
        assert data[start:start + len(retained)] == retained, f"retained span {start:08x}"


@pytest.fixture(scope="module", params=tuple(IMAGE_FIXTURES))
def image(request):
    name = request.param
    data = romkit.load(name).data
    assert hashlib.sha256(data).hexdigest() == IMAGE_FIXTURES[name], name
    layout = LAYOUTS[name]
    _bind_spans(data, layout)
    assert data[layout.table:layout.table + 8] == STOCK_CELLS
    return data, layout


def _machine(data: bytes) -> PathSh2:
    machine = PathSh2(data)
    machine.macl = MACL_GUARD
    machine.mach = MACH_GUARD
    machine.seed(STACK_TOP - 8, bytes.fromhex("12345678") + bytes(28) + bytes.fromhex("9abcdef0"))
    return machine


@dataclass
class LookupObservation:
    machine: PathSh2
    returned: int


def _observe_lookup(data: bytes, layout: Layout, index: int) -> LookupObservation:
    machine = _machine(data)
    machine.r[0] = 0xDEADBEEF
    machine.r[4], machine.r[5] = layout.table, index & MASK
    machine.call(layout.lookup)
    return LookupObservation(machine, machine.r[0])


def _seed_consumer(machine: PathSh2, layout: Layout, index: int, flags: int) -> None:
    machine.seed(layout.index, bytes([index]))
    for arm in layout.arms:
        machine.seed(arm.cell - 1, b"\xa5\xcc\xa5")
    if layout is JK78C:
        machine.seed(0xFFFF23AF, b"\0")
    else:
        # These incoming bases and state bytes are unrelated to the scale.
        machine.r[14] = layout.state_base
        machine.seed(layout.state_base, b"\0")
        machine.gbr = layout.gbr
        machine.seed(layout.gbr + layout.flag_offset, bytes([flags]))


def _read_sample(machine: PathSh2, layout: Layout, arm: Arm):
    start, stop, register = arm.reader
    machine.run(start, (stop,))
    samples = [sext(machine.r[register], 32)]
    sums = []
    if arm.add:
        # The independent incoming operand is not an input producer proof.
        if layout is JK78C:
            machine.r[5] = 165
        else:
            machine.r[0] = 165
        start, stop, register = arm.add
        machine.run(start, (stop,))
        sums.append(sext(machine.r[register], 32))
    if layout is ME:
        # A second actual signed reader and its add, with unrelated incoming
        # base/byte explicitly supplied; no intervening function is replaced.
        machine.r[11] = 0xFFFE82AD
        machine.seed(0xFFFE82B3, b"\xa5")
        machine.run(0x7384A, (0x7384E,))
        samples.append(sext(machine.r[9], 32))
        machine.run(0x7384E, (0x73854,))
        sums.append(sext(machine.r[2], 32))
    return tuple(samples), tuple(sums)


@dataclass
class ConsumerObservation:
    machine: PathSh2
    arm: Arm
    table: int | None
    target: int | None
    returned: int
    end: int
    samples: tuple[int, ...]
    sums: tuple[int, ...]


def _observe_consumer(data: bytes, layout: Layout, index: int, mode: int = 0,
                      flags: int = 0) -> ConsumerObservation:
    if layout is JK78C:
        data = _patch(data, 0x8966, bytes([(data[0x8966] & ~1) | mode]))
    machine = _machine(data)
    _seed_consumer(machine, layout, index, flags)
    call = machine.run(layout.source, tuple(arm.call for arm in layout.arms))
    arm = next(arm for arm in layout.arms if arm.call == call)
    table, target = machine.r[4], machine.r[layout.target_register]
    machine.run(call, (call + 4,))
    returned = machine.r[0]
    end = machine.run(call + 4, arm.stops)
    samples, sums = _read_sample(machine, layout, arm)
    return ConsumerObservation(machine, arm, table, target, returned, end, samples, sums)


def _observe_representation(data: bytes, layout: Layout, returned: int,
                            mode: int) -> ConsumerObservation:
    machine = _machine(data)
    _seed_consumer(machine, layout, 0, 0)
    arm = layout.arms[mode]
    machine.r[0] = returned & MASK
    machine.r[11] = layout.lookup
    end = machine.run(arm.call + 4, arm.stops)
    samples, sums = _read_sample(machine, layout, arm)
    return ConsumerObservation(machine, arm, None, None, returned & MASK, end, samples, sums)


def _implicit_byte(cells: bytes, index: int) -> int:
    """Independent arithmetic oracle; observation helpers never call it."""
    c = index & 255
    if c >= 224:
        return cells[7]
    i, remainder = divmod(c, 32)
    left, right = cells[i:i + 2]
    if right >= left:
        return left + (right - left) * remainder // 32
    return left - (left - right) * remainder // 32


def _assert_guards(machine: PathSh2) -> None:
    assert machine.r[15] == STACK_TOP
    assert machine.macl == MACL_GUARD
    assert machine.mach == MACH_GUARD
    assert machine.peek(STACK_TOP - 8, 4) == 0x12345678
    assert machine.peek(STACK_TOP + 24, 4) == 0x9ABCDEF0


def _assert_lookup_trace(machine: PathSh2, layout: Layout, index: int) -> None:
    c = index & 255
    assert layout.lookup in machine.executed
    table_reads = [(pc, at, size) for pc, at, size in machine.loads
                   if layout.table <= at <= layout.table + 8]
    if c >= 224:
        assert table_reads == [(layout.endpoint_slot, layout.table + 7, 1)]
        assert layout.endpoint_rts in machine.executed
    else:
        i = c // 32
        assert table_reads == [(layout.byte_loads[0], layout.table + i, 1),
                               (layout.byte_loads[1], layout.table + i + 1, 1)]
        if layout.byte_choice:
            assert layout.byte_choice in machine.executed
    # Every executed instruction and ROM literal of these slices is retained;
    # the actual calibration cells are the only other ROM reads.
    ranges = [(start, start + len(bytes.fromhex(value))) for start, value in SPANS[layout.name]]
    assert all(any(start <= pc and pc + 2 <= end for start, end in ranges)
               for pc in machine.executed)
    assert all(layout.table <= at and at + size <= layout.table + 8
               or any(start <= at and at + size <= end for start, end in ranges)
               for _, at, size in machine.loads if at < len(machine.data))


def _assert_sample(obs: ConsumerObservation, layout: Layout, raw: int,
                   mode: int = 0, flags: int = 0) -> None:
    machine, arm = obs.machine, layout.arms[mode]
    assert obs.arm == arm
    assert machine.stored(arm.cell) == [(arm.store, 1, (raw - 128) & 255)]
    assert obs.samples == (raw - 128,) * (2 if layout is ME else 1)
    assert obs.sums == (165 + raw - 128,) * (2 if layout is ME else int(arm.add is not None))
    assert machine.peek(arm.cell) == (raw - 128) & 255
    assert machine.peek(arm.cell - 1) == 0xA5
    assert machine.peek(arm.cell + 1) == 0xA5
    assert obs.end == arm.stops[0 if flags & 0x10 else -1]
    reads = [(pc, at, size) for pc, at, size in machine.loads if at == arm.cell]
    first_pc = arm.reader[0] + (4 if layout is JK78C and mode == 0 else 2 if layout is JK78C else 0)
    assert reads == [(first_pc, arm.cell, 1)] + ([(0x7384C, arm.cell, 1)] if layout is ME else [])
    allowed = {arm.cell} | set(range(STACK_TOP - 4, STACK_TOP))
    if layout is not JK78C:
        allowed |= {STACK_TOP + 0x14} | set(range(STACK_TOP + 0x10, STACK_TOP + 0x14))
    assert machine.written() <= allowed
    _assert_guards(machine)


def test_timing_state_addend_alternate_scale(image) -> None:
    """Positive scale evidence for each image, actual lookup, store and reader."""
    data, layout = image
    modes = range(len(layout.arms))
    flags = (0,) if layout is JK78C else (0, 0x10)
    for mode in modes:
        for flag in flags:
            for index in range(256):
                obs = _observe_consumer(data, layout, index, mode, flag)
                raw = _implicit_byte(STOCK_CELLS, index)
                assert obs.table == layout.table and obs.target == layout.lookup
                assert (layout.table_load, layout.table_literal, 4) in obs.machine.loads
                assert obs.returned & 255 == raw
                _assert_lookup_trace(obs.machine, layout, index)
                _assert_sample(obs, layout, raw, mode, flag)
            # Unequal fractional results also continue through the real caller,
            # including both directions, byte stores, and signed readers.
            for cells in (bytes.fromhex("08f908f908f908f9"), bytes.fromhex("f908f908f908f908")):
                calibrated = _patch(data, layout.table, cells)
                for index in (1, 31, 33, 63, 223):
                    obs = _observe_consumer(calibrated, layout, index, mode, flag)
                    assert obs.table == layout.table and obs.target == layout.lookup
                    _assert_lookup_trace(obs.machine, layout, index)
                    _assert_sample(obs, layout, _implicit_byte(cells, index), mode, flag)
            # Every ordinate byte reaches both the interior and endpoint
            # return paths through the actual table address and real lookup.
            for raw in range(256):
                calibrated = _patch(data, layout.table, bytes([raw]) * 8)
                for index in (31, 224):
                    obs = _observe_consumer(calibrated, layout, index, mode, flag)
                    assert obs.table == layout.table and obs.target == layout.lookup
                    _assert_lookup_trace(obs.machine, layout, index)
                    _assert_sample(obs, layout, raw, mode, flag)


@pytest.mark.parametrize("cells", (
    bytes.fromhex("08f908f908f908f9"),
    bytes.fromhex("f908f908f908f908"),
    bytes([193]) * 8,
    STOCK_CELLS,
))
def test_real_implicit8_fractional_domain_and_index_aliases(image, cells: bytes) -> None:
    data, layout = image
    calibrated = _patch(data, layout.table, cells)
    for index in range(256):
        for upper in (0, 0x123400, 0xFFFFFF00):
            obs = _observe_lookup(calibrated, layout, upper | index)
            raw = _implicit_byte(cells, index)
            expected = sext(raw, 8) & MASK if index >= 224 else raw
            assert obs.returned == expected
            _assert_lookup_trace(obs.machine, layout, index)
            _assert_guards(obs.machine)
            if index < 224:
                descending = cells[index // 32 + 1] < cells[index // 32]
                rts, slot = ((layout.descending_rts, layout.descending_slot) if descending
                             else (layout.ascending_rts, layout.ascending_slot))
                assert rts in obs.machine.executed and slot in obs.machine.executed
                allowed = set(range(STACK_TOP - 4, STACK_TOP)) if descending and layout is not ME else set()
                assert obs.machine.written() == allowed
            else:
                assert not obs.machine.stores


@pytest.mark.parametrize("raw", (0, 1, 127, 128, 129, 255))
def test_consumer_upper_return_bits_are_representation_only(image, raw: int) -> None:
    data, layout = image
    for mode in range(len(layout.arms)):
        for upper in (0, 0x100, 0x123400, 0xFFFFFF00):
            obs = _observe_representation(data, layout, upper | raw, mode)
            _assert_sample(obs, layout, raw, mode)
            assert layout.lookup not in obs.machine.executed
            assert obs.table is None and obs.target is None


@pytest.mark.parametrize("mutation", (
    "index-extu", "threshold", "phase", "load-width", "direction",
    "ascending-slot", "descending-slot", "endpoint-slot", "macl", "stack",
))
def test_executed_lookup_mutants_violate_contract_without_snapshot_binding(image, mutation: str) -> None:
    data, layout = image
    cells = bytes.fromhex("08f908f908f908f9")
    index = 31
    if mutation == "index-extu":
        at, word, index = layout.lookup + 2, 0x0009, 0x100
    elif mutation == "threshold":
        at, word, index = layout.threshold, 225, 224
    elif mutation == "phase":
        at, word = {"jk78c": (0x288A8, 0x4509), "1nd": (0x28EC4, 0x4509),
                    "1me3b": (0x2AA0C, 0x4308)}[layout.name]
    elif mutation == "load-width":
        at, word = layout.byte_loads[0], 0x6141
    elif mutation == "direction":
        at = {"jk78c": 0x2856A, "1nd": 0x28B86, "1me3b": 0x2AA1A}[layout.name]
        word = 0x8B00 | (int.from_bytes(data[at:at + 2], "big") & 255)
    elif mutation == "ascending-slot":
        at, word = layout.ascending_slot, 0x0009
    elif mutation == "descending-slot":
        at, word, index = layout.descending_slot, 0x0009, 63
    elif mutation == "endpoint-slot":
        at, word, index = layout.endpoint_slot, 0x8446, 224
    elif mutation == "macl":
        at = {"jk78c": 0x2858C, "1nd": 0x28BA8, "1me3b": 0x2AA38}[layout.name]
        word = 0x0009
    else:
        if layout is ME:
            # This leaf does not use the stack; a valid store exposes that
            # invariant without introducing an unsupported instruction.
            at, word = 0x2AA28, 0x2F76
        else:
            at = 0x2857A if layout is JK78C else 0x28B96
            word = 0x62F2
        index = 63
    mutant = _patch(_patch(data, layout.table, cells), at, word.to_bytes(2, "big"))
    obs = _observe_lookup(mutant, layout, index)
    # Execution occurs outside raises: an unsupported opcode is a failure of
    # the test, not an accepted negative result.
    with pytest.raises(AssertionError):
        raw = _implicit_byte(cells, index)
        assert obs.returned == (sext(raw, 8) & MASK if index & 255 >= 224 else raw)
        _assert_lookup_trace(obs.machine, layout, index)
        _assert_guards(obs.machine)


@pytest.mark.parametrize("mutation", (
    "table-binding", "bias", "store-width", "read-width", "call-slot", "mode-or-delay",
))
def test_executed_consumer_mutants_violate_contract_without_snapshot_binding(image, mutation: str) -> None:
    data, layout = image
    for mode, arm in enumerate(layout.arms):
        index, flags = 31, 0
        if mutation == "table-binding":
            at, value = layout.table_literal, (layout.table + 8).to_bytes(4, "big")
        elif mutation == "bias":
            at = ((0x64796, 0x646E6)[mode] if layout is JK78C
                  else 0x6F578 if layout is ND else 0x7342E)
            value = bytes.fromhex("7281")
        elif mutation == "store-width":
            at = arm.store
            value = bytes.fromhex("0b25" if layout is JK78C else "2c21")
        elif mutation == "read-width":
            at = ((0x64A06, 0x64736)[mode] if layout is JK78C else arm.reader[0])
            value = bytes.fromhex(("0cbd", "06bd")[mode] if layout is JK78C else "65c1")
        elif mutation == "call-slot":
            # Home converts its input in the BT/S slot; both JSR slots are NOP.
            at = 0x646DA if layout is JK78C else arm.call + 2
            value = bytes.fromhex("0009")
        else:
            if layout is JK78C:
                # Invert BT/S to BF/S, retaining its real input-conversion slot.
                at = 0x646D8
                value = (int.from_bytes(data[at:at + 2], "big") ^ 0x0200).to_bytes(2, "big")
            else:
                at, value = arm.store - 2, bytes.fromhex("8905")
        mutant = _patch(data, at, value)
        obs = _observe_consumer(mutant, layout, index, mode, flags)
        with pytest.raises(AssertionError):
            assert obs.table == layout.table and obs.target == layout.lookup
            _assert_lookup_trace(obs.machine, layout, index)
            _assert_sample(obs, layout, _implicit_byte(STOCK_CELLS, index), mode, flags)
        if layout is ME and mutation == "read-width":
            # The later reader is challenged independently of the first one.
            mutant = _patch(data, 0x7384C, bytes.fromhex("69c1"))
            second = _observe_consumer(mutant, layout, index, mode, flags)
            with pytest.raises(AssertionError):
                _assert_sample(second, layout, _implicit_byte(STOCK_CELLS, index), mode, flags)


def test_snapshot_mutants_reject_each_retained_span_separately(image) -> None:
    data, layout = image
    for start, _ in SPANS[layout.name]:
        mutant = _patch(data, start, bytes([data[start] ^ 1]))
        with pytest.raises(AssertionError, match="retained span"):
            _bind_spans(mutant, layout)


def test_compiled_owner_scale_evidence_and_ast_contract() -> None:
    from kb import checks, compile, levels, match, repo
    from kb.model import SymbolKey

    # A fresh compiler model leaves the cached model and durable owner intact.
    model = compile.build(repo.ROOT)
    key = SymbolKey("jk78c", "tbl", JK78C.table)
    meaning = model.symbols[key].meaning
    props = deepcopy(meaning.props)
    statuses = deepcopy(meaning.statuses)
    tables = deepcopy(meaning.tables)
    links = [(link.type, link.to.key, deepcopy(link.props), deepcopy(link.evidence), set(link.sources))
             for link in meaning.links]
    original = {layout: (deepcopy(symbol.props), deepcopy(symbol.evidence))
                for layout, symbol in meaning.symbols.items()}
    assert OWNER in meaning.sources
    assert (meaning.home, meaning.props["cols"], meaning.props["rows"], meaning.props["storage"]) == (
        "jk78c", 8, 1, "uint8")
    assert {name: meaning.props[name] for name in ("unit", "scale", "to_raw", "scale_level", "level")} == {
        "unit": "Timing-state count", "scale": "x-128", "to_raw": "x+128",
        "scale_level": "code", "level": "code"}
    assert {layout: symbol.address for layout, symbol in meaning.symbols.items()} == {
        "jk78c": JK78C.table, "1nd": ND.table, "1me3b": ME.table}
    for symbol in meaning.symbols.values():
        assert {name: symbol.value(name) for name in (
            "unit", "scale", "to_raw", "scale_level", "level", "cols", "rows", "storage")} == {
                "unit": "Timing-state count", "scale": "x-128", "to_raw": "x+128",
                "scale_level": "code", "level": "code", "cols": 8, "rows": 1, "storage": "uint8"}
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(node, ast.FunctionDef)}
    assert SCALE_KEY in functions
    item = {"kind": "test", "supports": "scale", "path": THIS_TEST, "key": SCALE_KEY}
    for symbol in meaning.symbols.values():
        actual = [existing for existing in symbol.evidence
                  if existing.get("kind") == "test" and existing.get("path") == THIS_TEST]
        assert actual == [item]
        assert match.verify(model, symbol, item) is None
        broken = {**item, "key": "test_missing_timing_state_scale"}
        assert "defines no function" in match.verify(model, symbol, broken)
    assert not [issue for issue in levels.check(model, subjects={meaning.key})
                if issue.subject == meaning.key and "scale" in issue.message]
    assert not [issue for issue in checks.homology(model, subjects={symbol.key.key for symbol in meaning.symbols.values()})
                if issue.subject in {symbol.key.key for symbol in meaning.symbols.values()}]
    for symbol in meaning.symbols.values():
        valid = symbol.evidence
        try:
            symbol.evidence = [broken if existing == item else existing for existing in valid]
            issues = [issue for issue in checks.homology(model, subjects={symbol.key.key})
                      if issue.subject == symbol.key.key]
            assert any("test_missing_timing_state_scale" in issue.message for issue in issues)
        finally:
            symbol.evidence = valid
    # Typed identity/homology evidence cannot replace local scale evidence.
    for symbol in meaning.symbols.values():
        symbol.evidence = [existing for existing in symbol.evidence
                           if existing.get("supports") != "scale"]
    assert any(issue.subject == meaning.key and "scale level code lacks grounding" in issue.message
               for issue in levels.check(model, subjects={meaning.key}))
    identity_only = {layout: list(symbol.evidence) for layout, symbol in meaning.symbols.items()}
    try:
        for symbol in meaning.symbols.values():
            if symbol.layout == meaning.home:
                continue
            homologous = {
                "kind": "byte-identical", "supports": "homology",
                "at": symbol.key.location, "to": key.location,
                "sha256": hashlib.sha256(STOCK_CELLS).hexdigest(),
            }
            assert match.verify(model, symbol, homologous) is None
            symbol.evidence.append(homologous)
        assert all(rank >= levels.CODE for rank, _ in match.grounded(
            model, [symbol.key for symbol in meaning.symbols.values()]).values())
        assert any(issue.subject == meaning.key and "scale level code lacks grounding" in issue.message
                   for issue in levels.check(model, subjects={meaning.key}))
    finally:
        for layout, symbol in meaning.symbols.items():
            symbol.evidence = identity_only[layout]
    assert meaning.props == props and meaning.tables == tables and meaning.statuses == statuses
    assert links == [(link.type, link.to.key, link.props, link.evidence, set(link.sources))
                     for link in meaning.links]
    for layout, symbol in meaning.symbols.items():
        old_props, old_evidence = original[layout]
        assert symbol.props == old_props
        assert [item for item in symbol.evidence if item.get("supports") != "scale"] == [
            item for item in old_evidence if item.get("supports") != "scale"]
        symbol.evidence = old_evidence
        assert symbol.evidence == original[layout][1]


def test_inverse_and_specification_bind_only_local_byte_count() -> None:
    for raw in range(256):
        count = sext((raw - 128) & 255, 8)
        assert count == raw - 128
        assert count + 128 == raw
    text = (ROOT / SPEC).read_text()
    assert THIS_TEST in text and SCALE_KEY in text and "rom-images/roms.csv" in text
    assert not re.search(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text, re.IGNORECASE)
    for name in IMAGE_FIXTURES:
        layout = LAYOUTS[name]
        assert (f'| `{name}` | `IMAGE_FIXTURES["{name}"]` | `{layout.name}` | '
                f'`{layout.table:08x}` |') in text
    for layout in (JK78C, ND, ME):
        for start, expected in SPANS[layout.name]:
            if 0x20000 <= start < 0x30000:
                end = start + len(bytes.fromhex(expected))
                assert f"`[{start:08x},{end:08x})`" in text
        for arm in layout.arms:
            assert f"`{arm.cell:08x}`" in text
    normalized = " ".join(text.split())
    for fragment in ("u8(lookup ordinate)-128", "not a wide-register sample", "static RPM axis",
                     "whole-function reachability", "physical time unit", "hardware validation",
                     "before the minimum", "0007367c", "0007384c", "table[8]"):
        assert fragment in normalized
