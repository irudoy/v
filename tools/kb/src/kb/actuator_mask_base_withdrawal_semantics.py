"""Independent fixed-record bit predicates, staged threshold masks and low-speed OR."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry!=0x5096C
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the actuator mask base equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the actuator mask base equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the actuator mask base equation loses one authoritative physical preimage')
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

    def record_predicate(row,identifier):
        if identifier not in (0x71,0x123) or r[4]!=identifier:
            raise ValueError('the record predicate changes either complete post-delay fixed identifier')
        # Both natural caller arguments are positive signed words and are not -1.
        # The generic indexed record annotation is resolved using the actual ID.
        emit(0x25E20,0x25E28);r[1]=RAM_BASE+0x5718;r[0]=identifier;t(False)
        branch(0x25E26,False,0x25E3E)
        emit(0x25E28,0x25E3E);r[6]=r[1]+3*identifier
        r[0]=load(0x25E32,0x5718+3*identifier+1,1,0)
        active=bool(r[0]&0x80);t(not active);r[0]=int(active);r[2]=r[0]
        control(0x25E3A,'jump',0x25E40,True)
        emit(0x25E40,0x25E44);control(0x25E40,'return',pr,True);returned(row,0x25E40)
        return active

    def staged_mask(row):
        emit(0x509A0,0x509AE);r[6]=RAM_BASE+0x119C;r[0]=0x17
        raw=load(0x509A4,0x11B3,1,2)&255;r[2]=raw
        thresholds=(43,44,45,46,47,48)
        level=sum(raw>=threshold for threshold in thresholds)
        mask=(0,1,5,7,15,31,63)[level]
        for index,head in enumerate((0x509A6,0x509B2,0x509BC,0x509C6,0x509D0,0x509DA)):
            if index:emit(head,head+6)
            r[6]=thresholds[index];taken=level>index;t(taken)
            site=head+(6 if index==0 else 4)
            target=(0x509B2,0x509BC,0x509C6,0x509D0,0x509DA,0x509E6)[index]
            branch(site,taken,target,index==5)
            if index==5:
                emit(0x509E0);r[0]=63
                terminal=0x509E6 if taken else 0x509E2
                emit(terminal,terminal+4);r[0]=mask
                control(terminal,'return',pr,True);returned(row,terminal);return mask
            if not taken:
                terminal=site+2;emit(terminal,terminal+4);r[0]=mask
                control(terminal,'return',pr,True);returned(row,terminal);return mask
        raise ValueError('the staged mask loses its finite six-threshold terminal')

    def low_speed_mask(row):
        emit(0x509EA,0x509F6);r[5]=RAM_BASE+0x1094;r[0]=0x7A;r[6]=2
        r[2]=load(0x509F0,0x110E,1,2);above=r[2]>2;t(above)
        branch(0x509F4,above,0x509FE)
        enabled=False
        if not above:
            emit(0x509F6,0x509FE);r[0]=0x50;r[0]=load(0x509F8,0x10E4,1,0)
            enabled=bool(r[0]&4);t(not enabled);branch(0x509FC,enabled,0x50A02)
        terminal=0x50A02 if enabled else 0x509FE
        emit(terminal,terminal+4);r[0]=63 if enabled else 0
        control(terminal,'return',pr,True);returned(row,terminal);return r[0]

    emit(0x5096C,0x50976);push(0x5096C,pr);stack-=4
    r[6]=0x25E20;r[4]=0x71
    first=record_predicate(call(0x50972,0x25E20),0x71)
    emit(0x50976,0x5097A);t(not first);branch(0x50978,first,0x5098A)
    second=False
    if not first:
        emit(0x5097A,0x50982);r[6]=0x25E20;r[4]=0x123
        second=record_predicate(call(0x5097E,0x25E20),0x123)
        emit(0x50982,0x50986);t(not second);branch(0x50984,second,0x5098A)
    if first or second:
        emit(0x5098A,0x5098E);staged=staged_mask(call(0x5098A,0x509A0))
        emit(0x5098E,0x50992)
        # The second BSR stores the first returned mask in its real delay slot.
        frame_access(0x50990,'write',stack,1,0,r[0])
        low=low_speed_mask(call(0x5098E,0x509EA))
        emit(0x50992,0x50998);r[2]=signed(frame_access(0x50992,'read',stack,1,2),8)&MASK
        r[2]|=r[0];r[0]=r[2]&255
        lookups.append(dict(kind='staged-mask-OR-low-speed-mask',staged=staged,low_speed=low,value=r[0]))
    else:
        emit(0x50986,0x5098A);control(0x50986,'jump',0x50998,True);r[0]=0
    emit(0x50998,0x509A0);stack+=4;pr=pop(0x5099A)
    control(0x5099C,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
