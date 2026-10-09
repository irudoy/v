"""Independent raw memory equations for the complete feedback call.

The functions use arithmetic, table interpolation, and state equations. They
do not decode or interpret SH instructions and do not assign physical units.
This draft is not an executable acceptance receipt.
"""
from fractions import Fraction

U16 = 65535
signed16 = lambda value: value - 65536 if value & 32768 else value
increment = lambda value: min(U16, value + 1)


class Memory:
    def __init__(self, ram, rom):
        assert len(ram) == 65536
        self.ram = bytearray(ram)
        self.rom = bytes(rom)

    def read(self, address, width=1, signed=False):
        if address >= 0xffff0000:
            data = self.ram[address - 0xffff0000:address - 0xffff0000 + width]
        else:
            data = self.rom[address:address + width]
        assert len(data) == width
        return int.from_bytes(data, 'big', signed=signed)

    def put(self, address, value, width=1):
        assert 0xffff0000 <= address and address + width <= 0x100000000
        self.ram[address - 0xffff0000:address - 0xffff0000 + width] = (
            value & ((1 << (8 * width)) - 1)).to_bytes(width, 'big')

    def b(self, address):
        return self.read(address)

    def w(self, address):
        return self.read(address, 2)

    def l(self, address):
        return self.read(address, 4)


def byte_curve(memory, table, axis, coordinate, count):
    """Unsigned byte curve with the stock directional integer rounding."""
    x = [memory.b(axis + i) for i in range(count)]
    y = [memory.b(table + i) for i in range(count)]
    index = max((i for i in range(count) if coordinate >= x[i]), default=0)
    fraction = (0 if coordinate <= x[0] or index == count - 1 or coordinate == x[index]
                else int(Fraction(65536 * (coordinate - x[index]), x[index + 1] - x[index])))
    change = abs(y[index + 1] - y[index]) * fraction // 65536 if index < count - 1 else 0
    return y[index] + change if index == count - 1 or y[index + 1] >= y[index] else y[index] - change


def transition(memory):
    """Whole two-bank transition detector 0005ca8c after packet binding."""
    base = 0xffff88b4
    control, factor = memory.b(0xffff89d8), memory.b(0xffff89d9)
    words = [memory.w(0xffff89cc + 2 * bank) for bank in range(2)]
    trigger = (control == 0 and memory.b(base + 0x19) != 0
               or words[1] == 0x4000 and memory.w(base) > 0x4000
               or words[0] == 0 and memory.w(base + 2) != 0)
    threshold = memory.b(0x8822) * factor
    for bank in range(2):
        flag, count = memory.b(base + 0xc + bank), memory.w(base + 4 + 2 * bank)
        if flag != 1 and not trigger:
            memory.put(base + 0xc + bank, 0)
            memory.put(base + 4 + 2 * bank, 0, 2)
            continue
        if flag == 0:
            memory.put(base + 0xc + bank, 1)
        nominal = memory.w(0xffff89d0 + 2 * bank)
        observed = memory.w(0xffff89d4 + 2 * bank)
        low = (nominal - memory.w(0x92ee)) & U16
        high = (nominal + memory.w(0x92f0)) & U16
        if count > threshold or low <= observed <= high:
            memory.put(base + 0xc + bank, 0)
            memory.put(base + 4 + 2 * bank, 0, 2)
        else:
            memory.put(base + 4 + 2 * bank, increment(count), 2)
    memory.put(base + 0x19, control)
    memory.put(base, words[1], 2)
    memory.put(base + 2, words[0], 2)


