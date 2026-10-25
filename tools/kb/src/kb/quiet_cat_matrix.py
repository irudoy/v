"""Typed inputs for the natural quiet-cat entry."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0xBE32A
PATTERNS = ('stock', 'constant', 'rising', 'high')


def curve(pattern):
    if pattern == 'stock':
        return None
    if pattern == 'constant':
        return (100,) * 8
    if pattern == 'rising':
        return tuple(10 + index * 12 for index in range(8))
    if pattern == 'high':
        return (255,) * 8
    raise ValueError('the quiet-cat calibration input changes its declared pattern')


def cases(declared, image):
    result = []

    def add(index=0, pattern='stock', source=0x90, other=0x80, coordinate=0x10, side=0x20,
            flag=0, gate=1, wide=0):
        result.append(dict(index=len(result), entry=ENTRY, input=index, pattern=pattern, source=source,
            other=other, coordinate=coordinate, side=side, flag=flag, gate=gate, wide=wide,
            variant=len(result) % 4,
            sr=(len(result) & 1) | ((len(result) & 15) << 4) | ((len(result) & 3) << 8)))

    for pattern in PATTERNS:
        add(pattern=pattern)
    add(index=1, source=0xA0, other=0x70)
    add(index=1, source=0xA0, other=0x70, pattern='constant')
    add(source=0x80, pattern='constant')
    add(coordinate=30, side=60, pattern='rising')
    add(coordinate=200, flag=1, gate=0, wide=1)
    add(coordinate=20, pattern='constant')
    add(coordinate=0, side=0, pattern='rising')
    add(index=2, source=0x88, other=0x60, pattern='high')
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF for reg in range(15)]
    registers[4] = case['input'] & 255
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000 | case['input'])


def calibration_spans(declared):
    return ((0x123EA, 9), (0x12412, 9), (0x11BE3, 8), (0x8616, 1), (0x8615, 1), (0x8D64, 7), (0x87AF, 1), (0x87B4, 1))


def calibrations(declared, image, case):
    values = curve(case['pattern'])
    primary = bytearray(image[0x123EA:0x123F3])
    secondary = bytearray(image[0x12412:0x1241B])
    if values is not None:
        target = primary if case['input'] == 0 else secondary
        target[:8] = bytes(values)
    gate = bytearray(image[0x8616:0x8617])
    gate[0] = 1 if case['gate'] else 0
    wide = bytearray(image[0x8615:0x8616])
    wide[0] = 0x40 if case['wide'] else image[0x8615]
    return {0x123EA: bytes(primary), 0x12412: bytes(secondary), 0x11BE3: image[0x11BE3:0x11BEB],
            0x8616: bytes(gate), 0x8615: bytes(wide), 0x8D64: image[0x8D64:0x8D6B],
            0x87AF: image[0x87AF:0x87B0], 0x87B4: image[0x87B4:0x87B5]}


def memory(case):
    result = bytearray(RAM_SIZE)
    result[0x1224 + (case['input'] & 255)] = case['source'] & 255
    result[0x1262 + (case['input'] & 255)] = case['other'] & 255
    result[0x11AE] = case['coordinate'] & 255
    result[0x2772] = case['side'] & 255
    result[0x1071] = case['side'] & 255
    result[0x24A7] = 1 if case['flag'] else 0
    result[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(result)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the quiet-cat original changes an explicit index, curve or biased byte')
