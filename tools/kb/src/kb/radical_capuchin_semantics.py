"""The table is the comparison threshold, independent of timer/10 operands."""

from kb.spirited_hamster_semantics import curve


def caller(calibration, before):
    if type(before) is not bytes or len(before) != 65536 or set(calibration) != {0x12362, 0x12FDE}:
        raise ValueError('the comparison lacks its exact threshold curve, axis or full RAM')
    looked = curve(calibration[0x12362], calibration[0x12FDE], before[0x2773])
    timer = int.from_bytes(before[0x8C90:0x8C92], 'big')
    quotient = timer // 10
    output = int(looked['value'] >= quotient)
    after = bytearray(before)
    after[0x8CB4:0x8CB8] = output.to_bytes(4, 'big')
    return dict(memory=bytes(after), lookup=looked['value'], reads=looked['reads'], divisor=10,
                dividend=timer, quotient=quotient, output=output, fault=bytes(after[0x9818:0x981C]))
