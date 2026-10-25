"""Independent sexy-tamarin: two indexed byte lookups and signed quotients."""

from kb import division_callees_semantics as division

ENTRY = 0xC0D90
FIRST_SITE = 0xC0DF6
SECOND_SITE = 0xC0F28
DIVISOR = 100
BASE = 0x128C
MASK = 0xFFFFFFFF


def sx(value):
    return value - 0x100000000 if value & 0x80000000 else value


def scan_byte(axis, coordinate):
    offset = origin = 7
    while True:
        knot = axis[offset]
        if knot == coordinate:
            return offset, 0
        if coordinate > knot:
            if offset == origin:
                return offset, 0
            dividend = ((coordinate - knot) & MASK) << 16
            divisor = (axis[offset + 1] - knot) & MASK
            return offset, division.quotient('unsigned', divisor, dividend & MASK) & 65535
        offset -= 1
        if offset < 0:
            return 0, 0


def linear(first, second, fraction):
    if second >= first:
        return (first + (((fraction * (second - first)) & MASK) >> 16)) & MASK
    return (first - (((fraction * (first - second)) & MASK) >> 16)) & MASK


def curve_byte(table, axis, coordinate):
    if len(table) != 9 or len(axis) != 8:
        raise ValueError('the sexy-tamarin byte curve needs eight axis knots and nine table bytes')
    offset, fraction = scan_byte(axis, coordinate & 255)
    value = linear(table[offset], table[offset + 1], fraction) & 255
    return dict(value=value, offsets=(offset + 1, offset))


def word_at(raw, offset):
    return int.from_bytes(raw[offset:offset + 2], 'big')


def scan_word(axis, coordinate, origin):
    offset = origin
    while True:
        knot = word_at(axis, offset)
        if knot == coordinate:
            return offset, 0
        if coordinate > knot:
            if offset == origin:
                return offset, 0
            upper = word_at(axis, offset + 2)
            dividend = ((coordinate - knot) & MASK) << 16
            divisor = (upper - knot) & MASK
            return offset, division.quotient('unsigned', divisor, dividend & MASK) & 65535
        offset -= 2
        if offset < 0:
            return 0, 0


def curve_word(table, axis, coordinate):
    offset, fraction = scan_word(axis, coordinate & 65535, 30)
    return linear(word_at(table, offset), word_at(table, offset + 2), fraction) & 65535


def bilinear_word(table, row_axis, row, col_axis, col):
    row_at, row_fraction = scan_word(row_axis, row & 65535, 14)
    col_at, col_fraction = scan_word(col_axis, col & 65535, 14)
    base = col_at + 8 * row_at

    def pair(at):
        return word_at(table, at), word_at(table, at + 2)

    if col_fraction:
        left = linear(*pair(base), col_fraction)
        if row_fraction == 0:
            return left & 65535
        right = linear(*pair(base + 16), col_fraction)
        return linear(left, right, row_fraction) & 65535
    if row_fraction == 0:
        return word_at(table, base)
    return linear(word_at(table, base), word_at(table, base + 16), row_fraction) & 65535


def shar7(value):
    return (sx(value) >> 7) & MASK


def overlay(image, calibration):
    raw = bytearray(image)
    for address, _size in ((0x1252A, 9), (0x12532, 9), (0x123F2, 9), (0x123FA, 9)):
        if address in calibration:
            raw[address:address + len(calibration[address])] = calibration[address]
    for address, data in calibration.items():
        if address not in (0x1252A, 0x12532, 0x123F2, 0x123FA):
            raw[address:address + len(data)] = data
    return bytes(raw)


