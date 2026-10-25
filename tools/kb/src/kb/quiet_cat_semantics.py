"""Independent quiet-cat: indexed byte lookup and signed quotient."""

from kb import division_callees_semantics as division

ENTRY = 0xBE32A
SIGNED_SITE = 0xBE41E
DIVISOR = 100
BASE = 0x128C
MASK = 0xFFFFFFFF


def sx(value):
    return value - 0x100000000 if value & 0x80000000 else value


def scan(axis, coordinate):
    offset = origin = 7
    while True:
        knot = axis[offset]
        if knot == coordinate:
            return offset, 0
        if coordinate > knot:
            if offset == origin:
                return offset, 0
            upper = axis[offset + 1]
            dividend = ((coordinate - knot) & MASK) << 16
            divisor = (upper - knot) & MASK
            fraction = division.quotient('unsigned', divisor, dividend & MASK) & 65535
            return offset, fraction
        offset -= 1
        if offset < 0:
            return 0, 0


def linear(first, second, fraction):
    if second >= first:
        return (first + (((fraction * (second - first)) & MASK) >> 16)) & MASK
    return (first - (((fraction * (first - second)) & MASK) >> 16)) & MASK


def curve(table, axis, coordinate):
    if len(table) != 9 or len(axis) != 8:
        raise ValueError('the quiet-cat curve needs eight axis knots and nine table bytes')
    offset, fraction = scan(axis, coordinate & 255)
    value = linear(table[offset], table[offset + 1], fraction) & 255
    return dict(value=value, offsets=(offset, offset + 1))


def bilinear(table, row_axis, row, col_axis, col):
    row_at, row_fraction = scan(row_axis, row & 255)
    col_at, col_fraction = scan(col_axis, col & 255)
    base = col_at + row_at * 8

    def pair(at):
        return table[at], table[at + 1]

    if col_fraction:
        left = linear(*pair(base), col_fraction)
        if row_fraction == 0:
            return left & 255
        right = linear(*pair(base + 8), col_fraction)
        return linear(left, right, row_fraction) & 255
    if row_fraction == 0:
        return table[base]
    return linear(table[base], table[base + 8], row_fraction) & 255


def overlay(image, calibration):
    raw = bytearray(image)
    for address, data in calibration.items():
        raw[address:address + len(data)] = data
    return bytes(raw)


def caller(image, calibration, before, index):
    if type(before) is not bytes or len(before) != 65536 or type(image) is not bytes:
        raise ValueError('the quiet-cat equation needs its complete image and RAM input')
    image = overlay(image, calibration)
    for address, size in ((0x123EA, 9), (0x12412, 9), (0x11BE3, 8), (0x8616, 1), (0x8615, 1),
                          (0x8D64, 7), (0x87AF, 1), (0x87B4, 1)):
        if address not in calibration or len(calibration[address]) != size:
            raise ValueError('the quiet-cat equation lacks an explicit curve or configuration byte')
    result = bytearray(before)
    index &= 255
    gate = image[0x8616] & 1
    source = before[0x1224 + index]
    biased = (source - 0x80) & MASK
    if gate:
        side = before[0x2772]
        table_a = image[0xA09A:0xA09A + 80] if index == 0 else image[0xA0DA:0xA0DA + 80]
        col_axis = image[0x13046:0x1304E]
    else:
        side = before[0x1071]
        table_a = image[0xA01A:0xA01A + 80] if index == 0 else image[0xA05A:0xA05A + 80]
        col_axis = image[0x1304E:0x13056]
    primary = bilinear(table_a, image[0x13026:0x1302E], before[0x11AE], col_axis, side) & 255
    result[BASE + 0x368 + index] = primary
    dividend = ((primary * biased) << 8) & MASK
    quotient = division.quotient('signed', DIVISOR, dividend)
    mixed = (quotient + 0x8000) & MASK
    if sx(mixed) < 0:
        mixed = 0
    if sx(mixed) > 65535:
        mixed = 65535
    result[BASE + 0x860 + index * 2:BASE + 0x862 + index * 2] = mixed.to_bytes(2, 'big')
    other = (before[0x1262 + index] - 0x80) & MASK
    address = 0x123EA if index == 0 else 0x12412
    looked = curve(image[address:address + 9], image[0x11BE3:0x11BEB], before[0x11AE])
    result[BASE + 0x348 + index] = looked['value']
    second_dividend = (looked['value'] * ((biased - other) & MASK)) & MASK
    second = division.quotient('signed', DIVISOR, second_dividend)
    clamped = (second + 0x80) & MASK
    if sx(clamped) < 0:
        clamped = 0
    if sx(clamped) > 255:
        clamped = 255
    result[BASE + 0x7F8 + index] = clamped & 255
    calls = [dict(site=0xBE3BC, target=0x21BBC, divisor=DIVISOR, dividend=dividend),
             dict(site=SIGNED_SITE, target=0x21BBC, divisor=DIVISOR, dividend=second_dividend,
                  lookup=looked['value'], table=address)]
    level = image[0x8D67]
    if (before[0x24A7] & 1) == 0 and not (-level <= sx(biased) <= level):
        factor = image[0x87AF if index == 0 else 0x87B4]
        third_dividend = ((factor * biased) << 9) & MASK
        third = division.quotient('signed', DIVISOR, third_dividend)
        slot = BASE + 0x830 + index * 4
        total = (third + int.from_bytes(result[slot:slot + 4], 'big')) & MASK
        if sx(total) < 0:
            total = 0
        if sx(total) > 0xFFFFFF:
            total = 0xFFFFFF
        result[slot:slot + 4] = total.to_bytes(4, 'big')
        calls.append(dict(site=0xBE4F4, target=0x21BBC, divisor=DIVISOR, dividend=third_dividend))
    if -image[0x8D6A] <= sx(biased) <= image[0x8D6A]:
        acc = 0x800000
    else:
        word = int.from_bytes(result[BASE + 0x860 + index * 2:BASE + 0x862 + index * 2], 'big')
        acc = ((((word + 0xFFFF8000) & MASK) << 8) + 0x800000) & MASK
    slot = BASE + 0x830 + index * 4
    acc = (acc + ((int.from_bytes(result[slot:slot + 4], 'big') - 0x800000) & MASK)) & MASK
    if not (-image[0x8D64] <= sx(biased) <= image[0x8D64]):
        acc = (acc + (((clamped - 0x80) & MASK) << 16)) & MASK
    if (image[0x8615] & 0x40) == 0:
        extra = result[BASE + 0x7F2 + index]
        acc = (acc + (((extra - 0x80) & MASK) << 16)) & MASK
    if sx(acc) < 0:
        acc = 0
    if sx(acc) > 0xFFFFFF:
        acc = 0xFFFFFF
    result[BASE + 0x870 + index * 4:BASE + 0x874 + index * 4] = acc.to_bytes(4, 'big')
    return dict(memory=bytes(result), calls=tuple(calls), lookup=looked, dividend=second_dividend,
                divisor=DIVISOR, table=address, fault=bytes(result[0x9818:0x981C]))