def backup_state(memory, p1, p2, p3, p4, p5, factor):
    """State/counter equations of 0005d86e with its four output bindings."""
    base = 0xffff88cc
    if memory.b(base + 0x20) & 0x40 == 0:
        memory.put(base + 0x20, memory.b(base + 0x20) | 0x40)
    else:
        admitted = not (p3 < 2 and (p1 < memory.b(0x8cfa)
            or p4 < memory.b(0x8dbf) or p5 < memory.b(0x8801) or p2 != 1))
        if not admitted:
            if memory.b(base) == 1:
                value = memory.b(0x87ff if memory.b(0xffff88e8) < memory.b(0x8da7) else 0x8800)
                memory.put(0xffff2be6, value << 8, 2)
            else:
                memory.put(base + 0x18, 0, 4)
                memory.put(0xffff3364, 0, 2)
        else:
            if memory.l(base + 0x18) == 0:
                memory.put(base + 0x18, 1, 4)
                memory.put(0xffff88e8, p4)
            count = memory.w(0xffff3364)
            if count < ((factor * memory.b(0x839a)) & U16):
                memory.put(0xffff3364, count + 1, 2)
            else:
                memory.put(base, 1)
                value = memory.b(0x87ff if memory.b(0xffff88e8) < memory.b(0x8da7) else 0x8800)
                memory.put(0xffff2be6, value << 8, 2)
        leaving = (memory.b(base) == 1 and p3 < 2 and (p1 < memory.b(0x8cfa)
            or p4 < memory.b(0x8dbe) or p5 < memory.b(0x8802) or p2 == 0))
        if leaving:
            count = memory.w(0xffff3366)
            if count < ((factor * memory.b(0x8399)) & U16):
                memory.put(0xffff3366, count + 1, 2)
                memory.put(0xffff2be6, 0x6400, 2)
            else:
                memory.put(base, 0)
        else:
            memory.put(0xffff3366, 0, 2)
    memory.put(0xffff8964, memory.b(base))
    memory.put(0xffff891c, memory.w(0xffff3364), 2)
    memory.put(0xffff8920, memory.w(0xffff2be6), 2)
    memory.put(0xffff891e, memory.w(0xffff3366), 2)


def active_state(memory, p1, p2, banks, p4, p5):
    """Latch, elapsed count, and delayed active-bank equations of 0005d6ae."""
    base = 0xffff88bc
    if p1 == 0 and memory.b(base + 0x12) == 1:
        memory.put(base + 6, 1)
    elif p4 <= 2 and memory.w(base) >= 3:
        memory.put(base + 6, 0)
    memory.put(base + 0x12, p1)
    memory.put(base, p4, 2)
    count = increment(memory.w(base + 0x38)) if memory.b(base + 6) else 0
    memory.put(0xffff34e2, count, 2)
    if memory.b(base + 0x30) & 0x80 == 0:
        memory.put(base + 0x30, memory.b(base + 0x30) | 0x80)
    else:
        criterion = byte_curve(memory, 0x12312, 0x12f9e, p5, 16)
        old_pair = bool(memory.l(base + 0x14) and memory.l(base + 0x1c))
        for bank in range(2):
            memory.put(base + 8 + 4 * bank, int(old_pair and banks[bank] == 1), 4)
        memory.put(base + 0x18, 2)
        memory.put(base + 0x14, int(100 * criterion < count), 4)
        memory.put(base + 0x1c, int(bool(memory.l(base + 0x20) or memory.l(base + 0x24))), 4)
        threshold = memory.b(0x8392 if p5 < memory.b(0x8730) else 0x8cd4)
        memory.put(base + 0x20, int(threshold <= p2), 4)
        divided_threshold = 232 * memory.b(0x8475) // 10
        memory.put(base + 0x24, int(count >= divided_threshold and memory.b(0x8d14) <= p2), 4)
    for bank in range(2):
        memory.put(0xffff895c + 4 * bank, memory.l(base + 8 + 4 * bank), 4)
    memory.put(base + 0x38, count, 2)


def neutral_ramp(memory, p1, p2, p3, p4, p5, p6, p7, banks, step, factor):
    """Counter, activation, and two-bank neutral ramp of 0005da24."""
    base = 0xffff88f4
    memory.put(base + 0x98, int(p2 != 0x4000), 4)
    memory.put(base + 0x9c, int(p1 != 0), 4)
    admitted = (p3 != 0 and p4 == 0 and p5 == 0
        and memory.b(0x8d7d) <= p6 < memory.b(0x8d7c)
        and memory.b(0x88db) <= p7 < memory.b(0x88da))
    count = increment(memory.w(base + 2)) if admitted else 0
    memory.put(0xffff3410, count, 2)
    memory.put(base + 0x94, int(factor * memory.b(0x8a51) < count), 4)
    flags = [int(bool(memory.l(base + 0x9c) or memory.l(base + 0x98)
        or memory.l(base + 0x94) or memory.b(0x8659) or bank)) for bank in banks]
    for bank, flag in enumerate(flags):
        memory.put(base + 0x90 + bank, flag)
        memory.put(0xffff8965 + bank, flag)
    if any(flags):
        for bank in range(2):
            value = memory.w(0xffff40b0 + 2 * bank)
            scratch = base + (0x7c + 4 * bank if value < 0x6400 else 0x84 + 4 * bank)
            memory.put(scratch, value + step if value < 0x6400 else value - step, 4)
            output = (memory.w(0x23744 + 2 * bank) if step == 255
                else min(0x6400, value + step) if value < 0x6400 else max(0x6400, value - step))
            memory.put(base + 0x8c + 2 * bank, output, 2)
    for bank in range(2):
        memory.put(0xffff8922 + 2 * bank, memory.w(base + 0x8c + 2 * bank), 2)
    memory.put(base + 2, count, 2)


