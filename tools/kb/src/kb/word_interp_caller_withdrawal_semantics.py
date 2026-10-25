"""Separate unsigned backward-axis, word interpolation and complete caller composition."""

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
    if (type(entry) is not int or entry not in (0x72F1E,0xB7B98)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the word caller equations need complete exact CPU/RAM/frame inputs')
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
                r[0]=next_word-r[1];r[2]=0x26C78 if count==16 else 0x26D10
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
        emit(0x26714,0x26722);push(0x26714,pr);push(0x26716,r[4],4)
        r[0]=r[5];r[5]=coordinate&65535;r[7]=0x26B84;r[4]=62
        nested=call(0x2671E,0x26B84);pos=axis(0x26B84,32,nested)
        emit(0x26722,0x26736);r[6]=pop(0x26722,6)+r[4]
        r[0]=signed(read(0x26726,r[6]+2,0),16)&MASK;r[2]=r[0]&65535;r[3]=r[5]
        r[1]=signed(read(0x2672C,r[6],1),16)&MASK;pr=pop(0x2672E)
        r[6]=0x26AF8;r[0]=r[1]&65535;control(0x26732,'jump',0x26AF8,True)
        value=interpolation(0x26AF8,row)
        lookups.append(dict(pos,kind='curve',base=base,axis=axis_base,coordinate=coordinate,**value))
        return value

    def surface_finish(row):
        nonlocal pr
        emit(0x26848,0x26864);push(0x26848,r[8],8);push(0x2684A,pr)
        r[7]=macl;r[0]=(r[0]&65535)*(r[5]&65535);r[4]+=r[2]+r[0]
        r[5]=r[4]+32;r[8]=r[1];r[7]=0x26740;t(r[3]==0);branch(0x26862,r[3]==0,0x2688A)
        values=[]
        if r[3]:
            emit(0x26864,0x2686E);r[1]=signed(read(0x26864,r[4],1),16)&MASK
            r[0]=signed(read(0x26866,r[4]+2,0),16)&MASK;r[2]=r[0]&65535;r[0]=r[1]&65535
            nested=call(0x2686A,0x26740);values.append(interpolation(0x26740,nested))
            emit(0x2686E,0x26872);t(r[8]==0);branch(0x26870,r[8]==0,0x2689A)
            if r[8]:
                emit(0x26872,0x2687E);push(0x26872,r[0],0)
                r[1]=signed(read(0x26874,r[5],1),16)&MASK
                r[0]=signed(read(0x26876,r[5]+2,0),16)&MASK;r[2]=r[0]&65535;r[0]=r[1]&65535
                nested=call(0x2687A,0x26740);values.append(interpolation(0x26740,nested))
                emit(0x2687E,0x26886);r[2]=r[0];r[0]=pop(0x26880,0);r[3]=r[8]
                nested=call(0x26882,0x26740);values.append(interpolation(0x26740,nested))
                emit(0x26886,0x2688A);control(0x26886,'jump',0x2689A,True)
        else:
            emit(0x2688A,0x26890);t(r[8]==0);branch(0x2688C,r[8]==0,0x2689A,True)
            r[0]=signed(read(0x2688E,r[4],0),16)&MASK
            if r[8]:
                emit(0x26890,0x2689A);r[2]=read(0x26890,r[5],2);r[0]&=65535;r[3]=r[8]
                nested=call(0x26896,0x26740);values.append(interpolation(0x26740,nested))
        emit(0x2689A,0x268A0);pr=pop(0x2689A);r[8]=pop(0x2689E,8)
        control(0x2689C,'return',pr,True);returned(row,0x2689C)
        lookups.append(dict(kind='surface',raw_result=r[0],value=r[0]&65535,interpolations=values))

    def surface(row):
        nonlocal pr
        emit(0x262A8,0x262B8);push(0x262A8,pr);push(0x262AA,r[4],4)
        r[7]&=65535;r[0]=r[5];r[5]=r[7];r[7]=0x26984;r[4]=30
        nested=call(0x262B4,0x26984);axis(0x26984,16,nested)
        emit(0x262B8,0x262C6);push(0x262B8,r[5],5);push(0x262BA,r[4],4);r[0]=r[6]
        r[5]=frame_access(0x262BE,'read',stack+16,4,5)&65535;r[4]=30
        nested=call(0x262C2,0x26984);axis(0x26984,16,nested)
        emit(0x262C6,0x262D8);r[0]=pop(0x262C6,0);r[1]=pop(0x262C8,1)
        r[2]=r[4];r[3]=r[5];r[4]=pop(0x262CE,4);pr=pop(0x262D0);r[7]=0x26848;r[5]=16
        control(0x262D4,'jump',0x26848,True);surface_finish(row)

    if entry==0x72F1E:
        emit(0x72F1E,0x72F32);push(0x72F1E,pr);r[5]=0x18E86;r[7]=RAM_BASE+0x128C
        threshold=read(0x72F26,0x18EC4,2);source=int.from_bytes(memory[0x1D08:0x1D0C],'big')
        event(0x72F2C,'read',RAM_BASE+0x1D08,4,6,'ram',memory[0x1D08:0x1D0C])
        r[0]=0xA7C;r[2]=threshold;r[6]=source;high=source>threshold;t(high);branch(0x72F30,high,0x72F4E)
        if high:
            emit(0x72F4E,0x72F5A);r[6]=source>>4;r[4]=65535;clamp=r[6]>65535;t(clamp)
            branch(0x72F58,not clamp,0x72F5C)
            if clamp:emit(0x72F5A);r[6]=65535
            emit(0x72F5C,0x72F66);r[4]=0x18F96;r[5]=0x18E46;r[2]=0x26714
            row=call(0x72F62,0x26714);curve(row)
            emit(0x72F66,0x72F6E);r[6]=r[0];r[7]=RAM_BASE+0x128C;r[0]=0xA86;output=r[6]
            site=0x72F6C;register=6
        else:
            emit(0x72F32,0x72F3A);r[4]=65535;t(False);branch(0x72F38,True,0x72F3C)
            emit(0x72F3C,0x72F44);r[4]=0x18FD6;r[2]=0x26714;r[6]&=65535
            row=call(0x72F40,0x26714);curve(row)
            emit(0x72F44,0x72F4E);r[2]=r[0];r[7]=RAM_BASE+0x128C;r[0]=0xA86;output=r[2]
            control(0x72F4A,'jump',0x72F6E,True);site=0x72F4C;register=2
        ram[0x1D12:0x1D14]=(output&65535).to_bytes(2,'big')
        event(site,'write',RAM_BASE+0x1D12,2,register,'ram',bytes(ram[0x1D12:0x1D14]))
        emit(0x72F6E,0x72F74);pr=pop(0x72F6E);control(0x72F70,'return',pr,True)
    else:
        emit(0xB7B98,0xB7BBA);push(0xB7B98,r[13],13);push(0xB7B9A,r[14],14)
        push(0xB7B9C,pr);push(0xB7B9E,macl);stack-=4
        r[14]=r[5]&255;r[2]=r[6];r[5]=0x13D74;r[0]=r[4];r[6]=0x13DB4
        r[13]=r[7];r[4]=0xD40E;r[7]=r[2]&65535;r[3]=0x262A8
        frame_access(0xB7BB8,'write',stack+2,2,0,r[0])
        row=call(0xB7BB6,0x262A8);surface(row)
        emit(0xB7BBA,0xB7BC0);t(r[14]==0);branch(0xB7BBC,r[14]==0,0xB7BC4,True);r[2]=r[0]
        if r[14]:
            emit(0xB7BC0,0xB7BC4);r[2]=0;control(0xB7BC0,'jump',0xB7BCC,True)
        else:
            emit(0xB7BC4,0xB7BCC);r[13]&=255;r[2]&=65535;macl=r[2]*r[13];r[2]=macl
        emit(0xB7BCC,0xB7BD2);r[5]=RAM_BASE+0x28F8;r[0]=0x40C;output=r[2]
        ram[0x2D04:0x2D08]=output.to_bytes(4,'big')
        event(0xB7BD0,'write',RAM_BASE+0x2D04,4,2,'ram',bytes(ram[0x2D04:0x2D08]))
        emit(0xB7BD2,0xB7BDE);stack+=4;macl=pop(0xB7BD4);pr=pop(0xB7BD6)
        r[14]=pop(0xB7BD8,14);r[13]=pop(0xB7BDC,13);control(0xB7BDA,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),registers=tuple(v&MASK for v in r),
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=context[15],mach=context[16],macl=macl,output=output)
