"""Explicit high-range coordinate, numerator and calibration inputs."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x81674
KINDS = ('window',)
PATTERNS = ('stock', 'zero', 'one', 'two', 'maximum', 'rising', 'falling')


def cases(declared, image):
    result = []

    def add(pattern, coordinate, numerator):
        index = len(result)
        result.append(dict(index=index, kind='window', entry=ENTRY, pattern=pattern,
                           coordinate=coordinate, numerator=numerator, variant=index % 4,
                           sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))

    coordinates = {0, 1, 0xC3FE, 0xC3FF}
    for knot in range(0x1000, 0xC001, 0x1000):
        coordinates.update((knot - 1, knot, knot + 1))
    for pattern in PATTERNS:
        for coordinate in sorted(coordinates):
            add(pattern, coordinate, 1)
    for pattern in ('zero', 'one', 'two', 'maximum'):
        for numerator in (0, 1, 2, 127, 128, 254, 255):
            add(pattern, 0x2800, numerator)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[0] = 0x3C00 + case['coordinate']
    registers[12] = RAM_BASE + 0x128C
    registers[14] = 0x263F4
    return (*registers, RAM_BASE + 0x128C, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x15022, 32),)


def calibrations(declared, image, case):
    pattern = case['pattern']
    if pattern == 'stock':
        raw = image[0x15022:0x15042]
    elif pattern in ('zero', 'one', 'two', 'maximum'):
        value = dict(zero=0, one=0x100, two=0x200, maximum=0xFFFF)[pattern]
        raw = value.to_bytes(2, 'big') * 16
    elif pattern in ('rising', 'falling'):
        words = tuple(index * 0x1111 for index in range(16))
        if pattern == 'falling':
            words = tuple(0xFFFF - value for value in words)
        raw = b''.join(value.to_bytes(2, 'big') for value in words)
    else:
        raise ValueError('the rugged-gerbil calibration changes its explicit pattern')
    return {0x15022: raw}


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x1737] = case['numerator']
    ram[0x1738] = 0xD3
    ram[0x1733] = 0xA7
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not 0 <= case['coordinate'] <= 0xC3FF
            or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the rugged-gerbil original changes its explicit high-range entry premises')
