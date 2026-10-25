"""Separate complete paired flag callers,ordered byte RMW operands and real nibble helper."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0x7C8FA,0x7C9A8)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the paired flag writer caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        events.setdefault(index,[]).append(dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex()))

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the paired flag writer caller equation loses one authoritative physical preimage')
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

    def load(site,address,width,register):
        raw=bytes(ram[address:address+width]);event(site,'read',RAM_BASE+address,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,address,width,register,value):
        ram[address:address+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+address,width,register,'ram',bytes(ram[address:address+width]))

    def rmw(site,address,mask,kind):
        raw=bytes(ram[address:address+1]);event(site,'read',RAM_BASE+address,1,None,'ram',raw)
        value=raw[0]|mask if kind=='or' else raw[0]&mask
        ram[address]=value;event(site,'write',RAM_BASE+address,1,None,'ram',bytes([value]))

    def nibble(row):
        emit(0x7D84C,0x7D856);r[6]=RAM_BASE+0x5B33;r[0]=load(0x7D84E,0x5B33,1,0)&15
        put(0x7D854,0x5B33,1,0,r[0]);control(0x7D852,'return',pr,True);returned(row,0x7D852)

    def first_caller():
        nonlocal stack,gbr,pr
        emit(0x7C8FA,0x7C90C);push(0x7C8FA,pr);push(0x7C8FC,gbr);r[0]=gbr=RAM_BASE+0x5718
        r[6]=RAM_BASE+0x41A9;r[0]=0x1C;r[0]=load(0x7C906,0x41C5,1,0)
        active=bool(r[0]&32);t(not active);branch(0x7C90A,not active,0x7C9A0)
        if not active:return
        emit(0x7C90C,0x7C914);r[0]=0x26;r[0]=load(0x7C90E,0x41CF,1,0)
        blocked=bool(r[0]&32);t(not blocked);branch(0x7C912,blocked,0x7C9A0)
        if blocked:return
        emit(0x7C914,0x7C938);r[5]=RAM_BASE+0x5B2A
        for site,offset in ((0x7C918,0x31),(0x7C91C,0x2E),(0x7C920,0x2B),(0x7C924,0x28),
                (0x7C928,0x25),(0x7C92C,0x22),(0x7C930,0x1F)):
            r[0]=offset;rmw(site,0x5718+offset,4,'or')
        r[0]=load(0x7C932,0x5B2C,1,0);blocked=bool(r[0]&8);t(not blocked);branch(0x7C936,blocked,0x7C9A0)
        if blocked:return
        emit(0x7C938,0x7C94E);r[0]=0x2B;r[4]=RAM_BASE+0x4558;r[0]=load(0x7C93C,0x41D4,1,0)&0xDF
        r[2]=r[0];r[0]=0x2B;put(0x7C944,0x41D4,1,2,r[2]);r[2]=0
        r[0]=load(0x7C948,0x5B2B,1,0)&0xBF;put(0x7C94C,0x5B2B,1,0,r[0])
        emit(0x7C94E,0x7C96A)
        for site,offset in ((0x7C950,0x32),(0x7C954,0x2F),(0x7C958,0x2C),(0x7C95C,0x29),
                (0x7C960,0x26),(0x7C964,0x23),(0x7C968,0x20)):
            r[0]=offset;rmw(site,0x5718+offset,0xBF,'and')
        emit(0x7C96A,0x7C98E);r[0]=0x56E;put(0x7C96C,0x4AC6,1,2,0);r[0]=0x4ED;put(0x7C970,0x4A45,1,2,0)
        r[0]=0x518;put(0x7C974,0x4A70,2,2,0);r[0]=load(0x7C976,0x5B2A,1,0)&0xFB;put(0x7C97A,0x5B2A,1,0,r[0])
        r[0]=0x18;r[0]=load(0x7C97E,0x41C1,1,0)&0xFD;r[2]=r[0];r[0]=0x18;put(0x7C986,0x41C1,1,2,r[2]);r[2]=0
        r[0]=0x36A;put(0x7C98C,0x48C2,1,2,0)
        emit(0x7C98E,0x7C996);r[0]=load(0x7C98E,0x5B33,1,0);blocked=bool(r[0]&128);t(not blocked);r[2]=r[0]
        branch(0x7C992,blocked,0x7C9A0,True)
        if blocked:return
        emit(0x7C996,0x7C99C);r[0]=r[2];active=bool(r[0]&32);t(not active);branch(0x7C99A,not active,0x7C9A0)
        if active:
            emit(0x7C99C,0x7C9A0);row=call(0x7C99C,0x7D84C);nibble(row)

    def second_caller():
        nonlocal stack,gbr,pr
        emit(0x7C9A8,0x7C9BA);push(0x7C9A8,pr);push(0x7C9AA,gbr);r[0]=gbr=RAM_BASE+0x5718
        r[5]=RAM_BASE+0x41A9;r[0]=0x2F;r[0]=load(0x7C9B4,0x41D8,1,0)
        active=bool(r[0]&32);t(not active);branch(0x7C9B8,not active,0x7CA50)
        if not active:return
        emit(0x7C9BA,0x7C9C2);r[0]=0x12;r[0]=load(0x7C9BC,0x41BB,1,0)
        blocked=bool(r[0]&64);t(not blocked);branch(0x7C9C0,blocked,0x7CA50)
        if blocked:return
        emit(0x7C9C2,0x7C9D0);r[2]=RAM_BASE+0x28F8;r[0]=0x820;r[5]=0x885D;r[6]=load(0x7C9C8,0x3118,1,6)
        r[2]=signed(read(0x7C9CA,0x885D,2,1),8)&MASK;blocked=r[6]>=r[2];t(blocked);branch(0x7C9CE,blocked,0x7CA50)
        if blocked:return
        emit(0x7C9D0,0x7C9F4);r[6]=RAM_BASE+0x5B2A
        for site,offset in ((0x7C9D4,0x31),(0x7C9D8,0x2E),(0x7C9DC,0x2B),(0x7C9E0,0x28),
                (0x7C9E4,0x25),(0x7C9E8,0x22),(0x7C9EC,0x1F)):
            r[0]=offset;rmw(site,0x5718+offset,4,'or')
        r[0]=load(0x7C9EE,0x5B2C,1,0);blocked=bool(r[0]&8);t(not blocked);branch(0x7C9F2,blocked,0x7CA50)
        if blocked:return
        emit(0x7C9F4,0x7CA0C);r[5]=RAM_BASE+0x41A9;r[0]=0x2B;r[0]=load(0x7C9F8,0x41D4,1,0)&0xF7
        r[2]=r[0];r[0]=0x2B;put(0x7CA00,0x41D4,1,2,r[2]);r[2]=0;r[0]=load(0x7CA04,0x5B2B,1,0)
        r[5]=RAM_BASE+0x4558;r[0]&=0xEF;put(0x7CA0A,0x5B2B,1,0,r[0])
        emit(0x7CA0C,0x7CA28)
        for site,offset in ((0x7CA0E,0x32),(0x7CA12,0x2F),(0x7CA16,0x2C),(0x7CA1A,0x29),
                (0x7CA1E,0x26),(0x7CA22,0x23),(0x7CA26,0x20)):
            r[0]=offset;rmw(site,0x5718+offset,0xBF,'and')
        emit(0x7CA28,0x7CA3E);r[0]=0x570;put(0x7CA2A,0x4AC8,1,2,0);r[0]=0x4EF;put(0x7CA2E,0x4A47,1,2,0)
        r[0]=0x51C;put(0x7CA32,0x4A74,2,2,0);r[0]=load(0x7CA34,0x5B2B,1,0)&0x7F;put(0x7CA38,0x5B2B,1,0,r[0])
        r[0]=0x36C;put(0x7CA3C,0x48C4,1,2,0)
        emit(0x7CA3E,0x7CA46);r[0]=load(0x7CA3E,0x5B33,1,0);blocked=bool(r[0]&128);t(not blocked);r[2]=r[0]
        branch(0x7CA42,blocked,0x7CA50,True)
        if blocked:return
        emit(0x7CA46,0x7CA4C);r[0]=r[2];active=bool(r[0]&32);t(not active);branch(0x7CA4A,not active,0x7CA50)
        if active:
            emit(0x7CA4C,0x7CA50);row=call(0x7CA4C,0x7D84C);nibble(row)

    if entry==0x7C8FA:
        first_caller();emit(0x7C9A0,0x7C9A8);gbr=pop(0x7C9A0);pr=pop(0x7C9A2);control(0x7C9A4,'return',pr,True)
    else:
        second_caller();emit(0x7CA50,0x7CA58);gbr=pop(0x7CA50);pr=pop(0x7CA52);control(0x7CA54,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
