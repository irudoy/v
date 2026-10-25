"""Independent 32-knot lookup and the signed call that does not consume it."""

from kb import division_callees_semantics as division

ENTRY=0xB784E
SITE=0xB7892
DIVISOR=0xF4240
BASE=0x28F8
POINTER=0x3000


def sext16(value):
    value&=65535
    return value-65536 if value&0x8000 else value


def words(raw):
    if len(raw)!=66:
        raise ValueError('the uptight-duck curve needs 32 semantic words and one physical neighbor')
    return tuple(int.from_bytes(raw[index:index+2],'big') for index in range(0,66,2))


def axis_words(raw):
    if len(raw)!=64:
        raise ValueError('the uptight-duck axis needs 32 explicit knots')
    return tuple(int.from_bytes(raw[index:index+2],'big') for index in range(0,64,2))


def scan(axis, coordinate):
    offset=origin=62
    while True:
        knot=axis[offset//2]
        if knot==coordinate:
            return offset, 0
        if coordinate>knot:
            if offset==origin:
                return offset, 0
            upper=axis[offset//2+1]
            dividend=((coordinate-knot)&0xFFFFFFFF)<<16
            divisor=(upper-knot)&0xFFFFFFFF
            return offset, division.quotient('unsigned', divisor, dividend&0xFFFFFFFF)&65535
        offset-=2
        if offset<0:
            return 0, 0


def lookup(table, axis, coordinate):
    cells, knots=words(table), axis_words(axis)
    offset, fraction=scan(knots, coordinate&65535)
    index=offset//2
    first, second=cells[index], cells[index+1]
    if second>=first:
        value=first+(((fraction*(second-first))&0xFFFFFFFF)>>16)
    else:
        value=first-(((fraction*(first-second))&0xFFFFFFFF)>>16)
    return dict(value=value&65535, offsets=(index*2+2, index*2), fraction=fraction)


def caller(calibration, before, dividend, coordinate):
    if type(before) is not bytes or len(before)!=65536 or type(dividend) is not int or not 0<=dividend<=0xFFFFFFFF:
        raise ValueError('the uptight-duck equation needs its complete RAM input and a 32-bit dividend')
    for address, size in ((0x15BF0,66),(0x15C40,64),(0x15C80,66),(0x13CA8,64),(0x8C8C,1)):
        if address not in calibration or len(calibration[address])!=size:
            raise ValueError('the uptight-duck equation lacks an explicit table, axis or threshold byte')
    second_table=calibration[0x15C40]+calibration[0x15C80][:2]
    first=lookup(calibration[0x15BF0], calibration[0x13CA8], coordinate)
    second=lookup(second_table, calibration[0x13CA8], coordinate)
    third=lookup(calibration[0x15C80], calibration[0x13CA8], coordinate)
    quotient=division.quotient('signed', DIVISOR, dividend)
    if quotient>=0x80000000:
        quotient-=1<<32
    threshold=sext16(calibration[0x8C8C][0]-0x32)
    chosen=third['value'] if sext16(quotient)>=threshold else 1
    result=bytearray(before)
    result[POINTER:POINTER+2]=second['value'].to_bytes(2,'big')
    base=BASE
    result[base+0xCBC:base+0xCBE]=second['value'].to_bytes(2,'big')
    result[base+0xCBE:base+0xCC0]=(chosen&65535).to_bytes(2,'big')
    side=first['value'] if first['value']>=1 else 1
    result[base+0xCA8:base+0xCAA]=(side&65535).to_bytes(2,'big')
    return dict(memory=bytes(result), first=first, second=second, third=third, chosen=chosen&65535,
        divisor=DIVISOR, dividend=dividend, quotient=quotient&0xFFFFFFFF,
        call=dict(site=SITE, target=0x21BBC, divisor=DIVISOR, dividend=dividend, after_delay_slot=True),
        fault=bytes(result[0x9818:0x981C]))
