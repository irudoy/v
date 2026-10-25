"""Separate complete state-monitor gates,absolute differences,unordered clamp and refresh."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry!=0x39316
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the clamp latch caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the clamp latch caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the clamp latch caller equation loses one authoritative physical preimage')
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

    def load(site,at,width,register):
        raw=bytes(ram[at:at+width]);event(site,'read',RAM_BASE+at,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,at,width,register,value):
        ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+at,width,register,'ram',bytes(ram[at:at+width]))

    def absolute(row):
        incoming=signed(r[4]);positive=incoming>0
        emit(0x22590,0x22594);t(positive);branch(0x22592,positive,0x22596)
        if not positive:emit(0x22594);r[4]=(-r[4])&MASK
        emit(0x22596,0x2259A);r[0]=r[4]
        control(0x22596,'return',pr,True);returned(row,0x22596)
        return r[0]

    def monitor(mode):
        emit(0x39334,0x3933C);r[5]=RAM_BASE+0x4185;r[0]=load(0x39336,0x4185,1,0)
        blocked=not bool(r[0]&128);t(blocked);branch(0x3933A,blocked,0x393E4)
        if blocked:return
        emit(0x3933C,0x39340);blocked=bool(r[0]&64);t(not blocked);branch(0x3933E,blocked,0x393E4)
        if blocked:return
        for first,at,base,mask,requires_set in (
                (0x39340,0x2451,0x2451,32,True),(0x39348,0x2449,0x2449,128,False),
                (0x39350,0x4250,0x424C,64,False)):
            emit(first,first+8);r[5]=RAM_BASE+base;r[0]=load(first+2,at,1,0)
            bit=bool(r[0]&mask);t(not bit);blocked=not bit if requires_set else bit
            branch(first+6,blocked,0x393E4)
            if blocked:return
        emit(0x39358,0x3935C);t(not bool(r[2]));branch(0x3935A,not bool(r[2]),0x393A0)
        direct=False
        if mode:
            emit(0x3935C,0x39370);r[6]=RAM_BASE+0x11D4;r[0]=0x16
            r[2]=load(0x39360,0x11EA,1,2);r[6]=RAM_BASE+0x22DC;r[4]=r[2]&255
            r[0]=load(0x39366,0x22E4,1,0);r[6]=0x22590;r[2]=r[0]&255;r[4]=(r[4]-r[2])&MASK
            first=absolute(call(0x3936C,0x22590))
            emit(0x39370,0x39376);r[6]=10;large=signed(r[0])>=10;t(large);branch(0x39374,large,0x393A0)
            if not large:
                emit(0x39376,0x3938E);r[6]=RAM_BASE+0x1048;r[5]=RAM_BASE+0x1E60
                r[0]=load(0x3937A,0x1062,2,0);r[6]=0x22590;r[4]=r[0]&65535
                r[0]=0x51;r[0]<<=2;r[2]=load(0x39384,0x1FA4,2,2)
                r[4]=(r[4]<<2)&MASK;r[2]&=65535;r[4]=(r[4]-r[2])&MASK
                second=absolute(call(0x3938A,0x22590))
                emit(0x3938E,0x39396);r[6]=128;large=signed(r[0])>=128;t(large);branch(0x39394,large,0x393A0)
                if not large:
                    emit(0x39396,0x393A0);r[5]=RAM_BASE+0x256A;r[0]=0x69;r[2]=load(0x3939A,0x25D3,1,2)
                    direct=r[2]==0;t(direct);branch(0x3939E,direct,0x393B0)
        if not direct:
            emit(0x393A0,0x393B0);r[2]=RAM_BASE+0x1114;r[0]=0x6A
            r[6]=load(0x393A4,0x117E,2,6);r[0]=load(0x393A6,0x55E6,1,0);r[6]&=65535;r[2]=r[0]&255
            blocked=r[6]>=r[2];t(blocked);branch(0x393AE,blocked,0x393E4)
            if blocked:return
        emit(0x393B0,0x393C8);r[0]=load(0x393B0,0x55E6,1,0);r[5]=RAM_BASE+0x1E60;r[6]=r[0]&255;r[4]=0x8692
        r[0]=0xFFFFFF82;r[0]&=255;r[2]=load(0x393BC,0x1EE2,2,2)
        r[5]=signed(read(0x393BE,0x8692,5,1),8)&MASK;r[6]=(r[6]+r[2])&MASK;r[0]=r[5]&255
        total=signed(r[6]);lower=r[0];at_least_lower=total>=lower;t(at_least_lower)
        branch(0x393C6,not at_least_lower,0x393D2)
        upper=None
        if at_least_lower:
            emit(0x393C8,0x393D0);r[0]=signed(read(0x393C8,0x8693,0,1),8)&MASK;r[0]&=255
            upper=r[0];at_least_upper=total>=upper;t(at_least_upper);branch(0x393CE,at_least_upper,0x393D2)
            if not at_least_upper:emit(0x393D0);r[0]=r[6]
        clamped=r[0]&255
        lookups.append(dict(kind='ordered-conditions-with-unordered-byte-limits',total=total,lower=lower,upper=upper,value=clamped))
        emit(0x393D2,0x393E4);r[6]=RAM_BASE+0x421C;put(0x393D4,0x55E6,1,0,r[0]);r[0]=0x13
        r[0]=load(0x393D8,0x422F,1,0);r[5]=RAM_BASE+0x421C;r[0]|=4;r[2]=r[0];r[0]=0x13
        put(0x393E2,0x422F,1,2,r[2])

    emit(0x39316,0x3932A);push(0x39316,pr);push(0x39318,gbr)
    gbr=r[0]=RAM_BASE+0x55BC;r[6]=RAM_BASE+0x2459;r[0]=load(0x39320,0x2459,1,0)&32
    mode=bool(r[0]);t(not mode);branch(0x39326,mode,0x39334,True);r[2]=r[0]
    if not mode:
        emit(0x3932A,0x39334);r[5]=0x8B7E;r[0]=0x69;r[6]=signed(read(0x3932E,0x8B7E,6,1),8)&MASK
        r[5]=RAM_BASE+0x256A;put(0x39332,0x25D3,1,6,r[6])
    monitor(mode)
    emit(0x393E4,0x393F8);r[6]=RAM_BASE+0x1026;r[0]=0x51;r[5]=RAM_BASE+0x1E60;r[0]<<=2
    r[2]=load(0x393EC,0x1026,2,2);put(0x393EE,0x1FA4,2,2,r[2]);gbr=pop(0x393F0);pr=pop(0x393F2)
    control(0x393F4,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
