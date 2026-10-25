"""Separate clipped-byte curve, unsigned minimum and two exact saturating word sums."""

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
    if (type(entry) is not int or entry!=0x464DE
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the byte sum caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the byte sum caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the byte sum caller equation loses one authoritative physical preimage')
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
        if base!=0x128D8:raise ValueError('the implicit curve changes its exact natural eight-byte root')
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

    emit(0x464DE,0x464EE);push(0x464DE,r[14],14);push(0x464E0,pr)
    r[2]=RAM_BASE+0x22DC;r[5]=40;r[0]=load(0x464E6,0x22E4,1,0);r[6]=r[0]&255
    inside=r[6]>=40;t(inside);branch(0x464EC,inside,0x464F2)
    if not inside:
        emit(0x464EE,0x464F2);r[5]=0;control(0x464EE,'jump',0x46544,True)
    else:
        emit(0x464F2,0x46500);r[2]=(r[6]-40)*4;r[5]=255;above=r[2]>255;t(above)
        branch(0x464FE,not above,0x4653C)
        if above:
            emit(0x46500,0x46504);r[2]=r[5];control(0x46500,'jump',0x46542,True)
        else:emit(0x4653C,0x46542);r[6]=(r[6]-40)*4;r[2]=r[6]
        emit(0x46542);r[5]=r[2]
    emit(0x46544,0x4654E);r[4]=0x128D8;r[2]=0x26370;r[14]=RAM_BASE+0x128C;r[5]&=255
    row=call(0x4654A,0x26370);implicit_curve(row)
    emit(0x4654E,0x46576);r[6]=r[0]&255;r[0]=0x48A;put(0x46552,0x1716,1,6,r[6])
    r[0]=0x4B5;r[7]=load(0x46556,0x1741,1,7);r[0]=0x4C3;r[7]&=255
    r[2]=load(0x4655C,0x174F,1,2);r[0]=0x4B6;r[5]=r[2]&255;r[2]=r[7]
    r[4]=load(0x46564,0x1742,1,4);r[2]=(r[2]+r[5])&MASK;r[0]=0x4B0;r[4]&=255;r[2]=(r[2]+r[4])&MASK
    above=r[4]>r[6];t(above);put(0x46570,0x173C,2,2,r[2]);branch(0x46572,not above,0x46578,True);r[2]=r[4]
    if above:emit(0x46576);r[2]=r[6]
    emit(0x46578,0x4658C);r[0]=0x4C0;r[2]&=65535;r[7]=(r[7]+r[2])&MASK
    r[2]=load(0x4657E,0x174C,2,2);r[5]=65535;r[2]&=65535;r[2]=(r[2]+r[7])&MASK
    above=r[2]>65535;t(above);branch(0x4658A,not above,0x4658E)
    if above:emit(0x4658C);r[2]=r[5]
    emit(0x4658E,0x465A2);r[0]=0x4B2;put(0x46590,0x173E,2,2,r[2]);r[2]&=65535
    r[0]=0x4B4;r[6]=load(0x46596,0x1740,1,6);r[4]=r[6]&255;r[2]=(r[2]+r[4])&MASK
    above=r[2]>r[5];t(above);branch(0x4659E,not above,0x465A4,True);r[6]=r[2]
    if above:emit(0x465A2);r[6]=r[5]
    emit(0x465A4,0x465AE);r[0]=0x4BC;put(0x465A6,0x1748,2,6,r[6]);pr=pop(0x465A8);r[14]=pop(0x465AC,14)
    control(0x465AA,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
