"""Minimal SH-2 integer interpreter for executable gates over exact stock images.

The interpreter executes the stock instructions of an image in place. It
implements only the instructions of the paths that the gates execute and
rejects any other opcode, any store into the image, and any branch or
PC-relative load in a delay slot. A read of a cell outside the image that no
seed or store has set fails, unless the machine is created with a value for
such cells.
"""

from __future__ import annotations

MASK = 0xFFFFFFFF
RETURN = 0x0FFFFFF0
STACK_TOP = 0x0F000000


def u16(data: bytes, address: int) -> int:
    return int.from_bytes(data[address : address + 2], "big")


def sext(value: int, bits: int) -> int:
    value &= (1 << bits) - 1
    return value - (1 << bits) if value >> (bits - 1) else value


def control_or_pc_relative(opcode: int) -> bool:
    top, group, low = opcode >> 12, (opcode >> 8) & 0xF, opcode & 0xFF
    if top in (0x9, 0xA, 0xB, 0xD):
        return True
    if top == 0x8 and group in (0x9, 0xB, 0xD, 0xF):
        return True
    if top == 0xC and group == 0x7:
        return True
    if top == 0x4 and low in (0x0B, 0x2B):
        return True
    return top == 0x0 and low in (0x03, 0x0B, 0x23, 0x2B)


