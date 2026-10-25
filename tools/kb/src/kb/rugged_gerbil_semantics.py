"""Separate word interpolation, high-byte divisor and saturation equations."""


def caller(calibration, before, coordinate):
    if (type(before) is not bytes or len(before) != 65536 or type(coordinate) is not int
            or not 0 <= coordinate <= 0xC3FF or set(calibration) != {0x15022}
            or type(calibration[0x15022]) is not bytes or len(calibration[0x15022]) != 32):
        raise ValueError('the rugged-gerbil equation lacks its bounded coordinate, curve or complete RAM')
    raw = calibration[0x15022]
    index, remainder = divmod(coordinate, 0x1000)
    first = int.from_bytes(raw[index * 2:index * 2 + 2], 'big')
    second = int.from_bytes(raw[index * 2 + 2:index * 2 + 4], 'big')
    magnitude = (abs(second - first) * (remainder << 4)) >> 16
    lookup = first + magnitude if second >= first else first - magnitude
    divisor = (lookup >> 8) & 255
    dividend = before[0x1737] << 8
    quotient = dividend // divisor if divisor else None
    output = min(255, quotient) if divisor else 255
    after = bytearray(before)
    after[0x1738], after[0x1733] = divisor, output
    return dict(memory=bytes(after), lookup=lookup, reads=(index * 2, index * 2 + 2),
                divisor=divisor, dividend=dividend, quotient=quotient, output=output,
                fault=bytes(after[0x9818:0x981C]))
