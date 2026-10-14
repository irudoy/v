"""Six-image gates for the candidate nominal lavender count conversion.

Fixed instruction/literal snapshots and independent image SHA locks bind the
lookups, Q12 state, extraction, local word publication, and signed read/copy.
The unchanged PathSh2 executes every instruction; the subclass only rejects
fractional explicit-axis and optional-floor entries. There are no relocations,
stock-function stubs, manual result stores, or alternate instruction decoders.
Incoming operands and state are explicit seeds, not whole-function reachability
claims. Instruction mutants exist only in memory as negative fixtures.
"""

from __future__ import annotations

import ast
import csv
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from pathlib import Path
import re

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import MASK, STACK_TOP, sext
from tools.mapkit.tests.test_candidate_identity_paths import PathSh2

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_lavender_scale.py"
SPEC = "defs/JK08A.lavender-scale.md"
OWNER = "defs/JK08A.findings.csv"
SCALE_KEY = "test_lavender_nominal_initialized_scale"
IMAGE_FIXTURES = {
    "JK00A": "ed0941de8435d9c61ac093a293757b93ad81bd413270a348c44a8fb6b78b6118",
    "JK03A": "f78929547c08dc5ecde256fb3a6f6f3ef6daa9010e1531b3eac99fd9509225b4",
    "JK03B": "a9aa7a337375b7c9419b0970c32674e98f12ea4215c079898190c5c771a96f1a",
    "JK08A": "ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23",
    "JK00C": "b287ef26373cd6d06a0b9f206648e9b8890a2a5b6cde982bb9d918d77eb69289",
    "JK00D": "e2d7a374b4f7cb42d1963e7aeea424f2147ef01afd231f31b599d83f87f315d3",
}

