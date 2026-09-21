"""Gates for the JK78C pressure channel, its units, and the booster-vacuum flag.

The stock ROM bytes of FUN_00021E0C, FUN_00022562, FUN_000225C0,
FUN_00044034, the scaling tail of FUN_00043CDE, FUN_00045A4C, FUN_0005A314,
and the frame copy of FUN_00020F1A run in a minimal SH-2 interpreter and are
compared with closed-form models. The interpreter implements only the
instructions these paths use and rejects any other opcode, any read of an
unset RAM cell, any write outside RAM, and any branch or PC-relative load in a
delay slot. Every instruction and both outcomes of every conditional branch
of the CODE_RANGES entries run at least once; the zero divisor and saturation
outcomes run on copies of the image that differ only in the named calibration
bytes. The cycle schedule and port stepping of the ADC sampler FUN_0002AA88
are gated by its exact instruction bytes.
"""

from __future__ import annotations

import json
import random
import re
import shutil
import struct
import subprocess
from fractions import Fraction
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[3]
ROM_PATH = ROOT / "rom-images/23710-JK78C/1JK78C-20260715-stock.bin"
DOC_PATH = ROOT / "defs/JK78C.vvel.md"
MANUAL_PATH = ROOT / "refs/renesas-sh7059-sh7058s-hardware-manual.md"
ESM_2013_PDF = ROOT / "refs/nissan-esm-2013-g37-sedan/ENGINE CONTROL SYSTEM.pdf"
ESM_2013_FRAGMENTS = ROOT / "refs/diagnostics/nissan-esm-2013-g37-sedan/fragments.jsonl"
THIS_TEST = "tools/mapkit/tests/test_jk78c_pressure_channel.py"

MASK = 0xFFFFFFFF
RETURN = 0x000FFFF0
STACK_TOP = 0xFFFFBF00
STACK_BOTTOM = 0xFFFFBE00
RAM_START = 0xFFFF0000
RAM_END = 0xFFFFC000

DIVIDE = 0x00021E0C
SHIFT6 = 0x00022562
BLOCK_COPY = 0x000225C0
SCALE_ARGUMENT = 0x00044034
REFERENCE_TAIL = (0x00043DAC, 0x00043DFA)
BOOSTER = 0x00045A4C
VACUUM = 0x0005A314

REFERENCE_BASE = 0xFFFF48D4
REFERENCE = 0xFFFF57C4
SCALED_REFERENCE = 0xFFFF4AC2
SCALED_ARGUMENT = 0xFFFF3314
DIVIDE_ERROR = 0xFFFF9748

BOOSTER_SAMPLE = 0xFFFF3868
BOOSTER_COPY = 0xFFFF42E2
BOOSTER_FLAGS = 0xFFFF45AE
BOOSTER_FILTER = 0xFFFF27D0
BOOSTER_SCALED = 0xFFFF2764

SPEED = 0xFFFF10FC
LATCHED_BOOSTER = 0xFFFF2666
THRESHOLD = 0xFFFF3324
VACUUM_WORD = 0xFFFF3338
LOW_FLAGS = 0xFFFF4516
LOW_HOLD = 0xFFFF4753
SUFFICIENT_FLAGS = 0xFFFF4515
SUFFICIENT_HOLD = 0xFFFF482C
REQUEST_FLAGS = 0xFFFF455E
SPEED_FLAGS = 0xFFFF4577
MODE_FLAGS = 0xFFFF4565
OVERRIDE_FLAGS = 0xFFFF4573
BRAKE_LATCH = 0xFFFF23AF
BRAKE_QUALIFIER = 0xFFFF23BD
STATUS_A = 0xFFFF5FCA
STATUS_B = 0xFFFF5FCD

# Executed instruction ranges, half-open, with the literal pools excluded.
CODE_RANGES = {
    DIVIDE: [(0x00021E0C, 0x00021EF2)],
    SHIFT6: [(0x00022562, 0x00022570)],
    BLOCK_COPY: [(0x000225C0, 0x000225F8)],
    SCALE_ARGUMENT: [(0x00044034, 0x00044088)],
    REFERENCE_TAIL[0]: [REFERENCE_TAIL],
    BOOSTER: [(0x00045A4C, 0x00045B0C)],
    VACUUM: [(0x0005A314, 0x0005A44E), (0x0005A458, 0x0005A516), (0x0005A568, 0x0005A57C)],
}


def _rom() -> bytes:
    return ROM_PATH.read_bytes()


def _u16(data: bytes, address: int) -> int:
    return struct.unpack_from(">H", data, address)[0]


def _u32(data: bytes, address: int) -> int:
    return struct.unpack_from(">I", data, address)[0]


def _ops(data: bytes, address: int, count: int) -> str:
    return " ".join(f"{_u16(data, address + 2 * index):04x}" for index in range(count))


def _pc_literal(data: bytes, address: int) -> int:
    opcode = _u16(data, address)
    assert opcode >> 12 == 0xD
    return _u32(data, ((address + 4) & ~3) + (opcode & 0xFF) * 4)


def _pc_word(data: bytes, address: int) -> int:
    opcode = _u16(data, address)
    assert opcode >> 12 == 0x9
    return _u16(data, address + 4 + (opcode & 0xFF) * 2)


def _doc() -> str:
    return " ".join(DOC_PATH.read_text(encoding="utf-8").split())


def _patched(data: bytes, **cells: int) -> bytes:
    """Return a copy of the image with calibration bytes, named x<address>, replaced."""
    patched = bytearray(data)
    for name, value in cells.items():
        patched[int(name[1:], 16)] = value
    return bytes(patched)


def _s8(value: int) -> int:
    value &= 0xFF
    return (value - 0x100 if value & 0x80 else value) & MASK


def _s16(value: int) -> int:
    value &= 0xFFFF
    return (value - 0x10000 if value & 0x8000 else value) & MASK


def _signed(value: int) -> int:
    return value - (1 << 32) if value & 0x80000000 else value


def _control_or_pc_relative(opcode: int) -> bool:
    top = opcode >> 12
    group8 = (opcode >> 8) & 0xF
    low8 = opcode & 0xFF
    if top in (0x9, 0xA, 0xB, 0xD):
        return True
    if top == 0x8 and group8 in (0x9, 0xB, 0xD, 0xF):
        return True
    if top == 0xC and group8 == 0x7:
        return True
    if top == 0x4 and low8 in (0x0B, 0x2B):
        return True
    return top == 0x0 and low8 in (0x03, 0x0B, 0x23, 0x2B)


class Coverage:
    def __init__(self) -> None:
        self.executed: set[int] = set()
        self.branches: set[tuple[int, bool]] = set()

    def assert_complete(self, data: bytes, ranges: list[tuple[int, int]]) -> None:
        missing = []
        branch_gaps = []
        for start, end in ranges:
            for address in range(start, end, 2):
                if address not in self.executed:
                    missing.append(address)
                opcode = _u16(data, address)
                if opcode >> 12 == 0x8 and (opcode >> 8) & 0xF in (0x9, 0xB, 0xD, 0xF):
                    for taken in (False, True):
                        if (address, taken) not in self.branches:
                            branch_gaps.append((hex(address), taken))
        assert not missing, [hex(address) for address in missing]
        assert not branch_gaps, branch_gaps


