"""Explicit bounded entries, native storage values and descriptor inputs."""

RAM_BASE = 0x01000000
RAM_SIZE = 65536
KINDS = ('capture', 'monitor-prefix', 'monitor-read', 'mailbox')
ENTRIES = (0x2040, 0xA6DC8, 0xA6E9E, 0xC2FE4)
NATIVE_IO = ((0xFFFFD900, 1024), (0xFFFFF400, 256), (0xFFFFF700, 256))
PATTERNS = ('stock', 'zero', 'type-one', 'type-two', 'type-three', 'type-four', 'inactive',
            'unknown', 'identifier-min', 'identifier-max')
RECORDS = (bytes(4), bytes(4), bytes.fromhex('01084720'), bytes.fromhex('02fffdff'),
           bytes.fromhex('03014720'), bytes.fromhex('041f5600'), bytes.fromhex('05000000'),
           bytes.fromhex('ff00ffff'), bytes.fromhex('01000001'), bytes.fromhex('01ffffff'))


def cases(declared, image):
    result = []
    group = 0

    def add(kind, **values):
        row = dict(pattern='stock', slot=25, selector=0, param=0, word=0, prior=0)
        row.update(values)
        seed = row['slot'] + row['selector'] + row['param'] + row['prior']
        row.update(index=len(result), group=group, kind=kind, entry=ENTRIES[KINDS.index(kind)],
                   variant=seed % 4, sr=(seed & 1) | ((seed & 15) << 4) | ((seed & 3) << 8))
        result.append(row)

    for param in (0, 1, 0x7FFF, 0x8000, 0xFFFF, 0xF00DCAFE, 0xFFFFFFFF):
        for word in (0, 1, 0xFFFF, 0x10000, 0x7FFFFFFF, 0x80000000, 0xA1B2C3D4, 0xFFFFFFFF):
            add('capture', param=param, word=word)
            group += 1
    for selector in (0, 6):
        for word in (0, 1, 3, 4, 0x7FF, 0x800, 0x804, 0xFFFF):
            add('monitor-prefix', selector=selector, word=word)
            add('monitor-read', selector=selector, word=word)
            group += 1
    for slot in (0, 24, 25, 26, 29):
        for pattern in PATTERNS:
            for prior in (0, 0x12345678, 0xFFFFFFFF):
                add('mailbox', slot=slot, pattern=pattern, prior=prior)
                group += 1
    return tuple(result)


def context(declared, case, previous=None):
    registers = [(0x1728394A + reg * 0x110203 + case['variant'] * 0x1000101) & 0xFFFFFFFF
                 for reg in range(15)]
    gbr = 0x12344321
    if case['kind'] == 'capture':
        registers[4] = case['param']
    elif case['kind'] == 'monitor-prefix':
        registers[4] = case['selector']
    elif case['kind'] == 'monitor-read':
        if previous is None:
            raise ValueError('the monitor word read lacks its actual preceding stride result')
        registers[4], gbr = previous['exit'][15], previous['exit'][4]
    elif case['kind'] == 'mailbox':
        registers[7], registers[9], registers[11] = 1 << (case['slot'] + 1), case['prior'], case['slot']
    else:
        raise ValueError('the I/O inputs change a declared entry role')
    return (*registers, gbr, 0x13579BDF, 0x2468ACE0, case['sr'], 0xB6C70000)


def calibration_spans(declared):
    return ((0x975A, 120), (0x23AC4, 392))


def calibrations(declared, image, case):
    result = {at: image[at:at + size] for at, size in calibration_spans(declared)}
    if case['kind'] == 'mailbox' and case['pattern'] != 'stock':
        raw = bytearray(result[0x975A])
        offset = case['slot'] * 4
        raw[offset:offset + 4] = RECORDS[PATTERNS.index(case['pattern'])]
        result[0x975A] = bytes(raw)
    return result


def memory(case):
    ram = bytearray(RAM_SIZE)
    for (start, size), value in zip(NATIVE_IO, (0xA5, 0x5C, 0x6D)):
        offset = start & 65535
        ram[offset:offset + size] = bytes([value]) * size
    if case['kind'] == 'capture':
        ram[0xF430:0xF434] = case['word'].to_bytes(4, 'big')
    elif case['kind'] in ('monitor-prefix', 'monitor-read'):
        ram[0xF754:0xF756] = case['word'].to_bytes(2, 'big')
    return bytes(ram)


def native_bytes(ram):
    return b''.join(ram[start & 65535:(start & 65535) + size] for start, size in NATIVE_IO)


def require_input(declared, image, case, observed, previous=None):
    from kb import test_contract
    if (observed['entry'] != case['entry']
            or not test_contract.exact(observed['context'], context(declared, case, previous))
            or observed['memory_before'] != (memory(case),)
            or observed['native_before'] != native_bytes(memory(case))
            or not test_contract.exact(observed['calibration_before'], calibrations(declared, image, case))
            or not test_contract.exact(observed['calibration_after'], calibrations(declared, image, case))):
        raise ValueError('the I/O original changes its complete exact entry/native-storage/descriptor inputs')
