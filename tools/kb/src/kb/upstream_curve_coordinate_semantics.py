"""Independent complete source-curve, derived-coordinate and long-output equations."""

RAM_BASE=0x01000000
MASK=0xFFFFFFFF


def signed(value,bits=32):
    return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(memory,calibration,frame_before,context):
    if (type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)
            or context[18]&~0x3F1):
        raise ValueError('the upstream-coordinate equations require complete raw RAM, frame and CPU inputs')
    fifth_word=int.from_bytes(frame_before[160:164],'big')
    if fifth_word!=context[19]:
        raise ValueError('the upstream-coordinate equations detach the full incoming fifth argument')
    after=bytearray(memory)
    operands,calls,tails,lookups=[],[],[],[]

    def physical(address,width):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:
            raise ValueError('the upstream-coordinate equations lose an exact physical ROM span')
        at,data=spans[0]
        if type(data) is not bytes:
            raise ValueError('the upstream-coordinate equations replace immutable calibration')
        return data[address-at:address-at+width]

    def constant(address,width,signed_bits=None):
        value=int.from_bytes(physical(address,width),'big')
        return signed(value,signed_bits) if signed_bits is not None else value

    def read(site,address,width,register):
        raw=physical(address,width)
        operands.append(dict(site=site,mode='read',address=address,width_bytes=width,
            register=register,domain='rom',bytes=raw.hex()))
        return int.from_bytes(raw,'big')

    def write(site,address,width,value,register):
        raw=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        after[address:address+width]=raw
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=raw.hex()))

    def call(site,target,arguments,sp_delta=-32,returned=None):
        row=dict(site=site,target=target,arguments=arguments,sp_delta=sp_delta,return_address=site+4)
        if returned is not None:row['returned']=returned
        calls.append(row)
        return row

    def signed_division(site,divisor,raw_dividend,extra=None):
        if not 0<divisor<=65535:
            raise ValueError('the upstream-coordinate caller loses its positive bounded divisor')
        dividend=signed(raw_dividend&MASK)
        quotient=abs(dividend)//divisor
        if dividend<0:quotient=-quotient
        arguments={0:divisor,1:raw_dividend&MASK}
        if extra:arguments.update(extra)
        call(site,0x21BBC,arguments,returned={0:quotient&MASK})
        return quotient

    def axis(site,base,coordinate,count):
        parent=call(site,0x26984,{0:base,4:(count-1)*2,5:coordinate},-40)
        index,fraction,bracket,scanned=0,0,False,[]
        for index in range(count-1,-1,-1):
            knot=read(0x26986,base+index*2,2,1)
            scanned.append(index)
            if coordinate==knot or coordinate>knot and index==count-1:break
            if coordinate>knot:
                lower=read(0x2699C,base+index*2,2,1)
                upper=read(0x2699E,base+(index+1)*2,2,0)
                divisor,dividend=upper-lower,(coordinate-knot)*65536
                if divisor<=0 or not lower<coordinate<upper:
                    raise ValueError('the rightmost upstream-coordinate axis loses its positive actual bracket')
                fraction,bracket=dividend//divisor,True
                call(0x269AA,0x26C78,{0:divisor,1:dividend},-44,{0:fraction})
                break
        parent['returned']={4:index*2,5:fraction}
        result=dict(kind='axis',site=site,base=base,coordinate=coordinate,count=count,
            index=index,fraction=fraction,bracket=bracket,scanned=tuple(scanned))
        lookups.append(result)
        return result

    def explicit(site,entry,base,axis_base,coordinate,count):
        parent=call(site,entry,{4:base,5:axis_base,6:coordinate})
        position=axis(entry+10,axis_base,coordinate,count)
        index,fraction=position['index'],position['fraction']
        second=read(entry+18,base+(index+1)*2,2,0)
        first=read(entry+24,base+index*2,2,1)
        delta=abs(second-first)*fraction//65536
        returned=first+delta if second>=first else first-delta
        parent['returned']={0:returned}
        tails.append((entry+30,0x26740))
        lookups.append(dict(kind='explicit-word-curve',site=site,entry=entry,base=base,
            axis=axis_base,coordinate=coordinate,count=count,index=index,fraction=fraction,
            first=first,second=second,return_register=returned,value=returned))
        return returned

    initial_divisor=constant(0xB7AFE,2,16)
    initial_quotient=signed_division(0xB7A62,initial_divisor,context[6],{11:context[5]})
    local_byte=context[7]&255
    adjusted=initial_quotient-local_byte*50
    upper=constant(0xB7B00,2,16)
    lower=constant(0xB7C20,4,32)
    if adjusted>upper:
        initial_word=constant(0xB7B02,2,16)
    elif adjusted<lower:
        initial_word=-32768
    else:
        initial_word=adjusted+constant(0xB7B04,2,16)
    narrowed=signed(initial_word&65535,16)
    nonnegative=max(0,narrowed)
    source_coordinate=(fifth_word&255)*256
    source_return=explicit(0xB7AAC,0x264CC,0x14E42,0x13BB8,source_coordinate,8)
    first_factor=read(0xB7AB2,0x8A30,1,0)
    full_initial_product=nonnegative*first_factor
    initial_product_limit=constant(0xB7C30,4)
    full_B=MASK if full_initial_product>initial_product_limit else full_initial_product//2
    H=context[4]&65535
    ratio_factor=read(0xB7AD2,0x8832,1,5)
    source_value=source_return&65535
    ratio_product=(-source_value*ratio_factor)&MASK
    ratio_quotient=None
    if H:
        ratio_dividend=(ratio_product*20)&MASK
        ratio_quotient=signed_division(0xB7AE8,H,ratio_dividend)
        coordinate_before_extension=ratio_quotient-1 if ratio_quotient>=constant(0xB7C04,4,32) else 0
    else:
        coordinate_before_extension=-1 if signed(ratio_product)>=0 else 0
    consumer_coordinate=coordinate_before_extension&65535
    consumer_return=explicit(0xB7B14,0x264F8,0x151F2,0x13BF8,consumer_coordinate,16)
    consumer_value=consumer_return&65535
    negative_weight=-consumer_value
    full_inverse_weight=negative_weight-1 if negative_weight>=constant(0xB7BF0,2,16) else 0
    inverse_weight=full_inverse_weight&255
    selector=min(4,(context[5]&255)+1)
    if selector==1:
        full_coefficient=10
    else:
        site,address={2:(0xB7B56,0x8A35),3:(0xB7B54,0x8A36),4:(0xB7B4C,0x8A34)}[selector]
        full_coefficient=signed(read(site,address,1,0),8)
    coefficient=full_coefficient&255
    B=full_B&65535
    first_product=B*inverse_weight
    first_quotient=first_product//255
    call(0xB7B6C,0x21CE0,{0:255,1:first_product,14:coefficient},returned={0:first_quotient})
    second_product=(first_quotient&65535)*H
    second_divisor=constant(0xB7BF2,2,16)
    second_quotient=second_product//second_divisor
    call(0xB7B78,0x21CE0,{0:second_divisor,1:second_product},returned={0:second_quotient})
    value=(second_quotient*coefficient)&MASK
    write(0xB7B84,0x3228,4,value,2)
    return dict(memory=bytes(after),operands=operands,calls=calls,tails=tails,lookups=lookups,
        fifth_word=fifth_word,local_byte=local_byte,initial_quotient=initial_quotient,adjusted=adjusted,
        initial_word=initial_word,narrowed=narrowed,nonnegative=nonnegative,source_coordinate=source_coordinate,
        source_return=source_return,source_value=source_value,first_factor=first_factor,
        full_initial_product=full_initial_product,full_B=full_B,B=B,H=H,ratio_factor=ratio_factor,
        ratio_product=ratio_product,ratio_quotient=ratio_quotient,
        coordinate_before_extension=coordinate_before_extension,consumer_coordinate=consumer_coordinate,
        consumer_return=consumer_return,consumer_value=consumer_value,full_inverse_weight=full_inverse_weight,
        inverse_weight=inverse_weight,selector=selector,full_coefficient=full_coefficient,coefficient=coefficient,
        first_product=first_product,first_quotient=first_quotient,second_product=second_product,
        second_quotient=second_quotient,value=value)
