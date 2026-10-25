"""Independent full caller equations and physical coolant-coordinate operands."""

RAM_BASE=0x01000000
MASK=0xFFFFFFFF


def signed(value,bits):
    return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(memory,calibration,frame_before):
    if (type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192):
        raise ValueError('the coolant-coordinate equations require complete incoming RAM and frame')
    after=bytearray(memory)
    operands,calls,tails,lookups=[],[],[],[]

    def read(site,address,width,register,domain='ram'):
        if domain=='ram':
            raw=bytes(after[address:address+width])
        else:
            spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
            if len(spans)!=1:
                raise ValueError('the coolant-coordinate equations lose an exact physical ROM span')
            at,data=spans[0]
            if type(data) is not bytes:
                raise ValueError('the coolant-coordinate equations replace immutable calibration')
            raw=data[address-at:address-at+width]
        operands.append(dict(site=site,mode='read',address=RAM_BASE+address if domain=='ram' else address,
            width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        return int.from_bytes(raw,'big')

    def write(site,address,width,value,register):
        raw=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        after[address:address+width]=raw
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=raw.hex()))

    def call(site,target,arguments,sp_delta,returned=None):
        row=dict(site=site,target=target,arguments=arguments,sp_delta=sp_delta,return_address=site+4)
        if returned is not None:row['returned']=returned
        calls.append(row)
        return row

    def linear(first,second,fraction):
        delta=abs(second-first)*fraction//65536
        return first+delta if second>=first else first-delta

    def interpolate(site,first,second,fraction,sp_delta):
        value=linear(first,second,fraction)
        call(site,0x26740,{0:first,2:second,3:fraction},sp_delta,{0:value})
        return value

    coolant=read(0x52582,0x106F,1,0)
    inner=read(0x52588,0x10F0,1,0)
    surface_call=call(0x5258C,0x26040,{4:0xA8EA,5:coolant,6:inner},-16)
    row,column=coolant//32,inner//32
    raw_row_fraction,raw_column_fraction=(coolant%32)*2048,(inner%32)*2048
    call(0x2604C,0x26AE0,{3:inner,4:coolant,5:0},-28,{4:row,5:raw_row_fraction})
    call(0x26056,0x26AE0,{3:inner,4:inner,5:0},-28,{4:column,5:raw_column_fraction})
    row_fraction=raw_row_fraction if row<7 else 0
    column_fraction=raw_column_fraction if column<7 else 0
    tails.append((0x26074,0x26770))
    first_address=0xA8EA+row*8+column
    second_address=first_address+8
    if column_fraction:
        first=read(0x2678A,first_address,1,1,'rom')
        second=read(0x2678C,first_address+1,1,0,'rom')
        upper=interpolate(0x26790,first,second,column_fraction,-24)
        if row_fraction:
            first=read(0x2679A,second_address,1,1,'rom')
            second=read(0x2679C,second_address+1,1,0,'rom')
            lower=interpolate(0x267A0,first,second,column_fraction,-28)
            surface_return=interpolate(0x267A8,upper,lower,row_fraction,-24)
        else:
            surface_return=upper
    else:
        first=read(0x267B4,first_address,1,0,'rom')
        if row_fraction:
            second=read(0x267B6,second_address,1,2,'rom')
            surface_return=interpolate(0x267BC,first,second,row_fraction,-24)
        else:
            surface_return=signed(first,8)&MASK
    surface_value=surface_return&255
    surface_call['returned']={0:surface_return}
    lookups.append(dict(kind='implicit-byte-surface',site=0x5258C,base=0xA8EA,
        row=row,column=column,outer_coordinate=coolant,inner_coordinate=inner,
        raw_row_fraction=raw_row_fraction,raw_column_fraction=raw_column_fraction,
        row_fraction=row_fraction,column_fraction=column_fraction,
        first_address=first_address,return_register=surface_return,value=surface_value))

    word_input=read(0x52592,0x1222,2,0)
    scaled_coordinate=word_input*32
    word_coordinate=min(65535,scaled_coordinate)
    word_call=call(0x525AA,0x263D8,{4:0x14ED2,5:word_coordinate},-16)
    word_index=min(7,word_coordinate//8192)
    word_fraction=(word_coordinate%8192)*8 if word_coordinate<57344 else 0
    if word_coordinate>=57344:
        first=read(0x263E8,0x14ED2+14,2,0,'rom')
        second=None
        word_return=signed(first,16)&MASK
    else:
        first=read(0x26AA0,0x14ED2+word_index*2,2,1,'rom')
        second=read(0x26AA2,0x14ED2+word_index*2+2,2,0,'rom')
        word_return=linear(first,second,word_fraction)
        tails.extend(((0x263E2,0x26A60),(0x26AB6,0x26740)))
    word_value=word_return&65535
    word_call['returned']={0:word_return}
    lookups.append(dict(kind='implicit-word-curve',site=0x525AA,base=0x14ED2,
        raw_coordinate=word_input,scaled_coordinate=scaled_coordinate,coordinate=word_coordinate,
        index=word_index,fraction=word_fraction,first=first,second=second,
        return_register=word_return,value=word_value))
    product=word_value*surface_value
    shifted=product//128
    value=min(65535,shifted)
    write(0x525CC,0x1652,2,value,2)
    return dict(memory=bytes(after),operands=operands,calls=calls,tails=tails,lookups=lookups,
        coolant_coordinate=coolant,inner_coordinate=inner,row=row,column=column,
        raw_row_fraction=raw_row_fraction,raw_column_fraction=raw_column_fraction,
        row_fraction=row_fraction,column_fraction=column_fraction,
        surface_return=surface_return,surface_value=surface_value,word_input=word_input,
        scaled_coordinate=scaled_coordinate,word_coordinate=word_coordinate,
        word_return=word_return,word_value=word_value,product=product,shifted=shifted,value=value)
