"""Separate raw signed-word difference, dual-byte factors and exact partial-product physical paths."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def linear(first,second,fraction):
    if any(type(v) is not int or not 0<=v<=65535 for v in (first,second,fraction)):
        raise ValueError('the word interpolation equation changes an unsigned operand width')
    magnitude=abs(second-first)*fraction//65536
    ascending=second>=first
    return dict(value=first+magnitude if ascending else first-magnitude,magnitude=magnitude,
        first=first,second=second,fraction=fraction,ascending=ascending)


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry!=0x4BA48
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the byte factor caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the byte factor caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the byte factor caller equation loses one authoritative physical preimage')
        at,data=spans[0];raw=data[address-at:address-at+width]
        event(site,'read',address,width,register,'rom',raw)
        return int.from_bytes(raw,'big')

    def frame_access(site,mode,address,width,register,value=None):
        at=160+address-sp
        if mode=='write':frame[at:at+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
        raw=bytes(frame[at:at+width]);event(site,mode,address,width,register,'frame',raw)
        return int.from_bytes(raw,'big')

    def push(site,value,register=None):
        nonlocal stack
        stack-=4;frame_access(site,'write',stack,4,register,value)

    def pop(site,register=None):
        nonlocal stack
        value=frame_access(site,'read',stack,4,register);stack+=4;return value

    def t(value):
        nonlocal sr,sr_mask
        sr=(sr&~1)|int(bool(value));sr_mask|=1

    def control(site,kind,target,delay=False):controls.append(dict(site=site,kind=kind,target=target,delay=delay))

    def branch(site,taken,target,delay=False):
        control(site,'taken' if taken else 'fallthrough',target if taken else site+(4 if delay else 2),delay)

    def call(site,target):
        nonlocal pr
        row=dict(site=site,target=target,return_address=site+4,sp=stack,registers=tuple(r),
            gbr=gbr,mach=context[16],macl=macl,sr=sr,sr_mask=sr_mask)
        calls.append(row);pr=site+4;control(site,'call',target,True);return row

    def returned(row,site):
        row.update(return_site=site,return_registers=tuple(r),return_sr=sr,return_sr_mask=sr_mask,
            return_gbr=gbr,return_mach=context[16],return_macl=macl)

    def interpolation(target,row=None):
        nonlocal macl
        value=linear(r[0],r[2],r[3]);t(value['ascending'])
        emit(target,target+4);branch(target+2,value['ascending'],target+28)
        if value['ascending']:
            emit(target+28,target+46);r[1]=macl;r[2]=value['magnitude'];r[0]=value['value']
            terminal=target+42
        else:
            emit(target+4,target+28);push(target+4,r[0],0)
            r[1]=macl;pop(target+18,2);r[2]=r[0]=value['value'];terminal=target+24
        control(terminal,'return',pr,True)
        if row is not None:returned(row,terminal)
        return value

    def load(site,at,width,register):
        raw=bytes(ram[at:at+width]);event(site,'read',RAM_BASE+at,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,at,width,register,value):
        ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+at,width,register,'ram',bytes(ram[at:at+width]))

    def implicit_curve(row):
        base,coordinate=r[4],r[5]&255
        if base not in (0x126A0,0x126A8):raise ValueError('the implicit curve changes its exact natural eight-byte root')
        emit(0x26370,0x26378);r[0]=224;r[5]=coordinate;endpoint=coordinate>=224;t(endpoint)
        branch(0x26376,endpoint,0x2637E)
        if endpoint:
            emit(0x2637E,0x26382);r[0]=signed(read(0x26380,base+7,0,1),8)&MASK
            control(0x2637E,'return',pr,True);returned(row,0x2637E)
            lookups.append(dict(kind='implicit-byte-curve',index=7,fraction=0,endpoint=True,value=r[0]&255))
        else:
            emit(0x26378,0x2637E);r[6]=0x26A80;r[3]=0;control(0x2637A,'jump',0x26A80,True)
            emit(0x26A80,0x26A9C);index,remainder=divmod(coordinate,32)
            r[5]=index;r[3]=remainder<<11;r[0]=0;t(True);branch(0x26A9A,True,0x26AAA)
            emit(0x26AAA,0x26ABA);r[4]=base+index
            r[1]=signed(read(0x26AAC,r[4],1,1),8)&MASK
            r[0]=signed(read(0x26AAE,r[4]+1,0,1),8)&MASK;r[2]=r[0]&255;r[0]=r[1]&255;r[6]=0x26740
            control(0x26AB6,'jump',0x26740,True);value=interpolation(0x26740,row)
            lookups.append(dict(kind='implicit-byte-curve',index=index,fraction=remainder<<11,endpoint=False,**value))

    emit(0x4BA48,0x4BA5A);push(0x4BA48,r[13],13);push(0x4BA4A,r[14],14)
    push(0x4BA4C,pr);push(0x4BA4E,macl);r[6]=RAM_BASE+0x2470;r[13]=RAM_BASE+0x128C
    r[0]=load(0x4BA54,0x2478,1,0);override=bool(r[0]&2);t(not override)
    branch(0x4BA58,not override,0x4BA7A);mode='override' if override else 'curves'
    if override:
        emit(0x4BA5A,0x4BA62);r[0]=0x3CB;r[5]=0x886B;control(0x4BA5E,'jump',0x4BA64,True)
        emit(0x4BA64,0x4BA76);r[6]=load(0x4BA64,0x1657,1,6)
        r[0]=signed(read(0x4BA66,0x886D,0,1),8)&MASK;r[6]&=255;r[2]=(r[0]&255)*2
        r[6]=(r[6]-r[2])&MASK;r[2]=signed(r[6]&65535,16)&MASK
        nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x4BA74,nonnegative,0x4BB5C)
        if not nonnegative:
            emit(0x4BA76,0x4BA7A);control(0x4BA76,'jump',0x4BB5C,True);r[2]=0
    else:
        emit(0x4BA7A,0x4BA8A);r[0]=0x370;r[2]=load(0x4BA7C,0x15FC,2,2)
        r[0]=0x372;r[2]&=65535;r[6]=load(0x4BA82,0x15FE,2,6);r[2]=(r[2]-r[6])&MASK
        nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x4BA88,nonnegative,0x4BA8C)
        if not nonnegative:emit(0x4BA8A);r[2]=0
        emit(0x4BA8C,0x4BA98);r[6]=RAM_BASE+0x2458;r[14]=r[2];r[2]=load(0x4BA90,0x2458,1,2)
        r[0]=r[2]&255;percentage=bool(r[0]&32);t(not percentage);branch(0x4BA96,not percentage,0x4BAC0)
        if percentage:
            mode='percentage';emit(0x4BA98,0x4BAB8);r[5]=0x886B
            r[6]=signed(read(0x4BA9A,0x886B,6,1),8)&MASK;r[2]=r[6]&255;macl=(r[2]*r[14])&MASK
            r[6]=100;r[2]=macl;macl=(r[2]*r[6])&MASK;r[2]=255;r[6]=macl>>14
            above=r[6]>255;t(above);branch(0x4BAB6,not above,0x4BABA)
            if above:emit(0x4BAB8);r[6]=MASK
            emit(0x4BABA,0x4BAC0);r[0]=0x3CB;put(0x4BABE,0x1657,1,6,r[6])
            control(0x4BABC,'jump',0x4BB60,True)
        else:
            emit(0x4BAC0,0x4BAD6);r[2]=RAM_BASE+0x1024;r[5]=255;r[6]=load(0x4BAC6,0x1024,2,6)
            r[2]=(r[6]&65535)>>7;above=r[2]>255;t(above);branch(0x4BAD4,above,0x4BAD8)
            if not above:emit(0x4BAD6);r[5]=r[2]
            emit(0x4BAD8,0x4BAE2);r[4]=0x126A8;r[5]&=255;r[7]=0x26370
            row=call(0x4BADE,0x26370);implicit_curve(row)
            emit(0x4BAE2,0x4BAF8);r[2]=r[0];r[0]=0x3CD;put(0x4BAE6,0x1659,1,2,r[2])
            r[0]=32;r[2]=RAM_BASE+0x119C;r[6]=load(0x4BAEC,0x11BC,2,6);r[5]=r[6]&65535
            r[2]=(r[5]-32)&MASK;nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x4BAF6,nonnegative,0x4BAFC)
            if not nonnegative:
                emit(0x4BAF8,0x4BAFC);r[5]=0;control(0x4BAF8,'jump',0x4BAFE,True)
            else:emit(0x4BAFC);r[5]=(r[5]-32)&MASK
            emit(0x4BAFE,0x4BB06);r[2]=255;above=r[5]>255;t(above);branch(0x4BB04,not above,0x4BB08)
            if above:emit(0x4BB06);r[5]=MASK
            emit(0x4BB08,0x4BB10);r[4]=0x126A0;r[7]=0x26370;r[5]&=255
            row=call(0x4BB0C,0x26370);implicit_curve(row)
            emit(0x4BB10,0x4BB42);r[2]=r[0];r[0]=0x3CC;put(0x4BB14,0x1658,1,2,r[2]);r[2]&=255
            r[0]=0x3CD;r[5]=load(0x4BB1A,0x1659,1,5);r[6]=r[5]&255
            macl=(r[6]&65535)*(r[2]&65535);r[6]=100;r[2]=macl
            macl=(r[14]*r[6])&MASK;r[2]&=65535;r[5]=macl;r[6]=r[5]&65535
            macl=(r[2]*r[6])&MASK;r[5]=(r[5]>>16)&65535;r[4]=macl
            macl=(r[2]*r[5])&MASK;r[6]=65535;r[2]=macl;r[4]>>=16
            above=r[2]>65535;t(above);branch(0x4BB40,above,0x4BB44)
            if not above:emit(0x4BB42);r[6]=r[2]
            emit(0x4BB44,0x4BB5A);r[4]&=65535;r[2]=r[6]&65535;r[4]=(r[4]+r[2])&MASK
            r[4]>>=5;r[6]=255;above=r[4]>255;t(above);branch(0x4BB56,not above,0x4BB5C,True);r[2]=r[4]
            if above:emit(0x4BB5A);r[2]=MASK
    if mode!='percentage':
        emit(0x4BB5C,0x4BB60);r[0]=0x3CB;put(0x4BB5E,0x1657,1,2,r[2])
    emit(0x4BB60,0x4BB6A);macl=pop(0x4BB60);pr=pop(0x4BB62);r[14]=pop(0x4BB64,14);r[13]=pop(0x4BB68,13)
    control(0x4BB66,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,mode=mode,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
