"""Independent reciprocal quotient and genuine zero-divisor fault footprint."""

from kb.viridian_armadillo_semantics import curve


def caller(calibration, before, case):
    if type(before) is not bytes or len(before) != 65536:
        raise ValueError('the reciprocal equation needs its complete actual RAM input')
    first = case['kind'] == 'first'
    table, axis = (0x237C4, 0x237B4) if first else (0x23804, 0x237F4)
    looked = curve(calibration[table], calibration[axis], case['coordinate'], 14)
    divisor = looked['value']
    quotient = 256 // divisor if divisor else 0
    after = bytearray(before)
    if not divisor:
        after[0x9818:0x981C] = (0x44E).to_bytes(4, 'big')
    return dict(memory=bytes(after), table=table, axis=axis, lookup=looked,
                divisor=divisor, dividend=256, quotient=quotient,
                site=0x69624 if first else 0x696C8, fault=bytes(after[0x9818:0x981C]))
