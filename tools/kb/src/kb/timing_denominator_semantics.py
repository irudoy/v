"""Independent 16 by 16 word surface, eight-word denominator and clamp equations."""

from kb import division_callees_semantics as division


def values(raw,count,width):
    if type(raw) is not bytes or len(raw)!=count*width:
        raise ValueError('the denominator equation changes an exact typed calibration extent')
    return tuple(int.from_bytes(raw[index:index+width],'big') for index in range(0,len(raw),width))


def position(knots,coordinate,maximum):
    if (type(coordinate) is not int or not 0<=coordinate<=maximum or len(knots) not in (8,16)
            or any(first>=second for first,second in zip(knots,knots[1:]))):
        raise ValueError('the denominator equation needs a strict axis and a bounded coordinate')
    if coordinate<=knots[0]:return 0,0
    if coordinate>=knots[-1]:return len(knots)-1,0
    index=max(index for index in range(len(knots)-1) if knots[index]<=coordinate)
    return index,((coordinate-knots[index])*65536)//(knots[index+1]-knots[index])


def linear(first,second,fraction):
    if (any(type(value) is not int for value in (first,second,fraction))
            or not 0<=first<=65535 or not 0<=second<=65535 or not 0<=fraction<65536):
        raise ValueError('the denominator interpolation equation changes an operand width')
    magnitude=(abs(second-first)*fraction)//65536
    return first+magnitude if second>=first else first-magnitude


def surface(table,row_axis,column_axis,row_value,column_value):
    cells=values(table,256,2)
    row,row_fraction=position(values(row_axis,16,2),row_value,65535)
    column,column_fraction=position(values(column_axis,16,2),column_value,65535)
    base=row*16+column
    offsets=[base*2]
    first=cells[base]
    if column_fraction:
        offsets.append((base+1)*2)
        first=linear(first,cells[base+1],column_fraction)
    if row_fraction:
        second=cells[base+16]
        offsets.append((base+16)*2)
        if column_fraction:
            offsets.append((base+17)*2)
            second=linear(second,cells[base+17],column_fraction)
        first=linear(first,second,row_fraction)
    return dict(row=row,column=column,row_fraction=row_fraction,column_fraction=column_fraction,
        value=first&65535,operand_offsets=offsets)


def curve(table_with_neighbor,axis,coordinate):
    cells=values(table_with_neighbor,9,2)
    index,fraction=position(values(axis,8,2),coordinate,65535)
    return dict(index=index,fraction=fraction,value=linear(cells[index],cells[index+1],fraction)&65535,
        operand_offsets=[index*2+2,index*2],semantic_words=8,physical_bytes=18)


def sext16(value):
    value&=65535
    return value-65536 if value&0x8000 else value


def word(raw,address):
    return int.from_bytes(raw[address:address+2],'big')


def store(raw,address,value):
    raw[address:address+2]=(value&65535).to_bytes(2,'big')


def biased(value):
    return sext16(sext16(value)-32768)


def caller(kind,calibration,before):
    if kind not in ('parent-a','parent-b') or type(before) is not bytes or len(before)!=65536:
        raise ValueError('the denominator equation needs one parent and its complete RAM input')
    if type(calibration) is not dict or 0x83C1 not in calibration:
        raise ValueError('the denominator equation needs its explicit configuration byte')
    parent_a=kind=='parent-a'
    gate=bool(calibration[0x83C1][0]&2)
    row=word(before,0x412A if parent_a else 0x35CE)
    column=word(before,0x11B6)
    curve_coordinate=word(before,0x10BC)
    high=sext16(word(before,0x4138))
    low=sext16(word(before,0x413A if parent_a else 0x35F0))
    override=before[0x41FB if parent_a else 0x4214]
    result=bytearray(before)
    lookup=None
    curve_lookup=None
    unsigned=None
    active=gate and (parent_a or not override&0x30)
    if not gate:
        store(result,0x2C6C if parent_a else 0x35D2,word(before,0x243C if parent_a else 0x1D26))
    elif not parent_a and override&0x10:
        store(result,0x35D2,word(before,0x35F0))
    elif not parent_a and override&0x20:
        store(result,0x35D2,word(before,0x4138))
    else:
        if parent_a:
            lookup=surface(calibration[0xC98E],calibration[0x13478],calibration[0x13498],row,column)
            curve_lookup=curve(calibration[0x14AFA],calibration[0x134B8],curve_coordinate)
            surface_at,curve_at,ratio_at,final_at=0x2C6E,0x2CFE,0x2CFD,0x2C6C
        else:
            lookup=surface(calibration[0x16948],calibration[0x18846],calibration[0x18866],row,column)
            curve_lookup=curve(calibration[0x18DD6],calibration[0x18886],curve_coordinate)
            surface_at,curve_at,ratio_at,final_at=0x35D0,0x35D8,0x35D6,0x35D2
        denominator=curve_lookup['value']
        store(result,surface_at,biased(lookup['value']))
        store(result,curve_at,denominator)
        dividend=(row*255)&0xFFFFFFFF
        if denominator==0:
            ratio=255
        else:
            quotient=dividend//denominator
            unsigned=dict(divisor=denominator,dividend=dividend,quotient=quotient,after_delay_slot=True)
            ratio=255 if quotient>255 else quotient
        result[ratio_at]=ratio
        product=sext16(word(before,0x413A if parent_a else 0x35F0))*(255-ratio)
        signed=sext16(division.quotient('signed',255,product&0xFFFFFFFF))
        total=biased(lookup['value'])+signed
        if parent_a:
            if total>high:total=high
            if total<low:total=low
            if override&0x20:total=high
            if override&0x10:total=low
        elif total>high:
            total=high
        elif total<low:
            total=low
        store(result,final_at,total)
    return dict(memory=bytes(result),active=active,gate=gate,zero_bypass=bool(active and curve_lookup and curve_lookup['value']==0),
        surface=lookup,curve=curve_lookup,unsigned=unsigned,output=word(bytes(result),0x2C6C if parent_a else 0x35D2),
        fault=bytes(result[0x9818:0x981C]))