class Sh2:
    """Minimal SH-2 integer interpreter over an exact image.

    `unset` is the byte that a cell outside the image reads before any seed or
    store sets it; None makes such a read fail.
    """

    def __init__(self, data: bytes, unset: int | None = None) -> None:
        self.data = data
        self.unset = unset
        self.ram: dict[int, int] = {}
        self.r = [0] * 16
        self.r[15] = STACK_TOP
        self.t = self.q = self.m = 0
        self.mach = self.macl = 0
        self.gbr = 0
        self.pr = RETURN
        self.loads: list[tuple[int, int, int]] = []
        self.stores: list[tuple[int, int, int, int]] = []

    def seed(self, address: int, values: bytes) -> None:
        for offset, value in enumerate(values):
            self.ram[address + offset] = value

    def seed_word(self, address: int, value: int) -> None:
        self.seed(address, value.to_bytes(2, "big"))

    def peek(self, address: int, size: int = 1) -> int:
        return int.from_bytes(bytes(self.ram[address + i] for i in range(size)), "big")

    def stored(self, address: int) -> list[tuple[int, int, int]]:
        """The (instruction, size, value) of every store that starts at `address`."""
        return [(pc, size, value) for pc, at, size, value in self.stores if at == address]

    def written(self) -> set[int]:
        return {at + offset for _, at, size, _ in self.stores for offset in range(size)}

    def loaded(self, addresses) -> list[tuple[int, int]]:
        """The (instruction, address) of every load of one of `addresses`."""
        wanted = set(addresses)
        return [(pc, at) for pc, at, _ in self.loads if at in wanted]

    def run(self, pc: int, stops: tuple[int, ...], limit: int = 20000) -> int:
        for _ in range(limit):
            if pc in stops:
                return pc
            assert pc != RETURN, f"returned before {[hex(stop) for stop in stops]}"
            pc = self._step(pc)
        raise AssertionError("step limit reached")

    def call(self, entry: int, limit: int = 20000) -> None:
        self.pr = RETURN
        self.run(entry, (RETURN,), limit)

    def _read(self, address: int, size: int, pc: int) -> int:
        address &= MASK
        value = 0
        for offset in range(size):
            at = address + offset
            if at < len(self.data):
                byte = self.data[at]
            elif at in self.ram:
                byte = self.ram[at]
            elif self.unset is not None:
                byte = self.unset
            else:
                raise AssertionError(f"{pc:#010x}: read of unset cell {at:#010x}")
            value = (value << 8) | byte
        self.loads.append((pc, address, size))
        return value

    def _write(self, address: int, size: int, value: int, pc: int) -> None:
        address &= MASK
        assert address >= len(self.data), f"{pc:#010x}: store into the image {address:#010x}"
        value &= (1 << (8 * size)) - 1
        for offset in range(size):
            self.ram[address + offset] = (value >> (8 * (size - 1 - offset))) & 0xFF
        self.stores.append((pc, address, size, value))

    def _step(self, pc: int) -> int:
        assert pc % 2 == 0 and pc < len(self.data), hex(pc)
        transfer = self._execute(pc, u16(self.data, pc))
        if transfer is None:
            return pc + 2
        delayed, target = transfer
        if delayed:
            slot = u16(self.data, pc + 2)
            assert not control_or_pc_relative(slot), f"delay slot {pc + 2:#010x}: {slot:04x}"
            assert self._execute(pc + 2, slot) is None
        return target

    def _div1(self, n: int, m: int) -> None:
        r = self.r
        old_q = self.q
        self.q = r[n] >> 31
        value = ((r[n] << 1) | self.t) & MASK
        before = value
        if old_q == self.m:
            value = (value - r[m]) & MASK
            carry = int(value > before)
        else:
            value = (value + r[m]) & MASK
            carry = int(value < before)
        self.q = self.q ^ carry if self.m == 0 else 1 - (self.q ^ carry)
        self.t = int(self.q == self.m)
        r[n] = value

    def _execute(self, pc: int, w: int):
        r = self.r
        top, n, m = w >> 12, (w >> 8) & 0xF, (w >> 4) & 0xF
        low, imm = w & 0xF, w & 0xFF

        def put(index: int, value: int) -> None:
            r[index] = value & MASK

        if top == 0x0:
            if w == 0x0009:
                return None
            if w == 0x000B:
                return True, self.pr
            if w == 0x0019:
                self.m = self.q = self.t = 0
                return None
            if imm == 0x12:
                put(n, self.gbr)
            elif imm == 0x29:
                put(n, self.t)
            elif imm == 0x0A:
                put(n, self.mach)
            elif imm == 0x1A:
                put(n, self.macl)
            elif low in (0x4, 0x5, 0x6):
                self._write(r[0] + r[n], 1 << (low - 0x4), r[m], pc)
            elif low == 0x7:
                self.macl = (r[n] * r[m]) & MASK
            elif low in (0xC, 0xD, 0xE):
                size = 1 << (low - 0xC)
                put(n, sext(self._read(r[0] + r[m], size, pc), 8 * size))
            else:
                raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        elif top == 0x1:
            self._write(r[n] + low * 4, 4, r[m], pc)
        elif top == 0x2:
            if low in (0x0, 0x1, 0x2):
                self._write(r[n], 1 << low, r[m], pc)
            elif low == 0x6:
                put(n, r[n] - 4)
                self._write(r[n], 4, r[m], pc)
            elif low == 0x7:
                self.q, self.m = r[n] >> 31, r[m] >> 31
                self.t = int(self.q != self.m)
            elif low == 0x8:
                self.t = int((r[n] & r[m]) == 0)
            elif low == 0x9:
                put(n, r[n] & r[m])
            elif low == 0xA:
                put(n, r[n] ^ r[m])
            elif low == 0xB:
                put(n, r[n] | r[m])
            elif low == 0xD:
                put(n, (r[n] >> 16) | (r[m] << 16))
            elif low == 0xE:
                self.macl = ((r[n] & 0xFFFF) * (r[m] & 0xFFFF)) & MASK
            else:
                raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        elif top == 0x3:
            x, y = r[n], r[m]
            if low == 0x0:
                self.t = int(x == y)
            elif low == 0x3:
                self.t = int(sext(x, 32) >= sext(y, 32))
            elif low == 0x4:
                self._div1(n, m)
            elif low == 0x6:
                self.t = int(x > y)
            elif low == 0x7:
                self.t = int(sext(x, 32) > sext(y, 32))
            elif low == 0xA:
                difference = (x - y) & MASK
                result = (difference - self.t) & MASK
                self.t = int(x < difference or difference < result)
                put(n, result)
            elif low == 0xC:
                put(n, x + y)
            elif low == 0xD:
                product = (sext(x, 32) * sext(y, 32)) & ((1 << 64) - 1)
                self.mach, self.macl = product >> 32, product & MASK
            elif low == 0xE:
                total = (x + y) & MASK
                result = (total + self.t) & MASK
                self.t = int(x > total or total > result)
                put(n, result)
            else:
                raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        elif top == 0x4:
            x = r[n]
            if imm == 0x00:
                self.t = x >> 31
                put(n, x << 1)
            elif imm in (0x02, 0x12, 0x22, 0x13):
                put(n, x - 4)
                value = {0x02: self.mach, 0x12: self.macl, 0x22: self.pr, 0x13: self.gbr}[imm]
                self._write(r[n], 4, value, pc)
            elif imm == 0x04:
                self.t = x >> 31
                put(n, (x << 1) | self.t)
            elif imm in (0x06, 0x16, 0x26, 0x17):
                value = self._read(x, 4, pc)
                put(n, x + 4)
                if imm == 0x06:
                    self.mach = value
                elif imm == 0x16:
                    self.macl = value
                elif imm == 0x26:
                    self.pr = value
                else:
                    self.gbr = value
            elif imm == 0x08:
                put(n, x << 2)
            elif imm == 0x09:
                put(n, x >> 2)
            elif imm == 0x0B:
                self.pr = pc + 4
                return True, x
            elif imm == 0x1E:
                self.gbr = x
            elif imm == 0x15:
                self.t = int(sext(x, 32) > 0)
            elif imm == 0x18:
                put(n, x << 8)
            elif imm == 0x19:
                put(n, x >> 8)
            elif imm == 0x21:
                self.t = x & 1
                put(n, sext(x, 32) >> 1)
            elif imm == 0x24:
                carry = self.t
                self.t = x >> 31
                put(n, (x << 1) | carry)
            elif imm == 0x25:
                carry = self.t
                self.t = x & 1
                put(n, (x >> 1) | (carry << 31))
            elif imm == 0x28:
                put(n, x << 16)
            elif imm == 0x29:
                put(n, x >> 16)
            elif imm == 0x2B:
                return True, x
            else:
                raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        elif top == 0x5:
            put(n, self._read(r[m] + low * 4, 4, pc))
        elif top == 0x6:
            x = r[m]
            if low in (0x0, 0x1, 0x2):
                size = 1 << low
                put(n, sext(self._read(x, size, pc), 8 * size))
            elif low == 0x3:
                put(n, x)
            elif low in (0x4, 0x6):
                size = 1 << (low - 0x4)
                value = sext(self._read(x, size, pc), 8 * size)
                if n != m:
                    put(m, x + size)
                put(n, value)
            elif low == 0x7:
                put(n, ~x)
            elif low == 0x9:
                put(n, (x << 16) | (x >> 16))
            elif low == 0xC:
                put(n, x & 0xFF)
            elif low == 0xD:
                put(n, x & 0xFFFF)
            elif low == 0xE:
                put(n, sext(x, 8))
            else:
                raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        elif top == 0x7:
            put(n, r[n] + sext(imm, 8))
        elif top == 0x8:
            if n in (0x0, 0x1):
                size = 1 << n
                self._write(r[m] + low * size, size, r[0], pc)
            elif n in (0x4, 0x5):
                size = 1 << (n - 0x4)
                put(0, sext(self._read(r[m] + low * size, size, pc), 8 * size))
            elif n == 0x8:
                self.t = int(r[0] == (sext(imm, 8) & MASK))
            elif n in (0x9, 0xB, 0xD, 0xF):
                taken = self.t == (1 if n in (0x9, 0xD) else 0)
                target = (pc + 4 + sext(imm, 8) * 2) & MASK
                if n in (0x9, 0xB):
                    return (False, target) if taken else None
                return True, target if taken else pc + 4
            else:
                raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        elif top == 0x9:
            put(n, sext(self._read(pc + 4 + imm * 2, 2, pc), 16))
        elif top == 0xA:
            return True, (pc + 4 + sext(w & 0xFFF, 12) * 2) & MASK
        elif top == 0xB:
            self.pr = pc + 4
            return True, (pc + 4 + sext(w & 0xFFF, 12) * 2) & MASK
        elif top == 0xC:
            if n in (0x0, 0x2):
                size = 1 << n
                self._write(self.gbr + imm * size, size, r[0], pc)
            elif n in (0x4, 0x6):
                size = 1 << (n - 0x4)
                put(0, sext(self._read(self.gbr + imm * size, size, pc), 8 * size))
            elif n == 0x8:
                self.t = int((r[0] & imm) == 0)
            elif n == 0x9:
                put(0, r[0] & imm)
            elif n == 0xA:
                put(0, r[0] ^ imm)
            elif n == 0xB:
                put(0, r[0] | imm)
            elif n == 0xC:
                self.t = int((self._read(self.gbr + r[0], 1, pc) & imm) == 0)
            elif n == 0xD:
                address = self.gbr + r[0]
                self._write(address, 1, self._read(address, 1, pc) & imm, pc)
            else:
                raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        elif top == 0xD:
            put(n, self._read((pc & ~3) + 4 + imm * 4, 4, pc))
        elif top == 0xE:
            put(n, sext(imm, 8))
        else:
            raise AssertionError(f"{pc:#010x}: opcode {w:04x}")
        return None
