"""Typed inputs for the natural sexy-tamarin entry."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0xC0D90
PATTERNS = ('stock', 'constant', 'rising')


def curve(pattern):
    if pattern == 'stock':
        return None
    if pattern == 'constant':
        return (100,) * 8
    if pattern == 'rising':
        return tuple(10 + index * 12 for index in range(8))
    raise ValueError('the sexy-tamarin calibration input changes its declared pattern')


def cases(declared, image):
    result = []

    def add(index=0, pattern='stock', which=0, source=0x90, other=0x80, coordinate=0x10,
            column=0x20, row=0x30, gate=0, wide=0):
        result.append(dict(index=len(result), entry=ENTRY, input=index, pattern=pattern, which=which,
            source=source, other=other, coordinate=coordinate, column=column, row=row, gate=gate, wide=wide,
            variant=len(result) % 4,
            sr=(len(result) & 1) | ((len(result) & 15) << 4) | ((len(result) & 3) << 8)))

    add()
    add(pattern='constant', which=1)
    add(pattern='rising', which=1)
    add(pattern='constant', which=2)
    add(pattern='rising', which=2)
    add(index=1, source=0xA0, other=0x70, row=0x40)
    add(index=1, source=0xA0, other=0x70, row=0x40, pattern='constant', which=1)
    add(index=1, source=0xA0, other=0x70, row=0x40, pattern='constant', which=2)
    add(gate=1)
    add(source=0x80, coordinate=40)
    add(wide=1)
    add(index=2, source=0x88, other=0x60, pattern='rising', which=1)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF for reg in range(15)]
    registers[4] = case['input'] & 255
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000 | case['input'])


def calibration_spans(declared):
    return ((0x1252A, 9), (0x12532, 9), (0x123F2, 9), (0x123FA, 9), (0x1302E, 8), (0x11BEB, 8),
            (0x8D61, 11), (0x833C, 1), (0x8DD9, 1), (0x879A, 1), (0x87B0, 1), (0x87B1, 1))


def calibrations(declared, image, case):
    values = {0x1252A: bytearray(image[0x1252A:0x12533]), 0x12532: bytearray(image[0x12532:0x1253B]),
              0x123F2: bytearray(image[0x123F2:0x123FB]), 0x123FA: bytearray(image[0x123FA:0x12403])}
    pattern = curve(case['pattern'])
    if pattern is not None and case['which']:
        address = (0x1252A if case['input'] == 0 else 0x12532) if case['which'] == 1 else (
            0x123F2 if case['input'] == 0 else 0x123FA)
        values[address][:8] = bytes(pattern)
    return {0x1252A: bytes(values[0x1252A]), 0x12532: bytes(values[0x12532]),
            0x123F2: bytes(values[0x123F2]), 0x123FA: bytes(values[0x123FA]),
            0x1302E: image[0x1302E:0x13036], 0x11BEB: image[0x11BEB:0x11BF3],
            0x8D61: image[0x8D61:0x8D6C], 0x833C: image[0x833C:0x833D], 0x8DD9: image[0x8DD9:0x8DDA],
            0x879A: image[0x879A:0x879B], 0x87B0: image[0x87B0:0x87B1], 0x87B1: image[0x87B1:0x87B2]}


def memory(case):
    result = bytearray(RAM_SIZE)
    result[0x1240 + (case['input'] & 255)] = case['source'] & 255
    result[0x127E + (case['input'] & 255)] = case['other'] & 255
    result[0x11AE] = case['coordinate'] & 255
    result[0x2327] = case['column'] & 255
    result[0x2324 + (case['input'] & 255)] = case['row'] & 255
    if case['gate']:
        result[0x1ACC] = (case['input'] + 1) & 255
    if case['wide']:
        result[0x14C8] = (case['input'] + 1) & 255
    result[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the sexy-tamarin original changes an explicit index, curve or biased byte')
