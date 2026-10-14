"""Execute local VVEL unsigned-word counts and the two task pointer roles.

Image identities and retained instruction/literal spans are independent of the
image under test. Overlays change calibration only, except explicit negative
instruction fixtures. Oracles are used by assertions, never by execution.
1ME3B fractional paths and all floating-point consumers remain outside scope.
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
from tools.mapkit.sh2_interpreter import MASK, RETURN, STACK_TOP, sext
from tools.mapkit.tests.test_candidate_identity_paths import PathSh2

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_vq37_command_count_scales.py"
SPEC = "defs/VQ37.command-count-scales.md"
SCALE_KEYS = ("test_vvel_command_shaft_angle_scale", "test_vvel_command_shaft_angle_second_scale")
MEANINGS = ("vvel_command_shaft_angle", "vvel_command_shaft_angle_second")
IMAGE_FIXTURES = {
    "JK78C": "86387d1de1daa8bf5f98e071eb899be462b7a466cb43f88a96e4dc8b87892b8d",
    "1ND0A": "650d3d3d5f1fdefdb310820a990d6e1a49baa1e072e51ee0019c0b69fd6da978",
    "1ND3B": "0e428cff9e601db74b380ae2e05d3c4ec0ff31313eb7d70aa3badd49a232ec7e",
    "1ME3B": "f905b78901b4ca96002a31c2fca8f1cd00dee57b02bea1921a341caa6db2a6f3",
}
STOCK_VALUES = (12800, 13824, 15360, 17920, 20480, 23040, 25600, 28160,
                30720, 33280, 35840, 37351, 37351, 37351, 37351, 37351)
STOCK_AXIS = (0, 290, 763, 1647, 2643, 3758, 5000, 6390,
              7981, 9889, 12489, 15536, 15536, 15536, 15536, 15536)
RAW_BOUNDARIES = (0, 1, 127, 128, 255, 256, 32767, 32768, 65534, 65535)
STRICT_AXIS = tuple(1000 + 4000 * i for i in range(16))
MACL_GUARD = 0xA5B6C7D8
MACH_GUARD = 0x87654321

SPANS = {
    "jk78c": (
        (0x28320, "4f222f466053656dd707470be41e66f6364c8561620d635361614f26d601462b601d000900028568000287ac"),
        (0x28510, "4f222f466053656dd707470be41e66f6364c8561620d635361614f26d601462b601d000900028920000289ac"),
        (0x287AC, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be50000028aa0"),
        (0x289AC, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be50000028b38"),
        (0x28AA0, "200889462f26e20000194124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412462f6000b6013000be000"),
        (0x28B38, "200889462f26e20000194124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412462f6000b6013000be000"),
        (0x28568, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c"),
        (0x28920, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c"),
        (0x4D3DC, "d06b401e6c63664304126e736d530512d7687420470b666d6203662d"),
        (0x4D58C, "000156dc00028320"),
        (0x4FCB8, "2fe64f224f13d031401e7ffc66436e5304120512d2227420420b666dd22066ed041205127420420b2f01660d67f1"),
        (0x4FD58, "00028510"),
        (0x4FD84, "0001afea"),
        (0x556D8, "dd5e666dde5ed25f64d3420b65e3650de045400806fd646d35438b02e045400805fde001401802fce0014018642c02fc22488b21e0f8d349600c02fd9013642d073d677d34778b02e0f8600c07fde047400802fd655d642d35478b05a00764530d780d5a0d760fb8e047400804fd654d677d357789006573e046400802fd665d642d36438b02e046400806fdd23ee042e50064e30265e0440255666dd239420b65d36203d62d904f934f0625"),
        (0x55820, "0d66a228"),
        (0x55834, "ffff2854"),
        (0x55854, "000156dc000156fc00028320ffff4468"),
    ),
    "1nd": (
        (0x2893C, "4f222f466053656dd707470be41e66f6364c8561620d635361614f26d601462b601d000900028b8400028dc8"),
        (0x28B2C, "4f222f466053656dd707470be41e66f6364c8561620d635361614f26d601462b601d000900028f3c00028fc8"),
        (0x28DC8, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be500000290bc"),
        (0x28FC8, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be50000029154"),
        (0x290BC, "200889462f26e20000194124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412462f6000b6013000be000"),
        (0x29154, "200889462f26e20000194124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412432044124320441243204412462f6000b6013000be000"),
        (0x28B84, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c"),
        (0x28F3C, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c"),
        (0x55158, "6c736d6362436e53662dd56dd46dd36e430b00096603626d662d"),
        (0x55318, "00015c0200015c220002893c"),
        (0x58964, "2fe64f227ff862436e53662dd563d464d364430b00096203612d601381f266edd55ed45fd35f430b00096603626d662d"),
        (0x58B00, "0001b63e0001b65e00028b2c"),
        (0x5E87E, "de4dd44dd14e65e3410b666d650de0bc600c08fd678d35738b02e0bc600c05fde0a4600c04fc624e22488b16e09cd244600c0cfd85213c068f036103e09c600c01fd665d62ad36278f0164a36453664d621d36278f0165136543695d62dd39238d0166d366536063c100e000d533d833da35c10164e3480b666ddc3381a6"),
        (0x5E2B2, "d0af401e"),
        (0x5E570, "fffeb7ba"),
        (0x5E9B4, "00015c2200015c020002893cfffeaa76fffea7c6fffe83dc"),
    ),
    "1me3b": (
        (0x2AF88, "666d6053e21e012d611d3612897be21c012d611d361089763616895fe21a012d611d3610896f36168958e218012d611d3610896836168951e216012d611d361089613616894ae214012d611d3610895a36168943e212012d611d361089533616893ce210012d611d3610894c36168935e20e012d611d361089453616892ee20c012d611d3610893e36168927e20a012d611d3610893736168920e208012d611d3610893036168919e206012d611d3610892936168912e204012d611d361089223616890be202012d611d3610891b36168904e200012d611d36168b1436184628352c8551600d301820088d0de5004601465af12de102415af22df122405af02df103a001e501e500342c2558891b61418541611d600d3012890b67133108061af13d055a0157011a461a60734129000b30183018061af13d055a0057001a461a4029000b301c000b6041"),
        (0x2BCD4, "666d6053e21e012d611d3612897be21c012d611d361089763616895fe21a012d611d3610896f36168958e218012d611d3610896836168951e216012d611d361089613616894ae214012d611d3610895a36168943e212012d611d361089533616893ce210012d611d3610894c36168935e20e012d611d361089453616892ee20c012d611d3610893e36168927e20a012d611d3610893736168920e208012d611d3610893036168919e206012d611d3610892936168912e204012d611d361089223616890be202012d611d3610891b36168904e200012d611d36168b1436184628352c8551600d301820088d0de5004601465af12de102415af22df122405af02df103a001e501e500342c2558891b61418541611d600d3012890b67133108061af13d055a0157011a461a60734129000b30183018061af13d055a0057001a461a4029000b301c000b6041"),
        (0x58FB8, "6c736d6362436e53662dd56fd46fd370430b00096603626d662d"),
        (0x59180, "00015a5600015a760002af88"),
        (0x5C7D4, "2fe64f227ff862436e53662dd563d464d364430b00096203612d601381f266edd55ed45fd35f430b00096603626d662d"),
        (0x5C970, "0001b7180001b7380002bcd4"),
        (0x623D2, "de4cd44cd24d65e3420b666d650de0bc600c0dfd61dd35138b02e0bc600c05fde0a4600c01fc21188b16e09cd244600c0dfd85213d068f036103e09c600c01fd665d629d36278f0164936453664d621d36278f0165136543645d62bd34238d0166b36653d237e000d533d8332261812164e3480b666dd533d7348156"),
        (0x62504, "00015a7600015a560002af88fffeaba4fffeb91afffea8b4fffe83a7"),
    ),
}


@dataclass(frozen=True)
class Pair:
    values: int
    axis: int
    lookup: int
    search: int = 0
    division: int = 0
    finish: int = 0


@dataclass(frozen=True)
class Layout:
    name: str
    pairs: tuple[Pair, Pair]
    primary: tuple[int, int, int]
    second: tuple[int, int, int, int, int]
    task: tuple[int, int, int, int, int, int, int]


JK78C = Layout("jk78c", (
    Pair(0x156FC, 0x156DC, 0x28320, 0x287AC, 0x28AA0, 0x28568),
    Pair(0x1B00A, 0x1AFEA, 0x28510, 0x289AC, 0x28B38, 0x28920),
), (0x4D3DC, 0x4D3F8, 0x4D3F0), (0x4FCB8, 0x4FCE6, 0x4FCD0, 0x4FCDE, 0x4FCE0),
    (0x556D8, 0x55784, 0x556E2, 0x55776, 0x5576C, 0xFFFF44AA, 0xFFFF35BA))
ND = Layout("1nd", (
    Pair(0x15C22, 0x15C02, 0x2893C, 0x28DC8, 0x290BC, 0x28B84),
    Pair(0x1B65E, 0x1B63E, 0x28B2C, 0x28FC8, 0x29154, 0x28F3C),
), (0x55158, 0x55172, 0x55168), (0x58964, 0x58994, 0x58976, 0x5898A, 0x58980),
    (0x5E87E, 0x5E8FC, 0x5E886, 0x5E8F4, 0x5E8E6, 0xFFFEB7BA, 0xFFFEA7D2))
ME = Layout("1me3b", (
    Pair(0x15A76, 0x15A56, 0x2AF88), Pair(0x1B738, 0x1B718, 0x2BCD4),
), (0x58FB8, 0x58FD2, 0x58FC8), (0x5C7D4, 0x5C804, 0x5C7E6, 0x5C7FA, 0x5C7F0),
    (0x623D2, 0x6244E, 0x623DA, 0x62444, 0x6243E, 0xFFFEB91A, 0xFFFEA8C0))
LAYOUTS = {"JK78C": JK78C, "1ND0A": ND, "1ND3B": ND, "1ME3B": ME}


def _patch(data: bytes, address: int, value: bytes) -> bytes:
    result = bytearray(data)
    result[address:address + len(value)] = value
    return bytes(result)


def _words(values) -> bytes:
    return b"".join(value.to_bytes(2, "big") for value in values)


def _calibrate(data: bytes, pair: Pair, values, axis=STOCK_AXIS, extra: int | None = None) -> bytes:
    data = _patch(_patch(data, pair.axis, _words(axis)), pair.values, _words(values))
    return _patch(data, pair.values + 32, _words((extra,))) if extra is not None else data


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
    for pair in layout.pairs:
        assert data[pair.values:pair.values + 32] == _words(STOCK_VALUES)
        assert data[pair.axis:pair.axis + 32] == _words(STOCK_AXIS)
    return data, layout


def _machine(data: bytes) -> PathSh2:
    machine = PathSh2(data)
    machine.macl, machine.mach = MACL_GUARD, MACH_GUARD
    machine.seed(STACK_TOP - 40, bytes.fromhex("12345678") + bytes(0x18C) + bytes.fromhex("9abcdef0"))
    machine.r[14] = 0x14141414
    machine.gbr = 0x15151515
    return machine


def _assert_guards(machine: PathSh2, sp: int = STACK_TOP) -> None:
    assert machine.r[15] == sp
    assert (machine.macl, machine.mach) == (MACL_GUARD, MACH_GUARD)
    assert machine.peek(STACK_TOP - 40, 4) == 0x12345678
    assert machine.peek(STACK_TOP + 0x168, 4) == 0x9ABCDEF0
    assert all(STACK_TOP - 32 <= at and at + size <= STACK_TOP + 0x150
               or at >= 0xFFFE0000 for _, at, size, _ in machine.stores)


def _assert_retained_trace(machine: PathSh2, layout: Layout) -> None:
    spans = [(start, start + len(bytes.fromhex(value))) for start, value in SPANS[layout.name]]
    assert all(any(start <= pc and pc + 2 <= end for start, end in spans) for pc in machine.executed)
    calibration = [(pair.axis, pair.axis + 32) for pair in layout.pairs]
    calibration += [(pair.values, pair.values + 34) for pair in layout.pairs]
    assert all(any(start <= at and at + size <= end for start, end in spans + calibration)
               for _, at, size in machine.loads if at < len(machine.data))
    assert all(not (int.from_bytes(machine.data[pc:pc + 2], "big") & 0xF0FF == 0x405A)
               and machine.data[pc] >> 4 != 0xF for pc in machine.executed)


def _oracle(values, axis, coordinate: int) -> tuple[int, int, int]:
    c = coordinate & 65535
    i = max((i for i, point in enumerate(axis) if point <= c), default=0)
    if c <= axis[0] or c >= axis[-1] or c == axis[i]:
        return values[i], i, 0
    phase = (c - axis[i]) * 65536 // (axis[i + 1] - axis[i])
    left, right = values[i:i + 2]
    delta = abs(right - left) * phase // 65536
    return left + delta if right >= left else left - delta, i, phase


def _observe_lookup(data: bytes, pair: Pair, coordinate: int) -> PathSh2:
    machine = _machine(data)
    machine.r[4], machine.r[5], machine.r[6] = pair.values, pair.axis, coordinate & MASK
    machine.call(pair.lookup)
    return machine


def _assert_lookup(machine: PathSh2, layout: Layout, pair: Pair, coordinate: int,
                   values=STOCK_VALUES, axis=STOCK_AXIS) -> None:
    raw, i, phase = _oracle(values, axis, coordinate)
    assert machine.r[0] == (sext(raw, 16) & MASK if layout is ME else raw)
    reads = [(pc, at, size) for pc, at, size in machine.loads if pair.values <= at <= pair.values + 32]
    if layout is ME:
        assert phase == 0
        assert reads == [(pair.lookup + 0x148, pair.values + 2 * i, 2)]
        assert pair.lookup + 0x146 in machine.executed
        assert pair.lookup + 0xF0 not in machine.executed
        assert not machine.stores
    else:
        assert reads == [(pair.lookup + 0x12, pair.values + 2 * i + 2, 2),
                         (pair.lookup + 0x18, pair.values + 2 * i, 2)]
        assert machine.r[3] == phase
        assert pair.search in machine.executed and pair.finish in machine.executed
        assert pair.lookup + 0xC in machine.executed and pair.lookup + 0x20 in machine.executed
        assert (pair.division in machine.executed) == bool(phase)
        next_value = (values[i + 1] if i < 15 else
                      int.from_bytes(machine.data[pair.values + 32:pair.values + 34], "big"))
        offset = 0x2A if next_value >= values[i] else 0x18
        assert pair.finish + offset in machine.executed
        assert pair.finish + offset + 2 in machine.executed
        if phase:
            assert pair.division + 8 in machine.executed
            assert sum(pc == pair.division + 12 + 4 * j for pc in machine.executed for j in range(32)) == 32
            assert pair.search + 0x28 in machine.executed
            assert pair.search + 0x2E in machine.executed
        else:
            assert pair.search + 0x38 in machine.executed and pair.search + 0x3A in machine.executed
        assert machine.written() <= set(range(STACK_TOP - 16, STACK_TOP))
    _assert_guards(machine)
    _assert_retained_trace(machine, layout)


@dataclass
class ConsumerObservation:
    machine: PathSh2
    arguments: tuple[tuple[int, int, int, int], ...]
    returns: tuple[int, ...]
    spill: int | None


def _observe_consumer(data: bytes, layout: Layout, second: bool, coordinates) -> ConsumerObservation:
    machine = _machine(data)
    machine.r[4], machine.r[5] = (coordinate & MASK for coordinate in coordinates)
    machine.r[6], machine.r[7] = 0x66666666, 0x77777777
    if second:
        start, stop, first, other, _ = layout.second
        calls = (first, other)
    else:
        start, stop, first = layout.primary
        calls = (first,)
    arguments, returned = [], []
    next_pc = start
    for call in calls:
        machine.run(next_pc, (call,))
        machine.run(call, (layout.pairs[int(second)].lookup,))
        arguments.append((call, machine.r[4], machine.r[5], machine.r[6]))
        machine.run(layout.pairs[int(second)].lookup, (call + 4,))
        returned.append(machine.r[0])
        next_pc = call + 4
    machine.run(next_pc, (stop,))
    spill = STACK_TOP - (16 if layout is JK78C else 12) if second else None
    return ConsumerObservation(machine, tuple(arguments), tuple(returned), spill)


def _assert_consumer(obs: ConsumerObservation, layout: Layout, second: bool, coordinates,
                     values=STOCK_VALUES, axis=STOCK_AXIS) -> None:
    machine, pair = obs.machine, layout.pairs[int(second)]
    wanted = [_oracle(values, axis, c)[0] for c in coordinates[:2 if second else 1]]
    calls = layout.second[2:4] if second else (layout.primary[2],)
    assert obs.arguments == tuple((call, pair.values, pair.axis, c & 65535)
                                  for call, c in zip(calls, coordinates))
    assert obs.returns == tuple(sext(raw, 16) & MASK if layout is ME else raw for raw in wanted)
    assert machine.r[6] == wanted[-1]
    if second:
        assert machine.stored(obs.spill) == [(layout.second[4], 2, wanted[0])]
        assert machine.peek(obs.spill, 2) == wanted[0]
        if layout is JK78C:
            assert machine.r[7] == sext(wanted[0], 16) & MASK
            assert (0x4FCE4, obs.spill, 2) in machine.loads
        assert machine.peek(STACK_TOP - 4, 4) == 0x14141414
        assert machine.peek(STACK_TOP - 8, 4) == RETURN
        if layout is JK78C:
            assert machine.peek(STACK_TOP - 12, 4) == 0x15151515
        _assert_guards(machine, STACK_TOP - 16)
        assert machine.written() <= set(range(STACK_TOP - 32, STACK_TOP))
    else:
        _assert_guards(machine)
        assert machine.written() <= set(range(STACK_TOP - 16, STACK_TOP))
    _assert_retained_trace(machine, layout)


def _positive_scale(data: bytes, layout: Layout, second: bool) -> None:
    pair = layout.pairs[int(second)]
    for c in (*STOCK_AXIS, 65535):
        _assert_lookup(_observe_lookup(data, pair, c), layout, pair, c)
        coords = (c, STOCK_AXIS[15 - STOCK_AXIS.index(c)] if c in STOCK_AXIS else 0)
        _assert_consumer(_observe_consumer(data, layout, second, coords), layout, second, coords)
    for values in (tuple(RAW_BOUNDARIES[i % len(RAW_BOUNDARIES)] for i in range(16)),
                   tuple(reversed(RAW_BOUNDARIES)) + (65535,) * 6):
        calibrated = _calibrate(data, pair, values, STRICT_AXIS)
        for i, c in enumerate(STRICT_AXIS):
            machine = _observe_lookup(calibrated, pair, c)
            _assert_lookup(machine, layout, pair, c, values, STRICT_AXIS)
            assert (pair.values + 2 * i) in {at for _, at, size in machine.loads if size == 2}
            coords = (c, STRICT_AXIS[15 - i])
            _assert_consumer(_observe_consumer(calibrated, layout, second, coords), layout,
                             second, coords, values, STRICT_AXIS)
        for c in (0, 999, 61001, 65535):
            _assert_lookup(_observe_lookup(calibrated, pair, c), layout, pair, c, values, STRICT_AXIS)
    if layout is not ME:
        for values in (STOCK_VALUES, tuple(60000 - 3900 * i for i in range(16)), (32768,) * 16):
            calibrated = _calibrate(data, pair, values, STRICT_AXIS)
            for i in range(15):
                for displacement in (1, 1999, 3999):
                    c = STRICT_AXIS[i] + displacement
                    _assert_lookup(_observe_lookup(calibrated, pair, c), layout, pair, c, values, STRICT_AXIS)
                    coords = (c, STRICT_AXIS[14 - i] + 2001)
                    _assert_consumer(_observe_consumer(calibrated, layout, second, coords), layout,
                                     second, coords, values, STRICT_AXIS)
        for c in (1, 289, 291, 762, 764, 1646, 15535):
            _assert_lookup(_observe_lookup(data, pair, c), layout, pair, c)


def test_vvel_command_shaft_angle_scale(image) -> None:
    data, layout = image
    _positive_scale(data, layout, False)


def test_vvel_command_shaft_angle_second_scale(image) -> None:
    data, layout = image
    _positive_scale(data, layout, True)


@pytest.mark.parametrize("second", (False, True))
def test_stock_duplicate_tail_and_actual_extra_word_read(image, second: bool) -> None:
    data, layout = image
    pair = layout.pairs[int(second)]
    assert STOCK_AXIS[11:] == (15536,) * 5
    for extra in RAW_BOUNDARIES:
        calibrated = _calibrate(data, pair, STOCK_VALUES, extra=extra)
        machine = _observe_lookup(calibrated, pair, 15536)
        _assert_lookup(machine, layout, pair, 15536)
        assert machine.r[0] & 65535 == STOCK_VALUES[15]
        extra_reads = [(pc, at, size) for pc, at, size in machine.loads if at == pair.values + 32]
        assert extra_reads == ([] if layout is ME else [(pair.lookup + 0x12, pair.values + 32, 2)])
        assert (pair.values + 30) in {at for _, at, size in machine.loads if size == 2}
    for c in (15536, 15537, 65535):
        machine = _observe_lookup(data, pair, c)
        _assert_lookup(machine, layout, pair, c)
        assert _oracle(STOCK_VALUES, STOCK_AXIS, c)[1:] == (15, 0)


@pytest.mark.parametrize("second", (False, True))
def test_unsigned_input_aliases_and_count_boundaries(image, second: bool) -> None:
    data, layout = image
    pair = layout.pairs[int(second)]
    for raw in RAW_BOUNDARIES:
        calibrated = _calibrate(data, pair, (raw,) * 16, STRICT_AXIS)
        for upper in (0, 0x12340000, 0xFFFF0000):
            for c in (1000, 61000, 65535):
                coordinate = upper | c
                _assert_lookup(_observe_lookup(calibrated, pair, coordinate), layout, pair,
                               coordinate, (raw,) * 16, STRICT_AXIS)
                coords = (coordinate, upper | 1000)
                _assert_consumer(_observe_consumer(calibrated, layout, second, coords), layout,
                                 second, coords, (raw,) * 16, STRICT_AXIS)


@dataclass(frozen=True)
class Bounds:
    upper_first: int
    lower_stack: int
    lower_other: int
    lower_ram: int
    upper_last: int
    flags: int


TASK_CASES = (
    (0, Bounds(0, 0, 0, 0, 0, 0)),
    (3, Bounds(763, 0, 0, 0, 290, 1)),
    (3, Bounds(5000, 0, 0, 0, 5000, 0)),
    (3, Bounds(5000, 2643, 3758, 5000, 7981, 0)),
    (3, Bounds(5000, 5000, 6390, 3758, 7981, 0)),
    (3, Bounds(1647, 1647, 1647, 1647, 1647, 0)),
    (15, Bounds(15536, 0, 0, 0, 12489, 1)),
    (3, Bounds(5000, 2643, 3758, 5000, 2643, 0)),
)


@dataclass
class TaskObservation:
    machine: PathSh2
    arguments: tuple[tuple[int, int, int, int], ...]
    returned: tuple[int, int]
    final_store: int


def _observe_task(data: bytes, layout: Layout, coordinate: int, bounds: Bounds) -> TaskObservation:
    machine = _machine(data)
    machine.r[6] = coordinate & MASK
    start, stop, first, second, _, _, _ = layout.task
    if layout is JK78C:
        for offset, value in ((0x114, bounds.upper_first), (0x11C, bounds.lower_other),
                              (0xF8, bounds.lower_stack), (0x118, bounds.upper_last)):
            machine.seed_word(STACK_TOP + offset, value)
        machine.seed(STACK_TOP + 0x100, bytes([bounds.flags]))
        machine.seed_word(0xFFFF380C, bounds.lower_ram)
    else:
        machine.seed_word(STACK_TOP + 0xBC, bounds.upper_first)
        machine.seed_word(STACK_TOP + 0x9C, bounds.lower_stack)
        machine.seed(STACK_TOP + 0xA4, bytes([bounds.flags]))
        if layout is ND:
            machine.r[10], machine.r[13] = bounds.lower_other, bounds.upper_last
            machine.seed_word(0xFFFEAA78, bounds.lower_ram)
            machine.run(0x5E2B2, (0x5E2B6,))
        else:
            machine.r[9], machine.r[11] = bounds.lower_other, bounds.upper_last
            machine.seed_word(0xFFFEABA6, bounds.lower_ram)
    for cell in (layout.task[5], layout.task[5] + 2, layout.task[6]):
        machine.seed(cell - 1, b"\xa5\xcc\xcc\xa5")
    arguments, returned = [], []
    next_pc = start
    for call in (first, second):
        machine.run(next_pc, (call,))
        machine.run(call, (layout.pairs[0].lookup,))
        arguments.append((call, machine.r[4], machine.r[5], machine.r[6]))
        machine.run(layout.pairs[0].lookup, (call + 4,))
        returned.append(machine.r[0])
        next_pc = call + 4
    machine.run(next_pc, (stop,))
    return TaskObservation(machine, tuple(arguments), tuple(returned), stop - 2)


def _assert_task(obs: TaskObservation, layout: Layout, coordinate: int, bounds: Bounds) -> None:
    pair, machine = layout.pairs[0], obs.machine
    first_raw = _oracle(STOCK_AXIS, STOCK_VALUES, coordinate)[0]
    bounded = min(first_raw, bounds.upper_first)
    if not bounds.flags:
        bounded = max(bounded, bounds.lower_stack, bounds.lower_other, bounds.lower_ram)
    bounded = min(bounded, bounds.upper_last)
    second_raw = _oracle(STOCK_VALUES, STOCK_AXIS, bounded)[0]
    first_call, second_call = layout.task[2:4]
    assert obs.arguments == ((first_call, pair.axis, pair.values, coordinate & 65535),
                             (second_call, pair.values, pair.axis, bounded))
    assert tuple(value & 65535 for value in obs.returned) == (first_raw, second_raw)
    bound_store, bound_cell, result_cell = layout.task[4:]
    assert machine.stored(bound_cell) == [(bound_store, 2, bounded)]
    assert machine.stored(bound_cell + 2) == [(0x55770 if layout is JK78C else
                                             0x5E8F0 if layout is ND else 0x62440, 2, 0)]
    assert machine.stored(result_cell) == [(obs.final_store, 2, second_raw)]
    assert machine.peek(bound_cell - 1) == 0xA5
    assert machine.peek(bound_cell + 4) == 0xA5
    assert machine.peek(result_cell - 1) == machine.peek(result_cell + 2) == 0xA5
    assert all(call + 2 in machine.executed for call in (first_call, second_call))
    assert machine.written() <= set(range(STACK_TOP - 16, STACK_TOP)) | {
        bound_cell, bound_cell + 1, bound_cell + 2, bound_cell + 3, result_cell, result_cell + 1}
    _assert_guards(machine)
    _assert_retained_trace(machine, layout)


def test_actual_task_pointer_roles_bounds_and_stores(image) -> None:
    data, layout = image
    traces = []
    for index, bounds in TASK_CASES:
        coordinate = STOCK_VALUES[index]
        obs = _observe_task(data, layout, coordinate, bounds)
        _assert_task(obs, layout, coordinate, bounds)
        traces.append(obs.machine.executed)
    branches = ((0x556F2, 0x5570A, 0x5571E, 0x55732, 0x5574C, 0x5575C) if layout is JK78C else
                (0x5E896, 0x5E8A8, 0x5E8B6, 0x5E8C6, 0x5E8D2, 0x5E8DE) if layout is ND else
                (0x623EA, 0x623FA, 0x62408, 0x62418, 0x62424, 0x62430))
    for pc in branches:
        following = {trace[i + 1] for trace in traces for i, at in enumerate(trace[:-1]) if at == pc}
        delayed = int.from_bytes(data[pc:pc + 2], "big") >> 8 in (0x8D, 0x8F)
        if delayed:
            assert following == {pc + 2}
            following = {trace[i + 2] for trace in traces for i, at in enumerate(trace[:-2]) if at == pc}
        assert len(following) == 2, f"both task branch outcomes {pc:08x}"


@pytest.mark.parametrize("second", (False, True))
def test_real_unsigned_division_zero_and_nonzero_branches(image, second: bool) -> None:
    data, layout = image
    if layout is ME:
        pytest.skip("1ME3B has no integer division helper in this lookup")
    pair = layout.pairs[int(second)]
    for numerator, denominator in ((0, 0), (65535, 0), (0, 1), (1, 1),
                                   (0xFFFF0000, 65535), (65536, 290), (65535, 4000)):
        machine = _machine(data)
        machine.r[0], machine.r[1], machine.r[2] = denominator, numerator, 0x22222222
        machine.call(pair.division)
        assert machine.r[0] == (numerator // denominator if denominator else 0)
        assert machine.r[2] == 0x22222222
        assert pair.division + (0x8E if denominator else 0x92) in machine.executed
        assert pair.division + (0x90 if denominator else 0x94) in machine.executed
        assert machine.written() == (set(range(STACK_TOP - 4, STACK_TOP)) if denominator else set())
        _assert_guards(machine)
        _assert_retained_trace(machine, layout)


@pytest.mark.parametrize("second", (False, True))
@pytest.mark.parametrize("mutation", ("coordinate-extu", "values-width", "endpoint-slot"))
def test_executed_representation_mutants_without_snapshot_binding(image, second: bool, mutation: str) -> None:
    data, layout = image
    pair = layout.pairs[int(second)]
    values = (32769,) * 16
    data = _calibrate(data, pair, values, STRICT_AXIS)
    if mutation == "coordinate-extu":
        at = pair.lookup if layout is ME else pair.lookup + 6
        word = 0x0009 if layout is ME else 0x6563
        coordinate = 0x12340000 | 1000
    elif mutation == "values-width":
        at = pair.lookup + (0x148 if layout is ME else 0x18)
        word = 0x6040 if layout is ME else 0x6160
        coordinate = 1000
    else:
        at = pair.lookup + (0x148 if layout is ME else 0x20)
        word = 0x0009
        coordinate = 61000
    mutant = _patch(data, at, word.to_bytes(2, "big"))
    machine = _observe_lookup(mutant, pair, coordinate)
    with pytest.raises(AssertionError):
        _assert_lookup(machine, layout, pair, coordinate, values, STRICT_AXIS)


@pytest.mark.parametrize("second", (False, True))
@pytest.mark.parametrize("mutation", ("phase-shift", "division-slot", "direction", "ascending-slot", "descending-slot", "macl", "stack"))
def test_executed_integer_fractional_mutants_without_snapshot_binding(image, second: bool, mutation: str) -> None:
    data, layout = image
    if layout is ME:
        pytest.skip("1ME3B fractional lookup is outside the integer proof")
    pair = layout.pairs[int(second)]
    values = tuple(60000 - 3900 * i for i in range(16)) if mutation in ("descending-slot", "stack") else STOCK_VALUES
    coordinate = STRICT_AXIS[2] + 1999
    if mutation == "phase-shift":
        at, word = pair.search + 0x14, 0x4508
    elif mutation == "division-slot":
        at, word = pair.division + 0x90, 0x0009
    elif mutation == "direction":
        at, word = pair.finish + 2, 0x8B0B
    elif mutation == "ascending-slot":
        at, word = pair.finish + 0x2C, 0x0009
    elif mutation == "descending-slot":
        at, word = pair.finish + 0x1A, 0x0009
    elif mutation == "macl":
        at, word = pair.finish + 0x24, 0x0009
    else:
        at, word = pair.finish + 0x12, 0x62F2
    mutant = _patch(_calibrate(data, pair, values, STRICT_AXIS), at, word.to_bytes(2, "big"))
    machine = _observe_lookup(mutant, pair, coordinate)
    with pytest.raises(AssertionError):
        _assert_lookup(machine, layout, pair, coordinate, values, STRICT_AXIS)


@pytest.mark.parametrize("second", (False, True))
@pytest.mark.parametrize("mutation", ("table-binding", "extu", "call-slot", "spill-width"))
def test_executed_consumer_mutants_without_snapshot_binding(image, second: bool, mutation: str) -> None:
    data, layout = image
    pair = layout.pairs[int(second)]
    coordinates = (STOCK_AXIS[2], STOCK_AXIS[9])
    if mutation == "spill-width" and not second:
        pytest.skip("The primary pre-FPUL slice has no result spill")
    if mutation == "table-binding":
        at = (0x4FD84 if second else 0x4D58C) if layout is JK78C else (
            (0x58B04 if second else 0x5531C) if layout is ND else (0x5C974 if second else 0x59184))
        replacement = (pair.axis if layout is not JK78C else pair.values).to_bytes(4, "big")
    elif mutation == "extu":
        at = ((0x4FCE2 if second else 0x4D3F6) if layout is JK78C else
              (0x58990 if second else 0x5516E) if layout is ND else (0x5C800 if second else 0x58FCE))
        replacement = (0x660C if layout is JK78C else 0x626C).to_bytes(2, "big")
    elif mutation == "call-slot":
        at = layout.second[2] + 2 if second else layout.primary[2] + 2
        replacement = (0xE600).to_bytes(2, "big")
    else:
        at = layout.second[4]
        replacement = (0x2F00 if layout is JK78C else 0x80F4).to_bytes(2, "big")
    mutant = _patch(data, at, replacement)
    obs = _observe_consumer(mutant, layout, second, coordinates)
    with pytest.raises(AssertionError):
        _assert_consumer(obs, layout, second, coordinates)


@pytest.mark.parametrize("mutation", ("first-values", "second-values", "bound-store-width", "result-store-width", "bounds-branch"))
def test_executed_task_binding_mutants_without_snapshot_binding(image, mutation: str) -> None:
    data, layout = image
    index, bounds = TASK_CASES[4]
    if mutation == "first-values":
        at, word = ((0x556E0, 0x64E3) if layout is JK78C else
                    (0x5E880, 0x64E3) if layout is ND else (0x623D4, 0x64E3))
    elif mutation == "second-values":
        at, word = ((0x5576A, 0x64D3) if layout is JK78C else
                    (0x5E8F2, 0x6453) if layout is ND else (0x62442, 0x6453))
    elif mutation == "bound-store-width":
        at, word = layout.task[4], (0x0264 if layout is JK78C else 0xC000 if layout is ND else 0x2260)
    elif mutation == "result-store-width":
        at, word = layout.task[1] - 2, (0x0624 if layout is JK78C else 0x80A6 if layout is ND else 0x8056)
    else:
        at, word = ((0x5574C, 0x8B00) if layout is JK78C else
                    (0x5E8D2, 0x8D01) if layout is ND else (0x62424, 0x8D01))
    mutant = _patch(data, at, word.to_bytes(2, "big"))
    obs = _observe_task(mutant, layout, STOCK_VALUES[index], bounds)
    with pytest.raises(AssertionError):
        _assert_task(obs, layout, STOCK_VALUES[index], bounds)


def test_snapshot_mutants_reject_every_retained_span(image) -> None:
    data, layout = image
    for start, _ in SPANS[layout.name]:
        with pytest.raises(AssertionError, match="retained span"):
            _bind_spans(_patch(data, start, bytes([data[start] ^ 1])), layout)


def test_compiled_owner_scale_evidence_and_ast_contract() -> None:
    from kb import checks, compile, levels, match, repo
    from kb.model import SymbolKey

    model = compile.build(repo.ROOT)
    functions = {node.name for node in ast.parse((ROOT / THIS_TEST).read_text()).body if isinstance(node, ast.FunctionDef)}
    for n, (name, token) in enumerate(zip(MEANINGS, SCALE_KEYS)):
        key = SymbolKey("jk78c", "tbl", JK78C.pairs[n].values)
        meaning = model.symbols[key].meaning
        assert f"kb/tbl/{name}.toml" in meaning.sources
        if n == 0:
            assert " ".join(meaning.props["summary"].split()) == (
                "Unsigned-word conversion between the paired shaft-coordinate array (axis) "
                "and the command-word domain (values). The task first uses command words as "
                "the axis and paired coordinates as values for the bound word at 0xFFFF44AA, "
                "then exchanges those roles for the returned word at 0xFFFF35BA.")
        props, tables, statuses = deepcopy(meaning.props), deepcopy(meaning.tables), deepcopy(meaning.statuses)
        links = [(link.type, link.to.key, deepcopy(link.props), deepcopy(link.evidence), set(link.sources)) for link in meaning.links]
        original = {layout: (deepcopy(symbol.props), deepcopy(symbol.evidence)) for layout, symbol in meaning.symbols.items()}
        assert {k: meaning.props[k] for k in ("unit", "scale", "to_raw", "scale_level", "level", "cols", "rows", "storage")} == {
            "unit": "count", "scale": "x", "to_raw": "x", "scale_level": "code", "level": "code", "cols": 16, "rows": 1, "storage": "uint16"}
        assert {layout: symbol.address for layout, symbol in meaning.symbols.items()} == {
            "jk78c": JK78C.pairs[n].values, "1nd": ND.pairs[n].values, "1me3b": ME.pairs[n].values}
        assert token in functions
        item = {"kind": "test", "supports": "scale", "path": THIS_TEST, "key": token}
        broken = {**item, "key": "test_missing_command_count_scale"}
        try:
            for symbol in meaning.symbols.values():
                assert {k: symbol.value(k) for k in (
                    "unit", "scale", "to_raw", "scale_level", "level", "cols", "rows", "storage")} == {
                    "unit": "count", "scale": "x", "to_raw": "x", "scale_level": "code",
                    "level": "code", "cols": 16, "rows": 1, "storage": "uint16"}
                actual = [e for e in symbol.evidence
                          if e.get("kind") == "test" and e.get("path") == THIS_TEST]
                assert actual == [item]
                assert match.verify(model, symbol, item) is None
                assert "defines no function" in match.verify(model, symbol, broken)
            assert not [i for i in levels.check(model) if i.subject == meaning.key and "scale" in i.message]
            for symbol in meaning.symbols.values():
                valid = symbol.evidence
                symbol.evidence = [broken if e == item else e for e in valid]
                assert any("test_missing_command_count_scale" in i.message
                           for i in checks.homology(model, subjects={symbol.key.key})
                           if i.subject == symbol.key.key)
                symbol.evidence = valid
            for symbol in meaning.symbols.values():
                symbol.evidence = [e for e in symbol.evidence if e.get("supports") != "scale"]
                if symbol.layout != meaning.home:
                    identity = {"kind": "byte-identical", "supports": "homology", "at": symbol.key.location,
                                "to": key.location, "sha256": hashlib.sha256(_words(STOCK_VALUES)).hexdigest()}
                    assert match.verify(model, symbol, identity) is None
                    symbol.evidence.append(identity)
            assert all(rank >= levels.CODE for rank, _ in match.grounded(model, [s.key for s in meaning.symbols.values()]).values())
            assert any(i.subject == meaning.key and "scale level code lacks grounding" in i.message for i in levels.check(model))
            assert meaning.props == props and meaning.tables == tables and meaning.statuses == statuses
            assert links == [(link.type, link.to.key, link.props, link.evidence, set(link.sources)) for link in meaning.links]
        finally:
            for layout, symbol in meaning.symbols.items():
                assert symbol.props == original[layout][0]
                symbol.evidence = original[layout][1]
                assert symbol.evidence == original[layout][1]


def test_inverse_specification_and_home_task_declaration() -> None:
    for raw in RAW_BOUNDARIES:
        assert (raw & 65535) == raw
    text = (ROOT / SPEC).read_text()
    assert THIS_TEST in text and "rom-images/roms.csv" in text
    assert all(token in text for token in SCALE_KEYS)
    assert not re.search(r"(?<![0-9a-f])[0-9a-f]{64}(?![0-9a-f])", text, re.IGNORECASE)
    for name, layout in LAYOUTS.items():
        assert (f'| `{name}` | `IMAGE_FIXTURES["{name}"]` | `{layout.name}` | '
                f'`{layout.pairs[0].values:08x}` / `{layout.pairs[0].axis:08x}` | '
                f'`{layout.pairs[1].values:08x}` / `{layout.pairs[1].axis:08x}` |') in text
    for layout in (JK78C, ND, ME):
        start, stop, first, second, bound_pc, bound_cell, result_cell = layout.task
        pair = layout.pairs[0]
        assert (f"| `{layout.name}` | `[{start:08x},{stop:08x})` | "
                f"`{first:08x}`: `{pair.axis:05x}` / `{pair.values:05x}` | "
                f"`{bound_pc:08x}`: `{bound_cell:08x}` | "
                f"`{second:08x}`: `{pair.values:05x}` / `{pair.axis:05x}` | "
                f"`{stop - 2:08x}`: `{result_cell:08x}` |") in text
        for start, expected in SPANS[layout.name]:
            assert f"`[{start:08x},{start + len(bytes.fromhex(expected)):08x})`" in text
    normalized = " ".join(text.split())
    for fragment in ("u16(lookup ordinate)", "not exhaustive uint16 execution", "table[16]",
                     "strictly increasing", "whole-function reachability", "physical units", "hardware validation",
                     "1ME3B fractional", "DID", "independent slice inputs", "phase-zero output independence"):
        assert fragment in normalized
    home = " ".join((ROOT / "defs/JK78C.vvel.md").read_text().split())
    assert "target word --> lookup(values 0x156DC, axis 0x156FC) --> bounds --> command ffff44aa" in home
    assert ("At `0x000556E2`, the task passes `0x000156DC` as values and `0x000156FC` as the axis before "
            "the bounds and the store to `0xFFFF44AA`. At `0x00055776`, it passes `0x000156FC` as values "
            "and `0x000156DC` as the axis; the returned low word is stored at `0xFFFF35BA`.") in home
    assert "These raw pointer roles do not establish physical units." in home
    assert "`VQ37.command-count-scales.md`; it is separate from the latch and DID chain." in home
    can = " ".join((ROOT / "defs/JK78C.can.md").read_text().split())
    _, stop, first, second, bound_pc, bound_cell, result_cell = JK78C.task
    pair = JK78C.pairs[0]
    assert (f"At `0x{first:08X}`, it passes `0x{pair.axis:08X}` as values and `0x{pair.values:08X}` "
            f"as the axis to `FUN_{pair.lookup:08X}`. Bounds are applied before the store at "
            f"`0x{bound_pc:08X}` to `0x{bound_cell:08X}`. At `0x{second:08X}`, it passes "
            f"`0x{pair.values:08X}` as values and `0x{pair.axis:08X}` as the axis; the returned low "
            f"word is stored at `0x{stop - 2:08X}` to `0x{result_cell:08X}`.") in can
    assert "These raw pointer roles do not establish physical units." in can
    assert "`VQ37.command-count-scales.md`, separate from the latch and DID chain." in can


@pytest.mark.parametrize("mutation", ("first-roles", "second-roles", "bound-store", "result-store", "physical-boundary"))
def test_home_can_task_declaration_rejects_mutants(monkeypatch, mutation: str) -> None:
    path = ROOT / "defs/JK78C.can.md"
    text = " ".join(path.read_text().split())
    _, stop, first, second, bound_pc, bound_cell, result_cell = JK78C.task
    pair = JK78C.pairs[0]
    first_roles = (f"At `0x{first:08X}`, it passes `0x{pair.axis:08X}` as values and "
                   f"`0x{pair.values:08X}` as the axis")
    second_roles = (f"At `0x{second:08X}`, it passes `0x{pair.values:08X}` as values and "
                    f"`0x{pair.axis:08X}` as the axis")
    bound_store = f"the store at `0x{bound_pc:08X}` to `0x{bound_cell:08X}`"
    result_store = f"word is stored at `0x{stop - 2:08X}` to `0x{result_cell:08X}`"
    boundary = "These raw pointer roles do not establish physical units."
    mutations = {
        "first-roles": (first_roles, second_roles.replace(f"{second:08X}", f"{first:08X}")),
        "second-roles": (second_roles, first_roles.replace(f"{first:08X}", f"{second:08X}")),
        "bound-store": (bound_store, bound_store.replace(f"{bound_cell:08X}", f"{result_cell:08X}")),
        "result-store": (result_store, result_store.replace(f"{result_cell:08X}", f"{bound_cell:08X}")),
        "physical-boundary": (boundary, boundary.replace("do not establish", "establish")),
    }
    before, after = mutations[mutation]
    assert text.count(before) == 1
    mutant = text.replace(before, after, 1)
    read_text = Path.read_text

    def mutated_text(file, *args, **kwargs):
        return mutant if file == path else read_text(file, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", mutated_text)
    with pytest.raises(AssertionError):
        test_inverse_specification_and_home_task_declaration()