class Sh2:
    """Minimal SH-2 interpreter over the exact ROM image."""

    def __init__(self, data: bytes, coverage: Coverage | None = None) -> None:
        self.rom = data
        self.ram: dict[int, int] = {}
        self.written: set[int] = set()
        self.r = [0] * 16
        self.r[15] = STACK_TOP
        self.t = self.q = self.m = 0
        self.gbr = 0
        self.pr = RETURN
        self.macl = 0
        self.coverage = coverage or Coverage()

    def poke8(self, address: int, value: int) -> None:
        self.ram[address] = value & 0xFF

    def poke16(self, address: int, value: int) -> None:
        self.poke8(address, value >> 8)
        self.poke8(address + 1, value)

    def peek8(self, address: int) -> int:
        return self.ram[address]

    def peek16(self, address: int) -> int:
        return (self.ram[address] << 8) | self.ram[address + 1]

    def written_outside_stack(self) -> set[int]:
        return {a for a in self.written if not STACK_BOTTOM <= a < STACK_TOP}

    def _read8(self, address: int) -> int:
        address &= MASK
        if address < len(self.rom):
            return self.rom[address]
        if address not in self.ram:
            raise AssertionError(f"read of unset cell {address:#010x}")
        return self.ram[address]

    def _read16(self, address: int) -> int:
        address &= MASK
        assert address % 2 == 0, hex(address)
        return (self._read8(address) << 8) | self._read8(address + 1)

    def _read32(self, address: int) -> int:
        address &= MASK
        assert address % 4 == 0, hex(address)
        return (self._read16(address) << 16) | self._read16(address + 2)

    def _write8(self, address: int, value: int) -> None:
        address &= MASK
        if not RAM_START <= address < RAM_END:
            raise AssertionError(f"write outside RAM at {address:#010x}")
        self.ram[address] = value & 0xFF
        self.written.add(address)

    def _write16(self, address: int, value: int) -> None:
        address &= MASK
        assert address % 2 == 0, hex(address)
        self._write8(address, value >> 8)
        self._write8(address + 1, value)

    def _write32(self, address: int, value: int) -> None:
        address &= MASK
        assert address % 4 == 0, hex(address)
        self._write16(address, value >> 16)
        self._write16(address + 2, value)

    def _fetch(self, address: int) -> int:
        assert address % 2 == 0 and address < len(self.rom), hex(address)
        return _u16(self.rom, address)

    def call(self, entry: int, limit: int = 20000) -> None:
        self.pr = RETURN
        self.run(entry, RETURN, limit)

    def run(self, pc: int, stop: int, limit: int = 20000) -> None:
        for _ in range(limit):
            if pc == stop:
                return
            pc = self._execute(pc)
        raise AssertionError("step limit reached")

    def _slot(self, pc: int) -> None:
        opcode = self._fetch(pc + 2)
        assert not _control_or_pc_relative(opcode), f"delay slot {pc + 2:#x}: {opcode:04x}"
        assert self._execute(pc + 2) == pc + 4

    def _div1(self, m: int, n: int) -> None:
        old_q = self.q
        self.q = self.r[n] >> 31
        value = ((self.r[n] << 1) | self.t) & MASK
        before = value
        if old_q == self.m:
            value = (value - self.r[m]) & MASK
            carry = int(value > before)
        else:
            value = (value + self.r[m]) & MASK
            carry = int(value < before)
        self.q = self.q ^ carry if self.m == 0 else 1 - (self.q ^ carry)
        self.t = int(self.q == self.m)
        self.r[n] = value

    def _execute(self, pc: int) -> int:
        opcode = self._fetch(pc)
        self.coverage.executed.add(pc)
        r = self.r
        top = opcode >> 12
        n = (opcode >> 8) & 0xF
        m = (opcode >> 4) & 0xF
        low = opcode & 0xF
        imm = opcode & 0xFF
        following = pc + 2

        if top == 0x0:
            if opcode == 0x0009:
                return following
            if opcode == 0x000B:
                target = self.pr
                self._slot(pc)
                return target
            if opcode == 0x0019:
                self.m = self.q = self.t = 0
                return following
            if low == 0x9 and m == 0x2:
                r[n] = self.t
                return following
            if low == 0xA and m == 0x1:
                r[n] = self.macl
                return following
            if low == 0x4:
                self._write8(r[0] + r[n], r[m])
                return following
            if low == 0x5:
                self._write16(r[0] + r[n], r[m])
                return following
            if low == 0x6:
                self._write32(r[0] + r[n], r[m])
                return following
            if low == 0x7:
                self.macl = (r[n] * r[m]) & MASK
                return following
            if low == 0xC:
                r[n] = _s8(self._read8(r[0] + r[m]))
                return following
            if low == 0xD:
                r[n] = _s16(self._read16(r[0] + r[m]))
                return following
            if low == 0xE:
                r[n] = self._read32(r[0] + r[m])
                return following
        elif top == 0x1:
            self._write32(r[n] + low * 4, r[m])
            return following
        elif top == 0x2:
            value = r[m]
            if low == 0x0:
                self._write8(r[n], value)
            elif low == 0x1:
                self._write16(r[n], value)
            elif low == 0x2:
                self._write32(r[n], value)
            elif low == 0x6:
                r[n] = (r[n] - 4) & MASK
                self._write32(r[n], value)
            elif low == 0x8:
                self.t = int((r[n] & value) == 0)
            elif low == 0x9:
                r[n] &= value
            elif low == 0xA:
                r[n] ^= value
            elif low == 0xB:
                r[n] |= value
            else:
                raise AssertionError(f"unsupported {opcode:04x} at {pc:#x}")
            return following
        elif top == 0x3:
            a, b = r[n], r[m]
            if low == 0x0:
                self.t = int(a == b)
            elif low == 0x2:
                self.t = int(a >= b)
            elif low == 0x3:
                self.t = int(_signed(a) >= _signed(b))
            elif low == 0x4:
                self._div1(m, n)
            elif low == 0x6:
                self.t = int(a > b)
            elif low == 0x7:
                self.t = int(_signed(a) > _signed(b))
            elif low == 0x8:
                r[n] = (a - b) & MASK
            elif low == 0xC:
                r[n] = (a + b) & MASK
            elif low == 0xE:
                partial = (a + b) & MASK
                result = (partial + self.t) & MASK
                self.t = int(a > partial or partial > result)
                r[n] = result
            else:
                raise AssertionError(f"unsupported {opcode:04x} at {pc:#x}")
            return following
        elif top == 0x4:
            if imm == 0x00:
                self.t = r[n] >> 31
                r[n] = (r[n] << 1) & MASK
            elif imm == 0x01:
                self.t = r[n] & 1
                r[n] >>= 1
            elif imm == 0x08:
                r[n] = (r[n] << 2) & MASK
            elif imm == 0x09:
                r[n] >>= 2
            elif imm == 0x18:
                r[n] = (r[n] << 8) & MASK
            elif imm == 0x19:
                r[n] >>= 8
            elif imm == 0x28:
                r[n] = (r[n] << 16) & MASK
            elif imm == 0x29:
                r[n] >>= 16
            elif imm == 0x11:
                self.t = int(_signed(r[n]) >= 0)
            elif imm == 0x21:
                self.t = r[n] & 1
                r[n] = (_signed(r[n]) >> 1) & MASK
            elif imm == 0x24:
                carry = r[n] >> 31
                r[n] = ((r[n] << 1) | self.t) & MASK
                self.t = carry
            elif imm == 0x0B:
                target = r[n]
                self.pr = (pc + 4) & MASK
                self._slot(pc)
                return target
            elif imm == 0x2B:
                target = r[n]
                self._slot(pc)
                return target
            elif imm == 0x1E:
                self.gbr = r[n]
            elif imm == 0x13:
                r[n] = (r[n] - 4) & MASK
                self._write32(r[n], self.gbr)
            elif imm == 0x17:
                self.gbr = self._read32(r[n])
                r[n] = (r[n] + 4) & MASK
            elif imm == 0x12:
                r[n] = (r[n] - 4) & MASK
                self._write32(r[n], self.macl)
            elif imm == 0x16:
                self.macl = self._read32(r[n])
                r[n] = (r[n] + 4) & MASK
            elif imm == 0x22:
                r[n] = (r[n] - 4) & MASK
                self._write32(r[n], self.pr)
            elif imm == 0x26:
                self.pr = self._read32(r[n])
                r[n] = (r[n] + 4) & MASK
            else:
                raise AssertionError(f"unsupported {opcode:04x} at {pc:#x}")
            return following
        elif top == 0x5:
            r[n] = self._read32(r[m] + low * 4)
            return following
        elif top == 0x6:
            if low == 0x0:
                r[n] = _s8(self._read8(r[m]))
            elif low == 0x1:
                r[n] = _s16(self._read16(r[m]))
            elif low == 0x2:
                r[n] = self._read32(r[m])
            elif low == 0x3:
                r[n] = r[m]
            elif low == 0x4:
                value = _s8(self._read8(r[m]))
                if n != m:
                    r[m] = (r[m] + 1) & MASK
                r[n] = value
            elif low == 0x6:
                value = self._read32(r[m])
                if n != m:
                    r[m] = (r[m] + 4) & MASK
                r[n] = value
            elif low == 0xC:
                r[n] = r[m] & 0xFF
            elif low == 0xD:
                r[n] = r[m] & 0xFFFF
            elif low == 0xE:
                r[n] = _s8(r[m])
            elif low == 0xF:
                r[n] = _s16(r[m])
            else:
                raise AssertionError(f"unsupported {opcode:04x} at {pc:#x}")
            return following
        elif top == 0x7:
            r[n] = (r[n] + _s8(imm)) & MASK
            return following
        elif top == 0x8:
            if n == 0x0:
                self._write8(r[m] + low, r[0])
                return following
            if n == 0x8:
                self.t = int(r[0] == _s8(imm))
                return following
            if n == 0x1:
                self._write16(r[m] + low * 2, r[0])
                return following
            if n == 0x4:
                r[0] = _s8(self._read8(r[m] + low))
                return following
            if n == 0x5:
                r[0] = _s16(self._read16(r[m] + low * 2))
                return following
            if n in (0x9, 0xB, 0xD, 0xF):
                taken = self.t == (1 if n in (0x9, 0xD) else 0)
                self.coverage.branches.add((pc, taken))
                target = (pc + 4 + _signed(_s8(imm)) * 2) & MASK
                if n in (0xD, 0xF):
                    self._slot(pc)
                    return target if taken else pc + 4
                return target if taken else following
        elif top == 0x9:
            r[n] = _s16(self._read16(pc + 4 + imm * 2))
            return following
        elif top == 0xA:
            displacement = opcode & 0xFFF
            if displacement & 0x800:
                displacement -= 0x1000
            target = (pc + 4 + displacement * 2) & MASK
            self._slot(pc)
            return target
        elif top == 0xC:
            if n == 0x0:
                self._write8(self.gbr + imm, r[0])
            elif n == 0x1:
                self._write16(self.gbr + imm * 2, r[0])
            elif n == 0x4:
                r[0] = _s8(self._read8(self.gbr + imm))
            elif n == 0x5:
                r[0] = _s16(self._read16(self.gbr + imm * 2))
            elif n == 0x8:
                self.t = int((r[0] & imm) == 0)
            elif n == 0x9:
                r[0] &= imm
            elif n == 0xA:
                r[0] ^= imm
            elif n == 0xB:
                r[0] |= imm
            elif n == 0xD:
                address = self.gbr + r[0]
                self._write8(address, self._read8(address) & imm)
            elif n == 0xF:
                address = self.gbr + r[0]
                self._write8(address, self._read8(address) | imm)
            else:
                raise AssertionError(f"unsupported {opcode:04x} at {pc:#x}")
            return following
        elif top == 0xD:
            r[n] = self._read32((pc & ~3) + 4 + imm * 4)
            return following
        elif top == 0xE:
            r[n] = _s8(imm)
            return following
        raise AssertionError(f"unsupported {opcode:04x} at {pc:#x}")


