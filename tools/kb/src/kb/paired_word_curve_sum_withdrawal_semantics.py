"""Separate paired32-knot word curves,ordered local carrier and complete saturated arithmetic."""


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
    if (type(entry) is not int or entry!=0x72C3C
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the paired word curve sum equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

    def emit(first,last=None):
        path.extend(range(first,first+2 if last is None else last,2))

    def event(site,mode,address,width,register,domain,raw):
        index=len(path)-1-path[::-1].index(site)
        if index in events:raise ValueError('the paired word curve sum equation assigns two operands to one instruction')
        events[index]=dict(site=site,mode=mode,address=address,width_bytes=width,register=register,
            domain=domain,bytes=raw.hex())

    def read(site,address,register,width=2):
        spans=[(at,data) for at,data in calibration.items() if at<=address and address+width<=at+len(data)]
        if len(spans)!=1:raise ValueError('the paired word curve sum equation loses one authoritative physical preimage')
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

    def load(site,at,width,register):
        raw=bytes(ram[at:at+width]);event(site,'read',RAM_BASE+at,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,at,width,register,value):
        ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+at,width,register,'ram',bytes(ram[at:at+width]))

    emit(0x72C3C,0x72C54);push(0x72C3C,r[12],12);push(0x72C3E,r[13],13);push(0x72C40,r[14],14)
    push(0x72C42,pr);push(0x72C44,gbr);r[0]=gbr=RAM_BASE+0x128C;stack-=4
    r[6]=RAM_BASE+0x24CE;r[0]=load(0x72C4E,0x24D2,1,0)
    alternate=bool(r[0]&1);t(not alternate);branch(0x72C52,alternate,0x72CA6)
    if not alternate:
        emit(0x72C54,0x72C5A);r[0]=load(0x72C54,0x24CE,1,0)
        alternate=bool(r[0]&4);t(not alternate);branch(0x72C58,alternate,0x72CA6)
    if not alternate:
        emit(0x72C5A,0x72C7A);r[7]=RAM_BASE+0x128C;r[0]=0x5B2;r[4]=RAM_BASE+0x120E
        r[5]=load(0x72C60,0x183E,2,5);r[0]=load(0x72C62,0x1340,2,0);r[5]&=65535;r[2]=r[0]&65535
        r[6]=(r[5]+r[2])&MASK;r[2]=load(0x72C6C,0x120E,2,2);r[4]=(r[2]&65535)>>2
        r[6]=(r[6]-r[4])&MASK;nonnegative=signed(r[6])>=0;t(nonnegative)
        branch(0x72C76,nonnegative,0x72C7C,True);r[2]=r[6]
        if not nonnegative:emit(0x72C7A);r[2]=0
        emit(0x72C7C,0x72C84);r[6]=65535;above=signed(r[2])>65535;t(above);branch(0x72C82,not above,0x72C86)
        if above:emit(0x72C84);r[2]=r[6]
        emit(0x72C86,0x72CA2);r[7]=RAM_BASE+0x128C;r[0]=0x726;r[6]=RAM_BASE+0x28F8
        first_output=r[2]&65535;put(0x72C8C,0x19B2,2,2,r[2]);r[0]=0x49;r[0]<<=2
        r[2]=load(0x72C92,0x2A1C,2,2);r[6]=r[2]&65535;r[2]=r[5];r[5]=65535;r[2]=(r[2]+r[6])&MASK
        above=r[2]>r[5];t(above);branch(0x72CA0,not above,0x72CE2)
        if above:
            emit(0x72CA2,0x72CA6);control(0x72CA2,'jump',0x72CE2,True);r[2]=r[5]
    else:
        emit(0x72CA6,0x72CBA);r[14]=RAM_BASE+0x2898;r[0]=0x24;r[12]=0x13202
        r[6]=load(0x72CAC,0x28BC,2,6);r[13]=0x155A0;r[4]=r[12];r[2]=0x26524;r[6]&=65535;r[5]=r[13]
        first=curve(call(0x72CB6,0x26524))
        emit(0x72CBA,0x72CCA);frame_access(0x72CBA,'write',stack,2,0,r[0]);r[0]=0x26
        r[6]=load(0x72CBE,0x28BE,2,6);r[4]=r[12];r[2]=0x26524;r[5]=r[13];r[6]&=65535
        second=curve(call(0x72CC6,0x26524))
        emit(0x72CCA,0x72CDA);r[7]=signed(frame_access(0x72CCA,'read',stack,2,7),16)&MASK
        r[2]=r[0]&65535;r[5]=MASK;r[7]&=65535;r[7]=(r[7]+r[2])&MASK;r[2]=65535
        above=r[7]>r[2];t(above);branch(0x72CD8,above,0x72CDC)
        if not above:emit(0x72CDA);r[2]=r[7]
        emit(0x72CDC,0x72CE2);r[7]=RAM_BASE+0x128C;r[0]=0x726
        first_output=r[2];put(0x72CE0,0x19B2,2,2,r[2])
        lookups.append(dict(kind='paired-word-curve-saturated-sum',first=first['value'],second=second['value'],value=r[2]))
    emit(0x72CE2,0x72CF4);r[0]=0x72A;second_output=r[2]&65535;put(0x72CE4,0x19B6,2,2,r[2])
    stack+=4;gbr=pop(0x72CE8);pr=pop(0x72CEA);r[14]=pop(0x72CEC,14);r[13]=pop(0x72CEE,13)
    control(0x72CF0,'return',pr,True);r[12]=pop(0x72CF2,12)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r)},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0],
        alternate=alternate,first_output=first_output,second_output=second_output)
