"""Explicit natural entry inputs and conditional curve calibrations."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x4BBEE
PATTERNS = ('stock', 'zero', 'one', 'two', '127', '128', 'maximum', 'second-zero', 'rising', 'falling', 'slopes')


def cases(declared, image):
    result = []

    def add(pattern, mode=1, coordinate=112, numerator=64, prior=255, history=0):
        index = len(result)
        result.append(dict(index=index, entry=ENTRY, pattern=pattern, mode=mode, coordinate=coordinate,
                           numerator=numerator, prior=prior, history=history, variant=index % 4,
                           sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))

    for mode in (0, 1):
        for pattern in PATTERNS:
            for coordinate in (0, 15, 16, 112, 127, 239, 240, 255):
                add(pattern, mode, coordinate)
    for mode in (0, 1):
        for pattern in ('one', '127', 'second-zero'):
            for numerator in (0, 1, 127, 128, 255):
                add(pattern, mode, numerator=numerator)
        for prior in (0, 129, 130, 131, 255):
            for history in (0, 16639, 16640, 65535):
                add('slopes', mode, prior=prior, history=history)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x1243A, 16), (0x1244A, 16), (0x12462, 16), (0x12472, 16), (0x87CA, 9), (0x11ECD, 1))


def calibrations(declared, image, case):
    result = {at: image[at:at + size] for at, size in calibration_spans(declared)}
    pattern = case['pattern']
    if pattern == 'stock':
        return result
    result.update({0x1243A: bytes([32]) * 16, 0x1244A: bytes([1]) * 16,
                   0x12462: bytes([200]) * 16, 0x12472: bytes([200]) * 16, 0x11ECD: b'\x80'})
    if pattern in ('zero', 'one', 'two', '127', '128', 'maximum'):
        result[0x1244A] = bytes([{'zero': 0, 'one': 1, 'two': 2, '127': 127, '128': 128, 'maximum': 255}[pattern]]) * 16
    elif pattern == 'second-zero':
        result[0x12472] = bytes(16)
    elif pattern in ('rising', 'falling'):
        values = bytes(index * 17 for index in range(16))
        result[0x1244A] = values if pattern == 'rising' else bytes(255 - value for value in values)
    elif pattern == 'slopes':
        result[0x87CA] = bytes((130, 130, 0, 0, 0, 255, 255, 255, 255))
    else:
        raise ValueError('the arrogant-catfish calibration changes its explicit pattern')
    return result


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x2466] = case['mode'] * 64
    ram[0x11B3], ram[0x1048], ram[0x15EB] = case['coordinate'], case['numerator'], case['prior']
    ram[0x22E8:0x22EA] = case['history'].to_bytes(2, 'big')
    for at, value in ((0x15ED, 0xA3), (0x15EE, 0xB4), (0x15EC, 0xC5), (0x15EA, 0xD6)):
        ram[at] = value
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the arrogant-catfish original changes an explicit natural-entry input')
