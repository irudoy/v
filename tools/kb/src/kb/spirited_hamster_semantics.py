"""Separate byte interpolation, word product, quotient and saturation equations."""


def curve(table, axis, coordinate):
    if len(table) != 9 or len(axis) != 8 or not 0 <= coordinate <= 255:
        raise ValueError('the spirited-hamster equation needs eight knots and a retained physical neighbor')
    index, fraction = 7, 0
    while True:
        knot = axis[index]
        if coordinate == knot or coordinate > knot and index == 7:
            break
        if coordinate > knot:
            divisor = axis[index + 1] - knot
            fraction = ((coordinate - knot) << 16) // divisor if divisor else 0
            break
        index -= 1
        if index < 0:
            index = 0
            break
    first, second = table[index], table[index + 1]
    magnitude = (abs(second - first) * fraction) >> 16
    value = first + magnitude if second >= first else first - magnitude
    return dict(value=value, reads=(index + 1, index))


def caller(calibration, before, coordinate):
    if (type(before) is not bytes or len(before) != 65536 or set(calibration) != {0x11FD6, 0x11A83}
            or type(coordinate) is not int or not 0 <= coordinate <= 255):
        raise ValueError('the spirited-hamster equation lacks its exact coordinate, curve or complete RAM')
    looked = curve(calibration[0x11FD6], calibration[0x11A83], coordinate)
    divisor = looked['value']
    dividend = int.from_bytes(before[0x2C78:0x2C7A], 'big') * 200
    quotient = dividend // divisor if divisor else None
    output = min(65535, quotient) if divisor else 65535
    after = bytearray(before)
    after[0x2BE4] = divisor
    after[0x2C74:0x2C76] = output.to_bytes(2, 'big')
    return dict(memory=bytes(after), lookup=divisor, reads=looked['reads'], divisor=divisor,
                dividend=dividend, quotient=quotient, output=output, fault=bytes(after[0x9818:0x981C]))
