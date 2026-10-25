"""Explicit paired word divisors, axes and prior fault inputs."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
KINDS = ('first', 'second')
ENTRIES = (0x6961A, 0x696BC)
TABLES = (0x237C4, 0x23804)
AXIS_ADDRESSES = (0x237B4, 0x237F4)
PATTERNS = ('stock', 'zero', 'one', 'two', 'four', '256', 'maximum', 'rising', 'falling')
AXES = ('stock', 'strict', 'raised')


def cases(declared, image):
    result = []
    for kind, entry in zip(KINDS, ENTRIES):
        for pattern in PATTERNS:
            for axis in AXES:
                for coordinate in (0, 1, 31, 32, 33, 64, 127, 128, 223, 224, 225, 254, 255):
                    index = len(result)
                    result.append(dict(index=index, kind=kind, entry=entry, pattern=pattern, axis=axis,
                        coordinate=coordinate, variant=index % 4,
                        sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[4] = TABLES[KINDS.index(case['kind'])]
    registers[6], registers[11], registers[12], registers[14] = case['coordinate'], 0x21BBC, 256, 0x264CC
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x237C4, 18), (0x23804, 18), (0x237B4, 16), (0x237F4, 16))


def calibrations(declared, image, case):
    result = {at: image[at:at + size] for at, size in calibration_spans(declared)}
    selected = TABLES[KINDS.index(case['kind'])]
    pattern = case['pattern']
    if pattern in ('zero', 'one', 'two', 'four', '256', 'maximum'):
        values = ({'zero': 0, 'one': 1, 'two': 2, 'four': 4, '256': 256, 'maximum': 65535}[pattern],) * 8
    elif pattern in ('rising', 'falling'):
        values = tuple(index * 8192 for index in range(8))
        if pattern == 'falling':
            values = tuple(65535 - value for value in values)
    elif pattern == 'stock':
        values = None
    else:
        raise ValueError('the reciprocal-curve calibration changes its explicit pattern')
    if values is not None:
        result[selected] = b''.join(value.to_bytes(2, 'big') for value in values) + image[selected + 16:selected + 18]
    if case['axis'] != 'stock':
        if case['axis'] not in ('strict', 'raised'):
            raise ValueError('the reciprocal-curve calibration changes its explicit axis')
        raw = b''.join((index * 32 + int(case['axis'] == 'raised')).to_bytes(2, 'big') for index in range(8))
        for at in AXIS_ADDRESSES:
            result[at] = raw
    return result


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRIES[KINDS.index(case['kind'])]
            or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the reciprocal original changes an explicit divisor lookup or register input')
