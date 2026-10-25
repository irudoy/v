"""Independent APC reset offset: byte lookup factor and signed quotient."""

from kb import division_callees_semantics as division

ENTRY=0x4C1E4
SIGNED_SITE=0x4C34E
UNSIGNED_SITE=0x4C2BA
DIVISOR=0x14000


def u16(raw,address):
    return int.from_bytes(raw[address:address+2],'big')


def put8(raw,address,value):
    raw[address]=value&255


def fraction(low,bits):
    value=low&((1<<bits)-1)
    assembled=0
    for _ in range(bits):
        bit=value&1
        value>>=1
        assembled=((assembled>>1)|(bit<<31))&0xFFFFFFFF
    return ((assembled&65535)<<16)|(assembled>>16)


def curve(table,coordinate):
    if len(table)!=8:
        raise ValueError('the APC reset curve needs eight explicit bytes')
    coordinate&=255
    if coordinate>=224:
        return dict(value=table[7],offsets=(7,))
    index=coordinate>>5
    weight=fraction(coordinate,5)
    first,second=table[index],table[index+1]
    if second>=first:
        value=first+(((weight*(second-first))&0xFFFFFFFF)>>16)
    else:
        value=first-(((weight*(first-second))&0xFFFFFFFF)>>16)
    return dict(value=value&255,offsets=(index,index+1))


def clamp_byte(value,high,low):
    value&=255
    if value>high:value=high
    return value if value>=low else low


def caller(calibration,before):
    if type(before) is not bytes or len(before)!=65536:
        raise ValueError('the APC reset equation needs its complete RAM input')
    for address,size in ((0x1208E,8),(0x12096,8),(0x851F,7),(0x8291,1),(0x828A,1),(0x959A,2),(0x8B87,2)):
        if address not in calibration or len(calibration[address])!=size:
            raise ValueError('the APC reset equation lacks an explicit curve or configuration byte')
    config=calibration[0x851F]
    gate=bool(before[0x4184]&0x40)
    if gate:
        factor=((config[1]<<3)&0xFFFFFFFF)
        side=calibration[0x8291][0]
        adjusted=u16(before,0x10CA)>>2
        source=255 if adjusted>255 else adjusted
    else:
        factor=(config[0]*3)&0xFFFFFFFF
        side=calibration[0x828A][0]
        source=before[0x11AE]
    primary=clamp_byte(source,config[3],config[4])
    secondary=before[0x1108]
    if secondary<config[6]:secondary=config[6]
    result=bytearray(before)
    put8(result,0x144C,primary)
    put8(result,0x1450,secondary)
    calls=[]
    if secondary:
        scale=(primary*config[5]*6)&0xFFFFFFFF
        dividend=(primary*int.from_bytes(calibration[0x959A],'big')*6)&0xFFFFFFFF
        divisor=(secondary*secondary)&0xFFFFFFFF
        quotient=division.quotient('unsigned',divisor,dividend)
        calls.append(dict(site=UNSIGNED_SITE,target=0x21CE0,divisor=divisor,dividend=dividend,quotient=quotient,
            after_delay_slot=True))
        mixed=(quotient+scale)&0xFFFFFFFF
        if gate:
            mixed=((mixed*config[2]*10)>>8)&0xFFFFFFFF
    else:
        mixed=(primary*(config[5]+65535)*6)&0xFFFFFFFF
    mixed=(mixed+(side&255))&0xFFFFFFFF
    if mixed>calibration[0x8B87][0]:mixed=calibration[0x8B87][0]
    if mixed<calibration[0x8B87][1]:mixed=calibration[0x8B87][1]
    put8(result,0x1874,mixed)
    first=curve(calibration[0x1208E],primary)
    second=curve(calibration[0x12096],secondary)
    put8(result,0x144D,first['value'])
    put8(result,0x1451,second['value'])
    product=((factor&0xFFFFFFFF)*first['value'])&0xFFFFFFFF
    signed_dividend=(product*second['value'])&0xFFFFFFFF
    signed=division.quotient('signed',DIVISOR,signed_dividend)
    if signed>=0x80000000:signed-=1<<32
    published=255 if (signed&0xFFFFFFFF)>255 else signed&255
    put8(result,0x1875,published)
    chosen=published if mixed>published else mixed
    put8(result,0x2406,0x18 if before[0x4251]&1 else chosen)
    calls.append(dict(site=SIGNED_SITE,target=0x21BBC,divisor=DIVISOR,dividend=signed_dividend,
        quotient=signed&0xFFFFFFFF,after_delay_slot=True,lookup=first['value']))
    return dict(memory=bytes(result),calls=tuple(calls),first=first,second=second,factor=factor&0xFFFFFFFF,
        dividend=signed_dividend,divisor=DIVISOR,fault=bytes(result[0x9818:0x981C]),chosen=chosen&255)
