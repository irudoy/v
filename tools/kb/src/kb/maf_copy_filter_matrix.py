"""Explicit bank arguments, independent words, mode flags and coefficient."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
KINDS = ('copy', 'filter')
ENTRIES = (0x3A982, 0x3A9AA)
PAIRS = ((0, 0), (1, 0), (0, 1), (100, 101), (101, 100), (100, 100),
         (65535, 0), (0, 65535), (32768, 32767), (32767, 32768), (65535, 65534), (65534, 65535))


def cases(declared, image):
    result = []

    def add(kind, argument, value, previous, flags, coefficient):
        seed = KINDS.index(kind) + argument + previous + flags + coefficient
        result.append(dict(index=len(result), kind=kind, entry=ENTRIES[KINDS.index(kind)], argument=argument,
            input=value, previous=previous, flags=flags, coefficient=coefficient, variant=seed % 4,
            sr=(seed & 1) | ((seed & 15) << 4) | ((seed & 3) << 8)))

    for bank in (0, 1):
        for value in (0, 1, 100, 101, 32767, 32768, 65534, 65535):
            add('copy', bank, value, 0x1234, 0, 26)
        for value, previous in PAIRS:
            for flags in (0, 0x20):
                for coefficient in (0, 26):
                    add('filter', bank, value, previous, flags, coefficient)
        add('copy', 0xF00DCA00 | bank, 32768, 0x1234, 0, 26)
        add('filter', 0xF00DCA00 | bank, 1000, 0, 0x20, 26)
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + index * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF for index in range(15)]
    registers[4] = case['argument']
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x870A, 1),)


def calibrations(declared, image, case):
    return {0x870A: bytes([case['coefficient']])}


def memory(case):
    bank = case['argument'] & 255
    if bank not in (0, 1):
        raise ValueError('the MAF input leaves its explicit bank domain')
    result = bytearray([0xA5]) * RAM_SIZE
    for index in (0, 1):
        result[0x1054 + index * 2:0x1056 + index * 2] = (case['input'] if case['kind'] == 'copy' and index == bank else 0x6C19).to_bytes(2, 'big')
        result[0x1058 + index * 2:0x105A + index * 2] = (case['input'] if case['kind'] == 'filter' and index == bank else 0xA55A).to_bytes(2, 'big')
        result[0x1DF0 + index * 2:0x1DF2 + index * 2] = (case['previous'] if index == bank else 0x7ABC).to_bytes(2, 'big')
    result[0x2461] = case['flags']
    return bytes(result)


def require_input(declared, image, case, observed):
    from kb import test_contract
    if (observed['entry'] != case['entry'] or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the MAF original changes its complete explicit bank, words, mode or coefficient inputs')