def elapsed_state(memory, control, level, common, input_mask, inhibit_mask):
    """Elapsed counts, hold selection, and edge filtering of 0005df48."""
    base = 0xffff88f8
    negative = [int(memory.read(0xffff2bd6 + 2 * bank, 2, signed=True) < 0) for bank in range(2)]
    high_level = int(memory.b(0x8db9) <= level)
    memory.put(base + 0xd0, high_level, 4)
    for bank in range(2):
        memory.put(base + 0xc8 + 4 * bank, negative[bank], 4)
        enabled = memory.b(0xffff8904 + bank) != 0
        count = increment(memory.w(base + 8 + 2 * bank)) if enabled else 0
        memory.put(0xffff3132 + 2 * bank, count, 2)
    candidates = []
    for bank in range(2):
        byte = memory.w(0xffff2898 + 2 * bank) >> 8
        hold = bool(control and high_level and (byte >= memory.b(0x82f1) or byte <= memory.b(0x82f0)))
        candidate = memory.w(base + 4 + 2 * bank) if hold else increment(memory.w(base + 2 * bank))
        candidates.append(candidate)
        memory.put(base + 0xc2 + 2 * bank, candidate, 2)
    outputs = []
    for bank in range(2):
        count = memory.w(0xffff3132 + 2 * bank)
        reject = bool(input_mask[bank] or common or memory.b(base + 0x10 + bank)
            or count // 10 >= memory.b(0x8b7f) or inhibit_mask[bank]
            or negative[bank] and memory.b(base + 0x12 + bank) == 0)
        output = 0 if reject else candidates[bank]
        outputs.append(output)
        memory.put(0xffff40c0 + 2 * bank, output, 2)
    for bank in range(2):
        memory.put(base + 8 + 2 * bank, memory.w(0xffff3132 + 2 * bank), 2)
        memory.put(base + 0x12 + bank, negative[bank])
        memory.put(base + 4 + 2 * bank, candidates[bank], 2)
        memory.put(base + 2 * bank, outputs[bank], 2)
        memory.put(base + 0x10 + bank, memory.b(0xffff894c + bank))


