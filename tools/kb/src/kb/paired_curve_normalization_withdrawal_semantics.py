"""Separate paired curve-normalization caller arithmetic and complete real helper/frame paths."""

from kb import division_callees_semantics as division

MASK=0xFFFFFFFF
RAM_BASE=0x01000000


def signed(value,bits=32):return value-(1<<bits) if value&(1<<(bits-1)) else value


def position(knots,coordinate):
    """Select the rightmost qualifying byte knot without a monotonicity premise."""
    if (type(coordinate) is not int or not 0<=coordinate<=255 or len(knots)!=16
            or any(type(knot) is not int or not 0<=knot<=255 for knot in knots)):
        raise ValueError('the backward byte-axis equation changes an unsigned coordinate or physical byte')
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
    if (type(entry) is not int or entry not in (0x655B4,0x65B08)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the paired curve normalization caller equations need complete exact CPU/RAM/frame inputs')
    r=list(context[:15]);ram=bytearray(memory);frame=bytearray(frame_before)
    path=[];events={};controls=[];calls=[];lookups=[];stack=sp;pr=continuation
    sr=sr_before;sr_mask=MASK;macl=context[17];gbr=context[15]

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

    def axis(target,width,row):
        nonlocal pr
        base,coordinate=r[0],r[5];maximum=15*width;r[3]=r[4]
        if width!=1 or r[4]!=maximum:raise ValueError('the word-axis wrapper changes its actual complete axis extent')
        source=next(data for at,data in calibration.items() if at==base)
        pos=position(tuple(int.from_bytes(source[i:i+width],'big') for i in range(0,len(source),width)),coordinate);lookups.append(dict(kind='axis',target=target,base=base,**pos))
        emit(target)
        for index in pos['scanned']:
            emit(target+2,target+10);r[1]=read(target+2,base+width*index,1,width)
            equal=coordinate==r[1];t(equal);branch(target+8,equal,target+0x38)
            r[4]=width*index
            if equal:break
            emit(target+10,target+14);higher=coordinate>r[1];t(higher);branch(target+12,not higher,target+0x30)
            if higher:
                emit(target+14,target+18);last=index==15;t(last);branch(target+16,last,target+0x38)
                if last:break
                emit(target+18,target+42)
                r[5]=pos['numerator'];r[1]=read(target+24,base+width*index,1,width)
                next_word=read(target+26,base+width*index+width,0,width)
                r[0]=next_word-r[1];r[2]=0x26C78
                push(target+32,pr);r[1]=r[5]
                nested=call(target+38,r[2]);fraction(r[2],nested)
                emit(target+42,target+48);pr=pop(target+42)
                r[5]=r[0];control(target+44,'return',pr,True);returned(row,target+44)
                return pos
            emit(target+48,target+54);r[4]-=width;t(r[4]>=0);branch(target+52,r[4]>=0,target+2)
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

    def load(site,at,width,register):
        raw=bytes(ram[at:at+width]);event(site,'read',RAM_BASE+at,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,at,width,register,value):
        ram[at:at+width]=(value&((1<<(width*8))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+at,width,register,'ram',bytes(ram[at:at+width]))

    def divide(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if not 1<=divisor<=256:raise ValueError('the paired normalization callers lose their actual positive1..256 signed divisor premise')
        saved_r2,saved_r3,saved_r4=r[2:5]
        emit(0x21BBC,0x21BC2);push(0x21BBC,saved_r2,2);t(divisor==0);branch(0x21BC0,divisor==0,0x21C70)
        if divisor==0:
            emit(0x21C70,0x21C7C);r[1]=RAM_BASE+0x9818;r[2]=0x44E;put(0x21C74,0x9818,4,2,r[2])
            r[0]=0;r[2]=pop(0x21C7A,2);terminal=0x21C78
            row.update(divisor=divisor,dividend=numerator,zero=True,large_divisor=False,long_path=False)
        else:
            negative=bool(numerator&0x80000000);large=divisor>65535;long_path=not large and abs(signed(numerator))>=divisor*256
            emit(0x21BC2,0x21BCC);push(0x21BC2,saved_r3,3);t(True);branch(0x21BCA,True,0x21BD0)
            emit(0x21BD0,0x21BD4);positive=signed(numerator)>0;t(positive);branch(0x21BD2,positive,0x21BD8)
            if not positive:emit(0x21BD4,0x21BD8)
            emit(0x21BD8,0x21BDE);branch(0x21BDC,large,0x21C7C)
            if large:
                emit(0x21C7C,0x21CCC);branch(0x21CCA,not negative,0x21CD0)
                if negative:emit(0x21CCC,0x21CD0)
                emit(0x21CD0,0x21CD6);pop(0x21CD0,3);pop(0x21CD4,2);terminal=0x21CD2
            else:
                emit(0x21BDE,0x21BE6);branch(0x21BE4,long_path,0x21C08)
                if long_path:
                    emit(0x21C08,0x21C64);push(0x21C08,saved_r4,4);branch(0x21C62,not negative,0x21C68)
                    if negative:emit(0x21C64,0x21C68)
                    emit(0x21C68,0x21C70);pop(0x21C68,4);pop(0x21C6A,3);pop(0x21C6E,2);terminal=0x21C6C
                else:
                    emit(0x21BE6,0x21BFE);branch(0x21BFC,not negative,0x21C02)
                    if negative:emit(0x21BFE,0x21C02)
                    emit(0x21C02,0x21C08);pop(0x21C02,3);pop(0x21C06,2);terminal=0x21C04
            r[0]=division.quotient('signed',divisor,numerator);r[1]=None
            r[2],r[3],r[4]=saved_r2,saved_r3,saved_r4
            sr&=~0x301;sr_mask&=~0x100;t(negative)
            row.update(divisor=divisor,dividend=numerator,zero=False,large_divisor=large,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    def byte_curve(row):
        nonlocal pr
        base,axis_base,coordinate=r[4:7]
        if (base,axis_base)!=(0x11D24,0x1199E) or not 0<=coordinate<=255:
            raise ValueError('the paired byte curve changes an exact data/axis root or normalized byte coordinate')
        emit(0x264a0,0x264ae);push(0x264a0,pr);push(0x264a2,r[4],4)
        r[0]=r[5];r[5]=coordinate&255;r[7]=0x26944;r[4]=15
        nested=call(0x264aa,0x26944);pos=axis(0x26944,1,nested)
        emit(0x264ae,0x264c2);r[6]=pop(0x264ae,6)+r[4]
        r[0]=signed(read(0x264b2,r[6]+1,0,1),8)&MASK;r[2]=r[0]&255;r[3]=r[5]
        r[1]=signed(read(0x264b8,r[6],1,1),8)&MASK;pr=pop(0x264ba);r[6]=0x26740;r[0]=r[1]&255
        control(0x264be,'jump',0x26740,True);value=interpolation(0x26740,row)
        lookups.append(dict(pos,kind='byte-curve',base=base,axis=axis_base,coordinate=coordinate&255,**value))
        return value

    def curve_call(site):
        row=call(site,0x264A0);return byte_curve(row)

    def signed_shift8():
        r[6]=r[2]>>8;r[2]=((r[6]&65535)<<16)|(r[6]>>16)
        r[6]=signed(r[2]&255,8)&MASK;r[2]=((r[2]>>16)|(r[6]<<16))&MASK

    def first_caller():
        nonlocal stack,gbr,macl
        emit(0x655B4,0x655CC);push(0x655B4,r[12],12);push(0x655B6,r[14],14)
        push(0x655B8,pr);push(0x655BA,macl);push(0x655BC,gbr);r[0]=gbr=RAM_BASE+0x128C;stack-=8
        r[6]=0x8710;r[0]=signed(read(0x655C6,0x8710,0,1),8)&MASK
        alternate=bool(r[0]&32);t(not alternate);branch(0x655CA,alternate,0x65660)
        if not alternate:
            emit(0x655CC,0x655EE);r[0]=load(0x655CC,0x12DF,1,0);r[7]=RAM_BASE+0x23BC;r[6]=r[0]&255
            r[12]=RAM_BASE+0x128C;r[0]=53;r[2]=load(0x655D6,0x23F1,1,2)
            r[0]=72;r[5]=load(0x655DA,0x2404,1,5);r[0]=0x35E;r[2]=(r[2]-r[5]-r[6])&MASK
            r[6]=load(0x655E2,0x15EA,1,6)&255;r[2]=(r[2]-r[6])&MASK
            nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x655EA,nonnegative,0x655F0,True);r[6]=r[2]
            if not nonnegative:emit(0x655EE);r[6]=0
            emit(0x655F0,0x655FA);r[14]=255;r[6]=signed(r[6]&65535,16)&MASK
            above=signed(r[6])>r[14];t(above);branch(0x655F8,not above,0x655FC)
            if above:raise ValueError('the full raw signed-byte difference exceeds its proved255 upper bound')
            emit(0x655FC,0x65608);r[4]=0x11D24;r[5]=0x1199E;r[2]=0x264A0
            frame_access(0x65602,'write',stack,1,6,r[6]);r[6]&=255;curve_call(0x65604)
            emit(0x65608,0x6562A);frame_access(0x65608,'write',stack+4,1,0,r[0])
            r[0]=load(0x6560A,0x12DF,1,0);r[7]=RAM_BASE+0x119C;r[5]=r[0]&255;r[0]=0x35E
            r[6]=signed(frame_access(0x65612,'read',stack,1,6),8)&MASK;r[2]=load(0x65614,0x15EA,1,2)
            r[0]=38;r[4]=load(0x65618,0x11C2,1,4);r[6]&=255;r[2]&=255
            r[6]=(r[6]+r[4]+r[5]+r[2])&MASK;nonnegative=signed(r[6])>=0;t(nonnegative)
            branch(0x65626,nonnegative,0x6562C,True);r[2]=r[6]
            if not nonnegative:emit(0x6562A);r[2]=0
            emit(0x6562C,0x65632);r[6]=signed(r[2]&65535,16)&MASK;above=signed(r[6])>r[14]
            t(above);branch(0x65630,not above,0x65634)
            if above:emit(0x65632);r[6]=r[14]
            emit(0x65634,0x6563E);r[4]=0x11D24;r[5]=0x1199E;r[2]=0x264A0;r[6]&=255;curve_call(0x6563A)
            emit(0x6563E,0x6565C);r[5]=r[0]&255;r[0]=signed(frame_access(0x65640,'read',stack+4,1,0),8)&MASK
            r[6]=256;r[7]=r[0]&255;r[0]=0x640;r[2]=r[6]-r[5];r[5]=load(0x6564E,0x18CC,2,5)
            r[6]-=r[7];r[0]=r[6];macl=(r[5]*r[2])&MASK;r[5]=0x21BBC;r[1]=macl
            row=call(0x65658,0x21BBC);divide(row)
            emit(0x6565C,0x65660);control(0x6565C,'jump',0x656DE,True);r[2]=r[0]
            return
        emit(0x65660,0x6566C);r[7]=RAM_BASE+0x119C;r[0]=load(0x65662,0x11A0,2,0);r[4]=r[0]
        r[0]=load(0x65666,0x119E,2,0);equal=r[0]==r[4];t(equal);branch(0x6566A,not equal,0x65674)
        if equal:
            emit(0x6566C,0x65674);r[12]=RAM_BASE+0x128C;r[0]=0x642;r[2]=load(0x65672,0x18CE,2,2)
            control(0x65670,'jump',0x656DE,True);return
        emit(0x65674,0x6568C);r[7]=RAM_BASE+0x23BC;r[0]=38;r[2]=RAM_BASE+0x4124
        r[6]=load(0x6567A,0x23E2,1,6);r[0]=27;r[5]=load(0x6567E,0x413F,1,5)
        r[4]=(r[4]+r[6])&MASK;r[5]&=255;r[6]=signed(r[5]&65535,16)&MASK;r[2]=(-r[6])&MASK
        above=signed(r[4])>signed(r[2]);t(above);branch(0x6568A,not above,0x65692)
        if above:
            emit(0x6568C,0x65692);r[5]=signed(r[5]&65535,16)&MASK;r[6]=(-r[5])&MASK
            control(0x6568E,'jump',0x65694,True)
        else:emit(0x65692);r[6]=r[4]
        emit(0x65694,0x656A6);r[0]=72;r[2]=load(0x65696,0x2404,1,2);r[0]=53;r[6]=(r[6]+r[2])&MASK
        r[2]=load(0x6569C,0x23F1,1,2);r[2]=(r[2]-r[6])&MASK;nonnegative=signed(r[2])>=0;t(nonnegative)
        branch(0x656A2,nonnegative,0x656A8,True);r[6]=r[2]
        if not nonnegative:emit(0x656A6);r[6]=0
        emit(0x656A8,0x656B0);r[14]=255;above=signed(r[6])>r[14];t(above);branch(0x656AE,not above,0x656B2)
        if above:emit(0x656B0);r[6]=r[14]
        emit(0x656B2,0x656BE);r[4]=0x11D24;r[5]=0x1199E;r[2]=0x264A0;r[12]=RAM_BASE+0x128C;r[6]&=255
        curve_call(0x656BA)
        emit(0x656BE,0x656D2);r[6]=r[0]&255;r[0]=0x640;r[2]=256-r[6];r[6]=load(0x656C8,0x18CC,2,6)
        macl=(r[6]*r[2])&MASK;r[2]=macl;nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x656D0,nonnegative,0x656D4)
        if not nonnegative:emit(0x656D2);r[2]=(r[2]+r[14])&MASK
        emit(0x656D4,0x656DE);signed_shift8()

    def second_caller():
        nonlocal stack,gbr,macl
        emit(0x65B08,0x65B20);push(0x65B08,r[12],12);push(0x65B0A,r[14],14)
        push(0x65B0C,pr);push(0x65B0E,macl);push(0x65B10,gbr);r[0]=gbr=RAM_BASE+0x128C;stack-=8
        r[6]=0x8710;r[0]=signed(read(0x65B1A,0x8710,0,1),8)&MASK
        alternate=bool(r[0]&32);t(not alternate);branch(0x65B1E,alternate,0x65BB6)
        if not alternate:
            emit(0x65B20,0x65B44);r[0]=load(0x65B20,0x12DF,1,0);r[2]=RAM_BASE+0x23BC;r[6]=r[0]&255
            r[12]=RAM_BASE+0x128C;r[0]=53;r[4]=load(0x65B2A,0x23F1,1,4)
            r[0]=72;r[5]=load(0x65B2E,0x2404,1,5);r[0]=0x35E;r[2]=(r[4]-r[5]-r[6])&MASK
            r[6]=load(0x65B38,0x15EA,1,6)&255;r[2]=(r[2]-r[6])&MASK
            nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x65B40,nonnegative,0x65B46,True);r[6]=r[2]
            if not nonnegative:emit(0x65B44);r[6]=0
            emit(0x65B46,0x65B50);r[14]=255;r[2]=r[6]&65535;above=signed(r[2])>r[14]
            t(above);branch(0x65B4E,not above,0x65B52)
            if above:raise ValueError('the full raw signed-byte difference exceeds its proved255 upper bound')
            emit(0x65B52,0x65B60);frame_access(0x65B52,'write',stack,1,2,r[2])
            r[4]=0x11D24;r[6]=r[2]&255;r[5]=0x1199E;r[2]=0x264A0;curve_call(0x65B5C)
            emit(0x65B60,0x65B80);frame_access(0x65B60,'write',stack+4,1,0,r[0])
            r[0]=load(0x65B62,0x12DF,1,0);r[7]=RAM_BASE+0x119C;r[2]=r[0]&255;r[0]=0x35E
            r[6]=signed(frame_access(0x65B6A,'read',stack,1,6),8)&MASK;r[5]=load(0x65B6C,0x15EA,1,5)
            r[0]=37;r[4]=load(0x65B70,0x11C1,1,4);r[6]&=255;r[5]&=255;r[6]=(r[6]+r[4]+r[2]+r[5])&MASK
            nonnegative=signed(r[6])>=0;t(nonnegative);branch(0x65B7E,nonnegative,0x65B82)
            if not nonnegative:emit(0x65B80);r[6]=0
            emit(0x65B82,0x65B88);r[6]&=65535;above=signed(r[6])>r[14];t(above);branch(0x65B86,not above,0x65B8A)
            if above:emit(0x65B88);r[6]=r[14]
            emit(0x65B8A,0x65B94);r[4]=0x11D24;r[5]=0x1199E;r[2]=0x264A0;r[6]&=255;curve_call(0x65B90)
            emit(0x65B94,0x65BB2);r[5]=r[0]&255;r[0]=signed(frame_access(0x65B96,'read',stack+4,1,0),8)&MASK
            r[6]=256;r[7]=r[0]&255;r[0]=0x640;r[2]=r[6]-r[5];r[5]=load(0x65BA4,0x18CC,2,5)
            r[6]-=r[7];r[0]=r[6];macl=(r[5]*r[2])&MASK;r[5]=0x21BBC;r[1]=macl
            row=call(0x65BAE,0x21BBC);divide(row)
            emit(0x65BB2,0x65BB6);control(0x65BB2,'jump',0x65C02,True);r[2]=r[0]
            return
        emit(0x65BB6,0x65BC8);r[7]=RAM_BASE+0x119C;r[2]=RAM_BASE+0x23BC;r[0]=load(0x65BBA,0x11A2,1,0)
        r[5]=r[0];r[0]=53;r[2]=load(0x65BC0,0x23F1,1,2);r[2]=(r[2]-r[5])&MASK
        nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x65BC6,nonnegative,0x65BCA)
        if not nonnegative:emit(0x65BC8);r[2]=0
        emit(0x65BCA,0x65BD4);r[14]=255;r[6]=r[2]&255;above=r[6]>r[14];t(above);branch(0x65BD2,not above,0x65BD6)
        if above:raise ValueError('the EXTU.B caller operand exceeds its exact255 bound')
        emit(0x65BD6,0x65BE2);r[4]=0x11D24;r[5]=0x1199E;r[2]=0x264A0;r[12]=RAM_BASE+0x128C;r[6]&=255
        curve_call(0x65BDE)
        emit(0x65BE2,0x65BF6);r[6]=r[0]&255;r[0]=0x640;r[2]=256-r[6];r[6]=load(0x65BEC,0x18CC,2,6)
        macl=(r[6]*r[2])&MASK;r[2]=macl;nonnegative=signed(r[2])>=0;t(nonnegative);branch(0x65BF4,nonnegative,0x65BF8)
        if not nonnegative:emit(0x65BF6);r[2]=(r[2]+r[14])&MASK
        emit(0x65BF8,0x65C02);signed_shift8()

    if entry==0x655B4:
        first_caller();emit(0x656DE,0x656E4);r[6]=32767;above=signed(r[2])>r[6];t(above);branch(0x656E2,above,0x656E6)
        if not above:emit(0x656E4);r[6]=r[2]
        emit(0x656E6,0x656EE);r[2]=(-32768)&MASK;inside=signed(r[6])>=-32768;t(inside);branch(0x656EC,not inside,0x656F0)
        if inside:emit(0x656EE);r[2]=r[6]
        emit(0x656F0,0x65702);r[0]=0x648;put(0x656F2,0x18D4,2,2,r[2]);stack+=8
        gbr=pop(0x656F6);macl=pop(0x656F8);pr=pop(0x656FA);r[14]=pop(0x656FC,14);r[12]=pop(0x65700,12)
        control(0x656FE,'return',pr,True)
    else:
        second_caller();emit(0x65C02,0x65C08);r[6]=32767;above=signed(r[2])>r[6];t(above);branch(0x65C06,above,0x65C0A)
        if not above:emit(0x65C08);r[6]=r[2]
        emit(0x65C0A,0x65C12);r[2]=(-32768)&MASK;inside=signed(r[6])>=-32768;t(inside);branch(0x65C10,not inside,0x65C14)
        if inside:emit(0x65C12);r[2]=r[6]
        emit(0x65C14,0x65C26);r[0]=0x642;put(0x65C16,0x18CE,2,2,r[2]);stack+=8
        gbr=pop(0x65C1A);macl=pop(0x65C1C);pr=pop(0x65C1E);r[14]=pop(0x65C20,14);r[12]=pop(0x65C24,12)
        control(0x65C22,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={i:value&MASK for i,value in enumerate(r) if value is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=r[0])
