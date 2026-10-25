"""Independent signed-curve lookup, zero bypass and clamped quotient equations."""

from kb import division_callees_semantics as division
from kb import timing_denominator_semantics as words


def curve(table, axis, coordinate):
    cells=words.values(table,17,2)
    index,fraction=words.position(words.values(axis,16,2),coordinate,65535)
    return dict(index=index,fraction=fraction,value=words.linear(cells[index],cells[index+1],fraction)&65535,
        operand_offsets=[index*2+2,index*2],semantic_words=16,physical_bytes=34)


def biased(value):
    return (value&65535)-32768


def word(raw,address):
    return int.from_bytes(raw[address:address+2],'big')


def signed_word(raw,address):
    return words.sext16(word(raw,address))


def store(raw,address,value):
    raw[address:address+2]=(value&65535).to_bytes(2,'big')


def floor0(value):
    return value if value>=0 else 0


def quotient(divisor,factor):
    product=factor*800
    result=division.quotient('signed',divisor&0xFFFFFFFF,product&0xFFFFFFFF)
    if result>=0x80000000:
        result-=1<<32
    return 800 if result>800 else result


def caller(calibration,before):
    if type(before) is not bytes or len(before)!=65536 or type(calibration) is not dict:
        raise ValueError('the signed-curve equation needs its complete RAM and calibration inputs')
    for address in (0x18DE6,0x18E06,0x18E26,0x83C1):
        if address not in calibration:
            raise ValueError('the signed-curve equation lacks an explicit table, axis or gate byte')
    coordinate=word(before,0x10BC)
    first=biased(curve(calibration[0x18E06],calibration[0x18E26],coordinate)['value'])
    second_lookup=curve(calibration[0x18DE6],calibration[0x18E26],coordinate)
    second=biased(second_lookup['value'])
    base=0x28F8
    first_term=floor0(signed_word(before,base+0xA94)-first)
    second_term=floor0(signed_word(before,base+0xA96)-first)
    third_term=floor0(signed_word(before,base+0xA9E)-first)
    divisor=floor0(second-first)
    mode=bool(before[0x4214]&0x40)
    stack=word(before,base+0xCF2) if mode else word(before,0x2A7A)
    result=bytearray(before)
    calls=[]
    if divisor==0:
        stored=(800,800,800)
    else:
        stored=tuple(quotient(divisor,factor) for factor in (first_term,second_term,third_term))
        calls=[dict(divisor=divisor,dividend=factor*800,quotient=value,after_delay_slot=True)
               for factor,value in zip((first_term,second_term,third_term),stored)]
    for offset,value in zip((0xD0E,0xD10,0xD12),stored):
        store(result,base+offset,value)
    first_stored=word(result,base+0xD0E)
    chosen=stack if (stack&65535)>=(first_stored&65535) else first_stored
    second_stored=word(result,base+0xD10)
    if (chosen&65535)<(second_stored&65535):
        chosen=second_stored
    third_stored=stored[2]&65535
    if (chosen&65535)>third_stored:
        chosen=third_stored
    chosen&=65535
    low=before[0x4213]
    low=(low&~2)| (2 if chosen==second_stored else 0)
    result[0x4213]=low&255
    high=before[0x4214]
    high=(high&~8)| (8 if chosen==third_stored else 0)
    high=(high&~0x10)| (0 if chosen>0 else 0x10)
    high=(high&~0x20)| (0x20 if chosen>=800 else 0)
    result[0x4214]=high&255
    flag=before[0x4255]
    if calibration[0x83C1][0]&2:
        flag=(flag&~0x10)|(0 if chosen==(stack&65535) else 0x10)
        result[0x4255]=flag&255
        store(result,base+0xCD6,chosen)
    else:
        flag=(flag&~0x10)|(0x10 if before[0x249B]&2 else 0)
        result[0x4255]=flag&255
        store(result,base+0xCD6,word(before,0x2712))
    return dict(memory=bytes(result),active=divisor!=0,zero_bypass=divisor==0,calls=tuple(calls),
        divisor=divisor,stored=stored,output=chosen,curve=second_lookup,
        fault=bytes(result[0x9818:0x981C]))
