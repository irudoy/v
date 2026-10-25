"""Explicit byte coordinates, word numerators and retained neighbor inputs."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x7A20A
KINDS = ('window',)
PATTERNS = ('stock', 'zero', 'one', 'two', 'maximum', 'rising', 'falling')
AXES = ('stock', 'strict', 'raised')


def cases(declared, image):
    result = []

    def add(pattern, axis, coordinate, numerator):
        index = len(result)
        result.append(dict(index=index, kind='window', entry=ENTRY, pattern=pattern, axis=axis,
                           coordinate=coordinate, numerator=numerator, variant=index % 4,
                           sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))

    coordinates = {0, 1, 254, 255}
    for knot in range(0, 226, 32):
        coordinates.update(value for value in (knot - 1, knot, knot + 1, knot + 2) if 0 <= value <= 255)
    for axis in AXES:
        for pattern in PATTERNS:
            for coordinate in sorted(coordinates):
                add(pattern, axis, coordinate, 1)
    for pattern in ('zero', 'one', 'two', 'maximum'):
        for numerator in (0, 1, 327, 328, 32767, 32768, 65534, 65535):
            add(pattern, 'strict', 112, numerator)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[2] = case['coordinate']
    registers[11] = RAM_BASE + 0x28F8
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x11FD6, 9), (0x11A83, 8))


def calibrations(declared, image, case):
    pattern = case['pattern']
    if pattern == 'stock':
        raw = image[0x11FD6:0x11FDE]
    elif pattern in ('zero', 'one', 'two', 'maximum'):
        raw = bytes([dict(zero=0, one=1, two=2, maximum=255)[pattern]]) * 8
    elif pattern in ('rising', 'falling'):
        raw = bytes(index * 32 for index in range(8))
        if pattern == 'falling':
            raw = bytes(255 - value for value in raw)
    else:
        raise ValueError('the spirited-hamster calibration changes its explicit pattern')
    axis = image[0x11A83:0x11A8B]
    if case['axis'] in ('strict', 'raised'):
        axis = bytes(index * 32 + int(case['axis'] == 'raised') for index in range(8))
    elif case['axis'] != 'stock':
        raise ValueError('the spirited-hamster calibration changes its explicit axis')
    return {0x11FD6: raw + image[0x11FDE:0x11FDF], 0x11A83: axis}


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x2C78:0x2C7A] = case['numerator'].to_bytes(2, 'big')
    ram[0x2BE4] = 0xD3
    ram[0x2C74:0x2C76] = bytes.fromhex('a7b8')
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not 0 <= case['coordinate'] <= 255
            or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the spirited-hamster original changes its explicit bounded-entry premises')
