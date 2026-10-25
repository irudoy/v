"""Independent conditional curve, coefficient and bounded timing argument equations."""

from kb import timing_division_semantics as byte_numeric,ignition_diagnostic_semantics as word_numeric


def caller(calibration,before):
    if type(before) is not bytes or len(before)!=65536:
        raise ValueError('the timing-tail equation needs its complete exact RAM input')
    word=lambda at:int.from_bytes(before[at:at+2],'big')
    minimum=min(word(0x28B8),word(0x28BA))
    coefficient=max(minimum-7350,0)
    enabled=bool(before[0x41AB]&64) and minimum>=int.from_bytes(calibration[0x9010],'big')
    after=bytearray(before);after[0x1900:0x1902]=coefficient.to_bytes(2,'big')
    curve=amplitude=None;dividend=quotient=None;selected=0
    if enabled:
        curve=byte_numeric.curve(calibration[0x11EFA],calibration[0x11EEA],before[0x106F])
        amplitude=word_numeric.word_curve(calibration[0x147CA],calibration[0x1460A],word(0x10CA))
        bounded=min(amplitude['value'],255)
        dividend=(curve['value']*coefficient*bounded)&0xFFFFFFFF
        quotient=dividend//500000;selected=min(255,quotient)
        after[0x1347],after[0x1349],after[0x134B]=bounded,selected,curve['value']
    after[0x12D5]=selected
    return dict(memory=bytes(after),minimum=minimum,coefficient=coefficient,lookup_enabled=enabled,
        byte_curve=curve,word_curve=amplitude,divisor=500000 if enabled else None,
        dividend=dividend,quotient=quotient,output=selected)
