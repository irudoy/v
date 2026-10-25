"""Explicit curve-difference entry, byte input and independent table variations."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x44A58
KINDS = ('window',)
PATTERNS = ('stock', 'a-low', 'a-high', 'b-low', 'b-high', 'equal', 'bypass', 'maximum', 'rising', 'falling')


def cases(declared, image):
    result = []
    for pattern in PATTERNS:
        for coordinate in (0, 15, 16, 112, 127, 239, 240, 255):
            for observed in (0, 64, 100, 255):
                index = len(result)
                result.append(dict(index=index, kind='window', entry=ENTRY, pattern=pattern,
                    coordinate=coordinate, observed=observed, variant=index % 4,
                    sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[10], registers[11], registers[14] = RAM_BASE + 0x128C, RAM_BASE + 0x106A, 0x26388
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x12738, 16), (0x12748, 16), (0x12930, 16))


def calibrations(declared, image, case):
    pattern = case['pattern']
    if pattern == 'stock':
        return {at: image[at:at + size] for at, size in calibration_spans(declared)}
    first, second, coefficient = (100,) * 16, (20,) * 16, (200,) * 16
    if pattern == 'a-high':
        first = (120,) * 16
    elif pattern == 'b-high':
        second = (40,) * 16
    elif pattern == 'equal':
        second = first
    elif pattern == 'bypass':
        first, second = (20,) * 16, (100,) * 16
    elif pattern == 'maximum':
        first, second, coefficient = (255,) * 16, (254,) * 16, (255,) * 16
    elif pattern in ('rising', 'falling'):
        first = tuple(index * 17 for index in range(16))
        if pattern == 'falling':
            first = tuple(255 - value for value in first)
    elif pattern not in ('a-low', 'b-low'):
        raise ValueError('the differential-curve calibration changes its explicit pattern')
    return {0x12738: bytes(first), 0x12748: bytes(second), 0x12930: bytes(coefficient)}


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x106F], ram[0x16AB], ram[0x171D] = case['coordinate'], case['observed'], 0xA7
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the differential-curve original changes its explicit bounded entry premises')
