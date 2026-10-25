"""Separate timing history, eight-knot word curve, transformed-pulse quotient and remainder paths."""

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
    if (type(coordinate) is not int or not 0<=coordinate<=65535 or len(knots) not in (8,16)
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
    if (type(entry) is not int or entry not in (0x4D99C,0x521A8)
            or type(memory) is not bytes or len(memory)!=65536
            or type(frame_before) is not bytes or len(frame_before)!=192
            or type(context) is not tuple or len(context)!=20
            or any(type(v) is not int or not 0<=v<=MASK for v in context)):
        raise ValueError('the timing remainder caller equations need complete exact CPU/RAM/frame inputs')
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

    def curve(target,count,row):
        nonlocal pr
        base,axis_base,coordinate=r[4:7]
        emit(target,target+14);push(target,pr);push(target+2,r[4],4)
        r[0]=r[5];r[5]=coordinate&65535;r[7]=0x26984;r[4]=2*(count-1)
        nested=call(target+10,0x26984);pos=axis(0x26984,count,nested)
        emit(target+14,target+34);r[6]=pop(target+14,6)+r[4]
        r[0]=signed(read(target+18,r[6]+2,0),16)&MASK;r[2]=r[0]&65535;r[3]=r[5]
        r[1]=signed(read(target+24,r[6],1),16)&MASK;pr=pop(target+26)
        r[6]=0x26740;r[0]=r[1]&65535;control(target+30,'jump',0x26740,True)
        value=interpolation(0x26740,row)
        lookups.append(dict(pos,kind='curve',base=base,axis=axis_base,coordinate=coordinate,**value))
        return value

    def signed_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2];negative=bool(numerator&0x80000000)
        if divisor!=120 or not 0<=numerator<=131070:raise ValueError('the timing remainder signed helper loses its actual positive word divisor')
        long_path=abs(signed(numerator))>=divisor*256
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
        r[0]=division.quotient('signed',divisor,numerator);r[1]=None
        r[2],r[3],r[4]=saved_r2,saved_r3,saved_r4
        sr&=~0x301;sr_mask&=~0x100;t(negative)
        row.update(divisor=divisor,dividend=numerator,long_path=long_path)
        control(terminal,'return',pr,True);returned(row,terminal)

    def unsigned_divider(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if divisor!=100:raise ValueError('the timing remainder unsigned helper changes an actual fixed divisor')
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

    def load(site,address,width,register):
        raw=bytes(ram[address:address+width]);event(site,'read',RAM_BASE+address,width,register,'ram',raw)
        value=int.from_bytes(raw,'big');return signed(value,width*8)&MASK if width<4 else value

    def put(site,address,width,register,value):
        ram[address:address+width]=(value&((1<<(8*width))-1)).to_bytes(width,'big')
        event(site,'write',RAM_BASE+address,width,register,'ram',bytes(ram[address:address+width]))

    def remainder(row):
        nonlocal sr,sr_mask
        divisor,numerator=r[:2]
        if divisor!=120 or not 0<=numerator<=131070:
            raise ValueError('the transformed-pulse remainder changes its real positive divisor or bounded raw numerator')
        quotient=numerator//divisor;long_path=numerator>=divisor*256
        saved_r2,saved_r3,saved_r4=r[2:5]
        emit(0x21E14,0x21E26);push(0x21E14,saved_r2,2);push(0x21E1A,saved_r3,3)
        branch(0x21E18,False,0x21ED0);branch(0x21E24,True,0x21E2A)
        emit(0x21E2A,0x21E2E);positive=numerator>0;t(positive);branch(0x21E2C,positive,0x21E32)
        if not positive:emit(0x21E2E,0x21E32)
        emit(0x21E32,0x21E40);branch(0x21E36,False,0x21EDC);branch(0x21E3E,long_path,0x21E68)
        # The final nonrestoring quotient bit is quotient parity. T selects
        # the restoring addition; the complete actual DIV1 CPU state remains
        # an independent instruction obligation rather than a quotient stub.
        restored_without_add=bool(quotient&1)
        if long_path:
            emit(0x21E68,0x21EBA);push(0x21E68,saved_r4,4)
            t(restored_without_add);branch(0x21EB8,restored_without_add,0x21EBC)
            if not restored_without_add:emit(0x21EBA)
            emit(0x21EBC,0x21EC4);t(False);branch(0x21EC2,True,0x21EC8)
            emit(0x21EC8,0x21ED0);pop(0x21EC8,4);pop(0x21ECA,3);pop(0x21ECE,2);terminal=0x21ECC
        else:
            emit(0x21E40,0x21E54);t(restored_without_add);branch(0x21E52,restored_without_add,0x21E56)
            if not restored_without_add:emit(0x21E54)
            emit(0x21E56,0x21E5E);t(False);branch(0x21E5C,True,0x21E62)
            emit(0x21E62,0x21E68);pop(0x21E62,3);pop(0x21E66,2);terminal=0x21E64
        r[0]=numerator%divisor;r[1]=None;r[2],r[3],r[4]=saved_r2,saved_r3,saved_r4
        sr&=~0x301;sr_mask&=~0x100;t(False)
        row.update(divisor=divisor,dividend=numerator,quotient=quotient,long_path=long_path,
            restoration_without_add=restored_without_add)
        control(terminal,'return',pr,True);returned(row,terminal)

    if entry==0x521A8:
        emit(0x521A8,0x521BE);push(0x521A8,r[14],14);push(0x521AA,pr);push(0x521AC,macl);push(0x521AE,gbr)
        r[0]=gbr=RAM_BASE+0x23BC;stack-=8;r[6]=RAM_BASE+0x4184;r[0]=load(0x521B8,0x4184,1,0)
        alternate=bool(r[0]&64);t(not alternate);branch(0x521BC,not alternate,0x521C6)
        if alternate:
            emit(0x521BE,0x521C6);r[2]=RAM_BASE+0x1094;r[0]=0x36;r[6]=load(0x521C4,0x10CA,2,6)
            control(0x521C2,'jump',0x521CC,True)
        else:
            emit(0x521C6,0x521CC);r[2]=RAM_BASE+0x119C;r[0]=0x20;r[6]=load(0x521CA,0x11BC,2,6)
        emit(0x521CC,0x521E2);r[6]=(r[6]&65535)*16;r[2]=0xC49B;macl=(r[6]*r[2])&MASK
        r[4]=gbr+0x18;r[7]=macl>>16;r[14]=0;r[5]=6
        for index in range(6):
            emit(0x521E2,0x521EA);r[2]=load(0x521E2,0x23D4+2*index,2,2)&65535
            retained=r[14]>=r[2];t(retained);branch(0x521E8,retained,0x521EC)
            if not retained:emit(0x521EA);r[14]=r[2]
            emit(0x521EC,0x521F2);r[5]-=1;t(r[5]==0);r[4]+=2
            branch(0x521EE,r[5]!=0,0x521E2,True)
        emit(0x521F2,0x521FA);r[0]=load(0x521F2,0x241C,2,0);r[6]=r[0]&65535
        retained=r[14]>=r[6];t(retained);branch(0x521F8,retained,0x521FC)
        if not retained:emit(0x521FA);r[14]=r[6]
        emit(0x521FC,0x5220A);macl=(r[7]*r[14])&MASK;r[4]=255;r[2]=macl>>16
        above=r[2]>255;t(above);branch(0x52208,above,0x5220C)
        if not above:emit(0x5220A);r[4]=r[2]
        emit(0x5220C,0x5221E);r[2]=RAM_BASE+0x128C;r[4]&=255;r[0]=0x6A2;r[5]=load(0x52212,0x192E,2,5)&65535
        r[2]=r[4]*2;within=r[5]>=r[2];t(within);branch(0x5221C,within,0x52222)
        if within:emit(0x52222,0x52228);t(bool(r[5]&0x80000000));r[5]*=2;r[4]*=4;r[5]-=r[4]
        else:emit(0x5221E,0x52222);r[5]=0;control(0x5221E,'jump',0x52228,True)
        emit(0x52228,0x52232);r[6]=RAM_BASE+0x24C8;frame_access(0x5222A,'write',stack,4,5,r[5])
        r[0]=load(0x5222C,0x24C9,1,0);offset_active=bool(r[0]&32);t(not offset_active);branch(0x52230,not offset_active,0x52242)
        if offset_active:
            emit(0x52232,0x5223E);r[6]=0x83EA;r[2]=signed(read(0x52234,0x83EA,2,1),8)&MASK;r[2]&=255
            r[5]=(r[5]-r[2])&MASK;positive=signed(r[5])>=0;t(positive);branch(0x5223C,positive,0x52240)
            if not positive:emit(0x5223E);r[5]=0
            emit(0x52240);frame_access(0x52240,'write',stack,4,5,r[5])
        emit(0x52242,0x5224A);r[2]=0x21BBC;r[0]=120;r[1]=r[5]
        row=call(0x52246,0x21BBC);signed_divider(row)
        emit(0x5224A,0x52254);r[2]=0x21E14;r[1]=frame_access(0x5224C,'read',stack,4,1)
        frame_access(0x5224E,'write',stack+4,4,0,r[0]);r[0]=120
        row=call(0x52250,0x21E14);remainder(row)
        emit(0x52254,0x5225C);r[2]=4;within=signed(r[0])>=4;t(within);r[5]=r[0]
        branch(0x52258,within,0x5225E,True)
        if not within:emit(0x5225C);r[5]=4
        emit(0x5225E,0x52264);r[2]=116;above=signed(r[5])>116;t(above);branch(0x52262,not above,0x52266)
        if above:emit(0x52264);r[5]=116
        emit(0x52266,0x5226C);t(True);r[2]=r[5];branch(0x52268,True,0x5226E,True)
        emit(0x5226E,0x5227E);t(bool(r[2]&1));r[2]>>=1;r[5]=RAM_BASE+0x424C
        t(bool(r[2]&1));r[2]>>=1;r[0]=r[2];put(0x52276,0x23BF,1,0,r[0]);r[0]=load(0x52278,0x4251,1,0)
        override=bool(r[0]&1);t(not override);branch(0x5227C,not override,0x52282)
        if override:emit(0x5227E,0x52282);r[6]=3;frame_access(0x52280,'write',stack+4,4,6,r[6])
        emit(0x52282,0x52292);r[0]=frame_access(0x52282,'read',stack+4,4,0);put(0x52284,0x23F0,1,0,r[0])
        output=(r[2]&255,r[0]&255);stack+=8;gbr=pop(0x52288);macl=pop(0x5228A);pr=pop(0x5228C);r[14]=pop(0x52290,14)
        control(0x5228E,'return',pr,True)
    else:
        emit(0x4D99C,0x4D9BC)
        for site,index in ((0x4D99C,12),(0x4D99E,13),(0x4D9A0,14)):push(site,r[index],index)
        push(0x4D9A2,pr);push(0x4D9A4,macl);push(0x4D9A6,gbr);r[0]=gbr=RAM_BASE+0x1FF4
        r[2]=0x8710;r[7]=RAM_BASE+0x24C0;r[0]=signed(read(0x4D9B0,0x8710,0,1),8)&MASK;r[0]&=32;r[6]=r[0]
        r[0]=load(0x4D9B6,0x24C5,1,0);other=bool(r[0]&32);t(not other);branch(0x4D9BA,other,0x4D9D8)
        if not other:
            emit(0x4D9BC,0x4D9C2);r[0]=load(0x4D9BC,0x24CB,1,0);other=bool(r[0]&4);t(not other)
            branch(0x4D9C0,other,0x4D9D8)
        if not other:
            emit(0x4D9C2,0x4D9D0);r[14]=RAM_BASE+0x11D4;r[0]=0x25;t(r[6]==0)
            r[5]=load(0x4D9C8,0x11F9,1,5);r[0]=(-r[5])&MASK;put(0x4D9CE,0x11D6,2,0,r[0])
            branch(0x4D9CC,r[6]==0,0x4DA2A,True)
            if r[6]!=0:
                emit(0x4D9D0,0x4D9D8);r[0]=0x26;r[6]=load(0x4D9D2,0x11FA,1,6);r[0]=(-r[6])&MASK
                control(0x4D9D4,'jump',0x4DA28,True);emit(0x4DA28);put(0x4DA28,0x11D8,2,0,r[0])
        else:
            emit(0x4D9D8,0x4D9DC);mode=r[6]!=0;t(not mode);branch(0x4D9DA,mode,0x4D9F6)
            if not mode:
                emit(0x4D9DC,0x4D9EE);r[14]=RAM_BASE+0x11D4;r[0]=0x25;r[4]=RAM_BASE+0x22F8
                r[2]=load(0x4D9E2,0x11F9,1,2);r[0]=load(0x4D9E4,0x22FA,1,0);r[6]=(-r[2])&MASK
                above=signed(r[0])>signed(r[6]);t(above);r[2]=r[0];branch(0x4D9EA,above,0x4D9F0,True)
                if not above:emit(0x4D9EE);r[6]=r[2]
                emit(0x4D9F0,0x4D9F6);r[0]=r[6];put(0x4D9F4,0x11D6,2,0,r[0]);control(0x4D9F2,'jump',0x4DA2A,True)
            else:
                emit(0x4D9F6,0x4DA16);r[6]=RAM_BASE+0x23BC;r[4]=RAM_BASE+0x22F8
                r[0]=load(0x4D9FA,0x23C2,2,0);r[14]=RAM_BASE+0x11D4;r[6]=(r[0]&65535)>>8
                r[0]=load(0x4DA00,0x22FA,1,0);r[5]=r[2]=r[0];r[0]=0x26;r[4]=load(0x4DA0A,0x11FA,1,4)
                r[2]=signed((r[2]-r[6])&65535,16)&MASK;r[6]=(-r[4])&MASK;above=signed(r[2])>signed(r[6])
                t(above);branch(0x4DA14,not above,0x4DA18)
                if above:emit(0x4DA16);r[2]=r[6]
                emit(0x4DA18,0x4DA20);above=signed(r[5])>signed(r[6]);t(above);r[0]=r[2]
                put(0x4DA1E,0x11D6,2,0,r[0]);branch(0x4DA1C,not above,0x4DA24,True)
                if above:emit(0x4DA20,0x4DA24);r[2]=r[6];control(0x4DA20,'jump',0x4DA26,True)
                else:emit(0x4DA24);r[2]=signed(r[5]&255,8)&MASK
                emit(0x4DA26,0x4DA2A);r[0]=r[2];put(0x4DA28,0x11D8,2,0,r[0])
        emit(0x4DA2A,0x4DA32);r[12]=0x8290;r[5]=signed(read(0x4DA2C,0x8290,5,1),8)&MASK
        zero=r[5]==0;t(zero);branch(0x4DA30,zero,0x4DA70);clear_flag=zero
        if not zero:
            emit(0x4DA32,0x4DA40);r[0]=load(0x4DA32,0x24C2,1,0);r[2]=r[0];r[0]&=2;r[6]=r[0];r[0]=r[2]
            first=bool(r[0]&1);t(not first);branch(0x4DA3E,not first,0x4DA5E)
            if first:
                emit(0x4DA40,0x4DA44);t(r[6]==0);branch(0x4DA42,r[6]!=0,0x4DA5E)
            if first and r[6]==0:
                emit(0x4DA44,0x4DA5E);r[13]=RAM_BASE+0x2330;r[0]=0x48;r[4]=RAM_BASE+0x1FF4
                r[2]=load(0x4DA4A,0x2378,1,2);r[0]=0x2A9;r[6]=RAM_BASE+0x25FB
                put(0x4DA50,0x229D,1,2,r[2]);r[0]=load(0x4DA52,0x24C0,1,0);r[0]|=64
                put(0x4DA56,0x24C0,1,0,r[0]);r[0]=r[5];put(0x4DA5C,0x25FC,1,0,r[0])
                control(0x4DA5A,'jump',0x4DA76,True)
            else:
                emit(0x4DA5E,0x4DA62);clear_flag=r[6]!=0;t(not clear_flag);branch(0x4DA60,clear_flag,0x4DA70)
                if not clear_flag:
                    emit(0x4DA62,0x4DA70);r[0]=load(0x4DA62,0x1FF8,4,0);r[4]=RAM_BASE+0x1FF4;r[3]=r[0];r[0]=0x2A9
                    r[2]=load(0x4DA6A,0x229D,1,2);equal=r[3]==r[2];t(equal);clear_flag=equal;branch(0x4DA6E,not equal,0x4DA76)
        if clear_flag:
            emit(0x4DA70,0x4DA76);r[0]=load(0x4DA70,0x24C0,1,0);r[0]&=0xBF;put(0x4DA74,0x24C0,1,0,r[0])
        emit(0x4DA76,0x4DA7C);r[0]=load(0x4DA76,0x24CC,1,0);bypass=bool(r[0]&2);t(not bypass);branch(0x4DA7A,bypass,0x4DB74)
        if not bypass:
            emit(0x4DA7C,0x4DA8C);r[13]=RAM_BASE+0x2330;r[0]=0x4E;r[4]=0x147DA;r[7]=load(0x4DA82,0x237E,2,7)
            r[5]=0x13C48;r[2]=0x264CC;r[6]=r[7]&65535;row=call(0x4DA88,0x264CC);curve(0x264CC,8,row)
            emit(0x4DA8C,0x4DA98);r[5]=RAM_BASE+0x2459;r[6]=r[0];put(0x4DA90,0x2000,2,0,r[0])
            r[0]=load(0x4DA92,0x2459,1,0);first=bool(r[0]&32);t(not first);branch(0x4DA96,not first,0x4DAA8)
            if first:
                emit(0x4DA98,0x4DAA4);r[5]=0x8A3C;r[4]=RAM_BASE+0x1FF4;r[2]=signed(read(0x4DA9C,0x8A3C,2,1),8)&MASK;r[0]=0x278
                put(0x4DAA2,0x226C,1,2,r[2]);control(0x4DAA0,'jump',0x4DAB4,True)
            else:
                emit(0x4DAA8,0x4DAB4);r[2]=0x8A3D;r[4]=RAM_BASE+0x1FF4;r[5]=signed(read(0x4DAAC,0x8A3D,5,1),8)&MASK
                r[0]=0x278;r[2]=r[5];put(0x4DAB2,0x226C,1,5,r[5])
            emit(0x4DAB4,0x4DAC2);r[6]&=65535;r[2]&=255;macl=r[6]*r[2];r[6]=0x21CE0;r[0]=100;r[1]=macl
            row=call(0x4DABE,0x21CE0);unsigned_divider(row)
            emit(0x4DAC2,0x4DACC);r[6]=65535;above=r[0]>65535;t(above);r[2]=r[0];branch(0x4DAC8,not above,0x4DACE,True)
            if above:emit(0x4DACC);r[2]=r[6]
            emit(0x4DACE,0x4DADC);r[7]=RAM_BASE+0x24C0;r[6]=r[2]&65535;r[0]=r[6];put(0x4DAD4,0x1FF6,2,0,r[0])
            r[0]=load(0x4DAD6,0x24C0,1,0);history_mode=bool(r[0]&64);t(not history_mode);branch(0x4DADA,not history_mode,0x4DB14)
            limited=False
            if history_mode:
                emit(0x4DADC,0x4DAE4);r[5]=RAM_BASE+0x25FB;r[0]=load(0x4DADE,0x25FC,1,0)
                counter=r[0]!=0;t(not counter);branch(0x4DAE2,counter,0x4DB0E)
                if not counter:
                    emit(0x4DAE4,0x4DAF2);r[4]=RAM_BASE+0x1FF4;r[0]=0x2A9;r[2]=load(0x4DAE8,0x229D,1,2)
                    r[0]=load(0x4DAEA,0x1FF8,4,0);above=signed(r[0])>signed(r[2]);t(above);r[5]=r[0]
                    branch(0x4DAEE,not above,0x4DAFE,True);store_history=above
                    if above:
                        emit(0x4DAF2,0x4DAFE);r[0]=signed(read(0x4DAF2,0x8290,0,1),8)&MASK;r[3]=RAM_BASE+0x25FB
                        put(0x4DAF6,0x25FC,1,0,r[0]);r[0]=(signed(r[5]&65535,16)-1)&MASK;control(0x4DAFA,'jump',0x4DB0C,True)
                    else:
                        emit(0x4DAFE,0x4DB02);within=signed(r[5])>=signed(r[2]);t(within);branch(0x4DB00,within,0x4DB0E)
                        if not within:
                            emit(0x4DB02,0x4DB0C);r[0]=signed(read(0x4DB02,0x8290,0,1),8)&MASK;r[3]=RAM_BASE+0x25FB
                            put(0x4DB06,0x25FC,1,0,r[0]);r[0]=(signed(r[5]&65535,16)+1)&MASK;store_history=True
                    if store_history:emit(0x4DB0C);put(0x4DB0C,0x1FF8,4,0,r[0])
                emit(0x4DB0E,0x4DB14);r[0]=load(0x4DB0E,0x1FF8,4,0);r[2]=r[0];control(0x4DB10,'jump',0x4DB56,True)
            else:
                emit(0x4DB14,0x4DB20);r[2]=RAM_BASE+0x40CC;r[0]=0x1B;r[4]=load(0x4DB18,0x40E7,1,4)&255
                active=r[4]>0;t(active);branch(0x4DB1E,not active,0x4DB48)
                if active:
                    emit(0x4DB20,0x4DB26);r[0]=load(0x4DB20,0x24C2,1,0);active=(r[0]&2)==0;t(active);branch(0x4DB24,not active,0x4DB48)
                limited=active
                if limited:
                    emit(0x4DB26,0x4DB38);r[0]=load(0x4DB26,0x11D6,2,0);r[5]=signed(r[4]&65535,16)&MASK;r[7]=r[0]
                    r[0]=0x26;r[2]=load(0x4DB2E,0x2356,1,2);r[7]=(r[7]+r[2])&MASK;r[2]=(-r[5])&MASK
                    above=signed(r[7])>signed(r[2]);t(above);branch(0x4DB36,not above,0x4DB3C)
                    if above:emit(0x4DB38,0x4DB3C);r[4]=signed(r[4]&65535,16)&MASK;r[7]=(-r[4])&MASK
                    emit(0x4DB3C,0x4DB48);r[0]=0x48;r[2]=r[6];r[6]=load(0x4DB40,0x2378,1,6)
                    r[6]=(r[6]+r[7]-r[2])&MASK;control(0x4DB44,'jump',0x4DB60,True)
                else:
                    emit(0x4DB48,0x4DB56);r[0]=load(0x4DB48,0x11D6,2,0);r[4]=r[0];r[0]=0x48;r[2]=load(0x4DB4E,0x2378,1,2)
                    r[2]=(r[2]+r[4])&MASK;r[0]=r[2];put(0x4DB54,0x1FF8,4,0,r[0])
            if not limited:
                emit(0x4DB56,0x4DB60);r[0]=0x26;r[5]=load(0x4DB58,0x2356,1,5);r[2]=(r[2]+r[5]-r[6])&MASK;r[6]=r[2]
            emit(0x4DB60,0x4DB68);r[2]=0xFFFFFF80;within=signed(r[6])>=-128;t(within);r[2]=r[6]
            branch(0x4DB64,within,0x4DB6A,True)
            if not within:emit(0x4DB68);r[2]=0xFFFFFF80
            emit(0x4DB6A,0x4DB70);r[6]=127;above=signed(r[2])>127;t(above);branch(0x4DB6E,not above,0x4DB86)
            if above:emit(0x4DB70,0x4DB74);r[2]=127;control(0x4DB70,'jump',0x4DB86,True)
        else:
            emit(0x4DB74,0x4DB82);r[13]=RAM_BASE+0x2330;r[0]=0x48;r[6]=127;r[2]=load(0x4DB7A,0x2378,1,2)
            # MOV.B sign extension bounds R2 to -128..127 here.
            t(False);r[6]=r[2];branch(0x4DB7E,True,0x4DB84,True)
            emit(0x4DB84);r[2]=r[6]
        emit(0x4DB86,0x4DB9C);r[6]=r[2];r[2]=RAM_BASE+0x128C;r[0]=0x4A;put(0x4DB8C,0x12D6,1,6,r[6]);output=r[6]&255
        gbr=pop(0x4DB8E);macl=pop(0x4DB90);pr=pop(0x4DB92);r[14]=pop(0x4DB94,14);r[13]=pop(0x4DB96,13);r[12]=pop(0x4DB9A,12)
        control(0x4DB98,'return',pr,True)
    return dict(ram=bytes(ram),frame=bytes(frame),known_registers={index:value&MASK for index,value in enumerate(r) if value is not None},
        path=tuple(path),events=events,controls=controls,calls=calls,lookups=lookups,
        sr=sr,sr_mask=sr_mask,sp=stack,pr=pr,gbr=gbr,mach=context[16],macl=macl,output=output)
