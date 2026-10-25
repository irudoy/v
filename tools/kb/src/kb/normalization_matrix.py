"""Explicit sequenced coefficient and selected-U inputs with complete RAM continuity."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
KINDS = ('coefficient', 'branch-a', 'branch-b')
ENTRIES = (0x627A6, 0x627C2, 0x627C8)
PATTERNS = ('stock', 'U-one', 'U-two', 'K-zero', 'K-one', 'K-two', 'K-unity', 'maximum', 'rising', 'falling')


def cases(declared, image):
    result = []
    group = 0
    for selected in ('branch-a', 'branch-b'):
        for pattern in PATTERNS:
            for coordinate, coefficient_coordinate in ((0, 0), (4096, 16), (30720, 120), (65535, 255)):
                for kind in ('coefficient', selected):
                    index = len(result)
                    result.append(dict(index=index, group=group, kind=kind, selected=selected,
                        entry=ENTRIES[KINDS.index(kind)], pattern=pattern, coordinate=coordinate,
                        coefficient_coordinate=coefficient_coordinate, variant=group % 4,
                        sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))
                group += 1
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[6] = case['coefficient_coordinate']
    registers[8] = 1
    registers[10] = case['coordinate']
    registers[12], registers[13], registers[14] = RAM_BASE + 0x28F8, 0x15CE0, 0x264F8
    return (*registers, RAM_BASE + 0x8D58, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x1495A, 34), (0x1459A, 34), (0x145CA, 34), (0x13A98, 32), (0x15CE0, 32))


def calibrations(declared, image, case):
    result = {at: image[at:at + size] for at, size in calibration_spans(declared)}
    pattern = case['pattern']
    if pattern == 'stock':
        return result
    selected = 0x1459A if case['selected'] == 'branch-a' else 0x145CA
    words = {0x1495A: (50000,) * 16, 0x1459A: (10000,) * 16, 0x145CA: (10000,) * 16}
    if pattern in ('U-one', 'U-two'):
        words[selected] = (1000 if pattern == 'U-one' else 2000,) * 16
    elif pattern in ('K-zero', 'K-one', 'K-two', 'K-unity'):
        words[0x1495A] = ({'K-zero': 0, 'K-one': 1000, 'K-two': 2000, 'K-unity': 50000}[pattern],) * 16
    elif pattern == 'maximum':
        words[0x1495A] = words[selected] = (65535,) * 16
    elif pattern in ('rising', 'falling'):
        values = tuple(index * 4096 for index in range(16))
        if pattern == 'falling':
            values = tuple(65535 - value for value in values)
        words[0x1495A] = words[selected] = values
    else:
        raise ValueError('the normalization calibration changes its explicit pattern')
    for at, values in words.items():
        result[at] = b''.join(value.to_bytes(2, 'big') for value in values) + image[at + 32:at + 34]
    result[0x13A98] = b''.join((index * 16).to_bytes(2, 'big') for index in range(16))
    result[0x15CE0] = b''.join((index * 4096).to_bytes(2, 'big') for index in range(16))
    return result


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x2B68:0x2B6A] = bytes.fromhex('a3b4')
    ram[0x8D60:0x8D64] = bytes.fromhex('11223344')
    ram[0x8D68:0x8D6C] = bytes.fromhex('a7b8c9da')
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != ENTRIES[KINDS.index(case['kind'])]
            or not test_contract.exact(observed['context'], context(declared, case))
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))
            or case['kind'] == 'coefficient' and observed['memory_before'] != (memory(case),)):
        raise ValueError('the normalization original changes its explicit entry or calibration premises')
