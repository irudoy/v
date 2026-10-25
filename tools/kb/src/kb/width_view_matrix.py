"""Explicit bounded inputs for byte diagnostics and wider working-state accesses."""

from kb import test_contract

PATTERNS = (0x0000, 0xFFFF, 0x80FF, 0x7F00, 0x1234, 0xA55A)
SELECTORS = (0, 1, 2, 6, 127, 128, 254, 255)
MASK = 0xFFFFFFFF
RAM_BASE = 0x01000000
RAM_SIZE = 65536


def cases(window):
    patterns = (*PATTERNS, *(1 << bit for bit in range(16)))
    selectors = SELECTORS if window['key'].startswith('2142-') else (1,)
    if window['key'] == '2142-byte-counter':
        patterns,selectors = (0x1234,0x80FF),tuple(range(256))
    result = []
    for entry in window['entries']:
        for selector in selectors:
            for pattern in patterns:
                index = len(result)
                result.append(dict(index=index, entry=entry, selector=selector, pattern=pattern,
                    variant=index % 6, sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))
    return tuple(result)


def entry(window, case):
    registers = [(0x1728394A + register * 0x110203 + case['variant'] * 0x1000101) & MASK
                 for register in range(15)]
    if window['key'] == '2142-indexed-store':
        registers[14] = case['selector']
        registers[0] = 0xB6C70000 | case['pattern']
    if window['key'] == '4544-write-b':
        registers[13] = RAM_BASE + 0x55BC
    if case['entry'] == 0x3CEBE:
        registers[0] = 2 if case['variant'] & 1 else 0
    if window['key'] == '2142-byte-counter':
        registers[0] = 0x40 if case['variant'] & 1 else 0
    stack8 = (case['pattern'] << 16) | (case['pattern'] ^ 0xFFFF)
    return (*registers, RAM_BASE + (window['gbr'] & 65535),
            0x13579BDF, 0x2468ACE0, case['sr'], stack8)


def memory(case):
    value = (0x5D + case['variant'] * 37) & 255
    ram = bytearray([value]) * RAM_SIZE
    pattern = case['pattern']
    for address in (0x118A, 0x16D2, 0x4544, 0x5606, 0x2142 + case['selector'] * 2):
        ram[address:address + 2] = pattern.to_bytes(2, 'big')
    metric = 0x21D4 + 4 * case['selector']
    ram[metric:metric + 4] = ((pattern << 16) | (pattern ^ 0xFFFF)).to_bytes(4, 'big')
    ram[0x11DE] = ram[0x2142] = ram[0x2143] = case['selector']
    return bytes(ram)


def require_input(window, case, observed):
    if (observed['entry'] != case['entry']
            or not test_contract.exact(observed['context'], entry(window, case))
            or observed['memory_before'] != (memory(case),)):
        raise ValueError('the width-view observation changes its exact declared entry, registers, stack, selector or RAM')


def decode_rle(value):
    """Lossless complete RAM, with one canonical representation per byte string."""
    if type(value) is not str or not value:
        raise ValueError('the width-view memory requires a complete canonical RLE string')
    output = bytearray()
    previous = None
    for item in value.split(','):
        count, separator, encoded = item.partition(':')
        if (not separator or not count.isascii() or not count.isdecimal()
                or str(int(count)) != count or not 1 <= int(count) <= RAM_SIZE
                or len(encoded) != 2 or any(char not in '0123456789abcdef' for char in encoded)):
            raise ValueError('the width-view memory has a noncanonical run')
        byte = int(encoded, 16)
        if previous == byte or len(output) + int(count) > RAM_SIZE:
            raise ValueError('the width-view memory repeats a run or exceeds its complete RAM span')
        output.extend(bytes([byte]) * int(count))
        previous = byte
    if len(output) != RAM_SIZE:
        raise ValueError('the width-view memory omits part of its complete RAM span')
    return bytes(output)
