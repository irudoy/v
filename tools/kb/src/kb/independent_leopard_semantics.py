"""Independent two-step byte lookup and constant-100 unsigned division."""

from kb import division_callees_semantics as division

ENTRY=0x5AC54
SITE=0x5AD62
BIAS=500
DIVISOR=100


def u16(raw,address):
    return int.from_bytes(raw[address:address+2],'big')


def put8(raw,address,value):
    raw[address]=value&255


def put16(raw,address,value):
    raw[address:address+2]=(value&65535).to_bytes(2,'big')


def sext16(value):
    value&=65535
    return value-65536 if value&0x8000 else value


def coordinate(byte):
    shifted=((byte-0x68)<<1)&0xFFFFFFFF if byte>=0x68 else 0
    return 255 if shifted>255 else shifted


def fraction(low):
    value=low&63
    assembled=0
    for _ in range(6):
        bit=value&1
        value>>=1
        assembled=((assembled>>1)|(bit<<31))&0xFFFFFFFF
    return ((assembled&65535)<<16)|(assembled>>16)


def curve(table,coordinate_value):
    if len(table)!=4 or any(byte>255 for byte in table):
        raise ValueError('the independent-leopard curve needs four explicit bytes')
    coordinate_value&=255
    if coordinate_value>=192:
        return dict(value=table[3],offsets=(3,),saturated=True)
    index=coordinate_value>>6
    weight=fraction(coordinate_value)
    first,second=table[index],table[index+1]
    if second>=first:
        amount=((weight*(second-first))&0xFFFFFFFF)>>16
        value=first+amount
    else:
        amount=((weight*(first-second))&0xFFFFFFFF)>>16
        value=first-amount
    return dict(value=value&255,offsets=(index,index+1),saturated=False)


def caller(calibration,before):
    if type(before) is not bytes or len(before)!=65536 or type(calibration) is not dict:
        raise ValueError('the independent-leopard equation needs its complete RAM and calibration inputs')
    for address in (0x12522,0x12526):
        if address not in calibration or len(calibration[address])!=4:
            raise ValueError('the independent-leopard equation lacks an explicit four-byte curve')
    result=bytearray(before)
    calls=[]
    lookups=[]
    for index in (0,1):
        left=u16(before,0x288C+2*index)
        right=u16(before,0x4020+2*index)
        difference=(left-right)&0xFFFFFFFF
        put16(result,0x40A8+2*index,difference)
        point=coordinate(before[0x3529+index])
        negative=sext16(difference)<0
        table=calibration[0x12526 if negative else 0x12522]
        looked=curve(table,point)
        factor=(-difference)&0xFFFFFFFF if negative else difference
        dividend=(looked['value']*factor)&0xFFFFFFFF
        quotient=division.quotient('unsigned',DIVISOR,dividend)
        calls.append(dict(site=SITE,target=0x21CE0,divisor=DIVISOR,dividend=dividend,quotient=quotient,
            after_delay_slot=True,index=index,table=0x12526 if negative else 0x12522))
        lookups.append(looked)
        put8(result,0x409C+index,looked['value'])
        if sext16(difference)>=0:
            total=(BIAS+quotient)&0xFFFFFFFF
            stored=0xFFFFFFFF if total>65535 else total
        else:
            stored=(BIAS-quotient)&0xFFFFFFFF
        put16(result,0x40A4+2*index,stored)
    open_calls=tuple(row for row in calls if row['table']==0x12522)
    return dict(memory=bytes(result),calls=tuple(calls),open_calls=open_calls,lookups=tuple(lookups),
        fault=bytes(result[0x9818:0x981C]),bias=BIAS,divisor=DIVISOR)
