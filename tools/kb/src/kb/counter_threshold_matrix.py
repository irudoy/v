"""Explicit lower-knot cell, elapsed-byte, word-counter and ratio-factor inputs."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x79686
KINDS = ('window',)
PATTERNS = ('stock', 'zero', 'one', 'two', 'nine', 'eleven', '127', '128', '254', '255', 'rising', 'falling')
AXES = ('stock', 'strict', 'raised')


def axis_bytes(image, kind):
    if kind == 'stock':
        return image[0x12FEE:0x12FF2], image[0x12FF2:0x12FF6]
    offset = int(kind == 'raised')
    if kind not in ('strict', 'raised'):
        raise ValueError('the counter-threshold input changes its explicit axis')
    raw = bytes(offset + index * 64 for index in range(4))
    return raw, raw


def boundaries(axis):
    return sorted({0, 255, *(value + delta for value in axis for delta in (-1, 0, 1) if 0 <= value + delta <= 255)})


def cases(declared, image):
    result = []

    def add(pattern, axis, row=44, word=92, elapsed=7, counter=9):
        index = len(result)
        seed = row + word + elapsed + counter
        result.append(dict(index=index, kind='window', entry=ENTRY, pattern=pattern, axis=axis,
            row=row, word=word, elapsed=elapsed, counter=counter, variant=seed % 4,
            sr=(seed & 1) | ((seed & 15) << 4) | ((seed & 3) << 8)))

    for axis in AXES:
        rows, columns = axis_bytes(image, axis)
        coordinates = {(row, columns[1]) for row in boundaries(rows)}
        coordinates.update((rows[1], column) for column in boundaries(columns))
        coordinates.update((row, column) for row in rows for column in columns)
        for pattern in PATTERNS:
            for row, column in sorted(coordinates):
                add(pattern, axis, row, column * 4)
    for pattern in ('zero', 'one', 'two', 'nine', 'eleven', '127', '128', '254', '255'):
        for elapsed in (0, 1, 2, 9, 10, 127, 128, 255):
            add(pattern, 'strict', elapsed=elapsed)
        for counter in (0, 2, 3, 6, 7, 9, 10, 13, 14, 6501, 6502, 65534, 65535):
            add(pattern, 'strict', counter=counter)
    for word in (0, 3, 4, 1019, 1020, 1021, 65535):
        add('one', 'strict', word=word)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[6], registers[11], registers[12] = min(case['word'] >> 2, 255), RAM_BASE + 0x28F8, 0
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0xAAFA, 16), (0xAAEA, 16), (0x12FEE, 4), (0x12FF2, 4))


def calibrations(declared, image, case):
    result = {at: image[at:at + size] for at, size in calibration_spans(declared)}
    result[0x12FEE], result[0x12FF2] = axis_bytes(image, case['axis'])
    pattern = case['pattern']
    if pattern == 'stock':
        return result
    if pattern in ('zero', 'one', 'two', 'nine', 'eleven', '127', '128', '254', '255'):
        value = {'zero': 0, 'one': 10, 'two': 20, 'nine': 9, 'eleven': 11,
                 '127': 127, '128': 128, '254': 254, '255': 255}[pattern]
        raw = bytes([value]) * 16
    elif pattern in ('rising', 'falling'):
        raw = bytes(index * 17 for index in range(16))
        if pattern == 'falling':
            raw = bytes(255 - value for value in raw)
    else:
        raise ValueError('the counter-threshold calibration changes its explicit raw-byte pattern')
    result[0xAAFA], result[0xAAEA] = raw, bytes([3]) * 16
    return result


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x11AE] = case['row']
    ram[0x40C6:0x40C8] = case['word'].to_bytes(2, 'big')
    ram[0x3446:0x3448] = case['counter'].to_bytes(2, 'big')
    ram[0x3448], ram[0x3449], ram[0x351C] = case['elapsed'], 0xB4, 0xA3
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the counter-threshold original changes an explicit local fifth, row, elapsed or counter input')
