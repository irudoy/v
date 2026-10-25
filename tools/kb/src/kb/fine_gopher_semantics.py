"""Independent fine-gopher lookups, scaled dividends and zero-divisor bypass."""

from kb import division_callees_semantics as division
from kb import timing_denominator_semantics as words

GBR=0x8C54
BLOCK=0x99FC
ENTRY=0x6062C
OPEN=(0x14F42,0x14F52,0x15002)


def u16(raw,address):
    return int.from_bytes(raw[address:address+2],'big')


def u32(raw,address):
    return int.from_bytes(raw[address:address+4],'big')


def s8(raw,address):
    value=raw[address]
    return value-256 if value&128 else value


def put8(raw,address,value):
    raw[address]=value&255


def put16(raw,address,value):
    raw[address:address+2]=(value&65535).to_bytes(2,'big')


def put32(raw,address,value):
    raw[address:address+4]=(value&0xFFFFFFFF).to_bytes(4,'big')


def curve(table,axis,coordinate):
    return words.curve(table,axis,coordinate)


def neighbor(head,tail):
    if len(head)!=16 or len(tail)<2:
        raise ValueError('the fine-gopher curve extent changes its eight semantic words or physical neighbor')
    return head+tail[:2]


def clamp(left,right):
    diff=left-right
    if diff>127:signed=127
    elif diff<-128:signed=-128
    else:signed=diff
    if signed>=0:
        return signed&255,signed&255,diff&65535
    magnitude=(-signed)&65535
    return signed&255,magnitude&255,magnitude


def scale(product):
    if (product&0xFFFFFFFF)>0x3FFFC0:return 65535
    return (product&0xFFFFFFFF)>>6


def udiv(dividend,divisor):
    return division.quotient('unsigned',divisor&0xFFFFFFFF,dividend&0xFFFFFFFF)


def wrapped(base,addend):
    total=(base+addend)&0xFFFFFFFF
    return (0xFFFFFFFF,True) if total<base else (total,False)


