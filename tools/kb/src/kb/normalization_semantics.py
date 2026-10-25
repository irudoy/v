"""Independent word-curve, coefficient publication and normalization product equations."""


def word_curve(table, axis, coordinate):
    if len(table) != 34 or len(axis) != 32 or not 0 <= coordinate <= 65535:
        raise ValueError('the normalization curve requires sixteen words and its retained physical neighbor')
    word = lambda raw, at: int.from_bytes(raw[at:at + 2], 'big')
    offset, fraction = 30, 0
    while True:
        knot = word(axis, offset)
        if coordinate == knot or coordinate > knot and offset == 30:
            break
        if coordinate > knot:
            divisor = word(axis, offset + 2) - knot
            fraction = ((coordinate - knot) << 16) // divisor if divisor else 0
            break
        offset -= 2
        if offset < 0:
            offset = 0
            break
    first, second = word(table, offset), word(table, offset + 2)
    magnitude = (abs(second - first) * fraction) >> 16
    return dict(value=first + magnitude if second >= first else first - magnitude,
                reads=(offset + 2, offset))


def caller(calibration, before, case):
    if type(before) is not bytes or len(before) != 65536:
        raise ValueError('the normalization equation needs the complete actual RAM input')
    after = bytearray(before)
    if case['kind'] == 'coefficient':
        at, axis, coordinate = 0x1495A, 0x13A98, case['coefficient_coordinate']
        looked = word_curve(calibration[at], calibration[axis], coordinate)
        after[0x2B68:0x2B6A] = looked['value'].to_bytes(2, 'big')
        return dict(memory=bytes(after), table=at, lookup=looked, coefficient=looked['value'],
                    dividend=None, quotient=None, output=looked['value'], fault=bytes(after[0x9818:0x981C]))
    at = 0x1459A if case['kind'] == 'branch-a' else 0x145CA
    looked = word_curve(calibration[at], calibration[0x15CE0], case['coordinate'])
    coefficient = int.from_bytes(before[0x2B68:0x2B6A], 'big')
    dividend = (looked['value'] * coefficient) & 0xFFFFFFFF
    quotient = dividend // 50000
    output = min(65535, quotient)
    after[0x8D68:0x8D6A] = looked['value'].to_bytes(2, 'big')
    after[0x8D60:0x8D64] = quotient.to_bytes(4, 'big')
    after[0x8D6A:0x8D6C] = output.to_bytes(2, 'big')
    return dict(memory=bytes(after), table=at, lookup=looked, coefficient=coefficient,
                dividend=dividend, quotient=quotient, output=output, fault=bytes(after[0x9818:0x981C]))
