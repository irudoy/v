"""Independent paired differences, conditional normalization and byte clamp."""

from kb.arrogant_catfish_semantics import curve


def caller(calibration, before, coordinate):
    if (type(before) is not bytes or len(before) != 65536 or set(calibration) != {0x12798, 0x127D8}
            or type(coordinate) is not int or not 0 <= coordinate <= 255):
        raise ValueError('the paired normalization lacks its exact curves, coordinate or full RAM')
    first = curve(calibration[0x12798], coordinate)
    second = curve(calibration[0x127D8], coordinate)
    first_anchor = curve(calibration[0x12798], 128)
    second_anchor = curve(calibration[0x127D8], 128)
    difference = first['value'] - second['value']
    anchor_difference = first_anchor['value'] - second_anchor['value']
    opened = difference > 0
    divided = opened and anchor_difference > 0
    dividend = difference << 8 if opened else None
    divisor = anchor_difference if divided else None
    quotient = dividend // divisor if divided else None
    intermediate = quotient if divided else dividend if opened else 0
    output = min(255, intermediate)
    after = bytearray(before)
    after[0x2236] = output
    return dict(memory=bytes(after), first=first, second=second, first_anchor=first_anchor,
        second_anchor=second_anchor, difference=difference, anchor_difference=anchor_difference,
        opened=opened, divided=divided, dividend=dividend, divisor=divisor, quotient=quotient,
        intermediate=intermediate, output=output, mode=before[0x2459] & 32,
        fault=bytes(after[0x9818:0x981C]))