def caller(calibration,before):
    if type(before) is not bytes or len(before)!=65536 or type(calibration) is not dict:
        raise ValueError('the fine-gopher equation needs its complete RAM and calibration inputs')
    for address,size in ((0x1453A,16),(0x1454A,18),(0x14F42,16),(0x14F52,18),(0x15002,16),(0x15012,18),
                         (0x13C58,16),(0x13C38,16),(0x13BD8,16),(0x13BE8,16),(0x93E8,2),(0x93EC,2),(0x9066,2)):
        if address not in calibration or len(calibration[address])!=size:
            raise ValueError('the fine-gopher equation lacks an explicit table, axis or divisor word')
    coordinate=u16(before,0x11F4)
    byte_coordinate=before[0x1076]
    rare=curve(neighbor(calibration[0x14F42],calibration[0x14F52]),calibration[0x13C58],coordinate)
    ochre=curve(calibration[0x14F52],calibration[0x13C58],coordinate)
    signed,magnitude,raw_word=clamp(s8(before,0x11D4),s8(before,0x2365))
    first_factor=curve(neighbor(calibration[0x1453A],calibration[0x1454A]),calibration[0x13C38],magnitude)
    second_factor=curve(calibration[0x1454A],calibration[0x13C38],magnitude)
    product=(u16(before,0x1026)*u16(before,0x22E6))&0xFFFFFFFF
    first_quotient=udiv(product,0x20202)
    first_scaled=scale(first_quotient*first_factor['value'])
    rare_dividend=(first_scaled*rare['value'])&0xFFFFFFFF
    rare_quotient=udiv(rare_dividend,0x3FC)
    rare_word=65535 if rare_quotient>65535 else rare_quotient
    second_scaled=scale(first_quotient*second_factor['value'])
    ochre_dividend=(second_scaled*ochre['value'])&0xFFFFFFFF
    ochre_quotient=udiv(ochre_dividend,0x3FC)
    ochre_word=65535 if ochre_quotient>65535 else ochre_quotient
    tail_dividend=(ochre_word*0x139B)&0xFFFFFFFF
    tail_quotient=udiv(tail_dividend,0x1388)
    flag=1 if before[0x4185]&0x40 else 0
    block0,block8,blockc=u32(before,BLOCK),u32(before,BLOCK+8),u32(before,BLOCK+0xC)
    block10,block14=u32(before,BLOCK+0x10),u32(before,BLOCK+0x14)
    block18,block1a,block1c=u16(before,BLOCK+0x18),u16(before,BLOCK+0x1A),u16(before,BLOCK+0x1C)
    block20,block24=u32(before,BLOCK+0x20),u32(before,BLOCK+0x24)
    limit=int.from_bytes(calibration[0x9066],'big')
    if block20==0:
        if flag==0 and block24!=0:block20=1
    elif block0==0:
        if block1c<limit:block1c=(block1c+1)&65535
        else:block0=1
    result=bytearray(before)
    calls=[]
    def record(site,divisor,dividend,quotient):
        calls.append(dict(site=site,target=0x21CE0,divisor=divisor&0xFFFFFFFF,dividend=dividend&0xFFFFFFFF,
            quotient=quotient&0xFFFFFFFF,after_delay_slot=True))
    record(0x606DA,0x20202,product,first_quotient)
    record(0x60710,0x3FC,rare_dividend,rare_quotient)
    record(0x60784,0x20202,product,first_quotient)
    record(0x607B6,0x3FC,ochre_dividend,ochre_quotient)
    record(0x607D4,0x1388,tail_dividend,tail_quotient)
    put8(result,GBR+0x24,flag)
    put16(result,GBR+0x22,raw_word)
    put8(result,GBR+0x38,signed);put8(result,GBR+0x34,signed)
    put8(result,GBR+0x39,magnitude);put8(result,GBR+0x35,magnitude)
    put16(result,0x401C+0x18,rare['value']);put16(result,0x401C+0x1A,ochre['value'])
    put16(result,0x401C+0x0E,first_factor['value']);put16(result,0x401C+0x10,second_factor['value'])
    put16(result,GBR+0x20,first_scaled);put16(result,GBR+0x1E,second_scaled)
    put16(result,0x401C+0x34,rare_word);put16(result,GBR+0x1C,ochre_word)
    put16(result,0x401C+0x4A,tail_quotient)
    put32(result,BLOCK+4,flag);put32(result,BLOCK+0x24,flag)
    put32(result,BLOCK,block0);put32(result,BLOCK+0x20,block20);put16(result,BLOCK+0x1C,block1c)
    if block0==0:join=block14
    else:
        join,overflow=wrapped(block10,block1a)
        put32(result,GBR+0x10,join)
    put32(result,GBR+0x28,block0);put32(result,GBR+0x0C,join)
    beetle=None
    if join==0:
        beetle=curve(neighbor(calibration[0x15002],calibration[0x15012]),calibration[0x13BD8],byte_coordinate)
        beetle_value=(beetle['value']*255)&0xFFFFFFFF
    else:beetle_value=join
    put32(result,0x401C+0x40,beetle_value)
    divisor=int.from_bytes(calibration[0x93E8],'big')
    if divisor==0:beetle_byte=255
    else:
        beetle_quotient=udiv(beetle_value,divisor)
        record(0x608C2,divisor,beetle_value,beetle_quotient)
        beetle_byte=255 if beetle_quotient>255 else beetle_quotient
    put8(result,GBR+0x3B,beetle_byte);put8(result,GBR+0x3A,(~beetle_byte)&255)
    put8(result,0x288C+5,(~beetle_byte)&255)
    put32(result,GBR+0x30,1 if beetle_byte==255 else 0)
    if block0==0:second=blockc
    else:
        second,overflow=wrapped(block8,block18)
        put32(result,GBR+8,second)
    put32(result,GBR+4,second)
    paired=None
    if second==0:
        paired=curve(calibration[0x15012],calibration[0x13BE8],byte_coordinate)
        second_value=(paired['value']*0x42F)&0xFFFFFFFF
    else:second_value=second
    put32(result,GBR,second_value)
    rom_ec=int.from_bytes(calibration[0x93EC],'big')
    put32(result,GBR+0x14,rom_ec<<8)
    if rom_ec==0:second_byte=255
    else:
        first=udiv(second_value,0x42F)
        put16(result,0x401C+0x48,first)
        record(0x6095A,0x42F,second_value,first)
        dividend=((first&65535)*255*16)&0xFFFFFFFF
        second_quotient=udiv(dividend,rom_ec<<8)
        put32(result,GBR+0x18,second_quotient)
        record(0x60972,rom_ec<<8,dividend,second_quotient)
        second_byte=255 if second_quotient>255 else second_quotient
    put8(result,GBR+0x37,second_byte);put8(result,GBR+0x36,(~second_byte)&255)
    put8(result,0x288C+6,(~second_byte)&255)
    put32(result,GBR+0x2C,1 if second_byte==255 else 0)
    put32(result,BLOCK+0x14,beetle_value);put16(result,BLOCK+0x1A,rare_word)
    put32(result,BLOCK+0x10,beetle_value);put32(result,BLOCK+0xC,second_value);put32(result,BLOCK+8,second_value)
    put16(result,BLOCK+0x18,tail_quotient)
    port=before[0x423E]
    port=(port&~0x02)|(0x02 if block0 else 0)
    port=(port&~0x20)|(0x20 if second_byte==255 else 0)
    port=(port&~0x40)|(0x40 if beetle_byte==255 else 0)
    put8(result,0x423E,port)
    return dict(memory=bytes(result),calls=tuple(calls),fault=bytes(result[0x9818:0x981C]),
        rare=rare,ochre=ochre,beetle=beetle,paired=paired,
        rare_call=calls[1],ochre_call=calls[3],
        beetle_call=next((row for row in calls if row['site']==0x608C2),None),
        beetle_lookup=beetle is not None,zero_bypass=beetle is not None and divisor==0,
        beetle_byte=beetle_byte,second_byte=second_byte,flag=flag,block0=block0)
