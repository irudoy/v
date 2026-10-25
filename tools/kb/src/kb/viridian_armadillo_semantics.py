"""Independent viridian-armadillo: the word lookup scales one signed dividend."""

from kb import division_callees_semantics as division

ENTRY = 0xB7A3C
SITE = 0xB7AE8
CONSTANT_DIVISOR = 0x4E20
MASK = 0xFFFFFFFF


def sx(value):
    return value - 0x100000000 if value & 0x80000000 else value


def exts_w(value):
    value &= 65535
    if value & 0x8000:
        value -= 0x10000
    return value & MASK


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


def linear(first, second, fraction):
    if second >= first:
        return (first + (((fraction * ((second - first) & MASK)) & MASK) >> 16)) & MASK
    return (first - (((fraction * ((first - second) & MASK)) & MASK) >> 16)) & MASK


def curve(table, axis, coordinate, origin):
    if len(table) < origin + 4 or len(axis) < origin + 2:
        raise ValueError('the viridian-armadillo curve needs the selected knot and its neighbor')
    offset, fraction = scan_word(axis, coordinate & 65535, origin)
    value = linear(word_at(table, offset), word_at(table, offset + 2), fraction) & 65535
    return dict(value=value, offsets=(offset + 2, offset))


def overlay(image, calibration):
    raw = bytearray(image)
    for address, data in calibration.items():
        raw[address:address + len(data)] = data
    return bytes(raw)


def caller(image, calibration, before, incoming):
    if type(before) is not bytes or len(before) != 65536 or type(image) is not bytes:
        raise ValueError('the viridian-armadillo equation needs its complete image and RAM input')
    for address, size in ((0x14E42, 18), (0x13BB8, 16), (0x8832, 1), (0x8A30, 7)):
        if address not in calibration or len(calibration[address]) != size:
            raise ValueError('the viridian-armadillo equation lacks the curve, its axis or the ROM factor')
    image = overlay(image, calibration)
    r4, r5, r6, r7, fifth = (incoming[name] & MASK for name in ('divisor', 'selector', 'dividend', 'scale', 'coordinate'))
    result = bytearray(before)
    quotient = division.quotient('signed', CONSTANT_DIVISOR, r6)
    adjusted = (quotient - ((r7 & 255) * 0x32)) & MASK
    if sx(adjusted) > 0x763B:
        mixed = 0x7FFF
    elif sx(adjusted) >= sx(0xFFFF763C):
        mixed = (adjusted + 0x9C4) & MASK
    else:
        mixed = 0xFFFF8000
    mixed = exts_w(mixed)
    if sx(mixed) < 0:
        mixed = 0
    stage = mixed & 65535
    lookup = curve(image[0x14E42:0x14E54], image[0x13BB8:0x13BC8], (fifth & 255) << 8, 14)
    scale = stage * image[0x8A30]
    narrowed = 0xFFFFFFFF if scale > 0x1FFFE else (scale >> 1) & MASK
    calls = [dict(site=0xB7A62, target=0x21BBC, divisor=CONSTANT_DIVISOR, dividend=r6)]
    divisor = r4 & 65535
    product = (((-lookup['value']) & MASK) * image[0x8832]) & MASK
    signed_dividend = (product * 20) & MASK
    if divisor:
        signed = division.quotient('signed', divisor, signed_dividend)
        calls.append(dict(site=SITE, target=0x21BBC, divisor=divisor, dividend=signed_dividend, lookup=lookup['value']))
        shaped = (signed - 1) & MASK if sx(signed) >= sx(0xFFFF0001) else 0
    else:
        shaped = 0xFFFFFFFF if sx(product) >= 0 else 0
    second = curve(image[0x151F2:0x15216], image[0x13BF8:0x13C18], shaped & 65535, 30)
    negated = (-(second['value'] & 65535)) & MASK
    prepared = (negated - 1) & MASK if sx(negated) >= sx(0xFFFFFF01) else 0
    selector = min(((r5 & 255) + 1), 4)
    chosen = {1: 0x0A, 2: image[0x8A35], 3: image[0x8A36], 4: image[0x8A34]}[selector]
    first_dividend = ((prepared & 255) * (narrowed & 65535)) & MASK
    first_quotient = division.quotient('unsigned', 255, first_dividend)
    calls.append(dict(site=0xB7B6C, target=0x21CE0, divisor=255, dividend=first_dividend))
    second_dividend = (divisor * (first_quotient & 65535)) & MASK
    second_quotient = division.quotient('unsigned', 0x9C4, second_dividend)
    calls.append(dict(site=0xB7B78, target=0x21CE0, divisor=0x9C4, dividend=second_dividend))
    result[0x3228:0x322C] = (((second_quotient & MASK) * (chosen & 255)) & MASK).to_bytes(4, 'big')
    return dict(memory=bytes(result), calls=tuple(calls), lookup=lookup, dividend=signed_dividend,
                divisor=divisor, factor=image[0x8832], fault=bytes(result[0x9818:0x981C]))