# Closed-form models.


def _transfer(data: bytes, word: int) -> int:
    """Stored scaling of FUN_00044034 and the FUN_00043CDE tail."""
    if data[0x8ADA] == 0:
        return 0xFFFF
    return min(0xFFFF, (word * data[0x8822] * 10 >> 6) // data[0x8ADA] + data[0x8816])


def _booster(data: bytes, sample: int, flags: int, previous: int) -> dict[int, int]:
    word = (sample & 0xFFFF) << 6
    outputs = {BOOSTER_COPY: sample & 0xFFFF}
    if not flags & 0x02:
        value = word
        outputs[BOOSTER_FLAGS] = (flags | 0x02) & 0xFF
    else:
        gain = data[0x8B76]
        value = ((word * gain + previous * ((128 - gain) & MASK)) & MASK) >> 7
        if value == previous and value < word:
            value += 1
    value = min(value, 0xFFFF)
    outputs[BOOSTER_FILTER] = value
    if data[0x8ADB] == 0:
        outputs[BOOSTER_SCALED] = 0xFFFF
    else:
        scaled = value * data[0x8823] * 5 // (data[0x8ADB] * 32) + data[0x8817]
        outputs[BOOSTER_SCALED] = min(0xFFFF, scaled)
    return outputs


def _vacuum(data: bytes, state: dict[int, int]) -> dict[int, int]:
    speed = state[SPEED]
    flags = state[SPEED_FLAGS]
    step = data[0x8AFE]
    flags = (flags | 0x40) if speed + (step if flags & 0x40 else 0) > data[0x8B17] else (flags & 0xBF)
    flags = (flags | 0x20) if speed + (step if flags & 0x20 else 0) > data[0x8B18] else (flags & 0xDF)
    if flags & 0x20:
        threshold = _u16(data, 0x9098)
    elif flags & 0x40:
        threshold = _u16(data, 0x9096)
    else:
        threshold = _u16(data, 0x9094)
    vacuum = max(0, state[SCALED_REFERENCE] - state[LATCHED_BOOSTER])
    outputs = {SPEED_FLAGS: flags, THRESHOLD: threshold, VACUUM_WORD: vacuum}

    low = state[LOW_FLAGS]
    if vacuum > threshold:
        outputs[LOW_HOLD] = data[0x8429]
        low &= 0x7F
        outputs[LOW_FLAGS] = low
    elif state[LOW_HOLD] == 0:
        low |= 0x80
        outputs[LOW_FLAGS] = low

    def brake(bound: int) -> bool:
        if not state[BRAKE_LATCH] & 0x40:
            return True
        return bool(state[BRAKE_QUALIFIER] & 0x30) and speed < bound

    status = not state[STATUS_A] & 0x80 and not state[STATUS_B] & 0x80
    override = bool(state[OVERRIDE_FLAGS] & 0x10)

    request = state[REQUEST_FLAGS]
    if (not low & 0x80 and brake(data[0x8AFA]) and status) or override:
        request &= 0xFE
    else:
        request |= 0x01

    sufficient = state[SUFFICIENT_FLAGS]
    if vacuum >= threshold + _u16(data, 0x909C):
        if state[SUFFICIENT_HOLD] == 0:
            sufficient |= 0x01
            outputs[SUFFICIENT_FLAGS] = sufficient
    else:
        outputs[SUFFICIENT_HOLD] = (data[0x8428] << 2) & 0xFFFF
        sufficient &= 0xFE
        outputs[SUFFICIENT_FLAGS] = sufficient

    bound = max(0, data[0x8AFA] - data[0x8AFD])
    if (sufficient & 0x01 and brake(bound) and status) or override:
        request |= 0x02
    else:
        request &= 0xFD
    outputs[REQUEST_FLAGS] = request

    mode = state[MODE_FLAGS]
    mode = (mode | 0x40) if request & 0x01 or not request & 0x02 else (mode & 0xBF)
    outputs[MODE_FLAGS] = mode
    return outputs


WORD_CELLS = {
    SCALED_REFERENCE,
    LATCHED_BOOSTER,
    THRESHOLD,
    VACUUM_WORD,
    SUFFICIENT_HOLD,
    BOOSTER_SAMPLE,
    BOOSTER_COPY,
    BOOSTER_FILTER,
    BOOSTER_SCALED,
}


def _cells(outputs: dict[int, int]) -> set[int]:
    cells = set()
    for address in outputs:
        cells.add(address)
        if address in WORD_CELLS:
            cells.add(address + 1)
    return cells


def _peek(sim: Sh2, address: int) -> int:
    return sim.peek16(address) if address in WORD_CELLS else sim.peek8(address)


# Division and shift helpers.


def _divide(data: bytes, dividend: int, divisor: int, coverage: Coverage) -> tuple[int, Sh2]:
    sim = Sh2(data, coverage)
    sim.r[0] = divisor
    sim.r[1] = dividend
    sim.r[2] = 0x13572468
    sim.r[3] = 0x2468ACE0
    sim.call(DIVIDE)
    assert (sim.r[2], sim.r[3], sim.r[15]) == (0x13572468, 0x2468ACE0, STACK_TOP)
    return sim.r[0], sim


def test_division_helper_is_unsigned_floor_division_on_every_path() -> None:
    data = _rom()
    coverage = Coverage()
    rng = random.Random(0x21E0C)

    # Eight div1 steps, two sixteen-step stages, and sixteen steps with rotcl.
    assert _ops(data, 0x21E0C, 8) == "2f26 2008 8941 620d 3020 8b44 0019 4018"
    assert _ops(data, 0x21E1C, 12) == "3016 8b0b " + " ".join(["3104"] * 8) + " 4124 62f6"
    assert _ops(data, 0x21E40, 16) == " ".join(["3104"] * 16)
    assert _ops(data, 0x21E60, 5) == "621d 212a 322e 4228 313c"
    assert _ops(data, 0x21E6A, 16) == " ".join(["3104"] * 16)
    assert _ops(data, 0x21EA2, 5) == "0019 621d 4228 4129 4224"
    assert _ops(data, 0x21EAC, 32) == " ".join(["3104 4224"] * 16)
    assert _ops(data, 0x21E96, 6) == "d117 d217 2122 e000 000b 62f6"
    assert _pc_literal(data, 0x21E96) == DIVIDE_ERROR
    assert _pc_literal(data, 0x21E98) == 0x44E

    cases = [(0, 1), (1, 1), (254, 255), (255, 255), (65279, 255), (65280, 255), (0xFFFFFFFF, 1)]
    cases += [(0xFFFFFFFF, 0xFFFF), (0xFFFFFFFF, 0x10000), (0xFFFFFFFF, 0xFFFFFFFF), (0x10000, 0x10001)]
    for _ in range(400):
        divisor = rng.randrange(1, 0x10000)
        cases.append((rng.randrange(divisor << 8), divisor))
        cases.append((rng.randrange(divisor << 8, 1 << 32), divisor))
        cases.append((rng.randrange(1 << 32), rng.randrange(0x10000, 1 << 32)))
    for dividend, divisor in cases:
        quotient, sim = _divide(data, dividend, divisor, coverage)
        assert quotient == dividend // divisor, (dividend, divisor)
        assert sim.written_outside_stack() == set()

    quotient, sim = _divide(data, 12345, 0, coverage)
    assert quotient == 0
    assert sim.written_outside_stack() == set(range(DIVIDE_ERROR, DIVIDE_ERROR + 4))
    assert sim.peek16(DIVIDE_ERROR) == 0 and sim.peek16(DIVIDE_ERROR + 2) == 0x44E

    coverage.assert_complete(data, CODE_RANGES[DIVIDE])


def test_shift_helper_is_arithmetic_shift_right_by_six() -> None:
    data = _rom()
    coverage = Coverage()
    assert _ops(data, SHIFT6, 7) == "4021 4021 4021 4021 4021 000b 4021"
    for value in (0, 1, 63, 64, 18349800, 0x7FFFFFFF, 0x80000000, 0xFFFFFFC0, 0xFFFFFFFF):
        sim = Sh2(data, coverage)
        sim.r[0] = value
        sim.call(SHIFT6)
        assert sim.r[0] == (_signed(value) >> 6) & MASK
    coverage.assert_complete(data, CODE_RANGES[SHIFT6])


def _block_copy(data: bytes, length: int, target: int, source: int, coverage: Coverage) -> Sh2:
    sim = Sh2(data, coverage)
    for offset in range(length):
        sim.poke8(source + offset, 0xA5 ^ (offset * 29))
    sim.r[0], sim.r[1], sim.r[2] = length, target, source
    for index in range(3, 15):
        sim.r[index] = 0x00100000 + index
    sim.call(BLOCK_COPY)
    return sim


def test_block_copy_helper_copies_r0_bytes_forward() -> None:
    data = _rom()
    coverage = Coverage()
    target, source = 0xFFFF3000, 0xFFFF3100
    for length in range(10):
        sim = _block_copy(data, length, target, source, coverage)
        assert sim.written_outside_stack() == {target + offset for offset in range(length)}
        assert [sim.peek8(target + offset) for offset in range(length)] == [
            sim.peek8(source + offset) for offset in range(length)
        ]
        assert sim.r[2:15] == [source] + [0x00100000 + index for index in range(3, 15)]
        assert sim.r[15] == STACK_TOP
    coverage.assert_complete(data, CODE_RANGES[BLOCK_COPY])


def test_frame_copy_at_0x20ff0_moves_six_bytes() -> None:
    """Executes FUN_00020F1A from 0x00020F3A through the copy at 0x00020FF0, helpers included."""
    data = _rom()
    # r11 = 0xF0 from 0x00020F30; the next three instructions write r2 and SR only.
    assert _ops(data, 0x20F30, 5) == "ebf0 6bbc 2269 22bb 420e"
    assert _u16(data, 0x20F3C) == 0xEE06 and _u16(data, 0x20FEA) == 0x60E3
    coverage = Coverage()
    sim = Sh2(data, coverage)
    for address in range(RAM_START, RAM_END):
        sim.poke8(address, address * 7 + 3)
    for address in range(0xFFFFF430, 0xFFFFF434):
        sim.poke8(address, 0)
    sim.r[11] = 0xF0
    sim.run(0x20F3A, 0x20FF0)
    assert (sim.r[0], sim.r[1], sim.r[2], sim.r[12]) == (6, 0xFFFF2564, 0xFFFF256A, BLOCK_COPY)
    # The helpers called before the copy: FUN_000225C0 (r12), 0x00022164 (r8), 0x00022230 (r10).
    assert {BLOCK_COPY, 0x22164, 0x22230} <= coverage.executed
    source = [sim.peek8(0xFFFF256A + offset) for offset in range(6)]
    sim.written.clear()
    sim.run(0x20FF0, 0x20FF4)
    assert sim.written_outside_stack() == set(range(0xFFFF2564, 0xFFFF256A))
    assert [sim.peek8(0xFFFF2564 + offset) for offset in range(6)] == source
    assert sim.peek16(0xFFFF2568) == sim.peek16(0xFFFF256E)


# Scaled reference and scaled argument.


def _scale_argument(data: bytes, word: int, coverage: Coverage) -> Sh2:
    sim = Sh2(data, coverage)
    sim.r[4] = 0xA5A50000 | word
    sim.call(SCALE_ARGUMENT)
    assert sim.r[15] == STACK_TOP
    return sim


def _reference_tail(data: bytes, word: int, coverage: Coverage) -> Sh2:
    sim = Sh2(data, coverage)
    sim.r[13] = REFERENCE_BASE
    sim.gbr = REFERENCE_BASE
    sim.poke16(REFERENCE, word)
    sim.run(*REFERENCE_TAIL)
    assert sim.r[15] == STACK_TOP
    return sim


def test_scaled_reference_and_argument_paths_execute_the_stored_transfer() -> None:
    data = _rom()
    coverage = Coverage()

    assert _ops(data, SCALE_ARGUMENT, 42) == (
        "4f22 4f12 d727 6270 2228 891c d326 644d 843c 620c 0247 061a 6063 4008 306c "
        "d623 460b 4000 d71f 6103 d61d 6570 460b 605c d31d 6530 665c 306c e6ff 666d "
        "3066 8f03 6203 a001 6263 e2ff d512 900e 4f16 4f26 000b 0525"
    )
    assert [_pc_literal(data, a) for a in (0x44038, 0x44040, 0x44052, 0x4405C, 0x4407C)] == [
        0x8ADA, 0x8816, SHIFT6, DIVIDE, 0xFFFF2854,
    ]
    assert _pc_word(data, 0x4407E) == 0x0AC0 and 0xFFFF2854 + 0x0AC0 == SCALED_ARGUMENT
    # FUN_00043EEC and FUN_00043F60 call it with bsr.
    for site in (0x43F52, 0x4402A):
        opcode = _u16(data, site)
        assert opcode >> 12 == 0xB and site + 4 + (opcode & 0xFFF) * 2 == SCALE_ARGUMENT

    assert _ops(data, REFERENCE_TAIL[0], 39) == (
        "d434 6240 2228 8920 9029 d731 06dd 847e 666d 620c 0267 061a 6063 4008 306c "
        "d62e 460b 4000 d42b 6103 d62c 6540 645c 460b 6043 d727 6203 e6ff 8472 666d "
        "650c 325c 3266 8b00 6263 a001 6023 e0ff c1f7"
    )
    assert [_pc_literal(data, a) for a in (0x43DAC, 0x43DB6, 0x43DCA, 0x43DD4)] == [
        0x8ADA, 0x8814, SHIFT6, DIVIDE,
    ]
    assert _pc_word(data, 0x43DB4) == 0x0EF0 and REFERENCE_BASE + 0x0EF0 == REFERENCE
    assert REFERENCE_BASE + 0xF7 * 2 == SCALED_REFERENCE
    # FUN_00043CDE loads GBR and r13 with the base, and calls the clamp just before the tail.
    assert _ops(data, 0x43CE8, 2) == "d05a 401e" and _pc_literal(data, 0x43CE8) == REFERENCE_BASE
    assert _u16(data, 0x43CEE) == 0xDD59 and _pc_literal(data, 0x43CEE) == REFERENCE_BASE
    assert _u16(data, 0x43DA8) == 0xBF74 and 0x43DA8 + 4 + (0xF74 - 0x1000) * 2 == 0x43C94

    assert (data[0x8822], data[0x8ADA], data[0x8816]) == (28, 255, 20)

    rng = random.Random(0x4AC2)
    words = sorted({n << 6 for n in range(1024)} | {0xFFFF, 1, 40450, 57878, 58461})
    words += [rng.randrange(0x10000) for _ in range(300)]
    for word in words:
        expected = _transfer(data, word)
        assert expected == 20 + 7 * word // 408
        sim = _scale_argument(data, word, coverage)
        assert sim.peek16(SCALED_ARGUMENT) == expected
        assert sim.written_outside_stack() == {SCALED_ARGUMENT, SCALED_ARGUMENT + 1}
    for word in words[::4]:
        sim = _reference_tail(data, word, coverage)
        assert sim.peek16(SCALED_REFERENCE) == _transfer(data, word)
        assert sim.written_outside_stack() == {SCALED_REFERENCE, SCALED_REFERENCE + 1}

    # Zero divisor and saturation outcomes with calibration-only differences.
    zero = _patched(data, x8ADA=0)
    wide = _patched(data, x8ADA=1, x8822=255)
    for variant in (zero, wide):
        for word in (0, 0x40, 57878, 0xFFC0, 0xFFFF):
            expected = _transfer(variant, word)
            assert _scale_argument(variant, word, coverage).peek16(SCALED_ARGUMENT) == expected
            assert _reference_tail(variant, word, coverage).peek16(SCALED_REFERENCE) == expected
    assert _transfer(zero, 0) == 0xFFFF and _transfer(wide, 0xFFFF) == 0xFFFF

    coverage.assert_complete(data, CODE_RANGES[SCALE_ARGUMENT])
    coverage.assert_complete(data, CODE_RANGES[REFERENCE_TAIL[0]])


def test_initializer_and_clamp_values_follow_the_transfer() -> None:
    data = _rom()
    assert _pc_literal(data, 0x2F1B8) == REFERENCE_BASE and _u16(data, 0x2F1B8) >> 8 == 0xDB
    assert _pc_literal(data, 0x2F2DA) == 0x9242 and _u16(data, 0x2F2E0) == 0x6261
    assert _pc_literal(data, 0x2F2E6) == 0x8D12 and _u16(data, 0x2F2FA) == 0x6261
    assert _pc_word(data, 0x2F2F6) == 0x0EF0 and _u16(data, 0x2F2F8) == 0x0B25
    assert _pc_word(data, 0x2F2FC) == 0x01EE and _u16(data, 0x2F300) == 0x0B25
    assert REFERENCE_BASE + 0x01EE == SCALED_REFERENCE

    default_reference = _u16(data, 0x9242)
    default_scaled = _u16(data, 0x8D12)
    clamp = (_u16(data, 0x9246), _u16(data, 0x9244))
    assert (default_reference, default_scaled, clamp) == (57878, 1013, (40450, 58461))
    assert _transfer(data, default_reference) == default_scaled
    assert tuple(_transfer(data, word) for word in clamp) == (713, 1023)
    assert tuple(f"{float(Fraction(word, 64) * 5 / 1024):.2f}" for word in clamp) == ("3.09", "4.46")


# Booster pressure.


def test_booster_pressure_path_executes_the_filter_and_transfer() -> None:
    data = _rom()
    coverage = Coverage()

    assert _ops(data, 0x45A54, 18) == (
        "d02e 401e d62e d52f 856c de2f 6203 6603 9052 672d 4708 0565 e024 00ec 4708 c802 8f06 4708"
    )
    assert [_pc_literal(data, a) for a in (0x45A54, 0x45A58, 0x45A5A, 0x45A5E)] == [
        0xFFFF26D6, 0xFFFF3850, 0xFFFF3C18, 0xFFFF458A,
    ]
    assert [_pc_literal(data, a) for a in (0x45A84, 0x45ABE, 0x45ACA, 0x45AE0, 0x45AE6)] == [
        0x8B76, 0x8ADB, 0x8823, DIVIDE, 0x8817,
    ]
    assert _pc_word(data, 0x45A64) == 0x06CA and 0xFFFF3C18 + 0x06CA == BOOSTER_COPY
    assert 0xFFFF3850 + 0x18 == BOOSTER_SAMPLE and 0xFFFF458A + 0x24 == BOOSTER_FLAGS
    assert 0xFFFF26D6 + 0x7D * 2 == BOOSTER_FILTER and 0xFFFF26D6 + 0x47 * 2 == BOOSTER_SCALED
    assert (data[0x8B76], data[0x8823], data[0x8ADB], data[0x8817]) == (64, 28, 255, 20)

    def run(variant: bytes, sample: int, flags: int, previous: int | None) -> None:
        sim = Sh2(variant, coverage)
        sim.gbr = 0x0BADCAFE
        sim.r[14] = 0x1234
        sim.poke16(BOOSTER_SAMPLE, sample)
        sim.poke8(BOOSTER_FLAGS, flags)
        if previous is not None:
            sim.poke16(BOOSTER_FILTER, previous)
        sim.call(BOOSTER)
        assert (sim.gbr, sim.r[14], sim.r[15]) == (0x0BADCAFE, 0x1234, STACK_TOP)
        expected = _booster(variant, sample, flags, previous or 0)
        assert {a: _peek(sim, a) for a in expected} == expected
        assert sim.written_outside_stack() == _cells(expected)

    rng = random.Random(0x2764)
    for sample in [0, 1, 511, 1023, 1024, 0xFFFF] + [rng.randrange(1024) for _ in range(100)]:
        run(data, sample, rng.randrange(256) & ~0x02, None)
    for _ in range(400):
        sample = rng.randrange(1024)
        word = sample << 6
        previous = rng.choice([word, max(word - 1, 0), word + 1, rng.randrange(0x10000)])
        run(data, sample, rng.randrange(256) | 0x02, previous)
    run(data, 0xFFFF, 0x02, 0xFFFF)
    for variant in (_patched(data, x8ADB=0), _patched(data, x8ADB=1, x8823=255)):
        for sample in (0, 700, 1023):
            run(variant, sample, 0x00, None)

    # The transfer equals the scaled-reference transfer for every filtered word.
    for word in range(0x10000):
        assert word * 28 * 5 // (255 * 32) + 20 == 20 + 7 * word // 408

    coverage.assert_complete(data, CODE_RANGES[BOOSTER])


# Booster vacuum and the throttled-mode flag.


def _vacuum_run(data: bytes, state: dict[int, int], coverage: Coverage) -> None:
    sim = Sh2(data, coverage)
    saved = {9: 0x99, 10: 0xAA, 11: 0xBB, 12: 0xCC, 13: 0xDD}
    for register, value in saved.items():
        sim.r[register] = value
    sim.gbr = 0x0BADCAFE
    for address, value in state.items():
        if address in WORD_CELLS:
            sim.poke16(address, value)
        else:
            sim.poke8(address, value)
    sim.call(VACUUM)
    assert {register: sim.r[register] for register in saved} == saved
    assert (sim.gbr, sim.r[15]) == (0x0BADCAFE, STACK_TOP)
    expected = _vacuum(data, state)
    assert {a: _peek(sim, a) for a in expected} == expected, state
    assert sim.written_outside_stack() == _cells(expected), state


def _random_state(rng: random.Random, data: bytes) -> dict[int, int]:
    thresholds = [_u16(data, a) for a in (0x9094, 0x9096, 0x9098)]
    edge = rng.choice(thresholds) + rng.choice([-1, 0, 1, 9, 10, 11])
    reference = rng.randrange(0x10000) if rng.random() < 0.2 else rng.randrange(600, 1150)
    booster = max(0, reference - edge) if rng.random() < 0.6 else rng.randrange(0x10000)
    return {
        SPEED: rng.choice([0, 1, 2, 3, 4, 6, 7, 8, 9, 127, 128, 252, 253, 254, 255, rng.randrange(256)]),
        SPEED_FLAGS: rng.randrange(256),
        SCALED_REFERENCE: reference,
        LATCHED_BOOSTER: booster,
        LOW_FLAGS: rng.randrange(256),
        LOW_HOLD: 0 if rng.random() < 0.5 else rng.randrange(1, 256),
        SUFFICIENT_FLAGS: rng.randrange(256),
        SUFFICIENT_HOLD: 0 if rng.random() < 0.5 else rng.randrange(1, 0x10000),
        REQUEST_FLAGS: rng.randrange(256),
        MODE_FLAGS: rng.randrange(256),
        OVERRIDE_FLAGS: rng.randrange(256) & (0xFF if rng.random() < 0.3 else 0xEF),
        BRAKE_LATCH: rng.randrange(256),
        BRAKE_QUALIFIER: rng.randrange(256),
        STATUS_A: rng.randrange(256) & (0xFF if rng.random() < 0.3 else 0x7F),
        STATUS_B: rng.randrange(256) & (0xFF if rng.random() < 0.3 else 0x7F),
    }


def test_vacuum_flag_function_matches_the_model() -> None:
    data = _rom()
    coverage = Coverage()

    assert _ops(data, VACUUM, 8) == "2f96 2fa6 2fb6 2fc6 2fd6 4f13 d07e 401e"
    assert _pc_literal(data, 0x5A320) == 0xFFFF4506
    assert [_pc_literal(data, a) for a in (0x5A324, 0x5A342, 0x5A34A, 0x5A372)] == [
        0xFFFF1084, 0x8AFA, 0x8B17, 0x8B18,
    ]
    assert [_pc_literal(data, a) for a in (0x5A38C, 0x5A398, 0x5A39E)] == [0x9098, 0x9096, 0x9094]
    assert [_pc_literal(data, a) for a in (0x5A3A2, 0x5A3A6, 0x5A3AC)] == [
        0xFFFF2854, REFERENCE_BASE, 0xFFFF25D8,
    ]
    assert [_pc_literal(data, a) for a in (0x5A3D0, 0x5A3E0, 0x5A3F6, 0x5A402, 0x5A424)] == [
        0xFFFF472C, 0x8429, 0xFFFF23AC, 0xFFFF23BC, 0xFFFF5E94,
    ]
    assert [_pc_literal(data, a) for a in (0x5A45C, 0x5A46E, 0x5A47C)] == [0x909C, 0xFFFF4822, 0x8428]
    assert [_pc_word(data, a) for a in (0x5A3A4, 0x5A3AA, 0x5A3C2, 0x5A426, 0x5A434)] == [
        0x0AD0, 0x01EE, 0x0AE4, 0x0136, 0x0139,
    ]
    assert 0xFFFF2854 + 0x0AD0 == THRESHOLD and 0xFFFF2854 + 0x0AE4 == VACUUM_WORD
    assert 0xFFFF25D8 + 0x8E == LATCHED_BOOSTER and 0xFFFF1084 + 0x78 == SPEED
    assert 0xFFFF472C + 0x27 == LOW_HOLD and 0xFFFF4822 + 0x0A == SUFFICIENT_HOLD
    assert (0xFFFF5E94 + 0x136, 0xFFFF5E94 + 0x139) == (STATUS_A, STATUS_B)
    assert (0xFFFF23AC + 3, 0xFFFF23BC + 1) == (BRAKE_LATCH, BRAKE_QUALIFIER)
    assert [0xFFFF4506 + offset for offset in (0x10, 0x58, 0x0F, 0x5F, 0x71, 0x6D)] == [
        LOW_FLAGS, REQUEST_FLAGS, SUFFICIENT_FLAGS, MODE_FLAGS, SPEED_FLAGS, OVERRIDE_FLAGS,
    ]
    # FUN_0009DFA8 loads the same status-table base.
    assert _u16(data, 0x9DFCA) == 0xD484 and _pc_literal(data, 0x9DFCA) == 0xFFFF5E94

    assert [_u16(data, a) for a in (0x9094, 0x9096, 0x9098, 0x909C)] == [0, 467, 547, 10]
    assert [data[a] for a in (0x8429, 0x8428, 0x8AFA, 0x8AFD, 0x8AFE, 0x8B17, 0x8B18)] == [
        3, 8, 254, 1, 1, 2, 7,
    ]

    rng = random.Random(0x5A314)
    for _ in range(2500):
        _vacuum_run(data, _random_state(rng, data), coverage)
    for speed in (1, 2, 3, 6, 7, 8, 252, 253, 254, 255):
        for speed_flags in (0x00, 0x20, 0x40, 0x60):
            state = _random_state(rng, data)
            state.update({SPEED: speed, SPEED_FLAGS: speed_flags, BRAKE_LATCH: 0x40, BRAKE_QUALIFIER: 0x10})
            state.update({OVERRIDE_FLAGS: 0, STATUS_A: 0, STATUS_B: 0, LOW_HOLD: 0, SUFFICIENT_HOLD: 0})
            _vacuum_run(data, state, coverage)
    # A step above the bound clamps the second bound to zero (0x0005A49E).
    clamped = _patched(data, x8AFD=0xFF)
    for _ in range(200):
        _vacuum_run(clamped, _random_state(rng, clamped), coverage)
    coverage.assert_complete(data, CODE_RANGES[VACUUM])


def test_vacuum_model_reads_as_the_document_states() -> None:
    data = _rom()
    base = {
        SPEED: 0, SPEED_FLAGS: 0, SCALED_REFERENCE: 1013, LATCHED_BOOSTER: 1013,
        LOW_FLAGS: 0, LOW_HOLD: 0, SUFFICIENT_FLAGS: 0, SUFFICIENT_HOLD: 0,
        REQUEST_FLAGS: 0, MODE_FLAGS: 0, OVERRIDE_FLAGS: 0, BRAKE_LATCH: 0,
        BRAKE_QUALIFIER: 0, STATUS_A: 0, STATUS_B: 0,
    }

    def outputs(**changes: int) -> dict[int, int]:
        state = dict(base)
        state.update({globals()[name]: value for name, value in changes.items()})
        return _vacuum(data, state)

    # Threshold selection by the latched speed bits (2 km/h per count).
    assert outputs(SPEED=2)[THRESHOLD] == 0
    assert outputs(SPEED=3)[THRESHOLD] == 467
    assert outputs(SPEED=2, SPEED_FLAGS=0x40)[THRESHOLD] == 467
    assert outputs(SPEED=8)[THRESHOLD] == 547
    assert outputs(SPEED=7, SPEED_FLAGS=0x60)[THRESHOLD] == 547
    assert (2 * data[0x8B17], 2 * data[0x8B18]) == (4, 14)

    # A vacuum at or below the threshold holds the low flag; ten counts above it sets sufficiency.
    assert outputs(SPEED=3, SCALED_REFERENCE=1467, LATCHED_BOOSTER=1000)[MODE_FLAGS] & 0x40
    engaged = outputs(SPEED=3, SCALED_REFERENCE=1477, LATCHED_BOOSTER=1000)
    assert engaged[SUFFICIENT_FLAGS] & 0x01 and not engaged[MODE_FLAGS] & 0x40
    assert outputs(SPEED=3, SCALED_REFERENCE=1476, LATCHED_BOOSTER=1000)[MODE_FLAGS] & 0x40

    # The brake input requests the throttled mode unless 0xFFFF23BD bit 5 or 4 is set below speed 253.
    assert outputs(SCALED_REFERENCE=1010, LATCHED_BOOSTER=1000, BRAKE_LATCH=0x40)[MODE_FLAGS] & 0x40
    released = outputs(SCALED_REFERENCE=1010, LATCHED_BOOSTER=1000, BRAKE_LATCH=0x40, BRAKE_QUALIFIER=0x20)
    assert not released[MODE_FLAGS] & 0x40
    fast = outputs(
        SPEED=253, SPEED_FLAGS=0x60, SCALED_REFERENCE=1557, LATCHED_BOOSTER=1000,
        BRAKE_LATCH=0x40, BRAKE_QUALIFIER=0x20,
    )
    assert fast[MODE_FLAGS] & 0x40
    assert outputs(SCALED_REFERENCE=1010, LATCHED_BOOSTER=1000, STATUS_B=0x80)[MODE_FLAGS] & 0x40
    assert not outputs(SCALED_REFERENCE=900, LATCHED_BOOSTER=1000, OVERRIDE_FLAGS=0x10)[MODE_FLAGS] & 0x40


def test_vector_120_handler_counts_down_the_hold_arrays_every_tenth_call() -> None:
    data = _rom()
    # VBR = 0x00020004; vector 120 lies at VBR + 120 * 4.
    assert _ops(data, 0x21CD4, 2) == "d202 422e" and _pc_literal(data, 0x21CD4) == 0x00020004
    assert 0x00020004 + 120 * 4 == 0x201E4 and _u32(data, 0x201E4) == 0x0002040C
    # Call counter 0xFFFFADC0: increment, compare with 10, and reset to zero after the block.
    assert _ops(data, 0x205B6, 8) == "9849 6082 7001 880a 8d02 2802 a1a8 0009"
    assert _pc_word(data, 0x205B6) == 0xADC0
    assert _ops(data, 0x208E8, 2) == "a014 e200" and _u16(data, 0x20914) == 0x2822
    # Byte array 0xFFFF472C + 0xC4 and word array 0xFFFF4822 + 0x46 decrement every nonzero cell.
    assert _ops(data, 0x2060E, 20) == (
        "d519 e4c4 644c 6253 324c 3522 8d0c 6653 6260 2228 8903 6260 72ff 622c 2620 7601 6253 324c 3622 8bf3"
    )
    assert _pc_literal(data, 0x2060E) == 0xFFFF472C
    assert _ops(data, 0x20636, 11) == "d510 6253 7246 3522 8d25 6653 6261 2228 891c a018 6261"
    assert _pc_literal(data, 0x20636) == 0xFFFF4822
    assert _ops(data, 0x2067C, 8) == "72ff 622d 2621 7602 6253 7246 3622 8bda"
    assert 0xFFFF472C <= LOW_HOLD < 0xFFFF472C + 0xC4
    assert 0xFFFF4822 <= SUFFICIENT_HOLD < 0xFFFF4822 + 0x46 and (SUFFICIENT_HOLD - 0xFFFF4822) % 2 == 0
    assert (0xFFFF472C + 0xC4 - 1, 0xFFFF4822 + 0x46 - 1) == (0xFFFF47EF, 0xFFFF4867)
    assert (data[0x8429], data[0x8428] << 2) == (3, 32)


def _branch_target(data: bytes, address: int) -> int:
    opcode = _u16(data, address)
    if opcode >> 12 == 0xA:
        displacement = opcode & 0xFFF
        return address + 4 + (displacement - 0x1000 if displacement & 0x800 else displacement) * 2
    return address + 4 + _signed(_s8(opcode)) * 2


def test_sampler_cycle_count_and_port_bits() -> None:
    data = _rom()
    # r13 = 0xFFFF1274: the count is byte 0x414; bytes 0x415 and 0x416 must be clear.
    assert _u16(data, 0x2AA9C) == 0xDDB3 and _pc_literal(data, 0x2AA9C) == 0xFFFF1274
    assert [_pc_word(data, a) for a in (0x2AAAA, 0x2AAB6, 0x2AAC2, 0x2AE04)] == [0x415, 0x416, 0x414, 0x414]
    assert 0xFFFF1274 + 0x414 == 0xFFFF1688
    assert _ops(data, 0x2AAAC, 4) == "02dc 2228 8901 a1ab" and _ops(data, 0x2AAB8, 4) == "02dc 2228 8901 a1a5"
    assert _ops(data, 0x2AAC4, 5) == "06dc 7601 666c 0d64 6063"
    # cmp/eq #n,r0 with r0 = count; each bf leads to the next compare, the last to the common exit.
    chain = (0x2AACE, 0x2AB2C, 0x2AB80, 0x2ABBE, 0x2AC2C, 0x2AC6C, 0x2ACD0, 0x2AD86)
    targets = [_branch_target(data, address + 2) for address in chain]
    assert [_u16(data, address) for address in chain] == [0x8800 | n for n in range(1, 9)]
    assert all(_u16(data, address + 2) >> 8 == 0x8B for address in chain)
    assert targets == [0x2AB2C, 0x2AB80, 0x2ABBE, 0x2AC2C, 0x2AC6C, 0x2ACCE, 0x2AD84, 0x2AE24]
    assert _u16(data, 0x2ACCE) == _u16(data, 0x2AD84) == 0x6063
    # Cycle 8 clears the count.
    assert _ops(data, 0x2AE06, 3) == "e200 a00c 0d24"
    # PFDR = 0xFFFFF748 + 6. Cycles 1, 3, 5, 7 set bit 13; cycles 2, 4, 6 keep bits 0..12 and
    # set 0x4000, 0x8000, 0xC000 through the tail at 0x0002AD42; cycle 8 clears bits 13..15.
    assert (_s16(0xF748) + 6) & MASK == 0xFFFFF74E
    assert _ops(data, 0x2AB1C, 6) == "9583 e720 4718 8553 207b 8153"
    assert _ops(data, 0x2AB72, 7) == "9558 9758 8553 2079 81f4 a0e1 e740"
    assert _ops(data, 0x2AC10, 7) == "9509 9709 8553 2079 9707 a093 81f4"
    assert _ops(data, 0x2ACC0, 7) == "954d 974d 8553 2079 974b a03b 81f4"
    assert _ops(data, 0x2AD3C, 6) == "950f e720 8553 4718 207b 8153"
    assert _ops(data, 0x2ADE6, 6) == "952c d39e 8553 600d 2039 8153"
    assert _pc_literal(data, 0x2ADE8) == 0xFFFF1FFF
    for address in (0x2AB1C, 0x2AB72, 0x2AC10, 0x2ACC0, 0x2AD3C, 0x2ADE6):
        assert _pc_word(data, address) == 0xF748
    assert [_pc_word(data, a) for a in (0x2AB74, 0x2AC12, 0x2AC18, 0x2ACC2, 0x2ACC8)] == [
        0x1FFF, 0x1FFF, 0x8000, 0x1FFF, 0xC000
    ]
    assert [_branch_target(data, a) for a in (0x2AB7C, 0x2AC1A, 0x2ACCA)] == [0x2AD42, 0x2AD44, 0x2AD44]
    assert [_branch_target(data, a) for a in (0x2ABBA, 0x2AC68)] == [0x2AD28, 0x2AD28]
    assert _ops(data, 0x2AD42, 3) == "4718 207b 8153"
    # Cycle 7 reaches 0x0002AD28 by falling through; 0x0002AD28..0x0002AD3C holds no branch.
    assert not any(_control_or_pc_relative(_u16(data, a)) and _u16(data, a) >> 12 != 0x9
                   for a in range(0x2AD26, 0x2AD3C, 2))
    updates = {1: (0xFFFF, 0x2000), 2: (0x1FFF, 0x4000), 3: (0xFFFF, 0x2000), 4: (0x1FFF, 0x8000),
               5: (0xFFFF, 0x2000), 6: (0x1FFF, 0xC000), 7: (0xFFFF, 0x2000), 8: (0x1FFF, 0x0000)}
    port = 0
    for cycle in range(1, 9):
        mask, value = updates[cycle]
        port = (port & mask) | value
        assert port >> 13 == cycle % 8

    doc = _doc()
    for phrase in (
        "On each call with `0xFFFF1689` and `0xFFFF168A` clear, the ADC sampler `FUN_0002AA88` "
        "increments the cycle count `0xFFFF1688` and runs cycle `n` at count `n`; cycle 8 clears the count.",
        "ends by setting bits 13..15 of `PFDR` (`0xFFFFF74E`) to `n mod 8`.",
    ):
        assert phrase in doc, phrase


def test_sampler_channels_and_block_copy() -> None:
    data = _rom()
    manual = " ".join(MANUAL_PATH.read_text(encoding="utf-8").split())

    assert _ops(data, 0x2AA96, 3) == "eef8 d5b3 4e18"
    assert (_s8(0xF8) << 8) & MASK == 0xFFFFF800
    assert _pc_literal(data, 0x2AA90) == 0xFFFF1CC4 and _u16(data, 0x2AA92) == 0x401E
    # Cycle 4: AN1 and AN13.
    assert _u16(data, 0x2ABBE) == 0x8804
    assert _ops(data, 0x2ABE0, 14) == "85e1 600d 4009 4009 4009 815c e022 02ed d55f 602d 4009 4009 4009 8152"
    assert _pc_literal(data, 0x2ABC4) == 0xFFFF3850 and 0xFFFF3850 + 0x18 == BOOSTER_SAMPLE
    assert _pc_literal(data, 0x2ABF0) == 0xFFFF256A
    # Cycle 6: AN12 to 0xFFFF1CDC and, while ROM8[0x87D1] bit 7 is set, to 0xFFFF1CE2.
    assert _u16(data, 0x2AC6C) == 0x8806
    assert _ops(data, 0x2AC7C, 20) == (
        "e020 02ed 602d d23d 4009 4009 4009 c10c 6020 c880 8906 e020 02ed 602d 4009 4009 4009 c10f 85e1 600d"
    )
    assert _pc_literal(data, 0x2AC82) == 0x87D1 and data[0x87D1] == 0xC0
    assert (0xFFFF1CC4 + 0x0C * 2, 0xFFFF1CC4 + 0x0F * 2) == (0xFFFF1CDC, 0xFFFF1CE2)
    # FUN_0004185A reads 0xFFFF1CE2 and stores the filtered result << 6 as the DID 0x1116 source.
    assert _pc_literal(data, 0x41868) == 0xFFFF1CC4 and _u16(data, 0x4186C) == 0x856F
    assert _pc_literal(data, 0x4188A) == 0x0003E050 and _u16(data, 0x4188E) == 0x420B
    assert _ops(data, 0x41896, 9) == "620d c1a3 4208 622d 4208 622d 4208 e072 0625"
    assert _pc_literal(data, 0x41894) == 0xFFFF1104 and 0xFFFF1104 + 0x72 == 0xFFFF1176
    assert _u32(data, 0x22718 + 0x16 * 4) == 0xFFFF1176
    # FUN_00020F1A copies 6 bytes 0xFFFF256A.. to 0xFFFF2564.. through FUN_000225C0 (r14 = 6).
    assert _ops(data, 0x20FE8, 5) == "d158 60e3 d258 de59 4c0b"
    assert (_pc_literal(data, 0x20FE8), _pc_literal(data, 0x20FEC)) == (0xFFFF2564, 0xFFFF256A)
    assert _u16(data, 0x20F3C) == 0xEE06 and _pc_literal(data, 0x20F58) == 0x000225C0
    assert _ops(data, 0x225CA, 4) == "6423 340c 6024 2100"
    assert 0xFFFF256E - 0xFFFF256A == 0xFFFF2568 - 0xFFFF2564 < 6

    for register, address in (("ADDR1", "H'FFFFF802"), ("ADDR12", "H'FFFFF820"), ("ADDR13", "H'FFFFF822")):
        assert f"{register} (H/L) R H'0000 {address} 8, 16" in manual
    assert "| Port F data register | PFDR | R/W | H'0000 | H'FFFFF74E | 8, 16 |" in manual
    assert (
        "The A/D converter converts analog input to a 10-bit digital value. The upper 8 bits of this "
        "data are stored in the upper byte of the ADDR corresponding to the selected channel, and the "
        "lower 2 bits in the lower byte of that ADDR."
    ) in manual

    doc = _doc()
    assert "The per-pass block copy `0xFFFF2564 <- 0xFFFF256A` (6 bytes, `FUN_00020F1A` at `0x00020FF0`) copies `0xFFFF256E` to `0xFFFF2568`." in doc
    assert "`ROM8[0x87D1]` bit 7 is set (stock `0xC0`)" in doc
    assert "sample different converter channels, AN12 in cycle 6 and AN13 in cycle 4" in doc
    assert "the DID `0x1116` source (`ROM32[0x22770]`)" in doc


def test_units_and_thresholds_in_the_document() -> None:
    data = _rom()
    doc = _doc()

    # Transfer of a 10-bit sample n: 56/51 counts per sample count; 5 V per 1024 counts.
    for n in range(1024):
        assert _transfer(data, n << 6) == 20 + 56 * n // 51
    counts_per_volt = Fraction(56, 51) * Fraction(1024, 5)
    assert counts_per_volt == Fraction(57344, 255)
    volts_per_count = 1 / counts_per_volt
    assert max(_transfer(data, word) for word in range(0x10000)) == 1144

    assert "`S = 20 + floor(7 * W / 408)`" in doc
    assert "`S = 20 + floor(56 * n / 51)`" in doc
    assert "`S` never exceeds 1144" in doc
    assert (
        f"one count of `S` is 255/57344 V ({float(volts_per_count) * 1000:.3f} mV), "
        f"{float(counts_per_volt):.1f} counts per volt: `S = 20 + floor(57344 * V / 255)`"
    ) in doc
    assert "maps the initializer value 57878 of `0xFFFF57C4` to 1013, the initializer value of `0xFFFF4AC2`" in doc
    assert "maps the clamp bounds 40450 and 58461 to 713 and 1023" in doc
    offset_kpa = Fraction(data[0x8816], 10)
    slope_kpa = counts_per_volt / 10
    assert f"`P = {float(offset_kpa):.1f} kPa + {float(slope_kpa):.2f} kPa/V * V`" in doc

    # Candidate column of the manual-row table: the transfer at 1 hPa per count.
    rows = re.findall(r"\| (\d+) hPa \| (\d\.\d) - (\d\.\d) V \| (\d\.\d\d) V \|", doc)
    assert [int(row[0]) for row in rows] == [800, 850, 900, 950, 1000, 1050]
    for pressure, low, high, candidate in rows:
        volts = (int(pressure) - data[0x8816]) * volts_per_count
        assert f"{float(volts):.2f}" == candidate
        assert Fraction(low) <= volts <= Fraction(high)
    rows = re.findall(r"\| -(\d+(?:\.\d)?) kPa \(-(\d+) mmHg\) \| (\d\.\d) - (\d\.\d) V \| (\d\.\d\d) V \|", doc)
    assert [row[:2] for row in rows] == [("40", "300"), ("53.3", "400"), ("66.7", "500"), ("80", "600")]
    for kpa, _, low, high, candidate in rows:
        volts = Fraction(kpa) * 10 * volts_per_count
        assert f"{float(volts):.2f}" == candidate
        assert Fraction(low) <= volts <= Fraction(high)

    # Threshold table: the vacuum is a difference of scaled words, so only the slope applies.
    step = _u16(data, 0x909C)
    pascal_per_mmhg = Fraction(101325, 760)

    def volts(counts: int) -> str:
        return "0" if counts == 0 else f"{float(counts * volts_per_count):.3f}"

    def kpa(counts: int) -> str:
        return "0" if counts == 0 else f"{counts / 10:.1f}"

    def mmhg(counts: int) -> str:
        return f"{float(counts * 100 / pascal_per_mmhg):.1f}"

    selections = {
        0x9094: "bits 6 and 5 clear",
        0x9096: "bit 6 set, bit 5 clear",
        0x9098: "bit 5 set",
    }
    for address, selected in selections.items():
        low = _u16(data, address)
        high = low + step
        row = (
            f"| {low} | {selected} | `<= {low}` | `>= {high}` | {volts(low)} / {volts(high)} V | "
            f"{kpa(low)} / {kpa(high)} kPa"
        )
        if low:
            row += f" ({mmhg(low)} / {mmhg(high)} mmHg)"
        assert row + " |" in doc, row

    for phrase in (
        f"`ROM8[0x8822]` = {data[0x8822]}, `ROM8[0x8ADA]` = {data[0x8ADA]}, and `ROM8[0x8816]` = {data[0x8816]}",
        f"`ROM8[0x8823]` = {data[0x8823]}, `ROM8[0x8ADB]` = {data[0x8ADB]}, and `ROM8[0x8817]` = {data[0x8817]}",
        f"`K` = `ROM8[0x8B76]` = {data[0x8B76]}",
        f"`ROM16[0x9242]` = {_u16(data, 0x9242)} to `0xFFFF57C4` and `ROM16[0x8D12]` = {_u16(data, 0x8D12)}",
        f"`ROM16[0x9098]` = {_u16(data, 0x9098)} while bit 5 is set",
        f"`ROM16[0x9096]` = {_u16(data, 0x9096)} while bit 6 is set",
        f"`ROM16[0x9094]` = {_u16(data, 0x9094)}",
        f"`ROM16[0x909C]` = {_u16(data, 0x909C)}",
        f"`ROM8[0x8429]` = {data[0x8429]}",
        f"`ROM8[0x8428] << 2` = {data[0x8428] << 2}",
        f"`ROM8[0x8AFA]` = {data[0x8AFA]}",
        f"`ROM8[0x8AFA] - ROM8[0x8AFD]` = {data[0x8AFA] - data[0x8AFD]}",
        f"`ROM8[0x8B17]` = {data[0x8B17]} and `ROM8[0x8B18]` = {data[0x8B18]} counts "
        f"({2 * data[0x8B17]} and {2 * data[0x8B18]} km/h)",
        f"`ROM8[0x8AFE]` = {data[0x8AFE]}",
        "decrements every nonzero byte of `0xFFFF472C..0xFFFF47EF` and every nonzero word of "
        "`0xFFFF4822..0xFFFF4867` on every tenth call",
        f"so each condition must persist for {data[0x8429]} or {data[0x8428] << 2} such steps",
        "A zero divisor stores `0x44E` at `0xFFFF9748` and returns 0.",
        "`FUN_00022562` is an arithmetic shift right by 6.",
        f"`{THIS_TEST}` executes the scaling paths, the division and block-copy helpers, and `FUN_0005A314` from the exact ROM bytes.",
    ):
        assert phrase in doc, phrase
    assert (ROOT / THIS_TEST).is_file()


def test_map_reference_constants_in_the_document() -> None:
    data = _rom()
    doc = _doc()
    assert _u32(data, 0x21A4C + 96 * 4) == 0x00043CDE and _u32(data, 0x21A4C + 97 * 4) == VACUUM
    assert "`FUN_00043CDE` (entry 96)" in doc and "`FUN_0005A314` (entry 97)" in doc
    for phrase in (
        f"filter order `ROM8[0x8B81]` = {data[0x8B81]}",
        f"`ROM16[0x8DF8]` = {_u16(data, 0x8DF8)}",
        f"`ROM8[0x89DA]` = {data[0x89DA]}",
        f"`ROM8[0x8813]` = {data[0x8813]} or `ROM8[0x83AA]` = {data[0x83AA]}",
        "curve `0x000135E8` = `" + ", ".join(str(b) for b in data[0x135E8:0x135F0]) + "`",
        f"`0x000132D6` = `{data[0x132D6]}..{data[0x132DD]}`",
        f"`0xFFFF10B6 * 4 > ROM8[0x877E]` = {data[0x877E]}",
        f"`ROM8[0x82EC]` = {data[0x82EC]}",
        f"`ROM8[0x8814]` = {data[0x8814]}",
        f"`[ROM16[0x9246], ROM16[0x9244]]` = `[{_u16(data, 0x9246)}, {_u16(data, 0x9244)}]`, which is 3.09..4.46 V",
    ):
        assert phrase in doc, phrase
    assert list(data[0x132D6:0x132DE]) == [32 * i for i in range(8)]


def test_range_monitor_window_in_the_document() -> None:
    data = _rom()
    doc = _doc()
    # P010A and P0555 bounds, lower then upper.
    for low, high in ((0x9296, 0x9294), (0x9290, 0x928E)):
        assert (_u16(data, low), _u16(data, high)) == (1024, 65024)
        assert f"outside `[ROM16[0x{low:04X}], ROM16[0x{high:04X}]]` = `[1024, 65024]`" in doc
    volts = [f"{float(Fraction(word, 64) * 5 / 1024):.2f}" for word in (1024, 65024)]
    assert f"so the window is {volts[0]}..{volts[1]} V of a 5 V scale." in doc


def test_scaled_words_have_no_did_binding() -> None:
    data = _rom()
    words = {_u32(data, address) for address in range(0, len(data), 4)}
    assert not {SCALED_REFERENCE, BOOSTER_SCALED, VACUUM_WORD} & words

    fragments = {}
    with ESM_2013_FRAGMENTS.open(encoding="utf-8") as source:
        for line in source:
            fragment = json.loads(line)
            if fragment["page_label"] == "EC-162":
                fragments[fragment["kind"]] = " ".join(fragment["text"].split())
    text = fragments["data_monitor"]
    assert "[VQ37VHR]" in text
    for item in ("ATOM PRES SEN", "BRAKE BST PRE SE"):
        assert re.search(re.escape(item) + r" mv \W+ This item is not efficient for V36 models\.", text), item
    assert "the VQ37VHR data monitor marks `ATOM PRES SEN` and `BRAKE BST PRE SE` not efficient for V36 models (EC-162)" in _doc()


def _pdf_page(path: Path, page: int) -> str:
    if shutil.which("pdftotext") is None:
        pytest.skip("pdftotext is not installed")
    result = subprocess.run(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(path), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout


def _bands(text: str) -> tuple[list[tuple[str, str, str]], list[tuple[str, str, str, str]]]:
    atmospheric = re.findall(r"^\s*(\d{3,4})\s+(\d\.\d)\s*[-\u2013]\s*(\d\.\d)\b", text, re.M)
    vacuum = re.findall(r"^\s*-(\d+(?:\.\d)?)kPa \(-(\d+)mmHg\)\s+(\d\.\d)\s*[-\u2013]\s*(\d\.\d)\b", text, re.M)
    return atmospheric, vacuum


def test_manual_sensor_characteristics_match_the_document() -> None:
    pages = {page: _pdf_page(ESM_2013_PDF, page) for page in (213, 214, 393, 394)}
    for page, title in ((213, "P010A MANIFOLD"), (214, "P010A MANIFOLD"), (393, "P0555 BRAKE"), (394, "P0555 BRAKE")):
        text = pages[page]
        assert title in text and "[VQ37VHR]" in text
        assert re.search(rf"EC-{page}\s+2013 G Sedan", text)

    map_atmospheric, _ = _bands(pages[213])
    _, map_vacuum = _bands(pages[214])
    booster_atmospheric, booster_vacuum = _bands(pages[394])
    assert "Voltage difference (V)" in pages[214] and "Voltage difference (V)" in pages[394]
    assert map_atmospheric == booster_atmospheric and len(map_atmospheric) == 6
    assert map_vacuum == booster_vacuum and len(map_vacuum) == 4

    doc = _doc()
    for pressure, low, high in map_atmospheric:
        assert re.search(rf"\| {pressure} hPa \| {re.escape(low)} - {re.escape(high)} V \| \d\.\d\d V \|", doc)
    for kpa, mmhg, low, high in map_vacuum:
        row = rf"\| -{re.escape(kpa)} kPa \(-{mmhg} mmHg\) \| {re.escape(low)} - {re.escape(high)} V \| \d\.\d\d V \|"
        assert re.search(row, doc)
    assert "the MAP sensor (EC-213, EC-214) and the brake booster pressure sensor (EC-393, EC-394)" in doc
