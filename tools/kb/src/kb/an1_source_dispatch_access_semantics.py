"""Independent complete two-lane RAM sequence and actual byte-curve publications."""

RAM_BASE=0x01000000


def curve(values,coordinate):
    if (type(values) is not bytes or len(values)!=32 or type(coordinate) is not int
            or not 0<=coordinate<=255):
        raise ValueError('the AN1 curve equations require the physical32-byte source and raw uint8 coordinate')
    if coordinate>=248:return dict(index=31,fraction=0,value=values[31],endpoint=True)
    index,remainder=divmod(coordinate,8);fraction=remainder<<13
    a,b=values[index:index+2];magnitude=abs(b-a)*fraction//65536
    return dict(index=index,fraction=fraction,value=a+magnitude if b>=a else a-magnitude,endpoint=False)


def sequence(memory,calibration):
    if type(memory) is not bytes or len(memory)!=65536:
        raise ValueError('the AN1 sequence equations require complete raw RAM')
    ram=bytearray(memory);writes=[];lookups=[];tags={}

    def byte(at):return ram[at]
    def word(at):return int.from_bytes(ram[at:at+2],'big')
    def cal(at):
        rows=[(start,raw) for start,raw in calibration.items() if start<=at<start+len(raw)]
        if len(rows)!=1:raise ValueError('the AN1 equations omit an exact independent calibration byte')
        start,raw=rows[0];return raw[at-start]
    def put(site,at,value,width=1,register=None):
        raw=(value&((1<<(8*width))-1)).to_bytes(width,'big');ram[at:at+width]=raw
        writes.append(dict(site=site,mode='write',address=RAM_BASE+at,width_bytes=width,
            register=register,domain='ram',bytes=raw.hex()))
    values=bytes(cal(0x12DEA+i) for i in range(32))
    def lookup(lane,source,site,root_call):
        raw=word(source);coordinate=(raw>>2)&255;value=curve(values,coordinate)
        lookups.append(dict(lane=lane,source=source,raw=raw,coordinate=coordinate,
            callsite=site,root_call=root_call,**value))
        return value['value']

    # Both natural filter entries precede every conversion entry.
    for lane in (0,1):
        mask=lane+1;phase=byte(0x3F3E)
        if not phase&mask:
            raw=word(0x1D58+2*lane);prior=word(0x2832+2*lane)
            if not byte(0x3F44)&mask:
                put(0x3D298,0x3F44,byte(0x3F44)|mask,register=2);filtered=raw
            else:
                filtered=(3*prior+raw)//4
                if filtered==prior and filtered<raw:filtered+=1
            put(0x3D2C6,0x2832+2*lane,filtered,2,4);phase|=mask
        else:phase&=~mask
        put(0x3D2D2,0x3F3E,phase,register=12)
    put(0x3D854,0x2830,word(0x2832),2,0)

    fallback=not cal(0x8B42)&1 and bool(cal(0x8B34)&16) and not cal(0x8B34)&2 and not cal(0x8B42)&32
    tags['fallback']=fallback
    for lane in (0,1):
        if fallback:put(0x3D30E,0x2838+lane,75,register=1)
        else:put(0x3D336,0x2838+lane,lookup(lane,0x2832+2*lane,0x3D32E,(0x3D852,0x3D856)[lane]),register=2)
    put(0x3D860,0x2837,byte(0x2838),register=0)
    for lane in (0,1):
        value=byte(0x2838+lane)
        if value<10:site,out,register=0x3D36C,0,3
        elif value>=170:site,out,register=0x3D3A4,255,3
        else:site,out,register=0x3D39C,240*(value-10)//150,6
        put(site,0x1175+lane,out,register=register)
    put(0x3D872,0x1174,byte(0x1175),register=2)
    for lane in (0,1):put(0x3D3CC,0x3F3F+lane,word(0x2832+2*lane)>>2,register=6)
    put(0x3D880,0x2836,byte(0x3F3F),register=0)

    for lane in (0,1):
        mask=lane+1
        if byte(0x1EDA+lane)==0:
            put(0x3D454,0x1EDA+lane,1,register=6)
        else:
            fresh=byte(0x1F85)
            if byte(0x4185)&64 and byte(0x1188)<100:
                put(0x3D3F8,0x1F85,fresh&~mask,register=2);admitted=True
            elif fresh&mask:admitted=False
            else:put(0x3D412,0x1F85,fresh|mask,register=4);admitted=True
            if admitted:put(0x3D44E,0x5610+lane,byte(0x2838+lane),register=6)
    put(0x3D894,0x454C,byte(0x5610),register=2)

    for lane in (0,1):
        if not byte(0x4185)&64 and not byte(0x417F)&32 and byte(0x3F3E)&(lane+1):
            value=byte(0x2838+lane)
            if value<byte(0x3F4C+lane):put(0x3D4A2,0x3F4C+lane,value,register=5)
    put(0x3D8A0,0x283C,byte(0x3F4C),register=0)

    if not byte(0x4226)&128:
        for index,site in enumerate((0x3D53E,0x3D542,0x3D546,0x3D54A,0x3D54E,0x3D552,0x3D556)):
            put(site,0x3F45+index,byte(0x2837),register=2)
        put(0x3D55E,0x4226,byte(0x4226)|128,register=0);tags['history']='initialize'
    elif byte(0x84C3)&32:
        prior=byte(0x3F4A);put(0x3D572,0x3F4B,prior,register=7)
        for source,target,site in ((0x3F49,0x3F4A,0x3D57C),(0x3F48,0x3F49,0x3D584),
                (0x3F47,0x3F48,0x3D58C),(0x3F46,0x3F47,0x3D594),(0x3F45,0x3F46,0x3D59C)):
            put(site,target,byte(source),register=2)
        current=byte(0x2837);put(0x3D5A6,0x3F45,current,register=2)
        put(0x3D5B8 if current<prior else 0x3D5BE,0x3D62,abs(current-prior),register=2)
        tags['history']='update'
    else:tags['history']='hold'

    if byte(0x118E)<cal(0x8DC8):
        put(0x3D5F2,0x423A,byte(0x423A)&254,register=0)
        put(0x3D5F6,0x42C6,cal(0x8C5D),register=0)
    else:put(0x3D5EA,0x423A,(byte(0x423A)&254)|int(byte(0x42C6)==0),register=0)

    if byte(0x4187)&64 and not byte(0x4185)&64:
        put(0x3D624,0x4237,byte(0x4237)|32,register=0)
    elif byte(0x4185)&64:put(0x3D624,0x4237,byte(0x4237)&223,register=0)
    if not byte(0x4237)&32:
        put(0x3D648,0x4238,byte(0x4238)&223)
        put(0x3D64C,0x42C7,cal(0x8C5E),register=2)
    elif byte(0x42C7)==0:put(0x3D63C,0x4238,byte(0x4238)|32)

    if (cal(0x8D27)<=byte(0x1079)<=cal(0x8D26) and byte(0x423A)&1
            and byte(0x3D62)<cal(0x8424) and byte(0x4238)&32 and byte(0x84C3)&32):
        put(0x3D6BC,0x3D52,min(255,byte(0x3D52)+1),register=2)
    flags=byte(0x422E)
    if not flags&8:
        if byte(0x118E)>=cal(0x8DC8):
            put(0x3D6E2,0x422E,flags&239,register=0)
            put(0x3D6E8,0x422E,byte(0x422E)|8)
    elif byte(0x3D52)>=cal(0x83EE):put(0x3D6FC,0x422E,flags|16,register=0)

    if not byte(0x4237)&2:
        put(0x3D7CC,0x283A,byte(0x2837),register=2)
        put(0x3D7D4,0x4237,byte(0x4237)|2,register=6)
    temp=byte(0x1076);difference=abs(byte(0x454C)-temp)
    offset=cal(0x8B5B if temp<cal(0x8CEF) and difference<cal(0x8CCE) else 0x8B5C)
    put(0x3D762,0x283A,max(0,byte(0x283C)-offset),register=0)
    for lane in (0,1):
        value=lookup(lane,0x1D58+2*lane,0x3D4C0,(0x3D8B6,0x3D8BA)[lane])
        put(0x3D4DA if value>10 else 0x3D4E6,0x3F42+lane,max(0,value-10),register=6 if value>10 else 1)
    put(0x3D8C6,0x3F41,byte(0x3F42),register=2)
    if not byte(0x4237)&4:
        first,second=byte(0x454C),byte(0x5612)
        put(0x3D804 if first<second else 0x3D802,0x283D,min(first,second),register=7 if first<second else 4)
        put(0x3D80E,0x4237,byte(0x4237)|4,register=5)
    if byte(0x422E)&16:put(0x3D82C,0x5612,byte(0x283A),register=2)
    return dict(ram=bytes(ram),writes=writes,lookups=lookups,tags=tags,
        temperature_codes=(byte(0x2838),byte(0x2839)),PID=(byte(0x3F42),byte(0x3F43)),
        publication=byte(0x3F41),running_minimum=(byte(0x3F4C),byte(0x3F4D)))
