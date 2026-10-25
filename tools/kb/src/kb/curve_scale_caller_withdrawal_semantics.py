"""Separate32-knot curve, raw signed division, bias, saturation and complete caller composition."""

from kb import division_callees_semantics as division

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def words(raw,count):
    if type(raw) is not bytes or len(raw)!=2*count:
        raise ValueError('the word interpolation equation changes an exact physical calibration extent')
    return tuple(int.from_bytes(raw[i:i+2],'big') for i in range(0,len(raw),2))


def position(knots,coordinate):
    """Select the rightmost qualifying knot without a monotonicity premise."""
    if (type(coordinate) is not int or not 0<=coordinate<=65535 or len(knots) not in (16,32)
            or any(type(knot) is not int or not 0<=knot<=65535 for knot in knots)):
        raise ValueError('the backward word-axis equation changes an unsigned coordinate or physical word')
    scanned=[]
    for index in range(len(knots)-1,-1,-1):
        scanned.append(index)
        if coordinate==knots[index] or coordinate>knots[index] and index==len(knots)-1:
            return dict(index=index,fraction=0,scanned=tuple(scanned),bracket=False)
        if coordinate>knots[index]:
            denominator=knots[index+1]-knots[index]
            if denominator<=0 or not knots[index]<coordinate<knots[index+1]:
                raise ValueError('the rightmost word-axis bracket loses its positive actual divisor')
            numerator=(coordinate-knots[index])*65536
            return dict(index=index,fraction=numerator//denominator,scanned=tuple(scanned),
                bracket=True,denominator=denominator,numerator=numerator)
    return dict(index=0,fraction=0,scanned=tuple(scanned),bracket=False)


def linear(first,second,fraction):
    if any(type(v) is not int or not 0<=v<=65535 for v in (first,second,fraction)):
        raise ValueError('the word interpolation equation changes an unsigned operand width')
    magnitude=abs(second-first)*fraction//65536
    ascending=second>=first
    return dict(value=first+magnitude if ascending else first-magnitude,magnitude=magnitude,
        first=first,second=second,fraction=fraction,ascending=ascending)


