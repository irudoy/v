"""Typed register inputs for the natural viridian-armadillo entry."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0xB7A3C
PATTERNS = ('stock', 'thousand', 'two-thousand', 'early')
AXES = ('stock', 'strict', 'raised')


def words(pattern):
    if pattern == 'stock':
        return None
    if pattern == 'thousand':
        return (0,) * 7 + (1000,)
    if pattern == 'two-thousand':
        return (0,) * 7 + (2000,)
    if pattern == 'early':
        return (100, 300) + (0,) * 6
    raise ValueError('the viridian-armadillo calibration input changes its declared pattern')


def axis_words(pattern):
    if pattern == 'stock':
        return None
    if pattern == 'strict':
        return tuple(index * 0x200 for index in range(8))
    if pattern == 'raised':
        return tuple(0x100 + index * 0x200 for index in range(8))
    raise ValueError('the viridian-armadillo calibration input changes its declared axis')


def cases(declared, image):
    result = []

    def add(pattern='stock', axis='stock', divisor=10, selector=0, dividend=0x4E20, scale=0, coordinate=1, factor=4, stage_factor=0):
        result.append(dict(index=len(result), entry=ENTRY, pattern=pattern, axis=axis, divisor=divisor,
            selector=selector, dividend=dividend, scale=scale, coordinate=coordinate, factor=factor, stage_factor=stage_factor,
            variant=len(result) % 4,
            sr=(len(result) & 1) | ((len(result) & 15) << 4) | ((len(result) & 3) << 8)))

    add()
    add(pattern='thousand', axis='strict', coordinate=14)
    add(pattern='two-thousand', axis='strict', coordinate=14)
    add(pattern='thousand', axis='strict', coordinate=14, divisor=0)
    add(pattern='thousand', axis='strict', coordinate=14, divisor=0, factor=0)
    add(pattern='thousand', axis='strict', coordinate=14, divisor=1, factor=255)
    add(pattern='early', axis='strict', coordinate=1)
    add(pattern='early', axis='raised', coordinate=0)
    add(pattern='thousand', factor=0)
    add(pattern='thousand', scale=200, dividend=0)
    add(dividend=0x7FFFFFFF, stage_factor=255)
    add(dividend=0x80000000, stage_factor=255)
    add(dividend=0xFFFFFFFF, stage_factor=1)
    for selector in (0, 1, 2, 3, 4, 255):
        add(selector=selector, pattern='thousand', axis='strict', coordinate=14, stage_factor=1)
    for coordinate in (0, 2, 3, 12, 13, 14, 15, 255):
        add(pattern='early', axis='strict', coordinate=coordinate)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF for reg in range(15)]
    registers[4] = case['divisor'] & 0xFFFFFFFF
    registers[5] = case['selector'] & 0xFFFFFFFF
    registers[6] = case['dividend'] & 0xFFFFFFFF
    registers[7] = case['scale'] & 0xFFFFFFFF
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], case['coordinate'] & 255)


def calibration_spans(declared):
    return ((0x14E42, 18), (0x13BB8, 16), (0x8832, 1), (0x8A30, 7))


def calibrations(declared, image, case):
    table = bytearray(image[0x14E42:0x14E54])
    pattern = words(case['pattern'])
    if pattern is not None:
        for index, value in enumerate(pattern):
            table[index * 2:index * 2 + 2] = value.to_bytes(2, 'big')
    knots = bytearray(image[0x13BB8:0x13BC8])
    axis = axis_words(case['axis'])
    if axis is not None:
        for index, value in enumerate(axis):
            knots[index * 2:index * 2 + 2] = value.to_bytes(2, 'big')
    stages = bytearray(image[0x8A30:0x8A37])
    stages[0] = case['stage_factor'] & 255
    return {0x14E42: bytes(table), 0x13BB8: bytes(knots), 0x8832: bytes([case['factor'] & 255]),
            0x8A30: bytes(stages)}


def memory(case):
    result = bytearray(RAM_SIZE)
    result[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the viridian-armadillo original changes an explicit divisor, curve or ROM factor')
