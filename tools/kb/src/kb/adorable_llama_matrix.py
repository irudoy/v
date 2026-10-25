"""Explicit paired curves, byte coordinate and preserved mode-byte inputs."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
ENTRY = 0x4161C
KINDS = ('window',)
PATTERNS = ('stock', 'zero', 'maximum', 'rising', 'falling', 'ratio-first', 'ratio-second',
            'anchor-equal', 'anchor-above', 'tiny-divisor')


def cases(declared, image):
    result = []
    coordinates = {0, 1, 239, 240, 241, 254, 255, *(value + delta for value in range(0, 241, 16)
                    for delta in (-1, 0, 1) if 0 <= value + delta <= 255)}
    for pattern in PATTERNS:
        for coordinate in sorted(coordinates):
            for flags in (0x42, 0x62):
                seed = coordinate + flags
                result.append(dict(index=len(result), kind='window', entry=ENTRY, pattern=pattern,
                    coordinate=coordinate, flags=flags, variant=seed % 4,
                    sr=(seed & 1) | ((seed & 15) << 4) | ((seed & 3) << 8)))
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[5], registers[10] = case['coordinate'], RAM_BASE + 0x1FF4
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x12798, 16), (0x127D8, 16))


def calibrations(declared, image, case):
    pattern = case['pattern']
    if pattern == 'stock':
        return {at: image[at:at + size] for at, size in calibration_spans(declared)}
    first, second = bytes([200]) * 16, bytearray(16)
    if pattern == 'maximum':
        second[:] = bytes([255]) * 16
    elif pattern == 'rising':
        second[:] = bytes(index * 16 for index in range(16))
    elif pattern == 'falling':
        second[:] = bytes(255 - index * 16 for index in range(16))
    elif pattern in ('ratio-first', 'ratio-second'):
        second[:] = bytes([192 if pattern == 'ratio-first' else 190]) * 16
        second[:8] = bytes([196 if pattern == 'ratio-first' else 198]) * 8
    elif pattern in ('anchor-equal', 'anchor-above'):
        first = bytes([40]) * 16
        second[:] = bytes([40 if pattern == 'anchor-equal' else 50]) * 16
        second[:8] = bytes([10]) * 8
    elif pattern == 'tiny-divisor':
        first = bytes([255]) * 16
        second[8:] = bytes([254]) * 8
    elif pattern != 'zero':
        raise ValueError('the paired normalization changes its explicit calibration pattern')
    return {0x12798: first, 0x127D8: bytes(second)}


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x2459], ram[0x2236] = case['flags'], 0xA7
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRY or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the paired normalization changes its complete explicit bounded inputs')