# Retained byte snapshots, never reconstructed from a loaded image at test time.
HOME_SPANS = (
    (0x62070, "909d401e"),
    (0x621AE, "8d58"),
    (0x6266C, "6aacdd66688c"),
    (0x62674, "927dde65"),
    (0x626AC, "65d3"),
    (0x626B2, "d45781674e0b66a3d45665d381f84e0b66a381fa65d384f7d45362034e0b662c288866038d20666de04702fc6523e202352689199444844388018b09844420088b06dc49903d963d02cee00180442622d44765d3dc454e0b66a3620d9031421842084208a0410c26942a844388018b328444620c22288f261f2685fadc3b650d85f8670d901d35738d0902ce326c0c2642194209420932728908a026000932680c264219420942093272891e4718900847084708a0190c760097009b00c400bc9a300ab09a24"),
    (0x62778, "963ddc286262903b0c26e000a00a804485fadc24620d90334218420842080c26e0018043c61920088968"),
    (0x62808, "00015ce0000264f800013182000131a2000133d2ffff28f8000131c2"),
    (0x62874, "d794e2ff9052622d067e46194609460936268f016263e2ff904966230725666dd58d60634008306c4000305666038f03c2029a3da00a60a3d28836228902e080a0034018d586606f305c6a03c10a6aaf"),
    (0x62920, "0ab00aac7fff9a30"),
    (0x62AC8, "ffff28f800019f1b00009f1cfffee0e4"),
    (0x62B64, "9777"),
    (0x62B94, "c50a817a"),
    (0x264F8, "4f222f466053656dd707470be41e66f6364c8561620d635361614f26d601462b601d00090002674000026984"),
    (0x26984, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be50000026c78"),
    (0x26740, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c0000"),
)
JK00C_SPANS = (
    (0x642E0, "909d401e"),
    (0x6441E, "8d68"),
    (0x648DC, "6aacdd66688c"),
    (0x648E4, "927dde65"),
    (0x6491C, "65d3"),
    (0x64922, "d45781674e0b66a3d45665d381f84e0b66a381fa65d384f7d45362034e0b662c288866038d20666de04702fc6523e202352689199444844388018b09844420088b06dc49903d963d02cee00180442622d44765d3dc454e0b66a3620d9031421842084208a0410c26942a844388018b328444620c22288f261f2685fadc3b650d85f8670d901d35738d0902ce326c0c2642194209420932728908a026000932680c264219420942093272891e4718900847084708a0190c760097009b00c400bc9a400ad89a34"),
    (0x649E8, "963ddc286262903b0c26e000a00a804485fadc24620d90334218420842080c26e0018043c61920088968"),
    (0x64A78, "00018172000270fc000155140001553400015784ffff29a400015554"),
    (0x64AE4, "d794e2ff9052622d067e46194609460936268f016263e2ff904966230725666dd58d60634008306c4000305666038f03c2029a3da00a60a3d28836228902e080a0034018d586606f305c6a03c10a6aaf"),
    (0x64B90, "0ad80ad27fff9a40"),
    (0x64D38, "ffff29a400019f1b00009f1cfffee0e4"),
    (0x64DD4, "9777"),
    (0x64E04, "c50a817a"),
    (0x270FC, "4f222f466053656dd707470be41e66f6364c8561620d635361614f26d601462b601d00090002734400027588"),
    (0x27588, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be5000002787c"),
    (0x27344, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c0000"),
)
JK00D_SPANS = (
    (0x642DC, "909d401e"),
    (0x6441A, "8d68"),
    (0x648D8, "6aacdd66688c"),
    (0x648E0, "927dde65"),
    (0x64918, "65d3"),
    (0x6491E, "d45781674e0b66a3d45665d381f84e0b66a381fa65d384f7d45362034e0b662c288866038d20666de04702fc6523e202352689199444844388018b09844420088b06dc49903d963d02cee00180442622d44765d3dc454e0b66a3620d9031421842084208a0410c26942a844388018b328444620c22288f261f2685fadc3b650d85f8670d901d35738d0902ce326c0c2642194209420932728908a026000932680c264219420942093272891e4718900847084708a0190c760097009b00c400bc9a400ad89a34"),
    (0x649E4, "963ddc286262903b0c26e000a00a804485fadc24620d90334218420842080c26e0018043c61920088968"),
    (0x64A74, "00018192000270fc0001553400015554000157a4ffff29b800015574"),
    (0x64AE0, "d794e2ff9052622d067e46194609460936268f016263e2ff904966230725666dd58d60634008306c4000305666038f03c2029a3da00a60a3d28836228902e080a0034018d586606f305c6a03c10a6aaf"),
    (0x64B8C, "0ad80ad27fff9a40"),
    (0x64D34, "ffff29b800019f1b00009f1cfffee0e4"),
    (0x64DD0, "9777"),
    (0x64E00, "c50a817a"),
    (0x270FC, "4f222f466053656dd707470be41e66f6364c8561620d635361614f26d601462b601d00090002734400027588"),
    (0x27588, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be5000002787c"),
    (0x27344, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c0000"),
)


@dataclass(frozen=True)
class Layout:
    delta: int
    h: int
    t: int
    step: int
    alternate: int
    axis: int
    state: int
    counts: int
    flags: int
    saved: int
    floor_flag: int
    component: int
    wrapper: int
    axis_helper: int
    finisher: int
    fraction: int
    spans: tuple[tuple[int, str], ...]

    def site(self, home: int) -> int:
        return home + self.delta


HOME = Layout(0, 0x131A2, 0x13182, 0x133D2, 0x131C2, 0x15CE0,
              0xFFFF33A8, 0xFFFF33A4, 0xFFFF9A30, 0xFFFF9A24,
              0xFFFF8DBC, 0xFFFF8D6C, 0x264F8, 0x26984, 0x26740, 0x26C78, HOME_SPANS)
JK00C = Layout(0x2270, 0x15534, 0x15514, 0x15784, 0x15554, 0x18172,
               0xFFFF347C, 0xFFFF3476, 0xFFFF9A40, 0xFFFF9A34,
               0xFFFF8DCC, 0xFFFF8D7C, 0x270FC, 0x27588, 0x27344, 0x2787C, JK00C_SPANS)
JK00D = Layout(0x226C, 0x15554, 0x15534, 0x157A4, 0x15574, 0x18192,
               0xFFFF3490, 0xFFFF348A, 0xFFFF9A40, 0xFFFF9A34,
               0xFFFF8DCC, 0xFFFF8D7C, 0x270FC, 0x27588, 0x27344, 0x2787C, JK00D_SPANS)
LAYOUTS = {"JK00A": HOME, "JK03A": HOME, "JK03B": HOME, "JK08A": HOME,
           "JK00C": JK00C, "JK00D": JK00D}
STOCK_H = {
    "JK00A": (7350,) * 6 + (7325,) * 5 + (7310,) * 5,
    "JK03A": (7350,) * 11 + (7290,) * 5,
    "JK03B": (7350,) * 11 + (7290,) * 5,
    "JK08A": (7350,) * 11 + (7290,) * 5,
    "JK00C": (7350,) * 6 + (7325,) * 5 + (7310,) * 5,
    "JK00D": (7350,) * 6 + (7325,) * 5 + (7310,) * 5,
}
EXACT_INPUTS = (0, 1, *range(10, 161, 10), 255)
LINEAR_RAW = (4074, 4075, 6553, 6554, 7350, 9830, 9831, 10625, 10626)


class LavenderSh2(PathSh2):
    """Use the primary interpreter with additional exclusion guards only."""

    def __init__(self, data: bytes, layout: Layout):
        super().__init__(data)
        self.layout = layout

    def _execute(self, pc: int, opcode: int):
        assert pc != self.layout.fraction, "fractional explicit-axis path outside gate"
        assert pc != self.layout.site(0x627A2), "optional floor path outside gate"
        return super()._execute(pc, opcode)


def _bind(data: bytes, layout: Layout) -> None:
    for address, encoded in layout.spans:
        expected = bytes.fromhex(encoded)
        assert data[address:address + len(expected)] == expected, f"stock span {address:08x}"


@pytest.fixture(params=tuple(IMAGE_FIXTURES), scope="module")
def image(request):
    name = request.param
    source = romkit.load(name)
    data, layout = source.data, LAYOUTS[name]
    assert hashlib.sha256(data).hexdigest() == IMAGE_FIXTURES[name], name
    _bind(data, layout)
    assert tuple(source.values(layout.h, 16, "uint16")) == STOCK_H[name]
    assert source.values(layout.t, 16, "uint16") == list(STOCK_H[name])
    assert source.values(layout.step, 16, "uint16") == [0] * 16
    assert source.values(layout.axis, 16, "uint16") == list(range(10, 161, 10))
    return name, data, layout


def _patch(data: bytes, address: int, value: bytes) -> bytes:
    changed = bytearray(data)
    changed[address:address + len(value)] = value
    return bytes(changed)


def _machine(data: bytes, layout: Layout) -> LavenderSh2:
    machine = LavenderSh2(data, layout)
    machine.run(layout.site(0x62070), (layout.site(0x62074),))
    machine.seed(machine.gbr + 0x14, bytes.fromhex("a55ac33c"))
    machine.seed(layout.flags + 0x14, bytes.fromhex("5aa53cc3"))
    machine.seed(layout.floor_flag, bytes(4))
    return machine


def _source(data: bytes, layout: Layout, raw: int | None = None, coordinate: int = 10,
            mode: int = 0, selector: int = 2, initialized: int = 0, saved: int = 0,
            state: int | None = None, saved_state: int | None = None,
            step_coordinate: int = 0) -> LavenderSh2:
    if raw is not None:
        data = _patch(data, layout.h, raw.to_bytes(2, "big") * 16)
    machine = _machine(data, layout)
    machine.r[10], machine.r[8] = coordinate, mode
    machine.seed(layout.flags + 3, bytes([initialized]))
    machine.seed(layout.flags + 4, bytes([saved]))
    machine.seed(STACK_TOP + 0x47, bytes([selector]))
    machine.seed(STACK_TOP + 7, bytes([step_coordinate]))
    if state is not None:
        machine.seed(layout.state, state.to_bytes(4, "big"))
    if saved_state is not None:
        machine.seed(layout.saved, saved_state.to_bytes(4, "big"))
    machine.run(layout.site(0x6266C), (layout.site(0x62672),))
    machine.run(layout.site(0x62674), (layout.site(0x62678),))
    machine.run(layout.site(0x626AC), (layout.site(0x626AE),))
    machine.run(layout.site(0x626B2), (layout.site(0x626B4),))
    # Earlier calculations and the unrelated saved-word copy at 626b4 are excluded.
    machine.run(layout.site(0x626B6), (layout.site(0x628C4),))
    return machine


def _copy(machine: LavenderSh2, layout: Layout) -> int:
    # Mixed calculations between the local publication and this copy are excluded.
    machine.run(layout.site(0x62B64), (layout.site(0x62B66),))
    destination = machine.r[7] + 0x14
    machine.run(layout.site(0x62B94), (layout.site(0x62B98),))
    return destination


def _component(machine: LavenderSh2) -> int:
    return sext(machine.peek(machine.gbr + 0x14, 2), 16)


def test_lavender_nominal_initialized_scale(image) -> None:
    _, data, layout = image
    executed = set()
    for raw in LINEAR_RAW:
        for coordinate in EXACT_INPUTS:
            machine = _source(data, layout, raw, coordinate)
            expected = 10 * raw - 73500
            assert machine.gbr + 0x14 == layout.component
            assert machine.stored(STACK_TOP + 0x14) == [(layout.site(0x626C4), 2, raw)]
            assert machine.stored(layout.state) == [(layout.site(0x62796), 4, raw << 12)]
            assert machine.stored(layout.counts) == [(layout.site(0x62890), 2, raw)]
            assert machine.stored(layout.component) == [(layout.site(0x628C0), 2, expected & 0xFFFF)]
            assert _component(machine) == sext(machine.r[10], 32) == expected
            if raw == 7350:
                assert machine.r[0] == 0xFFFF0000
            assert machine.peek(layout.flags + 3) == 1
            assert machine.peek(layout.component + 2, 2) == 0xC33C
            destination = _copy(machine, layout)
            assert destination == layout.flags + 0x14
            assert (layout.site(0x62B94), layout.component, 2) in machine.loads
            assert machine.stored(destination) == [(layout.site(0x62B96), 2, expected & 0xFFFF)]
            assert machine.r[0] == expected & MASK
            assert machine.peek(destination + 2, 2) == 0x3CC3
            assert any(layout.h <= address < layout.h + 32 and width == 2
                       for _, address, width in machine.loads)
            executed.update(machine.executed)
    assert {layout.wrapper, layout.axis_helper, layout.finisher} <= executed
    assert {layout.site(site) for site in (
        0x626C0, 0x626C2, 0x626C4, 0x62788, 0x62790, 0x62792, 0x62794,
        0x62796, 0x6287E, 0x62880, 0x62882, 0x62890, 0x62898, 0x6289A,
        0x6289C, 0x628A4, 0x628BA, 0x628BC, 0x628C0, 0x628C2,
        0x62B94, 0x62B96)} <= executed
    assert not {layout.fraction, layout.site(0x627A2), layout.site(0x628C4)} & executed


def test_stock_cells_and_exact_endpoint_lookups_keep_the_nominal_domain(image) -> None:
    name, data, layout = image
    reached_cells = set()
    for coordinate in EXACT_INPUTS:
        index = 0 if coordinate <= 10 else min(15, coordinate // 10 - 1)
        raw = STOCK_H[name][index]
        machine = _source(data, layout, coordinate=coordinate)
        assert machine.peek(STACK_TOP + 0x14, 2) == raw
        assert machine.peek(layout.state, 4) == raw << 12
        assert machine.peek(layout.counts, 2) == raw
        assert _component(machine) == 10 * raw - 73500
        selected = layout.h + 2 * index
        assert any(address == selected and width == 2 for _, address, width in machine.loads)
        reached_cells.add(index)
    assert reached_cells == set(range(16))
    assert 4074 <= min(STOCK_H[name]) <= max(STOCK_H[name]) <= 10626
    # The terminal wrapper also reads the following word with fraction zero.
    terminal = _source(data, layout, coordinate=255)
    assert any(address == layout.h + 32 and width == 2 for _, address, width in terminal.loads)
    assert terminal.peek(STACK_TOP + 0x14, 2) == STOCK_H[name][-1]


@pytest.mark.parametrize("raw", (0, 1, 4073, 4074, 10626, 10627, 32767, 32768, 65534, 65535))
def test_raw_extrema_and_signed_saturation_boundaries_are_separate_from_stock(image, raw: int) -> None:
    _, data, layout = image
    machine = _source(data, layout, raw)
    nominal = 10 * raw - 73500
    expected = min(32767, max(-32768, nominal))
    assert machine.peek(STACK_TOP + 0x14, 2) == raw
    assert machine.peek(layout.state, 4) == raw << 12
    assert machine.peek(layout.counts, 2) == raw
    assert machine.stored(layout.component) == [(layout.site(0x628C0), 2, expected & 0xFFFF)]
    assert _component(machine) == sext(machine.r[10], 32) == expected
    destination = _copy(machine, layout)
    assert sext(machine.peek(destination, 2), 16) == expected
    assert machine.r[0] == expected & MASK
    assert (layout.site(0x628B2) in machine.executed) == (nominal < -32768)
    assert (layout.site(0x628A6) in machine.executed) == (nominal > 32767)


@pytest.mark.parametrize("state", (0, 1, 4095, 4096, (65535 << 12) | 4095, 65536 << 12, MASK))
def test_extraction_caps_an_independent_incoming_q12_state(image, state: int) -> None:
    _, data, layout = image
    machine = _machine(data, layout)
    machine.seed(layout.state, state.to_bytes(4, "big"))
    machine.run(layout.site(0x62874), (layout.site(0x628C4),))
    counts = min(65535, state >> 12)
    expected = min(32767, max(-32768, 10 * counts - 73500))
    assert machine.peek(layout.counts, 2) == counts
    assert _component(machine) == expected
    assert not machine.stored(layout.state)
    assert not any(layout.h <= address < layout.h + 32 for _, address, _ in machine.loads)
    assert (layout.site(0x6288A) in machine.executed) == (state >> 12 > 65535)


def test_retained_state_is_a_counterexample_to_universal_h_to_component(image) -> None:
    name, data, layout = image
    machine = _source(data, layout, coordinate=160, initialized=1, state=7350 << 12)
    h = STOCK_H[name][-1]
    assert machine.peek(STACK_TOP + 0x14, 2) == h
    assert machine.peek(layout.state, 4) == 7350 << 12
    assert machine.peek(layout.counts, 2) == 7350
    assert _component(machine) == 0 != 10 * h - 73500
    assert layout.site(0x62750) in machine.executed
    assert layout.site(0x62796) not in machine.executed
    below = _source(data, layout, coordinate=160, initialized=1, state=(h - 1) << 12)
    assert below.peek(layout.state, 4) == h << 12
    assert (layout.site(0x62768), 4, h << 12) in below.stored(layout.state)


def test_alternate_save_and_restore_break_the_universal_h_relation(image) -> None:
    name, data, layout = image
    alternate = _source(data, layout, coordinate=30, mode=1, initialized=1, state=7350 << 12)
    assert alternate.peek(STACK_TOP + 0x14, 2) == 7350
    assert alternate.peek(layout.state, 4) == 7385 << 12
    assert alternate.peek(layout.saved, 4) == 7350 << 12
    assert alternate.peek(layout.flags + 4) == 1
    assert _component(alternate) == 350 != 10 * 7350 - 73500
    assert (layout.site(0x62718), 4, 7385 << 12) in alternate.stored(layout.state)
    assert any(address == layout.alternate + 4 and width == 2 for _, address, width in alternate.loads)
    restored = _source(data, layout, coordinate=160, initialized=1, saved=1,
                       state=7385 << 12, saved_state=7350 << 12)
    assert restored.peek(layout.state, 4) == 7350 << 12
    assert restored.peek(layout.flags + 4) == 0
    assert _component(restored) == 0 != 10 * STOCK_H[name][-1] - 73500
    assert (layout.site(0x62780), 4, 7350 << 12) in restored.stored(layout.state)
    assert (layout.site(0x62786), 1, 0) in restored.stored(layout.flags + 4)


@pytest.mark.parametrize("mode,selector,alternate", ((0, 2, False), (1, 2, True), (1, 3, False), (1, 255, False)))
def test_mode_predicate_selects_normal_or_alternate_initializer(image, mode, selector, alternate) -> None:
    _, data, layout = image
    machine = _source(data, layout, coordinate=30, mode=mode, selector=selector)
    assert machine.peek(layout.state, 4) == (7385 if alternate else 7350) << 12
    assert (layout.site(0x62708) in machine.executed) == alternate
    assert (layout.site(0x62796) in machine.executed) != alternate


@pytest.mark.parametrize("coordinate,step_coordinate", ((15, 0), (10, 15)))
def test_nonzero_fraction_explicit_axis_paths_are_rejected(image, coordinate, step_coordinate) -> None:
    _, data, layout = image
    with pytest.raises(AssertionError, match="fractional explicit-axis path outside gate"):
        _source(data, layout, coordinate=coordinate, step_coordinate=step_coordinate)


def test_optional_floor_entry_is_an_explicit_static_boundary(image) -> None:
    _, data, layout = image
    machine = _machine(data, layout)
    with pytest.raises(AssertionError, match="optional floor path outside gate"):
        machine.run(layout.site(0x627A2), (layout.site(0x627A4),))
    assert not machine.stored(layout.component)


SNAPSHOT_MUTANTS = (0x621AF, 0x62817, 0x62794, 0x62882, 0x628C0, 0x628C1,
                    0x628A2, 0x628A4, 0x62ACC, 0x62AD7, 0x62B94, 0x62B95)


@pytest.mark.parametrize("home_address", SNAPSHOT_MUTANTS)
def test_fixed_snapshots_reject_register_literal_width_branch_and_delay_mutants(image, home_address) -> None:
    _, data, layout = image
    address = layout.site(home_address)
    changed = _patch(data, address, bytes([data[address] ^ 1]))
    with pytest.raises(AssertionError, match="stock span"):
        _bind(changed, layout)


@pytest.mark.parametrize("site,replacement", ((0x62794, "0009"), (0x62882, "0009"), (0x6289C, "0009")))
def test_independently_executed_shift_and_multiplier_mutants_change_publication(image, site, replacement) -> None:
    _, data, layout = image
    stock = _source(data, layout, 7350)
    assert _component(stock) == 10 * 7350 - 73500 == 0
    changed = _patch(data, layout.site(site), bytes.fromhex(replacement))
    # The changed instruction is executed, not rejected by the snapshot binder.
    mutant = _source(changed, layout, 7350)
    assert layout.site(site) in mutant.executed
    assert _component(mutant) != _component(stock)


def test_independently_executed_offset_and_saturation_mutants_change_results(image) -> None:
    _, data, layout = image
    offset = _patch(data, layout.site(0x62AD4), (-73490 & MASK).to_bytes(4, "big"))
    assert _component(_source(data, layout, 7350)) == 0
    assert _component(_source(offset, layout, 7350)) == 10
    upper = _patch(data, layout.site(0x628A2), bytes.fromhex("8d03"))
    assert _component(_source(data, layout, 10627)) == 32767
    assert _component(_source(upper, layout, 10627)) == -32766
    lower = _patch(data, layout.site(0x628B0), bytes.fromhex("8b02"))
    assert _component(_source(data, layout, 4073)) == -32768
    assert _component(_source(lower, layout, 4073)) == 32766


def test_independently_executed_store_and_reader_width_mutants_change_observations(image) -> None:
    _, data, layout = image
    stock = _source(data, layout, 7290)
    expected = 10 * 7290 - 73500
    destination = _copy(stock, layout)
    assert sext(stock.peek(destination, 2), 16) == expected
    store = _patch(data, layout.site(0x628C0), bytes.fromhex("c00a"))
    mutant = _source(store, layout, 7290)
    assert not mutant.stored(layout.component)
    assert mutant.stored(mutant.gbr + 10)[-1] == (layout.site(0x628C0), 1, expected & 255)
    assert _component(mutant) == sext(0xA55A, 16) != expected
    reader = _patch(data, layout.site(0x62B94), bytes.fromhex("c40a"))
    mutant = _source(reader, layout, 7290)
    destination = _copy(mutant, layout)
    assert (layout.site(0x62B94), mutant.gbr + 10, 1) in mutant.loads
    assert sext(mutant.peek(destination, 2), 16) != expected


def test_independently_executed_signedness_mutants_change_register_and_q12_domains(image) -> None:
    _, data, layout = image
    signed = _source(data, layout, 7290)
    consumer = _patch(data, layout.site(0x628C2), bytes.fromhex("6aad"))
    unsigned = _source(consumer, layout, 7290)
    assert _component(signed) == _component(unsigned) == -600
    assert sext(signed.r[10], 32) == -600
    assert unsigned.r[10] == 64936 != sext(signed.r[10], 32)
    initializer = _patch(data, layout.site(0x6278C), bytes.fromhex("620f"))
    stock = _source(data, layout, 0x8001)
    mutant = _source(initializer, layout, 0x8001)
    assert stock.peek(layout.state, 4) == 0x08001000
    assert mutant.peek(layout.state, 4) == 0xF8001000
    assert stock.peek(layout.counts, 2) == 0x8001
    assert mutant.peek(layout.counts, 2) == 0xFFFF


def test_compiled_owner_binds_candidate_scale_evidence_and_ast() -> None:
    from kb import checks, compile, match, repo, store
    from kb.model import SymbolKey

    model = compile.cached(repo.ROOT)
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body
                 if isinstance(node, ast.FunctionDef)}
    with (ROOT / OWNER).open(newline="") as source:
        row = next(row for row in csv.DictReader(source) if row["addr"] == "000131a2")
    assert (row["confidence"], row["role"], row["units"], row["scale_expr"], row["to_byte"], row["scale_conf"]) == (
        "code", "threshold", "centered ffff8d6c channel counts", "x*10-73500", "(x+73500)/10", "candidate")
    assert row["scale_evidence"] == f"test:{THIS_TEST}#{SCALE_KEY}"
    symbol = model.symbols[SymbolKey("7mfk", "tbl", 0x131A2)]
    assert symbol.sources == {store.path_of("tbl", "lavender-butterfly").as_posix()}
    assert checks._owned(model, symbol)
    assert {name: symbol.value(name) for name in ("unit", "scale", "to_raw", "scale_level")} == {
        "unit": row["units"], "scale": row["scale_expr"], "to_raw": row["to_byte"], "scale_level": "candidate"}
    [item] = [item for item in symbol.evidence if item.get("kind") == "test" and item.get("path") == THIS_TEST]
    assert item == {"kind": "test", "supports": "scale", "path": THIS_TEST, "key": SCALE_KEY}
    assert SCALE_KEY in functions and match.verify(model, symbol, item) is None
    broken = {**item, "key": "test_missing_lavender_scale"}
    assert "defines no function" in match.verify(model, symbol, broken)
    original = symbol.evidence
    try:
        symbol.evidence = [broken if existing is item else existing for existing in original]
        issues = [issue for issue in checks.homology(model, subjects={symbol.key.key})
                  if issue.subject == symbol.key.key]
        assert any("test_missing_lavender_scale" in issue.message for issue in issues)
    finally:
        symbol.evidence = original


def test_nominal_inverse_and_specification_keep_the_scoped_contract() -> None:
    from tools import single_source

    for raw in range(65536):
        assert Fraction(10 * raw - 73500 + 73500, 10) == raw
    assert Fraction(32767 + 73500, 10).denominator != 1
    assert Fraction(-32768 + 73500, 10).denominator != 1
    assert Fraction(1 + 73500, 10).denominator != 1
    text = (ROOT / SPEC).read_text()
    assert not re.search(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text, re.IGNORECASE)
    assert THIS_TEST in text and "rom-images/roms.csv" in text and SCALE_KEY in text
    assert SPEC in set(single_source._tracked(".md"))
    for name in IMAGE_FIXTURES:
        assert f'| `{name}` | `IMAGE_FIXTURES["{name}"]` |' in text
        layout, cells = LAYOUTS[name], STOCK_H[name]
        row = f"| `{name}` | `{layout.h:08x}` | {min(cells)}..{max(cells)} | `{layout.component:08x}` |"
        assert row in text
    normalized = " ".join(text.split())
    for required in ("candidate", "10*H-73500", "(x+73500)/10", "4073/4074", "10626/10627",
                     "exact/end points", "nonzero-fraction", "optional floor", "static",
                     "retained", "alternate", "restore", "signed", "low word", "GBR",
                     "not a final actuator output", "physical unit", "no hardware validation"):
        assert required in normalized
