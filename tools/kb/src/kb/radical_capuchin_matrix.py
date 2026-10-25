"""Explicit byte coordinate, threshold calibration and independent word timer."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x6160C
KINDS = ('window',)
PATTERNS = ('stock', 'zero', 'one', 'two', 'maximum', 'rising', 'falling')
AXES = ('stock', 'strict', 'raised')


def cases(declared, image):
    result = []

    def add(pattern, axis, coordinate, timer):
        seed = coordinate + timer
        result.append(dict(index=len(result), kind='window', entry=ENTRY, pattern=pattern, axis=axis,
                           coordinate=coordinate, timer=timer, variant=seed % 4,
                           sr=(seed & 1) | ((seed & 15) << 4) | ((seed & 3) << 8)))

    for axis in AXES:
        knots = image[0x12FDE:0x12FE6] if axis == 'stock' else bytes(
            index * 32 + int(axis == 'raised') for index in range(8))
        coordinates = {0, 1, 254, 255, *(value + delta for value in knots for delta in (-1, 0, 1)
                                       if 0 <= value + delta <= 255)}
        for pattern in PATTERNS:
            for coordinate in sorted(coordinates):
                add(pattern, axis, coordinate, 10)
    for pattern in PATTERNS:
        for timer in (0, 1, 9, 10, 11, 19, 20, 21, 2549, 2550, 2559, 2560, 32767, 32768, 65535):
            add(pattern, 'strict', 112, timer)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    return (*registers, RAM_BASE + 0x8C90, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x12362, 9), (0x12FDE, 8))


def calibrations(declared, image, case):
    pattern = case['pattern']
    if pattern == 'stock':
        raw = image[0x12362:0x1236A]
    elif pattern in ('zero', 'one', 'two', 'maximum'):
        raw = bytes([dict(zero=0, one=1, two=2, maximum=255)[pattern]]) * 8
    elif pattern in ('rising', 'falling'):
        raw = bytes(index * 32 for index in range(8))
        if pattern == 'falling':
            raw = bytes(255 - value for value in raw)
    else:
        raise ValueError('the threshold changes its explicit curve pattern')
    axis = image[0x12FDE:0x12FE6]
    if case['axis'] in ('strict', 'raised'):
        axis = bytes(index * 32 + int(case['axis'] == 'raised') for index in range(8))
    elif case['axis'] != 'stock':
        raise ValueError('the threshold changes its explicit axis pattern')
    return {0x12362: raw + image[0x1236A:0x1236B], 0x12FDE: axis}


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x2773] = case['coordinate']
    ram[0x8C90:0x8C92] = case['timer'].to_bytes(2, 'big')
    ram[0x8CB4:0x8CB8] = bytes.fromhex('d3e4f506')
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the threshold comparison changes its complete explicit bounded inputs')
