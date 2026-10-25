"""Separate complete counter-rate caller,real unsigned divider and full auxiliary gate."""
MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry not in (0x68D58,)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the auxiliary rate caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the auxiliary rate caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the auxiliary rate caller equation loses one authoritative physical preimage')
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

    def unsigned_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if not 0<divisor<=65535 or not 0<=numerator<=MASK:
            raise ValueError('the actual auxiliary rate unsigned helper loses its positive bounded variable divisor')
        long_path=numerator>=divisor*256;saved_r2,saved_r3=r[2],r[3]
        emit(0x21CE0,0x21CF4);push(0x21CE0,saved_r2,2)
        branch(0x21CE4,False,0x21D6A);branch(0x21CEA,False,0x21D76);branch(0x21CF2,long_path,0x21D0C)
        if long_path:
            emit(0x21D0C,0x21D6A);push(0x21D0C,saved_r3,3)
            pop(0x21D64,3);pop(0x21D68,2);terminal=0x21D66
        else:
            emit(0x21CF4,0x21D0C);pop(0x21D06,2);terminal=0x21D08
        r[0]=numerator//divisor;r[1]=None;r[2],r[3]=saved_r2,saved_r3
        sr&=~0x301;sr_mask&=~0x101
        row.update(divisor=divisor,dividend=numerator,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    def auxiliary_gate(row):
        nonlocal stack,gbr
        emit(0x8C3FA,0x8C40A);push(0x8C3FA,gbr);r[0]=gbr=RAM_BASE+0x4184;stack-=4
        r[0]=load(0x8C402,0x4184,1,0);blocked=bool(r[0]&64);t(not blocked)
        branch(0x8C406,blocked,0x8C43E,True);r[1]=0
        local=False
        if not blocked:
            emit(0x8C40A,0x8C412);r[6]=RAM_BASE+0x244F;r[0]=load(0x8C40C,0x244F,1,0)
            enabled=bool(r[0]&32);t(not enabled);branch(0x8C410,not enabled,0x8C43E)
            if enabled:
                emit(0x8C412,0x8C41C);r[0]=load(0x8C412,0x41A5,1,0);r[6]=1
                active=bool(r[0]&4);t(not active);branch(0x8C418,not active,0x8C43C,True)
                frame_access(0x8C41A,'write',stack,4,6,r[6]);local=True
                if active:
                    emit(0x8C41C,0x8C422);r[0]=load(0x8C41C,0x41BD,1,0)
                    blocked=bool(r[0]&1);t(not blocked);branch(0x8C420,blocked,0x8C43C)
                    if not blocked:
                        emit(0x8C422,0x8C42E);r[5]=RAM_BASE+0x28F8;r[4]=20;r[0]=0xBEC
                        r[2]=load(0x8C428,0x34E4,2,2);high=r[2]>=r[4];t(high);branch(0x8C42C,high,0x8C43C)
                        if not high:
                            emit(0x8C42E,0x8C438);r[0]=0xBEE;r[2]=load(0x8C430,0x34E6,2,2)&65535
                            high=r[2]>=r[4];t(high);branch(0x8C436,high,0x8C43C)
                            if not high:
                                emit(0x8C438,0x8C43C);r[6]=0;frame_access(0x8C43A,'write',stack,4,6,0)
        if local:emit(0x8C43C);r[1]=frame_access(0x8C43C,'read',stack,4,1)
        emit(0x8C43E,0x8C446);r[0]=r[1]&255;stack+=4;gbr=pop(0x8C444)
        control(0x8C442,'return',pr,True);returned(row,0x8C442)

    def natural_caller():
        nonlocal stack,gbr,macl
        emit(0x68D58,0x68D6C);push(0x68D58,pr);push(0x68D5A,macl);push(0x68D5C,gbr)
        r[0]=gbr=RAM_BASE+0x1FF4;stack-=8;r[6]=RAM_BASE+0x24C0;r[0]=load(0x68D66,0x24C0,1,0)
        active=bool(r[0]&4);t(not active);branch(0x68D6A,not active,0x68DDC)
        if not active:return
        emit(0x68D6C,0x68D74);r[4]=RAM_BASE+0x424C;r[0]=load(0x68D6E,0x4251,1,0)
        initialize=bool(r[0]&1);t(not initialize);branch(0x68D72,not initialize,0x68D82)
        if initialize:
            emit(0x68D74,0x68D82);r[2]=400;r[5]=RAM_BASE+0x2330;r[0]=44
            put(0x68D7C,0x235C,2,2,r[2]);r[0]=0;put(0x68D80,0x2018,2,0,0)
        emit(0x68D82,0x68D8E);r[5]=RAM_BASE+0x2330;r[0]=44;r[6]=load(0x68D86,0x235C,2,6)&65535
        empty=r[6]==0;t(empty);branch(0x68D8C,empty,0x68DC4)
        if not empty:
            emit(0x68D8E,0x68DA2);r[0]=load(0x68D8E,0x2018,2,0)
            frame_access(0x68D90,'write',stack+4,4,0,r[0]);frame_access(0x68D92,'write',stack,4,0,r[0])
            r[0]=load(0x68D94,0x201A,2,0);r[5]=r[0]&65535;r[0]=4000
            macl=(r[6]*r[5])&MASK;r[6]=0x21CE0;r[1]=macl
            row=call(0x68D9E,0x21CE0);unsigned_divider(row)
            emit(0x68DA2,0x68DB4);r[6]=r[0];r[0]=load(0x68DA4,0x201A,2,0)
            r[2]=frame_access(0x68DA6,'read',stack,4,2);r[5]=r[0]&65535;r[6]=(r[6]+r[2])&MASK
            r[2]=(r[5]-125)&MASK;above=signed(r[6])>signed(r[2]);t(above);branch(0x68DB2,not above,0x68DB8)
            if above:emit(0x68DB4,0x68DB8);r[5]=(r[5]-125)&MASK;r[6]=r[5]
            emit(0x68DB8,0x68DBE);r[2]=125;at_least=signed(r[6])>=r[2];t(at_least)
            branch(0x68DBC,at_least,0x68DC0)
            if not at_least:emit(0x68DBE);r[6]=125
            emit(0x68DC0,0x68DC4);control(0x68DC0,'jump',0x68DC6,True);r[0]=r[6]
        else:emit(0x68DC4);r[0]=0
        emit(0x68DC6,0x68DCC);r[2]=0x8C3FA;put(0x68DCA,0x201E,2,0,r[0])
        row=call(0x68DC8,0x8C3FA);auxiliary_gate(row)
        emit(0x68DCC,0x68DD0);empty=r[0]==0;t(empty);branch(0x68DCE,empty,0x68DDC)
        if empty:return
        emit(0x68DD0,0x68DD8);r[4]=RAM_BASE+0x424C;r[0]=load(0x68DD2,0x4251,1,0)
        initialized=bool(r[0]&1);t(not initialized);branch(0x68DD6,initialized,0x68DDC)
        if initialized:return
        emit(0x68DD8,0x68DDC);r[0]=0;put(0x68DDA,0x201E,2,0,0)

    natural_caller();emit(0x68DDC,0x68DE8);stack+=8;gbr=pop(0x68DDE);macl=pop(0x68DE0);pr=pop(0x68DE2)
    control(0x68DE4,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r) if value is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
