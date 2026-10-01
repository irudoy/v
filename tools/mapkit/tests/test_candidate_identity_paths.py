"""Narrow stock-code gates for eight JK08A candidate identities.

Fixed opcode and literal spans bind the reviewed regions to the owned stock
image. The existing SH-2 interpreter executes the lookups and the selected
integer consumers; seven additional integer forms are local to this module.
The assertions describe these regions, not complete ECU functions or physical
units. Explicit-axis lookups use exact/end points only: fractional division and
the scaled-axis fractional finisher are outside this gate. Implicit lookups
execute their fractional kernel and finisher without stubs.

Segments that skip preceding calculations seed their incoming value explicitly.
Base-register segments execute their stock literal load. Stack padding is zero;
the wrappers consume only the low word or byte of the argument slot. Calibration
and configuration variants change data bytes in memory, not instructions under
review. Instruction mutants are negative fixtures, not firmware patches.
"""

from __future__ import annotations

import csv
from itertools import product
from pathlib import Path

import pytest

from tools.mapkit import rom as romkit
from tools.mapkit.sh2_interpreter import MASK, STACK_TOP, Sh2, sext

ROOT = Path(__file__).resolve().parents[3]
THIS_TEST = "tools/mapkit/tests/test_candidate_identity_paths.py"

