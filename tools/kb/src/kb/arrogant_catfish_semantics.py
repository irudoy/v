"""Separate interpolation, signed argument and piecewise correction equations."""

from kb import division_callees_semantics as division

MASK = 0xFFFFFFFF


def sx(value):
    return value - 0x100000000 if value & 0x80000000 else value


def curve(raw, coordinate):
    if len(raw) != 16 or not 0 <= coordinate <= 255:
        raise ValueError('the arrogant-catfish equation needs sixteen bytes and an explicit coordinate')
    if coordinate >= 240:
        return dict(value=raw[15], reads=(15,))
    index, fraction = divmod(coordinate, 16)
    first, second = raw[index:index + 2]
    magnitude = (abs(second - first) * fraction) // 16
    return dict(value=first + magnitude if second >= first else first - magnitude, reads=(index, index + 1))


def caller(calibration, before):
    if (type(before) is not bytes or len(before) != 65536
            or set(calibration) != {0x1243A, 0x1244A, 0x12462, 0x12472, 0x87CA, 0x11ECD}):
        raise ValueError('the arrogant-catfish equation lacks its exact calibration or complete RAM')
    mode = bool(before[0x2466] & 64)
    first_at, second_at = (0x1244A, 0x12472) if mode else (0x1243A, 0x12462)
    first = curve(calibration[first_at], before[0x11B3])
    second = curve(calibration[second_at], before[0x11B3])
    threshold = calibration[0x11ECD][0]
    divisor = threshold - first['value']
    opened = divisor > 0
    dividend = ((before[0x1048] - first['value']) * second['value']) & MASK
    quotient = sx(division.quotient('signed', divisor, dividend)) if opened else None
    phase = max(0, min(second['value'], quotient)) if opened else 0
    raw = calibration[0x87CA]
    breakpoint, ascending, descending = (raw[1], raw[6], raw[8]) if mode else (raw[0], raw[5], raw[7])
    prior = before[0x15EB]
    history = int.from_bytes(before[0x22E8:0x22EA], 'big')
    if prior < breakpoint:
        product = ascending * (prior * 128 - history)
    elif history < breakpoint * 128:
        product = descending * (prior - breakpoint) * 128 + ascending * (breakpoint * 128 - history)
    else:
        product = descending * (prior * 128 - history)
    correction = sx(product & MASK) >> 14
    output = max(0, min(phase, correction))
    after = bytearray(before)
    after[0x15ED], after[0x15EE], after[0x15EC], after[0x15EA] = first['value'], second['value'], phase, output
    return dict(memory=bytes(after), first=first, second=second, first_table=first_at, second_table=second_at,
                divisor=divisor if opened else None, dividend=dividend if opened else None, opened=opened,
                phase=phase, correction=correction, output=output, fault=bytes(after[0x9818:0x981C]))
