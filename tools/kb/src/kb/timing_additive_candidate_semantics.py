"""Independent optional timing-term equations, physical lookup flow and full stack carrier."""
RAM_BASE=0x01000000
MASK=0xFFFFFFFF

def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value

def evaluate(memory,calibration,frame_before):
    if (type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192):
        raise ValueError('the timing additive equations need complete exact incoming RAM and frame')
    after=bytearray(memory);operands=[];calls=[];tails=[];lookups=[]
    def rom(address,width):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the timing additive equation loses one physical ROM span')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the timing additive equation replaces immutable calibration')
        return raw[address-at:address-at+width]
    def read(site,address,width,register,domain='ram'):
        raw=bytes(after[address:address+width]) if domain=='ram' else rom(address,width)
        operands.append(dict(site=site,mode='read',address=RAM_BASE+address if domain=='ram' else address,
            width_bytes=width,register=register,domain=domain,bytes=raw.hex()))
        return int.from_bytes(raw,'big')
    def write(site,address,width,value,register):
        raw=(value&((1<<(width*8))-1)).to_bytes(width,'big');after[address:address+width]=raw
        operands.append(dict(site=site,mode='write',address=RAM_BASE+address,width_bytes=width,
            register=register,domain='ram',bytes=raw.hex()))
    def call(site,target,arguments,sp_delta,returned=None):
        row=dict(site=site,target=target,return_address=site+4,arguments=arguments,sp_delta=sp_delta)
        if returned is not None:row['returned']=returned
        calls.append(row);return row
    def axis(site,base,coordinate,width,sp_delta):
        word=width==2;entry=0x26984 if word else 0x26944
        search=call(site,entry,{0:base,4:14 if word else 7,5:coordinate},sp_delta)
        first_site=0x26986 if word else 0x26946
        lower_site=0x2699C if word else 0x2695C
        upper_site=0x2699E if word else 0x2695E
        division_site=0x269AA if word else 0x2696A
        scanned=[];fraction=0;bracket=False;index=0
        for index in range(7,-1,-1):
            knot=read(first_site,base+index*width,width,1,'rom');scanned.append(index)
            if coordinate==knot or coordinate>knot and index==7:break
            if coordinate>knot:
                lower=read(lower_site,base+index*width,width,1,'rom')
                upper=read(upper_site,base+(index+1)*width,width,0,'rom')
                denominator=upper-lower;numerator=(coordinate-knot)*65536
                if denominator<=0 or not lower<coordinate<upper:
                    raise ValueError('the rightmost additive axis bracket loses its positive actual divisor')
                fraction=numerator//denominator;bracket=True
                call(division_site,0x26C78,{0:denominator,1:numerator},sp_delta-4,{0:fraction})
                break
        search['returned']={4:index*width,5:fraction}
        result=dict(base=base,width=width,index=index,fraction=fraction,coordinate=coordinate,
            scanned=tuple(scanned),bracket=bracket)
        lookups.append(dict(kind='axis',**result));return result
    def linear(first,second,fraction):
        change=abs(second-first)*fraction//65536
        return first+change if second>=first else first-change
    def interpolation(site,first,second,fraction,sp_delta):
        value=linear(first,second,fraction)
        call(site,0x26740,{0:first,2:second,3:fraction},sp_delta,{0:value})
        return value
    alternate=bool(read(0x4BDD6,0x2458,1,0)&32)
    active=False;candidate=None;curve=None;surface=None;surface_return=None
    product=None;quotient=None;inner_argument=None;inner_raw=None;outer_coordinate=None
    if alternate:
        subtract=read(0x4BEAA,0x23C5,1,0)
        base=read(0x4BEB4,0x1A7D,1,2)
        prior=signed(read(0x4BEB8,0x23EE,1,4),8)
        flags=read(0x4BEBC,0x24D1,1,0)
        composed=base+prior-subtract-64;flag_output=flags|32
    else:
        first=read(0x4BDDC,0x23BD,1,0)
        subtract=read(0x4BDE2,0x23C5,1,0)
        correction=signed(read(0x4BDE8,0x23F1,1,2),8)
        earlier=read(0x4BDEA,0x12DC,1,0)
        adjustment=read(0x4BDF4,0x15EA,1,5)
        base=read(0x4BDFE,0x1A7D,1,6)
        first_word=read(0x4BE08,0x28B8,2,6)
        second_word=read(0x4BE0E,0x28BA,2,2)
        smaller=min(first_word,second_word)
        composed=base+correction+first-subtract-earlier-adjustment-128
        gate=bool(read(0x4BE20,0x41AB,1,0)&64)
        threshold=read(0x4BE2A,0x9012,2,2,'rom') if gate else None
        active=gate and smaller>=threshold
        if active:
            byte_coordinate=read(0x4BE36,0x106F,1,0)
            byte_parent=call(0x4BE3C,0x26474,{4:0x11F02,5:0x11EEA,6:byte_coordinate},-24)
            byte_axis=axis(0x2647E,0x11EEA,byte_coordinate,1,-32)
            index=byte_axis['index'];fraction=byte_axis['fraction']
            second=read(0x26486,0x11F02+index+1,1,0,'rom')
            first=read(0x2648C,0x11F02+index,1,1,'rom')
            curve=linear(first,second,fraction)
            byte_parent['returned']={0:curve};tails.append((0x26492,0x26740))
            lookups.append(dict(kind='byte-curve',index=index,fraction=fraction,first=first,second=second,value=curve))
            write(0x4BE42,0x134C,1,curve,0)
            inner_raw=read(0x4BE44,0x1024,2,0)
            inner_argument=int.from_bytes(frame_before[136:138]+inner_raw.to_bytes(2,'big'),'big')
            outer_coordinate=read(0x4BE4C,0x10CA,2,3)
            word_parent=call(0x4BE56,0x26270,{4:0xC50E,5:0x1461A,6:0x1464A,7:outer_coordinate},-24)
            outer=axis(0x2627C,0x1461A,outer_coordinate,2,-32)
            inner=axis(0x2628A,0x1464A,inner_argument&65535,2,-40)
            tails.append((0x2629C,0x26848))
            row=outer['index'];column=inner['index'];rf=outer['fraction'];cf=inner['fraction']
            address=0xC50E+row*16+column*2;next_row=address+16
            if cf:
                first=read(0x26864,address,2,1,'rom');second=read(0x26866,address+2,2,0,'rom')
                first_value=interpolation(0x2686A,first,second,cf,-32)
                if rf:
                    lower_first=read(0x26874,next_row,2,1,'rom');lower_second=read(0x26876,next_row+2,2,0,'rom')
                    second_value=interpolation(0x2687A,lower_first,lower_second,cf,-36)
                    surface_return=interpolation(0x26882,first_value,second_value,rf,-32)
                else:surface_return=first_value
            else:
                first=read(0x2688E,address,2,0,'rom')
                if rf:
                    second=read(0x26890,next_row,2,2,'rom')
                    surface_return=interpolation(0x26896,first,second,rf,-32)
                else:surface_return=signed(first,16)&MASK
            word_parent['returned']={0:surface_return};surface=min(255,surface_return&65535)
            lookups.append(dict(kind='word-surface',row=row,column=column,row_fraction=rf,column_fraction=cf,
                raw_unsigned_value=surface_return&65535,return_register=surface_return,capped_value=surface))
            write(0x4BE68,0x1348,1,surface,0)
            factor=read(0x4BE6E,0x1900,2,2)
            carried_curve=read(0x4BE70,0x134C,1,0)
            product=surface*factor*carried_curve;quotient=product//500000
            if not 0<=product<=MASK:raise ValueError('the additive unsigned product changes its exact full32 premise')
            call(0x4BE80,0x21CE0,{0:500000,1:product},-24,{0:quotient})
            candidate=min(255,quotient);write(0x4BE92,0x134A,1,candidate,0)
            additive=candidate
        else:additive=0
        write(0x4BEA0,0x12D4,1,additive,0)
        composed+=additive
        flags=read(0x4BEA4,0x24D1,1,0);flag_output=flags&0xDF
    # The full sum is explicitly narrowed before the actual signed-byte limits.
    narrowed=signed(composed&65535,16)
    write(0x4BECE,0x24D1,1,flag_output,0)
    final=max(-128,min(narrowed,127))
    write(0x4BEE2,0x1830,1,final,2)
    if any(row['mode']=='read' and row['address']==RAM_BASE+0x134A for row in operands):
        raise ValueError('the timing additive equations invent a physical read of prior134A RAM')
    return dict(memory=bytes(after),operands=operands,calls=calls,tails=tails,lookups=lookups,
        alternate=alternate,active=active,candidate=candidate,curve=curve,surface=surface,
        surface_return=surface_return,inner_argument=inner_argument,inner_raw=inner_raw,
        outer_coordinate=outer_coordinate,product=product,quotient=quotient,composed=composed,
        narrowed=narrowed,value=final&255,signed_value=final,flag_output=flag_output)