# Constants from JK08A stock SHA-256
# ab60f18793fb121e4f55f626246117a6c69d9a900c0307ab1f4fc5f6ac718b23.
# Expected instruction bytes are independent of the image loaded at test time.
COMMON = {
    "word-axis": (
        (0x26984, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be50000026c78"),
    ),
    "byte-axis": (
        (0x26944, "6343014c611c3510891635168b103340891235184528304c61008401611c600c4f22d2063018420b61534f26000b650374ff441189e5e400000be50000026c78"),
    ),
    "implicit": (
        (0x26A5C, "450143254501432545014325450143254501432545014325450143254501432545014325450143254501432545014325450143254501432563394019200889064500345c61418541620da005601d345c61408441620c601cd601462b0009000900026740"),
    ),
    "finish": (
        (0x26740, "3202890b2f063028011a0037001a411a600962f6600d3208000b60233208011a0237021a411a6229622d000b302c0000"),
    ),
    "word-2d": (
        (0x262A8, "4f222f46677d60536573d70a470be41e2f562f46606355f4655d470be41e60f661f66243635364f64f26d701472be5100002684800026984"),
        (0x26848, "2f864f22071a205e342c001a471a4500340c354c6813d7102338891261418541620d470b601d288889132f0661518551620d470b601d620360f6470b6383a008000928888d0560416251600d622d470b63834f26000b68f600026740"),
    ),
    "byte-2d": (
        (0x26084, "4f222f46677c60536573d70a470be4032f462f56606355f4655c470be40361f660f66243635364f64f26d701472be5040002677000026944"),
        (0x26770, "2f864f22071a205e342c001a471a340c354c6813d7102338891261408441620c470b601c288889132f0661508451620c470b601c620360f6470b6383a008000928888d0560406250600c622c470b63834f26000b68f6000900026740"),
    ),
    "byte-1d": (
        (0x26550, "4f222f466053656dd707470be41e66f64401364c8461620c635361604f26d601462b601c0002674000026984"),
    ),
    "implicit-byte": (
        (0x26370, "9007655c35028902d602462be300000b844700e000026a809007655c35028902d602462be300000b844f00f000026a84"),
    ),
    "implicit-word4": (
        (0x263BC, "d005655d35028902d602462be300000b8543000900026a5c0000c000"),
    ),
    "implicit-word16": (
        (0x263F4, "d005655d35028902d602462be300000b854f000900026a640000f000"),
    ),
    "scaled-2d": (
        (0x26660, "4f222f46677d60536573d70b470be40f2f562f46606355f4655dd708470be41e60f661f640006243635364f64f26d701472be51000026b2800026bc400026b84"),
        (0x26B84, "6343014d611d3510891635168b103340891235184528304c61018501611d600d4f22d2063018420b61534f26000b650374fe441189e5e400000be50000026d10"),
        (0x26BC4, "6343014c611c410841083150891b3156891533408917351845286343330c61308431611c600c40084108400841084f22d2063018420b61534f26000b650374ff441189dee400000be500000900026d10"),
        (0x26B28, "2f864f22071a205e342c001a471a4500340c354c6813d7102338891261418541620d470b601d288889132f0661518551620d470b601d620360f6470b6383a008000928888d0560416251600d622d470b63834f26000b68f600026af8"),
    ),
}

PATHS = {
    "c98e": (
        (0x7B2D2, "d039401e7ffcd6386060c8028958d737d438857dd53881f1c503d637d238dc38420b670d620d9059e580d436662fd2364518365cd5360c65"),
        (0x7B35A, "620f90270ecdc50a3e2c3e078f0166036e63c50b3e038d0164036e43c4d7c8208d026203c50a6e036023c8108901c50b6e039012a0070ce5d617e080600cdc0e026d900a0c25"),
        (0x7B3AE, "03760406040503740000ffff4124000083c1ffff119c0000c98e0001347800013498000262a8ffff28f800014afa000264cc000134b8ffff109400021ce000021bbcffff23bc"),
    ),
    "12e52": (
        (0xA6838, "4f22d585e017d488065cd285420b656c6203d684901d4f26000b0624"),
        (0xA688A, "0c84"),
        (0xA68F4, "d262d75964219060644d66434619057c6269662e655c226d3527895c905644196249057c662e226d655c32538953"),
        (0xA69BE, "0c850c84"),
        (0xA6A50, "ffff119c00012e6200026388ffff28f800012e52"),
        (0xA6A80, "ffff1024"),
        (0xA6AFA, "d27bde7b6721906d677d6673461904ec6269662e644c226d3427896a90634719627904ec662e226d644c32438961"),
        (0xA6BDE, "0c850c84"),
        (0xA6CE8, "ffff1024ffff28f8"),
    ),
    "12918": (
        (0x469AC, "da73"),
        (0x46B7C, "ffff128c"),
        (0x46C08, "d6130a458464c808890ad612d412856ed512d213420b660d62039017a00a0a24d60cd410856ed50dd20d420b660d6603900c0a64"),
        (0x46C54, "048e0000ffff424cffff119c00012908000140d40002655000012918"),
        (0x474AE, "d158"),
        (0x474F4, "9062051c655c6253420842003623890345084500a00162536243d541e03ede41642d0525"),
        (0x475BC, "048e"),
        (0x47610, "ffff128cffff23bc00008a17"),
    ),
    "14982": (
        (0x836A6, "da7a84a5660c76e046118900e60062634218eeff42006eed32e789006e23d473dd74dc704d0b65ed6203900bd47265ed4d0b0c2562039006de700c25"),
        (0x836E8, "02530298029a"),
        (0x8388C, "ffff28f8ffff106a0001497a000263bc00014982ffff4558"),
        (0x84422, "d741903a067d666d36c68b69de40903502ed622d36238b26"),
        (0x844A6, "0e7d66ed"),
        (0x844B0, "de1f"),
        (0x844B4, "903402ed652d36538b23"),
        (0x8449C, "0102029a"),
        (0x84520, "029a"),
        (0x84528, "ffff36d8ffff5b2affff28f8"),
        (0x8457E, "d7769076d374027d9074652d043d644d35438901a0c20009"),
        (0x8462C, "d74a901fde48027d901d652d04ed644d35438b29"),
        (0x84670, "0102029a"),
        (0x84754, "ffff28f8ffff36d8"),
        (0x86678, "dd21903bd72202dd72010d25"),
        (0x866F4, "0102"),
        (0x86700, "ffff36d8ffff4242ffff401c"),
        (0x86760, "902fd58802ddd78872010d25"),
        (0x867C2, "0102"),
        (0x86984, "ffff37eaffff401c"),
    ),
    "09eca": (
        (0x7A0A4, "dd90e05f07dc"),
        (0x7A0E0, "db80"),
        (0x7A12E, "6073c8088b01a1280009"),
        (0x7A248, "84dec8028d336e03d32de7ffee018533620d4209662d627c36278d014e186263d42dd52e60c3d62e672cd22e420b80f3660ce00740180b643e68902904bd902b644d064705bc84de655c061a0e57021a362c461934668f036e0335608b007601e2ff622c36268900626390150b24"),
        (0x7A2D8, "038802ec0380037c0386037affff28f8ffff41a9"),
        (0x7A308, "ffff4124ffff119c00021ce000011fd600011a830002647400009eca00011a5100011a4500026084"),
    ),
    "1295c": (
        (0x44A30, "da3c"),
        (0x44A34, "db4c"),
        (0x44A46, "9069d44b0a2484b5d648460b650c62039062d4480a24"),
        (0x44B1C, "04a304a2"),
        (0x44B24, "ffff128c"),
        (0x44B68, "ffff106a0001295400026370000263880001295c00012738"),
        (0x453AC, "d30d642f9015073c677c627f420034278b41647fa03f4400"),
        (0x453DE, "04a2"),
        (0x453E4, "ffff128c"),
        (0x45442, "604381f4"),
        (0x455B4, "d3329046023c85f4622c302c6603d32f9040053c655c625f420036278b02625fa00142006263602381f4"),
        (0x455EA, "699c29988904d227420b0009a0130009d3219025053c85f4655c625342006403302c921e302789024500345c62436623d21ee0220265"),
        (0x45646, "016b04a203287fff"),
        (0x45680, "ffff128c"),
        (0x45690, "0002c626ffff120e"),
    ),
    "14e52": (
        (0x64A2E, "d64de017d44d026cdc46652cd24c45189a79420b655d620d9076d6490c25e04c096de054086d9070699d688d04cd349c348c34a78b0064a3644fdb39906665230427e20107bd42283258061a0727021a362c6269622f6d2f3d438d050bd53d708b02d32f7d0103d5"),
        (0x64B34, "7fff037c073a0712"),
        (0x64B50, "ffff128c"),
        (0x64B64, "ffff119c00014e52000263f4ffff23bc"),
    ),
    "749bc": (
        (0x749C4, "d24364206043c90120088d496603d5418452c80489446043c90220088f206403d63e6060c8208903d63d8464c8808917de399061d73b06ede03cd33b057ce02e023d36238b00626390560e25622f326060538f01cb10c9ef6503e03ca029075424488926de2c9047d72e05ede03cd32f047ce07c063de068023d326789006623666f35638b0066539036626f32500e6560438f01cb10c9ef6403e03ca009074426688906d61fe03c006cc9ef6203e03c0624e0ffdd1481f1901fd41d0eddd51dd61d67edd21dde14420b0009620d9013e580662f4518365c626f06ed36278b006623900b0d65"),
        (0x74ABC, "0d1c0a3e0a9a"),
        (0x74ACC, "ffff128c"),
        (0x74AD4, "00008b28ffff4188ffff28f8000089faffff24ceffff2470ffff4124ffff1094000175c80001871600018ac600026660"),
    ),
}
KERNELS = {
    "c98e": ("word-axis", "word-2d", "finish"),
    "12e52": ("implicit-byte", "implicit", "finish"),
    "12918": ("word-axis", "byte-1d", "finish"),
    "14982": ("implicit-word4", "implicit", "finish"),
    "09eca": ("byte-axis", "byte-2d", "finish"),
    "1295c": ("implicit-byte", "implicit", "finish"),
    "14e52": ("implicit-word16", "implicit", "finish"),
    "749bc": ("scaled-2d",),
}


class PathSh2(Sh2):
    """Seven integer instruction forms needed by these stock regions only."""

    def __init__(self, data: bytes):
        super().__init__(data)
        self.executed: list[int] = []
        self.seed(STACK_TOP - 4, b"\0" * 20)

    def _execute(self, pc: int, opcode: int):
        assert pc not in (0x26C78, 0x26D10, 0x26AF8), "fractional explicit-axis path outside gate"
        self.executed.append(pc)
        n, m = (opcode >> 8) & 15, (opcode >> 4) & 15
        form = opcode & 0xF00F
        if form == 0x600F:  # EXTS.W Rm,Rn
            self.r[n] = sext(self.r[m], 16) & MASK
        elif form == 0x3008:  # SUB Rm,Rn
            self.r[n] = (self.r[n] - self.r[m]) & MASK
        elif form == 0x3002:  # CMP/HS Rm,Rn
            self.t = int(self.r[n] >= self.r[m])
        elif opcode & 0xF0FF == 0x4001:  # SHLR Rn
            self.t = self.r[n] & 1
            self.r[n] >>= 1
        elif opcode & 0xF0FF == 0x4011:  # CMP/PZ Rn
            self.t = int(sext(self.r[n], 32) >= 0)
        elif opcode & 0xF0FF == 0x401A:  # LDS Rn,MACL
            self.macl = self.r[n]
        elif opcode >> 8 == 0xC5:  # MOV.W @(disp,GBR),R0
            self.r[0] = sext(self._read(self.gbr + (opcode & 255) * 2, 2, pc), 16) & MASK
        else:
            return super()._execute(pc, opcode)
        return None


@pytest.fixture(scope="module")
def stock() -> bytes:
    return romkit.load("JK08A").data


def _bind(data: bytes, key: str) -> None:
    spans = list(PATHS[key])
    for kernel in KERNELS[key]:
        spans.extend(COMMON[kernel])
    for address, expected_hex in spans:
        expected = bytes.fromhex(expected_hex)
        assert data[address:address + len(expected)] == expected, f"{key}: stock span {address:08x}"


def _patch(data: bytes, address: int, value: bytes) -> bytes:
    result = bytearray(data)
    result[address:address + len(value)] = value
    return bytes(result)


def _table(data: bytes, address: int, count: int, width: int, value: int) -> bytes:
    return _patch(data, address, value.to_bytes(width, "big") * count)


def _word(machine: Sh2, address: int, value: int) -> None:
    machine.seed_word(address, value & 0xFFFF)


def _map_reads(machine: Sh2, address: int, size: int, width: int) -> None:
    found = [(pc, at, n) for pc, at, n in machine.loads if address <= at < address + size]
    assert found and all(n == width and at + n <= address + size for _, at, n in found), found


def _bases(machine: PathSh2, *sites: int) -> None:
    for site in sites:
        machine.run(site, (site + 2,))


def _correction(data: bytes, raw: int, other: int, lower: int, upper: int, flags: int) -> PathSh2:
    data = _table(data, 0xC98E, 256, 2, raw)
    data = _patch(data, 0x83C1, bytes([data[0x83C1] | 2]))
    machine = PathSh2(data)
    _word(machine, 0xFFFF11B6, 0)
    _word(machine, 0xFFFF412A, 0)
    _word(machine, 0xFFFF413A, lower)
    _word(machine, 0xFFFF4138, upper)
    machine.seed(0xFFFF41FB, bytes([flags]))
    machine.run(0x7B2D2, (0x262A8,))
    assert (machine.r[4], machine.r[5], machine.r[6], machine.r[7]) == (0xC98E, 0x13478, 0x13498, 0)
    machine.run(0x262A8, (0x7B2F6,))
    machine.run(0x7B2F6, (0x7B30A,))
    assert machine.peek(0xFFFF2C6E, 2) == (raw - 32768) & 0xFFFF
    # The other interpolated term and its divider are outside this region.
    machine.r[0] = other & 0xFFFF
    machine.run(0x7B35A, (0x7B3A0,))
    _map_reads(machine, 0xC98E, 512, 2)
    assert machine.stored(0xFFFF2C6C)[-1][:2] == (0x7B390, 2)
    return machine


def test_c98e_signed_correction_and_stock_gate(stock: bytes) -> None:
    _bind(stock, "c98e")
    assert stock[0x83C1] == 0x2C
    assert stock[0xC98E:0xCB8E] == bytes.fromhex("8000") * 256
    machine = PathSh2(stock)
    _word(machine, 0xFFFF243C, 0xABCD)
    machine.run(0x7B2D2, (0x7B3A0,))
    assert machine.stored(0xFFFF2C6C) == [(0x7B39E, 2, 0xABCD)]
    assert not machine.stored(0xFFFF2C6E) and 0x262A8 not in machine.executed
    for raw, other, bounds, flags in product(
        (0, 0x7FFF, 0x8000, 0xFFFF), (-32768, -1, 0, 1, 32767),
        ((-100, 100), (-32768, 32767), (0, 0)), (0, 0x10, 0x20, 0x30),
    ):
        lower, upper = bounds
        expected = min(upper, max(lower, raw - 32768 + other))
        if flags & 0x20:
            expected = upper
        if flags & 0x10:
            expected = lower
        machine = _correction(stock, raw, other, lower, upper, flags)
        assert (0x7B35E, 0xFFFF2C6E, 2) in machine.loads
        assert sext(machine.peek(0xFFFF2C6C, 2), 16) == expected


def _window(data: bytes, entry: int, high: int, lower: int, upper: int, low: int = 0x5A) -> bool:
    machine = PathSh2(data)
    _word(machine, 0xFFFF1024, (high << 8) | low)
    machine.seed(0xFFFF357D, bytes([lower]))
    machine.seed(0xFFFF357C, bytes([upper]))
    passed, rejected = (0xA6922, 0xA69CA) if entry == 0xA68F4 else (0xA6B28, 0xA6BEC)
    reached = machine.run(entry, (passed, rejected))
    assert (0xA68F8 if entry == 0xA68F4 else 0xA6AFE, 0xFFFF1024, 2) in machine.loads
    return reached == passed


def test_12e52_strict_upper_load_bound(stock: bytes) -> None:
    _bind(stock, "12e52")
    assert stock[0x12E52:0x12E62] == b"\xff" * 16
    for rpm in (0, 1, 15, 16, 239, 240, 255):
        machine = PathSh2(stock)
        machine.seed(0xFFFF11B3, bytes([rpm]))
        machine.call(0xA6838)
        _map_reads(machine, 0x12E52, 16, 1)
        assert machine.stored(0xFFFF357C) == [(0xA6852, 1, 255)]
        assert 0x26388 in machine.executed
    for entry, high, bounds, low in product(
        (0xA68F4, 0xA6AFA), (0, 16, 17, 18, 19, 20, 254, 255),
        ((0, 255), (17, 19)), (0, 255),
    ):
        lower, upper = bounds
        assert _window(stock, entry, high, lower, upper, low) == (lower <= high < upper)


def _selected_floor(data: bytes, selected: int, row: int = 0) -> PathSh2:
    machine = PathSh2(data)
    _bases(machine, 0x469AC)
    machine.seed(0xFFFF4250, bytes([selected]))
    _word(machine, 0xFFFF11B8, row)
    machine.run(0x46C08, (0x46C3C,))
    return machine


def _floor(data: bytes, raw: int, current: int) -> PathSh2:
    machine = PathSh2(data)
    _bases(machine, 0x474AE)
    machine.seed(0xFFFF171A, bytes([raw]))
    machine.r[4] = machine.r[6] = current
    machine.run(0x474F4, (0x47518,))
    return machine


def test_12918_selected_internal_floor(stock: bytes) -> None:
    _bind(stock, "12918")
    assert stock[0x12918:0x12928] == bytes.fromhex("00000a131c23323c4d5c6f82919ba0a2")
    # Different samples distinguish the two branches without relying on equality.
    data = _table(stock, 0x12908, 16, 1, 17)
    data = _table(data, 0x12918, 16, 1, 203)
    for row, (selected, address, expected) in product(
        (0, 65535), ((0, 0x12918, 203), (8, 0x12908, 17)),
    ):
        machine = _selected_floor(data, selected, row)
        _map_reads(machine, address, 16, 1)
        assert machine.peek(0xFFFF171A) == expected and 0x26550 in machine.executed
        first_sample = address + (0 if row == 0 else 15)
        assert (0x2656A, first_sample, 1) in machine.loads
        # The last-point path also fetches the next byte, but its fraction is zero.
        assert machine.r[3] == 0
    for raw, current in product((0, 1, 127, 128, 162, 255), (0, 7, 8, 1023, 1024, 2040, 65535)):
        machine = _floor(stock, raw, current)
        assert machine.stored(0xFFFF23FA) == [(0x47516, 2, max(current, raw * 8))]
    # Subsequent transforms to ffff122a are not executed by this local floor gate.


def _event_compare(data: bytes, path: int, counter: int, threshold: int) -> bool:
    machine = PathSh2(data)
    _word(machine, 0xFFFF37DA, counter)
    _word(machine, 0xFFFF2B92, threshold)
    if path == 0:
        machine.r[12] = 0  # Separate preceding positive-count predicate.
        reached = machine.run(0x84422, (0x8443A, 0x84488, 0x84502))
        accepted = 0x8443A
    elif path == 1:
        _bases(machine, 0x84422, 0x84424)
        machine.run(0x844A6, (0x844AA,))
        # The positive-count predicate and unrelated flag OR are outside this segment.
        _bases(machine, 0x844B0)
        reached = machine.run(0x844B4, (0x844BE, 0x84506))
        accepted = 0x844BE
    elif path == 2:
        reached = machine.run(0x8457E, (0x84596, 0x8471A))
        accepted = 0x84596
    else:
        reached = machine.run(0x8462C, (0x84640, 0x84694))
        accepted = 0x84640
    assert any(at == 0xFFFF37DA and n == 2 for _, at, n in machine.loads)
    assert any(at == 0xFFFF2B92 and n == 2 for _, at, n in machine.loads)
    return reached == accepted


def test_14982_event_counter_threshold(stock: bytes) -> None:
    _bind(stock, "14982")
    assert stock[0x14982:0x1498A] == bytes.fromhex("003c") * 4
    for coolant in (0, 31, 32, 33, 127, 128, 255):
        machine = PathSh2(stock)
        machine.seed(0xFFFF106F, bytes([coolant]))
        machine.run(0x836A6, (0x836D2,))
        expected_index = min(65535, max(0, coolant - 32) * 512)
        assert machine.r[14] == expected_index and machine.r[13] == 0x263BC
        machine.run(0x836D2, (0x263BC,))
        assert machine.r[4] == 0x14982 and machine.r[5] == expected_index
        assert machine.stored(0xFFFF2B90) == [(0x836D8, 2, 33)]
        machine.run(0x263BC, (0x836DA,))
        machine.run(0x836DA, (0x836E2,))
        _map_reads(machine, 0x14982, 8, 2)
        assert machine.stored(0xFFFF2B92) == [(0x836E0, 2, 60)]
    for path, counter in product(range(4), (59, 60, 61, 32767, 32768, 65535)):
        assert _event_compare(stock, path, counter, 60) == (counter >= 60)
    for start, stop in ((0x86678, 0x86684), (0x86760, 0x8676C)):
        for counter in (0, 59, 60, 65535):
            machine = PathSh2(stock)
            _word(machine, 0xFFFF37DA, counter)
            _bases(machine, 0x86678)
            machine.run(start, (stop,))
            assert machine.peek(0xFFFF37DA, 2) == (counter + 1) & 0xFFFF
    # No window number, reset/completion meaning, or cylinder identity is asserted.


def _mix(data: bytes, weight: int, new: int, old: int, first_gate: int = 8, second_gate: int = 2) -> PathSh2:
    machine = PathSh2(_table(data, 0x9ECA, 16, 1, weight))
    _bases(machine, 0x7A0A4, 0x7A0E0)
    machine.seed(0xFFFF4208, bytes([first_gate]))
    machine.seed(0xFFFF41B7, bytes([second_gate]))
    _word(machine, 0xFFFF2C80, new)
    machine.seed(0xFFFF2C7E, bytes([old]))
    _word(machine, 0xFFFF412A, 0)
    machine.run(0x7A0A6, (0x7A0AA,))
    reached = machine.run(0x7A12E, (0x7A138, 0x7A388))
    if reached == 0x7A388:
        return machine
    # The upstream row calculation is an incoming operand, fixed at its low end.
    machine.r[12] = 0
    machine.run(0x7A248, (0x7A2B6,))
    return machine


def test_09eca_q8_progress_and_saturation(stock: bytes) -> None:
    _bind(stock, "09eca")
    assert stock[0x9ECA:0x9EDA] == b"\0" * 16
    for weight, new, old in product((0, 1, 127, 128, 255), (0, 1, 254, 255, 256, 65535), (0, 1, 127, 254, 255)):
        blended = (weight * new + (256 - weight) * old) // 256
        expected = min(255, blended + int(new > blended and blended == old))
        machine = _mix(stock, weight, new, old)
        _map_reads(machine, 0x9ECA, 16, 1)
        assert machine.stored(0xFFFF2FF8) == [(0x7A27E, 1, weight)]
        assert machine.stored(0xFFFF2C7E) == [(0x7A2B4, 1, expected)]
    for gates in ((0, 2), (8, 0), (0, 0)):
        machine = _mix(stock, 1, 1, 0, *gates)
        assert not machine.stored(0xFFFF2FF8) and not machine.stored(0xFFFF2C7E)
    assert _mix(stock, 0, 1, 0).peek(0xFFFF2C7E) == 1
    assert _mix(stock, 1, 1, 0).peek(0xFFFF2C7E) == 1


def _upper_source(data: bytes, bound: int, coolant: int = 0) -> PathSh2:
    machine = PathSh2(_table(data, 0x1295C, 8, 1, bound))
    _bases(machine, 0x44A30, 0x44A34)
    machine.seed(0xFFFF106F, bytes([coolant]))
    machine.run(0x44A46, (0x44A5C,))
    assert machine.stored(0xFFFF172E) == [(0x44A5A, 1, bound)]
    _map_reads(machine, 0x1295C, 8, 1)
    return machine


def _upper_first(data: bytes, bound: int, value: int) -> PathSh2:
    machine = _upper_source(data, bound)
    machine.r[2] = value & MASK
    machine.run(0x453AC, (0x45446,))
    return machine


def _upper_second(data: bytes, bound: int, value: int, added: int = 0) -> PathSh2:
    machine = _upper_source(data, bound)
    _word(machine, STACK_TOP + 8, value)
    machine.seed(0xFFFF13F7, bytes([added]))
    machine.run(0x455B4, (0x455DE,))
    return machine


def test_1295c_branch_local_upper_clamp(stock: bytes) -> None:
    _bind(stock, "1295c")
    assert stock[0x1295C:0x12964] == b"\x80" * 8
    for coolant in (0, 1, 31, 32, 223, 224, 255):
        _upper_source(stock, 128, coolant)
    for bound in (0, 1, 128, 255):
        for value in (-32768, -1, 0, 2 * bound - 1, 2 * bound, 2 * bound + 1, 32767):
            machine = _upper_first(stock, bound, value)
            assert sext(machine.peek(STACK_TOP + 8, 2), 16) == min(value, 2 * bound)
            for added in (0, 1, 255):
                machine = _upper_second(stock, bound, value, added)
                local = min(value + added, 2 * bound)
                assert sext(machine.peek(STACK_TOP + 8, 2), 16) == local
                # Normal completion adds a term after the local upper clamp.
                machine.seed(0xFFFF15B4, b"\xff")
                machine.r[9] = 0
                machine.run(0x455EA, (0x45620,))
                assert machine.stored(0xFFFF1230) == [(0x4561E, 2, min(local + 510, 32767) & 0xFFFF)]
    machine = _upper_second(stock, 128, 300)
    machine.r[9] = 1
    machine.run(0x455EA, (0x2C626,))
    assert not machine.stored(0xFFFF1230)
    # Alternate completion and the surrounding mode selection are outside this gate.


def _lag(data: bytes, weight: int, current: int, previous: int, rpm: int = 0, a: int = 0, b: int = 0) -> PathSh2:
    machine = PathSh2(_table(data, 0x14E52, 16, 2, weight))
    machine.seed(0xFFFF11B3, bytes([rpm]))
    _word(machine, 0xFFFF19C6, current)
    _word(machine, 0xFFFF2408, a)
    _word(machine, 0xFFFF2410, b)
    _word(machine, 0xFFFF199E, previous)
    machine.run(0x64A2E, (0x64A96,))
    return machine


def test_14e52_signed_q16_progress(stock: bytes) -> None:
    _bind(stock, "14e52")
    assert stock[0x14E52:0x14E72] == bytes.fromhex("1f40") * 16
    for rpm in (0, 1, 239, 240, 255):
        machine = _lag(stock, 8000, 100, -100, rpm)
        _map_reads(machine, 0x14E52, 32, 2)
        assert machine.stored(0xFFFF1608) == [(0x64A4A, 2, 8000)]
    for weight, current, previous in product(
        (0, 1, 8000, 32768, 65535), (-32768, -1, 0, 1, 32767), (-32768, -1, 0, 1, 32767),
    ):
        blended = (weight * current + (65536 - weight) * previous) // 65536
        expected = blended + int(blended < current and blended == previous)
        machine = _lag(stock, weight, current, previous)
        assert sext(machine.peek(0xFFFF199E, 2), 16) == expected
        writes = machine.stored(0xFFFF199E)
        assert writes[0] == (0x64A8A, 2, blended & 0xFFFF)
        assert len(writes) == 1 + int(expected != blended)
    machine = _lag(stock, 65535, 32767, 0, a=65535, b=65535)
    assert sext(machine.peek(0xFFFF199E, 2), 16) == 32766
    # History copies following 00064a96 are outside this weighted update gate.


def _arbitrate(data: bytes, config: int, active: int, state: int, first: int,
               a: int, b: int, raw: int, selector: int = 0, second_flag: int = 0,
               row: int = 0) -> PathSh2:
    data = _table(data, 0x175C8, 256, 2, raw)
    data = _patch(data, 0x8B28, bytes([config]))
    data = _patch(data, 0x89FA, bytes([selector]))
    machine = PathSh2(data)
    machine.seed(0xFFFF418A, bytes([active]))
    machine.seed(0xFFFF24D2, bytes([second_flag]))
    machine.seed(0xFFFF24AC, b"\xa5")
    _word(machine, 0xFFFF3614, state)
    _word(machine, 0xFFFF4152, first)
    _word(machine, 0xFFFF1110, a)
    _word(machine, 0xFFFF10FC, b)
    assert row in (0, 65535)  # Low and high clamped row endpoints, no fractional division.
    _word(machine, 0xFFFF1CCA, row)
    machine.run(0x749C4, (0x26660,))
    assert (machine.r[4], machine.r[5], machine.r[6], machine.r[7]) == (0x175C8, 0x18716, 0x18AC6, row)
    assert machine.peek(STACK_TOP + 2, 2) == 65535
    machine.run(0x26660, (0x74A90,))
    machine.run(0x74A90, (0x74AAA,))
    _map_reads(machine, 0x175C8, 512, 2)
    cell = 0x175C8 + 2 * (15 if row == 0 else 255)
    assert (0x26B6E, cell, 2) in machine.loads
    assert machine.stored(0xFFFF1D26)[-1][:2] == (0x74AA8, 2)
    return machine


def test_749bc_direct_lookup_and_arbitration(stock: bytes) -> None:
    _bind(stock, "749bc")
    assert stock[0x175E6:0x175E8] == bytes.fromhex("8558")
    gates = ((0, 0, 0, 0), (1, 0, 0, 0), (1, 4, 0, 0),
             (1, 4, 32, 0), (1, 4, 32, 128), (3, 0, 0, 0), (3, 4, 0, 0))
    for gate, state, values, raw, row in product(
        gates, (-32768, -1, 0, 32767),
        ((-32768, -5, 12), (32767, 12, -5), (0, -1, -1)),
        (0, 0x7FFF, 0x8000, 0xFFFF), (0, 65535),
    ):
        config, active, selector, second_flag = gate
        first, a, b = values
        expected_state, expected_flag = state, 0xA5
        if config & 1:
            if not active & 4:
                expected_flag &= ~16
            elif config & 2:
                expected_state = max(state, min(a, b))
                expected_flag = (expected_flag | 16) if expected_state != state else (expected_flag & ~16)
            elif not selector & 32 or second_flag & 128:
                expected_state = max(state, first)
                expected_flag = (expected_flag | 16) if expected_state != state else (expected_flag & ~16)
        machine = _arbitrate(stock, config, active, state, first, a, b, raw, selector, second_flag, row)
        assert sext(machine.peek(0xFFFF3614, 2), 16) == expected_state
        assert machine.peek(0xFFFF24AC) == expected_flag
        assert sext(machine.peek(0xFFFF1D26, 2), 16) == min(expected_state, raw - 32768)
    # No physical terminal purpose or transitive dependency on 00072f1e is asserted.


# Each group rejects a changed map literal, register operand, data width, and
# branch/delay-slot operand independently of the arithmetic reference models.
MUTATIONS = {
    "c98e": ((0x7B3C7, 1), (0x7B2E2, 1), (0x7B35F, 1), (0x7B370, 4)),
    "12e52": ((0xA6A63, 1), (0xA6842, 1), (0xA6917, 1), (0xA6920, 4)),
    "12918": ((0x46C6F, 1), (0x46C2A, 1), (0x46C3B, 1), (0x46C10, 4)),
    "14982": ((0x8389F, 1), (0x836D2, 1), (0x836E1, 1), (0x836D9, 1)),
    "09eca": ((0x7A323, 1), (0x7A272, 1), (0x7A285, 1), (0x7A29E, 4)),
    "1295c": ((0x44B7B, 1), (0x44A4E, 1), (0x455C7, 1), (0x455D7, 1)),
    "14e52": ((0x64B6B, 1), (0x64A3A, 1), (0x64A73, 1), (0x64A88, 4)),
    "749bc": ((0x74AF7, 1), (0x74A88, 1), (0x74AA9, 1), (0x74A59, 1)),
}


@pytest.mark.parametrize("key", tuple(MUTATIONS))
def test_candidate_identity_bindings_reject_operand_mutations(stock: bytes, key: str) -> None:
    for address, xor in MUTATIONS[key]:
        mutated = _patch(stock, address, bytes([stock[address] ^ xor]))
        with pytest.raises(AssertionError, match="stock span"):
            _bind(mutated, key)


def test_candidate_identity_arithmetic_rejects_incomplete_models(stock: bytes) -> None:
    # These mutants execute without the fixed-span assertion so a changed output
    # demonstrates why the omitted instruction matters, rather than only its bytes.
    drop_progress = _patch(stock, 0x7A2A6, bytes.fromhex("0009"))
    assert _mix(stock, 1, 1, 0).peek(0xFFFF2C7E) == 1
    assert _mix(drop_progress, 1, 1, 0).peek(0xFFFF2C7E) == 0
    drop_saturation = _patch(stock, 0x7A2AE, bytes.fromhex("0009"))
    assert _mix(stock, 255, 512, 0).peek(0xFFFF2C7E) == 255
    assert _mix(drop_saturation, 255, 512, 0).peek(0xFFFF2C7E) == 254
    drop_progress = _patch(stock, 0x64A92, bytes.fromhex("0009"))
    assert _lag(stock, 1, 1, 0).peek(0xFFFF199E, 2) == 1
    assert _lag(drop_progress, 1, 1, 0).peek(0xFFFF199E, 2) == 0
    floor_by_four = _patch(stock, 0x474FE, bytes.fromhex("0009"))
    floor_by_four = _patch(floor_by_four, 0x47506, bytes.fromhex("0009"))
    assert _floor(stock, 128, 0).peek(0xFFFF23FA, 2) == 1024
    assert _floor(floor_by_four, 128, 0).peek(0xFFFF23FA, 2) == 512
    inclusive_upper = _patch(stock, 0xA691E, bytes.fromhex("3257"))
    assert not _window(stock, 0xA68F4, 19, 17, 19)
    assert _window(inclusive_upper, 0xA68F4, 19, 17, 19)
    drop_delay_shift = _patch(stock, 0x455D6, bytes.fromhex("0009"))
    assert _upper_second(stock, 128, 300).peek(STACK_TOP + 8, 2) == 256
    assert _upper_second(drop_delay_shift, 128, 300).peek(STACK_TOP + 8, 2) == 128
    byte_consumer = _patch(stock, 0x7B35E, bytes.fromhex("0ecc"))
    assert _correction(stock, 0x8001, 0, -100, 100, 0).peek(0xFFFF2C6C, 2) == 1
    assert _correction(byte_consumer, 0x8001, 0, -100, 100, 0).peek(0xFFFF2C6C, 2) == 0
    strict_threshold = _patch(stock, 0x84436, bytes.fromhex("3627"))
    assert _event_compare(stock, 0, 60, 60)
    assert not _event_compare(strict_threshold, 0, 60, 60)
    drop_change_flag = _patch(stock, 0x74A58, bytes.fromhex("0009"))
    assert _arbitrate(stock, 3, 4, 0, 0, 10, 20, 0x8000).peek(0xFFFF24AC) == 0xB5
    assert _arbitrate(drop_change_flag, 3, 4, 0, 0, 10, 20, 0x8000).peek(0xFFFF24AC) == 0xA5


OWNERS = (
    ("JK08A.findings.csv", "0000c98e", "test_c98e_signed_correction_and_stock_gate", "site:0007b2e2"),
    ("JK08A.findings.csv", "00012e52", "test_12e52_strict_upper_load_bound", "site:000a683e"),
    ("JK08A.findings.csv", "00012918", "test_12918_selected_internal_floor", "site:00046c2a"),
    ("JK08A.findings.csv", "00014982", "test_14982_event_counter_threshold", "site:000836d2"),
    ("JK08A.findings.csv", "00009eca", "test_09eca_q8_progress_and_saturation", "site:0007a268"),
    ("JK08A.findings.csv", "0001295c", "test_1295c_branch_local_upper_clamp", "site:00044a48"),
    ("JK08A.findings.csv", "00014e52", "test_14e52_signed_q16_progress", "site:00064a32"),
    ("JK08A.funcs.csv", "000749bc", "test_749bc_direct_lookup_and_arbitration", "site:00074a7e"),
)


def test_candidate_identity_owners_name_their_regression_paths() -> None:
    rows = {}
    for name in {item[0] for item in OWNERS}:
        with (ROOT / "defs" / name).open(newline="") as source:
            rows[name] = {row["addr"]: row for row in csv.DictReader(source)}
    for name, address, test, site in OWNERS:
        evidence = set(rows[name][address]["evidence"].split(";"))
        assert site in evidence
        assert f"test:{THIS_TEST}#{test}" in evidence
