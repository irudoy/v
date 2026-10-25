"""Independent wide event timing equations with actual publication and live result flow."""
RAM_BASE=0x01000000
MASK=0xFFFFFFFF

def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value

def evaluate(memory,calibration):
    if type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the event timing equations need complete exact incoming RAM')
    after=bytearray(memory);operands=[];calls=[];tails=[];lookup=None
    def rom(address,width):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the event timing equation loses one complete physical ROM span')
        at,raw=spans[0]
        if type(raw) is not bytes:raise ValueError('the event timing equation replaces immutable raw calibration')
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
    knock=bool(read(0x4D9B0,0x8710,1,0,'rom')&32)
    first_gate=read(0x4D9B6,0x24C5,1,0)&32
    second_gate=read(0x4D9BC,0x24CB,1,0)&4 if not first_gate else None
    if not first_gate and not second_gate:
        ordinary=-signed(read(0x4D9C8,0x11F9,1,5),8)
        write(0x4D9CE,0x11D6,2,ordinary,0)
        if knock:write(0x4DA28,0x11D8,2,-signed(read(0x4D9D2,0x11FA,1,6),8),0)
    elif not knock:
        floor=-signed(read(0x4D9E2,0x11F9,1,2),8)
        prior=signed(read(0x4D9E4,0x22FA,1,0),8)
        write(0x4D9F4,0x11D6,2,min(prior,floor),0)
    else:
        high=read(0x4D9FA,0x23C2,2,0)>>8
        prior=signed(read(0x4DA00,0x22FA,1,0),8)
        floor=-signed(read(0x4DA0A,0x11FA,1,4),8)
        write(0x4DA1E,0x11D6,2,min(signed((prior-high)&65535,16),floor),0)
        write(0x4DA28,0x11D8,2,min(prior,floor),0)
    timer_raw=read(0x4DA2C,0x8290,1,5,'rom');clear=False
    if timer_raw:
        flags=read(0x4DA32,0x24C2,1,0)
        if flags&1 and not flags&2:
            target=signed(read(0x4DA4A,0x2378,1,2),8)
            write(0x4DA50,0x229D,1,target,2)
            flag=read(0x4DA52,0x24C0,1,0);write(0x4DA56,0x24C0,1,flag|64,0)
            write(0x4DA5C,0x25FC,1,timer_raw,0)
        elif not flags&2:
            previous=read(0x4DA62,0x1FF8,4,0)
            target=signed(read(0x4DA6A,0x229D,1,2),8)&MASK
            clear=previous==target
        else:clear=True
    else:clear=True
    if clear:
        flag=read(0x4DA70,0x24C0,1,0);write(0x4DA74,0x24C0,1,flag&0xBF,0)
    bypass=bool(read(0x4DA76,0x24CC,1,0)&2)
    candidate=None;coefficient=None;product=None;quotient=None;scaled=None
    if bypass:
        value=min(signed(read(0x4DB7A,0x2378,1,2),8),127)
    else:
        coordinate=read(0x4DA82,0x237E,2,7)
        parent=call(0x4DA88,0x264CC,{4:0x147DA,5:0x13C48,6:coordinate},-24)
        search=call(0x264D6,0x26984,{0:0x13C48,4:14,5:coordinate},-32)
        scanned=[];bracket=False;fraction=0;index=0
        for index in range(7,-1,-1):
            knot=read(0x26986,0x13C48+index*2,2,1,'rom');scanned.append(index)
            if coordinate==knot or coordinate>knot and index==7:break
            if coordinate>knot:
                lower=read(0x2699C,0x13C48+index*2,2,1,'rom')
                upper=read(0x2699E,0x13C48+index*2+2,2,0,'rom')
                denominator=upper-lower;numerator=(coordinate-knot)*65536
                if denominator<=0 or not lower<coordinate<upper:
                    raise ValueError('the rightmost event axis bracket loses its actual positive divisor')
                fraction=numerator//denominator;bracket=True
                call(0x269AA,0x26C78,{0:denominator,1:numerator},-36,{0:fraction})
                break
        search['returned']={4:index*2,5:fraction}
        second=read(0x264DE,0x147DA+index*2+2,2,0,'rom')
        first=read(0x264E4,0x147DA+index*2,2,1,'rom')
        delta=abs(second-first)*fraction//65536
        candidate=first+delta if second>=first else first-delta
        parent['returned']={0:candidate};tails.append((0x264EA,0x26740))
        lookup=dict(coordinate=coordinate,index=index,fraction=fraction,scanned=tuple(scanned),
            first=first,second=second,value=candidate,bracket=bracket)
        write(0x4DA90,0x2000,2,candidate,0)
        alternate=bool(read(0x4DA92,0x2459,1,0)&32)
        coefficient=read(0x4DA9C if alternate else 0x4DAAC,0x8A3C if alternate else 0x8A3D,
            1,2 if alternate else 5,'rom')
        write(0x4DAA2 if alternate else 0x4DAB2,0x226C,1,coefficient,2 if alternate else 5)
        product=candidate*coefficient;quotient=product//100;scaled=min(65535,quotient)
        call(0x4DABE,0x21CE0,{0:100,1:product},-24,{0:quotient})
        write(0x4DAD4,0x1FF6,2,scaled,0)
        slew=bool(read(0x4DAD6,0x24C0,1,0)&64)
        if slew:
            timer=read(0x4DADE,0x25FC,1,0)
            if not timer:
                target=signed(read(0x4DAE8,0x229D,1,2),8)
                previous=signed(read(0x4DAEA,0x1FF8,4,0))
                if previous!=target:
                    raw=read(0x4DAF2 if previous>target else 0x4DB02,0x8290,1,0,'rom')
                    write(0x4DAF6 if previous>target else 0x4DB06,0x25FC,1,raw,0)
                    stepped=signed(previous&65535,16)+(-1 if previous>target else 1)
                    write(0x4DB0C,0x1FF8,4,stepped,0)
            staged=read(0x4DB0E,0x1FF8,4,0)
            correction=signed(read(0x4DB58,0x2356,1,5),8)
            value=signed((staged+correction-scaled)&MASK)
        else:
            limit=read(0x4DB18,0x40E7,1,4)
            restricted=limit>0 and not read(0x4DB20,0x24C2,1,0)&2
            if restricted:
                ordinary=signed(read(0x4DB26,0x11D6,2,0),16)
                correction=signed(read(0x4DB2E,0x2356,1,2),8)
                bounded=min(ordinary+correction,-limit)
                target=signed(read(0x4DB40,0x2378,1,6),8)
                value=signed((target+bounded-scaled)&MASK)
            else:
                ordinary=signed(read(0x4DB48,0x11D6,2,0),16)
                target=signed(read(0x4DB4E,0x2378,1,2),8)
                staged=(target+ordinary)&MASK
                write(0x4DB54,0x1FF8,4,staged,0)
                correction=signed(read(0x4DB58,0x2356,1,5),8)
                value=signed((staged+correction-scaled)&MASK)
        value=max(-128,min(value,127))
    write(0x4DB8C,0x12D6,1,value,6)
    if any(row['mode']=='read' and row['address']==RAM_BASE+0x2000 for row in operands):
        raise ValueError('the event timing equations invent a physical read of prior2000 RAM')
    return dict(memory=bytes(after),operands=operands,calls=calls,tails=tails,lookup=lookup,
        active=not bypass,candidate=candidate,coefficient=coefficient,product=product,quotient=quotient,
        scaled=scaled,value=value&255,signed_value=value,knock=knock)
