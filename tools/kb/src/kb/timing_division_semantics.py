"""Independent word surface, byte curve and timing-composition equations."""


def values(raw,count,width):
    if type(raw) is not bytes or len(raw)!=count*width:
        raise ValueError('the timing equation changes an exact typed calibration extent')
    return tuple(int.from_bytes(raw[index:index+width],'big') for index in range(0,len(raw),width))


def position(knots,coordinate,maximum):
    if (type(coordinate) is not int or not 0<=coordinate<=maximum or len(knots)!=8
            or any(first>=second for first,second in zip(knots,knots[1:]))):
        raise ValueError('the timing equation needs a strict eight-point axis and a bounded coordinate')
    if coordinate<=knots[0]:return 0,0
    if coordinate>=knots[-1]:return 7,0
    index=max(index for index in range(7) if knots[index]<=coordinate)
    return index,((coordinate-knots[index])*65536)//(knots[index+1]-knots[index])


def linear(first,second,fraction):
    if (any(type(value) is not int for value in (first,second,fraction))
            or not 0<=first<=65535 or not 0<=second<=65535 or not 0<=fraction<65536):
        raise ValueError('the timing interpolation equation changes an operand width')
    magnitude=(abs(second-first)*fraction)//65536
    return first+magnitude if second>=first else first-magnitude


def surface(table,outer_axis,inner_axis,outer_value,inner_value):
    cells=values(table,64,2)
    row,rf=position(values(outer_axis,8,2),outer_value,65535)
    column,cf=position(values(inner_axis,8,2),inner_value,65535)
    base=row*8+column
    offsets=[base*2]
    first=cells[base]
    if cf:
        first=linear(first,cells[base+1],cf)
        offsets.append((base+1)*2)
    if rf:
        second=cells[base+8]
        offsets.append((base+8)*2)
        if cf:
            second=linear(second,cells[base+9],cf)
            offsets.append((base+9)*2)
        first=linear(first,second,rf)
    return dict(row=row,column=column,row_fraction=rf,column_fraction=cf,
        value=first,operand_offsets=offsets)


def curve(table_with_neighbor,axis,coordinate):
    cells=values(table_with_neighbor,9,1)
    index,fraction=position(values(axis,8,1),coordinate,255)
    return dict(index=index,fraction=fraction,value=linear(cells[index],cells[index+1],fraction),
        operand_offsets=[index+1,index],semantic_bytes=8,physical_bytes=9)


def signed_byte(value):
    return value-256 if value&128 else value


def caller(calibration,before):
    if type(before) is not bytes or len(before)!=65536:
        raise ValueError('the timing composition requires a complete independent RAM input')
    word=lambda at:int.from_bytes(before[at:at+2],'big')
    bypass=bool(before[0x2458]&32)
    enabled=bool(before[0x41AB]&64) and min(word(0x28B8),word(0x28BA))>=int.from_bytes(calibration[0x9012],'big')
    result=bytearray(before)
    lookup_surface=lookup_curve=None
    dividend=quotient=None
    if bypass:
        composed=before[0x1A7D]+signed_byte(before[0x23EE])-before[0x23C5]-64
        result[0x24D1]|=32
    else:
        selected=0
        if enabled:
            lookup_curve=curve(calibration[0x11F02],calibration[0x11EEA],before[0x106F])
            lookup_surface=surface(calibration[0xC50E],calibration[0x1461A],calibration[0x1464A],
                word(0x10CA),word(0x1024))
            bounded=min(255,lookup_surface['value'])
            dividend=(lookup_curve['value']*word(0x1900)*bounded)&0xFFFFFFFF
            quotient=dividend//500000
            selected=min(255,quotient)
            result[0x1348],result[0x134A],result[0x134C]=bounded,selected,lookup_curve['value']
        result[0x12D4]=selected
        composed=(signed_byte(before[0x23F1])+before[0x23BD]-before[0x23C5]-before[0x12DC]
            -before[0x15EA]+before[0x1A7D]-128+selected)
        result[0x24D1]&=223
    composed=((composed+32768)&65535)-32768
    output=max(-128,min(127,composed))
    result[0x1830]=output&255
    return dict(memory=bytes(result),bypass=bypass,lookup_enabled=enabled and not bypass,
        surface=lookup_surface,curve=lookup_curve,divisor=500000 if quotient is not None else None,
        dividend=dividend,quotient=quotient,composed=composed,output=output)
