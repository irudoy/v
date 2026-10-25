"""Independent difference divisor, signed product and bounded output equations."""

from kb import division_callees_semantics as division
from kb.arrogant_catfish_semantics import curve


def caller(calibration, before):
    if type(before) is not bytes or len(before) != 65536 or set(calibration) != {0x12738, 0x12748, 0x12930}:
        raise ValueError('the differential-curve equation lacks its exact curves or complete RAM')
    coordinate = before[0x106F]
    looked = {at: curve(raw, coordinate) for at, raw in calibration.items()}
    first, second, coefficient = (looked[at]['value'] for at in (0x12738, 0x12748, 0x12930))
    opened = first > second
    divisor = first - second if opened else None
    dividend = (coefficient * (first - before[0x16AB])) & 0xFFFFFFFF if opened else None
    quotient = division.quotient('signed', divisor, dividend) if opened else None
    if quotient is not None and quotient & 0x80000000:
        quotient -= 0x100000000
    output = max(0, min(255, quotient)) if opened else 0
    after = bytearray(before)
    after[0x171D] = output
    return dict(memory=bytes(after), lookups=looked, divisor=divisor, dividend=dividend,
                opened=opened, quotient=quotient, output=output, fault=bytes(after[0x9818:0x981C]))