def late_ramp(memory, input_mask, step):
    """Per-bank delayed neutral ramp and edge flags of 0005ddc4."""
    base = 0xffff8904
    flags = [int(memory.w(0xffff40c0 + 2 * bank) // 10 >= memory.b(0x8876)) for bank in range(2)]
    for bank in range(2):
        memory.put(base + 0xb4 + bank, flags[bank])
        memory.put(base + 0x9c + bank, flags[bank])
    for bank in (1, 0):
        if flags[bank] == 0:
            continue
        value = memory.w(0xffff40b0 + 2 * bank)
        scratch = base + (0xa0 if bank == 1 else 0xa8) + (0 if value < 0x6400 else 4)
        memory.put(scratch, value + step if value < 0x6400 else value - step, 4)
        output = (0x6400 if step == 255 else min(0x6400, value + step)
                  if value < 0x6400 else max(0x6400, value - step))
        memory.put(base + (0xb0 if bank == 1 else 0xb2), output, 2)
    memory.put(base + 0x98, memory.w(base + 0xb2), 2)
    memory.put(base + 0x9a, memory.w(base + 0xb0), 2)
    for bank in range(2):
        selected = memory.b(0x23748 + bank) if flags[bank] and memory.b(base + 2 + bank) == 0 else input_mask[bank]
        memory.put(base + 0x9e + bank, selected)
        memory.put(base + 2 + bank, flags[bank])


def combined_elapsed_ramp(memory, control, level, common, input_mask, inhibit_mask, ramp_mask, step):
    """Real helper call and output binding order of 0005dcfa."""
    base = 0xffff8904
    elapsed_state(memory, control, level, common, input_mask, inhibit_mask)
    for bank in range(2):
        memory.put(0xffff892e + 2 * bank, memory.w(0xffff40c0 + 2 * bank), 2)
    late_ramp(memory, ramp_mask, step)
    for bank in range(2):
        memory.put(0xffff8926 + 2 * bank, memory.w(base + 0x98 + 2 * bank), 2)
        memory.put(0xffff8969 + bank, memory.b(base + 0x9c + bank))
        memory.put(0xffff896b + bank, memory.b(base + 0x9e + bank))
        memory.put(0xffff892a + 2 * bank, memory.w(0xffff3132 + 2 * bank), 2)
        memory.put(base + bank, memory.b(base + 0x9c + bank))


def evaluate(ram, rom):
    """Whole 0005cbec RAM result from independent state equations."""
    memory = Memory(ram, rom)
    base = 0xffff88b0
    pair = lambda offset: [memory.b(base + offset + bank) for bank in range(2)]
    curve = byte_curve(memory, 0x23752, 0x2374a, (memory.w(0xffff11bc) >> 1) & 255, 8)
    memory.put(base + 0x97, curve)
    for address, value, width in ((0xffff89d8, memory.b(0xffff14c1), 1),
        (0xffff89d9, curve, 1), (0xffff89cc, memory.w(0xffff15da), 2),
        (0xffff89ce, memory.w(0xffff22e8), 2)):
        memory.put(address, value, width)
    for bank in range(2):
        memory.put(0xffff89d0 + 2 * bank, memory.w(0xffff28b8 + 2 * bank), 2)
        memory.put(0xffff89d4 + 2 * bank, memory.w(0xffff29e2 + 2 * bank), 2)
    transition(memory)
    for bank in range(2):
        memory.put(base + 0xa8 + bank, memory.b(0xffff88c0 + bank))
    masks = ((0x82, 0xffff2c01), (0x84, 0xffff2bfe), (0x87, 0xffff10c8),
             (0x8b, 0xffff3082), (0x8d, 0xffff2b46), (0x93, 0xffff328a))
    for offset, address in masks:
        for bank in range(2):
            memory.put(base + offset + bank, int(bool(memory.b(address) & (1 << bank))))
    for bank in range(2):
        memory.put(base + 0x89 + bank, int(bool(memory.b(0xffff24a1) & (1 << bank) & 1)))
    common = ((0x86, 0xffff244f, 4), (0x8f, 0xffff41a5, 0x20),
        (0x90, 0xffff41be, 0x40), (0x91, 0xffff41d0, 1), (0x92, 0xffff24d2, 1),
        (0x95, 0xffff2458, 0x20), (0x96, 0xffff4184, 0x40))
    for offset, address, mask in common:
        memory.put(base + offset, int(bool(memory.b(address) & mask)))
    for bank in range(2):
        memory.put(0xffff89da + bank, memory.b(base + 0x8d + bank))
        memory.put(0xffff89dc + bank, memory.b(base + 0x93 + bank))
    either = int(bool(memory.b(base + 0x90) or memory.b(base + 0x91)))
    threshold = int(bool(memory.b(base + 0x92) and memory.w(0xffff1024) > memory.w(0xffff196a)))
    memory.put(0xffff8998, either, 4)
    memory.put(0xffff8994, threshold, 4)
    for bank in range(2):
        flag = int(bool(memory.b(base + 0x89 + bank) or memory.b(0x85f4) or memory.b(0x8658)
            or memory.b(base + 0x82 + bank) or memory.b(0xffff22e0)
            or memory.b(base + 0x8f) or memory.b(0xffff289c) or either or threshold))
        memory.put(base + 0xb7 + bank, flag)
    backup_state(memory, memory.b(0xffff1071), memory.b(base + 0x95), memory.b(0xffff14c1),
        memory.b(0xffff110e), memory.w(0xffff11bc), curve)
    active_state(memory, memory.b(base + 0x96), memory.b(0xffff1071), pair(0x87),
        memory.w(0xffff11bc), memory.b(0xffff106e))
    neutral_ramp(memory, memory.w(0xffff15da), memory.w(0xffff22e8), memory.b(base + 0x95),
        memory.b(base + 0x96), memory.b(base + 0x86), memory.b(0xffff110e), memory.w(0xffff11bc),
        pair(0x84), memory.b(0x86f8), curve)
    active = [memory.l(base + 0xac + 4 * bank) for bank in range(2)]
    for bank in range(2):
        count = increment(memory.w(base + 0x40 + 2 * bank)) if active[bank] else 0
        memory.put(base + 0x60 + 2 * bank, count, 2)
        product = 0x3333 * count
        if bank == 1:
            memory.put(base + 0x5c, product, 4)
        memory.put(0xffff161b + bank, 255 if product > 0x1fe0000 else (product >> 17) & 255)
    if memory.b(base + 0x3c) & 0x20 == 0:
        memory.put(base + 0x3c, memory.b(base + 0x3c) | 0x20)
    else:
        for bank in range(2):
            if active[bank] == 0:
                memory.put(base + 0xe + bank, 0)
            elif (memory.b(0x8823) <= memory.b(0xffff161b + bank)
                  or memory.w(0x8f9a) <= memory.w(0xffff322c + 2 * bank)):
                memory.put(base + 0xe + bank, 1)
        memory.put(base + 0x39, 2)
    for bank in range(2):
        admitted = (memory.b(base + 0xe + bank) != 0 and memory.b(base + 0xb4) == 0
            and memory.b(base + 0xb7 + bank) == 0 and memory.b(base + 0xb5 + bank) == 0
            and memory.b(base + 0xa8 + bank) == 0)
        memory.put(base + 0x9c + bank, int(not admitted))
    combined_elapsed_ramp(memory, memory.b(base + 0x95), memory.b(0xffff110e), memory.b(0xffff2f0a),
        pair(0x93), pair(0x8d), pair(0x8b), memory.b(0x86f8))
    for bank in range(2):
        gate = int(bool(memory.b(base + 0x9c + bank) or memory.b(base + 0xb9 + bank)))
        memory.put(base + 0xa0 + 4 * bank, gate, 4)
        memory.put(base + 0x9e + bank, int(not (memory.b(base + 0x8d + bank)
            or memory.b(base + 0x93 + bank) or gate)))
        memory.put(base + 0x9a + bank, int(gate == 0))

    def publish(address, flags):
        value = memory.b(address)
        for bank, flag in enumerate(flags):
            value = value | (1 << bank) if flag else value & ~(1 << bank)
        memory.put(address, value)

    for address, offset in ((0xffff1221, 0x9a), (0xffff2b67, 0xb5), (0xffff3377, 0xb7),
        (0xffff2b66, 0x9c), (0xffff22e3, 0xb9), (0xffff230e, 0xe), (0xffff3082, 0xbb)):
        publish(address, pair(offset))
    if memory.w(base + 0x3c) & 0x1000 == 0:
        memory.put(base + 0x3c, memory.b(base + 0x3c) | 0x10)
    else:
        backup = memory.w(base + 0x70)
        for bank in range(2):
            if memory.b(base + 0xe + bank) != 1:
                value = 0x6400
            elif memory.b(0xffff89da + bank):
                value = memory.w(0xffff2a1e + 2 * bank)
            elif memory.b(0xffff89dc + bank):
                value = memory.w(0xffff1628 + 2 * bank)
            elif memory.b(base + 0xa8 + bank):
                value = 0x6400
            elif memory.b(base + 0xb4):
                value = backup
            elif memory.b(base + 0xb7 + bank):
                value = 0x6400
            elif memory.b(base + 0xb5 + bank):
                value = memory.w(base + 0x72 + 2 * bank)
            elif memory.b(base + 0xb9 + bank):
                value = memory.w(base + 0x76 + 2 * bank)
            else:
                value = memory.w(0xffff2898 + 2 * bank)
            memory.put(base + 2 * bank, value, 2)
        memory.put(base + 0x3a, 2)
    for bank in range(2):
        value = memory.w(base + 2 * bank)
        upper = min(memory.w(0x8fc6), value)
        result = max(memory.w(0x8fc4), upper)
        memory.put(base + 0x64 + 2 * bank, upper, 2)
        memory.put(base + 0x68 + 2 * bank, result, 2)
        memory.put(base + 0x98 + bank, int(result != value))
    publish(0xffff12ed, pair(0xa8))
    publish(0xffff161a, active)
    publish(0xffff22e1, pair(0x9e))
    publish(0xffff32ff, pair(0x98))
    for bank in range(2):
        memory.put(0xffff40ac + 2 * bank, memory.w(base + 0x68 + 2 * bank), 2)
        memory.put(base + 0x40 + 2 * bank, memory.w(base + 0x60 + 2 * bank), 2)
    return bytes(memory.ram)
