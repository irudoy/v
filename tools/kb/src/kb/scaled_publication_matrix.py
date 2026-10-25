"""Explicit paired publication entries and bounded register inputs."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
KINDS = ('signed', 'unsigned')
ENTRIES = (0x7A778, 0x7A968)


def cases(declared, image):
    result = []
    for kind, entry in zip(KINDS, ENTRIES):
        for value in (0, 1, 2, 799, 800, 801, 1599, 1600, 32767, 32768, 65534, 65535):
            for variant in range(4):
                index = len(result)
                result.append(dict(index=index, kind=kind, entry=entry, value=value, variant=variant,
                                   sr=(index & 1) | ((index & 15) << 4) | ((index & 3) << 8)))
    return tuple(result)


def context(declared, case):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    registers[5] = registers[6] = case['value']
    registers[9] = RAM_BASE + 0x28F8
    registers[12] = 65535
    return (*registers, 0x12344321, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ()


def calibrations(declared, image, case):
    return {}


def memory(case):
    ram = bytearray(RAM_SIZE)
    ram[0x1210:0x1212] = bytes.fromhex('a3b4')
    ram[0x1248:0x124A] = bytes.fromhex('c5d6')
    ram[0x35CC:0x35CE] = bytes.fromhex('e7f8')
    ram[0x9818:0x981C] = bytes.fromhex('a5c3d2e1')
    return bytes(ram)


def require_input(declared, image, case, observed):
    from kb import test_contract
    expected = ENTRIES[KINDS.index(case['kind'])]
    if (observed['entry'] != expected or not 0 <= case['value'] <= 65535
            or not test_contract.exact(observed['context'], context(declared, case))
            or observed['memory_before'] != (memory(case),)
            or observed['calibration_before'] != {} or observed['calibration_after'] != {}):
        raise ValueError('the scaled-publication original changes a bounded register or complete RAM input')
