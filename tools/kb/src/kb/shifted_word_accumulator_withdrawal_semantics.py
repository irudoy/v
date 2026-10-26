"""Independent gate, product, bounded shift and saturated accumulator state equations."""

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):
    return value-(1<<bits) if value&(1<<(bits-1)) else value


def accumulation(gate,native_gate,metric,word,prior,factor,shift,threshold):
    if any(type(value) is not int or not 0<=value<=limit for value,limit in (
            (gate,255),(native_gate,255),(metric,255),(word,65535),(prior,65535),
            (factor,255),(shift,255),(threshold,255))):
        raise ValueError('the accumulator equations require exact unsigned physical input widths')
    active=bool(gate&32) and bool(native_gate&64) and metric>threshold
    scale=word*factor//256
    product=(metric-threshold)*scale if active else 0
    shifted=product
    count=0
    capped=False
    if active and shift:
        while count<shift or count<8:
            if shifted>=0x800000:
                shifted=0xFFFFFF;capped=True;break
            shifted*=2;count+=1
    updated=0 if not gate&32 else min(65535,prior+(shifted>>16)) if active else prior
    return dict(active=active,scale=scale,product=product,shifted=shifted,count=count,
        capped=capped,increment=shifted>>16 if active else 0,updated=updated,
        final_saturated=active and prior+(shifted>>16)>65535)


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    if (type(entry) is not int or entry!=0xA5398 or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(value) is not int or not 0<=value<=MASK for value in context)
            or type(sp) is not int or sp&3 or type(sr_before) is not int
            or sr_before&0x3F1!=context[18] or type(continuation) is not int):
        raise ValueError('the accumulator equations lose complete independent incoming CPU/RAM/frame state')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];sr=sr_before
    tags=accumulation(memory[0x244F],memory[0x84C3],memory[0x338A],
        int.from_bytes(memory[0x1040:0x1042],'big'),int.from_bytes(memory[0x3334:0x3336],'big'),
        calibration[0x83EC][0],calibration[0x8A0D][0],calibration[0x8CBA][0])

    def emit(first,last=None):path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the accumulator equations duplicate an exact physical instruction operand')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,
            register=register,domain=domain,bytes=raw.hex())

    def load(site,at,width,register,native=False):
        raw=bytes(ram[at:at+width]);event(site,'read',
            (0xFFFF0000 if native else RAM_BASE)+at,width,register,'native-control' if native else 'ram',raw)
        return signed(int.from_bytes(raw,'big'),width*8)&MASK if width<4 else int.from_bytes(raw,'big')

    def rom(site,address,width,register):
        spans=[(at,raw) for at,raw in calibration.items() if at<=address and address+width<=at+len(raw)]
        if len(spans)!=1:raise ValueError('the accumulator equations omit a complete physical ROM operand')
        at,raw=spans[0];raw=raw[address-at:address-at+width]
        event(site,'read',address,width,register,'rom',raw)
        return signed(int.from_bytes(raw,'big'),width*8)&MASK if width<4 else int.from_bytes(raw,'big')

    def t(value):
        nonlocal sr
        sr=(sr&~1)|int(bool(value))

    def branch(site,taken,target,delay=False):
        controls.append(dict(site=site,kind='taken' if taken else 'fallthrough',
            target=target if taken else site+(4 if delay else 2),delay=delay))

    def jump(site,target,kind='jump'):
        controls.append(dict(site=site,kind=kind,target=target,delay=True))

    def store(site,register):
        raw=(r[register]&65535).to_bytes(2,'big');ram[0x3334:0x3336]=raw
        event(site,'write',RAM_BASE+0x3334,2,register,'ram',raw)

    emit(0xA5398,0xA53A2)
    frame[156:160]=context[17].to_bytes(4,'big')
    event(0xA5398,'write',sp-4,4,None,'frame',bytes(frame[156:160]))
    r[6]=RAM_BASE+0x244F;r[0]=load(0xA539C,0x244F,1,0)
    inactive=not bool(r[0]&32);t(inactive);branch(0xA53A0,inactive,0xA5430)
    if inactive:
        emit(0xA5430,0xA5438);r[3]=RAM_BASE+0x28F8;r[2]=0;r[0]=0xA3C;store(0xA5436,2)
    else:
        emit(0xA53A2,0xA53AA);r[6]=0xFFFF84C3;r[0]=load(0xA53A4,0x84C3,1,0,True)
        inhibited=not bool(r[0]&64);t(inhibited);branch(0xA53A8,inhibited,0xA5438)
        if not inhibited:
            emit(0xA53AA,0xA53BC);r[2]=RAM_BASE+0x28F8;r[0]=0xA92
            r[4]=load(0xA53AE,0x338A,1,4)&255;r[2]=0x8CBA
            r[5]=rom(0xA53B4,0x8CBA,1,5)&255
            greater=r[4]>r[5];t(greater);branch(0xA53BA,not greater,0xA5438)
            if greater:
                emit(0xA53BC,0xA53D6);r[6]=RAM_BASE+0x102C;r[2]=0x83EC
                r[0]=load(0xA53C0,0x1040,2,0);r[6]=rom(0xA53C2,0x83EC,1,6)
                r[7]=r[0]&65535;r[2]=(r[6]&255)*r[7]//256;r[6]=65535
                # A uint16 times uint8 divided by 256 is at most 65279.
                t(False);branch(0xA53D4,True,0xA53D8)
                emit(0xA53D8,0xA53EA);r[6]=r[2]&65535;r[2]=0x8A0D;r[4]-=r[5]
                product=r[4]*r[6];r[7]=rom(0xA53E0,0x8A0D,1,7)&255
                zero=r[7]==0;t(zero);branch(0xA53E6,zero,0xA540E,True);r[5]=product
                if not zero:
                    emit(0xA53EA,0xA53F4);r[4]=0x800000;r[6]=0;r[1]=8
                    while True:
                        emit(0xA53F4,0xA53FA);r[6]&=255;enough=r[6]>=r[7]
                        t(enough);branch(0xA53F8,not enough,0xA53FE)
                        if enough:
                            emit(0xA53FA,0xA53FE);complete=r[6]>=r[1];t(complete)
                            branch(0xA53FC,complete,0xA540E)
                            if complete:break
                        emit(0xA53FE,0xA5402);capped=r[5]>=r[4];t(capped)
                        branch(0xA5400,not capped,0xA5408)
                        if capped:
                            emit(0xA5402,0xA5408);r[5]=0xFFFFFF;jump(0xA5404,0xA540E);break
                        emit(0xA5408,0xA540E);t(bool(r[5]&0x80000000));r[5]=(r[5]*2)&MASK
                        r[6]=(r[6]+1)&MASK;jump(0xA540A,0xA53F4)
                emit(0xA540E,0xA5424);r[3]=RAM_BASE+0x28F8;r[2]=r[5]>>16;r[0]=0xA3C
                prior=load(0xA5416,0x3334,2,5)&65535;r[5]=prior+r[2];r[2]=65535
                overflow=r[5]>65535;t(overflow);branch(0xA5422,not overflow,0xA5426)
                if overflow:emit(0xA5424);r[5]=MASK
                emit(0xA5426,0xA5430);r[3]=RAM_BASE+0x28F8;r[0]=0xA3C
                store(0xA542A,5);jump(0xA542C,0xA5438)
    emit(0xA5438,0xA543C);jump(0xA5438,continuation,'return')
    event(0xA543A,'read',sp-4,4,None,'frame',bytes(frame[156:160]))
    if int.from_bytes(ram[0x3334:0x3336],'big')!=tags['updated']:
        raise ValueError('the accumulator state composition disagrees with its separate numerical equation')
    return dict(registers=tuple(value&MASK for value in r),sr=sr,pr=continuation,
        macl=context[17],mach=context[16],gbr=context[15],sp=sp,frame=bytes(frame),ram=bytes(ram),
        path=tuple(path),events=events,controls=controls,calls=[],tags=tags)