def caller(image, calibration, before, index):
    if type(before) is not bytes or len(before) != 65536 or type(image) is not bytes:
        raise ValueError('the sexy-tamarin equation needs its complete image and RAM input')
    image = overlay(image, calibration)
    for address, size in ((0x1252A, 9), (0x12532, 9), (0x123F2, 9), (0x123FA, 9), (0x1302E, 8),
                          (0x11BEB, 8), (0x8D61, 11), (0x833C, 1), (0x8DD9, 1), (0x879A, 1),
                          (0x87B0, 1), (0x87B1, 1)):
        if address not in calibration or len(calibration[address]) != size:
            raise ValueError('the sexy-tamarin equation lacks an explicit curve or configuration byte')
    result = bytearray(before)
    index &= 255
    biased = (before[0x1240 + index] - 0x80) & MASK
    other = (before[0x127E + index] - 0x80) & MASK
    coordinate = before[0x11AE]
    first_table = 0x1252A if index == 0 else 0x12532
    first = curve_byte(image[first_table:first_table + 9], image[0x1302E:0x13036], coordinate)
    result[BASE + 0x36A + index] = first['value']
    first_dividend = ((first['value'] * biased) << 8) & MASK
    first_quotient = division.quotient('signed', DIVISOR, first_dividend)
    mixed = (first_quotient + 0x8000) & MASK
    if sx(mixed) < 0:
        mixed = 0
    if sx(mixed) > 65535:
        mixed = 65535
    result[BASE + 0x86C + index * 2:BASE + 0x86E + index * 2] = (mixed & 65535).to_bytes(2, 'big')
    calls = [dict(site=FIRST_SITE, target=0x21BBC, divisor=DIVISOR, dividend=first_dividend, table=first_table,
                  lookup=first['value'])]
    slot = BASE + 0x838 + index * 4
    level = image[0x8D68]
    if before[BASE + 0x840] & ((index + 1) & 255):
        result[slot:slot + 4] = (0x800000).to_bytes(4, 'big')
    elif not (-level <= sx(biased) <= level):
        factor = image[0x87B0 if index == 0 else 0x87B1]
        side_dividend = ((factor * biased) << 9) & MASK
        side = division.quotient('signed', DIVISOR, side_dividend)
        total = (side + int.from_bytes(result[slot:slot + 4], 'big')) & MASK
        if sx(total) < 0:
            total = 0
        if sx(total) > 0xFFFFFF:
            total = 0xFFFFFF
        result[slot:slot + 4] = total.to_bytes(4, 'big')
        calls.append(dict(site=0xC0E86, target=0x21BBC, divisor=DIVISOR, dividend=side_dividend))
    second_table = 0x123F2 if index == 0 else 0x123FA
    second = curve_byte(image[second_table:second_table + 9], image[0x11BEB:0x11BF3], coordinate)
    result[BASE + 0x34A + index] = second['value']
    second_dividend = (second['value'] * ((biased - other) & MASK)) & MASK
    second_quotient = division.quotient('signed', DIVISOR, second_dividend)
    clamped = (second_quotient + 0x80) & MASK
    if sx(clamped) < 0:
        clamped = 0
    if sx(clamped) > 255:
        clamped = 255
    result[BASE + 0x7FE + index] = clamped & 255
    calls.append(dict(site=SECOND_SITE, target=0x21BBC, divisor=DIVISOR, dividend=second_dividend,
                      table=second_table, lookup=second['value']))
    if -image[0x8D6B] <= sx(biased) <= image[0x8D6B]:
        acc = 0x800000
    else:
        word = int.from_bytes(result[BASE + 0x86C + index * 2:BASE + 0x86E + index * 2], 'big')
        acc = ((((word + 0xFFFF8000) & MASK) << 8) + 0x800000) & MASK
    acc = (acc + ((int.from_bytes(result[slot:slot + 4], 'big') - 0x800000) & MASK)) & MASK
    if not (-image[0x8D65] <= sx(biased) <= image[0x8D65]):
        acc = (acc + (((clamped - 0x80) & MASK) << 16)) & MASK
    if sx(acc) < 0:
        acc = 0
    if sx(acc) > 0xFFFFFF:
        acc = 0xFFFFFF
    result[BASE + 0x880 + index * 4:BASE + 0x884 + index * 4] = acc.to_bytes(4, 'big')
    product = (((acc + 0xFF800000) & MASK) * image[0x833C]) & MASK
    byte_divisor = image[0x8DD9]
    quotient = division.quotient('signed', byte_divisor, product)
    calls.append(dict(site=0xC0FDA, target=0x21BBC, divisor=byte_divisor, dividend=product))
    if sx(quotient) > sx(0xFF800000):
        shaped = 0x0FFFFFFF if sx(quotient) > 0x7FFFFF else ((quotient << 4) + 0x08000000) & MASK
    else:
        shaped = 0
    result[BASE + 0x804 + index * 4:BASE + 0x808 + index * 4] = shaped.to_bytes(4, 'big')
    wide = 0x15AD0 if before[BASE + 0x23C] & ((index + 1) & 255) else 0x15B10
    wide_value = curve_word(image[wide:wide + 40], image[0x149CA:0x149F0], coordinate)
    result[BASE + 0x80C + index * 2:BASE + 0x80E + index * 2] = wide_value.to_bytes(2, 'big')
    grid = image[(0xF38E if index == 0 else 0xF40E):(0xF38E if index == 0 else 0xF40E) + 160]
    first_word = bilinear_word(grid, image[0x1498A:0x1499A], coordinate, image[0x149AA:0x149BA], before[0x2327])
    second_word = bilinear_word(grid, image[0x1498A:0x1499A], coordinate, image[0x149AA:0x149BA], before[0x2324 + index])
    result[BASE + 0x158 + index * 2:BASE + 0x15A + index * 2] = (first_word & 65535).to_bytes(2, 'big')
    result[BASE + 0x154 + index * 2:BASE + 0x156 + index * 2] = (second_word & 65535).to_bytes(2, 'big')
    magnitude = sx(biased)
    if magnitude < 0:
        magnitude = (-magnitude) & MASK
    if magnitude >= image[0x8D61]:
        final = (shar7((((first_word - second_word) & MASK) * ((image[0x879A] - 0x80) & MASK)) & MASK) + (second_word & 65535)) & MASK
        if sx(final) < 0:
            final = 0
        if sx(final) > 65535:
            final = 65535
    else:
        final = second_word & 65535
    result[BASE + 0x7FA + index * 2:BASE + 0x7FC + index * 2] = (final & 65535).to_bytes(2, 'big')
    return dict(memory=bytes(result), calls=tuple(calls), first=first, second=second,
                first_table=first_table, second_table=second_table, dividend=second_dividend,
                first_dividend=first_dividend, divisor=DIVISOR, fault=bytes(result[0x9818:0x981C]))
