"""Separate constant-root byte interpolation, endpoint promotion and caller state equations."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def lookup(raw,coordinate):
    if type(raw) is not bytes or len(raw)!=8 or type(coordinate) is not int or not 0<=coordinate<=255:
        raise ValueError('the byte-curve equation needs eight exact cells and a byte coordinate')
    if coordinate>=224:
        return dict(value=raw[7],raw_result=signed(raw[7],8)&MASK,index=7,fraction=0,
            endpoint=True,ascending=None,t=True,reads=((7,1),))
    index,remainder=divmod(coordinate,32);first,second=raw[index:index+2]
    magnitude=(abs(second-first)*remainder)//32
    ascending=second>=first;value=first+magnitude if ascending else first-magnitude
    return dict(value=value,raw_result=value,index=index,fraction=remainder<<11,
        endpoint=False,ascending=ascending,t=ascending,magnitude=magnitude,first=first,second=second,
        reads=((index,1),(index+1,1)))


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry not in (0x2C59C,0x6E3D8)
            or type(memory) is not bytes or len(memory)!=65536 or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20 or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the byte-curve caller equations need complete exact CPU/RAM/frame inputs')
    registers=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    frames={};writes={};calls=[];controls={};curves=[];t=bool(sr_before&1);division_active=False;special_gbr=context[15]
    def reg(i,value):registers[i]=value&MASK
    def saved(site,mode,depth,value,register=None):
        raw=(value&MASK).to_bytes(4,'big');frames[site]=(mode,depth,register,raw)
        if mode=='write':frame[160-depth:164-depth]=raw
    def put(site,at,width,value):
        raw=(value&((1<<(8*width))-1)).to_bytes(width,'big');ram[at:at+width]=raw;writes[site]=raw
    def control(site,kind,target,delay=False):controls[site]=dict(site=site,kind=kind,target=target,delay=delay)
    def branch(site,taken,target,delay=False):control(site,'taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)
    def call(site,target,macl):
        row=dict(site=site,target=target,return_address=site+4,sp=sp-8,registers=tuple(registers),
            gbr=special_gbr,mach=context[16],macl=macl,sr=(sr_before&~1)|int(t),arguments={0:registers[0],1:registers[1],4:registers[4],5:registers[5]})
        calls.append(row);control(site,'call',target,True);return row
    def curve(site,base,coordinate):
        nonlocal t
        row=call(site,0x26370,context[17]);value=lookup(calibration[base],coordinate)
        curves.append(dict(value,site=site,base=base,return_address=site+4))
        branch(0x26376,value['endpoint'],0x2637E)
        if value['endpoint']:
            reg(0,value['raw_result']);t=True
            control(0x2637E,'return',site+4,True)
        else:
            control(0x2637A,'jump',0x26A80,True)
            branch(0x26A9A,True,0x26AAA)
            control(0x26AB6,'jump',0x26740,True)
            branch(0x26742,value['ascending'],0x2675C)
            reg(0,value['value']);reg(1,context[17]);reg(2,value['magnitude'] if value['ascending'] else value['value'])
            reg(3,value['fraction']);reg(4,base+value['index']);reg(5,value['index']);reg(6,0x26740);t=value['t']
            if not value['ascending']:
                saved(0x26744,'write',12,value['first'],0);saved(0x26752,'read',12,value['first'],2)
            control(0x2676A if value['ascending'] else 0x26758,'return',site+4,True)
        row.update(return_registers=tuple(registers),return_site=0x2637E if value['endpoint'] else (0x2676A if value['ascending'] else 0x26758),
            return_sr=(sr_before&~1)|int(t),return_sr_mask=MASK)
        return value
    saved(entry,'write',4,continuation)
    if entry==0x2C59C:
        saved(0x2C59E,'write',8,context[15]);special_gbr=RAM_BASE+0x1E50
        coordinate=memory[0x1077]
        reg(0,signed(coordinate,8));reg(2,0x26370);reg(4,0x12332);reg(5,coordinate)
        value=curve(0x2C5AC,0x12332,coordinate)
        put(0x2C5B0,0x1F24,1,value['value']);reg(0,value['value']<<8);put(0x2C5B6,0x1E54,2,registers[0])
        saved(0x2C5B8,'read',8,context[15]);saved(0x2C5BA,'read',4,continuation)
        control(0x2C5BC,'return',continuation,True)
        output=value['value']<<8
    else:
        saved(0x6E3DA,'write',8,context[17]);saved(0x6E43A,'read',8,context[17]);saved(0x6E43C,'read',4,continuation)
        mode=memory[0x244F];denominator=memory[0x16B1];gain=memory[0x16AE];coordinate=memory[0x106F]
        direct=bool(mode&2);t=not direct;reg(0,signed(mode,8));reg(6,RAM_BASE+0x244F)
        branch(0x6E3E2,not direct,0x6E3F4)
        if direct:
            reg(0,signed(coordinate,8));reg(2,0x26370);reg(4,0x1296C);reg(5,coordinate)
            value=curve(0x6E3EC,0x1296C,coordinate);reg(2,value['raw_result'])
            control(0x6E3F0,'jump',0x6E436,True)
            output=value['value']
        else:
            reg(7,RAM_BASE+0x128C);reg(0,0x425);reg(2,signed(denominator,8));t=denominator==0
            branch(0x6E3FC,not t,0x6E402)
            if t:
                control(0x6E3FE,'jump',0x6E438,True);reg(2,MASK);output=255
            else:
                reg(0,signed(coordinate,8));reg(2,0x26370);reg(4,0x1296C);reg(5,coordinate)
                value=curve(0x6E40A,0x1296C,coordinate)
                dividend=value['value']*gain;quotient=dividend//denominator
                reg(0,denominator);reg(1,dividend);reg(2,gain);reg(4,denominator);reg(5,denominator);reg(6,0x21BBC);reg(7,RAM_BASE+0x128C)
                row=call(0x6E426,0x21BBC,dividend);division_active=True
                row['long_path']=dividend>=denominator*256
                returned=list(registers);returned[0]=quotient;returned[1]=None
                row.update(return_registers=tuple(returned),return_site=0x21C6C if row['long_path'] else 0x21C04,
                    return_sr=sr_before&~0x301,return_sr_mask=MASK&~0x100)
                saved(0x21BBC,'write',12,gain,2);saved(0x21BC2,'write',16,registers[3],3)
                if row['long_path']:
                    saved(0x21C08,'write',20,denominator,4);saved(0x21C68,'read',20,denominator,4)
                    saved(0x21C6A,'read',16,registers[3],3);saved(0x21C6E,'read',12,gain,2)
                else:
                    saved(0x21C02,'read',16,registers[3],3);saved(0x21C06,'read',12,gain,2)
                reg(5,MASK);reg(6,quotient);reg(2,255);t=quotient>255
                branch(0x6E432,t,0x6E436)
                if not t:reg(2,quotient)
                output=min(255,quotient)
        reg(0,0x4DA);reg(7,RAM_BASE+0x128C);put(0x6E440,0x1766,1,output)
        control(0x6E43E,'return',continuation,True)
    known={i:value for i,value in enumerate(registers)}
    if division_active:known.pop(1)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers=known,t=bool(t),division_active=division_active,
        curves=curves,calls=calls,controls=controls,frame_accesses=frames,physical_writes=writes,
        gbr=context[15],mach=context[16],macl=context[17],pr=continuation,sp=sp,output=output,sr_before=sr_before)
