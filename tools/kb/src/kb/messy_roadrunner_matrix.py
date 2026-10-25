"""Explicit word coordinates and base quantities for a bounded byte correction."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x6AE78
KINDS = ('window',)
PATTERNS = ('stock', 'zero', 'one', 'two', 'maximum', 'rising', 'falling')
AXES = ('stock', 'strict', 'raised')


def cases(declared, image):
    result = []

    def add(pattern, axis, word, base):
        seed = word + base
        result.append(dict(index=len(result), kind='window', entry=ENTRY, pattern=pattern, axis=axis,
                           word=word, base=base, variant=seed % 4,
                           sr=(seed & 1) | ((seed & 15) << 4) | ((seed & 3) << 8)))

    for axis in AXES:
        knots = image[0x11AEF:0x11AF7] if axis == 'stock' else bytes(
            index * 32 + int(axis == 'raised') for index in range(8))
        coordinates = {0, 1, 254, 255, *(value + delta for value in knots for delta in (-1, 0, 1)
                                       if 0 <= value + delta <= 255)}
        for pattern in PATTERNS:
            for coordinate in sorted(coordinates):
                add(pattern, axis, coordinate << 8, 17)
    for pattern in PATTERNS:
        for base in (0, 1, 0x7FBE, 0x7FFF, 0x803E, 0x803F, 0x8040, 0x8041, 0x8042, 65534, 65535):
            add(pattern, 'strict', 0x7000, base)
        for word in (0, 1, 255, 256, 257, 32767, 32768, 65534, 65535):
            add(pattern, 'strict', word, 17)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[2], registers[8], registers[11] = case['word'], RAM_BASE + 0x8E08, 0x21BBC
    return (*registers, RAM_BASE + 0x8E34, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x11F3A, 9), (0x11AEF, 8))


def calibrations(declared, image, case):
    pattern = case['pattern']
    if pattern == 'stock':
        raw = image[0x11F3A:0x11F42]
    elif pattern in ('zero', 'one', 'two', 'maximum'):
        raw = bytes([dict(zero=0, one=1, two=2, maximum=255)[pattern]]) * 8
    elif pattern in ('rising', 'falling'):
        raw = bytes(index * 32 for index in range(8))
        if pattern == 'falling':
            raw = bytes(255 - value for value in raw)
    else:
        raise ValueError('the byte correction changes its explicit curve pattern')
    axis = image[0x11AEF:0x11AF7]
    if case['axis'] in ('strict', 'raised'):
        axis = bytes(index * 32 + int(case['axis'] == 'raised') for index in range(8))
    elif case['axis'] != 'stock':
        raise ValueError('the byte correction changes its explicit axis pattern')
    return {0x11F3A: raw + image[0x11F42:0x11F43], 0x11AEF: axis}


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x8E08:0x8E0A] = case['base'].to_bytes(2, 'big')
    ram[0x8EC0:0x8EC4] = bytes.fromhex('d3e4f506')
    ram[0x8FDE:0x8FE0] = bytes.fromhex('a7b8')
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the byte correction changes its complete explicit bounded inputs')