def evaluate(entry,memory,calibration,context,sr_before,frame_before,sp,continuation):
    """Compose real helper summaries and physical events independently of instruction decoding."""
    if (type(entry) is not int or entry!=0xB7768
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the curve-scale caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the word caller equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the word caller equation loses one authoritative physical preimage')
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
            gbr=context[15],mach=context[16],macl=macl,sr=sr,sr_mask=sr_mask)
        calls.append(row);pr=site+4;control(site,'call',target,True);return row

    def returned(row,site):
        row.update(return_site=site,return_registers=tuple(r),return_sr=sr,return_sr_mask=sr_mask,
            return_gbr=context[15],return_mach=context[16],return_macl=macl)

    def fraction(target,row):
        nonlocal sr,sr_mask
        divisor,numerator=r[0],r[1]
        if not 0<divisor<=65535 or not 0<=numerator<divisor*65536:
            raise ValueError('the natural word-axis caller loses its positive bounded division premise')
        emit(target,target+6);t(False);branch(target+2,False,target+0x92)
        push(target+4,r[2],2)
        emit(target+6,target+0x92)
        r[0]=r[1]=numerator//divisor
        r[2]=pop(target+0x8C,2)
        sr&=~0x301;sr_mask&=~0x101
        control(target+0x8E,'return',pr,True);returned(row,target+0x8E)

    def axis(target,count,row):
        nonlocal pr
        base,coordinate=r[0],r[5];maximum=2*(count-1);r[3]=r[4]
        if r[4]!=maximum:raise ValueError('the word-axis wrapper changes its actual complete axis extent')
        source=next(data for at,data in calibration.items() if at==base)
        pos=position(words(source,count),coordinate);lookups.append(dict(kind='axis',target=target,base=base,**pos))
        emit(target)
        for index in pos['scanned']:
            emit(target+2,target+10);r[1]=read(target+2,base+2*index,1)
            equal=coordinate==r[1];t(equal);branch(target+8,equal,target+0x38)
            r[4]=2*index
            if equal:break
            emit(target+10,target+14);higher=coordinate>r[1];t(higher);branch(target+12,not higher,target+0x30)
            if higher:
                emit(target+14,target+18);last=index==count-1;t(last);branch(target+16,last,target+0x38)
                if last:break
                emit(target+18,target+42)
                r[5]=pos['numerator'];r[1]=read(target+24,base+2*index,1)
                next_word=read(target+26,base+2*index+2,0)
                r[0]=next_word-r[1];r[2]=0x26C78
                push(target+32,pr);r[1]=r[5]
                nested=call(target+38,r[2]);fraction(r[2],nested)
                emit(target+42,target+48);pr=pop(target+42)
                r[5]=r[0];control(target+44,'return',pr,True);returned(row,target+44)
                return pos
            emit(target+48,target+54);r[4]-=2;t(r[4]>=0);branch(target+52,r[4]>=0,target+2)
            if r[4]<0:emit(target+54);r[4]=0
        emit(target+56,target+60);r[5]=0;control(target+56,'return',pr,True);returned(row,target+56)
        return pos

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

    def curve(row):
        nonlocal pr
        base,axis_base,coordinate=r[4:7]
        emit(0x26524,0x26532);push(0x26524,pr);push(0x26526,r[4],4)
        r[0]=r[5];r[5]=coordinate&65535;r[7]=0x26984;r[4]=62
        nested=call(0x2652E,0x26984);pos=axis(0x26984,32,nested)
        emit(0x26532,0x26546);r[6]=pop(0x26532,6)+r[4]
        r[0]=signed(read(0x26536,r[6]+2,0),16)&MASK;r[2]=r[0]&65535;r[3]=r[5]
        r[1]=signed(read(0x2653C,r[6],1),16)&MASK;pr=pop(0x2653E)
        r[6]=0x26740;r[0]=r[1]&65535;control(0x26542,'jump',0x26740,True)
        value=interpolation(0x26740,row)
        lookups.append(dict(pos,kind='curve',base=base,axis=axis_base,coordinate=coordinate,**value))
        return value

    def signed_divider(row):
        nonlocal sr,sr_mask
        numerator=r[1];negative=bool(numerator&0x80000000);long_path=abs(signed(numerator))>=10000*256
        if r[0]!=10000:raise ValueError('the curve-scale signed call changes its immutable actual divisor')
        saved_r2,saved_r3,saved_r4=r[2],r[3],r[4]
        emit(0x21BBC,0x21BC2);push(0x21BBC,saved_r2,2);t(False);branch(0x21BC0,False,0x21C70)
        emit(0x21BC2,0x21BCC);push(0x21BC2,saved_r3,3);t(True);branch(0x21BCA,True,0x21BD0)
        emit(0x21BD0,0x21BD4);positive=signed(numerator)>0;t(positive);branch(0x21BD2,positive,0x21BD8)
        if not positive:emit(0x21BD4,0x21BD8)
        emit(0x21BD8,0x21BE6);branch(0x21BDC,False,0x21C7C);branch(0x21BE4,long_path,0x21C08)
        if long_path:
            emit(0x21C08,0x21C64);push(0x21C08,saved_r4,4);branch(0x21C62,not negative,0x21C68)
            if negative:emit(0x21C64,0x21C68)
            emit(0x21C68,0x21C70);pop(0x21C68,4);pop(0x21C6A,3);pop(0x21C6E,2);terminal=0x21C6C
        else:
            emit(0x21BE6,0x21BFE);branch(0x21BFC,not negative,0x21C02)
            if negative:emit(0x21BFE,0x21C02)
            emit(0x21C02,0x21C08);pop(0x21C02,3);pop(0x21C06,2);terminal=0x21C04
        r[0]=division.quotient('signed',10000,numerator);r[1]=None
        r[2],r[3],r[4]=saved_r2,saved_r3,saved_r4
        sr&=~0x301;sr_mask&=~0x100;t(negative)
        row.update(divisor=10000,dividend=numerator,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    emit(0xB7768,0xB7782);push(0xB7768,r[14],14);push(0xB776A,pr);push(0xB776C,macl);stack-=12
    frame_access(0xB7770,'write',stack,4,5,r[5]);r[14]=r[4]
    r[4]=0x14B0A;r[0]=r[6];r[5]=0x13FF4;r[6]=r[14]&65535;r[2]=0x26524
    frame_access(0xB7780,'write',stack+7,1,0,r[0]);row=call(0xB777E,0x26524);lookup=curve(row)
    emit(0xB7782,0xB778C);frame_access(0xB7782,'write',stack+8,2,0,r[0]);r[5]=0x21BBC;r[0]=10000
    r[1]=frame_access(0xB778A,'read',stack,4,1);row=call(0xB7788,0x21BBC);signed_divider(row)
    emit(0xB778C,0xB77A0);r[5]=r[0]
    bias=frame_access(0xB778E,'read',stack+7,1,0);r[0]=signed(bias,8)&MASK;r[6]=100;r[2]=bias
    macl=bias*100;r[2]=macl;r[5]=(r[5]-r[2])&MASK;candidate=signed(r[5]);r[2]=27767
    above=candidate>27767;t(above);branch(0xB779E,not above,0xB77A6)
    if above:
        emit(0xB77A0,0xB77A6);r[2]=32767;control(0xB77A2,'jump',0xB77B8,True)
    else:
        emit(0xB77A6,0xB77AC);r[2]=0xFFFF6C78;within=candidate>=-37768;t(within);branch(0xB77AA,within,0xB77B2)
        if within:
            emit(0xB77B2,0xB77B8);r[6]=5000;r[5]=(r[5]+5000)&MASK;r[2]=r[5]
        else:
            emit(0xB77AC,0xB77B2);r[2]=0xFFFF8000;control(0xB77AE,'jump',0xB77B8,True)
    emit(0xB77B8,0xB77BE);r[5]=signed(r[2]&65535,16)&MASK;nonnegative=signed(r[5])>=0;t(nonnegative)
    branch(0xB77BC,nonnegative,0xB77C0)
    if not nonnegative:emit(0xB77BE);r[5]=0
    emit(0xB77C0,0xB77E0);r[4]=0x8543;r[5]&=65535
    r[0]=signed(frame_access(0xB77C4,'read',stack+8,2,0),16)&MASK
    gain=read(0xB77C6,0x8543,2,1);r[2]=signed(gain,8)&MASK;r[6]=r[0]&65535;r[0]=0x410;r[4]=gain
    macl=r[4]*r[6];r[2]=(macl>>8)&65535;macl=(r[2]*r[5])&MASK
    r[2]=RAM_BASE+0x28F8;r[6]=macl>>8;output=r[6]
    ram[0x2D08:0x2D0C]=output.to_bytes(4,'big')
    event(0xB77DE,'write',RAM_BASE+0x2D08,4,6,'ram',bytes(ram[0x2D08:0x2D0C]))
    emit(0xB77E0,0xB77EA);stack+=12;macl=pop(0xB77E2);pr=pop(0xB77E4);r[14]=pop(0xB77E8,14)
    control(0xB77E6,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:v&MASK for i,v in enumerate(r) if v is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=context[15],mach=context[16],macl=macl,output=output,
        signed_quotient=division.quotient('signed',10000,context[5]),byte_bias=bias,candidate=candidate,
        curve_value=lookup['value'],gain=gain,nonnegative=nonnegative)
