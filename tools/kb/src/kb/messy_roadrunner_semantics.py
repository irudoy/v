"""Independent byte interpolation, product64/125 and saturated-base equations."""

from kb.spirited_hamster_semantics import curve


def caller(calibration, before, word):
    if (type(before) is not bytes or len(before) != 65536 or set(calibration) != {0x11F3A, 0x11AEF}
            or type(word) is not int or not 0 <= word <= 65535):
        raise ValueError('the byte correction lacks its exact curve, word coordinate or full RAM')
    looked = curve(calibration[0x11F3A], calibration[0x11AEF], word >> 8)
    dividend = looked['value'] * 64
    quotient = dividend // 125
    total = int.from_bytes(before[0x8E08:0x8E0A], 'big') + quotient
    saturated = total > 0x8041
    output = 65535 if saturated else total + 0x7FBE
    after = bytearray(before)
    after[0x8EC0:0x8EC4] = total.to_bytes(4, 'big')
    after[0x8FDE:0x8FE0] = output.to_bytes(2, 'big')
    return dict(memory=bytes(after), lookup=looked['value'], reads=looked['reads'], divisor=125,
                dividend=dividend, quotient=quotient, total=total, output=output, saturated=saturated,
                fault=bytes(after[0x9818:0x981C]))
